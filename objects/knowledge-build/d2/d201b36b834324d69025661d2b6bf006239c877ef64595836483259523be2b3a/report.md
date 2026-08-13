# Knowledge-Formation Report

## Node: root

**Title:** Research state for maximal-determinant-23  
**Type:** Root  
**Status:** Active

For

\[
D_{23}=\max\left\{|\det A|:A\in\{-1,+1\}^{23\times23}\right\},
\]

the current supplied judgments support the certified interval

\[
\boxed{
2{,}779{,}447{,}296{,}000{,}000
\le D_{23}\le
2{,}982{,}295{,}321{,}444{,}352
}.
\]

The lower endpoint is equivalently

\[
2^{22}\,3\,5^6\,67\,211.
\]

It remains certified by the explicit \(23\times23\) sign-matrix witness assessed in immutable primary judgment

`sha256:34be73e7adced95684a58544e50a7ce03a8781b860fa3ba1640129f3bdfb687d`.

That judgment found that the witness reproduces the published record rather than improving it. The new judgment supplies no matrix with a larger determinant, so the certified lower bound is unchanged.

The previously supplied real upper estimate is

\[
D_{23}\le 2^{22}\,3\,5^6\,675\sqrt{505}
      =2^{22}\cdot31{,}640{,}625\sqrt{505}.
\]

Immutable primary judgment

`sha256:f6722db5b0fa49f20e948a0e36f8aaa83d1aaf1700db4823dd0b20df5aaddbe3`

supports a stronger arithmetic rounding of that estimate. It finds that every order-\(23\) sign-matrix determinant is divisible by \(2^{22}\), so the quotient \(D_{23}/2^{22}\) is an integer. The exact floor calculation

\[
\left\lfloor31{,}640{,}625\sqrt{505}\right\rfloor
=711{,}034{,}613
\]

therefore gives

\[
D_{23}\le
2^{22}\cdot711{,}034{,}613
=
2{,}982{,}295{,}321{,}444{,}352.
\]

The ordinary integer floor of the real-valued endpoint is

\[
2{,}982{,}295{,}321{,}630{,}773,
\]

so the divisibility-rounded endpoint is \(186{,}421\) smaller. The new judgment characterizes this as an arithmetic sharpening only: it relies on, and does not rederive or strengthen, the supplied analytic inequality.

The exact value of \(D_{23}\) remains unresolved. In particular, the supplied judgments do not:

- prove that the published lower endpoint is optimal;
- exhibit a determinant strictly above that endpoint;
- establish that \(711{,}034{,}613\) occurs as a \(22\times22\) zero-one determinant;
- prove that the rounded upper endpoint is attainable;
- exclude the rounded upper endpoint through Gram, congruence, or other structural restrictions; or
- provide an exhaustive classification or search certificate.

The current program layer consists of:

- `exact-witness-certification` — the established program for exact, independently replayable certification of explicit sign-matrix witnesses and their determinants;
- `arithmetic-divisibility-reduction` — exact reduction of order-\(23\) sign determinants to zero-one determinants, universal divisibility, and arithmetic rounding of determinant bounds.

The best global lower and upper bounds and the unresolved exact-value question remain at the root because they span witness, arithmetic, analytic, classification, and search approaches.

**Provenance**

- Frontier source: William P. Orrick, Bruce Solomon, Roland Dowdeswell, and Warren D. Smith, *New lower bounds for the maximal determinant problem* (2003), arXiv:`math/0304410`.
- Existing-witness judgment: `sha256:34be73e7adced95684a58544e50a7ce03a8781b860fa3ba1640129f3bdfb687d`.
- Existing-witness subject transaction: `fb88b7832c0fa7e84c1583110a7df800571bca02`, ledger position 1.
- Arithmetic-reduction judgment: `sha256:f6722db5b0fa49f20e948a0e36f8aaa83d1aaf1700db4823dd0b20df5aaddbe3`.
- Arithmetic-reduction subject transaction: `7b28860c418486cb41e6379e68cc355ff861b1a5`, ledger position 2.
- No conflict records or reconciliation judgments were supplied.

## Change: root

The arithmetic-reduction judgment certifies an upper endpoint smaller than the previously retained integer floor, so the root’s global interval and upper-bound account must be updated. The lower endpoint and its witness remain unchanged. The same judgment establishes an independent, durable arithmetic-reduction agenda, requiring its addition alongside the existing witness-certification program.

