## `bssc-sum-capacity/two-letter-marton-exhaustive-transplant-certificate`

**Verdict: indeterminate**

Most of the finite-family certificate is rigorously supported, but the declared high-precision “independent 100-digit evaluation” is not certified by the supplied execution.

### Finite-law and objective audit

The verifier affirmatively checks that:

- the vendored source file has the pinned SHA-256 digest and byte length;
- exactly two records, indexed 6 and 7, are used;
- each record has shape \(2\times4\times4\times9\), nonnegative integer numerators, denominator \(10^{12}\), and total mass exactly one;
- every map is encoded by nine base-four digits, giving exactly
  \[
  4^9=262{,}144
  \]
  maps per law and \(524{,}288\) law-map pairs.

The product-channel matrices in the contribution agree with the two-use half-skew BSSC transitions.

The entropy identity is also correct. Expanding the two Marton endpoints gives
\[
E_Y=H(Y^2)+H(W,Z^2)-H(W,U,Y^2)-H(W,V,Z^2)+H(W,U,V),
\]
\[
E_Z=H(Z^2)+H(W,Y^2)-H(W,U,Y^2)-H(W,V,Z^2)+H(W,U,V),
\]
whose sum is exactly equation (3). The verifier constructs all required joint entropies slice-by-slice with the correct coefficient signs.

### Interval and exhaustivity audit

For every exact probability \(n/(4\cdot10^{12})\), the program encloses
\(-p\log_2p\) using correctly rounded `Decimal.ln`, adjacent representable values, and directed multiplication and division. It then rounds each entropy-cell enclosure outward to the \(10^{-18}\)-bit grid. The sign choices used in the objective are valid:

- upper endpoints for positive entropy terms;
- lower endpoints for negatively weighted entropy terms;
- the reverse choices for a candidate lower bound.

The projection-table optimization does not omit maps: the terminal loop still visits every map ID from \(0\) through \(4^9-1\) for each source law.

The pinned subject attestation establishes that this exact verifier completed successfully and reported:

\[
0.5451904011322205365
\le \max_{r,\phi}L_{1/2}(p_{r,\phi})
\le 0.5451904011322206215.
\]

The lower endpoint comes from row 7 and map
\[
(1,0,3,0,0,2,3,2,3),
\]
whose base-four ID is indeed
\[
1+3\cdot4^2+2\cdot4^5+3\cdot4^6+2\cdot4^7+3\cdot4^8
=243761.
\]

### RTD comparison and dependency

The strict comparison is supported. Transaction
`88a1004f309460f3ec1cacdae88d30f88559f9bc` proves, by its directed interval certificate,

\[
2L_{\rm RTD}>
0.7232857688439092313268831563011740144159620214477211104074274596056014.
\]

The subject verifier compares the upper bound for \(2L_{1/2}\) against twice this directed lower bound on the common integer scale. Since
\[
0.5451904011322206215<0.7232857688439092313\ldots,
\]
every law-map member in the stated finite family is strictly below \(2L_{\rm RTD}\).

**Required dependency:**  
`88a1004f309460f3ec1cacdae88d30f88559f9bc`, only for identifying and certifying the directed \(2L_{\rm RTD}\) threshold.

The external Huang–Liu–Liu provenance is not a mathematical dependency: the rational tables themselves are vendored and directly checked. Neither H-Marton nor H-binary is needed for this finite numerical comparison.

### Unresolved declared obligation

The claim additionally states:

> “an independent 100-digit evaluation begins  
> \(0.545190401132220579101772556649110872\).”

The verifier does **not** perform or certify such a high-precision evaluation. It hard-codes

```python
EXPECTED_LHALF = Decimal("0.545190401132220579101772...")
```

and checks only that this number lies inside the much wider enclosure

\[
[0.5451904011322205365,\;0.5451904011322206215].
\]

That enclosure fixes only the common leading digits through approximately
\(0.545190401132220\); it does not establish the subsequent digits
\(579101772556649110872\). No independent high-precision computation, sufficiently narrow interval, or terminal attestation for that decimal prefix is supplied.

Thus there is no demonstrated contradiction, so the claim is not invalid, but its exact conjunction cannot be marked valid. The finite-family maximum enclosure, exhaustive-map conclusion, RTD comparison, and stated scope limitations are otherwise supported.
