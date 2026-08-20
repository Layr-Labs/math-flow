## bssc-sum-capacity/code-induced-dependence-balance-and-entropy-no-go

**Verdict: Valid**

**Required dependencies:** None. The mathematical arguments needed for both parts are supplied self-contained in the subject evidence. The historical acceptance records and retained source hashes are provenance only, not logical premises.

**Objective attestation:** None supplied. The claimed checker output is therefore not treated as executed evidence; the relevant identities can nevertheless be verified directly from the analytic construction.

### 1. Finite-block code-induced balance

#### Scope and notation

The detailed subject fixes \(N_1,N_2\ge 2\) and defines
\[
R_j=\frac1n\log_2 N_j.
\]
These qualifications are necessary: the condensed declaration omits them, and \(\log_2(N_j-1)\) is undefined for \(N_j=1\). The verified result is thus the theorem on the explicitly supplied domain \(N_j\ge2\). No singleton-message extension is established without an additional convention.

#### Telescope

With
\[
D_i=I(A;B\mid Y^i,Z_{i+1}^n),
\]
one has
\[
I(A;B\mid S_i,Y_i)=D_i,\qquad
I(A;B\mid S_i,Z_i)=D_{i-1}.
\]
Consequently the displayed sum telescopes exactly to
\[
D_n-D_0=I(A;B\mid Y^n)-I(A;B\mid Z^n).
\]
This uses only the definitions and has no hidden channel inequality.

#### Fano bounds

Nonnegativity is automatic. Moreover,
\[
I(A;B\mid Y^n)\le H(A\mid Y^n)\le F_1,
\]
and
\[
I(A;B\mid Z^n)\le H(B\mid Z^n)\le F_2.
\]
Hence the difference lies in \([-F_2,F_1]\), giving
\[
\left|\frac1n(D_n-D_0)\right|
 \le \max\{\delta_1,\delta_2\}.
\]
Uniform independent time sharing converts the average precisely into
\[
\left|I(U;V\mid W,T,Y)-I(U;V\mid W,T,Z)\right|
\le\max\{\delta_1,\delta_2\}.
\]

#### Induced-law factorization

For fixed \((u,v,t)\), the deterministic encoder fixes \(X_t=f_t(u,v)\). Memorylessness makes the current output pair independent of all outputs at other coordinates, including
\[
W=(Y^{t-1},Z_{t+1}^n),
\]
conditional on that fixed input. Thus
\[
p(t,u,v,w,x,y,z)
=\frac1n p_U(u)p_V(v)p(w\mid u,v,t)
  \mathbf 1\{x=f_t(u,v)\}P_{YZ\mid X}(y,z\mid x)
\]
is correct. In particular, the realized \(W\) cannot change the encoder map after \((u,v,t)\) is fixed.

#### Four rate rows

The individual rows follow from Fano, the forward or reverse chain rule, and adjoining \(S_i\) to the first mutual-information argument.

For the first sum row,
\[
n(R_1+R_2)
\le I(A;Y^n)+I(B;Z^n\mid A)+F_1+F_2.
\]
Deterministic encoding and the channel Markov property give
\[
I(B;Z^n\mid A)=I(X^n;Z^n\mid A).
\]
Writing \(P_i=Y^{i-1}\) and \(G_i=Z_{i+1}^n\), the supplied conditioned Csiszár identity
\[
\sum_i I(G_i;Y_i\mid A,P_i)
=\sum_i I(P_i;Z_i\mid A,G_i)
\]
is correct. The per-coordinate expansion leaves the nonnegative remainder
\[
\sum_i I(P_i;Y_i),
\]
so dropping it yields the first asserted sum row. The receiver-swapped derivation leaves
\[
\sum_i I(G_i;Z_i)\ge0
\]
and proves the second sum row. No unsupported sign assumption is used.

The subject also correctly limits the conclusion: growing alphabets prevent this from being, by itself, a fixed-cardinality single-letter outer region.

### 2. Exact entropy/copy no-go theorem

#### Scalar BSSC support inequality

