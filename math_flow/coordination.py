from __future__ import annotations

import fcntl
import functools
import json
import os
import re
import shutil
import tempfile
from pathlib import Path

from .artifacts import verify_bundle
from .errors import MathFlowError
from .repository import sha256_json, validate_slug


DIGEST = re.compile(r"^sha256:[0-9a-f]{64}$")


def _scheduler_locked(function):
    @functools.wraps(function)
    def wrapped(path: Path, *args, **kwargs):
        lock_path = path.with_name(f"{path.name}.lock")
        lock_path.parent.mkdir(parents=True, exist_ok=True)
        with lock_path.open("a+", encoding="utf-8") as handle:
            fcntl.flock(handle.fileno(), fcntl.LOCK_EX)
            try:
                return function(path, *args, **kwargs)
            finally:
                fcntl.flock(handle.fileno(), fcntl.LOCK_UN)

    return wrapped


def _digest(value: object, label: str) -> str:
    if not isinstance(value, str) or not DIGEST.fullmatch(value):
        raise MathFlowError(f"{label} must be a SHA-256 digest")
    return value


def _atomic_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    rendered = json.dumps(value, indent=2, ensure_ascii=False) + "\n"
    descriptor, temporary = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
            handle.write(rendered)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def load_scheduler(path: Path) -> dict[str, object]:
    if not path.exists():
        return {"schemaVersion": 1, "lanes": {}}
    try:
        state = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise MathFlowError(f"could not read knowledge scheduler state: {exc}") from exc
    if not isinstance(state, dict) or state.get("schemaVersion") != 1:
        raise MathFlowError("invalid knowledge scheduler state")
    lanes = state.get("lanes")
    if not isinstance(lanes, dict) or any(not isinstance(lane, dict) for lane in lanes.values()):
        raise MathFlowError("knowledge scheduler has an invalid lane index")
    return state


def lane_id(
    problem: str,
    builder_spec_digest: str,
    projection_spec_digest: str | None = None,
) -> str:
    _digest(builder_spec_digest, "builder spec digest")
    if projection_spec_digest is not None:
        _digest(projection_spec_digest, "projection spec digest")
        identity = {
            "problemId": problem,
            "projectionSpecDigest": projection_spec_digest,
        }
    else:
        identity = {
            "problemId": problem,
            "builderSpecDigest": builder_spec_digest,
        }
    return f"sha256:{sha256_json(identity)}"


@_scheduler_locked
def record_completed_inputs(
    path: Path,
    problem: str,
    builder_spec_digest: str,
    judgment_ids: list[str],
    conflict_ids: list[str],
    minimum_interval_seconds: int,
    now: int,
    projection_spec_digest: str | None = None,
) -> dict[str, object]:
    if minimum_interval_seconds < 0:
        raise MathFlowError("minimum knowledge-build interval cannot be negative")
    if now < 0:
        raise MathFlowError("scheduler time cannot be negative")
    for judgment_id in judgment_ids:
        _digest(judgment_id, "judgment ID")
    for conflict_id in conflict_ids:
        _digest(conflict_id, "conflict ID")
    state = load_scheduler(path)
    lanes = state["lanes"]
    identifier = lane_id(problem, builder_spec_digest, projection_spec_digest)
    lane = lanes.get(identifier)
    if lane is None:
        lane = {
            "laneId": identifier,
            "problemId": problem,
            "builderSpecDigest": builder_spec_digest,
            "minimumIntervalSeconds": minimum_interval_seconds,
            "latestStateRun": None,
            "lastCompletedAt": None,
            "nextEligibleAt": now,
            "observedJudgmentIds": [],
            "observedConflictIds": [],
            "pendingJudgmentIds": [],
            "pendingConflictIds": [],
            "activeBuild": None,
        }
        if projection_spec_digest is not None:
            lane["projectionSpecDigest"] = projection_spec_digest
        lanes[identifier] = lane
    elif lane.get("projectionSpecDigest") != projection_spec_digest:
        raise MathFlowError("knowledge-build lane projection does not match its existing policy")
    elif lane.get("minimumIntervalSeconds") != minimum_interval_seconds:
        raise MathFlowError("knowledge-build lane interval does not match its existing policy")
    observed_judgments = set(lane.setdefault("observedJudgmentIds", []))
    observed_conflicts = set(lane.setdefault("observedConflictIds", []))
    new_judgments = set(judgment_ids) - observed_judgments
    new_conflicts = set(conflict_ids) - observed_conflicts
    observed_judgments.update(judgment_ids)
    observed_conflicts.update(conflict_ids)
    lane["observedJudgmentIds"] = sorted(observed_judgments)
    lane["observedConflictIds"] = sorted(observed_conflicts)
    pending_judgments = set(lane["pendingJudgmentIds"])
    pending_judgments.update(new_judgments)
    pending_conflicts = set(lane["pendingConflictIds"])
    pending_conflicts.update(new_conflicts)
    lane["pendingJudgmentIds"] = sorted(pending_judgments)
    lane["pendingConflictIds"] = sorted(pending_conflicts)
    if (
        lane["nextEligibleAt"] is None
        and lane["activeBuild"] is None
        and (lane["pendingJudgmentIds"] or lane["pendingConflictIds"])
    ):
        last = lane["lastCompletedAt"]
        lane["nextEligibleAt"] = max(now, int(last) + minimum_interval_seconds) if last is not None else now
    _atomic_json(path, state)
    return lane


