from __future__ import annotations

import copy
import json
from pathlib import Path
from pathlib import PurePosixPath

from .artifacts import verify_bundle
from .coordination import DIGEST, MAX_AUTOMATIC_FAILURES, lane_id
from .errors import MathFlowError
from .governance import list_active_projections
from .repository import (
    ledger,
    list_files_at,
    read_at,
    resolve_commit,
    sha256_json,
    validate_slug,
    worktree_ledger,
)


_LANE_FIELDS = {
    "laneId",
    "problemId",
    "builderSpecDigest",
    "minimumIntervalSeconds",
    "latestStateRun",
    "lastCompletedAt",
    "nextEligibleAt",
    "observedJudgmentIds",
    "observedConflictIds",
    "pendingJudgmentIds",
    "pendingConflictIds",
    "activeBuild",
}
_OPTIONAL_LANE_FIELDS = {
    "conflictDependencies",
    "judgmentDependencies",
    "lastFailure",
    "reconciliationDependencies",
}
_ACTIVE_BUILD_FIELDS = {
    "schemaVersion",
    "laneId",
    "problemId",
    "builderSpecDigest",
    "baseStateRun",
    "judgmentIds",
    "conflictIds",
    "judgmentSetDigest",
    "buildToken",
    "claimedAt",
}
_LAST_FAILURE_FIELDS = {
    "schemaVersion",
    "laneId",
    "buildToken",
    "problemLedgerDigest",
    "failedAt",
    "consecutiveFailures",
    "retryNotBefore",
}


def _digest(value: object, label: str) -> str:
    if not isinstance(value, str) or not DIGEST.fullmatch(value):
        raise MathFlowError(f"{label} must be a SHA-256 digest")
    return value


def _optional_digest(value: object, label: str) -> str | None:
    if value is None:
        return None
    return _digest(value, label)


def _nonnegative_integer(value: object, label: str) -> int:
    if not isinstance(value, int) or isinstance(value, bool) or value < 0:
        raise MathFlowError(f"{label} must be a nonnegative integer")
    return value


def _optional_time(value: object, label: str) -> int | None:
    if value is None:
        return None
    return _nonnegative_integer(value, label)


def _digest_list(value: object, label: str) -> list[str]:
    if not isinstance(value, list):
        raise MathFlowError(f"{label} must be a list")
    digests = [_digest(item, f"{label} item") for item in value]
    if digests != sorted(set(digests)):
        raise MathFlowError(f"{label} must contain unique digests in sorted order")
    return digests


def _validate_active_build(
    value: object,
    lane: dict[str, object],
    label: str,
) -> dict[str, object] | None:
    if value is None:
        return None
    if not isinstance(value, dict):
        raise MathFlowError(f"{label} must be an object or null")
    expected_fields = set(_ACTIVE_BUILD_FIELDS)
    projection_digest = lane.get("projectionSpecDigest")
    if projection_digest is not None:
        expected_fields.add("projectionSpecDigest")
    if set(value) != expected_fields:
        raise MathFlowError(f"{label} has unsupported or missing fields")
    if value.get("schemaVersion") != 1 or isinstance(value.get("schemaVersion"), bool):
        raise MathFlowError(f"{label} has an unsupported schema version")
    for field in ("laneId", "problemId", "builderSpecDigest"):
        if value.get(field) != lane[field]:
            raise MathFlowError(f"{label} {field} does not match its lane")
    if value.get("projectionSpecDigest") != projection_digest:
        raise MathFlowError(f"{label} projectionSpecDigest does not match its lane")

    base_state = _optional_digest(value.get("baseStateRun"), f"{label} baseStateRun")
    if base_state != lane.get("latestStateRun"):
        raise MathFlowError(f"{label} baseStateRun does not match its lane")
    judgments = _digest_list(value.get("judgmentIds"), f"{label} judgmentIds")
    conflicts = _digest_list(value.get("conflictIds"), f"{label} conflictIds")
    if not judgments and not conflicts:
        raise MathFlowError(f"{label} cannot claim an empty build")
    expected_set_digest = f"sha256:{sha256_json({'judgmentIds': judgments, 'conflictIds': conflicts})}"
    if value.get("judgmentSetDigest") != expected_set_digest:
        raise MathFlowError(f"{label} has an invalid judgmentSetDigest")

    request_core = {
        key: item
        for key, item in value.items()
        if key not in {"buildToken", "claimedAt"}
    }
    expected_token = f"sha256:{sha256_json(request_core)}"
    if value.get("buildToken") != expected_token:
        raise MathFlowError(f"{label} has an invalid buildToken")
    _nonnegative_integer(value.get("claimedAt"), f"{label} claimedAt")
    return value


