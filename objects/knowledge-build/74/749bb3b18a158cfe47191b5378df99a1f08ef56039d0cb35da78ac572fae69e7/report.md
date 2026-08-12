# Knowledge-Formation Report

## Formation scope

This report organizes the supplied immutable judgments into a holistic current knowledge state for the no-three-in-line problem at grid size \(77\). It does not reassess the mathematics.

### Immutable provenance

- Earlier primary judgment: `sha256:a470e4a9c0903097d9c860badaa8976cf32ed5336c154f11d8fad980d401f74e`
- Current primary judgment: `sha256:71fbde8d269728a92be52f6401e857230043ee6938c45f810c32308d88fb9927`
- Baseline evidence transaction: `dfc0cc40d41105292a119840dcdbe6f22860cf43`
- Local-rigidity evidence transaction: `c5e8096d942d57228bb4fed00f7617fb6b43af9f`

No conflict records or reconciliation outcomes were supplied. Consequently, no active dispute node is required. The unresolved value of \(D(77)\) remains an open mathematical question caused by missing evidence, not a conflict between opposed judgments.

The existing nodes `no-three-in-line/d77-certified-interval` and `no-three-in-line/d77-near-capacity-occupancy` remain unchanged. They are included in the root inventory but are not rematerialized below.

---

## Node: root

- **Type:** Root research state
- **Status:** Active
- **Parent:** None
- **Primary provenance:**
  - `sha256:a470e4a9c0903097d9c860badaa8976cf32ed5336c154f11d8fad980d401f74e`
  - `sha256:71fbde8d269728a92be52f6401e857230043ee6938c45f810c32308d88fb9927`

For

\[
G_n=\{0,1,\ldots,n-1\}^2,
\]

let \(D(n)\) denote the largest cardinality of a subset of \(G_n\) containing no three distinct collinear points.

The current judge-established research state at grid size \(77\) consists of the following durable conclusions and open questions:

1. A particular 152-point no-three-in-line subset \(C\subseteq G_{76}\) has an exact coordinate certificate. Its no-three-in-line property was checked over all
   \[
   \binom{152}{3}=573{,}800
   \]
   triples using exact integer determinants.

2. The same configuration is invariant under the quarter-turn
   \[
   (x,y)\mapsto(75-y,x).
   \]
   It has exactly two distinct images under the eight dihedral symmetries of the square. Applying the four translations in \(\{0,1\}^2\) to those images produces exactly eight distinct specified subsets of \(G_{77}\).

3. The certified global interval remains
   \[
   152\le D(77)\le154.
   \]
   The lower bound comes from embedding the verified 152-point configuration, while the upper bound comes from the row-capacity argument already represented in the unchanged certified-interval node.

4. The previously represented necessary row and column occupancy constraints for hypothetical 153- and 154-point sets remain active and unchanged.

5. Each of the eight specified embeddings of the known configuration is saturated in \(G_{77}\): every one of its 5,777 outside cells is blocked by at least two pairs of embedded points. Each embedding is therefore inclusion-maximal, though not thereby established to have maximum cardinality.

6. Removing one point from any specified embedding does not make any cell that was originally outside the embedding addable. The removed point itself can still be restored.

7. Removing any two points from a specified embedding frees at most one originally outside cell. For each embedding, exactly 16 unordered removal pairs free a cell, distributed over four cells with four removal pairs per cell.

8. For every specified embedding \(E\), a no-three-in-line set \(S\) satisfying
   \[
   |E\setminus S|\le2
   \]
   must satisfy
   \[
   |S\setminus E|\le1
   \quad\text{and}\quad
   |S|\le152.
   \]
   Consequently, every no-three-in-line set \(S\subseteq G_{77}\) with \(|S|\ge153\) must satisfy, relative to each specified embedding,
   \[
   |E\setminus S|\ge3,\qquad |S\setminus E|\ge4,
   \qquad |E\triangle S|\ge7.
   \]

9. The exact value of \(D(77)\) remains unresolved. The local computations do not provide a 153- or 154-point certificate and do not prove that either cardinality is globally impossible. Removal depth three and greater, other 152-point configurations, and configurations sufficiently far from all eight specified embeddings remain outside the established exclusion.

The materialized node inventory is:

- `no-three-in-line/g76-152-point-set`
- `no-three-in-line/d77-certified-interval`
- `no-three-in-line/d77-near-capacity-occupancy`
- `no-three-in-line/d77-saturation-of-embedded-g76-152-record`
- `no-three-in-line/d77-one-removal-robustness-of-embedded-g76-record`
- `no-three-in-line/d77-two-removal-rigidity-of-embedded-g76-record`
- `no-three-in-line/d77-distance-from-embedded-g76-152-record`
- `no-three-in-line/d77-exact-value`

There are no active adjudicative conflicts in the supplied record.

---

## Node: no-three-in-line/g76-152-point-set

- **Type:** Verified existence, symmetry, and finite-orbit claim
- **Status:** Supported
- **Parent:** `root`
- **Primary provenance:**
  - `sha256:a470e4a9c0903097d9c860badaa8976cf32ed5336c154f11d8fad980d401f74e`
  - `sha256:71fbde8d269728a92be52f6401e857230043ee6938c45f810c32308d88fb9927`
- **Evidence transactions:**
  - `dfc0cc40d41105292a119840dcdbe6f22860cf43`
  - `c5e8096d942d57228bb4fed00f7617fb6b43af9f`

The immutable judgments support the existence of a particular 152-point subset

\[
C\subseteq G_{76}=\{0,\ldots,75\}^2
\]

containing no three distinct collinear points.

The supplied payload decodes deterministically into 76 pairs of points, with two points in each row \(y=0,\ldots,75\). The judgments report that the certificate and verifier establish:

- exactly 152 distinct decoded points;
- all coordinates lie in \(G_{76}\);
- duplicate and out-of-grid points are rejected;
- all
  \[
  \binom{152}{3}=573{,}800
  \]
  unordered triples are checked;
- collinearity is tested using the exact integer determinant
  \[
  (x_2-x_1)(y_3-y_1)-(x_3-x_1)(y_2-y_1);
  \]
- the computation uses exact integer arithmetic; and
- no defect was identified in the decoding or no-three-in-line verification logic.

The current primary judgment additionally supports with high confidence that \(C\) is invariant under

\[
q(x,y)=(75-y,x).
\]

Enumeration and deduplication of all eight dihedral transformations of the \(76\times76\) square produce exactly two distinct images of \(C\). Applying to those two images each translation

\[
(t_x,t_y)\in\{0,1\}^2
\]

produces exactly eight distinct subsets of \(G_{77}\).

### Scope

The symmetry conclusion concerns this particular certified configuration. It does not establish that all optimal or near-optimal configurations in \(G_{76}\) or \(G_{77}\) possess quarter-turn symmetry.

The count of eight embeddings is restricted to:

1. the two distinct dihedral images of \(C\); and
2. the four placements of \(G_{76}\) inside \(G_{77}\) obtained by translations in \(\{0,1\}^2\).

It does not cover unrelated affine images or other 152-point configurations.

### Evidentiary qualification

The current judgment was based on static inspection of the deterministic standard-library checker and its supplied result file rather than a separately documented execution in an independent environment. The judgment nevertheless assigns high confidence because the decisive routines are finite, exact, deterministic, and auditable.

### Credit

The underlying coordinate set is attributed in the supplied materials to Achim Flammenkamp’s maintained database. Robert is credited with reproducing and independently verifying the baseline certificate, not with originating the underlying construction. The finer priority or authorship history of the 152-point construction remains undetermined by the supplied evidence.

The local symmetry analysis, code, and accompanying text are attributed by the current judgment to an AI research agent working at Robert Raynor’s request.

---

## Node: no-three-in-line/d77-saturation-of-embedded-g76-152-record

- **Type:** Exact computational structural claim
- **Status:** Supported with high confidence
- **Parent:** `root`
- **Primary provenance:** `sha256:71fbde8d269728a92be52f6401e857230043ee6938c45f810c32308d88fb9927`
- **Evidence transactions:**
  - `dfc0cc40d41105292a119840dcdbe6f22860cf43`
  - `c5e8096d942d57228bb4fed00f7617fb6b43af9f`
- **Related configuration:** `no-three-in-line/g76-152-point-set`

Let \(E\subseteq G_{77}\) be any one of the eight specified subsets obtained from the two distinct dihedral images of the certified 152-point configuration in \(G_{76}\), followed by a translation in \(\{0,1\}^2\).

The current primary judgment supports with high confidence that every cell of

\[
G_{77}\setminus E
\]

is collinear with a pair of points of \(E\). More precisely, for every specified embedding:

- there are
  \[
  77^2-152=5{,}777
  \]
  outside cells;
