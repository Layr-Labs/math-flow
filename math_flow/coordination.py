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
FAILURE_INITIAL_RETRY_SECONDS = 300
FAILURE_MAX_RETRY_SECONDS = 21_600
MAX_AUTOMATIC_FAILURES = 5


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


def _validated_input_dependencies(
    judgment_ids: list[str],
    conflict_ids: list[str],
    conflict_dependencies: dict[str, list[str]] | None,
    reconciliation_dependencies: dict[str, dict[str, object]] | None,
) -> tuple[dict[str, set[str]], dict[str, tuple[str, set[str]]]]:
    judgments = set(judgment_ids)
    conflicts = set(conflict_ids)
    if len(judgments) != len(judgment_ids):
        raise MathFlowError("knowledge trigger contains duplicate judgments")
    if len(conflicts) != len(conflict_ids):
        raise MathFlowError("knowledge trigger contains duplicate conflicts")
    if conflict_dependencies is None and reconciliation_dependencies is None:
        return {}, {}
    if conflict_dependencies is None:
        raise MathFlowError(
            "reconciliation dependencies require conflict dependency records"
        )
    if set(conflict_dependencies) != conflicts:
        raise MathFlowError(
            "conflict dependency records do not match the triggered conflicts"
        )

    validated_conflicts: dict[str, set[str]] = {}
    for conflict_id, input_ids in conflict_dependencies.items():
        _digest(conflict_id, "conflict dependency ID")
        if (
            not isinstance(input_ids, list)
            or len(input_ids) < 2
            or len(input_ids) != len(set(input_ids))
        ):
            raise MathFlowError(
                f"conflict dependency must name distinct primary judgments: {conflict_id}"
            )
        inputs = {_digest(item, "conflict dependency judgment ID") for item in input_ids}
        if not inputs <= judgments:
            missing = sorted(inputs - judgments)[0]
            raise MathFlowError(
                f"conflict dependency judgment is absent from the trigger: {missing}"
            )
        validated_conflicts[conflict_id] = inputs

    validated_reconciliations: dict[str, tuple[str, set[str]]] = {}
    for reconciliation_id, dependency in (reconciliation_dependencies or {}).items():
        _digest(reconciliation_id, "reconciliation judgment ID")
        if reconciliation_id not in judgments:
            raise MathFlowError(
                "reconciliation dependency judgment is absent from the trigger: "
                f"{reconciliation_id}"
            )
        if not isinstance(dependency, dict) or set(dependency) != {
            "conflictId",
            "inputJudgmentIds",
        }:
            raise MathFlowError(
                f"reconciliation dependency is invalid: {reconciliation_id}"
            )
        conflict_id = _digest(
            dependency.get("conflictId"), "reconciliation conflict ID"
        )
        raw_inputs = dependency.get("inputJudgmentIds")
        if (
            not isinstance(raw_inputs, list)
            or len(raw_inputs) != len(set(raw_inputs))
        ):
            raise MathFlowError(
                f"reconciliation dependency inputs are invalid: {reconciliation_id}"
            )
        inputs = {
            _digest(item, "reconciliation input judgment ID") for item in raw_inputs
        }
        if conflict_id not in validated_conflicts:
            raise MathFlowError(
                f"reconciliation dependency conflict is absent from the trigger: {conflict_id}"
            )
        if inputs != validated_conflicts[conflict_id]:
            raise MathFlowError(
                "reconciliation dependency inputs do not match its conflict: "
                f"{reconciliation_id}"
            )
        validated_reconciliations[reconciliation_id] = (conflict_id, inputs)
    return validated_conflicts, validated_reconciliations


def _lane_input_dependencies(
    lane: dict[str, object],
) -> tuple[dict[str, set[str]], dict[str, tuple[str, set[str]]]]:
    raw_conflicts = lane.get("conflictDependencies")
    raw_reconciliations = lane.get("reconciliationDependencies")
    if raw_conflicts is None and raw_reconciliations is None:
        return {}, {}
    if not isinstance(raw_conflicts, dict) or not isinstance(
        raw_reconciliations, dict
    ):
        raise MathFlowError("knowledge-build lane has invalid dependency records")
    judgments = lane.get("observedJudgmentIds")
    conflicts = lane.get("observedConflictIds")
    if not isinstance(judgments, list) or not isinstance(conflicts, list):
        raise MathFlowError("knowledge-build lane has invalid observed inputs")
    if not set(raw_conflicts) <= set(conflicts):
        raise MathFlowError(
            "knowledge-build lane has a dependency for an unobserved conflict"
        )
    return _validated_input_dependencies(
        judgments,
        list(raw_conflicts),
        raw_conflicts,
        raw_reconciliations,
    )


