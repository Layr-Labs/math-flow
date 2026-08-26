# BSSC Historical Work-Accounting Bootstrap and Replay V1

Status: provider-free readiness harness, inactive. This does not register or
activate a projection, alter canonical or projection history, call a model, or
write production CAS state.

## Exact source boundary

`math_flow.bssc_work_replay` reads two immutable Git histories at pinned commit
IDs:

- canonical BSSC submissions from the repository's first-parent ledger at
  `180e1032695f2b0f17238a01d7bc9e4ff4fb3f8f`; and
- the terminal hierarchical-research-v5 chain ending at run
  `sha256:6149417354857151da0e2ae910d608b457ec06ffe9d898f9db858e206198def5`
  in projection commit `ebe7a32786e73c244a0c3f95d0e5a111869e1fdb`.

Every run manifest and research-batch/state artifact is read as exact bytes and
checked against its declared SHA-256 digest. The harness then verifies the v5
base-run chain, state predecessor bindings, validity-to-formation status,
cumulative accepted-contribution set, and the exact 25-submission first-parent
order. The small source-pin fixture is
`tests/fixtures/bssc_work_replay_source_v1.json`.

## Why the cutoff is after ordinal 18

The v5 history contains two runs with more than one accepted submission. The
initial run forms six accepted submissions together. A later run forms accepted
ordinals 17 and 18 together. There is no exact provider-produced intermediate
knowledge state between either run's members. Replaying them one at a time would
therefore require inventing mathematical builder output, which this harness
rejects.

The deterministic rule is to cut over after the last v5 run containing multiple
accepted submissions. For BSSC this fixes the bootstrap at canonical ordinal 18,
source state
`sha256:a2de5b6616d7469ea4cb987a35ce6e2acbbc25e79962e96889596b5c8a913884`.
The cutoff covers 12 accepted submissions as baseline history. It does not claim
12 ex-post work reductions.

After that cutoff, accepted ordinals 19, 21, 24, and 25 each have one exact
post-builder state. Ordinals 20, 22, and 23 are excluded-only runs and preserve
the exact knowledge state, so they are not accounting subjects and do not break
the accepted-submission predecessor chain.

## Deterministic v1-to-v2 migration

`migrate_research_program_state_v1_to_v2` validates the complete legacy state,
adds an empty lineage array to each program, and recomputes only the structural
record/state digests. It preserves every program, thread, item, contribution,
status, stable ID, semantic field, provenance reference, and ledger head. The
serialized harness supplies the migrated predecessor digest because the v1 and
v2 content digests necessarily differ.

For each of the four post-cutoff states the harness derives the topology
alignment from the exact migrated before/after pair. Alignment is never supplied
by a provider. The historical post-cutoff changes are additive under stable IDs;
future moves, splits, merges, and retirements remain governed by builder-v6 and
the existing topology reducer.

Programs and research threads are the only numeric accounting nodes. Items are
preserved as semantic/evidence leaves and appear in alignment metadata, but the
accounting state cannot annotate them.

## Readiness result and missing inputs

The checked machine-readable result is
`docs/BSSC_WORK_ACCOUNTING_REPLAY_READINESS_V1.json`. It lists all 25 canonical
subjects, all 16 accepted subjects missing actual work evaluations, the 12
bootstrap subjects, the four exact replay subjects, source and migrated state
digests, deterministic alignment digests, and the activation seam.

The report deliberately remains `activation-blocked-on-provider-inputs`. Real
provider execution must still supply:

1. the governed root contract and a complete cutoff baseline in competent human
   researcher hours for every program/thread; and
2. safe-facts, no-access, and with-access responses for each of the four exact
   post-cutoff submissions.

Only those actual counterfactual responses can establish strict `D = R - C > 0`
for historical submissions. The readiness report explicitly records that this
has not yet been established; it never substitutes fixture estimates.

The production CAS initializer currently requires an empty builder-v6 baseline.
Activation therefore needs a separately reviewed atomic bootstrap operation that
seeds the migrated cutoff knowledge state and provider-authored baseline
accounting state, marks the 12 cutoff subjects as baseline history, and then
executes the four exact transitions. This module does not weaken or bypass that
guard.

## Provider-free proof harness

`tests/test_bssc_work_replay.py` also runs the inactive end-to-end pipeline with
deterministic fixture providers and a real builder-v6 topology split. It proves:

- one work evaluation `x` per accepted fixture submission;
- strict positive `workValueHours` with no clamping;
- exact accounting predecessor chaining;
- identical final artifacts whether both submissions are processed together or
  with `maximum_subjects=1`;
- idempotent resume without repeating builder or work-provider calls; and
- numeric annotations contain only programs and threads, never items.

These fixture results exercise orchestration and invariants only. They are not
BSSC mathematical estimates and are not included in the historical readiness
report.
