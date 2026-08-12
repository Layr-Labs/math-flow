# Knowledge-Formation Report: Triangle Midpoint Quadrilateral

## Formation summary

The prior materialized state contained only the root node and stated that no judge-authored research program had been established. The supplied primary judgments now support a durable hierarchy consisting of:

1. the equal-area theorem for the four midpoint triangles;
2. the midpoint-segment relations supporting that theorem;
3. the corrected altitude-scaling relation and its base-height application; and
4. the current status of possible formal verification.

The mathematical conclusions below are attributed to the immutable judgments. No independent proof, extension, or reassessment is introduced.

No conflict records or reconciliation outcomes were supplied. Consequently, no active-dispute node is required. In particular, the refuted equal-altitude assertion is not an unresolved conflict: judgment `sha256:ae48d86e7bd2cdc4b6c2a708194553c6c8444c7f448bd73a82f8af95b64580c3` expressly rejects it and also states that neither earlier supplied contribution contains it. That judgment retains uncertainty only about whether the unavailable external report actually contained the quoted error.

---

## Node: root

- **Type:** root
- **Status:** active
- **Title:** Research state for triangle-midpoints

The current research state concerns the geometry and area relations produced by joining the side midpoints of a nondegenerate triangle.

The supplied primary judgments establish an ordinary elementary proof, assessed as correct and complete with high or very high confidence, that the four triangles determined by the three side midpoints all have area one quarter of the original triangle. The established state includes:

- the equal-area theorem in `triangle-midpoints/equal-area`;
- the midpoint vector and segment relations in `triangle-midpoints/midpoint-segment-relations`;
- the correct scaling of the altitude to a midpoint segment in `triangle-midpoints/altitude-scaling`; and
- the limited verification status in `triangle-midpoints/formal-verification`.

The supported proof framework uses the midpoint theorem, position-vector identities, similarity or homothety with scale factor \(1/2\), and standard area-scaling formulas. An optional base-height argument is valid only when both the base and the corresponding altitude are scaled by \(1/2\); parallelism alone does not make the two altitudes equal.

The evidence establishes an informal Euclidean and vector proof. It does not establish completed Lean verification or any other machine-checked formalization.

### Source-judgment attribution

- `sha256:427537f9898af49bb7e20230201f0ab01db5a51cccbfdb5b57c474e488b3a262` supports the midpoint-theorem, corner-area, medial-area, and final equal-area conclusions, while qualifying the formalization suggestion.
- `sha256:575cfe733758035c57b6a7f7915c3e2a38a78c25f4b0c6ce026504546e4655ed` supports the vector derivation of the midpoint relations and the resulting similarity and area conclusions.
- `sha256:ae48d86e7bd2cdc4b6c2a708194553c6c8444c7f448bd73a82f8af95b64580c3` supports the corrected altitude scaling, refutes the equal-altitude assertion, and confirms that the main equal-area theorem and earlier arguments remain valid.

---

## Node: triangle-midpoints/equal-area

- **Parent:** `root`
- **Type:** claim
- **Status:** active
- **Title:** Equal areas of the four midpoint triangles

Let \(ABC\) be a nondegenerate triangle, and let \(D\), \(E\), and \(F\) be the midpoints of \(BC\), \(CA\), and \(AB\), respectively. The supplied judgments support, as correct and complete,

\[
[AEF]=[BFD]=[CDE]=[DEF]=\frac14[ABC].
\]

The current supported account is:

- The medial triangle \(DEF\) is similar to \(ABC\) with linear scale factor \(1/2\), because its sides are parallel to and half the lengths of the corresponding sides of \(ABC\). Its area is therefore \([ABC]/4\).
- Each corner triangle is a half-scale copy of the corresponding orientation of \(ABC\). Equivalently, its two sides adjacent to the original vertex are half the corresponding original sides and have the same included angle. Thus each corner triangle has area \([ABC]/4\).
- The cyclic cases \(BFD\) and \(CDE\) require no additional substantive lemma beyond the argument for \(AEF\); the judgments characterize the omitted cyclic computations as expository compression rather than a logical gap.
- A separate partition argument is unnecessary because each of the four areas is independently identified as one quarter of \([ABC]\). Judgment `sha256:427537f9898af49bb7e20230201f0ab01db5a51cccbfdb5b57c474e488b3a262` specifically finds no circularity on this point.
- Nondegeneracy ensures \([ABC]>0\) and gives positive unsigned areas for all four smaller triangles. Judgment `sha256:575cfe733758035c57b6a7f7915c3e2a38a78c25f4b0c6ce026504546e4655ed` notes that the vector identities would also imply equal zero areas in a degenerate extension, but the supplied proof is not required to treat that extension.
- The false optional assertion that parallel lines \(EF\) and \(BC\) are equally distant from \(A\) is not needed for the theorem. The correct altitude relation is recorded in `triangle-midpoints/altitude-scaling`.
- The result is established only at the level of an ordinary mathematical proof; no machine-checked artifact has been supplied.

