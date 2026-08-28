#!/usr/bin/env python3
"""Exact combinatorial audit for receiver-curve row stability.

This checker independently rebuilds the generic length-three path rows accepted
in dependency e3c1036ca607539a5ebcddf3058e6014ac5c1cd9.  It checks the
reviewed curve-error coefficient table and elementary uniform-grid formulas.
It does not prove the analytic entropy or compactness arguments in README.md.
"""

from __future__ import annotations

import json
from fractions import Fraction
from pathlib import Path


GROUPS = ("a", "b", "c")
OUTPUTS = ("Y", "G", "K", "Z")
MIRROR_KIND = {
    "W": "W", "U|W": "V|W", "V|W": "U|W", "UW": "VW",
    "VW": "UW", "X|UW": "X|VW", "X|VW": "X|UW",
}
TERM_WEIGHT = {
    "W": 2, "U|W": 2, "V|W": 2, "UW": 2, "VW": 2,
    "X|UW": 1, "X|VW": 1,
}
EXPECTED_DEPENDENCIES = [
    "e3c1036ca607539a5ebcddf3058e6014ac5c1cd9",
    "e2bbc1e210e496b3c834e658820fc90287f3b2c0",
]
EXPECTED = {
    "F_Y_left": (1, 0), "F_Y_right_minus_left": (3, 0),
    "F_Z_left": (0, 1), "F_Z_right_minus_left": (0, 3),
    "N_Y(0)": (0, 0), "N_Y(1)": (4, 0), "N_Y(2)": (4, 4),
    "N_Z(0)": (0, 0), "N_Z(1)": (0, 4), "N_Z(2)": (4, 4),
    "R1A(0)": (4, 4), "R1A(1)": (4, 4), "R1A(2)": (4, 4),
    "R1T(0)": (0, 0), "R1T(1)": (4, 0), "R1T(2)": (4, 4),
    "R2A(0)": (4, 4), "R2A(1)": (4, 4), "R2A(2)": (4, 4),
    "R2T(0)": (0, 0), "R2T(1)": (0, 4), "R2T(2)": (4, 4),
    "SL(1,U)": (3, 4), "SL(2,U)": (4, 3),
    "SL(3,C)": (4, 4), "SL(3,U)": (4, 4),
    "SR(1,C)": (4, 4), "SR(1,U)": (4, 4),
    "SR(2,U)": (3, 4), "SR(3,U)": (4, 3),
}

Term = tuple[int, str, str, str]
Row = tuple[str, int, int, tuple[Term, ...]]


def term(coefficient: int, group: str, kind: str, output: str) -> Term:
    return coefficient, group, kind, output


def mirror(terms: tuple[Term, ...]) -> tuple[Term, ...]:
    group_mirror = {"a": "c", "b": "b", "c": "a"}
    output_mirror = {"Y": "Z", "G": "K", "K": "G", "Z": "Y"}
    return tuple(
        term(c, group_mirror[g], MIRROR_KIND[k], output_mirror[o])
        for c, g, k, o in terms
    )


