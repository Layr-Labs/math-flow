from __future__ import annotations

import hashlib
import json
import re
import subprocess
from dataclasses import dataclass
from pathlib import Path, PurePosixPath

from .errors import MathFlowError


SLUG = re.compile(r"^[a-z0-9][a-z0-9-]*$")


@dataclass(frozen=True)
class ChangedPath:
    status: str
    path: str
    old_path: str | None = None


def _run_git(root: Path, *args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    try:
        result = subprocess.run(
            ["git", *args],
            cwd=root,
            check=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
    except FileNotFoundError as exc:
        raise MathFlowError("Git is required but was not found") from exc
    if check and result.returncode:
        detail = result.stderr.strip() or result.stdout.strip()
        raise MathFlowError(f"git {' '.join(args)} failed: {detail}")
    return result


def is_git_repository(root: Path) -> bool:
    return _run_git(root, "rev-parse", "--is-inside-work-tree", check=False).returncode == 0


def resolve_commit(root: Path, revision: str) -> str:
    result = _run_git(root, "rev-parse", "--verify", f"{revision}^{{commit}}")
    return result.stdout.strip()


def validate_slug(value: str, label: str) -> None:
    if not SLUG.fullmatch(value):
        raise MathFlowError(
            f"invalid {label} {value!r}; use lowercase letters, numbers, and hyphens"
        )


def _check_nonempty(path: Path, label: str) -> None:
    if not path.is_file() or not path.read_text(encoding="utf-8").strip():
        raise MathFlowError(f"{label} must exist and contain text: {path}")


def validate_tree(root: Path) -> dict[str, int]:
    root = root.resolve()
    problems_root = root / "problems"
    if not problems_root.is_dir():
        raise MathFlowError(f"missing problems directory: {problems_root}")

    problem_count = 0
    contribution_count = 0
    for problem_dir in sorted(problems_root.iterdir()):
        if not problem_dir.is_dir():
            raise MathFlowError(f"problems directory may only contain problem directories: {problem_dir}")
        if problem_dir.is_symlink():
            raise MathFlowError(f"problem directories may not be symlinks: {problem_dir}")
        validate_slug(problem_dir.name, "problem id")
        _check_nonempty(problem_dir / "problem.md", "problem statement")
        problem_count += 1

        contributions = problem_dir / "contributions"
        if not contributions.exists():
            continue
        if not contributions.is_dir() or contributions.is_symlink():
            raise MathFlowError(f"contributions must be a real directory: {contributions}")
        for contribution in sorted(contributions.iterdir()):
            if not contribution.is_dir():
                raise MathFlowError(
                    f"contributions directory may only contain contribution directories: {contribution}"
                )
            if contribution.is_symlink():
                raise MathFlowError(f"contributions may not be symlinks: {contribution}")
            validate_slug(contribution.name, "contribution id")
            _check_nonempty(contribution / "README.md", "contribution README")
            for artifact in contribution.rglob("*"):
                if artifact.is_symlink():
                    raise MathFlowError(f"contribution artifacts may not be symlinks: {artifact}")
            contribution_count += 1

    if not problem_count:
        raise MathFlowError("the repository must contain at least one problem")
    return {"problems": problem_count, "contributions": contribution_count}


def _parse_name_status(raw: str) -> list[ChangedPath]:
    fields = raw.split("\0")
    if fields and fields[-1] == "":
        fields.pop()
    changes: list[ChangedPath] = []
    index = 0
    while index < len(fields):
        status = fields[index]
        index += 1
        if not status:
            continue
        if status[0] in {"R", "C"}:
            if index + 1 >= len(fields):
                raise MathFlowError("could not parse Git rename/copy output")
            old_path, path = fields[index], fields[index + 1]
            index += 2
            changes.append(ChangedPath(status=status, path=path, old_path=old_path))
        else:
            if index >= len(fields):
                raise MathFlowError("could not parse Git diff output")
            changes.append(ChangedPath(status=status, path=fields[index]))
            index += 1
    return changes


def contribution_key(path: str) -> tuple[str, str] | None:
    parts = PurePosixPath(path).parts
    if len(parts) < 5 or parts[0] != "problems" or parts[2] != "contributions":
        return None
    return parts[1], parts[3]


def validate_pr(root: Path, base: str, head: str) -> dict[str, object]:
    root = root.resolve()
    base_sha = resolve_commit(root, base)
    head_sha = resolve_commit(root, head)
    diff = _run_git(
        root,
        "diff",
        "--name-status",
        "-z",
        "--find-renames=100%",
        f"{base_sha}...{head_sha}",
        "--",
    )
    changes = _parse_name_status(diff.stdout)
    if not changes:
        raise MathFlowError("the pull request contains no file changes")

    keys: set[tuple[str, str]] = set()
    for change in changes:
        key = contribution_key(change.path)
        if key is None:
            raise MathFlowError(
                "contribution PRs may only change one new contribution directory; "
                f"found {change.path}"
            )
        keys.add(key)
        if change.status != "A":
            raise MathFlowError(
                f"every file in a contribution PR must be newly added; {change.path} "
                f"has status {change.status}"
            )

    if len(keys) != 1:
        rendered = ", ".join(f"{problem}/{contribution}" for problem, contribution in sorted(keys))
        raise MathFlowError(f"a PR must add exactly one contribution directory; found {rendered}")

    problem, contribution = next(iter(keys))
    validate_slug(problem, "problem id")
    validate_slug(contribution, "contribution id")
    prefix = f"problems/{problem}/contributions/{contribution}"

    if _run_git(root, "cat-file", "-e", f"{base_sha}:{prefix}", check=False).returncode == 0:
        raise MathFlowError(f"the contribution directory already exists at the base commit: {prefix}")
    if _run_git(root, "cat-file", "-e", f"{head_sha}:problems/{problem}/problem.md", check=False).returncode:
        raise MathFlowError(f"problem does not exist at the head commit: {problem}")

    readme_path = f"{prefix}/README.md"
    readme = _run_git(root, "show", f"{head_sha}:{readme_path}", check=False)
    if readme.returncode or not readme.stdout.strip():
        raise MathFlowError(f"the new contribution must contain a non-empty {readme_path}")

    tree = _run_git(root, "ls-tree", "-r", head_sha, "--", prefix)
    for line in tree.stdout.splitlines():
        mode = line.split(" ", 1)[0]
        if mode == "120000":
            raise MathFlowError(f"contribution artifacts may not be symlinks: {line.rsplit(chr(9), 1)[-1]}")

    return {
        "base": base_sha,
        "head": head_sha,
        "problemId": problem,
        "contributionId": contribution,
        "files": len(changes),
    }


def _commit_author(root: Path, commit: str) -> dict[str, str]:
    value = _run_git(root, "show", "-s", "--format=%an%x00%ae", commit).stdout.rstrip("\n")
    name, _, email = value.partition("\0")
    return {"displayName": name, "email": email}


def ledger(root: Path, problem: str, head: str = "HEAD") -> dict[str, object]:
    root = root.resolve()
    validate_slug(problem, "problem id")
    head_sha = resolve_commit(root, head)
    path_prefix = f"problems/{problem}/contributions"
    if _run_git(root, "cat-file", "-e", f"{head_sha}:problems/{problem}/problem.md", check=False).returncode:
        raise MathFlowError(f"problem does not exist at {head_sha}: {problem}")

    commits = _run_git(
        root, "rev-list", "--first-parent", "--reverse", head_sha, "--", path_prefix
    ).stdout.splitlines()
    transactions: list[dict[str, object]] = []
    seen: set[tuple[str, str]] = set()
    for commit in commits:
        parent_line = _run_git(root, "rev-list", "--parents", "-n", "1", commit).stdout.split()
        if len(parent_line) == 1:
            diff = _run_git(root, "diff-tree", "--root", "--no-commit-id", "--name-status", "-r", "-z", commit)
        else:
            diff = _run_git(root, "diff-tree", "--no-commit-id", "--name-status", "-r", "-z", parent_line[1], commit)
        additions: set[tuple[str, str]] = set()
        for change in _parse_name_status(diff.stdout):
            key = contribution_key(change.path)
            if change.status == "A" and key is not None and key[0] == problem and key not in seen:
                additions.add(key)
        for _, contribution in sorted(additions):
            seen.add((problem, contribution))
            transactions.append(
                {
                    "ordinal": len(transactions) + 1,
                    "transactionId": commit,
                    "contributionId": contribution,
                    "path": f"{path_prefix}/{contribution}",
                    "author": _commit_author(root, commit),
                }
            )

    return {"problemId": problem, "ledgerHead": head_sha, "transactions": transactions}


def read_at(root: Path, head: str, path: str) -> str:
    if head == "WORKTREE":
        target = (root / path).resolve()
        try:
            target.relative_to(root.resolve())
        except ValueError as exc:
            raise MathFlowError(f"path escapes repository root: {path}") from exc
        return target.read_text(encoding="utf-8")
    return _run_git(root, "show", f"{head}:{path}").stdout


def list_files_at(root: Path, head: str, prefix: str) -> list[str]:
    if head == "WORKTREE":
        directory = (root / prefix).resolve()
        try:
            directory.relative_to(root.resolve())
        except ValueError as exc:
            raise MathFlowError(f"path escapes repository root: {prefix}") from exc
        if not directory.is_dir():
            raise MathFlowError(f"missing contribution directory: {prefix}")
        return sorted(
            path.relative_to(root).as_posix()
            for path in directory.rglob("*")
            if path.is_file() and not path.is_symlink()
        )
    result = _run_git(root, "ls-tree", "-r", "--name-only", head, "--", prefix)
    return sorted(path for path in result.stdout.splitlines() if path)


def worktree_ledger(root: Path, problem: str) -> dict[str, object]:
    validate_slug(problem, "problem id")
    problem_dir = root / "problems" / problem
    _check_nonempty(problem_dir / "problem.md", "problem statement")
    contributions_dir = problem_dir / "contributions"
    contributions = sorted(path for path in contributions_dir.iterdir() if path.is_dir()) if contributions_dir.is_dir() else []
    digest = hashlib.sha256()
    for path in sorted(problem_dir.rglob("*")):
        if path.is_file() and not path.is_symlink():
            digest.update(path.relative_to(root).as_posix().encode())
            digest.update(b"\0")
            digest.update(path.read_bytes())
            digest.update(b"\0")
    head = f"WORKTREE:{digest.hexdigest()}"
    transactions = [
        {
            "ordinal": index,
            "transactionId": f"worktree:{contribution.name}",
            "contributionId": contribution.name,
            "path": contribution.relative_to(root).as_posix(),
            "author": {"displayName": "unknown", "email": ""},
        }
        for index, contribution in enumerate(contributions, start=1)
    ]
    return {"problemId": problem, "ledgerHead": head, "transactions": transactions}


def canonical_json(value: object) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def sha256_json(value: object) -> str:
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()
