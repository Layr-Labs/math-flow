# Small real-problem V10/V2 shadow benchmark

## Recommendation

Use `no-three-in-line-77` for the next ecological-validity shadow benchmark.
It is the only repository problem in the intended small range with three to
eight exact accepted canonical submissions: four of its ten canonical
contributions have `valid` validity-v4 assessments. It is active, its evidence
is varied, and one historical knowledge/credit pair already demonstrates that
downstream accounting consumes nontrivial hierarchy.

The provider-free contract is pinned at
`protocol/experiments/no-three-v10-v2-shadow-v1/manifest.json`. It authorizes no
provider call and no publication. A deterministic preflight now verifies every
input and emits the exact serial stage/budget plan, but deliberately contains
no authored V10 transition, V2 work estimate, or semantic request digest.

## Repository inventory

Counts below use the most recent exact validity generation available for each
problem (`validity-v4` for BSSC and No-Three-in-Line, otherwise `validity-v2`).
The archive flag comes from `protocol/problem-registry.json`.

| Rank | Problem | Canonical contributions | Exact accepted | Other outcomes | Archived | Existing knowledge / credit evidence | Assessment |
| ---: | --- | ---: | ---: | --- | --- | --- | --- |
| 1 | `no-three-in-line-77` | 10 | 4 | 6 indeterminate | No | V5 state: 4 programs, 11 threads, 9 items, 4 contributions; historical credit evaluates all 4 programs | Best fit |
| 2 | `triangle-midpoints` | 3 | 2 | 1 indeterminate | Yes | Legacy state: 1 program, 1 thread, 5 items, 2 contributions; historical credit exists | Closest fallback, but below target and archived |
| 3 | `maximal-determinant-23` | 3 | 1 | 1 invalid, 1 indeterminate | Yes | Legacy state: 1 program, 2 threads, 4 items, 1 contribution; historical credit exists | Too little accepted history |
| 4 | `schur-number-6` | 3 | 1 | 2 indeterminate | Yes | Legacy state: 1 program, 1 thread, 5 items, 1 contribution; historical credit exists | Too little accepted history and unusually heavy certificate evidence |
| — | `bssc-sum-capacity` | 25 | 16 | 9 indeterminate | No | Rich V10/V2 development history | Valuable wide benchmark, not small |
| — | `metric-universality-price` | 1 | 1 | — | Yes | Historical projection evidence | Too small |
| — | `multiway-cut-ckr-gap` | 1 | 1 | — | Yes | Historical projection evidence | Too small |
| — | `replicable-pac-sample-complexity` | 1 | 0 | 1 invalid | Yes | Historical projection evidence | No eligible subject |
| — | `zeta-critical-line-density` | 0 | 0 | — | Yes | No contribution projection | No eligible subject |

The three archived problems with three repository contributions are not really
three-submission accepted histories. Their exact validity-v2 outcomes are:

- Triangle: two valid, one indeterminate.
- Maximal determinant: one valid, one invalid, one indeterminate.
- Schur: one valid, two indeterminate.

Promoting an indeterminate subject into a benchmark would fabricate admission,
so the experiment does not do that.

## Why No-Three-in-Line is ecologically useful

The four accepted transactions, in canonical accepted order, are:

1. ledger position 4, `29ccbd3…`: a self-contained finite-rotation
   classification proof;
2. ledger position 5, `0ffe9a1…`: an objective verification of the 152-point
   record, with an objective attestation;
3. ledger position 9, `87f78eb…`: a theorem giving an exact encoding for the
   `rct4` subclass; and
4. ledger position 10, `17928a9…`: an attested computation establishing local
   rigidity around eight record embeddings.

This is a compact mixture of proof, exact verification, method/encoding, and a
larger computational artifact. The accepted evidence bundles range from about
4 KB to 65 KB. All four exact validity artifacts include accepted summaries and
scope qualifications, so V10 can be tested with real semantic guidance rather
than a hand-authored teacher fixture.

The historical V5 state provides a useful observational reference:

```text
root
├── certified-configurations
└── rotational-symmetry
    └── rotational-symmetry/rct4
```

That state contains four result items plus five separately typed proof, method,
computation, and tool items. V10 should test the intended simplification by
packaging those support forms inside durable intermediate results. The old
shape is not hard gold: V10 should independently apply the author-blind
activation/stopping-condition test, particularly to whether `rct4` remains a
nested work package.

The historical hierarchical credit run is also useful evidence of machine
consumption. It evaluates the root and all three non-root programs and assigns
separate effects to the certified-configuration and rotational programs. It is
not a V2 numerical oracle. That run used a different judge and accounting
construction, so its values cannot be compared directly with competent-human
researcher-hour `W-`, `W+`, or `D` estimates.

## Exact provider-free binding

The manifest pins:

- a review-draft, publication-forbidden experimental V10 knowledge-projection
  descriptor and a problem-specific accounting root contract;
- the canonical problem statement and provider-free preflight implementation;
- the final Builder V10 experiment spec and Work Accounting V2 spec/policy by
  local SHA-256 digest;
- projection commit `ed4f8bc198ce0a29f13609042712440bcff44ba5`;
- the exact problem run index, catalog, problem ledger head, and problem ledger
  digest;
