## `bssc-sum-capacity/theorem9-source-bound-audit`

**Verdict: indeterminate**

**Required declared dependencies:** none.  
Gohari–Liu–Nair Theorem 9 is explicitly assumed as a primary-source premise rather than proved here. No transaction reference is needed for the downstream algebra because the needed constraint system is restated in the subject.

### What the terminal attestation establishes

The trusted execution establishes that the pinned verifier:

- read a 255268-byte file with SHA-256  
  `24c4153530008f7ae339ac19ca8cb90fb8ea574ea8fbcd6a36c2221722d651fa`;
- extracted text that its parser associates with equations (19a)–(19p), the factorization, and two side conditions;
- found that text equal to the strings generated from `theorem9_spec.json`;
- expanded the specification into 30 rows;
- compared those rows, after only the stated \(UW\) and \(VW\) chain-rule normalizations, with the independently coded path-row generator;
- found the audited distinct output-term sets to have sizes \(3,12,12,3\).

It does **not** establish Theorem 9 itself, any numerical capacity bound, or the subsequent marginalization and \(V_0\) arguments; those must be checked mathematically.

### Material unresolved source-fidelity obligation

The exact declared claim says that the transcription **faithfully reproduces the theorem in the source PDF**. The verifier’s encoded predicate is weaker than complete PDF-semantic or visual equivalence:

- `_decode_text` recognizes text shown through `Tj` and `TJ`, but silently ignores other PDF operators after clearing their operands. In particular, it does not fail if text is shown through other legal text-showing operators such as `'` or `"`.
- It does not recursively process form XObjects invoked through `Do`, nor prove that the relevant page resources contain no such source of theorem content.
- It concatenates decoded strings in content-stream order without checking text position, rendering mode, clipping, or visibility. Thus it does not rule out expected but invisible text coexisting with different visible content.
- The verifier does not perform an exhaustive operator audit showing that all theorem-bearing content in the pinned pages is represented by the handled `Tj`/`TJ` operations.

Consequently, the passed execution certifies equality with the parser’s extracted string, but the supplied record does not affirmatively prove that this string is the complete rendered mathematical statement in the PDF. There is no demonstrated counterexample involving the pinned bytes, so this is an unresolved material obligation rather than a decisive falsification.

The attestation also authenticates only the committed bytes and digest; it does not independently establish the provenance assertion that those bytes are the official author-hosted version. That is primarily a source-provenance limitation, not a mathematical defect.

### Conditional verification of the 30-row specialization

Conditional on the displayed source transcription being correct:

1. Replacing \(R_0\) by zero is direct.
2. An inequality
   \[
   L\le A+\min_i b_i
   \]
   is equivalent to the collection \(L\le A+b_i\) for every branch \(i\).
3. The branch counts are
   \[
   6\cdot3+2\cdot2+4\cdot1=26.
   \]
4. Each side condition \(0\le L\le R\) is equivalent to \(L\ge0\) and \(R-L\ge0\), adding four rows.

Thus the stated total of \(30\) rows is correct. The verifier checks equality of rate coefficients and normalized information-term coefficients for all 30 rows. The normalization
\[
I(U,W;A)=I(W;A)+I(U;A\mid W)
\]
and its \(V\)-analogue is universally valid, so the row comparison is mathematically sound conditional on the transcription.

### Marginalization argument

This portion is correct conditional on the factorization and audited term list.

For any subtuple \(D\) of one auxiliary group, the factorization gives
\[
p(d,x,g)=p_X(x)p_{D\mid X}(d\mid x)\bar T_{G\mid X}(g\mid x),
\]
where \(\bar T_{G\mid X}\) is the \(G\)-marginal induced by the original auxiliary-receiver channel and the fixed physical channel. Replacing the latter by
\[
T'_{G,K\mid X,Y,Z}
 =\bar T_{G\mid X}\bar T_{K\mid X}
\]
therefore preserves every joint law \((D,X,G)\); likewise it preserves every \((D,X,K)\) law. The \(Y\)- and \(Z\)-bearing laws are unchanged.

Since the audited system contains no joint \((G,K)\) term and no output conditioned on another output, every listed information quantity, including those in the side conditions, is preserved. Product input-only channels are themselves admissible, so the claimed reverse inclusion is also valid.

### Extended-real inequalities

These follow immediately from set inclusion:
\[
V_Q(G,K)\le V(1/2;G,K)
\]
because \(Q\)-support restricts the fair-prior feasible hierarchies, and
\[
V(1/2;G,K)\le \sup_{q\in[0,1]}V(q;G,K)=B(G,K).
\]
The convention \(\sup\varnothing=-\infty\) handles an empty restricted feasible set without changing these inequalities.

### Well-definedness and finiteness of \(V_0\)

For \(S-X-A\) at the fair prior,
\[
I(S;A)=J_A(1/2)-\mathbb E J_A(q_S),\qquad
I(X;A\mid S)=\mathbb E J_A(q_S).
\]
Subtracting the corresponding identities gives
\[
I(U;A\mid W)
 =\mathbb E J_A(q_W)-\mathbb E J_A(q_{U,W}),
\]
and similarly for \(V\). These identities cover every audited term type.

For \(Q_0=\{0,\tfrac12,1\}\),
\[
J_A(0)=J_A(1)=0,
\]
so channel dependence enters only through \(J_A(1/2)\). For the physical BSSC,
\[
J_Y(1/2)=J_Z(1/2)=h_2(1/4)-\tfrac12=c.
\]
Hence all rows and side conditions depend on the receiver channels only through \((c,g,k,c)\), establishing representation-independence of \(V_0(g,k)\).

The restricted problem is nonempty: choose \(W_a=W_b=W_c=X\) and all \(U_j,V_j\) constant. All relevant posteriors lie in \(Q_0\), both side conditions vanish, and \(R_1=R_2=0\) satisfies the rows. Finally, branch-zero rows imply
\[
R_1\le I(U_a,W_a;Y)\le1,\qquad
R_2\le I(V_c,W_c;Z)\le1,
\]
so the supremum is finite. Thus this downstream part is correct.

Because the source-fidelity conjunct remains unsupported by the verifier’s exact encoded predicate, the all-or-nothing declared claim cannot be marked valid.
