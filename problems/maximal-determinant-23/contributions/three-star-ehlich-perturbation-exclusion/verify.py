#!/usr/bin/env python3
"""Exclude record-level three-star perturbations of order-23 Ehlich blocks."""

from collections import Counter, defaultdict
from fractions import Fraction
from itertools import combinations_with_replacement, permutations, product
import json
from math import isqrt, lcm
from pathlib import Path


ORDER = 23
SIGN_DIVISOR = 2 ** (ORDER - 1)
GRAM_DIVISOR = SIGN_DIVISOR**2
RECORD_COEFFICIENT = 3 * 5**6 * 67 * 211
EXPECTED_PARTITION_COUNT = 1_255
EXPECTED_INDEXED_SPEC_COUNT = 1_882_943
EXPECTED_CANONICAL_SPEC_COUNT = 102_799
EXPECTED_ABOVE_COUNT = 74_896
EXPECTED_SQUARE_COUNT = 104
EXPECTED_HASSE_COUNT = 83
EXPECTED_EMPTY_PATTERN_COUNT = 2
EXPECTED_FARKAS_COUNT = 19
Descriptor = tuple[tuple[int, int], ...]
Spec = tuple[tuple[int, ...], Descriptor]


def partitions(total: int, minimum: int = 1):
    """Yield nondecreasing positive integer partitions of ``total``."""
    if total == 0:
        yield ()
        return
    for part in range(minimum, total + 1):
        for tail in partitions(total - part, part):
            yield (part,) + tail


def validate_partition(partition: tuple[int, ...]) -> None:
    if (
        not partition
        or sum(partition) != ORDER
        or any(part <= 0 for part in partition)
        or tuple(sorted(partition)) != partition
    ):
        raise ValueError("invalid nondecreasing partition of 23")


def canonical_descriptor(
    partition: tuple[int, ...], assignment: tuple[int, int, int, int]
) -> Descriptor:
    """Quotient leaf order and permutations of equal-sized parent blocks."""
    center, *leaves = assignment
    variants: list[Descriptor] = []
    for ordered_leaves in set(permutations(leaves)):
        component_labels: dict[tuple[int, int], int] = {}
        next_label: Counter[int] = Counter()
        descriptor: list[tuple[int, int]] = []
        for block in (center,) + ordered_leaves:
            size = partition[block]
            key = (size, block)
            if key not in component_labels:
                component_labels[key] = next_label[size]
                next_label[size] += 1
            descriptor.append((size, component_labels[key]))
        variants.append(tuple(descriptor))
    return min(variants)


def indexed_specs(partition: tuple[int, ...]):
    """Enumerate fixed parent-block choices and map them to star orbits."""
    block_count = len(partition)
    for center in range(block_count):
        for leaves in combinations_with_replacement(range(block_count), 3):
            assignment = (center,) + leaves
            needs = Counter(assignment)
            if any(partition[block] < count for block, count in needs.items()):
                continue
            yield partition, canonical_descriptor(partition, assignment)


def canonical_specs(partition: tuple[int, ...]) -> list[Spec]:
    return sorted(set(indexed_specs(partition)))


def selected_tokens(
    partition: tuple[int, ...], spec: Spec
) -> tuple[tuple[int, int], tuple[int, int], tuple[int, int], tuple[int, int]]:
    """Construct four distinct representative vertices from a descriptor."""
    _, descriptor = spec
    if len(descriptor) != 4:
        raise ValueError("a three-star descriptor must have four vertices")
    available: dict[int, list[int]] = defaultdict(list)
    for index, size in enumerate(partition):
        available[size].append(index)
    vertex_counts: Counter[int] = Counter()
    result: list[tuple[int, int]] = []
    for size, component_label in descriptor:
        if not 0 <= component_label < len(available[size]):
            raise ArithmeticError("descriptor requests a missing block")
        block = available[size][component_label]
        result.append((block, vertex_counts[block]))
        vertex_counts[block] += 1
    if len(set(result)) != 4 or any(
        vertex_counts[block] > partition[block] for block in vertex_counts
    ):
        raise ArithmeticError("descriptor does not select four distinct vertices")
    reconstructed = tuple(block for block, _ in result)
    if canonical_descriptor(partition, reconstructed) != spec[1]:
        raise ArithmeticError("descriptor canonicalization is not idempotent")
    return result[0], result[1], result[2], result[3]


