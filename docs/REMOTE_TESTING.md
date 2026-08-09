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
`state/delta.json`, `state/state.json`, and `state/revisions.jsonl` before enabling
hosted inference.

## 4. Enable the manual hosted judge

Add `OPENROUTER_API_KEY` as a GitHub Actions repository secret. Manually dispatch
`Project OpenRouter judge` for `triangle-midpoints`. It is intentionally not a
push-triggered workflow so early experiments cannot create surprise inference
spend.

## 5. Exercise the real transaction boundary

Create a branch that adds one new contribution directory, open a pull request, and
confirm `Validate transaction` passes. Also try a deliberately invalid PR that
edits `problem.md` alongside the contribution and confirm it is rejected. Squash-
merge the valid PR, then compare projections at the old and new commit heads.
