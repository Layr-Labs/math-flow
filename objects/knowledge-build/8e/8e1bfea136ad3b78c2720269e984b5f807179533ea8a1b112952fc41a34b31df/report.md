# Knowledge-Formation Report

The supplied conflict registry is empty, and no reconciliation outcomes are present. Accordingly, no active-dispute node is required. Qualified and unresolved findings are preserved as qualified or open knowledge nodes without choosing conclusions beyond the immutable judgments.

The hierarchy establishes two durable research programs:

1. certification and local perturbation of the known \(152\)-point \(G_{76}\) record;
2. rotational-symmetry restrictions and the rct4 search model.

The exact-value question, certified interval, and general extremal occupancy conditions remain directly under the root because they apply across research programs.

## Node: root

- **Type:** root
- **Parent:** none
- **Status:** active
- **Title:** Research state for no-three-in-line at grid size 77

For

\[
G_{77}=\{0,\ldots,76\}^2,
\]

the exact maximum \(D(77)\) remains unresolved. The complete certified global state is

\[
152\le D(77)\le154,
\qquad
D(77)\in\{152,153,154\}.
\]

No supplied judgment establishes a \(153\)- or \(154\)-point configuration, excludes either size globally, or improves either endpoint.

Two durable research programs are established:

1. **Known-record certification and local perturbation:** exact certification of the \(152\)-point \(G_{76}\) record, its specified embeddings in \(G_{77}\), and rigidity under removal of at most two embedded points.
2. **Rotational symmetry and rct4 modeling:** general orbit obstructions, the center restriction for half-turn-invariant \(154\)-point sets, and an exact model for a strict rct4 subclass.

General global facts remain outside these programs:

- the unresolved exact-value question;
- the certified interval \(152\le D(77)\le154\);
- necessary row-and-column occupancy patterns at cardinalities \(153\) and \(154\).

There are no supplied conflict records and therefore no active mathematical dispute nodes. The qualified rotational-classification claim and the open rct4 satisfiability question remain explicitly qualified or unresolved rather than being treated as settled.

### Provenance

This state is attributed to the following immutable judgments:

- `sha256:a470e4a9c0903097d9c860badaa8976cf32ed5336c154f11d8fad980d401f74e`
- `sha256:71fbde8d269728a92be52f6401e857230043ee6938c45f810c32308d88fb9927`
- `sha256:d24a70c16a08ff85401e969cfe12d8f8253056bb8d75e469ec226eba7a3b44c5`

Their subject transactions are:

- `dfc0cc40d41105292a119840dcdbe6f22860cf43`
- `c5e8096d942d57228bb4fed00f7617fb6b43af9f`
- `c98dd877ad81611a9a469b1bd790cd909b56b1ce`

## Change: root

The previous root stated that no research programs existed. The immutable judgments now support a global certified state and two independent, durable programs, so the root is expanded while retaining global bounds and the exact-value question at root level.

## Node: d77/exact-value

- **Type:** question
- **Parent:** `root`
- **Status:** open
- **Title:** Exact value of \(D(77)\)

The exact value of \(D(77)\) is unresolved. The supplied judgments support only

\[
D(77)\in\{152,153,154\}.
\]

None of the judged transactions supplies:

- a \(153\)-point coordinate certificate;
- a \(154\)-point coordinate certificate;
- a global impossibility proof for \(153\) points;
- a global impossibility proof for \(154\) points; or
- any other upper- or lower-bound improvement.

The local rigidity results concern only eight specified embeddings of one \(152\)-point record. They leave other \(152\)-point configurations and configurations sufficiently distant from those embeddings unconstrained.

The rotational-symmetry work also does not resolve the exact value. In particular, the rct4 model concerns only a strict subclass of centered half-turn-invariant \(154\)-point sets, and its \(n=77\) satisfiability remains unknown.

### Provenance

- Primary judgment `sha256:a470e4a9c0903097d9c860badaa8976cf32ed5336c154f11d8fad980d401f74e`, subject `dfc0cc40d41105292a119840dcdbe6f22860cf43`
- Primary judgment `sha256:71fbde8d269728a92be52f6401e857230043ee6938c45f810c32308d88fb9927`, subject `c5e8096d942d57228bb4fed00f7617fb6b43af9f`
- Primary judgment `sha256:d24a70c16a08ff85401e969cfe12d8f8253056bb8d75e469ec226eba7a3b44c5`, subject `c98dd877ad81611a9a469b1bd790cd909b56b1ce`

