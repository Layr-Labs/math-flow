# Exact product additivity of the symmetric UV sum-rate functional

## Contribution and exact scope

This submission proves an analytic tensorization theorem for a standard scalar
consequence of the classical UV outer bound.  For every pair of finite-alphabet
discrete memoryless broadcast channels (DMBCs), the symmetric sum-rate
functional

\[
 B_{\rm UV}(W)=\max_{p_X}\frac12\bigl(
 I(X;Y)+I(X;Z)+\mathfrak C[t_W](p_X)
                 +\mathfrak C[-t_W](p_X)\bigr),
 \qquad
 t_W(p_X)=I(X;Y)-I(X;Z),                                      \tag{1}
\]

is exactly additive:

\[
 B_{\rm UV}(W_1\times W_2)=B_{\rm UV}(W_1)+B_{\rm UV}(W_2).   \tag{2}
\]

Here \(\mathfrak C\) is the upper concave envelope over the input
simplex, all mutual informations are evaluated using the displayed input
law and the relevant channel, and the maximum is over all input laws.  The
inputs of the two factors may be arbitrarily correlated when the left side of
(2) is optimized.  The two factor channels need not be identical, symmetric,
binary-input, or BSSCs.  No assumption is made about the correlation of
\(Y_i\) and \(Z_i\) within one factor.

The functional in (1) is the equally weighted, or symmetric, scalar UV
sum-rate relaxation (the quantity often written in the upper-concave-envelope
form used for the BSSC).  The theorem is deliberately **not** a claim that the
whole UV outer region, or every scalarization of it, is additive.

For the half-skew BSSC \(P\), (2) implies for every \(n\geq 1\)

\[
 \frac1n B_{\rm UV}(P^{\times n})=B_{\rm UV}(P).               \tag{3}
\]

Thus grouping channel uses, allowing each envelope auxiliary to depend jointly
on all coordinates of the super-symbol, and allowing arbitrary correlated
super-symbol inputs cannot improve this particular per-letter BSSC converse.

## Definitions and why (1) is an outer bound

For a continuous real function \(f\) on the finite input simplex, use the
following operational definition of its upper concave envelope:

\[
 \mathfrak C[f](p)
 =\sup_{\substack{A-X-(Y,Z)\\P_X=p}}
       \sum_a P_A(a) f(P_{X|A=a}).                             \tag{4}
\]

Equivalently, the supremum is over all finite convex decompositions
\(p=\sum_a\alpha_a p_a\).  Standard finite-dimensional support reduction
makes the supremum a maximum, but the proof below only needs the supremum
form.  Formula (4) also makes clear that \(\mathfrak C[f]\) is concave and
majorizes \(f\).

For completeness, the private-message UV outer bound implies, under one
induced input law \(p_X\), both relaxed sum-rate inequalities

\[
 \begin{aligned}
 R_1+R_2&\leq I(U;Y)+I(X;Z|U),\\
 R_1+R_2&\leq I(V;Z)+I(X;Y|V),
 \end{aligned}                                                \tag{5}
\]

with \(U-X-(Y,Z)\) and \(V-X-(Y,Z)\).  Put
\(t(p)=I_p(X;Y)-I_p(X;Z)\).  For any such \(U\), the Markov chain and the
chain rule give

\[
 \begin{aligned}
 I(U;Y)+I(X;Z|U)
 &= I_p(X;Z)+I(U;Y)-I(U;Z)\\
 &= I_p(X;Y)-\sum_u P(u)t(P_{X|u})\\
 &\leq I_p(X;Y)+\mathfrak C[-t](p).                            \tag{6}
 \end{aligned}
\]

Likewise,

\[
 I(V;Z)+I(X;Y|V)
 =I_p(X;Z)+\sum_v P(v)t(P_{X|v})
 \leq I_p(X;Z)+\mathfrak C[t](p).                             \tag{7}
\]

Both right sides bound the same achievable sum rate.  Their arithmetic mean
does too, and maximizing that mean over \(p\) is exactly (1).  This paragraph
only records the standard validity of the scalar functional; the new program
contribution is its exact product factorization.

## The factorization lemma

Let

\[
 W_1(y_1,z_1|x_1)W_2(y_2,z_2|x_2)                            \tag{8}
\]

be a product DMBC.  Write \(t_i(p_i)=I(X_i;Y_i)-I(X_i;Z_i)\),
and define \(t_{12}\) in the same way for input \((X_1,X_2)\) and outputs
\((Y_1,Y_2)\), \((Z_1,Z_2)\).  If \(p_{12}\) is any, possibly correlated,
input law and \(p_1,p_2\) are its marginals, then

