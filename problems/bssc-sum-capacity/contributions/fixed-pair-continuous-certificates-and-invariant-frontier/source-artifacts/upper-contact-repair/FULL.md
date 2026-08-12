# Microscopic-backoff repair of the continuous full-Theorem-9 BSSC certificate

## Contribution

For the binary skew-symmetric broadcast channel with skew parameter one half and private messages only, this submission proves the computer-assisted bound

~~~text
C_sum <= 0.369296946555519725636 bits per channel use.
~~~

More precisely, the exact certificate encloses the dual value U in

~~~text
[0.36929694655551972563539254207215942386102502532943886683678450695288358384488448,
 0.36929694655551972563539254207215942386102502532943886683678450695288358384488468].
~~~

This is a continuous weak-duality certificate. It covers every input prior and every posterior measure induced by the auxiliary random variables. It is not a sampled-grid claim.

The current knowledge state already records a continuous certificate at this
fixed reflected channel using group-B chord lines with an upward intercept of
`10^-18`.  The exact zero-intercept line at the submitted rounded slope is in
fact infeasible by about `4.90e-35` near its interior contact.  The present
contribution replaces the old backoff by `10^-33`, explicitly covers both
previously omitted two-sided contact guards, and certifies strict feasibility
on them.  This reduces the group-B backoff by fifteen orders of magnitude and
tightens the recorded bound by approximately `2.0e-18`, without making a false
claim of exact contact attainment.

## Channel, rates, and scope

The physical BSSC is

~~~text
P(Y|X) = [[1/2, 1/2],
          [0,   1  ]]

P(Z|X) = [[1,   0  ],
          [1/2, 1/2]]
~~~

with binary input X, no common message, base-two logarithms, and private-message sum-capacity

~~~text
C_sum = sup { R1 + R2 : (R1,R2) is achievable }.
~~~

Write q = P(X=1) and h2 for binary entropy. The physical mutual-information curves are

~~~text
I_Y(q) = h2((1-q)/2) - (1-q),
I_Z(q) = h2(q/2) - q = I_Y(1-q).
~~~

Choose the following exact-decimal binary auxiliary receivers:

~~~text
G = (P(G=0|X=0), P(G=0|X=1))
  = (0.2068684034, 0.8268635311),

K = (P(K=0|X=0), P(K=0|X=1))
  = (0.1731364689, 0.7931315966).
~~~

Thus K is the input/output reflection of G. If a = 0.2068684034, b = 0.8268635311, and d = b-a, then

~~~text
I_G(q) = h2(a+dq) - (1-q)h2(a) - q h2(b),
I_K(q) = I_G(1-q).
~~~

The only external mathematical input is Theorem 9, equations (19a)–(19p) and its side conditions, of Gohari, Liu, and Nair, A Two Auxiliary Receiver Outer Bound to the Capacity Region of a Two-Receiver Discrete Memoryless Broadcast Channel (January 2026). The proof below states every row from that theorem that is actually used. The canonical structural reduction is consistent with the chosen input-only G and K, but is not needed to justify this particular fixed pair: the outer-bound theorem permits any fixed auxiliary-receiver pair.

## The six rows used from the outer bound

For each g in {a,b,c}, let (U_g,V_g,W_g)-X-(Y,Z,G,K) be the hierarchy appearing in Theorem 9. Set R0=0. The certificate uses the following five rate inequalities and one a-side condition, copied term-for-term from the displayed outer-bound system. Choosing a branch of a minimum is valid because the theorem imposes the bound by the minimum.

~~~text
(A) R1 <= I(Wc;Z) + I(Ua;Y|Wa)
          + I(Wa;G) - I(Wb;G) + I(Wb;K) - I(Wc;K)
          + I(Ub,Wb;G) - I(Ua,Wa;G).

(B) R2 <= I(Wc;Z) + I(Vc;Z|Wc)
          + I(Vb,Wb;K) - I(Vc,Wc;K).

(C) R1+R2 <= I(Wa;Y)
          + I(Wc;K) - I(Wb;K) + I(Wb;G) - I(Wa;G)
          + I(Va,Wa;G) - I(Vb,Wb;G)
          + I(Vb,Wb;K) - I(Vc,Wc;K)
          + I(Vc;Z|Wc) + I(X;Y|Va,Wa).