- every outside cell has at least two distinct blocking pairs from \(E\); and
- the total blocking incidence is \(51{,}449\).

The judgment therefore concludes that each specified embedding is inclusion-maximal in \(G_{77}\): no additional point can be added to it while retaining the no-three-in-line property.

### Certificate basis

The judgment reports two complementary exact enumerations:

- a primitive-direction census through each outside cell; and
- a pair-based primitive line walk through the grid.

The checker requires exact agreement between the two enumerations in both the set of blocked cells and the number of blocking pairs at every cell.

### Scope

Inclusion-maximality is not maximum cardinality. This claim does not exclude:

- unrelated 153- or 154-point sets;
- other 152-point configurations;
- affine images outside the specified dihedral-and-translation family; or
- configurations reached after removing points from \(E\) before adding others.

### Evidentiary qualification and credit

The supporting judgment assigns high confidence based on static inspection of deterministic exact code and the committed result file, without a separately documented independent execution.

The coordinate configuration is attributed to Achim Flammenkamp’s maintained database. The saturation analysis, code, and text are attributed to an AI research agent working at Robert Raynor’s request.

---

## Node: no-three-in-line/d77-one-removal-robustness-of-embedded-g76-record

- **Type:** Exact computational local-rigidity claim
- **Status:** Supported with high confidence
- **Parent:** `root`
- **Primary provenance:** `sha256:71fbde8d269728a92be52f6401e857230043ee6938c45f810c32308d88fb9927`
- **Evidence transactions:**
  - `dfc0cc40d41105292a119840dcdbe6f22860cf43`
  - `c5e8096d942d57228bb4fed00f7617fb6b43af9f`
- **Related configuration:** `no-three-in-line/g76-152-point-set`
- **Related saturation claim:** `no-three-in-line/d77-saturation-of-embedded-g76-152-record`

For every one of the eight specified embeddings \(E\subseteq G_{77}\) and every point \(r\in E\), the current primary judgment supports with high confidence that removing \(r\) does not make any cell that was originally outside \(E\) addable.

Equivalently, every

\[
c\in G_{77}\setminus E
\]

remains blocked by a surviving pair of points from \(E\setminus\{r\}\).

### Scope

The claim concerns cells that were outside the original embedding. It does not say that \(E\setminus\{r\}\) has no addable cell at all: the removed point \(r\) can be restored.

The result is restricted to the eight specified embeddings of the particular certified configuration. It is not a statement about all 152-point no-three-in-line subsets of \(G_{77}\).

### Certificate basis and qualification

The judgment reports that the checker exhaustively enumerates removal sets of size at most two capable of destroying all blocking pairs through an outside cell. It reports no singleton removal freeing an originally outside cell, and the complementary line-walk/hitting-set reconstruction is required to agree cell by cell.

The judgment assigns high confidence based on exact deterministic computation and source inspection, while noting the absence of a separately documented execution in an independent environment.

### Credit

The underlying coordinate set is attributed to Achim Flammenkamp’s maintained database. The one-removal analysis, code, and text are attributed to an AI research agent working at Robert Raynor’s request.

---

## Node: no-three-in-line/d77-two-removal-rigidity-of-embedded-g76-record

- **Type:** Exact computational local-rigidity claim
- **Status:** Supported with high confidence
- **Parent:** `root`
- **Primary provenance:** `sha256:71fbde8d269728a92be52f6401e857230043ee6938c45f810c32308d88fb9927`
- **Evidence transactions:**
  - `dfc0cc40d41105292a119840dcdbe6f22860cf43`
  - `c5e8096d942d57228bb4fed00f7617fb6b43af9f`
- **Related configuration:** `no-three-in-line/g76-152-point-set`

For every one of the eight specified embeddings \(E\subseteq G_{77}\), the current primary judgment supports with high confidence the following complete accounting of two-point removals:

- removing any unordered pair of points of \(E\) frees at most one cell that was originally in \(G_{77}\setminus E\);
- exactly 16 unordered removal pairs per embedding free an outside cell;
- those 16 pairs are distributed over exactly four outside cells;
- each of the four cells is freed by exactly four removal pairs; and
- every reported freeing uses the “two-lines-of-two” mechanism identified by the computation.

The judgment reports that each claimed freeing was directly simulated against all pairs among the 150 surviving embedded points.

### Certificate basis

The primary judgment attributes the result to exhaustive finite computation using:

1. a direction census that determines the blocking lines through each outside cell;
2. a line-walk reconstruction of the blocking-pair table;
3. a hitting-set enumeration of removal sets of size at most two;
4. direct simulation of every reported freed cell; and
5. an exact required match between recomputed output and the committed result file.

The direction-census and line-walk methods are structurally different cross-checks, but the judgment qualifies their independence because they share the decoded configuration and a small primitive-direction routine.

### Scope

The result concerns removal of exactly two embedded points and addability of cells that were originally outside the embedding. It does not address removal sets of size three or greater.

It also does not establish a global restriction on all 152-, 153-, or 154-point configurations in \(G_{77}\).

### Evidentiary qualification and credit

The judgment assigns high confidence based on deterministic exact source inspection and the supplied output, without a separately documented independent execution.

The underlying coordinate set is attributed to Achim Flammenkamp’s maintained database. The two-removal analysis, code, and text are attributed to an AI research agent working at Robert Raynor’s request.

---

## Node: no-three-in-line/d77-distance-from-embedded-g76-152-record

- **Type:** Structural consequence for nearby configurations
- **Status:** Proved from the supported local computations
- **Parent:** `root`
- **Primary provenance:** `sha256:71fbde8d269728a92be52f6401e857230043ee6938c45f810c32308d88fb9927`
- **Evidence transactions:**
  - `dfc0cc40d41105292a119840dcdbe6f22860cf43`
  - `c5e8096d942d57228bb4fed00f7617fb6b43af9f`
- **Related local claims:**
  - `no-three-in-line/d77-saturation-of-embedded-g76-152-record`
  - `no-three-in-line/d77-one-removal-robustness-of-embedded-g76-record`
  - `no-three-in-line/d77-two-removal-rigidity-of-embedded-g76-record`

Let \(E\) be any one of the eight specified embeddings of the certified 152-point configuration, and let \(S\subseteq G_{77}\) be no-three-in-line.

The current primary judgment concludes from the supported saturation and removal computations that if

\[
|E\setminus S|\le2,
\]

then

\[
|S\setminus E|\le1
\quad\text{and}\quad
|S|\le152.
\]

Consequently, every no-three-in-line set \(S\) with

\[
|S|\ge153
\]

must satisfy, relative to every specified embedding \(E\),

\[
|E\setminus S|\ge3,
\qquad
|S\setminus E|\ge4,
\]

and therefore

\[
|E\triangle S|\ge7.
\]

Thus no 153- or 154-point configuration can be obtained from any specified embedding after removing at most two of its points.

### Scope

The judgment expressly does not extend this exclusion to the entire strategy of perturbing the known configuration. In particular, it does not rule out:

- removing three embedded points and adding four;
- any other modification of removal depth at least three;
- perturbations of other 152-point configurations; or
- configurations lying at symmetric-difference distance at least seven from every specified embedding.

This is a local distance constraint, not a global impossibility theorem and not an improvement to the certified interval for \(D(77)\).

### Credit

The underlying coordinate set is attributed to Achim Flammenkamp’s maintained database. The local computations and resulting symmetric-difference analysis are attributed to an AI research agent working at Robert Raynor’s request.

---

## Node: no-three-in-line/d77-exact-value

- **Type:** Open mathematical question
- **Status:** Unresolved
- **Parent:** `root`
- **Primary provenance:**
  - `sha256:a470e4a9c0903097d9c860badaa8976cf32ed5336c154f11d8fad980d401f74e`
  - `sha256:71fbde8d269728a92be52f6401e857230043ee6938c45f810c32308d88fb9927`
- **Evidence transactions:**
  - `dfc0cc40d41105292a119840dcdbe6f22860cf43`
  - `c5e8096d942d57228bb4fed00f7617fb6b43af9f`
- **Related bound:** `no-three-in-line/d77-certified-interval`
- **Related constraints:**
  - `no-three-in-line/d77-near-capacity-occupancy`
  - `no-three-in-line/d77-distance-from-embedded-g76-152-record`

The exact value of \(D(77)\) remains unresolved under the supplied immutable judgments. The strongest globally certified conclusion remains

\[
152\le D(77)\le154.
\]

The evidence contains neither:

- a 153-point coordinate certificate;
- a 154-point coordinate certificate;
- a global impossibility proof for 153 points;
- a global impossibility proof for 154 points;
- a global exhaustive search;
- nor a symmetry-class impossibility theorem that narrows the certified interval.

