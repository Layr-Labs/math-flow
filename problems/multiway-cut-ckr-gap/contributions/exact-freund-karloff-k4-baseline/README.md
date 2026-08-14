# Exact Freund--Karloff $k=4$ CKR baseline

## Claim

The committed `instance-k4.json` is a conventional four-terminal Multiway
Cut instance with 10 vertices, 24 edges, and rational weights.  Its exact
values are

\[
  \operatorname{CKR}=\frac{11}{12},\qquad
  \operatorname{OPT}=1,\qquad
  \frac{\operatorname{OPT}}{\operatorname{CKR}}=\frac{12}{11}.
\]

It is the $k=4$ member of the classical Freund--Karloff midpoint family.
This contribution is an exact, offline-replayable baseline, not a new lower
bound.

More generally, for every integer $k\geq 3$, define $H_k$ as follows.
Its terminals are $t_1,\ldots,t_k$, and it has one additional vertex
$m_{ij}$ for every $1\leq i<j\leq k$.  The only edges are:

- $t_i m_{ij}$ and $t_jm_{ij}$, each of weight
  \(a=1/(k-1)^2\); and
- the three edges of the triangle on
  \(m_{ij},m_{i\ell},m_{j\ell}\) for every $i<j<\ell$, each of
  weight \(b=3/(2k(k-1)^2)\).

Then

\[
 \operatorname{CKR}(H_k)=\frac{7k-6}{8(k-1)},\qquad
 \operatorname{OPT}(H_k)=1,
\]

and hence the exact ratio is

\[
 \frac{8(k-1)}{7k-6}
 =\frac{8}{7+1/(k-1)}.
\]

## Exact CKR certificate

Embed $t_i$ at $e_i$ and embed

\[
  m_{ij}\longmapsto \frac{e_i+e_j}{2}.
\]

Every edge then has half-ℓ1 length $1/2$.  There are
$k(k-1)$ terminal--midpoint edges and
$3\binom{k}{3}=k(k-1)(k-2)/2$ midpoint--midpoint edges, so the displayed
embedding has value

\[
 \frac12\left(k(k-1)a+3\binom{k}{3}b\right)
 =\frac{k}{2(k-1)}+\frac{3(k-2)}{8(k-1)}
 =\frac{7k-6}{8(k-1)}.
\]

Here is an exact first-order certificate that this feasible value is the LP
optimum.  For a nonzero coordinate difference on an edge, take the forced
subgradient $+1$ or $-1$ of the absolute value.  For a zero coordinate
difference:

- on a terminal--midpoint edge, take the subgradient with respect to the
  midpoint endpoint to be $+3/4$; and
- on a midpoint--midpoint edge, take it to be $0$.

At a fixed $m_{ij}$, the resulting objective subgradient in coordinate
$i$ or $j$ is

\[
  \frac{k-2}{2}b,
\]

while in any coordinate outside $\{i,j\}$ it is

\[
  \frac34a-b.
\]

The two quantities agree exactly:

\[
  \frac{k-2}{2}b=\frac34a-b
  =\frac{3(k-2)}{4k(k-1)^2}=:\mu.
\]

Thus the subgradient at every nonterminal is the constant vector
$\mu\mathbf 1$.  If $x$ is any other feasible embedding and $x^*$ is
the midpoint embedding, convexity gives

\[
 F(x)\geq F(x^*)+
 \sum_{i<j}\mu\sum_{r=1}^k(x_{m_{ij},r}-x^*_{m_{ij},r})
 =F(x^*),
\]

because both simplex vectors have coordinate sum one.  This proves the exact
CKR value without a floating-point solver.  `verify.py` constructs this
subgradient with `fractions.Fraction` and checks every sign, interval, and
stationarity equation for the committed $k=4$ instance.

## Integral optimum certificate

The lower bound uses a 64-case local lemma, which `verify.py` exhausts exactly.
Consider three terminals and their three pair midpoints.  Give each of the six
terminal--midpoint edges weight $1/6$, and each edge of the midpoint triangle
weight $1/4$.  Allow midpoint labels in $\{1,2,3,4\}$, with terminal labels
fixed.  Exact enumeration establishes:

1. every labeling costs at least $2/3$; and
2. every *non-opposite* labeling, in which $m_{ij}$ has label $i$, $j$,
   or $4$, costs at least $1$.

