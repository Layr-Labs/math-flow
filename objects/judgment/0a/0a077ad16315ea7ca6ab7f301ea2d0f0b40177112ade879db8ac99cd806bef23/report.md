# Judgment on transaction `7e7626cbff7270572d51a8fda719154ab602907f`

## Overall disposition

**Accepted for its principal mathematical claims, with a limited evidentiary qualification concerning the named rank-eight quotient coordinates.**

The supplied material gives a credible, auditable computer-assisted proof of the improved universal converse

\[
\boxed{C_{\mathrm{sum}}\le 0.369296945969202842443}.
\]

The proof is not a posterior-grid computation: it combines an exact rational audit of a nonnegative combination of six Gohari–Liu–Nair Theorem 9 constraints with continuous, outward-rounded interval certificates over the whole posterior interval \([0,1]\), followed by an analytic maximization over every input prior.

The transaction also establishes an exact skew-invariant six-row representation of the particular dual functional used in that converse. That is an algebraic identity of functionals, not merely numerical symmetry. It does **not** prove that invariant duals are globally sufficient.

The resulting governed benchmark interval is rigorously narrowed, on the supplied evidence, to

\[
0.361642884421954615663441578150587\ldots
\le C_{\mathrm{sum}}
\le 0.369296945969202842443.
\]

No exact capacity value or matching achievability is established.

---

## Finding 1 — Fixed reflected binary receivers give the stated continuous Theorem 9 converse

**Claim key:** `BSSC full-Theorem-9 fixed-pair upper bound 0.369296945969202842443`

### Claim

For the exact binary auxiliary-receiver pair

\[
G=(0.206961624915382,0.826953249115544),
\qquad
K=(0.173046750884456,0.793038375084618),
\]

where the coordinates are \(P(G=0\mid X=0),P(G=0\mid X=1)\) and \(K\) is the input/output reflection of \(G\), the full Gohari–Liu–Nair Theorem 9 outer bound implies

\[
C_{\rm sum}\le U
\]

with

\[
\begin{aligned}
U\in[&
0.36929694596920284244271335135600317726937686320586339865039784778686683932875798,\\
&
0.36929694596920284244271335135600317726937686320586339865039784778686683932875818].
\end{aligned}
\]

Consequently,

\[
C_{\rm sum}\le0.369296945969202842443.
\]

### Judgment

**Supported.**

### Decisive reasoning

#### 1. The selected six-row combination has the correct rate normalization

The certificate uses five rate inequalities and one nonnegative side-condition expression from Theorem 9. With

\[
\epsilon=0.000173428163029,
\]

the six weights are

\[
\epsilon,\ \epsilon,\ \epsilon,\ 
\frac{1-\epsilon}{2},\
\frac{1-3\epsilon}{2},\
\epsilon.
\]

They are all nonnegative because \(0<\epsilon<1/3\). The supplied exact `Fraction` audit checks that the resulting coefficient of each of \(R_1\) and \(R_2\) is exactly one. Thus adding these constraints gives a valid inequality with left side \(R_1+R_2\).

This is an important proof step: the argument is not treating a numerical LP solution as a converse. It explicitly verifies that the chosen row multipliers form a valid nonnegative dual combination.

#### 2. The posterior reduction uses only valid identities and a relaxation in the safe direction

For any binary-input receiver \(A\), the certificate uses

\[
I(W;A)=I_A(q_0)-\mathbb E I_A(q_W),
\]

\[
I(U;A\mid W)=\mathbb E I_A(q_W)-\mathbb E I_A(q_U),
\]

and the corresponding \(V,UW,VW,X|UW,X|VW\) identities. These are standard consequences of \(W-X-A\) and posterior conditioning.

The genuine hierarchy implies the martingale constraints

\[
\mathbb E[q_U\mid q_W]=q_W,\qquad
\mathbb E[q_V\mid q_W]=q_W,\qquad
\mathbb E q_W=q_0.
\]