\[
 \begin{aligned}
 \mathfrak C[t_{12}](p_{12})
   &\leq \mathfrak C[t_1](p_1)+\mathfrak C[t_2](p_2),\\
 \mathfrak C[-t_{12}](p_{12})
   &\leq \mathfrak C[-t_1](p_1)+\mathfrak C[-t_2](p_2).       \tag{9}
 \end{aligned}
\]

The first inequality is the \(\lambda=1\) case of the usual
chain-rule factorization for the concave envelope of
\(I(X;Y)-\lambda I(X;Z)\).  The full cancellation at \(\lambda=1\) is
proved next rather than assumed.

### Exact chain-rule identity for correlated inputs

Fix an arbitrary finite \(A\) such that

\[
 A-(X_1,X_2)-(Y_1,Z_1,Y_2,Z_2)                               \tag{10}
\]

under (8), with marginal input law \(p_{12}\).  Conditional on \(A=a\),
the input coordinates may still be correlated.  Chain the two receiver-1
outputs in forward factor order, and the two receiver-2 outputs in reverse
factor order.  Product memorylessness gives

\[
 \begin{aligned}
 I(X_1X_2;Y_1Y_2|A)
   &=I(X_1;Y_1|A)+I(X_2;Y_2|A,Y_1),\\
 I(X_1X_2;Z_1Z_2|A)
   &=I(X_2;Z_2|A)+I(X_1;Z_1|A,Z_2).                           \tag{11}
 \end{aligned}
\]

For example, the first line uses
\(I(X_2;Y_1|X_1,A)=0\) and
\(I(X_1;Y_2|X_2,A,Y_1)=0\).  These conditional independences follow from
the factorization in (8), not from independence of \(X_1\) and \(X_2\).

The only apparent mismatch in (11) is resolved by two explicit
co-information identities.  The elementary identity

\[
 I(B;C|D)-I(B;C|D,E)
 =I(C;E|D)-I(C;E|B,D)                                        \tag{12}
\]

gives

\[
 \begin{aligned}
 &I(X_1;Y_1|A)-I(X_1;Y_1|A,Z_2)\\
 &\qquad=I(Y_1;Z_2|A)-I(Y_1;Z_2|X_1,A)
          =I(Y_1;Z_2|A),                                     \tag{13}\\
 &I(X_2;Z_2|A)-I(X_2;Z_2|A,Y_1)\\
 &\qquad=I(Z_2;Y_1|A)-I(Z_2;Y_1|X_2,A)
          =I(Y_1;Z_2|A).                                     \tag{14}
 \end{aligned}
\]

The last terms vanish because the two channel factors are independent:
\(Y_1\perp Z_2\mid(X_1,A)\) and
\(Z_2\perp Y_1\mid(X_2,A)\).  Again, those statements remain true for an
arbitrary correlated law of \((A,X_1,X_2)\): after fixing \(X_1\), the law
of \(Y_1\) no longer depends on \((A,X_2,Z_2)\), and symmetrically after
fixing \(X_2\).

Equations (13) and (14) have identical right sides.  Substitution into (11)
therefore proves the exact \(\lambda=1\) identity

\[
 \begin{aligned}
 &I(X_1X_2;Y_1Y_2|A)-I(X_1X_2;Z_1Z_2|A)\\
 &=\bigl[I(X_1;Y_1|A,Z_2)-I(X_1;Z_1|A,Z_2)\bigr]\\
 &\quad+\bigl[I(X_2;Y_2|A,Y_1)-I(X_2;Z_2|A,Y_1)\bigr].        \tag{15}
 \end{aligned}
\]

To locate precisely why \(\lambda=1\) matters, repeat the same algebra with
the receiver-2 terms multiplied by \(\lambda\).  It yields

\[
 \begin{aligned}
 &I(X_1X_2;Y_1Y_2|A)-\lambda I(X_1X_2;Z_1Z_2|A)\\
 &=\bigl[I(X_1;Y_1|A,Z_2)-\lambda I(X_1;Z_1|A,Z_2)\bigr]\\
 &\quad+\bigl[I(X_2;Y_2|A,Y_1)-\lambda I(X_2;Z_2|A,Y_1)\bigr]\\
 &\quad-(\lambda-1)I(Y_1;Z_2|A).                              \tag{16}
 \end{aligned}
\]

