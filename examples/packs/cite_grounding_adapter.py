from __future__ import annotations

from typing import Any, Mapping

from citation_engine import (
    Artifact,
    Assertion,
    Citation,
    CitationEngine,
    CitationRelation,
    EpistemicStatus,
    Provenance,
)


def _evidence_locator(evidence: Mapping[str, Any]) -> str | None:
    page = evidence.get("page") or evidence.get("page_number")
    if page is not None:
        return f"page:{page}"
    return evidence.get("url") or evidence.get("pdf_url") or None


def ingest_grounded_claim(
    engine: CitationEngine,
    grounded: Mapping[str, Any],
    *,
    namespace: str = "cite-fixture",
) -> dict[str, Any]:
    """Map one current Cite `ground_claims_to_papers` item into the neutral core.

    Expected Cite shape (fields may contain more data):

    {
      "claim": str,
      "status": "grounded" | "ungrounded",
      "confidence": float,
      "evidence": [{"paper_id", "title", "score", "excerpt"/"snippet", ...}]
    }

    The adapter is deliberately outside `src/citation_engine`: papers and claim
    grounding are Cite semantics, not engine ontology.
    """

    claim_text = str(grounded.get("claim") or "").strip()
    if not claim_text:
        raise ValueError("grounded claim requires claim text")

    claim_ref = f"{namespace}:claim"
    claim_artifact = engine.record_artifact(
        Artifact(
            id=claim_ref,
            kind="cite.claim_candidate",
            payload={"text": claim_text},
            provenance=Provenance(source="cite-agent", method="claim_grounding"),
        )
    )

    evidence_refs: list[str] = []
    evidence_rows = list(grounded.get("evidence") or [])
    for index, row in enumerate(evidence_rows):
        paper_key = str(row.get("paper_id") or row.get("id") or index)
        evidence_ref = f"{namespace}:evidence:{paper_key}"
        engine.record_artifact(
            Artifact(
                id=evidence_ref,
                kind="cite.paper_evidence",
                payload=dict(row),
                provenance=Provenance(
                    source=str(row.get("source") or row.get("url") or paper_key),
                    method=str(row.get("grounding") or "cite-claim-grounding"),
                    locator=_evidence_locator(row),
                ),
            )
        )
        evidence_refs.append(evidence_ref)

    if not evidence_refs:
        # An ungrounded claim remains a canonical candidate, but is not promoted
        # into a supported Assertion merely because the grounder ran.
        return {
            "claim_ref": claim_artifact.id,
            "assertion_ref": None,
            "citation_refs": (),
            "status": "ungrounded",
        }

    status = (
        EpistemicStatus.SUPPORTED
        if grounded.get("status") == "grounded"
        else EpistemicStatus.HYPOTHESIS
    )
    assertion_ref = f"{namespace}:assertion"
    assertion = engine.record_assertion(
        Assertion(
            id=assertion_ref,
            subject_ref=claim_artifact.id,
            predicate="cite.claim_support",
            value={"grounding_status": grounded.get("status")},
            status=status,
            basis_refs=tuple(evidence_refs),
            confidence=float(grounded.get("confidence") or 0.0),
            produced_by="cite-agent.claim_grounding",
        )
    )

    citation_refs: list[str] = []
    for index, (evidence_ref, row) in enumerate(zip(evidence_refs, evidence_rows)):
        citation = engine.record_citation(
            Citation(
                id=f"{namespace}:citation:{index}",
                subject_ref=assertion.id,
                basis_ref=evidence_ref,
                relation=CitationRelation.SUPPORTS,
                locator=_evidence_locator(row),
                note=str(row.get("excerpt") or row.get("snippet") or "")[:500] or None,
                produced_by="cite-agent.claim_grounding",
            )
        )
        citation_refs.append(citation.id)

    return {
        "claim_ref": claim_artifact.id,
        "assertion_ref": assertion.id,
        "citation_refs": tuple(citation_refs),
        "status": assertion.status.value,
    }
