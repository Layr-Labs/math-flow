## `bssc-sum-capacity/code-induced-dependence-balance-and-entropy-no-go`

**Verdict: valid**

The supplied evidence affirmatively establishes both parts of the declared structural claim, subject to the explicitly stated scope: finite-alphabet memoryless broadcast channels, deterministic encoders, message sizes \(N_j\ge 2\), and finite sequences of standard copy-lemma extensions. It does not establish a new capacity bound, and the contribution correctly disclaims one.

### 1. Finite-block dependence telescope

Let
\[
D_i=I(A;B\mid Y^i,Z_{i+1}^n),\qquad 0\le i\le n.
\]
Since
\[
(S_i,Y_i)=(Y^i,Z_{i+1}^n),\qquad
(S_i,Z_i)=(Y^{i-1},Z_i^n),
\]
the \(i\)-th summand is exactly \(D_i-D_{i-1}\). Therefore
\[
\sum_{i=1}^n\!\left[I(A;B\mid S_i,Y_i)-I(A;B\mid S_i,Z_i)\right]
=D_n-D_0,
\]
which is the displayed telescope. No memorylessness or channel inequality is needed for this step.

Both endpoint mutual informations are nonnegative. Moreover,
\[
D_n\le H(A\mid Y^n)\le F_1,\qquad
D_0\le H(B\mid Z^n)\le F_2
\]
by Fano’s inequality. Hence
\[
|D_n-D_0|\le \max\{F_1,F_2\}.
\]
Averaging over an independent uniform time \(T\) gives exactly
\[
\left|I(U;V\mid W,T,Y)-I(U;V\mid W,T,Z)\right|
\le \max\{\delta_1,\delta_2\}.
\]

The source artifact explicitly supplies the needed conventions
\[
N_j\ge2,\qquad R_j=\frac1n\log_2N_j.
\]
Thus there is no unresolved \(N_j=1\) or rate-definition issue in the fully stated theorem.

### 2. Induced-law factorization and fixed-map property

For fixed \((u,v,t)\), deterministic encoding fixes
\[
X_t=f_t(u,v).
\]
The variable \(W=(Y^{t-1},Z_{t+1}^n)\) only contains outputs from coordinates other than \(t\). Memorylessness therefore makes \((Y_t,Z_t)\) conditionally independent of \(W\) given the fixed current input. This proves
\[
p(t,u,v,w,x,y,z)
=\frac1n p_U(u)p_V(v)p(w\mid u,v,t)
\mathbf 1\{x=f_t(u,v)\}P_{YZ\mid X}(y,z\mid x).
\]

Consequently:

- \(U\perp V\);
- \(T\perp(U,V)\);
- \(H(X\mid U,V,T)=0\);
- \(I(X;W\mid U,V,T)=0\);
- \((U,V,W,T)-X-(Y,Z)\).

In particular, the realized value of \(W\) cannot select a different encoder map after \((u,v,t)\) is fixed. The claim correctly distinguishes this from the weaker condition \(H(X\mid U,V,W,T)=0\).

### 3. Four rate rows

The individual rows follow from Fano and chain rules. Writing
\[
P_i=Y^{i-1},\qquad G_i=Z_{i+1}^n,
\]
one has
\[
I(A,P_i,G_i;Y_i)-I(A;Y_i\mid P_i)
=I(P_i;Y_i)+I(G_i;Y_i\mid A,P_i)\ge0.
\]
This proves the first individual row after averaging; the reverse-chain counterpart proves the second.

For the first sum row, independence and Fano give
\[
n(R_1+R_2)
\le I(A;Y^n)+I(B;Z^n\mid A)+F_1+F_2.
\]
Deterministic encoding and \((A,B)-X^n-Z^n\) imply
\[
I(B;Z^n\mid A)=I(X^n;Z^n\mid A).
\]

The conditional Csiszár identity
\[
\sum_i I(G_i;Y_i\mid A,P_i)
=\sum_i I(P_i;Z_i\mid A,G_i)
\]
is proved by an explicit telescope. Memorylessness gives the required reductions to \(X_i\), and the supplied expansion leaves precisely
\[
\sum_i I(P_i;Y_i)\ge0
\]
after the cross terms cancel. Thus
\[
R_1+R_2\le I(U,W;Y\mid T)+I(X;Z\mid U,W,T)+\delta_1+\delta_2.
\]

