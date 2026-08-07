# MVP architecture and rollout

## Goal

Prove that a GitHub repository can be both a usable collaboration surface and a
replayable source of truth for plural mathematical adjudication.

The MVP is successful when two contributors can submit independent folder-based
contributions through pull requests, those contributions acquire an unambiguous
order when squash-merged, and two judge specifications can project different
views over exactly the same ledger prefix.

## Protocol boundaries

### Canonical transaction layer

The protected default branch is the ledger. A contribution transaction is the
squash commit that first adds exactly one directory at:

```text
problems/<problem-id>/contributions/<contribution-id>/
```

The directory must contain a non-empty `README.md`; everything else is arbitrary.
The source pull request remains the social record for discussion and iteration.
The canonical commit is the protocol record. Sequence is derived from the
first-parent history of the protected branch, not from filenames or counters.

Recommended GitHub settings:

- require pull requests and the `Validate transaction` check;
- allow squash merge only;
- require linear history;
- block force pushes and branch deletion;
- require branches to be current before merge (or add a merge queue later).

The validator checks PR shape, but repository rules are what make the resulting
branch a trustworthy linear ledger.

### Objective attestations

Lean, tests, and other verifiers are checks over a proposed contribution. They do
not write `accepted: true` into canonical content. In a later milestone, durable
attestations will identify the transaction commit, verifier image/digest, inputs,
and structured result. GitHub check runs are the MVP transport for this evidence.

### Pluralistic state layer

A projection is addressed by:

```text
(problem id, ledger head commit, judge specification digest)
```

Judge specifications are versioned JSON files. Projections contain per-
contribution verdicts, a cumulative knowledge state, and credit assignments. The
included `baseline-v1` implementation is intentionally epistemically neutral: it
indexes contributions but leaves verdicts and credit unassessed. It is a stable
fixture for exercising replay and comparison before an AI provider is chosen.
Each result records both the spec digest and the Math Flow runner version.

The `openrouter-math-review-v1` implementation sends the problem and text
artifacts to OpenRouter's chat-completions endpoint with strict structured output.
Its spec pins the model, system prompt, rubric, seed, output limit, and routing
privacy requirements. A completed projection records the request digest, model
resolved by OpenRouter, response ID, and usage. Provider credentials are read only
from `OPENROUTER_API_KEY`, used only in the HTTP authorization header, and never
enter request bodies, specs, projection files, or normal command output.

Generated projections are workflow artifacts or deployment data, not commits on
the canonical branch. This avoids making an interpretation part of the ledger it
interprets.

## MVP phases

### Phase 1 — protocol spine (implemented here)

- repository conventions and sample problem;
- full-tree and PR-diff validation;
- canonical ledger derivation from Git first-parent history;
- judge spec hashing and deterministic baseline projection;
- transaction and projection GitHub workflows;
- tests covering valid and invalid PR shapes and deterministic replay.

### Phase 2 — useful judging (in progress)

- OpenRouter AI judge adapter with structured-output validation — implemented;
- persisted prompt, model identifier, parameters, runner revision, and rubric —
  implemented;
- add a second judge and a projection-diff view;
- record verifier attestations with content and environment digests;
- add adversarial fixtures (incorrect proof, duplicate result, correction,
  conflicting claims) and evaluate judge behavior.

### Phase 3 — contributor experience

- a read-only Vercel web app that renders the ledger and switches between judge
  projections;
- a GitHub App that posts richer check summaries and projection links;
- GitHub identity/PR provenance derived through the API;
- contribution scaffolding and reference helpers.

### Phase 4 — governance and scale

- signed/reproducible judge runs and durable artifact storage;
- explicit policies for judge promotion, appeals, and human overrides;
- merge queue support, caching, incremental projections, and large-artifact
  storage;
- export/replay tooling so third parties can audit the full state.

## Decisions intentionally deferred

- **AI provider and model:** the judge contract should be proven before coupling
  it to an API.
- **Database:** Git remains adequate while usage is repository-native and query
  volume is low. A database can index Git later without becoming authoritative.
- **Credit formula:** the protocol represents a judge's assignment; it should not
  prematurely endorse one social-choice mechanism.
- **Tamper resistance beyond GitHub controls:** signed commits/transparency logs
  can be added if the threat model requires them.

## Known MVP limitations

- Git commit author is only a fallback identity and may not equal the source PR
  author; a GitHub App should resolve immutable GitHub user IDs.
- The PR validator assumes contribution-only PRs. Maintainer problem/protocol PRs
  should run `validate-tree`, not `validate-pr`.
- First-parent ordering is only canonical when branch protections enforce a
  linear, non-rewritable history.
- The worktree projection mode is for local preview. Only commit-addressed
  projections are canonical/replayable protocol outputs.
- The MVP identifies runner releases semantically; production-grade replay should
  additionally pin an executable or container digest.
