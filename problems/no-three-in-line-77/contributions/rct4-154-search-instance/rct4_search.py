"""Validated symmetry-reduced exact search instance for a 154-point
no-three-in-line configuration in G_77 (the rct4 route).

Class definition (Prellberg, arXiv:2602.07751, adapted to n = 77). Let
rho(i, j) = (j, n-1-i) be the quarter-turn about the center ((n-1)/2, (n-1)/2)
of G_n, n odd. A configuration S is in the rct4 pattern when:

  * the anti-diagonal {(i, n-1-i)} contains no point of S;
  * S minus the main diagonal is a union of full <rho>-orbits (size 4); and
  * S meets the main diagonal in exactly one <rho^2>-orbit pair
    {(i, i), (n-1-i, n-1-i)} with i != (n-1)/2.

Choosing (n-1)/2 off-diagonal orbits plus one diagonal pair yields exactly
4*(n-1)/2 + 2 = 2n points. Every known 2n certificate for odd n from 47
through 69 belongs to this class (Flammenkamp database markers 'c').

Subcommands (validation paths are stdlib-only):

  check-known [--certificates FILE]   decode every certificate line, verify
                                      the no-3-in-line property exactly, and
                                      check it satisfies the reduced model
  results [--write]                   recompute all deterministic results and
                                      compare against (or write) results.json
  solve N [--seed --time --workers --out]   CP-SAT search (needs ortools)
  export-cnf N --out FILE             DIMACS CNF of the instance (needs
                                      python-sat for cardinality encoding)
  verify FILE N                       exact check of a JSON point list

Every claimed solution is re-verified point-by-point with exact integer
arithmetic before being reported or written. No floating point anywhere.
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

HERE = Path(__file__).resolve().parent
DEFAULT_CERTIFICATES = HERE / "known_certificates.txt"
DEFAULT_RESULTS = HERE / "results.json"

Point = tuple[int, int]


def fail(message: str) -> None:
    raise SystemExit(f"FAILED: {message}")


def rho(i: int, j: int, n: int) -> Point:
    return (j, n - 1 - i)


def orbit(cell: Point, n: int) -> tuple[Point, ...]:
    pts = [cell]
    for _ in range(3):
        pts.append(rho(*pts[-1], n))
    return tuple(sorted(set(pts)))


def enumerate_lines(n: int) -> list[list[Point]]:
    """Every maximal grid line carrying >= 3 lattice points of G_n.

    Any three collinear grid points lie on such a line, so bounding every
    enumerated line by 2 selected points is exactly the no-3-in-line
    condition. Directions with max(|dx|, |dy|) > (n-1)//2 cannot carry three
    grid points and are skipped.
    """
    lines = []
    max_step = (n - 1) // 2
    dirs = [(0, 1), (1, 0)]
    for dx in range(1, max_step + 1):
        for dy in range(-max_step, max_step + 1):
            if dy != 0 and gcd(dx, abs(dy)) == 1:
                dirs.append((dx, dy))
    for dx, dy in dirs:
        for x in range(n):
            for y in range(n):
                px, py = x - dx, y - dy
                if 0 <= px < n and 0 <= py < n:
                    continue  # (x, y) is not the first grid point on the line
                cells = []
                cx, cy = x, y
                while 0 <= cx < n and 0 <= cy < n:
                    cells.append((cx, cy))
                    cx += dx
                    cy += dy
                if len(cells) >= 3:
                    lines.append(cells)
    return lines


def build_structure(n: int):
    """Orbit layout: cell -> ('off', orbit index) or ('diag', pair index)."""
    if n % 2 == 0:
        fail("this instance is defined for odd n")
    m = (n - 1) // 2
    anti = {(i, n - 1 - i) for i in range(n)}
    orbit_of: dict[Point, tuple[str, int]] = {}
    off_orbits: list[tuple[Point, ...]] = []
    seen: set[tuple[Point, ...]] = set()
    for x in range(n):
        for y in range(n):
            cell = (x, y)
            if cell in anti:
                continue  # anti-diagonal cells are fixed empty
            if x == y:
                orbit_of[cell] = ("diag", min(x, n - 1 - x))
                continue
            orb = orbit(cell, n)
            if orb not in seen:
                seen.add(orb)
                for c in orb:
                    orbit_of[c] = ("off", len(off_orbits))
                off_orbits.append(orb)
    return m, anti, orbit_of, off_orbits


def line_constraints(n: int):
    """Deduplicated constraints sum(coeff * y) <= 2, one per grid line orbit."""
    m, anti, orbit_of, off_orbits = build_structure(n)
    constraints: set[tuple] = set()
    for cells in enumerate_lines(n):
        weights: dict[tuple[str, int], int] = defaultdict(int)
        for c in cells:
            if c not in anti:
                weights[orbit_of[c]] += 1
        terms = tuple(sorted(weights.items()))
        if sum(v for _, v in terms) >= 3:
            constraints.add(terms)
    return m, orbit_of, off_orbits, sorted(constraints)


def decode_certificate(line: str) -> tuple[int, list[Point]]:
    encoded = line.strip()
    payload = encoded[1:]
    if len(payload) % 2:
        fail("certificate payload must contain two entries per row")
    n = len(payload) // 2
    points = []
    for row in range(n):
        for off in range(2):
            char = payload[2 * row + off]
            if char not in ALPHABET:
                fail(f"character {char!r} outside the certificate alphabet")
            points.append((ALPHABET.index(char), row))
    return n, points


def full_verify(points: list[Point], n: int) -> None:
    if len(points) != len(set(points)):
        fail("duplicate points")
    if any(not (0 <= x < n and 0 <= y < n) for x, y in points):
        fail("point outside the grid")
    for a, b, c in itertools.combinations(points, 3):
        if (b[0] - a[0]) * (c[1] - a[1]) - (c[0] - a[0]) * (b[1] - a[1]) == 0:
            fail(f"collinear triple {a} {b} {c}")


def assignment_from_points(points: list[Point], n: int):
    """Decompose an rct4-class configuration into model variables."""
    m, anti, orbit_of, off_orbits = build_structure(n)
    S = set(points)
    if S & anti:
        fail("configuration occupies the anti-diagonal")
    off: set[int] = set()
    diag: set[int] = set()
    for p in S:
        kind, idx = orbit_of[p]
        if kind == "off":
            if not set(orbit(p, n)) <= S:
                fail(f"rho-orbit of {p} is not fully occupied")
            off.add(idx)
        else:
            diag.add(idx)
    if len(off) != (n - 1) // 2 or len(diag) != 1:
        fail(f"unexpected decomposition: {len(off)} orbits, {len(diag)} pairs")
    return off, diag


def model_stats(n: int) -> dict:
    m, orbit_of, off_orbits, constraints = line_constraints(n)
    return {
        "n": n,
        "offOrbitVariables": len(off_orbits),
        "diagonalPairVariables": m,
        "lineConstraints": len(constraints),
        "targetPoints": 2 * n,
        "chosenOffOrbits": (n - 1) // 2,
        "chosenDiagonalPairs": 1,
    }


def check_certificate_line(raw: str) -> dict:
    n, points = decode_certificate(raw)
    full_verify(points, n)
    off, diag = assignment_from_points(points, n)
    m, orbit_of, off_orbits, constraints = line_constraints(n)
    values = {("off", i): int(i in off) for i in range(len(off_orbits))}
    values.update({("diag", i): int(i in diag) for i in range(m)})
    for terms in constraints:
        if sum(values[k] * v for k, v in terms) > 2:
            fail(f"n={n}: model constraint violated by known certificate")
    return {
        "n": n,
        "marker": raw.strip()[0],
        "points": len(points),
        "lineSha256": "sha256:" + hashlib.sha256(raw.strip().encode()).hexdigest(),
        "verifiedNoThreeInLine": True,
        "satisfiesReducedModel": True,
        "lineConstraintsChecked": len(constraints),
    }


def cmd_check_known(cert_path: Path) -> list[dict]:
    reports = []
    for raw in cert_path.read_text().splitlines():
        if not raw.strip():
            continue
        report = check_certificate_line(raw)
        print(
            f"n={report['n']}: {report['points']} points verified exactly; "
            f"satisfies all {report['lineConstraintsChecked']} reduced-model "
            "constraints"
        )
        reports.append(report)
    if not reports:
        fail("no certificates found")
    return reports


def cmd_results(cert_path: Path, results_path: Path, write: bool) -> None:
    results = {
        "schemaVersion": 1,
        "problem": "no-three-in-line-77",
        "instance": "rct4-pattern search for a 154-point set in G_77",
        "knownCertificates": {
            "fileSha256": "sha256:"
            + hashlib.sha256(cert_path.read_bytes()).hexdigest(),
            "checks": cmd_check_known(cert_path),
        },
        "modelStats": [model_stats(n) for n in (41, 47, 77)],
    }
    rendered = (
        json.dumps(json.loads(json.dumps(results)), indent=2, sort_keys=True) + "\n"
    )
    if write:
        results_path.write_text(rendered, encoding="ascii")
        print(f"wrote {results_path}", file=sys.stderr)
    elif results_path.read_text(encoding="ascii") != rendered:
        fail("computed results differ from the committed results.json")
    else:
        print("results.json verified")


def cmd_solve(n: int, seed: int, limit: float, workers: int, out: str | None) -> int:
    from ortools.sat.python import cp_model

    t0 = time.time()
    m, orbit_of, off_orbits, constraints = line_constraints(n)
    model = cp_model.CpModel()
    y_off = [model.NewBoolVar(f"o{i}") for i in range(len(off_orbits))]
    y_diag = [model.NewBoolVar(f"d{i}") for i in range(m)]
    var = {("off", i): y_off[i] for i in range(len(off_orbits))}
    var.update({("diag", i): y_diag[i] for i in range(m)})
    for terms in constraints:
        model.Add(sum(v * var[k] for k, v in terms) <= 2)
    model.Add(sum(y_off) == (n - 1) // 2)
    model.Add(sum(y_diag) == 1)
    print(
        f"n={n}: model built in {time.time() - t0:.1f}s: {len(y_off)}+{len(y_diag)} "
        f"vars, {len(constraints)} line constraints",
        flush=True,
    )
    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = limit
    solver.parameters.num_workers = workers
    solver.parameters.random_seed = seed
    solver.parameters.randomize_search = True
    status = solver.Solve(model)
    name = solver.StatusName(status)
    print(
        f"n={n} seed={seed}: {name} after {solver.WallTime():.1f}s "
        f"(conflicts {solver.NumConflicts()}, branches {solver.NumBranches()})",
        flush=True,
    )
    if status in (cp_model.FEASIBLE, cp_model.OPTIMAL):
        points: list[Point] = []
        for i, orb in enumerate(off_orbits):
            if solver.Value(y_off[i]):
                points.extend(orb)
        for i in range(m):
            if solver.Value(y_diag[i]):
                points.extend([(i, i), (n - 1 - i, n - 1 - i)])
        points = sorted(points)
        full_verify(points, n)
        print(f"SOLUTION: {len(points)} points verified exactly")
        payload = json.dumps(points)
        if out:
            Path(out).write_text(payload + "\n")
            print(f"wrote {out}")
        else:
            print(payload)
        return 10
    return 20 if name == "INFEASIBLE" else 0


def cmd_export_cnf(n: int, out: str) -> None:
    from pysat.card import CardEnc, EncType
    from pysat.formula import IDPool

    m, orbit_of, off_orbits, constraints = line_constraints(n)
    n_off = len(off_orbits)

    def vid(key: tuple[str, int]) -> int:
        kind, idx = key
        return idx + 1 if kind == "off" else n_off + idx + 1

    clauses: list[list[int]] = []
    for terms in constraints:
        heavy = [vid(k) for k, v in terms if v >= 3]
        for u in heavy:
            clauses.append([-u])
        twos = [vid(k) for k, v in terms if v == 2]
        ones = [vid(k) for k, v in terms if v == 1]
        for a, b in itertools.combinations(twos, 2):
            clauses.append([-a, -b])
        for a in twos:
            for b in ones:
                clauses.append([-a, -b])
        for a, b, c in itertools.combinations(ones, 3):
            clauses.append([-a, -b, -c])
    pool = IDPool(start_from=n_off + m + 1)
    card1 = CardEnc.equals(
        lits=list(range(1, n_off + 1)),
        bound=(n - 1) // 2,
        vpool=pool,
        encoding=EncType.seqcounter,
    )
    card2 = CardEnc.equals(
        lits=list(range(n_off + 1, n_off + m + 1)),
        bound=1,
        vpool=pool,
        encoding=EncType.seqcounter,
    )
    all_clauses = clauses + card1.clauses + card2.clauses
    top = max(pool.top, n_off + m)
    with open(out, "w") as fh:
        fh.write(f"c rct4-pattern 2n search, n={n}\n")
        fh.write(f"c vars 1..{n_off} = off-diagonal orbits (see rct4_search.py)\n")
        fh.write(f"c vars {n_off + 1}..{n_off + m} = main-diagonal pairs\n")
        fh.write(f"p cnf {top} {len(all_clauses)}\n")
        for cl in all_clauses:
            fh.write(" ".join(map(str, cl)) + " 0\n")
    print(f"wrote {out}: {top} vars, {len(all_clauses)} clauses")


def cmd_verify(path: str, n: int) -> None:
    points = [tuple(p) for p in json.loads(Path(path).read_text())]
    full_verify(points, n)
    print(f"verified: {len(points)} points on {n} x {n}, no three collinear")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("check-known")
    p.add_argument("--certificates", type=Path, default=DEFAULT_CERTIFICATES)
    p = sub.add_parser("results")
    p.add_argument("--certificates", type=Path, default=DEFAULT_CERTIFICATES)
    p.add_argument("--results", type=Path, default=DEFAULT_RESULTS)
    p.add_argument("--write", action="store_true")
    p = sub.add_parser("solve")
    p.add_argument("n", type=int)
    p.add_argument("--seed", type=int, default=1)
    p.add_argument("--time", type=float, default=3600)
    p.add_argument("--workers", type=int, default=1)
    p.add_argument("--out", default=None)
    p = sub.add_parser("export-cnf")
    p.add_argument("n", type=int)
    p.add_argument("--out", required=True)
    p = sub.add_parser("verify")
    p.add_argument("path")
    p.add_argument("n", type=int)
    args = ap.parse_args()
    if args.cmd == "check-known":
        cmd_check_known(args.certificates)
        return 0
    if args.cmd == "results":
        cmd_results(args.certificates, args.results, args.write)
        return 0
    if args.cmd == "solve":
        return cmd_solve(args.n, args.seed, args.time, args.workers, args.out)
    if args.cmd == "export-cnf":
        cmd_export_cnf(args.n, args.out)
        return 0
    cmd_verify(args.path, args.n)
    return 0


if __name__ == "__main__":
    sys.exit(main())
