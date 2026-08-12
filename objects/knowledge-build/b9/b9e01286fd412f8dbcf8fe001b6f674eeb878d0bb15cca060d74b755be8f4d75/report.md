# Knowledge-Formation Report

## Node: root

- **Title:** Research state for no-three-in-line at grid size 77
- **Type:** Root
- **Status:** Active

### Central question

For

\[
G_{77}=\{0,1,\ldots,76\}^2,
\]

let \(D(77)\) be the largest cardinality of a subset containing no three distinct collinear points. The exact value remains unresolved:

\[
D(77)\in\{152,153,154\}.
\]

The current certified interval is

\[
\boxed{152\le D(77)\le154}.
\]

No supplied judgment establishes a 153- or 154-point certificate, excludes either cardinality globally, or improves the upper bound.

### Current global lower bound

The judgments support \(D(77)\ge152\) through an exact executable certificate for a 152-point no-three-in-line subset of \(G_{76}\), followed by the direct inclusion \(G_{76}\subset G_{77}\).

The baseline judgment accepted the certificate as an exact, self-contained computation using integer determinants on all

\[
\binom{152}{3}=573{,}800
\]

triples. A later replay package strongly supported the same mathematical artifact but did not supply evidence that its proposed governed hosted-verifier run had actually occurred. That missing hosted attestation does not alter the certificate’s mathematical implication.

### Current global upper bound

The judgments support \(D(77)\le154\). Each of the 77 horizontal rows is a line and can contain at most two selected points, so every no-three-in-line subset of \(G_{77}\) has at most \(2\cdot77=154\) points.

### Scope of the current advances

The supplied judgments establish additional structural information without changing the interval:

- hypothetical 153- and 154-point sets satisfy strict row and column occupancy conditions;
- the eight specified embeddings of the known 152-point \(G_{76}\) record are locally rigid against removing at most two record points;
- a hypothetical 153-point set cannot have nonidentity rotational symmetry;
- a rotationally symmetric hypothetical 154-point set must have the centered half-turn about \((38,38)\), with the center unselected;
- an exact SAT/CP-SAT-style model is available for the narrower 154-point `rct4` subclass, but the satisfiability of that model remains unknown.

None of these conclusions is a global impossibility theorem for 153 or 154 points.

### Durable research programs

