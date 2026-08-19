## `no-three-in-line-77/finite-rotation-classification-proof`

**Verdict: valid**

### Finite-rotation lemma

The proof establishes every required step.

1. **Rationality of the linear part.**  
   Noncollinearity supplies \(p_0,p_1,p_2\in S\) such that
   \[
   B=(p_1-p_0\;\;p_2-p_0)
   \]
   is a nonsingular integer matrix. Since \(T(S)=S\subset\mathbb Z^2\), the corresponding image-difference matrix \(C\) is also integral. The identity
   \[
   C=QB
   \]
   follows because the rotational center and translational terms cancel in differences. Hence
   \[
   Q=CB^{-1}\in M_2(\mathbb Q),
   \]
   so both \(c\) and \(s\) are rational. No lattice condition on the center is used.

2. **Finite order.**  
   Because \(T\) bijectively preserves finite \(S\), its restriction to \(S\) is a permutation. Thus some \(T^m\) fixes every point of \(S\). An Euclidean isometry fixing three noncollinear points is the identity, so \(T^m\) is the identity map and \(Q^m=I\).

3. **Classification of possible traces.**  
   The eigenvalues of finite-order \(Q\) are roots of unity. Therefore
   \[
   t=\operatorname{tr}(Q)=2c
   \]
   is an algebraic integer. Since \(Q\) is rational, \(t\in\mathbb Q\), and hence \(t\in\mathbb Z\). The rotation condition gives \(|t|\le2\), so
   \[
   t\in\{-2,-1,0,1,2\}.
   \]
   The cases \(t=\pm1\) imply \(c=\pm\frac12\) and \(s^2=\frac34\), contradicting \(s\in\mathbb Q\). The case \(t=2\) gives \(c=1,s=0\), hence the identity rotation, which is excluded. The remaining cases are:
   - \(t=-2\): \(c=-1,s=0\), a half-turn;
   - \(t=0\): \(c=0,s=\pm1\), a quarter-turn in either orientation.

   Thus the exact finite-rotation lemma follows.

### Application to cardinality \(153\)

A no-three-in-line set with more than two points is necessarily noncollinear, so the lemma applies.

- Under a half-turn, every noncentral point lies in a two-point orbit. An invariant set of odd cardinality must therefore contain the unique fixed point, namely the center. If any other point \(p\) is selected, then \(p\), the center, and its opposite image are three distinct collinear selected points. Hence an odd-cardinality half-turn-invariant no-three-in-line set has at most one point.
- Under a quarter-turn, every noncentral orbit has size four. If the center is absent, cardinality is divisible by four. If the center is present, invariance under the square of the quarter-turn gives the same forbidden collinear triple with every noncentral point, so the set has size at most one.

Therefore neither a half-turn nor a quarter-turn can preserve a 153-point no-three-in-line set. By the finite-rotation lemma, no other nonidentity rotation is possible. Consequence 1 is proved.

### Application to cardinality \(154\)

Quarter-turn symmetry is impossible because \(154\not\equiv0\pmod4\), while selecting the center would force the set to have size at most one. Thus any nontrivial rotational symmetry must be a half-turn.

For a 154-point subset of \(G_{77}\):

- each of the 77 rows contains at most two points, and their occupancies sum to \(154\), so every row contains exactly two points;
- the identical argument applies to columns.

Consequently the coordinate extrema are \(0\) and \(76\) in both coordinates, so the coordinatewise bounding box is exactly \([0,76]^2\). A half-turn preserving the set preserves this bounding box. If its center is \(z=(z_x,z_y)\), preservation of the extrema gives
\[
2z_x=0+76,\qquad 2z_y=0+76,
\]
hence \(z=(38,38)\).

Finally, the center cannot be selected: a half-turn-invariant finite set containing its unique fixed point has odd cardinality, since all other orbits have size two. This contradicts \(|S|=154\). Thus \((38,38)\notin S\).

Consequence 2 is therefore proved with the stated scope. The argument concerns rotations only and does not establish existence or nonexistence of 153- or 154-point configurations, so it does not change the certified interval for \(D(77)\).
