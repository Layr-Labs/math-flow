# Sample complexity of replicable realizable PAC learning

Let \(H\subseteq\{0,1\}^X\) be a finite hypothesis class. A realizable labeled
distribution is obtained by choosing a distribution \(D\) on \(X\) and a
target \(h^\star\in H\), then labeling \(x\sim D\) by \(h^\star(x)\). For an
arbitrary classifier \(g\in\{0,1\}^X\), write

\[
\operatorname{err}_{D,h^\star}(g)
=\Pr_{x\sim D}[g(x)\ne h^\star(x)].
\]

A randomized, possibly improper learner \(A\), given \(n\) independent labeled
examples, returns a classifier \(A(S;r)\in\{0,1\}^X\). It is
\((\varepsilon,\delta)\)-accurate if for every \(D\) and \(h^\star\in H\),

\[
\Pr_{S,r}\!\left[
\operatorname{err}_{D,h^\star}(A(S;r))>\varepsilon
\right]\le\delta.
\]

It is \(\rho\)-replicable if, for every \(D\) and \(h^\star\in H\), two
independent samples \(S_1,S_2\) from that realizable distribution, processed
with the same internal random seed \(r\), satisfy

\[
\Pr_{S_1,S_2,r}[A(S_1;r)=A(S_2;r)]\ge1-\rho.
\]

Let \(n_{\mathrm{rep}}(N,\varepsilon,\delta,\rho)\) be the supremum, over all
domains \(X\) and finite classes \(H\subseteq\{0,1\}^X\) with \(|H|\le N\),
of the least sample size of an unrestricted, computationally unbounded,
possibly improper randomized learner satisfying both conditions above.
All logarithms below are natural. Determine this worst-case sample complexity.
In particular, for fixed sufficiently small positive \(\rho\) and \(\delta\),
close the current gap in the exponent of \(\log N\):

\[
\widetilde\Omega\!\left(
\frac{(\log N)^{3/2}}{\varepsilon}
\right)
\ \le\ n_{\mathrm{rep}}(N,\varepsilon,\delta,\rho)
\ \le\ O\!\left(\frac{(\log N)^2}{\varepsilon}\right).
\]

Here the tilde on the established lower bound suppresses factors logarithmic
in \(\log N\) and \(1/\varepsilon\); \(\rho\) and \(\delta\) are fixed in
this exponent comparison.

Thus a headline result may take either form:

- construct an explicit parameterized family \((X_m,H_m)\) and prove
  \(n_{\mathrm{rep}}(|H_m|,\varepsilon,\delta,\rho)
  =\widetilde\Omega((\log|H_m|)^c/\varepsilon)\) for some \(c>3/2\), ideally
  \(c=2\), by showing that every learner which is both
  \((\varepsilon,\delta)\)-accurate and \(\rho\)-replicable has an adversarial
  realizable choice of \(D\) and \(h^\star\) requiring that many samples; or
- give a universal learner with an upper bound
  \[
  O\!\left(\frac{(\log|H|)^c}{\varepsilon}
  \operatorname{polylog}\!\left(
  \log|H|,\frac1\varepsilon,\frac1\rho,\frac1\delta
  \right)\right)
  \]
  for some \(c<2\), ideally \(c=3/2\), with every suppressed factor and its
  dependence on \(\rho\) and \(\delta\) explicit.

The universal finite-class upper bound of Bun et al. is

\[
O\!\left(
\frac{\log^2|H|+\log(1/(\rho\delta))}
{\varepsilon\rho^2}\log^3\frac1\rho
\right).
\]

Larsen--Mathiasen--Pabbaraju--Svendsen prove that for every
\(d\ge10^{11}\) and \(0<\varepsilon,\delta,\rho\le10^{-4}\), there is a
finite class of VC dimension \(d\) for which every learner has an adversarial
realizable distribution requiring at least

\[
\frac{10^{-9}(\log|H|)^{3/2}}
{\varepsilon(\log\log|H|)^2\log(\log|H|/\varepsilon)}.
\]

Their hard family uses \(X=[d]\times\mathbb Z_k\) for prime \(k\),
\(|H|=k^d\), cyclic half-interval hypotheses, and a uniform distribution.
They also report a family-specific
\(\widetilde O((\log|H|)^{3/2}/(\rho\varepsilon))\) learner. This is the
source's notation and its summary leaves the suppressed polylogarithmic
dependence implicit. It nevertheless rules out a stronger \(\log|H|\)
exponent for essentially the same family, so such a lower bound requires a
genuinely different hard family or technique.
These are established external baselines, not Math Flow ledger evidence.

Useful contributions include:

- a new explicit hard family and a proof quantified over every learner that is
  both accurate and replicable, with the order of all asymptotic parameters
  stated and any dependence of the family on
  \(\varepsilon,\delta,\rho\) disclosed;
- a universal replicable-learning algorithm improving the logarithmic
  exponent or the current \(\rho^{-2}\) dependence toward \(\rho^{-1}\);
- a combinatorial, expansion, isoperimetric, spectral, or information-theoretic
  hardness criterion and an explicit family satisfying it;
- a matching learner or counterexample that rules out a proposed hard family;
- a sharp theorem for a substantial restricted class, with the restriction
  stated in the claim;
- removal of polylogarithmic losses or extension of the known parameter regime;
  or
- finite computation or numerical evidence used as a clearly labeled lead for
  an asymptotic theorem.

A single finite instance, empirical instability, or a construction without a
universal lower-bound proof against randomized learners does not establish the
headline lower bound. Proper-only, efficient-only, or distribution-restricted
claims must be labeled if they do not cover the general definition above.

## Frontier sources

- Mark Bun, Marco Gaboardi, Max Hopkins, Russell Impagliazzo, Rex Lei, Toniann
  Pitassi, Satchit Sivakumar, and Jessica Sorrell,
  [Stability is Stable: Connections between Replicability, Privacy, and Adaptive Generalization](https://arxiv.org/abs/2303.12921),
  STOC 2023.
- Kasper Green Larsen, Markus Engelund Mathiasen, Chirag Pabbaraju, and
  Clement Svendsen,
  [The Sample Complexity of Replicable Realizable PAC Learning](https://arxiv.org/abs/2602.19552),
  STOC 2026.

The open exponent gap was checked against these primary sources on 2026-08-12.