1. [`programs/certificates-and-extremal-occupancy`](#node-programscertificates-and-extremal-occupancy)  
   Exact construction certificates and necessary occupancy structure near the row and column capacity.

2. [`programs/record-perturbation-rigidity`](#node-programsrecord-perturbation-rigidity)  
   Exact local analysis around the specified embeddings of the known 152-point record.

3. [`programs/symmetry-restricted-analysis`](#node-programssymmetry-restricted-analysis)  
   General rotational restrictions and exact models for symmetry-restricted searches.

The certified interval and exact-value question remain at root because they span all three programs.

### Conflict state

No conflict records or incompatible reconciliation outcomes were supplied. Accordingly, no active dispute node is required. Open mathematical questions remain represented as unresolved questions rather than adjudicative disputes.

### Governing provenance

- Baseline certificate and bounds judgment: `sha256:a470e4a9c0903097d9c860badaa8976cf32ed5336c154f11d8fad980d401f74e`
- Certificate replay judgment: `sha256:8c5f8eeb55af54b575fd3d46473e7894095afd6a4741186fe0583d3d0feade8a`
- Local rigidity judgment: `sha256:71fbde8d269728a92be52f6401e857230043ee6938c45f810c32308d88fb9927`
- Initial symmetry-restricted model judgment: `sha256:d24a70c16a08ff85401e969cfe12d8f8253056bb8d75e469ec226eba7a3b44c5`
- Completed arbitrary-center rotation judgment: `sha256:21f3e6bb405eaaf804b58020a1695c213023b0dd3f1d25a08248fb5a48750eca`

## Change: root

The root previously stated that no research programs had been established. This build replaces that empty state with the judgment-supported global interval, preserves the unresolved exact-value question at root, and establishes three durable programs for certificate structure, local perturbation rigidity, and symmetry-restricted analysis.

---

## Node: programs/certificates-and-extremal-occupancy

- **Title:** Exact certificates and near-capacity occupancy
- **Parent:** `root`
- **Type:** Research program
- **Status:** Active

### Program purpose

This program organizes exact coordinate certificates and necessary row-and-column structure for configurations near the elementary capacity \(2n\). It supports the global lower bound but does not own the cross-program certified interval, which remains at root.

### Current program knowledge

The judgments support an exact executable certificate for 152 distinct points in \(G_{76}\) with no three collinear. Direct inclusion into \(G_{77}\) supplies the current lower bound \(D(77)\ge152\).

For hypothetical configurations closer to the upper capacity:

- a 154-point no-three-in-line subset of \(G_{77}\) must have exactly two points in every row and exactly two points in every column;
- a 153-point subset must have exactly 76 rows with two points and one row with one point, and likewise exactly 76 columns with two points and one column with one point.

These are necessary conditions only. They establish neither existence nor nonexistence at either size.

### Program structure

- [`programs/certificates-and-extremal-occupancy/g76-152-certificate`](#node-programscertificates-and-extremal-occupancyg76-152-certificate)
- [`programs/certificates-and-extremal-occupancy/g77-near-capacity-occupancy`](#node-programscertificates-and-extremal-occupancyg77-near-capacity-occupancy)

### Provenance and credit

The supplied materials attribute the underlying 152-point configuration to Achim Flammenkamp’s maintained database. The baseline contribution is credited with making the certificate self-contained and supplying an independent exact verifier, rather than with originating the construction. The replay package is credited with packaging the existing artifacts for a proposed hosted verification, not with a new configuration, algorithm, or bound.

Relevant judgments:

- `sha256:a470e4a9c0903097d9c860badaa8976cf32ed5336c154f11d8fad980d401f74e`
- `sha256:8c5f8eeb55af54b575fd3d46473e7894095afd6a4741186fe0583d3d0feade8a`

## Change: programs/certificates-and-extremal-occupancy

This program is created to preserve the durable certificate and occupancy agenda separately from the global exact-value question. It consolidates the supported baseline construction and necessary near-capacity conditions without treating any submission or replay event as a knowledge node.

---

## Node: programs/certificates-and-extremal-occupancy/g76-152-certificate

- **Title:** Exact 152-point certificate in \(G_{76}\)
- **Parent:** `programs/certificates-and-extremal-occupancy`
- **Type:** Certified construction
- **Status:** Supported

### Current knowledge

The judgments support the existence of a 152-point subset of

\[
G_{76}=\{0,\ldots,75\}^2
\]

containing no three collinear points.

The supplied encoded artifact decodes to two points in each of 76 rows. The exact verifier checks:

- that all 152 decoded points are distinct;
- that every coordinate lies in \(\{0,\ldots,75\}^2\);
- that the determinant is nonzero for every one of the
  \[
  \binom{152}{3}=573{,}800
  \]
  unordered triples.

The judgments characterize this as an exact, reproducible computational certificate using integer arithmetic. The same coordinates embed unchanged into \(G_{77}\), yielding the root-level lower bound

\[
D(77)\ge152.
\]

### Verification qualifications

The later replay package contains a complete deterministic checker and expected output, but its proposed governed hosted-verifier acceptance is not established. No hosted attestation, exit status, transcript, or hosted output was supplied. A future hosted run would add execution independence, not algorithmic independence, because the checker was copied from the earlier artifact.

The baseline verifier accepts a leading symmetry marker but does not itself verify quarter-turn symmetry. This does not weaken its certification of the 152-point no-three-in-line property. Quarter-turn symmetry of the specific record was separately supported by the local-rigidity judgment.

The replay README contains an incorrect provenance pointer:

- stated pointer: `dfc0cc40d1193b8d5ca25e7f177fa48ff9a1b38d`;
- supplied baseline transaction: `dfc0cc40d41105292a119840dcdbe6f22860cf43`.

The replay judgment treats this as a clerical metadata error that does not affect the coordinates, checker, or lower-bound implication. Strict byte-for-byte identity of the republished files was not independently established by a checksum, although unchanged mathematical substance was strongly supported.

### Provenance and credit

**Subject transactions**

- `dfc0cc40d41105292a119840dcdbe6f22860cf43`
- `0ffe9a12c3ad44cf136dd22df7083dcdd53af1b0`

**Judgments**

- `sha256:a470e4a9c0903097d9c860badaa8976cf32ed5336c154f11d8fad980d401f74e`
- `sha256:8c5f8eeb55af54b575fd3d46473e7894095afd6a4741186fe0583d3d0feade8a`

The underlying construction is attributed in the supplied materials to Achim Flammenkamp’s maintained database. The baseline packaging and verifier are credited as a self-contained reproduction and exact check. The replay package is credited only for packaging a proposed hosted-verification request and republishing the artifacts.

## Change: programs/certificates-and-extremal-occupancy/g76-152-certificate

This node is created to materialize the durable certified construction underlying the lower bound. It also records the judgment-prescribed distinction between mathematical certificate validity, unestablished hosted execution, and the replay package’s clerical provenance error.

---

## Node: programs/certificates-and-extremal-occupancy/g77-near-capacity-occupancy

- **Title:** Necessary occupancy conditions at cardinalities 153 and 154
- **Parent:** `programs/certificates-and-extremal-occupancy`
- **Type:** Structural result
- **Status:** Supported

### Current knowledge

The baseline judgment supports the following necessary conditions for no-three-in-line subsets of \(G_{77}\).

#### Cardinality 154

Any 154-point no-three-in-line set must contain exactly two points in each of the 77 rows and exactly two points in each of the 77 columns.

#### Cardinality 153

Any 153-point no-three-in-line set must contain:

- exactly two points in 76 rows and one point in the remaining row; and
- exactly two points in 76 columns and one point in the remaining column.

### Scope

The judgments expressly qualify these occupancy patterns as necessary conditions only. They do not establish that a 153- or 154-point set exists, and they do not prove that either cardinality is impossible.

The 154-point occupancy condition is also used by the accepted rotational analysis to force the full coordinate range and hence the center of any half-turn symmetry. That dependency is represented in the symmetry program rather than by moving this occupancy result out of its certificate-and-capacity context.

### Provenance

- Subject transaction: `dfc0cc40d41105292a119840dcdbe6f22860cf43`
- Judgment: `sha256:a470e4a9c0903097d9c860badaa8976cf32ed5336c154f11d8fad980d401f74e`

## Change: programs/certificates-and-extremal-occupancy/g77-near-capacity-occupancy

This node is created because the row-and-column patterns are durable structural constraints distinct from the certificate itself. Their explicitly necessary-only scope is preserved to prevent them from being read as existence or impossibility results.

---

## Node: programs/record-perturbation-rigidity

- **Title:** Local perturbation rigidity around the known 152-point record
- **Parent:** `root`
- **Type:** Research program
- **Status:** Active

### Program purpose

This program studies exact local neighborhoods of specified embeddings of the known 152-point \(G_{76}\) record inside \(G_{77}\). Its current scope is limited to the eight embeddings obtained from the record’s two distinct dihedral images and the four translations in \(\{0,1\}^2\).

### Current program knowledge

The judgments support, with high confidence from exact finite computations, that:

- the specified record has quarter-turn symmetry and exactly two distinct dihedral images;
- those images and four translations yield exactly eight distinct subsets of \(G_{77}\);
- every such embedding is inclusion-maximal in \(G_{77}\);
- no originally outside cell becomes addable after removing one embedded point;
- removing two embedded points frees at most one originally outside cell;
- every no-three-in-line set of size at least 153 is at symmetric-difference distance at least seven from each specified embedding.

### Program limitation

The program does not exclude improvements obtained after removing three or more embedded points. In particular, removing three points and adding four remains outside the certified neighborhood. It also does not constrain unrelated 152-point configurations or all possible embeddings and transformations.

### Program structure

- [`programs/record-perturbation-rigidity/specified-g76-record-embeddings`](#node-programsrecord-perturbation-rigidityspecified-g76-record-embeddings)
- [`programs/record-perturbation-rigidity/depth-two-local-rigidity`](#node-programsrecord-perturbation-rigiditydepth-two-local-rigidity)

### Provenance and credit

The local analysis, code, and text are attributed by the judgment report to a disclosed AI research agent working at Robert Raynor’s request. The underlying coordinate set remains attributed to Achim Flammenkamp’s maintained database.

- Subject transaction: `c5e8096d942d57228bb4fed00f7617fb6b43af9f`
- Baseline evidence transaction: `dfc0cc40d41105292a119840dcdbe6f22860cf43`
- Judgment: `sha256:71fbde8d269728a92be52f6401e857230043ee6938c45f810c32308d88fb9927`

## Change: programs/record-perturbation-rigidity

This program is created to preserve the exact local-neighborhood agenda around the known record. Its boundary follows the judgment’s qualification: depth at most two is certified, while broader claims about the entire perturbation strategy are not.

---

## Node: programs/record-perturbation-rigidity/specified-g76-record-embeddings

- **Title:** Symmetry orbit and eight specified embeddings of the \(G_{76}\) record
- **Parent:** `programs/record-perturbation-rigidity`
- **Type:** Certified finite structure
- **Status:** Supported with high confidence

### Current knowledge

For the specified 152-point configuration \(C\subseteq G_{76}\), the local-rigidity judgment supports:

1. invariance under the quarter-turn
   \[
   (x,y)\longmapsto(75-y,x);
   \]
2. exactly two distinct images under the dihedral group of the square;
3. exactly eight distinct subsets of \(G_{77}\) obtained by applying the four translations
   \[
   (t_x,t_y)\in\{0,1\}^2
   \]
   to those two distinct dihedral images.

The computation independently decodes the record, verifies its no-three-in-line property, applies the transformations, and deduplicates the resulting sets using exact coordinates and finite set equality.

### Scope

“Specified embeddings” means precisely those dihedral-and-translation placements. The result does not classify unrelated affine images, other 152-point configurations, or every possible realization of the record in \(G_{77}\).

The baseline certificate’s own checker did not verify the leading quarter-turn marker. Quarter-turn symmetry is supported here by the separate local-rigidity computation.

### Provenance

- Subject transaction: `c5e8096d942d57228bb4fed00f7617fb6b43af9f`
- Baseline evidence: `dfc0cc40d41105292a119840dcdbe6f22860cf43`
- Judgment: `sha256:71fbde8d269728a92be52f6401e857230043ee6938c45f810c32308d88fb9927`

## Change: programs/record-perturbation-rigidity/specified-g76-record-embeddings

This node is created to define the exact finite family to which the local-rigidity conclusions apply. Separating that family from the rigidity result prevents the eight embeddings from being mistaken for all configurations or all affine images.

---

## Node: programs/record-perturbation-rigidity/depth-two-local-rigidity

- **Title:** Saturation and depth-two rigidity of the specified embeddings
- **Parent:** `programs/record-perturbation-rigidity`
- **Type:** Exact computational result
- **Status:** Supported with high confidence

### Current knowledge

Let \(E\) be any one of the eight specified embeddings of the known 152-point record in \(G_{77}\).

#### Saturation

Every one of the

\[
77^2-152=5{,}777
\]

cells in \(G_{77}\setminus E\) is blocked by pairs of points of \(E\). For every embedding, the computation reports:

- at least two blocking pairs at each outside cell;
- total blocking incidence \(51{,}449\).

Consequently, each \(E\) is inclusion-maximal in \(G_{77}\). The judgment expressly distinguishes this from maximum cardinality.

#### One-removal robustness

For every \(r\in E\), removing \(r\) does not make any cell that was originally in \(G_{77}\setminus E\) addable. The removed point itself may of course be restored; the claim concerns only originally outside cells.

#### Two-removal accounting

For every unordered pair removed from \(E\):

- at most one originally outside cell becomes addable;
- exactly 16 removal pairs per embedding free a cell;
- these 16 pairs are distributed over four outside cells;
- each of those four cells is freed by four removal pairs;
- all reported cases use the two-lines-of-two mechanism.

The judgment supports this as a finite exact computation. A primitive-direction census and a line-walk/hitting-set enumeration provide structurally different cross-checks, although they share the decoded configuration and primitive-direction routine.

#### Distance consequence

For every no-three-in-line set \(S\subseteq G_{77}\), if

\[
|E\setminus S|\le2,
\]

then

\[
|S\setminus E|\le1
\quad\text{and}\quad
|S|\le152.
\]

Consequently, any no-three-in-line set with \(|S|\ge153\) must satisfy

\[
|E\setminus S|\ge3,\qquad
|S\setminus E|\ge4,\qquad
|E\triangle S|\ge7.
\]

The judgment accepts this consequence as proved from the supported local computations.

### Scope and evidentiary limits

The result rules out every improvement obtained from a specified embedding after removing at most two embedded points. It does not rule out:

- removal depth three or greater;
- a modification removing three points and adding four;
- configurations based on other 152-point sets;
- configurations at symmetric-difference distance at least seven;
- a global 153- or 154-point construction.

The computational judgment is based on exact source inspection and supplied deterministic output rather than a separately documented execution environment. It nevertheless assigns high confidence because the code is deterministic, standard-library-only, uses exact integer arithmetic, and requires agreement between complementary enumerations.

### Provenance and credit

- Subject transaction: `c5e8096d942d57228bb4fed00f7617fb6b43af9f`
- Baseline evidence: `dfc0cc40d41105292a119840dcdbe6f22860cf43`
- Judgment: `sha256:71fbde8d269728a92be52f6401e857230043ee6938c45f810c32308d88fb9927`

The local rigidity analysis, code, and text are attributed in the judgment report to the disclosed AI research agent working at Robert Raynor’s request.

## Change: programs/record-perturbation-rigidity/depth-two-local-rigidity

This node is created to consolidate the mutually dependent saturation, one-removal, two-removal, and distance conclusions into one durable local-rigidity result. The judgment’s rejection of the broader “entire perturbation strategy” wording is retained as an explicit depth limitation.

---

## Node: programs/symmetry-restricted-analysis

- **Title:** Rotational structure and symmetry-restricted search
- **Parent:** `root`
- **Type:** Research program
- **Status:** Active

### Program purpose

This program organizes general theorems about rotations preserving finite lattice sets, their consequences for hypothetical 153- and 154-point configurations in \(G_{77}\), and exact search models for narrower symmetry subclasses.

### Current program knowledge

The judgments support the following high-confidence structural conclusions:

- a nonidentity Euclidean rotation preserving a finite noncollinear subset of \(\mathbb Z^2\) must be a half-turn or quarter-turn, even when the center is arbitrary;
- a 153-point no-three-in-line subset of \(G_{77}\) cannot have any nonidentity rotational symmetry;
- if a 154-point no-three-in-line subset has nontrivial rotational symmetry, it must be invariant under the half-turn about \((38,38)\), and the center is unselected;
- centered half-turn symmetry is strictly broader than the `rct4` subclass;
- the supplied \(n=77\) `rct4` model exactly represents its stated 154-point subclass;
- bounded solver timeouts do not decide that model’s satisfiability.

### Scope

The program does not classify reflections. It does not exclude asymmetric or reflection-symmetric configurations. It also does not establish the existence or nonexistence of any general centered-half-turn 154-point set.

### Program structure

- [`programs/symmetry-restricted-analysis/finite-lattice-rotation-classification`](#node-programssymmetry-restricted-analysisfinite-lattice-rotation-classification)
- [`programs/symmetry-restricted-analysis/g77-153-154-rotational-restrictions`](#node-programssymmetry-restricted-analysisg77-153-154-rotational-restrictions)
- [`programs/symmetry-restricted-analysis/rct4-154-model`](#node-programssymmetry-restricted-analysisrct4-154-model)
- [`programs/symmetry-restricted-analysis/rct4-154-satisfiability`](#node-programssymmetry-restricted-analysisrct4-154-satisfiability)

### Provenance

- Initial symmetry-model judgment: `sha256:d24a70c16a08ff85401e969cfe12d8f8253056bb8d75e469ec226eba7a3b44c5`
- Completed rotation-classification judgment: `sha256:21f3e6bb405eaaf804b58020a1695c213023b0dd3f1d25a08248fb5a48750eca`

The latter judgment explicitly treats its arbitrary-center theorem as completing a missing justification in the earlier rotational classification, not as contradicting its narrowed mathematical conclusion.

## Change: programs/symmetry-restricted-analysis

This program is created to preserve the durable relationship between general rotational theorems and restricted computational searches. It keeps the exact `rct4` agenda subordinate to the broader symmetry analysis and preserves the judgment-supported distinction between `rct4` and general centered-half-turn configurations.

---

## Node: programs/symmetry-restricted-analysis/finite-lattice-rotation-classification

- **Title:** Classification of nontrivial rotations preserving finite noncollinear lattice sets
- **Parent:** `programs/symmetry-restricted-analysis`
- **Type:** General lemma
- **Status:** Accepted as proved

### Current knowledge

The completed rotation judgment accepts the following theorem with high confidence:

> If a finite noncollinear set \(S\subset\mathbb Z^2\) is preserved by a nonidentity Euclidean rotation about an arbitrary center, then the rotation is a half-turn or a quarter-turn.

The accepted proof establishes a rational rotation matrix from three noncollinear lattice points, obtains finite order from the induced permutation of the finite set, and excludes all other finite rotation orders using the rational algebraic-integer trace. This closes the arbitrary-center classification step that was missing from the earlier symmetry-model argument.

### Scope

The theorem requires noncollinearity. It concerns exact Euclidean rotations only and does not classify:

- reflections;
- affine automorphisms;
- approximate symmetries;
- arbitrary rotations preserving degenerate sets such as singletons.

### Relationship to earlier judgment

The earlier judgment on the `rct4` model accepted the half-turn and quarter-turn arguments but qualified the broad rotational conclusion because rotations of other orders about arbitrary centers had not been excluded in the displayed argument. The later accepted theorem supplies that missing classification. The supplied judgments describe this as completion of insufficient justification rather than a conflict in mathematical conclusions.

### Provenance and credit

- Subject transaction: `29ccbd396781fd36d436ed2e6d0952a4730361b9`
- Judgment: `sha256:21f3e6bb405eaaf804b58020a1695c213023b0dd3f1d25a08248fb5a48750eca`

The judgment credits this subject contribution with the decisive arbitrary-center finite-rotation argument. It notes that the half-turn and quarter-turn orbit arguments were already present in earlier supplied evidence. Broader historical priority for the general theorem was not adjudicated.

## Change: programs/symmetry-restricted-analysis/finite-lattice-rotation-classification

This node is created to record the accepted general theorem that completes the earlier rotational analysis. Its arbitrary-center and noncollinearity scope is stated explicitly so the result is not silently extended to reflections, affine maps, or degenerate finite sets.

---

## Node: programs/symmetry-restricted-analysis/g77-153-154-rotational-restrictions

- **Title:** Rotational restrictions for hypothetical 153- and 154-point configurations
- **Parent:** `programs/symmetry-restricted-analysis`
- **Type:** Structural result
- **Status:** Accepted as proved

### Current knowledge

#### Cardinality 153

Any 153-point no-three-in-line subset of \(G_{77}\), if one exists, has no nonidentity rotational symmetry about any center.

The accepted classification leaves only half-turns and quarter-turns. The supplied judgments accept the orbit and collinearity obstructions excluding both possibilities at cardinality 153.

This is not a nonexistence theorem. Reflection-symmetric and asymmetric 153-point sets remain possible in principle.

#### Cardinality 154

If a 154-point no-three-in-line subset of \(G_{77}\) has nontrivial rotational symmetry, then:

- its symmetry is the half-turn about
  \[
  (38,38);
  \]
- the center \((38,38)\) is unselected.

Quarter-turn symmetry is excluded by the accepted orbit-cardinality obstruction. The accepted occupancy result forces two points in every row and column, hence full coordinate range; the rotational judgment accepts that this forces the half-turn center to be the grid center.

This does not establish that a 154-point set exists. Asymmetric and reflection-symmetric 154-point sets remain possible in principle.

### Distinction from `rct4`

The judgments expressly state that general centered-half-turn invariance is broader than `rct4`. The `rct4` restrictions additionally impose an empty anti-diagonal, near-complete quarter-turn orbit structure, and a particular main-diagonal pair pattern. Therefore the centered-half-turn conclusion does not reduce the entire rotationally symmetric 154-point problem to the `rct4` instance.

### Provenance

**Subject transactions**

- `c98dd877ad81611a9a469b1bd790cd909b56b1ce`
- `29ccbd396781fd36d436ed2e6d0952a4730361b9`

**Judgments**

- `sha256:d24a70c16a08ff85401e969cfe12d8f8253056bb8d75e469ec226eba7a3b44c5`
- `sha256:21f3e6bb405eaaf804b58020a1695c213023b0dd3f1d25a08248fb5a48750eca`

The later judgment accepts the completed arbitrary-center classification and thereby removes the earlier proof gap while retaining the earlier qualification that `rct4` is only a strict subclass.

## Change: programs/symmetry-restricted-analysis/g77-153-154-rotational-restrictions

This node is created to hold the complete current rotational classification at the two unresolved cardinalities. It incorporates the later accepted arbitrary-center lemma while preserving the strict distinction between centered half-turn symmetry and the narrower `rct4` model.

---

## Node: programs/symmetry-restricted-analysis/rct4-154-model

- **Title:** Exact `rct4` model for a 154-point configuration in \(G_{77}\)
- **Parent:** `programs/symmetry-restricted-analysis`
- **Type:** Restricted exact model
- **Status:** Supported within its stated subclass

### Current knowledge

Static inspection in the `rct4` judgment supports, with high confidence, that the supplied \(n=77\) model is sound and complete for the stated 154-point `rct4` subclass.

That subclass requires:

1. the anti-diagonal to be empty;
2. occupied off-diagonal cells to occur in complete quarter-turn orbits;
3. exactly one half-turn pair on the main diagonal to be occupied.

For \(n=77\), the model contains:

- 1,444 off-diagonal quarter-turn-orbit variables;
- 38 main-diagonal half-turn-pair variables;
- exact cardinality requirements selecting 38 off-diagonal orbits and one diagonal pair;
- therefore exactly
  \[
  4\cdot38+2=154
  \]
  selected cells;
- 388,148 deduplicated line constraints in the reported deterministic census.

The judgment supports the primitive-line enumeration, weighted at-most-two line constraints, CNF translation, and model equivalence within this subclass. It also supports the exact handling of the center and diagonal structure.

### Calibration evidence

The five supplied calibration certificates at

\[
n=41,47,57,65,69
\]

provide exact regression checks at those sizes. The checker verifies their decoded points, no-three-in-line property, `rct4` orbit structure, and induced model assignments.

These certificates validate implementation behavior only at the five listed sizes. They do not establish a broader historical range claim, external provenance, or discovery priority.

### Scope

A feasible \(n=77\) model assignment would provide a 154-point no-three-in-line set and therefore settle the global value at 154. In contrast, infeasibility of this particular model would exclude only the `rct4` subclass.

The model does not encode every centered-half-turn configuration, every rotationally symmetric configuration, or every 154-point configuration.

### Provenance and credit

- Subject transaction: `c98dd877ad81611a9a469b1bd790cd909b56b1ce`
- Judgment: `sha256:d24a70c16a08ff85401e969cfe12d8f8253056bb8d75e469ec226eba7a3b44c5`

The judgment attributes the new symmetry observations, \(n=77\) model implementation, validation machinery, and bounded search report to Robert Raynor and the disclosed AI research agent. The underlying `rct4` class and symmetry-reduction method are attributed in the supplied materials to Thomas Prellberg.

## Change: programs/symmetry-restricted-analysis/rct4-154-model

This node is created to preserve the exact restricted model as a durable method rather than as a submission event. Its accepted model equivalence and calibration scope are recorded together with the decisive limitation that `rct4` is not the full centered-half-turn class.

---

## Node: programs/symmetry-restricted-analysis/rct4-154-satisfiability

- **Title:** Satisfiability of the \(n=77\) 154-point `rct4` instance
- **Parent:** `programs/symmetry-restricted-analysis`
- **Type:** Open restricted question
- **Status:** Unresolved

### Current knowledge

The satisfiability of the supplied \(n=77\) `rct4` model is not established.

The reported CP-SAT `UNKNOWN` outcomes and SAT timeouts prove neither satisfiability nor unsatisfiability. The judgment assigns them no negative mathematical force because:

- no solver returned a certified infeasibility result;
- no proof trace was supplied;
- no committed solver logs or exact invocation record were supplied;
- comparable bounded runs reportedly failed at calibration sizes where committed certificates establish satisfiability.

The private-channel breakthrough reference mentioned in the judgment report carries no mathematical weight because it supplies no coordinates, proof, solver output, or definite value.

### Implications of possible future outcomes

As scoped by the judgment:

- a feasible assignment would give a 154-point certificate and imply \(D(77)=154\);
- a certified proof of `rct4` infeasibility would rule out only the `rct4` subclass;
- such an infeasibility result would not rule out general centered-half-turn, reflection-symmetric, or asymmetric 154-point configurations.

No one of these outcomes is currently established.

### Provenance

- Subject transaction: `c98dd877ad81611a9a469b1bd790cd909b56b1ce`
- Judgment: `sha256:d24a70c16a08ff85401e969cfe12d8f8253056bb8d75e469ec226eba7a3b44c5`

## Change: programs/symmetry-restricted-analysis/rct4-154-satisfiability

This node is created because satisfiability of the exact restricted instance is a durable open mathematical-computational question distinct from the model’s accepted encoding correctness. The supplied timeouts are retained only as scoped provenance and are not converted into an infeasibility claim.
