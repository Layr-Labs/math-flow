# Two-entity knowledge-state migration and audit v1

Status: provider-free comparison prototype for the proposed
`research-program-state-v3` contract. It does not alter, coerce, or publish any
existing state-v1 or state-v2 artifact.

## Purpose and target

The proposed Builder V7 knowledge state has only two graph entity kinds:

- **programs**, which form one strict hierarchy and contain the current program
  synthesis, local residual work, and links to relevant results; and
- **intermediate results**, which contain the accepted statement, scope,
  dependencies, provenance, and bundled proof, method, computation, tool, and
  objective-evidence support.

The governed names reserved for this additive line are Builder V7 and profile
`hierarchical-research-v7`. The executable v3 schema and reducer are separate
versioned components. The provider-free code in
`math_flow.two_entity_migration` is an audit adapter, not that reducer.

The adapter answers two questions before a fresh V7 lane is considered:

1. How much can the existing Builder V6 state be simplified without another
   semantic judgment?
2. Where did state v2 fail to record enough structure to perform that fold
   deterministically?

Run the read-only audit against an extracted state-v2 artifact with:

```console
python3 -m math_flow two-entity-migration-audit \
  --state /path/to/research-program-state-v2.json \
  --output /path/to/two-entity-audit.json
```

The command does not call a provider or modify a projection.

## Deterministic mapping

`audit_two_entity_migration_v2` first validates the complete source state with
the frozen state-v2 validator. It then emits canonical thread/item mappings, a
summary, and either one complete proposed v3 state or `proposedState: null` plus
explicit unresolved mappings. `migrate_research_program_state_v2_to_v3` is the
strict interface and raises if any mapping is unresolved.

The mapping rules are:

1. Preserve every state-v2 program ID, parent, objective, lifecycle, lineage,
   and source transaction.
2. Fold each `unstructured` thread into its owning program's
   `localResidualSummary`.
3. Map a substantive thread to the one program that explicitly occupies it via
   `parentThreadIds`; otherwise promote it to a child program under its current
   owning program, reusing the thread ID. An unrelated program-ID collision or
   multiple occupants is unresolved.
4. Preserve every `result` item ID as an intermediate-result ID. Its state-v2
   owning program remains primary. Programs obtained from its contribution's
   direct thread placements become related programs, so the adapter does not
   pretend that historical thread placement was a current item move.
5. Bundle a proof, method, computation, or tool with the unique result in the
   same immutable contribution. With multiple results, use a unique direct
   dependency edge first, then a unique accepted-claim overlap, then a unique
   owning-program match. Otherwise report all candidate result IDs as
   unresolved.
6. Replace every cross-bundle item dependency with a dependency between the
   corresponding intermediate results. Dependencies internal to one bundle are
   represented by its support sections rather than a self-edge.
7. Replace `directProgramId` plus `directThreadIds` in contribution provenance
   with the canonical set of mapped `directProgramIds`. Map all contribution
   items to the corresponding unique `intermediateResultIds`.

The adapter does not split text heuristically. State v2 has no structured scope
qualification field, so the complete result summary becomes `statement` and
`scopeQualifications` remains empty. A fresh Builder V7 replay can author a
better separation from the accepted evidence.

## Fail-closed boundaries

The audit refuses to emit a partial proposed state when any of these conditions
holds:

- a source item belongs to zero or multiple contribution mappings;
- a support item has no result in its contribution;
- several result candidates remain after the deterministic association rules;
- explicit dependency edges associate one support item with several results;
- a `question` item requires a semantic choice between a program direction and
  an intermediate result;
- grouping an otherwise acyclic item graph would create a cycle between result
  bundles;
- a substantive thread has several program occupants or its promoted ID
  collides with an unrelated program; or
- the source state, record digests, dependency graph, or contribution
  references do not pass the frozen state-v2 validator.

These are audit findings, not prompts for manual repair. Canonical adoption
should run Builder V7 from the zero state through accepted submissions in
canonical order. If the snapshot adapter finds ambiguity, either a generally
valid deterministic rule must be added and tested or the fresh V7 builder must
make the organization from the accepted evidence. No migration operator may
invent a result statement, support relationship, or program boundary.

