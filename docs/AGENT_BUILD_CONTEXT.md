# Agent build context

This is the starting point for agents collaborating on the Math Flow product and
protocol. It describes the current architecture, operational deployment, safety
boundaries, and next build priorities. It is not a replacement for the detailed
protocol documents linked below.

Last reconciled with `main`: 2026-08-12 (`acd3ad6`).

## Product thesis

Math Flow is a GitHub-native system for collaborative mathematical research. Its
central rule is:

> Canonicalize what participants did, not what it means.

Participant contributions form a canonical Git ledger. Judges produce plural,
replayable interpretations of that ledger: immutable judgments, reconciliations,
holistic knowledge states, and eventually credit. A judge may revisit an earlier
conclusion when later evidence appears, but it does so by appending a revision;
published history is never rewritten.

The canonical deployment target is the private organization repository
`Layr-Labs/math-flow`. The former pilot repository, `mooselumph/math-flow`, is
retained as a fallback remote named `personal`; its scheduled projection wake-up
is disabled and it must not receive new canonical solver or protocol work.

The organization `main` branch requires the `Admin admission approval` check,
applies the repository's pull-request protections to administrators, and is
covered by the active all-branch signed-commit ruleset. The one-time migration
join is the verified signed commit `bbd2447`. The orphan `projections` branch
contains the union of the former organization and personal pilot artifacts, and
the repository-backed viewer reads its Layr-Labs catalog with a read-only token.

## System map

```text
solver participant-event PR
        │
        ├── repository + atomic-diff validation
        ▼
automatic squash merge to main
        │
        ├── contribution ── baseline + approved OpenRouter projections
        │             └── declared verification ── pinned objective attestation
        └── direction event ── provider-free direction ledger
                    │
                    ├── parallel primary judgments
                    ├── deterministic conflict detection
                    ├── reuse published reconciliations
                    ├── parallel missing reconciliations
                    ▼
              coalesced builder claim
                    │
                    ▼
      serialized formation per knowledge profile
                    │
                    ▼
    GitHub-signed commit on orphan projections branch
                    │
                    ├── content-addressed judgment/build objects
                    ├── scheduler and per-problem indexes
                    ├── viewer/catalog.json
                    └── exact knowledge dependency lock
                                      │
                                      ▼
                         qualitative credit overlay
                                 │
                                 ▼
                    repository-backed research atlas
```

`main` and `projections` have different meanings:

- `main` is the canonical, first-parent transaction ledger plus protocol code.
- `projections` is one orphan publication branch containing every logical
  projection's content-addressed artifacts. Git commit order on this branch has
  no mathematical meaning.
- Logical projections and serialized knowledge lanes are isolated by the digest
  of `protocol/projections/<projection-id>.json`, not by additional Git branches.
- Hosted execution is partitioned by a verified `(problem, primary-judge)`
  stream. Independent judges and problems run concurrently; projections sharing
  a judge form a short reuse queue so they do not duplicate paid judgments.

## Invariants that changes must preserve

### Canonical ledger

- One solver PR adds exactly one non-empty contribution directory under
  `problems/<problem-id>/contributions/<contribution-id>/`.
- A contribution may contain Markdown, code, proof-assistant files, datasets, or
  other artifacts. `README.md` is required.
- Acceptance, rejection, confidence, credit, and knowledge-state fields never go
  in a contribution directory.
- The squash commit on `main`, not a PR number or filename counter, is the
  transaction ID. First-parent history defines order.
- A second canonical participant stream stores exactly one immutable
  `register`, `update`, `release`, or `complete` event under
  `problems/<problem>/directions/<direction>/events/<event>/`.
- Direction status is derived from a linear predecessor chain. Registrations are
  non-exclusive evidence of intent and priority, not ownership or mathematical
  truth. They do not advance the contribution ledger or trigger judgments.

### Judgment and reconciliation

- A primary judgment is immutable, content-addressed, and has no base knowledge
  state. Independent judgments must remain parallelizable.
- The current OpenRouter judges have no shell, code interpreter, or tool calls.
  They receive supported repository artifacts as quoted text and return model
  output. Executable evidence must use a separately governed objective verifier;
  its pinned, networkless attestation may then be supplied to a judge as evidence.
