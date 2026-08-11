from __future__ import annotations

import copy
import json
import time
from pathlib import Path, PurePosixPath

from .artifacts import read_verified_artifact, verify_bundle
from .errors import MathFlowError
from .governance import resolve_projection
from .projection_dependencies import (
    projection_dependency_state_digest,
    resolve_projection_dependencies,
    same_projection_dependency_state,
)
from .repository import (
    commit_timestamp,
    ledger,
    list_files_at,
    read_at,
    resolve_commit,
    sha256_json,
)


_DIGEST_PREFIX = "sha256:"
_PERIOD_SECONDS = {"hour": 3_600, "day": 86_400}
_SCHEDULE_FIELDS = {
    "schemaVersion",
    "mode",
    "evaluatedAt",
    "minimumIntervalSeconds",
    "allocationWindow",
    "previousRunDigest",
}
_WINDOW_FIELDS = {"unit", "startAt", "endAt", "transactionIds"}


def _nonnegative_integer(value: object, label: str) -> int:
    if not isinstance(value, int) or isinstance(value, bool) or value < 0:
        raise MathFlowError(f"{label} must be a nonnegative integer")
    return value


def _optional_digest(value: object, label: str) -> str | None:
    if value is None:
        return None
    if (
        not isinstance(value, str)
        or not value.startswith(_DIGEST_PREFIX)
        or len(value) != 71
        or any(character not in "0123456789abcdef" for character in value[7:])
    ):
        raise MathFlowError(f"{label} must be a SHA-256 digest or null")
    return value


def validate_credit_run_schedule(
    value: object,
    transaction_ids: list[str] | None = None,
) -> dict[str, object]:
    """Validate the immutable scheduling envelope stored in new credit runs."""

    if not isinstance(value, dict) or set(value) != _SCHEDULE_FIELDS:
        raise MathFlowError("credit run schedule has unsupported or missing fields")
    if value.get("schemaVersion") != 1 or isinstance(
        value.get("schemaVersion"), bool
    ):
        raise MathFlowError("credit run schedule has an invalid schema version")
    evaluated_at = _nonnegative_integer(
        value.get("evaluatedAt"), "credit run evaluatedAt"
    )
    interval = _nonnegative_integer(
        value.get("minimumIntervalSeconds"),
        "credit run minimumIntervalSeconds",
    )
    if interval > 86_400:
        raise MathFlowError("credit run minimumIntervalSeconds exceeds one day")
    _optional_digest(value.get("previousRunDigest"), "credit run previousRunDigest")

    mode = value.get("mode")
    window = value.get("allocationWindow")
    if mode == "rolling":
        if window is not None:
            raise MathFlowError("rolling credit run cannot have an allocation window")
    elif mode == "utc-calendar":
        if not isinstance(window, dict) or set(window) != _WINDOW_FIELDS:
            raise MathFlowError("calendar credit run has an invalid allocation window")
        unit = window.get("unit")
        if unit not in _PERIOD_SECONDS:
            raise MathFlowError("calendar credit run has an invalid period unit")
        start = _nonnegative_integer(window.get("startAt"), "allocation window startAt")
        end = _nonnegative_integer(window.get("endAt"), "allocation window endAt")
        seconds = _PERIOD_SECONDS[str(unit)]
        if start % seconds != 0 or end != start + seconds or evaluated_at < end:
            raise MathFlowError("calendar credit run has an unaligned or open window")
        ids = window.get("transactionIds")
        if (
            not isinstance(ids, list)
            or not ids
            or any(not isinstance(item, str) for item in ids)
            or len(ids) != len(set(ids))
            or (transaction_ids is not None and ids != transaction_ids)
        ):
            raise MathFlowError(
                "calendar credit run window does not match its transactions"
            )
    else:
        raise MathFlowError("credit run schedule has an invalid mode")
    return value


def _problem_index_entries(
    projection_root: Path, problem: str
) -> list[dict[str, object]]:
    path = projection_root / "indexes" / "problems" / problem / "runs.json"
    if not path.exists():
        return []
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise MathFlowError(f"could not read projection credit index: {exc}") from exc
    if not isinstance(value, list) or any(not isinstance(item, dict) for item in value):
        raise MathFlowError("projection credit index must be an object array")
    return value


