## `bssc-sum-capacity/two-letter-marton-exhaustive-transplant-certificate-repair`

**Verdict: valid**

### Finite family and enumeration

- The subject pins `source_certificate.json` by SHA-256 and byte length. The executed verifier checked both, selected exactly source rows 6 and 7, verified shape \((2,4,4,9)\), nonnegative integer numerators, denominator \(10^{12}\), and total mass \(1\).
- A deterministic map from nine labels to four super-inputs has \(4^9=262{,}144\) possibilities. Scanning two laws therefore gives exactly \(524{,}288\) law-map pairs.
- The projection-table optimization does not omit maps: the final loops range over every map ID \(0,\ldots,4^9-1\), while projections merely remove zero-mass labels from individual entropy tables.

### Channel and objective calculation

The displayed product-channel kernels are correct for the governed BSSC in super-symbol order \(00,01,10,11\).

Expanding the two endpoints gives

\[
E_Y=H(Y^2)+H(W,Z^2)-H(W,U,Y^2)-H(W,V,Z^2)+H(W,U,V),
\]

\[
E_Z=H(Z^2)+H(W,Y^2)-H(W,U,Y^2)-H(W,V,Z^2)+H(W,U,V),
\]

and hence the claimed identity for \(2L_{1/2}=E_Y+E_Z\). The verifier’s `RecordTables`, `objective_interval`, and `endpoint_intervals` implement exactly these entropy terms and coefficients.

Every probability entering an entropy is an integer multiple of \(1/(4\cdot10^{12})\). The verifier:

- represents these probabilities exactly as terminating decimals;
- encloses `Decimal.ln` results by adjacent representable values;
- uses directed multiplication and division;
- rounds each entropy contribution outward to the \(10^{-18}\)-bit grid; and
- uses upper bounds for positive terms and lower bounds for negatively signed terms when forming a global upper bound, with the choices reversed for a witness lower bound.

The interval orientations are therefore correct.

### Exhaustive upper bound and witness lower bound

The terminal subject attestation confirms successful execution of the supplied verifier and locks the following scaled intervals for \(2L_{1/2}\):

- row 6 global upper: `1090205773997791666`;
- row 7 global upper: `1090380802264441243`;
- row 7, map ID \(243761\), witness interval:
  \[
  [1090380802264441073,\;1090380802264441243].
  \]

Dividing the latter by \(2\cdot10^{18}\) yields

\[
0.5451904011322205365
\le L_{1/2}
\le 0.5451904011322206215.
\]

The witness map decodes under the stated base-four convention as

\[
(1,0,3,0,0,2,3,2,3),
\]

and its actual value supplies the lower bound on the family maximum. The exhaustive row-wise upper scans supply the upper bound. Thus the maximum over exactly the claimed finite family lies in the stated enclosure.

### Comparison with \(2L_{\rm RTD}\)

Transaction `88a1004f309460f3ec1cacdae88d30f88559f9bc` is a **required dependency only for this comparison**. Its RTD symmetrization, derivative analysis, boundary cases, and directed interval certificate establish

\[
2L_{\rm RTD}>
0.7232857688439092313268831563011740144159620214477211104074274596056014.
\]

The subject compares bounds for \(2L_{1/2}\) on the integer scale:

\[
1090380802264441243
<
1446571537687818462,
\]

where the right side is the floor of twice the certified lower bound for \(2L_{\rm RTD}\), scaled by \(10^{18}\). Consequently

\[
L_{1/2}<2L_{\rm RTD}
\]

for every scanned law-map pair. There is no normalization error: both sides concern two original channel uses.

The external hypotheses `(H-Marton)` and `(H-binary)` from that reference are not needed here, because the subject asserts neither achievability nor identification with the unrestricted one-letter Marton optimum.

### Dependencies and scope

- **Required dependency:** `88a1004f309460f3ec1cacdae88d30f88559f9bc`, solely for the rigorous directed RTD threshold.
- **Not a required dependency:** `1075dd02e8f83427a17b3f9f1391dfbb9e6d0a82`. The corrected scan is independently restated and re-executed in the subject; the earlier transaction is corrective/provenance material only.
- The supplied record pins the local source bytes but does not independently authenticate their external repository history. That is provenance, not a premise of the finite mathematical calculation.

The conclusion is correctly restricted to the two fixed rational laws and deterministic relabelings. It does not extend to stochastic maps, altered or mixed laws, auxiliary reoptimization, unrestricted Marton additivity, or broadcast-channel capacity.
