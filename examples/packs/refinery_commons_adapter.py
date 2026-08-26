from __future__ import annotations

from typing import Any, Iterable, Mapping

from citation_engine import (
    Artifact,
    Assertion,
    AuthorityState,
    Citation,
    CitationEngine,
    CitationRelation,
    ContextPack,
    EpistemicStatus,
    GateResult,
    Provenance,
    Receipt,
    canonical_hash,
)


def _nonempty(value: Any, label: str) -> str:
    text = str(value or "").strip()
    if not text:
        raise ValueError(f"{label} is required")
    return text


def capability_ref(intrinsic: Mapping[str, Any], *, namespace: str = "refinery") -> str:
    """Stable semantic identity for one reviewed capability contract.

    Display metadata and concrete implementations are intentionally excluded.
    """
    return f"{namespace}:capability:{canonical_hash(dict(intrinsic))}"


def implementation_ref(
    *,
    capability_ref: str,
    implementation_identity: Mapping[str, Any],
    namespace: str = "refinery",
) -> str:
    """Stable identity for one concrete realization of a capability."""
    material = {
        "capability_ref": _nonempty(capability_ref, "capability_ref"),
        "implementation_identity": dict(implementation_identity),
    }
    return f"{namespace}:implementation:{canonical_hash(material)}"


def record_evidence_artifact(
    engine: CitationEngine,
    *,
    artifact_id: str,
    kind: str,
    payload: Mapping[str, Any],
    source: str,
    method: str,
    locator: str | None = None,
    parent_refs: Iterable[str] = (),
) -> Artifact:
    return engine.record_artifact(Artifact(
        id=_nonempty(artifact_id, "artifact_id"),
        kind=_nonempty(kind, "kind"),
        payload=dict(payload),
        provenance=Provenance(
            source=_nonempty(source, "source"),
            method=_nonempty(method, "method"),
            locator=locator,
            parent_refs=tuple(parent_refs),
        ),
    ))


def record_capability(
    engine: CitationEngine,
    *,
    intrinsic: Mapping[str, Any],
    basis_refs: Iterable[str],
    metadata: Mapping[str, Any] | None = None,
    namespace: str = "refinery",
) -> Artifact:
    """Represent a Commons Capability Capsule as a domain Artifact.

    The engine remains unaware of the `Capability` noun. The adapter binds the
    reviewed semantic contract to the exact evidence objects used to author it.
    """
    basis = tuple(basis_refs)
    if not basis:
        raise ValueError("reviewed capability requires at least one basis_ref")
    intrinsic_dict = dict(intrinsic)
    ref = capability_ref(intrinsic_dict, namespace=namespace)
    return engine.record_artifact(Artifact(
        id=ref,
        kind="refinery.capability",
        payload={
            "intrinsic": intrinsic_dict,
            "metadata": dict(metadata or {}),
        },
        provenance=Provenance(
            source="refinery-commons",
            method="reviewed-semantic-contract",
            parent_refs=basis,
        ),
    ))


def record_implementation(
    engine: CitationEngine,
    *,
    capability_ref: str,
    implementation_identity: Mapping[str, Any],
    source_ref: str,
    payload: Mapping[str, Any] | None = None,
    namespace: str = "refinery",
) -> Artifact:
    """Represent one exact capability realization without globalizing its evidence."""
    identity = dict(implementation_identity)
    ref = implementation_ref(
        capability_ref=capability_ref,
        implementation_identity=identity,
        namespace=namespace,
    )
    return engine.record_artifact(Artifact(
        id=ref,
        kind="refinery.implementation",
        payload={
            "capability_ref": capability_ref,
            "implementation_identity": identity,
            **dict(payload or {}),
        },
        provenance=Provenance(
            source="refinery-commons",
            method="exact-realization-binding",
            # Adapter-local structural closure: a realization is not accepted unless
            # both its semantic contract and exact source/artifact identity exist.
            parent_refs=(capability_ref, source_ref),
        ),
    ))


