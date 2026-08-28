# Exact strict local maximum in the two-letter product-code quotient

## Claim and scope

Let \(P\) be the governed half-skew BSSC, with one-use transition rows

\[
P_{Y\mid X=0}=(1/2,1/2),\quad P_{Y\mid X=1}=(0,1),
\]
\[
P_{Z\mid X=0}=(1,0),\quad P_{Z\mid X=1}=(1/2,1/2).
\]

Order every two-bit super-symbol as \(00,01,10,11\), identified with
\(0,1,2,3\). This contribution studies the following precise 16-cell
subfamily of laws for \(P^{\otimes2}\). Let \(W,X^2\in\{0,1,2,3\}\), let
\(q(w,x)>0\) be an arbitrary point of the 15-dimensional probability simplex,
and make \(U,V\in\{0,1,2,3\}\) deterministic from \((W,X^2)\) by

\[
(U,V)=
\begin{cases}
(x,0),&w=0,\\
(2x_1,x_2),&w=1,\\
(x_2,2x_1),&w=2,\\
(0,x),&w=3,
\end{cases}
\qquad x=2x_1+x_2.
\tag{1}
\]

Thus
\(p(w,u,v,x)=q(w,x)\mathbf 1\{(u,v)\text{ obeys (1)}\}\).
The four values of \(W\) assign both uses to \(U\), the first to \(U\) and
second to \(V\), the first to \(V\) and second to \(U\), or both to \(V\).

For this law define the two Marton endpoints

\[
\begin{aligned}
E_Y(q)&=I(W;Y^2)+I(U;Y^2\mid W)+I(V;Z^2\mid W)-I(U;V\mid W),\\
E_Z(q)&=I(W;Z^2)+I(U;Y^2\mid W)+I(V;Z^2\mid W)-I(U;V\mid W),
\end{aligned}
\tag{2}
\]

and \(L_{1/2}(q)=(E_Y(q)+E_Z(q))/2\). The ordinary Marton value of this
selected law is \(\min\{E_Y(q),E_Z(q)\}\), hence is at most \(L_{1/2}(q)\).

Put

\[
q_-=\frac{15-\sqrt{105}}{30}
\tag{3}
\]

and define the one-use symmetric law

\[
r_*(s,x)=
\begin{cases}
q_-/2,&s=x,\\
(1-q_-)/2,&s\ne x.
\end{cases}
\tag{4}
\]

Writing \(w=2s_1+s_2\) and \(x=2x_1+x_2\), let
\(q_*(w,x)=r_*(s_1,x_1)r_*(s_2,x_2)\). Equivalently, with rows indexed by
\(w\), columns by \(x\), and \(s=\sqrt{105}\),

\[
q_*=\frac1{120}
\begin{pmatrix}
11-s&4&4&11+s\\
4&11-s&11+s&4\\
4&11+s&11-s&4\\
11+s&4&4&11-s
\end{pmatrix}.
\tag{5}
\]

The exact result is

\[
\boxed{
q_*\text{ is a strict local maximum of }L_{1/2}
\text{ on the full 15-dimensional simplex in (1).}
}
\tag{6}
\]

More precisely, the gradient of \(L_{1/2}\) at \(q_*\) is constant on all
16 cells, and its Hessian is negative definite on the tangent hyperplane
\(\sum_{w,x}\delta q(w,x)=0\). Canonical transaction
`88a1004f309460f3ec1cacdae88d30f88559f9bc` identifies the one-use law (4)
with the exact randomized-time-division optimizer, so independence gives

\[
L_{1/2}(q_*)=2L_{\rm RTD}.
\tag{7}
\]

Receiver symmetry gives \(E_Y(q_*)=E_Z(q_*)\). Therefore (6), continuity,
and \(\min\{E_Y,E_Z\}\le L_{1/2}\) imply that every sufficiently close
\(q\ne q_*\) in this fixed architecture has Marton value strictly below
\(2L_{\rm RTD}\).

## Stationarity

For the one-use law (4), direct expansion gives

