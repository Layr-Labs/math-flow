# Validated rct4 search instance for a 154-point set in G_77

This contribution packages the one viable *rotational* route to resolving
`D(77) = 154` as an exact, validated, reusable search instance, together with
a small symmetry lemma that proves it is the only such route, and an
honestly-scoped report of bounded search attempts that did not find a
solution. It changes no bounds: `152 <= D(77) <= 154` and the open question
`no-three-in-line/d77-exact-value` remain exactly as certified.

## Context: an unverified breakthrough report

This work was prompted by a private-channel report (received 2026-08-11,
without any artifact) of a breakthrough on `D(77)`. Public sources were
checked immediately before packaging:

- Achim Flammenkamp's No-Three-in-Line database
  ([readme](https://wwwhomes.uni-bielefeld.de/achim/no3in/readme.html), page
  dated 2026-08-10 19:57 UTC+2) records `n = 76` (Marijn Heule, rot4 class)
  as the largest solved size; odd sizes 71, 73, 75, 77 have no recorded
  2n-point solution and the largest solved odd size is 69.
- The database's
  [`all_known_solutions`](https://wwwhomes.uni-bielefeld.de/~achim/no3in/download/all_known_solutions)
  download (retrieved 2026-08-11T01:13Z, 23,830,822 bytes) contains no line of
  length 155, i.e. no `n = 77` configuration; the longest entries have length
  153 (`n = 76`).
- No preprint or other public trace of a 77 result was found.

The report is therefore treated as an unverified claim: this contribution
neither confirms nor refutes it. What it does is reproduce, validate, and
package the exact search pipeline that produced every known odd-size record,
instantiated at `n = 77`, so that adequately provisioned solvers can attack
or audit the claim.

## Lemma: available rotational symmetry at sizes 153 and 154

Let `S` be a no-three-in-line subset of `G_77` (all statements below hold for
any grid). Write a *half-turn* for a 180-degree rotation about any center
point `z` of the plane and a *quarter-turn* for a 90-degree rotation about any
center.

1. **Half-turn-invariant sets of odd size do not exist (beyond one point).**
   If `S` is invariant under the half-turn about `z` and `|S|` is odd, some
   point is fixed (the map pairs `p` with its reflection `2z - p`, whose only
   fixed point is `z`), so `z` is a grid point of `S`. But then for any other
   `p` in `S`, the three points `p`, `z`, `2z - p` are distinct and collinear
   (`z` is the midpoint of the segment). Hence `|S| <= 1`. In particular **no
   153-point set has a half-turn symmetry about any center.**
2. **Quarter-turn invariance forces size 0 or 1 modulo 4.** An order-4
   rotation has orbits of size 4 except for its single fixed point (an orbit
   of size 2 would consist of a point fixed by the half-turn square of the
   rotation, and only `z` is). A quarter-turn-invariant `S` is also invariant
   under the half-turn about the same center, so by (1) it either equals
   `{z}` or excludes `z` and has `|S| = 0 (mod 4)`. Since `153 = 1 (mod 4)`
   requires `z` in `S` (impossible for `|S| > 1`) and `154 = 2 (mod 4)`, **no
   153- or 154-point set has a quarter-turn symmetry about any center.**
3. **A 154-point half-turn symmetry can only be about the grid center.** A
   154-point set has exactly two points in every row and every column (the
   canonical occupancy constraint), so its bounding box is all of `G_77`; a
   half-turn preserving the set preserves the bounding box, forcing the
   center `z = (38, 38)`, which by (1) is not in `S`.

Consequently the only rotational symmetry available above 152 points is:
`|S| = 154`, half-turn about `(38, 38)`, center unoccupied. The **rct4
pattern** used for every known odd-size record (`n = 47` through `69`;
database marker `c`) is exactly such a structure with additional partial
quarter-turn regularity, and it is what this instance encodes. A 153-point
set, if one exists, has no rotational symmetry at all; only reflection
symmetry or none.

## The rct4 pattern and the exact model

Following Prellberg, [Constraint Satisfaction Programming for the
No-three-in-line Problem](https://arxiv.org/abs/2602.07751) (whose Table 1
constructions and database markers define the class), with
`rho(i, j) = (j, 76 - i)` the quarter-turn about `(38, 38)`:

- the anti-diagonal `{(i, 76 - i)}` is empty;
- off-diagonal occupied cells form full `rho`-orbits of size 4;
- exactly one main-diagonal pair `{(i, i), (76 - i, 76 - i)}`, `i != 38`, is
  occupied (a `rho^2`-orbit; note such a set is `rho^2`-invariant but not
  `rho`-invariant, consistent with the lemma).

Choosing 38 off-diagonal orbits plus one diagonal pair gives
`4 * 38 + 2 = 154` points. The model has one Boolean per off-diagonal orbit
(1444) and one per diagonal pair (38). Every maximal grid line carrying at
least 3 lattice points contributes `sum(coeff * y) <= 2` after mapping cells
to orbit variables (388,148 distinct constraints at `n = 77` after
deduplication, which realizes the `rho^2` line-orbit reduction); cardinality
constraints fix 38 chosen orbits and 1 chosen pair. Any three collinear grid
points lie on an enumerated line, and cells of the anti-diagonal are fixed
empty, so feasible assignments correspond exactly to rct4-pattern 154-point
no-three-in-line sets (soundness and completeness within the class). Every
solver output is additionally re-verified point-by-point by the exhaustive
exact-integer triple test before being reported.

## Validation against known certificates

`known_certificates.txt` reproduces five `c`-class lines from the database
download (sizes 41, 47, 57, 65, 69; SHA-256 of the file and of each line are
pinned in `results.json`). For each one, `check-known`:

1. decodes it (marker character, then two alphabet-encoded x-coordinates per
   row, the convention documented in `record-152-certificate`);
2. verifies the no-three-in-line property exhaustively in exact integers;
3. decomposes it into the class structure (38-type orbit counts, one diagonal
   pair, empty anti-diagonal); and
4. checks it satisfies every constraint of this model at its size.

All five pass. This establishes that the encoding does not exclude real
solutions of the class it targets, and that the class is *satisfiable* at the
calibration sizes used below.

## Reproduction

From this directory (validation is Python-stdlib-only):

```bash
python3 rct4_search.py check-known     # decode + verify + model-check the 5 certificates
python3 rct4_search.py results         # recompute everything deterministic vs results.json
```

Search and export (tested with Python 3.12.3, `ortools` 9.15.6755,
`python-sat` 1.9.dev12):

```bash
python3 rct4_search.py solve 77 --seed 7 --time 3600 --workers 4 --out sol77.json
python3 rct4_search.py export-cnf 77 --out n77.cnf     # DIMACS for any SAT solver
python3 rct4_search.py verify sol77.json 77            # exact check of any claimed list
```

`results --write` regenerates `results.json`. The `results` run takes about
one minute; building the `n = 77` model takes about 10 seconds.

## Bounded search report (negative, hardware-scoped)

All runs below on a 4-core cloud VM (15 GB RAM), OR-Tools CP-SAT and CaDiCaL
1.9.5 via the commands above. **These are budget statements, not evidence of
nonexistence**: the class is provably satisfiable at `n = 41` and `n = 47`
(committed witnesses), yet the same pipeline also failed to find those within
similar budgets, demonstrating that this hardware scale is far below what the
instance family needs. For comparison, the literature's `n <= 60` results
used 384 parallel runs with multi-day horizons, and sizes 65-76 required
specialized new SAT solvers.

| target | engine | budget and seed | outcome |
| --- | --- | --- | --- |
| n=41 (satisfiable) | CP-SAT, 4 workers | 300 s, seed 1 | no solution (UNKNOWN) |
| n=47 (satisfiable) | CP-SAT, 4 workers | 600 s, seed 1 | no solution (UNKNOWN) |
| n=41 (satisfiable) | CaDiCaL 1.9.5 via python-sat, same clause encoding | 420 s | no result (timeout) |
| n=77 (this instance) | CP-SAT, 2 workers | seed 7, >= 45 min | no solution |
| n=77 (this instance) | CaDiCaL 1.9.5 via python-sat, same clause encoding | >= 45 min | no result |

An exploratory stochastic local search over orbit space (not part of this
artifact) plateaued at 17 violated lines at `n = 41` and was not competitive.
No run returned INFEASIBLE at any size; nothing here bounds `D(77)`.

## Provenance and reused work

- Knowledge state: projection `openrouter-research-v1`, verified `current` at
  canonical problem head `c5e8096d942d57228bb4fed00f7617fb6b43af9f`, state
  digest `sha256:a3ace33ff5d4fea1127568d4e20c771a5e90b5b25c730ac7be610b4d1cb2a708`.
  Primary nodes addressed: the open question `no-three-in-line/d77-exact-value`
  and the occupancy lemma `no-three-in-line/d77-near-capacity-occupancy`
  (judgment `sha256:a470e4a9c0903097d9c860badaa8976cf32ed5336c154f11d8fad980d401f74e`);
  the local-rigidity nodes, e.g.
  `no-three-in-line/d77-distance-from-embedded-g76-152-record`
  (judgment `sha256:71fbde8d269728a92be52f6401e857230043ee6938c45f810c32308d88fb9927`),
  motivate a global symmetric search by closing the perturbative route to 153.
- Certificate encoding convention: contribution `record-152-certificate`
  (transaction `dfc0cc40d41105292a119840dcdbe6f22860cf43`).
- `known_certificates.txt` lines are reproduced verbatim from Achim
  Flammenkamp's database download (retrieved 2026-08-11T01:13Z) so the
  validation does not depend on a mutable web page. Per the database history,
  the record discoveries at these sizes are credited to the database's
  contributors, including Thomas Prellberg (first odd-size records through
  `n = 63`) and Marijn Heule (`n = 65` through `n = 76`); this contribution
  claims no originality for them.
- Class definition and symmetry-reduction methodology: Prellberg,
  arXiv:2602.07751. The model here is an independent implementation of that
  specification.

## Known gaps and limitations

- No change to the certified interval; no existence or nonexistence evidence
  for 153 or 154 points. The private-channel breakthrough report remains
  unverified in both directions.
- The instance covers the rct4 pattern only. General half-turn (rot2)
  configurations satisfy a weaker symmetry (the lemma shows rot2 about the
  center is the full rotational envelope at 154); a rot2-general model has
  roughly twice the variables and is not included. Reflection-symmetric and
  asymmetric searches (the only options at 153) are likewise out of scope.
- The negative search table reflects small budgets on small hardware and
  carries no weight about satisfiability of the `n = 77` instance.
- The lemma constrains rotations only; it says nothing about reflection or
  glide symmetries.

## Authorship

Analysis, lemma, code, and text by an AI research agent (Cursor cloud agent,
model Fable 5) operating the repository's math-flow-solver workflow at
Robert's request, as a replication attempt for a privately reported
breakthrough. Reproduced certificates and the class definition are credited
above; errors are the agent's.
