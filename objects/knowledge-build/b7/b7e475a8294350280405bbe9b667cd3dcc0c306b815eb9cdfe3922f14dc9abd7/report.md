# Knowledge-Formation Report

## Node: root

- **Type:** Root
- **Title:** Research state for no-three-in-line at grid size 77
- **Status:** Active
- **Parent:** None

For

\[
G_{77}=\{0,1,\ldots,76\}^2,
\]

the exact maximum cardinality \(D(77)\) of a subset containing no three distinct collinear points remains unresolved. The accepted primary judgments support the certified interval

\[
152\le D(77)\le154.
\]

No accepted judgment determines whether the exact value is \(152\), \(153\), or \(154\).

The active root-level organization is:

1. **`no-three-in-line/d77-exact-value`** — the central exact-value question and the current global lower and upper bounds.
2. **`no-three-in-line/d77-row-column-occupancy`** — necessary row and column occupancy conditions for hypothetical 153- and 154-point configurations.
3. **`programs/rotational-symmetry`** — the classification of rotations preserving finite noncollinear lattice sets and its conditional consequences for hypothetical 153- and 154-point subsets of \(G_{77}\).
4. **`programs/embedded-g76-record-rigidity`** — the particular 152-point \(G_{76}\) record, its specified embeddings in \(G_{77}\), and the accepted local saturation and rigidity results around those embeddings.

Primary judgment `sha256:a470e4a9c0903097d9c860badaa8976cf32ed5336c154f11d8fad980d401f74e` supports both sides of the interval with high confidence. It accepts an exact, self-contained computational certificate for a 152-point no-three-in-line subset of \(G_{76}\), whose direct inclusion in \(G_{77}\) gives the lower bound, and it accepts the elementary two-points-per-row argument giving the upper bound. It also supplies the root-level occupancy restrictions now organized in `no-three-in-line/d77-row-column-occupancy`.

The previously accepted results remain in force:

- Primary judgment `sha256:21f3e6bb405eaaf804b58020a1695c213023b0dd3f1d25a08248fb5a48750eca` accepts conditional rotational-symmetry restrictions without resolving the global problem.
- Primary judgment `sha256:71fbde8d269728a92be52f6401e857230043ee6938c45f810c32308d88fb9927` accepts local rigidity results for eight specified embeddings of the particular \(G_{76}\) record. Those results exclude improvements obtained after removing at most two points from one of those embeddings, but they do not constrain unrelated configurations or perturbations requiring at least three removals.
- Primary judgment `sha256:8c5f8eeb55af54b575fd3d46473e7894095afd6a4741186fe0583d3d0feade8a` accepts the mathematical implication of a republished executable certificate while distinguishing it from a completed governed hosted replay and from an algorithmically independent implementation.

No conflict records, unresolved reconciliations, needs-evidence outcomes, or incompatible reconciliation outcomes have been supplied. There are therefore no active dispute nodes in the current state.

**Authoritative provenance**

- Baseline certificate and elementary-bound judgment: `sha256:a470e4a9c0903097d9c860badaa8976cf32ed5336c154f11d8fad980d401f74e`
- Baseline subject and evidence transaction: `dfc0cc40d41105292a119840dcdbe6f22860cf43`, ledger position 1
- Rotational-symmetry judgment: `sha256:21f3e6bb405eaaf804b58020a1695c213023b0dd3f1d25a08248fb5a48750eca`
- Rotational-symmetry subject transaction: `29ccbd396781fd36d436ed2e6d0952a4730361b9`, ledger position 4
- Embedded-record rigidity judgment: `sha256:71fbde8d269728a92be52f6401e857230043ee6938c45f810c32308d88fb9927`
- Embedded-record rigidity subject transaction: `c5e8096d942d57228bb4fed00f7617fb6b43af9f`, ledger position 2
- Republishing and hosted-replay judgment: `sha256:8c5f8eeb55af54b575fd3d46473e7894095afd6a4741186fe0583d3d0feade8a`
- Republishing subject transaction: `0ffe9a12c3ad44cf136dd22df7083dcdd53af1b0`, ledger position 5
- **Lineage:** None

## Change: root

Updated the root account to incorporate the direct judgment provenance for both certified bounds and to add the durable root-level occupancy result. The two existing research programs remain coherent and unchanged, and no supplied conflict requires a dispute node or taxonomy restructuring.

## Node: no-three-in-line/d77-exact-value