@_scheduler_locked
def claim_due_build(
    path: Path,
    identifier: str,
    now: int,
    maximum_judgments: int,
) -> dict[str, object] | None:
    if maximum_judgments <= 0:
        raise MathFlowError("maximum judgments per build must be positive")
    state = load_scheduler(path)
    lanes = state["lanes"]
    lane = lanes.get(identifier)
    if not isinstance(lane, dict):
        raise MathFlowError("knowledge-build lane does not exist")
    if lane.get("activeBuild") is not None:
        return None
    eligible = lane.get("nextEligibleAt")
    pending = lane.get("pendingJudgmentIds")
    conflicts = lane.get("pendingConflictIds")
    if (
        not isinstance(pending, list)
        or not isinstance(conflicts, list)
        or (not pending and not conflicts)
        or not isinstance(eligible, int)
        or now < eligible
    ):
        return None
    selected_judgments = pending[:maximum_judgments]
    selected_conflicts = list(conflicts)
    request_core: dict[str, object] = {
        "schemaVersion": 1,
        "laneId": identifier,
        "problemId": lane["problemId"],
        "builderSpecDigest": lane["builderSpecDigest"],
        "baseStateRun": lane["latestStateRun"],
        "judgmentIds": selected_judgments,
        "conflictIds": selected_conflicts,
        "judgmentSetDigest": f"sha256:{sha256_json({'judgmentIds': selected_judgments, 'conflictIds': selected_conflicts})}",
    }
    if lane.get("projectionSpecDigest") is not None:
        request_core["projectionSpecDigest"] = lane["projectionSpecDigest"]
    request = {
        **request_core,
        "buildToken": f"sha256:{sha256_json(request_core)}",
        "claimedAt": now,
    }
    lane["pendingJudgmentIds"] = pending[len(selected_judgments) :]
    lane["pendingConflictIds"] = []
    lane["activeBuild"] = request
    lane["nextEligibleAt"] = None
    _atomic_json(path, state)
    return request


@_scheduler_locked
def complete_build(
    path: Path,
    identifier: str,
    build_token: str,
    state_run_digest: str,
    now: int,
) -> dict[str, object]:
    _digest(build_token, "build token")
    _digest(state_run_digest, "state run digest")
    state = load_scheduler(path)
    lane = state["lanes"].get(identifier)
    if not isinstance(lane, dict):
        raise MathFlowError("knowledge-build lane does not exist")
    active = lane.get("activeBuild")
    if not isinstance(active, dict) or active.get("buildToken") != build_token:
        raise MathFlowError("knowledge build completion does not match the active lease")
    lane["latestStateRun"] = state_run_digest
    lane["lastCompletedAt"] = now
    lane["activeBuild"] = None
    has_pending = bool(lane["pendingJudgmentIds"] or lane["pendingConflictIds"])
    lane["nextEligibleAt"] = now + int(lane["minimumIntervalSeconds"]) if has_pending else None
    _atomic_json(path, state)
    return lane