(D) R1+R2 <= I(Wa;Y) + I(Ua;Y|Wa) + I(Vc;Z|Wc)
          + I(Ub,Wb;G) - I(Ua,Wa;G)
          - I(Vc;K|Wc) + I(X;K|Ub,Wb).

(E) R1+R2 <= I(Wc;Z) + I(Ua;Y|Wa) + I(Vc;Z|Wc)
          + I(Vb,Wb;K) - I(Vc,Wc;K)
          - I(Ua;G|Wa) + I(X;G|Vb,Wb).

(F) 0 <= I(Ua;Y|Wa) - I(Ua;G|Wa)
          - I(X;Y|Va,Wa) + I(X;G|Va,Wa).
~~~

Let

~~~text
epsilon = 0.000172556,
c1      = (1-epsilon)/2 = 0.499913722,
c1p     = (1+epsilon)/2 = 0.500086278.
~~~

Multiply (A), (B), (C), and (F) by epsilon, multiply (D) by

~~~text
1/2 - epsilon/2 = 0.499913722,
~~~

and multiply (E) by

~~~text
1/2 - 3 epsilon/2 = 0.499741166.
~~~

All weights are nonnegative. The coefficient of each of R1 and R2 in the sum is exactly one. Adding the selected inequalities and the nonnegative right side of (F) therefore gives a valid upper bound on R1+R2.

The supporting verifier independently stores these six rows as exact sparse tensors. Its first phase checks with rational arithmetic that the weights are nonnegative, that both rate coefficients are exactly one, and that the weighted tensor equals the closed form derived next.

## Posterior-measure relaxation

For any binary-input channel A with mutual-information curve I_A(q), posterior conditioning gives

~~~text
I(W;A)       = I_A(q0) - E I_A(q_W),
I(U;A|W)     = E I_A(q_W) - E I_A(q_U),
I(U,W;A)     = I_A(q0) - E I_A(q_U),
I(X;A|U,W)   = E I_A(q_U),
~~~

where

~~~text
q0  = P(X=1),
q_W = P(X=1|W),
q_U = P(X=1|U,W).
~~~

The same identities hold for V. They follow directly by writing each mutual information as an output entropy minus its conditional output entropy.

For each group g, let mu_g be the law of q_W, and let nuU_g and nuV_g be the joint laws of (q_W,q_U) and (q_W,q_V). These measures obey

~~~text
E_mu q_W = q0,
E(q_U | q_W) = q_W,
E(q_V | q_W) = q_W.
~~~

Every actual hierarchy induces such measures. Retaining only these mass and martingale constraints is a relaxation, so an upper bound valid for every relaxed measure is automatically valid for every hierarchy in the outer-bound theorem.

Define

~~~text
h(q)  = I_G(q) - I_Y(q),
hC(q) = I_K(q) - I_Z(q) = h(1-q).
~~~

Exact collection of the weighted terms reduces the right side to

~~~text
c1p [I_Y(q0)+I_Z(q0)]
+ sum over g in {a,b,c} of
    { E_mu_g fW_g(q_W)
    + E_nuU_g fU_g(q_U)
    + E_nuV_g fV_g(q_V) },
~~~

where

~~~text
group a:
  fW_a = -c1 h,       fU_a = h,                    fV_a = 0;

group b:
  fW_b = 0,           fU_b = c1 I_K - c1p I_G,    fV_b = c1 I_G - c1p I_K;

group c:
  fW_c = -c1 hC,      fU_c = 0,                   fV_c = hC.
~~~

No strong-duality assertion is used. Only this exact algebra and weak duality are needed.

## Continuous dual certificate

Suppose that, for each group and each w, affine functions

~~~text
ellU_w(q) = gammaU(w) + deltaU(w) q,
ellV_w(q) = gammaV(w) + deltaV(w) q
~~~

satisfy

~~~text
(D1) ellU_w(q) >= fU(q) and ellV_w(q) >= fV(q)
     for every q in [0,1],
~~~

and an outer line L_g(w)=alpha_g+beta_g w satisfies

