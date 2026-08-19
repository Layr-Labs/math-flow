## `bssc-sum-capacity/gk-input-reduction-and-q0-foundations`

**Verdict: indeterminate**

The supplied arguments contain substantial internally consistent mathematics, and no explicit counterexample was found. However, the declared claim depends materially on the exact content of Gohari–Liu–Nair Theorem 9 and its 30-row specialization, neither of which is supplied as an explicit dependency or reproduced completely. The executable checkers verify algebra for a locally encoded row system; they do not independently establish that this encoding is exactly equations (19a)–(19p), their side conditions, or the governed definition of \(B(G,K)\) and \(V_Q(G,K)\). Consequently, the exact external-scope statements cannot be affirmatively certified from the admitted evidence.

### 1. Input-only marginalization of \(G,K\)

The probabilistic reduction itself is correct conditional on the asserted factorization and term audit.

For any auxiliary subtuple \(D\) satisfying \(D-X-(Y,Z,G,K)\),

\[
p(d,x,g)
=p_X(x)p_{D|X}(d|x)
 \sum_{y,z,k}T_{YZ|X}(y,z|x)T_{GK|XYZ}(g,k|x,y,z),
\]

so defining the final sum as \(\bar T_{G|X}(g|x)\) shows that replacing the original channel by

\[
T'_{GK|XYZ}(g,k|x,y,z)
=\bar T_{G|X}(g|x)\bar T_{K|X}(k|x)
\]

preserves the complete law of \((D,X,G)\). The analogous calculation preserves \((D,X,K)\), while the \(Y\)- and \(Z\)-marginal laws are unchanged. Thus every mutual-information term involving exactly one of \(Y,Z,G,K\), with all remaining arguments drawn from \(D,X\), is preserved. Signed sums and minima of preserved terms are also preserved. The reverse attainable-set inclusion is valid because every pair of input-only channels is itself an allowed \(T_{GK|XYZ}\) that ignores \(Y,Z\).

The unresolved obligation is syntactic but essential: the evidence asserts that the displayed audit table exhausts all terms in Theorem 9 equations (19a)–(19p) and its two side conditions, but the authoritative equations are not included or declared as a dependency. If even one omitted branch contained, for example, \(I(S;G,K\mid R)\), \(I(S;G\mid K,R)\), or another joint/output-conditioned expression, the marginalization would not establish the stated theorem-wide invariance. The checker does not address this issue.

Accordingly, the marginalization lemma is verified **for the supplied single-output term list**, but its claimed applicability to the exact external Theorem 9 system remains unverified.

### 2. Finite-grid receiver-cardinality reduction

The self-contained convex-geometric portion is sound.

For a fair-input posterior measure \(m=\sum_a m_a\delta_{\rho_a}\), the reconstruction

\[
P(A=a\mid X=0)=2m_a(1-\rho_a),\qquad
P(A=a\mid X=1)=2m_a\rho_a
\]

defines a valid channel exactly when \(\sum_a m_a\rho_a=1/2\). Direct substitution gives

\[
I_m(q)=\int\psi(q,\rho)\,dm(\rho).
\]

For a grid \(Q\) of size \(N\) containing \(0,1\), preserving the mean and the \(N-2\) interior samples is preservation of a point in the convex hull of a subset of \(\mathbb R^{N-1}\). Carathéodory’s theorem therefore gives a representing measure with at most \(N\) atoms. No closure or attainment issue occurs for the stated finite-output starting measure.

The identities

\[
I(S;A)=I_A(1/2)-\mathbb E I_A(q_S),\qquad
I(X;A\mid S)=\mathbb E I_A(q_S)
\]

follow from \(S-X-A\), and the conditional difference identities follow similarly. Reflection also behaves correctly:

\[
I_{m^\circ}(q)=I_m(1-q).
\]

Thus the reflected replacement is valid when \(Q\) is reflection closed.

What remains unresolved is whether the asserted 30-row functional really contains only terms covered by these identities and whether all relevant hierarchy posteriors are precisely restricted to \(Q\). That is asserted in prose but cannot be compared with an authoritative definition of \(V_Q\). Therefore the cardinality theorem is verified for a functional having the stated sampled-curve dependence, but not conclusively for the externally named “grid-restricted 30-row value.”

