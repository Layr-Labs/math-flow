# Work-accounting viewer/export V1 (inactive)

## Status and authority

This is an additive, provider-free presentation adapter for hierarchical work
accounting. It is intentionally inactive: no projection registry entry,
scheduler, workflow, persistence path, or catalog discovery rule admits it.
Existing viewer catalogs contain no `workAccountingProjections` field and render
exactly as before.

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

The output schema is
`protocol/schemas/work-accounting-viewer-projection-v1.schema.json`. Its run ID is
the exact schedule digest and it includes the exact terminal accounting state
and exact per-submission evaluation objects. `viewerDigest` binds the derived
presentation envelope.

## Accounting semantics shown in the UI

- Credit belongs to a canonical submission transaction.
- `R` is ex-ante/no-access work remaining, `C` is ex-post/with-access work
  remaining, and stored submission credit is the positive reduction `D = R-C`.
- The unit is **competent human researcher hours**.
- Raw hour values are immutable canonical decimal strings. No binary floating
  point is used for new work-accounting presentation.
- Percentages are not exported or stored. The UI sums exact decimal `D` values
  and derives displayed shares with `BigInt` arithmetic at render time.
- Node figures are accounting annotations within a submission evaluation. Only
  research programs and research threads may have numeric annotations. Semantic
  result/method items are excluded.
- Corrections are prospective. Historical `D` is not replayed; an affected
  evaluation shows its schedule-bound repair digests and affected-history flag.

## Activation seam

The persistence/catalog owner can activate this only after defining a governed,
content-addressed storage convention for the final schedule, publication
manifests, terminal accounting state, evaluation bundles, and any repair
artifacts. At that seam it should pass an explicit source configuration through
the keyword-only `work_accounting_sources` seam of `export_viewer_catalog`.
That path calls `load_work_accounting_viewer_projection(...)`, requires the
terminal knowledge-state digest to exist in the named research projection, and
adds the result to an optional top-level `workAccountingProjections` array. The
current viewer validates and presents that optional array. Ordinary catalog
export does not add the field, scan arbitrary bundles, or admit model-produced
presentation JSON directly.
