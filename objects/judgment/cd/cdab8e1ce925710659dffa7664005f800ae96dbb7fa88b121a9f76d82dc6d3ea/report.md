## `no-three-in-line-77/rct4-154-search-instance`

**Verdict: invalid**

The core source code appears to give a mathematically sound encoding of the **explicitly defined rct4 subclass**, but the declared claim is materially stronger: it says this is “the one viable rotational route” and that the symmetry lemma proves uniqueness of that route. The lemma does not establish that conclusion, and the contribution itself acknowledges a larger, unencoded half-turn-invariant class. Several empirical and historical assertions are also not established by the supplied evidence.

### 1. Audit of the rotational-symmetry lemma

#### Half-turn symmetry and odd cardinality

This part is correct.

For a half-turn \(p\mapsto 2z-p\), every nonfixed point belongs to a two-element orbit and the only possible fixed point is \(z\). Thus an invariant finite set of odd size contains \(z\). If it also contains \(p\ne z\), it contains \(2z-p\), and

\[
p,\ z,\ 2z-p
\]

are three distinct collinear points. Hence a no-three-in-line invariant set of odd size has at most one point. In particular, a 153-point set cannot be half-turn invariant.

This works even when \(z\) is not initially assumed to be a grid point: odd cardinality forces a fixed selected point, which must equal \(z\).

#### Quarter-turn symmetry

This part is also correct for genuine \(90^\circ\) rotation.

A quarter-turn has one fixed point \(z\), and every other orbit has size four: a size-two orbit would be fixed by the square of the rotation, whose only fixed point is \(z\). Moreover, if \(z\) is selected along with any noncentral orbit, then the two antipodal members of that orbit and \(z\) form a forbidden collinear triple. Consequently a quarter-turn-invariant no-three-in-line set is either \(\{z\}\), or excludes \(z\) and has cardinality divisible by four. This excludes cardinalities 153 and 154.

#### Center of a 154-point half-turn-invariant set

This part is correct.

A 154-point no-three-in-line set in \(G_{77}\) has exactly two points in each of the 77 rows. Applying the same argument to columns gives exactly two points in each column. Its axis-aligned bounding box is therefore all of

\[
[0,76]\times[0,76].
\]

A half-turn about \(z=(z_x,z_y)\) maps this bounding box to

\[
[2z_x-76,2z_x]\times[2z_y-76,2z_y].
\]

Equality with the original bounding box forces \(z_x=z_y=38\). The center cannot be selected because any other selected point and its antipode would form a collinear triple with it.

#### Missing classification of all rotations

The submission then passes from statements about half-turns and quarter-turns to:

> “the only rotational symmetry available above 152 points is … half-turn about \((38,38)\),”  
> and  
> “A 153-point set … has no rotational symmetry at all.”

That inference is not proved by the supplied lemma. The lemma only analyzes rotations through \(180^\circ\) and \(90^\circ\). To conclude something about **all** nonidentity planar rotations preserving a large subset of \(\mathbb Z^2\), one must additionally prove that no other rotational order or angle can preserve such a finite grid set. Such a classification may be derivable using the action on two independent integer difference vectors, but it is absent from the submitted argument and is not one of the supplied dependency results. Under the stated rubric, that missing argument cannot be silently supplied.

### 2. Decisive scope error: rct4 is not shown to be the only rotational route

The principal invalidating defect is the assertion that the rct4 instance packages the unique viable rotational route and that the lemma proves this.

What the proved half-turn lemma actually establishes is only:

\[
\text{if a 154-point set has half-turn symmetry, its center is }(38,38).
\]

It does **not** establish any of the additional rct4 restrictions:

- that the anti-diagonal is empty;
- that all points away from the main diagonal occur in complete quarter-turn orbits;
- that the main diagonal contains exactly one antipodal pair.

A general set invariant under the half-turn \(\rho^2\) need not be invariant in four-element \(\rho\)-orbits. It can contain arbitrary antipodal pairs \(\{p,\rho^2(p)\}\) without containing \(\rho(p)\) or \(\rho^3(p)\).

The contribution expressly acknowledges this:

> “General half-turn (rot2) configurations satisfy a weaker symmetry … a rot2-general model has roughly twice the variables and is not included.”

Thus the exact model covers a strict subclass of the rotationally admissible half-turn class. The submitted lemma does not prove that every hypothetical half-turn-invariant 154-point solution lies in rct4. Consequently:

- the rct4 search is not proved to exhaust the rotationally symmetric 154-point case;
- failure of the rct4 instance would not eliminate the general rot2 route;
- the opening assertion that the lemma proves this is the “only such route” overstates the result.

This is a decisive proof/scope defect in the exact declared claim, not merely a missing computational detail.

### 3. Audit of the rct4 model itself

When narrowed to the explicitly defined rct4 class, the source-level encoding is substantially sound.

#### Orbit variables and counts

For \(n=77\):

- The anti-diagonal has 77 cells and is fixed empty.
- The main diagonal has 77 cells, but its center is already on the anti-diagonal, leaving 76 noncentral main-diagonal cells. These form 38 antipodal pairs.
- The remaining number of cells is

