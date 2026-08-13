# Knowledge-Formation Report

The current taxonomy remains coherent. The exact-value question stays at root because its certified interval is global. A durable certificate node is created beneath the existing embedded-record rigidity program to organize the mathematical certificate, its verification scope, the unresolved hosted-replay status, and the qualified provenance finding. No program split, merge, retirement, restoration, topology-only move, or active dispute is warranted by the supplied judgment.

## Node: no-three-in-line/d77-exact-value

- **Type:** Central question and global bounds
- **Title:** Exact value and certified interval for \(D(77)\)
- **Status:** Active and unresolved
- **Parent:** `root`

The central question is to determine the maximum size \(D(77)\) of a no-three-in-line subset of \(G_{77}\).

The accepted primary judgments leave the current certified interval at

\[
152\le D(77)\le154.
\]

The lower bound is supported by a verified 152-point no-three-in-line subset of \(G_{76}\), which embeds unchanged into \(G_{77}\). Primary judgment `sha256:8c5f8eeb55af54b575fd3d46473e7894095afd6a4741186fe0583d3d0feade8a` provides an additional assessment of a republished executable certificate package and accepts the implication

\[
D(77)\ge152,
\]

conditional only on the complete executable certificate verification described in that judgment. This is a re-verification of the existing lower bound, not an improvement. The package does not evidence a completed hosted run and does not use an independently implemented checking algorithm; those qualifications do not alter the previously certified interval.

No accepted contribution supplies:

- a 153- or 154-point coordinate certificate;
- a global impossibility proof for either cardinality;
- a global exhaustive search resolving the interval; or
- a new upper-bound argument improving \(D(77)\le154\).

Primary judgment `sha256:21f3e6bb405eaaf804b58020a1695c213023b0dd3f1d25a08248fb5a48750eca` accepts the following rotational-symmetry restrictions without improving the global bounds:

- any hypothetical 153-point configuration has no nonidentity rotational symmetry, although reflection-symmetric and asymmetric possibilities remain;
- if a hypothetical 154-point configuration has nontrivial rotational symmetry, it must have the half-turn about \((38,38)\), with that center unselected;
- asymmetric and reflection-symmetric 154-point configurations remain possible in principle; and
- general centered-half-turn symmetry is broader than the previously referenced `rct4` class.

Primary judgment `sha256:71fbde8d269728a92be52f6401e857230043ee6938c45f810c32308d88fb9927` accepts a separate local restriction around eight specified embeddings of one 152-point \(G_{76}\) record:

- none of those embeddings can be improved after removing at most two embedded points;
- for each specified embedding \(E\), any no-three-in-line set \(S\) with \(|S|\ge153\) must satisfy
  \[
  |E\setminus S|\ge3,\qquad |S\setminus E|\ge4,\qquad |E\triangle S|\ge7;
  \]
- configurations based on three or more removals remain unexamined; and
- other 152-point configurations and larger configurations sufficiently far from every specified embedding remain unconstrained by this local computation.

Primary judgment `sha256:8c5f8eeb55af54b575fd3d46473e7894095afd6a4741186fe0583d3d0feade8a` further finds that its subject transaction does not determine \(D(77)\) or improve the interval. It supplies neither a larger certificate nor an exclusion or upper-bound proof.

The accepted certificate, rotational, and local-rigidity results therefore do not select among

\[
D(77)=152,\qquad D(77)=153,\qquad D(77)=154.
\]

**Authoritative provenance**

- Primary judgment on rotational restrictions: `sha256:21f3e6bb405eaaf804b58020a1695c213023b0dd3f1d25a08248fb5a48750eca`
- Subject and evidence transaction for the rotational judgment: `29ccbd396781fd36d436ed2e6d0952a4730361b9`
- Primary judgment on embedded-record rigidity: `sha256:71fbde8d269728a92be52f6401e857230043ee6938c45f810c32308d88fb9927`
- Subject transaction for the rigidity judgment: `c5e8096d942d57228bb4fed00f7617fb6b43af9f`
- Supporting baseline evidence transaction: `dfc0cc40d41105292a119840dcdbe6f22860cf43`
- Primary judgment on the republished executable certificate and unchanged lower bound: `sha256:8c5f8eeb55af54b575fd3d46473e7894095afd6a4741186fe0583d3d0feade8a`
- Subject transaction for that judgment: `0ffe9a12c3ad44cf136dd22df7083dcdd53af1b0`, ledger position 5
- Claim keys represented here: `no-three-in-line/d77-exact-value` and `no-three-in-line/d77-lower-bound-152`

## Change: no-three-in-line/d77-exact-value

Updated the root-level exact-value node to record the additional judged re-verification of the existing 152 lower bound and the judgment’s finding that no exact-value or interval improvement resulted. The certified interval and unresolved status are unchanged; the node remains at root because they are global rather than program-specific.

## Node: no-three-in-line/g76-152-point-set