Discarding other compatibility conditions enlarges the hierarchy class. Since the goal is to upper-bound the weighted right side, proving an upper bound over that enlarged martingale class is valid weak duality. No equality between the relaxed martingale problem and the original auxiliary hierarchy is required or asserted.

#### 3. The exact row expansion is independently audited

The final verifier transcribes the six selected rows into a sparse posterior tensor. Exact rational arithmetic checks that this tensor equals the claimed three-group closed form. In particular, after summing root-level coefficients across the three groups, the coefficients are

\[
c_Y=c_Z=\frac{1+\epsilon}{2},\qquad c_G=c_K=0.
\]

This cancellation is decisive later when maximizing over the input prior.

The exact audit significantly reduces the risk that the numerical certificate is certifying the wrong functional. The remaining external trust point is that the six displayed rows and side-condition signs are correctly transcribed from Theorem 9; the manuscript itself is cited but not reproduced in full in the supplied evidence.

#### 4. The affine majorants certify the entire posterior continuum

For each hierarchy group, the proof constructs affine inner majorants and an affine outer line satisfying the two weak-duality conditions:

\[
L_U(w;q)\ge f_U(q),\qquad L_V(w;q)\ge f_V(q)
\quad\text{for all }w,q\in[0,1],
\]

and

\[
\alpha+\beta w
\ge f_W(w)+L_U(w;w)+L_V(w;w)
\quad\text{for all }w\in[0,1].
\]

The martingale identities then turn these pointwise line inequalities into an expectation bound depending only on \(q_0\).

The supplied continuous proof is materially stronger than a finite-grid check:

- Exact rational identities determine the curvature signs.
- For the \(a\)-group curve \(h=I_G-I_Y\), the sign of \(h''\) is reduced to an affine polynomial. This establishes one concave and one convex region.
- Tangents based in the concave region dominate there. On the convex tail, the curve lies below its endpoint chord, and the tangent dominates that chord because it dominates at the inflection point and has strictly positive value at \(q=1\).
- The required endpoint quantity
  \[
  h(T_A)+(1-T_A)h'(T_A)
  \]
  is enclosed strictly above zero using directed intervals.
- The \(c\)-group is treated by reflection and also checked directly.
- The group-\(b\) line gaps are covered using exact convexity checks near the contact windows and adaptive directed interval subdivision elsewhere.
- All of \([0,1]\) is partitioned into analytically controlled windows and fail-closed interval-cover segments.

The final checker reports 136 accepted regular cells and aborts if any cell cannot be certified, if a depth or cell budget is exceeded, or if an exact identity fails. Thus the certificate is genuinely continuous.

#### 5. Maximization over the input prior is analytic, not sampled

After the majorant step, the bound has the form

\[
B(q_0)=
\frac{1+\epsilon}{2}\bigl(I_Y(q_0)+I_Z(q_0)\bigr)+\text{constant},
\]

because the auxiliary-receiver root coefficients and total affine slope cancel exactly.

Both physical mutual-information curves are concave, and

\[
I_Z(q)=I_Y(1-q).
\]

Therefore \(B\) is concave and reflection symmetric. A concave symmetric function on \([0,1]\) is globally maximized at \(q_0=1/2\). This closes the optimization over every input prior without a prior grid.

#### 6. The final numerical enclosure is outward rounded

The entropy and logarithm evaluations use 80-digit `Decimal` intervals with directed arithmetic. Each correctly rounded logarithm is expanded by one adjacent representable value in each direction. The final interval has width approximately \(2\times10^{-79}\), and its upper endpoint is below the rounded headline

\[
0.369296945969202842443.
\]

The hostile-context reruns are not themselves a proof of interval soundness, but they are a useful check that ambient decimal precision and rounding modes do not silently alter derived constants.

### Effect on the benchmark

The new upper endpoint is strictly below the governed benchmark

\[
0.369316568803963.
\]

It also improves the preceding repaired fixed-pair certificate by approximately

\[
5.8631688\times10^{-10}.
\]

This is a real, though numerically small, frontier improvement.

### Confidence and trust boundary

