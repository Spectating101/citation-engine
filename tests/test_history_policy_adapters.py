import pytest

from citation_engine import AuthorityState, CitationRelation, CitationEngine, MemoryStore
from examples.packs.nocturnal_adapter import (
    ingest_correction,
    ingest_public_snapshot_manifest,
)
from examples.packs.policy_lab_adapter import (
    ingest_policy_lab_decision,
    issue_policy_lab_receipt,
)


HASHES = {
    "decision": "d" * 64,
    "case": "e" * 64,
    "policy": "a" * 64,
    "evidence": "b" * 64,
    "context": "c" * 64,
}


def test_nocturnal_correction_preserves_prior_and_records_explicit_lineage():
    engine = CitationEngine(MemoryStore())
    mapped = ingest_correction(
        engine,
        prior_module={
            "module_id": "matter-1-original",
            "status_stage": "allegation",
            "text": "Original historical record",
        },
        correction_module={
            "module_id": "matter-1-correction",
            "correction_of": "matter-1-original",
            "status_stage": "corrected",
            "text": "Later correction",
        },
    )

    prior = engine.store.get(mapped["prior_ref"])
    replacement = engine.store.get(mapped["correction_ref"])
    revision = engine.store.get(mapped["revision_ref"])
    citation = engine.store.get(mapped["citation_ref"])

    assert prior.payload["text"] == "Original historical record"
    assert replacement.payload["text"] == "Later correction"
    assert revision.prior_ref == prior.id
    assert revision.replacement_ref == replacement.id
    assert citation.relation is CitationRelation.CORRECTS


def _snapshot_manifest(*, publishable: bool):
    if publishable:
        return {
            "snapshot_id": "nocturnal-fixture-pass",
            "commit_sha": "abc123",
            "dataset_license": "CC-BY-4.0",
            "source_rights_reviewed": True,
            "pilot_gate": {"publication_allowed": True, "blockers": []},
            "publishable": True,
            "publication_blockers": [],
            "counts": {"modules": 3, "chains": 1},
            "integrity": {"ok": True, "chains": [{"chain_id": "fixture", "ok": True}]},
            "files": {"modules.jsonl": {"sha256": "1" * 64, "bytes": 42}},
        }
    return {
        "snapshot_id": "nocturnal-fixture-block",
        "commit_sha": "abc123",
        "dataset_license": "UNSPECIFIED-NOT-FOR-PUBLICATION",
        "source_rights_reviewed": False,
        "pilot_gate": {"publication_allowed": False, "blockers": ["approval missing"]},
        "publishable": False,
        "publication_blockers": ["dataset license is unspecified", "source-rights review has not been recorded"],
        "counts": {"modules": 3, "chains": 1},
        "integrity": {"ok": True, "chains": [{"chain_id": "fixture", "ok": True}]},
        "files": {"modules.jsonl": {"sha256": "1" * 64, "bytes": 42}},
    }


def test_nocturnal_publishable_snapshot_advances_publication_authority():
    engine = CitationEngine(MemoryStore())
    mapped = ingest_public_snapshot_manifest(engine, _snapshot_manifest(publishable=True))

    decision = engine.store.get(mapped["decision_ref"])
    transition = engine.store.get(mapped["authority_ref"])
    assert decision.authorized is True
    assert decision.outcome == "publishable"
    assert transition.to_state is AuthorityState.AUTHORIZED


def test_nocturnal_release_gate_fails_closed_when_release_preconditions_are_missing():
    engine = CitationEngine(MemoryStore())
    mapped = ingest_public_snapshot_manifest(engine, _snapshot_manifest(publishable=False))
    decision = engine.store.get(mapped["decision_ref"])

    assert decision.authorized is False
    assert mapped["authority_ref"] is None
    assert {gate.gate_id for gate in decision.gate_results if not gate.passed} == {
        "dataset_license",
        "source_rights",
        "pilot_publication",
    }

    with pytest.raises(ValueError):
        engine.transition_authority(
            transition_id="nocturnal:forced-publication",
            subject_ref=mapped["release_ref"],
            current=AuthorityState.BLOCKED,
            target=AuthorityState.AUTHORIZED,
            decision_ref=decision.id,
            actor="fixture-operator",
        )


