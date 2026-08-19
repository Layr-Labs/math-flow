## `bssc-sum-capacity/uv-product-branchwise-additivity`

**Verdict: indeterminate**

The four substantive UV-functional assertions are supported by the supplied analytic arguments and the declared dependency. However, the exact declared statement additionally asserts that  
\[
C_{\rm sum}\le 0.369296945969202842443
\]
is a *certified full-Theorem-9 capacity upper bound*. No certificate or theorem establishing that bound is supplied or declared as a dependency; indeed, the problem statement expressly says that merely mentioning the corresponding local artifact does not pre-accept it. Thus the complete compound claim cannot be marked valid, even though its UV additivity and BSSC-evaluation components check out.

### 1. Product additivity of \(B_{\rm avg}\)

This part is verified.

For a product channel \(W_1\times W_2\) and arbitrary
\[
A-(X_1,X_2)-(Y_1,Z_1,Y_2,Z_2),
\]
the displayed chain-rule identity is correct even when \(X_1,X_2\) are correlated conditional on \(A\). Product memorylessness gives
\[
\begin{aligned}
I(X_1X_2;Y_1Y_2\mid A)
 &=I(X_1;Y_1\mid A)+I(X_2;Y_2\mid A,Y_1),\\
I(X_1X_2;Z_1Z_2\mid A)
 &=I(X_2;Z_2\mid A)+I(X_1;Z_1\mid A,Z_2).
\end{aligned}
\]
The co-information identity yields
\[
\begin{aligned}
I(X_1;Y_1\mid A)-I(X_1;Y_1\mid A,Z_2)
 &=I(Y_1;Z_2\mid A),\\
I(X_2;Z_2\mid A)-I(X_2;Z_2\mid A,Y_1)
 &=I(Y_1;Z_2\mid A).
\end{aligned}
\]
The residual conditional mutual informations vanish because
\[
Y_1\perp Z_2\mid(A,X_1),\qquad Z_2\perp Y_1\mid(A,X_2),
\]
which remain valid under an arbitrary correlated law of \((A,X_1,X_2)\). Hence the common correction terms cancel and give the asserted exact identity.

Moreover,
\[
(A,Z_2)-X_1-(Y_1,Z_1),\qquad
(A,Y_1)-X_2-(Y_2,Z_2),
\]
so each resulting bracket is an average of the corresponding one-factor function \(t_i\) over valid posterior input laws. Applying the definition and concavity of the upper concave envelope gives
\[
\mathfrak C[t_{12}](p_{12})
 \le \mathfrak C[t_1](p_1)+\mathfrak C[t_2](p_2).
\]
Swapping the receiver labels throughout gives the same inequality for \(-t\). This covers arbitrary finite alphabets, correlated product-channel priors, zero-probability input symbols, and joint envelope auxiliaries.

For the non-envelope terms,
\[
I(X_1X_2;Y_1Y_2)
 \le I(X_1;Y_1)+I(X_2;Y_2),
\]
because \(H(Y_1Y_2)\le H(Y_1)+H(Y_2)\), while product memorylessness gives
\[
H(Y_1Y_2\mid X_1X_2)
 =H(Y_1\mid X_1)+H(Y_2\mid X_2).
\]
The analogous inequality holds for \(Z\). This proves the required product upper bound for \(B_{\rm avg}\).

For the reverse inequality, product priors and product posterior decompositions satisfy
\[
t_{12}(p_{1a}\times p_{2b})
 =t_1(p_{1a})+t_2(p_{2b}).
\]
Taking arbitrarily near-optimal finite decompositions proves the reverse envelope inequalities at product priors, for both signs. The ordinary mutual informations are additive there. Taking suprema therefore establishes
\[
B_{\rm avg}(W_1\times W_2)
 =B_{\rm avg}(W_1)+B_{\rm avg}(W_2).
\]

### 2. Receiver-skew symmetry and \(B_{\rm br}=B_{\rm avg}\)

This part is verified.

If the affine input involution \(S\) exchanges the two receiver channels up to bijective output relabeling, then
\[
I_Y(Sp)=I_Z(p),\qquad I_Z(Sp)=I_Y(p),
\]
and consequently
\[
t(Sp)=-t(p).
\]
Because \(S\) bijects all finite posterior decompositions,
\[
\mathfrak C[-t](Sp)=\mathfrak C[t](p),\qquad
\mathfrak C[t](Sp)=\mathfrak C[-t](p).
\]
Thus
\[
A(Sp)=D(p),\qquad D(Sp)=A(p).
\]

