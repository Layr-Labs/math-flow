# Canonical Per-Submission Work-Accounting Scheduling V1

Status: normative foundation, inactive. This policy defines scheduling and
publication semantics for hierarchical work accounting. It does not register a
projection, change an active workflow, or authorize provider execution.

## 1. Semantic order

The credit subject is one accepted submission transaction. For each problem,
the scheduler obtains submission order from the canonical `main` first-parent
problem ledger. It intersects that order with the exact accepted contribution
records in the builder-owned knowledge state. Items, programs, and research
threads are context and accounting nodes; none is a second credit subject.

Every accepted transaction has exactly one subject record. Successfully
processed subjects must form a prefix of the accepted transactions in canonical
ledger order. A subject cannot run while an earlier canonical transaction lacks
a terminal validity and formation disposition, even if that earlier transaction
will ultimately be excluded. `resolvedSubmissionIds` records this coverage.
An accepted transaction is necessarily resolved; a resolved transaction need
not be accepted.

The knowledge builder can process several submissions in one hosted batch. In
that case several subjects may bind the same exact post-builder knowledge-state
digest. Accounting still serializes them:

```text
A0 --x1--> A1 --x2--> A2 --x3--> A3
```

Each arrow is planned, evaluated, published, and committed separately. Provider
request grouping, worker count, batch size, and wall-clock timing are absent
from transition and publication identity. Changing operational grouping must
not change any claim, evaluation, publication, or committed-state digest.

## 2. Schedule state

`work-accounting-schedule-v1` is an append-only discovery and execution record
for one problem and projection lane. It binds:

- the exact projection spec and root contract;
- the canonical problem-ledger digest and ordered transaction IDs;
- terminal disposition coverage;
- a fixed deterministic automatic-retry policy;
- the latest observed builder-owned knowledge state;
- the initial and current terminal accounting states;
- one ordered record per accepted submission; and
- prospective state-repair event digests.

Each subject freezes the exact knowledge state first observed after the builder
accepted it. Ordinary discovery may append canonical ledger history, add newly
accepted subjects, and add terminal dispositions. It may not remove an accepted
subject or disposition. If a later builder decision would insert an accepted
subject behind already processed accounting history, ordinary discovery fails;
that inconsistency requires an explicit prospective repair rather than silent
reordering or replay.

Subject status is explicit:

- `pending`: the canonical frontier is eligible for a first attempt;
- `failed`: its latest deterministic attempt failed and is retryable or
  exhausted as shown by failure history;
- `blocked`: an earlier canonical disposition or accepted subject is
  unresolved; or
- `processed`: an immutable publication, or an explicitly declared bootstrap
  cutoff, completed the subject.

Processed subjects form a prefix. Later subjects remain blocked behind the
first incomplete accepted subject.

## 3. Exact transition claims

A transition claim binds one subject record to:

- its canonical ledger ordinal;
- the exact live predecessor accounting-state digest;
- the exact predecessor builder-state digest;
- the subject's frozen post-builder state digest and ledger head;
- the next consecutive attempt number;
- the previous failed claim, when retrying; and
- a stable automatic-retry key.

Planning fails closed if supplied states do not match the schedule terminal, if
the subject is absent from the target builder state, or if processed IDs differ
between accounting and scheduling state. A stale claim cannot advance state.

The retry key is constant across attempts for the same semantic transition. It
is not permission to reuse a provider answer: each attempt has its own claim
digest and append-only failure evidence.

## 4. Failure and retry

V1 recognizes provider-invalid, nonpositive-work-value,
counterfactual-invalid, and publication-invalid failures. A failure records its
claim, evidence digest, attempt, timestamp, deterministic exponential backoff,
and exhaustion bit. The maximum attempt count and base delay are sealed into
the schedule; callers cannot vary them from attempt to attempt.

Nonpositive `D(x)` is invalid. It is never clamped to zero or converted into a
nominal credit. Provider-invalid or semantically invalid output likewise cannot
advance accounting state. Retry is automatic and bounded. Exhaustion leaves the
subject explicitly failed and blocks the accepted suffix. V1 has no manual
review, approval, or override path.

## 5. Publication and crash recovery

A publication manifest is materialized only from a valid positive
`submission-work-value-v1` evaluation. It binds the exact transition claim,
both primitive patches, the ephemeral no-access state, the committed
with-access state, and `D(x)` in competent-human-researcher hours.

The publication reducer recomputes this manifest from the supplied evaluation
and exact states. It does not trust duplicated provider-authored work totals or
derived state. The committed state must append the one subject to
`processedSubmissionIds`, name that subject, use `with-access` mode, and descend
from the exact predecessor.

Publication application is idempotent for the exact same manifest. A crash
after artifact materialization but before schedule commit can safely resume by
reconstructing the same claim and publication. A second, different publication
for an already processed subject is rejected. Publication manifests contain no
hosted-batch identity, so recovery and batching do not change results.

## 6. Corrections

V1 corrections are prospective state-repair events. A repair is permitted only
at an empty subject backlog and advances the live terminal accounting state to
a new baseline state over the exact current builder topology. It preserves the
ordered processed-submission IDs and records a nonempty canonical subset of
historical evaluations affected by the correction.

The historical publication and work-value artifacts remain immutable. Subject
records receive `affectedByRepairDigests` flags so consumers can distinguish an
original estimate from later knowledge about its reliability. V1 sets
`suffixReplay: false`: it does not automatically rescore or rewrite the
historical suffix. Future submissions use the repaired state as their exact
predecessor.

Corrections require immutable evidence references and one of the governed
reason kinds: validity reversal, evidence defect, implementation defect, or
topology-lineage defect. They are not a manual-review escape hatch for failed
provider output.

## 7. Integration boundary

The pure implementation is `math_flow.work_accounting_schedule`. It validates
and reduces caller-supplied artifacts without invoking a provider, writing a
projection branch, or defining another portfolio topology. The builder-owned
knowledge state remains authoritative for program and thread identity,
parentage, ownership, item semantics, and topology lineage.

Activation still requires separately reviewed persistence paths, evidence
construction, provider-stage integration, projection registration, workflow
wiring, and viewer presentation. Those operations are outside this inactive V1
foundation.