For \(\lambda\geq1\) the last term is nonpositive; at \(\lambda=1\) it
vanishes exactly.  Thus (15), including its cross-term cancellation, is valid
without any independence assumption on the input coordinates.

### Passage from the identity to the envelopes

The left side of (15) is

\[
 \sum_a P(a)t_{12}(P_{X_1X_2|a}).                             \tag{17}
\]

Moreover,

\[
 (A,Z_2)-X_1-(Y_1,Z_1),\qquad
 (A,Y_1)-X_2-(Y_2,Z_2),                                      \tag{18}
\]

again by (8).  Consequently the first bracket in (15) equals
\(\sum_{a,z_2}P(a,z_2)t_1(P_{X_1|a,z_2})\).  For each fixed
\(z_2\), definition (4), followed by concavity of the envelope, gives

\[
 \begin{aligned}
 \sum_{a,z_2}P(a,z_2)t_1(P_{X_1|a,z_2})
 &\leq \sum_{z_2}P(z_2)\mathfrak C[t_1](P_{X_1|z_2})\\
 &\leq \mathfrak C[t_1]\!\left(
       \sum_{z_2}P(z_2)P_{X_1|z_2}\right)\\
 &=\mathfrak C[t_1](p_1).                                    \tag{19}
 \end{aligned}
\]

The identical argument, first conditioning on \(Y_1\), bounds the second
bracket by \(\mathfrak C[t_2](p_2)\).  Hence every auxiliary \(A\) in (4)
satisfies

\[
 \sum_aP(a)t_{12}(P_{X_1X_2|a})
 \leq\mathfrak C[t_1](p_1)+\mathfrak C[t_2](p_2).             \tag{20}
\]

Taking the supremum over \(A\) proves the first line of (9).  Swapping
\(Y_i\) and \(Z_i\) in the entire argument changes every \(t_i\) to
\(-t_i\) and proves the second line.  This completes the factorization
lemma.

## Proof of exact additivity

For an arbitrary correlated product-channel input \(p_{12}\), product
memorylessness and entropy subadditivity imply

\[
 \begin{aligned}
 I(X_1X_2;Y_1Y_2)
 &=H(Y_1Y_2)-H(Y_1Y_2|X_1X_2)\\
 &\leq H(Y_1)+H(Y_2)-H(Y_1|X_1)-H(Y_2|X_2)\\
 &=I(X_1;Y_1)+I(X_2;Y_2),                                    \tag{21}
 \end{aligned}
\]

and likewise
\(I(X_1X_2;Z_1Z_2)\leq I(X_1;Z_1)+I(X_2;Z_2)\).
Combining these inequalities with (9) in (1) gives the pointwise bound

\[
 F_{12}(p_{12})\leq F_1(p_1)+F_2(p_2),                       \tag{22}
\]

where \(F\) denotes the expression inside the maximization in (1).  Therefore

\[
 B_{\rm UV}(W_1\times W_2)
 \leq B_{\rm UV}(W_1)+B_{\rm UV}(W_2).                       \tag{23}
\]

For the reverse direction, take any factor priors \(p_1,p_2\) and their
product \(p_1\times p_2\).  If
\(p_1=\sum_a\alpha_a p_{1a}\) and
\(p_2=\sum_b\beta_b p_{2b}\), then

\[
 p_1\times p_2=\sum_{a,b}\alpha_a\beta_b
                       (p_{1a}\times p_{2b}),                 \tag{24}
\]

and product inputs make mutual information additive, so

\[
 t_{12}(p_{1a}\times p_{2b})=t_1(p_{1a})+t_2(p_{2b}).         \tag{25}
\]

Using product decompositions in (4) and taking suprema shows

\[
 \mathfrak C[t_{12}](p_1\times p_2)
 \geq\mathfrak C[t_1](p_1)+\mathfrak C[t_2](p_2).             \tag{26}
\]

The same holds for \(-t\).  Inequality (9) makes both relations equalities
at product priors.  The two un-enveloped mutual informations are also
additive there, and hence

\[
 F_{12}(p_1\times p_2)=F_1(p_1)+F_2(p_2).                    \tag{27}
\]

Taking maximizing priors (or maximizing sequences) gives the reverse of
(23), proving (2).

## Blocking consequence and the BSSC

Induction in (2) gives, for arbitrary finite-alphabet factors,

\[
 B_{\rm UV}\!\left(\mathop{\times}_{i=1}^n W_i\right)
 =\sum_{i=1}^n B_{\rm UV}(W_i).                               \tag{28}
\]

