# Mathematical Judgment

## Overall assessment

The subject transaction supports a correct and well-scoped theorem chain about two **separately relaxed UV sum-rate scalar functionals**:

1. the symmetric averaged functional is exactly additive over arbitrary finite-alphabet product broadcast channels;
2. for receiver-skew-symmetric channels, the branchwise minimum equals the averaged functional;
3. consequently, the branchwise scalar is additive over finite products of receiver-skew-symmetric channels; and
4. for the half-skew BSSC, both normalized functionals equal
   \[
   2h_2(1/4)-\frac54
   =0.3725562489182657\ldots
   \]
   at every finite blocklength.

The decisive arguments are analytic and do not depend on the accompanying numerical experiments. The scope limitations are important and are stated correctly: the result does **not** establish additivity of the complete UV outer region, a common joint-\((U,V)\) optimization, the simplified Gohari–Liu–Nair functional, or the full Theorem 9 system.

The BSSC value is a valid but noncompetitive converse value. It exceeds the supplied continuously certified full-Theorem-9 upper bound near \(0.3692969459692\), so it neither improves the capacity upper frontier nor supplies an achievable rate.

---

## Finding 1 — Exact product additivity of the averaged, separately relaxed UV functional

**Claim key:** `uv-averaged-functional-product-additivity`

### Proposition assessed

For finite-alphabet broadcast channels \(W_1,W_2\), define
\[
t_W(p)=I_p(X;Y)-I_p(X;Z),
\]
\[
A_W(p)=I_p(X;Y)+\mathfrak C[-t_W](p),\qquad
D_W(p)=I_p(X;Z)+\mathfrak C[t_W](p),
\]
and
\[
B_{\rm avg}(W)=\sup_p\frac{A_W(p)+D_W(p)}2.
\]
The subject claims
\[
B_{\rm avg}(W_1\times W_2)
=
B_{\rm avg}(W_1)+B_{\rm avg}(W_2),
\]
including arbitrarily correlated product-channel inputs and envelope auxiliaries joint across the two factors.

### Decisive reasoning

The crucial supplied identity is
\[
\begin{aligned}
&I(X_1X_2;Y_1Y_2\mid A)-I(X_1X_2;Z_1Z_2\mid A)\\
&=I(X_1;Y_1\mid A,Z_2)-I(X_1;Z_1\mid A,Z_2)\\
&\quad+I(X_2;Y_2\mid A,Y_1)-I(X_2;Z_2\mid A,Y_1).
\end{aligned}
\tag{1}
\]

This identity is correct. One way to audit its nontrivial part is to expand the output entropies. The apparent cross corrections reduce to
\[
H(Y_1\mid A)-H(Z_2\mid A)
=
H(Y_1\mid A,Z_2)-H(Z_2\mid A,Y_1),
\]
which follows by expanding \(H(Y_1,Z_2\mid A)\) in the two possible orders. Product-channel conditional independence supplies the channel-noise terms needed to identify the remaining quantities with the displayed conditional mutual informations.

For every auxiliary \(A\), the conditioned variables \((A,Z_2)\) and \((A,Y_1)\) are legitimate one-factor auxiliaries:
\[
(A,Z_2)-X_1-(Y_1,Z_1),\qquad
(A,Y_1)-X_2-(Y_2,Z_2).
\]
Consequently, taking expectations of (1) over the relevant posterior laws yields
\[
\mathfrak C[t_{12}](p_{12})
\le
\mathfrak C[t_1](p_1)+\mathfrak C[t_2](p_2).
\tag{2}
\]
Negating (1) gives the corresponding inequality for \(-t\):
\[
\mathfrak C[-t_{12}](p_{12})
\le
\mathfrak C[-t_1](p_1)+\mathfrak C[-t_2](p_2).
\tag{3}
\]

The ordinary mutual informations also satisfy, for arbitrary correlated \(p_{12}\),
\[
I(X_1X_2;Y_1Y_2)
\le I(X_1;Y_1)+I(X_2;Y_2),
\]
and similarly for \(Z\). This follows from output-entropy subadditivity together with additivity of the conditional channel entropies. Combining these inequalities with (2)–(3) proves the product upper bound.

