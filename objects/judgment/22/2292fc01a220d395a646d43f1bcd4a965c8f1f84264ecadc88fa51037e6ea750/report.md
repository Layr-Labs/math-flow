## `no-three-in-line-77/record-152-local-rigidity`

**Verdict: indeterminate**

### Material missing premise

The exact configuration defining \(C\) is not included in the supplied evidence. The checker reads

```text
../record-152-certificate/configuration.txt
```

but that artifact is absent, and the dependency packet declares no dependency transaction. The prose reference to transaction `dfc0cc40...` does not constitute an explicitly declared or supplied premise.

Neither the SHA-256 value nor `pointsDigest` recovers the 152 coordinates. Moreover, `results.json` contains only aggregate results and the exceptional removal pairs, not enough information to reconstruct \(C\) or independently verify all 5777 outside cells.

Consequently, the supplied checker cannot be reproduced from the evidence packet, and the following indispensable facts remain unverified:

- that decoding the referenced file yields exactly the intended 152 points;
- that those points are distinct, lie in \(G_{76}\), and have no collinear triple;
- that the configuration has exactly two dihedral images and eight translated embeddings;
- that the exhaustive per-cell computation actually produces the committed `results.json`.

This is an evidentiary gap rather than a demonstrated counterexample, so the proper verdict is **indeterminate**, not invalid.

### Static audit of the checker

Conditional on supplying the exact missing configuration file and obtaining a successful default execution of `rigidity.py`, the checker’s mathematical logic appears sound:

1. **Base and embedding validation**
   - `decode` produces two points in each of 76 rows.
   - `assert_no_three_in_line` checks cardinality, distinctness, grid bounds, and all
     \[
     \binom{152}{3}=573{,}800
     \]
     triples using an exact determinant.
   - All eight dihedral transformations and all four offsets in \(\{0,1\}^2\) are enumerated and deduplicated.
   - The main routine requires exactly two distinct dihedral images and eight distinct embedded sets.

2. **Saturation census**
   - For an outside cell \(c\), sign-normalized primitive directions correctly partition configuration points by geometric lines through \(c\).
   - A group of size at least two is precisely a blocking line, and
     \[
     \binom{k}{2}
     \]
     counts its blocking pairs.
   - Every outside cell is enumerated. A zero blocking count causes failure.
   - The committed report’s minimum count of two would establish the stronger “at least two distinct blocking pairs” assertion if recomputed and byte-matched.

3. **Removal enumeration**
   - Distinct lines through an outside cell have disjoint sets of configuration points because their only intersection is the outside cell.
   - A heavy line containing \(k\) configuration points requires at least \(k-1\) removals to cease blocking.
   - Thus the only minimal freeing patterns using at most two removals are exactly:
     - one line of two;
     - one line of three;
     - two lines of two.
   - The implementation enumerates these cases correctly. Since the accepted computation also requires no singleton freeing, no nonminimal two-point freeing is omitted through the treatment of the one-line-of-two case.

4. **Cross-check**
   - `walk_pair_table` walks the full lattice line of every configuration pair using primitive integer steps.
   - Convexity of the square grid ensures that stopping after leaving the grid cannot miss a later re-entry.
   - `hitting_sets_from_pairs` exhaustively finds all hitting sets of size at most two: every two-element hitting set must contain an endpoint of the first blocking pair, after which the second point must lie in the intersection of all remaining pairs.
   - The walked cell set, per-cell pair counts, and freeing sets are all required to equal the census results.

5. **Positive-result simulation and output binding**
   - Every reported freeing is directly rechecked against all pairs of the remaining 150 points.
   - A removal pair freeing more than one cell causes failure.
   - The main routine requires exactly 16 freeing pairs per embedding.
   - The generated complete report must byte-match `results.json`; the displayed lists then show four freed cells with four removal pairs each.

All arithmetic uses Python integers, so there is no floating-point or overflow issue.

### Corollary audit

The corollary follows correctly from claims 1–3, conditional on those computational claims.

Let
\[
R=E\setminus S,\qquad A=S\setminus E.
\]
Every \(a\in A\) must be unblocked by \(E\setminus R\), since two retained points of \(E\) collinear with \(a\) would form a forbidden triple in \(S\).

- If \(|R|=0\), saturation gives no possible \(a\).
- If \(|R|=1\), one-robust saturation gives no possible \(a\).
- If \(|R|=2\), the two-removal claim gives at most one possible outside cell.

Hence \(|A|\le 1\) whenever \(|R|\le2\), and
\[
|S|=152-|R|+|A|\le152.
\]
Therefore \(|S|\ge153\) implies \(|R|\ge3\), and then
\[
|A|=|S|-152+|R|\ge153-152+3=4.
\]
Thus \(|E\triangle S|=|R|+|A|\ge7\). There is no logical defect in this deduction.

### Conclusion

The code provides a plausible and statically sound exact verifier, and the corollary is valid conditional on its computed premises. However, the undeclared and unsupplied configuration file is essential input. Without it, the exact claim cannot be affirmatively verified from the permitted evidence, so acceptance is withheld.
