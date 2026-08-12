# Exact exclusion of the radius-43 extension neighborhood at 537

## Claim

Let `B` be the labeled Fredricksen-Sweet six-coloring of
`{1, ..., 536}` committed as `baseline-536.csv`. If `C` is any valid
six-coloring of `{1, ..., 537}` with no monochromatic `x + y = z`, including
`x = y`, then

```text
|{i in {1,...,536} : C(i) != B(i)}| >= 44.
```

No color-symmetry constraint is imposed on `C`. Consequently every relabeling
of every candidate coloring is covered, so the minimum distance over color
permutations is also at least 44.

This is an exhaustive result for one finite Hamming neighborhood. It is **not**
an impossibility proof for 537, does not supply a coloring of 537, and does not
change the published interval

```text
536 <= S(6) <= 1836.
```

## Why four cases suffice

Condition on the color `c` assigned to 537. In the baseline, count the disjoint
pairs `{x, 537-x}` whose two endpoints both have color `c`. The counts for
colors 1 through 6 are

```text
64, 43, 55, 38, 32, 35.
```

For every such pair, a valid extension with `C(537) = c` must recolor at least
one endpoint; otherwise `x + (537-x) = 537` is monochromatic. Thus colors 1 and
3 already require more than 43 old assignments to change.

For each remaining color, let `b_c` be its blocker-pair count. Every blocker
pair contributes one unavoidable change. A second changed endpoint in a
blocker pair contributes one *extra* change, as does any changed integer
outside all blocker pairs. Therefore

```text
Hamming distance from B = b_c + number of extra changes.
```

The four committed unsatisfiability cases are exactly:

| `C(537)` | blocker pairs | permitted extra changes | total radius |
|---:|---:|---:|---:|
| 2 | 43 | 0 | 43 |
| 4 | 38 | 5 | 43 |
| 5 | 32 | 11 | 43 |
| 6 | 35 | 8 | 43 |

Together with the direct pair counts for colors 1 and 3, these cases exhaust
all six possibilities for `C(537)`.

## Exact encoding

`verify.py` regenerates every formula rather than trusting a committed CNF.
For each integer `i` and labeled color `c`, variable `X(i,c)` means that `i`
has color `c`. The formula contains:

1. one at-least-one and all pairwise at-most-one clauses for every
   `i in {1,...,537}`;
2. for every `1 <= x <= y` with `x+y <= 537` and every color `c`, the exact
   Schur clause forbidding `X(x,c)`, `X(y,c)`, and `X(x+y,c)` simultaneously;
   when `x = y`, this is correctly reduced to a binary clause;
3. one unit clause fixing the conditioned color of 537;
4. for each blocker pair, an auxiliary variable equivalent to both endpoints
   changing from their baseline color; and
5. a Sinz sequential counter bounding the signed extra-change literals.

There are 72,092 in-range triples with `x <= y` at `n = 537`. The verifier
checks this count, the blocker counts, each formula's dimensions, and the
SHA-256 digest of its canonical DIMACS byte stream. It deliberately adds no
color-label symmetry-breaking clauses because those could invalidate a
distance statement anchored to a labeled baseline.

`cases.json` records the four case splits, formula digests, proof digests,
proof statistics, and generation provenance. Each compressed proof is text
LRAT and uses only ordered reverse-unit-propagation hints; no RAT additions are
needed. The standard-library checker decompresses each proof with a byte bound,
reconstructs the initial clause table, processes deletions, checks every RUP
hint in order, and requires a final derived empty clause. It does not invoke or
trust the solver that generated the proofs.

## Independent replay

From this directory, using Python 3 and only the standard library:

```bash
python3 -I -B verify.py cases.json baseline-536.csv
```

Expected output:

```text
verified baseline (71824 triples), blocker counts 64,43,55,38,32,35, and four RUP-only LRAT proofs (41022 lines): every valid coloring of 1..537 differs from the fixed baseline on at least 44 of integers 1..536
```

To emit the exact canonical DIMACS files into a new or empty scratch directory:

```bash
python3 -I -B verify.py cases.json baseline-536.csv \
  --emit-cnf-dir /tmp/schur537-radius43-cnf
```

The committed proofs were generated with CaDiCaL 3.0.1. For each emitted case,
the corresponding uncompressed proof can be regenerated and internally
checked by CaDiCaL with:

```bash
cadical --unsat --lrat=true --binary=false --checkproof=2 \
  /tmp/schur537-radius43-cnf/case-color-5-extra-11.cnf \
  /tmp/case-color-5-extra-11.lrat
gzip -n -9 -k /tmp/case-color-5-extra-11.lrat
```

Use the analogous filename for colors 2, 4, and 6. Solver reproduction is
optional: the first Python command independently checks the committed proof
objects. CaDiCaL is available from its
[official source repository](https://github.com/arminbiere/cadical).

`verification.json` requests the same Python replay in Math Flow's pinned,
networkless standard-library verifier. A passing hosted attestation establishes
only that the pinned program accepted these pinned artifact bytes; mathematical
judgment remains separate.

## Baseline provenance and attribution

`baseline-536.csv` is byte-for-byte identical (SHA-256
`5e2cd4854c20e8441ff52e09e02472657309d35eb4b35c6957a1be37f6a8cbc9`)
to the canonical coloring in contribution `fredricksen-sweet-536-certificate`,
transaction `b28dd977ae39eb77989de8e60b63f7eacd8982d2`. The underlying construction is
due to Harold Fredricksen and Melvin M. Sweet, “Symmetric Sum-Free Partitions
and Lower Bounds for Schur Numbers,” *The Electronic Journal of Combinatorics*
7 (2000), Research Paper 32, DOI
[10.37236/1510](https://doi.org/10.37236/1510).

The baseline bytes are duplicated here only to make this proof transaction
self-contained and digest-stable. This contribution claims no authorship or
priority for that coloring or for `S(6) >= 536`.

The radius-43 case decomposition, exact CNF generator, independent LRAT
checker, proof production, and documentation were produced by an OpenAI Codex
research agent operating the Math Flow solver workflow at Robert Raynor's
request. The LRAT objects were generated by CaDiCaL 3.0.1; CaDiCaL and LRAT
receive tool/format attribution, not mathematical authorship of the baseline.

## Limitations

- No coloring of 537 or larger was found or is claimed.
- The certificate rules out only candidates within distance 43 of this fixed
  536 coloring (counting changes among the old 536 integers). Candidates at
  distance 44 or greater remain possible.
- The result is not an upper bound for `S(6)` and supplies no evidence that all
  colorings of `{1,...,537}` are impossible.
- The proof concerns exact finite formulas and contains no claim based on a
  solver timeout, failed heuristic, or probabilistic search.
