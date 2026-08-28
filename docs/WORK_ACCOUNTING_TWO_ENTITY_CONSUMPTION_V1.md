# Two-entity knowledge consumption for work accounting

Status: additive provider-neutral foundation. Existing work-accounting V1/V2
profiles and published builder-v6 bundles retain their exact program/thread
topology, impact-context V1 bytes, stage order, and replay behavior.

Research program state V3 changes only the downstream topology selected by the
knowledge-state version:

- programs are the complete work-accounting node tree;
- intermediate results are semantic/provenance leaves and never receive their
  own work annotations; and
- topology alignment V2 and same-world handoff V2 are reducer-authored builder
  artifacts, selected only for state V3.

`math_flow.work_accounting_knowledge` is the single version-dispatch boundary
used by accounting state construction, work projection, scheduling, and the
CAS pipeline. It selects builder-v6 reducers and alignment/handoff V1 for
legacy state, and builder-v7 reducers and alignment/handoff V2 for state V3.
Cross-version transitions fail closed.

## Impact context V2

`build_impact_subgraph_context` continues to emit byte-identical schemaVersion
1 packets for program/thread/item states. For state V3 it emits additive
schemaVersion 2 packets containing:

- program-only seeds, ancestors, sibling decision points, bounded descendants,
  and collapsed program boundaries;
- counts of intermediate results behind collapsed boundaries; and
- `semanticIntermediateResultRefs` with only result identity, program links,
  lifecycle status, claim identities, dependency-result IDs, and record digest.

The shared packet deliberately omits result title, statement, scope
qualifications, and every proof/method/computation/tool support body. It is
therefore safe to embed in the no-access request without using the post-state
as a back door for submission content. Exact reconstruction against the bound
builder state remains mandatory before either counterfactual stage.

## Remaining publication and governance seams

This foundation does not mutate the immutable work-accounting V1/V2 profiles
or their prompts. A hosted two-entity lane still needs additive governed
identities that register impact-context V2 and describe program-only node
references. It also needs a `PublishedResearchV7TransitionProvider` after the
research bundle loader publishes and verifies the hierarchical-research-v7
profile. That adapter should mirror `work_accounting_research_v6`: replay the
v7 reducer, alignment V2, and handoff V2 from exact bundle bytes, follow the
content-addressed `baseRun` chain to origin, and perform no provider call.

These are activation seams, not gaps in local reducer consumption. The CAS
pipeline can already consume a supplied V7 transition end to end and persist
its program-only state, alignment, and handoff.
