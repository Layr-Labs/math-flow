# Local/fractal research Builder V10 foundation

Status: inactive additive runtime foundation. It introduces no governed judge,
profile, projection, workflow, publication route, or provider call. Builder V9,
state v3, and every published projection remain unchanged.

## Purpose

Builder V9 keeps the complete semantic core of every program and intermediate
result in every provider request. That prevents hidden consolidation targets,
but it also repeats a growing global portfolio and cumulative provenance. V10
tests a different boundary:

1. trusted code retains the complete canonical state-v3 predecessor;
2. a model routes through compact recursive portfolio views and global search;
3. trusted code resolves a bounded exact local read set;
4. a second model call authors a transition inside an explicit write scope; and
5. the existing V9/V8/state-v3 reducer applies the expanded transition to the
   complete hidden predecessor.

The full state remains authoritative and replayable. Locality changes only the
provider-visible view and permitted mutation surface.

## Trusted compact directory

`build_research_builder_v10_catalog` derives three digest-bound indexes from an
exact validated state-v3 value:

- program cards containing hierarchy, objective, current synthesis, residual,
  and lifecycle;
- result cards containing the statement, qualifications, program links,
  result dependencies, and lifecycle; and
- a program directory containing immediate child/result IDs, descendant counts,
  and a recursive subtree commitment.

Cards deliberately omit proof/method/computation/tool support and cumulative
`sourceTransactionIds`, `claimRefs`, and `judgmentIds`. The trusted catalog is
not itself a provider prompt. `build_research_builder_v10_program_capsule`
reveals one bounded page of immediate children and linked results for any
program. Loading a child yields the same shape, so navigation is fractal rather
than a one-time root summary. Pages bind the base state, catalog, subtree, page
offsets, and limits.

`search_research_builder_v10_catalog` is a topology-independent deterministic
lexical search over program and result cards. It uses no mutable external index,
embedding model, or network service. Stable score and ID ordering make identical
state/query inputs replay exactly. Hierarchical navigation is therefore not the
only way to recover a distant consolidation target.

## Route then author

The initial route context contains a bounded root capsule and compact cards for
every result in the accepted submission's declared dependency closure. It binds
the exact base-state, accepted-claim, and catalog digests.

A route plan may request:

- exact inspection of known programs or results;
- up to eight bounded global searches;
- existing program/result write IDs; and
- exact IDs that may be created.

Trusted code canonicalizes and digests that plan. Search hits, explicitly
selected records, every declared dependency result, recursive result
dependencies and live supersession targets, all linked programs, relevant
program-lineage peers, and every ancestor through root form the local read set.
The constructor fails rather than truncating when this mandatory closure exceeds
its program or result budget.

The resulting authoring packet contains:

- exact semantic views of selected programs, with digest commitments replacing
  their cumulative source and result-link arrays;
- exact selected result semantics and support, with digest commitments replacing
  cumulative claim, source, and judgment provenance arrays;
- bounded capsules for inspected, searched, and writable programs;
- compact search-hit identities and scores;
- an explicit read set and separate existing/create write scopes; and
- a commitment to counts and ID sets for the hidden complete state.

Program source/result arrays are intentionally not copied into ancestor views.
A future provider adapter must expand model-authored additions against trusted
existing arrays before calling the reducer, as Builder V9 already does for
support and provenance.

`run_research_builder_v10_two_stage` is a provider-agnostic reference
orchestrator. It accepts separate route and author callbacks so tests and
experiments can use deterministic fakes without making a provider call.

## Enforcement and compatibility

`apply_research_builder_v10_transition` accepts an already-expanded,
V9-compatible transition. Before reduction it re-derives and validates the
authoring packet from the exact base and accepted claims. It rejects:

- stale state, route-context, route-plan, catalog, or packet bindings;
- writes to an existing entity outside the declared existing write scope;
- creation of an ID outside the declared create scope; and
- program/result references outside the resolved read set.

It then calls the unchanged V9 application path, which calls the unchanged V8
integrity checks and state-v3 reducer. After reduction it additionally verifies
that every non-operated program/result and every prior contribution record is
byte-for-byte unchanged. State-v3 topology alignment and same-world accounting
handoff derivation therefore remain unchanged.

The implementation and tests live in:

- `math_flow/research_builder_v10.py`
- `tests/test_research_builder_v10.py`

## Remaining integration work

This foundation intentionally stops before activation. A complete governed V10
candidate still needs:

1. two sealed provider request/response schemas and an allowlisted provider
   adapter;
2. trusted expansion of compact program/result patches into complete V9
   transition values;
3. content-addressed route-context, route-plan, authoring-packet, and attempt
   artifacts in a new output profile;
4. one bounded re-route path when the author discovers that a read-only search
   hit must become writable;
5. state-digest keyed catalog caching and per-stage token/byte telemetry; and
6. a separately governed inactive projection and experiment workflow before any
   production admission.

Deterministic lexical search can miss paraphrases. A governed embedding index
could later supplement it, but must bind the embedding implementation and index
bytes. Individual heavily consolidated result records can also grow even though
the number of loaded results is bounded; support paging is the next locality
boundary if scale probes show that single-record growth is material.