## Change: d77/exact-value

This new global node records the common unresolved conclusion of all three judgments without placing the central problem inside either specialized program.

## Node: d77/certified-interval

- **Type:** result
- **Parent:** `root`
- **Status:** active
- **Title:** Certified bounds for \(D(77)\)

The current certified interval is

\[
\boxed{152\le D(77)\le154}.
\]

The lower bound is supported by an exact \(152\)-point no-three-in-line certificate in \(G_{76}\). Direct inclusion

\[
G_{76}\subset G_{77}
\]

places the same configuration in \(G_{77}\), giving \(D(77)\ge152\).

The upper bound follows from the \(77\) horizontal rows of \(G_{77}\). A no-three-in-line set contains at most two selected points on each row, so its cardinality is at most

\[
2\cdot77=154.
\]

The judgments support this interval with high confidence. No later judged result in the supplied material changes either endpoint.

### Provenance

- Primary judgment: `sha256:a470e4a9c0903097d9c860badaa8976cf32ed5336c154f11d8fad980d401f74e`
- Subject and certificate evidence: `dfc0cc40d41105292a119840dcdbe6f22860cf43`
- The unchanged interval is also affirmed by judgments:
  - `sha256:71fbde8d269728a92be52f6401e857230043ee6938c45f810c32308d88fb9927`
  - `sha256:d24a70c16a08ff85401e969cfe12d8f8253056bb8d75e469ec226eba7a3b44c5`

## Change: d77/certified-interval

This global node is added because the baseline certificate and elementary row bound establish durable cross-program bounds that were absent from the previous knowledge state.

## Node: d77/extremal-occupancy

- **Type:** lemma
- **Parent:** `root`
- **Status:** active
- **Title:** Necessary row-and-column occupancy at sizes 153 and 154

Any no-three-in-line subset of \(G_{77}\) has at most two points in each row and at most two points in each column.

Consequently:

- A valid \(154\)-point set must contain exactly two points in every one of the \(77\) rows and exactly two points in every one of the \(77\) columns.
- A valid \(153\)-point set must contain exactly two points in \(76\) rows and one point in the remaining row. It must likewise contain exactly two points in \(76\) columns and one point in the remaining column.

These are necessary conditions only. They establish neither existence nor nonexistence at either cardinality.

### Provenance

- Primary judgment: `sha256:a470e4a9c0903097d9c860badaa8976cf32ed5336c154f11d8fad980d401f74e`
- Subject and evidence transaction: `dfc0cc40d41105292a119840dcdbe6f22860cf43`

## Change: d77/extremal-occupancy

This node is added as a general structural fact applicable to every hypothetical \(153\)- or \(154\)-point configuration, independent of the two specialized programs.

## Node: program/record-certificate-and-perturbation

- **Type:** program
- **Parent:** `root`
- **Status:** active
- **Title:** Certification and local perturbation of the known \(G_{76}\) record

This program studies the supplied \(152\)-point no-three-in-line configuration in \(G_{76}\), its specified placements in \(G_{77}\), and the extent to which those placements can be locally modified.

Its current established state is:

- the \(152\)-point \(G_{76}\) configuration has an exact integer-arithmetic certificate;
- the particular record is quarter-turn invariant;
- it has two distinct dihedral images and eight distinct specified embeddings in \(G_{77}\) after the four translations in \(\{0,1\}^2\);
- each specified embedding is saturated in \(G_{77}\);
- removing one embedded point frees no originally outside cell;
- removing two embedded points frees at most one originally outside cell, with a complete exact census;
- every no-three-in-line set of size at least \(153\) is at symmetric-difference distance at least seven from each specified embedding.

The program does not cover arbitrary affine images, other \(152\)-point configurations, or perturbations requiring removal of three or more embedded points. It therefore supplies local rigidity, not a global upper-bound improvement.

The underlying coordinate set is attributed in the judgments to Achim Flammenkamp’s maintained database. Robert is credited for making the baseline certificate self-contained and independently checkable, rather than for originating that coordinate construction. The local rigidity analysis, code, and text are attributed to an AI research agent working at Robert Raynor’s request.

### Provenance

- Baseline judgment: `sha256:a470e4a9c0903097d9c860badaa8976cf32ed5336c154f11d8fad980d401f74e`
- Local-rigidity judgment: `sha256:71fbde8d269728a92be52f6401e857230043ee6938c45f810c32308d88fb9927`
- Subject transactions:
  - `dfc0cc40d41105292a119840dcdbe6f22860cf43`
  - `c5e8096d942d57228bb4fed00f7617fb6b43af9f`

