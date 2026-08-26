#!/usr/bin/env python3
"""Corroborate the four constant-padding residual identities."""

from fractions import Fraction as F
from functools import lru_cache
from itertools import product
from math import log2


BASE = ("W", "U", "V", "X1", "X2")
ALL = BASE + ("Y1", "Y2", "Z1", "Z2")


def need(condition, message):
    if not condition:
        raise AssertionError(message)


def bssc_y(x, y):
    return ((F(1, 2), F(1, 2)), (F(0), F(1)))[x][y]


def bssc_z(x, z):
    return ((F(1), F(0)), (F(1, 2), F(1, 2)))[x][z]


def build_law():
    base_weights = {}
    for w, u, v, x1, x2 in product(range(2), repeat=5):
        code = 1 + 3 * w + 5 * u + 7 * v + 11 * x1 + 13 * x2
        interaction = 4 * (u == x2) + 6 * (v == x1) + 5 * (x1 == x2)
        base_weights[(w, u, v, x1, x2)] = 1 + (code * code + interaction) % 23
    total = sum(base_weights.values())
    law = {}
    for base, weight in base_weights.items():
        x1, x2 = base[3], base[4]
        for y1, y2, z1, z2 in product(range(2), repeat=4):
            probability = (
                F(weight, total)
                * bssc_y(x1, y1)
                * bssc_y(x2, y2)
                * bssc_z(x1, z1)
                * bssc_z(x2, z2)
            )
            if probability:
                law[base + (y1, y2, z1, z2)] = probability
    need(sum(law.values()) == 1, "joint law normalization")
    return law


LAW = build_law()
INDEX = {name: i for i, name in enumerate(ALL)}


@lru_cache(maxsize=None)
def marginal(names):
    indices = tuple(INDEX[name] for name in names)
    out = {}
    for atom, probability in LAW.items():
        key = tuple(atom[i] for i in indices)
        out[key] = out.get(key, F(0)) + probability
    return out


@lru_cache(maxsize=None)
def entropy(names):
    if not names:
        return 0.0
    return -sum(float(p) * log2(float(p)) for p in marginal(tuple(names)).values())


def conditional_entropy(a, c=()):
    return entropy(tuple(a) + tuple(c)) - entropy(tuple(c))


def mutual_information(a, b, c=()):
    a, b, c = tuple(a), tuple(b), tuple(c)
    return (
        entropy(a + c)
        + entropy(b + c)
        - entropy(c)
        - entropy(a + b + c)
    )


def lhalf_two_letter():
    return (
        F(1, 2) * mutual_information(("W",), ("Y1", "Y2"))
        + F(1, 2) * mutual_information(("W",), ("Z1", "Z2"))
        + mutual_information(("U",), ("Y1", "Y2"), ("W",))
        + mutual_information(("V",), ("Z1", "Z2"), ("W",))
        - mutual_information(("U",), ("V",), ("W",))
    )


def coordinate_sum(a, b):
    value = 0.0
    for i in (1, 2):
        yi, zi = (f"Y{i}",), (f"Z{i}",)
        value += 0.5 * mutual_information(("W",), yi)
        value += 0.5 * mutual_information(("W",), zi)
        if i == a:
            value += mutual_information(("U",), yi, ("W",))
        if i == b:
            value += mutual_information(("V",), zi, ("W",))
        if i == a == b:
            value -= mutual_information(("U",), ("V",), ("W",))
    return value


def explicit_terms():
    a = {
        1: mutual_information(("Y2",), ("Y1", "U"), ("W",)),
        2: mutual_information(("Y1",), ("Y2", "U"), ("W",)),
    }
    b = {
        1: mutual_information(("Z2",), ("Z1", "V"), ("W",)),
        2: mutual_information(("Z1",), ("Z2", "V"), ("W",)),
    }
    d = mutual_information(("U",), ("V",), ("W",))
    charge = 0.5 * (
        mutual_information(("Y1",), ("Y2",), ("W",))
        + mutual_information(("Y1",), ("Y2",))
        + mutual_information(("Z1",), ("Z2",), ("W",))
        + mutual_information(("Z1",), ("Z2",))
    )
    return a, b, d, charge


def main():
    two = float(lhalf_two_letter())
    a_terms, b_terms, penalty, charge = explicit_terms()
    residuals = {}
    for a, b in product((1, 2), repeat=2):
        direct = two - coordinate_sum(a, b)
        explicit = a_terms[a] + b_terms[b] - (penalty if a != b else 0.0) - charge
        need(abs(direct - explicit) < 2e-12, f"padding identity ({a},{b})")
        residuals[(a, b)] = explicit

    crossed_sum = residuals[(1, 2)] + residuals[(2, 1)]
    combined = (
        mutual_information(("Y1",), ("Y2",), ("W",))
        + mutual_information(("Z1",), ("Z2",), ("W",))
        - mutual_information(("Y1",), ("Y2",))
        - mutual_information(("Z1",), ("Z2",))
        + mutual_information(("U",), ("Y2",), ("Y1", "W"))
        + mutual_information(("U",), ("Y1",), ("Y2", "W"))
        + mutual_information(("V",), ("Z2",), ("Z1", "W"))
        + mutual_information(("V",), ("Z1",), ("Z2", "W"))
        - 2.0 * penalty
    )
    need(abs(crossed_sum - combined) < 3e-12, "combined crossed-padding identity")
    need(max(residuals.values()) - min(residuals.values()) > 1e-5,
         "test law exercises distinct padding residuals")
    print("PASS: four constant-padding residual identities")
    print("PASS: crossed-test chain-rule identity")
    for pair in sorted(residuals):
        print(f"padding {pair}: residual={residuals[pair]:.15f}")


if __name__ == "__main__":
    main()
