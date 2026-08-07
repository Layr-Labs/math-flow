# First remote and provider test

The local protocol and OpenRouter adapter are mock-tested. The next useful test
requires real Git commits because commit SHAs are transaction IDs and ledger heads.
That makes **now** the right point to create the GitHub remote.

## 1. Establish the bootstrap commit

Review the untracked files, then create one initial commit containing the protocol,
sample problem, and sample contribution. This bootstrap establishes the first
ledger head. The workspace is already initialized on the `main` branch.

No API key belongs in the commit. `.env` is ignored; `.env.example` is intentionally
empty.

## 2. Create and push the GitHub repository

Create an empty GitHub repository, add it as `origin`, and push `main`. Do not add a
GitHub-generated README or license during remote creation, since the local tree
already contains the bootstrap files.

Confirm that `Validate repository` and `Project baseline judge` pass. The baseline
workflow should upload a projection addressed by the bootstrap commit SHA.

## 3. Protect the ledger branch

Configure a ruleset for `main` that:

- requires pull requests;
- allows squash merge only and requires linear history;
- requires `Validate repository` and `Validate transaction` where applicable;
- blocks force pushes and branch deletion.

The code validates transaction shape; these repository controls make first-parent
history a non-rewritable canonical order.

## 4. Run one local OpenRouter smoke test

First inspect the request without credentials or cost:

```bash
python -m math_flow render-request \
  --problem triangle-midpoints \
  --judge protocol/judges/openrouter-math-review-v1.json \
  --head HEAD \
  --output /tmp/math-flow-openrouter-request.json
```

Then export `OPENROUTER_API_KEY` and run the matching `project` command from the
README. Inspect the resulting verdict, request digest, resolved model, usage, and
projection digest before enabling hosted inference.

## 5. Enable the manual hosted judge

Add `OPENROUTER_API_KEY` as a GitHub Actions repository secret. Manually dispatch
`Project OpenRouter judge` for `triangle-midpoints`. It is intentionally not a
push-triggered workflow so early experiments cannot create surprise inference
spend.

## 6. Exercise the real transaction boundary

Create a branch that adds one new contribution directory, open a pull request, and
confirm `Validate transaction` passes. Also try a deliberately invalid PR that
edits `problem.md` alongside the contribution and confirm it is rejected. Squash-
merge the valid PR, then compare projections at the old and new commit heads.
