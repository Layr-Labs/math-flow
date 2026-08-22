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
ordinal: 4
transaction_id: f236017c62c67ce4218c1f81ea34134f0954b556
contribution_id: uv-product-branchwise-additivity
author: Robert Raynor
<artifact path="problems/bssc-sum-capacity/contributions/uv-product-branchwise-additivity/README.md">
# Exact UV product and branchwise additivity

## Claim and scope

This contribution independently ports and rechecks the two accepted Yukon
artifacts `upper-uv-additivity` and `frontier-uv-branchwise`.  They form one
dependency-ordered theorem chain for the two separately relaxed UV sum-rate
rows.

For a finite-alphabet discrete memoryless broadcast channel \(W\), write

\[
t_W(p)=I_p(X;Y)-I_p(X;Z)
\]

and let \(\mathfrak C\) denote the upper concave envelope on the input
simplex.  Define

\[
A_W(p)=I_p(X;Y)+\mathfrak C[-t_W](p),
\qquad
D_W(p)=I_p(X;Z)+\mathfrak C[t_W](p),
\]

\[
B_{\rm avg}(W)=\sup_p\frac{A_W(p)+D_W(p)}2,
\qquad
B_{\rm br}(W)=\sup_p\min\{A_W(p),D_W(p)\}.
\]

The checked claims are:

1. For arbitrary finite-alphabet DMBCs,
   \[
   B_{\rm avg}(W_1\times W_2)
   =B_{\rm avg}(W_1)+B_{\rm avg}(W_2).
   \]
   The product-channel prior may be correlated and the envelope auxiliary may
   be joint across factors.
2. If an involutive input relabeling exchanges the two receivers, then
   \[
   B_{\rm br}(W)=B_{\rm avg}(W),
   \]
   and the optimum may be restricted to invariant input laws.
3. Finite products preserve this receiver-skew symmetry, so both scalar
   functionals are exactly additive on arbitrary finite products of such
   channels.
4. For the half-skew BSSC \(P\), the unique invariant binary prior is the fair
   prior.  Combining the theorem with the sharp BSSC posterior support already
   represented by canonical transaction
   `c70e1829a7c6a2a8cb8cfc2383f8abf825ac5ea6` gives
   \[
   B_{\rm br}(P^{\times n})=B_{\rm avg}(P^{\times n})
   =n\left(2h_2(1/4)-\frac54\right)
   \]
   for every finite \(n\ge1\).  Numerically, the normalized value is
   \(0.3725562489182657\ldots\) bits per channel use.

The last value is a valid but non-frontier UV converse.  It is weaker than the
current certified full-Theorem-9 capacity upper bound
\(0.369296945969202842443\), so this contribution does not move either endpoint
of the governed capacity interval.

This is an ordinary unregistered contribution.  The UV program lies outside
the registered `yukon-auxiliary-converse-port` scope, and this contribution
does not claim to advance or complete that direction.

## Argument

For any finite auxiliary

\[
A-(X_1,X_2)-(Y_1,Z_1,Y_2,Z_2)
\]

on a product DMBC, the crucial exact identity is

\[
\begin{aligned}
&I(X_1X_2;Y_1Y_2\mid A)-I(X_1X_2;Z_1Z_2\mid A)\\
&=I(X_1;Y_1\mid A,Z_2)-I(X_1;Z_1\mid A,Z_2)\\
&\quad+I(X_2;Y_2\mid A,Y_1)-I(X_2;Z_2\mid A,Y_1).
\end{aligned}
\]

The two chain-rule correction terms are both
\(I(Y_1;Z_2\mid A)\) and cancel.  The conditioned variables
\((A,Z_2)\) and \((A,Y_1)\) remain valid one-factor auxiliaries.  Applying the
one-factor envelopes and their concavity gives

\[
\mathfrak C[\pm t_{12}](p_{12})
\le
\mathfrak C[\pm t_1](p_1)+\mathfrak C[\pm t_2](p_2)
\]

even for correlated \(p_{12}\).  Mutual-information subadditivity proves the
product upper bound.  Product priors and independent near-optimal posterior
decompositions prove the reverse inequality.

For a receiver-skew involution \(S\), posterior decompositions are carried
bijectively to posterior decompositions and \(t(Sp)=-t(p)\).  Hence

\[
A_W(Sp)=D_W(p),\qquad D_W(Sp)=A_W(p).
\]

Both rows are concave.  At \(\bar p=(p+Sp)/2\), each row is therefore at least
the average of the two rows at \(p\).  This gives
\(B_{\rm br}\ge B_{\rm avg}\); the pointwise inequality
\(\min(a,d)\le(a+d)/2\) gives the reverse direction.

For the BSSC, put \(h=h_2(1/4)\), \(c=h-1/2\), and \(r=h-3/4\).  The sharp
canonical support from transaction `c70e182...` and its reflection give
\(t(q)\le2rq\).  Thus every fair-prior posterior decomposition has mean
\(1/2\) and average \(t\) at most \(r\).  Equality is attained by the source
mixture with masses \(5/8\) at \(q=4/5\) and \(3/8\) at \(q=0\), since
\(t(4/5)=8r/5\).  Therefore the relevant envelope value is exactly \(r\), and
the fair-prior UV value is

\[
c+r=2h_2(1/4)-\frac54.
\]

## Immutable Yukon provenance

All source reads were made from the dirty-worktree-independent Git objects of
`/Users/robert/eig/autoresearch/bssc/yukon-bssc-challenge`.  The accepted
formed source snapshot is `local-yukon/canonical` commit
`1af4e641fcfd4c76ec382c4e7cd5bed32af15e9c`.

### Averaged functional

- Original source commit: `1e41cfadf20ec6d1e149547d10b074d882a6cb79`
- Original author: Robert `<robert.raynor@gmail.com>`
- Source subject: `Prove exact UV product additivity`
- Accepted judgment ID:
  `71f4dc08876d2e6aeee3b569f30e2142fdaf845d0d5cd4df5ef69168d19cda80`
- Immutable judgment commit:
  `fdd2dc2137e1e0ca5dd38acd1fdc89f5c09f056f`
- Formed Yukon knowledge commit:
  `31c4c4ef5e72a1099863905267a681efe2d26a40`
- `FULL.md` Git blob: `06834d7020429bcae39e5f321787b6a4f191e381`
- `verify_uv_factorization.py` Git blob:
  `93efd576e1652ca77ee78a89db095f19d3759f55`

The judgment verdict was `ACCEPT`.  It specifically accepted the correlated
input chain-rule identity, both envelope inequalities, exact arbitrary-product
additivity, and the all-blocklength structural consequence, while excluding
the complete UV region, branchwise minimum, and the GK/Theorem-9 systems.

### Branchwise functional

- Original source commit: `7f51930dd39a89c0a0a4e78d8630f39da8e6c87f`
- Original author: Robert `<robert.raynor@gmail.com>`
- Source subject: `Prove branchwise UV additivity under skew symmetry`
- Accepted judgment ID:
  `d2251d88c98360c9b6db0a22daedc778c667bb66c2e70999cff67a1ec72909e7`
- Immutable judgment commit:
  `f7046f55f817c02f80d086b34b18fb5e1038e3c5`
- Formed Yukon knowledge commit:
  `ccee6b9529621884c014db5a81dc5c2f6a67c6f0`
- `FULL.md` Git blob: `e020e5c85c3e101baddda12fba5dd906b2a72ac9`

Its judgment verdict was also `ACCEPT`.  It accepted envelope covariance,
symmetrization, equality of the two scalar optima, closure of skew symmetry
under products, and the inherited all-blocklength BSSC result.

The three copied source files in `source-artifacts/` are byte-identical to
their original source-commit blobs.  Porting preserves the original
authorship; it is not a claim of new authorship for those results.

## Reproduction

From the repository root, run:

```text
python3 problems/bssc-sum-capacity/contributions/uv-product-branchwise-additivity/source-artifacts/upper-uv-additivity/verify_uv_factorization.py
python3 problems/bssc-sum-capacity/contributions/uv-product-branchwise-additivity/verify_uv_hostile_cases.py
```

The first command is the original dependency-free, deterministic Yukon audit.
It checks random strictly positive finite product channels, correlated input
laws, the coefficient-one and general-coefficient chain identities,
mutual-information subadditivity, product posterior mixtures, and the BSSC
contact value.  The second command independently adds deterministic channels,
zero-probability rows, perfectly correlated and degenerate inputs, exact BSSC
skew-matrix checks, and a 90-digit Decimal contact evaluation.

Byte identity can be checked with:

```text
git hash-object problems/bssc-sum-capacity/contributions/uv-product-branchwise-additivity/source-artifacts/upper-uv-additivity/FULL.md
git hash-object problems/bssc-sum-capacity/contributions/uv-product-branchwise-additivity/source-artifacts/upper-uv-additivity/verify_uv_factorization.py
git hash-object problems/bssc-sum-capacity/contributions/uv-product-branchwise-additivity/source-artifacts/frontier-uv-branchwise/FULL.md
```

The expected hashes, in order, are `06834d7020429bcae39e5f321787b6a4f191e381`,
`93efd576e1652ca77ee78a89db095f19d3759f55`, and
`e020e5c85c3e101baddda12fba5dd906b2a72ac9`.

## Limitations

- The scalar rows optimize their envelope auxiliaries separately.  The theorem
  does not establish tensorization of the complete UV rate region or a common
  joint-\((U,V)\) optimization.
- Branchwise equality is proved only under receiver-skew symmetry; no claim is
  made for nonsymmetric channels or other weighted scalarizations.
- Nothing here tensorizes the simplified GK functional or the full
  Gohari--Liu--Nair Theorem-9 system.
- The executable checks are corroboration.  The universal finite-alphabet
  theorem rests on the displayed analytic identities and concavity argument.
- The original averaged-functional artifact labels its sampled BSSC decimals
  as non-certified.  The exact BSSC specialization here instead uses the sharp
  posterior support already accepted and represented under canonical Math Flow
  transaction `c70e182...`.
- This contribution changes no capacity frontier and supplies no achievable
  coding improvement.

</artifact>
<artifact path="problems/bssc-sum-capacity/contributions/uv-product-branchwise-additivity/source-artifacts/frontier-uv-branchwise/FULL.md">
# Branchwise UV additivity for receiver-skew-symmetric channels

## Contribution

The current knowledge proves product additivity of the *average* of the two
separately relaxed UV sum-rate rows, but explicitly leaves open the stronger
scalar obtained by taking their pointwise minimum.  This note closes that
question for every finite-alphabet receiver-skew-symmetric broadcast channel.

For such channels the branchwise-minimum scalar equals the averaged scalar.
Together with the already established product-additivity theorem, this implies
exact additivity of the branchwise scalar for arbitrary finite products of
receiver-skew-symmetric channels.  In particular, for every blocklength `n`,
envelope auxiliaries that are joint across coordinates, and arbitrarily
correlated inputs, cannot improve the per-letter branchwise-relaxed UV
converse for the half-skew BSSC.

The argument is exact and uses only concavity, channel relabeling, and the
canonical averaged-functional product theorem.  There is no numerical search.

## Definitions and precise scope

Let `W : X -> (Y,Z)` be a finite-alphabet discrete memoryless broadcast
channel and let `p` be an input distribution.  Write

```text
IY(p) = I_p(X;Y),       IZ(p) = I_p(X;Z),
t(p)  = IY(p) - IZ(p).
```

For a real function `f` on the input simplex, define its upper concave
envelope by

```text
C[f](p) = sup sum_a alpha_a f(p_a),
```

where the supremum is over finite mixtures with `alpha_a >= 0`,
`sum_a alpha_a = 1`, and `sum_a alpha_a p_a = p`.  Define the two separately
relaxed UV rows

```text
A_W(p) = IY(p) + C[-t](p),
D_W(p) = IZ(p) + C[ t](p).
```

The two scalar functionals compared below are

```text
B_avg(W) = sup_p (A_W(p)+D_W(p))/2,
B_min(W) = sup_p min(A_W(p),D_W(p)).
```

`B_avg` is exactly the functional called `B_UV` in current canonical
knowledge.  `B_min` is the branchwise minimum of the same two separately
relaxed rows.  This note does **not** identify `B_min` with the complete UV
region or with an optimization retaining a common joint law for both UV
auxiliaries.

A channel is called receiver-skew-symmetric here if there are an input
permutation `s` with `s^2 = id` and bijections `phi : Y -> Z` and
`psi : Z -> Y` such that, for every input and output symbol,

```text
W_Y(y | s(x)) = W_Z(phi(y) | x),
W_Z(z | s(x)) = W_Y(psi(z) | x).
```

Thus the input relabeling exchanges the two receiver channels up to bijective
output relabeling.  Equivalently for this proof, if `S` is the induced affine
involution on input distributions, then for every `p`

```text
IY(S p) = IZ(p),        IZ(S p) = IY(p).
```

The channel-level relabeling condition implies these identities because
mutual information is invariant under bijective relabeling.  For the
half-skew BSSC, take `s(x)=1-x`, `phi(y)=1-y`, and `psi(z)=1-z`.  Its two
displayed channel matrices directly give

```text
P_Y(y | 1-x) = P_Z(1-y | x),
P_Z(z | 1-x) = P_Y(1-z | x),
```

so it has exactly the required symmetry.

## Why these are valid UV row relaxations

For completeness, let `U-X-(Y,Z)` and let `p_u` be the posterior input law
given `U=u`.  The first UV sum row can be written

```text
I(U;Y) + I(X;Z|U)
  = IY(p) + sum_u p(u) [IZ(p_u)-IY(p_u)]
  = IY(p) + sum_u p(u) [-t(p_u)]
  <= A_W(p).
```

The analogous row based on `V-X-(Y,Z)` is at most `D_W(p)`.  Hence taking the
minimum of these two separately relaxed rows gives the scalar `B_min(W)`.
This paragraph is only a derivation of the stated relaxation; no claim about
simultaneous attainment by a joint `(U,V)` is used.

## Envelope covariance under the skew involution

The mutual-information symmetry gives

```text
t(S p) = -t(p).
```

Every finite decomposition `p = sum_a alpha_a p_a` is carried bijectively by
`S` to the decomposition `S p = sum_a alpha_a S p_a`.  Therefore

```text
C[-t](S p)
  = sup_{sum alpha_a q_a = S p} sum_a alpha_a [-t(q_a)]
  = sup_{sum alpha_a p_a = p}   sum_a alpha_a [-t(S p_a)]
  = C[t](p).
```

The same calculation with the signs reversed gives
`C[t](S p)=C[-t](p)`.  Consequently the two relaxed rows are exchanged:

```text
A_W(S p) = D_W(p),      D_W(S p) = A_W(p).       (1)
```

## Equality of the branchwise and averaged scalars

Both `A_W` and `D_W` are concave functions of `p`.  Indeed, mutual information
is concave in the input law for a fixed channel, each upper concave envelope
is concave by its definition, and sums of concave functions are concave.

Fix any input law `p` and symmetrize it:

```text
p_bar = (p + S p)/2.
```

Then `S p_bar = p_bar`.  Concavity and (1) give

```text
A_W(p_bar)
  >= [A_W(p)+A_W(S p)]/2
   = [A_W(p)+D_W(p)]/2,

D_W(p_bar)
  >= [D_W(p)+D_W(S p)]/2
   = [D_W(p)+A_W(p)]/2.
```

Thus

```text
min(A_W(p_bar),D_W(p_bar))
  >= [A_W(p)+D_W(p)]/2.                         (2)
```

Taking suprema in (2) proves `B_min(W) >= B_avg(W)`.  The reverse inequality
is pointwise, since `min(a,d) <= (a+d)/2`.  Therefore

```text
B_min(W) = B_avg(W)                              (3)
```

for every finite-alphabet receiver-skew-symmetric broadcast channel.  The
proof also shows that the supremum may be restricted to `S`-invariant input
laws.  No binary-input assumption is involved.

## Exact product additivity

Let `W_1,...,W_n` be finite-alphabet receiver-skew-symmetric broadcast
channels, not necessarily identical.  The coordinatewise input involution and
coordinatewise output relabelings exchange the two vector receiver channels,
so the product channel is again receiver-skew-symmetric.  Applying (3) to the
product and to each factor, and using the product-additivity theorem for
`B_avg` already established in canonical knowledge, yields

```text
B_min(W_1 x ... x W_n)
  = B_avg(W_1 x ... x W_n)
  = sum_i B_avg(W_i)
  = sum_i B_min(W_i).                            (4)
```

The middle equality remains valid when the product-channel input is
arbitrarily correlated and the envelope auxiliary is joint across factors;
those are part of the scope of the canonical averaged-functional theorem.
Equation (4) therefore inherits that full scope rather than assuming product
inputs or product auxiliaries.

For the half-skew BSSC `P`, current canonical knowledge identifies the
one-letter classical UV value as

```text
B_min(P) = B_avg(P)
         = 2 h2(1/4) - 5/4
         = 0.3725562489182657... bits/use.
```

Hence, for every `n >= 1`,

```text
B_min(P^{x n}) = n [2 h2(1/4)-5/4].              (5)
```

Blocking, correlated super-symbol priors, and envelope auxiliaries joint
across coordinates do not strengthen this branchwise-relaxed UV sum converse
per channel use.

## Validation and dependency audit

The new argument has three independently checkable components:

1. skew relabeling maps `t` to `-t` and bijects all posterior mixtures, giving
   the two envelope covariance identities;
2. concavity applied to `(p+S p)/2` proves both inequalities in (2), while the
   elementary pointwise minimum-versus-average inequality proves the reverse
   comparison; and
3. receiver-skew symmetry is closed under finite products, after which the
   already accepted exact additivity of `B_avg` gives (4).

The only imported research theorem is the canonical product additivity of
`B_avg`; its accepted proof covers arbitrary finite alphabets, correlated
product inputs, and joint envelope auxiliaries.  The BSSC numerical value in
(5) is likewise already canonical.  The new equality (3) and its branchwise
product consequence require no floating-point or computer-assisted step.

## Novelty, effect, and limitations

Canonical knowledge explicitly lists tensorization of the branchwise minimum
as open and excludes it from the scope of the averaged theorem.  Equality (3)
supplies the missing bridge for the full receiver-skew-symmetric class and
therefore upgrades the all-blocklength BSSC conclusion from the averaged
scalar to the pointwise minimum of the two relaxed UV rows.

This does not improve the numerical BSSC upper bound: the value remains the
classical UV value, which is weaker than the certified full-Theorem-9 bound.
It closes one multiletter UV route by showing that retaining the branchwise
minimum cannot improve the BSSC converse through blocking.

No claim is made about nonsymmetric channels, the complete UV rate region,
other weighted UV scalarizations, a joint `(U,V)` optimization, simplified
equation (16), the GK auxiliary-receiver construction, or full Theorem 9.

</artifact>
<artifact path="problems/bssc-sum-capacity/contributions/uv-product-branchwise-additivity/source-artifacts/upper-uv-additivity/FULL.md">
# Exact product additivity of the symmetric UV sum-rate functional

## Contribution and exact scope

This submission proves an analytic tensorization theorem for a standard scalar
consequence of the classical UV outer bound.  For every pair of finite-alphabet
discrete memoryless broadcast channels (DMBCs), the symmetric sum-rate
functional

\[
 B_{\rm UV}(W)=\max_{p_X}\frac12\bigl(
 I(X;Y)+I(X;Z)+\mathfrak C[t_W](p_X)
                 +\mathfrak C[-t_W](p_X)\bigr),
 \qquad
 t_W(p_X)=I(X;Y)-I(X;Z),                                      \tag{1}
\]

is exactly additive:

\[
 B_{\rm UV}(W_1\times W_2)=B_{\rm UV}(W_1)+B_{\rm UV}(W_2).   \tag{2}
\]

Here \(\mathfrak C\) is the upper concave envelope over the input
simplex, all mutual informations are evaluated using the displayed input
law and the relevant channel, and the maximum is over all input laws.  The
inputs of the two factors may be arbitrarily correlated when the left side of
(2) is optimized.  The two factor channels need not be identical, symmetric,
binary-input, or BSSCs.  No assumption is made about the correlation of
\(Y_i\) and \(Z_i\) within one factor.

The functional in (1) is the equally weighted, or symmetric, scalar UV
sum-rate relaxation (the quantity often written in the upper-concave-envelope
form used for the BSSC).  The theorem is deliberately **not** a claim that the
whole UV outer region, or every scalarization of it, is additive.

For the half-skew BSSC \(P\), (2) implies for every \(n\geq 1\)

\[
 \frac1n B_{\rm UV}(P^{\times n})=B_{\rm UV}(P).               \tag{3}
\]

Thus grouping channel uses, allowing each envelope auxiliary to depend jointly
on all coordinates of the super-symbol, and allowing arbitrary correlated
super-symbol inputs cannot improve this particular per-letter BSSC converse.

## Definitions and why (1) is an outer bound

For a continuous real function \(f\) on the finite input simplex, use the
following operational definition of its upper concave envelope:

\[
 \mathfrak C[f](p)
 =\sup_{\substack{A-X-(Y,Z)\\P_X=p}}
       \sum_a P_A(a) f(P_{X|A=a}).                             \tag{4}
\]

Equivalently, the supremum is over all finite convex decompositions
\(p=\sum_a\alpha_a p_a\).  Standard finite-dimensional support reduction
makes the supremum a maximum, but the proof below only needs the supremum
form.  Formula (4) also makes clear that \(\mathfrak C[f]\) is concave and
majorizes \(f\).

For completeness, the private-message UV outer bound implies, under one
induced input law \(p_X\), both relaxed sum-rate inequalities

\[
 \begin{aligned}
 R_1+R_2&\leq I(U;Y)+I(X;Z|U),\\
 R_1+R_2&\leq I(V;Z)+I(X;Y|V),
 \end{aligned}                                                \tag{5}
\]

with \(U-X-(Y,Z)\) and \(V-X-(Y,Z)\).  Put
\(t(p)=I_p(X;Y)-I_p(X;Z)\).  For any such \(U\), the Markov chain and the
chain rule give

\[
 \begin{aligned}
 I(U;Y)+I(X;Z|U)
 &= I_p(X;Z)+I(U;Y)-I(U;Z)\\
 &= I_p(X;Y)-\sum_u P(u)t(P_{X|u})\\
 &\leq I_p(X;Y)+\mathfrak C[-t](p).                            \tag{6}
 \end{aligned}
\]

Likewise,

\[
 I(V;Z)+I(X;Y|V)
 =I_p(X;Z)+\sum_v P(v)t(P_{X|v})
 \leq I_p(X;Z)+\mathfrak C[t](p).                             \tag{7}
\]

Both right sides bound the same achievable sum rate.  Their arithmetic mean
does too, and maximizing that mean over \(p\) is exactly (1).  This paragraph
only records the standard validity of the scalar functional; the new program
contribution is its exact product factorization.

## The factorization lemma

Let

\[
 W_1(y_1,z_1|x_1)W_2(y_2,z_2|x_2)                            \tag{8}
\]

be a product DMBC.  Write \(t_i(p_i)=I(X_i;Y_i)-I(X_i;Z_i)\),
and define \(t_{12}\) in the same way for input \((X_1,X_2)\) and outputs
\((Y_1,Y_2)\), \((Z_1,Z_2)\).  If \(p_{12}\) is any, possibly correlated,
input law and \(p_1,p_2\) are its marginals, then

\[
 \begin{aligned}
 \mathfrak C[t_{12}](p_{12})
   &\leq \mathfrak C[t_1](p_1)+\mathfrak C[t_2](p_2),\\
 \mathfrak C[-t_{12}](p_{12})
   &\leq \mathfrak C[-t_1](p_1)+\mathfrak C[-t_2](p_2).       \tag{9}
 \end{aligned}
\]

The first inequality is the \(\lambda=1\) case of the usual
chain-rule factorization for the concave envelope of
\(I(X;Y)-\lambda I(X;Z)\).  The full cancellation at \(\lambda=1\) is
proved next rather than assumed.

### Exact chain-rule identity for correlated inputs

Fix an arbitrary finite \(A\) such that

\[
 A-(X_1,X_2)-(Y_1,Z_1,Y_2,Z_2)                               \tag{10}
\]

under (8), with marginal input law \(p_{12}\).  Conditional on \(A=a\),
the input coordinates may still be correlated.  Chain the two receiver-1
outputs in forward factor order, and the two receiver-2 outputs in reverse
factor order.  Product memorylessness gives

\[
 \begin{aligned}
 I(X_1X_2;Y_1Y_2|A)
   &=I(X_1;Y_1|A)+I(X_2;Y_2|A,Y_1),\\
 I(X_1X_2;Z_1Z_2|A)
   &=I(X_2;Z_2|A)+I(X_1;Z_1|A,Z_2).                           \tag{11}
 \end{aligned}
\]