- A reconciliation is a new judgment over an explicit conflict and its input
  judgments. It does not mutate either input and does not directly write state.
- Opposed judgments must not be silently settled by the knowledge builder. They
  require reconciliation, or they remain represented as an active dispute.
- Mathematical detail belongs in unconstrained Markdown. Structured JSON is a
  small control/routing surface, not the required form of a judge's reasoning.

### Knowledge formation

- Knowledge state is a holistic current account, not a list of event-shaped
  deltas. Deltas and immutable revisions live in the transaction/build history.
- Knowledge formation consumes completed judgments and reconciliation outcomes;
  it does not independently adjudicate the mathematics again.
- Primary judgments run concurrently. After their complete verified set is
  available, missing reconciliation judgments for independent conflicts also
  run concurrently. Construction of a given `(problem, projection)` knowledge
  chain is single-writer and serialized.
- Formation may be triggered by completed judgments but should coalesce work and
  obey a configurable minimum interval. The active example projection currently
  sets that interval to zero for MVP testing.
- Retroactive changes append `issue`, `revise`, `retract`, or `reinstate`
  revisions with base digest/revision guards. Old runs remain reproducible.

### Projection protocol and publication

- The core run envelope standardizes identity, provenance, and artifact
  integrity; it does not prescribe one mathematical output schema or call
  topology.
- Judge and builder implementations are allowlisted components. Repository JSON
  must never import or execute an arbitrary Python path.
- Every downloaded or resumed artifact is reverified against its manifest,
  content digest, judge identity, problem ledger, and expected subjects.
- Only verified bundles are copied into content-addressed projection objects.
- Projection commits are created through GitHub's API and must be GitHub-signed.
- Do not commit generated projection data to `main` or manually edit the
  `projections` branch.

## Current implementation

| Area | Current state | Primary source |
| --- | --- | --- |
| Repository validator and ledger | Implemented | `math_flow/repository.py` |
| Generic run/artifact envelope | Implemented | `math_flow/runs.py`, `math_flow/artifacts.py` |
| Approved projection registry | Implemented | `math_flow/governance.py`, `protocol/projections/` |
| Permissioned governed admission | Implemented; native reviews or exact `/approve-admission <full-head-SHA>` comments | `math_flow/governance.py`, `.github/workflows/admission-control.yml` |
| Parallel primary judgments | Implemented | `math_flow/judgments.py` |
| Conflict detection and reconciliation | Implemented locally and in the hosted projection workflow | `math_flow/judgments.py`, `.github/workflows/project-openrouter.yml` |
| Coalescing, leased formation lanes | Implemented | `math_flow/coordination.py` |
| Holistic hierarchical state and revisions | Implemented | `math_flow/formation.py`, `math_flow/knowledge.py` |
| Content-addressed projection publisher | Implemented, including optimistic cross-problem merge/retry and bounded GitHub commits | `math_flow/coordination.py`, `math_flow/projection_queue.py`, `math_flow/github_projection.py` |
| Provider-free congestion probe | Implemented; models concurrent problems, solvers, judge streams, projection lanes, atomic reconciliations, throttling, failure recovery, optimistic publication, chunking, catalog export, and agent context with zero provider calls | `math_flow/scale_probe.py`, `tests/test_scale_probe.py` |
| Repository-backed viewer | Implemented and deployed through ChatGPT Sites | `viewer/` |
| Non-UI agent context command | Implemented; deterministically reports verified credit assignments or explicit pending/stale/invalid/unavailable status without model calls | `math_flow/context.py`, `math_flow/credit_context.py` |
| Solver-facing repository skill | Implemented; requires repository tools and explains qualitative scoring semantics and exact-reference inspection | `.agents/skills/math-flow-solver/` |
| Typed projection dependencies | Implemented in PR #20: governed declarations plus exact verified knowledge-state locks | `math_flow/governance.py`, `math_flow/projection_dependencies.py` |
| Credit overlay runner, profile, cadence, and publication transport | Governed local/hosted runner, provider-free eligibility planner, bounded semantic retries, rolling coalescing, catch-up over closed UTC periods, predecessor-chain terminals, and independent `credit-assignment` bundles implemented | `math_flow/credit.py`, `math_flow/credit_schedule.py`, `.github/workflows/project-credit.yml` |
| Research direction registration | Implemented and merged in PR #28: append-only schema/reducer, atomic validation and auto-merge, provider-free CLI/context/catalog refresh, solver skill, viewer, and registration-aware credit v2 | `math_flow/directions.py`, `protocol/schemas/research-direction-event.schema.json`, `viewer/` |
| Objective verifier attestations | Additive v1 recipe, bounded pinned OCI runner, durable bundle, uniqueness/semantic validation, automatic hosted execution and signed publication, replay, context, and viewer presentation implemented | `math_flow/attestations.py`, `.github/workflows/project-attestation.yml`, `docs/OBJECTIVE_ATTESTATIONS.md` |
| GitHub App / immutable contributor identity | Not yet implemented | `docs/MVP.md` |

