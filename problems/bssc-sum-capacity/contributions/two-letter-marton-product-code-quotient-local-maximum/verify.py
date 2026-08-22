#!/usr/bin/env python3
"""Exact certificate for the BSSC product-code quotient local maximum.

The checker uses rational arithmetic in Q(sqrt(105)).  It constructs the
half-skew BSSC product kernels and all seven entropy marginal maps, verifies
the exact interior stationary point, forms the full 16-by-16 Hessian, and
proves negativity on the 15-dimensional simplex tangent space by exact LDL^T.
"""

from dataclasses import dataclass
from fractions import Fraction as F
import json
from math import lcm, sqrt
from pathlib import Path


D = 105
ROOT = Path(__file__).resolve().parent
DEPENDENCY = "88a1004f309460f3ec1cacdae88d30f88559f9bc"
CLAIM_KEY = (
    "bssc-sum-capacity/"
    "two-letter-marton-product-code-quotient-local-maximum"
)
EXPECTED_COUNTS = {"Y": 4, "Z": 4, "WY": 16, "WZ": 16,
                   "WUY": 25, "WVZ": 25, "WUV": 16}


def need(condition, message):
    if not condition:
        raise AssertionError(message)


def load_json(path):
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def check_metadata():
    claims = load_json(ROOT / "claims.json")
    need(claims.get("schemaVersion") == 1, "claims schema")
    payload = claims.get("claims")
    need(isinstance(payload, list) and len(payload) == 1, "single claim")
    claim = payload[0]
    need(claim.get("claimKey") == CLAIM_KEY, "claim key")
    need(
        claim.get("dependencyTransactionIds") == [DEPENDENCY],
        "sole exact-RTD dependency",
    )
    statement = claim.get("statement", "")
    for phrase in (
        "Q(sqrt(105))",
        "15-dimensional simplex tangent space",
        "strict local maximum",
        "does not rule out",
    ):
        need(phrase in statement, "claim scope token: " + phrase)

    verification = load_json(ROOT / "verification.json")
    need(verification.get("schemaVersion") == 1, "verification schema")
    need(verification.get("entrypoint") == "verify.py", "entrypoint")
    need(verification.get("arguments") == [], "no arguments")


@dataclass(frozen=True)
class Qsqrt:
    """a + b sqrt(105), represented exactly."""

    a: F = F(0)
    b: F = F(0)

    @staticmethod
    def coerce(value):
        return value if isinstance(value, Qsqrt) else Qsqrt(F(value), F(0))

    def __add__(self, other):
        other = self.coerce(other)
        return Qsqrt(self.a + other.a, self.b + other.b)

    __radd__ = __add__

    def __neg__(self):
        return Qsqrt(-self.a, -self.b)

    def __sub__(self, other):
        return self + (-self.coerce(other))

    def __rsub__(self, other):
        return self.coerce(other) - self

    def __mul__(self, other):
        other = self.coerce(other)
        return Qsqrt(
            self.a * other.a + D * self.b * other.b,
            self.a * other.b + self.b * other.a,
        )

    __rmul__ = __mul__

    def inverse(self):
        denominator = self.a * self.a - D * self.b * self.b
        if denominator == 0:
            raise ZeroDivisionError
        return Qsqrt(self.a / denominator, -self.b / denominator)

    def __truediv__(self, other):
        return self * self.coerce(other).inverse()

    def __rtruediv__(self, other):
        return self.coerce(other) / self

    def __pow__(self, exponent):
        if not isinstance(exponent, int):
            return NotImplemented
        if exponent < 0:
            return (self.inverse()) ** (-exponent)
        result = ONE
        base = self
        while exponent:
            if exponent & 1:
                result *= base
            base *= base
            exponent >>= 1
        return result

    def sign(self):
        """Exact sign, using irrationality of sqrt(105)."""
        if self.b == 0:
            return (self.a > 0) - (self.a < 0)
        if self.a == 0:
            return (self.b > 0) - (self.b < 0)
        sign_a = (self.a > 0) - (self.a < 0)
        sign_b = (self.b > 0) - (self.b < 0)
        if sign_a == sign_b:
            return sign_a
        comparison = self.a * self.a - D * self.b * self.b
        if comparison == 0:
            raise AssertionError("sqrt(105) unexpectedly rational")
        return sign_a if comparison > 0 else sign_b

    def approx(self):
        return float(self.a) + float(self.b) * sqrt(D)


