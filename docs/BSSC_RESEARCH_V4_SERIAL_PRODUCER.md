# BSSC research-v4 serial producer

Status: provider-free producer implementation with an inactive hosted-workflow
template. This change does not admit a governed projection, call a provider, or
publish a run.

The producer is the one allowed path from the historical BSSC validity-v4
record to the new builder-v6 knowledge chain. It starts at the structural K0
state and publishes exactly K1 through K16, one accepted canonical submission
per run. The nine excluded submissions do not create a knowledge state.

## Immutable source and frontier

`protocol/runtime/bssc-research-v4-validity-source-v1.json` pins the canonical
25-submission ledger and the projection commit containing the already published
validity-v4 bundles. `math_flow.bssc_research_v4_producer` verifies those Git
objects, reconstructs the full historical formation disposition, and requires
accepted ledger ordinals:

```text
3, 4, 5, 9, 10, 11, 12, 14, 15, 16, 17, 18, 19, 21, 24, 25
```

It copies the exact bytes of every required validity bundle through the next
frontier into ephemeral staging and revalidates each bundle. It does not run a
validity provider and does not reinterpret the published disposition.

Before exposing the next subject, the planner walks the published builder-v6
base-run chain from the scheduler's exact `latestStateRun`. Every run must bind
the approved projection digest, builder-v6 digest, pinned judgment run and ID,
and next subject in the accepted prefix. A missing object, stale scheduler base,
cycle, alternate subject order, or non-prefix history stops execution.

The CLI entry point is:

```text
python -m math_flow bssc-research-v4-frontier \
  --source protocol/runtime/bssc-research-v4-validity-source-v1.json \
  --projection protocol/runtime/openrouter-research-v4-projection.json \
  --expected-projection-digest <governed-digest> \
  --projection-dir <published-projection-worktree> \
  --scheduler-file <published-projection-worktree>/coordination/scheduler.json \
  --materialization-dir <ephemeral-validity-directory> \
  --output <frontier-plan.json>
```

The runtime projection path above is an activation input. The planner requires
it to be active, BSSC-only, builder-v6, reconciliation-free, and to set
`maximumJudgmentsPerBuild` to one. It also requires its canonical digest to
equal the separately admitted governed projection when
`--expected-projection-digest` is supplied.

## Hosted serialization and recovery

`.github/workflows/project-research-v4-serial.yml.inactive` is the complete
hosted template. Renaming it to a `.yml` workflow is an activation step after
the active runtime candidate exists and an identical projection has been
admitted separately.

One workflow run:

1. resolves the governed projection and byte-binds it to the runtime candidate;
2. plans one exact accepted frontier and materializes its historical validity
   inputs;
3. records only the accepted prefix, claims with a hard limit of one, and checks
   that the lease names exactly the planned judgment;
4. invokes builder v6 at the subject's own Git commit with the exact predecessor;
5. completes or fails the lease, then publishes the normal content-addressed
   knowledge-build bundle and scheduler together; and
6. dispatches the next serial run only after successful publication.

The provider secret is scoped to the one formation step. Failure returns the
lease to the lane with the normal retry record before publishing scheduler
state. The workflow never invokes accounting, never authors alignment, and
never refreshes the viewer catalog. Downstream accounting discovers and binds
the published v6 state/alignment/handoff chain separately.

## Activation boundary

Activation still requires three deliberate repository changes:

- add the approved active runtime projection candidate and its resealed BSSC
  root contract;
- admit the identical projection through the existing one-file governance
  process; and
- rename the inactive workflow template to
  `.github/workflows/project-research-v4-serial.yml`.

No historical validity, knowledge, or canonical contribution object is
rewritten by those steps.
