from __future__ import annotations

import argparse
import csv
import gzip
import hashlib
import json
from pathlib import Path
from typing import Any, Iterable


N = 537
OLD_N = 536
COLOR_COUNT = 6
RADIUS = 43
EXPECTED_BASELINE_SHA256 = (
    "5e2cd4854c20e8441ff52e09e02472657309d35eb4b35c6957a1be37f6a8cbc9"
)
EXPECTED_BASELINE_TRANSACTION = "b28dd977ae39eb77989de8e60b63f7eacd8982d2"
EXPECTED_BLOCKER_COUNTS = {1: 64, 2: 43, 3: 55, 4: 38, 5: 32, 6: 35}
EXPECTED_CASES = {
    2: (43, 0, "case-color-2-extra-0.lrat.gz"),
    4: (38, 5, "case-color-4-extra-5.lrat.gz"),
    5: (32, 11, "case-color-5-extra-11.lrat.gz"),
    6: (35, 8, "case-color-6-extra-8.lrat.gz"),
}
CASE_KEYS = {
    "newColor",
    "blockerPairs",
    "maximumExtraChanges",
    "cnfVariables",
    "cnfClauses",
    "cnfSha256",
    "proofFile",
    "compressedProofSha256",
    "uncompressedProofSha256",
    "proofLines",
    "proofAdditions",
    "proofDeletions",
}
MAX_UNCOMPRESSED_PROOF_BYTES = 64 * 1024 * 1024


