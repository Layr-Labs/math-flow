# Integrality gap of the CKR relaxation for Multiway Cut

Let \([k]=\{1,\ldots,k\}\). Let \(G=(V,E)\) be a finite undirected graph
with nonnegative edge weights \(w:E\to\mathbb R_{\ge 0}\), and let
\(T=\{t_1,\ldots,t_k\}\) be a set of distinct terminals. Write
\(w_{uv}=w(\{u,v\})\).
The integral Multiway Cut optimum is

\[
\operatorname{OPT}(G,T,w)
=
\min_{\substack{f:V\to[k]\\f(t_i)=i}}
\sum_{\{u,v\}\in E}w_{uv}\mathbf 1[f(u)\ne f(v)].
\]

Write

\[
\Delta_k=\left\{x\in\mathbb R_{\ge0}^k:
\sum_{i=1}^k x_i=1\right\}.
\]

Writing \(e_i\) for the \(i\)-th standard unit vector, the
Călinescu--Karloff--Rabani relaxation has value

\[
\operatorname{CKR}(G,T,w)
=
\min_{\substack{x_v\in\Delta_k\ (v\in V)\\
x_{t_i}=e_i\ (i\in[k])}}
\frac12\sum_{\{u,v\}\in E}w_{uv}\lVert x_u-x_v\rVert_1.
\]

For \(k\ge3\), define

\[
\Gamma_k=
\sup_{\substack{(G,T,w):\ |T|=k\\
\operatorname{CKR}(G,T,w)>0}}
\frac{\operatorname{OPT}(G,T,w)}
{\operatorname{CKR}(G,T,w)},
\qquad
\Gamma=\sup_{k\ge3}\Gamma_k.
\]

Improve either side of the current unconditional bracket

\[
1.20016\le \Gamma\le1.2787.
\]

Concretely, prove \(\Gamma\ge L\) for an explicit \(L>1.20016\), or prove
\(\Gamma\le U\) for an explicit \(U<1.2787\). A lower bound may be
asymptotic: it is enough to prove that for every \(\varepsilon>0\) there is a
finite conventional Multiway Cut instance with ratio at least
\(L-\varepsilon\). An upper bound must compare against the CKR value for every
finite instance, not merely give an approximation ratio relative to
\(\operatorname{OPT}\).

The lower benchmark is obtained through an auxiliary non-opposite-cut problem
on the three-dimensional simplex \(\Delta_4\) and a transfer to conventional
instances with a growing number of terminals. It is not a four-terminal CKR
gap of \(1.20016\). The upper benchmark comes from a rigorously
interval-certified rounding scheme. Both facts are established background,
not Math Flow ledger evidence.

Useful contributions include:

- an explicit rationally weighted graph, terminal set, feasible CKR embedding,
  and exact certificates for its integral and relaxed values;
- a parameterized family with a complete proof of every limiting error and
  quantifier;
- a discretized-simplex non-opposite-cut certificate together with the full
  transfer theorem to finite conventional instances;
- a new rounding distribution and a universal expected-cost proof;
- an analytic, formal, exact-enumeration, MILP, or outward-rounded interval
  certificate for a stated construction or rounding family;
- a structural theorem about ordinary or non-opposite cuts in \(\Delta_4\);
- an exact finite minimax bound plus a proved discretization-error estimate; or
- a counterexample, restricted-family result, reproducible numerical lead, or
  independent baseline replay whose limited scope is stated explicitly.

A floating-point objective value or an auxiliary simplex grid without its
transfer proof is not by itself a new bound on \(\Gamma\). Conditional
connections to optimal approximation under the Unique Games Conjecture must be
labeled conditional; the governed integrality-gap objective is unconditional.

## Frontier sources

- Gruia Călinescu, Howard Karloff, and Yuval Rabani,
  [An Improved Approximation Algorithm for Multiway Cut](https://doi.org/10.1006/jcss.1999.1687),
  Journal of Computer and System Sciences 60 (2000).
- Haris Angelidakis, Yury Makarychev, and Pasin Manurangsi,
  [An Improved Integrality Gap for the Călinescu--Karloff--Rabani Relaxation for Multiway Cut](https://arxiv.org/abs/1611.05530),
  2017.
- Kristóf Bérczi, Karthekeyan Chandrasekaran, Tamás Király, and
  Vivek Madan,
  [Improving the Integrality Gap for Multiway Cut](https://arxiv.org/abs/1807.09735),
  Mathematical Programming 183 (2020).
- Joshua Brakensiek, Neng Huang, Aaron Potechin, and Uri Zwick,
  [Improved Approximation Algorithms for Multiway Cut by Large Mixtures of New and Old Rounding Schemes](https://arxiv.org/abs/2603.28700),
  STOC 2026.
- Brakensiek--Huang--Potechin--Zwick,
  [pinned interval-verification code](https://github.com/jbrakensiek/multiway-cut-verification/tree/633ee8b6e1cf67280d3967469cbd2e05bbb7f6d7).

The displayed bracket was checked against these primary sources on 2026-08-12.
