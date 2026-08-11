# Projection protocol

Math Flow's core protocol does not prescribe a judge's mathematical output
schema. It standardizes the identity and integrity of a judge run, then lets the
judge declare an output profile.

## Protocol envelope

Every judge run is a directory containing `run.json` and one or more artifacts.
The manifest records:

- the problem and exact ledger head;
- a problem-ledger head and digest unaffected by unrelated problems;
- the judge-spec and runner identity;
- the allowlisted builder components used for input, invocation, output, and
  optional reduction;
- an optional base-run digest;
- the declared output profile;
- request digests and provider-run metadata;
- artifact paths, roles, media types, sizes, and SHA-256 digests.

The protocol validates this envelope without understanding the semantics of the
artifacts. A profile supplies those semantics. This permits independent judges to
produce JSON, Markdown, formal proof objects, images, notebooks, or a composite
bundle without changing the canonical transaction layer.

## Example profiles

### `math-flow/flat-json-v1`

This is the original MVP projection. `projection.json` contains verdicts, one
cumulative state object, and credit assignments. It remains useful for small
experiments, but it is only one example profile.

### `math-flow/hierarchical-markdown-v1`

This profile contains:

```text
run.json
control/selection.json
report.md
state/delta.json
state/state.json
```

The included OpenRouter builder uses three stages:

1. A structured selector sees a compact state index and chooses the smallest set
   of existing nodes relevant to the ledger.
2. A Markdown writer sees the selected node bodies and writes an unconstrained,
   auditable mathematical report without a JSON response format.
3. A structured extractor reads the report and emits only state operations. It
   does not redo the mathematical judgment.

Each stage may select its own model and generation parameters in the judge spec.
The structured stages are control-plane operations; the detailed mathematical
assessment stays in Markdown.

Version 1 remains available for replay. New runs should normally use the
revision-aware `math-flow/hierarchical-markdown-v2` profile described below.

### `math-flow/hierarchical-markdown-v2`

Version 2 adds one artifact to the hierarchical bundle:

```text
control/normalizations.json
state/revisions.jsonl
```

The output adapter records deterministic control-plane normalizations separately
from the judge report. It derives concurrency guards from the selected state,
orders parents before children, assigns selected `root` as the parent of an
otherwise parentless top-level node, and canonicalizes an impossible first
`revise` to `issue`. Mathematical judgments and non-mechanical invalid transitions
are never normalized this way.

Each JSON Lines entry is an immutable, content-addressed adjudication revision.
The log is copied forward as an exact prefix and new revisions are appended. The
materialized `state/state.json` points each node to its current revision, so
consumers that only need the latest view do not need to replay the log.

Revision operations are `issue`, `revise`, `retract`, and `reinstate`. They use
both the prior node digest and prior revision ID as optimistic concurrency guards.
The first revision uses null base references; subsequent revisions explicitly
chain to the revision they supersede.

Subjects and evidence are intentionally different fields. A subject identifies
the ledger transaction whose adjudication is being changed. Evidence records why
the judgment is warranted or changed, with relations such as `supports`,
`refutes`, `qualifies`, and `formalizes`. Evidence can identify a transaction,
content-addressed artifact, verifier attestation, or judge run.

### Retroactive correction and time

Retroactive correction never mutates an old run. Suppose a judge accepts a claim
at ledger head H1, and a contribution at H2 contains a checked Lean counterexample.
A new run based on the H1 bundle can append a `retract` revision with:

- the H1 contribution as its subject;
- the H2 contribution or verifier attestation as refuting evidence;
- the old revision ID as `baseRevisionId`;
- H2 as `issuedAtLedgerHead`.

Subjects carry their original `ledgerPosition`. These two temporal coordinates
make both views reproducible: a query as of H1 sees the acceptance, while a query
as of H2 sees the retraction and its reason. The earlier acceptance remains an
auditable historical fact rather than being silently rewritten.

## Hierarchical state

The state is a tree with stable IDs such as:

```text
root
├── program/synthetic
│   ├── claim/midpoint-similarity
│   └── question/lean-formalization
└── program/coordinate
    └── method/determinant-area
```

Nodes have individual content digests. Version 1 deltas `upsert` or `retire`
nodes; version 2 uses semantic adjudication revision operations. Updating an
existing node requires its exact prior digest, and the reducer rejects stale
operations. Existing nodes may be updated only if the selector chose them. New
nodes must be attached beneath a selected or newly created node. Unselected
subtrees are carried forward byte-for-byte.

Detailed node support is authored in a referenced section of `report.md`. The
reducer copies that section into the node's `contentMarkdown`, alongside its
summary, lifecycle status, transaction links, and source-report digest. Selected
nodes therefore carry their full prior body into the next writer call, while the
long-form mathematical content remains absent from the structured model response.

### Neutral facet-aware knowledge revisions

`math-flow/knowledge-build-markdown-v2` is an additive knowledge-formation
profile. It does not describe every edit to a knowledge view as an adjudication.
Its state uses `schemaVersion: 3`, nodes point to `currentRevision`, and the
immutable `knowledge-revisions` artifact contains neutral knowledge revisions.
Version 1 knowledge-build bundles and version 2 adjudication-revision state remain
valid and replayable; there is no in-place conversion of their histories.

