# Projection protocol

Math Flow's core protocol does not prescribe a judge's mathematical output
schema. It standardizes the identity and integrity of a judge run, then lets the
judge declare an output profile.

## Protocol envelope

Every judge run is a directory containing `run.json` and one or more artifacts.
The manifest records:

- the problem and exact ledger head;
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

Nodes have individual content digests. A delta may `upsert` or `retire` nodes.
Updating an existing node requires its exact prior digest, and the reducer rejects
stale operations. Existing nodes may be updated only if the selector chose them.
New nodes must be attached beneath a selected or newly created node. Unselected
subtrees are carried forward byte-for-byte.

Detailed node support is authored in a referenced section of `report.md`. The
reducer copies that section into the node's `contentMarkdown`, alongside its
summary, lifecycle status, transaction links, and source-report digest. Selected
nodes therefore carry their full prior body into the next writer call, while the
long-form mathematical content remains absent from the structured model response.

## Judge-builder flexibility

Judge specs declare four allowlisted components:

```json
{
  "inputBuilder": "ledger-text-artifacts-v1",
  "invocationAdapter": "openrouter-chat-completions-v1",
  "outputAdapter": "select-report-extract-v1",
  "reducer": "hierarchical-delta-v1",
  "outputProfile": "math-flow/hierarchical-markdown-v1"
}
```

The allowlist is an MVP security boundary: a repository spec cannot import and
execute an arbitrary Python path. New builders can be registered in the runner;
later they can be separately signed executables or container images identified by
digest.