def _validate_last_failure(
    value: object,
    lane: dict[str, object],
    label: str,
) -> dict[str, object] | None:
    if value is None:
        return None
    if not isinstance(value, dict) or set(value) != _LAST_FAILURE_FIELDS:
        raise MathFlowError(f"{label} has unsupported or missing fields")
    if value.get("schemaVersion") != 1 or isinstance(
        value.get("schemaVersion"), bool
    ):
        raise MathFlowError(f"{label} has an unsupported schema version")
    if value.get("laneId") != lane["laneId"]:
        raise MathFlowError(f"{label} does not match its lane")
    _digest(value.get("buildToken"), f"{label} buildToken")
    _optional_digest(
        value.get("problemLedgerDigest"), f"{label} problemLedgerDigest"
    )
    failed_at = _nonnegative_integer(value.get("failedAt"), f"{label} failedAt")
    count = value.get("consecutiveFailures")
    if not isinstance(count, int) or isinstance(count, bool) or count <= 0:
        raise MathFlowError(f"{label} consecutiveFailures must be a positive integer")
    retry = _nonnegative_integer(
        value.get("retryNotBefore"), f"{label} retryNotBefore"
    )
    if retry <= failed_at:
        raise MathFlowError(f"{label} retryNotBefore must follow failedAt")
    return value