The supported local computations establish that a set of size at least 153 must differ from each of the eight specified embeddings by at least three removals and four additions, giving symmetric-difference distance at least seven. They do not constrain all configurations at or beyond that distance and do not address all other 152-point configurations.

Accordingly, the currently supported possibilities remain

\[
D(77)\in\{152,153,154\}.
\]

This is unresolved because decisive evidence is absent. It is not an active dispute between incompatible judgments.

---

# Revision Provenance

## Change: root

The root node is revised to incorporate the durable conclusions of primary judgment `sha256:71fbde8d269728a92be52f6401e857230043ee6938c45f810c32308d88fb9927`.

The previous root represented the verified \(G_{76}\) certificate, the certified interval, near-capacity occupancy constraints, and the unresolved exact value. The revised root additionally inventories:

- verified quarter-turn symmetry and the finite family of eight specified embeddings;
- saturation of those embeddings;
- one-removal robustness;
- complete two-removal rigidity;
- the resulting symmetric-difference constraint.

No previous conclusion is retracted. The certified interval and occupancy nodes remain unchanged. No dispute node is introduced because the conflict record is empty and the exact-value uncertainty is not adjudicative opposition.

## Change: no-three-in-line/g76-152-point-set

This existing node is revised rather than split into an event-shaped symmetry node.

The earlier primary judgment, `sha256:a470e4a9c0903097d9c860badaa8976cf32ed5336c154f11d8fad980d401f74e`, supported the 152-point certificate but stated that its verifier did not independently verify the leading quarter-turn symmetry marker.

The current primary judgment, `sha256:71fbde8d269728a92be52f6401e857230043ee6938c45f810c32308d88fb9927`, explicitly supports quarter-turn invariance, exactly two distinct dihedral images, and exactly eight translated embeddings in \(G_{77}\). The former verifier limitation is therefore no longer the complete current account of the configuration’s symmetry. It is replaced in the materialized node by the newly supported symmetry conclusion.

The baseline no-three-in-line certificate and its credit statements are retained.

## Change: no-three-in-line/d77-saturation-of-embedded-g76-152-record

This is a proposed new stable node because saturation is a distinct durable property of the eight specified embedded configurations. It remains mathematically meaningful without reference to the transaction or chronology.

The node is justified by Finding 2 of primary judgment `sha256:71fbde8d269728a92be52f6401e857230043ee6938c45f810c32308d88fb9927`. Its scope preserves the judgment’s distinction between inclusion-maximality and maximum cardinality.

## Change: no-three-in-line/d77-one-removal-robustness-of-embedded-g76-record

This is a proposed new stable node because robustness after one removal is a distinct local structural property not represented by the saturation claim alone.

It is justified by Finding 3 of primary judgment `sha256:71fbde8d269728a92be52f6401e857230043ee6938c45f810c32308d88fb9927`. The node preserves the judgment’s qualification that only cells originally outside the embedding remain blocked; the removed point itself may be restored.

## Change: no-three-in-line/d77-two-removal-rigidity-of-embedded-g76-record

This is a proposed new stable node because the exhaustive two-removal accounting is a durable finite classification distinct from both saturation and one-removal robustness.

It is justified by Finding 4 of primary judgment `sha256:71fbde8d269728a92be52f6401e857230043ee6938c45f810c32308d88fb9927`. The node retains the exact counts, the “two-lines-of-two” classification, and the judgment’s limited-independence qualification for the computational cross-checks.

## Change: no-three-in-line/d77-distance-from-embedded-g76-152-record

This is a proposed new stable node because the symmetric-difference lower bound is a distinct reusable structural consequence concerning all hypothetical sets of size at least 153 relative to the specified embeddings.

It is justified by Finding 5 of primary judgment `sha256:71fbde8d269728a92be52f6401e857230043ee6938c45f810c32308d88fb9927`.

The node also carries the judgment’s qualification of the broader “perturb the known record” description: only modifications involving at most two removals are excluded. Removal depth three or greater remains unexplored.

## Change: no-three-in-line/d77-exact-value

The exact-value node remains unresolved and retains the interval

\[
152\le D(77)\le154.
\]

It is revised to include the newly supported local exclusion around the eight specified embeddings. This does not change the answer set \(\{152,153,154\}\), because primary judgment `sha256:71fbde8d269728a92be52f6401e857230043ee6938c45f810c32308d88fb9927` expressly supplies neither a larger coordinate certificate nor a global impossibility proof.

The node continues to represent an open question rather than an active dispute.
