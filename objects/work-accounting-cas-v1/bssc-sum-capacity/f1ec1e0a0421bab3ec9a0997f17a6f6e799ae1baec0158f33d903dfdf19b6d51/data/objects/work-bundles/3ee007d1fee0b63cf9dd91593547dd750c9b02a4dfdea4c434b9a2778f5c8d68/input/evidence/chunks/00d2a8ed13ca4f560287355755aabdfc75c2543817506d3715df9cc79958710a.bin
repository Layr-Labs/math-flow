# Uniform receiver-curve approximation and 30-row stability

## Claim and dependency boundary

This contribution has two logical dependencies, in canonical ledger order:

1. `e3c1036ca607539a5ebcddf3058e6014ac5c1cd9`
   (`theorem9-cited-premise-foundations`) supplies the premise-bound private-message
   30-row system, its optimization order, and its exact receiver-term audit.
2. `e2bbc1e210e496b3c834e658820fc90287f3b2c0`
   (`finite-grid-q0-foundations`) supplies the posterior-measure representation
   and the exact at-most-$N$ sampled-curve reduction on an $N$-point grid.

Starting from those accepted boundaries, this contribution proves:

1. an alphabet-independent input-prior continuity bound for every binary-input
   receiver $A$,
   \[
   |J_A(p)-J_A(p')|\le 2h_2(|p-p'|);
   \]
2. a compact generalized receiver-curve space whose finite-output curves are
   uniformly dense, quantitatively: for every finite grid $Q$ containing
   $\{0,1/2,1\}$, every generalized receiver has an at-most-$|Q|$-output
   replacement $A_Q$ satisfying
   \[
   \|J_A-J_{A_Q}\|_\infty
   \le \varepsilon_Q:=\min\{1,4h_2(\Delta_Q)\},
   \qquad
   \Delta_Q=\sup_{p\in[0,1]}\min_{q\in Q}|p-q|;
   \]
   a reflection-closed grid preserves an already reflected pair; and
3. exact stability coefficients for every row of the accepted 30-row system.
   If $G,K$ are replaced by receivers whose complete curves are within
   $\varepsilon_G,\varepsilon_K$, respectively, the right side of row $r$
   changes by at most
   \[
   a_r\varepsilon_G+b_r\varepsilon_K,
   \]
   with the table below.  In particular every row changes by at most
   $4\varepsilon_G+4\varepsilon_K$.

The rowwise theorem gives exact relaxed-system and strict-feasibility
corollaries.  It does **not** assert convergence or attainment for the
unrelaxed optimized functional $B(G,K)$, because its rate-free side
conditions may be active with zero margin.

## 1. Generalized receivers and their curves

Give the binary input its fair prior.  A generalized receiver is represented
by a Borel probability measure $m$ on $[0,1]$ satisfying

\[
\int_0^1 \rho\,dm(\rho)=\frac12.
\]

As in transaction `e2bbc1e210e496b3c834e658820fc90287f3b2c0`, this is the
fair-prior distribution of the posterior $\rho=P(X=1\mid A)$.  Conversely it
defines the two channel rows by the finite measures

\[
dT_{A|0}(\rho)=2(1-\rho)\,dm(\rho),\qquad
dT_{A|1}(\rho)=2\rho\,dm(\rho).
\]

Both have mass one.  Atomic $m$ are exactly finite-output receivers up to
splitting outputs with the same posterior.  For input prior $p$, define

\[
J_m(p)=I_p(X;A)=\int_0^1\psi(p,\rho)\,dm(\rho),
\]

where $\psi$ is the continuous integrand displayed in the finite-grid
dependency.  The standard zero-summand convention extends it continuously at
the corners of $[0,1]^2$.

## 2. Alphabet-free continuity in the input prior

Fix a receiver channel and let $0\le p\le p'\le1$, with
$\delta=p'-p$.  If $\delta=1$, both priors are deterministic and both mutual
informations vanish.  Otherwise write $P_0,P_1$ for the joint laws of
$(X,A)$ when $X$ is fixed to zero or one, and put

