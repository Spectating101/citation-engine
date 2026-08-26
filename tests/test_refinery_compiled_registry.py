from __future__ import annotations

import pytest

from citation_engine import (
    Assertion,
    AuthorityTransition,
    CitationEngine,
    Decision,
    EpistemicStatus,
    MemoryStore,
    export_bundle,
)
from examples.packs.refinery_commons_adapter import (
    assertions_for_subject,
    ingest_compiled_registry,
    record_evidence_artifact,
    record_exact_provenance_claim,
)


def compiled_registry_fixture() -> tuple[dict, str, str, str, str]:
    registry_id = "rregistry:sha256:" + "0" * 64
    capability_id = "rcap:sha256:" + "1" * 64
    git_id = "rimpl:sha256:" + "2" * 64
    oci_id = "rimpl:sha256:" + "3" * 64
    digest = "a" * 64
    compiled = {
        "schema_version": 0,
        "registry_id": registry_id,
        "metadata": {"registry_name": "fixture Commons registry"},
        "capsules": [
            {
                "object_id": capability_id,
                "key": "capability:uv-toolchain",
                "intrinsic": {
                    "contract_version": "1",
                    "capability": "python-project-package-runtime-toolchain",
                    "behavior_claims": [{"id": "resolve", "statement": "resolve dependencies"}],
                    "constraints": [],
                    "falsifiers": ["cannot resolve a declared graph"],
                },
                "metadata": {"title": "uv toolchain"},
            }
        ],
        "implementations": [
            {
                "object_id": git_id,
                "key": "implementation:github-overlay:uv",
                "capsule_id": capability_id,
                "intrinsic": {
                    "capsule_id": capability_id,
                    "source": {
                        "kind": "git",
                        "ref": "github://astral-sh/uv",
                        "revision": "5715fe31",
                    },
                },
                "metadata": {"title": "uv Git revision"},
            },
            {
                "object_id": oci_id,
                "key": "implementation:oci:uv",
                "capsule_id": capability_id,
                "intrinsic": {
                    "capsule_id": capability_id,
                    "source": {
                        "kind": "oci",
                        "ref": "ghcr.io/astral-sh/uv",
                        "digest": f"sha256:{digest}",
                    },
                },
                "metadata": {"title": "uv OCI artifact"},
            },
        ],
        "claims": [
            {
                "object_id": "rclaim:sha256:" + "4" * 64,
                "key": "claim:uv-provenance",
                "subject_id": oci_id,
                "intrinsic": {
                    "subject_id": oci_id,
                    "claim_type": "provenance",
                    "outcome": "pass",
                    "evidence_ref": "https://example.invalid/uv-attestation",
                    "issuer": "machine:slsa-verifier",
                    "observed_at": "2026-08-21T00:00:00Z",
                    "payload": {
                        "verification_status": "verified",
                        "subjects": [{"digest": {"sha256": digest}}],
                    },
                },
                "metadata": {},
            },
            {
                "object_id": "rclaim:sha256:" + "5" * 64,
                "key": "claim:curation",
                "subject_id": capability_id,
                "intrinsic": {
                    "subject_id": capability_id,
                    "claim_type": "curation",
                    "outcome": "pass",
                    "evidence_ref": "fixture://curation-record",
                    "issuer": "fixture-review-board",
                    "observed_at": "2026-08-21T00:00:00Z",
                    "payload": {"recommendation": "retain"},
                },
                "metadata": {},
            },
        ],
    }
    return compiled, registry_id, capability_id, git_id, oci_id


def test_current_refinery_compiled_registry_ingests_without_core_schema_change():
    engine = CitationEngine(MemoryStore())
    compiled, registry_id, capability_id, git_id, oci_id = compiled_registry_fixture()

    mapped = ingest_compiled_registry(engine, compiled)

    assert mapped["registry_ref"] == registry_id
    assert mapped["capability_refs"] == (capability_id,)
    assert mapped["implementation_refs"] == (git_id, oci_id)
    assert engine.store.get(capability_id).kind == "refinery.capability"
    assert engine.store.get(oci_id).kind == "refinery.implementation"

    oci_claims = assertions_for_subject(engine, oci_id)
    git_claims = assertions_for_subject(engine, git_id)
    capability_claims = assertions_for_subject(engine, capability_id)

    assert len(oci_claims) == 1
    assert oci_claims[0].predicate == "refinery.claim.provenance"
    # A normalized imported claim is a record of what Refinery said, not a fresh
    # independent verification performed by Citation Engine.
    assert oci_claims[0].status is EpistemicStatus.OBSERVED
    assert git_claims == ()
    assert len(capability_claims) == 1
    assert capability_claims[0].predicate == "refinery.claim.curation"

    # Imported curation evidence must not silently manufacture CE authority.
    assert not any(isinstance(engine.store.get(ref), Decision) for ref in engine.store.ids())
    assert not any(isinstance(engine.store.get(ref), AuthorityTransition) for ref in engine.store.ids())


def test_imported_claim_bundle_keeps_registry_subject_and_evidence_pointer_closure():
    engine = CitationEngine(MemoryStore())
    compiled, registry_id, capability_id, _, oci_id = compiled_registry_fixture()
    mapped = ingest_compiled_registry(engine, compiled)

    provenance_assertion = next(
        engine.store.get(ref)
        for ref in mapped["assertion_refs"]
        if isinstance(engine.store.get(ref), Assertion)
        and engine.store.get(ref).subject_ref == oci_id
    )
    bundle = export_bundle(engine.store, [provenance_assertion.id])
    ids = {row["data"].get("id") for row in bundle["objects"]}

    assert provenance_assertion.id in ids
    assert provenance_assertion.basis_refs[0] in ids
    assert oci_id in ids
    assert capability_id in ids
    assert registry_id in ids


def test_raw_slsa_can_upgrade_exact_imported_oci_subject_but_not_git_sibling():
    engine = CitationEngine(MemoryStore())
    compiled, _, _, git_id, oci_id = compiled_registry_fixture()
    ingest_compiled_registry(engine, compiled)
    digest = "a" * 64

    raw = record_evidence_artifact(
        engine,
        artifact_id="refinery:evidence:raw-slsa",
        kind="slsa.provenance",
        payload={
            "statement": {
                "predicateType": "https://slsa.dev/provenance/v1",
                "subject": [{"name": "uv", "digest": {"sha256": digest}}],
            }
        },
        source="slsa-verifier",
        method="raw-verified-attestation",
    )

    verified = record_exact_provenance_claim(
        engine,
        assertion_id="refinery:assertion:raw-oci-provenance",
        subject_ref=oci_id,
        evidence_ref=raw.id,
        verification_status="verified",
        expected_sha256=digest,
    )
    assert verified.status is EpistemicStatus.VERIFIED
    assert verified.value is True

    with pytest.raises(ValueError, match="exact implementation subject"):
        record_exact_provenance_claim(
            engine,
            assertion_id="refinery:assertion:raw-git-illegal",
            subject_ref=git_id,
            evidence_ref=raw.id,
            verification_status="verified",
            expected_sha256=digest,
        )
