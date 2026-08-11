# Repository workflow

## Build a verified context

Fetch both refs from the trusted upstream and create or refresh a separate projection worktree. Choose a path outside the canonical checkout and do not edit it:

```bash
git fetch origin main projections
git worktree add --detach ../math-flow-projection-state origin/projections
```

If the trusted upstream has no `projections` ref yet, stop and report that no
published knowledge state exists. Do not silently substitute another remote;
use one only when the repository owner explicitly designates it as trusted.

For an existing projection worktree, update it without creating a merge:

```bash
git fetch origin main projections
git -C ../math-flow-projection-state switch --detach origin/projections
```

Materialize the context into a new or empty directory:

```bash
python3 -m math_flow context \
  --problem <problem-id> \
  --projection-dir ../math-flow-projection-state \
  --projection <projection-id> \
  --head origin/main \
  --output-dir /tmp/math-flow-context-<problem-id>
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

- transaction IDs are canonical Git commits; inspect with `git show <id>`;
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

## Validate and hand off

Run the contribution's own verifier first. Then run:

```bash
python3 -m math_flow validate-tree
python3 -m unittest discover -s tests -v
python3 -m math_flow validate-pr --base origin/main --head HEAD
```

`validate-pr` expects the branch diff to add exactly one previously absent contribution directory. Protocol changes, new problems, projection definitions, and governance changes require separate maintainer workflows and must not be bundled into a solver transaction.

In the PR description, state the tested commands and results, identify the knowledge node or open question addressed, and disclose any incomplete or non-reproducible parts. Do not claim that submission itself changes the canonical knowledge state; judgments and serialized knowledge formation do that later.

The trusted base-branch workflow re-runs atomic validation, waits for repository,
viewer, transaction, and admission checks on the current head, and automatically
squash-merges a valid solver contribution. It then dispatches the baseline and
approved OpenRouter projection for the affected problem. A failed or missing
check leaves the PR open; do not bypass it by mixing protocol or governance
changes into the contribution.
