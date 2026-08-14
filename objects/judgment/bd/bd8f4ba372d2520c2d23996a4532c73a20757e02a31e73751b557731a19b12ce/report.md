# Mathematical Judgment

## Overall assessment

The subject transaction supports a **credible exact exclusion theorem for a sharply defined subfamily of order-\(23\) candidate Gram matrices**: three-edge star perturbations of Ehlich block matrices. The mathematical reduction is coherent, the obstructions used are valid necessary conditions for a sign-matrix Gram factorization, and the supplied verifier is deterministic and uses exact integer or rational arithmetic throughout.

A static review of the formulas and code reveals no decisive mathematical error. The numerical classification totals remain computational claims unless the verifier is actually run, but the artifact is sufficiently complete to permit independent replay with only the Python standard library. The result is therefore best regarded as a strong, replayable computational proof of the stated **local family exclusion**, not as a determination of \(D_{23}\) or an improvement of either endpoint of the global interval.

No contradiction was found between the subject transaction and the two earlier supplied contributions. The record determinant and the universal \(2^{22}\)-divisibility are used correctly.

---

## Finding 1 — Classification of three-star perturbations up to parent-block symmetry

**Claim key:** `order-23-ehlich-three-star/orbit-classification`

### Proposition assessed

For every positive integer partition \(r=(r_1,\ldots,r_s)\) of \(23\), the transaction claims to enumerate, up to automorphisms of the parent Ehlich block matrix and permutations of the three leaves, all choices of four distinct vertices
\[
(c,\ell_1,\ell_2,\ell_3)
\]
defining a three-edge star perturbation. It reports:

- \(1{,}255\) partitions of \(23\);
- \(1{,}882{,}943\) feasible indexed center/leaf-block specifications;
- \(102{,}799\) canonical specifications.

### Decisive reasoning

The parent matrix
\[
E(r)=20I_{23}-J_{23}+4\operatorname{diag}(J_{r_1},\ldots,J_{r_s})
\]
is invariant under:

1. arbitrary permutations of vertices within each block; and
2. permutations of blocks having equal size.

The three leaves are unordered because permuting \(\ell_1,\ell_2,\ell_3\) does not alter the set of toggled edges. Consequently, an orbit is determined by:

- the block size occupied by each of the center and leaves;
- which selected vertices belong to the same parent block;
- the distinction between the center and the unordered leaves; and
- the capacity condition that no block supplies more selected vertices than its size.

The descriptor used in the verifier records exactly this information by assigning first-occurrence labels separately among blocks of each size and minimizing over leaf permutations. The reconstruction routine then chooses distinct representative vertices and verifies the descriptor is stable under re-canonicalization.

The recursive partition generator is exhaustive for nondecreasing positive partitions. The use of combinations with replacement for leaf blocks is also appropriate because leaf order is irrelevant while repeated block membership is allowed.

### Caveat about the implemented checks

The code test

```python
if set(expanded) != set(specs):
```

is not an independent completeness check: `specs` is itself constructed as the sorted set of `expanded`, so this equality is tautological. The real justification for the orbit quotient is the mathematical structure of the descriptor and reconstruction, not that particular assertion.

The README states, rather than fully proves, the converse lemma that two assignments have the same canonical descriptor exactly when they are related by equal-size block permutations and leaf permutations. That converse is nevertheless straightforward from the restricted-growth/first-occurrence labeling: for each block size, the labels encode precisely the equality relation among the selected parent blocks. No counterexample is apparent.

### Judgment

The classification method is mathematically sound. The exact totals are credible replayable computational outputs, though they are not independently derived in the prose. Confidence is high conditional on a successful verifier run.

---

## Finding 2 — Exact determinant formula for the perturbed matrices

**Claim key:** `order-23-ehlich-three-star/rank-two-determinant-formula`

### Proposition assessed

The determinant of every three-star perturbation is evaluated exactly using the inverse of the parent matrix and a rank-two determinant update.

### Parent determinant and inverse

Let
\[
H=20I_{23}+4\operatorname{diag}(J_{r_1},\ldots,J_{r_s}),
\qquad E(r)=H-J.
\]
Within a block of size \(r_i\), the determinant contribution of \(20I+4J\) is
\[
20^{r_i-1}(20+4r_i).
\]
Applying the rank-one determinant lemma for subtraction of \(J=\mathbf1\mathbf1^{\mathsf T}\) gives
\[
\det E(r)
=
20^{23-s}\prod_i(20+4r_i)\,
\Delta,
\qquad
\Delta=1-\sum_i\frac{r_i}{4(5+r_i)}.
\]