## Change: program/record-certificate-and-perturbation

This durable program is introduced to group the exact base certificate, specified embeddings, local rigidity results, and the remaining depth-three-or-greater perturbation frontier without creating event-shaped nodes.

## Node: g76/152-point-certificate

- **Type:** result
- **Parent:** `program/record-certificate-and-perturbation`
- **Status:** active
- **Title:** Exact 152-point no-three-in-line certificate in \(G_{76}\)

An exact computational certificate supports the existence of a \(152\)-point subset of

\[
G_{76}=\{0,\ldots,75\}^2
\]

containing no three collinear points.

The encoded payload yields two distinct points in each of the \(76\) rows. All coordinates lie in \(\{0,\ldots,75\}^2\), and the verifier checks:

- that exactly \(152\) distinct points are decoded;
- that every point belongs to \(G_{76}\); and
- that the determinant is nonzero for all
  \[
  \binom{152}{3}=573{,}800
  \]
  unordered triples.

The verification uses exact integer arithmetic.

The baseline verifier accepts a leading symmetry marker but does not itself verify quarter-turn symmetry. This does not weaken the no-three-in-line certificate, which depends only on the decoded coordinates. Quarter-turn symmetry of this particular record was separately checked in the later local-rigidity computation.

The judgments attribute the underlying coordinate set to Achim Flammenkamp’s maintained database. Robert is credited for the self-contained reproduction and independent verifier, not for originating the construction.

### Provenance

- Primary judgment: `sha256:a470e4a9c0903097d9c860badaa8976cf32ed5336c154f11d8fad980d401f74e`
- Subject and evidence transaction: `dfc0cc40d41105292a119840dcdbe6f22860cf43`
- Separate symmetry verification: judgment `sha256:71fbde8d269728a92be52f6401e857230043ee6938c45f810c32308d88fb9927`, transaction `c5e8096d942d57228bb4fed00f7617fb6b43af9f`

## Change: g76/152-point-certificate

This node is added to materialize the exact lower-bound certificate as a durable mathematical result while preserving the verifier’s symmetry-marker limitation and the supplied credit attribution.

## Node: g76/record-symmetry-and-g77-embeddings

- **Type:** result
- **Parent:** `program/record-certificate-and-perturbation`
- **Status:** active
- **Title:** Symmetry orbit and specified \(G_{77}\) embeddings of the \(G_{76}\) record

For the supplied \(152\)-point configuration \(C\subseteq G_{76}\), exact computation supports with high confidence that:

- \(C\) is invariant under the quarter-turn
  \[
  (x,y)\longmapsto(75-y,x);
  \]
- the eight symmetries of the square produce exactly two distinct dihedral images of \(C\); and
- applying each translation
  \[
  (t_x,t_y)\in\{0,1\}^2
  \]
  to those distinct images produces exactly eight distinct subsets of \(G_{77}\).

Here “specified embeddings” means only those dihedral images followed by those four natural translations of the \(76\times76\) square inside \(G_{77}\). The result does not classify unrelated affine images, other \(G_{76}\) configurations, or all \(152\)-point subsets of \(G_{77}\).

### Provenance

- Primary judgment: `sha256:71fbde8d269728a92be52f6401e857230043ee6938c45f810c32308d88fb9927`
- Subject transaction: `c5e8096d942d57228bb4fed00f7617fb6b43af9f`
- Evidence transactions:
  - `dfc0cc40d41105292a119840dcdbe6f22860cf43`
  - `c5e8096d942d57228bb4fed00f7617fb6b43af9f`

## Change: g76/record-symmetry-and-g77-embeddings

This node is added because the later exact computation independently establishes a durable symmetry-and-embedding classification for the particular certified record.

## Node: d77/embedded-record-local-rigidity

- **Type:** result
- **Parent:** `program/record-certificate-and-perturbation`
- **Status:** active
- **Title:** Saturation and removal rigidity of the eight specified embeddings

Let \(E\subseteq G_{77}\) be any of the eight specified embeddings of the supplied \(152\)-point \(G_{76}\) record.

Exact computation supports with high confidence the following complete local account.

### Saturation

Every one of the

\[
77^2-152=5{,}777
\]

cells outside \(E\) is blocked by a pair of points of \(E\). Every outside cell has at least two blocking pairs, and the total blocking incidence is \(51{,}449\) for each embedding.

