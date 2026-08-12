# Knowledge-Formation Report

## Formation summary

The supplied primary judgment adds several durable symmetry and modeling results while leaving the global problem unchanged:

\[
152\le D(77)\le154,
\qquad
D(77)\in\{152,153,154\}.
\]

The following organizational actions are supported:

1. Update the root research state to include the accepted symmetry obstructions, the centered half-turn condition for a hypothetical 154-point set, the qualified scope of the rotational-symmetry classification, and the exact restricted rct4 model.
2. Update the existing exact-value question to record that these results do not determine \(D(77)\) or narrow its certified interval.
3. Create four durable nodes:
   - general half-turn and quarter-turn cardinality obstructions;
   - the centered half-turn condition for a 154-point subset of \(G_{77}\);
   - the qualified rotational-symmetry classification at cardinalities 153 and 154;
   - the exact rct4 model and its unresolved satisfiability.

The calibration certificates and bounded solver runs are incorporated into the rct4 model node rather than represented as event-shaped nodes. No conflict records or reconciliation outcomes were supplied, so no active adjudicative dispute node is required. The unresolved exact value and unresolved rct4 satisfiability are evidentiary uncertainties, not conflicts between judgments.

---

## Node: root

- **Type:** Root research state
- **Status:** Active
- **Parent:** None
- **Primary judgment provenance:**
  - `sha256:a470e4a9c0903097d9c860badaa8976cf32ed5336c154f11d8fad980d401f74e`
  - `sha256:71fbde8d269728a92be52f6401e857230043ee6938c45f810c32308d88fb9927`
  - `sha256:d24a70c16a08ff85401e969cfe12d8f8253056bb8d75e469ec226eba7a3b44c5`
- **Evidence transactions:**
  - `dfc0cc40d41105292a119840dcdbe6f22860cf43`
  - `c5e8096d942d57228bb4fed00f7617fb6b43af9f`
  - `c98dd877ad81611a9a469b1bd790cd909b56b1ce`

For

\[
G_n=\{0,1,\ldots,n-1\}^2,
\]

let \(D(n)\) be the largest cardinality of a subset of \(G_n\) containing no three distinct collinear points.

The current judge-established research state at grid size \(77\) is as follows.

### Certified configuration and global bounds

1. A particular 152-point no-three-in-line subset \(C\subseteq G_{76}\) has an exact coordinate certificate. Its no-three-in-line property was checked over all

   \[
   \binom{152}{3}=573{,}800
   \]

   triples using exact integer determinants.

2. The configuration is invariant under the quarter-turn

   \[
   (x,y)\longmapsto(75-y,x).
   \]

   It has exactly two distinct images under the eight dihedral symmetries of the square. Applying the four translations in \(\{0,1\}^2\) to those images gives exactly eight distinct specified embeddings in \(G_{77}\).

3. The globally certified interval remains

   \[
   152\le D(77)\le154.
   \]

   The lower bound follows from embedding the verified 152-point configuration. The upper bound follows from the row-capacity argument: each of the 77 rows contains at most two selected points.

4. The necessary row and column occupancy constraints for hypothetical 153- and 154-point sets remain active and unchanged.

### Local rigidity around the eight specified embeddings

5. Each specified embedding is saturated in \(G_{77}\): every one of its 5,777 outside cells is blocked by at least two pairs of embedded points. Each embedding is therefore inclusion-maximal, without thereby being established as maximum-cardinality.

6. Removing one point from a specified embedding makes no originally outside cell addable. The removed point itself can still be restored.

7. Removing any two points from a specified embedding frees at most one originally outside cell. For each embedding, exactly 16 unordered removal pairs free a cell, distributed over four cells with four removal pairs per cell.

8. For every specified embedding \(E\), any no-three-in-line set \(S\subseteq G_{77}\) satisfying

   \[
   |E\setminus S|\le2
   \]

   also satisfies

   \[
   |S\setminus E|\le1
   \quad\text{and}\quad
   |S|\le152.
   \]

   Consequently, every no-three-in-line set \(S\subseteq G_{77}\) with \(|S|\ge153\) must satisfy, relative to each specified embedding,

   \[
   |E\setminus S|\ge3,\qquad
   |S\setminus E|\ge4,\qquad
   |E\triangle S|\ge7.
   \]

### Rotational-cardinality constraints

