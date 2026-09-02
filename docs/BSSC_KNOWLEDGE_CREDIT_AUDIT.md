# BSSC knowledge formation and work-accounting audit

Status: non-normative design and implementation audit. This document records
observed behavior, the work-remaining proposal evaluated on 2026-08-25, settled
design decisions, and remaining implementation questions. It does not change
the active builder, credit policy, schemas, reducers, projection registrations,
workflows, or published artifacts.

## Verified snapshot

The original audit used an isolated checkout and a detached copy of the
published projection branch. The exact heads were:

- `main`: `180e1032695f2b0f17238a01d7bc9e4ff4fb3f8f`;
- `projections`: `ebe7a32786e73c244a0c3f95d0e5a111869e1fdb`;
- terminal BSSC builder-v5 run:
  `sha256:6149417354857151da0e2ae910d608b457ec06ffe9d898f9db858e206198def5`;
- terminal BSSC research-state digest:
  `sha256:8ec126fc2b26334c836d951303a40b06fb2664c17a9bd7e8efce1ca63673f40c`;
- terminal BSSC credit-v3 run:
  `sha256:2cd8e34ff9045b26ad35b908e948a39f5494376b74c045d4295825e6f8a7a8cb`.

At that snapshot BSSC had 25 canonical contribution transactions: 16 with at
least one accepted claim and 9 wholly indeterminate. The v5 knowledge chain had
14 build runs, four of which were excluded-only empty transitions. The terminal
state had 5 programs including root, 21 threads, 39 items, and 16 contribution
records. The viewer exposed 65 knowledge nodes:

| Node kind | Count |
| --- | ---: |
| Programs | 5 |
| Questions/threads | 21 |
| Results | 16 |
| Proofs | 12 |
| Tools | 7 |
| Computations | 3 |
| Methods | 1 |

## Executive findings

1. **Knowledge formation is strongly path-dependent.** Builder v5 can add new
   sibling or nested programs, but cannot move or reparent an existing program,
   change a thread owner or kind, or move/retype an item. Early hierarchy and
   granularity decisions constrain every later state.
2. **The current hierarchy is admissible, not demonstrably optimal.** Every
   accepted BSSC contribution has a valid `local-objective` placement audit and
   none is directly at root. The four root children are a sensible first cut,
   but Marton and auxiliary-receiver work are broad enough to merit nested
   programs, while the three converse programs plausibly share a parent.
3. **Knowledge nodes are deliberately not submission nodes.** A submission can
   create or update results, proofs, methods, tools, computations, threads, and
   programs. Program/thread scaffolding also creates nodes. No governed
   one-submission/one-node invariant exists.
4. **The builder does not optimize semantic node count.** Its prompt asks for a
   small complete delta and coherent programs, while the reducer enforces
   legality, coverage, provenance, and placement. It cannot prove semantic
   minimality or reject every redundant durable lineage.
5. **Active credit-v3 re-estimates work at every knowledge terminal.** It sends
   one full common-horizon request covering every immediate child of every
   credit-bearing program, supplies no prior credit state to the reducer, and
   materializes all local evaluations anew. Deterministic code then validates,
   sums, normalizes, and propagates the new estimates.
6. **The active credit-bearing leaves are submission transactions, not knowledge
   items.** Programs are also assessed on their immediate parent edge. Results,
   proofs, tools, methods, computations, and threads supply state and evidence
   but do not receive independent allocations.
7. **Current work units are not operationally calibrated.** The policy describes
   expected future work under a competent adaptive solver, but active artifacts
   select no stable physical unit. All 21 BSSC threads have
   `expectedExposure: "1"`, while evaluator work values are neither derived from
   nor bounded by those values.
8. **The terminal credit input is incomplete.** The shared evidence helper caps
   each text artifact at 50,000 characters and total evidence at 300,000
   characters. Accepted ordinal 18 is truncated and accepted ordinals 19, 21,
   24, and 25 have no original bodies in the terminal credit input.
