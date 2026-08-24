# Phase 4 Status — real consumers

**Date:** 2026-08-24

## Summary

Citation Engine now has two real shadow-consumer candidates in separate repositories:

1. Cite-Agent draft PR #6 — scholarly claim/evidence tracing.
2. Hardware-Splicer draft PR #69 — deterministic physical bench authorization tracing.

These are deliberately different consumption paths. Cite records a supported assertion and typed evidence citations after its domain grounder has made the epistemic judgment. Hardware imports an already-evaluated multi-gate decision after its domain runtime has made the physical authorization judgment.

No new core primitive was required for either consumer.

## Cite-Agent

Branch: `citation-engine-shadow`

Current bounded local validation:

```text
9 passed
```

The suite covers:

- PDF-passage evidence remains `passage_verified` in Cite and gains a Citation Engine receipt trace;
- abstract-only evidence remains `abstract_only` / `provisional` rather than being upgraded by the kernel;
- ungrounded/planning claims produce no supported evidence link even when candidate rows are present;
- independent runtime kill switch restores the previous response shape;
- persistent JsonlStore is idempotent for repeated identical grounding.

### GitHub Actions anomaly

Two PR workflow runs failed before any job step executed. Both the frontend and backend jobs terminate with no step records (`steps=null`), including before checkout or language setup. This is not currently classified as a code-test failure.

The same account's Hardware-Splicer Actions runners execute normally, so this appears repository/run-specific rather than a global GitHub Actions outage.

Cite PR remains draft.

## Hardware-Splicer

Branch: `citation-engine-shadow`

Focused reconstructed bridge validation:

```text
5 passed
```

The native Hardware-Splicer CI then successfully:

- checked out the branch;
- configured Python/Node;
- installed KiCad;
- completed the normal `Splice v1 slim install` with the pinned Citation Engine dependency;
- completed project-package bridge tests;
- completed splice demo verification;
- completed golden-loop verification;
- completed **Splice real-bench verification**;
- completed evidence-integration focused tests;
- completed the splice-ui production build;
- completed product/API checks through the observed CI progress.

### Native golden-real artifact proof

The uploaded `splice-golden-real-report` artifact contains a real non-simulated Hardware result:

```text
build_id: robot_drive_base
drc_pass: true
contract_update_count: 2
contract_updates_ok: true
matched_measurement_count: 11
open_gates: []
bench_after.power_on_authorized: true
passed: true
```

The corresponding verification artifact contains:

```text
citation_engine.status: recorded
bundleSchema: citation-engine.bundle.v1
bundleObjectCount: 10
authorityRef: hardware-splicer:authority:6931975fdbed0d3764e9e712
receiptDigest: a987f894324cd0ccf2e978b9e876fc5ffdc3fc9ae5224b5ddce152ad93737d90
bundleFingerprint: 4582c6602792070a776510e6d4052abce7f567c9937f0c901024e0cc01ab364b
```

This is the first native proof that an existing project can install Citation Engine through its ordinary dependency path and emit a real authority/receipt graph without moving domain authority into the kernel.

Hardware PR remains draft until the complete native workflows finish.

## Cross-language result

Policy Lab's `@solarpunk/constraint-core` is JavaScript/ESM, while Citation Engine is currently Python. This is now treated as a transport question, not a reason to hand-copy the kernel into another language.

Observed operations used by the first two consumers:

```text
record artifact
record assertion
record citation
record/import decision
record authority transition
issue receipt
export rooted bundle
optional append-only persistence
```

A future language-neutral interface should be chosen from these observed calls, not from a speculative universal API.

## Current conclusion

The two real integrations strengthen the original abstraction:

```text
domain authority remains domain-owned
→ consequential result crosses a thin adapter boundary
→ Citation Engine records the inspectable basis graph
→ receipt/bundle identity can travel downstream
```

The next milestone is not another domain fixture. It is native completion of the two consumer workflows, representative real Cite traces, and then a decision about whether any one domain transition should move from shadow tracing to fail-closed shared enforcement.
