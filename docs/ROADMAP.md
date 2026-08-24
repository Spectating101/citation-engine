# Roadmap

Citation Engine should grow by **extraction pressure**, not by speculative framework design.

## Phase 0 — seed the invariant

Status: **current**

- [x] canonical artifacts and deterministic semantic digest
- [x] provenance / parent lineage
- [x] first-class typed citation edges
- [x] basis-bound assertions
- [x] explicit epistemic status
- [x] deterministic gate results and decisions
- [x] authority transitions
- [x] append-only revision links
- [x] receipts
- [x] context-pack boundary
- [x] initial cross-project extraction map
- [ ] CI green on the repository itself

Exit condition: the core can express the recurring trust mechanics without importing a domain noun.

## Phase 1 — prove the abstraction against real clients

Do **not** migrate whole products.

Build thin adapters for two maximally different systems first:

1. **Cite** — scholarly claim → exact basis → claim boundary / verification.
2. **Hardware Splicer** — measurement/contract → gate → operational authorization.

Why these two: if the same core survives both research claims and physical power-on authority without special-casing either, the abstraction has real breadth.

Required work:

- [ ] define a stable pack manifest shape;
- [ ] implement one Cite fixture pack using existing claim-grounding output;
- [ ] implement one Hardware fixture pack using existing bench/evidence output;
- [ ] prove identical core APIs serve both;
- [ ] add conformance vectors for citation, promotion, and authority invariants.

Exit condition: no engine changes are needed merely because the second client is a different domain.

## Phase 2 — history, challenge, and release semantics

Pressure-test with Nocturnal and Policy Lab.

- [ ] correction/dispute lifecycle over `RevisionLink`;
- [ ] explicit superseded/stale obligations;
- [ ] portable receipt schema;
- [ ] deterministic identity/version compatibility rules;
- [ ] separate evaluation validity from actor authority;
- [ ] release/publication gate pattern;
- [ ] replay / reproducibility contract.

Exit condition: a prior decision can be challenged or superseded without erasing the basis on which it was originally made.

## Phase 3 — evidence estate and promotion mechanics

Pressure-test with Research Drive and Sharpe Alpha.

- [ ] independent provenance / verification / readiness projections;
- [ ] candidate → reviewed → promoted state pattern;
- [ ] manifest + decision-log adapters;
- [ ] structured gaps / unresolved requirements;
- [ ] derived-artifact multi-parent lineage.

Exit condition: the engine can support durable evidence estates and promotion pipelines without inventing a universal domain score.

## Phase 4 — protocol surfaces

Only after the object model survives the client tests:

- [ ] JSON schemas for portable core objects;
- [ ] serialization/versioning contract;
- [ ] Python API stabilization;
- [ ] CLI inspection/replay tools;
- [ ] optional MCP server exposing engine inspection operations;
- [ ] optional HTTP service;
- [ ] persistent store adapter.

MCP remains a protocol surface, not canonical truth semantics.

## Phase 5 — seed-template use

Prove the original portfolio goal: new projects should start from Citation Engine rather than re-inventing trust mechanics.

A new domain should require mainly:

```text
schemas
+ adapters/tools
+ rules/gates
+ workflows
+ renderers
```

and should inherit:

```text
canonical refs
+ citations
+ lineage
+ promotion discipline
+ authority discipline
+ receipts
```

## Stop rules

Do not add a feature merely because one existing project has it.

Do not add:

- a generic agent planner because Cite has an agent;
- a generic ledger because Nocturnal has one;
- a generic policy DSL because Policy Lab has rules;
- a generic hardware state model because Hardware Splicer has contracts;
- a generic research ontology because Research Drive/Cite have one;
- a generic scoring model because several products display confidence/status.

Extract mechanics only after repeated independent evidence.
