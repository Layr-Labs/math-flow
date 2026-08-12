# Exact certificate for the published lower bound S(6) >= 536

## Claim

The committed `coloring.csv` is a complete six-coloring of
`{1, 2, ..., 536}` with no monochromatic solution to `x + y = z`, including
the case `x = y`. It therefore independently replays the published baseline
lower bound

```text
S(6) >= 536.
```

This certificate does not improve the bound. The problem's published interval
remains `536 <= S(6) <= 1836`.

## Witness encoding and exact check

`coloring.csv` is the canonical expanded encoding: it has the exact header
`integer,color`, followed by one row for every integer in increasing order,
with colors numbered 1 through 6. `published-symmetric.json` preserves the
compact form printed by the source paper. Each ordinary representative `r`
encodes both `r` and `537-r` in the same color. The exceptional pair is
recorded explicitly as `[179, 4]` and `[358, 1]`, exactly as printed.

Run from this directory with Python 3 and only the standard library:

```bash
python3 -I -B verify.py published-symmetric.json coloring.csv
```

Expected output:

```text
verified 6-coloring of 1..536: class sizes 129,86,110,77,64,70; all 71824 in-range x<=y Schur triples are nonmonochromatic
```

The checker:

1. validates the compact witness schema, `n = 536`, six nonempty color
   classes, and symmetry modulus 537;
2. rejects noncanonical, duplicate, out-of-range, or overlapping paired
   representatives and special assignments;
3. expands the compact source witness and requires exact coverage of `1..536`;
4. validates the CSV header, row count, canonical integer order, and color
   range, and requires exact agreement with the source witness; and
5. enumerates every integer triple with `1 <= x <= y` and
   `z = x + y <= 536`, rejecting a monochromatic triple. Thus `x = y` is
   included rather than silently omitted.

`verification.json` requests a replay by the repository's pinned, networkless
Python-standard-library verifier. A passing hosted attestation is evidence only
that the pinned checker accepted the pinned artifact bytes; mathematical
judgment remains separate.

## Primary-source provenance and attribution

The construction is due to Harold Fredricksen and Melvin M. Sweet:

- Harold Fredricksen and Melvin M. Sweet, “Symmetric Sum-Free Partitions and
  Lower Bounds for Schur Numbers,” *The Electronic Journal of Combinatorics*
  7 (2000), Research Paper 32, DOI
  [10.37236/1510](https://doi.org/10.37236/1510).
- [Official journal article page](https://www.combinatorics.org/ojs/index.php/eljc/article/view/v7i1r32).
- [Official primary PDF](https://www.combinatorics.org/ojs/index.php/eljc/article/download/v7i1r32/pdf),
  retrieved 2026-08-12, SHA-256
  `ae8541c564efd65785a0e1d2c778108d58fec4c060707d7c277dd7f3eecad259`.

Page 2 defines a symmetric partition and permits `(n+1)/3` and
`2(n+1)/3` to occupy different sets when 3 divides `n+1`. Page 6 prints the
536 construction, says that only the smaller ordinary member of each symmetric
pair is listed, and places the exceptional values 179 and 358 in sets 4 and 1,
respectively. `published-symmetric.json` is a transcription of that page,
separating those exceptions from the paired representatives. `coloring.csv`
is the deterministic full expansion.

The official PDF was independently checked both by layout-preserving text
extraction and by visual inspection of the rendered page. The construction,
the bound, and their mathematical authorship remain Fredricksen and Sweet's;
this contribution claims no originality or priority for the construction.

## Limitations

- The certificate proves only the already published lower bound `S(6) >= 536`.
- It supplies no coloring of 537 or higher and no upper-bound information.
- The PDF is not vendored. Its official URLs and exact content digest are
  recorded, while all witness bytes needed for offline replay are committed.
- The verifier establishes the encoded finite predicate; it does not explain
  how Fredricksen and Sweet found the coloring.

## Artifact authorship

The witness and mathematical construction are by Harold Fredricksen and Melvin
M. Sweet. Transcription, canonical expansion design, checker, and documentation
were produced by an OpenAI Codex research agent operating the Math Flow solver
workflow at Robert Raynor's request. Any transcription or implementation errors
in these artifacts are the agent's.