## Node: arithmetic-divisibility-reduction

**Title:** Arithmetic divisibility and zero-one reduction for order 23  
**Type:** Program  
**Parent:** `root`  
**Status:** Active

This program organizes exact arithmetic reductions for determinants of \(23\times23\) sign matrices. Its established scope includes:

1. the determinant correspondence between normalized \(23\times23\) sign matrices and \(22\times22\) zero-one matrices;
2. the universal divisibility of order-\(23\) sign determinants by \(2^{22}\), including the sharpness of that universal divisor;
3. divisibility rounding of the supplied real upper estimate; and
4. exact replay of the relevant arithmetic constants and determinant examples.

According to immutable primary judgment

`sha256:f6722db5b0fa49f20e948a0e36f8aaa83d1aaf1700db4823dd0b20df5aaddbe3`,

these results produce the certified upper-bound improvement

\[
D_{23}\le2^{22}\cdot711{,}034{,}613
=2{,}982{,}295{,}321{,}444{,}352.
\]

The program does not presently include a derivation or improvement of the underlying real analytic estimate. It also contains no exhaustive test of all sign or zero-one matrices, no classification of candidate Gram matrices, no proof about endpoint attainability, and no restriction shown to apply specifically to near-maximal determinants.

The program contains the following durable nodes:

- `arithmetic-divisibility-reduction/sign-zero-one-correspondence`;
- `arithmetic-divisibility-reduction/universal-divisor`;
- `arithmetic-divisibility-reduction/rounded-upper-bound`;
- `arithmetic-divisibility-reduction/exact-replay`.

**Attribution**

The immutable judgment preserves attribution to Orrick, Solomon, Dowdeswell, and Smith for the supplied real upper estimate and published record matrix. It supports attribution to Robert Raynor for the assessed exact presentation and application of the normalization/divisibility argument, the numerical divisibility rounding, and the replay script. It does not establish historical priority for the general \(2^{n-1}\) divisibility observation or the sign/zero-one correspondence.

**Provenance**

- Primary judgment: `sha256:f6722db5b0fa49f20e948a0e36f8aaa83d1aaf1700db4823dd0b20df5aaddbe3`.
- Subject and direct evidence transaction: `7b28860c418486cb41e6379e68cc355ff861b1a5`, ledger position 2.
- Earlier bound and record evidence transaction: `fb88b7832c0fa7e84c1583110a7df800571bca02`, ledger position 1.
- No associated conflict or reconciliation record was supplied.

## Change: arithmetic-divisibility-reduction

This program is added because the accepted judgment establishes a coherent long-lived agenda—zero-one reduction, universal divisibility, divisibility rounding, and exact replay—that is independent of explicit record-witness certification and remains meaningful without reference to the originating transaction.

## Node: arithmetic-divisibility-reduction/sign-zero-one-correspondence

**Title:** Order-23 sign/zero-one determinant correspondence  
**Type:** Result  
**Parent:** `arithmetic-divisibility-reduction`  
**Status:** Established

Immutable primary judgment

`sha256:f6722db5b0fa49f20e948a0e36f8aaa83d1aaf1700db4823dd0b20df5aaddbe3`

supports the exact correspondence

\[
D_{23}
=
2^{22}
\max\left\{|\det B|:B\in\{0,1\}^{22\times22}\right\}.
\]

Under the judgment’s assessment, signed row and column operations normalize the first row and first column of any \(23\times23\) sign matrix without changing the absolute determinant. Subtracting the normalized first row from the remaining rows produces a lower-right block of the form \(-2B\), where \(B\) is a \(22\times22\) zero-one matrix. Consequently,

\[
|\det A|=2^{22}|\det B|.
\]

Conversely, for every \(B\in\{0,1\}^{22\times22}\), the sign matrix

\[
A(B)=
\begin{pmatrix}
1&\mathbf 1^{\mathsf T}\\
\mathbf 1&J-2B
\end{pmatrix}
\]

satisfies

\[
\det A(B)=(-2)^{22}\det B.
\]

The judgment therefore finds that neither direction loses determinant values after accounting for the factor \(2^{22}\).

The same judgment supports the quotient examples:

- \(B=0\) gives \(\det A(B)/2^{22}=0\);
- \(B=I_{22}\) gives \(\det A(B)/2^{22}=1\);
- \(B=C\oplus I_{19}\), with
  \[
  C=
  \begin{pmatrix}
  1&1&0\\
  1&0&1\\
  0&1&1
  \end{pmatrix},
  \qquad \det C=-2,
  \]
  gives \(\det A(B)/2^{22}=-2\).

According to the judgment, the quotient values \(0\) and \(1\) rule out any nontrivial residue class modulo \(m>1\) containing all order-\(23\) determinant quotients. The nonsingular quotient examples \(1\) and \(-2\) also exhibit both parities.

This conclusion is qualified: the examples do not exclude congruence, Gram, or other structural restrictions that apply only to matrices whose determinants are near the maximum.

**Provenance**

- Primary judgment: `sha256:f6722db5b0fa49f20e948a0e36f8aaa83d1aaf1700db4823dd0b20df5aaddbe3`.
- Subject and evidence transaction: `7b28860c418486cb41e6379e68cc355ff861b1a5`, ledger position 2.
- Relevant judgment finding: `order-23-sign-zero-one/determinant-correspondence`.
- No conflict record was supplied.

## Change: arithmetic-divisibility-reduction/sign-zero-one-correspondence

This result is added as a distinct durable reduction theorem because the primary judgment accepts both directions of the sign/zero-one correspondence and the resulting equality of the two maximal-determinant formulations, while preserving the stated limitation concerning near-maximal structural restrictions.

## Node: arithmetic-divisibility-reduction/universal-divisor

**Title:** Greatest universal divisor of order-23 sign determinants  
**Type:** Result  
**Parent:** `arithmetic-divisibility-reduction`  
**Status:** Established

Immutable primary judgment

`sha256:f6722db5b0fa49f20e948a0e36f8aaa83d1aaf1700db4823dd0b20df5aaddbe3`

supports the universal divisibility statement

\[
2^{22}\mid\det A
\qquad
\text{for every }A\in\{-1,+1\}^{23\times23}.
\]

The judgment finds that this includes singular matrices and follows from the normalized zero-one reduction

\[
|\det A|=2^{22}|\det B|.
\]

It further supports the sharpness statement that \(2^{22}\) is the greatest positive integer dividing the determinants of all order-\(23\) sign matrices. The assessed witness for sharpness takes \(B=I_{22}\) in

\[
A(B)=
\begin{pmatrix}
1&\mathbf 1^{\mathsf T}\\
\mathbf 1&J-2B
\end{pmatrix},
\]

which gives

\[
\det A(B)=2^{22}.
\]

Thus the judgment concludes that every universal divisor must divide \(2^{22}\), while \(2^{22}\) divides every determinant.

The sharpness of this universal divisor does not establish sharpness or attainability of any upper bound for \(D_{23}\). The judgment expressly leaves open the possibility of stronger restrictions that apply only in the high-determinant regime.

**Provenance**

- Primary judgment: `sha256:f6722db5b0fa49f20e948a0e36f8aaa83d1aaf1700db4823dd0b20df5aaddbe3`.
- Subject and evidence transaction: `7b28860c418486cb41e6379e68cc355ff861b1a5`, ledger position 2.
- Relevant judgment finding: `order-23-sign-determinant/universal-divisor`.
- No conflict record was supplied.

## Change: arithmetic-divisibility-reduction/universal-divisor

This result is added because the primary judgment accepts both universal \(2^{22}\)-divisibility and the separate sharpness claim identifying \(2^{22}\) as the greatest common universal determinant divisor. Its limitation regarding high-determinant structural restrictions is retained.

## Node: arithmetic-divisibility-reduction/rounded-upper-bound

**Title:** Divisibility-rounded upper estimate for \(D_{23}\)  
**Type:** Certified result  
**Parent:** `arithmetic-divisibility-reduction`  
**Status:** Established

Immutable primary judgment

`sha256:f6722db5b0fa49f20e948a0e36f8aaa83d1aaf1700db4823dd0b20df5aaddbe3`

supports the exact arithmetic sharpening

\[
D_{23}\le
2{,}982{,}295{,}321{,}444{,}352.
\]

The result uses, without rederiving, the supplied analytic estimate

