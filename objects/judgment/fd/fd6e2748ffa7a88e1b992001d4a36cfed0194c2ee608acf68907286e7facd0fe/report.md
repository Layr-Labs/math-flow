## `bssc-sum-capacity/code-induced-dependence-balance-and-entropy-no-go`

**Verdict: VALID**

**Required dependencies:** None. The necessary arguments are supplied within the subject evidence. The retained Yukon artifacts and acceptance records are provenance only and are not mathematical premises.

**Objective attestations:** None were supplied. The checker and its claimed output are therefore not treated as trusted execution evidence; the verdict rests on the analytic argument and direct inspection of the witness construction.

### 1. Finite-block dependence balance

Let  
\[
D_i=I(A;B\mid Y^i,Z_{i+1}^n),\qquad 0\le i\le n.
\]
Since
\[
(S_i,Y_i)=(Y^i,Z_{i+1}^n),\qquad
(S_i,Z_i)=(Y^{i-1},Z_i^n),
\]
the \(i\)-th summand is exactly \(D_i-D_{i-1}\). Hence
\[
\sum_i\bigl[I(A;B\mid S_i,Y_i)-I(A;B\mid S_i,Z_i)\bigr]
=D_n-D_0.
\]
No channel inequality is used here.

The endpoint bounds are applicable:
\[
D_n\le H(A\mid Y^n)\le F_1,\qquad
D_0\le H(B\mid Z^n)\le F_2.
\]
Thus, because both endpoints are nonnegative,
\[
|D_n-D_0|\le \max\{F_1,F_2\}.
\]
Uniform independent time sampling therefore gives
\[
\left|I(U;V\mid W,T,Y)-I(U;V\mid W,T,Z)\right|
\le \max\{\delta_1,\delta_2\}.
\]

The detailed source explicitly assumes \(N_1,N_2\ge2\), which is the natural domain on which \(\log_2(N_j-1)\) is defined. Singleton message sets would require a separate harmless convention but are not part of the literal displayed Fano formula.

### 2. Induced-law factorization and fixed encoder map

For fixed \(A=u,B=v,T=t\), the deterministic encoder fixes
\[
X=X_t=f_t(u,v).
\]
The variable \(W=(Y^{t-1},Z_{t+1}^n)\) only contains outputs at coordinates other than \(t\). Memorylessness makes \((Y_t,Z_t)\) conditionally independent of \(W\) given the fixed current input. Consequently,
\[
p(t,u,v,w,x,y,z)
=\frac1n p_U(u)p_V(v)p(w\mid u,v,t)
\mathbf1\{x=f_t(u,v)\}P_{YZ\mid X}(y,z\mid x)
\]
is correct.

It follows in particular that \(U\perp V\), \(T\perp(U,V)\), \(H(X\mid U,V,T)=0\), and \(W\) cannot select a different encoder map after \((u,v,t)\) is fixed. This is stronger than merely requiring \(H(X\mid U,V,W,T)=0\).

### 3. Four rate rows

The individual rows follow from Fano, the forward or reverse chain rule, and enlargement of the first mutual-information argument:
\[
R_1\le I(U,W;Y\mid T)+\delta_1,\qquad
R_2\le I(V,W;Z\mid T)+\delta_2.
\]

For the first sum row, independence and Fano give
\[
n(R_1+R_2)
\le I(A;Y^n)+I(B;Z^n\mid A)+F_1+F_2.
\]
Deterministic encoding and the conditional Markov relation imply
\[
I(B;Z^n\mid A)=I(X^n;Z^n\mid A).
\]
The supplied conditional Csiszár identity is correct:
\[
\sum_i I(Z_{i+1}^n;Y_i\mid A,Y^{i-1})
=\sum_i I(Y^{i-1};Z_i\mid A,Z_{i+1}^n).
\]
Direct expansion leaves the nonnegative remainder
\[
\sum_i I(Y^{i-1};Y_i),
\]
so
\[
R_1+R_2
\le I(U,W;Y\mid T)+I(X;Z\mid U,W,T)+\delta_1+\delta_2.
\]
The receiver-swapped calculation similarly leaves
\[
\sum_i I(Z_{i+1}^n;Z_i)\ge0
\]
and proves the fourth row. No unproved sign assumption or degradedness property is used.