For example, the first line uses
\(I(X_2;Y_1|X_1,A)=0\) and
\(I(X_1;Y_2|X_2,A,Y_1)=0\).  These conditional independences follow from
the factorization in (8), not from independence of \(X_1\) and \(X_2\).

The only apparent mismatch in (11) is resolved by two explicit
co-information identities.  The elementary identity

\[
 I(B;C|D)-I(B;C|D,E)
 =I(C;E|D)-I(C;E|B,D)                                        \tag{12}
\]

gives

\[
 \begin{aligned}
 &I(X_1;Y_1|A)-I(X_1;Y_1|A,Z_2)\\
 &\qquad=I(Y_1;Z_2|A)-I(Y_1;Z_2|X_1,A)
          =I(Y_1;Z_2|A),                                     \tag{13}\\
 &I(X_2;Z_2|A)-I(X_2;Z_2|A,Y_1)\\
 &\qquad=I(Z_2;Y_1|A)-I(Z_2;Y_1|X_2,A)
          =I(Y_1;Z_2|A).                                     \tag{14}
 \end{aligned}
\]

The last terms vanish because the two channel factors are independent:
\(Y_1\perp Z_2\mid(X_1,A)\) and
\(Z_2\perp Y_1\mid(X_2,A)\).  Again, those statements remain true for an
arbitrary correlated law of \((A,X_1,X_2)\): after fixing \(X_1\), the law
of \(Y_1\) no longer depends on \((A,X_2,Z_2)\), and symmetrically after
fixing \(X_2\).

Equations (13) and (14) have identical right sides.  Substitution into (11)
therefore proves the exact \(\lambda=1\) identity

\[
 \begin{aligned}
 &I(X_1X_2;Y_1Y_2|A)-I(X_1X_2;Z_1Z_2|A)\\
 &=\bigl[I(X_1;Y_1|A,Z_2)-I(X_1;Z_1|A,Z_2)\bigr]\\
 &\quad+\bigl[I(X_2;Y_2|A,Y_1)-I(X_2;Z_2|A,Y_1)\bigr].        \tag{15}
 \end{aligned}
\]

To locate precisely why \(\lambda=1\) matters, repeat the same algebra with
the receiver-2 terms multiplied by \(\lambda\).  It yields

\[
 \begin{aligned}
 &I(X_1X_2;Y_1Y_2|A)-\lambda I(X_1X_2;Z_1Z_2|A)\\
 &=\bigl[I(X_1;Y_1|A,Z_2)-\lambda I(X_1;Z_1|A,Z_2)\bigr]\\
 &\quad+\bigl[I(X_2;Y_2|A,Y_1)-\lambda I(X_2;Z_2|A,Y_1)\bigr]\\
 &\quad-(\lambda-1)I(Y_1;Z_2|A).                              \tag{16}
 \end{aligned}
\]

For \(\lambda\geq1\) the last term is nonpositive; at \(\lambda=1\) it
vanishes exactly.  Thus (15), including its cross-term cancellation, is valid
without any independence assumption on the input coordinates.

### Passage from the identity to the envelopes

The left side of (15) is

\[
 \sum_a P(a)t_{12}(P_{X_1X_2|a}).                             \tag{17}
\]

Moreover,

\[
 (A,Z_2)-X_1-(Y_1,Z_1),\qquad
 (A,Y_1)-X_2-(Y_2,Z_2),                                      \tag{18}
\]

again by (8).  Consequently the first bracket in (15) equals
\(\sum_{a,z_2}P(a,z_2)t_1(P_{X_1|a,z_2})\).  For each fixed
\(z_2\), definition (4), followed by concavity of the envelope, gives

\[
 \begin{aligned}
 \sum_{a,z_2}P(a,z_2)t_1(P_{X_1|a,z_2})
 &\leq \sum_{z_2}P(z_2)\mathfrak C[t_1](P_{X_1|z_2})\\
 &\leq \mathfrak C[t_1]\!\left(
       \sum_{z_2}P(z_2)P_{X_1|z_2}\right)\\
 &=\mathfrak C[t_1](p_1).                                    \tag{19}
 \end{aligned}
\]

The identical argument, first conditioning on \(Y_1\), bounds the second
bracket by \(\mathfrak C[t_2](p_2)\).  Hence every auxiliary \(A\) in (4)
satisfies

\[
 \sum_aP(a)t_{12}(P_{X_1X_2|a})
 \leq\mathfrak C[t_1](p_1)+\mathfrak C[t_2](p_2).             \tag{20}
\]

Taking the supremum over \(A\) proves the first line of (9).  Swapping
\(Y_i\) and \(Z_i\) in the entire argument changes every \(t_i\) to
\(-t_i\) and proves the second line.  This completes the factorization
lemma.

## Proof of exact additivity

For an arbitrary correlated product-channel input \(p_{12}\), product
memorylessness and entropy subadditivity imply

\[
 \begin{aligned}
 I(X_1X_2;Y_1Y_2)
 &=H(Y_1Y_2)-H(Y_1Y_2|X_1X_2)\\
 &\leq H(Y_1)+H(Y_2)-H(Y_1|X_1)-H(Y_2|X_2)\\
 &=I(X_1;Y_1)+I(X_2;Y_2),                                    \tag{21}
 \end{aligned}
\]

and likewise
\(I(X_1X_2;Z_1Z_2)\leq I(X_1;Z_1)+I(X_2;Z_2)\).
Combining these inequalities with (9) in (1) gives the pointwise bound

\[
 F_{12}(p_{12})\leq F_1(p_1)+F_2(p_2),                       \tag{22}
\]

where \(F\) denotes the expression inside the maximization in (1).  Therefore

\[
 B_{\rm UV}(W_1\times W_2)
 \leq B_{\rm UV}(W_1)+B_{\rm UV}(W_2).                       \tag{23}
\]

For the reverse direction, take any factor priors \(p_1,p_2\) and their
product \(p_1\times p_2\).  If
\(p_1=\sum_a\alpha_a p_{1a}\) and
\(p_2=\sum_b\beta_b p_{2b}\), then

\[
 p_1\times p_2=\sum_{a,b}\alpha_a\beta_b
                       (p_{1a}\times p_{2b}),                 \tag{24}
\]

and product inputs make mutual information additive, so

\[
 t_{12}(p_{1a}\times p_{2b})=t_1(p_{1a})+t_2(p_{2b}).         \tag{25}
\]

Using product decompositions in (4) and taking suprema shows

\[
 \mathfrak C[t_{12}](p_1\times p_2)
 \geq\mathfrak C[t_1](p_1)+\mathfrak C[t_2](p_2).             \tag{26}
\]

The same holds for \(-t\).  Inequality (9) makes both relations equalities
at product priors.  The two un-enveloped mutual informations are also
additive there, and hence

\[
 F_{12}(p_1\times p_2)=F_1(p_1)+F_2(p_2).                    \tag{27}
\]

Taking maximizing priors (or maximizing sequences) gives the reverse of
(23), proving (2).

## Blocking consequence and the BSSC

Induction in (2) gives, for arbitrary finite-alphabet factors,

\[
 B_{\rm UV}\!\left(\mathop{\times}_{i=1}^n W_i\right)
 =\sum_{i=1}^n B_{\rm UV}(W_i).                               \tag{28}
\]

For one fixed DMBC \(W\), a length-\(m\) code for the super-symbol channel
\(W^{\times n}\) is exactly a length-\(mn\) code for \(W\), with rates per
super-symbol scaled by \(n\).  Conversely, ordinary codes can be padded to
blocklengths divisible by fixed \(n\) with asymptotically negligible rate
loss.  Thus the private-message capacity regions, with their respective
per-use units, satisfy

\[
 \mathcal C(W^{\times n})=n\mathcal C(W),\qquad
 C_{\rm sum}(W^{\times n})=nC_{\rm sum}(W).                   \tag{29}
\]

Applying (1) to the super-symbol channel and dividing by \(n\) consequently
returns exactly the one-letter functional:

\[
 C_{\rm sum}(W)
 =\frac1nC_{\rm sum}(W^{\times n})
 \leq\frac1nB_{\rm UV}(W^{\times n})
 =B_{\rm UV}(W).                                              \tag{30}
\]

In particular this applies to the half-skew BSSC with receiver marginals

\[
 W_Y=\begin{pmatrix}1/2&1/2\\0&1\end{pmatrix},\qquad
 W_Z=\begin{pmatrix}1&0\\1/2&1/2\end{pmatrix}.               \tag{31}
\]

The earlier attempt's sampled one-letter evaluation was approximately
\(0.3725562489182657\) bits/use, and its enriched two-letter sampled value was
approximately \(0.7451124978365314\) bits/super-symbol.  Those decimals are
useful numerical checks of (2), not ingredients in the proof and not claimed
here as interval-certified evaluations.  The rigorous BSSC conclusion is the
symbolic equality (3), which does not depend on either decimal.

## Executable corroboration

The accompanying `verify_uv_factorization.py` is a small dependency-free
audit of the fragile algebraic steps.  On deterministic pseudorandom finite
product channels and arbitrary correlated laws \(P_{A,X_1,X_2}\), it checks:

1. both product-channel conditional independences used in (13)--(14);
2. the exact \(\lambda=1\) equality (15) and the residual formula (16) for
   several \(\lambda\)'s;
3. the mutual-information subadditivity inequalities in (21);
4. the product-mixture identities (24)--(25); and
5. the BSSC candidate-contact mixture numerical witness reported above.

It is run with

```text
python3 submission/verify_uv_factorization.py
```

and fails by assertion if a check exceeds its stated floating-point tolerance.
This code is corroboration only.  The exact theorem rests on the displayed
finite-alphabet identities, not on randomized testing or a discretized
optimization.

## Separation from the two-letter GK search

Attempt 007 also performed a floating-point, grid-restricted search of the
simplified two-auxiliary GK equation-(16) functional.  With product
auxiliaries it found about \(0.7385943932915563\) per two-letter super-symbol;
the best joint-auxiliary sample found about \(0.7385943932915559\).  That
difference is at roundoff scale.  These values provide **no theorem**:

- sampled upper concave envelopes and a sampled input maximization are not a
  continuous global certificate;
- the search has no proved auxiliary-cardinality bound or global optimality
  guarantee;
- the search evaluated only the simplified equation-(16) objective, not the
  full Theorem-9 product-channel constraint system; and
- the nested GK envelopes do not obey the factorization argument above.

Accordingly, this submission makes no claim of GK additivity, no claim that
two-letter GK cannot improve, and no claim about additivity of the full
two-auxiliary-receiver region.  The existing input-only marginalization result
for auxiliary receivers does not fill the missing global-optimization or
factorization steps.  Those remain open.

## Novelty, effect, and limitations

The chain-rule method behind (16) is classical; no claim of priority for that
general technique is made.  The useful new item relative to the current BSSC
knowledge record is a complete, directly checkable theorem for the exact
functional actually used in the BSSC UV comparison, including arbitrary
correlated product inputs, the previously implicit \(\lambda=1\) cancellation,
and the all-blocklength blocking consequence.  It closes the UV product-channel
route as a source of a stronger per-letter BSSC bound.

The result does not improve the numerical BSSC capacity upper bound.  It does
not prove a capacity formula, an achievable rate, a full-region tensorization,
additivity of the branchwise minimum of separately relaxed UV constraints, or
any GK/J/full-Theorem-9 tensorization.  Potential multiletter improvements must
therefore retain structure absent from the symmetric functional (1), such as
the coupling between different UV branches or the richer nested auxiliary
constraints.

</artifact>
<artifact path="problems/bssc-sum-capacity/contributions/uv-product-branchwise-additivity/source-artifacts/upper-uv-additivity/verify_uv_factorization.py">
#!/usr/bin/env python3
"""Numerical audit of the exact UV product-factorization identities.

This is corroboration, not a proof.  It uses only the Python standard library.
"""

from __future__ import annotations

from collections import defaultdict
import math
import random


TOL = 2.0e-11


def normalized(values):
    total = sum(values)
    return [value / total for value in values]


def random_factor_channel(rng):
    """Return W[x][y][z] for binary X,Y,Z, with strictly positive rows."""
    channel = []
    for _x in range(2):
        row = normalized([rng.random() + 0.1 for _ in range(4)])
        channel.append([[row[2 * y + z] for z in range(2)] for y in range(2)])
    return channel


def product_joint(p_ax, w1, w2):
    """Law of (A,X1,X2,Y1,Z1,Y2,Z2)."""
    joint = {}
    for (a, x1, x2), pin in p_ax.items():
        for y1 in range(2):
            for z1 in range(2):
                for y2 in range(2):
                    for z2 in range(2):
                        joint[(a, x1, x2, y1, z1, y2, z2)] = (
                            pin * w1[x1][y1][z1] * w2[x2][y2][z2]
                        )
    return joint


def project(key, indices):
    return tuple(key[index] for index in indices)


def conditional_mi(joint, left, right, given=()):
    """I(key[left]; key[right] | key[given]) in bits."""
    abc = defaultdict(float)
    ac = defaultdict(float)
    bc = defaultdict(float)
    c = defaultdict(float)
    for key, probability in joint.items():
        a_value = project(key, left)
        b_value = project(key, right)
        c_value = project(key, given)
        abc[(a_value, b_value, c_value)] += probability
        ac[(a_value, c_value)] += probability
        bc[(b_value, c_value)] += probability
        c[c_value] += probability
    result = 0.0
    for (a_value, b_value, c_value), probability in abc.items():
        if probability:
            ratio = probability * c[c_value] / (
                ac[(a_value, c_value)] * bc[(b_value, c_value)]
            )
            result += probability * math.log2(ratio)
    return result


def random_input_auxiliary(rng):
    values = normalized([rng.random() + 0.05 for _ in range(8)])
    return {
        (a, x1, x2): values[4 * a + 2 * x1 + x2]
        for a in range(2)
        for x1 in range(2)
        for x2 in range(2)
    }


def audit_chain_identities(seed, trials=100):
    rng = random.Random(seed)
    worst_markov = 0.0
    worst_identity = 0.0
    worst_lambda = 0.0
    worst_subadd_slack = float("inf")

    # Coordinate indices in product_joint's keys.
    a, x1, x2, y1, z1, y2, z2 = range(7)

    for _ in range(trials):
        w1 = random_factor_channel(rng)
        w2 = random_factor_channel(rng)
        joint = product_joint(random_input_auxiliary(rng), w1, w2)

        cross_1 = conditional_mi(joint, (y1,), (z2,), (x1, a))
        cross_2 = conditional_mi(joint, (z2,), (y1,), (x2, a))
        worst_markov = max(worst_markov, abs(cross_1), abs(cross_2))

        iy12 = conditional_mi(joint, (x1, x2), (y1, y2), (a,))
        iz12 = conditional_mi(joint, (x1, x2), (z1, z2), (a,))
        iy1 = conditional_mi(joint, (x1,), (y1,), (a, z2))
        iz1 = conditional_mi(joint, (x1,), (z1,), (a, z2))
        iy2 = conditional_mi(joint, (x2,), (y2,), (a, y1))
        iz2 = conditional_mi(joint, (x2,), (z2,), (a, y1))
        cross = conditional_mi(joint, (y1,), (z2,), (a,))

        error = (iy12 - iz12) - ((iy1 - iz1) + (iy2 - iz2))
        worst_identity = max(worst_identity, abs(error))

        for lam in (1.0, 1.7, 3.0):
            expected = (iy1 - lam * iz1) + (iy2 - lam * iz2)
            expected -= (lam - 1.0) * cross
            error_lam = (iy12 - lam * iz12) - expected
            worst_lambda = max(worst_lambda, abs(error_lam))

        iy12_plain = conditional_mi(joint, (x1, x2), (y1, y2))
        iy_sum = conditional_mi(joint, (x1,), (y1,))
        iy_sum += conditional_mi(joint, (x2,), (y2,))
        iz12_plain = conditional_mi(joint, (x1, x2), (z1, z2))
        iz_sum = conditional_mi(joint, (x1,), (z1,))
        iz_sum += conditional_mi(joint, (x2,), (z2,))
        worst_subadd_slack = min(
            worst_subadd_slack, iy_sum - iy12_plain, iz_sum - iz12_plain
        )

    assert worst_markov < TOL, worst_markov
    assert worst_identity < TOL, worst_identity
    assert worst_lambda < TOL, worst_lambda
    assert worst_subadd_slack > -TOL, worst_subadd_slack
    return worst_markov, worst_identity, worst_lambda, worst_subadd_slack


def channel_input_joint(prior, channel):
    return {
        (x, y, z): prior[x] * channel[x][y][z]
        for x in range(2)
        for y in range(2)
        for z in range(2)
    }


def t_factor(prior, channel):
    joint = channel_input_joint(prior, channel)
    return conditional_mi(joint, (0,), (1,)) - conditional_mi(joint, (0,), (2,))


def t_product(prior, w1, w2):
    # Reuse product_joint with a constant auxiliary.
    p_ax = {
        (0, x1, x2): prior[2 * x1 + x2]
        for x1 in range(2)
        for x2 in range(2)
    }
    joint = product_joint(p_ax, w1, w2)
    return conditional_mi(joint, (1, 2), (3, 5)) - conditional_mi(
        joint, (1, 2), (4, 6)
    )


def audit_product_mixtures(seed):
    rng = random.Random(seed)
    w1 = random_factor_channel(rng)
    w2 = random_factor_channel(rng)
    alpha = normalized([rng.random() + 0.1 for _ in range(3)])
    beta = normalized([rng.random() + 0.1 for _ in range(4)])
    post1 = [[1.0 - q, q] for q in [rng.random() for _ in alpha]]
    post2 = [[1.0 - q, q] for q in [rng.random() for _ in beta]]
    p1 = [sum(alpha[i] * post1[i][x] for i in range(3)) for x in range(2)]
    p2 = [sum(beta[j] * post2[j][x] for j in range(4)) for x in range(2)]

    barycenter = [0.0] * 4
    product_average = 0.0
    for i in range(3):
        for j in range(4):
            weight = alpha[i] * beta[j]
            prior = [
                post1[i][x1] * post2[j][x2]
                for x1 in range(2)
                for x2 in range(2)
            ]
            for x in range(4):
                barycenter[x] += weight * prior[x]
            product_average += weight * t_product(prior, w1, w2)

    target_barycenter = [p1[x1] * p2[x2] for x1 in range(2) for x2 in range(2)]
    factor_average = sum(
        alpha[i] * t_factor(post1[i], w1) for i in range(3)
    ) + sum(beta[j] * t_factor(post2[j], w2) for j in range(4))
    barycenter_error = max(
        abs(left - right) for left, right in zip(barycenter, target_barycenter)
    )
    value_error = abs(product_average - factor_average)
    assert barycenter_error < TOL, barycenter_error
    assert value_error < TOL, value_error
    return barycenter_error, value_error


def binary_entropy(q):
    if q == 0.0 or q == 1.0:
        return 0.0
    return -q * math.log2(q) - (1.0 - q) * math.log2(1.0 - q)


def bssc_t(q):
    iy = binary_entropy((1.0 - q) / 2.0) - (1.0 - q)
    iz = binary_entropy(q / 2.0) - q
    return iy - iz


def bssc_candidate_contact_witness():
    # At p=1/2, mix q=0 and q=4/5 for C[t], and q=1/5 and q=1 for C[-t].
    receiver_mi = binary_entropy(0.25) - 0.5
    envelope_witness = (5.0 / 8.0) * bssc_t(0.8)
    witness = receiver_mi + envelope_witness
    expected = 0.3725562489182657
    assert abs(witness - expected) < 2.0e-15, witness
    return witness, 2.0 * witness


def main():
    markov, identity, lambda_error, slack = audit_chain_identities(20260803)
    barycenter, product_value = audit_product_mixtures(20260804)
    one, two = bssc_candidate_contact_witness()
    print(f"max conditional-Markov residual: {markov:.3e}")
    print(f"max lambda=1 identity residual:  {identity:.3e}")
    print(f"max general-lambda residual:     {lambda_error:.3e}")
    print(f"minimum MI subadditivity slack:  {slack:.3e}")
    print(f"product-mixture barycenter error:{barycenter:.3e}")
    print(f"product-mixture value error:     {product_value:.3e}")
    print(f"BSSC candidate-contact witness: {one:.16f}; doubled: {two:.16f}")
    print("PASS")


if __name__ == "__main__":
    main()

</artifact>
<artifact path="problems/bssc-sum-capacity/contributions/uv-product-branchwise-additivity/verify_uv_hostile_cases.py">
#!/usr/bin/env python3
"""Independent hostile-case audit for the ported UV identities.

This is corroboration of the analytic proof, not a finite-alphabet proof by
testing.  It deliberately includes zero-probability and deterministic channel
rows that are absent from the source randomized audit.
"""

from __future__ import annotations

from decimal import Decimal, getcontext
from fractions import Fraction
import runpy
from pathlib import Path
import sys


TOL = 3.0e-11


def load_source_audit():
    sys.dont_write_bytecode = True
    source = (
        Path(__file__).parent
        / "source-artifacts"
        / "upper-uv-additivity"
        / "verify_uv_factorization.py"
    )
    return runpy.run_path(str(source), run_name="uv_source_audit")


def hostile_channels():
    constant = [
        [[1.0, 0.0], [0.0, 0.0]],
        [[1.0, 0.0], [0.0, 0.0]],
    ]
    identity_antidentity = [
        [[0.0, 1.0], [0.0, 0.0]],
        [[0.0, 0.0], [1.0, 0.0]],
    ]
    bssc_common_noise = [
        [[0.5, 0.0], [0.5, 0.0]],
        [[0.0, 0.0], [0.5, 0.5]],
    ]
    return [constant, identity_antidentity, bssc_common_noise]


def hostile_inputs():
    laws = []
    laws.append({(0, 0, 0): 0.5, (0, 1, 1): 0.5})
    laws.append(
        {
            (x1 ^ x2, x1, x2): 0.25
            for x1 in range(2)
            for x2 in range(2)
        }
    )
    laws.append({(1, 1, 0): 1.0})
    laws.append(
        {
            (x1, x1, x2): probability
            for (x1, x2), probability in {
                (0, 0): 0.1,
                (0, 1): 0.2,
                (1, 0): 0.3,
                (1, 1): 0.4,
            }.items()
        }
    )
    return laws


def audit_hostile_chain_identities(api):
    cmi = api["conditional_mi"]
    product_joint = api["product_joint"]
    worst = Decimal(0)
    minimum_slack = float("inf")
    a, x1, x2, y1, z1, y2, z2 = range(7)

    count = 0
    for w1 in hostile_channels():
        for w2 in hostile_channels():
            for p_ax in hostile_inputs():
                count += 1
                joint = product_joint(p_ax, w1, w2)
                cross_1 = cmi(joint, (y1,), (z2,), (x1, a))
                cross_2 = cmi(joint, (z2,), (y1,), (x2, a))
                iy12 = cmi(joint, (x1, x2), (y1, y2), (a,))
                iz12 = cmi(joint, (x1, x2), (z1, z2), (a,))
                iy1 = cmi(joint, (x1,), (y1,), (a, z2))
                iz1 = cmi(joint, (x1,), (z1,), (a, z2))
                iy2 = cmi(joint, (x2,), (y2,), (a, y1))
                iz2 = cmi(joint, (x2,), (z2,), (a, y1))
                cross = cmi(joint, (y1,), (z2,), (a,))

                residuals = [cross_1, cross_2]
                residuals.append((iy12 - iz12) - (iy1 - iz1 + iy2 - iz2))
                for lam in (0.0, 1.0, 1.7, 3.0):
                    rhs = iy1 - lam * iz1 + iy2 - lam * iz2
                    rhs -= (lam - 1.0) * cross
                    residuals.append(iy12 - lam * iz12 - rhs)
                for residual in residuals:
                    worst = max(worst, Decimal(str(abs(residual))))

                iy_plain = cmi(joint, (x1, x2), (y1, y2))
                iy_parts = cmi(joint, (x1,), (y1,)) + cmi(
                    joint, (x2,), (y2,)
                )
                iz_plain = cmi(joint, (x1, x2), (z1, z2))
                iz_parts = cmi(joint, (x1,), (z1,)) + cmi(
                    joint, (x2,), (z2,)
                )
                minimum_slack = min(
                    minimum_slack, iy_parts - iy_plain, iz_parts - iz_plain
                )

    assert worst < Decimal(str(TOL)), worst
    assert minimum_slack > -TOL, minimum_slack
    return count, worst, minimum_slack


