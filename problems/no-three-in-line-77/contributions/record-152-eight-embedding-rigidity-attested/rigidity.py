"""Local rigidity of the certified 152-point record inside the 77 x 77 grid.

This checker establishes, by exhaustive exact-integer computation, that every
embedding of the certified 152-point no-three-in-line configuration on G_76
into G_77 is an isolated local optimum:

  1. Saturation: every cell of G_77 outside the embedded configuration is
     collinear with two configuration points, so the embedding is maximal.
  2. One-robust saturation: after removing any single configuration point,
     every outside cell is still blocked. No cell is freed.
  3. Two-removal accounting: removing any two configuration points frees at
     most one outside cell; exactly sixteen unordered removal pairs free a
     (unique) cell, and these are listed exhaustively in results.json.

Consequently, for every embedding E and every no-three-in-line set S in G_77:
if |E \\ S| <= 2 then |S \\ E| <= 1 and |S| <= 152. Hence any hypothetical
153- or 154-point configuration omits at least three points of E and contains
at least four points outside E (symmetric difference at least seven).

As a by-product the checker verifies that the decoded record configuration is
invariant under a quarter-turn rotation of G_76, so its dihedral orbit has
exactly two distinct images and the eight embeddings enumerated here (two
images times four translations) are the complete set.

Methods (both exact, no floating point, no randomness):

  * Primary "line census": for each outside cell c, group configuration
    points by the sign-normalized primitive direction of p - c. Points share
    a line through c exactly when they share a direction, so the groups of
    size >= 2 ("heavy lines") determine every blocking pair. Two distinct
    lines through c meet only at c, so a removed point lowers the census of
    at most one heavy line; freeing c with at most two removals is therefore
    possible only in the three enumerated patterns (one line of two, one line
    of three, or two lines of two).
  * Independent cross-check "line walk": for every pair of configuration
    points, walk the full lattice line through the pair in primitive steps
    and record each visited cell. Per-cell blocking-pair counts must match
    the census exactly, and freeing removal sets are re-derived from these
    explicit pair lists as minimum hitting sets and must match as well.
  * Every reported freeing is finally re-verified by direct simulation:
    remove the pair, then test the freed cell against all remaining pairs
    with the standard 2x2 determinant.

Usage (from this directory):

    python3 rigidity.py            # verify every claim against results.json
    python3 rigidity.py --write    # regenerate results.json

Exits nonzero (with a message) if any claim or the committed results fail.
"""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import sys
import time
from collections import defaultdict
from math import gcd
from pathlib import Path

ALPHABET = (
    "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"
    "#$%&@?!()[]<>{}=*+|-/~^_:;,."
)

SMALL = 76  # grid of the certified record
BIG = 77  # target grid
POINTS = 152

HERE = Path(__file__).resolve().parent
DEFAULT_CONFIGURATION = HERE / "configuration.txt"
DEFAULT_RESULTS = HERE / "results.json"

# The dihedral group of the 76 x 76 grid, acting on {0..75}^2 with m = 75.
DIHEDRAL = {
    "identity": lambda x, y: (x, y),
    "rot90": lambda x, y: (SMALL - 1 - y, x),
    "rot180": lambda x, y: (SMALL - 1 - x, SMALL - 1 - y),
    "rot270": lambda x, y: (y, SMALL - 1 - x),
    "flip-x": lambda x, y: (SMALL - 1 - x, y),
    "flip-y": lambda x, y: (x, SMALL - 1 - y),
    "transpose": lambda x, y: (y, x),
    "anti-transpose": lambda x, y: (SMALL - 1 - y, SMALL - 1 - x),
}

Point = tuple[int, int]


def fail(message: str) -> None:
    raise SystemExit(f"FAILED: {message}")


