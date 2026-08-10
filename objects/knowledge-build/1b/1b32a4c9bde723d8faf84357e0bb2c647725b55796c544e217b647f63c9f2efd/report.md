## Node: root
Stable id: root

Organizational change
- Preserve the existing top-level program node "Research state for triangle-midpoints" and append links (provenance pointers) to the new claim nodes created below. No change to the root's status ("active"), but its content is expanded by explicit child claim nodes derived from the immutable judgment report.

Provenance
- This update follows the single immutable judgment report listed below (sha256:9df802c9...). See child nodes for the detailed attributions and evidence lists.

Reference (immutable judgment)
- Judgment: sha256:9df802c904f03c561ed0d5e78f4181765fb2ad58e7cfe5f65df22949d7de4fce
- Subject transaction: 8bcf66bbd7777ee31f637a0a1a144535feb82ba4

Credit statement carried forward
- The judgment attributes the contributions and correction to the same author (Robert). That credit is preserved here as part of the provenance for the child nodes.

----

## Node: triangle-midpoints/altitude-equality
Stable id: triangle-midpoints/altitude-equality

Claim (as recorded in the supplied judgments)
- The ancillary statement "the altitude from A to EF equals the altitude from A to BC" is refuted.

Stance and confidence (preserved from the immutable judgment)
- Stance: refutes
- Confidence (as recorded in the judgment): high

Summary of provenance and reasoning recorded in the judgment
- Source judgment: sha256:9df802c904f03c561ed0d5e78f4181765fb2ad58e7cfe5f65df22949d7de4fce (subject transaction 8bcf66bbd7777ee31f637a0a1a144535feb82ba4).
- Evidence transaction ids cited in the judgment: 8bcf66bbd7777ee31f637a0a1a144535feb82ba4 and 4ccbe3f18db7402d31a2ef795f6ad67962ff63e3.
- Recorded decisive reasoning: With E and F midpoints of AC and AB, the homothety centered at A with scale factor 1/2 sends BC to EF and scales all distances from A by 1/2; therefore the perpendicular distance (altitude) from A to EF is half, not equal to, the perpendicular distance from A to BC.
- Note on provenance gap recorded in the judgment: The judgment notes a meta-commentary provenance inconsistency (an earlier erroneous sentence is not present in the supplied midpoint-lemma-detail file), but treats the refutation and correction as self-contained.

Audit trail
- Immutable judgment id: sha256:9df802c904f03c561ed0d5e78f4181765fb2ad58e7cfe5f65df22949d7de4fce
- Subject transaction: 8bcf66bbd7777ee31f637a0a1a144535feb82ba4
- Evidence transaction ids: 8bcf66bbd7777ee31f637a0a1a144535feb82ba4, 4ccbe3f18db7402d31a2ef795f6ad67962ff63e3

Remarks for an auditor
- This node preserves the judgment's exact stance (refutes) and recorded confidence (high). No attempt is made here to re-prove or further justify the refutation beyond quoting the judgment's reasoning and evidence pointers.

----

## Node: triangle-midpoints/area-aef-one-quarter
Stable id: triangle-midpoints/area-aef-one-quarter

Claim (as recorded in the supplied judgments)
- area(AEF) = (1/4) · area(ABC)

Stance and confidence (preserved)
- Stance: supports
- Confidence (as recorded in the judgment): high

Summary of provenance and reasoning recorded in the judgment
- Source judgment: sha256:9df802c904f03c561ed0d5e78f4181765fb2ad58e7cfe5f65df22949d7de4fce (subject transaction 8bcf66bbd7777ee31f637a0a1a144535feb82ba4).
- Evidence transaction ids cited in the judgment: 8bcf66bbd7777ee31f637a0a1a144535feb82ba4, 4ccbe3f18db7402d31a2ef795f6ad67962ff63e3, 64afc12868e150370e6c56e6eeceab6b7aabe158.
- Recorded decisive reasoning: Vector/determinant formulation or homothety about vertex A with factor 1/2. Writing position vectors relative to A, E − A = (C − A)/2 and F − A = (B − A)/2, so the area determinant for triangle AEF is 1/4 of that for ABC; equivalently, halving both base and corresponding height gives area scaling factor 1/4.

Audit trail
- Immutable judgment id: sha256:9df802c904f03c561ed0d5e78f4181765fb2ad58e7cfe5f65df22949d7de4fce
- Subject transaction: 8bcf66bbd7777ee31f637a0a1a144535feb82ba4
- Evidence transaction ids: 8bcf66bbd7777ee31f637a0a1a144535feb82ba4, 4ccbe3f18db7402d31a2ef795f6ad67962ff63e3, 64afc12868e150370e6c56e6eeceab6b7aabe158

