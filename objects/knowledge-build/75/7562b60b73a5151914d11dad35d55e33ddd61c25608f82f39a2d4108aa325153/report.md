# Knowledge-Formation Report

The supplied judgment updates three existing durable concepts: the \(G_{76}\) certificate, the global certified interval for \(D(77)\), and the unresolved exact-value question. No new research program, mathematical result node, or dispute node is warranted. The hosted-verification request, replay packaging, and provenance error are incorporated into the existing certificate node because they qualify the evidence and provenance of that certificate rather than constitute independent mathematical concepts.

## Node: g76/152-point-certificate

- **Type:** result
- **Parent:** `program/record-certificate-and-perturbation`
- **Status:** active
- **Title:** Exact 152-point no-three-in-line certificate in \(G_{76}\)

The supplied judgments support the existence of a \(152\)-point subset of

\[
G_{76}=\{0,\ldots,75\}^2
\]

containing no three collinear points.

The encoded payload decodes to exactly \(152\) distinct grid points, with two points in each of the \(76\) rows. The exact verifier checks:

- that the payload decodes to \(152\) distinct points;
- that every coordinate lies in \(G_{76}\); and
- that the determinant is nonzero for all
  \[
  \binom{152}{3}=573{,}800
  \]
  unordered triples.

The verifier uses deterministic exact integer arithmetic, without floating-point tolerances, random sampling, or external mathematical dependencies. The judgments characterize it as a complete executable certificate. The checker infers the grid size and point count from the pinned payload rather than hard-coding `size == 76` and `count == 152`; the latest judgment states that this does not undermine soundness for the supplied artifact because the decoded values are exposed by the reported verification behavior.

The baseline verifier accepts a leading symmetry marker but does not itself verify the represented symmetry. This does not affect its no-three-in-line check, which depends only on the decoded coordinates. A separate judged local-rigidity computation checked quarter-turn symmetry for this particular coordinate set.

A later replay package republishes the displayed configuration text and the same verifier logic. The latest judgment strongly supports identity in mathematical substance with the earlier artifacts, while qualifying that strict byte-for-byte identity—including details such as terminal newlines or line endings—is not independently established by a checksum.

The replay package includes a request for execution in a governed hosted-verifier environment, but no hosted execution result has been supplied. In particular, there is no content-addressed attestation, exit status, execution transcript, or hosted output establishing that the pinned checker and certificate were accepted in that environment. The external schema and binding rules are also not available in the supplied evidence for independent assessment. The judgment distinguishes the supplied executable certificate from an attestation that the requested hosted run occurred. It further states that a future hosted run would provide execution independence, not algorithmic independence, because the checker is copied from the earlier contribution.

The replay package’s README contains an erroneous provenance identifier. It names the earlier transaction as

```text
dfc0cc40d1193b8d5ca25e7f177fa48ff9a1b38d
```

whereas the supplied baseline record is

```text
dfc0cc40d41105292a119840dcdbe6f22860cf43
```

The latest judgment treats this as a clerical metadata error that should be corrected. It does not alter the coordinate set, the verifier, or the certified no-three-in-line property.

The judgments attribute the underlying coordinate set to Achim Flammenkamp’s maintained database. Robert is credited for the self-contained reproduction and independent verifier, not for originating the construction. The later replay transaction is credited for packaging a canonical hosted-verification request and republishing the artifacts in a replayable form, not for discovering the configuration, devising a new verification algorithm, or improving the bound.

### Provenance

- Baseline primary judgment: `sha256:a470e4a9c0903097d9c860badaa8976cf32ed5336c154f11d8fad980d401f74e`
- Baseline certificate transaction: `dfc0cc40d41105292a119840dcdbe6f22860cf43`
- Separate symmetry-verification judgment: `sha256:71fbde8d269728a92be52f6401e857230043ee6938c45f810c32308d88fb9927`
- Separate symmetry-verification transaction: `c5e8096d942d57228bb4fed00f7617fb6b43af9f`
- Replay-package judgment: `sha256:8c5f8eeb55af54b575fd3d46473e7894095afd6a4741186fe0583d3d0feade8a`
- Replay-package transaction: `0ffe9a12c3ad44cf136dd22df7083dcdd53af1b0`

## Change: g76/152-point-certificate

This build incorporates the latest judgment’s evidence qualification into the existing certificate node. It records the reproduced executable verifier, the absence of a hosted-run attestation, the distinction between execution and algorithmic independence, the qualified artifact-identity claim, the incorrect baseline transaction identifier, and the replay-package credit. These matters refine the evidence and provenance of the same durable certificate and therefore do not justify separate mathematical or event-shaped nodes.

## Node: d77/certified-interval

- **Type:** result
- **Parent:** `root`
- **Status:** active
- **Title:** Certified bounds for \(D(77)\)

The supplied judgments support the current certified interval

