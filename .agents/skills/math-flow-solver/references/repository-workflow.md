# Repository workflow

## Contents

- [Create isolated worktrees](#create-isolated-worktrees)
- [Use repository tools, not the UI](#use-repository-tools-not-the-ui)
- [Discover every canonical problem](#discover-every-canonical-problem)
- [Build a verified context](#build-a-verified-context)
- [Inspect provenance](#inspect-provenance)
- [Inspect qualitative credit](#inspect-qualitative-credit)
- [Register a research direction](#register-a-research-direction)
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

If the trusted upstream has no `projections` ref yet, report that no published
knowledge state exists, but continue canonical problem discovery with
`list-problems` and omit `--projection-dir`. Do not silently substitute another
remote; use one only when the repository owner explicitly designates it as
trusted.

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

- use `python3 -m math_flow list-problems` to enumerate canonical admissions,
  including admitted problems that have no contributions or projection runs;
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

## Discover every canonical problem

Never derive the available problem set from `origin/projections`. That branch
contains published interpretation artifacts, not the canonical admission
registry. In particular, a newly admitted problem is intentionally absent until
its first contribution produces a knowledge run.

After creating the worktrees, join canonical admissions with verified
projection status:

```bash
problem_index="${TMPDIR:-/tmp}/math-flow-problems-$agent_task.json"
cd "$solver_worktree"
python3 -m math_flow list-problems \
  --head origin/main \
  --projection-dir "$projection_worktree" \
  --output "$problem_index"
```

To answer “what problems need work?”, inspect all entries, not only projected
ones. Useful filters include:

```bash
python3 -m math_flow list-problems \
  --head origin/main \
  --projection-dir "$projection_worktree" \
  --stage ready-for-first-contribution
```

Interpret stages as follows:

- `ready-for-first-contribution`: admitted with an empty canonical contribution
  ledger; read `statementPath` from `origin/main` and propose bounded initial
  work without trying to materialize context;
- `knowledge-pending`: contributions exist but no active knowledge run is
  published yet;
- `knowledge-stale`: a verified active run exists but misses canonical
  contributions;
- `knowledge-current`: at least one active knowledge projection matches the
  canonical contribution ledger and can be passed to `context`;
- `projection-unchecked`: projection verification was omitted, so inspect the
  trusted projection ref before making claims about knowledge status.

`activeKnowledgeProjectionIds` lists governed knowledge profiles even before
their first run. `activeOverlayProjectionIds` lists dependent overlays such as
credit; their presence does not imply a published assessment. Read an exact
problem statement with:

```bash
git -C "$solver_worktree" show \
  "origin/main:problems/<problem-id>/problem.md"
```

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

When multiple governed credit overlays apply, the first snapshot reports
`credit.status` as `selection-required`. Materialize a new snapshot with the
chosen overlay rather than editing the output:

```bash
python3 -m math_flow context \
  --problem <problem-id> \
  --projection-dir "$projection_worktree" \
  --projection <knowledge-projection-id> \
  --credit-projection <credit-projection-id> \
  --head origin/main \
  --output-dir <new-empty-context-dir>
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

`context.json` distinguishes primary judgments included in the state chain, transactions represented in state provenance, scheduler inputs still pending formation, objective-verification status, and a summary of active, released, and completed research directions. `directions.json` contains the exact canonical direction-event ledger, while `attestations.json` contains verified pending/passed/failed objective checks and bounded output previews. These are operational signals, not mathematical verdicts. A passing attestation establishes only that the pinned checker accepted its encoded predicate.

## Inspect provenance

Use the identifiers in `state.json` and `context.json` rather than relying on prose alone:

- transaction IDs are canonical Git commits; inspect with
  `git -C "$solver_worktree" show <id>`;
- judgment IDs identify immutable judgment records and reports on the projection branch;
- node and state digests protect materialized content;
- the latest run digest and its `baseRun` chain identify state history.

Never edit or regenerate these records as part of a solver contribution.

## Inspect qualitative credit

Read `credit.json` before choosing a research direction. The context command
discovers active governed credit overlays at the canonical head and verifies
published candidates with the repository's credit-bundle loader. It never
calls a model. Interpret `credit.status` exactly:

- `current`: one verified run matches the same governed credit projection,
  problem ledger, producer runs, and dependency artifacts; its assignments are
  authoritative for this snapshot even if unrelated repository commits changed
  the lock's audit-only canonical head;
- `pending`: the governed overlay or its knowledge dependency is ready or in
  progress, but no current scoring run is published yet;
- `stale`: a uniquely latest verified historical run is shown, but its governed
  projection or dependency state differs; do not use it as current scoring;
- `invalid`: indexed scoring objects exist but fail canonical verification;
- `ambiguous`: multiple equally applicable runs exist and no overlay terminal
  selects one; do not choose by digest, file order, or prose;
- `selection-required`: rerun with `--credit-projection <id>`;
- `unavailable`: no governed overlay applies or a required dependency cannot be
  resolved.

For `current`, inspect `credit-report.md` and follow identifiers rather than
guessing from prose:

- `transactionId` and `path` identify the canonical contribution evidence;
- `knowledgeRefs` identify exact current node/revision pairs;
- `directionRegistrationTransactionIds` identify exact prior canonical
  `register` events in a registration-aware credit profile;
- `reservationTransactionIds` are legacy credit-v1 references to ordinary
  contributions that the older assessment interpreted as informal reservations;
- `reportSection` identifies the detailed rationale in the raw report.

Credit is qualitative and non-zero-sum. A `major`, `minor`, or `none`
assignment neither accepts nor rejects mathematics, and multiple contributions
may receive substantial credit. Never use credit to override a judgment or
knowledge node. Do not fabricate reservation priority: follow only exact
canonical transaction references present in the verified assignment.

## Register a research direction

First inspect the canonical state without a web UI:

```bash
python3 -m math_flow directions \
  --problem <problem-id> \
  --head origin/main \
  --status active
```

Register only substantial, bounded work. Registration is optional and
non-exclusive: it records specific intent and priority evidence, but it does not
reserve ownership, prevent overlap, establish correctness, or replace a
mathematical contribution. Prefer one direction that another solver could
distinguish from neighboring work.

Create exactly one new event directory in a dedicated branch and PR:

```text
problems/<problem-id>/directions/<direction-id>/events/<event-id>/
  README.md
  event.json
```

For an initial registration, use the complete current snapshot:

```json
{
  "schemaVersion": 1,
  "eventType": "register",
  "eventId": "initial-plan",
  "directionId": "modular-construction",
  "title": "Modular construction",
  "summary": "Search a specified modular family for a verifiable construction.",
  "relatedKnowledgeNodeIds": ["program/modular-search"]
}
```

Put the detailed scope, method, expected evidence, overlap with prior work, and
clear completion criterion in `README.md`. Node IDs must be exact current IDs;
sort them lexicographically. Run `validate-tree`, commit the two files, and run:

```bash
python3 -m math_flow validate-pr --base origin/main --head HEAD
```

The result must report `transactionKind: direction-event`. Push one PR and let
the trusted workflow squash-merge it. Record that squash commit before starting
if priority timing matters. A registration merge does not dispatch mathematical
judgment or knowledge formation; it triggers only a provider-free viewer-catalog
refresh. Re-fetch `origin/main` and re-materialize context rather than waiting on
a knowledge run.

Later lifecycle events are separate atomic PRs in the same direction. Each must
name the current `previousEventId`; concurrent stale successors are rejected:

- `update` supplies a new complete `title`, `summary`, and sorted
  `relatedKnowledgeNodeIds` snapshot;
- `release` supplies a non-empty `reason` and permanently closes this event
  chain;
- `complete` supplies a summary and canonical, ledger-ordered
  `contributionTransactionIds`, and permanently closes the chain.

Do not edit old events. Do not combine a direction event with a contribution.
Released or completed directions cannot be reopened in v1; create a newly named
direction if genuinely new work resumes.

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
absent contribution directory or exactly one two-file direction event.
Protocol changes, new problems, projection definitions, and governance changes
require separate maintainer workflows and must not be bundled into a participant
transaction.

In the PR description, state the tested commands and results, identify the knowledge node or open question addressed, and disclose any incomplete or non-reproducible parts. Do not claim that submission itself changes the canonical knowledge state; judgments and serialized knowledge formation do that later.

The trusted base-branch workflow re-runs atomic validation, waits for repository,
viewer, transaction, and admission checks on the current head, and automatically
squash-merges a valid contribution or direction event. It dispatches baseline
and approved mathematical projections only for a contribution. A failed or
missing check leaves the PR open; do not bypass it by mixing protocol or
governance changes into the participant transaction.

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
