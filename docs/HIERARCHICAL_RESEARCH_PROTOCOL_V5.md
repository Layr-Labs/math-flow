# Hierarchical research protocol v5

Builder v5 is an additive correction to the validity-v4 research lane. It does
not change mathematical adjudication, accepted-claim identity, dependency
selection, the serialized state schema, or hierarchical credit semantics. It
changes the organizer's initial-program contract so a fresh replay reliably
forms useful local credit contexts instead of leaving every contribution at
root.

The validity-v4 judge remains responsible only for rigorous correctness and
required-premise selection. Builder v5 receives those immutable outcomes plus
the accepted original submissions, separates accepted results from their
supporting proofs and methods, and organizes only that accepted material.
Invalid and indeterminate submissions remain wholly absent.

## Initial hierarchy and placement

Programs are stable local-objective and credit contexts in a strict tree. The
organizer should create siblings for genuinely distinct research agendas and a
nested program when a specialization has its own local objective within a
broader agenda. It must not create a program merely for a submission,
contributor, timestamp, or display grouping.

Every accepted contribution has one immutable placement audit in the v5 delta:

- `local-objective` places it directly in a non-root program and names exactly
  that program;
- `canonical-objective` is the explicit escape for genuinely problem-global
  work placed at root; and
- `cross-program` places work at root only when it directly spans at least two
  named active non-root programs that are incomparable in the tree.

Each audit carries a non-empty rationale. Audits appear in the same order as
the contribution mappings and remain in the published delta and accepted
history consumed by ex-post credit. They are organizational evidence, not a
credit score.

The deterministic v5 boundary rejects a materialized state with at least two
accepted contributions when every contribution is still direct at root. This
post-state rule applies across batches, so two singleton builds cannot evade
it. A single genuinely global result remains valid at root, and global or
cross-program results remain valid once the state also contains local work.

## State and topology compatibility

The materialized `research-program-state` remains schema version 1. Builder v5
uses a schema-version-2 batch delta containing the existing operations and
contribution mappings plus `placementAudits`. Its reducer validates the audit,
strips it, and invokes the frozen v2-v4 state reducer. Published v2-v4 bundles
therefore retain their exact behavior and replay identity.

This version may create sibling and nested programs, including a child beneath
an existing active program. It still preserves the parent of every existing
program, thread ownership and kind, and item program and type. Split, merge,
move, and reparent operations remain planned topology evolution for a later
governed version. The initial tree is not an eternal ontology.

Every active program continues to require exactly one active unstructured
thread. A non-root program occupies at least one local thread in its parent.
Cross-program mathematical use is represented through item dependencies rather
than duplicate items.

## Enforcement and retry

The structured output schema requires one placement audit per accepted
contribution. The trusted reducer checks exact audit coverage and order,
placement basis, referenced program existence and activity, pairwise
incomparability for cross-program placement, and the total post-state flatness
invariant.

If structured extraction or deterministic v5 reduction rejects a provider
response, the runner invalidates that response's replay checkpoint and retries
with the exact validation failure as correction context. A rejected root-only
proposal therefore cannot become a reusable formation checkpoint.

Bundle loaders and the viewer revalidate the v5 delta against its materialized
state. Hierarchical credit history retains the raw delta, so placement audits
are available at the common hindsight horizon without changing the credit
output schema.

## Versioned components and rollout

Runtime support adds immutable identities:

- `protocol/judges/openrouter-hierarchical-research-builder-v5.json`;
- `protocol/profiles/hierarchical-research-v5.json`; and
- `protocol/schemas/research-program-delta-v5.schema.json`.

Builder v5 consumes validity-v4 judgments. Runtime support and these versioned
components must merge before a separate one-file governed edit points
`openrouter-research-v3` at builder v5. That projection-spec digest creates a
fresh lane; it does not migrate or rewrite the v4 chain. The existing validity
judgments remain reusable, while both retained problems replay from an empty v5
state. The dependent credit-v3 overlay continues to name the logical producer
and becomes due against the new exact terminal after replay.
