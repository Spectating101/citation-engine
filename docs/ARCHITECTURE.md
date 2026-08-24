# Citation Engine Architecture

## 1. Design thesis

Citation Engine is the layer below domain products that answers one question:

> **What must a system preserve so that a consequential claim, decision, or action can cite its basis?**

The answer is not "an LLM" and not "a source URL". It is a chain of canonical objects, typed relationships, explicit uncertainty, deterministic gates, authority transitions, and reproducible receipts.

```text
observation / input
      ↓
Artifact ───────────────┐
      ↓                 │
Assertion               │
      ↓                 │ Citation edges
verification / gates ◄──┤
      ↓                 │
Decision                │
      ↓                 │
AuthorityTransition     │
      ↓                 │
output / action         │
      ↓                 │
Receipt ◄───────────────┘
```

## 2. Citation is a typed basis edge

An academic citation is one instance of a more general relation.

Citation Engine therefore models citation as:

```text
subject ──relation──> basis
```

Initial relations include:

```text
SUPPORTS
DERIVED_FROM
CONSTRAINS
CONTRADICTS
CORRECTS
AUTHORIZES
CONTEXTUALIZES
```

A URL, DOI, file name, model response, hash, or tool invocation is not by itself a citation. The system must know **what object is citing what basis, in what relationship, and optionally where in that basis**.

## 3. Epistemic state and operational authority are separate

This is one of the strongest recurring invariants across the portfolio.

```text
Epistemic question:
What does the evidence justify believing or asserting?

Operational question:
What is the system/operator allowed to do next?
```

A verified observation does not automatically authorize publication, issuance, firmware generation, power-on, promotion, or any other consequential transition.

Likewise, an actor possessing operational permission does not make a claim true.

The engine therefore keeps `Assertion.status` separate from `AuthorityState` and requires a `Decision` before consequential authorization.

## 4. Evidence is not truth

The engine deliberately refuses several common collapses:

```text
source exists          ≠ source is authoritative
cryptographically valid ≠ provenance established
matched                ≠ identical
query-ready            ≠ externally verified
schema-valid           ≠ decision-valid
model confidence       ≠ authority
simulation succeeded   ≠ physical truth
publication permission ≠ evidence quality
```

Domain packs define what verification means for their objects. The engine only preserves the mechanics by which that judgment remains inspectable.

## 5. Identity and presentation are separate

Canonical identity should bind the semantic object, not arbitrary presentation labels. `Artifact.digest` therefore excludes the artifact address/id and hashes the semantic body.

Domain packs may require stricter identity bodies, versioned schemas, source hashes, or policy manifest hashes. The core does not dictate one universal identity formula.

Rule: changing presentation should not silently create new evidence; changing semantic content should not silently retain old identity.

## 6. Corrections are append-only

Canonical objects cannot be silently overwritten. A correction or replacement creates a new object and an explicit `RevisionLink`.

This supports:

- Nocturnal-style corrections/disputes;
- revised research evidence;
- corrected datasets;
- updated interface contracts;
- policy/version changes;
- superseded model outputs.

History remains inspectable rather than being rewritten in place.

## 7. Tools are capabilities, not authorities

A context pack may attach:

```text
MCP tools
HTTP APIs
CLI programs
LLMs
retrievers
compilers
simulators
sensors
instrument drivers
renderers
```

Tools may retrieve, calculate, infer, compile, simulate, or render. A tool call cannot by itself promote a hypothesis into an authoritative fact or authorize a consequential action.

This is why MCP belongs at the attachment layer, not in the canonical ontology.

## 8. Context packs own domain meaning

The kernel must not know what any of these are:

```text
Paper
CitationStyle
Circuit
DonorModule
NewsEvent
Person
PolicyInstrument
Settlement
Dataset
Security
Shelter
Animal
```

A `ContextPack` may know all of them.

```text
ContextPack
├── schemas
├── tools
├── gates
├── rules
├── workflows
├── renderers
└── metadata
        │
        ▼
CitationEngine
├── Artifact
├── Citation
├── Assertion
├── GateResult
├── Decision
├── AuthorityTransition
├── RevisionLink
└── Receipt
```

## 9. Initial invariants

1. No assertion without inspectable basis.
2. No citation whose subject or basis is unresolved.
3. No silent overwrite of canonical state.
4. Corrections preserve prior objects.
5. Decisions require explicit gate results and basis.
6. Failed gates cannot authorize consequential transitions.
7. A decision cannot authorize a different subject.
8. Receipts may only cite resolvable canonical objects.
9. Execution backends never acquire truth authority merely by running successfully.
10. Domain nouns do not enter the core.

## 10. Deliberately absent from v0.1

- LLM orchestration;
- vector database selection;
- UI;
- MCP server implementation;
- distributed persistence;
- generic confidence aggregation;
- autonomous rule/policy generation;
- generic identity resolution;
- domain schemas.

A capability should move into the engine only after at least two independent clients demonstrate that the same **mechanic**, rather than merely a similarly named feature, is required.
