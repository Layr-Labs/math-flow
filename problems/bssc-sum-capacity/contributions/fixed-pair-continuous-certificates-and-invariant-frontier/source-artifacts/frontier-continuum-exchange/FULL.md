# An invariant representation of the frontier Theorem-9 certificate

## Contribution and effect

The currently certified BSSC upper bound uses a visibly non-invariant
six-row combination of the 30 scalar rows of Gohari--Liu--Nair Theorem 9.
This submission proves that its **entire posterior-hierarchy functional** has
an exactly equal six-row representation whose weights are skew-invariant.
The equality holds for every input prior, every pair of auxiliary receiver
curves $G,K$ (not only reflected or binary-output pairs), every admissible
three-group posterior hierarchy, and every

\[
0\le \epsilon\le \frac13.
\]

In particular, at the accepted exact decimal

\[
\epsilon=0.000173428163029,
\]

the continuous certificate for

\[
C_{\rm sum}\le 0.369296945969202842443
\]

already lies in the skew-invariant dual cone.  Thus its relation to the
accepted rank-eight invariant quotient is exact, rather than a numerical
near-symmetry.

This does not lower the bound.  Its research effect is to identify a genuine
dual degeneracy and sharpen the next search target: changing row
representatives inside this equivalence class cannot help.  Any material
improvement must change the invariant quotient point, change the receiver
geometry, or use a genuinely different non-invariant functional.

The included `verify.py` is a standard-library-only exact rational audit.  It
transcribes every row used below term by term, expands the posterior
identities, checks both rate normalizations, checks invariance of the new
weights, and proves the claimed functional identity coefficient by
coefficient as a polynomial in \(\epsilon\).

## Posterior tensor convention

For a binary-input receiver $D$, write $I_D(q)$ for its mutual-information
curve.  In any hierarchy group $g$ in the set $\{a,b,c\}$, the standard posterior
identities are

\[
\begin{aligned}
I(W_g;D)&=I_D(q_0)-\mathbb E I_D(q_W),\\
I(U_g;D\mid W_g)&=\mathbb E I_D(q_W)-\mathbb E I_D(q_U),\\
I(V_g;D\mid W_g)&=\mathbb E I_D(q_W)-\mathbb E I_D(q_V),\\
I(U_g,W_g;D)&=I_D(q_0)-\mathbb E I_D(q_U),\\
I(V_g,W_g;D)&=I_D(q_0)-\mathbb E I_D(q_V),\\
I(X;D\mid U_g,W_g)&=\mathbb E I_D(q_U),\\
I(X;D\mid V_g,W_g)&=\mathbb E I_D(q_V).
\end{aligned}
\]

Consequently a weighted row combination is represented by coefficients

\[
T_{g,L,D},\qquad
g\in\{a,b,c\},\quad
L\in\{0,W,U,V\},\quad D\in\{Y,Z,G,K\},
\]

where level $0$ multiplies $I_D(q_0)$, and the other levels multiply the
corresponding posterior expectations.  All three hierarchy groups have the
same prior $q_0$.  Therefore two row combinations induce the same
pointwise functional if

1. their $W,U,V$ tensors agree separately in every group; and
2. their level-zero tensors agree after summing over the three groups.

This criterion is before any least-concave-majorant operation.  Pointwise
identity therefore survives every nested envelope, martingale-measure
optimization, finite-grid restriction, and maximization over the input prior.

## The two row combinations

Use the row labels of the accepted exact 30-row expansion.  The frontier
combination has the following nonzero weights:

| row | frontier weight \(\lambda\) |
|---|---:|
| `r1_c_1` | \(\epsilon\) |
| `r2_c_1` | \(\epsilon\) |
| `19l_a` | \(\epsilon\) |
| `19m` | \((1-\epsilon)/2\) |
| `19o` | \((1-3\epsilon)/2\) |
| `final_a_rml` | \(\epsilon\) |

Define instead the following combination:

| row | invariant weight \(\widetilde\lambda\) |
|---|---:|
| `r1_c_1` | \(\epsilon\) |
| `r2_a_1` | \(\epsilon\) |
| `19k_a` | \((1-\epsilon)/2\) |
| `19l_c` | \((1-\epsilon)/2\) |
| `final_a_rml` | \((1-\epsilon)/2\) |
| `final_c_rml` | \((1-\epsilon)/2\) |

