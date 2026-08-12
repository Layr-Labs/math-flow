# Output-dependent auxiliary receivers are redundant in the full GK bound

## Contribution

This note proves an exact marginalization theorem for the full two-auxiliary-
receiver outer bound of Gohari, Liu, and Nair (their Theorem 9, equations
(19a)--(19p)). Although that theorem permits an auxiliary channel

```text
T_{G,K|X,Y,Z},
```

every displayed constraint depends on it only through the two separate
input-to-output marginals `T_{G|X}` and `T_{K|X}`. Consequently, for every
finite-alphabet broadcast channel, the full constraint system is unchanged if
one restricts to conditionally independent, input-only auxiliary receivers

```text
T'_{G,K|X,Y,Z}(g,k|x,y,z)
  = T_{G|X}(g|x) T_{K|X}(k|x).
```

Thus output dependence and conditional `G`--`K` correlation cannot improve
any outer bound obtained solely from Theorem 9's displayed constraints. For
the binary skew-symmetric broadcast channel (BSSC), this removes a seemingly
larger auxiliary family from the upper-bound optimization. No numerical
capacity value is claimed.

## Setting and exact statement

Let `T_{Y,Z|X}` be any finite-alphabet discrete memoryless broadcast channel.
The BSSC of interest is the specialization

```text
T_{Y|X} = [[1/2, 1/2],
           [0,   1  ]],

T_{Z|X} = [[1,   0  ],
           [1/2, 1/2]],
```

with rows indexed by `x=0,1`. The full GK theorem considers three auxiliary
groups

```text
A_a=(U_a,V_a,W_a),  A_b=(U_b,V_b,W_b),  A_c=(U_c,V_c,W_c)
```

and the factorization

```text
p(x,a_a,a_b,a_c,y,z,g,k)
  = p_X(x)
    p_{A_a|X}(a_a|x)
    p_{A_b|X}(a_b|x)
    p_{A_c|X}(a_c|x)
    T_{Y,Z|X}(y,z|x)
    T_{G,K|X,Y,Z}(g,k|x,y,z).
```

The two extra side conditions accompanying (19a)--(19p) are

```text
0 <= I(X;Z|U_c,W_c) - I(X;K|U_c,W_c)
  <= I(V_c;Z|W_c) - I(V_c;K|W_c),

0 <= I(X;Y|V_a,W_a) - I(X;G|V_a,W_a)
  <= I(U_a;Y|W_a) - I(U_a;G|W_a).
```

Fix the broadcast channel, `p_X`, the three conditional laws
`p_{A_j|X}`, and an arbitrary finite-alphabet `T_{G,K|X,Y,Z}`. Define

```text
bar_T_{G|X}(g|x)
  = sum_{y,z,k} T_{Y,Z|X}(y,z|x)
                  T_{G,K|X,Y,Z}(g,k|x,y,z),

bar_T_{K|X}(k|x)
  = sum_{y,z,g} T_{Y,Z|X}(y,z|x)
                  T_{G,K|X,Y,Z}(g,k|x,y,z),
```

and let

```text
T'_{G,K|X,Y,Z}(g,k|x,y,z)
  = bar_T_{G|X}(g|x) bar_T_{K|X}(k|x).
```

**Marginalization theorem.** Replacing `T_{G,K|X,Y,Z}` by `T'` leaves
the right-hand side of each constraint (19a)--(19p), including every branch
of every displayed minimum, unchanged. It also leaves both sides of the two
side conditions unchanged. This equality is pointwise: it holds for every
choice of `p_X` and all three auxiliary-group distributions, without an
optimization or symmetry assumption.

It follows that the set of constraint-value vectors attainable with arbitrary
output-dependent `T_{G,K|X,Y,Z}` is exactly the set attainable with pairs of
input-only channels. This remains true with fixed separate alphabet bounds on
`G` and `K` because the replacement uses the same two alphabets. Hence any
supremum, infimum, envelope, linear combination, or rate-region intersection
formed solely from these constraints has the same value in the two families.

## Complete term audit

The proof depends on one syntactic property of the full GK system: every
mutual-information term contains exactly one member of `{Y,Z,G,K}` as its
output argument. For auditability, the following is the complete list of
distinct output-bearing terms in (19a)--(19p) and the two side conditions;
repetitions and signed copies are omitted.

| Output | All terms containing that output |
|---|---|
| `Y` | `I(W_a;Y)`, `I(U_a;Y|W_a)`, `I(X;Y|V_a,W_a)` |
| `Z` | `I(W_c;Z)`, `I(V_c;Z|W_c)`, `I(X;Z|U_c,W_c)` |
| `G` | `I(W_a;G)`, `I(W_b;G)`, `I(U_a,W_a;G)`, `I(U_b,W_b;G)`, `I(V_a,W_a;G)`, `I(V_b,W_b;G)`, `I(U_a;G|W_a)`, `I(U_b;G|W_b)`, `I(V_b;G|W_b)`, `I(X;G|U_a,W_a)`, `I(X;G|V_b,W_b)`, `I(X;G|V_a,W_a)` |
| `K` | `I(W_b;K)`, `I(W_c;K)`, `I(U_b,W_b;K)`, `I(U_c,W_c;K)`, `I(V_b,W_b;K)`, `I(V_c,W_c;K)`, `I(U_b;K|W_b)`, `I(V_b;K|W_b)`, `I(V_c;K|W_c)`, `I(X;K|U_b,W_b)`, `I(X;K|V_c,W_c)`, `I(X;K|U_c,W_c)` |

