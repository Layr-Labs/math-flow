# Conditional-product Marton architectures have no multiletter gain

## Claim and scope

Let \(T:x\mapsto(Y,Z)\) be a finite two-receiver broadcast channel. For a
finite law \(P_{WUVX}\), write

\[
\begin{aligned}
M_T(P)&=\min\{I(W;Y),I(W;Z)\}
  +I(U;Y\mid W)+I(V;Z\mid W)-I(U;V\mid W),\\
L_{\alpha,T}(P)&=(1-\alpha)I(W;Y)+\alpha I(W;Z)
  +I(U;Y\mid W)+I(V;Z\mid W)-I(U;V\mid W),
\end{aligned}
\]

and let \(M_T=\sup_P M_T(P)\) and
\(L_{\alpha,T}=\sup_P L_{\alpha,T}(P)\). The suprema use the usual Markov
condition \((W,U,V)-X-(Y,Z)\).

Call \(T\) **receiver-skew** if there are an input involution
\(s:\mathcal X\to\mathcal X\) and output bijections
\(r_Y:\mathcal Y\to\mathcal Z\), \(r_Z:\mathcal Z\to\mathcal Y\) such that

\[
T_{Y\mid X}(y\mid x)=T_{Z\mid X}(r_Y(y)\mid s(x)),\qquad
T_{Z\mid X}(z\mid x)=T_{Y\mid X}(r_Z(z)\mid s(x)).
\tag{RS}
\]

Thus applying \(s\) to the input and relabeling the outputs exchanges the two
receiver marginal channels. Equivalently, every valid one-letter law has a
relabeled partner for which the roles of \((Y,U)\) and \((Z,V)\) are
exchanged. For the half-skew BSSC, \(s(x)=1-x\) and both output relabelings
are the bit flip \(b\mapsto1-b\).

For \(n\geq1\), define the conditional-product Marton class on
\(T^{\otimes n}\) by the laws

\[
P(w,u^n,v^n,x^n)
=P(w)\prod_{i=1}^n P_i(u_i,v_i,x_i\mid w),
\qquad
U=(U_1,\ldots,U_n),\quad V=(V_1,\ldots,V_n).
\tag{1}
\]

The common auxiliary \(W\) in (1) is completely arbitrary. It can carry a
joint schedule, use different coordinate laws for every \(w\), and correlate
all coordinates unconditionally. The sole structural restriction is that the
coordinate satellite/input packets \((U_i,V_i,X_i)\) are independent
conditioned on the actual \(W\) used by the Marton construction.

This contribution proves

\[
\boxed{
\sup_{P\text{ satisfying }(1)} M_{T^{\otimes n}}(P)=nM_T
}
\tag{2}
\]

for every finite receiver-skew broadcast channel \(T\) and every positive
integer \(n\). No attainment assumption is needed.

For the half-skew BSSC \(P\), (2) says in particular that the two-letter
conditional-product supremum is

\[
2M_P
=0.723285768843909231326883156301174\ldots
\quad\text{bits per two uses},
\]

using the governed one-letter Marton benchmark. Therefore any strict
two-letter BSSC gain must lie outside (1): it cannot be generated solely by
an arbitrary common \(W\) followed by conditionally independent coordinate
packets. A gaining witness must instead use a genuinely non-factorizable
cross-use satellite/input law given its common auxiliary: every chosen
coordinate-packet decomposition under which (1) could be tested must fail
that factorization. For the broader class with a chosen tuple decomposition
but otherwise arbitrarily correlated satellites and inputs, equation (11)
below gives an exact total-correlation ledger, and (13) is a strict necessary
correlation-balance test for any gain. The ledger depends on that chosen
decomposition.

## Relation to the August 2026 frontier

This contribution discharges the conditional-product structural-pruning
target in research direction `bssc-multiletter-marton-frontier`, registered by
canonical transaction `7e1e52fe42fde37ba1964ef9ae5062daf8bb55f8`.
That registration is program provenance, not a mathematical premise, so the
claim manifest declares no dependency on it.

