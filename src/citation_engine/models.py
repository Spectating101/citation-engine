from __future__ import annotations

from dataclasses import asdict, dataclass, field, is_dataclass
from enum import Enum
from hashlib import sha256
import json
from typing import Any, Mapping


class EpistemicStatus(str, Enum):
    HYPOTHESIS = "hypothesis"
    OBSERVED = "observed"
    SUPPORTED = "supported"
    VERIFIED = "verified"


class AuthorityState(str, Enum):
    BLOCKED = "blocked"
    REVIEWABLE = "reviewable"
    AUTHORIZED = "authorized"


class CitationRelation(str, Enum):
    SUPPORTS = "supports"
    DERIVED_FROM = "derived_from"
    CONSTRAINS = "constrains"
    CONTRADICTS = "contradicts"
    CORRECTS = "corrects"
    AUTHORIZES = "authorizes"
    CONTEXTUALIZES = "contextualizes"


def _canonicalize(value: Any) -> Any:
    if isinstance(value, Enum):
        return value.value
    if is_dataclass(value):
        return _canonicalize(asdict(value))
    if isinstance(value, Mapping):
        return {str(k): _canonicalize(v) for k, v in sorted(value.items(), key=lambda item: str(item[0]))}
    if isinstance(value, (tuple, list)):
        return [_canonicalize(v) for v in value]
    if isinstance(value, set):
        return sorted(_canonicalize(v) for v in value)
    return value


def canonical_hash(value: Any) -> str:
    encoded = json.dumps(
        _canonicalize(value),
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")
    return sha256(encoded).hexdigest()


@dataclass(frozen=True)
class Provenance:
    source: str
    method: str
    locator: str | None = None
    captured_at: str | None = None
    parent_refs: tuple[str, ...] = ()


@dataclass(frozen=True)
class Artifact:
    id: str
    kind: str
    payload: Mapping[str, Any]
    provenance: Provenance

    @property
    def digest(self) -> str:
        # `id` is an address/label. The digest binds the semantic object.
        return canonical_hash({
            "kind": self.kind,
            "payload": self.payload,
            "provenance": self.provenance,
        })


@dataclass(frozen=True)
class Citation:
    """A typed, inspectable edge from a consequential object to its basis."""

    id: str
    subject_ref: str
    basis_ref: str
    relation: CitationRelation
    locator: str | None = None
    note: str | None = None
    produced_by: str | None = None


@dataclass(frozen=True)
class Assertion:
    id: str
    subject_ref: str
    predicate: str
    value: Any
    status: EpistemicStatus
    basis_refs: tuple[str, ...]
    confidence: float | None = None
    produced_by: str | None = None

    def __post_init__(self) -> None:
        if not self.basis_refs:
            raise ValueError("assertions require at least one basis_ref")
        if self.confidence is not None and not 0 <= self.confidence <= 1:
            raise ValueError("confidence must be between 0 and 1")


@dataclass(frozen=True)
class GateResult:
    gate_id: str
    passed: bool
    basis_refs: tuple[str, ...]
    reason: str

    def __post_init__(self) -> None:
        if not self.basis_refs:
            raise ValueError("gate results require inspectable basis_refs")


@dataclass(frozen=True)
class Decision:
    id: str
    subject_ref: str
    outcome: str
    rule_id: str
    gate_results: tuple[GateResult, ...]
    basis_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if not self.gate_results:
            raise ValueError("decisions require at least one gate result")
        if not self.basis_refs:
            raise ValueError("decisions require inspectable basis_refs")

    @property
    def authorized(self) -> bool:
        return all(gate.passed for gate in self.gate_results)


@dataclass(frozen=True)
class AuthorityTransition:
    id: str
    subject_ref: str
    from_state: AuthorityState
    to_state: AuthorityState
    decision_ref: str
    actor: str


@dataclass(frozen=True)
class RevisionLink:
    """Append-only replacement/correction lineage; history is never erased."""

    id: str
    prior_ref: str
    replacement_ref: str
    reason: str
    actor: str | None = None


@dataclass(frozen=True)
class Receipt:
    id: str
    workflow: str
    input_refs: tuple[str, ...]
    assertion_refs: tuple[str, ...]
    decision_refs: tuple[str, ...]
    output_refs: tuple[str, ...]
    citation_refs: tuple[str, ...] = ()
    metadata: Mapping[str, Any] = field(default_factory=dict)

    @property
    def digest(self) -> str:
        return canonical_hash({
            "workflow": self.workflow,
            "input_refs": self.input_refs,
            "assertion_refs": self.assertion_refs,
            "decision_refs": self.decision_refs,
            "output_refs": self.output_refs,
            "citation_refs": self.citation_refs,
            "metadata": self.metadata,
        })
