# Maximal determinant at order 23

Let

\[
D_{23}=\max\left\{|\det A|:A\in\{-1,+1\}^{23\times23}\right\}.
\]

Determine \(D_{23}\), improve its certified lower bound by exhibiting a
matrix with larger determinant, or improve its certified upper bound. The
published record and general upper estimate give

\[
2^{22}\,3\,5^6\,67\,211
\le D_{23}\le
2^{22}\,3\,5^6\,675\sqrt{505}.
\]

The lower endpoint equals \(2{,}779{,}447{,}296{,}000{,}000\). Since
\(D_{23}\) is an integer, the displayed real-valued upper endpoint may of
course be replaced by its floor; any stronger divisibility rounding must be
proved as part of the claimed bound.

Useful contributions include:

- a complete \(23\times23\) sign matrix with a larger exactly evaluated
  determinant;
- a fraction-free or modular determinant verifier;
- an exhaustive Gram-matrix classification with replayable pruning
  certificates;
- a proof strengthening the analytic or arithmetic upper bound;
- a symmetry or equivalence reduction under signed row and column operations,
  with its scope proved; or
- a reproducible heuristic search or non-finding explicitly labeled as
  non-exhaustive.

Floating-point determinants are not certificates. Computational claims should
include the matrix or proof artifact and permit exact independent replay.

## Frontier source

- William P. Orrick, Bruce Solomon, Roland Dowdeswell, and Warren D. Smith,
  [New lower bounds for the maximal determinant problem](https://arxiv.org/abs/math/0304410),
  2003; the paper gives the order-23 record matrix and the displayed bounds.
