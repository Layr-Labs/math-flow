"""Exact, standard-library verifier for the n=77 rct4 subclass encoding.

This program verifies only the finite constraint system described in README.md.
It makes no solver call and no assertion about whether the n=77 instance is
satisfiable.  The bundled smaller certificates are regression fixtures, not a
claim that every record belongs to this subclass.
"""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
from collections import defaultdict
from functools import lru_cache
from math import gcd
from pathlib import Path
from typing import Iterator


ALPHABET = (
    "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"
    "#$%&@?!()[]<>{}=*+|-/~^_:;,."
)

HERE = Path(__file__).resolve().parent
DEFAULT_CERTIFICATES = HERE / "calibration-certificates.txt"
DEFAULT_RESULTS = HERE / "results.json"

Point = tuple[int, int]
Variable = tuple[str, int]
Constraint = tuple[tuple[Variable, int], ...]


def fail(message: str) -> None:
    raise SystemExit(f"FAILED: {message}")


def rho(point: Point, n: int) -> Point:
    x, y = point
    return y, n - 1 - x


def quarter_turn_orbit(point: Point, n: int) -> tuple[Point, ...]:
    points = [point]
    for _ in range(3):
        points.append(rho(points[-1], n))
    return tuple(sorted(set(points)))


@lru_cache(maxsize=None)
def build_structure(
    n: int,
) -> tuple[
    int,
    frozenset[Point],
    dict[Point, Variable],
    tuple[tuple[Point, ...], ...],
    tuple[tuple[Point, Point], ...],
]:
    """Partition non-anti-diagonal cells into rct4 model variables."""
    if n < 3 or n % 2 == 0:
        fail("the rct4 encoding is defined here only for odd n >= 3")
    m = (n - 1) // 2
    anti = frozenset((i, n - 1 - i) for i in range(n))
    orbit_of: dict[Point, Variable] = {}
    off_orbits: list[tuple[Point, ...]] = []
    seen: set[tuple[Point, ...]] = set()

    for x in range(n):
        for y in range(n):
            cell = (x, y)
            if cell in anti:
                continue
            if x == y:
                orbit_of[cell] = ("diag", min(x, n - 1 - x))
                continue
            orbit = quarter_turn_orbit(cell, n)
            if len(orbit) != 4:
                fail(f"off-diagonal cell {cell} does not have a four-cell orbit")
            if orbit not in seen:
                seen.add(orbit)
                index = len(off_orbits)
                for member in orbit:
                    if member in anti or member[0] == member[1]:
                        fail("off-diagonal orbit crosses a fixed diagonal")
                    orbit_of[member] = ("off", index)
                off_orbits.append(orbit)

    diagonal_pairs = tuple(
        ((i, i), (n - 1 - i, n - 1 - i)) for i in range(m)
    )
    expected_domain = {
        (x, y) for x in range(n) for y in range(n) if (x, y) not in anti
    }
    if set(orbit_of) != expected_domain:
        fail("model variables do not partition the non-anti-diagonal cells")
    if len(off_orbits) != m * m:
        fail(f"expected {m * m} off-diagonal orbits, found {len(off_orbits)}")
    if len(diagonal_pairs) != m:
        fail(f"expected {m} diagonal pairs")
    return m, anti, orbit_of, tuple(off_orbits), diagonal_pairs


def maximal_grid_lines(n: int) -> Iterator[tuple[Point, ...]]:
    """Yield each maximal lattice line in G_n carrying at least three cells.

    Directions are sign-normalized primitive vectors.  A line with three grid
    cells contains two primitive steps, so neither step component can exceed
    (n-1)//2 in absolute value.  Requiring the predecessor of the first cell
    to be outside the grid makes the enumeration unique and maximal.
    """
    max_step = (n - 1) // 2
    directions = [(0, 1), (1, 0)]
    directions.extend(
        (dx, dy)
        for dx in range(1, max_step + 1)
        for dy in range(-max_step, max_step + 1)
        if dy != 0 and gcd(dx, abs(dy)) == 1
    )
    if len(directions) != len(set(directions)):
        fail("primitive direction enumeration contains a duplicate")

    for dx, dy in directions:
        for x in range(n):
            for y in range(n):
                predecessor = (x - dx, y - dy)
                if 0 <= predecessor[0] < n and 0 <= predecessor[1] < n:
                    continue
                cells: list[Point] = []
                cx, cy = x, y
                while 0 <= cx < n and 0 <= cy < n:
                    cells.append((cx, cy))
                    cx += dx
                    cy += dy
                if len(cells) >= 3:
                    yield tuple(cells)


def line_constraints(n: int) -> tuple[Constraint, ...]:
    """Return canonical weighted at-most-two constraints for the subclass."""
    _, anti, orbit_of, _, _ = build_structure(n)
    constraints: set[Constraint] = set()
    for cells in maximal_grid_lines(n):
        weights: dict[Variable, int] = defaultdict(int)
        for cell in cells:
            if cell not in anti:
                weights[orbit_of[cell]] += 1
        terms = tuple(sorted(weights.items()))
        if sum(coefficient for _, coefficient in terms) >= 3:
            constraints.add(terms)
    return tuple(sorted(constraints))


def constraints_digest(constraints: tuple[Constraint, ...]) -> str:
    serializable = [
        [[kind, index, coefficient] for ((kind, index), coefficient) in terms]
        for terms in constraints
    ]
    encoded = json.dumps(serializable, separators=(",", ":"), ensure_ascii=True)
    return "sha256:" + hashlib.sha256(encoded.encode("ascii")).hexdigest()


