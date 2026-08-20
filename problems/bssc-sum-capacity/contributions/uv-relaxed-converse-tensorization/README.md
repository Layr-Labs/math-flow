# Tensorization of two separately relaxed UV scalar functionals

## Claim and exact scope

Let \(W:x\mapsto (Y,Z)\) be a finite-alphabet discrete memoryless
broadcast channel.  For an input law \(p\), define

\[
t_W(p)=I_p(X;Y)-I_p(X;Z).
\]

For a real function \(f\) on the input simplex, write

\[
\mathfrak C[f](p)
=\sup\left\{\sum_a \lambda_a f(p_a):
  \lambda_a\ge0,\ \sum_a\lambda_a=1,\
  \sum_a\lambda_a p_a=p\right\}
\]

for its upper concave envelope.  Put

\[
 A_W(p)=I_p(X;Y)+\mathfrak C[-t_W](p),\qquad
 D_W(p)=I_p(X;Z)+\mathfrak C[t_W](p),
\]

and define the two scalar functionals

\[
 B_{\rm avg}(W)=\sup_p\frac{A_W(p)+D_W(p)}2,
 \qquad
 B_{\rm br}(W)=\sup_p\min\{A_W(p),D_W(p)\}.
\]

The claim is the following single theorem and its BSSC specialization.

1. For arbitrary finite-alphabet DMBCs \(W_1,W_2\),
   \[
   B_{\rm avg}(W_1\times W_2)
   =B_{\rm avg}(W_1)+B_{\rm avg}(W_2).
   \]
   This includes correlated product-channel input laws and envelope
   auxiliaries that are joint across the factors.
2. If an involutive input relabeling exchanges the two receiver marginals,
   up to output relabeling, then
   \(B_{\rm br}(W)=B_{\rm avg}(W)\), and either supremum may be restricted
   to input laws invariant under that involution.  Finite products preserve
   this symmetry, so both scalar functionals are additive on finite products
   of receiver-skew channels.
3. For the half-skew BSSC \(P\) in the governed problem and every integer
   \(n\ge1\),
   \[
   B_{\rm br}(P^{\times n})=B_{\rm avg}(P^{\times n})
   =n\left(2h_2(1/4)-\frac54\right).
   \]
   The normalized value is
   \(0.37255624891826566\ldots\) bits per channel use.

This contribution depends on canonical transaction
`c70e1829a7c6a2a8cb8cfc2383f8abf825ac5ea6` only for the sharp scalar
BSSC posterior-support inequality used in the last specialization.  The
general product and symmetry theorem below is independent of that result.

The theorem concerns two *separately relaxed scalar* UV rows.  It does not
tensorize the complete UV rate region or a common joint-\((U,V)\)
optimization.  It says nothing about tensorization of the simplified GK
functional or the full Gohari--Liu--Nair Theorem-9 system, and it does not
identify the BSSC capacity.  Its normalized BSSC value is larger than the
governed upper endpoint \(0.369316568803963\), so it does not change the
problem's capacity interval.

## Product theorem

Write \(X_{12}=(X_1,X_2)\), and similarly for the outputs of the product
channel.  Let \(A-X_{12}-(Y_1,Z_1,Y_2,Z_2)\) be any finite auxiliary.  The
Csiszar sum identity, together with the product-channel Markov relations,
gives

\[
\begin{aligned}
 &I(X_{12};Y_1Y_2\mid A)-I(X_{12};Z_1Z_2\mid A)\\
 &=I(X_1;Y_1\mid A,Z_2)-I(X_1;Z_1\mid A,Z_2)\\
 &\quad+I(X_2;Y_2\mid A,Y_1)-I(X_2;Z_2\mid A,Y_1).
\end{aligned}
\tag{1}
\]

For completeness, expand the two left-hand mutual informations in opposite
orders.  The uncancelled cross terms are both \(I(Y_1;Z_2\mid A)\):

\[
\begin{aligned}
I(X_{12};Y_1Y_2\mid A)
 &=I(X_1;Y_1\mid A,Z_2)+I(X_2;Y_2\mid A,Y_1)
   +I(Y_1;Z_2\mid A),\\
I(X_{12};Z_1Z_2\mid A)
 &=I(X_1;Z_1\mid A,Z_2)+I(X_2;Z_2\mid A,Y_1)
   +I(Y_1;Z_2\mid A).
\end{aligned}
\]

Conditioning on \((A,Z_2)\) leaves the first factor governed by \(W_1\),
and conditioning on \((A,Y_1)\) leaves the second governed by \(W_2\).
The corresponding conditional input laws form posterior ensembles with
barycenters \(p_1\) and \(p_2\).  Thus (1), first for every posterior
ensemble of \(p_{12}\) and then after taking its supremum, proves

\[
\mathfrak C[t_{12}](p_{12})
\le \mathfrak C[t_1](p_1)+\mathfrak C[t_2](p_2).
\tag{2}
\]

