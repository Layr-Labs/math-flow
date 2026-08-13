from __future__ import annotations

import argparse
import hashlib
import mmap
from pathlib import Path


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        while block := stream.read(1024 * 1024):
            digest.update(block)
    return digest.hexdigest()


def extract_core(
    source_path: Path, target_path: Path, initial_clause_count: int
) -> dict[str, int | str]:
    selected: list[tuple[int, int]] = []
    needed: set[int] | None = None
    additions = 0
    deletions = 0
    final_id: int | None = None

    with source_path.open("rb") as source:
        with mmap.mmap(source.fileno(), 0, access=mmap.ACCESS_READ) as data:
            cursor = len(data)
            while cursor:
                line_end = cursor
                if data[line_end - 1 : line_end] == b"\n":
                    line_end -= 1
                previous_newline = data.rfind(b"\n", 0, line_end)
                line_start = previous_newline + 1
                cursor = line_start
                line = data[line_start:line_end].strip()
                if not line:
                    continue

                fields = line.split()
                command_id = int(fields[0])
                if len(fields) >= 2 and fields[1] == b"d":
                    deletions += 1
                    continue

                additions += 1
                if fields[-1] != b"0":
                    raise ValueError(f"command {command_id}: missing final zero")
                try:
                    clause_end = fields.index(b"0", 1)
                except ValueError as error:
                    raise ValueError(
                        f"command {command_id}: missing clause terminator"
                    ) from error

                if needed is None:
                    if clause_end != 1:
                        raise ValueError(
                            f"last addition {command_id} is not the empty clause"
                        )
                    final_id = command_id
                    needed = {command_id}

                if command_id not in needed:
                    continue

                needed.remove(command_id)
                selected.append((line_start, line_end))
                for raw_hint in fields[clause_end + 1 : -1]:
                    hint = int(raw_hint)
                    if hint <= 0:
                        raise ValueError(
                            f"command {command_id}: non-RUP hint {hint}"
                        )
                    if hint > initial_clause_count:
                        if hint >= command_id:
                            raise ValueError(
                                f"command {command_id}: non-earlier hint {hint}"
                            )
                        needed.add(hint)

            if needed is None:
                raise ValueError("proof has no additions")
            if needed:
                raise ValueError(
                    f"missing derived dependencies: {sorted(needed)[:10]}"
                )

            with target_path.open("xb") as target:
                for start, end in reversed(selected):
                    target.write(data[start:end])
                    target.write(b"\n")

    return {
        "inputSha256": sha256_file(source_path),
        "outputSha256": sha256_file(target_path),
        "initialClauses": initial_clause_count,
        "finalId": final_id if final_id is not None else 0,
        "inputAdditions": additions,
        "inputDeletions": deletions,
        "keptAdditions": len(selected),
        "outputBytes": target_path.stat().st_size,
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Extract the transitive RUP core ending at the empty clause"
    )
    parser.add_argument("source", type=Path)
    parser.add_argument("target", type=Path)
    parser.add_argument("initial_clauses", type=int)
    args = parser.parse_args()
    if args.initial_clauses <= 0:
        raise ValueError("initial_clauses must be positive")
    if args.source.resolve() == args.target.resolve():
        raise ValueError("source and target must be different paths")
    stats = extract_core(args.source, args.target, args.initial_clauses)
    print(" ".join(f"{key}={value}" for key, value in stats.items()))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