9. **Counterfactual dependency consistency is requested but not enforced.** The
   state contains item dependency links, but no reducer determines whether
   downstream information must be removed, retained independently, or assigned
   reconstruction work when a submission is withheld.
10. **Historical reference eligibility depends on formation batching.** A
    child's obviation ledger is the local pre-state of the build in which it
    first appeared. Different coalescing can therefore change which work was
    considered pre-existing.
11. **Hierarchical conservation does not eliminate causal overlap.** One child
    cannot count the same thread twice and local allocations conserve the
    parent pot, but different siblings can still claim overlapping causal
    reductions.
12. **The active projection is ex post only.** The policy discusses ex-ante
    forecasts, but credit-v3 has no ex-ante input, evaluator, or artifact.

## Knowledge formation and hierarchy

### Actual pipeline

Validity v4 evaluates each exact submission and chooses the required premises
for each valid declared claim. Builder v5 consumes only accepted claims and the
accepted submission evidence. It may inspect the submission to separate a valid
result from its proof, method, computation, or tool, but may not import unjudged
assertions.

One coalesced builder call may integrate several dependency-ready judgments into
one atomic delta. The reducer checks exact contribution coverage, accepted-claim
provenance, a strict program tree, one unstructured thread per active program,
local/direct-thread mappings, item dependencies, and placement audits. Invalid
and indeterminate bodies do not become standalone knowledge.

### Evidence of path dependence

The initial BSSC v5 run created three sibling root programs for code-induced
structure, relaxed UV functionals, and auxiliary-receiver converses. The Marton
program was created later as another root sibling. Later contributions added
items, provenance, and direct threads beneath those boundaries; none created a
nested program.

The current reducer freezes:

- the parent of every existing program;
- the owner and kind of every existing thread; and
- the program and type of every existing item.

A later builder can create a nested successor but cannot move old items,
threads, contributions, or programs into it. This makes the state sensitive to
the first model-authored topology and discourages later consolidation.

### Assessment of the current hierarchy

| Program | Accepted contributions | Assessment |
| --- | ---: | --- |
| Code-induced converse structure | 1 | Coherent, but its result is also required by both UV results. |
| UV-relaxed functionals | 2 | Coherent, with near-duplicate result/proof lineages on the same objective. |
| Auxiliary-receiver converses | 4 | Coherent umbrella spanning premise interfaces, fixed-pair certification, finite-grid reduction, and a continuum bridge; increasingly broad. |
| Multiletter Marton achievability | 9 | Too broad for one durable local context; mixes foundation repair, structural pruning, finite-family certification, and local geometry. |

All 16 placements use `local-objective`; none uses exceptional
`canonical-objective` or `cross-program` root placement. The audit found no
specific root-placement error.

A topology worth evaluating through ordinary future builder evolution is:

```text
BSSC root
├── Converse / upper-bound methods
│   ├── Code-induced structure
│   ├── UV-relaxed functionals
│   └── Auxiliary-receiver converses
│       └── Receiver-space reduction and continuum bridge
└── Multiletter Marton achievability
    ├── Structural pruning and analytic reductions
    └── Finite-architecture certification and local geometry
```

This is an audit hypothesis, not a manually curated replacement portfolio. The
Math Flow builder remains responsible for forming and revising the authoritative
hierarchy from accepted submissions.

### Why there are more knowledge nodes than submissions

The state is a normalized current knowledge graph rather than an event list.
The 16 accepted submission transactions produced 39 mathematical items plus
program and thread structure. A submission may support a result, a proof, and
an audit tool with different reuse and dependency semantics. Another submission
may add provenance to an existing item. The 9 wholly indeterminate submissions
produce no accepted contribution record or standalone knowledge item.

No global objective establishes that 39 items or 21 threads is the optimal
resolution. Useful future diagnostics include whether two nodes have the same
statement and support, whether a proof or tool is reusable apart from its
result, whether a thread has a distinct decision/work budget, whether a program
remains coherent as work accumulates, and whether alternative decompositions
make counterfactual accounting more stable.

