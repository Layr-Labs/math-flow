# Provider-free protocol evaluation suite

Status: additive local evaluation surface. The suite is not a governed
projection, a provider runner, a publication workflow, or authorization for
semantic execution.

## Purpose

The protocol evaluation substrate has several independent provider-free checks:
builder context scale, Builder V10 route/refine planning, the final BSSC V10
K2-only holdout dry-run, the miniature V10/V2 reducer replay, Work Accounting
V2 context scale, and the exact No-Three shadow preflight. The umbrella suite
runs those checks through one stable command and emits one machine-readable
result:

```bash
python3 -m math_flow protocol-evaluation-suite \
  --mode pr \
  --output-dir /tmp/math-flow-protocol-evaluation-pr
```

`--mode` defaults to `pr`. The output directory must be new or empty. The
runner never reuses or overwrites a prior result directory.

The suite answers a narrow integration question: do the seven frozen,
provider-free evaluation components still agree with their checked artifacts
and safety contracts at this repository revision? A pass does not establish
semantic model quality, hour calibration, shadow-lane readiness, or permission
to spend or publish.

## Frozen manifest and component allowlist

The canonical manifest is
`protocol/experiments/protocol-evaluation-suite-v1/manifest.json`, with suite ID
`protocol-evaluation-suite-v1`. It fixes this ordered seven-component set:

| Component ID | Checked artifact | `pr` mode | `full` mode |
| --- | --- | --- | --- |
| `builder-context-scale` | `protocol/experiments/local-builder-scale-v1/results-provider-free.json` | Verify the locked exact builder V9/V10 report and run a bounded representative scale smoke | Regenerate the complete exact report and require it to match the lock |
| `builder-v10-widening-plan` | `protocol/experiments/local-builder-v10-widening-v1/manifest.json` | Build and verify the complete provider-free route/refine widening plan | Same complete provider-free plan |
| `bssc-v10-k2-dry-run` | `protocol/experiments/bssc-local-builder-v10-v2/manifest.json` | Run the complete final V2 dry-run, restricted to K2 and seed 1729 | Same complete dry-run plan |
| `miniature-v10-v2-replay` | `protocol/experiments/miniature-e2e-v1/scenario-v1.json` | Run the exact eight-submission V10/V2 replay with its hard pass requirement | Same exact replay |
| `work-accounting-context-scale` | `protocol/experiments/work-accounting-context-scale-v1/provider-free-report.json` | Verify the locked exact Work Accounting V2 report and run a bounded representative scale smoke | Regenerate the complete exact report and require it to match the lock |
| `work-accounting-local-slice` | `protocol/experiments/work-accounting-local-slice-v1/provider-free-report.json` | Verify the locked 24-case report and run direct, topology, and decisive-completion root-total smokes | Regenerate the complete report and require its 20 admitted root-total checks and four explicit widening results to match the lock |
| `no-three-v10-v2-preflight` | `protocol/experiments/no-three-v10-v2-shadow-v1/provider-free-preflight.json` | Regenerate and verify the exact four-submission zero-call preflight | Same exact preflight |

Every entry names a built-in component ID plus a repository-relative checked
artifact and its exact digest. The manifest cannot name a Python module,
callable, shell command, provider adapter, workflow, or publication target.
Trusted code maps an allowlisted ID to its provider-free implementation.
Unknown, duplicate, removed, or reordered required components fail validation.

An advanced or test invocation may select another repository-contained
manifest:

```bash
python3 -m math_flow protocol-evaluation-suite \
  --manifest protocol/experiments/protocol-evaluation-suite-v1/manifest.json \
  --mode pr \
  --output-dir /tmp/math-flow-protocol-evaluation-candidate
```

This override is a review surface, not an authority surface. The path must stay
inside the repository and the candidate must pass the same schema, path,
digest, required-component, registry, and safety checks. A manifest alone
cannot make a new implementation executable.

## Mode contract

### Pull-request mode

`pr` is the default bounded integration tier. It always verifies the exact
digest of every locked checked artifact. It then runs bounded scale/reducer
smokes for the three expensive matrices and runs the other four components in
full:

- complete provider-free V10 widening plan;
- final V2 BSSC K2-only dry-run;
- miniature V10/V2 replay with the equivalent of `--require-pass`; and
- exact No-Three V10/V2 preflight regeneration.

The smokes do not replace the committed full reports. Digest verification
still detects drift in any full report; the bounded execution check catches
constructor, reducer, and safety regressions without regenerating the largest
fixtures on every pull request.

### Full mode

`full` runs the same four exact components and exact-regenerates all three
complete scale/reducer reports:

```bash
python3 -m math_flow protocol-evaluation-suite \
  --mode full \
  --output-dir /tmp/math-flow-protocol-evaluation-full
```

The regenerated builder and Work Accounting reports must match the artifacts
locked by the suite manifest. This is the manual, scheduled, or integration
check for changes affecting fixture generation, request construction, scale
telemetry, or report serialization.

Neither mode accepts a partial component selector. The suite is an umbrella
contract: all manifested components run in their fixed order, and the aggregate
passes only when every component passes.

## Zero-authority safety envelope

The suite intentionally has less authority than the standalone experimental
runners it audits:

- it accepts no API key, provider token, account, model, transport, price,
  budget, retry, resume, provider-execution, workflow-dispatch, or publication
  argument;
- provider credentials that happen to exist in the process environment are not
  read and do not enable another path;
- it does not expose or forward standalone flags such as
  `--execute-provider`;
