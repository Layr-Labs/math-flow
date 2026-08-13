# Compact certificate for a strictly improved BSSC upper bound

## Claim

For the half-skew BSSC, choose the exact reflected binary auxiliary pair

\[
G=(0.206961624915382,0.826953249115544),\qquad
K=(0.173046750884456,0.793038375084618).
\]

The included continuous weak-duality certificate proves

\[
\begin{aligned}
C_{\rm sum}\le U\in[&0.36929694596920284244271335135600317726937686320586339865039784778686683932875798,\\
&0.36929694596920284244271335135600317726937686320586339865039784778686683932875818].
\end{aligned}
\]

Thus the upward-rounded headline is

\[
\boxed{C_{\rm sum}\le0.369296945969202842443}.
\]

The upper endpoint is below the prior canonical certified upper endpoint
`0.36929694655551972563539254207215942386102502532943886683678450695288358384488468`
by `5.8631688319267919072e-10` (and hence also below its rounded headline
`0.369296946555519725636`).  Search numerics are not evidence: every decimal
below is frozen as an exact rational and all continuous inequalities are
recertified by `verify.py`.

## Six-row dual and posterior reduction

Let \(I_A(q)\) be the mutual information of binary-input channel \(A\) at
\(P(X=1)=q\).  For a hierarchy \((U,V,W)-X-A\),

\[
\begin{aligned}
I(W;A)&=I_A(q_0)-\mathbb E I_A(q_W),\\
I(U;A|W)&=\mathbb E I_A(q_W)-\mathbb E I_A(q_U),\\
I(U,W;A)&=I_A(q_0)-\mathbb E I_A(q_U),\\
I(X;A|U,W)&=\mathbb E I_A(q_U),
\end{aligned}
\]

and similarly for \(V\).  Posterior laws obey
\(\mathbb E[q_U|q_W]=\mathbb E[q_V|q_W]=q_W\) and
\(\mathbb E q_W=q_0\).  Retaining only these martingale constraints relaxes
the genuine auxiliary problem, so its dual still upper-bounds every Theorem 9
structure.

Write \(W_g(A)=I(W_g;A)\), \(U_g(A)=I(U_g;A|W_g)\), and likewise
\(V_g,UW_g,VW_g,X|UW_g,X|VW_g\).  The six accepted scalar Theorem 9 rows
used here are

\[
\begin{aligned}
R_1\le{}&W_c(Z)+U_a(Y)+W_a(G)-W_b(G)+W_b(K)-W_c(K)+UW_b(G)-UW_a(G),\\
R_2\le{}&W_c(Z)+V_c(Z)+VW_b(K)-VW_c(K),\\
R_1+R_2\le{}&W_a(Y)+W_c(K)-W_b(K)+W_b(G)-W_a(G)+VW_a(G)-VW_b(G)\\
&+VW_b(K)-VW_c(K)+V_c(Z)+X|VW_a(Y),\\
R_1+R_2\le{}&W_a(Y)+U_a(Y)+V_c(Z)+UW_b(G)-UW_a(G)-V_c(K)+X|UW_b(K),\\
R_1+R_2\le{}&W_c(Z)+U_a(Y)+V_c(Z)+VW_b(K)-VW_c(K)-U_a(G)+X|VW_b(G),\\
0\le{}&U_a(Y)-U_a(G)-X|VW_a(Y)+X|VW_a(G).
\end{aligned}
\]

The last line is the final \(a\)-side condition in right-minus-left form; its
sign is positive in the combination.  Freeze

\[
\epsilon=0.000173428163029,
c_1=(1-\epsilon)/2,\quad c'_1=(1+\epsilon)/2.
\]

The row weights, in displayed order, are

\[
(\epsilon,\epsilon,\epsilon,\tfrac12-\tfrac\epsilon2,
\tfrac12-\tfrac{3\epsilon}2,\epsilon).
\]