def record_claim(
    engine: CitationEngine,
    *,
    assertion_id: str,
    subject_ref: str,
    predicate: str,
    value: Any,
    status: EpistemicStatus,
    basis_refs: Iterable[str],
    relation: CitationRelation = CitationRelation.SUPPORTS,
    confidence: float | None = None,
    produced_by: str = "refinery-commons-adapter",
) -> Assertion:
    """Split a Refinery Claim into an Assertion plus explicit basis edges."""
    basis = tuple(dict.fromkeys(str(ref) for ref in basis_refs))
    assertion = engine.record_assertion(Assertion(
        id=_nonempty(assertion_id, "assertion_id"),
        subject_ref=_nonempty(subject_ref, "subject_ref"),
        predicate=_nonempty(predicate, "predicate"),
        value=value,
        status=status,
        basis_refs=basis,
        confidence=confidence,
        produced_by=produced_by,
    ))
    for index, basis_ref in enumerate(basis):
        engine.record_citation(Citation(
            id=f"{assertion.id}:citation:{index}",
            subject_ref=assertion.id,
            basis_ref=basis_ref,
            relation=relation,
            produced_by=produced_by,
        ))
    return assertion


def _sha256_from_implementation(implementation: Artifact) -> str | None:
    identity = implementation.payload.get("implementation_identity")
    if not isinstance(identity, Mapping):
        return None
    source = identity.get("source") if isinstance(identity.get("source"), Mapping) else {}
    digest = str(identity.get("digest") or source.get("digest") or "").strip()
    if digest.startswith("sha256:") and len(digest) == 71:
        return digest.removeprefix("sha256:")
    return None


def _slsa_subject_sha256s(evidence: Artifact) -> set[str]:
    packet = evidence.payload
    statement = packet.get("statement") if isinstance(packet, Mapping) else None
    if not isinstance(statement, Mapping):
        statement = packet
    subjects = statement.get("subject") if isinstance(statement, Mapping) else None
    if not isinstance(subjects, list):
        return set()
    values: set[str] = set()
    for row in subjects:
        if not isinstance(row, Mapping):
            continue
        digest = row.get("digest")
        if isinstance(digest, Mapping):
            sha = str(digest.get("sha256") or "").strip()
            if len(sha) == 64:
                values.add(sha)
    return values


def record_exact_provenance_claim(
    engine: CitationEngine,
    *,
    assertion_id: str,
    subject_ref: str,
    evidence_ref: str,
    verification_status: str,
    expected_sha256: str | None = None,
) -> Assertion:
    """Bind provenance evidence to one exact realization and fail closed on mismatch.

    This is the MEV0-001 anti-laundering rule learned by Refinery: provenance for
    one immutable release/artifact cannot silently verify a sibling implementation.
    """
    engine.store.require(subject_ref, evidence_ref)
    subject = engine.store.get(subject_ref)
    evidence = engine.store.get(evidence_ref)
    if not isinstance(subject, Artifact) or subject.kind != "refinery.implementation":
        raise TypeError("provenance subject must be a refinery implementation Artifact")
    if not isinstance(evidence, Artifact):
        raise TypeError("provenance evidence_ref must resolve to an Artifact")

    actual = _sha256_from_implementation(subject)
    expected = str(expected_sha256 or actual or "").removeprefix("sha256:")
    if not expected or len(expected) != 64:
        raise ValueError("exact provenance binding requires a full SHA-256 implementation digest")
    if actual != expected:
        raise ValueError("expected SHA-256 does not match the exact implementation subject")
    if expected not in _slsa_subject_sha256s(evidence):
        raise ValueError("provenance evidence subject digest does not match implementation")

    status_text = _nonempty(verification_status, "verification_status")
    if status_text not in {"verified", "unverified", "failed"}:
        raise ValueError("unsupported verification_status")

    if status_text == "verified":
        value = True
        epistemic = EpistemicStatus.VERIFIED
    elif status_text == "failed":
        value = False
        epistemic = EpistemicStatus.VERIFIED
    else:
        value = None
        epistemic = EpistemicStatus.OBSERVED

    return record_claim(
        engine,
        assertion_id=assertion_id,
        subject_ref=subject_ref,
        predicate="provenance.verified",
        value=value,
        status=epistemic,
        basis_refs=(evidence_ref,),
        relation=CitationRelation.SUPPORTS,
        produced_by="refinery-slsa-adapter",
    )


