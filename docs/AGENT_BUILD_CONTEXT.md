# Agent build context

This is the starting point for agents collaborating on the Math Flow product and
protocol. It describes the current architecture, operational deployment, safety
boundaries, and next build priorities. It is not a replacement for the detailed
protocol documents linked below.

Last reconciled with `main`: 2026-08-11 (`2e99f7a`).

## Product thesis

Math Flow is a GitHub-native system for collaborative mathematical research. Its
central rule is:

> Canonicalize what participants did, not what it means.

Participant contributions form a canonical Git ledger. Judges produce plural,
replayable interpretations of that ledger: immutable judgments, reconciliations,
holistic knowledge states, and eventually credit. A judge may revisit an earlier
conclusion when later evidence appears, but it does so by appending a revision;
published history is never rewritten.

The current deployment target is the private personal repository
`mooselumph/math-flow`. Do not push to `Layr-Labs/math-flow` until the owner
explicitly switches the project back after organization access is ready.

## System map

```text
solver contribution PR
        │
        ├── repository + atomic-diff validation
        ▼
automatic squash merge to main
        │
        ├── canonical transaction commit
        ├── baseline projection
        └── approved OpenRouter projections
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
                    └── viewer/catalog.json
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

### Judgment and reconciliation

- A primary judgment is immutable, content-addressed, and has no base knowledge
  state. Independent judgments must remain parallelizable.
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
| Repository-backed viewer | Implemented and deployed through ChatGPT Sites | `viewer/` |
| Non-UI agent context command | Implemented | `math_flow/context.py` |
| Solver-facing repository skill | Implemented | `.agents/skills/math-flow-solver/` |
| Typed dependencies and credit overlays | Not yet implemented; current active build | This document, `docs/PROJECTION_PROTOCOL.md` |
| Objective verifier attestations | Not yet implemented as durable protocol artifacts | `docs/MVP.md` |
| GitHub App / immutable contributor identity | Not yet implemented | `docs/MVP.md` |

The approved hosted projections are:

- `openrouter-research-v1`, the original holistic knowledge profile;
- `openrouter-no-three-in-line-research-programs-v2`, a knowledge-only profile
  for `no-three-in-line-77` that reuses the same immutable primary and
  reconciliation judgments while prioritizing independent research programs.

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
The deployed Sites viewer reads the personal repository through its explicit
`MATH_FLOW_CATALOG_URL` binding, so projection publication updates the UI
without a viewer redeploy.

The repository currently contains two problems:

- `triangle-midpoints`, the initial correction/revision test fixture;
- `no-three-in-line-77`, the more substantive active research problem.

## Hosted workflow lifecycle

The ordinary solver path is fully automatic:

1. `Validate repository`, `Validate transaction`, and
   `Admin admission approval` report on the PR's current head.
   Governed one-file PRs can be approved by an allowlisted administrator using
   either a native current-head review or an exact
   `/approve-admission <full-40-character-head-SHA>` comment. A new commit,
   comment edit, or deletion triggers revalidation against the current head.
2. `Auto-merge validated contribution` re-fetches the candidate as inert Git
   data and re-runs the trusted atomic validator against current `main`.
3. If the PR is still open, non-draft, targets `main`, and every required check
   succeeded, it is squash-merged at the exact validated head SHA.
4. The auto-merger explicitly dispatches the baseline and approved OpenRouter
   workflows for only the affected problem.
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

Automatic merging applies only to valid atomic solver contributions. Code,
workflow, protocol, problem-admission, projection-admission, and governance PRs
remain maintainer changes. New or modified problem/projection namespaces require
the administrator approval described in `docs/GOVERNANCE.md`.

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
provenance, select an open direction, and submit exactly one atomic contribution.
Do not infer current knowledge from the checked-in viewer fallback file.

### Build and protocol agents

1. Start from the current personal-repository `main`.
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
python3 -m math_flow resolve-projection \
  --projection openrouter-research-v1 \
  --problem no-three-in-line-77 \
  --head HEAD
python3 -m math_flow render-request --help
python3 -m math_flow context --help
```

For workflow edits, also parse the YAML and syntax-check extracted shell blocks.
Hosted provider tests spend money and mutate projection state; run them only when
the task requires an end-to-end check.

## Near-term build priorities

These are the most important gaps as of this document's reconciliation date:

1. **Add typed projection dependencies and a credit overlay.** This is the
   active build. Judgment reuse currently decouples a knowledge profile from its
   primary judge by pinned judge identity, but credit and future overlays need
   governed, typed dependencies on verified published artifacts. A credit run
   should execute after its declared judgment/knowledge dependencies, append
   content-addressed credit assessments, and never mutate mathematical knowledge.
2. **Add reservations as canonical research transactions.** A reservation must
   be participant-authored evidence rather than an adjudication field. The
   credit overlay can consider priority, specificity, overlap, completion
   quality, and abandonment without making a reservation itself mathematical
   truth or permanent exclusive ownership.
3. **Add durable objective attestations.** Lean, exact certificate checkers, and
   reproducible computation should become content-addressed evidence with pinned
   environments rather than only ephemeral CI checks.
4. **Exercise paid hosted reconciliation.** The hosted planner and no-conflict
   path are live, but a genuine opposed primary set has not yet generated a paid
   reconciliation artifact in the repository workflow.
5. **Improve GitHub identity and contributor UX.** A GitHub App can record stable
   user identity, add richer PR summaries and projection links, and scaffold
   valid contribution directories.
6. **Exercise governance on an organization plan.** The personal repository is
   the current test target. Required checks, CODEOWNER review, bypass controls,
   and projection-branch restrictions must be configured when organization
   access becomes available.

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
