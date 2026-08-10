from __future__ import annotations

import json
import re
from pathlib import Path, PurePosixPath
from typing import Callable

from .errors import MathFlowError
from .repository import (
    _parse_name_status,
    _run_git,
    read_at,
    resolve_commit,
    sha256_json,
    validate_slug,
)


PROJECTION_FIELDS = {
    "schemaVersion",
    "id",
    "description",
    "status",
    "engine",
    "allowedProblems",
    "primaryJudge",
    "reconciliationJudge",
    "knowledgeBuilder",
    "scheduling",
}
SCHEDULING_FIELDS = {
    "judgmentMaxParallel",
    "knowledgeMinimumIntervalSeconds",
    "maximumJudgmentsPerBuild",
}
EXPECTED_IMPLEMENTATIONS = {
    "primaryJudge": "openrouter-markdown-judgment-v1",
    "reconciliationJudge": "openrouter-markdown-reconciliation-v1",
    "knowledgeBuilder": "openrouter-knowledge-builder-v1",
}
LOGIN = re.compile(r"^[A-Za-z0-9](?:[A-Za-z0-9-]{0,37}[A-Za-z0-9])?$")


def _json_object(text: str, label: str) -> dict[str, object]:
    try:
        value = json.loads(text)
    except json.JSONDecodeError as exc:
        raise MathFlowError(f"{label} is not valid JSON: {exc}") from exc
    if not isinstance(value, dict):
        raise MathFlowError(f"{label} must be a JSON object")
    return value


def _projection_reference(value: object, label: str) -> str:
    if not isinstance(value, str):
        raise MathFlowError(f"projection {label} must be a repository path")
    parts = PurePosixPath(value).parts
    if (
        len(parts) != 3
        or parts[:2] != ("protocol", "judges")
        or not parts[2].endswith(".json")
    ):
        raise MathFlowError(
            f"projection {label} must name one protocol/judges/*.json file"
        )
    validate_slug(parts[2][:-5], f"projection {label} id")
    return value


def validate_projection_spec(
    value: object,
    projection_id: str,
    read_text: Callable[[str], str],
) -> dict[str, object]:
    if not isinstance(value, dict) or set(value) != PROJECTION_FIELDS:
        raise MathFlowError(
            f"projection {projection_id!r} must contain exactly the supported fields"
        )
    if value.get("schemaVersion") != 1 or value.get("id") != projection_id:
        raise MathFlowError(
            f"projection {projection_id!r} has the wrong schema version or id"
        )
    description = value.get("description")
    if not isinstance(description, str) or not description.strip():
        raise MathFlowError(f"projection {projection_id!r} needs a description")
    if value.get("status") not in {"active", "disabled"}:
        raise MathFlowError(f"projection {projection_id!r} has an invalid status")
    if value.get("engine") != "openrouter-repository-v1":
        raise MathFlowError(f"projection {projection_id!r} uses an unsupported engine")

    allowed = value.get("allowedProblems")
    if not isinstance(allowed, list) or not allowed or any(
        not isinstance(item, str) for item in allowed
    ):
        raise MathFlowError(f"projection {projection_id!r} needs allowedProblems")
    if len(allowed) != len(set(allowed)) or ("*" in allowed and allowed != ["*"]):
        raise MathFlowError(
            f"projection {projection_id!r} allowedProblems must be unique or exactly ['*']"
        )
    for problem in allowed:
        if problem != "*":
            validate_slug(problem, "allowed problem id")

    for field, implementation in EXPECTED_IMPLEMENTATIONS.items():
        reference = _projection_reference(value.get(field), field)
        judge = _json_object(read_text(reference), f"judge specification {reference}")
        if judge.get("implementation") != implementation:
            raise MathFlowError(
                f"projection {projection_id!r} {field} must use {implementation}"
            )

    scheduling = value.get("scheduling")
    if not isinstance(scheduling, dict) or set(scheduling) != SCHEDULING_FIELDS:
        raise MathFlowError(f"projection {projection_id!r} has invalid scheduling policy")
    limits = {
        "judgmentMaxParallel": (1, 256),
        "knowledgeMinimumIntervalSeconds": (0, 86_400),
        "maximumJudgmentsPerBuild": (1, 5_000),
    }
    for field, (minimum, maximum) in limits.items():
        setting = scheduling.get(field)
        if (
            not isinstance(setting, int)
            or isinstance(setting, bool)
            or not minimum <= setting <= maximum
        ):
            raise MathFlowError(
                f"projection {projection_id!r} {field} must be between {minimum} and {maximum}"
            )
    return value


