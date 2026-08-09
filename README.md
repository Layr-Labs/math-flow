# Math Flow

Math Flow is a GitHub-native protocol for collaborative mathematical research.
Git records the canonical history of contributions; independently versioned judges
turn any prefix of that history into a replayable view of correctness, shared
knowledge, and credit.

The protocol's central rule is:

> Canonicalize what participants did, not what it means.

This repository is an executable MVP of that rule. It contains:

- a folder-based contribution format that stays pleasant to read and edit;
- a pull-request validator enforcing one atomic contribution per PR;
- a ledger command that derives contribution order from first-parent Git history;
- a versioned, allowlisted judge-builder interface;
- generic judge-run bundles with profile-specific artifacts;
- flat JSON and hierarchical Markdown example profiles;
- GitHub Actions for transaction checks and projection artifacts.

## Repository layout

```text
problems/<problem-id>/
  problem.md
  contributions/<contribution-id>/
    README.md
    ... arbitrary supporting artifacts

protocol/
  judges/                 versioned judge specifications
  profiles/               optional output-profile definitions
  schemas/                protocol and example-profile contracts

projections/<run>/
  run.json                protocol-level provenance and artifact manifest
  ...                     profile-specific artifacts; ignored by Git
```

A contribution may contain Markdown, Lean, source code, data, diagrams, or any
other useful artifact. Only `README.md` is required. Correctness and credit never
live in the contribution folder; they belong to judge projections.

## Try it locally

The CLI uses only the Python standard library (Python 3.11+):

```bash
python -m math_flow validate-tree
python -m math_flow run \
  --problem triangle-midpoints \
  --judge protocol/judges/baseline-v1.json \
  --head WORKTREE \
  --output-dir projections/baseline-v1/triangle-midpoints/worktree
```

After this repository is committed, use a Git commit instead:

```bash
python -m math_flow ledger --problem triangle-midpoints --head HEAD
python -m math_flow run \
  --problem triangle-midpoints \
  --judge protocol/judges/baseline-v1.json \
  --head HEAD \
  --output-dir projections/baseline-v1/triangle-midpoints/first-run
```

### OpenRouter judges

The original flat-JSON judge remains available as an example profile. Render its
exact request without making a network call:

```bash
python -m math_flow render-request \
  --problem triangle-midpoints \
  --judge protocol/judges/openrouter-math-review-v1.json \
  --head WORKTREE \
  --output /tmp/math-flow-openrouter-request.json
```

The older `project` command remains a compatibility interface for flat profiles;
new integrations should use `run` and consume `run.json`.

The recommended revision-aware hierarchical judge uses three calls: node
selection, an unconstrained Markdown assessment, and structured delta extraction.
The three-stage builder is an example, not a core protocol requirement. Export an
API key and run it against a commit-addressed ledger:

```bash
export OPENROUTER_API_KEY="..."
python -m math_flow run \
  --problem triangle-midpoints \
  --judge protocol/judges/openrouter-hierarchical-markdown-v2.json \
  --head HEAD \
  --output-dir projections/openrouter-hierarchical-markdown-v2/triangle-midpoints/run-1
```

Its bundle contains a small `run.json`, `report.md`, the node selection and delta,
audited adapter normalizations, the reduced hierarchical state, and an immutable
adjudication revision log. A later run can selectively update current state or
revise a past adjudication in light of new evidence:

```bash
python -m math_flow run \
  --problem triangle-midpoints \
  --judge protocol/judges/openrouter-hierarchical-markdown-v2.json \
  --head HEAD \
  --base-run projections/openrouter-hierarchical-markdown-v2/triangle-midpoints/run-1 \
  --output-dir projections/openrouter-hierarchical-markdown-v2/triangle-midpoints/run-2
```

The judge sends the problem statement and supported text artifacts (`.md`,
`.lean`, `.py`, `.tex`, and similar formats) to OpenRouter. Binary artifacts are
not sent. The included spec denies provider data collection and requires routing
to an endpoint that supports all requested parameters.

Run the tests with:

```bash
python -m unittest discover -s tests -v
```

## Submitting a contribution

1. Create one new directory under one problem's `contributions/` directory.
2. Add a non-empty `README.md`; put supporting files beside it.
3. Open a pull request. The transaction check rejects edits outside that one new
   directory.
4. Once checks and human review pass, squash-merge the PR. That commit is the
   canonical transaction, and its position on the protected branch is its order.

Problem creation and protocol changes use separate maintainer PRs. They are
validated structurally but are not contribution transactions.

See [docs/MVP.md](docs/MVP.md) for the architecture, decisions, rollout plan, and
known limitations. The generic run envelope and example output profiles are
documented in [docs/PROJECTION_PROTOCOL.md](docs/PROJECTION_PROTOCOL.md).