Confidence is **high**, conditional on:

1. the cited Theorem 9 being valid;
2. the six selected manuscript rows and side-condition orientation being transcribed correctly; and
3. Python’s documented `Decimal.ln` behavior used by the interval layer.

The supplied source is sufficient to audit the algebraic and interval strategy. It is not a proof-assistant formalization, and the complete manuscript row comparison is an external trust point.

---

## Finding 2 — The frontier six-row functional has an exact skew-invariant representation

**Claim key:** `Theorem-9 frontier six-row functional admits exact skew-invariant representation`

### Claim

For every

\[
0\le\epsilon\le\frac13,
\]

the non-invariant six-row combination used by the frontier certificate induces exactly the same posterior-hierarchy functional as another nonnegative six-row combination whose weights are invariant under the BSSC skew involution.

The identity is claimed for every input prior, every auxiliary-receiver pair \(G,K\), and every admissible three-group hierarchy—not only for the particular reflected binary pair used in the numerical certificate.

### Judgment

**Supported.**

### Decisive reasoning

A weighted row combination expands into coefficients

\[
T_{g,L,D},
\]

where \(g\in\{a,b,c\}\), \(L\in\{0,W,U,V\}\), and \(D\in\{Y,Z,G,K\}\).

Two such combinations define the same hierarchy functional if:

1. their \(W,U,V\) coefficients agree separately in every group; and
2. their root-level coefficients agree after summing over the three groups.

The second condition is sufficient because all three groups share the same prior \(q_0\), so every root contribution in receiver column \(D\) multiplies the same \(I_D(q_0)\).

The exact checker establishes:

- both row combinations have rate vector exactly \((1,1)\);
- all nonconstant \(W,U,V\) tensor coefficients agree group by group;
- the only root-level residuals are
  \[
  \begin{array}{c|cc}
   &G&K\\ \hline
  a&(3\epsilon-1)/2&0\\
  b&(1-3\epsilon)/2&(1-\epsilon)/2\\
  c&0&(\epsilon-1)/2,
  \end{array}
  \]
  with no \(Y\) or \(Z\) residuals;
- each receiver column sums to zero across the three groups;
- every displayed invariant weight is nonnegative on
  \(0\le\epsilon\le1/3\); and
- weights agree on every skew-paired row support.

Therefore the two weighted right sides are exactly equal before any envelope optimization, posterior restriction, or maximization over the input prior. This proves an identity of functionals rather than equality only at an optimizer.

### Scope of the result

This establishes that the particular frontier functional can be represented inside the skew-invariant dual cone. It does **not** establish any of the following:

- that every optimal Theorem 9 dual can be chosen invariant;
- that restricting receiver pairs to reflected pairs is sufficient;
- that the certified receiver pair or value of \(\epsilon\) is optimal;
- that leaving the invariant cone cannot improve the global bound.

The transaction states these limitations correctly.

### Evidentiary qualification on the quotient coordinates

The claimed quotient point

\[
\left(\frac{1-\epsilon}{2},0,\epsilon,0,0,0,0,
\frac{1-\epsilon}{2}\right)
\]

with normalization

\[
2s_B+s_C+s_D+s_E=1
\]

is consistent with the mapping asserted in the artifact and is checked algebraically after that mapping is encoded.

However, the supplied subject evidence does not reproduce the earlier full rank-eight quotient theorem or independently derive the map from all 15 skew-paired rows to the named coordinates
\((s_B,s_C,s_D,s_E,s_{N_0},s_{N_1},s_{F_0},s_{F_1})\). The non-normative state fixture mentions that prior result, but it is expressly not the mathematical certificate for it.

Accordingly:

- the **functional identity and skew invariance are fully supported** by the supplied exact row expansion;
- the **identification with those particular named quotient coordinates is conditional on the previously established quotient convention**.

This qualification does not affect the capacity upper bound.

---

## Finding 3 — The rounded zero-intercept group-\(b\) line in the earlier certificate is infeasible

**Claim key:** `Earlier frozen group-b rounded-slope zero-intercept majorant is infeasible`

