# Joint portfolio serial candidate V2

Status: inactive additive reducer milestone. Its registered judge adapters now
compose through a manual-only, publication-forbidden K1-K3 hosted holdout, but
it has no projection, scheduler, publication path, continuation, or viewer
integration and does not change an active lane.

## Purpose

V2 turns the successful K2 joint topology/live-work experiment into a bounded
serial state transition while preserving the established credit order:

1. bind accepted submission semantics, exact evidence, and a V10 local scope;
2. jointly author the local knowledge/topology change and the new live `W+`
   primitives;
3. reduce and freeze that exact post-state and `W+` once;
4. extract counterfactual-safe facts with submission evidence;
5. estimate `W-` without raw submission evidence or joint-judge rationales;
6. derive positive `D = W- - W+` in trusted code; and
7. allocate the complete value directly to the canonical submission.

The provider never authors `R`, `C`, `W`, `D`, node effects, percentages, or a
second with-access state.

## Semantic transition

The semantic packet binds the old state, accepted claims, evidence manifest,
root synthesis, and a canonical list of result changes. Result operations have
separate meanings:

- `create` creates an active result with accepted-claim provenance;
- `support` preserves title, statement, qualifications, dependencies, status,
  and placement while adding accepted support and provenance;
- `supersede` preserves the predecessor's semantic core, identifies one or
  more newly created active successors, and changes only lifecycle/provenance;
- `retire` preserves semantic core and successor links while changing only
  lifecycle/provenance.

A changed statement, qualification, dependency set, or meaning must use a new
result ID and explicit supersession. A supersession or retirement operation may
not attach the new accepted claim as proof of the old semantic statement. The
new claim must be represented by a created or support-refreshed result. Thus a
pruning submission can create a root-owned pruning result while retiring the
obsolete package and its old results.

Root-owned results are first-class. One result may also be shared by several
incomparable non-root programs through one primary owner plus related owners;
the reducer maintains one result identity and reciprocal membership rather than
duplicating it.

## Program and lifecycle transition

Scoped program operations are:

- `create`: a new active program;
- `refresh`: a semantic summary refresh with stable parent, including an
  explicit active-to-completed transition;
- `move`: a pure move that preserves program semantics, lifecycle, and
  provenance; and
- `retire`: a pure active/completed-to-retired lifecycle transition.

Root is synthesized in trusted code and remains active. Completion and
retirement require zero live direct work and zero non-root incidence in `W+`,
as enforced by the existing work-accounting reducer. The affected set always
contains root, every changed or result-owning program, and both the old and new
parent of a moved or inserted package. Every affected existing non-root program
must be in the exact V10 write scope.

V2 deliberately does not support program move plus semantic refresh in one
operation, intermediate-result placement moves, split/merge lineage, or
reopening a completed program. Those cases need separately versioned atomic
contracts rather than implicit multi-operation behavior. Until such a lineage
contract exists, any transition containing a program `retire` may contain only
other program `retire` operations: program creation, refresh, or move in the
same transition is rejected to prevent anonymous split/merge successors.
Multiple retire-only operations remain valid pure pruning. Result create,
supersede, and retire operations may accompany pure program retirement because
they cannot introduce or repurpose a program successor; this preserves the
root-owned pruning-result pattern above. A result shared
between root and a non-root program is also deferred because the inherited V7
placement audit permits root-only or incomparable non-root direct placements,
but not their mixture.

## Cumulative work-policy boundaries

`joint_portfolio_boundaries.py` stores exactly one digest-bound work-policy
boundary for every program:

- direct residual work scope;
- activation condition;
- stopping condition; and
- independent-variation rationale.

Each state binds the exact knowledge-state and ledger-head digests. A transition
must replace boundaries for the complete accounting-affected set. Trusted code
carries every unaffected boundary's text forward and rebinds it to the new
knowledge state. Missing, stale, duplicate, or tampered boundaries fail closed.

## Primitive and derived accounting quantities

The joint judge authors only the primitive state:

- `d_v = directWorkHours`: competent-human-researcher hours incurred at program
  `v`, conditional on activating it; and
- `P_{v|u} = conditionalIncidence`: the probability that child `v` is included
  or activated conditional on reaching its parent `u`.

Trusted code derives:

```text
R_root = 1
R_v = R_parent(v) * P_{v|parent(v)}
C_v = d_v + sum_child P_{child|v} * C_child
W = C_root = sum_v R_v * d_v
```

Here `R_v` is global reach probability and `C_v` is conditional subtree work.
They are not provider-authored aliases for incidence or direct hours. Every
affected program supplies a complete `d/P` assessment; unchanged primitives
outside the affected set are carried forward exactly.

