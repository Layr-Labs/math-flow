#!/usr/bin/env python3
"""Exact face audit and directed certificates for full-support necessity."""

from dataclasses import dataclass
from decimal import Context, Decimal, ROUND_CEILING, ROUND_FLOOR, ROUND_HALF_EVEN
from fractions import Fraction as F


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

    @staticmethod
    def fraction(x):
        x = x if isinstance(x, F) else F(x)
        return IV(
            DOWN.divide(D(x.numerator), D(x.denominator)),
            UP.divide(D(x.numerator), D(x.denominator)),
        )

    def __add__(self, other):
        other = as_iv(other)
        return IV(DOWN.add(self.lo, other.lo), UP.add(self.hi, other.hi))

    def __radd__(self, other):
        return self + other

    def __neg__(self):
        return IV(self.hi.copy_negate(), self.lo.copy_negate())

    def __sub__(self, other):
        return self + (-as_iv(other))

    def __rsub__(self, other):
        return as_iv(other) - self

    def __mul__(self, other):
        other = as_iv(other)
        products = (
            (self.lo, other.lo),
            (self.lo, other.hi),
            (self.hi, other.lo),
            (self.hi, other.hi),
        )
        return IV(
            min(DOWN.multiply(a, b) for a, b in products),
            max(UP.multiply(a, b) for a, b in products),
        )

    def __rmul__(self, other):
        return self * other

    def __truediv__(self, other):
        other = as_iv(other)
        need(not (other.lo <= 0 <= other.hi), "interval division by zero")
        inverse = IV(
            DOWN.divide(D(1), other.hi),
            UP.divide(D(1), other.lo),
        )
        return self * inverse

    def ln(self):
        need(self.lo > 0, "logarithm domain")
        # Decimal.ln is correctly rounded to nearest. Expand by one ulp at
        # both endpoints to turn those evaluations into an outward interval.
        lo = NEAR.ln(self.lo).next_minus(context=NEAR)
        hi = NEAR.ln(self.hi).next_plus(context=NEAR)
        return IV(lo, hi)


def as_iv(x):
    if isinstance(x, IV):
        return x
    if isinstance(x, F):
        return IV.fraction(x)
    return IV.point(x)


Q = IV.point
QF = IV.fraction
ONE = Q(1)
LN2 = Q(2).ln()


def log2(x):
    return as_iv(x).ln() / LN2


def entropy(probabilities):
    out = Q(0)
    for probability in probabilities:
        p = as_iv(probability)
        if p.lo == p.hi == 0:
            continue
        out = out - p * log2(p)
    return out


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


def transpose_bits(x):
    x1, x2 = divmod(x, 2)
    return 2 * x2 + x1


def complement_bits(x):
    return x ^ 3


def generated_orbit(seed):
    todo = [seed]
    seen = set()
    while todo:
        x = todo.pop()
        if x in seen:
            continue
        seen.add(x)
        todo.extend((transpose_bits(x), complement_bits(x)))
    return frozenset(seen)


def affine_output(channel, weighted_inputs):
    """Return exact (constant, linear) coefficients in the parameter s."""
    output = []
    for out in range(4):
        constant = sum(c * channel[x][out] for x, (c, _) in weighted_inputs)
        linear = sum(k * channel[x][out] for x, (_, k) in weighted_inputs)
        output.append((constant, linear))
    return tuple(output)


def uniform_row_entropy(row):
    support = [p for p in row if p]
    need(support and len(set(support)) == 1, "expected uniform transition row")
    return {1: 0, 2: 1, 4: 2}[len(support)]


def affine_row_entropy(channel, weighted_inputs):
    constant = sum(c * uniform_row_entropy(channel[x])
                   for x, (c, _) in weighted_inputs)
    linear = sum(k * uniform_row_entropy(channel[x])
                 for x, (_, k) in weighted_inputs)
    return constant, linear


def exact_face_audit():
    y = ((F(1, 2), F(1, 2)), (F(0), F(1)))
    z = ((F(1), F(0)), (F(1, 2), F(1, 2)))
    yy, zz = product_channel(y), product_channel(z)

    for x in range(4):
        for out in range(4):
            need(yy[transpose_bits(x)][transpose_bits(out)] == yy[x][out],
                 "Y coordinate-transposition symmetry")
            need(zz[transpose_bits(x)][transpose_bits(out)] == zz[x][out],
                 "Z coordinate-transposition symmetry")
            need(yy[x][out] ==
                 zz[complement_bits(x)][complement_bits(out)],
                 "receiver-skew reflection")

    orbits = {generated_orbit(missing) for missing in range(4)}
    need(orbits == {frozenset((0, 3)), frozenset((1, 2))},
         "four faces split into the two claimed symmetry orbits")

    # Missing-00 representative: p01=p10=s, p11=1-2s.
    end_weights = (
        (1, (F(0), F(1))),
        (2, (F(0), F(1))),
        (3, (F(1), F(-2))),
    )
    need(affine_output(yy, end_weights) == (
        (F(0), F(0)), (F(0), F(1, 2)),
        (F(0), F(1, 2)), (F(1), F(-1))),
        "missing-00 Y output law")
    need(affine_output(zz, end_weights) == (
        (F(1, 4), F(1, 2)), (F(1, 4), F(0)),
        (F(1, 4), F(0)), (F(1, 4), F(-1, 2))),
        "missing-00 Z output law")
    need(affine_row_entropy(yy, end_weights) == (F(0), F(2)),
         "missing-00 Y row entropy")
    need(affine_row_entropy(zz, end_weights) == (F(2), F(-2)),
         "missing-00 Z row entropy")

    # Missing-01 representative after endpoint symmetrization:
    # p00=p11=(1-s)/2, p10=s.
    mixed_weights = (
        (0, (F(1, 2), F(-1, 2))),
        (2, (F(0), F(1))),
        (3, (F(1, 2), F(-1, 2))),
    )
    y_mixed = affine_output(yy, mixed_weights)
    z_mixed = affine_output(zz, mixed_weights)
    expected_y = (
        (F(1, 8), F(-1, 8)), (F(1, 8), F(-1, 8)),
        (F(1, 8), F(3, 8)), (F(5, 8), F(-1, 8)),
    )
    need(y_mixed == expected_y, "missing-01 Y output law")
    need(sorted(z_mixed) == sorted(expected_y),
         "missing-01 receiver output laws are permutations")
    need(affine_row_entropy(yy, mixed_weights) == (F(1), F(0)),
         "missing-01 Y row entropy")
    need(affine_row_entropy(zz, mixed_weights) == (F(1), F(0)),
         "missing-01 Z row entropy")


