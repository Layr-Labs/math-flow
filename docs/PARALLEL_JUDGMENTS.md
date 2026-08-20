# Parallel judgments MVP

The new execution path separates expensive, parallelizable mathematical work
from intentionally serialized knowledge formation.

```text
contributions
    ├── validity judgment ─┐
    ├── validity judgment ─┼─ dependency-safe coalescing lane
    └── validity judgment ─┘                 │
                                             ▼
                              batched hierarchical formation
```

This is the default validity-v2 path. The additive validity-v3 path preserves
the same parallel topology while narrowing dependency and objective-attestation
semantics. Legacy judgment projections may still insert conflict detection and
reconciliation before formation.

## Run a primary judgment

Use one command per independently adjudicated subject. The legacy v1 judge may
receive additional transactions as evidence without making them subjects:

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

The v2 validity judge has a narrower contract:

```bash
python -m math_flow judgment \
  --problem bssc-sum-capacity \
  --judge protocol/judges/openrouter-validity-judgment-v2.json \
  --head HEAD \
  --subject <transaction-sha> \
  --projection-dir /path/to/projections-worktree \
  --output-dir projections/staging/judgment-1
```

It accepts exactly one subject and rejects `--evidence`. A contribution may
declare claims in an optional `claims.json`; each claim supplies a stable
`claimKey`, its exact statement, and prior canonical transaction IDs on which it
depends. Existing contributions remain compatible: the runner derives one claim
from the first `## Claim`, `## Claims`, `## Claim and scope`, or
`## Claims and exact scope` section, falling back to the full README, and treats
full prior transaction IDs cited there as explicit dependencies.

The runner writes a content-addressed `dependency-packet.json`. It contains the
declared claims, only their declared prior transactions, and—when available—only
nodes from a historical knowledge state that cite those dependencies. The state
must precede the subject; the current state and the rest of the contribution
ledger are never sent.

The judge's overriding objective is to prevent false acceptance. It audits every
material inference, hypothesis, quantifier, domain restriction, edge case,
calculation, and dependency application, and it may decompose the proof into as
many intermediate obligations as rigorous verification requires. A claim is
valid only after affirmative verification; decisive defects produce `invalid`,
and unresolved material obligations produce `indeterminate`.

The output still has one assessment and one derived routing finding per declared
claim, but this is only an identity and indexing invariant. It does not limit the
depth or breadth of the mathematical audit. Missing premises, proof defects, and
scope qualifications remain attached to that assessment rather than becoming
new top-level claim identities. Novelty, global placement, program organization,
and cumulative state remain the knowledge builder's responsibility.

### Frozen validity-v3 boundary

Validity v3 separates a contribution's declared references from the premises
that its proof actually needs. Every prior transaction cited by the claim is
recorded in `declaredReferenceTransactionIds` and supplied to the judge. The
judge returns `requiredDependencyTransactionIds`, an exact subset containing
only results that must already be valid for the current argument to establish
the claim. Attribution-only citations and arguments fully restated in the
current submission remain provenance, not formation edges.

Formation consumes only the judge-selected required set. A required submission
must have a valid judgment and already belong to research state. Invalid and
indeterminate submissions are excluded completely, while all declared
references remain in immutable judgment/build history for later credit analysis.
This contract is versioned; validity-v2 packets keep their legacy dependency
semantics.

A v3 subject that declares objective verification is deferred until its exact
content-addressed request has a verified terminal attestation. Coverage reports
it in `deferredTransactions` rather than the judgment matrix. This is a
subject-local gate: unrelated ordinary subjects remain in the matrix and run in
parallel. Passing and failing terminal outcomes both unblock the judge, which
receives the attestation as evidence rather than as a verdict. The packet,
judgment identity, and manifest inputs bind the attestation run digest. Terminal
publication redispatches the applicable active v3 streams so the deferred
subject is reconsidered automatically.

See `docs/HIERARCHICAL_RESEARCH_PROTOCOL_V3.md` for the complete frozen contract
and rollout boundary.

Before dispatching work, automation can compare the canonical problem ledger
with the published projection index:

```bash
python -m math_flow judgment-plan \
  --problem triangle-midpoints \
  --judge protocol/judges/openrouter-markdown-judgment-v1.json \
  --head HEAD \
  --projection-dir /path/to/projections-worktree \
  --output /tmp/judgment-plan.json
```

