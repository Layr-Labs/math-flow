## `bssc-sum-capacity/uv-relaxed-converse-tensorization`

**Verdict: valid**

The supplied analytic proof establishes the exact declared statement, including correlated product inputs and joint envelope auxiliaries.

### 1. Product-channel decomposition

Every finite posterior ensemble \(\{(\lambda_a,p_a)\}\) of an input law \(p_{12}\) can be represented by a finite auxiliary \(A\) satisfying
\[
A-X_1X_2-(Y_1,Z_1,Y_2,Z_2),
\]
with
\[
\sum_a\lambda_a t_{12}(p_a)
=I(X_1X_2;Y_1Y_2\mid A)-I(X_1X_2;Z_1Z_2\mid A).
\]

For a product channel, the required conditional independences hold even when \(X_1,X_2\) are correlated and \(A\) is joint across both factors. In particular,
\[
Y_1-X_1-(A,X_2,Y_2,Z_2),\qquad
Z_2-X_2-(A,X_1,Y_1,Z_1),
\]
and the receiver-swapped analogues hold. Chain-rule expansion therefore gives
\[
\begin{aligned}
I(X_{12};Y_1Y_2\mid A)
&=I(X_1;Y_1\mid A,Z_2)
 +I(X_2;Y_2\mid A,Y_1)
 +I(Y_1;Z_2\mid A),\\
I(X_{12};Z_1Z_2\mid A)
&=I(X_1;Z_1\mid A,Z_2)
 +I(X_2;Z_2\mid A,Y_1)
 +I(Y_1;Z_2\mid A).
\end{aligned}
\]
Thus the common cross term cancels and equation (1) is correct.

Conditioning on \((A,Z_2)\) produces a finite posterior ensemble of the marginal law \(p_1\), while conditioning on \((A,Y_1)\) produces one of \(p_2\). Consequently,
\[
\mathfrak C[t_{12}](p_{12})
\le \mathfrak C[t_1](p_1)+\mathfrak C[t_2](p_2).
\]
Receiver exchange gives the corresponding inequality for \(-t\).

For arbitrary correlated \(p_{12}\), product-channel conditional independence and entropy subadditivity give
\[
I(X_{12};Y_1Y_2)\le I(X_1;Y_1)+I(X_2;Y_2),
\]
and similarly for \(Z_1Z_2\). Hence
\[
A_{12}(p_{12})\le A_1(p_1)+A_2(p_2),\qquad
D_{12}(p_{12})\le D_1(p_1)+D_2(p_2).
\]
Taking the averaged row and then its supremum proves the required upper product inequality.

### 2. Reverse product inequality

For product input \(p_1p_2\), independently combining arbitrary finite posterior ensembles of \(p_1\) and \(p_2\) gives an ensemble of \(p_1p_2\). At every product posterior,
\[
t_{12}(q_1q_2)=t_1(q_1)+t_2(q_2),
\]
because both receiver mutual informations are additive. It follows, using arbitrarily near-optimal ensembles if necessary, that
\[
\mathfrak C[\pm t_{12}](p_1p_2)
\ge \mathfrak C[\pm t_1](p_1)+\mathfrak C[\pm t_2](p_2).
\]
Combined with the already proved upper inequalities, equality holds. Ordinary mutual information is also additive at product inputs, so
\[
A_{12}(p_1p_2)=A_1(p_1)+A_2(p_2),\qquad
D_{12}(p_1p_2)=D_1(p_1)+D_2(p_2).
\]
Choosing each \(p_i\) arbitrarily close to maximizing
\((A_i+D_i)/2\) proves
\[
B_{\rm avg}(W_1\times W_2)
=B_{\rm avg}(W_1)+B_{\rm avg}(W_2).
\]
No attainment assumption is used.

### 3. Receiver-skew reduction

The upper concave-envelope operation is concave: two finite ensembles can be concatenated to obtain an ensemble at any convex combination of their barycenters. Since channel mutual information is concave in the input law, both \(A\) and \(D\) are concave.

If the involution \(S\) exchanges receiver marginals up to bijective output relabeling, then
\[
I_Y(Sp)=I_Z(p),\qquad t(Sp)=-t(p).
\]
Applying \(S\) to each member of an ensemble proves exactly
\[
A(Sp)=D(p),\qquad D(Sp)=A(p).
\]
For the invariant symmetrization \(\bar p=(p+Sp)/2\),
\[
A(\bar p),D(\bar p)\ge \frac{A(p)+D(p)}2.
\]
Therefore
\[
\min\{A(\bar p),D(\bar p)\}
\ge \frac{A(p)+D(p)}2,
\]
which implies \(B_{\rm br}\ge B_{\rm avg}\). The reverse inequality follows pointwise from
\[
\min\{A,D\}\le \frac{A+D}{2}.
\]
Thus
\[
B_{\rm br}(W)=B_{\rm avg}(W),
\]
and both suprema may be restricted to invariant laws. Componentwise products of the involutions preserve receiver skew, so together with averaged additivity this proves additivity of both functionals over every finite product of receiver-skew channels.

### 4. Half-skew BSSC specialization

For \(q=\Pr[X=1]\), direct evaluation of the channel matrices gives
\[
I_Y(q)=h_2((1-q)/2)-(1-q),\qquad
I_Z(q)=h_2(q/2)-q.
\]
The input complement exchanges the two receiver channels up to output complement, and the only invariant binary input law is \(q=1/2\). At that law,
\[
I_Y(1/2)=I_Z(1/2)=h_2(1/4)-\frac12.
\]

The declared dependency proves, for \(g=I_Z-I_Y\),
\[
g(q)\le 2r(1-q),\qquad r=h_2(1/4)-\frac34,
\]
and \(g(1-q)=-g(q)\). Reflecting this inequality gives
\[
t(q)=I_Y(q)-I_Z(q)\le 2rq.
\]
Thus every posterior ensemble with mean \(1/2\) satisfies
\[
\mathbb E[t(q_A)]\le 2r\,\mathbb E[q_A]=r.
\]
The ensemble with masses \(5/8\) at \(q=4/5\) and \(3/8\) at \(q=0\) has mean \(1/2\), and the dependency’s contact identity gives
\[
t(4/5)=\frac85r,\qquad t(0)=0.
\]
Its average is therefore exactly \(r\), proving
\[
\mathfrak C[t](1/2)=r.
\]
Receiver skew similarly gives
\[
\mathfrak C[-t](1/2)=r.
\]

Hence the single-channel value is
\[
h_2(1/4)-\frac12+r
=2h_2(1/4)-\frac54.
\]
Product additivity and product receiver skew yield, for every integer \(n\ge1\),
\[
B_{\rm br}(P^{\times n})
=B_{\rm avg}(P^{\times n})
=n\left(2h_2(1/4)-\frac54\right).
\]

The normalized numerical value
\[
2h_2(1/4)-\frac54
=0.37255624891826566\ldots
\]
is consistent with the exact formula.

### 5. Scope

The contribution correctly limits its conclusion to the two explicitly defined, separately relaxed scalar functionals. No inference is made to tensorization of a common joint-\((U,V)\) optimization, the full UV region, the GK functional, the Gohari–Liu–Nair system, or the private-message capacity. Thus the value exceeding the governed capacity upper bound creates no contradiction.