The approved hosted projections are:

- `openrouter-research-v1`, the original holistic knowledge profile;
- `openrouter-no-three-in-line-research-programs-v2`, a knowledge-only profile
  for `no-three-in-line-77` that reuses the same immutable primary and
  reconciliation judgments while prioritizing independent research programs;
- `openrouter-no-three-in-line-credit-v1`, a qualitative, non-zero-sum overlay
  for `no-three-in-line-77` that declares the research-program knowledge state
  as its exact dependency;
- `openrouter-no-three-in-line-credit-directions-v2`, the registration-aware
  qualitative overlay admitted in PR #29, with the same exact knowledge
  dependency and a one-hour rolling minimum interval. It is active; repository
  evidence, its locked knowledge dependency, and the direction-event ledger are
  approved inputs to its OpenRouter runner.

The `openrouter-credit-assignment-v2` runner/profile embeds the verified
direction-event ledger and lets assignments cite exact prior canonical
`register` transactions. Credit v1 remains active and immutable for comparison;
agents and viewers must select the intended overlay explicitly. Credit v2 has a
current authoritative run (`sha256:b0e1c432...`) covering all five accepted
`no-three-in-line-77` contributions. Its assignment for the finite-rotation
classification proof cites the exact prior registration transaction
`a9552d14...`.

Their judges and builders are pinned to `openai/gpt-5.6-sol` with high reasoning
through OpenRouter. The current registry allows at most 16 parallel judgment or
reconciliation jobs and 500 dependency-connected judgments in one formation
batch.

The first research-program build published successfully in hosted run
`31519191523`. It reused all three existing primary judgments, found no current
conflicts, skipped both paid judgment stages, and produced a 16-node state with
two top-level programs: known-record certification/local perturbation, and
rotational symmetry/rct4 modeling. Its state run digest is
`sha256:8e1bfea136ad3b78c2720269e984b5f807179533ea8a1b112952fc41a34b31df`.
After the objective-verification contribution merged, hosted run `31569748809`
reused the shared judgment stream and published the third research-program
state. The current knowledge run is `sha256:7562b60b...`, its holistic state is
`sha256:71b92511...`, and it covers canonical problem-ledger head `0ffe9a12`
with no missing primary judgment or state representation.
The public Sites viewer at
`https://math-flow-research-atlas.appromoximate.chatgpt.site` reads the
Layr-Labs repository through its explicit
`MATH_FLOW_CATALOG_URL` binding and a read-only organization token, so
projection publication updates the UI
without a viewer redeploy. Its top controls now group the knowledge projection
and state selectors in one vertical control bubble and the credit projection
and state selectors in a parallel bubble, with the problem selector to their
left. Selector state remains URL-backed and repository-catalog-driven. A viewer
following the current knowledge or credit head advances when a new terminal is
published; an explicitly selected historical state remains pinned and exposes a
control to return to the latest state.
Its build chain is pinned to a zero-advisory npm resolution; the last compatible
vinext release without the vulnerable transitive image parser is retained until
that parser has an upstream patched release. Objective-verification requests
and their authenticated published outcomes appear as a separate transaction
tab, never as judgments or credit.

## P0 operational evidence

The scale-readiness P0s are implemented and exercised on the organization
repository:

- **Provider-free congestion:** PR #12 added the deterministic scale probe. Its
  reference case covers 12 problems, four projections, 12 solvers per problem,
  48 independent lanes, 576 primary jobs, 48 reconciliation jobs, contested
  leases, bounded retry/reset, optimistic publication, 2,256 immutable files,
  catalog export, and agent context with zero provider calls.
