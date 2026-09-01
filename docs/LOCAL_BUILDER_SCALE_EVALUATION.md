# Local-builder context scale evaluation

This document records the provider-free scale and adversarial harness for a
fractal knowledge builder. It is experimental infrastructure, not a production
projection change and not authorization to call a provider.

## What the probe measures

`math_flow.builder_scale` generates valid research-program state v3 fixtures
while varying these dimensions independently:

- program count, maximum tree depth, and maximum width;
- intermediate-result count and support bytes;
- submissions represented by each result;
- cumulative `sourceTransactionIds`, `claimRefs`, and `judgmentIds` on results;
- cumulative source provenance on the root and every affected ancestor;
- dependency-closure depth and width; and
- current-submission evidence bytes.

Every generated state passes the production
`validate_research_program_state_v3` validator. The fixtures also precommit gold
for six teacher/student challenges:

1. transitive dependency-closure retrieval;
2. a semantically duplicated result in a distant, incomparable program;
3. one result that directly affects two incomparable programs;
4. an independent new route that belongs as a root sibling;
5. an exact result that must be found despite a misleading program capsule; and
6. an atomic topology revision with one retired predecessor and two reciprocal
   successors.

The adversarial scorer consumes generic route-plan fields. It is therefore
usable by the local-builder candidate without binding this harness to a
particular V10 schema.

## Three context strategies

The default scale matrix compares:

- **V9 all-core:** the actual `build_research_builder_v9_context` result. Every
  program and result semantic core is present, while support is limited to the
  declared dependency closure.
- **Bounded semantic:** a two-call model. The route call receives root and a
  bounded number of child capsules. Trusted host-side search returns bounded
  cards. The author call receives selected paths, dependency closure, boundary
  cards, and semantic records. Cumulative provenance arrays are replaced by
  counts plus exact record digests.
- **Bounded exact provenance:** the same bounded selection, but every selected
  node retains its complete provenance arrays.

The trusted search catalog is measured as host-side state, not included in any
model request. No global catalog is smuggled into the route prompt.

The distinction between the two bounded strategies is important. Merely
selecting local nodes does not bound prompt growth if the root and ancestors
still repeat every historical source ID. The eventual author protocol should
let trusted code preserve and extend those arrays, just as V9 already preserves
hidden support and derives some provenance fields. The model needs semantic
content, stable digests, and provenance counts; it ordinarily does not need
thousands of opaque transaction or judgment identifiers.

## Provider-free measurements

The committed report uses a nominal 128,000-token input budget. Token counts are
`ceil(compact UTF-8 bytes / 4)`, not model-tokenizer or provider counts. They are
suitable for growth comparisons and candidate budget crossings only. Live runs
must retain provider-reported usage alongside component bytes.

| Programs | Results | Submissions | V9 max | Bounded semantic max | Bounded exact max | V9 provenance share |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 16 | 24 | 24 | 7,206 | 3,894 | 4,620 | 34.1% |
| 64 | 128 | 512 | 71,026 | 5,932 | 22,946 | 72.2% |
| 256 | 512 | 4,096 | 500,905 | 8,773 | 143,498 | 84.8% |
| 1,024 | 2,048 | 32,768 | 4,018,994 | 12,502 | 1,130,723 | 92.5% |

At the nominal budget, V9 crosses between the second and third cases. The
bounded exact-provenance strategy also crosses in the third case. The bounded
semantic strategy remains below 13,000 estimated tokens in the largest case,
with a 99.7% maximum-stage reduction relative to V9.

These cases scale several dimensions together and are not an estimate of a
particular problem's date of failure. They demonstrate the mechanism:
cumulative provenance, especially the root source array, can dominate before
the mathematical semantic state itself is unusually large.

## Failure classes

`classify_capacity_outcome` keeps three observations separate:

- `hard-input-exhaustion`: the prompt exceeds the configured input budget;
- `hard-output-exhaustion`: the completion reaches its limit, including
  trailing-whitespace or repeated-character pathology; and
- `soft-semantic-degradation`: the request fits but precommitted retrieval,
  placement, dependency, or topology checks fail.

Provider-free input measurements cannot diagnose a live output failure, and a
successful fit cannot establish semantic quality. Beginning, middle, and end
position probes expose identical hidden gold so paid teacher/student runs can
measure soft degradation without conflating it with scale or sampling changes.

## Running the matrix

From the repository root:

```bash
python3 -m experiments.local_builder_scale_probe \
  --input-budget-tokens 128000 \
  --output /tmp/local-builder-scale-report.json
```

The output includes component bytes and estimates for every stage, budget
thresholds at 50%, 70%, 85%, 95%, and 100%, V9/local ratios, provenance
occurrences, adversarial scorer self-checks, and semantic-probe sizes. It always
reports `providerCalls: 0`.

## Binding an actual local builder

The strategy adapter is deliberately small:

```text
strategy(fixture, challenge_name) -> {
  stage_name: {component_name: serializable_value}
}
```

An integration test can therefore wrap the actual route-context and authoring-
packet builders without copying their schemas into this module. The next
integration should assert:

`make_v10_context_strategy(route_builder, authoring_packet_builder)` already
binds the candidate's exact raw route-plan fields and exposes both provider
stages to component telemetry. It takes the functions as arguments so this
provider-free experiment remains replayable without importing or activating a
particular builder version.

- dependency closure is never truncated;
- host-side global search can recover distant duplicates independently of tree
  routing;
- root siblings and cross-program work remain expressible;
- topology revisions load every affected branch before authoring;
- hidden provenance is digest-bound and extended only by trusted code; and
- a budget breach fails with a component report rather than truncating context.
