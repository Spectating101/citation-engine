from __future__ import annotations

import pytest

from citation_engine import (
    AuthorityState,
    CitationEngine,
    CitationRelation,
    EpistemicStatus,
    MemoryStore,
    export_bundle,
)
from examples.packs.refinery_commons_adapter import (
    assertions_for_subject,
    capability_ref,
    implementation_ref,
    issue_review_receipt,
    make_curation_pack,
    record_capability,
    record_claim,
    record_evidence_artifact,
    record_exact_provenance_claim,
    record_implementation,
)


def _seed_capability(engine: CitationEngine):
    review = record_evidence_artifact(
        engine,
        artifact_id="refinery:evidence:capability-review",
        kind="refinery.review_packet",
        payload={"source": "pinned upstream description", "reviewed": True},
        source="fixture",
        method="manual-review",
    )
    intrinsic = {
        "contract_version": "1",
        "capability": "python-project-package-runtime-toolchain",
        "behavior_claims": [
            {"id": "resolve", "statement": "resolve Python project dependencies"},
        ],
        "constraints": [],
        "falsifiers": ["cannot resolve a declared dependency graph"],
    }
    capability = record_capability(
        engine,
        intrinsic=intrinsic,
        basis_refs=(review.id,),
        metadata={"title": "Python project/package/runtime toolchain"},
    )
    return review, intrinsic, capability


def _record_git_and_oci_implementations(engine: CitationEngine, capability_id: str):
    git_source = record_evidence_artifact(
        engine,
        artifact_id="refinery:evidence:uv-git",
        kind="source.git_revision",
        payload={"repository": "github://astral-sh/uv", "revision": "5715fe31"},
        source="github",
        method="pinned-revision",
    )
    oci_digest = "a" * 64
    oci_source = record_evidence_artifact(
        engine,
        artifact_id="refinery:evidence:uv-oci",
        kind="source.oci_descriptor",
        payload={"ref": "ghcr.io/astral-sh/uv", "digest": f"sha256:{oci_digest}"},
        source="oci",
        method="descriptor",
    )
    git_impl = record_implementation(
        engine,
        capability_ref=capability_id,
        implementation_identity={
            "kind": "git",
            "repository": "github://astral-sh/uv",
            "revision": "5715fe31",
        },
        source_ref=git_source.id,
    )
    oci_impl = record_implementation(
        engine,
        capability_ref=capability_id,
        implementation_identity={
            "kind": "oci",
            "ref": "ghcr.io/astral-sh/uv",
            "digest": f"sha256:{oci_digest}",
        },
        source_ref=oci_source.id,
    )
    return git_source, oci_source, git_impl, oci_impl, oci_digest


def test_semantic_capability_identity_is_stable_while_realization_identity_changes():
    intrinsic = {
        "capability": "stateful-agent-orchestration",
        "behavior_claims": [{"id": "resume", "statement": "resume stateful execution"}],
    }
    first_capability = capability_ref(intrinsic)
    second_capability = capability_ref(dict(intrinsic))
    assert first_capability == second_capability

    first_impl = implementation_ref(
        capability_ref=first_capability,
        implementation_identity={"kind": "git", "revision": "aaa"},
    )
    second_impl = implementation_ref(
        capability_ref=first_capability,
        implementation_identity={"kind": "git", "revision": "bbb"},
    )
    assert first_impl != second_impl

    changed_contract = dict(intrinsic)
    changed_contract["behavior_claims"] = [
        {"id": "resume", "statement": "resume and deterministically replay stateful execution"},
    ]
    assert capability_ref(changed_contract) != first_capability


