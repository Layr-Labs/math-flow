## `no-three-in-line-77/rct4-154-subclass-encoding-theorem`

**Verdict: Valid**

### Audit

1. **Orbit structure**
   - \(\rho^2(x,y)=(76-x,76-y)\) and \(\rho^4=\mathrm{id}\).
   - The only point fixed by \(\rho^2\), and hence the only possible orbit of size less than four, is \((38,38)\). This point lies on both diagonals.
   - The union of the main and anti-diagonals is invariant under \(\rho\), since \(\rho\) interchanges those diagonals. Therefore its complement is invariant, and every point off both diagonals belongs to a complete four-element \(\rho\)-orbit.

2. **Partition of available cells**
   - The center is excluded because the anti-diagonal is fixed empty.
   - The remaining 76 main-diagonal cells are partitioned into the 38 disjoint pairs
     \[
     D_i=\{(i,i),(76-i,76-i)\},\qquad 0\le i<38.
     \]
   - Together with the disjoint four-element orbits off both diagonals, these pairs partition \(G_{77}\setminus A\).
   - Consequently, each subclass set determines a unique Boolean assignment, and each assignment expands uniquely to a set in the defined subclass.

3. **Cardinality**
   - Selecting exactly 38 four-orbit variables and one diagonal-pair variable produces
     \[
     38\cdot4+1\cdot2=154
     \]
     distinct cells.
   - Conversely, a 154-point set in the subclass already contains exactly two diagonal cells; its remaining 152 cells are a disjoint union of four-cell orbits, so it selects exactly \(152/4=38\) such orbits.

4. **Line constraints**
   - Because the variable cell sets are disjoint and all omitted anti-diagonal cells are fixed empty,
     \[
     |S\cap L|=\sum_v |L\cap O_v|\,y_v
     \]
     holds exactly for every maximal lattice line \(L\).
   - Lines containing fewer than three grid cells cannot contain a collinear triple and need no constraint.
   - Any three collinear grid points lie on a unique Euclidean line whose full intersection with \(G_{77}\) is a maximal lattice line containing at least three grid cells. Thus a collinear triple violates the corresponding inequality.
   - Conversely, a violated inequality directly exhibits at least three selected cells on one line.

Hence the pseudo-Boolean system is sound and complete for exactly the 154-point no-three-in-line sets in the explicitly defined rct4 subclass. It does not establish existence, infeasibility, or any bound on \(D(77)\), consistently with the claim’s stated limitations.

### Dependencies

- **Declared references:** None.
- **Required dependencies:** None. The supplied subject independently establishes all needed facts.
- **Objective attestation:** None supplied or needed for this purely mathematical encoding theorem.
