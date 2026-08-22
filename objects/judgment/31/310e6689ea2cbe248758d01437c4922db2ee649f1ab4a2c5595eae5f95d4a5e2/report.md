## `bssc-sum-capacity/two-letter-marton-marginal-correlation-pruning`

**Verdict: valid**

### Required dependencies

Both declared references are genuine mathematical dependencies, and their required portions are satisfied:

1. **`33a5944dca980bf94cc869c6c7dee2d04385ff58`** — required for
   \[
   \begin{aligned}
   M&\le I(S;Y^2)+2r(2-Q),\\
   M&\le I(S;Z^2)+2rQ,
   \end{aligned}
   \qquad
   M\le G(P_S)+2r.
   \]
   These inequalities are not independently reproved in the subject. The cited reference supplies a valid derivation from the one-letter support lines, the product-channel chain identity, and the Marton-to-UV reduction.

2. **`88a1004f309460f3ec1cacdae88d30f88559f9bc`** — required for the exact identification and certified enclosure of
   \[
   T=2L_{\mathrm{RTD}}.
   \]
   Only its unconditional RTD calculus and interval certificate are used. Neither `(H-Marton)` nor `(H-binary)` is needed for this claim.

No other dependency is required.

### Proof audit

#### 1. Exact decomposition of \(G\)

For either receiver, memorylessness gives
\[
H(Y_1,Y_2\mid X_1,X_2)
=H(Y_1\mid X_1)+H(Y_2\mid X_2),
\]
even when \(X_1,X_2\) are correlated. Therefore
\[
I(S;Y^2)=I(X_1;Y_1)+I(X_2;Y_2)-I(Y_1;Y_2),
\]
and analogously for \(Z^2\). With
\[
F(q)=\frac{I_Y(q)+I_Z(q)}2,
\]
this proves exactly
\[
G(P_S)=F(q_1)+F(q_2)-\frac12C_{\rm out}.
\]
No input-independence assumption is hidden here.

#### 2. Coordinate-marginal pruning

From the two imported rows and nonnegativity of output mutual information,
\[
M\le A(q_1)+A(q_2),\qquad
M\le A(1-q_1)+A(1-q_2),
\]
where
\[
A(q)=I_Y(q)+2r(1-q).
\]
The derivatives are correctly computed:
\[
A'(q)=1-\frac12\log_2\frac{1+q}{1-q}-2r,\qquad
A''(q)=-\frac1{\ln2(1-q^2)}<0.
\]
Using \(h_2(1/4)=2-\frac34\log_2 3\), the claimed maximizer
\[
q_{\max}=\frac{19}{35}
\]
indeed satisfies \(A'(q_{\max})=0\).

Thus, if \(q_i\le3/8\),
\[
M\le A(3/8)+A(19/35)<0.722032<T.
\]
Applying the reflected bound similarly excludes \(q_i\ge5/8\). Hence
\[
q_1,q_2\in(3/8,5/8).
\]
The stated weaker inclusion in \((7/20,13/20)\) follows because
\[
\frac38>\frac7{20},\qquad \frac58<\frac{13}{20}.
\]

#### 3. Output-correlation bound

The derivative
\[
F'(q)=\frac14\log_2\frac{(2-q)(1-q)}{q(1+q)}
\]
has the asserted sign, so \(F(q)\le F(1/2)\). Therefore \(M>T\) implies
\[
C_{\rm out}<4F(1/2)+4r-2T.
\]
The directed computation encloses the right-hand side near
\[
0.04365345798524445,
\]
strictly below
\[
\frac7{160}=0.04375<0.044.
\]
Thus the claimed strict output-correlation bound follows.

#### 4. Input-covariance consequence

For both receivers the output-one probability is affine in \(X\) with slope \(1/2\). Conditional independence across channel uses therefore yields
\[
\operatorname{Cov}(R_1,R_2)=\frac14c_{\rm in}.
\]
For a binary pair, the four deviations of its joint table from the product table are \(\pm\operatorname{Cov}(R_1,R_2)\), hence
\[
\left\|P_{R_1R_2}-P_{R_1}P_{R_2}\right\|_{\rm TV}
=\frac12|c_{\rm in}|.
\]
Pinsker’s inequality in bits gives, for each receiver,
\[
I(R_1;R_2)\ge \frac{c_{\rm in}^2}{2\ln2}.
\]
Summing over \(Y\) and \(Z\),
\[
C_{\rm out}\ge\frac{c_{\rm in}^2}{\ln2}.
\]
Combining this with \(C_{\rm out}<7/160\) gives
\[
|c_{\rm in}|<\sqrt{\frac7{160}\ln2}<\frac7{40},
\]
with the final rational comparison certified by directed arithmetic.

#### 5. Sum-marginal pruning

Concavity of \(I_Y\) gives
\[
I(S;Y^2)\le I_Y(q_1)+I_Y(q_2)\le2I_Y(Q/2),
\]
so
\[
M\le B(Q):=2I_Y(Q/2)+2r(2-Q).
\]
The derivatives
\[
B'(Q)=1-\frac12\log_2\frac{1+Q/2}{1-Q/2}-2r,
\qquad
B''(Q)<0
\]
are correct. The certificate establishes \(B'(17/20)>0\) and
\[
B(17/20)<0.721880<T.
\]
Concavity then makes \(B\) increasing on \([0,17/20]\), excluding \(Q\le17/20\). Applying the reflected row to \(2-Q\) excludes \(Q\ge23/20\). Therefore
\[
\frac{17}{20}<Q<\frac{23}{20}.
\]

#### 6. Reflected/transposed family

For
\[
P(00)=P(11)=\alpha,\qquad
P(01)=P(10)=\frac12-\alpha,
\]
both input marginals are fair, and direct channel evaluation gives the displayed \(Y^2\) table. The \(Z^2\) table is its complemented permutation, so the two output mutual informations agree.

The derivative
\[
J_{\rm out}'(\alpha)
=\frac14\log_2\frac{\alpha(2+\alpha)}{(1-\alpha)^2}
\]
changes sign only at \(\alpha=1/4\): it is negative below and positive above. Directed evaluation proves
\[
2J_{\rm out}(1/8)>\frac7{160},\qquad
2J_{\rm out}(5/13)>\frac7{160}.
\]
Monotonicity and the already-proved \(C_{\rm out}<7/160\) therefore force
\[
\frac18<\alpha<\frac5{13}.
\]

### Objective-attestation audit

The subject attestation records a successful pinned Python 3.13 execution. Its script checks:

- the exact rational bracket for \(\sqrt{105}\);
- the directed enclosure of \(T=2L_{\mathrm{RTD}}\);
- the coordinate and sum-envelope inequalities;
- the \(7/160\) and \(7/40\) comparisons;
- the two endpoint correlations for the \(\alpha\)-family.

It does **not** by itself prove the information-theoretic identities or imported Marton inequalities. Those analytic obligations are supplied by the written arguments and the two required references and have been checked above.

### Scope

The conclusion is only a set of necessary conditions for a finite-auxiliary, unnormalized two-letter Marton value satisfying \(M>T\). It neither constructs such a gain nor rules one out and does not constitute a capacity converse.
