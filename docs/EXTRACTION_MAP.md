# Portfolio Extraction Map

This file records **why** Citation Engine exists and prevents the core from becoming an abstraction invented in isolation.

Existing projects are specimens, clients, and adversarial validation cases. They are not dependencies.

## Extraction rule

A primitive belongs in Citation Engine only if:

1. it appears independently in at least two systems;
2. its semantics can be expressed without a domain noun;
3. extracting it reduces duplicated trust/verification mechanics;
4. domain systems can still define their own policy without forking the core.

## Current map

| System | Existing domain implementation | Neutral mechanic extracted |
|---|---|---|
| **Cite-Agent** | claim grounding, exact evidence spans, paper Audit, deterministic vs model-assisted findings, explicit “supports / do not claim yet / next checks” boundaries | `Assertion`, typed `Citation`, locator-bearing support, epistemic status, explicit non-promotion, downstream obligations |
| **Policy Lab / SolarPunk** | evidence envelopes, provenance decisions, policy manifests/hashes, admission and quantity rules, settlement constraints, deterministic decision results and receipts | canonical artifact identity, rule/gate separation, basis-bound decision, versioned policy context, receipt, distinction between structural validity and decision validity |
| **Hardware Splicer** | donor evidence graph, unresolved interface fields, bench gates, firmware/power-on authorization, external compilers/projection backends | unresolved evidence state, gate closure, `AuthorityTransition`, tool/authority separation, canonical state vs projections |
| **Nocturnal** | evidence grades, strict hash/chain verification, no silent identity merges, append-only corrections/disputes, deterministic public filtering, separate public/intake/operator authority | canonical identity, lineage, `RevisionLink`, fail-closed gates, scoped authority, release receipts/manifests |
| **Research Drive / YZU Cluster** | durable evidence estate, source vs verification vs readiness as independent axes, source chains/citations, model cannot silently upgrade verification, backend durable consequence | Artifact registry, independent status dimensions, typed citation/provenance edges, explicit promotion authority, durable consequence |
| **Sharpe / Sharpe Alpha** | older content-agnostic synthesis engine with citation/provenance; newer candidate manifest gates checking provenance and promotion evidence | prior portability attempt, multi-source citation lineage, promotion gates, decision log/manifest boundary |

## Important source observations

### Cite-Agent

Relevant surfaces include:

- `cite_agent/claim_grounding.py` — evidence links and confidence exist so downstream output can explain **why a claim is believable**;
- `docs/LIBRARY_AUDIT_DIRECTION.md` — claims, exact locations, supporting evidence, deterministic/model-assisted distinction, and human-review obligations;
- `web/src/lib/empiricalClaimBoundary.ts` — explicitly separates what current evidence supports from what must not yet be claimed.

**Extraction:** citation is not merely bibliographic identity. It is the trace from an assertion to the exact basis and the boundary of what that basis permits.

### Policy Lab

Relevant surfaces include:

- `protocol/schema/README.md` — portable evidence/provenance/policy/claim/decision/receipt schemas;
- `docs/protocol/THREAT_MODEL_ALPHA.md` — evidence identity, policy identity, quantity bounds, state integrity, and boundary honesty;
- `docs/research/FINAL_RESEARCH_POLICY_LAB_RECONCILIATION.md` — implementation stages are kept distinct from research boundaries and stronger claims do not cascade automatically.

Policy Lab explicitly notes that schema validity does not equal financial/decision validity and that a deterministic decision result is not legal issuance authority.

**Extraction:** canonical identity, syntax validity, evidence quality, decision validity, and operational authority are separate layers.

### Hardware Splicer

`docs/INTEGRATION_STACK.md` establishes a particularly clean boundary:

```text
Hardware Splicer owns evidence + authority semantics.
External tools own execution details.
External tools never promote a hypothesis into an authoritative fact.
```

