#!/usr/bin/env python3
"""Exact symbolic audit for the finite-grid Q0 foundation claim.

No optimizer or floating-point comparison is used.  The program rebuilds the
30 scalar rows supplied by the declared foundation transaction, compares them
with a reviewed normalized-signature digest, and checks the H/L/X witnesses from README.md by
coefficientwise nonnegativity after the stated nonnegative substitutions.
"""

from __future__ import annotations

import hashlib
import json
from collections import Counter
from dataclasses import dataclass
from fractions import Fraction as F
from pathlib import Path


Term = tuple[int, str, int, F]  # group 1..3, kind, letter Y/G/K/Z, coefficient

FOUNDATION_TRANSACTION = "e3c1036ca607539a5ebcddf3058e6014ac5c1cd9"
EXPECTED_FOUNDATION_ROW_SHA256 = (
    "9d742dba6f0c176fbf5152ead6e44ffbb48095aa48a41e6f31f598529dcfb931"
)


@dataclass(frozen=True)
class Row:
    label: str
    r1: int
    r2: int
    terms: tuple[Term, ...]


MIRROR_KIND = {
    "W": "W",
    "U|W": "V|W",
    "V|W": "U|W",
    "UW": "VW",
    "VW": "UW",
    "X|UW": "X|VW",
    "X|VW": "X|UW",
}


def mirror_terms(terms: tuple[Term, ...]) -> tuple[Term, ...]:
    return tuple((4 - j, MIRROR_KIND[kind], 3 - letter, coeff)
                 for j, kind, letter, coeff in terms)


def make_rows() -> list[Row]:
    """Build the L=3 manuscript rows directly from their path formulas."""
    rows: list[Row] = []
    L = 3

    for m in range(1, L + 1):
        u_walk = tuple(
            term for j in range(1, m)
            for term in ((j, "UW", j - 1, F(1)), (j, "UW", j, F(-1)))
        )
        uc_walk = tuple(
            term for j in range(1, m)
            for term in ((j, "U|W", j - 1, F(1)), (j, "U|W", j, F(-1)))
        )
        vc_walk = tuple(
            term for j in range(m + 1, L + 1)
            for term in ((j, "V|W", j, F(1)), (j, "V|W", j - 1, F(-1)))
        )
        v_walk = tuple(
            term for j in range(m + 1, L + 1)
            for term in ((j, "VW", j, F(1)), (j, "VW", j - 1, F(-1)))
        )
        rows.append(Row(f"SL({m},U)", 1, 1, u_walk +
                        ((m, "UW", m - 1, F(1)),
                         (m, "X|UW", m, F(1))) + vc_walk))
        rows.append(Row(f"SR({m},U)", 1, 1, v_walk +
                        ((m, "VW", m, F(1)),
                         (m, "X|VW", m - 1, F(1))) + uc_walk))
        if m == L:
            rows.append(Row(f"SL({m},C)", 1, 1, uc_walk +
                            ((m, "U|W", m - 1, F(1)),
                             (m, "X|UW", m, F(1)),
                             (m, "W", m, F(1))) + vc_walk))
        if m == 1:
            rows.append(Row(f"SR({m},C)", 1, 1, vc_walk +
                            ((m, "V|W", m, F(1)),
                             (m, "X|VW", m - 1, F(1)),
                             (m, "W", m - 1, F(1))) + uc_walk))

    r1_rows: list[Row] = []
    for t in range(L):
        terms = tuple(
            term for j in range(1, t + 1)
            for term in ((j, "UW", j - 1, F(1)), (j, "UW", j, F(-1)))
        ) + ((t + 1, "UW", t, F(1)),)
        r1_rows.append(Row(f"R1T({t})", 1, 0, terms))
    for s in range(L):
        terms = tuple(
            term for j in range(1, s + 1)
            for term in ((j, "U|W", j - 1, F(1)),
                         (j, "U|W", j, F(-1)))
        ) + ((s + 1, "U|W", s, F(1)),) + tuple(
            term for j in range(s + 1, L)
            for term in ((j, "W", j, F(1)), (j + 1, "W", j, F(-1)))
        ) + ((L, "W", L, F(1)),)
        r1_rows.append(Row(f"R1A({s})", 1, 0, terms))
    rows.extend(r1_rows)
    rows.extend(Row("R2" + row.label[2:], 0, 1, mirror_terms(row.terms))
                for row in r1_rows)

    n_rows: list[Row] = []
    for t in range(L):
        terms = ((1, "W", 0, F(1)),) + tuple(
            term for j in range(1, t + 1)
            for term in ((j + 1, "W", j, F(1)), (j, "W", j, F(-1)))
        )
        n_rows.append(Row(f"N_Y({t})", 0, 0, terms))
    rows.extend(n_rows)
    rows.extend(Row(f"N_Z({t})", 0, 0, mirror_terms(row.terms))
                for t, row in enumerate(n_rows))

    rows.extend([
        Row("F_Z_left", 0, 0,
            ((3, "X|UW", 3, F(1)), (3, "X|UW", 2, F(-1)))),
        Row("F_Z_right_minus_left", 0, 0,
            ((3, "V|W", 3, F(1)), (3, "V|W", 2, F(-1)),
             (3, "X|UW", 3, F(-1)), (3, "X|UW", 2, F(1)))),
        Row("F_Y_left", 0, 0,
            ((1, "X|VW", 0, F(1)), (1, "X|VW", 1, F(-1)))),
        Row("F_Y_right_minus_left", 0, 0,
            ((1, "U|W", 0, F(1)), (1, "U|W", 1, F(-1)),
             (1, "X|VW", 0, F(-1)), (1, "X|VW", 1, F(1)))),
    ])
    return rows


