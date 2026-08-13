# Knowledge-formation report

## Node: root

- **Type:** Root
- **Title:** Research state for no-three-in-line at grid size 77
- **Status:** Active
- **Parent:** None

For

\[
G_{77}=\{0,1,\ldots,76\}^2,
\]

the exact maximum cardinality \(D(77)\) of a subset containing no three distinct collinear points remains undecided. The current certified interval is

\[
152\le D(77)\le154.
\]

The primary judgment establishes no improvement to either bound. It accepts structural restrictions on rotationally symmetric configurations but does not establish the existence or global impossibility of configurations with 153 or 154 points.

The current organization has two active root-level branches:

1. **`no-three-in-line/d77-exact-value`** records the central exact-value question and current certified bounds as a genuinely global fact.
2. **`programs/rotational-symmetry`** organizes the accepted classification of rotations preserving finite noncollinear lattice sets and its consequences for hypothetical 153- and 154-point configurations in \(G_{77}\).

There are no active disputes, because no conflict records or incompatible reconciliation outcomes were supplied.

**Authoritative provenance**

- Primary judgment: `sha256:21f3e6bb405eaaf804b58020a1695c213023b0dd3f1d25a08248fb5a48750eca`
- Judged subject transaction: `29ccbd396781fd36d436ed2e6d0952a4730361b9`
- Ledger position: 4

## Change: root

The previously empty root at digest `sha256:182fd4ab3cff13c2410f364403d9962b96944122acda56bea8389df70bd43d03` is updated to represent the certified global bounds and the first durable research program warranted by the supplied primary judgment. No split, merge, restoration, or reparenting is involved because no prior program taxonomy existed.

## Node: no-three-in-line/d77-exact-value

- **Type:** Central question and global bounds
- **Title:** Exact value and certified interval for \(D(77)\)
- **Status:** Active and unresolved
- **Parent:** `root`

The central question is to determine the maximum size \(D(77)\) of a no-three-in-line subset of \(G_{77}\).

According to primary judgment `sha256:21f3e6bb405eaaf804b58020a1695c213023b0dd3f1d25a08248fb5a48750eca`, the exact value remains undecided and the current certified interval remains

\[
152\le D(77)\le154.
\]

The judged contribution does not provide:

- a 153- or 154-point coordinate certificate;
- an impossibility proof for either cardinality; or
- a global exhaustive search.

The accepted rotational-symmetry results therefore do not improve either side of the interval. They only narrow the possible symmetry classes:

- any hypothetical 153-point configuration has no nonidentity rotational symmetry, although reflection-symmetric and asymmetric possibilities remain;
- if a hypothetical 154-point configuration has nontrivial rotational symmetry, it must have the half-turn about \((38,38)\), with that center unselected;
- asymmetric and reflection-symmetric 154-point configurations remain possible in principle;
- general centered-half-turn symmetry is broader than the previously referenced `rct4` class.

No conclusion has been accepted that selects among \(D(77)=152\), \(153\), or \(154\).

**Authoritative provenance**

- Primary judgment: `sha256:21f3e6bb405eaaf804b58020a1695c213023b0dd3f1d25a08248fb5a48750eca`
- Claim key: `no-three-in-line/d77-exact-value`
- Subject and evidence transaction: `29ccbd396781fd36d436ed2e6d0952a4730361b9`

## Change: no-three-in-line/d77-exact-value

This node is created as the durable root-level home for the unresolved exact-value question and best certified bounds. It remains outside any individual program because the bounds and exact value govern the entire problem.

## Node: programs/rotational-symmetry

- **Type:** Research program
- **Title:** Rotational symmetry of finite lattice configurations
- **Status:** Active
- **Parent:** `root`
- **Lineage:** None; this program was not formed by a split or merge.

This program studies which nonidentity Euclidean rotations can preserve finite noncollinear lattice sets and what those classifications imply for large no-three-in-line configurations in \(G_{77}\).