def _indexed_bundle(
    projection_root: Path, entry: dict[str, object]
) -> tuple[Path, str]:
    digest = entry.get("runDigest")
    path = entry.get("path")
    if not isinstance(digest, str) or not isinstance(path, str):
        raise MathFlowError("projection credit index entry is incomplete")
    relative = PurePosixPath(path)
    if relative.is_absolute() or ".." in relative.parts:
        raise MathFlowError("projection credit index path escapes its root")
    root = projection_root.resolve()
    target = root.joinpath(*relative.parts).resolve()
    try:
        target.relative_to(root)
    except ValueError as exc:
        raise MathFlowError("projection credit index path escapes its root") from exc
    return target, digest


def _published_credit_runs(
    projection_root: Path,
    problem: str,
    projection_id: str,
    projection_digest: str,
) -> list[dict[str, object]]:
    # The import is intentionally local: credit.py calls this planner after its
    # loader has been defined, while the loader validates the full bundle.
    from .credit import load_credit_assignment_bundle

    runs: list[dict[str, object]] = []
    for entry in _problem_index_entries(projection_root, problem):
        if entry.get("runKind") != "credit-assignment":
            continue
        bundle, expected = _indexed_bundle(projection_root, entry)
        raw_manifest, raw_digest = verify_bundle(bundle)
        if raw_digest != expected:
            raise MathFlowError("published credit run does not match its index")
        raw_inputs = raw_manifest.get("inputs")
        if (
            not isinstance(raw_inputs, dict)
            or raw_inputs.get("projectionId") != projection_id
            or raw_inputs.get("projectionSpecDigest") != projection_digest
        ):
            continue
        manifest, _, digest = load_credit_assignment_bundle(bundle)
        if digest != expected:
            raise MathFlowError("published credit run does not match its index")
        inputs = manifest.get("inputs")
        if not isinstance(inputs, dict):  # pragma: no cover - loader guarantees this
            raise AssertionError("verified credit bundle has no inputs")
        lock = json.loads(read_verified_artifact(bundle, manifest, "dependency-lock"))
        schedule = inputs.get("schedule")
        if schedule is not None:
            schedule = validate_credit_run_schedule(schedule)
        runs.append(
            {
                "runDigest": digest,
                "manifest": manifest,
                "dependencyLock": lock,
                "schedule": schedule,
            }
        )
    return runs


def ordered_credit_runs(
    runs: list[dict[str, object]],
) -> list[dict[str, object]]:
    """Return a verified predecessor chain, rejecting arbitrary terminals."""

    scheduled = [item for item in runs if item["schedule"] is not None]
    legacy = [item for item in runs if item["schedule"] is None]
    if not scheduled:
        if len(legacy) <= 1:
            return legacy
        raise MathFlowError(
            "credit projection has multiple legacy runs with no terminal ordering"
        )
    if len(legacy) > 1:
        raise MathFlowError(
            "credit projection has multiple legacy predecessors with no ordering"
        )
    scheduled.sort(key=lambda item: int(item["schedule"]["evaluatedAt"]))
    evaluated = [int(item["schedule"]["evaluatedAt"]) for item in scheduled]
    if len(evaluated) != len(set(evaluated)):
        raise MathFlowError(
            "credit projection has multiple runs at one evaluation time"
        )
    ordered = [*legacy, *scheduled]
    previous = str(legacy[0]["runDigest"]) if legacy else None
    for item in scheduled:
        if item["schedule"].get("previousRunDigest") != previous:
            raise MathFlowError(
                "credit projection runs do not form one predecessor chain"
            )
        previous = str(item["runDigest"])
    return ordered


def _latest_run(runs: list[dict[str, object]]) -> dict[str, object] | None:
    ordered = ordered_credit_runs(runs)
    return ordered[-1] if ordered else None


def _ineligible(
    projection_id: str,
    projection_digest: str,
    problem: str,
    as_of: int,
    reason: str,
    message: str,
    *,
    next_eligible_at: int | None = None,
) -> dict[str, object]:
    return {
        "schemaVersion": 1,
        "projectionId": projection_id,
        "projectionSpecDigest": projection_digest,
        "problemId": problem,
        "asOf": as_of,
        "eligible": False,
        "reasonCode": reason,
        "message": message,
        "nextEligibleAt": next_eligible_at,
        "schedule": None,
    }


