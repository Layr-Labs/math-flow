# Exact exclusion of three-star Ehlich perturbations

## Claim

For a positive integer partition
$r=(r_1,\ldots,r_s)$ of $23$, let

\[
E(r)=20I_{23}-J_{23}
  +4\operatorname{diag}(J_{r_1},\ldots,J_{r_s}).
\]

Thus $E(r)$ has diagonal entries $23$, entry $3$ between distinct
coordinates in the same block, and entry $-1$ between different blocks.
Choose four distinct coordinates $c,\ell_1,\ell_2,\ell_3$. Form $G$ by
toggling each of the three symmetric off-diagonal pairs
$c\ell_1,c\ell_2,c\ell_3$ between $3$ and $-1$.

There is no $23\times23$ sign matrix $A$ such that

\[
AA^{\mathsf T}=G
\quad\text{and}\quad
|\det A|\ge
2^{22}\,3\,5^6\,67\,211
=2{,}779{,}447{,}296{,}000{,}000.
\]

Equivalently, no record-level or better sign Gram matrix occurs in this
three-toggle star family. This is an exact, natural distance-three subfamily,
not a classification of every three-toggle perturbation or of every candidate
Gram matrix at order $23$.

## Exact canonical classification

For each of the $1{,}255$ nondecreasing positive integer partitions of $23$,
the verifier first keeps the parent blocks distinguished. It chooses one
center block and an unordered multiset of three leaf blocks, retaining the
choice exactly when each block contains enough distinct selected vertices.
This gives $1{,}882{,}943$ fixed-component specifications.

The parent-block automorphism group permutes blocks of equal size, while the
three leaves may be permuted arbitrarily. For every leaf order, the verifier
labels equal-sized parent blocks by order of first occurrence in

\[
(c,\ell_1,\ell_2,\ell_3).
\]

The lexicographically least resulting four-token sequence

\[
(\text{block size},\text{first-occurrence label within that size})
\]

is the canonical descriptor. Two fixed-component choices have the same
descriptor exactly when these symmetries carry one to the other. The verifier
reconstructs four distinct representative vertices from every descriptor and
checks that canonicalization is idempotent. Exactly $102{,}799$
base-automorphism orbit specifications remain.

These are specifications relative to a parent block graph. A resulting graph
can have more than one parent description, including one at smaller edit
distance. Such overlap is harmless: the theorem quantifies over every eligible
parent and every eligible three-star toggle.

## Exact rank-two determinant enumeration

Set

\[
\Delta=1-\sum_i\frac{r_i}{4(5+r_i)}.
\]

The parent determinant is

\[
\det E(r)=20^{23-s}\prod_i(20+4r_i)\Delta.
\]

For coordinates $x,y$ in blocks $i,j$, respectively, the verifier uses the
exact inverse identity

\[
(E(r)^{-1})_{xy}
=\frac{\mathbf 1_{x=y}}{20}
-\frac{\mathbf 1_{i=j}}{20(5+r_i)}
+\frac{1}{16(5+r_i)(5+r_j)\Delta}.
\]

Let $a_k=-4$ when $c$ and $\ell_k$ belong to the same parent block and
$a_k=4$ otherwise, and put $v=\sum_k a_ke_{\ell_k}$. The three toggles
together have the rank-two form

\[
e_cv^{\mathsf T}+ve_c^{\mathsf T}.
\]

The verifier therefore evaluates the matrix-determinant-lemma correction as
one exact $2\times2$ determinant over the rationals. For every normalized
square survivor it also constructs the full $23\times23$ integer matrix and
independently recomputes its determinant by fraction-free Bareiss elimination.

The exact threshold enumeration is

\[
\begin{array}{c|r}
\text{class} & \text{number of canonical specifications}\\ \hline
\text{all three-star specifications} & 102{,}799\\
\det G>\bigl(2^{22}\,3\,5^6\,67\,211\bigr)^2 & 74{,}896\\
\det G=\bigl(2^{22}\,3\,5^6\,67\,211\bigr)^2 & 0.
\end{array}
\]

## Normalized-square obstruction for 74,792 specifications

Canonical transaction
`7b28860c418486cb41e6379e68cc355ff861b1a5` proves that every order-$23$
sign determinant is divisible by $2^{22}$. If $G=AA^{\mathsf T}$, then

\[
\frac{\det G}{2^{44}}
=\left(\frac{\det A}{2^{22}}\right)^2
\]

must be an integer square. Of the $74{,}896$ above-record specifications,
$74{,}792$ have nonsquare normalized determinant. Exactly $104$
normalized-square candidates remain.

## Local quadratic-form obstruction for 83 candidates

If $G=AA^{\mathsf T}$ and $G$ is nonsingular, then

\[
G=A I_{23}A^{\mathsf T},
\]