\[
R=\frac{(1-p')P_0+pP_1}{1-\delta}.
\]

Then the two joint laws are

\[
P_p=(1-\delta)R+\delta P_0,
\qquad
P_{p'}=(1-\delta)R+\delta P_1.
\]

Introduce the Bernoulli mixture label $E$.  In either mixture the exceptional
component has deterministic $X$.  Hence

\[
H_{P_p}(X)=(1-\delta)H_R(X)+I_{P_p}(X;E),
\]

and the analogous identity holds for $P_{p'}$.  Both correction terms lie in
$[0,H(E)]=[0,h_2(\delta)]$, so

\[
|H_{P_p}(X)-H_{P_{p'}}(X)|\le h_2(\delta).
\]

Conditioning on the receiver output gives, by the same chain rule,

\[
H_{P_p}(X\mid A)
=(1-\delta)H_R(X\mid A)+I_{P_p}(X;E\mid A),
\]

with both conditional correction terms again in
$[0,h_2(\delta)]$.  Therefore

\[
|H_{P_p}(X\mid A)-H_{P_{p'}}(X\mid A)|\le h_2(\delta).
\]

Subtracting conditional entropy from input entropy proves

\[
\boxed{|J_A(p)-J_A(p')|\le2h_2(|p-p'|).}
\]

The proof depends only on the binary input and is independent of the output
alphabet.  It applies to the generalized receivers above.

## 3. Quantitative finite-support approximation

Let $Q$ have $N$ points and contain $0,1/2,1$.  The accepted sampled-curve
argument applies without an atomicity assumption: the barycenter of the
continuous map

\[
\rho\longmapsto
(\rho,\psi(q_1,\rho),\ldots,\psi(q_{N-2},\rho))\in\mathbb R^{N-1}
\]

lies in the convex hull of its compact image.  Caratheodory's theorem supplies
an atomic measure $m_Q$ on at most $N$ points with the same mean and the same
curve values on all of $Q$.

For any $p$, choose $q\in Q$ with $|p-q|\le\Delta_Q$.  Exact matching at
$q$ and the continuity theorem give

\[
\begin{aligned}
|J_m(p)-J_{m_Q}(p)|
&\le |J_m(p)-J_m(q)|+|J_{m_Q}(q)-J_{m_Q}(p)|\\
&\le4h_2(|p-q|)\le4h_2(\Delta_Q).
\end{aligned}
\]

Here $\Delta_Q\le1/2$ because the grid contains both endpoints, so $h_2$ is
monotone on the relevant interval.  Since both curve values lie in $[0,1]$,
the stated minimum with one is also valid.

For the reflection-closed grid, if $m_Q$ matches $m$ on $Q$, then

\[
J_{m_Q^\circ}(p)=J_{m_Q}(1-p)
\]

matches $J_{m^\circ}$ on $Q$ and has the same uniform error.  Thus an already
reflected pair $(m,m^\circ)$ is approximated by the reflected finite pair
$(m_Q,m_Q^\circ)$.  This does not symmetrize an arbitrary pair.

A convenient explicit sequence is

\[
Q_M=\left\{\frac{j}{2M}:0\le j\le2M\right\}.
\]

It is reflection closed, has $N=2M+1$ points and mesh radius
$\Delta_{Q_M}=1/(4M)=1/(2(N-1))$.  Hence the support grows linearly while the
uniform error is at most

\[
\min\left\{1,4h_2\!\left(\frac1{4M}\right)\right\}\longrightarrow0.
\]

## 4. Compact receiver-curve completion

Let $\mathcal M_{1/2}$ be the set of Borel probability measures on $[0,1]$
with mean $1/2$.  It is weakly compact.  If $m_n\Rightarrow m$, continuity of
$\psi(p,\cdot)$ gives $J_{m_n}(p)\to J_m(p)$ for every fixed $p$.  The
alphabet-free modulus above is common to every curve, so a finite-net argument
upgrades pointwise convergence to uniform convergence.  Consequently

\[
m\longmapsto J_m
\]

is continuous from $\mathcal M_{1/2}$ into
$C([0,1])$ with the sup norm.  Its image is compact.  Section 3 shows that
finite-output receiver curves are uniformly dense in this compact image.

It follows, for example, that every continuous functional of finitely many
complete receiver curves attains its generalized-receiver optimum and has the
same infimum over finite-output curves.  This statement is not applied to
$B(G,K)$ here: continuity of that optimized constrained functional has not
been established.

## 5. Stability of mutual-information terms

Suppose $\|J_A-J_{A'}\|_\infty\le\varepsilon_A$.  For every finite Markov
chain $S-X-A$, posterior conditioning gives

\[
I(S;A)=J_A(q)-\mathbb E J_A(q_S),\qquad
I(X;A\mid S)=\mathbb E J_A(q_S).
\]

It follows that replacing $A$ by $A'$ changes any term of kind `W`, `U|W`,
`V|W`, `UW`, or `VW` by at most $2\varepsilon_A$, and any term of kind
`X|UW` or `X|VW` by at most $\varepsilon_A$.

Applying these weights to the exact raw terms in the accepted path-row
generator, after combining identical signed atoms within each row, gives:

| row | $a_r$ | $b_r$ | row | $a_r$ | $b_r$ |
|---|---:|---:|---|---:|---:|
| `F_Y_left` | 1 | 0 | `F_Y_right_minus_left` | 3 | 0 |
| `F_Z_left` | 0 | 1 | `F_Z_right_minus_left` | 0 | 3 |
| `N_Y(0)` | 0 | 0 | `N_Z(0)` | 0 | 0 |
| `N_Y(1)` | 4 | 0 | `N_Z(1)` | 0 | 4 |
| `N_Y(2)` | 4 | 4 | `N_Z(2)` | 4 | 4 |
| `R1A(0)` | 4 | 4 | `R2A(0)` | 4 | 4 |
| `R1A(1)` | 4 | 4 | `R2A(1)` | 4 | 4 |
| `R1A(2)` | 4 | 4 | `R2A(2)` | 4 | 4 |
| `R1T(0)` | 0 | 0 | `R2T(0)` | 0 | 0 |
| `R1T(1)` | 4 | 0 | `R2T(1)` | 0 | 4 |
| `R1T(2)` | 4 | 4 | `R2T(2)` | 4 | 4 |
| `SL(1,U)` | 3 | 4 | `SR(3,U)` | 4 | 3 |
| `SL(2,U)` | 4 | 3 | `SR(2,U)` | 3 | 4 |
| `SL(3,U)` | 4 | 4 | `SR(1,U)` | 4 | 4 |
| `SL(3,C)` | 4 | 4 | `SR(1,C)` | 4 | 4 |

Thus $a_r,b_r\le4$ for all 30 rows.

## 6. What the stability theorem does and does not imply

Write each accepted constraint as

\[
r_{1,r}R_1+r_{2,r}R_2\le L_r(H;G,K),
\]

where $H$ is the fixed auxiliary hierarchy.  This includes the rate-free rows,
whose left side is zero.  Define a rowwise $\eta$-relaxed system by replacing
the right side with $L_r+\eta_r$.

If $(R_1,R_2,H)$ is feasible for $(G,K)$, the same triple is feasible for the
approximating $(G',K')$ after relaxing row $r$ by

\[
\eta_r=a_r\varepsilon_G+b_r\varepsilon_K.
\]

The reverse statement holds with primed and unprimed receivers exchanged.
Consequently, if $V^{\boldsymbol\eta}$ denotes the rowwise-relaxed value,

\[
V(q;G,K)\le V^{\boldsymbol\eta}(q;G',K'),
\qquad
V(q;G',K')\le V^{\boldsymbol\eta}(q;G,K),
\]

and the same inequalities hold after taking $\sup_q$ to define relaxed
$B$-values.  A uniform relaxation
$\eta=4\varepsilon_G+4\varepsilon_K$ is always sufficient.

There is also an exact interior statement.  If a fixed triple has slack
strictly greater than $a_r\varepsilon_G+b_r\varepsilon_K$ in every row, then
the same rates and hierarchy remain feasible after receiver replacement.
Thus every strictly feasible witness survives all sufficiently fine grid
approximations.

What is missing for the original unrelaxed value is a theorem that near-optimal
hierarchies can be chosen with a uniform feasibility margin, or another
regularity argument controlling active rate-free constraints.  Uniform curve
convergence alone cannot change an equality constraint continuously into an
inequality in the required direction.  No such constraint qualification is
present in the two canonical dependencies, so this contribution deliberately
stops at the exact relaxed and strict-feasibility statements.

## 7. Deterministic audit

Run from this contribution directory:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 verify_stability.py
```

`verification.json` requests the same no-argument entrypoint under the pinned,
networkless `python-stdlib-3-13-v1` verifier.  The checker requires
`claims.json` to name exactly the two dependencies above, independently
rebuilds the accepted generic length-three path rows, combines identical raw
terms, applies the proved term weights, and checks all 30 reviewed
$(a_r,b_r)$ pairs and the global $(4,4)$ bound.  It also checks the exact
uniform-grid support and mesh formulas.  This is a mechanical coefficient and
drift audit; it does not computationally prove the entropy continuity argument,
Caratheodory's theorem, or compactness.

## Provenance, authorship, and limitations

The 30-row system, path formulas, posterior representation, and sampled-curve
reduction are attributed to their canonical dependency transactions.  The
common-mixture continuity proof, uniform full-curve consequence, compactness
formulation, and stability analysis were prepared in this contribution.

- The cited Gohari--Liu--Nair Theorem 9 remains an explicit premise; this
  contribution neither authenticates nor re-proves it.
- The theorem gives support bounds for uniform curve approximation, not a
  fixed exact cardinality for $B(G,K)$.
- It preserves an already reflected pair but does not prove reflected
  optimality or symmetrize arbitrary receiver pairs.
- It proves relaxed-system and strict-interior stability, not unrelaxed
  optimized-value convergence, minimax interchange, receiver attainment for
  $B$, a new numerical converse, or the exact BSSC sum-capacity.
