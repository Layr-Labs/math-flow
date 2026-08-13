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
