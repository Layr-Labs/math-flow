# BSSC hosted work-accounting V1

`math_flow.bssc_work_accounting_hosted` is the production-shaped, BSSC-only
caller for the zero-origin builder-v6/work-accounting lane. The active runtime
config is committed and fails closed until both governed projections are
admitted byte-for-byte. Its scheduled workflow remains an inactive template at
`.github/workflows/project-bssc-work-accounting-v1.yml.inactive` until those
admissions are complete.

## Frozen execution contract

Each hosted run loads the pinned historical validity-v4 source, normalizes all
25 BSSC dispositions, and reconstructs the exact 16 accepted submission inputs.
The nine excluded submissions are terminal `indeterminate` dispositions and
never create knowledge or accounting transitions.

Planning creates a checksummed frozen artifact for at most one accepted
canonical frontier.  Its identity binds the current canonical and projection
heads, the BSSC problem-ledger digest, the exact governed overlay digest, the
knowledge/accounting predecessor states, the accepted normalized submission,
the validity judgment, all provider and runner identities, and the retry
history.  Completion order of validity runs cannot change the serial accepted
submission order.

Execution discovers exactly one published builder-v6 bundle whose governed
knowledge projection, builder spec, base state, and normalized submission match
the frozen subject.  `PublishedResearchV6TransitionProvider` replays that
already-published transition provider-free; only the work-estimation stages call
OpenRouter.  The pipeline enforces a one-subject maximum and records a governed
failure/retry transition when provider output is unavailable or invalid.

Before publication, a fresh main checkout and a fresh projections checkout
must reproduce every frozen dispatch binding.  Any canonical, projection,
subject, predecessor, schedule, disposition, or semantic-key drift makes the
result unpublishable.  Publication then uses the deletion-free CAS projection
publisher and requires its GitHub-signed commit report.

## Recovery and credentials

The workflow template uses one non-cancelling concurrency group for the lane.
It downloads prior frozen-plan artifacts as ZIP bytes, and the runner accepts
only an exact one-file archive named by its numeric GitHub run ID.  GitHub run
status is normalized only after the frozen plan and its digest validate.  Live
claims suppress duplicate work; stale claims, failed runs, and successful runs
that did not advance the projection are retried automatically with bounded
backoff.  There is no manual-review branch.

`OPENROUTER_API_KEY` appears only on the exact provider-execution step.
`GITHUB_TOKEN` appears only at GitHub history, signed publication, and catalog
refresh boundaries.  Checkout credentials are not persisted.  No submission,
model output, artifact path, or workflow input is interpolated into a shell
command.

## Activation seam

Activation requires the following governed sequence:

1. Admit each active projection candidate in its own required one-file PR by
   copying it byte-for-byte to `protocol/projections/<projection-id>.json`. The
   hosted loader fails closed if an admitted copy is missing or differs by one
   byte.
2. Run the serial knowledge producer through the accepted frontier.
3. Rename `project-bssc-work-accounting-v1.yml.inactive` to
   `project-bssc-work-accounting-v1.yml`, configure `OPENROUTER_API_KEY`, and
   leave the workflow concurrency and permissions unchanged.

The template runs every five minutes and processes at most one subject.  After
a signed publication it dispatches the existing viewer-catalog refresh.  The
catalog itself remains governed by the existing projection consumer and is not
modified by this hosted caller.
