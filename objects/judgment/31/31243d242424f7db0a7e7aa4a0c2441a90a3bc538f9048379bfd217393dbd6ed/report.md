## `no-three-in-line-77/rct4-154-search-instance`

**Verdict: INDETERMINATE**

The handwritten encoding is substantially plausible and its central soundness/completeness argument within the stated `rct4` subclass can be verified statically. However, the exact declared statement contains material scope and execution claims that are not established by the supplied evidence. No terminal objective attestation is present.

### 1. Rotational-symmetry lemma

The following parts are correct:

- For a finite set invariant under a half-turn about \(z\), all nonfixed points occur in pairs \(\{p,2z-p\}\), with \(z\) the only possible fixed point.
- If such a no-three-in-line set has odd cardinality, it contains \(z\); then any other \(p\) produces the forbidden collinear triple
  \[
  p,\ z,\ 2z-p.
  \]
  Thus an odd half-turn-invariant no-three-in-line set has at most one point. This excludes half-turn symmetry for a 153-point set.
- Under a quarter-turn, every noncentral orbit has size four. If the center belongs to a no-three-in-line invariant set, no other orbit can occur because \(p,z,\rho^2(p)\) would be collinear. Hence a nontrivial quarter-turn-invariant no-three-in-line set has cardinality divisible by four. This excludes cardinalities 153 and 154.
- A 154-point set has exactly two points in every row and every column. If it is half-turn-invariant, preservation of the coordinate extrema forces the half-turn center to be \((38,38)\). Its center cannot be occupied, since all other points are paired and an occupied center would make the cardinality odd—or directly create a forbidden midpoint triple.

There are nevertheless two scope defects:

1. The conclusion that a 153-point set has **no rotational symmetry at all** does not follow solely from the supplied half-turn and quarter-turn arguments. A rotation preserving a finite lattice set must indeed ultimately be shown to have order \(2\) or \(4\), but that requires an omitted argument. For example, one can use three noncollinear lattice points to show that the rotation matrix is rational and then classify rational finite-order planar rotation matrices. The submission neither supplies this argument nor explicitly restricts “rotational symmetry” to square-grid automorphisms.

2. The opening assertion that the packaged `rct4` instance is “the only” rotational route is not established by the lemma. The lemma restricts a rotationally symmetric 154-point solution to central half-turn symmetry, but `rct4` is a strict subclass of such half-turn-invariant configurations. It additionally requires:
   - an empty anti-diagonal;
   - full quarter-turn orbits off the diagonals; and
   - exactly one main-diagonal antipodal pair.

   None of these extra conditions follows from half-turn symmetry. The contribution itself acknowledges that the general `rot2` model is omitted. Thus the lemma establishes, at most, the central half-turn **symmetry envelope**, not the exhaustiveness of the packaged `rct4` search route.

These are proof/scope gaps rather than a supplied counterexample to the existence claim, so they support an indeterminate rather than valid verdict.

### 2. Static audit of the `rct4` model

Within the expressly defined `rct4` subclass, the handwritten model is logically well formed:

- Removing the two diagonals leaves
  \[
  77^2-(2\cdot77-1)=76^2=5776
  \]
  cells, partitioned into quarter-turn orbits of size four. Hence there are
  \[
  5776/4=1444
  \]
  off-diagonal orbit variables.
- The main diagonal excluding the center consists of 76 cells paired by the half-turn, giving 38 diagonal-pair variables.
- Selecting 38 off-diagonal orbits and one diagonal pair gives
  \[
  38\cdot4+2=154
  \]
  points.
- `enumerate_lines` uses primitive direction vectors. Any line containing at least three lattice points in \(G_{77}\) has primitive coordinate steps of absolute value at most 38, so the direction bounds are sufficient. The predecessor test selects the first grid point on each maximal line.
- For each enumerated line, the coefficient of a variable is exactly the number of cells from its orbit or pair lying on that line. Thus
  \[
  \sum_v c_vy_v\le2
  \]
  is precisely the no-three-on-that-line condition.
- Every collinear triple of lattice points lies on one of these primitive maximal lines. Consequently, assuming the enumeration executes as written, the line constraints are sound and complete for the no-three-in-line condition in the represented class.
- The CP-SAT solution expansion correctly reconstructs every selected orbit and diagonal pair and then applies an exact determinant-based triple check.
- The handwritten weighted-at-most-two translation in `cmd_export_cnf` is logically correct: coefficients at least three force a variable false; two coefficient-two variables are incompatible; a coefficient-two and coefficient-one variable are incompatible; and every triple of coefficient-one variables is forbidden.

A minor literal discrepancy is that not every maximal grid line produces a stored constraint: lines having fewer than three non-fixed eligible cells are omitted as tautologies, and equivalent expressions are deduplicated. This does not damage the model but makes the prose “every maximal grid line contributes” imprecise.

The asserted numerical count of **388,148** distinct constraints is not derivable from the supplied prose alone and depends on executing the enumeration.

### 3. Certificate-validation claims

The validation path has an appropriate structure:

- certificate decoding yields exactly two entries per row;
- `full_verify` checks distinctness, range, and every triple by exact determinant;
- orbit completeness is checked for occupied off-diagonal points;
- anti-diagonal occupancy is rejected;
- cardinalities and every reduced line constraint are checked.

For these particular certificate inputs, the otherwise incomplete diagonal check in `assignment_from_points` is rescued by the fixed total of \(2n\) decoded points: \(m\) complete four-point off-diagonal orbits account for \(4m\) points, so the remaining two points with one diagonal-pair index must be both members of that pair.

However, the assertions that all five certificates pass, have the listed hashes, and check the listed numbers of constraints are execution claims. The raw files and verifier make them reproducible, but:

- no trusted execution transcript is supplied;
- `results.json` is itself untrusted claimed output; and
- there is no terminal objective attestation pinning an execution of `python3 rct4_search.py results`.

Therefore those finite but substantial determinant and model checks are not affirmatively established by the supplied record.

### 4. Bounded-search report

The negative runs are correctly described as having no implication for satisfiability or for \(D(77)\). Nevertheless, the occurrence of the runs is not reproducibly certified:

- no logs, solver outputs, or content-addressed run artifacts are supplied;
- the table does not give exact commands for all runs;
- the script has no CaDiCaL solve subcommand, so “via the commands above” requires additional unspecified external invocation; and
- the displayed reproduction command for \(n=77\) uses four workers and 3600 seconds, whereas the reported table describes two workers and only “\(\ge45\) min.”

Thus the bounded-search history remains unsupported empirical reporting. It cannot be used for any mathematical conclusion, which the contribution appropriately avoids doing.

### 5. Bounds

The contribution supplies neither a 154-point solution nor an infeasibility proof, so it does not improve the interval. The statement that the bounds remain

\[
152\le D(77)\le154
\]

is consistent with the problem’s supplied baseline.

### Required dependencies

**None.**

- `c5e8096d942d57228bb4fed00f7617fb6b43af9f` is motivational/local-rigidity context and is not needed for the symmetry lemma or the `rct4` encoding.
- `dfc0cc40d41105292a119840dcdbe6f22860cf43` is cited for provenance and an encoding convention, but the alphabet, decoder, model, and calibration certificate data are independently included in the subject. The baseline interval is also supplied directly by the problem.

The references should therefore be preserved as declared references but not treated as accepted-state prerequisites.
