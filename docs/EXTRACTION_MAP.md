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
| **Refinery Commons** | semantic Capability/Implementation split, exact-subject SLSA/SPDX/OCI evidence, append-only positive/negative claims, explicit curation boundary, software + institutional generalization | exact-subject anti-laundering invariant, semantic-vs-realization identity pressure test, claim/basis separation, recommendation as authority rather than maturity |

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

### Refinery Commons: exact subject before global conclusion

The current Commons line separates a semantic capability contract from one or more concrete realizations. It then attaches evaluation, provenance, rights, security, demand, deployment, usage, stewardship, and curation evidence to exact subjects rather than a vague project container.

The strongest adverse finding is `MEV0-001`: early SLSA/SPDX attachment at project scope could launder one release's evidence onto sibling implementations. The repair requires explicit subject binding and can require exact SHA-256 agreement. A verified OCI artifact therefore does not verify a sibling Git realization.

The same Commons grammar also survived a real institutional coral-restoration / conservation-finance case without requiring a new canonical institutional object, while preserving activity/effectiveness and program-existence/current-availability boundaries.

**Extraction:** evidence scope is part of epistemic correctness. Evidence attached to subject X must not silently confer verification or authority on related subject Y.

A second useful pressure test is semantic identity versus concrete realization identity. Citation Engine can currently represent both as domain Artifacts, but the structural `realizes` relationship is not itself an evidentiary citation. The current adapter therefore uses provenance parent closure only as a bounded integration technique; it does **not** justify a new core relation primitive yet.

See `docs/REFINERY_INTEGRATION.md` and `examples/packs/refinery_commons_adapter.py`.

## Candidate primitives and evidence count

| Primitive | Independent systems supporting extraction |
|---|---|
| canonical artifact / stable identity | Policy Lab, Nocturnal, Research Drive, Hardware Splicer, Refinery |
| provenance / parent lineage | all major systems above, including Refinery machine evidence |
| typed citation / basis edge | Cite, Policy Lab, Nocturnal, Research Drive, Sharpe, Refinery adapter |
| assertion with explicit epistemic posture | Cite, Policy Lab, Hardware Splicer, Nocturnal, Refinery claims |
| deterministic/bounded gate | Policy Lab, Hardware Splicer, Nocturnal, Sharpe Alpha, Refinery curation/admission |
| authority transition | Hardware Splicer, Nocturnal, Policy Lab, Research Drive; Refinery recommendation maps cleanly onto it |
| append-only revision/correction | Nocturnal, Policy Lab versioning, Research Drive durable history, Cite downstream stale obligations, Refinery positive/negative coexistence |
| receipt / reproducibility artifact | Policy Lab, Hardware Splicer, Nocturnal; implicit in research workflows; Refinery review bundles map cleanly |
| context/capability pack boundary | Cite MCP, Hardware Splicer backends, Nocturnal integrations, Research Drive/Cite intelligence, older Sharpe engine, Refinery Commons adapter |

## What is intentionally **not** extracted yet

The following are common features but not yet proven neutral mechanics at the required level:

- generic LLM planner/agent loop;
- generic vector search;
- generic scoring/confidence aggregation;
- generic identity resolution;
- generic structural `Relation` graph / semantic-realization ontology;
- generic workflow DSL;
- one shared database;
- one UI shell;
- one universal evidence-quality taxonomy.

The Refinery integration specifically does **not** promote `Capability`, `Implementation`, evidence maturity, recommendation, SLSA, SPDX, OCI, or institutional concepts into the kernel. A generic structural relation should only be added after the existing representation fails in at least one additional domain with the same noun-free need.

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
Refinery Pack    → capability contracts, realizations, exact-subject evidence, curation gates
```

If the core ever needs `Paper`, `Circuit`, `Matter`, `Policy`, `Dataset`, `Security`, `Capability`, or `Implementation`, stop and move that concept back into its pack.
