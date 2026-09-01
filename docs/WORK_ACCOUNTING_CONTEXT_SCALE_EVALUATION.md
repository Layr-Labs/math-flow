# Work-accounting V2 context scale evaluation

This document records the provider-free context/capacity probe for the actual
Work Accounting V2 request path. It is additive experimental infrastructure.
It does not activate a projection, publish an artifact, or authorize a model
call.

## What is real and what is estimated

`math_flow.work_accounting_scale` constructs valid research-state v3 knowledge
states and valid baseline, with-access (`W+`), and no-access (`W-`) accounting
states. It then exercises the production implementations of:

- evidence manifestation and counterfactual-safe-fact wrapping;
- state-v3 local impact-subgraph construction;
- V2 with-access and frozen-`W+` no-access stage inputs;
- topology-derived required primitive updates;
- work-accounting patches and trusted reduction; and
- the governed OpenRouter Work Accounting V2 adapter.

The adapter is given an in-memory capture transport. This executes the real
outbound request assembly—system prompt, stage prompt, quoted user data,
base64 evidence, response schema, and provider parameters—but the transport
returns a local synthetic response and never uses the network. The report
therefore records `providerCalls: 0` and `networkUsed: false`.

The report preserves two byte views. `actualTransportEnvelope` is the exact
compact HTTP-payload JSON size, including outer escaping and routing parameters.
`modelInputProxy` sums the exact UTF-8 bytes of the three message contents and
the compact structured-output response format, avoiding the outer HTTP JSON
escaping that a model does not tokenize as prompt text. Budget classification
uses `ceil(modelInputProxy bytes / 4)`; every component also carries a
one-token-per-byte conservative upper bound. These remain size proxies, not
model-tokenizer counts. The nominal input threshold is 128,000 estimated
tokens, matching the existing local-builder scale report. The bound experimental
V2 judge spec separately allows 12,000 output tokens for safe facts and 16,000
for each work-estimation stage. Each case records input-only estimates and input
plus the configured maximum output reservation.

## Matrix and adversarial cases

The committed matrix widens state and hot-branch dimensions together:

| Programs | Intermediate results | Hot branch width | Descendant depth | Evidence bytes |
| ---: | ---: | ---: | ---: | ---: |
| 16 | 24 | 4 | 2 | 4,096 |
| 64 | 64 | 8 | 2 | 4,096 |
| 256 | 128 | 16 | 2 | 4,096 |
| 1,024 | 256 | 32 | 2 | 4,096 |

Every size runs four cases, each through all three V2 stages:

1. **Dependency closure:** the accepted claim depends on an existing result.
   The fixture deterministically traverses the result graph and pre-expands the
   owner-program seeds; the actual V2 impact builder must then retain every
   transitive result identity without truncation. This is intentionally not a
   claim that the production impact builder itself traverses dependencies—it
   currently does not.
2. **Topology revision:** one active program moves under a different parent;
   the deterministic alignment marks it moved and both branches require a new
   conditional-incidence estimate.
3. **Solving zero-out:** one leaf program becomes completed. `W+` must set its
   direct work and incidence to zero, while same-world `W-` may retain positive
   work for the completed-in-the-realized-world node.
4. **Broad local subtree:** the selected non-root program exposes its descendant
   closure through the configured depth; children beyond that depth must be
   excluded from exact nodes and represented by boundary summaries. The default
   width-scaling matrix happens to select terminal immediate children, so a
   separate focused deep-tree fixture requires a nonempty out-of-depth boundary.

Capacity crossings and semantic/adversarial failures are separate report
fields. A case can fit but fail an invariant, or cross the nominal input budget
while all deterministic invariants still pass.

## Provider-free results

All 16 semantic/adversarial cases pass. Exact model-input-proxy ranges from the
digest-bound report are below; ranges span the four scenarios at each size.

| Programs | Baseline accounting bytes | Impact-context bytes | Safe-facts est. tokens | `W+` est. tokens | `W-` est. tokens |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 16 | 8,446 | 5,128–14,405 | 5,168 | 6,758–9,041 | 7,548–9,934 |
| 64 | 30,637 | 8,324–40,250 | 10,715 | 13,104–21,050 | 19,444–27,491 |
| 256 | 115,318 | 9,919–115,595 | 31,886 | 34,673–61,056 | 62,183–88,667 |
| 1,024 | 448,514 | 18,303–376,987 | 115,185 | 120,068–209,703 | 230,878–320,613 |