def _validate_lane(identifier: str, value: object) -> dict[str, object]:
    _digest(identifier, "knowledge scheduler lane key")
    if not isinstance(value, dict):
        raise MathFlowError(f"knowledge scheduler lane {identifier} must be an object")
    expected_fields = set(_LANE_FIELDS)
    if "projectionSpecDigest" in value:
        expected_fields.add("projectionSpecDigest")
    expected_fields.update(set(value) & _OPTIONAL_LANE_FIELDS)
    if set(value) != expected_fields:
        raise MathFlowError(
            f"knowledge scheduler lane {identifier} has unsupported or missing fields"
        )
    if value.get("laneId") != identifier:
        raise MathFlowError(f"knowledge scheduler lane {identifier} has a mismatched laneId")

    problem = value.get("problemId")
    if not isinstance(problem, str):
        raise MathFlowError(f"knowledge scheduler lane {identifier} has an invalid problemId")
    validate_slug(problem, "knowledge scheduler problem id")
    builder_digest = _digest(
        value.get("builderSpecDigest"),
        f"knowledge scheduler lane {identifier} builderSpecDigest",
    )
    projection_digest = value.get("projectionSpecDigest")
    if "projectionSpecDigest" in value:
        projection_digest = _digest(
            projection_digest,
            f"knowledge scheduler lane {identifier} projectionSpecDigest",
        )
    expected_identifier = lane_id(problem, builder_digest, projection_digest)
    if identifier != expected_identifier:
        raise MathFlowError(
            f"knowledge scheduler lane {identifier} does not match its identity fields"
        )

    _nonnegative_integer(
        value.get("minimumIntervalSeconds"),
        f"knowledge scheduler lane {identifier} minimumIntervalSeconds",
    )
    latest_state = _optional_digest(
        value.get("latestStateRun"),
        f"knowledge scheduler lane {identifier} latestStateRun",
    )
    last_completed = _optional_time(
        value.get("lastCompletedAt"),
        f"knowledge scheduler lane {identifier} lastCompletedAt",
    )
    if (latest_state is None) != (last_completed is None):
        raise MathFlowError(
            f"knowledge scheduler lane {identifier} must pair latestStateRun and lastCompletedAt"
        )
    next_eligible = _optional_time(
        value.get("nextEligibleAt"),
        f"knowledge scheduler lane {identifier} nextEligibleAt",
    )

    observed_judgments = _digest_list(
        value.get("observedJudgmentIds"),
        f"knowledge scheduler lane {identifier} observedJudgmentIds",
    )
    observed_conflicts = _digest_list(
        value.get("observedConflictIds"),
        f"knowledge scheduler lane {identifier} observedConflictIds",
    )
    pending_judgments = _digest_list(
        value.get("pendingJudgmentIds"),
        f"knowledge scheduler lane {identifier} pendingJudgmentIds",
    )
    pending_conflicts = _digest_list(
        value.get("pendingConflictIds"),
        f"knowledge scheduler lane {identifier} pendingConflictIds",
    )
    if not set(pending_judgments).issubset(observed_judgments):
        raise MathFlowError(
            f"knowledge scheduler lane {identifier} has unobserved pending judgments"
        )
    if not set(pending_conflicts).issubset(observed_conflicts):
        raise MathFlowError(
            f"knowledge scheduler lane {identifier} has unobserved pending conflicts"
        )

    raw_judgment_dependencies = value.get("judgmentDependencies")
    if raw_judgment_dependencies is not None:
        if not isinstance(raw_judgment_dependencies, dict):
            raise MathFlowError(
                f"knowledge scheduler lane {identifier} judgmentDependencies must be an object"
            )
        adjacency: dict[str, list[str]] = {}
        for judgment_id, inputs in raw_judgment_dependencies.items():
            if not isinstance(judgment_id, str):
                raise MathFlowError(
                    f"knowledge scheduler lane {identifier} judgment dependency keys must be strings"
                )
            _digest(judgment_id, "knowledge scheduler dependent judgment ID")
            input_ids = _digest_list(
                inputs,
                f"knowledge scheduler lane {identifier} judgment dependency inputs",
            )
            if judgment_id not in observed_judgments:
                raise MathFlowError(
                    f"knowledge scheduler lane {identifier} has an unobserved judgment dependency"
                )
            if judgment_id in input_ids:
                raise MathFlowError(
                    f"knowledge scheduler lane {identifier} has a self-dependent judgment"
                )
            if not set(input_ids).issubset(observed_judgments):
                raise MathFlowError(
                    f"knowledge scheduler lane {identifier} judgment dependency has unobserved inputs"
                )
            adjacency[judgment_id] = input_ids

        visiting: set[str] = set()
        visited: set[str] = set()

        def visit(judgment_id: str) -> None:
            if judgment_id in visiting:
                raise MathFlowError(
                    f"knowledge scheduler lane {identifier} judgment dependency graph has a cycle"
                )
            if judgment_id in visited:
                return
            visiting.add(judgment_id)
            for dependency_id in adjacency.get(judgment_id, []):
                visit(dependency_id)
            visiting.remove(judgment_id)
            visited.add(judgment_id)

        for judgment_id in sorted(adjacency):
            visit(judgment_id)

    conflict_dependencies: dict[str, list[str]] = {}
    raw_conflict_dependencies = value.get("conflictDependencies")
    raw_reconciliation_dependencies = value.get("reconciliationDependencies")
    if (raw_conflict_dependencies is None) != (
        raw_reconciliation_dependencies is None
    ):
        raise MathFlowError(
            f"knowledge scheduler lane {identifier} must pair dependency maps"
        )
    if raw_conflict_dependencies is not None:
        if not isinstance(raw_conflict_dependencies, dict):
            raise MathFlowError(
                f"knowledge scheduler lane {identifier} conflictDependencies must be an object"
            )
        for conflict_id, inputs in raw_conflict_dependencies.items():
            if not isinstance(conflict_id, str):
                raise MathFlowError(
                    f"knowledge scheduler lane {identifier} conflict dependency "
                    "keys must be strings"
                )
            _digest(conflict_id, "knowledge scheduler conflict dependency ID")
            input_ids = _digest_list(
                inputs,
                f"knowledge scheduler lane {identifier} conflict dependency inputs",
            )
            if len(input_ids) < 2:
                raise MathFlowError(
                    f"knowledge scheduler lane {identifier} conflict dependency "
                    "needs at least two judgments"
                )
            if conflict_id not in observed_conflicts:
                raise MathFlowError(
                    f"knowledge scheduler lane {identifier} has an unobserved conflict dependency"
                )
            if not set(input_ids).issubset(observed_judgments):
                raise MathFlowError(
                    f"knowledge scheduler lane {identifier} conflict dependency "
                    "has unobserved judgments"
                )
            conflict_dependencies[conflict_id] = input_ids

    if raw_reconciliation_dependencies is not None:
        if not isinstance(raw_reconciliation_dependencies, dict):
            raise MathFlowError(
                f"knowledge scheduler lane {identifier} "
                "reconciliationDependencies must be an object"
            )
        for judgment_id, dependency in raw_reconciliation_dependencies.items():
            if not isinstance(judgment_id, str):
                raise MathFlowError(
                    f"knowledge scheduler lane {identifier} reconciliation dependency "
                    "keys must be strings"
                )
            _digest(judgment_id, "knowledge scheduler reconciliation judgment ID")
            if not isinstance(dependency, dict) or set(dependency) != {
                "conflictId",
                "inputJudgmentIds",
            }:
                raise MathFlowError(
                    f"knowledge scheduler lane {identifier} has an invalid "
                    "reconciliation dependency"
                )
            conflict_id = _digest(
                dependency.get("conflictId"),
                "knowledge scheduler reconciliation conflict ID",
            )
            input_ids = _digest_list(
                dependency.get("inputJudgmentIds"),
                f"knowledge scheduler lane {identifier} reconciliation inputs",
            )
            if judgment_id not in observed_judgments:
                raise MathFlowError(
                    f"knowledge scheduler lane {identifier} has an unobserved reconciliation"
                )
            if conflict_id not in conflict_dependencies:
                raise MathFlowError(
                    f"knowledge scheduler lane {identifier} reconciliation names "
                    "an unknown conflict dependency"
                )
            if input_ids != conflict_dependencies[conflict_id]:
                raise MathFlowError(
                    f"knowledge scheduler lane {identifier} reconciliation inputs "
                    "do not match its conflict"
                )

    active = _validate_active_build(
        value.get("activeBuild"), value, f"knowledge scheduler lane {identifier} activeBuild"
    )
    last_failure = _validate_last_failure(
        value.get("lastFailure"),
        value,
        f"knowledge scheduler lane {identifier} lastFailure",
    )
    if active is not None:
        if next_eligible is not None:
            raise MathFlowError(
                f"knowledge scheduler lane {identifier} cannot be eligible during an active build"
            )
        if set(active["judgmentIds"]) & set(pending_judgments):
            raise MathFlowError(
                f"knowledge scheduler lane {identifier} has active judgments still pending"
            )
        if set(active["conflictIds"]) & set(pending_conflicts):
            raise MathFlowError(
                f"knowledge scheduler lane {identifier} has active conflicts still pending"
            )
        if not set(active["judgmentIds"]).issubset(observed_judgments):
            raise MathFlowError(
                f"knowledge scheduler lane {identifier} has unobserved active judgments"
            )
        if not set(active["conflictIds"]).issubset(observed_conflicts):
            raise MathFlowError(
                f"knowledge scheduler lane {identifier} has unobserved active conflicts"
            )
    elif (pending_judgments or pending_conflicts) and next_eligible is None:
        raise MathFlowError(
            f"knowledge scheduler lane {identifier} has pending work without eligibility"
        )
    elif (
        pending_judgments or pending_conflicts
    ) and last_completed is not None and next_eligible < (
        last_completed + value["minimumIntervalSeconds"]
    ):
        raise MathFlowError(
            f"knowledge scheduler lane {identifier} violates its minimum interval"
        )
    if (
        last_failure is not None
        and active is None
        and next_eligible != last_failure["retryNotBefore"]
    ):
        raise MathFlowError(
            f"knowledge scheduler lane {identifier} failure retry does not match eligibility"
        )
    return value


