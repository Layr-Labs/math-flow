## `no-three-in-line-77/record-152-eight-embedding-local-rigidity`

**Verdict: INDETERMINATE**

### Required dependency

- **Required:** `dfc0cc40d41105292a119840dcdbe6f22860cf43`
  - It supplies the exact `configuration.txt` bytes defining \(C\), which are not embedded directly in the subject checker.
  - The reference’s prose claims about \(D(77)\) and provenance are not required premises. The subject checker independently rechecks the needed cardinality, bounds, distinctness, and no-three-in-line property.

### Audit of the mathematical and algorithmic argument

The checker’s logic is structurally adequate, conditional on a successful execution against the supplied files:

1. **Base configuration**
   - `decode` requires exactly \(2\cdot 76=152\) payload characters and produces two points per row.
   - `assert_no_three_in_line` checks 152 distinct in-bounds points and all
     \(\binom{152}{3}=573800\) triples using exact integer determinants.

2. **Eight embeddings**
   - The eight displayed transformations are the dihedral symmetries of \(G_{76}\).
   - The program computes the distinct images rather than assuming their number, requires exactly two, translates each by the four vectors in \(\{0,1\}^2\), deduplicates, and requires exactly eight resulting sets.
   - Each resulting embedding is checked again for bounds, distinctness, and no collinear triple.

3. **Blocking census**
   - For an outside cell \(c\), sign-normalized primitive directions correctly group points lying on the same full line through \(c\), including points on opposite rays.
   - A group of size \(k\) contributes exactly \(\binom{k}{2}\) blocking pairs.
   - The generated report records minimum blocking count \(2\). Although `analyze_embedding` itself only fails when this count is zero, byte equality with `results.json`, if actually checked, would establish the stronger claimed minimum of two.

4. **Deletion analysis**
   - Distinct lines through an outside cell are disjoint on \(E\), since their only common point is that outside cell.
   - Consequently, the enumerated size-\(\le2\) hitting-set patterns are exhaustive:
     one line of two, one line of three, or two lines of two.
   - The program rejects every singleton freeing, maps every freeing pair to all cells it frees, and rejects a pair freeing more than one cell.
   - It independently reconstructs pair incidences by walking complete primitive lattice lines and compares the resulting hitting sets with the census.
   - The reported pair freeings are additionally checked by direct determinant simulation.
   - The committed JSON visibly contains 16 records for each embedding, grouped as four pairs on each of four cells, all labelled `two-lines-of-two`. A successful byte-for-byte comparison would bind these records to the exhaustive computation.

5. **Consequences for a no-three-in-line set \(S\)**
   - Put \(R=E\setminus S\) and \(A=S\setminus E\).
   - Every \(a\in A\) must be freed after deleting \(R\); otherwise \(a\) and a surviving blocking pair from \(E\setminus R\subseteq S\) would form a collinear triple.
   - Thus, if \(|R|\le2\), the deletion computation gives \(|A|\le1\), and
     \[
     |S|=152-|R|+|A|\le152.
     \]
   - Hence \(|S|\ge153\) implies \(|R|\ge3\), and
     \[
     |A|=|S|-152+|R|\ge4,\qquad
     |E\triangle S|=|R|+|A|\ge7.
     \]
   These deductions are correct and retain the claimed eight-embedding scope.

### Unresolved material obligation

The packet contains **no terminal objective attestation**. The README’s claimed command, expected output, and SHA-256 strings are authored assertions, not trusted execution evidence. Likewise, `results.json` is not a full per-cell certificate and by itself does not verify the exhaustive results for all 5,777 outside cells of each embedding.

Therefore the supplied record does not affirmatively establish that:

- `rigidity.py` was executed successfully on the exact supplied configuration and result bytes;
- all determinant and blocking-census loops completed without failure; or
- the recomputed report actually matched `results.json` byte for byte.

No decisive mathematical or source-code defect was found, but these exhaustive finite computations are essential to the claim and remain unevidenced by a pinned successful execution. Under the conservative rubric, the claim cannot be marked valid.