ZERO = Qsqrt()
ONE = Qsqrt(F(1))
HALF = F(1, 2)


def auxiliary_map(orientation, x):
    x1, x2 = divmod(x, 2)
    return (
        (x, 0),
        (2 * x1, x2),
        (x2, 2 * x1),
        (0, x),
    )[orientation]


def one_use(receiver, input_bit, output_bit):
    if receiver == "Y":
        return F(1, 2) if input_bit == 0 else F(output_bit == 1)
    return F(output_bit == 0) if input_bit == 0 else F(1, 2)


def transition(receiver, input_symbol, output_symbol):
    x1, x2 = divmod(input_symbol, 2)
    y1, y2 = divmod(output_symbol, 2)
    return one_use(receiver, x1, y1) * one_use(receiver, x2, y2)


def aggregation(keys, receiver=None):
    rows = {}
    for w in range(4):
        for x in range(4):
            u, v = auxiliary_map(w, x)
            column = 4 * w + x
            for output in range(4) if receiver else (None,):
                values = {"w": w, "u": u, "v": v, "x": x, "o": output}
                key = tuple(values[name] for name in keys)
                weight = transition(receiver, x, output) if receiver else F(1)
                if weight:
                    rows.setdefault(key, [F(0)] * 16)[column] += weight
    return tuple(tuple(row) for row in rows.values())


TERMS = (
    (F(1, 2), aggregation(("o",), "Y"), "Y"),
    (F(1, 2), aggregation(("o",), "Z"), "Z"),
    (F(1, 2), aggregation(("w", "o"), "Y"), "WY"),
    (F(1, 2), aggregation(("w", "o"), "Z"), "WZ"),
    (F(-1), aggregation(("w", "u", "o"), "Y"), "WUY"),
    (F(-1), aggregation(("w", "v", "o"), "Z"), "WVZ"),
    (F(1), aggregation(("w", "u", "v")), "WUV"),
)


def qstar():
    low = Qsqrt(F(11, 120), F(-1, 120))
    middle = Qsqrt(F(1, 30))
    high = Qsqrt(F(11, 120), F(1, 120))
    return (
        low, middle, middle, high,
        middle, low, high, middle,
        middle, high, low, middle,
        high, middle, middle, low,
    )


def dot(row, vector):
    return sum((Qsqrt.coerce(x) * y for x, y in zip(row, vector)), ZERO)


def product_tensor_check(q, qminus):
    low = qminus / 2
    high = (1 - qminus) / 2
    one_letter = ((low, high), (high, low))
    expected = []
    for s1 in range(2):
        for s2 in range(2):
            for x1 in range(2):
                for x2 in range(2):
                    expected.append(one_letter[s1][x1] * one_letter[s2][x2])
                    u1, v1 = (x1, 0) if s1 == 0 else (0, x1)
                    u2, v2 = (x2, 0) if s2 == 0 else (0, x2)
                    need(
                        auxiliary_map(2 * s1 + s2, 2 * x1 + x2)
                        == (2 * u1 + u2, 2 * v1 + v2),
                        "product-code orientation",
                    )
    need(tuple(expected) == q, "q* tensor-product law")


def exact_stationarity(q):
    """Prove all 16 gradient entries equal by exact log-product identities."""
    constants = [F(0)] * 16
    logarithms = [{} for _ in range(16)]
    for coefficient, rows, name in TERMS:
        for row in rows:
            mass = dot(row, q)
            need(mass.sign() > 0, name + " positive marginal")
            for column, weight in enumerate(row):
                if not weight:
                    continue
                log_coefficient = -coefficient * weight
                constants[column] += log_coefficient
                current = logarithms[column].get(mass, F(0))
                logarithms[column][mass] = current + log_coefficient

    verified = 0
    for column in range(1, 16):
        need(constants[column] == constants[0], "gradient constant terms")
        difference = dict(logarithms[column])
        for mass, coefficient in logarithms[0].items():
            difference[mass] = difference.get(mass, F(0)) - coefficient
        difference = {
            mass: coefficient
            for mass, coefficient in difference.items()
            if coefficient
        }
        common = 1
        for coefficient in difference.values():
            common = lcm(common, coefficient.denominator)
        positive = ONE
        negative = ONE
        for mass, coefficient in difference.items():
            exponent = int(coefficient * common)
            need(F(exponent) == coefficient * common, "integral log exponent")
            if exponent > 0:
                positive *= mass ** exponent
            else:
                negative *= mass ** (-exponent)
        need(positive == negative, "exact gradient log-product identity")
        verified += 1
    return verified


