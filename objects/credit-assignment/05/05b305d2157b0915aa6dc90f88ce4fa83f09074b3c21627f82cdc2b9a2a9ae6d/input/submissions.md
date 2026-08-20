<contribution>
ordinal: 3
transaction_id: c70e1829a7c6a2a8cb8cfc2383f8abf825ac5ea6
contribution_id: code-induced-dependence-balance-and-entropy-no-go
author: Robert Raynor
<artifact path="problems/bssc-sum-capacity/contributions/code-induced-dependence-balance-and-entropy-no-go/README.md">
# Code-induced dependence balance and its entropy/copy obstruction

## Claims and exact scope

This is an attributed, independently audited port of the consecutive accepted
Yukon artifacts `upper-dependence-balance` and `upper-entropy-nogo`.  They form
one dependency-complete structural result: the first derives a necessary
condition from every deterministic private-message code, and the second proves
that a specified entropy-only relaxation of that condition cannot improve the
classical UV value.

### Finite-block code-induced balance

Let (A) and (B) be independent uniform private messages, encoded
deterministically over (n) uses of a finite-alphabet memoryless broadcast
channel.  Receiver (Y) estimates (A) with average error (p_1), and
receiver (Z) estimates (B) with error (p_2).  Define

\[
F_j=h_2(p_j)+p_j\log_2(N_j-1),\qquad \delta_j=F_j/n.
\]

For

\[
S_i=(Y^{i-1},Z_{i+1}^n),
\]

the exact telescope is

\[
\sum_{i=1}^n
\left[I(A;B\mid S_i,Y_i)-I(A;B\mid S_i,Z_i)\right]
=I(A;B\mid Y^n)-I(A;B\mid Z^n).
\]

Both endpoints are nonnegative, while Fano bounds them by (F_1) and
(F_2), respectively.  With independent uniform time (T), and

\[
U=A,\quad V=B,\quad W=S_T,\quad X=X_T,\quad Y=Y_T,\quad Z=Z_T,
\]

every such code therefore induces

\[
\left|I(U;V\mid W,T,Y)-I(U;V\mid W,T,Z)\right|
\le\max\{\delta_1,\delta_2\}.
\]

The complete induced law retains the fixed coordinate map:

\[
p(t,u,v,w,x,y,z)=\frac1n p_U(u)p_V(v)p(w\mid u,v,t)
\mathbf 1\{x=f_t(u,v)\}P_{YZ\mid X}(y,z\mid x).
\]

In particular, (U\perp V), (T\perp(U,V)), (X=f_T(U,V)), and the
realized state (W) cannot select another encoder map after (u,v,t) are
fixed.  The same variables satisfy four compatible rate rows:

\[
\begin{aligned}
R_1&\le I(U,W;Y\mid T)+\delta_1,\\
R_2&\le I(V,W;Z\mid T)+\delta_2,\\
R_1+R_2&\le I(U,W;Y\mid T)+I(X;Z\mid U,W,T)+\delta_1+\delta_2,\\
R_1+R_2&\le I(V,W;Z\mid T)+I(X;Y\mid V,W,T)+\delta_1+\delta_2.
\end{aligned}
\]

This is an exact sequence-level necessary condition.  The alphabets of the
messages and (W) grow with blocklength, so it is not by itself a fixed-
cardinality single-letter outer region.

### Exact entropy/copy no-go theorem

At uniform input, put

\[
h=h_2(1/4),\qquad c=h-1/2,\qquad r=h-3/4.
\]

Consider the coarse entropy relaxation that imposes:

- the complete seven nonempty entropies of the common-noise BSSC coupling,
  namely (H(X)=1), (H(Y)=H(Z)=h),
  (H(X,Y)=H(X,Z)=H(Y,Z)=3/2), and (H(X,Y,Z)=2);
- message/time independence, deterministic encoding, the fixed-map equality,
  the memoryless Markov equality, and exact dependence balance;
- every conditional BEC identity
  (I(L;Y,Z\mid K)=\tfrac12I(L;X\mid K)) for disjoint subtuples
  (L,K\subseteq\{U,V,W,T\}), with (L\ne\varnothing);
- the two sharp scalar BSSC posterior-support inequalities with right side
  (r).

There is an actual finite entropic point satisfying all these constraints for
which both direct sum branches equal

\[
\boxed{2h_2(1/4)-\frac54
=0.3725562489182657\ldots}.
\]

Consequently, adding any collection of universally valid finite-variable
information inequalities, including unknown non-Shannon inequalities, cannot
lower this relaxation below that value.  Nor can any finite sequence of
standard copy-lemma extensions: each copy step can be realized by conditional
resampling of the finite witness while preserving its original marginal and
objective.

The witness is deliberately not a binary BSSC distribution.  Its (X) is a
tuple of six nondegenerate independent binary components.  Exact binary-
posterior or other channel-specific consistency constraints exclude it and
remain viable.  The theorem obstructs only the stated entropy/copy refinement
route.

## Independent proof audit

For the balance theorem, set

\[
D_i=I(A;B\mid Y^i,Z_{i+1}^n),\qquad 0\le i\le n.
\]

The (i)-th balance summand is exactly (D_i-D_{i-1}), so no channel
inequality is hidden in the telescope.  Separate reliability bounds the two
endpoints.  The displayed fixed-map factorization follows because, conditional
on (A,B,T), the current input is fixed and the current memoryless output is
independent of the past/future outputs in (W).  The two sum-rate rows use the
conditioned Csiszar identity; their uncancelled remainders are respectively
(sum_i I(Y^{i-1};Y_i)) and
(sum_i I(Z_{i+1}^n;Z_i)), hence nonnegative.

For the no-go theorem, write (g(q)=I_Z(q)-I_Y(q)).  Direct differentiation
gives

\[
g''(q)=\frac{2q-1}{\ln(2)q(1-q)(1+q)(2-q)}.
\]

Thus (g) is concave to (1/2) and convex thereafter.  The exact identities

\[
g(1/5)=\frac85r,\qquad g'(1/5)=-2r
\]

show that the tangent (2r(1-q)) is a global upper support.  The posterior
mixture of mass (5/8) at (1/5) and (3/8) at (1) attains mean (1/2)
and support value (r); reflection gives the other direction.

The explicit entropic witness uses mutually independent binary components

| component | `C` | `A` | `B1c` | `B2c` | `Eu` | `Ev` | `Ny` | `Nz` |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| entropy | (2r) | (1-h) | (r) | (7/4-2h) | (1/2-r) | (r) | (1/2) | (1/2) |

and tuple variables

\[
\begin{aligned}
U&=(C,A,B2c,Eu),&V&=(B1c,Ev),\\
X&=(C,A,B1c,B2c,Eu,Ev),\\
Y&=(C,A,Ny),&Z&=(C,B1c,B2c,Nz),
\end{aligned}
\]

with (W,T) constant.  Since all entropies are affine expressions in (h),
the retained witness can be checked using exact rational coefficient
arithmetic and component-set intersections.

## Reproduction

Run the independent standard-library checker from this contribution directory:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 verify_exact_witness.py
PYTHONDONTWRITEBYTECODE=1 python3 -O verify_exact_witness.py
```

It verifies exactly, without floating-point arithmetic:

- positivity of all component entropies from
  (3/4<h_2(1/4)<7/8);
- the complete base entropy vector and all structural equalities;
- both zero-valued dependence-balance sides;
- all 65 disjoint-subtuple conditional BEC identities;
- both sharp support rows and both objective branches at
  (2h_2(1/4)-5/4).

It prints:

```text
PASS: exact affine-in-h component audit
PASS: 65 disjoint-subtuple BEC identities
PASS: dependence balance, support rows, and both objective branches
```

The two accepted source submissions are retained byte-for-byte under
`source-artifacts/`; they contain analytic proofs rather than executable
artifacts.  Their immutable SHA-256 hashes are:

```text
a11816b72452187bed84f3d9d32ef6fa2788f444077222fc66854ba2cf9cccc8  upper-dependence-balance/FULL.md
ad7b04c34212cb4dc7debc04fb4c0a37cb4dad1e91dcb14c0000104b8120b779  upper-entropy-nogo/FULL.md
```

For each file, the source-commit blob, official judgment-bundle submission
blob, and retained port blob are identical.

## Provenance, acceptance, and authorship

The read-only source repository is
`/Users/robert/eig/autoresearch/bssc/yukon-bssc-challenge`; its accepted
snapshot is `local-yukon/canonical` at
`1af4e641fcfd4c76ec382c4e7cd5bed32af15e9c`.

| artifact | source ref and commit | author | judgment commit and fingerprint | Yukon knowledge acceptance |
|---|---|---|---|---|
| finite-block dependence balance | `local-yukon/submissions/upper-dependence-balance`, `e723bc5d85270ff9119e17c07502b6836f91d46e` | Robert (`robert.raynor@gmail.com`) | `2f3e16a6f81ef6d90c003ee5058afc45a20a0602`, `9707a391748afbad90dfbe3d6ac76fe416f132d89778a583e93019172cbc554f` | `c9222de0efdc2a89fbfcaf8d279f94348b8329dc` |
| exact entropy/copy no-go | `local-yukon/submissions/upper-entropy-nogo`, `73f22f13e1a5fa2f6b9c80934cc0d513bae40a30` | Robert (`robert.raynor@gmail.com`) | `43df61ac5aa0858639b1ff5c2a0c81fb172045bc`, `3ce2bbdfbadff26e6d427d563140d84693c5aef1ed376ba601a6181001defa56` | `6374c04275bda4ac538eaba84db03cbf0efba521` |

Both official judgments record `outcome: accepted`, with `accepted: true`,
`advisory: false`, and `mode: official`; their acceptance sequence numbers are
8 and 9.  The second source base is the formed state of the first, and its
theorem explicitly uses the first artifact's dependence balance and fixed-map
structure.  This dependency is why the two artifacts are kept together as one
coherent atomic contribution.

The port preserves Robert's original mathematical authorship.  The exact
checker was added only as an independent reproducibility audit and does not
claim new authorship of the accepted theorems.

## Capacity effect and limitations

There is **no capacity-frontier change**.  The canonical certified bound

```text
C_sum <= 0.369296945969202842443
```

remains unchanged.  The contribution supplies a code-induced necessary
condition and closes one coarse entropy/copy refinement route; it does not
make the value (0.3725562489182657\ldots) a new capacity bound.

- No fixed-alphabet support reduction is proved for the code-induced laws.
- The entropy counterfeit is not produced by the binary BSSC and is excluded
  by complete channel-specific posterior constraints.
- No achievability result, global converse optimization, capacity formula, or
  improvement over the existing upper bound is claimed.
- The result is an unregistered contribution.  It neither updates nor
  completes any research-direction event.

</artifact>
<artifact path="problems/bssc-sum-capacity/contributions/code-induced-dependence-balance-and-entropy-no-go/source-artifacts/upper-dependence-balance/FULL.md">
# A code-induced dependence-balance constraint for the BSSC

## Contribution and exact scope

This note proves a new necessary condition on the single-letter variables
induced by every reliable deterministic private-message code for the
two-receiver binary skew-symmetric broadcast channel (BSSC).  The condition is
an asymptotic dependence balance

```text
I(U;V | W,T,Y) - I(U;V | W,T,Z) -> 0,
```

where `U` and `V` are the two independent messages, `T` is the sampled time,
and `W` consists of the past `Y` outputs and future `Z` outputs.  Equivalently,
if the time index is included in `Wbar=(W,T)`,

```text
I(U;V | Wbar,Y) - I(U;V | Wbar,Z) -> 0.
```

The proof gives the exact finite-blocklength telescope, an explicit Fano
bound on the defect, four associated rate rows, and the complete induced-law
factorization.  That factorization retains the important fixed-encoder-map
condition: at time `T=t`, `X=f_t(U,V)` independently of the realized
past/future state `W`.

The result is qualitative.  It supplies no numerical capacity upper bound and
no finite-cardinality single-letter region.  In particular, it does not alter
the currently certified numerical BSSC upper bound.

## Channel and code model

All logarithms are base two.  The proof applies to every finite-alphabet
memoryless two-receiver broadcast channel and hence to the half-skew BSSC,
whose marginal channels (rows `x=0,1`, columns `0,1`) are

```text
P(Y|X) = [[1/2, 1/2],
          [0,   1  ]],

P(Z|X) = [[1,   0  ],
          [1/2, 1/2]].
```

Fix a blocklength `n`.  Let `A` and `B` be independent, uniform private
messages on finite sets of sizes `N_1,N_2 >= 2`.  A deterministic encoder is

```text
X_i = f_i(A,B),                 i=1,...,n.
```

The channel acts memorylessly according to any joint kernel `P_{YZ|X}` having
the stated BSSC marginals.  Receiver `Y` estimates `A`, receiver `Z` estimates
`B`, and their average error probabilities are `p_1,p_2`.  Define the Fano
quantities

```text
F_j = h_2(p_j) + p_j log_2(N_j-1),
delta_j = F_j/n,                j=1,2.
```

Fano's inequality gives

```text
H(A|Y^n) <= F_1,        H(B|Z^n) <= F_2.                (1)
```

The deterministic-code formulation loses no ordinary average-error
achievable rates: any randomized encoder can be conditioned on a realization
of its independent random seed having no larger sum of the two average error
probabilities.  The theorem below itself is stated only for deterministic
codes, so it does not otherwise rely on that reduction.

## The exact dependence telescope

For `i=1,...,n`, set

```text
S_i = (Y^{i-1}, Z_{i+1}^n),
```

with the natural empty-string conventions at the endpoints.  Also set

```text
D_i = I(A;B | Y^i,Z_{i+1}^n),       i=0,...,n.
```

Then, exactly at every blocklength,

```text
sum_{i=1}^n [ I(A;B | S_i,Y_i) - I(A;B | S_i,Z_i) ]
  = I(A;B | Y^n) - I(A;B | Z^n).                       (2)
```

Indeed, `(S_i,Y_i)=(Y^i,Z_{i+1}^n)` and
`(S_i,Z_i)=(Y^{i-1},Z_i^n)`.  The `i`th summand is therefore `D_i-D_{i-1}`,
so the sum telescopes from `D_0=I(A;B|Z^n)` to
`D_n=I(A;B|Y^n)`.  No channel inequality is hidden in (2).

Both endpoints are nonnegative, and (1) implies

```text
D_n <= H(A|Y^n) <= F_1,
D_0 <= H(B|Z^n) <= F_2.
```

Consequently

```text
abs( (1/n) sum_i
       [I(A;B | S_i,Y_i)-I(A;B | S_i,Z_i)] )
  <= max(delta_1,delta_2).                              (3)
```

Notice why separate reliability matters: decoder `Y` controls one endpoint
and decoder `Z` controls the other.

## Time sharing and the fixed-map law

Let `Q` be uniform on `{1,...,n}` and independent of the code and channel,
and define

```text
T=Q,       U=A,       V=B,       W=S_Q,
X=X_Q,     Y=Y_Q,     Z=Z_Q.                            (4)
```

Then (2)-(3) become

```text
abs( I(U;V | W,T,Y) - I(U;V | W,T,Z) )
  <= max(delta_1,delta_2).                              (5)
```

Equivalently, with `Wbar=(W,T)`, (5) is

```text
abs( I(U;V | Wbar,Y) - I(U;V | Wbar,Z) )
  <= max(delta_1,delta_2).                              (6)
```

The complete induced law has the factorization

```text
p(t,u,v,w,x,y,z)
 = (1/n) p_U(u) p_V(v) p(w|u,v,t)
     1{x=f_t(u,v)} P_{YZ|X}(y,z|x).                    (7)