Firmware generation and physical power-on are separate authority transitions, and familiar hardware analogies cannot silently inherit electrical contracts.

**Extraction:** successful computation/projection is not truth and is not authorization.

### Nocturnal

The canonical runtime independently implements:

- strict hash and chain verification;
- ambiguity-aware identities and no silent same-name merges;
- append-only corrections and disputes;
- deterministic fail-closed publication controls;
- isolated intake with no mutation authority;
- portable release snapshots with manifests and hashes.

**Extraction:** history must survive correction; public visibility is an authority decision rather than a side effect of ingestion.

### Research Drive

`docs/UI_PRODUCT_AUTHORITY.md` repeatedly separates:

```text
EVIDENCE = what is this?
SOURCE   = where did it come from?
VERIFY   = what relationship to authoritative/sourcable evidence is established?
STATE    = can the system use it now?
```

It explicitly enforces:

```text
Verified ≠ data is true
Matched ≠ identical
Query-ready ≠ externally verified
Self-provided ≠ unusable
```

and forbids model prose from upgrading verification/source authority.

**Extraction:** provenance, verification, readiness, and usability must not be collapsed into one confidence score.

### Sharpe: the useful precursor

The older `sharpe/engine` already attempted a portable content-analysis engine: multi-source synthesis, citation tracking, provenance, LLM routing, and adaptable content types.

That precursor is valuable but sits **too high in the stack** for the present goal. It generalizes synthesis/orchestration; Citation Engine generalizes the trust substrate beneath synthesis.

The newer `sharpe-alpha/alpha/scripts/manifest_gates.py` checks candidate manifests for **provenance and promotion evidence**, independently rediscovering the same promotion-gate pattern.

**Extraction:** LLM consensus/synthesis should become a context-pack capability; provenance and promotion mechanics belong below it.

## Candidate primitives and evidence count

| Primitive | Independent systems supporting extraction |
|---|---|
| canonical artifact / stable identity | Policy Lab, Nocturnal, Research Drive, Hardware Splicer |
| provenance / parent lineage | all major systems above |
| typed citation / basis edge | Cite, Policy Lab, Nocturnal, Research Drive, Sharpe |
| assertion with explicit epistemic posture | Cite, Policy Lab, Hardware Splicer, Nocturnal |
| deterministic/bounded gate | Policy Lab, Hardware Splicer, Nocturnal, Sharpe Alpha |
| authority transition | Hardware Splicer, Nocturnal, Policy Lab, Research Drive |
| append-only revision/correction | Nocturnal, Policy Lab versioning, Research Drive durable history, Cite downstream stale obligations |
| receipt / reproducibility artifact | Policy Lab, Hardware Splicer, Nocturnal; implicit in research workflows |
| context/capability pack boundary | Cite MCP, Hardware Splicer backends, Nocturnal integrations, Research Drive/Cite intelligence, older Sharpe engine |

## What is intentionally **not** extracted yet

The following are common features but not yet proven neutral mechanics at the required level:

- generic LLM planner/agent loop;
- generic vector search;
- generic scoring/confidence aggregation;
- generic identity resolution;
- generic workflow DSL;
- one shared database;
- one UI shell;
- one universal evidence-quality taxonomy.

These remain domain/client responsibilities until repeated implementations prove a genuinely common contract.

## Client test

The abstraction is healthy only if each project can attach without leaking its nouns into core:

```text
Cite Pack        → papers, claims, statistical checks, scholarly records
Policy Pack      → evidence envelopes, policy manifests, settlement rules
Nocturnal Pack   → matters, identities, correction/publication rules
Hardware Pack    → donor interfaces, measurements, bench/power gates
Research Pack    → dataset assets, source/verification/readiness rules
Sharpe Pack      → candidate manifests, backtests, promotion gates
```

If the core ever needs `Paper`, `Circuit`, `Matter`, `Policy`, `Dataset`, or `Security`, stop and move that concept back into its pack.
