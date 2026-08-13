#!/usr/bin/env python3
"""Verify the exact divisibility-rounded order-23 upper endpoint."""

from math import isqrt


ORDER = 23
DIVISOR = 2 ** (ORDER - 1)
RADICAND = 505
COEFFICIENT_FACTOR = 3 * 5**6 * 675
ROUNDED_COEFFICIENT = 711_034_613
ROUNDED_UPPER_BOUND = 2_982_295_321_444_352
ORDINARY_INTEGER_FLOOR = 2_982_295_321_630_773


def bareiss_determinant(matrix: list[list[int]]) -> int:
    """Return the exact determinant of a square integer matrix."""
    a = [row[:] for row in matrix]
    n = len(a)
    if n == 0 or any(len(row) != n for row in a):
        raise ValueError("matrix must be nonempty and square")

    sign = 1
    previous_pivot = 1
    for column in range(n - 1):
        pivot_row = next(
            (row for row in range(column, n) if a[row][column] != 0), None
        )
        if pivot_row is None:
            return 0
        if pivot_row != column:
            a[column], a[pivot_row] = a[pivot_row], a[column]
            sign = -sign

        pivot = a[column][column]
        for row in range(column + 1, n):
            for other_column in range(column + 1, n):
                numerator = (
                    a[row][other_column] * pivot
                    - a[row][column] * a[column][other_column]
                )
                quotient, remainder = divmod(numerator, previous_pivot)
                if remainder:
                    raise ArithmeticError("Bareiss division was not exact")
                a[row][other_column] = quotient
            a[row][column] = 0
        previous_pivot = pivot

    return sign * a[-1][-1]


def normalized_sign_matrix(binary_core: list[list[int]]) -> list[list[int]]:
    """Construct [[1, 1^T], [1, J - 2B]] from a square zero-one core B."""
    size = len(binary_core)
    if size == 0 or any(len(row) != size for row in binary_core):
        raise ValueError("binary core must be nonempty and square")
    if any(entry not in (0, 1) for row in binary_core for entry in row):
        raise ValueError("binary core entries must be zero or one")
    return [[1] * (size + 1)] + [
        [1] + [1 - 2 * entry for entry in row] for row in binary_core
    ]


def main() -> None:
    squared_coefficient_bound = COEFFICIENT_FACTOR**2 * RADICAND
    lower_square = ROUNDED_COEFFICIENT**2
    upper_square = (ROUNDED_COEFFICIENT + 1) ** 2

    if not lower_square < squared_coefficient_bound < upper_square:
        raise ArithmeticError("integer square certificate is invalid")
    if isqrt(squared_coefficient_bound) != ROUNDED_COEFFICIENT:
        raise ArithmeticError("rounded coefficient is not the exact floor")
    if DIVISOR * ROUNDED_COEFFICIENT != ROUNDED_UPPER_BOUND:
        raise ArithmeticError("rounded endpoint product is inconsistent")

    squared_real_bound = DIVISOR**2 * squared_coefficient_bound
    if isqrt(squared_real_bound) != ORDINARY_INTEGER_FLOOR:
        raise ArithmeticError("ordinary integer floor is inconsistent")
    if not (
        ROUNDED_UPPER_BOUND**2
        < squared_real_bound
        < (ROUNDED_UPPER_BOUND + DIVISOR) ** 2
    ):
        raise ArithmeticError("endpoint is not the largest permitted multiple")

    identity_core = [
        [1 if row == column else 0 for column in range(ORDER - 1)]
        for row in range(ORDER - 1)
    ]
    sharpness_matrix = normalized_sign_matrix(identity_core)
    sharpness_determinant = bareiss_determinant(sharpness_matrix)
    if sharpness_determinant != DIVISOR:
        raise ArithmeticError("sharpness witness determinant is inconsistent")

    determinant_two_core = [
        [1, 1, 0],
        [1, 0, 1],
        [0, 1, 1],
    ]
    determinant_two_core += [
        [0] * 3 + [1 if row == column else 0 for column in range(ORDER - 4)]
        for row in range(ORDER - 4)
    ]
    for row in range(3):
        determinant_two_core[row] += [0] * (ORDER - 4)
    second_matrix = normalized_sign_matrix(determinant_two_core)
    second_determinant = bareiss_determinant(second_matrix)
    if second_determinant != -2 * DIVISOR:
        raise ArithmeticError("second quotient witness determinant is inconsistent")

    print(f"universal divisor: {DIVISOR}")
    print(f"coefficient factor: {COEFFICIENT_FACTOR}")
    print(f"lower square: {lower_square}")
    print(f"squared irrational coefficient: {squared_coefficient_bound}")
    print(f"upper square: {upper_square}")
    print(f"rounded coefficient: {ROUNDED_COEFFICIENT}")
    print(f"ordinary integer floor: {ORDINARY_INTEGER_FLOOR}")
    print(f"divisibility-rounded upper bound: {ROUNDED_UPPER_BOUND}")
    print(
        "improvement over ordinary floor: "
        f"{ORDINARY_INTEGER_FLOOR - ROUNDED_UPPER_BOUND}"
    )
    print(f"sharpness witness determinant: {sharpness_determinant}")
    print(f"second quotient witness determinant: {second_determinant}")
    print("verification: PASS")


if __name__ == "__main__":
    main()
