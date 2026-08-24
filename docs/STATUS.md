# Current Status

**Date:** 2026-08-24  
**Stage:** v0.1 extraction seed + four-domain pressure test

## What exists

Citation Engine now contains a runnable neutral Python core with:

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

The current package was reconstructed from the repository and tested locally on 2026-08-24:

```text
18 passed in 0.08s
```

The first eight neutral invariants cover:

1. semantic artifact digest does not depend on arbitrary address/id;
2. assertion cannot exist without basis;
3. unknown basis cannot enter canonical assertion state;
4. citation subject and basis must resolve;
5. failed gate cannot authorize;
6. decision cannot authorize another subject;
7. correction/replacement preserves the prior object;
8. receipt cannot contain dangling references.

The Cite / Hardware pass adds:

9. current Cite claim-grounding output maps to Artifact + Assertion + typed Citation;
10. an ungrounded Cite planning claim is not promoted into a supported assertion;
11. a Hardware Splicer-style measurement gate can authorize when unit/range evidence closes;
12. wrong-unit hardware evidence fails closed and cannot authorize.

The Nocturnal / Policy Lab pass adds:

13. an accepted Nocturnal correction preserves the prior record while adding explicit revision and `CORRECTS` lineage;
14. a publishable Nocturnal snapshot advances publication authority only when all declared release gates pass;
15. missing Nocturnal license / rights / pilot approval remains fail-closed and cannot be force-authorized;
16. a Policy Lab `ADMIT_WITH_LIMIT` result can enter canonical state without reimplementing its calculators;
17. Policy Lab receipt time/runtime metadata may change while semantic decision identity remains stable;
18. a Policy Lab `BLOCKED` result remains non-authorizing.

A GitHub Actions workflow is still **not** claimed as installed: the connected GitHub write path previously blocked creation of `.github/workflows/ci.yml`. CI remains a separate repository task.

## Why the second pass mattered

The first Cite / Hardware proof showed that scholarly evidence and physical measurement could share the same substrate.

Nocturnal and Policy Lab attack different failure modes:

- history must be correctable without silent overwrite;
- a release may be structurally valid but still lack publication authority;
- domain-specific deterministic calculators should remain domain-owned;
- a decision should retain semantic identity even when later audit/runtime metadata changes.

That exposed one shared missing primitive: **domain runtimes must be able to submit an already-evaluated decision to Citation Engine without forcing Citation Engine to duplicate the domain calculation.**

The resulting core change was intentionally narrow:

```text
Decision.digest
record_decision(decision)
```

No Nocturnal or Policy Lab nouns entered `src/citation_engine/`.

## Current real adapters

### Cite claim grounding

`examples/packs/cite_grounding_adapter.py`

Maps Cite's `claim / status / confidence / evidence[]` result into canonical claim/evidence artifacts, a basis-bound assertion, and locator-bearing `SUPPORTS` citations.

### Hardware Splicer bench gate

`examples/packs/hardware_bench_adapter.py`

Maps measurement reference, expected unit, and bounds into neutral gate results used by the core decision and authority mechanics.

### Nocturnal history and release

`examples/packs/nocturnal_adapter.py`

Maps accepted correction relationships into append-only revision/citation lineage and imports the public-snapshot publication decision from Nocturnal's explicit integrity, license, source-rights, and pilot gates.

### Policy Lab decision and receipt

`examples/packs/policy_lab_adapter.py`

Maps Policy Lab's deterministic `DecisionResult` and `DecisionReceipt` semantics into domain-reference artifacts, neutral gate results, a semantic decision, and a later audit receipt. Policy calculators remain outside Citation Engine.

## Architectural conclusion

The common engine is **not** a universal agent or universal research workflow.

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

Domain-specific retrieval, LLM synthesis, policy logic, circuit compilation, public-memory semantics, dataset procurement, and financial backtesting remain context-pack/domain-runtime responsibilities.

## Next pressure test

The next useful pair is Research Drive + Sharpe/Sharpe Alpha because they test a different distinction:

1. **Research Drive:** source identity, external verification relationship, and operational readiness are independent states (`exists ≠ registered ≠ query-ready`, `Verified ≠ data is true`).
2. **Sharpe Alpha:** candidate promotion requires provenance and promotion evidence rather than backtest output alone.

That pair should test whether Citation Engine needs a neutral promotion/readiness state primitive, or whether those concepts correctly remain domain assertions plus gates.