## Current credit execution and accounting

### One holistic refresh, not one run per submission

The active `openrouter-research-credit-v3` runner is a retrospective refresh.
For each exact producer terminal it:

1. replays the complete accepted builder-v5 chain;
2. identifies every immediate program and contribution child;
3. constructs a first-appearance reference context for every child;
4. collects accepted submissions in ledger order;
5. makes one provider request to evaluate every child at one horizon;
6. passes `prior_credit_state=None` to deterministic materialization; and
7. publishes the raw evaluation and newly reduced allocations.

The terminal BSSC run has one provider record with 291,941 prompt tokens and
10,262 completion tokens. Each submission is a child entry inside that response,
not a separate provider run.

### Work is re-estimated before deterministic reduction

Between the preceding terminal at ledger head `9068945…` and the audited
terminal at `9ff49a7…`, raw materialized values changed:

| Submission | Prior direct / obviated / total | Audited direct / obviated / total |
| --- | --- | --- |
| Code-induced balance/entropy no-go (`c70e1829…`) | `0.80 / 0 / 0.80` | `0.85 / 0 / 0.85` |
| Fixed-pair upper-bound certificate (`d2506be7…`) | `0.95 / 0 / 0.95` | `1.00 / 0 / 1.00` |

Their local denominators also changed. Displayed percentage changes therefore
combine fresh model estimates with deterministic normalization and hierarchical
propagation. A fixed raw value could also change percentage when sibling or
residual estimates change.

Every published bundle remains immutable. Under current credit-v3, an updated
assessment is a new bundle at a new exact research terminal. The scheduler
rejects a duplicate published run for the same dependency state.

### Units and presentation

The current policy quantity is expected future work actually spent before a
local objective is resolved. It includes pursuit probability, abandonment,
switching, parallel work, and early stopping, but does not choose hours or
another observable unit.

The reducer stores exact fraction numerators and denominators. The viewer
converts those stored fractions to percentages and rounds for display; it does
not perform substantive work estimation in the browser.

## Dependency and context handling

The earlier phrase **dependency closure** conflated two mechanisms. The updated
work-remaining design should distinguish them:

1. **Impact-subgraph context construction:** map a submission to seed nodes,
   expand through relevant ancestors, descendants, siblings, shared work, and
   semantic dependencies, supply boundary summaries, and permit deterministic
   further expansion.
2. **Counterfactual information consistency:** when withholding a submission,
   classify dependent accepted information as uniquely inherited, independently
   available, or mixed. Remove unique information, retain independent support,
   and assign reconstruction work to mixed cases.

Neither mechanism awards a submission the value of every transitive dependency.
Knowledge nodes and links select and constrain the counterfactual; the credited
subject remains the submission.

The BSSC code/UV relationship illustrates the risk. Both UV results list the
code-induced balance/entropy no-go result as a dependency. A counterfactual that
withholds the code program while simply retaining all UV information may be
inconsistent unless the UV submissions independently establish the removed
premise or are assigned its reconstruction cost.

## Batch-dependent historical references

Current first-appearance logic assigns every contribution in one formation
batch the same pre-build reference. The six contributions in the initial BSSC
v5 batch therefore share an empty pre-batch ledger for their newly formed
programs even though canonical transaction order distinguishes them.

The successor design removes formation batching from credit semantics. If one
hosted run claims several accepted submissions, it constructs a virtual
serialized sequence in canonical `main` first-parent order:

```text
S0 --x1--> S1 --x2--> S2 --x3--> S3
```

Each `x_i` receives its own frozen pre-state, no-access state, with-access state,
and global work difference. Operational provider packaging does not alter the
sequence.

## Evidence-completeness defect

The terminal BSSC `input/submissions.md` is 309,481 bytes including wrappers,
but the evidence collector stops after 300,000 content characters:

- ordinal 18 (`33a5944d…`) ends mid-word and omits remaining artifacts;
- ordinals 19 (`9bb22afe…`), 21 (`90689453…`), 24 (`43fcf08a…`), and 25
  (`9ff49a7c…`) contain metadata followed by an omission marker.

Those submissions retain accepted claims, validity records, item summaries,
dependencies, and transition provenance elsewhere in the request, but not their
complete original bodies. The bundle is replayable yet replayably incomplete
relative to the governed description. The same helper is used for builder
evidence, although this audit directly established truncation only in the
terminal credit input.

The successor should use content-addressed chunked evidence, an explicit
manifest, and fail-closed behavior when a stage requires complete text.

## Successor work-remaining design

### Settled decisions

The following decisions supersede assumptions made during the initial audit:

- The credit subject `x` is one canonical accepted **submission transaction**.
  A submission may affect several programs, work nodes, incidence edges, and
  topology operations, but receives one global value
  `D(x) = W(S_x^-) - W(S_x^+)`. No within-submission item allocation is needed.
- The **Math Flow knowledge-state builder owns the reference portfolio**. The
  community supplies submissions; the builder organizes accepted content into
  programs, subprograms, items, and work contexts. Credit must not maintain a
  competing hierarchy or require a manually curated external portfolio.
- Version one has **no manual review gate**. Invalid provider output is rejected
  by deterministic validation and bounded semantic retry; an exhausted run
  fails without advancing state.
- Version one uses **point estimates only**. Uncertainty intervals, Monte Carlo
  propagation, and confidence discounts are deferred.
- Active credit-bearing submissions must have **strictly positive** `D(x)`.
  Nonpositive output is a failed same-world counterfactual, not a value to clamp.
- Topology is forward-revisable. The builder performs the revision; accounting
  aligns the prior and new portfolio using stable identities and explicit
  lineage, then evaluates the current submission counterfactually on that
  aligned view.
- The accounting unit is a **competent human researcher hour** under a fixed
  conventional tool baseline. It is additive person-time, not wall time. The
  contributor may be an LLM without changing the unit.

### Authoritative topology with separate accounting state

Knowledge and credit remain independently governed projections, but there is
only one portfolio topology. The knowledge state owns node identity, parentage,
content, lifecycle, and lineage. The accounting state stores versioned numeric
annotations and counterfactual provenance against an exact knowledge-state
digest:

- direct residual work `d_v` conditional on activation;
- edge incidence `P_{u|v}`;
- derived reach `R_v`, subtree work `C_v`, and total `W`;
- submission-to-affected-node mappings;
- exact pre-state and topology-alignment provenance; and
- processed submission order and predecessor state digest.

The accounting state must not create an alternative program boundary. A later
consumer can render the two states together because every numeric annotation is
bound to the builder-authored identity or explicit lineage record.

### Same-world evaluation after progressive formation

For accepted submission `x`:

1. Freeze prior knowledge/accounting state and the canonical subject identity.
2. Let the knowledge builder produce the post-submission hierarchy `K_x`.
3. Align prior accounting estimates onto `K_x`, using lineage for moves, splits,
   merges, retirements, and newly explicit nodes.
4. Extract a counterfactual-safe account of facts revealed by `x`.
5. Construct `S_x^-` on the aligned portfolio. The evaluator knows the realized
   world and the safe facts, but the counterfactual community lacks actionable
   access to `x`.
6. Construct `S_x^+` with full access to `x`.
7. Deterministically derive both totals and require
   `D(x) = W(S_x^-) - W(S_x^+) > 0`.
8. Publish the immutable evaluation and commit `S_x^+` as the accounting state
   for the next canonical submission.

This resolves the apparent-work-growth problem. A new subprogram can make the
post-state more explicit, but its latent work belongs in `S_x^-` according to
the probability that the community would have discovered, pursued, rejected,
or completed it. The observed difference between the old displayed portfolio
and the new displayed portfolio is never used as credit.

The evaluator-visible aligned topology is not automatically actor-visible in
the no-access world. Newly revealed names or descriptions may themselves leak
strategy, so the no-access stage receives only the safe representation and
models discovery through incidence probabilities.

