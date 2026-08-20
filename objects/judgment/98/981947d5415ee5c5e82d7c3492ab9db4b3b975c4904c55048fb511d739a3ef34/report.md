## bssc-sum-capacity/theorem9-cited-premise-foundations

**Verdict: valid, conditional on the explicitly assumed Theorem 9 premise.**

### Premise boundary

The claim does not assert that `theorem9_spec.json` is faithful to the cited PDF or that Gohari–Liu–Nair Theorem 9 is itself correct. It assumes the encoded factorization, equations (19a)–(19p), side conditions, and quantifier order. The following conclusions are valid under that premise.

### Expansion into 30 scalar rows

For an inequality
\[
L\le A+\min_i b_i,
\]
equivalence with the family \(L\le A+b_i\) for every branch \(i\) is exact.

After \(R_0=0\):

- the six three-branch constraints (19a), (19b), (19c)–(19d), (19e)–(19f), (19g)–(19h), and (19i)–(19j) give \(6\cdot3=18\) rows;
- (19k) and (19l) give two rows each, contributing \(4\);
- (19m)–(19p) give four single rows.

Thus there are \(18+4+4=26\) equation-derived rows. In particular, (19a) and (19b) become genuine nonnegativity constraints and are not discarded.

Each side condition \(0\le L\le R\) is exactly equivalent to
\[
L\ge0,\qquad R-L\ge0,
\]
so the two side conditions add four rows, for a total of \(30\).

Inspection of the structured specification and `make_path_rows` confirms that their labels, rate coefficients, and signed information terms agree after only the valid chain-rule normalizations
\[
I(U,W;A)=I(W;A)+I(U;A\mid W),
\quad
I(V,W;A)=I(W;A)+I(V;A\mid W).
\]
The script constructs 30 distinct path rows and compares all of them exactly; no floating-point or optimization assumption is involved.

### Product-marginal replacement

Under the assumed factorization, if \(D\) is a subtuple of one auxiliary group, then
\[
p(d,x,g)=p_X(x)p_{D\mid X}(d\mid x)\bar T_{G\mid X}(g\mid x),
\]
where \(\bar T_{G\mid X}\) is the \(G\)-marginal induced by the original \(T_{G,K\mid X,Y,Z}\). The analogous identity holds for \(K\).

The audited system contains only information quantities involving:

- one auxiliary group and one of \(G\) or \(K\), or
- one auxiliary group and the unchanged physical output \(Y\) or \(Z\).

There are no joint \((G,K)\) terms, no conditioning of one receiver output on another, and no term involving auxiliary variables from multiple groups. Consequently, replacing the auxiliary-receiver channel by
\[
T'_{G,K\mid X,Y,Z}(g,k\mid x,y,z)
=\bar T_{G\mid X}(g\mid x)\bar T_{K\mid X}(k\mid x)
\]
preserves every joint marginal needed by every information term, and hence preserves all 30 rows. Conversely, every such input-only product channel is admitted by the assumed theorem.

### Converse and quantifiers

For an achievable private-message pair, the premise supplies an input prior \(q\) and, for every fixed finite input-only pair \((G,K)\), a finite feasible auxiliary hierarchy. Therefore
\[
R_1+R_2\le V(q;G,K)\le B(G,K)
\]
for every such pair. Hence
\[
R_1+R_2\le \inf_{G,K}B(G,K).
\]
Taking the supremum over all achievable private-message pairs yields
\[
C_{\rm sum}\le
\inf_{\substack{T_{G\mid X},T_{K\mid X}\\
\text{finite-output, binary-input}}}B(G,K).
\]
No invalid interchange of \(\sup_q\) and \(\inf_{G,K}\) occurs.

### Restricted values

The feasible hierarchies defining \(V_Q(G,K)\) form a subset of those defining \(V(1/2;G,K)\). With the declared extended-real convention,
\[
V_Q(G,K)\le V(1/2;G,K)\le \sup_qV(q;G,K)=B(G,K),
\]
including the case where the restricted feasible set is empty.

### Dependence of \(V_0\) only on \((g,k)\)

For \(S-X-A\) at the fair prior,
\[
I(S;A)=J_A(1/2)-\mathbb E[J_A(q_S)],
\qquad
I(X;A\mid S)=\mathbb E[J_A(q_S)].
\]
Subtracting the corresponding identities gives
\[
I(U;A\mid W)
=\mathbb E[J_A(q_W)]-\mathbb E[J_A(q_{U,W})],
\]
and similarly for \(V\). These identities cover every audited term type.

For \(Q_0=\{0,\tfrac12,1\}\),
\[
J_A(0)=J_A(1)=0
\]
for every channel \(A\). Thus every such information term depends on the receiver channel only through \(J_A(1/2)\). For the physical BSSC,
\[
J_Y(1/2)=J_Z(1/2)=h_2(1/4)-\tfrac12=c,
\]
so all rows depend on the four receivers only through \((c,g,k,c)\). Therefore two auxiliary-receiver pairs having the same midpoint values \(g,k\) produce the same restricted optimization, and \(V_0(g,k)\) is unambiguous on the realizable domain.

Finally, the \(Q_0\)-supported choice \(W_a=W_b=W_c=X\), with all \(U_j,V_j\) constant, is feasible at the fair prior: all side-condition quantities vanish, and receiver-difference terms cancel. It admits \(R_1=R_2=0\). The zero-branch individual-rate rows imply
\[
R_1\le I(U_a,W_a;Y)\le1,\qquad
R_2\le I(V_c,W_c;Z)\le1,
\]
because \(Y,Z\) are binary. Hence \(0\le V_0(g,k)\le2\), so it is a finite real number.

The claim makes no authenticated-source, numerical-bound, cardinality, or continuum-optimization assertion beyond these conditional conclusions.
