## `no-three-in-line-77/rct4-154-subclass-encoding-theorem`

**Verdict: valid**

**Required dependencies:** none.  
**Objective attestations:** none supplied or needed; the claim is an abstract encoding theorem and makes no implementation or solver-execution assertion.

### 1. Orbit and cell-partition audit

Let \(M=\{(i,i)\}\) be the main diagonal and \(A=\{(i,76-i)\}\) the anti-diagonal. The map

\[
\rho(x,y)=(y,76-x)
\]

is a bijection of \(G_{77}\), with

\[
\rho^2(x,y)=(76-x,76-y),\qquad \rho^4=\mathrm{id}.
\]

The only point fixed by \(\rho^2\), and hence the only orbit of size less than four, is \((38,38)\). Therefore every point off the two diagonals has a four-element orbit. Moreover, \(\rho\) interchanges \(M\) and \(A\), so an orbit starting off both diagonals remains off both diagonals.

The center lies in \(A\) and is fixed empty. The remaining 76 main-diagonal points decompose into the 38 disjoint pairs

\[
D_i=\{(i,i),(76-i,76-i)\},\qquad 0\le i<38.
\]

Thus \(G_{77}\setminus A\) is partitioned into the four-cell off-diagonal orbits and these 38 main-diagonal pairs. There is consequently no overlap or omitted selectable cell in the variable representation.

### 2. Subclass and cardinality constraints

A satisfying assignment selects exactly 38 four-cell orbit blocks and exactly one two-cell diagonal block. Its expansion therefore:

- contains no anti-diagonal point;
- is a union of complete four-cell \(\rho\)-orbits off both diagonals;
- has main-diagonal intersection equal to exactly one allowed antipodal pair; and
- has cardinality
  \[
  38\cdot4+1\cdot2=154.
  \]

Conversely, an rct4-subclass set already has exactly one diagonal pair. If it has 154 points and contains \(k\) selected four-cell orbits, then

\[
154=2+4k,
\]

so \(k=38\). Its Boolean values are forced by whether each disjoint block is occupied, proving uniqueness.

The README contains one overbroad sentence:

> “Conversely every Boolean assignment expands uniquely to an rct4-subclass set.”

Taken literally for unconstrained Boolean assignments, this is false: the all-zero assignment, for example, has no main-diagonal pair. This does not defeat the declared theorem, which concerns **satisfying assignments**, including the exactly-one diagonal-pair constraint. The constrained version needed for the theorem follows directly from the stated variable semantics and constraints.

### 3. Line-constraint audit

Because the variable blocks are disjoint and partition all non-fixed-empty cells, for every represented assignment and lattice line \(L\),

\[
|S\cap L|=\sum_v |L\cap O_v|\,y_v.
\]

This remains correct when one block meets \(L\) in multiple cells, because the coefficient is the exact intersection cardinality.

If three distinct selected grid points are collinear, their Euclidean line intersects \(G_{77}\) in the corresponding maximal lattice line containing at least those three cells. Its weighted sum is therefore at least three, violating the inequality.

Conversely, if a line inequality is violated, its integer-valued left side is at least three, so that line contains at least three distinct selected cells. Hence the expanded set has a collinear triple.

Lines containing fewer than three grid cells need no constraint because they cannot contain a forbidden triple.

### 4. Exact scope

The argument establishes a sound and complete bijection only between:

- satisfying assignments of the stated abstract Boolean system, and
- 154-point no-three-in-line members of the explicitly defined rct4 subclass.

It does **not** establish that the system is satisfiable or infeasible, and therefore does not determine or improve the global bounds on \(D(77)\). No implementation-specific count, digest, or broader symmetry assertion is supported or required.
