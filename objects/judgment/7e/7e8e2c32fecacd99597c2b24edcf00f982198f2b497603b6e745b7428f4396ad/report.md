## `bssc-sum-capacity/gk-input-reduction-and-q0-foundations`

**Verdict: INDETERMINATE**

**Required declared dependencies:** none. No reference transaction was declared, so the Gohari–Liu–Nair manuscript and the cited source commits cannot be treated as admitted mathematical premises.

The supplied arguments are internally plausible and several algebraic components check out, but the record does not establish that its reconstructed 30-row system is exactly Theorem 9, equations (19a)–(19p), including all branches and side conditions. That unresolved correspondence affects all four numbered assertions.

### 1. Input-only, conditionally independent replacement

The marginalization argument itself is correct under the asserted factorization and asserted term audit:

- The proposed \(\bar T_{G|X}\) and \(\bar T_{K|X}\) are valid channels.
- For any auxiliary subtuple \(D\),
  \[
  p(d,x,g)=p_X(x)p_{D|X}(d|x)\bar T_{G|X}(g|x),
  \]
  and analogously for \(K\).
- Hence every mutual information involving only one of \(G\) or \(K\), together with \(X\) and auxiliary variables, is preserved.
- Terms involving \(Y\) or \(Z\) are unaffected.
- The reverse attainable-set inclusion follows because any pair of input-only channels is already an admissible output-dependent channel that ignores \(Y,Z\).
- Zero-probability inputs or outputs do not create a defect because equality of the relevant finite joint laws is asserted directly.

However, the essential premise that **every** term in the actual Theorem 9 system has the stated single-output form is not independently established. The manuscript equations are not supplied as declared reference evidence. The “complete term audit” is an assertion within the contribution, not a comparison against admitted source material. Consequently the exact claim about equations (19a)–(19p) remains unresolved.

### 2. Finite-grid receiver cardinality reduction

The abstract convex-geometric argument is sound:

- The posterior-measure/channel correspondence at the fair input is correct.
- The displayed formula
  \[
  I_m(q)=\int\psi(q,\rho)\,dm(\rho)
  \]
  follows by direct substitution.
- Preserving the mean and the \(N-2\) nonendpoint samples gives a point in \(\mathbb R^{N-1}\); Carathéodory therefore yields at most \(N\) atoms.
- The identities
  \[
  I(S;A)=I_A(1/2)-\mathbb E I_A(q_S),\qquad
  I(X;A\mid S)=\mathbb E I_A(q_S)
  \]
  and their conditional analogues are valid for \(S-X-A\).
- Reflection covariance gives the claimed simultaneous reduction of a reflected pair when \(Q\) is reflection closed.

What remains unproved is that the referenced grid-restricted value \(V_Q\) is exactly determined by only these samples. That requires a complete, authoritative definition of \(V_Q\) and verification that every term in its actual 30 rows has the asserted form and that every relevant posterior is restricted to \(Q\). The supplied checker generates a hard-coded row model but does not establish its correspondence to the external theorem. Thus the cardinality theorem is verified only conditionally on an unestablished model-identification premise.

### 3. Exact \(Q_0\) optimum

Several internal calculations are correct:

- At the fair input,
  \[
  I(X;Y)=I(X;Z)=h_2(1/4)-\tfrac12=c.
  \]
- The revealing-erasure posterior measure
  \[
  \frac c2\delta_0+(1-c)\delta_{1/2}+\frac c2\delta_1
  \]
  is valid, reflection invariant, and has sampled mutual-information curve \((0,c,0)\) on \(Q_0\).
- If the supplied row `SL(1,U)` is indeed an actual constraint, equality of the four sampled receiver curves makes its cross-differences vanish, while
  \[
  I(U,W;G)+I(X;G\mid U,W)=I(X;G)=c.
  \]
  This gives the asserted upper bound within that row model.
- The lower-bound witness \(W=X\), with \(U,V\) constant, is also valid provided the reconstructed 30 constraints are complete and correct.

Again, the decisive unresolved issue is correspondence: neither the stated row table nor the generated rows are shown against admitted Theorem 9 evidence. Therefore the equality
\[
\inf_{G,K}V_{Q_0}(G,K)=\inf_mV_{Q_0}(m,m^\circ)=c
\]
is not affirmatively established for the named external functional.

### 4. Pointwise coercive bound and midpoint window

Conditional on the reconstructed 30-row LP, the algebra is coherent:

- The \(Q_0\)-block parameterization
  \[
  A,U,V\ge0,\qquad A+U\le1,\quad A+V\le1
  \]
  and the seven resulting information terms are consistent with posterior martingales on \(\{0,\tfrac12,1\}\).
- The H, L, and X witness formulas have the required nonnegative box slacks in their stated domains.
- The three cases cover high, low, and straddling midpoint values, with boundary cases handled by H or L.
- The symmetry argument gives the complementary \(g,k\) branch.
- The inversion is correct:
  \[
  F(x)\le U,\quad c\le U<2c
  \]
  implies
  \[
  \frac{2c^2}{U}-c\le x\le\frac{Uc}{2c-U}.
  \]

The supplied Python code uses exact rational polynomial arithmetic and appears designed to check the generated row slacks. But there is no terminal objective attestation establishing that the command ran on pinned bytes. More importantly, even a successful run would prove only consistency of the hard-coded generated row system; it would not prove that this system is exactly the relevant Theorem 9 LP. The passage
\[
B(G,K)\ge V(1/2;G,K)\ge V_0(g,k)
\]
also depends on the unprovided formal definition and optimization order of \(B\).

### Provenance assertions

The statements that the files are byte-for-byte copies of particular source commits and that the artifacts were previously accepted are not established by the packet: no source comparison, content-addressed attestation, or declared reference transaction is supplied. These assertions are provenance matters rather than mathematical premises, but they are part of the exact declared statement and remain unverified.

### Conclusion

No decisive counterexample or internal algebraic contradiction was found. Nevertheless, the missing authoritative identification of the reconstructed constraints with the named Theorem 9 system—and the absence of attested execution or provenance evidence—leaves material proof obligations unresolved. The conjunction of the four claims therefore cannot be marked valid.