def base_determinant_and_delta(
    partition: tuple[int, ...]
) -> tuple[int, Fraction]:
    product_term = 20 ** (ORDER - len(partition))
    delta = Fraction(1)
    for size in partition:
        product_term *= 20 + 4 * size
        delta -= Fraction(size, 20 + 4 * size)
    determinant = product_term * delta
    if determinant.denominator != 1 or determinant <= 0 or delta <= 0:
        raise ArithmeticError("invalid Ehlich-block determinant data")
    return determinant.numerator, delta


def base_inverse_entry(
    partition: tuple[int, ...],
    delta: Fraction,
    left: tuple[int, int],
    right: tuple[int, int],
) -> Fraction:
    left_block, left_vertex = left
    right_block, right_vertex = right
    left_size = partition[left_block]
    right_size = partition[right_block]
    value = Fraction(0)
    if left_block == right_block:
        if left_vertex == right_vertex:
            value += Fraction(1, 20)
        value -= Fraction(1, 20 * (5 + left_size))
    value += (
        Fraction(1, 16 * (5 + left_size) * (5 + right_size)) / delta
    )
    return value


def perturbed_determinant(spec: Spec) -> int:
    """Evaluate a three-star determinant by a rank-two determinant lemma."""
    partition = spec[0]
    base_determinant, delta = base_determinant_and_delta(partition)
    center, *leaves = selected_tokens(partition, spec)
    coefficients = [
        -4 if center[0] == leaf[0] else 4 for leaf in leaves
    ]

    def inverse_entry(left: tuple[int, int], right: tuple[int, int]) -> Fraction:
        return base_inverse_entry(partition, delta, left, right)

    center_v = sum(
        coefficient * inverse_entry(center, leaf)
        for coefficient, leaf in zip(coefficients, leaves)
    )
    v_v = sum(
        left_coefficient
        * right_coefficient
        * inverse_entry(left, right)
        for left_coefficient, left in zip(coefficients, leaves)
        for right_coefficient, right in zip(coefficients, leaves)
    )
    correction = (
        (1 + center_v) ** 2 - inverse_entry(center, center) * v_v
    )
    determinant = base_determinant * correction
    if determinant.denominator != 1:
        raise ArithmeticError("rank-two determinant was not integral")
    return determinant.numerator


def partition_blocks(partition: tuple[int, ...]) -> list[list[int]]:
    blocks: list[list[int]] = []
    cursor = 0
    for size in partition:
        blocks.append(list(range(cursor, cursor + size)))
        cursor += size
    return blocks


def candidate_matrix_and_cells(
    spec: Spec,
) -> tuple[list[list[int]], list[list[int]]]:
    partition = spec[0]
    blocks = partition_blocks(partition)
    labels = [label for label, size in enumerate(partition) for _ in range(size)]
    matrix = [
        [
            23
            if row == column
            else (3 if labels[row] == labels[column] else -1)
            for column in range(ORDER)
        ]
        for row in range(ORDER)
    ]
    starts = [block[0] for block in blocks]
    tokens = selected_tokens(partition, spec)
    special = [starts[block] + vertex for block, vertex in tokens]
    for leaf in special[1:]:
        matrix[special[0]][leaf] = matrix[leaf][special[0]] = (
            -1 if matrix[special[0]][leaf] == 3 else 3
        )
    cells = [[vertex] for vertex in special]
    special_set = set(special)
    for block in blocks:
        remainder = [vertex for vertex in block if vertex not in special_set]
        if remainder:
            cells.append(remainder)
    return matrix, cells


def bareiss_determinant(matrix: list[list[int]]) -> int:
    entries = [row[:] for row in matrix]
    size = len(entries)
    if size == 0 or any(len(row) != size for row in entries):
        raise ValueError("matrix must be nonempty and square")
    sign = 1
    previous = 1
    for column in range(size - 1):
        pivot_row = next(
            (row for row in range(column, size) if entries[row][column]), None
        )
        if pivot_row is None:
            return 0
        if pivot_row != column:
            entries[column], entries[pivot_row] = (
                entries[pivot_row],
                entries[column],
            )
            sign = -sign
        pivot = entries[column][column]
        for row in range(column + 1, size):
            for other in range(column + 1, size):
                numerator = (
                    entries[row][other] * pivot
                    - entries[row][column] * entries[column][other]
                )
                quotient, remainder = divmod(numerator, previous)
                if remainder:
                    raise ArithmeticError("Bareiss division was not exact")
                entries[row][other] = quotient
            entries[row][column] = 0
        previous = pivot
    return sign * entries[-1][-1]