The supplied inverse formula
\[
(E(r)^{-1})_{xy}
=
\frac{\mathbf 1_{x=y}}{20}
-\frac{\mathbf 1_{i=j}}{20(5+r_i)}
+\frac{1}{16(5+r_i)(5+r_j)\Delta}
\]
is consistent with first inverting the block-diagonal matrix \(H\) and then applying the Sherman–Morrison formula to \(H-\mathbf1\mathbf1^{\mathsf T}\).

### Rank-two perturbation

Each toggled edge changes by:

- \(-4\) if its endpoints were in the same parent block, changing \(3\) to \(-1\);
- \(+4\) if they were in different blocks, changing \(-1\) to \(3\).

Writing
\[
v=\sum_{k=1}^3 a_k e_{\ell_k},
\]
the entire symmetric perturbation is
\[
e_cv^{\mathsf T}+ve_c^{\mathsf T}.
\]
The matrix determinant lemma then reduces the determinant correction to
\[
(1+e_c^{\mathsf T}E^{-1}v)^2
-
(e_c^{\mathsf T}E^{-1}e_c)(v^{\mathsf T}E^{-1}v),
\]
which is exactly what the verifier computes.

For all normalized-square survivors, the code reconstructs the full \(23\times23\) integer matrix and checks its determinant again by Bareiss elimination. This is a meaningful independent arithmetic cross-check against the rank-two formula.

### Exactness

All determinant-lemma calculations use `Fraction`, and all direct determinant calculations use integer-only Bareiss elimination with exact-division checks. There is no reliance on floating-point determinants.

### Judgment

The determinant formulas and their implementation are correct. The direct Bareiss comparison for the relevant survivors materially strengthens the computational evidence.

---

## Finding 3 — Exact threshold enumeration within the family

**Claim key:** `order-23-ehlich-three-star/record-threshold-enumeration`

### Proposition assessed

Among the \(102{,}799\) canonical specifications, the transaction reports:

\[
74{,}896
\]
with determinant strictly larger than the square of the published record determinant, and none with determinant exactly equal to that square.

### Relevance of the threshold

Let
\[
R=2^{22}\,3\,5^6\,67\,211.
\]
If \(G=AA^{\mathsf T}\), then
\[
\det G=(\det A)^2.
\]
Therefore a sign matrix satisfying \(|\det A|\ge R\) would require
\[
\det G\ge R^2.
\]
It is consequently sufficient to:

1. show there are no specifications with \(\det G=R^2\); and
2. exclude sign-matrix Gram factorizations for every specification with \(\det G>R^2\).

Candidates below \(R^2\) are irrelevant to the stated local theorem.

### Arithmetic consistency

The threshold coefficient used in the code is
\[
3\cdot5^6\cdot67\cdot211=662{,}671{,}875,
\]
so the threshold is correctly represented as
\[
(2^{22}\cdot662{,}671{,}875)^2.
\]

The code also requires every enumerated candidate determinant to be divisible by \(2^{44}\). This is consistent with the matrix entries: every entry of such a candidate is congruent to \(-1\pmod 4\), since the diagonal is \(23\) and the off-diagonal entries are \(3\) or \(-1\). Subtracting the first row from each of the remaining \(22\) rows yields a factor \(4^{22}=2^{44}\).

### Evidence limitation

The totals \(74{,}896\) and \(0\) are generated by exhaustive execution; they cannot be confirmed merely by inspecting the source. The code does, however, enumerate the stated finite space directly and compare exact integer determinants to the threshold. There is no random or heuristic component.

### Judgment

The threshold logic is correct, and the computational enumeration is a valid replayable certificate design. The exact numerical totals warrant high confidence after successful execution.

---

## Finding 4 — Normalized-square obstruction

**Claim key:** `order-23-sign-gram/normalized-determinant-square-condition`

### Proposition assessed

Of the \(74{,}896\) above-threshold specifications, \(74{,}792\) are excluded because
\[
\frac{\det G}{2^{44}}
\]
is not an integer square.

### Decisive proof

The earlier supplied divisibility contribution proves that every order-\(23\) sign matrix satisfies
\[
2^{22}\mid\det A.
\]
Thus, if \(G=AA^{\mathsf T}\),
\[
\frac{\det G}{2^{44}}
=
\left(\frac{\det A}{2^{22}}\right)^2,
\]
which must be an integer square.

