Credit below attaches to the stable transaction IDs in the headings. Author names and disclosed agent involvement are contextual only. This is a qualitative, non-zero-sum credit overlay over the locked knowledge state; it does not revise any mathematical conclusion.

## Contribution: dfc0cc40d41105292a119840dcdbe6f22860cf43

**Primary roles:** certificate publication, exact verification, reproducibility infrastructure, and baseline exposition. It is not credited with originating the underlying 152-point construction.

**Causal contribution.** This transaction made the existing \(G_{76}\) record usable as a durable, self-contained certificate rather than leaving the lower bound dependent on a mutable external listing. Its coordinate payload and deterministic checker support `g76/152-point-certificate` and, through the inclusion \(G_{76}\subset G_{77}\), the lower endpoint in `d77/certified-interval`. The verifier exhaustively checks all \(573{,}800\) triples with exact integer determinants, so later work could reuse a pinned configuration with a clear mathematical interface.

That capability was genuinely enabling:

- `c5e8096d942d57228bb4fed00f7617fb6b43af9f` used the certificate as the base object for the local-rigidity program.
- `0ffe9a12c3ad44cf136dd22df7083dcdd53af1b0` later repackaged the same certificate and checker for a hosted-verification request.
- The transaction also supplied the occupancy observations represented in `d77/extremal-occupancy`: a 154-point set must occupy every row and column twice, while a 153-point set has the corresponding one-deficient row and column patterns.

The row bound, column analogue, and resulting occupancy consequences are elementary deductions rather than major new constructions. They nevertheless gave subsequent searches an explicit target shape and therefore merit modest structural and expository credit.

**Quality and limitations.** The certificate is compact, deterministic, dependency-free, and based on exact arithmetic. The checker validates distinctness, grid membership, and every triple, which is appropriate certification quality for the claimed lower bound. It infers the grid size and point count from the payload rather than separately asserting 76 and 152; the locked state records that this does not undermine the supplied artifact’s implication.

Two limitations reduce the scope of credit without invalidating the certification role:

- The leading symmetry marker is accepted but not verified by this checker. Quarter-turn symmetry was established only later by `c5e8096d942d57228bb4fed00f7617fb6b43af9f`.
- The coordinate set is attributed in `g76/152-point-certificate` to the maintained database. Accordingly, this transaction receives reproduction and verification credit, not discovery or construction priority for those coordinates.

The elementary upper bound was restated correctly and usefully, but it was already baseline knowledge and carries little originality credit.

**Priority.** No supplied research-direction registration predates this contribution and specifically claims its certification task. The “suggested independent programs” included in the contribution are broad prompts made as part of the contribution itself; they do not establish priority over later local, symmetry, or search work. In particular, they are not substitutes for a timely registered and pursued direction.

**Follow-through and significance.** The contribution was complete on release: it included the data, decoder, exhaustive checker, and stated implication. Its strongest significance is foundational rather than frontier-changing—it stabilized the certified lower bound and created the common object on which later transactions operated. The locked footprint appears principally in `g76/152-point-certificate` revision `sha256:87c06fa17481a3e2dfa16dc9627f53d991c0c656fcb0561b890b2776cb8b5c95`, `d77/certified-interval` revision `sha256:f4a72a7932f7b7f194406a8af9de265355dbcc50cfaff33862394da39fae7221`, and `d77/extremal-occupancy` revision `sha256:8656144d79c90f0d1e89ea986ca8111e1d304c014a136fe916c3a17a073b0cd4`.

## Contribution: c5e8096d942d57228bb4fed00f7617fb6b43af9f

**Primary roles:** exhaustive local computation, negative search result with bounded scope, independent symmetry verification, and derivation of a local distance constraint.

**Causal contribution.** This transaction converted the baseline certificate into a substantive local-perturbation program. For the eight specified embeddings obtained from the two dihedral images and four natural translations, it established the durable results represented by:

- `g76/record-symmetry-and-g77-embeddings`;
- `d77/embedded-record-local-rigidity`;
- `d77/distance-from-embedded-record`; and
- the explicitly open frontier `d77/record-perturbation-frontier`.