Huang, Liu, and Liu,
[arXiv:2608.19869v1](https://arxiv.org/abs/2608.19869v1), prove that some
finite, nonbinary-input channels satisfy
\(M_{T^{\otimes2}}>2M_T\), while explicitly leaving binary-input tightness
open. Their equations (2)--(3) record the Marton and affine functionals above,
and the max--min identity displayed immediately afterward is

\[
M_T=\min_{\alpha\in[0,1]}L_{\alpha,T}.
\tag{3}
\]

The one-letter binary-input result of Nair, Wang, and Geng in the cited
arXiv v1,
[arXiv:1001.1468v1](https://arxiv.org/abs/1001.1468v1), proves that randomized
time division evaluates \(M_T\) for every binary-input channel. Equation (2)
does not merely take independent copies of that special optimizer: its upper
bound permits arbitrary one-letter \(U_i,V_i\) within every coordinate and an
arbitrary shared \(W\), and identifies conditional cross-use coupling as a
necessary ingredient for a gain.

Canonical transaction
f236017c62c67ce4218c1f81ea34134f0954b556 proves exact product additivity
for two *separately relaxed UV outer functionals*. The present result is
different: it applies directly to the joint Marton \(U,V,W\) functional, but
only on the conditional-product architecture (1). Neither theorem implies
the other. The canonical transaction is contextual comparison, not a premise
of the present proof.

## Proof

### 1. Receiver skew fixes the midpoint, self-containedly

For a candidate \(P\), abbreviate

\[
a=I(W;Y),\qquad b=I(W;Z),\qquad
S=I(U;Y\mid W)+I(V;Z\mid W)-I(U;V\mid W).
\]

Define its reflected candidate \(\widetilde P\) by

\[
(\widetilde W,\widetilde U,\widetilde V,\widetilde X)
=(W,V,U,s(X)).
\]

If \((\widetilde Y,\widetilde Z)\) are the channel outputs under this
candidate, (RS) and invariance of mutual information under bijective output
relabelings give

\[
\begin{aligned}
I(\widetilde W;\widetilde Y)&=b,&
I(\widetilde W;\widetilde Z)&=a,\\
I(\widetilde U;\widetilde Y\mid\widetilde W)
  &=I(V;Z\mid W),&
I(\widetilde V;\widetilde Z\mid\widetilde W)
  &=I(U;Y\mid W),\\
I(\widetilde U;\widetilde V\mid\widetilde W)
  &=I(U;V\mid W).
\end{aligned}
\]

Reflection is a bijection on the candidate laws. Thus
\(L_{\alpha,T}(\widetilde P)=L_{1-\alpha,T}(P)\), and taking suprema proves

\[
L_{\alpha,T}=L_{1-\alpha,T}.
\tag{4}
\]

The equality needed below follows without a minimax premise. Pointwise,
\(\min\{a,b\}\leq(a+b)/2\), so \(M_T\leq L_{1/2,T}\). For the converse, let a
fair bit \(Q\) select \(P\) or \(\widetilde P\), and include the selector in
the common auxiliary:

\[
W'=(Q,W_Q),\qquad U'=U_Q,\qquad V'=V_Q,\qquad X'=X_Q.
\]

The alphabets in the two branches may be placed in disjoint tagged copies, so
this is a valid finite Marton law even when the original \(U,V\) alphabets
differ. Because \(W'\) reveals the branch, its satellite term is exactly
\(\tfrac12(S+S)=S\), while

\[
\begin{aligned}
I(W';Y)&=I(Q;Y)+I(W_Q;Y\mid Q)
       =I(Q;Y)+\tfrac12(a+b)\geq\tfrac12(a+b),\\
I(W';Z)&=I(Q;Z)+I(W_Q;Z\mid Q)
       =I(Q;Z)+\tfrac12(a+b)\geq\tfrac12(a+b).
\end{aligned}
\]

Therefore \(M_T(P')\geq(a+b)/2+S=L_{1/2,T}(P)\). This construction works for
every \(P\), so taking suprema gives the reverse inequality and hence

\[
M_T=L_{1/2,T}.
\tag{5}
\]

There is no attainment assumption. As an independent check, \(L_{\alpha,T}\)
is convex as a supremum of affine functions, and (4) makes \(1/2\) a
minimizer; combining that observation with the published max--min identity
(3) gives the same conclusion. Equation (3) is therefore cited context, not a
premise of this proof.

### 2. Conditional terms add exactly, pointwise in \(W\)

Fix a law of the form (1). Conditional on every positive-probability value
\(W=w\), the memoryless product channel and (1) give

\[
P(u^n,v^n,x^n,y^n,z^n\mid w)
=\prod_{i=1}^n
P_i(u_i,v_i,x_i\mid w)T(y_i,z_i\mid x_i).
\tag{6}
\]

Thus the coordinate pairs \((U_i,Y_i)\), the coordinate pairs \((V_i,Z_i)\),
and the coordinate pairs \((U_i,V_i)\) are each independent across \(i\)
conditioned on \(W=w\). Additivity of entropy for product laws gives,
pointwise in \(w\),

\[
\begin{aligned}
I(U^n;Y^n\mid W=w)&=\sum_i I(U_i;Y_i\mid W=w),\\
I(V^n;Z^n\mid W=w)&=\sum_i I(V_i;Z_i\mid W=w),\\
I(U^n;V^n\mid W=w)&=\sum_i I(U_i;V_i\mid W=w).
\end{aligned}
\tag{7}
\]

Averaging (7) over \(w\) proves the same three identities conditioned on
\(W\). This is exact, rather than an inequality or an asymptotic
single-letterization.

### 3. The common term is subadditive

Equation (6) also makes \(Y_1,\ldots,Y_n\) conditionally independent given
\(W\). Hence

\[
\begin{aligned}
I(W;Y^n)
&=H(Y^n)-H(Y^n\mid W)\\
&\leq\sum_iH(Y_i)-\sum_iH(Y_i\mid W)
=\sum_iI(W;Y_i).
\end{aligned}
\tag{8}
\]

The same proof gives \(I(W;Z^n)\leq\sum_iI(W;Z_i)\). Using
\(\min\{a,b\}\leq(a+b)/2\), then (7)--(8), gives

\[
\begin{aligned}
M_{T^{\otimes n}}(P)
&\leq \tfrac12 I(W;Y^n)+\tfrac12 I(W;Z^n)
  +I(U^n;Y^n\mid W)+I(V^n;Z^n\mid W)-I(U^n;V^n\mid W)\\
&\leq\sum_{i=1}^n\Big[
  \tfrac12 I(W;Y_i)+\tfrac12 I(W;Z_i)
  +I(U_i;Y_i\mid W)+I(V_i;Z_i\mid W)-I(U_i;V_i\mid W)
\Big].
\end{aligned}
\tag{9}
\]

For every \(i\), the marginal \(P_{WU_iV_iX_i}\) is an admissible one-letter
Marton law for \(T\). Its bracket in (9) is therefore at most
\(L_{1/2,T}=M_T\) by (5). This proves the upper bound in (2).

### 4. An exact correlation ledger beyond the product class

The preceding bound has a sign-exact refinement that also identifies what a
correlated witness would have to overcome. Consider the broader
**tuple-auxiliary class** consisting of every finite law
\(P(w,u^n,v^n,x^n)\), with the explicit aggregate representation
\(U=(U_1,\ldots,U_n)\), \(V=(V_1,\ldots,V_n)\), followed by the product
channel:

\[
P(w,u^n,v^n,x^n,y^n,z^n)
=P(w,u^n,v^n,x^n)\prod_iT(y_i,z_i\mid x_i).
\tag{10}
\]

Unlike (1), equation (10) permits arbitrary conditional cross-use correlation
among the satellite pairs and arbitrary cross-use input dependence; in
particular, \(X_i\) may depend on all of \(U^n,V^n,W\). Any finite abstract
auxiliaries \(U,V\) admit such a tuple representation by placing the whole
variable in one coordinate and padding the others with constants. The
representation is noncanonical, however, and every term in the ledger below
is evaluated relative to the particular decomposition chosen. For a vector
\(A^n\), define

\[
\operatorname{TC}(A^n\mid C)
=\sum_iH(A_i\mid C)-H(A^n\mid C),
\qquad
\operatorname{TC}(A^n)
=\sum_iH(A_i)-H(A^n),
\]

and define the cross-conditioning gaps

\[
\begin{aligned}
G_{UY}&=\sum_iH(Y_i\mid U_i,W)-H(Y^n\mid U^n,W),\\
G_{VZ}&=\sum_iH(Z_i\mid V_i,W)-H(Z^n\mid V^n,W),\\
G_{UV}&=\sum_iH(U_i\mid V_i,W)-H(U^n\mid V^n,W).
\end{aligned}
\]

Each displayed total correlation and gap is nonnegative by entropy
subadditivity and conditioning. Let \(P^{(i)}\) denote the coordinate marginal
\(P_{WU_iV_iX_i}\), which is a valid one-letter Marton law because the
memoryless channel makes \((W,U_i,V_i)-X_i-(Y_i,Z_i)\) even when the input law
in (10) is globally coupled. Direct entropy expansion gives the exact
identity

\[
\begin{aligned}
&L_{1/2,T^{\otimes n}}(P)
 -\sum_iL_{1/2,T}(P^{(i)})\\
&\quad=\operatorname{TC}(U^n\mid W)+G_{UY}+G_{VZ}-G_{UV}\\
&\qquad\quad-\tfrac12\big[
 \operatorname{TC}(Y^n\mid W)+\operatorname{TC}(Y^n)
 +\operatorname{TC}(Z^n\mid W)+\operatorname{TC}(Z^n)
\big].
\tag{11}
\end{aligned}
\]

Indeed, the common-\(Y\), private-\(UY\), and penalty differences are,
respectively,

\[
\begin{aligned}
I(W;Y^n)-\sum_iI(W;Y_i)
  &=\operatorname{TC}(Y^n\mid W)-\operatorname{TC}(Y^n),\\
I(U^n;Y^n\mid W)-\sum_iI(U_i;Y_i\mid W)
  &=-\operatorname{TC}(Y^n\mid W)+G_{UY},\\
-I(U^n;V^n\mid W)+\sum_iI(U_i;V_i\mid W)
  &=\operatorname{TC}(U^n\mid W)-G_{UV}.
\end{aligned}
\]

The \(Z\) expansions are identical. Summing them with the half weights proves
(11). This identity itself uses only the tuple representation and product
channel, not receiver skew; the gain implication below additionally uses
(5). The apparently asymmetric penalty representation is harmless: if
\(G_{VU}=\sum_iH(V_i\mid U_i,W)-H(V^n\mid U^n,W)\), then

\[
\operatorname{TC}(U^n\mid W)-G_{UV}
=\sum_iI(U_i;V_i\mid W)-I(U^n;V^n\mid W)
=\operatorname{TC}(V^n\mid W)-G_{VU}.
\]

For a conditional-product law (1), every conditional total correlation and
every \(G\)-gap in (11) vanishes. Thus (11) reduces to

\[
L_{1/2,T^{\otimes n}}(P)
=\sum_iL_{1/2,T}(P^{(i)})
 -\tfrac12\big[\operatorname{TC}(Y^n)+\operatorname{TC}(Z^n)\big],
\tag{12}
\]

which sharpens (9) and makes its only possible slack explicit.

More generally, if a tuple-auxiliary law (10) gives
\(M_{T^{\otimes n}}(P)>nM_T\), then
\(M_{T^{\otimes n}}(P)\leq L_{1/2,T^{\otimes n}}(P)\) and
\(\sum_iL_{1/2,T}(P^{(i)})\leq nM_T\). Equation (11) therefore forces the strict
necessary condition

\[
\operatorname{TC}(U^n\mid W)+G_{UY}+G_{VZ}-G_{UV}
>\tfrac12\big[
 \operatorname{TC}(Y^n\mid W)+\operatorname{TC}(Y^n)
 +\operatorname{TC}(Z^n\mid W)+\operatorname{TC}(Z^n)
\big].
\tag{13}
\]

This correlation-balance test is not sufficient for a gain, but it gives a
human-checkable pruning condition for the remaining nonproduct search.

### 5. Independent copies prove the reverse inequality

Let \(\varepsilon>0\) and choose a finite one-letter law \(P^*_{WUVX}\) with

\[
M_T(P^*)>M_T-\varepsilon.
\]

Take \(n\) independent copies, put the copy-wise common variables into the
single aggregate common auxiliary \(W=(W_1,\ldots,W_n)\), and use
\(U=(U_1,\ldots,U_n)\), \(V=(V_1,\ldots,V_n)\). Conditional on aggregate
\(W\), the coordinate packets factor exactly as in (1). Full independence
across copies makes both common mutual informations and all three conditional
terms additive, so

\[
M_{T^{\otimes n}}((P^*)^{\otimes n})=nM_T(P^*)
>nM_T-n\varepsilon.
\]

Letting \(\varepsilon\downarrow0\) proves the reverse inequality in (2). This
argument uses an epsilon-optimizer and therefore does not assume that the
one-letter supremum is attained.

## Deterministic corroboration

Run from this contribution directory:

    PYTHONDONTWRITEBYTECODE=1 python3 verify_conditional_product.py

verification.json requests the same networkless standard-library entrypoint.
The script checks the exact rational BSSC receiver-skew relabeling, then uses
a fixed seed to construct finite conditional-product laws and mechanically
checks (7), (8), and (9). It separately constructs independent copies of a
one-letter law and checks equality of the complete Marton functional. A
second fixed-seed family has arbitrary correlated tuple satellites and
inputs; it checks both sides of (11), nonnegativity of every displayed gap,
and the symmetric \(U\)-versus-\(V\) representation of the penalty term.

These finite floating-point checks are corroboration only. The universal
theorem rests on the symmetrization proof and entropy identities above; the
verifier does not exhaust arbitrary alphabets or certify any optimizing law.

## Limitations and provenance

- Equation (2) does **not** establish unrestricted additivity
  \(M_{T^{\otimes n}}=nM_T\). In particular it does not resolve the open
  binary-input or BSSC tightness question highlighted in arXiv:2608.19869v1.
- The equality theorem (2) does not cover conditionally coupled coordinate
  packets. The ledger (11) does cover arbitrary coupling after any chosen
  tuple representation, including trivial constant padding, but gives only a
  necessary correlation-balance test, not a no-gain result. Its numerical and
  pruning usefulness can change with the noncanonical decomposition.
- It does not improve either endpoint of the governed BSSC capacity interval
  and gives no capacity converse.
- The max--min identity (3) is external published context, explicitly
  attributed above, but it is not a premise. The receiver-skew midpoint
  equality, conditional-product theorem, and correlation ledger are proved
  internally.
- Rates in this contribution use bits, while arXiv:2608.19869v1 uses natural
  logarithms. Every identity is invariant under this common positive scale.

The theorem and proof were derived for this Math Flow contribution by an
OpenAI Codex research agent under Robert Raynor's direction. The two cited
papers retain authorship of their results; no part of their counterexample is
claimed here.
