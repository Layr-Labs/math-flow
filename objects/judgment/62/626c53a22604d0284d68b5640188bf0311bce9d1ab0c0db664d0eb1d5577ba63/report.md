## `bssc-sum-capacity/finite-grid-q0-foundations`

**Verdict: VALID, relative to the explicitly declared transaction `e3c1036ca607539a5ebcddf3058e6014ac5c1cd9`.**

The claim remains conditional on the accepted 30-row outer-bound premise and its definitions. It does not establish an unconditional new capacity converse or improve the benchmark interval.

### 1. Dependency and scope

The declared dependency supplies exactly the objects used here:

- the finite-output, input-only receiver reduction;
- the 30 scalar constraints and their optimization order;
- the definitions of \(V(q;G,K)\), \(B(G,K)\), \(V_Q(G,K)\), and \(V_0(g,k)\);
- the inequalities
  \[
  V_Q(G,K)\le V(1/2;G,K)\le B(G,K);
  \]
- the fact that, on \(Q_0\), receiver dependence is only through \((c,g,k,c)\).

The subject does not improperly interchange receiver infima with prior suprema, nor extend a finite-grid result to the continuum.

### 2. Posterior representation and sampled mutual information

For a finite receiver under the fair input prior, the posterior measure
\[
m=\sum_a m_a\delta_{\rho_a}
\]
satisfies
\[
\sum_a m_a=1,\qquad \sum_a m_a\rho_a=\frac12.
\]
Conversely,
\[
T_{A|X}(a|0)=2m_a(1-\rho_a),\qquad
T_{A|X}(a|1)=2m_a\rho_a
\]
has nonnegative entries and row sums one. An output having zero fair-prior mass necessarily has zero probability under both inputs, so discarding it causes no domain problem.

Direct substitution verifies
\[
J_A(q)=\int\psi(q,\rho)\,dm(\rho).
\]
At \(q=0,1\), mutual information is zero, including the degenerate posterior cases under the stated zero-summand convention. At \(q=1/2\),
\[
\psi(1/2,\rho)=1-h_2(\rho).
\]
Reflection gives
\[
J_{m^\circ}(q)=J_m(1-q).
\]

### 3. Exact \(N\)-output reduction

If \(Q\) has \(N\) points and contains \(0,1/2,1\), there are exactly \(N-2\) nonendpoint samples. The map
\[
\Phi_Q(\rho)=\bigl(\rho,\psi(q_1,\rho),\ldots,\psi(q_{N-2},\rho)\bigr)
\]
takes values in \(\mathbb R^{N-1}\). Since the original posterior measure is finite, its integral is already a finite convex combination of points in \(\Phi_Q([0,1])\). Carathéodory’s theorem therefore supplies a representation using at most \(N\) points.

The first coordinate preserves the fair-prior mean \(1/2\), so the reduced measure is a valid receiver. The other coordinates preserve every nonendpoint sample, while endpoint samples are universally zero. Thus all samples on \(Q\) are preserved exactly.

For every \(S-X-A\),
\[
I(S;A)=J_A(1/2)-\mathbb E J_A(q_S),\qquad
I(X;A\mid S)=\mathbb E J_A(q_S),
\]
and consequently
\[
I(U;A\mid W)
=\mathbb E J_A(q_W)-\mathbb E J_A(q_{U,W}).
\]
These identities cover all seven receiver-term kinds in the accepted 30-row system. Hence a sampled-curve replacement preserves every constraint and objective value in a \(Q\)-supported hierarchy. The two infimum inequalities follow in opposite directions from:

1. exact value-preserving reduction of every finite receiver pair; and
2. inclusion of the at-most-\(N\)-output class in the finite-output class.

Thus
\[
\inf_{G,K\text{ finite}}V_Q(G,K)
=\inf_{|G|,|K|\le N}V_Q(G,K).
\]

When \(Q\) is reflection closed, replacing \(m\) by \(m'\) and using \(m'^\circ\) preserves the second receiver’s samples because
\[
J_{m'^\circ}(q)=J_{m'}(1-q)=J_m(1-q)=J_{m^\circ}(q).
\]
This proves the reflected infimum equality without asserting arbitrary-pair symmetrization.

### 4. \(Q_0\) scalar reduction

