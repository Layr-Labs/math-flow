# Per-submission work projection V1

This document describes the inactive, provider-neutral runner implemented in
`math_flow/work_projection.py`. It is a foundation for later governed
integration. It is not registered as an active projection, scheduled by a
workflow, or admitted into published projection state.

## Transition contract

One run evaluates exactly one accepted submission transaction `x`. The target
knowledge state must be adjacent to the base knowledge state, and `x` must be
the only newly accepted contribution. The base accounting terminal must have
processed every contribution already accepted in the base knowledge state.

Every transition binds the exact:

- root/unit contract;
- base and target knowledge-state digests;
- base accounting-state digest;
- deterministic topology-alignment digest;
- accepted validity/claim identities;
- submission manifest, framed submission digest, and complete chunk set; and
- no-access and with-access requests, responses, patches, states, and final
  evaluation.

The deterministic reducer applies both sparse primitive patches to the same
base accounting state on the target topology. It computes derived work itself
and rejects `W(S_x^-) - W(S_x^+) <= 0`. There is no clamp, epsilon, or automatic
publication fallback. The with-access state is the only candidate next live
state; the no-access state remains an evaluation branch.

## Epistemic boundary

The safe-fact extraction stage receives the exact verified submission as a
sequence of byte-preserving evidence files outside its JSON request. The
validated extraction is the governed semantic judgment boundary. Structural
validation rejects unexpected fields, actor-visible facts, invalid claim/node
references, and evidence-integrity failures, but it deliberately does not use
literal text overlap as a proxy for semantic leakage. It cannot prove that a
valid summary is non-actionable or unbiased.

The no-access request contains the validated safe facts, builder-owned impact
context, root contract, prior numeric annotations, a deterministic topology
alignment reference, and digest bindings. It does not contain the full topology
alignment (which can include submission-revealed item identities), the evidence
manifest, evidence chunks, target knowledge records, with-access request or
patch, or raw submission bytes. Its provider call receives an empty evidence
sequence. Provider-authored safe-fact prose may overlap submission wording; the
protocol relies on the role contract rather than a deterministic substring
rejection until a semantic exposure test establishes a better rule.

The with-access request binds the metadata-only evidence manifest and complete
chunk index. The provider call separately receives every reconstructed file as
exact bytes. Missing, extra, truncated, or digest-mismatched chunks fail before
provider execution.

## Immutable bundle

`run_work_projection_bundle` writes a standard `run.json` checksum index and
canonical paths for all inputs and results. Submission chunks remain separate
content-addressed binary objects under `input/evidence/chunks/`; neither the
manifest nor the stage input duplicates their contents.

`load_work_projection_bundle` verifies all files, rejects loose files and path
escape, optionally checks the expected content address of `run.json`, and then
replays every semantic construction. In particular it rebuilds safe facts,
impact context, stage inputs, provider requests, guarded patches, both states,
and the positive evaluation from the stored base inputs and responses.

Provider checkpoints are keyed by the request digest and bind the stage,
request, response, and response digest. They contain no runtime timestamps, so
resuming a completed set of provider calls produces byte-identical bundles.
Invalid checkpoint data fails closed.

## Deferred integration

V1 deliberately does not implement provider-specific prompting or transport,
scheduling, retry policy, projection admission, publication, CLI commands,
workflow jobs, or accounting-policy upgrades. An inactive, provider-free viewer
adapter is documented in `docs/WORK_ACCOUNTING_VIEWER_V1.md`; it has no catalog
admission path. Other layers can call the provider-neutral interfaces after
their governance and concurrency rules are specified.
