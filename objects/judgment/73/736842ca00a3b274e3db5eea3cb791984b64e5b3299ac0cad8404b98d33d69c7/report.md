## `bssc-sum-capacity/fixed-pair-upper-bound-attested`

**Verdict: VALID, conditional on the expressly assumed Theorem 9 premise.**

### Required dependency

- **Required:** `e3c1036ca607539a5ebcddf3058e6014ac5c1cd9`
  
  Its mathematical content is needed to connect the six selected inequalities to the assumed Gohari–Liu–Nair outer bound and hence to \(C_{\mathrm{sum}}\). The subject does not independently prove that outer-bound interface.

The external manuscript itself is not authenticated here: the exact Theorem 9 statement is explicitly an assumption of both the dependency and this claim.

### Audit

1. **Auxiliary receivers.**  
   All four exact decimal probabilities lie in \([0,1]\). The verifier checks exactly
   \[
   K_0=1-G_1,\qquad K_1=1-G_0,
   \]
   so \(K\) is the required reflection of \(G\).

2. **Selected outer-bound rows.**  
   The six displayed rows agree with the dependency’s encoded rows
   \[
   R1A(1),\ R2T(1),\ SR(1,C),\ SL(2,U),\ SR(2,U),
   \ F_Y^{\mathrm{right-left}}.
   \]
   Their weights are nonnegative. Exact rational arithmetic verifies that their combined left side is precisely \(R_1+R_2\), including the zero-left-side feasibility row.

3. **Posterior reduction.**  
   Under the dependency’s factorization, every relevant auxiliary posterior satisfies the necessary Markov and martingale relations. The stated identities for \(I(W;A)\), \(I(U;A\mid W)\), \(I(U,W;A)\), and \(I(X;A\mid U,W)\) follow by chain rule and posterior conditioning. The exact tensor audit produces the displayed three-group functions and cancels all prior \(I_G(q_0)\) and \(I_K(q_0)\) terms.

4. **Weak-duality argument.**  
   The directions are correct: affine inner lines majorize \(f_U,f_V\); the martingale identities replace their conditional expectations by evaluation at \(q_W\); and the affine outer line then bounds each group. This requires neither strong duality nor an optimization-order exchange.

5. **Continuous-domain coverage.**  
   The certificate is not a posterior grid check. The curvature identity
   \[
   \operatorname{sgn} h''(q)
   =\operatorname{sgn}\!\left(a(1-a)-d^2+d(1-2a)q\right)
   \]
   is correct after clearing the positive denominators. The exact sign checks justify the concave, convex, tangent, endpoint, and reflected regions. The remaining regions are covered by outward-rounded interval subdivision. The interval derivative/mean-value tests, endpoint handling, depth guard, and cell-budget guard are mathematically sound for the functions used.

6. **All input priors.**  
   After summing the three group bounds, the affine slopes cancel and the only channel-dependent prior term is
   \[
   c'_1\bigl(I_Y(q_0)+I_Z(q_0)\bigr).
   \]
   This is concave and invariant under \(q_0\mapsto1-q_0\), so its global maximum on \([0,1]\) occurs at \(q_0=\tfrac12\). Thus the certificate covers every prior, not only the fair prior.

7. **Objective attestation.**  
   The terminal attestation records successful execution of the pinned no-argument verifier with exit code \(0\). It establishes that the supplied checker completed the exact row/tensor audit, continuous interval coverage, all-prior reduction, and hostile-Decimal-context reproducibility, obtaining
   \[
   U\in[
   0.36929694596920284244271335135600317726937686320586339865039784778686683932875798,
   \]
   \[
   0.36929694596920284244271335135600317726937686320586339865039784778686683932875818].
   \]
   The upper endpoint is strictly below
   \[
   0.369296945969202842443,
   \]
   so the rounded headline follows.

### Scope

Accordingly, under the stated Theorem 9 premise,
\[
\boxed{C_{\mathrm{sum}}\le 0.369296945969202842443}.
\]
This verifies only the fixed receiver pair and its dual certificate. It does not establish Theorem 9 itself, receiver or dual optimality, a matching achievable rate, or the exact sum-capacity.