def validate_scheduler_state(value: object) -> dict[str, object]:
    """Validate and copy the complete scheduler state used for publication."""

    if not isinstance(value, dict) or set(value) != {"schemaVersion", "lanes"}:
        raise MathFlowError("knowledge scheduler state has unsupported or missing fields")
    if value.get("schemaVersion") != 1 or isinstance(value.get("schemaVersion"), bool):
        raise MathFlowError("knowledge scheduler state has an unsupported schema version")
    lanes = value.get("lanes")
    if not isinstance(lanes, dict):
        raise MathFlowError("knowledge scheduler state has an invalid lane index")
    validated: dict[str, object] = {}
    for identifier in sorted(lanes):
        if not isinstance(identifier, str):
            raise MathFlowError("knowledge scheduler lane keys must be strings")
        validated[identifier] = copy.deepcopy(_validate_lane(identifier, lanes[identifier]))
    return {"schemaVersion": 1, "lanes": validated}


def merge_scheduler_states(
    base: object,
    ours: object,
    theirs: object,
) -> dict[str, object]:
    """Three-way merge scheduler state, treating each lane as one semantic unit.

    A lane may change on either side, or change identically on both. Any other
    same-lane edit is ambiguous and is rejected instead of field-merging leases
    or pending-work sets.
    """

    base_state = validate_scheduler_state(base)
    our_state = validate_scheduler_state(ours)
    their_state = validate_scheduler_state(theirs)
    base_lanes = base_state["lanes"]
    our_lanes = our_state["lanes"]
    their_lanes = their_state["lanes"]
    missing = object()
    merged: dict[str, object] = {}
    for identifier in sorted(set(base_lanes) | set(our_lanes) | set(their_lanes)):
        original = base_lanes.get(identifier, missing)
        current = our_lanes.get(identifier, missing)
        incoming = their_lanes.get(identifier, missing)
        if current == incoming:
            selected = current
        elif current == original:
            selected = incoming
        elif incoming == original:
            selected = current
        else:
            raise MathFlowError(
                f"knowledge scheduler lane changed divergently: {identifier}"
            )
        if selected is not missing:
            merged[identifier] = copy.deepcopy(selected)
    return validate_scheduler_state({"schemaVersion": 1, "lanes": merged})


