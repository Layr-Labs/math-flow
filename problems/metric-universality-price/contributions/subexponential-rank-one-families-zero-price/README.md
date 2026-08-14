# Subexponential rank-one families have zero restricted price

## Claim

Fix a dimension \(n\), an integer \(M\ge 2\), and any finite family of unit
vectors

\[
\mathcal U=\{u_1,\ldots,u_m\}\subset S^{n-1}.
\]

Associate to these vectors the trace-normalized rank-one metrics
\(\Sigma_i=n u_i u_i^{\mathsf T}\). Define the minimax overhead restricted to
this family by

\[
\Pi_n(\mathcal U,M)=
\inf_{\substack{C\subset\mathbb R^n\\ |C|=M}}
\max_{1\le i\le m}
\left[
\frac{\log_2 M}{n}
-R_{\mathrm{wf}}\bigl(\Sigma_i,D(C,\Sigma_i)\bigr)
\right].
\]

Put

\[
\beta_m=4m\sqrt{2\ln(8m)}
\]

and

\[
B(M,m)=
\frac{4\beta_m^2\ln M}{(M-1)^2}
+\frac{2}{\sqrt{2\pi}\,M^2}
\left(2\sqrt{\ln M}+\frac{1}{2\sqrt{\ln M}}\right).
\]

There is an explicit collinear \(M\)-word codebook, depending on
\(\mathcal U\), for which

\[
D(C,\Sigma_i)\le B(M,m)\qquad(1\le i\le m).
\]

Consequently, whenever \(B(M,m)<1\),

\[
0\le \Pi_n(\mathcal U,M)
\le \frac{1}{2n}\log_2\!\bigl(M^2B(M,m)\bigr).
\tag{1}
\]

In particular, let \(R>0\), let \(M_n=\lceil 2^{nR}\rceil\), and allow the
rank-one family \(\mathcal U_n\) to vary with \(n\). If its cardinality
\(m_n\) satisfies

\[
\ln m_n=o(n),
\]

then

\[
\lim_{n\to\infty}\Pi_n(\mathcal U_n,M_n)=0.
\tag{2}
\]

Thus no fixed, polynomial-size, or more generally subexponential-size family
of differently oriented rank-one metrics can by itself prove a positive
asymptotic minimax price against arbitrary codebooks. Any rank-one
finite-family lower-bound route must use exponentially many orientations (at
the relevant exponent) or add an argument that genuinely controls metrics
outside the displayed family.

## A simultaneous nonorthogonality lemma

The key elementary fact is uniform over the geometry of the vectors.

**Lemma.** For every \(u_1,\ldots,u_m\in S^{n-1}\), there is a vector
\(v\in\mathbb R^n\) such that

\[
\frac{1}{4m}\le |u_i^{\mathsf T}v|
\le \sqrt{2\ln(8m)}
\qquad(1\le i\le m).
\tag{3}
\]

**Proof.** Draw \(G\sim N(0,I_n)\). Each marginal
\(u_i^{\mathsf T}G\) is a standard normal random variable; independence is
not needed. For \(a=1/(4m)\), the standard normal density bound gives

\[
\Pr\{|u_i^{\mathsf T}G|<a\}
\le \sqrt{\frac{2}{\pi}}a.
\]

For \(b=\sqrt{2\ln(8m)}\), the Chernoff tail bound gives

\[
\Pr\{|u_i^{\mathsf T}G|>b\}
\le 2e^{-b^2/2}=\frac{1}{4m}.
\]

The union bound over all lower- and upper-tail events is at most

\[
\frac14\sqrt{\frac2\pi}+\frac14<1.
\]

Therefore some realization \(v\) avoids every event and satisfies (3).
\(\square\)

For this \(v\), write

\[
\alpha_i=u_i^{\mathsf T}v,
\qquad
\alpha_*=\min_i|\alpha_i|.
\]

The lemma implies

\[
1\le \frac{\max_i|\alpha_i|}{\alpha_*}\le\beta_m.
\tag{4}
\]

## Collinear codebook and distortion bound

Let

\[
A=2\sqrt{\ln M}
\]

and take the \(M\) distinct collinear codewords

\[
c_j=s_jv,
\qquad
s_j=-\frac{A}{\alpha_*}
+\frac{2A(j-1)}{\alpha_*(M-1)},
\qquad 1\le j\le M.
\tag{5}
\]

For a fixed \(i\), the projected codebook
\(\{u_i^{\mathsf T}c_j\}_{j=1}^M\) is an equally spaced scalar grid with
endpoints \(\pm L_i\), up to reversal, where

\[
L_i=A\frac{|\alpha_i|}{\alpha_*}\ge A.
\]

