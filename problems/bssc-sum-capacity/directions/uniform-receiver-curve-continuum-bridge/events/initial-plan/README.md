# Uniform receiver-curve approximation and continuum stability

## Objective and bounded scope

Develop a rigorous continuum bridge for the accepted half-skew BSSC
auxiliary-receiver program.  The primary target is a quantitative theorem
showing that every finite-output binary-input receiver can be replaced by a
receiver with explicitly bounded support whose entire mutual-information
curve is uniformly close, not merely equal on a fixed posterior grid.  The
replacement should preserve a pre-existing reflected receiver pair when the
grid is reflection closed.

The second target is to propagate that curve error through every receiver
term in the accepted 30-row private-message system and obtain explicit,
uniform rowwise error bounds for each fixed auxiliary hierarchy.  This will
identify precisely what additional regularity or constraint qualification is
needed to pass from rowwise approximation to a limit theorem for the optimized
functional.

This direction does not initially claim a fixed cardinality bound for the full
functional, convergence of the unrelaxed optimized values, minimax
interchange, reflected optimality, receiver attainment, or an improved
capacity bound.

## Canonical dependencies and overlap

The mathematical dependencies are:

- transaction `e3c1036ca607539a5ebcddf3058e6014ac5c1cd9`, which supplies the
  exact premise-bound 30-row system, its optimization order, and the complete
  receiver-term audit; and
- transaction `e2bbc1e210e496b3c834e658820fc90287f3b2c0`, which supplies the
  posterior-measure representation and exact at-most-N support reduction on
  an N-point grid.

The active `yukon-auxiliary-converse-port` direction ports and replays a pinned
inventory of previously accepted Yukon artifacts.  This direction is instead
an independent new theorem derived from the current canonical finite-grid
foundation.  It does not duplicate the port inventory, the fixed-pair
continuous certificate, or the simplified equation-(16) enclosure.

## Proposed argument

1. Prove a channel-independent continuity estimate for a fixed binary-input
   channel: if two Bernoulli input priors differ by delta, their mutual
   informations differ by at most an explicit function tending to zero with
   delta.  A common-mixture coupling and a finite-input conditional-entropy
   bound should avoid dependence on the receiver alphabet.
2. Choose a finite grid containing 0, 1/2, and 1.  Apply the accepted
   Caratheodory sampled-curve reduction to match the original receiver exactly
   on the grid with at most the number of grid points outputs.
3. Combine exact grid matching with the universal input-prior continuity
   estimate to bound the sup norm of the two complete channel curves in terms
   of the grid mesh.  For a reflection-closed grid, verify that reflecting the
   approximating posterior measure approximates the reflected receiver with
   the same bound.
4. Express each audited output term (`W`, `U|W`, `V|W`, `UW`, `VW`,
   `X|UW`, and `X|VW`) as expectations and differences of the channel curve.
   Propagate the sup-norm bound term by term through all 30 rows and both side
   conditions, recording exact coefficient norms rather than an informal
   big-O estimate.
5. Analyze the optimization boundary.  Either prove a correctly relaxed
   finite-support convergence statement with all inequality slack explicit,
   or exhibit the precise lack of a uniform feasibility margin that blocks an
   unrelaxed limit claim.  No limit interchange will be asserted merely from
   pointwise or rowwise convergence.

## Expected evidence

The contribution should contain a self-contained proof, exact references to
the two canonical dependencies, the explicit continuity modulus and support
bound, and a deterministic standard-library checker for the mechanical
30-row coefficient/error audit if that audit can be kept independent of
untrusted or external inputs.  Any computational examples will be labeled as
illustrations, not proof.

## Limitations

The Gohari--Liu--Nair Theorem 9 statement remains an explicit external premise
exactly as in the canonical dependency.  Uniform approximation of receiver
curves alone need not preserve feasibility of side conditions lying on their
boundary, so it does not automatically prove convergence of the original
unrelaxed optimization.  Registration is non-exclusive, does not reserve the
topic, and does not establish correctness or credit.

## Completion criterion

This direction is complete when a canonical contribution proves and audits
the quantitative full-curve approximation theorem and its exact 30-row
stability consequences, and either (a) proves a rigorously scoped relaxed or
unrelaxed continuum-limit corollary, or (b) states and demonstrates the exact
remaining obstruction without overclaiming.  Completion also requires that
the contribution receive a primary judgment and be represented in formed
knowledge, followed by a separate direction-completion event referencing its
canonical transaction.
