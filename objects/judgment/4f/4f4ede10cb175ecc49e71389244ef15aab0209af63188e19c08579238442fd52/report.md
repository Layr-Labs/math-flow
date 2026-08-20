## `no-three-in-line-77/rct4-154-exact-subclass-encoding`

**Verdict: indeterminate**

**Required dependencies:** none. No references were declared, and the construction is intended to be self-contained.

### Source-level structural audit

The mathematical structure encoded by the source is consistent with the stated subclass:

- For \(n=77\), the anti-diagonal has 77 cells. The main diagonal contributes 76 additional cells after excluding the center \((38,38)\), which lies on both diagonals.
- Thus there are
  \[
  77^2-77-76=5776
  \]
  cells off both diagonals.
- Every such cell has a four-element orbit under
  \(\rho(x,y)=(y,76-x)\), and these orbits remain off both diagonals. Hence there are
  \[
  5776/4=1444
  \]
  off-diagonal orbit variables.
- The 76 available main-diagonal cells form the 38 antipodal pairs
  \[
  \{(i,i),(76-i,76-i)\},\qquad 0\le i<38.
  \]
- Selecting 38 off-diagonal orbits and one diagonal pair therefore gives
  \[
  38\cdot4+2=154
  \]
  distinct points. Conversely, every 154-point member of the explicitly defined subclass has exactly this representation.

The implementation of `build_structure` agrees with these facts and checks that its variables partition all non-anti-diagonal cells.

### Line-constraint audit

The source-level soundness and completeness argument is substantially correct:

- `maximal_grid_lines` uses sign-normalized primitive directions.
- If a grid line contains at least three lattice cells, two primitive steps fit inside a coordinate span of 76, so each direction component has absolute value at most 38. The enumerated range is therefore sufficient.
- Requiring the predecessor to lie outside the grid identifies the unique first cell of each maximal line, so each such line is enumerated once.
- For each line, the coefficient of a Boolean variable is exactly the number of cells from that variable’s expansion lying on the line.
- Anti-diagonal cells are correctly omitted because they are fixed empty.
- Constraints with fewer than three potentially occupiable cells are tautological and may safely be omitted.
- Under Boolean assignments, the weighted sum is exactly the number of selected cells on that line. Thus the inequality \(\sum c_vy_v\le2\) is equivalent to that line containing at most two selected points.
- Every collinear triple of lattice points lies on one of the enumerated maximal primitive lattice lines.
- Deduplicating identical weighted inequalities preserves the feasible set.

The variable indexing and serialization also appear deterministic: orbit indices are assigned through deterministic grid traversal, and terms and constraints are explicitly sorted before JSON serialization.

### Unresolved computational obligations

The exact claim also asserts:

1. that the deduplicated construction contains exactly **388,148** constraints; and
2. that its canonical serialization has SHA-256 digest  
   `5c0051739717f52f8eddd00cd01e8a83030849b3fd7b4516b0d308882c9aaf62`.

These are finite computational outputs, not consequences established by the supplied prose alone. The packet contains:

- no terminal objective attestation;
- no complete serialized constraint list from which the count and digest could be independently checked; and
- only `results.json`, which repeats the asserted outputs.

Although `verify_rct4_instance.py results` is designed to recompute the instance and compare it byte-for-byte with `results.json`, no trusted execution of that command is supplied. The smaller calibration fixtures neither establish the \(n=77\) count nor the \(n=77\) digest, and they likewise have no terminal execution attestation here.

Accordingly, the source supports the conditional encoding theorem, but the exact numerical count and digest remain unverified. Because those are material parts of the declared statement, the full claim cannot be marked valid. No decisive contradiction has been found, so the appropriate verdict is **indeterminate**, not invalid.
