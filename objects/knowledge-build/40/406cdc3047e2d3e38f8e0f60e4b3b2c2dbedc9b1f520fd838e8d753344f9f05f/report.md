# Knowledge-Formation Report

## Formation scope

This report materializes the conclusions accepted by the supplied immutable judgments without independently reassessing their mathematics.

The organizational actions are:

- revise `root` to include the accepted arbitrary-center rotation classification and its consequences;
- create `finite-lattice-sets/nontrivial-rotation-classification` for the distinct, durable lattice-rotation lemma;
- revise `no-three-in-line/d77-rotational-symmetry-at-153-154` because the formerly qualified arbitrary-center classification is now accepted as complete;
- revise `no-three-in-line/d77-exact-value` to record the stronger symmetry restrictions while retaining the unresolved interval.

The following remain substantively unchanged and do not require separate node sections:

- the verified 152-point certificate;
- the certified interval \(152\le D(77)\le154\);
- the near-capacity row and column occupancy constraints;
- the saturation and local-rigidity results around the eight specified embeddings;
- the general half-turn and quarter-turn cardinality obstructions;
- the centered-half-turn condition already established for a hypothetical 154-point set;
- the scope and unresolved satisfiability of the restricted `rct4` model.

No conflict records or reconciliation outcomes were supplied. Consequently, no active dispute node is required.

---

## Node: root

- **Type:** Root research state
- **Status:** Active
- **Parent:** None
- **Primary judgment provenance:**
  - `sha256:a470e4a9c0903097d9c860badaa8976cf32ed5336c154f11d8fad980d401f74e`
  - `sha256:71fbde8d269728a92be52f6401e857230043ee6938c45f810c32308d88fb9927`
  - `sha256:d24a70c16a08ff85401e969cfe12d8f8253056bb8d75e469ec226eba7a3b44c5`
  - `sha256:21f3e6bb405eaaf804b58020a1695c213023b0dd3f1d25a08248fb5a48750eca`
- **Evidence transactions:**
  - `dfc0cc40d41105292a119840dcdbe6f22860cf43`
  - `c5e8096d942d57228bb4fed00f7617fb6b43af9f`
  - `c98dd877ad81611a9a469b1bd790cd909b56b1ce`
  - `29ccbd396781fd36d436ed2e6d0952a4730361b9`

For

\[
G_n=\{0,1,\ldots,n-1\}^2,
\]

let \(D(n)\) be the largest cardinality of a subset of \(G_n\) containing no three distinct collinear points.

According to the supplied immutable judgments, the complete current research state at grid size \(77\) is as follows.

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

3. The globally certified interval is

   \[
   152\le D(77)\le154.
   \]

   The lower bound follows from embedding the verified 152-point configuration. The upper bound follows because each of the 77 horizontal rows contains at most two selected points.

4. The necessary row and column occupancy constraints for hypothetical 153- and 154-point sets remain active.

### Local rigidity around the specified embeddings

5. Each of the eight specified embeddings is saturated in \(G_{77}\): every one of its 5,777 outside cells is blocked by at least two pairs of embedded points. Each embedding is therefore inclusion-maximal, but this does not establish maximum cardinality.

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

   These are local restrictions around the eight embeddings, not a global exclusion of larger configurations.

### Rotations of finite lattice sets

9. Judgment `sha256:21f3e6bb405eaaf804b58020a1695c213023b0dd3f1d25a08248fb5a48750eca` accepts as proved that if a finite noncollinear subset of \(\mathbb Z^2\) is preserved by a nonidentity Euclidean rotation about an arbitrary center, then the rotation is a half-turn or a quarter-turn.

10. The accepted classification is limited to exact Euclidean rotations. Noncollinearity is essential. It does not classify reflections, affine transformations, approximate symmetries, or collinear finite sets.

### Rotational restrictions at cardinalities 153 and 154

11. An odd-cardinality no-three-in-line set invariant under a half-turn has at most one point. In particular, a 153-point no-three-in-line set cannot have half-turn symmetry.

12. A quarter-turn-invariant no-three-in-line set has cardinality divisible by four or equal to one. Thus neither a 153-point nor a 154-point no-three-in-line set can be quarter-turn invariant.

