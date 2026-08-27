# Work-accounting viewer/export V1/V2

## Status and authority

This is the additive, provider-free presentation adapter for hierarchical work
accounting. Catalogs without a `workAccountingProjections` field and published
V1 viewer objects continue to render exactly as before.

Math Flow's knowledge builder remains the sole authority for the research
program/thread portfolio. The viewer neither invents topology nor accepts an
alignment supplied by a model.

## Verified export boundary

`math_flow.work_accounting_viewer.load_work_accounting_viewer_projection` loads
every evaluation through `load_work_projection_bundle`, which verifies artifact
content addresses and deterministically replays both counterfactual branches.
The exporter then requires, for every evaluated canonical subject:

1. exactly one verified work-projection bundle;
2. exactly one valid publication manifest;
3. exact agreement among the evaluation, publication, schedule completion, and
   committed with-access state;
4. an unbroken predecessor-state chain from the schedule's initial state to its
   terminal state; and
5. exact repair-event/state coverage when a prospective correction exists.

The original output schema is
`protocol/schemas/work-accounting-viewer-projection-v1.schema.json`. The additive
V2 exporter uses
`protocol/schemas/work-accounting-viewer-projection-v2.schema.json`; V1 objects
remain readable. A run ID is the exact schedule digest and includes the exact
terminal accounting state and exact per-submission evaluation objects.
`viewerDigest` binds the derived presentation envelope.

## Accounting semantics shown in the UI

- Credit belongs to a canonical submission transaction.
- `W^-` is no-access work remaining, `W^+` is the new committed live work
  remaining, and stored submission credit is the positive reduction
  `D = W^- - W^+`. The symbols `R_v` and `C_v` remain reserved for global reach
  and conditional subtree work at node `v`.
- The unit is **competent human researcher hours**.
- Raw hour values are immutable canonical decimal strings. No binary floating
  point is used for new work-accounting presentation.
- Percentages are not exported or stored. The UI sums exact decimal `D` values
  and derives displayed shares with `BigInt` arithmetic at render time.
- V2 exports the current terminal parameterization of every program/thread:
  direct work `d`, incoming incidence `P`, global reach `R`, conditional subtree
  work `C`, and expected direct work `R*d`, together with status and digests.
- For each submission, V2 exports the complete union of direct `W^-` and `W^+`
  patch nodes separately from unpatched nodes whose derived values changed by
  propagation. Every row contains both branch values. The signed node quantity
  `R^-d^- - R^+d^+` is additive and the exact row sum must equal `D`; differences
  of overlapping subtree `C` values are shown only as non-additive context.
- Topology-required patch rows are marked explicitly. If their primitive branch
  values agree and their additive node contribution is zero, the row is
  topology-only even when non-additive subtree context changes below it.
- Only research programs and research threads may have numeric annotations.
  Semantic result/method items are excluded.
- Corrections are prospective. Historical `D` is not replayed; an affected
  evaluation shows its schedule-bound repair digests and affected-history flag.

## Publication seam

The persistence/catalog owner passes a governed, content-addressed storage
configuration for the final schedule, publication manifests, terminal
accounting state, evaluation bundles, and any repair artifacts through the
keyword-only `work_accounting_sources` seam of `export_viewer_catalog`.
That path calls `load_work_accounting_viewer_projection(...)`, requires the
terminal knowledge-state digest to exist in the named research projection, and
adds the result to an optional top-level `workAccountingProjections` array. The
viewer validates and presents that optional array. Ordinary catalog export
without an explicit source does not add the field, scan arbitrary bundles, or
admit model-produced presentation JSON directly.
