# Miniature end-to-end protocol evaluation V1

This unpublished, provider-free benchmark is the first complete candidate
contract joining the inactive local Builder V10 experiment to the A-first Work
Accounting V2 judge and policy already active for the separate BSSC V2 lane.
The V10/V2 composition itself is inactive. It processes eight synthetic
accepted submissions from an empty knowledge and accounting lane, exercises
the real state-v3 knowledge reducer and hierarchical work reducer, and
publishes nothing.

The scenario manifest freezes these intended candidate inputs by path and
SHA-256 digest:

- `protocol/judges/openrouter-hierarchical-research-builder-v10-experiment.json`;
- `protocol/judges/openrouter-work-accounting-v2.json`; and
- `protocol/policies/hierarchical-work-remaining-accounting-v2.md`.

The provider-free fixture substitutes precommitted synthetic transitions for
V10's semantic route, route-refine, and organize judgments, and precommitted
sparse primitive patches for V2's semantic `W+` and `W-` judgments. It does not
pretend to test model quality. For every accepted submission, trusted code now
builds the exact V10 catalog and route context, binds a minimal route plan,
derives the local authoring packet, and applies the precommitted transition
through `apply_research_builder_v10_transition`. The replay therefore exercises
V10's write scope, readable-reference boundary, stale-packet rejection, hidden
state preservation, exact evidence binding, V8 affected-ancestor refresh, and
the shared V7 state/topology reducer. It also preserves with-access-first
materialization and freeze, same-base no-access reduction, strictly positive
`D = W- - W+`, and advancement of only `W+`.

Each transcript step stores a compact `knowledgeBuilderReplay` record: zero
provider calls, exact synthetic evidence-file refs, the fully bound route plan,
the route-context and authoring-packet digests, the derived read and write
scopes, and the expanded-transition digest. The scorer reconstructs the full
route context and authoring packet from the preceding state and requires every
stored binding to match before applying the transition. This binds the exact
V10 mechanics without duplicating the much larger deterministic packet in the
fixture.

## Reference history

All work is measured in competent-human-researcher hours under one immutable
root contract.

| Submission | Case | Knowledge/topology event | W- | W+ | D |
| --- | --- | --- | ---: | ---: | ---: |
| 1 | Independent route, partial positive | Create route A and its opening result | 80 | 60 | 20 |
| 2 | Independent route, partial positive | Create sibling route B and a suspect child branch | 105 | 100 | 5 |
| 3 | Dependency, partial positive | Create a route-A foundation depending on submission 1 | 100 | 90 | 10 |
| 4 | Negative/pruning | Prove the suspect route-B branch impossible | 90 | 75 | 15 |
| 5 | Duplicate/reproduction | Add independent support to submission 1's stable result | 75 | 73 | 2 |
| 6 | Topology revelation/correction | Move the stable foundation from route A to shared root scope | 73 | 71 | 2 |
| 7 | Cross-program result | Add one canonical bridge linked to routes A and B | 71 | 59 | 12 |
| 8 | Decisive completion | Solve the root and zero every resolved live package | 59 | 0 | 59 |

Submission 3 decomposes previously implicit route-A work without increasing
its no-access total. Submission 6 reanchors the same stable foundation without
increasing no-access work. These checks prevent topology revelation from
manufacturing credit. Submission 4 demonstrates the completed-node exception:
the branch is zero in live `W+`, while same-world `W-` retains the 15 hours the
unaware community would still incur.

Submission 6 also records one prior-credit correction separately from its own
two-hour work value. The correction changes only the displayed allocation of
submission 3 from route-A-only to a 60/40 route-A/route-B split. It points to
submission 3's immutable evaluation digest, is normalized and digest-bound,
and explicitly states that it does not change a live work estimate. This is a
benchmark expectation for a future correction layer, not a claim that the
current production credit system implements that correction.

## Deterministic score

The code-owned `miniature-e2e-v1` scorer reconstructs and validates every V10
route/packet binding, replays every scoped knowledge transition, and replays
every pair of work patches. It currently evaluates 102 hard assertions,
including exact topology/handoff replay, the frozen `W+` candidate, audit-only
`W-`, positive `D`, processed-submission order, terminal zero-out, and exact
node-level reduction sums. Focused negative tests additionally prove that a
stale authoring packet, an out-of-scope write, and a provenance change hidden
inside a pure topology move are rejected.

Its aggregate adversarial scorecard has eight required groups:

1. duplicate credit;
2. dependency double counting;
3. nonpositive `D`;
4. live `W+` chaining and A-first freeze;
5. solving zero-out;
6. cross-program contribution;
7. topology revelation without invented work; and
8. prior-credit correction separation.

Run the checked-in scenario with:

```bash
python3 -m math_flow teacher-student-scenario \
  --manifest protocol/experiments/miniature-e2e-v1/scenario-v1.json \
  --output-dir /tmp/miniature-e2e-v1 \
  --require-pass
```

Regenerate the transcript, oracle, fixture, and manifest with:

```bash
python3 -m experiments.miniature_e2e_protocol
```

Tests require regeneration to reproduce every checked-in byte exactly.

## Limitations

- Synthetic accepted claims and hour estimates are oracle inputs, so this does
  not measure builder retrieval, semantic judgment quality, or hour calibration.
- The semantic route/refine/author choices remain precommitted, so the benchmark
  bypasses provider calls and cannot establish that a model will choose the
  bound local scope or author the precommitted transition. The deterministic
  V10 route binding, packet construction, and scoped application are exact.
- It mirrors V2's A-first freeze and deterministic accounting but bypasses safe
  fact extraction, epistemic-firewall prompting, retries, and provider output
  validation.
- Prior-credit correction is an explicitly separate benchmark record; no
  production correction reducer or payout rule is introduced.
- The synthetic 40-character transaction IDs are fixture identities, not
  canonical Git commits, and the scenario has no admission or publication path.
- Passing proves reducer composition and invariant coverage only. Paid
  teacher-student tests, small real problems, and an independent adversarial
  evaluator remain required before any shadow or active lane.
