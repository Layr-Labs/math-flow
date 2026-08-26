# Hierarchical research topology foundation v1

Status: additive provider-free runtime foundation. No governed judge, profile,
projection, hosted workflow, or active lane uses these contracts yet.

This foundation defines how a future Math Flow knowledge builder can revise the
authoritative research-program portfolio without changing the meaning or replay
behavior of published hierarchical research v1-v5 artifacts. It does not create
a second accounting hierarchy. Work accounting remains an independent consumer
of exact builder-owned knowledge-state versions.

## Version boundary

Published hierarchical research v1-v5 states retain
`research-program-state.schema.json` with `schemaVersion: 1`. Their program
records have no lineage field and their reducers continue to freeze existing
topology.

The topology foundation adds:

- `research-program-state-v2.schema.json`, whose program records carry explicit
  reciprocal lineage;
- `research-program-topology-transition-v1.schema.json`, a stale-guarded
  topology-only operation envelope;
- `research-program-topology-alignment-v1.schema.json`, a deterministic
  consumer-neutral identity mapping; and
- `math_flow.research_topology`, the pure validators and reducer.

Consumers that support both histories should call
`validate_research_program_state_versioned`; it dispatches to the frozen v1
validator or the state-v2 validator without coercing either artifact.

There is deliberately no v1-to-v2 in-place migration. A future governed builder
lane should begin a fresh replay into state v2 so old manifests, state bytes,
record digests, and run identities remain reproducible.

## State semantics

Programs remain a strict tree with stable IDs. Threads and items have one owning
program. Cross-program mathematical dependencies continue to use item
dependency edges rather than multiple placement parents.

State v2 adds a required program `lineage` array with these reciprocal pairs:

- active split successors use `split-from`, while the retired predecessor uses
  `split-into`;
- active merge successors use `merged-from`, while each retired predecessor
  uses `merged-into`.

A split has at least two sibling successors under the predecessor's former
parent. A merge has at least two predecessors and one successor. Lineage must be
reciprocal, reference existing programs, contain no duplicate targets, and form
an acyclic predecessor-to-successor graph. The reducer canonically sorts lineage
records before computing record and state digests.

Lineage is append-only history. A successor may later be completed, moved, or
retired as the predecessor of another split or merge without deleting its prior
incoming lineage. Sibling placement and active-successor lifecycle are checked
when a lineage event is added, rather than incorrectly requiring historical
successors to remain active siblings forever.

An active program cannot be beneath a retired ancestor. A retired program may
retain terminal threads and its historical parent-thread placement, but it may
not own a live thread or any current item. Its active child subtrees, live
threads, and items must move to active scope in the same atomic transition. This
is the deterministic completeness boundary for splits, merges, and pruning.

Contribution records retain their first-placement `directProgramId` and
`directThreadIds`. These fields are immutable provenance in state v2; their
targets may later be retired or moved. Current placement is read from the
program, thread, and item records. This permits one historical submission's
items to be distributed across split successors without rewriting the accepted
submission record.

## Transition operations

Every transition binds the exact `baseStateDigest`, and every operation on an
existing entity binds its exact `baseDigest`. The pure reducer accepts:

- `create` for a new program, thread, or item;
- `move` for a stable program, thread, or item; and
- `retire` for a non-root program or a thread.

A move may change only structural placement: `parentId`, `parentThreadIds`, or
program lineage for a program, and `programId` for a thread or item. It preserves
the stable ID, title, objective or summary, type or kind, lifecycle, mathematical
claim references, dependencies, and source provenance exactly. Program
retirement changes only lifecycle and lineage. Thread retirement changes only
lifecycle and sets expected exposure to zero.

The transition is applied atomically and the complete resulting tree is
validated before a state or alignment can be returned. Operations cannot remove
entities, rewrite content under the guise of a move, or move the root.

## Deterministic alignment

The reducer derives, rather than accepts, one subjectless alignment artifact.
The alignment validator accepts adjacent replayable state-v1 snapshots as well
as evolvable state-v2 snapshots, so accounting never falls back to a
digest-correct but semantically forged alignment during migration:

```text
schemaVersion
problemId
beforeKnowledgeStateDigest
afterKnowledgeStateDigest
preserved[]
moved[]
splits[]
merges[]
created[]
retired[]
alignmentDigest
```

`preserved`, `moved`, `created`, and `retired` use typed program, thread, or item
identities and exact record digests. A moved entry records its prior and next
parent/owner; program moves also record prior and next parent-thread IDs.
`splits` and `merges` contain the program-specific predecessor/successor sets
derived from newly added reciprocal lineage. Every array and nested ID set is
canonically sorted, and `alignmentDigest` is computed over the complete artifact
without its digest field.

The alignment is intentionally subjectless. One coalesced builder transition
may organize several accepted submissions, while the exact before and after
knowledge-state digests completely identify the coordinate change. A work-
accounting submission transition can bind this alignment digest independently.

## Integration seam

The active builder-v5 runner and reducer remain untouched. The inactive
provider-free builder-v6 foundation now composes state-v2 content operations
and topology operations into one accepted-submission transition, then:

1. bind all operations to the exact published state-v2 base;
2. integrate every accepted claim and immutable contribution mapping;
3. apply the topology operations without allowing them to rewrite content;
4. set the final state's `baseStateDigest` to the exact published predecessor;
5. validate the complete state with `validate_research_program_state_v2`;
6. derive the alignment from the published predecessor and final post-state;
7. retain the raw delta, final state, and alignment in the immutable build
   bundle; and
8. expose the alignment digest to downstream work accounting.

The standalone `apply_research_topology_transition` function intentionally
handles topology-only adjacent v2 states. The provider-free
`apply_research_builder_v6_transition` adapter validates the accepted-content
intermediate, invokes that reducer, and rebinds the final composite state
directly to the published predecessor; it never publishes the intermediate.
See `docs/HIERARCHICAL_RESEARCH_PROTOCOL_V6.md` for the remaining provider,
bundle, governance, and projection-activation seam.

No provider call, active projection admission, scheduler behavior, workflow,
viewer, or credit policy is part of this foundation.
