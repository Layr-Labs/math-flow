# BSSC Builder V10 plus separate Work Accounting V2 lane

This additive BSSC-only shadow protocol turns the previously inactive local
Builder V10 candidate into a serial knowledge projection and connects a
separate A-first Work Accounting V2 projection to that exact knowledge chain.
It exists as an initial end-to-end semantic-evaluation target. It does not
change or migrate any Builder V4–V9 or Work Accounting V1/V2 history.

The two governed projection identities are openrouter-research-v8, using
validity v4 and openrouter-hierarchical-research-builder-v10, and
openrouter-v10-work-accounting-v2, consuming the exact published V8 knowledge
transition and using the existing openrouter-work-accounting-v2 judge and
policy.

Runtime support, workflows, and active-form projection candidates merge before
the projections are admitted. Each candidate must then be copied byte-for-byte
through its own one-file governed PR under docs/GOVERNANCE.md. Neither workflow
can run successfully before its corresponding admission exists.

## Knowledge sequence

The V8 knowledge lane starts at the empty state-v3 root and processes the 16
validity-v4-accepted BSSC submissions in canonical accepted order. One workflow
run may form only one adjacent transition. The trusted frontier planner:

1. verifies the pinned 25-submission validity history and its 16 accepted
   subjects;
2. verifies that the published V8 chain is an exact accepted prefix;
3. materializes the already-published immutable validity bundle for the next
   accepted subject;
4. requires a one-judgment scheduler claim; and
5. binds the exact predecessor bundle, projection digest, Builder V10 digest,
   submission, judgment, and evidence.

Builder V10 then performs route, route-refine, and organize calls. Routing sees
only bounded digest-bound local/fractal context; raw submission evidence is
available only to organize. Trusted code expands hidden state, applies the
unchanged state-v3 reducer, stores all route and authoring artifacts in the
bundle, and replays them when the bundle is loaded.

The dedicated workflow is manual. continue=false produces at most one
transition. continue=true dispatches another run only after successful
publication when another accepted frontier remains. The generic OpenRouter
workflow rejects this projection, so it cannot accidentally bypass the serial
route.

## Work-accounting sequence

The accounting lane also starts from zero and advances one subject at a time.
For an eligible subject it discovers and fully replays the unique published V8
transition for the exact old knowledge state and accepted submission. It then
uses the state-v3 pipeline and existing V2 call order:

1. extract safe facts;
2. estimate and freeze live with-access state W+;
3. estimate audit-only same-base no-access state W-;
4. derive D = W- - W+ in trusted code; and
5. commit only the validated W+ state.

The V10 lane uses rich validity-v4 claim assessments, including accepted scope
qualifications, rather than collapsing them to the earlier statement-only
shape. The accounting root contract names the V8 builder as portfolio
authority and retains competent-human-researcher hours as the stable unit.

The work workflow is dispatch-only and single-subject. It has the same frozen
plan, durable history, retry isolation, fresh prepublication recheck, immutable
CAS, and GitHub-signed projection publication boundary as the active BSSC V2
lane. Only its execute step receives the OpenRouter key, and only its publish
step receives the repository token in its environment. It has no automatic
schedule because the lane is intended for controlled semantic evaluation.

## Publication and evaluation boundary

The runtime merge and the two projection admissions do not themselves call a
provider or publish projection artifacts. A maintainer must separately
authorize and dispatch the knowledge workflow. Accounting can advance only
after its exact V8 predecessor has appeared on the projections branch.

Both workflows refresh the repository-backed viewer catalog after successful
publication, so admitted and published V8 knowledge and V10/V2 accounting
states become selectable in the Research Atlas without a viewer redeploy.

This lane is a semantic-evaluation target, not evidence that Builder V10 routing
or V2 hour estimates are calibrated. Keep its identity and history additive.
Use exact published artifacts for adversarial evaluation, and do not overwrite
the older comparison lanes.
