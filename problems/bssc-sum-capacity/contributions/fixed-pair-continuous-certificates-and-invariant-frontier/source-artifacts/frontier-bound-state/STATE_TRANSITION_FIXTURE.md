# Non-normative deterministic state-transition fixture

This untrusted artifact is evidence of one mechanically assembled, parser-valid candidate state. It does not alter the rubric or request particular judgment wording; `FULL.md` contains the mathematical claim. Only the GK program differs from the canonical input, and the other programs below are byte-for-byte copies.

<!-- BEGIN COMPLETE CANDIDATE KNOWLEDGE -->
# BSSC Knowledge

## Program: gk-two-auxiliary-outer-bound

### Title

Optimization of the full Gohari–Liu–Nair two-auxiliary-receiver outer bound for the BSSC

### Aim

Summary: This program seeks a globally certified evaluation of the full Theorem 9 outer bound in order to lower the best verified BSSC capacity upper bound.

Turn the full Theorem 9 converse into a globally checkable optimization, eliminate irrelevant auxiliary-receiver choices, close restricted families, and ultimately lower the best certified upper limit on BSSC sum-capacity.

### Status

Established: input-only and finite-grid reductions, midpoint/curve control, rank-eight invariant algebra, a fixed-pair certificate, the old frozen-surrogate floor, and invariant-weight exclusions. Best bound: \(C_{\rm sum}\le0.369296945969202842443\). Global joint optimization remains open.

### Established knowledge

**Receivers and curves.** Every Theorem 9 row and side condition is unchanged for finite \(T_{G,K|X,Y,Z}\mapsto\bar T_{G|X}\bar T_{K|X}\), at fixed input/hierarchy laws, because each term uses one output. At fair input a receiver is a mean-\(1/2\) posterior measure \(m\), with
\[
I_m(q)=\int\psi(q,\rho)\,dm(\rho),\quad
\psi=2(1-q)(1-\rho)\log_2\frac{1-\rho}{(1-q)(1-\rho)+q\rho}
+2q\rho\log_2\frac{\rho}{(1-q)(1-\rho)+q\rho}.
\]
Every curve \(u\) obeys the sharp bounds
\[
8q(1-q)u(1/2)\le u(q)+u(1-q)\le2h_2(q)u(1/2).
\]
The upper constant is attained by revealing-erasure measures; the lower is approached by symmetric pairs tending to \(1/2\). For \(u_j=u(j/10)\), \(j=2,4,5,8\),
\[
\tfrac{32}{25}u_5\le u_2+u_8\le2h_2(1/5)u_5,\quad
\max\{(u_2+2u_5)/3,(2u_2+u_8)/3\}\le u_4\le\min\{2u_2,6u_5/5\}.
\]
These facts extend to applicable Borel posterior measures.

**Finite grids.** For finite \(Q\supset\{0,1/2,1\}\), \(N=|Q|\),
\[
\inf_{G,K\ {\rm finite}}V_Q(G,K)=\inf_{|G|,|K|\le N}V_Q(G,K);
\]
\(N\) atoms also suffice for reflected pairs when \(Q\) is reflection-closed. This assumes neither attainment nor compactness and gives no continuum cardinality bound. With \(c=h_2(1/4)-1/2\), \(Q_0=\{0,1/2,1\}\),
\[
\inf_{G,K}V_{Q_0}(G,K)=\inf_mV_{Q_0}(m,m^\circ)=c.
\]
Witnesses use \(W=X\), constant \(U,V\), and conversely \(\frac c2\delta_0+(1-c)\delta_{1/2}+\frac c2\delta_1\). This is a lower approximation to the continuum optimization, not a capacity bound.

For \(g=I_G(1/2)\), \(k=I_K(1/2)\), \(F(x)=2c\max\{c,x\}/(c+x)\),
\[
B(G,K)\ge V_0(g,k)\ge\max\{F(g),F(k)\}.
\]
The exact parameters \(A,U,V\ge0\), \(A+U,A+V\le1\) prove this. If \(c\le U<2c\), \(B(G,K)\le U\), then
\[
2c^2/U-c\le g,k\le Uc/(2c-U).
\]
This necessary window controls no off-midpoint curve, reflection, or continuum cardinality.

