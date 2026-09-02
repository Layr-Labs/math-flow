# Joint portfolio serial candidate V1

Status: inactive local candidate. It has no judge registration, projection,
workflow, CLI command, publication path, or viewer integration.

## Purpose

This candidate generalizes the successful K2 joint-topology experiment into an
adjacent serial transition that can be replayed from arbitrary valid knowledge
and live work-accounting states. It keeps topology formation and the new live
work state, W+, in one bounded judgment, then completes credit accounting with
the existing counterfactual safe-facts and no-access machinery.

The intended order is:

1. deterministically bind the current submission semantics and local routing
   scope;
2. jointly author the local program/result changes and full W+ assessments for
   root plus every changed program;
3. reduce those changes and derive the sparse W+ primitive patch in trusted
   code;
4. freeze that exact joint transition and W+ state;
5. extract safe facts with current submission evidence;
6. estimate W- without raw submission evidence or joint-judge rationales;
7. derive D = W- - W+ and the node-effect explanation in trusted code; and
8. allocate D directly to the subject submission.

There is no second with-access estimation. W+ is authoritative exactly once.

## Transition boundary

`math_flow/joint_portfolio_serial_transition.py` defines two inputs around the
joint provider boundary.

The fixed semantic packet binds:

- the old knowledge-state digest;
- the accepted-claims digest;
- the exact evidence-manifest digest;
- the root synthesis after the submission; and
- every intermediate-result creation or refresh, including exact base guards,
  final semantic fields, support additions, dependencies, and accepted claim
  keys.

The V10 authoring packet is reducer-derived and binds the local read and write
scope. The response must bind both packet digests and both old-state digests.
It may create, refresh, or move only scoped programs, place every fixed result,
state a work-policy boundary for each changed program and root, and assess W+
for root and every changed program.

Trusted reduction then:

- appends result evidence and provenance;
- derives reciprocal program membership;
- applies stale-guarded V10 content and topology operations;
- builds the topology alignment and same-world handoff;
- converts full local W+ assessments into only the primitive changes actually
  needed; and
- derives global reach `R`, conditional subtree work `C`, and total `W` from
  the authored direct residual work `d` and conditional edge incidence `P`.

Programs outside the exact write scope cannot be changed. Existing primitives
outside the assessed local set are carried forward unchanged. The K3 contract
is an exact in-place refresh: the response names the prior result and program
digests, retains their IDs and placement, appends the new submission's evidence
and provenance, and creates no duplicate program or result.

V1 intentionally rejects a semantic refresh and placement move of the same
result in one transition. That case needs a separately designed atomic move
contract rather than an implicit relaxation.

## Frozen W+ and counterfactual credit

`math_flow/joint_portfolio_serial_credit.py` re-reduces the exact joint response
before any counterfactual call and seals a frozen candidate that binds:

- root contract;
- old and new knowledge states;
- old accounting state and topology alignment;
- joint response, semantic packet, authoring packet, and reduced transition;
- same-world handoff; and
- W+ patch and W+ state.

An optional expected frozen candidate provides an external replay guard. A
different but internally rehashed response, packet, scope, transition, or W+
state is rejected before a provider call.

Safe-fact extraction receives the exact current evidence. The W- request
receives the safe facts, structural impact context, old live accounting state,
and frozen numeric W+ state. It does not receive raw evidence bytes, the
evidence manifest, the joint response, the W+ patch, or joint topology/W+
rationales. Evidence and claim digests remain in authoritative request bindings;
they identify the subject without revealing its body to the no-access judge.

The existing Work Accounting V2 patch reducer materializes W- and reproduces
the frozen W+ state. Trusted code rejects D <= 0; it does not clamp or repair a
nonpositive judgment. Trusted code also derives node effects and requires their
sum to equal D exactly. The sole allocation target is the subject submission,
not an intermediate result or program.

Checkpoint keys include the full stage request digest. A failed nonpositive or
otherwise invalid W- result invalidates only the no-access checkpoint; the
evidence-bound safe-facts result remains reusable. A successful exact replay
requires no provider calls.

## Provider-free regression surface

`tests/test_joint_portfolio_serial_transition.py` and
`tests/test_joint_portfolio_serial_credit.py` cover an ordered synthetic
K1/K2/K3 sequence:

- K1 creates one result-owning root-child work package.
- K2 creates a distinct root-child work package whose activation/stopping
  decision is independent, even though its result mathematically depends on
  K1 evidence.
- K3 strengthens K2 in place, preserving the exact program/result identity and
  placement while appending evidence and provenance.

The tests also cover stale response bindings, rehashed evidence substitution,
out-of-scope program writes, duplicate-result replacement, frozen-candidate
tampering, raw-evidence exclusion from W-, strict positive D without clamping,
node-effect conservation, and checkpoint invalidation/replay.

These fixtures demonstrate reducer and boundary invariants. They do not test
model quality, prompt reliability, long-context behavior, repeated-judge
variance, or publication/generation replay. A hosted miniature and then a
governed versioned projection remain separate activation milestones.
