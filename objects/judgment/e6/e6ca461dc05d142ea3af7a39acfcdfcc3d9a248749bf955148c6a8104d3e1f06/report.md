## `bssc-sum-capacity/uv-product-branchwise-additivity`

**Verdict: VALID**

### Required dependency

- `c70e1829a7c6a2a8cb8cfc2383f8abf825ac5ea6`
  - Required for the globally valid BSSC posterior-support inequality and its equality contact, which are needed for the exact one-letter BSSC evaluation.
  - Its finite-block code-induced sum-rate rows also supply an independent justification that the resulting branchwise functional is a genuine private-message converse.

The Yukon commit, authorship, byte-identity, and prior-acceptance descriptions are provenance only and are not mathematical dependencies.

### 1. Product chain-rule identity

For arbitrary finite \(A\) with
\[
A-(X_1,X_2)-(Y_1,Z_1,Y_2,Z_2)
\]
on the product channel, product memorylessness gives
\[
\begin{aligned}
I(X_1X_2;Y_1Y_2\mid A)
 &=I(X_1;Y_1\mid A)+I(X_2;Y_2\mid A,Y_1),\\
I(X_1X_2;Z_1Z_2\mid A)
 &=I(X_2;Z_2\mid A)+I(X_1;Z_1\mid A,Z_2).
\end{aligned}
\]
These identities do not require \(X_1\) and \(X_2\) to be independent.

The co-information identity used in the submission is valid. Moreover,
\[
Y_1\perp Z_2\mid(A,X_1),\qquad Z_2\perp Y_1\mid(A,X_2),
\]
even for correlated inputs, because the two channel factors are independent once their respective inputs are fixed. Thus both correction terms equal \(I(Y_1;Z_2\mid A)\) and cancel, proving
\[
\begin{aligned}
&I(X_1X_2;Y_1Y_2\mid A)-I(X_1X_2;Z_1Z_2\mid A)\\
&=I(X_1;Y_1\mid A,Z_2)-I(X_1;Z_1\mid A,Z_2)\\
&\quad+I(X_2;Y_2\mid A,Y_1)-I(X_2;Z_2\mid A,Y_1).
\end{aligned}
\]

No hidden independence assumption is used.

### 2. Concave-envelope factorization

The conditional variables satisfy
\[
(A,Z_2)-X_1-(Y_1,Z_1),\qquad
(A,Y_1)-X_2-(Y_2,Z_2).
\]
Consequently, each bracket in the preceding identity is an average of the corresponding one-factor \(t_i\) over valid posterior input laws. Applying the envelope first within each conditioning value and then its concavity yields
\[
\mathfrak C[t_{12}](p_{12})
 \le \mathfrak C[t_1](p_1)+\mathfrak C[t_2](p_2).
\]
Swapping \(Y_i\) and \(Z_i\) proves the same inequality for \(-t\). This argument covers:

- arbitrary correlated \(p_{12}\);
- arbitrary finite joint envelope auxiliaries;
- boundary and zero-probability input laws, using only positive-probability conditional atoms.

### 3. Exact additivity of \(B_{\rm avg}\)

For a correlated product-channel input,
\[
I(X_1X_2;Y_1Y_2)\le I(X_1;Y_1)+I(X_2;Y_2),
\]
and analogously for \(Z\). This follows from output-entropy subadditivity and exact additivity of conditional output entropy under a product channel.

Combining these inequalities with the two envelope inequalities gives
\[
F_{12}(p_{12})\le F_1(p_1)+F_2(p_2),
\]
where \(F_W=(A_W+D_W)/2\). Taking suprema proves the upper product bound.

For the reverse direction, product priors and products of arbitrarily near-optimal posterior decompositions give
\[
\mathfrak C[\pm t_{12}](p_1\times p_2)
\ge \mathfrak C[\pm t_1](p_1)+\mathfrak C[\pm t_2](p_2).
\]
Together with the already proved reverse inequality, these are equalities at product priors. The ordinary mutual informations are also additive there. Maximizing, or taking maximizing sequences, therefore gives
\[
B_{\rm avg}(W_1\times W_2)
=B_{\rm avg}(W_1)+B_{\rm avg}(W_2).
\]

### 4. Receiver-skew symmetrization

Let \(S\) be the induced affine input involution. Receiver exchange implies
\[
I_Y(Sp)=I_Z(p),\qquad I_Z(Sp)=I_Y(p),
\]
hence \(t(Sp)=-t(p)\).

