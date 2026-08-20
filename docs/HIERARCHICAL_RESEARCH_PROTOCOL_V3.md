# Hierarchical research protocol v3

The v3 path freezes a narrower boundary between mathematical validity and
knowledge formation. It is additive: published v2 packets, judgments, and
research states retain their original semantics and remain replayable.

## Reference provenance is not a logical dependency

A contribution's claim declaration can cite earlier transactions for several
reasons: an indispensable premise, attribution, historical context, or a proof
that is fully restated in the current submission. The v3 evidence packet calls
their union `declaredReferenceTransactionIds`. These references are immutable
provenance and remain available to downstream credit assignment, but they do not
automatically create formation edges.

The primary judge evaluates each valid claim and returns
`requiredDependencyTransactionIds`, an exact subset of the declared references.
It includes only transactions whose mathematical result must already be valid
for the submitted argument to establish the claim. A citation used only for
provenance, or an earlier argument restated completely enough to audit in the
current submission, is not required.

The v3 formation runner uses only these judge-selected required dependencies.
Every required submission must itself have a valid v3 judgment and be included
in research state. Invalid and indeterminate submissions are excluded
completely; a builder cannot import them as results, uncertainty, methods, or
premises. Declared references remain in the immutable judgment and build input
history so later credit work can inspect them without treating them as accepted
knowledge.

For example, the self-contained finite-rotation proof in transaction
`29ccbd396781fd36d436ed2e6d0952a4730361b9` may retain its citation to
`c98dd877ad81611a9a469b1bd790cd909b56b1ce`. If the judge finds the proof fully
restated, its required-dependency set is empty and formation accepts it even if
the cited rct4 submission is invalid. Marking rct4 as required instead makes the
build fail closed.

## Objective-attestation gate

When a subject declares `verification.json`, a v3 primary judgment waits for
the exact canonical request to have one verified terminal objective-attestation
bundle. Pending subjects appear in `deferredTransactions`, not in the hosted
judgment matrix. Ordinary subjects and subjects with terminal attestations
remain in the matrix and can be judged in parallel; there is no problem-wide or
stream-wide attestation barrier.

Both passing and failing terminal attestations unblock adjudication. The
attestation is bounded evidence, not a verdict about the mathematical claim.
The dependency packet embeds its verified request digest, run digest,
attestation ID, outcome, environment, artifact identities, and bounded output.
The packet digest, judgment ID, and run inputs therefore bind the exact
attestation evidence.

After publishing a terminal attestation, the trusted attestation workflow
redispatches every active v3 projection stream that covers the problem. Coverage
planning then schedules the formerly deferred subject without rerunning already
covered independent subjects.

## Versioned components and rollout

The frozen v3 component set is:

- `protocol/judges/openrouter-validity-judgment-v3.json`;
- `protocol/judges/openrouter-hierarchical-research-builder-v3.json`;
- `protocol/profiles/validity-judgment-v3.json`;
- `protocol/profiles/hierarchical-research-v3.json`.

The validity judge's bounded historical context points to the planned
`openrouter-research-v2` lane. The first replay can rely on explicit declared
references while that lane is empty; later submissions receive only
reference-grounded historical nodes from their own v3 state.

Runtime support must merge before a separate, one-file governed projection PR
admits `protocol/projections/openrouter-research-v2.json`. That projection must
pair the v3 primary judge and v3 builder, omit reconciliation, retain parallel
judgment scheduling, and use a fresh projection identity. Do not rewrite or
retarget the active v1 projection in place. Credit overlays can be admitted or
retargeted separately after the new state chain is current.