def decode(text: str) -> list[Point]:
    """Decode the record certificate: one marker character, then two
    alphabet-encoded x coordinates per row y = 0..75."""
    encoded = text.strip()
    payload = encoded[1:]
    if len(payload) != 2 * SMALL:
        fail(f"expected {2 * SMALL} payload characters, found {len(payload)}")
    points = []
    for row in range(SMALL):
        for offset in range(2):
            char = payload[2 * row + offset]
            if char not in ALPHABET:
                fail(f"character {char!r} outside the certificate alphabet")
            points.append((ALPHABET.index(char), row))
    return points


def det(a: Point, b: Point, c: Point) -> int:
    return (b[0] - a[0]) * (c[1] - a[1]) - (c[0] - a[0]) * (b[1] - a[1])


def assert_no_three_in_line(points: list[Point], grid: int, label: str) -> None:
    if len(points) != POINTS or len(set(points)) != POINTS:
        fail(f"{label}: expected {POINTS} distinct points")
    if any(not (0 <= x < grid and 0 <= y < grid) for x, y in points):
        fail(f"{label}: point outside the {grid} x {grid} grid")
    for triple in itertools.combinations(points, 3):
        if det(*triple) == 0:
            fail(f"{label}: collinear triple {triple}")


def primitive(dx: int, dy: int) -> Point:
    g = gcd(abs(dx), abs(dy))
    px, py = dx // g, dy // g
    if px < 0 or (px == 0 and py < 0):
        px, py = -px, -py
    return px, py


def point_set_digest(points: frozenset[Point]) -> str:
    canonical = json.dumps(sorted(points), separators=(",", ":"))
    return "sha256:" + hashlib.sha256(canonical.encode("ascii")).hexdigest()


def census_heavy_lines(config: list[Point], cell: Point) -> list[list[Point]]:
    """All maximal groups of >= 2 configuration points collinear with cell."""
    groups: dict[Point, list[Point]] = defaultdict(list)
    cx, cy = cell
    for p in config:
        groups[primitive(p[0] - cx, p[1] - cy)].append(p)
    return [sorted(group) for group in groups.values() if len(group) >= 2]


def minimal_freeing_sets(heavy: list[list[Point]]) -> tuple[list[Point], list[frozenset[Point]]]:
    """Minimal removal sets of size <= 2 that unblock a cell with the given
    heavy lines. Distinct lines through the cell meet only at the cell, so a
    removal serves at most one line; each heavy line of n points needs n - 1
    removals. Only three patterns fit within two removals."""
    singletons: list[Point] = []
    pairs: list[frozenset[Point]] = []
    if len(heavy) == 1:
        line = heavy[0]
        if len(line) == 2:
            singletons.extend(line)
        elif len(line) == 3:
            pairs.extend(frozenset(pair) for pair in itertools.combinations(line, 2))
    elif len(heavy) == 2:
        first, second = heavy
        if len(first) == 2 and len(second) == 2:
            pairs.extend(frozenset((a, b)) for a in first for b in second)
    return singletons, pairs


def walk_pair_table(config: list[Point]) -> dict[Point, list[tuple[Point, Point]]]:
    """Independent construction: cell -> list of configuration pairs collinear
    with it, found by walking every pair's full lattice line inside G_77."""
    table: dict[Point, list[tuple[Point, Point]]] = defaultdict(list)
    for a, b in itertools.combinations(config, 2):
        sx, sy = primitive(b[0] - a[0], b[1] - a[1])
        for direction in (1, -1):
            k = direction
            while True:
                cell = (a[0] + k * sx, a[1] + k * sy)
                if not (0 <= cell[0] < BIG and 0 <= cell[1] < BIG):
                    break
                if cell != a and cell != b:
                    table[cell].append((a, b))
                k += direction
    return table


def hitting_sets_from_pairs(
    pairs: list[tuple[Point, Point]],
) -> tuple[list[Point], list[frozenset[Point]]]:
    """Minimal removal sets of size <= 2 covering every blocking pair,
    derived from the explicit pair list (independent of the census logic)."""
    singletons = [r for r in set(itertools.chain.from_iterable(pairs)) if all(r in p for p in pairs)]
    result: set[frozenset[Point]] = set()
    a0, b0 = pairs[0]
    for r1 in (a0, b0):
        rest = [p for p in pairs if r1 not in p]
        if not rest:
            continue  # r1 alone suffices; handled as a singleton
        candidates = set(rest[0])
        for p in rest[1:]:
            candidates &= set(p)
            if not candidates:
                break
        for r2 in candidates:
            if r2 != r1:
                result.add(frozenset((r1, r2)))
    return sorted(singletons), sorted(result, key=sorted)


