# Protocol evaluation roadmap

This document defines a staged path from local prompt regressions to empirical
end-to-end evaluation of knowledge formation and hierarchical work-remaining
credit. It is an evaluation plan, not a change to canonical policy or an
authorization for provider spending.

## Immediate objective: one full credit candidate

The next candidate should join one fixed knowledge-builder version to one fixed
work-accounting version and process a small ordered history from an empty lane.
For each accepted submission `x`:

1. form the new knowledge state and exact topology alignment;
2. estimate the new live with-access state `W+` from the prior live state,
   submission evidence, and affected knowledge context;
3. freeze `W+`, estimate the same-world no-access state `W-`, and derive
   `D(x) = W- - W+` deterministically;
4. publish neither branch during the experiment, but retain every request,
   response, retry, patch, state, and reducer decision; and
5. advance the live state with `W+` exactly once before processing the next
   submission.

The first candidate should use the existing human-researcher-hour root contract,
the V2 A-first order, local program topology, and no uncertainty intervals or
manual review. Its purpose is to determine whether the complete construction is
coherent, not to calibrate a final economic payout.

The audit scorecard should include:

- every accepted submission receives strictly positive `D(x)`;
- completed work is zeroed in `W+`, while the corresponding same-world work may
  remain positive in `W-`;
- negative and partial results update only directly affected packages and
  ancestors whose aggregate state changes;
- a solving contribution can zero all genuinely resolved descendant work;
- dependencies are not double-counted as separate avoided work;
- duplicate or independently reproduced evidence does not receive the original
  result's full value again;
- topology revisions are evaluated in the revised same world and do not create
  work merely by revealing a previously implicit package;
- `W+` becomes the sole live input to later submissions, while historical `W-`
  remains an audit artifact; and
- node-level deltas reduce exactly to the displayed submission total.

Prior-credit corrections should be reported separately from current-submission
credit. The experiment should record which earlier allocation changed, the new
knowledge or topology that caused the correction, and whether the correction
changes only presentation/allocation or also changes a live work estimate.

## Context-capacity evaluation

Every provider adapter should emit common telemetry for every attempt:

- stage, model, configured context and completion limits;
- serialized characters and provider-reported prompt, cached, reasoning,
  completion, and total tokens;
- bytes and tokens by logical component: system prompt, schema, problem,
  submission evidence, accepted assessments, full state, local impact context,
  safe facts, frozen `W+`, and retry feedback;
- counts of programs, intermediate results, contributions, dependency-loaded
  results, omitted supports, included local nodes, and collapsed boundary nodes;
- finish reason, output characters, trailing-whitespace characters, validation
  class, and retry cause; and
- cost and elapsed time where the provider reports them.

Capacity testing must distinguish three failure classes:

1. **hard input exhaustion** — the serialized request no longer fits;
2. **hard output exhaustion** — the response hits its completion limit, including
   pathological whitespace or repetition; and
3. **soft context degradation** — the request fits, but the judge misses,
   duplicates, overgeneralizes, or forgets relevant information.

Build deterministic synthetic histories at increasing sizes and record behavior
near 50%, 70%, 85%, and 95% of the configured input budget. Vary dimensions
independently: evidence bytes per submission, number and depth of programs,
number of results, dependency-closure width, result-support size, local-subtree
width, and retry-feedback size. Hard-limit tests can be provider-free. Soft
degradation needs hidden-answer probes distributed near the beginning, middle,
and end of otherwise realistic context.

Current implementation evidence suggests different risk profiles by stage:

| Stage | Current locality | Primary growth risk |
| --- | --- | --- |
| Primary validity | One submission plus declared dependencies | Large submission or dependency evidence |
| Reconciliation | Conflicting judgments/evidence component | Wide conflict component |
| Builder V9 | All program/result semantic records; support only for dependency closure | Linear long-history state plus current evidence |
| Builder V10 candidate | Bounded route/refine/author read set; cumulative support and provenance hidden behind counts/digests | Large selected local closure, repeated capsules, or current evidence |
| Safe facts | Full live accounting baseline, local impact context, current evidence | Global accounting state or large current submission |
| Work `W+` | Full live accounting baseline, local impact subgraph, current evidence | Global accounting state, large local subtree, or submission |
| Work `W-` | Full live accounting baseline and full frozen `W+`, plus local structural context; no raw evidence | Two global accounting states plus local subtree/patch |
| Publication/viewer | Immutable history and catalog summaries | File count, catalog size, and rendering rather than model context |

