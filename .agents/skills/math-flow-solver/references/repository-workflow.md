# Repository workflow

## Contents

- [Create isolated worktrees](#create-isolated-worktrees)
- [Build a verified context](#build-a-verified-context)
- [Inspect provenance](#inspect-provenance)
- [Create one contribution](#create-one-contribution)
- [Validate and hand off](#validate-and-hand-off)
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

## Handoff and cleanup

Push the solver branch from its own worktree and open the PR from that branch.
Report the solver branch and worktree path so another agent can resume safely.
Keep the worktree while work is uncommitted, unpushed, under review, or otherwise
needed for handoff.

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
