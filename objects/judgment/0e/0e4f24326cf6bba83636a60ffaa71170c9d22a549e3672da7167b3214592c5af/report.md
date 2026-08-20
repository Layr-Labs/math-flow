## Claim: `no-three-in-line-77/record-152-governed-replay`

**Verdict: VALID**

### Artifact and identity checks

- The supplied `configuration.txt` matches the corresponding artifact in transaction `dfc0cc40d41105292a119840dcdbe6f22860cf43` byte-for-byte.
- Its stated SHA-256 digest is  
  `a23f1f55d9a914cff49fb6ba369b9f392f7af4c5ce08085267b3af1e7d7742c4`.
- The supplied `verify.py` has the stated SHA-256 digest  
  `43463d0207199ef42ae0dc9c88c67f855fd92b070fb8d007f477a6b2de1998ec`.
- The formal claim does **not** assert that this checker is byte-for-byte identical to the checker in the canonical reference. This is important because the displayed reference checker has an additional trailing blank line. That discrepancy therefore does not contradict the declared claim.

### Verifier audit

The verifier’s successful path establishes all necessary certificate properties:

1. It removes one recognized symmetry marker and interprets the remaining payload in pairs.
2. The attested output reports a grid size of \(76\). Since the decoder creates two points per row, this yields exactly \(2\cdot76=152\) points.
3. Before examining triples, it rejects:
   - duplicate points, and
   - any coordinate outside \(\{0,\ldots,75\}^2\).
4. It then iterates over `itertools.combinations(points, 3)`. With 152 distinct points, this covers every unordered triple exactly once. The count is
   \[
   \binom{152}{3}
   =\frac{152\cdot151\cdot150}{6}
   =573{,}800.
   \]
5. For every triple it evaluates
   \[
   (x_2-x_1)(y_3-y_1)-(x_3-x_1)(y_2-y_1),
   \]
   using unbounded Python integer arithmetic. For three distinct planar points, this determinant is zero exactly when they are collinear.
6. Any zero determinant raises an exception before the success message. Thus the attested successful exit and success output, together with the audited source, imply that no checked triple was collinear.

### Objective attestation

The terminal attestation reports:

- status `passed`;
- exit code \(0\);
- no timeout; and
- exact stdout:
  `verified 152 points on a 76 x 76 grid; no collinear triple`.

The supplied `verification.json` selects the pinned Python verifier, names `verify.py` as the entrypoint, and supplies `configuration.txt` as its sole argument. It contains no participant-authored result field. Thus the request itself does not pre-assert success; success is supplied separately by the terminal attestation.

The attestation establishes successful execution of the pinned checker on the pinned subject inputs. It does not by itself prove the transaction-to-transaction byte-identity assertion or the displayed SHA-256 values; those are separate artifact checks above.

### Mathematical implication

The verified points lie in

\[
G_{76}=\{0,\ldots,75\}^2\subseteq \{0,\ldots,76\}^2=G_{77}.
\]

Embedding them unchanged therefore gives a 152-point no-three-in-line subset of \(G_{77}\), so

\[
D(77)\ge 152.
\]

This establishes only the existing lower bound. It does not establish a 153- or 154-point configuration, optimality, or the exact value of \(D(77)\).

### Dependency classification

- **Required mathematical dependencies:** none. The certificate, verifier, and successful replay independently establish \(D(77)\ge152\).
- Transaction `dfc0cc40d41105292a119840dcdbe6f22860cf43` is needed as comparison evidence for the literal byte-identity/provenance clause, but its mathematical claims are not needed as premises for the lower-bound proof.
