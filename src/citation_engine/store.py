from __future__ import annotations

from dataclasses import dataclass, field
import json
from pathlib import Path
from typing import Any, Protocol

from .serialization import deserialize_object, object_refs, serialize_object


def _same_canonical_object(left: Any, right: Any) -> bool:
    """Compare canonical objects by their versioned serialized semantics.

    JSON persistence normalizes representational details such as tuples into lists.
    Those shapes are intentionally equivalent under the Citation Engine object
    schema, so append-only idempotence must use the same semantic representation
    rather than raw Python dataclass equality.
    """
    try:
        return serialize_object(left)["fingerprint"] == serialize_object(right)["fingerprint"]
    except (TypeError, ValueError):
        # Canonical stores should contain supported engine objects, but retain a
        # conservative equality fallback for lightweight protocol implementations.
        return left == right


class CanonicalStore(Protocol):
    def put(self, object_id: str, value: Any) -> None: ...
    def get(self, object_id: str) -> Any: ...
    def contains(self, object_id: str) -> bool: ...
    def require(self, *refs: str) -> None: ...
    def ids(self) -> tuple[str, ...]: ...


@dataclass
class MemoryStore:
    """Append-only in-memory canonical object store."""

    objects: dict[str, Any] = field(default_factory=dict)

    def put(self, object_id: str, value: Any) -> None:
        if object_id in self.objects and not _same_canonical_object(self.objects[object_id], value):
            raise ValueError(f"refusing silent overwrite of canonical object: {object_id}")
        self.objects[object_id] = value

    def get(self, object_id: str) -> Any:
        return self.objects[object_id]

    def contains(self, object_id: str) -> bool:
        return object_id in self.objects

    def require(self, *refs: str) -> None:
        missing = [ref for ref in refs if not self.contains(ref)]
        if missing:
            raise ValueError(f"unknown canonical refs: {missing}")

    def ids(self) -> tuple[str, ...]:
        return tuple(self.objects)


class JsonlStore:
    """Append-only durable store using one versioned canonical-object envelope per line.

    The file is an interchange log, not a second object model. On open, every
    envelope fingerprint is verified and the complete loaded graph is checked for
    dangling references before the store is accepted.
    """

    def __init__(self, path: str | Path):
        self.path = Path(path)
        self.objects: dict[str, Any] = {}
        self._load()

    def _load(self) -> None:
        if not self.path.exists():
            return
        lines = self.path.read_text(encoding="utf-8").splitlines()
        for line_no, line in enumerate(lines, start=1):
            if not line.strip():
                continue
            try:
                envelope = json.loads(line)
                value = deserialize_object(envelope)
            except Exception as exc:
                raise ValueError(f"invalid canonical store line {line_no}: {exc}") from exc
            object_id = str(getattr(value, "id", "") or "")
            if not object_id:
                raise ValueError(f"invalid canonical store line {line_no}: object has no id")
            if object_id in self.objects and not _same_canonical_object(self.objects[object_id], value):
                raise ValueError(f"conflicting duplicate canonical object in store: {object_id}")
            self.objects[object_id] = value
        self.validate_references()

    def validate_references(self) -> None:
        known = set(self.objects)
        dangling = {
            object_id: [ref for ref in object_refs(value) if ref not in known]
            for object_id, value in self.objects.items()
        }
        dangling = {key: refs for key, refs in dangling.items() if refs}
        if dangling:
            raise ValueError(f"canonical store has dangling references: {dangling}")

    def put(self, object_id: str, value: Any) -> None:
        actual_id = str(getattr(value, "id", "") or "")
        if actual_id != object_id:
            raise ValueError(f"object id mismatch: key={object_id}, value.id={actual_id}")
        if object_id in self.objects:
            if not _same_canonical_object(self.objects[object_id], value):
                raise ValueError(f"refusing silent overwrite of canonical object: {object_id}")
            return

        missing = [ref for ref in object_refs(value) if ref not in self.objects]
        if missing:
            raise ValueError(f"cannot persist object with unknown canonical refs: {missing}")

        self.path.parent.mkdir(parents=True, exist_ok=True)
        line = json.dumps(
            serialize_object(value),
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
        )
        with self.path.open("a", encoding="utf-8") as handle:
            handle.write(line + "\n")
        self.objects[object_id] = value

    def get(self, object_id: str) -> Any:
        return self.objects[object_id]

    def contains(self, object_id: str) -> bool:
        return object_id in self.objects

    def require(self, *refs: str) -> None:
        missing = [ref for ref in refs if not self.contains(ref)]
        if missing:
            raise ValueError(f"unknown canonical refs: {missing}")

    def ids(self) -> tuple[str, ...]:
        return tuple(self.objects)
