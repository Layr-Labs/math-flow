# Exact midpoint coercivity for arbitrary auxiliary-receiver pairs

## Contribution and effect

Let `B(G,K)` be the full Theorem-9 sum-rate value for the BSSC and let
`V_0(G,K)` be its fair-input posterior LP with every auxiliary posterior
restricted to the already-solved grid

```text
Q0={0,1/2,1}.
```

The accepted result gives only the global floor `V_0>=c`. This note sharpens
it pointwise for **every arbitrary, not necessarily reflected** binary-input
pair. Put

```text
c=I_Y(1/2)=I_Z(1/2)=h_2(1/4)-1/2=(3/4)log_2(4/3),
g=I_G(1/2),   k=I_K(1/2),
F(x)=2c max{c,x}/(c+x).
```

The theorem is

```text
B(G,K) >= V_0(g,k) >= max{F(g),F(k)}.                   (1)
```

The first inequality in (1) is a safe restriction inequality; the second is
proved by three explicit primal witness families checked against all 30 rows.
No symmetrization of `(G,K)` is used.

This yields a new necessary condition for the unsolved continuum bridge. If
`c<=U<2c` and `B(G,K)<=U`, then

```text
2c^2/U-c <= g,k <= Uc/(2c-U).                           (2)
```

At the accepted reflected upper bound

```text
U_*=0.369296946555519725636,                             (3)
```

every arbitrary-pair challenger must satisfy (2) with `U=U_*`. Thus the two
midpoint-information tails outside those exact symbolic endpoints are
rigorously removed from any global search. No decimal enclosure of the
derived endpoints is needed or asserted. This is a necessary condition on
the full continuum value, not a proof that its optimum is reflected.

## 1. Exact scalar form of the `Q0` LP

For a binary-input channel `A`, let `J_A(q)` denote its mutual information at
input prior `P(X=1)=q`. Since `J_A(0)=J_A(1)=0`, its values on `Q0` are
completely specified by `x=J_A(1/2)`. Consequently the four receiver letters
in the `Q0` LP have scalar values

```text
(J_Y(1/2),J_G(1/2),J_K(1/2),J_Z(1/2))=(c,g,k,c).        (4)
```

For completeness, each of the three posterior-martingale blocks in this LP
has an exact three-variable form. In block `j`, define

```text
(A_j,U_j,V_j),
A_j,U_j,V_j>=0,   A_j+U_j<=1,   A_j+V_j<=1.             (5)
```

To construct the block, put coarse mass `A_j/2` at each endpoint `0,1` and
mass `1-A_j` at `1/2`. In the `U` refinement, move mass `U_j/2` from the
midpoint to each endpoint; do the same with `V_j/2` in the `V` refinement.
This realizes every triple in (5). Conversely, the mass, mean, and martingale
equations on `Q0` force exactly this form, because every mean-`1/2` law on
`Q0` has equal endpoint masses.

If a row letter has midpoint information `x`, its seven possible term kinds
are therefore

| row term | exact value |
|---|---:|
| `W` | `A_j x` |
| `U|W` | `U_j x` |
| `V|W` | `V_j x` |
| `UW` | `(A_j+U_j)x` |
| `VW` | `(A_j+V_j)x` |
| `X|UW` | `(1-A_j-U_j)x` |
| `X|VW` | `(1-A_j-V_j)x` |

For example, the coarse midpoint mass is `1-A_j`, the fine `U` midpoint
mass is `1-A_j-U_j`, and hence

```text
I(U;letter|W)=U_j x,
I(X;letter|U,W)=(1-A_j-U_j)x.
```

Thus the complete 30-row problem depends on the auxiliary receivers only
through `(g,k)`. Denote it by `V_0(g,k)`.

The accepted skew involution reverses the four letters and the three blocks,
exchanges `U,V` and `R1,R2`, and permutes the 30 rows exactly. At the fair
prior the physical endpoint letters both equal `c`, so

```text
V_0(g,k)=V_0(k,g).                                      (6)
```

## 2. Three explicit primal witnesses

Each construction below specifies all three block triples and uses
`R1=R2=r`. Section 3 gives a complete exact row-slack audit.

### H: a selected middle letter is at least `c`

Let `x>=c`, and let the other middle-letter value `y` be arbitrary in
`[0,1]`. Set

```text
d=c+x,   a=x/d,   b=c/d,   r=cx/d,

(A_1,U_1,V_1)=(a,0,b),
(A_2,U_2,V_2)=(a,b,0),
(A_3,U_3,V_3)=(a,b,0).                                  (H)
```

Here `a,b>=0` and `a+b=1`, so (5) holds. For the letter ordering
`(c,x,y,c)`, H is feasible and gives

```text
R1+R2=2cx/(c+x)=F(x).                                   (7)
```

The witness is independent of `y`. Therefore it proves `V_0(g,k)>=F(g)`
whenever `g>=c`, and by (6) it proves `V_0(g,k)>=F(k)` whenever `k>=c`.

### L: both middle letters are at most `c`

Let `0<=x<=y<=c`. Set

```text
d=c+x,   a=x/d,   b=c/d,   r=c^2/d,

(A_1,U_1,V_1)=(a,b,0),
(A_2,U_2,V_2)=(a,0,b),
(A_3,U_3,V_3)=(a,0,b).                                  (L)
```

Again `a+b=1`. For `(c,x,y,c)`, L is feasible and gives

```text
R1+R2=2c^2/(c+x)=F(x).                                  (8)
```

