## `bssc-sum-capacity/finite-grid-q0-foundations`

**Verdict: VALID**

### Required dependency

- **Required:** `e3c1036ca607539a5ebcddf3058e6014ac5c1cd9`, for the exact 30-row functional, its optimization order, the definitions of \(V_Q,V_0,B\), and the inequality \(V_Q(G,K)\le B(G,K)\).
- The cited Theorem 9’s external PDF provenance and its capacity-converse interpretation are not additionally needed for this finite-grid claim; the present result is valid relative to the exact supplied 30-row system.

### Finite-output receiver reduction

Under the fair prior, the posterior representation
\[
m=\sum_a m_a\delta_{\rho_a},\qquad \sum_a m_a\rho_a=\tfrac12
\]
is correct, and the inverse formulas
\[
T(a|0)=2m_a(1-\rho_a),\qquad T(a|1)=2m_a\rho_a
\]
produce stochastic channel rows. Direct substitution gives
\[
J_A(q)=\int\psi(q,\rho)\,dm(\rho).
\]

For an \(N\)-point grid containing \(0,1\), only the \(N-2\) nonendpoint samples must be retained in addition to the posterior mean. Thus
\[
\Phi_Q(\rho)\in\mathbb R^{N-1}.
\]
Carathéodory’s theorem supplies at most \(N\) atoms preserving that vector. There is no closure issue because the original posterior measure is finite, and the endpoint samples are universally \(J_A(0)=J_A(1)=0\).

The identities
\[
I(S;A)=J_A(1/2)-\mathbb E J_A(q_S),\qquad
I(X;A|S)=\mathbb E J_A(q_S)
\]
and their conditional consequences cover all seven term types in the supplied rows. Hence a sampled-curve replacement preserves every row for every \(Q\)-supported hierarchy, not merely the final objective. This proves the unrestricted cardinality equality in both directions.

For a reflection-closed grid,
\[
J_{m^\circ}(q)=J_m(1-q)
\]
shows that replacing \(m\) and then using \(m'^\circ\) preserves the reflected pair’s samples. This establishes the reflected infimum equality without asserting symmetrization of arbitrary pairs.

### Exact \(Q_0\) reduction

For \(Q_0=\{0,\tfrac12,1\}\), a fair-prior coarse posterior law must have equal endpoint masses, giving the parameter \(A\). Refinement martingale constraints imply parameters \(U,V\ge0\) with
\[
A+U\le1,\qquad A+V\le1.
\]
Conversely, every such triple is jointly realizable by revealing/erasure refinements, chosen conditionally independently given \((X,W)\). Thus there is no omitted compatibility condition between the \(U\)- and \(V\)-refinements.

The resulting seven information quantities are exactly
\[
Ax,\ Ux,\ Vx,\ (A+U)x,\ (A+V)x,\ (1-A-U)x,\ (1-A-V)x.
\]
Consequently all rows depend only on \((c,g,k,c)\). The displayed row involution correctly exchanges \(g,k\), \(U,V\), the auxiliary-group order, and \(R_1,R_2\), proving \(V_0(g,k)=V_0(k,g)\).

### Coercive witnesses

The terminal attestation establishes that the pinned execution of `verify_q0.py`:

- generated all 30 labeled rows and matched the declared foundation-row digest;
- verified the full row-system reflection symmetry;
- checked every one of the 30 row slacks and all 15 block constraints for each of the H, L, and X families by exact rational-polynomial arithmetic;
- verified that `SL(1,U)` reduces identically to the common curve value when all four \(Q_0\) curves agree.

The polynomial substitutions correctly encode the claimed domains:

- H: \(x=c+p\), hence \(x\ge c\);
- L: \(y=x+p\), \(c=y+q\), hence \(0\le x\le y\le c\);
- X: \(c=x+p\), \(y=c+q\), hence \(x\le c\le y\), with the claimed strict-straddle formulas used only when the denominator is positive.

For the actual
\[
c=\frac34\log_2\frac43>0,
\]
all witness denominators are positive on their stated domains, and all rates are nonnegative. H, L, and the two separate X/H witnesses in the straddling case establish
\[
V_0(g,k)\ge \max\{F(g),F(k)\},
\qquad
F(x)=\frac{2c\max\{c,x\}}{c+x}.
\]
Together with the dependency’s \(B(G,K)\ge V_0(g,k)\), the claimed pointwise inequality follows.

### \(Q_0\) infima

For every \(x\ge0\), both branches of \(F\) satisfy \(F(x)\ge c\), so every finite receiver pair has \(V_0(g,k)\ge c\).

The posterior measure
\[
\frac c2\delta_0+(1-c)\delta_{1/2}+\frac c2\delta_1
\]
is valid, reflection invariant, and has \(Q_0\)-sampled curve \((0,c,0)\), matching both physical receivers. For this pair, the `SL(1,U)` row gives \(R_1+R_2\le c\) for every \(Q_0\)-supported hierarchy. Therefore
\[
c\le \inf_{G,K}V_{Q_0}(G,K)
\le \inf_m V_{Q_0}(m,m^\circ)\le c,
\]
so both infima equal \(c\). The earlier reduction gives the stated three-output sufficiency.

### Midpoint window

From \(F(x)\le U\), with \(c\le U<2c\),

- if \(x\le c\),
  \[
  x\ge \frac{2c^2}{U}-c;
  \]
- if \(x\ge c\),
  \[
  x\le \frac{Uc}{2c-U}.
  \]

Moreover,
\[
\frac{2c^2}{U}-c\le c,\qquad
\frac{Uc}{2c-U}\ge c,
\]
so each branch also satisfies the opposite side of the claimed interval. Applying this to \(g\) and \(k\) proves the necessary window.

### Attestation scope and final qualification

The attestation does not itself prove the posterior representation, Carathéodory reduction, martingale parameterization, or infimum arguments; those obligations are nevertheless established by the supplied mathematical proof. Conversely, neither the proof nor the attestation establishes a continuum receiver-cardinality bound, a grid-limit interchange, reflected optimality for \(B\), or a new numerical bound on \(C_{\mathrm{sum}}\). These limitations agree with the exact claim.