The reverse inequality is also justified. Choose product input laws and independent posterior decompositions approaching each factor’s two concave-envelope values. For product posteriors,
\[
t_{12}(p_{1,a}p_{2,b})=t_1(p_{1,a})+t_2(p_{2,b}),
\]
so the product decomposition realizes the sum of the two one-factor envelope objectives. Applying the same construction separately to \(t\) and \(-t\) establishes the required lower bound. No common envelope auxiliary for the two signs is being asserted or needed because \(B_{\rm avg}\) itself contains two separately optimized envelopes.

### Judgment

**Accepted with high confidence.**

The proof covers the advertised finite-alphabet generality and does not assume product input laws in the difficult upper-bound direction. The executable random-channel checks are merely corroborative; the analytic identity and envelope argument are sufficient.

### Scope qualification

This proposition concerns the scalar functional built from **separate** upper concave envelopes. It does not imply product additivity of:

- the complete UV rate region;
- a scalar retaining a common joint law for both UV auxiliaries;
- arbitrary weighted UV scalarizations;
- the simplified GK functional; or
- the full Gohari–Liu–Nair Theorem 9 bound.

The subject states these exclusions correctly.

---

## Finding 2 — Equality of branchwise and averaged UV scalars under receiver-skew symmetry

**Claim key:** `receiver-skew-symmetric-uv-branch-average-equality`

### Proposition assessed

Suppose an involutive input relabeling \(S\) exchanges the two receiver channels up to bijective output relabeling. Define
\[
B_{\rm br}(W)=\sup_p\min\{A_W(p),D_W(p)\}.
\]
The claim is
\[
B_{\rm br}(W)=B_{\rm avg}(W),
\]
and the optimization may be restricted to \(S\)-invariant input laws.

### Decisive reasoning

Receiver exchange gives
\[
I_Y(Sp)=I_Z(p),\qquad I_Z(Sp)=I_Y(p),
\]
and therefore
\[
t(Sp)=-t(p).
\]

Because \(S\) is affine and bijects all finite posterior decompositions of \(p\) with those of \(Sp\), the upper concave envelopes transform exactly:
\[
\mathfrak C[-t](Sp)=\mathfrak C[t](p),\qquad
\mathfrak C[t](Sp)=\mathfrak C[-t](p).
\]
Hence
\[
A_W(Sp)=D_W(p),\qquad D_W(Sp)=A_W(p).
\tag{4}
\]

Both \(A_W\) and \(D_W\) are concave: mutual information is concave in the input law for a fixed channel, and the upper concave envelope is concave by construction. For
\[
\bar p=\frac{p+Sp}{2},
\]
concavity and (4) give
\[
A_W(\bar p)\ge\frac{A_W(p)+D_W(p)}2,
\]
\[
D_W(\bar p)\ge\frac{D_W(p)+A_W(p)}2.
\]
Therefore
\[
\min\{A_W(\bar p),D_W(\bar p)\}
\ge\frac{A_W(p)+D_W(p)}2.
\tag{5}
\]
Taking suprema proves
\[
B_{\rm br}(W)\ge B_{\rm avg}(W).
\]
The reverse inequality is immediate from
\[
\min\{a,d\}\le\frac{a+d}{2}.
\]
Thus equality follows.

Since \(\bar p\) is \(S\)-invariant, (5) also proves the claimed restriction to invariant input laws. At an invariant law, covariance additionally gives \(A_W(\bar p)=D_W(\bar p)\).

### Judgment

**Accepted with high confidence.**

The proof is complete, short, and does not require a binary input alphabet. It uses precisely the symmetry needed to exchange the two scalar rows.

### Missing extensions, not proof defects

No evidence is supplied—and none is claimed—for analogous equality on nonsymmetric channels. Likewise, this argument does not convert the separately relaxed rows into a simultaneous common-\((U,V)\) formulation.

---

## Finding 3 — Product additivity of the branchwise scalar for skew-symmetric factors

**Claim key:** `receiver-skew-symmetric-uv-branchwise-product-additivity`

### Proposition assessed