def _persist_input_dependencies(
    lane: dict[str, object],
    conflicts: dict[str, set[str]],
    reconciliations: dict[str, tuple[str, set[str]]],
    received: bool,
) -> None:
    if not received:
        return
    stored_conflicts, stored_reconciliations = _lane_input_dependencies(lane)
    for conflict_id, input_ids in conflicts.items():
        existing = stored_conflicts.get(conflict_id)
        if existing is not None and existing != input_ids:
            raise MathFlowError(
                "conflict dependency changed for content-addressed ID: "
                f"{conflict_id}"
            )
        stored_conflicts[conflict_id] = set(input_ids)
    for reconciliation_id, dependency in reconciliations.items():
        existing = stored_reconciliations.get(reconciliation_id)
        if existing is not None and existing != dependency:
            raise MathFlowError(
                "reconciliation dependency changed for content-addressed ID: "
                f"{reconciliation_id}"
            )
        conflict_id, input_ids = dependency
        stored_reconciliations[reconciliation_id] = (
            conflict_id,
            set(input_ids),
        )
    lane["conflictDependencies"] = {
        conflict_id: sorted(input_ids)
        for conflict_id, input_ids in sorted(stored_conflicts.items())
    }
    lane["reconciliationDependencies"] = {
        reconciliation_id: {
            "conflictId": conflict_id,
            "inputJudgmentIds": sorted(input_ids),
        }
        for reconciliation_id, (conflict_id, input_ids) in sorted(
            stored_reconciliations.items()
        )
    }


