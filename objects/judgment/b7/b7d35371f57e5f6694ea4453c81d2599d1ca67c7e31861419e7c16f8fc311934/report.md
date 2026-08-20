## `bssc-sum-capacity/fixed-pair-continuous-certificates-and-invariant-frontier`

**Verdict: indeterminate**

### 1. Capacity-converse premise is not established

The claimed capacity bound relies materially on the assertion that the six displayed inequalities, including the rate-free side condition, are valid consequences of the full Gohari–Liu–Nair Theorem 9 outer bound and that the theorem permits the fixed auxiliary-receiver pair \(G,K\) used here for every achievable rate pair.

That is an indispensable logical premise: the interval certificate only majorizes a weighted combination of those six rows. It does not independently prove that achievable BSSC rates satisfy them.

No reference transaction is declared for this claim. The packet merely bibliographically mentions the 2026 manuscript and asserts that the rows were copied from it; it does not supply the theorem, its proof, all side conditions, or evidence verifying the transcription and applicability. Under the dependency restrictions, that missing external theorem cannot be admitted as an established dependency. Consequently, the inference from the certified functional to \(C_{\rm sum}\) remains unresolved.

### 2. Conditional weak-duality argument

Conditional on the six rows being valid and correctly transcribed, the mathematical architecture is coherent:

- The nonnegative weights have the advertised rate coefficients; the exact `Fraction` audit is designed to check that both \(R_1\) and \(R_2\) receive coefficient one.
- The posterior identities
  \[
  I(W;A)=I_A(q_0)-\mathbb E I_A(q_W),\qquad
  I(U;A\mid W)=\mathbb E I_A(q_W)-\mathbb E I_A(q_U)
  \]
  and their \(V,UW,VW\) analogues are correct under the stated Markov hierarchy.
- Dropping all constraints except mass, common mean, and the martingale identities is a relaxation in the correct direction for an upper bound.
- If the asserted affine inequalities (D1) and (D2) hold continuously, conditional expectation and the martingale property yield the displayed \(B(q_0)\) bound without requiring strong duality.
- The exact coefficient cancellation would make
  \[
  B(q_0)=c'_1\bigl(I_Y(q_0)+I_Z(q_0)\bigr)+\text{constant}.
  \]
  Since \(c'_1\ge0\), this is concave and reflection-symmetric, so its maximum over \(q_0\in[0,1]\) is at \(q_0=1/2\).

Thus no decisive direction-of-relaxation or prior-maximization error was found, but this only establishes a conditional argument.

### 3. Continuous numerical certificate is not affirmatively executed in the packet

The final `verify.py` is structured as a fail-closed interval checker and contains:

- exact rational audits of the row weights and posterior tensor;
- directed 80-digit arithmetic;
- continuous interval covers rather than a finite posterior grid;
- curvature-based tangent and endpoint arguments;
- adaptive interval subdivision for the remaining regions; and
- hostile ambient-context reruns.

The coverage decomposition appears internally consistent: the tangent, endpoint, window, and regular segments together cover the relevant copies of \([0,1]\).

Nevertheless, there is no terminal objective attestation. The statements that the checker prints `PASS`, uses 136 cells, and returns the quoted 80-digit interval are untrusted run reports, not pinned execution evidence. The supplied record does not otherwise evaluate all of the numerous directed inequalities by hand. Therefore the crucial numerical assertions—especially the very small positive tangent margin and all interval-cover acceptance margins—are not affirmatively established by trusted execution in this packet.

The rounding implication itself is correct if the quoted enclosure is accepted:
\[
0.369296945969202842442713\ldots
<0.369296945969202842443.
\]

### 4. Claimed strict improvement and repaired predecessor

Numerically, the quoted final upper endpoint is strictly smaller than the quoted repaired endpoint:
\[
0.36929694596920284244\ldots
<
0.36929694655551972563\ldots .
\]
Thus the decimal comparison is sound.

The mathematical validity of the preceding repaired capacity certificate, however, depends on the same unestablished Theorem 9 premise and on an unattested interval run. In addition, the supplied repaired checker does not visibly enforce a separate exact zero-intercept infeasibility assertion; that negative-gap enclosure is reported in `CERTIFICATE.md` rather than established by terminal execution evidence. Hence the claims about a valid repaired certificate and its strictly negative zero-backoff gap remain unresolved.

These predecessor statements are not required to derive the new bound.

### 5. Invariant representation

Several elementary parts are directly correct:

- For \(0\le\epsilon\le1/3\), all displayed frontier and invariant weights are nonnegative.
- The proposed invariant quotient coordinates satisfy
  \[
  2s_B+s_C+s_D+s_E
  =2\frac{1-\epsilon}{2}+\epsilon=1.
  \]
- At the specified decimal \(\epsilon\), the displayed quotient point follows by substitution.

The exact-rational verifier is designed to show that the two six-row combinations have identical \(W,U,V\) coefficients and that their remaining root-level \(G,K\) residuals cancel after summing over the three groups sharing \(q_0\). That would indeed prove equality of the posterior-hierarchy functionals before any envelope optimization.

Two material obligations remain unsupported:

1. There is no terminal attestation establishing successful execution of this verifier.
2. The skew-pair ordering and the map from pair weights to the named rank-eight quotient are hard-coded or asserted rather than independently derived in the supplied claim evidence. Likewise, the additional invariant rows are not verified against the undeclared Theorem 9 source.

Accordingly, the exact functional identity is plausible and internally well encoded, but the full “skew-invariant Theorem 9 representation at the stated rank-eight quotient” claim is not affirmatively established.

### 6. Provenance

The assertions that these are four previously accepted artifacts and that the files are byte-for-byte verbatim ports are provenance statements. No source Git objects, content-addressed comparison attestation, or complete digest audit is supplied for all artifacts. Per the rubric, these historical assertions are retained as references only and are not treated as mathematical prerequisites.

### Dependencies

- **Declared reference transactions:** none.
- **Required accepted dependencies:** none available from the declared record.
- **Missing indispensable premise:** the content and applicability of the Gohari–Liu–Nair Theorem 9 outer bound, including verification of the used rows and side conditions.

Because that converse premise and the claimed interval executions remain unresolved, the exact universal capacity bound cannot be marked valid. No decisive counterexample or numerical contradiction was established, so the appropriate verdict is **indeterminate**, not invalid.