Both \(A\) and \(D\) are concave: fixed-channel mutual information is concave in the input law, and the operational upper concave envelopes are concave. For
\[
\bar p=\frac{p+Sp}{2},
\]
one has \(S\bar p=\bar p\), and concavity gives
\[
A(\bar p),D(\bar p)\ge \frac{A(p)+D(p)}2.
\]
Therefore
\[
\min\{A(\bar p),D(\bar p)\}
 \ge \frac{A(p)+D(p)}2.
\]
Taking suprema proves \(B_{\rm br}\ge B_{\rm avg}\), while
\[
\min\{A(p),D(p)\}\le\frac{A(p)+D(p)}2
\]
gives the reverse inequality. Hence
\[
B_{\rm br}(W)=B_{\rm avg}(W).
\]

The same symmetrization shows that the supremum of either functional can be restricted to \(S\)-invariant input laws. In finite dimensions, the relevant extrema can also be attained using finite posterior decompositions, so the use of “optimum” causes no unresolved boundary issue.

### 3. Finite-product branchwise additivity

This part is verified.

The coordinatewise product of receiver-skew involutions and output bijections again exchanges the two vector receivers. Hence a finite product of receiver-skew-symmetric channels is receiver-skew-symmetric. Combining the preceding equality with product additivity of \(B_{\rm avg}\) gives
\[
\begin{aligned}
B_{\rm br}\!\left(\prod_i W_i\right)
 &=B_{\rm avg}\!\left(\prod_i W_i\right)\\
 &=\sum_i B_{\rm avg}(W_i)
 =\sum_i B_{\rm br}(W_i).
\end{aligned}
\]
No product-input or coordinatewise-auxiliary restriction is introduced in this argument.

### 4. Exact half-skew BSSC specialization

This part is verified from the declared dependency.

For \(q=P(X=1)\),
\[
\begin{aligned}
I_Y(q)&=h_2((1-q)/2)-(1-q),\\
I_Z(q)&=h_2(q/2)-q.
\end{aligned}
\]
At \(q=1/2\),
\[
I_Y(1/2)=I_Z(1/2)=h_2(1/4)-\frac12=:c.
\]

The BSSC input involution is \(q\mapsto1-q\); its unique invariant binary prior is \(q=1/2\). The declared dependency proves, for
\[
g(q)=I_Z(q)-I_Y(q)=-t(q),\qquad r=h_2(1/4)-\frac34,
\]
the global support
\[
g(q)\le 2r(1-q).
\]
Using \(g(1-q)=-g(q)\) gives
\[
t(q)\le 2rq.
\]
Thus every posterior decomposition with mean \(1/2\) obeys
\[
\mathbb E\,t(Q)\le2r\,\mathbb E Q=r.
\]
Equality is attained by
\[
P(Q=4/5)=5/8,\qquad P(Q=0)=3/8,
\]
since its mean is \(1/2\) and the dependency establishes
\[
t(4/5)=\frac85r,\qquad t(0)=0.
\]
Consequently
\[
\mathfrak C[t](1/2)=r.
\]
Reflection gives \(\mathfrak C[-t](1/2)=r\). Therefore
\[
A(1/2)=D(1/2)=c+r
 =2h_2(1/4)-\frac54.
\]
Since invariant-prior restriction leaves only the fair prior,
\[
B_{\rm br}(P)=B_{\rm avg}(P)
 =2h_2(1/4)-\frac54.
\]
Finite-product additivity then gives, for every finite \(n\ge1\),
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

### 5. Converse status and frontier effect

The value is indeed a valid separately relaxed UV converse. This can be grounded in the declared dependency’s two code-induced sum-rate rows: after incorporating \((W,T)\) into the respective auxiliaries, the two rows are bounded by \(A_W(p_X)\) and \(D_W(p_X)\) under the same overall input law. Thus every achievable sum rate is bounded by
\[
\sup_p\min\{A_W(p),D_W(p)\}=B_{\rm br}(W).
\]

It also cannot improve the governed published upper endpoint, since
\[
0.3725562489182657\ldots
>
0.369316568803963.
\]
Hence the claimed no-frontier-change conclusion follows already from the benchmark interval in the problem.

What remains unsupported is the stronger contextual assertion that
\[
0.369296945969202842443
\]
is presently a *certified full-Theorem-9 capacity bound*. The supplied material neither proves that theorem/certificate nor declares the relevant fixed-pair-certificate transaction as a dependency. The problem explicitly warns that its mention does not pre-accept it. This unresolved assertion prevents acceptance of the exact compound declared claim.
