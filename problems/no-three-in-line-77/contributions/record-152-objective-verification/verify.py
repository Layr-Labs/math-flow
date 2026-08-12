from __future__ import annotations

import argparse
import itertools
from pathlib import Path


ALPHABET = (
    "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"
    "#$%&@?!()[]<>{}=*+|-/~^_:;,."
)


def decode(value: str) -> tuple[int, list[tuple[int, int]]]:
    encoded = value.strip()
    if not encoded:
        raise ValueError("configuration is empty")
    if encoded[0] not in ".:/-ocx+*":
        raise ValueError("configuration has no recognized symmetry marker")
    payload = encoded[1:]
    if not payload or len(payload) % 2:
        raise ValueError("configuration payload must contain two columns per row")
    size = len(payload) // 2
    try:
        points = [
            (ALPHABET.index(payload[2 * row + offset]), row)
            for row in range(size)
            for offset in range(2)
        ]
    except ValueError as exc:
        raise ValueError("configuration contains a character outside the alphabet") from exc
    return size, points


def determinant(
    first: tuple[int, int],
    second: tuple[int, int],
    third: tuple[int, int],
) -> int:
    return (second[0] - first[0]) * (third[1] - first[1]) - (
        third[0] - first[0]
    ) * (second[1] - first[1])


def verify(path: Path) -> tuple[int, int]:
    size, points = decode(path.read_text(encoding="utf-8"))
    if len(set(points)) != len(points):
        raise ValueError("configuration contains a duplicate point")
    if any(not (0 <= x < size and 0 <= y < size) for x, y in points):
        raise ValueError("configuration contains a point outside its grid")
    for triple in itertools.combinations(points, 3):
        if determinant(*triple) == 0:
            raise ValueError(f"collinear triple: {triple}")
    return size, len(points)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("configuration", type=Path)
    args = parser.parse_args()
    size, count = verify(args.configuration)
    print(f"verified {count} points on a {size} x {size} grid; no collinear triple")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
