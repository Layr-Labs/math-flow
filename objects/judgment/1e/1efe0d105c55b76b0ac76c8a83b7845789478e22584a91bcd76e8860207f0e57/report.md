## `bssc-sum-capacity/fixed-pair-continuous-certificates-and-invariant-frontier`

**Verdict: INDETERMINATE**

The supplied certificate has a coherent internal weak-duality construction, and no decisive numerical or algebraic contradiction was found. However, the claimed capacity converse and parts of the invariant/provenance statement depend on material results that are neither included nor declared as dependencies. Consequently, the exact declared claim cannot be affirmed.

### 1. Checks supported by the supplied artifacts

#### Fixed auxiliary pair and weights

The stated channels are valid and exactly reflected:

\[
1-0.826953249115544=0.173046750884456,\qquad
1-0.206961624915382=0.793038375084618.
\]

For

\[
\epsilon=0.000173428163029,
\]

the six displayed weights

\[
\epsilon,\epsilon,\epsilon,\frac{1-\epsilon}{2},
\frac{1-3\epsilon}{2},\epsilon
\]

are nonnegative. Using the rate coefficients encoded in `verify.py`, the coefficients of both \(R_1\) and \(R_2\) sum exactly to one. The use of the rate-free side condition is also directionally consistent: multiplying a condition \(0\le F\) by a nonnegative coefficient and adding \(F\) to the right side only weakens an upper bound.

#### Posterior reduction and weak duality

Conditional on the six rows being genuine applicable outer-bound inequalities, the posterior identities

\[
I(W;A)=I_A(q_0)-\mathbb E I_A(q_W),
\quad
I(U;A\mid W)=\mathbb E I_A(q_W)-\mathbb E I_A(q_U),
\]

and their \(V,UW,VW\) analogues are correct for binary \(X\). The martingale conditions

\[
\mathbb E[q_U\mid q_W]=q_W,\qquad
\mathbb E[q_V\mid q_W]=q_W,\qquad
\mathbb E q_W=q_0
\]

also follow from conditional expectation.

The proposed dual implication is valid: if the affine inner majorants satisfy (D1) and the outer lines satisfy (D2), then conditional-mean preservation converts each expected affine majorant into its value at \(q_W\), yielding

\[
R_1+R_2\le
c'_1\bigl(I_Y(q_0)+I_Z(q_0)\bigr)
+\sum_g(\alpha_g+\beta_gq_0).
\]

This uses only weak duality and does not require a minimax exchange.

#### Continuous-cover architecture

The curvature identity used for \(h=I_G-I_Y\) is algebraically correct:

\[
\ln 2\,m(q)(1-m(q))(1-q^2)h''(q)
=
a(1-a)-d^2+d(1-2a)q,
\]

where \(m(q)=a+dq\). The right side is affine, so the exact rational sign checks in the verifier suffice to locate the unique curvature transition.

The tangent-majorant argument is sound in form:

- concavity makes a tangent dominate \(h\) before the curvature transition;
- convexity places \(h\) below the endpoint chord afterward;
- positivity of
  \[
  \phi(T_A)=h(T_A)+(1-T_A)h'(T_A)
  \]
  makes the same tangent dominate that chord;
- reflection gives the corresponding group-\(c\) argument.

The remaining interval partition covers the stated domains without an evident gap. The convex tangent floors, concave endpoint bounds, and adaptive interval covers are mathematically appropriate. The interval implementation uses directed rounding for elementary operations and expands each `Decimal.ln` result outward.

#### Maximization over the prior

The exact tensor bookkeeping encoded by the verifier gives

\[
c_Y=c_Z=\frac{1+\epsilon}{2}\ge0,\qquad c_G=c_K=0,
\]

and zero total affine slope. Therefore the resulting prior function is concave and invariant under \(q_0\mapsto1-q_0\). Such a function is globally maximized at \(q_0=1/2\).

The claimed numerical implication is arithmetically correct if the reported enclosure is certified. Its upper endpoint

\[
0.369296945969202842442713\ldots
\]

is below the upward-rounded headline

\[
0.369296945969202842443.
\]

It is also strictly below the repaired endpoint

\[
0.369296946555519725635392\ldots
\]

by approximately \(5.86317\times10^{-10}\).

#### Repaired certificate qualification

The repair artifact explicitly gives a negative interval for the zero-intercept group-\(b\) gap at the frozen slope. Thus it correctly avoids claiming zero-backoff feasibility. Adding \(10^{-33}\) is consistent with the reported positive guard margin.

#### Exact functional identity

Within the row tensors encoded in `frontier-continuum-exchange/verify.py`, the invariant-representation algebra is exact:

- both combinations have rate vector \((1,1)\);
- all \(W,U,V\) posterior-level tensor coefficients agree;
- the only root-level residuals are the four stated \(G,K\) entries;
- those residuals cancel after summing over hierarchy groups, which share the same \(q_0\);
- all weights are nonnegative for \(0\le\epsilon\le1/3\).

Thus the two encoded posterior-hierarchy functionals are indeed identical as polynomials in \(\epsilon\). The displayed normalization

\[
2\frac{1-\epsilon}{2}+\epsilon=1
\]

is also correct.

### 2. Material unresolved dependency: the capacity outer bound

The dependency packet declares **no dependency transactions**. Nevertheless, the central implication

\[
\text{six encoded inequalities}
\Longrightarrow C_{\rm sum}\le U
\]

depends on Gohari–Liu–Nair Theorem 9 and its side conditions. The theorem itself is not included in the evidence.

Consequently, the supplied material does not independently establish:

1. that all six encoded rows are exact transcriptions of applicable Theorem 9 inequalities;
2. that their signs, branches of minima, and rate-free side-condition direction are correct;
3. that all six rows apply simultaneously to the same admissible hierarchy;
4. that the fixed channels \(G,K\) are permitted exactly as used;
5. that every achievable private-message rate pair is covered, including the required asymptotic/closure passage from finite codes to \(C_{\rm sum}\).

The scripts verify algebra relative to their hard-coded `ROWS`; they do not verify those rows against the external theorem. Without the theorem as an admitted premise, the computation certifies an upper bound for the encoded formal system, not affirmatively for the broadcast-channel sum-capacity.

This is a material missing premise and requires an **indeterminate**, rather than valid, verdict.

### 3. Unresolved invariant-framework premises

The tensor equality itself is supported, but the stronger descriptions “skew-invariant” and “rank-eight quotient point” rely on external structure not established by the declared dependencies:

- the list of 15 skew-paired rows is hard-coded;
- the accepted skew involution is not derived from a supplied theorem;
- the map from pair weights to the eight quotient coordinates is referenced as an earlier accepted construction rather than proved in the normative artifact.

Accordingly, the exact equality of the two encoded functionals is supported, but their asserted placement in the named skew-invariant rank-eight quotient is not independently certified from the admitted premises.

### 4. Provenance assertions

The statement also claims that four artifacts were previously accepted and preserved verbatim from specified source commits. The artifacts and a provenance table are supplied, but the referenced repositories, commit contents, judgment bundles, and byte-for-byte comparisons are not dependency evidence. Those historical assertions therefore cannot be verified from the packet.

### 5. Conclusion

The internal dual algebra, posterior relaxation, continuous-cover strategy, prior maximization, decimal rounding, strict numerical comparison, and encoded functional identity are mutually consistent. No decisive mathematical counterexample was found.

However, the undeclared and unavailable Theorem 9 premise is indispensable to the claimed capacity upper bound, while the invariant-quotient and provenance assertions also rely on unsupported external material. Therefore the exact bundled claim remains **indeterminate**.
