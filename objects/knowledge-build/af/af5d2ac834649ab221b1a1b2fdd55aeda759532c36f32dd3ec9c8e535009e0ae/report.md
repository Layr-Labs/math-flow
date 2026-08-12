# Knowledge-Formation Report

## Formation summary

This build updates four existing nodes within `program/rotational-symmetry`. It creates no new program, mathematical node, or dispute node.

The accepted arbitrary-center rotation theorem closes the qualification previously recorded in `d77/rotational-classification-scope`. The resulting classification also strengthens the established consequences for hypothetical \(153\)- and \(154\)-point configurations.

No judgment improves either global bound or determines the exact value. Accordingly, the root-level exact-value question and certified interval remain unchanged:

\[
152\le D(77)\le154.
\]

There are no conflict records or incompatible reconciliation outcomes. The new judgment characterizes its result as completing a previously missing justification, not contradicting an earlier mathematical conclusion.

## Node: program/rotational-symmetry

- **Type:** program
- **Parent:** `root`
- **Status:** active
- **Title:** Rotational-symmetry restrictions and rct4 modeling

This program studies rotational restrictions on hypothetical \(153\)- and \(154\)-point no-three-in-line subsets of \(G_{77}\), together with exact search models for a narrower rotationally structured subclass.

Its complete current state is:

- A nonidentity Euclidean rotation preserving a finite noncollinear subset of \(\mathbb Z^2\), even when its center is arbitrary, must be a half-turn or a quarter-turn.
- An odd-cardinality no-three-in-line set invariant under a half-turn has at most one point.
- A quarter-turn-invariant no-three-in-line set has cardinality divisible by four or is a singleton.
- Consequently, any \(153\)-point no-three-in-line subset of \(G_{77}\), if one exists, has no nonidentity rotational symmetry about any center.
- If a \(154\)-point no-three-in-line subset of \(G_{77}\) has nontrivial rotational symmetry, its nontrivial rotation must be the half-turn about \((38,38)\), and \((38,38)\) must be unselected.
- These restrictions do not exclude reflection-symmetric or asymmetric configurations. They do not establish the existence or nonexistence of a \(153\)- or \(154\)-point set.
- Centered half-turn invariance is strictly broader than the `rct4` conditions. The `rct4` class additionally imposes requirements including an empty anti-diagonal, complete quarter-turn orbits away from the diagonals, and one selected main-diagonal half-turn pair.
- The supplied \(n=77\) `rct4` model exactly represents its stated restricted subclass.
- Satisfiability of that model remains unresolved. Reported search timeouts have no negative mathematical force.
- No result in this program changes the certified interval
  \[
  152\le D(77)\le154.
  \]

### Scope

The accepted arbitrary-center classification concerns exact Euclidean rotations preserving finite noncollinear lattice sets. It does not classify reflections, affine automorphisms, approximate symmetries, or collinear finite sets.

### Credit

The earlier judgment attributes the symmetry observations, implementation, validation machinery, and bounded search report in transaction `c98dd877ad81611a9a469b1bd790cd909b56b1ce` to Robert Raynor and a disclosed AI research agent. It attributes the underlying `rct4` class and symmetry-reduction method to Thomas; the supplied excerpt ends during that attribution. The problem statement separately identifies Thomas Prellberg’s constraint-programming work as a frontier source.

Judgment `sha256:21f3e6bb405eaaf804b58020a1695c213023b0dd3f1d25a08248fb5a48750eca` credits transaction `29ccbd396781fd36d436ed2e6d0952a4730361b9` with supplying the decisive arbitrary-center finite-rotation argument. It records that the half-turn and quarter-turn orbit arguments and the row-and-column occupancy observation were already present in earlier evidence. It does not adjudicate broader historical priority for the finite-rotation theorem.

### Provenance

- New primary judgment completing the arbitrary-center classification: `sha256:21f3e6bb405eaaf804b58020a1695c213023b0dd3f1d25a08248fb5a48750eca`
- Subject and supporting transaction for that judgment: `29ccbd396781fd36d436ed2e6d0952a4730361b9`
- Earlier primary judgment supporting the orbit restrictions, `rct4` scope, exact model, and unresolved search status: `sha256:d24a70c16a08ff85401e969cfe12d8f8253056bb8d75e469ec226eba7a3b44c5`
- Earlier subject transaction: `c98dd877ad81611a9a469b1bd790cd909b56b1ce`
- Supporting baseline transactions:
  - `dfc0cc40d41105292a119840dcdbe6f22860cf43`
  - `c5e8096d942d57228bb4fed00f7617fb6b43af9f`