9. Judgment `sha256:d24a70c16a08ff85401e969cfe12d8f8253056bb8d75e469ec226eba7a3b44c5` accepts the general conclusion that an odd-cardinality no-three-in-line set invariant under a half-turn has at most one point. In particular, a 153-point no-three-in-line set cannot have half-turn symmetry about any center.

10. The same judgment accepts that a quarter-turn-invariant no-three-in-line set has cardinality divisible by four or equal to one. Thus neither a 153-point nor a 154-point no-three-in-line set can be quarter-turn invariant.

11. The judgment accepts that if a 154-point no-three-in-line subset of \(G_{77}\) is invariant under a half-turn, then the half-turn must be centered at

    \[
    (38,38),
    \]

    and this center is unoccupied.

12. The broader statement that centered half-turn symmetry is the only possible nontrivial rotational symmetry type at cardinality 154 is qualified rather than fully established by the supplied written argument. If rotations about arbitrary plane centers are intended, the contribution omits an explicit classification excluding other finite-order lattice rotations. If “rotational symmetry” is restricted to rotations in the dihedral symmetry group of the square grid, this is a terminological rather than substantive gap.

13. The rct4 subclass is strictly narrower than the class of all centered half-turn-invariant configurations. It additionally requires an empty anti-diagonal, complete quarter-turn orbits away from the diagonals, and exactly one selected half-turn pair on the main diagonal.

### Exact restricted rct4 model

14. Static inspection in judgment `sha256:d24a70c16a08ff85401e969cfe12d8f8253056bb8d75e469ec226eba7a3b44c5` supports, with high confidence, that the supplied \(n=77\) model is sound and complete for the stated 154-point rct4 subclass.

15. The model has:
    - 1,444 off-diagonal quarter-turn-orbit variables;
    - 38 main-diagonal half-turn-pair variables;
    - exact cardinality conditions selecting 38 off-diagonal orbits and one diagonal pair;
    - 388,148 deduplicated weighted line constraints generated with exact integer arithmetic.

    Every feasible assignment therefore represents

    \[
    4\cdot38+2=154
    \]

    selected points satisfying the rct4 pattern, and the accepted model equivalence says that feasibility is exactly equivalent to the no-three-in-line property within that subclass.

16. Five committed calibration certificates at

    \[
    n=41,47,57,65,69
    \]

    provide exact implementation regression checks at those sizes. The judgment does not treat them as proof of a broader historical range claim, external provenance, or discovery priority.

17. The satisfiability of the \(n=77\) rct4 instance remains unresolved. Reported `UNKNOWN` results and timeouts establish neither satisfiability nor unsatisfiability. The lack of committed logs or proof traces, together with comparable failures on known satisfiable calibration sizes, gives the timeouts no negative mathematical force.

### Global unresolved question

18. The exact value of \(D(77)\) remains unresolved. The current possibilities are

    \[
    D(77)\in\{152,153,154\}.
    \]

    There is still no supplied 153- or 154-point certificate and no global impossibility proof for either cardinality. The embedding-rigidity results are local, and the rct4 model concerns only a strict symmetry-restricted subclass.

### Current node inventory

- `no-three-in-line/g76-152-point-set`
- `no-three-in-line/d77-certified-interval`
- `no-three-in-line/d77-near-capacity-occupancy`
- `no-three-in-line/d77-saturation-of-embedded-g76-152-record`
- `no-three-in-line/d77-one-removal-robustness-of-embedded-g76-record`
- `no-three-in-line/d77-two-removal-rigidity-of-embedded-g76-record`
- `no-three-in-line/d77-distance-from-embedded-g76-152-record`
- `no-three-in-line/rotational-cardinality-obstructions`
- `no-three-in-line/d77-154-centered-half-turn-condition`
- `no-three-in-line/d77-rotational-symmetry-at-153-154`
- `no-three-in-line/d77-rct4-154-model`
- `no-three-in-line/d77-exact-value`

There are no active adjudicative conflicts in the supplied record.

---

## Node: no-three-in-line/rotational-cardinality-obstructions

- **Type:** Structural theorem
- **Status:** Accepted
- **Parent:** `root`
- **Primary judgment provenance:** `sha256:d24a70c16a08ff85401e969cfe12d8f8253056bb8d75e469ec226eba7a3b44c5`
- **Evidence transaction:** `c98dd877ad81611a9a469b1bd790cd909b56b1ce`
- **Related nodes:**
  - `no-three-in-line/d77-154-centered-half-turn-condition`
  - `no-three-in-line/d77-rotational-symmetry-at-153-154`
  - `no-three-in-line/d77-exact-value`

