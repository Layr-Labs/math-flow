## `bssc-sum-capacity/theorem9-private-row-audit`

**Verdict: Indeterminate**

**Required declared dependencies:** None were declared. The cited Gohari–Liu–Nair manuscript is not supplied as declared reference evidence, so it cannot be used to certify correspondence with the primary source.

### 1. Primary-source transcription fidelity is not established

The claim asserts that the bounded transcription faithfully reproduces Theorem 9’s:

- factorization,
- equations (19a)–(19p), and
- two side conditions.

The supplied terminal attestation ran:

```text
verify_specialization.py
```

with no `--source-pdf` argument. Consequently, it did **not** authenticate or inspect the claimed PDF bytes. The script only reads the locally authored `theorem9_spec.json` and compares that specification with another locally authored construction. It does not compare either artifact with the external manuscript, and it does not check the factorization at all.

The PDF URL, byte count, and claimed SHA-256 are metadata asserted by the contribution, not authenticated primary-source evidence. Thus the exact source-fidelity portion remains materially unresolved.

### 2. The internal 30-row comparison is correct relative to the local transcription

Conditional on treating `theorem9_spec.json` as the source system, the row expansion is sound:

- (19a) and (19b): \(3+3\) branches;
- (19c)–(19j): four three-branch inequalities, giving \(12\) rows;
- (19k) and (19l): \(2+2\) branches;
- (19m)–(19p): \(4\) rows.

This totals \(26\). Splitting each interval condition \(0\le L\le R\) into \(L\ge0\) and \(R-L\ge0\) adds four rows, yielding \(30\).

The equivalence

\[
L\le A+\min_i b_i
\iff
L\le A+b_i\quad\text{for every }i
\]

is valid for these finite minima. The checker compares rate coefficients and information-term coefficients exactly after applying only the valid chain rules

\[
I(U,W;A)=I(W;A)+I(U;A\mid W),
\qquad
I(V,W;A)=I(W;A)+I(V;A\mid W).
\]

The attested execution therefore establishes exact equality between the JSON-derived rows and `make_path_rows()` under that normalization.

However, the four side-condition rows in `make_path_rows()` are explicitly hardcoded rather than derived from the generic path loops. Thus the execution establishes equality of two local encodings, but not a fully independent generic derivation of all 30 rows.

### 3. The single-output audit supports the marginalization argument

Relative to the local transcription, the checker exhaustively collects the output-bearing terms and obtains the asserted counts:

\[
Y:3,\qquad G:12,\qquad K:12,\qquad Z:3.
\]

There is no term involving the joint output \((G,K)\), nor any term conditioning one receiver output on another.

For any auxiliary subtuple \(D\) appearing in a row, the stated factorization gives

\[
p(d,x,g)
=
p_X(x)p_{D\mid X}(d\mid x)\bar T_{G\mid X}(g\mid x),
\]

and analogously for \(K\). Replacing the original auxiliary-receiver law by

\[
T'_{G,K\mid X,Y,Z}
=
\bar T_{G\mid X}\bar T_{K\mid X}
\]

therefore preserves every marginal law needed for a single-\(G\) or single-\(K\) mutual-information term. It also leaves the \(Y\) and \(Z\) terms unchanged. Hence every locally transcribed row and side condition is preserved. The reverse containment follows because such input-only product channels are members of the originally admitted class.

This argument is mathematically valid **conditional on the completeness and correctness of the transcription and factorization**.

### 4. The value inequalities are set-inclusion consequences, with an empty-feasible-set gap

Whenever the quantities are defined,

\[
V_Q(G,K)\le V(1/2;G,K)\le \sup_{q\in[0,1]}V(q;G,K)=B(G,K)
\]

follows directly because the \(Q\)-supported hierarchies form a restriction of the fair-prior feasible set.

There is, however, an unstated domain convention. For example, take

\[
Q=\{1/2\}.
\]

Then every admitted posterior in the definition equals \(1/2\). The \(Z,K\) side condition becomes

\[
0\le c-k\le 0,
\]

because its right side is zero; similarly the \(Y,G\) condition forces \(c-g=0\). Thus for channels with \(g\ne c\) or \(k\ne c\), the \(Q\)-supported feasible set is empty. The contribution does not specify whether \(V_Q\) is extended-real valued with \(\sup\varnothing=-\infty\). Without that convention, \(V_Q(G,K)\) need not be defined for every stated \(Q,G,K\). This prevents unconditional acceptance of the displayed general inequality as written.

### 5. The \(Q_0\) channel-reduction argument is otherwise sound

For \(S-X-A\) at fair prior,

\[
I(S;A)=J_A(1/2)-\mathbb E J_A(q_S),
\qquad
I(X;A\mid S)=\mathbb E J_A(q_S),
\]

and consequently

\[
I(U;A\mid W)
=
\mathbb E J_A(q_W)-\mathbb E J_A(q_{U,W}),
\]

with the analogous identity for \(V\). These identities cover all locally audited term types.

For

\[
Q_0=\{0,1/2,1\},
\]

one has \(J_A(0)=J_A(1)=0\) for every channel. Hence every row depends on receiver \(A\) only through \(J_A(1/2)\). For the BSSC,

\[
J_Y(1/2)=J_Z(1/2)=h_2(1/4)-\tfrac12=c.
\]

Thus the row values depend on \(Y,G,K,Z\) only through

\[
(c,g,k,c).
\]

The auxiliary-law domain and the \(Q_0\)-support condition themselves do not depend on the receiver transition laws, so two channels with the same \(g\) and \(k\) induce the same optimization problem.

Unlike the general \(Q\) case, the \(Q_0\) feasible set is nonempty: taking every \(U_j,V_j,W_j\) deterministically equal to \(X\) makes all relevant posteriors lie in \(\{0,1\}\), satisfies both side conditions, and permits \(R_1=R_2=0\). Therefore the claimed channel-invariance of \(V_{Q_0}(G,K)\) is supported.

### 6. Exact scope of the attestation

The passed execution establishes only that the committed checker:

- loaded the committed JSON transcription;
- expanded its minima and side conditions;
- generated 30 local rows;
- found exact normalized equality with `make_path_rows()`;
- matched the locally hardcoded term whitelist; and
- exited successfully.

It does **not** establish:

- authenticity or contents of the external PDF;
- fidelity of the JSON or Markdown transcription to that PDF;
- correctness of the stated factorization as a transcription of Theorem 9;
- Theorem 9 itself;
- the marginalization proof or value-reduction proof; or
- any numerical capacity bound.

Because primary-source fidelity is an explicit part of the compound claim and remains unauthenticated, and because the general \(V_Q\) definition lacks an empty-set convention, the exact declared claim cannot be marked valid.
