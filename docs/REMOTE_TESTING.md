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

## 3. Run the provider-free congestion probe

Exercise many independent problems, solvers, judge streams, projection lanes,
reconciliation components, failures, retries, stale publications, chunking,
and repository-backed discovery without configuring a provider key:

```bash
python -m math_flow provider-free-scale-probe \
  --problems 12 \
  --projections-per-problem 4 \
  --solvers 12 \
  --minimum-interval 300 \
  --maximum-judgments 64 \
  --output /tmp/math-flow-scale-report.json
```

The command is deterministic apart from temporary paths, reports
`providerCalls: 0`, and exits nonzero if an invariant fails. It gives two
competing claim attempts to every lane, preserves reconciliation dependency
components, coalesces arrivals behind active builds, exercises durable backoff
and new-evidence reset, merges disjoint stale scheduler snapshots, rejects a
same-lane race, plans bounded 100-file publication commits, then constructs a
real multi-problem catalog and materializes agent context for every sampled
lane.

On the reference local run, the default scenario completed with 48 independent
knowledge lanes, 576 primary and 48 reconciliation jobs, 48 simultaneous
cross-lane leases, 48 rejected duplicate same-lane claims, five durable retries,
five new-evidence resets, and a 133,787-byte scheduler. Its modeled catch-up
publication contained 2,256 immutable files split into 23 bounded commits plus
one 14-file metadata commit; all four sampled catalog/context lanes were found.

Important current capacity boundaries are:

- governed primary matrices and knowledge claims are bounded independently;
  the registry currently uses 16 parallel judgments and at most 500 judgments
  per formation claim;
- hosted concurrency is one queue per verified `(problem, primary-judge)`
  stream, so independent judges do not block, while profiles sharing a judge
  deliberately serialize to reuse paid artifacts;
- formation is single-writer only within one projection lane; disjoint lanes
  merge optimistically, but the orphan projection ref remains a final commit
  serialization point with eight publication attempts;
- immutable files chunk across as many 100-file GitHub commits as needed, while
  one metadata commit can contain at most 100 changed indexes/scheduler/catalog
  files; ordinary one-problem publication stays well below that bound;
- the wake-up workflow inspects the newest 1,000 projection runs, so an unusually
  large same-head burst should be monitored for history-window exhaustion.

## 4. Run one local OpenRouter smoke test

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

## 5. Enable the repository projection

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

## 6. Exercise the real transaction boundary

Create a branch that adds one new contribution directory, open a pull request, and
confirm `Validate transaction` passes. Also try a deliberately invalid PR that
edits `problem.md` alongside the contribution and confirm it is rejected. Squash-
confirm that the valid PR is automatically squash-merged after every check
passes, then compare projections at the old and new commit heads.
