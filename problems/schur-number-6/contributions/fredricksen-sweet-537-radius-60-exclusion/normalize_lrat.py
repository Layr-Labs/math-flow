from __future__ import annotations

import argparse
import hashlib
import importlib.util
from pathlib import Path
from typing import Any


def load_verifier() -> Any:
    path = Path(__file__).with_name("verify.py")
    spec = importlib.util.spec_from_file_location("radius60_verifier", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("could not load verify.py")
    verifier = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(verifier)
    return verifier


def normalize_hints(
    verifier: Any,
    clause: tuple[int, ...],
    hints: list[int],
    clause_table: list[tuple[int, ...] | None],
    command_id: int,
) -> tuple[list[int], int, int]:
    assignments: dict[int, bool] = {}
    for literal in clause:
        if not verifier.set_true(assignments, -literal):
            raise ValueError(f"LRAT clause {command_id} is tautological")

    kept: list[int] = []
    removed_satisfied = 0
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
            removed_satisfied += 1
            continue

        kept.append(hint)
        if not unassigned:
            removed_after_conflict = len(hints) - position - 1
            return kept, removed_satisfied, removed_after_conflict
        if len(unassigned) != 1:
            raise ValueError(
                f"LRAT hint {hint} is not unit in clause {command_id}"
            )
        if not verifier.set_true(assignments, unassigned[0]):
            raise ValueError(
                f"LRAT hint {hint} gives an inconsistent unit in clause {command_id}"
            )
    raise ValueError(f"LRAT clause {command_id} does not derive a conflict")


def normalize(
    verifier: Any,
    source_path: Path,
    target_path: Path,
    clauses: list[tuple[int, ...] | None],
    variable_count: int,
) -> dict[str, int | str]:
    last_command_id = len(clauses) - 1
    additions = 0
    deletions = 0
    lines = 0
    removed_satisfied = 0
    removed_after_conflict = 0
    last_added_clause: tuple[int, ...] | None = None
    digest = hashlib.sha256()
    byte_count = 0

    with source_path.open("r", encoding="ascii", newline="") as source, target_path.open(
        "w", encoding="ascii", newline="\n"
    ) as target:
        for lines, raw_line in enumerate(source, 1):
            if not raw_line.endswith("\n") or raw_line.strip() != raw_line[:-1]:
                raise ValueError(f"noncanonical LRAT line {lines}")
            tokens = raw_line[:-1].split(" ")
            if any(not token for token in tokens):
                raise ValueError(f"noncanonical LRAT spacing at line {lines}")
            command_id = verifier.canonical_integer(tokens[0], f"line {lines} id")

            if len(tokens) >= 3 and tokens[1] == "d":
                if command_id < last_command_id or tokens[-1] != "0":
                    raise ValueError(f"invalid LRAT deletion at line {lines}")
                last_command_id = command_id
                deleted_ids = [
                    verifier.canonical_integer(token, f"line {lines} deletion")
                    for token in tokens[2:-1]
                ]
                if not deleted_ids or len(set(deleted_ids)) != len(deleted_ids):
                    raise ValueError(f"invalid LRAT deletion list at line {lines}")
                for deleted_id in deleted_ids:
                    if (
                        not 0 < deleted_id <= command_id
                        or deleted_id >= len(clauses)
                        or clauses[deleted_id] is None
                    ):
                        raise ValueError(
                            f"LRAT deletion references invalid clause {deleted_id}"
                        )
                    clauses[deleted_id] = None
                output_line = raw_line
                deletions += 1
            else:
                if command_id <= last_command_id:
                    raise ValueError("LRAT addition identifiers are not increasing")
                last_command_id = command_id
                if tokens[-1] != "0" or tokens.count("0") != 2:
                    raise ValueError(f"malformed LRAT addition at line {lines}")
                separator = tokens.index("0", 1)
                clause = tuple(
                    verifier.canonical_integer(token, f"line {lines} literal")
                    for token in tokens[1:separator]
                )
                if any(
                    literal == 0 or abs(literal) > variable_count
                    for literal in clause
                ) or len(set(clause)) != len(clause):
                    raise ValueError(f"invalid LRAT clause at line {lines}")
                hints = [
                    verifier.canonical_integer(token, f"line {lines} hint")
                    for token in tokens[separator + 1 : -1]
                ]
                if any(hint <= 0 for hint in hints):
                    raise ValueError("normalizer accepts the RUP-only LRAT subset")
                hints, removed_here, trailing_here = normalize_hints(
                    verifier, clause, hints, clauses, command_id
                )
                removed_satisfied += removed_here
                removed_after_conflict += trailing_here
                output_tokens = [
                    str(command_id),
                    *map(str, clause),
                    "0",
                    *map(str, hints),
                    "0",
                ]
                output_line = " ".join(output_tokens) + "\n"
                if command_id >= len(clauses):
                    clauses.extend([None] * (command_id - len(clauses) + 1))
                if clauses[command_id] is not None:
                    raise ValueError(f"LRAT clause {command_id} is already occupied")
                clauses[command_id] = clause
                additions += 1
                last_added_clause = clause

            target.write(output_line)
            encoded = output_line.encode("ascii")
            digest.update(encoded)
            byte_count += len(encoded)

    if lines == 0 or last_added_clause != ():
        raise ValueError("normalized proof does not end by deriving the empty clause")
    return {
        "lines": lines,
        "additions": additions,
        "deletions": deletions,
        "removedSatisfiedHints": removed_satisfied,
        "removedAfterConflictHints": removed_after_conflict,
        "bytes": byte_count,
        "sha256": digest.hexdigest(),
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Normalize CaDiCaL RUP-only LRAT hints for the strict verifier"
    )
    parser.add_argument("cases", type=Path)
    parser.add_argument("baseline", type=Path)
    parser.add_argument("color", type=int)
    parser.add_argument("source", type=Path)
    parser.add_argument("target", type=Path)
    parser.add_argument(
        "--post-extraction",
        action="store_true",
        help="check the expected no-change replay after dependency extraction",
    )
    args = parser.parse_args()

    if args.source.resolve() == args.target.resolve():
        raise ValueError("source and target must be different paths")

    verifier = load_verifier()
    metadata = verifier.read_metadata(args.cases)
    if args.color not in verifier.EXPECTED_CASES:
        raise ValueError("color does not name a conditioned case")
    if args.baseline.name != metadata["baseline"]["file"]:
        raise ValueError("baseline argument name disagrees with cases.json")
    baseline = verifier.read_baseline(args.baseline)
    blockers, maximum_extra_changes, _ = verifier.EXPECTED_CASES[args.color]
    clauses, variable_count, blocker_pairs = verifier.build_case_formula(
        baseline, args.color, maximum_extra_changes
    )
    if len(blocker_pairs) != blockers:
        raise ValueError("regenerated blocker count is wrong")
    stats = normalize(
        verifier, args.source, args.target, clauses, variable_count
    )
    stage = "postExtractionReplay" if args.post_extraction else "normalization"
    expected = metadata["proofGeneration"][stage]["removedHints"][str(args.color)]
    if stats["removedSatisfiedHints"] != expected["satisfied"] or stats[
        "removedAfterConflictHints"
    ] != expected["afterConflict"]:
        raise ValueError("removed-hint counts disagree with cases.json")
    print(
        f"normalized color {args.color}: {stats['lines']} lines, "
        f"removed {stats['removedSatisfiedHints']} satisfied and "
        f"{stats['removedAfterConflictHints']} post-conflict hints, "
        f"{stats['bytes']} bytes, sha256={stats['sha256']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
