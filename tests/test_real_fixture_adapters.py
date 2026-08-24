import pytest

from citation_engine import (
    Artifact,
    AuthorityState,
    CitationEngine,
    CitationRelation,
    MemoryStore,
    Provenance,
)
from examples.packs.cite_grounding_adapter import ingest_grounded_claim
from examples.packs.hardware_bench_adapter import make_measurement_gate_pack


def test_cite_grounded_claim_maps_without_core_domain_types():
    engine = CitationEngine(MemoryStore())
    result = ingest_grounded_claim(
        engine,
        {
            "claim": "The reported mechanism is supported by the cited passage.",
            "status": "grounded",
            "confidence": 0.72,
            "evidence": [
                {
                    "paper_id": "paper-1",
                    "title": "Fixture paper",
                    "source": "fixture-index",
                    "score": 0.72,
                    "grounding": "pdf_passage",
                    "page": 3,
                    "excerpt": "A directly supporting fixture passage.",
                }
            ],
        },
    )

    assertion = engine.store.get(result["assertion_ref"])
    citation = engine.store.get(result["citation_refs"][0])
    assert assertion.status.value == "supported"
    assert citation.relation is CitationRelation.SUPPORTS
    assert citation.locator == "page:3"


def test_cite_ungrounded_claim_is_not_promoted_to_supported_assertion():
    engine = CitationEngine(MemoryStore())
    result = ingest_grounded_claim(
        engine,
        {
            "claim": "A planning hypothesis should remain ungrounded.",
            "status": "ungrounded",
            "confidence": 0.0,
            "evidence": [],
            "reason": "planning language",
        },
    )
    assert result["assertion_ref"] is None
    assert result["status"] == "ungrounded"


def _seed_hardware_fixture():
    engine = CitationEngine(MemoryStore())
    subject = engine.record_artifact(
        Artifact(
            id="hardware:interface:1",
            kind="hardware.interface",
            payload={"unresolved_fields": []},
            provenance=Provenance(source="hardware-splicer", method="interface-contract"),
        )
    )
    measurement = engine.record_artifact(
        Artifact(
            id="hardware:measurement:idle-voltage",
            kind="hardware.measurement",
            payload={"measurement_id": "idle_voltage_v", "value": 3.3, "unit": "V"},
            provenance=Provenance(source="bench", method="DMM"),
        )
    )
    pack = make_measurement_gate_pack(
        measurement_ref=measurement.id,
        gate_id="idle_voltage_v",
        expected_unit="V",
        lower=0.0,
        upper=5.5,
    )
    return engine, subject, measurement, pack


def test_hardware_measurement_gate_can_authorize_when_evidence_closes():
    engine, subject, _, pack = _seed_hardware_fixture()
    decision = engine.evaluate(
        pack=pack,
        subject_ref=subject.id,
        rule_id="hardware-splicer.measurement-gate",
        context={"value": 3.3, "unit": "V"},
        decision_id="hardware:decision:pass",
    )
    transition = engine.transition_authority(
        transition_id="hardware:authority:firmware",
        subject_ref=subject.id,
        current=AuthorityState.REVIEWABLE,
        target=AuthorityState.AUTHORIZED,
        decision_ref=decision.id,
        actor="fixture-operator",
    )
    assert decision.authorized is True
    assert transition.to_state is AuthorityState.AUTHORIZED


def test_hardware_wrong_unit_fails_closed_and_cannot_authorize():
    engine, subject, _, pack = _seed_hardware_fixture()
    decision = engine.evaluate(
        pack=pack,
        subject_ref=subject.id,
        rule_id="hardware-splicer.measurement-gate",
        context={"value": 3.3, "unit": "A"},
        decision_id="hardware:decision:block",
    )
    assert decision.authorized is False
    assert "expected unit V" in decision.gate_results[0].reason

    with pytest.raises(ValueError):
        engine.transition_authority(
            transition_id="hardware:authority:blocked",
            subject_ref=subject.id,
            current=AuthorityState.BLOCKED,
            target=AuthorityState.AUTHORIZED,
            decision_ref=decision.id,
            actor="fixture-operator",
        )