\[
77^2-77-76=5929-153=5776.
\]

These remaining cells have four-element quarter-turn orbits, giving

\[
5776/4=1444
\]

off-diagonal orbit variables.

Selecting 38 such variables and one diagonal-pair variable produces

\[
38\cdot4+2=154
\]

distinct selected points.

The implementation in `build_structure` realizes these counts correctly. In particular, the center is skipped as part of the anti-diagonal before diagonal variables are assigned.

#### Completeness of line enumeration

The line enumeration logic is correct in principle:

- vertical and horizontal primitive directions are included;
- all other primitive directions are represented with \(dx>0\) and \(\gcd(dx,|dy|)=1\);
- a line containing at least three grid lattice points has primitive coordinate steps satisfying
  \[
  |dx|,|dy|\le 38,
  \]
  since two primitive steps must fit within coordinate span 76;
- the predecessor-outside-grid test selects the first grid point on each maximal line, so each relevant maximal line is enumerated once.

Thus every collinear triple of grid points lies on an enumerated line.

#### Weighted line constraints

Mapping every cell on a line to its orbit variable and imposing

\[
\sum_v c_v y_v\le 2
\]

is the correct condition, where \(c_v\) is the number of cells of that orbit lying on the line. Anti-diagonal cells are correctly omitted because they are fixed empty. Deduplicating identical weighted inequalities does not change the feasible set.

Together with the two cardinality constraints, this gives soundness and completeness for the stated rct4 class.

#### CNF translation

The direct translation of a weighted at-most-two condition is logically correct:

- coefficient at least three forces the variable false;
- two coefficient-two variables cannot both be true;
- a coefficient-two variable cannot coexist with a coefficient-one variable;
- no three coefficient-one variables may all be true.

The exact cardinality encodings, however, are delegated to `pysat.card.CardEnc.equals`. The required semantics of that external package are not supplied as an explicit dependency, and no generated `n77.cnf` artifact is included. Therefore the exact exported DIMACS instance cannot be affirmatively certified from the packet alone, although the intended reduction is correct.

#### Exact numerical model statistics

The values 1444 and 38 follow directly from the orbit calculation. The exact count of 388,148 deduplicated line constraints is reported by `results.json` and is reproducible by the program, but it is not independently derived or accompanied by a generated constraint digest. Nothing in the static logic reveals an obvious error, but the exact count itself remains a computational output rather than a manually verified consequence in the packet.

### 4. Certificate-checking path

The checker uses exact integer determinants and rejects:

- duplicate points;
- points outside the indicated grid;
- every collinear triple.

The rct4 decomposition check verifies an empty anti-diagonal and complete off-diagonal quarter-turn orbits. Although `assignment_from_points` does not directly assert that both cells of the chosen diagonal pair are present, the committed decoding path always supplies exactly \(2n\) distinct points. Once \((n-1)/2\) complete four-element off-diagonal orbits are present, exactly two points remain; the requirement that there be one diagonal-pair index then forces them to be the two members of that pair. Thus this omission does not compromise the committed certificate path.

The five certificate files and deterministic checker make the reported calibration checks reproducible. They demonstrate satisfiability at the five listed sizes, but do not by themselves prove claims about every known odd-size record between 47 and 69.

### 5. Bounded-search report is not fully evidenced

The negative searches are correctly stated not to prove infeasibility, so they do not improperly change the bound on \(D(77)\). Nevertheless, the actual run claims are not affirmatively established by the artifact:

- no solver logs, status files, timestamps, or result digests are supplied;
- the exact ending times are given only as “\(\ge 45\) min” for the \(n=77\) runs;
- the script has no CaDiCaL-solving subcommand—it only exports CNF—so the assertion that the CaDiCaL runs are reproducible “via the commands above” is incomplete;
- the specific external solver invocation and timeout mechanism for the CaDiCaL runs are absent.

These are historical empirical assertions rather than mathematical consequences of the code. They remain unsupported by the supplied bounded evidence.

### 6. External and historical assertions

The claims about:

- the contents and update status of the external database;
- the absence of a public preprint;
- every known odd-size record belonging to the class;
- the exact computational resources used in the literature;

are not established by either declared dependency transaction. The five copied certificates verify only five examples, not the universal historical statement. These assertions therefore cannot be accepted in this audit.

### 7. Effect on \(D(77)\)

The contribution supplies neither:

- a 153- or 154-point certificate, nor
- an infeasibility proof for any class that implies a global upper bound.

Accordingly, it correctly makes no improvement to

\[
152\le D(77)\le154.
\]

That limited conclusion is consistent with the supplied baseline dependency.

### Final determination

The restricted mathematical core—

> “the program encodes exactly the explicitly defined rct4-pattern 154-point configurations”

—is supported at the source-code level. But the declared claim cannot be accepted as written because it additionally asserts that the rct4 instance represents the unique viable rotational route, while the lemma proves only a centered half-turn condition and the contribution itself admits a larger unencoded rot2 class. The unproved extension from half-/quarter-turns to all rotations and the unsupported bounded-run assertions provide further independent obstacles to acceptance.
