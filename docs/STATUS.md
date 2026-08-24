# Current Status

**Date:** 2026-08-24  
**Stage:** v0.1 extraction seed

## What exists

Citation Engine now contains a runnable neutral Python core with:

- canonical `Artifact` objects and semantic digests;
- `Provenance` with parent lineage;
- first-class typed `Citation` edges;
- basis-bound `Assertion` objects;
- explicit epistemic status;
- inspectable `GateResult` and `Decision` records;
- operational `AuthorityTransition` separate from epistemic status;
- append-only `RevisionLink` correction/replacement lineage;
- reproducible `Receipt` objects;
- append-only in-memory canonical storage;
- `ContextPack` attachment boundary.

## Validation

The exact v0.1 package was reconstructed and tested locally on 2026-08-24:

```text
8 passed in 0.06s
```

Covered invariants:

1. semantic artifact digest does not depend on arbitrary address/id;
2. assertion cannot exist without basis;
3. unknown basis cannot enter canonical assertion state;
4. citation subject and basis must resolve;
5. failed gate cannot authorize;
6. decision cannot authorize another subject;
7. correction/replacement preserves the prior object;
8. receipt cannot contain dangling references.

A GitHub Actions workflow was intentionally **not** claimed as installed: the connected GitHub write path blocked creation of `.github/workflows/ci.yml`. CI remains a separate repository task.

## Portfolio evidence examined

The initial extraction pass inspected current implementation/docs from:

- Cite-Agent;
- Policy Lab / SolarPunk;
- Hardware Splicer;
- Nocturnal Oversight;
- Research Drive / YZU Cluster;
- Sharpe / Sharpe Alpha;
- the older portable Sharpe content-analysis engine as a historical precursor.

The recurring pattern is sufficiently independent across domains to justify extraction. See `EXTRACTION_MAP.md`.

## Architectural conclusion

The common engine is **not** a universal agent or universal research workflow.

The lower-level invariant is:

```text
consequential object
→ cites basis
→ preserves provenance
→ exposes uncertainty
→ passes explicit gates
→ records decision
→ advances authority separately
→ emits reproducible lineage / receipt
```

Domain-specific retrieval, LLM synthesis, policy logic, circuit compilation, public-memory semantics, dataset procurement, and financial backtesting remain context-pack responsibilities.

## Next proof

The next engineering work should not add more abstract features. It should build two thin real fixture packs:

1. Cite claim-grounding fixture;
2. Hardware Splicer evidence/bench-gate fixture.

Those domains are intentionally far apart. If both fit the same engine contract without core special cases, v0.1 graduates from plausible abstraction to demonstrated reusable substrate.