On `[0,c]`, `F` is decreasing. Thus when both `g,k<=c`, choose
`x=min{g,k}`, `y=max{g,k}` and use (6); (8) equals
`max{F(g),F(k)}`.

### X: the middle letters straddle `c`

Let `0<=x<c<y`, put `d=c+x`, `Delta=y-x`, and define

```text
a=x/d,   b=c/d,   r=c^2/d,

A=[c(y-c)+x(c-x)]/[d Delta],
V=c(c-x)/[d Delta],

(A_1,U_1,V_1)=(a,b,0),
(A_2,U_2,V_2)=(A,0,V),
(A_3,U_3,V_3)=(b,a,0).                                  (X)
```

The entries are nonnegative. The only non-obvious box inequality is

```text
1-A-V=x(y-c)/[d Delta]>=0,                              (9)
```

while `A<=A+V<=1` follows from (9). Thus (5) holds. For `(c,x,y,c)`, X is
feasible and gives the low-side value

```text
R1+R2=2c^2/(c+x)=F(x).                                 (10)
```

Independently, H applied to the high letter `y` after (6) gives `F(y)`.
Hence the crossing case also gives `max{F(x),F(y)}`. Cases H, L, and X,
including their H/L boundary cases, exhaust the square `[0,1]^2` and prove
the second inequality in (1).

## 3. Exact audit of all 30 inequalities

For a row with rate coefficients `(rho_1,rho_2)`, define its slack as its
right side minus `rho_1 R1+rho_2 R2`. This definition also covers the ten
rate-free rows, whose rate coefficients vanish.

Direct substitution in the complete 30-row manuscript system gives the
following **complete sets** of possible row-slack numerators:

| witness | positive common denominator | complete numerator set |
|---|---:|---|
| H | `c+x` | `0`, `cx` |
| L | `c+x` | `0`, `xc`, `c(c-y)`, `c(c-x)` |
| X | `(c+x)(y-x)` | the nine expressions below |

For X, put

```text
p=c-x>=0,   q=y-c>=0,   y-x=p+q.
```

Its nine row-slack numerators are exactly

```text
0,
x q(p+q),
x c(p+q),
x p q,
(p+q)(c^2+xq),
x p y,
x[c(p+q)+pq],
c^2(p+q),
p c(p+q).
```

Every expression is manifestly nonnegative. These sets include the eight
sum rows, twelve individual-rate rows, six nonnegativity rows, and all four
side rows.

The self-contained `submission/verify_q0.py` supplies an exact executable
audit. It rebuilds the 30 rows from their path formulas and verifies their
labels. For H, it substitutes `x=c+p` with formal nonnegative variables
`(c,p,y)`. For L, it substitutes `y=x+p`, `c=y+q`. For X, it substitutes
`c=x+p`, `y=c+q`. It checks coefficientwise nonnegativity of all 30 row
slacks and all 15 block box slacks, and checks that the resulting distinct
row-slack polynomials are exactly the sets displayed above. It uses only
integer/rational polynomial arithmetic: no floating point and no optimizer.

Running

```text
PYTHONDONTWRITEBYTECODE=1 python3 submission/verify_q0.py
```

prints exactly

```text
PASS H: all 30 row slacks and all 15 box slacks are nonnegative
PASS L: all 30 row slacks and all 15 box slacks are nonnegative
PASS X: all 30 row slacks and all 15 box slacks are nonnegative
PASS upper: SL(1,U) is identically c when all four Q0 curves agree
PASS: exact three-posterior coercive-floor certificate complete
```

The `SL(1,U)` check is retained from the accepted `Q0` equality: when all four
sampled receiver curves equal `c`, that row is identically
`R1+R2<=c` for every hierarchy.

## 4. Passage to the full functional and midpoint localization

The direction of passage is important. Let `V(1/2;G,K)` be the continuum
posterior LP at the fair input. Every H/L/X witness is `Q0` supported, hence

```text
V(1/2;G,K)>=V_0(g,k).                                   (11)
```

By definition, the full receiver value takes a supremum over input priors:

```text
B(G,K)=sup_q V(q;G,K)>=V(1/2;G,K).                      (12)
```

Combining the three-case result of Section 2 with (11)-(12) proves (1). No
equality between `V_0` and either continuum quantity is asserted.

Now suppose `B(G,K)<=U`, where `c<=U<2c`. Equation (1) forces
`F(g)<=U` and `F(k)<=U`. For `x<=c`,

```text
F(x)=2c^2/(c+x)<=U  iff  x>=2c^2/U-c.                  (13)
```

For `x>=c`,

```text
F(x)=2cx/(c+x)<=U  iff  x<=Uc/(2c-U).                  (14)
```

Equations (13)-(14) give (2). Taking `U=U_*` from (3) gives the stated
specialization to the accepted certified upper bound.

## Novelty and limitations

- The accepted result `inf V_0=c` used the asymmetric point
  `(R1,R2)=(c,0)` and did not constrain `(g,k)`. The H/L/X witnesses add a
  strict penalty whenever either midpoint information differs from `c`.
- The theorem applies directly to arbitrary receiver pairs. It does not map
  a pair to a reflected pair and does not assume invariant dual weights.
- The exact equality `inf_all V_0=inf_reflected V_0=c` remains only a
  finite-grid statement. This note does not claim
  `inf_all B=inf_reflected B`.
- The window (2) is necessary but not sufficient. It does not control
  continuum auxiliary posteriors away from `Q0`, provide a continuum
  cardinality bound, or justify an infimum/limit exchange.
- No output-union symmetrization, bilinear-convexity argument, numerical
  selector completeness, or unverified optimizer output is used.