def h2(q: Decimal) -> Decimal:
    if q == 0 or q == 1:
        return Decimal(0)
    one = Decimal(1)
    return -(q * q.ln() + (one - q) * (one - q).ln()) / Decimal(2).ln()


def bssc_t(q: Decimal) -> Decimal:
    one = Decimal(1)
    iy = h2((one - q) / 2) - (one - q)
    iz = h2(q / 2) - q
    return iy - iz


def audit_bssc_specialization():
    getcontext().prec = 90
    one = Decimal(1)
    h = h2(one / 4)
    c = h - one / 2
    r = h - Decimal(3) / 4
    q = Decimal(4) / 5

    # Exact proof inputs: the canonical sharp support gives t(q) <= 2 r q.
    # The source contact mixture saturates that support at q=4/5 and has
    # barycenter 1/2 after adding mass 3/8 at q=0.
    contact_residual = bssc_t(q) - Decimal(8) * r / 5
    barycenter = Decimal(5) / 8 * q + Decimal(3) / 8 * Decimal(0)
    envelope_contact = Decimal(5) / 8 * bssc_t(q)
    uv_value = c + r
    closed_form = 2 * h - Decimal(5) / 4

    assert abs(contact_residual) < Decimal("1e-80"), contact_residual
    assert barycenter == one / 2, barycenter
    assert abs(envelope_contact - r) < Decimal("1e-80")
    assert abs(uv_value - closed_form) < Decimal("1e-88")

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

    return contact_residual, uv_value


def main():
    api = load_source_audit()
    count, worst, slack = audit_hostile_chain_identities(api)
    contact, value = audit_bssc_specialization()
    print(f"hostile product laws checked: {count}")
    print(f"largest hostile identity residual: {worst:.3E}")
    print(f"minimum hostile MI-subadditivity slack: {slack:.3e}")
    print(f"BSSC contact residual (90-digit Decimal): {contact:.3E}")
    print(f"exact-form numerical value: {value}")
    print("PASS")


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
ordinal: 10
transaction_id: d2506be78c46f1799e9b54cfcb6eee17b984f0f1
contribution_id: fixed-pair-upper-bound-attested
author: Robert Raynor
<artifact path="problems/bssc-sum-capacity/contributions/fixed-pair-upper-bound-attested/README.md">
# Attested fixed-pair BSSC upper certificate

## One claim and exact scope

For the half-skew BSSC in the problem statement, fix the binary-input,
binary-output auxiliary receivers whose output-zero probabilities are

\[
\begin{aligned}
P(G=0\mid X=0)&=0.206961624915382,&
P(G=0\mid X=1)&=0.826953249115544,\\
P(K=0\mid X=0)&=0.173046750884456,&
P(K=0\mid X=1)&=0.793038375084618.
\end{aligned}
\]

Every displayed decimal is treated as an exact rational. The single claim in
[claims.json](claims.json) assumes the cited Gohari--Liu--Nair Theorem 9
outer-bound premise exactly as stated in the sole declared dependency.  Under
that premise, the dependency's private-message rows and the included
continuous weak-duality certificate prove

\[
\begin{aligned}
C_{\rm sum}\le U\in[&
0.36929694596920284244271335135600317726937686320586339865039784778686683932875798,\\
&
0.36929694596920284244271335135600317726937686320586339865039784778686683932875818].
\end{aligned}
\]

In particular,

\[
C_{\rm sum}\le 0.369296945969202842443.
\]

This is a certificate for one fixed pair of auxiliary receivers and one
nonnegative six-row dual combination. It does not assert that the receiver
pair or dual face is optimal, does not establish a matching achievable rate,
and does not determine the exact sum-capacity.

## Premise-bound theorem interface

Canonical transaction
e3c1036ca607539a5ebcddf3058e6014ac5c1cd9
is the sole logical dependency. It takes the exact cited Gohari--Liu--Nair
Theorem 9 outer-bound statement as an explicit premise, derives its
private-message 30-row specialization, and exposes the fixed-receiver
outer-bound value

\[
B(G,K)=\sup_{q\in[0,1]}V(q;G,K),
\qquad C_{\rm sum}\le \inf_{G,K}B(G,K).
\]

The six rows used here match that audited system exactly under the labels

    R1A(1)
    R2T(1)
    SR(1,C)
    SL(2,U)
    SR(2,U)
    F_Y_right_minus_left

in that order. Write \(W_g(A)=I(W_g;A)\),
\(U_g(A)=I(U_g;A\mid W_g)\), and analogously for \(V,UW,VW,X|UW,X|VW\).
The rows are

\[
\begin{aligned}
R_1\le{}&W_c(Z)+U_a(Y)+W_a(G)-W_b(G)+W_b(K)-W_c(K)
 +UW_b(G)-UW_a(G),\\
R_2\le{}&W_c(Z)+V_c(Z)+VW_b(K)-VW_c(K),\\
R_1+R_2\le{}&W_a(Y)+W_c(K)-W_b(K)+W_b(G)-W_a(G)
 +VW_a(G)-VW_b(G)\\
&+VW_b(K)-VW_c(K)+V_c(Z)+X|VW_a(Y),\\
R_1+R_2\le{}&W_a(Y)+U_a(Y)+V_c(Z)+UW_b(G)-UW_a(G)
 -V_c(K)+X|UW_b(K),\\
R_1+R_2\le{}&W_c(Z)+U_a(Y)+V_c(Z)+VW_b(K)-VW_c(K)
 -U_a(G)+X|VW_b(G),\\
0\le{}&U_a(Y)-U_a(G)-X|VW_a(Y)+X|VW_a(G).
\end{aligned}
\]

The final row is the right-minus-left form of the audited \(Y,G\) side
condition. The declared dependency supplies the complete source binding and
all other rows; this contribution needs only these six.

## Exact dual reduction

For a fixed binary-input receiver \(A\), let \(I_A(q)\) be its mutual
information at \(P(X=1)=q\). Posterior conditioning gives

\[
\begin{aligned}
I(W;A)&=I_A(q_0)-\mathbb E I_A(q_W),\\
I(U;A\mid W)&=\mathbb E I_A(q_W)-\mathbb E I_A(q_U),\\
I(U,W;A)&=I_A(q_0)-\mathbb E I_A(q_U),\\
I(X;A\mid U,W)&=\mathbb E I_A(q_U),
\end{aligned}
\]

with the analogous \(V\) identities. The posterior laws obey the common-mean
and martingale relations

\[
\mathbb E[q_U\mid q_W]=\mathbb E[q_V\mid q_W]=q_W,
\qquad \mathbb E q_W=q_0.
\]

Set

\[
\epsilon=0.000173428163029,\quad
c_1=(1-\epsilon)/2,\quad c'_1=(1+\epsilon)/2.
\]

The six nonnegative row weights, in the order above, are

\[
(\epsilon,\epsilon,\epsilon,\tfrac12-\tfrac\epsilon2,
\tfrac12-\tfrac{3\epsilon}2,\epsilon).
\]

[verify.py](verify.py) expands every row term with exact Fraction arithmetic
and checks that the resulting coefficients of both \(R_1\) and \(R_2\) are
one. The complete posterior tensor reduces to

\[
\begin{array}{c|ccc}
 &f_W&f_U&f_V\\ \hline
a&c_1(I_Y-I_G)&I_G-I_Y&0\\
b&0&c_1I_K-c'_1I_G&c_1I_G-c'_1I_K\\
c&c_1(I_Z-I_K)&0&I_K-I_Z.
\end{array}
\]

