## bssc-sum-capacity/two-letter-output-covariance-curvature

**Verdict: valid**

### Curvature inequality

Let \(d=c_{\rm in}/4\). For either receiver, memorylessness and the affine conditional output means give

\[
\operatorname{Cov}(Y_1,Y_2)
=\operatorname{Cov}(Z_1,Z_2)
=\frac14\operatorname{Cov}(X_1,X_2)=d.
\]

For a binary joint table with fixed marginals and covariance parameter \(d\),

\[
D_2(P_d\|P_0)''=\frac1{\ln 2}\sum_{a,b}\frac1{p_{ab}(d)}.
\]

This differentiation is correct: the four cell derivatives are \(\pm1\), and the affine terms cancel.

For the paired \(Y\)- and \(Z\)-tables, marking \(Y_i=0\) and \(Z_i=1\) is appropriate because

\[
\Pr(Y_i=0)+\Pr(Z_i=1)=\frac{1-q_i}{2}+\frac{q_i}{2}=\frac12.
\]

If \(x=y_{00}+z_{11}\), the four paired class totals are consequently

\[
x,\quad \frac12-x,\quad \frac12-x,\quad 1+x.
\]

In the relative interior, \(0<x<1/2\). Applying
\[
\frac1u+\frac1v\ge \frac4{u+v}
\]
within each class yields

\[
R\ge 4\left(\frac1x+\frac2{1/2-x}+\frac1{1+x}\right).
\]

The supplied polynomial reduction is correct:

\[
5x(1/2-x)(1+x)\left(R_{\rm lower}-\frac{248}{5}\right)
=2p(x),
\]
where
\[
p(x)=124x^3+62x^2-42x+5.
\]

Since \(p''(x)=744x+124>0\), its unique minimum on \((0,1/2)\) lies between \(1/5\) and \(21/100\). Writing \(x=1/5+t\), \(0\le t\le1/100\), gives

\[
p(x)=124t^3+\frac{682}{5}t^2-\frac{58}{25}t+\frac9{125}
\ge \frac{61}{1250}>0.
\]

Thus \(R>248/5\) throughout the relative interior.

For the sum \(\Phi(d)\) of the two receiver mutual informations,

\[
\Phi''(d)>\frac{248}{5\ln2},\qquad
\Phi(0)=\Phi'(0)=0.
\]

The twice-integrated inequality is valid for either sign of \(d\), giving

\[
\Phi(d)\ge \frac{124}{5\ln2}d^2.
\]

Substituting \(d=c_{\rm in}/4\) yields exactly

\[
C_{\rm out}\ge
\frac{124}{5\ln2}\frac{c_{\rm in}^2}{16}
=\frac{31}{20\ln2}c_{\rm in}^2.
\]

The boundary treatment is adequate. If \(c_{\rm in}\ne0\), both input-coordinate marginals lie strictly between zero and one, so the independence tables are positive and any zero-cell endpoint can be approached through the positive segment. Mutual information is continuous there. If an input coordinate is deterministic, then \(c_{\rm in}=0\), and the asserted non-strict inequality follows from \(C_{\rm out}\ge0\).

### Marton-gain consequence

The declared reference establishes, for every finite two-letter Marton law with \(M>2L_{\rm RTD}\),

\[
C_{\rm out}<\frac7{160}.
\]

Combining this with the verified curvature inequality gives

\[
\frac{31}{20\ln2}c_{\rm in}^2<\frac7{160},
\]
hence
\[
c_{\rm in}^2<\frac{7\ln2}{248}
\quad\text{and}\quad
|c_{\rm in}|<\sqrt{\frac{7\ln2}{248}}.
\]

The directed computation certifies

\[
\frac{7\ln2}{248}<\frac{49}{2500},
\]
so
\[
|c_{\rm in}|<\sqrt{\frac{7\ln2}{248}}<\frac7{50}.
\]

All strictness directions are correct.

### Attestation audit

The subject attestation passed the supplied standard-library verifier. It checks the polynomial identity, derivative bracket, positivity margin, curvature rescaling, and directed logarithmic comparison. It does not itself prove the information-theoretic reduction or continuous-domain argument, but those are established in the written proof above.

The declared-reference attestation certifies the numerical RTD threshold and the strict correlation-cap comparison. Its analytic Marton-to-input reduction is supplied by the declared reference record rather than by that computation alone.

### Dependencies

- **Required dependency:** `9bb22afe5abd3e1d9f419c1717bd61bb33a958ff`, solely for the implication \(M>2L_{\rm RTD}\Rightarrow C_{\rm out}<7/160\).
- The curvature inequality itself is independent of that reference.
- The earlier foundation and full-support transactions are transitive context for the declared reference, not additional direct dependencies of this claim.

The stated limitations are respected: this is only a necessary condition for a finite two-letter Marton improvement and neither constructs nor excludes such an improvement, tensorizes Marton’s functional, or proves a capacity converse.