@_scheduler_locked
def fail_build(path: Path, identifier: str, build_token: str, now: int) -> dict[str, object]:
    _digest(build_token, "build token")
    state = load_scheduler(path)
    lane = state["lanes"].get(identifier)
    if not isinstance(lane, dict):
        raise MathFlowError("knowledge-build lane does not exist")
    active = lane.get("activeBuild")
    if not isinstance(active, dict) or active.get("buildToken") != build_token:
        raise MathFlowError("knowledge build failure does not match the active lease")
    lane["pendingJudgmentIds"] = sorted(
        set(lane["pendingJudgmentIds"]) | set(active["judgmentIds"])
    )
    lane["pendingConflictIds"] = sorted(
        set(lane["pendingConflictIds"]) | set(active["conflictIds"])
    )
    lane["activeBuild"] = None
    last = lane["lastCompletedAt"]
    lane["nextEligibleAt"] = max(now, int(last) + int(lane["minimumIntervalSeconds"])) if last is not None else now
    _atomic_json(path, state)
    return lane


def publish_batch(projection_root: Path, bundle_dirs: list[Path]) -> dict[str, object]:
    if not bundle_dirs:
        raise MathFlowError("projection publication requires at least one run bundle")
    root = projection_root.resolve()
    root.mkdir(parents=True, exist_ok=True)
    published: list[dict[str, object]] = []
    for bundle_dir in bundle_dirs:
        manifest, manifest_digest = verify_bundle(bundle_dir)
        run_kind = manifest.get("runKind", "legacy-projection")
        if run_kind not in {"judgment", "knowledge-build", "legacy-projection"}:
            raise MathFlowError(f"unsupported run kind for publication: {run_kind}")
        digest_hex = manifest_digest.removeprefix("sha256:")
        relative = Path("objects") / str(run_kind) / digest_hex[:2] / digest_hex
        target = root / relative
        if target.exists():
            _, stored_digest = verify_bundle(target)
            if stored_digest != manifest_digest:
                raise MathFlowError("published run object does not match its content address")
        else:
            target.parent.mkdir(parents=True, exist_ok=True)
            temporary = Path(tempfile.mkdtemp(prefix=f".{digest_hex}.", dir=target.parent))
            try:
                shutil.copytree(bundle_dir.resolve(), temporary / "bundle")
                os.replace(temporary / "bundle", target)
            finally:
                shutil.rmtree(temporary, ignore_errors=True)
        published.append(
            {
                "runDigest": manifest_digest,
                "runKind": run_kind,
                "problemId": manifest.get("problemId"),
                "path": relative.as_posix(),
            }
        )
    objects = sorted(published, key=lambda item: str(item["runDigest"]))
    batch_core = {"schemaVersion": 1, "objects": objects}
    batch_id = f"sha256:{sha256_json(batch_core)}"
    batch = {**batch_core, "batchId": batch_id}
    batch_path = root / "publication-batches" / f"{batch_id.removeprefix('sha256:')}.json"
    if not batch_path.exists():
        _atomic_json(batch_path, batch)

    by_problem: dict[str, list[dict[str, object]]] = {}
    for item in objects:
        problem = item.get("problemId")
        if isinstance(problem, str):
            validate_slug(problem, "problem id")
            by_problem.setdefault(problem, []).append(item)
    for problem, items in by_problem.items():
        index_path = root / "indexes" / "problems" / problem / "runs.json"
        existing: list[dict[str, object]] = []
        if index_path.exists():
            value = json.loads(index_path.read_text(encoding="utf-8"))
            if not isinstance(value, list) or any(not isinstance(item, dict) for item in value):
                raise MathFlowError(f"invalid projection index: {index_path}")
            existing = value
        merged = {str(item["runDigest"]): item for item in [*existing, *items]}
        _atomic_json(index_path, [merged[key] for key in sorted(merged)])
    return batch