### Positive-value invariant

Strict positivity is enforced before publication:

```text
W(S_x^-) > W(S_x^+)
```

The reducer must not replace a nonpositive result with zero or an epsilon. It
should reject the patch with correction context. After bounded retries, no state
transition is published. A submission whose acceptance is later retracted may
be marked `void`; it does not need a synthetic zero or negative work value.

### Topology revision semantics

The next hierarchical builder version needs append-only operations and lineage:

- **move/reparent:** preserve the work identity and carry estimates to the new
  location;
- **split:** identify successors and distribute prior direct work/incidence
  without duplication;
- **merge:** identify predecessors and deduplicate shared work;
- **create:** include the new node in `S^-` with its estimated discovery/work
  incidence instead of treating all of it as work caused by `x`;
- **retire/prune:** permit the node to remain active in `S^-` and become
  inactive or zero-incidence in `S^+`.

A topology revision changes the current comparison coordinate system; by itself
it does not revise historical submission values.

### Unit contract

The root/profile contract should define one competent human researcher hour as:

> One focused person-hour of research by a researcher qualified in the relevant
> field, using the fixed conventional tool baseline named by the profile.

`d_v` is expected person-hours actually incurred conditional on activation.
`P` captures whether that work is incurred. Parallel effort is additive across
people. The baseline should be changed only through a versioned profile so an
hour does not drift with frontier LLM capability.

### No routine prior-credit refresh

Ordinary state evolution does not alter previously published `D(x)`:

| Event | Historical submission value | Live accounting state |
| --- | --- | --- |
| New accepted submission | Unchanged | Advances through its new transition |
| Later change to `d` or `P` | Unchanged | Updates prospectively |
| Deterministic `R/C/W` recomputation | Unchanged | Recomputed from current primitives |
| Move, reparent, split, or merge | Unchanged | Aligned through topology lineage |
| Model, schema, or policy upgrade | Old projection remains historical | New governed projection version |
| Validity reversal, missing evidence, or implementation defect | Exceptional correction or void | Repaired prospectively |

This removes the current common-horizon practice of periodically reestimating
every earlier submission.

### Exceptional prior-credit corrections

A correction is reserved for a defect in the original evaluation basis:

- later validity retraction or material revision;
- incomplete, truncated, or misbound subject evidence;
- arithmetic, reducer, or validator defect; or
- incorrect topology lineage that invalidated the counterfactual.

The correction should be append-only and name the exact evaluation it
supersedes, the reason/evidence, and either a replacement positive evaluation or
`void` status. Original bundles remain replayable. Effective-credit consumers
follow the correction chain rather than selecting an overwritten object.

One policy question remains open. A correction may imply that later accounting
states depended on a premise no longer accepted. The recommended v1 boundary is
to repair the current live state prospectively and flag downstream evaluations
as affected, without automatically replaying and rescoring the complete
historical suffix. Full suffix replay can be added later if exceptional cases
prove common enough to justify its cost and its changed historical meaning.

## Implementation assessment

This is an additive subsystem, not a prompt-only update. A practical design can
reuse `overlay-repository-v1` and the immutable `credit-assignment` envelope,
while introducing a new stateful runner/profile and artifacts. A new run kind or
projection engine is unnecessary for v1 unless another projection must consume
the accounting state as a typed dependency.

### Required artifacts and pure reducer

Add versioned contracts for:

- root/unit contract;
- work-accounting state;
- sparse primitive patch;
- topology alignment;
- counterfactual-safe facts;
- impact-subgraph context; and
- submission work-value evaluation.

The pure reducer should own exact decimal/rational arithmetic, tree and lineage
validation, alias neutrality, nonnegative direct work, bounded probabilities,
top-down reach, bottom-up subtree work, equality
`C_root = sum(R_v * d_v)`, sparse-patch base guards, shared-work deduplication,
incremental invalidation, strict positive `D(x)`, and canonical digests.

