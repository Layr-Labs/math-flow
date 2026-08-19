# Audit result

| Declared claim | Verdict |
|---|---|
| `maximal-determinant-23/universal-divisibility-upper-rounding` | **Invalid** |

## `maximal-determinant-23/universal-divisibility-upper-rounding`

**Verdict: Invalid.**

The universal divisibility and the improved upper endpoint are correct, but the declared claim also gives an incorrect value for the ordinary integer floor. Because the exact declared statement is a conjunction containing that false assertion, it cannot be accepted as valid.

### 1. Universal divisibility is verified

After signed column operations, the first row can be made all \(+1\). Signed row operations then make the first column all \(+1\), without changing the determinant except possibly its sign.

Subtracting the first row from each of the remaining \(22\) rows produces a matrix whose lower-left column is zero and whose other lower entries are \(0\) or \(-2\). Factoring \(-2\) from those \(22\) rows and expanding along the first column gives

\[
|\det A|=2^{22}|\det B|
\]

for an integral \(22\times22\) zero-one matrix \(B\). Thus

\[
2^{22}\mid \det A
\]

for every order-\(23\) sign matrix, including singular matrices.

The converse construction

\[
A(B)=
\begin{pmatrix}
1&\mathbf1^{\mathsf T}\\
\mathbf1&J-2B
\end{pmatrix}
\]

indeed satisfies

\[
\det A(B)=(-2)^{22}\det B.
\]

Taking \(B=I_{22}\) yields determinant \(2^{22}\), so the asserted common divisor is also sharp.

### 2. The divisibility-rounded upper endpoint is verified

Let

\[
d=2^{22}=4{,}194{,}304,\qquad
c=3\cdot5^6\cdot675=31{,}640{,}625.
\]

Since \(D_{23}/d\) is an integer and the supplied problem premise gives

\[
D_{23}\le d\,c\sqrt{505},
\]

it follows that

\[
D_{23}\le d\left\lfloor c\sqrt{505}\right\rfloor.
\]

The submitted square certificate is arithmetically correct:

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

Therefore

\[
\left\lfloor c\sqrt{505}\right\rfloor=711{,}034{,}613,
\]

and

\[
D_{23}\le
2^{22}\cdot711{,}034{,}613
=
2{,}982{,}295{,}321{,}444{,}352.
\]

This part of the claim is correct.

### 3. Decisive arithmetic defect: the ordinary floor is off by one

Set

\[
q=711{,}034{,}613,\qquad
S=c^2\cdot505,
\]

so that

\[
S-q^2=63{,}205{,}856.
\]

The real upper endpoint is \(d\sqrt S\). For an integer \(k\),

\[
(d\sqrt S)^2-(dq+k)^2
=
d\bigl(d(S-q^2)-2qk\bigr)-k^2.
\]

For \(k=186{,}422\),

\[
d(S-q^2)-2qk=296{,}429{,}465,
\]

and hence

\[
(d\sqrt S)^2-(dq+186{,}422)^2
=
1{,}243{,}280{,}537{,}605{,}276>0.
\]

For \(k=186{,}423\),

\[
d(S-q^2)-2qk=-1{,}125{,}639{,}761,
\]

so

\[
(d\sqrt S)^2-(dq+186{,}423)^2<0.
\]

All quantities are positive, and therefore

\[
dq+186{,}422
<
d\sqrt S
<
dq+186{,}423.
\]

Consequently, the correct ordinary floor is

\[
\left\lfloor 2^{22}c\sqrt{505}\right\rfloor
=
2{,}982{,}295{,}321{,}630{,}774,
\]

not

\[
2{,}982{,}295{,}321{,}630{,}773.
\]

Thus the actual improvement over the ordinary floor is

\[
2{,}982{,}295{,}321{,}630{,}774
-
2{,}982{,}295{,}321{,}444{,}352
=
186{,}422,
\]

rather than \(186{,}421\).

The supplied verification script contains the same off-by-one constant and therefore would fail its `isqrt(squared_real_bound)` check.

**Conclusion:** the principal upper bound is established, but the declared comparison value is false, making the exact declared claim **invalid**.
