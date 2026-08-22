# Exhaustive directed certificate for two fixed BSSC transplant families

## Claim and exact scope

Let \(P\) be the governed half-skew BSSC and \(P^{\otimes2}\) its two-use
super-symbol channel. This contribution takes the two exact rational
\(2\times4\times4\times9\) laws

\[
p_r(w,u,v,i),\qquad r\in\{6,7\},\quad 0\leq i<9,
\]

from the vendored Huang--Liu--Liu certificate. For every deterministic map

\[
\phi:\{0,\ldots,8\}\longrightarrow\{00,01,10,11\},
\]

it forms

\[
p_{r,\phi}(w,u,v,x)
=\sum_{i:\phi(i)=x}p_r(w,u,v,i)
\]

and evaluates the half-weight Marton functional of this induced law on
\(P^{\otimes2}\). There are \(4^9=262{,}144\) maps per source law and
\(524{,}288\) law-map pairs in total.

The included standard-library verifier exhaustively evaluates all of them with
outward entropy intervals and proves

\[
\boxed{
0.5451904011322205365
\ \leq\
\max_{\substack{r\in\{6,7\}\\\phi:\{0,\ldots,8\}\to\{0,1,2,3\}}}
L_{1/2}(p_{r,\phi})
\ \leq\
0.5451904011322206215
}
\tag{1}
\]

bits per two uses. Canonical transaction
`88a1004f309460f3ec1cacdae88d30f88559f9bc` supplies the directed threshold

\[
2L_{\rm RTD}>
0.7232857688439092313268831563011740144159620214477211104074274596056014.
\tag{2}
\]

Thus every member of these two fixed-law deterministic-map families is
strictly below \(2L_{\rm RTD}\).

This is an exhaustive no-gain result only for the displayed finite family.
It does not cover stochastic relabelings, changes to \(p_r(w,u,v,i)\),
mixtures or reflected continuations, auxiliary optimization after relabeling,
or any local-search campaign. It is not an unrestricted Marton-additivity
theorem and not a capacity converse.

## 1. Pinned rational source laws

The file `source_certificate.json` is byte-identical to

`data/certificates/fixed_input/cc_certificate_e5e-7.json`

at commit

`cc33e854cb1c5e99cb18fe500f60a529fce136f8`

of
`https://github.com/yanxiaoliu-mike/Suboptimality_Marton`. Its fixed identity
is

`sha256:45502b2e7a694ae2d1beaee3e19249d63d9efe39b6405daa42ada0e1cbb846d6`

and its exact byte length is \(17{,}683\). The verifier fails closed unless
both agree. It reads only the two `winning_schemes` records, with source row
indices 6 and 7. Each record has axis order \((W,U,V,X_1X_2)\), shape
\((2,4,4,9)\), denominator \(10^{12}\), 288 nonnegative integer
numerators, and exact total numerator \(10^{12}\).

The external certificate was produced for a different ternary-input broadcast
channel. No theorem or numerical conclusion about that channel is imported
here. Only its two rational probability tables are used as explicitly
specified finite inputs to the present BSSC calculation.

## 2. Objective identity

For a finite law \((W,U,V)-X-(Y^2,Z^2)\), define the two Marton endpoints

\[
\begin{aligned}
E_Y&=I(W;Y^2)+I(U;Y^2\mid W)+I(V;Z^2\mid W)-I(U;V\mid W),\\
E_Z&=I(W;Z^2)+I(U;Y^2\mid W)+I(V;Z^2\mid W)-I(U;V\mid W),
\end{aligned}
\]

and \(L_{1/2}=(E_Y+E_Z)/2\). Expanding the mutual informations gives the
identity used by the verifier:

\[
\begin{aligned}
2L_{1/2}
={}&H(Y^2)+H(Z^2)+H(W,Y^2)+H(W,Z^2)\\
&-2H(W,U,Y^2)-2H(W,V,Z^2)+2H(W,U,V).
\end{aligned}
\tag{3}
\]

The half-skew BSSC product transitions, with both input and output
super-symbols ordered \(00,01,10,11\), have the following numerator matrices
over the common denominator four:

\[
4P_{Y^2\mid X^2}=
\begin{pmatrix}
1&1&1&1\\
0&2&0&2\\
0&0&2&2\\
0&0&0&4
\end{pmatrix},
\qquad
4P_{Z^2\mid X^2}=
\begin{pmatrix}
4&0&0&0\\
2&2&0&0\\
2&0&2&0\\
1&1&1&1
\end{pmatrix}.
\tag{4}
\]

Consequently every cell entering (3) is an exact integer multiple of
\(1/(4\cdot10^{12})\).

## 3. Directed entropy certificate

For an exact cell \(p=n/(4\cdot10^{12})\), the checker bounds

\[
h(p)=-p\log_2p
\]

as follows.