- **Hosted reconciliation:** run `31563447090` produced one paid reconciliation
  over a controlled, repository-derived conflict. It returned
  `prefer-refutation`, judgment `sha256:b3f7acd0...`, and run
  `sha256:b4e015ac...`; the retained smoke evidence was deliberately not
  published as canonical mathematical state. The fixture is pinned to its
  reviewed historical ledger prefix, so later contributions do not invalidate
  the smoke path.
- **Objective verification:** canonical contribution `0ffe9a12` declares the
  exact 152-point checker. Run `31569747227` executed it inside the governed,
  digest-pinned, networkless, non-root OCI environment and reported
  `verified 152 points on a 76 x 76 grid; no collinear triple`. It published
  attestation `sha256:079692f8...` in run object `sha256:293d1eed...`; both the
  immutable-object commit `d0965e7` and catalog commit `c5a17f0` are verified
  GitHub signatures. Machine context reports one passed and zero pending
  objective attestations.
- **Queue handoff:** the objective run exposed a missing repository binding in
  the checkout-free successor dispatcher. PR #19 fixed it. Run `31570610937`
  then completed the current projection and successfully dispatched run
  `31570656849`, which reused the existing primary judgment and brought the
  second knowledge projection current. The cadence wake-up subsequently
  dispatched both credit overlays; registration-aware run `31570861867`
  published the current five-contribution terminal.
- **Viewer and dependency chain:** public Sites version 15 is deployed at the
  canonical research-atlas URL with objective-verification presentation and
  follow-head semantics. The exact merged viewer build, nine rendered tests,
  lint, and npm audit pass; the default
  branch has zero open Dependabot alerts and recent production worker logs have
  no errors.

At this checkpoint, `math_flow context` reports current research-program
knowledge, current registration-aware credit, zero knowledge coverage gaps, no
active build, and one passed/zero pending objective attestations for
`no-three-in-line-77`.

The credit overlay was admitted in PR #22 at `640f41a`; its first qualitative
assignment was published at projection commit `e0c6fc8` (run-digest prefix
`sha256:11da3274`). Non-UI agents resolve the verified predecessor-chain
terminal through `math_flow context`; that command never invokes the credit
model. The governed cadence layer wakes every five minutes, plans without a
provider, and dispatches only eligible overlays. The existing projection keeps
its rolling/all-ledger behavior until a separate governed spec change opts into
UTC calendar allocation windows.

Automatic credit retries are keyed to the exact rolling dependency state or UTC
allocation window. Active duplicates are suppressed and five consecutive
failures stop automatic spend until state changes or a matching run succeeds;
manual dispatch remains an explicit escape hatch. Credit planning errors are
reported per overlay after knowledge queues have already been dispatched, so a
broken overlay cannot starve unrelated formation work.

Credit applicability compares the governed consumer projection, problem ledger,
producer runs, and locked artifacts. The immutable dependency-lock digest still
covers the canonical head for audit provenance, but unrelated repository commits
do not alone make an otherwise identical credit assignment stale.

The repository currently contains two problems:

- `triangle-midpoints`, the initial correction/revision test fixture;
- `no-three-in-line-77`, the more substantive active research problem.

## Scale pilot: admit and seed new problems

Adding a problem is a governed maintainer operation, not an atomic solver
transaction. An agent assigned to add problems should follow the build/protocol
agent rules in this document, use an isolated worktree from current
`origin/main`, and read `docs/GOVERNANCE.md`. It should not present a new problem
as a contribution or combine it with solver work.

For each new problem:

1. Choose a stable lowercase-hyphenated problem ID and write one self-contained
   `problems/<problem-id>/problem.md`. State the exact objective and definitions,
   known lower and upper bounds or baseline results, admissible artifact types,
   and authoritative references. Clearly distinguish established background
   from the open target. Prefer problems with several separable research
   programs and small independently checkable intermediate claims.
2. Open one PR containing exactly that one new file. Do not batch several
   problems, a projection spec, a verifier, or a seed contribution into the same
   PR. Run `python3 -m math_flow validate-tree`, the complete unit suite, and
   `git diff --check`; the hosted admission check validates the exact one-file
   shape against trusted base-branch code.
