## `bssc-sum-capacity/theorem9-cited-premise-foundations`

**Verdict: VALID, as a conditional claim.**

The verdict establishes only the implication from the explicitly assumed Theorem 9 premise. It does **not** authenticate the cited manuscript, prove Theorem 9, or establish an unconditional numerical upper bound.

### Audit

1. **Premise boundary and quantifiers**
   - The supplied premise states that for each achievable rate triple there is one input law \(p_X\) such that, for every finite \(T_{G,K|X,Y,Z}\), suitable finite auxiliary triples exist with the displayed factorization and constraints.
   - This quantifier order is sufficient for the subsequent fixed-\((G,K)\) optimization argument.
   - The factorization makes the three auxiliary groups conditionally independent of the receivers given \(X\), as required by the marginalization proof.

2. **Expansion to 30 scalar rows**
   - For an inequality
     \[
     L\le A+\min_i b_i,
     \]
     expansion into all inequalities \(L\le A+b_i\) is exactly equivalent.
   - The six three-branch constraints contribute \(18\) rows; (19k) and (19l) contribute \(2+2\); (19m)–(19p) contribute \(4\), totaling \(26\).
   - Each side condition \(0\le L\le R\) is equivalently \(L\ge0\) and \(R-L\ge0\), adding four rows.
   - Thus the total is exactly \(30\).
   - The supplied transcription and JSON encoding agree term by term on the displayed constraints. The trusted attestation confirms that the encoded expansion agrees with the independently generated path rows after only the valid chain-rule normalizations
     \[
     I(U,W;A)=I(W;A)+I(U;A\mid W),
     \quad
     I(V,W;A)=I(W;A)+I(V;A\mid W).
     \]

3. **Product-marginal replacement**
   - Every receiver-bearing term involves only one of \(Y,G,K,Z\); there are no terms involving joint outputs such as \((G,K)\), nor terms conditioning one receiver output on another.
   - For any auxiliary subtuple \(D\),
     \[
     p(d,x,g)=p_X(x)p_{D|X}(d|x)\bar T_{G|X}(g|x),
     \]
     and analogously for \(K\). Hence replacing the original auxiliary receiver law by
     \[
     T'_{G,K|X,Y,Z}
       =\bar T_{G|X}\bar T_{K|X}
     \]
     preserves every joint marginal needed for all listed mutual-information terms.
   - This covers unconditional, conditional, and residual terms such as
     \(I(U;G\mid W)\), \(I(U,W;G)\), and \(I(X;G\mid U,W)\).
   - Therefore all 30 rows, including both split side conditions, are preserved.

4. **Capacity upper-bound inference**
   - For an achievable private-message pair, the assumed premise supplies a prior \(q\) and a feasible hierarchy for every finite input-only pair \((G,K)\).
   - Consequently,
     \[
     R_1+R_2\le V(q;G,K)\le B(G,K)
     \]
     for every such pair.
   - Taking the receiver infimum and then the supremum over achievable pairs validly gives
     \[
     C_{\mathrm{sum}}
       \le \inf_{\substack{T_{G|X},T_{K|X}\\\text{finite output}}} B(G,K).
     \]
   - No unjustified interchange of \(\sup_q\) and \(\inf_{G,K}\) occurs.

5. **Restricted-value inequalities**
   - The \(Q\)-supported hierarchies form a subset of those admitted in \(V(1/2;G,K)\), so, including empty feasible sets,
     \[
     V_Q(G,K)\le V(1/2;G,K).
     \]
   - Since \(1/2\in[0,1]\),
     \[
     V(1/2;G,K)\le \sup_q V(q;G,K)=B(G,K).
     \]
   - These inequalities remain correct under the stated convention
     \(\sup\varnothing=-\infty\).

6. **Well-definedness of \(V_0(g,k)\)**
   - For every \(S-X-A\),
     \[
     I(S;A)=J_A(1/2)-\mathbb E J_A(q_S),
     \qquad
     I(X;A\mid S)=\mathbb E J_A(q_S),
     \]
     and the analogous difference formula for \(I(U;A\mid W)\) follows by the chain rule.
   - For \(Q_0=\{0,1/2,1\}\), \(J_A(0)=J_A(1)=0\). Thus every audited information term depends on channel \(A\) only through \(J_A(1/2)\).
   - Direct calculation for the physical BSSC gives
     \[
     J_Y(1/2)=J_Z(1/2)=h_2(1/4)-\tfrac12=c.
     \]
     Hence all rows depend only on \((c,g,k,c)\), proving independence from the particular channels realizing \(g\) and \(k\).
   - The choice \(W_a=W_b=W_c=X\) with all \(U_j,V_j\) constant is \(Q_0\)-supported, satisfies the side conditions, and admits \(R_1=R_2=0\). Thus the feasible set is nonempty.
   - The branch-zero individual-rate rows yield
     \[
     R_1\le I(U_a,W_a;Y)\le1,\qquad
     R_2\le I(V_c,W_c;Z)\le1,
     \]
     so \(0\le V_0(g,k)\le2\). Therefore \(V_0\) is finite and well defined on its realizable domain.

### Objective attestation scope

The terminal attestation establishes successful execution of the pinned verifier and its exact row-comparison and term-audit predicates. It does **not** establish manuscript fidelity, the truth of the assumed outer-bound theorem, or the later marginalization and optimization arguments; those latter arguments were separately checked above.

### Required dependencies

**None.** No reference transaction was declared. The Gohari–Liu–Nair statement is fully restated as an explicit hypothesis of this conditional claim, while its bibliographic attribution remains provenance rather than an accepted-state dependency.