Its current accepted knowledge consists of:

- the classification that a nonidentity Euclidean rotation preserving a finite noncollinear subset of \(\mathbb Z^2\) must be a half-turn or quarter-turn, even when the rotation center is arbitrary;
- the resulting exclusion of all nontrivial rotational symmetry for a hypothetical 153-point no-three-in-line subset of \(G_{77}\);
- the conclusion that any rotationally symmetric hypothetical 154-point subset must be invariant under the half-turn about \((38,38)\), with the center unselected.

The program does not currently classify reflections, affine automorphisms, or approximate symmetries. It does not establish the existence or nonexistence of 153- or 154-point configurations and does not identify centered-half-turn symmetry with the narrower `rct4` class.

The primary judgment assigns high confidence to the accepted rotation results and reports that their proof uses no computational or external factual assumptions.

**Active descendants**

- `finite-lattice-sets/nontrivial-rotation-is-half-or-quarter-turn`
- `no-three-in-line/g77-153-has-no-nontrivial-rotation`
- `no-three-in-line/g77-154-rotation-is-centered-half-turn`

**Authoritative provenance**

- Primary judgment: `sha256:21f3e6bb405eaaf804b58020a1695c213023b0dd3f1d25a08248fb5a48750eca`
- Subject and evidence transaction: `29ccbd396781fd36d436ed2e6d0952a4730361b9`

## Change: programs/rotational-symmetry

This program is created because the accepted general rotation-classification theorem and its \(G_{77}\) consequences form a coherent, separately extensible research agenda. No predecessor program exists, so no reciprocal split or merge lineage is required.

## Node: finite-lattice-sets/nontrivial-rotation-is-half-or-quarter-turn

- **Type:** Theorem
- **Title:** Classification of rotations preserving a finite noncollinear lattice set
- **Status:** Accepted as proved
- **Parent:** `programs/rotational-symmetry`

Primary judgment `sha256:21f3e6bb405eaaf804b58020a1695c213023b0dd3f1d25a08248fb5a48750eca` accepts the following statement as proved:

> If \(S\subset\mathbb Z^2\) is finite and noncollinear, and a nonidentity Euclidean rotation about an arbitrary center satisfies \(T(S)=S\), then the rotation is a half-turn or a quarter-turn.

Thus the only admitted nonidentity rotation angles are \(180^\circ\) and \(\pm90^\circ\).

The judgment reports that the proof:

- obtains a rational rotation matrix from the images of three noncollinear lattice points;
- obtains finite rotation order from the induced permutation of the finite set; and
- uses the rational algebraic-integer trace to exclude all remaining finite rotation orders.

The arbitrary-center scope is material: the theorem does not require the center to be a lattice point or require the rotation to preserve the whole lattice.

The noncollinearity assumption is essential. The accepted theorem concerns Euclidean rotations only and does not classify reflections, affine symmetries, or approximate symmetries.

**Credit and priority carried from the judgment**

The subject transaction supplies the decisive arbitrary-center finite-rotation argument and closes the logical gap identified in earlier rotational reasoning. The supplied evidence is insufficient to adjudicate broader historical priority for the theorem.

**Authoritative provenance**

- Primary judgment: `sha256:21f3e6bb405eaaf804b58020a1695c213023b0dd3f1d25a08248fb5a48750eca`
- Claim key: `finite-lattice-sets/nontrivial-rotation-is-half-or-quarter-turn`
- Subject and evidence transaction: `29ccbd396781fd36d436ed2e6d0952a4730361b9`

## Change: finite-lattice-sets/nontrivial-rotation-is-half-or-quarter-turn

This theorem node is created because the accepted arbitrary-center rotation classification is a durable general mathematical result supporting, but not limited to, the \(G_{77}\) applications.

## Node: no-three-in-line/g77-153-has-no-nontrivial-rotation