Remarks for an auditor
- The node records the judgment's exact supportive stance and its coupling to the cited evidence. No independent verification or extension is attempted here.

----

## Node: triangle-midpoints/area-def-one-quarter
Stable id: triangle-midpoints/area-def-one-quarter

Claim (as recorded in the supplied judgments)
- area(DEF) = (1/4) · area(ABC)

Stance and confidence (preserved)
- Stance: supports
- Confidence (as recorded in the judgment): high

Summary of provenance and reasoning recorded in the judgment
- Source judgment: sha256:9df802c904f03c561ed0d5e78f4181765fb2ad58e7cfe5f65df22949d7de4fce (subject transaction 8bcf66bbd7777ee31f637a0a1a144535feb82ba4).
- Evidence transaction ids cited in the judgment: 4ccbe3f18db7402d31a2ef795f6ad67962ff63e3, 64afc12868e150370e6c56e6eeceab6b7aabe158.
- Recorded decisive reasoning: Midpoint lemma: EF ∥ BC and |EF| = |BC|/2 (and cyclic variants for other sides), so triangle DEF is similar to ABC with linear scale 1/2 and hence area scales by (1/2)^2 = 1/4.

Audit trail
- Immutable judgment id: sha256:9df802c904f03c561ed0d5e78f4181765fb2ad58e7cfe5f65df22949d7de4fce
- Subject transaction: 8bcf66bbd7777ee31f637a0a1a144535feb82ba4
- Evidence transaction ids: 4ccbe3f18db7402d31a2ef795f6ad67962ff63e3, 64afc12868e150370e6c56e6eeceab6b7aabe158

Remarks for an auditor
- This node preserves the judgment's conclusion that the medial triangle DEF has area 1/4 that of ABC, citing the same judgment and the midpoint-lemma-detail and affine-area-proof materials.

----

## Node: triangle-midpoints/four-small-triangles-equal-area
Stable id: triangle-midpoints/four-small-triangles-equal-area

Claim (as recorded in the supplied judgments)
- The four triangles AEF, BFD, CDE, and DEF have equal area (each equal to one quarter of area(ABC)).

Stance and confidence (preserved)
- Stance: supports
- Confidence (as recorded in the judgment): high

Summary of provenance and reasoning recorded in the judgment
- Source judgment: sha256:9df802c904f03c561ed0d5e78f4181765fb2ad58e7cfe5f65df22949d7de4fce (subject transaction 8bcf66bbd7777ee31f637a0a1a144535feb82ba4).
- Evidence transaction ids cited in the judgment: 8bcf66bbd7777ee31f637a0a1a144535feb82ba4, 4ccbe3f18db7402d31a2ef795f6ad67962ff63e3, 64afc12868e150370e6c56e6eeceab6b7aabe158.
- Recorded decisive reasoning: Combine the corner-triangle scaling results (each corner triangle is homothetic to the corresponding corner of ABC with linear factor 1/2 → area 1/4 of ABC) with the medial-triangle area result (DEF area 1/4 of ABC). Since all four are equal to 1/4 area(ABC), they are equal to each other.

Audit trail
- Immutable judgment id: sha256:9df802c904f03c561ed0d5e78f4181765fb2ad58e7cfe5f65df22949d7de4fce
- Subject transaction: 8bcf66bbd7777ee31f637a0a1a144535feb82ba4
- Evidence transaction ids: 8bcf66bbd7777ee31f637a0a1a144535feb82ba4, 4ccbe3f18db7402d31a2ef795f6ad67962ff63e3, 64afc12868e150370e6c56e6eeceab6b7aabe158

Remarks for an auditor
- This node records the overall theorem as supported in the immutable judgment. The exact supportive logic and evidence citations are preserved without modification.

----

Status of conflicts
- The supplied conflict records list is empty. There are no unresolved or active conflicts to represent.
- The only refutation present is the recorded refutation of the ancillary altitude-equality claim; that refutation is represented above as an explicit node and preserved as an active settled refutation (the judgment itself contains a high-confidence refutation and no competing judgments were supplied).

Final notes for auditing
- All nodes above reproduce exactly the stances, summaries, evidence pointers, and confidence levels given in the immutable judgment sha256:9df802c9...; no additional mathematical claims, proofs, or reconciliations have been introduced or inferred beyond those explicitly recorded in that judgment.
- For detailed line-by-line reasoning, consult the cited subject transaction 8bcf66bbd7777ee31f637a0a1a144535feb82ba4 and the evidence transactions listed in each node.
