## `bssc-sum-capacity/theorem9-render-complete-audit`

**Verdict: indeterminate**

**Required transaction dependencies:** none.  
The Gohari–Liu–Nair citation and bundled PDF are source evidence and an expressly assumed primary-source premise, not declared transaction dependencies. The correctness of Theorem 9 itself is not reproved or audited here.

### Obligations that are verified

1. **Private-message row expansion, conditional on the transcription.**
   - Setting \(R_0=0\) is straightforward.
   - Replacing
     \[
     L\le A+\min_i b_i
     \]
     by all scalar inequalities \(L\le A+b_i\) is exactly equivalent.
   - The branch counts are
     \[
     6\cdot3+2\cdot2+4\cdot1=26.
     \]
   - Each interval condition \(0\le L\le R\) is equivalent to \(L\ge0\) and \(R-L\ge0\), producing four more rows.
   - The verifier compares these 30 rows with the path-generated rows after only the valid identities
     \[
     I(U,W;A)=I(W;A)+I(U;A\mid W),
     \quad
     I(V,W;A)=I(W;A)+I(V;A\mid W).
     \]
     Its passing execution therefore supports exact algebraic equivalence modulo those identities.

2. **Input-only product marginalization, conditional on the audited term list.**
   For any auxiliary subtuple \(D\) from one group, the stated factorization gives
   \[
   p(d,x,g)=p_X(x)p_{D|X}(d|x)\bar T_{G|X}(g|x),
   \]
   and analogously for \(K\). Thus replacing the auxiliary receiver by
   \[
   T'_{G,K|X,Y,Z}
   =\bar T_{G|X}\bar T_{K|X}
   \]
   preserves every marginal involving \(D,X,G\), every marginal involving \(D,X,K\), and the physical \(Y,Z\) marginals. The displayed system contains no joint \((G,K)\) term and no conditioning of one output on another. Hence all listed rows and side conditions are preserved. The reverse inclusion is immediate because product input-only channels are among the originally admitted channels.

3. **Extended-real inequalities.**
   A \(Q\)-supported hierarchy is a restriction of the feasible set defining \(V(1/2;G,K)\), so monotonicity of the supremum, including the convention \(\sup\varnothing=-\infty\), gives
   \[
   V_Q(G,K)\le V(1/2;G,K).
   \]
   Since \(1/2\in[0,1]\),
   \[
   V(1/2;G,K)\le \sup_{q\in[0,1]}V(q;G,K)=B(G,K).
   \]

4. **Dependence of the \(Q_0\) problem on midpoint mutual informations.**
   For \(S-X-A\) at the fair prior,
   \[
   I(S;A)=J_A(1/2)-\mathbb E J_A(q_S),\qquad
   I(X;A\mid S)=\mathbb E J_A(q_S).
   \]
   Subtraction yields the asserted formulas for \(I(U;A\mid W)\) and \(I(V;A\mid W)\). These cover all seven term types in the transcription. For
   \[
   Q_0=\{0,\tfrac12,1\},
   \]
   every channel has \(J_A(0)=J_A(1)=0\). Therefore channel dependence is only through \(J_A(1/2)\). For the physical BSSC,
   \[
   J_Y(1/2)=J_Z(1/2)=h_2(1/4)-\tfrac12=c,
   \]
   so the rows depend on the four receivers only through \((c,g,k,c)\).

5. **Finiteness of \(V_0\).**
   Taking every \(W_j=X\) and every \(U_j,V_j\) constant is \(Q_0\)-supported. The side conditions vanish, all zero-rate inequalities are satisfied, and hence the restricted feasible set is nonempty. The branch-zero rows give
   \[
   R_1\le I(U_a,W_a;Y)\le1,\qquad
   R_2\le I(V_c,W_c;Z)\le1.
   \]
   Thus \(0\le V_0(g,k)\le2\), and the channel-independence argument makes the definition unambiguous for realizable \(g,k\).

### Material unresolved obligation

The terminal attestation establishes that the pinned checker exited successfully and that it:

- authenticated a 255268-byte PDF with the stated SHA-256;
- accepted the page tree, resources, operators, font metadata, text positioning, and hard-coded geometry digest;
- compared the extracted character sequence with the structured equations;
- compared all 30 generated rows; and
- confirmed the single-output term whitelist.

It does **not**, however, affirmatively establish the claim’s stronger description as a **render-complete semantic audit**. In particular, the supplied Type1 handling decrypts enough material to inventory CharString names and checks whole-font hashes, but it does not parse or execute the Type1 CharString programs to verify the actual painted glyph outlines. ToUnicode mappings, glyph names, widths, declared bounding boxes, and membership in a CharStrings dictionary do not by themselves prove that the visible glyph shapes represent those Unicode characters. The hard-coded font-program hashes bind exact bytes but the record supplies no independently auditable proof connecting those hashes to the asserted visible glyph semantics.

Consequently, the execution certifies acceptance by this checker, not the full claimed visible-render semantic equivalence. Because source fidelity is an explicit conjunct of the all-or-nothing declared claim, while the later algebraic and information-theoretic parts are valid conditional on the transcription, the composite claim cannot be marked valid from the supplied evidence.
