# Replayable objective verification of the 152-point record

This contribution republishes the exact `record-152-certificate` checker and
certificate bytes with a canonical `verification.json` request. Its purpose is
to produce a durable, independently replayable objective attestation through
Math Flow's trusted hosted verifier path.

## Scope

The encoded configuration is byte-for-byte identical, and the checker logic is
identical, to the artifacts in the earlier canonical contribution
`record-152-certificate` (transaction
`dfc0cc40d1193b8d5ca25e7f177fa48ff9a1b38d`). The checker establishes that the
payload decodes to 152 distinct points in the `76 x 76` grid and that every
triple has nonzero integer determinant. Since that grid embeds into the
`77 x 77` grid, this re-verifies the existing lower bound

\[
D(77) \ge 152.
\]

This is independent verification infrastructure, not a new bound and not a
claim about optimality. A successful attestation proves only that the pinned
checker accepted these pinned bytes in the governed environment; judgment of
whether the encoding captures the stated mathematics remains separate.

## Reproduction

Run locally with Python 3 and the standard library:

```bash
python3 -I -B verify.py configuration.txt
```

The expected output is:

```text
verified 152 points on a 76 x 76 grid; no collinear triple
```

After canonical merge, `verification.json` requests the repository-approved
`python-stdlib-3-13-v1` verifier. The trusted workflow should execute it in the
digest-pinned, networkless, read-only OCI environment and publish the resulting
content-addressed attestation separately on the `projections` branch.