- each subject transaction, ledger position, contribution tree object,
  path/content evidence digest, claim key, validity run, judgment ID, judgment
  artifact, dependency packet, report, and objective attestation runs; and
- the historical V5 knowledge and credit states as explicitly observational
  baselines.

`sha256-path-content-v1` sorts every file path relative to one contribution,
then hashes the byte sequence
`path + NUL + lowercase-file-sha256 + newline` for every file. This supplements
the immutable Git tree object with a provider-free check that current canonical
evidence bytes have not drifted.

The root contract uses competent-human-researcher hours under conventional
non-autonomous tools frozen at 2026-09-01. Its objective preserves the
canonical disjunction: determine `D(77)` or improve either side of the certified
interval. Its terminal condition is intentionally narrower and unambiguous:
the root completes only when accepted evidence makes the lower and upper bounds
coincide at the exact value. A one-sided bound improvement advances the program
but is not terminal.

There are no semantic fixtures or expected semantic output digests. The
current adapter is a provider-free serial preflight with a hard budget of zero
calls, zero tokens, and zero cost. It is implemented without a provider,
transport, credential, checkpoint, projection store, or publication parameter.
Run it with:

```bash
python3 -m math_flow --root . no-three-shadow-preflight \
  --output /tmp/no-three-v10-v2-preflight.json
```

The checked replay is
`protocol/experiments/no-three-v10-v2-shadow-v1/provider-free-preflight.json`.
It verifies the pinned projection commit and all manifested artifacts, derives
the exact accepted-claim and accepted-claim-reference identities, reconstructs
all four submission evidence manifests, validates the from-zero knowledge and
accounting origins, and emits 36 strictly serial steps. Of those, 24 are
future provider stages and 12 are trusted local reduction/freeze steps.
The advisory maximum is 72 attempts and 840,000 reserved completion tokens.
Every current authorization counter remains zero.

The preflight does not fabricate semantic request digests. After the first
authoring boundary, each V10/V2 request depends on a trusted predecessor `K` or
`W` state that does not exist before the prior semantic stage succeeds. The
plan therefore binds the exact inputs, dependency order, per-stage limits, and
aggregate caps while leaving request materialization deferred.

## Future shadow execution order

After the blockers below are resolved and a separate provider authorization is
given, replay the four accepted subjects from zero. For each subject `x_i`:

1. derive the accepted claim only from its pinned validity-v4 assessment and
   load its complete digest-verified canonical evidence;
2. run V10 route, route-refine, and organize against `K_(i-1)`, then apply the
   trusted state-v3 reducer to obtain the post-submission topology `K_i`;
3. align the old live accounting state onto `K_i` without inventing work;
4. run V2 safe-facts and with-access, validate and freeze `W+_i`;
5. run no-access from the same old live base, with the defined epistemic
   boundary, to obtain audit-only `W-_i`;
6. have trusted code derive `D_i = W-_i - W+_i`, require `D_i > 0`, and commit
   only `W+_i`; and
7. stop before the next subject on any protocol concern.

The future advisory envelope reserves 24 nominal calls and at most 72 calls:
four subjects, three V10 provider stages and three V2 provider stages, with no
more than three governed attempts per stage. The exact completion-token
reservation is 840,000 tokens from the pinned per-stage maxima. These are
planning caps, not execution authority. A request-side verified price bound is
required because post-response cost reporting cannot itself prevent a
single-call overshoot.

## Scoring

Hard checks should cover exact subject selection and order, every immutable
binding, V10 reducer replay, hidden-state preservation, topology alignment,
the frozen `W+` boundary, same-base `W-`, positive `D`, advancement of only
`W+`, complete request/context/token/cost/retry telemetry, and zero publication
effects.

Relational and adversarial review should ask:

- whether certified-configuration/local-rigidity work and rotational-symmetry
  work remain independently estimable root-level packages;
- whether `rct4` placement is justified by an independent activation or
  stopping condition rather than copied from V5;
- whether proof, method, computation, tool, artifacts, and attestations remain
  support for aggregate intermediate results rather than becoming extra
  entities;
- which nodes each contribution changes in `W-` and `W+`, and why;
- whether the fourth contribution's larger evidence packet causes unexpected
  routing or context growth; and
- whether any retry signals a protocol defect rather than ordinary provider
  variance.

The four accepted judgments all declare an empty
`requiredDependencyTransactionIds` set. Some submissions declare historical
references, but the validity assessments do not require those references to
establish the accepted claims. This real benchmark therefore does not exercise
mandatory dependency closure and must remain paired with the synthetic
dependency cases.

## Remaining blockers

The candidate is preflight-ready but not semantic-execution-ready:

1. The problem-specific root contract is a schema-valid review draft, not an
   approved semantic contract. A human must explicitly review its objective,
   exact-solution terminal condition, researcher qualification, and fixed tool
   baseline.
2. A later publication-forbidden semantic runner must add governed provider
   checkpoints, materialize each request only after its exact trusted
   predecessor exists, run the unchanged V10 and V2 reducers, and write only
   local experiment artifacts. The current preflight has no such provider
   boundary by design.
3. A request-side verified price bound remains required; reported post-response
   cost alone cannot prevent a single-call overshoot.
4. Provider execution needs a separate authorization after contract review and
   semantic-runner review.

Until those conditions are met, the manifest and runner remain auditable local
plans and cannot spend or publish.