Thus every specified embedding is inclusion-maximal in \(G_{77}\): no additional point can be added directly. This does not mean that the embedding has maximum possible cardinality.

### One-point removal

For every \(r\in E\), removing \(r\) makes no cell of \(G_{77}\setminus E\) addable. This assertion concerns only cells originally outside \(E\); the removed point itself can be restored.

### Two-point removal

Removing any unordered pair from \(E\) frees at most one cell that was originally outside \(E\).

For each embedding:

- exactly \(16\) unordered removal pairs free an outside cell;
- those pairs are distributed over four outside cells;
- each of those four cells is freed by four removal pairs; and
- every freeing occurs through the “two-lines-of-two” mechanism identified by the computation.

The direction census and line-walk/hitting-set enumeration provide structurally different exact cross-checks, although they share the decoded configuration and primitive-direction routine.

The judgment’s high confidence rests on deterministic standard-library code, exact integer arithmetic, complete supplied source, and committed expected output. It also records that the assessment was based on source inspection and supplied results rather than a separately documented execution environment.

### Provenance

- Primary judgment: `sha256:71fbde8d269728a92be52f6401e857230043ee6938c45f810c32308d88fb9927`
- Subject transaction: `c5e8096d942d57228bb4fed00f7617fb6b43af9f`
- Evidence transactions:
  - `dfc0cc40d41105292a119840dcdbe6f22860cf43`
  - `c5e8096d942d57228bb4fed00f7617fb6b43af9f`

## Change: d77/embedded-record-local-rigidity

This node consolidates the mutually dependent saturation, one-removal, and exhaustive two-removal findings into one durable local-rigidity result for the same eight embeddings.

## Node: d77/distance-from-embedded-record

- **Type:** corollary
- **Parent:** `program/record-certificate-and-perturbation`
- **Status:** active
- **Title:** Distance constraint from every specified record embedding

Let \(E\) be any one of the eight specified \(152\)-point embeddings, and let \(S\subseteq G_{77}\) be no-three-in-line.

The supported local computations imply:

\[
|E\setminus S|\le2
\quad\Longrightarrow\quad
|S\setminus E|\le1
\quad\text{and}\quad
|S|\le152.
\]

Consequently, every no-three-in-line set \(S\) with \(|S|\ge153\) must satisfy

\[
|E\setminus S|\ge3,
\qquad
|S\setminus E|\ge4,
\]

and therefore

\[
|E\triangle S|\ge7.
\]

This conclusion applies separately to each specified embedding. It does not constrain other \(152\)-point base configurations or establish the nonexistence of configurations at distance seven or greater.

### Provenance

- Primary judgment: `sha256:71fbde8d269728a92be52f6401e857230043ee6938c45f810c32308d88fb9927`
- Subject and evidence transaction: `c5e8096d942d57228bb4fed00f7617fb6b43af9f`
- Base-certificate evidence: `dfc0cc40d41105292a119840dcdbe6f22860cf43`

## Change: d77/distance-from-embedded-record

This node is added for the durable symmetric-difference consequence derived in the judgment from the accepted local computations.

## Node: d77/record-perturbation-frontier

- **Type:** question
- **Parent:** `program/record-certificate-and-perturbation`
- **Status:** open
- **Title:** Perturbations beyond two removals

The established computation rules out every improvement obtained from a specified embedding after removing at most two embedded points.

It does not rule out the broader strategy of perturbing the known record. In particular, the following remain unexamined:

- removal of three or more embedded points;
- a modification that removes three points and adds four;
- deeper replacement neighborhoods around any specified embedding;
- perturbations of other \(152\)-point configurations; and
- configurations unrelated to the supplied record.

The claim that the computation prunes the entire record-perturbation strategy is therefore not accepted. Its justified scope ends at removal depth two.

### Provenance

- Qualified finding in primary judgment: `sha256:71fbde8d269728a92be52f6401e857230043ee6938c45f810c32308d88fb9927`
- Subject and evidence transaction: `c5e8096d942d57228bb4fed00f7617fb6b43af9f`

## Change: d77/record-perturbation-frontier

This open node preserves the judgment’s correction of the overly broad strategy claim and identifies the durable unexplored depth-three-or-greater neighborhood.

## Node: program/rotational-symmetry

- **Type:** program
- **Parent:** `root`
- **Status:** active
- **Title:** Rotational-symmetry restrictions and rct4 modeling

This program studies cardinality restrictions imposed by rotational invariance and exact search models for rotationally restricted \(154\)-point configurations.

Its current state is:

- an odd-cardinality no-three-in-line set invariant under a half-turn has at most one point, so a \(153\)-point set cannot have half-turn symmetry;
- a quarter-turn-invariant no-three-in-line set has cardinality divisible by four or equal to one, excluding cardinalities \(153\) and \(154\);
- a half-turn-invariant \(154\)-point subset of \(G_{77}\) must be centered at \((38,38)\), with that center unoccupied;
- the broad classification of rotations about arbitrary centers is not fully established in the supplied argument because a finite-order lattice-rotation classification step is omitted;
- rct4 is a strict subclass of centered half-turn configurations, not the whole remaining half-turn class;
- the supplied \(n=77\) rct4 model exactly represents its stated subclass;
- satisfiability of that model remains unresolved, and reported timeouts have no negative mathematical force.

The judgment attributes the new symmetry observations, implementation, validation machinery, and bounded search report to Robert Raynor and a disclosed AI research agent. It attributes the underlying rct4 class and symmetry-reduction method to Thomas; the supplied judgment excerpt ends during that attribution. The problem statement separately identifies Thomas Prellberg’s constraint-programming work as a frontier source.

### Provenance

- Primary judgment: `sha256:d24a70c16a08ff85401e969cfe12d8f8253056bb8d75e469ec226eba7a3b44c5`
- Subject transaction: `c98dd877ad81611a9a469b1bd790cd909b56b1ce`
- Supporting baseline evidence:
  - `dfc0cc40d41105292a119840dcdbe6f22860cf43`
  - `c5e8096d942d57228bb4fed00f7617fb6b43af9f`

## Change: program/rotational-symmetry

This independent program is introduced to preserve the rotational orbit lemmas, qualified classification scope, exact rct4 model, calibration evidence, and unresolved restricted satisfiability question under one durable agenda.

## Node: rotational-symmetry/cardinality-obstructions

- **Type:** lemma
- **Parent:** `program/rotational-symmetry`
- **Status:** active
- **Title:** Half-turn and quarter-turn cardinality obstructions

The supplied judgment accepts the following rotational orbit restrictions.

### Half-turn obstruction

If a finite no-three-in-line set is invariant under a half-turn and has odd cardinality, then it has at most one point. Consequently, a \(153\)-point no-three-in-line set cannot be invariant under a half-turn about any center.

### Quarter-turn obstruction

A quarter-turn-invariant no-three-in-line set has cardinality divisible by four or is a singleton. Consequently, neither \(153\) nor \(154\) is possible under quarter-turn invariance.

These conclusions apply to the stated symmetry assumptions and do not themselves classify every possible finite-order rotation preserving a grid subset.

### Provenance

- Primary judgment: `sha256:d24a70c16a08ff85401e969cfe12d8f8253056bb8d75e469ec226eba7a3b44c5`
- Subject and evidence transaction: `c98dd877ad81611a9a469b1bd790cd909b56b1ce`

## Change: rotational-symmetry/cardinality-obstructions

This node is added to retain the two accepted orbit-based cardinality restrictions as a common structural foundation for the rotational-symmetry program.

## Node: d77/154-half-turn-center

- **Type:** lemma
- **Parent:** `program/rotational-symmetry`
- **Status:** active
- **Title:** Center of a half-turn-invariant 154-point set

If a \(154\)-point no-three-in-line subset of \(G_{77}\) is invariant under a half-turn, then the half-turn is centered at

\[
(38,38).
\]

The center itself is unoccupied.

This conclusion is supported by the immutable judgment. It applies only after half-turn invariance and cardinality \(154\) are assumed; it does not assert that such a configuration exists.

### Provenance

- Primary judgment: `sha256:d24a70c16a08ff85401e969cfe12d8f8253056bb8d75e469ec226eba7a3b44c5`
- Subject and evidence transaction: `c98dd877ad81611a9a469b1bd790cd909b56b1ce`
- The required full row-and-column occupancy is also supported by judgment `sha256:a470e4a9c0903097d9c860badaa8976cf32ed5336c154f11d8fad980d401f74e`.

## Change: d77/154-half-turn-center

This node is added for the accepted and durable center restriction on any hypothetical half-turn-invariant extremal set.

## Node: d77/rotational-classification-scope

- **Type:** qualified claim
- **Parent:** `program/rotational-symmetry`
- **Status:** qualified
- **Title:** Scope of the rotational-symmetry classification at sizes 153 and 154

