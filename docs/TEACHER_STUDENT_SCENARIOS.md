# Provider-free teacher-student scenarios

The teacher-student scenario runner is a replayable experiment harness for
prompt, context, topology, and accounting regressions. It replaces experiment-
specific orchestration with one versioned scenario contract while making no
provider calls and offering no projection-publication path.

Run a scenario with:

```bash
python3 -m math_flow \
  teacher-student-scenario \
  --manifest protocol/experiments/<experiment>/scenario-v1.json \
  --output-dir /tmp/<new-empty-directory>
```

Add `--require-pass` when a hard gold failure should return status 2. A normal
replay still writes and verifies a complete bundle when the student fails its
gold; failed experiments are evidence and should not lose their artifacts.

## Manifest V1

A V1 manifest binds:

- an experiment ID, problem, full frozen ledger head, and description;
- `publicationForbidden: true` and the sole initial execution adapter
  `fixture-replay-v1`;
- one or more named candidate variants and deterministic seeds;
- aggregate hard ceilings for recorded provider calls, stage attempts, prompt
  tokens, completion tokens, total tokens, and cost;
- every frozen input by repository-relative path, media type, and exact SHA-256;
- ordered steps, each containing an arbitrary ordered list of stages;
- every stage's explicit read set and output contract;
- one exact fixture for each `(variant, seed, step, stage)` matrix cell; and
- allowlisted scorer implementations and digest-bound relational gold.

The explicit stage list is intentionally not tied to one builder call. A local
builder can be represented as:

```text
submission K
  route   reads prior capsules/index; writes retrieval plan
  author  reads retrieval plan and exact packet; writes transition/state
  audit   reads transition and global cards; writes placement findings
```

A later work-accounting case can use `safe-facts → W+ → W- → reduction` under
the same contract. Read references are either frozen input IDs or fully
qualified earlier outputs such as `k2.route.plan`; forward or undeclared reads
are rejected before execution. Each fixture repeats that exact ordered read set
as `inputBindings`, including the SHA-256 of every artifact it claims was
visible. The fixture's own manifest-bound digest therefore commits its raw
requests, responses, and outputs to one exact declared input set. Preflight
compares those bindings against the actual variant-and-seed chain before
creating an output directory.

Manifests cannot name Python modules. Stage adapters and scorers are selected
from code-owned allowlists. V1 implements only fixture replay. Most experiments
use the safe declarative `json-relational-v1` scorer; the additive
`miniature-e2e-v1` scorer is a code-owned deterministic replay of the exact
knowledge and work reducers for one frozen benchmark contract. A
provider-backed adapter must be added separately as governed code; changing a
manifest alone can never enable spending or publication.

## Fixture V1

Each fixture contains:

- its exact stage ID and terminal outcome;
- an ordered `inputBindings` array containing exactly the manifest stage's
  declared artifact IDs and their exact content digests;
- every raw request/response record retained by the source experiment;
- a retry/accepted/failed attempt sequence;
- common telemetry for every attempt; and
- inline or path-and-digest-bound stage outputs matching the manifest contract.

The harness and its checked-in fixtures are still unpublished experimental
surfaces, so this closes the V1 contract in place instead of introducing a
legacy-unbound mode that would keep producing evaluation-valid scores. Manifest
shape, fixture attempt/output shape, scorer behavior, and run-envelope versions
remain compatible; an unbound fixture must be migrated once by adding the
bindings and refreshing its digest in the manifest.

Common telemetry includes the logical request components, character and byte
counts where known, prompt/cached/reasoning/completion/total tokens, context and
completion limits, finish reason, output and trailing-whitespace characters,
validation class, retry cause, cost, elapsed time, and stage-specific entity
counts. Aggregates are emitted globally, per stage, and per chain.

`providerCallsExecuted` is always zero for this runner. Replayed fixtures may
record historical or fake provider calls and historical cost. Those values are
reported as `providerCallsRecorded` and `costUsdRecorded` and are checked against
the manifest's hard budgets. This distinction prevents a replay from appearing
to spend money while preserving the cost profile of the experiment it models.

## Relational gold

`json-relational-v1` evaluates assertions against frozen inputs and stage
outputs. Assertions have stable IDs, hard or advisory severity, variant/seed
filters, an actual expression, and a comparison. Supported expressions include:

- artifact lookup with an RFC 6901 JSON pointer;
- `keys`, `values`, `length`, `map`, `filter`, `flatten`, `unique`, and `sort`;
- array `difference`, `intersection`, and `concat`.

Supported comparisons are `equals`, `not-equals`, `contains`, `set-equals`,
`subset-of`, `greater-than`, `less-than`, `truthy`, and `falsy`. This is a data
query language, not executable plugin code.

Relational gold should cover facts that can be checked mechanically. A Markdown
gold can remain a separately frozen authoritative rubric for semantic fidelity,
scope qualifications, and judgments that cannot responsibly be reduced to
string guards. Adding an executable sidecar does not rewrite the original gold.

## Artifact envelope

The output uses the repository's normal digest-indexed `ArtifactBundle`. It
contains:

- the exact manifest and all frozen inputs;
- the exact fixture for every stage;
- raw attempts and separately normalized telemetry;
- every stage output and its read/output digest bindings, plus a dedicated
  `input-binding.json` that joins the fixture digest to the exact read IDs and
  digests for that matrix cell;
- chain scorecards and summaries;
- aggregate telemetry, budget checks, summary, and report.

`verify_bundle` rejects missing, modified, extra, or symlinked files. The
manifest and every external fixture/output are digest-checked before the output
directory is created. Fixture input IDs must exactly equal the stage's declared
reads, and their digests must equal the actual frozen or preceding chain
artifacts. Missing, extra, reordered, future, or stale bindings fail closed
before replay; hard budgets are also checked before replay begins.

## Migrated BSSC holdout

`protocol/experiments/bssc-credit-topology-v3/scenario-v1.json` expresses the
existing two-seed K2/K3 holdout without modifying `gold.md`. Its executable
relational sidecar checks the structural subset of that precommitted rubric.
The replay reproduces:

- two completed chains and four accepted transitions;
- five recorded calls, including one length-truncation retry;
- 141,879 prompt tokens, 37,925 completion tokens, and 179,804 total tokens;
- recorded cost of $0.590397; and
- nine of thirteen structural assertions passing in each seed.

The four failures per seed are the already documented consequence of producing
one combined result instead of the gold's two-result partition: the K2 result
count/create count, the retained K3 result count, and the corresponding K3
content-update count. The replay therefore demonstrates that the common harness
preserves a negative finding rather than laundering it into a passing fixture.

The legacy experiment did not retain full raw requests, and one pathological
response was mostly whitespace. Its replay fixtures preserve the historical
request/response metadata, exact parsed transitions, exact topology summaries,
and exact telemetry, but identify the raw captures as `legacy-summary-only`.
New scenarios should retain complete raw attempts when safe and available.

## Miniature end-to-end candidate

`protocol/experiments/miniature-e2e-v1/scenario-v1.json` is the first complete
provider-free knowledge-plus-work candidate. Its manifest digest-binds the
Builder V10 experiment, work-accounting V2 judge, and V2 policy. Synthetic
oracle choices replace semantic model calls, while trusted code reconstructs
and binds each V10 route context, route plan, and local authoring packet before
the scoped V10/V8/V7 and work-accounting reducers replay eight ordered
submissions from zero. The code-owned scorer checks 102 hard invariants and
emits an aggregate adversarial scorecard. See
`docs/MINIATURE_E2E_PROTOCOL_EVALUATION.md` for the exact cases, hour states,
and limitations.

## Current limitations

- V1 replays frozen outputs; it does not construct new prompts or call models.
- The relational scorer covers JSON structure, not mathematical correctness;
  the miniature scorer covers reducer composition against synthetic oracle
  truth, not model judgment quality.
- Token counts by logical component are unavailable when the source adapter did
  not measure them; aggregate provider counts remain exact.
- Scenario schemas are enforced by executable validation rather than a separate
  JSON Schema file, avoiding two competing enforcement surfaces initially.
- The binding proves which input artifacts a frozen fixture declares and binds
  that declaration to its complete bytes. It cannot prove the historical model
  did not receive an off-protocol side channel; scenarios must still be produced
  by a trusted capture path. Unbound pre-contract fixtures are rejected and
  must be migrated by adding exact bindings and refreshing their manifest
  digests.
- Paid/scheduled runners, provider adapters, adversarial evaluators, and
  publication remain separate future additions.

These limitations are deliberate. The first layer provides a deterministic,
CI-safe substrate on which broader synthetic scale cases and governed paid
adapters can be added without reintroducing bespoke orchestration.
