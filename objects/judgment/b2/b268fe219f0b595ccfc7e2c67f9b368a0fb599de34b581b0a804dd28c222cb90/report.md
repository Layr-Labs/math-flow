## `bssc-sum-capacity/two-letter-marton-computational-nonfinding`

**Verdict: INDETERMINATE**

### What is affirmatively verified

1. **The encoded search architectures and nominal counts are consistent.**
   The supplied source code has the advertised loop structures:
   - \(2\cdot4^9=524{,}288\) transplant evaluations;
   - 48 \(W=U=V=4\) starts at 20,000 iterations;
   - 24 \(W=8,U=V=4\) starts at 30,000 iterations;
   - \(24+24=48\) transplant continuations;
   - \(3\cdot11=33\) homotopy runs;
   - \(15\cdot6=90\) fixed-input runs;
   - \(6(1+6+3+3)=78\) escape runs;
   - four face tests, each encoding 5,000 random samples and 12 local starts.

2. **The implemented half-weight objective is mathematically appropriate.**
   The entropy expression in `MartonHalf.value_grad` is the expansion of
   \[
   \frac12(E_Y+E_Z)
   \]
   for a joint law \(p(w,u,v,x^2)\), and the product BSSC transition matrices are constructed correctly. The conversion from internal nats to reported bits is also consistent.

3. **The frozen aggregate numbers satisfy the claimed tolerance.**
   Among the aggregate objective values actually examined by `verify.py`, the largest is the recorded product-seed value
   \[
   0.723285768843912,
   \]
   whose excess over the certified directed lower threshold is
   \[
   2.7686731168\ldots\times10^{-15}<10^{-12}.
   \]
   The recorded escape value and margin are mutually consistent to the verifier’s declared \(2\times10^{-16}\)-bit tolerance.

4. **The threshold reference is adequately supported.**
   Transaction `88a1004f309460f3ec1cacdae88d30f88559f9bc` supplies the necessary directed certificate
   \[
   0.7232857688439092313268831563011740144\ldots
   <2L_{\rm RTD}<
   0.7232857688439092313268831563011740145\ldots .
   \]
   Its terminal attestation executed the interval checker successfully. The checker uses an exact rational bracket for \(\sqrt{105}\), outward interval arithmetic, and expanded correctly rounded logarithms. This supports the comparison threshold used by the subject claim.

5. **The limitations are correctly stated.**
   Even if every recorded run is accepted, these finite searches do not establish Marton additivity, a global two-letter optimum, or a capacity converse.

### Material unresolved obligations

The subject terminal attestation ran only:

```text
python3 -I -B verify.py
```

That checker explicitly **does not rerun the NumPy discovery campaign**. It verifies internal consistency of `evidence.json`, source-file hashes, count arithmetic, and comparisons among aggregate values already written into the ledger. It does not establish that:

- any of the 369 local searches or 524,288 transplant evaluations were actually executed with the recorded programs;
- the reported campaign maxima are maxima over the claimed runs;
- every run’s objective was at most its reported campaign maximum;
- the specified Python 3.13.1/NumPy 2.4.3 environment produced the recorded outputs;
- the external source file with the asserted SHA-256 was present and was the file actually scanned;
- every escape candidate had full input support;
- the near-threshold outputs actually lie in the product-RTD basin rather than merely having similar objective values.

No complete run logs, per-run output ledger, saved candidate laws, or terminal attestations for the expensive discovery commands are supplied. For several campaigns, `evidence.json` contains only an asserted aggregate maximum. Consequently, the static verifier can confirm that the asserted maxima imply the \(10^{-12}\) non-finding, but it cannot confirm that those maxima faithfully summarize the claimed executions.

There is also a scope gap concerning the validation-only face campaign: the face program optimizes a minimum-endpoint inequality violation rather than recording the Marton half-weight of every tested law. Thus, if “these finite recorded computations” is read as including every face-test computation in the subsequent half-weight maximum assertion, that assertion is not checked by `verify.py`.

These are evidentiary gaps rather than demonstrated counterexamples, so **invalid** is not warranted; however, they prevent affirmative verification of the exact empirical claim.

### Dependency classification

- **Required dependency:** `88a1004f309460f3ec1cacdae88d30f88559f9bc`, for the certified directed \(2L_{\rm RTD}\) threshold.
- **Reference only:** `f6ea30479b9ca461294ba89a8a1a31c06ce59d08`. It supplies source/repository provenance and historical context but is not needed for the mathematical threshold or objective calculations. Its attestation also does not repair the missing execution evidence for the subject campaign.

**Conclusion:** The code, counts, objective, threshold, and frozen aggregate comparisons are internally consistent, but the supplied terminal evidence does not establish the claimed discovery executions or that the aggregate ledger exhaustively and accurately records them. Therefore the declared claim remains **indeterminate**.
