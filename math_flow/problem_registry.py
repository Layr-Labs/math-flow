from __future__ import annotations

import json
from pathlib import Path, PurePosixPath

from .errors import MathFlowError
from .repository import list_files_at, read_at, resolve_commit, validate_slug


PROBLEM_REGISTRY_PATH = "protocol/problem-registry.json"


def canonical_problem_ids(root: Path, head: str = "HEAD") -> list[str]:
    root = root.resolve()
    resolved_head = "WORKTREE" if head == "WORKTREE" else resolve_commit(root, head)
    problems: set[str] = set()
    for path in list_files_at(root, resolved_head, "problems"):
        parts = PurePosixPath(path).parts
        if len(parts) != 3 or parts[0] != "problems" or parts[2] != "problem.md":
            continue
        validate_slug(parts[1], "problem id")
        problems.add(parts[1])
    return sorted(problems)


def validate_problem_registry(
    value: object, problem_ids: list[str]
) -> dict[str, object]:
    if not isinstance(value, dict) or set(value) != {
        "schemaVersion",
        "archivedProblems",
    }:
        raise MathFlowError(
            "problem registry must contain schemaVersion and archivedProblems"
        )
    if value.get("schemaVersion") != 1:
        raise MathFlowError("problem registry has an unsupported schema version")
    archived = value.get("archivedProblems")
    if not isinstance(archived, list) or any(
        not isinstance(problem, str) for problem in archived
    ):
        raise MathFlowError("problem registry archivedProblems must be a list of ids")
    for problem in archived:
        validate_slug(problem, "archived problem id")
    if archived != sorted(set(archived)):
        raise MathFlowError(
            "problem registry archivedProblems must be unique and sorted"
        )
    unknown = sorted(set(archived) - set(problem_ids))
    if unknown:
        raise MathFlowError(
            f"problem registry references an unknown problem: {unknown[0]}"
        )
    return {
        "schemaVersion": 1,
        "archivedProblems": list(archived),
    }


def load_problem_registry(root: Path, head: str = "HEAD") -> dict[str, object]:
    root = root.resolve()
    resolved_head = "WORKTREE" if head == "WORKTREE" else resolve_commit(root, head)
    problem_ids = canonical_problem_ids(root, resolved_head)
    if resolved_head == "WORKTREE":
        path = root / PROBLEM_REGISTRY_PATH
        if not path.exists():
            return {"schemaVersion": 1, "archivedProblems": []}
        try:
            value = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            raise MathFlowError("problem registry is not valid JSON") from exc
    else:
        if PROBLEM_REGISTRY_PATH not in list_files_at(root, resolved_head, "protocol"):
            return {"schemaVersion": 1, "archivedProblems": []}
        try:
            value = json.loads(read_at(root, resolved_head, PROBLEM_REGISTRY_PATH))
        except json.JSONDecodeError as exc:
            raise MathFlowError("problem registry is not valid JSON") from exc
    return validate_problem_registry(value, problem_ids)


def problem_status(root: Path, problem: str, head: str = "HEAD") -> str:
    validate_slug(problem, "problem id")
    problem_ids = canonical_problem_ids(root, head)
    if problem not in problem_ids:
        raise MathFlowError(f"problem does not exist: {problem}")
    registry = load_problem_registry(root, head)
    return (
        "archived"
        if problem in set(registry["archivedProblems"])
        else "active"
    )


def active_problem_ids(root: Path, head: str = "HEAD") -> list[str]:
    archived = set(load_problem_registry(root, head)["archivedProblems"])
    return [
        problem
        for problem in canonical_problem_ids(root, head)
        if problem not in archived
    ]