def plan_due_projection_dispatches(
    root: Path,
    scheduler: object,
    now: int,
    repository_head: str = "HEAD",
    projection_root: Path | None = None,
) -> dict[str, object]:
    """Plan due projection workflows as a deterministic queue per problem."""

    current_time = _nonnegative_integer(now, "projection dispatch time")
    state = validate_scheduler_state(scheduler)
    root = root.resolve()
    resolved_head = (
        "WORKTREE"
        if repository_head == "WORKTREE"
        else resolve_commit(root, repository_head)
    )

    if projection_root is not None:
        return _plan_recoverable_projection_dispatches(
            root,
            state,
            current_time,
            resolved_head,
            projection_root.resolve(),
        )

    due_by_problem: dict[str, dict[str, str]] = {}
    for identifier, lane in state["lanes"].items():
        pending = bool(lane["pendingJudgmentIds"] or lane["pendingConflictIds"])
        if not pending or lane["activeBuild"] is not None:
            continue
        eligible = lane["nextEligibleAt"]
        if eligible > current_time:
            continue
        projection_digest = lane.get("projectionSpecDigest")
        if projection_digest is None:
            raise MathFlowError(
                f"due knowledge scheduler lane has no governed projection: {identifier}"
            )
        problem = lane["problemId"]
        due_by_problem.setdefault(problem, {})[projection_digest] = identifier

    problem_queues: list[dict[str, object]] = []
    for problem in sorted(due_by_problem):
        active = list_active_projections(
            root,
            problem,
            resolved_head,
            engine="openrouter-repository-v1",
        )
        active_by_digest = {
            item["projectionSpecDigest"]: item for item in active["projections"]
        }
        due = due_by_problem[problem]
        unknown = sorted(set(due) - set(active_by_digest))
        if unknown:
            lanes = ", ".join(due[digest] for digest in unknown)
            raise MathFlowError(
                f"due knowledge scheduler lanes do not map to active governed projections: {lanes}"
            )
        for digest, identifier in due.items():
            projection = active_by_digest[digest]
            expected_interval = projection["scheduling"][
                "knowledgeMinimumIntervalSeconds"
            ]
            lane = state["lanes"][identifier]
            if lane["minimumIntervalSeconds"] != expected_interval:
                raise MathFlowError(
                    "due knowledge scheduler lane interval does not match its "
                    f"governed projection: {identifier}"
                )
        queue = [
            active_by_digest[digest]
            for digest in sorted(
                due,
                key=lambda item: (
                    str(active_by_digest[item]["projectionId"]),
                    item,
                ),
            )
        ]
        problem_queues.append({"problemId": problem, "projections": queue})

    return {
        "schemaVersion": 1,
        "repositoryHead": resolved_head,
        "problems": problem_queues,
    }


