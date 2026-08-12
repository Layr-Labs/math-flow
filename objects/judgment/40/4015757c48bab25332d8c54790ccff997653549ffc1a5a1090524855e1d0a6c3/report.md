# Mathematical Judgment

## Overall assessment

The subject transaction provides a **substantial and reproducible local rigidity result** for the known 152-point configuration, but it does **not determine \(D(77)\)** and does not improve the certified interval

\[
152\le D(77)\le 154.
\]

The formal computational claims are well scoped and are supported by complete Python source, exact integer arithmetic, explicit expected results, and two complementary enumerations. Static inspection finds the mathematical logic of the checker sound. The strongest justified conclusion is that every specified embedding of this particular 152-point record is resistant to modifications involving the removal of at most two of its points.

The introductory statement that the computation “prunes the entire ‘perturb the known record’ strategy” is too broad: perturbations removing three or more record points remain entirely unexplored. The later formal claims and “Known gaps and limitations” section correctly state the narrower scope.

---

## Finding 1: Quarter-turn symmetry and the eight specified embeddings

**Claim key:** `no-three-in-line/g76-record-quarter-turn-symmetry-and-dihedral-orbit`

**Claim.** The supplied 152-point configuration \(C\subseteq G_{76}\) is invariant under

\[
(x,y)\longmapsto (75-y,x),
\]

has exactly two distinct images under the dihedral group of the square, and consequently gives exactly eight distinct subsets of \(G_{77}\) after applying those images and translations by \((t_x,t_y)\in\{0,1\}^2\).

**Judgment:** **Supported with high confidence.**

### Decisive evidence

The checker:

1. independently decodes the supplied coordinate string;
2. verifies that it gives 152 distinct points in \(G_{76}\);
3. checks all
   \[
   \binom{152}{3}=573{,}800
   \]
   triples by the exact determinant test;
4. explicitly applies the quarter-turn and compares the resulting point set with the original;
5. enumerates all eight dihedral transformations and deduplicates their images;
6. applies all four allowed translations to every distinct image and deduplicates the resulting subsets of \(G_{77}\);
7. asserts that the resulting numbers are exactly two dihedral images and eight embeddings.

These operations use finite set equality and integer coordinates, so there is no numerical ambiguity.

The translations \((0,0),(0,1),(1,0),(1,1)\) are the natural placements of the \(76\times76\) square inside \(G_{77}\). The computation’s use of the term “embedding” is explicitly restricted to dihedral images followed by these translations. It should not be interpreted as covering unrelated affine images or other 152-point configurations.

### Scope

This verifies symmetry of the particular supplied record, not a general symmetry property of all optimal or near-optimal configurations on \(G_{76}\) or \(G_{77}\).

---

## Finding 2: Saturation of every specified embedding in \(G_{77}\)

**Claim key:** `no-three-in-line/d77-saturation-of-embedded-g76-152-record`

**Claim.** For each of the eight specified embeddings \(E\subseteq G_{77}\), every cell of \(G_{77}\setminus E\) is collinear with a pair of points of \(E\). In fact, every such cell has at least two distinct blocking pairs. Therefore \(E\) is inclusion-maximal in \(G_{77}\).

**Judgment:** **Supported with high confidence as an exact computational certificate.**

### Decisive reasoning

For a fixed outside cell \(c\), the primary computation groups the 152 points according to the sign-normalized primitive direction of \(p-c\). Two points lie with \(c\) on the same line exactly when they belong to the same direction group. Thus a direction group of size at least two gives a blocking pair.

The checker fails if any outside cell has no heavy direction group. The generated result reports:

- \(77^2-152=5777\) outside cells for every embedding;
- minimum blocking-pair count equal to \(2\);
- total blocking incidence \(51449\) for every embedding.

The independent line-walk enumeration starts from every pair of configuration points, walks the complete primitive lattice line through that pair inside \(G_{77}\), and reconstructs the blocking-pair table. It requires exact agreement with the direction census both in the set of blocked cells and in the number of blocking pairs at every cell.