def test_verified_oci_provenance_does_not_launder_onto_sibling_git_implementation():
    engine = CitationEngine(MemoryStore())
    _, _, capability = _seed_capability(engine)
    _, _, git_impl, oci_impl, oci_digest = _record_git_and_oci_implementations(engine, capability.id)

    slsa = record_evidence_artifact(
        engine,
        artifact_id="refinery:evidence:uv-slsa",
        kind="slsa.provenance",
        payload={
            "statement": {
                "predicateType": "https://slsa.dev/provenance/v1",
                "subject": [{"name": "uv", "digest": {"sha256": oci_digest}}],
            },
            "verification_status": "verified",
        },
        source="slsa-verifier",
        method="verified-attestation",
    )

    provenance = record_exact_provenance_claim(
        engine,
        assertion_id="refinery:assertion:uv-oci-provenance",
        subject_ref=oci_impl.id,
        evidence_ref=slsa.id,
        verification_status="verified",
        expected_sha256=oci_digest,
    )
    assert provenance.subject_ref == oci_impl.id
    assert assertions_for_subject(engine, git_impl.id) == ()
    assert [row.predicate for row in assertions_for_subject(engine, oci_impl.id)] == ["provenance.verified"]

    with pytest.raises(ValueError, match="exact implementation subject"):
        record_exact_provenance_claim(
            engine,
            assertion_id="refinery:assertion:illegal-sibling-promotion",
            subject_ref=git_impl.id,
            evidence_ref=slsa.id,
            verification_status="verified",
            expected_sha256=oci_digest,
        )


def test_positive_and_negative_evidence_coexist_without_erasing_history():
    engine = CitationEngine(MemoryStore())
    _, _, capability = _seed_capability(engine)
    _, _, git_impl, _, _ = _record_git_and_oci_implementations(engine, capability.id)

    pass_evidence = record_evidence_artifact(
        engine,
        artifact_id="refinery:evidence:evaluation-pass",
        kind="evaluation.report",
        payload={"test": "bounded-control", "outcome": "pass"},
        source="fixture-evaluator",
        method="bounded-control",
    )
    fail_evidence = record_evidence_artifact(
        engine,
        artifact_id="refinery:evidence:evaluation-fail",
        kind="evaluation.report",
        payload={"test": "replay-control", "outcome": "fail"},
        source="fixture-evaluator",
        method="adversarial-control",
    )

    record_claim(
        engine,
        assertion_id="refinery:assertion:control-pass",
        subject_ref=git_impl.id,
        predicate="evaluation.bounded_control",
        value=True,
        status=EpistemicStatus.VERIFIED,
        basis_refs=(pass_evidence.id,),
    )
    record_claim(
        engine,
        assertion_id="refinery:assertion:replay-fail",
        subject_ref=git_impl.id,
        predicate="evaluation.replay_safe",
        value=False,
        status=EpistemicStatus.VERIFIED,
        basis_refs=(fail_evidence.id,),
        relation=CitationRelation.CONTRADICTS,
    )

    rows = assertions_for_subject(engine, git_impl.id)
    assert {(row.predicate, row.value) for row in rows} == {
        ("evaluation.bounded_control", True),
        ("evaluation.replay_safe", False),
    }
    assert engine.store.contains(pass_evidence.id)
    assert engine.store.contains(fail_evidence.id)


def test_evidence_maturity_cannot_become_recommendation_without_explicit_curation():
    engine = CitationEngine(MemoryStore())
    _, _, capability = _seed_capability(engine)
    _, _, _, oci_impl, _ = _record_git_and_oci_implementations(engine, capability.id)

    curation = record_evidence_artifact(
        engine,
        artifact_id="refinery:evidence:curation-act",
        kind="refinery.curation_record",
        payload={"subregistry": "fixture", "curator": "review-board"},
        source="fixture-subregistry",
        method="explicit-curation-record",
    )
    pack = make_curation_pack(curation_basis_ref=curation.id)

    blocked = engine.evaluate(
        pack=pack,
        subject_ref=oci_impl.id,
        rule_id="refinery:rule:recommendation",
        context={"explicit_curation": False, "curator": ""},
        decision_id="refinery:decision:not-recommended",
    )
    assert blocked.authorized is False
    with pytest.raises(ValueError):
        engine.transition_authority(
            transition_id="refinery:authority:illegal",
            subject_ref=oci_impl.id,
            current=AuthorityState.REVIEWABLE,
            target=AuthorityState.AUTHORIZED,
            decision_ref=blocked.id,
            actor="refinery",
        )

    allowed = engine.evaluate(
        pack=pack,
        subject_ref=oci_impl.id,
        rule_id="refinery:rule:recommendation",
        context={"explicit_curation": True, "curator": "review-board"},
        decision_id="refinery:decision:recommended",
    )
    transition = engine.transition_authority(
        transition_id="refinery:authority:recommended",
        subject_ref=oci_impl.id,
        current=AuthorityState.REVIEWABLE,
        target=AuthorityState.AUTHORIZED,
        decision_ref=allowed.id,
        actor="review-board",
    )
    assert transition.to_state is AuthorityState.AUTHORIZED


