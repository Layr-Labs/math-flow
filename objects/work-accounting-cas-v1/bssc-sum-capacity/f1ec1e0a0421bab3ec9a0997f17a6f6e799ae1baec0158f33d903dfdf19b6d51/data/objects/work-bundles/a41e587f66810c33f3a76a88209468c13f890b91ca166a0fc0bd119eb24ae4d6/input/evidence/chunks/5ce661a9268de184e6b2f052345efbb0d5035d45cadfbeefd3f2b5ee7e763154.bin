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
