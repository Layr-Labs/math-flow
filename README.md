# Math Flow

Math Flow is a GitHub-native protocol for collaborative mathematical research.
Git records the canonical history of contributions; independently versioned judges
turn any prefix of that history into a replayable view of correctness, shared
knowledge, and credit.

The protocol's central rule is:

> Canonicalize what participants did, not what it means.

This repository is an executable MVP of that rule. It contains:

- folder-based contribution and research-direction event formats that stay
  pleasant to read and edit;
- a pull-request validator enforcing one atomic participant event per PR;
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
  directions/<direction-id>/events/<event-id>/
    README.md
    event.json

protocol/
  judges/                 versioned judge specifications
  projections/            approved logical projection definitions
  profiles/               optional output-profile definitions
  schemas/                protocol and example-profile contracts

projections/<run>/
  run.json                protocol-level provenance and artifact manifest
  ...                     profile-specific artifacts; ignored by Git
```

A contribution may contain Markdown, Lean, source code, data, diagrams, or any
other useful artifact. Only `README.md` is required. Correctness and credit never
live in the contribution folder; they belong to judge projections.

A contribution may optionally include `verification.json`, which pins a
repository-approved verifier recipe but never its outcome. After canonical
merge, `math-flow attest` runs the verifier in its digest-pinned, networkless OCI
environment and emits a replayable content-addressed projection bundle. See
[the objective-attestation protocol](docs/OBJECTIVE_ATTESTATIONS.md).
The trusted merge lifecycle now dispatches that execution automatically, while
`math-flow attestation-plan` provides a provider-free, non-executing status check.

Research-direction events are a separate append-only participant stream. A
`register` event records a specific intended direction; later `update`, `release`,
or `complete` events extend it through an exact predecessor. A `release` must
match the originating registration's canonical Git author identity. Registrations are
non-exclusive evidence of priority, not ownership or mathematical truth. They do
not enter the contribution ledger or trigger mathematical projections. Their
merge performs a provider-free refresh of the repository viewer catalog.

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
python -m math_flow directions --problem triangle-midpoints --head HEAD
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

### Parallel judgments and serialized knowledge formation

The v0.5 execution path separates immutable primary and reconciliation judgments
from rate-limited knowledge formation. Judgments have no base run and can execute
concurrently; opposed findings create explicit conflict records for targeted
reconciliation. Completed judgments coalesce in a single-writer knowledge-builder
lane instead of immediately rebuilding state.

The included knowledge builder consumes one exact scheduler claim. It is
deliberately non-adjudicative: it may organize primary findings and supplied
reconciliation outcomes, but an unreconciled or unresolved conflict must become
an active dispute node. A deterministic reducer then applies the sparse update
to the one serialized state chain. This three-stage OpenRouter builder remains
an example profile rather than a core protocol requirement.

See [docs/PARALLEL_JUDGMENTS.md](docs/PARALLEL_JUDGMENTS.md) for the command flow,
scheduler semantics, and content-addressed batch publisher. The existing `run`
command remains available for replay and comparison of combined hierarchical
judge/state runs.

Before spending provider credits on a scale test, run the deterministic
congestion probe:

```bash
python -m math_flow provider-free-scale-probe \
  --problems 12 \
  --projections-per-problem 4 \
  --solvers 12 \
  --output /tmp/math-flow-scale-report.json
```

It exercises parallel judgment completion, reconciliation-atomic formation,
single-writer leases and throttling, failures and retries, optimistic scheduler
merges, bounded publication commits, and repository-backed viewer/context
discovery with `providerCalls: 0`. Hosted projection workflows use verified
`(problem, primary-judge)` concurrency streams: independent judges run in
parallel, while projections sharing one judge queue briefly to reuse published
paid judgments.

### Credit overlays

Credit is an independent projection over an exact locked knowledge state, never
a field in the mathematical state. After a schema-version-2 overlay projection
has been admitted, inspect its immutable inputs without a provider call:

```bash
python -m math_flow resolve-projection-dependencies \
  --projection <credit-projection-id> \
  --problem <problem-id> \
  --head HEAD \
  --projection-dir /path/to/projection-worktree
```

Run the initial qualitative Markdown/index profile locally with:

```bash
python -m math_flow credit \
  --projection <credit-projection-id> \
  --problem <problem-id> \
  --head HEAD \
  --projection-dir /path/to/projection-worktree \
  --output-dir /tmp/math-flow-credit-run
```

Check eligibility without spending provider credits first:

```bash
python -m math_flow credit-plan \
  --projection <credit-projection-id> \
  --problem <problem-id> \
  --head HEAD \
  --projection-dir /path/to/projection-worktree