Builder operations use the lifecycle verbs `create`, `update`, `retire`, and
`restore`. An operation is a full proposed node snapshot and does not declare
what kind of change it made. The `hierarchical-knowledge-revisions-v3` reducer
compares the materialized snapshot with the prior revision and deterministically
records one or more ordered facets:

- `topology`: `parentId` or node type changed;
- `content`: title, summary, or the exact materialized Markdown changed;
- `lifecycle`: active/retired status changed;
- `provenance`: subjects or evidence changed.

Every neutral operation names two exact, node-specific report sections.
`reportSection` identifies `## Node: <nodeId>`, the holistic snapshot that becomes
the node's current Markdown. `changeSection` identifies the separate, unique
`## Change: <nodeId>` audit explanation. The reducer copies that change section's
non-empty body verbatim into immutable `changeRationale` and records its report
digest and heading in `changeRef`; the extractor cannot supply a second rationale
that might drift from the report. `reportRef` continues to point only to the
materialized node section.

The revision stores a digest of the exact materialized Markdown. Validators bind
both report references to the exact report bytes and recompute the facets from the
revision chain rather than trusting the builder or the recorded facet list.
Consequently, a topology-only revision is possible only when content, lifecycle,
and provenance are byte-for-byte and structurally unchanged. A change rationale,
report pointer, or timestamp change by itself is audit metadata, not a material
knowledge revision, and is rejected as a no-op.

## Judge-builder flexibility

Judge specs declare four allowlisted components:

```json
{
  "inputBuilder": "ledger-text-artifacts-v1",
  "invocationAdapter": "openrouter-chat-completions-v1",
  "outputAdapter": "select-report-extract-revisions-v2",
  "reducer": "hierarchical-revisions-v2",
  "outputProfile": "math-flow/hierarchical-markdown-v2"
}
```

The allowlist is an MVP security boundary: a repository spec cannot import and
execute an arbitrary Python path. New builders can be registered in the runner;
later they can be separately signed executables or container images identified by
digest.

## Parallel judgments and scheduled knowledge formation

Version 0.5 separates immutable mathematical judgments from cumulative knowledge
state. This is an additive path; older hierarchical runs remain replayable and
continue to combine assessment with state reduction.

A `runKind: judgment` bundle has no reducer or base run. Its Markdown report is
the detailed assessment, while `judgment.json` contains only the provenance and
small routing index needed to identify subjects, evidence, claims, and potential
conflicts. Primary judgments can therefore run concurrently over different
transaction subsets.

Conflict detection is conservative and non-adjudicative. Opposed `supports` and
`refutes` findings for the same stable claim key create a content-addressed open
conflict record. That record, the immutable input judgments, and the canonical
contribution evidence become the inputs to a separate reconciliation judgment.
Reconciliation reports decide whether the apparent conflict is compatible,
resolved toward one side, synthesized, unresolved, or awaiting evidence. They do
not mutate knowledge state and never rewrite their input judgments.

Completed primary and reconciliation judgments mark a knowledge-builder lane
dirty. A governed lane is keyed by `(problem id, projection-spec digest)`; the
builder digest remains bound inside the lane and legacy ungoverned lanes retain
their `(problem id, builder-spec digest)` identity. Each lane admits one active
build, coalesces pending inputs, and enforces a minimum interval between completed
builds. Conflict, primary-judgment, and reconciliation dependencies are claimed
as one connected component so batching cannot separate a dispute from the
evidence needed to interpret it. A claimed build records its exact base-state
run, judgment IDs, conflict IDs, and judgment-set digest. New completions during
the build remain pending for the next eligible interval. Failed claims are
returned atomically and carry a bounded exponential-retry marker tied to the
claim and problem ledger.

Knowledge formation is intentionally not implemented by the primary or
reconciliation judge adapters. The example `openrouter-knowledge-builder-v1`
adapter consumes one claimed input set, organizes resolved findings and open
disputes, emits a sparse hierarchical delta, and uses the existing deterministic
revision reducer. It cannot silently settle an unresolved input: every conflict
without a single resolving reconciliation outcome must appear as content-addressed
evidence on an active dispute operation or the run is rejected.

The knowledge-build bundle records `runKind: knowledge-build`, the scheduler
lane, builder digest, exact base-state digest, judgment and conflict IDs,
judgment-set digest, and build token. Its output profile is a reusable example,
not a core requirement. A different registered builder may use another call
topology or output profile while preserving the same immutable run envelope and
serialized state-chain semantics.

Projection publication is independent of computation. Workers produce verified
run bundles; publisher jobs copy them into content-addressed object paths and
record idempotent publication batches. Disjoint problem lanes may publish in
parallel: each publisher refetches the orphan `projections` branch, three-way
merges its scheduler lane, and retries an expected-head race. Git publication
order has no semantic meaning;
judgment, reconciliation, and state relationships are always explicit digests.