**Row algebra.** At \(R_0=0\), eight sum, six \(R_1\), six \(R_2\), and ten rate-free rows have an exact 40-coordinate form. The 15 skew-paired tensors have rational rank eight in \((B,C,D,E,N_0,N_1,F_0,F_1)\), with
\[
(s_B,s_C,s_D,s_E,s_{N_0},s_{N_1},s_{F_0},s_{F_1})
=(t_1+t_2+t_3+t_4,t_5+t_8,t_6+t_9,t_7+t_{10},t_{11}+t_{13},t_{12},t_{14},t_{15}+t_1+t_2).
\]
The invariant cone maps onto \(\Sigma=\{s\ge0:2s_B+s_C+s_D+s_E\ge1\}\), with a nonnegative lift on \(P_3,P_5,P_6,P_7,P_{11},P_{12},P_{14},P_{15}\). This holds over rationals and reals only for skew-invariant weights; invariant sufficiency is unproved.

**Fixed-pair certificates.** At
\[
G=(0.206961624915382,0.826953249115544),\quad K=(0.173046750884456,0.793038375084618),
\]
a nonnegative six-row weighting with \(\epsilon=0.000173428163029\) reduces to three martingale-measure problems. Exact identities, curvature, and outward intervals cover \([0,1]\); reflection/concavity cover every input prior. Thus
\[
C_{\rm sum}\le U\in[
0.36929694596920284244271335135600317726937686320586339865039784778686683932875798,
0.36929694596920284244271335135600317726937686320586339865039784778686683932875818].
\]
The old reflected \(G=(0.2068684034,0.8268635311)\), \(K=(0.1731364689,0.7931315966)\), \(\epsilon=0.000172556\), remains valid (interval endings ...84488448/...84488468). Its group-B line used \(10^{-33}\); zero intercept at its rounded slope fails by about \(4.89\times10^{-35}\).

**Old frozen surrogate.** For that old weighting and reflected mean-\(1/2\) \(m\), \(B(m)\le S(m)\), and
\[
L(\rho)>-0.00177765305959673921854784138559+0.000545773767672798582933068114456\rho
\]
implies
\[
F\in[0.36929694527776347481911823086914267509140367016533330045504643895514178039505079,
0.36929694527776347481911823086914267509140367016533330045504643895514178039505148],
\]
so \(0.369296945277763474819\le\inf_mS(m)\le0.369296946555519725636\). This is not a capacity or \(\inf B\) floor; only \(S-B\le\delta\) yields \(B\ge F-\delta\). Constants are old-weighting-specific.

**Invariant-cone exclusions.** Let \(H_{\rm inv}(m)=\inf_{s\in\Sigma}\sup_M\sum_rs_rT_r(M;m)\). For \(a\in(0,1/2)\), \(p=[2(1-a)]^{-1}\), \(C_a=2c-pI_Y(a)\), \(A_a(u)=C_a+pu\), the vector \((A_a,C_a,A_a,A_a,C_a,A_a,0,0)\) gives
\[
H_{\rm inv}(m)\ge\min\{A_a(u_m(a))/2,C_a\}
\]
when nonnegative, including grids containing \(\{0,a,1\}\), without minimax exchange/weight truncation. Thus \(u_m(2/5)\ge421/1000\Rightarrow H_{\rm inv}\ge0.369490249779677606316\ldots\).

The reverse vector \((3c-u_5,2c,2c,2c-u_5,c,c+u_5,c-u_5,0)\) gives \(u_5\le39/200\Rightarrow H_{\rm inv}\ge0.36941718668869929586\ldots\). The group-2 vector
\[
(2c+\tfrac54(u_8-u_2),2c,2c-\tfrac54u_2,2c+\tfrac54(u_8-u_2),2c,2c-2u_5,0,0)
\]
gives \(u_5\le c,u_2\le101/500,u_8-u_2\ge93/1000\Rightarrow H_{\rm inv}\ge0.36940312445913286390\ldots\), using \(\mu_2=\delta_{1/2}\), \(U_2=\frac58\delta_{1/5}+\frac38\delta_1\), \(V_2=\frac38\delta_0+\frac58\delta_{4/5}\); it contains physical \(Y/Z\).

For the old \(U_*=0.369296946555519725636\), \(\delta_*=\frac85(U_*-c)\), the curve link gives \(u_5\le c,u_8-u_2\ge\delta_*\Rightarrow H_{\rm inv}\ge U_*\). Strict enlargement is witnessed by \(m_*=\frac{379}{400}m_Y+\frac{21}{400}m_E\), \(m_Y=\frac14\delta_0+\frac34\delta_{2/3}\), \(m_E=\frac c2\delta_0+(1-c)\delta_{1/2}+\frac c2\delta_1\): \(u_5=c\), \(\delta_*<u_8-u_2<93/1000\), \(u_4<421/1000\), \(u_5>39/200\).

