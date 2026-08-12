This assessment assigns qualitative credit to immutable transaction IDs for their causal role in producing the locked knowledge state. It does not revise any mathematical judgment or rank the transactions on a single scale.

## Contribution: dfc0cc40d41105292a119840dcdbe6f22860cf43

**Primary roles:** certificate packaging, exact verification, baseline certification, and elementary structural exposition.

This transaction supplied the ledger’s foundational executable evidence: a pinned encoding of 152 points in \(G_{76}\), together with a deterministic verifier checking distinctness, grid membership, and all \(573{,}800\) unordered triples using exact integer determinants. Its durable mathematical effect was to make the lower-bound implication \(D(77)\ge 152\) self-contained within the ledger rather than dependent on a mutable external database. It therefore directly supports `g76/152-point-certificate` and the lower endpoint in `d77/certified-interval`.

The transaction should receive substantial credit for **reproduction and independent certification**, but not for originating the coordinate construction. The locked state attributes the underlying 152-point set to Achim Flammenkamp’s maintained database. The transaction’s distinctive work was preserving the certificate, documenting its encoding, and supplying a complete, small verifier. That distinction matters: copying coordinates alone would have had limited value, while pairing them with an exhaustive exact checker created a reusable research object.

The certificate also causally enabled later work. Transaction `c5e8096d942d57228bb4fed00f7617fb6b43af9f` used its pinned configuration as the base object for the local-rigidity analysis, and transaction `0ffe9a12c3ad44cf136dd22df7083dcdd53af1b0` later repackaged the same certificate and checker for a hosted-verification request. Thus this first transaction contributed not only a bound but infrastructure on which two later transactions depended.

Its quality is strong for the claim actually certified:

- the arithmetic is exact and deterministic;
- the checker is dependency-free apart from the Python standard library;
- every triple is tested rather than sampled;
- the embedding \(G_{76}\subset G_{77}\) makes the lower-bound implication immediate.

There are minor limitations that narrow, but do not materially undermine, this verification credit. The checker infers the grid size and number of points from the payload instead of separately hard-coding 76 and 152. The locked state records that the decoded artifact nevertheless exposes exactly those values. It also accepts a symmetry marker without checking the represented quarter-turn symmetry. That omission does not affect the no-three-in-line certificate; the symmetry property was separately verified by the next transaction. These qualifications are recorded in `g76/152-point-certificate` at its current second revision.

The transaction also states the elementary row upper bound and the resulting interval \(152\le D(77)\le154\). It receives appropriate expository and baseline credit for placing those facts next to the certificate, but little originality credit for the elementary upper bound itself. Likewise, the necessary row-and-column occupancy patterns recorded in `d77/extremal-occupancy` are useful structural consequences, but they are elementary deductions rather than a deep advance.

The suggested search programs were sensible orientation for later work, especially perturbation and symmetry analysis. They were broad suggestions, however, and should not be treated as ownership of those later directions. The durable priority of this transaction lies in being the first canonical ledger entry to supply the pinned, independently checkable baseline object.

**Overall significance:** foundational for certification and reproducibility, with high verification value; limited construction originality and no improvement beyond the already stated interval.

## Contribution: c5e8096d942d57228bb4fed00f7617fb6b43af9f

**Primary roles:** exhaustive local computation, negative search result, symmetry verification, structural census, and derivation of a local distance constraint.

This transaction turned the first transaction’s static certificate into a substantive local research program. For each of the eight specified embeddings of the record into \(G_{77}\), it established the saturation and removal-depth-two results recorded in `d77/embedded-record-local-rigidity`. In particular, it supplied an exhaustive account showing that every outside cell is blocked, one removal frees no originally outside cell, and two removals free at most one such cell, with a complete census of the exceptional removal pairs.

That is a meaningful **negative computational result with precise local force**. It rules out direct extension and all improvements lying within the tested removal neighborhood. Its most durable derived capability is the pruning statement in `d77/distance-from-embedded-record`: any no-three-in-line set of at least 153 points must have symmetric-difference distance at least seven from each specified embedding. This does not improve the certified interval, but it tells subsequent searches where solutions cannot lie and prevents repeated effort on a natural but shallow perturbative neighborhood.

The transaction also independently checked the quarter-turn symmetry left unverified by the baseline checker. From that it computed exactly two distinct dihedral images and eight distinct translated embeddings, as recorded in `g76/record-symmetry-and-g77-embeddings`. This deserves separate verification credit: it corrected an evidentiary gap about the symmetry marker and made the scope of the local census explicit.

The computational quality is strong. The contribution provided:

- deterministic standard-library source;
- exact integer arithmetic;
- re-verification of the base configuration and every embedding;
- a direction-based line census;
- a line-walk and hitting-set cross-check;
- direct simulation of every reported freeing; and
- committed output required to match the recomputed results.

The two enumeration paths are structurally different enough to strengthen confidence, although they are not wholly independent: they share the decoded input and primitive-direction machinery. The locked state also notes that confidence rests on source inspection and committed output rather than a separately documented execution environment. Those are modest reproducibility qualifications, not reasons to withhold credit for the accepted computations.

