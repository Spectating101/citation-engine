# Current Status

**Date:** 2026-08-24  
**Stage:** v0.1 extraction seed + first cross-domain proof

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

The exact current package was reconstructed and tested locally on 2026-08-24:

```text
12 passed in 0.04s
```

The original eight neutral invariants cover:

1. semantic artifact digest does not depend on arbitrary address/id;
2. assertion cannot exist without basis;
3. unknown basis cannot enter canonical assertion state;
4. citation subject and basis must resolve;
5. failed gate cannot authorize;
6. decision cannot authorize another subject;
7. correction/replacement preserves the prior object;
8. receipt cannot contain dangling references.

Four additional tests now exercise two real portfolio-shaped adapters:

9. current Cite claim-grounding output maps to Artifact + Assertion + typed Citation;
10. an ungrounded Cite planning claim is not promoted into a supported assertion;
11. a Hardware Splicer-style measurement gate can authorize when unit/range evidence closes;
12. wrong-unit hardware evidence fails closed and cannot authorize.

**No core changes were required to move from the Cite fixture to the Hardware fixture.** This is the first concrete evidence that the abstraction is operating below both domains rather than merely renaming one project's architecture.

A GitHub Actions workflow is intentionally **not** claimed as installed: the connected GitHub write path blocked creation of `.github/workflows/ci.yml`. CI remains a separate repository task.

## Portfolio evidence examined

The extraction pass inspected current implementation/docs from:

- Cite-Agent;
- Policy Lab / SolarPunk;
- Hardware Splicer;
- Nocturnal Oversight;
- Research Drive / YZU Cluster;
- Sharpe / Sharpe Alpha;
- the older portable Sharpe content-analysis engine as a historical precursor.

The recurring pattern is sufficiently independent across domains to justify extraction. See `EXTRACTION_MAP.md`.

## First real adapters

### Cite claim grounding

`examples/packs/cite_grounding_adapter.py` accepts the current Cite shape:

```text
claim
status = grounded | ungrounded
confidence
evidence[]
```

and maps grounded evidence into canonical source artifacts, an assertion, and locator-bearing `SUPPORTS` citations. An ungrounded claim remains a canonical candidate but is not promoted merely because the grounding routine ran.

### Hardware Splicer bench gate

`examples/packs/hardware_bench_adapter.py` accepts Hardware Splicer-style measurement semantics:

```text
measurement_ref
expected_unit
lower / upper bounds
```

and converts them into a neutral `GateResult`. The same core `Decision` and `AuthorityTransition` mechanics then enforce fail-closed authorization.

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

The next pressure test should come from the systems with the strongest history/release semantics:

1. Nocturnal correction + publication-gate fixture;
2. Policy Lab deterministic decision + receipt fixture.

Those should test whether `RevisionLink`, release authority, deterministic identity, and receipts are sufficient before the core grows further.
