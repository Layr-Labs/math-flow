# Finite-auxiliary Marton multiletter foundation and directed RTD threshold

## Claim and exact scope

Let \(P\) be the governed half-skew BSSC.  For each \(n\geq1\), let
\(\mathcal A_n^{\mathrm{fin}}\) be the collection of all choices of **finite**
alphabets \(\mathcal U,\mathcal V,\mathcal W\) and all joint laws

\[
p(u,v,w,x^n)P^{\otimes n}(y^n,z^n\mid x^n)
\]

on those alphabets.  Equivalently, every member obeys
\((U,V,W)-X^n-(Y^n,Z^n)\).  Define

\[
\begin{aligned}
F_n(U,V,W,X^n)
={}&\min\{I(W;Y^n),I(W;Z^n)\}\\
&+I(U;Y^n\mid W)+I(V;Z^n\mid W)-I(U;V\mid W),\\
M_n^{\mathrm{fin}}(P)
={}&\sup_{\mathcal A_n^{\mathrm{fin}}}F_n(U,V,W,X^n).
\end{aligned}
\tag{1}
\]

The superscript is retained here to make the finite-auxiliary scope explicit;
no statement about arbitrary measurable auxiliary spaces is needed or made.
Because a constant law has value zero and the BSSC outputs are binary,

\[
0\leq M_n^{\mathrm{fin}}(P)\leq2n.
\tag{2}
\]

The following algebraic conclusions are unconditional:

\[
M_{m+n}^{\mathrm{fin}}(P)
\geq M_m^{\mathrm{fin}}(P)+M_n^{\mathrm{fin}}(P),
\qquad m,n\geq1,
\tag{3}
\]

and hence, by Fekete's lemma,

\[
\lim_{n\to\infty}\frac{M_n^{\mathrm{fin}}(P)}n
=\sup_{n\geq1}\frac{M_n^{\mathrm{fin}}(P)}n.
\tag{4}
\]

Two classical results are kept as explicit hypotheses rather than silently
promoted to newly proved facts:

- **(H-Marton)** For every finite two-receiver discrete memoryless broadcast
  channel \(T:x\mapsto(y,z)\) and every finite law
  \((U,V,W)-X-(Y,Z)\), the closure of the nonnegative private-message rate
  pairs satisfying

  \[
  \begin{aligned}
  R_1&\leq I(U,W;Y),\\
  R_2&\leq I(V,W;Z),\\
  R_1+R_2&\leq \min\{I(W;Y),I(W;Z)\}
  +I(U;Y\mid W)+I(V;Z\mid W)-I(U;V\mid W)
  \end{aligned}
  \tag{H-M}
  \]

  is achievable under the average-error convention.
- **(H-binary)** For every finite binary-input two-receiver broadcast
  channel, the supremum of the one-letter Marton private-message sum
  functional equals the randomized-time-division supremum.

Under (H-Marton), the finite-super-symbol reduction is

\[
\boxed{C_{\mathrm{sum}}(P)\geq
\frac{M_n^{\mathrm{fin}}(P)}n\quad(n\geq1),}
\tag{5}
\]

and consequently

\[
C_{\mathrm{sum}}(P)\geq
\lim_{n\to\infty}\frac{M_n^{\mathrm{fin}}(P)}n.
\tag{6}
\]

For the BSSC, define \(h_2(t)=-t\log_2t-(1-t)\log_2(1-t)\),

\[
J(q)=h_2(q/2)-q,
\qquad D(q)=J(q)-J(1-q),
\tag{7}
\]

and let \(L_{\mathrm{RTD}}\) be the randomized-time-division supremum.  The
calculus and symmetrization proof below gives the exact formula

\[
\boxed{
L_{\mathrm{RTD}}
=h_2(1/4)-\frac12
+\frac12\left[
h_2(q_-/2)-h_2((1-q_-)/2)+1-2q_-
\right],
\quad q_-=\frac{15-\sqrt{105}}{30}.}
\tag{8}
\]

The included directed certificate proves

\[
\begin{aligned}
0.3616428844219546156634415781505870072079810107238605552037137298028007
&<L_{\mathrm{RTD}}\\
&<0.3616428844219546156634415781505870072079810107238605552037137298028008,
\end{aligned}
\tag{9}
\]

and

\[
\begin{aligned}
0.7232857688439092313268831563011740144159620214477211104074274596056014
&<2L_{\mathrm{RTD}}\\
&<0.7232857688439092313268831563011740144159620214477211104074274596056016.
\end{aligned}
\tag{10}
\]