- **Type:** Central question and global bounds
- **Title:** Exact value and certified interval for \(D(77)\)
- **Status:** Active and unresolved
- **Parent:** `root`

The central question is to determine the maximum size \(D(77)\) of a no-three-in-line subset of \(G_{77}\).

The accepted primary judgments support the current certified interval

\[
152\le D(77)\le154.
\]

### Certified lower bound

Primary judgment `sha256:a470e4a9c0903097d9c860badaa8976cf32ed5336c154f11d8fad980d401f74e` accepts an exact, self-contained computational certificate for 152 distinct points in \(G_{76}\) with no three collinear. Because

\[
G_{76}\subset G_{77},
\]

the same points establish

\[
D(77)\ge152.
\]

Primary judgment `sha256:8c5f8eeb55af54b575fd3d46473e7894095afd6a4741186fe0583d3d0feade8a` separately accepts the same lower-bound implication from a republished executable package. That later package re-verifies the existing bound rather than improving it. Its evidence does not establish a completed governed hosted run, and its checker is not algorithmically independent of the earlier verifier; those qualifications do not alter the certified mathematical interval.

### Certified upper bound

Primary judgment `sha256:a470e4a9c0903097d9c860badaa8976cf32ed5336c154f11d8fad980d401f74e` accepts the elementary upper-bound argument. Every horizontal row of \(G_{77}\) is a line and can contain at most two selected points. Since there are 77 rows,

\[
D(77)\le 2\cdot77=154.
\]

The corresponding column argument gives the same capacity.

### Necessary occupancy restrictions

The same primary judgment accepts the following necessary conditions:

- a hypothetical 154-point set must contain exactly two points in every row and exactly two points in every column;
- a hypothetical 153-point set must contain two points in 76 rows and one point in the remaining row, and likewise two points in 76 columns and one point in the remaining column.

These conditions are organized in `no-three-in-line/d77-row-column-occupancy`. They are necessary only and establish neither existence nor nonexistence at either cardinality.

### Other accepted restrictions

Primary judgment `sha256:21f3e6bb405eaaf804b58020a1695c213023b0dd3f1d25a08248fb5a48750eca` accepts the following rotational restrictions without improving the global bounds:

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
- other 152-point configurations, and larger configurations sufficiently far from every specified embedding, remain unconstrained by that computation.

### Unresolved scope

No accepted contribution supplies:

- a 153- or 154-point coordinate certificate;
- a global impossibility proof for either cardinality;
- a global exhaustive search resolving the interval; or
- an upper-bound argument improving \(D(77)\le154\).

The accepted certificate, occupancy, rotational, and local-rigidity results therefore do not select among

\[
D(77)=152,\qquad D(77)=153,\qquad D(77)=154.
\]

**Authoritative provenance**

- Baseline certificate, bounds, occupancy, and unresolved-status judgment: `sha256:a470e4a9c0903097d9c860badaa8976cf32ed5336c154f11d8fad980d401f74e`
- Baseline subject and evidence transaction: `dfc0cc40d41105292a119840dcdbe6f22860cf43`, ledger position 1
- Republishing and unchanged-lower-bound judgment: `sha256:8c5f8eeb55af54b575fd3d46473e7894095afd6a4741186fe0583d3d0feade8a`
- Republishing subject transaction: `0ffe9a12c3ad44cf136dd22df7083dcdd53af1b0`, ledger position 5
- Rotational-restrictions judgment: `sha256:21f3e6bb405eaaf804b58020a1695c213023b0dd3f1d25a08248fb5a48750eca`
- Rotational subject transaction: `29ccbd396781fd36d436ed2e6d0952a4730361b9`, ledger position 4
- Embedded-record rigidity judgment: `sha256:71fbde8d269728a92be52f6401e857230043ee6938c45f810c32308d88fb9927`
- Rigidity subject transaction: `c5e8096d942d57228bb4fed00f7617fb6b43af9f`, ledger position 2
- Represented claim keys include:
  - `d77/lower-bound-152`
  - `d77/upper-bound-154`
  - `d77/interval-152-154`
  - `d77/exact-value`
- **Lineage:** None

## Change: no-three-in-line/d77-exact-value

Updated the central question with direct primary-judgment support for both endpoints of the certified interval and with the newly accepted occupancy restrictions. Prior rotational, local-rigidity, certificate-replay, and unresolved-status qualifications are retained without changing their scope.

## Node: no-three-in-line/d77-row-column-occupancy

