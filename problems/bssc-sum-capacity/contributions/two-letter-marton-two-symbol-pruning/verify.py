#!/usr/bin/env python3
"""Exact orbit audit and directed repetition-orbit tangent certificate."""

from dataclasses import dataclass
from decimal import Context, Decimal, ROUND_CEILING, ROUND_FLOOR, ROUND_HALF_EVEN
from fractions import Fraction as F
from itertools import combinations


D = Decimal
NEAR = Context(prec=80, rounding=ROUND_HALF_EVEN)
DOWN = Context(prec=80, rounding=ROUND_FLOOR)
UP = Context(prec=80, rounding=ROUND_CEILING)


def need(ok, message):
    if not ok:
        raise AssertionError(message)


@dataclass(frozen=True)
class IV:
    lo: Decimal
    hi: Decimal

    def __post_init__(self):
        need(self.lo <= self.hi, "reversed interval")

    @staticmethod
    def point(x):
        x = x if isinstance(x, Decimal) else D(x)
        return IV(x, x)

    def __add__(self, other):
        return IV(DOWN.add(self.lo, other.lo), UP.add(self.hi, other.hi))

    def __neg__(self):
        return IV(self.hi.copy_negate(), self.lo.copy_negate())

    def __sub__(self, other):
        return self + (-other)

    def __mul__(self, other):
        products = ((self.lo, other.lo), (self.lo, other.hi),
                    (self.hi, other.lo), (self.hi, other.hi))
        return IV(min(DOWN.multiply(a, b) for a, b in products),
                  max(UP.multiply(a, b) for a, b in products))

    def __truediv__(self, other):
        need(not (other.lo <= 0 <= other.hi), "interval division by zero")
        inverse = IV(DOWN.divide(D(1), other.hi),
                     UP.divide(D(1), other.lo))
        return self * inverse

    def ln(self):
        need(self.lo > 0, "logarithm domain")
        lo = NEAR.ln(self.lo).next_minus(context=NEAR)
        hi = NEAR.ln(self.hi).next_plus(context=NEAR)
        return IV(lo, hi)


Q = IV.point
ONE = Q(1)
LN2 = Q(2).ln()


def entropy(probabilities):
    out = Q(0)
    for probability in probabilities:
        p = probability if isinstance(probability, IV) else Q(probability)
        if p.lo == p.hi == 0:
            continue
        out = out - p * p.ln() / LN2
    return out


def j_rep(q):
    q = q if isinstance(q, IV) else Q(q)
    a = q / Q(4)
    b = ONE - Q(3) * q / Q(4)
    return entropy((a, a, a, b)) - Q(2) * q


def jp_rep(q):
    q = q if isinstance(q, IV) else Q(q)
    return Q("0.75") * ((Q(4) - Q(3) * q) / q).ln() / LN2 - Q(2)


def product_channel(base):
    result = []
    for x in range(4):
        x1, x2 = divmod(x, 2)
        row = []
        for y in range(4):
            y1, y2 = divmod(y, 2)
            row.append(base[x1][y1] * base[x2][y2])
        result.append(tuple(row))
    return tuple(result)


def exact_orbit_audit():
    y = ((F(1, 2), F(1, 2)), (F(0), F(1)))
    z = ((F(1), F(0)), (F(1, 2), F(1, 2)))
    yy, zz = product_channel(y), product_channel(z)

    pairs = list(combinations(range(4), 2))
    adjacent = [p for p in pairs if (p[0] ^ p[1]).bit_count() == 1]
    diagonal = [p for p in pairs if (p[0] ^ p[1]).bit_count() == 2]
    need(len(pairs) == 6 and len(adjacent) == 4 and
         diagonal == [(0, 3), (1, 2)], "support orbit classification")

    # Repetition transition rows used in equation (1).
    need(yy[0] == (F(1, 4),) * 4 and yy[3] == (0, 0, 0, 1),
         "Y repetition rows")
    need(zz[0] == (1, 0, 0, 0) and zz[3] == (F(1, 4),) * 4,
         "Z repetition rows")

    # Antirepetition: each marginal has one common erasure output of mass 1/2
    # and one disjoint identifying output of mass 1/2 for each input.
    for channel in (yy, zz):
        r0, r1 = channel[1], channel[2]
        common = [i for i in range(4) if r0[i] == r1[i] == F(1, 2)]
        unique0 = [i for i in range(4) if r0[i] == F(1, 2) and r1[i] == 0]
        unique1 = [i for i in range(4) if r1[i] == F(1, 2) and r0[i] == 0]
        need(len(common) == len(unique0) == len(unique1) == 1,
             "antirepetition BEC structure")

    # Every adjacent pair has an input-independent coordinate and a varying
    # coordinate with exactly the original half-skew transition matrices.
    for a, b in adjacent:
        differing = 0 if (a // 2) != (b // 2) else 1
        for channel, base in ((yy, y), (zz, z)):
            for symbol in range(2):
                marginal_a = sum(channel[a][out] for out in range(4)
                                 if divmod(out, 2)[differing] == symbol)
                marginal_b = sum(channel[b][out] for out in range(4)
                                 if divmod(out, 2)[differing] == symbol)
                need((marginal_a, marginal_b) ==
                     (base[0][symbol], base[1][symbol]),
                     "adjacent varying-coordinate marginal")


def interval_certificate():
    q0 = Q("0.85")
    half = Q("0.5")
    jhalf = j_rep(half)
    d0 = j_rep(ONE - q0) - j_rep(q0)
    dp0 = -jp_rep(ONE - q0) - jp_rep(q0)

    need(jhalf.hi < D("0.549"), "J(1/2) coarse bound")
    need(dp0.hi < 0, "negative tangent slope")

    # A concave function is below its tangent. Since this tangent has negative
    # slope, its maximum on [1/2,1] is attained at the left endpoint.
    d_upper = UP.add(d0.hi,
                     UP.multiply(dp0.lo.copy_negate(), D("0.35")))
    need(d_upper < D("0.132"), "global |D| tangent bound")
    marton_upper = UP.add(jhalf.hi, UP.divide(d_upper, D(2)))
    need(marton_upper < D("0.615"), "repetition Marton bound")

    product_rtd_floor = D("0.7232857688439092")
    need(D("0.615") < product_rtd_floor,
         "strict separation from product RTD")
    return jhalf, d0, dp0, d_upper, marton_upper


def main():
    exact_orbit_audit()
    jhalf, d0, dp0, d_upper, marton_upper = interval_certificate()
    print("PASS: 6 support pairs = 4 adjacent + antirepetition + repetition")
    print("J_rep(1/2) =", f"[{jhalf.lo}, {jhalf.hi}]")
    print("D(17/20) =", f"[{d0.lo}, {d0.hi}]")
    print("D'(17/20) =", f"[{dp0.lo}, {dp0.hi}]")
    print("global max |D| upper =", d_upper)
    print("repetition Marton upper =", marton_upper)
    print("certified coarse headline < 0.615 < 0.7232857688439092")


if __name__ == "__main__":
    main()