def assertions_for_subject(engine: CitationEngine, subject_ref: str) -> tuple[Assertion, ...]:
    rows: list[Assertion] = []
    for object_id in engine.store.ids():
        value = engine.store.get(object_id)
        if isinstance(value, Assertion) and value.subject_ref == subject_ref:
            rows.append(value)
    return tuple(rows)


def ingest_compiled_registry(
    engine: CitationEngine,
    compiled: Mapping[str, Any],
) -> dict[str, Any]:
    """Ingest Refinery's current compiled `rcap/rimpl/rclaim/rregistry` output.

    Imported claim records are intentionally conservative: they become OBSERVED
    assertions over canonical evidence-pointer Artifacts. A normalized Refinery
    provenance claim saying `verified` is not independently re-verified here; raw
    SLSA/attestation material must still pass `record_exact_provenance_claim()` to
    become a CE `VERIFIED` provenance assertion.
    """
    if not isinstance(compiled, Mapping):
        raise TypeError("compiled registry must be a mapping")
    registry_id = _nonempty(compiled.get("registry_id"), "registry_id")
    capsules = compiled.get("capsules")
    implementations = compiled.get("implementations")
    claims = compiled.get("claims")
    if not isinstance(capsules, list) or not isinstance(implementations, list) or not isinstance(claims, list):
        raise ValueError("compiled registry requires capsules, implementations, and claims lists")

    registry = engine.record_artifact(Artifact(
        id=registry_id,
        kind="refinery.registry_snapshot",
        payload={
            "schema_version": compiled.get("schema_version"),
            "registry_id": registry_id,
            "metadata": dict(compiled.get("metadata") or {}),
            "counts": {
                "capsules": len(capsules),
                "implementations": len(implementations),
                "claims": len(claims),
            },
        },
        provenance=Provenance(
            source="refinery-commons",
            method="compiled-registry-import",
        ),
    ))

    capability_refs: list[str] = []
    for row in capsules:
        if not isinstance(row, Mapping):
            raise ValueError("compiled capsule rows must be mappings")
        object_id = _nonempty(row.get("object_id"), "compiled capsule object_id")
        intrinsic = row.get("intrinsic")
        if not isinstance(intrinsic, Mapping):
            raise ValueError("compiled capsule intrinsic must be a mapping")
        engine.record_artifact(Artifact(
            id=object_id,
            kind="refinery.capability",
            payload={
                "intrinsic": dict(intrinsic),
                "metadata": dict(row.get("metadata") or {}),
                "refinery_key": row.get("key"),
            },
            provenance=Provenance(
                source="refinery-commons",
                method="compiled-capability-import",
                parent_refs=(registry.id,),
            ),
        ))
        capability_refs.append(object_id)

    implementation_refs: list[str] = []
    for row in implementations:
        if not isinstance(row, Mapping):
            raise ValueError("compiled implementation rows must be mappings")
        object_id = _nonempty(row.get("object_id"), "compiled implementation object_id")
        capsule_id = _nonempty(row.get("capsule_id"), "compiled implementation capsule_id")
        engine.store.require(capsule_id)
        intrinsic = row.get("intrinsic")
        if not isinstance(intrinsic, Mapping):
            raise ValueError("compiled implementation intrinsic must be a mapping")
        engine.record_artifact(Artifact(
            id=object_id,
            kind="refinery.implementation",
            payload={
                "capability_ref": capsule_id,
                "implementation_identity": dict(intrinsic),
                "metadata": dict(row.get("metadata") or {}),
                "refinery_key": row.get("key"),
            },
            provenance=Provenance(
                source="refinery-commons",
                method="compiled-implementation-import",
                parent_refs=(capsule_id, registry.id),
            ),
        ))
        implementation_refs.append(object_id)

    evidence_refs: list[str] = []
    assertion_refs: list[str] = []
    for row in claims:
        if not isinstance(row, Mapping):
            raise ValueError("compiled claim rows must be mappings")
        claim_id = _nonempty(row.get("object_id"), "compiled claim object_id")
        subject_id = _nonempty(row.get("subject_id"), "compiled claim subject_id")
        engine.store.require(subject_id)
        intrinsic = row.get("intrinsic")
        if not isinstance(intrinsic, Mapping):
            raise ValueError("compiled claim intrinsic must be a mapping")
        claim_type = _nonempty(intrinsic.get("claim_type"), "compiled claim_type")
        outcome = _nonempty(intrinsic.get("outcome"), "compiled claim outcome")
        evidence_locator = _nonempty(intrinsic.get("evidence_ref"), "compiled claim evidence_ref")
        issuer = str(intrinsic.get("issuer") or "refinery-claim-import").strip() or "refinery-claim-import"
        pointer_id = "refinery:evidence-pointer:" + canonical_hash({
            "evidence_ref": evidence_locator,
            "issuer": issuer,
        })
        pointer = engine.record_artifact(Artifact(
            id=pointer_id,
            kind="refinery.evidence_pointer",
            payload={
                "evidence_ref": evidence_locator,
                "issuer": issuer,
            },
            provenance=Provenance(
                source=issuer,
                method="imported-evidence-pointer",
                locator=evidence_locator,
                parent_refs=(registry.id,),
            ),
        ))
        evidence_refs.append(pointer.id)

        assertion = record_claim(
            engine,
            assertion_id=f"{claim_id}:assertion",
            subject_ref=subject_id,
            predicate=f"refinery.claim.{claim_type}",
            value={
                "outcome": outcome,
                "payload": dict(intrinsic.get("payload") or {}),
                "issuer": issuer,
                "observed_at": intrinsic.get("observed_at"),
                "refinery_claim_id": claim_id,
            },
            status=EpistemicStatus.OBSERVED,
            basis_refs=(pointer.id,),
            relation=CitationRelation.SUPPORTS,
            produced_by="refinery-compiled-registry-import",
        )
        assertion_refs.append(assertion.id)

    return {
        "registry_ref": registry.id,
        "capability_refs": tuple(capability_refs),
        "implementation_refs": tuple(implementation_refs),
        "assertion_refs": tuple(assertion_refs),
        "evidence_refs": tuple(dict.fromkeys(evidence_refs)),
        "boundary": (
            "Imported Refinery claims remain observed records. Curation does not authorize recommendation, "
            "and normalized provenance does not become independently verified without exact raw evidence."
        ),
    }


