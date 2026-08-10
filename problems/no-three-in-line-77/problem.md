# No-three-in-line at grid size 77

For a positive integer `n`, let

\[
G_n = \{0,1,\ldots,n-1\}^2,
\]

and let `D(n)` be the largest cardinality of a subset of `G_n` containing no
three distinct collinear points.

Determine `D(77)`, or improve either side of the current certified interval

\[
152 \le D(77) \le 154.
\]

The upper bound is elementary: each of the 77 horizontal grid lines contains at
most two selected points. For the lower bound, a 152-point configuration on the
`76 x 76` grid can be embedded unchanged in `G_77`. The initial contribution
records and independently checks such a configuration.

Useful contributions include:

- an exact coordinate certificate with 153 or 154 points;
- a small, reproducible verifier or SAT/CP-SAT encoding;
- a symmetry-restricted result with its precise scope stated;
- a structural lemma constraining hypothetical 153- or 154-point sets;
- a reproducible search improvement or negative search result, clearly
  distinguished from a global impossibility proof; or
- a proof improving the upper bound.

All computational claims should include enough data and code to verify the
claimed implication with exact integer arithmetic. The frontier is active, so a
later contribution may update these baseline bounds without rewriting this
historical statement.

## Frontier sources

- Achim Flammenkamp's maintained
  [No-Three-in-Line database](https://wwwhomes.uni-bielefeld.de/achim/no3in/readme.html),
  updated 2026-08-10, records the first `n = 76` configuration.
- Thomas Prellberg,
  [Constraint Satisfaction Programming for the No-three-in-line Problem](https://arxiv.org/abs/2602.07751),
  describes the recent constraint-programming approach and its earlier advance
  through `n = 60`.

