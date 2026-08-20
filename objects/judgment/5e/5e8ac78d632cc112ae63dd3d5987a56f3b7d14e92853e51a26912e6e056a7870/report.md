## `bssc-sum-capacity/gk-input-reduction-and-q0-foundations`

**Verdict: INDETERMINATE**

**Declared references:** none.  
**Required accepted dependencies:** none can be admitted from this packet.

The Gohari–Liu–Nair manuscript is cited bibliographically inside the contribution, but it is not a declared reference transaction and its Theorem 9 equations are not supplied. The subject does not fully restate those equations or provide a verified correspondence between them and the reconstructed 30-row system. This is a material target-identification gap affecting all four numbered assertions.

### 1. Input-only marginalization

The abstract marginalization argument is correct under its stated syntactic premise:

- From the displayed factorization, the auxiliary groups are conditionally independent of \((Y,Z,G,K)\) given \(X\).
- For every auxiliary subtuple \(D\),
  \[
  p(d,x,g)=p_X(x)p_{D|X}(d|x)\bar T_{G|X}(g|x),
  \]
  and similarly for \(K\).
- Thus every mutual information involving one of \(G\) or \(K\), with all other arguments drawn from \(X\) and the auxiliary variables, is preserved by the product replacement.
- The \(Y\)- and \(Z\)-marginals are unchanged.
- The reverse attainable-set inclusion is correctly obtained by taking any pair of input-only channels and letting them ignore \(Y,Z\).
- Finite alphabets and zero-probability symbols cause no problem.

The unresolved premise is that **every term in the actual Theorem 9 equations (19a)–(19p), every minimum branch, and both side conditions really has the asserted single-output form**. The contribution gives an alleged exhaustive term list, but the referenced equations themselves are absent, and no supplied evidence checks that exhaustiveness. The proof therefore establishes a conditional lemma about the listed terms, not yet the exact claim about the named theorem.

**Subclaim status: indeterminate.**

### 2. Finite-grid receiver cardinality

The internal convex-geometric argument is sound:

- The posterior-measure/channel correspondence at fair input is correct.
- Direct substitution gives
  \[
  I_m(q)=\int\psi(q,\rho)\,dm(\rho).
  \]
- Matching the mean and the \(N-2\) nonendpoint samples is a convex-hull problem in \(\mathbb R^{N-1}\); Carathéodory therefore gives at most \(N\) atoms.
- The endpoint values \(I_m(0)=I_m(1)=0\) need not be included as separate coordinates.
- The identities
  \[
  I(S;A)=I_A(1/2)-\mathbb E I_A(q_S),\qquad
  I(X;A|S)=\mathbb E I_A(q_S)
  \]
  and the displayed conditional version are correct for the relevant Markov chains.
- Reflection covariance correctly shows that replacing \(m\) by \(m'\) simultaneously replaces \((m,m^\circ)\) by \((m',m'^\circ)\) when \(Q\) is reflection closed.

However, equality of the named value \(V_Q\) additionally requires proof that every receiver-dependent expression and every feasibility condition in the actual grid-restricted Theorem 9 LP is determined by precisely these samples. That is asserted but not verified against a supplied definition of \(V_Q\) or the original equations.

**Subclaim status: indeterminate.**

### 3. Exact \(Q_0\) value

Several calculations are correct:

- For the BSSC at fair input,
  \[
  I(X;Y)=I(X;Z)=h_2(1/4)-\tfrac12=c.
  \]
- The revealing-erasure posterior measure
  \[
  \frac c2\delta_0+(1-c)\delta_{1/2}+\frac c2\delta_1
  \]
  is a valid mean-\(1/2\), reflection-invariant channel and has sampled curve \((0,c,0)\) on \(Q_0\).
- In the supplied reconstructed row `SL(1,U)`, equality of all four sampled receiver curves makes the cross-differences vanish and yields
  \[
  I(U,W;G)+I(X;G|U,W)=I(X;G)=c.
  \]
- Within the reconstructed rows, setting \(W=X\) and \(U,V\) constant makes \((c,0)\) feasible, while the revealing-erasure construction supplies the matching sum-row upper bound.

Thus the lower and upper certificates are coherent for the **encoded** 30-row system. But the packet does not establish that this encoded system is exactly the named grid-restricted Theorem 9 value \(V_{Q_0}\). Consequently the claimed equality for the actual \(V_{Q_0}\) remains unresolved.

There is also an evidence inconsistency: `frontier-global-bridge/FULL.md` states that its checker prints four messages beginning with `PASS: rebuilt...`, whereas the supplied `frontier-global-bridge/verify_q0.py` is the H/L/X coercivity checker and prints different messages. This does not refute the mathematical construction, but it defeats the claimed reproduction description for that retained artifact.

**Subclaim status: indeterminate.**

### 4. Coercive strengthening and midpoint window

For the reconstructed scalar LP, the H/L/X certificate is internally consistent:

- The three cases cover \(g,k\ge c\), \(g,k\le c\), and the straddling regime, including boundaries through H or L.
- The displayed block parameters satisfy the stated box inequalities in their applicable domains.
- The symbolic substitutions in the checker make every encoded row slack coefficientwise nonnegative.
- Symmetry of the generated rows justifies exchanging \(g\) and \(k\) for that encoding.
- The resulting bound is
  \[
  V_0(g,k)\ge\max\{F(g),F(k)\},
  \qquad
  F(x)=\frac{2c\max\{c,x\}}{c+x}.
  \]
- The inversion is algebraically correct:
  \[
  x\le c:\quad F(x)\le U\iff x\ge \frac{2c^2}{U}-c,
  \]
  \[
  x\ge c:\quad F(x)\le U\iff x\le \frac{Uc}{2c-U},
  \]
  using \(c\le U<2c\). These combine into the stated necessary window.

Two material obligations remain:

1. The exact parameterization of every admissible \(Q_0\) hierarchy by \((A,U,V)\) is described through separate \(U\)- and \(V\)-refinements, but simultaneous realization of both refinements by a single admissible joint hierarchy is not explicitly established.
2. More importantly, neither the reconstructed 30 rows nor the relation
   \[
   B(G,K)\ge V(1/2;G,K)\ge V_0(g,k)
   \]
   is verified against a supplied definition of the actual Theorem 9 functional \(B\).

The Python files contain exact rational-polynomial checks of their own generated rows, but there is no terminal objective attestation. Even a successful execution would certify only those encoded polynomial predicates, not their correspondence with the external theorem.

**Subclaim status: indeterminate.**

### Evidence and provenance qualification

The claims that these are “verbatim accepted submissions,” that the checkers are the exact accepted checkers, and that the files are byte-for-byte copies of specified source commits are not established by any supplied content-addressed attestation or source comparison. These provenance assertions are not used as mathematical premises.

### Conclusion

No decisive mathematical counterexample was found to the internal marginalization, Carathéodory, \(Q_0\), or H/L/X arguments. Nevertheless, the packet does not affirmatively establish that the listed or generated rows are exactly the Gohari–Liu–Nair Theorem 9 system named in the claim. Because that correspondence is essential to every numbered statement, the declared claim cannot be marked valid.