All omitted weights are zero.  Both combinations are nonnegative on the
stated interval.  Exact addition gives coefficient one on each of $R_1,R_2$
for both combinations.

Under the accepted skew involution, the three nonzero row pairs in the new
combination are

\[
(`r1_c_1`,`r2_a_1`),\qquad
(`19k_a`,`19l_c`),\qquad
(`final_c_rml`,`final_a_rml`).
\]

The weights within every pair agree; all twelve other row pairs have two zero
weights.  Hence \(\widetilde\lambda\) is exactly skew-invariant.

In the accepted formal pair ordering this support is

\[
t_3=(1-\epsilon)/2,\qquad t_9=\epsilon,\qquad
t_{15}=(1-\epsilon)/2.
\]

The rank-eight quotient point is consequently

\[
(s_B,s_C,s_D,s_E,s_{N_0},s_{N_1},s_{F_0},s_{F_1})
=((1-\epsilon)/2,0,\epsilon,0,0,0,0,(1-\epsilon)/2),
\]

and its normalization is exposed exactly:

\[
2s_B+s_C+s_D+s_E=(1-\epsilon)+\epsilon=1.
\]

## Exact tensor identity

Expand both combinations using the posterior identities above.  Subtract the
new tensor from the frontier tensor.  Every $W,U,V$ coefficient is exactly
zero.  The only nonzero level-zero entries are

\[
\begin{array}{c|cc}
 &G&K\\ \hline
a&(3\epsilon-1)/2&0\\
b&(1-3\epsilon)/2&(1-\epsilon)/2\\
c&0&(\epsilon-1)/2.
\end{array}
\]

There are no $Y$ or $Z$ residuals.  Columnwise summation over the three
groups gives

\[
\frac{3\epsilon-1}{2}+\frac{1-3\epsilon}{2}=0,
\qquad
\frac{1-\epsilon}{2}+\frac{\epsilon-1}{2}=0.
\]

Since all groups share $q_0$, the residual contribution is identically

\[
0\cdot I_G(q_0)+0\cdot I_K(q_0)=0.
\]

The two weighted right sides are therefore equal for every hierarchy and
every receiver pair.  This proves the claim without symmetry of $G,K$,
without an envelope approximation, and without numerical evaluation.

## Row-level audit

For clarity, `verify.py` does not store the residual table as an assumption.
It independently constructs the ten distinct scalar rows appearing in the
two combinations from terms of the form

```text
(hierarchy group, mutual-information kind, receiver, sign)
```

and applies the seven posterior expansions displayed above.  Polynomial
weights are pairs of exact `Fraction` objects representing the constant and
linear coefficients in \(\epsilon\).  The verifier then checks:

- the rate vectors of both combinations are exactly `(1,1)`;
- all 15 skew-paired row weights agree in the new combination;
- the displayed rank-eight quotient coordinates satisfy normalization exactly;
- all nonconstant tensor differences vanish;
- the four stated constant residuals are exact; and
- the group-summed constant residual vanishes for each of $Y,Z,G,K$.

Run

```text
python3 submission/verify.py
python3 -O submission/verify.py
```

Both modes perform explicit exception-raising checks; Python assertions are
not used for correctness.

## Relation to the continuum-exchange search

The exact identity explains a repeated numerical phenomenon in adaptive
all-30-row contact exchange at the certified receiver: after missing
continuous contacts are restored, the optimized weights return to
six-row skew-paired representations with the frontier value.  Grid-only
decreases disappear under dense true-envelope reevaluation.  Those numerical
observations are motivation only and are not submitted as a bound or an
optimality theorem; the contribution here is the exact tensor identity.

## Scope and limitations

- No new capacity upper bound, lower bound, or achievable rate is claimed.
- The theorem proves that one important functional has an invariant
  representation.  It does not prove that every full-Theorem-9 optimum may be
  chosen invariant.
- It does not prove global or local optimality of the certified receiver pair,
  of \(\epsilon\), or of the six-row face.
- It does not exclude asymmetric receivers, larger auxiliary alphabets, or a
  different 30-row dual face.
- It does not reproduce the reported decimal near `0.369296340638082`.

The practical next step is therefore geometric: optimize genuinely different
points of the rank-eight invariant cone jointly with receiver posterior
measures, while running a parallel non-invariant separation oracle to detect
whether leaving that cone creates a stable continuous gain.