```

In particular,

```text
U independent V,
T independent (U,V),
H(X|U,V,T)=0,
I(X;W|U,V,T)=0,
(U,V,W,T) - X - (Y,Z).                                 (8)
```

The fourth line is displayed even though it follows from the third, because
it records the structural point that is easily lost in relaxations.  For a
fixed `(u,v,t)`, the current input is the single value `f_t(u,v)`; `W` cannot
select another Boolean encoder map.  Retaining only
`H(X|U,V,W,T)=0` would be strictly weaker: it would allow a different map for
different `w`.  Likewise, writing `Wbar=(W,T)` is harmless for (6) only if the
distinguished component `T`, its independence from `(U,V)`, and the
`w`-independent map `f_t` in (7) are retained.

The factorization follows directly from the code.  Conditional on `(u,v,t)`,
the input word is fixed, `W` is generated by channel outputs at coordinates
other than `t`, and the current pair `(Y_t,Z_t)` is generated from `X_t` by
the memoryless channel independently of those other outputs.  This also shows
that (1)-(6) are invariant under the choice of joint coupling `P_{YZ|X}` with
the prescribed BSSC marginals.  Although `W` contains past `Y` and future `Z`,
none of those quantities contains both receiver outputs from the same channel
use; memorylessness therefore makes their laws depend only on the two marginal
channels.

For any reliable sequence with bounded rates, `p_{j,n}->0` implies
`delta_{j,n}->0`.  Thus the scalar defect in (5), or equivalently (6), tends
to zero.  This is the precise meaning of the asymptotic equality in this
submission.

## Four code-induced rate rows

Write `R_j=(1/n)log_2 N_j`.  The variables (4) also obey

```text
R_1 <= I(U,W;Y | T) + delta_1,                          (9a)
R_2 <= I(V,W;Z | T) + delta_2,                          (9b)

R_1+R_2 <= I(U,W;Y | T)
            + I(X;Z | U,W,T) + delta_1+delta_2,         (9c)

R_1+R_2 <= I(V,W;Z | T)
            + I(X;Y | V,W,T) + delta_1+delta_2.         (9d)
```

Here is a self-contained derivation, including the cross-term signs.

For the first individual row, Fano and the forward chain rule give

```text
nR_1
 <= sum_i I(A;Y_i | Y^{i-1}) + F_1
 <= sum_i I(A,S_i;Y_i) + F_1.
```

The second inequality only adjoins variables to the first argument: expanding
`I(A,S_i;Y_i)` produces the original term plus nonnegative mutual
informations.  Division by `n` gives (9a).  Reverse the chain rule for `Z^n`
to get (9b).

For (9c), message independence and Fano give

```text
n(R_1+R_2)
 <= I(A;Y^n) + I(B;Z^n | A) + F_1+F_2
  = I(A;Y^n) + I(X^n;Z^n | A) + F_1+F_2.               (10)
```

The equality uses deterministic encoding and the Markov chain
`(A,B)-X^n-Z^n`.

Put `P_i=Y^{i-1}` and `G_i=Z_{i+1}^n`, so `S_i=(P_i,G_i)`.  The conditional
Csiszar sum identity needed below is

```text
sum_i I(G_i;Y_i | A,P_i)
  = sum_i I(P_i;Z_i | A,G_i).                          (11)
```

For completeness, let `C_i=I(Y^i;Z_{i+1}^n|A)`.  Two chain-rule expansions
show

```text
C_i-C_{i-1}
 = I(Y_i;G_i | A,P_i) - I(P_i;Z_i | A,G_i).
```

Summing gives (11), because `C_0=C_n=0`.

Memorylessness gives

```text
I(X^n;Z_i | A,G_i) = I(X_i;Z_i | A,G_i),
I(P_i;Z_i | A,G_i,X_i) = 0.
```

Therefore, by direct chain-rule expansion,

```text
& I(A,S_i;Y_i) + I(X_i;Z_i | A,S_i)
  - I(A;Y_i | P_i) - I(X_i;Z_i | A,G_i)

= I(P_i;Y_i)
   + I(G_i;Y_i | A,P_i) - I(P_i;Z_i | A,G_i).          (12)
```

Summing (12), using (11), and dropping only the nonnegative quantity
`sum_i I(P_i;Y_i)` yields

```text
I(A;Y^n)+I(X^n;Z^n|A)
 <= sum_i [I(A,S_i;Y_i)+I(X_i;Z_i|A,S_i)].             (13)
```

Insert (13) into (10), divide by `n`, and use (4) to obtain (9c).

For (9d), interchange `(A,Y,forward)` with `(B,Z,reverse)`.  Explicitly, use

```text
n(R_1+R_2)
 <= I(B;Z^n)+I(X^n;Y^n|B)+F_1+F_2
```

and the same telescoping proof of

```text
sum_i I(P_i;Z_i | B,G_i)
  = sum_i I(G_i;Y_i | B,P_i).
```

The counterpart of (12) leaves the nonnegative remainder
`sum_i I(G_i;Z_i)`.  This proves (9d) and also checks that neither branch
depends on an unproved sign assumption.

## Exact residual-dependence decomposition

The balance has a useful algebraic relation to the two sum rows.  Define

```text
M = I(U;Y|W,T) + I(V;Z|W,T) - I(U;V|W,T),
d_Y = I(U;V|W,T,Y),
d_Z = I(U;V|W,T,Z),

B_1 = I(U,W;Y|T) + I(X;Z|U,W,T),
B_2 = I(V,W;Z|T) + I(X;Y|V,W,T).
```

Then the following are exact for every induced finite-`n` law:

```text
B_1 = I(W;Y|T) + M + d_Z,
B_2 = I(W;Z|T) + M + d_Y.                              (14)
```

To verify the first identity, (7) gives
`I(X;Z|U,W,T)=I(V;Z|U,W,T)`.  The chain rule gives

```text
I(V;Z|U,W,T)
 = I(V;Z|W,T)-I(U;V|W,T)+I(U;V|W,T,Z).
```

Adding `I(U,W;Y|T)` proves the first line of (14); the second is symmetric.
By (5), `d_Y-d_Z=o(1)` along every reliable bounded-rate code sequence.
Equation (14) isolates, but does not bound, the residual message dependence
that remains after revealing `W` and either current output.  Either residual
may grow with blocklength, so no estimate such as `d_Y<=H(X)` is asserted.

## Closure qualification and missing support reduction

The message alphabets and the alphabet of
`W=(Y^{Q-1},Z_{Q+1}^n)` grow with `n`.  Therefore (5) is an asymptotic scalar
constraint on the sequence of code-induced laws; by itself it is not a claim
that those laws possess a convergent subsequence on one fixed finite
alphabet.

Two exact readings of the limiting equality are justified:

1. Along every reliable bounded-rate code sequence, the difference of the
   two finite mutual informations in (5) tends to zero.
2. If a subsequence is represented on common finite alphabets by a separately
   proved reduction that preserves (5), (7), and the rate functionals, and
   those represented laws converge in total variation, continuity of finite
   mutual information gives
   `I(U;V|W,T,Y)=I(U;V|W,T,Z)` for the limiting law.

This submission does not supply that reduction.  In particular, a standard
support lemma applied separately conditional on `W` can destroy
`U independent V` or allow `W` to choose the encoder map.  A valid
cardinality/compactness theorem must simultaneously preserve:

```text
U independent V;                 T independent (U,V);
X=f_T(U,V);                      I(X;W|U,V,T)=0;
the two sides of (5);            all four rows (9).
```

Until that theorem or a safe monotone outer relaxation is proved, optimizing
over a chosen small alphabet is an inner search over only part of the
code-induced family and cannot yield a capacity upper bound.

## Validation, novelty, and limitations

The proof is analytic and finite-alphabet.  Its checkable core consists of:

- the endpoint-replacement telescope (2);
- the two Fano endpoint bounds leading to (3);
- the explicit induced factorization (7); and
- the conditioned Csiszar identity (11), with the nonnegative remainders in
  (12) and its receiver-swapped counterpart.

No numerical optimization, external theorem beyond elementary Fano and chain
rules, or computer calculation is used.  Exploratory small-alphabet searches
that motivated this contribution are deliberately not offered as evidence:
allowing `W` to select the map is an over-relaxation, while fixing small
alphabets for `U,V,W` is an under-approximation.  Values returned by either
kind of local floating-point search are neither capacity bounds nor global
evaluations of (5)-(9).

This contribution is distinct from the existing auxiliary-receiver and
equation-(16) programs.  Those optimize inequalities over broad auxiliary
families; (2)-(8) instead record structure inherited directly from independent
messages, separate reliability, and one fixed encoder coordinate in an actual
block code.  The useful advance is a rigorously scoped extra constraint and a
precise diagnosis of why it cannot yet be numerically exploited.

The principal open question is the support reduction just stated.  After it,
one would still need a certified global optimization, or a new BSSC-specific
inequality controlling the residual in (14), before any improved numerical
converse could be claimed.

</artifact>
<artifact path="problems/bssc-sum-capacity/contributions/code-induced-dependence-balance-and-entropy-no-go/source-artifacts/upper-entropy-nogo/FULL.md">
# An exact entropic counterfeit for BSSC entropy/copy relaxations

## Contribution and effect

This note proves a narrowly scoped no-go theorem for entropy-cone approaches
to the private-message sum rate of the half-skew binary skew-symmetric
broadcast channel (BSSC).  At the uniform input, there is an explicit *actual
finite distribution* with a nonbinary, tuple-valued `X` which simultaneously

- has the complete seven-coordinate entropy vector of the usual common-noise
  BSSC coupling `(X,Y,Z)`;
- satisfies message and time independence, deterministic encoding, the
  memoryless Markov equality, and the dependence-balance equality;
- satisfies every conditional entropy identity furnished by the fact that
  `(Y,Z)` is a `BEC(1/2)` observation of `X`; and
- satisfies at equality the two exact scalar BSSC posterior-support rows which
  give the corrected classical UV sum bound.

Both direct sum-rate branches at this entropic point equal

```text
2 h2(1/4) - 5/4 = 0.3725562489182657... .
```

Consequently, no collection of information inequalities valid for all finite
random variables, known or unknown, can remove this point.  Nor can any finite
standard copy-lemma hierarchy: the point is entropic, and every copy step has
a probabilistic realization.  Such an entropy-only relaxation therefore
cannot certify a value strictly below the displayed exact constant.

The quantifiers and limitation matter.  This is not a claim that
channel-specific inequalities are futile.  The construction is not generated
by a binary BSSC.  Exact binary-posterior constraints exclude it immediately,
and inequalities using those constraints remain a viable route.  The theorem
only closes the route that tries to replace those probability constraints by
universal entropy/copy inequalities on top of the particular coarse
equalities and two UV support directions listed below.  It is not a capacity
upper bound and makes no claim about the numerical optimum of a sampled LP.

## Channel notation and the exact UV support constant

Write

```text
h = h2(1/4),       c = h - 1/2,       r = h - 3/4.
```

For the common-noise coupling of the half-skew BSSC,

```text
N ~ Bernoulli(1/2),       N independent of X,
Y = X OR N,               Z = X AND N,
```

the pair `S=(Y,Z)` is a `BEC(1/2)` observation: `00` reveals input
zero, `11` reveals input one, and `10` is an erasure.  For a binary input with
`q=P(X=1)`, set

```text
IY(q) = h2((1-q)/2) - (1-q),
IZ(q) = h2(q/2)     - q,
g(q)  = IZ(q)-IY(q).
```

The exact upper concave envelope of `g` at `q=1/2` is `r`.  Here is a short
calculus proof, included so that the support rows used in the theorem do not
depend on a reported decimal.  On the open unit interval,

```text
g''(q) = (2q-1) / (ln(2) q(1-q)(1+q)(2-q)).
```

Thus `g` is concave on `[0,1/2]` and convex on `[1/2,1]`.  Direct substitution,
using `h=2-(3/4)log2(3)`, gives

```text
g(1/5)  = (8/5)r,       g'(1/5) = -2r.
```

The tangent at `1/5` is therefore `2r(1-q)`.  Concavity puts `g` below
this tangent on the left half.  On the right half, convexity and
`g(1/2)=g(1)=0` give `g(q)<=0<=2r(1-q)`.  Hence, for every random posterior
`q_A=P(X=1|A)` with mean `1/2`,

```text
E g(q_A) <= E[2r(1-q_A)] = r.                  (1)
```

Equality is attainable: put posterior `1/5` under an auxiliary atom of mass
`5/8` and posterior `1` under an atom of mass `3/8`.  Their mean is `1/2` and
their average `g` value is `r`.  Reflection, `g(1-q)=-g(q)`, gives the other
support direction.  Thus every genuine uniform-input binary BSSC obeys, for
any auxiliary tuple `A` preceding the channel,

```text
I(X;Z|A)-I(X;Y|A) <= r,
```

and the reflected inequality has the same sharp right side.

## Precise no-go theorem

Consider finite variables `(U,V,W,T,X,Y,Z)` and the following entropy
relaxation at the uniform input.

First impose the complete base entropy vector

```text
H(X)=1,
H(Y)=H(Z)=h,
H(X,Y)=H(X,Z)=H(Y,Z)=3/2,
H(X,Y,Z)=2.                                             (2)
```

Impose the code-structural equalities

```text
I(U;V)=0,                         I(T;U,V)=0,
H(X|U,V,T)=0,                     I(X;W|U,V,T)=0,
I(U,V,W,T;Y,Z|X)=0,                                      (3)
I(U;V|W,T,Y)=I(U;V|W,T,Z).                               (4)
```

Equation (4) is the dependence-balance equality obtained by telescoping
`I(M1;M2|Y^t,Z_{t+1}^n)` and taking the vanishing-Fano limit.  Keeping `T`
explicit avoids any relaxation caused by absorbing the time index into `W`.

For every two disjoint subtuples `L,K` formed from `{U,V,W,T}`, with `L`
nonempty, impose all conditional BEC entropy identities

```text
I(L;Y,Z|K) = (1/2) I(L;X|K).                            (5)
```

Finally impose the two sharp UV posterior-support rows from (1):

```text
I(X;Z|U,W,T)-I(X;Y|U,W,T) <= r,
I(X;Y|V,W,T)-I(X;Z|V,W,T) <= r.                         (6)
```

Define the two direct sum branches

```text
B1 = I(U,W;Y|T) + I(X;Z|U,W,T),
B2 = I(V,W;Z|T) + I(X;Y|V,W,T).                         (7)
```

**Theorem.**  The constraints (2)--(6), together with every universally valid
entropy inequality and any finite sequence of standard copy-lemma
extensions, have a feasible entropic point for which

```text
B1 = B2 = c+r = 2h2(1/4)-5/4.                           (8)
```

In particular, maximizing `min(B1,B2)` over any such relaxation gives a value
at least (8), so these ingredients cannot prove a strictly smaller sum-rate
bound.

## Explicit finite entropic witness

Besides `c` and `r`, put

```text
t = 2r,             s = 1/2-c = 1-h.
```

Take mutually independent binary components with the following entropies:

| component | `C` | `A` | `B1c` | `B2c` | `Eu` | `Ev` | `Ny` | `Nz` |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| entropy | `t` | `s` | `r` | `s-r` | `1/2-r` | `r` | `1/2` | `1/2` |

The component names `B1c,B2c` are unrelated to the branch names in (7).
All listed numbers lie strictly between zero and one.  One exact check is

```text
h = 2-(3/4)log2(3),       3/4 < h < 7/8,
```

where the two strict inequalities are respectively equivalent to `27<32`
and `9>8`.  They imply positivity of `r`, `s`, and
`s-r=7/4-2h`; the remaining cases are immediate.  A binary random variable
of any prescribed entropy in `[0,1]` exists by continuity of `h2` on
`[0,1/2]`, so this specifies an actual finite probability distribution, not
just a polymatroid.

Set `W` and `T` constant and define tuple variables

```text
U = (C,A,B2c,Eu),             V = (B1c,Ev),
X = (C,A,B1c,B2c,Eu,Ev),
Y = (C,A,Ny),                 Z = (C,B1c,B2c,Nz).        (9)
```

Because the components are independent, the entropy of a tuple is simply the
sum of the weights of the distinct components it contains.  This makes every
check below finite arithmetic in `h`.

### Base-vector audit

The identities `r+s=1/4` and `t=2r` give

```text
H(X)       = t+s+r+(s-r)+(1/2-r)+r = 1,
H(Y)       = t+s+1/2                 = h,
H(Z)       = t+r+(s-r)+1/2           = h.
```

The non-noise part of `Y` and of `Z` is already contained in `X`, so

```text
H(X,Y)=H(X)+H(Ny)=3/2,
H(X,Z)=H(X)+H(Nz)=3/2,
H(X,Y,Z)=H(X)+H(Ny)+H(Nz)=2.
```

Finally, the union in `(Y,Z)` is `(C,A,B1c,B2c,Ny,Nz)`, and hence

```text
H(Y,Z)=t+s+r+(s-r)+1=3/2.
```

This proves all seven equalities in (2).

### Structural and BEC-identity audit

The variables `U` and `V` use disjoint independent components, and their
union is exactly `X`.  Thus `I(U;V)=0`, `H(X|U,V,T)=0`, and the remaining
time/encoder equalities in (3) hold because `W,T` are constant.  Conditional
on `X`, the only output randomness is the independent pair `(Ny,Nz)`, proving
the Markov equality.

The joint output reveals from `X` precisely `(C,A,B1c,B2c)`.  Within `U`, its
revealed part `(C,A,B2c)` has entropy

```text
t+s+(s-r)=r+2s=(1/2)H(U),
```

while within `V` the revealed component `B1c` has entropy
`r=(1/2)H(V)`.  Since `U,V` are independent and `W,T` are constant, the same
half-entropy statement holds after conditioning on any disjoint subtuple and
after taking either or both of `U,V` on the left.  This proves every identity
in (5), not merely its unconditional instances.

Conditioning on `Y` reveals only components of `U`; conditioning on `Z`
reveals separate components of `U` and `V`.  In neither case is dependence
created between their still-independent components.  Therefore

```text
I(U;V|W,T,Y)=I(U;V|W,T,Z)=0,
```

which proves (4).

### Support rows and objective audit

Component intersection in (9) gives

```text
I(U;Y)=H(C,A)=t+s=c,
I(V;Z)=H(B1c)=r,