def filter_projection_dispatch_history(
    plan: object,
    run_history: object,
    maximum_consecutive_failures: int = MAX_AUTOMATIC_FAILURES,
) -> dict[str, object]:
    """Suppress duplicate or repeatedly failing same-head workflow dispatches."""

    if (
        not isinstance(maximum_consecutive_failures, int)
        or isinstance(maximum_consecutive_failures, bool)
        or maximum_consecutive_failures <= 0
    ):
        raise MathFlowError("maximum consecutive projection failures must be positive")
    if not isinstance(plan, dict) or set(plan) != {
        "schemaVersion",
        "repositoryHead",
        "problems",
    }:
        raise MathFlowError("projection dispatch plan has unsupported or missing fields")
    repository_head = plan.get("repositoryHead")
    problems = plan.get("problems")
    if (
        plan.get("schemaVersion") != 1
        or not isinstance(repository_head, str)
        or not isinstance(problems, list)
    ):
        raise MathFlowError("projection dispatch plan is invalid")
    if not isinstance(run_history, list):
        raise MathFlowError("projection workflow history must be a list")

    runs: list[dict[str, object]] = []
    seen_run_ids: set[int] = set()
    for item in run_history:
        if not isinstance(item, dict) or set(item) != {
            "conclusion",
            "databaseId",
            "displayTitle",
            "headSha",
            "status",
        }:
            raise MathFlowError("projection workflow history contains an invalid run")
        run_id = item.get("databaseId")
        if (
            not isinstance(run_id, int)
            or isinstance(run_id, bool)
            or run_id <= 0
            or run_id in seen_run_ids
            or not isinstance(item.get("displayTitle"), str)
            or not isinstance(item.get("headSha"), str)
            or not isinstance(item.get("status"), str)
            or (
                item.get("conclusion") is not None
                and not isinstance(item.get("conclusion"), str)
            )
        ):
            raise MathFlowError("projection workflow history contains an invalid run")
        seen_run_ids.add(run_id)
        runs.append(item)
    runs.sort(key=lambda item: int(item["databaseId"]), reverse=True)

    active_statuses = {
        "in_progress",
        "pending",
        "queued",
        "requested",
        "waiting",
    }
    filtered_problems: list[dict[str, object]] = []
    for problem_item in problems:
        if not isinstance(problem_item, dict) or set(problem_item) != {
            "problemId",
            "projections",
        }:
            raise MathFlowError("projection dispatch plan contains an invalid problem")
        problem = problem_item.get("problemId")
        projections = problem_item.get("projections")
        if not isinstance(problem, str) or not isinstance(projections, list):
            raise MathFlowError("projection dispatch plan contains an invalid problem")
        selected: list[object] = []
        for projection in projections:
            if not isinstance(projection, dict):
                raise MathFlowError(
                    "projection dispatch plan contains an invalid projection"
                )
            projection_id = projection.get("projectionId")
            if not isinstance(projection_id, str):
                raise MathFlowError(
                    "projection dispatch plan contains an invalid projection"
                )
            title = f"Project {projection_id}/{problem}"
            matching = [
                run
                for run in runs
                if run["displayTitle"] == title
                and run["headSha"] == repository_head
            ]
            if any(run["status"] in active_statuses for run in matching):
                continue
            consecutive_failures = 0
            for run in matching:
                if run["status"] != "completed":
                    continue
                if run["conclusion"] == "success":
                    break
                if run["conclusion"] == "failure":
                    consecutive_failures += 1
            if consecutive_failures >= maximum_consecutive_failures:
                continue
            selected.append(copy.deepcopy(projection))
        if selected:
            filtered_problems.append(
                {"problemId": problem, "projections": selected}
            )
    return {
        "schemaVersion": 1,
        "repositoryHead": repository_head,
        "problems": filtered_problems,
    }


