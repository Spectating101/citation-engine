import json
from copy import deepcopy

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
    JsonlStore,
    MemoryStore,
    Provenance,
    Receipt,
    canonical_hash,
    deserialize_object,
    export_bundle,
    import_bundle,
    serialize_object,
    validate_store,
)


def seeded(store):
    engine = CitationEngine(store)
    source = engine.record_artifact(Artifact(
        id="artifact:source",
        kind="source",
        payload={"value": 7},
        provenance=Provenance(source="fixture", method="observed"),
    ))
    subject = engine.record_artifact(Artifact(
        id="artifact:subject",
        kind="subject",
        payload={"name": "candidate"},
        provenance=Provenance(source="fixture", method="declared"),
    ))
    assertion = engine.record_assertion(Assertion(
        id="assertion:supported",
        subject_ref=subject.id,
        predicate="has_support",
        value=True,
        status=EpistemicStatus.SUPPORTED,
        basis_refs=(source.id,),
        confidence=0.9,
    ))
    citation = engine.record_citation(Citation(
        id="citation:support",
        subject_ref=assertion.id,
        basis_ref=source.id,
        relation=CitationRelation.SUPPORTS,
        locator="fixture:7",
    ))
    pack = ContextPack(name="fixture", version="1")
    pack.register_gate("evidence", lambda subject_ref, context: GateResult(
        gate_id="evidence",
        passed=True,
        basis_refs=(source.id,),
        reason="fixture evidence closes",
    ))
    decision = engine.evaluate(
        pack=pack,
        subject_ref=subject.id,
        rule_id="fixture.rule",
        context={},
        decision_id="decision:allow",
    )
    transition = engine.transition_authority(
        transition_id="authority:allow",
        subject_ref=subject.id,
        current=AuthorityState.REVIEWABLE,
        target=AuthorityState.AUTHORIZED,
        decision_ref=decision.id,
        actor="fixture",
    )
    receipt = engine.issue_receipt(Receipt(
        id="receipt:result",
        workflow="fixture",
        input_refs=(source.id, subject.id),
        assertion_refs=(assertion.id,),
        decision_refs=(decision.id,),
        output_refs=(transition.id,),
        citation_refs=(citation.id,),
        metadata={"run": 1},
    ))
    return engine, receipt


@pytest.mark.parametrize("object_id", [
    "artifact:source",
    "artifact:subject",
    "assertion:supported",
    "citation:support",
    "decision:allow",
    "authority:allow",
    "receipt:result",
])
def test_versioned_object_roundtrip_preserves_semantics(object_id):
    engine, _ = seeded(MemoryStore())
    original = engine.store.get(object_id)
    restored = deserialize_object(serialize_object(original))
    assert restored == original
    if hasattr(original, "digest"):
        assert restored.digest == original.digest


@pytest.mark.parametrize("value", [
    Provenance(
        source="fixture",
        method="direct",
        locator="row:1",
        parent_refs=("artifact:source",),
    ),
    GateResult(
        gate_id="fixture",
        passed=True,
        basis_refs=("artifact:source",),
        reason="passes",
    ),
])
def test_nested_core_values_have_versioned_roundtrip_envelopes(value):
    assert deserialize_object(serialize_object(value)) == value


def test_unknown_object_schema_fails_closed():
    engine, _ = seeded(MemoryStore())
    envelope = serialize_object(engine.store.get("artifact:source"))
    envelope["schema"] = "citation-engine.object.v999"
    with pytest.raises(ValueError, match="unsupported object schema"):
        deserialize_object(envelope)


def test_object_fingerprint_detects_mutation():
    engine, _ = seeded(MemoryStore())
    envelope = serialize_object(engine.store.get("artifact:source"))
    envelope["data"]["payload"]["value"] = 999
    with pytest.raises(ValueError, match="fingerprint mismatch"):
        deserialize_object(envelope)


def test_jsonl_store_reopens_same_objects(tmp_path):
    path = tmp_path / "canonical.jsonl"
    engine, receipt = seeded(JsonlStore(path))
    before = engine.store.get(receipt.id).digest

    reopened = JsonlStore(path)
    assert reopened.get(receipt.id).digest == before
    assert set(reopened.ids()) == set(engine.store.ids())


def test_memory_store_uses_serialized_semantics_for_idempotence():
    store = MemoryStore()
    tuple_form = Artifact(
        id="artifact:nested",
        kind="nested",
        payload={"gates": ({"id": "a", "basis": ("x", "y")},)},
        provenance=Provenance(source="fixture", method="declared"),
    )
    json_form = Artifact(
        id="artifact:nested",
        kind="nested",
        payload={"gates": [{"id": "a", "basis": ["x", "y"]}]},
        provenance=Provenance(source="fixture", method="declared"),
    )
    assert tuple_form != json_form
    assert serialize_object(tuple_form)["fingerprint"] == serialize_object(json_form)["fingerprint"]
    store.put(tuple_form.id, tuple_form)
    store.put(json_form.id, json_form)


