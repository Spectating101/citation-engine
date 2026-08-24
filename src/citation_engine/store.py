from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class MemoryStore:
    """Replaceable canonical object store for early engine work.

    Canonical ids are append-only: an id may be re-put only with an equal value.
    Corrections and replacements use new objects plus explicit RevisionLink edges.
    """

    objects: dict[str, Any] = field(default_factory=dict)

    def put(self, object_id: str, value: Any) -> None:
        if object_id in self.objects and self.objects[object_id] != value:
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