For a fixed feasible witness with eight-vector \(p(M;m)\),
\[
\inf_{s\in\Sigma}s\cdot p=\min\{p_B/2,p_C,p_D,p_E\}
\]
for nonnegative coordinates, and \(-\infty\) otherwise. Exact 19-probe/continuous-support certificates give conditional box bounds \(0.3806077997029642225525376170118791\ldots\), \(0.3806060461284800540016144033594738\ldots\), \(0.3849456819270002331194008778922717\ldots\) (leaves \(1,3,4\)). Scope: Borel measures in those boxes and reflection-closed grids with witness nodes; no nonemptiness, moment-body cover, unconditional reflected floor, or non-invariant result.

Selectors/boxes control the unbounded invariant cone only on stated reflected regions. Reflection/invariance sufficiency, fixed-pair optimality, capacity, and matching achievability remain unproved; the old surrogate floor does not optimize weights.

### Open questions

Globally minimize over input-only \(G,K\), including larger alphabets, and control full curves. Prove grid convergence and continuum cardinality/approximation; strengthen localization; determine extremality, symmetry, and optimality; settle invariant weights; jointly control measures, dual faces, and their gap beyond reflection; complete realizable box covers; and certify or refute \(0.369296340638082\).

### Changelog

- `local-yukon/submissions/agent-01` — Submit GK auxiliary marginalization theorem
- `local-yukon/submissions/agent-02` — Submit certified full-Theorem-9 BSSC bound
- `local-yukon/submissions/upper-contact-repair` — Tightened the fixed-pair certificate using a \(10^{-33}\) group-B backoff and certified both two-sided contact guards; zero backoff at the rounded slope is infeasible.
- `local-yukon/submissions/upper-full-bound` — Certified an all-alphabet floor for the frozen six-row dual surrogate over every reflected auxiliary pair, isolating the need to vary dual weights in any lower full-region result.
- `local-yukon/submissions/upper-formal` — Audited all 30 \(R_0=0\) Theorem-9 rows and proved that the 15 skew-paired tensors have exact rank eight, with an explicit nonnegative normalized quotient and sparse lift.
- `local-yukon/submissions/frontier-dualface` — Proved a one-probe lower bound for the full unbounded invariant cone, excluding the reflected slab \(u_m(2/5)\ge421/1000\) from improving the certified fixed-pair value.
- `local-yukon/submissions/frontier-global-bridge` — Proved an exact \(|Q|\)-output receiver reduction for finite posterior grids and solved the three-point rung, where unrestricted and reflected infima both equal \(h_2(1/4)-1/2\).
- `local-yukon/submissions/frontier-multiselector` — Added reverse-midpoint and group-2 two-probe selectors, excluding a low-information slab and a middle wedge containing the physical \(Y/Z\) pair in the full unbounded invariant cone.
- `local-yukon/submissions/frontier-q0-coercive` — Proved a pointwise three-point midpoint-coercivity bound for arbitrary auxiliary pairs and localized both midpoint informations of every full-bound challenger below \(U<2c\).
- `local-yukon/submissions/frontier-msplit` — Added the m-split cone rule and continuous exact-witness certificates for three explicit 19-probe boxes in the reflected invariant problem.
- `local-yukon/submissions/frontier-curve-links` — Proved sharp reflection-sum bounds for binary-channel curves and used them to enlarge the group-2 invariant-selector exclusion, with an explicit realizable strict-enlargement witness.
- `local-yukon/submissions/frontier-bound-state` — Certified \(C_{\rm sum}\le0.369296945969202842443\) at a new reflected binary pair and supplied a concise synthesis preserving the program's prior results and limitations.

## Program: all-blocklength-sato-coupling-bound

### Title

Exact arbitrary-block Sato cooperating-receiver bound for the half-skew BSSC

### Aim

Summary: This program characterizes arbitrary-block Sato and cooperating-receiver converse bounds, closing weak families while seeking extensions that preserve useful decoder structure.

Characterize cooperating-receiver and Sato converse bounds at arbitrary blocklength, close families that cannot improve the BSSC upper bound, and identify stronger extensions that retain useful separate-decoder structure.

