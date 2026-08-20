# Hierarchical Research Protocol v2

> **Superseded historical design.** This document records the immutable
> validity-v2/builder-v2 semantics of `openrouter-research-v1`. The preferred
> replacement production lane is `openrouter-research-v3`; v1/v2 remain
> temporarily active comparison lanes during retirement. See
> `HIERARCHICAL_RESEARCH_PROTOCOL_V4.md`. The historical identities and command
> examples below are intentionally not rewritten.

The default `openrouter-research-v1` projection now separates three concerns:

1. parallel primary judgments decide mathematical validity;
2. a dependency-safe batched builder organizes accepted knowledge; and
3. hierarchical two-term credit remains a downstream, ex-post operation.

The v1 serialized replay remains available as a reference and test path. It is
not the production scheduling topology.

## Primary validity judgment

`openrouter-validity-judgment-v2` receives one contribution, its declared
claims, the raw submissions explicitly named as dependencies, and the smallest
pre-subject research-state slice representing those dependencies. Its only
normative job is conservative mathematical verification. It may inspect as many
proof obligations as necessary, but it returns one structured assessment per
declared claim so claim identity remains stable.

Validity judgments have no mutable base state and may run in parallel. Their
completion order does not determine research-state order.

## Batched research-state formation

`openrouter-hierarchical-research-builder-v2` consumes a leased set of
validity-v2 judgment bundles plus the current hierarchical research-program
state. It also reads the original content of every accepted submission so it can
separate results from proofs, methods, computations, tools, and questions and
can record use of prior accepted work.

The builder does not decide truth. Claims marked `invalid` or `indeterminate`
are not sent to the organizer and are absent from the research state. If no
claim in a leased batch is valid, the run records that the input judgments were
processed without making a provider call or changing the state artifact.

One structured delta covers the whole accepted batch. Each accepted submission
maps atomically to:

- every accepted claim key;
- one direct local program;
- at least one direct local research thread; and
- at least one durable item representing its accepted claims.

Every changed entity cites at least one accepted submission from the batch.
Dependencies must already be represented in the base state or be accepted in
the same batch.

## Dependency-safe batching

The scheduler persists a content-addressed judgment dependency graph derived
from validity dependency packets. When both a submission and a submission it
depends on are pending, their connected component is claimed as one indivisible
formation batch. A component larger than the governed maximum is rejected
rather than split across inconsistent post-states.

Independent judgments can complete and publish concurrently. Formation remains
optimistically serialized by the existing lane lease and base-run chain. A
stale competing formation cannot silently become the lane tip; publication and
the durable wake-up planner force it to replan from the current base.

Batching therefore reduces state-builder work from one call per accepted
submission to one call per claimed accepted batch. Primary validity still costs
two calls per submission: one rigorous audit and one faithful structured
extraction.

## Program topology

Programs remain strict-tree local objective and credit contexts. The v2 reducer
keeps existing program parents, thread ownership and kind, and item program and
type stable during ordinary formation. This is a versioned operational
restriction, not a claim that the current tree is permanent or that programs
exclusively own all mathematically relevant work. Cross-program use is recorded
through item dependencies. A future governed builder version may add atomic
split, merge, move, and reparent operations after their interaction with credit
has been evaluated.

## Credit boundary

The state builder records contribution-to-program and contribution-to-item
links but does not estimate credit. The independent
`openrouter-research-credit-v2` overlay applies the two-term hierarchical policy
locally at each program:

`credit = direct work avoided + other pre-existing local work obviated`.

This is a matched hindsight counterfactual given what is known at the evaluation
horizon. It is not the historical difference between pre- and post-submission
estimates of remaining work. A negative result may increase the latter while
still reducing counterfactual work.

The overlay locks one exact `research-program-state`, walks its immutable
`baseRun` chain, and recovers the first build in which every contribution or
child program appeared. Contributions accepted in one formation batch share
the same historical base and post state; a unique post state per submission is
not required. The credit judge receives:

- the current program state as the common hindsight horizon;
- every accepted submission's original content and exact valid claim records;
- the complete accepted formation trace and provenance links;
- each child's direct local thread IDs; and
- that child's pre-existing local thread ledger at first appearance.

Invalid and indeterminate claims are absent. The model returns direct and
obviated work effects plus an unattributed local residual. Trusted reduction
checks exact child and thread coverage, preserves the historical snapshots,
computes local shares, and propagates them through the strict program tree.
Every refresh recomputes all credit-bearing programs at one horizon; it does
not retain stale sibling scores from a prior credit state.

Credit scheduling is independent of primary judgment and research-state
formation. The default overlay has a one-hour rolling minimum interval, so
several state advances may coalesce into one broader retrospective evaluation.
It never serializes or delays primary validity judgments.

## Production command path

The existing hosted commands remain the production interface:

```text
math-flow judgment ...
math-flow knowledge-trigger ...
math-flow knowledge-claim ...
math-flow knowledge-build ...
math-flow knowledge-complete ...
math-flow credit --projection openrouter-research-credit-v2 ...
```

`knowledge-build` dispatches by the governed builder implementation. Legacy
builders retain their existing behavior; the hierarchical v2 builder produces a
`knowledge-build` run containing `research-batch-input`,
`research-program-delta`, and `research-program-state` artifacts.

The credit command uses the existing governed overlay workflow. Its
`credit-assignment` bundle contains the exact dependency lock, accepted history,
original submission evidence, historical local contexts, raw credit delta, and
the deterministic `hierarchical-credit-state`. The viewer catalog exports these
runs separately as `hierarchicalCreditProjections`; they are not coerced into
the legacy qualitative assignment format.