The receiver-swapped argument is also valid: its uncancelled remainder is
\[
\sum_i I(G_i;Z_i)\ge0.
\]
This proves the fourth row without any hidden sign assumption.

The qualification that these laws have growing alphabets and do not by themselves define a fixed-cardinality outer region is correct and necessary.

### 4. Sharp scalar BSSC support inequalities

For the common-noise coupling and a binary posterior \(q=P(X=1)\),
\[
g(q)=I_Z(q)-I_Y(q)
\]
has
\[
g''(q)=
\frac{2q-1}{\ln(2)\,q(1-q)(1+q)(2-q)}.
\]
Thus \(g\) is concave on \([0,\tfrac12]\) and convex on \([\tfrac12,1]\).

The identities
\[
g(1/5)=\frac85r,\qquad g'(1/5)=-2r
\]
make the tangent at \(1/5\)
\[
2r(1-q).
\]
Concavity places \(g\) below this tangent on the left half. On the right half, convexity together with \(g(1/2)=g(1)=0\) gives \(g(q)\le0\), hence again
\[
g(q)\le2r(1-q).
\]
For any posterior mixture with mean \(1/2\),
\[
\mathbb E g(q_A)\le r.
\]

The proposed mixture,
\[
P(q_A=1/5)=5/8,\qquad P(q_A=1)=3/8,
\]
has mean \(1/2\) and attains equality. Reflection gives the opposite support direction. The two scalar inequalities used in the relaxation are therefore correctly derived and sharp.

### 5. Explicit finite entropic witness

The bounds
\[
\frac34<h_2(1/4)<\frac78
\]
ensure every listed component entropy is strictly between zero and one. Since binary entropy continuously covers \([0,1]\), independent binary components with those exact entropies exist.

For
\[
\begin{aligned}
U&=(C,A,B2c,Eu),&
V&=(B1c,Ev),\\
X&=(C,A,B1c,B2c,Eu,Ev),\\
Y&=(C,A,Ny),&
Z&=(C,B1c,B2c,Nz),
\end{aligned}
\]
with \(W,T\) constant, independent-component arithmetic verifies:

- the complete seven-coordinate base entropy vector;
- \(U\perp V\), with \(U,V\) jointly determining \(X\);
- the fixed-map and memoryless Markov equalities;
- both dependence-balance terms equal zero;
- all 65 disjoint-subtuple BEC identities.

For the BEC identities, the components of \(U\) revealed by \((Y,Z)\) have exactly half of \(H(U)\), and the revealed component of \(V\) has exactly half of \(H(V)\). Independence of \(U,V\), together with constant \(W,T\), extends this to every allowed disjoint pair \((L,K)\).

Direct component intersection gives
\[
\begin{aligned}
I(U;Y)&=c,& I(X;Z\mid U)&=r,\\
I(V;Z)&=r,& I(X;Y\mid V)&=c,
\end{aligned}
\]
and the two support differences both equal \(r\). Hence
\[
B_1=B_2=c+r
=2h_2(1/4)-\frac54
=0.3725562489182657\ldots.
\]

### 6. Universal inequalities and copy-lemma consequence

The witness is an actual finite distribution, not merely a polymatroid. It therefore satisfies every information inequality universally valid for finite random variables.

For a standard copy-lemma step, the copied tuple can be conditionally resampled from the required conditional law, independently of the variables from which conditional independence is required. This preserves the original marginal and objective. Iterating this construction realizes every finite sequential copy extension. Thus no finite collection of universal inequalities or finite standard copy-lemma hierarchy can exclude this witness from the stated relaxation or force its optimized value below
\[
2h_2(1/4)-\frac54.
\]

The limitation is correctly stated: the witness has tuple-valued, nonbinary \(X\) and is not generated by the BSSC. Binary-posterior and other exact channel-consistency constraints can exclude it. Accordingly, the no-go theorem applies only to the specified coarse entropy/copy relaxation and does not furnish a capacity upper bound.
