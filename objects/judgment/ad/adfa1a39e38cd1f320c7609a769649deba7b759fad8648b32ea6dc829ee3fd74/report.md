## `no-three-in-line-77/record-152-eight-embedding-rigidity-attested`

**Verdict: VALID**

### 1. Objective attestation and encoded predicate

The terminal attestation reports a successful, non-timeout execution with exit code \(0\) for the verifier request whose entrypoint is `rigidity.py` and whose argument list is empty. Thus the default local `configuration.txt` and `results.json` were used. The reported stdout and per-embedding stderr agree with the program’s success path.

The execution establishes that, on the pinned contribution bytes:

- `build_results` completed without any failed assertion;
- its recomputed JSON was byte-for-byte equal to the committed `results.json`;
- the quarter-turn, orbit-size, embedding-count, and 16-freeing-pairs assertions passed.

This is execution evidence for the program’s exact predicate, not by itself a proof of the mathematical interpretation. The source below correctly implements that interpretation.

### 2. Configuration digest and no-three-in-line property

The program reads the raw bytes of `configuration.txt`, computes their SHA-256 digest, places it in the recomputed result, and compares the entire rendering with `results.json`, whose required value is

\[
\texttt{a23f1f55d9a914cff49fb6ba369b9f392f7af4c5ce08085267b3af1e7d7742c4}.
\]

Successful attested execution therefore establishes the asserted digest.

The decoder removes one leading marker and requires exactly \(2\cdot76\) payload characters. It produces two points in each row \(y=0,\ldots,75\), hence 152 points. `assert_no_three_in_line` then verifies:

- exactly 152 points;
- pairwise distinctness;
- both coordinates in \(\{0,\ldots,75\}\);
- every one of the
  \[
  \binom{152}{3}=573800
  \]
  unordered triples has nonzero determinant.

The determinant formula is the standard exact collinearity criterion, and Python integer arithmetic introduces no numerical approximation. Thus \(C\subseteq G_{76}\) is a 152-point no-three-in-line set.

### 3. Symmetry, dihedral orbit, and embeddings

The eight transformations in `DIHEDRAL` are precisely the standard dihedral symmetries of \(G_{76}\). The program directly verifies that

\[
(x,y)\mapsto(75-y,x)
\]

fixes the decoded set, establishing quarter-turn invariance.

It explicitly applies all eight dihedral transformations, deduplicates the resulting point sets, and requires exactly two distinct images. For each image it applies all four translations in \(\{0,1\}^2\), deduplicates again, and requires exactly eight resulting sets. Every resulting set is also checked to consist of 152 distinct points in \(G_{77}\) and to have no collinear triple. This establishes the exact orbit and embedding statements.

### 4. Blocking census

For each embedding \(E\), the program enumerates all

\[
77^2-152=5777
\]

cells in \(G_{77}\setminus E\).

For an outside cell \(c\), configuration points are grouped by the sign-normalized primitive direction of \(p-c\). Two points have the same normalized direction exactly when they and \(c\) are collinear, including when they lie on opposite rays from \(c\). Therefore each group of size \(k\ge2\) contributes exactly \(\binom{k}{2}\) blocking pairs.

The computed minimum blocking count is 2 for every embedding, as recorded in `results.json`; equality of the recomputed and committed results was enforced by the attested run. Hence every outside cell is blocked by at least two distinct unordered pairs of \(E\).

The independent pair-walking table also exhaustively walks the complete primitive lattice line through every unordered pair of \(E\). The program requires:

- its key set to equal all outside cells;
- its pair count at every cell to equal the direction-census count;
- its size-\(\le2\) hitting sets to equal those found by the primary census.

The shared primitive-direction routine does not invalidate the primary argument, and the pair walk provides an additional exhaustive consistency check.

### 5. Removal claims

To free an outside cell, the removed points must hit every blocking pair for that cell. Distinct lines through an outside cell have disjoint sets of configuration points, since two distinct such lines meet only at that outside cell.

The program exhaustively enumerates every possible minimal hitting set of size at most two:

- one line containing two configuration points: singleton removals;
- one line containing three points: two-point removals;
- two lines each containing two points: one removal from each line.

All other line patterns require at least three removals. Moreover, because the configuration itself is no-three-in-line, heavy lines actually contain at most two points, but the implementation safely handles the size-three case as well.

The run establishes:

- no singleton removal frees any outside cell;
- every two-point removal frees at most one outside cell;
- exactly 16 distinct unordered removal pairs per embedding free a cell.

Unlisted removal pairs cannot free a cell: the program derives candidates exhaustively for every outside cell. Every reported freeing is additionally checked by direct determinant simulation against every pair remaining after deletion.

### 6. Consequence for nearby no-three-in-line sets

Fix one of the eight embeddings and let

\[
r=|E\setminus S|,\qquad a=|S\setminus E|.
\]

Every point of \(S\setminus E\) must be unblocked by \(E\cap S=E\setminus(E\setminus S)\); otherwise it would form a collinear triple inside \(S\).

Thus:

- if \(r=0\), no outside cell is available;
- if \(r=1\), no outside cell is available;
- if \(r=2\), at most one outside cell is available.

Therefore \(r\le2\) implies \(a\le1\), and

\[
|S|=152-r+a\le152.
\]

Consequently, if \(|S|\ge153\), then \(r\ge3\). Rearranging the same identity gives

\[
a=|S|-152+r\ge 1+r\ge4,
\]

and hence

\[
|E\triangle S|=r+a\ge3+4=7.
\]

These conclusions hold separately for every one of the eight embeddings. They do not imply a new global bound for \(D(77)\), consistent with the claim’s stated scope.

### Dependencies

The sole declared reference,

`bf1301b6b472841276f79852c2e7fe0499309684`,

is **not a required logical dependency**. It preserves provenance and independently corroborates the base configuration, but the present contribution includes the configuration bytes and rechecks the digest, decoding, bounds, distinctness, and all collinearity conditions itself.
