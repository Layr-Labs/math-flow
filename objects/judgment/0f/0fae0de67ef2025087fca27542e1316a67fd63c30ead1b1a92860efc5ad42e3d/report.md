# Judgment of transaction `d638c346212db3e75f6a53dcebcfd09f55125852`

## Overall assessment

The transaction contains four mathematically distinct results:

1. a reduction of the Gohari–Liu–Nair auxiliary receivers \(G,K\) to conditionally independent input-only channels;
2. a finite-cardinality reduction for receiver channels when the auxiliary posterior optimization is restricted to a finite grid;
3. an exact evaluation of the three-point-grid receiver optimization;
4. a pointwise coercive lower bound depending only on the midpoint informations \(I_G(1/2)\) and \(I_K(1/2)\).

The supplied arguments for these results are logically strong and, for the finite-grid claims, are accompanied by inspectable exact symbolic code. The principal qualification is that the full equations (19a)–(19p) of the cited outer bound are not included. Consequently, the algebraic arguments can be checked from the supplied material, but the assertion that the term list and the hard-coded 30 rows exactly reproduce the manuscript cannot be independently established from this transaction alone.

None of the results changes either endpoint of the stated capacity interval. The contribution correctly describes the finite-grid values as lower approximations to the fixed-receiver outer-bound functional, not as converse bounds on \(C_{\mathrm{sum}}\).

There is also a concrete reproducibility inconsistency: the checker included under `frontier-global-bridge` is the same coercivity checker included under `frontier-q0-coercive`, while the former artifact describes a different expected output and claims a direct audit of the \(W=X\) witness table. This does not invalidate the mathematical conclusions, because the included checker verifies a stronger coercive lower bound and the matching upper row, but the two commands are not independent checks and the documentation of the first checker is inaccurate.

---

## Finding 1: Input-only marginalization of the two auxiliary receivers

**Claim key:** `GK-Theorem-9-input-only-auxiliary-receiver-reduction`

### Proposition assessed

For the displayed Gohari–Liu–Nair Theorem 9 constraint system, any finite channel
\[
T_{G,K\mid X,Y,Z}
\]
can be replaced by
\[
T'_{G,K\mid X,Y,Z}(g,k\mid x,y,z)
=\bar T_{G\mid X}(g\mid x)\bar T_{K\mid X}(k\mid x)
\]
without changing any branch of equations (19a)–(19p) or either side condition.

### Decisive reasoning

The proof correctly isolates the relevant invariant. Under the asserted factorization, for any auxiliary subtuple \(D\),
\[
p(d,x,g)
=p_X(x)p_{D\mid X}(d\mid x)
  \sum_{y,z,k}T_{Y,Z\mid X}(y,z\mid x)
  T_{G,K\mid X,Y,Z}(g,k\mid x,y,z).
\]
The sum is precisely the induced channel \(\bar T_{G\mid X}(g\mid x)\). Under the proposed product replacement, marginalizing \(Y,Z,K\) produces the same expression. Thus the complete joint law of \((D,X,G)\) is preserved. The analogous statement holds for \((D,X,K)\), while the \(Y\) and \(Z\) marginal laws are unchanged directly.

It follows that every mutual information of the forms
\[
I(S;G\mid R),\qquad I(S;K\mid R),
\]
with \(S,R\) made from \(X\) and the auxiliary variables, is unchanged. Signed sums and minima of unchanged quantities are also unchanged. The reverse attainable-set inclusion is immediate because every pair \(Q_{G\mid X},Q_{K\mid X}\) can be embedded in the original family by ignoring \(Y,Z\).

Conditional \(G\)-\(K\) correlation is therefore indeed irrelevant whenever the constraint system contains no joint terms involving both outputs and no terms conditioning one output on another.

### Missing evidence and scope qualification

The proof depends critically on the syntactic assertion that the supplied audit table exhausts equations (19a)–(19p) and the two side conditions. The actual equations are not reproduced in the transaction, so this exhaustiveness cannot be independently compared against the manuscript using only the supplied evidence.

Accordingly:

- the marginal-law argument itself is correct;
- the theorem applies to any constraint system having the stated single-output structure;
- its identification with the complete cited Theorem 9 system is well supported by the detailed term audit, but not fully self-contained here.

The stated limitation is appropriate: a bound containing a term such as \(I(S;G,K\mid R)\), \(I(S;Y\mid G)\), or any other joint/output-conditioned term would not be covered.

### Judgment

**Supported with high confidence, conditional on the supplied term audit being a faithful transcription of Theorem 9.**

---

## Finding 2: Finite-grid receiver-cardinality reduction

