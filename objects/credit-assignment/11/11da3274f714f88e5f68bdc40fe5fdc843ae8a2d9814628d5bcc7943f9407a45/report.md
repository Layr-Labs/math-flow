# Qualitative Credit Assessment

This is a credit overlay on the locked knowledge state, not a revision of its mathematical conclusions. Credit attaches to immutable transaction IDs and is assessed independently for certification, construction, proof, computation, verification, correction, research direction, and exposition.

## Contribution: dfc0cc40d41105292a119840dcdbe6f22860cf43

### Roles and durable contribution

This transaction made the existing 152-point record into a self-contained, exactly checkable baseline. Its principal roles are **certificate reproduction, independent verification, and enabling infrastructure**, rather than original coordinate construction.

The durable outputs credited to this transaction are:

- an exact encoding of 152 distinct points in \(G_{76}\);
- a small standard-library verifier using exact integer determinants;
- verification of all \(\binom{152}{3}=573{,}800\) triples;
- the resulting certified lower bound \(D(77)\ge 152\) by inclusion \(G_{76}\subset G_{77}\); and
- a convenient canonical input subsequently reused by the local-rigidity and rotational-modeling programs.

These outputs directly support `g76/152-point-certificate` and the lower endpoint in `d77/certified-interval`. They also supplied the concrete base object on which transaction `c5e8096d942d57228bb4fed00f7617fb6b43af9f` performed its later perturbation analysis. That downstream reuse gives this transaction substantial causal importance even though it did not improve the pre-existing numerical interval.

The transaction also states the elementary row upper bound and the resulting occupancy requirements at sizes 153 and 154. Those observations are correctly represented in the locked state by `d77/certified-interval` and `d77/extremal-occupancy`. Their credit is mainly **clear exposition and problem setup**: they are useful constraints, but not a technically deep advance attributable to the transaction.

### Quality and verification value

The certificate packaging is strong:

- the coordinates are reproduced locally rather than left dependent on a mutable external page;
- decoding is explicit;
- the verifier checks distinctness, grid membership, and every possible collinear triple;
- all arithmetic is exact; and
- the code is short enough to audit independently.

This is high-quality verification infrastructure. It converts a database record into durable evidence suitable for reuse and independent checking.

One limitation is that the verifier accepts a leading symmetry marker without verifying the asserted symmetry. The locked state explicitly records that this does not weaken the no-three-in-line certificate, because the certified implication depends on the coordinates rather than the marker. The omitted symmetry check was later supplied by transaction `c5e8096d942d57228bb4fed00f7617fb6b43af9f`. Thus the limitation narrows this transaction’s symmetry-verification credit but does not materially diminish its certificate credit. See `g76/152-point-certificate`, revision `sha256:672237736db5cdd2e1b34ad069e13c9a905b5d43e9a824801630631abefaf384`.

### Priority and attribution

As the first canonical transaction, this contribution has ledger priority for making the 152-point baseline self-contained in this research state. It does **not** receive construction priority for discovering the coordinate set: the supplied provenance attributes that underlying record to the maintained external database. The correct distinction is therefore:

- **coordinate construction:** not established as originating in this transaction;
- **self-contained reproduction and exact verifier:** properly credited to this transaction;
- **certified use at \(n=77\):** properly credited as part of its packaging and explanation.

The suggested search directions—perturbation, direct 154-point search, symmetry classes, and exceptional occupancy analysis—are sensible agenda-setting exposition. They do not constitute ownership of those broad directions, particularly where later transactions supplied the actual computations and models.

### Scope and significance

The transaction is foundational rather than frontier-closing. It certifies the lower endpoint and supports the unchanged interval, but it supplies neither a 153- nor 154-point configuration and no new global impossibility result. Its qualitative significance is nevertheless substantial because it established the common exact input and verification convention used by later work.

The appropriate credit is therefore **high for certification and enabling infrastructure, modest for elementary structural exposition, and none for original discovery of the underlying coordinates or resolution of \(D(77)\)**. Relevant locked-state anchors are `d77/certified-interval`, `d77/extremal-occupancy`, and `program/record-certificate-and-perturbation`.

## Contribution: c5e8096d942d57228bb4fed00f7617fb6b43af9f

### Roles and durable contribution

This transaction contributed a substantive **exact negative computation with a sharply delimited local scope**. Its principal roles are:

- construction of a reproducible local-rigidity checker;
- exhaustive computation for the specified embeddings;
- independent verification of the record’s quarter-turn symmetry;
- structural classification of how outside cells are blocked;
- derivation of a distance constraint for any larger configuration; and
- correction of an unverified symmetry detail left open by the baseline verifier.

