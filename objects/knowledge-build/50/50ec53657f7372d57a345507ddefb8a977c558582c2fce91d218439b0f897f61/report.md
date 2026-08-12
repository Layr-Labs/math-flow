# Knowledge-Formation Report

The supplied primary judgment re-supports the existing 152-point certificate and the resulting lower bound, while adding qualifications about hosted execution and artifact provenance. It does not alter the certified interval or resolve the exact value of \(D(77)\).

Accordingly:

- the certificate, hosted-replay qualification, artifact-identity qualification, and provenance correction are consolidated into `no-three-in-line/g76-152-point-set`;
- the re-verified lower-bound implication is consolidated into `no-three-in-line/d77-certified-interval`;
- the absence of any improvement or exact determination is incorporated into `no-three-in-line/d77-exact-value`;
- no event-shaped node is created for the replay package, hosted-verification request, or clerical correction;
- no new mathematical claim or dispute node is warranted; and
- the supplied conflict record set is empty, so no reconciliation outcome or active conflict requires separate representation.

## Node: no-three-in-line/g76-152-point-set

- **Type:** Verified existence, symmetry, and finite-orbit claim
- **Status:** Supported; hosted execution remains unevidenced
- **Parent:** `root`
- **Primary judgment provenance:**
  - `sha256:a470e4a9c0903097d9c860badaa8976cf32ed5336c154f11d8fad980d401f74e`
  - `sha256:71fbde8d269728a92be52f6401e857230043ee6938c45f810c32308d88fb9927`
  - `sha256:8c5f8eeb55af54b575fd3d46473e7894095afd6a4741186fe0583d3d0feade8a`
- **Evidence transactions:**
  - `dfc0cc40d41105292a119840dcdbe6f22860cf43`
  - `c5e8096d942d57228bb4fed00f7617fb6b43af9f`
  - `0ffe9a12c3ad44cf136dd22df7083dcdd53af1b0`

The immutable judgments support the existence of a particular subset

\[
C\subseteq G_{76}=\{0,\ldots,75\}^2
\]

having exactly 152 distinct points and containing no three distinct collinear points.

### Certificate and exact verification

The judgments report that the encoded certificate is decoded deterministically into 76 pairs of points, with two points in every row \(y=0,\ldots,75\). The supplied standard-library checker:

- decodes exactly 152 points from the pinned payload;
- checks that the decoded points are distinct;
- checks that every coordinate lies in \(G_{76}\);
- examines all
  \[
  \binom{152}{3}=573{,}800
  \]
  unordered triples; and
- tests collinearity by the exact integer determinant
  \[
  (x_2-x_1)(y_3-y_1)-(x_3-x_1)(y_2-y_1).
  \]

The judgments characterize this as a complete, deterministic, reproducible exact verifier rather than a heuristic or floating-point test. No defect was identified in the decoding, range checks, distinctness checks, or exhaustive collinearity test.

The checker infers the intended grid size and point count from the supplied payload rather than hard-coding assertions that the size is 76 and the count is 152. The current judgment says that this does not undermine soundness for the pinned artifact because the inferred values are exposed by the reported output, although hard-coded expectations would make the intended claim more explicit.

### Symmetry and specified embeddings

The judgment at

`sha256:71fbde8d269728a92be52f6401e857230043ee6938c45f810c32308d88fb9927`

additionally supports with high confidence that \(C\) is invariant under the quarter-turn

\[
q(x,y)=(75-y,x).
\]

Enumeration and deduplication of the eight dihedral transformations of the \(76\times76\) square produce exactly two distinct images of \(C\).

For each of those two images, applying each translation

\[
(t_x,t_y)\in\{0,1\}^2
\]

produces exactly eight distinct subsets of \(G_{77}\) in total.

These symmetry and orbit conclusions concern only the certified configuration and the stated family of transformations. They do not establish that every optimal or near-optimal configuration in \(G_{76}\) or \(G_{77}\) has quarter-turn symmetry.

The count of eight embeddings is limited to:

1. the two distinct dihedral images of \(C\); and
2. the four placements obtained from translations in \(\{0,1\}^2\).

It does not count unrelated affine images or embeddings of other 152-point configurations.

