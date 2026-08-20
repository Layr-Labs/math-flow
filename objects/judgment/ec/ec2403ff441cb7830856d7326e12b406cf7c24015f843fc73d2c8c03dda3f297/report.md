## `bssc-sum-capacity/theorem9-source-bound-audit`

**Verdict: indeterminate**

The downstream algebraic and information-theoretic arguments are correct conditional on the supplied transcription being complete and faithful. However, the exact source-binding component of this composite claim is not affirmatively established by the evidence available here, so the all-or-nothing claim cannot be marked valid.

### 1. Primary-source fidelity is not verifiable from the supplied evidence

The claim asserts that the committed official PDF and its deterministic extraction establish exact agreement with Theorem 9. The supplied packet includes:

- the asserted PDF hash and byte length;
- the extractor and verifier source code;
- the structured transcription;
- statements that the verifier passes.

It does **not** include:

- the bytes of `GK-outer.pdf`;
- a governed execution result or signed attestation showing that the verifier was actually run successfully on those bytes; or
- declared reference evidence independently binding the asserted digest to the official author-hosted manuscript.

Consequently, the following material facts cannot be checked:

1. that the alleged PDF bytes have the stated digest and size;
2. that the pinned PDF has the page, object-stream, resource, and font structures assumed by `pdf_source_extract.py`;
3. that extraction of those bytes yields the exact theorem text against which the JSON is compared;
4. that the committed file is in fact the official manuscript rather than merely a file accompanied by self-declared metadata.

The expected digest is stored in the same contribution as the asserted source file, so the metadata alone is not independent evidence of provenance or content. Also, despite the README mentioning the embedded creation date, `verify_specialization.py` does not inspect or verify `pdfCreationDate`.

Taking Theorem 9 itself as a premise excuses re-proving its converse, but it does not establish that the particular bounded transcription faithfully reproduces the primary source. This unresolved source obligation is decisive for the composite claim.

### 2. Thirty-row specialization is correct conditional on the transcription

For the equations displayed in `SOURCE_TRANSCRIPTION.md` and encoded in `theorem9_spec.json`, setting \(R_0=0\) and expanding minima gives:

- \(6\) nonnegativity rows from (19a)–(19b);
- \(12\) individual-rate rows from the four three-branch inequalities (19c)–(19j);
- \(8\) sum-rate rows from (19k)–(19p);
- \(4\) rows from splitting the two interval side conditions.

Thus there are \(26+4=30\) scalar rows.

The rule
\[
L\le A+\min_i b_i
\quad\Longleftrightarrow\quad
L\le A+b_i\ \text{for every }i
\]
is applied correctly. Likewise,
\[
0\le L\le R
\quad\Longleftrightarrow\quad
L\ge0,\qquad R-L\ge0.
\]

Inspection of `make_path_rows` shows that its left/right path formulas agree with the structured rows after only the stated chain-rule expansions
\[
I(U,W;A)=I(W;A)+I(U;A\mid W),\qquad
I(V,W;A)=I(W;A)+I(V;A\mid W).
\]
The rate coefficients and row counts are also consistent.

This verifies equivalence between the supplied structured transcription and the supplied local construction, but not their equivalence to the unavailable PDF.

### 3. Product marginalization argument is mathematically sound conditional on term completeness

Under the stated factorization, for any subtuple \(D\) of one auxiliary group,
\[
p(d,x,g)
 =p_X(x)p_{D\mid X}(d\mid x)
   \sum_{y,z,k}T_{Y,Z\mid X}(y,z\mid x)
   T_{G,K\mid X,Y,Z}(g,k\mid x,y,z).
\]
The final factor is exactly the induced marginal \(\bar T_{G\mid X}(g\mid x)\). Replacing the auxiliary channel by
\[
T'_{G,K\mid X,Y,Z}(g,k\mid x,y,z)
 =\bar T_{G\mid X}(g\mid x)\bar T_{K\mid X}(k\mid x)
\]
therefore preserves every joint law of the form \((D,X,G)\), and analogously every \((D,X,K)\) law. The \(Y\)- and \(Z\)-marginals are unchanged.

Every term in the supplied 3/12/12/3 audit involves only:

- one auxiliary-group subtuple;
- \(X\), where applicable; and
- one output among \(Y,G,K,Z\).

There is no joint \((G,K)\) term and no conditioning of one receiver output on another. Hence all listed information quantities, rows, and side conditions are preserved. Conversely, every input-only product channel is an allowed special case of \(T_{G,K\mid X,Y,Z}\).

Thus the marginalization proof is correct for the displayed system. Its claimed applicability to the *entire actual Theorem 9 system* remains conditional on the unresolved source-fidelity and exhaustive-term obligations.

### 4. The value inequalities are verified

Because \(V_Q(G,K)\) restricts the auxiliary hierarchies admitted in \(V(1/2;G,K)\),
\[
V_Q(G,K)\le V(1/2;G,K).
\]
By definition,
\[
B(G,K)=\sup_{q\in[0,1]}V(q;G,K),
\]
so the \(q=1/2\) value satisfies
\[
V(1/2;G,K)\le B(G,K).
\]
These remain valid as extended-real inequalities, including when a restricted feasible set is empty and its supremum is defined as \(-\infty\).

### 5. Dependence of \(V_{Q_0}\) only on \((c,g,k,c)\) is verified

At the fair input prior, for a Markov chain \(S-X-A\),
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
with the analogous identity for \(V\).

For every binary-input channel,
\[
J_A(0)=J_A(1)=0.
\]
If all relevant posteriors belong to
\[
Q_0=\{0,1/2,1\},
\]
every expectation above is determined solely by \(J_A(1/2)\) and the hierarchy’s posterior probabilities. The hierarchy law itself is chosen conditional on \(X\) and does not depend on the realization of the receiver channel. Therefore all supplied rows and side conditions depend on the four channels only through
\[
\bigl(J_Y(1/2),J_G(1/2),J_K(1/2),J_Z(1/2)\bigr)
 =(c,g,k,c).
\]
Hence two finite-output channels \(G,K\) with the same midpoint values produce the same restricted optimization value.

This establishes well-definedness for pairs \((g,k)\) induced by the admitted finite-output channels.

### 6. Finiteness and nonemptiness of \(V_0(g,k)\) are verified

With \(W_a=W_b=W_c=X\) and all \(U_j,V_j\) constant:

- every relevant posterior is \(0\) or \(1\), so the hierarchy is \(Q_0\)-supported;
- all conditional terms with \(X\) conditioned on \(W_j=X\) vanish;
- both side conditions reduce to \(0\le0\le0\);
- all cross-group differences cancel;
- every remaining private-rate or sum-rate right-hand side is nonnegative.

Thus \(R_1=R_2=0\) is feasible.

The branch-zero individual-rate rows give
\[
R_1\le I(U_a,W_a;Y)\le H(Y)\le1,
\qquad
R_2\le I(V_c,W_c;Z)\le H(Z)\le1.
\]
Therefore every feasible sum satisfies \(R_1+R_2\le2\), proving that \(V_0(g,k)\) is a finite real number.

### Conclusion

The row expansion, marginalization, extended-real inequalities, posterior reduction, and finiteness arguments are correct **conditional on the supplied transcription being the complete Theorem 9 statement**. Because the actual PDF bytes and an auditable successful execution/source attestation are absent, exact fidelity to the primary source remains materially unresolved. The composite declared claim is therefore **indeterminate**, not valid.