def _canonical_problems(root: Path, repository_head: str) -> list[str]:
    problems: set[str] = set()
    for path in list_files_at(root, repository_head, "problems"):
        parts = PurePosixPath(path).parts
        if len(parts) == 3 and parts[0] == "problems" and parts[2] == "problem.md":
            validate_slug(parts[1], "problem id")
            problems.add(parts[1])
    return sorted(problems)


def _builder_spec_digest(
    root: Path, repository_head: str, projection: dict[str, object]
) -> str:
    path = projection.get("knowledgeBuilder")
    if not isinstance(path, str):
        raise MathFlowError("active projection has no knowledge builder")
    try:
        value = json.loads(read_at(root, repository_head, path))
    except json.JSONDecodeError as exc:
        raise MathFlowError(f"knowledge builder specification is not valid JSON: {path}") from exc
    if not isinstance(value, dict):
        raise MathFlowError(f"knowledge builder specification must be an object: {path}")
    return f"sha256:{sha256_json(value)}"


def _latest_state_is_current(
    projection_root: Path,
    lane: dict[str, object],
    projection: dict[str, object],
    problem_ledger_digest: str,
) -> bool:
    latest = lane.get("latestStateRun")
    if latest is None:
        return False
    latest_digest = _digest(latest, "knowledge scheduler latest state run")
    digest_hex = latest_digest.removeprefix("sha256:")
    bundle = (
        projection_root
        / "objects"
        / "knowledge-build"
        / digest_hex[:2]
        / digest_hex
    )
    if not bundle.exists():
        return False
    if not bundle.is_dir() or bundle.is_symlink():
        raise MathFlowError(
            f"published latest knowledge state is not a bundle: {latest_digest}"
        )
    manifest, actual_digest = verify_bundle(bundle)
    if actual_digest != latest_digest:
        raise MathFlowError(
            "published latest knowledge state does not match its content address: "
            f"{latest_digest}"
        )
    identifier = str(lane["laneId"])
    problem = str(lane["problemId"])
    projection_digest = str(projection["projectionSpecDigest"])
    builder_digest = str(lane["builderSpecDigest"])
    inputs = manifest.get("inputs")
    judge_spec = manifest.get("judgeSpec")
    if (
        manifest.get("runKind") != "knowledge-build"
        or manifest.get("problemId") != problem
        or not isinstance(inputs, dict)
        or inputs.get("laneId") != identifier
        or inputs.get("problemId") != problem
        or inputs.get("builderSpecDigest") != builder_digest
        or inputs.get("projectionSpecDigest") != projection_digest
        or not isinstance(judge_spec, dict)
        or judge_spec.get("digest") != builder_digest
    ):
        raise MathFlowError(
            "published latest knowledge state does not match its projection lane: "
            f"{latest_digest}"
        )
    manifest_ledger = _digest(
        manifest.get("problemLedgerDigest"),
        "published latest knowledge state problemLedgerDigest",
    )
    return manifest_ledger == problem_ledger_digest


