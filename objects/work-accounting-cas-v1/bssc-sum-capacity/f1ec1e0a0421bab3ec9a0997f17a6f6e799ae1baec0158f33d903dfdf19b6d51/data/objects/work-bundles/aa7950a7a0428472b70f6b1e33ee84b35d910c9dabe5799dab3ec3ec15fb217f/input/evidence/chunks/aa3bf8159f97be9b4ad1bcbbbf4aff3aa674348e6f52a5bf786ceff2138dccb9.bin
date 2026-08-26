# Finite-grid receiver reduction and exact Q0 foundations

## Claim and dependency boundary

This contribution has one logical dependency:

`e3c1036ca607539a5ebcddf3058e6014ac5c1cd9`
(`bssc-sum-capacity/theorem9-cited-premise-foundations`).

That accepted transaction supplies the private-message 30-row system, the
definitions and optimization order for $V(q;G,K)$, $B(G,K)$, $V_Q(G,K)$ and
$V_0(g,k)$, the input-only reduction, and

\[
C_{\rm sum}\le\inf_{G,K}B(G,K),\qquad
V_Q(G,K)\le V(1/2;G,K)\le B(G,K).
\]

Starting exactly from that boundary, this contribution proves one cohesive
finite-grid foundation:

1. if $Q\subset[0,1]$ has $N$ points and contains $\{0,1/2,1\}$, each
   finite-output binary-input receiver can be replaced by one with at most
   $N$ outputs without changing $V_Q$; the replacement also preserves the
   reflected class when $Q$ is reflection closed;
2. for $Q_0=\{0,1/2,1\}$ and
   $c=h_2(1/4)-1/2$, the unrestricted and reflected receiver infima both
   equal $c$; and
3. every finite-output input-only pair obeys the pointwise coercive floor
   \[
   B(G,K)\ge V_0(g,k)\ge\max\{F(g),F(k)\},\qquad
   F(x)=\frac{2c\max\{c,x\}}{c+x},
   \]
   so $c\le U<2c$ and $B(G,K)\le U$ imply
   \[
   \frac{2c^2}{U}-c\le g,k\le\frac{Uc}{2c-U}.
   \]

Here $g=J_G(1/2)$ and $k=J_K(1/2)$.  All receiver alphabets in the infima
are finite.  No part of this claim is a continuum cardinality theorem, a
grid-limit interchange, or reflected optimality for the full functional $B$.
Explicitly,

\[
c=h_2(1/4)-\frac12=\frac34\log_2\frac43\in(0,1),
\]

so every later probability weight involving $c$ is nonnegative and normalized,
and every denominator whose positivity uses $c$ is strictly positive.

## 1. Posterior measures and sampled channel curves

Give the binary input its fair prior.  After discarding zero-probability
outputs, represent a receiver $A$ by

\[
m=\sum_a m_a\delta_{\rho_a},\qquad
m_a=P(A=a),\quad \rho_a=P(X=1\mid A=a).
\]

Then $m$ is a finite atomic probability measure on $[0,1]$ with
$\sum_a m_a\rho_a=1/2$.  Conversely, every such measure defines a channel by

\[
T_{A|X}(a|0)=2m_a(1-\rho_a),\qquad
T_{A|X}(a|1)=2m_a\rho_a.
\]

The two rows are nonnegative and each sums to one, so this is an exact
correspondence up to splitting outputs with the same posterior.

For $q=P(X=1)$ put

\[
\ell_q(\rho)=(1-q)(1-\rho)+q\rho
\]

and, with the standard zero-summand convention,

\[
\psi(q,\rho)=
2(1-q)(1-\rho)\log_2\frac{1-\rho}{\ell_q(\rho)}
+2q\rho\log_2\frac{\rho}{\ell_q(\rho)}.
\]

Direct substitution gives the complete channel curve

\[
J_A(q)=I(X;A)=\int\psi(q,\rho)\,dm(\rho).
\]

