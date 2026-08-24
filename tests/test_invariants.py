import pytest

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
    MemoryStore,
    Provenance,
    Receipt,
    RevisionLink,
)


def seeded_engine():
    engine = CitationEngine(MemoryStore())
    source = engine.record_artifact(
        Artifact(
            id="artifact:source-1",
            kind="source",
            payload={"value": 42},
            provenance=Provenance(source="fixture", method="direct-observation"),
        )
    )
    subject = engine.record_artifact(
        Artifact(
            id="artifact:subject-1",
            kind="subject",
            payload={"name": "fixture subject"},
            provenance=Provenance(source="fixture", method="declared"),
        )
    )
    return engine, source, subject


def test_artifact_digest_is_not_changed_by_address_label():
    provenance = Provenance(source="fixture", method="direct")
    left = Artifact(id="artifact:a", kind="source", payload={"x": 1}, provenance=provenance)
    right = Artifact(id="artifact:b", kind="source", payload={"x": 1}, provenance=provenance)
    assert left.digest == right.digest


def test_assertion_requires_basis():
    with pytest.raises(ValueError):
        Assertion(
            id="assertion:x",
            subject_ref="artifact:subject",
            predicate="has_value",
            value=True,
            status=EpistemicStatus.SUPPORTED,
            basis_refs=(),
        )


def test_unknown_basis_cannot_enter_canonical_state():
    engine, _, subject = seeded_engine()
    assertion = Assertion(
        id="assertion:x",
        subject_ref=subject.id,
        predicate="has_value",
        value=True,
        status=EpistemicStatus.SUPPORTED,
        basis_refs=("artifact:missing",),
    )
    with pytest.raises(ValueError):
        engine.record_assertion(assertion)


def test_citation_is_a_first_class_resolvable_edge():
    engine, source, subject = seeded_engine()
    assertion = engine.record_assertion(
        Assertion(
            id="assertion:x",
            subject_ref=subject.id,
            predicate="has_value",
            value=True,
            status=EpistemicStatus.SUPPORTED,
            basis_refs=(source.id,),
        )
    )
    citation = engine.record_citation(
        Citation(
            id="citation:x",
            subject_ref=assertion.id,
            basis_ref=source.id,
            relation=CitationRelation.SUPPORTS,
            locator="fixture:1",
        )
    )
    assert engine.store.get(citation.id).basis_ref == source.id


def test_failed_gate_cannot_authorize():
    engine, source, subject = seeded_engine()
    pack = ContextPack(name="fixture", version="1")
    pack.register_gate(
        "must-pass",
        lambda subject_ref, context: GateResult(
            gate_id="must-pass",
            passed=False,
            basis_refs=(source.id,),
            reason="fixture intentionally blocks",
        ),
    )
    decision = engine.evaluate(
        pack=pack,
        subject_ref=subject.id,
        rule_id="rule:fixture",
        context={},
        decision_id="decision:x",
    )
    with pytest.raises(ValueError):
        engine.transition_authority(
            transition_id="authority:x",
            subject_ref=subject.id,
            current=AuthorityState.BLOCKED,
            target=AuthorityState.AUTHORIZED,
            decision_ref=decision.id,
            actor="operator",
        )


def test_decision_cannot_authorize_different_subject():
    engine, source, subject = seeded_engine()
    other = engine.record_artifact(
        Artifact(
            id="artifact:subject-2",
            kind="subject",
            payload={"name": "other"},
            provenance=Provenance(source="fixture", method="declared"),
        )
    )
    pack = ContextPack(name="fixture", version="1")
    pack.register_gate(
        "pass",
        lambda subject_ref, context: GateResult(
            gate_id="pass",
            passed=True,
            basis_refs=(source.id,),
            reason="fixture passes",
        ),
    )
    decision = engine.evaluate(
        pack=pack,
        subject_ref=subject.id,
        rule_id="rule:fixture",
        context={},
        decision_id="decision:x",
    )
    with pytest.raises(ValueError):
        engine.transition_authority(
            transition_id="authority:x",
            subject_ref=other.id,
            current=AuthorityState.REVIEWABLE,
            target=AuthorityState.AUTHORIZED,
            decision_ref=decision.id,
            actor="operator",
        )


def test_revision_preserves_prior_object():
    engine, source, _ = seeded_engine()
    replacement = engine.record_artifact(
        Artifact(
            id="artifact:source-2",
            kind="source",
            payload={"value": 43},
            provenance=Provenance(
                source="fixture",
                method="corrected-observation",
                parent_refs=(source.id,),
            ),
        )
    )
    revision = engine.record_revision(
        RevisionLink(
            id="revision:x",
            prior_ref=source.id,
            replacement_ref=replacement.id,
            reason="corrected fixture",
            actor="reviewer",
        )
    )
    assert engine.store.contains(source.id)
    assert engine.store.get(revision.id).replacement_ref == replacement.id


def test_receipt_must_resolve_every_reference():
    engine, source, _ = seeded_engine()
    receipt = Receipt(
        id="receipt:x",
        workflow="fixture",
        input_refs=(source.id,),
        assertion_refs=(),
        decision_refs=(),
        output_refs=("artifact:missing",),
    )
    with pytest.raises(ValueError):
        engine.issue_receipt(receipt)
