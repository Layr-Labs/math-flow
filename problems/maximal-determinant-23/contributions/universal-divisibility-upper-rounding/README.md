# Divisibility-rounded upper bound at order 23

## Claim

Every \(23\times23\) matrix \(A\) with entries in \(\{-1,+1\}\) satisfies

\[
2^{22}\mid\det A.
\]

Combining this universal divisibility with the real upper estimate in the
problem statement gives the strictly sharper exact endpoint

\[
D_{23}\le
2^{22}\cdot711{,}034{,}613
=2{,}982{,}295{,}321{,}444{,}352.
\]

For comparison, merely taking the integer floor of the displayed real
estimate gives \(2{,}982{,}295{,}321{,}630{,}773\), which is 186,421 larger.

## Divisibility proof and binary-core correspondence

Take an arbitrary sign matrix \(A\). Multiplying columns by signs makes its
first row all \(+1\), and then multiplying rows by signs makes its first column
all \(+1\). These operations change at most the sign of the determinant.

For each row after the first, subtract the first row. The first entry of every
such row becomes zero, and every other entry is either zero or \(-2\). Factoring
\(-2\) from each of these 22 rows and expanding along the first column gives

\[
|\det A|=2^{22}|\det B|
\]

for a \(22\times22\) zero-one matrix \(B\). This proves the claimed
divisibility, including when \(A\) is singular.

Conversely, every \(22\times22\) zero-one matrix \(B\) occurs in this way:
form the normalized sign matrix

\[
A(B)=
\begin{pmatrix}
1 & \mathbf 1^{\mathsf T}\\
\mathbf 1 & J-2B
\end{pmatrix}.
\]

The same row operation gives

\[
\det A(B)=(-2)^{22}\det B.
\]

In particular, \(B=I_{22}\) produces a sign matrix with determinant exactly
\(2^{22}\). Thus \(2^{22}\) is the exact greatest universal divisibility factor:
no larger integer divides the determinant of every order-23 sign matrix. The
correspondence also gives

\[
D_{23}=2^{22}
\max\{ |\det B|:B\in\{0,1\}^{22\times22}\}.
\]

There is likewise no nontrivial fixed congruence class for the quotient that
holds for all sign matrices: \(B=0\) and \(B=I_{22}\) give quotients 0 and 1,
respectively. To also exhibit both parities among nonsingular examples, take
the block diagonal zero-one matrix with leading block

\[
C=\begin{pmatrix}1&1&0\\1&0&1\\0&1&1\end{pmatrix}
\]

and remaining block \(I_{19}\). Its determinant is \(-2\), so the corresponding
sign matrix has determinant \(-2^{23}\). Thus the possible quotients
\(\det A/2^{22}\) already include 1 and \(-2\). This observation does not rule
out congruence or Gram restrictions confined to matrices near the upper bound;
none is claimed here.

## Exact rounding without floating point

Write the supplied real upper estimate as

\[
2^{22}c\sqrt{505},
\qquad
c=3\cdot5^6\cdot675=31{,}640{,}625.
\]

Since \(D_{23}/2^{22}\) is an integer, it is at most
\(\lfloor c\sqrt{505}\rfloor\). The following integer square comparisons are
an exact certificate for that floor:

\[
\begin{aligned}
711{,}034{,}613^2
&=505{,}570{,}220{,}884{,}059{,}769,\\
c^2\cdot505
&=505{,}570{,}220{,}947{,}265{,}625,\\
711{,}034{,}614^2
&=505{,}570{,}222{,}306{,}128{,}996.
\end{aligned}
\]

The middle integer lies strictly between the other two, so

\[
\lfloor c\sqrt{505}\rfloor=711{,}034{,}613.
\]

Multiplying by \(2^{22}\) yields the claimed exact upper bound.

## Reproduction

`verify.py` uses only Python standard-library integer arithmetic. It checks all
displayed constants and strict square inequalities, computes both the ordinary
integer floor and the divisibility-rounded endpoint, and exactly evaluates the
generated \(A(I_{22})\) by fraction-free Bareiss elimination to witness the
sharpness of the universal power of two.

From this contribution directory, run:

```sh
python3 verify.py
```

The final line must be `verification: PASS`.

## Provenance, attribution, and limitations

This contribution uses the real upper estimate already supplied in the
canonical problem statement; it does not rederive that analytic estimate. The
problem attributes the estimate to William P. Orrick, Bruce Solomon, Roland
Dowdeswell, and Warren D. Smith, “New Lower Bounds for the Maximal Determinant
Problem,” arXiv:math/0304410 (2003).

The previously certified lower witness and its exact replay are canonical
transaction
`fb88b7832c0fa7e84c1583110a7df800571bca02`. This contribution does not reuse
that matrix or claim a new lower bound. Its new content is the elementary
normalization/divisibility proof, exact integer rounding, and replay script.
These new proof, documentation, and verifier components are contributed by
Robert Raynor.

The argument proves the strongest rounding obtainable from a common universal
divisor, because the constructed \(A(I_{22})\) has determinant exactly
\(2^{22}\). It does not prove that coefficient \(711{,}034{,}613\) is attained,
classify high-determinant zero-one or Gram matrices, or exclude that coefficient
by a non-divisibility argument. Such an exclusion would be needed for any
further improvement beyond the endpoint claimed here. The elementary binary
core correspondence and the small quotient examples above revealed no safe
additional universal congruence or Gram-based rounding.
