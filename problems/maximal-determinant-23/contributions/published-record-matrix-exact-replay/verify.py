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