- the BSSC holdout is forced onto its dry-run path;
- the widening component is forced onto provider-free planning;
- the miniature uses only its checked fixture replay and local capture
  transport;
- the No-Three component stops at the provider/transport-free preflight; and
- no component has a projection store, workflow dispatcher, or publisher.

The runner verifies the result of every component before aggregation. A passing
component must report zero provider calls, no network use, and no publication
attempt. The suite repeats those invariants at the aggregate boundary. Any
nonzero or unknown authority signal is a failure, even when the component's
domain-specific checks otherwise pass.

Failure reporting is conservative. Checked-artifact drift detected before a
component is invoked has a known zero-effect record. If an invoked component
raises before returning its complete authority report, its provider-call,
network, and publication fields are `null` (unknown), that uncertainty is
propagated to the aggregate authority record, and the suite fails. The runner
never rewrites an unknown post-invocation effect to zero.

The machine summary makes the authority boundary explicit:

```json
{
  "authority": {
    "credentialInputsAccepted": [],
    "executionFlagsAccepted": [],
    "providerCalls": 0,
    "networkUsed": false,
    "publicationAttempted": false
  }
}
```

This records what the suite accepted and attempted. It is not a claim that a
provider-backed semantic evaluation was performed.

## Output contract

Every completed run writes these canonical top-level reports:

- `summary.json` — machine-readable source of truth; and
- `summary.md` — deterministic human-readable rendering of the same outcome.

`summary.json` has these top-level fields:

| Field | Meaning |
| --- | --- |
| `schemaVersion` | Summary-envelope version |
| `suiteId` | Manifest suite ID |
| `mode` | `pr` or `full` |
| `status` | `passed` or `failed` aggregate status |
| `suiteManifest` | Repository-relative manifest path and actual digest |
| `authority` | Accepted authority inputs and aggregate provider/network/publication counters |
| `componentCount` | Number of manifested components |
| `passedComponents` | Number of components that passed |
| `failedComponents` | Ordered failed IDs; includes `suite-authority-boundary` when aggregate external effects are unknown or nonzero |
| `components` | Ordered component summaries |
| `durationMs` | Measured wall-clock duration |
| `summaryDigest` | `sha256:` plus the repository canonical-JSON digest of the complete summary core with this field omitted |

Each item in `components` contains:

- `id`, `status`, `verification`, and `durationMs`;
- `providerCalls`, `networkUsed`, and `publicationAttempted`;
- `checkedArtifact` with `path`, `expectedDigest`, `actualDigest`, and `bytes`;
- `componentDigest`, binding the complete component record including its
  measured duration.

A successful item also contains `outputDigest`, binding its normalized result,
and `details`. A failed item instead contains a bounded `failure` record and may
omit `outputDigest` because no trusted normalized result exists.

Component working artifacts are temporary and are discarded after their
normalized result is recorded. Only `summary.json` and `summary.md` are stable
outputs. Consumers should use `summary.json`, component IDs, checked-artifact
bindings, and output digests as the interface. `summary.md` is for review and
must not be parsed as the machine contract. Durations are measured run data and
are included in the summary core, so separate successful runs need not have the
same `summaryDigest` even when every deterministic component `outputDigest`
matches.

A component failure makes the aggregate status fail, places its ID in
`failedComponents`, and causes a nonzero command exit. Manifest, path,
allowlist, or authority-envelope violations fail closed rather than falling
back to a smaller suite.

## Additive component registry

The seven current components are a required prefix, not an indefinitely closed
set. A future provider-free component can be appended without changing the
summary envelope. That addition requires one coherent repository change:

1. implement a provider-free component with a normalized result and explicit
   zero-authority report;
2. add its ID to the trusted component registry;
3. append one digest-locked entry to the canonical suite manifest;
4. add positive, drift, path, authority, and mode tests; and
5. document what the new check proves and what it does not prove.

Appending a component changes `componentCount`, the ordered component arrays,
and the suite-manifest digest. It does not by itself change the suite ID,
component envelope, or summary schema. Removing, replacing, or reordering one
of the seven base components is not additive and requires an explicit new suite
contract.

The appended accounting-slice component checks the narrower criterion the
prototype actually establishes: for each admitted digest-bound cut, local
`W-` and `W+` root totals equal the trusted full V2 reducer's totals. Trusted
full V2 still materializes the canonical states and `D`; the component does not
claim independent local reconstruction, semantic scope sufficiency, or that
every exact slice is smaller than the full form.

## Interpretation and related contracts

A suite pass establishes that the pinned provider-free integration substrate
replays at the checked repository revision, that the three scale/reducer reports remain
locked according to the selected mode, and that every component remained
inside the zero-provider/network/publication envelope. It does not supersede
the individual experiment documents:

- `docs/LOCAL_BUILDER_SCALE_EVALUATION.md`
- `docs/RESEARCH_BUILDER_V10_WIDENING_EXPERIMENT.md`
- `docs/LOCAL_RESEARCH_BUILDER_V10.md`
- `docs/MINIATURE_E2E_PROTOCOL_EVALUATION.md`
- `docs/WORK_ACCOUNTING_CONTEXT_SCALE_EVALUATION.md`
- `docs/WORK_ACCOUNTING_LOCAL_SLICE_EXPERIMENT.md`
- `docs/NO_THREE_V10_V2_SHADOW_PLAN.md`
- `docs/PROTOCOL_EVALUATION_ROADMAP.md`

Provider-backed K2, widening, miniature, or No-Three runs remain separate,
explicitly authorized experiments with their own stop budgets. No successful
umbrella-suite result grants that authorization.
