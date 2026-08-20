## `no-three-in-line-77/record-152-local-rigidity`

**Verdict: INDETERMINATE**

**Required declared dependencies:** None. No reference transactions were declared. The prior `record-152-certificate` contribution is mentioned as provenance and as the location of an input file, but its evidence is not available in this packet and cannot be imported as a premise.

### Static mathematical and code audit

The proposed verification method is logically appropriate, conditional on the checker actually running successfully against the claimed configuration:

1. **Configuration validation**
   - `assert_no_three_in_line` checks that there are exactly 152 distinct in-grid points and exhaustively tests all
     \[
     \binom{152}{3}=573{,}800
     \]
     triples using the exact determinant.
   - The count \(77^2-152=5929-152=5777\) is correct.

2. **Blocking census**
   - For an outside cell \(c\), sign-normalized primitive vectors \(p-c\) correctly group configuration points by undirected lines through \(c\).
   - A group of \(m\) points contributes exactly \(\binom m2\) blocking pairs.
   - Distinct such groups are disjoint because two distinct lines through \(c\) intersect only at \(c\), which is outside the configuration.

3. **Removal-depth analysis**
   - A heavy line containing \(m\) configuration points requires at least \(m-1\) removals to cease blocking \(c\).
   - With at most two removals, the only possible freeing patterns are:
     - one line of size 2;
     - one line of size 3;
     - two lines of size 2.
   - Thus `minimal_freeing_sets` gives an exhaustive census for the claimed removal depths.
   - Because the claimed successful computation has no singleton freeings, every pair that frees a cell is minimal; the otherwise nonminimal-pair behavior possible in `hitting_sets_from_pairs` when a singleton hitting set exists cannot affect this claimed run.

4. **Cross-check**
   - `walk_pair_table` walks every full lattice line through every configuration pair in primitive steps. Rectangular convexity ensures a walked ray cannot leave and later re-enter \(G_{77}\).
   - Equality of its key set with all outside cells verifies saturation, while per-cell pair-count and hitting-set comparisons cross-check the census.
   - The shared `primitive` routine is correct on all calls here; its zero-vector case cannot occur because outside cells differ from all configuration points and configuration pairs are distinct.

5. **Claimed consequences**
   - Saturation implies maximality: any proper superset contains an outside cell already collinear with two points of \(E\).
   - The corollary is valid conditional on the removal claims. Writing
     \[
     S=(E\setminus R)\cup A,
     \]
     every \(a\in A\) must be unblocked by \(E\setminus R\). Hence for \(|R|=0,1\), \(A=\varnothing\), and for \(|R|=2\), \(|A|\le1\). Therefore \(|S|\le152\).
   - If \(|S|\ge153\), this forces \(|R|\ge3\), and
     \[
     |A|=|S|-152+|R|\ge4,
     \]
     so \(|E\triangle S|=|R|+|A|\ge7\).
   - The weaker “two simultaneous additions are impossible” conclusion also follows: if \(E\cup\{a,b\}\) were no-three-in-line, then \(E\cup\{a\}\) would be as well.

### Material unresolved evidence obligations

The exhaustive numerical claims are not affirmatively established by the supplied record:

- The referenced input file  
  `../record-152-certificate/configuration.txt`  
  is not supplied. Consequently, the packet does not permit verification of:
  - its claimed SHA-256;
  - the decoded 152 coordinates;
  - their no-three-in-line property;
  - quarter-turn symmetry;
  - the two-element dihedral orbit;
  - the eight distinct translated embeddings.

- There is **no terminal objective attestation** showing that the pinned checker was executed, exited successfully, and byte-matched the supplied `results.json`.

- `results.json` is an asserted output, not an independently checkable certificate of exhaustiveness. Its listed 16 pairs and four cells can be inspected for internal form, but without the full configuration and a verified execution they do not establish that no omitted cell or removal pair exists.

- Several conclusion fields in `results.json` are written as fixed values by `build_results`; they become justified only because the preceding analyses would abort on relevant failures and the default run would byte-compare the generated output. No evidence of that run is present.

Thus the proof logic and verifier design survive static scrutiny, but the indispensable computational execution and its exact input are missing. The exact declared claim therefore cannot be marked valid from this packet.
