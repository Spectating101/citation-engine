# Citation Engine

**A domain-neutral substrate for systems where claims, decisions, and authority must remain traceable to their basis.**

> Citation here is a systems principle, not a bibliography feature: **nothing consequential should exist without an inspectable basis.**

Citation Engine extracts the recurring trust architecture independently implemented across Cite-Agent, Policy Lab, Nocturnal, Hardware Splicer, and Research Drive. Those products remain separate domain systems. They become clients and validation cases for the engine rather than modules compiled into it.

**Status:** v0.1 extraction seed with cross-domain fixture validation. Not a production framework yet.

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
- replaceable canonical store
- `ContextPack` attachment boundary

## Domain attachment

```text
                         CONTEXT PACKS
       ┌──────────┬──────────┬──────────┬──────────┐
       │   Cite   │ Policy   │Nocturnal │    HS    │
       │ schemas  │ schemas  │ schemas  │ schemas  │
       │ tools    │ rules    │ feeds    │ tools    │
       │ MCP      │ gates    │ gates    │ gates    │
       └────┬─────┴────┬─────┴────┬─────┴────┬─────┘
            └──────────┴──────┬────┴──────────┘
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

MCP, HTTP, CLI, model calls, compilers, search APIs, sensors, policy calculators, and other external systems are **capability transports/execution backends or domain runtimes**. They may retrieve, calculate, simulate, compile, classify, or render. They do not automatically promote observations or hypotheses into authoritative facts.

## Current pressure tests

The neutral core is exercised by thin adapters for four deliberately different clients:

- Cite claim grounding: evidence-backed claims and locator-bearing support edges;
- Hardware Splicer: physical measurement gates and operational authorization;
- Nocturnal: append-only corrections and fail-closed publication authorization;
- Policy Lab: deterministic constraint decisions whose audit receipt may change without changing decision identity.

The adapters live under `examples/packs/`; domain nouns are intentionally absent from `src/citation_engine/`.

## Non-goals

Citation Engine is not:

- a merged super-app;
- an academic citation manager;
- an LLM agent framework;
- a universal ontology;
- a reason for every project to share one database;
- a replacement for working domain-specific engines;
- a system where model confidence silently becomes authority.

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

Start with [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md), [`docs/EXTRACTION_MAP.md`](docs/EXTRACTION_MAP.md), [`docs/PACK_SPEC.md`](docs/PACK_SPEC.md), and [`docs/STATUS.md`](docs/STATUS.md).
