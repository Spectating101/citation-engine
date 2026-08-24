from __future__ import annotations

from typing import Any, Mapping

from citation_engine import (
    Artifact,
    Assertion,
    Citation,
    CitationEngine,
    CitationRelation,
    ContextPack,
    EpistemicStatus,
    GateResult,
    Provenance,
)

_QUERY_READY = {"instant", "instant_or_minutes"}


def ingest_drive_dataset(
    engine: CitationEngine,
    dataset: Mapping[str, Any],
    *,
    archive_result: Mapping[str, Any] | None = None,
    namespace: str = "research-drive",
) -> dict[str, Any]:
    """Map one Research Drive registry asset while keeping identity, custody verification,
    and query readiness as separate semantics.

    Research Drive's archive verification proves that a copy/transfer was checked. It does
    not prove the dataset is substantively true, nor does it make metadata-only assets
    query-ready. Model prose is deliberately ignored as authority evidence.
    """
    dataset_id = str(dataset.get("dataset_id") or "").strip()
    if not dataset_id:
        raise ValueError("Research Drive dataset requires dataset_id")

    dataset_ref = f"{namespace}:asset:{dataset_id}"
    asset = engine.record_artifact(Artifact(
        id=dataset_ref,
        kind="drive.asset",
        payload=dict(dataset),
        provenance=Provenance(
            source=str(dataset.get("source_of_truth") or dataset.get("source") or "research-drive-registry"),
            method="registry-identity",
            locator=str(dataset.get("canonical_remote") or dataset.get("local_path") or "") or None,
        ),
    ))

    verification_ref: str | None = None
    verification_assertion_ref: str | None = None
    citation_ref: str | None = None
    if archive_result is not None:
        verification_ref = f"{namespace}:verification:{dataset_id}"
        verification = engine.record_artifact(Artifact(
            id=verification_ref,
            kind="drive.archive_check",
            payload=dict(archive_result),
            provenance=Provenance(
                source=str(archive_result.get("remote_path") or archive_result.get("canonical_remote") or "research-drive"),
                method="archive-verification",
                parent_refs=(asset.id,),
            ),
        ))
        if bool(archive_result.get("ok")) and bool(archive_result.get("verified")):
            assertion = engine.record_assertion(Assertion(
                id=f"{namespace}:assertion:custody:{dataset_id}",
                subject_ref=asset.id,
                predicate="drive.custody_verified",
                value=True,
                status=EpistemicStatus.VERIFIED,
                basis_refs=(verification.id,),
                produced_by="research-drive.archive-check",
            ))
            verification_assertion_ref = assertion.id
            citation = engine.record_citation(Citation(
                id=f"{namespace}:citation:custody:{dataset_id}",
                subject_ref=assertion.id,
                basis_ref=verification.id,
                relation=CitationRelation.SUPPORTS,
                note="Archive/copy verification supports custody integrity only; not substantive truth.",
                produced_by="research-drive-adapter",
            ))
            citation_ref = citation.id

    return {
        "dataset_ref": asset.id,
        "verification_ref": verification_ref,
        "verification_assertion_ref": verification_assertion_ref,
        "citation_ref": citation_ref,
    }


def make_query_readiness_pack(*, dataset_ref: str) -> ContextPack:
    """Translate Drive operational readiness into neutral gates.

    The context may contain explanatory/model fields, but only registry readiness and
    actual path availability determine this gate.
    """
    pack = ContextPack(name="research-drive-readiness-fixture", version="1")

    def readiness_gate(subject_ref: str, context: Mapping[str, Any]) -> GateResult:
        readiness = str(context.get("analysis_readiness") or "").strip().lower()
        path_resolves = bool(context.get("path_resolves"))
        passed = readiness in _QUERY_READY and path_resolves
        reasons: list[str] = []
        if readiness not in _QUERY_READY:
            reasons.append(f"analysis_readiness={readiness or 'unset'} is not query-ready")
        if not path_resolves:
            reasons.append("query path does not resolve")
        return GateResult(
            gate_id="query_readiness",
            passed=passed,
            basis_refs=(dataset_ref,),
            reason="query-ready registry state and path confirmed" if passed else "; ".join(reasons),
        )

    pack.register_gate("query_readiness", readiness_gate)
    return pack