### Execution and hosted-replay qualification

The mathematical support rests on static inspection of a finite, exact, deterministic checker and its pinned certificate. The newer replay transaction supplies the executable artifacts and a claimed expected output, but it does not include an execution log or attestation proving that this particular replay was run.

In particular, acceptance by the specified governed hosted-verifier environment is not established. The transaction includes a `verification.json` request containing a verifier identifier, specification digest, checker entry point, and certificate argument, but no content-addressed hosted attestation, exit status, transcript, or hosted output is supplied.

The external schema and workflow rules needed to determine exactly how artifact bytes would be bound into a future attestation are also absent from the adjudicated evidence. A future hosted execution would provide execution independence, not algorithmic independence, because the checker is copied from the earlier contribution rather than independently reimplemented.

These hosted-execution limitations do not overturn the judgments’ support for the certificate itself.

### Artifact identity and provenance qualification

The displayed configuration and verifier in transaction

`0ffe9a12c3ad44cf136dd22df7083dcdd53af1b0`

are judged to reproduce the earlier mathematical artifacts unchanged in substance. Strict byte-for-byte identity, including details such as line endings and terminal newlines, is not independently established by a checksum.

The replay README contains an erroneous provenance pointer. It names the earlier transaction as

`dfc0cc40d1193b8d5ca25e7f177fa48ff9a1b38d`,

whereas the supplied baseline record is

`dfc0cc40d41105292a119840dcdbe6f22860cf43`.

The primary judgment treats this as a clerical metadata error. It does not affect the coordinates, verifier, no-three-in-line implication, or resulting lower bound, but the incorrect pointer should not be used as the canonical provenance reference.

### Credit

The underlying coordinate set is attributed in the supplied materials to Achim Flammenkamp’s maintained database. Robert is credited with reproducing and independently checking the baseline certificate, not with originating the construction. The finer priority or authorship history of the 152-point construction remains undetermined by the supplied evidence.

The local symmetry analysis, code, and accompanying text are attributed by the earlier judgment to an AI research agent working at Robert Raynor’s request.

The newer transaction is credited with packaging a canonical hosted-verification request and republishing the existing artifacts in replayable form. It is not credited with discovering the configuration, devising a new verification algorithm, or improving the bound.

## Change: no-three-in-line/g76-152-point-set

The stable certificate node is retained rather than creating separate nodes for the replay transaction, hosted-verifier request, artifact comparison, or provenance typo. Those matters qualify the verification and provenance of the same durable mathematical certificate.

The current account incorporates primary judgment

`sha256:8c5f8eeb55af54b575fd3d46473e7894095afd6a4741186fe0583d3d0feade8a`

and evidence transaction

`0ffe9a12c3ad44cf136dd22df7083dcdd53af1b0`.

That judgment:

- strongly re-supports the 152-point certificate through the supplied executable exact checker;
- distinguishes an executable certificate from an execution attestation;
- leaves governed hosted-verifier acceptance unestablished;
- supports unchanged-in-substance artifact identity without asserting independently proven byte identity;
- identifies the incorrect prior transaction hash as a clerical provenance error; and
- preserves the existing mathematical validity, symmetry conclusions, and credit allocation.

The canonical baseline transaction reference in the materialized account is therefore the supplied record

`dfc0cc40d41105292a119840dcdbe6f22860cf43`.

The immutable erroneous README text is not rewritten or treated as a competing mathematical claim.

## Node: no-three-in-line/d77-certified-interval

- **Type:** Certified bound
- **Status:** Supported with high confidence
- **Parent:** `root`
- **Primary judgment provenance:**
  - `sha256:a470e4a9c0903097d9c860badaa8976cf32ed5336c154f11d8fad980d401f74e`
  - `sha256:8c5f8eeb55af54b575fd3d46473e7894095afd6a4741186fe0583d3d0feade8a`
- **Evidence transactions:**
  - `dfc0cc40d41105292a119840dcdbe6f22860cf43`
  - `0ffe9a12c3ad44cf136dd22df7083dcdd53af1b0`
- **Related certificate:** `no-three-in-line/g76-152-point-set`

For

