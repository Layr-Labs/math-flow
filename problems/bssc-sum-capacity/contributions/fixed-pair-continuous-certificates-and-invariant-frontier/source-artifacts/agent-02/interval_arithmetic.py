"""Small outward-rounded Decimal interval layer used by the certificate."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import (
    Context,
    Decimal,
    ROUND_CEILING,
    ROUND_FLOOR,
    ROUND_HALF_EVEN,
    localcontext,
)

PRECISION = 80
NEAREST = Context(prec=PRECISION, rounding=ROUND_HALF_EVEN)
DOWN = Context(prec=PRECISION, rounding=ROUND_FLOOR)
UP = Context(prec=PRECISION, rounding=ROUND_CEILING)


def D(value: str | int | Decimal) -> Decimal:
    return value if isinstance(value, Decimal) else Decimal(value)


def down_add(x: Decimal, y: Decimal) -> Decimal:
    with localcontext(DOWN):
        return x + y


def up_add(x: Decimal, y: Decimal) -> Decimal:
    with localcontext(UP):
        return x + y


def down_sub(x: Decimal, y: Decimal) -> Decimal:
    with localcontext(DOWN):
        return x - y


def up_sub(x: Decimal, y: Decimal) -> Decimal:
    with localcontext(UP):
        return x - y


def down_mul(x: Decimal, y: Decimal) -> Decimal:
    with localcontext(DOWN):
        return x * y


def up_mul(x: Decimal, y: Decimal) -> Decimal:
    with localcontext(UP):
        return x * y


def down_div(x: Decimal, y: Decimal) -> Decimal:
    with localcontext(DOWN):
        return x / y


def up_div(x: Decimal, y: Decimal) -> Decimal:
    with localcontext(UP):
        return x / y


@dataclass(frozen=True)
class IV:
    lo: Decimal
    hi: Decimal

    def __post_init__(self) -> None:
        if self.lo > self.hi:
            raise ValueError((self.lo, self.hi))

    @staticmethod
    def point(value: str | int | Decimal) -> "IV":
        value = D(value)
        return IV(value, value)

    def __add__(self, other: "IV") -> "IV":
        return IV(down_add(self.lo, other.lo), up_add(self.hi, other.hi))

    def __neg__(self) -> "IV":
        return IV(self.hi.copy_negate(), self.lo.copy_negate())

    def __sub__(self, other: "IV") -> "IV":
        return self + (-other)

    def __mul__(self, other: "IV") -> "IV":
        lower = [
            down_mul(self.lo, other.lo),
            down_mul(self.lo, other.hi),
            down_mul(self.hi, other.lo),
            down_mul(self.hi, other.hi),
        ]
        upper = [
            up_mul(self.lo, other.lo),
            up_mul(self.lo, other.hi),
            up_mul(self.hi, other.lo),
            up_mul(self.hi, other.hi),
        ]
        return IV(min(lower), max(upper))

    def reciprocal(self) -> "IV":
        if self.lo <= 0 <= self.hi:
            raise ZeroDivisionError(self)
        return IV(down_div(D(1), self.hi), up_div(D(1), self.lo))

    def __truediv__(self, other: "IV") -> "IV":
        return self * other.reciprocal()

    def ln(self) -> "IV":
        if self.lo <= 0:
            raise ValueError(f"ln domain: {self}")
        with localcontext(NEAREST) as context:
            lo_near = self.lo.ln(context=context)
            hi_near = self.hi.ln(context=context)
            lo = lo_near.next_minus(context=context)
            hi = hi_near.next_plus(context=context)
        return IV(lo, hi)

    def width(self) -> Decimal:
        return up_sub(self.hi, self.lo)

    def __str__(self) -> str:
        return f"[{self.lo}, {self.hi}]"


ZERO = IV.point(0)
ONE = IV.point(1)
HALF = IV.point("0.5")
LN2 = IV.point(2).ln()
REPORTED_COMPARISON = D("0.369296340638082")
