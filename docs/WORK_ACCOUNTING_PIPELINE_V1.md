# Work-Accounting Pipeline and CAS V1

Status: implementation foundation, inactive. This document specifies the
orchestration and persistence seam for hierarchical work accounting. It does
not register or activate a projection, invoke a hosted provider by itself, or
change a workflow.

## 1. One accepted submission is one transition

The pipeline reads accepted submissions in the canonical problem ledger's
`main` first-parent order. It sends exactly one submission to the builder,
validates and persists the resulting `research_builder_v6` post-state,
topology alignment, and same-world handoff, and then asks the scheduler for the
one claim at the canonical frontier. Only that claim can produce a work bundle
and publication.

The serial semantic history is:

```text
(K0, A0) --submission x1--> (K1, A1) --submission x2--> (K2, A2)
```

`Ki` is the exact builder-owned program/thread portfolio after `xi`; `Ai` is
the committed with-access accounting state for `xi`. Each claim binds `Ai-1`,
`Ki-1`, and `Ki` exactly. Items remain semantic/evidence anchors. The pipeline
does not create or store an independent portfolio topology.

`maximum_subjects` is an invocation limit only. It is absent from every stored
semantic artifact, provider request, retry key, and digest. Splitting the same
canonical input across hosted batches therefore produces identical states,
bundles, publications, and final lane head.

## 2. Injectable execution boundaries

`math_flow.work_accounting_pipeline` defines three deliberately narrow seams:

- a builder transition provider returns one model-authored v6 transition;
- the existing work projection provider answers the three counterfactual
  stages for one transition; and
- `CASObjectStore` stores immutable bytes and compare-and-swap lane references.

The orchestrator itself has no network dependency. Provider calls are
injected, and tests use deterministic fakes. Builder proposals are reduced by
the repository's v6 reducer; provider-authored derived state, work totals, and
publication values are never trusted.

## 3. Immutable objects and the mutable lane head

All durable values other than the lane head are immutable. Their keys contain
their canonical digest or a digest of the complete semantic request:

- root contracts, knowledge states, accounting states, and schedules;
- normalized submission inputs and exact evidence chunks;
- builder proposals, results, topology alignments, and same-world handoffs;
- transition claims, failure evidence, work bundles, and publication
  manifests; and
- every intermediate pipeline-state snapshot.

A work bundle is visible only after all indexed artifacts are stored. Its
content-addressed `run.json` is written last and is the completeness marker.
`materialize_stored_work_projection_bundle` reconstructs and revalidates a
stored bundle without a provider.

The sole mutable value is the problem/projection lane reference. It is advanced
with compare-and-swap from an exact prior byte version. A stale writer reloads
the winner; it cannot overwrite it. The included local implementation locks
per key, rejects path traversal and symlink traversal, fsyncs temporary content,
and atomically replaces the lane reference. The interface can also be
implemented by an object store with equivalent immutable-put and conditional
write semantics.

## 4. Durable phases and recovery

The pipeline state has three phases:

| Phase | Durable meaning | Resume action |
| --- | --- | --- |
| `ready` | Builder and accounting histories have one common terminal state. | Start the first supplied, unprocessed canonical submission. |
| `awaiting-work` | The post-builder state and exact handoff are durable; a claim may be ready or waiting for retry backoff. | Reproduce/reload the claim, then reuse or run the work bundle. |
| `publication-prepared` | Bundle, publication, next accounting state, and next schedule are all durable. | Revalidate every binding and CAS the lane back to `ready`. |

Every external-call result is persisted before the lane points at it. Every
lane transition is idempotent. Crashes before a CAS leave unreachable but
valid immutable objects that a deterministic retry can reuse; crashes after a
CAS resume from the new phase. The work-stage checkpoint is bound to the exact
claim digest. A semantic work-result index is bound to the claim's stable
automatic-retry key so a crash during publication does not repeat provider
work.

## 5. Failure and retry

Provider-invalid, nonpositive-work-value, counterfactual-invalid, and
publication-invalid outcomes never publish and are never clamped. The pipeline
persists digest-bound failure evidence and delegates all attempt counting,
backoff, exhaustion, and suffix blocking to `work_accounting_schedule`.
Retrying creates the scheduler's next exact claim. There is no manual review or
override path.

Builder failure happens before an accounting subject can be formed and leaves
the lane at its prior `ready` state; a retry reuses the exact stored submission
and deterministic builder-request identity. This is formation recovery, not a
work-credit retry.

Corrections remain the scheduler's prospective state-repair events. This V1
orchestrator does not automatically replay a historical suffix. Any future
repair integration must preserve immutable prior artifacts and their
affected-history flags.

## 6. Activation boundary

The module and schema are inactive library foundations. Production activation
still requires a separately reviewed projection specification, runner/workflow
wiring, hosted provider adapter, production CAS implementation and retention
policy, operational metrics, and end-user presentation. None is introduced by
this change.