In particular, $J_A(0)=J_A(1)=0$ and
$\psi(1/2,\rho)=1-h_2(\rho)$.  If $m^\circ$ is the pushforward under
$\rho\mapsto1-\rho$, then

\[
J_{m^\circ}(q)=J_m(1-q).
\]

## 2. Exact N-output reduction on an N-point grid

Write the nonendpoint points of $Q$ as $q_1,\ldots,q_{N-2}$ and define the
continuous map

\[
\Phi_Q(\rho)=
(\rho,\psi(q_1,\rho),\ldots,\psi(q_{N-2},\rho))
\in\mathbb R^{N-1}.
\]

The vector $\int\Phi_Q\,dm$ lies in the convex hull of
$\Phi_Q([0,1])$.  Caratheodory's theorem in $\mathbb R^{N-1}$ supplies a
convex combination of at most $N$ points with the same vector.  The first
coordinate preserves the mean $1/2$, so the combination represents a valid
receiver $A'$ with at most $N$ outputs.  The remaining coordinates, together
with the universal endpoint values, give

\[
J_{A'}(q)=J_A(q)\quad\text{for every }q\in Q.
\]

This step invokes the standard Caratheodory convex-hull theorem as an external
mathematical theorem; the deterministic certificate does not purport to
re-prove it.

For every Markov chain $S-X-A$, posterior conditioning gives

\[
I(S;A)=J_A(1/2)-\mathbb E[J_A(q_S)],\qquad
I(X;A\mid S)=\mathbb E[J_A(q_S)].
\]

Conditional versions include

\[
I(U;A\mid W)=
\mathbb E[J_A(q_W)]-\mathbb E[J_A(q_{U,W})].
\]

The dependency's exhaustive term audit shows that these identities cover
every receiver term in all 30 rows.  In a $Q$-supported hierarchy all
posteriors on the right belong to $Q$, and $1/2\in Q$.  Therefore replacing
$G$ or $K$ by its sampled-curve match leaves every row right side, the feasible
set, and the objective unchanged.  Applying the replacement independently to
both receivers proves the pointwise identity and hence

\[
\inf_{G,K\text{ finite}}V_Q(G,K)
=\inf_{|G|,|K|\le N}V_Q(G,K).
\]

No attainment is used: every pair on the left has an exactly value-preserving
pair on the right, while the right-hand class is a subset of the left.

If $Q$ is reflection closed, first replace $m$ by $m'$ and set the second
receiver to $m'^\circ$.  For $q\in Q$,

\[
J_{m'^\circ}(q)=J_{m'}(1-q)=J_m(1-q)=J_{m^\circ}(q),
\]

so the same argument gives

\[
\inf_{m\text{ finite}}V_Q(m,m^\circ)
=\inf_{|\operatorname{supp}m|\le N}V_Q(m,m^\circ).
\]

This preserves an already reflected pair; it does not symmetrize an arbitrary
pair.

## 3. Exact scalar form on Q0

On $Q_0=\{0,1/2,1\}$, every receiver curve used by the rows is determined by
its midpoint value.  For one auxiliary group, every $Q_0$-supported hierarchy
block has parameters

\[
A,U,V\ge0,\qquad A+U\le1,\quad A+V\le1.
\]

The coarse posterior law has mass $A/2$ at each endpoint and $1-A$ at the
midpoint.  The $U$ refinement moves $U/2$ from the midpoint to each endpoint,
and the $V$ refinement does the same with $V/2$.  Conversely, the mass, mean,
and martingale equations on $Q_0$ force this form.  Every admissible pair of
refinements is jointly realizable: use the corresponding revealing/erasure
kernels conditionally independently given $(X,W)$.  The accepted system uses
the $U$ and $V$ refinements separately and contains no joint $(U,V)$ receiver
term.  Thus, for a receiver with
midpoint information $x$, the seven row terms are

| kind | value |
|---|---:|
| $W$ | $Ax$ |
| $U\mid W$ | $Ux$ |
| $V\mid W$ | $Vx$ |
| $UW$ | $(A+U)x$ |
| $VW$ | $(A+V)x$ |
| $X\mid UW$ | $(1-A-U)x$ |
| $X\mid VW$ | $(1-A-V)x$ |

The four receiver values are therefore $(c,g,k,c)$.  Reversing the four
receivers and three auxiliary groups while exchanging $U$ with $V$ and
$R_1$ with $R_2$ permutes the complete row system.  Hence

\[
V_0(g,k)=V_0(k,g).
\]

## 4. Three exact primal witness families

Each family below sets $R_1=R_2=r$ and specifies all three triples
$(A_j,U_j,V_j)$.  The checker substitutes them into every one of the 30 rows
and all 15 nonnegativity/box slacks using exact rational-polynomial arithmetic.

### H: a selected middle value is at least c

For $x\ge c$ and arbitrary $y\in[0,1]$, put

\[
d=c+x,\quad a=x/d,\quad b=c/d,\quad r=cx/d,
\]

\[
(A_1,U_1,V_1)=(a,0,b),\quad
(A_2,U_2,V_2)=(a,b,0),\quad
(A_3,U_3,V_3)=(a,b,0).
\]

Since $a+b=1$, all block constraints hold.  For receiver values $(c,x,y,c)$
the witness is feasible and gives

\[
R_1+R_2=\frac{2cx}{c+x}=F(x).
\]

It is independent of $y$.  This proves the desired floor for any selected
middle receiver at least $c$, using the row symmetry when the selected
receiver is $K$.

### L: both middle values are at most c

For $0\le x\le y\le c$, use

\[
d=c+x,\quad a=x/d,\quad b=c/d,\quad r=c^2/d,
\]

\[
(A_1,U_1,V_1)=(a,b,0),\quad
(A_2,U_2,V_2)=(a,0,b),\quad
(A_3,U_3,V_3)=(a,0,b).
\]

This is feasible and gives

\[
R_1+R_2=\frac{2c^2}{c+x}=F(x).
\]

On $[0,c]$, $F$ is decreasing.  Taking
$x=\min\{g,k\}$ therefore gives $\max\{F(g),F(k)\}$.

### X: the middle values straddle c

For $0\le x<c<y$, put $d=c+x$, $\Delta=y-x$, and

\[
a=x/d,\quad b=c/d,\quad r=c^2/d,
\]

\[
A=\frac{c(y-c)+x(c-x)}{d\Delta},\qquad
V=\frac{c(c-x)}{d\Delta},
\]

\[
(A_1,U_1,V_1)=(a,b,0),\quad
(A_2,U_2,V_2)=(A,0,V),\quad
(A_3,U_3,V_3)=(b,a,0).
\]

Every entry is nonnegative and

\[
1-A-V=\frac{x(y-c)}{d\Delta}\ge0,
\]

which supplies the only non-obvious box constraint.  The witness gives the
low-side value $2c^2/(c+x)=F(x)$.  Independently, H applied to the high value
$y$ (after row symmetry if necessary) gives $F(y)$.  Since both are feasible,
$V_0(g,k)$ is at least their maximum.

H, L, and X, including their shared boundaries, exhaust $[0,1]^2$.  This
proves

\[
V_0(g,k)\ge\max\{F(g),F(k)\}.
\]

The dependency gives $B(G,K)\ge V_0(g,k)$, so the full pointwise inequality
follows without any continuum approximation.

## 5. Solving the Q0 receiver infima

For every $x\ge0$, $F(x)\ge c$: on $x\le c$ this is
$2c^2/(c+x)\ge c$, and on $x\ge c$ it is
$2cx/(c+x)\ge c$.  The pointwise floor therefore gives

\[
V_0(g,k)\ge c
\]

for every finite receiver pair.

For a matching upper construction, take the revealing-erasure receiver whose
fair-prior posterior measure is

\[
\frac c2\delta_0+(1-c)\delta_{1/2}+\frac c2\delta_1.
\]

It is a three-output receiver, is invariant under reflection, and has sampled
curve $(0,c,0)$ on $Q_0$, the same as both physical BSSC receivers.  When all
four sampled curves agree, the dependency row `SL(1,U)` becomes

\[
\begin{aligned}
R_1+R_2
&\le I(U_a,W_a;Y)+I(X;G\mid U_a,W_a)\\
&\quad +I(V_b;K\mid W_b)-I(V_b;G\mid W_b)\\
&\quad +I(V_c;Z\mid W_c)-I(V_c;K\mid W_c)\\
&=I(U_a,W_a;G)+I(X;G\mid U_a,W_a)=I(X;G)=c.
\end{aligned}
\]

Thus this reflected pair has $V_0\le c$.  Since the reflected class is a
subset of the all-pair class and the construction belongs to both,

\[
c\le\inf_{G,K\text{ finite}}V_{Q_0}(G,K)
\le\inf_{m\text{ finite}}V_{Q_0}(m,m^\circ)\le c.
\]

Both infima equal $c$.  The $N=3$ cardinality result shows that no larger
receiver alphabet is needed for either $Q_0$ infimum.

## 6. Exact midpoint window

Suppose $c\le U<2c$ and $B(G,K)\le U$.  The pointwise floor forces
$F(g),F(k)\le U$.  For a scalar $x\le c$,

\[
F(x)=\frac{2c^2}{c+x}\le U
\quad\Longleftrightarrow\quad
x\ge\frac{2c^2}{U}-c.
\]

For $x\ge c$, positivity of $2c-U$ gives

\[
F(x)=\frac{2cx}{c+x}\le U
\quad\Longleftrightarrow\quad
x\le\frac{Uc}{2c-U}.
\]

Applying the appropriate branch to $g$ and $k$ proves the claimed window.
It is necessary, not sufficient.

## 7. Deterministic certificate

Run from this contribution directory:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 verify_q0.py
```

`verification.json` requests the same no-argument entrypoint under the
networkless `python-stdlib-3-13-v1` verifier, with governed spec digest
`sha256:fc7ed06b77396fabc1da84694b4d8a08800843f41ad8ca4b9cd666b67ba60884`.

The checker requires `claims.json` to name exactly the one dependency above,
independently rebuilds all 30 path rows, and compares their canonical JSON
signature with the reviewed SHA-256 obtained from the dependency's
`make_path_rows` construction.  The signature contains each sorted label,
rate-coefficient pair, and raw `(group, kind, output, coefficient)` term.  This
is a local drift guard; the networkless checker does not fetch or independently
authenticate the dependency transaction.  Canonical dependency resolution is
the protocol and primary-judgment boundary.  The checker then verifies the complete H,
L, and X row-slack sets and all block-box slacks as coefficientwise
nonnegative polynomials after the stated substitutions.  It also verifies that
`SL(1,U)` has constant coefficient one when all four sampled curves agree.
No floating point, optimizer, third-party package, or network request is used.

## Provenance and authorship

The finite-grid argument and H/L/X witnesses are re-presented from the earlier
transaction `d638c346212db3e75f6a53dcebcfd09f55125852` and its attributed
Yukon source artifacts.  That transaction is provenance, not a declared
logical dependency: the proofs and certificate needed here are included
again, while the accepted 30-row boundary is supplied only by
`e3c1036ca607539a5ebcddf3058e6014ac5c1cd9`.  The original mathematical
artifacts are attributed there to Robert Raynor.  This repair does not claim
new authorship for them.

## Limitations

- The $N$-output result is exact only for a fixed finite posterior grid.  It
  supplies no receiver-cardinality bound for the continuum functional.
- $\inf V_{Q_0}=c$ is a solved lower-approximation rung.  Since
  $V_{Q_0}(G,K)\le B(G,K)$, it is not a capacity upper bound.
- The coercive window is necessary only; it gives no off-midpoint control or
  sufficient condition for the full receiver value.
- No limit interchange, compactness-based attainment, arbitrary-pair
  symmetrization, or equality of unrestricted and reflected infima for $B$ is
  asserted.
