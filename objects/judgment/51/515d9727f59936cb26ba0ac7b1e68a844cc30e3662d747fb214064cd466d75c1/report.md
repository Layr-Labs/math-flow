## Claim: `no-three-in-line-77/finite-rotation-classification-proof`

**Verdict: Valid**

### Finite-rotation lemma

The proof establishes the exact stated lemma.

1. **Rationality of the linear part.**  
   For noncollinear \(p_0,p_1,p_2\in S\), the matrix
   \[
   B=(p_1-p_0\;\;p_2-p_0)
   \]
   is an invertible integer matrix. Since \(T(S)=S\subset\mathbb Z^2\), the corresponding image-difference matrix \(C\) is also integral. Translation cancels, giving
   \[
   C=QB,\qquad Q=CB^{-1}.
   \]
   Thus \(Q\in M_2(\mathbb Q)\), so both \(c\) and \(s\) are rational. This does not require the rotation center to lie in \(\mathbb Z^2\).

2. **Finite order.**  
   Because \(T\) permutes the finite set \(S\), some \(T^m\) fixes every point of \(S\). An isometry fixing three noncollinear points is the identity, so \(T^m=\mathrm{id}\), and consequently \(Q^m=I\).

3. **Classification of possible angles.**  
   The eigenvalues of \(Q\) are roots of unity. Hence
   \[
   t=\operatorname{tr}(Q)=2c
   \]
   is an algebraic integer. Since \(Q\) is rational, \(t\in\mathbb Q\), so \(t\in\mathbb Z\). The bound \(|t|\le 2\) leaves
   \[
   t\in\{-2,-1,0,1,2\}.
   \]
   The cases \(t=\pm1\) force \(s^2=3/4\), contradicting \(s\in\mathbb Q\). The case \(t=2\) gives \(Q=I\), hence the identity rotation, which is excluded. The remaining cases are:
   - \(t=-2\): \(Q=-I\), a half-turn;
   - \(t=0\): \(Q\) is rotation through \(90^\circ\) or \(270^\circ\).

   These exhaust all possibilities.

### Application to cardinality \(153\)

A no-three-in-line set with at least three points is necessarily noncollinear, so the lemma applies.

- Under a half-turn, all noncentral points occur in pairs, while the center is the unique possible fixed point. Odd cardinality forces the center to be selected. If any other point \(p\) is selected, then \(p\), the center, and its opposite point are three distinct collinear selected points. Thus an odd half-turn-invariant no-three-in-line set has size at most one.
- Under a quarter-turn, noncentral orbits have size four. If the center is absent, cardinality is divisible by four. If the center is present, invariance under the square of the rotation gives the same collinear-triple obstruction, so the set has size at most one.

Therefore cardinality \(153\) admits neither a half-turn nor a quarter-turn. By the finite-rotation lemma, it admits no nonidentity rotational symmetry.

### Application to cardinality \(154\)

Quarter-turn symmetry is impossible because \(154\not\equiv0\pmod4\), and selecting the center would force size at most one. Hence any nontrivial rotational symmetry must be a half-turn.

Every row contains at most two selected points. Since there are 77 rows and \(154=2\cdot77\), every row contains exactly two points. The identical argument for columns shows every column contains exactly two points. Thus the coordinatewise minima and maxima are \(0\) and \(76\) in both coordinates.

If a half-turn about \(z=(z_x,z_y)\) preserves \(S\), it preserves its coordinatewise bounding box. For the \(x\)-range this gives
\[
[0,76]=[2z_x-76,\,2z_x],
\]
so \(z_x=38\); similarly \(z_y=38\). Hence the half-turn is about \((38,38)\).

Finally, a half-turn-invariant finite set has even cardinality precisely when its unique fixed point—the center—is absent. Since \(|S|=154\), it follows that
\[
(38,38)\notin S.
\]

### Scope and evidence

- The argument classifies rotations only; it does not address reflections or other transformations.
- It is conditional at size \(154\) and supplies no \(153\)- or \(154\)-point configuration.
- It does not improve \(152\le D(77)\le154\).
- No objective attestations were supplied. The repository commands listed in the contribution are not execution evidence, but none is needed because the claim is established by the self-contained mathematical proof.

### Dependencies

**Required dependencies: none.**

Declared reference transaction `c98dd877ad81611a9a469b1bd790cd909b56b1ce` is a provenance and prior-context reference, not a logical dependency: all orbit, parity, occupancy, and bounding-box arguments needed for this claim are independently restated and justified in the subject.