def make_curation_pack(*, curation_basis_ref: str) -> ContextPack:
    """Keep evidence maturity separate from explicit recommendation authority."""
    basis_ref = _nonempty(curation_basis_ref, "curation_basis_ref")
    pack = ContextPack(name="refinery-commons-curation", version="1")

    def explicit_curation_gate(subject_ref: str, context: Mapping[str, Any]) -> GateResult:
        curator = str(context.get("curator") or "").strip()
        explicit = bool(context.get("explicit_curation"))
        passed = bool(curator) and explicit
        return GateResult(
            gate_id="explicit_named_curator",
            passed=passed,
            basis_refs=(basis_ref,),
            reason=(
                f"explicit curation by {curator}"
                if passed
                else "recommendation requires an explicit curation act from a named curator"
            ),
        )

    pack.register_gate("explicit_named_curator", explicit_curation_gate)
    return pack


def issue_review_receipt(
    engine: CitationEngine,
    *,
    subject_ref: str,
    decision_ref: str,
    evidence_refs: Iterable[str],
    assertion_refs: Iterable[str],
    reviewed_at: str,
) -> Receipt:
    inputs = tuple(dict.fromkeys(str(ref) for ref in evidence_refs))
    assertions = tuple(dict.fromkeys(str(ref) for ref in assertion_refs))
    receipt_id = "refinery:receipt:" + canonical_hash({
        "subject_ref": subject_ref,
        "decision_ref": decision_ref,
        "inputs": inputs,
        "assertions": assertions,
        "reviewed_at": reviewed_at,
    })[:24]
    return engine.issue_receipt(Receipt(
        id=receipt_id,
        workflow="refinery.commons-review",
        input_refs=inputs,
        assertion_refs=assertions,
        decision_refs=(decision_ref,),
        output_refs=(subject_ref,),
        metadata={"reviewed_at": reviewed_at},
    ))


__all__ = [
    "assertions_for_subject",
    "capability_ref",
    "implementation_ref",
    "ingest_compiled_registry",
    "issue_review_receipt",
    "make_curation_pack",
    "record_capability",
    "record_claim",
    "record_evidence_artifact",
    "record_exact_provenance_claim",
    "record_implementation",
]