### Claim

For the earlier fixed pair and exact frozen slope

\[
0.0026976853408719163997223206507487,
\]

the corresponding zero-intercept group-\(b\) line fails to majorize the curve at the stated contact point. A positive intercept of \(10^{-33}\) repairs the failure.

### Judgment

**Supported in the narrow stated sense.**

The supplied repaired-certificate record gives the directed enclosure

\[
[-4.8921763736983316\ldots\times10^{-35},
 -4.8921763736983316\ldots\times10^{-35}]
\]

for the zero-intercept gap at the frozen contact point. Its upper endpoint is strictly negative. Thus that particular exact-decimal slope with zero intercept is not feasible.

Adding \(10^{-33}\) leaves a positive directed margin, including after accounting for the derivative penalty on a two-sided neighborhood. The repair then covers the remaining interval by adaptive subdivision.

This result should not be overread: it does not prove that every possible zero-intercept supporting line is infeasible. It concerns the specified rounded slope and contact construction only.

The differing earlier numerical endpoints are therefore not contradictory:

- the first certificate used a \(10^{-18}\) group-\(b\) backoff;
- the repaired certificate used \(10^{-33}\);
- the later frontier certificate changed the receiver pair and other frozen constants and gives the stronger final bound.

---

## Finding 4 — The transaction does not solve the sum-capacity or the global auxiliary optimization

**Claim key:** `BSSC exact private-message sum-capacity remains undetermined by fixed-pair Theorem-9 certificate`

### Judgment

**Correctly limited.**

The transaction proves a valid upper bound at one chosen reflected binary pair. It does not prove:

- that binary auxiliary-receiver outputs suffice globally;
- that reflected pairs suffice;
- that the fixed pair is locally or globally optimal;
- that the selected six-row dual face is globally optimal;
- that the reported lead
  \[
  0.369296340638082
  \]
  is valid or invalid for the full Theorem 9 optimization;
- that the Theorem 9 bound equals capacity; or
- any new achievable sum rate.

Thus the exact value of \(C_{\rm sum}\) remains open. The contribution rigorously improves only the converse side of the benchmark interval.

---

## Consistency and conflicts

### No conflict with the published smaller numerical lead

The certified upper bound

\[
0.369296945969202842443
\]

is larger than the reported simplified-calculation value

\[
0.369296340638082.
\]

This is not a contradiction. The latter is explicitly described as an uncertified numerical lead, while the present transaction certifies a different fixed-pair full-Theorem-9 dual value. The transaction neither reproduces nor refutes the smaller decimal.

### No conflict among the successive fixed-pair values

The source artifacts contain several close but distinct values. They arise from different backoffs or different exact auxiliary pairs:

- the original \(10^{-18}\)-backoff certificate;
- the repaired \(10^{-33}\)-backoff certificate; and
- the improved frontier certificate at a new receiver pair.

The later values supersede the earlier ones as upper bounds but do not logically contradict them.

### Dependence on the earlier input-only reduction

The subject contribution cites the earlier reduction from output-dependent \(T_{G,K\mid X,Y,Z}\) to separate input-only channels. That reduction is useful for interpreting the wider optimization program, but the fixed-pair converse does not require it: Theorem 9 already permits selecting the particular input-only pair used here. Consequently, any uncertainty in the global reduction would not invalidate this fixed-pair certificate.

---

## Credit and provenance

The transaction is an attributed port rather than a claim of new authorship by the act of porting.

According to the supplied provenance:

- the first continuous certificate, improved frontier certificate, and invariant-functional artifact were authored by **Robert Raynor**;
- the microscopic-backoff repair is attributed to **Red Team D**, committed by Robert Raynor;
- the current transaction preserves those source artifacts and does not claim new mathematical authorship for the port itself.

The principal new mathematical frontier represented here is the certified bound

\[
C_{\rm sum}\le0.369296945969202842443,
\]

together with the exact invariant representation of its six-row functional. No cumulative project credit is assigned in this judgment.
