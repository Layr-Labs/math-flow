# Hierarchical Research Protocol v1

This protocol separates mathematical correctness, research-state formation, and
credit estimation. The stages share content only when the next stage needs it;
they do not share responsibility.

## Responsibilities

### 1. Primary validity judgment

The validity judge answers one question: does the submitted evidence establish
each declared claim with mathematical rigor?

It receives:

- the canonical problem statement;
- the current submission in full;
- earlier submissions explicitly cited as dependencies;
- the relevant accepted items, programs, and direct research lines selected
  from the latest pre-subject research state for those dependencies.

It does not receive the entire preceding contribution ledger automatically. It
may inspect as many intermediate proof obligations as correctness requires, but
the structured result preserves the contribution's declared claim identities.
It does not decide novelty, program placement, global state, or credit.

Claims marked `invalid` or `indeterminate` are not passed into research state.

### 2. Serialized research-program builder

The builder receives only claims marked `valid`, together with the submission,
its explicit dependencies, the validity report, and the previous accepted
post-state.

It:

- preserves the exact accepted claim statements and qualifications;
- separates durable results from proofs, methods, computations, tools, and
  questions;
- organizes those items into a strict tree of programs with explicit local
  objectives;
- maintains each program's ledger of future research threads and expected
  exposure;
- maps all accepted claims from one submission into one atomic contribution
  record, one direct program, and one local research line.

It does not rejudge truth. Invalid or indeterminate claims, and artifacts whose
only role is to record that a judgment occurred, are absent from the state.

Program topology and item ownership are stable in v1. A program has one credit
parent. Cross-program mathematical use is represented through item dependency
edges, not by giving an item a second allocation parent.

### 3. Immediate hierarchical credit update

After each accepted submission, the credit stage reevaluates:

- the submission at its direct program; and
- the affected child program at each ancestor edge.

Unchanged siblings retain their prior evaluations. The reducer recomputes local
shares and propagates them through the program tree. This makes the routine
cost local while preserving one score for every immediate child.

### 4. Retrospective credit refresh

A retrospective refresh reevaluates every immediate child at one common
hindsight horizon. It requires the complete serialized accepted history:

- every accepted submission in full;
- every validity report;
- every program-state delta and post-state digest;
- the final program state;
- stored historical reference ledgers for every credit child.

This is the broader, more expensive operation that corrects mixed-horizon
provisional scores.

## Serialized state

For accepted contribution `i`, the update stores one post-state `S_i` with
`baseStateDigest = digest(S_{i-1})`. Thus the pre-state is the preceding
post-state; no separately authored pre-state artifact is needed.

Invalid or indeterminate submissions do not create a research-state transition.
They remain available in their validity bundles but are absent from accepted
knowledge and credit.

Each active program has exactly one active `unstructured` thread. Every thread
stores `expectedExposure`, meaning expected future work actually spent on that
thread before the local objective is resolved under competent adaptive
continuation. It is not the nominal cost of pursuing the thread indefinitely.
Exposure and credit work values are relative work units interpreted locally to
the program; hierarchical shares are invariant to a common rescaling within a
program.

## Credit semantics

For child `x` at local program `v`, the evaluator constructs a matched
counterfactual at horizon `H`:

1. hold the realized underlying mathematical problem fixed;
2. remove `x` and information uniquely inherited from `x`;
3. retain independently available information;
4. allow a competent solver to adapt optimally.

The score is

`S_x = D_x + O_x = W_without_x(H) - W_with_x(H)`.

`D_x` is work avoided on the child's own local line, net of follow-up work.
`O_x` is exposure reduced on other threads that already existed in the child's
historical base ledger. The same work cannot appear in both terms.

The observed change between historical estimates,
`W_before - W_after`, is not credit. It also contains news about latent
difficulty. A negative result may increase the observed estimate of work
remaining and still receive positive causal credit.

At each program, immediate-child scores plus a non-negative unattributed
residual determine exact local shares. The deterministic reducer propagates
those shares down the strict program tree. Descendant value is not scored again
at ancestors.

## Context policy

The normal reference for prior accepted work is the research-program state.
Raw earlier submissions are included only when:

- the current submission explicitly cites them as dependencies; or
- a retrospective refresh requests the complete accepted trace.

This keeps routine validity and formation contexts bounded without depriving
the validity judge of premises or the retrospective evaluator of causal history.

## Workload

Let `N` be the number of submissions and `A` the number with at least one valid
claim.

- validity: `2N` calls, one rigorous report and one faithful claim-index extract;
- accepted state plus immediate credit: `2A` calls, one structured organizer and
  one structured local credit evaluation;
- final retrospective refresh: `1` call.

The total for a full replay is `2N + 2A + 1` calls. If all four canonical BSSC
submissions are accepted, the replay uses 17 provider calls.

## Deliberate simplifications

The v1 path does not carry forward the legacy knowledge/credit machinery merely
for compatibility. In particular it has:

- no reconciliation stage between primary judgments;
- no batch knowledge-formation claim or scheduler format;
- no event-shaped knowledge nodes or immutable revision ledger inside state;
- no split, merge, move, or reparent operations for program topology;
- no qualitative significance labels, contributor roles, reservation overlays,
  or independent credit projection;
- no per-claim credit children for a multi-claim submission;
- no separately authored pre-state snapshot;
- no migration adapter for old knowledge or credit projections.

Legacy code remains available for existing governed projections, but none of it
is an input to this new replay path.

## Commands

Run one validity judgment with the previous accepted state as bounded context:

```text
math-flow judgment --problem PROBLEM --judge protocol/judges/openrouter-validity-judgment-v2.json --head TRANSACTION --subject TRANSACTION --research-state-run PREVIOUS_RUN --output-dir VALIDITY_RUN
```

Apply one accepted contribution:

```text
math-flow research-update --problem PROBLEM --judge protocol/judges/openrouter-hierarchical-research-v1.json --head TRANSACTION --validity-bundle VALIDITY_RUN --base-run PREVIOUS_RUN --output-dir RESEARCH_RUN
```

Refresh all credit at a common horizon:

```text
math-flow research-credit-refresh --problem PROBLEM --judge protocol/judges/openrouter-hierarchical-research-v1.json --latest-run LATEST_RUN --history-run RUN_1 --history-run RUN_2 --output-dir CREDIT_REFRESH
```

Replay a complete canonical ledger and perform the final refresh:

```text
math-flow research-replay --problem PROBLEM --validity-judge protocol/judges/openrouter-validity-judgment-v2.json --research-judge protocol/judges/openrouter-hierarchical-research-v1.json --output-dir OUTPUT
```