For finite-alphabet receiver-skew-symmetric channels \(W_1,\dots,W_n\),
\[
B_{\rm br}\!\left(\prod_{i=1}^nW_i\right)
=
\sum_{i=1}^n B_{\rm br}(W_i).
\]

### Decisive reasoning

The product channel remains receiver-skew-symmetric under the coordinatewise input involution and coordinatewise output relabelings. Applying Finding 2 to the product and to each factor gives
\[
B_{\rm br}\!\left(\prod_iW_i\right)
=
B_{\rm avg}\!\left(\prod_iW_i\right),
\]
and
\[
B_{\rm br}(W_i)=B_{\rm avg}(W_i).
\]
Finding 1 then gives
\[
B_{\rm avg}\!\left(\prod_iW_i\right)
=
\sum_iB_{\rm avg}(W_i).
\]
Combining these equalities proves the proposition.

This deduction inherits the full scope of the averaged additivity theorem: the product-channel input may be correlated, and the concave-envelope auxiliary may range jointly across all factors.

### Judgment

**Accepted with high confidence.**

This is a valid dependency-ordered consequence of the first two findings. There is no hidden product-input restriction.

---

## Finding 4 — Exact BSSC value of the two UV scalars

**Claim key:** `half-skew-bssc-uv-relaxed-scalar-value`

### Proposition assessed

For the half-skew BSSC \(P\),
\[
B_{\rm br}(P)=B_{\rm avg}(P)
=
2h_2(1/4)-\frac54,
\]
and hence
\[
B_{\rm br}(P^{\times n})
=
B_{\rm avg}(P^{\times n})
=
n\left(2h_2(1/4)-\frac54\right)
\]
for every finite \(n\ge1\).

### Receiver symmetry

The input flip \(x\mapsto1-x\), together with output flips, exchanges the two marginal receiver channels. Thus the BSSC satisfies the symmetry hypothesis of Findings 2 and 3.

For the binary one-letter input law, the only distribution invariant under the input flip is the fair prior \(q=1/2\). Therefore the global one-letter scalar optimization can be evaluated there.

### Exact envelope calculation

Let
\[
h=h_2(1/4),\qquad
c=h-\frac12,\qquad
r=h-\frac34.
\]
At the fair prior,
\[
I_Y(1/2)=I_Z(1/2)=c.
\]

The supporting transaction supplies the sharp BSSC posterior support. With
\[
t(q)=I_Y(q)-I_Z(q),
\]
one has
\[
t(q)\le 2rq.
\tag{6}
\]
This is the reflection of the proved tangent support for
\[
g(q)=I_Z(q)-I_Y(q).
\]
Any posterior decomposition with mean \(1/2\) therefore satisfies
\[
\mathbb E\,t(q_A)\le 2r\,\mathbb E q_A=r.
\]
Equality is attained by the two-point posterior mixture
\[
\frac58\delta_{4/5}+\frac38\delta_0,
\]
because its mean is \(1/2\) and
\[
t(4/5)=\frac85r,\qquad t(0)=0.
\]
Thus
\[
\mathfrak C[t](1/2)=r.
\]
Reflection gives
\[
\mathfrak C[-t](1/2)=r.
\]

It follows that
\[
A_P(1/2)=D_P(1/2)=c+r
=
2h_2(1/4)-\frac54.
\]
Numerically,
\[
2h_2(1/4)-\frac54
=
0.3725562489182657\ldots.
\]

Finding 3 then supplies the exact finite-product statement.

### Judgment

**Accepted with high confidence.**

The BSSC specialization relies on the sharp posterior support established in the supplied earlier transaction. That support is independently substantiated there by the curvature calculation, the tangent at \(q=1/5\), and an equality-achieving posterior mixture. The orientation change from \(g=I_Z-I_Y\) to \(t=I_Y-I_Z\) is handled correctly by reflection.

---

## Finding 5 — Interpretation as a converse and effect on the capacity frontier

**Claim key:** `half-skew-bssc-uv-relaxed-converse-does-not-improve-frontier`

### Proposition assessed

The value
\[
2h_2(1/4)-\frac54
\]
is a valid branchwise-relaxed UV sum-rate converse, but it does not improve the governed BSSC capacity interval.

