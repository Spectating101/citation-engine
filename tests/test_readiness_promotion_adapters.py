import pytest

from citation_engine import AuthorityState, CitationEngine, MemoryStore
from examples.packs.research_drive_adapter import ingest_drive_dataset, make_query_readiness_pack
from examples.packs.sharpe_promotion_adapter import (
    ingest_sharpe_candidate,
    issue_promotion_receipt,
    make_promotion_pack,
)


def _drive_dataset(readiness="metadata_search"):
    return {
        "dataset_id": "fixture-market-data",
        "name": "Fixture market data",
        "source": "fixture-provider",
        "source_of_truth": "gdrive",
        "canonical_remote": "gdrive:research/fixture-market-data",
        "analysis_readiness": readiness,
    }


def test_drive_verified_custody_does_not_imply_query_readiness():
    engine = CitationEngine(MemoryStore())
    mapped = ingest_drive_dataset(
        engine,
        _drive_dataset("metadata_search"),
        archive_result={
            "ok": True,
            "verified": True,
            "remote_path": "gdrive:research/fixture-market-data",
        },
    )
    assert mapped["verification_assertion_ref"] is not None

    pack = make_query_readiness_pack(dataset_ref=mapped["dataset_ref"])
    decision = engine.evaluate(
        pack=pack,
        subject_ref=mapped["dataset_ref"],
        rule_id="research-drive.query-readiness",
        context={
            "analysis_readiness": "metadata_search",
            "path_resolves": True,
        },
        decision_id="drive:decision:not-ready",
    )
    assert decision.authorized is False
    assert "not query-ready" in decision.gate_results[0].reason


def test_drive_model_prose_cannot_upgrade_failed_verification():
    engine = CitationEngine(MemoryStore())
    mapped = ingest_drive_dataset(
        engine,
        _drive_dataset("instant"),
        archive_result={
            "ok": False,
            "verified": False,
            "remote_path": "gdrive:research/fixture-market-data",
            "model_says_verified": True,
        },
    )
    assert mapped["verification_ref"] is not None
    assert mapped["verification_assertion_ref"] is None


def test_drive_query_ready_requires_registry_state_and_resolving_path():
    engine = CitationEngine(MemoryStore())
    mapped = ingest_drive_dataset(engine, _drive_dataset("instant"))
    pack = make_query_readiness_pack(dataset_ref=mapped["dataset_ref"])

    blocked = engine.evaluate(
        pack=pack,
        subject_ref=mapped["dataset_ref"],
        rule_id="research-drive.query-readiness",
        context={
            "analysis_readiness": "instant",
            "path_resolves": False,
            "assistant_claim": "This dataset is ready to use.",
        },
        decision_id="drive:decision:path-missing",
    )
    assert blocked.authorized is False

    ready = engine.evaluate(
        pack=pack,
        subject_ref=mapped["dataset_ref"],
        rule_id="research-drive.query-readiness",
        context={"analysis_readiness": "instant", "path_resolves": True},
        decision_id="drive:decision:ready",
    )
    assert ready.authorized is True
    transition = engine.transition_authority(
        transition_id="drive:authority:query",
        subject_ref=mapped["dataset_ref"],
        current=AuthorityState.REVIEWABLE,
        target=AuthorityState.AUTHORIZED,
        decision_ref=ready.id,
        actor="fixture-runtime",
    )
    assert transition.to_state is AuthorityState.AUTHORIZED


def _sharpe_manifest(status="deployable_sleeve"):
    return {
        "manifest_version": "1",
        "run_id": "fixture-run-001",
        "strategy": "fixture-alpha",
        "status": status,
        "created_at": "2026-08-24T00:00:00Z",
        "run_dir": "backtests/fixture-run-001",
        "params": {
            "universe_id": "fixture-universe",
            "benchmark_id": "fixture-benchmark",
            "validation_protocol": "walk-forward",
            "cost_model_id": "fixture-cost",
            "risk_model_id": "fixture-risk",
            "execution_safety_config": "fixture-safety",
        },
        "artifacts": {
            "signal": {"path": "signal.csv"},
            "scorecard": {"path": "scorecard.json"},
        },
        "metrics": {"sharpe": 4.2, "annual_return": 0.61},
    }