\[
G_{77}=\{0,\ldots,76\}^2,
\]

let \(D(77)\) be the largest cardinality of a subset containing no three distinct collinear points. The immutable judgments support the certified interval

\[
\boxed{152\le D(77)\le154}.
\]

### Certified lower bound

The exact certificate represented by `no-three-in-line/g76-152-point-set` supplies 152 no-three-in-line points in

\[
G_{76}=\{0,\ldots,75\}^2.
\]

The judgments accept that the same coordinates form a subset of \(G_{77}\), since \(G_{76}\subset G_{77}\). They therefore support

\[
D(77)\ge152.
\]

The newer replay judgment independently re-supports this implication conditional only on the executable certificate verification it describes. Its absence of a hosted execution attestation does not supply a stronger lower bound, but neither does it overturn the existing certified lower bound.

### Certified upper bound

The earlier primary judgment accepts the elementary row-capacity argument: every one of the 77 horizontal grid lines contains at most two selected points in a no-three-in-line set. It therefore supports

\[
D(77)\le 2\cdot77=154.
\]

The newer transaction supplies no new upper-bound argument and does not alter this side of the interval.

### Scope

The current interval is the strongest globally certified bound in the supplied judgment record. The replay package:

- does not supply a 153-point or 154-point configuration;
- does not prove that 153 or 154 points are impossible;
- does not improve the lower bound beyond 152; and
- does not improve the upper bound below 154.

Thus the supported interval remains exactly

\[
152\le D(77)\le154.
\]

## Change: no-three-in-line/d77-certified-interval

The finding routed under `no-three-in-line/d77-lower-bound-152` is consolidated into the existing interval node rather than represented as a parallel lower-bound node. It is another evidentiary basis for one side of the same durable certified interval.

Primary judgment

`sha256:8c5f8eeb55af54b575fd3d46473e7894095afd6a4741186fe0583d3d0feade8a`

re-verifies the existing implication \(D(77)\ge152\) from the executable \(G_{76}\) certificate. It expressly states that this is not an improved lower bound. No new evidence changes the established upper bound \(D(77)\le154\).

The mathematical interval is therefore unchanged. The organizational update adds the replay judgment and its execution qualification to the provenance supporting the lower side of the existing node.

## Node: no-three-in-line/d77-exact-value

- **Type:** Open mathematical question
- **Status:** Unresolved
- **Parent:** `root`
- **Primary judgment provenance:**
  - `sha256:a470e4a9c0903097d9c860badaa8976cf32ed5336c154f11d8fad980d401f74e`
  - `sha256:71fbde8d269728a92be52f6401e857230043ee6938c45f810c32308d88fb9927`
  - `sha256:d24a70c16a08ff85401e969cfe12d8f8253056bb8d75e469ec226eba7a3b44c5`
  - `sha256:21f3e6bb405eaaf804b58020a1695c213023b0dd3f1d25a08248fb5a48750eca`
  - `sha256:8c5f8eeb55af54b575fd3d46473e7894095afd6a4741186fe0583d3d0feade8a`
- **Evidence transactions:**
  - `dfc0cc40d41105292a119840dcdbe6f22860cf43`
  - `c5e8096d942d57228bb4fed00f7617fb6b43af9f`
  - `c98dd877ad81611a9a469b1bd790cd909b56b1ce`
  - `29ccbd396781fd36d436ed2e6d0952a4730361b9`
  - `0ffe9a12c3ad44cf136dd22df7083dcdd53af1b0`
- **Related bound:** `no-three-in-line/d77-certified-interval`
- **Related structural nodes:**
  - `no-three-in-line/d77-near-capacity-occupancy`
  - `no-three-in-line/d77-distance-from-embedded-g76-152-record`
  - `finite-lattice-sets/nontrivial-rotation-classification`
  - `no-three-in-line/rotational-cardinality-obstructions`
  - `no-three-in-line/d77-154-centered-half-turn-condition`
  - `no-three-in-line/d77-rotational-symmetry-at-153-154`
  - `no-three-in-line/d77-rct4-154-model`

The exact value of \(D(77)\) remains unresolved under the supplied immutable judgments. The strongest globally certified conclusion is

\[
152\le D(77)\le154,
\]