Thus (H-binary) implies
\(M_1^{\mathrm{fin}}(P)=L_{\mathrm{RTD}}\).  Under (H-Marton), an
\(n\)-letter finite Marton law of exact value \(S_n\) strictly improves the
governed RTD achievable lower bound through super-symbol normalization if and
only if

\[
S_n>nL_{\mathrm{RTD}}.
\tag{11}
\]

Under both hypotheses, the same inequality is equivalently a strict
improvement over the complete one-letter Marton sum optimum.  For a numerical
two-letter witness, comparison with the directed upper endpoint in (10) is a
rigorous sufficient test; the old ellipsized decimal is not used as an exact
upper bound.

## Proof of the finite-super-symbol reduction

Fix \(n\).  If \(M_n^{\mathrm{fin}}(P)=0\), (5) follows from the trivial
zero-rate code.  Otherwise fix
\(0<\epsilon<M_n^{\mathrm{fin}}(P)\).  The definition of a finite supremum
gives a member of \(\mathcal A_n^{\mathrm{fin}}\) with

\[
F_n>M_n^{\mathrm{fin}}(P)-\epsilon>0.
\tag{12}
\]

For this law put

\[
A=I(U,W;Y^n),\qquad B=I(V,W;Z^n),\qquad S=F_n.
\]

The nonnegativity of mutual information and the two possible branches of the
minimum give \(S\leq A+B\).  Hence there are nonnegative
\(R_1\leq A\), \(R_2\leq B\) with \(R_1+R_2=S\): for example, take
\(R_1=\min\{A,S\}\) and \(R_2=S-R_1\).  These rates obey all three
inequalities in (H-M).  Under (H-Marton), rates arbitrarily close to this pair
are therefore achievable on the finite super-channel \(P^{\otimes n}\).

An \(\ell\)-use code for that super-channel maps each message pair to
\(\ell\) input blocks in \(\{0,1\}^n\).  Flattening those blocks, without
changing the encoder or either decoder, gives an ordinary BSSC code of
blocklength \(n\ell\).  Memorylessness makes the two induced channel laws
identical, so the average error probabilities are unchanged.  The sum rate
per original use is divided by \(n\), and (12) gives a rate arbitrarily close
to \((M_n^{\mathrm{fin}}(P)-\epsilon)/n\).  Letting
\(\epsilon\downarrow0\) proves (5).  This uses only the defining property of
a supremum; no optimizer or auxiliary-cardinality theorem is invoked.

## Proof of superadditivity and the limit

Take independent finite laws at lengths \(m\) and \(n\), each within
\(\epsilon\) of its supremum, and concatenate them.  Pairing their finite
auxiliaries gives another finite law.  Every conditional private term and the
penalty add exactly.  If

\[
A_r=I(W_r;Y^r),\qquad B_r=I(W_r;Z^r),
\qquad r\in\{m,n\},
\]

then the common term satisfies

\[
\min\{A_m+A_n,B_m+B_n\}
\geq\min\{A_m,B_m\}+\min\{A_n,B_n\}.
\tag{13}
\]

Indeed, the right side is no larger than either argument on the left.  Letting
\(\epsilon\downarrow0\) proves (3).

For (2), a constant law gives zero.  For every candidate, discard the
nonpositive penalty and use the \(Y^n\) branch of the minimum:

\[
F_n\leq I(U,W;Y^n)+I(V;Z^n\mid W)
\leq H(Y^n)+H(Z^n)\leq2n.
\]

Fekete's lemma now applies to the finite superadditive sequence and gives
(4); combining (4) with (5) gives (6).

If one finite \(n\)-letter law has value \(S_n\), \(k\) independent copies
have value exactly \(kS_n\).  All conditional terms add, and the common term
uses \(\min\{kA,kB\}=k\min\{A,B\}\).  This propagation is an identity for
the selected laws, not a claim that the suprema are additive.

## Exact RTD reduction and maximizer

For input prior \(q=\Pr[X=0]\), the BSSC receiver mutual informations are
\(J(q)\) and \(J(1-q)\).  Consider an arbitrary randomized-time-division law:
conditioned on a finite common schedule \(W=w\), transmit only to receiver
\(Y\) or only to receiver \(Z\), with conditional input prior \(q_w\).  Let
\(\bar q=\mathbb E q_W\).  Since \(\min\{a,b\}\leq(a+b)/2\), the RTD sum is
at most

\[
\frac{J(\bar q)+J(1-\bar q)}2
+\frac12\mathbb E\,|J(q_W)-J(1-q_W)|.
\tag{14}
\]