## Mapping invariants

A ready proposal guarantees:

- **source binding:** the audit binds the exact source `stateDigest`; its
  proposed snapshot uses `baseStateDigest: null` because a v2 digest is not a
  valid v3 predecessor;
- **totality:** every source thread and item has exactly one reported mapping;
- **stable anchors:** all source programs and result IDs survive unchanged;
- **single support ownership:** every proof, method, computation, and tool is
  bundled into exactly one intermediate result;
- **dependency preservation:** every source item edge becomes either internal
  support or one cross-result edge;
- **program/result reciprocity:** program `intermediateResultIds` exactly match
  all primary and related links from intermediate results;
- **contribution preservation:** every source contribution remains a distinct
  transaction record with the same claims, dependencies, and judgment;
- **canonical bytes:** arrays, records, the target state, and the audit report
  have deterministic ordering and content digests; and
- **input immutability:** the source object is validated and copied, never
  rewritten.

The adapter preserves knowledge content but cannot synthesize the ideal
`currentStateSummary`. For an existing program it uses mapped substantive-thread
summaries, falling back to the old objective; for a newly promoted leaf program
it preserves the source thread summary and status. Producing a compact holistic
account of what is established and what remains is a Builder V7 responsibility.

## Additive compatibility

State v1 and v2 schemas, builders, projections, run envelopes, and published
objects remain immutable and replayable. No existing projection should be
edited to reinterpret an old state as v3.

Adoption requires, in order:

1. deploy the new state-v3 validator, Builder V7 reducer/provider adapter,
   context consumers, and viewer support while retaining old readers;
2. admit a separately versioned Builder V7 judge/profile and a new projection
   in their governed changes;
3. initialize that projection at the v3 zero state and replay one accepted
   submission per transition in canonical order; and
4. bind any new work-accounting or credit experiment explicitly to the V7
   projection digest and exact knowledge terminal.

The audit proposal may be displayed or measured, but it must not be inserted as
a predecessor into the governed V7 chain. Published content-addressed history is
never rewritten, and state-v2 contribution provenance remains available for
comparison.

## Provider-free BSSC comparison plan

Run the following before spending on a BSSC V7 shadow lane:

1. Resolve and validate the exact terminal Builder V6 BSSC state and record its
   projection, run, state, and ledger-head digests.
2. Run `audit_two_entity_migration_v2` without a provider. Retain its audit
   digest, complete thread/item maps, unresolved records, and proposed-state
   digest when ready.
3. Compare entity counts by source and target kind: programs, substantive and
   unstructured threads, results, bundled support items, contributions, and
   unresolved mappings. The current terminal's expected starting counts are 5
   programs, 13 threads, 72 items, and 16 contributions; these counts must be
   re-derived from the bound artifact rather than hard-coded.
4. Check preservation mechanically: every source entity appears once in the
   audit, every external item dependency maps to a result dependency, every
   internal edge is explained by one support bundle, and every contribution's
   mapped program/result references resolve.
5. Materialize three provider-free context views from the same accepted
   frontier: the full v2 state, the complete v3 proposal, and a progressive v3
   view containing program summaries plus result statements with support loaded
   only for selected results. Compare serialized bytes, approximate token count,
   node count, dependency count, and duplicate source text.
6. Render v2 and v3 side by side for human readability. This is evaluation of
   the representation, not manual completion of unresolved mappings.
7. If the audit is ready, use it as a fixed expectation for fresh V7 replay
   coverage—not as the replay initializer. If unresolved, report the exact
   source IDs and reason codes, then determine whether Builder V7's from-zero
   representation avoids the ambiguity.

Later semantic experiments should freeze the accepted evidence and compare
full-v2, result-only-v3, and progressively loaded v3 contexts for validity,
work-accounting, and credit judgments. The provider-free comparison establishes
information preservation and context size; it cannot establish judgment quality
without those controlled ablations.