**Claim key:** `finite-posterior-grid-receiver-cardinality-at-most-grid-size`

### Proposition assessed

Let \(Q\subset[0,1]\) be an \(N\)-point grid containing \(0,\tfrac12,1\). For the fair-input posterior LP in which every auxiliary posterior is restricted to \(Q\), each finite-output binary-input receiver can be replaced, without changing the LP value, by a receiver with at most \(N\) outputs. If \(Q\) is reflection closed, the same reduction preserves reflected receiver pairs.

### Decisive reasoning

The posterior-measure representation is correct. Under the fair input, a finite-output binary-input channel is represented by
\[
m=\sum_a m_a\delta_{\rho_a},\qquad
\sum_a m_a\rho_a=\frac12,
\]
and conversely this measure determines a valid channel through
\[
P(A=a\mid X=0)=2m_a(1-\rho_a),\qquad
P(A=a\mid X=1)=2m_a\rho_a.
\]

The displayed function \(\psi(q,\rho)\) is linear in the posterior measure and gives
\[
I_m(q)=\int\psi(q,\rho)\,dm(\rho).
\]
To preserve the receiver on the grid, it suffices to preserve:

- the posterior mean \(\int\rho\,dm=\frac12\);
- the \(N-2\) mutual-information samples at the nonendpoint grid points.

These form a vector in \(\mathbb R^{N-1}\). Carathéodory’s theorem therefore gives a representing measure with at most \(N\) atoms. The mean coordinate ensures that the replacement remains a valid binary-input channel.

The identities
\[
I(S;A)=I_A(1/2)-\mathbb E I_A(q_S),
\qquad
I(X;A\mid S)=\mathbb E I_A(q_S)
\]
follow from the Markov relation \(S-X-A\) and the chain rule. Their conditional variants similarly express all single-receiver mutual-information terms through samples \(I_A(q)\). Thus, if every posterior appearing in the restricted auxiliary hierarchy lies in \(Q\), equality of the receiver curves on \(Q\) preserves every such row value.

The reflected-pair statement also follows:
\[
I_{m^\circ}(q)=I_m(1-q).
\]
For reflection-closed \(Q\), matching \(m\) on \(Q\) automatically matches \(m^\circ\) through the reflected replacement.

### Important scope distinctions

This is a cardinality theorem for the **receiver outputs** in a fixed finite-grid auxiliary optimization. It is not:

- a cardinality theorem for the continuum posterior problem;
- a proof that receiver posterior atoms themselves belong to \(Q\);
- an interchange of an infimum with a grid limit;
- a proof that reflected pairs suffice among arbitrary continuum receiver pairs.

The contribution states these limitations correctly.

As in Finding 1, applying the result specifically to the named 30-row LP assumes that all relevant terms have the asserted single-receiver posterior-sample form. The general Carathéodory argument is independently sound.

### Judgment

**Supported with high confidence.** The proof is concise, exact, and uses the correct ambient dimension, giving the claimed bound of \(N\), not \(N+1\).

---

## Finding 3: Exact solution of the three-point grid \(Q_0\)

**Claim key:** `three-point-grid-GK-receiver-optimum-equals-BSSC-midpoint-information`

### Proposition assessed

For
\[
Q_0=\left\{0,\frac12,1\right\},\qquad
c=h_2(1/4)-\frac12,
\]
the unrestricted finite-output receiver-pair infimum and the reflected-pair infimum both equal \(c\):
\[
\inf_{G,K}V_{Q_0}(G,K)
=
\inf_mV_{Q_0}(m,m^\circ)
=
c.
\]

### Lower bound

At the fair input,
\[
I(X;Y)=I(X;Z)=c.
\]
Choosing \(W=X\) and \(U,V\) constant in each auxiliary group uses only endpoint posteriors and is therefore admissible on \(Q_0\). The supplied table asserts that \((R_1,R_2)=(c,0)\) satisfies all 30 rows for every \(G,K\). This gives
\[
V_{Q_0}(G,K)\ge c
\]
for every receiver pair.

The table is consistent with the usual identities for \(W=X\): all conditional terms below \(W\) vanish, while \(I(W;A)=I(X;A)\). The side-condition rows also reduce to zero.

### Matching upper construction

The revealing-erasure posterior measure
\[
m_E=\frac c2\delta_0+(1-c)\delta_{1/2}+\frac c2\delta_1
\]
has mean \(1/2\), is reflection invariant, and satisfies
\[
I_E(0)=I_E(1)=0,\qquad I_E(1/2)=c.
\]
Hence \(Y,G,K,Z\) have identical sampled curves on \(Q_0\) when \(G=K=E\).

