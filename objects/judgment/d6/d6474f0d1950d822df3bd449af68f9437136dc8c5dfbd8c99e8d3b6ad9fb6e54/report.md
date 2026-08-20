## `bssc-sum-capacity/uv-relaxed-converse-tensorization`

**Verdict: VALID**

### 1. Product additivity of \(B_{\rm avg}\)

For an auxiliary \(A-X_{12}-(Y_1,Z_1,Y_2,Z_2)\) on the product channel, the displayed decomposition

\[
\begin{aligned}
&I(X_{12};Y_1Y_2\mid A)-I(X_{12};Z_1Z_2\mid A)\\
&=I(X_1;Y_1\mid A,Z_2)-I(X_1;Z_1\mid A,Z_2)\\
&\quad+I(X_2;Y_2\mid A,Y_1)-I(X_2;Z_2\mid A,Y_1)
\end{aligned}
\]

is correct. It follows by opposite-order chain-rule expansions; product-channel conditional independence justifies replacing terms such as
\(H(Y_1\mid X_1,A,Z_2)\) by \(H(Y_1\mid X_1)\). The cross term
\(I(Y_1;Z_2\mid A)\) appears identically in the two expansions and cancels.

Every posterior ensemble of \(p_{12}\) can be represented by such an \(A\). The conditional laws indexed by \((A,Z_2)\) and \((A,Y_1)\) are valid posterior ensembles of the factor marginals \(p_1,p_2\). Hence

\[
\mathfrak C[t_{12}](p_{12})
 \le \mathfrak C[t_1](p_1)+\mathfrak C[t_2](p_2),
\]

and receiver exchange gives the analogous inequality for \(-t\).

For arbitrary, potentially correlated \(p_{12}\),

\[
I(X_{12};Y_1Y_2)\le I(X_1;Y_1)+I(X_2;Y_2),
\]

because \(H(Y_1,Y_2)\le H(Y_1)+H(Y_2)\), while the product channel makes the conditional output entropy additive. The same argument applies to \(Z\). Thus

\[
A_{12}(p_{12})\le A_1(p_1)+A_2(p_2),\qquad
D_{12}(p_{12})\le D_1(p_1)+D_2(p_2),
\]

which proves the upper product inequality for \(B_{\rm avg}\).

For product inputs \(p_1p_2\), independent products of factor posterior ensembles satisfy

\[
t_{12}(q_1q_2)=t_1(q_1)+t_2(q_2).
\]

Together with the already proved upper inequalities, this gives exact envelope additivity at product inputs. Ordinary mutual information is also additive there. Choosing \(\varepsilon\)-optimal factor laws proves the reverse inequality without assuming attainment. Therefore

\[
B_{\rm avg}(W_1\times W_2)
=B_{\rm avg}(W_1)+B_{\rm avg}(W_2).
\]

### 2. Receiver-skew reduction

An input involution \(S\) exchanging the receiver marginals gives

\[
I_Y(Sp)=I_Z(p),\qquad t(Sp)=-t(p).
\]

Applying \(S\) to all members of a posterior ensemble proves

\[
A(Sp)=D(p),\qquad D(Sp)=A(p).
\]

Both \(A\) and \(D\) are concave: mutual information is concave in the input law, and the upper concave envelopes are concave by construction. Hence, for the invariant law
\(\bar p=(p+Sp)/2\),

\[
A(\bar p),D(\bar p)\ge \frac{A(p)+D(p)}2.
\]

It follows that

\[
\min\{A(\bar p),D(\bar p)\}
\ge \frac{A(p)+D(p)}2.
\]

Taking suprema yields \(B_{\rm br}\ge B_{\rm avg}\); the pointwise inequality
\(\min\{A,D\}\le(A+D)/2\) gives the reverse direction. The same symmetrization also justifies restricting both suprema to invariant input laws.

Componentwise involutions preserve receiver skew under finite products. Combining this fact with the already established additivity of \(B_{\rm avg}\) proves equality and additivity of both scalar functionals on finite products of receiver-skew channels.

### 3. Half-skew BSSC specialization

For \(q=\Pr[X=1]\), direct evaluation of the two channel matrices gives

\[
I_Y(q)=h_2((1-q)/2)-(1-q),\qquad
I_Z(q)=h_2(q/2)-q.
\]

At the unique input-flip-invariant binary law \(q=1/2\),

\[
I_Y(1/2)=I_Z(1/2)=h_2(1/4)-\frac12.
\]

The declared reference proves the global support inequality

\[
t(q)=I_Y(q)-I_Z(q)\le 2rq,\qquad
r=h_2(1/4)-\frac34,
\]

for every \(q\in[0,1]\). Its proof is adequate: after defining
\(g=-t\), it computes the sign-changing second derivative, constructs the tangent support at \(q=1/5\), handles the convex half using the endpoint chord, and reflects the result.

Therefore every posterior ensemble with barycenter \(1/2\) has average \(t\) at most \(r\). Equality is achieved by masses \(5/8\) at \(q=4/5\) and \(3/8\) at \(q=0\), since

\[
\frac58\frac45=\frac12,\qquad
t(4/5)=\frac85r,\qquad t(0)=0.
\]

Thus

\[
\mathfrak C[t](1/2)=r.
\]

Receiver skew gives \(\mathfrak C[-t](1/2)=r\). Consequently,

\[
B_{\rm br}(P)=B_{\rm avg}(P)
=h_2(1/4)-\frac12+r
=2h_2(1/4)-\frac54.
\]

Finite-product additivity then proves, for every \(n\ge1\),

\[
B_{\rm br}(P^{\times n})
=B_{\rm avg}(P^{\times n})
=n\left(2h_2(1/4)-\frac54\right).
\]

### 4. Dependency classification

**Required dependency:**

- `c70e1829a7c6a2a8cb8cfc2383f8abf825ac5ea6`

Only its sharp global BSSC posterior-support inequality is logically required for the exact specialization. The general product-additivity and receiver-skew arguments are independently established in the subject. The reference supplies a sufficient analytic proof of the needed support inequality.

### 5. Objective attestation

The terminal attestation records a successful pinned execution with exit code \(0\). The script checks:

- the contact identity at \(q=4/5\) numerically to \(10^{-80}\);
- the attaining mixture and its barycenter;
- the exact receiver-skew matrix relations using rational arithmetic; and
- the numerical value
  \[
  0.372556248918265727819391584\ldots.
  \]

It does **not** verify the continuum support inequality or the universal product theorem; those are established analytically above.

There is a minor non-governing numerical typo in the README, which states
\(0.37255624891826566\ldots\). The correct expansion begins
\(0.3725562489182657278\ldots\), as the attestation reports. This does not affect the exact declared formula.

The claim is correctly scoped: it establishes only the two separately relaxed scalar functionals and makes no inference about the full UV region, a common \((U,V)\) optimization, the GK functional, or the BSSC capacity.
