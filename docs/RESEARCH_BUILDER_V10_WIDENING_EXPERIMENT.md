# Builder V10 route/refine widening experiment

## Purpose and non-goals

This is an unpublished, publication-forbidden experiment for the local/fractal
Builder V10 routing foundation. It asks a teacher/student question: given a
valid increasingly large research-program state and an accepted validity
summary, can the governed router find the bounded local read/write scope that a
later author would need?

The experiment invokes only `route` and `route-refine`. It constructs the final
trusted authoring packet so its closure and limits can be checked, but it never
invokes `organize`, applies a transition, changes a knowledge state, writes a
projection, dispatches a workflow, or publishes an artifact. It therefore does
not test prose authoring, topology reduction, or end-to-end credit assignment.

The default command is provider-free. Provider execution requires both an
explicit command flag and the exact authorization value named by the manifest.
No provider call was made while implementing or testing this experiment.

## Authoritative contract

The manifest is
`protocol/experiments/local-builder-v10-widening-v1/manifest.json`. It binds the
exact V10 judge file by raw-file SHA-256, including the corrected author-blind,
same-world/no-access work-package policy. It is fail-closed if the judge file,
model, reasoning effort, completion limit, publication prohibition, cases, or
budget relationships change.

The widening series contains valid synthetic state-v3 portfolios with 16, 64,
256, and 1,024 programs. It exercises dependency closure, topology-independent
duplicate discovery, and a misleading local capsule. Separate adversarial cases
cover cross-program placement, an independent root sibling, and an atomic
topology revision. All normal cases place a representative routing clue in the
accepted `validitySummary`, which is part of both model-visible routing stages.

A separate 64-step hot-branch case holds program/result topology fixed while
63 later accepted contributions accumulate on one declared-dependency result.
The final state is reducer-valid and the selected result has exactly 64 source
transactions, claim references, and judgments. This isolates cumulative local
history from global portfolio width; it is a final-checkpoint reconstruction,
not 64 provider calls or 64 serialized intermediate snapshots.

One explicit limitation case places the only useful routing clue in raw
submission evidence. Builder V10 intentionally withholds that evidence from
both routing stages. The hard assertion for that case is that the clue is
present in the evidence and absent from every route request. Failure to recover
the hidden target is reported as the expected limitation rather than disguised
as a routing regression. Accidental recovery is reported separately.

## Two-stage protocol under test

For each case, trusted code derives the compact root/dependency route context
from the complete canonical state. The governed route stage may inspect IDs,
request deterministic lexical searches, declare existing write IDs, and reserve
new stable IDs. Trusted code binds that plan to the state and context digests,
performs deterministic search, loads mandatory declared-dependency closure, and
constructs a bounded discovery packet.

The route-refine stage sees that packet and returns a complete final route plan.
Trusted code then constructs (but does not send to an author) the exact local
authoring packet. Scoring uses its final `readSet` and `writeScope`, not an
untrusted model self-report. The test checks required programs, results, and
writes. The root-sibling case also requires root context and a reserved new
program ID. Since parent placement is authored only in the later organize
stage, route/refine can test the root-sibling reservation but cannot by itself
prove the eventual new program's parent.

## Telemetry and hard stops

Every actual transport call records the complete request and response plus
their digests and exact serialized character/byte measurements. The report also
measures the quoted route input and the system prompt, stage prompt, user
envelope, route input, and response-format components separately. Provider
telemetry records prompt, completion, reasoning, and total tokens, model,
finish reason, output size, cost, cumulative usage, and cumulative reservations.
The governed adapter's accepted invocation records and every retry-journal
snapshot are retained alongside transport attempts.

Each discovery and final authoring packet also gets a separate entity-duplication
report. It counts semantic-table, capsule, route-context, and search-card
appearances by stable entity ID; reports total versus unique appearances,
duplicate occurrence fraction, bytes in appearances after the first, and the
largest repeated entities with their exact packet paths. This makes local packet
growth caused by repeated table/capsule representations visible separately from
growth in the complete hidden state.

Before a call reaches transport, the experiment enforces all of these manifest
ceilings:

- actual provider-call count;
- compact request bytes;
- estimated prompt tokens (`ceil(request bytes / 4)`);
- conservative prompt tokens (one token per request byte plus an overhead
  reservation);
- completion tokens requested by the stage;
- cumulative conservative token reservations; and
- cumulative per-call cost reservations.

After a response, it requires internally consistent provider-reported token and
cost telemetry and enforces reported token, per-call cost, and total-cost caps.
Any transport uncertainty or missing/inconsistent usage telemetry permanently
blocks later calls. Reservations are never released after a validation failure,
so governed retries consume their own full call/token/cost allowance.

A client cannot prevent a provider from charging more than an asserted
per-request cost reservation after accepting the request. Such a violation is
therefore detected after that response and blocks every later call. The total
reservation still prevents the experiment from deliberately initiating more
calls than the approved maximum exposure.

## Running safely

Provider-free planning is the default and refuses to reuse an existing output
directory:

```sh
python3 -m experiments.research_builder_v10_widening \
  --output-dir /tmp/local-builder-v10-widening-plan
```

That command builds every valid synthetic state and records route-context
growth with `providerCalls: 0`.

Provider execution is intentionally double-gated and should only be used after
separate authorization:

```sh
MATH_FLOW_V10_WIDENING_AUTHORIZATION=local-builder-v10-widening-v1-provider-run \
python3 -m experiments.research_builder_v10_widening \
  --execute-provider \
  --output-dir /tmp/local-builder-v10-widening-provider-run
```

Even in that mode, the runner has no publication path and stops on the first
hard budget, protocol, or semantic failure.

## Interpretation

A pass shows that, for the tested teacher/student fixtures, accepted semantic
clues plus deterministic search/refinement can recover a bounded trusted local
packet as the full state widens. It does not demonstrate repeated-judge
variance, general mathematical understanding, correct authoring, or correct
credit allocation. The evidence-only case is especially important: it makes
the router's epistemic boundary empirical and prevents a test fixture from
quietly granting routing information that the production stage would never see.
