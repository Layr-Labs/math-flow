from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any


EXPECTED_KEYS = {
    "schemaVersion",
    "n",
    "colorCount",
    "encoding",
    "symmetryModulus",
    "pairedClasses",
    "specialAssignments",
}


def exact_int(value: Any, label: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise ValueError(f"{label} must be an integer")
    return value


def assign(colors: dict[int, int], value: int, color: int, source: str) -> None:
    if value in colors:
        raise ValueError(f"integer {value} assigned more than once ({source})")
    colors[value] = color


def expand_symmetric(path: Path) -> tuple[int, int, dict[int, int]]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict) or set(data) != EXPECTED_KEYS:
        raise ValueError("symmetric witness has unexpected or missing fields")
    if exact_int(data["schemaVersion"], "schemaVersion") != 1:
        raise ValueError("unsupported schemaVersion")
    n = exact_int(data["n"], "n")
    color_count = exact_int(data["colorCount"], "colorCount")
    modulus = exact_int(data["symmetryModulus"], "symmetryModulus")
    if (n, color_count, modulus) != (536, 6, 537):
        raise ValueError("expected n=536, six colors, and symmetry modulus 537")
    if data["encoding"] != "symmetric-representatives-v1":
        raise ValueError("unsupported symmetric encoding")

    classes = data["pairedClasses"]
    if not isinstance(classes, list) or len(classes) != color_count:
        raise ValueError("pairedClasses must contain exactly six class lists")

    colors: dict[int, int] = {}
    for color, representatives in enumerate(classes, start=1):
        if not isinstance(representatives, list) or not representatives:
            raise ValueError(f"paired class {color} must be a nonempty list")
        if representatives != sorted(representatives):
            raise ValueError(f"paired class {color} is not in canonical order")
        for index, raw in enumerate(representatives):
            value = exact_int(raw, f"pairedClasses[{color - 1}][{index}]")
            complement = modulus - value
            if not (1 <= value < complement <= n):
                raise ValueError(f"{value} is not the smaller member of a valid pair")
            assign(colors, value, color, "paired representative")
            assign(colors, complement, color, "paired complement")

    specials = data["specialAssignments"]
    if not isinstance(specials, list) or specials != sorted(specials):
        raise ValueError("specialAssignments must be a canonically sorted list")
    for index, pair in enumerate(specials):
        if not isinstance(pair, list) or len(pair) != 2:
            raise ValueError(f"specialAssignments[{index}] must be [integer, color]")
        value = exact_int(pair[0], f"specialAssignments[{index}][0]")
        color = exact_int(pair[1], f"specialAssignments[{index}][1]")
        if not (1 <= value <= n and 1 <= color <= color_count):
            raise ValueError("special assignment is outside the valid range")
        assign(colors, value, color, "special assignment")

    expected_domain = set(range(1, n + 1))
    if set(colors) != expected_domain:
        missing = sorted(expected_domain - set(colors))
        extra = sorted(set(colors) - expected_domain)
        raise ValueError(
            f"expanded witness is not a partition; missing={missing}, extra={extra}"
        )
    return n, color_count, colors


def read_canonical_csv(path: Path, n: int, color_count: int) -> dict[int, int]:
    with path.open(newline="", encoding="ascii") as stream:
        rows = list(csv.reader(stream))
    if not rows or rows[0] != ["integer", "color"]:
        raise ValueError("CSV header must be exactly integer,color")
    if len(rows) != n + 1:
        raise ValueError(f"CSV must have exactly {n} data rows")

    colors: dict[int, int] = {}
    for expected_integer, row in enumerate(rows[1:], start=1):
        if len(row) != 2 or not all(
            field.isascii() and field.isdecimal() for field in row
        ):
            raise ValueError(f"malformed CSV row {expected_integer + 1}")
        value, color = map(int, row)
        if row != [str(value), str(color)]:
            raise ValueError(f"noncanonical decimal at CSV row {expected_integer + 1}")
        if value != expected_integer:
            raise ValueError("CSV integers must appear exactly once in increasing order")
        if not (1 <= color <= color_count):
            raise ValueError(f"color outside 1..{color_count} at integer {value}")
        colors[value] = color
    return colors


def verify_sum_free(n: int, colors: dict[int, int]) -> int:
    checked = 0
    for x in range(1, n + 1):
        for y in range(x, n - x + 1):
            z = x + y
            checked += 1
            if colors[x] == colors[y] == colors[z]:
                raise ValueError(
                    f"monochromatic Schur triple: {x}+{y}={z}, color {colors[x]}"
                )
    return checked


def verify(
    symmetric_path: Path, csv_path: Path
) -> tuple[int, int, list[int], int]:
    n, color_count, expanded = expand_symmetric(symmetric_path)
    canonical = read_canonical_csv(csv_path, n, color_count)
    if canonical != expanded:
        mismatch = next(
            value for value in range(1, n + 1) if canonical[value] != expanded[value]
        )
        raise ValueError(f"CSV disagrees with symmetric source at integer {mismatch}")
    class_sizes = [
        sum(color == expected for color in canonical.values())
        for expected in range(1, color_count + 1)
    ]
    if any(size == 0 for size in class_sizes) or sum(class_sizes) != n:
        raise ValueError("CSV does not encode six nonempty color classes")
    checked = verify_sum_free(n, canonical)
    return n, color_count, class_sizes, checked


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Verify the Fredricksen-Sweet Schur-6 witness"
    )
    parser.add_argument("symmetric_witness", type=Path)
    parser.add_argument("canonical_coloring", type=Path)
    args = parser.parse_args()
    n, color_count, class_sizes, checked = verify(
        args.symmetric_witness, args.canonical_coloring
    )
    sizes = ",".join(map(str, class_sizes))
    print(
        f"verified {color_count}-coloring of 1..{n}: class sizes {sizes}; "
        f"all {checked} in-range x<=y Schur triples are nonmonochromatic"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
