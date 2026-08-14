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
