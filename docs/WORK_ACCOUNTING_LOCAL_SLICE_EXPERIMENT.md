# Inactive Work Accounting local-slice experiment

This document records an additive, provider-free experiment aimed at the
full-state growth mechanism measured in
`docs/WORK_ACCOUNTING_CONTEXT_SCALE_EVALUATION.md`. It does not change active
Work Accounting V2, add a judge adapter, publish a projection, or authorize a
provider call.

## Contract under test

The complete accounting state remains authoritative and private to trusted
reduction code. `math_flow.work_accounting_local_slice` derives a prospective
model-facing packet from that state and the existing deterministic impact
context. The packet contains three accounting record classes:

1. **Exact writable nodes.** Every seed, descendant, sibling decision point,
   and other non-pure-ancestor program in the impact cut carries its exact base
   annotation digest, current `directWorkHours`, current
   `conditionalIncidence`, target knowledge digest, target parent, status, and
   included/boundary child identities.
2. **Ancestor aggregates.** A pure ancestor remains individually writable, so
   current sparse patches can still update it. It carries the same exact base
   primitives and guards, but all excluded child subtrees are represented by a
   summed conditional contribution rather than expanded annotations.
3. **Boundary aggregates.** Each excluded child subtree is represented by its
   target-topology root, parent, target knowledge digest, root base-annotation
   digest, incidence, exact conditional subtree work, conditional contribution,
   and program count. Internal programs and primitives are not exposed.

The entire packet binds the root contract, subject, evaluation mode, base
accounting state, before/after knowledge states, topology alignment, and impact
context by digest. Trusted application validates the packet, reconstructs it
from the complete global inputs, rejects any difference, validates the sparse
patch against its exact write scope and required primitive set, reduces the
local tree, applies the unchanged full-state V2 reducer, and requires both root
totals to be identical. It then requires local `W-`, `W+`, and `D` artifacts to
be byte-for-byte equal to the ordinary full-state materialization.

The no-access capacity experiment also constructs a measurement-only frozen
`W+` snapshot with the same cut and boundary aggregates. It is explicitly not
a live predecessor or activation API.

## Fail-closed rules

The experiment rejects:

- a stale base, knowledge, topology, impact, subject, or mode digest;
- any impact packet that is not the deterministic reconstruction from its
  seeds and descendant depth;
- a created, moved, or with-access inactive-zeroing node missing from the exact
  cut or from the patch's required primitive changes;
- duplicate or unknown program IDs;
- a patch update outside the exact included-node write scope;
- a boundary overlapping the writable cut, containing a new/unestimated node,
  using a stale parent or count, or changing even after its nested digests are
  recomputed; and
- a cut larger than its configured included-node or boundary-node bound.

There is no truncation fallback. A failed bound means that a future caller must
explicitly widen the cut, choose a different deterministic retrieval policy, or
stop.

## Deterministic replay matrix

The checked-in report runs six cases at 16, 64, 256, and 1,024 programs:

- one direct leaf update;
- a pre-expanded dependency-owner scope;
- a multi-node local sibling/work-package update;
- a topology move with required incidence re-anchoring;
- a decisive internal-subtree `W+` zero-out paired with a same-world positive
  `W-`; and
- a deliberately broad local subtree.

All 20 cases admitted by the default 128/256 bounds reproduce the complete
global `W-`, `W+`, and evaluation objects exactly. Four cases reject before
local reduction: dependency closure at 256 programs (129 included nodes),
dependency closure at 1,024 (257 included and 767 boundary roots), decisive
internal completion at 1,024 (64 included and 960 boundary roots), and broad
scope at 1,024 (65 included and 959 boundary roots). They are recorded as
explicit widening requirements with `truncated: false`.

The decisive-completion fixture marks an internal program and every descendant
completed. Through 256 programs, all required zeroing nodes fit and replay
exactly. A separate adversarial cut deliberately collapses those completed
descendants; construction rejects it because required primitive updates are
missing. The experiment does not authorize a semantic “zero this boundary”
shortcut. At 1,024 programs the complete descendant set is present, but the
surrounding sibling boundary count exceeds the configured bound, so the case
still stops rather than truncates.

At 1,024 programs, the full baseline accounting state is 448,514 compact JSON
bytes. Representative bounded results are:

| Case | Included | Boundaries | `W+` input slice bytes | Frozen-`W+` snapshot bytes | Full `W+` state bytes |
| --- | ---: | ---: | ---: | ---: | ---: |
| Direct | 33 | 31 | 40,695 | 38,938 | 448,667 |
| Multi-node subtree | 33 | 31 | 40,695 | 38,939 | 448,667 |
| Topology alignment | 67 | 30 | 62,774 | 59,469 | 448,638 |

Thus the 1,024-program bounded cases use about 9.1% to 14.0% of the full
baseline bytes for the `W+` slice, and about 8.7% to 13.3% of the full frozen
`W+` bytes for the measurement snapshot. Compact bytes divided by four are
reported only as a size proxy, not as provider-tokenizer measurements.
These are accounting-object comparisons, not complete future request sizes;
system/stage prompts, schemas, impact context, safe facts, and current evidence
would still have to be measured in a separately versioned request adapter.

Locality is not automatically smaller at every scale. Fixed schema and digest
overhead make some 16-program slices larger than the full state. At 256
programs the admitted broad-scope slice is 148,991 bytes and decisive-completion
slice is 151,275 bytes versus a 115,318-byte full baseline because 223–224
individual boundary aggregates cost more than the global annotation
representation. A future request path should compare the two exact encodings
and fail or choose the smaller authorized form; this experiment does not
introduce that policy.

## What this proves—and what it does not

The result proves that the current sparse primitive patch can be validated and
reduced from this local numeric cut while trusted code preserves and commits a
complete state, conditional on the deterministic impact cut containing every
patch target and required primitive update. It does not prove that the cut is
semantically sufficient. It covers direct, dependency, subtree, topology,
completion, and broad-scope deterministic fixtures, including two independent
seed branches, a moved subtree with unchanged collapsed descendants, and
adversarial stale, missing, duplicate, unknown, out-of-scope, and
rehashed-boundary mutations.

It does not prove:

- that an LLM can make equally good estimates from the slice;
- that the present impact router always selects the right semantic scope;
- that dependency owners should continue to be pre-expanded outside the impact
  builder;
- that the default 128/256 limits are the right production limits;
- a maximum legal request size or a model-tokenizer count; or
- compatibility with legacy program/thread knowledge states.

The experiment intentionally supports only program-only research state v3.
Ancestor depth, dependency closure, root-wide changes, and broad boundaries can
still grow. Those cases must widen or fail, never silently omit work.

The local boundary and cut reducers use iterative traversal and are exercised
on a synthetic 1,500-node chain. That is not a claim that upstream research
state validation, impact-context construction, or the unchanged full V2 global
reducer accepts adversarially deep trees; the full equivalence matrix uses the
valid widening fixtures through 1,024 programs. The checked-in topology fixture
and focused regressions cover a root-child move and a moved subtree with
collapsed unchanged descendants, but not every non-root cross-branch reparent
shape. That remains a useful property-test extension before activation.

## Reproduction

From the repository root:

```bash
PYTHONPATH=. python3 experiments/work_accounting_local_slice_probe.py \
  --output /tmp/work-accounting-local-slice.json
python3 -m unittest tests.test_work_accounting_local_slice
```

The generated report must exactly equal
`protocol/experiments/work-accounting-local-slice-v1/provider-free-report.json`.
