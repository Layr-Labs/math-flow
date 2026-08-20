# `bssc-sum-capacity/theorem9-private-row-audit`

**Verdict: INDETERMINATE**

The internally supplied algebra largely supports the specialization, marginalization, and \(Q_0\)-reduction arguments. However, the exact compound claim cannot be accepted because fidelity to the external primary source is not established by the supplied evidence. There is also an unaddressed empty-feasible-set issue in the general definition of \(V_Q\).

## 1. Primary-source transcription is not verifiable from the packet

The claim asserts that `SOURCE_TRANSCRIPTION.md` “faithfully reproduces” Gohari–Liu–Nair Theorem 9, including:

- its factorization;
- equations (19a)–(19p);
- both side conditions.

No copy of the cited PDF, independently authenticated extract, or declared reference evidence is supplied. The URL, byte count, creation date, and SHA-256 digest identify alleged source bytes but do not expose their mathematical contents.

The optional `--source-pdf` logic in `verify_specialization.py` only verifies the size and digest of a separately supplied PDF. It does **not** extract equations from that PDF and compare them to `SOURCE_TRANSCRIPTION.md` or `theorem9_spec.json`. Thus even a successful invocation would authenticate bytes, not transcription fidelity. The no-argument verifier compares two local encodings whose source-facing correctness remains unproved.

Taking Theorem 9’s validity as a premise does not by itself establish that the displayed local transcription is its exact statement. This is a material unresolved obligation because all later audits are conditional on that transcription.

## 2. Conditional audit of the 30-row specialization

Relative to the supplied transcription, the row count and expansion logic are correct:

- (19a), (19b), (19c)–(19d), (19e)–(19f), (19g)–(19h), and (19i)–(19j) each have three minimum branches, giving \(6\cdot3=18\) rows.
- (19k) and (19l) each have two branches, giving \(4\) rows.
- (19m)–(19p) give four singleton rows.
- Hence there are \(18+4+4=26\) rate/nonnegativity rows.
- Each interval condition \(0\le L\le R\) is equivalent to \(L\ge0\) and \(R-L\ge0\), giving four further rows.

Thus the total is \(30\).

The transformation
\[
L\le A+\min_i b_i
\quad\Longleftrightarrow\quad
L\le A+b_i\ \text{for every }i
\]
is valid. The code compares rate coefficients and normalized information terms, using only
\[
I(U,W;A)=I(W;A)+I(U;A\mid W)
\]
and its \(V\)-analogue. Inspection of the JSON and code reveals no contradiction in this conditional row comparison.

This verifies equivalence between the two **local encodings**, but not that either encoding faithfully represents the unavailable primary source.

## 3. Single-output marginalization argument

Conditional on the displayed term list being exhaustive, this part is mathematically sound.

For any subtuple \(D\) of one auxiliary group, the asserted factorization gives \(D-X-(Y,Z,G,K)\). Marginalizing an arbitrary \(T_{G,K\mid X,Y,Z}\) yields
\[
p(d,x,g)
 =p_X(x)p_{D\mid X}(d\mid x)
   \sum_{y,z,k}T_{Y,Z\mid X}(y,z\mid x)
                  T_{G,K\mid X,Y,Z}(g,k\mid x,y,z)
 =p_X(x)p_{D\mid X}(d\mid x)\bar T_{G\mid X}(g\mid x).
\]
The same argument applies to \(K\). Replacing the auxiliary receiver law by
\[
T'_{G,K\mid X,Y,Z}
 =\bar T_{G\mid X}\bar T_{K\mid X}
\]
therefore preserves every \((D,X,G)\) and \((D,X,K)\) marginal, while the \(Y\) and \(Z\) marginals are unchanged.

Every information quantity in the supplied transcription involves only one receiver output at a time; no term contains \((G,K)\) jointly or conditions one receiver output on another. Hence all displayed rows and side conditions are preserved term by term. Conversely, an input-only product law is a special admissible auxiliary-receiver law.

The limitation is that exhaustiveness has only been checked against the local transcription, whose fidelity to Theorem 9 remains unresolved.

## 4. The inequalities involving \(V_Q,V\), and \(B\)

Whenever the relevant suprema are defined,
\[
V_Q(G,K)\le V(1/2;G,K)
\]
follows from restriction of the feasible auxiliary hierarchies, and
\[
V(1/2;G,K)\le\sup_{q\in[0,1]}V(q;G,K)=B(G,K)
\]
is immediate.

There is, however, an omitted empty-set convention. A \(Q\)-supported feasible hierarchy need not exist for every finite \(Q\ni1/2\). For example, take
\[
Q=\{1/2\}
\]
and let \(G=X\) be noiseless. Then every allowed posterior \(P(X=1\mid V_a,W_a)\) equals \(1/2\), so
\[
I(X;Y\mid V_a,W_a)=c,\qquad
I(X;G\mid V_a,W_a)=1.
\]
The left part of the \(Y,G\) side condition would require
\[
0\le c-1,
\]
which is false because
\[
c=h_2(1/4)-\tfrac12<1.
\]
Thus the restricted feasible set is empty in this example.

If the contribution adopts the extended-real convention \(\sup\varnothing=-\infty\), the displayed inequality remains true. But that convention is not stated; as a real-valued supremum, \(V_Q(G,K)\) is then undefined. This prevents unconditional acceptance of the exact assertion that the local definitions themselves give the inequality for every stated \(Q,G,K\).

## 5. \(Q_0\)-dependence and well-definedness of \(V_0(g,k)\)

The channel-dependence argument is correct under the supplied factorization. For \(S-X-A\) at fair prior,
\[
I(S;A)=J_A(1/2)-\mathbb E[J_A(q_S)],
\qquad
I(X;A\mid S)=\mathbb E[J_A(q_S)].
\]
Likewise,
\[
I(U;A\mid W)
 =\mathbb E[J_A(q_W)]-\mathbb E[J_A(q_{U,W})],
\]
and similarly for \(V\).

For every channel,
\[
J_A(0)=J_A(1)=0.
\]
Consequently, on
\[
Q_0=\{0,1/2,1\},
\]
all audited information terms depend on channel \(A\) only through \(J_A(1/2)\). For the physical BSSC,
\[
J_Y(1/2)=J_Z(1/2)
=h_2(1/4)-\tfrac12=c,
\]
so the receiver-channel dependence is only through
\[
(c,g,k,c).
\]
Therefore two choices of \(G,K\) having the same midpoint values \(g,k\) produce identical row values for every fixed \(Q_0\)-supported hierarchy, and hence identical feasible sets and objective suprema.

Unlike the general \(Q\) case, \(Q_0\)-feasibility can be exhibited: take all \(W\)'s constant, take \(U_a,V_c\) constant, and take \(V_a,U_b,V_b,U_c=X\). All relevant posteriors lie in \(Q_0\), both side conditions reduce to zero, and the 26 displayed right-hand sides reduce to nonnegative combinations of \(0,g,k\). Thus the restricted feasible set is nonempty.

Accordingly, the \(V_0(g,k)\) reduction is supported **conditional on the accuracy and exhaustiveness of the source transcription**.

## Conclusion

The local mathematical reductions are substantially supported, but the declared claim is an all-or-nothing conjunction. Its primary-source fidelity component is unsupported by the supplied bounded evidence, and the general \(V_Q\) definition lacks an empty-supremum convention. Therefore the exact claim cannot be marked valid.
