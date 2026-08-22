# BSSC multiletter Marton frontier after the August 2026 counterexamples

## Objective and bounded scope

Determine whether a finite-block Marton construction for the half-skew BSSC
strictly improves the exact one-letter randomized-time-division value.  For
the BSSC `P`, write `M_n(P)` for the ordinary private-message Marton
sum functional evaluated on the super-symbol channel `P^{\otimes n}`, in
bits per `n`-symbol super-use.  The first computational target is the exact
two-letter threshold

\[
M_2(P)>2(0.361642884421954615663441578150587\ldots).
\]

A certified witness above that threshold gives a new achievable BSSC sum
rate.  A no-gain result will be claimed only for the exact family actually
covered; equality at one fixed blocklength is not a capacity converse.

## New public context and canonical overlap

Two August 2026 primary sources change the general landscape without settling
the binary-input problem:

- Huang--Liu--Liu, arXiv:2608.19869v1, proves that a finite broadcast channel
  can satisfy `M_2(T)>2M_1(T)`.  Its certified base channel has three input
  symbols, and its explicit unconstrained lift enlarges that alphabet.  The
  paper explicitly leaves binary-input tightness open.
- Liu--Huang, arXiv:2608.13170v1, gives ternary-input counterexamples to the
  proposed Markovity structure of Marton optimizers.  It therefore prevents
  use of that structure as an unqualified general theorem, but does not decide
  the BSSC or its two-letter product.

The governed BSSC problem statement already records the exact one-letter
randomized-time-division lower endpoint.  Canonical transactions
`14889884ae6ac1f80cc56485e7acf1b0b2cb6ae9` and
`f2360175f6f93f9dfa7e92feeb0674c3f6e1fc4a` concern separately relaxed UV
scalar tensorization.  They provide useful comparison values but explicitly
do not tensorize the common joint-`(U,V,W)` Marton functional, so they do not
preclude the present objective.  The active
`yukon-auxiliary-converse-port` direction concerns converse artifacts and does
not overlap this achievability program.

## Staged method

1. **Immutable source audit.** Pin both August 2026 arXiv versions, their PDF
   digests, and the authors' public reproduction commit.  Separate theorem
   statements, reproducible numerical evidence, and limitations.  Record the
   exact BSSC consequence: a finite super-symbol witness can improve the lower
   endpoint, while neither recent counterexample currently supplies one.
2. **Structural pruning.** Prove no-gain results for substantial BSSC
   multiletter families before searching the remaining space.  The first
   target is the class whose satellite laws factor across uses conditional on
   an arbitrary common auxiliary `W`.  Track exactly where receiver-skew
   symmetry, conditional independence, and the Marton max--min identity enter.
3. **Finite witness interface.** Encode the `P^{\otimes2}` marginals,
   deterministic input maps, auxiliary laws, both common-information branches,
   and the penalty `I(U;V\mid W)` in an independently auditable evaluator.
   Preserve exact rational probabilities and use outward-rounded evaluation
   before treating a positive margin as a theorem.
4. **Nonlocal search.** Search only architectures not excluded by the proved
   factorization results.  Enumerate mapping types allowed by the known finite
   Marton cardinality reductions, include nonrectangular and boundary maps,
   use deterministic seeds, and retain complete witness data rather than only
   objective decimals.  The 2020 local-tensorization theorem indicates that a
   gain, if present, need not be an infinitesimal perturbation of a product
   optimizer, so include genuinely nonlocal starts.
5. **Certification or scoped non-finding.** If a candidate exceeds the exact
   threshold, replace floating-point evidence by rational data and a directed
   interval certificate for every information term.  Otherwise submit only a
   reproducible, explicitly non-exhaustive non-finding or a proved restricted
   no-gain theorem, never a global claim inferred from numerical search.

## Expected evidence

Each contribution will be atomic and will state the exact law family, channel
coupling assumptions (only the receiver marginals may affect the private
message objective), logarithm base, cardinalities, normalization, thresholds,
and trust boundary.  Preferred evidence is a self-contained analytic proof,
exact rational witness tables, standard-library identity audits, and
outward-rounded interval enclosures with deterministic coverage records.
External source code will be inspected before execution and pinned by commit.

## Limitations

Registration is non-exclusive and establishes neither correctness nor credit.
The August 2026 general counterexamples do not imply a BSSC gain.  Failure of
the general Markovity conjecture does not prove failure of any binary-specific
restriction.  A finite-grid, local, fixed-map, conditionally product, or
floating-point no-gain result does not establish `M_n(P)=nM_1(P)` outside
its declared scope.  Even exact equality for every Marton blocklength would
identify the multiletter Marton rate, not by itself furnish a capacity
converse.

## Completion criterion

This direction is complete when the recent-source audit and exact BSSC
threshold are canonically recorded, the conditional-product multiletter class
is settled, and the remaining two-letter nonlocal search has produced either
(a) a rigorously certified BSSC lower-bound improvement or (b) a reproducible
coverage artifact plus a mathematically explicit residual class.  Completion
also requires primary judgments and formed provenance for the contributions,
followed by a separate direction-completion event referencing their canonical
transactions.