Since the no-three-in-line property is hereditary, if a proper superset of \(E\) were valid, then adding any one of its new points to \(E\) would also be valid. Saturation rules this out. Thus the conclusion that \(E\) is maximal is valid.

### Important distinction

“Maximal” here means that no further point can be added while retaining the property. It does **not** mean “maximum cardinality.” A saturated 152-point set is compatible with the possible existence of unrelated 153- or 154-point sets.

---

## Finding 3: Robust saturation after one removal

**Claim key:** `no-three-in-line/d77-one-removal-robustness-of-embedded-g76-record`

**Claim.** For every specified embedding \(E\) and every \(r\in E\), removing \(r\) does not make any previously outside cell \(c\in G_{77}\setminus E\) addable.

**Judgment:** **Supported with high confidence.**

### Decisive reasoning

For a fixed outside cell \(c\), the blocking lines through \(c\) are disjoint away from \(c\). Therefore one removed configuration point can affect at most one blocking line through \(c\). The census explicitly enumerates all minimal removal sets of size at most two that would destroy every blocking pair at \(c\).

The checker fails if it finds any singleton removal that frees a previously outside cell. The committed computation reports zero such singleton freeings for all eight embeddings, and the line-walk/hitting-set reconstruction is required to agree cell by cell.

The wording “no cell is freed” must retain the contribution’s stated qualification: it concerns cells in \(G_{77}\setminus E\). The removed point \(r\) itself can of course be added back.

---

## Finding 4: Complete two-removal accounting

**Claim key:** `no-three-in-line/d77-two-removal-rigidity-of-embedded-g76-record`

**Claim.** For every specified embedding \(E\), removing any unordered pair of points of \(E\) frees at most one cell of \(G_{77}\setminus E\). Exactly 16 removal pairs free a cell; these 16 pairs are distributed over four cells, four removal pairs per cell.

**Judgment:** **Supported with high confidence as a finite exact computation.**

### Why the enumeration is exhaustive

For a fixed outside cell \(c\), let the heavy lines through \(c\) contain \(n_1,n_2,\ldots\) configuration points. To make \(c\) addable, every heavy line must be reduced to at most one surviving point. Because distinct lines through \(c\) have disjoint configuration-point sets, this requires

\[
\sum_i (n_i-1)
\]

removals.

With a budget of at most two removals, the only generic possibilities are:

1. one line containing two points, requiring one removal;
2. one line containing three points, requiring two removals;
3. two lines containing two points each, requiring one removal on each line.

The base set is already verified to have no three collinear points, so a heavy line containing three configuration points cannot actually occur here. The reported pair freeings are all of the third type, labeled “two-lines-of-two.”

The checker then independently treats the blocking pairs through a cell as a hitting-set problem. Any pair of removed points that frees the cell must hit every blocking pair. Its hitting-set routine exhaustively finds all such sets of size at most two and compares them against the census enumeration.

Finally:

- pair-removal freeings are stored by unordered removal pair;
- the checker fails if one removal pair frees more than one outside cell;
- every reported freeing is directly simulated by testing the freed cell against all
  \[
  \binom{150}{2}
  \]
  remaining pairs;
- the full generated output must byte-match the committed `results.json`;
- each embedding is required to have exactly 16 freeing pairs.

This is sufficient to establish the claimed two-removal accounting, assuming successful execution of the supplied checker.

### Independence qualification

The census and line-walk methods are structurally different, which is a valuable cross-check. They are not wholly independent implementations: they share the decoded configuration and the small `primitive` direction routine. That shared routine is simple and auditable, so this does not create a serious correctness concern, but “independent” should be understood in this limited computational sense.

---

## Finding 5: Distance constraint for any 153- or 154-point configuration

**Claim key:** `no-three-in-line/d77-distance-from-embedded-g76-152-record`

**Claim.** Let \(E\) be any one of the eight specified embeddings. If \(S\subseteq G_{77}\) is no-three-in-line and \(|E\setminus S|\le2\), then

\[
|S\setminus E|\le1
\quad\text{and}\quad
|S|\le152.
\]