At 1,024 programs, every `W-` case crosses the nominal 128,000-token input
threshold under the model-input-proxy estimate. The dependency and broad-local
`W+` cases also cross; the local topology and solving `W+` cases remain at
127,967 and 120,068 estimated tokens. Safe facts reaches 460,737 proxy bytes, or
115,185 estimated input tokens; input plus its configured 12,000-token
completion reservation is 127,185. No case at 256 programs crosses the
input-only threshold.

The largest envelopes are:

- dependency closure `W-`: 1,282,452 proxy bytes / 320,613 estimated tokens;
- broad-local-subtree `W-`: 1,221,603 proxy bytes / 305,401 estimated tokens;
- topology-revision `W-`: 955,224 proxy bytes / 238,806 estimated tokens; and
- solving-zero-out `W-`: 923,509 proxy bytes / 230,878 estimated tokens.

The exact values, all component measurements, state bindings, required-update
counts, invariant results, and report digest are in
`protocol/experiments/work-accounting-context-scale-v1/provider-free-report.json`.

## Main finding

The impact context is local, but the V2 request envelope is not asymptotically
local. `_make_request` includes the complete live baseline accounting state in
all three stages. The no-access input additionally embeds the complete frozen
`W+` state. In the 1,024-program solving case, the local impact context is only
18,303 bytes and contains 33 programs, yet the `W-` model-input proxy is 923,509
bytes. The baseline state alone is 448,514 bytes, and the frozen `W+` state is 448,662
bytes. This is why `W-` is the maximum stage in every case.

The probe does not show semantic failure: all topology, dependency, zero-out,
firewall, and locality checks pass. It identifies a deterministic capacity
mechanism. A future protocol revision should preserve exact global state in
trusted storage while giving judges a digest-bound local accounting slice plus
the ancestor/decision-boundary aggregates needed to reduce it. For `W-`, the
frozen `W+` input should use the same bounded representation rather than a
second complete global state. Such a revision needs a replay proof that sparse
local updates reduce to the same globally bound accounting state; this probe is
the regression baseline for that work.

The dependency case also exposes a separate context-engineering boundary:
dependency owner programs must already appear in safe-fact seeds (or be expanded
deterministically by a future host rule). The present impact-context builder
does not discover a transitive result dependency from one direct program seed.

## Additive local-slice follow-up

The inactive provider-free follow-up in
`docs/WORK_ACCOUNTING_LOCAL_SLICE_EXPERIMENT.md` implements the proposed
trusted-global/local-judge seam without changing active V2. Across direct,
dependency, multi-node subtree, topology, completed-node, and broad-scope
fixtures, every cut admitted by the experimental 128-included/256-boundary
limits reproduces the full global `W-`, `W+`, and evaluation objects exactly.
At 1,024 programs, representative local and frozen-`W+` packets are roughly
9%–14% of their corresponding full-state bytes. Dependency-expanded and broad
cuts which exceed the bounds fail before reduction and are never truncated.

This closes the deterministic reducer-equivalence experiment, not the semantic
or activation question. A future versioned judge/request path still needs
model-facing prompt tests, a choice between local and full encodings when local
boundary overhead is larger, explicit production bounds, and a paid shadow
evaluation before activation.

This equivalence is conditional on the deterministic impact cut containing all
patch targets and required updates. The follow-up explicitly rejects a decisive
internal completion if completed descendants have been collapsed, and its
1,024-program decisive-completion and broad cases exceed the boundary bound.
It therefore does not establish general semantic scope sufficiency.

## Reproducing the report

From the repository root:

```bash
PYTHONPATH=. python3 experiments/work_accounting_context_scale_probe.py \
  --input-budget-tokens 128000 \
  --output /tmp/work-accounting-context-scale.json
```

The run is deterministic, takes no provider credentials, and makes no network
request. The focused regression suite is:

```bash
python3 -m unittest tests.test_work_accounting_scale
```