## Change: program/rotational-symmetry

Judgment `sha256:21f3e6bb405eaaf804b58020a1695c213023b0dd3f1d25a08248fb5a48750eca` accepts the previously missing arbitrary-center rotation theorem. The program summary is therefore revised from a qualified classification to a complete classification within the stated Euclidean-rotation scope, while preserving the unresolved `rct4` search and unchanged global bounds.

## Node: d77/rotational-classification-scope

- **Type:** claim
- **Parent:** `program/rotational-symmetry`
- **Status:** active
- **Title:** Arbitrary-center rotational classification and its scope

The supplied judgments now establish the following complete rotational classification within their stated scope:

> If a finite noncollinear subset of \(\mathbb Z^2\) is preserved by a nonidentity Euclidean rotation about an arbitrary center, that rotation is a half-turn or a quarter-turn.

Judgment `sha256:21f3e6bb405eaaf804b58020a1695c213023b0dd3f1d25a08248fb5a48750eca` accepts this theorem as proved with high confidence and records that it closes the missing arbitrary-center step identified by the earlier judgment.

Applied to no-three-in-line subsets of \(G_{77}\), the classification has the following accepted consequences:

- a hypothetical \(153\)-point set cannot have any nonidentity rotational symmetry;
- a rotationally symmetric \(154\)-point set must be invariant under the half-turn about \((38,38)\), with the center unselected.

These conclusions classify nontrivial rotational symmetry only. They do not address reflections or other nonrotational symmetries, and they do not establish existence or nonexistence at either cardinality.

The noncollinearity assumption is essential. The classification does not cover collinear finite sets, reflections, affine automorphisms, or approximate symmetries.

The classification also does not identify all centered half-turn configurations with `rct4`. The `rct4` conditions define a strict subclass by adding an empty anti-diagonal, complete quarter-turn orbits away from the diagonals, and one selected main-diagonal half-turn pair.

There is no active dispute. The earlier judgment identified incomplete justification rather than an opposed conclusion, and the later judgment accepts a proof that supplies the omitted lemma.

### Provenance

- Earlier qualified finding: `sha256:d24a70c16a08ff85401e969cfe12d8f8253056bb8d75e469ec226eba7a3b44c5`
- Earlier subject transaction: `c98dd877ad81611a9a469b1bd790cd909b56b1ce`
- Judgment accepting the arbitrary-center theorem and closing the qualification: `sha256:21f3e6bb405eaaf804b58020a1695c213023b0dd3f1d25a08248fb5a48750eca`
- Subject and evidence transaction for the completed theorem: `29ccbd396781fd36d436ed2e6d0952a4730361b9`

## Change: d77/rotational-classification-scope

The earlier judgment left arbitrary-center rotational classification qualified because rotations of other finite orders had not been excluded. The new primary judgment accepts a proof excluding those possibilities, so this node moves from qualified to active while retaining the established limits concerning reflections, noncollinear scope, and the narrower `rct4` class.

## Node: rotational-symmetry/cardinality-obstructions

- **Type:** lemma
- **Parent:** `program/rotational-symmetry`
- **Status:** active
- **Title:** Half-turn and quarter-turn cardinality obstructions

The supplied judgments accept the following rotational restrictions.

### General rotation classification

If a finite noncollinear subset of \(\mathbb Z^2\) is preserved by a nonidentity Euclidean rotation about any center, the rotation is a half-turn or a quarter-turn. No other nontrivial rotational order can occur under these hypotheses.

### Half-turn obstruction

If a finite no-three-in-line set is invariant under a half-turn and has odd cardinality, it has at most one point. Consequently, a \(153\)-point no-three-in-line set cannot be half-turn invariant.

### Quarter-turn obstruction

A quarter-turn-invariant no-three-in-line set has cardinality divisible by four or is a singleton. Consequently, neither \(153\) nor \(154\) is possible under quarter-turn invariance.

### Consequence for cardinality \(153\)