- **Type:** Structural result
- **Title:** Necessary row and column occupancy at sizes 153 and 154
- **Status:** Active; supported as necessary conditions only
- **Parent:** `root`

Primary judgment `sha256:a470e4a9c0903097d9c860badaa8976cf32ed5336c154f11d8fad980d401f74e` accepts precise row and column occupancy conditions for any no-three-in-line subset \(S\subseteq G_{77}\) whose cardinality is 153 or 154.

Every row and every column of \(G_{77}\) is a line, so each has occupancy at most two.

### Hypothetical 154-point sets

If \(|S|=154\), then \(S\) attains the full total capacity of the 77 rows. Consequently, every row must contain exactly two points. Applying the same capacity statement to the columns gives:

\[
|S|=154
\quad\Longrightarrow\quad
\begin{cases}
\text{every row contains exactly two points},\\
\text{every column contains exactly two points}.
\end{cases}
\]

### Hypothetical 153-point sets

If \(|S|=153\), the total deficiency from the row capacity \(154\) is exactly one. The accepted consequence is that exactly 76 rows contain two points and the remaining row contains one point. The same statement holds for columns:

\[
|S|=153
\quad\Longrightarrow\quad
\begin{cases}
76\text{ rows contain two points and one row contains one point},\\
76\text{ columns contain two points and one column contains one point}.
\end{cases}
\]

### Scope

These occupancy patterns are necessary conditions only. The primary judgment expressly qualifies that they do not:

- construct a 153- or 154-point set;
- prove that either cardinality is attainable;
- prove that either cardinality is impossible; or
- determine \(D(77)\).

The result is retained at root level because it constrains any hypothetical configuration at the two unresolved upper cardinalities, independently of the rotational-symmetry and particular-record rigidity programs.

**Authoritative provenance**

- Primary judgment: `sha256:a470e4a9c0903097d9c860badaa8976cf32ed5336c154f11d8fad980d401f74e`
- Subject and evidence transaction: `dfc0cc40d41105292a119840dcdbe6f22860cf43`, ledger position 1
- Represented claim keys:
  - `d77/154-point-row-column-occupancy`
  - `d77/153-point-row-column-occupancy`
  - `d77/153-154-occupancy-sufficiency`
- **Lineage:** None

## Change: no-three-in-line/d77-row-column-occupancy

Created a durable root-level structural node because the accepted occupancy conditions apply globally to all hypothetical 153- and 154-point configurations and form a separately reusable constraint, rather than belonging specifically to either existing research program.

## Node: no-three-in-line/g76-152-point-set

- **Type:** Certified configuration and verification result
- **Title:** The 152-point no-three-in-line configuration in \(G_{76}\)
- **Status:** Active; exact mathematical certificate supported, governed hosted replay not established
- **Parent:** `programs/embedded-g76-record-rigidity`

This node records the particular 152-point \(G_{76}\) certificate underlying the current lower bound and the accepted distinctions among its mathematical verification, its symmetry metadata, and the later hosted-replay request.

### Exact certificate

Primary judgment `sha256:a470e4a9c0903097d9c860badaa8976cf32ed5336c154f11d8fad980d401f74e` accepts the original transaction as an exact, self-contained computational certificate for 152 distinct points of \(G_{76}\) with no three collinear.

After removal of the initial symmetry marker `o`, the encoded payload splits into 76 consecutive pairs, representing two points in each row \(y=0,\ldots,75\). The judgment finds that:

- the payload represents \(2\cdot76=152\) points;
- all coordinate values lie in \(\{0,\ldots,75\}\);
- the two encoded points in each row differ;
- the verifier explicitly checks global point distinctness;
- the verifier checks grid membership; and
- the verifier checks every one of
  \[
  \binom{152}{3}=573{,}800
  \]
  unordered triples using the exact integer determinant
  \[
  (x_2-x_1)(y_3-y_1)-(x_3-x_1)(y_2-y_1).
  \]

The judgment notes that Python’s arbitrary-precision integers avoid overflow and that the verification uses no floating-point tolerances, heuristic sampling, or random search. It accepts the reported verification result, conditional on running the supplied script on the supplied certificate as stated.

The mathematical consequence is that the same 152 points embed directly into \(G_{77}\), supporting

\[
D(77)\ge152.
\]

This is the established baseline lower bound, not an improvement.

### Symmetry metadata

