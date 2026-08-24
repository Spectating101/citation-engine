from __future__ import annotations

from typing import Any, Mapping

from citation_engine import (
    Artifact,
    CitationEngine,
    ContextPack,
    GateResult,
    Provenance,
    Receipt,
    canonical_hash,
)


def ingest_sharpe_candidate(
    engine: CitationEngine,
    *,
    manifest: Mapping[str, Any],
    manifest_gate_result: Mapping[str, Any],
    frozen_decision: Mapping[str, Any] | None = None,
    namespace: str = "sharpe",
) -> dict[str, Any]:
    """Map a Sharpe candidate and its promotion evidence without promoting on metrics alone."""
    run_id = str(manifest.get("run_id") or "").strip()
    if not run_id:
        raise ValueError("Sharpe candidate requires run_id")

    candidate_ref = f"{namespace}:candidate:{run_id}"
    candidate = engine.record_artifact(Artifact(
        id=candidate_ref,
        kind="sharpe.candidate",
        payload=dict(manifest),
        provenance=Provenance(
            source="sharpe-candidate-registry",
            method="candidate-manifest",
            locator=str(manifest.get("run_dir") or "") or None,
        ),
    ))

    gate_ref = f"{namespace}:manifest-gate:{run_id}"
    gate_artifact = engine.record_artifact(Artifact(
        id=gate_ref,
        kind="sharpe.manifest_gate_report",
        payload=dict(manifest_gate_result),
        provenance=Provenance(
            source="sharpe-alpha",
            method="manifest-gate-report",
            parent_refs=(candidate.id,),
        ),
    ))

    frozen_ref: str | None = None
    if frozen_decision is not None:
        decision_id = str(frozen_decision.get("decision_id") or f"{run_id}-frozen").strip()
        frozen_ref = f"{namespace}:frozen-decision:{decision_id}"
        engine.record_artifact(Artifact(
            id=frozen_ref,
            kind="sharpe.frozen_decision",
            payload=dict(frozen_decision),
            provenance=Provenance(
                source="sharpe-alpha",
                method="frozen-decision-log",
                parent_refs=(candidate.id,),
            ),
        ))

    return {
        "candidate_ref": candidate.id,
        "manifest_gate_ref": gate_artifact.id,
        "frozen_decision_ref": frozen_ref,
    }


def make_promotion_pack(
    *,
    candidate_ref: str,
    manifest_gate_ref: str,
    frozen_decision_ref: str | None,
    require_frozen_decision: bool,
) -> ContextPack:
    """Translate Sharpe's promotion checks into neutral gate results.

    Backtest metrics may be supplied in context for display, but they are never a
    substitute for provenance/promotion evidence.
    """
    pack = ContextPack(name="sharpe-promotion-fixture", version="1")

    def manifest_gate(subject_ref: str, context: Mapping[str, Any]) -> GateResult:
        passed = bool(context.get("manifest_passed"))
        reasons = list(context.get("manifest_reasons") or [])
        return GateResult(
            gate_id="manifest_integrity",
            passed=passed,
            basis_refs=(manifest_gate_ref,),
            reason="candidate manifest promotion evidence passed" if passed else "; ".join(map(str, reasons)) or "manifest gate failed",
        )

    pack.register_gate("manifest_integrity", manifest_gate)

    if require_frozen_decision:
        def frozen_gate(subject_ref: str, context: Mapping[str, Any]) -> GateResult:
            evaluated = bool(frozen_decision_ref) and bool(context.get("frozen_decision_evaluated"))
            return GateResult(
                gate_id="evaluated_frozen_decision",
                passed=evaluated,
                basis_refs=((frozen_decision_ref,) if frozen_decision_ref else (candidate_ref,)),
                reason="evaluated frozen decision exists" if evaluated else "evaluated frozen decision missing",
            )

        pack.register_gate("evaluated_frozen_decision", frozen_gate)

    return pack


def issue_promotion_receipt(
    engine: CitationEngine,
    *,
    mapped: Mapping[str, Any],
    decision_ref: str,
    evaluated_at: str,
) -> Receipt:
    inputs = [str(mapped["candidate_ref"]), str(mapped["manifest_gate_ref"])]
    if mapped.get("frozen_decision_ref"):
        inputs.append(str(mapped["frozen_decision_ref"]))
    receipt_id = "sharpe:receipt:" + canonical_hash({
        "decision_ref": decision_ref,
        "evaluated_at": evaluated_at,
        "inputs": inputs,
    })[:24]
    return engine.issue_receipt(Receipt(
        id=receipt_id,
        workflow="sharpe.promotion-review",
        input_refs=tuple(inputs),
        assertion_refs=(),
        decision_refs=(decision_ref,),
        output_refs=(str(mapped["candidate_ref"]),),
        metadata={"evaluated_at": evaluated_at},
    ))
