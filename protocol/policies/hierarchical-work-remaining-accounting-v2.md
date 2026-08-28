# Hierarchical Work-Remaining Accounting Policy V2

Status: additive protocol foundation. V2 does not change or reinterpret any V1
bundle. Activation requires a separately governed projection lane.

## 1. Subject, states, and value

The sole credit subject is one accepted canonical submission transaction `x`.
For its exact post-builder topology, V2 defines:

- `W+`: remaining work when the reference community receives actionable access
  to `x`. This is the candidate next live accounting state.
- `W-`: remaining work in the same realized world when the evaluator withholds
  actionable access to `x` from the counterfactual community.
- `D(x) = W- - W+`: the submission's work value.

`W+` and `W-` are states, not the node quantities `R_v` and `C_v`. At every
accounting node `v`, `R_v` remains global reach probability and `C_v` remains
conditional subtree work.

V2 requires `D(x) > 0`. Trusted code rejects zero or negative results without a
clamp, epsilon, manual override, or mutation of `W+`.

## 2. Portfolio, unit, and primitives

The Math Flow knowledge builder owns the exact program/thread portfolio and its
post-submission topology. Submissions do not author an accounting hierarchy.
Programs and research threads are accounting nodes; mathematical items are
semantic evidence anchors, not independent accounting nodes or credit subjects.

The unit remains one competent-human-researcher hour under the immutable root
contract. The only provider-authored primitives are:

- `d_v`, direct residual work conditional on node activation; and
- `P_{u|v}`, conditional work incidence for a non-root child.

Trusted finite-decimal reduction computes:

\[
R_{root}=1,\qquad R_u=R_vP_{u|v},
\]

\[
C_v=d_v+\sum_{u\in child(v)}P_{u|v}C_u,
\]

and

\[
W=C_{root}=\sum_vR_vd_v.
\]

Both branch patches are sparse primitive patches from the same old live state,
aligned to the same post-submission topology. `W-` is not produced by patching
`W+`. This preserves a common stale-guarded base and avoids hiding branch
differences inside a derived-state mutation.

## 3. A-first estimation order

For an adjacent accepted transition, trusted execution performs this exact
order:

1. Validate the old live accounting state, old and new knowledge states,
   topology alignment, accepted claims, and complete submission evidence.
2. Extract and validate counterfactual-safe facts.
3. Give the with-access estimator the old live state, the post-submission
   topology context, and the complete verified submission.
4. Validate its sparse patch against the old live state and materialize `W+`.
5. Freeze a content-addressed candidate containing the exact request, response,
   patch, and reducer-authored `W+` state. Reproduce the state from the bound
   patch before the candidate is reusable.
6. Give the no-access estimator the old live state, safe facts, bounded
   program/thread context, and the numeric frozen `W+` state. Do not provide the
   `W+` patch rationale/evidence or raw submission evidence.
7. Validate its direct sparse `W-` patch against the same old live state,
   materialize both branches, reproduce the frozen `W+` exactly, and compute
   `D(x)`.
8. Commit only `W+`. Preserve `W-` and the evaluation as immutable audit
   evidence.

The no-access estimator cannot modify `W+`. Its request digest binds the full
frozen numeric state and frozen-candidate digest. Its output schema contains
only sparse `d/P` updates.

## 4. Epistemic policy

V2 separates evaluator knowledge from actor knowledge.

- The with-access evaluator and actors receive the exact submission.
- The no-access evaluator may inspect the frozen numeric `W+` state and
  validated safe facts because it evaluates the realized same world.
- The no-access evaluator receives no raw submission bytes, evidence manifest,
  evidence chunks, raw claim statements, item-bearing alignment, or `W+` patch
  rationales/evidence.
- Counterfactual actors do not receive or use `x`. They may adapt under the old
  information policy until independent discovery of the withheld facts.

Structural byte and field guards enforce the machine-checkable part of this
boundary. Prompt/model governance remains responsible for modeling actors who
do not know the solution even though the evaluator sees its numeric
consequences.

## 5. Live-state authority and retries

Accuracy of `W+` has priority because it is the sole state consumed by future
submissions. Once its candidate passes semantic validation, credit estimation
cannot regenerate, tune, or trade it against a desired `D(x)`.

If a `W-` response is structurally invalid, semantically invalid, or produces
`D(x) <= 0`, trusted execution invalidates only that no-access response. A retry
reuses and fully revalidates the exact frozen `W+` candidate, then re-estimates
only `W-`. No numeric difference or positivity diagnostic is fed back into the
with-access stage. Retry exhaustion fails closed and does not advance the live
state.

The stable candidate identity includes the root contract, old live accounting
state, old and new knowledge-state digests, topology alignment, submission
manifest/digest, accepted-claim identities, context depth, and exact
with-access request/response/patch/state.

## 6. Inactive nodes and topology revisions

Completed and retired nodes must have zero direct work and non-root incidence
in committed `W+`. They may retain positive values in ephemeral `W-` when the
counterfactual community would still pursue the work before independently
discovering the result that completed or retired it.

Topology alignment remains builder-authored. New, moved, split, merged, or
retired nodes are evaluated in one post-topology coordinate system. V2 does not
permit the accounting estimator to author topology.

## 7. Local-anchor compatibility

V2 directly estimates an absolute sparse `W-` patch in its first implementation.
Local anchor operations can later compile to differences between the frozen
`W+` primitives and a direct `W-` patch—for example direct speedup, branch
pruning, or incidence change. Anchors must remain explanations or typed patch
constructors. Trusted code still performs one global reduction so overlapping
subtrees are not credited twice.

Introducing typed anchors, structural probability templates, uncertainty, or a
delta-from-`W+` provider output requires a later version. V2 itself retains V1
point estimates, state schema, primitive patch schema, and deterministic
hierarchical reducer.
