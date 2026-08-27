from __future__ import annotations

import json
import re
from pathlib import Path, PurePosixPath
from typing import Callable

from .artifacts import sha256_bytes
from .errors import MathFlowError
from .problem_registry import (
    PROBLEM_REGISTRY_PATH,
    canonical_problem_ids,
    problem_status,
    validate_problem_registry,
)
from .repository import (
    _parse_name_status,
    _run_git,
    list_files_at,
    read_at,
    resolve_commit,
    sha256_json,
    validate_slug,
)


KNOWLEDGE_PROJECTION_REQUIRED_FIELDS = {
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
KNOWLEDGE_PROJECTION_OPTIONAL_FIELDS = {"dependencies"}
OVERLAY_PROJECTION_FIELDS = {
    "schemaVersion",
    "id",
    "description",
    "status",
    "engine",
    "allowedProblems",
    "runner",
    "dependencies",
    "scheduling",
}
OVERLAY_RUNNER_FIELDS = {"implementation", "spec"}
OVERLAY_SCHEDULING_REQUIRED_FIELDS = {"minimumIntervalSeconds"}
OVERLAY_SCHEDULING_OPTIONAL_FIELDS = {"utcCalendarPeriod"}
OVERLAY_IMPLEMENTATIONS = {
    "openrouter-credit-assignment-v1",
    "openrouter-credit-assignment-v2",
    "openrouter-hierarchical-research-credit-v2",
    "openrouter-work-accounting-v1",
    "openrouter-work-accounting-v2",
}
PROJECTION_DEPENDENCY_FIELDS = {"name", "projectionId", "artifactRole"}
ARTIFACT_ROLE = re.compile(r"^[a-z0-9][a-z0-9-]*$")
SCHEDULING_FIELDS = {
    "judgmentMaxParallel",
    "knowledgeMinimumIntervalSeconds",
    "maximumJudgmentsPerBuild",
}
EXPECTED_IMPLEMENTATIONS = {
    "primaryJudge": {
        "openrouter-markdown-judgment-v1",
        "openrouter-validity-judgment-v2",
        "openrouter-validity-judgment-v3",
        "openrouter-validity-judgment-v4",
    },
    "reconciliationJudge": {"openrouter-markdown-reconciliation-v1"},
    "knowledgeBuilder": {
        "openrouter-knowledge-builder-v1",
        "openrouter-knowledge-builder-v2",
        "openrouter-knowledge-builder-v3",
        "openrouter-hierarchical-research-builder-v2",
        "openrouter-hierarchical-research-builder-v3",
        "openrouter-hierarchical-research-builder-v4",
        "openrouter-hierarchical-research-builder-v5",
        "openrouter-hierarchical-research-builder-v6",
    },
}
LOGIN = re.compile(r"^[A-Za-z0-9](?:[A-Za-z0-9-]{0,37}[A-Za-z0-9])?$")
FULL_GIT_SHA = re.compile(r"^[0-9a-f]{40}$")
ADMISSION_APPROVAL_COMMAND = re.compile(
    r"^/approve-admission ([0-9a-fA-F]{40})$"
)


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
    if not isinstance(value, dict):
        raise MathFlowError(
            f"projection {projection_id!r} has unsupported or missing fields"
        )
    schema_version = value.get("schemaVersion")
    if (
        not isinstance(schema_version, int)
        or isinstance(schema_version, bool)
        or schema_version not in {1, 2}
        or value.get("id") != projection_id
    ):
        raise MathFlowError(
            f"projection {projection_id!r} has the wrong schema version or id"
        )
    if schema_version == 1:
        if (
            not KNOWLEDGE_PROJECTION_REQUIRED_FIELDS <= set(value)
            or not set(value)
            <= KNOWLEDGE_PROJECTION_REQUIRED_FIELDS
            | KNOWLEDGE_PROJECTION_OPTIONAL_FIELDS
        ):
            raise MathFlowError(
                f"projection {projection_id!r} has unsupported or missing fields"
            )
    elif set(value) != OVERLAY_PROJECTION_FIELDS:
        raise MathFlowError(
            f"projection {projection_id!r} has unsupported or missing fields"
        )

    description = value.get("description")
    if not isinstance(description, str) or not description.strip():
        raise MathFlowError(f"projection {projection_id!r} needs a description")
    if value.get("status") not in {"active", "disabled"}:
        raise MathFlowError(f"projection {projection_id!r} has an invalid status")
    expected_engine = (
        "openrouter-repository-v1"
        if schema_version == 1
        else "overlay-repository-v1"
    )
    if value.get("engine") != expected_engine:
        raise MathFlowError(
            f"projection {projection_id!r} uses an unsupported engine"
        )

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

    dependencies = value.get("dependencies", [])
    if not isinstance(dependencies, list) or any(
        not isinstance(item, dict) or set(item) != PROJECTION_DEPENDENCY_FIELDS
        for item in dependencies
    ):
        raise MathFlowError(
            f"projection {projection_id!r} has invalid dependencies"
        )
    dependency_names: set[str] = set()
    dependency_targets: set[tuple[str, str]] = set()
    for dependency in dependencies:
        name = dependency.get("name")
        target = dependency.get("projectionId")
        role = dependency.get("artifactRole")
        if not isinstance(name, str):
            raise MathFlowError(
                f"projection {projection_id!r} dependency name must be a slug"
            )
        validate_slug(name, "projection dependency name")
        if not isinstance(target, str):
            raise MathFlowError(
                f"projection {projection_id!r} dependency projectionId must be a slug"
            )
        validate_slug(target, "projection dependency projection id")
        if target == projection_id:
            raise MathFlowError(
                f"projection {projection_id!r} cannot depend on itself"
            )
        if not isinstance(role, str) or not ARTIFACT_ROLE.fullmatch(role):
            raise MathFlowError(
                f"projection {projection_id!r} dependency artifactRole must be a slug"
            )
        if name in dependency_names:
            raise MathFlowError(
                f"projection {projection_id!r} dependency names must be unique"
            )
        target_key = (target, role)
        if target_key in dependency_targets:
            raise MathFlowError(
                f"projection {projection_id!r} repeats a dependency target and artifact role"
            )
        dependency_names.add(name)
        dependency_targets.add(target_key)

    if schema_version == 2:
        if not dependencies:
            raise MathFlowError(
                f"overlay projection {projection_id!r} needs at least one dependency"
            )
        runner = value.get("runner")
        if not isinstance(runner, dict) or set(runner) != OVERLAY_RUNNER_FIELDS:
            raise MathFlowError(
                f"overlay projection {projection_id!r} has an invalid runner"
            )
        implementation = runner.get("implementation")
        if implementation not in OVERLAY_IMPLEMENTATIONS:
            raise MathFlowError(
                f"overlay projection {projection_id!r} uses an unsupported runner"
            )
        reference = _projection_reference(runner.get("spec"), "runner spec")
        runner_spec = _json_object(
            read_text(reference), f"overlay runner specification {reference}"
        )
        if runner_spec.get("implementation") != implementation:
            raise MathFlowError(
                f"overlay projection {projection_id!r} runner does not match its spec"
            )
        work_version_suffix = {
            "openrouter-work-accounting-v1": "-v1",
            "openrouter-work-accounting-v2": "-v2",
        }.get(str(implementation))
        if work_version_suffix is not None and not projection_id.endswith(
            work_version_suffix
        ):
            raise MathFlowError(
                f"overlay projection {projection_id!r} ID and work profile version disagree"
            )
        if implementation == "openrouter-work-accounting-v2":
            policy = runner_spec.get("policy")
            if (
                not isinstance(policy, dict)
                or set(policy) != {"path", "digest"}
                or policy.get("path")
                != "protocol/policies/hierarchical-work-remaining-accounting-v2.md"
                or not isinstance(policy.get("digest"), str)
                or not re.fullmatch(r"sha256:[0-9a-f]{64}", str(policy["digest"]))
            ):
                raise MathFlowError(
                    f"overlay projection {projection_id!r} has an invalid V2 policy binding"
                )
            try:
                policy_bytes = read_text(str(policy["path"])).encode("utf-8")
            except (OSError, UnicodeError) as exc:
                raise MathFlowError(
                    f"overlay projection {projection_id!r} could not read its V2 policy"
                ) from exc
            if sha256_bytes(policy_bytes) != policy["digest"]:
                raise MathFlowError(
                    f"overlay projection {projection_id!r} V2 policy digest mismatch"
                )
        scheduling = value.get("scheduling")
        if (
            not isinstance(scheduling, dict)
            or not OVERLAY_SCHEDULING_REQUIRED_FIELDS <= set(scheduling)
            or not set(scheduling)
            <= OVERLAY_SCHEDULING_REQUIRED_FIELDS
            | OVERLAY_SCHEDULING_OPTIONAL_FIELDS
        ):
            raise MathFlowError(
                f"overlay projection {projection_id!r} has invalid scheduling policy"
            )
        interval = scheduling.get("minimumIntervalSeconds")
        if (
            not isinstance(interval, int)
            or isinstance(interval, bool)
            or not 0 <= interval <= 86_400
        ):
            raise MathFlowError(
                f"overlay projection {projection_id!r} minimumIntervalSeconds "
                "must be between 0 and 86400"
            )
        period = scheduling.get("utcCalendarPeriod")
        if period is not None and (
            not isinstance(period, dict)
            or set(period) != {"unit"}
            or period.get("unit") not in {"hour", "day"}
        ):
            raise MathFlowError(
                f"overlay projection {projection_id!r} utcCalendarPeriod must "
                "select exactly one of 'hour' or 'day'"
            )
        if (
            isinstance(period, dict)
            and period.get("unit") == "hour"
            and interval > 3_600
        ):
            raise MathFlowError(
                f"overlay projection {projection_id!r} minimumIntervalSeconds "
                "cannot exceed its UTC calendar period"
            )
        return value

    resolved_implementations: dict[str, str | None] = {}
    for field, implementations in EXPECTED_IMPLEMENTATIONS.items():
        raw_reference = value.get(field)
        if field == "reconciliationJudge" and raw_reference is None:
            resolved_implementations[field] = None
            continue
        reference = _projection_reference(raw_reference, field)
        judge = _json_object(read_text(reference), f"judge specification {reference}")
        implementation = judge.get("implementation")
        if implementation not in implementations:
            raise MathFlowError(
                f"projection {projection_id!r} {field} must use one of "
                f"{', '.join(sorted(implementations))}"
            )
        resolved_implementations[field] = str(implementation)

    reconciliation = resolved_implementations["reconciliationJudge"]
    primary = resolved_implementations["primaryJudge"]
    builder = resolved_implementations["knowledgeBuilder"]
    validity_research_pair = (
        primary,
        builder,
    ) in {
        (
            "openrouter-validity-judgment-v2",
            "openrouter-hierarchical-research-builder-v2",
        ),
        (
            "openrouter-validity-judgment-v3",
            "openrouter-hierarchical-research-builder-v3",
        ),
        (
            "openrouter-validity-judgment-v4",
            "openrouter-hierarchical-research-builder-v4",
        ),
        (
            "openrouter-validity-judgment-v4",
            "openrouter-hierarchical-research-builder-v5",
        ),
        (
            "openrouter-validity-judgment-v4",
            "openrouter-hierarchical-research-builder-v6",
        ),
    }
    if reconciliation is None and not validity_research_pair:
        raise MathFlowError(
            f"projection {projection_id!r} may omit reconciliation only for the "
            "version-matched validity hierarchical research pipeline"
        )
    if builder in {
        "openrouter-hierarchical-research-builder-v2",
        "openrouter-hierarchical-research-builder-v3",
        "openrouter-hierarchical-research-builder-v4",
        "openrouter-hierarchical-research-builder-v5",
        "openrouter-hierarchical-research-builder-v6",
    } and (not validity_research_pair or reconciliation is not None):
        raise MathFlowError(
            f"projection {projection_id!r} hierarchical research builder requires "
            "version-matched validity primary judgments and no reconciliation stage"
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


def _validate_projection_graph(specs: dict[str, dict[str, object]]) -> None:
    """Validate dependency references, problem coverage, and acyclicity."""

    adjacency: dict[str, list[str]] = {}
    for projection_id, spec in specs.items():
        targets: list[str] = []
        consumer_allowed = set(spec["allowedProblems"])
        for dependency in spec.get("dependencies", []):
            target_id = str(dependency["projectionId"])
            target = specs.get(target_id)
            if target is None:
                raise MathFlowError(
                    f"projection {projection_id!r} depends on unknown projection {target_id!r}"
                )
            producer_allowed = set(target["allowedProblems"])
            covered = (
                "*" in producer_allowed
                or (
                    "*" not in consumer_allowed
                    and consumer_allowed <= producer_allowed
                )
            )
            if not covered:
                raise MathFlowError(
                    f"projection {projection_id!r} dependency {target_id!r} "
                    "does not cover every allowed problem"
                )
            targets.append(target_id)
        adjacency[projection_id] = targets

    visiting: set[str] = set()
    visited: set[str] = set()

    def visit(projection_id: str) -> None:
        if projection_id in visiting:
            raise MathFlowError(
                f"projection dependency graph contains a cycle at {projection_id!r}"
            )
        if projection_id in visited:
            return
        visiting.add(projection_id)
        for target_id in adjacency[projection_id]:
            visit(target_id)
        visiting.remove(projection_id)
        visited.add(projection_id)

    for projection_id in sorted(adjacency):
        visit(projection_id)


def _worktree_projection_specs(root: Path) -> dict[str, dict[str, object]]:
    registry = root / "protocol" / "projections"
    if not registry.exists():
        return {}
    if not registry.is_dir() or registry.is_symlink():
        raise MathFlowError(f"projection registry must be a real directory: {registry}")
    specs: dict[str, dict[str, object]] = {}
    for path in sorted(registry.iterdir()):
        if not path.is_file() or path.suffix != ".json" or path.is_symlink():
            raise MathFlowError(
                f"projection registry may only contain JSON files: {path}"
            )
        validate_slug(path.stem, "projection id")
        value = _json_object(
            path.read_text(encoding="utf-8"), f"projection specification {path}"
        )
        specs[path.stem] = validate_projection_spec(
            value,
            path.stem,
            lambda relative: (root / relative).read_text(encoding="utf-8"),
        )
    _validate_projection_graph(specs)
    return specs


def _projection_specs_at(
    root: Path, resolved_head: str
) -> dict[str, dict[str, object]]:
    specs: dict[str, dict[str, object]] = {}
    for path in list_files_at(root, resolved_head, "protocol/projections"):
        parts = PurePosixPath(path).parts
        if (
            len(parts) != 3
            or parts[:2] != ("protocol", "projections")
            or not parts[2].endswith(".json")
        ):
            raise MathFlowError(
                f"projection registry may only contain JSON files: {path}"
            )
        projection_id = parts[2][:-5]
        validate_slug(projection_id, "projection id")
        value = _json_object(
            read_at(root, resolved_head, path),
            f"projection specification {path}",
        )
        specs[projection_id] = validate_projection_spec(
            value,
            projection_id,
            lambda relative: read_at(root, resolved_head, relative),
        )
    _validate_projection_graph(specs)
    return specs


def validate_projection_registry(root: Path) -> dict[str, object]:
    root = root.resolve()
    specs = _worktree_projection_specs(root)
    return {
        "projections": len(specs),
        "active": sum(spec.get("status") == "active" for spec in specs.values()),
    }


def projection_registry_index(root: Path) -> dict[str, dict[str, object]]:
    """Return active projection metadata keyed by its content digest."""

    root = root.resolve()
    specs = _worktree_projection_specs(root)
    indexed: dict[str, dict[str, object]] = {}
    for spec in specs.values():
        if spec["status"] != "active":
            continue
        digest = f"sha256:{sha256_json(spec)}"
        indexed[digest] = {
            "id": spec["id"],
            "description": spec["description"],
            "digest": digest,
            "engine": spec["engine"],
            "allowedProblems": spec["allowedProblems"],
            "dependencies": spec.get("dependencies", []),
            "scheduling": spec["scheduling"],
            "runner": spec.get("runner"),
        }
    return indexed


def resolve_projection(
    root: Path, projection: str, problem: str, head: str = "HEAD"
) -> dict[str, object]:
    root = root.resolve()
    validate_slug(projection, "projection id")
    validate_slug(problem, "problem id")
    resolved_head = "WORKTREE" if head == "WORKTREE" else resolve_commit(root, head)
    specs = (
        _worktree_projection_specs(root)
        if resolved_head == "WORKTREE"
        else _projection_specs_at(root, resolved_head)
    )
    spec = specs.get(projection)
    if spec is None:
        raise MathFlowError(f"unknown projection: {projection}")
    if spec["status"] != "active":
        raise MathFlowError(f"projection is not active: {projection}")
    if problem_status(root, problem, resolved_head) == "archived":
        raise MathFlowError(f"problem is archived: {problem}")
    allowed = spec["allowedProblems"]
    if "*" not in allowed and problem not in allowed:
        raise MathFlowError(
            f"projection {projection!r} is not approved for problem {problem!r}"
        )
    read_at(root, resolved_head, f"problems/{problem}/problem.md")
    dependencies: list[dict[str, object]] = []
    for dependency in spec.get("dependencies", []):
        target_id = str(dependency["projectionId"])
        target = specs[target_id]
        target_allowed = target["allowedProblems"]
        if target["status"] != "active":
            raise MathFlowError(
                f"projection {projection!r} dependency is not active: {target_id}"
            )
        if "*" not in target_allowed and problem not in target_allowed:
            raise MathFlowError(
                f"projection {projection!r} dependency {target_id!r} is not "
                f"approved for problem {problem!r}"
            )
        dependencies.append(
            {
                "name": dependency["name"],
                "projectionId": target_id,
                "projectionSpecDigest": f"sha256:{sha256_json(target)}",
                "artifactRole": dependency["artifactRole"],
            }
        )
    resolved: dict[str, object] = {
        "schemaVersion": 1,
        "projectionId": projection,
        "projectionSpecDigest": f"sha256:{sha256_json(spec)}",
        "problemId": problem,
        "canonicalHead": resolved_head,
        "engine": spec["engine"],
        "dependencies": dependencies,
        "scheduling": spec["scheduling"],
    }
    if spec["schemaVersion"] == 1:
        primary_judge = _json_object(
            read_at(root, resolved_head, str(spec["primaryJudge"])),
            f"primary judge specification {spec['primaryJudge']}",
        )
        primary_judge_digest = f"sha256:{sha256_json(primary_judge)}"
        stream_core = {
            "problemId": problem,
            "primaryJudgeDigest": primary_judge_digest,
        }
        resolved.update(
            {
                "primaryJudge": spec["primaryJudge"],
                "primaryJudgeDigest": primary_judge_digest,
                "judgmentStreamId": f"sha256:{sha256_json(stream_core)}",
                "reconciliationJudge": spec["reconciliationJudge"],
                "knowledgeBuilder": spec["knowledgeBuilder"],
            }
        )
    else:
        resolved["runner"] = spec["runner"]
    return resolved


def list_active_projections(
    root: Path,
    problem: str,
    head: str = "HEAD",
    engine: str | None = None,
) -> dict[str, object]:
    """Resolve every active projection approved for a problem at one commit."""

    root = root.resolve()
    validate_slug(problem, "problem id")
    resolved_head = "WORKTREE" if head == "WORKTREE" else resolve_commit(root, head)
    read_at(root, resolved_head, f"problems/{problem}/problem.md")
    status = problem_status(root, problem, resolved_head)
    if status == "archived":
        return {
            "schemaVersion": 1,
            "problemId": problem,
            "problemStatus": status,
            "canonicalHead": resolved_head,
            "projections": [],
        }
    specs = (
        _worktree_projection_specs(root)
        if resolved_head == "WORKTREE"
        else _projection_specs_at(root, resolved_head)
    )
    projection_ids: list[str] = []
    for projection_id, spec in specs.items():
        allowed = spec["allowedProblems"]
        if (
            spec["status"] == "active"
            and ("*" in allowed or problem in allowed)
            and (engine is None or spec["engine"] == engine)
        ):
            projection_ids.append(projection_id)
    projections = [
        resolve_projection(root, projection_id, problem, resolved_head)
        for projection_id in sorted(projection_ids)
    ]
    return {
        "schemaVersion": 1,
        "problemId": problem,
        "problemStatus": status,
        "canonicalHead": resolved_head,
        "projections": projections,
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


def head_bound_comment_approvers(
    head_sha: str,
    comments: object | None,
) -> list[str]:
    """Return authors of exact approval commands bound to ``head_sha``.

    The caller supplies a current snapshot of PR comments normalized to
    ``{"author": <GitHub login>, "body": <comment text>}`` objects. Deleted
    comments are therefore absent, edited comments expose only their current
    body, and commands for an older PR head cannot authorize a newer one.
    """

    if not FULL_GIT_SHA.fullmatch(head_sha):
        raise MathFlowError("admission approval head must be a full Git SHA")
    if comments is None:
        return []
    if not isinstance(comments, list):
        raise MathFlowError("admission approval comments must be a JSON array")

    approvers: set[str] = set()
    for index, comment in enumerate(comments):
        if (
            not isinstance(comment, dict)
            or set(comment) != {"author", "body"}
            or not isinstance(comment.get("author"), str)
            or not LOGIN.fullmatch(str(comment["author"]))
            or not isinstance(comment.get("body"), str)
        ):
            raise MathFlowError(
                f"admission approval comment {index} has an invalid shape"
            )
        command = ADMISSION_APPROVAL_COMMAND.fullmatch(
            str(comment["body"]).strip()
        )
        if command is not None and command.group(1).lower() == head_sha:
            approvers.add(str(comment["author"]))
    return sorted(approvers, key=str.lower)


def validate_admission_pr(
    root: Path,
    base: str,
    head: str,
    approvers: list[str] | None = None,
    approval_comments: object | None = None,
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
    problem_registry_changes = []
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
        if path == PROBLEM_REGISTRY_PATH:
            return "problem-registry"
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
        "problem-registry": problem_registry_changes,
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
        ("problem-registry", problem_registry_changes),
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
            "problem, problem-registry, projection, and governance-policy admissions must use separate one-file PRs"
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
    elif kind == "problem-registry":
        subject_id = "problem-registry"
        value = _json_object(
            read_at(root, head_sha, change.path),
            "candidate problem registry",
        )
        validate_problem_registry(value, canonical_problem_ids(root, head_sha))
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
    supplied_approvers = list(approvers or [])
    supplied_approvers.extend(
        head_bound_comment_approvers(head_sha, approval_comments)
    )
    matched = sorted(
        {
            administrator_map[login.lower()]
            for login in supplied_approvers
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
