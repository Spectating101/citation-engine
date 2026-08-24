from __future__ import annotations

from typing import Any

from .serialization import deserialize_object, object_refs, serialize_object
from .store import CanonicalStore


def validate_store(store: CanonicalStore) -> dict[str, Any]:
    """Validate a populated store against Citation Engine's canonical contract.

    Third-party store implementations can call this in their own test suites.
    """
    ids = tuple(store.ids())
    known = set(ids)
    roundtrip_failures: list[str] = []
    dangling: dict[str, list[str]] = {}

    for object_id in ids:
        value = store.get(object_id)
        if str(getattr(value, "id", "") or "") != object_id:
            raise ValueError(f"store key/object id mismatch: {object_id}")
        restored = deserialize_object(serialize_object(value))
        if restored != value:
            roundtrip_failures.append(object_id)
        missing = [ref for ref in object_refs(value) if ref not in known]
        if missing:
            dangling[object_id] = missing

    if roundtrip_failures:
        raise ValueError(f"store objects fail canonical roundtrip: {roundtrip_failures}")
    if dangling:
        raise ValueError(f"store has dangling canonical references: {dangling}")

    return {
        "ok": True,
        "objects": len(ids),
        "ids": ids,
    }