No stage should silently truncate. When a budget is exceeded, the protocol
should fail with a measured component breakdown until a versioned deterministic
compaction or retrieval rule is adopted. Naive prefix/suffix truncation would
break provenance and can create path-dependent judgments.

## Regression pyramid

Use one common scenario format and run it at progressively more expensive
levels.

### 1. Deterministic reducer tests

Provider-free unit and property tests cover schemas, digests, state replay,
topology alignment, `W+`/`W-` reduction, positive `D`, retry identity, and exact
publication. Add adversarial split, merge, reparent, duplicate, correction,
dependency, and solved-subtree fixtures.

### 2. Provider-free scale tests

Extend the existing congestion probe with serialized request construction and
component telemetry. Generate large but valid knowledge and accounting states,
exercise bounded impact-context selection, and assert that no provider call is
needed to identify hard budget crossings.

### 3. Teacher-student microcases

Keep the current prompt experiments, but express them as small ordered scenario
manifests with relational gold rather than bespoke scripts. Score topology,
semantic partition, qualification fidelity, operation validity, retry behavior,
token use, and cost independently.

Add a safe-fact exposure ablation with the subject, base state, frozen `W+`,
model identity, and seed held fixed. Compare an outcome-only summary, a normal
semantic paraphrase, a near-verbatim result summary, and an intentionally
proof-bearing/actionable summary while every arm retains the same structural
ban on raw evidence containers and attached evidence files. Measure changes in
`W-` totals, node patches, scope, retries, and cost across repeated samples. The
test should identify material semantic anchoring; it must not substitute a
substring-overlap score for counterfactual quality.

### 4. Sequential real-contribution holdouts

Freeze accepted repository judgments and evidence, hide later submissions, and
test whether the builder maintains stable, useful programs as evidence arrives.
The BSSC K1/K2/K3 experiment is the first instance of this level.

### 5. Miniature end-to-end problems

Curate problems with roughly three to eight ordered submissions and a known
reference work portfolio. A useful benchmark suite should jointly contain:

- two independent research routes;
- a dependency chain;
- a negative result that prunes work;
- a partial positive result;
- a decisive result that completes a package or the problem;
- a duplicate or independent reproduction;
- a later topology revelation or correction; and
- at least one contribution spanning more than one program.

Synthetic mathematical histories are acceptable initially because they let the
suite precommit ground truth and exercise rare cases. Small real problems should
then test ecological validity. Later truth must remain hidden from earlier
knowledge and work judges except through the explicitly defined same-world
counterfactual stage.

### 6. Adversarial end-to-end audit

Give a separate evaluator the complete transcript, frozen oracle portfolio, and
final artifacts. Ask it to find major accounting failures rather than reproduce
the builder's reasoning. Score concrete counterexamples: missing work, invented
work, incorrect ancestry, dependency double counting, duplicated credit,
nonpositive deltas, implausible hour scale, inconsistent sibling estimates,
unjustified corrections, and credit that changes under semantically irrelevant
batching or IDs.

An adversarial LLM is evidence, not an oracle. Its findings should be tied to
specific nodes, states, and deterministic reductions, and verified by replay or
a second independent audit where possible.

### 7. Shadow and live lanes

Only candidates that pass the lower levels should run against a complete real
problem history. First run unpublished shadow lanes. Activate a canonical lane
only after its version, budgets, stop conditions, and cleanup/migration policy
are explicit.

## Common experiment harness

The present BSSC experiments are intentionally additive but repeat substantial
orchestration code. Replace that repetition with a versioned scenario runner.
A scenario manifest should specify:

- frozen problem, ledger head, initial state, ordered subjects, and accepted
  judgment artifacts;