I(X;Y|U)=0,                     I(X;Z|U)=r,
I(X;Y|V)=c,                     I(X;Z|V)=H(C,B2c)=1/4.
```

Both differences in (6) are consequently exactly `r`.  Substitution in (7)
then gives

```text
B1=c+r,                 B2=r+c=c+r,
```

establishing (8).

### Why universal inequalities and copy variables cannot help

The preceding construction is a joint distribution of finitely many random
variables, so its entropy vector satisfies *every* information inequality
valid for all finite distributions, including undiscovered non-Shannon
inequalities.  A standard copy-lemma step is also realizable on any finite
distribution: conditionally resample the copied tuple from its conditional
law over the designated base tuple, independently of the variables from
which it is required to be a copy.  Repeating this operation realizes every
finite sequential copy construction.  Universal inequalities on the enlarged
variable list therefore remain true.  Since the original marginal and (8)
are unchanged, no finite entropy/copy certificate can exclude this witness or
derive a smaller objective from (2)--(6).

This argument is stronger and cleaner than checking a catalog of named
inequalities.  No floating-point LP optimum or numerical scan is part of the
theorem.

## The missing binary-channel premise

The witness has `H(X)=1`, but `X` is a tuple of six nondegenerate binary
components and is not binary.  Thus neither `H(X)=1` nor even the complete
base entropy vector (2) encodes `|X|=2` or the BSSC transition table.

There is a particularly direct exact way to see how the true channel excludes
the witness.  For an actual Markov chain `A-X-Y`,

```text
I(X;Y)=I(A;Y)+I(X;Y|A).
```

For the witness, `I(U;Y)=I(X;Y)=c`, so `I(X;Y|U)=0`, yet
`I(X;Z|U)=r>0`.  For the genuine binary BSSC, however,
`IY(q)>0` at every posterior `0<q<1`.  Therefore
`I(X;Y|A)=E IY(q_A)=0` forces every posterior to be `0` or `1`: `A`
determines `X`, and then necessarily `I(X;Z|A)=0`.  The witness violates this
binary-posterior face implication.

More generally, the exact channel-specific region for every auxiliary `A` is

```text
(H(X|A), I(X;Y|A), I(X;Z|A))
  = E_A (h2(q_A), IY(q_A), IZ(q_A)),       E_A q_A=q.    (10)
