# Four padding-correlation tests for a two-letter Marton gain

## Claim and dependency boundary

Let \(T\) be a finite receiver-skew two-receiver broadcast channel, let \(M_T\)
be its one-letter private-message Marton sum functional, and consider an
arbitrary finite two-letter Marton law

\[
 P(w,u,v,x_1,x_2)T(y_1,z_1\mid x_1)T(y_2,z_2\mid x_2).
\tag{1}
\]

The auxiliaries \(U,V\) in (1) are abstract: no product or tuple structure is
assumed.  This contribution is a direct specialization of the exact
tuple-law residual and gain implication in canonical transaction
`5ed3f525b9ae7f32c6e1dcbf22ecdb5ae946a4a6`
(`conditional-product-marton-no-gain`), which is the sole declared logical
dependency.

Put

\[
\begin{aligned}
A_1&=I(Y_2;Y_1,U\mid W),&
A_2&=I(Y_1;Y_2,U\mid W),\\
B_1&=I(Z_2;Z_1,V\mid W),&
B_2&=I(Z_1;Z_2,V\mid W),\\
D&=I(U;V\mid W),
\end{aligned}
\tag{2}
\]

and let the output-correlation charge be

\[
C=\frac12\left[
 I(Y_1;Y_2\mid W)+I(Y_1;Y_2)
 +I(Z_1;Z_2\mid W)+I(Z_1;Z_2)
\right].
\tag{3}
\]

If the law (1) gives a strict two-letter gain,

\[
 M_{T^{\otimes2}}(P)>2M_T,
\tag{4}
\]

then all four strict inequalities

\[
\boxed{
 A_a+B_b>C+\mathbf 1\{a\ne b\}D,
 \qquad (a,b)\in\{1,2\}^2
}
\tag{5}
\]

must hold.  Equivalently,

\[
\min\{A_1+B_1,\ A_2+B_2,\ A_1+B_2-D,\ A_2+B_1-D\}>C.
\tag{6}
\]

Thus failure of even one test in (5) rigorously rules out a gain for that
law.  Under the published binary-input evaluation, the half-skew BSSC has
\(2M_T=2L_{\rm RTD}\), so the tests apply to every candidate above the current
two-letter Marton baseline.  They neither
prove that any law passing the tests gains nor establish unrestricted
additivity.

## Proof by four constant paddings

For \(a\in\{1,2\}\), represent the abstract auxiliary \(U\) as a tuple by
putting \(U_a=U\) and making \(U_{3-a}\) constant.  Independently, for
\(b\in\{1,2\}\), put \(V_b=V\) and make \(V_{3-b}\) constant.  This gives four
legitimate tuple decompositions of the same law (1).  The dependency's exact
residual identity may be applied to every one of them.

For each \(a\), constant padding gives

\[
 \operatorname{TC}(U_1,U_2\mid W)=0
\]

and the dependency's \(G_{UY}\) term becomes

\[
\begin{aligned}
G_{UY}^{(1)}
 &=H(Y_1\mid U,W)+H(Y_2\mid W)-H(Y_1,Y_2\mid U,W)\\
 &=I(Y_2;Y_1,U\mid W)=A_1,\\
G_{UY}^{(2)}
 &=I(Y_1;Y_2,U\mid W)=A_2.
\end{aligned}
\tag{7}
\]

The identical calculation on the other receiver gives

\[
G_{VZ}^{(1)}=B_1,
\qquad
G_{VZ}^{(2)}=B_2.
\tag{8}
\]

The auxiliary cross-gap distinguishes aligned and crossed padding.  If
\(a=b\), both nonconstant auxiliaries occupy the same coordinate and

\[
G_{UV}^{(a,a)}=0.
\]

If \(a\ne b\), they occupy different coordinates and

\[
\begin{aligned}
G_{UV}^{(a,b)}
 &=H(U\mid W)-H(U\mid V,W)\\
 &=I(U;V\mid W)=D.
\end{aligned}
\tag{9}
\]

For two coordinates, each output total correlation in the dependency is an
ordinary mutual information:

\[
\operatorname{TC}(Y_1,Y_2\mid W)=I(Y_1;Y_2\mid W),
\qquad
\operatorname{TC}(Y_1,Y_2)=I(Y_1;Y_2),
\tag{10}
\]

and similarly for \(Z\).  Substitution of (7)--(10) into the exact residual
therefore yields, for each padding pair,

\[
L_{1/2,T^{\otimes2}}(P)
-\sum_{i=1}^2L_{1/2,T}(P_i^{(a,b)})
=A_a+B_b-\mathbf1\{a\ne b\}D-C.
\tag{11}
\]

The dependency proves that (4) forces the left side of (11) to be strictly
positive for every chosen tuple decomposition.  Applying it to all four
paddings proves (5)--(6).

## A combined crossed-padding obstruction

Adding the two crossed tests \((a,b)=(1,2),(2,1)\) gives a sometimes more
convenient necessary condition.  By the chain rule,

\[
\begin{aligned}
A_1+A_2
 &=2I(Y_1;Y_2\mid W)
 +I(U;Y_2\mid Y_1,W)+I(U;Y_1\mid Y_2,W),\\
B_1+B_2
 &=2I(Z_1;Z_2\mid W)
 +I(V;Z_2\mid Z_1,W)+I(V;Z_1\mid Z_2,W).
\end{aligned}
\]

Consequently every gain also requires

\[
\begin{aligned}
&I(Y_1;Y_2\mid W)+I(Z_1;Z_2\mid W)
-I(Y_1;Y_2)-I(Z_1;Z_2)\\
&\quad+I(U;Y_2\mid Y_1,W)+I(U;Y_1\mid Y_2,W)\\
&\quad+I(V;Z_2\mid Z_1,W)+I(V;Z_1\mid Z_2,W)
>2I(U;V\mid W).
\end{aligned}
\tag{12}
\]

Equation (12) is weaker than retaining both crossed tests separately, but it
makes the competition transparent: cross-coordinate satellite information
and conditional output correlation must overcome both unconditional output
correlation and twice the Marton auxiliary penalty.

## Deterministic corroboration

Run from this contribution directory using only the Python standard library:

```text
python3 -I -B verify_padding_tests.py
```

The checker constructs a strictly positive, correlated rational law on
\((W,U,V,X_1,X_2)\), passes it through the exact half-skew BSSC product
marginals, and evaluates all information quantities in two independent ways.
For every one of the four padding pairs, it compares the complete two-letter
minus coordinatewise \(L_{1/2}\) difference with the right side of (11).  It
also checks the chain-rule reduction to (12).  These finite numerical checks
corroborate the identities; the universal result rests on the displayed
entropy proof and its declared dependency.

## Scope and authorship

- The result is a necessary filter for a fixed two-letter Marton law, not a
  sufficient condition or an optimization theorem.
- Passing all four inequalities does not imply a gain.
- The tests do not restrict support size or auxiliary cardinality and do not
  determine BSSC capacity.
- The specialization and checker were prepared by an OpenAI Codex solver
  agent at Robert Raynor's request.
