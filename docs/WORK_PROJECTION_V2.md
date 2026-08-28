# Per-submission work projection V2

V2 is an additive, provider-neutral A-first foundation. It is implemented and
replayable, but no projection file activates it. Active
`openrouter-work-accounting-v1` bundles retain their original request schema,
stage order, prompts, and loader.

## Order and state authority

For one adjacent accepted submission `x`, V2 performs:

1. `safe-facts` over the complete verified submission;
2. `with-access`, producing a sparse patch from the old live state;
3. trusted materialization and semantic validation of the candidate live `W+`;
4. `no-access`, producing a separate sparse `W-` patch from the same old live
   state while receiving the frozen numeric `W+` state; and
5. trusted calculation of `D(x) = W- - W+`, followed by commitment of only
   `W+`.

The persistable frozen candidate binds the exact transition, safe-fact request
and response, impact context, with-access request and response, primitive patch,
and reducer-authored state. Reuse reproduces the candidate from its patch and
old base. Reuse also requires the caller-expected descendant depth; that depth
and the V2 output profile are part of the retry-stable CAS key. A stale,
tampered, wrong-predecessor, differently processed, or wrong-depth state is
rejected.

The no-access input contains the numeric `W+` state and its exact candidate/state
digests. It does not contain the `W+` patch, rationales, evidence references,
submission evidence manifest, raw chunks, raw claims, or item-bearing topology.
The evaluator can use the realized numeric state, while the simulated actors
remain unable to use `x` before independent discovery.

## Retry isolation

V2 checkpoint identity is stable across automatic attempts for the same exact
transition. Before requesting `W-`, the pipeline stores the fully validated
candidate in immutable CAS under `automaticRetryKey`; this survives a new claim
digest and a fresh hosted scratch directory. Safe-fact and with-access responses
are reusable only after the candidate is semantically reproduced. A no-access
response that fails patch validation or produces nonpositive `D(x)` is removed
from the local checkpoint; subsequent attempts load and revalidate the CAS
candidate, re-estimate only `W-`, and preserve the same `W+` bytes.

The runner also exposes `prepare_frozen_with_access_candidate_v2` so an
orchestrator can persist the validated `W+` boundary before requesting `W-`.

## Compatibility and activation

V2 reuses the V1 root contract, state schema, primitive patch schema, work-value
schema, and deterministic reducer. It adds:

- `math-flow/work-accounting-transition-v2`;
- request and bundle schema V2;
- a no-access stage-input V2;
- a frozen-with-access candidate schema;
- `openrouter-work-accounting-v2`; and
- a dedicated V2 policy.

The repository includes a sealed BSSC V2 hosted-runtime candidate, an active-form
runtime projection candidate, and a workflow initially shipped as an ignored
`.yml.inactive` template. These files are activation inputs, not admission or
deployment by themselves. Admission still requires a separately governed,
byte-identical copy in `protocol/projections/`; workflow activation still
requires the explicit template rename. The shared pipeline has dormant
profile-conditional V2 dispatch and CAS retry isolation; its V1 provider,
request order, claim-scoped checkpoints, bundle format, projection, and semantic
retry behavior remain unchanged.

The pipeline selects an expected profile from trusted lane configuration, binds
its version to the versioned projection ID, cross-checks the provider, and
requires restored and newly produced bundles to use that exact profile. Both
judge loading and overlay governance verify the V2 policy digest against the
actual policy bytes rather than accepting a declared digest alone.

The hosted runner selects both the V2 provider class and expected V2 output
profile only from the explicitly loaded, content-sealed V2 config. Safe-fact and
W+ semantic failures retry within the governed provider invocation. W- receives
only patch-local and absolute-state retry feedback; the combined positive-delta
check remains an outer `W-`-only retry against the immutable CAS-frozen W+, so no
target-D diagnostic is sent to the no-access judge.
