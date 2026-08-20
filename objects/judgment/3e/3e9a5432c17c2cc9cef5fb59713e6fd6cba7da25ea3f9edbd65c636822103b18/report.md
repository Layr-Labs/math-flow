## `bssc-sum-capacity/fixed-pair-upper-bound-attested`

**Verdict: VALID, with the claim’s explicit conditional scope.**

The claim is valid assuming the Gohari–Liu–Nair Theorem 9 premise exactly as encoded in the declared dependency. Nothing in the supplied evidence authenticates that external theorem or its transcription, and the verdict does not do so.

### Required dependency

- **Required:** `e3c1036ca607539a5ebcddf3058e6014ac5c1cd9`
  - Its necessary role is limited to supplying the assumed outer-bound interface and identifying the six displayed inequalities as constraints obeyed by every achievable private-message rate pair for the fixed auxiliary receivers.
  - Its broader product-marginal reduction, \(Q_0\) discussion, and provenance material are not necessary for this fixed-pair certificate.

No historical Yukon transactions or prior numerical/grid artifacts are required dependencies.

### Audit of the mathematical reduction

1. **Auxiliary channels are admissible.**  
   All four exact decimal probabilities lie in \([0,1]\). They also satisfy exactly
   \[
   K_0=1-G_1,\qquad K_1=1-G_0,
   \]
   so the claimed reflection relation is correct.

2. **The six rows match the declared premise system.**  
   Direct comparison with `theorem9_spec.json` confirms the labels and terms:
   \[
   \mathrm{R1A}(1),\ \mathrm{R2T}(1),\ \mathrm{SR}(1,C),\
   \mathrm{SL}(2,U),\ \mathrm{SR}(2,U),\
   \mathrm{F\_Y\_right\_minus\_left}.
   \]
   In particular, the last row is a nonnegative slack from the \(Y,G\) side condition and hence may be added with a nonnegative multiplier.

3. **Dual weights are nonnegative and normalize the rates.**  
   With \(e=0.000173428163029\), the weights are
   \[
   e,\ e,\ e,\ \frac12-\frac e2,\ \frac12-\frac{3e}{2},\ e.
   \]
   They are all positive. Exact rational summation gives coefficient \(1\) on both \(R_1\) and \(R_2\). Thus their weighted sum is a legitimate upper bound on \(R_1+R_2\).

4. **The posterior tensor reduction is exact.**  
   Expanding every mutual information using
   \[
   I(W;A)=I_A(q_0)-\mathbb E I_A(q_W),
   \]
   and the analogous \(U,V,UW,VW\) identities yields exactly the three displayed group tensors. The prior coefficients reduce to
   \[
   c_1'\bigl(I_Y(q_0)+I_Z(q_0)\bigr),
   \]
   with zero total coefficients on \(I_G(q_0)\) and \(I_K(q_0)\). The exact-Fraction audit confirms all cancellations.

5. **Weak duality applies to every finite auxiliary hierarchy.**  
   For each \(W\)-state,
   \[
   \mathbb E[q_{UW}\mid W]=\mathbb E[q_{VW}\mid W]=q_W.
   \]
   Since each inner majorant is affine in the posterior variable, its conditional expectation equals its value at \(q_W\). The outer affine majorant can then be averaged without any strong-duality, attainment, or minimax assumption.

6. **The certificate covers the full continuous posterior domain.**
   - For groups \(a\) and \(c\), the exact curvature numerator
     \[
     S(q)=a(1-a)-d^2+d(1-2a)q
     \]
     has the checked signs and ordering needed for the concave/convex tangent and endpoint arguments. Group \(c\) follows by exact reflection.
   - For group \(b\), exact rational positivity of the relevant quadratic curvature numerators establishes the contact-window convexity.
   - All remaining portions of \([0,1]\) are covered by outward-directed interval subdivision, not by a sampled grid. The derivative-based cell bounds are valid interval mean-value bounds, and endpoint cells are handled without invoking singular physical-channel derivatives.
   - The successful execution covered 136 regular cells with maximum depth 30; unresolved cells, excessive depth, or budget exhaustion would have caused failure.

7. **All input priors are covered.**  
   The affine slopes from groups \(a\) and \(c\) cancel, and the group-\(b\) inner lines have constant sum. The remaining prior-dependent term is a positive multiple of
   \[
   I_Y(q_0)+I_Z(q_0).
   \]
   This function is concave in \(q_0\) and reflection-symmetric because \(I_Z(q)=I_Y(1-q)\). Therefore its global maximum on \([0,1]\) occurs at \(q_0=\tfrac12\), including the boundary priors.

8. **Numerical enclosure and rounding are correct.**  
   Directed interval evaluation encloses the exact weak-duality value \(U\) in
   \[
   \begin{aligned}
   [&0.36929694596920284244271335135600317726937686320586339865039784778686683932875798,\\
    &0.36929694596920284244271335135600317726937686320586339865039784778686683932875818].
   \end{aligned}
   \]
   Its upper endpoint is strictly below
   \[
   0.369296945969202842443,
   \]
   so the stated rounded upper bound follows.

### Attestation scope

The subject attestation establishes that the pinned no-argument `verify.py` execution under the specified Python 3.13 standard-library verifier:

- completed successfully;
- passed the exact row and tensor checks;
- passed the continuous interval certificate and all-prior reduction;
- reproduced the same evidence under three hostile ambient Decimal contexts; and
- produced exactly the claimed interval.

The reference attestation similarly establishes exact agreement of the encoded premise specialization with the generated 30-row system. Neither attestation authenticates the external manuscript or proves Theorem 9 itself.

### Accepted conclusion

Conditioned exactly as stated,
\[
\boxed{C_{\mathrm{sum}}\le 0.369296945969202842443.}
\]

This establishes only the fixed-receiver-pair converse certificate; it does not establish optimality of the receiver pair or dual face, a matching achievable rate, or the exact sum-capacity.
