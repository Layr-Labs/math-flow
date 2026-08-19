## `maximal-determinant-23/three-star-ehlich-perturbation-exclusion`

**Verdict: indeterminate**

No explicit counterexample or decisive algebraic error was found, and the proposed exhaustive verifier has a broadly coherent structure. However, the supplied evidence does not affirmatively establish that the exhaustive computation actually completed with `verification: PASS`, and several material premises are not available through the declared dependency packet.

### 1. Reduction to canonical star specifications

The intended reduction is plausible:

- `partitions(23)` recursively enumerates nondecreasing positive partitions of \(23\).
- `indexed_specs` considers every center block and every unordered multiset of three leaf blocks.
- The multiplicity test correctly enforces that the center and leaves can be represented by four distinct coordinates.
- Permuting equal-sized parent blocks and permuting the three leaves are the relevant evident symmetries.
- `selected_tokens` reconstructs four distinct vertices and checks idempotence of the canonical descriptor.

Nevertheless, the exact orbit-classification assertion is not fully certified by the checks in the program. In particular,

```python
specs = canonical_specs(partition)
if set(expanded) != set(specs):
```

does not independently test completeness: `canonical_specs` is defined as `sorted(set(indexed_specs(partition)))`, so this equality is true by construction. The prose asserts, but does not prove in detail, that two assignments have the same descriptor **exactly if** they are related by the stated symmetries. Idempotence alone does not establish that biconditional.

There is also no explicit proof of the reduction from an arbitrarily ordered tuple \((r_1,\ldots,r_s)\), if “partition” is interpreted that way, to the nondecreasing representation used by the program. This would require the usual simultaneous coordinate-permutation argument.

These points are likely repairable, but the audit may not supply those omitted arguments.

### 2. Determinant formulas

The displayed algebra is internally consistent:

- Writing
  \[
  E=B-J,\qquad
  B=20I+4\operatorname{diag}(J_{r_1},\ldots,J_{r_s}),
  \]
  gives
  \[
  \det B=20^{23-s}\prod_i(20+4r_i).
  \]
- The stated
  \[
  \Delta=1-\sum_i\frac{r_i}{4(5+r_i)}
  \]
  and the formula for \(E^{-1}\) agree with block inversion followed by a rank-one Sherman–Morrison correction.
- The three toggles are indeed
  \[
  e_cv^{\mathsf T}+ve_c^{\mathsf T},
  \]
  with coefficient \(-4\) for a within-block toggle and \(+4\) for a between-block toggle.
- The correction
  \[
  (1+e_c^{\mathsf T}E^{-1}v)^2
  -(e_c^{\mathsf T}E^{-1}e_c)(v^{\mathsf T}E^{-1}v)
  \]
  is the correct \(2\times2\) matrix-determinant-lemma factor.

The Bareiss implementation also appears to use exact integer arithmetic and, on the candidates where it is invoked, compares the direct determinant with the rank-two result.

The unresolved issue is computational: the crucial conclusions

\[
74\,896\text{ strictly above threshold},\qquad
0\text{ at threshold},\qquad
104\text{ normalized squares}
\]

are results of evaluating \(102\,799\) cases. The expected values are hardcoded constants. No execution transcript, per-candidate determinant list, or independently checkable aggregate certificate is supplied. The README says that running the program produces `verification: PASS`, but that assertion is not itself an exact replay result. Without executing the supplied program, these finite but material calculations remain unverified.

### 3. Nonsquare obstruction

Conditional on the computed determinants, the obstruction is sound. If \(G=AA^{\mathsf T}\), then

\[
\det G=(\det A)^2.
\]

Moreover, the verifier directly requires every candidate determinant to be divisible by \(2^{44}\). Since \(2^{44}\) is itself a square, nonsquareness of \(\det G/2^{44}\) implies nonsquareness of \(\det G\).

The README instead invokes the universal assertion \(2^{22}\mid\det A\) through transaction  
`7b28860c418486cb41e6379e68cc355ff861b1a5`. That transaction is not declared as a dependency and its proof is not supplied. Thus the argument as explicitly presented relies on unavailable dependency evidence. A candidate-specific reformulation avoiding that dependency is possible, but supplying it would amount to repairing the submitted proof.

The count \(74\,792\) is also dependent on the unexecuted exhaustive computation.

### 4. Hasse-invariant exclusions

The conditional logic is correct in form:

- A nonsingular factorization \(G=AA^{\mathsf T}\) makes \(G\) rationally congruent to \(I_{23}\).
- Hence a local invariant differing from that of the identity would exclude the factorization.
- The rational Schur-complement diagonalization and the independent leading-minor ratios are appropriate exact methods.
- The implemented odd-prime and \(2\)-adic Hilbert-symbol formulas have the standard form.

However:

1. No quadratic-form theorem establishing congruence invariance of the computed Hasse invariant is supplied through an explicit dependency.
2. The cited literature is not part of the declared dependency packet.
3. The identities used by `hilbert_symbol` are not proved in the contribution.
4. The \(83\) excluded specifications and witnessing primes are not included as a static certificate; they are discovered afresh by the verifier.
5. Consequently, the claim that exactly \(83\) candidates have a witnessing prime is unresolved without replay.

These are material because the final exhaustion depends on all \(83\) exclusions.

### 5. Inverse-quadratic and cell-moment exclusions

The mathematical implications are correctly formulated, conditional on the exact computations:

- For a column \(x=Ae_k\),
  \[
  x^{\mathsf T}G^{-1}x=1.
  \]
- Constancy of \(G^{-1}\) on the stated cells makes this quadratic expression depend only on the parity-compatible cell sums.
- The aggregate identity
  \[
  \sum_{k=1}^{23}t_i^{(k)}t_j^{(k)}
  =\sum_{a\in C_i}\sum_{b\in C_j}G_{ab}
  \]
  follows from \(AA^{\mathsf T}=G\).
- A functional nonnegative on every individually admissible pattern but negative on the required aggregate target gives a valid contradiction.

The JSON supplies the \(21\) claimed final certificates, and the verifier checks their signs using exact rational and integer arithmetic. But it does not include the enumerated admissible pattern sets or precomputed sign tables. Thus the two empty-pattern assertions and all nineteen Farkas inequalities still depend on actually running the verifier. Their validity cannot be inferred merely from the presence of the multipliers.

### 6. Final exhaustion

The final conclusion requires all of the following exact results:

\[
74\,896
=
74\,792+83+2+19,
\]

no threshold-equality case, correct canonical coverage, and disjoint exhaustive coverage of all \(104\) normalized-square candidates. The code is designed to check these conditions, but the supplied evidence contains no independently verified successful replay. In addition, the orbit-classification and Hasse-invariance premises are not fully established within the declared dependencies.

Therefore the exact universal exclusion claim cannot be marked valid from the supplied evidence. A successful independent execution together with the missing symmetry and local-quadratic-form justifications would be needed to resolve it.
