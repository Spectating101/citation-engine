from __future__ import annotations

from typing import Any, Mapping

from citation_engine import (
    Artifact,
    CitationEngine,
    Decision,
    GateResult,
    Provenance,
    Receipt,
    canonical_hash,
)


def _record_ref_artifact(
    engine: CitationEngine,
    *,
    ref: str,
    kind: str,
    payload: Mapping[str, Any],
    method: str,
) -> Artifact:
    return engine.record_artifact(Artifact(
        id=ref,
        kind=kind,
        payload=dict(payload),
        provenance=Provenance(source="policy-lab", method=method),
    ))


def _gate_from_evaluation(
    evaluation: Mapping[str, Any],
    *,
    hash_refs: Mapping[str, str],
    fallback_refs: tuple[str, ...],
) -> GateResult | None:
    status = str(evaluation.get("status") or "").strip().upper()
    if status == "NOT_APPLICABLE":
        return None
    if status not in {"PASS", "BLOCK"}:
        raise ValueError(f"unsupported Policy Lab evaluation status: {status}")

    input_refs = tuple(
        hash_refs[value]
        for value in (str(item).strip() for item in evaluation.get("input_refs") or [])
        if value in hash_refs
    ) or fallback_refs
    gate_id = str(
        evaluation.get("calculator_id")
        or evaluation.get("policy_rule_id")
        or "constraint"
    ).strip()
    reason = str(
        evaluation.get("explanation")
        or evaluation.get("boundary")
        or status
    ).strip()
    return GateResult(
        gate_id=gate_id,
        passed=status == "PASS",
        basis_refs=input_refs,
        reason=reason,
    )


def ingest_policy_lab_decision(
    engine: CitationEngine,
    decision_payload: Mapping[str, Any],
) -> dict[str, Any]:
    """Import a Policy Lab DecisionResult while leaving its calculators domain-owned."""
    external_decision_id = str(decision_payload.get("decision_id") or "").strip()
    case_id = str(decision_payload.get("case_id") or "").strip()
    policy_id = str(decision_payload.get("policy_id") or "").strip()
    policy_version = str(decision_payload.get("policy_version") or "").strip()
    policy_hash = str(decision_payload.get("policy_manifest_hash") or "").strip()
    if not all((external_decision_id, case_id, policy_id, policy_version, policy_hash)):
        raise ValueError("Policy Lab decision requires decision, case, and policy identity")

    case_hash = str(decision_payload.get("case_hash") or "").strip()
    case_ref = f"policy:case:{case_id}:{case_hash or 'unhashed'}"
    policy_ref = f"policy:manifest:{policy_hash}"
    _record_ref_artifact(
        engine,
        ref=case_ref,
        kind="policy.case_ref",
        payload={"case_id": case_id, "case_hash": case_hash or None},
        method="case-manifest-ref",
    )
    _record_ref_artifact(
        engine,
        ref=policy_ref,
        kind="policy.policy_manifest_ref",
        payload={
            "policy_id": policy_id,
            "policy_version": policy_version,
            "policy_manifest_hash": policy_hash,
        },
        method="policy-manifest-hash",
    )

    hash_refs: dict[str, str] = {policy_hash: policy_ref}
    evidence_refs: list[str] = []
    for evidence_hash in decision_payload.get("evidence_hashes") or []:
        evidence_hash = str(evidence_hash).strip()
        ref = f"policy:evidence:{evidence_hash}"
        _record_ref_artifact(
            engine,
            ref=ref,
            kind="policy.evidence_ref",
            payload={"evidence_hash": evidence_hash},
            method="evidence-hash-ref",
        )
        hash_refs[evidence_hash] = ref
        evidence_refs.append(ref)

    context_refs: list[str] = []
    for item in decision_payload.get("context_refs") or []:
        context_id = str(item.get("context_id") or "").strip()
        context_hash = str(item.get("context_hash") or "").strip()
        ref = f"policy:context:{context_hash}"
        _record_ref_artifact(
            engine,
            ref=ref,
            kind="policy.context_ref",
            payload={"context_id": context_id, "context_hash": context_hash},
            method="context-manifest-hash",
        )
        hash_refs[context_hash] = ref
        context_refs.append(ref)

    basis_refs = tuple(dict.fromkeys((case_ref, policy_ref, *evidence_refs, *context_refs)))
    fallback_refs = tuple(evidence_refs) or (case_ref, policy_ref)

    evaluations = list((decision_payload.get("admission") or {}).get("evaluations") or [])
    evaluations.extend((decision_payload.get("capacity") or {}).get("evaluations") or [])
    gates = tuple(
        gate
        for evaluation in evaluations
        if (gate := _gate_from_evaluation(
            evaluation,
            hash_refs=hash_refs,
            fallback_refs=fallback_refs,
        )) is not None
    )
    if not gates:
        raise ValueError("Policy Lab decision requires at least one applicable constraint evaluation")

    outcome = str(decision_payload.get("decision") or "").strip().upper()
    if outcome == "ADMIT_WITH_LIMIT" and not all(gate.passed for gate in gates):
        raise ValueError("ADMIT_WITH_LIMIT conflicts with a blocking imported evaluation")
    if outcome == "BLOCKED" and all(gate.passed for gate in gates):
        raise ValueError("BLOCKED decision requires at least one blocking imported evaluation")
    if outcome not in {"ADMIT_WITH_LIMIT", "BLOCKED"}:
        raise ValueError(f"unsupported Policy Lab decision outcome: {outcome}")

    result_ref = f"policy:decision-result:{external_decision_id}"
    engine.record_artifact(Artifact(
        id=result_ref,
        kind="policy.decision_result",
        payload=dict(decision_payload),
        provenance=Provenance(
            source="policy-lab",
            method="deterministic-decision-result",
            parent_refs=basis_refs,
        ),
    ))

    decision = engine.record_decision(Decision(
        id=f"policy:decision:{external_decision_id}",
        subject_ref=result_ref,
        outcome=outcome,
        rule_id=f"{policy_id}@{policy_version}",
        gate_results=gates,
        basis_refs=basis_refs,
    ))
    return {
        "decision_ref": decision.id,
        "decision_digest": decision.digest,
        "result_ref": result_ref,
        "basis_refs": basis_refs,
    }


def issue_policy_lab_receipt(
    engine: CitationEngine,
    *,
    mapped: Mapping[str, Any],
    external_receipt: Mapping[str, Any],
) -> Receipt:
    """Attach audit/runtime metadata without changing deterministic decision identity."""
    evaluated_at = str(external_receipt.get("evaluated_at") or "").strip()
    if not evaluated_at:
        raise ValueError("Policy Lab receipt requires evaluated_at")

    receipt_id = "policy:receipt:" + canonical_hash({
        "decision_ref": mapped["decision_ref"],
        "evaluated_at": evaluated_at,
        "runtime": external_receipt.get("runtime") or {},
    })[:24]
    return engine.issue_receipt(Receipt(
        id=receipt_id,
        workflow="policy-lab.decision-receipt",
        input_refs=tuple(mapped["basis_refs"]),
        assertion_refs=(),
        decision_refs=(str(mapped["decision_ref"]),),
        output_refs=(str(mapped["result_ref"]),),
        metadata={
            "evaluated_at": evaluated_at,
            "runtime": external_receipt.get("runtime") or {},
            "data_boundary": external_receipt.get("data_boundary"),
            "external_decision_id": external_receipt.get("decision_id"),
            "decision_digest": mapped["decision_digest"],
        },
    ))
