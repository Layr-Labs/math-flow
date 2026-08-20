## `no-three-in-line-77/record-152-eight-embedding-local-rigidity`

**Verdict: INDETERMINATE**

### Required dependency

- `dfc0cc40d41105292a119840dcdbe6f22860cf43` — **required**, because it supplies the exact bytes encoding \(C\). The subject does not independently include those coordinates; its checker reads them from this dependency.
- The dependency’s provenance and separate `verify.py` are not additional logical premises. The subject checker independently rechecks bounds, distinctness, and all triples once supplied the configuration bytes.

### Audit of the mathematical reduction and checker

The checker’s encoding of the claimed finite predicate is, on static inspection, mathematically appropriate:

1. **Configuration decoding and no-three-in-line check**
   - It decodes exactly \(2\cdot76=152\) payload characters after the marker.
   - It checks 152 distinct points, coordinate bounds, and all
     \[
     \binom{152}{3}=573800
     \]
     determinants.
   - Thus a successful execution would establish that the decoded \(C\) is a 152-point no-three-in-line subset of \(G_{76}\).

2. **Eight embeddings**
   - The eight listed transformations are the complete dihedral group of the \(76\times76\) square.
   - The checker computes the distinct dihedral images rather than assuming the marker’s asserted symmetry.
   - It forms all four translations by \((0,0),(0,1),(1,0),(1,1)\), deduplicates the resulting sets, and requires exactly eight distinct embeddings.
   - It also requires exactly two distinct dihedral images and quarter-turn invariance. These checks correctly imply the claimed \(2\cdot4=8\) embeddings.

3. **Blocking census**
   - For an outside cell \(c\), sign-normalized primitive directions correctly partition configuration points according to the unoriented lines through \(c\).
   - A group of size at least two corresponds exactly to blocking pairs collinear with \(c\).
   - Since \(c\notin E\), distinct lines through \(c\) have disjoint sets of points of \(E\). Consequently, unblocking \(c\) requires reducing every such group to at most one remaining point.
   - The enumerated possibilities for a removal set of size at most two are complete: one line of two, one line of three, or two lines of two. In a successful execution the initial no-three-in-line test would in fact rule out a line of three.

4. **One- and two-removal accounting**
   - The checker rejects any singleton freeing.
   - It records all minimal two-point removal sets found by the census. Because singleton freeings are separately forbidden, this also covers all exact two-point removals that can free a cell; there is no omitted nonminimal pair containing a freeing singleton.
   - It rejects a removal pair that frees more than one outside cell and requires exactly 16 recorded removal pairs for every embedding.
   - Byte-for-byte comparison with the supplied `results.json`, if executed successfully, would additionally establish that those 16 records involve four cells, four pairs per cell, and that every record has the `two-lines-of-two` label.

5. **Cross-check**
   - Walking each pair’s full lattice line in primitive steps covers exactly all integer grid cells collinear with that pair.
   - The checker compares these explicit pair lists against the direction census and independently recomputes hitting sets of size at most two.
   - The hitting-set routine is complete: any two-element hitting set must contain an endpoint of the first blocking pair, after which the second element must lie in the intersection of all remaining pairs.
   - The two methods share the `primitive` routine, so the cross-check is not wholly implementation-independent, but the primitive-direction logic itself is correct. This is not a mathematical defect.
   - Every reported freeing is finally tested against all remaining pairs using the exact determinant.

6. **Consequences for a no-three-in-line set \(S\)**
   
   Let
   \[
   R=E\setminus S,\qquad A=S\setminus E.
   \]
   Every \(a\in A\) must be freed by deleting \(R\): otherwise two points of \(E\setminus R\subseteq S\) together with \(a\) would form a collinear triple in \(S\).

   Therefore, conditional on the computed removal facts:
   - if \(|R|=0\) or \(1\), then \(A=\varnothing\);
   - if \(|R|=2\), then \(|A|\le1\).

   Hence \(|R|\le2\) implies
   \[
   |S|=152-|R|+|A|\le152.
   \]
   If \(|S|\ge153\), contraposition gives \(|R|\ge3\), and then
   \[
   |A|=|S|-152+|R|\ge1+|R|\ge4,
   \]
   so
   \[
   |E\triangle S|=|R|+|A|\ge7.
   \]
   This logical deduction is valid and has the claimed local scope.

### Material unresolved obligation

No terminal objective attestation or other trusted execution transcript is supplied. The committed `results.json` is an asserted output, not an exhaustive certificate of the 5,777 per-embedding blocking computations: it omits the per-cell line censuses and therefore cannot by itself establish saturation or exhaustiveness. Likewise, neither the dependency verifier nor `rigidity.py` is attested as having run successfully on the supplied bytes.

Thus the source code appears to encode the correct finite verification, but the record does not affirmatively establish that its exhaustive computation actually produces the committed report for this exact configuration. That unresolved computational obligation prevents a **valid** verdict. No decisive mathematical error was found, so **invalid** is not warranted.
