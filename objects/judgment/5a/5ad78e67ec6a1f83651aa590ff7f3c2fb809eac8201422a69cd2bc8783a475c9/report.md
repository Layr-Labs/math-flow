## `bssc-sum-capacity/uv-product-branchwise-additivity`

**Verdict: valid.**

The four stated mathematical claims are established for finite-alphabet DMBCs. The declared reference `c70e1829...` is a required dependency only for the sharp one-letter BSSC posterior-support calculation used in claim 4; the product-additivity and symmetry arguments are independently proved in the subject.

### 1. Additivity of \(B_{\rm avg}\)

For an arbitrary product-channel input law, including correlated \(X_1,X_2\), and any finite envelope auxiliary \(A\), the displayed identity

\[
\begin{aligned}
&I(X_1X_2;Y_1Y_2\mid A)-I(X_1X_2;Z_1Z_2\mid A)\\
&=I(X_1;Y_1\mid A,Z_2)-I(X_1;Z_1\mid A,Z_2)\\
&\quad+I(X_2;Y_2\mid A,Y_1)-I(X_2;Z_2\mid A,Y_1)
\end{aligned}
\]

is correct.

In detail:

- Product memorylessness gives
  \[
  I(X_1X_2;Y_1Y_2|A)
  =I(X_1;Y_1|A)+I(X_2;Y_2|A,Y_1),
  \]
  and the corresponding reverse-order expansion for \(Z_1,Z_2\).
- Even when \(X_1,X_2\) are correlated conditional on \(A\),
  \[
  Y_1\perp Z_2\mid(A,X_1),\qquad
  Z_2\perp Y_1\mid(A,X_2),
  \]
  because the two channel factors have independent transition kernels.
- The two co-information corrections are therefore both
  \(I(Y_1;Z_2|A)\), with opposite signs, and cancel.

Moreover,

\[
(A,Z_2)-X_1-(Y_1,Z_1),\qquad
(A,Y_1)-X_2-(Y_2,Z_2),
\]

so the two resulting terms are legitimate one-factor posterior mixtures. Applying the envelope definition and then concavity gives, for either sign,

\[
\mathfrak C[\pm t_{12}](p_{12})
\le
\mathfrak C[\pm t_1](p_1)+
\mathfrak C[\pm t_2](p_2).
\]

The remaining mutual-information terms satisfy

\[
I(X_1X_2;Y_1Y_2)
\le I(X_1;Y_1)+I(X_2;Y_2),
\]

and similarly for \(Z\), including for correlated inputs. This proves the product upper bound.

For the reverse bound, product priors and independent posterior decompositions give additive mutual information and

\[
t_{12}(p_{1a}\times p_{2b})
=t_1(p_{1a})+t_2(p_{2b}).
\]

Because the two envelopes are optimized separately, no common auxiliary is required. Taking suprema proves

\[
B_{\rm avg}(W_1\times W_2)
=B_{\rm avg}(W_1)+B_{\rm avg}(W_2).
\]

Thus correlated product-channel priors and auxiliaries joint across factors cannot improve the functional.

### 2. Receiver-skew symmetry and \(B_{\rm br}=B_{\rm avg}\)

Under the stated receiver-exchanging input involution \(S\),

\[
I_Y(Sp)=I_Z(p),\qquad I_Z(Sp)=I_Y(p),
\]

hence \(t(Sp)=-t(p)\). Since \(S\) bijects all finite posterior decompositions,

\[
\mathfrak C[-t](Sp)=\mathfrak C[t](p),\qquad
\mathfrak C[t](Sp)=\mathfrak C[-t](p).
\]

Consequently,

\[
A(Sp)=D(p),\qquad D(Sp)=A(p).
\]

Both \(A\) and \(D\) are concave: fixed-channel mutual information is concave in the input law, and upper concave envelopes are concave. For

\[
\bar p=\frac{p+Sp}{2},
\]

which is \(S\)-invariant,

\[
A(\bar p),D(\bar p)
\ge \frac{A(p)+D(p)}2.
\]

Therefore

\[
\min\{A(\bar p),D(\bar p)\}
\ge \frac{A(p)+D(p)}2.
\]

Taking suprema yields \(B_{\rm br}\ge B_{\rm avg}\), while the pointwise inequality