def test_sharpe_attractive_metrics_cannot_bypass_failed_promotion_evidence():
    engine = CitationEngine(MemoryStore())
    mapped = ingest_sharpe_candidate(
        engine,
        manifest=_sharpe_manifest(),
        manifest_gate_result={
            "run_id": "fixture-run-001",
            "status": "deployable_sleeve",
            "passed": False,
            "reasons": ["artifact_sha256_mismatch:scorecard"],
        },
        frozen_decision={
            "decision_id": "fixture-run-001-frozen",
            "evaluated_at": "2026-08-24T01:00:00Z",
        },
    )
    pack = make_promotion_pack(
        candidate_ref=mapped["candidate_ref"],
        manifest_gate_ref=mapped["manifest_gate_ref"],
        frozen_decision_ref=mapped["frozen_decision_ref"],
        require_frozen_decision=True,
    )
    decision = engine.evaluate(
        pack=pack,
        subject_ref=mapped["candidate_ref"],
        rule_id="sharpe.deployable-promotion",
        context={
            "manifest_passed": False,
            "manifest_reasons": ["artifact_sha256_mismatch:scorecard"],
            "frozen_decision_evaluated": True,
            "metrics": {"sharpe": 4.2, "annual_return": 0.61},
        },
        decision_id="sharpe:decision:blocked",
    )
    assert decision.authorized is False
    assert any(g.gate_id == "manifest_integrity" and not g.passed for g in decision.gate_results)


def test_sharpe_deployable_candidate_requires_evaluated_frozen_decision():
    engine = CitationEngine(MemoryStore())
    mapped = ingest_sharpe_candidate(
        engine,
        manifest=_sharpe_manifest(),
        manifest_gate_result={"run_id": "fixture-run-001", "passed": True, "reasons": []},
        frozen_decision=None,
    )
    pack = make_promotion_pack(
        candidate_ref=mapped["candidate_ref"],
        manifest_gate_ref=mapped["manifest_gate_ref"],
        frozen_decision_ref=None,
        require_frozen_decision=True,
    )
    decision = engine.evaluate(
        pack=pack,
        subject_ref=mapped["candidate_ref"],
        rule_id="sharpe.deployable-promotion",
        context={"manifest_passed": True, "frozen_decision_evaluated": True},
        decision_id="sharpe:decision:no-freeze",
    )
    assert decision.authorized is False
    assert any(g.gate_id == "evaluated_frozen_decision" and not g.passed for g in decision.gate_results)


def test_sharpe_complete_promotion_evidence_authorizes_and_receipts_lineage():
    engine = CitationEngine(MemoryStore())
    mapped = ingest_sharpe_candidate(
        engine,
        manifest=_sharpe_manifest(),
        manifest_gate_result={"run_id": "fixture-run-001", "passed": True, "reasons": []},
        frozen_decision={
            "decision_id": "fixture-run-001-frozen",
            "evaluated_at": "2026-08-24T01:00:00Z",
            "active_return": 0.03,
        },
    )
    pack = make_promotion_pack(
        candidate_ref=mapped["candidate_ref"],
        manifest_gate_ref=mapped["manifest_gate_ref"],
        frozen_decision_ref=mapped["frozen_decision_ref"],
        require_frozen_decision=True,
    )
    decision = engine.evaluate(
        pack=pack,
        subject_ref=mapped["candidate_ref"],
        rule_id="sharpe.deployable-promotion",
        context={"manifest_passed": True, "frozen_decision_evaluated": True},
        decision_id="sharpe:decision:promote",
    )
    assert decision.authorized is True

    receipt = issue_promotion_receipt(
        engine,
        mapped=mapped,
        decision_ref=decision.id,
        evaluated_at="2026-08-24T02:00:00Z",
    )
    assert mapped["frozen_decision_ref"] in receipt.input_refs
    assert decision.id in receipt.decision_refs