def exact_int(value: Any, label: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise ValueError(f"{label} must be an exact integer")
    return value


def sha256_file(path: Path, maximum_bytes: int | None = None) -> tuple[str, int]:
    digest = hashlib.sha256()
    size = 0
    with path.open("rb") as stream:
        while chunk := stream.read(1024 * 1024):
            size += len(chunk)
            if maximum_bytes is not None and size > maximum_bytes:
                raise ValueError(f"{path.name} exceeds the allowed byte bound")
            digest.update(chunk)
    return digest.hexdigest(), size


def sha256_gzip_payload(path: Path) -> tuple[str, int]:
    digest = hashlib.sha256()
    size = 0
    with gzip.open(path, "rb") as stream:
        while chunk := stream.read(1024 * 1024):
            size += len(chunk)
            if size > MAX_UNCOMPRESSED_PROOF_BYTES:
                raise ValueError(f"{path.name} expands beyond the allowed byte bound")
            digest.update(chunk)
    return digest.hexdigest(), size


def read_baseline(path: Path) -> dict[int, int]:
    digest, _ = sha256_file(path)
    if digest != EXPECTED_BASELINE_SHA256:
        raise ValueError("baseline bytes do not match the canonical transaction")
    with path.open(newline="", encoding="ascii") as stream:
        rows = list(csv.reader(stream))
    if not rows or rows[0] != ["integer", "color"]:
        raise ValueError("baseline header must be exactly integer,color")
    if len(rows) != OLD_N + 1:
        raise ValueError(f"baseline must have exactly {OLD_N} data rows")
    colors: dict[int, int] = {}
    for expected, row in enumerate(rows[1:], 1):
        if len(row) != 2 or not all(
            item.isascii() and item.isdecimal() for item in row
        ):
            raise ValueError(f"malformed baseline row {expected + 1}")
        value, color = map(int, row)
        if row != [str(value), str(color)]:
            raise ValueError(f"noncanonical decimal in baseline row {expected + 1}")
        if value != expected or not 1 <= color <= COLOR_COUNT:
            raise ValueError(f"invalid baseline assignment at integer {expected}")
        colors[value] = color
    if set(colors.values()) != set(range(1, COLOR_COUNT + 1)):
        raise ValueError("baseline must use all six colors")
    return colors


def verify_baseline(colors: dict[int, int]) -> int:
    checked = 0
    for x in range(1, OLD_N + 1):
        for y in range(x, OLD_N - x + 1):
            z = x + y
            checked += 1
            if colors[x] == colors[y] == colors[z]:
                raise ValueError(f"baseline has monochromatic triple {x}+{y}={z}")
    if checked != 71824:
        raise AssertionError("unexpected baseline triple count")
    return checked


def variable(value: int, color: int) -> int:
    return (value - 1) * COLOR_COUNT + color


def build_case_formula(
    baseline: dict[int, int], new_color: int, maximum_extra_changes: int
) -> tuple[list[tuple[int, ...] | None], int, list[tuple[int, int]]]:
    clauses: list[tuple[int, ...] | None] = [None]
    maximum_variable = 0

    def add(literals: Iterable[int]) -> None:
        nonlocal maximum_variable
        clause = tuple(literals)
        if not clause or 0 in clause:
            raise AssertionError("initial clauses must be nonempty and zero-free")
        if len(set(clause)) != len(clause):
            raise AssertionError("initial clause contains a duplicate literal")
        maximum_variable = max(maximum_variable, *(abs(literal) for literal in clause))
        clauses.append(clause)

    # Exactly one of the six labeled colors for every integer 1 through 537.
    for value in range(1, N + 1):
        add(variable(value, color) for color in range(1, COLOR_COUNT + 1))
        for first in range(1, COLOR_COUNT + 1):
            for second in range(first + 1, COLOR_COUNT + 1):
                add((-variable(value, first), -variable(value, second)))

    # Every Schur triple, including x=y (which becomes a binary clause).
    schur_triples = 0
    for x in range(1, N + 1):
        for y in range(x, N - x + 1):
            z = x + y
            values = (x, z) if x == y else (x, y, z)
            schur_triples += 1
            for color in range(1, COLOR_COUNT + 1):
                add(-variable(value, color) for value in values)
    if schur_triples != 72092:
        raise AssertionError("unexpected n=537 Schur-triple count")

    # Condition one case on the color assigned to the new integer 537.
    add((variable(N, new_color),))
    blocker_pairs = [
        (x, N - x)
        for x in range(1, N // 2 + 1)
        if baseline[x] == baseline[N - x] == new_color
    ]
    blocker_values = {value for pair in blocker_pairs for value in pair}

    # Each blocker pair must change at least one endpoint by its Schur clause.
    # The auxiliary literal below is true exactly when both endpoints change.
    next_auxiliary = N * COLOR_COUNT + 1
    counted_literals: list[int] = []
    for x, y in blocker_pairs:
        extra = next_auxiliary
        next_auxiliary += 1
        base_x = variable(x, baseline[x])
        base_y = variable(y, baseline[y])
        add((-extra, -base_x))
        add((-extra, -base_y))
        add((base_x, base_y, extra))
        counted_literals.append(extra)

    # A change outside the blocker pairs is also a change beyond their
    # unavoidable one-per-pair lower bound.
    counted_literals.extend(
        -variable(value, baseline[value])
        for value in range(1, N)
        if value not in blocker_values
    )

    # Exact Sinz sequential-counter encoding of at most the case limit among
    # these signed literals. No color-symmetry units are used: label-specific
    # Hamming distance to the fixed baseline already anchors the color names.
    if maximum_extra_changes == 0:
        for literal in counted_literals:
            add((-literal,))
    else:
        item_count = len(counted_literals)
        limit = maximum_extra_changes
        auxiliary_start = next_auxiliary

        def counter(i: int, j: int) -> int:
            if not (1 <= i <= item_count - 1 and 1 <= j <= limit):
                raise AssertionError("sequential-counter index outside encoding")
            return auxiliary_start + (i - 1) * limit + (j - 1)

        add((-counted_literals[0], counter(1, 1)))
        for i in range(2, item_count):
            literal = counted_literals[i - 1]
            add((-literal, counter(i, 1)))
            add((-counter(i - 1, 1), counter(i, 1)))
            for j in range(2, limit + 1):
                add((-literal, -counter(i - 1, j - 1), counter(i, j)))
                add((-counter(i - 1, j), counter(i, j)))
        for i in range(2, item_count + 1):
            literal = counted_literals[i - 1]
            add((-literal, -counter(i - 1, limit)))

    return clauses, maximum_variable, blocker_pairs


def dimacs_digest(
    clauses: list[tuple[int, ...] | None], variable_count: int
) -> str:
    digest = hashlib.sha256()
    digest.update(f"p cnf {variable_count} {len(clauses) - 1}\n".encode("ascii"))
    for clause in clauses[1:]:
        if clause is None:
            raise AssertionError("initial formula unexpectedly contains a deletion")
        line = " ".join(map(str, clause)) + " 0\n"
        digest.update(line.encode("ascii"))
    return digest.hexdigest()


def emit_dimacs(
    path: Path, clauses: list[tuple[int, ...] | None], variable_count: int
) -> None:
    with path.open("w", encoding="ascii", newline="\n") as stream:
        stream.write(f"p cnf {variable_count} {len(clauses) - 1}\n")
        for clause in clauses[1:]:
            if clause is None:
                raise AssertionError("initial formula unexpectedly contains a deletion")
            stream.write(" ".join(map(str, clause)) + " 0\n")


def canonical_integer(token: str, label: str) -> int:
    try:
        value = int(token)
    except ValueError as exc:
        raise ValueError(f"{label} is not an integer") from exc
    if token != str(value):
        raise ValueError(f"{label} is not a canonical decimal integer")
    return value


def set_true(assignments: dict[int, bool], literal: int) -> bool:
    variable_id = abs(literal)
    value = literal > 0
    previous = assignments.get(variable_id)
    if previous is not None and previous != value:
        return False
    assignments[variable_id] = value
    return True


def verify_rup(
    clause: tuple[int, ...],
    hints: list[int],
    clause_table: list[tuple[int, ...] | None],
    command_id: int,
) -> None:
    assignments: dict[int, bool] = {}
    for literal in clause:
        if not set_true(assignments, -literal):
            raise ValueError(f"LRAT clause {command_id} is tautological")
    if not hints:
        raise ValueError(f"LRAT clause {command_id} has no RUP hints")

    for position, hint in enumerate(hints):
        if not 0 < hint < command_id or hint >= len(clause_table):
            raise ValueError(f"LRAT clause {command_id} has invalid hint {hint}")
        reason = clause_table[hint]
        if reason is None:
            raise ValueError(f"LRAT clause {command_id} uses deleted hint {hint}")
        unassigned: list[int] = []
        satisfied = False
        for literal in reason:
            value = assignments.get(abs(literal))
            if value is None:
                unassigned.append(literal)
            elif value == (literal > 0):
                satisfied = True
                break
        if satisfied:
            raise ValueError(f"LRAT hint {hint} is satisfied rather than unit")
        if not unassigned:
            if position != len(hints) - 1:
                raise ValueError(f"LRAT clause {command_id} continues after conflict")
            return
        if len(unassigned) != 1:
            raise ValueError(f"LRAT hint {hint} is not unit under prior hints")
        if not set_true(assignments, unassigned[0]):
            raise ValueError(f"LRAT hint {hint} gives an inconsistent unit")
    raise ValueError(f"LRAT clause {command_id} does not derive a conflict")


def verify_lrat(
    proof_path: Path,
    initial_clauses: list[tuple[int, ...] | None],
    variable_count: int,
) -> dict[str, int]:
    clause_table = initial_clauses
    initial_count = len(clause_table) - 1
    last_command_id = initial_count
    additions = 0
    deletions = 0
    lines = 0
    last_added_clause: tuple[int, ...] | None = None

    with gzip.open(proof_path, "rt", encoding="ascii", newline="") as stream:
        for lines, raw_line in enumerate(stream, 1):
            if not raw_line.endswith("\n") or raw_line.strip() != raw_line[:-1]:
                raise ValueError(f"noncanonical LRAT line {lines} in {proof_path.name}")
            tokens = raw_line[:-1].split(" ")
            if any(not token for token in tokens):
                raise ValueError(f"noncanonical LRAT spacing at line {lines}")
            command_id = canonical_integer(tokens[0], f"LRAT line {lines} id")
            if len(tokens) >= 3 and tokens[1] == "d":
                if command_id < last_command_id:
                    raise ValueError("LRAT deletion identifier moves backward")
                last_command_id = command_id
                if tokens[-1] != "0":
                    raise ValueError(f"unterminated LRAT deletion at line {lines}")
                deleted_ids = [
                    canonical_integer(token, f"LRAT line {lines} deletion")
                    for token in tokens[2:-1]
                ]
                if not deleted_ids or len(set(deleted_ids)) != len(deleted_ids):
                    raise ValueError(f"invalid LRAT deletion list at line {lines}")
                for deleted_id in deleted_ids:
                    if not 0 < deleted_id <= command_id or deleted_id >= len(clause_table):
                        raise ValueError(f"LRAT deletion references invalid clause {deleted_id}")
                    if clause_table[deleted_id] is None:
                        raise ValueError(f"LRAT deletes absent clause {deleted_id}")
                    clause_table[deleted_id] = None
                deletions += 1
                continue

            if command_id <= last_command_id:
                raise ValueError("LRAT addition identifiers are not strictly increasing")
            last_command_id = command_id

            if tokens[-1] != "0" or tokens.count("0") != 2:
                raise ValueError(f"malformed LRAT addition at line {lines}")
            separator = tokens.index("0", 1)
            clause = tuple(
                canonical_integer(token, f"LRAT line {lines} literal")
                for token in tokens[1:separator]
            )
            if any(literal == 0 or abs(literal) > variable_count for literal in clause):
                raise ValueError(f"LRAT clause literal outside the CNF variables at line {lines}")
            if len(set(clause)) != len(clause):
                raise ValueError(f"duplicate literal in LRAT clause at line {lines}")
            hints = [
                canonical_integer(token, f"LRAT line {lines} hint")
                for token in tokens[separator + 1 : -1]
            ]
            if any(hint <= 0 for hint in hints):
                raise ValueError("this checker accepts the committed RUP-only LRAT subset")
            verify_rup(clause, hints, clause_table, command_id)
            if command_id >= len(clause_table):
                clause_table.extend([None] * (command_id - len(clause_table) + 1))
            if clause_table[command_id] is not None:
                raise ValueError(f"LRAT clause identifier {command_id} is already occupied")
            clause_table[command_id] = clause
            additions += 1
            last_added_clause = clause

    if lines == 0 or last_added_clause != ():
        raise ValueError(f"{proof_path.name} does not end by deriving the empty clause")
    return {
        "lines": lines,
        "additions": additions,
        "deletions": deletions,
        "lastCommandId": last_command_id,
    }


def read_metadata(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    expected_keys = {
        "schemaVersion",
        "n",
        "colorCount",
        "radius",
        "distanceDomain",
        "baseline",
        "blockerCounts",
        "cases",
        "proofGeneration",
    }
    if not isinstance(data, dict) or set(data) != expected_keys:
        raise ValueError("cases.json has unexpected or missing fields")
    if (
        exact_int(data["schemaVersion"], "schemaVersion") != 1
        or exact_int(data["n"], "n") != N
        or exact_int(data["colorCount"], "colorCount") != COLOR_COUNT
        or exact_int(data["radius"], "radius") != RADIUS
        or data["distanceDomain"] != "integers-1-through-536"
    ):
        raise ValueError("cases.json does not describe the fixed radius-43 problem")
    baseline = data["baseline"]
    if not isinstance(baseline, dict) or baseline != {
        "file": "baseline-536.csv",
        "sha256": EXPECTED_BASELINE_SHA256,
        "canonicalTransactionId": EXPECTED_BASELINE_TRANSACTION,
        "contributionId": "fredricksen-sweet-536-certificate",
    }:
        raise ValueError("cases.json baseline provenance is not exact")
    recorded_counts = data["blockerCounts"]
    if recorded_counts != {str(color): count for color, count in EXPECTED_BLOCKER_COUNTS.items()}:
        raise ValueError("cases.json blocker counts are not canonical")
    if data["proofGeneration"] != {
        "solver": "CaDiCaL 3.0.1",
        "format": "text-lrat-gzip",
        "options": ["--unsat", "--lrat=true", "--binary=false", "--checkproof=2"],
    }:
        raise ValueError("cases.json proof-generation provenance is not exact")
    return data


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Verify the exact radius-43 nonextension certificate at n=537"
    )
    parser.add_argument("cases", type=Path)
    parser.add_argument("baseline", type=Path)
    parser.add_argument("--emit-cnf-dir", type=Path)
    args = parser.parse_args()

    metadata = read_metadata(args.cases)
    if args.baseline.name != metadata["baseline"]["file"]:
        raise ValueError("baseline argument name disagrees with cases.json")
    baseline = read_baseline(args.baseline)
    baseline_triples = verify_baseline(baseline)

    blocker_counts = {
        color: sum(
            baseline[x] == baseline[N - x] == color
            for x in range(1, N // 2 + 1)
        )
        for color in range(1, COLOR_COUNT + 1)
    }
    if blocker_counts != EXPECTED_BLOCKER_COUNTS:
        raise ValueError(f"unexpected blocker-pair counts: {blocker_counts}")

    cases = metadata["cases"]
    if not isinstance(cases, list) or len(cases) != len(EXPECTED_CASES):
        raise ValueError("cases.json must contain exactly four conditioned cases")
    if [case.get("newColor") for case in cases if isinstance(case, dict)] != sorted(
        EXPECTED_CASES
    ):
        raise ValueError("conditioned cases are not in canonical color order")
    if args.emit_cnf_dir is not None:
        args.emit_cnf_dir.mkdir(parents=True, exist_ok=True)

    total_proof_lines = 0
    for index, case in enumerate(cases):
        if not isinstance(case, dict) or set(case) != CASE_KEYS:
            raise ValueError(f"case {index} has unexpected or missing fields")
        color = exact_int(case["newColor"], f"case {index} newColor")
        if color not in EXPECTED_CASES:
            raise ValueError(f"unexpected conditioned color {color}")
        expected_blockers, expected_extra, expected_proof = EXPECTED_CASES[color]
        if (
            exact_int(case["blockerPairs"], "blockerPairs") != expected_blockers
            or exact_int(case["maximumExtraChanges"], "maximumExtraChanges")
            != expected_extra
            or case["proofFile"] != expected_proof
            or expected_blockers + expected_extra != RADIUS
        ):
            raise ValueError(f"case for new color {color} has the wrong radius split")

        formula, variable_count, pairs = build_case_formula(
            baseline, color, expected_extra
        )
        clause_count = len(formula) - 1
        if len(pairs) != expected_blockers:
            raise ValueError(f"case for new color {color} has wrong blocker pairs")
        if (
            variable_count != exact_int(case["cnfVariables"], "cnfVariables")
            or clause_count != exact_int(case["cnfClauses"], "cnfClauses")
        ):
            raise ValueError(f"case for new color {color} has wrong CNF dimensions")
        if dimacs_digest(formula, variable_count) != case["cnfSha256"]:
            raise ValueError(f"case for new color {color} has wrong CNF digest")

        if args.emit_cnf_dir is not None:
            emit_dimacs(
                args.emit_cnf_dir / f"case-color-{color}-extra-{expected_extra}.cnf",
                formula,
                variable_count,
            )

        proof_path = args.cases.parent / expected_proof
        compressed_digest, _ = sha256_file(proof_path)
        if compressed_digest != case["compressedProofSha256"]:
            raise ValueError(f"compressed proof digest mismatch for color {color}")
        payload_digest, _ = sha256_gzip_payload(proof_path)
        if payload_digest != case["uncompressedProofSha256"]:
            raise ValueError(f"LRAT payload digest mismatch for color {color}")
        proof_stats = verify_lrat(proof_path, formula, variable_count)
        for field, key in (
            ("lines", "proofLines"),
            ("additions", "proofAdditions"),
            ("deletions", "proofDeletions"),
        ):
            if proof_stats[field] != exact_int(case[key], key):
                raise ValueError(f"proof statistic mismatch for color {color}: {field}")
        total_proof_lines += proof_stats["lines"]

    excluded_by_count = {
        color for color, count in blocker_counts.items() if count > RADIUS
    }
    if excluded_by_count != {1, 3}:
        raise AssertionError("unexpected colors excluded by blocker count alone")
    print(
        f"verified baseline ({baseline_triples} triples), blocker counts "
        f"{','.join(str(blocker_counts[color]) for color in range(1, 7))}, and "
        f"four RUP-only LRAT proofs ({total_proof_lines} lines): every valid "
        f"coloring of 1..537 differs from the fixed baseline on at least 44 "
        f"of integers 1..536"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
