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
