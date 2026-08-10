# Parallel judgments MVP

The new execution path separates expensive, parallelizable mathematical work
from intentionally serialized knowledge formation.

```text
contributions
    ├── primary judgment ─┐
    ├── primary judgment ─┼─ conflict detection ─ reconciliation judgments
    └── primary judgment ─┘                              │
                                                        ▼
                                          coalescing knowledge-build lane
                                                        │
                                                        ▼
                                      serialized hierarchical formation
```

## Run a primary judgment

Use one command per independently adjudicated subject. Additional transactions
may be supplied as evidence without becoming subjects:

```bash
python -m math_flow judgment \
  --problem triangle-midpoints \
  --judge protocol/judges/openrouter-markdown-judgment-v1.json \
  --head HEAD \
  --subject <transaction-sha> \
  --evidence <earlier-transaction-sha> \
  --output-dir projections/staging/judgment-1
```

The resulting bundle contains `report.md`, `judgment.json`, and `run.json` with
`runKind: judgment`. It has no `baseRun` and performs no knowledge-state update.
The manifest records both the repository-wide ledger head and a
`problemLedgerDigest`, so unrelated problem commits do not invalidate scheduling
or caches for this problem.

## Detect and reconcile conflicts

```bash
python -m math_flow detect-conflicts \
  --judgment-dir projections/staging/judgment-1 \
  --judgment-dir projections/staging/judgment-2 \
  --output projections/staging/conflicts.json

python -m math_flow reconcile \
  --problem triangle-midpoints \
  --judge protocol/judges/openrouter-markdown-reconciliation-v1.json \
  --head HEAD \
  --conflicts projections/staging/conflicts.json \
  --conflict-id <sha256-conflict-id> \
  --judgment-dir projections/staging/judgment-1 \
  --judgment-dir projections/staging/judgment-2 \
  --output-dir projections/staging/reconciliation-1
```

Detection only routes opposed findings. The reconciliation call performs the
mathematical comparison and emits another immutable judgment bundle.

## Coalesce knowledge-build triggers

Builder identities are full SHA-256 digests. The CLI can derive the digest from
the builder spec. Triggering is idempotent; repeating the same judgment or
conflict does not duplicate pending work.

```bash
python -m math_flow knowledge-trigger \
  --scheduler-file projections/coordination/scheduler.json \
  --problem triangle-midpoints \
  --builder protocol/judges/openrouter-knowledge-builder-v1.json \
  --minimum-interval 600 \
  --judgment-dir projections/staging/judgment-1 \
  --judgment-dir projections/staging/reconciliation-1 \
  --conflicts projections/staging/conflicts.json \
  --output projections/staging/knowledge-lane.json

python -m math_flow knowledge-claim \
  --scheduler-file projections/coordination/scheduler.json \
  --lane-id <sha256-lane-id> \
  --maximum-judgments 500 \
  --output projections/staging/knowledge-claim.json
```

The claim is null before the lane is eligible. It binds the exact base state,
judgment IDs, conflict IDs, builder digest, and a deterministic build token.
New completions during an active build remain pending for the next eligible
interval.

## Form the next knowledge state

Run the included example builder against the exact claimed batch:

```bash
python -m math_flow knowledge-build \
  --problem triangle-midpoints \
  --builder protocol/judges/openrouter-knowledge-builder-v1.json \
  --head HEAD \
  --claim projections/staging/knowledge-claim.json \
  --judgment-dir projections/staging/judgment-1 \
  --judgment-dir projections/staging/reconciliation-1 \
  --conflicts projections/staging/conflicts.json \
  --output-dir projections/staging/knowledge-build-1
```

For later builds, also pass the prior state bundle named by the claim:

```bash
  --base-run projections/staging/knowledge-build-1
```

The adapter writes unconstrained Markdown plus a sparse structured delta. It is
not allowed to redo mathematical adjudication. It can organize unopposed primary
findings and supplied reconciliation outcomes; every claimed conflict without a
single resolving reconciliation outcome must be cited by an active `dispute`
operation. The runner enforces that invariant before applying the deterministic
revision reducer.

Each provider stage is cached by request digest in a sibling checkpoint
directory. If a later stage is truncated or rejected, rerunning the same command
reuses successful earlier stages. Pass `--checkpoint-dir` to choose another
location. The formation schema also prevents context-only evidence from being
promoted into an adjudication subject.

Complete the scheduler lease only after the bundle verifies:

```bash
python -m math_flow knowledge-complete \
  --scheduler-file projections/coordination/scheduler.json \
  --lane-id <sha256-lane-id> \
  --build-token <sha256-build-token> \
  --state-run-dir projections/staging/knowledge-build-1
```

A failed builder calls `knowledge-fail`, which safely returns the exact batch to
pending work. `knowledge-complete --state-run-dir` verifies the bundle and derives
its manifest digest, avoiding a manual digest-copy step.

## Batch projection publication

```bash
python -m math_flow publish-batch \
  --projection-dir <projection-branch-worktree> \
  --bundle projections/staging/judgment-1 \
  --bundle projections/staging/reconciliation-1
```

The publisher verifies every manifest, digest, byte count, undeclared file, and
symlink before creating content-addressed objects, per-problem indexes, and an
idempotent publication-batch record. One automation process can commit these
batches to an orphan projection branch at its own cadence.