Exchanging \(Y\) and \(Z\) in the same calculation gives

\[
\mathfrak C[-t_{12}](p_{12})
\le \mathfrak C[-t_1](p_1)+\mathfrak C[-t_2](p_2).
\tag{3}
\]

Output independence conditional on \(X_{12}\), followed by entropy
subadditivity, gives

\[
I(X_{12};Y_1Y_2)\le I(X_1;Y_1)+I(X_2;Y_2),
\]

and the analogous inequality for \(Z_1Z_2\).  Combining these inequalities
with (2)--(3) yields, for every possibly correlated \(p_{12}\),

\[
A_{12}(p_{12})\le A_1(p_1)+A_2(p_2),\qquad
D_{12}(p_{12})\le D_1(p_1)+D_2(p_2).
\tag{4}
\]

Taking the averaged row and its supremum proves the `<=` product inequality.

For the reverse inequality, take product input laws \(p_1p_2\).  Given
posterior ensembles for \(p_1\) and \(p_2\), their independent product
ensemble has barycenter \(p_1p_2\), while

\[
t_{12}(q_1q_2)=t_1(q_1)+t_2(q_2).
\]

Consequently both envelope inequalities (2)--(3) reverse at product input
laws.  The ordinary mutual informations are also additive there, so

\[
A_{12}(p_1p_2)=A_1(p_1)+A_2(p_2),\qquad
D_{12}(p_1p_2)=D_1(p_1)+D_2(p_2).
\]

Choosing factor laws arbitrarily close to their suprema proves the `>=`
inequality and hence exact additivity.  No attainment assumption is needed.

## Receiver-skew reduction

Suppose an involution \(S\) of the input alphabet exchanges the receiver
marginals up to bijective output relabelings.  Mutual information is invariant
under relabeling, so

\[
I_Y(Sp)=I_Z(p),\qquad t(Sp)=-t(p).
\]

Applying \(S\) to every member of a posterior ensemble is a barycenter-
preserving bijection.  Therefore

\[
A(Sp)=D(p),\qquad D(Sp)=A(p).
\tag{5}
\]

Both \(A\) and \(D\) are concave.  For
\(\bar p=(p+Sp)/2\), equations (5) and concavity give

\[
A(\bar p),D(\bar p)\ge \frac{A(p)+D(p)}2.
\]

Thus an invariant law attains at least the averaged value of every law, and

\[
B_{\rm br}(W)\ge B_{\rm avg}(W).
\]

The reverse inequality follows pointwise from
\(\min\{a,d\}\le(a+d)/2\).  This proves equality and the invariant-law
restriction.  The componentwise product of the involutions exchanges the
receivers of a product channel.  Combining this observation with the product
theorem proves the finite-product statement.

## Exact half-skew BSSC specialization

Let \(q=\Pr[X=1]\), \(h=h_2(1/4)\), and \(r=h-3/4\).  Directly from the two
channel matrices,

\[
I_Y(q)=h_2((1-q)/2)-(1-q),\qquad
I_Z(q)=h_2(q/2)-q.
\tag{6}
\]

The BSSC is receiver-skew under input and output bit flips, and its only
invariant binary input law is \(q=1/2\).  At that law,

\[
I_Y(1/2)=I_Z(1/2)=h-\frac12.
\tag{7}
\]

The sharp posterior support established by canonical transaction
`c70e1829a7c6a2a8cb8cfc2383f8abf825ac5ea6`, after reflection, is

\[
t(q)\le 2rq\qquad(0\le q\le1).
\tag{8}
\]

Every posterior ensemble with barycenter \(1/2\) therefore has average
\(t\) at most \(r\).  Equality is attained by putting mass \(5/8\) at
\(q=4/5\) and mass \(3/8\) at \(q=0\): its barycenter is \(1/2\), and (6)
gives \(t(4/5)=8r/5\) and \(t(0)=0\).  Hence

\[
\mathfrak C[t](1/2)=r.
\]

Receiver skew gives the same value for \(\mathfrak C[-t](1/2)\).  Combining
this with (7), the invariant-law reduction, and finite-product additivity
proves

\[
B_{\rm br}(P^{\times n})=B_{\rm avg}(P^{\times n})
=n\left(h-\frac12+r\right)
=n\left(2h_2(1/4)-\frac54\right).
\]

## Reproduction

From the repository root, run

```text
PYTHONDONTWRITEBYTECODE=1 python3 problems/bssc-sum-capacity/contributions/uv-relaxed-converse-tensorization/verify_specialization.py
```

The standard-library script evaluates (6)--(8) at 90-decimal precision,
checks the attaining posterior mixture and the receiver-skew channel
relations, and prints the normalized value.  It corroborates the exact
specialization; the universal theorem rests on the analytic proof above.
