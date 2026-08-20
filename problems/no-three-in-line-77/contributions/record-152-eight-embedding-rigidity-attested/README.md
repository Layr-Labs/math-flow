# Governed eight-embedding local rigidity certificate

## One claim and its exact scope

This contribution makes the single claim declared in
[`claims.json`](claims.json). The included
[`configuration.txt`](configuration.txt) decodes to a 152-point
no-three-in-line subset \(C\) of
\(G_{76}=\{0,\ldots,75\}^2\). Exact exhaustive computation establishes
that \(C\) is invariant under a quarter turn, has two distinct dihedral
images, and therefore has exactly eight distinct embeddings in \(G_{77}\):
the two images translated by the four vectors in \(\{0,1\}^2\).

For each of those eight embeddings \(E\), the included
[`rigidity.py`](rigidity.py) establishes all of the following:

1. every cell outside \(E\) is blocked by at least two distinct unordered
   pairs of points of \(E\);
2. deleting any one point of \(E\) frees no originally outside cell;
3. deleting any unordered pair of points of \(E\) frees at most one
   originally outside cell; and
4. exactly 16 unordered deletion pairs per embedding free one cell.

Consequently, if a no-three-in-line set \(S\subseteq G_{77}\) satisfies
\(|E\setminus S|\leq2\), then \(|S\setminus E|\leq1\) and
\(|S|\leq152\). Thus any such \(S\) with at least 153 points has
\(|E\setminus S|\geq3\), \(|S\setminus E|\geq4\), and symmetric
difference at least seven from every one of the eight embeddings.

This is a local statement about these eight embeddings only. It does not
classify arbitrary 152-point configurations, exclude other construction
families, prove an upper bound for \(D(77)\), or claim global optimality.

## Self-contained evidence

The three normative evidence files are local to this contribution:

```text
configuration.txt  a23f1f55d9a914cff49fb6ba369b9f392f7af4c5ce08085267b3af1e7d7742c4
rigidity.py         f38a91c67f0cc9a3505c49e21b06515d7b470286af6041cc23127fb0cb6da4d8
results.json        3d33115ac06da925edcfe6be64dd292124d1de525c8341ab23ccbc0c155737a5
```

The checker reads the included configuration directly. It first checks all
\(\binom{152}{3}=573800\) triples of the base configuration with exact
integer determinants. It then reconstructs every dihedral image and
translation, verifies that there are exactly eight distinct embeddings,
performs a complete per-cell line census, and independently reconstructs the
same blocking-pair table by walking every lattice line through every pair.
Every reported freeing is finally checked by direct determinant simulation.
The recomputed, fully enumerated census must be byte-for-byte equal to
[`results.json`](results.json).

Run from this directory using only the Python standard library:

```bash
python3 -I -B rigidity.py
```

The run is deterministic, uses exact integer arithmetic, has no network
access or external package dependency, and writes no file in verification
mode. Use `--write` only to regenerate the committed results during an
independent audit.

## Governed verification

[`verification.json`](verification.json) requests the approved
`python-stdlib-3-13-v1` verifier at canonical spec digest

```text
sha256:fc7ed06b77396fabc1da84694b4d8a08800843f41ad8ca4b9cd666b67ba60884
```

to execute `rigidity.py` in the pinned, networkless, read-only environment.
The request does not assert a hosted result. After merge, the terminal
attestation is published separately on the projections branch and binds the
exit status and output digests to the exact committed input manifest.

## Dependency and provenance

Canonical transaction
`bf1301b6b472841276f79852c2e7fe0499309684` is the sole declared reference.
It contains the same configuration bytes and has a VALID validity-v3
assessment backed by a successful governed replay. Declaring it preserves
the certificate's provenance and makes that bounded, valid evidence
available to the judge.

The mathematical local-rigidity assertion does not require an opaque earlier
certificate transaction: this contribution includes the exact configuration,
checks its no-three-in-line property again, and performs the entire local
census itself. In particular,
`dfc0cc40d41105292a119840dcdbe6f22860cf43` is historical provenance
reachable through the valid governed replay, not a declared premise here.
Transactions `c5e8096d942d57228bb4fed00f7617fb6b43af9f` and
`3baf1c8586af31bbd6509d0fd3e552658c03673b` are superseded attempts at this
local result, and `0ffe9a12c3ad44cf136dd22df7083dcdd53af1b0` is not used.
None of those historical transactions is a dependency of the claim.

This repair was prepared and exhaustively replayed by an OpenAI Codex solver
agent at Robert Raynor's request. The underlying record configuration retains
its prior mathematical provenance.

## Limits of the certificate

- The hosted attestation checks the pinned program and files; it is not an
  algorithmically independent proof.
- The exhaustive conclusion is only the stated depth-two neighborhood of the
  eight embeddings.
- No conclusion about the exact value of \(D(77)\) follows.
