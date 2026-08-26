# Hierarchical research protocol v6 foundation

Status: inactive, opt-in runtime contract with a bundle runner and a
provider-free BSSC serial-producer implementation. No governed projection,
active hosted workflow, scheduler lane, or viewer uses this builder version.

Builder v6 is the first hierarchical research-builder contract over
`research-program-state-v2`. It joins accepted mathematical content to the
revisable program/thread topology defined by
`math_flow.research_topology`, without changing or migrating any published
builder-v1 through builder-v5 artifact.

The trusted reducer is provider-neutral. `run_research_build_bundle` now has an
inactive v6 branch that calls the governed provider adapter and publishes one
fully replayable bundle per accepted submission. Projection admission remains
separate.

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
materializes adjacent states sequentially. The bundle runner accepts exactly
one validity judgment with at least one accepted claim. Scheduling can discover
many ready judgments together, but it must publish one accepted submission at a
time; completion order cannot select formation order or collapse several
accepted submissions into one accounting subject.

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
- `protocol/schemas/research-builder-submission-input-v1.schema.json` — the
  accepted claims, judgment, ordinal, and manifested-evidence binding needed to
  replay that transition;
- `protocol/schemas/research-builder-same-world-handoff-v1.schema.json` — exact
  downstream handoff; and
- the existing state-v2, topology-transition-v1, and topology-alignment-v1
  contracts.

The judge loader and projection compatibility validator recognize these
component identities, so an inactive candidate can be checked before admission.
No registered projection references builder v6.

The BSSC deployment foundation adds
`math_flow.bssc_research_v4_producer`, the immutable validity source at
`protocol/runtime/bssc-research-v4-validity-source-v1.json`, and the
manual-dispatch hosted caller `.github/workflows/project-research-v4-serial.yml`.
The planner revalidates the exact historical validity-v4 bundle bytes, the
canonical 16-subject accepted frontier, and the published v6 predecessor chain
before allowing one next build. See `docs/BSSC_RESEARCH_V4_SERIAL_PRODUCER.md`.

## Activation seam

The hosted caller and active runtime candidate now supply the one-submission
formation boundary. Final activation requires the separate governed admission
of the byte-identical projection, after which the caller may be dispatched.
The deployment:

1. schedule each accepted subject in canonical ledger order and invoke the v6
   runner once from its exact predecessor; excluded submissions produce no
   knowledge bundle;
2. publish the stored proposal/transition, predecessor and post-state,
   reducer-derived topology alignment, and same-world handoff atomically;
3. teach downstream accounting transport to consume the exact published
   handoff/alignment artifacts instead of independently authoring topology;
4. uses the hosted serial resume/publication caller and v6 viewer support; and
5. admit the projection in the required separate one-file governed PR.

Until the one-file admission is merged, the caller fails closed and builder v6
cannot be selected by a registered projection. Historical builders and active
builder-v5 behavior remain byte-for-byte replayable.
