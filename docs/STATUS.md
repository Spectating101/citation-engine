# Current Status

**Date:** 2026-08-24  
**Stage:** v0.1 reusable kernel seed — Phase 3 complete

## What exists

Citation Engine now contains a runnable neutral Python kernel with:

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
- `ContextPack` attachment boundary;
- `CanonicalStore` protocol;
- `MemoryStore` for tests/embedding;
- append-only persistent `JsonlStore`;
- versioned object/value serialization (`citation-engine.object.v1`);
- rooted portable graph bundles (`citation-engine.bundle.v1`);
- reusable `validate_store()` conformance checking;
- a fresh-project seed example that persists state and exports a receipt bundle.

## Validation history

### Six-domain extraction pressure tests

The earlier extraction sequence established **24 validated invariant/adapter tests across sequential runs**:

- 8 neutral invariants;
- 4 Cite / Hardware Splicer tests;
- 6 Nocturnal / Policy Lab tests;
- 6 Research Drive / Sharpe Alpha tests.

Those runs established that the neutral model survives scholarly evidence, physical measurement, correction/publication history, deterministic policy decisions, data readiness, and quantitative promotion semantics.

### Phase 3 implementation validation

Phase 3 added persistence/interchange tests covering:

1. round-trip serialization for every canonical stored object;
2. standalone versioned envelopes for `Provenance` and `GateResult` values;
3. semantic digest preservation across round-trip;
4. explicit rejection of unknown object schema versions;
5. per-object fingerprint mutation detection;
6. persistent JSONL reopen with identical objects;
7. append-only/no-silent-overwrite enforcement;
8. tampered persistent-log detection;
9. receipt-rooted dependency-closure export;
10. bundle import into an empty persistent store;
11. top-level bundle fingerprint mutation detection;
12. dangling-reference rejection even when the top-level fingerprint is recomputed;
13. reusable conformance checks for both memory and persistent stores.

The Phase 3 targeted suite passes:

```text
18 passed in 0.07s
```

The same current Phase 3 reconstruction was then run with the original eight neutral invariant tests as a regression set:

```text
26 passed in 0.06s
```

The minimal fresh-project example was also executed successfully and emitted:

```text
citation-engine.bundle.v1
5-object receipt dependency closure
canonical.jsonl
receipt-bundle.json
```

### Execution limitation

This runtime still cannot DNS-resolve `github.com`, so a literal `git clone` followed by one monolithic `pytest` invocation is unavailable here. The current Phase 3 files were tested from the exact implementation content before/while committing them, and the original invariant regression was rerun against that current reconstruction. The earlier domain-adapter suites remain separately validated rather than being misreported as one current CI run.

## Phase 3 result

The kernel became reusable **without adding any new domain ontology**.

The important new boundary is:

```text
domain runtime / context pack
        ↓
canonical objects + basis refs
        ↓
Citation Engine
        ↓
append-only canonical store
        ↓
receipt-rooted portable bundle
```

Persistence does not introduce a second database model. `JsonlStore` persists the same versioned canonical objects the engine already uses.

A portable bundle is not a project export. It is the inspectable dependency closure for one or more consequential roots. A receipt bundle can therefore move between systems without bringing Cite, Hardware Splicer, Policy Lab, Nocturnal, Research Drive, or Sharpe code with it.

## Serialization and interchange contract

Object/value schema:

```text
citation-engine.object.v1
```

Supported envelopes:

- `Artifact`
- `Provenance`
- `Citation`
- `Assertion`
- `GateResult`
- `Decision`
- `AuthorityTransition`
- `RevisionLink`
- `Receipt`

Bundle schema:

```text
citation-engine.bundle.v1
```

Import/export fails closed on incompatible versions, mutated object fingerprints, mutated bundle fingerprints, dangling references, canonical-id conflicts, and unresolvable reference cycles.

`Provenance` and `GateResult` have independent interchange envelopes but remain nested values rather than standalone canonical store entities because they do not carry canonical ids.

## Adapter contract

A fresh project can now:

```text
install Citation Engine
→ choose MemoryStore or JsonlStore
→ define a ContextPack / thin adapter
→ record evidence and consequential subjects
→ emit basis-bound assertions/citations
→ evaluate or import domain decisions
→ advance authority when allowed
→ issue a receipt
→ persist canonical state
→ export an inspectable receipt bundle
```

See:

- `docs/PACK_SPEC.md`
- `docs/REUSE.md`
- `examples/minimal_seed.py`

## Current real adapters

- `examples/packs/cite_grounding_adapter.py`
- `examples/packs/hardware_bench_adapter.py`
- `examples/packs/nocturnal_adapter.py`
- `examples/packs/policy_lab_adapter.py`
- `examples/packs/research_drive_adapter.py`
- `examples/packs/sharpe_promotion_adapter.py`

No Cite, Hardware, Nocturnal, Policy, Drive, Dataset, Sharpe, Strategy, readiness, or promotion nouns have entered the kernel ontology.

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
→ can carry its dependency graph across systems
```

A successful external computation, transfer, model answer, backtest, publication build, or domain decision is evidence about a specific relationship. It is not automatically truth and it is not automatically authority.

## Next engineering question

The next useful proof should be **real consumption rather than more extraction**: make one existing project use Citation Engine as a dependency for a bounded workflow, while preserving that project's current domain runtime as the authority for domain-specific calculation.

A good first integration target should have:

- an already-working consequential workflow;
- clear basis/provenance objects;
- an existing receipt or audit output that can be mapped without a rewrite;
- low migration risk and an easy rollback path.

Do not add another neutral primitive merely to make integration convenient.

## CI limitation

A GitHub Actions workflow is still **not** claimed as installed. The connector previously blocked creation under `.github/workflows/`, and the execution runtime cannot clone GitHub directly. CI remains a separate repository task.
