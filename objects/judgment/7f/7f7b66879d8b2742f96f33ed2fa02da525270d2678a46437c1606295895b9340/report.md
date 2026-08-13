# Mathematical judgment for transaction `c70e1829a7c6a2a8cb8cfc2383f8abf825ac5ea6`

## Overall assessment

The transaction is mathematically sound within its explicitly limited scope. It establishes two related structural results:

1. an exact finite-block dependence-balance identity, together with a fixed-map selected-coordinate factorization and four compatible rate inequalities for private-message broadcast codes; and
2. an explicit finite entropic counterfeit showing that a specified coarse entropy relaxation cannot be strengthened below the classical UV value by universal information inequalities or any finite sequence of standard copy-lemma extensions.

Neither result determines the BSSC sum-capacity or improves the numerical capacity frontier. The value

\[
2h_2(1/4)-\frac54
=0.3725562489182657\ldots
\]

is the objective value of a deliberately over-relaxed entropy formulation, not a lower or upper bound on the actual BSSC capacity. It therefore does not contradict the substantially smaller fixed-pair capacity upper bound supplied elsewhere in the evidence.

The central proofs are self-contained and do not depend on numerical optimization. The included exact checker provides credible corroboration for the entropic witness, while the finite-block code theorem is established analytically by chain rules, Fano’s inequality, memorylessness, and a conditioned Csiszár sum identity.

---

## Finding 1 — Exact finite-block dependence-balance telescope

**Claim key:** `finite-block-private-message-dependence-balance-telescope`

### Proposition assessed

For independent private messages \(A,B\), a deterministic length-\(n\) encoder, and

\[
S_i=(Y^{i-1},Z_{i+1}^n),
\]

the transaction claims

\[
\sum_{i=1}^n
\left[
I(A;B\mid S_i,Y_i)-I(A;B\mid S_i,Z_i)
\right]
=
I(A;B\mid Y^n)-I(A;B\mid Z^n).
\]

It further claims the finite-block bound

\[
\left|
\frac1n\sum_{i=1}^n
\left[
I(A;B\mid S_i,Y_i)-I(A;B\mid S_i,Z_i)
\right]
\right|
\le \max\{\delta_1,\delta_2\},
\]

where \(\delta_j=F_j/n\) and \(F_j\) is the usual Fano quantity.

### Decisive reasoning

Define

\[
D_i=I(A;B\mid Y^i,Z_{i+1}^n),\qquad 0\le i\le n.
\]

Then

\[
(S_i,Y_i)=(Y^i,Z_{i+1}^n)
\]

and

\[
(S_i,Z_i)=(Y^{i-1},Z_i^n).
\]

Consequently the \(i\)-th summand is exactly \(D_i-D_{i-1}\). Summing gives

\[
D_n-D_0
=
I(A;B\mid Y^n)-I(A;B\mid Z^n).
\]

This is an exact identity and uses no inequality or channel property.

The endpoint estimates are also correct:

\[
0\le D_n\le H(A\mid Y^n)\le F_1,
\]

and

\[
0\le D_0\le H(B\mid Z^n)\le F_2.
\]

Since \(D_n\in[0,F_1]\) and \(D_0\in[0,F_2]\),

\[
|D_n-D_0|\le \max\{F_1,F_2\}.
\]

Thus the use of a maximum, rather than the weaker sum \(F_1+F_2\), is justified.

With a uniform independent time \(T\) and the selected-coordinate definitions

\[
U=A,\quad V=B,\quad W=S_T,\quad Y=Y_T,\quad Z=Z_T,
\]

conditioning on \(T=t\) averages the finite-block summands exactly. Therefore

\[
\left|
I(U;V\mid W,T,Y)-I(U;V\mid W,T,Z)
\right|
\le \max\{\delta_1,\delta_2\}.
\]

For reliable bounded-rate code sequences, \(\delta_j\to0\), since

\[
\frac{h_2(p_j)}n\to0,\qquad
\frac{p_j\log(N_j-1)}n\le p_jR_j\to0.
\]

### Judgment

**Accepted with high confidence.** The telescope and Fano estimate are complete and correctly scoped.

The transaction also correctly warns that this is a sequence-level condition. Because the alphabets of \(U,V,W\) can grow with blocklength, the vanishing scalar defect does not by itself imply a compact fixed-alphabet single-letter outer region.

---

## Finding 2 — Fixed-map selected-coordinate factorization and four rate rows

**Claim key:** `selected-coordinate-fixed-map-factorization-and-rate-inequalities`

### Proposition assessed

The transaction claims that every deterministic code induces the factorization

