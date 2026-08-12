# Provider and transaction testing

The repository has been bootstrapped and pushed. These steps exercise the
commit-addressed judge bundles and real transaction boundary.

## 1. Confirm the bootstrap workflows

Confirm that `Validate repository` and `Project baseline judge` pass. The baseline
workflow should upload a run bundle addressed by the bootstrap commit SHA.

## 2. Protect the ledger branch

Configure a ruleset for `main` that:

- requires pull requests;
- allows squash merge only and requires linear history;
- requires `Validate repository` and `Validate transaction` where applicable;
- blocks force pushes and branch deletion.

The code validates transaction shape; these repository controls make first-parent
history a non-rewritable canonical order.

## 3. Run one local OpenRouter smoke test

First inspect the request without credentials or cost:

```bash
python -m math_flow render-request \
  --problem triangle-midpoints \
  --judge protocol/judges/openrouter-math-review-v1.json \
  --head HEAD \
  --output /tmp/math-flow-openrouter-request.json
```

Then export `OPENROUTER_API_KEY` and run the hierarchical `run` command from the
README. Inspect `run.json`, `report.md`, `control/selection.json`,
`control/normalizations.json`, `state/delta.json`, `state/state.json`, and
`state/revisions.jsonl` before enabling hosted inference.

## 4. Enable the repository projection

Add `OPENROUTER_API_KEY` as a GitHub Actions repository secret. A validated
atomic participant event is squash-merged by
`Auto-merge validated participant transaction`. Contribution merges explicitly
dispatch `OpenRouter repository projection` from `main` for the affected problem;
direction-event merges do not dispatch mathematical projections. The projection
compares the ledger with judgments
published under the active judge spec, fans out one primary judgment for every
uncovered transaction, performs one serialized knowledge build over the
completed batch, publishes the verified bundles and scheduler state to the
orphan `projections` branch, and refreshes `viewer/catalog.json`. Manual
dispatch remains available for recovery and replay.

Before it trusts a reconciliation request, the runner re-derives the conflict
from the supplied immutable primary bundles and requires an exact match. A
content-addressed but forged or stale conflict record therefore fails before a
provider call.

If judgments succeed but a later formation or publication step fails, keep the
original run. After correcting the downstream failure, dispatch the workflow
again with the same projection and problem and set `resume_run_id` to that
earlier GitHub Actions run ID. The recovery dispatch skips paid judgment jobs,
downloads their retained artifacts, and verifies their bundle digests, approved
judge identity, problem-ledger digest, ancestry, and exact planned transaction
coverage before allowing knowledge formation.

The workflow retains a completed knowledge-state artifact before attempting the
GitHub-signed projection commit. Publication ignores only the scheduler's local
`coordination/scheduler.json.lock` synchronization file; any other unexpected
worktree path still fails closed. If publication fails, formation diagnostics
are uploaded after the failure as well.

The `Validate repository` workflow separately runs protocol tests plus the
viewer production-build, rendered-HTML, and lint checks on relevant pushes and
pull requests. The baseline judge continues to discover affected problems, so
unrelated problem pushes do not fan out projection jobs.

## 5. Exercise hosted reconciliation without publishing test state

`Hosted reconciliation smoke test` exercises the production conflict planner,
the pinned OpenRouter reconciliation runner, and post-call artifact verification
without publishing its deliberately fallible primary fixtures. It has read-only
repository permissions and contains no scheduler, formation, or projection
publication step. It must run from canonical `main` and requires an explicit
spend confirmation:

```bash
gh workflow run hosted-reconciliation-smoke.yml \
  --repo Layr-Labs/math-flow \
  --ref main \
  -f confirmation=RUN_HOSTED_RECONCILIATION_SMOKE
```

Find and watch the dispatched run, then download its complete retained evidence:

```bash
gh run list \
  --repo Layr-Labs/math-flow \
  --workflow hosted-reconciliation-smoke.yml \
  --limit 1
gh run watch <run-id> --repo Layr-Labs/math-flow --exit-status
gh run download <run-id> \
  --repo Layr-Labs/math-flow \
  --name hosted-reconciliation-smoke-<run-id> \
  --dir /tmp/math-flow-hosted-reconciliation-smoke
```

The job summary names the verified claim key, conflict ID, reconciliation
judgment ID, outcome, and run digest. The retained artifact also includes all
four primary bundles, the exact conflict record, plans from before and after the
call, and the raw reconciliation report and record. Fixture manifests identify
their resolved model as `fixture/deterministic-primary`; they are not canonical
judgments or knowledge-state inputs.

## 6. Exercise the real transaction boundary

Create a branch that adds one new contribution directory, open a pull request, and
confirm `Validate transaction` passes. Also try a deliberately invalid PR that
edits `problem.md` alongside the contribution and confirm it is rejected. Squash-
confirm that the valid PR is automatically squash-merged after every check
passes, then compare projections at the old and new commit heads.