In particular, the system has no term involving `(G,K)` jointly, no term
involving `(Y,G)` jointly, and no term involving `(Z,K)` jointly. Each term's
other arguments belong to `X` and one auxiliary group. A constraint can of
course add terms drawn from different groups; the claim is that each
individual mutual information has the listed single-output form.

## Proof

Write `A=(A_a,A_b,A_c)`. The factorization gives the Markov chain

```text
A - X - (Y,Z,G,K).
```

This remains valid when `G,K` depend on `Y,Z`: conditional on `X`, the law of
`A` is the product of the three `p_{A_j|X}` factors, while the law of all four
outputs is supplied by the final two channel factors.

Consider first a term whose output is `G`, and let `B` denote all auxiliary
variables from the one group appearing in that term. Under the original
channel,

```text
p(b,x,g)
  = p_X(x) p_{B|X}(b|x)
    sum_{y,z,k} T_{Y,Z|X}(y,z|x)
                  T_{G,K|X,Y,Z}(g,k|x,y,z)
  = p_X(x) p_{B|X}(b|x) bar_T_{G|X}(g|x).
```

Under the product replacement `T'`, summing out `Y,Z,K` gives exactly the
same expression. Therefore the complete joint law of `(B,X,G)` is unchanged.
Every marginal needed to calculate `I(S;G|R)`, where `S` and `R` are any
subtuples of `(B,X)`, is consequently unchanged. This covers every `G` term
in the audit table, including the terms with `X` in the first argument.

The identical calculation with `G` and `K` interchanged proves invariance of
every `K` term. For the `Y` and `Z` terms, the replacement changes neither
`T_{Y,Z|X}` nor any `p_{A_j|X}`, so the joint laws `(B,X,Y)` and `(B,X,Z)`
are unchanged directly.

The audit table exhausts all mutual-information terms in the right-hand sides
of (19a)--(19p) and in the side conditions. Each term is therefore unchanged.
Signed sums of the terms are unchanged, and taking a minimum of unchanged
branch values is unchanged. This proves the pointwise assertion.

For the attainable-set assertion, the forward inclusion follows from the
replacement just proved: every output-dependent channel produces the same
constraint vector as its pair of induced input marginals. For the reverse
inclusion, any chosen pair `(Q_{G|X},Q_{K|X})` is already an allowed
output-dependent channel by setting

```text
T_{G,K|X,Y,Z}(g,k|x,y,z)=Q_{G|X}(g|x)Q_{K|X}(k|x),
```

which simply ignores `Y,Z`. The two attainable sets are equal. Since the
equality holds before optimizing over `p_X` or the auxiliary groups, all
subsequent optimizations preserve it. This completes the proof.

## Consequences for the BSSC program

The full GK theorem appears at first to require optimization over the much
larger family `T_{G,K|X,Y,Z}`. The theorem above reduces that family exactly
to two ordinary stochastic matrices `T_{G|X}` and `T_{K|X}`. It also shows
that correlating `G` and `K` conditional on `X` adds nothing to this bound.
Accordingly:

1. computations of the full (19a)--(19p) region using input-only `G,K` do not
   omit a stronger output-dependent specialization;
2. output dependence cannot explain a discrepancy between two evaluations of
   a Theorem 9-derived BSSC upper bound; and
3. future searches may quotient out all parameters that preserve the two
   induced input marginals.

For this BSSC the joint coupling of `Y,Z` is in fact forced by the marginals:
when `x=0`, `Z=0` surely, and when `x=1`, `Y=1` surely. The proof does not
need that special fact; it works for every fixed finite-alphabet
`T_{Y,Z|X}`.

## Validation

The result is symbolic and has no numerical or computational dependency. Its
check consists of three finite steps:

1. verify the displayed factorization and hence `A-X-(Y,Z,G,K)`;
2. compare the term audit against (19a)--(19p) and the two side conditions;
3. apply the displayed marginal calculation separately to `G` and `K`.

No continuity, limiting-alphabet, floating-point, stationarity, convexity, or
symmetry argument is used. Zero-probability atoms cause no issue because the
proof establishes equality of the entire finite joint laws from which the
conditional mutual informations are defined.

## Novelty, limitations, and open questions

The contribution is a structural reduction of the recently proposed full GK
outer bound, not a new general property of mutual information. The current
canonical challenge knowledge contains no admitted contribution, and in
particular no record that the output-dependent auxiliary family in Theorem 9
is redundant. The useful novelty is the exact equality of the two optimization
families, including arbitrary finite output alphabets and arbitrary
conditional correlation.

The scope is deliberately narrow. The proof does not apply to a different
outer bound containing joint-output terms such as `I(S;Y|G)` or
`I(S;G,K|R)`. It does not prove that binary auxiliary alphabets suffice, that
reflected channels are optimal, that the full GK optimization has been solved,
or that any reported BSSC decimal is correct or incorrect. It supplies no new
capacity upper bound by itself and does not determine BSSC sum-capacity.

After this reduction, the substantive open problem is to optimize or globally
certify the full Theorem 9 value over the remaining pair of input-only
channels, including arbitrary separate output alphabets.

## Reference

A. A. Gohari, G. Liu, and C. Nair, *A Two Auxiliary Receiver Outer Bound to
the Capacity Region of a Two-Receiver Discrete Memoryless Broadcast Channel*,
January 2026, especially Theorem 9 and equations (19a)--(19p).
