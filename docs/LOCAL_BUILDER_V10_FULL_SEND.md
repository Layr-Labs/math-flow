# Local Builder V10 full-send checkpoint

Status: completed inactive experimental build, 2026-09-01. Nothing described
here activates a judge, changes a production projection, publishes a knowledge
or credit artifact, or changes the Research Atlas UI.

## Outcome

The repository now contains a complete local/fractal knowledge-builder
candidate and a widening evaluation ladder around it. The candidate keeps the
full canonical knowledge state in trusted storage while exposing only bounded,
digest-bound views to each model stage. It can be exercised provider-free at
synthetic scale, through precommitted teacher/student scenarios, and against an
exactly bound small real-problem history without creating a publication path.

The build also composes the intended A-first work-accounting order in a
provider-free eight-submission miniature. That composition reuses the existing
active BSSC Work Accounting V2 judge and policy, but the V10/V2 composition is
inactive and unpublished. It is not a new credit projection and it does not yet
run the semantic V2 judges on real evidence.

The candidate flow is:

```text
complete trusted state
        |
        v
compact recursive capsules + exact catalog commitments
        |
        v
route (no raw submission evidence)
        |
        v
trusted deterministic search and dependency expansion
        |
        v
route-refine (bounded discovery packet, no raw evidence)
        |
        v
trusted exact read set + existing/create write scopes
        |
        v
organize (local packet + exact current evidence)
        |
        v
trusted hidden-state expansion + unchanged state-v3 reducer
```

## Exact implementation changes

### 1. Trusted local/fractal state access

`math_flow/research_builder_v10.py` adds:

- a compact catalog of every program and intermediate result, committed to the
  exact predecessor state;
- recursive program capsules with bounded pages of children and linked results;
- deterministic topology-independent lexical search for distant consolidation
  targets;
- exact expansion of declared result dependencies, result dependencies,
  supersession targets, linked programs, relevant lineage peers, and ancestors;
- separate read, existing-write, and create scopes;
- authoring packets that replace cumulative support and provenance arrays with
  counts and digests; and
- a trusted application boundary that rejects stale bindings, out-of-scope
  mutations, unloaded references, and any change to an entity the transition
  did not operate on.

Mandatory closure fails when it exceeds a declared bound. It is never silently
truncated. Catalog traversal is iterative, so an adversarially deep valid tree
does not fail through Python recursion depth.

### 2. Sealed provider stages

`math_flow/research_builder_v10_provider.py` implements the experimental
OpenRouter route, route-refine, and organize stages. Route and refinement
receive accepted semantic guidance but zero raw evidence bytes. Organize alone
receives the exact current evidence. Trusted code restores hidden support,
claim, judgment, source, and program-result-link arrays before invoking the
unchanged reducer.

The provider-visible structured-output schemas use only the strict subset
accepted by OpenRouter. The trusted binder independently enforces uniqueness,
ID syntax and length, query length, per-array bounds, aggregate read/write/create
limits, and aggregate topology/content-operation limits.

The final inactive judge specification is
`openrouter-hierarchical-research-builder-v10-experiment`, with raw-file digest
`sha256:47528dfd15010796f3d6aaa2500ad8ec07e499cfeb5b5fd6bcd0c8522dbebffd`.
Its work-package rubric now makes these distinctions explicit:

- topical or mathematical dependence is not accounting ancestry;
- a child program belongs below a parent only when pursuing the child is
  conditional on pursuing the parent;
- independent activation or stopping conditions imply independently estimable
  work packages, including root-level siblings when appropriate; and
- the split test is applied in the same-world no-access portfolio even when the
  current contribution completes the package and leaves zero live work.

These are prompt-level accounting instructions, not a deterministic semantic
topology oracle.

### 3. Governed execution and replay

The experimental runners enforce publication prohibition, exact candidate and
fixture digests, request/call/token/cost reservations, attempt journals, and
terminal handling of unknown spend. Once a provider request may have left the
process, an outcome without a concrete response is terminal; it cannot cause a
second call. Concrete empty, invalid, or truncated responses retain the
versioned bounded diagnostic-retry path.

Scenario fixtures now bind the exact ordered stage-input artifact IDs and
digests they consume. Replay fails closed on substitution, reordering, unsafe
paths, symlinks, candidate drift, or a changed checked artifact.

### 4. Common teacher/student scenario substrate

`math_flow/teacher_student_scenarios.py` and the
`teacher-student-scenario` command provide a provider-free manifest, artifact,
budget, replay, and relational-scoring format. The BSSC K2/K3 holdout and the
miniature end-to-end history use this common substrate rather than relying only
on bespoke Markdown expectations.

### 5. Progressive scale and protocol evaluations

Four independent layers are checked in:

1. **Builder context scale.** Valid state-v3 fixtures widen from 16 to 1,024
   programs, from 24 to 2,048 results, and from 24 to 32,768 represented
   submissions. Six adversarial route/topology cases have positive and negative
   scorer controls.
2. **Route/refine widening.** A publication-forbidden manifest covers the same
   width series, cumulative hot-branch history, misleading capsules, distant
   duplicates, cross-program placement, root siblings, topology revision, and
   an explicit evidence-only routing limitation. Provider-free planning is the
   default; paid execution is separately gated.