The supplied argument establishes the half-turn and quarter-turn restrictions recorded in this program, but it does not fully establish the broader claim that all nontrivial rotational symmetry at cardinalities \(153\) or \(154\) has been classified when rotations about arbitrary centers are allowed.

The judgment identifies a missing step: the written argument does not explicitly exclude other finite-order lattice rotations preserving a finite noncollinear integer set. The judgment describes the desired classification as plausible and repairable, but does not accept the omitted argument as already supplied.

If “rotational symmetry” is restricted to rotations in the dihedral symmetry group of the square grid, this gap may be terminological. Under the broader arbitrary-center meaning used in the transaction, the classification remains incompletely justified.

Independently of that missing step, rct4 must not be identified with the entire centered half-turn class. The rct4 conditions add requirements such as an empty anti-diagonal, complete quarter-turn orbits away from the diagonals, and one selected main-diagonal half-turn pair. General centered half-turn configurations need not satisfy those restrictions.

There is no supplied opposed judgment on this issue. It is therefore a qualified scope node, not an active dispute.

### Provenance

- Qualified finding in primary judgment: `sha256:d24a70c16a08ff85401e969cfe12d8f8253056bb8d75e469ec226eba7a3b44c5`
- Subject and evidence transaction: `c98dd877ad81611a9a469b1bd790cd909b56b1ce`

## Change: d77/rotational-classification-scope

This node is added to preserve the judgment’s explicit qualification of the broad rotational-classification wording without supplying the missing classification or treating rct4 as the whole half-turn class.

## Node: d77/rct4-154-model

- **Type:** method
- **Parent:** `program/rotational-symmetry`
- **Status:** active
- **Title:** Exact rct4 model for 154 points in \(G_{77}\)

Static inspection supports with high confidence that the supplied \(n=77\) model is sound and complete for the stated rct4 subclass of \(154\)-point configurations.

That subclass requires:

1. the anti-diagonal to be empty;
2. occupied cells away from the two diagonals to occur in complete quarter-turn orbits; and
3. exactly one half-turn pair on the main diagonal to be occupied.

At \(n=77\), the model has:

- \(1{,}444\) off-diagonal quarter-turn-orbit variables;
- \(38\) main-diagonal half-turn-pair variables;
- exact cardinality conditions selecting \(38\) off-diagonal orbits and one diagonal pair; and
- \(388{,}148\) deduplicated weighted line constraints.

The selections represent

\[
4\cdot38+2=154
\]

points.

The model’s primitive-line enumeration, orbit-weighted at-most-two constraints, CNF translation, and deterministic statistics are accepted as sound and complete within this subclass. Thus:

- every feasible assignment yields a \(154\)-point no-three-in-line set satisfying the rct4 conditions; and
- every \(154\)-point no-three-in-line set satisfying those conditions induces a feasible assignment.

A feasible assignment would prove \(D(77)=154\). Infeasibility of this model would exclude only the rct4 subclass, not all centered half-turn sets and not all \(154\)-point sets.

### Provenance

- Primary judgment: `sha256:d24a70c16a08ff85401e969cfe12d8f8253056bb8d75e469ec226eba7a3b44c5`
- Subject and evidence transaction: `c98dd877ad81611a9a469b1bd790cd909b56b1ce`

## Change: d77/rct4-154-model

This node is added to materialize the accepted exact equivalence between feasible model assignments and the stated restricted rct4 class, while retaining its strict scope.

## Node: rct4/calibration-certificates

- **Type:** evidence result
- **Parent:** `program/rotational-symmetry`
- **Status:** active
- **Title:** Exact calibration certificates for the rct4 implementation

The supplied implementation verifies committed rct4 certificates at

\[
n=41,47,57,65,69.
\]

For each listed size, the checks cover:

- decoding two points per row;
- point distinctness and grid membership;
- exact determinant testing of every point triple;
- the empty anti-diagonal and required orbit structure; and
- satisfaction of the generated model constraints.

These five certificates provide exact implementation regression checks at those five sizes only.

They do not establish:

- that every relevant historical record in a broader range has rct4 form;
- the external provenance of the underlying configurations;
- discovery priority; or
- satisfiability of the \(n=77\) instance.

### Provenance

- Primary judgment: `sha256:d24a70c16a08ff85401e969cfe12d8f8253056bb8d75e469ec226eba7a3b44c5`
- Subject and evidence transaction: `c98dd877ad81611a9a469b1bd790cd909b56b1ce`

## Change: rct4/calibration-certificates

This node is added to preserve the five exact regression checks as scoped implementation evidence rather than allowing
