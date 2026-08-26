# Inactive Hosted Work-Accounting Dispatch V1

## Status and boundary

This surface is **inactive**. It adds no projection admission, scheduled trigger,
manual trigger, provider call, mutable object-store implementation, or publication
permission. The reusable workflow has only `workflow_call`, `actions: read`, and
`contents: read`; it receives no secrets. It can produce a dispatch authorization
or a prepublication recheck, but it cannot execute or publish one.

The executable identities are governed by
`protocol/runtime/inactive-work-accounting-hosted-v1.json`. The loader verifies the
content digests of the builder-v6 judge, work-accounting judge, provider transport,
and pipeline runner. The config is itself content addressed and hard-coded as
inactive. Changing any governed implementation requires a new, coherently resealed
config rather than a mutable model alias or implicit runner change.

## Canonical serial frontier

A validity service may finish submissions in parallel. Work accounting may not.
The disposition snapshot therefore covers every contribution in exact canonical
ledger order and uses one of `pending`, `accepted`, `rejected`, or `indeterminate`.
The planner selects the first accepted transaction not already represented by the
pipeline's completed canonical accepted prefix. It authorizes that transaction only
after every earlier ledger transaction has a terminal validity disposition.

Every workflow call targets the full 40-character subject transaction. A requested
subject that is not the calculated frontier is rejected. The eligible authorization
also binds:

- canonical head and problem-ledger digest;
- projection head and projection-state digest;
- pipeline, schedule, and validity-snapshot digests;
- exact accepted submission input and judgment identity;
- predecessor knowledge and accounting states;
- builder, work estimator, transport, runner, and runtime-policy identities.

Thus parallel validity completion changes latency but not accounting predecessor
order. One authorization always represents exactly one accepted submission `x`.

## Automatic recovery

There is no manual review path. The existing pipeline owns compare-and-swap lane
claims, immutable checkpoints, exact patch application, and crash resumption. The
hosted planner adds an independent run-history gate:

- an active run with the exact semantic dispatch key suppresses duplication until
  its governed claim lease expires;
- an expired active claim is counted as a failed attempt and recovered automatically;
- failed, cancelled, or timed-out runs retry automatically with bounded exponential
  backoff;
- a successful hosted run that did not advance the governed lane is treated as a
  stale success and is automatically recovered after backoff;
- an existing pending pipeline transition is resumed for the same exact subject;
- exhausted scheduler or hosted retry budgets fail closed, with no manual override.

`semanticDispatchKey` excludes the hosted batch limit. Batching is only an
operational cap on how many serial authorizations a future caller may process in one
hosted run. Each subject is still planned, executed, rechecked, and committed
separately; batching cannot change work estimates, predecessor states, or credit.

## Trusted transport and publication boundary

Submission/model data is never interpolated into shell source. Reusable-workflow
inputs enter fixed environment variables, are written as inert JSON bytes, and are
validated by the Python contract. The workflow exposes no model/API secret. A
future active caller may pass a provider secret only to the trusted governed
transport step, never to discovery, planning, checkout, artifact assembly, or
publication steps.

Immediately before publication, the caller must fetch the live canonical and
projection refs and invoke `work-accounting-prepublish-check` with freshly resolved
pipeline, schedule, disposition, and projection state. Publication is allowed only
when every original binding and the semantic dispatch key are unchanged. Any head,
state, subject, validity artifact, predecessor, or lane movement discards the model
result. The production CAS adapter must still perform its normal conditional write;
this recheck does not replace compare-and-swap.

## Activation seam

After builder-v6 and work-accounting projections are separately admitted, the
production projection-branch store is deployed, and provider spend is approved,
hosted triggering requires one new active caller workflow. That caller should:

1. fetch and verify current canonical/projection state;
2. construct the complete disposition snapshot and hosted run history;
3. invoke `work-accounting-dispatch-contract-v1.yml` for an exact subject;
4. call the governed pipeline through the trusted transport boundary only when the
   plan is eligible;
5. invoke the same contract with `operation: prepublish` using freshly fetched state;
6. publish through the production CAS adapter only when the recheck is publishable;
7. repeat serially up to the operational batch cap, replanning after every commit.

No existing active workflow or projection registry entry should be changed merely
to land this inactive foundation. Admission and the one-file caller are explicit,
reviewable later changes.
