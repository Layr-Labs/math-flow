# BSSC joint portfolio serial K1-K3 V1

This inactive experiment is the first complete provider-neutral holdout around
the merged joint topology/live-work V2 foundation. It is deliberately not a
projection: it has no scheduler, publication, catalog, viewer, automatic
continuation, or provider credentials.

The plan resolves the first three accepted BSSC subjects from the exact pinned
validity-v4 source:

1. K1 (`c70e1829...`) creates one durable code-induced-converse work package
   containing the two accepted semantic results represented in the earlier K1
   experiment.
2. K2 (`f236017c...`) creates one independent root-child relaxed-UV package
   containing the general averaged-scalar product theorem and its dependent
   receiver-skew/BSSC specialization. Mathematical dependence on K1 remains a
   result edge, not accounting ancestry.
3. K3 (`14889884...`) must reuse the exact K2 program and both K2 results. It
   appends the independent accepted proof and attestation support, creates no
   program or result, and reassesses the existing UV package's live W+ state.

K2 may represent its new package as already completed, with zero W+ work and
incidence; W- can still estimate positive counterfactual work for that package.
K3 reassessment requires explicit owner refresh and complete current-subject
assessments, not changed numerical values. Unchanged values, including zero on
a completed package, are valid. A topology explanation may state why no change
is needed. Positive D remains a separate counterfactual requirement.

For each subject, the runner freezes and durably checkpoints the validated W+
candidate before safe-fact extraction or W-. The existing credit adapter keeps
safe facts across a failed W- retry and invalidates only the rejected W-
checkpoint. Trusted reduction then requires strictly positive `D = W- - W+`
and allocates D directly to that submission.

The output is one nested content-addressed evidence bundle. It contains the
original immutable validity bundle, canonical submission manifest/chunks,
semantic and local-scope packets, author request/response, complete joint
reduction, frozen W+, counterfactual requests/responses, materialized states,
evaluation, and credit candidate for every step. Loading the bundle verifies
every declared byte and then rebuilds the complete graph. Artifact or manifest
self-digests are never treated as sufficient evidence.

The joint-author runner is the canonical public serial V2 adapter. Its injected
provider uses the neutral call shape
`provider(stage="joint-author", request=..., evidence_files=...)`; the work
provider uses the existing `safe-facts` and `no-access` call shape. Fixture or
capture transports therefore exercise the whole holdout with zero network.

The experiment binds the exact merged joint-author and work-judge specifications.
Every stored author request, response, reduction, and replay envelope is rebuilt
through the public adapter validator. The bundle separately records the sealed
request-core digest, full request-envelope digest, response digest, and replay
result digest; none can be substituted by rewriting a self-digest.

## Manual hosted runner

`hosted-runner-v1.json` and
`.github/workflows/hosted-bssc-joint-portfolio-k1-k3.yml` add one separately
reviewable execution seam. The default command only builds a zero-call plan.
The workflow is manual-only, accepts one exact confirmation phrase, requires a
fresh checkpoint directory, runs only at the current canonical `main`, has
read-only repository permission, and always retains its local evidence. It has
no publication or continuation code.

One fresh successful sample makes nine nominal calls: `joint-author`,
`safe-facts`, and `no-access` for each of K1, K2, and K3. Governed semantic
retries reserve at most 27 calls. Before each network request, the transport
enforces the fixed subject/stage order, request and token ceilings, cumulative
reservations, and an OpenRouter `provider.max_price` filter of $2 per million
prompt tokens and $10 per million completion tokens. Reported usage and cost
must remain inside those reservations or every later call is blocked.

The runner remains unexecuted by admission or merge. A paid sample still needs
a distinct manual dispatch authorization after the hosted code and checks are
reviewed.

## First hosted run and response-order correction

Run `33801731822` at `6c1aca0` stopped during K1 joint authoring after three
attempts, 143,089 reported tokens, and $0.2340176. No W+ checkpoint, W-, credit,
K2/K3 output, publication, or continuation was produced. The model included both
required results exactly once, but their order differed from the reducer's
canonical order; root-first boundaries/assessments and evidence ordering exposed
the same unnecessary restriction. The first attempt additionally put root in
`programChanges`, although its knowledge update belongs to the semantic packet.

The generic joint reducer now normalizes those set-like lists without changing
their entries. The raw response remains intact in the author replay envelope;
the canonical response lives in the separate reduction. Exact response-only
fixtures in `tests/fixtures/joint_portfolio_k1_hosted_ordering.json` cover this
failure without network access. Root program changes are still rejected, and
the inactive author prompt clarifies the distinction. Its new exact digests are
re-pinned in both manifests. Budgets, subjects, accounting rubric, retry limits,
and publication/continuation prohibitions are unchanged. A replacement paid
sample needs a separate explicit authorization.

## Replacement run and completion/reassessment correction

Run `33834473772` at `1ddb8a8` reached K3 after completing K1/K2 authoring and
credit. It used 10 calls and $0.8194814. Its first K2 response was rejected for
creating a completed program; the retry changed the represented residual scope.
K3's final two responses were rejected for explaining unchanged topology rather
than returning a null explanation. Diagnostic replay also exposed a holdout
rule requiring numerical W+ change despite complete reassessment.

Completed creation is now accepted through the terminal-lifecycle adapter,
unchanged-topology explanations are retained, and the numeric-change gate is
removed. Exact response-only fixtures replay all three formerly rejected
responses unchanged; a missing explicit owner update still fails. Full local
fake-provider bundles cover completed W+ with positive W-, and unchanged K3 W+
with a separately authored positive counterfactual difference. No live credit
has been generated for K3 by these tests, and no new sample is dispatched.
