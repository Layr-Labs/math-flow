## `schur-number-6/fredricksen-sweet-537-radius-60-exclusion`

**Verdict: INDETERMINATE**

### Mathematical reduction

The proposed reduction from the Hamming-radius claim to six conditioned cases is sound.

For a fixed color \(c\) assigned to \(537\), a blocker pair is
\[
(x,537-x)
\]
whose two endpoints both have baseline color \(c\). Because \(537\) is odd, these pairs are disjoint. In any valid coloring with \(537\) colored \(c\), the Schur constraint
\[
x+(537-x)=537
\]
prevents both endpoints from retaining color \(c\). Thus every blocker pair contributes at least one old-coordinate change.

For a blocker pair with baseline-color variables \(b_x,b_y\), the auxiliary variable \(e\) is constrained by
\[
(\neg e\lor\neg b_x),\qquad
(\neg e\lor\neg b_y),\qquad
(b_x\lor b_y\lor e).
\]
These clauses indeed give
\[
e\iff(\neg b_x\land\neg b_y).
\]
Consequently, after the unavoidable one change per blocker pair, \(e\) counts exactly whether that pair contributes a second change. Outside the blocker endpoints, the literal \(-b_v\) counts exactly whether \(v\) changes from its baseline color. Therefore, for a valid coloring in the case where \(537\) has color \(c\),
\[
d_{\mathrm H}
=
b_c+\sum_{\text{blockers}}e
+\sum_{\text{nonblocker }v}[-b_v],
\]
where \(b_c\) is the blocker count. Bounding the final two sums by \(60-b_c\) is therefore equivalent to bounding the old-coordinate Hamming distance by \(60\).

The Sinz encoding used by `build_case_formula` is a sound and complete existential encoding of “at most \(60-b_c\)” for the counted signed literals. Its dimensions are internally consistent with `cases.json`. Writing \(m=536-b_c\) and \(k=60-b_c\), the variable count is
\[
3222+b_c+(m-1)k,
\]
and the clause count is
\[
441145+3b_c+m+2k(m-2),
\]
which reproduces all five recorded case dimensions.

The remaining CNF components are also correctly formed:

- exactly one of six colors is imposed for every integer \(1,\dots,537\);
- all equations \(x+y=z\) with \(x\le y\) and \(z\le537\) are covered;
- the \(x=y\) case correctly reduces to a binary prohibition;
- the computed triple totals \(71{,}824\) through \(536\) and \(72{,}092\) through \(537\) are correct;
- conditioning on the six possible labeled colors of \(537\) is exhaustive;
- no unjustified color-symmetry reduction is used.

If the reported color-1 blocker count \(64\) is correct, that case is excluded directly because its distance is at least \(64>60\). The five remaining colors are represented by the five CNFs.

### Certificate checker

The final checker’s ordered-RUP procedure is propositionally sound. It assumes the negation of a proposed clause, follows only unit or conflicting antecedent clauses, and accepts an addition only upon reaching conflict. Hence each accepted addition is implied by the current formula. Ending with a checked empty-clause addition would establish UNSAT.

The checker also regenerates the CNFs rather than trusting stored DIMACS files, checks the baseline and blocker counts, and directly replays the logical proofs. The normalization and trimming tools are not needed for the soundness of that final replay.

### Material missing evidence

The five indispensable proof payloads are not present in the supplied subject evidence:

- `case-color-2-extra-17.lrat.gz`
- `case-color-3-extra-5.lrat.gz`
- `case-color-4-extra-22.lrat.gz`
- `case-color-5-extra-28.lrat.gz`
- `case-color-6-extra-25.lrat.gz`

Only their claimed names, sizes, hashes, and proof statistics appear in `cases.json` and the README. Those metadata do not establish that the files exist with the stated contents or that any of the five generated CNFs is unsatisfiable. Likewise, `verification.json` requests a replay but is not a replay result, and the README’s statement that a replay occurred is an unsupported assertion within the contribution. No explicit dependency transaction supplies an independently verified replay or the omitted proof bytes.

Thus the crucial obligations
\[
F_c\text{ is UNSAT}\qquad(c=2,3,4,5,6)
\]
cannot be checked from the supplied evidence. The static verifier and semantically correct reduction do not by themselves prove these UNSAT assertions.

### Conclusion

No counterexample or semantic encoding defect is apparent, but the local exclusion claim depends essentially on five unavailable unsatisfiability certificates. Because those material proof obligations remain unresolved, the exact claim cannot be accepted as valid from this packet.