```

Equivalently, every linear direction is bounded by the upper concave envelope
of the corresponding scalar function.  Constraints such as (10), and the
joint consistency of the posterior refinements associated with several
auxiliaries, are not universal entropy inequalities.  They use binary
cardinality and the exact transition probabilities.  They can exclude the
counterfeit and may still yield stronger converses.  This theorem does not
show that finitely many separate support rows suffice, nor does it preclude a
new channel-specific or direct code inequality.

## Validation, novelty, and limitations

The proof is an explicit component-entropy audit.  Its only analytic input is
the one-dimensional support calculation leading to (1), for which the second
derivative, tangent, and equality-achieving posterior mixture are displayed.
Every other equality follows by taking unions of independent component sets.

Relative to the current challenge knowledge, this is a new route-closing
result.  Existing entries reduce and certify particular Gohari--Liu--Nair
outer bounds, solve the all-block Sato coupling value, and evaluate the
simplified equation-(16) functional.  None records why universal
non-Shannon/copy refinements of this dependence-balance entropy formulation
cannot even pass the older UV value.

The limitations are deliberate:

- no new BSSC capacity upper bound or achievability result is claimed;
- no sampled posterior hull, floating LP value, or finite catalog of named
  inequalities is promoted to a certificate;
- the obstruction applies to the stated relaxation (2)--(6), not to an
  entropy formulation augmented by the full binary posterior law; and
- the theorem does not settle whether exact jointly consistent posterior
  constraints, a different single-letterization, or a direct multiletter code
  inequality can improve the best certified BSSC bound.

The concrete open problem left by the theorem is to find an exact inequality
for jointly consistent binary BSSC posterior refinements that supplies a
strict penalty absent from universal entropy geometry.

</artifact>
<artifact path="problems/bssc-sum-capacity/contributions/code-induced-dependence-balance-and-entropy-no-go/verify_exact_witness.py">
#!/usr/bin/env python3
"""Exact symbolic audit of the accepted entropy-counterfeit witness.

Every entropy is represented as ``a + b*h``, with rational ``a,b`` and
``h = h_2(1/4)``.  Tuple variables are projections of mutually independent
components, so entropy and conditional mutual information reduce to weighted
set union and intersection.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from itertools import product


@dataclass(frozen=True)
class AffineH:
    constant: Fraction = Fraction(0)
    h_coefficient: Fraction = Fraction(0)

    def __add__(self, other: "AffineH") -> "AffineH":
        return AffineH(
            self.constant + other.constant,
            self.h_coefficient + other.h_coefficient,
        )

    def __sub__(self, other: "AffineH") -> "AffineH":
        return AffineH(
            self.constant - other.constant,
            self.h_coefficient - other.h_coefficient,
        )

    def __mul__(self, scalar: int | Fraction) -> "AffineH":
        scalar = Fraction(scalar)
        return AffineH(self.constant * scalar, self.h_coefficient * scalar)

    __rmul__ = __mul__


ZERO = AffineH()
ONE = AffineH(Fraction(1))
HALF = AffineH(Fraction(1, 2))
H = AffineH(h_coefficient=Fraction(1))

C_VALUE = 2 * H - 3 * HALF
A_VALUE = ONE - H
R = H - AffineH(Fraction(3, 4))
B1C_VALUE = R
B2C_VALUE = AffineH(Fraction(7, 4)) - 2 * H
EU_VALUE = AffineH(Fraction(5, 4)) - H
EV_VALUE = R

COMPONENT_WEIGHTS = {
    "C": C_VALUE,
    "A": A_VALUE,
    "B1c": B1C_VALUE,
    "B2c": B2C_VALUE,
    "Eu": EU_VALUE,
    "Ev": EV_VALUE,
    "Ny": HALF,
    "Nz": HALF,
}

VARIABLES = {
    "U": frozenset({"C", "A", "B2c", "Eu"}),
    "V": frozenset({"B1c", "Ev"}),
    "W": frozenset(),
    "T": frozenset(),
    "X": frozenset({"C", "A", "B1c", "B2c", "Eu", "Ev"}),
    "Y": frozenset({"C", "A", "Ny"}),
    "Z": frozenset({"C", "B1c", "B2c", "Nz"}),
}


def total_weight(components: frozenset[str] | set[str]) -> AffineH:
    value = ZERO
    for component in components:
        value += COMPONENT_WEIGHTS[component]
    return value


def union_of(names: tuple[str, ...] | list[str]) -> frozenset[str]:
    result: set[str] = set()
    for name in names:
        result.update(VARIABLES[name])
    return frozenset(result)


def entropy(*names: str) -> AffineH:
    return total_weight(union_of(list(names)))


def conditional_mi(
    left: frozenset[str], right: frozenset[str], conditioned: frozenset[str]
) -> AffineH:
    return total_weight((left & right) - conditioned)


def cmi(left: tuple[str, ...], right: tuple[str, ...], given: tuple[str, ...]) -> AffineH:
    return conditional_mi(union_of(left), union_of(right), union_of(given))


def require_equal(label: str, actual: AffineH, expected: AffineH) -> None:
    if actual != expected:
        raise AssertionError(f"{label}: {actual!r} != {expected!r}")


def require_strictly_positive_on_h_bracket(label: str, value: AffineH) -> None:
    # The accepted exact bounds are 3/4 < h_2(1/4) < 7/8.
    endpoint = Fraction(3, 4) if value.h_coefficient >= 0 else Fraction(7, 8)
    lower_limit = value.constant + value.h_coefficient * endpoint
    if lower_limit < 0:
        raise AssertionError(f"{label}: negative on the certified h bracket")
    if lower_limit == 0 and value.h_coefficient == 0:
        raise AssertionError(f"{label}: identically zero")


def main() -> None:
    for name, value in COMPONENT_WEIGHTS.items():
        require_strictly_positive_on_h_bracket(name, value)

    # Structural equalities: U and V are independent component projections,
    # their union is exactly X, and W,T are constants.
    if VARIABLES["U"] & VARIABLES["V"]:
        raise AssertionError("U and V share an independent component")
    if VARIABLES["U"] | VARIABLES["V"] != VARIABLES["X"]:
        raise AssertionError("U and V do not determine exactly X")
    require_equal("I(U;V)", cmi(("U",), ("V",), ()), ZERO)
    require_equal("H(X|U,V,T)", total_weight(VARIABLES["X"] - union_of(["U", "V", "T"])), ZERO)
    require_equal("I(X;W|U,V,T)", cmi(("X",), ("W",), ("U", "V", "T")), ZERO)
    require_equal(
        "I(U,V,W,T;Y,Z|X)",
        cmi(("U", "V", "W", "T"), ("Y", "Z"), ("X",)),
        ZERO,
    )

    # Complete seven-coordinate base entropy vector.
    require_equal("H(X)", entropy("X"), ONE)
    require_equal("H(Y)", entropy("Y"), H)
    require_equal("H(Z)", entropy("Z"), H)
    require_equal("H(X,Y)", entropy("X", "Y"), AffineH(Fraction(3, 2)))
    require_equal("H(X,Z)", entropy("X", "Z"), AffineH(Fraction(3, 2)))
    require_equal("H(Y,Z)", entropy("Y", "Z"), AffineH(Fraction(3, 2)))
    require_equal("H(X,Y,Z)", entropy("X", "Y", "Z"), AffineH(Fraction(2)))

    # Exact dependence balance at the witness.
    require_equal("I(U;V|W,T,Y)", cmi(("U",), ("V",), ("W", "T", "Y")), ZERO)
    require_equal("I(U;V|W,T,Z)", cmi(("U",), ("V",), ("W", "T", "Z")), ZERO)

    # Audit all disjoint L,K subtuples of {U,V,W,T}, L nonempty.
    labels = ("U", "V", "W", "T")
    bec_identity_count = 0
    for assignment in product(range(3), repeat=len(labels)):
        left_names = tuple(label for label, slot in zip(labels, assignment) if slot == 1)
        given_names = tuple(label for label, slot in zip(labels, assignment) if slot == 2)
        if not left_names:
            continue
        lhs = cmi(left_names, ("Y", "Z"), given_names)
        rhs = cmi(left_names, ("X",), given_names)
        require_equal(f"BEC identity L={left_names}, K={given_names}", 2 * lhs, rhs)
        bec_identity_count += 1
    if bec_identity_count != 65:
        raise AssertionError(f"unexpected BEC identity count: {bec_identity_count}")

    # Sharp support rows and both objective branches.
    first_support = cmi(("X",), ("Z",), ("U", "W", "T")) - cmi(
        ("X",), ("Y",), ("U", "W", "T")
    )
    second_support = cmi(("X",), ("Y",), ("V", "W", "T")) - cmi(
        ("X",), ("Z",), ("V", "W", "T")
    )
    require_equal("first support row", first_support, R)
    require_equal("second support row", second_support, R)

    c_value = H - HALF
    branch_1 = cmi(("U", "W"), ("Y",), ("T",)) + cmi(
        ("X",), ("Z",), ("U", "W", "T")
    )
    branch_2 = cmi(("V", "W"), ("Z",), ("T",)) + cmi(
        ("X",), ("Y",), ("V", "W", "T")
    )
    expected_branch = 2 * H - AffineH(Fraction(5, 4))
    require_equal("B1", branch_1, c_value + R)
    require_equal("B2", branch_2, c_value + R)
    require_equal("exact UV value", branch_1, expected_branch)

    print("PASS: exact affine-in-h component audit")
    print(f"PASS: {bec_identity_count} disjoint-subtuple BEC identities")
    print("PASS: dependence balance, support rows, and both objective branches")


if __name__ == "__main__":
    main()

</artifact>
</contribution>
<contribution>
ordinal: 5
transaction_id: 14889884ae6ac1f80cc56485e7acf1b0b2cb6ae9
contribution_id: uv-relaxed-converse-tensorization
author: Robert Raynor
<artifact path="problems/bssc-sum-capacity/contributions/uv-relaxed-converse-tensorization/README.md">
# Tensorization of two separately relaxed UV scalar functionals

## Claim and exact scope

Let \(W:x\mapsto (Y,Z)\) be a finite-alphabet discrete memoryless
broadcast channel.  For an input law \(p\), define

\[
t_W(p)=I_p(X;Y)-I_p(X;Z).
\]

For a real function \(f\) on the input simplex, write

\[
\mathfrak C[f](p)
=\sup\left\{\sum_a \lambda_a f(p_a):
  \lambda_a\ge0,\ \sum_a\lambda_a=1,\
  \sum_a\lambda_a p_a=p\right\}
\]

for its upper concave envelope.  Put

\[
 A_W(p)=I_p(X;Y)+\mathfrak C[-t_W](p),\qquad
 D_W(p)=I_p(X;Z)+\mathfrak C[t_W](p),
\]

and define the two scalar functionals

\[
 B_{\rm avg}(W)=\sup_p\frac{A_W(p)+D_W(p)}2,
 \qquad
 B_{\rm br}(W)=\sup_p\min\{A_W(p),D_W(p)\}.
\]

The claim is the following single theorem and its BSSC specialization.

1. For arbitrary finite-alphabet DMBCs \(W_1,W_2\),
   \[
   B_{\rm avg}(W_1\times W_2)
   =B_{\rm avg}(W_1)+B_{\rm avg}(W_2).
   \]
   This includes correlated product-channel input laws and envelope
   auxiliaries that are joint across the factors.
2. If an involutive input relabeling exchanges the two receiver marginals,
   up to output relabeling, then
   \(B_{\rm br}(W)=B_{\rm avg}(W)\), and either supremum may be restricted
   to input laws invariant under that involution.  Finite products preserve
   this symmetry, so both scalar functionals are additive on finite products
   of receiver-skew channels.
3. For the half-skew BSSC \(P\) in the governed problem and every integer
   \(n\ge1\),
   \[
   B_{\rm br}(P^{\times n})=B_{\rm avg}(P^{\times n})
   =n\left(2h_2(1/4)-\frac54\right).
   \]
   The normalized value is
   \(0.37255624891826566\ldots\) bits per channel use.

This contribution depends on canonical transaction
`c70e1829a7c6a2a8cb8cfc2383f8abf825ac5ea6` only for the sharp scalar
BSSC posterior-support inequality used in the last specialization.  The
general product and symmetry theorem below is independent of that result.

The theorem concerns two *separately relaxed scalar* UV rows.  It does not
tensorize the complete UV rate region or a common joint-\((U,V)\)
optimization.  It says nothing about tensorization of the simplified GK
functional or the full Gohari--Liu--Nair Theorem-9 system, and it does not
identify the BSSC capacity.  Its normalized BSSC value is larger than the
governed upper endpoint \(0.369316568803963\), so it does not change the
problem's capacity interval.

## Product theorem

Write \(X_{12}=(X_1,X_2)\), and similarly for the outputs of the product
channel.  Let \(A-X_{12}-(Y_1,Z_1,Y_2,Z_2)\) be any finite auxiliary.  The
Csiszar sum identity, together with the product-channel Markov relations,
gives

\[
\begin{aligned}
 &I(X_{12};Y_1Y_2\mid A)-I(X_{12};Z_1Z_2\mid A)\\
 &=I(X_1;Y_1\mid A,Z_2)-I(X_1;Z_1\mid A,Z_2)\\
 &\quad+I(X_2;Y_2\mid A,Y_1)-I(X_2;Z_2\mid A,Y_1).
\end{aligned}
\tag{1}
\]

For completeness, expand the two left-hand mutual informations in opposite
orders.  The uncancelled cross terms are both \(I(Y_1;Z_2\mid A)\):

\[
\begin{aligned}
I(X_{12};Y_1Y_2\mid A)
 &=I(X_1;Y_1\mid A,Z_2)+I(X_2;Y_2\mid A,Y_1)
   +I(Y_1;Z_2\mid A),\\
I(X_{12};Z_1Z_2\mid A)
 &=I(X_1;Z_1\mid A,Z_2)+I(X_2;Z_2\mid A,Y_1)
   +I(Y_1;Z_2\mid A).
\end{aligned}
\]

Conditioning on \((A,Z_2)\) leaves the first factor governed by \(W_1\),
and conditioning on \((A,Y_1)\) leaves the second governed by \(W_2\).
The corresponding conditional input laws form posterior ensembles with
barycenters \(p_1\) and \(p_2\).  Thus (1), first for every posterior
ensemble of \(p_{12}\) and then after taking its supremum, proves

\[
\mathfrak C[t_{12}](p_{12})
\le \mathfrak C[t_1](p_1)+\mathfrak C[t_2](p_2).
\tag{2}
\]

Exchanging \(Y\) and \(Z\) in the same calculation gives

\[
\mathfrak C[-t_{12}](p_{12})
\le \mathfrak C[-t_1](p_1)+\mathfrak C[-t_2](p_2).
\tag{3}
\]

Output independence conditional on \(X_{12}\), followed by entropy
subadditivity, gives

\[
I(X_{12};Y_1Y_2)\le I(X_1;Y_1)+I(X_2;Y_2),
\]

and the analogous inequality for \(Z_1Z_2\).  Combining these inequalities
with (2)--(3) yields, for every possibly correlated \(p_{12}\),

\[
A_{12}(p_{12})\le A_1(p_1)+A_2(p_2),\qquad
D_{12}(p_{12})\le D_1(p_1)+D_2(p_2).
\tag{4}
\]

Taking the averaged row and its supremum proves the `<=` product inequality.

For the reverse inequality, take product input laws \(p_1p_2\).  Given
posterior ensembles for \(p_1\) and \(p_2\), their independent product
ensemble has barycenter \(p_1p_2\), while

\[
t_{12}(q_1q_2)=t_1(q_1)+t_2(q_2).
\]

Consequently both envelope inequalities (2)--(3) reverse at product input
laws.  The ordinary mutual informations are also additive there, so

\[
A_{12}(p_1p_2)=A_1(p_1)+A_2(p_2),\qquad
D_{12}(p_1p_2)=D_1(p_1)+D_2(p_2).
\]

Choosing factor laws arbitrarily close to their suprema proves the `>=`
inequality and hence exact additivity.  No attainment assumption is needed.

## Receiver-skew reduction

Suppose an involution \(S\) of the input alphabet exchanges the receiver
marginals up to bijective output relabelings.  Mutual information is invariant
under relabeling, so

\[
I_Y(Sp)=I_Z(p),\qquad t(Sp)=-t(p).
\]

Applying \(S\) to every member of a posterior ensemble is a barycenter-
preserving bijection.  Therefore

\[
A(Sp)=D(p),\qquad D(Sp)=A(p).
\tag{5}
\]

Both \(A\) and \(D\) are concave.  For
\(\bar p=(p+Sp)/2\), equations (5) and concavity give

\[
A(\bar p),D(\bar p)\ge \frac{A(p)+D(p)}2.
\]

Thus an invariant law attains at least the averaged value of every law, and

\[
B_{\rm br}(W)\ge B_{\rm avg}(W).
\]

The reverse inequality follows pointwise from
\(\min\{a,d\}\le(a+d)/2\).  This proves equality and the invariant-law
restriction.  The componentwise product of the involutions exchanges the
receivers of a product channel.  Combining this observation with the product
theorem proves the finite-product statement.

## Exact half-skew BSSC specialization

Let \(q=\Pr[X=1]\), \(h=h_2(1/4)\), and \(r=h-3/4\).  Directly from the two
channel matrices,

\[
I_Y(q)=h_2((1-q)/2)-(1-q),\qquad
I_Z(q)=h_2(q/2)-q.
\tag{6}
\]

The BSSC is receiver-skew under input and output bit flips, and its only
invariant binary input law is \(q=1/2\).  At that law,

\[
I_Y(1/2)=I_Z(1/2)=h-\frac12.
\tag{7}
\]

The sharp posterior support established by canonical transaction
`c70e1829a7c6a2a8cb8cfc2383f8abf825ac5ea6`, after reflection, is

\[
t(q)\le 2rq\qquad(0\le q\le1).
\tag{8}
\]

Every posterior ensemble with barycenter \(1/2\) therefore has average
\(t\) at most \(r\).  Equality is attained by putting mass \(5/8\) at
\(q=4/5\) and mass \(3/8\) at \(q=0\): its barycenter is \(1/2\), and (6)
gives \(t(4/5)=8r/5\) and \(t(0)=0\).  Hence

\[
\mathfrak C[t](1/2)=r.
\]

Receiver skew gives the same value for \(\mathfrak C[-t](1/2)\).  Combining
this with (7), the invariant-law reduction, and finite-product additivity
proves

\[
B_{\rm br}(P^{\times n})=B_{\rm avg}(P^{\times n})
=n\left(h-\frac12+r\right)
=n\left(2h_2(1/4)-\frac54\right).
\]

## Reproduction

From the repository root, run

```text
PYTHONDONTWRITEBYTECODE=1 python3 problems/bssc-sum-capacity/contributions/uv-relaxed-converse-tensorization/verify_specialization.py
```

The standard-library script evaluates (6)--(8) at 90-decimal precision,
checks the attaining posterior mixture and the receiver-skew channel
relations, and prints the normalized value.  It corroborates the exact
specialization; the universal theorem rests on the analytic proof above.

</artifact>
<artifact path="problems/bssc-sum-capacity/contributions/uv-relaxed-converse-tensorization/claims.json">
{
  "schemaVersion": 1,
  "claims": [
    {
      "claimKey": "bssc-sum-capacity/uv-relaxed-converse-tensorization",
      "statement": "For finite-alphabet discrete memoryless broadcast channels, the averaged separately-relaxed UV sum-rate functional defined in this contribution is exactly additive under products. On a receiver-skew channel the branchwise functional equals the averaged functional, and the same equality and additivity hold for every finite product of receiver-skew channels. Consequently, for the half-skew BSSC P and every integer n >= 1, both functionals on P^{times n} equal n(2 h_2(1/4) - 5/4) bits. This is a theorem only about the two separately-relaxed scalar UV functionals, not about tensorization of the full UV region, a common joint-(U,V) optimization, the GK functional, or the capacity itself.",
      "dependencyTransactionIds": [
        "c70e1829a7c6a2a8cb8cfc2383f8abf825ac5ea6"
      ]
    }
  ]
}

</artifact>
<artifact path="problems/bssc-sum-capacity/contributions/uv-relaxed-converse-tensorization/verification.json">
{
  "schemaVersion": 1,
  "verifier": {
    "id": "python-stdlib-3-13-v1",
    "specDigest": "sha256:fc7ed06b77396fabc1da84694b4d8a08800843f41ad8ca4b9cd666b67ba60884"
  },
  "entrypoint": "verify_specialization.py",
  "arguments": []
}

</artifact>
<artifact path="problems/bssc-sum-capacity/contributions/uv-relaxed-converse-tensorization/verify_specialization.py">
#!/usr/bin/env python3
"""High-precision audit of the exact half-skew BSSC specialization."""

from decimal import Decimal, getcontext
from fractions import Fraction


getcontext().prec = 90
ONE = Decimal(1)


def h2(q: Decimal) -> Decimal:
    if q == 0 or q == 1:
        return Decimal(0)
    return -(q * q.ln() + (ONE - q) * (ONE - q).ln()) / Decimal(2).ln()


def t(q: Decimal) -> Decimal:
    i_y = h2((ONE - q) / 2) - (ONE - q)
    i_z = h2(q / 2) - q
    return i_y - i_z


def main() -> None:
    h = h2(ONE / 4)
    r = h - Decimal(3) / 4
    contact = Decimal(4) / 5

    assert abs(t(contact) - Decimal(8) * r / 5) < Decimal("1e-80")
    assert t(Decimal(0)) == 0
    assert Decimal(5) / 8 * contact == ONE / 2
    assert abs(Decimal(5) / 8 * t(contact) - r) < Decimal("1e-80")

    y = (
        (Fraction(1, 2), Fraction(1, 2)),
        (Fraction(0), Fraction(1)),
    )
    z = (
        (Fraction(1), Fraction(0)),
        (Fraction(1, 2), Fraction(1, 2)),
    )
    for x in range(2):
        for output in range(2):
            assert y[1 - x][output] == z[x][1 - output]
            assert z[1 - x][output] == y[x][1 - output]

    value = 2 * h - Decimal(5) / 4
    governed_upper = Decimal("0.369316568803963")
    assert value > governed_upper
    print("PASS: BSSC support contact and receiver-skew identities")
    print(f"normalized relaxed-UV value: {value}")


if __name__ == "__main__":
    main()

</artifact>
</contribution>
<contribution>
ordinal: 9
transaction_id: e3c1036ca607539a5ebcddf3058e6014ac5c1cd9
contribution_id: theorem9-cited-premise-foundations
author: Robert Raynor
<artifact path="problems/bssc-sum-capacity/contributions/theorem9-cited-premise-foundations/README.md">
# Theorem 9 cited-premise private-message foundations

## Premise and exact claim boundary

This contribution takes the following statement as an explicit premise.  For
the fixed physical BSSC $T_{Y,Z|X}$ and every finite auxiliary-receiver law
$T_{G,K|X,Y,Z}$, Gohari--Liu--Nair Theorem 9 is the outer-bound assertion with
the factorization, equations (19a)--(19p), and both side conditions encoded
term by term in the authoritative premise file `theorem9_spec.json` and
displayed for human review in `SOURCE_TRANSCRIPTION.md`.  Precisely, for every
achievable rate triple there is one input law $p_X$ such that, for each chosen
finite auxiliary-receiver law, some finite auxiliary variables admitted by the
factorization satisfy the stated system.

The claimed and governed result begins from that premise.  After setting
$R_0=0$, expanding every displayed minimum produces 26 scalar rows and
splitting the two interval side conditions produces four more.  These are
exactly, term for term, the local 30-row system independently generated by the
generic $L=3$ path formulas in `verify_specialization.py`.  An exhaustive term
audit then proves that replacing arbitrary $G,K$ by their input-only product
marginals preserves the entire system.  Therefore, with the optimization
order and domains defined below,

\[
C_{\rm sum}\le
\inf_{\substack{T_{G|X},T_{K|X}\\
                 \text{finite-output, binary-input}}} B(G,K),
\qquad
V_Q(G,K)\le V(1/2;G,K)\le B(G,K).
\]

On $Q_0=\{0,1/2,1\}$ every row depends on the four receiver channels only
through $(c,g,k,c)$, so the finite quantity $V_0(g,k)$ is well defined on its
realizable $(g,k)$-domain.  These
specialization, marginalization, capacity-bound, and local-value consequences
form one all-or-nothing foundation claim.

This contribution does **not** prove or authenticate the cited Theorem 9
premise.  It also does not claim a numerical bound, the optimum of the $Q_0$
problem, a coercive inequality, a receiver-cardinality theorem, or a continuum
limit.

## Citation and non-claiming review aids

The premise is attributed to:

> Amin Gohari, Yi Liu, and Chandra Nair, *A Two Auxiliary Receiver Outer Bound
> to the Capacity Region of a Two-Receiver Discrete Memoryless Broadcast
> Channel*, Appendix B, Theorem 9, equations (19a)--(19p).

Citation URL:
<https://chandra.ie.cuhk.edu.hk/pub/papers/BC/GK-outer.pdf>

For provenance, the consulted version was a 255268-byte sequence with SHA-256
`24c4153530008f7ae339ac19ca8cb90fb8ea574ea8fbcd6a36c2221722d651fa`.
The PDF, its URL, its bibliographic origin, and any claim of visual/source
fidelity are **outside the claimed result**.  No PDF or parser is included in
this contribution.  The governed no-argument verifier treats
`theorem9_spec.json` as the exact cited mathematical premise;
`SOURCE_TRANSCRIPTION.md` is review exposition.  It checks only the
downstream consequences above.

The earlier transactions
`d638c346212db3e75f6a53dcebcfd09f55125852`,
`f093396fe03f8920f9905c385ef34b1335792d5e`,
`dcdd3ab29be1a45b42a75767dbee30d8381544eb`, and
`54ace2045150d21f8ac4c06b3dde8d109fc82e0f` motivated this premise-bound
replacement, but none is a mathematical premise.  They are provenance only,
not declared claim dependencies.

## Definitions and optimization order

Fix the physical BSSC $T_{Y,Z|X}$.  After the marginalization proved below,
fix finite-output binary-input channels $T_{G|X}$ and $T_{K|X}$.  For
$q\in[0,1]$, use $P(X=1)=q$.

Let

\[
C_{\rm sum}:=\sup\{R_1+R_2:(R_0,R_1,R_2)=(0,R_1,R_2)
\text{ is achievable for the physical BSSC}\}.
\]

Define $V(q;G,K)$ to be the extended-real supremum of $R_1+R_2$ over:

1. nonnegative $R_1,R_2$;
2. finite auxiliary triples
   $(U_j,V_j,W_j)$, $j\in\{a,b,c\}$, with conditional law
   \[
   p_{U_a,V_a,W_a|X}p_{U_b,V_b,W_b|X}p_{U_c,V_c,W_c|X};
   \]
3. choices satisfying all 26 private-rate/nonnegativity rows obtained from
   (19a)--(19p) after setting $R_0=0$, and all four scalar inequalities
   obtained from the two side conditions.

Thus the supremum over rates and finite auxiliary hierarchies is taken while
$q,G,K$ are fixed.  No closure or attainment is assumed.  Throughout this
contribution, $\sup\varnothing=-\infty$; this makes every restricted value
defined even when a support restriction admits no feasible hierarchy.

Define the fixed-receiver full-prior value by

\[
B(G,K):=\sup_{q\in[0,1]}V(q;G,K).
\]

This order is important: first optimize the Theorem 9 auxiliary hierarchy at
fixed $q,G,K$, then take the supremum over $q$.  The resulting receiver
outer bound is subsequently minimized over finite $G,K$:

\[
C_{\rm sum}\le \inf_{G,K}B(G,K).
\]

No equality or interchange with
$\sup_q\inf_{G,K}V(q;G,K)$ is asserted.

For a fixed receiver $A\in\{Y,G,K,Z\}$, let

\[
J_A(t):=I(X;A)\quad\text{when }P(X=1)=t
\]

with $T_{A|X}$ held fixed.  Let $Q\subset[0,1]$ be finite and contain
$1/2$.  A fair-prior auxiliary hierarchy is **$Q$-supported** when every
positive-probability posterior

\[
P(X=1|W_j),\qquad P(X=1|U_j,W_j),\qquad
P(X=1|V_j,W_j)
\]

belongs to $Q$, for all three groups.  Define

\[
V_Q(G,K):=\sup\{R_1+R_2:\text{the defining optimization for }
V(1/2;G,K)\text{ uses a }Q\text{-supported hierarchy}\}.
\]

This is a restriction inside the auxiliary-hierarchy supremum, hence

\[
V_Q(G,K)\le V(1/2;G,K)\le \sup_qV(q;G,K)=B(G,K).
\]

Finally let

\[
Q_0=\{0,1/2,1\},\qquad
c=J_Y(1/2)=J_Z(1/2)=h_2(1/4)-1/2.
\]

For any $G,K$, put $g=J_G(1/2)$, $k=J_K(1/2)$, and define

\[
V_0(g,k):=V_{Q_0}(G,K).
\]

The proof below shows that the right-hand side depends only on $g,k$, not on
which channels realize those two midpoint values, so this definition is
unambiguous.  It is also a finite real value: the $Q_0$-supported choice
$W_a=W_b=W_c=X$ with all $U_j,V_j$ constant makes both side conditions zero
and admits $R_1=R_2=0$, while the branch-zero individual-rate rows give
$R_1\le I(U_a,W_a;Y)\le1$ and
$R_2\le I(V_c,W_c;Z)\le1$.

## Exact expansion to 30 rows

In the source, (19c)--(19d), (19e)--(19f), (19g)--(19h), and
(19i)--(19j) are four inequalities whose continuations carry separate equation
labels.  Expanding a condition $L\le A+\min\{b_1,\ldots,b_m\}$ means imposing
the $m$ scalar rows $L\le A+b_i$.  The complete mapping is:

| source line(s) | branches | generated local rows |
|---|---:|---|
| (19a) | 3 | `N_Y(0)`, `N_Y(1)`, `N_Y(2)` |
| (19b) | 3 | `N_Z(0)`, `N_Z(1)`, `N_Z(2)` |
| (19c)--(19d) | 3 | `R1T(0)`, `R1T(1)`, `R1T(2)` |
| (19e)--(19f) | 3 | `R1A(0)`, `R1A(1)`, `R1A(2)` |
| (19g)--(19h) | 3 | `R2A(0)`, `R2A(1)`, `R2A(2)` |
| (19i)--(19j) | 3 | `R2T(0)`, `R2T(1)`, `R2T(2)` |
| (19k) | 2 | `SL(3,U)`, `SL(3,C)` |
| (19l) | 2 | `SR(1,C)`, `SR(1,U)` |
| (19m) | 1 | `SL(2,U)` |
| (19n) | 1 | `SL(1,U)` |
| (19o) | 1 | `SR(2,U)` |
| (19p) | 1 | `SR(3,U)` |

These are 26 rows.  Each side condition $0\le L\le R$ is exactly the pair
$L\ge0$, $R-L\ge0$.  The $Z,K$ condition gives `F_Z_left` and
`F_Z_right_minus_left`; the $Y,G$ condition gives `F_Y_left` and
`F_Y_right_minus_left`.  The total is therefore 30.

The verifier first requires that the structured premise contain exactly all 16
equation labels, the stated factorization, and two side conditions.  It then
constructs rows in two independent ways.  First, it reads
`theorem9_spec.json`, expands every minimum, and splits the side conditions.
Second, `make_path_rows` builds an $L=3$ chain
$Y\to G\to K\to Z$ from generic left- and right-walk formulas.
It normalizes the results only with

\[
I(U,W;A)=I(W;A)+I(U;A|W),\qquad
I(V,W;A)=I(W;A)+I(V;A|W),
\]

and compares the rate coefficients and every signed information term exactly.

## Exhaustive output-term audit and marginalization

The complete distinct output-bearing term set from the source transcription is:

| output | terms |
|---|---|
| $Y$ | $I(W_a;Y)$, $I(U_a;Y|W_a)$, $I(X;Y|V_a,W_a)$ |
| $Z$ | $I(W_c;Z)$, $I(V_c;Z|W_c)$, $I(X;Z|U_c,W_c)$ |
| $G$ | $I(W_a;G)$, $I(W_b;G)$, $I(U_a,W_a;G)$, $I(U_b,W_b;G)$, $I(V_a,W_a;G)$, $I(V_b,W_b;G)$, $I(U_a;G|W_a)$, $I(U_b;G|W_b)$, $I(V_b;G|W_b)$, $I(X;G|U_a,W_a)$, $I(X;G|V_a,W_a)$, $I(X;G|V_b,W_b)$ |
| $K$ | $I(W_b;K)$, $I(W_c;K)$, $I(U_b,W_b;K)$, $I(U_c,W_c;K)$, $I(V_b,W_b;K)$, $I(V_c,W_c;K)$, $I(U_b;K|W_b)$, $I(V_b;K|W_b)$, $I(V_c;K|W_c)$, $I(X;K|U_b,W_b)$, $I(X;K|U_c,W_c)$, $I(X;K|V_c,W_c)$ |

The verifier compares this 3/12/12/3 audit against a second, independently
encoded whitelist.  In particular, there is no joint $(G,K)$ output term and
no term that conditions one output on another.

For an arbitrary admitted $T_{G,K|X,Y,Z}$, define

\[
\bar T_{G|X}(g|x)=\sum_{y,z,k}T_{Y,Z|X}(y,z|x)
T_{G,K|X,Y,Z}(g,k|x,y,z),
\]

\[
\bar T_{K|X}(k|x)=\sum_{y,z,g}T_{Y,Z|X}(y,z|x)
T_{G,K|X,Y,Z}(g,k|x,y,z),
\]

and replace it by

\[
T'_{G,K|X,Y,Z}(g,k|x,y,z)=\bar T_{G|X}(g|x)\bar T_{K|X}(k|x).
\]

If $D$ is any subtuple of one auxiliary group, then the Theorem 9
factorization gives

\[
p(d,x,g)=p_X(x)p_{D|X}(d|x)\bar T_{G|X}(g|x).
\]

This law is unchanged by $T'$, and the same calculation holds for $K$.
The $Y,Z$ laws are unchanged directly.  The exhaustive term audit therefore
shows that every row and both side conditions are preserved term by term.  The
reverse inclusion is immediate because an input-only product channel is an
allowed $T_{G,K|X,Y,Z}$.

Now fix any achievable private-message pair $(R_1,R_2)$.  The premise supplies
one input prior $q$ and, for each fixed finite input-only pair $(G,K)$, a
feasible auxiliary hierarchy for the specialized rows.  Consequently

\[
R_1+R_2\le V(q;G,K)\le B(G,K)
\]

for every such $(G,K)$.  Taking the infimum over finite-output binary-input
$(G,K)$ and then the supremum over achievable private-message pairs gives
$C_{\rm sum}\le\inf_{G,K}B(G,K)$.  This uses the displayed optimization order;
it does not interchange the supremum over $q$ with the receiver infimum.

## Why $V_0(g,k)$ is well defined

For any Markov chain $S-X-A$, posterior conditioning and the chain rule give

\[
I(S;A)=J_A(1/2)-\mathbb E[J_A(q_S)],\qquad
I(X;A|S)=\mathbb E[J_A(q_S)],
\]

where $q_S=P(X=1|S)$.  In particular,

\[
I(U;A|W)=\mathbb E[J_A(q_W)]-\mathbb E[J_A(q_{U,W})],
\]

with the analogous $V$ identity.  These identities cover every term kind in
the audited system: `W`, `U|W`, `V|W`, `UW`, `VW`, `X|UW`, and `X|VW`.

For $Q_0$-supported hierarchies, $J_A(0)=J_A(1)=0$; hence all these
expectations use only $J_A(1/2)$.  The physical BSSC values are $c,c$, and
the auxiliary-receiver values are $g,k$.  Therefore every objective row and
feasibility row is determined by the four scalar values $(c,g,k,c)$, proving
that $V_{Q_0}(G,K)$ depends on $G,K$ only through $g,k$.

## Reproduction

From this contribution directory, the repository-bounded check is:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 verify_specialization.py
```

