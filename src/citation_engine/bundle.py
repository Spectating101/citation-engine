from __future__ import annotations

from typing import Any, Mapping, Sequence

from .models import canonical_hash
from .serialization import deserialize_object, object_refs, serialize_object
from .store import CanonicalStore

BUNDLE_SCHEMA = "citation-engine.bundle.v1"


def _closure(store: CanonicalStore, roots: Sequence[str]) -> tuple[str, ...]:
    pending = list(dict.fromkeys(str(root) for root in roots))
    seen: set[str] = set()
    while pending:
        ref = pending.pop()
        if ref in seen:
            continue
        if not store.contains(ref):
            raise ValueError(f"unknown bundle root/reference: {ref}")
        seen.add(ref)
        pending.extend(dep for dep in object_refs(store.get(ref)) if dep not in seen)
    return tuple(sorted(seen))


def export_bundle(store: CanonicalStore, roots: Sequence[str]) -> dict[str, Any]:
    root_refs = tuple(dict.fromkeys(str(root) for root in roots))
    if not root_refs:
        raise ValueError("bundle requires at least one root")
    object_ids = _closure(store, root_refs)
    objects = [serialize_object(store.get(object_id)) for object_id in object_ids]
    manifest = {
        "schema": BUNDLE_SCHEMA,
        "roots": list(root_refs),
        "objects": objects,
    }
    manifest["fingerprint"] = canonical_hash(manifest)
    return manifest


def _verify_bundle(bundle: Mapping[str, Any]) -> None:
    schema = str(bundle.get("schema") or "")
    if schema != BUNDLE_SCHEMA:
        raise ValueError(f"unsupported bundle schema: {schema or '<missing>'}")
    fingerprint = str(bundle.get("fingerprint") or "")
    if not fingerprint:
        raise ValueError("bundle missing fingerprint")
    material = {
        "schema": bundle.get("schema"),
        "roots": bundle.get("roots"),
        "objects": bundle.get("objects"),
    }
    if canonical_hash(material) != fingerprint:
        raise ValueError("bundle fingerprint mismatch")


def import_bundle(bundle: Mapping[str, Any], store: CanonicalStore) -> tuple[str, ...]:
    _verify_bundle(bundle)

    raw_objects = bundle.get("objects")
    if not isinstance(raw_objects, list):
        raise ValueError("bundle objects must be a list")

    decoded: dict[str, Any] = {}
    for envelope in raw_objects:
        if not isinstance(envelope, Mapping):
            raise ValueError("bundle object envelope must be a mapping")
        value = deserialize_object(envelope)
        object_id = str(getattr(value, "id", "") or "")
        if not object_id:
            raise ValueError("bundle object has no id")
        if object_id in decoded and decoded[object_id] != value:
            raise ValueError(f"bundle contains conflicting object id: {object_id}")
        decoded[object_id] = value

    roots = tuple(str(root) for root in bundle.get("roots") or ())
    if not roots:
        raise ValueError("bundle requires at least one root")

    available = set(decoded) | set(store.ids())
    missing_roots = [root for root in roots if root not in available]
    if missing_roots:
        raise ValueError(f"bundle roots are missing: {missing_roots}")

    dangling = {
        object_id: [ref for ref in object_refs(value) if ref not in available]
        for object_id, value in decoded.items()
    }
    dangling = {key: refs for key, refs in dangling.items() if refs}
    if dangling:
        raise ValueError(f"bundle has dangling references: {dangling}")

    pending = dict(decoded)
    while pending:
        progressed = False
        for object_id, value in list(pending.items()):
            refs = object_refs(value)
            if all(store.contains(ref) for ref in refs):
                store.put(object_id, value)
                del pending[object_id]
                progressed = True
        if not progressed:
            raise ValueError(f"bundle contains cyclic or unresolvable references: {sorted(pending)}")

    return roots