The verifier computes the quotient exactly and applies integer square root, checking the result by squaring. Therefore every nonsquare quotient is conclusively incompatible with a sign-matrix Gram factorization.

This use of the prior divisibility result is valid. That result is also supported independently by the elementary normalization argument supplied in the earlier transaction.

### Judgment

This obstruction is decisive and correctly applied. Subject to the enumeration total, the exclusion of \(74{,}792\) specifications is fully justified.

---

## Finding 5 — Local Hasse-invariant obstruction

**Claim key:** `order-23-ehlich-three-star/local-quadratic-form-obstruction`

### Proposition assessed

Of the \(104\) above-threshold specifications whose normalized determinant is a square, \(83\) are excluded because their rational quadratic forms are not congruent to the identity form.

### Necessary condition

If \(G=AA^{\mathsf T}\) and \(A\) is nonsingular, then over \(\mathbb Q\)
\[
G=A I_{23} A^{\mathsf T}.
\]
Hence the quadratic form represented by \(G\) is rationally congruent to the identity form. In particular, after extension to every \(\mathbb Q_p\), it must have the same local Hasse invariant as the identity. The identity form has Hasse invariant \(+1\).

Thus finding a prime \(p\) for which
\[
\epsilon_p(G)=-1
\]
is a conclusive obstruction.

### Implementation review

The verifier:

1. constructs the full candidate matrix;
2. diagonalizes it by exact rational Schur complements;
3. independently recovers the same diagonal pivots as ratios of exact leading principal minors;
4. checks the product of pivots equals the determinant;
5. evaluates Hilbert symbols using the standard odd-prime and \(2\)-adic formulas; and
6. searches prime divisors of the exact normalized square root until it finds an invariant \(-1\).

The implemented formulas are standard:

- for odd \(p\), valuation and Legendre-symbol terms are combined correctly;
- for \(p=2\), the unit residues modulo \(8\) and the usual exponent formula are used.

A prime with invariant \(-1\) suffices; the search need not prove that no other prime works.

### Missing standalone certificates

The artifact does not list the \(83\) candidates and their detecting primes in a separate transcript. Instead, the verifier recomputes the candidates, factors the relevant roots, and performs the local-invariant tests during replay. This is still a valid proof artifact, but it means the numerical count cannot be audited without running the code.

### Judgment

The Hasse-invariant argument is mathematically valid, and the exact implementation appears correct. The reported count of \(83\) is a replay-dependent computational finding rather than a prose proof, but the supplied computation is sufficiently explicit.

---

## Finding 6 — Inverse-quadratic and aggregate cell-moment obstructions

**Claim key:** `order-23-ehlich-three-star/cell-moment-nonfactorization`

### Proposition assessed

The final \(21\) normalized-square candidates are excluded as follows:

- \(2\) have no possible sign-vector column satisfying the inverse quadratic condition;
- \(19\) admit individual column patterns but fail exact aggregate moment constraints, as certified by the supplied integer separating functionals.

### Inverse quadratic condition

If \(G=AA^{\mathsf T}\) and \(x\) is a column of \(A\), then \(x=Ae_k\) for some \(k\), and
\[
x^{\mathsf T}G^{-1}x
=
e_k^{\mathsf T}A^{\mathsf T}A^{-\mathsf T}A^{-1}Ae_k
=1.
\]
Thus every sign column must satisfy
\[
x^{\mathsf T}G^{-1}x=1.
\]

The chosen cells consist of the center and leaves as singleton cells and one residual cell for the unselected vertices of each nonempty parent block. The verifier checks directly that both \(G\) and \(G^{-1}\) have the required cell constancy. Consequently, the quadratic value depends only on the cell sums
\[
t_i=\sum_{a\in C_i}x_a.
\]

For a cell of size \(m\), the possible sums are exactly
\[
-m,-m+2,\ldots,m,
\]
so the enumeration in the verifier captures every parity-compatible sign-vector pattern. The formula used for the quadratic form correctly accounts for:

- the fixed diagonal contribution;
- within-cell terms proportional to \(t_i^2\); and
- twice the between-cell contributions \(t_it_j\).

If no enumerated pattern satisfies the equation, no sign column can exist. This decisively excludes the two `empty` cases.

### Aggregate moment condition

For the \(23\) columns \(x^{(1)},\ldots,x^{(23)}\) of a hypothetical factor \(A\),
\[
\sum_{k=1}^{23}t_i^{(k)}t_j^{(k)}
=
\sum_{a\in C_i}\sum_{b\in C_j}G_{ab}.
\]
This follows by expanding the cell sums and using
\[
G_{ab}=\sum_k A_{ak}A_{bk}.
\]