def rational_diagonalization(matrix: list[list[int]]) -> list[Fraction]:
    entries = [[Fraction(value) for value in row] for row in matrix]
    diagonal: list[Fraction] = []
    for pivot_index in range(len(entries)):
        pivot = entries[pivot_index][pivot_index]
        if pivot <= 0:
            raise ArithmeticError("record-level candidate is not positive definite")
        diagonal.append(pivot)
        for row in range(pivot_index + 1, len(entries)):
            for column in range(row, len(entries)):
                value = (
                    entries[row][column]
                    - entries[row][pivot_index]
                    * entries[column][pivot_index]
                    / pivot
                )
                entries[row][column] = entries[column][row] = value
        for row in range(pivot_index + 1, len(entries)):
            entries[row][pivot_index] = entries[pivot_index][row] = 0
    return diagonal


def leading_minor_diagonalization(matrix: list[list[int]]) -> list[Fraction]:
    entries = [row[:] for row in matrix]
    minors = [1]
    previous = 1
    for column in range(len(entries) - 1):
        pivot = entries[column][column]
        if pivot <= 0:
            raise ArithmeticError("nonpositive leading principal minor")
        minors.append(pivot)
        for row in range(column + 1, len(entries)):
            for other in range(column + 1, len(entries)):
                numerator = (
                    entries[row][other] * pivot
                    - entries[row][column] * entries[column][other]
                )
                quotient, remainder = divmod(numerator, previous)
                if remainder:
                    raise ArithmeticError("leading-minor elimination failed")
                entries[row][other] = quotient
            entries[row][column] = 0
        previous = pivot
    final_minor = entries[-1][-1]
    if final_minor <= 0:
        raise ArithmeticError("nonpositive full determinant")
    minors.append(final_minor)
    return [
        Fraction(minors[index], minors[index - 1])
        for index in range(1, len(minors))
    ]


def is_prime(value: int) -> bool:
    if value < 2:
        return False
    divisor = 2
    while divisor * divisor <= value:
        if value % divisor == 0:
            return value == divisor
        divisor = 3 if divisor == 2 else divisor + 2
    return True


def prime_factors(value: int) -> list[int]:
    factors: list[int] = []
    divisor = 2
    while divisor * divisor <= value:
        if value % divisor == 0:
            factors.append(divisor)
            while value % divisor == 0:
                value //= divisor
        divisor = 3 if divisor == 2 else divisor + 2
    if value > 1:
        factors.append(value)
    if not factors or any(not is_prime(prime) for prime in factors):
        raise ArithmeticError("prime factorization failed")
    return factors


def valuation(value: Fraction, prime: int) -> tuple[int, Fraction]:
    numerator, denominator = value.numerator, value.denominator
    exponent = 0
    while numerator % prime == 0:
        numerator //= prime
        exponent += 1
    while denominator % prime == 0:
        denominator //= prime
        exponent -= 1
    return exponent, Fraction(numerator, denominator)


def unit_residue(unit: Fraction, modulus: int) -> int:
    return (
        unit.numerator % modulus
        * pow(unit.denominator % modulus, -1, modulus)
        % modulus
    )