~~~text
(D2) L_g(w) >= fW_g(w) + ellU_w(w) + ellV_w(w)
     for every w in [0,1].
~~~

The martingale property gives

~~~text
E_nuU fU(q_U)
 <= E_nuU ellU_qW(q_U)
  = E_mu ellU_qW(q_W),
~~~

and similarly for V. Applying (D2), then E q_W=q0, gives

~~~text
R1+R2 <= B(q0)
       = c1p[I_Y(q0)+I_Z(q0)] + sum_g (alpha_g+beta_g q0).
~~~

The frozen lines are as follows. All displayed decimals are exact rationals.

For group a, use the tangent to h at w when 0<=w<=T_A and the fixed tangent at T_A when T_A<=w<=1, with

~~~text
T_A     = 0.223552668538408774737672966080,
L_a(w)  = ALPHA_A + BETA_A w,
ALPHA_A = 0.00484636345006208271335829634629,
BETA_A  = 0.0455746969473466097687930352226.
~~~

The V-majorant is zero. For group c, use the exact reflection:

~~~text
T_C     = 1-T_A,
L_c(w)  = ALPHA_C + BETA_C w,
ALPHA_C = ALPHA_A+BETA_A,
BETA_C  = -BETA_A.
~~~

For group b, use fixed inner lines

~~~text
ellV(q) = ICPT_V + SLOPE_V q,
ICPT_V  = 0.000000000000000000000000000000001,
SLOPE_V = 0.0026976853408719163997223206507487,

ellU(q) = ICPT_U + SLOPE_U q,
ICPT_U  = ICPT_V+SLOPE_V,
SLOPE_U = -SLOPE_V.
~~~

Take L_b(w)=ellU(w)+ellV(w), making (D2) for group b an identity once the two inner majorants are established.

The group-a and group-c outer intercepts retain their upward backoff of
`10^-18`. The group-B inner intercept is `10^-33`. Consequently the endpoint
gaps are strictly positive, as are the two interior near-contact gaps.  The
smallest of these margins is established with directed arithmetic rather than
inferred from rounded point samples.

### Why the tangent family is globally valid

For group a, h has one curvature change. With m(q)=a+dq,

~~~text
ln(2) m(q)(1-m(q))(1-q^2) h''(q)
~~~

has the sign of the affine polynomial

~~~text
a(1-a) - d^2 + d(1-2a)q.
~~~

This polynomial is increasing. It is negative through T_A and changes sign once at ci. Consequently h is concave on [0,ci] and convex on [ci,1].

For any w<=T_A, the tangent T_w dominates h on the concave interval [0,ci]. On [ci,1], convexity puts h below its chord between ci and 1. The same tangent dominates that chord because it dominates at ci and because

~~~text
T_w(1) = phi(w) = h(w)+(1-w)h'(w)
                >= phi(T_A) > 0 = h(1).
~~~

Here phi is decreasing on [0,T_A], since phi'(w)=(1-w)h''(w)<0. Directed interval evaluation gives

~~~text
phi(T_A) in [2.599502e-31, 2.599502e-31].
~~~

The fixed tangent at T_A follows by the same argument. Reflection proves the group-c statement, and the verifier evaluates the reflected case independently as a check.

### Certification of all remaining inequalities

The exact constants used to isolate near-contact regions are

~~~text
M_A0   = 0.114285343005993681661925002371,
M_A1   = 0.768455543733403745703862116196,
CI_A   = 0.606140352457671436157307542343,
M_BV   = 0.770454053982572010542858483762,
window half-width = 1/16,
group-B contact guard offset = 10^-16.
~~~

Their group-c and group-b partners are exact reflections.

The verifier proves (D1) and (D2) on the whole unit interval by a finite cover:

- four convex group-A/C near-contact windows use the rigorous lower bound
  `f(M)-|f'(M)|r`;

- two concave regions use the fact that a concave function takes its minimum at an endpoint;

- the group-B endpoints are closed by a nonnegative endpoint enclosure and
  directed derivative signs on `[0,0.01]` and its reflection, while the full
  intervals `[M_BV-10^-16,M_BV+10^-16]` and its reflection are covered by the
  convex lower bound `f(M)-|f'(M)|10^-16`; and

