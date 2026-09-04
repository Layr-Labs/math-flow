# Joint portfolio serial provider V2

Status: inactive additive provider milestone. The component now has a
manual-only, publication-forbidden K1-K3 holdout runner and workflow, but no
projection, scheduler, publication, continuation, viewer path, or automatic
provider-spend authority.

## Boundary

`math_flow/joint_portfolio_serial_provider_v2.py` adds the provider-facing
boundary for the trusted serial transition in
`joint_portfolio_serial_transition_v2.py`. It does not alter that reducer and it
does not perform counterfactual `W-`, derive `D`, or allocate credit.

The hosted adapter has three governed stages:

1. `route` sees the V10 route context, accepted validity assessments, and the
   validity-derived semantic packet, but no raw submission evidence;
2. `route-refine` sees the deterministic bounded discovery packet, still with
   no raw evidence; and
3. `joint-author` receives one sealed bounded request and returns one topology,
   result-placement, cumulative-boundary, and live-`W+` response.

The route grants a maximum local scope. It does not require every reserved ID
to be created. Existing result changes and root synthesis must be writable
before authoring begins.

## Sealed author request

`build_joint_portfolio_serial_author_request_v2` validates all authoritative
inputs before provider I/O and binds:

- exact base knowledge-state and ledger-head digests;
- exact base live-`W+` and cumulative-boundary state digests;
- the root contract, accepted-claims digest, semantic-packet digest, judgment
  ID, judge-spec digest, evidence digest, route-plan digest, and V10 authoring
  packet digest;
- exact knowledge records, accounting annotations, and work-policy boundaries
  for the bounded V10 read set;
- the full validity-derived semantic packet and accepted claim assessments;
- digest-verified submission evidence; and
- the exact dynamic structured-response schema with all predecessor bindings
  fixed as constants.

The complete predecessor states remain trusted reducer authority. The model
does not receive a lossy replacement for a local entity, but it also does not
receive unrelated global entities: their preservation is committed by the base
state and V10 hidden-state digests. The serialized author request is capped at
4,000,000 bytes and fails before provider dispatch if it exceeds that bound.

Repository and evidence content is always enclosed as untrusted quoted JSON
data. No repository-authored prompt or instruction is loaded. System and stage
instructions come only from the new inactive versioned judge spec
`openrouter-joint-portfolio-serial-author-v2.json`.

## Provider-neutral capture and replay

The reusable injected interface is:

```python
provider(
    *,
    stage: str,
    request: Mapping[str, object],
    evidence_files: Sequence[SubmissionEvidenceFile],
) -> object
```

`run_joint_portfolio_serial_author_v2` invokes it exactly once with stage
`joint-author`. This allows provider-free capture and fake transports to use the
same sealed request as the hosted adapter. It returns the request, raw response,
request and response digests, the exact trusted V2 reduction, and an outer
result digest. Digest names are deliberately distinct:

- `requestDigest` is the request's self-digest over its canonical core with the
  `requestDigest` field omitted;
- `requestEnvelopeDigest` is the digest of the complete sealed request,
  including that self-digest;
- `responseDigest` is the digest of the complete raw author response; and
- `resultDigest` is the self-digest of the complete result core, which includes
  both request digests, the response digest, and the trusted reduction.

The raw response and its digest preserve the provider's list order. The reducer
separately canonicalizes a copy of the set-like response fields: program changes,
result placements and their related program IDs, work-policy boundaries, live
assessments, and typed evidence references. It does not deduplicate, fill missing
rows, repair references, change numbers or prose, or alter authoritative input
packets. Permutations therefore yield the same reduced state, while raw-response
substitution still fails exact audit replay. Previously canonical reducer outputs
and their digests are unchanged.

Root knowledge is supplied by `semanticPacket.rootUpdate`, not a root row in
`programChanges`. The author must still supply the root boundary and direct-work
assessment in `programBoundaries` and `withAccessAssessments`. The governed
joint-author stage prompt now states this distinction explicitly; root program
changes remain errors and are never silently removed.

The author may create an already-completed program with zero W+ direct work
and incidence. It need not widen the objective to manufacture residual work.
The subsequent W- branch may estimate positive counterfactual work for that
completed live program. Support-only updates still explicitly refresh their
non-root owners and supply complete current-subject assessments; the assessed
numbers may remain unchanged. A nonempty explanation of unchanged topology is
also valid. The inactive stage prompt states all three rules explicitly, and
the exact holdout/hosted pins change with it. No active projection is repinned.

`validate_joint_portfolio_serial_author_replay_v2` rebuilds the request from the
authoritative inputs, checks every digest, and re-runs
`reduce_joint_portfolio_serial_transition_v2`. A changed request, response,
scope, predecessor, semantic packet, evidence file, judge identity, or reduced
artifact fails exact replay.

## Retry and spend boundary

The OpenRouter wrapper uses the repository's canonical automatic retry policy:
at most three attempts for empty, invalid structured, semantically rejected, or
length-truncated responses. Each attempt records request and response digests
and can be persisted through the governed attempt-journal callback. A transport
exception after dispatch is classified as uncertain spend and suppresses every
automatic retry. Trusted input validation and request-size rejection happen
before the first call.