Consequently, any no-three-in-line set \(S\) with \(|S|\ge153\) must satisfy

\[
|E\setminus S|\ge3,\qquad |S\setminus E|\ge4,
\]

and hence

\[
|E\triangle S|\ge7.
\]

**Judgment:** **Proved from the supported computational findings.**

### Decisive proof

Write

\[
R=E\setminus S,\qquad A=S\setminus E,
\]

so that

\[
S=(E\setminus R)\cup A.
\]

Every \(a\in A\) must be unblocked by \(E\setminus R\); otherwise \(a\) and a surviving pair from \(E\) would form a collinear triple in \(S\).

- If \(|R|=0\), saturation permits no points of \(A\).
- If \(|R|=1\), one-removal robustness permits no points of \(A\).
- If \(|R|=2\), the two-removal result permits at most one point of \(A\).

Therefore \(|A|\le1\) whenever \(|R|\le2\), and

\[
|S|=152-|R|+|A|\le152.
\]

If instead \(|S|\ge153\), then \(|R|\ge3\), and

\[
|A|=|S|-152+|R|\ge153-152+3=4.
\]

Thus

\[
|E\triangle S|=|R|+|A|\ge3+4=7.
\]

This implication is purely deductive once the local computational claims are accepted.

---

## Finding 6: No improvement to the global value of \(D(77)\)

**Claim key:** `no-three-in-line/d77-exact-value`

**Claim addressed.** Whether \(D(77)\) equals \(152\), \(153\), or \(154\).

**Judgment:** **Unresolved by this transaction.**

The transaction supplies neither:

- a 153- or 154-point coordinate certificate, nor
- a global impossibility proof for 153 or 154 points.

It only excludes larger configurations within a precisely described neighborhood of eight embeddings of one known 152-point set. Other 152-point configurations, or configurations differing from every listed embedding by at least seven points, are not constrained by the computation.

Accordingly, the certified interval remains

\[
152\le D(77)\le154.
\]

---

## Overstatement and internal scope tension

The sentence claiming that the result

> “prunes the entire ‘perturb the known record’ strategy for reaching 153 or 154 points”

is not justified literally. The computation explores only removals of depth at most two. Its own later limitation states that depth three and beyond is unexamined. A set obtained by removing three record points and adding four new points is still naturally describable as a perturbation, and such a set is not ruled out.

The defensible replacement is:

> The computation rules out every improvement obtained from any specified embedding after removing at most two of its points.

The formal corollary and the limitations section use the correct restricted scope, so this promotional overstatement does not invalidate the mathematical certificate.

---

## Reproducibility and missing evidence

The supplied evidence is unusually complete for a computational local result:

- the exact base certificate is supplied;
- its source path and expected hash are recorded;
- the decoder is included;
- all collinearity tests use exact integer determinants;
- all transformations and translations are explicitly enumerated;
- there is no randomness or external solver;
- the output is committed in full;
- recomputation must byte-match that output.

The main evidentiary limitation is that this judgment is based on source inspection and the supplied result file rather than an independently documented execution in a separate environment. Nevertheless, the program is standard-library-only, deterministic, and short enough in its decisive routines to audit. The warranted confidence is therefore high.

No evidence is supplied for:

- removal neighborhoods of depth at least three;
- other 152-point configurations in \(G_{77}\);
- a global exhaustive search;
- a symmetry-class impossibility theorem;
- an improved upper or lower bound.

---

## Contribution and priority

The underlying 152-point coordinate set is attributed in the supplied materials to Achim Flammenkamp’s maintained database. The earlier contribution packaged that coordinate certificate and supplied a baseline verifier.

The present transaction’s distinct contribution is the local rigidity analysis: verification of quarter-turn symmetry, enumeration of the eight specified embeddings, saturation, one-removal robustness, exhaustive two-removal accounting, and the resulting symmetric-difference constraint. The authorship disclosure states that the analysis, code, and text were produced by an AI research agent at Robert Raynor’s request. These attributions are consistent within the supplied evidence.
