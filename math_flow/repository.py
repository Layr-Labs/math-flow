from __future__ import annotations

import hashlib
import json
import re
import subprocess
from fnmatch import fnmatchcase
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


def is_ancestor(root: Path, ancestor: str, descendant: str) -> bool:
    return (
        _run_git(
            root,
            "merge-base",
            "--is-ancestor",
            resolve_commit(root, ancestor),
            resolve_commit(root, descendant),
            check=False,
        ).returncode
        == 0
    )


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
    # Imported lazily to keep the projection registry's Git-oriented admission
    # helpers from creating an import cycle at module load time.
    from .directions import validate_direction_tree
    from .governance import validate_projection_registry
    from .attestations import validate_contribution_verification_at, validate_verifier_tree
    from .claims import validate_claim_manifest
    from .problem_registry import load_problem_registry

    validate_projection_registry(root)
    validate_verifier_tree(root)
    problems_root = root / "problems"
    if not problems_root.is_dir():
        raise MathFlowError(f"missing problems directory: {problems_root}")
    load_problem_registry(root, "WORKTREE")

    problem_count = 0
    contribution_count = 0
    direction_count = 0
    direction_event_count = 0
    for problem_dir in sorted(problems_root.iterdir()):
        if not problem_dir.is_dir():
            raise MathFlowError(f"problems directory may only contain problem directories: {problem_dir}")
        if problem_dir.is_symlink():
            raise MathFlowError(f"problem directories may not be symlinks: {problem_dir}")
        validate_slug(problem_dir.name, "problem id")
        _check_nonempty(problem_dir / "problem.md", "problem statement")
        problem_count += 1

        contributions = problem_dir / "contributions"
        if contributions.exists():
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
                claims_path = contribution / "claims.json"
                if claims_path.exists():
                    try:
                        claims = json.loads(claims_path.read_text(encoding="utf-8"))
                    except json.JSONDecodeError as exc:
                        raise MathFlowError(
                            f"contribution claims manifest is not valid JSON: {claims_path}"
                        ) from exc
                    validate_claim_manifest(claims, problem=problem_dir.name)
                for artifact in contribution.rglob("*"):
                    if artifact.is_symlink():
                        raise MathFlowError(f"contribution artifacts may not be symlinks: {artifact}")
                validate_contribution_verification_at(
                    root,
                    "WORKTREE",
                    contribution.relative_to(root).as_posix(),
                )
                contribution_count += 1

        events, directions = validate_direction_tree(root, problem_dir)
        direction_event_count += events
        direction_count += directions

    if not problem_count:
        raise MathFlowError("the repository must contain at least one problem")
    return {
        "problems": problem_count,
        "contributions": contribution_count,
        "researchDirections": direction_count,
        "directionEvents": direction_event_count,
    }


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

    from .directions import (
        direction_event_key,
        research_direction_ledger,
        validate_direction_event,
    )

    contribution_keys = {contribution_key(change.path) for change in changes}
    direction_keys = {direction_event_key(change.path) for change in changes}
    contribution_only = None not in contribution_keys
    direction_only = None not in direction_keys
    if contribution_only and direction_only:
        raise MathFlowError("participant PR paths ambiguously match multiple transaction types")
    if not contribution_only and not direction_only:
        raise MathFlowError(
            "participant PRs may only change one new contribution or research direction event; "
            f"found {changes[0].path}"
        )
    for change in changes:
        if change.status != "A":
            raise MathFlowError(
                f"every file in a participant PR must be newly added; {change.path} "
                f"has status {change.status}"
            )

    if contribution_only:
        keys = {key for key in contribution_keys if key is not None}
        if len(keys) != 1:
            rendered = ", ".join(
                f"{problem}/{contribution}"
                for problem, contribution in sorted(keys)
            )
            raise MathFlowError(
                f"a PR must add exactly one contribution directory; found {rendered}"
            )
        problem, contribution = next(iter(keys))
        validate_slug(problem, "problem id")
        validate_slug(contribution, "contribution id")
        prefix = f"problems/{problem}/contributions/{contribution}"

        if _run_git(
            root, "cat-file", "-e", f"{base_sha}:{prefix}", check=False
        ).returncode == 0:
            raise MathFlowError(
                f"the contribution directory already exists at the base commit: {prefix}"
            )
        if _run_git(
            root,
            "cat-file",
            "-e",
            f"{head_sha}:problems/{problem}/problem.md",
            check=False,
        ).returncode:
            raise MathFlowError(f"problem does not exist at the head commit: {problem}")
        from .problem_registry import problem_status

        if problem_status(root, problem, base_sha) == "archived":
            raise MathFlowError(
                f"problem is archived and cannot accept contributions: {problem}"
            )

        readme_path = f"{prefix}/README.md"
        readme = _run_git(root, "show", f"{head_sha}:{readme_path}", check=False)
        if readme.returncode or not readme.stdout.strip():
            raise MathFlowError(
                f"the new contribution must contain a non-empty {readme_path}"
            )

        tree = _run_git(root, "ls-tree", "-r", head_sha, "--", prefix)
        for line in tree.stdout.splitlines():
            mode = line.split(" ", 1)[0]
            if mode == "120000":
                raise MathFlowError(
                    f"contribution artifacts may not be symlinks: {line.rsplit(chr(9), 1)[-1]}"
                )

        from .attestations import validate_contribution_verification_at
        from .claims import validate_claim_manifest

        validate_contribution_verification_at(root, head_sha, prefix)
        claims_path = f"{prefix}/claims.json"
        if claims_path in list_files_at(root, head_sha, prefix):
            try:
                claims = json.loads(read_at(root, head_sha, claims_path))
            except json.JSONDecodeError as exc:
                raise MathFlowError(
                    "contribution claims manifest is not valid JSON"
                ) from exc
            prior = ledger(root, problem, base_sha)
            validate_claim_manifest(
                claims,
                problem=problem,
                subject_transaction_id=head_sha,
                prior_transaction_ids={
                    str(item["transactionId"]) for item in prior["transactions"]
                },
            )

        return {
            "base": base_sha,
            "head": head_sha,
            "transactionKind": "contribution",
            "problemId": problem,
            "contributionId": contribution,
            "files": len(changes),
        }

    keys = {key for key in direction_keys if key is not None}
    if len(keys) != 1:
        rendered = ", ".join(
            f"{problem}/{direction}/{event}"
            for problem, direction, event in sorted(keys)
        )
        raise MathFlowError(
            f"a PR must add exactly one research direction event; found {rendered}"
        )
    problem, direction_id, event_id = next(iter(keys))
    validate_slug(problem, "problem id")
    validate_slug(direction_id, "research direction id")
    validate_slug(event_id, "research direction event id")
    prefix = f"problems/{problem}/directions/{direction_id}/events/{event_id}"
    paths = sorted(change.path for change in changes)
    expected_paths = sorted([f"{prefix}/README.md", f"{prefix}/event.json"])
    if paths != expected_paths:
        raise MathFlowError(
            "a research direction event PR must add exactly README.md and event.json"
        )
    if _run_git(
        root, "cat-file", "-e", f"{base_sha}:{prefix}", check=False
    ).returncode == 0:
        raise MathFlowError(
            f"the research direction event already exists at the base commit: {prefix}"
        )
    if _run_git(
        root,
        "cat-file",
        "-e",
        f"{head_sha}:problems/{problem}/problem.md",
        check=False,
    ).returncode:
        raise MathFlowError(f"problem does not exist at the head commit: {problem}")
    from .problem_registry import problem_status

    if problem_status(root, problem, base_sha) == "archived":
        raise MathFlowError(
            f"problem is archived and cannot accept direction events: {problem}"
        )
    readme = read_at(root, head_sha, f"{prefix}/README.md")
    if not readme.strip():
        raise MathFlowError("research direction event README must contain text")
    tree = _run_git(root, "ls-tree", "-r", head_sha, "--", prefix)
    for line in tree.stdout.splitlines():
        mode = line.split(" ", 1)[0]
        if mode == "120000":
            raise MathFlowError(
                f"research direction event files may not be symlinks: {line.rsplit(chr(9), 1)[-1]}"
            )
    try:
        raw_event = json.loads(read_at(root, head_sha, f"{prefix}/event.json"))
    except json.JSONDecodeError as exc:
        raise MathFlowError(f"research direction event is not valid JSON: {exc}") from exc
    event = validate_direction_event(
        raw_event,
        expected_direction_id=direction_id,
        expected_event_id=event_id,
    )
    direction_state = research_direction_ledger(root, problem, base_sha)
    existing = next(
        (
            item
            for item in direction_state["directions"]
            if item["directionId"] == direction_id
        ),
        None,
    )
    event_type = str(event["eventType"])
    if event_type == "register":
        if existing is not None:
            raise MathFlowError(
                f"research direction already exists at the base commit: {direction_id}"
            )
    else:
        if existing is None:
            raise MathFlowError(
                f"research direction does not exist at the base commit: {direction_id}"
            )
        if existing["status"] != "active":
            raise MathFlowError(
                f"research direction is already {existing['status']}: {direction_id}"
            )
        if event["previousEventId"] != existing["currentEventId"]:
            raise MathFlowError(
                "research direction event does not extend the current terminal event"
            )
        originating_author = existing.get("registeredBy")
        event_author = _commit_author(root, head_sha)
        if event_type == "release" and event_author != originating_author:
            raise MathFlowError(
                "research direction release author must match the originating "
                "register event author"
            )
    if event_type == "complete":
        source = ledger(root, problem, base_sha)
        ordinals = {
            str(item["transactionId"]): int(item["ordinal"])
            for item in source["transactions"]
        }
        transaction_ids = list(event["contributionTransactionIds"])
        if any(item not in ordinals for item in transaction_ids):
            raise MathFlowError(
                "research direction completion references a non-canonical contribution"
            )
        if transaction_ids != sorted(transaction_ids, key=ordinals.get):
            raise MathFlowError(
                "research direction completion contribution IDs must follow ledger order"
            )
    return {
        "base": base_sha,
        "head": head_sha,
        "transactionKind": "direction-event",
        "problemId": problem,
        "directionId": direction_id,
        "eventId": event_id,
        "eventType": event_type,
        "files": len(changes),
    }