def test_jsonl_store_reinsert_accepts_json_normalized_semantic_equivalent(tmp_path):
    path = tmp_path / "canonical.jsonl"
    original = Artifact(
        id="artifact:nested",
        kind="nested",
        payload={"gates": ({"id": "a", "basis": ("x", "y")},)},
        provenance=Provenance(source="fixture", method="declared"),
    )
    store = JsonlStore(path)
    store.put(original.id, original)
    original_line_count = len(path.read_text(encoding="utf-8").splitlines())

    reopened = JsonlStore(path)
    assert reopened.get(original.id) != original  # JSON reload normalizes nested tuples to lists.
    assert reopened.get(original.id).digest == original.digest
    reopened.put(original.id, original)

    assert len(path.read_text(encoding="utf-8").splitlines()) == original_line_count


def test_jsonl_store_still_rejects_changed_nested_semantics(tmp_path):
    path = tmp_path / "canonical.jsonl"
    original = Artifact(
        id="artifact:nested",
        kind="nested",
        payload={"gates": ({"id": "a", "basis": ("x", "y")},)},
        provenance=Provenance(source="fixture", method="declared"),
    )
    JsonlStore(path).put(original.id, original)
    reopened = JsonlStore(path)
    changed = Artifact(
        id=original.id,
        kind=original.kind,
        payload={"gates": ({"id": "a", "basis": ("x", "z")},)},
        provenance=original.provenance,
    )
    with pytest.raises(ValueError, match="silent overwrite"):
        reopened.put(changed.id, changed)


def test_jsonl_store_refuses_silent_overwrite(tmp_path):
    path = tmp_path / "canonical.jsonl"
    engine, _ = seeded(JsonlStore(path))
    conflicting = Artifact(
        id="artifact:source",
        kind="source",
        payload={"value": 999},
        provenance=Provenance(source="fixture", method="observed"),
    )
    with pytest.raises(ValueError, match="silent overwrite"):
        engine.store.put(conflicting.id, conflicting)


def test_jsonl_store_detects_tampered_log(tmp_path):
    path = tmp_path / "canonical.jsonl"
    seeded(JsonlStore(path))
    rows = path.read_text().splitlines()
    first = json.loads(rows[0])
    first["data"]["payload"]["value"] = "tampered"
    rows[0] = json.dumps(first)
    path.write_text("\n".join(rows) + "\n")
    with pytest.raises(ValueError, match="fingerprint mismatch"):
        JsonlStore(path)


def test_receipt_bundle_exports_dependency_closure_and_imports(tmp_path):
    engine, receipt = seeded(MemoryStore())
    bundle = export_bundle(engine.store, [receipt.id])

    exported_ids = {obj["data"]["id"] for obj in bundle["objects"]}
    assert exported_ids == {
        "artifact:source",
        "artifact:subject",
        "assertion:supported",
        "citation:support",
        "decision:allow",
        "authority:allow",
        "receipt:result",
    }

    imported = JsonlStore(tmp_path / "imported.jsonl")
    roots = import_bundle(bundle, imported)
    assert roots == (receipt.id,)
    assert imported.get(receipt.id).digest == receipt.digest


def test_bundle_fingerprint_detects_mutation():
    engine, receipt = seeded(MemoryStore())
    bundle = export_bundle(engine.store, [receipt.id])
    mutated = deepcopy(bundle)
    mutated["roots"] = ["artifact:source"]
    with pytest.raises(ValueError, match="bundle fingerprint mismatch"):
        import_bundle(mutated, MemoryStore())


def test_bundle_rejects_dangling_reference_even_with_recomputed_fingerprint():
    engine, receipt = seeded(MemoryStore())
    bundle = export_bundle(engine.store, [receipt.id])
    bundle["objects"] = [
        obj for obj in bundle["objects"] if obj["data"]["id"] != "artifact:source"
    ]
    bundle["fingerprint"] = canonical_hash({
        "schema": bundle["schema"],
        "roots": bundle["roots"],
        "objects": bundle["objects"],
    })
    with pytest.raises(ValueError, match="dangling references"):
        import_bundle(bundle, MemoryStore())


def test_populated_stores_pass_reusable_conformance(tmp_path):
    memory, _ = seeded(MemoryStore())
    durable, _ = seeded(JsonlStore(tmp_path / "conformance.jsonl"))
    assert validate_store(memory.store)["ok"] is True
    assert validate_store(durable.store)["ok"] is True
