## Assessment: `no-three-in-line-77/rct4-154-subclass-encoding-theorem`

**Verdict: VALID**

The declared claim is a sound-and-complete encoding theorem for the explicitly restricted rct4 subclass. It does **not** establish that the encoding is satisfiable or improve the global bounds on \(D(77)\).

### 1. Orbit structure and cell partition

For
\[
\rho(x,y)=(y,76-x),
\]
one computes
\[
\rho^2(x,y)=(76-x,76-y),\qquad \rho^4=\mathrm{id}.
\]
The only point fixed by \(\rho\) or \(\rho^2\) is \((38,38)\). Therefore every point off both diagonals has a four-element \(\rho\)-orbit.

Let
\[
M=\{(i,i):0\le i\le 76\},\qquad
A=\{(i,76-i):0\le i\le 76\}.
\]
The map \(\rho\) interchanges \(M\) and \(A\), so their complement is \(\rho\)-invariant. Hence an orbit starting off both diagonals remains off both diagonals.

The diagonals meet only at \((38,38)\), which lies in the fixed-empty anti-diagonal. The remaining main-diagonal cells form the 38 disjoint pairs
\[
D_i=\{(i,i),(76-i,76-i)\},\qquad 0\le i<38.
\]
Thus the four-cell off-diagonal orbits together with the \(D_i\) form a disjoint partition of \(G_{77}\setminus A\). As a consistency check, the number of cells off both diagonals is
\[
77^2-(77+77-1)=5776=1444\cdot4.
\]

### 2. Cardinality and subclass conditions

A constrained assignment selects:

- exactly 38 disjoint four-cell orbits; and
- exactly one disjoint two-cell diagonal pair.

Its expansion therefore has
\[
38\cdot4+1\cdot2=154
\]
points. It automatically has empty anti-diagonal, is a union of complete four-cell orbits off both diagonals, and has exactly one antipodal pair on the main diagonal.

Conversely, if \(S\) is a 154-point member of the stated subclass, its main-diagonal contribution is exactly two points. If it contains \(k\) selected off-diagonal orbits, then
\[
154=2+4k,
\]
so \(k=38\). Because the represented cell sets are nonempty and pairwise disjoint, the variables selected by \(S\) are unique.

### 3. Exactness of the line inequalities

For an expanded assignment,
\[
S=\bigcup_{v:y_v=1}O_v.
\]
Since the \(O_v\) are disjoint and partition all potentially occupied cells,
\[
|S\cap L|
=\sum_v |L\cap O_v|\,y_v
\]
for every lattice line \(L\). Anti-diagonal cells require no additional term because they are fixed empty.

Therefore
\[
\sum_v |L\cap O_v|\,y_v\le 2
\]
holds exactly when \(L\) contains at most two selected points.

Every collinear triple of grid points lies on a unique Euclidean line, whose full intersection with \(G_{77}\) is a maximal lattice line containing at least three grid cells. Thus a collinear triple violates one of the imposed inequalities. Conversely, any violated inequality directly supplies at least three selected collinear cells. Lines containing fewer than three grid cells need no constraint.

This proves both soundness and completeness.

### 4. Minor wording issue in the proof

The sentence

> “Conversely every Boolean assignment expands uniquely to an rct4-subclass set”

is literally too broad if “every Boolean assignment” includes assignments not satisfying the two cardinality equations: for example, the all-zero assignment does not have exactly one main-diagonal pair. Read in the surrounding context as referring to assignments satisfying the encoding’s selection equations, it is correct. This overstatement is not material to the declared claim, which only concerns **satisfying assignments**, and both required directions are otherwise explicitly established.

### 5. Scope confirmation

No premise from another transaction is needed. The argument does not prove:

- existence or infeasibility of a satisfying assignment;
- anything about larger rotational or reflection-symmetric classes; or
- any improvement to \(152\le D(77)\le154\).

Within its expressly stated subclass and scope, the encoding theorem is correct.