3. Report the PR's full 40-character head SHA to an allowlisted administrator.
   The administrator may approve the current head with the exact comment
   `/approve-admission <full-head-SHA>`. Governed admissions are intentionally
   not handled by the participant auto-merger, so a maintainer must merge the
   green problem PR. Any new commit requires a fresh head-bound approval.
4. Treat the merged problem as an empty namespace. It does not trigger a paid
   judgment, knowledge formation, or credit run, and it will not have a
   selectable knowledge state in the atlas until a contribution is merged and a
   projection is published.
5. The active `openrouter-research-v1` projection has
   `allowedProblems: ["*"]`, so no projection admission is required for the
   baseline scale pilot. The first valid contribution to the new problem will
   auto-merge and dispatch the baseline plus that OpenRouter judgment/knowledge
   pipeline. A specialized research-program builder or credit policy is a
   separate one-file governed projection PR and should be added only when the
   experiment calls for it.
6. After admission, hand the exact problem ID to solver agents and require them
   to follow `.agents/skills/math-flow-solver/SKILL.md`. Each solver must create
   its own worktree and submit exactly one contribution or direction event per
   PR. The first contribution can optionally declare an already admitted
   objective verifier; adding a new verifier implementation is a separate
   maintainer change.

Start the paid pilot in a bounded wave rather than admitting and seeding every
candidate simultaneously. A useful first observation point is a few new
problems with a few independent contributions each: verify automatic merges,
per-problem judgment fan-out, cross-problem publication, retry behavior,
`math_flow context` coverage, and public-atlas discovery before increasing the
wave size. Problem admission itself is provider-free; merged contributions are
the events that begin paid judging.

## Hosted workflow lifecycle

The ordinary solver path is fully automatic:

1. `Validate repository`, `Validate transaction`, and
   `Admin admission approval` report on the PR's current head.
   Governed one-file PRs can be approved by an allowlisted administrator using
   either a native current-head review or an exact
   `/approve-admission <full-40-character-head-SHA>` comment. A new commit,
   comment edit, or deletion triggers revalidation against the current head.
2. `Auto-merge validated participant transaction` re-fetches the candidate as
   inert Git data and re-runs the trusted atomic validator against current
   `main`.
3. If the PR is still open, non-draft, targets `main`, and every required check
   succeeded, it is squash-merged at the exact validated head SHA.
4. For a contribution, the auto-merger explicitly dispatches the baseline and
   approved OpenRouter workflows for only the affected problem. If the merged
   transaction contains `verification.json`, it also dispatches the trusted,
   provider-free objective-attestation workflow for that exact squash SHA. A direction
   event dispatches only the provider-free viewer-catalog refresh because it has
   no mathematical judgment effect.
5. OpenRouter coverage planning fans out one primary judgment for each
   transaction not covered by the active judge-spec digest.
6. The workflow reconstructs the complete verified primary set, derives the
   exact current conflicts, reuses matching published reconciliations, and fans
   out one OpenRouter call for each missing conflict reconciliation.
7. Completed primary and reconciliation judgments are claimed dependency-
   atomically into one serialized knowledge build, then published with the
   updated scheduler, indexes, and viewer catalog. Later knowledge projections
   using the same judge identities reuse those published judgments.
8. Cross-problem publications three-way merge disjoint scheduler lanes against
   the latest orphan-branch head and retry expected-head races. A scheduled
   wake-up pass redispatches due coalesced lanes every five minutes. Formation
   failures publish their claim rollback and an exponential retry marker;
   automatic retry stops after five failures on one problem ledger. Same-head
   workflow history applies the same cap to failures before formation begins,
   while leaving unrelated projections eligible.

The explicit dispatch in step 4 is intentional. A merge made with the workflow's
`GITHUB_TOKEN` does not normally cause a second workflow through a `push` event.

Automatic merging applies only to valid atomic solver contributions and
research-direction events. Code, workflow, protocol, problem-admission,
projection-admission, and governance PRs remain maintainer changes. New or
modified problem/projection namespaces require the administrator approval
described in `docs/GOVERNANCE.md`.

### Recovery

If judgment succeeds but formation or publication fails, do not rerun paid
judgments. After fixing the downstream defect, dispatch
`project-openrouter.yml` with the same projection and problem and set
`resume_run_id` to the failed run. The workflow downloads and re-verifies the
retained judgment artifacts and skips the judgment matrix.