### Reasoning

For a UV auxiliary \(U-X-(Y,Z)\),
\[
\begin{aligned}
I(U;Y)+I(X;Z\mid U)
&=I_Y(p)+\sum_u p(u)\bigl(I_Z(p_u)-I_Y(p_u)\bigr)\\
&\le I_Y(p)+\mathfrak C[-t](p)
=A_W(p).
\end{aligned}
\]
The receiver-swapped UV sum row is analogously bounded by \(D_W(p)\). Since any rate pair satisfying both UV rows obeys
\[
R_1+R_2\le\min\{A_W(p),D_W(p)\},
\]
maximization over \(p\) gives the stated branchwise scalar as a valid outer bound.

However,
\[
0.3725562489182657\ldots
>
0.369316568803963,
\]
and also exceeds the supplied fixed-pair continuous Theorem 9 certificate
\[
0.369296945969202842443.
\]
Therefore the UV result is strictly weaker than both the published benchmark upper endpoint and the stronger supplied certificate. It changes neither the lower nor the upper capacity frontier.

### Judgment

**Accepted.**

The transaction correctly avoids presenting the UV value as an achievable rate or as a new best capacity upper bound.

---

## Contradictions and consistency checks

### No mathematical contradiction among the subject’s principal claims

The apparent tension between “branchwise minimum” and “averaged scalar” is resolved by receiver-skew symmetrization. In general,
\[
\min\{A,D\}\le\frac{A+D}{2},
\]
but on a skew-symmetric channel the symmetrized prior makes both branches at least the original average, producing equality of the optimized values. There is therefore no contradiction.

### No conflict with the stronger Theorem 9 certificate

The UV value is larger than the supplied full-Theorem-9 upper bound. This means only that the UV relaxation is weaker; it does not invalidate either result.

### Provenance statements are not mathematical evidence by themselves

The transaction repeatedly records earlier “accepted” Yukon judgments and immutable source hashes. Those facts may establish attribution and file identity, but they do not substitute for proof. In this case the main theorems are nevertheless supported by the displayed analytic arguments, so the mathematical judgment does not depend on the prior acceptance labels.

### Truncated source artifact

The supplied copy of the original averaged-functional `FULL.md` is truncated by the evidence limit. This would be a concern if the claim depended only on that file. It does not: the subject README contains the decisive chain-rule identity, envelope inequalities, upper-bound argument, and product-decomposition reverse argument. The branchwise source is also supplied in full. Thus the truncation does not create a material proof gap.

---

## Credit and priority assessment

The subject describes itself as an attributed port of two earlier accepted artifacts. The mathematical authorship is attributed to Robert Raynor, and the port expressly disclaims new authorship of the original results. That attribution is consistent across the supplied provenance records.

The theorem chain has two distinct contributions:

1. exact product additivity of the averaged separately relaxed UV scalar; and
2. the symmetry argument identifying the branchwise and averaged scalars, thereby transferring additivity to the branchwise functional.

The exact BSSC numerical specialization additionally uses the sharp posterior-support calculation supplied in the earlier dependence-balance/entropy-no-go transaction. That supporting calculation should be distinguished from the new tensorization and symmetry arguments.

No cumulative project credit is assigned here.

---

## Final disposition

**Accepted as a correct structural contribution.**

The strongest warranted conclusions are:

\[
\boxed{
B_{\rm avg}(W_1\times W_2)
=
B_{\rm avg}(W_1)+B_{\rm avg}(W_2)
}
\]
for arbitrary finite-alphabet broadcast channels;

\[
\boxed{
B_{\rm br}(W)=B_{\rm avg}(W)
}
\]
for receiver-skew-symmetric channels; and

\[
\boxed{
B_{\rm br}(P^{\times n})
=
B_{\rm avg}(P^{\times n})
=
n\left(2h_2(1/4)-\frac54\right)
}
\]
for every finite \(n\) for the half-skew BSSC.

These results rigorously close the specified multiletter route through the separately relaxed UV scalars. They do not determine \(C_{\rm sum}\), improve its current benchmark interval, or establish tensorization of stronger converse regions.