A probability distribution on \(Q_0=\{0,1/2,1\}\) with mean \(1/2\) must have equal endpoint masses. Hence the coarse posterior law has masses
\[
A/2,\quad 1-A,\quad A/2.
\]
A refinement can move total mass \(U\) or \(V\) from the midpoint equally to the two endpoints, yielding
\[
A,U,V\ge0,\qquad A+U\le1,\qquad A+V\le1.
\]

There is no omitted compatibility condition between the \(U\)- and \(V\)-refinements: they can be implemented conditionally independently given \((X,W)\) by revealing/erasure kernels. All required auxiliaries are finite.

The seven information terms consequently equal
\[
Ax,\ Ux,\ Vx,\ (A+U)x,\ (A+V)x,\ (1-A-U)x,\ (1-A-V)x,
\]
as stated. The accepted row system is invariant under reversal of the receiver chain, exchange of \(U,V\), and exchange of \(R_1,R_2\), proving
\[
V_0(g,k)=V_0(k,g).
\]

### 5. H/L/X witnesses and coercive floor

The three families cover all cases:

- **H:** a selected midpoint value is at least \(c\);
- **L:** both are at most \(c\), after ordering them;
- **X:** they strictly straddle \(c\), with boundary cases handled by H or L.

All denominators are positive:

- \(c+x>0\), since \(c>0\);
- in X, additionally \(\Delta=y-x>0\).

The stated tuples obey all block constraints. In X, the only nontrivial one is
\[
1-A-V=\frac{x(y-c)}{(c+x)(y-x)}\ge0.
\]

The supplied exact verifier reconstructs the same 30 path rows as the dependency and, using rational polynomial arithmetic, checks every row slack and all block constraints coefficientwise after the substitutions. It uses no floating-point or optimization assumption. The algebra gives:

- H: \(2cx/(c+x)=F(x)\) on \(x\ge c\);
- L: \(2c^2/(c+x)=F(x)\) for the smaller of two values in \([0,c]\);
- X: \(F(x)\) for the low value, while H independently supplies \(F(y)\) for the high value.

Because \(V_0\) is a supremum, separate witnesses for the two values suffice to obtain their maximum. Therefore
\[
V_0(g,k)\ge\max\{F(g),F(k)\}.
\]
Combining this with the dependency gives
\[
B(G,K)\ge V_0(g,k)\ge\max\{F(g),F(k)\}.
\]

### 6. Exact \(Q_0\) infima

The constant is correctly evaluated:
\[
c=h_2(1/4)-\frac12
=\frac34\log_2\frac43\in(0,1).
\]
For every \(x\ge0\),
\[
F(x)\ge c
\]
on both branches, so every finite receiver pair satisfies \(V_0(g,k)\ge c\).

The posterior measure
\[
\frac c2\delta_0+(1-c)\delta_{1/2}+\frac c2\delta_1
\]
is a valid reflection-invariant three-output receiver with sampled curve \((0,c,0)\). Thus all four \(Q_0\)-sampled receiver curves agree. In row `SL(1,U)`, the difference terms cancel and the remaining terms give
\[
I(U_a,W_a;G)+I(X;G\mid U_a,W_a)=I(X;G)=c.
\]
Hence \(V_{Q_0}\le c\) for this reflected pair. Together with the universal floor,
\[
\inf_{G,K\text{ finite}}V_{Q_0}(G,K)
=\inf_{m\text{ finite}}V_{Q_0}(m,m^\circ)
=c.
\]

### 7. Midpoint window and edge cases

From \(B(G,K)\le U\) and the floor, \(F(g),F(k)\le U\). Solving each branch gives
\[
x\le c\implies x\ge \frac{2c^2}{U}-c,
\]
and
\[
x\ge c\implies x\le \frac{Uc}{2c-U}.
\]
The denominator \(2c-U\) is strictly positive because \(U<2c\).

The opposite side of each two-sided bound follows from the branch condition: when \(x\le c\), the displayed upper endpoint is at least \(c\); when \(x\ge c\), the displayed lower endpoint is at most \(c\). Thus
\[
\frac{2c^2}{U}-c\le g,k\le\frac{Uc}{2c-U}.
\]
The endpoint \(U=c\) is also consistent and forces \(g=k=c\).

The stated finite-grid, reflected-class, and necessary-coercivity qualifications are therefore all respected.