Because the general classification leaves only half-turns and quarter-turns, and both are excluded at cardinality \(153\), every \(153\)-point no-three-in-line subset of \(G_{77}\), if one exists, has no nonidentity rotational symmetry about any center.

This does not imply that a \(153\)-point configuration is nonexistent. Reflection-symmetric and asymmetric possibilities remain open.

### Consequence for cardinality \(154\)

Quarter-turn symmetry is excluded at cardinality \(154\). Therefore, if a \(154\)-point no-three-in-line subset of \(G_{77}\) has any nontrivial rotational symmetry, that symmetry must be a half-turn. The grid-specific determination of its center is recorded in `d77/154-half-turn-center`.

These conclusions concern rotations only. They do not classify reflections, affine symmetries, approximate symmetries, or finite collinear sets.

### Provenance

- Earlier judgment accepting the half-turn and quarter-turn orbit restrictions: `sha256:d24a70c16a08ff85401e969cfe12d8f8253056bb8d75e469ec226eba7a3b44c5`
- Earlier subject transaction: `c98dd877ad81611a9a469b1bd790cd909b56b1ce`
- Judgment accepting the arbitrary-center classification and the resulting \(153\)-point conclusion: `sha256:21f3e6bb405eaaf804b58020a1695c213023b0dd3f1d25a08248fb5a48750eca`
- Subject and evidence transaction for the completed classification: `29ccbd396781fd36d436ed2e6d0952a4730361b9`

## Change: rotational-symmetry/cardinality-obstructions

The accepted arbitrary-center theorem removes the former limitation to separately analyzed half-turns and quarter-turns. This permits the existing orbit obstructions to support the judgment’s complete exclusion of all nonidentity rotational symmetry at cardinality \(153\), without making any global nonexistence claim.

## Node: d77/154-half-turn-center

- **Type:** lemma
- **Parent:** `program/rotational-symmetry`
- **Status:** active
- **Title:** Rotational symmetry of a 154-point set

If a \(154\)-point no-three-in-line subset \(S\subseteq G_{77}\) has any nontrivial rotational symmetry, the supplied judgments establish all of the following:

1. The symmetry cannot be a quarter-turn.
2. The arbitrary-center rotation classification excludes every nontrivial rotation other than a half-turn or quarter-turn.
3. Therefore the nontrivial rotational symmetry must be a half-turn.
4. Every one of the \(77\) rows and every one of the \(77\) columns contains exactly two selected points.
5. The coordinatewise bounding box of \(S\) is
   \[
   [0,76]\times[0,76].
   \]
6. The half-turn is centered at
   \[
   (38,38).
   \]
7. The center is unselected:
   \[
   (38,38)\notin S.
   \]

Thus any rotationally symmetric \(154\)-point configuration must belong to the centered half-turn class.

This is a conditional symmetry classification. It does not assert that a \(154\)-point no-three-in-line subset exists. It does not exclude asymmetric or reflection-symmetric \(154\)-point sets, and it does not identify the full centered half-turn class with the stricter `rct4` subclass.

The associated judgment reports high confidence in this rotational conclusion and states that it uses no computational or external factual assumptions.

### Provenance

- Earlier judgment supporting the center conclusion conditional on half-turn invariance: `sha256:d24a70c16a08ff85401e969cfe12d8f8253056bb8d75e469ec226eba7a3b44c5`
- Earlier subject transaction: `c98dd877ad81611a9a469b1bd790cd909b56b1ce`
- Judgment supporting full row-and-column occupancy: `sha256:a470e4a9c0903097d9c860badaa8976cf32ed5336c154f11d8fad980d401f74e`
- Judgment accepting the complete arbitrary-center rotational classification for cardinality \(154\): `sha256:21f3e6bb405eaaf804b58020a1695c213023b0dd3f1d25a08248fb5a48750eca`
- Subject and evidence transaction for the completed classification: `29ccbd396781fd36d436ed2e6d0952a4730361b9`

## Change: d77/154-half-turn-center

This node previously assumed half-turn invariance before determining the center. The new judgment accepts the missing arbitrary-center classification and excludes quarter-turn symmetry at cardinality \(154\), allowing the node to classify every rotationally symmetric \(154\)-point set while preserving its conditional, nonexistence-neutral scope.