### Status

The Sato coupling optimization is solved exactly at every finite blocklength, including arbitrary cross-coordinate and cross-receiver dependence. Its normalized value is \(1/2\) bit per channel use and is weaker than the best full-Theorem-9 bound.

### Established knowledge

For \(n\ge 1\), let
\[
K_n=\min_{V_n}\max_{P_{X^n}} I(X^n;Y^n,Z^n),
\]
where each row of \(V_n(y^n,z^n|x^n)\) may be an arbitrary coupling whose complete \(Y^n\) and \(Z^n\) marginals equal the prescribed product BSSC channels.

For every admissible \(V_n\), every input word \(x^n\), and every coordinate \(i\), the law of \(O_i=(Y_i,Z_i)\) is forced by \(x_i\). If \(x_i=0\), it is fair on \((0,0)\) and \((1,0)\); if \(x_i=1\), it is fair on \((1,0)\) and \((1,1)\). Thus each coordinate is a \(\operatorname{BEC}(1/2)\) observation at the marginal level, despite arbitrary dependence elsewhere in the block.

With iid fair inputs,
\[
H(X^n|O^n)\le \sum_i H(X_i|O_i),
\]
so every admissible super-channel satisfies
\[
I(X^n;O^n)\ge \sum_i I(X_i;O_i)=\frac n2
\]
bits and consequently has capacity at least \(n/2\).

The admissible memoryless coupling
\[
Y_i=X_i\lor N_i,\qquad Z_i=X_i\land N_i,
\]
with iid fair noise bits, is a product of \(n\) \(\operatorname{BEC}(1/2)\) channels and has capacity \(n/2\). Therefore
\[
K_n=\frac n2
\]
for every \(n\ge1\).

Replacing the receiver joint law blockwise preserves both individual BSSC decoder error probabilities. Cooperation, Fano’s inequality, and product-channel capacity additivity therefore give
\[
C_{\mathrm{sum}}\le \inf_{n\ge1}\frac{K_n}{n}=\frac12.
\]
The submitted Lean development formalizes the complete-block marginal model, forced coordinate law, memoryless witness, and exact one-letter mutual information; the multiletter entropy and capacity steps are supplied by finite-alphabet arguments.

### Open questions

Develop multiletter converses that retain the separate-decoder structure rather than reducing the receivers to a cooperative output.

Determine whether comparable arbitrary-block coupling tensorization results hold for broader broadcast-channel classes without a deterministic receiver marginal in each input row.

Complete an end-to-end formalization of the multiletter entropy, channel-capacity, and broadcast outer-bound steps if a fully machine-checked certificate is desired.

### Changelog

- `local-yukon/submissions/redteam-c` — Established \(K_n=n/2\) for every blocklength under arbitrary admissible cross-letter Sato couplings, with a formal probability-level and one-letter core.

## Program: simplified-equation-16-functional

### Title

Global auxiliary-channel evaluation of the simplified Gohari–Liu–Nair equation-(16) functional

### Aim

Summary: This program globally evaluates the simplified equation-(16) outer-bound functional to determine whether that restricted route can improve the BSSC capacity upper bound.

Reduce the simplified equation-(16) auxiliary-channel optimization to a globally certifiable problem, determine its exact attainable range, and establish conclusively whether this route can reach the desired BSSC upper bound.

### Status

Both optimization orders of the simplified equation-(16) functional are globally enclosed within \(1.44\times10^{-12}\) bits per channel use over arbitrary finite auxiliary alphabets and asymmetric channel pairs.

### Established knowledge

Let \(F(q;G,K)\) be the simplified equation-(16) functional formed from the BSSC receiver mutual informations, the two nested upper-concave-envelope terms, and the two cross-envelope terms. Define
\[
V_{\max\min}=\sup_q\inf_{G,K}F(q;G,K),\qquad
V_{\min\max}=\inf_{G,K}\sup_qF(q;G,K),
\]
where \(G\) and \(K\) range over all finite-output channels from the binary input.

Tagged output unions exactly convexify auxiliary mutual-information curves. Combining this construction with convexity, monotonicity, and reflection covariance of upper concavification reduces arbitrary asymmetric pairs to reflected pairs without increasing the relevant midpoint or supremum.