The original verifier accepts the leading marker `o` but does not itself check quarter-turn symmetry. Primary judgment `sha256:a470e4a9c0903097d9c860badaa8976cf32ed5336c154f11d8fad980d401f74e` finds that this omission does not affect the no-three-in-line certificate because the lower-bound implication depends only on the explicitly decoded points.

Quarter-turn symmetry of this particular coordinate set is separately supported by primary judgment `sha256:71fbde8d269728a92be52f6401e857230043ee6938c45f810c32308d88fb9927` and is organized in `no-three-in-line/g76-record-quarter-turn-symmetry-and-dihedral-orbit`. It is not independently established by the baseline certificate verifier alone.

### Republishing and hosted replay

Primary judgment `sha256:8c5f8eeb55af54b575fd3d46473e7894095afd6a4741186fe0583d3d0feade8a` accepts that a later transaction republishes the configuration unchanged in mathematical substance and supplies a deterministic exact verifier with the same checking logic.

Acceptance in the specified governed hosted-verifier environment is not established by the supplied evidence. The later transaction contains a verification request identifying a verifier specification, checker entry point, and certificate argument, but the judgment finds no content-addressed hosted attestation, exit status, execution transcript, or hosted output proving that the requested run occurred. The governing external schema and artifact-binding workflow were also unavailable for independent adjudication.

A future successful hosted run could provide execution independence. It would not provide algorithmic independence because the republished checker is copied from the earlier contribution. This qualification concerns the later replay claim, not the accepted mathematical certificate.

### Artifact identity and provenance

The later judgment supports identity in mathematical substance between the displayed coordinate set and the earlier baseline, and it supports equivalence of the displayed checker logic. Strict byte-for-byte identity, including line-ending and terminal-newline details, is not independently established by a checksum in the later transaction.

The republished README contains an erroneous provenance pointer. It names the earlier transaction as

```text
dfc0cc40d1193b8d5ca25e7f177fa48ff9a1b38d
```

whereas the authoritative earlier baseline transaction is

```text
dfc0cc40d41105292a119840dcdbe6f22860cf43
```

Primary judgment `sha256:8c5f8eeb55af54b575fd3d46473e7894095afd6a4741186fe0583d3d0feade8a` treats this as a clerical metadata error that does not affect the points, verifier, or lower-bound implication.

### Scope

The certificate establishes the existence of a 152-point no-three-in-line subset of \(G_{76}\), and consequently of \(G_{77}\). It does not supply:

- a 153- or 154-point configuration;
- a proof that 152 is optimal in \(G_{77}\);
- a completed governed hosted-verifier attestation;
- a new bound beyond \(152\le D(77)\le154\); or
- by itself, a verification of the leading symmetry marker.

The configuration remains nested beneath the embedded-record rigidity program because that program studies this particular record and its specified embeddings. Its global lower-bound consequence is recorded in the root-level exact-value node.

### Credit recorded by the judgments

- The coordinate construction predates the judged certificate packages and is attributed in the supplied materials to Achim Flammenkamp’s maintained database.
- Primary judgment `sha256:a470e4a9c0903097d9c860badaa8976cf32ed5336c154f11d8fad980d401f74e` records that Robert should be credited for making the baseline certificate self-contained and readily checkable through a reproduction and independent verifier, not for originating the underlying 152-point construction.
- The finer priority or authorship history of the coordinate construction is not determined by the supplied artifacts.
- The checker in the later republishing transaction is copied from the earlier baseline contribution.
- The later transaction receives credit for republishing the artifacts in replayable form and packaging a canonical hosted-verification request, not for discovering the configuration, devising a new algorithm, or improving the bound.
- The incorrect prior-transaction hash weakens the later provenance metadata but does not create a competing mathematical priority claim.

**Authoritative provenance**

- Original certificate judgment: `sha256:a470e4a9c0903097d9c860badaa8976cf32ed5336c154f11d8fad980d401f74e`
- Original certificate subject and evidence transaction: `dfc0cc40d41105292a119840dcdbe6f22860cf43`, ledger position 1
- Republishing and hosted-replay judgment: `sha256:8c5f8eeb55af54b575fd3d46473e7894095afd6a4741186fe0583d3d0feade8a`
- Republishing subject transaction: `0ffe9a12c3ad44cf136dd22df7083dcdd53af1b0`, ledger position 5
- Separate symmetry and orbit judgment: `sha256:71fbde8d269728a92be52f6401e857230043ee6938c45f810c32308d88fb9927`
- Represented claim keys include:
  - `no-three-in-line/g76-152-point-subset`
  - `no-three-in-line/g76-152-point-set`
  - `no-three-in-line/certificate-quarter-turn-symmetry`
  - `no-three-in-line/g76-152-certificate-hosted-replay-acceptance`
  - `no-three-in-line/g76-152-certificate-artifact-identity-and-provenance`
