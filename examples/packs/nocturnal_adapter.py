from __future__ import annotations

from typing import Any, Mapping

from citation_engine import (
    Artifact,
    AuthorityState,
    Citation,
    CitationEngine,
    CitationRelation,
    Decision,
    GateResult,
    Provenance,
    RevisionLink,
)


_UNSPECIFIED_LICENSES = {"", "unspecified", "unspecified-not-for-publication", "noassertion"}


def ingest_correction(
    engine: CitationEngine,
    *,
    prior_module: Mapping[str, Any],
    correction_module: Mapping[str, Any],
) -> dict[str, str]:
    """Map Nocturnal's append-only correction semantics into neutral lineage."""
    prior_id = str(prior_module.get("module_id") or "").strip()
    correction_id = str(correction_module.get("module_id") or "").strip()
    if not prior_id or not correction_id:
        raise ValueError("both prior and correction modules require module_id")

    declared_prior = str(correction_module.get("correction_of") or "").strip()
    supersedes = {str(value).strip() for value in correction_module.get("supersedes") or []}
    if declared_prior and declared_prior != prior_id and prior_id not in supersedes:
        raise ValueError("correction does not point to the supplied prior module")

    prior_ref = f"nocturnal:module:{prior_id}"
    correction_ref = f"nocturnal:module:{correction_id}"

    engine.record_artifact(Artifact(
        id=prior_ref,
        kind="nocturnal.module",
        payload=dict(prior_module),
        provenance=Provenance(source="nocturnal", method="ledger-module"),
    ))
    engine.record_artifact(Artifact(
        id=correction_ref,
        kind="nocturnal.module",
        payload=dict(correction_module),
        provenance=Provenance(
            source="nocturnal",
            method="accepted-correction",
            parent_refs=(prior_ref,),
        ),
    ))

    revision = engine.record_revision(RevisionLink(
        id=f"nocturnal:revision:{correction_id}",
        prior_ref=prior_ref,
        replacement_ref=correction_ref,
        reason="accepted correction preserves prior historical record",
        actor="nocturnal-operator",
    ))
    citation = engine.record_citation(Citation(
        id=f"nocturnal:citation:corrects:{correction_id}",
        subject_ref=correction_ref,
        basis_ref=prior_ref,
        relation=CitationRelation.CORRECTS,
        note="Correction/supersession edge from Nocturnal public-memory history.",
        produced_by="nocturnal-adapter",
    ))
    return {
        "prior_ref": prior_ref,
        "correction_ref": correction_ref,
        "revision_ref": revision.id,
        "citation_ref": citation.id,
    }


def ingest_public_snapshot_manifest(
    engine: CitationEngine,
    manifest: Mapping[str, Any],
    *,
    actor: str = "nocturnal-release-gate",
) -> dict[str, str | None]:
    """Import Nocturnal's already-evaluated publication gate without reimplementing its runtime."""
    snapshot_id = str(manifest.get("snapshot_id") or "").strip()
    if not snapshot_id:
        raise ValueError("snapshot manifest requires snapshot_id")

    manifest_ref = f"nocturnal:snapshot-manifest:{snapshot_id}"
    release_ref = f"nocturnal:release:{snapshot_id}"
    engine.record_artifact(Artifact(
        id=manifest_ref,
        kind="nocturnal.public_snapshot_manifest",
        payload=dict(manifest),
        provenance=Provenance(source="nocturnal", method="public-snapshot-export"),
    ))
    engine.record_artifact(Artifact(
        id=release_ref,
        kind="release.candidate",
        payload={
            "snapshot_id": snapshot_id,
            "commit_sha": manifest.get("commit_sha"),
            "counts": manifest.get("counts") or {},
            "files": manifest.get("files") or {},
        },
        provenance=Provenance(
            source="nocturnal",
            method="publication-candidate",
            parent_refs=(manifest_ref,),
        ),
    ))

    integrity_ok = bool((manifest.get("integrity") or {}).get("ok"))
    dataset_license = str(manifest.get("dataset_license") or "").strip()
    license_ok = dataset_license.casefold() not in _UNSPECIFIED_LICENSES
    rights_ok = bool(manifest.get("source_rights_reviewed"))
    pilot_ok = bool((manifest.get("pilot_gate") or {}).get("publication_allowed"))

    gates = (
        GateResult("strict_integrity", integrity_ok, (manifest_ref,), "strict ledger integrity"),
        GateResult("dataset_license", license_ok, (manifest_ref,), "explicit dataset license"),
        GateResult("source_rights", rights_ok, (manifest_ref,), "source-rights review recorded"),
        GateResult("pilot_publication", pilot_ok, (manifest_ref,), "bounded pilot publication approval"),
    )
    computed_publishable = all(gate.passed for gate in gates)
    declared_publishable = bool(manifest.get("publishable"))
    if declared_publishable != computed_publishable:
        raise ValueError("snapshot publishable flag conflicts with its declared release gates")

    decision = engine.record_decision(Decision(
        id=f"nocturnal:publication-decision:{snapshot_id}",
        subject_ref=release_ref,
        outcome="publishable" if computed_publishable else "blocked",
        rule_id="nocturnal.public_snapshot.v1",
        gate_results=gates,
        basis_refs=(manifest_ref,),
    ))

    authority_ref: str | None = None
    if decision.authorized:
        transition = engine.transition_authority(
            transition_id=f"nocturnal:publication-authority:{snapshot_id}",
            subject_ref=release_ref,
            current=AuthorityState.REVIEWABLE,
            target=AuthorityState.AUTHORIZED,
            decision_ref=decision.id,
            actor=actor,
        )
        authority_ref = transition.id

    return {
        "manifest_ref": manifest_ref,
        "release_ref": release_ref,
        "decision_ref": decision.id,
        "authority_ref": authority_ref,
    }