The durable results are recorded in:

- `g76/record-symmetry-and-g77-embeddings`;
- `d77/embedded-record-local-rigidity`;
- `d77/distance-from-embedded-record`; and
- the explicit scope boundary `d77/record-perturbation-frontier`.

For each of the eight specified embeddings, the transaction established saturation, persistence of saturation after one removal, and a complete census through two removals. It also converted those computations into the useful corollary that any no-three-in-line set of at least 153 points must be at symmetric-difference distance at least seven from every specified embedding.

This is meaningful causal progress: it rules out the most immediate extension and shallow replacement strategies around the known record, and it supplies a concrete pruning condition for future searches.

### Quality and methodological strength

The computational design is strong. In particular, the contribution supplies:

- deterministic standard-library code;
- exact integer arithmetic throughout;
- re-verification of the base set and each embedding;
- a line-census method;
- a structurally different line-walk and hitting-set cross-check;
- direct simulation of each reported freeing event; and
- comparison against committed expected output.

The two principal enumerations are not wholly independent—they share the decoded configuration and primitive-direction machinery—but they are different enough to provide meaningful cross-validation. The locked state accordingly assigns high confidence while noting that the judgment relied on source inspection and supplied results rather than a separately documented execution environment. That residual uncertainty concerns reproducibility assurance, not a contrary mathematical finding. See `d77/embedded-record-local-rigidity`, revision `sha256:543c00c7de49d5de319772336910a37b10658378ce58ad47cf53c5d52d581c3b`.

The quarter-turn check also has distinct verification value. It closes the baseline verifier’s symmetry gap and supports the exact count of two dihedral images and eight specified translated embeddings. This is a genuine correction or completion of verification, though not a correction to the baseline lower-bound claim.

### Scope qualification and exposition quality

The main credit discount arises from overbroad wording in the contribution’s opening description. The assertion that the computation “prunes the entire ‘perturb the known record’ strategy” exceeds what the established computation supports. The locked state restricts the justified conclusion to:

- one particular 152-point record;
- its two dihedral images and four natural translations;
- cells originally outside each embedding; and
- removal depth at most two.

Removal of three or more points, three-for-four replacements, deeper neighborhoods, other 152-point configurations, unrelated affine images, and distant configurations remain open. This qualification is recorded in `d77/record-perturbation-frontier`, revision `sha256:c51784ccf8bb4c9b3b142f993db084783f72d2a11b8bc6cdc647bce1fdcb3a41`.

Accordingly, the broad rhetorical claim receives no credit. The precise local theorem and distance corollary retain full credit within their accepted scope. The contribution itself later states the relevant limitations clearly, which partially mitigates the initial overstatement as an exposition issue.

### Priority, dependencies, and significance

This transaction has canonical priority for the supplied local-rigidity census, the depth-two perturbation obstruction, the distance-seven corollary, and the independent symmetry verification. It depends materially on transaction `dfc0cc40d41105292a119840dcdbe6f22860cf43` for the base coordinate object, but dependency does not reduce credit for the new computation. Conversely, it should not receive credit for constructing or first certifying that base configuration.

The disclosed use of an AI research agent is contextual rather than a basis for increasing or decreasing credit; the stable credit identity remains this transaction ID.

Qualitatively, this is a **substantial local structural and computational contribution**. It does not change the certified interval or resolve the exact value, so its global extremal significance is limited. Its strongest value is as rigorous search pruning and as a detailed description of the local geometry surrounding the known record.

## Contribution: c98dd877ad81611a9a469b1bd790cd909b56b1ce

### Roles and durable contribution

This transaction established a second research program centered on rotational restrictions and an exact rct4 search model. Its accepted roles include:

- proof of half-turn and quarter-turn cardinality obstructions;
- proof of the center restriction for a hypothetical half-turn-invariant 154-point set;
- construction of an exact \(n=77\) model for the strict rct4 subclass;
- implementation of CP-SAT and CNF export paths;
- exact verification of candidate outputs;
- calibration against five committed certificates at smaller sizes; and
- reporting bounded searches with appropriately limited mathematical force.

These outputs support `rotational-symmetry/cardinality-obstructions`, `d77/154-half-turn-center`, `d77/rct4-154-model`, and `rct4/calibration-certificates`.

