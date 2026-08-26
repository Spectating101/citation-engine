# Refinery Commons integration pressure test

## Purpose

Refinery Commons is the seventh adversarial client for Citation Engine.

The integration deliberately does **not** merge Refinery into Citation Engine and does **not** add `Capability`, `Implementation`, software-supply-chain, maturity, recommendation, or institutional nouns to the core. It asks whether Refinery's accumulated evidence/provenance mechanics can be represented by the existing neutral substrate and which missing primitive, if any, is actually earned by failure.

The adapter lives at:

- `examples/packs/refinery_commons_adapter.py`

The pressure tests live at:

- `tests/test_refinery_commons_adapter.py`

## Mapping

| Refinery Commons concept | Citation Engine representation |
|---|---|
| source/README/OCI/SPDX/SLSA/Scorecard packet | `Artifact` + `Provenance` |
| Capability Capsule | domain `Artifact(kind="refinery.capability")` |
| exact Implementation | domain `Artifact(kind="refinery.implementation")` |
| Claim | `Assertion` plus explicit `Citation` basis edges |
| positive/negative evaluations | coexisting append-only assertions |
| explicit curation/recommendation | `GateResult` -> `Decision` -> `AuthorityTransition` |
| reviewer/export packet | `Receipt` + rooted evidence bundle |
| Commons evidence maturity | stays in the Refinery pack/domain; not a CE state enum |

## Extracted invariant: exact-subject evidence binding

Refinery machine-evidence work discovered `MEV0-001`: SLSA/SPDX evidence first attached at project scope could accidentally confer one release's evidence onto sibling implementations.

The adapter therefore enforces:

> Evidence attached to subject X must not silently confer its epistemic or verification state upon related subject Y.

`record_exact_provenance_claim()` requires:

1. an exact `refinery.implementation` subject;
2. a full SHA-256 digest in that implementation identity;
3. the same SHA-256 digest in the provenance evidence subject;
4. an explicit verification state.

A verified OCI artifact therefore does not verify a sibling Git implementation merely because both realize the same semantic capability.

This invariant is domain-neutral even though the first adapter is SLSA-shaped. The same failure mode exists for dataset snapshots, paper versions, policy revisions, hardware units, model checkpoints, deployments, and other related-but-distinct subjects.

## Semantic identity versus realization identity

Refinery has also pressure-tested a useful two-level distinction:

```text
semantic capability contract
        |
        +---- concrete realization A
        +---- concrete realization B
```

The adapter implements this distinction without adding a core `Relation` object:

- capability IDs hash only the reviewed semantic contract;
- implementation IDs hash the capability reference plus exact realization identity;
- an implementation's provenance parents include the capability and exact source/artifact packet so rooted bundles preserve the structural closure.

A source revision can therefore change without mutating semantic capability identity. Changing the semantic contract changes the capability identity.

This parent-link use is intentionally adapter-local. It is not evidence that Citation Engine should permanently overload provenance as a universal structural-relation graph.

## Why no core `Relation` primitive yet

The mapping `Implementation -> realizes -> Capability` is structural rather than evidentiary. A future neutral `Relation(subject_ref, relation, object_ref)` may be justified, but this tranche deliberately does not add it.

The extraction gate remains:

1. demonstrate a real mapping failure with existing primitives;
2. demonstrate the same neutral need in at least one additional domain/client;
3. define the relation without leaking Refinery nouns;
4. prove that adding it reduces awkwardness rather than creating a generic ontology layer.

Until then, the core remains unchanged.

## Adversarial gates

The integration suite exercises:

1. **Revision identity** — implementation revision changes while capability identity stays stable; semantic contract changes mutate capability identity.
2. **Evidence laundering** — verified OCI/SLSA evidence cannot promote a sibling Git implementation.
3. **Contradiction preservation** — pass and fail evidence coexist; later evidence does not erase earlier adverse evidence.
4. **Curation boundary** — evidence maturity does not become recommendation without an explicit named curator act and a decision/authority transition.
5. **Cross-domain generalization** — an institutional coral-restoration case uses the same adapter without requiring a new CE core ontology.
6. **Portable closure** — a Refinery review receipt exports the complete transitive basis graph through Citation Engine bundles.

## Direction of reuse

### Refinery -> Citation Engine

- exact-subject evidence-scoping discipline;
- semantic-contract versus concrete-realization identity pressure test;
- adversarial sibling-evidence tests;
- standards-shaped provenance inputs as future adapter cases.

### Citation Engine -> Refinery

- canonical evidence objects instead of free-floating `evidence_ref` strings;
- separate Assertion and Citation semantics;
- explicit gate/decision/authority boundary for recommendation/admission;
- append-only correction and receipt semantics;
- portable rooted evidence closures.

## Current decision

**Do not merge the projects. Do not add a core primitive yet.**

Treat Refinery as a live client and use failures to earn neutral extraction. If the current adapter remains natural across real uv machine evidence and additional non-software cases, the existing Citation Engine kernel is sufficient for this tranche. If structural relationship modeling is the repeated remaining awkwardness, `Relation` becomes the next candidate for a separately justified core change.
