# Agent build context

This is the starting point for agents collaborating on the Math Flow product and
protocol. It describes the current architecture, operational deployment, safety
boundaries, and next build priorities. It is not a replacement for the detailed
protocol documents linked below.

Last reconciled with `main`: 2026-09-01 (`4190d6a`).
Published-state claims below were checked against `origin/projections` at
`ebe7a32`.

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
        ├── contribution ── active OpenRouter research projection
        │             └── declared verification ── pinned objective attestation
        └── direction event ── provider-free direction ledger
                    │
                    ├── parallel, exact-subject validity-v4 judgments
                    │       └── bounded declared references and attestations
                    ▼
       dependency-ready accepted judgment bundles
                    │
                    ▼
      serialized, coalesced builder-v5 formation
                    │
                    ├── results separated from proofs/methods/tools
                    └── strict-tree local-objective programs
                    ▼
    GitHub-signed commit on orphan projections branch
                    │
                    ├── content-addressed judgment/build objects
                    ├── scheduler and per-problem indexes
                    ├── viewer/catalog.json
                    └── exact state dependency lock
                                      │
                                      ▼
                 independent common-horizon two-term
                     hierarchical credit overlay
                                 │
                                 ▼
                    repository-backed research atlas
```

This diagram is the active `openrouter-research-v3` path. Reconciliation code
and historical reconciled objects remain replayable, but no active research
projection currently has a reconciliation judge.

### Active stage boundaries

| Stage | Governed responsibility | Context it receives | Output and ordering |
| --- | --- | --- | --- |
| Primary validity v4 | Decide whether each declared mathematical claim is rigorously established and identify its exact required premises | Problem statement, current canonical submission, the claims' declared-reference union with each claim restricted to its own declarations, selected pre-subject knowledge grounded in those references, and exact terminal objective attestations for the subject/reference union | One immutable assessment per declared claim. Exact subjects run in parallel; completion order has no knowledge or credit meaning. |
| Hierarchical builder v5 | Import valid declared claims, separate results from materially supporting proofs/methods/computations/tools, and organize accepted work into strict-tree local-objective programs | Current serialized program state, a dependency-ready batch of immutable validity outcomes, original submissions for accepted transactions, and bounded provenance/reference history | One atomic post-state and placement audit for the batch. Formation is coalesced and single-writer per problem/projection. Invalid and indeterminate material is excluded. |
| Hierarchical credit v3 | Estimate local causal work reduction at every immediate program edge using the two-term policy | Exact locked builder-v5 terminal, complete accepted state-transition history, accepted canonical submission text, validity records, dependencies/provenance, and historical local thread ledgers | Direct-work, obviated-work, confidence, evidence, and residual assessments; deterministic validation/share propagation. Runs only after an eligible exact knowledge terminal exists. |

The primary judge therefore does not construct or receive an unrestricted
global post-subject knowledge state. The builder does receive and update global
program state. Credit sees the broader accepted hindsight history because its
counterfactual question is explicitly ex post.

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
- Every direction `release` must have the same exact canonical Git author name
  and email as its originating `register` event. Only that participant can
  release the direction under the repository identity model.
- `protocol/problem-registry.json` may reversibly archive an admitted problem.
  Archival preserves its complete canonical ledger and published history while
  excluding it from ordinary solver discovery, new participant events, active
  projection resolution, recovery scheduling, and the live viewer catalog.
  Unarchiving removes the ID through a separately governed one-file registry PR.

### Judgment and reconciliation

- A primary judgment is immutable, content-addressed, and has no mutable base
  knowledge state. Independent judgments must remain parallelizable. A bounded
  validity judge may receive a content-addressed pre-subject dependency packet:
  declared claims, explicitly cited prior transactions, an exact terminal
  objective attestation when requested, and only historical knowledge nodes
  grounded in those references. It must never receive the current post-subject
  state or an automatically embedded preceding ledger.
- In historical validity v3, cited transactions are declared provenance, not automatic
  logical dependencies. The judge selects the exact subset required as premises
  for each valid claim. Formation uses only that subset; invalid and
  indeterminate submissions remain wholly excluded. The broader declared
  reference set stays in immutable history for later credit assignment.
- Objective verification is a subject-local gate in historical validity v3. Only the
  requesting subject waits for a verified terminal attestation; unrelated
  subjects remain eligible for parallel primary judgment. Terminal publication
  redispatches applicable v3 streams, and packet/judgment identity binds the exact
  attestation evidence.
- Validity v4 extends that gate to exactly the transactions declared by the
  subject's claims. A pending request on a declared reference defers only
  subjects that cite it; references with no request and unrelated subjects do
  not wait. Terminal passed, failed, and error evidence is bound by transaction
  ID. The packet never expands to unrelated attested ledger entries, and
  publication redispatches applicable v3 and v4 streams; the current active
  research stream uses v4.
- Primary-judgment completion order must not determine knowledge-state order or
  credit context. A later transaction may finish judgment before an earlier
  independent transaction without being discarded or forcing either judgment to
  rerun. Only an explicit mathematical dependency may create a validity-ordering
  constraint; single-writer knowledge formation is a downstream concern.
- Hosted automatic dispatches identify one exact subject transaction. Runs are
  concurrency-keyed by projection, problem, and subject with cancellation
  disabled: duplicate triggers for one subject queue and replan after waiting,
  while different subjects remain parallel. Manual batch planning remains an
  explicit recovery mode. Published indexes and publication preflight reject
  distinct primary judgment IDs for one judge-spec digest and subject.
- A validity-only primary judge devotes its mathematical work to rigorous,
  conservative correctness verification, with prevention of false acceptance
  as its overriding priority. It may decompose a proof into any number of
  intermediate obligations and must audit every material inference, assumption,
  quantifier, domain restriction, edge case, calculation, and dependency use.
  One structured assessment per declared claim is an identity/indexing rule,
  not a restriction on the analysis. Missing premises, evidence issues, and
  scope qualifications remain properties of that assessment rather than new
  top-level claim identities. Novelty, frontier placement, research-program
  organization, and cumulative state belong to the knowledge builder.
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
- Knowledge formation consumes completed judgments and, for historical specs
  that declare it, reconciliation outcomes; it does not independently
  adjudicate the mathematics again.
- In the active validity-v4 lane the builder receives the original submission
  together with its immutable judgment. It may inspect submission text only to
  separate a valid declared result from the proof, method, computation, or tool
  that establishes it. It must not promote an unjudged assertion from elsewhere
  in the submission.
- Invalid and indeterminate claims, their arguments, and their uncertainty are
  excluded completely. The builder does not preserve a rejected submission as
  tentative knowledge and does not repair or relitigate the primary verdict.
- The builder receives the current serialized program state because it owns the
  cumulative organization of accepted work. The primary judge does not receive
  that unrestricted current state: it receives only pre-subject nodes grounded
  in the subject's declared references, plus the referenced canonical artifacts
  and bounded attestation evidence.
- Primary judgments run concurrently. The active validity-v4 lane feeds
  dependency-ready outcomes directly to formation and has no reconciliation
  stage. Historical lanes that declare reconciliation may fan out their missing
  conflict judgments after the verified primary set is available. Construction
  of a given `(problem, projection)` knowledge chain is single-writer and
  serialized.
- Single-writer formation does not imply one provider call or one authored
  post-state per submission. A formation claim may freeze and consume a
  deterministic batch of dependency-ready judgments, producing one atomic
  post-state plus per-submission provenance and historical credit-reference
  ledgers. The experimental hierarchical replay is currently a serial reference
  implementation; do not treat its per-transaction loop as an architectural
  requirement for hosted execution.
- Formation may be triggered by completed judgments but should coalesce work and
  obey a configurable minimum interval. The active `openrouter-research-v3`
  producer uses a five-minute minimum interval; a newly created lane can run
  immediately, while later inputs arriving inside the interval are coalesced.
- Retroactive changes append `issue`, `revise`, `retract`, or `reinstate`
  revisions with base digest/revision guards. Old runs remain reproducible.

### Research-program taxonomy evolution

Knowledge revision history, mathematical node identities, and provenance are
additive, but the materialized program taxonomy is not immutable. Preserve a
node ID while the same mathematical concept or research agenda continues; do
not preserve a program boundary solely because it appeared in an earlier run.

The versioned neutral v3 builder may introduce a durable subprogram, promote or reparent a
program, split one broad program into sibling successors, merge overlapping
programs, move stable nodes without rewriting their mathematical content, and
retire predecessor programs. These are organizational operations over supplied
judgments, not permission to make new mathematical conclusions. A program must
remain meaningful without contributor names, transaction names, or chronology.

When the selector identifies an active program for taxonomy review, the adapter
expands selection to that program's active subtree and ancestors. For a split,
the report and extracted delta must form one atomic change set:

1. create the active successor programs with reciprocal `split-from` lineage;
2. move every active descendant subtree to a successor or genuinely shared
   active scope without duplicating it;
3. retire the predecessor with reciprocal `split-into` lineage; and
4. validate the final tree before writing any artifact.

Merges use `merged-from` and `merged-into` in the same way. A topology-only
`move` reuses the exact prior node content, subjects, evidence, and report
reference while appending a new change rationale. New runs reject an active node
beneath a retired ancestor, missing or one-sided lineage, cycles, stale base
guards, and partial splits. Historical schema-v3 states remain readable without
lineage fields, so existing projection histories and exact revision hashes do not
change.

The neutral knowledge-builder v3 taxonomy supports move, reparent, split, and
merge operations in its revision-based state representation. The separate
hierarchical research builders v2-v4 did not port that behavior: they can create
programs, but preserve every existing program parent, thread owner/kind, and
item program/type. The former v4 builder lane therefore did not guarantee a useful
initial hierarchy and could validly remain flat at root.

The additive hierarchical builder v5 corrects initial formation without
overstating topology evolution. It requires immutable placement audits, rejects
an all-root state once at least two accepted contributions exist, and explicitly
supports creation of sibling and nested local-objective programs. Existing
topology remains fixed in v5. Future versions should restore audited move,
reparent, split, and merge operations using append-only topology revisions,
successor/retirement lineage, and deterministic credit invalidation or refresh
for every affected local program edge. Preserve this evolution path when
simplifying or replacing the experimental builder.

The Builder V6 foundation and one-submission state-v2 bundle runner implement
that next reducer boundary for the active BSSC-only `openrouter-research-v4`
lane. It materializes one exact adjacent post-state per accepted canonical
submission, composes accepted content with stable moves, retirement, split, and
merge operations, derives rather than accepts topology alignment, and emits an
exact same-world accounting handoff. Its dedicated serial workflow keeps this
history separate from the later state-v3 Builder V7–V9 lanes.

The BSSC-only Builder V9 lane preserves the two-entity state-v3 model but
replaces Builder V8's complete provider-visible predecessor with a digest-bound
progressive context: every program and result core remains visible, while full
support is loaded only for results selected by the current submission's declared
dependencies and recursive result-dependency closure. Provider-authored
`supportAdditions` are merged into the complete trusted predecessor so omitted
support cannot be deleted. The context is stored and re-derived during replay.
Its `openrouter-research-v7` projection and dedicated serial workflow are active
for BSSC. The local/fractal Builder V10 described later remains a separate,
inactive experiment and does not alter this active V9 lane. See
`docs/BSSC_RESEARCH_V7_CONTEXT_EXPERIMENT.md`.

Cross-program claims belong at root or another genuinely shared active scope.
Do not duplicate a mathematical node merely because multiple programs depend on
it. A dispute follows the claim it disputes. Taxonomy changes must never be based
only on contributor identity, transaction boundaries, chronology, or display
preference.

### Hierarchical credit assignment

- Programs are credit contexts, not exclusive intellectual-ownership
  containers. The strict tree supplies one immediate-parent comparison at each
  level. Cross-program mathematical use is represented by dependencies and
  evidence rather than by duplicating a node or giving it several parents.
- `openrouter-research-credit-v3` is an independent consumer of the exact locked
  `openrouter-research-v3` terminal. Its common-horizon evaluator receives the
  current program state, complete accepted transition history, accepted
  canonical submission text, validity records, provenance/dependency links,
  and local program threads. Rejected submission bodies are not credit inputs.
- Credit is ex post and counterfactual. Given everything known at the common
  horizon, remove one immediate child and information uniquely inherited from
  it, hold the realized underlying problem fixed, retain independently available
  information, and let a competent solver adapt optimally.
- The local score has exactly two non-negative components: direct work avoided
  on the child's own local line and work obviated on other threads that existed
  in the child's historical local reference ledger. It is not the observed
  change between pre- and post-submission estimates of remaining work; useful
  bad news can reveal a harder problem while still reducing counterfactual work.
- Evaluate only immediate-parent effects. A child program receives credit at its
  parent edge; that program's immediate children divide value inside the local
  program context. Do not repeat descendant value at ancestors. Preserve
  uncertain local value as a non-negative unattributed residual rather than
  forcing exhaustive or falsely precise allocation.
- The model returns governed local causal-work assessments. Deterministic code
  validates the assessments, computes local shares, and propagates them through
  the hierarchy. Credit never changes validity or knowledge state.

### Unpublished joint portfolio/work candidates

The branch-only `bssc-joint-portfolio-credit-k2-v1` experiment is the first
hosted candidate to join one accepted accounting-aware topology/W+ judgment to
a direct same-world W- estimate and a submission-level allocation. It freezes
the exact successful K2 joint response from run `33564954137`; trusted replay
must reproduce the post-knowledge digest, W+ state digest, and 4,351.7375-hour
W+ total before another provider call is possible. It never asks a second judge
to regenerate topology or W+.

Hosted run `33588922200` completed the remaining candidate without publication
or continuation. Its W- estimate was 4,595.7375 hours, so trusted reduction
assigned `D = 244` competent-human-researcher hours directly to canonical K2
submission `f236017c...`. The additive explanation was 144 hours on the new
root-child UV product/branchwise-additivity package and 100 hours of root-level
integration/pruning work. Those node effects are explanatory differences, not
separate credit recipients. W- passed on its first attempt; the run used four
provider calls, 137,556 reported tokens, and $0.1852836.

The safe-fact stage used all three attempts because a deterministic 32-byte
overlap rule rejected ordinary mathematical phrases copied from the submission.
That literal-copy rule has now been removed from safe-fact validation and final
W- request assembly. Evidence manifests, chunks, attached files, submission
payload fields, W+ patch rationales/evidence, and unexpected schema fields
remain structurally excluded from W-. Safe-fact prose may overlap submission
wording. A future teacher-student exposure ablation must measure whether
outcome-only, paraphrased, near-verbatim, or proof-bearing summaries materially
bias W-; lexical overlap alone is not a quality criterion.

This experiment remains unpublished, K2-only, and absent from the Research
Atlas. Its 244-hour result is one uncalibrated model judgment, not sampling-
variance or numerical-accuracy evidence. It proves the candidate call order,
bindings, frozen-W+ authority, trusted reduction, and submission allocation;
it does not yet establish a sequential multi-submission credit lane.

The provider-neutral `bssc-joint-portfolio-serial-k1-k3-v1` holdout now extends
that reducer graph through three exact accepted BSSC submissions. K1 creates one
code-induced-converse work package, K2 creates one independent relaxed-UV work
package, and K3 must reuse the K2 program and both results while appending
support and refreshing live W+. Every validated author response is durably
checkpointed before safe-fact extraction or W-, and the final nested bundle is
fully replayed from its byte-pinned validity and submission evidence.

The holdout remains inactive, unpublished, and fixed-route. Its OpenRouter
adapters can be composed without network access: complete trusted joint-author
reduction runs inside the governed semantic retry loop, and an additive
joint-credit adapter accepts the standard safe-fact request plus the
boundary-aware joint W- profile under the exact Work V2 judge identity. A
manual-only hosted runner now adds fresh-run checkpoints, durable attempt
journals, exact K1-K3 stage ordering, request/token/cost stops, and a
request-side OpenRouter price filter. It has read-only repository permission,
retains local artifacts, and cannot publish or continue. Merge alone makes no
provider call; every paid K1-K3 sample still requires a distinct exact manual
dispatch authorization.

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
| Parallel primary judgments | Implemented with exact-subject automatic dispatch, same-subject queue/replan deduplication, and distinct-subject concurrency; validity v4 adds subject-and-declared-reference terminal-attestation deferral | `math_flow/judgments.py`, `.github/workflows/project-openrouter.yml` |
| Conflict detection and reconciliation | Retained for replay and governed historical specs; no active research projection declares a reconciliation judge | `math_flow/judgments.py`, `.github/workflows/project-openrouter.yml` |
| Coalescing, leased formation lanes | Implemented, including atomic submission-dependency components and one hosted lock spanning formation through final state publication | `math_flow/coordination.py`, `.github/workflows/project-openrouter.yml` |
| Batched hierarchical research state | `openrouter-research-v3` is active with validity v4 and audited builder v5; it forms sibling/nested local-objective programs, enforces placement audits, and keeps existing topology fixed | `math_flow/research_projection.py`, `math_flow/research_state.py`, `docs/HIERARCHICAL_RESEARCH_PROTOCOL_V5.md` |
| Holistic hierarchical state and revisions | Implemented | `math_flow/formation.py`, `math_flow/knowledge.py` |
| Content-addressed projection publisher | Implemented, including optimistic cross-problem merge/retry and bounded GitHub commits | `math_flow/coordination.py`, `math_flow/projection_queue.py`, `math_flow/github_projection.py` |
| Provider-free congestion probe | Implemented; models concurrent problems, solvers, judge streams, projection lanes, atomic reconciliations, throttling, failure recovery, optimistic publication, chunking, catalog export, and agent context with zero provider calls | `math_flow/scale_probe.py`, `tests/test_scale_probe.py` |
| Repository-backed viewer | Implemented and deployed through ChatGPT Sites | `viewer/` |
| Non-UI agent discovery and context commands | Implemented; canonical problem discovery includes admitted problems with no projection, omitted context selection resolves exactly one active registered knowledge lane while explicit IDs preserve historical access, `credit-status` reads governed policy without a run, and `register-direction` scaffolds a policy-neutral initial event | `math_flow/discovery.py`, `math_flow/context.py`, `math_flow/credit_context.py`, `math_flow/solver_tools.py` |
| Solver-facing repository skill | Implemented; requires repository tools and exact-reference inspection | `.agents/skills/math-flow-solver/` |
| Builder-facing repository skill | Implemented; routes protocol and repository maintenance away from solver participation and requires isolated worktrees for parallel agents | `.agents/skills/math-flow-builder/` |
| Local/fractal Builder V10 experiment | Inactive, unpublished route/refine/author candidate with bounded digest-bound scopes, hidden-state preservation, provider-free widening through 1,024 programs, and a stopped BSSC paid holdout | `math_flow/research_builder_v10.py`, `math_flow/research_builder_v10_provider.py`, `docs/LOCAL_BUILDER_V10_FULL_SEND.md` |
| BSSC V10 plus separate V2 shadow runtime | Additive serial runtime and dispatch-only workflows are available for a fresh Builder V10 knowledge chain and an independently zero-origin A-first V2 accounting chain. Each active-form candidate requires its own byte-identical governed admission before execution; runtime deployment and admission make no provider call or projection publication. | `docs/BSSC_RESEARCH_V8_V10_V2_PROTOCOL.md`, `.github/workflows/project-research-v8-serial.yml`, `.github/workflows/project-bssc-v10-work-accounting-v2.yml` |
| Joint topology/W+ credit candidates | The unpublished K2-only hosted candidate freezes one accepted W+ result and derives submission credit. The additive K1-K3 holdout serializes three fixed local author scopes, live W+, boundary-aware W-, and direct submission allocation with exact bundle replay. Its manual hosted seam is fresh-run-only, hard-budgeted, read-only, and publication-forbidden; merge never dispatches it. | `math_flow/joint_portfolio_credit_experiment.py`, `math_flow/joint_portfolio_serial_holdout.py`, `math_flow/joint_portfolio_serial_hosted.py`, `.github/workflows/hosted-bssc-joint-portfolio-k1-k3.yml`, `protocol/experiments/bssc-joint-portfolio-serial-k1-k3-v1/` |
| Serial joint portfolio candidate V2 | Inactive reducer milestone generalizes joint knowledge/topology/live-W+ through K1/K2/K3, cumulative work-policy boundaries, support-versus-supersession semantics, root-owned and shared results, bounded lifecycle/move operations, typed evidence, frozen W+ replay, safe-facts/W-/positive-D, and direct submission allocation. Provider-neutral and OpenRouter author/credit adapters plus the bounded K1-K3 hosted holdout now exist, but there is no projection, publication, continuation, or viewer path. | `math_flow/joint_portfolio_serial_transition_v2.py`, `math_flow/joint_portfolio_serial_provider_v2.py`, `math_flow/joint_portfolio_serial_credit_v2.py`, `math_flow/joint_portfolio_serial_hosted.py`, `docs/JOINT_PORTFOLIO_SERIAL_CANDIDATE_V2.md` |
| Protocol evaluation substrate | Provider-free manifest/replay/scoring harness, builder/work-accounting scale probes, bounded accounting-root-total replay, eight-submission exact V10-scoped miniature using the real V2 provider adapter plus public bundle run/load replay over 24 local capture-transport invocations, and review-gated No-Three zero-call serial preflight implemented. An additive seven-component umbrella suite now runs those checks in bounded `pr` or exact-regenerating `full` mode, emits canonical JSON/Markdown summaries, and accepts no provider or publication authority; paid semantic V10/V2 execution and judge-quality evaluation remain pending. | `math_flow/teacher_student_scenarios.py`, `docs/PROTOCOL_EVALUATION_SUITE.md`, `docs/PROTOCOL_EVALUATION_ROADMAP.md` |
| Typed projection dependencies | Implemented in PR #20: governed declarations plus exact verified knowledge-state locks | `math_flow/governance.py`, `math_flow/projection_dependencies.py` |
| Credit overlay runner, profile, cadence, and publication transport | Active credit-v3 uses the two-term common-horizon hierarchical evaluator over locked research-v3 state/history; governed local/hosted execution, provider-free eligibility, bounded semantic retries, rolling coalescing, predecessor-chain terminals, and independent bundles are implemented | `math_flow/research_credit.py`, `math_flow/credit.py`, `math_flow/credit_schedule.py`, `.github/workflows/project-credit.yml` |
| Hierarchical work accounting V1 and V2 | Both BSSC-only lanes are active. V1 preserves the original no-access/with-access comparison; additive V2 freezes a validated with-access `W+` candidate in immutable CAS before estimating direct same-base no-access `W-`. Their identities, histories, and workflows remain separate. | `math_flow/work_projection.py`, `math_flow/work_accounting_pipeline.py`, `docs/WORK_PROJECTION_V2.md`, `protocol/projections/openrouter-work-accounting-v1.json`, `protocol/projections/openrouter-work-accounting-v2.json` |
| Inactive local accounting slice | Provider-free experiment keeps complete accounting state in trusted code and proves exact local root-total agreement with trusted full V2 for admitted cuts from bounded writable nodes plus digest-bound ancestor/boundary aggregates through 1,024 programs; trusted full V2 materializes canonical states and `D`, while over-wide dependency/completion/broad cuts fail rather than truncate; no provider or active profile | `math_flow/work_accounting_local_slice.py`, `docs/WORK_ACCOUNTING_LOCAL_SLICE_EXPERIMENT.md` |
| Research direction registration | Implemented: append-only schema/reducer, atomic validation and auto-merge, provider-free CLI/context/catalog refresh, solver skill, viewer, and historical registration-aware qualitative credit-v2 artifacts | `math_flow/directions.py`, `protocol/schemas/research-direction-event.schema.json`, `viewer/` |
| Objective verifier attestations | Additive v1 recipe, bounded pinned OCI runner, durable bundle, uniqueness/semantic validation, automatic hosted execution and signed publication, replay, context, viewer presentation, v3 subject-local deferral, and v4 declared-reference deferral/redispatch implemented | `math_flow/attestations.py`, `.github/workflows/project-attestation.yml`, `docs/OBJECTIVE_ATTESTATIONS.md` |
| GitHub App / immutable contributor identity | Not yet implemented | `docs/MVP.md` |

The active production path is intentionally small:

- `openrouter-research-v3` uses parallel validity-v4 judgments, no
  reconciliation stage, audited hierarchical builder v5, and a five-minute
  formation interval. Its bounded validity packet includes terminal objective
  evidence for the subject and requesting transactions in the subject's
  declared-reference union. Formation imports only valid declared claims and
  follows only judge-selected required premises.
- BSSC also has active, separately versioned serial knowledge lanes V4 through
  V7. They replay the accepted validity-v4 history one submission at a time
  through Builders V6, V7, V8, and V9 respectively; each has its own projection
  identity, immutable history, and dedicated workflow. The additive V8/V10
  active-form candidate remains a separate fresh lane and becomes runnable only
  after its required one-file governed admission.
- `openrouter-research-credit-v3` has an exact dependency on that logical v3
  producer and is allowlisted for `bssc-sum-capacity` and
  `no-three-in-line-77`. It uses the common-horizon two-term policy and the
  hierarchical credit-v2 runner; both current assignments are locked to the
  exact current builder-v5 terminal for their problem.
- `openrouter-work-accounting-v1` remains the active BSSC comparison lane with
  its original branch order and immutable history.
- `openrouter-work-accounting-v2` is the separate active BSSC-only A-first lane
  over the serial research-v4 knowledge state. It advances only validated
  `W+`, retains same-base `W-` as an audit branch, and derives per-submission
  `D = W- - W+`.

The research-v3 producer is a wildcard specification, while the scheduled
wake-up is deliberately targeted to the two retained active problems. The
research-v1, research-v2, and research-credit-v2 governed specs are disabled,
as are the specialized no-three comparison lanes. Their content-addressed
objects remain valid explicit history and may be inspected by exact ID, but
ordinary dispatch follows every applicable active judgment stream, including
the dedicated BSSC V4 through V7 and work-accounting lanes. When more than one
active published knowledge lane applies—as it does for BSSC—context and viewer
callers must select the projection explicitly; omission fails closed instead of
silently preferring V3. No-Three currently retains V3 as its sole active
knowledge lane.

The active judge, builder, and credit evaluator are pinned to
`openai/gpt-5.6-sol` with high reasoning through OpenRouter. The registry allows
at most 16 parallel judgments and 500 dependency-connected judgments in one
formation batch. At the published head checked above:

- BSSC research-v3 is current at `9ff49a7`, with four active non-root sibling
  programs for code-induced converse structure, relaxed UV functionals,
  auxiliary-receiver converses, and multiletter Marton achievability.
- No-three-in-line research-v3 is current at its unchanged problem ledger head,
  with sibling certified-configuration and rotational-symmetry programs and the
  nested `rotational-symmetry/rct4` program.
- Credit-v3 is current and non-stale for both exact research terminals.

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
control to return to the latest state. The app embeds no checked-in problem
snapshot; an unavailable or valid-but-empty repository catalog produces an
explicit empty screen, so archived research cannot reappear during an outage.
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
- **Q0 exact-subject handoff:** canonical BSSC contribution `e2bbc1e` has passed
  objective-attestation receipt `sha256:6dfb1921...`. Exact-subject research-v3
  run `32407861386` published historical knowledge terminal
  `sha256:08b406e1...` at that exact problem-ledger head, proving the handoff
  before the later builder-v5 replay.
- **Queue handoff:** the objective run exposed a missing repository binding in
  the checkout-free successor dispatcher. PR #19 fixed it. Run `31570610937`
  then completed the then-current projection and successfully dispatched run
  `31570656849`, which reused the existing primary judgment and brought a second
  knowledge projection current. The cadence wake-up subsequently dispatched the
  then-active credit overlays; registration-aware run `31570861867` published a
  historical five-contribution terminal.
- **Viewer and dependency chain:** public Sites version 18 is deployed at the
  canonical research-atlas URL with objective-verification presentation and
  follow-head semantics. The exact merged viewer build, nine rendered tests,
  lint, and npm audit pass; the default
  branch has zero open Dependabot alerts and recent production worker logs have
  no errors.

Non-UI agents resolve the verified research-v3 predecessor-chain terminal
through `math_flow context`; that command never invokes a judge or credit model.
When `--projection` is omitted it selects exactly one published lane carrying an
active governed projection identity, and fails if none or more than one exists.
Omission therefore selects `openrouter-research-v3` for No-Three, but BSSC has
multiple active knowledge projections and requires an explicit `--projection`.
An explicit logical or content-addressed ID remains available for historical
inspection. The governed cadence layer wakes every five minutes, plans without
a provider, and dispatches only eligible overlays.

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

The active registry retains exactly two problems:

- `bssc-sum-capacity`;
- `no-three-in-line-77`.

Seven earlier admitted namespaces, including the original
`triangle-midpoints` fixture, are archived. Their canonical ledgers and
published projection objects remain intact, but ordinary discovery, new
participant events, scheduling, recovery, and the live viewer exclude them.

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
5. The active `openrouter-research-v3` producer has `allowedProblems: ["*"]`,
   uses validity v4 and builder v5, and has a five-minute formation interval, so
   no knowledge-projection admission is required for the baseline scale pilot.
   Superseded comparison lanes are disabled. Credit-v3 remains explicitly
   allowlisted to the two retained problems; extending credit or introducing a
   specialized knowledge policy requires a separate governed projection edit.
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
   each applicable active OpenRouter judgment stream for only the affected
   problem and exact merged transaction. The general producer handles
   `openrouter-research-v3`; the active BSSC-only V4 through V7 projections use
   their dedicated serial workflows. If the merged transaction contains
   `verification.json`, the
   auto-merger also dispatches the trusted, provider-free objective-attestation
   workflow for that exact squash SHA. A direction event dispatches only the
   provider-free viewer-catalog refresh because it has no mathematical judgment
   effect.
5. Automatic OpenRouter coverage planning targets the dispatched transaction
   and emits a one-item or empty matrix according to the active judge-spec
   digest. Different subjects retain independent concurrency; duplicate
   same-subject triggers wait and replan to zero after successful publication.
   Validity v4 defers a transaction requesting objective verification, or one
   citing a reference with a pending requested verification, until the exact
   terminal attestation exists; unrelated subjects stay in the matrix and
   continue in parallel. It scans only the subject and the claim-declared
   reference union, never the preceding ledger. Terminal attestation publication
   diffs pre/post coverage and redispatches each exact newly-ready subject in the
   active validity-v4 judge stream.
6. Each paid primary result is verified and published as an immutable object
   before reconciliation or formation and without touching the scheduler. One
   projection/problem lock then spans formation through final knowledge-state
   and scheduler publication. The reconciliation-free validity-v4 lane may
   integrate ready independent judgments while another primary is pending;
   `knowledge-trigger` withholds any claim whose required-premise judgment is
   absent. Historical reconciliation behavior remains available only to replay a
   governed spec that declares it.
   Durable recovery treats reusable published judgments absent from the lane's
   observed IDs as fresh work even when the problem ledger is unchanged.
7. Validity v4 derives formation edges from the exact required premises selected
   by the primary judge, retains broader declared references only as provenance,
   and binds bounded reference-attestation evidence to the immutable packet. The
   validity-v2/v3 dependency and reconciliation paths remain historical replay
   behavior, not active production fan-out.
8. Completed judgments are claimed dependency-atomically into one batched
   knowledge build, then published with the updated scheduler, indexes, and
   viewer catalog. Later knowledge projections using the same judge identities
   reuse those published judgments.
9. Cross-problem publications three-way merge disjoint scheduler lanes against
   the latest orphan-branch head and retry expected-head races. A scheduled
   wake-up pass redispatches due coalesced lanes every five minutes. For the
   explicitly allowlisted research-v3 problems it recomputes validity-v4
   coverage, dispatches each ready missing primary as an exact subject, and
   uses one subjectless wake only when formation/recovery remains with no ready
   primary gap. Exact-subject run history suppresses only that subject; legacy
   projection streams retain their subjectless behavior, while an allowlisted
   projection is suppressed completely outside its explicit problem allowlist.
   Batch-history suppression of that projection also suppresses any surviving
   projection in the same judge stream, so it cannot bypass the target boundary.
   An active sibling batch suppresses exact wakeups for that full stream until
   it finishes, and exact-subject history is shared across every sibling.
   Subjectless scheduled recovery carries a live no-primary-work guard, so a
   newly ready subject stops the run before provider work rather than widening
   it into a batch. Formation failures publish their claim rollback and an
   exponential retry marker;
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

If the complete judgment matrix succeeds but formation or publication fails,
do not rerun paid judgments. After fixing the downstream defect, dispatch
`project-openrouter.yml` with the same projection and problem and set
`resume_run_id` to the failed run. The workflow downloads and re-verifies the
retained judgment artifacts and skips the judgment matrix.

If one primary matrix job itself fails, its publisher first verifies and durably
publishes every successful sibling artifact that is a nonempty subset of the
frozen plan, then leaves the run failed. The same mechanism applies when
replaying a historical spec with a reconciliation matrix. Use GitHub Actions'
**rerun failed jobs** operation on that original run. This regenerates only the
missing item and then reruns the dependent formation and publication jobs. A
subjectless `resume_run_id` can preserve an already-produced in-plan subset
while excluding and reporting whole out-of-plan bundles, but it cannot
regenerate missing work and is not a partial-matrix repair mechanism.

Formation caches successful provider stages by exact request digest. Empty
assistant messages are retried up to three times and are never checkpointed;
length-truncated responses are also non-cacheable.

Hosted reconciliation remains implemented and fail-closed for replay of legacy
projection specs, but no active projection invokes it. Deterministic and
fake-provider tests cover opposed primaries, conflict derivation,
reconciliation reuse, dependency-atomic formation, and rejection of missing
conflict inputs. The research-v3 validity-v4/builder-v5 path consumes validity
outcomes directly and refuses dependencies excluded from accepted research
state.

## Agent roles and working conventions

### Mathematical solver agents

Read and follow `.agents/skills/math-flow-solver/SKILL.md`. Use
`python3 -m math_flow context` to materialize a verified latest state, inspect
provenance and current governed credit, select an open direction, and submit exactly
one atomic participant event per PR. Inspect `directions.json`, `credit.json`,
and the optional raw
`credit-report.md` rather than the UI; active hierarchical credit is
counterfactual causal-work attribution and does not alter mathematical validity.
A direction registration may precede
substantial work, but it is optional and non-exclusive; complete it in a later
atomic event referencing the canonical contribution transaction. The viewer has
no embedded fallback problem; its catalog-unavailable screen is deliberately
empty and is never a source of current knowledge or scoring.

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
   In particular, never update a builder file referenced by an active governed
   projection in place. Projection lanes are named by the projection-spec digest
   but retain their original builder-spec digest; an in-place builder change can
   leave the lane bound to the old digest and is rejected before a new claim is
   formed. Add a versioned builder/implementation, preserve the old file for
   replay, and admit a new or edited projection in its required separate one-file
   governed PR. Deploy runtime support before admitting that projection.
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
python3 -m math_flow list-problems \
  --head origin/main \
  --projection-dir <detached-projections-worktree>
python3 -m math_flow ledger --problem no-three-in-line-77 --head HEAD
python3 -m math_flow directions --problem no-three-in-line-77 --head HEAD
python3 -m math_flow credit-status --problem no-three-in-line-77 --head HEAD
python3 -m math_flow resolve-projection \
  --projection openrouter-research-v3 \
  --problem no-three-in-line-77 \
  --head HEAD
python3 -m math_flow render-request --help
python3 -m math_flow context --help
python3 -m math_flow context \
  --problem no-three-in-line-77 \
  --projection openrouter-research-v3 \
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

1. **Evaluate builder-v5 program quality.** The first fresh v5 states now prove
   that sibling and nested local-objective programs can be formed. Audit whether
   their boundaries remain useful as accepted work accumulates, then design the
   governed topology-evolution version that can move, reparent, split, merge,
   retire, and refresh affected local credit without rewriting history.
2. **Complete and calibrate an end-to-end credit candidate.** The unpublished
   joint K2 experiment now proves one frozen-W+ to W- to submission-allocation
   path. Extend it through an ordered miniature and then a small real history;
   compare repeated fixed-input samples, growing accepted histories, safe-fact
   exposure levels, and node-level drivers. Test whether counterfactual evidence,
   local scope, live-W+ chaining, corrections, and hour estimates are stable
   enough for the intended semantics before introducing a finite award pool or
   time-bucketed allocation profile.
3. **Run the hosted scale pilot.** The provider-free congestion probe covers
   scheduler, retry, merge, chunking, viewer, and context invariants locally.
   Admit several real problems with simultaneous solver contributions to
   measure GitHub runner/API congestion and confirm the same behavior on the
   organization repository without changing the protocol under load.
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

That registration-aware credit-v2 profile belongs to the superseded qualitative
credit lane. The active hierarchical credit-v3 evaluator does not currently
ingest direction events; adding direction-priority evidence to its causal-work
policy would require an explicit governed design change.

The MVP supports these immutable events:

- `register`: describe a specific intended direction, motivation, proposed
  evidence or method, and optional related knowledge-node IDs;
- `update`: supersede a prior registration with a more precise scope or plan;
- `release`: state that the participant is no longer actively pursuing it; and
- `complete`: connect the registration to a submitted contribution without
  claiming that the contribution is correct or sufficient.

Each event identifies its direction and predecessor where applicable;
author identity and priority time come from the canonical squash transaction.
Every `release` event must match the originating registration's exact Git author
name and email. This provides repository-level continuity so another participant
cannot release the registration; a future GitHub App should replace this
metadata identity with a stable authenticated provider ID.
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
4. A registration-aware qualitative credit-v2 profile that receives verified
   direction events as typed inputs and cites their canonical transaction IDs.
   Its published bundles and the earlier credit-v1 bundles remain immutable
   historical artifacts.

Automatic merge accepts a valid one-event direction PR using the same trusted
revalidation pattern as solver contributions. It refreshes the repository-backed
catalog without dispatching a mathematical or paid projection. Direction
registration introduces no locks, exclusive claims, or requirement to register
before submitting mathematics.

The first complete hosted lifecycle remains canonical: registration `a9552d14`,
proof contribution `29ccbd39`, and completion event `bbf27430`. Its historical
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
- `docs/BSSC_KNOWLEDGE_CREDIT_AUDIT.md` — non-normative BSSC formation/credit
  audit and the settled design record for the proposed hierarchical
  work-remaining successor.
- `docs/BSSC_RESEARCH_V4_SERIAL_PRODUCER.md` — exact historical validity-v4
  frontier, one-submission builder-v6 production, recovery, and activation
  boundary for the BSSC K0-to-K16 chain.
- `docs/BSSC_RESEARCH_V7_CONTEXT_EXPERIMENT.md` — active BSSC-only Builder V9
  progressive-context contract, provider-free measurements, serial route, and
  stop conditions.
- `docs/LOCAL_BUILDER_V10_FULL_SEND.md` — inactive local/fractal Builder V10
  checkpoint, exact implementation changes, empirical scale findings, limits,
  and next evaluation sequence.
- `docs/BSSC_RESEARCH_V8_V10_V2_PROTOCOL.md` — additive serial Builder V10
  knowledge and separate A-first V2 accounting runtime, admission, publication,
  and semantic-evaluation boundaries.
- `docs/MINIATURE_E2E_PROTOCOL_EVALUATION.md` — provider-free eight-submission
  V10/V2 candidate contract, including the real V2 adapter and public bundle
  replay over a local capture transport, exact knowledge/work bindings, and
  adversarial scorecard. Its semantics remain precommitted oracle inputs rather
  than a judge-quality result.
- `docs/PROTOCOL_EVALUATION_SUITE.md` — additive seven-component provider-free
  umbrella command, PR/full mode boundary, canonical summary contract,
  zero-authority invariants, and component-registry extension policy.
- `docs/PROTOCOL_EVALUATION_ROADMAP.md` — staged path from provider-free reducer
  and scale checks through paid holdouts, miniature problems, adversarial audit,
  and possible shadow activation.
- `docs/WORK_PROJECTION_V2.md` — active BSSC A-first work-accounting profile,
  frozen-live-state boundary, epistemic policy, and retry-isolation contract.
- `protocol/experiments/bssc-joint-portfolio-credit-k2-v1/README.md` —
  unpublished K2 joint topology/W+ to W- candidate, submission allocation, and
  hosted execution boundary.
- `docs/JOINT_PORTFOLIO_SERIAL_CANDIDATE_V2.md` — inactive generalized joint
  knowledge/topology/live-W+ reducer, cumulative boundary state, serial credit
  adapter, tested lifecycle, and explicit deferred topology cases.
- `docs/MVP.md` — architecture, phased roadmap, and deferred decisions.
- `docs/HIERARCHICAL_RESEARCH_PROTOCOL_V5.md` — current audited initial
  sibling/nested program formation, fixed-topology boundary, and rollout.
- `docs/HIERARCHICAL_RESEARCH_PROTOCOL_V6.md` — inactive provider-free
  per-submission state-v2 topology evolution, same-world handoff contract, and
  BSSC serial-producer foundation.
- `docs/HIERARCHICAL_RESEARCH_PROTOCOL_V4.md` — validity-v4,
  reference-attestation, dependency-safe batching, and the superseded v4 builder
  baseline retained for replay.
- `docs/HIERARCHICAL_RESEARCH_PROTOCOL_V2.md` — superseded historical
  validity-v2/builder-v2 architecture retained for replay.
- `docs/HIERARCHICAL_RESEARCH_PROTOCOL_V3.md` — superseded validity-v3 and
  subject-attestation rollout retained for replay.
- `docs/HIERARCHICAL_RESEARCH_PROTOCOL_V1.md` — serialized replay and
  hierarchical-credit reference path.
- `docs/PROJECTION_PROTOCOL.md` — run envelopes, profiles, revisions, and
  builder flexibility.
- `protocol/projections/openrouter-research-v3.json` — active validity-v4 and
  builder-v5 producer registration.
- `protocol/projections/openrouter-research-credit-v3.json` — active hierarchical
  credit consumer and exact research dependency.
- `protocol/policies/two-term-hierarchical-research-credit-v1.md` — current
  common-horizon direct-work plus obviated-work credit semantics.
- `docs/PARALLEL_JUDGMENTS.md` — judgment/reconciliation/formation command flow.
- `docs/GOVERNANCE.md` — problem and projection admission policy.
- `docs/REMOTE_TESTING.md` — hosted workflow testing and recovery.
- `viewer/README.md` — repository-backed atlas behavior and local testing.
- `.agents/skills/math-flow-solver/SKILL.md` — mathematical solver workflow.
- `.agents/skills/math-flow-builder/SKILL.md` — protocol and repository builder workflow with isolated parallel worktrees.

If this document conflicts with executable validators, registered specs, or
workflow code, those are authoritative. Update this document in the same PR that
changes an architectural invariant or operational lifecycle.
