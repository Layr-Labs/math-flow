## `bssc-sum-capacity/theorem9-render-complete-audit`

**Verdict: indeterminate**

The algebraic and information-theoretic parts of the contribution are largely supportable conditional on the stated transcription and factorization. However, the exact source-fidelity and “render-complete semantic audit” portion is not affirmatively established by the supplied evidence. Because the declared claim is conjunctive and all-or-nothing, this unresolved material obligation prevents a valid verdict.

### 1. Primary-source fidelity is not verifiable from the supplied packet

The claim requires exact agreement between the committed `GK-outer.pdf` and `theorem9_spec.json`. But the evidence supplied here does not include:

- the bytes of `GK-outer.pdf`;
- an independently authenticated copy of those bytes;
- the output of a successful governed verifier execution; or
- a signed or otherwise auditable verifier attestation.

`verification.json` merely specifies an entrypoint and environment. It is not evidence that the verifier ran successfully on the claimed PDF. The README’s assertion that a trusted attestation exists cannot substitute for the absent attestation.

Consequently, none of the following runtime-dependent facts can be checked from the evidence:

- that the PDF has the claimed byte length and SHA-256 digest;
- that its xref and object structure match the hard-coded profile;
- that pages 14–15 contain the claimed glyph stream;
- that all equation and factorization comparisons pass; or
- that the final 30-row comparison passes on the committed files.

The human-readable `SOURCE_TRANSCRIPTION.md` does not resolve this issue: it is itself part of the subject contribution and is not independent evidence of what the absent PDF contains.

### 2. The supplied renderer also leaves an unresolved glyph-semantics obligation

Even conditional on a successful run, the assertion that the audit establishes the **complete visible mathematical statement** is stronger than what the supplied code affirmatively proves.

In particular:

- `_type1_charstrings` decrypts the Type1 eexec section only far enough to inventory CharString names. It does not decode and execute each encrypted Type1 CharString or verify the path painted by a named glyph.
- `glyph_name_unicode` identifies a glyph by its declared name, and the code checks agreement with ToUnicode. A glyph named `plus`, with ToUnicode `+`, is not thereby proved to paint a plus sign.
- The font-program SHA-256 manifest pins bytes but does not, by itself, establish the visual semantics of those bytes. No independent proof or certificate connecting the listed hashes to the claimed glyph outlines is supplied.
- Glyph rectangles are computed from the font-wide declarative `FontBBox`, not from the actual CharString outline. Thus the code does not itself prove actual painted-shape containment, clipping, or nonoverlap.
- The geometry digest binds the extractor’s glyph metadata and those derived rectangles; it is not a rendering or outline-semantic certificate.

For one fixed benign PDF, these concerns might be discharged by an independently reviewed font-program certificate, but no such evidence is included. Thus the description “fail-closed, render-complete semantic audit” is not affirmatively justified by the supplied artifacts.

### 3. Algebraic expansion to 30 rows is correct conditional on the transcription

Given the equations in `SOURCE_TRANSCRIPTION.md` and `theorem9_spec.json`, the row count is correct:

- six three-branch constraints, (19a)–(19j), give \(6\cdot3=18\) rows;
- (19k) and (19l) give \(2+2=4\) rows;
- (19m)–(19p) give four rows.

Hence there are \(18+4+4=26\) rows from (19a)–(19p). Each side condition
\[
0\le L\le R
\]
is equivalent to the two scalar inequalities
\[
L\ge 0,\qquad R-L\ge0,
\]
so the two side conditions add four rows, for a total of 30.

Likewise,
\[
L\le A+\min_i b_i
\]
is exactly equivalent to the family \(L\le A+b_i\) over all branches. Setting \(R_0=0\) produces the rate coefficients encoded in the specification. The only normalization used in the row comparison,
\[
I(U,W;A)=I(W;A)+I(U;A\mid W),
\]
and its \(V\)-analogue, is valid.

This verifies the algebraic method conditional on the transcription, but it does not establish that the transcription is what the absent source PDF states or that the claimed verifier execution succeeded.

### 4. Product marginalization is mathematically sound conditional on the factorization and term inventory

Assume the stated factorization
\[
p_Xp_{U_a,V_a,W_a|X}p_{U_b,V_b,W_b|X}
p_{U_c,V_c,W_c|X}T_{Y,Z|X}T_{G,K|X,Y,Z}.
\]