## Evidence and limits

Provider-free tests replay K1 creation, K2 creation of one program containing
two results, and K3 in-place support refresh with no topology creation. Negative
tests cover empty and length-truncated outputs, structured-schema failure,
stale predecessor bindings, out-of-scope writes, request/response tampering,
attempt journals, and uncertain-spend suppression.

The first hosted holdout (`33801731822`, runtime `6c1aca0`) stopped at K1 after
three responses and $0.2340176. Attempt 1 supplied an extra root program change;
attempts 2 and 3 supplied all required entities in a noncanonical order. Exact
parsed response fixtures now exercise the generic adapter with no network:
attempts 2 and 3 pass in one invocation with raw evidence preserved, and attempt
1 still rejects its root row. A separately labeled diagnostic correction of that
row also passes. None of these fixture replays is a published state or credit
assignment. The inactive author prompt and holdout pins change together; no
active projection or accounting rubric changes, and this fix dispatches no run.

The three unaccepted responses implied W+ totals of 446, 1,712, and 3,440 hours.
Their full-response retries changed numerical judgments despite formatting-only
rejections. These are not credit scores or a controlled sampling-variance study:
retry feedback differed and no W- was generated. Deterministic ordering removes
that unnecessary reason to reopen the live-work estimate.

Replacement run `33834473772` (`1ddb8a8`) used 10 calls, 347,787 reported tokens,
and $0.8194814, then stopped at K3. K1 succeeded on its first author attempt;
K2 required one retry. Provider-free checkpoint replay verified K1 W-=1410,
W+=1188, D=222 hours and K2 W-=1348, W+=1158, D=190 hours. There is no completed
K1-K3 bundle, K3 credit, publication, or continuation from that run.

K2's rejected first author response created a completed package; the retry
instead broadened it to an active residual-work package. Completed creation is
now admitted without changing the original response. K3 first omitted the
required owner refresh, then twice supplied valid support refreshes and
unchanged work estimates with an explanation of unchanged topology. Those
last two responses now pass generic validation and the holdout reuse gate
unchanged. The old holdout additionally demanded numerical W+ change; it now
relies on the generic complete current-subject assessment requirement instead.
The response-only fixture retains both accepted and rejected author outputs
with provenance and digests, never raw provider envelopes or reasoning fields.
These are mechanical replay tests, not a new paid semantic result.

The additive hosted holdout composes this adapter with the serial K1-K3 bundle,
fresh-run checkpoints, durable attempt journals, exact stage ordering, request
and token ceilings, and a request-side OpenRouter `max_price` filter. It is
manual-only and read-only, and retains local Actions artifacts without
publication. It does not provide general semantic-packet generation,
cross-workflow checkpoint resume, split/merge lineage, projection admission,
publication, UI integration, or automatic continuation. Those remain
separately reviewable inactive stages.

## Complete hosted sample and context-handoff finding

Run `33839277447` at canonical `04e139a` completed the full holdout. All nine
nominal calls passed on their first attempt, with 253,246 reported tokens and
$0.765019 reported cost. Its byte-verified bundle digest is
`sha256:a9c027373380880cf6fbdb4cab9378d820a306932634d4ccaff9888f5074d788`.
K1 produced `W-=1832`, `W+=1408`, `D=424`; K2 produced `1480`, `1408`, `72`;
and K3 produced `1600`, `1408`, `192` competent-researcher hours. The run made
no publication or continuation attempt.

The mechanics passed, including K2 completed-at-creation and K3 unchanged live
W+, but the K3 counterfactual is not yet semantically acceptable as a reference
result. The joint author received K2's complete relevant prior result records
and correctly classified K3 as new support for the same completed results. The
safe-fact request did not receive those prior records. Its schema permits only
subject-derived facts labeled `withheld-until-independent-discovery`. The W-
request received the zero-work completed package, its exact prior stopping
policy, and structural result/provenance references, but the state-v3 impact
packet deliberately omits prior result statements, support bodies, titles, and
scope prose. It then charged 480 conditional hours at incidence 0.4 for proving
the already completed theorem package.

A provider-free reconstruction reproduced the exact recorded safe-fact and W-
provider request digests, including the effective price-filtered digests. Those
requests were 26,001 and 26,484 bytes, used 12,415 and 7,345 reported prompt
tokens, and both returned with `finish_reason=stop`. This rules out request
truncation or context-window overflow for the observation. A separate local
diagnostic proved that an empty K3 W- patch is structurally valid and reproduces
`W-=W+=1408`, after which the current strictly-positive-D gate rejects it.

The next candidate should add a bounded, digest-bound pre-submission epistemic
packet for the local impact slice. It should carry compact prior statements,
qualifications, support summaries, and provenance to the safe-fact and W-
stages, and distinguish independently available information from information
unique to the current submission. Do not expose the full global predecessor or
raw prior artifacts. Implement this under an additive joint-only profile rather
than changing the active work-V2 identity in place. Provider-free regressions
must cover a truly novel contribution, an independently supported duplicate,
and exact absence of raw subject evidence from W-. Whether a valid zero marginal
reduction should be recorded rather than rejected remains an explicit policy
decision, not a prompt-only correction.
