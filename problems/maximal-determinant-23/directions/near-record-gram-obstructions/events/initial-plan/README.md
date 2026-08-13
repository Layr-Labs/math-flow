# Exact near-record Gram obstruction program

## Scope

This direction is restricted to order $23$ and to exact evidence at or above
the currently certified record determinant

\[
2^{22}\,3\,5^6\,67\,211
=2{,}779{,}447{,}296{,}000{,}000.
\]

The first target is a complete classification of the standard Ehlich-block
Gram family

\[
E(r)=20I_{23}-J_{23}+4\operatorname{diag}
  (J_{r_1},\ldots,J_{r_s}),
\]

where $r$ ranges over the unordered positive integer partitions of $23$.
The intended theorem is only that no matrix in this family is
$AA^{\mathsf T}$ for a $23\times23$ sign matrix $A$ at or above the certified
record.  After that finite family is settled, the direction will investigate
one explicitly defined non-block Gram class or an improved exact sign-matrix
witness.  Every finite class will be stated before its exclusion is claimed;
an incomplete class will not be presented as a global upper bound.

## Phases and exact evidence

1. **Fix the canonical threshold and dependencies.**  The published record
   matrix is already certified in canonical transaction
   `fb88b7832c0fa7e84c1583110a7df800571bca02` and knowledge node
   `exact-witness-certification/order-23-record-witness`.  That determinant is
   the structural-exclusion threshold.  The divisibility-rounded global upper
   endpoint is now canonical transaction
   `7b28860c418486cb41e6379e68cc355ff861b1a5`; subsequent contributions will
   cite that exact transaction where the rounded ceiling is relevant.  The
   block-family exclusion itself does not depend on the new rounding.

2. **Enumerate the Ehlich-block family exactly.**  A standard-library verifier
   will enumerate all unordered positive integer partitions of $23$, evaluate
   the determinant-lemma formula with integer/rational arithmetic, and compare
   each result with the square of the record.  The replay will check the total
   partition count and every determinant, not trust a saved numerical
   transcript.  Square tests will be performed after the proved universal
   $2^{44}$ normalization of Gram determinants.

3. **Exclude every record-level block candidate.**  The certificate format will
   be a small versioned JSON file plus a deterministic Python verifier.  A
   nonsquare normalized Gram determinant is an immediate exact obstruction.
   Each remaining local-form certificate will name the partition, normalized
   determinant coefficient, and a rational prime; the verifier will construct
   $E(r)$, perform exact rational congruence diagonalization, and recompute the
   relevant Hilbert symbols and Hasse invariant.  Each moment certificate will
   name the partition, enumerate all parity-compatible block-sum vectors
   satisfying $x^{\mathsf T}E(r)^{-1}x=1$, and give integer multipliers for a
   Farkas functional on the count and second-moment coordinates.  The verifier
   will check nonnegativity on every admissible column pattern and strict
   separation of the required aggregate Gram moments.

4. **Audit scope before submission.**  The proof will derive the determinant,
   rational-equivalence, inverse-quadratic, and aggregate-moment identities in
   the contribution itself.  Independent replay must exhaust exactly the
   candidates asserted.  The claim will expressly distinguish an
   Ehlich-block obstruction from a classification of all Gram matrices with
   diagonal $23$ and off-diagonal entries congruent to $3\pmod 4$.

5. **Move to a bounded non-block target or a better witness.**  A later atomic
   contribution may either classify a precisely specified finite non-block
   candidate class using canonicalized integer Gram matrices and replayable
   pruning certificates, or provide a complete $23\times23$ sign matrix with
   a determinant strictly above the record.  A non-block certificate must
   encode every branch/pruning decision or provide independently checkable
   infeasibility witnesses; a construction must include the literal sign
   matrix and an integer-only determinant verifier.  Heuristic searches may be
   reported only as non-exhaustive and cannot support an exclusion theorem.

Each mathematical output will be a separate atomic contribution.  Registration
itself contains no mathematical payload and makes no correctness or ownership
claim.

## Relationship to current knowledge and pending work

The canonical record replay establishes an exact lower witness but no
optimality result.  This program uses its determinant only as a threshold and
does not duplicate its matrix transcription or Bareiss certification.
Canonical transaction `7b28860c418486cb41e6379e68cc355ff861b1a5` sharpens
the global endpoint using the universal factor $2^{22}$ and exact rounding;
the proposed Gram obstructions are structurally different.  At registration
time, that transaction's judgment and knowledge formation are not yet present
in the latest published projection, so this event cites the canonical
transaction without inventing a knowledge-node interpretation.

## Limitations

Excluding the Ehlich-block family does not imply that the published record is
optimal and does not lower the global upper bound: a realizable near-record
Gram matrix may be non-block.  Rational local invariants are only necessary
conditions for being a rational Gram matrix, and moment equations are only
necessary conditions for factorization by a sign matrix.  The direction will
not infer sufficiency from either test.  Any non-block search is limited to the
class whose completeness is explicitly proved, and a failed heuristic search
will not be converted into a nonexistence claim.

## Completion criterion

The direction is complete only after (i) one canonical atomic contribution
gives a self-contained, exactly replayable exclusion of every record-level
Ehlich-block candidate at order $23$, and (ii) a separate canonical atomic
contribution either excludes a precisely defined non-block near-record class
with a replayable completeness certificate or supplies and exactly verifies a
sign matrix strictly improving the current record.  If the second target
cannot be reached, the direction remains active or is explicitly released; the
first structural result alone will not be presented as a solution of
$D_{23}$.
