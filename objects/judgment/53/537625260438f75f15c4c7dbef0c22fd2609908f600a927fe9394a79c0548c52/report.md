## `maximal-determinant-23/published-record-matrix-exact-replay`

**Verdict: valid**

### Matrix-format obligations

- `matrix.txt` contains exactly 23 rows.
- Direct counting confirms that every row contains exactly 23 characters.
- Every character is either `+` or `-`, and the parser maps these bijectively to \(+1\) and \(-1\).
- Thus the supplied artifact defines a complete matrix
  \[
  A\in\{-1,+1\}^{23\times23}.
  \]

### Determinant-verifier audit

The supplied `bareiss_determinant` routine correctly implements fraction-free Bareiss elimination:

\[
a'_{ij}
=\frac{a_{ij}p-a_{i k}a_{k j}}{p_{\mathrm{previous}}},
\]

where \(p=a_{kk}\). The relevant correctness points are satisfied:

- The input matrix is copied, so elimination does not corrupt the parsed witness.
- At each stage, a nonzero pivot is selected from the active column; an absent pivot correctly implies determinant zero.
- Row swaps are applied to the whole row, and their parity is accumulated in `determinant_sign`.
- Entries used elsewhere in the same elimination stage are not overwritten prematurely: the pivot row remains unchanged and `a[row][column]` is cleared only after that row’s trailing entries are updated.
- Every Bareiss division is performed with integer arithmetic and explicitly checked for zero remainder.
- Python integers have arbitrary precision, so there is no overflow or floating-point issue.
- After the final stage, `a[-1][-1]` is the determinant of the row-permuted matrix. Multiplication by the accumulated swap sign recovers the determinant of the original matrix.

The expected value is not used to produce the determinant; it is only compared with the independently computed Bareiss result. Exact replay on the supplied literal matrix reaches the stated absolute determinant.

### Arithmetic check

The factor product is

\[
3\cdot 5^6\cdot 67\cdot 211
=662{,}671{,}875,
\qquad
2^{22}=4{,}194{,}304,
\]

and therefore

\[
2^{22}\cdot3\cdot5^6\cdot67\cdot211
=4{,}194{,}304\cdot662{,}671{,}875
=2{,}779{,}447{,}296{,}000{,}000.
\]

This agrees with the verifier’s exact absolute determinant.

### Scope

Because the witness is a \(23\times23\) sign matrix, it certifies

\[
D_{23}\ge 2{,}779{,}447{,}296{,}000{,}000.
\]

That is precisely the already stated lower endpoint. The artifact does not establish a larger lower bound, a stronger upper bound, or optimality, and it does not purport to do so. No external provenance claim is needed for the mathematical determinant certificate.