- builder, work-accounting, and optional adversarial-auditor specs;
- seeds, maximum attempts, maximum calls, token/cost stop budgets, and whether
  publication is forbidden;
- relational gold and scorer plugins for each stage; and
- expected artifacts and replay checks.

The runner should produce one common artifact envelope containing raw attempts,
normalized telemetry, all intermediate states, deterministic scorecards,
semantic-audit findings, and an aggregate report. CI tiers can then be explicit:

- pull request: provider-free reducers and scale construction;
- scheduled: a small fixed paid regression set within a hard budget; and
- manual approval: complete end-to-end or new-model calibration runs.

Repeated judge samples estimate sampling variance only when the subject, state,
prompt, model identity, and evidence are held fixed. Cross-submission dispersion
and disagreement between protocol versions must be reported separately.

The provider-free V1 substrate is implemented in
`math_flow/teacher_student_scenarios.py` and documented in
`docs/TEACHER_STUDENT_SCENARIOS.md`. It supports arbitrary ordered stage
sequences, including route-to-author local builders, but intentionally has no
provider or publication adapter. The BSSC K2/K3 V3 holdout is its first migrated
scenario and retains the original Markdown gold alongside an executable
relational sidecar.

The inactive local Builder V10 candidate now supplies the next two layers:

- valid synthetic state-v3 scale fixtures through 1,024 programs, 2,048
  intermediate results, and 32,768 represented submissions;
- six deterministic adversarial routing/topology cases and beginning/middle/end
  soft probes;
- an actual V10 route/refine/author constructor measurement using the fixture's
  oracle-correct route, rather than only an idealized local-packet model; and
- a manifest-bound unpublished BSSC K2/K3 provider holdout with request, token,
  call, and reported-cost stops plus executable relational scoring.

At the largest provider-free case, V9's maximum request is estimated at
4,018,994 tokens and V10's actual-constructor, oracle-correct-route packet at
50,150. V10's three-stage cumulative estimate is 100,201. This is strong
evidence that locality plus trusted provenance/support expansion addresses
global history growth for a correct bounded route, but it is neither a
maximum-legal-route bound nor a soft-semantic result. Paid tests must still
measure retrieval quality,
especially a cross-program clue present in raw evidence but absent from the
accepted validity summary; that case may require one bounded author-initiated
re-route or a stronger validity-to-builder semantic contract.

The provider-free miniature end-to-end candidate is implemented in
`protocol/experiments/miniature-e2e-v1/`. It digest-binds the Builder V10
experiment and work-accounting V2 spec/policy, substitutes precommitted
synthetic semantic choices, reconstructs and binds each exact V10 route context
and local authoring packet, and replays eight ordered submissions through the
scoped V10/V8/V7 reducers. For every submission it now constructs the real
`OpenRouterWorkProjectionProviderV2` with a local stage-aware capture transport
and uses the public `PROFILE_V2` `run_work_projection_bundle` and
`load_work_projection_bundle` path. The fixed transcript makes exactly 24 local
transport invocations—safe facts, `W+`, and `W-` for each submission—with zero
network calls, external/provider spend, or publication. It binds exact
synthetic evidence and assessment inputs, the full frozen `W+` candidate, and
the `W-` firewall/candidate boundary. This completes the provider-free
request/bundle-replay portion of the first recommended item; it does not
replace a paid semantic run, a model-quality evaluation, or an independent
adversarial audit.

The actual Work Accounting V2 request path now has a separate provider-free
16-case scale probe through 1,024 programs. All deterministic semantic checks
pass, but every 1,024-program `W-` request crosses the nominal 128,000-token
input proxy and reaches as high as 320,613 estimated tokens. The local impact
subgraph is therefore not sufficient by itself: current V2 requests repeat the
complete live accounting state, and `W-` repeats the complete frozen `W+` state
as well. A bounded digest-bound accounting slice with an independently checked
root-total reduction is required before making locality claims.

