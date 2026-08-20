## `no-three-in-line-77/rct4-154-exact-subclass-encoding`

**Verdict: INDETERMINATE**

### Source-level obligations that are verified

1. **Partition of the permitted cells**
   - The two diagonals of \(G_{77}\) intersect only at \((38,38)\), so the number of cells off both diagonals is
     \[
     77^2-(77+77-1)=5929-153=5776.
     \]
   - For \(\rho(x,y)=(y,76-x)\),
     \[
     \rho^2(x,y)=(76-x,76-y),\qquad \rho^4=\mathrm{id}.
     \]
   - A cell off both diagonals cannot have a \(\rho\)-orbit of size one or two: the only fixed point of \(\rho\) or \(\rho^2\) is the center, which lies on both diagonals. Also, \(\rho\) maps off-both-diagonals cells to off-both-diagonals cells. Thus these 5,776 cells partition into
     \[
     5776/4=1444
     \]
     four-cell orbits.
   - The anti-diagonal restriction excludes the center. The other 76 main-diagonal cells partition under \(\rho^2\) into
     \[
     76/2=38
     \]
     antipodal pairs. The implementation indexes precisely these pairs by \(i=0,\ldots,37\).

2. **Cardinality and assignment correspondence**
   - Choosing 38 distinct four-cell orbits and one diagonal pair gives disjoint cells totaling
     \[
     38\cdot4+2=154.
     \]
   - Conversely, every 154-point member of the stated subclass must contain the prescribed two diagonal points and therefore \(152/4=38\) complete off-diagonal orbits.
   - Because the orbit and diagonal-pair partitions are disjoint, this correspondence with Boolean selections is unique.

3. **Completeness of line enumeration**
   - Every lattice line has a sign-normalized primitive direction with either direction \((0,1)\), \((1,0)\), or \(dx>0\) and \(\gcd(dx,|dy|)=1\).
   - If a maximal grid line contains at least three lattice cells, two primitive steps fit within each coordinate range of length 76. Hence
     \[
     |dx|,|dy|\le 38,
     \]
     exactly matching the implementation’s direction bounds.
   - Requiring the predecessor to lie outside the grid selects exactly one initial cell for each maximal line, including directions with negative \(dy\). Thus no relevant maximal line is omitted or multiply enumerated before constraint deduplication.

4. **Correctness of weighted line inequalities**
   - For a line \(L\), the coefficient of a variable is exactly the number of cells represented by that variable which lie on \(L\).
   - For a Boolean assignment, the weighted sum therefore equals the number of selected expanded cells on \(L\). Anti-diagonal cells correctly contribute zero because they are fixed empty.
   - Omitting a line whose total possible coefficient sum is below three is safe: such a line cannot contain three selected cells under any assignment.
   - Every collinear triple of grid points lies on an enumerated maximal primitive lattice line. Consequently the expansion is no-three-in-line exactly when every retained weighted inequality has value at most two.
   - Deduplicating identical weighted left-hand sides is safe because all inequalities have the same right-hand side \(2\).

No source-level defect was found in these structural or logical parts of the encoding.

### Unresolved exact computational obligation

The exact declared statement also asserts:

- precisely **388,148** deduplicated constraints; and
- the exact SHA-256 digest  
  `5c0051739717f52f8eddd00cd01e8a83030849b3fd7b4516b0d308882c9aaf62`.

The supplied Python program deterministically defines the relevant enumeration and serialization, and its ordering appears deterministic: orbit indices arise from fixed nested loops, all set-derived collections are sorted before serialization, and the JSON encoding is explicitly specified. However, neither the complete serialized constraint list nor an independently verified execution trace is supplied. `results.json` repeats the asserted count and digest; it does not by itself establish that evaluating the generator actually produces them.

An exact replay such as

```bash
python3 verify_rct4_instance.py results
```

with confirmed successful completion would discharge this finite computational obligation. Without that recomputation, the exact count and digest remain unaffirmed. Because they are material parts of the declared claim, the whole claim cannot be marked valid, although no evidence makes it invalid.
