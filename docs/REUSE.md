# Reusing Citation Engine

Citation Engine is now usable as a small trust/provenance kernel without importing any portfolio-specific domain model.

## 1. Choose a store

For tests or embedding:

```python
from citation_engine import CitationEngine, MemoryStore

engine = CitationEngine(MemoryStore())
```

For durable local state:

```python
from citation_engine import CitationEngine, JsonlStore

engine = CitationEngine(JsonlStore(".citation-engine/canonical.jsonl"))
```

`JsonlStore` is append-only. Reusing an existing canonical id with different content fails closed. Every line is a versioned, fingerprinted canonical-object envelope; reopening the store verifies fingerprints and dangling references before accepting the file.

## 2. Define domain meaning outside core

A new project normally contributes a `ContextPack` plus thin adapters.

The minimum adapter contract is:

1. convert domain inputs/results into canonical `Artifact` objects with explicit `Provenance`;
2. create `Assertion` and typed `Citation` edges only for relationships actually supported by the supplied basis;
3. expose deterministic or explicitly bounded domain checks as `GateResult` values;
4. either let `CitationEngine.evaluate()` run registered gates, or import an already-evaluated domain `Decision` with `record_decision()`;
5. use `AuthorityTransition` only after a permitting decision;
6. emit a `Receipt` for consequential workflows;
7. keep corrections append-only through new objects plus `RevisionLink` rather than overwriting history.

Domain objects such as papers, circuits, policies, datasets, strategies, matters, or instruments remain in adapters/packs.

## 3. Serialization contract

`serialize_object()` / `deserialize_object()` use:

```text
citation-engine.object.v1
```

Versioned envelopes exist for:

- `Artifact`
- `Provenance`
- `Citation`
- `Assertion`
- `GateResult`
- `Decision`
- `AuthorityTransition`
- `RevisionLink`
- `Receipt`

Each envelope contains a canonical fingerprint. Unknown schema versions and mutated payloads are rejected explicitly.

`Provenance` and `GateResult` may be serialized independently for interchange, but they remain nested values rather than standalone canonical store entities because they do not carry canonical ids.

## 4. Export a portable evidence bundle

A rooted bundle contains the complete dependency closure needed to inspect a consequential object.

```python
from citation_engine import export_bundle

bundle = export_bundle(engine.store, ["receipt:my-workflow"])
```

The bundle schema is:

```text
citation-engine.bundle.v1
```

A bundle contains:

- explicit root refs;
- versioned object envelopes;
- per-object fingerprints;
- a top-level bundle fingerprint.

Import into another store:

```python
from citation_engine import JsonlStore, import_bundle

other = JsonlStore("other/canonical.jsonl")
roots = import_bundle(bundle, other)
```

Import fails on incompatible schema versions, object mutation, bundle mutation, dangling refs, canonical-id conflicts, or unresolvable reference cycles.

## 5. Store conformance

Third-party store implementations should expose the `CanonicalStore` methods:

```text
put(object_id, value)
get(object_id)
contains(object_id)
require(*refs)
ids()
```

Then run:

```python
from citation_engine import validate_store

validate_store(my_store)
```

The checker verifies key/id agreement, canonical serialization round-trip, and graph referential integrity for the populated store.

## 6. Minimal seed

See [`../examples/minimal_seed.py`](../examples/minimal_seed.py).

It demonstrates a fresh project that:

```text
records evidence + subject
→ defines a ContextPack gate
→ evaluates a Decision
→ advances Authority
→ issues a Receipt
→ persists the graph
→ exports a receipt-rooted portable bundle
```

The example intentionally contains no Cite, Policy Lab, Nocturnal, Hardware Splicer, Research Drive, or Sharpe code.

## Boundary rule

Do not expand Citation Engine merely because two projects use the same application feature.

Extract only mechanics that remain meaningful without the domain noun. Retrieval, LLM orchestration, scoring models, identity resolution, workflow DSLs, database schemas, and UI shells remain outside the kernel until independent implementations demonstrate a narrower common invariant.