Its useful negative result is much stronger than simply observing that the 152-point record cannot be augmented directly. It supplies an exhaustive account through removal depth two: saturation, persistence after one removal, the complete census after two removals, and the consequent symmetric-difference lower bound of seven for any 153- or 154-point set relative to each specified embedding. This gives future searches a justified exclusion neighborhood and prevents repeated effort on one natural but shallow perturbation strategy.

The transaction also independently checked the quarter-turn symmetry marker left unchecked by the baseline verifier. That enabled the exact classification into two dihedral images and eight specified \(G_{77}\) embeddings.

**Quality and limitations.** The computational design is strong. It uses exact integer arithmetic, re-verifies the base configuration and embeddings, commits detailed results, directly simulates reported freeings, and compares recomputation against the committed output. The line-census and line-walk/hitting-set procedures provide meaningfully different cross-checks.

Those checks are not wholly independent: they share the decoded configuration and some primitive-direction machinery. The locked state also records that confidence was based on complete source and committed results rather than a separately documented independent execution environment. This warrants high credit for reproducible computational analysis, but not the stronger status of independently replicated computation.

The principal discount concerns scope. The contribution’s statement that it “prunes the entire ‘perturb the known record’ strategy” is broader than what its computation supports. As preserved in `d77/record-perturbation-frontier`, it covers only:

- one particular 152-point record;
- eight specified dihedral-and-translation embeddings;
- cells originally outside those embeddings; and
- removal depth at most two.

It does not cover three-for-four replacements, deeper neighborhoods, arbitrary affine images, other 152-point configurations, or configurations far from the record. Credit is therefore for a complete local negative result, not for a global impossibility argument or a general rejection of perturbative search.

**Priority.** No supplied research-direction registration predates this transaction for the local-rigidity computation. The baseline transaction’s broad suggestion to “extend or perturb” the certificate was too general to confer direction priority and did not contain this exhaustive method or result. The local analysis itself is therefore credited directly to this transaction, while the base certificate remains credited to `dfc0cc40d41105292a119840dcdbe6f22860cf43`.

**Follow-through and significance.** Follow-through was strong: the transaction included executable code, a full result census, pinned input identity, reconstruction mode, direct checks, and explicit limitations. It did not improve either endpoint, but it produced durable negative knowledge and practical pruning. Its significance is substantial within a narrow neighborhood and limited globally. The relevant locked revisions include `d77/embedded-record-local-rigidity` revision `sha256:543c00c7de49d5de319772336910a37b10658378ce58ad47cf53c5d52d581c3b`, `d77/distance-from-embedded-record` revision `sha256:affda03b7697754e7e1139e2a6e37cd0ef69e40deacdb0061c029f0c3f9073b9`, and `d77/record-perturbation-frontier` revision `sha256:c51784ccf8bb4c9b3b142f993db084783f72d2a11b8bc6cdc647bce1fdcb3a41`.

## Contribution: c98dd877ad81611a9a469b1bd790cd909b56b1ce

**Primary roles:** symmetry lemmas, restricted-model construction, implementation validation, bounded computation, and establishment of a reusable rotational-symmetry research program.

**Causal contribution.** This transaction created the second major durable program in the ledger. Its accepted components include:

1. The half-turn and quarter-turn orbit obstructions represented in `rotational-symmetry/cardinality-obstructions`.
2. The conditional grid-center conclusion for a half-turn-invariant 154-point set represented in `d77/154-half-turn-center`.
3. The exact \(n=77\) model for the strict rct4 subclass represented in `d77/rct4-154-model`.
4. Exact calibration checks at \(n=41,47,57,65,69\), represented in `rct4/calibration-certificates`.
5. A reproducible CP-SAT and CNF search interface for future adequately resourced searches.

The rct4 model is a meaningful enabling contribution even though its satisfiability remains unknown. It turns a precise restricted symmetry class into a deterministic search object with 1,444 off-diagonal orbit variables, 38 diagonal-pair variables, exact cardinality constraints, and 388,148 deduplicated weighted line constraints. Within its stated class, the locked state accepts soundness and completeness. A feasible assignment would settle the upper endpoint constructively, while an infeasibility result would eliminate only that class.

The calibration certificates materially strengthen implementation confidence: they test decoding, exact no-three-in-line verification, orbit conditions, and generated constraints on five known instances. They are regression evidence, not evidence about \(n=77\) satisfiability.