Formation caches successful provider stages by exact request digest. Empty
assistant messages are retried up to three times and are never checkpointed;
length-truncated responses are also non-cacheable.

Hosted reconciliation is implemented and fail-closed. Deterministic and
fake-provider tests cover opposed primaries, conflict derivation, reconciliation
reuse, dependency-atomic formation, and rejection of missing conflict inputs.
The hosted research-program run exercised the no-conflict branch successfully;
a real repository event containing opposed current primary judgments is still
needed to exercise a paid reconciliation call end to end.

## Agent roles and working conventions

### Mathematical solver agents

Read and follow `.agents/skills/math-flow-solver/SKILL.md`. Use
`python3 -m math_flow context` to materialize a verified latest state, inspect
provenance and qualitative credit, select an open direction, and submit exactly
one atomic participant event per PR. Inspect `directions.json`, `credit.json`,
and the optional raw
`credit-report.md` rather than the UI; credit is non-zero-sum attribution and
does not alter mathematical validity. A direction registration may precede
substantial work, but it is optional and non-exclusive; complete it in a later
atomic event referencing the canonical contribution transaction. Do not infer
current knowledge or scoring from the checked-in viewer fallback file.

### Build and protocol agents

1. Start from the current `Layr-Labs/math-flow` `main`. In the maintained local
   checkout this is `origin/main`; `personal/main` is historical fallback state.
2. Read this document, then only the detailed references relevant to the task.
3. Inspect `git status` before editing. Existing changes belong to another agent
   or the owner unless explicitly assigned.
4. Use a dedicated branch and keep changes narrow. Do not combine product code,
   protocol governance, and a mathematical contribution in one PR.
5. Preserve replayability and validate old artifacts when changing schemas or
   reducers. Prefer additive versions to in-place semantic changes.
6. Never print, commit, or pass repository/OpenRouter tokens in command arguments.
7. Report commands run, test results, remaining risks, and any external settings
   required for the change to be effective.

When several agents share one worktree, partition work by files or components,
communicate before touching overlapping files, and give one agent ownership of
integration and final verification. Never reset or discard another agent's
changes to obtain a clean tree.

## Validation commands

Run the smallest relevant checks while iterating, then the complete local suite
before handing off a protocol or workflow change:

```bash
python3 -m math_flow validate-tree
python3 -m math_flow validate-projections
python3 -m unittest discover -s tests -v

cd viewer
npm ci
npm test
npm run lint
```

Useful read-only diagnostics include:

```bash
python3 -m math_flow ledger --problem no-three-in-line-77 --head HEAD
python3 -m math_flow directions --problem no-three-in-line-77 --head HEAD
python3 -m math_flow resolve-projection \
  --projection openrouter-research-v1 \
  --problem no-three-in-line-77 \
  --head HEAD
python3 -m math_flow render-request --help
python3 -m math_flow context --help
python3 -m math_flow context \
  --problem no-three-in-line-77 \
  --projection openrouter-no-three-in-line-research-programs-v2 \
  --credit-projection openrouter-no-three-in-line-credit-directions-v2 \
  --head origin/main \
  --projection-dir <detached-projections-worktree> \
  --output-dir <new-empty-context-directory>
```

For workflow edits, also parse the YAML and syntax-check extracted shell blocks.
Hosted provider tests spend money and mutate projection state; run them only when
the task requires an end-to-end check.

## Post-P0 build priorities

The scale-readiness P0s above are complete. These are the most important next
experiments and product gaps as of this document's reconciliation date:

1. **Run the hosted scale pilot.** The provider-free congestion probe now covers
   scheduler, retry, merge, chunking, viewer, and context invariants locally.
   Admit several real problems with simultaneous solver contributions to
   measure GitHub runner/API congestion and confirm the same behavior on the
   organization repository without changing the protocol under load.
2. **Exercise natural reconciliation.** The controlled paid smoke run succeeded
   without publication. The remaining operational proof is a real opposed
   primary set flowing through automatic reconciliation, formation, publication,
   viewer discovery, and agent context without special fixture inputs.