`verification.json` requests that exact no-argument entrypoint in the governed
`python-stdlib-3-13-v1` environment, pinned at verifier-spec digest
`sha256:fc7ed06b77396fabc1da84694b4d8a08800843f41ad8ca4b9cd666b67ba60884`.
The governed runner invokes `python3 -I -B verify_specialization.py`.  The
trusted attestation covers the explicit structured premise, the independent
path-row comparison, and the exhaustive term audit.  It makes no network
request and reads no PDF.  The checker uses only the Python standard library
and exact integer linear forms.  It emits one `PASS` line for every premise
branch/side-condition row, checks the exhaustive output-term audit, and
finishes with:

```text
PASS: cited-premise R0=0 expansion and all 30 independently generated private-message rows agree exactly
```

## Limitations and authorship

- This audit uses the cited Theorem 9 manuscript statement as a premise; it does not re-prove
  the coding-theorem converse behind Theorem 9.
- The citation URL and recorded PDF digest are provenance metadata only.  No
  source-authentication, rendering, or visual-semantic result is asserted.
- No assertion is made about a $Q_0$ optimum, midpoint coercivity, receiver
  cardinality, continuum convergence, reflected optimality, or a numerical
  capacity upper bound.
- The mathematical theorem and equations are attributed to Gohari, Liu, and
  Nair.  The premise encoding, definitions, path comparison, and verifier in
  this contribution were prepared for Math Flow.

</artifact>
<artifact path="problems/bssc-sum-capacity/contributions/theorem9-cited-premise-foundations/SOURCE_TRANSCRIPTION.md">
# Bounded transcription of Gohari--Liu--Nair Theorem 9

This file is a human-readable display of the mathematical premise.  The
authoritative exact premise is encoded in `theorem9_spec.json`.  The displayed
statement is attributed to Amin Gohari, Yi Liu, and Chandra Nair, *A Two Auxiliary Receiver Outer Bound
to the Capacity Region of a Two-Receiver Discrete Memoryless Broadcast
Channel*, Appendix B, Theorem 9, PDF pages 14--15:

<https://chandra.ie.cuhk.edu.hk/pub/papers/BC/GK-outer.pdf>

For bibliographic provenance, the version consulted had 255268 bytes and
SHA-256
`24c4153530008f7ae339ac19ca8cb90fb8ea574ea8fbcd6a36c2221722d651fa`.
Neither that provenance nor fidelity to external PDF rendering is part of the
claim.  `theorem9_spec.json` is this premise in executable form, and
`verify_specialization.py` checks only its downstream mathematical
specialization and reductions.

## Factorization and quantifiers

For a broadcast channel $T_{Y,Z|X}$ and an achievable rate triple, Theorem 9
states that there is an input law $p_X$ such that, for every auxiliary channel
$T_{G,K|X,Y,Z}$, the constraints below hold for some finite auxiliary laws
with joint factorization

\[
p_X p_{U_a,V_a,W_a|X} p_{U_b,V_b,W_b|X}
p_{U_c,V_c,W_c|X} T_{Y,Z|X} T_{G,K|X,Y,Z}.
\]

## Equations (19a)--(19p)

\[
\begin{aligned}
R_0\le{}&I(W_a;Y)+\min\{0,
 I(W_b;G)-I(W_a;G),\\
&I(W_b;G)-I(W_a;G)+I(W_c;K)-I(W_b;K)\}. \tag{19a}
\end{aligned}
\]

\[
\begin{aligned}
R_0\le{}&I(W_c;Z)+\min\{0,
 I(W_b;K)-I(W_c;K),\\
&I(W_b;K)-I(W_c;K)+I(W_a;G)-I(W_b;G)\}. \tag{19b}
\end{aligned}
\]

The source places labels (19c) and (19d) on the two displayed lines of this
single inequality:

\[
\begin{aligned}
R_0+R_1\le{}&I(W_a;Y)+I(U_a;Y|W_a) \tag{19c}\\
&+\min\{0,
 I(U_b,W_b;G)-I(U_a,W_a;G),\\
&\qquad I(U_b,W_b;G)-I(U_a,W_a;G)
 +I(U_c,W_c;K)-I(U_b,W_b;K)\}. \tag{19d}
\end{aligned}
\]

Likewise, (19e) and (19f) are one inequality:

\[
\begin{aligned}
R_0+R_1\le{}&I(W_c;Z)+I(U_a;Y|W_a)
 +I(W_a;G)-I(W_b;G)+I(W_b;K)-I(W_c;K) \tag{19e}\\
&+\min\{0,
 I(U_b,W_b;G)-I(U_a,W_a;G),\\
&\qquad I(U_b,W_b;G)-I(U_a,W_a;G)
 +I(U_c,W_c;K)-I(U_b,W_b;K)\}. \tag{19f}
\end{aligned}
\]

Equations (19g) and (19h) are one inequality:

\[
\begin{aligned}
R_0+R_2\le{}&I(W_a;Y)+I(V_c;Z|W_c)
 +I(W_c;K)-I(W_b;K)+I(W_b;G)-I(W_a;G) \tag{19g}\\
&+\min\{0,
 I(V_b,W_b;K)-I(V_c,W_c;K),\\
&\qquad I(V_b,W_b;K)-I(V_c,W_c;K)
 +I(V_a,W_a;G)-I(V_b,W_b;G)\}. \tag{19h}
\end{aligned}
\]

Equations (19i) and (19j) are one inequality:

\[
\begin{aligned}
R_0+R_2\le{}&I(W_c;Z)+I(V_c;Z|W_c) \tag{19i}\\
&+\min\{0,
 I(V_b,W_b;K)-I(V_c,W_c;K),\\
&\qquad I(V_b,W_b;K)-I(V_c,W_c;K)
 +I(V_a,W_a;G)-I(V_b,W_b;G)\}. \tag{19j}
\end{aligned}
\]

\[
\begin{aligned}
R_0+R_1+R_2\le{}&\min\{I(W_a;Y),
 I(W_c;Z)+I(W_a;G)-I(W_b;G)+I(W_b;K)-I(W_c;K)\}\\
&+I(U_c,W_c;K)-I(U_b,W_b;K)
 +I(U_b,W_b;G)-I(U_a,W_a;G)\\
&+I(U_a;Y|W_a)+I(X;Z|U_c,W_c). \tag{19k}
\end{aligned}
\]

\[
\begin{aligned}
R_0+R_1+R_2\le{}&\min\{I(W_a;Y)+I(W_c;K)-I(W_b;K)
 +I(W_b;G)-I(W_a;G), I(W_c;Z)\}\\
&+I(V_a,W_a;G)-I(V_b,W_b;G)
 +I(V_b,W_b;K)-I(V_c,W_c;K)\\
&+I(V_c;Z|W_c)+I(X;Y|V_a,W_a). \tag{19l}
\end{aligned}
\]

\[
\begin{aligned}
R_0+R_1+R_2\le{}&I(W_a;Y)+I(U_a;Y|W_a)+I(V_c;Z|W_c)\\
&+I(U_b,W_b;G)-I(U_a,W_a;G)-I(V_c;K|W_c)
 +I(X;K|U_b,W_b). \tag{19m}
\end{aligned}
\]