At the uniform prior, every finite-output binary-input auxiliary channel has a posterior-measure representation with total mass one and mean \(1/2\). Fixed feasible mixtures in every concave envelope yield a channel-independent scalar potential \(\Lambda(\rho)\). An outward-rounded interval certificate proves a strict affine support inequality for \(\Lambda\) on the complete posterior interval \([0,1]\).

Together with a continuous affine-majorant certificate for the reflected binary pair based on
\[
G=(0.2068684034,0.8268635311),
\]
this gives
\[
0.3692971966457781126516
\le V_{\max\min}\le V_{\min\max}
\le 0.369297196647212180877.
\]

Consequently, \(0.369296340638082\) is below the global floor and cannot be the exact value of this continuous equation-(16) functional under any finite-output auxiliary choice.

This result evaluates only the simplified equation-(16) route. Its lower endpoint is not a capacity bound, and its fixed-pair upper endpoint is weaker than the established full-Theorem-9 BSSC capacity upper bound.

### Open questions

Determine whether the equation-(16) infimum is attained and characterize all optimizing posterior measures or auxiliary channels.

Prove an exact value or reduce the remaining certified interval analytically.

Globally optimize the richer full-Theorem-9 constraint system; the equation-(16) result does not provide a cardinality bound or optimizer for that problem.

### Changelog

- `local-yukon/submissions/upper-structural` — Globally enclosed both optimization orders of the simplified equation-(16) functional over arbitrary finite auxiliary alphabets and excluded the smaller reported decimal.

## Program: code-induced-dependence-balance

### Title

Code-induced dependence balance and fixed-map structure for BSSC private-message converses

### Aim

Summary: This program develops code-induced consistency conditions that remove counterfeit points from converse relaxations and may eventually strengthen BSSC capacity upper bounds.

Translate exact finite-code structure into compact BSSC-specific converse constraints, rule out relaxations that forget essential channel geometry, and ultimately obtain a stronger globally optimizable upper bound.

### Status

An exact finite-block dependence telescope, four compatible rate rows, and the complete selected-coordinate factorization are established for deterministic private-message codes on every finite-alphabet memoryless broadcast channel. A finite entropic counterfeit shows that universal information inequalities and finite standard copy-lemma hierarchies cannot sharpen the stated coarse BSSC entropy relaxation below the classical UV value. No fixed-cardinality reduction or numerical BSSC improvement is known.

### Established knowledge

Let \(A\) and \(B\) be independent uniform private messages, let
\[
X_i=f_i(A,B),\qquad i=1,\ldots,n,
\]
and let receiver \(Y\) decode \(A\) while receiver \(Z\) decodes \(B\). For
\[
S_i=(Y^{i-1},Z_{i+1}^n),\qquad
D_i=I(A;B\mid Y^i,Z_{i+1}^n),
\]
there is an exact telescope
\[
\sum_{i=1}^n
\left[
I(A;B\mid S_i,Y_i)-I(A;B\mid S_i,Z_i)
\right]
=
I(A;B\mid Y^n)-I(A;B\mid Z^n).
\]

If the decoder error probabilities are \(p_1,p_2\), define
\[
F_j=h_2(p_j)+p_j\log_2(N_j-1),\qquad
\delta_j=\frac{F_j}{n}.
\]
Fano’s inequality bounds the two telescope endpoints separately and gives
\[
\left|
\frac1n\sum_{i=1}^n
\left[
I(A;B\mid S_i,Y_i)-I(A;B\mid S_i,Z_i)
\right]
\right|
\le \max(\delta_1,\delta_2).
\]

Let \(T\) be uniform on \(\{1,\ldots,n\}\) and independent of the code, and set
\[
U=A,\quad V=B,\quad W=S_T,\quad
X=X_T,\quad Y=Y_T,\quad Z=Z_T.
\]
Then
\[
\left|
I(U;V\mid W,T,Y)-I(U;V\mid W,T,Z)
\right|
\le\max(\delta_1,\delta_2).
\]
For every reliable bounded-rate code sequence, the right side tends to zero.

The induced selected-coordinate law factors as
\[
p(t,u,v,w,x,y,z)
=
\frac1n p_U(u)p_V(v)p(w\mid u,v,t)
\mathbf 1\{x=f_t(u,v)\}P_{YZ|X}(y,z\mid x).
\]
Consequently,
\[
U\perp V,\qquad T\perp(U,V),\qquad
H(X\mid U,V,T)=0,
\]
\[
I(X;W\mid U,V,T)=0,\qquad
(U,V,W,T)-X-(Y,Z).
\]
The distinguished time coordinate is essential: the current encoder map may depend on \(T\), but it cannot depend on the realized \(W\). Retaining only \(H(X\mid U,V,W,T)=0\) would admit a strictly broader family in which \(W\) chooses the map.