The stated limitation is also correct: \(U,V,W\) have blocklength-dependent alphabets, so these facts alone do not provide a compact fixed-cardinality single-letter outer region.

### 4. Scalar BSSC support inequalities

For the common-noise coupling and posterior \(q=P(X=1)\),
\[
I_Y(q)=h_2((1-q)/2)-(1-q),\qquad
I_Z(q)=h_2(q/2)-q.
\]
For \(g=I_Z-I_Y\), differentiation gives
\[
g''(q)=
\frac{2q-1}{\ln(2)\,q(1-q)(1+q)(2-q)}.
\]
Thus \(g\) is concave on \([0,\tfrac12]\) and convex on \([\tfrac12,1]\). The identities
\[
g(1/5)=\frac85r,\qquad g'(1/5)=-2r
\]
make \(2r(1-q)\) the tangent at \(q=1/5\). Concavity handles the left half; on the right half, convexity together with \(g(1/2)=g(1)=0\) yields \(g(q)\le0\). Therefore
\[
g(q)\le2r(1-q)
\]
globally. Averaging over posteriors of mean \(1/2\) gives the claimed support bound \(r\). The mixture with masses \(5/8\) at \(1/5\) and \(3/8\) at \(1\) has mean \(1/2\) and attains equality. Reflection gives the opposite support direction.

### 5. Explicit finite entropic witness

All component entropy weights are strictly between zero and one using
\[
\frac34<h_2(1/4)<\frac78.
\]
A binary variable with each prescribed entropy therefore exists, so the construction is an actual finite distribution rather than only an abstract entropy vector.

For the tuple construction, independent-component union arithmetic verifies:

- \(H(X)=1\);
- \(H(Y)=H(Z)=h\);
- \(H(X,Y)=H(X,Z)=H(Y,Z)=3/2\);
- \(H(X,Y,Z)=2\);
- \(U\perp V\), and \(U,V\) together determine \(X\);
- the required Markov and fixed-map equalities;
- both dependence-balance terms are zero;
- every disjoint-subtuple BEC identity, since the output pair reveals exactly half the entropy of each independent \(U\)- and \(V\)-block, including after conditioning on a disjoint whole block.

The relevant intersections give
\[
I(U;Y)=c,\quad I(V;Z)=r,
\]
and
\[
I(X;Y\mid U)=0,\quad I(X;Z\mid U)=r,
\]
\[
I(X;Y\mid V)=c,\quad I(X;Z\mid V)=\frac14.
\]
Since \(c-\tfrac14=r\), both support rows are tight, and
\[
B_1=B_2=c+r=2h_2(1/4)-\frac54
=0.3725562489182657\ldots.
\]

### 6. Universal inequalities and copy extensions

Because the witness is an actual finite joint distribution, it satisfies every universally valid finite-variable information inequality, including non-Shannon inequalities. A standard copy-lemma extension can be realized by conditional resampling from the designated conditional distribution. Iterating this construction realizes every finite sequential copy extension while preserving the original marginal and objective.

Hence the witness remains feasible under any such universal-inequality or finite standard-copy strengthening. Therefore the supremum of the relaxation’s \(\min(B_1,B_2)\) objective cannot be forced below the displayed value by those ingredients alone.

The scope restriction is essential and correctly stated: the witness has tuple-valued, nonbinary \(X\) and is not generated by the actual BSSC. Exact binary-posterior or other channel-specific constraints can exclude it. Thus the result is a no-go theorem only for the specified coarse entropy/copy route and is not a capacity bound.