Its spacing \(h_i\) obeys, by (4),

\[
h_i=\frac{2L_i}{M-1}
\le \frac{2A\beta_m}{M-1}.
\tag{6}
\]

If \(Z\sim N(0,1)\) and \(G_i\) denotes this scalar grid, then pointwise

\[
\operatorname{dist}(Z,G_i)^2
\le \frac{h_i^2}{4}+(|Z|-A)_+^2.
\tag{7}
\]

Indeed, inside \([-L_i,L_i]\) the nearest-grid error is at most \(h_i/2\),
while outside that interval the error is \(|Z|-L_i\le |Z|-A\).

Let \(\phi\) and \(Q\) be the standard normal density and upper tail. By
integration by parts and the Mills bound,

\[
\begin{aligned}
\mathbb E (|Z|-A)_+^2
&\le \mathbb E\bigl[Z^2\mathbf 1\{|Z|>A\}\bigr]\\
&=2\bigl(A\phi(A)+Q(A)\bigr)\\
&\le 2(A+A^{-1})\phi(A)\\
&=\frac{2}{\sqrt{2\pi}\,M^2}
\left(2\sqrt{\ln M}+\frac{1}{2\sqrt{\ln M}}\right).
\end{aligned}
\tag{8}
\]

For \(\Sigma_i=n u_i u_i^{\mathsf T}\), normalization cancels the only
nonzero eigenvalue:

\[
\begin{aligned}
D(C,\Sigma_i)
&=\frac1n\mathbb E\min_{c\in C}
n\bigl(u_i^{\mathsf T}(W-c)\bigr)^2\\
&=\mathbb E\min_{c\in C}(Z-u_i^{\mathsf T}c)^2.
\end{aligned}
\tag{9}
\]

Combining (6)--(9), and using \(A^2=4\ln M\), gives precisely
\(D(C,\Sigma_i)\le B(M,m)\), simultaneously for every \(i\).

## Conversion to overhead

The spectrum of \(\Sigma_i\) is \((n,0,\ldots,0)\). For \(0<D<1\), its
water level is \(t=nD\), and hence

\[
R_{\mathrm{wf}}(\Sigma_i,D)
=\frac{1}{2n}\log_2\frac1D.
\tag{10}
\]

When \(B(M,m)<1\), equations (9)--(10) give for the codebook (5)

\[
\frac{\log_2 M}{n}
-R_{\mathrm{wf}}(\Sigma_i,D(C,\Sigma_i))
\le
\frac{1}{2n}\log_2\!\bigl(M^2B(M,m)\bigr),
\]

uniformly in \(i\). Taking the maximum and then the infimum proves the upper
bound in (1); its lower bound is the Gaussian rate-distortion converse already
stated in the problem.

For a transparent asymptotic estimate, \(M/(M-1)\le2\) gives

\[
M^2B(M,m)
\le 16\beta_m^2\ln M
+\frac{2}{\sqrt{2\pi}}
\left(2\sqrt{\ln M}+\frac{1}{2\sqrt{\ln M}}\right).
\tag{11}
\]

If \(M=M_n=\lceil2^{nR}\rceil\), then \(\ln M_n=\Theta(n)\). If also
\(\ln m_n=o(n)\), then \(\ln\beta_{m_n}=o(n)\). The right side of (11) has
base-two logarithm \(o(n)\), whereas \(B(M_n,m_n)=o(1)\). Applying (1)
proves (2).

## Scope and limitations

This is a negative result about one proposed lower-bound mechanism, not a
solution of the governed minimax problem. The full definition lets the
adversary choose from an uncountable family after seeing the codebook. The
collinear codebook (5) is tailored to the prescribed finite family and can
perform very poorly for other rank-one orientations and for higher-rank
metrics. Therefore the result does **not** prove \(\pi(R)=0\), nor does it
exclude a lower bound using exponentially many rank-one orientations, a
continuum argument with adequate uniform control, or a genuinely low-rank or
full-rank adversarial family.

No independence or general-position assumption is made on the orientations,
and repeated or linearly dependent vectors are allowed. The family may depend
on \(n\); only its cardinality enters the bound.

No computational experiment or external mathematical source is used. The
argument is self-contained apart from the Gaussian rate-distortion converse
and water-filling definitions supplied in the canonical problem statement.

## Reproduction and validation

The contribution contains a symbolic proof and no computational certificate.
From the repository root, validate its protocol shape with:

```sh
python3 -m math_flow validate-tree
python3 -m unittest discover -s tests -v
git diff --check
```

## Authorship

Proof and exposition by an OpenAI Codex research agent working through the
Math Flow solver protocol at Robert Raynor's request.