### Source-judgment attribution

- Judgment `sha256:427537f9898af49bb7e20230201f0ab01db5a51cccbfdb5b57c474e488b3a262` supports:
  - `medial-triangle-area-quarter`;
  - `corner-midpoint-triangles-area-quarter`; and
  - `four-midpoint-triangles-equal-area`.
- Judgment `sha256:575cfe733758035c57b6a7f7915c3e2a38a78c25f4b0c6ce026504546e4655ed` supports:
  - `medial-triangle-is-similar-to-original-at-half-scale`;
  - `each-corner-midpoint-triangle-has-quarter-area`; and
  - the positive-area qualification under nondegeneracy.
- Judgment `sha256:ae48d86e7bd2cdc4b6c2a708194553c6c8444c7f448bd73a82f8af95b64580c3` supports `triangle-midpoints/four-subtriangles-have-equal-area` and explicitly states that the altitude correction does not undermine the theorem, the midpoint identities, the similarity argument, or the included-angle area argument.

---

## Node: triangle-midpoints/midpoint-segment-relations

- **Parent:** `triangle-midpoints/equal-area`
- **Type:** lemma
- **Status:** active
- **Title:** Parallelism and half-length relations for triangle midpoint segments

For position vectors \(A,B,C\) and side midpoints

\[
D=\frac{B+C}{2},\qquad
E=\frac{C+A}{2},\qquad
F=\frac{A+B}{2},
\]

judgment `sha256:575cfe733758035c57b6a7f7915c3e2a38a78c25f4b0c6ce026504546e4655ed` supports the identities

\[
E-F=\frac{C-B}{2},\qquad
F-D=\frac{A-C}{2},\qquad
D-E=\frac{B-A}{2}.
\]

The same judgment concludes from these identities that

\[
EF\parallel BC,\qquad
FD\parallel CA,\qquad
DE\parallel AB,
\]

and that

\[
|EF|=\frac12|BC|,\qquad
|FD|=\frac12|CA|,\qquad
|DE|=\frac12|AB|.
\]

Endpoint-order signs do not affect the parallelism or length conclusions.

These relations support SSS similarity between \(DEF\) and \(ABC\) with scale factor \(1/2\). They also provide the half-length relations needed for the corner triangles. The judgments recognize both the standard midpoint theorem and the explicit position-vector identities as valid routes to these facts.

### Source-judgment attribution

- `sha256:575cfe733758035c57b6a7f7915c3e2a38a78c25f4b0c6ce026504546e4655ed` directly supports the vector identities and their parallelism and half-length consequences with very high confidence.
- `sha256:427537f9898af49bb7e20230201f0ab01db5a51cccbfdb5b57c474e488b3a262` supports invoking the same relations through the standard midpoint theorem and finds that invocation sufficient for an ordinary Euclidean proof.

---

## Node: triangle-midpoints/altitude-scaling

- **Parent:** `triangle-midpoints/equal-area`
- **Type:** claim
- **Status:** active
- **Title:** Altitude scaling under the midpoint homothety

Let \(E\) and \(F\) be the midpoints of \(AC\) and \(AB\). Judgment `sha256:ae48d86e7bd2cdc4b6c2a708194553c6c8444c7f448bd73a82f8af95b64580c3` supports, with high confidence,

\[
\operatorname{dist}(A,\overleftrightarrow{EF})
=
\frac12\operatorname{dist}(A,\overleftrightarrow{BC}).
\]

