# Phase 4 — Real consumption and transport boundary

## Goal

Prove Citation Engine reduces duplicated trust infrastructure in real projects before making it enforcement-critical or multiplying implementations across languages.

## Current live candidates

### Cite-Agent — draft PR #6

Seam: grounded claim → existing evidence-link substrate → Citation Engine trace.

Required proof:

- representative PDF-passage grounding emits stable claim/evidence/citation/receipt identity;
- abstract-only evidence remains abstract-only in Cite while still producing an honest trace;
- unsupported/planning claims do not enter the supported-assertion path;
- optional JsonlStore survives repeated requests without silent overwrite;
- bridge failure/disable does not alter Cite grounding semantics;
- determine whether trace metadata should remain response-local or also persist in project/manuscript artifacts.

Current complication: the first Cite PR GitHub Actions run failed before any job step executed in either backend or frontend job. This is recorded as a runner/workflow-level failure rather than a code-test failure until GitHub provides a concrete executed-step error.

### Hardware-Splicer — draft PR #69

Seam: native golden-real report → imported decision/gates → Citation Engine receipt bundle.

Required proof:

- native Hardware CI installs the pinned Citation Engine package through the normal editable-install path;
- golden-real verification still passes its native electrical/bench bar;
- authorized report creates an authority trace;
- blocked/inconsistent report cannot create authority;
- emitted trace is useful in the verification/report artifact without becoming a second electrical authority.

## Cross-language boundary

Policy Lab's `@solarpunk/constraint-core` is JavaScript/ESM. Do not copy the Python kernel into JS.

After the two Python consumers settle, inventory the operations they actually use. Current observed operations are:

```text
record artifact
record assertion
record citation
record/import decision
record authority transition
issue receipt
export rooted bundle
persist append-only graph
```

Then decide whether cross-language consumption needs:

1. a small HTTP/local service around the Python kernel;
2. a language-neutral wire protocol plus canonical reference implementation;
3. a generated client over a stable service contract;
4. or only bundle import/export for asynchronous interoperability.

Do not choose before real consumer traces show which calls are latency-sensitive and which can remain asynchronous.

## Enforcement gate

Citation Engine must remain shadow/non-authoritative until all are true:

- two distinct native consumer workflows execute successfully with the kernel installed;
- representative real outputs produce semantically faithful trace graphs;
- rollback is tested;
- persistent store behavior is acceptable;
- a domain can name one specific transition that central enforcement would improve rather than duplicate;
- failure semantics are explicit (fail-open vs fail-closed) for that transition.

## Non-goals

Phase 4 does not add:

- generic agents;
- universal readiness/promotion states;
- a shared UI;
- a universal ontology;
- a JavaScript rewrite;
- a network service merely because one might be useful later.