\[
\ell(t)=h_2(1/4)-t+
\frac12\left[h_2(t/2)-h_2((1-t)/2)\right].
\tag{8}
\]

Its derivative vanishes exactly when

\[
\frac{(2-t)(1+t)}{t(1-t)}=16,
\tag{9}
\]

or equivalently \(15t^2-15t+2=0\). The root in \((0,1/2)\) is (3).
At \(q_*=r_*\otimes r_*\), every marginal entering the two-use entropy
formula factors across uses. Differentiating an entropy at a product point
splits its logarithm into the sum of the two one-use logarithms, so the
two-use gradient is constant.

The verifier checks more than this factorization argument. It constructs all
seven two-use marginal maps from (1) and the BSSC kernels. For every one of
the 15 gradient differences it collects the exact rational coefficients of
the logarithms of positive elements of \(\mathbb Q(\sqrt{105})\), clears
denominators, exponentiates, and verifies the resulting multiplicative
identity exactly. Thus no floating-point logarithm is used for stationarity.

## Exact Hessian certificate

The entropy identity used is

\[
L_{1/2}
=\frac12\{H(Y^2)+H(Z^2)+H(W,Y^2)+H(W,Z^2)\}
-H(W,U,Y^2)-H(W,V,Z^2)+H(W,U,V).
\tag{10}
\]

If a marginal is represented as \(Aq\), then in natural-log units

\[
\nabla^2 H(Aq)=-A^\mathsf T
\operatorname{diag}\left(\frac1{Aq}\right)A.
\tag{11}
\]

All transition coefficients are rational and every positive marginal at
(5) lies in \(\mathbb Q(\sqrt{105})\). The checker therefore constructs the
full \(16\times16\) Hessian exactly in that quadratic field.

Let \(B\) be the \(16\times15\) matrix whose columns are
\(e_i-e_{15}\), \(0\le i<15\). It computes an exact decomposition

\[
B^\mathsf T\nabla^2L_{1/2}(q_*)B
=L D L^\mathsf T
\tag{12}
\]

without pivoting, reconstructs every matrix entry exactly, and proves that all
15 diagonal entries of \(D\) are strictly negative. Signs of
\(a+b\sqrt{105}\) are decided exactly by rational sign checks and comparison
of \(a^2\) with \(105b^2\); the displayed decimal pivots are diagnostic only.
Sylvester's inertia law then makes (12) negative definite. Together with
exact stationarity and the fact that (5) is interior, the second-derivative
test proves (6).

## Reproduction

From this contribution directory run:

```text
python3 -I -B verify.py
```

The verifier uses only the Python standard library. Its governing predicate
checks the metadata and sole dependency, the exact product-code orientation,
the exact tensor-product simplex point, all 15 tangent gradient identities,
the seven marginal-map row counts, Hessian symmetry, all 15 negative exact
LDL pivots, and exact LDL reconstruction.

## Dependency and limitations

- Transaction `88a1004f309460f3ec1cacdae88d30f88559f9bc` is the sole direct
  mathematical dependency. It supplies the exact RTD optimizer/value used
  only to identify (7). The stationarity and Hessian theorem are derived and
  checked self-containedly here.
- This theorem varies only the 16 masses \(q(w,x)\) while retaining the four
  deterministic maps (1). It does not include directions that activate
  other \((w,u,v,x)\) atoms, stochastic encoders, different deterministic
  maps, larger auxiliaries, or a different \(W\) alphabet.
- The result is local and supplies no explicit neighborhood radius. It does
  not rule out a distant improvement even inside this 15-dimensional family.
- It does not rule out a two-letter Marton gain in another architecture, prove
  Marton additivity, determine sum-capacity, or give a capacity converse.
- The exact proof uses \(L_{1/2}\) as an upper bound on the selected law's
  min-endpoint Marton value; it does not replace the minimum by an equality
  away from the symmetric point.

This contribution is original analysis for the non-exclusive
`bssc-multiletter-marton-frontier` direction registered by transaction
`7e1e52fe42fde37ba1964ef9ae5062daf8bb55f8`. No external source or
numerical optimizer output is a premise.
