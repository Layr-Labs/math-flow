## `bssc-sum-capacity/fixed-pair-upper-bound-attested`

**Verdict: indeterminate**

The symbolic structure of the proposed converse certificate is coherent, but the supplied evidence does not include a successful execution attestation or a complete static interval trace. Several essential numerical inequalities therefore remain unverified.

### 1. Use of the declared dependency

The claim is explicitly conditional on the encoded Gohari–Liu–Nair Theorem 9 premise. Under the sole dependency, one has

\[
C_{\mathrm{sum}}\le \inf_{G,K} B(G,K),
\]

and hence, for the fixed binary receivers used here,

\[
C_{\mathrm{sum}}\le B(G,K).
\]

This inference has the correct direction and does not require receiver optimality. The contribution appropriately does not claim to authenticate or re-prove Theorem 9.

The six selected rows agree with the displayed dependency rows:

- `R1A(1)`,
- `R2T(1)`,
- `SR(1,C)`,
- `SL(2,U)`,
- `SR(2,U)`,
- `F_Y_right_minus_left`.

In particular, the last row has the correct orientation \(0\le\text{right}-\text{left}\), so multiplying it by a nonnegative dual weight and adding it to the rate inequalities is legitimate.

### 2. Exact dual combination

Let \(e=\epsilon\). The six weights are

\[
e,\ e,\ e,\ \frac12-\frac e2,\ \frac12-\frac{3e}{2},\ e.
\]

They are nonnegative, and direct calculation gives coefficient one on each rate:

\[
e+e+\left(\frac12-\frac e2\right)
+\left(\frac12-\frac{3e}{2}\right)=1
\]

for both \(R_1\) and \(R_2\), with the two initial \(e\)-terms arising from the appropriate individual-rate and sum-rate rows. Thus the weighted sum has left side \(R_1+R_2\).

The posterior expansion encoded by `KINDS` is also correct:

\[
\begin{aligned}
I(W;A)&=I_A(q_0)-\mathbb E I_A(q_W),\\
I(U;A\mid W)&=\mathbb E I_A(q_W)-\mathbb E I_A(q_{U,W}),\\
I(U,W;A)&=I_A(q_0)-\mathbb E I_A(q_{U,W}),\\
I(X;A\mid U,W)&=\mathbb E I_A(q_{U,W}),
\end{aligned}
\]

and analogously for \(V\). The required martingale identities follow from the hierarchy’s Markov factorization.

The displayed combined tensor is consistent with the six rows. In particular, after summing over groups, the prior coefficients are

\[
c_1' I_Y(q_0)+c_1'I_Z(q_0),
\]

with zero coefficients on \(I_G(q_0)\) and \(I_K(q_0)\). This supports the claimed all-priors reduction.

### 3. Channel formulas and reflection

The formulas used in the checker are correct for the four binary channels:

\[
I_Y(q)=h_2\!\left(\frac{1-q}{2}\right)-(1-q),
\qquad
I_Z(q)=h_2\!\left(1-\frac q2\right)-q.
\]

For \(G\), with \(a=P(G=0\mid X=0)\) and \(d=P(G=0\mid X=1)-a\),

\[
I_G(q)=h_2(a+dq)-(1-q)h_2(a)-q h_2(a+d).
\]

The exact decimal identities

\[
P(K=0\mid X=0)=1-P(G=0\mid X=1),\qquad
P(K=0\mid X=1)=1-P(G=0\mid X=0)
\]

hold, so the asserted reflection \(I_K(q)=I_G(1-q)\) is valid.

The curvature numerator

\[
S(q)=a(1-a)-d^2+d(1-2a)q
\]

does indeed have the sign of \((I_G-I_Y)''\), up to a strictly positive denominator. Thus the proposed concave/convex tangent arguments are mathematically appropriate if all the asserted sign and positivity tests pass.

### 4. Weak-duality logic

Conditionally on the pointwise line inequalities, the weak-duality argument is sound. For each group, if

\[
L_U(w;q)\ge f_U(q),\qquad L_V(w;q)\ge f_V(q)
\]

for all \(w,q\in[0,1]\), with the inner lines affine in \(q\), then

\[
\mathbb E[L_U(q_W;q_U)\mid q_W]
 =L_U(q_W;q_W),
\]

and similarly for \(V\). An affine outer majorant can then be averaged using only the common-mean martingale identities. No strong duality or minimax interchange is needed.

The cancellation of all affine prior slopes leaves

\[
c_1'\bigl(I_Y(q_0)+I_Z(q_0)\bigr)
\]

plus constants. Since each mutual information is concave in the input prior and

\[
I_Y(q)=I_Z(1-q),
\]

this expression is concave and reflection symmetric, so its maximum over \(q_0\in[0,1]\) is attained at \(q_0=1/2\). Endpoint priors cause no conceptual problem.

### 5. Material unresolved numerical obligations

The decisive evidentiary gap is that `verification.json` contains only a verifier request and **records no result**. The README explicitly confirms this:

> “The request records no result. Its terminal outcome is published after canonical merge as a separate content-addressed attestation.”

No such terminal attestation is included in the supplied evidence.

Consequently, the following essential assertions in `verify.py` are not affirmatively shown to have succeeded:

1. Positivity of the two global tangent quantities:
   ```python
   need(phi_a.lo > 0 and phi_c.lo > 0, ...)
   ```

2. Positivity of all eight analytic tangent/endpoint floors.

3. Successful completion of every recursive interval cover without:
   - an unresolved cell,
   - exceeding maximum depth,
   - falling below the minimum cell width, or
   - exceeding the cell budget.

4. The reported claim that the cover closes using 136 cells at maximum depth 30.

5. Exact reproduction under the three hostile ambient `Decimal` contexts.

6. Most importantly, the equality
   ```python
   need(value == EXPECTED_VALUE, "final interval drift")
   ```
   and the final upper-endpoint comparison with the headline decimal.

The program is fail-closed and its interval-arithmetic design appears structurally suitable, but an assertion in source code is not evidence that the assertion passed. The contribution also does not provide the generated subdivision cells and margins as a static certificate that can be independently checked without executing the recursive calculation.

### Conclusion

No decisive mathematical counterexample or symbolic error was found. If the supplied `verify.py` is successfully executed in the pinned environment, with the expected directed-rounding semantics, and produces the claimed evidence tuple and final interval, then the conditional upper bound would follow.

On the evidence actually supplied, however, the indispensable continuous numerical certification has not been affirmatively completed. Therefore the exact interval and the headline bound

\[
C_{\mathrm{sum}}\le 0.369296945969202842443
\]

cannot yet be marked valid.
