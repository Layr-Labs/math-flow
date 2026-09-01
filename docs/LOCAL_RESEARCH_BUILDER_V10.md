# Local/fractal research Builder V10 foundation

Status: inactive additive experimental candidate. It includes a direct sealed
provider adapter, an unpublished branch-only holdout, and provider-free scale
tests, but no admitted judge, profile, projection, publication route, or
production activation. Builder V9, state v3, and every published projection
remain unchanged.

## Purpose

Builder V9 keeps the complete semantic core of every program and intermediate
result in every provider request. That prevents hidden consolidation targets,
but it also repeats a growing global portfolio and cumulative provenance. V10
tests a different boundary:

1. trusted code retains the complete canonical state-v3 predecessor;
2. a model routes through compact recursive portfolio views and requests global
   searches without seeing raw submission evidence;
3. a refinement call sees deterministic search results and selects a bounded
   exact local read/write set;
4. an author call sees that exact packet plus the current raw evidence and
   authors a transition inside an explicit write scope; and
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

## Route, refine, then author

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
- exact selected result semantics, with counts and digest commitments replacing
  cumulative support, claim, source, and judgment arrays;
- bounded capsules for inspected, searched, and writable programs;
- compact search-hit identities and scores;
- an explicit read set and separate existing/create write scopes; and
- a commitment to counts and ID sets for the hidden complete state.

Program source/result arrays and result support/provenance arrays are
intentionally not copied into author views. A future provider adapter must
expand model-authored additions against trusted existing arrays before calling
the reducer, as Builder V9 already does for support and provenance.

`run_research_builder_v10_two_stage` remains a provider-agnostic reference
orchestrator. It accepts separate route and author callbacks so tests and
experiments can use deterministic fakes without making a provider call.

`OpenRouterResearchBuilderV10Provider` implements the experimental sealed path:

1. `route` receives accepted assessments and the bounded root/dependency view;
2. `route-refine` receives the trusted discovery packet and search hits; and
3. `organize` receives the final authoring packet and exact current evidence.

The first two calls explicitly receive zero raw-evidence bytes. This is a
context boundary, not an epistemic validity guard: authoritative validity
summaries and qualifications remain visible. The author call receives the full
current evidence, while prior support bodies remain hidden behind counts and an
exact digest.

Because existing program result-link arrays can also grow, provider-authored
program values use explicit `intermediateResultIdAdditions` and
`intermediateResultIdRemovals`. Trusted code applies that patch to the complete
hidden predecessor before invoking the unchanged reducer. This permits both
ordinary additive refreshes and deliberate topology moves without asking the
model to reproduce an unbounded opaque array.

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
- `math_flow/research_builder_v10_provider.py`
- `tests/test_research_builder_v10.py`
- `tests/test_research_builder_v10_provider.py`

## Remaining integration work

This candidate intentionally stops before activation. Remaining work is:

1. test and design one bounded re-route path for a placement clue present only
   in raw evidence, after the author discovers that another entity must become
   readable or writable;
2. add an optional separately bounded prior-support expansion only if empirical
   consolidation tests show that result statements plus support counts/digests
   are insufficient;
3. add state-digest keyed catalog caching;
4. place the route, discovery, authoring, patch, attempt, and telemetry artifacts
   in a new admitted output profile before any shadow lane; and
5. extend the completed provider-free miniature so its precommitted transitions
   pass through V10's exact authoring-packet and scoped-application wrapper,
   then run semantic knowledge-plus-work judges before considering a production
   projection.

Deterministic lexical search can miss paraphrases. A governed embedding index
could later supplement it, but must bind the embedding implementation and index
bytes. Individual heavily consolidated result records can also grow even though
the number of loaded results is bounded. If method-level consolidation quality
needs prior support bodies, add an explicitly requested, separately bounded
support-expansion page rather than restoring cumulative support to every author
packet. The unpublished BSSC holdout also reserves request bytes, completion
tokens, total tokens, provider calls, and a conservative per-call dollar ceiling
before each call; cost telemetry remains provider-reported and is not a
substitute for an account-side provider spending cap.