\[
\begin{aligned}
R_0+R_1+R_2\le{}&I(W_a;Y)+I(U_a;Y|W_a)+I(V_c;Z|W_c)\\
&+I(V_b;K|W_b)-I(V_c;K|W_c)-I(V_b;G|W_b)
 +I(X;G|U_a,W_a). \tag{19n}
\end{aligned}
\]

\[
\begin{aligned}
R_0+R_1+R_2\le{}&I(W_c;Z)+I(U_a;Y|W_a)+I(V_c;Z|W_c)\\
&+I(V_b,W_b;K)-I(V_c,W_c;K)-I(U_a;G|W_a)
 +I(X;G|V_b,W_b). \tag{19o}
\end{aligned}
\]

\[
\begin{aligned}
R_0+R_1+R_2\le{}&I(W_c;Z)+I(U_a;Y|W_a)+I(V_c;Z|W_c)\\
&+I(U_b;G|W_b)-I(U_a;G|W_a)-I(U_b;K|W_b)
 +I(X;K|V_c,W_c). \tag{19p}
\end{aligned}
\]

## Both side conditions

\[
0\le I(X;Z|U_c,W_c)-I(X;K|U_c,W_c)
\le I(V_c;Z|W_c)-I(V_c;K|W_c),
\]

\[
0\le I(X;Y|V_a,W_a)-I(X;G|V_a,W_a)
\le I(U_a;Y|W_a)-I(U_a;G|W_a).
\]

No definition of $B(G,K)$, $V(q;G,K)$, $V_Q(G,K)$, or
$V_0(g,k)$ is attributed to the paper.  Those are explicit local definitions
given in `README.md`, derived from this complete constraint system.

</artifact>
<artifact path="problems/bssc-sum-capacity/contributions/theorem9-cited-premise-foundations/claims.json">
{
  "schemaVersion": 1,
  "claims": [
    {
      "claimKey": "bssc-sum-capacity/theorem9-cited-premise-foundations",
      "statement": "Assume the cited Gohari--Liu--Nair Theorem 9 outer-bound premise exactly as encoded in theorem9_spec.json and displayed for review in SOURCE_TRANSCRIPTION.md: for every finite auxiliary-receiver law T_{G,K|X,Y,Z}, achievable rates obey the stated factorization, equations (19a)-(19p), and both side conditions. Then setting R0=0 and exhaustively expanding the displayed minima and interval conditions gives exactly the independently generated local 30-row system; the exhaustive single-output term audit proves that replacing G,K by their input-only product marginals preserves the entire system, and hence for the physical BSSC C_sum <= inf_{finite-output binary-input T_{G|X},T_{K|X}} B(G,K). With the explicit extended-real local definitions (including sup(empty set)=-infinity), V_Q(G,K) <= V(1/2;G,K) <= B(G,K), and every Q0-supported row depends on the receiver channels only through (c,g,k,c), making V_0(g,k) finite and well defined on its realizable (g,k)-domain. No PDF-origin, source-fidelity, rendering, or visual-semantic assertion is part of this claim.",
      "dependencyTransactionIds": []
    }
  ]
}

</artifact>
<artifact path="problems/bssc-sum-capacity/contributions/theorem9-cited-premise-foundations/theorem9_spec.json">
{
  "schemaVersion": 1,
  "source": {
    "title": "A Two Auxiliary Receiver Outer Bound to the Capacity Region of a Two-Receiver Discrete Memoryless Broadcast Channel",
    "authors": [
      "Amin Gohari",
      "Yi Liu",
      "Chandra Nair"
    ],
    "url": "https://chandra.ie.cuhk.edu.hk/pub/papers/BC/GK-outer.pdf",
    "premiseBoundary": "The factorization, equations (19a)-(19p), and both side conditions encoded here are the explicit cited Theorem 9 premise; their source fidelity and bibliographic provenance are not verifier results.",
    "pdfSha256": "24c4153530008f7ae339ac19ca8cb90fb8ea574ea8fbcd6a36c2221722d651fa",
    "location": "Appendix B, Theorem 9, PDF pages 14-15, equations (19a)-(19p) and the two unnumbered side conditions"
  },
  "factorization": {
    "variables": ["Ua", "Va", "Wa", "Ub", "Vb", "Wb", "Uc", "Vc", "Wc", "X", "Y", "Z", "G", "K"],
    "factors": ["pX", "pUa,Va,Wa|X", "pUb,Vb,Wb|X", "pUc,Vc,Wc|X", "TY,Z|X", "TG,K|X,Y,Z"]
  },
  "termEncoding": [
    "integer coefficient",
    "group a, b, or c",
    "one of W, U|W, V|W, UW, VW, X|UW, X|VW",
    "one of Y, G, K, or Z"
  ],
  "privateMessageSpecialization": "R0=0",
  "constraints": [
    {
      "sourceLabels": ["19a"],
      "minimumPosition": "suffix",
      "rateCoefficients": [0, 0],
      "base": [[1, "a", "W", "Y"]],
      "branches": [
        {"row": "N_Y(0)", "terms": []},
        {"row": "N_Y(1)", "terms": [[1, "b", "W", "G"], [-1, "a", "W", "G"]]},
        {"row": "N_Y(2)", "terms": [[1, "b", "W", "G"], [-1, "a", "W", "G"], [1, "c", "W", "K"], [-1, "b", "W", "K"]]}
      ]
    },
    {
      "sourceLabels": ["19b"],
      "minimumPosition": "suffix",
      "rateCoefficients": [0, 0],
      "base": [[1, "c", "W", "Z"]],
      "branches": [
        {"row": "N_Z(0)", "terms": []},
        {"row": "N_Z(1)", "terms": [[1, "b", "W", "K"], [-1, "c", "W", "K"]]},
        {"row": "N_Z(2)", "terms": [[1, "b", "W", "K"], [-1, "c", "W", "K"], [1, "a", "W", "G"], [-1, "b", "W", "G"]]}
      ]
    },
    {
      "sourceLabels": ["19c", "19d"],
      "minimumPosition": "suffix",
      "rateCoefficients": [1, 0],
      "base": [[1, "a", "W", "Y"], [1, "a", "U|W", "Y"]],
      "branches": [
        {"row": "R1T(0)", "terms": []},
        {"row": "R1T(1)", "terms": [[1, "b", "UW", "G"], [-1, "a", "UW", "G"]]},
        {"row": "R1T(2)", "terms": [[1, "b", "UW", "G"], [-1, "a", "UW", "G"], [1, "c", "UW", "K"], [-1, "b", "UW", "K"]]}
      ]
    },
    {
      "sourceLabels": ["19e", "19f"],
      "minimumPosition": "suffix",
      "rateCoefficients": [1, 0],
      "base": [[1, "c", "W", "Z"], [1, "a", "U|W", "Y"], [1, "a", "W", "G"], [-1, "b", "W", "G"], [1, "b", "W", "K"], [-1, "c", "W", "K"]],
      "branches": [
        {"row": "R1A(0)", "terms": []},
        {"row": "R1A(1)", "terms": [[1, "b", "UW", "G"], [-1, "a", "UW", "G"]]},
        {"row": "R1A(2)", "terms": [[1, "b", "UW", "G"], [-1, "a", "UW", "G"], [1, "c", "UW", "K"], [-1, "b", "UW", "K"]]}
      ]
    },
    {
      "sourceLabels": ["19g", "19h"],
      "minimumPosition": "suffix",
      "rateCoefficients": [0, 1],
      "base": [[1, "a", "W", "Y"], [1, "c", "V|W", "Z"], [1, "c", "W", "K"], [-1, "b", "W", "K"], [1, "b", "W", "G"], [-1, "a", "W", "G"]],
      "branches": [
        {"row": "R2A(0)", "terms": []},
        {"row": "R2A(1)", "terms": [[1, "b", "VW", "K"], [-1, "c", "VW", "K"]]},
        {"row": "R2A(2)", "terms": [[1, "b", "VW", "K"], [-1, "c", "VW", "K"], [1, "a", "VW", "G"], [-1, "b", "VW", "G"]]}
      ]
    },
    {
      "sourceLabels": ["19i", "19j"],
      "minimumPosition": "suffix",
      "rateCoefficients": [0, 1],
      "base": [[1, "c", "W", "Z"], [1, "c", "V|W", "Z"]],
      "branches": [
        {"row": "R2T(0)", "terms": []},
        {"row": "R2T(1)", "terms": [[1, "b", "VW", "K"], [-1, "c", "VW", "K"]]},
        {"row": "R2T(2)", "terms": [[1, "b", "VW", "K"], [-1, "c", "VW", "K"], [1, "a", "VW", "G"], [-1, "b", "VW", "G"]]}
      ]
    },
    {
      "sourceLabels": ["19k"],
      "minimumPosition": "prefix",
      "rateCoefficients": [1, 1],
      "base": [[1, "c", "UW", "K"], [-1, "b", "UW", "K"], [1, "b", "UW", "G"], [-1, "a", "UW", "G"], [1, "a", "U|W", "Y"], [1, "c", "X|UW", "Z"]],
      "branches": [
        {"row": "SL(3,U)", "terms": [[1, "a", "W", "Y"]]},
        {"row": "SL(3,C)", "terms": [[1, "c", "W", "Z"], [1, "a", "W", "G"], [-1, "b", "W", "G"], [1, "b", "W", "K"], [-1, "c", "W", "K"]]}
      ]
    },
    {
      "sourceLabels": ["19l"],
      "minimumPosition": "prefix",
      "rateCoefficients": [1, 1],
      "base": [[1, "a", "VW", "G"], [-1, "b", "VW", "G"], [1, "b", "VW", "K"], [-1, "c", "VW", "K"], [1, "c", "V|W", "Z"], [1, "a", "X|VW", "Y"]],
      "branches": [
        {"row": "SR(1,C)", "terms": [[1, "a", "W", "Y"], [1, "c", "W", "K"], [-1, "b", "W", "K"], [1, "b", "W", "G"], [-1, "a", "W", "G"]]},
        {"row": "SR(1,U)", "terms": [[1, "c", "W", "Z"]]}
      ]
    },
    {
      "sourceLabels": ["19m"],
      "rateCoefficients": [1, 1],
      "base": [[1, "a", "W", "Y"], [1, "a", "U|W", "Y"], [1, "c", "V|W", "Z"], [1, "b", "UW", "G"], [-1, "a", "UW", "G"], [-1, "c", "V|W", "K"], [1, "b", "X|UW", "K"]],
      "branches": [
        {"row": "SL(2,U)", "terms": []}
      ]
    },
    {
      "sourceLabels": ["19n"],
      "rateCoefficients": [1, 1],
      "base": [[1, "a", "W", "Y"], [1, "a", "U|W", "Y"], [1, "c", "V|W", "Z"], [1, "b", "V|W", "K"], [-1, "c", "V|W", "K"], [-1, "b", "V|W", "G"], [1, "a", "X|UW", "G"]],
      "branches": [
        {"row": "SL(1,U)", "terms": []}
      ]
    },
    {
      "sourceLabels": ["19o"],
      "rateCoefficients": [1, 1],
      "base": [[1, "c", "W", "Z"], [1, "a", "U|W", "Y"], [1, "c", "V|W", "Z"], [1, "b", "VW", "K"], [-1, "c", "VW", "K"], [-1, "a", "U|W", "G"], [1, "b", "X|VW", "G"]],
      "branches": [
        {"row": "SR(2,U)", "terms": []}
      ]
    },
    {
      "sourceLabels": ["19p"],
      "rateCoefficients": [1, 1],
      "base": [[1, "c", "W", "Z"], [1, "a", "U|W", "Y"], [1, "c", "V|W", "Z"], [1, "b", "U|W", "G"], [-1, "a", "U|W", "G"], [-1, "b", "U|W", "K"], [1, "c", "X|VW", "K"]],
      "branches": [
        {"row": "SR(3,U)", "terms": []}
      ]
    }
  ],
  "sideConditions": [
    {
      "name": "Z-K side condition",
      "left": [[1, "c", "X|UW", "Z"], [-1, "c", "X|UW", "K"]],
      "right": [[1, "c", "V|W", "Z"], [-1, "c", "V|W", "K"]],
      "rows": [
        {"row": "F_Z_left", "operation": "left"},
        {"row": "F_Z_right_minus_left", "operation": "right-minus-left"}
      ]
    },
    {
      "name": "Y-G side condition",
      "left": [[1, "a", "X|VW", "Y"], [-1, "a", "X|VW", "G"]],
      "right": [[1, "a", "U|W", "Y"], [-1, "a", "U|W", "G"]],
      "rows": [
        {"row": "F_Y_left", "operation": "left"},
        {"row": "F_Y_right_minus_left", "operation": "right-minus-left"}
      ]
    }
  ]
}

</artifact>
<artifact path="problems/bssc-sum-capacity/contributions/theorem9-cited-premise-foundations/verification.json">
{
  "schemaVersion": 1,
  "verifier": {
    "id": "python-stdlib-3-13-v1",
    "specDigest": "sha256:fc7ed06b77396fabc1da84694b4d8a08800843f41ad8ca4b9cd666b67ba60884"
  },
  "entrypoint": "verify_specialization.py",
  "arguments": []
}