def validate_projection_registry(root: Path) -> dict[str, object]:
    root = root.resolve()
    registry = root / "protocol" / "projections"
    if not registry.exists():
        return {"projections": 0, "active": 0}
    if not registry.is_dir() or registry.is_symlink():
        raise MathFlowError(f"projection registry must be a real directory: {registry}")
    specs: list[dict[str, object]] = []
    for path in sorted(registry.iterdir()):
        if not path.is_file() or path.suffix != ".json" or path.is_symlink():
            raise MathFlowError(
                f"projection registry may only contain JSON files: {path}"
            )
        validate_slug(path.stem, "projection id")
        value = _json_object(
            path.read_text(encoding="utf-8"), f"projection specification {path}"
        )
        specs.append(
            validate_projection_spec(
                value,
                path.stem,
                lambda relative: (root / relative).read_text(encoding="utf-8"),
            )
        )
    return {
        "projections": len(specs),
        "active": sum(spec.get("status") == "active" for spec in specs),
    }


def projection_registry_index(root: Path) -> dict[str, dict[str, object]]:
    """Return active projection metadata keyed by its content digest."""

    root = root.resolve()
    registry = root / "protocol" / "projections"
    if not registry.is_dir():
        return {}
    indexed: dict[str, dict[str, object]] = {}
    for path in sorted(registry.glob("*.json")):
        value = _json_object(
            path.read_text(encoding="utf-8"), f"projection specification {path}"
        )
        spec = validate_projection_spec(
            value,
            path.stem,
            lambda relative: (root / relative).read_text(encoding="utf-8"),
        )
        if spec["status"] != "active":
            continue
        digest = f"sha256:{sha256_json(spec)}"
        indexed[digest] = {
            "id": spec["id"],
            "description": spec["description"],
            "digest": digest,
        }
    return indexed


def resolve_projection(
    root: Path, projection: str, problem: str, head: str = "HEAD"
) -> dict[str, object]:
    root = root.resolve()
    validate_slug(projection, "projection id")
    validate_slug(problem, "problem id")
    resolved_head = "WORKTREE" if head == "WORKTREE" else resolve_commit(root, head)
    path = f"protocol/projections/{projection}.json"
    value = _json_object(
        read_at(root, resolved_head, path), f"projection specification {path}"
    )
    spec = validate_projection_spec(
        value,
        projection,
        lambda relative: read_at(root, resolved_head, relative),
    )
    if spec["status"] != "active":
        raise MathFlowError(f"projection is not active: {projection}")
    allowed = spec["allowedProblems"]
    if "*" not in allowed and problem not in allowed:
        raise MathFlowError(
            f"projection {projection!r} is not approved for problem {problem!r}"
        )
    read_at(root, resolved_head, f"problems/{problem}/problem.md")
    scheduling = spec["scheduling"]
    return {
        "schemaVersion": 1,
        "projectionId": projection,
        "projectionSpecDigest": f"sha256:{sha256_json(spec)}",
        "problemId": problem,
        "canonicalHead": resolved_head,
        "primaryJudge": spec["primaryJudge"],
        "reconciliationJudge": spec["reconciliationJudge"],
        "knowledgeBuilder": spec["knowledgeBuilder"],
        "scheduling": scheduling,
    }


def _validate_policy(value: dict[str, object]) -> dict[str, object]:
    if set(value) != {"schemaVersion", "minimumApprovals", "administrators"}:
        raise MathFlowError("Math Flow governance policy has unsupported fields")
    administrators = value.get("administrators")
    minimum = value.get("minimumApprovals")
    if (
        value.get("schemaVersion") != 1
        or not isinstance(administrators, list)
        or not administrators
        or any(not isinstance(login, str) or not LOGIN.fullmatch(login) for login in administrators)
        or len({login.lower() for login in administrators}) != len(administrators)
        or not isinstance(minimum, int)
        or isinstance(minimum, bool)
        or not 1 <= minimum <= len(administrators)
    ):
        raise MathFlowError("Math Flow governance policy is invalid")
    return value


