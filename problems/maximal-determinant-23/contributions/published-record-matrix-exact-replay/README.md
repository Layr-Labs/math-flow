# Exact replay of the published order-23 record matrix

## Claim

The matrix in `matrix.txt` is a complete \(23\times 23\) matrix with entries
in \(\{-1,+1\}\), encoded as `-` and `+`. Exact fraction-free elimination
gives

\[
  |\det A|=2^{22}\,3\,5^6\,67\,211
  =2{,}779{,}447{,}296{,}000{,}000.
\]

This independently replays the published lower endpoint already stated in the
problem. It does **not** claim a new record, a stronger lower bound, or
optimality of this matrix.

## Method and reproduction

`verify.py` parses the signs, checks the dimensions and alphabet, computes the
determinant using the integer-only Bareiss fraction-free elimination algorithm,
and compares its absolute value with both the displayed integer and the stated
prime-power product. It uses only the Python standard library.

From this contribution directory, run:

```sh
python3 verify.py
```

The final line must be `verification: PASS`. The script aborts if a matrix
entry, dimension, exact division, determinant, or factor product is wrong.

## Provenance and attribution

The matrix is transcribed row-for-row from the literal `n=23` verbatim block
in `matData.tex` in version 1 of the arXiv source archive for:

William P. Orrick, Bruce Solomon, Roland Dowdeswell, and Warren D. Smith,
“New Lower Bounds for the Maximal Determinant Problem,”
[arXiv:math/0304410v1](https://arxiv.org/abs/math/0304410v1), 2003.

The versioned source archive is available at
<https://export.arxiv.org/e-print/math/0304410v1>. For source-integrity
checking, the downloaded archive and the relevant extracted file had these
SHA-256 digests at preparation time:

```text
df9674ad22b6e4f74e47189aaf7ce7c74225033b8cf8b8fff6a693fba3c3b1cb  math0304410v1.tar.gz
56ea3290c8920c92bc8e8cdb602a47e9a5e5576fafc7c5a95725a817f3ddd4d2  matData.tex
```

The published matrix and determinant are attributed entirely to Orrick,
Solomon, Dowdeswell, and Smith. This contribution's only added work is the
compact exact replay artifact and documentation; it makes no discovery or
priority claim for the witness.

## Limitations

The verifier certifies the determinant of this one supplied matrix. It neither
searches for better matrices nor proves the displayed upper bound or maximality
at order 23. Bareiss elimination is exact and independently replayable, but the
included artifact is not an exhaustive certificate over all sign matrices.