### 3. Exact \(Q_0\) optimum

The numerical constant is correctly identified:

\[
c=h_2(1/4)-\frac12
 =\frac34\log_2\frac43
 \approx0.3112781244591328.
\]

The proposed revealing-erasure posterior measure

\[
\frac c2\delta_0+(1-c)\delta_{1/2}+\frac c2\delta_1
\]

is a valid mean-\(1/2\), reflection-invariant probability measure, and its sampled mutual-information curve on \(Q_0\) is \((0,c,0)\), matching the physical \(Y,Z\) curves there.

Conditional on the displayed row `SL(1,U)` being an actual universal sum-rate constraint, the matching upper bound is correct: identical sampled curves cancel the cross differences, and with \(S=(U_a,W_a)\),

\[
I(S;G)+I(X;G\mid S)=I(X;G)=c
\]

because \(S-X-G\). Hence that row enforces \(R_1+R_2\le c\).

The universal lower construction and the stronger H/L/X witnesses likewise establish feasibility within the locally encoded 30-row system. The infimum ordering

\[
c\le \inf_{\rm all}V_{Q_0}
\le \inf_{\rm reflected}V_{Q_0}\le c
\]

is then correct.

The decisive missing verification is again correspondence of the locally reconstructed rows with the actual Theorem 9 specialization. The checker creates its own rows from hard-coded “path formulas” and checks their algebra and labels; it does not compare them to an independently supplied theorem specification. Therefore the exact equality is conditionally established for the encoded LP, but the named \(V_{Q_0}\) equality is not fully certified.

### 4. Pointwise coercive bound and midpoint window

The \(Q_0\)-block parameterization is mathematically plausible and correctly derived for three-point posterior martingales:

\[
A,U,V\ge0,\qquad A+U\le1,\qquad A+V\le1,
\]

with the seven receiver terms equal to

\[
Ax,\ Ux,\ Vx,\ (A+U)x,\ (A+V)x,\ (1-A-U)x,\ (1-A-V)x.
\]

The H, L, and X substitutions have positive denominators in their stated domains, satisfy the box constraints, and yield the claimed sums:

- \(x\ge c\): \(2cx/(c+x)\);
- \(0\le x\le c\): \(2c^2/(c+x)\);
- crossing case \(x<c<y\): the low-side value \(2c^2/(c+x)\), while the high-side value follows from the reflected H construction.

The exact-polynomial checker is meaningful here: coefficientwise nonnegative polynomials in the declared nonnegative substitution variables do certify all encoded row and box slacks. The cases cover \([0,1]^2\), including boundaries via H or L. This conditionally proves

\[
V_0(g,k)\ge \max\{F(g),F(k)\},
\qquad
F(x)=\frac{2c\max\{c,x\}}{c+x}.
\]

The inversion is also correct. Since \(c>0\) and \(c\le U<2c\),

\[
x\le c:\quad
F(x)\le U
\iff x\ge \frac{2c^2}{U}-c,
\]

and

\[
x\ge c:\quad
F(x)\le U
\iff x\le \frac{Uc}{2c-U}.
\]

Thus, assuming \(B(G,K)\ge V_0(g,k)\), the stated necessary window follows.

The unresolved obligations are:

1. the encoded 30 rows have not been independently shown to equal the governing Theorem 9 rows;
2. the definition and optimization order asserted for
   \[
   B(G,K)=\sup_qV(q;G,K)
   \]
   are not supplied from an explicit dependency;
3. the claimed restriction relation \(B(G,K)\ge V_0(g,k)\), while directionally consistent, therefore cannot be checked against the authoritative definition.

### Overall conclusion

The contribution gives a strong conditional certificate for its own reconstructed LP and sound standalone arguments for marginal preservation, finite-grid Carathéodory reduction, and algebraic coercivity. Nevertheless, exact applicability to the externally named Theorem 9 system is a material unverified premise. The provenance assertions about accepted source artifacts and byte-for-byte retention are likewise not independently evidenced by the supplied acceptance records.

Because there is no decisive internal counterexample, **invalid** is not justified; because the theorem/row correspondence is indispensable and unresolved, **valid** is also not justified.
