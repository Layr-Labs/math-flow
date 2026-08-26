#!/usr/bin/env python3
"""Mechanical certificate for paired-output BSSC KL curvature.

This verifier performs no writes and no network access.
"""

from __future__ import annotations

import json
from decimal import Context, Decimal, ROUND_CEILING, ROUND_HALF_EVEN
from fractions import Fraction
from pathlib import Path


ROOT = Path(__file__).resolve().parent
D = Decimal
NEAR = Context(prec=100, rounding=ROUND_HALF_EVEN)
UP = Context(prec=100, rounding=ROUND_CEILING)
MARGINAL_TX = "9bb22afe5abd3e1d9f419c1717bd61bb33a958ff"
CLAIM_KEY = "bssc-sum-capacity/two-letter-output-covariance-curvature"


def need(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def polynomial(x: Fraction) -> Fraction:
    return 124 * x**3 + 62 * x**2 - 42 * x + 5


def derivative(x: Fraction) -> Fraction:
    return 372 * x**2 + 124 * x - 42


def poly_add(*polynomials: tuple[Fraction, ...]) -> tuple[Fraction, ...]:
    size = max(map(len, polynomials))
    return tuple(
        sum((p[i] if i < len(p) else Fraction(0)) for p in polynomials)
        for i in range(size)
    )


def poly_mul(
    left: tuple[Fraction, ...],
    right: tuple[Fraction, ...],
) -> tuple[Fraction, ...]:
    result = [Fraction(0)] * (len(left) + len(right) - 1)
    for i, a in enumerate(left):
        for j, b in enumerate(right):
            result[i + j] += a * b
    return tuple(result)


def poly_scale(
    scalar: Fraction,
    polynomial_: tuple[Fraction, ...],
) -> tuple[Fraction, ...]:
    return tuple(scalar * coefficient for coefficient in polynomial_)


def check_claim_metadata() -> None:
    payload = json.loads((ROOT / "claims.json").read_text(encoding="utf-8"))
    need(payload.get("schemaVersion") == 1, "claim schema")
    claims = payload.get("claims")
    need(isinstance(claims, list) and len(claims) == 1, "single claim")
    claim = claims[0]
    need(claim.get("claimKey") == CLAIM_KEY, "claim key")
    need(
        claim.get("dependencyTransactionIds") == [MARGINAL_TX],
        "exact direct dependency",
    )
    statement = claim.get("statement", "")
    for token in (
        "C_out >= 31 c_in^2/(20 ln 2)",
        "C_out < 7/160",
        "sqrt(7 ln 2/248) < 7/50",
        "necessary condition only",
    ):
        need(token in statement, f"claim statement token: {token}")

    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    need(MARGINAL_TX in readme, "README dependency")
    need("__MARGINAL_CORRELATION_TX_PENDING__" not in readme, "no placeholder")
    need(not (ROOT / "PENDING_DEPENDENCY.md").exists(), "no pending gate")


def check_reciprocal_lemma() -> None:
    one_fifth = Fraction(1, 5)
    twenty_one_hundredths = Fraction(21, 100)
    need(derivative(one_fifth) == Fraction(-58, 25), "left derivative")
    need(
        derivative(twenty_one_hundredths) == Fraction(1113, 2500),
        "right derivative",
    )

    # Exact coefficient audit after x=1/5+t.
    need(polynomial(one_fifth) == Fraction(9, 125), "constant coefficient")
    need(Fraction(3 * 124, 5) + 62 == Fraction(682, 5), "quadratic")
    need(
        Fraction(3 * 124, 25) + Fraction(2 * 62, 5) - 42
        == Fraction(-58, 25),
        "linear",
    )
    lower = Fraction(9, 125) - Fraction(58, 25) * Fraction(1, 100)
    need(lower == Fraction(61, 1250) > 0, "minimum positivity margin")

    # Directly derive the coefficients after clearing
    # 5*x*(1/2-x)*(1+x) from
    # 4*(1/x+2/(1/2-x)+1/(1+x))-248/5.
    x_poly = (Fraction(0), Fraction(1))
    half_minus_x = (Fraction(1, 2), Fraction(-1))
    one_plus_x = (Fraction(1), Fraction(1))
    cleared = poly_add(
        poly_scale(20, poly_mul(half_minus_x, one_plus_x)),
        poly_scale(40, poly_mul(x_poly, one_plus_x)),
        poly_scale(20, poly_mul(x_poly, half_minus_x)),
        poly_scale(
            -248,
            poly_mul(poly_mul(x_poly, half_minus_x), one_plus_x),
        ),
    )
    twice_p = (Fraction(10), Fraction(-84), Fraction(124), Fraction(248))
    need(cleared == twice_p, "cleared polynomial identity")

    # Curvature in d is >248/(5 ln2); Taylor contributes 1/2, and
    # d=c/4 contributes 1/16.
    need(Fraction(248, 5) * Fraction(1, 2) * Fraction(1, 16)
         == Fraction(31, 20), "curvature rescaling")


def directed_ln2() -> tuple[Decimal, Decimal]:
    nearest = NEAR.ln(D(2))
    return (
        nearest.next_minus(context=NEAR),
        nearest.next_plus(context=NEAR),
    )


def check_covariance_constants() -> None:
    ln2_lo, ln2_hi = directed_ln2()

    # Preliminary bounded-marginal route:
    # 77 ln(2)/2048 < (13/80)^2.
    preliminary_hi = UP.divide(UP.multiply(D(77), ln2_hi), D(2048))
    preliminary_rational = UP.divide(D(169), D(6400))
    need(preliminary_hi < preliminary_rational, "13/80 preliminary bound")

    # Paired-table route: 7 ln(2)/248 < (7/50)^2.
    paired_hi = UP.divide(UP.multiply(D(7), ln2_hi), D(248))
    paired_rational = UP.divide(D(49), D(2500))
    need(paired_hi < paired_rational, "7/50 paired bound")
    need(Fraction(7, 50) < Fraction(13, 80), "strict improvement")

    radius = NEAR.sqrt(NEAR.divide(NEAR.multiply(D(7), ln2_hi), D(248)))
    print(f"ln(2) enclosure: [{ln2_lo}, {ln2_hi}]")
    print(f"paired covariance-square upper: {paired_hi}")
    print(f"paired covariance radius (orientation): {radius}")
    print("certified rational radius: 7/50 = 0.14")


def main() -> None:
    check_claim_metadata()
    check_reciprocal_lemma()
    check_covariance_constants()
    print("PASS: paired-output KL curvature and covariance-pruning certificate")


if __name__ == "__main__":
    main()