def make_rows() -> list[Row]:
    rows: list[Row] = []
    length = 3

    def group(index: int) -> str:
        return GROUPS[index - 1]

    def output(index: int) -> str:
        return OUTPUTS[index]

    for middle in range(1, length + 1):
        u_walk = tuple(
            entry for index in range(1, middle) for entry in (
                term(1, group(index), "UW", output(index - 1)),
                term(-1, group(index), "UW", output(index)),
            )
        )
        uc_walk = tuple(
            entry for index in range(1, middle) for entry in (
                term(1, group(index), "U|W", output(index - 1)),
                term(-1, group(index), "U|W", output(index)),
            )
        )
        vc_walk = tuple(
            entry for index in range(middle + 1, length + 1) for entry in (
                term(1, group(index), "V|W", output(index)),
                term(-1, group(index), "V|W", output(index - 1)),
            )
        )
        v_walk = tuple(
            entry for index in range(middle + 1, length + 1) for entry in (
                term(1, group(index), "VW", output(index)),
                term(-1, group(index), "VW", output(index - 1)),
            )
        )
        rows.append((
            f"SL({middle},U)", 1, 1,
            u_walk + (
                term(1, group(middle), "UW", output(middle - 1)),
                term(1, group(middle), "X|UW", output(middle)),
            ) + vc_walk,
        ))
        rows.append((
            f"SR({middle},U)", 1, 1,
            v_walk + (
                term(1, group(middle), "VW", output(middle)),
                term(1, group(middle), "X|VW", output(middle - 1)),
            ) + uc_walk,
        ))
        if middle == length:
            rows.append((
                f"SL({middle},C)", 1, 1,
                uc_walk + (
                    term(1, group(middle), "U|W", output(middle - 1)),
                    term(1, group(middle), "X|UW", output(middle)),
                    term(1, group(middle), "W", output(middle)),
                ) + vc_walk,
            ))
        if middle == 1:
            rows.append((
                f"SR({middle},C)", 1, 1,
                vc_walk + (
                    term(1, group(middle), "V|W", output(middle)),
                    term(1, group(middle), "X|VW", output(middle - 1)),
                    term(1, group(middle), "W", output(middle - 1)),
                ) + uc_walk,
            ))

    r1_rows: list[Row] = []
    for stop in range(length):
        terms = tuple(
            entry for index in range(1, stop + 1) for entry in (
                term(1, group(index), "UW", output(index - 1)),
                term(-1, group(index), "UW", output(index)),
            )
        ) + (term(1, group(stop + 1), "UW", output(stop)),)
        r1_rows.append((f"R1T({stop})", 1, 0, terms))
    for stop in range(length):
        terms = tuple(
            entry for index in range(1, stop + 1) for entry in (
                term(1, group(index), "U|W", output(index - 1)),
                term(-1, group(index), "U|W", output(index)),
            )
        ) + (term(1, group(stop + 1), "U|W", output(stop)),) + tuple(
            entry for index in range(stop + 1, length) for entry in (
                term(1, group(index), "W", output(index)),
                term(-1, group(index + 1), "W", output(index)),
            )
        ) + (term(1, group(length), "W", output(length)),)
        r1_rows.append((f"R1A({stop})", 1, 0, terms))
    rows.extend(r1_rows)
    rows.extend(("R2" + label[2:], 0, 1, mirror(terms)) for label, _, _, terms in r1_rows)

    nonnegative_y: list[Row] = []
    for stop in range(length):
        terms = (term(1, "a", "W", "Y"),) + tuple(
            entry for index in range(1, stop + 1) for entry in (
                term(1, group(index + 1), "W", output(index)),
                term(-1, group(index), "W", output(index)),
            )
        )
        nonnegative_y.append((f"N_Y({stop})", 0, 0, terms))
    rows.extend(nonnegative_y)
    rows.extend((f"N_Z({stop})", 0, 0, mirror(row[3])) for stop, row in enumerate(nonnegative_y))

    rows.extend([
        ("F_Z_left", 0, 0, (
            term(1, "c", "X|UW", "Z"), term(-1, "c", "X|UW", "K"))),
        ("F_Z_right_minus_left", 0, 0, (
            term(1, "c", "V|W", "Z"), term(-1, "c", "V|W", "K"),
            term(-1, "c", "X|UW", "Z"), term(1, "c", "X|UW", "K"))),
        ("F_Y_left", 0, 0, (
            term(1, "a", "X|VW", "Y"), term(-1, "a", "X|VW", "G"))),
        ("F_Y_right_minus_left", 0, 0, (
            term(1, "a", "U|W", "Y"), term(-1, "a", "U|W", "G"),
            term(-1, "a", "X|VW", "Y"), term(1, "a", "X|VW", "G"))),
    ])
    return rows


def row_bound(terms: tuple[Term, ...]) -> tuple[int, int]:
    combined: dict[tuple[str, str, str], int] = {}
    for coefficient, group, kind, output in terms:
        atom = group, kind, output
        combined[atom] = combined.get(atom, 0) + coefficient
    result = {"G": 0, "K": 0}
    for (_, kind, output), coefficient in combined.items():
        if output in result:
            result[output] += abs(coefficient) * TERM_WEIGHT[kind]
    return result["G"], result["K"]


def check_claims() -> None:
    data = json.loads(Path("claims.json").read_text(encoding="utf-8"))
    claims = data.get("claims")
    if data.get("schemaVersion") != 1 or not isinstance(claims, list) or len(claims) != 1:
        raise AssertionError("claims.json must contain exactly one schema-v1 claim")
    if claims[0].get("dependencyTransactionIds") != EXPECTED_DEPENDENCIES:
        raise AssertionError("unexpected dependency transaction list or order")
    print("PASS: exact canonical dependencies")


def check_rows() -> None:
    rows = make_rows()
    labels = [row[0] for row in rows]
    if len(rows) != 30 or len(set(labels)) != 30 or set(labels) != set(EXPECTED):
        raise AssertionError("generic path generator did not produce the exact 30 labels")
    for label, _, _, terms in rows:
        actual = row_bound(terms)
        if actual != EXPECTED[label]:
            raise AssertionError(f"{label}: expected {EXPECTED[label]}, got {actual}")
        if actual[0] > 4 or actual[1] > 4:
            raise AssertionError(f"{label}: global coefficient bound failed")
        print(f"PASS {label}: (a_r,b_r)={actual}")
    print("PASS: all 30 rowwise bounds and the global (4,4) bound")


def check_uniform_grids() -> None:
    for m in range(1, 257):
        grid = [Fraction(j, 2 * m) for j in range(2 * m + 1)]
        if len(grid) != 2 * m + 1 or grid[0] != 0 or grid[-1] != 1:
            raise AssertionError("uniform grid support formula failed")
        if Fraction(1, 2) not in grid or grid != [1 - q for q in reversed(grid)]:
            raise AssertionError("uniform grid midpoint/reflection property failed")
        mesh_radius = max((grid[j + 1] - grid[j]) / 2 for j in range(len(grid) - 1))
        if mesh_radius != Fraction(1, 4 * m):
            raise AssertionError("uniform grid mesh-radius formula failed")
    print("PASS: Q_M has 2M+1 points, is reflected, and has mesh radius 1/(4M)")


def main() -> None:
    check_claims()
    check_rows()
    check_uniform_grids()
    print("PASS: uniform receiver-curve continuum-bridge mechanical audit")


if __name__ == "__main__":
    main()
