## `no-three-in-line-77/record-152-eight-embedding-rigidity-attested`

**Verdict: VALID**

### Certificate and base configuration

The governed subject attestation executed the supplied `rigidity.py` with no arguments under the pinned Python verifier and exited successfully. Static inspection shows that this invocation necessarily:

- reads the local `configuration.txt`;
- computes its SHA-256 digest;
- decodes one ignored marker followed by exactly \(2\cdot 76\) coordinate characters;
- requires exactly 152 distinct points, all in \(G_{76}\);
- checks all
  \[
  \binom{152}{3}=573800
  \]
  unordered triples using the exact integer determinant; and
- compares the complete recomputed output byte-for-byte with the supplied `results.json`.

The committed result records the digest

\[
\texttt{a23f1f55d9a914cff49fb6ba369b9f392f7af4c5ce08085267b3af1e7d7742c4}.
\]

A digest mismatch, duplicate point, out-of-range point, or collinear triple would have caused a nonzero exit. Thus the digest and 152-point no-three-in-line assertions are established.

### Symmetry and eight embeddings

The program explicitly applies all eight correct dihedral transformations of \(G_{76}\). It verifies:

- equality of the base set with its \(90^\circ\) rotation;
- exactly two distinct sets among the eight dihedral images;
- all four translations by \((0,0),(0,1),(1,0),(1,1)\);
- exactly eight distinct resulting point sets; and
- that every resulting set consists of 152 no-three-in-line points in \(G_{77}\).

These are precisely the eight ambient-square embeddings described in the claim.

### Blocking census

For each embedding \(E\), the program enumerates every one of the

\[
77^2-152=5777
\]

outside cells. For an outside cell \(c\), it groups points of \(E\) by sign-normalized primitive direction from \(c\). Two points lie in the same group exactly when they and \(c\) are collinear, so summing \(\binom{k}{2}\) over groups of size \(k\ge2\) gives the exact number of distinct blocking pairs.

The computed minimum is 2 for every embedding. This value is included in the byte-for-byte checked `results.json`, so the successful execution establishes that every outside cell is blocked by at least two distinct unordered pairs.

The separate pair-line walk enumerates every unordered pair of \(E\), walks its complete primitive lattice line in both directions, and requires its per-cell pair lists and counts to agree with the direction census. The line-walk implementation covers both signs and excludes the two defining selected points; the prior no-three-in-line check rules out an unhandled third selected point on such a line.

### One- and two-point removals

For each outside cell, freeing it after removals is exactly a vertex-cover problem on its blocking pairs. Distinct lines through an outside cell have disjoint selected-point sets, so the census correctly enumerates all minimal freeing sets of size at most two:

- one heavy line of two points gives singleton removals;
- one heavy line of three gives two-point removals;
- two heavy lines of two give one removal from each line;
- all other patterns require more than two removals.

In this application, the no-three-in-line property additionally prevents heavy lines of size at least three.

The explicit pair-table routine independently reconstructs all singleton and two-point hitting sets and requires exact agreement with the census. The successful run establishes:

- no singleton removal frees an outside cell;
- every two-point removal frees at most one outside cell;
- exactly 16 distinct unordered removal pairs per embedding free a cell; and
- each reported freeing is additionally confirmed by direct determinant testing against every remaining selected pair.

Because no singleton freeing exists, every freeing caused by a two-point removal is minimal and therefore is included in the enumerated two-point table; there is no omitted “nonminimal” two-point case.

### Consequences for nearby no-three-in-line sets

Fix one of the eight embeddings and let

\[
R=E\setminus S,\qquad A=S\setminus E.
\]

If \(S\) is no-three-in-line, every point of \(A\) must be unblocked by \(E\setminus R\); otherwise it forms a collinear triple with two points retained from \(E\).

When \(|R|\le2\), the verified removal census shows that at most one originally outside cell is unblocked. Hence

\[
|A|\le1
\]

and

\[
|S|=|E|-|R|+|A|=152-|R|+|A|\le152.
\]

Therefore, if \(|S|\ge153\), necessarily \(|R|\ge3\). Moreover,

\[
|A|=|S|-152+|R|\ge153-152+3=4,
\]

and consequently

\[
|E\triangle S|=|R|+|A|\ge3+4=7.
\]

All quantified conclusions in the claim follow.

### Attestation scope and dependencies

- The subject attestation establishes successful execution of the exact requested checker; the mathematical conclusion follows only after the code audit above, not from the success message alone.
- The declared-reference attestation independently verifies the same base certificate as 152 no-three-in-line points, but it does not establish the symmetry or rigidity census.
- Transaction `bf1301b6b472841276f79852c2e7fe0499309684` is **not a required dependency**: the subject contains the configuration and completely rechecks every mathematical fact needed for this claim. It remains a declared provenance/reference citation only.
- The result is correctly limited to the eight specified embeddings and proves no improved global bound for \(D(77)\).

**Required dependencies: none.**
