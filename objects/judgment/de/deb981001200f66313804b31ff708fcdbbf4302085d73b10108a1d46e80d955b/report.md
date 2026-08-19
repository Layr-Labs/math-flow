## `metric-universality-price/subexponential-rank-one-families-zero-price`

**Verdict: VALID**

The quantitative existence, distortion, overhead, and asymptotic claims are established by the supplied argument.

### 1. Simultaneous nonorthogonality lemma

Implicitly \(m\ge 1\), as required for \(\beta_m\) and the displayed maximum.

For \(G\sim N(0,I_n)\), each \(u_i^{\mathsf T}G\sim N(0,1)\), regardless of dependence between the projections. For \(a=1/(4m)\),

\[
\Pr(|Z|<a)\le 2a\sup_x\phi(x)
=\sqrt{\frac2\pi}\,a.
\]

For \(b=\sqrt{2\ln(8m)}\),

\[
\Pr(|Z|>b)\le 2e^{-b^2/2}=\frac1{4m}.
\]

Thus the union of all \(2m\) bad events has probability at most

\[
m\sqrt{\frac2\pi}\frac1{4m}+m\frac1{4m}
=\frac14\sqrt{\frac2\pi}+\frac14<1.
\]

Consequently, a witness \(v\) satisfying

\[
\frac1{4m}\le |u_i^{\mathsf T}v|\le \sqrt{2\ln(8m)}
\]

exists. In particular, \(\alpha_*=\min_i|u_i^{\mathsf T}v|>0\), so \(v\ne0\), and

\[
\frac{\max_i|\alpha_i|}{\alpha_*}
\le 4m\sqrt{2\ln(8m)}=\beta_m.
\]

No independence or general-position assumption is used.

### 2. Codebook geometry and cardinality

The scalars \(s_j\) are distinct because \(M\ge2\), \(A>0\), and \(\alpha_*>0\). Since \(v\ne0\), the codewords \(c_j=s_jv\) are also distinct, so the codebook has exactly \(M\) elements.

For each \(i\),

\[
u_i^{\mathsf T}c_j=\alpha_i s_j
\]

forms, up to reversal, an equally spaced grid with endpoints \(\pm L_i\), where

\[
L_i=A\frac{|\alpha_i|}{\alpha_*}\ge A.
\]

Its spacing is

\[
h_i=\frac{2L_i}{M-1}
\le \frac{2A\beta_m}{M-1}.
\]

These conclusions remain valid for repeated or linearly dependent orientations.

### 3. Scalar quantization bound

For \(|z|\le L_i\), the nearest-grid error is at most \(h_i/2\). For \(|z|>L_i\), the nearest point is the corresponding endpoint and

\[
\operatorname{dist}(z,G_i)=|z|-L_i\le |z|-A.
\]

Therefore the claimed global, albeit non-tight, bound

\[
\operatorname{dist}(z,G_i)^2
\le \frac{h_i^2}{4}+(|z|-A)_+^2
\]

is correct in both regions.

For \(Z\sim N(0,1)\),

\[
(|Z|-A)_+^2\le Z^2\mathbf 1_{\{|Z|>A\}}.
\]

Integration by parts gives

\[
\mathbb E[Z^2\mathbf 1_{\{|Z|>A\}}]
=2(A\phi(A)+Q(A)).
\]

Since \(A>0\), Mills’ inequality \(Q(A)\le \phi(A)/A\) applies. With
\(A=2\sqrt{\ln M}\),

\[
\phi(A)=\frac{1}{\sqrt{2\pi}}e^{-A^2/2}
=\frac{1}{\sqrt{2\pi}M^2}.
\]

This yields exactly the stated tail term. The grid term satisfies

\[
\frac{h_i^2}{4}
\le \frac{A^2\beta_m^2}{(M-1)^2}
=\frac{4\beta_m^2\ln M}{(M-1)^2}.
\]

Thus their sum is precisely \(B(M,m)\).

### 4. Reduction of the rank-one distortion

For \(\Sigma_i=nu_iu_i^{\mathsf T}\),

\[
\frac1n d_{\Sigma_i}(W,c)
=(u_i^{\mathsf T}W-u_i^{\mathsf T}c)^2.
\]

Because \(u_i\) is a unit vector, \(u_i^{\mathsf T}W\sim N(0,1)\). Hence

\[
D(C,\Sigma_i)
=\mathbb E\operatorname{dist}(Z,G_i)^2
\le B(M,m).
\]

The distortion is also strictly positive: a finite grid cannot contain a continuously distributed \(Z\) almost surely. Therefore, when \(B(M,m)<1\), one has \(0<D(C,\Sigma_i)<1\), so the interior water-filling formula is applicable.

### 5. Water-filling and overhead conversion

The spectrum is \((n,0,\ldots,0)\). For \(0<D<1\), the equation

\[
D_{\mathrm{wf}}(\Sigma_i,t)=D
\]

gives \(t=nD\), and therefore

\[
R_{\mathrm{wf}}(\Sigma_i,D)
=\frac1{2n}\log_2\frac{n}{nD}
=\frac1{2n}\log_2\frac1D.
\]

Since this overhead is increasing in \(D\),

\[
\begin{aligned}
\frac{\log_2M}{n}
-R_{\mathrm{wf}}(\Sigma_i,D(C,\Sigma_i))
&=\frac1{2n}\log_2\!\left(M^2D(C,\Sigma_i)\right)\\
&\le \frac1{2n}\log_2\!\left(M^2B(M,m)\right).
\end{aligned}
\]

Taking the maximum over \(i\) and then the infimum over all \(M\)-word codebooks proves the upper bound in (1).

The lower bound \(\Pi_n\ge0\) follows from the Gaussian rate-distortion converse explicitly supplied in the problem: an encoder whose reproduction takes at most \(M\) values has information rate at most \(\log_2M/n\), which cannot be below \(R_{\mathrm{wf}}(\Sigma_i,D)\).

### 6. Asymptotic passage

For \(M_n=\lceil2^{nR}\rceil\) with \(R>0\),

\[
\ln M_n=\Theta(n).
\]

If \(\ln m_n=o(n)\), then

\[
\ln\beta_{m_n}
=\ln4+\ln m_n+\frac12\ln\!\bigl(2\ln(8m_n)\bigr)
=o(n).
\]

Consequently, both terms in \(B(M_n,m_n)\) decay exponentially up to subexponential factors, so

\[
B(M_n,m_n)=o(1).
\]

Thus \(B<1\) eventually. Moreover,

\[
M_n^2B(M_n,m_n)
\le 16\beta_{m_n}^2\ln M_n+O(\sqrt{\ln M_n}),
\]

whose logarithm is \(o(n)\). Hence

\[
0\le \Pi_n(\mathcal U_n,M_n)
\le \frac1{2n}\log_2\!\left(M_n^2B(M_n,m_n)\right)
\longrightarrow0.
\]

This proves (2).

### 7. Scope and terminology

The final scope conclusion is justified: a lower bound based solely on maximizing over a prescribed subexponential rank-one family cannot give a positive asymptotic restricted minimax overhead. The result does not control the full uncountable metric family and therefore does not establish \(\pi(R)=0\).

The witness \(v\) is obtained probabilistically rather than by an effective deterministic algorithm. Thus “explicit” is justified only in the sense that the codebook has the displayed formula once a valid witness is selected; no efficient algorithmic construction is proved. This does not affect the formal existence or minimax bounds.