The constant prior term is \(c'_1(I_Y(q_0)+I_Z(q_0))\).

## Continuous weak-duality certificate

For each group, the verifier supplies affine inner lines and one affine outer
line satisfying, over the complete interval \([0,1]\),

\[
L_U(w;q)\ge f_U(q),\qquad L_V(w;q)\ge f_V(q),
\]

\[
\alpha+\beta w\ge
f_W(w)+L_U(w;w)+L_V(w;w).
\]

The martingale identities turn the expectation of each inner affine line at
\(q_U,q_V\) into its value at \(q_W\). Taking expectations of the outer line
therefore gives a valid weak-duality upper bound without strong duality,
minimax exchange, or an exact-contact assumption.

Here are the lines checked by the verifier.  Put

\[
h(q)=I_G(q)-I_Y(q),\qquad h_C(q)=I_K(q)-I_Z(q)=h(1-q).
\]

For group \(a\), \(L_V=0\), the outer line is
\(\alpha_A+\beta_Aw\), and

\[
L_U(w;q)=
\begin{cases}
h(w)+h'(w)(q-w),&w\le T_A,\\
h(T_A)+h'(T_A)(q-T_A),&w\ge T_A.
\end{cases}
\]

For group \(c\), reflect this construction: \(L_U=0\), the outer line is
\(\alpha_C-\beta_Aw\), where
\(T_C=1-T_A\) and \(\alpha_C=\alpha_A+\beta_A\), and \(L_V\) is the fixed
tangent to \(h_C\) at \(T_C\) for \(w\le T_C\), then the tangent to \(h_C\)
at \(w\) for \(w\ge T_C\).  For group \(b\),

\[
L_V(w;q)=10^{-18}+s q,\qquad
L_U(w;q)=10^{-18}+s-sq,
\]

with \(s=\mathrm{SLOPE\_V}\); their constant sum is the outer line.

The frozen certificate constants are

    T_A     .223554338099290337686997491745
    M_A0    .114270117882180886477206425091
    M_A1    .768484852026196875796918575693
    BETA_A  .0455668698298748564310479904957
    ALPHA_A .00484278650837243101713855267415
    CI_A    .606174265413707974748966890325
    M_BV    .770453933591712211652688419314
    SLOPE_V .00271239427013419822092236108071
    ICPT_V  1e-18

Group \(c\) is the exact reflection of group \(a\). For group \(b\), the two
inner lines have slopes \(\pm\)SLOPE_V and intercept \(10^{-18}\).

Coverage is continuous, not a sampled-grid check. Exact rational identities
reduce the curvature sign of \(h=I_G-I_Y\) to the affine polynomial

\[
S(q)=a(1-a)-d^2+d(1-2a)q,
\]

where \(a=P(G=0\mid X=0)\) and
\(d=P(G=0\mid X=1)-a\). Exact sign and ordering checks justify the special
tangent and endpoint regions.  In particular, before the unique curvature
transition, concavity puts \(h\) below its tangent.  After the transition,
convexity puts \(h\) below the endpoint chord; the exact positive check

\[
h(T_A)+(1-T_A)h'(T_A)>0
\]

puts the fixed tangent above that chord at its other endpoint.  For the moving
tangents, \(\phi(w)=h(w)+(1-w)h'(w)\) obeys
\(\phi'(w)=(1-w)h''(w)<0\), so
\(\phi(w)\ge\phi(T_A)>0\) for \(w\le T_A\).  Reflection proves the group-\(c\)
statement.  Exact positivity of the corresponding rational curvature
numerator proves convexity at both group-\(b\) contact windows.  The remaining
regions use fail-closed directed Decimal interval
subdivision, interval derivative bounds, a maximum-depth guard, and a
cell-budget guard. A second run under each of three hostile ambient Decimal
contexts must reproduce the entire evidence tuple and final interval exactly.
The successful certificate uses 136 regular cells at maximum depth 30.

Finally, the exact tensor audit gives nonnegative equal coefficients on
\(I_Y(q_0)\) and \(I_Z(q_0)\), zero coefficients on \(I_G(q_0),I_K(q_0)\),
and zero total affine slope. The prior bound is therefore concave and
reflection symmetric, so its global maximum over every \(q_0\in[0,1]\) is
the certified value at \(q_0=1/2\).

## Reproduction and governed verification

Run from this directory using only the Python standard library:

    python3 -I -B verify.py

The checker performs the exact row and tensor audit, proves every continuous
inner and outer inequality, certifies the all-priors reduction, requires the
computed interval to equal the interval in the claim exactly, and requires
its upper endpoint not to exceed the rounded headline. It exits nonzero on
any unresolved interval, evidence drift, or failed assertion.

[verification.json](verification.json) requests the approved
python-stdlib-3-13-v1 verifier at spec digest

    sha256:fc7ed06b77396fabc1da84694b4d8a08800843f41ad8ca4b9cd666b67ba60884

to run the same no-argument entrypoint in the pinned networkless, read-only
environment. The request records no result. Its terminal outcome is published
after canonical merge as a separate content-addressed attestation.

## Provenance and exclusions

The numerical certificate and original checker were authored in the Yukon
BSSC work and later ported in canonical transaction
7e7626cbff7270572d51a8fda719154ab602907f. That indeterminate cumulative
transaction is historical provenance only and is not a logical dependency.
The verifier here retains its mathematical computation, adds explicit exact
interval and rounded-headline assertions, labels the six premise-bound rows,
and removes the unrelated comparison with a preceding certificate.

Transactions d638c346212db3e75f6a53dcebcfd09f55125852 and
f093396fe03f8920f9905c385ef34b1335792d5e, and any finite-grid or \(Q_0\)
replacement, are likewise not required premises. No invariant functional,
rank-eight quotient, predecessor improvement, receiver optimality, or
provenance-verbatim claim from the cumulative port is repeated here.

The certificate was narrowed, source-mapped, and replayed by an OpenAI Codex
solver agent at Robert Raynor's request. The underlying numerical certificate
retains its original authorship and provenance.

</artifact>
<artifact path="problems/bssc-sum-capacity/contributions/fixed-pair-upper-bound-attested/claims.json">
{
  "schemaVersion": 1,
  "claims": [
    {
      "claimKey": "bssc-sum-capacity/fixed-pair-upper-bound-attested",
      "statement": "Assume the cited Gohari--Liu--Nair Theorem 9 outer-bound premise exactly as stated in the sole declared dependency. For the half-skew BSSC, fix binary auxiliary receivers with P(G=0|X=0)=0.206961624915382, P(G=0|X=1)=0.826953249115544, P(K=0|X=0)=0.173046750884456, and P(K=0|X=1)=0.793038375084618, treating every displayed decimal as exact. The dependency's premise-bound private-message rows and the included exact-rational plus directed-interval weak-duality certificate prove C_sum <= U with U in [0.36929694596920284244271335135600317726937686320586339865039784778686683932875798, 0.36929694596920284244271335135600317726937686320586339865039784778686683932875818], and hence C_sum <= 0.369296945969202842443. This claim concerns only this fixed receiver pair and dual certificate; it does not authenticate or re-prove the cited theorem premise and does not assert receiver or dual optimality, a matching achievable rate, or the exact BSSC sum-capacity.",
      "dependencyTransactionIds": [
        "e3c1036ca607539a5ebcddf3058e6014ac5c1cd9"
      ]
    }
  ]
}

</artifact>
<artifact path="problems/bssc-sum-capacity/contributions/fixed-pair-upper-bound-attested/verification.json">
{
  "schemaVersion": 1,
  "verifier": {
    "id": "python-stdlib-3-13-v1",
    "specDigest": "sha256:fc7ed06b77396fabc1da84694b4d8a08800843f41ad8ca4b9cd666b67ba60884"
  },
  "entrypoint": "verify.py",
  "arguments": []
}

</artifact>
<artifact path="problems/bssc-sum-capacity/contributions/fixed-pair-upper-bound-attested/verify.py">
#!/usr/bin/env python3
"""Outward fixed-pair dual certificate under the declared theorem premise."""

from collections import defaultdict
from dataclasses import dataclass
from decimal import (Context, Decimal, ROUND_CEILING, ROUND_FLOOR,
                     ROUND_HALF_EVEN, ROUND_UP, getcontext, setcontext)
from fractions import Fraction

D = Decimal
NEAR = Context(prec=80, rounding=ROUND_HALF_EVEN)
DOWN = Context(prec=80, rounding=ROUND_FLOOR)
UP = Context(prec=80, rounding=ROUND_CEILING)


@dataclass(frozen=True)
class IV:
    lo: Decimal
    hi: Decimal

    def __post_init__(self):
        if self.lo > self.hi:
            raise ValueError(self)

    @staticmethod
    def point(x):
        x = x if isinstance(x, Decimal) else D(x)
        return IV(x, x)

    def __add__(self, y):
        return IV(DOWN.add(self.lo, y.lo), UP.add(self.hi, y.hi))

    def __neg__(self):
        return IV(self.hi.copy_negate(), self.lo.copy_negate())

    def __sub__(self, y):
        return self + (-y)

    def __mul__(self, y):
        p = ((self.lo, y.lo), (self.lo, y.hi),
             (self.hi, y.lo), (self.hi, y.hi))
        return IV(min(DOWN.multiply(x, z) for x, z in p),
                  max(UP.multiply(x, z) for x, z in p))

    def __truediv__(self, y):
        if y.lo <= 0 <= y.hi:
            raise ZeroDivisionError(y)
        return self * IV(DOWN.divide(D(1), y.hi), UP.divide(D(1), y.lo))

    def ln(self):
        if self.lo <= 0:
            raise ValueError(self)
        lo, hi = NEAR.ln(self.lo), NEAR.ln(self.hi)
        return IV(lo.next_minus(context=NEAR), hi.next_plus(context=NEAR))

    def __str__(self):
        return f"[{self.lo}, {self.hi}]"


Q = IV.point
ZERO, ONE, HALF = Q(0), Q(1), Q("0.5")
LN2 = Q(2).ln()
HEADLINE = D("0.369296945969202842443")
EXPECTED_VALUE = IV(
    D("0.36929694596920284244271335135600317726937686320586339865039784778686683932875798"),
    D("0.36929694596920284244271335135600317726937686320586339865039784778686683932875818"),
)


def need(ok, message):
    if not ok:
        raise AssertionError(message)


def h2(p):
    if p.lo == p.hi and p.lo in (0, 1):
        return ZERO
    if p.lo > 0 and p.hi < 1:
        return -(p * p.ln() + (ONE - p) * (ONE - p).ln()) / LN2
    if p.lo <= 0 and p.hi <= D(".25"):
        return IV(D(0), h2(Q(p.hi)).hi)
    if p.hi >= 1 and p.lo >= D(".75"):
        return IV(D(0), h2(Q(p.lo)).hi)
    raise ValueError(p)


# Every numeral below is an exact decimal rational.
A_CH = D("0.206961624915382")
B_CH = D("0.826953249115544")
K0_CH = D("0.173046750884456")
K1_CH = D("0.793038375084618")
EPS = D("0.000173428163029")
C1 = D("0.4999132859184855")
C1P = D("0.5000867140815145")
W_M = D("0.4999132859184855")
W_O = D("0.4997398577554565")

TA = D("0.223554338099290337686997491745")
MA0 = D("0.114270117882180886477206425091")
MA1 = D("0.768484852026196875796918575693")
BA = D("0.0455668698298748564310479904957")
AA = D("0.00484278650837243101713855267415")
CI = D("0.606174265413707974748966890325")
MBV = D("0.770453933591712211652688419314")
SV = D("0.00271239427013419822092236108071")
IV0 = D("1e-18")
WIN = D("0.0625")
TC = NEAR.subtract(D(1), TA)
MC0 = NEAR.subtract(D(1), MA1)
MC1 = NEAR.subtract(D(1), MA0)
AC = NEAR.add(AA, BA)
MBU = NEAR.subtract(D(1), MBV)
IU0 = NEAR.add(IV0, SV)

H_A, H_B = h2(Q(A_CH)), h2(Q(B_CH))
H_K0, H_K1 = h2(Q(K0_CH)), h2(Q(K1_CH))
DQ = Q(B_CH) - Q(A_CH)


def iy(q):
    return h2((ONE - q) * HALF) - (ONE - q)


def iyp(q):
    m = (ONE - q) * HALF
    return -HALF * ((ONE - m) / m).ln() / LN2 + ONE


def iz(q):
    return h2(ONE - q * HALF) - q


def izp(q):
    m = ONE - q * HALF
    return -HALF * ((ONE - m) / m).ln() / LN2 - ONE


def ig(q):
    m = Q(A_CH) + q * DQ
    return h2(m) - (ONE - q) * H_A - q * H_B


def igp(q):
    m = Q(A_CH) + q * DQ
    return DQ * ((ONE - m) / m).ln() / LN2 + H_A - H_B


def ik(q):
    m = Q(K0_CH) + q * DQ
    return h2(m) - (ONE - q) * H_K0 - q * H_K1


def ikp(q):
    m = Q(K0_CH) + q * DQ
    return DQ * ((ONE - m) / m).ln() / LN2 + H_K0 - H_K1


def h(q): return ig(q) - iy(q)
def hp(q): return igp(q) - iyp(q)
def hc(q): return ik(q) - iz(q)
def hcp(q): return ikp(q) - izp(q)
def fv(q): return Q(C1) * ig(q) - Q(C1P) * ik(q)
def fvp(q): return Q(C1) * igp(q) - Q(C1P) * ikp(q)
def fu(q): return Q(C1) * ik(q) - Q(C1P) * ig(q)
def fup(q): return Q(C1) * ikp(q) - Q(C1P) * igp(q)


# Six premise-bound Theorem-9 rows from the declared foundation transaction.
# In order these are R1A(1), R2T(1), SR(1,C), SL(2,U), SR(2,U), and
# F_Y_right_minus_left.  A term is (group, MI-kind, channel, sign).
GA, GB, GC = range(3)
Y, Z, G, K = range(4)
CONST, WL, UL, VL = range(4)
KINDS = {
    "W": ((CONST, 1), (WL, -1)),
    "U|W": ((WL, 1), (UL, -1)),
    "V|W": ((WL, 1), (VL, -1)),
    "UW": ((CONST, 1), (UL, -1)),
    "VW": ((CONST, 1), (VL, -1)),
    "X|UW": ((UL, 1),), "X|VW": ((VL, 1),),
}
ROWS = (
    (1, 0, ((GC,"W",Z,1),(GA,"U|W",Y,1),(GA,"W",G,1),
            (GB,"W",G,-1),(GB,"W",K,1),(GC,"W",K,-1),
            (GB,"UW",G,1),(GA,"UW",G,-1))),
    (0, 1, ((GC,"W",Z,1),(GC,"V|W",Z,1),
            (GB,"VW",K,1),(GC,"VW",K,-1))),
    (1, 1, ((GA,"W",Y,1),(GC,"W",K,1),(GB,"W",K,-1),
            (GB,"W",G,1),(GA,"W",G,-1),(GA,"VW",G,1),
            (GB,"VW",G,-1),(GB,"VW",K,1),(GC,"VW",K,-1),
            (GC,"V|W",Z,1),(GA,"X|VW",Y,1))),
    (1, 1, ((GA,"W",Y,1),(GA,"U|W",Y,1),(GC,"V|W",Z,1),
            (GB,"UW",G,1),(GA,"UW",G,-1),(GC,"V|W",K,-1),
            (GB,"X|UW",K,1))),
    (1, 1, ((GC,"W",Z,1),(GA,"U|W",Y,1),(GC,"V|W",Z,1),
            (GB,"VW",K,1),(GC,"VW",K,-1),(GA,"U|W",G,-1),
            (GB,"X|VW",G,1))),
    (0, 0, ((GA,"U|W",Y,1),(GA,"U|W",G,-1),
            (GA,"X|VW",Y,-1),(GA,"X|VW",G,1))),
)
WEIGHTS = (EPS, EPS, EPS, W_M, W_O, EPS)


def exact_audit():
    e, half = Fraction(EPS), Fraction(1, 2)
    need(Fraction(K0_CH)==1-Fraction(B_CH) and
         Fraction(K1_CH)==1-Fraction(A_CH), "reflected channel")
    need(Fraction(C1) == half-e/2 and Fraction(C1P) == half+e/2 and
         Fraction(W_M) == half-e/2 and Fraction(W_O) == half-3*e/2,
         "weight identities")
    need(all(Fraction(w) >= 0 for w in WEIGHTS), "negative weight")
    need(sum(Fraction(w)*row[0] for w,row in zip(WEIGHTS,ROWS)) == 1 and
         sum(Fraction(w)*row[1] for w,row in zip(WEIGHTS,ROWS)) == 1,
         "rate coefficients")
    got = defaultdict(Fraction)
    for weight, (_, _, terms) in zip(WEIGHTS, ROWS):
        for group, kind, channel, sign in terms:
            for level, coefficient in KINDS[kind]:
                got[group,level,channel] += Fraction(weight)*sign*coefficient
    expected = {
        (GA,CONST,Y):half+e/2,(GA,CONST,G):-(half-e/2),
        (GA,WL,Y):half-e/2,(GA,WL,G):-(half-e/2),
        (GA,UL,Y):-1,(GA,UL,G):1,
        (GB,CONST,G):half-e/2,(GB,CONST,K):half+e/2,
        (GB,UL,G):-(half+e/2),(GB,UL,K):half-e/2,
        (GB,VL,G):half-e/2,(GB,VL,K):-(half+e/2),
        (GC,CONST,Z):half+e/2,(GC,CONST,K):-(half+e/2),
        (GC,WL,Z):half-e/2,(GC,WL,K):-(half-e/2),
        (GC,VL,Z):-1,(GC,VL,K):1,
    }
    need({k:v for k,v in got.items() if v} == expected, "combined tensor")
    for ch,target in ((Y,half+e/2),(Z,half+e/2),(G,0),(K,0)):
        need(sum(got[g,CONST,ch] for g in range(3)) == target,
             "constant/prior coefficients")
    need(Fraction(TC)==1-Fraction(TA) and Fraction(MC0)==1-Fraction(MA1)
         and Fraction(MC1)==1-Fraction(MA0) and
         Fraction(AC)==Fraction(AA)+Fraction(BA) and
         Fraction(MBU)==1-Fraction(MBV) and
         Fraction(IU0)==Fraction(IV0)+Fraction(SV), "mirror lines")

    dw, a, b = Fraction(WIN), Fraction(A_CH), Fraction(B_CH)
    ta, ma0, ma1, ci, mbv = map(Fraction, (TA,MA0,MA1,CI,MBV))
    need(0<ma0<ta<ci<ma1-dw and ma1+dw<1 and
         0<mbv-dw<mbv+dw<1 and 0<Fraction(MBU)-dw, "region order")
    delta = b-a
    sgn = lambda q: a*(1-a)-delta*delta+delta*(1-2*a)*q
    need(delta*(1-2*a)>0 and sgn(ta)<0 and sgn(ci)<0 and
         sgn(ma1-dw)>0, "curvature signs")

    k0, c1, c1p = Fraction(K0_CH), Fraction(C1), Fraction(C1P)
    def var(x0, q):
        m=x0+q*delta
        return m*(1-m)
    def rq(q): return c1*var(k0,q)-c1p*var(a,q)
    def positive_quadratic(lo, hi, f):
        values=[f(lo),f(hi)]
        lead=2*(f(Fraction(0))+f(Fraction(1))-2*f(Fraction(1,2)))
        if lead:
            vertex=-(f(Fraction(1))-f(Fraction(-1)))/(4*lead)
            if lo<vertex<hi: values.append(f(vertex))
        return all(v>0 for v in values)
    need(positive_quadratic(mbv-dw,mbv+dw,rq) and
         positive_quadratic(1-mbv-dw,1-mbv+dw,lambda q:rq(1-q)),
         "group-B contact convexity")


class Gaps:
    def __init__(self):
        self.ht, self.hpt = h(Q(TA)), hp(Q(TA))
        self.hct, self.hcpt = hc(Q(TC)), hcp(Q(TC))

    def a1(self,w): return Q(AA)+Q(BA)*w-Q(C1P)*h(w)
    def a1p(self,w): return Q(BA)-Q(C1P)*hp(w)
    def a2(self,w):
        return Q(AA)+Q(BA)*w+Q(C1)*h(w)-self.ht-self.hpt*(w-Q(TA))
    def a2p(self,w): return Q(BA)+Q(C1)*hp(w)-self.hpt
    def c1(self,w): return Q(AC)-Q(BA)*w-Q(C1P)*hc(w)
    def c1p(self,w): return -Q(BA)-Q(C1P)*hcp(w)
    def c2(self,w):
        return Q(AC)-Q(BA)*w+Q(C1)*hc(w)-self.hct-self.hcpt*(w-Q(TC))
    def c2p(self,w): return -Q(BA)+Q(C1)*hcp(w)-self.hcpt
    def bv(self,w): return Q(IV0)+Q(SV)*w-fv(w)
    def bvp(self,w): return Q(SV)-fvp(w)
    def bu(self,w): return Q(IU0)-Q(SV)*w-fu(w)
    def bup(self,w): return -Q(SV)-fup(w)


def abs_hi(x): return max(x.lo.copy_abs(), x.hi.copy_abs())


def tangent_floor(f, fp, middle, radius):
    value, deriv = f(Q(middle)), fp(Q(middle))
    floor = DOWN.subtract(value.lo, UP.multiply(abs_hi(deriv), radius))
    need(value.lo > 0 and floor > 0, "contact tangent bound")
    return floor


def endpoint_floor(f, left, right):
    a, b = f(Q(left)).lo, f(Q(right)).lo
    need(a > 0 and b > 0, "concave endpoint bound")
    return min(a, b)


def cover(f, fp, left, right, endpoint_derivative=False):
    stack, accepted, depth_max, worst = [(left,right,0)], 0, 0, None
    while stack:
        x,y,depth=stack.pop()
        need(depth <= 110 and UP.subtract(y,x) >= D("1e-40"),
             "unresolved interval cell")
        cell, value = IV(x,y), f(IV(x,y))
        if value.lo > 0:
            margin=value.lo
        else:
            mid=NEAR.divide(NEAR.add(x,y),D(2))
            need(x < mid < y, "noninterior subdivision midpoint")
            margin=None
            if endpoint_derivative or (x>0 and y<1):
                # Bound distance from the *computed* midpoint rather than
                # assuming its rounded value is the exact arithmetic midpoint.
                width=max(UP.subtract(mid,x),UP.subtract(y,mid))
                margin=DOWN.subtract(f(Q(mid)).lo,
                                     UP.multiply(abs_hi(fp(cell)),width))
            if margin is None or margin <= 0:
                stack.extend(((x,mid,depth+1),(mid,y,depth+1)))
                continue
        accepted += 1
        need(accepted <= 500000, "cell budget")
        depth_max=max(depth_max,depth)
        worst=margin if worst is None else min(worst,margin)
    return accepted, depth_max, worst


def certify():
    exact_audit()
    g=Gaps()
    phi_a=g.ht+(ONE-Q(TA))*g.hpt
    phi_c=g.hct-Q(TC)*g.hcpt
    need(phi_a.lo>0 and phi_c.lo>0, "global inner tangent lemma")

    floors=[
        tangent_floor(g.a1,g.a1p,MA0,max(UP.subtract(TA,MA0),MA0)),
        endpoint_floor(g.a2,TA,CI),
        tangent_floor(g.a2,g.a2p,MA1,WIN),
        tangent_floor(g.c1,g.c1p,MC1,max(UP.subtract(MC1,TC),
                                        UP.subtract(D(1),MC1))),
        endpoint_floor(g.c2,DOWN.subtract(D(1),CI),TC),
        tangent_floor(g.c2,g.c2p,MC0,WIN),
        tangent_floor(g.bv,g.bvp,MBV,WIN),
        tangent_floor(g.bu,g.bup,MBU,WIN),
    ]
    segments=(
        (g.a2,g.a2p,CI,DOWN.subtract(MA1,WIN),False),
        (g.a2,g.a2p,UP.add(MA1,WIN),D(1),False),
        (g.c2,g.c2p,D(0),DOWN.subtract(MC0,WIN),False),
        (g.c2,g.c2p,UP.add(MC0,WIN),DOWN.subtract(D(1),CI),False),
        (g.bv,g.bvp,D(0),DOWN.subtract(MBV,WIN),True),
        (g.bv,g.bvp,UP.add(MBV,WIN),D(1),True),
        (g.bu,g.bup,D(0),DOWN.subtract(MBU,WIN),True),
        (g.bu,g.bup,UP.add(MBU,WIN),D(1),True),
    )
    covers=[cover(*s) for s in segments]
    value=(Q(C1P)*(iy(HALF)+iz(HALF))+
           Q(AA)+Q(BA)*HALF+Q(AC)-Q(BA)*HALF+
           Q(IU0)-Q(SV)*HALF+Q(IV0)+Q(SV)*HALF)
    need(value == EXPECTED_VALUE, "final interval drift")
    need(value.hi <= HEADLINE, "claimed rounded upper bound not certified")
    evidence=(phi_a,phi_c,tuple(floors),tuple(covers),value)
    return value,evidence


def main():
    reference,evidence=certify()
    saved=getcontext().copy()
    try:
        for precision,rounding in ((5,ROUND_UP),(7,ROUND_FLOOR),
                                   (3,ROUND_CEILING)):
            getcontext().prec, getcontext().rounding = precision, rounding
            need(certify()==(reference,evidence), "ambient context leaked")
    finally:
        setcontext(saved)
    cells=sum(x[0] for x in evidence[3])
    depth=max(x[1] for x in evidence[3])
    print("PASS: exact row/tensor audit; continuous D1/D2; all priors;")
    print("      three hostile Decimal contexts identical")
    print("U =",reference)
    print("certified rounded headline =", HEADLINE)
    print("regular interval cover:",cells,"cells; max depth",depth)


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
<contribution>
ordinal: 12
transaction_id: 1be513bb3d8f67f54e299ea0085cd2ef05144711
contribution_id: uniform-receiver-curve-continuum-bridge
author: Robert Raynor
<artifact path="problems/bssc-sum-capacity/contributions/uniform-receiver-curve-continuum-bridge/README.md">
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

</artifact>
<artifact path="problems/bssc-sum-capacity/contributions/uniform-receiver-curve-continuum-bridge/claims.json">
{
  "schemaVersion": 1,
  "claims": [
    {
      "claimKey": "bssc-sum-capacity/uniform-receiver-curve-continuum-bridge",
      "statement": "Using the accepted premise-bound 30-row system and finite-grid posterior-measure reduction of transactions e3c1036ca607539a5ebcddf3058e6014ac5c1cd9 and e2bbc1e210e496b3c834e658820fc90287f3b2c0, respectively: (i) every binary-input receiver curve obeys |J_A(p)-J_A(p')| <= 2 h_2(|p-p'|); (ii) the generalized mean-one-half posterior-measure receiver curves form a compact subset of C([0,1]) whose finite-output curves are uniformly dense, and for every N-point grid Q containing {0,1/2,1} there is an at-most-N-output exact grid match with sup-norm error at most min{1,4 h_2(Delta_Q)}, preserving an already reflected pair on reflection-closed Q; and (iii) replacing G,K by curves within epsilon_G,epsilon_K changes every one of the accepted 30 row right sides by at most a_r epsilon_G+b_r epsilon_K with the displayed audited coefficients, universally at most 4 epsilon_G+4 epsilon_K. Hence the same hierarchy is feasible under those explicit row relaxations, and strictly feasible witnesses persist under sufficiently fine approximations. No unrelaxed optimized-value convergence, exact full-functional cardinality, reflected optimality, minimax interchange, numerical capacity improvement, or exact sum-capacity is asserted.",
      "dependencyTransactionIds": [
        "e3c1036ca607539a5ebcddf3058e6014ac5c1cd9",
        "e2bbc1e210e496b3c834e658820fc90287f3b2c0"
      ]
    }
  ]
}

</artifact>
<artifact path="problems/bssc-sum-capacity/contributions/uniform-receiver-curve-continuum-bridge/verification.json">
{
  "schemaVersion": 1,
  "verifier": {
    "id": "python-stdlib-3-13-v1",
    "specDigest": "sha256:fc7ed06b77396fabc1da84694b4d8a08800843f41ad8ca4b9cd666b67ba60884"
  },
  "entrypoint": "verify_stability.py",
  "arguments": []
}

</artifact>
<artifact path="problems/bssc-sum-capacity/contributions/uniform-receiver-curve-continuum-bridge/verify_stability.py">
#!/usr/bin/env python3
"""Exact combinatorial audit for receiver-curve row stability.

This checker independently rebuilds the generic length-three path rows accepted
in dependency e3c1036ca607539a5ebcddf3058e6014ac5c1cd9.  It checks the
reviewed curve-error coefficient table and elementary uniform-grid formulas.
It does not prove the analytic entropy or compactness arguments in README.md.
"""

from __future__ import annotations

import json
from fractions import Fraction
from pathlib import Path


GROUPS = ("a", "b", "c")
OUTPUTS = ("Y", "G", "K", "Z")
MIRROR_KIND = {
    "W": "W", "U|W": "V|W", "V|W": "U|W", "UW": "VW",
    "VW": "UW", "X|UW": "X|VW", "X|VW": "X|UW",
}
TERM_WEIGHT = {
    "W": 2, "U|W": 2, "V|W": 2, "UW": 2, "VW": 2,
    "X|UW": 1, "X|VW": 1,
}
EXPECTED_DEPENDENCIES = [
    "e3c1036ca607539a5ebcddf3058e6014ac5c1cd9",
    "e2bbc1e210e496b3c834e658820fc90287f3b2c0",
]
EXPECTED = {
    "F_Y_left": (1, 0), "F_Y_right_minus_left": (3, 0),
    "F_Z_left": (0, 1), "F_Z_right_minus_left": (0, 3),
    "N_Y(0)": (0, 0), "N_Y(1)": (4, 0), "N_Y(2)": (4, 4),
    "N_Z(0)": (0, 0), "N_Z(1)": (0, 4), "N_Z(2)": (4, 4),
    "R1A(0)": (4, 4), "R1A(1)": (4, 4), "R1A(2)": (4, 4),
    "R1T(0)": (0, 0), "R1T(1)": (4, 0), "R1T(2)": (4, 4),
    "R2A(0)": (4, 4), "R2A(1)": (4, 4), "R2A(2)": (4, 4),
    "R2T(0)": (0, 0), "R2T(1)": (0, 4), "R2T(2)": (4, 4),
    "SL(1,U)": (3, 4), "SL(2,U)": (4, 3),
    "SL(3,C)": (4, 4), "SL(3,U)": (4, 4),
    "SR(1,C)": (4, 4), "SR(1,U)": (4, 4),
    "SR(2,U)": (3, 4), "SR(3,U)": (4, 3),
}

Term = tuple[int, str, str, str]
Row = tuple[str, int, int, tuple[Term, ...]]


def term(coefficient: int, group: str, kind: str, output: str) -> Term:
    return coefficient, group, kind, output


def mirror(terms: tuple[Term, ...]) -> tuple[Term, ...]:
    group_mirror = {"a": "c", "b": "b", "c": "a"}
    output_mirror = {"Y": "Z", "G": "K", "K": "G", "Z": "Y"}
    return tuple(
        term(c, group_mirror[g], MIRROR_KIND[k], output_mirror[o])
        for c, g, k, o in terms
    )


def make_rows() -> list[Row]:
    rows: list[Row] = []
    length = 3

    def group(index: int) -> str:
        return GROUPS[index - 1]

    def output(index: int) -> str:
        return OUTPUTS[index]

    for middle in range(1, length + 1):
        u_walk = tuple(
            entry for index in range(1, middle) for entry in (
                term(1, group(index), "UW", output(index - 1)),
                term(-1, group(index), "UW", output(index)),
            )
        )
        uc_walk = tuple(
            entry for index in range(1, middle) for entry in (
                term(1, group(index), "U|W", output(index - 1)),
                term(-1, group(index), "U|W", output(index)),
            )
        )
        vc_walk = tuple(
            entry for index in range(middle + 1, length + 1) for entry in (
                term(1, group(index), "V|W", output(index)),
                term(-1, group(index), "V|W", output(index - 1)),
            )
        )
        v_walk = tuple(
            entry for index in range(middle + 1, length + 1) for entry in (
                term(1, group(index), "VW", output(index)),
                term(-1, group(index), "VW", output(index - 1)),
            )
        )
        rows.append((
            f"SL({middle},U)", 1, 1,
            u_walk + (
                term(1, group(middle), "UW", output(middle - 1)),
                term(1, group(middle), "X|UW", output(middle)),
            ) + vc_walk,
        ))
        rows.append((
            f"SR({middle},U)", 1, 1,
            v_walk + (
                term(1, group(middle), "VW", output(middle)),
                term(1, group(middle), "X|VW", output(middle - 1)),
            ) + uc_walk,
        ))
        if middle == length:
            rows.append((
                f"SL({middle},C)", 1, 1,
                uc_walk + (
                    term(1, group(middle), "U|W", output(middle - 1)),
                    term(1, group(middle), "X|UW", output(middle)),
                    term(1, group(middle), "W", output(middle)),
                ) + vc_walk,
            ))
        if middle == 1:
            rows.append((
                f"SR({middle},C)", 1, 1,
                vc_walk + (
                    term(1, group(middle), "V|W", output(middle)),
                    term(1, group(middle), "X|VW", output(middle - 1)),
                    term(1, group(middle), "W", output(middle - 1)),
                ) + uc_walk,
            ))

    r1_rows: list[Row] = []
    for stop in range(length):
        terms = tuple(
            entry for index in range(1, stop + 1) for entry in (
                term(1, group(index), "UW", output(index - 1)),
                term(-1, group(index), "UW", output(index)),
            )
        ) + (term(1, group(stop + 1), "UW", output(stop)),)
        r1_rows.append((f"R1T({stop})", 1, 0, terms))
    for stop in range(length):
        terms = tuple(
            entry for index in range(1, stop + 1) for entry in (
                term(1, group(index), "U|W", output(index - 1)),
                term(-1, group(index), "U|W", output(index)),
            )
        ) + (term(1, group(stop + 1), "U|W", output(stop)),) + tuple(
            entry for index in range(stop + 1, length) for entry in (
                term(1, group(index), "W", output(index)),
                term(-1, group(index + 1), "W", output(index)),
            )
        ) + (term(1, group(length), "W", output(length)),)
        r1_rows.append((f"R1A({stop})", 1, 0, terms))
    rows.extend(r1_rows)
    rows.extend(("R2" + label[2:], 0, 1, mirror(terms)) for label, _, _, terms in r1_rows)

    nonnegative_y: list[Row] = []
    for stop in range(length):
        terms = (term(1, "a", "W", "Y"),) + tuple(
            entry for index in range(1, stop + 1) for entry in (
                term(1, group(index + 1), "W", output(index)),
                term(-1, group(index), "W", output(index)),
            )
        )
        nonnegative_y.append((f"N_Y({stop})", 0, 0, terms))
    rows.extend(nonnegative_y)
    rows.extend((f"N_Z({stop})", 0, 0, mirror(row[3])) for stop, row in enumerate(nonnegative_y))

    rows.extend([
        ("F_Z_left", 0, 0, (
            term(1, "c", "X|UW", "Z"), term(-1, "c", "X|UW", "K"))),
        ("F_Z_right_minus_left", 0, 0, (
            term(1, "c", "V|W", "Z"), term(-1, "c", "V|W", "K"),
            term(-1, "c", "X|UW", "Z"), term(1, "c", "X|UW", "K"))),
        ("F_Y_left", 0, 0, (
            term(1, "a", "X|VW", "Y"), term(-1, "a", "X|VW", "G"))),
        ("F_Y_right_minus_left", 0, 0, (
            term(1, "a", "U|W", "Y"), term(-1, "a", "U|W", "G"),
            term(-1, "a", "X|VW", "Y"), term(1, "a", "X|VW", "G"))),
    ])
    return rows


def row_bound(terms: tuple[Term, ...]) -> tuple[int, int]:
    combined: dict[tuple[str, str, str], int] = {}
    for coefficient, group, kind, output in terms:
        atom = group, kind, output
        combined[atom] = combined.get(atom, 0) + coefficient
    result = {"G": 0, "K": 0}
    for (_, kind, output), coefficient in combined.items():
        if output in result:
            result[output] += abs(coefficient) * TERM_WEIGHT[kind]
    return result["G"], result["K"]


def check_claims() -> None:
    data = json.loads(Path("claims.json").read_text(encoding="utf-8"))
    claims = data.get("claims")
    if data.get("schemaVersion") != 1 or not isinstance(claims, list) or len(claims) != 1:
        raise AssertionError("claims.json must contain exactly one schema-v1 claim")
    if claims[0].get("dependencyTransactionIds") != EXPECTED_DEPENDENCIES:
        raise AssertionError("unexpected dependency transaction list or order")
    print("PASS: exact canonical dependencies")


def check_rows() -> None:
    rows = make_rows()
    labels = [row[0] for row in rows]
    if len(rows) != 30 or len(set(labels)) != 30 or set(labels) != set(EXPECTED):
        raise AssertionError("generic path generator did not produce the exact 30 labels")
    for label, _, _, terms in rows:
        actual = row_bound(terms)
        if actual != EXPECTED[label]:
            raise AssertionError(f"{label}: expected {EXPECTED[label]}, got {actual}")
        if actual[0] > 4 or actual[1] > 4:
            raise AssertionError(f"{label}: global coefficient bound failed")
        print(f"PASS {label}: (a_r,b_r)={actual}")
    print("PASS: all 30 rowwise bounds and the global (4,4) bound")


def check_uniform_grids() -> None:
    for m in range(1, 257):
        grid = [Fraction(j, 2 * m) for j in range(2 * m + 1)]
        if len(grid) != 2 * m + 1 or grid[0] != 0 or grid[-1] != 1:
            raise AssertionError("uniform grid support formula failed")
        if Fraction(1, 2) not in grid or grid != [1 - q for q in reversed(grid)]:
            raise AssertionError("uniform grid midpoint/reflection property failed")
        mesh_radius = max((grid[j + 1] - grid[j]) / 2 for j in range(len(grid) - 1))
        if mesh_radius != Fraction(1, 4 * m):
            raise AssertionError("uniform grid mesh-radius formula failed")
    print("PASS: Q_M has 2M+1 points, is reflected, and has mesh radius 1/(4M)")


def main() -> None:
    check_claims()
    check_rows()
    check_uniform_grids()
    print("PASS: uniform receiver-curve continuum-bridge mechanical audit")


if __name__ == "__main__":
    main()

</artifact>
</contribution>
<contribution>
ordinal: 14
transaction_id: b4f10336d43f1c31a11ecbc5f4eb94f1fca70e05
contribution_id: two-letter-marton-two-symbol-pruning
author: Robert Raynor
<artifact path="problems/bssc-sum-capacity/contributions/two-letter-marton-two-symbol-pruning/README.md">
# Two-letter Marton pruning for one- and two-symbol super-input support

## Claim and scope

Let $P$ be the half-skew BSSC in the governed problem and let
$P^{\otimes2}$ have super-input
$S=(X_1,X_2)\in\{00,01,10,11\}$.  Assume the binary-input Marton
sum-rate theorem of Geng, Jog, Nair, and Wang: for every binary-input
two-receiver broadcast channel, Marton's private-message sum-rate equals
randomized time division.

Under that premise, the Marton sum value of every finite law for
$P^{\otimes2}$ whose
induced super-input is supported on at most two of the four symbols satisfies

\[
 R_{\rm Marton}(\text{law})<0.615\quad\text{bits}.
\]

Since the product randomized-time-division witness has value

\[
 2R_{\rm RTD}
 =2(0.361642884421954615663441578150587\ldots)
 >0.7232857688439092,
\]

any two-letter Marton witness that strictly improves the current BSSC
achievable rate must give positive mass to at least three super-input
symbols.  This is a search-space pruning theorem, not a no-gain theorem for
three- or four-symbol laws.

This supplies a structural-pruning target in the non-exclusive
`bssc-multiletter-marton-frontier` direction registered by canonical
transaction `7e1e52fe42fde37ba1964ef9ae5062daf8bb55f8`.

The result was prompted by Huang, Liu, and Liu's August 2026 construction of
a ternary-input channel with a strict two-letter Marton gain.  Their paper
explicitly leaves the binary-input case open and uses nonrectangular
two-letter architectures; see
[*Sub-optimality of Marton's Inner Bound for the Two-Receiver Broadcast
Channel*](https://arxiv.org/abs/2608.19869).  No numerical value or theorem
from that construction is used as a premise here.

## The six two-symbol supports

The six unordered pairs split into three exact symmetry classes.

1. **Adjacent pairs.**  The four Hamming-distance-one pairs differ in only
   one input coordinate.  The other coordinate produces input-independent
   output and can be discarded.  For the varying coordinate, couple the two
   receiver outputs so that $(Y,Z)$ is a binary erasure observation of the
   input with erasure probability $1/2$: the ambiguous pair is $(1,0)$,
   while $(0,0)$ and $(1,1)$ identify the input.  Receiver cooperation is
   an outer bound and the private-message capacity depends only on the two
   marginals, so every adjacent-pair Marton rate is at most $1/2$ bit.
2. **Antirepetition pair \(\{01,10\}\).**  Each receiver marginal is a
   BEC\((1/2)\), up to output relabeling: one output of probability $1/2$
   is common to both inputs and the other two identify them.  The two
   marginals may be coupled as the same erasure observation, again giving
   the cooperative outer bound $1/2$ bit.
3. **Repetition pair \(\{00,11\}\).**  This is the only nontrivial class.
   It is a binary-input receiver-skew broadcast channel, so the cited
   binary-input Marton theorem reduces its Marton sum-rate to randomized time
   division.  The next section gives a self-contained upper bound below
   $0.615$ for that functional.

Singleton support conveys no information.  These cases exhaust every support
of size at most two.

## Repetition-orbit randomized-time-division bound

Write $q=\Pr[S=0]$.  For receiver $Y^2$, input $00$ produces the
uniform distribution on four outputs and input $11$ produces the point
mass at $11$.  Thus

\[
 J(q)=I_q(S;Y^2)
 =H_2\!\left(\frac q4,\frac q4,\frac q4,
                   1-\frac{3q}{4}\right)-2q,
 \tag{1}
\]

while $I_q(S;Z^2)=J(1-q)$.  For a randomized-time-division law, let
$q_w=\Pr[S=0\mid W=w]$, let $\bar q=\mathbb E q_W$, and in each
component direct the private layer to whichever receiver has the larger
mutual information.  Then

\[
\begin{aligned}
M
&\le \frac{I(W;Y^2)+I(W;Z^2)}2
   +\mathbb E\max\{J(q_W),J(1-q_W)\}\\
&=\frac{J(\bar q)+J(1-\bar q)}2
  +\frac12\mathbb E|J(q_W)-J(1-q_W)|\\
&\le J(1/2)+\frac12\max_{0\le q\le1}|J(q)-J(1-q)|.
\tag{2}
\end{aligned}
\]

The last step uses concavity of $J$: the sum
$J(q)+J(1-q)$ is concave and reflection symmetric, hence maximized at
$q=1/2$.

For $q\in[1/2,1]$, put $D(q)=J(1-q)-J(q)$.  Direct differentiation
gives

\[
 J'(q)=\frac34\log_2\frac{4-3q}{q}-2,
 \qquad
 J''(q)=-\frac{3}{\ln 2\;q(4-3q)},
\]

and therefore

\[
 D''(q)=-\frac3{\ln2}
 \left(
 \frac1{(1-q)(1+3q)}-\frac1{q(4-3q)}
 \right)<0
 \quad(q>1/2),
\tag{3}
\]

because $q(4-3q)-(1-q)(1+3q)=2q-1>0$.  Also
$D(1/2)=D(1)=0$, so $D\ge0$ and is concave on this half interval;
antisymmetry then gives
$\max|J(q)-J(1-q)|=\max_{[1/2,1]}D(q)$.

At the exact rational point $q_0=17/20$, concavity supplies the global
tangent bound

\[
 D(q)\le D(q_0)+D'(q_0)(q-q_0).
\]

The included directed-Decimal checker proves

\[
 J(1/2)<0.549,qquad D'(q_0)<0,qquad
 \max_{[1/2,1]}D<0.132.
\]

Equation (2) consequently gives $M<0.549+0.132/2=0.615$.

## Reproduction

Run from this contribution directory with only the Python standard library:

```text
python3 -I -B verify.py
```

The checker uses exact `Fraction` arithmetic to build both product receiver
marginals, classify all six two-symbol supports, and verify the displayed
adjacent, antirepetition, and repetition transition structures.  It then uses
80-digit directed `Decimal` intervals for (1)--(3), checks the tangent bound,
and requires the final upper endpoint to be strictly below `0.615`.  It also
checks the strict separation from the two-letter RTD baseline.  The interval
calculation is mechanical corroboration; the support reduction, cooperation
arguments, binary-input Marton premise, and calculus proof are mathematical.

## Provenance and limitations

The binary-input Marton theorem used as an explicit external premise is:
Yanlin Geng, Varun Jog, Chandra Nair, and Zizhou Vincent Wang, *An Information
Inequality and Evaluation of Marton's Inner Bound for Binary Input Broadcast
Channels*, IEEE Transactions on Information Theory 59 (2013),
[arXiv:1001.1468](https://arxiv.org/abs/1001.1468).

The theorem does not exclude a two-letter Marton improvement whose input law
uses three or four super-input symbols; it gives no positive-gain witness,
no multiletter tensorization, no capacity converse, and no improvement to the
governed capacity interval.  The `0.615` bound is deliberately coarse; its
purpose is a robust strict separation from $2R_{\rm RTD}$, not exact
evaluation of the repetition subchannel.  The proof and checker were prepared
by an OpenAI Codex solver agent at Robert Raynor's request.

</artifact>
<artifact path="problems/bssc-sum-capacity/contributions/two-letter-marton-two-symbol-pruning/claims.json">
{
  "schemaVersion": 1,
  "claims": [
    {
      "claimKey": "bssc-sum-capacity/two-letter-marton-two-symbol-pruning",
      "statement": "Assume the Geng--Jog--Nair--Wang theorem that Marton's private-message sum-rate for every binary-input broadcast channel equals randomized time division. For the half-skew BSSC product channel P^{otimes 2}, every finite Marton law whose induced super-input X_1X_2 is supported on at most two of {00,01,10,11} has sum-rate strictly below 0.615 bits. Consequently, because the product randomized-time-division value is greater than 0.7232857688439092 bits, every strict two-letter Marton improvement over the current BSSC achievable rate must use at least three super-input symbols. This is only a support-pruning result and does not rule out a gain on three- or four-symbol support.",
      "dependencyTransactionIds": []
    }
  ]
}

</artifact>
<artifact path="problems/bssc-sum-capacity/contributions/two-letter-marton-two-symbol-pruning/verification.json">
{
  "schemaVersion": 1,
  "verifier": {
    "id": "python-stdlib-3-13-v1",
    "specDigest": "sha256:fc7ed06b77396fabc1da84694b4d8a08800843f41ad8ca4b9cd666b67ba60884"
  },
  "entrypoint": "verify.py",
  "arguments": []
}

</artifact>
<artifact path="problems/bssc-sum-capacity/contributions/two-letter-marton-two-symbol-pruning/verify.py">
#!/usr/bin/env python3
"""Exact orbit audit and directed repetition-orbit tangent certificate."""

from dataclasses import dataclass
from decimal import Context, Decimal, ROUND_CEILING, ROUND_FLOOR, ROUND_HALF_EVEN
from fractions import Fraction as F
from itertools import combinations


D = Decimal
NEAR = Context(prec=80, rounding=ROUND_HALF_EVEN)
DOWN = Context(prec=80, rounding=ROUND_FLOOR)
UP = Context(prec=80, rounding=ROUND_CEILING)


def need(ok, message):
    if not ok:
        raise AssertionError(message)


@dataclass(frozen=True)
class IV:
    lo: Decimal
    hi: Decimal

    def __post_init__(self):
        need(self.lo <= self.hi, "reversed interval")

    @staticmethod
    def point(x):
        x = x if isinstance(x, Decimal) else D(x)
        return IV(x, x)

    def __add__(self, other):
        return IV(DOWN.add(self.lo, other.lo), UP.add(self.hi, other.hi))

    def __neg__(self):
        return IV(self.hi.copy_negate(), self.lo.copy_negate())

    def __sub__(self, other):
        return self + (-other)

    def __mul__(self, other):
        products = ((self.lo, other.lo), (self.lo, other.hi),
                    (self.hi, other.lo), (self.hi, other.hi))
        return IV(min(DOWN.multiply(a, b) for a, b in products),
                  max(UP.multiply(a, b) for a, b in products))

    def __truediv__(self, other):
        need(not (other.lo <= 0 <= other.hi), "interval division by zero")
        inverse = IV(DOWN.divide(D(1), other.hi),
                     UP.divide(D(1), other.lo))
        return self * inverse

    def ln(self):
        need(self.lo > 0, "logarithm domain")
        lo = NEAR.ln(self.lo).next_minus(context=NEAR)
        hi = NEAR.ln(self.hi).next_plus(context=NEAR)
        return IV(lo, hi)


Q = IV.point
ONE = Q(1)
LN2 = Q(2).ln()


def entropy(probabilities):
    out = Q(0)
    for probability in probabilities:
        p = probability if isinstance(probability, IV) else Q(probability)
        if p.lo == p.hi == 0:
            continue
        out = out - p * p.ln() / LN2
    return out


def j_rep(q):
    q = q if isinstance(q, IV) else Q(q)
    a = q / Q(4)
    b = ONE - Q(3) * q / Q(4)
    return entropy((a, a, a, b)) - Q(2) * q


def jp_rep(q):
    q = q if isinstance(q, IV) else Q(q)
    return Q("0.75") * ((Q(4) - Q(3) * q) / q).ln() / LN2 - Q(2)


def product_channel(base):
    result = []
    for x in range(4):
        x1, x2 = divmod(x, 2)
        row = []
        for y in range(4):
            y1, y2 = divmod(y, 2)
            row.append(base[x1][y1] * base[x2][y2])
        result.append(tuple(row))
    return tuple(result)


def exact_orbit_audit():
    y = ((F(1, 2), F(1, 2)), (F(0), F(1)))
    z = ((F(1), F(0)), (F(1, 2), F(1, 2)))
    yy, zz = product_channel(y), product_channel(z)

    pairs = list(combinations(range(4), 2))
    adjacent = [p for p in pairs if (p[0] ^ p[1]).bit_count() == 1]
    diagonal = [p for p in pairs if (p[0] ^ p[1]).bit_count() == 2]
    need(len(pairs) == 6 and len(adjacent) == 4 and
         diagonal == [(0, 3), (1, 2)], "support orbit classification")

    # Repetition transition rows used in equation (1).
    need(yy[0] == (F(1, 4),) * 4 and yy[3] == (0, 0, 0, 1),
         "Y repetition rows")
    need(zz[0] == (1, 0, 0, 0) and zz[3] == (F(1, 4),) * 4,
         "Z repetition rows")

    # Antirepetition: each marginal has one common erasure output of mass 1/2
    # and one disjoint identifying output of mass 1/2 for each input.
    for channel in (yy, zz):
        r0, r1 = channel[1], channel[2]
        common = [i for i in range(4) if r0[i] == r1[i] == F(1, 2)]
        unique0 = [i for i in range(4) if r0[i] == F(1, 2) and r1[i] == 0]
        unique1 = [i for i in range(4) if r1[i] == F(1, 2) and r0[i] == 0]
        need(len(common) == len(unique0) == len(unique1) == 1,
             "antirepetition BEC structure")

    # Every adjacent pair has an input-independent coordinate and a varying
    # coordinate with exactly the original half-skew transition matrices.
    for a, b in adjacent:
        differing = 0 if (a // 2) != (b // 2) else 1
        for channel, base in ((yy, y), (zz, z)):
            for symbol in range(2):
                marginal_a = sum(channel[a][out] for out in range(4)
                                 if divmod(out, 2)[differing] == symbol)
                marginal_b = sum(channel[b][out] for out in range(4)
                                 if divmod(out, 2)[differing] == symbol)
                need((marginal_a, marginal_b) ==
                     (base[0][symbol], base[1][symbol]),
                     "adjacent varying-coordinate marginal")


def interval_certificate():
    q0 = Q("0.85")
    half = Q("0.5")
    jhalf = j_rep(half)
    d0 = j_rep(ONE - q0) - j_rep(q0)
    dp0 = -jp_rep(ONE - q0) - jp_rep(q0)

    need(jhalf.hi < D("0.549"), "J(1/2) coarse bound")
    need(dp0.hi < 0, "negative tangent slope")

    # A concave function is below its tangent. Since this tangent has negative
    # slope, its maximum on [1/2,1] is attained at the left endpoint.
    d_upper = UP.add(d0.hi,
                     UP.multiply(dp0.lo.copy_negate(), D("0.35")))
    need(d_upper < D("0.132"), "global |D| tangent bound")
    marton_upper = UP.add(jhalf.hi, UP.divide(d_upper, D(2)))
    need(marton_upper < D("0.615"), "repetition Marton bound")

    product_rtd_floor = D("0.7232857688439092")
    need(D("0.615") < product_rtd_floor,
         "strict separation from product RTD")
    return jhalf, d0, dp0, d_upper, marton_upper


def main():
    exact_orbit_audit()
    jhalf, d0, dp0, d_upper, marton_upper = interval_certificate()
    print("PASS: 6 support pairs = 4 adjacent + antirepetition + repetition")
    print("J_rep(1/2) =", f"[{jhalf.lo}, {jhalf.hi}]")
    print("D(17/20) =", f"[{d0.lo}, {d0.hi}]")
    print("D'(17/20) =", f"[{dp0.lo}, {dp0.hi}]")
    print("global max |D| upper =", d_upper)
    print("repetition Marton upper =", marton_upper)
    print("certified coarse headline < 0.615 < 0.7232857688439092")


if __name__ == "__main__":
    main()

</artifact>
</contribution>
<contribution>
ordinal: 15
transaction_id: 5ed3f525b9ae7f32c6e1dcbf22ecdb5ae946a4a6
contribution_id: conditional-product-marton-no-gain
author: Robert Raynor
<artifact path="problems/bssc-sum-capacity/contributions/conditional-product-marton-no-gain/README.md">
# Conditional-product Marton architectures have no multiletter gain

## Claim and scope

Let \(T:x\mapsto(Y,Z)\) be a finite two-receiver broadcast channel. For a
finite law \(P_{WUVX}\), write

\[
\begin{aligned}
M_T(P)&=\min\{I(W;Y),I(W;Z)\}
  +I(U;Y\mid W)+I(V;Z\mid W)-I(U;V\mid W),\\
L_{\alpha,T}(P)&=(1-\alpha)I(W;Y)+\alpha I(W;Z)
  +I(U;Y\mid W)+I(V;Z\mid W)-I(U;V\mid W),
\end{aligned}
\]

and let \(M_T=\sup_P M_T(P)\) and
\(L_{\alpha,T}=\sup_P L_{\alpha,T}(P)\). The suprema use the usual Markov
condition \((W,U,V)-X-(Y,Z)\).

Call \(T\) **receiver-skew** if there are an input involution
\(s:\mathcal X\to\mathcal X\) and output bijections
\(r_Y:\mathcal Y\to\mathcal Z\), \(r_Z:\mathcal Z\to\mathcal Y\) such that

\[
T_{Y\mid X}(y\mid x)=T_{Z\mid X}(r_Y(y)\mid s(x)),\qquad
T_{Z\mid X}(z\mid x)=T_{Y\mid X}(r_Z(z)\mid s(x)).
\tag{RS}
\]

Thus applying \(s\) to the input and relabeling the outputs exchanges the two
receiver marginal channels. Equivalently, every valid one-letter law has a
relabeled partner for which the roles of \((Y,U)\) and \((Z,V)\) are
exchanged. For the half-skew BSSC, \(s(x)=1-x\) and both output relabelings
are the bit flip \(b\mapsto1-b\).

For \(n\geq1\), define the conditional-product Marton class on
\(T^{\otimes n}\) by the laws

\[
P(w,u^n,v^n,x^n)
=P(w)\prod_{i=1}^n P_i(u_i,v_i,x_i\mid w),
\qquad
U=(U_1,\ldots,U_n),\quad V=(V_1,\ldots,V_n).
\tag{1}
\]

The common auxiliary \(W\) in (1) is completely arbitrary. It can carry a
joint schedule, use different coordinate laws for every \(w\), and correlate
all coordinates unconditionally. The sole structural restriction is that the
coordinate satellite/input packets \((U_i,V_i,X_i)\) are independent
conditioned on the actual \(W\) used by the Marton construction.

This contribution proves

\[
\boxed{
\sup_{P\text{ satisfying }(1)} M_{T^{\otimes n}}(P)=nM_T
}
\tag{2}
\]

for every finite receiver-skew broadcast channel \(T\) and every positive
integer \(n\). No attainment assumption is needed.

For the half-skew BSSC \(P\), (2) says in particular that the two-letter
conditional-product supremum is

\[
2M_P
=0.723285768843909231326883156301174\ldots
\quad\text{bits per two uses},
\]

using the governed one-letter Marton benchmark. Therefore any strict
two-letter BSSC gain must lie outside (1): it cannot be generated solely by
an arbitrary common \(W\) followed by conditionally independent coordinate
packets. A gaining witness must instead use a genuinely non-factorizable
cross-use satellite/input law given its common auxiliary: every chosen
coordinate-packet decomposition under which (1) could be tested must fail
that factorization. For the broader class with a chosen tuple decomposition
but otherwise arbitrarily correlated satellites and inputs, equation (11)
below gives an exact total-correlation ledger, and (13) is a strict necessary
correlation-balance test for any gain. The ledger depends on that chosen
decomposition.

## Relation to the August 2026 frontier

This contribution discharges the conditional-product structural-pruning
target in research direction `bssc-multiletter-marton-frontier`, registered by
canonical transaction `7e1e52fe42fde37ba1964ef9ae5062daf8bb55f8`.
That registration is program provenance, not a mathematical premise, so the
claim manifest declares no dependency on it.

Huang, Liu, and Liu,
[arXiv:2608.19869v1](https://arxiv.org/abs/2608.19869v1), prove that some
finite, nonbinary-input channels satisfy
\(M_{T^{\otimes2}}>2M_T\), while explicitly leaving binary-input tightness
open. Their equations (2)--(3) record the Marton and affine functionals above,
and the max--min identity displayed immediately afterward is

\[
M_T=\min_{\alpha\in[0,1]}L_{\alpha,T}.
\tag{3}
\]

The one-letter binary-input result of Nair, Wang, and Geng in the cited
arXiv v1,
[arXiv:1001.1468v1](https://arxiv.org/abs/1001.1468v1), proves that randomized
time division evaluates \(M_T\) for every binary-input channel. Equation (2)
does not merely take independent copies of that special optimizer: its upper
bound permits arbitrary one-letter \(U_i,V_i\) within every coordinate and an
arbitrary shared \(W\), and identifies conditional cross-use coupling as a
necessary ingredient for a gain.

Canonical transaction
f236017c62c67ce4218c1f81ea34134f0954b556 proves exact product additivity
for two *separately relaxed UV outer functionals*. The present result is
different: it applies directly to the joint Marton \(U,V,W\) functional, but
only on the conditional-product architecture (1). Neither theorem implies
the other. The canonical transaction is contextual comparison, not a premise
of the present proof.

## Proof

### 1. Receiver skew fixes the midpoint, self-containedly

For a candidate \(P\), abbreviate

\[
a=I(W;Y),\qquad b=I(W;Z),\qquad
S=I(U;Y\mid W)+I(V;Z\mid W)-I(U;V\mid W).
\]

Define its reflected candidate \(\widetilde P\) by

\[
(\widetilde W,\widetilde U,\widetilde V,\widetilde X)
=(W,V,U,s(X)).
\]

If \((\widetilde Y,\widetilde Z)\) are the channel outputs under this
candidate, (RS) and invariance of mutual information under bijective output
relabelings give

\[
\begin{aligned}
I(\widetilde W;\widetilde Y)&=b,&
I(\widetilde W;\widetilde Z)&=a,\\
I(\widetilde U;\widetilde Y\mid\widetilde W)
  &=I(V;Z\mid W),&
I(\widetilde V;\widetilde Z\mid\widetilde W)
  &=I(U;Y\mid W),\\
I(\widetilde U;\widetilde V\mid\widetilde W)
  &=I(U;V\mid W).
\end{aligned}
\]

Reflection is a bijection on the candidate laws. Thus
\(L_{\alpha,T}(\widetilde P)=L_{1-\alpha,T}(P)\), and taking suprema proves

\[
L_{\alpha,T}=L_{1-\alpha,T}.
\tag{4}
\]

The equality needed below follows without a minimax premise. Pointwise,
\(\min\{a,b\}\leq(a+b)/2\), so \(M_T\leq L_{1/2,T}\). For the converse, let a
fair bit \(Q\) select \(P\) or \(\widetilde P\), and include the selector in
the common auxiliary:

\[
W'=(Q,W_Q),\qquad U'=U_Q,\qquad V'=V_Q,\qquad X'=X_Q.
\]

The alphabets in the two branches may be placed in disjoint tagged copies, so
this is a valid finite Marton law even when the original \(U,V\) alphabets
differ. Because \(W'\) reveals the branch, its satellite term is exactly
\(\tfrac12(S+S)=S\), while

\[
\begin{aligned}
I(W';Y)&=I(Q;Y)+I(W_Q;Y\mid Q)
       =I(Q;Y)+\tfrac12(a+b)\geq\tfrac12(a+b),\\
I(W';Z)&=I(Q;Z)+I(W_Q;Z\mid Q)
       =I(Q;Z)+\tfrac12(a+b)\geq\tfrac12(a+b).
\end{aligned}
\]

Therefore \(M_T(P')\geq(a+b)/2+S=L_{1/2,T}(P)\). This construction works for
every \(P\), so taking suprema gives the reverse inequality and hence

\[
M_T=L_{1/2,T}.
\tag{5}
\]

There is no attainment assumption. As an independent check, \(L_{\alpha,T}\)
is convex as a supremum of affine functions, and (4) makes \(1/2\) a
minimizer; combining that observation with the published max--min identity
(3) gives the same conclusion. Equation (3) is therefore cited context, not a
premise of this proof.

### 2. Conditional terms add exactly, pointwise in \(W\)

Fix a law of the form (1). Conditional on every positive-probability value
\(W=w\), the memoryless product channel and (1) give

\[
P(u^n,v^n,x^n,y^n,z^n\mid w)
=\prod_{i=1}^n
P_i(u_i,v_i,x_i\mid w)T(y_i,z_i\mid x_i).
\tag{6}
\]

Thus the coordinate pairs \((U_i,Y_i)\), the coordinate pairs \((V_i,Z_i)\),
and the coordinate pairs \((U_i,V_i)\) are each independent across \(i\)
conditioned on \(W=w\). Additivity of entropy for product laws gives,
pointwise in \(w\),

\[
\begin{aligned}
I(U^n;Y^n\mid W=w)&=\sum_i I(U_i;Y_i\mid W=w),\\
I(V^n;Z^n\mid W=w)&=\sum_i I(V_i;Z_i\mid W=w),\\
I(U^n;V^n\mid W=w)&=\sum_i I(U_i;V_i\mid W=w).
\end{aligned}
\tag{7}
\]

Averaging (7) over \(w\) proves the same three identities conditioned on
\(W\). This is exact, rather than an inequality or an asymptotic
single-letterization.

### 3. The common term is subadditive

Equation (6) also makes \(Y_1,\ldots,Y_n\) conditionally independent given
\(W\). Hence

\[
\begin{aligned}
I(W;Y^n)
&=H(Y^n)-H(Y^n\mid W)\\
&\leq\sum_iH(Y_i)-\sum_iH(Y_i\mid W)
=\sum_iI(W;Y_i).
\end{aligned}
\tag{8}
\]

The same proof gives \(I(W;Z^n)\leq\sum_iI(W;Z_i)\). Using
\(\min\{a,b\}\leq(a+b)/2\), then (7)--(8), gives

\[
\begin{aligned}
M_{T^{\otimes n}}(P)
&\leq \tfrac12 I(W;Y^n)+\tfrac12 I(W;Z^n)
  +I(U^n;Y^n\mid W)+I(V^n;Z^n\mid W)-I(U^n;V^n\mid W)\\
&\leq\sum_{i=1}^n\Big[
  \tfrac12 I(W;Y_i)+\tfrac12 I(W;Z_i)
  +I(U_i;Y_i\mid W)+I(V_i;Z_i\mid W)-I(U_i;V_i\mid W)
\Big].
\end{aligned}
\tag{9}
\]

For every \(i\), the marginal \(P_{WU_iV_iX_i}\) is an admissible one-letter
Marton law for \(T\). Its bracket in (9) is therefore at most
\(L_{1/2,T}=M_T\) by (5). This proves the upper bound in (2).

### 4. An exact correlation ledger beyond the product class

The preceding bound has a sign-exact refinement that also identifies what a
correlated witness would have to overcome. Consider the broader
**tuple-auxiliary class** consisting of every finite law
\(P(w,u^n,v^n,x^n)\), with the explicit aggregate representation
\(U=(U_1,\ldots,U_n)\), \(V=(V_1,\ldots,V_n)\), followed by the product
channel:

\[
P(w,u^n,v^n,x^n,y^n,z^n)
=P(w,u^n,v^n,x^n)\prod_iT(y_i,z_i\mid x_i).
\tag{10}
\]

Unlike (1), equation (10) permits arbitrary conditional cross-use correlation
among the satellite pairs and arbitrary cross-use input dependence; in
particular, \(X_i\) may depend on all of \(U^n,V^n,W\). Any finite abstract
auxiliaries \(U,V\) admit such a tuple representation by placing the whole
variable in one coordinate and padding the others with constants. The
representation is noncanonical, however, and every term in the ledger below
is evaluated relative to the particular decomposition chosen. For a vector
\(A^n\), define

\[
\operatorname{TC}(A^n\mid C)
=\sum_iH(A_i\mid C)-H(A^n\mid C),
\qquad
\operatorname{TC}(A^n)
=\sum_iH(A_i)-H(A^n),
\]

and define the cross-conditioning gaps

\[
\begin{aligned}
G_{UY}&=\sum_iH(Y_i\mid U_i,W)-H(Y^n\mid U^n,W),\\
G_{VZ}&=\sum_iH(Z_i\mid V_i,W)-H(Z^n\mid V^n,W),\\
G_{UV}&=\sum_iH(U_i\mid V_i,W)-H(U^n\mid V^n,W).
\end{aligned}
\]

Each displayed total correlation and gap is nonnegative by entropy
subadditivity and conditioning. Let \(P^{(i)}\) denote the coordinate marginal
\(P_{WU_iV_iX_i}\), which is a valid one-letter Marton law because the
memoryless channel makes \((W,U_i,V_i)-X_i-(Y_i,Z_i)\) even when the input law
in (10) is globally coupled. Direct entropy expansion gives the exact
identity

\[
\begin{aligned}
&L_{1/2,T^{\otimes n}}(P)
 -\sum_iL_{1/2,T}(P^{(i)})\\
&\quad=\operatorname{TC}(U^n\mid W)+G_{UY}+G_{VZ}-G_{UV}\\
&\qquad\quad-\tfrac12\big[
 \operatorname{TC}(Y^n\mid W)+\operatorname{TC}(Y^n)
 +\operatorname{TC}(Z^n\mid W)+\operatorname{TC}(Z^n)
\big].
\tag{11}
\end{aligned}
\]

Indeed, the common-\(Y\), private-\(UY\), and penalty differences are,
respectively,

\[
\begin{aligned}
I(W;Y^n)-\sum_iI(W;Y_i)
  &=\operatorname{TC}(Y^n\mid W)-\operatorname{TC}(Y^n),\\
I(U^n;Y^n\mid W)-\sum_iI(U_i;Y_i\mid W)
  &=-\operatorname{TC}(Y^n\mid W)+G_{UY},\\
-I(U^n;V^n\mid W)+\sum_iI(U_i;V_i\mid W)
  &=\operatorname{TC}(U^n\mid W)-G_{UV}.
\end{aligned}
\]

The \(Z\) expansions are identical. Summing them with the half weights proves
(11). This identity itself uses only the tuple representation and product
channel, not receiver skew; the gain implication below additionally uses
(5). The apparently asymmetric penalty representation is harmless: if
\(G_{VU}=\sum_iH(V_i\mid U_i,W)-H(V^n\mid U^n,W)\), then

\[
\operatorname{TC}(U^n\mid W)-G_{UV}
=\sum_iI(U_i;V_i\mid W)-I(U^n;V^n\mid W)
=\operatorname{TC}(V^n\mid W)-G_{VU}.
\]

For a conditional-product law (1), every conditional total correlation and
every \(G\)-gap in (11) vanishes. Thus (11) reduces to

\[
L_{1/2,T^{\otimes n}}(P)
=\sum_iL_{1/2,T}(P^{(i)})
 -\tfrac12\big[\operatorname{TC}(Y^n)+\operatorname{TC}(Z^n)\big],
\tag{12}
\]

which sharpens (9) and makes its only possible slack explicit.

More generally, if a tuple-auxiliary law (10) gives
\(M_{T^{\otimes n}}(P)>nM_T\), then
\(M_{T^{\otimes n}}(P)\leq L_{1/2,T^{\otimes n}}(P)\) and
\(\sum_iL_{1/2,T}(P^{(i)})\leq nM_T\). Equation (11) therefore forces the strict
necessary condition

\[
\operatorname{TC}(U^n\mid W)+G_{UY}+G_{VZ}-G_{UV}
>\tfrac12\big[
 \operatorname{TC}(Y^n\mid W)+\operatorname{TC}(Y^n)
 +\operatorname{TC}(Z^n\mid W)+\operatorname{TC}(Z^n)
\big].
\tag{13}
\]

This correlation-balance test is not sufficient for a gain, but it gives a
human-checkable pruning condition for the remaining nonproduct search.

### 5. Independent copies prove the reverse inequality

Let \(\varepsilon>0\) and choose a finite one-letter law \(P^*_{WUVX}\) with

\[
M_T(P^*)>M_T-\varepsilon.
\]

Take \(n\) independent copies, put the copy-wise common variables into the
single aggregate common auxiliary \(W=(W_1,\ldots,W_n)\), and use
\(U=(U_1,\ldots,U_n)\), \(V=(V_1,\ldots,V_n)\). Conditional on aggregate
\(W\), the coordinate packets factor exactly as in (1). Full independence
across copies makes both common mutual informations and all three conditional
terms additive, so

\[
M_{T^{\otimes n}}((P^*)^{\otimes n})=nM_T(P^*)
>nM_T-n\varepsilon.
\]

Letting \(\varepsilon\downarrow0\) proves the reverse inequality in (2). This
argument uses an epsilon-optimizer and therefore does not assume that the
one-letter supremum is attained.

## Deterministic corroboration

Run from this contribution directory:

    PYTHONDONTWRITEBYTECODE=1 python3 verify_conditional_product.py

verification.json requests the same networkless standard-library entrypoint.
The script checks the exact rational BSSC receiver-skew relabeling, then uses
a fixed seed to construct finite conditional-product laws and mechanically
checks (7), (8), and (9). It separately constructs independent copies of a
one-letter law and checks equality of the complete Marton functional. A
second fixed-seed family has arbitrary correlated tuple satellites and
inputs; it checks both sides of (11), nonnegativity of every displayed gap,
and the symmetric \(U\)-versus-\(V\) representation of the penalty term.

These finite floating-point checks are corroboration only. The universal
theorem rests on the symmetrization proof and entropy identities above; the
verifier does not exhaust arbitrary alphabets or certify any optimizing law.

## Limitations and provenance

- Equation (2) does **not** establish unrestricted additivity
  \(M_{T^{\otimes n}}=nM_T\). In particular it does not resolve the open
  binary-input or BSSC tightness question highlighted in arXiv:2608.19869v1.
- The equality theorem (2) does not cover conditionally coupled coordinate
  packets. The ledger (11) does cover arbitrary coupling after any chosen
  tuple representation, including trivial constant padding, but gives only a
  necessary correlation-balance test, not a no-gain result. Its numerical and
  pruning usefulness can change with the noncanonical decomposition.
- It does not improve either endpoint of the governed BSSC capacity interval
  and gives no capacity converse.
- The max--min identity (3) is external published context, explicitly
  attributed above, but it is not a premise. The receiver-skew midpoint
  equality, conditional-product theorem, and correlation ledger are proved
  internally.
- Rates in this contribution use bits, while arXiv:2608.19869v1 uses natural
  logarithms. Every identity is invariant under this common positive scale.

The theorem and proof were derived for this Math Flow contribution by an
OpenAI Codex research agent under Robert Raynor's direction. The two cited
papers retain authorship of their results; no part of their counterexample is
claimed here.

</artifact>
<artifact path="problems/bssc-sum-capacity/contributions/conditional-product-marton-no-gain/claims.json">
{
  "schemaVersion": 1,
  "claims": [
    {
      "claimKey": "bssc-sum-capacity/conditional-product-marton-no-gain",
      "statement": "Let T be any finite receiver-skew two-receiver broadcast channel, and let M_T be its one-letter private-message Marton sum-rate. For every n >= 1, the supremum of the n-letter Marton functional over laws P(w,u^n,v^n,x^n)=P(w) product_i P_i(u_i,v_i,x_i|w), with aggregate U=(U_i) and V=(V_i), equals n M_T. The common W is arbitrary and may correlate coordinates unconditionally. Consequently, any strict two-letter gain for the half-skew BSSC must use a law outside this conditional-product class: every chosen coordinate-packet decomposition under which the factorization could be tested must fail it. For the broader class of arbitrary finite tuple laws P(w,u^n,v^n,x^n), with a chosen aggregate U=(U_i), V=(V_i) and the product channel, the exact total-correlation residual identity in README equation (11) holds, so any strict gain must satisfy the correlation-balance inequality (13) for that decomposition. Trivial constant padding always supplies a tuple representation, but the ledger and its pruning usefulness depend on the noncanonical decomposition. These results do not establish unrestricted Marton additivity, binary-input tightness, a capacity bound, or the exact BSSC capacity.",
      "dependencyTransactionIds": []
    }
  ]
}

</artifact>
<artifact path="problems/bssc-sum-capacity/contributions/conditional-product-marton-no-gain/verification.json">
{
  "schemaVersion": 1,
  "verifier": {
    "id": "python-stdlib-3-13-v1",
    "specDigest": "sha256:fc7ed06b77396fabc1da84694b4d8a08800843f41ad8ca4b9cd666b67ba60884"
  },
  "entrypoint": "verify_conditional_product.py",
  "arguments": []
}

</artifact>
<artifact path="problems/bssc-sum-capacity/contributions/conditional-product-marton-no-gain/verify_conditional_product.py">
#!/usr/bin/env python3
"""Mechanical corroboration for the Marton entropy identities.

The universal theorem is analytic.  This deterministic standard-library
script checks its finite-alphabet entropy bookkeeping on fixed-seed examples
and verifies the exact half-skew BSSC receiver relabeling.  It also checks the
exact total-correlation ledger on arbitrary correlated tuple laws.
"""

from __future__ import annotations

from collections import defaultdict
from fractions import Fraction
from math import log2
from random import Random
from typing import Hashable, Iterable


TOL = 2e-11

Y_CHANNEL = (
    (Fraction(1, 2), Fraction(1, 2)),
    (Fraction(0), Fraction(1)),
)
Z_CHANNEL = (
    (Fraction(1), Fraction(0)),
    (Fraction(1, 2), Fraction(1, 2)),
)


def entropy(joint: dict[tuple[Hashable, ...], float], positions: Iterable[int]) -> float:
    selected = tuple(positions)
    marginal: dict[tuple[Hashable, ...], float] = defaultdict(float)
    for outcome, probability in joint.items():
        marginal[tuple(outcome[i] for i in selected)] += probability
    return -sum(p * log2(p) for p in marginal.values() if p > 0.0)


def mutual_information(
    joint: dict[tuple[Hashable, ...], float],
    left: Iterable[int],
    right: Iterable[int],
) -> float:
    left = tuple(left)
    right = tuple(right)
    return entropy(joint, left) + entropy(joint, right) - entropy(joint, left + right)


def conditional_mutual_information(
    joint: dict[tuple[Hashable, ...], float],
    left: Iterable[int],
    right: Iterable[int],
    given: Iterable[int],
) -> float:
    left = tuple(left)
    right = tuple(right)
    given = tuple(given)
    return (
        entropy(joint, left + given)
        + entropy(joint, right + given)
        - entropy(joint, given)
        - entropy(joint, left + right + given)
    )


def conditional_entropy(
    joint: dict[tuple[Hashable, ...], float],
    target: Iterable[int],
    given: Iterable[int] = (),
) -> float:
    target = tuple(target)
    given = tuple(given)
    if not given:
        return entropy(joint, target)
    return entropy(joint, target + given) - entropy(joint, given)


def total_correlation(
    joint: dict[tuple[Hashable, ...], float],
    coordinate_groups: Iterable[Iterable[int]],
    given: Iterable[int] = (),
) -> float:
    groups = tuple(tuple(group) for group in coordinate_groups)
    flattened = tuple(position for group in groups for position in group)
    return sum(conditional_entropy(joint, group, given) for group in groups) - (
        conditional_entropy(joint, flattened, given)
    )


def normalized_weights(rng: Random, count: int) -> tuple[float, ...]:
    weights = [rng.randrange(1, 100) for _ in range(count)]
    total = sum(weights)
    return tuple(weight / total for weight in weights)


PACKETS = tuple((u, v, x) for u in range(2) for v in range(2) for x in range(2))


def random_one_letter_law(
    rng: Random,
) -> tuple[dict[Hashable, float], dict[Hashable, dict[tuple[int, int, int], float]]]:
    w_values: tuple[Hashable, ...] = (0, 1)
    p_w_values = normalized_weights(rng, len(w_values))
    p_w = dict(zip(w_values, p_w_values, strict=True))
    conditionals: dict[Hashable, dict[tuple[int, int, int], float]] = {}
    for w in w_values:
        probabilities = normalized_weights(rng, len(PACKETS))
        conditionals[w] = dict(zip(PACKETS, probabilities, strict=True))
    return p_w, conditionals


def build_two_letter_base(
    p_w: dict[Hashable, float],
    first: dict[Hashable, dict[tuple[int, int, int], float]],
    second: dict[Hashable, dict[tuple[int, int, int], float]],
) -> dict[tuple[Hashable, ...], float]:
    # Tuple order: w,u1,v1,x1,u2,v2,x2.
    joint: dict[tuple[Hashable, ...], float] = {}
    for w, pw in p_w.items():
        for (u1, v1, x1), p1 in first[w].items():
            for (u2, v2, x2), p2 in second[w].items():
                joint[(w, u1, v1, x1, u2, v2, x2)] = pw * p1 * p2
    return joint


def random_correlated_tuple_base(
    rng: Random,
) -> dict[tuple[Hashable, ...], float]:
    """Build an arbitrary p(w,u1,v1,x1,u2,v2,x2)."""

    w_values: tuple[Hashable, ...] = (0, 1)
    p_w = dict(
        zip(w_values, normalized_weights(rng, len(w_values)), strict=True)
    )
    tuple_values = tuple(first + second for first in PACKETS for second in PACKETS)
    joint: dict[tuple[Hashable, ...], float] = {}
    for w, pw in p_w.items():
        conditional = dict(
            zip(
                tuple_values,
                normalized_weights(rng, len(tuple_values)),
                strict=True,
            )
        )
        for packet_pair, probability in conditional.items():
            joint[(w,) + packet_pair] = pw * probability
    return joint


def append_outputs(
    base: dict[tuple[Hashable, ...], float],
    channel: tuple[tuple[Fraction, Fraction], tuple[Fraction, Fraction]],
) -> dict[tuple[Hashable, ...], float]:
    # Output tuple order: base followed by o1,o2.
    joint: dict[tuple[Hashable, ...], float] = {}
    for outcome, probability in base.items():
        x1, x2 = int(outcome[3]), int(outcome[6])
        for o1 in range(2):
            for o2 in range(2):
                p = probability * float(channel[x1][o1] * channel[x2][o2])
                if p:
                    joint[outcome + (o1, o2)] = p
    return joint


def append_one_output(
    base: dict[tuple[Hashable, ...], float],
    channel: tuple[tuple[Fraction, Fraction], tuple[Fraction, Fraction]],
) -> dict[tuple[Hashable, ...], float]:
    # Input tuple order: w,u,v,x; output is appended at position 4.
    joint: dict[tuple[Hashable, ...], float] = {}
    for outcome, probability in base.items():
        x = int(outcome[3])
        for output in range(2):
            p = probability * float(channel[x][output])
            if p:
                joint[outcome + (output,)] = p
    return joint


def two_letter_terms(
    base: dict[tuple[Hashable, ...], float],
) -> dict[str, float]:
    y_joint = append_outputs(base, Y_CHANNEL)
    z_joint = append_outputs(base, Z_CHANNEL)

    common_y = mutual_information(y_joint, (0,), (7, 8))
    common_z = mutual_information(z_joint, (0,), (7, 8))
    common_y_sum = sum(mutual_information(y_joint, (0,), (i,)) for i in (7, 8))
    common_z_sum = sum(mutual_information(z_joint, (0,), (i,)) for i in (7, 8))

    u_y = conditional_mutual_information(y_joint, (1, 4), (7, 8), (0,))
    u_y_sum = (
        conditional_mutual_information(y_joint, (1,), (7,), (0,))
        + conditional_mutual_information(y_joint, (4,), (8,), (0,))
    )
    v_z = conditional_mutual_information(z_joint, (2, 5), (7, 8), (0,))
    v_z_sum = (
        conditional_mutual_information(z_joint, (2,), (7,), (0,))
        + conditional_mutual_information(z_joint, (5,), (8,), (0,))
    )
    u_v = conditional_mutual_information(base, (1, 4), (2, 5), (0,))
    u_v_sum = (
        conditional_mutual_information(base, (1,), (2,), (0,))
        + conditional_mutual_information(base, (4,), (5,), (0,))
    )

    marton = min(common_y, common_z) + u_y + v_z - u_v
    affine_half = (common_y + common_z) / 2 + u_y + v_z - u_v
    coordinate_sum = (
        (common_y_sum + common_z_sum) / 2 + u_y_sum + v_z_sum - u_v_sum
    )
    return {
        "common_y": common_y,
        "common_z": common_z,
        "common_y_sum": common_y_sum,
        "common_z_sum": common_z_sum,
        "u_y": u_y,
        "u_y_sum": u_y_sum,
        "v_z": v_z,
        "v_z_sum": v_z_sum,
        "u_v": u_v,
        "u_v_sum": u_v_sum,
        "marton": marton,
        "affine_half": affine_half,
        "coordinate_sum": coordinate_sum,
    }


def correlation_ledger_terms(
    base: dict[tuple[Hashable, ...], float],
) -> dict[str, float]:
    """Evaluate both sides of the exact two-letter residual identity."""

    y_joint = append_outputs(base, Y_CHANNEL)
    z_joint = append_outputs(base, Z_CHANNEL)
    marton_terms = two_letter_terms(base)

    tc_u_w = total_correlation(base, ((1,), (4,)), (0,))
    tc_v_w = total_correlation(base, ((2,), (5,)), (0,))
    tc_y_w = total_correlation(y_joint, ((7,), (8,)), (0,))
    tc_z_w = total_correlation(z_joint, ((7,), (8,)), (0,))
    tc_y = total_correlation(y_joint, ((7,), (8,)))
    tc_z = total_correlation(z_joint, ((7,), (8,)))

    g_u_y = (
        conditional_entropy(y_joint, (7,), (1, 0))
        + conditional_entropy(y_joint, (8,), (4, 0))
        - conditional_entropy(y_joint, (7, 8), (1, 4, 0))
    )
    g_v_z = (
        conditional_entropy(z_joint, (7,), (2, 0))
        + conditional_entropy(z_joint, (8,), (5, 0))
        - conditional_entropy(z_joint, (7, 8), (2, 5, 0))
    )
    g_u_v = (
        conditional_entropy(base, (1,), (2, 0))
        + conditional_entropy(base, (4,), (5, 0))
        - conditional_entropy(base, (1, 4), (2, 5, 0))
    )
    g_v_u = (
        conditional_entropy(base, (2,), (1, 0))
        + conditional_entropy(base, (5,), (4, 0))
        - conditional_entropy(base, (2, 5), (1, 4, 0))
    )

    residual = (
        tc_u_w
        + g_u_y
        + g_v_z
        - g_u_v
        - 0.5 * (tc_y_w + tc_y + tc_z_w + tc_z)
    )
    return {
        "delta": marton_terms["affine_half"] - marton_terms["coordinate_sum"],
        "residual": residual,
        "tc_u_w": tc_u_w,
        "tc_v_w": tc_v_w,
        "tc_y_w": tc_y_w,
        "tc_z_w": tc_z_w,
        "tc_y": tc_y,
        "tc_z": tc_z,
        "g_u_y": g_u_y,
        "g_v_z": g_v_z,
        "g_u_v": g_u_v,
        "g_v_u": g_v_u,
    }


def one_letter_marton(
    p_w: dict[Hashable, float],
    conditional: dict[Hashable, dict[tuple[int, int, int], float]],
) -> float:
    base: dict[tuple[Hashable, ...], float] = {}
    for w, pw in p_w.items():
        for (u, v, x), pc in conditional[w].items():
            base[(w, u, v, x)] = pw * pc
    y_joint = append_one_output(base, Y_CHANNEL)
    z_joint = append_one_output(base, Z_CHANNEL)
    common_y = mutual_information(y_joint, (0,), (4,))
    common_z = mutual_information(z_joint, (0,), (4,))
    u_y = conditional_mutual_information(y_joint, (1,), (4,), (0,))
    v_z = conditional_mutual_information(z_joint, (2,), (4,), (0,))
    u_v = conditional_mutual_information(base, (1,), (2,), (0,))
    return min(common_y, common_z) + u_y + v_z - u_v


def assert_close(left: float, right: float, label: str) -> None:
    if abs(left - right) > TOL:
        raise AssertionError(f"{label}: {left!r} != {right!r}")


def verify_skew() -> None:
    for x in range(2):
        for output in range(2):
            assert Y_CHANNEL[1 - x][output] == Z_CHANNEL[x][1 - output]
            assert Z_CHANNEL[1 - x][output] == Y_CHANNEL[x][1 - output]


def verify_random_conditional_products() -> None:
    rng = Random(260819869)
    for trial in range(24):
        p_w, first = random_one_letter_law(rng)
        _, second = random_one_letter_law(rng)
        base = build_two_letter_base(p_w, first, second)
        terms = two_letter_terms(base)

        assert_close(terms["u_y"], terms["u_y_sum"], f"trial {trial}: U/Y")
        assert_close(terms["v_z"], terms["v_z_sum"], f"trial {trial}: V/Z")
        assert_close(terms["u_v"], terms["u_v_sum"], f"trial {trial}: U/V")
        assert terms["common_y"] <= terms["common_y_sum"] + TOL
        assert terms["common_z"] <= terms["common_z_sum"] + TOL
        assert terms["marton"] <= terms["affine_half"] + TOL
        assert terms["affine_half"] <= terms["coordinate_sum"] + TOL

        ledger = correlation_ledger_terms(base)
        assert_close(ledger["delta"], ledger["residual"], f"trial {trial}: ledger")
        for label in (
            "tc_u_w",
            "tc_y_w",
            "tc_z_w",
            "g_u_y",
            "g_v_z",
            "g_u_v",
        ):
            assert_close(ledger[label], 0.0, f"trial {trial}: product {label}")
        expected_delta = -0.5 * (ledger["tc_y"] + ledger["tc_z"])
        assert_close(ledger["delta"], expected_delta, f"trial {trial}: deficit")


def verify_correlated_ledger() -> None:
    rng = Random(110260819869)
    largest_delta = 0.0
    for trial in range(24):
        base = random_correlated_tuple_base(rng)
        ledger = correlation_ledger_terms(base)
        assert_close(
            ledger["delta"],
            ledger["residual"],
            f"correlated trial {trial}: ledger",
        )
        assert_close(
            ledger["tc_u_w"] - ledger["g_u_v"],
            ledger["tc_v_w"] - ledger["g_v_u"],
            f"correlated trial {trial}: symmetric penalty",
        )
        for label in (
            "tc_u_w",
            "tc_v_w",
            "tc_y_w",
            "tc_z_w",
            "tc_y",
            "tc_z",
            "g_u_y",
            "g_v_z",
            "g_u_v",
            "g_v_u",
        ):
            if ledger[label] < -TOL:
                raise AssertionError(
                    f"correlated trial {trial}: negative {label}={ledger[label]!r}"
                )
        largest_delta = max(largest_delta, abs(ledger["delta"]))
    if largest_delta < 1e-6:
        raise AssertionError("correlated ledger trials were numerically trivial")


def verify_independent_copy_equality() -> None:
    rng = Random(10011468)
    p_w_one, conditional_one = random_one_letter_law(rng)
    one = one_letter_marton(p_w_one, conditional_one)

    p_w_pair: dict[tuple[Hashable, Hashable], float] = {}
    first: dict[tuple[Hashable, Hashable], dict[tuple[int, int, int], float]] = {}
    second: dict[tuple[Hashable, Hashable], dict[tuple[int, int, int], float]] = {}
    for w1, p1 in p_w_one.items():
        for w2, p2 in p_w_one.items():
            pair = (w1, w2)
            p_w_pair[pair] = p1 * p2
            first[pair] = conditional_one[w1]
            second[pair] = conditional_one[w2]

    base = build_two_letter_base(p_w_pair, first, second)
    two = two_letter_terms(base)["marton"]
    assert_close(two, 2 * one, "independent-copy Marton equality")


def main() -> None:
    verify_skew()
    verify_random_conditional_products()
    verify_correlated_ledger()
    verify_independent_copy_equality()
    print("PASS: exact BSSC receiver-skew relabeling")
    print("PASS: conditional-product entropy identities and common-term bounds")
    print("PASS: exact total-correlation ledger on correlated tuple laws")
    print("PASS: independent-copy Marton equality")


if __name__ == "__main__":
    main()

</artifact>
</contribution>
<contribution>
ordinal: 16
transaction_id: eb2d5550bc7af1f971c00c8246e4f951634c1ecb
contribution_id: two-letter-padding-correlation-tests
author: Robert Raynor
<artifact path="problems/bssc-sum-capacity/contributions/two-letter-padding-correlation-tests/README.md">
# Four padding-correlation tests for a two-letter Marton gain

## Claim and dependency boundary

Let \(T\) be a finite receiver-skew two-receiver broadcast channel, let \(M_T\)
be its one-letter private-message Marton sum functional, and consider an
arbitrary finite two-letter Marton law

\[
 P(w,u,v,x_1,x_2)T(y_1,z_1\mid x_1)T(y_2,z_2\mid x_2).
\tag{1}
\]

The auxiliaries \(U,V\) in (1) are abstract: no product or tuple structure is
assumed.  This contribution is a direct specialization of the exact
tuple-law residual and gain implication in canonical transaction
`5ed3f525b9ae7f32c6e1dcbf22ecdb5ae946a4a6`
(`conditional-product-marton-no-gain`), which is the sole declared logical
dependency.

Put

\[
\begin{aligned}
A_1&=I(Y_2;Y_1,U\mid W),&
A_2&=I(Y_1;Y_2,U\mid W),\\
B_1&=I(Z_2;Z_1,V\mid W),&
B_2&=I(Z_1;Z_2,V\mid W),\\
D&=I(U;V\mid W),
\end{aligned}
\tag{2}
\]

and let the output-correlation charge be

\[
C=\frac12\left[
 I(Y_1;Y_2\mid W)+I(Y_1;Y_2)
 +I(Z_1;Z_2\mid W)+I(Z_1;Z_2)
\right].
\tag{3}
\]

If the law (1) gives a strict two-letter gain,

\[
 M_{T^{\otimes2}}(P)>2M_T,
\tag{4}
\]

then all four strict inequalities

\[
\boxed{
 A_a+B_b>C+\mathbf 1\{a\ne b\}D,
 \qquad (a,b)\in\{1,2\}^2
}
\tag{5}
\]

must hold.  Equivalently,

\[
\min\{A_1+B_1,\ A_2+B_2,\ A_1+B_2-D,\ A_2+B_1-D\}>C.
\tag{6}
\]

Thus failure of even one test in (5) rigorously rules out a gain for that
law.  Under the published binary-input evaluation, the half-skew BSSC has
\(2M_T=2L_{\rm RTD}\), so the tests apply to every candidate above the current
two-letter Marton baseline.  They neither
prove that any law passing the tests gains nor establish unrestricted
additivity.

## Proof by four constant paddings

For \(a\in\{1,2\}\), represent the abstract auxiliary \(U\) as a tuple by
putting \(U_a=U\) and making \(U_{3-a}\) constant.  Independently, for
\(b\in\{1,2\}\), put \(V_b=V\) and make \(V_{3-b}\) constant.  This gives four
legitimate tuple decompositions of the same law (1).  The dependency's exact
residual identity may be applied to every one of them.

For each \(a\), constant padding gives

\[
 \operatorname{TC}(U_1,U_2\mid W)=0
\]

and the dependency's \(G_{UY}\) term becomes

\[
\begin{aligned}
G_{UY}^{(1)}
 &=H(Y_1\mid U,W)+H(Y_2\mid W)-H(Y_1,Y_2\mid U,W)\\
 &=I(Y_2;Y_1,U\mid W)=A_1,\\
G_{UY}^{(2)}
 &=I(Y_1;Y_2,U\mid W)=A_2.
\end{aligned}
\tag{7}
\]

The identical calculation on the other receiver gives

\[
G_{VZ}^{(1)}=B_1,
\qquad
G_{VZ}^{(2)}=B_2.
\tag{8}
\]

The auxiliary cross-gap distinguishes aligned and crossed padding.  If
\(a=b\), both nonconstant auxiliaries occupy the same coordinate and

\[
G_{UV}^{(a,a)}=0.
\]

If \(a\ne b\), they occupy different coordinates and

\[
\begin{aligned}
G_{UV}^{(a,b)}
 &=H(U\mid W)-H(U\mid V,W)\\
 &=I(U;V\mid W)=D.
\end{aligned}
\tag{9}
\]

For two coordinates, each output total correlation in the dependency is an
ordinary mutual information:

\[
\operatorname{TC}(Y_1,Y_2\mid W)=I(Y_1;Y_2\mid W),
\qquad
\operatorname{TC}(Y_1,Y_2)=I(Y_1;Y_2),
\tag{10}
\]

and similarly for \(Z\).  Substitution of (7)--(10) into the exact residual
therefore yields, for each padding pair,

\[
L_{1/2,T^{\otimes2}}(P)
-\sum_{i=1}^2L_{1/2,T}(P_i^{(a,b)})
=A_a+B_b-\mathbf1\{a\ne b\}D-C.
\tag{11}
\]

The dependency proves that (4) forces the left side of (11) to be strictly
positive for every chosen tuple decomposition.  Applying it to all four
paddings proves (5)--(6).

## A combined crossed-padding obstruction

Adding the two crossed tests \((a,b)=(1,2),(2,1)\) gives a sometimes more
convenient necessary condition.  By the chain rule,

\[
\begin{aligned}
A_1+A_2
 &=2I(Y_1;Y_2\mid W)
 +I(U;Y_2\mid Y_1,W)+I(U;Y_1\mid Y_2,W),\\
B_1+B_2
 &=2I(Z_1;Z_2\mid W)
 +I(V;Z_2\mid Z_1,W)+I(V;Z_1\mid Z_2,W).
\end{aligned}
\]

Consequently every gain also requires

\[
\begin{aligned}
&I(Y_1;Y_2\mid W)+I(Z_1;Z_2\mid W)
-I(Y_1;Y_2)-I(Z_1;Z_2)\\
&\quad+I(U;Y_2\mid Y_1,W)+I(U;Y_1\mid Y_2,W)\\
&\quad+I(V;Z_2\mid Z_1,W)+I(V;Z_1\mid Z_2,W)
>2I(U;V\mid W).
\end{aligned}
\tag{12}
\]

Equation (12) is weaker than retaining both crossed tests separately, but it
makes the competition transparent: cross-coordinate satellite information
and conditional output correlation must overcome both unconditional output
correlation and twice the Marton auxiliary penalty.

## Deterministic corroboration

Run from this contribution directory using only the Python standard library:

```text
python3 -I -B verify_padding_tests.py
```

The checker constructs a strictly positive, correlated rational law on
\((W,U,V,X_1,X_2)\), passes it through the exact half-skew BSSC product
marginals, and evaluates all information quantities in two independent ways.
For every one of the four padding pairs, it compares the complete two-letter
minus coordinatewise \(L_{1/2}\) difference with the right side of (11).  It
also checks the chain-rule reduction to (12).  These finite numerical checks
corroborate the identities; the universal result rests on the displayed
entropy proof and its declared dependency.

## Scope and authorship

- The result is a necessary filter for a fixed two-letter Marton law, not a
  sufficient condition or an optimization theorem.
- Passing all four inequalities does not imply a gain.
- The tests do not restrict support size or auxiliary cardinality and do not
  determine BSSC capacity.
- The specialization and checker were prepared by an OpenAI Codex solver
  agent at Robert Raynor's request.

</artifact>
<artifact path="problems/bssc-sum-capacity/contributions/two-letter-padding-correlation-tests/claims.json">
{
  "schemaVersion": 1,
  "claims": [
    {
      "claimKey": "bssc-sum-capacity/two-letter-padding-correlation-tests",
      "statement": "Assume canonical transaction 5ed3f525b9ae7f32c6e1dcbf22ecdb5ae946a4a6 and its exact tuple-law total-correlation residual. For any finite receiver-skew broadcast channel T and any arbitrary finite two-letter Marton law P(W,U,V,X_1,X_2), define A_1=I(Y_2;Y_1,U|W), A_2=I(Y_1;Y_2,U|W), B_1=I(Z_2;Z_1,V|W), B_2=I(Z_1;Z_2,V|W), D=I(U;V|W), and C=(I(Y_1;Y_2|W)+I(Y_1;Y_2)+I(Z_1;Z_2|W)+I(Z_1;Z_2))/2. If this law has Marton value strictly above 2M_T, then A_a+B_b>C+1{a!=b}D for all four (a,b) in {1,2}^2. Hence failure of any one inequality rules out a gain. Adding the crossed tests gives the combined necessary inequality in README equation (12). Applied to the half-skew BSSC, these tests cover every abstract two-letter auxiliary law without assuming an a priori tuple structure. They are necessary only and do not prove additivity, exhibit a gain, or determine capacity.",
      "dependencyTransactionIds": [
        "5ed3f525b9ae7f32c6e1dcbf22ecdb5ae946a4a6"
      ]
    }
  ]
}

</artifact>
<artifact path="problems/bssc-sum-capacity/contributions/two-letter-padding-correlation-tests/verification.json">
{
  "schemaVersion": 1,
  "verifier": {
    "id": "python-stdlib-3-13-v1",
    "specDigest": "sha256:fc7ed06b77396fabc1da84694b4d8a08800843f41ad8ca4b9cd666b67ba60884"
  },
  "entrypoint": "verify_padding_tests.py",
  "arguments": []
}

</artifact>
<artifact path="problems/bssc-sum-capacity/contributions/two-letter-padding-correlation-tests/verify_padding_tests.py">
#!/usr/bin/env python3
"""Corroborate the four constant-padding residual identities."""

from fractions import Fraction as F
from functools import lru_cache
from itertools import product
from math import log2


BASE = ("W", "U", "V", "X1", "X2")
ALL = BASE + ("Y1", "Y2", "Z1", "Z2")


def need(condition, message):
    if not condition:
        raise AssertionError(message)


def bssc_y(x, y):
    return ((F(1, 2), F(1, 2)), (F(0), F(1)))[x][y]


def bssc_z(x, z):
    return ((F(1), F(0)), (F(1, 2), F(1, 2)))[x][z]


def build_law():
    base_weights = {}
    for w, u, v, x1, x2 in product(range(2), repeat=5):
        code = 1 + 3 * w + 5 * u + 7 * v + 11 * x1 + 13 * x2
        interaction = 4 * (u == x2) + 6 * (v == x1) + 5 * (x1 == x2)
        base_weights[(w, u, v, x1, x2)] = 1 + (code * code + interaction) % 23
    total = sum(base_weights.values())
    law = {}
    for base, weight in base_weights.items():
        x1, x2 = base[3], base[4]
        for y1, y2, z1, z2 in product(range(2), repeat=4):
            probability = (
                F(weight, total)
                * bssc_y(x1, y1)
                * bssc_y(x2, y2)
                * bssc_z(x1, z1)
                * bssc_z(x2, z2)
            )
            if probability:
                law[base + (y1, y2, z1, z2)] = probability
    need(sum(law.values()) == 1, "joint law normalization")
    return law


LAW = build_law()
INDEX = {name: i for i, name in enumerate(ALL)}


@lru_cache(maxsize=None)
def marginal(names):
    indices = tuple(INDEX[name] for name in names)
    out = {}
    for atom, probability in LAW.items():
        key = tuple(atom[i] for i in indices)
        out[key] = out.get(key, F(0)) + probability
    return out


@lru_cache(maxsize=None)
def entropy(names):
    if not names:
        return 0.0
    return -sum(float(p) * log2(float(p)) for p in marginal(tuple(names)).values())


def conditional_entropy(a, c=()):
    return entropy(tuple(a) + tuple(c)) - entropy(tuple(c))


def mutual_information(a, b, c=()):
    a, b, c = tuple(a), tuple(b), tuple(c)
    return (
        entropy(a + c)
        + entropy(b + c)
        - entropy(c)
        - entropy(a + b + c)
    )


def lhalf_two_letter():
    return (
        F(1, 2) * mutual_information(("W",), ("Y1", "Y2"))
        + F(1, 2) * mutual_information(("W",), ("Z1", "Z2"))
        + mutual_information(("U",), ("Y1", "Y2"), ("W",))
        + mutual_information(("V",), ("Z1", "Z2"), ("W",))
        - mutual_information(("U",), ("V",), ("W",))
    )


def coordinate_sum(a, b):
    value = 0.0
    for i in (1, 2):
        yi, zi = (f"Y{i}",), (f"Z{i}",)
        value += 0.5 * mutual_information(("W",), yi)
        value += 0.5 * mutual_information(("W",), zi)
        if i == a:
            value += mutual_information(("U",), yi, ("W",))
        if i == b:
            value += mutual_information(("V",), zi, ("W",))
        if i == a == b:
            value -= mutual_information(("U",), ("V",), ("W",))
    return value


def explicit_terms():
    a = {
        1: mutual_information(("Y2",), ("Y1", "U"), ("W",)),
        2: mutual_information(("Y1",), ("Y2", "U"), ("W",)),
    }
    b = {
        1: mutual_information(("Z2",), ("Z1", "V"), ("W",)),
        2: mutual_information(("Z1",), ("Z2", "V"), ("W",)),
    }
    d = mutual_information(("U",), ("V",), ("W",))
    charge = 0.5 * (
        mutual_information(("Y1",), ("Y2",), ("W",))
        + mutual_information(("Y1",), ("Y2",))
        + mutual_information(("Z1",), ("Z2",), ("W",))
        + mutual_information(("Z1",), ("Z2",))
    )
    return a, b, d, charge


def main():
    two = float(lhalf_two_letter())
    a_terms, b_terms, penalty, charge = explicit_terms()
    residuals = {}
    for a, b in product((1, 2), repeat=2):
        direct = two - coordinate_sum(a, b)
        explicit = a_terms[a] + b_terms[b] - (penalty if a != b else 0.0) - charge
        need(abs(direct - explicit) < 2e-12, f"padding identity ({a},{b})")
        residuals[(a, b)] = explicit

    crossed_sum = residuals[(1, 2)] + residuals[(2, 1)]
    combined = (
        mutual_information(("Y1",), ("Y2",), ("W",))
        + mutual_information(("Z1",), ("Z2",), ("W",))
        - mutual_information(("Y1",), ("Y2",))
        - mutual_information(("Z1",), ("Z2",))
        + mutual_information(("U",), ("Y2",), ("Y1", "W"))
        + mutual_information(("U",), ("Y1",), ("Y2", "W"))
        + mutual_information(("V",), ("Z2",), ("Z1", "W"))
        + mutual_information(("V",), ("Z1",), ("Z2", "W"))
        - 2.0 * penalty
    )
    need(abs(crossed_sum - combined) < 3e-12, "combined crossed-padding identity")
    need(max(residuals.values()) - min(residuals.values()) > 1e-5,
         "test law exercises distinct padding residuals")
    print("PASS: four constant-padding residual identities")
    print("PASS: crossed-test chain-rule identity")
    for pair in sorted(residuals):
        print(f"padding {pair}: residual={residuals[pair]:.15f}")


if __name__ == "__main__":
    main()

</artifact>
</contribution>
<contribution>
ordinal: 17
transaction_id: 88a1004f309460f3ec1cacdae88d30f88559f9bc
contribution_id: marton-multiletter-foundation-repair
author: Robert Raynor
<artifact path="problems/bssc-sum-capacity/contributions/marton-multiletter-foundation-repair/README.md">
# Finite-auxiliary Marton multiletter foundation and directed RTD threshold

## Claim and exact scope

Let \(P\) be the governed half-skew BSSC.  For each \(n\geq1\), let
\(\mathcal A_n^{\mathrm{fin}}\) be the collection of all choices of **finite**
alphabets \(\mathcal U,\mathcal V,\mathcal W\) and all joint laws

\[
p(u,v,w,x^n)P^{\otimes n}(y^n,z^n\mid x^n)
\]

on those alphabets.  Equivalently, every member obeys
\((U,V,W)-X^n-(Y^n,Z^n)\).  Define

\[
\begin{aligned}
F_n(U,V,W,X^n)
={}&\min\{I(W;Y^n),I(W;Z^n)\}\\
&+I(U;Y^n\mid W)+I(V;Z^n\mid W)-I(U;V\mid W),\\
M_n^{\mathrm{fin}}(P)
={}&\sup_{\mathcal A_n^{\mathrm{fin}}}F_n(U,V,W,X^n).
\end{aligned}
\tag{1}
\]

The superscript is retained here to make the finite-auxiliary scope explicit;
no statement about arbitrary measurable auxiliary spaces is needed or made.
Because a constant law has value zero and the BSSC outputs are binary,

\[
0\leq M_n^{\mathrm{fin}}(P)\leq2n.
\tag{2}
\]

The following algebraic conclusions are unconditional:

\[
M_{m+n}^{\mathrm{fin}}(P)
\geq M_m^{\mathrm{fin}}(P)+M_n^{\mathrm{fin}}(P),
\qquad m,n\geq1,
\tag{3}
\]

and hence, by Fekete's lemma,

\[
\lim_{n\to\infty}\frac{M_n^{\mathrm{fin}}(P)}n
=\sup_{n\geq1}\frac{M_n^{\mathrm{fin}}(P)}n.
\tag{4}
\]

Two classical results are kept as explicit hypotheses rather than silently
promoted to newly proved facts:

- **(H-Marton)** For every finite two-receiver discrete memoryless broadcast
  channel \(T:x\mapsto(y,z)\) and every finite law
  \((U,V,W)-X-(Y,Z)\), the closure of the nonnegative private-message rate
  pairs satisfying

  \[
  \begin{aligned}
  R_1&\leq I(U,W;Y),\\
  R_2&\leq I(V,W;Z),\\
  R_1+R_2&\leq \min\{I(W;Y),I(W;Z)\}
  +I(U;Y\mid W)+I(V;Z\mid W)-I(U;V\mid W)
  \end{aligned}
  \tag{H-M}
  \]

  is achievable under the average-error convention.
- **(H-binary)** For every finite binary-input two-receiver broadcast
  channel, the supremum of the one-letter Marton private-message sum
  functional equals the randomized-time-division supremum.

Under (H-Marton), the finite-super-symbol reduction is

\[
\boxed{C_{\mathrm{sum}}(P)\geq
\frac{M_n^{\mathrm{fin}}(P)}n\quad(n\geq1),}
\tag{5}
\]

and consequently

\[
C_{\mathrm{sum}}(P)\geq
\lim_{n\to\infty}\frac{M_n^{\mathrm{fin}}(P)}n.
\tag{6}
\]

For the BSSC, define \(h_2(t)=-t\log_2t-(1-t)\log_2(1-t)\),

\[
J(q)=h_2(q/2)-q,
\qquad D(q)=J(q)-J(1-q),
\tag{7}
\]

and let \(L_{\mathrm{RTD}}\) be the randomized-time-division supremum.  The
calculus and symmetrization proof below gives the exact formula

\[
\boxed{
L_{\mathrm{RTD}}
=h_2(1/4)-\frac12
+\frac12\left[
h_2(q_-/2)-h_2((1-q_-)/2)+1-2q_-
\right],
\quad q_-=\frac{15-\sqrt{105}}{30}.}
\tag{8}
\]

The included directed certificate proves

\[
\begin{aligned}
0.3616428844219546156634415781505870072079810107238605552037137298028007
&<L_{\mathrm{RTD}}\\
&<0.3616428844219546156634415781505870072079810107238605552037137298028008,
\end{aligned}
\tag{9}
\]

and

\[
\begin{aligned}
0.7232857688439092313268831563011740144159620214477211104074274596056014
&<2L_{\mathrm{RTD}}\\
&<0.7232857688439092313268831563011740144159620214477211104074274596056016.
\end{aligned}
\tag{10}
\]

Thus (H-binary) implies
\(M_1^{\mathrm{fin}}(P)=L_{\mathrm{RTD}}\).  Under (H-Marton), an
\(n\)-letter finite Marton law of exact value \(S_n\) strictly improves the
governed RTD achievable lower bound through super-symbol normalization if and
only if

\[
S_n>nL_{\mathrm{RTD}}.
\tag{11}
\]

Under both hypotheses, the same inequality is equivalently a strict
improvement over the complete one-letter Marton sum optimum.  For a numerical
two-letter witness, comparison with the directed upper endpoint in (10) is a
rigorous sufficient test; the old ellipsized decimal is not used as an exact
upper bound.

## Proof of the finite-super-symbol reduction

Fix \(n\).  If \(M_n^{\mathrm{fin}}(P)=0\), (5) follows from the trivial
zero-rate code.  Otherwise fix
\(0<\epsilon<M_n^{\mathrm{fin}}(P)\).  The definition of a finite supremum
gives a member of \(\mathcal A_n^{\mathrm{fin}}\) with

\[
F_n>M_n^{\mathrm{fin}}(P)-\epsilon>0.
\tag{12}
\]

For this law put

\[
A=I(U,W;Y^n),\qquad B=I(V,W;Z^n),\qquad S=F_n.
\]

The nonnegativity of mutual information and the two possible branches of the
minimum give \(S\leq A+B\).  Hence there are nonnegative
\(R_1\leq A\), \(R_2\leq B\) with \(R_1+R_2=S\): for example, take
\(R_1=\min\{A,S\}\) and \(R_2=S-R_1\).  These rates obey all three
inequalities in (H-M).  Under (H-Marton), rates arbitrarily close to this pair
are therefore achievable on the finite super-channel \(P^{\otimes n}\).

An \(\ell\)-use code for that super-channel maps each message pair to
\(\ell\) input blocks in \(\{0,1\}^n\).  Flattening those blocks, without
changing the encoder or either decoder, gives an ordinary BSSC code of
blocklength \(n\ell\).  Memorylessness makes the two induced channel laws
identical, so the average error probabilities are unchanged.  The sum rate
per original use is divided by \(n\), and (12) gives a rate arbitrarily close
to \((M_n^{\mathrm{fin}}(P)-\epsilon)/n\).  Letting
\(\epsilon\downarrow0\) proves (5).  This uses only the defining property of
a supremum; no optimizer or auxiliary-cardinality theorem is invoked.

## Proof of superadditivity and the limit

Take independent finite laws at lengths \(m\) and \(n\), each within
\(\epsilon\) of its supremum, and concatenate them.  Pairing their finite
auxiliaries gives another finite law.  Every conditional private term and the
penalty add exactly.  If

\[
A_r=I(W_r;Y^r),\qquad B_r=I(W_r;Z^r),
\qquad r\in\{m,n\},
\]

then the common term satisfies

\[
\min\{A_m+A_n,B_m+B_n\}
\geq\min\{A_m,B_m\}+\min\{A_n,B_n\}.
\tag{13}
\]

Indeed, the right side is no larger than either argument on the left.  Letting
\(\epsilon\downarrow0\) proves (3).

For (2), a constant law gives zero.  For every candidate, discard the
nonpositive penalty and use the \(Y^n\) branch of the minimum:

\[
F_n\leq I(U,W;Y^n)+I(V;Z^n\mid W)
\leq H(Y^n)+H(Z^n)\leq2n.
\]

Fekete's lemma now applies to the finite superadditive sequence and gives
(4); combining (4) with (5) gives (6).

If one finite \(n\)-letter law has value \(S_n\), \(k\) independent copies
have value exactly \(kS_n\).  All conditional terms add, and the common term
uses \(\min\{kA,kB\}=k\min\{A,B\}\).  This propagation is an identity for
the selected laws, not a claim that the suprema are additive.

## Exact RTD reduction and maximizer

For input prior \(q=\Pr[X=0]\), the BSSC receiver mutual informations are
\(J(q)\) and \(J(1-q)\).  Consider an arbitrary randomized-time-division law:
conditioned on a finite common schedule \(W=w\), transmit only to receiver
\(Y\) or only to receiver \(Z\), with conditional input prior \(q_w\).  Let
\(\bar q=\mathbb E q_W\).  Since \(\min\{a,b\}\leq(a+b)/2\), the RTD sum is
at most

\[
\frac{J(\bar q)+J(1-\bar q)}2
+\frac12\mathbb E\,|J(q_W)-J(1-q_W)|.
\tag{14}
\]

The function \(J\) is concave, so the reflection-symmetric concave function
\(J(q)+J(1-q)\) is maximized at \(q=1/2\).  Equation (14) is therefore at
most

\[
J(1/2)+\frac12\max_{0\leq q\leq1}|D(q)|.
\tag{15}
\]

This upper bound is attained.  Let \(q\) maximize \(D\), use a fair binary
schedule, and choose conditional priors \(q\) and \(1-q\); in the first
schedule state transmit only to \(Y\), and in the second only to \(Z\).
The average prior is \(1/2\), both common informations are equal, and the
resulting sum is \(J(1/2)+D(q)/2\).  Antisymmetry
\(D(1-q)=-D(q)\) shows that this equals the right side of (15).

Direct differentiation on \((0,1)\) gives

\[
D'(q)=\frac12\log_2\frac{(2-q)(1+q)}{q(1-q)}-2.
\]

Because the logarithm argument is positive,

\[
D'(q)>0\iff15q^2-15q+2>0.
\]

The roots are \(q_\pm=(15\pm\sqrt{105})/30\).  The quadratic sign pattern,
the identities \(D(0)=D(1/2)=D(1)=0\), and antisymmetry show that the global
maximum is attained at \(q_-\).  Substitution gives (8).

## Directed interval certificate

Run from this contribution directory using only Python's standard library:

```text
python3 -I -B verify_repair.py
```

The checker first proves the rational inequalities
\(s_-^2<105<s_+^2\) for the decimal endpoints stored in
`interval_certificate.json`.  It therefore obtains a directed interval for
\(q_-=(15-\sqrt{105})/30\) without calling a floating-point square root.
All subsequent arithmetic uses 120-digit `Decimal` contexts with outward
rounding.  Python's `Decimal.ln` is correctly rounded using round-to-nearest;
the checker expands each logarithm result by one representable number in each
direction.  It then evaluates (8), requires the computed enclosure to lie
strictly inside the declared bounds (9), and independently checks (10) by
directed multiplication.  The certificate is an interval proof for the exact
closed form, not a check of a decimal prefix.

## Repair and provenance

Canonical transaction
`f6ea30479b9ca461294ba89a8a1a31c06ce59d08`
(`marton-multiletter-frontier-audit-2026`) is the sole declared reference in
`claims.json`.  It is a **corrective/provenance reference**, not a mathematical
premise: its primary judgment was indeterminate.  This append-only
contribution repairs and supersedes only these portions of that record:

1. its displayed \(M_n\) definition is replaced by (1), whose finite
   auxiliary scope and epsilon/supremum semantics are explicit;
2. its super-symbol capacity conclusion is replaced by the detailed reduction
   above, with (H-Marton) exposed as the exact hypothesis;
3. its unconditional wording \(M_1=L_{\mathrm{RTD}}\) is replaced by the
   exact conditional statement under (H-binary); and
4. its uncertified ellipsized threshold display is replaced by the directed
   intervals (9)--(10).

The old contribution's August 2026 source audit, theorem-scope audit, and
reproducibility-repository caveats are neither repeated nor superseded here.
No claim in this repair depends on their validity.

The exact external hypotheses are attributed to the following theorem
records:

- Katalin Marton, *A Coding Theorem for the Discrete Memoryless Broadcast
  Channel*, IEEE Transactions on Information Theory 25 (1979), 306--311,
  [doi:10.1109/TIT.1979.1056046](https://doi.org/10.1109/TIT.1979.1056046).
  The exact modern private-message formulation used as (H-Marton) is restated
  as Bound 1 of [Gohari, Nair, and Anantharam,
  arXiv:1202.0898v1](https://arxiv.org/abs/1202.0898v1).
- The binary-input equality with randomized time division in Corollary 1 of
  [Nair, Wang, and Geng, arXiv:1001.1468v1](https://arxiv.org/abs/1001.1468v1).

These results are quoted as hypotheses and are not independently re-proved or
authenticated by the interval checker.  The proof, specialization, and
certificate in this contribution were prepared by an OpenAI Codex solver
agent at Robert Raynor's request.

## Limitations

- This contribution does not independently prove (H-Marton) or (H-binary).
- It does not prove that arbitrary non-finite auxiliary spaces can be reduced
  to finite ones; they are excluded from the definition.
- It supplies no new BSSC witness and does not improve the governed capacity
  interval.
- Equality at one fixed blocklength is not a capacity converse; another
  blocklength or a non-Marton construction could do better.
- Superadditivity is not additivity.  The residual three- and four-symbol
  two-letter search remains open.

</artifact>
<artifact path="problems/bssc-sum-capacity/contributions/marton-multiletter-foundation-repair/claims.json">
{
  "schemaVersion": 1,
  "claims": [
    {
      "claimKey": "bssc-sum-capacity/marton-multiletter-finite-foundation-repair",
      "statement": "For the governed half-skew BSSC P and every n >= 1, define M_n^fin(P) as the supremum of the displayed private-message Marton functional over finite auxiliary alphabets U,V,W and finite laws (U,V,W)-X^n-(Y^n,Z^n). Unconditionally, 0 <= M_n^fin(P) <= 2n, M_{m+n}^fin(P) >= M_m^fin(P)+M_n^fin(P), and Fekete's lemma gives lim_n M_n^fin(P)/n = sup_n M_n^fin(P)/n; k independent copies of a selected n-letter law of value S_n have value exactly k S_n. Assume (H-Marton), the exact finite-DMBC private-message Marton achievability theorem stated in the README. Then C_sum(P) >= M_n^fin(P)/n for every n and hence C_sum(P) is at least the displayed Fekete limit. For the exact BSSC randomized-time-division value L_RTD, the README's symmetrization and calculus proof gives the stated closed form at q_-=(15-sqrt(105))/30, and the directed standard-library certificate proves the strict intervals 0.3616428844219546156634415781505870072079810107238605552037137298028007 < L_RTD < 0.3616428844219546156634415781505870072079810107238605552037137298028008 and 0.7232857688439092313268831563011740144159620214477211104074274596056014 < 2 L_RTD < 0.7232857688439092313268831563011740144159620214477211104074274596056016. Assume additionally (H-binary), the exact binary-input Marton-equals-randomized-time-division theorem stated in the README; then M_1^fin(P)=L_RTD. Under (H-Marton), a selected finite n-letter law strictly improves the governed RTD achievable lower bound through super-symbol normalization iff S_n > n L_RTD; under both hypotheses this is equivalently a strict improvement over the complete one-letter Marton sum optimum. This append-only claim repairs only the finite-auxiliary scope, conditional super-symbol conclusion, conditional one-letter identification, and decimal certification of transaction f6ea30479b9ca461294ba89a8a1a31c06ce59d08; that transaction is a corrective/provenance reference rather than a mathematical premise. No fixed-n equality is a capacity converse.",
      "dependencyTransactionIds": [
        "f6ea30479b9ca461294ba89a8a1a31c06ce59d08"
      ]
    }
  ]
}

</artifact>
<artifact path="problems/bssc-sum-capacity/contributions/marton-multiletter-foundation-repair/interval_certificate.json">
{
  "schemaVersion": 1,
  "units": "bits",
  "precisionDigits": 120,
  "exactDefinitions": {
    "binaryEntropy": "h_2(t)=-t log_2(t)-(1-t) log_2(1-t)",
    "receiverCurve": "J(q)=h_2(q/2)-q",
    "differenceCurve": "D(q)=J(q)-J(1-q)",
    "stationaryPolynomial": "15q^2-15q+2",
    "maximizer": "q_-=(15-sqrt(105))/30",
    "lRtd": "h_2(1/4)-1/2+(1/2)[h_2(q_-/2)-h_2((1-q_-)/2)+1-2q_-]"
  },
  "sqrt105": {
    "lower": "10.24695076595959838322103868052105199073503266345483292954197849989034798570535407292723162837854673695",
    "upper": "10.24695076595959838322103868052105199073503266345483292954197849989034798570535407292723162837854673696",
    "proofObligation": "lower^2 < 105 < upper^2 over exact rationals"
  },
  "lRtd": {
    "lower": "0.3616428844219546156634415781505870072079810107238605552037137298028007",
    "upper": "0.3616428844219546156634415781505870072079810107238605552037137298028008"
  },
  "twoLRtd": {
    "lower": "0.7232857688439092313268831563011740144159620214477211104074274596056014",
    "upper": "0.7232857688439092313268831563011740144159620214477211104074274596056016"
  },
  "method": {
    "sqrt": "exact rational square comparison; no runtime square root",
    "arithmetic": "Decimal contexts with ROUND_FLOOR and ROUND_CEILING",
    "logarithm": "correctly rounded Decimal.ln at 120 digits, expanded by one representable number in each direction",
    "acceptance": "computed enclosures must lie strictly inside every declared interval"
  }
}

</artifact>
<artifact path="problems/bssc-sum-capacity/contributions/marton-multiletter-foundation-repair/premises.json">
{
  "schemaVersion": 1,
  "externalHypotheses": [
    {
      "id": "H-Marton",
      "status": "explicit logical hypothesis; not independently proved in this contribution",
      "statement": "For every finite two-receiver discrete memoryless broadcast channel and every finite law (U,V,W)-X-(Y,Z), the closure of the nonnegative private-message rate pairs satisfying the two individual Marton inequalities and the displayed Marton sum inequality is achievable under average error.",
      "source": {
        "title": "On Marton's inner bound for broadcast channels",
        "authors": ["Amin Gohari", "Chandra Nair", "Venkat Anantharam"],
        "version": "arXiv:1202.0898v1",
        "location": "Bound 1 (attributed there to Marton)",
        "url": "https://arxiv.org/abs/1202.0898v1",
        "original": {
          "author": "Katalin Marton",
          "title": "A Coding Theorem for the Discrete Memoryless Broadcast Channel",
          "journal": "IEEE Transactions on Information Theory 25 (1979), 306-311",
          "doi": "10.1109/TIT.1979.1056046",
          "url": "https://doi.org/10.1109/TIT.1979.1056046"
        }
      }
    },
    {
      "id": "H-binary",
      "status": "explicit logical hypothesis; not independently proved in this contribution",
      "statement": "For every finite binary-input two-receiver broadcast channel, the supremum of the one-letter Marton private-message sum functional equals the randomized-time-division supremum.",
      "source": {
        "title": "An information inequality and evaluation of Marton's inner bound for binary input broadcast channels",
        "authors": ["Chandra Nair", "Zizhou Vincent Wang", "Yanlin Geng"],
        "version": "arXiv:1001.1468v1",
        "location": "Corollary 1",
        "url": "https://arxiv.org/abs/1001.1468v1"
      }
    }
  ],
  "canonicalReferences": [
    {
      "transactionId": "f6ea30479b9ca461294ba89a8a1a31c06ce59d08",
      "contributionId": "marton-multiletter-frontier-audit-2026",
      "role": "corrective and provenance reference only; not a mathematical premise",
      "primaryJudgmentId": "sha256:9bbc630bb3d15c5fb9fded5c0fb69a19ffd0bf9a7bb4f65620a65bb3250c0da4",
      "primaryJudgmentStatus": "indeterminate"
    }
  ],
  "repairScope": {
    "supersedes": [
      "the prior displayed M_n definition's unspecified auxiliary-alphabet scope",
      "the prior super-symbol conclusion's implicit use of Marton achievability",
      "the prior unconditional phrasing of M_1(P)=L_RTD",
      "the prior uncertified ellipsized decimal display"
    ],
    "doesNotSupersede": [
      "the August 2026 source and input-alphabet audit",
      "the August 2026 reproduction-repository replay record and caveat",
      "the fixed-blocklength non-converse limitation"
    ]
  }
}

</artifact>
<artifact path="problems/bssc-sum-capacity/contributions/marton-multiletter-foundation-repair/verification.json">
{
  "schemaVersion": 1,
  "verifier": {
    "id": "python-stdlib-3-13-v1",
    "specDigest": "sha256:fc7ed06b77396fabc1da84694b4d8a08800843f41ad8ca4b9cd666b67ba60884"
  },
  "entrypoint": "verify_repair.py",
  "arguments": []
}

</artifact>
<artifact path="problems/bssc-sum-capacity/contributions/marton-multiletter-foundation-repair/verify_repair.py">
#!/usr/bin/env python3
"""Directed RTD interval and structural audit for the foundation repair."""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from decimal import Context, Decimal, ROUND_CEILING, ROUND_FLOOR, ROUND_HALF_EVEN
from fractions import Fraction
from pathlib import Path


ROOT = Path(__file__).resolve().parent
D = Decimal
PRECISION = 120
NEAR = Context(prec=PRECISION, rounding=ROUND_HALF_EVEN)
DOWN = Context(prec=PRECISION, rounding=ROUND_FLOOR)
UP = Context(prec=PRECISION, rounding=ROUND_CEILING)


def need(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def load(name: str) -> dict:
    with (ROOT / name).open("r", encoding="utf-8") as handle:
        return json.load(handle)


@dataclass(frozen=True)
class IV:
    lo: Decimal
    hi: Decimal

    def __post_init__(self) -> None:
        need(self.lo <= self.hi, "reversed interval")

    @staticmethod
    def point(value: str | int | Decimal) -> "IV":
        value = value if isinstance(value, Decimal) else D(value)
        return IV(value, value)

    def __add__(self, other: "IV") -> "IV":
        return IV(DOWN.add(self.lo, other.lo), UP.add(self.hi, other.hi))

    def __neg__(self) -> "IV":
        return IV(self.hi.copy_negate(), self.lo.copy_negate())

    def __sub__(self, other: "IV") -> "IV":
        return self + (-other)

    def __mul__(self, other: "IV") -> "IV":
        products = (
            (self.lo, other.lo),
            (self.lo, other.hi),
            (self.hi, other.lo),
            (self.hi, other.hi),
        )
        return IV(
            min(DOWN.multiply(left, right) for left, right in products),
            max(UP.multiply(left, right) for left, right in products),
        )

    def __truediv__(self, other: "IV") -> "IV":
        need(not (other.lo <= 0 <= other.hi), "interval division by zero")
        reciprocal = IV(
            DOWN.divide(D(1), other.hi),
            UP.divide(D(1), other.lo),
        )
        return self * reciprocal

    def ln(self) -> "IV":
        need(self.lo > 0, "logarithm domain")
        # Decimal.ln is correctly rounded with ROUND_HALF_EVEN. Expanding the
        # endpoint evaluations by one representable number makes the enclosure
        # explicit; monotonicity of ln handles interval inputs.
        lower = NEAR.ln(self.lo).next_minus(context=NEAR)
        upper = NEAR.ln(self.hi).next_plus(context=NEAR)
        return IV(lower, upper)


Q = IV.point
ZERO = Q(0)
ONE = Q(1)
TWO = Q(2)
LN2 = TWO.ln()


def binary_entropy(value: IV) -> IV:
    need(D(0) < value.lo <= value.hi < D(1), "entropy input domain")
    complement = ONE - value
    return -(value * value.ln() + complement * complement.ln()) / LN2


def exact_fraction(text: str) -> Fraction:
    return Fraction(text)


def check_certificate() -> tuple[IV, IV, IV]:
    cert = load("interval_certificate.json")
    need(cert["schemaVersion"] == 1, "certificate schema")
    need(cert["units"] == "bits", "certificate units")
    need(cert["precisionDigits"] == PRECISION, "certificate precision")

    definitions = cert["exactDefinitions"]
    need(definitions["stationaryPolynomial"] == "15q^2-15q+2", "polynomial")
    need(definitions["maximizer"] == "q_-=(15-sqrt(105))/30", "maximizer")

    sqrt_data = cert["sqrt105"]
    sqrt_lo_q = exact_fraction(sqrt_data["lower"])
    sqrt_hi_q = exact_fraction(sqrt_data["upper"])
    need(sqrt_lo_q * sqrt_lo_q < 105 < sqrt_hi_q * sqrt_hi_q,
         "exact sqrt(105) bracket")

    sqrt_iv = IV(D(sqrt_data["lower"]), D(sqrt_data["upper"]))
    q_minus = (Q(15) - sqrt_iv) / Q(30)
    need(D(0) < q_minus.lo < q_minus.hi < D("0.5"), "q_- interval")

    # The bracket straddles the smaller root of the stationary polynomial.
    q_lo_q = exact_fraction(str(q_minus.lo))
    q_hi_q = exact_fraction(str(q_minus.hi))
    polynomial = lambda q: 15 * q * q - 15 * q + 2
    need(polynomial(q_lo_q) > 0 > polynomial(q_hi_q),
         "stationary-root straddle")

    half = Q("0.5")
    quarter = Q("0.25")
    l_rtd = (
        binary_entropy(quarter)
        - half
        + half
        * (
            binary_entropy(q_minus / TWO)
            - binary_entropy((ONE - q_minus) / TWO)
            + ONE
            - TWO * q_minus
        )
    )

    declared_l = IV(D(cert["lRtd"]["lower"]), D(cert["lRtd"]["upper"]))
    need(declared_l.lo < l_rtd.lo <= l_rtd.hi < declared_l.hi,
         "directed L_RTD enclosure")

    two_l_rtd = TWO * l_rtd
    declared_two = IV(
        D(cert["twoLRtd"]["lower"]),
        D(cert["twoLRtd"]["upper"]),
    )
    need(declared_two.lo < two_l_rtd.lo <= two_l_rtd.hi < declared_two.hi,
         "directed 2 L_RTD enclosure")
    need(
        DOWN.multiply(declared_l.lo, D(2)) == declared_two.lo
        and UP.multiply(declared_l.hi, D(2)) == declared_two.hi,
        "declared doubling consistency",
    )
    return q_minus, l_rtd, two_l_rtd


def check_structural_scope() -> None:
    claims = load("claims.json")
    premises = load("premises.json")
    need(claims["schemaVersion"] == premises["schemaVersion"] == 1, "schemas")
    need(len(claims["claims"]) == 1, "one declared claim")
    claim = claims["claims"][0]
    need(
        claim["claimKey"]
        == "bssc-sum-capacity/marton-multiletter-finite-foundation-repair",
        "claim key",
    )
    repaired = "f6ea30479b9ca461294ba89a8a1a31c06ce59d08"
    need(claim["dependencyTransactionIds"] == [repaired], "corrective reference")
    need(re.fullmatch(r"[0-9a-f]{40}", repaired) is not None, "transaction form")

    statement = claim["statement"]
    for required in (
        "finite auxiliary alphabets U,V,W",
        "M_{m+n}^fin(P) >= M_m^fin(P)+M_n^fin(P)",
        "Assume (H-Marton)",
        "Assume additionally (H-binary)",
        "corrective/provenance reference rather than a mathematical premise",
        "No fixed-n equality is a capacity converse",
    ):
        need(required in statement, f"claim scope: {required}")

    hypotheses = {item["id"]: item for item in premises["externalHypotheses"]}
    need(set(hypotheses) == {"H-Marton", "H-binary"}, "hypothesis ids")
    need(hypotheses["H-Marton"]["source"]["version"] == "arXiv:1202.0898v1",
         "Marton source version")
    need(
        hypotheses["H-Marton"]["source"]["authors"]
        == ["Amin Gohari", "Chandra Nair", "Venkat Anantharam"],
        "Marton restatement authors",
    )
    need(hypotheses["H-Marton"]["source"]["location"].startswith("Bound 1"),
         "Marton source location")
    original_marton = hypotheses["H-Marton"]["source"]["original"]
    need(original_marton["author"] == "Katalin Marton", "original author")
    need(original_marton["doi"] == "10.1109/TIT.1979.1056046",
         "original Marton DOI")
    need(hypotheses["H-binary"]["source"]["version"] == "arXiv:1001.1468v1",
         "binary source version")
    need(hypotheses["H-binary"]["source"]["location"] == "Corollary 1",
         "binary source location")
    need(all("not independently proved" in item["status"] for item in hypotheses.values()),
         "hypothesis boundary")

    references = premises["canonicalReferences"]
    need(len(references) == 1 and references[0]["transactionId"] == repaired,
         "canonical repair target")
    need("not a mathematical premise" in references[0]["role"], "reference role")
    need(references[0]["primaryJudgmentStatus"] == "indeterminate",
         "prior judgment status")

    # Exact symbolic case audit of min(a_m+a_n,b_m+b_n) >=
    # min(a_m,b_m)+min(a_n,b_n).  In each of the four order cases, write each
    # non-minimal member as its minimum plus a nonnegative slack.  The two
    # left-branch differences from the right side have only 0/1 slack
    # coefficients, hence are nonnegative.
    for m_chooses_a in (False, True):
        for n_chooses_a in (False, True):
            a_difference = (
                0 if m_chooses_a else 1,
                0 if n_chooses_a else 1,
            )
            b_difference = (
                1 if m_chooses_a else 0,
                1 if n_chooses_a else 0,
            )
            need(set(a_difference + b_difference) <= {0, 1}, "min inequality cases")


def print_hashes() -> None:
    for name in ("claims.json", "premises.json", "interval_certificate.json"):
        digest = hashlib.sha256((ROOT / name).read_bytes()).hexdigest()
        print(f"{name}: sha256:{digest}")


def main() -> None:
    # Inspect this source before execution. It performs no network access and
    # writes no files.
    check_structural_scope()
    q_minus, l_rtd, two_l_rtd = check_certificate()
    print_hashes()
    print(f"q_- enclosure: [{q_minus.lo}, {q_minus.hi}]")
    print(f"L_RTD enclosure: [{l_rtd.lo}, {l_rtd.hi}]")
    print(f"2 L_RTD enclosure: [{two_l_rtd.lo}, {two_l_rtd.hi}]")
    print("PASS: finite-scope repair and directed RTD threshold certificate")


if __name__ == "__main__":
    main()

</artifact>
</contribution>
<contribution>
ordinal: 18
transaction_id: 33a5944dca980bf94cc869c6c7dee2d04385ff58
contribution_id: two-letter-marton-full-support-necessity
author: Robert Raynor
<artifact path="problems/bssc-sum-capacity/contributions/two-letter-marton-full-support-necessity/README.md">
# Full super-input support is necessary for a two-letter Marton gain

## Claim and scope

Let \(P\) be the half-skew BSSC in the governed problem, and let
\(P^{\otimes 2}\) have super-input
\(S=(X_1,X_2)\in\{00,01,10,11\}\). For a finite Marton law write

\[
\begin{aligned}
M={}&\min\{I(W;Y^2),I(W;Z^2)\}
 +I(U;Y^2\mid W)+I(V;Z^2\mid W)-I(U;V\mid W),\\
 &(W,U,V)-S-(Y^2,Z^2).
\end{aligned}
\]

This contribution proves the support-pruning theorem

\[
 \boxed{|\operatorname{supp}P_S|\leq3\quad\Longrightarrow\quad
 M<0.695\ \text{bits}.}
 \tag{1}
\]

For a fully internal comparison, use a fair one-letter
randomized-time-division schedule with reflected conditional input priors
\(q=\Pr[X=1]=1/6\) and \(1-q=5/6\), directing the first state to \(Z\)
and the second to \(Y\). If \(J(q)=h_2(q/2)-q\), both common mutual informations
are

\[
J(1/2)-\frac{J(1/6)+J(5/6)}2,
\]

and the private term is \(J(1/6)\). Two independent copies therefore have
the exact unnormalized value

\[
B_{1/6}:=2h_2(1/4)+h_2(1/12)-h_2(5/12)-\frac13
>0.7231.
\tag{2}
\]

The included directed checker certifies the last inequality. Thus the
optimal repeated one-letter RTD benchmark is at least \(B_{1/6}\), and every
two-letter Marton witness that strictly improves that benchmark must give
**positive probability to all four** super-input symbols. In fact the proof
gives the quantitative interiority condition

\[
 P_S(00),P_S(11)>\frac1{180},\qquad
 P_S(01),P_S(10)>\frac1{325}.
 \tag{Q}
\]

This strengthens the canonical two-symbol pruning result, but does not depend
on it. The proof is self-contained: it does not assume the binary-input
Marton theorem, product additivity of a relaxed UV functional, the exact
governed RTD decimal, or any theorem from the 2026 multiletter counterexample
papers. It derives the two UV-style rows needed below directly from the
Marton expression, proves the one-letter BSSC support lines by calculus, and
proves the required two-factor identity by the chain rule.

This supplies the next structural-pruning step in the non-exclusiv
</artifact>
[remaining artifacts omitted: evidence limit reached]
</contribution>
<contribution>
ordinal: 19
transaction_id: 9bb22afe5abd3e1d9f419c1717bd61bb33a958ff
contribution_id: two-letter-marton-marginal-correlation-pruning
author: Robert Raynor
[remaining artifacts omitted: evidence limit reached]
</contribution>
<contribution>
ordinal: 21
transaction_id: 906894532b971ecf8c4ac6fcdd3f7380e00549b2
contribution_id: two-letter-output-covariance-curvature
author: Robert Raynor
[remaining artifacts omitted: evidence limit reached]
</contribution>
<contribution>
ordinal: 24
transaction_id: 43fcf08a3272a3995158951de8d8ca2a666a0792
contribution_id: two-letter-marton-exhaustive-transplant-certificate-repair
author: Robert Raynor
[remaining artifacts omitted: evidence limit reached]
</contribution>
<contribution>
ordinal: 25
transaction_id: 9ff49a7c2d1c242d6cb29cf9afd34803b06d2383
contribution_id: two-letter-marton-product-code-quotient-local-maximum
author: Robert Raynor
[remaining artifacts omitted: evidence limit reached]
</contribution>