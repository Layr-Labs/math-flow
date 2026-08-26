#!/usr/bin/env python3
"""High-precision audit of the exact half-skew BSSC specialization."""

from decimal import Decimal, getcontext
from fractions import Fraction


getcontext().prec = 90
ONE = Decimal(1)


def h2(q: Decimal) -> Decimal:
    if q == 0 or q == 1:
        return Decimal(0)
    return -(q * q.ln() + (ONE - q) * (ONE - q).ln()) / Decimal(2).ln()


def t(q: Decimal) -> Decimal:
    i_y = h2((ONE - q) / 2) - (ONE - q)
    i_z = h2(q / 2) - q
    return i_y - i_z


def main() -> None:
    h = h2(ONE / 4)
    r = h - Decimal(3) / 4
    contact = Decimal(4) / 5

    assert abs(t(contact) - Decimal(8) * r / 5) < Decimal("1e-80")
    assert t(Decimal(0)) == 0
    assert Decimal(5) / 8 * contact == ONE / 2
    assert abs(Decimal(5) / 8 * t(contact) - r) < Decimal("1e-80")

    y = (
        (Fraction(1, 2), Fraction(1, 2)),
        (Fraction(0), Fraction(1)),
    )
    z = (
        (Fraction(1), Fraction(0)),
        (Fraction(1, 2), Fraction(1, 2)),
    )
    for x in range(2):
        for output in range(2):
            assert y[1 - x][output] == z[x][1 - output]
            assert z[1 - x][output] == y[x][1 - output]

    value = 2 * h - Decimal(5) / 4
    governed_upper = Decimal("0.369316568803963")
    assert value > governed_upper
    print("PASS: BSSC support contact and receiver-skew identities")
    print(f"normalized relaxed-UV value: {value}")


if __name__ == "__main__":
    main()