def _pending_dependency_components(
    lane: dict[str, object],
    pending_judgments: list[str],
    pending_conflicts: list[str],
) -> list[tuple[set[tuple[str, str]], bool]]:
    conflict_dependencies, reconciliation_dependencies = (
        _lane_input_dependencies(lane)
    )
    missing_conflicts = set(pending_conflicts) - set(conflict_dependencies)
    if missing_conflicts:
        raise MathFlowError(
            "pending conflict has no persisted primary-judgment dependencies: "
            f"{sorted(missing_conflicts)[0]}"
        )
    pending_nodes = {
        *(("judgment", judgment_id) for judgment_id in pending_judgments),
        *(("conflict", conflict_id) for conflict_id in pending_conflicts),
    }
    pending_judgment_set = set(pending_judgments)
    pending_conflict_set = set(pending_conflicts)
    for conflict_id in pending_conflicts:
        missing_inputs = conflict_dependencies[conflict_id] - pending_judgment_set
        if missing_inputs:
            raise MathFlowError(
                "pending conflict is missing a named primary judgment: "
                f"{sorted(missing_inputs)[0]}"
            )
    for reconciliation_id in pending_judgment_set & set(
        reconciliation_dependencies
    ):
        conflict_id, input_ids = reconciliation_dependencies[reconciliation_id]
        if conflict_id not in pending_conflict_set:
            raise MathFlowError(
                "pending reconciliation is missing its named conflict: "
                f"{conflict_id}"
            )
        missing_inputs = input_ids - pending_judgment_set
        if missing_inputs:
            raise MathFlowError(
                "pending reconciliation is missing a named primary judgment: "
                f"{sorted(missing_inputs)[0]}"
            )
    adjacency: dict[tuple[str, str], set[tuple[str, str]]] = {}
    dependency_nodes: set[tuple[str, str]] = set()

    def connect(left: tuple[str, str], right: tuple[str, str]) -> None:
        adjacency.setdefault(left, set()).add(right)
        adjacency.setdefault(right, set()).add(left)
        dependency_nodes.update((left, right))

    for conflict_id, input_ids in conflict_dependencies.items():
        conflict_node = ("conflict", conflict_id)
        for judgment_id in input_ids:
            connect(conflict_node, ("judgment", judgment_id))
    for reconciliation_id, (conflict_id, input_ids) in (
        reconciliation_dependencies.items()
    ):
        reconciliation_node = ("judgment", reconciliation_id)
        conflict_node = ("conflict", conflict_id)
        connect(reconciliation_node, conflict_node)
        for judgment_id in input_ids:
            connect(reconciliation_node, ("judgment", judgment_id))

    remaining = set(pending_nodes)
    components: list[tuple[set[tuple[str, str]], bool]] = []
    while remaining:
        start = min(remaining, key=lambda item: (item[1], item[0]))
        component: set[tuple[str, str]] = set()
        frontier = [start]
        while frontier:
            node = frontier.pop()
            if node in component:
                continue
            component.add(node)
            frontier.extend(
                (adjacency.get(node, set()) & pending_nodes) - component
            )
        remaining.difference_update(component)
        components.append((component, bool(component & dependency_nodes)))
    return sorted(
        components,
        key=lambda item: tuple(sorted(item[0], key=lambda node: (node[1], node[0]))),
    )


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
    conflict_dependencies: dict[str, list[str]] | None = None,
    reconciliation_dependencies: dict[str, dict[str, object]] | None = None,
    problem_ledger_digest: str | None = None,
) -> dict[str, object]:
    if minimum_interval_seconds < 0:
        raise MathFlowError("minimum knowledge-build interval cannot be negative")
    if now < 0:
        raise MathFlowError("scheduler time cannot be negative")
    for judgment_id in judgment_ids:
        _digest(judgment_id, "judgment ID")
    for conflict_id in conflict_ids:
        _digest(conflict_id, "conflict ID")
    if problem_ledger_digest is not None:
        _digest(problem_ledger_digest, "problem ledger digest")
    validated_conflicts, validated_reconciliations = _validated_input_dependencies(
        judgment_ids,
        conflict_ids,
        conflict_dependencies,
        reconciliation_dependencies,
    )
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
    elif lane.get("builderSpecDigest") != builder_spec_digest:
        raise MathFlowError(
            "knowledge-build lane builder digest changed without a new projection identity"
        )
    elif lane.get("minimumIntervalSeconds") != minimum_interval_seconds:
        raise MathFlowError("knowledge-build lane interval does not match its existing policy")
    _persist_input_dependencies(
        lane,
        validated_conflicts,
        validated_reconciliations,
        conflict_dependencies is not None or reconciliation_dependencies is not None,
    )
    observed_judgments = set(lane.setdefault("observedJudgmentIds", []))
    observed_conflicts = set(lane.setdefault("observedConflictIds", []))
    new_judgments = set(judgment_ids) - observed_judgments
    new_conflicts = set(conflict_ids) - observed_conflicts
    prior_failure = lane.get("lastFailure")
    ledger_changed = (
        isinstance(prior_failure, dict)
        and problem_ledger_digest is not None
        and prior_failure.get("problemLedgerDigest") != problem_ledger_digest
    )
    if (
        new_judgments or new_conflicts or ledger_changed
    ) and prior_failure is not None:
        lane.pop("lastFailure", None)
        if lane.get("activeBuild") is None:
            lane["nextEligibleAt"] = now
    observed_judgments.update(judgment_ids)
    observed_conflicts.update(conflict_ids)
    lane["observedJudgmentIds"] = sorted(observed_judgments)
    lane["observedConflictIds"] = sorted(observed_conflicts)
    pending_judgments = set(lane["pendingJudgmentIds"])
    pending_judgments.update(new_judgments)
    pending_conflicts = set(lane["pendingConflictIds"])
    pending_conflicts.update(new_conflicts)
    for conflict_id in new_conflicts:
        pending_judgments.update(validated_conflicts.get(conflict_id, set()))
    for reconciliation_id in new_judgments:
        dependency = validated_reconciliations.get(reconciliation_id)
        if dependency is None:
            continue
        conflict_id, input_judgment_ids = dependency
        pending_conflicts.add(conflict_id)
        pending_judgments.update(input_judgment_ids)
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
    components = _pending_dependency_components(lane, pending, conflicts)
    for component, dependency_bearing in components:
        judgment_count = sum(kind == "judgment" for kind, _ in component)
        if dependency_bearing and judgment_count > maximum_judgments:
            component_ids = sorted(identifier for _, identifier in component)
            raise MathFlowError(
                "knowledge-build dependency component exceeds maximum judgments "
                f"per build ({judgment_count} > {maximum_judgments}): "
                f"{component_ids[0]}"
            )

    selected_nodes: set[tuple[str, str]] = set()
    remaining_capacity = maximum_judgments
    for component, _ in components:
        judgment_count = sum(kind == "judgment" for kind, _ in component)
        if judgment_count <= remaining_capacity:
            selected_nodes.update(component)
            remaining_capacity -= judgment_count
    selected_judgments = sorted(
        identifier
        for kind, identifier in selected_nodes
        if kind == "judgment"
    )
    selected_conflicts = sorted(
        identifier
        for kind, identifier in selected_nodes
        if kind == "conflict"
    )
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
    lane["pendingJudgmentIds"] = sorted(
        set(pending) - set(selected_judgments)
    )
    lane["pendingConflictIds"] = sorted(
        set(conflicts) - set(selected_conflicts)
    )
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
    lane.pop("lastFailure", None)
    has_pending = bool(lane["pendingJudgmentIds"] or lane["pendingConflictIds"])
    lane["nextEligibleAt"] = now + int(lane["minimumIntervalSeconds"]) if has_pending else None
    _atomic_json(path, state)
    return lane