13. Combining these orbit-cardinality results with the accepted arbitrary-center rotation classification, any 153-point no-three-in-line subset of \(G_{77}\), if one exists, has no nonidentity rotational symmetry about any center. This does not exclude reflection-symmetric or asymmetric 153-point sets.

14. If a 154-point no-three-in-line subset of \(G_{77}\) has any nontrivial rotational symmetry, judgment `sha256:21f3e6bb405eaaf804b58020a1695c213023b0dd3f1d25a08248fb5a48750eca` accepts that the symmetry must be the half-turn about

    \[
    (38,38),
    \]

    and that \((38,38)\) is unselected.

    The center is forced because a 154-point set attains equality in both the row and column capacity bounds, giving exactly two selected points in every row and every column and bounding box \([0,76]^2\).

15. The rotational classification does not classify reflections and does not imply that a 153- or 154-point configuration exists.

### Restricted `rct4` model

16. The `rct4` subclass is strictly narrower than the class of all centered half-turn-invariant configurations. It additionally requires:

    - an empty anti-diagonal;
    - complete quarter-turn orbits away from the diagonals;
    - exactly one selected half-turn pair on the main diagonal.

17. Static inspection in judgment `sha256:d24a70c16a08ff85401e969cfe12d8f8253056bb8d75e469ec226eba7a3b44c5` supports, with high confidence, that the supplied \(n=77\) model is sound and complete for the stated 154-point `rct4` subclass.

18. The model has:

    - 1,444 off-diagonal quarter-turn-orbit variables;
    - 38 main-diagonal half-turn-pair variables;
    - exact cardinality conditions selecting 38 off-diagonal orbits and one diagonal pair;
    - 388,148 deduplicated weighted line constraints generated with exact integer arithmetic.

    Every feasible assignment represents

    \[
    4\cdot38+2=154
    \]

    selected points satisfying the `rct4` pattern. Within that subclass, feasibility is accepted as equivalent to the no-three-in-line property.

19. Five committed calibration certificates at

    \[
    n=41,47,57,65,69
    \]

    provide exact implementation regression checks at those sizes. The judgments do not treat them as proof of a broader historical range claim, external provenance, or discovery priority.

20. The satisfiability of the \(n=77\) `rct4` instance remains unresolved. Reported `UNKNOWN` results and timeouts establish neither satisfiability nor unsatisfiability. They therefore have no negative mathematical force.

### Global unresolved question

21. The exact value of \(D(77)\) remains unresolved. The supported possibilities are

    \[
    D(77)\in\{152,153,154\}.
    \]

22. The supplied evidence contains no 153- or 154-point certificate and no global impossibility proof for either cardinality.

23. The accepted rotational restrictions constrain only possible symmetry classes:

    - a hypothetical 153-point set has no nontrivial rotational symmetry;
    - a rotationally symmetric 154-point set must have the centered half-turn about \((38,38)\);
    - asymmetric and reflection-symmetric cases remain possible in principle;
    - general centered-half-turn configurations are not exhausted by the `rct4` model.

### Current node inventory

- `finite-lattice-sets/nontrivial-rotation-classification`
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

## Change: root

The root research state is revised to incorporate judgment `sha256:21f3e6bb405eaaf804b58020a1695c213023b0dd3f1d25a08248fb5a48750eca`, concerning transaction `29ccbd396781fd36d436ed2e6d0952a4730361b9`.

That judgment accepts an arbitrary-center finite-lattice rotation classification and thereby closes the scope qualification formerly attached to the rotational conclusions for cardinalities 153 and 154. The root inventory consequently adds the durable lemma node `finite-lattice-sets/nontrivial-rotation-classification`.

The certified interval, local-rigidity conclusions, and restricted `rct4` status are retained without substantive alteration. In particular, the stronger symmetry classification does not change the unresolved status of \(D(77)\).

No conflict resolution was needed because the judgment characterizes the new proof as completing an earlier gap rather than contradicting an earlier accepted mathematical conclusion.

---

## Node: finite-lattice-sets/nontrivial-rotation-classification

