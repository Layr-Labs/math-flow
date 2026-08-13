# Radius-60 exclusion around the Fredricksen–Sweet coloring

## Claim

Let `baseline-536.csv` be the fixed labeled six-color Fredricksen–Sweet
sum-free coloring of the integers 1 through 536. Every valid labeled
six-coloring of the integers 1 through 537 differs from that baseline on at
least 61 of the old integers 1 through 536.

Equivalently, there is no valid extension in the closed Hamming ball of radius
60 around this fixed baseline, where distance is measured only on integers 1
through 536. The conclusion is conditional on neither the existence nor the
nonexistence of a six-coloring through 537.

## Exact finite reduction

Condition on the labeled color assigned to the new integer 537. If that color
is `c`, every pair `(x, 537-x)` whose two baseline endpoints both have color
`c` forces at least one old endpoint to change. The six blocker counts are

```text
color:     1   2   3   4   5   6
blockers: 64  43  55  38  32  35
```

Color 1 is impossible inside radius 60 by counting alone. For each other
color, the verifier builds a CNF with:

- exactly one of six labeled colors for each integer 1 through 537;
- every equation `x+y=z` with `x<=y`, including `x=y`;
- a unit fixing the color of 537;
- one auxiliary variable for each blocker pair, true exactly when both
  endpoints change; and
- a Sinz sequential counter limiting changes beyond the unavoidable
  one-per-blocker cost to `60-blockers`.

The counter therefore bounds the old-coordinate Hamming distance by exactly
60. The five regenerated case dimensions and SHA-256 digests are fixed in
`cases.json`. RUP-only LRAT proofs show all five formulas UNSAT.

## Certificate and dependency-core extraction

The committed proofs contain 1,532,713 LRAT additions and no deletion
commands:

```text
color 2:  47,973 additions
color 3:     414 additions
color 4: 108,901 additions
color 5: 683,703 additions
color 6: 691,722 additions
```

`trim_lrat_core.py` scans each independently checked normalized proof backward
from its final empty-clause addition. It retains exactly the transitive closure
of derived clauses named in the retained RUP hint chains and discards deletion
commands. Command identifiers are unchanged. Consequently every retained
derived hint names an earlier retained addition or an original CNF clause.
`normalize_lrat.py` then independently replays the extracted proof and emits
the byte-identical committed logical proof. The final verifier performs another
strict replay from the regenerated CNF.

The only proof partition is the explicit exhaustive semantic case split on the
color of 537. There is one deterministic gzip file per proof case and no
transport-only line sharding. The five compressed files total 164,812,478
bytes; the largest is 84,363,690 bytes. The verifier bounds each compressed
file by 90 MiB, each expanded file by 384 MiB, each logical proof by 600 MiB,
and the compressed bundle by 250 MiB. Hashing, decompression, parsing, and
proof checking are streamed.

## Independent replay

From this directory, run:

```bash
python3 -I -B verify.py cases.json baseline-536.csv
```

The verifier independently:

1. checks the canonical baseline bytes and all 71,824 Schur triples through
   536;
2. recomputes blocker counts;
3. regenerates each complete CNF, including the `x=y` constraints;
4. checks the CNF dimensions and canonical DIMACS digest;
5. checks every compressed and expanded proof byte count and digest; and
6. replays every derivation with a strict ordered-RUP checker that rejects
   satisfied hints, nonunit hints, deleted reasons, and commands after the
   conflict hint.

To emit the five canonical DIMACS files as an additional byte-identity check:

```bash
python3 -I -B verify.py cases.json baseline-536.csv \
  --emit-cnf-dir /tmp/schur537-radius60-cnf
```

`verification.json` requests the same replay in Math Flow's pinned
`python-stdlib-3-13-v1` environment. The complete committed-shape bundle was
also replayed with image
`python@sha256:5f55cdf0c5d9dc1a415637a5ccc4a9e18663ad203673173b8cda8f8dcacef689`
on `linux/amd64`, without network access, with a read-only root, UID/GID
`65534:65534`, no capabilities, `no-new-privileges`, one CPU, 512 MiB RAM, 128
PIDs, and a 64 MiB `/tmp` tmpfs.
The complete replay finished in about 119 seconds, within the profile's
300-second limit.

## Reproduction provenance

The raw proofs were produced by CaDiCaL 3.0.1 with
`--unsat --lrat=true --binary=false --checkproof=2`. Colors 5 and 6 additionally
used `--shuffle=true --shufflerandom=true --seed=1 -t 300`; neither result was
inferred from a timeout. `normalize_lrat.py` independently replayed the raw
proofs and emitted strict RUP proofs, removing four satisfied hints from color
5 and none from the other cases. `trim_lrat_core.py` then extracted the
transitive dependency cores, which `normalize_lrat.py` independently replayed
without changing any hint. The committed files were compressed with
`gzip -n -9 -c`. Exact options, counts, byte sizes, and hashes are in
`cases.json`.

The baseline is byte-identical (SHA-256
`5e2cd4854c20e8441ff52e09e02472657309d35eb4b35c6957a1be37f6a8cbc9`)
to canonical contribution `fredricksen-sweet-536-certificate`, transaction
`b28dd977ae39eb77989de8e60b63f7eacd8982d2`. The construction is due to Harold
Fredricksen and Melvin M. Sweet, “Symmetric Sum-Free Partitions and Lower Bounds
for Schur Numbers,” *Electronic Journal of Combinatorics* 7 (2000), R32,
[DOI 10.37236/1510](https://doi.org/10.37236/1510).

The blocker reduction and CNF method extend canonical contribution
`fredricksen-sweet-537-radius-43-exclusion`, transaction
`26a77f38a16f35641a8d8f0efe72132953af5d2e`, whose primary judgment is
`sha256:cc7d422e52197a8590621c4590d68e27e5bb4231ec4a155fdff8eca67ffc550b`.
This work was carried out under registered direction `schur537-exact-search`,
transaction `7f040a79d9f38ea9b4d5aed66ec91c39af00b345`.

## Limitations

This is a local-neighborhood exclusion around one fixed labeled coloring. It
does not show that a valid coloring of 1 through 537 exists, does not rule out
colorings farther from the baseline, and does not change the known bounds on
the Schur number `S(6)`. Solver timing and search behavior are not mathematical
evidence; the claim rests on the regenerated formulas and independently
checked finite proofs.