\[
p(t,u,v,w,x,y,z)
=
\frac1n p_U(u)p_V(v)p(w\mid u,v,t)
\mathbf 1\{x=f_t(u,v)\}P_{YZ\mid X}(y,z\mid x),
\]

and hence retains the stronger fixed-map property

\[
X=f_T(U,V),
\]

rather than merely allowing \(X\) to be a function of \(U,V,W,T\).

It also claims the four inequalities

\[
R_1\le I(U,W;Y\mid T)+\delta_1,
\]

\[
R_2\le I(V,W;Z\mid T)+\delta_2,
\]

\[
R_1+R_2
\le I(U,W;Y\mid T)+I(X;Z\mid U,W,T)+\delta_1+\delta_2,
\]

and

\[
R_1+R_2
\le I(V,W;Z\mid T)+I(X;Y\mid V,W,T)+\delta_1+\delta_2.
\]

### Fixed-map factorization

Conditional on \(U=u,V=v,T=t\), the entire transmitted word is fixed by the deterministic encoder, and in particular

\[
X_t=f_t(u,v).
\]

The variable \(W=(Y^{t-1},Z_{t+1}^n)\) depends only on outputs at coordinates other than \(t\). Memorylessness therefore makes the current output pair independent of \(W\), given the current input. This proves the displayed factorization.

The distinction emphasized by the transaction is mathematically important:

\[
H(X\mid U,V,T)=0
\]

forces one encoder map \(f_t\) for each time \(t\), independent of the realized \(W\). In contrast,

\[
H(X\mid U,V,W,T)=0
\]

alone would permit the state \(W\) to select among different encoder maps. The latter is a strictly weaker relaxation.

### Individual-rate rows

For the first receiver, Fano and the forward chain rule give

\[
nR_1
\le
\sum_i I(A;Y_i\mid Y^{i-1})+F_1.
\]

Adjoining \(S_i\) to the first argument cannot decrease mutual information:

\[
I(A;Y_i\mid Y^{i-1})
\le I(A,S_i;Y_i).
\]

Time sharing yields the first row. The receiver-\(Z\) row follows by the reverse chain rule.

### Sum-rate rows

The first branch begins with

\[
n(R_1+R_2)
\le I(A;Y^n)+I(B;Z^n\mid A)+F_1+F_2.
\]

Because \(X^n\) is a deterministic function of \((A,B)\) and the channel output is conditionally independent of \(B\) given \((A,X^n)\),

\[
I(B;Z^n\mid A)=I(X^n;Z^n\mid A).
\]

The conditioned Csiszár identity

\[
\sum_i I(Z_{i+1}^n;Y_i\mid A,Y^{i-1})
=
\sum_i I(Y^{i-1};Z_i\mid A,Z_{i+1}^n)
\]

then produces the claimed selected-coordinate terms. The uncancelled remainder is

\[
\sum_i I(Y^{i-1};Y_i)\ge0,
\]

which is discarded in the correct direction. The second sum branch follows symmetrically and leaves

\[
\sum_i I(Z_{i+1}^n;Z_i)\ge0.
\]

No unproved sign assumption is used.

### Judgment

**Accepted with high confidence.** The factorization and all four rate rows are justified. The proof correctly retains the distinguished role of \(T\) and the \(W\)-independent encoder map.

The absence of a simultaneous cardinality or compactness reduction is a decisive limitation, not a defect in the theorem. Without such a reduction, optimizing over arbitrarily chosen small alphabets would not certify a universal capacity converse.

---

## Finding 3 — Exact BSSC support inequality used in the entropy relaxation

**Claim key:** `uniform-bssc-posterior-difference-support-at-r`

### Proposition assessed

With

\[
h=h_2(1/4),\qquad r=h-\frac34,
\]

and

\[
g(q)=I_Z(q)-I_Y(q),
\]

the transaction claims the global affine support

\[
g(q)\le 2r(1-q),\qquad 0\le q\le1,
\]

which implies, at fair input,

\[
I(X;Z\mid A)-I(X;Y\mid A)\le r
\]

for every auxiliary \(A-X-(Y,Z)\). The reflected inequality has the same right side.

### Decisive reasoning

The supplied derivative calculation is correct:

\[
g''(q)
=
\frac{2q-1}
{\ln(2)\,q(1-q)(1+q)(2-q)}.
\]

Thus \(g\) is concave on \([0,1/2]\) and convex on \([1/2,1]\). The exact contact identities

\[
g(1/5)=\frac85r,\qquad g'(1/5)=-2r
\]

show that the tangent at \(q=1/5\) is

