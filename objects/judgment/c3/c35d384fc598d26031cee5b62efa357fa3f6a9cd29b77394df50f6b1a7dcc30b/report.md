## `no-three-in-line-77/rct4-154-exact-subclass-encoding`

**Verdict: Indeterminate**

**Required dependencies:** None. No reference transaction is mathematically required; the historical transaction mentioned in the README is provenance only and was not declared as a reference.

### Verified source-level obligations

The mathematical structure implemented by the supplied code is consistent with the stated subclass:

- \(G_{77}\) has \(77^2=5929\) cells.
- The two diagonals have \(77+77-1=153\) cells in their union, so there are
  \[
  5929-153=5776
  \]
  cells off both diagonals.
- On those cells the action of
  \[
  \rho(x,y)=(y,76-x)
  \]
  has no orbit of size less than four: a fixed point of \(\rho\) or \(\rho^2\) would be the center \((38,38)\), which lies on both diagonals and is excluded. Thus the off-diagonal cells form
  \[
  5776/4=1444
  \]
  four-cell orbits.
- Removing the center, the main diagonal has 76 cells, partitioned by \(\rho^2\) into 38 antipodal pairs.
- Selecting 38 off-diagonal orbits and one diagonal pair therefore gives
  \[
  38\cdot4+2=154
  \]
  distinct points, and every 154-point member of the defined subclass yields such a unique selection.

The line-constraint construction is also semantically sound:

- Primitive directions are sign-normalized correctly.
- Any grid line containing at least three lattice cells has primitive step components of absolute value at most \(38\), because two primitive steps must fit within coordinate span \(76\).
- Requiring the predecessor to lie outside the grid selects the unique first cell of each maximal line.
- The coefficient of a Boolean variable is exactly the number of cells from its orbit or diagonal pair lying on that line.
- Omitting lines with fewer than three non-anti-diagonal cells is harmless because the anti-diagonal is fixed empty.
- Consequently, for binary variables,
  \[
  \sum_v c_vy_v\le2
  \]
  is exactly the condition that the expanded set occupies at most two cells on that line.
- Every collinear triple is contained in one of these maximal primitive lattice lines, and deduplicating identical weighted inequalities preserves the feasible set.

No source-level counterexample to the claimed soundness and completeness within the explicitly restricted subclass was found.

### Unresolved material computational obligations

The exact claim also asserts that the generated system contains precisely **388,148** deduplicated constraints and that its canonical serialization has digest

`sha256:5c0051739717f52f8eddd00cd01e8a83030849b3fd7b4516b0d308882c9aaf62`.

Those facts are not affirmatively established by the supplied record:

- `results.json` merely states the claimed output.
- The complete generated serialization is not supplied for direct counting and hashing.
- No terminal objective attestation or other trusted execution of `verify_rct4_instance.py` is present.
- The calibration certificates concern smaller instances and do not establish the \(n=77\) constraint count or digest.
- Static inspection verifies how the program would calculate the count and digest, but does not verify the asserted numerical output of that computation.

Because the exact count and digest are material parts of the declared claim, the whole claim cannot be marked valid without trusted recomputation or equivalent complete evidence. There is no decisive contradiction establishing falsity, so the appropriate verdict is **indeterminate**, rather than invalid.
