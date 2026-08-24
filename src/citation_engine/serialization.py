from __future__ import annotations

from dataclasses import asdict
from enum import Enum
from typing import Any, Mapping

from .models import (
    Artifact,
    Assertion,
    AuthorityState,
    AuthorityTransition,
    Citation,
    CitationRelation,
    Decision,
    EpistemicStatus,
    GateResult,
    Provenance,
    Receipt,
    RevisionLink,
    canonical_hash,
)

OBJECT_SCHEMA = "citation-engine.object.v1"
SUPPORTED_TYPES = {
    "Artifact",
    "Assertion",
    "AuthorityTransition",
    "Citation",
    "Decision",
    "GateResult",
    "Provenance",
    "Receipt",
    "RevisionLink",
}


def _plain(value: Any) -> Any:
    if isinstance(value, Enum):
        return value.value
    if hasattr(value, "__dataclass_fields__"):
        return _plain(asdict(value))
    if isinstance(value, tuple):
        return [_plain(item) for item in value]
    if isinstance(value, list):
        return [_plain(item) for item in value]
    if isinstance(value, Mapping):
        return {str(key): _plain(item) for key, item in value.items()}
    return value


def object_type(value: Any) -> str:
    name = type(value).__name__
    if name not in SUPPORTED_TYPES:
        raise TypeError(f"unsupported canonical object type: {name}")
    return name


def object_refs(value: Any) -> tuple[str, ...]:
    """Return canonical refs this object or serialized value depends on."""
    if isinstance(value, Provenance):
        refs = value.parent_refs
    elif isinstance(value, GateResult):
        refs = value.basis_refs
    elif isinstance(value, Artifact):
        refs = value.provenance.parent_refs
    elif isinstance(value, Citation):
        refs = (value.subject_ref, value.basis_ref)
    elif isinstance(value, Assertion):
        refs = (value.subject_ref, *value.basis_refs)
    elif isinstance(value, Decision):
        refs = (
            value.subject_ref,
            *value.basis_refs,
            *(ref for gate in value.gate_results for ref in gate.basis_refs),
        )
    elif isinstance(value, AuthorityTransition):
        refs = (value.subject_ref, value.decision_ref)
    elif isinstance(value, RevisionLink):
        refs = (value.prior_ref, value.replacement_ref)
    elif isinstance(value, Receipt):
        refs = (
            *value.input_refs,
            *value.assertion_refs,
            *value.decision_refs,
            *value.output_refs,
            *value.citation_refs,
        )
    else:
        raise TypeError(f"unsupported canonical object type: {type(value).__name__}")
    return tuple(dict.fromkeys(refs))


def serialize_object(value: Any) -> dict[str, Any]:
    type_name = object_type(value)
    data = _plain(value)
    envelope = {
        "schema": OBJECT_SCHEMA,
        "type": type_name,
        "data": data,
    }
    envelope["fingerprint"] = canonical_hash(envelope)
    return envelope


def _expect_schema(envelope: Mapping[str, Any]) -> None:
    schema = str(envelope.get("schema") or "")
    if schema != OBJECT_SCHEMA:
        raise ValueError(f"unsupported object schema: {schema or '<missing>'}")


def _verify_fingerprint(envelope: Mapping[str, Any]) -> None:
    expected = str(envelope.get("fingerprint") or "")
    if not expected:
        raise ValueError("serialized object missing fingerprint")
    material = {
        "schema": envelope.get("schema"),
        "type": envelope.get("type"),
        "data": envelope.get("data"),
    }
    actual = canonical_hash(material)
    if actual != expected:
        raise ValueError("serialized object fingerprint mismatch")


def deserialize_object(envelope: Mapping[str, Any]) -> Any:
    _expect_schema(envelope)
    _verify_fingerprint(envelope)

    type_name = str(envelope.get("type") or "")
    if type_name not in SUPPORTED_TYPES:
        raise ValueError(f"unsupported object type: {type_name or '<missing>'}")
    data = envelope.get("data")
    if not isinstance(data, Mapping):
        raise ValueError("serialized object data must be a mapping")

    if type_name == "Provenance":
        return Provenance(
            source=str(data.get("source") or ""),
            method=str(data.get("method") or ""),
            locator=data.get("locator"),
            captured_at=data.get("captured_at"),
            parent_refs=tuple(data.get("parent_refs") or ()),
        )

    if type_name == "GateResult":
        return GateResult(
            gate_id=str(data["gate_id"]),
            passed=bool(data["passed"]),
            basis_refs=tuple(data.get("basis_refs") or ()),
            reason=str(data.get("reason") or ""),
        )

    if type_name == "Artifact":
        provenance_data = data.get("provenance") or {}
        provenance = Provenance(
            source=str(provenance_data.get("source") or ""),
            method=str(provenance_data.get("method") or ""),
            locator=provenance_data.get("locator"),
            captured_at=provenance_data.get("captured_at"),
            parent_refs=tuple(provenance_data.get("parent_refs") or ()),
        )
        return Artifact(
            id=str(data["id"]),
            kind=str(data["kind"]),
            payload=dict(data.get("payload") or {}),
            provenance=provenance,
        )

    if type_name == "Citation":
        return Citation(
            id=str(data["id"]),
            subject_ref=str(data["subject_ref"]),
            basis_ref=str(data["basis_ref"]),
            relation=CitationRelation(str(data["relation"])),
            locator=data.get("locator"),
            note=data.get("note"),
            produced_by=data.get("produced_by"),
        )

    if type_name == "Assertion":
        return Assertion(
            id=str(data["id"]),
            subject_ref=str(data["subject_ref"]),
            predicate=str(data["predicate"]),
            value=data.get("value"),
            status=EpistemicStatus(str(data["status"])),
            basis_refs=tuple(data.get("basis_refs") or ()),
            confidence=data.get("confidence"),
            produced_by=data.get("produced_by"),
        )

    if type_name == "Decision":
        gates = tuple(
            GateResult(
                gate_id=str(gate["gate_id"]),
                passed=bool(gate["passed"]),
                basis_refs=tuple(gate.get("basis_refs") or ()),
                reason=str(gate.get("reason") or ""),
            )
            for gate in data.get("gate_results") or ()
        )
        return Decision(
            id=str(data["id"]),
            subject_ref=str(data["subject_ref"]),
            outcome=str(data["outcome"]),
            rule_id=str(data["rule_id"]),
            gate_results=gates,
            basis_refs=tuple(data.get("basis_refs") or ()),
        )

    if type_name == "AuthorityTransition":
        return AuthorityTransition(
            id=str(data["id"]),
            subject_ref=str(data["subject_ref"]),
            from_state=AuthorityState(str(data["from_state"])),
            to_state=AuthorityState(str(data["to_state"])),
            decision_ref=str(data["decision_ref"]),
            actor=str(data["actor"]),
        )

    if type_name == "RevisionLink":
        return RevisionLink(
            id=str(data["id"]),
            prior_ref=str(data["prior_ref"]),
            replacement_ref=str(data["replacement_ref"]),
            reason=str(data["reason"]),
            actor=data.get("actor"),
        )

    if type_name == "Receipt":
        return Receipt(
            id=str(data["id"]),
            workflow=str(data["workflow"]),
            input_refs=tuple(data.get("input_refs") or ()),
            assertion_refs=tuple(data.get("assertion_refs") or ()),
            decision_refs=tuple(data.get("decision_refs") or ()),
            output_refs=tuple(data.get("output_refs") or ()),
            citation_refs=tuple(data.get("citation_refs") or ()),
            metadata=dict(data.get("metadata") or {}),
        )

    raise AssertionError("unreachable")