def model_stats(n: int) -> dict[str, int | str]:
    m, _, _, off_orbits, diagonal_pairs = build_structure(n)
    constraints = line_constraints(n)
    return {
        "n": n,
        "targetPoints": 2 * n,
        "offOrbitVariables": len(off_orbits),
        "diagonalPairVariables": len(diagonal_pairs),
        "chosenOffOrbits": m,
        "chosenDiagonalPairs": 1,
        "lineConstraints": len(constraints),
        "canonicalConstraintDigest": constraints_digest(constraints),
    }


def decode_certificate(raw: str) -> tuple[int, list[Point]]:
    encoded = raw.strip()
    if len(encoded) < 3 or (len(encoded) - 1) % 2:
        fail("certificate must have one marker followed by two cells per row")
    payload = encoded[1:]
    n = len(payload) // 2
    points: list[Point] = []
    for row in range(n):
        for offset in range(2):
            character = payload[2 * row + offset]
            if character not in ALPHABET:
                fail(f"certificate character {character!r} is outside the alphabet")
            points.append((ALPHABET.index(character), row))
    return n, points


def verify_no_three_in_line(points: list[Point], n: int) -> None:
    if len(points) != 2 * n or len(set(points)) != 2 * n:
        fail(f"expected {2 * n} distinct points")
    if any(not (0 <= x < n and 0 <= y < n) for x, y in points):
        fail("certificate contains a point outside the grid")
    for a, b, c in itertools.combinations(points, 3):
        determinant = (b[0] - a[0]) * (c[1] - a[1]) - (
            c[0] - a[0]
        ) * (b[1] - a[1])
        if determinant == 0:
            fail(f"certificate contains collinear triple {a}, {b}, {c}")


def assignment_from_points(
    points: list[Point], n: int
) -> tuple[set[int], set[int]]:
    """Require exact equality with an expanded rct4 Boolean assignment."""
    m, anti, orbit_of, off_orbits, diagonal_pairs = build_structure(n)
    selected = set(points)
    if selected & anti:
        fail("certificate occupies the anti-diagonal")
    off_indices: set[int] = set()
    diagonal_indices: set[int] = set()
    for point in selected:
        kind, index = orbit_of[point]
        if kind == "off":
            off_indices.add(index)
        else:
            diagonal_indices.add(index)
    if len(off_indices) != m or len(diagonal_indices) != 1:
        fail(
            f"unexpected assignment size: {len(off_indices)} off-orbits and "
            f"{len(diagonal_indices)} diagonal pairs"
        )
    expanded: set[Point] = set()
    for index in off_indices:
        expanded.update(off_orbits[index])
    for index in diagonal_indices:
        expanded.update(diagonal_pairs[index])
    if expanded != selected:
        fail("certificate is not exactly the expansion of its rct4 assignment")
    return off_indices, diagonal_indices


def check_certificate(raw: str) -> dict[str, int | str | bool]:
    n, points = decode_certificate(raw)
    verify_no_three_in_line(points, n)
    off_indices, diagonal_indices = assignment_from_points(points, n)
    _, _, _, off_orbits, diagonal_pairs = build_structure(n)
    constraints = line_constraints(n)
    values: dict[Variable, int] = {
        ("off", index): int(index in off_indices)
        for index in range(len(off_orbits))
    }
    values.update(
        {
            ("diag", index): int(index in diagonal_indices)
            for index in range(len(diagonal_pairs))
        }
    )
    for terms in constraints:
        if sum(values[variable] * coefficient for variable, coefficient in terms) > 2:
            fail(f"n={n} certificate violates a weighted line constraint")
    return {
        "n": n,
        "points": len(points),
        "lineSha256": "sha256:"
        + hashlib.sha256(raw.strip().encode("ascii")).hexdigest(),
        "verifiedNoThreeInLine": True,
        "verifiedExactRct4Expansion": True,
        "lineConstraintsChecked": len(constraints),
        "canonicalConstraintDigest": constraints_digest(constraints),
    }


def check_certificates(path: Path) -> list[dict[str, int | str | bool]]:
    reports = []
    for raw in path.read_text(encoding="ascii").splitlines():
        if not raw.strip():
            continue
        report = check_certificate(raw)
        reports.append(report)
        print(
            f"n={report['n']}: {report['points']} points verified; exact rct4 "
            f"expansion satisfies {report['lineConstraintsChecked']} constraints"
        )
    if not reports:
        fail("no calibration certificates found")
    return reports


def build_results(certificates_path: Path) -> dict[str, object]:
    return {
        "schemaVersion": 1,
        "problem": "no-three-in-line-77",
        "instance": "exact rct4-subclass encoding for 154 points in G_77",
        "modelStats": model_stats(77),
        "calibrationCertificates": {
            "role": "regression fixtures only; no historical universality claim",
            "fileSha256": "sha256:"
            + hashlib.sha256(certificates_path.read_bytes()).hexdigest(),
            "checks": check_certificates(certificates_path),
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    subparsers = parser.add_subparsers(dest="command", required=True)
    check = subparsers.add_parser("check-calibrations")
    check.add_argument(
        "--certificates", type=Path, default=DEFAULT_CERTIFICATES
    )
    results = subparsers.add_parser("results")
    results.add_argument(
        "--certificates", type=Path, default=DEFAULT_CERTIFICATES
    )
    results.add_argument("--results", type=Path, default=DEFAULT_RESULTS)
    results.add_argument("--write", action="store_true")
    args = parser.parse_args()

    if args.command == "check-calibrations":
        check_certificates(args.certificates)
        return 0

    value = build_results(args.certificates)
    rendered = json.dumps(value, indent=2, sort_keys=True) + "\n"
    if args.write:
        args.results.write_text(rendered, encoding="ascii")
        print(f"wrote {args.results}")
    elif args.results.read_text(encoding="ascii") != rendered:
        fail("recomputed model results differ from committed results.json")
    else:
        print("results.json verified byte-for-byte")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