- the remaining eight segments use outward-rounded interval evaluation with adaptive bisection, including a centered derivative form when the direct interval form is too wide.

The curvature signs required for the special windows are checked in exact
rational arithmetic. The finite bisection cover contains 1,058 accepted cells.
The smallest certified bisection margin is `2.75e-35`; the directed group-B
contact-guard floor is `9.51e-34`. Both remain positive in every hostile-context
rerun.

The complete algorithms, frozen constants, sparse row transcription, exact sign checks, interval operations, and fail-closed stopping criteria are in certify_th9_dual.py and interval_arithmetic.py. CERTIFICATE.md records the observed output and source digests.

## Maximization over every input prior

The exact phase-zero audit proves

~~~text
coefficient of I_Y = coefficient of I_Z = c1p >= 0,
coefficient of I_G = coefficient of I_K = 0,
sum_g beta_g = 0.
~~~

Therefore B(q0) is concave: the physical mutual-information curves are concave and all remaining terms are affine. It is symmetric under q0 -> 1-q0 because I_Z(q)=I_Y(1-q), the physical coefficients agree, and the total affine slope vanishes. A concave symmetric function on [0,1] is maximized at one half. Hence

~~~text
C_sum <= sup B(q0) = B(1/2) = U.
~~~

Directed 80-digit interval evaluation yields the enclosure stated at the beginning. Rounding its upper endpoint upward at the displayed precision gives

~~~text
C_sum <= 0.369296946555519725636.
~~~

## Validation and trust boundary

The verifier uses only the Python standard library. Interval endpoints are 80-digit Decimal values. Addition, subtraction, multiplication, and division use outward rounding. Decimal.ln is correctly rounded under Python's specified decimal arithmetic; the code expands each logarithm by one adjacent representable value on both sides.

The validation has four independent layers:

1. Exact Fraction arithmetic checks the dual weights, rate coefficients, row combination, mirror identities, line-slope cancellation, region ordering, and curvature signs.

2. Directed intervals establish the tangent endpoint condition, the positive
   group-B endpoint gaps, both complete two-sided contact guards, and every
   remaining continuous line inequality.

3. Three hostile process-wide Decimal contexts, with precisions 5, 7, and 3 and different rounding modes, reproduce the identical 80-digit enclosure. This checks that no ambient context leaks into derived constants.

4. A separate numerical cross-check, used only as corroboration, approached U from below on grids of 100001, 200001, and 500001 points, with gaps 1.3e-11, 1.0e-12, and 2.5e-13. The rigorous claim does not rely on this sampled computation.

The proof remains computer-assisted rather than proof-assistant formalized. Its trust base is the published outer-bound theorem, inspection of the six copied rows, Python's Decimal specification, and the two included source files. The source is evidence and need not be executed by the judge.

## Effect on the current research program

The current canonical knowledge records the same six-row continuous dual with
strict `10^-18` group-B chord backoffs. This contribution shows that a
`10^-33` backoff suffices, while also recording that the rounded zero-intercept
candidate is not feasible. The displayed capacity upper bound is
correspondingly tightened in its final certified digits.

The result should be incorporated into the existing gk-two-auxiliary-outer-bound program, not placed in a separate capacity program. The program remains open because the chosen pair has not been proved globally optimal.

## Novelty, limitations, and open questions

The numerical change relative to canonical knowledge is deliberately tiny;
the novelty claimed here is a fail-closed certification at a backoff fifteen
orders of magnitude smaller, including the contact intervals omitted by the
earlier rejected proof. This is not a claim that the result is the smallest
decimal in the literature. In particular, a reported value near
`0.369296340638082` remains about `6.06e-7` smaller and is neither reproduced
nor refuted here.

The following are expressly not claimed:

- global minimization over all auxiliary channels G and K;

- equality between the relaxed posterior-measure primal and the true auxiliary hierarchy at the fixed channel;

- a capacity formula or matching achievable rate;

- uniqueness of the channel, dual weights, contact points, or envelopes;

- improvement over every published numerical claim.

The next questions are to minimize the full Theorem 9 value over the reduced input-only channel family, establish cardinality or extremal structure, and determine whether the smaller reported decimal has a rigorous full-region certificate.
