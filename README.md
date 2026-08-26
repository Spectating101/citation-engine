# Citation Engine

**A domain-neutral substrate for systems where claims, decisions, and authority must remain traceable to their basis.**

> Citation here is a systems principle, not a bibliography feature: **nothing consequential should exist without an inspectable basis.**

Citation Engine extracts the recurring trust architecture independently implemented across Cite-Agent, Policy Lab, Nocturnal, Hardware Splicer, Research Drive, Sharpe Alpha, and now pressure-tested against Refinery Commons. Those products remain separate domain systems. They are clients and adversarial validation cases for the engine rather than modules compiled into it.

**Status:** v0.1 reusable kernel seed after seven-domain pressure testing and completed Phase 3 persistence/interchange work. Not a production framework yet.

## Core flow

```text
input / observation
        ↓
canonical artifact + provenance
        ↓
assertions / state
        ↓
typed citation / basis edges
        ↓
explicit uncertainty and unresolved fields
        ↓
verification / policy gates
        ↓
decision
        ↓
authority transition
        ↓
output / action
        ↓
receipt + revision lineage
```

## The invariant

Every consequential object should be able to answer:

```text
What is this?
Where did it come from?
What exactly does it support?
What remains unknown?
Which rule allowed the next step?
Who or what had authority to advance it?
What changed?
Can the result be reproduced or challenged?
```

## Current neutral primitives

- canonical `Artifact` identity
- `Provenance` and parent lineage
- first-class typed `Citation` edges
- basis-bound `Assertion`
- explicit epistemic status
- deterministic `GateResult`
- semantic `Decision` identity with inspectable rule and basis
- ingestion of decisions evaluated by domain runtimes
- `AuthorityTransition`
- append-only `RevisionLink`
- reproducible `Receipt`
- `CanonicalStore` attachment contract
- in-memory and append-only JSONL stores
- versioned object serialization
- portable rooted evidence/decision/receipt bundles
- `ContextPack` attachment boundary

## Reusable kernel surface

```python
from citation_engine import CitationEngine, JsonlStore

engine = CitationEngine(JsonlStore(".citation-engine/canonical.jsonl"))
```

Core/value envelopes use `citation-engine.object.v1`. Portable graph bundles use `citation-engine.bundle.v1`.

A receipt can be exported with its complete reference closure:

```python
from citation_engine import export_bundle

bundle = export_bundle(engine.store, ["receipt:workflow-result"])
```

See [`docs/REUSE.md`](docs/REUSE.md), [`docs/REFINERY_INTEGRATION.md`](docs/REFINERY_INTEGRATION.md), and [`examples/minimal_seed.py`](examples/minimal_seed.py).

## Domain attachment

```text
                               CONTEXT PACKS
   ┌────────┬────────┬──────────┬────────┬────────┬────────┬──────────┐
   │  Cite  │ Policy │Nocturnal │   HS   │ Drive  │ Sharpe │ Refinery │
   │ tools  │ rules  │ feeds    │ tools  │ data   │ gates  │ Commons  │
   │ MCP    │ gates  │ gates    │ gates  │ gates  │ models │ evidence │
   └────┬───┴────┬───┴────┬─────┴────┬───┴────┬───┴────┬───┴────┬─────┘
        └────────┴─────────┴──────┴────────┴────────┴───────┬──────┘
                                                            ▼
                                                  ┌───────────────────┐
                                                  │  CITATION ENGINE  │
                                                  │ Artifact          │
                                                  │ Provenance        │
                                                  │ Citation          │
                                                  │ Assertion         │
                                                  │ Gate / Decision   │
                                                  │ Authority         │
                                                  │ Revision          │
                                                  │ Receipt           │
                                                  └───────────────────┘
```

MCP, HTTP, CLI, model calls, compilers, search APIs, sensors, policy calculators, data procurement runtimes, backtest engines, supply-chain verifiers, and registries are **capability transports/execution backends or domain runtimes**. They may retrieve, calculate, simulate, compile, classify, verify an artifact, verify a transfer, or render. They do not automatically promote observations or hypotheses into authoritative facts.

## Current pressure tests

The neutral core has been exercised by thin adapters for seven deliberately different clients:

- **Cite:** evidence-backed claims and locator-bearing support edges;
- **Hardware Splicer:** physical measurement gates and operational authorization;
- **Nocturnal:** append-only corrections and fail-closed publication authorization;
- **Policy Lab:** deterministic constraint decisions whose audit receipt may change without changing decision identity;
- **Research Drive:** source/custody verification kept separate from operational query readiness;
- **Sharpe Alpha:** attractive backtest output kept separate from provenance and promotion authority;
- **Refinery Commons:** semantic capability versus concrete realization identity, exact-subject anti-laundering, contradictory evidence preservation, explicit curation authority, and cross-domain reuse without adding core ontology.

The Refinery pressure test deliberately keeps its Commons evidence-maturity model and software/institutional nouns outside `src/citation_engine/`. It adds no new kernel primitive. See [`docs/REFINERY_INTEGRATION.md`](docs/REFINERY_INTEGRATION.md).

The Research Drive / Sharpe pressure test required **no new core primitive**. Readiness and promotion remain domain gate outcomes rather than kernel state types.

Phase 3 then added reuse infrastructure without adding domain ontology:

- stable versioned envelopes for all core objects/values;
- append-only `JsonlStore` with fingerprint and referential-integrity checks;
- rooted bundle export/import with top-level fingerprinting;
- `validate_store()` for third-party store conformance;
- a minimal fresh-project seed example.

The Phase 3 targeted suite passes 18 tests; the same reconstruction plus the original eight neutral invariant tests passes 26. Earlier adapter pressure tests remain separately validated. Refinery integration execution is gated by native repository CI rather than being claimed from an unavailable local GitHub checkout. See [`docs/STATUS.md`](docs/STATUS.md) for the execution/CI caveat.

The adapters live under `examples/packs/`; domain nouns are intentionally absent from `src/citation_engine/`.

## Non-goals

Citation Engine is not:

- a merged super-app;
- an academic citation manager;
- an LLM agent framework;
- a universal ontology;
- a reason for every project to share one database;
- a replacement for working domain-specific engines;
- a system where model confidence silently becomes authority;
- a generic `ready/promoted/approved` status enum that erases why a transition was permitted.

## Extraction rule

A primitive belongs in the engine only when:

1. it appears independently in at least two domain systems;
2. its semantics can be stated without a domain noun;
3. extracting it reduces duplicated trust/verification mechanics;
4. domain projects can still define their own policies without forking the core.

## Development

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
pytest -q
```

Start with [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md), [`docs/EXTRACTION_MAP.md`](docs/EXTRACTION_MAP.md), [`docs/PACK_SPEC.md`](docs/PACK_SPEC.md), [`docs/REUSE.md`](docs/REUSE.md), [`docs/REFINERY_INTEGRATION.md`](docs/REFINERY_INTEGRATION.md), and [`docs/STATUS.md`](docs/STATUS.md).
