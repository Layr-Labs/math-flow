# Hierarchical Work-Remaining Accounting Policy V1

Status: additive, inactive protocol foundation. This policy does not alter or
replace any registered knowledge or credit projection.

## 1. Objective and subject

The sole credit subject is one canonical accepted submission transaction `x`.
Its raw work value is

\[
D(x)=W(S_x^-)-W(S_x^+),
\]

where `S_x^-` is the same-world continuation without actionable access to the
submission and `S_x^+` is the continuation with access to it. Both continuations
are evaluated in the world revealed by the accepted submission. A submission
may change estimates at many nodes, but receives one global value. Programs,
threads, and mathematical items do not receive independent submission credit.

V1 requires `D(x) > 0`. Deterministic code must reject a zero or negative result;
it must not clamp the value to zero or a positive epsilon. A failed estimate may
be retried by a later runner, but no state transition is published from the
invalid pair.

## 2. Authoritative portfolio

The Math Flow knowledge-state builder owns the reference portfolio. Community
submissions supply raw mathematical work; the builder decides how accepted work
is organized into programs, subprograms, threads, and items. Work accounting
must not author an independent portfolio or change knowledge topology.

V1 accounting nodes are exact references to builder-owned programs and research
threads:

- programs form the structural hierarchy and may carry direct coordination,
  integration, planning, verification, or undecomposed residual work;
- every thread is a leaf beneath its exact builder-owned program and may carry
  direct concrete work;
- mathematical items remain semantic and evidentiary anchors. They are not
  accounting nodes or credit subjects.

Every annotation binds the exact digest of its program or thread record. Every
state binds the exact builder-owned knowledge-state digest and ledger head.
Accounting records store no parent or owner field. The reducer derives program
parentage and thread ownership from the supplied knowledge state.

## 3. Root and unit contract

Each accounting lane has an immutable root contract binding:

- the problem and governed knowledge projection;
- the root objective and terminal condition;
- the reference-community definition and researcher qualification;
- the fixed conventional tool baseline; and
- the unit definition.

V1 uses one **competent human researcher hour**:

> One focused person-hour of research by a researcher qualified for the
> relevant work package, using the fixed conventional tool baseline named by
> the root contract.

This is additive person-time, not elapsed time. Parallel work by several people
adds their hours. The contributor may be a human, an LLM, or a mixed system; the
accounting unit does not change. A change to the conventional tool baseline or
unit definition requires a new versioned root contract or profile.

## 4. Primitive and derived quantities

For every accounting node `v`, `d_v` is direct residual work conditional on the
node becoming active. It excludes descendant work and all sunk work.

For every non-root node `u` with builder-owned parent `v`, `P_{u|v}` is the
conditional probability that `u` becomes active before the root program reaches
its terminal condition, given that `v` is active. It is incidence of work, not
probability of full completion. Sibling probabilities need not sum to one.

The reducer computes, using exact finite-decimal arithmetic:

\[
R_{root}=1, \qquad R_u=R_vP_{u|v},
\]

\[
C_v=d_v+\sum_{u\in child(v)}P_{u|v}C_u,
\]

and

\[
W=C_{root}=\sum_vR_vd_v.
\]

The equality is a mandatory invariant. `R`, `C`, expected direct work, total
`W`, and `D(x)` are reducer-authored fields. A model patch containing any of
these fields is invalid.

All V1 primitive values are canonical non-negative finite-decimal strings.
Incidence lies in `[0,1]`. Completed and retired knowledge nodes have zero direct
work and zero non-root incidence.

## 5. Progressive knowledge and the same-world comparison

Observed growth in the builder hierarchy is not an increase in work caused by
the current submission. For each accepted submission:

1. Freeze the prior live accounting state and its exact knowledge binding.
2. Obtain the builder-owned post-submission knowledge state.
3. Use a deterministic, builder-derived topology alignment when program or
   thread identity, parentage, or ownership changes.
4. Construct `S_x^-` on the new coordinate system. Newly explicit work is
   represented according to whether and how the no-access community would have
   discovered and incurred it in the realized world.
