## `schur-number-6/fredricksen-sweet-537-radius-43-exclusion`

**Verdict: indeterminate**

### Combinatorial reduction

The proposed six-way case split is mathematically sound, conditional on the stated blocker counts and the four claimed unsatisfiability certificates.

For a fixed color \(c=C(537)\), the pairs
\[
\{x,537-x\},\qquad 1\le x\le268,
\]
are disjoint. If both endpoints have baseline color \(c\), validity of \(C\) forces at least one endpoint to change, since otherwise
\[
x+(537-x)=537
\]
would be monochromatic.

Thus, if the blocker counts really are
\[
(64,43,55,38,32,35),
\]
colors \(1\) and \(3\) force respectively at least \(64\) and \(55\) changes and therefore cannot occur when the distance is at most \(43\).

For each remaining color with \(b_c\) blocker pairs:

- every blocker pair contributes at least one change;
- a blocker pair whose two endpoints both change contributes exactly one additional change;
- every change outside all blocker-pair endpoints contributes one additional change.

Because the blocker pairs are disjoint, this gives the exact identity
\[
d(C,B)=b_c+
\#\{\text{blocker pairs with both endpoints changed}\}
+\#\{\text{changed nonblocker endpoints}\}.
\]
Consequently, distance at most \(43\) implies the listed extra-change limits \(0,5,11,8\) for colors \(2,4,5,6\).

### CNF encoding audit

The source code’s principal encoding steps are appropriate:

1. The at-least-one and pairwise at-most-one clauses enforce exactly one of six colors for every integer \(1,\dots,537\).
2. The loops enumerate every \(1\le x\le y\) with \(x+y\le537\).
3. For \(x=y\), reducing the repeated ternary clause to
   \[
   \neg X(x,c)\lor\neg X(2x,c)
   \]
   correctly forbids \(x+x=2x\).
4. The auxiliary variable for a blocker pair is encoded as true exactly when both endpoints have changed from their common baseline color.
5. The signed literals counted by the sequential counter therefore represent exactly the “extra changes” above the unavoidable \(b_c\).
6. The sequential-counter clauses implement an at-most-\(k\) constraint. The reported variable and clause dimensions are internally consistent with the construction.
7. No color-symmetry restriction is added, so the encoding does not accidentally discard candidates on account of their labels.

The static LRAT checker also implements a sound, restrictive ordered-RUP verification procedure: each added clause is checked by assuming its negation, replaying unit hints from extant earlier clauses, and requiring a conflict. Deriving the empty clause by such additions would establish unsatisfiability of the generated CNF.

### Material evidence failure

The four proof objects referenced by `cases.json` are not present in the supplied evidence:

- `case-color-2-extra-0.lrat.gz`
- `case-color-4-extra-5.lrat.gz`
- `case-color-5-extra-11.lrat.gz`
- `case-color-6-extra-8.lrat.gz`

Only their claimed filenames, hashes, and statistics are supplied. Those metadata assertions do not establish that the proofs exist, match the hashes, or pass the checker. No replay output or hosted verification attestation is included either.

Accordingly, the central obligations
\[
F_{2,0},\quad F_{4,5},\quad F_{5,11},\quad F_{6,8}
\quad\text{are unsatisfiable}
\]
remain unverified. Static inspection of the generator and checker can show what a successful replay would prove, but cannot substitute for the missing LRAT derivations.

The blocker counts and baseline validity are algorithmically checked by `verify.py`, but no executed replay is supplied. This is secondary to the missing proofs, which alone prevent acceptance.

### Color-permutation consequence

Conditional on the main distance theorem, the permutation statement is correct. For every permutation \(\pi\) of the six colors, \(\pi\circ C\) remains a valid coloring, so applying the theorem to each \(\pi\circ C\) gives
\[
\min_\pi d(\pi\circ C,B)\ge44.
\]

### Conclusion

The reduction, encoding, and checker appear logically suitable, and no decisive counterexample is established. However, the indispensable unsatisfiability certificates are absent from the supplied artifacts. The exact radius-43 exclusion therefore cannot be affirmatively verified and must be marked **indeterminate**, not valid.
