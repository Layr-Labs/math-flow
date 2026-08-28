#!/usr/bin/env python3
"""Exact premise-to-specialization audit for the private-message GK bound.

The claimed checker has two deliberately independent constructions:

1. ``theorem9_spec.json`` is the explicit cited Theorem 9 premise encoded
   term by term.
2. ``make_path_rows`` constructs the local L=3 rows from generic path formulas.

The premise's minima are expanded after setting R0=0, and the two interval
side conditions are split into four nonnegative slacks.  The independent
constructions are normalized only with I(U,W;A)=I(W;A)+I(U;A|W) and its V
analogue, then compared exactly.  The output-term audit independently checks
the input-only product-marginal reduction.  No PDF, renderer, optimizer,
third-party package, or network request is used.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


GROUPS = ("a", "b", "c")
KINDS = ("W", "U|W", "V|W", "UW", "VW", "X|UW", "X|VW")
OUTPUTS = ("Y", "G", "K", "Z")
MIRROR_KIND = {
    "W": "W",
    "U|W": "V|W",
    "V|W": "U|W",
    "UW": "VW",
    "VW": "UW",
    "X|UW": "X|VW",
    "X|VW": "X|UW",
}

# These sets are an independent audit of the distinct output-bearing terms in
# (19a)-(19p) and the two side conditions.  They are intentionally not read
# from theorem9_spec.json.
EXPECTED_TERM_AUDIT = {
    "Y": {"a:W", "a:U|W", "a:X|VW"},
    "Z": {"c:W", "c:V|W", "c:X|UW"},
    "G": {
        "a:W", "b:W", "a:UW", "b:UW", "a:VW", "b:VW",
        "a:U|W", "b:U|W", "b:V|W", "a:X|UW", "a:X|VW",
        "b:X|VW",
    },
    "K": {
        "b:W", "c:W", "b:UW", "c:UW", "b:VW", "c:VW",
        "b:U|W", "b:V|W", "c:V|W", "b:X|UW", "c:X|UW",
        "c:X|VW",
    },
}
Atom = tuple[str, str, str]  # group, kind, output
RawTerm = tuple[int, str, str, str]
Linear = dict[Atom, int]


@dataclass(frozen=True)
class Row:
    label: str
    r1: int
    r2: int
    terms: tuple[RawTerm, ...]


def term(coefficient: int, group: str, kind: str, output: str) -> RawTerm:
    return coefficient, group, kind, output


def add_coefficient(result: Linear, atom: Atom, coefficient: int) -> None:
    result[atom] = result.get(atom, 0) + coefficient
    if result[atom] == 0:
        del result[atom]


def normalize_terms(terms: Iterable[RawTerm]) -> Linear:
    """Normalize solely by expanding UW and VW with the chain rule."""
    result: Linear = {}
    for coefficient, group, kind, output in terms:
        if (
            not isinstance(coefficient, int)
            or coefficient == 0
            or group not in GROUPS
            or kind not in KINDS
            or output not in OUTPUTS
        ):
            raise AssertionError((coefficient, group, kind, output))
        if kind == "UW":
            add_coefficient(result, (group, "W", output), coefficient)
            add_coefficient(result, (group, "U|W", output), coefficient)
        elif kind == "VW":
            add_coefficient(result, (group, "W", output), coefficient)
            add_coefficient(result, (group, "V|W", output), coefficient)
        else:
            add_coefficient(result, (group, kind, output), coefficient)
    return result


def as_raw_terms(value: object) -> tuple[RawTerm, ...]:
    if not isinstance(value, list):
        raise AssertionError("term list must be an array")
    result: list[RawTerm] = []
    for item in value:
        if not isinstance(item, list) or len(item) != 4:
            raise AssertionError(f"invalid encoded term: {item!r}")
        coefficient, group, kind, output = item
        if not all(isinstance(x, str) for x in (group, kind, output)):
            raise AssertionError(f"invalid encoded term: {item!r}")
        result.append(term(coefficient, group, kind, output))
    normalize_terms(result)
    return tuple(result)


def mirror_terms(terms: tuple[RawTerm, ...]) -> tuple[RawTerm, ...]:
    group_mirror = {"a": "c", "b": "b", "c": "a"}
    output_mirror = {"Y": "Z", "G": "K", "K": "G", "Z": "Y"}
    return tuple(
        term(
            coefficient,
            group_mirror[group],
            MIRROR_KIND[kind],
            output_mirror[output],
        )
        for coefficient, group, kind, output in terms
    )


def make_path_rows() -> list[Row]:
    """Construct the L=3 private-message rows from generic path formulas."""
    rows: list[Row] = []
    length = 3

    def group(index: int) -> str:
        return GROUPS[index - 1]

    def output(index: int) -> str:
        return OUTPUTS[index]

    for middle in range(1, length + 1):
        u_walk = tuple(
            entry
            for index in range(1, middle)
            for entry in (
                term(1, group(index), "UW", output(index - 1)),
                term(-1, group(index), "UW", output(index)),
            )
        )
        uc_walk = tuple(
            entry
            for index in range(1, middle)
            for entry in (
                term(1, group(index), "U|W", output(index - 1)),
                term(-1, group(index), "U|W", output(index)),
            )
        )
        vc_walk = tuple(
            entry
            for index in range(middle + 1, length + 1)
            for entry in (
                term(1, group(index), "V|W", output(index)),
                term(-1, group(index), "V|W", output(index - 1)),
            )
        )
        v_walk = tuple(
            entry
            for index in range(middle + 1, length + 1)
            for entry in (
                term(1, group(index), "VW", output(index)),
                term(-1, group(index), "VW", output(index - 1)),
            )
        )
        rows.append(
            Row(
                f"SL({middle},U)",
                1,
                1,
                u_walk
                + (
                    term(1, group(middle), "UW", output(middle - 1)),
                    term(1, group(middle), "X|UW", output(middle)),
                )
                + vc_walk,
            )
        )
        rows.append(
            Row(
                f"SR({middle},U)",
                1,
                1,
                v_walk
                + (
                    term(1, group(middle), "VW", output(middle)),
                    term(1, group(middle), "X|VW", output(middle - 1)),
                )
                + uc_walk,
            )
        )
        if middle == length:
            rows.append(
                Row(
                    f"SL({middle},C)",
                    1,
                    1,
                    uc_walk
                    + (
                        term(1, group(middle), "U|W", output(middle - 1)),
                        term(1, group(middle), "X|UW", output(middle)),
                        term(1, group(middle), "W", output(middle)),
                    )
                    + vc_walk,
                )
            )
        if middle == 1:
            rows.append(
                Row(
                    f"SR({middle},C)",
                    1,
                    1,
                    vc_walk
                    + (
                        term(1, group(middle), "V|W", output(middle)),
                        term(1, group(middle), "X|VW", output(middle - 1)),
                        term(1, group(middle), "W", output(middle - 1)),
                    )
                    + uc_walk,
                )
            )

    r1_rows: list[Row] = []
    for stop in range(length):
        terms = tuple(
            entry
            for index in range(1, stop + 1)
            for entry in (
                term(1, group(index), "UW", output(index - 1)),
                term(-1, group(index), "UW", output(index)),
            )
        ) + (term(1, group(stop + 1), "UW", output(stop)),)
        r1_rows.append(Row(f"R1T({stop})", 1, 0, terms))
    for stop in range(length):
        terms = tuple(
            entry
            for index in range(1, stop + 1)
            for entry in (
                term(1, group(index), "U|W", output(index - 1)),
                term(-1, group(index), "U|W", output(index)),
            )
        ) + (term(1, group(stop + 1), "U|W", output(stop)),) + tuple(
            entry
            for index in range(stop + 1, length)
            for entry in (
                term(1, group(index), "W", output(index)),
                term(-1, group(index + 1), "W", output(index)),
            )
        ) + (term(1, group(length), "W", output(length)),)
        r1_rows.append(Row(f"R1A({stop})", 1, 0, terms))
    rows.extend(r1_rows)
    rows.extend(
        Row("R2" + row.label[2:], 0, 1, mirror_terms(row.terms))
        for row in r1_rows
    )

    nonnegative_y: list[Row] = []
    for stop in range(length):
        terms = (term(1, "a", "W", "Y"),) + tuple(
            entry
            for index in range(1, stop + 1)
            for entry in (
                term(1, group(index + 1), "W", output(index)),
                term(-1, group(index), "W", output(index)),
            )
        )
        nonnegative_y.append(Row(f"N_Y({stop})", 0, 0, terms))
    rows.extend(nonnegative_y)
    rows.extend(
        Row(f"N_Z({stop})", 0, 0, mirror_terms(row.terms))
        for stop, row in enumerate(nonnegative_y)
    )

    rows.extend(
        [
            Row(
                "F_Z_left",
                0,
                0,
                (term(1, "c", "X|UW", "Z"), term(-1, "c", "X|UW", "K")),
            ),
            Row(
                "F_Z_right_minus_left",
                0,
                0,
                (
                    term(1, "c", "V|W", "Z"),
                    term(-1, "c", "V|W", "K"),
                    term(-1, "c", "X|UW", "Z"),
                    term(1, "c", "X|UW", "K"),
                ),
            ),
            Row(
                "F_Y_left",
                0,
                0,
                (term(1, "a", "X|VW", "Y"), term(-1, "a", "X|VW", "G")),
            ),
            Row(
                "F_Y_right_minus_left",
                0,
                0,
                (
                    term(1, "a", "U|W", "Y"),
                    term(-1, "a", "U|W", "G"),
                    term(-1, "a", "X|VW", "Y"),
                    term(1, "a", "X|VW", "G"),
                ),
            ),
        ]
    )
    return rows


def load_source_rows(spec: dict[str, object]) -> tuple[dict[str, Row], dict[str, str]]:
    rows: dict[str, Row] = {}
    origins: dict[str, str] = {}
    labels_seen: list[str] = []
    raw_terms: list[RawTerm] = []

    constraints = spec.get("constraints")
    if not isinstance(constraints, list) or len(constraints) != 12:
        raise AssertionError("expected the 12 substantive Theorem 9 constraints")
    for constraint in constraints:
        if not isinstance(constraint, dict):
            raise AssertionError("constraint must be an object")
        source_labels = constraint.get("sourceLabels")
        rates = constraint.get("rateCoefficients")
        branches = constraint.get("branches")
        if (
            not isinstance(source_labels, list)
            or not all(isinstance(item, str) for item in source_labels)
            or not isinstance(rates, list)
            or rates not in ([0, 0], [1, 0], [0, 1], [1, 1])
            or not isinstance(branches, list)
            or not branches
        ):
            raise AssertionError(f"invalid constraint envelope: {constraint!r}")
        labels_seen.extend(source_labels)
        base = as_raw_terms(constraint.get("base"))
        raw_terms.extend(base)
        for branch_index, branch in enumerate(branches):
            if not isinstance(branch, dict) or set(branch) != {"row", "terms"}:
                raise AssertionError(f"invalid minimum branch: {branch!r}")
            label = branch["row"]
            if not isinstance(label, str) or label in rows:
                raise AssertionError(f"duplicate or invalid row label: {label!r}")
            branch_terms = as_raw_terms(branch["terms"])
            raw_terms.extend(branch_terms)
            rows[label] = Row(label, rates[0], rates[1], base + branch_terms)
            source_text = ",".join(source_labels)
            origins[label] = f"({source_text}) branch {branch_index}"

    expected_labels = [f"19{chr(ord('a') + index)}" for index in range(16)]
    if labels_seen != expected_labels:
        raise AssertionError((labels_seen, expected_labels))

    side_conditions = spec.get("sideConditions")
    if not isinstance(side_conditions, list) or len(side_conditions) != 2:
        raise AssertionError("expected exactly two side conditions")
    for side in side_conditions:
        if not isinstance(side, dict):
            raise AssertionError("side condition must be an object")
        name = side.get("name")
        left = as_raw_terms(side.get("left"))
        right = as_raw_terms(side.get("right"))
        raw_terms.extend(left)
        raw_terms.extend(right)
        side_rows = side.get("rows")
        if not isinstance(name, str) or not isinstance(side_rows, list):
            raise AssertionError("invalid side condition envelope")
        for side_row in side_rows:
            if not isinstance(side_row, dict) or set(side_row) != {"row", "operation"}:
                raise AssertionError(f"invalid side row: {side_row!r}")
            label = side_row["row"]
            operation = side_row["operation"]
            if not isinstance(label, str) or label in rows:
                raise AssertionError(f"duplicate or invalid row label: {label!r}")
            if operation == "left":
                terms = left
            elif operation == "right-minus-left":
                terms = right + tuple(
                    term(-coefficient, group, kind, output)
                    for coefficient, group, kind, output in left
                )
            else:
                raise AssertionError(f"invalid side operation: {operation!r}")
            rows[label] = Row(label, 0, 0, terms)
            origins[label] = f"{name}: {operation}"

    audit = {output: set() for output in OUTPUTS}
    for _coefficient, group, kind, output in raw_terms:
        audit[output].add(f"{group}:{kind}")
    if audit != EXPECTED_TERM_AUDIT:
        raise AssertionError((audit, EXPECTED_TERM_AUDIT))
    return rows, origins


def main() -> None:
    root = Path(__file__).resolve().parent
    spec = json.loads((root / "theorem9_spec.json").read_text(encoding="utf-8"))
    if spec.get("schemaVersion") != 1:
        raise AssertionError("unsupported theorem specification version")
    source = spec.get("source")
    if not isinstance(source, dict):
        raise AssertionError("missing source metadata")
    premise_boundary = (
        "The factorization, equations (19a)-(19p), and both side conditions "
        "encoded here are the explicit cited Theorem 9 premise; their source "
        "fidelity and bibliographic provenance are not verifier results."
    )
    if source.get("premiseBoundary") != premise_boundary:
        raise AssertionError("unexpected mathematical-premise boundary")
    expected_factorization = {
        "variables": [
            "Ua", "Va", "Wa", "Ub", "Vb", "Wb", "Uc", "Vc", "Wc",
            "X", "Y", "Z", "G", "K",
        ],
        "factors": [
            "pX", "pUa,Va,Wa|X", "pUb,Vb,Wb|X", "pUc,Vc,Wc|X",
            "TY,Z|X", "TG,K|X,Y,Z",
        ],
    }
    if spec.get("factorization") != expected_factorization:
        raise AssertionError("unexpected cited-premise factorization")
    if spec.get("privateMessageSpecialization") != "R0=0":
        raise AssertionError("unexpected private-message specialization")
    constraints = spec.get("constraints")
    if not isinstance(constraints, list):
        raise AssertionError("premise constraints must be an array")
    labels: list[str] = []
    for constraint in constraints:
        if not isinstance(constraint, dict):
            raise AssertionError("premise constraint must be an object")
        raw_labels = constraint.get("sourceLabels")
        if not isinstance(raw_labels, list) or not all(
            isinstance(label, str) for label in raw_labels
        ):
            raise AssertionError("invalid premise source labels")
        labels.extend(raw_labels)
    expected_labels = [f"19{letter}" for letter in "abcdefghijklmnop"]
    if labels != expected_labels:
        raise AssertionError("premise does not encode exactly equations (19a)-(19p)")
    side_conditions = spec.get("sideConditions")
    if not isinstance(side_conditions, list) or len(side_conditions) != 2:
        raise AssertionError("premise does not encode exactly two side conditions")
    print("PASS explicit cited premise structure: factorization, 16 equations, 2 side conditions")

    source_rows, origins = load_source_rows(spec)
    path_rows_list = make_path_rows()
    if len(path_rows_list) != 30:
        raise AssertionError(f"path construction produced {len(path_rows_list)} rows")
    path_rows = {row.label: row for row in path_rows_list}
    if len(path_rows) != 30:
        raise AssertionError("path construction contains duplicate labels")
    if set(source_rows) != set(path_rows):
        raise AssertionError(
            f"row-label mismatch: source-only={sorted(set(source_rows)-set(path_rows))}, "
            f"path-only={sorted(set(path_rows)-set(source_rows))}"
        )

    for label, source_row in source_rows.items():
        path_row = path_rows[label]
        source_value = (source_row.r1, source_row.r2, normalize_terms(source_row.terms))
        path_value = (path_row.r1, path_row.r2, normalize_terms(path_row.terms))
        if source_value != path_value:
            raise AssertionError(
                f"{label} mismatch\nsource={source_value!r}\npath={path_value!r}"
            )
        print(f"PASS {origins[label]} -> {label}")

    counts = {output: len(EXPECTED_TERM_AUDIT[output]) for output in OUTPUTS}
    print(f"PASS exhaustive single-output term audit: {counts}")
    print(
        "PASS: cited-premise R0=0 expansion and all 30 independently generated "
        "private-message rows agree exactly"
    )


if __name__ == "__main__":
    main()