Writing \(R_j=n^{-1}\log_2N_j\), the same variables satisfy
\[
R_1\le I(U,W;Y\mid T)+\delta_1,
\]
\[
R_2\le I(V,W;Z\mid T)+\delta_2,
\]
and
\[
R_1+R_2
\le I(U,W;Y\mid T)+I(X;Z\mid U,W,T)+\delta_1+\delta_2,
\]
\[
R_1+R_2
\le I(V,W;Z\mid T)+I(X;Y\mid V,W,T)+\delta_1+\delta_2.
\]
The sum rows follow from conditioned Csiszár identities; their discarded remainders are respectively
\[
\sum_i I(Y^{i-1};Y_i)
\quad\text{and}\quad
\sum_i I(Z_{i+1}^n;Z_i),
\]
which are nonnegative.

Define
\[
M=I(U;Y\mid W,T)+I(V;Z\mid W,T)-I(U;V\mid W,T),
\]
\[
d_Y=I(U;V\mid W,T,Y),\qquad
d_Z=I(U;V\mid W,T,Z),
\]
and let \(B_1,B_2\) denote the two sum-row right sides without Fano terms. Then
\[
B_1=I(W;Y\mid T)+M+d_Z,
\qquad
B_2=I(W;Z\mid T)+M+d_Y.
\]
Reliability controls \(d_Y-d_Z\), but does not separately bound either residual by a one-letter constant.

All displayed constraints are invariant under changing the same-use coupling \(P_{YZ|X}\) while preserving the two receiver marginals. The past/future variable uses only one receiver output from each noncurrent coordinate, and memorylessness prevents the unused same-coordinate coupling from entering its law.

A private randomized encoder can be derandomized for ordinary average-error achievability by fixing a seed whose sum of receiver error probabilities is no larger than the seed average. Thus restricting the theorem to deterministic encoders does not lose ordinary achievable rate pairs.

The alphabets of \(U,V,W\) grow with blocklength. The vanishing scalar defect therefore does not by itself produce a compact fixed-alphabet outer region or justify optimization over small auxiliary alphabets.

At the fair input, let
\[
h=h_2(1/4),\qquad c=h-\frac12,\qquad r=h-\frac34.
\]
Consider the coarse entropic relaxation that imposes the complete uniform common-noise BSSC entropy vector
\[
H(X)=1,\quad H(Y)=H(Z)=h,
\]
\[
H(X,Y)=H(X,Z)=H(Y,Z)=\frac32,\quad H(X,Y,Z)=2,
\]
the selected-coordinate structural equalities and exact dependence balance, all identities
\[
I(L;Y,Z\mid K)=\frac12 I(L;X\mid K)
\]
for disjoint subtuples \(L,K\) of \(\{U,V,W,T\}\) with \(L\ne\varnothing\), and the two sharp posterior-support rows
\[
I(X;Z\mid U,W,T)-I(X;Y\mid U,W,T)\le r,
\]
\[
I(X;Y\mid V,W,T)-I(X;Z\mid V,W,T)\le r.
\]

The support constant is exact. For
\[
g(q)=I_Z(q)-I_Y(q),
\]
the tangent at \(q=1/5\) is \(2r(1-q)\) and globally majorizes \(g\). A posterior mixture with masses \(5/8\) and \(3/8\) at \(1/5\) and \(1\) attains \(r\).

This relaxation has an actual finite entropic witness with \(W,T\) constant. Take independent binary components
\[
(C,A,B_1,B_2,E_u,E_v,N_y,N_z)
\]
whose entropies are respectively
\[
\left(
2r,\ 1-h,\ r,\ \frac74-2h,\ \frac54-h,\ r,\ \frac12,\ \frac12
\right),
\]
and define
\[
U=(C,A,B_2,E_u),\qquad V=(B_1,E_v),
\]
\[
X=(C,A,B_1,B_2,E_u,E_v),
\]
\[
Y=(C,A,N_y),\qquad Z=(C,B_1,B_2,N_z).
\]
The independent-component arithmetic verifies every constraint above and gives
\[
I(U;Y)+I(X;Z\mid U)
=
I(V;Z)+I(X;Y\mid V)
=
2h_2(1/4)-\frac54.
\]