so $G$ is rationally congruent to the identity form. For $83$ candidates the
verifier finds a rational prime divisor $p$ of the exact normalized square
root for which the Hasse invariant satisfies

\[
\epsilon_p(G)=-1,
\]

whereas the identity form has invariant $+1$. It constructs each full
candidate matrix, performs exact rational Schur-complement diagonalization,
independently recovers the same pivots from fraction-free leading principal
minors, and evaluates the Hilbert symbols by explicit rational formulas. The
finite prime search is replayed rather than trusted from a transcript.

## Inverse-quadratic and cell-moment obstruction for 21 candidates

For each remaining candidate, the center and three leaves are singleton
cells. The unselected vertices in every parent block form one further cell
when nonempty. The verifier checks directly that both $G$ and $G^{-1}$ are
constant on every required diagonal, within-cell, and between-cell orbit.

For a sign vector $x$, let $t_i$ be its sum on cell $C_i$. Every column of a
hypothetical factor $A$ must satisfy

\[
x^{\mathsf T}G^{-1}x=1.
\]

The verifier enumerates every parity-compatible cell-sum pattern satisfying
this equation. Two candidates have no admissible pattern at all.

For each of the final $19$ candidates, `certificates.json` supplies an integer
linear functional on the count and cell-moment coordinates. If the columns of
$A$ had patterns $t^{(1)},\ldots,t^{(23)}$, their aggregate moments would
have to satisfy

\[
\sum_{k=1}^{23}t_i^{(k)}t_j^{(k)}
=\sum_{a\in C_i}\sum_{b\in C_j}G_{ab}.
\]

The verifier checks that each supplied functional is nonnegative on every
individually admissible pattern but strictly negative on the required
aggregate target. This exact Farkas separation excludes all $19$ candidates.
The LP used to discover a separator is not part of the proof and is not
trusted during replay.

The complete above-record accounting is

\[
74{,}896
=74{,}792\;\text{(nonsquare)}
+83\;\text{(Hasse)}
+2\;\text{(no column pattern)}
+19\;\text{(cell moments)},
\]

with no equality case and no unexcluded three-star specification.

## Reproduction

The replay uses only the Python standard library. From this contribution
directory, run:

```sh
python3 verify.py
```

The final line must be `verification: PASS`.

## Relationship to canonical work

This contribution continues registered direction
`near-record-gram-obstructions`, canonical registration transaction
`efb1cc4ce5b387eb94fc2358c3f5dd6585846092`.

The record threshold and exact witness are canonical transaction
`fb88b7832c0fa7e84c1583110a7df800571bca02`, represented in knowledge node
`exact-witness-certification/order-23-record-witness`. The universal
$2^{22}$ divisibility is canonical transaction
`7b28860c418486cb41e6379e68cc355ff861b1a5`, represented in node
`arithmetic-divisibility-reduction/universal-divisor` under primary judgment
`sha256:f6722db5b0fa49f20e948a0e36f8aaa83d1aaf1700db4823dd0b20df5aaddbe3`.

The exact block, one-toggle, and two-toggle exclusions prepared in the same
research program are separate local contributions. This artifact is
self-contained and does not assume that any unmerged local result is accepted
knowledge.

## Sources and attribution

The block family and determinant-bound framework originate in Hartmut Ehlich,
“Determinantenabschätzung für binäre Matrizen mit $n\equiv3\pmod4$,”
*Mathematische Zeitschrift* **84** (1964), 438–447,
<https://eudml.org/doc/170280>.

The exact candidate-Gram and local quadratic-form methodology is discussed by
Richard P. Brent, William Orrick, Judy-anne Osborn, and Paul Zimmermann,
“Maximal determinants and saturated D-optimal designs of orders 19 and 37,”
*Linear Algebra and its Applications* **441** (2014), 39–61,
<https://arxiv.org/abs/1112.4160>.

A modern survey is Patrick Browne, Ronan Egan, Fintan Hegarty, and Padraig
Ó Catháin, “A Survey of the Hadamard Maximal Determinant Problem,”
*Electronic Journal of Combinatorics* **28**(4) (2021), P4.41,
<https://doi.org/10.37236/10367>.

Robert Raynor contributes the three-star canonicalization, rank-two exact
enumeration, local-invariant and cell-moment exclusions, certificates,
documentation, and standard-library replay artifact supplied here.

## Limitations

This is structural progress, not quantitative movement of the global
$D_{23}$ interval. It treats only matrices with off-diagonal alphabet
$\{3,-1\}$ obtained from an Ehlich-block parent by toggling the three edges
of a $K_{1,3}$. It does not treat triangle, three-edge path, wedge-plus-edge,
or three-edge matching perturbations, matrices farther from every block graph,
or Gram matrices with other odd off-diagonal entries. It neither improves the
record nor lowers the global upper endpoint, and it does not determine
$D_{23}$. The replay is exact and deterministic but is not a proof-assistant
development.
