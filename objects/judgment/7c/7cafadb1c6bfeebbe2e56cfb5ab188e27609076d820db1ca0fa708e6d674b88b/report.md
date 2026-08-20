## `bssc-sum-capacity/theorem9-cited-premise-foundations`

**Verdict: valid, conditional on the explicitly assumed Theorem 9 premise.**

### Scope of the verdict

This verdict does **not** authenticate the external manuscript, the PDF, its transcription provenance, or Theorem 9 itself. It verifies the claimed downstream implications under the exact factorization and constraint system supplied in `theorem9_spec.json` and displayed in `SOURCE_TRANSCRIPTION.md`.

### Audit

1. **Expansion to 30 scalar rows**
   - After \(R_0=0\), the six three-branch minima in (19a)–(19j) produce \(18\) rows.
   - The minima in (19k) and (19l) produce \(2+2\) rows.
   - Equations (19m)–(19p) contribute \(4\) rows.
   - Thus the rate and nonnegativity system has \(18+4+4=26\) rows.
   - Each interval condition \(0\le L\le R\) is equivalently \(L\ge0\) and \(R-L\ge0\), producing four additional rows.
   - Total: \(30\) rows.

   The terminal attestation establishes, for the pinned execution, exact equality of the rate coefficients and normalized information-term coefficients between the premise-derived rows and the separately coded \(L=3\) path rows. Its scope is syntactic/algebraic equality of the encoded systems, not source authentication or proof of the external converse theorem.

2. **Input-only product marginal reduction**
   For an admitted \(T_{G,K|X,Y,Z}\), define its induced single-output marginals \(\bar T_{G|X}\) and \(\bar T_{K|X}\), and replace it by
   \[
   T'_{G,K|X,Y,Z}=\bar T_{G|X}\bar T_{K|X}.
   \]
   Under the assumed factorization, for every relevant auxiliary subtuple \(D\),
   \[
   p(d,x,g)=p_X(x)p_{D|X}(d|x)\bar T_{G|X}(g|x),
   \]
   and analogously for \(K\). Hence all mutual informations involving a single output \(G\) or \(K\), including conditionally expressed terms such as \(I(X;G\mid U,W)\), are preserved. The \(Y\)- and \(Z\)-terms are unchanged.

   The audited term list contains no joint \((G,K)\) term and no term conditioning one receiver output on another. Therefore every one of the 30 scalar constraints is preserved. Finite output alphabets remain finite.

3. **Universal capacity upper bound**
   The premise supplies, for each achievable private-message pair, one prior \(q\) that works for every finite auxiliary-receiver law, with an appropriate finite hierarchy for each such law. Therefore, for every finite input-only pair \((G,K)\),
   \[
   R_1+R_2\le V(q;G,K)\le B(G,K).
   \]
   Taking the infimum over \((G,K)\), followed by the supremum over achievable rate pairs, correctly yields
   \[
   C_{\rm sum}\le
   \inf_{\substack{T_{G|X},T_{K|X}\\\text{finite output}}}B(G,K).
   \]
   No unjustified interchange of \(\sup_q\) and \(\inf_{G,K}\) occurs.

4. **Restricted-value inequalities**
   A \(Q\)-supported hierarchy is a restriction of the feasible set defining \(V(1/2;G,K)\). Thus, with the stated extended-real convention,
   \[
   V_Q(G,K)\le V(1/2;G,K)\le \sup_{q\in[0,1]}V(q;G,K)=B(G,K).
   \]

5. **Dependence of the \(Q_0\) system only on \((c,g,k,c)\)**
   For \(S-X-A\) at the fair prior,
   \[
   I(S;A)=J_A(1/2)-\mathbb E J_A(q_S),\qquad
   I(X;A\mid S)=\mathbb E J_A(q_S),
   \]
   and consequently
   \[
   I(U;A\mid W)
   =\mathbb E J_A(q_W)-\mathbb E J_A(q_{U,W}),
   \]
   with the analogous formula for \(V\). These identities cover all term types appearing in the audited rows.

   For \(Q_0=\{0,\tfrac12,1\}\),
   \[
   J_A(0)=J_A(1)=0
   \]
   for every channel, since \(X\) is then deterministic. Hence receiver-channel dependence enters only through \(J_A(1/2)\). For the physical BSSC,
   \[
   J_Y(1/2)=J_Z(1/2)=h_2(1/4)-\tfrac12=c,
   \]
   so the four receiver values are exactly \((c,g,k,c)\). The admissible auxiliary-law domain itself is channel-independent, establishing that \(V_{Q_0}(G,K)\) is determined solely by \((g,k)\).

6. **Nonemptiness and finiteness of \(V_0(g,k)\)**
   Choosing \(W_a=W_b=W_c=X\) and all \(U_j,V_j\) constant is \(Q_0\)-supported, satisfies both side conditions with zero slack, and permits \(R_1=R_2=0\). Thus the restricted feasible set is nonempty.

   The branch-zero individual-rate constraints imply
   \[
   R_1\le I(U_a,W_a;Y)\le H(Y)\le1,\qquad
   R_2\le I(V_c,W_c;Z)\le H(Z)\le1.
   \]
   Therefore \(0\le V_0(g,k)\le2\), so it is a finite real number on the realizable \((g,k)\)-domain.

### Dependencies

**Required declared-reference dependencies: none.** The external Gohari–Liu–Nair result is an explicit hypothesis of this conditional claim rather than an independently validated conclusion or declared transaction dependency. Its attribution and PDF metadata remain provenance only.
