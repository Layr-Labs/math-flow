# Exact receiver-cardinality reduction on finite posterior grids, and the solved three-point rung

## Contribution and scope

Let `V_Q(G,K)` denote the already-audited fair-prior, 30-scalar-row
Theorem-9 sum-rate LP when every posterior occurring in its three auxiliary
groups is restricted to a finite grid `Q`.  This note proves two exact facts.

1. If `|Q|=N` and `{0,1/2,1} subset Q`, then each arbitrary finite-output
   auxiliary receiver channel can be replaced, without changing `V_Q`, by a
   channel with at most `N` outputs.  Consequently

   ```text
   inf over all finite-output G,K of V_Q(G,K)
     = inf over |G|,|K| <= N of V_Q(G,K).
   ```

   If `Q` is also reflection-closed, the same reduction preserves the
   reflected class:

   ```text
   inf over finite posterior measures m of V_Q(m,m°)
     = inf over m having at most N atoms of V_Q(m,m°).
   ```

   These are pointwise exact replacements, so neither equality needs an
   attainment or compactness assumption.

2. On the coarsest grid `Q0={0,1/2,1}`, the unrestricted and reflected
   receiver optimizations coincide exactly:

   ```text
   inf_all V_Q0 = inf_reflected V_Q0 = h2(1/4) - 1/2
                                      = 0.3112781244591328... bits.
   ```

The second statement is a genuine all-pair versus reflected-pair equality,
but only for the first finite-grid rung.  Since a grid restriction lowers the
inner auxiliary maximization, `V_Q(G,K) <= B(G,K)`.  Nothing here asserts a
capacity bound, a continuum-grid limit, or
`inf_all B = inf_reflected B` for the full functional.

## 1. Posterior-measure representation

Consider a finite-output channel `A` from a binary input.  Discard output
symbols having zero probability under the fair input.  For every remaining
symbol `a`, put

```text
m_a   = P(A=a),
rho_a = P(X=1 | A=a),
```

where this joint law uses `P(X=0)=P(X=1)=1/2`.  Then `m` is a probability
measure on `[0,1]` satisfying

```text
sum_a m_a rho_a = 1/2.
```

Conversely, every finite atomic probability measure
`m=sum_a m_a delta_{rho_a}` with mean `1/2` defines a binary-input channel by

```text
P(A=a | X=0) = 2 m_a (1-rho_a),
P(A=a | X=1) = 2 m_a rho_a.
```

The two rows are nonnegative and each sums to one.  Thus this is an exact
channel representation, up to splitting or merging output symbols with the
same posterior.

For an input prior `q=P(X=1)`, define

```text
ell_q(rho) = (1-q)(1-rho) + q rho,

psi(q,rho)
  = 2(1-q)(1-rho) log2((1-rho)/ell_q(rho))
    + 2q rho log2(rho/ell_q(rho)),
```

with the standard zero-summand convention.  Direct substitution in the
definition of mutual information gives the complete channel curve

```text
I_m(q) = integral psi(q,rho) dm(rho).                 (1)
```

In particular, `I_m(0)=I_m(1)=0` and
`psi(1/2,rho)=1-h2(rho)`.  If `m°` is the pushforward of `m` by
`rho -> 1-rho`, then

```text
I_{m°}(q) = I_m(1-q).                                 (2)
```

## 2. The finite-grid receiver-cardinality theorem

Let

```text
Q = {0,1,q_1,...,q_(N-2)}
```

with the interior points in any order, and define the continuous map

```text
Phi_Q(rho)
  = (rho, psi(q_1,rho), ..., psi(q_(N-2),rho)) in R^(N-1).
```

For a channel represented by `m`, its vector

```text
integral Phi_Q(rho) dm(rho)
```

lies in the convex hull of the curve `Phi_Q([0,1])`.  Caratheodory's theorem
in `R^(N-1)` supplies points `rho_1,...,rho_s`, `s<=N`, and convex weights
`alpha_1,...,alpha_s` having exactly the same vector.  Let