For any subtuple \(D\) of one auxiliary group,
\[
p(d,x,g)
 =p_X(x)p_{D|X}(d|x)
   \sum_{y,z,k}T_{Y,Z|X}(y,z|x)T_{G,K|X,Y,Z}(g,k|x,y,z)
 =p_X(x)p_{D|X}(d|x)\bar T_{G|X}(g|x).
\]
The analogous identity holds for \(K\). Replacing the original auxiliary channel by
\[
T'_{G,K|X,Y,Z}(g,k|x,y,z)
 =\bar T_{G|X}(g|x)\bar T_{K|X}(k|x)
\]
therefore preserves every joint law involving \(X\), one auxiliary subtuple, and one of \(G\) or \(K\). It leaves the \(Y\) and \(Z\) laws unchanged.

The supplied transcription contains only single-output information terms and no term involving the joint output \((G,K)\), conditioning one output on another, or simultaneously coupling an auxiliary with both outputs. Therefore, conditional on the completeness of that term inventory, every displayed row and side condition is preserved. The reverse inclusion is immediate because an input-only product channel is a special case of an admitted \(T_{G,K|X,Y,Z}\).

### 5. The extended-real inequalities are valid

By definition, \(V_Q(G,K)\) restricts the feasible auxiliary hierarchies used in \(V(1/2;G,K)\). Hence, including the empty-feasible-set convention,
\[
V_Q(G,K)\le V(1/2;G,K).
\]
Since \(1/2\in[0,1]\),
\[
V(1/2;G,K)\le \sup_{q\in[0,1]}V(q;G,K)=B(G,K).
\]
No attainment or interchange of suprema and infima is needed.

### 6. The \(Q_0\) reduction is valid conditional on the audited term list

For \(S-X-A\) under the fair prior,
\[
I(S;A)=J_A(1/2)-\mathbb E[J_A(q_S)],
\qquad
I(X;A\mid S)=\mathbb E[J_A(q_S)].
\]
Consequently,
\[
I(U;A\mid W)
 =\mathbb E[J_A(q_W)]-\mathbb E[J_A(q_{U,W})],
\]
and similarly for \(V\).

For \(Q_0=\{0,1/2,1\}\),
\[
J_A(0)=J_A(1)=0.
\]
Thus every listed term depends on channel \(A\) only through \(J_A(1/2)\); the remaining coefficients are posterior-event probabilities determined solely by the auxiliary law. The physical BSSC midpoint values satisfy
\[
J_Y(1/2)=J_Z(1/2)
=h_2(1/4)-\frac12=:c,
\]
while the auxiliary-channel values are \(g=J_G(1/2)\) and \(k=J_K(1/2)\). Therefore two receiver pairs with the same \((g,k)\) induce identical row values for every fixed \(Q_0\)-supported auxiliary hierarchy. This proves the claimed channel-independence of \(V_{Q_0}(G,K)\), conditional on completeness of the term list.

### 7. Finiteness of \(V_0\) is correctly justified

At fair input, choose
\[
W_a=W_b=W_c=X
\]
and all \(U_j,V_j\) constant. This satisfies the required product factorization and is \(Q_0\)-supported. All conditional terms given \(W_j=X\) vanish, all cross-group same-output differences cancel, and both side conditions become \(0\le0\le0\). The zero rate pair is therefore feasible. Also,
\[
c=h_2(1/4)-\frac12
=\frac34\log_2\frac43>0.
\]

The branch-zero individual-rate rows give
\[
R_1\le I(U_a,W_a;Y)\le H(Y)\le1,
\qquad
R_2\le I(V_c,W_c;Z)\le H(Z)\le1.
\]
With \(R_1,R_2\ge0\), every feasible sum lies in \([0,2]\). Thus the \(Q_0\) value is nonempty, bounded, and a finite real number.

### Conclusion

The row algebra, marginalization argument, extended-real inequalities, and \(Q_0\) reduction are correct conditional on the stated transcription and factorization. Nevertheless, the declared claim additionally asserts exact primary-source and render-complete semantic certification. The actual PDF and verifier attestation are absent, and the supplied renderer does not itself certify Type1 glyph-outline semantics. Those are material unresolved obligations, so the exact all-or-nothing claim cannot be accepted as valid.
