# Judgment of transaction `fb88b7832c0fa7e84c1583110a7df800571bca02`

## Overall assessment

The contribution is a valid, exact, and independently replayable verification artifact for the already published order-\(23\) witness. It supports the established lower bound

\[
D_{23}\ge 2^{22}\,3\,5^6\,67\,211
=2{,}779{,}447{,}296{,}000{,}000.
\]

It does **not** improve that lower bound, strengthen the upper bound, or determine \(D_{23}\). Those limitations are stated accurately by the contributor.

The determinant computation uses integer-only Bareiss elimination rather than floating-point arithmetic. The matrix and complete verifier are supplied, and the implementation is sufficiently small to audit and replay using the Python standard library.

---

## Finding 1 — Determinant of the displayed \(23\times 23\) sign matrix

**Claim key:** `determinant-of-the-displayed-order-23-sign-matrix`

**Claim assessed:** The matrix in `matrix.txt` is a \(23\times23\) matrix with entries in \(\{-1,+1\}\) and has

\[
|\det A|=2{,}779{,}447{,}296{,}000{,}000.
\]

### Assessment

This claim is supported with high confidence by the supplied artifact.

The matrix file visibly consists of sign strings, and the verifier enforces all of the relevant structural conditions:

- exactly \(23\) rows;
- exactly \(23\) characters in each row;
- no characters other than `+` and `-`;
- conversion of `+` to \(+1\) and `-` to \(-1\).

Thus a successful run cannot accidentally certify a matrix of the wrong order or one with inadmissible entries.

The determinant routine is a standard fraction-free Bareiss elimination:

\[
a^{(k+1)}_{ij}
=
\frac{a^{(k)}_{kk}a^{(k)}_{ij}
-a^{(k)}_{ik}a^{(k)}_{kj}}
{a^{(k-1)}_{k-1,k-1}}.
\]

The implementation has the important correctness features:

1. It copies the input rather than mutating the parsed witness.
2. It searches for a nonzero pivot within the active column.
3. It records the sign of every row interchange.
4. It performs every operation with Python integers.
5. It uses `divmod` and aborts unless every Bareiss division is exact.
6. It returns the final Bareiss entry with the accumulated row-swap correction.
7. It compares the absolute determinant computed from the matrix against the expected factor product, rather than merely printing a hard-coded value.

Row pivoting among the active rows does not invalidate Bareiss elimination; it corresponds to row permutations, whose determinant effect is exactly the sign accumulated by `determinant_sign`. If a required pivot did not exist, the routine would return zero, which would fail the subsequent nonzero determinant comparison.

The factor-product arithmetic is also consistent:

\[
2^{22}5^6=65{,}536{,}000{,}000,
\qquad
3\cdot67\cdot211=42{,}411,
\]

and hence

\[
65{,}536{,}000{,}000\cdot42{,}411
=
2{,}779{,}447{,}296{,}000{,}000.
\]

### Evidentiary qualification

No generated execution transcript or list of intermediate Bareiss pivots is included. Therefore, static reading of the transaction does not itself display the large determinant arithmetic step by step. This is not a material defect under the problem’s replayability standard: the complete input and deterministic exact verifier are present, and the code is short enough for independent audit. An independent execution remains the direct way to confirm the stated `verification: PASS` output.

---

## Finding 2 — Consequent lower bound for \(D_{23}\)

**Claim key:** `D23-at-least-2779447296000000`

**Claim assessed:**

\[
D_{23}\ge 2{,}779{,}447{,}296{,}000{,}000.
\]

### Assessment

This follows immediately from Finding 1. By definition,

\[
D_{23}
=
\max\{|\det B|:B\in\{-1,+1\}^{23\times23}\}.
\]

The displayed matrix is an admissible member of that set, so its absolute determinant is a lower bound for the maximum.

This is the same lower endpoint already given in the problem statement. Consequently, the contribution certifies the known lower bound but does not improve it.

---

## Finding 3 — Exact value or optimality at order \(23\)

**Claim key:** `D23-equals-2779447296000000`

**Claim assessed:** Whether the displayed lower endpoint is the exact value of \(D_{23}\).

### Assessment

The transaction provides no proof of this proposition.

The verifier examines only one explicit matrix. It does not:

- enumerate all \(23\times23\) sign matrices;
- classify possible Gram matrices;
- supply an exhaustive search certificate;
- prove that every larger candidate determinant is impossible;
- strengthen or round the stated analytic upper bound; or
- otherwise close the gap between the published lower and upper bounds.

Thus no conclusion about optimality follows from the exact determinant replay. In particular, the existence of a matrix attaining the known record does not imply that no matrix with a larger determinant exists.

The contribution itself expressly disclaims an optimality claim, so there is no internal contradiction on this point.

---

## Finding 4 — Improvement of the stated frontier bounds

**Claim keys:**

- `D23-lower-bound-strictly-above-2779447296000000`
- `D23-upper-bound-strictly-below-the-stated-general-upper-endpoint`

### Assessment

Neither proposition is supported by this transaction.

The determinant equals, rather than exceeds, the lower endpoint in the problem. No new matrix with a larger determinant is supplied. Likewise, the contribution contains no argument concerning the real-valued upper estimate, its floor, any determinant divisibility restriction, or any other improved upper bound.

The mathematical value of the transaction is therefore reproducibility and certification of the published witness, not movement of either numerical frontier.

---

## Provenance and attribution

The README attributes the matrix and determinant record to William P. Orrick, Bruce Solomon, Roland Dowdeswell, and Warren D. Smith, and limits Robert Raynor’s contribution to transcription, documentation, and construction of the compact exact verifier. That allocation is consistent with the stated purpose of the artifact and avoids making an unsupported discovery or priority claim.

The supplied SHA-256 values are useful for checking an externally retrieved arXiv archive and `matData.tex`, but the referenced archive and source file are not themselves included in the transaction. Consequently, the assertion that the matrix was transcribed row-for-row from that particular source version is not independently established solely by the included files. It can be checked through the cited versioned archive. This provenance qualification does not affect the determinant claim, which depends only on the included matrix and exact computation.

---

## Contradictions and missing evidence

There are no apparent mathematical contradictions among the README, matrix, verifier, and problem statement.

The principal absent evidence concerns claims the contribution does not make:

- no witness exceeding the published lower bound;
- no exhaustive nonexistence proof for larger determinants;
- no proof of equality for \(D_{23}\);
- no improved analytic or arithmetic upper bound;
- no search log or non-finding intended to characterize unexplored candidates.

These are limitations of scope rather than defects in the stated exact-replay claim.

## Final disposition

The transaction should be regarded as a sound exact replay artifact for the published order-\(23\) record matrix and its determinant. It certifies the known lower endpoint in a transparent, fraction-free, reproducible manner. It does not answer the unresolved maximality question or improve either bound.
