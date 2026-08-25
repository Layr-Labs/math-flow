# Hierarchical research protocol v6 foundation

Status: inactive, opt-in runtime contract. No governed projection, hosted
workflow, scheduler, active knowledge lane, viewer, or accounting runner uses
this builder version.

Builder v6 is the first hierarchical research-builder contract over
`research-program-state-v2`. It joins accepted mathematical content to the
revisable program/thread topology defined by
`math_flow.research_topology`, without changing or migrating any published
builder-v1 through builder-v5 artifact.

The implementation in this version is deliberately provider-free. It is the
trusted reduction and handoff boundary that a later provider adapter must call;
it is not yet dispatched by `run_research_build_bundle`.

## Authority and entity roles

Math Flow's knowledge-state builder is the sole authority for the reference
portfolio. Contributors supply canonical submissions, and validity judgments
decide which declared claims are accepted. Neither contributors nor work
accounting propose the program/thread hierarchy.

The three entity kinds have different downstream roles:

- programs and research threads are work-accounting nodes;
- items are semantic/evidence leaves that represent accepted results, proofs,
  methods, computations, tools, questions, and dependency links; and
- contributions preserve immutable first-placement and judgment provenance for
  one canonical submission.

An item can move with stable identity when the builder revises the portfolio,
but that does not turn the item into a separately estimated accounting node.

## One exact state transition per accepted submission

`apply_research_builder_v6_transition` consumes exactly one accepted canonical
submission. Its transition binds:

- the exact `subjectTransactionId`;
- the exact state-v2 `baseStateDigest`;
- additive content operations;
- explicit topology operations;
- one complete contribution mapping and placement audit; and
- a non-empty topology rationale whenever topology changes.

The materialized post-state sets `ledgerHead` to that submission transaction and
`baseStateDigest` to the exact predecessor state digest. The result contains the
exact post-state, a reducer-derived topology alignment, and a same-world
handoff. A proposed transition cannot include an alignment field; the strict
envelope rejects one.

`apply_research_builder_v6_sequence` accepts caller-supplied canonical ledger
ordinals and requires an exact one-to-one, same-order transition list. It
materializes adjacent states sequentially. Judgment scheduling can still
coalesce a ready batch, but completion order cannot select formation order and
coalescing cannot collapse several accepted submissions into one accounting
subject.

Excluded submissions have no v6 state transition. A submission with at least
one accepted claim must have one transition and at least one durable item that
represents every accepted claim.

## Atomic content and topology composition

Content operations create or update full program, thread, and item records.
They must cite the current accepted submission, retain earlier provenance, and
may not hide a move, reparent, type change, lineage edit, or retirement.
Accepted claim dependencies must already exist in the exact predecessor state.

After the content state and contribution are valid, the adapter invokes the
existing `apply_research_topology_transition` reducer for any topology
operations. This permits:

- stable-ID program, thread, and item moves;
- program reparenting;
- explicit program and thread retirement;
- complete reciprocal program splits; and
- complete reciprocal program merges.

The topology reducer enforces stale entity guards, strict-tree and lifecycle
invariants, reciprocal append-only lineage, complete evacuation of retired
scope, and stable content/provenance during a move. The adapter then binds the
final composite state directly to the published predecessor, validates the
state again, and derives alignment across those exact adjacent states. The
intermediate content state is never a published knowledge state.

Topology-operation `baseDigest` values bind the trusted intermediate content
state. A future model-facing output adapter must derive or verify those guards
from trusted state; it must not treat a model's claimed digest or alignment as
authority.

## Deterministic alignment and same-world handoff

Every accepted submission produces an explicit
`research-program-topology-alignment-v1` artifact, including when no entity
moves. The alignment is subjectless and canonical: exact before/after state
digests plus sorted preserved, moved, split, merged, created, and retired
identity mappings determine its digest.

The per-submission `research-builder-same-world-handoff-v1` binds:

```text
subjectTransactionId
beforeKnowledgeStateDigest
afterKnowledgeStateDigest
topologyAlignmentDigest
sameWorldReferenceStateDigest = afterKnowledgeStateDigest
accountingNodeKinds = [program, thread]
semanticLeafKinds = [item]
handoffDigest
```

This makes the same-world rule executable: downstream work accounting must
estimate the submission against the builder's fully organized post-submission
portfolio, even when the submission caused new subprograms, a split, a merge,
or another topology revision. New scope in the after-state is therefore not
naively interpreted as work created by the submission. The handoff contains no
work estimate, probability, credit value, or allocation.

## Versioned components

- `math_flow/research_builder_v6.py` — provider-free sequential reducer and
  deterministic handoff validator;
- `protocol/judges/openrouter-hierarchical-research-builder-v6.json` — inactive
  organizer identity and policy;
- `protocol/profiles/hierarchical-research-v6.json` — inactive artifact profile;
- `protocol/schemas/research-program-submission-transition-v6.schema.json` —
  one-submission transition;
- `protocol/schemas/research-builder-same-world-handoff-v1.schema.json` — exact
  downstream handoff; and
- the existing state-v2, topology-transition-v1, and topology-alignment-v1
  contracts.

The judge loader recognizes these component identities so the inert spec is
self-validating. Projection governance intentionally does not allow builder v6
yet, and no projection spec references it.

## Activation seam

Activation is a separate change. It must not weaken the reducer to fit the
current batched provider runner. A complete activation should:

1. add a v6 branch to `run_research_build_bundle` and its bundle loader;
2. retain scheduling/coalescing while ordering accepted subjects by canonical
   ledger ordinal and invoking the v6 adapter once per accepted submission;
3. persist every raw proposal, trusted transition, exact post-state, topology
   alignment, and same-world handoff, rather than only one terminal batch state;
4. have the trusted output adapter populate or verify intermediate topology
   base digests and reject any model-authored alignment;
5. extend governed compatibility only for validity-v4 plus builder-v6 with no
   reconciliation stage;
6. teach publication and downstream accounting transport to bind the exact
   handoff/alignment artifacts; and
7. admit or edit a projection in the required separate one-file governed PR.

Until all seven steps are present, builder v6 remains provider-free and cannot
be selected by a governed projection. Historical builders and active
builder-v5 behavior remain byte-for-byte replayable.