def legendre_symbol(unit: Fraction, prime: int) -> int:
    residue = pow(unit_residue(unit, prime), (prime - 1) // 2, prime)
    if residue not in (1, prime - 1):
        raise ArithmeticError("Legendre symbol received a nonunit")
    return -1 if residue == prime - 1 else 1


def hilbert_symbol(left: Fraction, right: Fraction, prime: int) -> int:
    alpha, left_unit = valuation(left, prime)
    beta, right_unit = valuation(right, prime)
    if prime != 2:
        value = -1 if alpha * beta * ((prime - 1) // 2) % 2 else 1
        if beta % 2:
            value *= legendre_symbol(left_unit, prime)
        if alpha % 2:
            value *= legendre_symbol(right_unit, prime)
        return value
    left_mod_8 = unit_residue(left_unit, 8)
    right_mod_8 = unit_residue(right_unit, 8)
    exponent = ((left_mod_8 - 1) // 2) * ((right_mod_8 - 1) // 2)
    exponent += alpha * ((right_mod_8**2 - 1) // 8)
    exponent += beta * ((left_mod_8**2 - 1) // 8)
    return -1 if exponent % 2 else 1


def hasse_invariant(diagonal: list[Fraction], prime: int) -> int:
    value = 1
    for index, left in enumerate(diagonal):
        for right in diagonal[index + 1 :]:
            value *= hilbert_symbol(left, right, prime)
    return value


def inverse(matrix: list[list[int]]) -> list[list[Fraction]]:
    size = len(matrix)
    augmented = [
        [Fraction(value) for value in row]
        + [Fraction(int(row_index == column)) for column in range(size)]
        for row_index, row in enumerate(matrix)
    ]
    for column in range(size):
        pivot_row = next(
            (row for row in range(column, size) if augmented[row][column]), None
        )
        if pivot_row is None:
            raise ArithmeticError("candidate matrix is singular")
        augmented[column], augmented[pivot_row] = (
            augmented[pivot_row],
            augmented[column],
        )
        pivot = augmented[column][column]
        augmented[column] = [value / pivot for value in augmented[column]]
        for row in range(size):
            if row == column:
                continue
            scale = augmented[row][column]
            if scale:
                augmented[row] = [
                    value - scale * pivot_value
                    for value, pivot_value in zip(
                        augmented[row], augmented[column]
                    )
                ]
    result = [row[size:] for row in augmented]
    for row in range(size):
        for column in range(size):
            value = sum(
                Fraction(matrix[row][index]) * result[index][column]
                for index in range(size)
            )
            if value != int(row == column):
                raise ArithmeticError("exact inverse product check failed")
    return result


def check_cell_constancy(
    matrix: list[list[int]] | list[list[Fraction]], cells: list[list[int]]
) -> None:
    if sorted(vertex for cell in cells for vertex in cell) != list(range(ORDER)):
        raise ArithmeticError("cells do not partition all coordinates")
    for cell in cells:
        if len({matrix[index][index] for index in cell}) != 1:
            raise ArithmeticError("diagonal is not constant on a cell")
        within = {
            matrix[left][right]
            for left in cell
            for right in cell
            if left != right
        }
        if len(within) > 1:
            raise ArithmeticError("off-diagonal value is not constant in a cell")
    for left_index, left_cell in enumerate(cells):
        for right_cell in cells[left_index + 1 :]:
            values = {
                matrix[left][right]
                for left in left_cell
                for right in right_cell
            }
            if len(values) != 1:
                raise ArithmeticError("value is not constant between cells")


def inverse_quadratic_data(
    inverse_matrix: list[list[Fraction]], cells: list[list[int]]
) -> tuple[Fraction, dict[tuple[int, int], Fraction]]:
    check_cell_constancy(inverse_matrix, cells)
    constant = Fraction(0)
    coefficients: dict[tuple[int, int], Fraction] = {}
    for left_index, left_cell in enumerate(cells):
        diagonal = inverse_matrix[left_cell[0]][left_cell[0]]
        off_diagonal = (
            inverse_matrix[left_cell[0]][left_cell[1]]
            if len(left_cell) > 1
            else Fraction(0)
        )
        constant += len(left_cell) * (diagonal - off_diagonal)
        coefficients[left_index, left_index] = off_diagonal
        for right_index in range(left_index + 1, len(cells)):
            coefficients[left_index, right_index] = (
                2 * inverse_matrix[left_cell[0]][cells[right_index][0]]
            )
    return constant, coefficients


def admissible_cell_sums(
    inverse_matrix: list[list[Fraction]], cells: list[list[int]]
) -> list[tuple[int, ...]]:
    constant, coefficients = inverse_quadratic_data(inverse_matrix, cells)
    denominator = lcm(
        constant.denominator,
        *(coefficient.denominator for coefficient in coefficients.values()),
    )
    integer_constant = constant.numerator * (denominator // constant.denominator)
    integer_coefficients = {
        indices: coefficient.numerator
        * (denominator // coefficient.denominator)
        for indices, coefficient in coefficients.items()
        if coefficient
    }
    return [
        totals
        for totals in product(
            *(range(-len(cell), len(cell) + 1, 2) for cell in cells)
        )
        if integer_constant
        + sum(
            coefficient * totals[left] * totals[right]
            for (left, right), coefficient in integer_coefficients.items()
        )
        == denominator
    ]


def parse_feature(feature: str, cell_count: int) -> tuple[int, int] | None:
    if feature == "count":
        return None
    pieces = feature.split(",")
    if len(pieces) != 2:
        raise ValueError("invalid moment feature")
    left, right = (int(piece) for piece in pieces)
    if not 0 <= left <= right < cell_count:
        raise ValueError("moment feature index is out of range")
    return left, right


def pattern_feature(totals: tuple[int, ...], feature: str) -> int:
    indices = parse_feature(feature, len(totals))
    if indices is None:
        return 1
    left, right = indices
    return totals[left] * totals[right]


def target_feature(
    matrix: list[list[int]], cells: list[list[int]], feature: str
) -> int:
    indices = parse_feature(feature, len(cells))
    if indices is None:
        return ORDER
    left, right = indices
    return sum(
        matrix[row][column]
        for row in cells[left]
        for column in cells[right]
    )


def entry_spec(entry: dict[str, object]) -> Spec:
    partition = tuple(entry["partition"])
    validate_partition(partition)
    descriptor = tuple(tuple(token) for token in entry["descriptor"])
    if (
        len(descriptor) != 4
        or any(
            len(token) != 2
            or not isinstance(token[0], int)
            or not isinstance(token[1], int)
            for token in descriptor
        )
    ):
        raise ValueError("invalid three-star descriptor")
    spec = partition, descriptor
    selected_tokens(partition, spec)
    return spec


def verify_cell_entry(
    entry: dict[str, object], square_candidates: dict[Spec, int]
) -> tuple[Spec, str]:
    if set(entry) != {
        "partition",
        "descriptor",
        "coefficient",
        "kind",
        "multipliers",
    }:
        raise ValueError("cell certificate has unsupported fields")
    spec = entry_spec(entry)
    if square_candidates.get(spec) != entry["coefficient"]:
        raise ArithmeticError("cell certificate names the wrong candidate")
    matrix, cells = candidate_matrix_and_cells(spec)
    check_cell_constancy(matrix, cells)
    patterns = admissible_cell_sums(inverse(matrix), cells)
    kind = entry["kind"]
    multipliers = entry["multipliers"]
    if kind == "empty":
        if patterns or multipliers != {}:
            raise ArithmeticError("empty-pattern certificate is invalid")
        return spec, kind
    if kind != "farkas":
        raise ValueError("unsupported cell certificate kind")
    if (
        not isinstance(multipliers, dict)
        or not multipliers
        or any(not isinstance(value, int) for value in multipliers.values())
    ):
        raise ValueError("Farkas multipliers must be nonempty integers")
    for feature in multipliers:
        parse_feature(feature, len(cells))
    for pattern in patterns:
        value = sum(
            multiplier * pattern_feature(pattern, feature)
            for feature, multiplier in multipliers.items()
        )
        if value < 0:
            raise ArithmeticError("Farkas functional is negative on a pattern")
    target_value = sum(
        multiplier * target_feature(matrix, cells, feature)
        for feature, multiplier in multipliers.items()
    )
    if target_value >= 0:
        raise ArithmeticError("Farkas functional does not separate the target")
    return spec, kind


def main() -> None:
    certificate = json.loads(
        Path(__file__).with_name("certificates.json").read_text(encoding="utf-8")
    )
    if set(certificate) != {
        "schemaVersion",
        "recordCoefficient",
        "cellExclusions",
    } or certificate["schemaVersion"] != 1:
        raise ValueError("unsupported certificate schema")
    if certificate["recordCoefficient"] != RECORD_COEFFICIENT:
        raise ValueError("record coefficient mismatch")

    all_partitions = list(partitions(ORDER))
    if (
        len(all_partitions) != EXPECTED_PARTITION_COUNT
        or len(set(all_partitions)) != EXPECTED_PARTITION_COUNT
    ):
        raise ArithmeticError("partition enumeration mismatch")

    all_specs: list[Spec] = []
    indexed_count = 0
    for partition in all_partitions:
        validate_partition(partition)
        expanded = list(indexed_specs(partition))
        indexed_count += len(expanded)
        specs = canonical_specs(partition)
        if set(expanded) != set(specs):
            raise ArithmeticError("canonical three-star classification is incomplete")
        for spec in specs:
            selected_tokens(partition, spec)
        all_specs.extend(specs)
    if indexed_count != EXPECTED_INDEXED_SPEC_COUNT:
        raise ArithmeticError("indexed three-star enumeration mismatch")
    if (
        len(all_specs) != EXPECTED_CANONICAL_SPEC_COUNT
        or len(set(all_specs)) != EXPECTED_CANONICAL_SPEC_COUNT
    ):
        raise ArithmeticError("canonical three-star enumeration mismatch")

    threshold = (SIGN_DIVISOR * RECORD_COEFFICIENT) ** 2
    above_record: list[tuple[Spec, int, int | None]] = []
    at_record: list[Spec] = []
    for spec in all_specs:
        determinant = perturbed_determinant(spec)
        quotient, remainder = divmod(determinant, GRAM_DIVISOR)
        if remainder:
            raise ArithmeticError("candidate lacks the universal 2^44 factor")
        if determinant == threshold:
            at_record.append(spec)
        elif determinant > threshold:
            root = isqrt(quotient)
            above_record.append(
                (spec, quotient, root if root**2 == quotient else None)
            )
    if at_record or len(above_record) != EXPECTED_ABOVE_COUNT:
        raise ArithmeticError("record-threshold three-star count mismatch")

    square_candidates = {
        spec: root for spec, _, root in above_record if root is not None
    }
    if len(square_candidates) != EXPECTED_SQUARE_COUNT:
        raise ArithmeticError("square-determinant three-star count mismatch")

    hasse_excluded: set[Spec] = set()
    for spec, root in square_candidates.items():
        matrix, _ = candidate_matrix_and_cells(spec)
        if bareiss_determinant(matrix) != perturbed_determinant(spec):
            raise ArithmeticError("rank-two and direct determinants disagree")
        diagonal = rational_diagonalization(matrix)
        independent = leading_minor_diagonalization(matrix)
        if diagonal != independent:
            raise ArithmeticError("independent diagonalizations disagree")
        diagonal_product = Fraction(1)
        for value in diagonal:
            diagonal_product *= value
        if diagonal_product != perturbed_determinant(spec):
            raise ArithmeticError("rational congruence changed determinant")
        if any(
            hasse_invariant(diagonal, prime) == -1
            for prime in prime_factors(root)
        ):
            hasse_excluded.add(spec)
    if len(hasse_excluded) != EXPECTED_HASSE_COUNT:
        raise ArithmeticError("local Hasse exclusion count mismatch")

    entries = certificate["cellExclusions"]
    if not isinstance(entries, list) or len(entries) != 21:
        raise ArithmeticError("cell certificate count mismatch")
    verified = [verify_cell_entry(entry, square_candidates) for entry in entries]
    cell_specs = {spec for spec, _ in verified}
    empty_count = sum(kind == "empty" for _, kind in verified)
    farkas_count = sum(kind == "farkas" for _, kind in verified)
    if (
        len(cell_specs) != len(entries)
        or hasse_excluded & cell_specs
        or hasse_excluded | cell_specs != set(square_candidates)
        or empty_count != EXPECTED_EMPTY_PATTERN_COUNT
        or farkas_count != EXPECTED_FARKAS_COUNT
    ):
        raise ArithmeticError("square certificates do not exactly exhaust")

    nonsquare_count = len(above_record) - len(square_candidates)
    print("canonical three-star specifications:", len(all_specs))
    print("determinants strictly above the record square:", len(above_record))
    print("determinants equal to the record square:", len(at_record))
    print("excluded by normalized nonsquare determinant:", nonsquare_count)
    print("excluded by local Hasse invariant:", len(hasse_excluded))
    print("excluded by empty inverse-quadratic pattern set:", empty_count)
    print("excluded by cell-moment certificate:", farkas_count)
    print("unexcluded record-level three-star candidates: 0")
    print("verification: PASS")


if __name__ == "__main__":
    main()
