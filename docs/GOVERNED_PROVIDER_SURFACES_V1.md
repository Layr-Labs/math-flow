# Governed Provider Surfaces V1

## Status

These surfaces are implemented but inactive. No projection specification or
workflow activates builder-v6 or work-accounting-v1. Activation remains a
separate administrative admission and integration change.

The implementation adds two adapters:

- `OpenRouterResearchBuilderV6Provider` authors one proposed builder-v6
  transition and returns only its content and topology operations after the
  existing deterministic reducer has validated the complete transition.
- `OpenRouterWorkProjectionProvider` implements the existing provider-neutral
  `WorkProjectionProvider` interface for three separately governed roles.

Both adapters accept an injected `OpenRouterTransport`, so tests and future
orchestration can use the existing transport seam without putting network or
persistence behavior into the adapters.

## Work-estimation roles

For exactly one accepted submission transaction `x`, the roles are:

1. `safe-facts` is the governed epistemic judgment boundary. It receives the
   exact complete manifested submission and may return only validated facts and
   explicit assumptions. Structural guards can exclude raw evidence copies and
   unauthorized fields, but they cannot prove that a paraphrase is
   non-actionable; prompt and model governance remain material at this boundary.
2. `no-access` estimates `R(x)`, the same-world remaining work when actors do
   not receive `x`. Its request contains only safe facts, accepted claim
   identities, exact builder-owned program/thread references and summaries,
   assumptions, boundary summaries, the root contract, and the accounting base
   state. It receives no evidence files, raw claim statements, raw evidence
   chunks, full topology alignment, or item-bearing alignment.
3. `with-access` estimates `C(x)` in the identical reference world after actors
   receive the complete digest-verified submission.

The reference world for both `R(x)` and `C(x)` is the exact post-topology
portfolio. This prevents a submission that reveals a previously implicit
program from appearing to increase work merely because the builder made that
work explicit. The unit is one hour of work by a competent human researcher
qualified for the local work package. V1 uses point estimates.

The provider may propose only `directWorkHours` and `conditionalIncidence` on
program or thread nodes. It never authors hierarchical totals, `D(x)`, credit,
or percentages. Trusted reduction applies stale-guarded patches, derives work,
computes `D(x) = R(x) - C(x)`, and rejects `D(x) <= 0` without clamping.

## Firewall and evidence binding

Evidence-bearing requests serialize every verified file as an ordered record
containing its canonical path, byte count, digest, and exact base64 content.
The record set must exactly match the request's content-addressed manifest;
missing, extra, reordered, path-escaping, or digest-mismatched evidence fails
closed.

The no-access adapter requires an empty evidence-file sequence and recursively
rejects evidence-manifest fields, chunk-verification fields, full topology
alignment, encoded submission content, and item-bearing records. The work
runner's earlier byte-window check remains the structural guard against raw
submission spans inside the validated no-access artifact.

Submission and model content are always framed as untrusted quoted JSON. They
cannot modify role prompts or output schemas.

## Retry and invocation identity

Both judge specifications require at most three automatic attempts for empty,
invalid structured, or length-truncated output. There is no manual-review path.
An adapter records only successful invocation metadata, including
content-addressed identities for:

- the complete judge specification, including prompts and policy;
- the transport implementation and endpoint contract;
- requested and resolved model identity;
- exact request and response objects; and
- the complete invocation record.

These records are exposed to later orchestration but are not persisted or
scheduled by this inactive layer.

## Builder-v6 boundary

Builder-v6 receives one accepted submission, its accepted-claim packet, the
exact state-v2 predecessor, and complete verified evidence. Its response schema
contains only the primitive builder transition: content operations, topology
operations, contribution mapping, placement audit, and topology rationale.

The adapter calls `apply_research_builder_v6_transition` as a validation oracle
but discards its derived result. Consequently the provider cannot author or
return `postState`, topology alignment, or the same-world accounting handoff;
trusted reducer code remains their sole author.

## Admission seam

No candidate file is added under `protocol/projections/`. Every file in that
directory is part of the governed registry, even when its status is `disabled`,
so adding a candidate there would itself be an admission.

A later administrative change may separately admit:

- a disabled schema-v1 knowledge projection pairing
  `openrouter-validity-judgment-v4` with
  `openrouter-hierarchical-research-builder-v6`, with no reconciliation stage;
  and
- a disabled schema-v2 overlay using `openrouter-work-accounting-v1` and
  depending on the admitted builder-v6 knowledge-state artifact.

The governance validator now recognizes these exact implementations so those
candidate shapes can be reviewed before admission. Registry validation and
active projection discovery remain unchanged until the separate projection
files and runtime integration are approved.