Scope discipline is important here. The README initially says the work “prunes the entire ‘perturb the known record’ strategy,” but the locked state retains only the narrower conclusion in `d77/record-perturbation-frontier`: the justified pruning ends at removal depth two for eight specified embeddings of this one record. Removal of three or more points, three-for-four replacements, other 152-point configurations, unrelated affine images, and distant configurations remain open. Credit should therefore attach to the complete depth-two census and its distance corollary, not to the broader rhetorical claim.

In priority terms, this transaction properly builds on the configuration supplied by `dfc0cc40d41105292a119840dcdbe6f22860cf43`. The earlier transaction retains credit for the pinned certificate; this transaction receives the distinct credit for devising and executing the local-rigidity analysis. Its explicit attribution of the base coordinates and prior packaging avoids conflating these roles.

**Overall significance:** a substantial and well-supported local structural advance. It does not address global optimality, but it creates durable search pruning, verifies the record’s symmetry, and establishes a complete negative result within a clearly bounded neighborhood.

## Contribution: c98dd877ad81611a9a469b1bd790cd909b56b1ce

**Primary roles:** symmetry-program formulation, orbit lemmas, restricted-model construction, exact implementation, calibration, and honestly scoped bounded search.

This transaction established the second major research program in the locked state: rotational restrictions and exact modeling of the strict `rct4` subclass. Its most substantial durable product is the model recorded in `d77/rct4-154-model`. The model represents 154-point `rct4` configurations with 1,444 off-diagonal orbit variables, 38 diagonal-pair variables, exact cardinality conditions, and 388,148 deduplicated weighted line constraints. Within that subclass, the locked state accepts the model as sound and complete.

That modeling work merits significant **construction and enabling-infrastructure credit**. A feasible assignment would provide a 154-point certificate and settle \(D(77)=154\), while an infeasibility result would exclude only the strict subclass. Even though neither outcome was obtained, producing an exact reusable instance materially increases the capability available to later solver work.

The transaction also supplied the half-turn and quarter-turn orbit arguments recorded in `rotational-symmetry/cardinality-obstructions`:

- odd half-turn-invariant no-three-in-line sets have at most one point;
- quarter-turn-invariant sets have cardinality divisible by four or are singletons;
- quarter-turn symmetry is therefore excluded at sizes 153 and 154;
- a 154-point half-turn-invariant set must be centered at \((38,38)\), with the center unselected.

These are genuine structural contributions. However, the transaction’s broader assertion that these exhausted all possible rotations about arbitrary centers was initially incomplete. The missing finite-rotation classification was later supplied by transaction `29ccbd396781fd36d436ed2e6d0952a4730361b9`. Accordingly, this transaction deserves credit for the correct orbit arguments, the conditional center analysis, and for identifying the intended rotational classification, but not for completing the arbitrary-center proof. That qualification is reflected in the history of `d77/rotational-classification-scope`.

The implementation was strengthened by the five exact calibration certificates recorded in `rct4/calibration-certificates`. Verifying known instances at \(n=41,47,57,65,69\) checked decoding, no-three-in-line validity, orbit structure, and satisfaction of generated constraints. These are useful regression tests and support confidence that the implementation captures its stated class. They do not confer discovery credit for those configurations or establish anything about satisfiability at \(n=77\).

Originality must also be apportioned carefully. The locked state attributes the underlying `rct4` class and symmetry-reduction method to prior work. This transaction’s proper credit is for an independent implementation, the concrete \(n=77\) instantiation, validation machinery, model export and verification tools, and the integration of the class into this ledger’s research program—not for originating the class itself.

The bounded CP-SAT and SAT runs receive only limited experimental credit. They documented reproducible budgets and outcomes, and the contribution correctly emphasized that timeouts were not impossibility evidence. The calibration failures under similar budgets usefully demonstrated that the available hardware and search budgets were weak. Under `program/rotational-symmetry`, satisfiability at \(n=77\) remains unresolved, so the negative runs contribute operational information rather than mathematical exclusion.

The unverified private breakthrough report served as motivation but supplied no artifact and produced no locked mathematical knowledge. It should not receive priority or proof credit through this transaction.

**Overall significance:** substantial as exact restricted-search infrastructure and as the source of the accepted orbit obstructions; qualified regarding the initially incomplete arbitrary-center classification; no credit for a bound improvement or for the weak timeouts as negative mathematical evidence.

## Contribution: 29ccbd396781fd36d436ed2e6d0952a4730361b9

**Primary roles:** proof, correction and completion of a prior qualified claim, structural synthesis, and precise scope clarification.

This transaction supplied the decisive missing argument for the arbitrary-center rotational classification. Its finite-rotation proof shows that a nonidentity Euclidean rotation preserving a finite noncollinear subset of \(\mathbb Z^2\) must be a half-turn or quarter-turn, without assuming that the center is a lattice point or that the rotation preserves the ambient square.

The proof’s durable value lies in closing a specifically identified logical gap. It uses noncollinear lattice differences to show that the rotation matrix is rational, finite permutation order to obtain finite rotational order, and the trace/eigenvalue argument to restrict the possibilities. This converted the previously qualified claim in `d77/rotational-classification-scope` into the complete classification recorded in its current second revision.