\[
D_{23}\le2^{22}\cdot c\sqrt{505},
\qquad
c=3\cdot5^6\cdot675=31{,}640{,}625.
\]

By the established universal divisor, the judgment writes

\[
D_{23}=2^{22}q
\]

for a nonnegative integer \(q\). It then supports

\[
q\le\left\lfloor c\sqrt{505}\right\rfloor
=711{,}034{,}613.
\]

The accepted exact square certificate is

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

The middle value lies strictly between the adjacent squares, establishing the quoted quotient floor. The judgment also verifies

\[
2^{22}\cdot711{,}034{,}613
=
2{,}982{,}295{,}321{,}444{,}352.
\]

For comparison, the ordinary integer floor of the supplied real endpoint is

\[
\left\lfloor2^{22}c\sqrt{505}\right\rfloor
=
2{,}982{,}295{,}321{,}630{,}773,
\]

and the accepted difference is

\[
186{,}421.
\]

According to the judgment, this is the strongest rounding obtainable solely from a common universal determinant divisor, because \(2^{22}\) is the greatest such divisor. That qualification does not rule out stronger upper bounds based on Gram conditions, congruences, or other restrictions specific to high-determinant matrices.

The judgment does not establish that the quotient \(711{,}034{,}613\) occurs as a zero-one determinant, that the rounded endpoint is attainable, or that it is the exact value of \(D_{23}\).

**Provenance**

- Primary judgment: `sha256:f6722db5b0fa49f20e948a0e36f8aaa83d1aaf1700db4823dd0b20df5aaddbe3`.
- Arithmetic subject transaction: `7b28860c418486cb41e6379e68cc355ff861b1a5`, ledger position 2.
- Supporting transaction for the supplied analytic estimate: `fb88b7832c0fa7e84c1583110a7df800571bca02`, ledger position 1.
- Relevant judgment finding: `d23/divisibility-rounded-upper-bound`.
- No conflict record was supplied.

## Change: arithmetic-divisibility-reduction/rounded-upper-bound

This certified-result node is added to preserve the accepted arithmetic derivation behind the new global upper endpoint. It records the exact floor certificate and the judgment’s limits without converting the result into a claim about attainability or exactness.

## Node: arithmetic-divisibility-reduction/exact-replay

**Title:** Exact replay method for order-23 divisibility rounding  
**Type:** Method  
**Parent:** `arithmetic-divisibility-reduction`  
**Status:** Available with qualifications

Immutable primary judgment

`sha256:f6722db5b0fa49f20e948a0e36f8aaa83d1aaf1700db4823dd0b20df5aaddbe3`

assesses the supplied verifier as a reproducible exact replay artifact for the arithmetic constants and determinant examples used by the divisibility-reduction program.

The judgment reports that the verifier:

- uses integer arithmetic and integer square root rather than floating-point arithmetic;
- checks the quotient floor and ordinary endpoint floor exactly;
- checks multiplication producing the rounded endpoint;
- deterministically constructs the sign matrices arising from \(B=I_{22}\) and \(B=C\oplus I_{19}\);
- evaluates their determinants by integer Bareiss elimination; and
- checks exact divisibility at each Bareiss step.

The verifier is not an exhaustive test of all \(23\times23\) sign matrices or all \(22\times22\) zero-one matrices. The universal divisibility theorem rests on the symbolic argument accepted by the judgment rather than on computational enumeration. The code provides independently replayable consistency checks but does not classify near-maximal determinants or verify the attainability of the rounded endpoint.

No execution transcript was supplied. The judgment nevertheless finds that the code and displayed exact arithmetic permit independent replay without reliance on floating-point output or an opaque computation.

**Provenance**

- Primary judgment: `sha256:f6722db5b0fa49f20e948a0e36f8aaa83d1aaf1700db4823dd0b20df5aaddbe3`.
- Subject and evidence transaction containing the replay artifact: `7b28860c418486cb41e6379e68cc355ff861b1a5`, ledger position 2.
- Relevant judgment finding: `order-23-rounding/exact-replay`.
- No conflict record was supplied.

## Change: arithmetic-divisibility-reduction/exact-replay

This method node is added because the primary judgment accepts the verifier as a durable, independently replayable exact-arithmetic resource while expressly distinguishing it from exhaustive verification and noting the absence of an execution transcript.
