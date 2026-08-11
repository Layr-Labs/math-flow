# Repository workflow

## Contents

- [Create isolated worktrees](#create-isolated-worktrees)
- [Use repository tools, not the UI](#use-repository-tools-not-the-ui)
- [Build a verified context](#build-a-verified-context)
- [Inspect provenance](#inspect-provenance)
- [Create one contribution](#create-one-contribution)
- [Validate and hand off](#validate-and-hand-off)
- [After submission](#after-submission)
- [Understand coordination lanes](#understand-coordination-lanes)
- [Handoff and cleanup](#handoff-and-cleanup)

## Create isolated worktrees

Treat the checkout where the task started as a shared control checkout. Other
agents or the owner may be using it. Inspect it and the registered worktrees
before doing anything else:

```bash
control_checkout=$(git rev-parse --show-toplevel)
git -C "$control_checkout" status --short --branch
git -C "$control_checkout" worktree list --porcelain
```

Do not edit files, switch branches, reset, clean, stash, commit, or run the
solver from that shared checkout. A dirty shared checkout is not a blocker and
must be left unchanged.

Fetch both refs from the owner-designated trusted upstream:

```bash
git -C "$control_checkout" fetch origin main projections
```

If the trusted upstream has no `projections` ref yet, stop and report that no
published knowledge state exists. Do not silently substitute another remote;
use one only when the repository owner explicitly designates it as trusted.

Choose a unique agent/task identifier containing only safe branch/path
characters. Create a writable solver worktree from canonical `main` and a
separate detached projection worktree. The paths and branch must not already
exist:

```bash
worktree_root="${TMPDIR:-/tmp}/math-flow-worktrees"
mkdir -p "$worktree_root"

agent_task="<agent-id>-<problem-id>-<short-task>-<unique-id>"
solver_branch="solver/$agent_task"
solver_worktree="$worktree_root/$agent_task"
projection_worktree="$worktree_root/$agent_task-projection"

git -C "$control_checkout" worktree add \
  -b "$solver_branch" "$solver_worktree" origin/main
git -C "$control_checkout" worktree add \
  --detach "$projection_worktree" origin/projections
```

Do not reuse a convenient existing worktree: its owner may update or remove it
while this task is running. Worktree isolation covers files and `HEAD`, but all
worktrees still share refs and Git objects. Unique branch and directory names
prevent agents from colliding in that shared metadata.

From this point on, run edits, artifact tools, tests, commits, and pushes with
`$solver_worktree` as the working directory. Use `$projection_worktree` only as
read-only published input. Do not switch its detached `HEAD` while a context
command is reading it.

## Use repository tools, not the UI

Complete repository work through machine-readable tools:

- use `python3 -m math_flow context` for the verified current knowledge state,
  freshness, coverage, and scheduler status;
- read `context.json`, `state.json`, and the content-addressed records in the
  detached projection worktree for provenance and raw judgments;
- use `python3 -m math_flow ledger` and `git show` for canonical transactions;
- use `git` for branches, commits, worktrees, fetches, and pushes;
- use `gh` or an available GitHub connector/API for PR creation, PR metadata,
  checks, workflow runs, and artifacts.

Do not open or automate the deployed research atlas or GitHub website for these
operations. Do not scrape UI text, copy UI-derived state into a contribution,
click merge buttons, or ask the user to perform routine browser steps. In
particular, never use `viewer/app/math-flow-data.json` as current state; it is a
development/outage fallback.

Browsing external mathematical literature is allowed when research requires
it. Cite and attribute those sources in the contribution. If `math_flow`, `git`,
or an authenticated GitHub CLI/connector is unavailable, stop and report the
specific tool or authentication blocker rather than falling back to the web UI.

## Build a verified context

To refresh this agent's projection worktree before context materialization,
fetch in the control checkout and move only this agent's detached worktree:

```bash
git -C "$control_checkout" fetch origin main projections
git -C "$projection_worktree" switch --detach origin/projections
```

Materialize context into a unique output directory outside both worktrees:

```bash
context_dir="${TMPDIR:-/tmp}/math-flow-context-$agent_task"
cd "$solver_worktree"
python3 -m math_flow context \
  --problem <problem-id> \
  --projection-dir "$projection_worktree" \
  --projection <projection-id> \
  --head origin/main \
  --output-dir "$context_dir"
```

Omit `--projection` only when exactly one projection exists. To reduce the Markdown payload while retaining the full verified `state.json`, repeat a subtree selector:

```bash
  --node <node-id> --node <another-node-id>
```

Interpret freshness as follows:

- `current`: the projected and canonical problem-ledger digests match, even if unrelated repository commits differ.
- `stale`: the projection is an ancestor and misses canonical problem changes.
- `ahead`: the chosen canonical head predates the projection.
- `diverged`: the histories do not form an ancestor chain.

`context.json` distinguishes primary judgments included in the state chain, transactions represented in state provenance, and scheduler inputs still pending formation. These are operational signals, not mathematical verdicts.

## Inspect provenance

Use the identifiers in `state.json` and `context.json` rather than relying on prose alone:

- transaction IDs are canonical Git commits; inspect with
  `git -C "$solver_worktree" show <id>`;
- judgment IDs identify immutable judgment records and reports on the projection branch;
- node and state digests protect materialized content;
- the latest run digest and its `baseRun` chain identify state history.

Never edit or regenerate these records as part of a solver contribution.

## Create one contribution

Choose lowercase hyphenated IDs and create only:

```text
problems/<problem-id>/contributions/<contribution-id>/
  README.md
  ... supporting files
```

Include in `README.md`:

1. the precise claim, bound, counterexample, or research question;
2. the argument or method and its assumptions;
3. links or transaction IDs for reused prior work;
4. exact commands needed to reproduce computational evidence;
5. known gaps, failed checks, and limitations;
6. authorship and external-source attribution.

Prefer exact checkers, proof-assistant files, small certificates, and deterministic seeds over unverifiable transcripts. Inspect submitted code before running it, and do not include secrets, generated environment files, or model credentials.

Create and edit these files only under `$solver_worktree`. Before committing,
confirm that the shared control checkout still has not been touched and that the
solver worktree contains no paths outside the one contribution directory.

## Validate and hand off

Run the contribution's own verifier first. Validate the worktree before
committing:

```bash
cd "$solver_worktree"
python3 -m math_flow validate-tree
python3 -m unittest discover -s tests -v
git diff --check
git status --short
```

Inspect the diff, commit only the one contribution directory, and then validate
the committed PR shape:

```bash
python3 -m math_flow validate-pr --base origin/main --head HEAD
```

`validate-pr` expects the committed branch diff to add exactly one previously
absent contribution directory. Protocol changes, new problems, projection
definitions, and governance changes require separate maintainer workflows and
must not be bundled into a solver transaction.

In the PR description, state the tested commands and results, identify the knowledge node or open question addressed, and disclose any incomplete or non-reproducible parts. Do not claim that submission itself changes the canonical knowledge state; judgments and serialized knowledge formation do that later.

The trusted base-branch workflow re-runs atomic validation, waits for repository,
viewer, transaction, and admission checks on the current head, and automatically
squash-merges a valid solver contribution. It then dispatches the baseline and
approved OpenRouter projection for the affected problem. A failed or missing
check leaves the PR open; do not bypass it by mixing protocol or governance
changes into the contribution.

## After submission

A green PR means the contribution is valid, not that judgment and knowledge
formation are complete. Close the loop with repository tools.

First wait for automatic merge and record the canonical squash commit:

```bash
pr_number=<pull-request-number>
merge_commit=$(gh pr view "$pr_number" \
  --json state,mergeCommit \
  --jq 'select(.state == "MERGED") | .mergeCommit.oid')
test -n "$merge_commit"
```

Fetch both authoritative refs. A new projection commit normally has a message
of the form `Publish <projection>/<problem> from run <run-id>`; use this only as
an operational signal, not as proof that the submission is covered:

```bash
git -C "$control_checkout" fetch origin main projections
git -C "$control_checkout" log -n 10 --format='%H %s' \
  --grep="^Publish <projection-id>/<problem-id> from run " \
  origin/projections
git -C "$projection_worktree" switch --detach origin/projections
```

Materialize context into a new empty directory on every poll; the context tool
deliberately refuses to overwrite an existing snapshot:

```bash
after_context="${TMPDIR:-/tmp}/math-flow-after-$agent_task-<unique-poll-id>"
cd "$solver_worktree"
python3 -m math_flow context \
  --problem <problem-id> \
  --projection-dir "$projection_worktree" \
  --projection <projection-id> \
  --head origin/main \
  --output-dir "$after_context"
```

Inspect the receipt fields without a web UI:

```bash
jq --arg transaction "$merge_commit" '{
  freshness: .freshness.status,
  projectedProblemLedgerHead: .freshness.projectedProblemLedgerHead,
  missingFromProjection:
    (.freshness.canonicalTransactionsMissingFromProjection | index($transaction)),
  missingPrimaryJudgment:
    ([.coverage.canonicalTransactionsWithoutBuiltPrimaryJudgment[].transactionId]
      | index($transaction)),
  missingFromState:
    ([.coverage.canonicalTransactionsNotRepresentedInState[].transactionId]
      | index($transaction)),
  coordination: .coordination
}' "$after_context/context.json"
```

Interpret the receipt in stages:

- canonical projection coverage is complete when `missingFromProjection` is
  `null` (`jq index` uses null to mean absent);
- primary judgment is published when `missingPrimaryJudgment` is `null`;
- knowledge formation represents the transaction in current state provenance
  when `missingFromState` is `null`;
- `freshness` is `current`, unless a known later same-problem contribution has
  made the just-fetched projection stale again;
- `projectedProblemLedgerHead` equals the merge commit when it is still the
  latest transaction for that problem, or is a later descendant that includes
  it.

The expected full lifecycle has all three missing fields null. If primary
judgment is present but state representation remains missing after the lane is
quiescent, report that formation outcome rather than resubmitting the same work
or polling forever; a builder may have omitted a transaction that produced no
durable state change, or formation may need maintainer attention.

Check the last condition robustly when other submissions may have merged:

```bash
projected_problem_head=$(jq -r \
  '.freshness.projectedProblemLedgerHead' "$after_context/context.json")
git -C "$solver_worktree" merge-base --is-ancestor \
  "$merge_commit" "$projected_problem_head"
```

To locate the raw primary judgment, search the detached projection objects for
the merge commit, then use `jq` to confirm it is a primary judgment whose
subjects contain that transaction. Read the sibling `report.md` for the full
assessment:

```bash
while IFS= read -r judgment_record; do
  jq --arg transaction "$merge_commit" --arg record "$judgment_record" '
    select(
      .judgmentKind == "primary"
      and any(.subjects[]?;
        .kind == "transaction" and .id == $transaction)
    )
    | {record: $record, judgmentId, findings}
  ' "$judgment_record"
done < <(
  rg -l --fixed-strings "$merge_commit" \
    "$projection_worktree/objects/judgment" -g judgment.json
)
```

Do not treat every matching file as the subject judgment: a transaction may
also appear as evidence. For a selected record, read `report.md` in the same
directory for the full assessment. If the receipt is incomplete, refresh the
refs and materialize another context snapshot later. Do not rerun or manually
merge the hosted projection from a solver task.

## Understand coordination lanes

`context.json.coordination` summarizes the scheduler lane for one logical
`(problem, projection)` knowledge chain:

- `laneId` is the stable digest identity of that problem and registered
  projection. It is not a solver lock or a Git branch.
- `pendingJudgmentIds` and `pendingConflictIds` are completed immutable inputs
  observed by the scheduler but not yet claimed into a formation batch.
- `activeBuild` is the exact leased batch currently constructing the next
  serialized state. Claimed inputs move out of pending while it is active.
- `nextEligibleAt` is the earliest Unix timestamp at which pending inputs may be
  claimed. It is null when no build is scheduled and also while `activeBuild`
  owns the lane; interpret it together with the other fields.

Do not delay or withhold a valid solver submission because `activeBuild` is
non-null. The lease serializes knowledge-state construction only. Contributions
may merge and primary judgments may run in parallel; judgments completed during
an active build stay pending for the next eligible coalesced build. A failed
build returns its claimed inputs to pending. Nonempty pending arrays or an
active build may belong to other concurrent submissions, so they do not by
themselves show that this solver's transaction is incomplete—use the receipt
checks above.

## Handoff and cleanup

Push the solver branch from its own worktree and open the PR from that branch
with `gh pr create` or an available GitHub connector. Use `gh pr checks` or the
connector to monitor validation; do not open GitHub in a browser. Report the
solver branch and worktree path so another agent can resume safely. Keep the
worktree while work is uncommitted, unpushed, under review, or otherwise needed
for handoff.

An agent may remove only the two worktrees it created. First verify the solver
worktree is clean and its commits are pushed:

```bash
git -C "$solver_worktree" status --short --branch
git -C "$control_checkout" worktree remove "$projection_worktree"
git -C "$control_checkout" worktree remove "$solver_worktree"
```

Do not pass `--force`. If removal refuses, stop and preserve the worktree. Do not
delete the solver branch, prune shared worktree metadata, or remove any path
listed for another agent unless the repository owner explicitly asks.