def _load_policy(root: Path, base_sha: str) -> dict[str, object]:
    value = _json_object(
        read_at(root, base_sha, ".github/math-flow-governance.json"),
        "Math Flow governance policy",
    )
    return _validate_policy(value)


def validate_admission_pr(
    root: Path,
    base: str,
    head: str,
    approvers: list[str] | None = None,
) -> dict[str, object]:
    """Validate a governance-sensitive PR and its current-head admin approvals.

    Ordinary contribution PRs and unrelated maintenance PRs are intentionally
    outside this admission check. Existing required checks continue to govern them.
    """

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

    problem_changes = []
    projection_changes = []
    policy_changes = []
    def governed_kind(path: str) -> str | None:
        parts = PurePosixPath(path).parts
        if len(parts) == 3 and parts[0] == "problems" and parts[2] == "problem.md":
            return "problem"
        if (
            len(parts) == 3
            and parts[:2] == ("protocol", "projections")
            and parts[2].endswith(".json")
        ):
            return "projection"
        if path in {
            ".github/math-flow-governance.json",
            ".github/CODEOWNERS",
            ".github/workflows/admission-control.yml",
        }:
            return "policy"
        return None

    change_indexes = {
        "problem": problem_changes,
        "projection": projection_changes,
        "policy": policy_changes,
    }
    for change in changes:
        kinds = {
            kind
            for candidate in (change.path, change.old_path)
            if candidate is not None
            if (kind := governed_kind(candidate)) is not None
        }
        for kind in kinds:
            change_indexes[kind].append(change)

    categories = [
        ("problem", problem_changes),
        ("projection", projection_changes),
        ("policy", policy_changes),
    ]
    active = [(kind, items) for kind, items in categories if items]
    if not active:
        return {
            "base": base_sha,
            "head": head_sha,
            "admissionType": "not-applicable",
            "approvalRequired": False,
        }
    if len(active) != 1 or len(changes) != 1 or len(active[0][1]) != 1:
        raise MathFlowError(
            "problem, projection, and governance-policy admissions must use separate one-file PRs"
        )

    kind, items = active[0]
    change = items[0]
    if change.status == "D" or change.status.startswith(("R", "C")):
        raise MathFlowError("governed definitions must be disabled or edited, not deleted or renamed")
    subject_id: str
    if kind == "problem":
        subject_id = PurePosixPath(change.path).parts[1]
        validate_slug(subject_id, "problem id")
        if change.status == "A":
            parent = f"problems/{subject_id}"
            if _run_git(root, "cat-file", "-e", f"{base_sha}:{parent}", check=False).returncode == 0:
                raise MathFlowError("new problem statement is inside an existing problem directory")
        statement = read_at(root, head_sha, change.path)
        if not statement.strip():
            raise MathFlowError("problem statement must contain text")
    elif kind == "projection":
        subject_id = Path(change.path).stem
        validate_slug(subject_id, "projection id")
        value = _json_object(
            read_at(root, head_sha, change.path),
            f"projection specification {change.path}",
        )
        validate_projection_spec(
            value,
            subject_id,
            lambda relative: read_at(root, head_sha, relative),
        )
    else:
        subject_id = PurePosixPath(change.path).name
        if change.path == ".github/math-flow-governance.json":
            policy = _json_object(
                read_at(root, head_sha, change.path),
                "candidate Math Flow governance policy",
            )
            _validate_policy(policy)

    policy = _load_policy(root, base_sha)
    administrator_map = {
        str(login).lower(): str(login) for login in policy["administrators"]
    }
    matched = sorted(
        {
            administrator_map[login.lower()]
            for login in (approvers or [])
            if login.lower() in administrator_map
        },
        key=str.lower,
    )
    required = int(policy["minimumApprovals"])
    if len(matched) < required:
        raise MathFlowError(
            f"{kind} admission needs {required} current-head admin approval(s); found {len(matched)}"
        )
    return {
        "base": base_sha,
        "head": head_sha,
        "admissionType": kind,
        "subjectId": subject_id,
        "approvalRequired": True,
        "requiredApprovals": required,
        "approvedBy": matched,
    }
