## `bssc-sum-capacity/theorem9-render-complete-audit`

**Verdict: indeterminate**

**Required dependency transactions:** none.  
Gohari–Liu–Nair Theorem 9 is explicitly assumed as a logical premise rather than re-proved. The older transactions mentioned in the README are provenance only and are not needed. The author-hosted URL likewise concerns provenance, not the conditional mathematics audited here.

### What the terminal attestation establishes

The trusted attestation records a successful execution of the no-argument verifier in the pinned Python environment. In particular, the executed checker:

- authenticated a 255,268-byte `GK-outer.pdf` with SHA-256  
  `24c4153530008f7ae339ac19ca8cb90fb8ea574ea8fbcd6a36c2221722d651fa`;
- checked the pinned catalog, page tree, page envelopes, resource closures, and enumerated page-content operators;
- decoded 1,789 theorem glyph records and matched their geometry to a pinned digest;
- compared decoded source text with the structured factorization, equations (19a)–(19p), and two side conditions;
- generated 30 rows from the structured transcription and compared them, after the stated chain-rule normalization, with `make_path_rows`;
- checked the stated \(3/12/12/3\) whitelist of output-bearing information terms.

The attestation does **not** independently establish the theorem’s converse, fetch or authenticate the mutable author-hosted URL, or execute the prose arguments concerning marginalization and \(V_Q,V,B,V_0\).

### Verified algebraic specialization

Conditional on the structured transcription being faithful:

1. Setting \(R_0=0\) is handled correctly.
2. An inequality
   \[
   L\le A+\min_i b_i
   \]
   is equivalent, since all quantities are finite mutual informations, to the collection \(L\le A+b_i\).
3. The branch count is correct:
   - six three-branch constraints: \(18\) rows;
   - (19k) and (19l): \(4\) rows;
   - (19m)–(19p): \(4\) rows;
   - total from (19a)–(19p): \(26\) rows.
4. Each interval condition \(0\le L\le R\) is equivalently \(L\ge0\) and \(R-L\ge0\), giving four further rows.
5. Thus the total is exactly \(30\) rows.
6. The normalization
   \[
   I(U,W;A)=I(W;A)+I(U;A\mid W),
   \qquad
   I(V,W;A)=I(W;A)+I(V;A\mid W)
   \]
   used in the comparison is valid.

### Verified marginalization argument

Again conditional on the audited term list being complete, the product marginalization argument is correct.

For any subtuple \(D\) of one auxiliary group, the theorem’s factorization gives
\[
p(d,x,g)=p_X(x)p_{D|X}(d|x)\bar T_{G|X}(g|x),
\]
and analogously for \(K\). Consequently, replacing the original auxiliary-receiver channel by
\[
T'_{G,K|X,Y,Z}(g,k|x,y,z)
=\bar T_{G|X}(g|x)\bar T_{K|X}(k|x)
\]
preserves every joint distribution needed for a term involving \(G\) alone or \(K\) alone. It directly preserves the \(Y\) and \(Z\) terms as well. Since the enumerated system contains neither joint \((G,K)\)-output terms nor terms conditioning one output on another, every listed row and side condition is preserved. The reverse class inclusion is immediate because an input-only product channel is an allowed auxiliary channel.

### Verified extended-real and \(Q_0\) arguments

The optimization inequalities follow directly from set inclusion:
\[
V_Q(G,K)\le V(1/2;G,K)\le\sup_{q\in[0,1]}V(q;G,K)=B(G,K).
\]
The convention \(\sup\varnothing=-\infty\) makes these inequalities meaningful even when a support-restricted feasible set is empty.

For a Markov chain \(S-X-A\) at the fair prior,
\[
I(S;A)=J_A(1/2)-\mathbb E J_A(q_S),
\qquad
I(X;A\mid S)=\mathbb E J_A(q_S).
\]
Taking differences also gives the asserted formulas for \(I(U;A\mid W)\) and \(I(V;A\mid W)\). These identities cover all seven term forms in the transcription.

For \(Q_0=\{0,\tfrac12,1\}\),
\[
J_A(0)=J_A(1)=0.
\]
Hence, for any fixed \(Q_0\)-supported hierarchy, all receiver dependence is through the four midpoint values
\[
\bigl(J_Y(1/2),J_G(1/2),J_K(1/2),J_Z(1/2)\bigr)=(c,g,k,c).
\]
The hierarchy and posterior-support domains themselves do not depend on the receiver channels, so two channel pairs with the same \((g,k)\) induce the same feasible rows and the same supremum.

Finiteness is also justified:

- choosing \(W_a=W_b=W_c=X\) and all \(U_j,V_j\) constant is \(Q_0\)-supported, satisfies both side conditions, and admits \(R_1=R_2=0\);
- the zero branches of the individual-rate constraints imply
  \[
  R_1\le I(U_a,W_a;Y)\le H(Y)\le1,
  \qquad
  R_2\le I(V_c,W_c;Z)\le H(Z)\le1.
  \]
Thus \(0\le V_0(g,k)\le2\) on its realizable \((g,k)\)-domain.

### Material unresolved source-fidelity obligation

The exact declared claim additionally characterizes the audit as **fail-closed and render-complete** and relies on it to establish fidelity to the complete *visible* theorem. That stronger obligation is not fully discharged by the supplied checker:

- The checker decrypts enough of each Type1 program to inventory `CharStrings`, and it binds each whole font program to a hard-coded digest, but it does not execute or geometrically validate the Type1 CharStrings. Glyph names and ToUnicode mappings are metadata; they do not by themselves prove that the actual painted glyph outline has the asserted visible character.
- Consequently, an empty, misleading, or visually different CharString would not be excluded merely by agreement between glyph name and ToUnicode. The font-program digest only authenticates bytes; the supplied record contains no independently auditable certificate connecting each pinned digest to the claimed visible outlines.
- The geometry check verifies declared font bounding boxes, start positions, page containment, and limited same-baseline monotonicity. It does not establish non-occlusion or semantic legibility of actual glyph outlines. Matching a preselected geometry digest authenticates the layout data but does not itself prove the omitted visual predicate.

These are material because the declared statement expressly relies on a render-complete audit of the visible PDF, rather than only a code-point or ToUnicode transcription. No counterexample to the particular pinned PDF is established, so this is not a decisive falsification. Nevertheless, the supplied evidence does not affirmatively close that obligation. Because the claim is expressly all-or-nothing, the overall verdict is **indeterminate**, despite the downstream algebraic, marginalization, and \(Q_0\) arguments being correct conditional on source fidelity.
