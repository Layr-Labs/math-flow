## `bssc-sum-capacity/theorem9-private-row-audit`

**Verdict: INDETERMINATE**

### Required dependencies

- **Declared reference transactions:** none.
- **Required dependencies from the declared set:** none.

The internal algebraic conclusions are largely established from the fully restated system. However, the claim also asserts exact fidelity to the external Gohari–Liu–Nair Theorem 9. That source-comparison obligation is not established by the supplied record.

### 1. Primary-source transcription fidelity — unresolved

The Markdown transcription and `theorem9_spec.json` are internally consistent: the displayed equations, rate coefficients, branches, and side conditions agree term by term.

But neither the reviewed PDF bytes nor independently authenticated source text is supplied. The attested command ran `verify_specialization.py` **without** `--source-pdf`, as confirmed by the absence of a `PASS source PDF` line. Consequently:

- the stated PDF hash and byte count are only metadata assertions in the contribution;
- the attestation does not authenticate the external PDF;
- the script does not compare the Markdown or JSON equations semantically against PDF contents;
- the factorization is not encoded or checked by the executable audit at all.

Even the optional `--source-pdf` mode would only verify hash and size; it would not parse the PDF and compare its equations with the transcription. Thus the exact assertion that the contribution “faithfully reproduces” the primary source remains materially unverified.

### 2. Private-message expansion to 30 rows — verified relative to the supplied transcription

Given the transcribed system:

- Setting \(R_0=0\) gives the claimed private-message rate coefficients.
- An inequality
  \[
  L\le A+\min_i b_i
  \]
  is equivalent to all scalar inequalities \(L\le A+b_i\).
- The branch count is
  \[
  6\cdot3+2+2+4=26.
  \]
- Each side condition \(0\le L\le R\) is exactly equivalent to
  \(L\ge0\) and \(R-L\ge0\), producing four further rows.

Hence the total is \(30\).

The terminal attestation establishes that the pinned no-argument execution exited successfully and that:

- all 26 expanded equation rows,
- all four side-condition rows,
- their rate coefficients, and
- their normalized signed information terms

agree exactly with the rows produced by `make_path_rows`, using only the stated \(UW\) and \(VW\) chain-rule expansions. This establishes exact equivalence to the supplied executable local formulation, but not fidelity of either representation to the external manuscript.

### 3. Input-only product marginalization — conditionally correct

For any subtuple \(D\) of one auxiliary group, the stated factorization gives

\[
p(d,x,g)
 =p_X(x)p_{D|X}(d|x)
   \sum_{y,z,k}T_{Y,Z|X}(y,z|x)
   T_{G,K|X,Y,Z}(g,k|x,y,z),
\]

which is exactly

\[
p_X(x)p_{D|X}(d|x)\bar T_{G|X}(g|x).
\]

Replacing the auxiliary receiver channel by

\[
T'_{G,K|X,Y,Z}
 =\bar T_{G|X}\bar T_{K|X}
\]

therefore preserves every joint law needed for a term involving \(G\) alone, and similarly for \(K\). The \(Y\)- and \(Z\)-marginals are unchanged.

The audited transcription contains only single-output terms—no joint \((G,K)\) term and no conditioning of one receiver output on another. Thus every transcribed row and side condition is preserved term by term. Product input-only channels are themselves admissible, so the reverse inclusion is immediate.

This conclusion is sound **provided the transcription is exhaustive and faithful**. The unresolved primary-source comparison prevents extending it unconditionally to the actual Theorem 9 system.

### 4. Optimization inequalities — verified

By definition, \(V_Q(G,K)\) restricts the admissible hierarchies in the optimization defining \(V(1/2;G,K)\). Therefore

\[
V_Q(G,K)\le V(1/2;G,K).
\]

Since \(B(G,K)=\sup_{q\in[0,1]}V(q;G,K)\) and \(1/2\in[0,1]\),

\[
V(1/2;G,K)\le B(G,K).
\]

These deductions require no interchange of suprema or attainment assumption.

The restricted feasible set is nonempty: taking \(W_a=W_b=W_c=X\), with the remaining auxiliaries constant, is \(Q_0\)-supported, makes both side conditions zero, and makes zero rates satisfy the rows. The branch-zero individual-rate constraints also bound \(R_1,R_2\), so the relevant suprema are not unbounded.

### 5. Well-definedness of \(V_0(g,k)\) — verified for the transcribed system

For \(S-X-A\) at the fair prior,

\[
I(S;A)=J_A(1/2)-\mathbb E[J_A(q_S)],
\qquad
I(X;A\mid S)=\mathbb E[J_A(q_S)].
\]

Consequently,

\[
I(U;A\mid W)
 =\mathbb E[J_A(q_W)]
  -\mathbb E[J_A(q_{U,W})],
\]

and analogously for \(V\). These identities cover all audited term types:
\(W,U|W,V|W,UW,VW,X|UW,X|VW\).

For every binary-input channel,

\[
J_A(0)=J_A(1)=0.
\]

Thus a \(Q_0=\{0,\tfrac12,1\}\)-supported hierarchy uses the receiver channel only through \(J_A(1/2)\). For the physical BSSC,

\[
J_Y(1/2)=J_Z(1/2)
 =h_2(1/4)-\frac12=c.
\]

Therefore every transcribed objective and feasibility row depends on the four receiver channels only through

\[
(c,g,k,c),
\qquad
g=J_G(1/2),\quad k=J_K(1/2).
\]

The support restriction itself depends only on the auxiliary law, not on the receiver channels. Hence two channels with the same \(g,k\) give identical restricted optimizations, so \(V_0(g,k)\) is unambiguous on its stated domain.

### Final assessment

No internal algebraic defect was found in the 30-row expansion, marginalization argument, optimization inequalities, or \(Q_0\) reduction. Nevertheless, the declared claim is composite and explicitly includes exact primary-source fidelity. Because the supplied attestation does not authenticate or compare against the external theorem—and does not check the factorization—the full all-or-nothing claim cannot be accepted as valid.