def normalized_row_digest(rows: list[Row]) -> str:
    """Digest the same raw path-row signature verified by the dependency."""
    group_name = {1: "a", 2: "b", 3: "c"}
    output_name = {0: "Y", 1: "G", 2: "K", 3: "Z"}
    value = [
        {
            "label": row.label,
            "r1": row.r1,
            "r2": row.r2,
            "terms": sorted(
                [group_name[group], kind, output_name[letter], int(coefficient)]
                for group, kind, letter, coefficient in row.terms
            ),
        }
        for row in sorted(rows, key=lambda item: item.label)
    ]
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(encoded).hexdigest()


def row_signature(row: Row) -> tuple[int, int, tuple[Term, ...]]:
    return row.r1, row.r2, tuple(sorted(row.terms))


Exponent = tuple[int, int, int]


class Poly:
    """Polynomial in three formal nonnegative variables, over Q."""

    def __init__(self, terms: dict[Exponent, F] | int = 0):
        if isinstance(terms, int):
            self.terms = {(0, 0, 0): F(terms)} if terms else {}
        else:
            self.terms = {power: F(value) for power, value in terms.items()
                          if value}

    @classmethod
    def var(cls, coordinate: int) -> "Poly":
        power = [0, 0, 0]
        power[coordinate] = 1
        return cls({tuple(power): F(1)})

    def __add__(self, other: "Poly | int") -> "Poly":
        if isinstance(other, int):
            other = Poly(other)
        terms = self.terms.copy()
        for power, value in other.terms.items():
            terms[power] = terms.get(power, F(0)) + value
            if terms[power] == 0:
                del terms[power]
        return Poly(terms)

    __radd__ = __add__

    def __neg__(self) -> "Poly":
        return Poly({power: -value for power, value in self.terms.items()})

    def __sub__(self, other: "Poly | int") -> "Poly":
        return self + (-other if isinstance(other, Poly) else -Poly(other))

    def __rsub__(self, other: int) -> "Poly":
        return Poly(other) - self

    def __mul__(self, other: "Poly | int | F") -> "Poly":
        if isinstance(other, (int, F)):
            other = Poly({(0, 0, 0): F(other)})
        terms: dict[Exponent, F] = {}
        for left_power, left_value in self.terms.items():
            for right_power, right_value in other.terms.items():
                power = tuple(left_power[i] + right_power[i]
                              for i in range(3))
                terms[power] = terms.get(power, F(0)) + left_value * right_value
        return Poly(terms)

    __rmul__ = __mul__

    def __eq__(self, other: object) -> bool:
        return isinstance(other, Poly) and self.terms == other.terms

    def __hash__(self) -> int:
        return hash(tuple(sorted(self.terms.items())))

    def coefficientwise_nonnegative(self) -> bool:
        return all(value >= 0 for value in self.terms.values())

    def __repr__(self) -> str:
        return f"Poly({self.terms!r})"