```

The report call is unconstrained Markdown. A second control call indexes one
qualitative assignment per transaction, linked to exact knowledge revisions.
The registration-aware v2 profile may additionally cite exact prior canonical
`register` events; the legacy v1 profile's informal reservation references remain
readable without changing their meaning. Registration is non-exclusive evidence,
and the v2 rubric discounts vague, abandoned, or poorly executed plans. This is
an example credit policy rather than a core formula. The five-minute wake-up
workflow plans governed overlay eligibility
without a provider call and dispatches the allowlisted credit runner only when
eligible. Rolling overlays coalesce dependency changes behind
`minimumIntervalSeconds`; an optional closed UTC hour/day window can instead
scope assignments to the transactions merged during that reproducible period.
After the first calendar run, missed nonempty periods are processed oldest-first
and empty periods are skipped. Automatic retries are keyed to the exact semantic
state or window, suppress active duplicates, and stop after five consecutive
failures; manual workflow dispatch remains available for diagnosis and repair.

### Interactive research atlas

The `viewer/` app presents the canonical transaction ledger, research-direction
history, full submission Markdown, published primary and reconciliation
judgments, every knowledge-state chain, credit overlays, and the immutable
adjudication revisions behind them. Its
server endpoint reads `viewer/catalog.json` directly from the orphan
`projections` branch; the browser refreshes that endpoint every 30 seconds and
offers problem and projection selectors. A checked-in deterministic export is
used only for local development or when repository state is unavailable.
Private repositories configure the viewer's server-only
`MATH_FLOW_GITHUB_TOKEN` binding with a fine-grained, read-only Contents token;
the credential is never sent to the browser.

Every validated atomic participant event is squash-merged by the trusted
auto-merge workflow. Contribution events dispatch the baseline and approved
OpenRouter projection for their problem; research-direction events do not. The
OpenRouter workflow resolves its logical
projection from `protocol/projections/` at canonical `main`, plans judgment
coverage for every ledger transaction under its judge spec, and fans out all
missing primary judgments concurrently. It then deterministically derives
conflicts from the complete verified primary set, reuses published
reconciliations, fans out any missing reconciliations, and coalesces the
dependency-complete results into one serialized knowledge build. It publishes
the content-addressed batch and scheduler state to `projections` and regenerates
the catalog. Manual dispatch remains
available for repair and replay, and redispatching is idempotent when coverage
is complete.

Problem namespaces and projection definitions require a configured administrator
approval before admission, while ordinary contribution PRs retain the atomic
transaction validator without this extra gate. See
[docs/GOVERNANCE.md](docs/GOVERNANCE.md) for the registry, approval workflow, and
required branch-protection settings.

For an offline fixture, generate the single-projection data file by listing runs
from oldest to newest:

```bash
python -m math_flow export-viewer \
  --problem triangle-midpoints \
  --head HEAD \
  --run-dir projections/openrouter-hierarchical-markdown-v2/triangle-midpoints/run-live-1 \
  --run-dir projections/openrouter-hierarchical-markdown-v2/triangle-midpoints/run-live-2 \
  --run-dir projections/openrouter-hierarchical-markdown-v2/triangle-midpoints/run-live-3 \
  --judgment-dir projections/staging/hosted-run-31361558280/judgment \
  --output viewer/app/math-flow-data.json

cd viewer
npm install
npm run dev
```

Open the URL printed by the development server. Select a state version to
time-travel across cumulative knowledge builds. Selecting a transaction keeps
the complete state visible, highlights its provenance connections, and offers
only Submission and Judgment details; its coverage label distinguishes a
primary judgment from an evidence-only mention. Selecting a node clears that
transaction context and offers only its current assessment and source Build
report. The Judgment view exposes both the original Markdown assessment and its
structured finding record.

### Agent context and solver skill

Build and protocol contributors should start with
[`docs/AGENT_BUILD_CONTEXT.md`](docs/AGENT_BUILD_CONTEXT.md), which records the
current architecture, deployment target, invariants, workflow lifecycle, safe
multi-agent conventions, and near-term priorities.

Agents that do not use the viewer should discover work from canonical problem
admissions, then materialize verified state for initialized problems:

```bash
python3 -m math_flow list-problems \
  --head origin/main \
  --projection-dir /path/to/projection-worktree

python3 -m math_flow context \
  --problem triangle-midpoints \
  --projection-dir /path/to/projection-worktree \
  --projection openrouter-research-v1 \
  --head origin/main \
  --output-dir /tmp/math-flow-context

python3 -m math_flow credit-status \
  --problem triangle-midpoints \
  --head origin/main
```

`list-problems` includes newly admitted problems that have no contributions or
projection runs yet. Those entries use `stage: ready-for-first-contribution`;
never infer the available problem set from the projection branch alone. Its
optional `--stage` filter may be repeated.

The context command writes the complete exact `state.json`, machine-readable
freshness and coverage metadata in `context.json`, and a concise `context.md`. Repeated
`--node` arguments scope the Markdown view without truncating the exact state.
The repository-owned [`math-flow-solver`](.agents/skills/math-flow-solver/SKILL.md)
skill explains how an agent should use this context, inspect provenance, and
submit one atomic contribution without mutating judgments or projections.
`credit-status` reads governed policy without requiring a published credit run.
If substantial work warrants an early coordination record, use
`python3 -m math_flow register-direction --help` to scaffold a policy-neutral
initial direction event from a complete Markdown plan.
The
[`math-flow-builder`](.agents/skills/math-flow-builder/SKILL.md) skill covers
protocol, implementation, workflow, schema, viewer, and governance changes in
isolated Git worktrees so multiple builders can work safely in parallel.

To test the repository-backed catalog locally, publish verified bundles into a
temporary projection worktree and run:

```bash
python -m math_flow export-viewer-catalog \
  --projection-dir /path/to/projection-worktree \
  --repository Layr-Labs/math-flow \
  --output /path/to/projection-worktree/viewer/catalog.json
```

Run the tests with:

```bash
python -m unittest discover -s tests -v
cd viewer && npm test && npm run lint
```

## Submitting a contribution

1. Create one new directory under one problem's `contributions/` directory.
2. Add a non-empty `README.md`; put supporting files beside it.
3. Open a pull request. The transaction check rejects edits outside that one new
   directory.
4. The trusted auto-merge workflow re-verifies the atomic diff and squash-merges
   it after all current-head checks pass. That commit is the canonical
   transaction, and its position on the ledger branch is its order.

Problem creation and protocol changes use separate maintainer PRs. They are
validated structurally but are not contribution transactions.

See [docs/MVP.md](docs/MVP.md) for the architecture, decisions, rollout plan, and
known limitations. The generic run envelope and example output profiles are
documented in [docs/PROJECTION_PROTOCOL.md](docs/PROJECTION_PROTOCOL.md).