def _commit_author(root: Path, commit: str) -> dict[str, str]:
    value = _run_git(root, "show", "-s", "--format=%an%x00%ae", commit).stdout.rstrip("\n")
    name, _, email = value.partition("\0")
    return {"displayName": name, "email": email}


def commit_timestamp(root: Path, commit: str) -> int:
    """Return the immutable Git committer timestamp for a canonical commit."""

    rendered = _run_git(root.resolve(), "show", "-s", "--format=%ct", commit).stdout.strip()
    try:
        value = int(rendered)
    except ValueError as exc:  # pragma: no cover - Git itself supplies this value
        raise MathFlowError(f"commit has an invalid committer timestamp: {commit}") from exc
    if value < 0:
        raise MathFlowError(f"commit has a negative committer timestamp: {commit}")
    return value


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

    statement = read_at(root, head_sha, f"problems/{problem}/problem.md")
    problem_core = {
        "problemId": problem,
        "problemStatementDigest": f"sha256:{hashlib.sha256(statement.encode('utf-8')).hexdigest()}",
        "transactionIds": [item["transactionId"] for item in transactions],
    }
    relevant = _run_git(
        root,
        "rev-list",
        "--first-parent",
        "-n",
        "1",
        head_sha,
        "--",
        f"problems/{problem}/problem.md",
        path_prefix,
    ).stdout.strip()
    return {
        "problemId": problem,
        "ledgerHead": head_sha,
        "problemLedgerHead": relevant or head_sha,
        "problemLedgerDigest": f"sha256:{sha256_json(problem_core)}",
        "transactions": transactions,
    }