For
\[
g(q)=I_Z(q)-I_Y(q),
\]
the supplied derivative
\[
g''(q)=
\frac{2q-1}{\ln(2)\,q(1-q)(1+q)(2-q)}
\]
has the stated sign: \(g\) is concave on \([0,\tfrac12]\) and convex on \([\tfrac12,1]\).

The identities
\[
g(1/5)=\frac85r,\qquad g'(1/5)=-2r
\]
make the tangent at \(1/5\) equal to \(2r(1-q)\). Concavity puts \(g\) below it on the left half. On the right half, convexity together with \(g(1/2)=g(1)=0\) gives \(g(q)\le0\), while \(2r(1-q)\ge0\). Therefore
\[
g(q)\le2r(1-q)
\]
globally. Averaging any posterior family of mean \(1/2\) gives the sharp bound \(r\). The posterior mixture with masses \(5/8\) at \(1/5\) and \(3/8\) at \(1\) has mean \(1/2\) and attains \(r\); reflection establishes the opposite support direction.

#### Existence and positivity of the witness

Using
\[
h=h_2(1/4),\qquad r=h-\frac34,\qquad s=1-h,\qquad t=2r,
\]
the bounds
\[
\frac34<h<\frac78
\]
make every listed component entropy strictly positive and below one. Continuity of binary entropy on \([0,\tfrac12]\) therefore supplies actual nondegenerate binary variables with exactly those entropies. Their independent product is a genuine finite distribution, not merely a polymatroid.

#### Base entropy vector

For the supplied tuple definitions, direct component-union arithmetic gives
\[
H(X)=1,\quad H(Y)=H(Z)=h,
\]
\[
H(X,Y)=H(X,Z)=H(Y,Z)=\frac32,
\qquad H(X,Y,Z)=2.
\]
All seven required base entropies are therefore satisfied exactly.

#### Structural equalities and BEC identities

The component sets of \(U\) and \(V\) are disjoint and their union is exactly \(X\). Thus
\[
I(U;V)=0,\qquad H(X\mid U,V,T)=0.
\]
Since \(W,T\) are constant, the time-independence and fixed-map constraints hold. Conditional on \(X\), the only extra output components are independent \(N_y,N_z\), proving the required Markov equality.

The joint output reveals exactly half the component entropy of each of \(U\) and \(V\):
\[
H(\text{revealed part of }U)=\frac12H(U),\qquad
H(\text{revealed part of }V)=\frac12H(V).
\]
Because \(U,V\) are independent and \(W,T\) are constant, this remains true after conditioning on any disjoint subtuple. Hence all 65 cases
\[
I(L;Y,Z\mid K)=\frac12 I(L;X\mid K)
\]
hold.

Conditioning on either \(Y\) or \(Z\) only reveals separate projections of the independent component families; it does not introduce dependence between \(U\) and \(V\). Therefore both dependence-balance terms are exactly zero.

#### Support rows and objective

Component intersections give
\[
I(U;Y)=c,\qquad I(V;Z)=r,
\]
\[
I(X;Y\mid U)=0,\qquad I(X;Z\mid U)=r,
\]
\[
I(X;Y\mid V)=c,\qquad I(X;Z\mid V)=\frac14.
\]
Since \(c-\tfrac14=r\), both support inequalities hold at equality. Consequently,
\[
B_1=B_2=c+r
=2h_2(1/4)-\frac54
=0.3725562489182657\ldots.
\]

#### Universal inequalities and copy extensions

Because the witness is an actual finite distribution, it satisfies every information inequality universally valid for finite random variables, including any non-Shannon inequality. Thus such inequalities cannot exclude it.

A standard copy-lemma extension can be realized by conditionally resampling the copied tuple from the required conditional law, independently of the designated variables given the base tuple. This preserves the original marginal and objective. Repeating the construction handles every finite sequential copy hierarchy. Therefore no finite entropy/copy refinement of precisely the stated relaxation can force its maximized objective below the displayed value.

### Scope qualification

The witness has tuple-valued, nonbinary \(X\), so it is not a BSSC input distribution. The result does not establish a capacity bound and does not obstruct binary-posterior or other channel-specific constraints. It proves only the stated no-go result for the specified coarse entropy relaxation and its universal-information-inequality or finite-copy refinements.