@_scheduler_locked
def fail_build(
    path: Path,
    identifier: str,
    build_token: str,
    now: int,
    problem_ledger_digest: str | None = None,
) -> dict[str, object]:
    _digest(build_token, "build token")
    if now < 0:
        raise MathFlowError("knowledge build failure time cannot be negative")
    if problem_ledger_digest is not None:
        _digest(problem_ledger_digest, "problem ledger digest")
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
    prior = lane.get("lastFailure")
    consecutive = 1
    if (
        isinstance(prior, dict)
        and prior.get("buildToken") == build_token
        and prior.get("problemLedgerDigest") == problem_ledger_digest
    ):
        prior_failed_at = prior.get("failedAt")
        if not isinstance(prior_failed_at, int) or now < prior_failed_at:
            raise MathFlowError("knowledge build failure time precedes its prior failure")
        prior_count = prior.get("consecutiveFailures")
        if not isinstance(prior_count, int) or isinstance(prior_count, bool):
            raise MathFlowError("knowledge build lane has an invalid prior failure")
        consecutive = prior_count + 1
    exponent = min(consecutive - 1, 30)
    retry_delay = min(
        FAILURE_INITIAL_RETRY_SECONDS * (2**exponent),
        FAILURE_MAX_RETRY_SECONDS,
    )
    last = lane["lastCompletedAt"]
    retry_not_before = now + retry_delay
    if last is not None:
        retry_not_before = max(
            retry_not_before,
            int(last) + int(lane["minimumIntervalSeconds"]),
        )
    lane["nextEligibleAt"] = retry_not_before
    lane["lastFailure"] = {
        "schemaVersion": 1,
        "laneId": identifier,
        "buildToken": build_token,
        "problemLedgerDigest": problem_ledger_digest,
        "failedAt": now,
        "consecutiveFailures": consecutive,
        "retryNotBefore": retry_not_before,
    }
    _atomic_json(path, state)
    return lane


def publish_batch(projection_root: Path, bundle_dirs: list[Path]) -> dict[str, object]:
    if not bundle_dirs:
        raise MathFlowError("projection publication requires at least one run bundle")
    root = projection_root.resolve()
    incoming_attestations: dict[tuple[str, str, str], str] = {}
    for bundle_dir in bundle_dirs:
        manifest, _ = verify_bundle(bundle_dir)
        if manifest.get("runKind") != "verifier-attestation":
            continue
        from .attestations import assert_attestation_publication_unique

        identity = assert_attestation_publication_unique(root, bundle_dir)
        key = (
            identity["problemId"],
            identity["transactionId"],
            identity["requestDigest"],
        )
        prior = incoming_attestations.get(key)
        if prior is not None and prior != identity["runDigest"]:
            raise MathFlowError(
                "publication batch contains different outcomes for one objective verification request"
            )
        incoming_attestations[key] = identity["runDigest"]
    root.mkdir(parents=True, exist_ok=True)
    published: list[dict[str, object]] = []
    for bundle_dir in bundle_dirs:
        manifest, manifest_digest = verify_bundle(bundle_dir)
        run_kind = manifest.get("runKind", "legacy-projection")
        if run_kind not in {
            "credit-assignment",
            "judgment",
            "knowledge-build",
            "legacy-projection",
            "verifier-attestation",
        }:
            raise MathFlowError(f"unsupported run kind for publication: {run_kind}")
        manifest_inputs = manifest.get("inputs")
        if (
            run_kind == "credit-assignment"
            and isinstance(manifest_inputs, dict)
            and manifest_inputs.get("schedule") is not None
        ):
            from .credit_schedule import assert_credit_publication_unique

            assert_credit_publication_unique(root, bundle_dir)
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