```text
m' = sum_(j=1)^s alpha_j delta_(rho_j).
```

The first coordinate says that `m'` still has mean `1/2`, so Section 1 turns
it into a valid channel with at most `N` outputs.  The remaining coordinates,
together with the universal endpoint values, say

```text
I_m'(q) = I_m(q) for every q in Q.                    (3)
```

It remains to check that these samples really determine `V_Q`.  For any
Markov chain `S-X-A`, the posterior identities are

```text
I(S;A)       = I_A(1/2) - E[I_A(q_S)],
I(X;A | S)   = E[I_A(q_S)].                           (4)
```

Their conditional versions give, for example,

```text
I(U;A | W) = E[I_A(q_W)] - E[I_A(q_UW)].              (5)
```

Every receiver term in all 30 rows, including the four scalar side-constraint
rows, has one of these forms.  In the `Q`-restricted LP, every posterior on
the right of (4)-(5) belongs to `Q`; the constant prior `1/2` also belongs to
`Q`.
Therefore replacing either receiver by a channel satisfying (3) leaves the
entire LP -- objective, all row right sides, and feasibility -- identical.

Apply this replacement independently to `G` and `K`.  Every channel pair has
an at-most-`N` pair with exactly the same value, while the bounded-cardinality
pairs form a subset of all pairs.  The first infimum equality follows in both
directions.

For the reflected statement, first replace `m` by the at-most-`N` measure
`m'`.  If `Q` is reflection-closed, then for every `q in Q`, equations
(2)-(3) give

```text
I_(m'°)(q) = I_m'(1-q) = I_m(1-q) = I_(m°)(q).
```

Thus both members of `(m,m°)` are matched simultaneously by
`(m',m'°)`, proving the second equality.  Notice that this is not a
per-pair symmetrization: no asymmetric pair is changed into a reflected pair.

## 3. Exact solution on `Q0={0,1/2,1}`

Write

```text
gamma = I(X;Y) = I(X;Z) = h2(1/4)-1/2
```

at the fair prior.  The equality of the two physical midpoint values follows
also from BSSC reflection symmetry.

### 3.1 Universal lower certificate

For every pair `G,K`, use in each of the three auxiliary groups

```text
W=X,   U=constant,   V=constant.
```

All resulting posteriors are `0` or `1`, hence are allowed by `Q0`.  For any
receiver letter `A`, substitution gives

| term kind | value |
|---|---:|
| `I(W;A)` | `I(X;A)` |
| `I(U;A|W)`, `I(V;A|W)` | `0` |
| `I(U,W;A)`, `I(V,W;A)` | `I(X;A)` |
| `I(X;A|U,W)`, `I(X;A|V,W)` | `0` |

Substitution in the 30 audited scalar rows produces the following exact
row-by-row table.  Here `y=I(X;Y)=gamma` and `z=I(X;Z)=gamma`; no `G` or `K`
term survives.

| row | right side | left side at `(R1,R2)=(gamma,0)` |
|---|---:|---:|
| `SL(1,U)` | `y` | `gamma` |
| `SR(1,U)` | `z` | `gamma` |
| `SR(1,C)` | `y` | `gamma` |
| `SL(2,U)` | `y` | `gamma` |
| `SR(2,U)` | `z` | `gamma` |
| `SL(3,U)` | `y` | `gamma` |
| `SR(3,U)` | `z` | `gamma` |
| `SL(3,C)` | `z` | `gamma` |
| `R1T(0)` | `y` | `gamma` |
| `R1T(1)` | `y` | `gamma` |
| `R1T(2)` | `y` | `gamma` |
| `R1A(0)` | `z` | `gamma` |
| `R1A(1)` | `z` | `gamma` |
| `R1A(2)` | `z` | `gamma` |
| `R2T(0)` | `z` | `0` |
| `R2T(1)` | `z` | `0` |
| `R2T(2)` | `z` | `0` |
| `R2A(0)` | `y` | `0` |
| `R2A(1)` | `y` | `0` |
| `R2A(2)` | `y` | `0` |
| `N_Y(0)` | `y` | `0` |
| `N_Y(1)` | `y` | `0` |
| `N_Y(2)` | `y` | `0` |
| `N_Z(0)` | `z` | `0` |
| `N_Z(1)` | `z` | `0` |
| `N_Z(2)` | `z` | `0` |
| `F_Z_left` | `0` | `0` |
| `F_Z_right_minus_left` | `0` | `0` |
| `F_Y_left` | `0` | `0` |
| `F_Y_right_minus_left` | `0` | `0` |