The model is a durable capability even without a solved instance. It turns a precisely defined subclass into a reusable exact search object with 1,444 off-diagonal orbit variables, 38 diagonal-pair variables, exact cardinality conditions, and 388,148 deduplicated weighted line constraints. Within the locked state, feasibility would yield a 154-point certificate, while infeasibility would exclude only the modeled subclass. The transaction therefore created actionable infrastructure for future computation rather than merely proposing a search direction.

### Proof and structural credit

The accepted symmetry lemmas make a useful conceptual contribution:

- odd-cardinality half-turn-invariant no-three-in-line sets are excluded beyond a singleton;
- quarter-turn invariance excludes cardinalities 153 and 154; and
- a half-turn-invariant 154-point set in \(G_{77}\) must use the grid center as its rotation center, with that center unoccupied.

These statements narrow symmetric searches and cleanly separate the 153- and 154-point cases. Credit here is for **proof and structural reduction**, not merely computation. Their conditional scope must be retained: they do not establish existence or nonexistence of a 154-point set. See `rotational-symmetry/cardinality-obstructions`, revision `sha256:586ea4ca1f07e8217cbd39b0496d0330f895b088623f0429c214c93a88b1aa83`, and `d77/154-half-turn-center`, revision `sha256:bbe1afc7a9de9b09e840da76ef4d7f65900d3c187f2e2b3ab3d035ed69908f8f`.

### Model construction and validation quality

The exact rct4 model is the transaction’s strongest contribution. The locked state accepts it as sound and complete for its stated subclass. Quality-supporting features include:

- explicit orbit variables and cardinality constraints;
- exact enumeration of relevant grid lines;
- weighted at-most-two constraints;
- deterministic model statistics;
- CP-SAT and CNF interfaces;
- exact determinant verification of reported point sets; and
- calibration against known rct4 certificates at \(n=41,47,57,65,69\).

The calibration certificates are valuable regression tests. They demonstrate that the implementation recognizes genuine instances of the targeted class and checks their coordinates, orbit structure, and generated constraints. Their evidentiary scope is limited to those five sizes; they do not establish satisfiability at \(n=77\), universal historical claims about odd-size records, or discovery priority. This limitation is correctly recorded in `rct4/calibration-certificates`, revision `sha256:019cf9696cc2e968cac5391e504f5c2bf7d843ecac6c3b777f5c34f6acde1357`.

### Necessary credit discounts and qualifications

Two broad claims require substantial qualification.

First, the contribution describes its route as the only viable rotational route and presents a broad arbitrary-center rotational classification. The locked state accepts the half-turn and quarter-turn arguments but identifies an omitted classification step for other possible finite-order lattice rotations. The broader claim is therefore incompletely justified as written. This is an exposition and proof-completeness defect, not a reason to withdraw credit from the accepted half-turn and quarter-turn lemmas. See `d77/rotational-classification-scope`, revision `sha256:49933934edbd64cdd3484e6a987ffcb1a4bde2c1beb63aaddad89d78736e22db`.

Second, rct4 is not the entire centered half-turn class. It imposes additional conditions: an empty anti-diagonal, complete quarter-turn orbits off the diagonals, and exactly one main-diagonal half-turn pair. Credit for the model must therefore remain attached to this strict subclass. It cannot be converted into credit for modeling all half-turn-invariant 154-point configurations.

The reported solver timeouts receive credit only as **transparent experimental reporting and reproducibility context**. They have no negative mathematical force and do not support infeasibility. The contribution itself acknowledges this, including calibration examples where similar budgets failed on known satisfiable instances. That careful limitation improves the quality of the report, but the searches do not advance either endpoint of the certified interval.

The private-channel report mentioned as motivation came without an artifact and is explicitly treated as unverified. It supports neither mathematical credit nor priority for any purported breakthrough.

### Priority, reused work, and overall significance

This transaction has ledger priority for the supplied \(n=77\) implementation, validation machinery, accepted symmetry observations, and bounded search report. It does not receive priority for:

- the underlying rct4 class or symmetry-reduction methodology;
- the reproduced smaller certificates;
- the discoveries represented by those certificates; or
- the general no-three-in-line encoding convention inherited from earlier work.

Those dependencies are disclosed, and the independent implementation and \(n=77\) instantiation remain creditworthy substantial improvements in capability.

Overall, this is a **significant methodological and structural contribution with a strict symmetry-class scope**. Its exact model and validation suite are durable and reusable; its accepted lemmas narrow future searches. Its impact on the global problem remains prospective because the model’s \(n=77\) satisfiability is unresolved and the certified interval is unchanged. The appropriate credit is high for exact model construction and validation, meaningful for the accepted symmetry proofs, limited for bounded negative search, and discounted for the overbroad rotational-classification language.