- **Type:** Structural lemma
- **Status:** Active; accepted as proved
- **Parent:** `root`
- **Primary judgment provenance:** `sha256:21f3e6bb405eaaf804b58020a1695c213023b0dd3f1d25a08248fb5a48750eca`
- **Evidence transaction:** `29ccbd396781fd36d436ed2e6d0952a4730361b9`
- **Related nodes:**
  - `no-three-in-line/rotational-cardinality-obstructions`
  - `no-three-in-line/d77-rotational-symmetry-at-153-154`
  - `no-three-in-line/d77-exact-value`

Judgment `sha256:21f3e6bb405eaaf804b58020a1695c213023b0dd3f1d25a08248fb5a48750eca` accepts the following statement as proved:

> If \(S\subset\mathbb Z^2\) is finite and noncollinear, and a nonidentity Euclidean rotation \(T\) about an arbitrary center satisfies \(T(S)=S\), then the rotation angle is \(180^\circ\) or \(\pm90^\circ\).

Equivalently, the only possible nonidentity rotational symmetry types of a finite noncollinear lattice set are a half-turn and a quarter-turn.

### Accepted basis

The source judgment identifies three decisive components in the supplied proof:

1. Images of three noncollinear lattice points show that the rotation matrix has rational entries, even when the center is arbitrary and the rotation does not preserve the whole lattice.
2. Because the rotation permutes a finite set, an appropriate positive power fixes three noncollinear points and is therefore the identity isometry; hence the rotation has finite order.
3. The matrix trace is both rational and an algebraic integer. The resulting possible trace values, together with rationality of both matrix parameters, leave only the identity, half-turn, and quarter-turn cases. Excluding the identity gives the stated classification.

These points record the grounds accepted by the immutable judgment; they are not an independent proof assessment by this report.

### Scope

The judgment expressly limits the result as follows:

- noncollinearity is essential;
- the center of rotation may be arbitrary;
- the theorem concerns exact Euclidean rotations;
- it does not classify reflections;
- it does not classify affine automorphisms or approximate symmetries;
- it does not extend to arbitrary collinear finite lattice sets.

The theorem is a general lattice-symmetry lemma independent of the particular grid size \(77\).

---

## Change: finite-lattice-sets/nontrivial-rotation-classification

This is a proposed new node because the accepted theorem is a distinct, durable mathematical concept that remains meaningful without the transaction name or the chronology of the \(D(77)\) investigation. It applies to every finite noncollinear subset of \(\mathbb Z^2\), not only to no-three-in-line configurations in \(G_{77}\).

Judgment `sha256:21f3e6bb405eaaf804b58020a1695c213023b0dd3f1d25a08248fb5a48750eca` attributes the decisive arbitrary-center finite-rotation argument to transaction `29ccbd396781fd36d436ed2e6d0952a4730361b9`. It also states that the half-turn and quarter-turn orbit-counting arguments used in the \(D(77)\) application, along with the row and column occupancy observation, were already present in earlier supplied evidence.

The judgment does not adjudicate broader historical priority for the finite-rotation theorem. This report carries that limitation forward and makes no independent priority claim.

---

## Node: no-three-in-line/d77-rotational-symmetry-at-153-154

- **Type:** Structural classification
- **Status:** Active; accepted as proved within the stated rotational scope
- **Parent:** `root`
- **Primary judgment provenance:**
  - `sha256:d24a70c16a08ff85401e969cfe12d8f8253056bb8d75e469ec226eba7a3b44c5`
  - `sha256:21f3e6bb405eaaf804b58020a1695c213023b0dd3f1d25a08248fb5a48750eca`
- **Evidence transactions:**
  - `c98dd877ad81611a9a469b1bd790cd909b56b1ce`
  - `29ccbd396781fd36d436ed2e6d0952a4730361b9`
- **Related nodes:**
  - `finite-lattice-sets/nontrivial-rotation-classification`
  - `no-three-in-line/rotational-cardinality-obstructions`
  - `no-three-in-line/d77-154-centered-half-turn-condition`
  - `no-three-in-line/d77-rct4-154-model`
  - `no-three-in-line/d77-exact-value`

The supplied judgments establish a complete classification of nontrivial rotational symmetry for hypothetical 153- and 154-point no-three-in-line subsets of \(G_{77}\), where rotation means an exact Euclidean rotation about any plane center.