def _plan_recoverable_projection_dispatches(
    root: Path,
    state: dict[str, object],
    now: int,
    repository_head: str,
    projection_root: Path,
) -> dict[str, object]:
    """Recover dispatches from canonical governance, ledgers, and published state."""

    problem_queues: list[dict[str, object]] = []
    lanes = state["lanes"]
    for problem in _canonical_problems(root, repository_head):
        current_ledger = (
            worktree_ledger(root, problem)
            if repository_head == "WORKTREE"
            else ledger(root, problem, repository_head)
        )
        nonempty_ledger = bool(current_ledger["transactions"])
        active = list_active_projections(
            root,
            problem,
            repository_head,
            engine="openrouter-repository-v1",
        )["projections"]
        due: list[dict[str, object]] = []
        for projection in active:
            projection_digest = str(projection["projectionSpecDigest"])
            builder_digest = _builder_spec_digest(root, repository_head, projection)
            identifier = lane_id(problem, builder_digest, projection_digest)
            lane = lanes.get(identifier)
            if lane is None:
                if nonempty_ledger:
                    due.append(projection)
                continue
            if (
                lane.get("problemId") != problem
                or lane.get("builderSpecDigest") != builder_digest
                or lane.get("projectionSpecDigest") != projection_digest
            ):
                raise MathFlowError(
                    f"knowledge scheduler lane does not match its active projection: {identifier}"
                )
            expected_interval = projection["scheduling"][
                "knowledgeMinimumIntervalSeconds"
            ]
            if lane["minimumIntervalSeconds"] != expected_interval:
                raise MathFlowError(
                    "knowledge scheduler lane interval does not match its governed "
                    f"projection: {identifier}"
                )

            current = _latest_state_is_current(
                projection_root,
                lane,
                projection,
                str(current_ledger["problemLedgerDigest"]),
            )
            if lane["activeBuild"] is not None:
                continue
            pending = bool(
                lane["pendingJudgmentIds"] or lane["pendingConflictIds"]
            )
            if pending:
                failure = lane.get("lastFailure")
                if (
                    isinstance(failure, dict)
                    and failure.get("problemLedgerDigest")
                    == current_ledger["problemLedgerDigest"]
                    and failure.get("consecutiveFailures", 0)
                    >= MAX_AUTOMATIC_FAILURES
                ):
                    continue
                eligible = lane["nextEligibleAt"]
                if eligible <= now:
                    due.append(projection)
                continue
            if nonempty_ledger and not current:
                due.append(projection)

        if due:
            problem_queues.append(
                {
                    "problemId": problem,
                    "projections": sorted(
                        due,
                        key=lambda item: (
                            str(item["projectionId"]),
                            str(item["projectionSpecDigest"]),
                        ),
                    ),
                }
            )

    return {
        "schemaVersion": 1,
        "repositoryHead": repository_head,
        "problems": problem_queues,
    }