The transaction then combined that new theorem with earlier accepted components:

- the half-turn and quarter-turn orbit obstructions from `c98dd877ad81611a9a469b1bd790cd909b56b1ce`; and
- the full row-and-column occupancy condition for 154 points associated with `dfc0cc40d41105292a119840dcdbe6f22860cf43`.

This synthesis yields the locked conclusions that a hypothetical 153-point set has no nonidentity rotational symmetry and that any rotationally symmetric 154-point set must use the half-turn about \((38,38)\) with the center unselected. Those consequences are recorded in `rotational-symmetry/cardinality-obstructions` and `d77/154-half-turn-center`.

Credit should be carefully separated among these ingredients. Transaction `29ccbd396781fd36d436ed2e6d0952a4730361b9` receives primary credit for the arbitrary-center finite-rotation theorem and for completing the application. It should not absorb credit for the earlier orbit arguments, occupancy observation, or `rct4` model, all of which it explicitly reuses. Conversely, the earlier transaction’s identification of the missing step does not diminish the later transaction’s proof credit.

The quality of this contribution is high within its stated scope. It is self-contained, noncomputational, and directly addresses the precise deficiency previously recorded. It also states its limitations accurately: rotations only, finite noncollinear lattice sets only, no reflection classification, no identification of general centered half-turn sets with `rct4`, and no existence or global impossibility result at sizes 153 or 154. Thus it improves structural knowledge without changing `d77/certified-interval`.

**Reservation evidence:** the contribution cites research-direction registration transaction `a9552d14dcd11d394a0ae9672b6d81dae033f127` for the task of closing the arbitrary-center gap. This is specific enough to provide some evidence of direction priority: it identifies a definite missing lemma and is connected to the resulting proof. Its weight is nevertheless limited because the supplied material does not include the registration’s full content or timing. Moreover, `c98dd877ad81611a9a469b1bd790cd909b56b1ce` had already exposed the underlying gap in earlier canonical ledger order. The registration therefore supports timely intention and competent pursuit by the later effort; it does not confer ownership of the broader symmetry program or displace the earlier transaction’s framing credit. The actual proof credit rests on transaction `29ccbd396781fd36d436ed2e6d0952a4730361b9`.

**Overall significance:** a focused but important proof advance that turns an incomplete rotational claim into a complete theorem within the accepted scope. It closes a structural question rather than improving the extremal bounds.

## Contribution: 0ffe9a12c3ad44cf136dd22df7083dcdd53af1b0

**Primary roles:** replay packaging, verification-request infrastructure, artifact republication, and prospective execution independence.

This transaction republished the existing 152-point certificate and checker together with a canonical request for execution in a governed hosted-verifier environment. Its intended causal contribution was operational: make the established lower-bound certificate replayable through a standardized trusted execution path and permit a content-addressed execution attestation to be produced separately.

That is a legitimate but limited infrastructure contribution. The locked state credits it with republishing the certificate and checker in replayable form and with packaging the hosted-verification request. It can re-establish the same lower-bound implication when the checker is run, as reflected in the second revisions of `g76/152-point-certificate` and `d77/certified-interval`.

The transaction does not receive discovery, construction, or new-algorithm credit. Its configuration and checker logic duplicate those of `dfc0cc40d41105292a119840dcdbe6f22860cf43`; consequently, even a future hosted run would add execution-environment independence rather than algorithmic independence. Nor does it improve either endpoint, provide a 153- or 154-point certificate, prove an exclusion, or contribute evidence about optimality. The exact-value question therefore remains unchanged in `d77/exact-value`.

The main intended objective was not completed in the locked state. No hosted-run attestation, execution transcript, exit status, or content-addressed verifier output was supplied. The external verifier schema and binding rules were also unavailable for independent assessment. Credit must therefore be assigned for creating the request and replay package, not for obtaining the promised objective attestation.

There are two further quality qualifications:

1. Strict byte-for-byte identity with the earlier artifacts was asserted but not independently established by a checksum covering details such as terminal newlines or line endings. The locked state supports identity in mathematical substance, which is sufficient for the repeated mathematical implication but weaker than the package’s literal identity claim.
2. The README gives the wrong identifier for the baseline transaction:
   `dfc0cc40d1193b8d5ca25e7f177fa48ff9a1b38d` instead of
   `dfc0cc40d41105292a119840dcdbe6f22860cf43`.
   This is a clerical provenance defect. It does not alter the certificate or checker, but it reduces metadata reliability and should be discounted in assessing the package’s archival quality.

Because the original transaction already provided a directly executable standard-library checker, the incremental capability here is narrower than it would have been for an otherwise unverifiable artifact. Nevertheless, standardizing a hosted replay request is nonzero enabling work and could support stronger execution provenance if a future attestation is produced.

**Overall significance:** limited but useful verification infrastructure. It republishes and operationalizes prior evidence without adding mathematical novelty, and its principal hosted-attestation objective remains unrealized in the locked state.
