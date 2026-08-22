## `bssc-sum-capacity/marton-multiletter-finite-foundation-repair`

**Verdict: valid, with the stated conditional scope.**

**Required dependency transactions:** none.

The sole declared reference, `f6ea30479b9ca461294ba89a8a1a31c06ce59d08`, is corrective/provenance material only. None of its mathematical content is needed because the present contribution restates and proves the necessary finite-auxiliary arguments. Its terminal attestation is therefore not an accepted-state prerequisite.

### 1. Definition, finiteness, and elementary bounds

The admissible class is nonempty: taking \(U,V,W,X^n\) constant gives \(F_n=0\), so
\[
M_n^{\mathrm{fin}}(P)\ge 0.
\]

For every candidate law,
\[
\begin{aligned}
F_n
&\le I(W;Y^n)+I(U;Y^n\mid W)+I(V;Z^n\mid W)\\
&=I(U,W;Y^n)+I(V;Z^n\mid W)\\
&\le H(Y^n)+H(Z^n)\le 2n.
\end{aligned}
\]
The first inequality uses the \(Y^n\) branch of the minimum and discards
\(-I(U;V\mid W)\le0\). Since both outputs are binary, the entropy bound is correct. Thus \(M_n^{\mathrm{fin}}\) is a finite real number in \([0,2n]\).

### 2. Superadditivity

Take independent finite laws of lengths \(m\) and \(n\), and pair all corresponding auxiliaries. The resulting law remains finite and satisfies the required Markov chain for \(P^{\otimes(m+n)}\).

Independence gives exact additivity of
\[
I(U;Y\mid W),\qquad I(V;Z\mid W),\qquad I(U;V\mid W),
\]
and of the two common-information branches. The remaining inequality is
\[
\min\{A_m+A_n,B_m+B_n\}
\ge \min\{A_m,B_m\}+\min\{A_n,B_n\},
\]
which is valid because the right side is bounded above by both arguments of the minimum on the left. Applying this to arbitrarily near-optimal laws and sending the approximation error to zero establishes
\[
M_{m+n}^{\mathrm{fin}}\ge M_m^{\mathrm{fin}}+M_n^{\mathrm{fin}}.
\]

No optimizer or cardinality theorem is assumed.

### 3. Fekete limit

The sequence is finite-valued and superadditive. Fekete’s lemma therefore applies and yields
\[
\lim_{n\to\infty}\frac{M_n^{\mathrm{fin}}}{n}
=\sup_{n\ge1}\frac{M_n^{\mathrm{fin}}}{n}.
\]
The bound \(M_n^{\mathrm{fin}}\le2n\) also confirms that this limit is finite.

### 4. Conditional super-symbol achievability

Assume exactly the stated hypothesis (H-Marton). For a candidate law of positive value \(S=F_n\), put
\[
A=I(U,W;Y^n),\qquad B=I(V,W;Z^n).
\]
One has \(S\le A+B\). Hence
\[
R_1=\min\{A,S\},\qquad R_2=S-R_1
\]
are nonnegative, satisfy \(R_1\le A\), \(R_2\le B\), and have sum \(S\). Thus all three inequalities in (H-M) hold.

Applying (H-Marton) to the finite super-channel \(P^{\otimes n}\), then flattening each super-symbol code, preserves the induced channel law and average errors while dividing rates by \(n\). The supremum approximation argument consequently proves
\[
C_{\mathrm{sum}}(P)\ge \frac{M_n^{\mathrm{fin}}(P)}n.
\]
Taking the supremum over \(n\) gives the asserted lower bound by the Fekete limit. These are correctly presented as conditional conclusions; the contribution does not purport to prove (H-Marton).

### 5. Repeated witnesses and threshold statement

For \(k\) independent copies of one selected law, every private term and the penalty scale by \(k\), while
\[
\min\{kA,kB\}=k\min\{A,B\}.
\]
Thus the copied law has value exactly \(kS_n\), not merely at least that value.

Under (H-Marton), the normalized lower bound furnished by that selected law is \(S_n/n\). It exceeds \(L_{\mathrm{RTD}}\) exactly when
\[
S_n>nL_{\mathrm{RTD}}.
\]
Under the additional stated hypothesis (H-binary), \(M_1^{\mathrm{fin}}=L_{\mathrm{RTD}}\), so the same inequality is exactly strict improvement over the complete one-letter Marton sum supremum. No fixed-blocklength equality is used as a capacity converse.

### 6. RTD optimization and calculus

For \(q=\Pr[X=0]\), direct calculation from the channel matrices gives
\[
I(X;Y)=h_2(q/2)-q=J(q),\qquad I(X;Z)=J(1-q).
\]

For an RTD schedule \(W\), with conditional priors \(q_w\), the common-information terms are
\[
I(W;Y)=J(\bar q)-\mathbb E J(q_W),\qquad
I(W;Z)=J(1-\bar q)-\mathbb E J(1-q_W).
\]
The private contribution in each state is at most
\[
\max\{J(q_w),J(1-q_w)\}.
\]
Combining this with \(\min\{a,b\}\le(a+b)/2\) gives equation (14):
\[
\text{RTD sum}\le
\frac{J(\bar q)+J(1-\bar q)}2
+\frac12\mathbb E|D(q_W)|.
\]
Concavity and reflection symmetry imply
\[
J(\bar q)+J(1-\bar q)\le2J(1/2),
\]
so the upper bound is
\[
J(1/2)+\frac12\max_q|D(q)|.
\]

A fair schedule using priors \(q\) and \(1-q\), assigned respectively to \(Y\) and \(Z\), attains
\[
J(1/2)+\frac12D(q)
\]
when \(D(q)\ge0\). Antisymmetry of \(D\) shows this attains the absolute-value bound at a maximizer.

The derivative
\[
D'(q)=\frac12\log_2\frac{(2-q)(1+q)}{q(1-q)}-2
\]
is correct. Its sign is that of
\[
15q^2-15q+2,
\]
whose roots are
\[
q_\pm=\frac{15\pm\sqrt{105}}{30}.
\]
The derivative sign pattern, endpoint values, and antisymmetry establish that the global maximum occurs at \(q_-\). Substitution gives the claimed closed form. The endpoint and derivative-domain cases are handled separately and correctly.

### 7. Numerical attestation

The subject’s terminal attestation records a successful pinned Python execution and reports directed enclosures
\[
L_{\mathrm{RTD}}\in[
0.36164288442195461566344157815058700720798101072386055520371372980280073545\ldots,
\;
0.36164288442195461566344157815058700720798101072386055520371372980280073545\ldots],
\]
strictly inside the declared interval, with the corresponding doubled enclosure strictly inside the declared interval for \(2L_{\mathrm{RTD}}\).

Inspection of the supplied checker confirms that:

- the \(\sqrt{105}\) bracket is proved by exact rational square comparisons;
- all relevant entropy arguments lie strictly in \((0,1)\);
- arithmetic uses directed floor/ceiling contexts;
- correctly rounded `Decimal.ln` endpoint values are expanded outward;
- the doubled interval is checked independently.

Thus the attestation supports the two numerical interval assertions. Its structural string checks do not themselves prove the analytic claims, but those claims are independently established above. The attestation does not prove either external hypothesis, consistently with their explicit conditional status.