3. **Synthetic end to end.** Eight ordered submissions exercise independent
   routes, dependency, pruning, duplicate support, topology correction,
   cross-program work, decisive completion, and a separate prior-credit
   correction record. The exact state-v3 and work reducers produce
   `D = [20, 5, 10, 15, 2, 2, 12, 59]` competent-human-researcher hours and 102
   hard assertions across eight adversarial groups.
4. **Small real-problem input audit.** The No-Three-in-Line shadow manifest binds
   all four exactly accepted contributions, contribution Git objects and
   evidence digests, validity artifacts, attestations, projection artifacts,
   V10/V2 specs, and observational historical V5 knowledge/credit states. It
   has zero execution authority pending its problem-specific root contract and
   a composed unpublished runner.

## Empirical findings

### Local Builder context growth

The provider-free builder report uses `ceil(compact UTF-8 bytes / 4)` as a size
proxy, not a provider tokenizer. With the fixture's precommitted correct route:

| Programs | Results | Represented submissions | V9 maximum | V10 maximum |
| ---: | ---: | ---: | ---: | ---: |
| 16 | 24 | 24 | 7,206 | 12,006 |
| 64 | 128 | 512 | 71,026 | 20,400 |
| 256 | 512 | 4,096 | 500,905 | 34,148 |
| 1,024 | 2,048 | 32,768 | 4,018,994 | 50,150 |

V10 has fixed multi-stage overhead and is larger at the smallest fixture. At
1,024 programs its maximum correct-route request is 98.8% smaller than V9's
global-state request. Its three-stage cumulative estimate is 100,201 tokens,
which matters for cost but not single-request capacity. This is evidence for
the locality mechanism, not evidence that a noisy router always chooses the
correct bounded scope or that semantic quality is stable at scale.

### Paid BSSC evidence

The first compatible paid holdout made nine provider requests. Eight returned
148,051 total reported tokens and $0.5386691 reported cost; one OpenRouter 502
had unknown usage/cost and correctly blocked further calls. The completed seed
reused one stable result across K2 and K3, but incorrectly nested K2's
independently activated UV work beneath the K1 branch. The holdout therefore
failed its central accounting-topology criterion and was not published.

That failure led to the final author-blind work-policy rubric above. The
corrected V10 candidate has a new digest and must not be evaluated by treating
the failed earlier sample as a pass.

### Work-accounting context growth

The provider-free Work Accounting V2 probe uses the real safe-facts, `W+`, and
frozen-`W+`/`W-` request constructors with an in-memory capture transport. All
16 semantic/adversarial cases pass and no provider/network call occurs. At
1,024 programs:

- safe facts is about 115,185 estimated input tokens;
- `W+` ranges from 120,068 to 209,703;
- `W-` ranges from 230,878 to 320,613; and
- every `W-` case crosses the probe's nominal 128,000-token input threshold.

The impact subgraph is local, but V2 still embeds the complete live accounting
state in every stage and the complete frozen `W+` state again in `W-`. This is
the clearest current long-running-problem risk. The next accounting revision
should keep global state in trusted storage and give the judges a digest-bound
local accounting slice plus the ancestor/decision-boundary aggregates needed
for exact reduction.

## What this checkpoint does not establish

- It does not activate or publish Builder V10.
- It does not create a new credit-assignment projection or UI view.
- The large builder fixtures measure correct-route construction and deterministic
  scorer behavior, not provider routing accuracy or repeated-judge variance.
- The miniature substitutes precommitted semantic outputs. It validates reducer
  order and invariants, not model judgment quality, epistemic-firewall quality,
  or hour calibration.
- The miniature uses the shared state-v3 reducer beneath V10 but does not pass
  its synthetic transitions through the V10 scoped authoring wrapper.
- No-Three-in-Line is input-bound but cannot execute until its own root contract
  and composed publication-forbidden V10-to-V2 runner exist.
- Deterministic lexical search is replayable but can miss paraphrases. Any
  semantic index would need its own versioned, digest-bound implementation.

## Recommended next sequence

1. Run one corrected BSSC K2 root-ownership holdout against the exact final V10
   digest, under a separate provider authorization and the existing hard stops.
2. Implement a bounded, digest-bound Work Accounting V2 slice and prove by
   provider-free replay that its sparse updates reduce to the same globally
   committed state as the current full-state path.
3. Add the No-Three-in-Line experimental root contract and composed unpublished
   real-evidence V10-to-V2 runner; review the contract before provider use.
4. Run the eight-submission miniature and then No-Three through semantic judges
   with precommitted relational scoring and hard spend/stop limits.
5. Add an independent adversarial transcript evaluator that reports concrete
   missing work, invented work, ancestry errors, dependency double counting,
   duplicated credit, nonpositive deltas, and unstable hour scales.
6. Only after those gates, run a full real-problem shadow lane. Activation and
   cleanup remain separate decisions.

Detailed contracts and reproduction commands are in:

- `docs/LOCAL_RESEARCH_BUILDER_V10.md`
- `docs/LOCAL_BUILDER_SCALE_EVALUATION.md`
- `docs/RESEARCH_BUILDER_V10_WIDENING_EXPERIMENT.md`
- `docs/MINIATURE_E2E_PROTOCOL_EVALUATION.md`
- `docs/WORK_ACCOUNTING_CONTEXT_SCALE_EVALUATION.md`
- `docs/NO_THREE_V10_V2_SHADOW_PLAN.md`
- `docs/PROTOCOL_EVALUATION_ROADMAP.md`
