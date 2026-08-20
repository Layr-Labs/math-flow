# Governed replay of the 152-point certificate

## Claim and exact scope

The [`configuration.txt`](configuration.txt) file in this contribution is a
byte-for-byte copy of the certificate in canonical transaction
`dfc0cc40d41105292a119840dcdbe6f22860cf43`.  The [`verify.py`](verify.py)
file is a byte-for-byte copy of the previously hosted replay checker in
transaction `0ffe9a12c3ad44cf136dd22df7083dcdd53af1b0`.  Its Python statements are
identical to the dependency's checker; the source files differ only because
the dependency has one additional empty line at end of file.  The exact
digests used in this replay are:

```text
configuration.txt  a23f1f55d9a914cff49fb6ba369b9f392f7af4c5ce08085267b3af1e7d7742c4
verify.py           43463d0207199ef42ae0dc9c88c67f855fd92b070fb8d007f477a6b2de1998ec
```

Running the copied checker on the copied configuration decodes exactly 152
distinct points in \(G_{76}=\{0,\ldots,75\}^2\), exhaustively evaluates the
exact integer determinant for all

\[
\binom{152}{3}=573800
\]

unordered triples, finds no zero determinant, and exits successfully.
Therefore the copied bytes certify a 152-point no-three-in-line subset of
\(G_{76}\), which embeds unchanged in \(G_{77}\) and re-establishes the
existing lower bound \(D(77)\ge152\).

[`verification.json`](verification.json) requests a governed replay of this
same checker and certificate.  The request itself does not assert that the
hosted run has already passed: its post-merge attestation is a separate,
content-addressed projection artifact.  A successful attestation establishes
that the pinned governed environment accepted the exact copied bytes; the
primary judge remains responsible for relating that encoded predicate to the
mathematical claim.

This is exactly one replay-and-identity claim, declared in
[`claims.json`](claims.json).  It re-verifies an established lower bound and
does not claim a new bound, optimality, or the exact value of \(D(77)\).

## Reproduction

Run from this directory with only the Python 3 standard library:

```bash
python3 -I -B verify.py configuration.txt
```

Expected output:

```text
verified 152 points on a 76 x 76 grid; no collinear triple
```

To compare the certificate with the declared dependency and the checker with
the prior replay in a canonical checkout:

```bash
cmp configuration.txt ../record-152-certificate/configuration.txt
cmp verify.py ../record-152-objective-verification/verify.py
shasum -a 256 configuration.txt verify.py
```

The checker:

1. recognizes and removes the leading certificate symmetry marker;
2. decodes two alphabet-indexed x-coordinates for each row;
3. checks distinctness and grid bounds; and
4. enumerates every unordered triple and rejects a zero determinant.

All arithmetic is exact Python integer arithmetic.  The run is deterministic,
has no network access or external package dependency, and writes no output
file.

## Governed verification request

The request pins verifier `python-stdlib-3-13-v1` at canonical spec digest

```text
sha256:fc7ed06b77396fabc1da84694b4d8a08800843f41ad8ca4b9cd666b67ba60884
```

and invokes `verify.py configuration.txt`.  The governed spec fixes Python
3.13 in a digest-pinned, networkless, read-only OCI environment with bounded
CPU, memory, process count, temporary storage, output, and runtime.  The
participant-authored request contains no result field; after merge, the
trusted attestation workflow publishes the exit status, stdout and stderr
digests, input-file manifest, verifier and environment digests, and invocation
on the projections branch.

## Provenance and correction

Canonical transaction `dfc0cc40d41105292a119840dcdbe6f22860cf43`
originally supplied the exact certificate and checker and attributes the
configuration to Achim Flammenkamp's maintained no-three-in-line database.
That transaction is the sole logical dependency of this claim and is declared
explicitly in `claims.json`, so its bounded artifacts are supplied to the
primary judge and retain provenance and credit.

Transaction `0ffe9a12c3ad44cf136dd22df7083dcdd53af1b0` attempted the first governed
replay but cited nonexistent transaction
`dfc0cc40d1193b8d5ca25e7f177fa48ff9a1b38d` and did not declare a dependency
manifest.  Its validity-v2 judgment was therefore unable to compare the
claimed artifact identity.  This new contribution corrects the transaction
ID, supplies `claims.json`, copies the dependency certificate exactly, retains
the already audited checker source without semantic change, and includes a
fresh governed verification request.  The older replay transaction is
historical provenance only and is not a logical dependency.

This repair was prepared and locally replayed by an OpenAI Codex solver agent
at Robert Raynor's request.  Mathematical and artifact authorship remains
credited to the canonical certificate contribution above.

## Limitations

- The attestation checks only the pinned program and input bytes; it is not an
  algorithmically independent proof.
- The certificate gives a lower bound of 152 only.  It says nothing about the
  existence or nonexistence of a 153- or 154-point set.
- Hosted acceptance is not stored in this contribution and must be read from
  the separately published trusted attestation.