The judgment attributes this relation to the homothety centered at \(A\) with scale factor \(1/2\), which maps \(B\) to \(F\), \(C\) to \(E\), and the line \(BC\) to the line \(FE\).

The same judgment refutes the assertion that the two altitudes are equal merely because \(EF\parallel BC\). Its current adjudicated status is:

- parallelism alone does not imply equal distances from a fixed point to two parallel lines;
- in this configuration, the altitude from \(A\) to \(EF\) is half the altitude from \(A\) to \(BC\), not equal to it.

Together with

\[
|EF|=\frac12|BC|,
\]

the supported base-height computation gives

\[
[AEF]=\frac14[ABC].
\]

The corresponding argument applies cyclically to the other corner triangles, as stated by the same judgment.

The judgment also records a provenance limitation: the external report allegedly containing the equal-altitude assertion was not supplied, so its wording and context cannot be verified. This uncertainty concerns attribution of the erroneous statement, not the mathematical assessment of that statement. Neither of the two earlier supplied contribution artifacts contains the equal-altitude assertion.

### Source-judgment attribution

All conclusions and qualifications in this node come from:

- `sha256:ae48d86e7bd2cdc4b6c2a708194553c6c8444c7f448bd73a82f8af95b64580c3`, specifically:
  - support for `triangle-midpoints/altitude-scaling-under-midpoint-homothety`;
  - refutation of `triangle-midpoints/equal-altitudes-from-parallelism`;
  - support for `triangle-midpoints/corner-triangle-quarter-area-by-base-height`; and
  - support for the continued validity of the earlier midpoint, similarity, and included-angle arguments.

---

## Node: triangle-midpoints/formal-verification

- **Parent:** `triangle-midpoints/equal-area`
- **Type:** verification-status
- **Status:** active
- **Title:** Formal-verification status of the midpoint equal-area theorem

The supplied evidence establishes an informal Euclidean and vector proof of the equal-area theorem. It does not establish completed formal verification.

Affine invariance and determinant methods have been identified as mathematically plausible approaches to a future Lean formalization, but the judgments report that no formal statement, source code, proof script, or machine-checked artifact was supplied. The formalization suggestion therefore remains prospective rather than verified evidence.

This limitation applies only to the verification medium. The judgments expressly state that it does not weaken their assessment of the ordinary mathematical proof as correct and complete.

### Source-judgment attribution

- `sha256:427537f9898af49bb7e20230201f0ab01db5a51cccbfdb5b57c474e488b3a262` qualifies `formalization-via-affine-invariance-or-determinants`: the suggested methods are plausible, but no completed formal verification is evidenced.
- `sha256:575cfe733758035c57b6a7f7915c3e2a38a78c25f4b0c6ce026504546e4655ed` likewise reports that no Lean artifact or other formal verification was provided.
- `sha256:ae48d86e7bd2cdc4b6c2a708194553c6c8444c7f448bd73a82f8af95b64580c3` confirms that no formal artifact is supplied and that none is needed for the completeness of the elementary paper proof.

---

# Revision provenance

## Change: root

The selected root previously had digest `sha256:a6f9dfb09d5938331e9e74179208f8c1017988ec1f7d4c9d516ad69993f9160e` and stated that no judge-authored research programs had been established.

That placeholder account should be replaced by the holistic research state above because all three primary judgments now support a stable theorem and durable supporting concepts. The contribution and judgment events themselves have not been turned into nodes.

**Formation basis:**

- `sha256:427537f9898af49bb7e20230201f0ab01db5a51cccbfdb5b57c474e488b3a262`
- `sha256:575cfe733758035c57b6a7f7915c3e2a38a78c25f4b0c6ce026504546e4655ed`
- `sha256:ae48d86e7bd2cdc4b6c2a708194553c6c8444c7f448bd73a82f8af95b64580c3`

No conflict or reconciliation content address is applicable because no conflict records were supplied.

---

## Change: triangle-midpoints/equal-area

This node should be created as the principal durable claim. It consolidates the overlapping claim keys about the medial triangle, the three corner triangles, and the final equality instead of creating separate event-shaped nodes for each contribution or judgment.

The node preserves the judgments’ confidence and scope:

- the theorem is correct and complete as an ordinary mathematical proof;
- nondegeneracy supplies positive unsigned areas;
- no partition argument is required;
- the altitude correction does not retract or weaken the theorem; and
- completed formal verification is not claimed.

**Provenance:**

- Primary judgment `sha256:427537f9898af49bb7e20230201f0ab01db5a51cccbfdb5b57c474e488b3a262`, concerning transaction `64afc12868e150370e6c56e6eeceab6b7aabe158`.
- Primary judgment `sha256:575cfe733758035c57b6a7f7915c3e2a38a78c25f4b0c6ce026504546e4655ed`, concerning transaction `4ccbe3f18db7402d31a2ef795f6ad67962ff63e3`.
- Primary judgment `sha256:ae48d86e7bd2cdc4b6c2a708194553c6c8444c7f448bd73a82f8af95b64580c3`, concerning transaction `8bcf66bbd7777ee31f637a0a1a144535feb82ba4`.

**Credit carried forward from the judgments:**

- The first judgment credits Robert’s contribution with a concise and complete proof using the midpoint theorem, similarity, and area scaling.
- The second judgment characterizes the vector derivation as an explanatory supplement rather than a repair of an invalid proof. It reports no new theorem or novel method and notes the contribution’s disclaimer of originality for the classical result.
- The third judgment states that Robert’s narrow correction does not challenge the main theorem and does not establish broader historical priority.

---

## Change: triangle-midpoints/midpoint-segment-relations

This node should be created because the midpoint-segment relations are a distinct reusable geometric lemma, meaningful independently of the contribution sequence. The standard midpoint theorem and its vector derivation belong in one stable node because they establish the same mathematical concept.

No separate node should be created for the transaction that supplied the vector calculation. The event remains provenance only.

**Provenance:**

- `sha256:575cfe733758035c57b6a7f7915c3e2a38a78c25f4b0c6ce026504546e4655ed` directly adjudicates the vector identities and their consequences.
- `sha256:427537f9898af49bb7e20230201f0ab01db5a51cccbfdb5b57c474e488b3a262` adjudicates the ordinary midpoint-theorem invocation as sufficient.

**Credit carried forward:**

The vector contribution is credited with clearly deriving the midpoint theorem in position-vector form. The judgment describes its value as expository and records that it appropriately disclaimed originality.

---

## Change: triangle-midpoints/altitude-scaling

This node should be created as the stable mathematical concept affected by the supplied correction. Its materialized content records the supported \(1/2\)-scaling relation and the refutation of equal-altitude reasoning; it is not titled or organized as a correction event.

The erroneous equal-altitude assertion should not receive its own parallel node because its only durable role is as a rejected alternative within the altitude-scaling concept. Nor should it become an active-dispute node: there is no supplied opposing judgment or unresolved reconciliation.

The node preserves the provenance uncertainty reported by the judgment. The mathematical statement was assessed, but the unavailable external report cannot be checked to confirm that it contained the attributed wording.

**Provenance:**

- `sha256:ae48d86e7bd2cdc4b6c2a708194553c6c8444c7f448bd73a82f8af95b64580c3`
- Subject transaction: `8bcf66bbd7777ee31f637a0a1a144535feb82ba4`

**Credit carried forward:**

The judgment credits Robert’s contribution with a valid and useful narrow correction that identifies the ancillary geometric error and replaces it with the homothety-based scaling relation. It also records the contribution’s disclaimer of any challenge to the main theorem or originality for the classical midpoint result.

---

## Change: triangle-midpoints/formal-verification

This node should be created as a durable verification-status concept rather than as a node for the paragraph or transaction that suggested formalization. It separates the established informal theorem from the unestablished claim of machine-checked verification.

The node does not assert that affine or determinant formalization has been completed. It preserves the judgments’ narrower assessment that these are plausible prospective approaches for which no artifact has been supplied.

**Provenance:**

- `sha256:427537f9898af49bb7e20230201f0ab01db5a51cccbfdb5b57c474e488b3a262`
- `sha256:575cfe733758035c57b6a7f7915c3e2a38a78c25f4b0c6ce026504546e4655ed`
- `sha256:ae48d86e7bd2cdc4b6c2a708194553c6c8444c7f448bd73a82f8af95b64580c3`

No conflict or reconciliation record bears on this status.