Because \(S\) bijects all finite posterior decompositions,
\[
\mathfrak C[-t](Sp)=\mathfrak C[t](p),\qquad
\mathfrak C[t](Sp)=\mathfrak C[-t](p).
\]
Thus
\[
A_W(Sp)=D_W(p),\qquad D_W(Sp)=A_W(p).
\]

Both \(A_W\) and \(D_W\) are concave. For
\[
\bar p=\frac{p+Sp}{2},
\]
which is invariant under \(S\), concavity gives
\[
A_W(\bar p),D_W(\bar p)
\ge \frac{A_W(p)+D_W(p)}2.
\]
Therefore
\[
B_{\rm br}(W)\ge B_{\rm avg}(W).
\]
The pointwise inequality
\[
\min\{A_W(p),D_W(p)\}\le\frac{A_W(p)+D_W(p)}2
\]
gives the reverse inequality. Hence
\[
B_{\rm br}(W)=B_{\rm avg}(W),
\]
and the supremum for either functional may be restricted to invariant input laws.

### 5. Finite products of skew-symmetric channels

Coordinatewise input involutions and output relabelings exchange the two vector receivers of a finite product channel. Thus the product remains receiver-skew-symmetric. Combining this fact with the preceding equality and product additivity of \(B_{\rm avg}\) gives
\[
B_{\rm br}\!\left(\prod_i W_i\right)
=B_{\rm avg}\!\left(\prod_i W_i\right)
=\sum_i B_{\rm avg}(W_i)
=\sum_i B_{\rm br}(W_i).
\]
This remains valid when the product-channel prior is correlated and the envelope auxiliaries are joint across coordinates.

### 6. Exact BSSC specialization

For the half-skew BSSC, input complementation exchanges the receivers, and the only invariant binary prior is \(q=P(X=1)=1/2\).

Put
\[
h=h_2(1/4),\qquad c=h-\frac12,\qquad r=h-\frac34.
\]
The declared reference proves the global support inequality for
\(g=I_Z-I_Y=-t\). Reflection gives
\[
t(q)\le 2rq,\qquad 0\le q\le1.
\]
Thus every posterior decomposition with mean \(1/2\) satisfies
\[
\mathbb E[t(q_A)]\le r.
\]
Equality is attained by masses \(5/8\) at \(q=4/5\) and \(3/8\) at \(q=0\), since the barycenter is \(1/2\) and
\[
t(4/5)=\frac85r.
\]
Therefore
\[
\mathfrak C[t](1/2)=r.
\]
Reflection gives \(\mathfrak C[-t](1/2)=r\). At the fair prior,
\[
I(X;Y)=I(X;Z)=h_2(1/4)-\frac12=c.
\]
Hence
\[
B_{\rm br}(P)=B_{\rm avg}(P)
=c+r=2h_2(1/4)-\frac54.
\]
Finite-product additivity then proves, for every \(n\ge1\),
\[
B_{\rm br}(P^{\times n})=B_{\rm avg}(P^{\times n})
=n\left(2h_2(1/4)-\frac54\right).
\]

The numerical value
\[
2h_2(1/4)-\frac54
=0.3725562489182657\ldots
\]
is consistent with the exact expression.

### 7. Converse status and frontier effect

The declared reference’s finite-block sum-rate rows imply the converse directly. For example, with \(A'=(U,W,T)\),
\[
R_1+R_2
\le I(U,W;Y\mid T)+I(X;Z\mid U,W,T)+o(1)
\le I(A';Y)+I(X;Z\mid A')+o(1)
\le A_W(p_X)+o(1),
\]
and the other row similarly gives \(D_W(p_X)+o(1)\). Thus
\[
R_1+R_2\le B_{\rm br}(W)+o(1).
\]
So the BSSC value is indeed a valid UV converse.

Because
\[
0.3725562489182657\ldots
>0.369316568803963,
\]
it is already weaker than the governed published upper endpoint and cannot improve the capacity interval. The stronger \(0.369296945969202842443\) provenance is not needed for that conclusion and is not independently certified by this packet.

### Objective evidence

No terminal objective attestation was supplied. The included Python scripts are explicitly corroborative finite tests, not proofs of the universal theorem. The analytic arguments and the declared reference suffice without relying on those executions.