They are nonnegative and their exact \(R_1,R_2\) coefficients both equal
one.  Exact expansion gives constant term
\(c'_1(I_Y(q_0)+I_Z(q_0))\) and the following three posterior groups:

\[
\begin{array}{c|ccc}
 &f_W&f_U&f_V\\ \hline
a&c_1(I_Y-I_G)&I_G-I_Y&0\\
b&0&c_1I_K-c'_1I_G&c_1I_G-c'_1I_K\\
c&c_1(I_Z-I_K)&0&I_K-I_Z.
\end{array}
\]

The verifier transcribes all six rows term by term and checks the rate sums
and complete tensor against this table using exact `Fraction` arithmetic.

## Weak-duality certificate

For each group, affine inner lines and an outer line satisfy

\[
L_U(w;q)\ge f_U(q),\quad L_V(w;q)\ge f_V(q)\quad(0\le w,q\le1), \tag{D1}
\]

\[
\alpha+\beta w\ge f_W(w)+L_U(w;w)+L_V(w;w)\quad(0\le w\le1). \tag{D2}
\]

Conditional posterior means turn the expectation of each inner affine line
at \(q_U,q_V\) into its value at \(q_W\); (D2) and
\(\mathbb E q_W=q_0\) then give

\[
B(q_0)=c'_1(I_Y(q_0)+I_Z(q_0))+\sum_g(\alpha_g+\beta_gq_0). \tag{1}
\]

No strong duality or exact contact assumption is used.

Put \(h=I_G-I_Y\) and \(h_C=I_K-I_Z=h(1-\cdot)\).  The frozen constants are

```text
T_A     .223554338099290337686997491745
M_A0    .114270117882180886477206425091
M_A1    .768484852026196875796918575693
BETA_A  .0455668698298748564310479904957
ALPHA_A .00484278650837243101713855267415
CI_A    .606174265413707974748966890325
M_BV    .770453933591712211652688419314
SLOPE_V .00271239427013419822092236108071
ICPT_V  1e-18
```

For group \(a\), use the tangent to \(h\) at \(w\) for \(w\le T_A\), the
fixed tangent at \(T_A\) for \(w\ge T_A\), and outer line
\(\alpha_A+\beta_Aw\).  Group \(c\) is its exact reflection:

\[
T_C=1-T_A,\quad\alpha_C=\alpha_A+\beta_A,\quad\beta_C=-\beta_A.
\]

For group \(b\), the fixed inner lines are

\[
\ell_V(q)=10^{-18}+s q,qquad
\ell_U(q)=10^{-18}+s-s q,qquad s=\mathrm{SLOPE_V},
\]

and their constant sum is the outer line.

### Continuous coverage

For \(a=G(0|0)\), \(d=G(0|1)-a\), the sign of

\[
\ln(2)(a+dq)(1-a-dq)(1-q^2)h''(q)
\]

equals the sign of the affine polynomial

\[
S(q)=a(1-a)-d^2+d(1-2a)q. \tag{2}
\]

Exact rational checks locate its unique zero \(c\) and prove the required
concave/convex regions.  For the tangent \(T_w\), concavity gives
\(T_w(c)\ge h(c)\).  With
\(\phi(w)=T_w(1)=h(w)+(1-w)h'(w)\),
\(\phi'(w)=(1-w)h''(w)<0\) on \([0,T_A]\), so
\(T_w(1)=\phi(w)\ge\phi(T_A)>0=h(1)\).  Thus \(T_w\) dominates the
endpoint chord on \([c,1]\), while convexity puts \(h\) below that chord.
The remaining strict check is the outward-certified

\[
h(T_A)+(1-T_A)h'(T_A)>7.009573\times10^{-33}>0.
\]

Reflection handles group \(c\).  For group \(b\), convexity at each contact
window follows from exact positivity of the relevant rational quadratic
\(c_1m_K(1-m_K)-c'_1m_G(1-m_G)\).

The verifier covers every remaining point as follows (\(\Delta=1/16\)):

| gaps | certified region and method |
|---|---|
| A1, A2, A2 | \([0,T_A]\) tangent at \(M_{A0}\); \([T_A,CI_A]\) endpoints; \([M_{A1}-\Delta,M_{A1}+\Delta]\) tangent |
| reflected C1, C2, C2 | the three reflected regions and the same methods |
| BV, BU | full two-sided \(\Delta\)-windows at \(M_{BV}\) and \(1-M_{BV}\), by tangent bounds |
| regular A2 | \([CI_A,M_{A1}-\Delta]\), \([M_{A1}+\Delta,1]\), by interval cover |
| regular C2 | the two reflected intervals, by interval cover |
| regular BV, BU | both sides outside each contact window, by interval cover |

The eight special tangent/endpoint bounds have positive directed floors; the
eight regular interval covers use natural and centered forms, total 136 cells,
maximum depth 30, and smallest reported margin about `6.193321e-19`.  Any
unresolved cell, excessive depth, or exhausted cell budget aborts.

## Every input prior and certified value

The exact tensor audit gives

\[
c_Y=c_Z=c'_1\ge0,qquad c_G=c_K=0,qquad
\beta_a+\beta_b+\beta_c=0.
\]

Thus (1) is concave and, using \(I_Z(q)=I_Y(1-q)\), symmetric about
\(q_0=1/2\).  Its global maximum over every \(q_0\in[0,1]\) is therefore
\(B(1/2)=U\), not merely a fair-prior sample.

## Reproduction, effect, and scope

Run `python3 -B verify.py`.  The source uses 80-digit directed Decimal
intervals; each correctly-rounded `Decimal.ln` result is expanded by one
representable number on both sides, and entropy endpoint cells use monotonic
enclosures.  It reruns every exact and continuous check under ambient contexts
`(prec=5, UP)`, `(7, FLOOR)`, and `(3, CEILING)` and requires the complete
evidence tuple and final interval to remain identical.  The run prints `PASS`,
the interval above, its strict margin, and the cover size.

`STATE_TRANSITION_FIXTURE.md` records a mechanically assembled, parser-valid,
non-normative candidate knowledge state for comparison.

The certified endpoint is strictly below the currently recorded fixed-pair
endpoint while using the same accepted six-row architecture.  It is only a
certificate at one reflected binary pair and one dual face: it does not prove
global receiver/weight optimality, binary or reflection sufficiency, a
matching achievable rate, or the exact BSSC sum-capacity.
