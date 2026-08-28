#!/usr/bin/env python3
"""Exact symbolic audit of the accepted entropy-counterfeit witness.

Every entropy is represented as ``a + b*h``, with rational ``a,b`` and
``h = h_2(1/4)``.  Tuple variables are projections of mutually independent
components, so entropy and conditional mutual information reduce to weighted
set union and intersection.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from itertools import product


@dataclass(frozen=True)
class AffineH:
    constant: Fraction = Fraction(0)
    h_coefficient: Fraction = Fraction(0)

    def __add__(self, other: "AffineH") -> "AffineH":
        return AffineH(
            self.constant + other.constant,
            self.h_coefficient + other.h_coefficient,
        )

    def __sub__(self, other: "AffineH") -> "AffineH":
        return AffineH(
            self.constant - other.constant,
            self.h_coefficient - other.h_coefficient,
        )

    def __mul__(self, scalar: int | Fraction) -> "AffineH":
        scalar = Fraction(scalar)
        return AffineH(self.constant * scalar, self.h_coefficient * scalar)

    __rmul__ = __mul__


ZERO = AffineH()
ONE = AffineH(Fraction(1))
HALF = AffineH(Fraction(1, 2))
H = AffineH(h_coefficient=Fraction(1))

C_VALUE = 2 * H - 3 * HALF
A_VALUE = ONE - H
R = H - AffineH(Fraction(3, 4))
B1C_VALUE = R
B2C_VALUE = AffineH(Fraction(7, 4)) - 2 * H
EU_VALUE = AffineH(Fraction(5, 4)) - H
EV_VALUE = R

COMPONENT_WEIGHTS = {
    "C": C_VALUE,
    "A": A_VALUE,
    "B1c": B1C_VALUE,
    "B2c": B2C_VALUE,
    "Eu": EU_VALUE,
    "Ev": EV_VALUE,
    "Ny": HALF,
    "Nz": HALF,
}

VARIABLES = {
    "U": frozenset({"C", "A", "B2c", "Eu"}),
    "V": frozenset({"B1c", "Ev"}),
    "W": frozenset(),
    "T": frozenset(),
    "X": frozenset({"C", "A", "B1c", "B2c", "Eu", "Ev"}),
    "Y": frozenset({"C", "A", "Ny"}),
    "Z": frozenset({"C", "B1c", "B2c", "Nz"}),
}


def total_weight(components: frozenset[str] | set[str]) -> AffineH:
    value = ZERO
    for component in components:
        value += COMPONENT_WEIGHTS[component]
    return value


def union_of(names: tuple[str, ...] | list[str]) -> frozenset[str]:
    result: set[str] = set()
    for name in names:
        result.update(VARIABLES[name])
    return frozenset(result)


def entropy(*names: str) -> AffineH:
    return total_weight(union_of(list(names)))


def conditional_mi(
    left: frozenset[str], right: frozenset[str], conditioned: frozenset[str]
) -> AffineH:
    return total_weight((left & right) - conditioned)


def cmi(left: tuple[str, ...], right: tuple[str, ...], given: tuple[str, ...]) -> AffineH:
    return conditional_mi(union_of(left), union_of(right), union_of(given))


def require_equal(label: str, actual: AffineH, expected: AffineH) -> None:
    if actual != expected:
        raise AssertionError(f"{label}: {actual!r} != {expected!r}")


def require_strictly_positive_on_h_bracket(label: str, value: AffineH) -> None:
    # The accepted exact bounds are 3/4 < h_2(1/4) < 7/8.
    endpoint = Fraction(3, 4) if value.h_coefficient >= 0 else Fraction(7, 8)
    lower_limit = value.constant + value.h_coefficient * endpoint
    if lower_limit < 0:
        raise AssertionError(f"{label}: negative on the certified h bracket")
    if lower_limit == 0 and value.h_coefficient == 0:
        raise AssertionError(f"{label}: identically zero")


def main() -> None:
    for name, value in COMPONENT_WEIGHTS.items():
        require_strictly_positive_on_h_bracket(name, value)

    # Structural equalities: U and V are independent component projections,
    # their union is exactly X, and W,T are constants.
    if VARIABLES["U"] & VARIABLES["V"]:
        raise AssertionError("U and V share an independent component")
    if VARIABLES["U"] | VARIABLES["V"] != VARIABLES["X"]:
        raise AssertionError("U and V do not determine exactly X")
    require_equal("I(U;V)", cmi(("U",), ("V",), ()), ZERO)
    require_equal("H(X|U,V,T)", total_weight(VARIABLES["X"] - union_of(["U", "V", "T"])), ZERO)
    require_equal("I(X;W|U,V,T)", cmi(("X",), ("W",), ("U", "V", "T")), ZERO)
    require_equal(
        "I(U,V,W,T;Y,Z|X)",
        cmi(("U", "V", "W", "T"), ("Y", "Z"), ("X",)),
        ZERO,
    )

    # Complete seven-coordinate base entropy vector.
    require_equal("H(X)", entropy("X"), ONE)
    require_equal("H(Y)", entropy("Y"), H)
    require_equal("H(Z)", entropy("Z"), H)
    require_equal("H(X,Y)", entropy("X", "Y"), AffineH(Fraction(3, 2)))
    require_equal("H(X,Z)", entropy("X", "Z"), AffineH(Fraction(3, 2)))
    require_equal("H(Y,Z)", entropy("Y", "Z"), AffineH(Fraction(3, 2)))
    require_equal("H(X,Y,Z)", entropy("X", "Y", "Z"), AffineH(Fraction(2)))

    # Exact dependence balance at the witness.
    require_equal("I(U;V|W,T,Y)", cmi(("U",), ("V",), ("W", "T", "Y")), ZERO)
    require_equal("I(U;V|W,T,Z)", cmi(("U",), ("V",), ("W", "T", "Z")), ZERO)

    # Audit all disjoint L,K subtuples of {U,V,W,T}, L nonempty.
    labels = ("U", "V", "W", "T")
    bec_identity_count = 0
    for assignment in product(range(3), repeat=len(labels)):
        left_names = tuple(label for label, slot in zip(labels, assignment) if slot == 1)
        given_names = tuple(label for label, slot in zip(labels, assignment) if slot == 2)
        if not left_names:
            continue
        lhs = cmi(left_names, ("Y", "Z"), given_names)
        rhs = cmi(left_names, ("X",), given_names)
        require_equal(f"BEC identity L={left_names}, K={given_names}", 2 * lhs, rhs)
        bec_identity_count += 1
    if bec_identity_count != 65:
        raise AssertionError(f"unexpected BEC identity count: {bec_identity_count}")

    # Sharp support rows and both objective branches.
    first_support = cmi(("X",), ("Z",), ("U", "W", "T")) - cmi(
        ("X",), ("Y",), ("U", "W", "T")
    )
    second_support = cmi(("X",), ("Y",), ("V", "W", "T")) - cmi(
        ("X",), ("Z",), ("V", "W", "T")
    )
    require_equal("first support row", first_support, R)
    require_equal("second support row", second_support, R)

    c_value = H - HALF
    branch_1 = cmi(("U", "W"), ("Y",), ("T",)) + cmi(
        ("X",), ("Z",), ("U", "W", "T")
    )
    branch_2 = cmi(("V", "W"), ("Z",), ("T",)) + cmi(
        ("X",), ("Y",), ("V", "W", "T")
    )
    expected_branch = 2 * H - AffineH(Fraction(5, 4))
    require_equal("B1", branch_1, c_value + R)
    require_equal("B2", branch_2, c_value + R)
    require_equal("exact UV value", branch_1, expected_branch)

    print("PASS: exact affine-in-h component audit")
    print(f"PASS: {bec_identity_count} disjoint-subtuple BEC identities")
    print("PASS: dependence balance, support rows, and both objective branches")


if __name__ == "__main__":
    main()