\[
2r(1-q).
\]

Concavity places \(g\) below this tangent on the left half. On the right half, convexity together with \(g(1/2)=g(1)=0\) gives \(g(q)\le0\), while \(2r(1-q)\ge0\). Hence the support is global.

For posterior probabilities \(q_A=P(X=1\mid A)\) with \(\mathbb E q_A=1/2\),

\[
I(X;Z\mid A)-I(X;Y\mid A)
=
\mathbb E g(q_A)
\le 2r\,\mathbb E(1-q_A)
=r.
\]

The posterior mixture placing mass \(5/8\) at \(1/5\) and \(3/8\) at \(1\) has mean \(1/2\) and attains equality, so the constant is sharp for this scalar direction.

### Judgment

**Accepted with high confidence.** This analytic component is complete and independent of numerical gridding.

---

## Finding 4 — Explicit finite entropic counterfeit at the classical UV value

**Claim key:** `coarse-bssc-entropy-relaxation-entropic-counterfeit`

### Proposition assessed

The transaction claims an actual finite distribution satisfying the stated coarse entropy relaxation and achieving

\[
B_1=B_2=2h_2(1/4)-\frac54.
\]

### Witness audit

Let

\[
s=1-h,\qquad r=h-\frac34,\qquad t=2r.
\]

The independent binary components have entropies

\[
t,\quad s,\quad r,\quad s-r,\quad \frac12-r,\quad r,\quad \frac12,\quad \frac12.
\]

The expressions appearing in different parts of the evidence are consistent:

\[
\frac12-r=\frac54-h.
\]

The bracket

\[
\frac34<h<\frac78
\]

makes every component entropy strictly between \(0\) and \(1\), and every such entropy is realized by a Bernoulli random variable.

The tuple variables are

\[
U=(C,A,B2c,Eu),\qquad V=(B1c,Ev),
\]

\[
X=(C,A,B1c,B2c,Eu,Ev),
\]

\[
Y=(C,A,Ny),\qquad Z=(C,B1c,B2c,Nz),
\]

with \(W,T\) constant.

Because these are projections of independent components, entropy calculations reduce to exact sums over component sets. The claimed base entropy vector follows:

\[
H(X)=1,\qquad H(Y)=H(Z)=h,
\]

\[
H(X,Y)=H(X,Z)=H(Y,Z)=\frac32,
\qquad H(X,Y,Z)=2.
\]

The structural conditions also hold:

- \(U\) and \(V\) use disjoint independent components;
- \(U,V\) together determine \(X\);
- \(W,T\) are constant;
- conditional on \(X\), only the independent noises \(Ny,Nz\) remain in the outputs.

The joint output reveals exactly half the entropy of each of \(U\) and \(V\). Since \(U,V\) are independent and \(W,T\) are constant, this establishes all the stated disjoint-subtuple BEC identities. The count \(65\) is correct: each of four labels can lie in \(L\), \(K\), or neither, giving \(3^4\) assignments, and the \(2^4\) assignments with empty \(L\) are excluded.

The key objective quantities are also correct:

\[
I(U;Y)=c,\qquad I(X;Z\mid U)=r,
\]

\[
I(V;Z)=r,\qquad I(X;Y\mid V)=c.
\]

Therefore

\[
B_1=B_2=c+r
=2h-\frac54.
\]

The two support rows are attained at equality.

### Executable evidence

The included checker uses exact rational coefficients in the formal parameter \(h\), not floating-point approximations. Its model of conditional mutual information as the weight of component intersections outside the conditioning set is correct for tuple projections of mutually independent components.

The checker does not prove the finite-block dependence telescope, but that theorem already has a complete analytic proof. Conversely, the checker gives a strong independent audit of the more elaborate component bookkeeping in the counterfeit.

### Judgment

**Accepted with high confidence.** The witness is an actual finite distribution, not merely an abstract polymatroid or sampled entropy vector.

---

## Finding 5 — Universal-information-inequality and finite-copy obstruction

**Claim key:** `universal-information-inequality-and-finite-copy-no-go-for-specified-relaxation`

### Proposition assessed

The transaction claims that the specified entropy relaxation cannot be forced below

\[
2h_2(1/4)-\frac54
\]

by adding any universally valid finite-variable information inequalities or any finite sequence of standard copy-lemma extensions.

### Decisive reasoning

The counterfeit is an actual finite joint distribution. It therefore satisfies every information inequality valid for all finite random variables, including unknown non-Shannon inequalities.

For a standard copy-lemma step, the required copied variables can be realized by conditionally resampling from the
