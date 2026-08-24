# Context Pack Specification

**Status:** v0 draft. This is an attachment contract, not yet a plugin ABI.

A context pack turns the neutral Citation Engine into a domain-capable system without moving domain ontology into the engine.

## Minimum identity

```yaml
name: <pack-name>
version: <semver-or-explicit-version>
```

## Capability families

```yaml
schemas: {}
tools: {}
gates: {}
rules: {}
workflows: {}
renderers: {}
metadata: {}
```

### `schemas`

Domain object definitions and validation contracts.

Examples: scholarly source, empirical result, donor interface, public-record matter, dataset asset.

### `tools`

Replaceable capabilities such as MCP calls, APIs, compilers, retrievers, model calls, instruments, or local functions.

Tools return observations, calculations, candidate artifacts, or execution results. **Tool success is not authority.**

### `gates`

Deterministic or explicitly bounded evaluators that return `GateResult` with:

```text
gate_id
passed
basis_refs
reason
```

A gate must expose the basis for its result.

### `rules`

Versioned domain policy/configuration used by gates or workflows. The core does not define a universal policy language.

### `workflows`

Domain orchestration recipes. Workflows compose tools, assertions, gates, decisions, transitions, and receipts; they do not change the meaning of core objects.

### `renderers`

Ways to expose canonical state as reports, UI models, packages, exports, or other presentation artifacts.

A renderer never changes canonical truth merely by presenting it differently.

## Pack-owned semantics

A pack may define:

- what counts as acceptable evidence;
- how domain identities are resolved;
- what a verified assertion means;
- which measurements/checks must close before authorization;
- what publication, promotion, settlement, or execution gates exist;
- which actor may approve a transition;
- what outputs are safe to expose;
- what uncertainty language is required.

## Engine-owned mechanics

A pack may not redefine these invariants without explicitly forking the engine contract:

- canonical refs must resolve;
- assertions require basis;
- citations are typed basis edges;
- failed gates cannot authorize;
- corrections/replacements preserve lineage;
- canonical ids cannot be silently overwritten;
- receipts reference inspectable objects.

## MCP boundary

MCP is one possible transport for `tools` and workflows.

```text
MCP / API / CLI / local callable
             ↓
          tool adapter
             ↓
         ContextPack
             ↓
       Citation Engine
```

MCP does not define provenance, epistemic status, decision validity, or authority by itself.

## Promotion rule

A pack may use model-assisted reasoning to propose assertions, classifications, or candidate actions. Promotion into stronger epistemic or operational states must occur through explicit pack semantics and recorded basis.

```text
model proposes
→ evidence remains visible
→ deterministic/bounded checks constrain
→ decision records why
→ human/system authority advances only when allowed
```