An additive inactive local-slice experiment now supplies that deterministic
root-total check. It retains complete global state in trusted code and exposes
exact writable nodes plus digest-bound ancestor and boundary aggregates. All
20 cases admitted by its default bounds reproduce the trusted full reducer's
`W-` and `W+` root totals through 1,024 programs; trusted full V2 then creates
the canonical states and `D`. Four dependency, decisive-completion, or broad
cases fail closed rather than truncate. Agreement is conditional on the impact
cut containing every patch target; scope sufficiency remains a semantic
question. This is not yet a Work Accounting V3 request format or a
semantic-judge result. See `docs/WORK_ACCOUNTING_LOCAL_SLICE_EXPERIMENT.md`.

The small-real-problem provider-free preflight is implemented at
`protocol/experiments/no-three-v10-v2-shadow-v1/`. It binds the four exactly
accepted No-Three-in-Line submissions, their Git/evidence/judgment/attestation
artifacts, the candidate specs, an experimental V10 projection descriptor, and
a problem-specific root-contract review draft without provider or publication
authority. Its zero-call runner verifies the bindings and zero origins and
emits the exact 36-stage serial plan with 24 nominal provider stages, at most 72
attempts, and 840,000 reserved completion tokens. It materializes no semantic
request because later requests require trusted predecessor K/W outputs. The
root contract still needs review, and the provider-free preflight is not the
later checkpointed semantic runner.

## Provider-free umbrella suite

The additive `protocol-evaluation-suite-v1` manifest now exposes the seven
implemented provider-free evaluation components through one command:

```bash
python3 -m math_flow protocol-evaluation-suite \
  --mode pr \
  --output-dir /tmp/math-flow-protocol-evaluation-pr
```

The required ordered components are builder context scale, Builder V10
provider-free widening plan, final V2 BSSC K2-only dry-run, miniature V10/V2
require-pass replay, Work Accounting V2 context scale, the local-slice
root-total replay, and the exact No-Three preflight. Pull-request mode verifies
every locked artifact, runs bounded scale/reducer smokes, and fully runs the
other four checks. `--mode full` exact-regenerates all three complete reports;
the remaining four checks are unchanged.

The command accepts neither provider credentials nor provider/publication
execution flags. Both modes verify an aggregate of zero provider calls, no
network use, and no publication attempt, then write canonical `summary.json`
and `summary.md`. This unifies regression execution only; it does not advance a
candidate to a paid tier or authorize any step below. The manifest uses a
trusted component registry rather than executable paths, and the local-slice
component was appended without changing the summary envelope.
See `docs/PROTOCOL_EVALUATION_SUITE.md` for the normative command, manifest,
summary, and extension contracts.

## Recommended sequence

1. **Complete — miniature V2 request/bundle replay.** The eight-submission
   fixture uses the real V2 provider adapter behind a local stage-aware capture
   transport, calls the public run/load bundle APIs, and records 24 local
   invocations without network, spend, or publication. Its safe facts and
   primitive responses remain deterministic oracle inputs, so this completion
   establishes request/bundle mechanics and bindings, not judge quality.
2. Run exactly one corrected BSSC K2-only holdout. Require root ownership and
   the conditional-parent test before running K3, another seed, or a wider paid
   fixture.
3. If K2 passes, widen paid route/refine teacher-student cases gradually through
   16, 64, 256, and 1,024 programs, stopping at the first semantic or budget
   concern.
4. **Complete — append the accounting-slice replay.** It is now included in the
   seven-component umbrella suite without replacing the full-state scale
   regression or changing the summary envelope. Convert it into a separately
   versioned candidate request only after prompt/semantic tests, explicit
   bounds, and a deterministic choice for cases where boundary aggregates are
   larger than the full state. Keep active V2 unchanged until those tests pass.
5. Review the No-Three-in-Line root-contract draft, then extend the completed
   zero-call preflight into a checkpointed, publication-forbidden semantic
   V10-to-V2 runner with a request-side verified price bound.
6. With separate provider authorization, run its four accepted submissions
   serially from zero and stop before the next subject on any protocol concern.
7. Run an independent adversarial transcript audit before creating a shadow
   output profile or considering activation.