Every inequality holds exactly, so

```text
V_Q0(G,K) >= gamma                                      (6)
```

for every finite-output pair, asymmetric or otherwise.

### 3.2 A matching reflected three-output construction

Let `E_gamma` be the revealing-erasure channel whose fair-input posterior
measure is

```text
(gamma/2) delta_0 + (1-gamma) delta_(1/2)
                         + (gamma/2) delta_1.           (7)
```

Equivalently, it reveals the input with probability `gamma` and outputs an
erasure otherwise.  Equation (1) shows

```text
(I_Egamma(0), I_Egamma(1/2), I_Egamma(1))
  = (0,gamma,0).
```

Measure (7) is invariant under `rho -> 1-rho`, so the pair
`(G,K)=(E_gamma,E_gamma°)` is reflected (indeed its two channels are the
same).  On `Q0`, the sampled curves of all four letters `Y,G,K,Z` are now
identical.

For every `Q0`-supported auxiliary hierarchy, the audited sum row `SL(1,U)`
is

```text
R1+R2 <= I(U_a,W_a;Y) + I(X;G | U_a,W_a)
         + I(V_b;K | W_b) - I(V_b;G | W_b)
         + I(V_c;Z | W_c) - I(V_c;K | W_c).            (8)
```

Identical sampled curves make both differences in (8) zero and allow `Y` to
be replaced by `G` in the first term.  The first two terms then telescope by
the Markov chain `(U_a,W_a)-X-G`:

```text
I(U_a,W_a;G) + I(X;G | U_a,W_a) = I(X;G) = gamma.
```

Thus (8) gives `R1+R2<=gamma` for every feasible hierarchy, proving

```text
V_Q0(E_gamma,E_gamma°) <= gamma.                         (9)
```

Combine (6)-(9).  The reflected class is a subset of the all-pair class, and
the construction belongs to both, so

```text
gamma <= inf_all V_Q0 <= inf_reflected V_Q0 <= gamma.
```

This proves the claimed equality.

## 4. Exact executable audit

Run

```text
python3 submission/verify_q0.py
```

The script uses only the Python standard library and exact `Fraction`
arithmetic.  It independently rebuilds the 30 scalar manuscript rows from
their path formulas, verifies their labels and the complete lower-witness
table, and symbolically reduces the generic-hierarchy `SL(1,U)` coefficient
in the matching construction to exactly one.  Its output is

```text
PASS: rebuilt and checked all 30 manuscript rows exactly
PASS: W=X witness makes every RHS 0, I(X;Y), or I(X;Z)
PASS: at (R1,R2)=(c,0) every row holds when I(X;Y)=I(X;Z)=c
PASS: SL(1,U) is identically c when all four Q0 curves agree
```

## Limitations

- The exact cardinality bound is `|output|<=|Q|` for a fixed finite
  posterior grid.  No cardinality bound for the continuum functional is
  claimed.
- The solved `Q0` value is a diagnostic lower approximation to the full
  receiver-optimized outer-bound value, not an upper bound on BSSC capacity.
- No limit-interchange, selector-completeness, bilinear convexity, or
  per-pair output-union symmetrization is used or asserted.
- The relation between `inf_all B` and `inf_reflected B` for the full
  continuum functional remains open.
