# BSSC Zero-Origin Knowledge and Work-Accounting Lane V1

Status: active deployment record. The two governed projections are admitted,
the 16-transition knowledge lane has been published and replay-verified, and
the work-accounting workflow is enabled to publish one accepted subject per
state transition.

## Root-contract review boundary

The proposed immutable contract is
`protocol/runtime/inactive-bssc-work-accounting-root-contract-v1.json`. It is
bound to the exact content digest of
`protocol/runtime/inactive-openrouter-research-v4-projection.json`, an inactive
BSSC-only validity-v4/builder-v6 candidate. The candidate is intentionally
outside `protocol/projections/`; admission remains a separate one-file governed
change.

The matching disabled overlay draft is
`protocol/runtime/inactive-openrouter-work-accounting-v1-projection.json`. It
depends on the per-submission builder handoff, so accounting is downstream of
the builder-owned topology rather than a second hierarchy author.

Current review identities:

- root contract: `sha256:062444bd715fc916c9ec2ad2bc7dda5d2a7e01d860f67642efcd86a2380a1ced`;
- bound knowledge projection: `sha256:568a1c71084965fa53dca8041b6429008492b9aa91b35e9363f310458e620fdf`.

The contract fixes five substantive choices for review:

1. The objective is the exact private-message sum-capacity of the canonical
   half-skew BSSC. A rigorous bound improvement is progress but not terminal.
2. The terminal condition requires matching rigorous achievability and converse
   bounds, including all limiting, cardinality, and certification obligations.
3. The accounting unit is one competent-human-researcher hour under a
   conventional-tool baseline frozen at 2026-08-25. Autonomous LLM or agent
   labor is excluded from the reference unit, regardless of who submitted the
   actual contribution.
4. Qualification is local to the work package: graduate mathematical maturity
   plus the relevant information-theory, probability, optimization, or
   computer-assisted-proof expertise, without unpublished solution-specific
   knowledge.
5. Math Flow's bound builder-v6 projection exclusively owns the program/thread
   portfolio. Contributors provide submissions, not hierarchy.

A change to any of these choices changes the contract digest. The projection
digest is likewise part of the contract, so the later admitted projection must
have identical canonical JSON content or the contract must be regenerated and
reviewed.

## Zero-origin execution

The new lane begins with `K0 = empty_research_program_state_v2` and a
deterministic structural `A0`. `K0` contains only the root program and its
unstructured-search thread. `A0` annotates both with zero direct work, gives the
active seed thread incidence one, has no processed submissions, and totals zero
hours.

`A0 = 0` is not an estimate that no work remains. It is the algebraic origin
before any accepted submission has supplied a builder-owned reference portfolio
on which the counterfactual estimator can operate. The first accepted subject
produces `K1`; the no-access and with-access roles then supply the first actual
primitive work estimates on that post-topology world, and only the with-access
state becomes the next live state.

The exact sequence is:

```text
K0, A0
  -> accepted x1: K1, R1/C1, D1, A1
  -> accepted x2: K2, R2/C2, D2, A2
  ...
  -> accepted x16: K16, R16/C16, D16, A16
```

All 25 canonical submissions are traversed in first-parent order. Accepted
ledger ordinals 3, 4, 5, 9, 10, 11, 12, 14, 15, 16, 17, 18, 19, 21, 24, and 25
each receive exactly one builder-v6 transition and one work evaluation. The nine
excluded submissions receive neither and do not advance either state.

`math_flow.bssc_zero_lane` constructs and validates this readiness model from
the pinned canonical ledger and historical validity dispositions. Historical
builder-v5 poststates, batches, and topology are explicitly not reused. The
provider-free report establishes the zero origin and the exact 16-subject order;
it cannot establish `D(x) > 0` before real provider responses exist.

The same module reconstructs all 16 exact accepted inputs from the immutable
validity-v4 judgment and dependency-packet artifacts plus each submission's own
canonical transaction tree. The test harness drives those real subject,
accepted-claim, dependency, assessment, and evidence bindings through 16
sequential builder/work transitions using deterministic fixture providers. This
proves orchestration and binding only; fixture topology and hour estimates are
not BSSC research judgments.

## Remaining provider work

Activation requires 16 builder-v6 proposals and 16 three-stage work evaluations
(`safe-facts`, `no-access`, and `with-access`). The reducer must enforce one
strictly positive `D(x) = R(x) - C(x)` per accepted submission without clamping.
Operational batching may package calls but cannot change subject boundaries or
predecessor order.

Running the exact inputs also exposed two byte-firewall false positives:
accepted claim keys and the public root objective can legitimately occur in a
submission. The guard now scans only provider-authored fact conditions and
assumptions for verbatim evidence spans, while structural validation separately
prohibits evidence manifests, chunks, and submission payload fields from the
no-access request. This preserves the epistemic boundary without rejecting the
mandatory identity and public-policy bindings.

## Prior-credit corrections

Starting from zero removes the special correction/migration question for the
first 12 accepted submissions: they receive ordinary first-pass evaluations in
the new lane. Later knowledge or topology revisions update the live primitive
state prospectively through the new submission's with-access branch; they do
not re-estimate earlier immutable `D(x)` values.

Exceptional correction remains append-only and is reserved for an invalid
original basis such as a validity reversal, incomplete evidence, reducer defect,
or invalid topology lineage. The current V1 policy flags affected later history
without silently replaying it. A future policy must explicitly choose whether a
correction repairs only the live state or creates a distinct suffix-replay lane.