Judgment `sha256:d24a70c16a08ff85401e969cfe12d8f8253056bb8d75e469ec226eba7a3b44c5` accepts the following two cardinality obstructions for no-three-in-line sets.

### Half-turn obstruction

Let \(S\) be a finite no-three-in-line set invariant under the half-turn

\[
p\longmapsto2z-p
\]

about a point \(z\). If \(|S|\) is odd, then

\[
|S|\le1.
\]

The judgment therefore accepts the specific consequence that a 153-point no-three-in-line set cannot be invariant under a half-turn about any center. The conclusion does not require the center to have been assumed to be a grid point.

### Quarter-turn obstruction

A no-three-in-line set invariant under a quarter-turn has cardinality either divisible by four or equal to one. Consequently, neither cardinality

\[
153\quad\text{nor}\quad154
\]

is possible for a quarter-turn-invariant no-three-in-line set.

These are symmetry-conditional obstructions. They do not exclude asymmetric configurations, reflection-symmetric configurations, or every configuration covered by a broader notion of rotational symmetry whose lattice-rotation classification has not been supplied.

---

## Node: no-three-in-line/d77-154-centered-half-turn-condition

- **Type:** Necessary structural condition
- **Status:** Accepted
- **Parent:** `root`
- **Primary judgment provenance:** `sha256:d24a70c16a08ff85401e969cfe12d8f8253056bb8d75e469ec226eba7a3b44c5`
- **Evidence transaction:** `c98dd877ad81611a9a469b1bd790cd909b56b1ce`
- **Related nodes:**
  - `no-three-in-line/rotational-cardinality-obstructions`
  - `no-three-in-line/d77-rotational-symmetry-at-153-154`
  - `no-three-in-line/d77-rct4-154-model`
  - `no-three-in-line/d77-exact-value`

Judgment `sha256:d24a70c16a08ff85401e969cfe12d8f8253056bb8d75e469ec226eba7a3b44c5` accepts the following necessary condition.

If \(S\subseteq G_{77}\) is a 154-point no-three-in-line set invariant under a half-turn, then:

1. every one of the 77 rows contains exactly two points of \(S\);
2. every one of the 77 columns contains exactly two points of \(S\);
3. the half-turn is centered at the grid center

   \[
   (38,38);
   \]

4. the center \((38,38)\) is not selected.

This result constrains every half-turn-invariant 154-point configuration, not merely the rct4 subclass. It does not assert that such a configuration exists or that every hypothetical 154-point configuration must have half-turn symmetry.

---

## Node: no-three-in-line/d77-rotational-symmetry-at-153-154

- **Type:** Qualified structural classification
- **Status:** Active with scope qualification
- **Parent:** `root`
- **Primary judgment provenance:** `sha256:d24a70c16a08ff85401e969cfe12d8f8253056bb8d75e469ec226eba7a3b44c5`
- **Evidence transaction:** `c98dd877ad81611a9a469b1bd790cd909b56b1ce`
- **Related nodes:**
  - `no-three-in-line/rotational-cardinality-obstructions`
  - `no-three-in-line/d77-154-centered-half-turn-condition`
  - `no-three-in-line/d77-rct4-154-model`
  - `no-three-in-line/d77-exact-value`

The supplied judgment accepts the following established components:

- a 153-point no-three-in-line set cannot have half-turn symmetry;
- neither a 153-point nor a 154-point no-three-in-line set can have quarter-turn symmetry;
- any half-turn symmetry of a 154-point no-three-in-line subset of \(G_{77}\) must be the centered half-turn about \((38,38)\).

The same judgment qualifies the broader claim that centered half-turn symmetry is the only possible nontrivial rotational symmetry type above 152 points.

### Scope qualification

The written contribution analyzes rotations of orders two and four but does not explicitly classify all finite-order rotations about arbitrary centers that could preserve a finite noncollinear subset of the integer lattice. The judgment describes the missing classification as short and repairable, but does not treat the omitted step as already supplied by the contribution.

Accordingly:

- if “rotational symmetry” means only rotations in the dihedral symmetry group of the square \(G_{77}\), the accepted half-turn and quarter-turn results leave centered half-turn symmetry as the only nontrivial rotational option at cardinality 154;
- if rotations about arbitrary plane centers are included, the supplied argument does not fully establish the exhaustive classification as written.

### Distinction between centered half-turn symmetry and rct4

