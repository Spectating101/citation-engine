# Current Status

**Date:** 2026-08-24  
**Stage:** v0.1 extraction seed + six-domain pressure test

## What exists

Citation Engine contains a runnable neutral Python core with:

- canonical `Artifact` objects and semantic digests;
- `Provenance` with parent lineage;
- first-class typed `Citation` edges;
- basis-bound `Assertion` objects;
- explicit epistemic status;
- inspectable `GateResult` records;
- semantic `Decision` identity independent of storage id and later receipt time;
- `record_decision()` for decisions evaluated by domain runtimes;
- operational `AuthorityTransition` separate from epistemic status;
- append-only `RevisionLink` correction/replacement lineage;
- reproducible `Receipt` objects;
- append-only in-memory canonical storage;
- `ContextPack` attachment boundary.

## Validation

The first four-domain package previously passed:

```text
18 passed in 0.08s
```

The Research Drive / Sharpe additions were then reconstructed against the unchanged core and tested separately:

```text
6 passed in 0.04s
```

So the current architecture has **24 validated invariant/adapter tests across the sequential validation runs**. The full repository was not cloned in the second run because the execution runtime could not resolve GitHub DNS; the six new tests were run from the exact GitHub file contents against the unchanged core.

### Neutral invariants

1. semantic artifact digest does not depend on arbitrary address/id;
2. assertion cannot exist without basis;
3. unknown basis cannot enter canonical assertion state;
4. citation subject and basis must resolve;
5. failed gate cannot authorize;
6. decision cannot authorize another subject;
7. correction/replacement preserves the prior object;
8. receipt cannot contain dangling references.

### Cite / Hardware Splicer

9. current Cite claim-grounding output maps to Artifact + Assertion + typed Citation;
10. an ungrounded Cite planning claim is not promoted into a supported assertion;
11. a Hardware Splicer-style measurement gate can authorize when unit/range evidence closes;
12. wrong-unit hardware evidence fails closed and cannot authorize.

### Nocturnal / Policy Lab

13. accepted Nocturnal correction preserves the prior record while adding explicit revision and `CORRECTS` lineage;
14. publishable Nocturnal snapshot advances publication authority only when all declared release gates pass;
15. missing Nocturnal license / rights / pilot approval remains fail-closed;
16. Policy Lab `ADMIT_WITH_LIMIT` can enter canonical state without reimplementing its calculators;
17. Policy Lab receipt metadata may change while semantic decision identity remains stable;
18. Policy Lab `BLOCKED` remains non-authorizing.

### Research Drive / Sharpe Alpha

19. verified archive/custody evidence does **not** imply query readiness;
20. model prose cannot upgrade a failed Drive verification into a verified assertion;
21. Drive query readiness requires both the declared operational state and a resolving path;
22. attractive Sharpe metrics cannot bypass failed promotion evidence;
23. deployable Sharpe promotion remains blocked without an evaluated frozen decision;
24. complete Sharpe promotion evidence can authorize and emit a receipt that preserves frozen-decision lineage.

## Phase 2 result: no new core primitive

Research Drive and Sharpe were chosen to test whether the kernel needed a generic `Readiness` or `Promotion` state.

It does not, at least not yet.

Research Drive already separates neutral inventory from operational activation: metadata-only resources may exist and even have verified custody while remaining non-query-ready. Sharpe similarly separates performance output from provenance/promotion evidence and requires hard gates before live-adjacent promotion.

Both map cleanly as:

```text
artifact / candidate
→ evidence or verification assertion
→ domain gate(s)
→ decision
→ optional authority transition
→ receipt
```

The core did **not** change for Phase 2. `Readiness`, `Promotion`, `Dataset`, `Strategy`, model recommendations, and backtest metrics remain domain semantics.

## Current real adapters

- `examples/packs/cite_grounding_adapter.py`
- `examples/packs/hardware_bench_adapter.py`
- `examples/packs/nocturnal_adapter.py`
- `examples/packs/policy_lab_adapter.py`
- `examples/packs/research_drive_adapter.py`
- `examples/packs/sharpe_promotion_adapter.py`

No Cite, Hardware, Nocturnal, Policy, Drive, Dataset, Sharpe, or Strategy nouns have entered `src/citation_engine/`.

## Architectural conclusion

The lower-level invariant remains:

```text
consequential object
→ cites basis
→ preserves provenance
→ exposes uncertainty
→ passes explicit gates
→ records decision
→ advances authority separately
→ preserves revision/history
→ emits reproducible receipt
```

A successful external computation, transfer, model answer, backtest, publication build, or domain decision is evidence about a specific relationship. It is not automatically truth and it is not automatically authority.

## Next engineering question

The abstraction has now survived six substantially different clients. The next useful work is no longer another domain fixture by default. It should test whether this can become a practical reusable seed:

1. stable serialization/versioned envelopes for core objects;
2. a persistent append-only store behind the current `MemoryStore` interface;
3. import/export of a complete citation graph/receipt bundle;
4. a minimal adapter contract/CLI so a new project can attach without copying example code;
5. conformance tests that every store/adapter implementation must pass.

Only add another neutral primitive if implementation pressure from at least two clients demands it.

## CI limitation

A GitHub Actions workflow is still **not** claimed as installed: the connected GitHub write path previously blocked creation of `.github/workflows/ci.yml`. CI remains a separate repository task.
