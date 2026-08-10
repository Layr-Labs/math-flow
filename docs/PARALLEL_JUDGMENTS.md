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
                                           future hierarchical builder
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

Builder identities are full SHA-256 digests. Triggering is idempotent; repeating
the same judgment or conflict does not duplicate pending work.

```bash
python -m math_flow knowledge-trigger \
  --scheduler-file projections/coordination/scheduler.json \
  --problem triangle-midpoints \
  --builder-digest <sha256-builder-spec-digest> \
  --minimum-interval 600 \
  --judgment-dir projections/staging/judgment-1 \
  --judgment-dir projections/staging/reconciliation-1 \
  --conflicts projections/staging/conflicts.json

python -m math_flow knowledge-claim \
  --scheduler-file projections/coordination/scheduler.json \
  --lane-id <sha256-lane-id> \
  --maximum-judgments 500
```

The claim is null before the lane is eligible. A successful builder later calls
`knowledge-complete`; a failed builder calls `knowledge-fail`, which safely
returns the exact batch to pending work. The actual knowledge-formation adapter
is the next implementation step.

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
