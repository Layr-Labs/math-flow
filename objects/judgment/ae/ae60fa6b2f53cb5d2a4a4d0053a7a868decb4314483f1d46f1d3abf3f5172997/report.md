## `bssc-sum-capacity/finite-grid-q0-foundations`

**Verdict: valid**

### Required dependency

- **Required:** `e3c1036ca607539a5ebcddf3058e6014ac5c1cd9`
- **Needed content only:** the definitions and optimization order for \(V(q;G,K)\), \(V_Q(G,K)\), \(V_0(g,k)\), and \(B(G,K)\); the exact 30-row private-message system; its single-output term structure; and \(V_Q(G,K)\le B(G,K)\).
- The external authenticity of Gohari–Liu–Nair Theorem 9 and the capacity-converse interpretation of that theorem are not needed for the present finite-grid algebraic claim.

The declared-reference attestation establishes exact agreement, after the stated chain-rule normalization, between the encoded premise and the generated 30-row system, together with the exhaustive single-output term audit. It does not authenticate the external manuscript, but that stronger fact is unnecessary here.

### Audit

1. **Posterior representation and sampled curves**

   Under the fair input prior, the posterior measure
   \[
   m=\sum_a m_a\delta_{\rho_a},\qquad \sum_a m_a\rho_a=\tfrac12
   \]
   is in exact correspondence with a finite-output binary-input channel through
   \[
   T(a|0)=2m_a(1-\rho_a),\qquad T(a|1)=2m_a\rho_a.
   \]
   Both channel rows sum to one. Direct substitution verifies
   \[
   J_A(q)=\int\psi(q,\rho)\,dm(\rho).
   \]
   For every nonendpoint \(q\in(0,1)\), \(\psi(q,\rho)\) is continuous in \(\rho\); the endpoint samples \(J_A(0)=J_A(1)=0\) are universal. Reflection gives
   \[
   J_{m^\circ}(q)=J_m(1-q).
   \]

2. **Exact \(N\)-output grid reduction**

   For an \(N\)-point grid containing \(0\) and \(1\), the map
   \[
   \Phi_Q(\rho)=\bigl(\rho,\psi(q_1,\rho),\ldots,\psi(q_{N-2},\rho)\bigr)
   \]
   takes values in \(\mathbb R^{N-1}\). Carathéodory’s theorem therefore represents its integral using at most \(N\) atoms. The first coordinate preserves posterior mean \(1/2\), so the resulting atomic measure is a valid receiver; the other coordinates preserve every nonendpoint sample, while endpoint samples are automatically zero.

   For every \(S-X-A\),
   \[
   I(S;A)=J_A(1/2)-\mathbb E J_A(q_S),\qquad
   I(X;A|S)=\mathbb E J_A(q_S),
   \]
   and hence
   \[
   I(U;A|W)=\mathbb E J_A(q_W)-\mathbb E J_A(q_{UW}).
   \]
   These identities cover all seven receiver-term kinds appearing in the audited rows. Thus matching \(J_A\) on \(Q\) preserves every row for every \(Q\)-supported hierarchy, not merely its objective value. Independent replacement of \(G\) and \(K\) proves
   \[
   \inf_{G,K\ \mathrm{finite}}V_Q(G,K)
   =\inf_{|G|,|K|\le N}V_Q(G,K).
   \]

   If \(Q\) is reflection closed, replacing \(m\) by \(m'\) and the second receiver by \(m'^\circ\) preserves both sampled curves because \(1-q\in Q\). Hence the reflected-class equality is also established. No attainment or limit interchange is used.