Each assessment cites typed evidence: accepted claim, submission evidence,
prior program, prior result, or semantic-packet result. The reducer resolves the
ID/digest pair against authoritative inputs and rejects unresolved, duplicate,
or malformed references. Set-like response lists are sorted on a copied input
before validation; their order is not a model-authored semantic decision. This
includes program changes, placements, related owners, boundaries, assessments,
and evidence references. Sorting never removes duplicate rows or repairs missing
coverage, invalid scope, stale identities, or contradictory content. Canonical
reducer artifacts remain deterministic; the provider adapter separately retains
the original response and its order-sensitive digest.
Prior-program and prior-result references must also
belong to the exact V10 read set; global existence is not sufficient authority.

## Frozen W+ and credit

The V2 credit adapter re-reduces the joint response and seals a frozen candidate
binding the old/new knowledge states, old accounting and boundary states,
topology alignment, semantic and authoring packets, same-world handoff, `W+`
patch, and `W+` state. An optional expected candidate provides a replay guard
before any provider call.

Safe-fact extraction receives exact evidence. The no-access stage receives the
safe facts, structural impact context, old live state, frozen numeric `W+`, and
a digest-bound local work-policy context. Existing target nodes receive their
exact pre-contribution boundary (direct-work scope, activation, stopping, and
independent-variation policy). A target-only newly created package receives a
fixed generic policy explaining how to estimate its no-access inclusion and
work without importing the contribution's semantics. The context binds the
base boundary state, both knowledge states, the impact packet, every prior
boundary digest, and every target node digest.

The no-access request receives no raw evidence bytes, evidence manifest, joint
response, target boundary text, `W+` patch, or joint topology/accounting
rationales. Its distinct inactive profile and request digest bind the safe
policy context. Trusted materialization requires the reproduced with-access
state to equal frozen `W+`, rejects `D <= 0` without clamping, derives
conserving node effects, and assigns the value to the subject submission.

Every accepted claim reference must use the exact post-state contribution
judgment and `assessmentDigest = sha256(canonical accepted semantic claim)`.
This binds counterfactual inputs to the same per-claim assessment identity used
by the joint semantic transition instead of accepting any well-formed digest.

Node effects have one complete canonical schema and are uniquely ordered by
program reference. Trusted validation checks every primitive/derived field,
canonical decimal, difference list, direct branch, signed work reduction, and
knowledge-node binding. Given the two states and patches, it re-derives the
entire effect array byte-for-byte; rehashed explanatory substitutions are not
accepted.

A rejected nonpositive `W-` invalidates only its no-access checkpoint. The
evidence-bound safe-fact checkpoint and frozen `W+` remain reusable.

## Regression evidence and limits

Provider-free tests cover:

- K1 creation, an actual frozen successful K1 state/live-work fixture, and the
  exact successful hosted K2 two-result response;
- K2 creation of one independent program containing both theorem-chain results;
- K3 support refresh of both K2 results without new IDs or topology;
- root-owned and shared results;
- active-to-completed, solve/prune/retire, explicit supersession, and pure move;
- pure multi-program retirement while rejecting retire+create, retire+refresh,
  retire+move, and a fully rebound anonymous one-to-two successor split;
- cumulative boundary carry, typed evidence, complete affected-node `W+`, and
  exact preservation outside that set;
- stale state/accounting/boundary/semantic/scope bindings, evidence
  substitution, typed evidence outside the V10 read set, out-of-scope writes,
  lifecycle contamination, and boundary tampering; and
- frozen-candidate tampering, no-access evidence exclusion, nonpositive `D`,
  accepted-claim identity substitution, boundary-aware request surfaces,
  complete node-effect schema/replay, and checkpoint retry/replay;
- permutation-invariant reduction with exact raw-response preservation, and
  duplicate/missing/malformed rows remaining errors; and
- the three actual K1 responses from failed hosted run `33801731822`: the two
  root-free responses pass without a formatting retry, while the original root
  program change remains rejected with an explicit field-routing diagnostic.

The accepted K1 provider response itself was not checked into the repository,
so V2 can validate its frozen successful post-state and live-work artifacts but
cannot replay that missing response byte-for-byte. The K2 response is checked in
and replayed through the V2 reducer, reproducing `W+ = 4351.7375` hours.
The complete deterministic K2 V2 reducer output is additionally pinned by one
whole-object digest in the regression.

These tests establish reducer semantics, not judge quality. Prompt reliability,
semantic packet generation, long-context behavior, calibration, repeated-judge
variance, hosted continuation, and publication remain later milestones. The
manual hosted runner can collect one complete semantic sample under exact
request, token, price, cost, stage-order, and retry stops. Its merge does not
execute that sample; dispatch remains a distinct approval.
