# Judgment of transaction `7b28860c418486cb41e6379e68cc355ff861b1a5`

## Overall assessment

The transaction is mathematically correct and supplies a genuine certified improvement to the upper bound for \(D_{23}\). Its main contribution is arithmetic rather than analytic: it combines the supplied real upper estimate with the universal divisibility

\[
2^{22}\mid \det A
\]

for every \(23\times 23\) sign matrix. The resulting bound is

\[
D_{23}\le 2^{22}\cdot 711{,}034{,}613
=2{,}982{,}295{,}321{,}444{,}352.
\]

This is \(186{,}421\) below the ordinary integer floor of the supplied real upper endpoint. The proof is self-contained apart from its explicit reliance on that supplied analytic estimate, and the arithmetic certificate uses exact integer comparisons.

The transaction does **not** determine \(D_{23}\), improve the published lower bound, or prove that the new upper endpoint is attainable or even compatible with structural conditions on near-maximal matrices.

---

## Finding 1 — `order-23-sign-determinant-universal-divisor`

### Claim

For every \(A\in\{-1,+1\}^{23\times23}\),

\[
2^{22}\mid \det A.
\]

Moreover, \(2^{22}\) is the greatest positive integer dividing the determinants of all order-\(23\) sign matrices.

### Assessment

This claim is proved correctly.

Multiplying individual columns by \(-1\) as needed normalizes the first row to all \(+1\). Multiplying individual rows by \(-1\) then normalizes the first column to all \(+1\), without disturbing the already normalized first row. These operations preserve the determinant up to sign.

Subtracting the first row from each of the remaining \(22\) rows gives a matrix whose first column is

\[
(1,0,\ldots,0)^{\mathsf T}
\]

and whose lower-right \(22\times22\) block has entries in \(\{0,-2\}\). Thus this block is \(-2B\) for a zero-one matrix \(B\), and expansion along the first column gives

\[
\det A'=\det(-2B)=(-2)^{22}\det B.
\]