def exact_hessian(q):
    hessian = [[ZERO for _ in range(16)] for _ in range(16)]
    marginal_counts = {}
    for coefficient, rows, name in TERMS:
        marginal_counts[name] = len(rows)
        for row in rows:
            mass = dot(row, q)
            if mass.sign() <= 0:
                raise AssertionError((name, "nonpositive marginal", mass))
            for i, left in enumerate(row):
                if not left:
                    continue
                for j, right in enumerate(row):
                    if right:
                        hessian[i][j] += -coefficient * left * right / mass
    return hessian, marginal_counts


def tangent_restriction(hessian):
    # Columns of B are e_i-e_15, i=0,...,14; return B^T H B.
    return [
        [
            hessian[i][j] - hessian[i][15]
            - hessian[15][j] + hessian[15][15]
            for j in range(15)
        ]
        for i in range(15)
    ]


def ldl_pivots(matrix):
    n = len(matrix)
    lower = [[ZERO for _ in range(n)] for _ in range(n)]
    pivots = []
    for i in range(n):
        lower[i][i] = ONE
        pivot = matrix[i][i] - sum(
            (lower[i][k] * lower[i][k] * pivots[k] for k in range(i)),
            ZERO,
        )
        if pivot.sign() >= 0:
            raise AssertionError(("nonnegative LDL pivot", i, pivot))
        pivots.append(pivot)
        for j in range(i + 1, n):
            numerator = matrix[j][i] - sum(
                (
                    lower[j][k] * lower[i][k] * pivots[k]
                    for k in range(i)
                ),
                ZERO,
            )
            lower[j][i] = numerator / pivot
    # Exact reconstruction is a separate implementation check.
    for i in range(n):
        for j in range(n):
            reconstructed = sum(
                (lower[i][k] * pivots[k] * lower[j][k]
                 for k in range(min(i, j) + 1)),
                ZERO,
            )
            if reconstructed != matrix[i][j]:
                raise AssertionError(("LDL reconstruction", i, j))
    return pivots


def main():
    check_metadata()
    q = qstar()
    need(
        sum(q, ZERO) == ONE and all(item.sign() > 0 for item in q),
        "q* interior simplex",
    )

    qminus = Qsqrt(F(1, 2), F(-1, 30))
    need(
        15 * qminus * qminus - 15 * qminus + 2 == ZERO,
        "q_- stationary polynomial",
    )
    likelihood_ratio = ((2 - qminus) * (1 + qminus)) / (
        qminus * (1 - qminus)
    )
    need(likelihood_ratio == Qsqrt(F(16)), "stationary ratio equals 16")
    product_tensor_check(q, qminus)
    stationarity_identities = exact_stationarity(q)
    need(stationarity_identities == 15, "all tangent gradient identities")

    hessian, counts = exact_hessian(q)
    need(counts == EXPECTED_COUNTS, "all seven marginal-map row counts")
    for i in range(16):
        for j in range(16):
            need(hessian[i][j] == hessian[j][i], "Hessian symmetry")
    pivots = ldl_pivots(tangent_restriction(hessian))
    need(len(pivots) == 15, "15-dimensional tangent LDL")

    print("PASS: exact BSSC product-code quotient strict local maximum")
    print("q cells:", "low=(11-sqrt(105))/120, middle=1/30, high=(11+sqrt(105))/120")
    print("exact tangent gradient identities:", stationarity_identities)
    print("marginal row counts:", counts)
    print("tangent dimension:", len(pivots))
    print("negative exact LDL pivots:", sum(p.sign() < 0 for p in pivots))
    print("approximate pivots:")
    for index, pivot in enumerate(pivots):
        print(index, format(pivot.approx(), ".17g"))


if __name__ == "__main__":
    main()
