"""Minimal fresh-project example for Citation Engine.

Run after installing the package:
    python examples/minimal_seed.py

It writes an append-only canonical store plus a portable receipt-rooted bundle.
"""

from __future__ import annotations

import json
from pathlib import Path

from citation_engine import (
    Artifact,
    AuthorityState,
    CitationEngine,
    ContextPack,
    GateResult,
    JsonlStore,
    Provenance,
    Receipt,
    export_bundle,
)


def build_seed(output_dir: str | Path = ".citation-engine") -> dict:
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)

    engine = CitationEngine(JsonlStore(output / "canonical.jsonl"))
    evidence = engine.record_artifact(Artifact(
        id="example:evidence:1",
        kind="example.evidence",
        payload={"observed": 42},
        provenance=Provenance(source="example", method="direct"),
    ))
    subject = engine.record_artifact(Artifact(
        id="example:subject:1",
        kind="example.subject",
        payload={"name": "candidate action"},
        provenance=Provenance(source="example", method="declared"),
    ))

    pack = ContextPack(name="example-pack", version="1")
    pack.register_gate("evidence-present", lambda subject_ref, context: GateResult(
        gate_id="evidence-present",
        passed=bool(context.get("allow")),
        basis_refs=(evidence.id,),
        reason="declared example evidence permits transition" if context.get("allow") else "example gate blocked",
    ))

    decision = engine.evaluate(
        pack=pack,
        subject_ref=subject.id,
        rule_id="example.rule.v1",
        context={"allow": True},
        decision_id="example:decision:1",
    )
    transition = engine.transition_authority(
        transition_id="example:authority:1",
        subject_ref=subject.id,
        current=AuthorityState.REVIEWABLE,
        target=AuthorityState.AUTHORIZED,
        decision_ref=decision.id,
        actor="example-runtime",
    )
    receipt = engine.issue_receipt(Receipt(
        id="example:receipt:1",
        workflow="example.seed",
        input_refs=(evidence.id, subject.id),
        assertion_refs=(),
        decision_refs=(decision.id,),
        output_refs=(transition.id,),
        metadata={"purpose": "minimal reusable seed"},
    ))

    bundle = export_bundle(engine.store, [receipt.id])
    (output / "receipt-bundle.json").write_text(
        json.dumps(bundle, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return bundle


if __name__ == "__main__":
    bundle = build_seed()
    print(bundle["fingerprint"])