def analyze_embedding(embedding: frozenset[Point]) -> dict:
    config = sorted(embedding)
    outside = [
        (x, y) for x in range(BIG) for y in range(BIG) if (x, y) not in embedding
    ]

    # Primary method: per-cell line census.
    blocking_counts: dict[Point, int] = {}
    singleton_freeings: list[tuple[Point, Point]] = []  # (removal, freed cell)
    pair_freeings: dict[frozenset[Point], list[Point]] = defaultdict(list)
    patterns: dict[Point, str] = {}
    for cell in outside:
        heavy = census_heavy_lines(config, cell)
        count = sum(len(line) * (len(line) - 1) // 2 for line in heavy)
        if count == 0:
            fail(f"saturation violated: cell {cell} is addable to an embedding")
        blocking_counts[cell] = count
        singles, pairs = minimal_freeing_sets(heavy)
        for r in singles:
            singleton_freeings.append((r, cell))
        for removal in pairs:
            pair_freeings[removal].append(cell)
        if singles or pairs:
            patterns[cell] = (
                "one-line-of-three" if len(heavy) == 1 else "two-lines-of-two"
            )

    # Independent cross-check: explicit pair lists via line walking.
    table = walk_pair_table(config)
    if set(table) != set(outside):
        fail("cross-check: walked cell set differs from the outside cells")
    for cell in outside:
        if len(table[cell]) != blocking_counts[cell]:
            fail(f"cross-check: blocking count mismatch at {cell}")
        singles, pairs = hitting_sets_from_pairs(table[cell])
        census_singles = sorted(r for r, c in singleton_freeings if c == cell)
        census_pairs = sorted(
            (rm for rm, cells in pair_freeings.items() if cell in cells), key=sorted
        )
        if singles != census_singles or pairs != census_pairs:
            fail(f"cross-check: freeing sets mismatch at {cell}")

    if singleton_freeings:
        fail(f"one-robust saturation violated: {sorted(singleton_freeings)}")

    # Direct simulation of every reported freeing.
    freeing_records = []
    for removal, cells in sorted(pair_freeings.items(), key=lambda kv: sorted(kv[0])):
        if len(cells) > 1:
            fail(f"removal pair {sorted(removal)} frees {len(cells)} cells")
        (cell,) = cells
        remaining = [p for p in config if p not in removal]
        if any(det(cell, a, b) == 0 for a, b in itertools.combinations(remaining, 2)):
            fail(f"simulation: {cell} is not actually freed by removing {sorted(removal)}")
        freeing_records.append(
            {
                "remove": sorted(removal),
                "freedCell": list(cell),
                "pattern": patterns[cell],
            }
        )

    return {
        "pointsDigest": point_set_digest(embedding),
        "outsideCells": len(outside),
        "minBlockingPairsPerCell": min(blocking_counts.values()),
        "blockingIncidenceTotal": sum(blocking_counts.values()),
        "singleRemovalFreedCells": 0,
        "pairRemovalFreeings": freeing_records,
    }


def build_results(configuration_path: Path) -> dict:
    raw = configuration_path.read_bytes()
    base = decode(raw.decode("ascii"))
    assert_no_three_in_line(base, SMALL, "base configuration")
    base_set = frozenset(base)

    rot90 = frozenset(DIHEDRAL["rot90"](x, y) for x, y in base_set)
    quarter_turn = rot90 == base_set

    images: dict[frozenset[Point], list[str]] = defaultdict(list)
    for name, transform in DIHEDRAL.items():
        images[frozenset(transform(x, y) for x, y in base_set)].append(name)

    embeddings: dict[frozenset[Point], dict] = {}
    for image, names in images.items():
        for tx, ty in ((0, 0), (0, 1), (1, 0), (1, 1)):
            embedded = frozenset((x + tx, y + ty) for x, y in image)
            if embedded not in embeddings:
                embeddings[embedded] = {
                    "imageTransforms": sorted(names),
                    "offset": [tx, ty],
                }

    embedding_reports = []
    ordered = sorted(embeddings.items(), key=lambda kv: (sorted(kv[1]["imageTransforms"]), kv[1]["offset"]))
    for index, (embedded, meta) in enumerate(ordered):
        assert_no_three_in_line(sorted(embedded), BIG, f"embedding {index}")
        started = time.time()
        report = analyze_embedding(embedded)
        report = {"index": index, **meta, **report}
        embedding_reports.append(report)
        print(
            f"embedding {index} (transforms {','.join(meta['imageTransforms'])}, "
            f"offset {tuple(meta['offset'])}): saturated, 0 single-removal freeings, "
            f"{len(report['pairRemovalFreeings'])} pair-removal freeings "
            f"[{time.time() - started:.1f}s]",
            file=sys.stderr,
        )

    return {
        "schemaVersion": 1,
        "problem": "no-three-in-line-77",
        "grid": BIG,
        "baseConfiguration": {
            "source": "configuration.txt",
            "fileSha256": "sha256:" + hashlib.sha256(raw).hexdigest(),
            "points": POINTS,
            "grid": SMALL,
            "pointsDigest": point_set_digest(base_set),
            "quarterTurnSymmetric": quarter_turn,
            "distinctDihedralImages": len(images),
        },
        "embeddings": embedding_reports,
        "conclusions": {
            "everyEmbeddingIsMaximalInG77": True,
            "maxCellsFreedByRemovals": {"0": 0, "1": 0, "2": 1},
            "statement": (
                "For each of the 8 embeddings E of the certified 152-point record "
                "into G_77 and every no-three-in-line set S in G_77 with |E \\ S| <= 2, "
                "it holds that |S \\ E| <= 1 and hence |S| <= 152. Any no-three-in-line "
                "set of 153 or more points therefore omits at least 3 points of every "
                "embedding, contains at least 4 points outside it, and has symmetric "
                "difference at least 7 with every embedding."
            ),
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--configuration", type=Path, default=DEFAULT_CONFIGURATION)
    parser.add_argument("--results", type=Path, default=DEFAULT_RESULTS)
    parser.add_argument(
        "--write", action="store_true", help="regenerate the results file"
    )
    args = parser.parse_args()

    started = time.time()
    results = build_results(args.configuration)

    if not results["baseConfiguration"]["quarterTurnSymmetric"]:
        fail("the decoded record configuration is not quarter-turn symmetric")
    if results["baseConfiguration"]["distinctDihedralImages"] != 2:
        fail("expected exactly 2 distinct dihedral images")
    if len(results["embeddings"]) != 8:
        fail("expected exactly 8 distinct embeddings")
    for report in results["embeddings"]:
        if len(report["pairRemovalFreeings"]) != 16:
            fail(f"embedding {report['index']}: expected 16 pair-removal freeings")

    # Round-trip through JSON so tuples and lists compare canonically.
    rendered = json.dumps(
        json.loads(json.dumps(results)), indent=2, sort_keys=True
    ) + "\n"
    if args.write:
        args.results.write_text(rendered, encoding="ascii")
        print(f"wrote {args.results}", file=sys.stderr)
    elif args.results.read_text(encoding="ascii") != rendered:
        fail("computed results differ from the committed results.json")

    print(
        "verified: all 8 embeddings of the 152-point record are maximal in G_77, "
        "remain saturating after any single removal, and admit at most one freed "
        "cell after any pair removal (16 freeing pairs each; see results.json). "
        "Any 153-point or 154-point configuration, if one exists, has symmetric "
        f"difference >= 7 with every embedding. [{time.time() - started:.1f}s]"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