### Cardinality 153

If a 153-point no-three-in-line subset of \(G_{77}\) exists, it has no nonidentity rotational symmetry about any center.

The accepted classification of finite noncollinear lattice-set rotations leaves only half-turns and quarter-turns:

- half-turn symmetry is impossible because an invariant set of odd cardinality must contain the fixed center, and any selected noncentral opposite pair together with that center would give three collinear points;
- quarter-turn symmetry is impossible because \(153\equiv1\pmod4\), so the center would have to be selected, while the squared rotation supplies the same opposite-pair collinearity obstruction.

This is a symmetry restriction only. It does not establish that a 153-point set is impossible. Reflection-symmetric and asymmetric possibilities remain open.

### Cardinality 154

If a 154-point no-three-in-line subset \(S\subseteq G_{77}\) has a nontrivial rotational symmetry, that symmetry must be the half-turn about

\[
(38,38),
\]

and

\[
(38,38)\notin S.
\]

The judgments accept the following components:

- quarter-turn symmetry is excluded because 154 is neither divisible by four nor equal to one;
- the arbitrary-center rotation classification leaves only a half-turn;
- equality in the row bound forces exactly two selected points in every row;
- equality in the column bound forces exactly two selected points in every column;
- the bounding box is therefore \([0,76]^2\);
- invariance of that bounding box forces the half-turn center to be \((38,38)\);
- the unique fixed point is unselected because the invariant set has even cardinality.

This does not establish the existence of a 154-point set. Asymmetric and reflection-symmetric 154-point configurations remain possible in principle.

### Rotations versus reflections

The classification concerns rotations only. It supplies no classification or exclusion of reflection symmetry.

### Centered half-turn symmetry versus `rct4`

The class of centered half-turn-invariant 154-point configurations is strictly broader than the `rct4` subclass.

The `rct4` model additionally requires:

- an empty anti-diagonal;
- complete quarter-turn orbits away from the diagonals;
- exactly one selected half-turn pair on the main diagonal.

Therefore, an infeasibility result for the `rct4` instance would not eliminate every centered-half-turn configuration.

---

## Change: no-three-in-line/d77-rotational-symmetry-at-153-154

The selected node formerly preserved a scope qualification because the earlier supplied argument explicitly treated only half-turns and quarter-turns and did not exclude arbitrary-center rotations of other finite orders.

Judgment `sha256:21f3e6bb405eaaf804b58020a1695c213023b0dd3f1d25a08248fb5a48750eca`, based on transaction `29ccbd396781fd36d436ed2e6d0952a4730361b9`, accepts a proof excluding all other nonidentity rotation orders for finite noncollinear lattice sets. The arbitrary-center qualification is therefore removed from the materialized classification.

The resulting current conclusions are:

- no nontrivial rotational symmetry is possible at cardinality 153;
- any nontrivial rotational symmetry at cardinality 154 is the half-turn about \((38,38)\), with that point unselected.

The limits concerning reflections, existence, and the narrower scope of `rct4` remain unchanged.

The judgment treats the new evidence as completing previously insufficient justification, not as contradicting an earlier mathematical conclusion. No dispute node is therefore formed.

---

## Node: no-three-in-line/d77-exact-value

- **Type:** Open mathematical question
- **Status:** Unresolved
- **Parent:** `root`
- **Primary judgment provenance:**
  - `sha256:a470e4a9c0903097d9c860badaa8976cf32ed5336c154f11d8fad980d401f74e`
  - `sha256:71fbde8d269728a92be52f6401e857230043ee6938c45f810c32308d88fb9927`
  - `sha256:d24a70c16a08ff85401e969cfe12d8f8253056bb8d75e469ec226eba7a3b44c5`
  - `sha256:21f3e6bb405eaaf804b58020a1695c213023b0dd3f1d25a08248fb5a48750eca`
- **Evidence transactions:**
  - `dfc0cc40d41105292a119840dcdbe6f22860cf43`
  - `c5e8096d942d57228bb4fed00f7617fb6b43af9f`
  - `c98dd877ad81611a9a469b1bd790cd909b56b1ce`
  - `29ccbd396781fd36d436ed2e6d0952a4730361b9`