ZERO = Poly()


def info_numerator(kind: str, denominator: Poly,
                   block: tuple[Poly, Poly, Poly]) -> Poly:
    """Numerator of a Q0 row term when block entries share denominator."""
    a, u, v = block
    return {
        "W": a,
        "U|W": u,
        "V|W": v,
        "UW": a + u,
        "VW": a + v,
        "X|UW": denominator - a - u,
        "X|VW": denominator - a - v,
    }[kind]


def row_slack_numerator(row: Row, values: tuple[Poly, Poly, Poly, Poly],
                        denominator: Poly,
                        blocks: tuple[tuple[Poly, Poly, Poly], ...],
                        rate_numerator: Poly) -> Poly:
    rhs = ZERO
    for group, kind, letter, coefficient in row.terms:
        rhs += coefficient * values[letter] * info_numerator(
            kind, denominator, blocks[group - 1])
    return rhs - (row.r1 + row.r2) * rate_numerator


def check_box_constraints(denominator: Poly,
                          blocks: tuple[tuple[Poly, Poly, Poly], ...]) -> None:
    for block in blocks:
        a, u, v = block
        for numerator in (a, u, v, denominator - a - u,
                          denominator - a - v):
            assert numerator.coefficientwise_nonnegative(), numerator


def check_case(name: str, rows: list[Row],
               values: tuple[Poly, Poly, Poly, Poly], denominator: Poly,
               blocks: tuple[tuple[Poly, Poly, Poly], ...],
               rate_numerator: Poly, expected_slacks: set[Poly]) -> None:
    check_box_constraints(denominator, blocks)
    actual: set[Poly] = set()
    for row in rows:
        slack = row_slack_numerator(
            row, values, denominator, blocks, rate_numerator)
        assert slack.coefficientwise_nonnegative(), (name, row.label, slack)
        actual.add(slack)
    assert actual == expected_slacks, (name, actual, expected_slacks)
    print(f"PASS {name}: all 30 row slacks and all 15 box slacks are nonnegative")


Linear = dict[str, F]


def add_linear(dst: Linear, src: Linear, scale: F) -> None:
    for key, value in src.items():
        dst[key] = dst.get(key, F(0)) + scale * value
        if dst[key] == 0:
            del dst[key]


def common_curve_factor(group: int, kind: str) -> Linear:
    """Formal multiplier of a common curve value for one generic block."""
    a, u, v = f"A{group}", f"U{group}", f"V{group}"
    return {
        "W": {a: F(1)},
        "U|W": {u: F(1)},
        "V|W": {v: F(1)},
        "UW": {a: F(1), u: F(1)},
        "VW": {a: F(1), v: F(1)},
        "X|UW": {"1": F(1), a: F(-1), u: F(-1)},
        "X|VW": {"1": F(1), a: F(-1), v: F(-1)},
    }[kind]


