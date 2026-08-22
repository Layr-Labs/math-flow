## `bssc-sum-capacity/conditional-product-marton-no-gain`

**Verdict: valid**

### 1. Receiver-skew midpoint identity

The proof correctly establishes
\[
M_T=L_{1/2,T}
\]
without relying on the externally mentioned max–min theorem.

For any candidate law, receiver-skew reflection exchanges
\[
I(W;Y)\leftrightarrow I(W;Z),\qquad
I(U;Y\mid W)\leftrightarrow I(V;Z\mid W),
\]
while preserving \(I(U;V\mid W)\). The input involution and bijective output relabelings are sufficient for these identities; no property of the joint \(Y,Z\) coupling is needed.

Mixing a law and its reflection with a fair branch variable included in the common auxiliary gives both common-information terms at least \((a+b)/2\), while the satellite term remains exactly \(S\). Hence every value of \(L_{1/2,T}\) is bounded above by an attainable Marton value after symmetrization. Together with the pointwise inequality
\[
\min\{a,b\}\le \frac{a+b}{2},
\]
this proves equality of the suprema. Tagged branch alphabets handle unequal \(U,V\) alphabets, and the argument uses an arbitrary candidate rather than an optimizer.

For the displayed half-skew BSSC, \(s(x)=1-x\) and output bit flips indeed satisfy the stated receiver-skew equations.

### 2. Conditional-product upper bound

Under
\[
P(w,u^n,v^n,x^n)=P(w)\prod_i P_i(u_i,v_i,x_i\mid w),
\]
the coordinate packets and channel outputs are independent across coordinates conditional on \(W=w\). Therefore the three satellite terms add exactly:
\[
\begin{aligned}
I(U^n;Y^n\mid W)&=\sum_i I(U_i;Y_i\mid W),\\
I(V^n;Z^n\mid W)&=\sum_i I(V_i;Z_i\mid W),\\
I(U^n;V^n\mid W)&=\sum_i I(U_i;V_i\mid W).
\end{aligned}
\]

Conditional output independence also gives
\[
I(W;Y^n)\le \sum_i I(W;Y_i),\qquad
I(W;Z^n)\le \sum_i I(W;Z_i).
\]
Combining these with \(\min\{a,b\}\le(a+b)/2\) bounds the \(n\)-letter functional by a sum of \(n\) one-letter \(L_{1/2,T}\) functionals. Each coordinate marginal obeys
\[
(W,U_i,V_i)-X_i-(Y_i,Z_i),
\]
so each summand is at most \(L_{1/2,T}=M_T\). Thus the conditional-product supremum is at most \(nM_T\).

### 3. Reverse inequality and nonattainment

Taking \(n\) independent copies of an \(\varepsilon\)-optimal one-letter law produces an admissible conditional-product law with aggregate
\[
W=(W_1,\ldots,W_n).
\]
All common and satellite mutual informations are additive, including the minimum because the copies are identical. Hence its value is \(nM_T(P^*)>nM_T-n\varepsilon\). Letting \(\varepsilon\downarrow0\) proves the reverse inequality without assuming attainment.

Consequently,
\[
\sup_{\text{conditional-product laws}}M_{T^{\otimes n}}=nM_T.
\]

### 4. Correlated tuple-law identity

For an arbitrary tuple law followed by the product channel, each coordinate marginal remains a valid one-letter Marton law: although \(X_i\) may be globally coupled with other coordinates, the memoryless channel ensures
\[
(W,U_i,V_i)-X_i-(Y_i,Z_i).
\]

Direct entropy expansion verifies the three component identities used in equation (11):

\[
I(W;Y^n)-\sum_i I(W;Y_i)
=\operatorname{TC}(Y^n\mid W)-\operatorname{TC}(Y^n),
\]

\[
I(U^n;Y^n\mid W)-\sum_i I(U_i;Y_i\mid W)
=-\operatorname{TC}(Y^n\mid W)+G_{UY},
\]

and
\[
-I(U^n;V^n\mid W)+\sum_i I(U_i;V_i\mid W)
=\operatorname{TC}(U^n\mid W)-G_{UV},
\]
with the analogous \(Z\) identity. Their weighted sum is exactly README equation (11), with the stated signs.

The asserted gap nonnegativity is also justified. For example,
\[
H(Y^n\mid U^n,W)
\le \sum_i H(Y_i\mid U^n,W)
\le \sum_i H(Y_i\mid U_i,W),
\]
and the same argument applies to \(G_{VZ}\) and \(G_{UV}\).

If a tuple law has Marton value exceeding \(nM_T\), then its affine midpoint value also exceeds \(nM_T\), whereas the sum of its coordinate midpoint functionals is at most \(nM_T\). Thus the residual in equation (11) is strictly positive, yielding precisely inequality (13). This is correctly stated only as a necessary condition.

Trivial constant padding does supply a tuple representation of arbitrary finite auxiliaries, while the individual ledger terms legitimately depend on the chosen, noncanonical decomposition.

### 5. Scope of the consequence

Any particular gaining law with value \(>nM_T\) cannot satisfy the conditional-product factorization under any exact coordinate decomposition for which the theorem applies; otherwise the proved upper bound would contradict the gain. The submission correctly avoids extending this to unrestricted Marton additivity, binary-input tightness, or broadcast-channel capacity.

### 6. Objective attestation

The terminal attestation establishes that the pinned Python program exited successfully and, for its fixed tests:

- checked the BSSC relabeling using exact rational channel entries;
- checked entropy identities and inequalities on finitely many floating-point conditional-product examples;
- checked equation (11) on finitely many two-letter correlated examples;
- checked one independent-copy example.

The floating-point, fixed-seed tests do **not** certify the universal theorem or arbitrary alphabets and do not justify the phrase “exact ledger” beyond those sampled computations. This does not create a gap because the universal claims are independently established by the analytic entropy proof.

**Required dependencies:** none. The external results discussed in the README are contextual and are not needed for the declared claim.