def test_refinery_review_receipt_exports_complete_reference_closure():
    engine = CitationEngine(MemoryStore())
    review, _, capability = _seed_capability(engine)
    _, oci_source, _, oci_impl, _ = _record_git_and_oci_implementations(engine, capability.id)

    evaluation = record_evidence_artifact(
        engine,
        artifact_id="refinery:evidence:review-evaluation",
        kind="evaluation.report",
        payload={"outcome": "pass"},
        source="fixture-evaluator",
        method="review",
    )
    assertion = record_claim(
        engine,
        assertion_id="refinery:assertion:review-evaluation",
        subject_ref=oci_impl.id,
        predicate="evaluation.reviewed",
        value=True,
        status=EpistemicStatus.VERIFIED,
        basis_refs=(evaluation.id,),
    )
    curation = record_evidence_artifact(
        engine,
        artifact_id="refinery:evidence:review-curation",
        kind="refinery.curation_record",
        payload={"curator": "review-board"},
        source="fixture-subregistry",
        method="explicit-curation-record",
    )
    decision = engine.evaluate(
        pack=make_curation_pack(curation_basis_ref=curation.id),
        subject_ref=oci_impl.id,
        rule_id="refinery:rule:review",
        context={"explicit_curation": True, "curator": "review-board"},
        decision_id="refinery:decision:review",
    )
    receipt = issue_review_receipt(
        engine,
        subject_ref=oci_impl.id,
        decision_ref=decision.id,
        evidence_refs=(evaluation.id, curation.id),
        assertion_refs=(assertion.id,),
        reviewed_at="2026-08-27T00:00:00Z",
    )

    bundle = export_bundle(engine.store, [receipt.id])
    bundled_ids = {row["data"].get("id") for row in bundle["objects"]}
    assert receipt.id in bundled_ids
    assert decision.id in bundled_ids
    assert assertion.id in bundled_ids
    assert evaluation.id in bundled_ids
    assert curation.id in bundled_ids
    assert oci_impl.id in bundled_ids
    assert oci_source.id in bundled_ids
    assert capability.id in bundled_ids
    assert review.id in bundled_ids


def test_same_adapter_handles_real_world_institutional_shape_without_core_ontology_change():
    engine = CitationEngine(MemoryStore())
    official = record_evidence_artifact(
        engine,
        artifact_id="refinery:evidence:coral-activity-source",
        kind="public.institutional_source",
        payload={
            "activity": "coral restoration",
            "dates": "2026-06-03/2026-06-10",
            "substrates": 50,
            "fragments": 2500,
        },
        source="official-publication",
        method="bounded-source-extraction",
    )
    capability = record_capability(
        engine,
        intrinsic={
            "contract_version": "1",
            "capability": "coral-restoration-activity",
            "behavior_claims": [{"id": "restore", "statement": "perform bounded coral-restoration activity"}],
            "constraints": ["activity evidence does not establish ecological effectiveness"],
            "falsifiers": ["no documented restoration activity"],
        },
        basis_refs=(official.id,),
    )
    initiative = record_implementation(
        engine,
        capability_ref=capability.id,
        implementation_identity={
            "kind": "institutional-initiative",
            "entity": "Telkom Bisa Biru",
            "location": "Buru Island",
            "period": "2026-06-03/2026-06-10",
        },
        source_ref=official.id,
    )
    activity = record_claim(
        engine,
        assertion_id="refinery:assertion:coral-activity-documented",
        subject_ref=initiative.id,
        predicate="activity.documented",
        value=True,
        status=EpistemicStatus.SUPPORTED,
        basis_refs=(official.id,),
    )
    effectiveness = record_claim(
        engine,
        assertion_id="refinery:assertion:coral-effectiveness-unknown",
        subject_ref=initiative.id,
        predicate="ecological_effectiveness",
        value="unknown",
        status=EpistemicStatus.OBSERVED,
        basis_refs=(official.id,),
    )

    assert activity.value is True
    assert effectiveness.value == "unknown"
    assert initiative.kind == "refinery.implementation"
    assert capability.kind == "refinery.capability"
