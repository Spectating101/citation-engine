# Consumer integrations

Citation Engine is useful only if real domain systems can consume it without surrendering their domain authority or copying the kernel into themselves.

## Consumer rule

A production consumer should attach at a consequential boundary that already exists in the domain system:

```text
domain runtime produces a bounded result
→ adapter maps result into neutral objects
→ Citation Engine records basis / lineage / receipt
→ domain response or artifact carries compact trace identity
```

The consumer must retain an explicit rollback path during initial adoption. Citation Engine should not be inserted inside domain scoring/calculation merely to claim integration.

## Consumer 1: Cite-Agent claim grounding

**Repository:** `Spectating101/cite-agent`  
**Candidate:** draft PR #6, branch `citation-engine-shadow`  
**Seam:** `/api/paper/ground-claims` → `evidence_substrate.links_from_grounded_claims()`

Cite remains authoritative for:

- claim extraction;
- grounding and confidence scoring;
- passage/abstract/metadata selection;
- overclaim and unsupported-marker rejection;
- evidence verification vocabulary.

Citation Engine starts only after Cite marks a claim `grounded`. The bridge records:

```text
claim candidate
→ evidence artifact(s)
→ SUPPORTED assertion
→ typed SUPPORTS citation(s)
→ receipt
→ portable bundle identity
```

Compact Citation Engine trace metadata is attached to Cite's existing evidence-link object. Existing evidence fields are not renamed or reinterpreted.

### Runtime posture

Default candidate mode is shadow/fail-open:

```text
CITE_AGENT_CITATION_ENGINE=on     # default
CITE_AGENT_CITATION_ENGINE_STRICT=off
```

Rollback:

```text
CITE_AGENT_CITATION_ENGINE=off
```

Optional durable canonical log:

```text
CITE_AGENT_CITATION_ENGINE_STORE=/data/citation-engine/grounding.jsonl
```

### What this integration tests

This is the first proof that Citation Engine can become an actual dependency rather than an extraction repository. It tests whether:

1. a domain system can keep its own epistemic judgment while delegating trace recording;
2. neutral object IDs and receipts can be added without changing the domain response contract;
3. the kernel can be disabled independently;
4. persistent storage can be introduced without forcing Cite to share a database;
5. the integration reduces future provenance/receipt duplication instead of moving Cite logic into the kernel.

## Consumer 2: Hardware-Splicer golden real authorization

**Repository:** `Spectating101/hardware-splicer`  
**Candidate:** draft PR #69, branch `citation-engine-shadow`  
**Seam:** `scripts/verify_splice_real_bench.py` after `run_splice_golden_real()` has produced the native report.

Hardware-Splicer remains authoritative for:

- electrical/interface contracts;
- KiCad DRC;
- firmware authorization;
- physical bench measurement acceptance;
- power-on authorization;
- whether a golden-real run is genuinely non-simulated and passed.

Citation Engine imports the already-evaluated Hardware result as six inspectable gates:

```text
golden-real run
├─ DRC evidence
├─ contract-update evidence
├─ firmware-authority evidence
├─ bench-submission evidence
├─ physical power-on evidence
└─ non-simulated evidence
       ↓
external Hardware decision
       ↓
optional AUTHORIZED transition
       ↓
receipt + portable bundle identity
```

The bridge checks that Hardware's declared `report.passed` agrees with those six existing conditions. It does not independently calculate electrical truth. A blocked native report remains non-authorizing in Citation Engine.

### Runtime posture

Rollback:

```text
HARDWARE_SPLICER_CITATION_ENGINE=off
```

Strict consistency checking:

```text
HARDWARE_SPLICER_CITATION_ENGINE_STRICT=1
```

Optional durable canonical log:

```text
HARDWARE_SPLICER_CITATION_ENGINE_STORE=/path/to/hardware-citation-engine.jsonl
```

### What this integration tests

The second consumer exercises a materially different kernel path from Cite:

1. domain runtime owns the deterministic decision rather than Citation Engine evaluating the domain;
2. `record_decision()` can preserve a multi-gate physical authorization basis;
3. operational authority remains separate from evidence/artifact existence;
4. blocked outcomes still receive inspectable receipts without creating authority;
5. identical real-run reports remain idempotent under the persistent store.

Focused local validation: `5 passed` against the exact Phase-3 kernel source. Native Hardware GitHub Actions also starts normally and executes real runner steps on the consumer branch.

## Cross-language observation: Policy Lab / constraint-core

`@solarpunk/constraint-core` is an ES-module package, while the current Citation Engine implementation is Python. Its decision/receipt semantics remain a strong semantic conformance case, but it should **not** gain a hand-copied JavaScript reimplementation merely to count as a consumer.

This creates a legitimate later transport question:

```text
Python package embedding
vs
language-neutral service/protocol/client
```

Do not solve that by duplicating canonical hashing, bundle validation, and authority semantics independently in every language. The cross-language interface should be extracted only after the two Python consumers prove which operations actually need to cross the boundary.

## Promotion rule for consumers

Do not make Citation Engine enforcement-critical in a consumer merely because shadow recording works.

A consumer should move from shadow to enforcement only after:

- representative real outputs produce semantically faithful traces;
- failure and rollback behavior are tested;
- persistent-store behavior is operationally acceptable;
- at least two substantially different consumers demonstrate the same kernel contract;
- the domain owner can state exactly which authority transition, if any, Citation Engine is permitted to block.

Cite + Hardware now satisfy the **two substantially different shadow consumers** prerequisite. They do **not** yet satisfy the representative production-output or enforcement-authority prerequisites.