Each JSON certificate supplies an integer linear functional \(L\) in the count and moment coordinates such that:

- \(L\) is nonnegative on every individually admissible pattern;
- \(L\) is strictly negative on the required aggregate target.

If \(23\) admissible column patterns existed with the required total moments, summing their nonnegative functional values would have to equal the negative target value, a contradiction. This is a valid finite Farkas-type separation argument.

The verifier does not trust an LP solver. It reconstructs all admissible patterns and checks every stated inequality directly with exact integers. It also verifies that the \(21\) certificate entries are distinct, correspond to the remaining square candidates, do not overlap the Hasse-excluded set, and exhaust all \(104\) square candidates together with the \(83\) Hasse exclusions.

### Judgment

Both the inverse-quadratic condition and the aggregate-moment separation are valid necessary conditions. The certificate checking logic is exact and complete for the listed candidates. This is the strongest and most specialized part of the artifact, and no logical gap was found in it.

---

## Finding 7 — Combined exclusion theorem for the three-star family

**Claim key:** `order-23-ehlich-three-star/record-level-nonrealizability`

### Proposition assessed

No matrix in the stated three-star perturbation family can be the Gram matrix of an order-\(23\) sign matrix whose determinant reaches or exceeds the published record.

### Combined accounting

The supplied exact accounting is
\[
74{,}896
=
74{,}792
+83
+2
+19.
\]

The categories are:

1. \(74{,}792\) with nonsquare normalized determinant;
2. \(83\) with a local Hasse obstruction;
3. \(2\) with no admissible sign-column pattern;
4. \(19\) with an aggregate cell-moment separation.

There are reportedly no specifications exactly at the record square. Therefore every specification whose determinant could support \(|\det A|\ge R\) is excluded.

The conclusion follows provided the classification and reported exact counts replay successfully.

### Judgment

The local exclusion theorem is supported. The argument is a proof of nonrealizability for the precisely specified family, not merely a heuristic non-finding.

---

## Scope and consequences for \(D_{23}\)

The transaction does **not** establish any of the following:

- that every high-determinant candidate Gram matrix belongs to an Ehlich block perturbation family;
- that every three-edge perturbation is covered;
- that perturbations of other graph shapes are excluded;
- that Gram matrices with off-diagonal entries other than \(3\) and \(-1\) are excluded;
- a stronger global upper bound for \(D_{23}\);
- a larger determinant witness; or
- the exact value of \(D_{23}\).

In particular, nothing in the artifact justifies lowering the certified global upper endpoint. To obtain such a consequence, one would need an additional theorem showing that every sign matrix above some determinant threshold has a Gram matrix in the treated family, or an exhaustive classification of all other candidate families. No such theorem is supplied.

The contribution is therefore genuine **structural progress** but does not move the numerical interval for \(D_{23}\).

---

## Contradictions and missing evidence

### Contradictions

No mathematical contradiction was detected among the supplied materials.

- The record threshold agrees with the exact record contribution.
- The use of universal \(2^{22}\)-divisibility agrees with the earlier divisibility proof.
- The stated limitations are consistent with what the verifier actually treats.

### Missing or weaker evidence

1. **No execution transcript is supplied.**  
   The exact numerical totals depend on running the verifier. The source is complete and replayable, but static inspection alone cannot certify millions of generated cases.

2. **The orbit-completeness check contains a tautological diagnostic.**  
   Equality of `set(expanded)` and `set(specs)` does not independently validate the quotient. The classification remains persuasive because the descriptor can be justified mathematically, but that justification should ideally be presented as an explicit lemma.

3. **No separate Hasse certificate list is supplied.**  
   The detecting primes are found afresh during execution. This is acceptable for replay, though a compact candidate/prime transcript would make independent spot checking easier.

4. **No formal verification is claimed.**  
   The proof is an exact conventional program, not a proof-assistant development. This is a limitation of assurance level, not a mathematical contradiction.

None of these issues appears to invalidate the local theorem; they affect the degree and mode of verification.

---

## Attribution and priority

The subject transaction appropriately attributes:

- the Ehlich block framework to Ehlich;
- the record determinant and bound context to Orrick, Solomon, Dowdeswell, and Smith;
- the general candidate-Gram and local quadratic-form methodology to prior literature.

Within the supplied evidence, Robert Raynor provides the specific three-star canonicalization, exact enumeration