def next_calendar_allocation_window(
    root: Path,
    transactions: list[dict[str, object]],
    unit: str,
    latest_closed_end: int,
    previous_end: int | None = None,
) -> dict[str, object] | None:
    """Select the next nonempty closed UTC window in one calendar chain.

    A new chain deliberately starts at the latest closed bucket. Once a chain
    exists, it advances from the preceding window end and deterministically
    skips empty buckets so downtime cannot strand an earlier nonempty period.
    """

    seconds = _PERIOD_SECONDS.get(unit)
    if seconds is None:
        raise MathFlowError("calendar allocation window has an invalid unit")
    _nonnegative_integer(latest_closed_end, "latest closed calendar end")
    if latest_closed_end % seconds != 0:
        raise MathFlowError("latest closed calendar end is not UTC-aligned")
    if previous_end is None:
        starts = [latest_closed_end - seconds] if latest_closed_end else []
    else:
        _nonnegative_integer(previous_end, "previous calendar end")
        if previous_end % seconds != 0 or previous_end > latest_closed_end:
            raise MathFlowError("previous calendar end is not a valid chain boundary")
        starts = range(previous_end, latest_closed_end, seconds)
    timestamps = {
        str(item["transactionId"]): commit_timestamp(
            root, str(item["transactionId"])
        )
        for item in transactions
    }
    for start in starts:
        end = start + seconds
        transaction_ids = [
            str(item["transactionId"])
            for item in transactions
            if start <= timestamps[str(item["transactionId"])] < end
        ]
        if transaction_ids:
            return {
                "unit": unit,
                "startAt": start,
                "endAt": end,
                "transactionIds": transaction_ids,
            }
    return None


