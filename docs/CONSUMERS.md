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

## Promotion rule for consumers

Do not make Citation Engine enforcement-critical in a consumer merely because shadow recording works.

A consumer should move from shadow to enforcement only after:

- representative real outputs produce semantically faithful traces;
- failure and rollback behavior are tested;
- persistent-store behavior is operationally acceptable;
- another substantially different consumer demonstrates the same kernel contract;
- the domain owner can state exactly which authority transition, if any, Citation Engine is permitted to block.