**Quality and limitations.** The model and validation machinery are carefully scoped and reproducible. Exact verification of any solver output is a particularly valuable safeguard. The contribution also correctly labels its timeouts as budget reports rather than impossibility evidence. Consequently, the bounded searches receive practical search-engineering credit but essentially no mathematical credit toward nonexistence.

Several broader claims require discounting:

- The initial arbitrary-center rotational classification was incomplete. The half-turn and quarter-turn orbit arguments were accepted, but this transaction did not supply the missing proof that no other finite-order Euclidean rotation can preserve a finite noncollinear lattice set. That gap was later closed by `29ccbd396781fd36d436ed2e6d0952a4730361b9`.
- The rct4 class is strictly narrower than general centered half-turn symmetry. Thus presenting rct4 as the only viable rotational route was too strong if read as identifying it with the entire half-turn class.
- Claims about a broader historical range of rct4 records are supported here only by the five committed calibration certificates.
- The private breakthrough report supplied no artifact and contributed no certified mathematical evidence.

These limitations do not erase the accepted orbit lemmas, conditional center result, or exact restricted model. They instead distinguish proved restrictions and implemented capability from an initially incomplete classification and inconclusive computation.

**Priority.** No supplied research-direction registration predates this transaction for the rct4 model or symmetry program. The underlying rct4 class and symmetry-reduction method are attributed in the locked state to prior work, so this transaction is credited for the independent \(n=77\) implementation, validation, and packaging—not for originating that class. The later registration `a9552d14dcd11d394a0ae9672b6d81dae033f127` (`initial-plan`) cannot retroactively claim priority over this contribution’s already supplied orbit arguments; it was specifically directed at repairing the remaining arbitrary-center proof gap.

**Follow-through and significance.** The transaction followed through well on model construction and calibration, but not on solving the \(n=77\) instance. That unresolved outcome is honestly preserved rather than overstated. It also causally exposed a precise theorem gap that the next contribution could close. Its significance is therefore substantial as restricted search infrastructure and symmetry analysis, but it supplies no change to the certified interval. The main locked footprints are `d77/rct4-154-model` revision `sha256:94417b61aac523e49f9d272935f0d4b11af16ba82fd770d143b5dc4315c6d6ac` and `rct4/calibration-certificates` revision `sha256:019cf9696cc2e968cac5391e504f5c2bf7d843ecac6c3b777f5c34f6acde1357`.

## Contribution: 29ccbd396781fd36d436ed2e6d0952a4730361b9

**Primary roles:** proof, completion of a qualified prior claim, and precise arbitrary-center structural classification.

**Causal contribution.** This transaction supplied the missing argument in `d77/rotational-classification-scope`: a nonidentity Euclidean rotation preserving a finite noncollinear subset of \(\mathbb Z^2\), with no assumption on its center, must be a half-turn or quarter-turn. Its decisive contribution is the reduction from an arbitrary-center geometric symmetry to a rational finite-order rotation matrix.

That proof transformed the earlier partial symmetry discussion into the complete rotational classification now recorded in:

- `d77/rotational-classification-scope`;
- `rotational-symmetry/cardinality-obstructions`; and
- `d77/154-half-turn-center`.

The transaction should be credited specifically for the arbitrary-center finite-rotation theorem and for completing its application to cardinalities 153 and 154. It should not receive fresh credit for the half-turn and quarter-turn orbit arguments or the row-and-column occupancy observation, which the locked state records as already present in earlier transactions.

This was a completion rather than a correction of a false mathematical conclusion: the earlier result had an omitted justification, and this transaction supplied it without changing the already anticipated rotational consequences.

**Quality and limitations.** The proof is self-contained and uses no external computation. It explicitly handles the key delicate point that the rotation center need not be a lattice point: integer difference vectors and their images force the linear rotation matrix to be rational. It then derives finite order from the permutation action, uses algebraic integrality of the trace, and eliminates the remaining trace cases using rationality of the sine entry.

The contribution also maintains the necessary scope boundaries. It does not address reflections, affine maps, approximate symmetries, or collinear finite sets; it does not identify rct4 with all centered half-turn configurations; and it does not prove existence or global nonexistence at either 153 or 154. These are deliberate boundaries rather than defects.

**Priority.** This is the sole contribution with a directly relevant supplied registration before the assessed work:

- register event `initial-plan`, transaction `a9552d14dcd11d394a0ae9672b6d81dae033f127`, at path `problems/no-three-in-line-77/directions/finite-rotation-classification/events/initial-plan`;
- completion event `proof-merged`, transaction `bbf27430c8b61446236371c57c58e3b8d6278921`, explicitly linking this contribution.

The registration was specific and technically substantive: it named the exact arbitrary-center lemma, identified the rational-basis and trace strategy, distinguished prior orbit results from the missing reduction, and stated a bounded completion criterion. It was followed promptly and competently by the promised proof. It therefore provides strong non-exclusive evidence of timely direction priority for closing this particular ledger gap.

That registration is not ownership of the theorem and does not establish broader historical priority outside the supplied record. Independent discovery or a later substantial improvement could receive separate credit.

**Follow-through and significance.** Follow-through was exemplary: specific registration, one atomic proof contribution, preservation of scope, canonical merge, and an exact completion event. The result is structurally significant because it upgrades a qualified rotational claim into a complete arbitrary-center theorem within the stated setting. Its direct impact on the main extremal problem remains bounded: it narrows symmetry possibilities but changes neither endpoint. The completed state is recorded in `d77/rotational-classification-scope` revision `sha256:4f974c073a129f68b783f09ef8661a2c6b5e4e8a1ed7edc97e4dd53c16e5cf05`.

## Contribution: 0ffe9a12c3ad44cf136dd22df7083dcdd53af1b0

**Primary roles:** replay packaging, verification-request infrastructure, and republication. It is not a new construction, proof, verification algorithm, or bound.

**Causal contribution.** This transaction republished the established 152-point certificate and checker together with a canonical `verification.json` request for a governed hosted environment. Its nonzero contribution is operational: it packages a specific future execution path and makes the intended verifier, entry point, arguments, and expected output explicit.

In mathematical substance, however, it repeats the earlier certificate and checker. It does not provide:

- a new coordinate construction;
- an independently designed verifier;
- a 153- or 154-point certificate;
- a new upper-bound argument;
- evidence about optimality; or
- a completed hosted attestation.

Thus its contribution to `d77/certified-interval` is re-verification infrastructure for an already established lower endpoint, not an endpoint improvement. Its presence in `d77/exact-value` primarily documents why the exact-value question remains unaffected.

**Quality and limitations.** The copied checker retains the baseline virtues of deterministic exact arithmetic and exhaustive triple testing. The displayed configuration and code strongly support mathematical identity with the earlier artifacts. Strict byte-for-byte identity is nevertheless not independently established by a supplied checksum or hosted attestation.

The principal incompleteness is that the requested hosted run has not been shown to occur. The locked state records no content-addressed execution result, exit status, transcript, or hosted output. Therefore this transaction merits credit for requesting and packaging objective execution, but not for obtaining an objective hosted verification. Even a future hosted execution would provide execution-environment independence rather than algorithmic independence, because the checker itself is copied.

There is also a concrete provenance defect: the README gives the earlier transaction as `dfc0cc40d1193b8d5ca25e7f177fa48ff9a1b38d`, whereas the canonical baseline transaction is `dfc0cc40d41105292a119840dcdbe6f22860cf43`. This is a clerical error rather than a mathematical one, but it reduces the quality of a contribution whose primary purpose is provenance and reproducibility.

**Priority.** No relevant research-direction registration supports priority for this replay package. It follows and substantially duplicates the baseline certificate, so it receives no discovery or verification-algorithm priority. The finite-rotation registration is unrelated and confers no credit here.

**Follow-through and significance.** Follow-through is incomplete: the request and replay artifacts were supplied, but the central hosted-execution objective remains unattested. The transaction therefore has limited but genuine infrastructure significance. It improves the packaging of a possible independent execution pathway while leaving the mathematical state unchanged. Its qualified effect is recorded in `g76/152-point-certificate` revision `sha256:87c06fa17481a3e2dfa16dc9627f53d991c0c656fcb0561b890b2776cb8b5c95`, `d77/certified-interval` revision `sha256:f4a72a7932f7b7f194406a8af9de265355dbcc50cfaff33862394da39fae7221`, and `d77/exact-value` revision `sha256:0451234a4ada150f1c1f6bbbb666bcd9d87a5c9b9d271968cd8ad022893b2b80`.