Provider output contains primitive edits only. It must not author derived
`R`, `C`, `W`, or `D` fields.

### Judge stages and firewall

The governed pipeline needs:

1. accepted-submission interpretation that reuses validity-v4 outcomes rather
   than readjudicating mathematics;
2. counterfactual-safe fact extraction;
3. no-access sparse-patch estimation;
4. with-access sparse-patch estimation; and
5. optional automated consistency assessment, with no human review gate.

The no-access request builder must enforce the epistemic firewall structurally.
Tests should establish that it cannot contain evidence manifests, chunks,
attached raw evidence files, submission payload fields, or with-access patch
rationales/evidence. Safe-fact prose is a governed semantic judgment and may
overlap submission wording; literal overlap is not a deterministic failure.
Complete evidence should be content-addressed and manifested rather than
silently truncated. A separate semantic exposure ablation should measure
whether increasingly proof-bearing safe-fact summaries bias `W-`.

### Scheduling and publication

Extend/version the credit scheduler to load the latest accounting terminal,
find exact unprocessed accepted submissions, construct canonical serialized
transitions independent of formation batching, reject gaps/duplicates/stale
bases, and keep one writer per problem/projection. Publication must recheck the
exact knowledge dependency, subject prefix, runner/profile digests, and prior
accounting terminal after provider work.

One hosted run may process several submissions serially and publish the final
state atomically. Each submission still retains its own pre-state,
counterfactual pair, evaluation, and intermediate post-state digest.

### Viewer and context

Expose submission-level human-researcher hours, `W^-`, `W^+`, affected program
nodes, and the exact knowledge/accounting state versions. Work-accounting nodes
and knowledge nodes should be visually linked without implying that every
knowledge item has an independent score. Any payout percentage remains a
separate derived presentation layer.

### Additive rollout

1. Normative policy, root contract, schemas, and provider-free reducer/tests.
2. Stateful runner and immutable transition bundles using fake-provider
   fixtures.
3. Topology alignment, local context construction, safe-fact stage, firewall,
   and complete evidence transport.
4. Scheduler, predecessor publication, retry/recovery, and canonical catch-up.
5. CLI/context/viewer support and forward shadow evaluation on one problem.
6. Separate governed projection activation after runtime deployment. Preserve
   credit-v3 and all historical objects unchanged.

## Remaining risks and deferred work

- Calibrate whether human-hour estimates remain comparable across program
  depths, problems, and repeated unpublished trials.
- Establish automatic retry/failure behavior for persistent nonpositive
  counterfactuals without silently losing accepted submissions.
- Test topology alignment through adversarial split/merge/shared-work fixtures.
- Decide whether a validity correction ever triggers full historical suffix
  replay; v1 recommendation is prospective repair only.
- Defer uncertainty intervals, Monte Carlo propagation, simultaneous-batch
  Shapley allocation, resource/capacity scheduling, and critical-path time to
  later versions.
- Keep work value separate from money, governance weight, or a finite payout
  pool.

## Relevant implementation surfaces

- `docs/HIERARCHICAL_RESEARCH_PROTOCOL_V5.md`;
- `docs/PROJECTION_PROTOCOL.md`;
- `protocol/projections/openrouter-research-v3.json`;
- `protocol/projections/openrouter-research-credit-v3.json`;
- `protocol/policies/two-term-hierarchical-research-credit-v1.md`;
- `math_flow/judges.py` (evidence limits);
- `math_flow/research_projection.py` (accepted evidence and builder stages);
- `math_flow/research_credit.py` (history replay and common-horizon refresh);
- `math_flow/research_state.py` (credit effects and exact reduction);
- `math_flow/credit_schedule.py` (predecessor ordering and eligibility);
- `math_flow/projection_dependencies.py` (typed dependency resolution);
- `.github/workflows/project-credit.yml` (hosted execution/publication);
- `math_flow/viewer.py`, `math_flow/credit_context.py`, and
  `viewer/app/creditPresentation.mjs` (consumer presentation).