The function \(J\) is concave, so the reflection-symmetric concave function
\(J(q)+J(1-q)\) is maximized at \(q=1/2\).  Equation (14) is therefore at
most

\[
J(1/2)+\frac12\max_{0\leq q\leq1}|D(q)|.
\tag{15}
\]

This upper bound is attained.  Let \(q\) maximize \(D\), use a fair binary
schedule, and choose conditional priors \(q\) and \(1-q\); in the first
schedule state transmit only to \(Y\), and in the second only to \(Z\).
The average prior is \(1/2\), both common informations are equal, and the
resulting sum is \(J(1/2)+D(q)/2\).  Antisymmetry
\(D(1-q)=-D(q)\) shows that this equals the right side of (15).

Direct differentiation on \((0,1)\) gives

\[
D'(q)=\frac12\log_2\frac{(2-q)(1+q)}{q(1-q)}-2.
\]

Because the logarithm argument is positive,

\[
D'(q)>0\iff15q^2-15q+2>0.
\]

The roots are \(q_\pm=(15\pm\sqrt{105})/30\).  The quadratic sign pattern,
the identities \(D(0)=D(1/2)=D(1)=0\), and antisymmetry show that the global
maximum is attained at \(q_-\).  Substitution gives (8).

## Directed interval certificate

Run from this contribution directory using only Python's standard library:

```text
python3 -I -B verify_repair.py
```

The checker first proves the rational inequalities
\(s_-^2<105<s_+^2\) for the decimal endpoints stored in
`interval_certificate.json`.  It therefore obtains a directed interval for
\(q_-=(15-\sqrt{105})/30\) without calling a floating-point square root.
All subsequent arithmetic uses 120-digit `Decimal` contexts with outward
rounding.  Python's `Decimal.ln` is correctly rounded using round-to-nearest;
the checker expands each logarithm result by one representable number in each
direction.  It then evaluates (8), requires the computed enclosure to lie
strictly inside the declared bounds (9), and independently checks (10) by
directed multiplication.  The certificate is an interval proof for the exact
closed form, not a check of a decimal prefix.

## Repair and provenance

Canonical transaction
`f6ea30479b9ca461294ba89a8a1a31c06ce59d08`
(`marton-multiletter-frontier-audit-2026`) is the sole declared reference in
`claims.json`.  It is a **corrective/provenance reference**, not a mathematical
premise: its primary judgment was indeterminate.  This append-only
contribution repairs and supersedes only these portions of that record:

1. its displayed \(M_n\) definition is replaced by (1), whose finite
   auxiliary scope and epsilon/supremum semantics are explicit;
2. its super-symbol capacity conclusion is replaced by the detailed reduction
   above, with (H-Marton) exposed as the exact hypothesis;
3. its unconditional wording \(M_1=L_{\mathrm{RTD}}\) is replaced by the
   exact conditional statement under (H-binary); and
4. its uncertified ellipsized threshold display is replaced by the directed
   intervals (9)--(10).

The old contribution's August 2026 source audit, theorem-scope audit, and
reproducibility-repository caveats are neither repeated nor superseded here.
No claim in this repair depends on their validity.

The exact external hypotheses are attributed to the following theorem
records:

- Katalin Marton, *A Coding Theorem for the Discrete Memoryless Broadcast
  Channel*, IEEE Transactions on Information Theory 25 (1979), 306--311,
  [doi:10.1109/TIT.1979.1056046](https://doi.org/10.1109/TIT.1979.1056046).
  The exact modern private-message formulation used as (H-Marton) is restated
  as Bound 1 of [Gohari, Nair, and Anantharam,
  arXiv:1202.0898v1](https://arxiv.org/abs/1202.0898v1).
- The binary-input equality with randomized time division in Corollary 1 of
  [Nair, Wang, and Geng, arXiv:1001.1468v1](https://arxiv.org/abs/1001.1468v1).

These results are quoted as hypotheses and are not independently re-proved or
authenticated by the interval checker.  The proof, specialization, and
certificate in this contribution were prepared by an OpenAI Codex solver
agent at Robert Raynor's request.

## Limitations

- This contribution does not independently prove (H-Marton) or (H-binary).
- It does not prove that arbitrary non-finite auxiliary spaces can be reduced
  to finite ones; they are excluded from the definition.
- It supplies no new BSSC witness and does not improve the governed capacity
  interval.
- Equality at one fixed blocklength is not a capacity converse; another
  blocklength or a non-Marton construction could do better.
- Superadditivity is not additivity.  The residual three- and four-symbol
  two-letter search remains open.