Coverage is scoped to the full judge-spec digest: a primary judgment from an
older or different judge remains part of history but does not satisfy the active
judge's queue. The output contains a GitHub-compatible matrix with one entry for
every uncovered transaction. Those judgments may execute in parallel because
they do not read or mutate a base knowledge state.

## Detect and reconcile conflicts (legacy projections)

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

The hosted projection workflow performs this stage automatically after it has
reconstructed and verified the complete current primary-judgment set. It derives
conflicts deterministically, reuses matching content-addressed reconciliation
bundles already published for the same judge identities, and fans out only the
missing reconciliations. Each OpenRouter reconciliation request contains the
derived conflict record, the relevant immutable primary judgment reports, and
the canonical subject evidence required to compare them; it does not receive an
unrestricted repository snapshot. Independent missing conflicts are reconciled
in parallel, after which knowledge formation remains serialized per lane.

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
location. A structured extraction that references no matching Markdown section
is rejected and retried once without regenerating the selection or report; both
attempts remain visible in `providerRuns`. The formation schema also prevents
context-only evidence from being promoted into an adjudication subject.

Complete the scheduler lease only after the bundle verifies:

```bash
python -m math_flow knowledge-complete \
  --scheduler-file projections/coordination/scheduler.json \
  --lane-id <sha256-lane-id> \
  --build-token <sha256-build-token> \
  --state-run-dir projections/staging/knowledge-build-1
```

A failed builder calls `knowledge-fail`, which safely returns the exact batch to
pending work and records a durable failure marker. Automatic retries start after
five minutes, back off exponentially to a six-hour ceiling, and stop after five
failures for the same claim and problem ledger. A successful build, new inputs,
or a changed problem ledger resets the marker. `knowledge-complete
--state-run-dir` verifies the bundle and derives its manifest digest, avoiding a
manual digest-copy step.

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

GitHub limits one `createCommitOnBranch` call to 100 file changes. The repository
publisher therefore writes large sets of immutable object and batch files in
bounded GitHub-signed commits, then writes mutable indexes, scheduler state, and
the viewer catalog in a final commit. A partial attempt can leave only harmless
unindexed immutable objects; retrying from the newest branch head is idempotent.

After updating the scheduler's authoritative state tip, the publisher can build
the repository viewer catalog from those indexes:

```bash
python -m math_flow export-viewer-catalog \
  --projection-dir <projection-branch-worktree> \
  --repository <owner/repository> \
  --canonical-ref main \
  --projection-ref projections \
  --output <projection-branch-worktree>/viewer/catalog.json
```

The catalog follows `baseRun` content digests and uses each scheduler lane's
`latestStateRun` as its authoritative terminal. Git publication order therefore
does not become knowledge-state order. The included OpenRouter repository
projection workflow fans out every missing primary judgment and coalesces
dependency-complete artifacts into one formation claim. Workflow runs are not
globally serialized by problem or judge stream, so independent submissions may
be judged concurrently even when they arrive in separate runs. Legacy
projections still derive conflicts and reuse or fan out reconciliations.
Formation leases and base-run checks remain serialized only within each
projection-specific knowledge lane.
Publication snapshots its lane update, three-way merges that
disjoint lane onto the newest orphan-branch scheduler, and retries optimistic
GitHub-signed publication when another problem wins the expected-head race.
Automatic dispatch partitions the sorted active projection list by verified
judgment stream. It starts those queues independently, while each workflow
dispatches the next projection sharing its stream even when its own formation
or publication fails. A five-minute repository wake-up pass
rediscovers eligible, never-started, and stale active lanes from repository
state, so minimum intervals, multi-batch formation, interrupted queues, failed
builders, and replaced GitHub pending runs recover without an unrelated
contribution. The wake-up pass also checks same-head workflow history: an active
run suppresses a duplicate dispatch, and five consecutive pre-formation failures
stop automatic retries for that projection without blocking other projections.
Direct workflow dispatch remains available for an operator retry.
Redispatching an already-current lane is a successful no-op. A newly registered
knowledge lane still forms from the complete inherited judgment set even when
the missing-judgment count is zero, and a dirtied but temporarily ineligible
lane publishes its pending scheduler state without invoking the builder.