so the supported possibilities remain

\[
D(77)\in\{152,153,154\}.
\]

### Certified bounds

The lower bound is supported by the exactly checked 152-point no-three-in-line configuration in \(G_{76}\), embedded unchanged into \(G_{77}\).

The upper bound is supported by the judgment accepting that each of the 77 rows contains at most two selected points.

No supplied judgment improves either side.

### Restrictions near the known embeddings

For each of the eight specified embeddings \(E\) of the verified 152-point configuration, the existing judgments support that every no-three-in-line set \(S\subseteq G_{77}\) with \(|S|\ge153\) must satisfy

\[
|E\setminus S|\ge3,
\qquad
|S\setminus E|\ge4,
\qquad
|E\triangle S|\ge7.
\]

These restrictions concern the eight specified embeddings only. They do not constrain all configurations beyond that distance and do not cover every possible 152-point configuration.

### Rotational restrictions

The supplied judgments establish the following limited structural conclusions:

- any hypothetical 153-point no-three-in-line subset of \(G_{77}\) has no nonidentity rotational symmetry about any center;
- if a hypothetical 154-point no-three-in-line subset has nontrivial rotational symmetry, that symmetry must be the half-turn about \((38,38)\); and
- the center \((38,38)\) must be unselected in such a 154-point set.

These conclusions do not classify or exclude reflection symmetry. Consequently, the judgment record leaves open:

- reflection-symmetric or asymmetric 153-point configurations;
- asymmetric or reflection-symmetric 154-point configurations; and
- 154-point configurations in the general centered-half-turn class.

### Restricted computational result

The \(n=77\) `rct4` model is accepted by the relevant judgment as an exact encoding of its stated 154-point subclass, but the satisfiability of that instance remains unresolved. Reported timeout and `UNKNOWN` outcomes establish neither satisfiability nor unsatisfiability.

The `rct4` class is strictly narrower than the class of all configurations invariant under the half-turn about \((38,38)\). Thus even a future `rct4` infeasibility certificate would not by itself exclude:

- other centered-half-turn 154-point configurations;
- reflection-symmetric 154-point configurations; or
- asymmetric 154-point configurations.

### Replay package and optimality

The replay package adjudicated at

`sha256:8c5f8eeb55af54b575fd3d46473e7894095afd6a4741186fe0583d3d0feade8a`

does not determine \(D(77)\) and does not improve the certified interval. It provides no 153-point or 154-point certificate, no exclusion proof, no global search certificate, and no new upper-bound argument.

Its hosted-verification request concerns re-execution of the known 152-point certificate. Whether that future hosted execution succeeds has no supplied implication establishing optimality at 152 or excluding either 153 or 154.

### Missing decisive evidence

The supplied evidence contains none of the following:

- a 153-point coordinate certificate;
- a 154-point coordinate certificate;
- a global impossibility proof for 153 points;
- a global impossibility proof for 154 points;
- a globally exhaustive search;
- a satisfiability or unsatisfiability certificate for the \(n=77\) `rct4` instance;
- an exclusion of every general centered-half-turn 154-point configuration;
- an exclusion of all reflection-symmetric candidates; or
- an exclusion of all asymmetric candidates.

The exact value remains unresolved because decisive evidence is absent. The supplied records do not present incompatible judgments about the value of \(D(77)\), and no active dispute or reconciliation record exists.

## Change: no-three-in-line/d77-exact-value

Primary judgment

`sha256:8c5f8eeb55af54b575fd3d46473e7894095afd6a4741186fe0583d3d0feade8a`

is added to the provenance of the unresolved exact-value question. Its routed `refutes` stance addresses the proposition that transaction `0ffe9a12c3ad44cf136dd22df7083dcdd53af1b0` determines \(D(77)\) or improves the interval; it does not refute or resolve the open question itself.

The judgment confirms that the transaction supplies none of the evidence needed to select among \(152\), \(153\), and \(154\). The materialized state therefore continues to record the exact value as unresolved, with all previously supported local and rotational restrictions preserved.

No dispute node is created. The unresolved state results from missing decisive evidence, not from incompatible primary judgments, and the supplied conflict-record list is empty.
