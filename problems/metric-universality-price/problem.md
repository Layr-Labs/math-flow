# Is metric universality strictly costly in Gaussian vector quantization?

For each dimension \(n\), let \(W\sim N(0,I_n)\). An unknown quadratic
distortion is specified by a positive-semidefinite matrix
\(\Sigma\succeq0\) with \(\operatorname{tr}\Sigma=n\), through the squared
Hilbert seminorm

\[
d_\Sigma(w,c)=(w-c)^\mathsf T\Sigma(w-c).
\]

A universal codebook \(C\subset\mathbb R^n\) is chosen without knowing
\(\Sigma\). The encoder does know \(\Sigma\) and may select a codeword
minimizing this distortion. Define its normalized distortion by

\[
D(C,\Sigma)=\frac1n\mathbb E_W\min_{c\in C}d_\Sigma(W,c).
\]

If \(\lambda_1,\ldots,\lambda_n\) are the eigenvalues of \(\Sigma\), the
Gaussian rate-distortion water-filling functions are

\[
D_{\mathrm{wf}}(\Sigma,t)=\frac1n\sum_{i=1}^n\min\{\lambda_i,t\},
\qquad
R_{\mathrm{wf}}(\Sigma,t)=
\frac1{2n}\sum_{i=1}^n\max\!\left\{0,
\log_2\frac{\lambda_i}{t}\right\}.
\]

For \(0<D<1\), write \(R_{\mathrm{wf}}(\Sigma,D)\) for the second expression
at a water level satisfying \(D_{\mathrm{wf}}(\Sigma,t)=D\), and set it to
zero for \(D\ge1\), and set \(R_{\mathrm{wf}}(\Sigma,0)=+\infty\).

Fix \(R>0\), let \(M_n=\lceil2^{nR}\rceil\) and
\(r_n=n^{-1}\log_2 M_n\), and define the finite-dimensional minimax overhead

\[
\pi_n(R)=
\inf_{\substack{C\subset\mathbb R^n\\|C|=M_n}}
\sup_{\substack{\Sigma\succeq0\\\operatorname{tr}\Sigma=n}}
\left[r_n-R_{\mathrm{wf}}\bigl(\Sigma,D(C,\Sigma)\bigr)\right],
\qquad
\pi(R)=\liminf_{n\to\infty}\pi_n(R).
\]

The Gaussian rate-distortion converse makes this overhead nonnegative. Decide
whether metric universality is strictly costly:

\[
\text{Do there exist }R_0>0\text{ and }\delta>0
\text{ such that }\pi(R_0)\ge\delta?
\]

Either direction resolves the question: prove such an explicit positive lower
bound, or construct universal codebooks proving \(\pi(R)=0\) for every fixed
\(R>0\). More generally, rigorously improve the definition-immediate bracket

\[
0\le\pi(R)\le R
\]

in a clearly specified rate regime.

The 2026 upper-bound paper proves a \(0.11\)-bit universality result through a
Gaussian random-coding tradeoff. Its final version reduces the relevant bound
to limiting two-point spectra and bounds the final one-variable objective by
approximately \(0.108<0.11\). Its formal achievability theorem uses separate
rate and additive-distortion limits; no uniform conversion of those limits to
the exact \(\pi(R)\) definition above is assumed here. The paper does not prove
a positive minimax lower bound for arbitrary universal codebooks, and its
random-coding optimization is not itself a lower bound on the price of
universality. The two-sided minimax question above is therefore the governed
target; it does not presume that the price is positive.

Useful contributions include:

- an adversarial family of incompatible, for example differently oriented,
  metrics giving a positive lower bound against every codebook;
- an explicit or probabilistic sequence of universal codebooks with a smaller
  worst-case overhead, including a zero-price construction;
- a finite-dimensional minimax theorem with quantified convergence to an
  asymptotic bound;
- a packing, covering, information-theoretic, or formal lemma that controls a
  specified part of the minimax problem;
- exact or rigorously interval-certified optimization over a stated finite
  metric family;
- an efficient explicit construction, separately labeled if it improves
  implementability but not the minimax bound; or
- a counterexample, restricted-codebook theorem, or numerical lead whose scope
  and unresolved passage to the full problem are explicit.

Results for diagonal metrics, lattices, product codebooks, stochastic metric
models, or a finite metric family do not automatically settle the deterministic
worst-case problem over arbitrary \(\Sigma\) and arbitrary codebooks. Every
submission should state those quantifiers precisely.

## Frontier sources

- Alina Harbuzova, Or Ordentlich, and Yury Polyanskiy,
  [Price of metric universality in vector quantization is at most 0.11 bit](https://proceedings.mlr.press/v336/harbuzova26a.html),
  COLT 2026; see also [arXiv:2602.05790v2](https://arxiv.org/abs/2602.05790v2).
- Emin Martinian, Gregory W. Wornell, and Ram Zamir,
  [Source Coding With Distortion Side Information](https://doi.org/10.1109/TIT.2008.928983),
  IEEE Transactions on Information Theory 54 (2008).

The status and final-version formulation were checked on 2026-08-12.