3. **Add a numerical/time-bucketed award profile if desired.** Hosted cadence,
   exact UTC transaction windows, and predecessor-chain terminals are now
   implemented, while the admitted example remains qualitative and non-zero-sum.
   A future runner can allocate a finite hourly/daily award without changing
   the scheduling envelope. Strict boundary-time knowledge would additionally
   require historical dependency resolution.
4. **Improve GitHub identity and contributor UX.** A GitHub App can record stable
   user identity, add richer PR summaries and projection links, and scaffold
   valid contribution directories.
5. **Harden organization operations.** Exercise admission approval, signer and
   projection-publication recovery with multiple maintainers; document secret
   rotation and disaster recovery; and remove temporary migration branches once
   the organization deployment has remained stable.

### Research direction registration MVP

Research direction registration is a participant-authored canonical
event stream, separate from submissions, judgments, knowledge formation, and
credit assignment. The protocol calls these direction events; the UI calls the
resulting objects **Research directions**. Existing
published credit-v1 artifacts that use `reservationTransactionIds` remain
immutable and readable, while credit v2 uses
`directionRegistrationTransactionIds`.

The MVP supports these immutable events:

- `register`: describe a specific intended direction, motivation, proposed
  evidence or method, and optional related knowledge-node IDs;
- `update`: supersede a prior registration with a more precise scope or plan;
- `release`: state that the participant is no longer actively pursuing it; and
- `complete`: connect the registration to a submitted contribution without
  claiming that the contribution is correct or sufficient.

Each event identifies its direction and predecessor where applicable;
author identity and priority time come from the canonical squash transaction.
Current status is derived deterministically from the append-only event history,
not stored as mutable repository state. Overlapping registrations are valid and
must be shown explicitly. An optional review horizon may inform the credit
policy, but expiry must not erase history.

The first credit policy that consumes these events considers priority,
specificity, meaningful progress, overlap, release or abandonment, and the
quality of the eventual contribution. It must treat registration only as
evidence: early vague registrations should be discountable, low-quality work
should not be rewarded merely for being first, and no solver should be prevented
from pursuing a registered direction.

Implemented surfaces are:

1. A versioned event schema, repository validator, and atomic-PR validation
   for registering, updating, releasing, or completing one direction event.
2. Provider-free CLI/context output that lists active, overlapping, released,
   and completed directions; the solver skill inspects the
   list and optionally register before beginning substantial work.
3. A repository-backed viewer surface for research directions without
   folding them into holistic mathematical knowledge.
4. A new credit-v2 profile that receives verified direction events as typed
   inputs and cites their canonical transaction IDs. Keep the existing credit-v1
   profile compatible rather than changing the meaning of published bundles.

Automatic merge accepts a valid one-event direction PR using the same trusted
revalidation pattern as solver contributions. It refreshes the repository-backed
catalog without dispatching a mathematical or paid projection. Direction
registration introduces no locks, exclusive claims, or requirement to register
before submitting mathematics.

The first complete hosted lifecycle is now canonical: registration `a9552d14`,
proof contribution `29ccbd39`, and completion event `bbf27430`. The current
registration-aware credit-v2 run links the proof's assignment back to that exact
prior registration, while the mathematical knowledge projection remains
independent of the credit result.

GitHub currently emits a non-blocking Node 20 deprecation annotation for the
account-required `actions/checkout@v5` and `actions/setup-python@v5`; GitHub is
successfully forcing those actions onto Node 24. Keep the v5 pins until the
Layr-Labs account constraint changes or the pinned actions provide a compatible
upgrade path.

## Detailed references

- `README.md` — repository overview and common commands.
- `docs/MVP.md` — architecture, phased roadmap, and deferred decisions.
- `docs/PROJECTION_PROTOCOL.md` — run envelopes, profiles, revisions, and
  builder flexibility.
- `docs/PARALLEL_JUDGMENTS.md` — judgment/reconciliation/formation command flow.
- `docs/GOVERNANCE.md` — problem and projection admission policy.
- `docs/REMOTE_TESTING.md` — hosted workflow testing and recovery.
- `viewer/README.md` — repository-backed atlas behavior and local testing.
- `.agents/skills/math-flow-solver/SKILL.md` — mathematical solver workflow.

If this document conflicts with executable validators, registered specs, or
workflow code, those are authoritative. Update this document in the same PR that
changes an architectural invariant or operational lifecycle.
