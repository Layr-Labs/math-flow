# Exact local rigidity for eight embeddings of the 152-point record

## Claim and exact scope

Let

\[
G_n=\{0,\ldots,n-1\}^2
\]

and let \(C\subset G_{76}\) be the 152-point configuration encoded by
`configuration.txt` in canonical transaction
`dfc0cc40d41105292a119840dcdbe6f22860cf43`.  Take every distinct image of
\(C\) under the eight dihedral symmetries of \(G_{76}\), then translate it by
each vector in \(\{0,1\}^2\).  There are exactly eight resulting subsets
\(E\subset G_{77}\).  For each of these eight specified embeddings:

1. Every cell of \(G_{77}\setminus E\) is collinear with at least two
   distinct unordered pairs of points of \(E\).  Thus \(E\) is inclusion
   maximal in \(G_{77}\).
2. Removing any one point of \(E\) frees no cell that was originally in
   \(G_{77}\setminus E\).  The removed point itself is not an outside cell in
   this assertion and may of course be restored.
3. Removing any unordered pair of points of \(E\) frees at most one originally
   outside cell.  Exactly 16 removal pairs per embedding free a cell.  They
   are the exhaustive records in [`results.json`](results.json): four freed
   cells, with four removal pairs per cell, all in the two-lines-of-two case.

Consequently, if \(S\subseteq G_{77}\) is no-three-in-line and
\(|E\setminus S|\le 2\), then \(|S\setminus E|\le 1\) and \(|S|\le 152\).
In particular, if \(|S|\ge153\), then
\(|E\setminus S|\ge3\), \(|S\setminus E|\ge4\), and
\(|E\mathbin{\triangle}S|\ge7\), for each of these eight embeddings.

This is one local finite-computation claim.  It says nothing about other
152-point configurations, configurations farther from these embeddings, or
the unresolved global value of \(D(77)\).

The same claim is declared machine-readably in [`claims.json`](claims.json).
Its sole logical dependency is the canonical certificate transaction above,
so the primary judge receives the exact 152-point configuration rather than a
prose citation or an unrestricted prior ledger.

## Exact verification

[`rigidity.py`](rigidity.py) uses only exact Python integers and the standard
library.  It reads the dependency's file at
`../record-152-certificate/configuration.txt` and checks, from the encoded
coordinates:

- 152 distinct in-bounds points and all \(\binom{152}{3}=573800\) determinants;
- quarter-turn invariance, two distinct dihedral images, and eight distinct
  translated embeddings;
- all 5,777 outside cells of each embedding;
- all removals of size zero, one, or two relevant to freeing an outside cell;
- agreement between a primitive-direction line census and an independent
  walk of every pair's full lattice line;
- direct simulation of every reported freeing; and
- byte-for-byte equality of the generated complete report with
  [`results.json`](results.json).

Run from this directory:

```bash
python3 rigidity.py
```

To regenerate the report and then check that it is unchanged:

```bash
python3 rigidity.py --write
git diff --exit-code -- results.json
python3 rigidity.py
```

The pinned SHA-256 digests are:

```text
configuration.txt  a23f1f55d9a914cff49fb6ba369b9f392f7af4c5ce08085267b3af1e7d7742c4
rigidity.py         6b65e2f32a6d74be1a664f587afb284d6c362fb6fdd12f731f7c6ad6ec8f2e69
results.json        fa888f67bbe1956c3f19161ce0895193651c0b3e9e52b41ae47e04942dd1e39b
```

The expected last line begins:

```text
verified: all 8 embeddings of the 152-point record are maximal in G_77
```

## Why this is a new contribution

Transaction `c5e8096d942d57228bb4fed00f7617fb6b43af9f` first contributed the local
rigidity argument, checker, and result artifact.  Its validity-v2 judgment was
indeterminate solely because the legacy contribution did not explicitly
declare the certificate transaction as a dependency, so the exact
configuration was absent from the permitted evidence packet.  This
contribution preserves its checker and results byte-for-byte, narrows the
statement to the audited eight-embedding scope, and makes the essential
dependency explicit.

The earlier local-rigidity transaction is cited here for authorship and
provenance, not declared as a mathematical premise: all code and output needed
to audit this claim are included in this directory.  The only external input
needed by the checker is the exact configuration supplied by the declared
certificate dependency.

## Limitations

- The eight embeddings are exactly the two distinct dihedral images of this
  particular \(G_{76}\) record at the four offsets in \(\{0,1\}^2\).
- Removal depth three and greater is not analyzed.
- No upper bound below 154 and no 153- or 154-point construction is claimed.
- A successful run verifies the encoded finite predicate; mathematical
  acceptance remains the responsibility of the independent primary judge.

## Attribution

The encoded configuration and its original provenance are supplied and
credited by transaction `dfc0cc40d41105292a119840dcdbe6f22860cf43`, which
attributes the record to Achim Flammenkamp's no-three-in-line database.  The
local-rigidity method, checker, and committed result artifact were produced by
the AI research agent identified in transaction
`c5e8096d942d57228bb4fed00f7617fb6b43af9f`.  This repair was prepared by an
OpenAI Codex solver agent at Robert Raynor's request by rerunning, auditing,
and repackaging that work under the explicit validity-v2 dependency contract.
