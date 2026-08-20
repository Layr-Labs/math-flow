# Hierarchical research protocol v4

Validity v4 is an additive correction to the frozen validity-v3 lane. It keeps
the same division of responsibility:

- the primary judge decides mathematical validity and selects required
  premises;
- the research builder separates accepted results from their proofs, methods,
  computations, and tools, then organizes them into programs; and
- the credit overlay evaluates local program contributions from immutable
  research-state history.

The change is deliberately narrow: a judge must receive terminal objective
evidence not only for a requesting subject, but also for every requesting
transaction explicitly declared as a reference by one of that subject's
claims.

## Bounded evidence packet

The v4 packet contains exactly:

1. one subject transaction and its declared claims;
2. the union of prior transaction IDs declared by those claims;
3. raw artifacts for the subject and that declared-reference union;
4. bounded pre-subject knowledge selected only through those references; and
5. verified terminal objective attestations for requesting transactions in the
   set `{subject} union {declared references}`.

It does not include an unrelated earlier transaction merely because that
transaction has an attestation or appears in the ledger. The packet records
each terminal attestation with its transaction ID and relation (`subject` or
`declared-reference`). Its digest binds the complete evidence collection. The
judgment record binds the packet digest, and the run manifest independently
records the attestation run digest keyed by transaction ID.

Declared references remain provenance until the judge determines that a
claim's argument actually requires them. For each claim,
`evidenceTransactionIds` and `requiredDependencyTransactionIds` may use only
references declared by that same claim. A provenance citation, corrected
target, or completely restated argument is not a formation dependency.

## Terminal-attestation gate

The queue treats each subject independently:

| scoped transaction | state | action |
| --- | --- | --- |
| no `verification.json` | no request | do not add evidence and do not wait |
| canonical request, no terminal run | pending | defer only subjects whose bounded packet needs that transaction |
| terminal `passed` | terminal evidence | include it and run the judge |
| terminal `failed` or `error` | terminal evidence | include it and run the judge; the outcome is evidence, not a validity verdict |

Before a primary judgment exists, the scheduler cannot know whether a declared
reference will become a required mathematical premise. It therefore waits for
every pending request in the claim-declared reference union. This is a local
latency cost, not a serialization barrier: ordinary subjects and subjects whose
scoped requests are terminal remain in the same parallel judgment matrix.

The manual judgment runner repeats the gate and fails closed if scheduling is
bypassed. Publishing a terminal attestation redispatches every active v3 or v4
judgment stream for the affected problem. Coverage then finds the previously
deferred v4 subject uncovered and ready.

Primary judgments never wait for referenced primary judgments. Initial and
full replays may therefore have `knowledgeContext: null`; the judge still has
the exact raw reference artifacts and terminal objective evidence. This
preserves parallel primary execution. Required-premise ordering is enforced
later by deterministic formation.

## Formation and credit

The v4 builder accepts only v4 validity records. It includes only claims marked
`valid`, excludes invalid and indeterminate claims completely, and enforces
accepted-state presence only for the judge-selected required premises. It may
extract a proof, method, computation, or tool only insofar as that material
establishes a valid declared claim. Independent theorem-like prose in an
otherwise accepted submission is not accepted knowledge.

The builder retains declared-reference provenance in immutable build history,
including the validity packet that binds objective evidence, but does not
promote a referenced invalid or indeterminate submission. Research-state
formation remains one deterministic, ledger-ordered batch regardless of
primary-judgment completion order.

The hierarchical credit runner keeps its existing common-horizon,
counterfactual-hindsight, and local-program semantics. Its serialized history
loader accepts v4 research builds and reconstructs accepted claims from their
v4 packets. The admitted `openrouter-research-credit-v3` overlay targets this
producer for the two retained problems, `bssc-sum-capacity` and
`no-three-in-line-77`. Its required runtime fix is deployed and its governed
status is active again. Its first assignment is current for each retained
problem.

## Versioned components and deployed rollout

The runtime introduces new immutable identities:

- `protocol/judges/openrouter-validity-judgment-v4.json`;
- `protocol/judges/openrouter-hierarchical-research-builder-v4.json`;
- `protocol/profiles/validity-judgment-v4.json`;
- `protocol/profiles/hierarchical-research-v4.json`; and
- the v4 evidence-packet and judgment schemas.

The earlier validity-v3 judge, builder, profiles, and
`openrouter-research-v2` projection were not edited. A separate governed
one-file admission added `openrouter-research-v3`, pairing the v4 judge and
builder with no reconciliation stage and the existing parallel/batched
scheduling limits. Both retained problems were replayed to current v3 producer
state before a later one-file governed admission added the matching credit-v3
overlay with an exact producer dependency. A follow-up governed status change
temporarily disabled that overlay before it produced current runs. After the
required runtime fix deployed, a second governed status change re-enabled the
overlay. Current assignment publication has now completed for both retained
problems.

The v1/v2 producer lanes and v2 credit consumer remain temporarily active for
comparison. Credit-v3 is current for both retained problems, so disabling those
superseded specifications now leaves `openrouter-research-v3` as the sole active
registered knowledge lane. Agent context will then select it when `--projection`
is omitted, while an explicit historical projection ID remains auditable.
Disabled specifications and their published bundles keep their original
identities and are never rewritten. Because retirement alone publishes no
mathematical run, operators must dispatch `refresh-viewer-catalog.yml` after the
retirement PRs merge so the live catalog reflects the governed active set.

Builder v4 preserves existing topology but did not deterministically require a
non-root initial taxonomy. The additive builder-v5 correction introduces
audited local/root placement and sibling/nested initial formation without
changing validity v4. See `HIERARCHICAL_RESEARCH_PROTOCOL_V5.md`; v4 artifacts
remain immutable and replayable.