- **Type:** Certified configuration and verification result
- **Title:** The 152-point no-three-in-line configuration in \(G_{76}\)
- **Status:** Active; mathematical certificate strongly supported, hosted replay not established
- **Parent:** `programs/embedded-g76-record-rigidity`

This node records the durable mathematical certificate underlying the current lower bound and the accepted limits of its republished verification package.

According to primary judgment `sha256:8c5f8eeb55af54b575fd3d46473e7894095afd6a4741186fe0583d3d0feade8a`, the supplied encoded configuration is strongly supported as representing 152 distinct points of \(G_{76}\) with no three collinear.

The judgment characterizes the supplied `verify.py` as a complete, deterministic, reproducible exact verifier. As assessed there, it:

- decodes the supplied configuration;
- determines the represented grid size and point count from the pinned payload;
- checks that the decoded points are distinct;
- checks that every point lies in \(G_{76}\); and
- exhaustively checks all unordered triples using an exact integer determinant.

The judgment notes that the checker uses no floating-point tolerances, random search, heuristic sampling, or external dependencies. Its inferred rather than hard-coded size and count do not undermine soundness for the pinned artifact, although hard-coded expectations would state the intended claim more explicitly.

The accepted consequence is that the same 152 points embed unchanged into \(G_{77}\), supporting

\[
D(77)\ge152.
\]

This is the established lower bound and not a new record or improvement.

### Hosted replay status

Acceptance in the specified governed hosted-verifier environment is not established by the supplied evidence.

The subject transaction contains a verification request identifying a verifier specification, checker entry point, and certificate argument. The judgment finds that it contains no content-addressed hosted attestation, exit status, execution transcript, or hosted output proving that the requested run occurred. The external schema and workflow rules governing how artifact bytes would be bound into such an attestation also were not available for independent adjudication.

A future successful hosted run could supply execution independence. It would not supply algorithmic independence because the checker is copied from the earlier contribution rather than independently implemented. This unresolved execution status is a qualification on the replay claim, not a conflict over the mathematical certificate.

### Artifact identity and provenance

The judgment supports that the displayed configuration republishes the earlier baseline configuration unchanged in mathematical substance and that the displayed verifier uses the same checker logic. Strict byte-for-byte identity, including line-ending and terminal-newline details, is not independently established by a checksum in the subject transaction.

The subject README contains an erroneous provenance pointer. It names the earlier transaction as

```text
dfc0cc40d1193b8d5ca25e7f177fa48ff9a1b38d
```

whereas the earlier baseline record supplied as evidence is

```text
dfc0cc40d41105292a119840dcdbe6f22860cf43
```

The primary judgment treats this as a clerical metadata error. It does not affect the points, the verifier, or the lower-bound implication, but the incorrect identifier should not be used as the authoritative pointer to the baseline artifact.

### Scope

This certificate establishes only the existence of a 152-point no-three-in-line subset of \(G_{76}\), and consequently of \(G_{77}\). It does not supply:

- a 153- or 154-point configuration;
- a proof that 152 points are optimal in \(G_{77}\);
- a new verification algorithm;
- a completed hosted-verifier attestation; or
- an improvement to either side of \(152\le D(77)\le154\).

The certificate is nested beneath the embedded-record rigidity program because that program studies this particular record and its specified embeddings. The global lower-bound consequence remains recorded only in the root-level exact-value node.

### Credit recorded by the judgment

- The underlying configuration and lower bound predate the republished replay package.
- The supplied history attributes the coordinate set to Achim Flammenkamp’s maintained database and to the earlier baseline contribution that packaged the certificate and checker.
- The checker in the subject transaction is copied from that earlier contribution.
- The subject transaction receives credit for republishing the artifacts in replayable form and packaging a canonical hosted-verification request, not for discovering the configuration, devising a new verifier, or improving the bound.
- The incorrect prior-transaction hash weakens the provenance record but does not create a competing mathematical priority claim.

**Authoritative provenance**

- Primary judgment: `sha256:8c5f8eeb55af54b575fd3d46473e7894095afd6a4741186fe0583d3d0feade8a`
- Subject transaction: `0ffe9a12c3ad44cf136dd22df7083dcdd53af1b0`, ledger position 5
- Earlier baseline evidence transaction: `dfc0cc40d41105292a119840dcdbe6f22860cf43`
- Represented claim keys:
  - `no-three-in-line/g76-152-point-set`
  - `no-three-in-line/d77-lower-bound-152`
  - `no-three-in-line/g76-152-certificate-hosted-replay-acceptance`
  - `no-three-in-line/g76-152-certificate-artifact-identity-and-provenance`

## Change: no-three-in-line/g76-152-point-set

Created a durable certificate node for the particular 152-point \(G_{76}\) configuration, nested beneath the existing program that studies this record. The node consolidates the supported mathematical certificate, its unchanged lower-bound implication, the unevidenced hosted execution, the lack of algorithmic independence, and the qualified artifact-provenance finding. These are facets of one enduring certificate concept rather than separate event-shaped nodes or an active dispute.