\[
\min\{a,d\}\le \frac{a+d}{2}
\]

gives the reverse inequality. Hence

\[
B_{\rm br}(W)=B_{\rm avg}(W).
\]

The same symmetrization shows that both optimizations may be restricted to invariant input laws.

### 3. Finite products

Coordinatewise input involutions and output relabelings preserve receiver-skew symmetry under finite products. Applying claim 2 to the product and to every factor, together with claim 1, gives

\[
\begin{aligned}
B_{\rm br}\!\left(\mathop{\times}_{i=1}^nW_i\right)
&=B_{\rm avg}\!\left(\mathop{\times}_{i=1}^nW_i\right)\\
&=\sum_{i=1}^n B_{\rm avg}(W_i)
=\sum_{i=1}^n B_{\rm br}(W_i).
\end{aligned}
\]

No product-input or coordinatewise-auxiliary restriction is inserted into the left-hand optimization.

### 4. Half-skew BSSC specialization

For the BSSC, receiver exchange is induced by \(x\mapsto1-x\), together with output complementation. An input law with \(q=P(X=1)\) is invariant exactly when \(q=1/2\), so the fair prior is the unique invariant binary prior.

The required part of declared reference `c70e1829...` proves, with

\[
h=h_2(1/4),\qquad r=h-\frac34,
\]

the global support inequality for \(g(q)=I_Z(q)-I_Y(q)\),

\[
g(q)\le 2r(1-q).
\]

Its reflection is

\[
t(q)=I_Y(q)-I_Z(q)\le 2rq.
\]

The reference justifies this globally by:

- the stated second derivative, giving concavity on \([0,1/2]\) and convexity on \([1/2,1]\);
- the tangent identities at \(q=1/5\);
- the zero endpoint values on the convex half.

Thus every posterior decomposition with mean \(1/2\) satisfies

\[
\mathbb E\,t(q_A)\le r.
\]

Equality is attained by masses \(5/8\) at \(q=4/5\) and \(3/8\) at \(q=0\), since

\[
\frac58\frac45=\frac12,\qquad
t(4/5)=\frac85r.
\]

Reflection gives the same value for \(\mathfrak C[-t](1/2)\). At the fair prior,

\[
I(X;Y)=I(X;Z)=h-\frac12,
\]

so

\[
A(1/2)=D(1/2)
=\left(h-\frac12\right)+\left(h-\frac34\right)
=2h_2(1/4)-\frac54.
\]

Claims 1–3 therefore imply, for every finite \(n\ge1\),

\[
B_{\rm br}(P^{\times n})
=B_{\rm avg}(P^{\times n})
=n\left(2h_2(1/4)-\frac54\right).
\]

The numerical evaluation

\[
2h_2(1/4)-\frac54
=0.3725562489182657\ldots
\]

is consistent with the exact expression.

### Converse and frontier scope

The scalar is a legitimate UV sum-rate converse: each of the two standard UV rows is bounded by \(A(p)\) and \(D(p)\), respectively, so the common sum rate is bounded by their minimum and hence by \(B_{\rm br}\). The finite-block rate rows in the declared reference also suffice to recover these UV rows after adjoining \(T\) to the auxiliary and letting the Fano terms vanish.

This value does not improve the governed capacity interval, since already

\[
0.3725562489\ldots >
0.369316568803963.
\]

The packet contains no terminal attestation for the separate assertion that \(0.369296945969202842443\) is a certified full-Theorem-9 bound. That certification status is therefore not independently established here and is not used as a premise; it is only provenance/context. The non-frontier conclusion follows from the governed benchmark itself.

### Dependencies and evidence

- **Required dependency:** `c70e1829a7c6a2a8cb8cfc2383f8abf825ac5ea6`, specifically its analytic BSSC support inequality and equality-achieving posterior mixture. Its unrelated dependence-balance and entropy-counterfeit claims are not needed for product or branchwise additivity.
- **No required dependency** on the cited Yukon source commits or prior judgments: the necessary additivity and symmetry arguments are fully restated in the subject.
- **Objective attestations:** none supplied. The scripts and hash statements are therefore only corroborative assertions, not trusted execution evidence. The universal theorem is nevertheless established by the analytic proof.