def affected_problems(
    root: Path,
    base: str,
    head: str,
    global_patterns: list[str] | None = None,
) -> dict[str, object]:
    """Return problems whose source changed between two repository commits.

    A path matching a global pattern affects every problem that exists at the
    head commit. Otherwise, changes under ``problems/<id>/`` affect only that
    problem. Deleted problems are omitted because they cannot be projected.
    """
    root = root.resolve()
    head_sha = resolve_commit(root, head)
    from .problem_registry import active_problem_ids

    problems = active_problem_ids(root, head_sha)

    if base and set(base) == {"0"}:
        return {
            "base": base,
            "head": head_sha,
            "problems": problems,
            "reason": "initial-push",
        }

    base_sha = resolve_commit(root, base)
    changed = _run_git(
        root, "diff", "--name-only", "-z", base_sha, head_sha, "--"
    ).stdout.split("\0")
    changed_paths = [path for path in changed if path]
    patterns = global_patterns or []
    if any(fnmatchcase(path, pattern) for path in changed_paths for pattern in patterns):
        selected = problems
        reason = "shared-input"
    else:
        selected = sorted(
            {
                parts[1]
                for path in changed_paths
                if len(parts := PurePosixPath(path).parts) >= 2
                and parts[0] == "problems"
                and parts[1] in problems
            }
        )
        reason = "problem-path"
    return {
        "base": base_sha,
        "head": head_sha,
        "problems": selected,
        "reason": reason,
    }


def read_at(root: Path, head: str, path: str) -> str:
    if head == "WORKTREE":
        target = (root / path).resolve()
        try:
            target.relative_to(root.resolve())
        except ValueError as exc:
            raise MathFlowError(f"path escapes repository root: {path}") from exc
        return target.read_text(encoding="utf-8")
    return _run_git(root, "show", f"{head}:{path}").stdout


def read_bytes_at(root: Path, head: str, path: str) -> bytes:
    """Read exact repository bytes without passing binary content through text Git I/O."""

    if head == "WORKTREE":
        target = (root / path).resolve()
        try:
            target.relative_to(root.resolve())
        except ValueError as exc:
            raise MathFlowError(f"path escapes repository root: {path}") from exc
        return target.read_bytes()
    try:
        result = subprocess.run(
            ["git", "show", f"{head}:{path}"],
            cwd=root,
            check=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
    except FileNotFoundError as exc:
        raise MathFlowError("Git is required but was not found") from exc
    if result.returncode:
        detail = result.stderr.decode("utf-8", errors="replace").strip()
        raise MathFlowError(f"git show {head}:{path} failed: {detail}")
    return result.stdout


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
    return {
        "problemId": problem,
        "ledgerHead": head,
        "problemLedgerHead": head,
        "problemLedgerDigest": f"sha256:{digest.hexdigest()}",
        "transactions": transactions,
    }


def canonical_json(value: object) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def sha256_json(value: object) -> str:
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()