</artifact>
<artifact path="problems/bssc-sum-capacity/contributions/theorem9-cited-premise-foundations/verify_specialization.py">
#!/usr/bin/env python3
"""Exact premise-to-specialization audit for the private-message GK bound.

The claimed checker has two deliberately independent constructions:

1. ``theorem9_spec.json`` is the explicit cited Theorem 9 premise encoded
   term by term.
2. ``make_path_rows`` constructs the local L=3 rows from generic path formulas.

The premise's minima are expanded after setting R0=0, and the two interval
side conditions are split into four nonnegative slacks.  The independent
constructions are normalized only with I(U,W;A)=I(W;A)+I(U;A|W) and its V
analogue, then compared exactly.  The output-term audit independently checks
the input-only product-marginal reduction.  No PDF, renderer, optimizer,
third-party package, or network request is used.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


GROUPS = ("a", "b", "c")
KINDS = ("W", "U|W", "V|W", "UW", "VW", "X|UW", "X|VW")
OUTPUTS = ("Y", "G", "K", "Z")
MIRROR_KIND = {
    "W": "W",
    "U|W": "V|W",
    "V|W": "U|W",
    "UW": "VW",
    "VW": "UW",
    "X|UW": "X|VW",
    "X|VW": "X|UW",
}

# These sets are an independent audit of the distinct output-bearing terms in
# (19a)-(19p) and the two side conditions.  They are intentionally not read
# from theorem9_spec.json.
EXPECTED_TERM_AUDIT = {
    "Y": {"a:W", "a:U|W", "a:X|VW"},
    "Z": {"c:W", "c:V|W", "c:X|UW"},
    "G": {
        "a:W", "b:W", "a:UW", "b:UW", "a:VW", "b:VW",
        "a:U|W", "b:U|W", "b:V|W", "a:X|UW", "a:X|VW",
        "b:X|VW",
    },
    "K": {
        "b:W", "c:W", "b:UW", "c:UW", "b:VW", "c:VW",
        "b:U|W", "b:V|W", "c:V|W", "b:X|UW", "c:X|UW",
        "c:X|VW",
    },
}
Atom = tuple[str, str, str]  # group, kind, output
RawTerm = tuple[int, str, str, str]
Linear = dict[Atom, int]


@dataclass(frozen=True)
class Row:
    label: str
    r1: int
    r2: int
    terms: tuple[RawTerm, ...]


def term(coefficient: int, group: str, kind: str, output: str) -> RawTerm:
    return coefficient, group, kind, output


def add_coefficient(result: Linear, atom: Atom, coefficient: int) -> None:
    result[atom] = result.get(atom, 0) + coefficient
    if result[atom] == 0:
        del result[atom]


def normalize_terms(terms: Iterable[RawTerm]) -> Linear:
    """Normalize solely by expanding UW and VW with the chain rule."""
    result: Linear = {}
    for coefficient, group, kind, output in terms:
        if (
            not isinstance(coefficient, int)
            or coefficient == 0
            or group not in GROUPS
            or kind not in KINDS
            or output not in OUTPUTS
        ):
            raise AssertionError((coefficient, group, kind, output))
        if kind == "UW":
            add_coefficient(result, (group, "W", output), coefficient)
            add_coefficient(result, (group, "U|W", output), coefficient)
        elif kind == "VW":
            add_coefficient(result, (group, "W", output), coefficient)
            add_coefficient(result, (group, "V|W", output), coefficient)
        else:
            add_coefficient(result, (group, kind, output), coefficient)
    return result


def as_raw_terms(value: object) -> tuple[RawTerm, ...]:
    if not isinstance(value, list):
        raise AssertionError("term list must be an array")
    result: list[RawTerm] = []
    for item in value:
        if not isinstance(item, list) or len(item) != 4:
            raise AssertionError(f"invalid encoded term: {item!r}")
        coefficient, group, kind, output = item
        if not all(isinstance(x, str) for x in (group, kind, output)):
            raise AssertionError(f"invalid encoded term: {item!r}")
        result.append(term(coefficient, group, kind, output))
    normalize_terms(result)
    return tuple(result)


def mirror_terms(terms: tuple[RawTerm, ...]) -> tuple[RawTerm, ...]:
    group_mirror = {"a": "c", "b": "b", "c": "a"}
    output_mirror = {"Y": "Z", "G": "K", "K": "G", "Z": "Y"}
    return tuple(
        term(
            coefficient,
            group_mirror[group],
            MIRROR_KIND[kind],
            output_mirror[output],
        )
        for coefficient, group, kind, output in terms
    )


def make_path_rows() -> list[Row]:
    """Construct the L=3 private-message rows from generic path formulas."""
    rows: list[Row] = []
    length = 3

    def group(index: int) -> str:
        return GROUPS[index - 1]

    def output(index: int) -> str:
        return OUTPUTS[index]

    for middle in range(1, length + 1):
        u_walk = tuple(
            entry
            for index in range(1, middle)
            for entry in (
                term(1, group(index), "UW", output(index - 1)),
                term(-1, group(index), "UW", output(index)),
            )
        )
        uc_walk = tuple(
            entry
            for index in range(1, middle)
            for entry in (
                term(1, group(index), "U|W", output(index - 1)),
                term(-1, group(index), "U|W", output(index)),
            )
        )
        vc_walk = tuple(
            entry
            for index in range(middle + 1, length + 1)
            for entry in (
                term(1, group(index), "V|W", output(index)),
                term(-1, group(index), "V|W", output(index - 1)),
            )
        )
        v_walk = tuple(
            entry
            for index in range(middle + 1, length + 1)
            for entry in (
                term(1, group(index), "VW", output(index)),
                term(-1, group(index), "VW", output(index - 1)),
            )
        )
        rows.append(
            Row(
                f"SL({middle},U)",
                1,
                1,
                u_walk
                + (
                    term(1, group(middle), "UW", output(middle - 1)),
                    term(1, group(middle), "X|UW", output(middle)),
                )
                + vc_walk,
            )
        )
        rows.append(
            Row(
                f"SR({middle},U)",
                1,
                1,
                v_walk
                + (
                    term(1, group(middle), "VW", output(middle)),
                    term(1, group(middle), "X|VW", output(middle - 1)),
                )
                + uc_walk,
            )
        )
        if middle == length:
            rows.append(
                Row(
                    f"SL({middle},C)",
                    1,
                    1,
                    uc_walk
                    + (
                        term(1, group(middle), "U|W", output(middle - 1)),
                        term(1, group(middle), "X|UW", output(middle)),
                        term(1, group(middle), "W", output(middle)),
                    )
                    + vc_walk,
                )
            )
        if middle == 1:
            rows.append(
                Row(
                    f"SR({middle},C)",
                    1,
                    1,
                    vc_walk
                    + (
                        term(1, group(middle), "V|W", output(middle)),
                        term(1, group(middle), "X|VW", output(middle - 1)),
                        term(1, group(middle), "W", output(middle - 1)),
                    )
                    + uc_walk,
                )
            )

    r1_rows: list[Row] = []
    for stop in range(length):
        terms = tuple(
            entry
            for index in range(1, stop + 1)
            for entry in (
                term(1, group(index), "UW", output(index - 1)),
                term(-1, group(index), "UW", output(index)),
            )
        ) + (term(1, group(stop + 1), "UW", output(stop)),)
        r1_rows.append(Row(f"R1T({stop})", 1, 0, terms))
    for stop in range(length):
        terms = tuple(
            entry
            for index in range(1, stop + 1)
            for entry in (
                term(1, group(index), "U|W", output(index - 1)),
                term(-1, group(index), "U|W", output(index)),
            )
        ) + (term(1, group(stop + 1), "U|W", output(stop)),) + tuple(
            entry
            for index in range(stop + 1, length)
            for entry in (
                term(1, group(index), "W", output(index)),
                term(-1, group(index + 1), "W", output(index)),
            )
        ) + (term(1, group(length), "W", output(length)),)
        r1_rows.append(Row(f"R1A({stop})", 1, 0, terms))
    rows.extend(r1_rows)
    rows.extend(
        Row("R2" + row.label[2:], 0, 1, mirror_terms(row.terms))
        for row in r1_rows
    )

    nonnegative_y: list[Row] = []
    for stop in range(length):
        terms = (term(1, "a", "W", "Y"),) + tuple(
            entry
            for index in range(1, stop + 1)
            for entry in (
                term(1, group(index + 1), "W", output(index)),
                term(-1, group(index), "W", output(index)),
            )
        )
        nonnegative_y.append(Row(f"N_Y({stop})", 0, 0, terms))
    rows.extend(nonnegative_y)
    rows.extend(
        Row(f"N_Z({stop})", 0, 0, mirror_terms(row.terms))
        for stop, row in enumerate(nonnegative_y)
    )

    rows.extend(
        [
            Row(
                "F_Z_left",
                0,
                0,
                (term(1, "c", "X|UW", "Z"), term(-1, "c", "X|UW", "K")),
            ),
            Row(
                "F_Z_right_minus_left",
                0,
                0,
                (
                    term(1, "c", "V|W", "Z"),
                    term(-1, "c", "V|W", "K"),
                    term(-1, "c", "X|UW", "Z"),
                    term(1, "c", "X|UW", "K"),
                ),
            ),
            Row(
                "F_Y_left",
                0,
                0,
                (term(1, "a", "X|VW", "Y"), term(-1, "a", "X|VW", "G")),
            ),
            Row(
                "F_Y_right_minus_left",
                0,
                0,
                (
                    term(1, "a", "U|W", "Y"),
                    term(-1, "a", "U|W", "G"),
                    term(-1, "a", "X|VW", "Y"),
                    term(1, "a", "X|VW", "G"),
                ),
            ),
        ]
    )
    return rows


def load_source_rows(spec: dict[str, object]) -> tuple[dict[str, Row], dict[str, str]]:
    rows: dict[str, Row] = {}
    origins: dict[str, str] = {}
    labels_seen: list[str] = []
    raw_terms: list[RawTerm] = []

    constraints = spec.get("constraints")
    if not isinstance(constraints, list) or len(constraints) != 12:
        raise AssertionError("expected the 12 substantive Theorem 9 constraints")
    for constraint in constraints:
        if not isinstance(constraint, dict):
            raise AssertionError("constraint must be an object")
        source_labels = constraint.get("sourceLabels")
        rates = constraint.get("rateCoefficients")
        branches = constraint.get("branches")
        if (
            not isinstance(source_labels, list)
            or not all(isinstance(item, str) for item in source_labels)
            or not isinstance(rates, list)
            or rates not in ([0, 0], [1, 0], [0, 1], [1, 1])
            or not isinstance(branches, list)
            or not branches
        ):
            raise AssertionError(f"invalid constraint envelope: {constraint!r}")
        labels_seen.extend(source_labels)
        base = as_raw_terms(constraint.get("base"))
        raw_terms.extend(base)
        for branch_index, branch in enumerate(branches):
            if not isinstance(branch, dict) or set(branch) != {"row", "terms"}:
                raise AssertionError(f"invalid minimum branch: {branch!r}")
            label = branch["row"]
            if not isinstance(label, str) or label in rows:
                raise AssertionError(f"duplicate or invalid row label: {label!r}")
            branch_terms = as_raw_terms(branch["terms"])
            raw_terms.extend(branch_terms)
            rows[label] = Row(label, rates[0], rates[1], base + branch_terms)
            source_text = ",".join(source_labels)
            origins[label] = f"({source_text}) branch {branch_index}"

    expected_labels = [f"19{chr(ord('a') + index)}" for index in range(16)]
    if labels_seen != expected_labels:
        raise AssertionError((labels_seen, expected_labels))

    side_conditions = spec.get("sideConditions")
    if not isinstance(side_conditions, list) or len(side_conditions) != 2:
        raise AssertionError("expected exactly two side conditions")
    for side in side_conditions:
        if not isinstance(side, dict):
            raise AssertionError("side condition must be an object")
        name = side.get("name")
        left = as_raw_terms(side.get("left"))
        right = as_raw_terms(side.get("right"))
        raw_terms.extend(left)
        raw_terms.extend(right)
        side_rows = side.get("rows")
        if not isinstance(name, str) or not isinstance(side_rows, list):
            raise AssertionError("invalid side condition envelope")
        for side_row in side_rows:
            if not isinstance(side_row, dict) or set(side_row) != {"row", "operation"}:
                raise AssertionError(f"invalid side row: {side_row!r}")
            label = side_row["row"]
            operation = side_row["operation"]
            if not isinstance(label, str) or label in rows:
                raise AssertionError(f"duplicate or invalid row label: {label!r}")
            if operation == "left":
                terms = left
            elif operation == "right-minus-left":
                terms = right + tuple(
                    term(-coefficient, group, kind, output)
                    for coefficient, group, kind, output in left
                )
            else:
                raise AssertionError(f"invalid side operation: {operation!r}")
            rows[label] = Row(label, 0, 0, terms)
            origins[label] = f"{name}: {operation}"

    audit = {output: set() for output in OUTPUTS}
    for _coefficient, group, kind, output in raw_terms:
        audit[output].add(f"{group}:{kind}")
    if audit != EXPECTED_TERM_AUDIT:
        raise AssertionError((audit, EXPECTED_TERM_AUDIT))
    return rows, origins


def main() -> None:
    root = Path(__file__).resolve().parent
    spec = json.loads((root / "theorem9_spec.json").read_text(encoding="utf-8"))
    if spec.get("schemaVersion") != 1:
        raise AssertionError("unsupported theorem specification version")
    source = spec.get("source")
    if not isinstance(source, dict):
        raise AssertionError("missing source metadata")
    premise_boundary = (
        "The factorization, equations (19a)-(19p), and both side conditions "
        "encoded here are the explicit cited Theorem 9 premise; their source "
        "fidelity and bibliographic provenance are not verifier results."
    )
    if source.get("premiseBoundary") != premise_boundary:
        raise AssertionError("unexpected mathematical-premise boundary")
    expected_factorization = {
        "variables": [
            "Ua", "Va", "Wa", "Ub", "Vb", "Wb", "Uc", "Vc", "Wc",
            "X", "Y", "Z", "G", "K",
        ],
        "factors": [
            "pX", "pUa,Va,Wa|X", "pUb,Vb,Wb|X", "pUc,Vc,Wc|X",
            "TY,Z|X", "TG,K|X,Y,Z",
        ],
    }
    if spec.get("factorization") != expected_factorization:
        raise AssertionError("unexpected cited-premise factorization")
    if spec.get("privateMessageSpecialization") != "R0=0":
        raise AssertionError("unexpected private-message specialization")
    constraints = spec.get("constraints")
    if not isinstance(constraints, list):
        raise AssertionError("premise constraints must be an array")
    labels: list[str] = []
    for constraint in constraints:
        if not isinstance(constraint, dict):
            raise AssertionError("premise constraint must be an object")
        raw_labels = constraint.get("sourceLabels")
        if not isinstance(raw_labels, list) or not all(
            isinstance(label, str) for label in raw_labels
        ):
            raise AssertionError("invalid premise source labels")
        labels.extend(raw_labels)
    expected_labels = [f"19{letter}" for letter in "abcdefghijklmnop"]
    if labels != expected_labels:
        raise AssertionError("premise does not encode exactly equations (19a)-(19p)")
    side_conditions = spec.get("sideConditions")
    if not isinstance(side_conditions, list) or len(side_conditions) != 2:
        raise AssertionError("premise does not encode exactly two side conditions")
    print("PASS explicit cited premise structure: factorization, 16 equations, 2 side conditions")

    source_rows, origins = load_source_rows(spec)
    path_rows_list = make_path_rows()
    if len(path_rows_list) != 30:
        raise AssertionError(f"path construction produced {len(path_rows_list)} rows")
    path_rows = {row.label: row for row in path_rows_list}
    if len(path_rows) != 30:
        raise AssertionError("path construction contains duplicate labels")
    if set(source_rows) != set(path_rows):
        raise AssertionError(
            f"row-label mismatch: source-only={sorted(set(source_rows)-set(path_rows))}, "
            f"path-only={sorted(set(path_rows)-set(source_rows))}"
        )

    for label, source_row in source_rows.items():
        path_row = path_rows[label]
        source_value = (source_row.r1, source_row.r2, normalize_terms(source_row.terms))
        path_value = (path_row.r1, path_row.r2, normalize_terms(path_row.terms))
        if source_value != path_value:
            raise AssertionError(
                f"{label} mismatch\nsource={source_value!r}\npath={path_value!r}"
            )
        print(f"PASS {origins[label]} -> {label}")

    counts = {output: len(EXPECTED_TERM_AUDIT[output]) for output in OUTPUTS}
    print(f"PASS exhaustive single-output term audit: {counts}")
    print(
        "PASS: cited-premise R0=0 expansion and all 30 independently generated "
        "private-message rows agree exactly"
    )


if __name__ == "__main__":
    main()

</artifact>
</contribution>
<contribution>
ordinal: 11
transaction_id: e2bbc1e210e496b3c834e658820fc90287f3b2c0
contribution_id: finite-grid-q0-foundations
author: Robert Raynor
<artifact path="problems/bssc-sum-capacity/contributions/finite-grid-q0-foundations/README.md">
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

</artifact>
<artifact path="problems/bssc-sum-capacity/contributions/finite-grid-q0-foundations/claims.json">
{
  "schemaVersion": 1,
  "claims": [
    {
      "claimKey": "bssc-sum-capacity/finite-grid-q0-foundations",
      "statement": "Using the accepted private-message 30-row definitions and optimization order of transaction e3c1036ca607539a5ebcddf3058e6014ac5c1cd9, let Q be any N-point posterior grid containing {0,1/2,1}. Every finite-output binary-input receiver has an at-most-N-output replacement with the same mutual-information samples on Q, so inf_{G,K finite} V_Q(G,K) = inf_{|G|,|K|<=N} V_Q(G,K); when Q is reflection closed, inf_{m finite} V_Q(m,m^circ) = inf_{|supp(m)|<=N} V_Q(m,m^circ). For Q0={0,1/2,1} and c=h_2(1/4)-1/2, inf_{G,K finite} V_{Q0}(G,K) = inf_{m finite} V_{Q0}(m,m^circ) = c. Moreover, for every finite-output input-only pair G,K with g=J_G(1/2), k=J_K(1/2), B(G,K) >= V_0(g,k) >= max{F(g),F(k)}, where F(x)=2c max{c,x}/(c+x); consequently, if c <= U < 2c and B(G,K) <= U, then 2c^2/U-c <= g,k <= Uc/(2c-U). These are finite-grid and necessary-coercivity statements only, with no continuum cardinality, limit interchange, or full-functional reflected-optimality assertion.",
      "dependencyTransactionIds": [
        "e3c1036ca607539a5ebcddf3058e6014ac5c1cd9"
      ]
    }
  ]
}

</artifact>
<artifact path="problems/bssc-sum-capacity/contributions/finite-grid-q0-foundations/verification.json">
{
  "schemaVersion": 1,
  "verifier": {
    "id": "python-stdlib-3-13-v1",
    "specDigest": "sha256:fc7ed06b77396fabc1da84694b4d8a08800843f41ad8ca4b9cd666b67ba60884"
  },
  "entrypoint": "verify_q0.py",
  "arguments": []
}

</artifact>
<artifact path="problems/bssc-sum-capacity/contributions/finite-grid-q0-foundations/verify_q0.py">
#!/usr/bin/env python3
"""Exact symbolic audit for the finite-grid Q0 foundation claim.

