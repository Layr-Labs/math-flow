## `bssc-sum-capacity/two-letter-marton-product-code-quotient-local-maximum`

**Verdict: valid**

### Mathematical audit

1. **Specified family and tensor point**
   - The four deterministic maps are encoded correctly by `auxiliary_map`.
   - The checker verifies that the displayed \(q_*\) is exactly
     \(r_*\otimes r_*\), not merely a numerical approximation.
   - Using \(15q_-^2-15q_-+2=0\),
     \[
     \frac{q_-^2}{4}=\frac{11-\sqrt{105}}{120},\quad
     \frac{q_-(1-q_-)}4=\frac1{30},\quad
     \frac{(1-q_-)^2}{4}=\frac{11+\sqrt{105}}{120},
     \]
     so the displayed matrix is correct.
   - All 16 entries are strictly positive and sum exactly to one; hence \(q_*\) is an interior point of the 15-dimensional simplex.

2. **Entropy representation**
   - Expanding the two endpoint functionals confirms
     \[
     L_{1/2}
     =\tfrac12\{H(Y^2)+H(Z^2)+H(W,Y^2)+H(W,Z^2)\}
      -H(W,U,Y^2)-H(W,V,Z^2)+H(W,U,V).
     \]
   - The seven aggregation maps in the checker correctly encode these marginals for the stated product BSSC and deterministic auxiliary maps.
   - Use of natural-log units in the Hessian computation only multiplies the base-two functional by the positive constant \(\ln 2\); it does not affect stationarity or definiteness.

3. **Exact stationarity**
   - For each entropy term \(H(Aq)\), the checker correctly represents the gradient as sums of constants and logarithms of marginal masses.
   - Every marginal mass used in a logarithm is checked to be strictly positive.
   - For all 15 independent gradient differences, rational coefficients are cleared and the resulting product identities are checked exactly in \(\mathbb Q(\sqrt{105})\).
   - Because all factors are positive, equality of those exact products is equivalent to equality of the corresponding logarithmic sums. The checker also verifies the constant terms. Thus all 16 ambient gradient components are equal, which is precisely stationarity on the simplex tangent hyperplane.

4. **Exact Hessian and negative definiteness**
   - The implemented identity
     \[
     \nabla^2H(Aq)=-A^{\mathsf T}\operatorname{diag}((Aq)^{-1})A
     \]
     is correct.
   - Restriction with columns \(e_i-e_{15}\), \(0\le i<15\), covers the entire tangent space \(\sum_i\delta q_i=0\).
   - The checker constructs an exact unit-lower-triangular \(LDL^{\mathsf T}\) factorization, verifies exact reconstruction entry by entry, and establishes by exact quadratic-field sign tests that all 15 pivots are strictly negative.
   - Therefore the restricted Hessian is negative definite by congruence with the negative diagonal matrix \(D\).

5. **Strict local maximum**
   - The relevant entropy marginals are positive at \(q_*\), so the functional is \(C^2\) on a neighborhood within the open simplex.
   - Interior tangent stationarity together with a negative-definite tangent Hessian satisfies the second-derivative test. Hence \(q_*\) is a strict local maximum in exactly the stated fixed-map 15-dimensional family.

6. **Value and nearby selected-law conclusion**
   - The declared reference proves that the one-use fair two-state RTD law with conditional priors \(q_-\) and \(1-q_-\) attains \(L_{\rm RTD}\). This is exactly the one-use law \(r_*\) used here.
   - The two-use construction is the independent product of two such laws. All mutual-information terms, including the conditional penalty, add under this independent product, giving
     \[
     L_{1/2}(q_*)=2L_{\rm RTD}.
     \]
   - Receiver/input-complement symmetry also gives \(E_Y(q_*)=E_Z(q_*)\).
   - Strict local maximality supplies a neighborhood in which every \(q\ne q_*\) has
     \[
     L_{1/2}(q)<2L_{\rm RTD}.
     \]
     Since
     \[
     \min\{E_Y(q),E_Z(q)\}\le \frac{E_Y(q)+E_Z(q)}2=L_{1/2}(q),
     \]
     every distinct sufficiently close selected law has Marton value strictly below \(2L_{\rm RTD}\).

### Objective-attestation audit

The passed subject attestation executes the supplied standard-library checker and establishes:

- exact tensor-product and orientation identities;
- 15 exact tangent-gradient identities;
- construction of all seven required marginal maps;
- exact Hessian symmetry;
- 15 strictly negative exact \(LDL^{\mathsf T}\) pivots; and
- exact factorization reconstruction.

The printed decimal pivots are only diagnostics; the acceptance predicate uses exact \(\mathbb Q(\sqrt{105})\) arithmetic. The checker does not itself prove the analytic second-derivative implication or the \(2L_{\rm RTD}\) identification, but those steps are supplied and verified separately above.

### Dependencies

- **Required dependency:** `88a1004f309460f3ec1cacdae88d30f88559f9bc`
  - Required only for identifying the one-use law as a global RTD optimizer and naming its value \(L_{\rm RTD}\).
  - Its relevant RTD symmetrization and calculus argument is sufficient and unconditional; neither `(H-Marton)` nor `(H-binary)` is needed for this claim.
- The stationarity, Hessian, and strict-local-maximum portions are independently established in the subject.

### Scope

The conclusion is correctly limited to the open 16-cell, fixed-deterministic-map quotient. It establishes neither global optimality in that quotient nor any statement about other maps, additional atoms or auxiliaries, Marton additivity, achievable capacity improvement, or a capacity converse.