1. Python 3.13 `decimal.Context.ln` at 50 digits supplies a correctly rounded
   nearest value for \(\ln p\) and \(\ln2\). The adjacent representable
   decimals on both sides give strict enclosing endpoints.
2. Floor- and ceiling-rounded Decimal multiplication and division propagate
   those endpoints through \(-p\ln p/\ln2\).
3. Each cell interval is then rounded outward to an integer multiple of
   \(10^{-18}\) bits.

All subsequent work uses only integer interval endpoints. For positive entropy
terms in (3), the scan uses upper endpoints; for the two negative entropy
terms, it uses lower endpoints. Reversing those choices gives a lower
endpoint for a selected law.

The cache/reduction is exhaustive rather than heuristic. For each marginal
slice, zero source-label masses are deleted and all \(4^k\) assignments of
the remaining \(k\) labels are tabulated. A projection table sends every full
nine-digit map ID to its exact slice-table index. The final loop still visits
every map ID from 0 through \(4^9-1\), separately for both source laws. In the
frozen replay this produces 42 entropy tables, 24,610 distinct exact entropy
cells, and 13 exact projection patterns.

The verifier uses the base-four convention

\[
\operatorname{id}(\phi)=\sum_{i=0}^{8}\phi(i)4^i.
\tag{5}
\]

For source row 7, the representative

\[
\phi_*=(1,0,3,0,0,2,3,2,3),\qquad
\operatorname{id}(\phi_*)=243761,
\tag{6}
\]

has independent 100-digit orientation values beginning

\[
\begin{aligned}
E_Y&=0.546525784279605207250945323672001290\ldots,\\
E_Z&=0.543855017984835950952599789626220453\ldots,\\
L_{1/2}&=0.545190401132220579101772556649110872\ldots.
\end{aligned}
\tag{7}
\]

Its outward replay intervals are

\[
\begin{aligned}
0.546525784279605164&\leq E_Y\leq0.546525784279605249,\\
0.543855017984835909&\leq E_Z\leq0.543855017984835994,\\
0.5451904011322205365&\leq L_{1/2}
 \leq0.5451904011322206215.
\end{aligned}
\tag{8}
\]

The exhaustive scan proves that the last upper endpoint in (8) also bounds
every other row-7 map. The scan's first upper-argmax representative is map ID
226354,
\((2,0,3,0,0,1,3,1,3)\), which is obtained from (6) by transposing the two
BSSC input coordinates. Product-channel coordinate symmetry gives the same
exact objective. Source row 6 has the smaller certified upper bound

\[
L_{1/2}\leq0.545102886998895833.
\tag{9}
\]

Equations (8)--(9) prove (1), and comparison with (2) proves the scoped
no-gain conclusion.  This comparison has no hidden per-letter normalization:
the entropy scan and the dependency threshold are both in bits per two channel
uses.  The verifier compares the integer upper bound for \(2L_{1/2}\) directly
with the floor of twice the directed lower endpoint in (2), on the common
\(10^{-18}\)-bit scale.

## 4. Reproduction

Run from this contribution directory:

```text
python3 -I -B verify.py
```

The checker uses only the standard library, performs no writes or network
access, and directly executes all \(524{,}288\) law-map evaluations. A
representative replay takes about 14 seconds, comfortably inside the governed
`python-stdlib-3-13-v1` verifier's 300-second timeout. The source hash, exact
simplexes, channel mass preservation, objective orientation values, map count,
global upper bound, and strict threshold comparison are all fail-closed checks.

## Dependency, corrective provenance, and limitations

- Transaction `88a1004f309460f3ec1cacdae88d30f88559f9bc` is the sole direct
  mathematical dependency, and only supplies the directed value of
  \(2L_{\rm RTD}\).
- Canonical transaction
  `fdbb2d1e94e5106feda2dc473464c95d8622f896` previously recorded this
  transplant scan together with many unrelated local-search campaigns. Its
  static verifier did not replay the claimed exhaustive scan, and its broad
  empirical claim received an indeterminate primary judgment. It is cited
  here only as corrective provenance, not as a premise. This contribution
  vendors the exact source and re-executes only the finite transplant family
  inside the objective verifier.
- The Huang--Liu--Liu authors receive full attribution for the two source
  rational laws. The BSSC relabeling calculation, directed interval reduction,
  and corrective certificate are the present contribution.
- The result says nothing about another source law, a stochastic channel from
  the nine labels to four inputs, a convex mixture of transplanted laws, or a
  reoptimized \((W,U,V,X^2)\) law.
- A no-gain result for this family does not imply
  \(M(P^{\otimes2})=2M(P)\), determine the multiletter Marton rate, or furnish
  a BSSC capacity converse.

This is a contribution in the non-exclusive
`bssc-multiletter-marton-frontier` direction registered by canonical
transaction `7e1e52fe42fde37ba1964ef9ae5062daf8bb55f8`.
