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

The additive hosted holdout composes this adapter with the serial K1-K3 bundle,
fresh-run checkpoints, durable attempt journals, exact stage ordering, request
and token ceilings, and a request-side OpenRouter `max_price` filter. It is
manual-only and read-only, and retains local Actions artifacts without
publication. It does not provide general semantic-packet generation,
cross-workflow checkpoint resume, split/merge lineage, projection admission,
publication, UI integration, or automatic continuation. Those remain
separately reviewable inactive stages.