- **Type:** Structural theorem
- **Title:** Rotational asymmetry of any 153-point configuration in \(G_{77}\)
- **Status:** Accepted as proved
- **Parent:** `programs/rotational-symmetry`

Primary judgment `sha256:21f3e6bb405eaaf804b58020a1695c213023b0dd3f1d25a08248fb5a48750eca` accepts as proved that every 153-point no-three-in-line subset of \(G_{77}\), if such a subset exists, has no nonidentity rotational symmetry about any center.

The accepted conclusion uses the general finite-lattice rotation classification to reduce the possibilities to half-turns and quarter-turns. The judgment accepts the corresponding orbit and collinearity obstructions for odd cardinality and for cardinality \(153\equiv1\pmod 4\).

This theorem is only a symmetry restriction. It does not prove that a 153-point configuration is impossible. In particular:

- reflection symmetry is not excluded;
- asymmetric configurations are not excluded; and
- no improvement to the certified lower or upper bound follows from this result alone.

**Credit carried from the judgment**

The half-turn and quarter-turn orbit arguments were already present in earlier supplied evidence. The subject transaction repeats them self-containedly and supplies the general arbitrary-center classification needed to exclude every other possible rotational order.

**Authoritative provenance**

- Primary judgment: `sha256:21f3e6bb405eaaf804b58020a1695c213023b0dd3f1d25a08248fb5a48750eca`
- Claim key: `no-three-in-line/g77-153-has-no-nontrivial-rotation`
- Subject and evidence transaction: `29ccbd396781fd36d436ed2e6d0952a4730361b9`

## Change: no-three-in-line/g77-153-has-no-nontrivial-rotation

This node is created to preserve the accepted 153-point rotational restriction as a distinct durable consequence, separate from both the general lattice theorem and the unresolved existence question.

## Node: no-three-in-line/g77-154-rotation-is-centered-half-turn

- **Type:** Structural theorem
- **Title:** Rotational symmetry of a 154-point configuration in \(G_{77}\)
- **Status:** Accepted as proved
- **Parent:** `programs/rotational-symmetry`

Primary judgment `sha256:21f3e6bb405eaaf804b58020a1695c213023b0dd3f1d25a08248fb5a48750eca` accepts as proved that if a 154-point no-three-in-line subset \(S\subset G_{77}\) has a nontrivial rotational symmetry, then:

- the symmetry is the half-turn about \((38,38)\); and
- \((38,38)\notin S\).

The judgment accepts the following associated constraints:

- quarter-turn symmetry is excluded by orbit cardinalities;
- equality in the row and column bounds forces exactly two selected points in every row and every column;
- consequently the coordinatewise bounding box is \([0,76]^2\);
- invariance of that bounding box forces the half-turn center to be \((38,38)\); and
- the unique fixed point of the half-turn is unselected.

The theorem is conditional on a 154-point configuration existing and having nontrivial rotational symmetry. It does not establish existence. It also does not exclude asymmetric or reflection-symmetric 154-point configurations.

Centered-half-turn invariance is not identified with the narrower `rct4` search class. The judgment explicitly preserves that distinction.

**Credit carried from the judgment**

The half-turn and quarter-turn orbit counting and the row/column occupancy observation were already present in earlier supplied evidence. The subject transaction presents the argument self-containedly and supplies the missing arbitrary-center rotation classification. It does not claim the earlier `rct4` construction methodology or known certificates.

**Authoritative provenance**

- Primary judgment: `sha256:21f3e6bb405eaaf804b58020a1695c213023b0dd3f1d25a08248fb5a48750eca`
- Claim key: `no-three-in-line/g77-154-rotation-is-centered-half-turn`
- Subject and evidence transaction: `29ccbd396781fd36d436ed2e6d0952a4730361b9`

## Change: no-three-in-line/g77-154-rotation-is-centered-half-turn

This node is created to preserve the accepted conditional classification of rotational symmetry at cardinality 154 without conflating it with existence, global impossibility, or the narrower `rct4` model.