No optimizer or floating-point comparison is used.  The program rebuilds the
30 scalar rows supplied by the declared foundation transaction, compares them
with a reviewed normalized-signature digest, and checks the H/L/X witnesses from README.md by
coefficientwise nonnegativity after the stated nonnegative substitutions.
"""

from __future__ import annotations

import hashlib
import json
from collections import Counter
from dataclasses import dataclass
from fractions import Fraction as F
from pathlib import Path


Term = tuple[int, str, int, F]  # group 1..3, kind, letter Y/G/K/Z, coefficient

FOUNDATION_TRANSACTION = "e3c1036ca607539a5ebcddf3058e6014ac5c1cd9"
EXPECTED_FOUNDATION_ROW_SHA256 = (
    "9d742dba6f0c176fbf5152ead6e44ffbb48095aa48a41e6f31f598529dcfb931"
)


@dataclass(frozen=True)
class Row:
    label: str
    r1: int
    r2: int
    terms: tuple[Term, ...]


MIRROR_KIND = {
    "W": "W",
    "U|W": "V|W",
    "V|W": "U|W",
    "UW": "VW",
    "VW": "UW",
    "X|UW": "X|VW",
    "X|VW": "X|UW",
}


def mirror_terms(terms: tuple[Term, ...]) -> tuple[Term, ...]:
    return tuple((4 - j, MIRROR_KIND[kind], 3 - letter, coeff)
                 for j, kind, letter, coeff in terms)


def make_rows() -> list[Row]:
    """Build the L=3 manuscript rows directly from their path formulas."""
    rows: list[Row] = []
    L = 3

    for m in range(1, L + 1):
        u_walk = tuple(
            term for j in range(1, m)
            for term in ((j, "UW", j - 1, F(1)), (j, "UW", j, F(-1)))
        )
        uc_walk = tuple(
            term for j in range(1, m)
            for term in ((j, "U|W", j - 1, F(1)), (j, "U|W", j, F(-1)))
        )
        vc_walk = tuple(
            term for j in range(m + 1, L + 1)
            for term in ((j, "V|W", j, F(1)), (j, "V|W", j - 1, F(-1)))
        )
        v_walk = tuple(
            term for j in range(m + 1, L + 1)
            for term in ((j, "VW", j, F(1)), (j, "VW", j - 1, F(-1)))
        )
        rows.append(Row(f"SL({m},U)", 1, 1, u_walk +
                        ((m, "UW", m - 1, F(1)),
                         (m, "X|UW", m, F(1))) + vc_walk))
        rows.append(Row(f"SR({m},U)", 1, 1, v_walk +
                        ((m, "VW", m, F(1)),
                         (m, "X|VW", m - 1, F(1))) + uc_walk))
        if m == L:
            rows.append(Row(f"SL({m},C)", 1, 1, uc_walk +
                            ((m, "U|W", m - 1, F(1)),
                             (m, "X|UW", m, F(1)),
                             (m, "W", m, F(1))) + vc_walk))
        if m == 1:
            rows.append(Row(f"SR({m},C)", 1, 1, vc_walk +
                            ((m, "V|W", m, F(1)),
                             (m, "X|VW", m - 1, F(1)),
                             (m, "W", m - 1, F(1))) + uc_walk))

    r1_rows: list[Row] = []
    for t in range(L):
        terms = tuple(
            term for j in range(1, t + 1)
            for term in ((j, "UW", j - 1, F(1)), (j, "UW", j, F(-1)))
        ) + ((t + 1, "UW", t, F(1)),)
        r1_rows.append(Row(f"R1T({t})", 1, 0, terms))
    for s in range(L):
        terms = tuple(
            term for j in range(1, s + 1)
            for term in ((j, "U|W", j - 1, F(1)),
                         (j, "U|W", j, F(-1)))
        ) + ((s + 1, "U|W", s, F(1)),) + tuple(
            term for j in range(s + 1, L)
            for term in ((j, "W", j, F(1)), (j + 1, "W", j, F(-1)))
        ) + ((L, "W", L, F(1)),)
        r1_rows.append(Row(f"R1A({s})", 1, 0, terms))
    rows.extend(r1_rows)
    rows.extend(Row("R2" + row.label[2:], 0, 1, mirror_terms(row.terms))
                for row in r1_rows)

    n_rows: list[Row] = []
    for t in range(L):
        terms = ((1, "W", 0, F(1)),) + tuple(
            term for j in range(1, t + 1)
            for term in ((j + 1, "W", j, F(1)), (j, "W", j, F(-1)))
        )
        n_rows.append(Row(f"N_Y({t})", 0, 0, terms))
    rows.extend(n_rows)
    rows.extend(Row(f"N_Z({t})", 0, 0, mirror_terms(row.terms))
                for t, row in enumerate(n_rows))

    rows.extend([
        Row("F_Z_left", 0, 0,
            ((3, "X|UW", 3, F(1)), (3, "X|UW", 2, F(-1)))),
        Row("F_Z_right_minus_left", 0, 0,
            ((3, "V|W", 3, F(1)), (3, "V|W", 2, F(-1)),
             (3, "X|UW", 3, F(-1)), (3, "X|UW", 2, F(1)))),
        Row("F_Y_left", 0, 0,
            ((1, "X|VW", 0, F(1)), (1, "X|VW", 1, F(-1)))),
        Row("F_Y_right_minus_left", 0, 0,
            ((1, "U|W", 0, F(1)), (1, "U|W", 1, F(-1)),
             (1, "X|VW", 0, F(-1)), (1, "X|VW", 1, F(1)))),
    ])
    return rows


def normalized_row_digest(rows: list[Row]) -> str:
    """Digest the same raw path-row signature verified by the dependency."""
    group_name = {1: "a", 2: "b", 3: "c"}
    output_name = {0: "Y", 1: "G", 2: "K", 3: "Z"}
    value = [
        {
            "label": row.label,
            "r1": row.r1,
            "r2": row.r2,
            "terms": sorted(
                [group_name[group], kind, output_name[letter], int(coefficient)]
                for group, kind, letter, coefficient in row.terms
            ),
        }
        for row in sorted(rows, key=lambda item: item.label)
    ]
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(encoded).hexdigest()


def row_signature(row: Row) -> tuple[int, int, tuple[Term, ...]]:
    return row.r1, row.r2, tuple(sorted(row.terms))


Exponent = tuple[int, int, int]


class Poly:
    """Polynomial in three formal nonnegative variables, over Q."""

    def __init__(self, terms: dict[Exponent, F] | int = 0):
        if isinstance(terms, int):
            self.terms = {(0, 0, 0): F(terms)} if terms else {}
        else:
            self.terms = {power: F(value) for power, value in terms.items()
                          if value}

    @classmethod
    def var(cls, coordinate: int) -> "Poly":
        power = [0, 0, 0]
        power[coordinate] = 1
        return cls({tuple(power): F(1)})

    def __add__(self, other: "Poly | int") -> "Poly":
        if isinstance(other, int):
            other = Poly(other)
        terms = self.terms.copy()
        for power, value in other.terms.items():
            terms[power] = terms.get(power, F(0)) + value
            if terms[power] == 0:
                del terms[power]
        return Poly(terms)

    __radd__ = __add__

    def __neg__(self) -> "Poly":
        return Poly({power: -value for power, value in self.terms.items()})

    def __sub__(self, other: "Poly | int") -> "Poly":
        return self + (-other if isinstance(other, Poly) else -Poly(other))

    def __rsub__(self, other: int) -> "Poly":
        return Poly(other) - self

    def __mul__(self, other: "Poly | int | F") -> "Poly":
        if isinstance(other, (int, F)):
            other = Poly({(0, 0, 0): F(other)})
        terms: dict[Exponent, F] = {}
        for left_power, left_value in self.terms.items():
            for right_power, right_value in other.terms.items():
                power = tuple(left_power[i] + right_power[i]
                              for i in range(3))
                terms[power] = terms.get(power, F(0)) + left_value * right_value
        return Poly(terms)

    __rmul__ = __mul__

    def __eq__(self, other: object) -> bool:
        return isinstance(other, Poly) and self.terms == other.terms

    def __hash__(self) -> int:
        return hash(tuple(sorted(self.terms.items())))

    def coefficientwise_nonnegative(self) -> bool:
        return all(value >= 0 for value in self.terms.values())

    def __repr__(self) -> str:
        return f"Poly({self.terms!r})"


ZERO = Poly()


def info_numerator(kind: str, denominator: Poly,
                   block: tuple[Poly, Poly, Poly]) -> Poly:
    """Numerator of a Q0 row term when block entries share denominator."""
    a, u, v = block
    return {
        "W": a,
        "U|W": u,
        "V|W": v,
        "UW": a + u,
        "VW": a + v,
        "X|UW": denominator - a - u,
        "X|VW": denominator - a - v,
    }[kind]


def row_slack_numerator(row: Row, values: tuple[Poly, Poly, Poly, Poly],
                        denominator: Poly,
                        blocks: tuple[tuple[Poly, Poly, Poly], ...],
                        rate_numerator: Poly) -> Poly:
    rhs = ZERO
    for group, kind, letter, coefficient in row.terms:
        rhs += coefficient * values[letter] * info_numerator(
            kind, denominator, blocks[group - 1])
    return rhs - (row.r1 + row.r2) * rate_numerator


def check_box_constraints(denominator: Poly,
                          blocks: tuple[tuple[Poly, Poly, Poly], ...]) -> None:
    for block in blocks:
        a, u, v = block
        for numerator in (a, u, v, denominator - a - u,
                          denominator - a - v):
            assert numerator.coefficientwise_nonnegative(), numerator


def check_case(name: str, rows: list[Row],
               values: tuple[Poly, Poly, Poly, Poly], denominator: Poly,
               blocks: tuple[tuple[Poly, Poly, Poly], ...],
               rate_numerator: Poly, expected_slacks: set[Poly]) -> None:
    check_box_constraints(denominator, blocks)
    actual: set[Poly] = set()
    for row in rows:
        slack = row_slack_numerator(
            row, values, denominator, blocks, rate_numerator)
        assert slack.coefficientwise_nonnegative(), (name, row.label, slack)
        actual.add(slack)
    assert actual == expected_slacks, (name, actual, expected_slacks)
    print(f"PASS {name}: all 30 row slacks and all 15 box slacks are nonnegative")


Linear = dict[str, F]


def add_linear(dst: Linear, src: Linear, scale: F) -> None:
    for key, value in src.items():
        dst[key] = dst.get(key, F(0)) + scale * value
        if dst[key] == 0:
            del dst[key]


def common_curve_factor(group: int, kind: str) -> Linear:
    """Formal multiplier of a common curve value for one generic block."""
    a, u, v = f"A{group}", f"U{group}", f"V{group}"
    return {
        "W": {a: F(1)},
        "U|W": {u: F(1)},
        "V|W": {v: F(1)},
        "UW": {a: F(1), u: F(1)},
        "VW": {a: F(1), v: F(1)},
        "X|UW": {"1": F(1), a: F(-1), u: F(-1)},
        "X|VW": {"1": F(1), a: F(-1), v: F(-1)},
    }[kind]


def main() -> None:
    root = Path(__file__).resolve().parent
    claim_manifest = json.loads((root / "claims.json").read_text(encoding="utf-8"))
    claims = claim_manifest.get("claims")
    assert claim_manifest.get("schemaVersion") == 1
    assert isinstance(claims, list) and len(claims) == 1
    assert claims[0].get("claimKey") == (
        "bssc-sum-capacity/finite-grid-q0-foundations"
    )
    assert claims[0].get("dependencyTransactionIds") == [FOUNDATION_TRANSACTION]
    print(f"PASS sole logical dependency: {FOUNDATION_TRANSACTION}")

    rows = make_rows()
    expected_labels = (
        "SL(1,U) SR(1,U) SR(1,C) SL(2,U) SR(2,U) SL(3,U) SR(3,U) "
        "SL(3,C) R1T(0) R1T(1) R1T(2) R1A(0) R1A(1) R1A(2) "
        "R2T(0) R2T(1) R2T(2) R2A(0) R2A(1) R2A(2) "
        "N_Y(0) N_Y(1) N_Y(2) N_Z(0) N_Z(1) N_Z(2) "
        "F_Z_left F_Z_right_minus_left F_Y_left F_Y_right_minus_left"
    ).split()
    assert len(rows) == 30
    assert [row.label for row in rows] == expected_labels
    row_digest = normalized_row_digest(rows)
    assert row_digest == EXPECTED_FOUNDATION_ROW_SHA256, row_digest
    print(
        f"PASS foundation rows: {FOUNDATION_TRANSACTION}, "
        f"sha256:{row_digest}"
    )
    signatures = Counter(row_signature(row) for row in rows)
    mirrored_signatures = Counter(
        row_signature(Row("", row.r2, row.r1, mirror_terms(row.terms)))
        for row in rows
    )
    assert signatures == mirrored_signatures
    print("PASS skew symmetry: G/K, Y/Z, group order, U/V, and R1/R2")

    # H: formal variables are (c,p,y), with x=c+p.  All are nonnegative.
    c, p, y = (Poly.var(i) for i in range(3))
    x = c + p
    denominator = c + x
    high_blocks = ((x, ZERO, c), (x, c, ZERO), (x, c, ZERO))
    check_case(
        "H", rows, (c, x, y, c), denominator, high_blocks, c * x,
        {ZERO, c * x})

    # L: variables are (x,p,q), with y=x+p and c=y+q.
    x, p, q = (Poly.var(i) for i in range(3))
    y = x + p
    c = y + q
    denominator = c + x
    low_blocks = ((x, c, ZERO), (x, ZERO, c), (x, ZERO, c))
    check_case(
        "L", rows, (c, x, y, c), denominator, low_blocks, c * c,
        {ZERO, x * c, c * q, c * (p + q)})

    # X: variables are (x,p,q), with c=x+p, y=c+q and Delta=p+q.
    x, p, q = (Poly.var(i) for i in range(3))
    c = x + p
    y = c + q
    delta = p + q
    denominator = (c + x) * delta
    a = x * delta
    b = c * delta
    middle_a = x * p + x * q + p * q
    middle_v = c * p
    cross_blocks = ((a, b, ZERO), (middle_a, ZERO, middle_v),
                    (b, a, ZERO))
    cross_slacks = {
        ZERO,
        x * q * delta,
        x * c * delta,
        x * p * q,
        delta * (c * c + x * q),
        x * p * y,
        x * (c * delta + p * q),
        c * c * delta,
        p * c * delta,
    }
    check_case(
        "X", rows, (c, x, y, c), denominator, cross_blocks,
        c * c * delta, cross_slacks)

    # For the matching construction all four sampled receiver curves are
    # identical.  The SL(1,U) row is then exactly c for every Q0 hierarchy.
    upper_row = next(row for row in rows if row.label == "SL(1,U)")
    polynomial: Linear = {}
    for group, kind, _letter, coeff in upper_row.terms:
        add_linear(polynomial, common_curve_factor(group, kind), coeff)
    assert polynomial == {"1": F(1)}, polynomial

    print("PASS upper: SL(1,U) is identically c when all four Q0 curves agree")
    print("PASS: exact finite-grid Q0 coercivity certificate complete")


if __name__ == "__main__":
    main()

</artifact>
</contribution>