For the supplied `SL(1,U)` row, identical receiver samples cancel the two cross differences. The remaining terms telescope:
\[
I(U,W;G)+I(X;G\mid U,W)=I(X;G)=c.
\]
Thus every feasible point obeys
\[
R_1+R_2\le c
\]
for this reflected receiver pair. Combined with the universal lower bound and inclusion of the reflected class in the unrestricted class, this proves the stated equality.

### Certification qualification

The exact script verifies that the hard-coded `SL(1,U)` coefficient becomes identically one when all four sampled curves coincide. The included coercivity audit also implies the universal lower bound, since the coercive function satisfies \(F(x)\ge c\).

However, the checker under `frontier-global-bridge` is not the checker described in that artifact’s reproduction section. In particular, it does not print the claimed direct `W=X` audit messages. Thus the prose proof and row table, rather than the described executable output, carry the direct \(W=X\) argument.

The supplied code still supports the mathematical conclusion for the encoded 30-row system, but it does not independently certify that those rows are an exact transcription of the external manuscript.

### Relation to capacity

Since the grid restriction lowers the inner auxiliary maximization,
\[
V_{Q_0}(G,K)\le B(G,K).
\]
Therefore the value \(c\approx0.311278\) is not a capacity upper bound and does not conflict with the much larger known achievable sum rate. The contribution states this direction correctly.

### Judgment

**Supported with high confidence for the supplied 30-row formulation, with a documentation and source-transcription qualification.**

---

## Finding 4: Midpoint coercivity for arbitrary receiver pairs

**Claim key:** `three-point-grid-midpoint-coercive-lower-bound`

### Proposition assessed

For
\[
g=I_G(1/2),\qquad k=I_K(1/2),
\]
define
\[
F(x)=\frac{2c\max\{c,x\}}{c+x}.
\]
Then
\[
B(G,K)\ge V_0(g,k)\ge\max\{F(g),F(k)\}.
\]
Consequently, if \(c\le U<2c\) and \(B(G,K)\le U\), then
\[
\frac{2c^2}{U}-c\le g,k\le\frac{Uc}{2c-U}.
\]

### Reduction of the \(Q_0\) hierarchy

On \(Q_0\), a mean-\(\tfrac12\) posterior law has equal endpoint masses. The claimed block parameterization
\[
A,U,V\ge0,\qquad A+U\le1,\qquad A+V\le1
\]
therefore gives the seven row-term coefficients
\[
A,\ U,\ V,\ A+U,\ A+V,\ 1-A-U,\ 1-A-V.
\]
Multiplying these coefficients by a receiver’s midpoint information correctly determines all its \(Q_0\) mutual-information terms. Thus the receiver dependence of the grid problem reduces to the two scalars \(g,k\).

### Witness families

The three supplied cases cover the square of possible midpoint values.

#### High case

For a selected value \(x\ge c\), the H witness gives symmetric rates
\[
R_1=R_2=\frac{cx}{c+x},
\]
hence sum
\[
\frac{2cx}{c+x}=F(x),
\]
independently of the other middle-letter value.

#### Low case

For \(0\le x\le y\le c\), the L witness gives
\[
R_1=R_2=\frac{c^2}{c+x},
\]
hence
\[
R_1+R_2=\frac{2c^2}{c+x}=F(x).
\]
Since \(F\) is decreasing on \([0,c]\), choosing \(x=\min\{g,k\}\) gives the larger of \(F(g)\) and \(F(k)\).

#### Crossing case

For \(x<c<y\), the X witness gives the low-side value
\[
F(x)=\frac{2c^2}{c+x}.
\]
The H witness, after exchanging the middle receivers, separately gives \(F(y)\). Since lower bounds may be established by different feasible witnesses, these two constructions together prove the maximum of the two values.

The X denominator is positive in the strict crossing case. Boundary cases are covered by H or L, so the apparent singularity when both offsets vanish creates no gap.

### Exact row audit

The included Python script:

- rebuilds 30 labeled rows from hard-coded path formulas;
- checks all H, L, and X block-box constraints;
- computes every row slack as an exact rational polynomial;
- verifies coefficientwise nonnegativity after substitutions by formal nonnegative variables;
- verifies the complete set of distinct slack polynomials claimed in the prose.

No floating-point or numerical optimizer is involved. Treating \(c\) as a formal nonnegative variable is legitimate here because the certificates establish stronger polynomial statements valid for all nonnegative parameter values satisfying the case substitutions.

Again, this certifies the hard-coded row system, while fidelity of those rows to the external manuscript remains an unverified transcription step.

### Passage to the full functional

The direction
\[
B(G,K)\ge V(1/2;G,K)\ge V_0(g,k)
\]
is correct:

- \(B\) takes a supremum over input priors, so it dominates the fair-prior value;
- the continuum fair-prior optimization includes all \(Q_0\)-supported witnesses, so it dominates the restricted-grid value.

No converse equality is asserted.

### Inversion to the midpoint window

For \(x\le c\),
\[
F(x)=\frac{2c^2}{c+x}\le U
\iff
x\ge\frac{2c^2}{U}-c.
\]
For \(x\ge c\),
\[
F(x)=\frac{2cx}{c+x}\le U
\iff
x\le\frac{Uc}{2c-U},
\]
where \(U<2c\) ensures a positive denominator. Since the lower endpoint is at most \(c\) and the upper endpoint is at least \(c\) when \(U\ge c\), these branchwise inequalities combine into the claimed interval.

### Judgment

**Supported with high confidence for the encoded 30-row \(Q_0\) problem.** It is a useful necessary localization condition, not a sufficiency result and not a proof of reflected optimality.

---

## Finding 5: Effect on the BSSC sum-capacity frontier

**Claim key:** `BSSC-sum-capacity-frontier-effect-of-Q0-foundations`

The transaction does not prove a new achievable rate or a smaller universal converse. In particular, it does not establish either
\[
C_{\mathrm{sum}}>0.3616428844\ldots
\]
or
\[
C_{\mathrm{sum}}<0.3693165688\ldots.
\]

The exact \(Q_0\) value \(c\) is a value of a restricted receiver optimization lying below the full fixed-receiver functional. It therefore cannot be substituted as a capacity converse. The midpoint window only eliminates receiver pairs whose midpoint informations are incompatible with a separately supplied upper threshold \(U\); it does not certify the global infimum of the full functional.

The transaction is consequently best classified as a structural and finite-grid foundation for a future converse calculation. Its own statement that it does not improve the capacity frontier is correct.

---

## Contradictions and missing evidence

### 1. Checker/documentation mismatch

The `frontier-global-bridge/FULL.md` reproduction section says its checker directly verifies the \(W=X\) table and prints messages such as:

> `PASS: W=X witness makes every RHS 0, I(X;Y), or I(X;Z)`

The supplied `frontier-global-bridge/verify_q0.py` is instead byte-for-byte the coercivity checker and prints H/L/X messages. Therefore:

- the reproduction description in `frontier-global-bridge/FULL.md` is inaccurate for the supplied file;
- running the two README commands executes duplicate mathematical content;
- the two runs are not independent corroborations.

This is a documentation contradiction, not a contradiction between the mathematical propositions.

### 2. Missing manuscript equations

Neither the complete equations (19a)–(19p) nor an externally checkable copy of the manuscript formulation is included. Thus the following remain asserted rather than independently certified by the transaction:

- that the single-output term audit is exhaustive;
- that the 30 hard-coded rows are exactly the manuscript rows;
- that the side-condition orientation and all row coefficients were transcribed correctly.

The symbolic calculations are exact after those rows are accepted.

### 3. Provenance assertions are not mathematical verification

The commit hashes, acceptance records, and byte-for-byte provenance are reported in the contribution, but the corresponding repository objects and judgment records are not supplied for independent comparison. They should not be used as substitutes for checking the proofs.

### 4. No continuum bridge

There is no proof of:

- a continuum receiver-cardinality bound;
- convergence of finite posterior grids to the full functional;
- interchange of a receiver infimum with a grid limit;
- reflected optimality for the full receiver optimization;
- a global certified minimization of \(B(G,K)\).

These are correctly listed as limitations and remain decisive missing ingredients for a new capacity converse.

---

## Contribution and attribution

The transaction attributes all three source artifacts and the port to Robert Raynor and expressly disclaims new authorship arising merely from the port. The supplied mathematical content is substantial: the marginalization argument, Carathéodory reduction, exact \(Q_0\) solution, and coercive witnesses are distinct contributions rather than numerical leads.

The reported historical acceptance and commit provenance cannot be independently verified from the supplied files, but there is no internal evidence contradicting the stated authorship.

---

## Final judgment

The mathematical claims are **substantively supported within their carefully limited scope**. The marginalization and finite-grid cardinality arguments are analytically convincing. The \(Q_0\) equality and coercivity theorem are backed by explicit witnesses and exact polynomial row checks.

The warranted qualifications are:

1. the connection to the external Theorem 9 formulation depends on an unverified row and term transcription;
2. the two supplied checker commands run the same checker, contrary to the first artifact’s reproduction description;
3. none of the results improves the governed capacity interval or resolves the continuum auxiliary-receiver optimization.

Subject to those qualifications, the transaction provides valid structural progress rather than a capacity-frontier result.