The rct4 class is not identical to the class of centered half-turn-invariant 154-point configurations. It imposes additional restrictions:

- the anti-diagonal is empty;
- off the two diagonals, selected cells occur in complete quarter-turn orbits;
- exactly one half-turn pair on the main diagonal is selected.

Thus an rct4 infeasibility result would not eliminate all centered half-turn configurations. This scope boundary remains active regardless of the eventual satisfiability status of the rct4 model.

This qualification is not an active dispute between incompatible judgments. It records the accepted limits of the single supplied judgment.

---

## Node: no-three-in-line/d77-rct4-154-model

- **Type:** Exact restricted computational model and open satisfiability question
- **Status:** Model equivalence accepted; satisfiability unresolved
- **Parent:** `root`
- **Primary judgment provenance:** `sha256:d24a70c16a08ff85401e969cfe12d8f8253056bb8d75e469ec226eba7a3b44c5`
- **Evidence transaction:** `c98dd877ad81611a9a469b1bd790cd909b56b1ce`
- **Related nodes:**
  - `no-three-in-line/d77-154-centered-half-turn-condition`
  - `no-three-in-line/d77-rotational-symmetry-at-153-154`
  - `no-three-in-line/d77-exact-value`

Judgment `sha256:d24a70c16a08ff85401e969cfe12d8f8253056bb8d75e469ec226eba7a3b44c5` supports with high confidence, based on static inspection of the supplied argument and code, that the \(n=77\) model exactly encodes the stated 154-point rct4 subclass.

### Encoded subclass

Let

\[
\rho(i,j)=(j,76-i)
\]

be the quarter-turn about \((38,38)\). The encoded configurations satisfy:

1. the anti-diagonal is empty;
2. away from the main and anti-diagonals, occupied cells form complete \(\rho\)-orbits;
3. exactly one half-turn pair on the main diagonal is occupied.

These restrictions define a strict subclass of centered half-turn-invariant configurations.

### Orbit variables and cardinality

After removing the two diagonals, the grid has

\[
77^2-(2\cdot77-1)=5776
\]

remaining cells. The model groups these into 1,444 quarter-turn orbits of four cells each.

The 76 noncentral main-diagonal cells form 38 half-turn pairs. The model therefore contains:

- 1,444 off-diagonal orbit variables;
- 38 main-diagonal pair variables.

It imposes the exact cardinality conditions

\[
\sum y_{\mathrm{off}}=38,
\qquad
\sum y_{\mathrm{diag}}=1.
\]

Every feasible assignment consequently represents

\[
4\cdot38+2=154
\]

selected cells.

### Line constraints and model equivalence

The accepted model enumeration uses primitive lattice directions with canonical sign and coordinate increments bounded by 38. It starts each maximal grid line at a point whose predecessor in the chosen direction lies outside the grid.

For each enumerated line, a variable’s coefficient is the number of cells from its orbit lying on that line. The weighted inequality

\[
\sum_v c_vy_v\le2
\]

therefore limits that line to at most two selected cells.

The judgment accepts that:

- every feasible assignment yields a 154-point no-three-in-line set in the stated rct4 class;
- every 154-point no-three-in-line set satisfying the rct4 conditions induces a feasible assignment.

The deterministic \(n=77\) model statistics are:

- 1,444 off-orbit variables;
- 38 diagonal-pair variables;
- 388,148 deduplicated weighted line constraints.

The exact line-constraint count is a reproducible computational census rather than a separately hand-derived theorem.

### CNF translation

The judgment accepts the CNF translation of each weighted at-most-two constraint:

- a variable of coefficient at least three is forced false;
- two coefficient-two variables cannot both be true;
- a coefficient-two variable cannot coexist with a coefficient-one variable;
- every triple of coefficient-one variables is forbidden.

Together with the exact-cardinality encoding, these clauses are accepted as equivalent to the model’s weighted constraints.

### Calibration scope

Five committed certificates at

\[
n=41,47,57,65,69
\]

are checked using exact operations. The checks include:

- coordinate decoding;
- distinctness and grid membership;
- exact determinant tests over all point triples;
- the empty anti-diagonal condition;
- the required orbit structure;
- satisfaction of the generated model constraints.

The judgment treats these certificates as exact regression checks for the five listed sizes only. They do not establish a broader historical range claim, external provenance, or discovery priority. File hashes establish file identity but not external provenance.

### Current satisfiability status

The \(n=77\) rct4 instance remains unresolved.