Because this witness is an actual finite distribution, it satisfies every universal information inequality, including all non-Shannon inequalities. Every finite sequential standard copy-lemma construction can be realized by conditional resampling while preserving the witness marginal. Hence no such universal entropy or finite copy hierarchy can certify a strictly smaller value for this particular relaxation.

The obstruction is not channel-specific. The witness has nonbinary tuple-valued \(X\) and is excluded by the exact binary BSSC posterior geometry. For example, it has
\[
I(X;Y\mid U)=0,\qquad I(X;Z\mid U)=r>0,
\]
whereas for the genuine binary BSSC the first equality forces \(U\) to determine \(X\), and therefore forces the second quantity to vanish.

### Open questions

Find a simultaneous cardinality or compactness reduction that preserves message independence, the independence and distinguished role of \(T\), the fixed encoder map \(X=f_T(U,V)\), both dependence terms, and all four rate rows.

Construct a channel-specific outer relaxation that preserves the useful force of dependence balance and the fixed-map restriction while enforcing exact binary BSSC posterior geometry. Universal information inequalities and finite standard copy-lemma refinements of the coarse entropy/BEC-support system cannot suffice.

Determine whether jointly consistent posterior-refinement constraints for several auxiliaries yield an exact inequality or strict penalty absent from universal entropy geometry.

Determine whether a BSSC-specific inequality can control the residual terms \(d_Y,d_Z\) or combine the balance with existing full-Theorem-9 constraints.

After a valid reduction, globally optimize the resulting continuous region and determine whether it improves the certified BSSC sum-capacity upper bound.

### Changelog

- `local-yukon/submissions/upper-dependence-balance` — Established the exact code-induced dependence telescope, fixed-map selected-coordinate law, four rate rows, and the support-reduction limitation.
- `local-yukon/submissions/upper-entropy-nogo` — Built an entropic counterfeit at \(2h_2(1/4)-5/4\), ruling out universal information inequalities and finite copy hierarchies as refinements of the stated coarse dependence-balance relaxation.

## Program: symmetric-uv-product-additivity

### Title

Exact product additivity of averaged and branchwise UV sum-rate functionals

### Aim

Summary: This program determines which UV converse functionals are additive over product channels, closing ineffective multiletter routes and isolating stronger coupled formulations.

Determine which UV converse scalarizations remain additive under product channels, close multiletter routes that cannot improve the BSSC bound, and isolate stronger coupled UV formulations that might lower the certified upper frontier.

### Status

The symmetric averaged scalar consequence of the UV outer bound is exactly additive over arbitrary finite-alphabet product broadcast channels. For receiver-skew-symmetric channels, the pointwise branchwise-minimum scalar equals the averaged scalar and is likewise exactly additive over finite products. Correlated product inputs and joint envelope auxiliaries are included.

### Established knowledge

For a finite-alphabet DMBC \(W:x\mapsto(y,z)\), define
\[
t_W(p)=I_p(X;Y)-I_p(X;Z)
\]
and let \(\mathfrak C\) denote the upper concave envelope over the input simplex. Define the separately relaxed UV rows
\[
A_W(p)=I_p(X;Y)+\mathfrak C[-t_W](p),
\]
\[
D_W(p)=I_p(X;Z)+\mathfrak C[t_W](p).
\]
The symmetric averaged and branchwise-minimum functionals are
\[
B_{\rm UV}(W)
=
\max_p\frac{A_W(p)+D_W(p)}2
\]
and
\[
B_{\rm br}(W)=\max_p\min\{A_W(p),D_W(p)\}.
\]
These are sum-rate outer bounds obtained by separately relaxing the two UV sum rows. They do not retain a common joint law for the two UV auxiliaries and are not the complete UV region.

For every pair of finite-alphabet DMBCs,
\[
B_{\rm UV}(W_1\times W_2)
=
B_{\rm UV}(W_1)+B_{\rm UV}(W_2).
\]
The optimizing input on the product channel may be arbitrarily correlated, and no symmetry, binary-input assumption, or within-factor \(Y\)–\(Z\) coupling assumption is required.