\[
\boxed{152\le D(77)\le154}.
\]

The lower bound is supported by the exact \(152\)-point no-three-in-line certificate in \(G_{76}\). Since

\[
G_{76}\subset G_{77},
\]

the same coordinates give a \(152\)-point no-three-in-line subset of \(G_{77}\), and hence

\[
D(77)\ge152.
\]

A later replay package supplies the same configuration and checker logic in executable form. The latest judgment accepts the lower-bound implication conditional on the described certificate verification and characterizes this as a re-verification of the established endpoint, not an improvement. The requested hosted-verifier execution has not been attested, but that absence does not retire or reduce the already certified lower bound supported by the earlier exact certificate judgment.

The upper bound remains

\[
D(77)\le154.
\]

It follows from the \(77\) horizontal rows of \(G_{77}\): a no-three-in-line set can contain at most two selected points on any row, giving the bound \(2\cdot77=154\).

No supplied judged result changes either endpoint. In particular, the replay package supplies neither a \(153\)- or \(154\)-point configuration nor a new upper-bound argument.

### Provenance

- Baseline certificate judgment: `sha256:a470e4a9c0903097d9c860badaa8976cf32ed5336c154f11d8fad980d401f74e`
- Baseline certificate transaction: `dfc0cc40d41105292a119840dcdbe6f22860cf43`
- Additional judgment affirming the unchanged interval: `sha256:71fbde8d269728a92be52f6401e857230043ee6938c45f810c32308d88fb9927`
- Additional judgment affirming the unchanged interval: `sha256:d24a70c16a08ff85401e969cfe12d8f8253056bb8d75e469ec226eba7a3b44c5`
- Replay-package judgment re-verifying the lower-bound implication: `sha256:8c5f8eeb55af54b575fd3d46473e7894095afd6a4741186fe0583d3d0feade8a`
- Replay-package transaction: `0ffe9a12c3ad44cf136dd22df7083dcdd53af1b0`

## Change: d77/certified-interval

This build adds the latest judgment’s renewed support for the existing lower bound and records its precise scope: the replay is an executable re-verification package without a hosted-run attestation and does not improve either endpoint. The interval remains a root-level global fact because it spans all research programs.

## Node: d77/exact-value

- **Type:** question
- **Parent:** `root`
- **Status:** open
- **Title:** Exact value of \(D(77)\)

The exact value of \(D(77)\) remains unresolved. The supplied judgments support only

\[
D(77)\in\{152,153,154\}.
\]

No judged transaction supplies:

- a \(153\)-point coordinate certificate;
- a \(154\)-point coordinate certificate;
- a global impossibility proof for \(153\) points;
- a global impossibility proof for \(154\) points; or
- another argument improving either endpoint of the certified interval.

The local-rigidity judgments concern only eight specified embeddings of one \(152\)-point record. Their conclusions do not constrain all \(152\)-point configurations or configurations sufficiently distant from those embeddings.

The rotational-symmetry work also does not determine the exact value. Its rct4 model concerns only a strict subclass of centered half-turn-invariant \(154\)-point sets, and satisfiability of that model for \(n=77\) remains unknown.

The later replay package republishes the existing \(152\)-point certificate and its checker. The latest judgment expressly finds that it neither determines \(D(77)\) nor improves the interval: it contains no \(153\)- or \(154\)-point certificate, no exclusion proof, and no new upper-bound argument. Its unresolved hosted-execution status likewise supplies no evidence about optimality.

Accordingly, the exact-value question remains open within the certified interval

\[
152\le D(77)\le154.
\]

### Provenance

- Baseline judgment: `sha256:a470e4a9c0903097d9c860badaa8976cf32ed5336c154f11d8fad980d401f74e`
- Baseline transaction: `dfc0cc40d41105292a119840dcdbe6f22860cf43`
- Local-rigidity judgment: `sha256:71fbde8d269728a92be52f6401e857230043ee6938c45f810c32308d88fb9927`
- Local-rigidity transaction: `c5e8096d942d57228bb4fed00f7617fb6b43af9f`
- Rotational-symmetry judgment: `sha256:d24a70c16a08ff85401e969cfe12d8f8253056bb8d75e469ec226eba7a3b44c5`
- Rotational-symmetry transaction: `c98dd877ad81611a9a469b1bd790cd909b56b1ce`
- Replay-package judgment: `sha256:8c5f8eeb55af54b575fd3d46473e7894095afd6a4741186fe0583d3d0feade8a`
- Replay-package transaction: `0ffe9a12c3ad44cf136dd22df7083dcdd53af1b0`

## Change: d77/exact-value

This build records the latest judgment’s explicit finding that the replay package neither resolves the exact-value question nor improves the certified interval. The question remains at root level because it is the central cross-program problem. No dispute node is introduced because the supplied records contain no conflicting judgments or unresolved reconciliation outcome.