Since \(|\det A|=|\det A'|\), it follows that

\[
|\det A|=2^{22}|\det B|.
\]

This argument includes singular matrices, for which both sides may be zero.

The sharpness argument is also valid. For \(B=I_{22}\), the explicitly defined sign matrix

\[
A(B)=
\begin{pmatrix}
1&\mathbf 1^{\mathsf T}\\
\mathbf 1&J-2B
\end{pmatrix}
\]

satisfies

\[
\det A(B)=(-2)^{22}\det B=2^{22}.
\]

Therefore every universal divisor divides \(2^{22}\), while \(2^{22}\) divides every determinant. Hence the greatest universal divisor is exactly \(2^{22}\).

### Confidence

High. The proof is elementary, complete, and contains no unproved computational step.

---

## Finding 2 — `order-23-sign-to-zero-one-determinant-correspondence`

### Claim

There is a determinant-preserving correspondence, up to the factor \(2^{22}\), between normalized \(23\times23\) sign matrices and \(22\times22\) zero-one matrices:

\[
D_{23}
=
2^{22}
\max\left\{|\det B|:B\in\{0,1\}^{22\times22}\right\}.
\]

### Assessment

This claim follows from both directions established in the transaction.

Every sign matrix can be normalized by signed row and column operations and then reduced to a zero-one core \(B\), with

\[
|\det A|=2^{22}|\det B|.
\]

Conversely, every zero-one \(B\) gives a valid sign matrix \(A(B)\) via

\[
A(B)=
\begin{pmatrix}
1&\mathbf 1^{\mathsf T}\\
\mathbf 1&J-2B
\end{pmatrix},
\]

and subtracting its first row from the remaining rows gives

\[
\det A(B)=(-2)^{22}\det B.
\]

Thus neither direction loses possible determinant values after accounting for the factor \(2^{22}\). Taking maxima yields the stated equality.

The supplementary quotient examples are also correct:

- \(B=0\) gives quotient \(0\);
- \(B=I_{22}\) gives quotient \(1\);
- \(B=C\oplus I_{19}\), where
  \[
  C=\begin{pmatrix}
  1&1&0\\
  1&0&1\\
  0&1&1
  \end{pmatrix},
  \qquad \det C=-2,
  \]
  gives quotient \(-2\).

Consequently, no single residue class modulo any integer \(m>1\) contains all possible quotients \(\det A/2^{22}\), since the quotients already include \(0\) and \(1\). The examples with quotients \(1\) and \(-2\) also show both parities among nonsingular matrices.

This does not exclude additional congruence or Gram restrictions specifically for matrices near the maximal determinant, and the transaction correctly refrains from claiming otherwise.

### Confidence

High.

---

## Finding 3 — `D23-divisibility-rounded-upper-bound`

### Claim

The supplied real upper estimate implies the exact bound

\[
D_{23}\le 2{,}982{,}295{,}321{,}444{,}352.
\]

### Assessment

The derivation is correct.

Write the supplied estimate as

\[
D_{23}\le 2^{22}c\sqrt{505},
\qquad
c=3\cdot 5^6\cdot 675=31{,}640{,}625.
\]

By Finding 1, \(D_{23}=2^{22}q\) for a nonnegative integer \(q\). Therefore

\[
q\le c\sqrt{505}
\quad\Longrightarrow\quad
q\le \left\lfloor c\sqrt{505}\right\rfloor.
\]

The transaction supplies the exact square certificate

\[
711{,}034{,}613^2
=
505{,}570{,}220{,}884{,}059{,}769,
\]

\[
c^2\cdot505
=
505{,}570{,}220{,}947{,}265{,}625,
\]

and

\[
711{,}034{,}614^2
=
505{,}570{,}222{,}306{,}128{,}996.
\]

The middle number lies strictly between the other two, so

\[
\left\lfloor c\sqrt{505}\right\rfloor=711{,}034{,}613.
\]

Multiplication by \(2^{22}=4{,}194{,}304\) gives

\[
2^{22}\cdot711{,}034{,}613
=
2{,}982{,}295{,}321{,}444{,}352.
\]

The stated ordinary floor,

\[
\left\lfloor 2^{22}c\sqrt{505}\right\rfloor
=
2{,}982{,}295{,}321{,}630{,}773,
\]

is consistent with the exact `isqrt` check in the verifier. The difference is indeed

\[
2{,}982{,}295{,}321{,}630{,}773
-
2{,}982{,}295{,}321{,}444{,}352
=
186{,}421.
\]

Thus the transaction improves the integer upper endpoint, even though it does not strengthen the underlying real analytic inequality.

Because \(2^{22}\) is the greatest universal determinant divisor, this is the strongest rounding obtainable solely by replacing “integer” with “multiple of a common universal divisor.” It does not follow that no stronger upper bound can be obtained from structural restrictions on high-determinant matrices.

### Confidence

High. The decisive comparison is an exact integer-square certificate, with no floating-point dependence.

---

## Finding 4 — `exact-replay-method-for-order-23-rounding`

### Claim

The supplied verifier gives a reproducible exact check of the arithmetic constants and the determinant witnesses used to establish sharpness of the universal divisor.

### Assessment

The source is suitable as a replay artifact:

- all bound calculations use Python integer arithmetic and `isqrt`;
- the endpoint multiplication and ordinary floor are checked exactly;
- the matrices corresponding to \(B=I_{22}\) and \(B=C\oplus I_{19}\) are generated deterministically;
- their determinants are evaluated using integer Bareiss elimination;
- exact divisibility at each Bareiss step is checked.

The script is not, and does not claim to be, an exhaustive verification over all sign matrices. The universal statement is certified by the symbolic proof in the README, not by testing. This division between deductive proof and computational consistency checks is appropriate.

No execution transcript is supplied in the evidence, but the code and exact displayed arithmetic permit independent replay. The main upper-bound proof does not depend on trusting a floating-point output or an opaque computation.

---

## Contradictions and missing evidence

No mathematical contradiction appears between this transaction and the supplied published-record replay. The latter certifies the existing lower endpoint, while the subject transaction leaves that lower bound unchanged.

The resulting certified interval supported by the supplied material is

\[
2{,}779{,}447{,}296{,}000{,}000
\le D_{23}\le
2{,}982{,}295{,}321{,}444{,}352.
\]

The following remain unproved:

1. The transaction does not rederive the analytic bound
   \[
   D_{23}\le 2^{22}\,3\,5^6\,675\sqrt{505};
   \]
   it explicitly relies on the estimate supplied in the problem.

2. It does not exhibit a matrix exceeding the published lower endpoint.

3. It does not prove that \(711{,}034{,}613\) can occur as the zero-one determinant quotient.

4. It does not exclude the rounded endpoint, classify candidate Gram matrices, or establish optimality of the published record.

5. Sharpness of the *universal divisor* does not establish sharpness of the new *upper bound*. Restrictions valid only in the high-determinant regime could still lead to further rounding or exclusion.

These limitations are disclosed accurately in the transaction.

---

## Contribution and attribution

The published real upper estimate and existing record matrix remain attributed to Orrick, Solomon, Dowdeswell, and Smith. The subject transaction makes no conflicting lower-bound or priority claim.

The supplied evidence supports attribution to Robert Raynor for this exact presentation and application of the normalization/divisibility argument, the numerical divisibility rounding, and the replay script. It does not establish historical priority for the general \(2^{n-1}\) divisibility observation or the sign/zero-one correspondence, which are elementary methods independent of this particular submission.

## Final determination

**Accepted as a correct certified upper-bound improvement.** It provides a rigorous arithmetic sharpening of the order-\(23\) upper endpoint, but not a determination of \(D_{23}\) or a new lower record.