5. Construct `S_x^+` on the same coordinate system with actionable access to
   the accepted submission.
6. Derive both totals, require strict positivity, and commit only `S_x^+` as the
   next live accounting state.

The no-access state is immutable audit evidence but never a live predecessor.
The evaluator may know safe facts revealed by the submission; the
counterfactual community may not use its actionable content. Enforcement of
that epistemic firewall belongs to the later context/request-builder layer.

## 6. Sparse primitive patches

A no-access patch and a with-access patch share the following exact identity:

- problem and submission transaction;
- immutable root-contract digest;
- base accounting-state digest;
- base and target knowledge-state digests; and
- optional builder-derived topology-alignment digest.

Each node update contains only a typed program/thread reference, an optimistic
base-annotation digest, changed primitive values, a rationale, and evidence
references. New nodes require complete `d` and `P` estimates. A node whose
builder-owned parent or owner moved requires a newly anchored `P` estimate.
Nodes absent from the target builder state cannot be patched.

The reducer rejects stale base guards, duplicate updates, missing new-node
estimates, unexplained topology changes, unsupported fields, and ordinary no-op
updates. Derived values are always discarded and recomputed by construction;
they are not a provider interface.

## 7. Submission ordering and publication

Canonical first-parent submission order determines accounting order. Hosted
formation or provider batching has no credit meaning. A run may package several
subjects operationally, but it must construct a virtual sequence in canonical
order and give each submission its own predecessor, counterfactual pair, work
value, and committed with-access state.

A live state records the ordered submission transactions already processed.
The reducer rejects a repeated subject. A later scheduler must additionally
reject gaps and prove that the claimed sequence is the exact eligible canonical
prefix before publication.

There is no manual review gate in V1. Invalid model output is handled by bounded
automated retry outside this pure reducer. Exhaustion fails closed and does not
advance the accounting state.

## 8. Topology revisions

Topology alignment is a builder-derived input, not a work-accounting decision.
It binds exact before/after knowledge states and their record lineage. Moves and
reparenting preserve stable identity; splits and merges use explicit builder
lineage; creation and retirement are reported rather than inferred from prose.

The accounting evaluator then reasons counterfactually on the revised topology:

- a move carries direct work but requires incidence to be re-anchored;
- a split distributes or re-estimates predecessor work without duplication;
- a merge deduplicates predecessor work;
- a new node receives no-access and with-access estimates rather than being
  treated as work created by the submission; and
- a retired branch can retain positive no-access incidence while having zero
  with-access incidence where the submission prunes it.

The current reducer verifies the exact alignment digest and state bindings. Full
semantic validation of split/merge lineage belongs to the builder topology
reducer that authors that alignment.

## 9. Immutability and corrections

Ordinary later research does not re-estimate or overwrite earlier `D(x)` values.
New submissions update current primitive estimates prospectively; deterministic
recalculation and builder topology revisions leave prior immutable evaluations
unchanged. A model, policy, unit, or schema change creates a new governed lane
rather than rewriting an old one.

Prior-credit correction is deferred beyond this foundation. The intended form
is an append-only object naming the superseded evaluation and one of:

- a replacement strictly positive evaluation; or
- `void`, for an evaluation whose accepted basis was retracted or invalid.

Correction candidates include validity reversal, incomplete or misbound
evidence, reducer defects, and invalid topology lineage. V1 does not silently
replay and rescore the historical suffix. A later policy must decide whether a
correction repairs only the current live state while flagging affected later
evaluations, or creates a distinct suffix-replay lane.

## 10. V1 boundary

This foundation provides point estimates only. It deliberately excludes
uncertainty intervals, Monte Carlo propagation, aliases and multi-parent
accounting, structural probability templates, resource vectors, critical-path
time, payout percentages, money, governance weight, and manual review.

It also does not implement provider prompts, the no-access evidence firewall,
scheduling, publication, viewer presentation, or projection activation. Those
surfaces require separately versioned changes and must preserve all active and
historical credit artifacts.