- **Lineage:** None

## Change: no-three-in-line/g76-152-point-set

Updated the stable certificate node with the direct original-certificate judgment, its exact encoding and exhaustive-check scope, and the explicit distinction between the unchecked symmetry marker and the separately verified symmetry result. The existing hosted-replay and artifact-provenance qualifications remain attached to the same mathematical configuration.

## Node: no-three-in-line/g76-record-quarter-turn-symmetry-and-dihedral-orbit

- **Type:** Structural result
- **Title:** Quarter-turn symmetry and specified embedding orbit of the 152-point \(G_{76}\) record
- **Status:** Active; supported with high confidence by the separate orbit analysis
- **Parent:** `programs/embedded-g76-record-rigidity`

Let \(C\subseteq G_{76}\) be the particular 152-point configuration supplied in the judged evidence.

Primary judgment `sha256:71fbde8d269728a92be52f6401e857230043ee6938c45f810c32308d88fb9927` supports with high confidence that the transformation

\[
(x,y)\longmapsto(75-y,x)
\]

preserves \(C\). Thus this particular coordinate set has quarter-turn symmetry.

The same judgment accepts that:

- the coordinate string decodes to 152 distinct points in \(G_{76}\);
- the no-three-in-line property was checked for all
  \[
  \binom{152}{3}=573{,}800
  \]
  triples using exact integer determinants;
- the eight transformations in the dihedral group of the square produce exactly two distinct images of \(C\); and
- applying the four translations
  \[
  (t_x,t_y)\in\{0,1\}^2
  \]
  to those two images produces exactly eight distinct subsets of \(G_{77}\).

Here “specified embedding” means only a dihedral image followed by one of those four translations. The result does not classify unrelated affine images, other \(G_{76}\) records, or general 152-point configurations in \(G_{77}\).

### Certificate-verifier qualification

Primary judgment `sha256:a470e4a9c0903097d9c860badaa8976cf32ed5336c154f11d8fad980d401f74e` finds that the original baseline certificate verifier accepts the leading symmetry marker `o` but does not check quarter-turn symmetry. That omission does not undermine the no-three-in-line certificate, but the verifier cannot independently establish symmetry as a separate property.

There is no conflict between the two judgments: the quarter-turn property is supported by the separate analysis accepted in judgment `sha256:71fbde8d269728a92be52f6401e857230043ee6938c45f810c32308d88fb9927`, not by the baseline verifier’s treatment of the marker.

### Credit recorded by the judgments

- The underlying coordinate set is attributed to Achim Flammenkamp’s maintained database.
- The orbit verification and embedding enumeration are attributed to the judged local-rigidity analysis, whose disclosure states that the analysis, code, and text were produced by an AI research agent at Robert Raynor’s request.
- The baseline certificate’s reproduction and exact no-three-in-line verifier do not independently receive credit for checking the quarter-turn property.

**Authoritative provenance**

- Symmetry and orbit primary judgment: `sha256:71fbde8d269728a92be52f6401e857230043ee6938c45f810c32308d88fb9927`
- Symmetry and orbit subject transaction: `c5e8096d942d57228bb4fed00f7617fb6b43af9f`
- Baseline-verifier qualification judgment: `sha256:a470e4a9c0903097d9c860badaa8976cf32ed5336c154f11d8fad980d401f74e`
- Baseline subject and evidence transaction: `dfc0cc40d41105292a119840dcdbe6f22860cf43`, ledger position 1
- Represented claim keys:
  - `no-three-in-line/g76-record-quarter-turn-symmetry-and-dihedral-orbit`
  - `no-three-in-line/certificate-quarter-turn-symmetry`
- **Lineage:** None

## Change: no-three-in-line/g76-record-quarter-turn-symmetry-and-dihedral-orbit

Updated the symmetry result to preserve the new judgment’s verifier-scope qualification: the baseline checker does not test the symmetry marker, while the existing separate orbit analysis remains the supporting source for quarter-turn symmetry. This clarification changes provenance and verification scope, not the accepted structural result.