For one fixed DMBC \(W\), a length-\(m\) code for the super-symbol channel
\(W^{\times n}\) is exactly a length-\(mn\) code for \(W\), with rates per
super-symbol scaled by \(n\).  Conversely, ordinary codes can be padded to
blocklengths divisible by fixed \(n\) with asymptotically negligible rate
loss.  Thus the private-message capacity regions, with their respective
per-use units, satisfy

\[
 \mathcal C(W^{\times n})=n\mathcal C(W),\qquad
 C_{\rm sum}(W^{\times n})=nC_{\rm sum}(W).                   \tag{29}
\]

Applying (1) to the super-symbol channel and dividing by \(n\) consequently
returns exactly the one-letter functional:

\[
 C_{\rm sum}(W)
 =\frac1nC_{\rm sum}(W^{\times n})
 \leq\frac1nB_{\rm UV}(W^{\times n})
 =B_{\rm UV}(W).                                              \tag{30}
\]

In particular this applies to the half-skew BSSC with receiver marginals

\[
 W_Y=\begin{pmatrix}1/2&1/2\\0&1\end{pmatrix},\qquad
 W_Z=\begin{pmatrix}1&0\\1/2&1/2\end{pmatrix}.               \tag{31}
\]

The earlier attempt's sampled one-letter evaluation was approximately
\(0.3725562489182657\) bits/use, and its enriched two-letter sampled value was
approximately \(0.7451124978365314\) bits/super-symbol.  Those decimals are
useful numerical checks of (2), not ingredients in the proof and not claimed
here as interval-certified evaluations.  The rigorous BSSC conclusion is the
symbolic equality (3), which does not depend on either decimal.

## Executable corroboration

The accompanying `verify_uv_factorization.py` is a small dependency-free
audit of the fragile algebraic steps.  On deterministic pseudorandom finite
product channels and arbitrary correlated laws \(P_{A,X_1,X_2}\), it checks:

1. both product-channel conditional independences used in (13)--(14);
2. the exact \(\lambda=1\) equality (15) and the residual formula (16) for
   several \(\lambda\)'s;
3. the mutual-information subadditivity inequalities in (21);
4. the product-mixture identities (24)--(25); and
5. the BSSC candidate-contact mixture numerical witness reported above.

It is run with

```text
python3 submission/verify_uv_factorization.py
```

and fails by assertion if a check exceeds its stated floating-point tolerance.
This code is corroboration only.  The exact theorem rests on the displayed
finite-alphabet identities, not on randomized testing or a discretized
optimization.

## Separation from the two-letter GK search

Attempt 007 also performed a floating-point, grid-restricted search of the
simplified two-auxiliary GK equation-(16) functional.  With product
auxiliaries it found about \(0.7385943932915563\) per two-letter super-symbol;
the best joint-auxiliary sample found about \(0.7385943932915559\).  That
difference is at roundoff scale.  These values provide **no theorem**:

- sampled upper concave envelopes and a sampled input maximization are not a
  continuous global certificate;
- the search has no proved auxiliary-cardinality bound or global optimality
  guarantee;
- the search evaluated only the simplified equation-(16) objective, not the
  full Theorem-9 product-channel constraint system; and
- the nested GK envelopes do not obey the factorization argument above.

Accordingly, this submission makes no claim of GK additivity, no claim that
two-letter GK cannot improve, and no claim about additivity of the full
two-auxiliary-receiver region.  The existing input-only marginalization result
for auxiliary receivers does not fill the missing global-optimization or
factorization steps.  Those remain open.

## Novelty, effect, and limitations

The chain-rule method behind (16) is classical; no claim of priority for that
general technique is made.  The useful new item relative to the current BSSC
knowledge record is a complete, directly checkable theorem for the exact
functional actually used in the BSSC UV comparison, including arbitrary
correlated product inputs, the previously implicit \(\lambda=1\) cancellation,
and the all-blocklength blocking consequence.  It closes the UV product-channel
route as a source of a stronger per-letter BSSC bound.

The result does not improve the numerical BSSC capacity upper bound.  It does
not prove a capacity formula, an achievable rate, a full-region tensorization,
additivity of the branchwise minimum of separately relaxed UV constraints, or
any GK/J/full-Theorem-9 tensorization.  Potential multiletter improvements must
therefore retain structure absent from the symmetric functional (1), such as
the coupling between different UV branches or the richer nested auxiliary
constraints.
