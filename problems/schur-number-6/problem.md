# The sixth Schur number

A set of positive integers is *sum-free* if it contains no \(x,y,z\), with
\(x\) and \(y\) allowed to be equal, such that \(x+y=z\). The Schur number
\(S(r)\) is the largest integer \(N\) for which
\(\{1,2,\ldots,N\}\) can be partitioned into \(r\) sum-free sets.
Equivalently, it is the largest \(N\) admitting an \(r\)-coloring with no
monochromatic solution to \(x+y=z\).

Determine \(S(6)\), or improve either side of the current published interval

\[
536\le S(6)\le1836.
\]

A lower-bound contribution should give an explicit coloring. An upper-bound
contribution must rule out every coloring at the claimed threshold; a search
that merely fails to find one is not an upper bound.

Useful contributions include:

- an explicit certified coloring of \(\{1,\ldots,N\}\) for \(N>536\);
- a compact exact checker and a canonical encoding of a coloring witness;
- a combinatorial argument lowering the upper endpoint;
- a SAT, pseudo-Boolean, or constraint-programming proof with a replayable
  unsatisfiability certificate;
- symmetry reductions proved to preserve all relevant colorings;
- a formal proof of a structural lemma; or
- reproducible search data or a negative search result with its non-global
  scope stated explicitly.

All witness checks should use exact integer arithmetic. Certificate-producing
computations should include enough source data and instructions for an
independent replay.

## Frontier sources

- Shalom Eliahou and Pastora Revuelta,
  [The Schur degree of additive sets](https://arxiv.org/abs/2006.01502),
  Discrete Mathematics 344 (2021), Article 112332; the paper records the
  displayed interval and conjectures the conditional upper bound \(966\).
- Marijn J. H. Heule,
  [Schur Number Five](https://ojs.aaai.org/index.php/AAAI/article/view/12209),
  AAAI 2018; this gives a model for certificate-based exact Schur-number work.