def phi(m, face_bound):
    m = QF(m)
    return entropy((m, ONE - m)) + (ONE - m) * face_bound


def interval_certificate():
    quarter = QF(F(1, 4))
    h_quarter = entropy((quarter, ONE - quarter))
    r = h_quarter - QF(F(3, 4))
    two_r = Q(2) * r
    need(r.lo > 0, "positive BSSC support constant")

    c_end = QF(F(3, 4)) * log2(QF(F(5, 3)))
    s = F(2, 5)
    # This is the squared exact stationarity equation corresponding to G'=0.
    stationary = (F(4) * ((1 - s) / s) ** 2
                  * ((1 - 2 * s) / (1 + 2 * s)))
    need(stationary == 1, "exact missing-00 stationary point")

    tangent_slope = QF(F(1, 8)) * log2(QF(F(725, 729)))
    need(tangent_slope.hi < 0, "negative missing-01 tangent slope")
    c_mixed_at_s0 = entropy((
        QF(F(5, 48)), QF(F(5, 48)),
        QF(F(9, 48)), QF(F(29, 48)),
    )) - ONE
    c_mixed = c_mixed_at_s0 - QF(F(1, 6)) * tangent_slope

    end_total = c_end + two_r
    mixed_total = c_mixed + two_r
    need(c_end.hi < D("0.553"), "exact missing-end G bound")
    need(end_total.hi < D("0.676"), "missing-end Marton bound")
    need(c_mixed.hi < D("0.573"), "missing-mixed tangent G bound")
    need(mixed_total.hi < D("0.695"), "universal three-face Marton bound")

    # Exact value of two independent copies of the fair q=1/6 reflected RTD
    # schedule: 2 h2(1/4)+h2(1/12)-h2(5/12)-1/3.
    rtd_witness = (
        Q(2) * h_quarter
        + entropy((QF(F(1, 12)), QF(F(11, 12))))
        - entropy((QF(F(5, 12)), QF(F(7, 12))))
        - QF(F(1, 3))
    )
    need(rtd_witness.lo > D("0.7231"),
         "explicit rational-schedule product RTD witness")
    need(D("0.695") < rtd_witness.lo,
         "strict separation from explicit product RTD witness")

    end_mass = F(1, 180)
    mixed_mass = F(1, 325)
    end_mass_upper = phi(end_mass, c_end) + two_r
    mixed_mass_upper = phi(mixed_mass, c_mixed) + two_r
    need(end_mass_upper.hi < rtd_witness.lo, "00/11 mass-floor separation")
    need(mixed_mass_upper.hi < rtd_witness.lo, "01/10 mass-floor separation")

    end_derivative = log2(QF((1 - end_mass) / end_mass)) - c_end
    mixed_derivative = log2(QF((1 - mixed_mass) / mixed_mass)) - c_mixed
    need(end_derivative.lo > 0, "00/11 mass potential is increasing")
    need(mixed_derivative.lo > 0, "01/10 mass potential is increasing")

    return {
        "r": r,
        "c_end": c_end,
        "c_mixed": c_mixed,
        "end_total": end_total,
        "mixed_total": mixed_total,
        "rtd_witness": rtd_witness,
        "end_mass_upper": end_mass_upper,
        "mixed_mass_upper": mixed_mass_upper,
    }


def show(name, interval):
    print(f"{name} = [{interval.lo}, {interval.hi}]")


def main():
    exact_face_audit()
    values = interval_certificate()
    print("PASS: 4 three-symbol faces = 2 exact symmetry orbits")
    show("r", values["r"])
    show("missing-end max G", values["c_end"])
    show("missing-end Marton upper", values["end_total"])
    show("missing-mixed tangent G upper", values["c_mixed"])
    show("missing-mixed Marton upper", values["mixed_total"])
    show("explicit q=1/6 product RTD witness", values["rtd_witness"])
    show("upper at p00/p11=1/180", values["end_mass_upper"])
    show("upper at p01/p10=1/325", values["mixed_mass_upper"])
    print("certified headline: support <= 3 gives M < 0.695 < B_1/6")
    print("certified gain floors: p00,p11 > 1/180; p01,p10 > 1/325")


if __name__ == "__main__":
    main()
