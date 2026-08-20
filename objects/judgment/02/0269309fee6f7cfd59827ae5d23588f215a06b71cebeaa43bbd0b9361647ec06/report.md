## `no-three-in-line-77/record-152-eight-embedding-local-rigidity`

**Verdict: valid**

### Dependency and base configuration

The declared dependency supplies the exact encoded configuration. The submitted checker independently decodes it and verifies:

- exactly \(152\) distinct points;
- all coordinates in \(G_{76}\);
- every one of the \(\binom{152}{3}=573800\) triples has nonzero integer determinant.

Thus the premise that \(C\) is a 152-point no-three-in-line subset of \(G_{76}\) is checked directly rather than merely assumed from provenance.

### Enumeration of the eight embeddings

The checker explicitly implements all eight dihedral transformations of \(G_{76}\), forms their images as point sets, and then applies all four translations in \(\{0,1\}^2\). It verifies:

- quarter-turn invariance of \(C\);
- exactly two distinct point sets in the dihedral orbit;
- exactly eight distinct translated point sets in \(G_{77}\);
- each resulting set still consists of 152 distinct in-bounds no-three-in-line points.

The committed report records the two image classes and four offsets for each. The computation deduplicates the actual point sets, so the count eight is not merely the nominal product \(2\cdot4\).

### Blocking and removal computation

For every one of the \(77^2-152=5777\) cells outside each embedding, the checker groups configuration points by their sign-normalized primitive direction from the cell. This exactly partitions points by lattice lines through that cell:

- two points lie in the same group exactly when they and the outside cell are collinear;
- each blocking unordered pair is counted exactly once;
- because \(E\) itself is no-three-in-line, no such line can contain three points of \(E\).

The generated report gives minimum blocking-pair count \(2\) for every embedding. Hence every outside cell is blocked by at least two distinct unordered pairs.

The removal analysis is exhaustive for deletion sets of size at most two. Distinct lines through an outside cell have disjoint sets of configuration points, so unblocking the cell requires reducing every heavy line to at most one remaining point. The checker enumerates precisely the possible hitting sets of size one or two. It finds:

- no singleton deletion frees any originally outside cell;
- each deletion pair frees at most one originally outside cell;
- exactly 16 deletion pairs per embedding free a cell;
- every reported case has two blocking lines containing two points each.

A two-lines-of-two cell has exactly \(2\cdot2=4\) freeing deletion pairs. Since no deletion pair frees two cells and there are 16 such pairs, these are exactly four cells with four pairs per cell. This agrees with every embedding record in `results.json`.

Exhaustiveness is additionally cross-checked by independently walking the full primitive lattice line of every unordered pair of configuration points. The resulting per-cell pair lists must agree with the direction census, and all singleton and two-point hitting sets are recomputed from those pair lists. Every reported freeing is then checked by direct determinant simulation after deletion. All arithmetic is exact Python integer arithmetic.

Although some summary fields in the report are literal values, the underlying predicates are enforced by failure conditions and by byte-for-byte comparison between the recomputed report and the committed `results.json`; the claim does not rely on those summary fields alone.

### Consequences for nearby no-three-in-line sets

Let
\[
R=E\setminus S,\qquad A=S\setminus E.
\]
Every \(a\in A\) must be unblocked by \(E\setminus R\), since otherwise \(a\) and a surviving blocking pair from \(E\) would form a collinear triple in \(S\).

Therefore:

- if \(|R|=0\), saturation gives \(A=\varnothing\);
- if \(|R|=1\), one-removal robustness gives \(A=\varnothing\);
- if \(|R|=2\), at most one outside cell is freed, so \(|A|\le1\).

Thus \(|R|\le2\) implies \(|A|\le1\), and
\[
|S|=152-|R|+|A|\le152.
\]

Consequently, if \(|S|\ge153\), then \(|R|\ge3\). Moreover,
\[
|A|=|S|-152+|R|\ge153-152+3=4,
\]
and hence
\[
|E\triangle S|=|R|+|A|\ge3+4=7.
\]

These deductions apply separately to each of the eight enumerated embeddings and do not imply any statement about other 152-point configurations or the global value of \(D(77)\), consistent with the declared scope.
