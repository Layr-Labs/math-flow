## `no-three-in-line-77/record-152-local-rigidity`

**Verdict: INDETERMINATE**

**Declared references:** none.  
**Required dependencies from declared references:** none.

### Evidence sufficiency

The claim is fundamentally computational, but two necessary pieces of evidence are absent:

1. The bytes of `../record-152-certificate/configuration.txt` are not supplied. Consequently, the 152-point set \(C\) cannot be decoded or independently inspected from this packet. The SHA-256 value in `results.json` does not reveal or mathematically certify those missing bytes.
2. `objectiveAttestation` is null. Thus there is no trusted evidence that
   ```bash
   python3 rigidity.py
   ```
   was executed against the claimed configuration and committed `results.json`, or that it exited successfully.

The prior transaction mentioned in the README is not a declared reference and its evidence is not supplied. It therefore cannot fill this gap. In any event, the prior mathematical verification would not be logically necessary if the raw configuration were supplied, because `rigidity.py` rechecks it; the missing raw file is an input-evidence defect rather than a required mathematical dependency on that transaction.

### Static audit of the checker

Conditional on execution against the intended bytes, the checker substantially matches the declared predicates:

- `decode` requires exactly 152 encoded points, two in each row.
- `assert_no_three_in_line` checks distinctness, grid membership, and all
  \(\binom{152}{3}=573{,}800\) triples using the exact determinant.
- All eight dihedral maps of \(G_{76}\) and all four allowed translations are enumerated and deduplicated. The program requires exactly two distinct dihedral images and eight distinct translated embeddings.
- For each outside cell, sign-normalized primitive directions correctly group configuration points lying on the same undirected line through that cell.
- Distinct heavy lines through an outside cell have disjoint configuration-point sets. Hence freeing a cell with at most two removals is exhaustively covered by:
  - one heavy line of size 2;
  - one heavy line of size 3;
  - two heavy lines of size 2.
- The pair-walk/hitting-set implementation correctly enumerates hitting sets of size at most two and cross-checks the census.
- Because the checker also requires that there are no singleton freeings, every two-point removal that frees a cell is represented among the enumerated minimal pair freeings.
- It rejects any removal pair freeing more than one cell and requires 16 freeing pairs per embedding.
- Successful byte comparison with the supplied `results.json` would additionally bind the reported minimum of two blocking pairs per outside cell and the explicit four-cells/four-pairs-per-cell lists.
- The corollary is logically correct: for \(R=E\setminus S\) and \(A=S\setminus E\), every \(a\in A\) must be unblocked by \(E\setminus R\). The computed bounds would imply \(|A|\le1\) for \(|R|\le2\), and therefore \(|S|\le152\). If \(|S|\ge153\), then \(|R|\ge3\), \(|A|=|S|-152+|R|\ge4\), and \(|R|+|A|\ge7\).

The arithmetic \(77^2-152=5777\) is also correct.

### Unresolved obligations

Despite the sound conditional encoding, the supplied record does not affirmatively establish:

- the actual coordinates or no-three-in-line property of \(C\);
- quarter-turn symmetry and exactly two dihedral images;
- exactly eight distinct embeddings;
- saturation of all 5777 outside cells for every embedding;
- the one- and two-removal enumeration;
- agreement between computed output and `results.json`.

`results.json` is an asserted output, not a self-verifying certificate containing enough information to check all 5777-cell computations without the missing configuration and execution evidence.

Accordingly, there is no decisive mathematical counterexample in the supplied material, but the exact claim cannot be accepted from the available evidence.