- **Related bound:** `no-three-in-line/d77-certified-interval`
- **Related structural nodes:**
  - `no-three-in-line/d77-near-capacity-occupancy`
  - `no-three-in-line/d77-distance-from-embedded-g76-152-record`
  - `finite-lattice-sets/nontrivial-rotation-classification`
  - `no-three-in-line/rotational-cardinality-obstructions`
  - `no-three-in-line/d77-154-centered-half-turn-condition`
  - `no-three-in-line/d77-rotational-symmetry-at-153-154`
  - `no-three-in-line/d77-rct4-154-model`

The exact value of \(D(77)\) remains unresolved under the supplied immutable judgments. The strongest globally certified conclusion is

\[
152\le D(77)\le154,
\]

so the currently supported possibilities are

\[
D(77)\in\{152,153,154\}.
\]

### Certified lower and upper bounds

The lower bound is supported by an exactly verified 152-point no-three-in-line configuration embedded into \(G_{77}\).

The upper bound follows because each of the 77 rows contains at most two selected points.

No supplied judgment improves either side of this interval.

### Local restrictions around the known embeddings

For each of the eight specified embeddings \(E\) of the verified 152-point configuration, every no-three-in-line set \(S\subseteq G_{77}\) with \(|S|\ge153\) must satisfy

\[
|E\setminus S|\ge3,\qquad
|S\setminus E|\ge4,\qquad
|E\triangle S|\ge7.
\]

These computations do not constrain all configurations at or beyond that distance and do not address every possible 152-point configuration.

### Complete current rotational restrictions

The supplied judgments establish:

- any hypothetical 153-point no-three-in-line set has no nonidentity rotational symmetry about any center;
- if a hypothetical 154-point no-three-in-line set has nontrivial rotational symmetry, that symmetry is the half-turn about \((38,38)\);
- the center \((38,38)\) is unselected in such a 154-point set.

These conclusions do not classify or exclude reflections. Accordingly:

- a 153-point set could still be reflection-symmetric or asymmetric;
- a 154-point set could still be asymmetric or reflection-symmetric;
- a rotationally symmetric 154-point set remains possible only within the general centered-half-turn class.

### Restricted computational result

The \(n=77\) `rct4` model is accepted as an exact encoding of its stated 154-point subclass, but its satisfiability remains unresolved. Reported timeouts and `UNKNOWN` outcomes establish neither satisfiability nor unsatisfiability.

The `rct4` class is strictly narrower than centered half-turn symmetry. Even an `rct4` infeasibility certificate would not by itself rule out:

- other centered-half-turn 154-point configurations;
- reflection-symmetric 154-point configurations;
- asymmetric 154-point configurations.

### Missing decisive evidence

The supplied evidence contains none of the following:

- a 153-point coordinate certificate;
- a 154-point coordinate certificate;
- a global impossibility proof for 153 points;
- a global impossibility proof for 154 points;
- a global exhaustive search;
- a satisfiability or unsatisfiability certificate for the \(n=77\) `rct4` instance;
- an exclusion of all general centered-half-turn 154-point configurations;
- an exclusion of reflection-symmetric or asymmetric candidates.

The unresolved exact value reflects the absence of decisive evidence. It is not an active dispute between incompatible judgments.

---

## Change: no-three-in-line/d77-exact-value

Judgment `sha256:21f3e6bb405eaaf804b58020a1695c213023b0dd3f1d25a08248fb5a48750eca` strengthens the accepted symmetry restrictions by closing the formerly missing arbitrary-center rotation classification.

The exact-value node is revised to state without qualification that:

- a hypothetical 153-point set has no nontrivial rotational symmetry;
- a rotationally symmetric 154-point set must use the centered half-turn about \((38,38)\).

The same judgment expressly finds that no bound improvement follows. It supplies neither a larger coordinate certificate nor an impossibility proof, and it leaves asymmetric, reflection-symmetric, and general centered-half-turn cases open. The materialized status therefore remains unresolved with

\[
152\le D(77)\le154.
\]

No separate event-shaped node is created for the new judgment. Its role is retained here as revision provenance for the enduring exact-value question.