def plan_credit_run(
    root: Path,
    projection_root: Path,
    projection: str,
    problem: str,
    head: str = "HEAD",
    as_of: int | None = None,
) -> dict[str, object]:
    """Plan one provider-free governed credit run at an explicit epoch."""

    now = int(time.time()) if as_of is None else as_of
    _nonnegative_integer(now, "credit planning time")
    resolved = resolve_projection(root, projection, problem, head)
    if resolved.get("engine") != "overlay-repository-v1":
        raise MathFlowError("credit planning requires an overlay projection")
    projection_digest = str(resolved["projectionSpecDigest"])
    runner = resolved.get("runner")
    runner_path = runner.get("spec") if isinstance(runner, dict) else None
    if not isinstance(runner_path, str):
        raise MathFlowError("credit projection has no governed runner specification")
    try:
        runner_spec = json.loads(
            read_at(root, str(resolved["canonicalHead"]), runner_path)
        )
    except json.JSONDecodeError as exc:
        raise MathFlowError("credit runner specification is not valid JSON") from exc
    if not isinstance(runner_spec, dict):
        raise MathFlowError("credit runner specification must be an object")
    runner_spec_digest = f"sha256:{sha256_json(runner_spec)}"
    scheduling = resolved.get("scheduling")
    if not isinstance(scheduling, dict):  # governed validation should already catch this
        raise MathFlowError("credit projection has no scheduling policy")
    interval = int(scheduling["minimumIntervalSeconds"])
    dependency_lock = resolve_projection_dependencies(
        root, projection_root, projection, problem, head
    )
    runs = _published_credit_runs(
        projection_root, problem, projection, projection_digest
    )
    latest = _latest_run(runs)
    previous_digest = str(latest["runDigest"]) if latest is not None else None

    period = scheduling.get("utcCalendarPeriod")
    if period is None:
        equivalent = [
            item
            for item in runs
            if same_projection_dependency_state(
                item["dependencyLock"], dependency_lock
            )
        ]
        if equivalent:
            return _ineligible(
                projection,
                projection_digest,
                problem,
                now,
                "dependency-state-already-covered",
                "A verified run already covers the current dependency state.",
            )
        if latest is not None:
            latest_schedule = latest["schedule"]
            if latest_schedule is None and interval:
                raise MathFlowError(
                    "cannot enforce a nonzero interval after an unordered legacy run"
                )
            eligible_at = (
                int(latest_schedule["evaluatedAt"]) + interval
                if latest_schedule is not None
                else now
            )
            if now < eligible_at:
                return _ineligible(
                    projection,
                    projection_digest,
                    problem,
                    now,
                    "minimum-interval-not-elapsed",
                    "The rolling coalescing interval has not elapsed.",
                    next_eligible_at=eligible_at,
                )
        transactions = ledger(root, problem, str(resolved["canonicalHead"]))[
            "transactions"
        ]
        if not transactions:
            return _ineligible(
                projection,
                projection_digest,
                problem,
                now,
                "no-transactions",
                "Credit assignment requires at least one canonical transaction.",
            )
        schedule = {
            "schemaVersion": 1,
            "mode": "rolling",
            "evaluatedAt": now,
            "minimumIntervalSeconds": interval,
            "allocationWindow": None,
            "previousRunDigest": previous_digest,
        }
    else:
        unit = str(period["unit"])
        seconds = _PERIOD_SECONDS[unit]
        latest_closed_end = (now // seconds) * seconds
        if latest_closed_end == 0:
            return _ineligible(
                projection,
                projection_digest,
                problem,
                now,
                "no-closed-calendar-period",
                "No UTC calendar period has closed yet.",
                next_eligible_at=seconds,
            )
        previous_end: int | None = None
        if latest is not None:
            latest_schedule = latest["schedule"]
            if latest_schedule is None:
                raise MathFlowError(
                    "cannot start calendar scheduling after an unordered legacy run"
                )
            eligible_at = int(latest_schedule["evaluatedAt"]) + interval
            if now < eligible_at:
                return _ineligible(
                    projection,
                    projection_digest,
                    problem,
                    now,
                    "minimum-interval-not-elapsed",
                    "The overlay minimum interval has not elapsed.",
                    next_eligible_at=eligible_at,
                )
            if latest_schedule.get("mode") != "utc-calendar":
                raise MathFlowError(
                    "calendar projection predecessor does not use calendar scheduling"
                )
            previous_window = latest_schedule.get("allocationWindow")
            if (
                not isinstance(previous_window, dict)
                or previous_window.get("unit") != unit
            ):
                raise MathFlowError(
                    "calendar projection predecessor uses another UTC period"
                )
            previous_end = int(previous_window["endAt"])
            if previous_end >= latest_closed_end:
                return _ineligible(
                    projection,
                    projection_digest,
                    problem,
                    now,
                    "no-new-closed-calendar-period",
                    "No UTC calendar period has closed after the published terminal.",
                    next_eligible_at=latest_closed_end + seconds,
                )
        canonical = ledger(root, problem, str(resolved["canonicalHead"]))[
            "transactions"
        ]
        window = next_calendar_allocation_window(
            root,
            canonical,
            unit,
            latest_closed_end,
            previous_end,
        )
        if window is None:
            continuing = previous_end is not None
            return _ineligible(
                projection,
                projection_digest,
                problem,
                now,
                "calendar-periods-empty" if continuing else "calendar-period-empty",
                (
                    "Every newly closed UTC period after the published terminal is empty."
                    if continuing
                    else "The latest closed UTC period contains no canonical transactions."
                ),
                next_eligible_at=latest_closed_end + seconds,
            )
        schedule = {
            "schemaVersion": 1,
            "mode": "utc-calendar",
            "evaluatedAt": now,
            "minimumIntervalSeconds": interval,
            "allocationWindow": window,
            "previousRunDigest": previous_digest,
        }

    validate_credit_run_schedule(schedule)
    dependency_state_digest = projection_dependency_state_digest(dependency_lock)
    retry_subject: dict[str, object] = {
        "projectionSpecDigest": projection_digest,
        "runnerSpecDigest": runner_spec_digest,
        "problemId": problem,
        "mode": schedule["mode"],
        "dependencyStateDigest": dependency_state_digest,
    }
    if schedule["mode"] == "utc-calendar":
        retry_subject["allocationWindow"] = schedule["allocationWindow"]
    automatic_retry_key = f"sha256:{sha256_json(retry_subject)}"
    return {
        "schemaVersion": 1,
        "projectionId": projection,
        "projectionSpecDigest": projection_digest,
        "runnerSpecDigest": runner_spec_digest,
        "problemId": problem,
        "asOf": now,
        "eligible": True,
        "reasonCode": "eligible",
        "message": "The governed credit projection is eligible to run.",
        "nextEligibleAt": None,
        "dependencyLockDigest": dependency_lock["dependencyLockDigest"],
        "dependencyStateDigest": dependency_state_digest,
        "problemLedgerDigest": dependency_lock["problemLedger"][
            "problemLedgerDigest"
        ],
        "automaticRetryKey": automatic_retry_key,
        "schedule": schedule,
    }


def plan_due_credit_dispatches(
    root: Path,
    projection_root: Path,
    head: str = "HEAD",
    as_of: int | None = None,
) -> dict[str, object]:
    """Plan every currently eligible governed credit overlay without providers."""

    from .governance import list_active_projections

    now = int(time.time()) if as_of is None else as_of
    _nonnegative_integer(now, "credit planning time")
    repository_head = resolve_commit(root, head)
    problems = sorted(
        {
            parts[1]
            for path in list_files_at(root, repository_head, "problems")
            if len(parts := PurePosixPath(path).parts) == 3
            and parts[0] == "problems"
            and parts[2] == "problem.md"
        }
    )
    dispatches: list[dict[str, object]] = []
    waiting: list[dict[str, str]] = []
    planning_errors: list[dict[str, str]] = []
    for problem in problems:
        projections = list_active_projections(
            root,
            problem,
            repository_head,
            engine="overlay-repository-v1",
        )["projections"]
        for projection in projections:
            projection_id = str(projection["projectionId"])
            try:
                plan = plan_credit_run(
                    root,
                    projection_root,
                    projection_id,
                    problem,
                    repository_head,
                    now,
                )
            except MathFlowError as exc:
                message = str(exc)
                target = waiting if any(
                    marker in message
                    for marker in (
                        "has an active build",
                        "has pending knowledge inputs",
                        "has no published state",
                        "is stale for the current problem ledger",
                        "must resolve to exactly one knowledge lane; found 0",
                    )
                ) else planning_errors
                target.append(
                    {
                        "problemId": problem,
                        "projectionId": projection_id,
                        "message": message,
                    }
                )
                continue
            if plan["eligible"] is True:
                dispatches.append(
                    {
                        "problemId": problem,
                        "projectionId": projection_id,
                        "projectionSpecDigest": plan["projectionSpecDigest"],
                        "asOf": now,
                        "automaticRetryKey": plan["automaticRetryKey"],
                    }
                )
    return {
        "schemaVersion": 1,
        "repositoryHead": repository_head,
        "asOf": now,
        "dispatches": dispatches,
        "waitingOnDependencies": waiting,
        "planningErrors": planning_errors,
    }


def filter_credit_dispatch_history(
    plan: object,
    run_history: object,
    maximum_consecutive_failures: int = 5,
) -> dict[str, object]:
    """Suppress active or repeatedly failing automatic credit retry keys.

    Manual workflow dispatches use the distinct ``manual`` key and never pass
    through this filter.
    """

    expected_plan_fields = {
        "schemaVersion",
        "repositoryHead",
        "asOf",
        "dispatches",
        "waitingOnDependencies",
        "planningErrors",
    }
    if not isinstance(plan, dict) or set(plan) != expected_plan_fields:
        raise MathFlowError("credit dispatch plan has unsupported or missing fields")
    if (
        plan.get("schemaVersion") != 1
        or not isinstance(plan.get("repositoryHead"), str)
        or not isinstance(plan.get("asOf"), int)
        or isinstance(plan.get("asOf"), bool)
        or not isinstance(plan.get("dispatches"), list)
        or not isinstance(plan.get("waitingOnDependencies"), list)
        or not isinstance(plan.get("planningErrors"), list)
        or not isinstance(maximum_consecutive_failures, int)
        or isinstance(maximum_consecutive_failures, bool)
        or maximum_consecutive_failures <= 0
    ):
        raise MathFlowError("credit dispatch plan is invalid")
    if not isinstance(run_history, list):
        raise MathFlowError("credit workflow history must be a list")
    required_run_fields = {
        "conclusion",
        "databaseId",
        "displayTitle",
        "headSha",
        "status",
    }
    runs: list[dict[str, object]] = []
    seen_ids: set[int] = set()
    for item in run_history:
        if not isinstance(item, dict) or set(item) != required_run_fields:
            raise MathFlowError("credit workflow history contains an invalid run")
        run_id = item.get("databaseId")
        if (
            not isinstance(run_id, int)
            or isinstance(run_id, bool)
            or run_id <= 0
            or run_id in seen_ids
            or not isinstance(item.get("displayTitle"), str)
            or not isinstance(item.get("headSha"), str)
            or not isinstance(item.get("status"), str)
            or (
                item.get("conclusion") is not None
                and not isinstance(item.get("conclusion"), str)
            )
        ):
            raise MathFlowError("credit workflow history contains an invalid run")
        seen_ids.add(run_id)
        runs.append(item)
    runs.sort(key=lambda item: int(item["databaseId"]), reverse=True)
    active_statuses = {"in_progress", "pending", "queued", "requested", "waiting"}
    selected: list[dict[str, object]] = []
    for dispatch in plan["dispatches"]:
        if not isinstance(dispatch, dict) or set(dispatch) != {
            "problemId",
            "projectionId",
            "projectionSpecDigest",
            "asOf",
            "automaticRetryKey",
        }:
            raise MathFlowError("credit dispatch plan contains an invalid dispatch")
        projection = dispatch.get("projectionId")
        problem = dispatch.get("problemId")
        retry_key = dispatch.get("automaticRetryKey")
        if not all(isinstance(item, str) for item in (projection, problem, retry_key)):
            raise MathFlowError("credit dispatch plan contains an invalid dispatch")
        title = f"Credit {projection}/{problem} [{retry_key}]"
        matching = [run for run in runs if run["displayTitle"] == title]
        if any(run["status"] in active_statuses for run in matching):
            continue
        failures = 0
        for run in matching:
            if run["status"] != "completed":
                continue
            if run["conclusion"] == "success":
                break
            if run["conclusion"] is not None:
                failures += 1
        if failures < maximum_consecutive_failures:
            selected.append(copy.deepcopy(dispatch))
    return {**copy.deepcopy(plan), "dispatches": selected}


def assert_credit_publication_unique(
    projection_root: Path, bundle_dir: Path
) -> None:
    """Reject a second new-format terminal for one governed state or UTC bucket."""

    from .credit import load_credit_assignment_bundle

    manifest, _, new_digest = load_credit_assignment_bundle(bundle_dir)
    inputs = manifest.get("inputs")
    if not isinstance(inputs, dict) or inputs.get("schedule") is None:
        return
    schedule = validate_credit_run_schedule(inputs["schedule"])
    projection = str(inputs.get("projectionId"))
    projection_digest = str(inputs.get("projectionSpecDigest"))
    problem = str(manifest.get("problemId"))
    existing = _published_credit_runs(
        projection_root, problem, projection, projection_digest
    )
    if any(item["runDigest"] == new_digest for item in existing):
        return
    previous = _latest_run(existing)
    expected_previous = str(previous["runDigest"]) if previous is not None else None
    if schedule.get("previousRunDigest") != expected_previous:
        raise MathFlowError(
            "credit run previousRunDigest does not select the published terminal"
        )
    if previous is not None and isinstance(previous.get("schedule"), dict):
        previous_schedule = previous["schedule"]
        minimum_time = int(previous_schedule["evaluatedAt"]) + int(
            schedule["minimumIntervalSeconds"]
        )
        if int(schedule["evaluatedAt"]) < minimum_time:
            raise MathFlowError(
                "credit publication violates its governed minimum interval"
            )
    if schedule["mode"] == "rolling":
        new_lock = json.loads(
            read_verified_artifact(bundle_dir, manifest, "dependency-lock")
        )
        if any(
            same_projection_dependency_state(item["dependencyLock"], new_lock)
            for item in existing
        ):
            raise MathFlowError(
                "credit publication already covers this dependency state"
            )
    else:
        start = schedule["allocationWindow"]["startAt"]
        if previous is not None and isinstance(previous.get("schedule"), dict):
            previous_window = previous["schedule"].get("allocationWindow")
            if (
                isinstance(previous_window, dict)
                and int(start) <= int(previous_window["startAt"])
            ):
                raise MathFlowError(
                    "credit calendar publication does not advance its UTC period"
                )
        if any(
            isinstance(item["schedule"], dict)
            and isinstance(item["schedule"].get("allocationWindow"), dict)
            and item["schedule"]["allocationWindow"].get("startAt") == start
            for item in existing
        ):
            raise MathFlowError("credit publication already covers this UTC period")
