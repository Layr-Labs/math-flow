## `bssc-sum-capacity/marton-multiletter-frontier-audit-2026`

**Verdict: INDETERMINATE**

The elementary multiletter reductions are largely correct, but the exact declared claim materially depends on two external theorems that are neither proved in the subject nor supplied as declared-reference evidence. The numerical decimal prefix is also not rigorously certified by the attested computation.

### 1. Definition and auxiliary-alphabet scope

The subject defines

\[
M_n(P)=\sup_{(U,V,W)-X^n-(Y^n,Z^n)} F_n(U,V,W,X^n)
\]

with the stated Marton objective. The proof subsequently says to “choose finite auxiliaries,” but the displayed definition does not explicitly restrict \(U,V,W\) to finite alphabets or provide a cardinality/finite-approximation theorem.

This matters because the invoked coding theorem is stated by the subject to apply to finite super-channels with finite auxiliaries. The argument is sound if \(M_n\) is, by definition, the supremum over finite auxiliaries. If arbitrary auxiliary spaces are included, an additional finite-approximation or cardinality argument is required and is absent.

### 2. Super-symbol capacity normalization

Conditional on the applicable private-message Marton coding theorem, the normalization is correct:

- An \(\ell\)-use code for the super-channel \(P^{\otimes n}\) is a code of blocklength \(\ell n\) for \(P\).
- A sum rate \(M_n-\epsilon\) per super-symbol becomes \((M_n-\epsilon)/n\) per original channel use.
- Taking \(\ell\to\infty\) and then \(\epsilon\downarrow0\) avoids any need for attainment of the supremum.

However, **Marton’s coding theorem itself is not proved in the subject or supplied through a declared reference**. The README explicitly acknowledges it as an external premise. Moreover, the precise theorem must establish achievability of this exact sum expression under the problem’s private-message and average-error conventions. That material obligation remains unresolved from the allowed evidence.

### 3. Superadditivity

The concatenation argument is correct, subject to a consistent definition of \(M_n\).

For independent \(m\)- and \(n\)-letter laws, the conditional mutual-information terms add. If

\[
A_r=I(W_r;Y^r),\qquad B_r=I(W_r;Z^r),
\]

then the common term obeys the universal inequality

\[
\min\{A_m+A_n,B_m+B_n\}
\ge \min\{A_m,B_m\}+\min\{A_n,B_n\}.
\]

Indeed, the right side is no larger than either \(A_m+A_n\) or \(B_m+B_n\). Thus epsilon-optimal laws give

\[
M_{m+n}\ge M_m+M_n.
\]

The verifier’s finite rational grid does not prove this universal inequality, but the preceding direct argument does.

### 4. Linear bounds and Fekete’s lemma

These steps are correct:

- Constant \(U,V,W\) give objective \(0\), hence \(M_n\ge0\).
- Dropping \(-I(U;V\mid W)\) and choosing the \(Y^n\) branch of the minimum gives
  \[
  \begin{aligned}
  F_n
  &\le I(W;Y^n)+I(U;Y^n\mid W)+I(V;Z^n\mid W)\\
  &=I(U,W;Y^n)+I(V;Z^n\mid W)\\
  &\le H(Y^n)+H(Z^n)\le 2n.
  \end{aligned}
  \]
- Hence \(M_n\) is finite and superadditive, so Fekete’s lemma yields
  \[
  \lim_{n\to\infty}\frac{M_n}{n}
  =\sup_{n\ge1}\frac{M_n}{n}.
  \]

The resulting capacity lower bound still depends on the unresolved Marton coding-theorem step.

### 5. Witness threshold and propagation

If \(S_n\) is the exact objective value of an \(n\)-letter Marton law, then its normalized lower bound is \(S_n/n\). Consequently it exceeds the one-letter value \(L_{\mathrm{RTD}}\) exactly when

\[
S_n>nL_{\mathrm{RTD}}.
\]

For \(k\) independent copies, all mutual-information terms scale by \(k\), including

\[
\min\{kA,kB\}=k\min\{A,B\},
\]

so the product witness has value exactly \(kS_n\). These algebraic assertions are correct.

The “if and only if” should be understood only for the direct normalized value of that witness. It does not say that a failed numerical certificate proves the underlying law cannot have a larger exact objective.

### 6. Identification \(M_1(P)=L_{\mathrm{RTD}}\)

This is a second unresolved external premise. The subject states that the classical binary-input Marton evaluation identifies

\[
M_1(P)=L_{\mathrm{RTD}},
\]

but explicitly says it does not re-prove that theorem. No reference transaction is declared for this claim. The problem statement identifies the benchmark lower endpoint as a randomized-time-division value within Marton’s inner bound, but it does not itself establish the stronger equality with the complete one-letter Marton optimum.

Therefore the claim’s interpretation of \(nL_{\mathrm{RTD}}\) as exactly the one-letter Marton benchmark is not affirmatively established by the supplied admissible evidence.

### 7. Exact RTD optimization

Given the asserted variational definition

\[
L_{\mathrm{RTD}}
=J(1/2)+\frac12\max_{q\in[0,1]}D(q),
\]

the calculus is correct:

\[
D'(q)
=\frac12\log_2\!\frac{(2-q)(1+q)}{q(1-q)}-2,
\]

and on \(0<q<1\),

\[
D'(q)>0
\iff 15q^2-15q+2>0.
\]

The roots are

\[
q_\pm=\frac{15\pm\sqrt{105}}{30}.
\]

Together with continuity, antisymmetry \(D(1-q)=-D(q)\), and the endpoint values, the derivative sign pattern establishes that \(q_-\) is the global maximizer. The resulting closed form is therefore correct conditional on the variational definition.

### 8. Decimal prefix

The attested verifier evaluates the closed form using 100-digit `Decimal` arithmetic and checks that its computed approximation begins with

\[
2L_{\mathrm{RTD}}
=0.723285768843909231326883156301174\ldots.
\]

But the checker does not use interval arithmetic, provide accumulated rounding-error bounds, or prove separation from the relevant decimal boundary. Its successful execution therefore establishes only that the particular high-precision computation produced the asserted prefix—not that the exact transcendental expression rigorously has those digits.

The warning that a displayed prefix is not a directed upper enclosure is itself correct.

### 9. Fixed-\(n\) equality is not a converse

This scope statement is correct. Establishing

\[
M_n=nL_{\mathrm{RTD}}
\]

for one fixed \(n\) supplies no universal upper bound on capacity and does not exclude another blocklength or a non-Marton coding construction.

### 10. Objective-attestation scope

The terminal attestation establishes that the pinned Python verifier exited successfully and that the locally encoded files had the printed hashes. It does **not** establish:

- Marton’s coding theorem;
- the binary-input theorem \(M_1(P)=L_{\mathrm{RTD}}\);
- finite-auxiliary sufficiency if arbitrary auxiliaries are included in the definition;
- a rigorous interval enclosure for the decimal prefix;
- the external August 2026 paper theorems.

The verifier itself expressly acknowledges several of these limitations. Its source-manifest and replay checks are unnecessary for the declared mathematical claim and do not resolve its missing premises.

### Dependencies

- **Declared references:** none.
- **Required dependencies among declared references:** none can be listed.
- **Unresolved external mathematical premises:** Marton’s applicable private-message coding theorem and the binary-input evaluation \(M_1(P)=L_{\mathrm{RTD}}\).

Because these necessary premises are not established by the subject or admissible declared-reference evidence, the exact claim cannot be marked valid.