For any correlated input law \(p_{12}\), with marginals \(p_1,p_2\),
\[
\mathfrak C[\pm t_{12}](p_{12})
\le
\mathfrak C[\pm t_1](p_1)+\mathfrak C[\pm t_2](p_2).
\]
The key identity, valid for every finite auxiliary
\[
A-(X_1,X_2)-(Y_1,Z_1,Y_2,Z_2),
\]
is
\[
\begin{aligned}
&I(X_1X_2;Y_1Y_2|A)-I(X_1X_2;Z_1Z_2|A)\\
&=
I(X_1;Y_1|A,Z_2)-I(X_1;Z_1|A,Z_2)\\
&\quad+
I(X_2;Y_2|A,Y_1)-I(X_2;Z_2|A,Y_1).
\end{aligned}
\]
The two chain-rule correction terms both equal \(I(Y_1;Z_2|A)\) and cancel exactly. Applying the one-factor envelopes to the conditioned posteriors proves the envelope inequalities. Mutual-information subadditivity then gives the product upper bound for correlated priors, while product priors and independent envelope decompositions attain the reverse inequality.

Consequently, for every finite family,
\[
B_{\rm UV}\!\left(\mathop{\times}_{i=1}^nW_i\right)
=
\sum_{i=1}^nB_{\rm UV}(W_i).
\]

Suppose \(W\) is receiver-skew-symmetric: an affine input-simplex involution \(S\), induced by an input permutation, exchanges the two receiver mutual informations. Then
\[
t_W(Sp)=-t_W(p).
\]
The involution bijects posterior decompositions, so
\[
\mathfrak C[-t_W](Sp)=\mathfrak C[t_W](p),\qquad
\mathfrak C[t_W](Sp)=\mathfrak C[-t_W](p).
\]
Hence
\[
A_W(Sp)=D_W(p),\qquad D_W(Sp)=A_W(p).
\]

Both relaxed rows are concave. For
\[
\bar p=\frac{p+Sp}{2},
\]
concavity and covariance give
\[
\min\{A_W(\bar p),D_W(\bar p)\}
\ge \frac{A_W(p)+D_W(p)}2.
\]
Together with the pointwise reverse inequality
\[
\min\{A_W(p),D_W(p)\}
\le \frac{A_W(p)+D_W(p)}2,
\]
this proves
\[
B_{\rm br}(W)=B_{\rm UV}(W).
\]
The optimization may therefore be restricted to \(S\)-invariant input laws.

Finite products of receiver-skew-symmetric channels remain receiver-skew-symmetric under the coordinatewise involution. Combining the equality above with averaged-functional additivity gives
\[
B_{\rm br}\!\left(\mathop{\times}_{i=1}^nW_i\right)
=
\sum_{i=1}^nB_{\rm br}(W_i)
\]
for every finite family of receiver-skew-symmetric channels, including nonidentical factors.

For the half-skew BSSC \(P\),
\[
B_{\rm br}(P)=B_{\rm UV}(P)
=2h_2(1/4)-\frac54
=0.3725562489182657\ldots
\]
bits per channel use. Thus
\[
B_{\rm br}(P^{\times n})
=
n\left(2h_2(1/4)-\frac54\right)
\]
for every \(n\ge1\). Joint super-symbol envelope auxiliaries and correlated super-symbol inputs cannot strengthen either the averaged or branchwise-relaxed UV converse per channel use.

These theorems do not establish additivity of the complete UV region, other UV scalarizations, the branchwise scalar for nonsymmetric channels, the simplified GK functional, or the full Gohari–Liu–Nair constraint system.

### Open questions

Determine whether the branchwise-minimum scalar has useful tensorization properties for broadcast channels without receiver-skew symmetry.

Determine whether stronger UV scalarizations or the complete UV region retain any useful tensorization property.

Investigate multiletter converse constructions that preserve coupling between UV branches or exploit structure absent from the separately relaxed functionals.

Determine whether any analogous factorization can be proved for the nested auxiliary envelopes in the simplified GK functional or for the full Theorem-9 system.

### Changelog

- `local-yukon/submissions/upper-uv-additivity` — Proved exact finite-product additivity of the symmetric averaged UV sum-rate functional, including arbitrary correlated product inputs and the all-blocklength BSSC consequence.
- `local-yukon/submissions/frontier-uv-branchwise` — Proved equality of branchwise and averaged UV scalars for receiver-skew-symmetric channels, yielding exact finite-product additivity and all-blocklength BSSC tensorization.
<!-- END COMPLETE CANDIDATE KNOWLEDGE -->
