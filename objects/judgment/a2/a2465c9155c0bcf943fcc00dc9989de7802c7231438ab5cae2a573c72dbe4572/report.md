## `bssc-sum-capacity/two-letter-padding-correlation-tests`

**Verdict: valid**

### Required dependency

- `5ed3f525b9ae7f32c6e1dcbf22ecdb5ae946a4a6` — **required and satisfied**.

The subject materially uses two results from this reference:

1. For receiver-skew \(T\),
   \[
   M_T=L_{1/2,T}.
   \]
2. For an arbitrary chosen tuple decomposition, the exact residual identity
   \[
   L_{1/2,T^{\otimes n}}(P)-\sum_iL_{1/2,T}(P^{(i)})
   \]
   equals the stated total-correlation ledger, and a Marton value above \(nM_T\) makes this residual strictly positive.

The reference proves both internally. Its midpoint proof uses receiver-skew reflection and fair-selector symmetrization without assuming attainment. Its entropy expansion establishes the residual identity. No additional declared dependency is needed for the present claim.

### Audit of the gain-to-residual implication

For any two-letter law \(P\),
\[
M_{T^{\otimes2}}(P)\le L_{1/2,T^{\otimes2}}(P)
\]
because \(\min\{I(W;Y^2),I(W;Z^2)\}\) is at most their average.

For each padded coordinate marginal \(P_i^{(a,b)}\), the product channel ensures
\[
(W,U_i,V_i)-X_i-(Y_i,Z_i),
\]
so it is an admissible one-letter Marton law. Receiver skew and the reference's midpoint identity give
\[
L_{1/2,T}(P_i^{(a,b)})\le L_{1/2,T}=M_T.
\]
Consequently,
\[
M_{T^{\otimes2}}(P)>2M_T
\]
implies, for every padding choice,
\[
L_{1/2,T^{\otimes2}}(P)
-\sum_{i=1}^2L_{1/2,T}(P_i^{(a,b)})>0.
\]
The strictness is justified: the first term is strictly above \(2M_T\), while the coordinate sum is at most \(2M_T\).

### Audit of the four constant paddings

For \(a\in\{1,2\}\), set \(U_a=U\) and the other \(U\)-coordinate constant. Then
\[
\operatorname{TC}(U_1,U_2\mid W)=0.
\]

For \(a=1\),
\[
\begin{aligned}
G_{UY}
&=H(Y_1\mid U,W)+H(Y_2\mid W)-H(Y_1,Y_2\mid U,W)\\
&=I(Y_2;Y_1,U\mid W)=A_1.
\end{aligned}
\]
For \(a=2\), the symmetric calculation gives \(G_{UY}=A_2\). The corresponding \(V,Z\) calculations give \(G_{VZ}=B_b\).

For the penalty gap:

- If \(a=b\), the nonconstant \(U,V\) occupy the same coordinate, so
  \[
  G_{UV}=0.
  \]
- If \(a\ne b\), they occupy different coordinates, and
  \[
  G_{UV}=H(U\mid W)-H(U\mid V,W)=I(U;V\mid W)=D.
  \]

For two coordinates,
\[
\operatorname{TC}(Y_1,Y_2\mid W)=I(Y_1;Y_2\mid W),
\qquad
\operatorname{TC}(Y_1,Y_2)=I(Y_1;Y_2),
\]
and likewise for \(Z\). Thus the reference residual specializes exactly to
\[
L_{1/2,T^{\otimes2}}(P)-\sum_iL_{1/2,T}(P_i^{(a,b)})
=A_a+B_b-\mathbf1\{a\ne b\}D-C.
\]

Since the left side is positive under a strict gain, all four claimed tests follow:
\[
A_a+B_b>C+\mathbf1\{a\ne b\}D.
\]

The equivalent minimum formulation is algebraically correct. Its contrapositive also justifies that equality or failure of any one strict inequality rules out a strict gain.

### Audit of the combined crossed test

The chain-rule identities are correct:
\[
\begin{aligned}
A_1+A_2
&=2I(Y_1;Y_2\mid W)
 +I(U;Y_2\mid Y_1,W)+I(U;Y_1\mid Y_2,W),\\
B_1+B_2
&=2I(Z_1;Z_2\mid W)
 +I(V;Z_2\mid Z_1,W)+I(V;Z_1\mid Z_2,W).
\end{aligned}
\]

Adding the two crossed inequalities gives
\[
A_1+A_2+B_1+B_2>2C+2D.
\]
Substitution and cancellation produce README equation (12) exactly. As stated, this summed condition is weaker than retaining the two crossed tests separately and remains necessary only.

### Coverage and edge cases

- Every finite abstract \(U,V\) admits each padded tuple representation \((U,\mathrm{const})\) or \((\mathrm{const},U)\), and similarly for \(V\). No original tuple or product structure is assumed.
- Constant or degenerate auxiliaries and zero-probability symbols cause no problem; all identities remain valid under the usual finite-alphabet entropy conventions.
- The half-skew BSSC is receiver-skew under input bit flip and output bit flips, so the general result applies.
- The result does not assert sufficiency, additivity, existence of a gaining law, or a capacity value.

### Objective attestations

The subject attestation establishes that the supplied Python checker completed successfully and numerically verified the four residual identities and crossed chain-rule identity for one fixed correlated rational base law, using floating-point logarithms and stated tolerances. The negative residuals printed for two paddings are not counterexamples because the tested law was not asserted to have a strict gain.

The reference attestation similarly checks fixed finite examples and the exact rational BSSC relabeling. Neither execution exhausts arbitrary finite laws or proves the universal implication. They are corroborative only; validity rests on the supplied analytic entropy argument and the verified reference proof.
