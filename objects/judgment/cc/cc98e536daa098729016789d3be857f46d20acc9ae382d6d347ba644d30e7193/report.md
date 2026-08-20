## `bssc-sum-capacity/fixed-pair-continuous-certificates-and-invariant-frontier`

**Verdict: INDETERMINATE**

### Dependencies

- **Declared references:** none.
- **Required dependencies among declared references:** none.
- **Missing essential premise:** the capacity converse relies on the mathematical validity and precise quantifiers of Gohari–Liu–Nair Theorem 9, including the six selected rows and the assertion that an arbitrary fixed auxiliary-receiver pair \(G,K\) may be used. That theorem is neither proved in the contribution nor supplied as a declared reference. It therefore cannot be treated as established from this packet.

The historical commit, authorship, and acceptance citations are provenance rather than mathematical dependencies.

### 1. Conditional converse derivation

Several internal parts of the argument are coherent:

- The stated \(K\) is exactly the input/output reflection of \(G\):
  \[
  1-0.826953249115544=0.173046750884456,\qquad
  1-0.206961624915382=0.793038375084618.
  \]
- For \(\epsilon=0.000173428163029\), all six displayed weights are nonnegative, and the rate coefficients algebraically sum to one for both \(R_1\) and \(R_2\).
- The posterior identities
  \[
  I(W;A)=I_A(q_0)-\mathbb E I_A(q_W),\qquad
  I(U;A\mid W)=\mathbb E I_A(q_W)-\mathbb E I_A(q_U)
  \]
  and their \(V,UW,VW\) analogues are correct for binary input.
- Retaining only the posterior mass, mean, and martingale constraints is indeed a relaxation. Thus affine majorants satisfying the stated global conditions (D1)–(D2) would give a valid weak-duality bound for every actual hierarchy.
- Conditional on the exact tensor audit and global line inequalities, the resulting prior bound has the form
  \[
  B(q_0)=c'_1\bigl(I_Y(q_0)+I_Z(q_0)\bigr)+\text{constant},
  \]
  because the auxiliary-channel prior coefficients and total affine slope cancel. Since \(c'_1\ge0\), this is concave and reflection-symmetric, so its maximum on \([0,1]\) is at \(q_0=1/2\).
- Selecting one branch from a minimum in an outer-bound row is legitimate if the theorem actually gives \(R\le\min\{A,B\}\), because then \(R\le A\) and \(R\le B\).
- Adding the nonnegative right side of the side condition \(0\le F\) to an upper-bound combination has the correct inequality direction.

These establish a sound **conditional** proof architecture. They do not establish that the six encoded rows are valid capacity-converse premises.

### 2. Missing verification of the outer-bound premise

The source files describe the six rows as copied from Theorem 9, but the packet supplies neither:

1. a proof of those rows as a converse for every achievable private-message rate pair;
2. the complete theorem statement and side conditions needed to check their applicability; nor
3. declared reference evidence against which the transcription can be audited.

The exact-Fraction checks only show that the program’s internally encoded rows combine into its internally encoded tensor. They do not prove that those rows faithfully transcribe the external theorem or that the theorem has the required intersection/union and auxiliary-channel quantifiers.

This is a material unresolved obligation for the claimed bound on \(C_{\rm sum}\).

### 3. Continuous numerical certificate

The verifier’s design is plausibly fail-closed:

- exact rational checks cover weights, tensor identities, reflections, curvature signs, and region ordering;
- the special convex and concave regions use mathematically valid tangent and endpoint bounds;
- the adaptive interval covers appear to partition all remaining portions of \([0,1]\);
- logarithms are expanded outward, and ordinary arithmetic uses directed contexts;
- endpoint entropy evaluations are treated separately.

No decisive source-level flaw is apparent in this structure. Nevertheless, **no terminal objective attestation is supplied**. The displayed `PASS` output and interval are self-reported subject evidence, not a pinned execution result. Static inspection does not independently establish that all 136 interval cells and all extremely small positive margins actually pass with the stated values.

Consequently, the exact enclosure
\[
U\in[
0.36929694596920284244271335135600317726937686320586339865039784778686683932875798,
0.36929694596920284244271335135600317726937686320586339865039784778686683932875818]
\]
remains computationally unverified in the supplied record.

If that enclosure were established, the headline rounding would be valid because its upper endpoint is strictly below
\[
0.369296945969202842443.
\]

### 4. Comparison with the repaired certificate

Numerically, the asserted final upper endpoint is strictly smaller than
\[
0.36929694655551972563539254207215942386102502532943886683678450695288358384488468,
\]
so the claimed strict improvement follows conditional on both certificates.

The repaired source does set the group-\(b\) intercept to \(10^{-33}\). However, the supplied repaired verifier operates with that positive intercept; it does not visibly perform the separately claimed zero-intercept evaluation. The negative enclosure for the zero-backoff gap appears only in the narrative certificate. Without an objective execution or an independently reproduced calculation, the statement that the frozen zero-intercept gap is strictly negative is unresolved.

### 5. Invariant representation

The exact algebraic portion is substantially supported:

- both row combinations have rate vector \((1,1)\);
- all weights are nonnegative for \(0\le\epsilon\le1/3\);
- the proposed invariant support has equal weights on the stated skew-paired rows;
- the encoded \(W,U,V\) tensors agree coefficientwise;
- the remaining root-level \(G,K\) residuals cancel after summing over the three groups, which is legitimate because all groups share the same prior \(q_0\).

Thus, conditional on the row definitions and skew-pairing convention, the functional identity is exact rather than numerical.

For
\[
(s_B,s_C,s_D,s_E,s_{N_0},s_{N_1},s_{F_0},s_{F_1})
=
\left(\frac{1-\epsilon}{2},0,\epsilon,0,0,0,0,\frac{1-\epsilon}{2}\right),
\]
the normalization is directly verified:
\[
2s_B+s_C+s_D+s_E=(1-\epsilon)+\epsilon=1.
\]

However, the mapping from the six row-pair weights to the named “rank-eight quotient” coordinates is asserted in comments and prose rather than derived from a supplied quotient definition or declared reference. Therefore the quotient-labeling portion is not fully established, even though the displayed normalization and tensor identity are internally consistent.

### 6. Provenance assertions

The claims that these are four previously accepted artifacts and that the files are byte-for-byte copies from specified commits cannot be checked from the supplied evidence: there are no source-commit byte attestations, judgment bundles, or terminal hash comparisons. These are provenance gaps and do not themselves undermine the conditional mathematics, but they prevent affirmation of the exact bundled claim.

### Conclusion

The packet presents a coherent fixed-pair weak-duality strategy and a credible exact invariant-tensor identity. It cannot be marked valid because the essential Theorem 9 converse premise is undeclared and unproved, the continuous computation has no objective execution attestation, the zero-backoff negativity is only reported narratively, and the provenance and quotient-map assertions are not independently verified. No decisive counterexample to the mathematical bound is exhibited, so **indeterminate**, rather than invalid, is the appropriate verdict.
