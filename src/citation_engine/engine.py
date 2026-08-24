from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping

from .context import ContextPack
from .models import (
    Artifact,
    Assertion,
    AuthorityState,
    AuthorityTransition,
    Citation,
    Decision,
    Receipt,
    RevisionLink,
)
from .store import MemoryStore


@dataclass
class CitationEngine:
    store: MemoryStore

    def record_artifact(self, artifact: Artifact) -> Artifact:
        self.store.require(*artifact.provenance.parent_refs)
        self.store.put(artifact.id, artifact)
        return artifact

    def record_citation(self, citation: Citation) -> Citation:
        self.store.require(citation.subject_ref, citation.basis_ref)
        self.store.put(citation.id, citation)
        return citation

    def record_assertion(self, assertion: Assertion) -> Assertion:
        self.store.require(assertion.subject_ref, *assertion.basis_refs)
        self.store.put(assertion.id, assertion)
        return assertion

    def evaluate(
        self,
        *,
        pack: ContextPack,
        subject_ref: str,
        rule_id: str,
        context: Mapping[str, Any],
        decision_id: str,
    ) -> Decision:
        self.store.require(subject_ref)
        if not pack.gates:
            raise ValueError("a decision requires at least one registered gate")

        gate_results = tuple(
            evaluator(subject_ref, context)
            for _, evaluator in sorted(pack.gates.items())
        )
        basis_refs = tuple(dict.fromkeys(
            ref for result in gate_results for ref in result.basis_refs
        ))
        self.store.require(*basis_refs)

        decision = Decision(
            id=decision_id,
            subject_ref=subject_ref,
            outcome="authorized" if all(gate.passed for gate in gate_results) else "blocked",
            rule_id=rule_id,
            gate_results=gate_results,
            basis_refs=basis_refs,
        )
        self.store.put(decision.id, decision)
        return decision

    def transition_authority(
        self,
        *,
        transition_id: str,
        subject_ref: str,
        current: AuthorityState,
        target: AuthorityState,
        decision_ref: str,
        actor: str,
    ) -> AuthorityTransition:
        self.store.require(subject_ref, decision_ref)
        decision = self.store.get(decision_ref)
        if not isinstance(decision, Decision):
            raise TypeError("decision_ref must resolve to a Decision")
        if decision.subject_ref != subject_ref:
            raise ValueError("decision cannot authorize a different subject")
        if target == AuthorityState.AUTHORIZED and not decision.authorized:
            raise ValueError("cannot authorize subject from a failed decision")

        transition = AuthorityTransition(
            id=transition_id,
            subject_ref=subject_ref,
            from_state=current,
            to_state=target,
            decision_ref=decision_ref,
            actor=actor,
        )
        self.store.put(transition.id, transition)
        return transition

    def record_revision(self, revision: RevisionLink) -> RevisionLink:
        if revision.prior_ref == revision.replacement_ref:
            raise ValueError("revision must point to a distinct replacement object")
        self.store.require(revision.prior_ref, revision.replacement_ref)
        self.store.put(revision.id, revision)
        return revision

    def issue_receipt(self, receipt: Receipt) -> Receipt:
        refs = (
            receipt.input_refs
            + receipt.assertion_refs
            + receipt.decision_refs
            + receipt.output_refs
            + receipt.citation_refs
        )
        self.store.require(*refs)
        self.store.put(receipt.id, receipt)
        return receipt