3. **Complete \(Q_0\) parametrization**

   On \(Q_0=\{0,\tfrac12,1\}\), the mean constraint forces the coarse posterior law to have masses
   \[
   A/2,\quad 1-A,\quad A/2.
   \]
   Martingale refinement forces each \(U\)- or \(V\)-refinement to move equal mass from \(1/2\) to the two endpoints, yielding exactly
   \[
   A,U,V\ge0,\qquad A+U\le1,\quad A+V\le1.
   \]
   Conversely, every such triple is jointly realizable by finite revealing/erasure kernels for \(U\) and \(V\), conditionally independently given \((X,W)\). Thus there is no omitted compatibility condition.

   The seven information terms consequently have coefficients
   \[
   A,\ U,\ V,\ A+U,\ A+V,\ 1-A-U,\ 1-A-V
   \]
   times the receiver midpoint value. Therefore the complete \(Q_0\) problem depends only on \((c,g,k,c)\).

4. **Symmetry and H/L/X witnesses**

   The subject verifier, in its pinned successful execution, checks:
   - the exact declared dependency and reviewed row digest;
   - invariance of all 30 rows under simultaneous \(G\leftrightarrow K\), \(Y\leftrightarrow Z\), group reversal, \(U\leftrightarrow V\), and \(R_1\leftrightarrow R_2\);
   - every one of the 30 row slacks and all block constraints for each H/L/X family using exact rational-polynomial arithmetic.

   The substitutions cover all cases:
   - H handles either selected midpoint value at least \(c\);
   - L handles both midpoint values at most \(c\), with the smaller midpoint producing the larger \(F\);
   - X handles strict straddling, while boundary cases are already covered by H or L.

   All witness denominators are positive on their claimed domains because
   \[
   c=h_2(1/4)-\tfrac12=\tfrac34\log_2(4/3)>0.
   \]
   The symbolic checks are sufficient because every slack becomes a polynomial with nonnegative coefficients in nonnegative variables. Thus
   \[
   V_0(g,k)\ge \max\{F(g),F(k)\},
   \qquad
   F(x)=\frac{2c\max\{c,x\}}{c+x}.
   \]

5. **Exact \(Q_0\) infima**

   For \(x\le c\),
   \[
   F(x)=\frac{2c^2}{c+x}\ge c,
   \]
   and for \(x\ge c\),
   \[
   F(x)=\frac{2cx}{c+x}\ge c.
   \]
   Hence every finite pair satisfies \(V_0(g,k)\ge c\).

   The proposed three-output posterior measure
   \[
   \frac c2\delta_0+(1-c)\delta_{1/2}+\frac c2\delta_1
   \]
   is valid, reflection invariant, and has \(Q_0\)-samples \((0,c,0)\), identical to those of each physical BSSC marginal. For this pair, the `SL(1,U)` row reduces for every \(Q_0\)-supported hierarchy to
   \[
   R_1+R_2\le I(U_a,W_a;G)+I(X;G|U_a,W_a)=I(X;G)=c.
   \]
   The subject attestation checks this row reduction exactly. Therefore both the unrestricted and reflected infima equal \(c\).

6. **Coercive midpoint window**

   From \(B(G,K)\ge V_0(g,k)\), the hypothesis \(B(G,K)\le U\) implies \(F(g),F(k)\le U\). Solving on the two branches gives
   \[
   x\le c\implies x\ge \frac{2c^2}{U}-c,
   \]
   and, since \(2c-U>0\),
   \[
   x\ge c\implies x\le \frac{Uc}{2c-U}.
   \]
   The missing side of each interval follows automatically from
   \[
   \frac{2c^2}{U}-c\le c\le \frac{Uc}{2c-U}
   \]
   for \(c\le U<2c\). Applying this to \(g\) and \(k\) proves the stated necessary window.

### Attestation scope

The subject attestation affirmatively establishes the row digest, symmetry, exact H/L/X row and box slacks, and the common-curve upper row. It does not itself prove the posterior representation, Carathéodory reduction, \(Q_0\) parametrization, infimum logic, or coercivity algebra; those obligations are nevertheless established by the written argument above.

The claim is correctly limited to finite grids and necessary midpoint coercivity. It does **not** establish a continuum cardinality theorem, reflected optimality for \(B\), a limit interchange, or an improved bound on \(C_{\mathrm{sum}}\).