The reported CP-SAT `UNKNOWN` outcomes and SAT timeouts establish neither satisfiability nor unsatisfiability. No committed solver logs, proof traces, or exact CaDiCaL invocation were supplied. Comparable failures on known satisfiable calibration sizes show that these timeouts have no negative mathematical force.

Accordingly, the evidence establishes none of the following:

- that the \(n=77\) rct4 instance is satisfiable;
- that it is unsatisfiable;
- that no centered half-turn 154-point configuration exists;
- that \(D(77)<154\).

A feasible assignment would provide a 154-point certificate and hence establish \(D(77)=154\). A proof of rct4 infeasibility would exclude only the rct4 subclass.

### Attribution carried forward

The judgment attributes the new symmetry observations, the \(n=77\) model implementation, its validation machinery, and the bounded search report to Robert Raynor and the disclosed AI research agent. It also records that the contribution attributes the underlying rct4 class and symmetry-reduction method to “Thomas”; the supplied judgment text ends at that name. No broader provenance or priority determination is made here.

---

## Node: no-three-in-line/d77-exact-value

- **Type:** Open mathematical question
- **Status:** Unresolved
- **Parent:** `root`
- **Primary judgment provenance:**
  - `sha256:a470e4a9c0903097d9c860badaa8976cf32ed5336c154f11d8fad980d401f74e`
  - `sha256:71fbde8d269728a92be52f6401e857230043ee6938c45f810c32308d88fb9927`
  - `sha256:d24a70c16a08ff85401e969cfe12d8f8253056bb8d75e469ec226eba7a3b44c5`
- **Evidence transactions:**
  - `dfc0cc40d41105292a119840dcdbe6f22860cf43`
  - `c5e8096d942d57228bb4fed00f7617fb6b43af9f`
  - `c98dd877ad81611a9a469b1bd790cd909b56b1ce`
- **Related bound:** `no-three-in-line/d77-certified-interval`
- **Related structural nodes:**
  - `no-three-in-line/d77-near-capacity-occupancy`
  - `no-three-in-line/d77-distance-from-embedded-g76-152-record`
  - `no-three-in-line/rotational-cardinality-obstructions`
  - `no-three-in-line/d77-154-centered-half-turn-condition`
  - `no-three-in-line/d77-rotational-symmetry-at-153-154`
  - `no-three-in-line/d77-rct4-154-model`

The exact value of \(D(77)\) remains unresolved under the supplied immutable judgments. The strongest globally certified conclusion remains

\[
152\le D(77)\le154,
\]

so the currently supported possibilities are

\[
D(77)\in\{152,153,154\}.
\]

### Existing local exclusion around the known embeddings

For each of the eight specified embeddings \(E\) of the verified 152-point configuration, every no-three-in-line set \(S\subseteq G_{77}\) with \(|S|\ge153\) must satisfy

\[
|E\setminus S|\ge3,\qquad
|S\setminus E|\ge4,\qquad
|E\triangle S|\ge7.
\]

These computations do not constrain all configurations at or beyond that distance and do not address every other 152-point configuration.

### Current symmetry restrictions

Judgment `sha256:d24a70c16a08ff85401e969cfe12d8f8253056bb8d75e469ec226eba7a3b44c5` adds the following restrictions without determining the exact value:

- a 153-point no-three-in-line set cannot have half-turn symmetry;
- neither a 153-point nor a 154-point no-three-in-line set can have quarter-turn symmetry;
- if a 154-point set has half-turn symmetry, that symmetry must be centered at \((38,38)\), with the center unoccupied;
- the exhaustive classification of rotations about arbitrary centers is qualified because the written contribution omits an explicit finite-order lattice-rotation classification;
- rct4 is only a strict subclass of centered half-turn configurations.

### Restricted computational result

The \(n=77\) rct4 model is accepted as an exact encoding of its stated 154-point subclass, but its satisfiability remains unresolved. The reported timeouts and `UNKNOWN` outcomes supply no negative mathematical conclusion.

Even a future proof that the rct4 instance is infeasible would rule out only that subclass. It would not by itself rule out:

- other centered half-turn 154-point configurations;
- reflection-symmetric 154-point configurations;
- asymmetric 154-point configurations.

### Missing decisive evidence

The supplied evidence contains neither:

- a 153-point coordinate certificate;
- a 154-point coordinate certificate;
- a global impossibility proof for 153 points;
- a global impossibility proof for 154 points;
- a global exhaustive search;
- a completed symmetry-class impossibility theorem that narrows the certified interval;
- nor a satisfiability or unsatisfiability certificate for the rct4 instance.

The unresolved exact value is an open mathematical question caused by the absence of decisive evidence. It is not an active dispute between incompatible judgments.

---

## Change: root

The root node should be revised to incorporate four new durable concepts recognized by judgment `sha256:d24a70c16a08ff85401e969cfe12d8f8253056bb8d75e469ec226eba7a3b44c5`:

1. accepted half-turn and quarter-turn cardinality obstructions;
2. the accepted centered half-turn condition for a hypothetical 154-point set;
3. the qualified scope of the rotational-symmetry classification;
4. the exact rct4 model together with its unresolved satisfiability.

The earlier certified configuration, interval, occupancy constraints, embedding rigidity, and distance results remain unchanged. The node inventory is expanded rather than replacing any of those concepts.

No conflict record accompanies the new judgment, and its qualifications are internally explicit. They therefore do not create an adjudicative dispute.

---

## Change: no-three-in-line/rotational-cardinality-obstructions

This is a proposed new node because the accepted half-turn and quarter-turn cardinality restrictions are general structural results that remain meaningful independently of the transaction or search chronology.

They are grouped in one node because both concern orbit-size and fixed-center restrictions imposed by rotational invariance on no-three-in-line sets. The node preserves the judgment’s accepted stance and does not extend the results to unclassified rotation orders.

Primary support is judgment `sha256:d24a70c16a08ff85401e969cfe12d8f8253056bb8d75e469ec226eba7a3b44c5`, based on transaction `c98dd877ad81611a9a469b1bd790cd909b56b1ce`.

---

## Change: no-three-in-line/d77-154-centered-half-turn-condition

This is a proposed new node because the location and occupancy condition for the center of a half-turn-invariant 154-point subset of \(G_{77}\) is a distinct durable structural constraint.

It is not merged with the general rotational-cardinality node because it depends specifically on full row and column occupancy at cardinality 154 in the \(77\times77\) grid. It is also broader than rct4, applying to every centered half-turn configuration of that cardinality.

Primary support is judgment `sha256:d24a70c16a08ff85401e969cfe12d8f8253056bb8d75e469ec226eba7a3b44c5`.

---

## Change: no-three-in-line/d77-rotational-symmetry-at-153-154

This is a proposed new qualified-classification node. Its purpose is to preserve the precise boundary between:

- the accepted order-two and order-four conclusions;
- the missing arbitrary-center lattice-rotation classification;
- and the strict-subclass status of rct4.

Keeping this scope qualification in a durable node prevents the exact rct4 model from being silently generalized to all rotationally symmetric or all centered half-turn configurations.

The qualification comes directly from judgment `sha256:d24a70c16a08ff85401e969cfe12d8f8253056bb8d75e469ec226eba7a3b44c5`. It is not treated as a dispute because there are no opposed primary judgments or conflict records.

---

## Change: no-three-in-line/d77-rct4-154-model

This is a proposed new node because an exact encoding of a mathematically defined symmetry subclass is a durable method and restricted research question, independent of the transaction that introduced it.

The model equivalence, deterministic statistics, CNF translation, calibration scope, and unresolved satisfiability are kept together because they jointly define the current trustworthy scope of the computational artifact.

The bounded searches are not separate nodes. They are provenance for the unresolved satisfiability status and carry no negative mathematical force. Likewise, the five calibration certificates are implementation checks within this method node rather than separate event or certificate nodes.

Primary support is judgment `sha256:d24a70c16a08ff85401e969cfe12d8f8253056bb8d75e469ec226eba7a3b44c5`, concerning transaction `c98dd877ad81611a9a469b1bd790cd909b56b1ce`.

---

## Change: no-three-in-line/d77-exact-value

The exact-value node should be revised to include the newly accepted symmetry restrictions and the exact restricted rct4 model while preserving its unresolved status.

Judgment `sha256:d24a70c16a08ff85401e969cfe12d8f8253056bb8d75e469ec226eba7a3b44c5` explicitly concludes that the contribution supplies neither a 153- or 154-point certificate nor a global upper-bound improvement. It therefore does not change the certified interval

\[
152\le D(77)\le154.
\]

The revision also records that rct4 infeasibility, if later certified, would exclude only a strict subclass. This prevents the restricted model or its timeouts from being misrepresented as a global result.
