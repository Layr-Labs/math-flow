#!/usr/bin/env python3
"""Directed certificates for BSSC marginal/output-correlation pruning.

This standard-library checker performs no writes and no network access.  It
corroborates only the numerical/rational parts of the README proof.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from decimal import Context, Decimal, ROUND_CEILING, ROUND_FLOOR, ROUND_HALF_EVEN
from fractions import Fraction
from pathlib import Path


ROOT = Path(__file__).resolve().parent
D = Decimal
PRECISION = 120
NEAR = Context(prec=PRECISION, rounding=ROUND_HALF_EVEN)
DOWN = Context(prec=PRECISION, rounding=ROUND_FLOOR)
UP = Context(prec=PRECISION, rounding=ROUND_CEILING)

FOUNDATION_TX = "88a1004f309460f3ec1cacdae88d30f88559f9bc"
UNIVERSAL_BOUND_TX = "33a5944dca980bf94cc869c6c7dee2d04385ff58"

# This exact decimal rational bracket is independently squared below.  It is
# the bracket used to reconstruct q_-=(15-sqrt(105))/30 in the foundation.
SQRT105_LO = (
    "10.246950765959598383221038680521051990735032663454832929541978499890"
    "34798570535407292723162837854673695"
)
SQRT105_HI = (
    "10.246950765959598383221038680521051990735032663454832929541978499890"
    "34798570535407292723162837854673696"
)


def need(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


@dataclass(frozen=True)
class IV:
    lo: Decimal
    hi: Decimal

    def __post_init__(self) -> None:
        need(self.lo <= self.hi, "reversed interval")

    @staticmethod
    def point(value: str | int | Decimal) -> "IV":
        exact = value if isinstance(value, Decimal) else D(value)
        return IV(exact, exact)

    def __add__(self, other: "IV") -> "IV":
        return IV(DOWN.add(self.lo, other.lo), UP.add(self.hi, other.hi))

    def __neg__(self) -> "IV":
        return IV(self.hi.copy_negate(), self.lo.copy_negate())

    def __sub__(self, other: "IV") -> "IV":
        return self + (-other)

    def __mul__(self, other: "IV") -> "IV":
        products = (
            (self.lo, other.lo),
            (self.lo, other.hi),
            (self.hi, other.lo),
            (self.hi, other.hi),
        )
        return IV(
            min(DOWN.multiply(left, right) for left, right in products),
            max(UP.multiply(left, right) for left, right in products),
        )

    def __truediv__(self, other: "IV") -> "IV":
        need(not (other.lo <= 0 <= other.hi), "interval division by zero")
        reciprocal = IV(
            DOWN.divide(D(1), other.hi),
            UP.divide(D(1), other.lo),
        )
        return self * reciprocal

    def ln(self) -> "IV":
        need(self.lo > 0, "logarithm domain")
        # Decimal.ln is correctly rounded with ROUND_HALF_EVEN.  Expand each
        # endpoint by one representable number; monotonicity handles intervals.
        lower = NEAR.ln(self.lo).next_minus(context=NEAR)
        upper = NEAR.ln(self.hi).next_plus(context=NEAR)
        return IV(lower, upper)


Q = IV.point
ZERO = Q(0)
ONE = Q(1)
TWO = Q(2)
FOUR = Q(4)
LN2 = TWO.ln()


def rational(numerator: int, denominator: int) -> IV:
    return Q(numerator) / Q(denominator)


def binary_entropy(value: IV) -> IV:
    need(D(0) < value.lo <= value.hi < D(1), "entropy input domain")
    complement = ONE - value
    return -(value * value.ln() + complement * complement.ln()) / LN2


def f_curve(q: IV) -> IV:
    return (
        binary_entropy(q / TWO)
        + binary_entropy((ONE - q) / TWO)
        - ONE
    ) / TWO


def log2(value: IV) -> IV:
    return value.ln() / LN2


def i_y(q: IV) -> IV:
    return binary_entropy((ONE - q) / TWO) - (ONE - q)


def entropy(probabilities: tuple[IV, ...]) -> IV:
    total = ZERO
    for probability in probabilities:
        need(probability.lo > 0, "positive entropy atom")
        total = total - probability * probability.ln() / LN2
    return total


def exact_rtd_threshold() -> tuple[IV, IV]:
    sqrt_lo = Fraction(SQRT105_LO)
    sqrt_hi = Fraction(SQRT105_HI)
    need(sqrt_lo * sqrt_lo < 105 < sqrt_hi * sqrt_hi,
         "exact sqrt(105) bracket")

    sqrt_iv = IV(D(SQRT105_LO), D(SQRT105_HI))
    q_minus = (Q(15) - sqrt_iv) / Q(30)
    need(D(0) < q_minus.lo < q_minus.hi < D("0.5"), "q_- bracket")

    q_lo = Fraction(str(q_minus.lo))
    q_hi = Fraction(str(q_minus.hi))
    polynomial = lambda q: 15 * q * q - 15 * q + 2
    need(polynomial(q_lo) > 0 > polynomial(q_hi), "stationary-root straddle")

    half = rational(1, 2)
    quarter = rational(1, 4)
    l_rtd = (
        binary_entropy(quarter)
        - half
        + half
        * (
            binary_entropy(q_minus / TWO)
            - binary_entropy((ONE - q_minus) / TWO)
            + ONE
            - TWO * q_minus
        )
    )
    threshold = TWO * l_rtd

    declared_lo = D(
        "0.7232857688439092313268831563011740144159620214477211104074274596056014"
    )
    declared_hi = D(
        "0.7232857688439092313268831563011740144159620214477211104074274596056016"
    )
    need(declared_lo < threshold.lo <= threshold.hi < declared_hi,
         "foundation threshold enclosure")
    return q_minus, threshold


def check_claim_metadata() -> None:
    with (ROOT / "claims.json").open("r", encoding="utf-8") as handle:
        claims = json.load(handle)
    need(claims["schemaVersion"] == 1, "claim schema")
    need(len(claims["claims"]) == 1, "one claim")
    claim = claims["claims"][0]
    need(
        claim["claimKey"]
        == "bssc-sum-capacity/two-letter-marton-marginal-correlation-pruning",
        "claim key",
    )
    need(
        claim["dependencyTransactionIds"]
        == [FOUNDATION_TX, UNIVERSAL_BOUND_TX],
        "exact dependencies in canonical ledger order",
    )
    statement = claim["statement"]
    for required in (
        "two pre-averaging Marton-to-input rows",
        "M <= G(P_{X_1X_2})+2r",
        "T=2L_RTD",
        "q_1,q_2 in (3/8,5/8)",
        "hence in (7/20,13/20)",
        "17/20<Q<23/20",
        "C_out<7/160=0.04375<0.044 bits",
        "|c_in|<7/40",
        "1/8<alpha<5/13",
        "necessary conditions only",
    ):
        need(required in statement, f"claim scope: {required}")


def check_pruning_certificates() -> None:
    q_minus, threshold = exact_rtd_threshold()
    quarter = rational(1, 4)
    half = rational(1, 2)
    h = binary_entropy(quarter)
    r = h - rational(3, 4)

    def row_envelope(q: IV) -> IV:
        return i_y(q) + TWO * r * (ONE - q)

    q_max = rational(19, 35)
    ratio = (ONE + q_max) / (ONE - q_max)
    need(ratio.lo <= D(27) / D(8) <= ratio.hi, "exact row maximizer ratio")
    row_derivative = ONE - log2(ratio) / TWO - TWO * r
    need(row_derivative.lo <= 0 <= row_derivative.hi,
         "row derivative contains exact zero")

    coordinate_upper = row_envelope(rational(3, 8)) + row_envelope(q_max)
    need(coordinate_upper.hi < D("0.722032"), "displayed coordinate upper")
    need(coordinate_upper.hi < threshold.lo, "coordinate cutoff below RTD")

    coordinate_root_lo = rational(379109, 1000000)
    coordinate_root_hi = rational(379110, 1000000)
    need((row_envelope(coordinate_root_lo) + row_envelope(q_max)).hi
         < threshold.lo, "coordinate root lower endpoint")
    need((row_envelope(coordinate_root_hi) + row_envelope(q_max)).lo
         > threshold.hi, "coordinate root upper endpoint")

    # Farey neighbors at order 20: a/b<c/d, bc-ad=1, b+d>20.
    need(5 * 8 - 3 * 13 == 1, "coordinate Farey determinant")
    need(8 + 13 > 20, "coordinate Farey order")
    need(Fraction(379110, 1000000) < Fraction(5, 13),
         "coordinate root below next Farey fraction")

    correlation_cap = FOUR * f_curve(half) + FOUR * r - TWO * threshold
    seven_160 = rational(7, 160)
    need(correlation_cap.hi < seven_160.lo, "7/160 correlation bound")
    need(seven_160.hi < D("0.044"), "7/160 below 0.044")
    seven_40 = rational(7, 40)
    covariance_square_cap = seven_160 * LN2
    need(covariance_square_cap.hi < (seven_40 * seven_40).lo,
         "7/40 input-covariance bound")

    def sum_envelope(q_sum: IV) -> IV:
        return TWO * i_y(q_sum / TWO) + TWO * r * (TWO - q_sum)

    q_sum_endpoint = rational(17, 20)
    sum_upper = sum_envelope(q_sum_endpoint)
    need(sum_upper.hi < D("0.721880"), "displayed sum upper")
    need(sum_upper.hi < threshold.lo, "sum cutoff below RTD")
    sum_ratio = (
        (ONE + q_sum_endpoint / TWO)
        / (ONE - q_sum_endpoint / TWO)
    )
    sum_derivative = ONE - log2(sum_ratio) / TWO - TWO * r
    need(sum_derivative.lo > 0, "sum envelope increasing through 17/20")
    sum_root_lo = rational(856393, 1000000)
    sum_root_hi = rational(856394, 1000000)
    need(sum_envelope(sum_root_lo).hi < threshold.lo,
         "sum root lower endpoint")
    need(sum_envelope(sum_root_hi).lo > threshold.hi,
         "sum root upper endpoint")

    def symmetric_receiver_mi(alpha: IV) -> IV:
        probabilities = (
            alpha / FOUR,
            (ONE - alpha) / FOUR,
            (ONE - alpha) / FOUR,
            (TWO + alpha) / FOUR,
        )
        return TWO * h - entropy(probabilities)

    symmetric_lower_correlation = TWO * symmetric_receiver_mi(rational(1, 8))
    symmetric_upper_correlation = TWO * symmetric_receiver_mi(rational(5, 13))
    need(symmetric_lower_correlation.lo > seven_160.hi,
         "symmetric lower endpoint")
    need(symmetric_upper_correlation.lo > seven_160.hi,
         "symmetric upper endpoint")

    print(f"q_- = [{q_minus.lo}, {q_minus.hi}]")
    print(f"2 L_RTD = [{threshold.lo}, {threshold.hi}]")
    print(f"coordinate envelope at 3/8 = "
          f"[{coordinate_upper.lo}, {coordinate_upper.hi}]")
    print("coordinate cutoff bracket = (0.379109, 0.379110)")
    print(f"correlation cap = [{correlation_cap.lo}, {correlation_cap.hi}]")
    print(f"input-covariance square cap = "
          f"[{covariance_square_cap.lo}, {covariance_square_cap.hi}]")
    print(f"sum envelope at 17/20 = [{sum_upper.lo}, {sum_upper.hi}]")
    print("sum cutoff bracket = (0.856393, 0.856394)")
    print("symmetric endpoint correlations = "
          f"[{symmetric_lower_correlation.lo}, "
          f"{symmetric_lower_correlation.hi}] and "
          f"[{symmetric_upper_correlation.lo}, "
          f"{symmetric_upper_correlation.hi}]")


def main() -> None:
    check_claim_metadata()
    check_pruning_certificates()
    print("PASS: directed marginal and output-correlation pruning certificates")


if __name__ == "__main__":
    main()
