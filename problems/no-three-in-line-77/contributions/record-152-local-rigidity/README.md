# Local rigidity of the 152-point record inside G_77

This contribution certifies, by exhaustive exact-integer computation, that the
certified 152-point no-three-in-line record on the `76 x 76` grid is an
isolated local optimum inside `G_77 = {0,...,76}^2`. It is a negative search
result with a precise scope, not a global impossibility proof: it prunes the
entire "perturb the known record" strategy for reaching 153 or 154 points and
quantifies how different any larger configuration must be.

## Claim

Let `C` be the 152-point configuration decoded from
[`../record-152-certificate/configuration.txt`](../record-152-certificate/configuration.txt),
and let `E` range over the embeddings of `C` into `G_77`, meaning every image
of `C` under the dihedral symmetries of `G_76` followed by a translation by
`(tx, ty)` with `tx, ty` in `{0, 1}`. There are exactly 8 distinct such
embeddings (see "By-product" below). For every embedding `E`:

1. **Saturation (maximality).** Every one of the `77^2 - 152 = 5777` cells of
   `G_77 \ E` is collinear with at least two points of `E` (in fact with at
   least two distinct blocking pairs). Hence no proper superset of `E` in
   `G_77` is a no-three-in-line set; in particular `E` extends to neither 153
   nor 154 points.
2. **One-robust saturation.** For every single point `r` of `E`, the 151-point
   set `E \ {r}` still blocks every cell of `G_77 \ E`. No cell is freed by
   any single removal.
3. **Two-removal accounting.** Removing any unordered pair of points of `E`
   frees at most one cell of `G_77 \ E`. Exactly 16 removal pairs free a cell;
   they are listed exhaustively in [`results.json`](results.json). The 16
   pairs concentrate on 4 freed cells (4 pairs each), and every instance is of
   the "two lines of two" pattern: the freed cell lies on exactly two heavy
   lines, each carrying exactly two configuration points.

**Corollary (certified).** For every embedding `E` and every no-three-in-line
set `S` in `G_77` with `|E \ S| <= 2`, it holds that `|S \ E| <= 1`, hence
`|S| <= 152`. Therefore any hypothetical 153- or 154-point no-three-in-line
set in `G_77` must omit at least 3 points of every embedding of the record and
contain at least 4 points outside it — symmetric difference at least 7 with
every embedding. (Proof of the corollary from claims 1-3: write
`S = (E \ R) ∪ A` with `R = E \ S`, `A = S \ E`. Every cell of `A` must be
free with respect to `E \ R`; for `|R| = 0, 1` there are no free cells, and
for `|R| = 2` there is at most one, so `|A| <= 1` and
`|S| = 152 - |R| + |A| <= 152` whenever `|R| <= 2`.)

A weaker immediate consequence of claim 1 alone: adding two points at once is
also impossible, since each added point would in particular have to be
individually addable.

## By-product: quarter-turn symmetry of the record

The decoded configuration `C` is invariant under the quarter-turn rotation
`(x, y) -> (75 - y, x)` of `G_76`. The checker verifies this exactly. The
existing primary judgment recorded the database's symmetry marker as
recognized but deliberately unverified; this computation supplies the missing
independent verification (relevant to knowledge node
`no-three-in-line/g76-optimal-value`). Consequently the dihedral orbit of `C`
has exactly 2 distinct images, and with the 4 translations this yields the 8
distinct embeddings analyzed here; the checker enumerates all 8 transforms and
4 offsets and deduplicates programmatically, so completeness of the embedding
list does not depend on the symmetry claim.

## Method and assumptions

All computation uses exact integer arithmetic (collinearity via the 2x2
determinant `(x2-x1)(y3-y1) - (x3-x1)(y2-y1)`); there is no floating point and
no randomness. The base configuration and each embedding are re-verified from
scratch (all `C(152,3) = 573,800` triples), so this contribution does not
assume the prior contribution's verifier ran correctly.

Two structurally independent enumerations must agree cell by cell:

- **Line census (primary).** For each outside cell `c`, group the 152
  configuration points by the sign-normalized primitive direction of `p - c`.
  Points are collinear with `c` exactly when they share a direction, so the
  groups of size at least 2 ("heavy lines") determine every blocking pair.
  Because two distinct lines through `c` intersect only at `c`, one removed
  point can lower the census of at most one heavy line, and a heavy line with
  `n` points needs `n - 1` removals. Freeing `c` with at most 2 removals is
  therefore possible only for: one heavy line of 2 (one removal), one heavy
  line of 3 (two removals on it), or two heavy lines of 2 (one removal on
  each). This case analysis is exhaustive, which makes the freeing enumeration
  complete.
- **Line walk (cross-check).** For every pair of configuration points, walk
  the full lattice line through the pair in primitive steps in both
  directions, recording every visited cell of `G_77`. This yields, for each
  cell, the explicit list of blocking pairs; minimal freeing sets are
  re-derived from these lists as minimum hitting sets. Per-cell pair counts
  and freeing sets must match the census exactly.

Finally, every reported freeing is re-verified by direct simulation (remove
the pair, test the freed cell against all `C(150,2)` remaining pairs),
and the assembled results must byte-match the committed `results.json`.

## Reproduction

From this directory:

```bash
python3 rigidity.py            # verifies every claim against results.json; exit 0 on success
python3 rigidity.py --write    # regenerates results.json
```

Requires only the Python 3 standard library (developed on CPython 3.11).
Deterministic; runs in about 4 seconds on a laptop. Expected final line:

```text
verified: all 8 embeddings of the 152-point record are maximal in G_77, ...
```

## Provenance and reused work

- Input configuration: `configuration.txt` from the prior contribution
  `record-152-certificate`, added in transaction
  `dfc0cc40d41105292a119840dcdbe6f22860cf43`. The file is read in place and
  not copied; its SHA-256
  (`a23f1f55d9a914cff49fb6ba369b9f392f7af4c5ce08085267b3af1e7d7742c4`) is
  pinned in `results.json`. The decoding convention (marker character, then
  two alphabet-encoded x coordinates per row) follows that contribution's
  README; the decoder here is an independent re-implementation.
- The underlying configuration is attributed to Achim Flammenkamp's
  maintained [No-Three-in-Line database](https://wwwhomes.uni-bielefeld.de/achim/no3in/readme.html)
  (n = 76 record), as recorded by the prior contribution and by primary
  judgment `sha256:6be1b72404002801ac782c66d7202888309fdf73c68b6ecb63633b3c163bcb8f`.
- Knowledge nodes addressed (projection `openrouter-research-v1`, state digest
  `sha256:0f96d2d379beff463bddb82914902718acf30ff15bb8a35db1ca3c2a7aea1884`):
  primarily the open question `no-three-in-line/d77-exact-value` (constrains
  where a 153- or 154-point set can be found); secondarily
  `no-three-in-line/g76-optimal-value` (verifies the flagged quarter-turn
  symmetry) and `no-three-in-line/d77-near-extremal-occupancy` (independent,
  complementary constraints).

This contribution is presented as evidence for future adjudication; it does
not modify the certified interval `152 <= D(77) <= 154` or any prior record.

## Known gaps and limitations

- The result is local: it says nothing about no-three-in-line sets far from
  the record embeddings, and it does not decide `D(77)`, which remains open
  among 152, 153, and 154.
- The scope is exactly the 8 embeddings of this particular record
  configuration. Other 152-point configurations in `G_77` (if any exist) are
  not covered.
- Neighborhoods of removal depth 3 or more are not explored; the symmetric
  difference bound of 7 is what depth 2 supports and is not claimed to be
  sharp.
- No failed checks: both enumeration methods, the direct simulations, and the
  byte-comparison against `results.json` all pass.

## Authorship

Analysis, code, and text were produced by an AI research agent (Cursor agent,
model Fable 5) operating the repository's math-flow-solver workflow at
Robert's request, building fresh verified context from the
`openrouter-research-v1` projection. The base configuration is Achim
Flammenkamp's (see provenance); the prior packaging and verification of that
configuration are credited to the `record-152-certificate` contribution.
