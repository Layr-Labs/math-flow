## `bssc-sum-capacity/two-letter-marton-four-run-execution-attestation`

**Verdict: Indeterminate**

### What the supplied terminal attestation establishes

The pinned subject attestation successfully executed the standard-library `verify.py` checker. That checker affirmatively establishes, for the frozen artifact it inspected:

- exactly four manifest/run records with case identifiers
  `w4-product`, `w4-interior`, `w8-product`, and `w8-interior`;
- recorded shapes \(4\times6\times6\times4\) and \(8\times6\times6\times4\), with seed indices \(0\) and \(12\);
- metadata stating 30,000 requested and executed iterations per record;
- complete candidate arrays of respectively 576 or 1152 binary64 entries;
- nonnegative finite entries and simplex residuals within the verifier’s stated tolerance;
- hash consistency among the manifest, candidate files, run records, combined JSONL, runner source, and three-event transcript files;
- transcript contents having the sequence `START`, `RESULT`, `END`;
- stored best-iteration fields lying between 1 and 30,000;
- independent standard-library evaluations of the smooth half-weight objective from the candidate arrays.

The independent recomputed binary64 values reported by the terminal attestation are

\[
\begin{aligned}
&0.7232857688438705,\\
&0.7135420139310601,\\
&0.7232857688438556,\\
&0.7191672502956984.
\end{aligned}
\]

These differ slightly from the four stored primary values in the claim,

\[
0.7232857688438716,\quad
0.7135420139310595,\quad
0.7232857688438569,\quad
0.719167250295698,
\]

but the discrepancies are within the verifier’s \(2\times10^{-14}\)-nat implementation-agreement tolerance. Thus the listed decimals are supported as the **stored primary binary64 values**, not as exact outputs of the independent recomputation.

All stored and independently recomputed binary64 values are numerically below

\[
0.7232857688439092313268831563011740144159620214477211104074274596056014.
\]

The declared-reference attestation for transaction `88a1004f309460f3ec1cacdae88d30f88559f9bc` ran its directed interval checker and supports that decimal as a strict lower bound for \(2L_{\rm RTD}\). Its interval construction uses exact rational square comparisons and outward-rounded decimal interval operations. This is adequate for the threshold role used here.

### Material unresolved execution-provenance obligation

The terminally attested subject command was only the frozen-artifact checker `verify.py`. It did **not**:

- invoke `run_case.py`;
- import or execute NumPy;
- replay any Adam optimization;
- verify 30,000 optimizer updates by observing their execution; or
- independently derive that the persisted candidate was the best candidate encountered during such an execution.

The `START/RESULT/END` files and the `iterationsExecuted` and `bestIteration` fields are pre-existing data consumed by the checker. Hashing and cross-checking them proves their integrity and internal consistency, but not that the four underlying optimizer executions actually occurred as reported. Likewise, the runner source shows what would happen **if invoked**, but the pinned attestation does not establish that this source produced the records.

Consequently, the supplied evidence does not affirmatively establish the claim’s historical assertions that:

- four searches were “freshly replayed”;
- each actually performed 30,000 Adam steps;
- the persisted arrays were genuinely the best-encountered iterates; or
- exactly those four fresh executions, and no additional relevant executions, occurred.

This is an evidentiary gap rather than a demonstrated counterexample, so the proper verdict is **indeterminate**, not invalid.

### Numerical and mathematical scope

The artifact does support only binary64 negative evidence. In particular:

- the objective calculations are not directed interval enclosures;
- some arrays have a nonzero exact simplex residual as binary64 arrays, so they are not certified exact real probability laws without normalization;
- the close product-run comparisons therefore do not prove that the exact mathematical objective of a normalized law is below \(2L_{\rm RTD}\);
- no local/global optimality, KKT, additivity, unrestricted Marton, or capacity conclusion follows.

These limitations are expressly disavowed by the claim and hence are not additional contradictions.

### Required dependency

- **Required:** `88a1004f309460f3ec1cacdae88d30f88559f9bc`, solely to certify that the comparison decimal is a directed lower endpoint for \(2L_{\rm RTD}\).
- No other mathematical dependency is required for the artifact-integrity or binary64 recomputation portions.
