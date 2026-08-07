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
- a versioned judge interface and a deterministic baseline projection;
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
  schemas/                output contracts

projections/              generated locally; ignored by Git
```

A contribution may contain Markdown, Lean, source code, data, diagrams, or any
other useful artifact. Only `README.md` is required. Correctness and credit never
live in the contribution folder; they belong to judge projections.

## Try it locally

The CLI uses only the Python standard library (Python 3.11+):

```bash
python -m math_flow validate-tree
python -m math_flow project \
  --problem triangle-midpoints \
  --judge protocol/judges/baseline-v1.json \
  --head WORKTREE \
  --output projections/baseline-v1/triangle-midpoints/worktree.json
```

After this repository is committed, use a Git commit instead:

```bash
python -m math_flow ledger --problem triangle-midpoints --head HEAD
python -m math_flow project \
  --problem triangle-midpoints \
  --judge protocol/judges/baseline-v1.json \
  --head HEAD
```

### Preview or run the OpenRouter judge

Render the exact request without making a network call:

```bash
python -m math_flow render-request \
  --problem triangle-midpoints \
  --judge protocol/judges/openrouter-math-review-v1.json \
  --head WORKTREE \
  --output /tmp/math-flow-openrouter-request.json
```

To perform a billed judge run, export an API key and replace `WORKTREE` with a
commit SHA or `HEAD` for a canonical projection:

```bash
export OPENROUTER_API_KEY="..."
python -m math_flow project \
  --problem triangle-midpoints \
  --judge protocol/judges/openrouter-math-review-v1.json \
  --head HEAD \
  --output projections/openrouter-math-review-v1/triangle-midpoints/result.json
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
known limitations. See [docs/REMOTE_TESTING.md](docs/REMOTE_TESTING.md) for the
first GitHub and live-provider test.
