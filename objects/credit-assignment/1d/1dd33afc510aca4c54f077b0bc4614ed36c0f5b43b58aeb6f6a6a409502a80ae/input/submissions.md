<contribution>
ordinal: 1
transaction_id: fb88b7832c0fa7e84c1583110a7df800571bca02
contribution_id: published-record-matrix-exact-replay
author: Robert Raynor
<artifact path="problems/maximal-determinant-23/contributions/published-record-matrix-exact-replay/README.md">
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

</artifact>
<artifact path="problems/maximal-determinant-23/contributions/published-record-matrix-exact-replay/matrix.txt">
+-+----++----++++++++++
-++--++----++--++++++++
++-++----++----++++++++
--++---++++++--++--++--
--+-+--++++++----++--++
-+-----+++------++--++-
-+-----++-+----+--++--+
+--++++++--+---+--+-++-
+--++++++---+---++-+--+
--++++----------+-++-+-
--+++-+--------+-+--+-+
-+-++--+---+++++-+-+-+-
-+-++---+--++++-+-+-+-+
+----------+++---++++--
+----------++-+++----++
++++--++--++--+-+++----
++++-+--++--+-++-++----
+++-++--+-++-+-+++-----
+++-+-++-+--++-++-+----
++++--+-++-+-+-----+-++
++++-+-+--+-++------+++
+++-++-+-+-+--+----++-+
+++-+-+-+-+-+-+----+++-

</artifact>
<artifact path="problems/maximal-determinant-23/contributions/published-record-matrix-exact-replay/verify.py">
#!/usr/bin/env python3
"""Exactly verify the determinant of the published order-23 sign matrix."""

from pathlib import Path


ORDER = 23
EXPECTED_FACTORS = ((2, 22), (3, 1), (5, 6), (67, 1), (211, 1))
EXPECTED_ABS_DETERMINANT = 2_779_447_296_000_000


def read_sign_matrix(path: Path) -> list[list[int]]:
    rows = path.read_text(encoding="ascii").splitlines()
    if len(rows) != ORDER:
        raise ValueError(f"expected {ORDER} rows, found {len(rows)}")
    if any(len(row) != ORDER for row in rows):
        raise ValueError("every row must contain exactly 23 signs")
    if any(sign not in "+-" for row in rows for sign in row):
        raise ValueError("matrix entries must be encoded only as '+' or '-'")
    return [[1 if sign == "+" else -1 for sign in row] for row in rows]


def bareiss_determinant(matrix: list[list[int]]) -> int:
    """Compute a square integer matrix determinant by exact Bareiss steps."""
    a = [row[:] for row in matrix]
    n = len(a)
    if n == 0 or any(len(row) != n for row in a):
        raise ValueError("matrix must be nonempty and square")

    determinant_sign = 1
    previous_pivot = 1
    for column in range(n - 1):
        pivot_row = next(
            (row for row in range(column, n) if a[row][column] != 0), None
        )
        if pivot_row is None:
            return 0
        if pivot_row != column:
            a[column], a[pivot_row] = a[pivot_row], a[column]
            determinant_sign *= -1

        pivot = a[column][column]
        for row in range(column + 1, n):
            for other_column in range(column + 1, n):
                numerator = (
                    a[row][other_column] * pivot
                    - a[row][column] * a[column][other_column]
                )
                quotient, remainder = divmod(numerator, previous_pivot)
                if remainder != 0:
                    raise ArithmeticError("Bareiss division was not exact")
                a[row][other_column] = quotient
            a[row][column] = 0
        previous_pivot = pivot

    return determinant_sign * a[-1][-1]


def main() -> None:
    matrix = read_sign_matrix(Path(__file__).with_name("matrix.txt"))
    determinant = bareiss_determinant(matrix)
    factor_product = 1
    for prime, exponent in EXPECTED_FACTORS:
        factor_product *= prime**exponent

    if factor_product != EXPECTED_ABS_DETERMINANT:
        raise ArithmeticError("stated factorization does not equal stated integer")
    if abs(determinant) != factor_product:
        raise ArithmeticError("matrix determinant does not equal stated value")

    factor_text = " * ".join(
        str(prime) if exponent == 1 else f"{prime}^{exponent}"
        for prime, exponent in EXPECTED_FACTORS
    )
    print(f"order: {len(matrix)}")
    print(f"determinant: {determinant}")
    print(f"absolute determinant: {abs(determinant)}")
    print(f"factorization: {factor_text}")
    print("verification: PASS")


if __name__ == "__main__":
    main()

</artifact>
</contribution>