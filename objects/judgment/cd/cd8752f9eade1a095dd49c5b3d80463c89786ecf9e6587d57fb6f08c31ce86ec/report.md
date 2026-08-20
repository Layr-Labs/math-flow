## `bssc-sum-capacity/uv-relaxed-converse-tensorization`

**Verdict: Valid**

**Required dependency:** `c70e1829a7c6a2a8cb8cfc2383f8abf825ac5ea6`, but only for the global sharp BSSC support inequality used in the specialization. The general product and receiver-skew arguments are independently established in the subject. The reference’s dependence-balance and entropy-counterfeit results are not dependencies.

### 1. Product identity and concave-envelope bounds

For an auxiliary \(A-X_1X_2-(Y_1,Z_1,Y_2,Z_2)\), the displayed decomposition

\[
\begin{aligned}
&I(X_1X_2;Y_1Y_2\mid A)-I(X_1X_2;Z_1Z_2\mid A)\\
&=I(X_1;Y_1\mid A,Z_2)-I(X_1;Z_1\mid A,Z_2)\\
&\quad+I(X_2;Y_2\mid A,Y_1)-I(X_2;Z_2\mid A,Y_1)
\end{aligned}
\]

is correct. For example, product-channel conditional independence gives

\[
H(Y_1\mid X_1,A,Z_2)=H(Y_1\mid X_1),
\]

and similarly for the other three channel outputs. The two expansions in the subject then both contain exactly the cross term \(I(Y_1;Z_2\mid A)\), which cancels.

Conditioned on \((A,Z_2)\), the first difference is the average of
\(t_{W_1}\) over the posterior laws of \(X_1\); those posteriors have barycenter \(p_1\). The analogous statement holds for \(X_2\) conditioned on \((A,Y_1)\). Thus

\[
\mathfrak C[t_{12}](p_{12})
 \le \mathfrak C[t_1](p_1)+\mathfrak C[t_2](p_2).
\]

Swapping the receivers yields the same inequality for \(-t\). This argument covers correlated \(p_{12}\) and auxiliaries joint across the factors.

Entropy subadditivity and product-channel conditional entropy additivity correctly give

\[
I(X_1X_2;Y_1Y_2)\le I(X_1;Y_1)+I(X_2;Y_2),
\]

and likewise for \(Z\). Hence the claimed pointwise inequalities for \(A\) and \(D\) follow.

For product input laws, independent products of posterior ensembles have the correct barycenter, and

\[
t_{12}(q_1q_2)=t_1(q_1)+t_2(q_2).
\]

Together with the preceding upper bound, this establishes equality of both concave envelopes at product laws. Ordinary mutual information is additive there as well. Taking factor laws arbitrarily close to their respective suprema proves the reverse inequality without requiring attainment. Therefore

\[
B_{\rm avg}(W_1\times W_2)
=B_{\rm avg}(W_1)+B_{\rm avg}(W_2).
\]

No cardinality, boundary, or correlated-input case is omitted.

### 2. Receiver-skew reduction

An involutive input permutation \(S\) exchanging the receiver marginals implies

\[
I_Y(Sp)=I_Z(p),\qquad t(Sp)=-t(p).
\]

Applying \(S\) to every posterior in an ensemble correctly gives

\[
A(Sp)=D(p),\qquad D(Sp)=A(p).
\]

Both \(A\) and \(D\) are concave: channel mutual information is concave in the input law, and the defined upper concave envelope is concave. Thus, for the invariant law
\(\bar p=(p+Sp)/2\),

\[
A(\bar p),D(\bar p)\ge \frac{A(p)+D(p)}2.
\]

Consequently,

\[
B_{\rm br}\ge B_{\rm avg},
\]

while the pointwise inequality
\(\min\{A,D\}\le (A+D)/2\) gives the reverse direction. This also justifies restricting both suprema to invariant laws.

The componentwise product involution exchanges the complete product receiver marginals, so the same equality holds for finite products. Combining this with additivity of \(B_{\rm avg}\) proves additivity of \(B_{\rm br}\) on products of receiver-skew channels.

### 3. Half-skew BSSC specialization

For \(q=\Pr[X=1]\), the formulas

\[
I_Y(q)=h_2((1-q)/2)-(1-q),\qquad
I_Z(q)=h_2(q/2)-q
\]

follow directly from the transition matrices. At \(q=1/2\),

\[
I_Y(1/2)=I_Z(1/2)=h_2(1/4)-\frac12.
\]

The declared reference proves, for
\(g(q)=I_Z(q)-I_Y(q)\) and \(r=h_2(1/4)-3/4\),

\[
g(q)\le 2r(1-q).
\]

Its proof is sufficient: the stated second derivative has the correct sign, the tangent identities at \(q=1/5\) are correct, concavity controls \(q\le 1/2\), and convexity with zero endpoint values controls \(q\ge1/2\). Reflecting via \(g(1-q)=-g(q)\) gives exactly the inequality needed by the subject:

\[
t(q)=I_Y(q)-I_Z(q)\le 2rq.
\]

Therefore every posterior ensemble with barycenter \(1/2\) has average \(t\) at most \(r\). The two-point ensemble

\[
\Pr(q=4/5)=5/8,\qquad \Pr(q=0)=3/8
\]

has barycenter \(1/2\), and \(t(4/5)=8r/5\), so it attains average \(r\). Hence

\[
\mathfrak C[t](1/2)=\mathfrak C[-t](1/2)=r.
\]

The binary input-flip involution has the unique invariant input law \(q=1/2\). The receiver-skew reduction and product theorem therefore yield, for every \(n\ge1\),

\[
B_{\rm br}(P^{\times n})
=B_{\rm avg}(P^{\times n})
=n\left(2h_2(1/4)-\frac54\right).
\]

### 4. Objective attestation scope

The passed attestation verifies only:

- the contact value at \(q=4/5\) to \(10^{-80}\) Decimal tolerance;
- the attaining posterior mixture and its barycenter;
- the receiver-skew matrix identities exactly using rational arithmetic;
- the numerical evaluation of the final constant.

It does **not** verify the global support inequality over all \(q\), the concave-envelope optimization, or the product theorem. Those obligations are instead discharged analytically by the subject and the required reference, so the limited scope of the executable evidence does not leave a gap.

### Minor non-claim defect

The README’s decimal

\[
0.37255624891826566\ldots
\]

is inaccurate. The exact expression begins

\[
0.372556248918265727819391584\ldots,
\]

as also shown by the attested execution. This does not affect the declared claim, which states the correct exact value. The result remains explicitly scoped to the two separately relaxed scalar functionals and does not establish capacity tensorization or a new capacity bound.
