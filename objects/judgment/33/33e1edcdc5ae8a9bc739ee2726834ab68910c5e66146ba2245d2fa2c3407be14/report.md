## `no-three-in-line-77/finite-rotation-classification-proof`

**Verdict: VALID**

### Required dependencies

**None.** The declared reference transaction  
`c98dd877ad81611a9a469b1bd790cd909b56b1ce` is retained as provenance and prior context, but its mathematical content is not required: the finite-rotation classification, orbit arguments, and occupancy argument are all independently supplied in the subject.

No objective attestation is present or needed; this is a purely deductive claim.

### Audit of the finite-rotation lemma

Let \(S\subset\mathbb Z^2\) be finite and noncollinear, and let the nonidentity rotation \(T\) preserve \(S\).

1. **Rationality of the linear part is established correctly.**
   - Noncollinearity supplies \(p_0,p_1,p_2\in S\) for which
     \[
     B=(p_1-p_0\;\;p_2-p_0)
     \]
     is a nonsingular integer matrix.
   - Since \(T(S)=S\), the corresponding image differences are integer vectors, so \(C\) is integer.
   - Translation cancels in differences, giving \(C=QB\), hence \(Q=CB^{-1}\).
   - Because \(B^{-1}\) has rational entries, \(Q\), and therefore \(c,s\), are rational. No assumption on the center is used.

2. **Finite order is justified.**
   - The bijection \(T:S\to S\) is a permutation of a finite set, so some \(T^m\) fixes every point of \(S\).
   - A Euclidean isometry fixing three noncollinear points is the identity. Thus \(T^m\) is globally the identity and \(Q^m=I\).

3. **The trace classification is complete.**
   - The eigenvalues of \(Q\) are roots of unity, so their sum \(t=\operatorname{tr}(Q)=2c\) is an algebraic integer.
   - Since \(Q\) is rational, \(t\in\mathbb Q\); hence \(t\in\mathbb Z\).
   - The bound \(|t|\le2\) gives \(t\in\{-2,-1,0,1,2\}\).
   - For \(t=\pm1\), \(c=\pm\frac12\) and \(s^2=\frac34\), contradicting the already established rationality of \(s\).
   - \(t=2\) gives \(Q=I\), hence the identity map, which is excluded.
   - \(t=-2\) gives a half-turn, while \(t=0\) gives a quarter-turn in one of the two orientations.

These cases exhaust all possibilities. The arbitrary-center finite-rotation lemma is therefore proved.

### Audit of the \(153\)-point consequence

A no-three-in-line set with at least three points cannot be collinear, so the lemma applies.

- Under a half-turn, all noncentral points lie in two-element orbits.
- An invariant set of odd cardinality must therefore contain the unique fixed point, namely the center.
- If any other point \(p\) is selected, then its opposite point is also selected, and those two points together with the center form three distinct collinear points.
- Thus an odd-cardinality half-turn-invariant no-three-in-line set has at most one point.

A quarter-turn has one possible fixed point and otherwise four-element orbits. If the center is selected, invariance under the square of the quarter-turn gives the same forbidden half-turn triple for every other point; otherwise the size is divisible by four. Hence a quarter-turn-invariant no-three-in-line set has size \(1\) or \(0\bmod 4\), with the size-\(1\bmod4\) case exceeding one impossible.

Therefore neither a half-turn nor a quarter-turn can preserve a \(153\)-point set. By the finite-rotation lemma, no other nonidentity rotation can do so.

### Audit of the \(154\)-point consequence

Quarter-turn symmetry is impossible because \(154\not\equiv0\pmod4\), and a selected center would force the set to have size one. Thus any nontrivial rotational symmetry must be a half-turn.

For a \(154\)-point no-three-in-line subset of \(G_{77}\):

- Every row contains at most two points.
- Since there are 77 rows and \(154=2\cdot77\), every row contains exactly two points.
- The identical argument for columns shows every column contains exactly two points.
- Consequently, points occur in both extreme rows and both extreme columns, so the coordinatewise bounding box is exactly \([0,76]^2\).

If a half-turn about \(z=(z_x,z_y)\) preserves a set whose coordinate extrema are \(0\) and \(76\), invariance of those extrema gives
\[
2z_x-76=0,\qquad 2z_y-76=0,
\]
so \(z=(38,38)\).

Finally, a half-turn-invariant finite set has cardinality equal to twice the number of noncentral orbits, plus one if the center is selected. Since \(154\) is even, the center is not selected. Equivalently, selection of the center together with any noncentral orbit would produce a forbidden collinear triple.

Thus the conditional \(154\)-point conclusion is established exactly as stated.

### Scope

The proof classifies rotations only. It establishes neither existence nor global nonexistence of \(153\)- or \(154\)-point configurations and does not improve the interval
\[
152\le D(77)\le154.
\]