For completeness, the local lemma implies the lower bound for every $H_k$
as follows.  Average a copy of this weighted six-vertex graph over all
\(\binom{k}{3}\) terminal triples; call the resulting weighting $W$.  Given
an integral $k$-labeling $f$, collapse labels outside a selected triple to
label 4.  This can only remove cut edges.  Let $q$ be the number of pair
vertices $m_{ij}$ for which $f(m_{ij})\notin\{i,j\}$.  A selected triple
can fail to be non-opposite only if one of its pair vertices is labeled by the
third terminal of that triple.  Each of the $q$ offending pair vertices can
make only one triple bad, so at most $q$ triples are bad.  The two exact
local minima therefore give

\[
  C_W(f)\geq 1-\frac{q}{3\binom{k}{3}}.
\]

Next, let $W'$ put weight $1/\binom{k}{2}$ on every
terminal--midpoint edge and zero on the other edges.  The path
$t_i-m_{ij}-t_j$ cuts one edge if $m_{ij}$ has an endpoint label and two
otherwise, so

\[
  C_{W'}(f)=1+\frac{q}{\binom{k}{2}}.
\]

The convex combination

\[
  \frac{k-2}{k-1}W+\frac1{k-1}W'
\]

has exactly the weights $a$ and $b$ defining $H_k$.  Its two
$q$-coefficients cancel, proving $C_{H_k}(f)\geq1$.  Equality is attained
by labeling every $m_{ij}$ with $i$ for $i<j$: this cuts one outer edge
per pair and two inner edges per triple, at cost

\[
 \binom{k}{2}a+2\binom{k}{3}b=1.
\]

Hence the integral optimum is exactly one.  Independently of this family
proof, the verifier checks all $4^6=4096$ assignments of the six
nonterminals in the committed $k=4$ instance.

## Reproduction

Run from this contribution directory using Python 3 and only the standard
library:

```sh
python3 -I -B verify.py
```

Expected output:

```text
instance: k=4, |V|=10, |E|=24
base lemma: unrestricted=2/3, non-opposite=1
CKR optimum: 11/12 (exact subgradient certificate)
integral optimum: 1 (4096 assignments, 28 minimizers)
integrality ratio: 12/11
verification: PASS
```

The verifier rejects a malformed graph, a changed rational weight, a changed
embedding, a failed subgradient condition, or a different exact optimum.

## Provenance and attribution

The family and the bound
$8/(7+1/(k-1))$ are due to Ari Freund and Howard Karloff:

- Ari Freund and Howard Karloff, “A lower bound of
  $8/(7+1/(k-1))$ on the integrality ratio of the
  Călinescu--Karloff--Rabani relaxation for multiway cut,” *Information
  Processing Letters* 75(1--2):43--50, 2000,
  [DOI 10.1016/S0020-0190(00)00065-X](https://doi.org/10.1016/S0020-0190(00)00065-X).

Appendix A and Section 5 of the following primary paper give the six-vertex
weighting and explain the averaging/mixing view used above:

- Haris Angelidakis, Yury Makarychev, and Pasin Manurangsi, “An Improved
  Integrality Gap for the Călinescu--Karloff--Rabani Relaxation for Multiway
  Cut,” [arXiv:1611.05530v1](https://arxiv.org/abs/1611.05530v1), 2016.

The construction and lower-bound family are attributed entirely to Freund and
Karloff.  The added work here is the explicit canonical JSON instance, the
compact exact LP subgradient certificate, the standard-library exhaustive
checker, and a self-contained normalization audit.  No discovery or priority
claim is made for the mathematical family.

## Limitations and relation to the governed benchmark

- For $k=4$, $12/11\approx1.09091$, far below the governed lower
  benchmark $1.20016$.
- Even asymptotically, this family's ratios approach only
  $8/7\approx1.14286<1.20016$.  It therefore cannot improve either side of
  the bracket in the problem statement.
- The artifact is useful as a conventional-instance regression test and exact
  baseline.  It is not the auxiliary four-label non-opposite-cut value
  $8/7$, and it does not confuse that auxiliary value with a four-terminal
  CKR gap.
- The checker exhausts the $k=4$ integral instance and the local 64-case
  lemma.  The displayed argument, rather than a finite loop over arbitrary
  $k$, proves the full family.
- No new rounding scheme, $1.20016$ transfer, or upper-bound argument is
  supplied.

## Artifact authorship

The mathematical construction and gap family are by Ari Freund and Howard
Karloff.  Reconstruction, exact certificate design, JSON encoding, checker,
and documentation were produced by an OpenAI Codex research agent operating
the Math Flow solver workflow at Robert Raynor's request.  Any transcription,
normalization, proof, or implementation errors in this artifact are the
agent's.
