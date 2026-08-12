# Knowledge-Formation Report

The supplied judgments establish one durable research program concerning the area structure induced by the three side midpoints of a triangle. The organization below preserves the accepted Euclidean, vector, similarity, and homothety conclusions; records the corrected altitude relation; and keeps prospective formalization separate from established verification. No conflict records or reconciliation outcomes were supplied, so no active dispute node is required.

## Node: root

**Title:** Research state for triangle-midpoints  
**Type:** Root  
**Status:** Active  
**Parent:** None

The current knowledge state contains one established research program:

- [`triangle-midpoints/equal-area-program`](#node-triangle-midpointsequal-area-program) — the geometric and affine structure of the four triangles determined by the side midpoints of a nondegenerate triangle.

Within that program, the immutable judgments assess the following current state:

- The midpoint segments are parallel to and half the length of the corresponding sides of the original triangle.
- The medial triangle \(DEF\) and each corner triangle \(AEF\), \(BFD\), and \(CDE\) have area \([ABC]/4\).
- Consequently, the four small triangles have equal positive area under the problem’s nondegeneracy hypothesis.
- The altitude from a corner to the corresponding midpoint segment is half, not equal to, the altitude to the opposite side.
- Affine-invariance and determinant methods remain only prospective formalization directions; no formal statement, code, or machine-checked artifact has been supplied.

The supplied conflict records are empty, and no conflict is designated for preservation as an active dispute.

**Judgment provenance:**

- `sha256:427537f9898af49bb7e20230201f0ab01db5a51cccbfdb5b57c474e488b3a262`
- `sha256:575cfe733758035c57b6a7f7915c3e2a38a78c25f4b0c6ce026504546e4655ed`
- `sha256:ae48d86e7bd2cdc4b6c2a708194553c6c8444c7f448bd73a82f8af95b64580c3`

**Subject transactions:**

- `64afc12868e150370e6c56e6eeceab6b7aabe158`, ledger position 1
- `4ccbe3f18db7402d31a2ef795f6ad67962ff63e3`, ledger position 2
- `8bcf66bbd7777ee31f637a0a1a144535feb82ba4`, ledger position 3

## Change: root

The previous root reported that no research programs existed. The three supplied judgments now support a coherent, durable triangle-midpoint area program with an established theorem, supporting lemmas and methods, a corrected altitude relation, and a distinct uncompleted formalization direction.

## Node: triangle-midpoints/equal-area-program

**Title:** Triangle-midpoint area structure  
**Type:** Research program  
**Status:** Active  
**Parent:** `root`

This program studies the geometric and affine consequences of taking \(D\), \(E\), and \(F\) as the midpoints of \(BC\), \(CA\), and \(AB\) in a nondegenerate triangle \(ABC\).

The program’s established ordinary-mathematical knowledge consists of:

1. **Midpoint-segment geometry.** The segments \(DE\), \(EF\), and \(FD\) are respectively parallel to \(AB\), \(BC\), and \(CA\), and each has half the corresponding side length.
2. **Medial-triangle area.** The triangle \(DEF\) is similar to \(ABC\) with linear factor \(1/2\), and therefore has area \([ABC]/4\).
3. **Corner-triangle areas.** Each of \(AEF\), \(BFD\), and \(CDE\) is a half-scale copy of the original triangle in the appropriate vertex correspondence, and each has area \([ABC]/4\).
4. **Altitude scaling.** Under the corner homothety with factor \(1/2\), the relevant base and point-to-line altitude both scale by \(1/2\). Parallelism alone does not make the two altitudes equal.
5. **Equal-area theorem.**
   \[
   [AEF]=[BFD]=[CDE]=[DEF]=\frac14[ABC].
   \]
   The judgments assess the ordinary Euclidean proof as complete and the main problem as fully solved with high or very high confidence.
6. **Formalization status.** Affine or determinant approaches are considered plausible for a future Lean formalization, but no formal verification has been established.

The program contains no supplied active mathematical dispute. The refuted equal-altitude explanation is not supported by an opposing supplied primary judgment; the current judged relation is the \(1:2\) altitude ratio.

**Program nodes:**

- `triangle-midpoints/midpoint-segment-relations`
- `triangle-midpoints/medial-triangle-quarter-area`
- `triangle-midpoints/corner-triangles-quarter-area`
- `triangle-midpoints/corner-altitude-scaling`
- `triangle-midpoints/equal-area-theorem`
- `triangle-midpoints/formalization-status`

**Credit carried from the judgments:**

- Judgment `sha256:427537...` credits Robert’s transaction with a concise and complete proof using the midpoint theorem, similarity, and area scaling.
- Judgment `sha256:575cfe...` characterizes transaction `4ccbe3...` as a clear explanatory supplement deriving the midpoint theorem through position vectors. It does not credit that transaction with a new theorem or novel method and notes its disclaimer of originality.
- Judgment `sha256:ae48d8...` credits Robert’s subject transaction with a valid and useful narrow repair of an ancillary base-height explanation. It does not infer broader historical priority and records the contribution’s disclaimer of originality for the classical midpoint result.

**Evidence:** All three immutable judgments and their three subject transactions listed at the root.

## Change: triangle-midpoints/equal-area-program

This program is created because the judged theorem, its midpoint and homothety lemmas, and the prospective formalization direction form one enduring mathematical agenda. They are organized together rather than as transaction-shaped nodes, and no separate formalization program is created because formal verification remains only a proposed direction.

## Node: triangle-midpoints/midpoint-segment-relations

**Title:** Parallelism and half-length relations for triangle midpoint segments  
**Type:** Lemma  
**Status:** Established  
**Parent:** `triangle-midpoints/equal-area-program`

For the side midpoints

\[
D=\frac{B+C}{2},\qquad
E=\frac{C+A}{2},\qquad
F=\frac{A+B}{2},
\]

judgment `sha256:575cfe...` accepts the position-vector identities

\[
E-F=\frac{C-B}{2},\qquad
F-D=\frac{A-C}{2},\qquad
D-E=\frac{B-A}{2}.
\]

The judgment concludes that these identities establish

\[
EF\parallel BC,\qquad
FD\parallel CA,\qquad
DE\parallel AB,
\]

and

\[
|EF|=\frac12|BC|,\qquad
|FD|=\frac12|CA|,\qquad
|DE|=\frac12|AB|.
\]

Changing endpoint order may change a vector’s sign, but the judgment notes that this does not affect parallelism or length. The same relations are also accepted in judgment `sha256:427537...` through the standard midpoint theorem.

This lemma supplies the side correspondences used in the medial-triangle similarity result and provides an explicit vector derivation of the geometric midpoint theorem invoked by the original Euclidean proof.

**Assessment carried from the judgments:** Correct, decisive, and supported with very high confidence. The vector derivation is an explanatory supplement rather than a repair of an invalid earlier proof.

**Provenance:**

- Primary judgment: `sha256:575cfe733758035c57b6a7f7915c3e2a38a78c25f4b0c6ce026504546e4655ed`
- Corroborating judgment: `sha256:427537f9898af49bb7e20230201f0ab01db5a51cccbfdb5b57c474e488b3a262`
- Subject and direct evidence transaction: `4ccbe3f18db7402d31a2ef795f6ad67962ff63e3`
- Additional evidence transaction: `64afc12868e150370e6c56e6eeceab6b7aabe158`

## Change: triangle-midpoints/midpoint-segment-relations

This lemma is materialized as a distinct durable concept because the vector identities independently establish the midpoint-segment geometry used by several area arguments. The cited judgment specifically distinguishes this derivation from the transaction event that supplied it.

## Node: triangle-midpoints/medial-triangle-quarter-area

**Title:** Area of the medial triangle  
**Type:** Result  
**Status:** Established  
**Parent:** `triangle-midpoints/equal-area-program`

The immutable judgments conclude that the three sides of \(DEF\) have half the lengths of the corresponding sides of \(ABC\):

\[
|DE|=\frac12|AB|,\qquad
|EF|=\frac12|BC|,\qquad
|FD|=\frac12|CA|.
\]

Judgments `sha256:427537...` and `sha256:575cfe...` therefore accept that \(DEF\) is similar to \(ABC\) with linear scale factor \(1/2\), whether similarity is justified through SSS or through the corresponding parallel lines. Applying the accepted area-scaling law for similar triangles gives

\[
[DEF]=\left(\frac12\right)^2[ABC]
     =\frac14[ABC].
\]

The standard midpoint-theorem invocation is judged sufficient for an ordinary Euclidean proof. The later vector derivation makes the underlying half-length and parallelism relations explicit but is not judged necessary to repair the earlier proof.

**Assessment carried from the judgments:** Correct and complete, with high to very high confidence.

**Credit carried from the judgments:** Judgment `sha256:427537...` credits Robert’s contribution with the concise midpoint-theorem and similarity proof. Judgment `sha256:575cfe...` credits transaction `4ccbe3...` with an explicit algebraic derivation of the supporting midpoint facts, while characterizing it as an explanatory supplement rather than a novel theorem or proof method.

**Provenance:**

- Judgments:
  - `sha256:427537f9898af49bb7e20230201f0ab01db5a51cccbfdb5b57c474e488b3a262`
  - `sha256:575cfe733758035c57b6a7f7915c3e2a38a78c25f4b0c6ce026504546e4655ed`
- Evidence transactions:
  - `64afc12868e150370e6c56e6eeceab6b7aabe158`
  - `4ccbe3f18db7402d31a2ef795f6ad67962ff63e3`

## Change: triangle-midpoints/medial-triangle-quarter-area

This result is created separately from the midpoint-segment lemma because it records the durable area consequence of the accepted half-scale similarity, rather than the underlying segment relations themselves.

## Node: triangle-midpoints/corner-triangles-quarter-area

**Title:** Areas of the three corner midpoint triangles  
**Type:** Result  
**Status:** Established  
**Parent:** `triangle-midpoints/equal-area-program`

The supplied judgments establish

\[
[AEF]=[BFD]=[CDE]=\frac14[ABC].
\]

They accept several compatible ordinary-mathematical justifications:

- For \(AEF\),
  \[
  AE=\frac12 AC,\qquad AF=\frac12 AB,
  \]
  while \(\angle EAF=\angle CAB\). The included-angle area formula therefore gives \([AEF]=[ABC]/4\).
- The corresponding half-length relations also give an SSS similarity between each corner triangle and the appropriately ordered original triangle, with scale factor \(1/2\).
- Equivalently, the factor-\(1/2\) homothety centered at each vertex maps the original triangle to its corresponding corner triangle.
- A base-height proof is valid when both the midpoint base and its corresponding altitude are scaled by \(1/2\).

The judgments accept the cyclic extension to \(BFD\) and \(CDE\) as direct and unambiguous. They treat the use of “cyclically” as an expository compression, not a missing substantive lemma.

Under the problem’s nondegeneracy assumption, all three corner triangles have positive unsigned area. Judgment `sha256:575cfe...` additionally observes that the vector relations would produce equal zero areas in a degenerate extension, but the supplied proof is not required to address that extension.

**Assessment carried from the judgments:** Correct and complete, with high to very high confidence.

**Provenance:**

- Judgments:
  - `sha256:427537f9898af49bb7e20230201f0ab01db5a51cccbfdb5b57c474e488b3a262`
  - `sha256:575cfe733758035c57b6a7f7915c3e2a38a78c25f4b0c6ce026504546e4655ed`
  - `sha256:ae48d86e7bd2cdc4b6c2a708194553c6c8444c7f448bd73a82f8af95b64580c3`
- Evidence transactions:
  - `64afc12868e150370e6c56e6eeceab6b7aabe158`
  - `4ccbe3f18db7402d31a2ef795f6ad67962ff63e3`
  - `8bcf66bbd7777ee31f637a0a1a144535feb82ba4`

## Change: triangle-midpoints/corner-triangles-quarter-area

This result is created as the stable home for the accepted quarter-area conclusions for all three corner triangles. It consolidates the included-angle, similarity, homothety, and corrected base-height routes without treating any contributing transaction as a knowledge node.

## Node: triangle-midpoints/corner-altitude-scaling

**Title:** Altitude scaling under the corner midpoint homothety  
**Type:** Lemma and method constraint  
**Status:** Established  
**Parent:** `triangle-midpoints/corner-triangles-quarter-area`

For the factor-\(1/2\) homothety centered at \(A\) that sends \(B\) to \(F\) and \(C\) to \(E\), judgment `sha256:ae48d8...` concludes that the line \(BC\) maps to the line \(FE\) and that point-to-line distances scale by \(1/2\). Thus

\[
\operatorname{dist}(A,\overleftrightarrow{EF})
=
\frac12\operatorname{dist}(A,\overleftrightarrow{BC}).
\]

Cyclically, the corresponding altitude relation holds at vertices \(B\) and \(C\).

The same judgment refutes the assertion that the altitudes from \(A\) to \(EF\) and \(BC\) are equal merely because the lines are parallel. Its accepted relation is a distance ratio of \(1:2\), not equality. Accordingly, the accepted base-height computation uses

\[
|EF|=\frac12|BC|
\]

and an altitude to \(EF\) equal to half the altitude to \(BC\), so both factors scale by \(1/2\).

The nondegeneracy hypothesis ensures that the relevant altitudes are nonzero. The judgment states that the scaling identity itself remains formally meaningful without that positivity.

This rejected equal-altitude explanation does not undermine the earlier midpoint, similarity, or included-angle arguments. The judgment reports that the erroneous assertion does not occur in the two supplied earlier contribution artifacts.

**Provenance limitation:** The external report allegedly containing the equal-altitude assertion was identified only by a digest and was not supplied. Judgment `sha256:ae48d8...` therefore does not verify that the quoted wording actually appeared in that report or whether it had qualifying context. This limitation concerns attribution only; the judgment nevertheless assesses the quoted mathematical assertion as false and the \(1/2\)-scaling relation as correct with high confidence.

**Credit carried from the judgment:** Robert’s subject transaction is credited with a valid and useful narrow repair of an ancillary base-height explanation. The judgment does not assign broader historical priority and records the contribution’s disclaimer of originality.

**Provenance:**

- Primary judgment: `sha256:ae48d86e7bd2cdc4b6c2a708194553c6c8444c7f448bd73a82f8af95b64580c3`
- Subject and direct evidence transaction: `8bcf66bbd7777ee31f637a0a1a144535feb82ba4`
- Context transactions:
  - `64afc12868e150370e6c56e6eeceab6b7aabe158`
  - `4ccbe3f18db7402d31a2ef795f6ad67962ff63e3`

## Change: triangle-midpoints/corner-altitude-scaling

This node is created beneath the corner-area result because the judged altitude ratio is a reusable geometric lemma and a necessary constraint on the base-height method. It also preserves the judgment’s attribution limitation without creating an unsupported conflict or report-shaped node.

## Node: triangle-midpoints/equal-area-theorem

**Title:** Equal-area theorem for the four midpoint triangles  
**Type:** Theorem  
**Status:** Established  
**Parent:** `triangle-midpoints/equal-area-program`

For a nondegenerate triangle \(ABC\), with \(D\), \(E\), and \(F\) the midpoints of \(BC\), \(CA\), and \(AB\), respectively, the immutable judgments establish

\[
[AEF]=[BFD]=[CDE]=[DEF]=\frac14[ABC].
\]

The medial-triangle conclusion follows from its accepted half-scale similarity to \(ABC\). The three corner conclusions follow from the accepted included-angle, similarity, or homothety arguments. The corrected base-height argument is also valid when both the base and altitude are scaled by \(1/2\).

Judgment `sha256:427537...` states that no separate partition argument is required because every small triangle is independently shown to have one quarter of the total area. It therefore finds no circularity. Judgments `sha256:427537...` and `sha256:ae48d8...` assess the main problem as fully solved, with a complete ordinary mathematical proof and high confidence. Judgment `sha256:575cfe...` likewise assesses the combined elementary proof as complete with very high confidence.

The nondegeneracy assumption gives \([ABC]>0\) and makes the four asserted equal areas positive. The vector judgment observes that a degenerate extension would yield equal zero areas, but no such extension is required by the problem.

The theorem’s ordinary mathematical status is independent of the absence of a machine-checked formalization.

**Provenance:**

- Judgments:
  - `sha256:427537f9898af49bb7e20230201f0ab01db5a51cccbfdb5b57c474e488b3a262`
  - `sha256:575cfe733758035c57b6a7f7915c3e2a38a78c25f4b0c6ce026504546e4655ed`
  - `sha256:ae48d86e7bd2cdc4b6c2a708194553c6c8444c7f448bd73a82f8af95b64580c3`
- Evidence transactions:
  - `64afc12868e150370e6c56e6eeceab6b7aabe158`
  - `4ccbe3f18db7402d31a2ef795f6ad67962ff63e3`
  - `8bcf66bbd7777ee31f637a0a1a144535feb82ba4`

## Change: triangle-midpoints/equal-area-theorem

This theorem node is created as the stable home for the central result independently supported by all three judgments. It records the complete current theorem status while leaving its component lemmas and proof methods in their own durable nodes.

## Node: triangle-midpoints/formalization-status

**Title:** Formalization status and prospective affine methods  
**Type:** Research direction and verification status  
**Status:** Open  
**Parent:** `triangle-midpoints/equal-area-program`

Affine invariance and determinant calculations are judged mathematically plausible approaches for a future Lean formalization of the triangle-midpoint equal-area theorem.

No supplied evidence contains:

- a formal theorem statement,
- Lean or other proof-assistant code,
- a machine-checked proof artifact, or
- independent formal-verification output.

Accordingly, the immutable judgments support only the completed ordinary Euclidean and vector mathematics, not a claim of completed formal verification. The absence of a formal artifact does not weaken the judgments’ assessment that the elementary paper proof is correct and complete.

This node records a prospective direction rather than an established formal result. No separate formalization research program is established by the available evidence.

**Provenance:**

- Judgment `sha256:427537f9898af49bb7e20230201f0ab01db5a51cccbfdb5b57c474e488b3a262`, qualifying finding on affine invariance or determinants
- Judgment `sha256:575cfe733758035c57b6a7f7915c3e2a38a78c25f4b0c6ce026504546e4655ed`, confirmation that no Lean artifact or formal verification was supplied
- Judgment `sha256:ae48d86e7bd2cdc4b6c2a708194553c6c8444c7f448bd73a82f8af95b64580c3`, confirmation that the earlier formalization mention remains only a proposal
- Evidence transactions:
  - `64afc12868e150370e6c56e6eeceab6b7aabe158`
  - `4ccbe3f18db7402d31a2ef795f6ad67962ff63e3`
  - `8bcf66bbd7777ee31f637a0a1a144535feb82ba4`

## Change: triangle-midpoints/formalization-status

This node is created to preserve the judgments’ explicit distinction between a plausible future formalization route and completed machine verification. It remains within the established program because the evidence does not support an independent formalization program or a verified formal result.