def main() -> None:
    root = Path(__file__).resolve().parent
    claim_manifest = json.loads((root / "claims.json").read_text(encoding="utf-8"))
    claims = claim_manifest.get("claims")
    assert claim_manifest.get("schemaVersion") == 1
    assert isinstance(claims, list) and len(claims) == 1
    assert claims[0].get("claimKey") == (
        "bssc-sum-capacity/finite-grid-q0-foundations"
    )
    assert claims[0].get("dependencyTransactionIds") == [FOUNDATION_TRANSACTION]
    print(f"PASS sole logical dependency: {FOUNDATION_TRANSACTION}")

    rows = make_rows()
    expected_labels = (
        "SL(1,U) SR(1,U) SR(1,C) SL(2,U) SR(2,U) SL(3,U) SR(3,U) "
        "SL(3,C) R1T(0) R1T(1) R1T(2) R1A(0) R1A(1) R1A(2) "
        "R2T(0) R2T(1) R2T(2) R2A(0) R2A(1) R2A(2) "
        "N_Y(0) N_Y(1) N_Y(2) N_Z(0) N_Z(1) N_Z(2) "
        "F_Z_left F_Z_right_minus_left F_Y_left F_Y_right_minus_left"
    ).split()
    assert len(rows) == 30
    assert [row.label for row in rows] == expected_labels
    row_digest = normalized_row_digest(rows)
    assert row_digest == EXPECTED_FOUNDATION_ROW_SHA256, row_digest
    print(
        f"PASS foundation rows: {FOUNDATION_TRANSACTION}, "
        f"sha256:{row_digest}"
    )
    signatures = Counter(row_signature(row) for row in rows)
    mirrored_signatures = Counter(
        row_signature(Row("", row.r2, row.r1, mirror_terms(row.terms)))
        for row in rows
    )
    assert signatures == mirrored_signatures
    print("PASS skew symmetry: G/K, Y/Z, group order, U/V, and R1/R2")

    # H: formal variables are (c,p,y), with x=c+p.  All are nonnegative.
    c, p, y = (Poly.var(i) for i in range(3))
    x = c + p
    denominator = c + x
    high_blocks = ((x, ZERO, c), (x, c, ZERO), (x, c, ZERO))
    check_case(
        "H", rows, (c, x, y, c), denominator, high_blocks, c * x,
        {ZERO, c * x})

    # L: variables are (x,p,q), with y=x+p and c=y+q.
    x, p, q = (Poly.var(i) for i in range(3))
    y = x + p
    c = y + q
    denominator = c + x
    low_blocks = ((x, c, ZERO), (x, ZERO, c), (x, ZERO, c))
    check_case(
        "L", rows, (c, x, y, c), denominator, low_blocks, c * c,
        {ZERO, x * c, c * q, c * (p + q)})

    # X: variables are (x,p,q), with c=x+p, y=c+q and Delta=p+q.
    x, p, q = (Poly.var(i) for i in range(3))
    c = x + p
    y = c + q
    delta = p + q
    denominator = (c + x) * delta
    a = x * delta
    b = c * delta
    middle_a = x * p + x * q + p * q
    middle_v = c * p
    cross_blocks = ((a, b, ZERO), (middle_a, ZERO, middle_v),
                    (b, a, ZERO))
    cross_slacks = {
        ZERO,
        x * q * delta,
        x * c * delta,
        x * p * q,
        delta * (c * c + x * q),
        x * p * y,
        x * (c * delta + p * q),
        c * c * delta,
        p * c * delta,
    }
    check_case(
        "X", rows, (c, x, y, c), denominator, cross_blocks,
        c * c * delta, cross_slacks)

    # For the matching construction all four sampled receiver curves are
    # identical.  The SL(1,U) row is then exactly c for every Q0 hierarchy.
    upper_row = next(row for row in rows if row.label == "SL(1,U)")
    polynomial: Linear = {}
    for group, kind, _letter, coeff in upper_row.terms:
        add_linear(polynomial, common_curve_factor(group, kind), coeff)
    assert polynomial == {"1": F(1)}, polynomial

    print("PASS upper: SL(1,U) is identically c when all four Q0 curves agree")
    print("PASS: exact finite-grid Q0 coercivity certificate complete")


if __name__ == "__main__":
    main()