def _policy_decision(*, blocked: bool = False):
    admission_status = "BLOCK" if blocked else "PASS"
    admission = {
        "result": admission_status,
        "evaluations": [
            {
                "calculator_id": "POSITIVE_SURPLUS",
                "constraint_class": "ADMISSION_GATE",
                "status": admission_status,
                "input_refs": [HASHES["evidence"]],
                "explanation": "Evidence gate fixture.",
            }
        ],
        "blocking_rules": ["POSITIVE_SURPLUS"] if blocked else [],
    }
    capacity = {
        "evaluated": not blocked,
        "unit": "ENERGY_CLAIM_UNIT" if not blocked else None,
        "quantity_decimals": 6 if not blocked else None,
        "evaluations": [] if blocked else [
            {
                "calculator_id": "EVIDENCE_BACKED_CAPACITY",
                "constraint_class": "QUANTITY_CEILING",
                "status": "PASS",
                "input_refs": [HASHES["evidence"]],
                "capacity": 100,
                "unit": "ENERGY_CLAIM_UNIT",
                "quantity_decimals": 6,
                "explanation": "Evidence backing permits 100 units.",
            }
        ],
        "admitted_maximum": 0 if blocked else 100,
        "binding_constraints": [] if blocked else ["EVIDENCE_BACKED_CAPACITY"],
    }
    return {
        "schema": "solarpunk.constraint.decision_result.v1",
        "decision_id": HASHES["decision"] if not blocked else "f" * 64,
        "case_id": "TYN-001",
        "case_hash": HASHES["case"],
        "policy_id": "ENERGY-CASE-PILOT-005",
        "policy_version": "1.0.0",
        "policy_manifest_hash": HASHES["policy"],
        "evidence_hashes": [HASHES["evidence"]],
        "context_refs": [{"context_id": "resource:tyn", "context_hash": HASHES["context"]}],
        "admission": admission,
        "capacity": capacity,
        "decision": "BLOCKED" if blocked else "ADMIT_WITH_LIMIT",
        "warnings": [],
        "boundary": "Research decision under declared inputs; not legal issuance authority.",
    }


def test_policy_lab_decision_import_preserves_domain_outcome_without_reimplementing_calculators():
    engine = CitationEngine(MemoryStore())
    mapped = ingest_policy_lab_decision(engine, _policy_decision())
    decision = engine.store.get(mapped["decision_ref"])

    assert decision.outcome == "ADMIT_WITH_LIMIT"
    assert decision.authorized is True
    assert decision.rule_id == "ENERGY-CASE-PILOT-005@1.0.0"
    assert len(decision.gate_results) == 2
    assert mapped["decision_digest"] == decision.digest


def test_policy_lab_receipt_time_changes_receipt_not_decision_identity():
    engine = CitationEngine(MemoryStore())
    mapped = ingest_policy_lab_decision(engine, _policy_decision())
    decision = engine.store.get(mapped["decision_ref"])

    first = issue_policy_lab_receipt(
        engine,
        mapped=mapped,
        external_receipt={
            "decision_id": HASHES["decision"],
            "evaluated_at": "2026-07-14T15:42:18Z",
            "runtime": {"package": "@solarpunk/constraint-core", "package_version": "0.1.0-alpha.1"},
            "data_boundary": "Raw evidence excluded.",
        },
    )
    second = issue_policy_lab_receipt(
        engine,
        mapped=mapped,
        external_receipt={
            "decision_id": HASHES["decision"],
            "evaluated_at": "2026-07-14T16:42:18Z",
            "runtime": {"package": "@solarpunk/constraint-core", "package_version": "0.1.0-alpha.1"},
            "data_boundary": "Raw evidence excluded.",
        },
    )

    assert first.digest != second.digest
    assert first.metadata["decision_digest"] == decision.digest
    assert second.metadata["decision_digest"] == decision.digest


def test_policy_lab_blocked_decision_remains_non_authorizing():
    engine = CitationEngine(MemoryStore())
    mapped = ingest_policy_lab_decision(engine, _policy_decision(blocked=True))
    decision = engine.store.get(mapped["decision_ref"])

    assert decision.outcome == "BLOCKED"
    assert decision.authorized is False
    assert decision.gate_results[0].passed is False
