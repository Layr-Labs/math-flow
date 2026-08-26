"""Inactive hosted dispatch and prepublication planning for work accounting V1."""

from __future__ import annotations

import copy
import json
import re
from collections.abc import Mapping
from pathlib import Path, PurePosixPath

from .artifacts import sha256_bytes
from .errors import MathFlowError
from .governed_providers import TRANSPORT_IDENTITY
from .judges import load_judge_spec
from .repository import ledger, resolve_commit, sha256_json
from .work_accounting_pipeline import validate_work_accounting_pipeline_state
from .work_accounting_schedule import validate_work_accounting_schedule


DIGEST = re.compile(r"^sha256:[0-9a-f]{64}$")
GIT_SHA = re.compile(r"^[0-9a-f]{40}$")
IDENTIFIER = re.compile(r"^[a-z0-9][a-z0-9/_-]*$")

CONFIG_FIELDS = {
    "schemaVersion",
    "id",
    "status",
    "projectionId",
    "knowledgeProjectionId",
    "builderSpec",
    "workProviderSpec",
    "transport",
    "runner",
    "retryPolicy",
    "hostedBatching",
    "runtimePolicyDigest",
    "configDigest",
}
SPEC_FIELDS = {"path", "id", "implementation", "digest"}
TRANSPORT_FIELDS = {"implementation", "endpoint", "digest"}
RUNNER_FIELDS = {"implementation", "path", "digest"}
RETRY_FIELDS = {
    "mode",
    "maximumAttempts",
    "baseRetrySeconds",
    "staleClaimSeconds",
    "manualReview",
}
BATCH_FIELDS = {"maximumSubjectsPerRun", "semanticEffect"}

SNAPSHOT_FIELDS = {
    "schemaVersion",
    "problemId",
    "canonicalHead",
    "problemLedgerDigest",
    "knowledgeProjectionId",
    "knowledgeBuilderSpecDigest",
    "subjects",
    "snapshotDigest",
}
DISPOSITION_FIELDS = {
    "transactionId",
    "ledgerOrdinal",
    "status",
    "judgmentId",
    "acceptedSubmissionInputDigest",
}
DISPOSITIONS = {"pending", "accepted", "rejected", "indeterminate"}

HISTORY_FIELDS = {"schemaVersion", "runs", "historyDigest"}
RUN_FIELDS = {
    "runId",
    "semanticDispatchKey",
    "subjectTransactionId",
    "status",
    "conclusion",
    "startedAt",
    "completedAt",
}
ACTIVE_STATUSES = {"queued", "in_progress"}
CONCLUSIONS = {"success", "failure", "cancelled", "timed_out"}

PLAN_FIELDS = {
    "schemaVersion",
    "eligible",
    "reasonCode",
    "message",
    "nextEligibleAt",
    "configuration",
    "problemId",
    "projectionId",
    "canonicalHead",
    "problemLedgerDigest",
    "projectionHead",
    "projectionStateDigest",
    "rootContractDigest",
    "pipelineStateDigest",
    "scheduleDigest",
    "dispositionSnapshotDigest",
    "subjectTransactionId",
    "ledgerOrdinal",
    "acceptedSubmissionInputDigest",
    "judgmentId",
    "predecessorAccountingStateDigest",
    "predecessorKnowledgeStateDigest",
    "mode",
    "semanticDispatchKey",
    "automaticAttemptNumber",
    "maximumSubjectsPerRun",
    "manualReview",
    "dispatchDigest",
}

CHECK_FIELDS = {
    "schemaVersion",
    "publishable",
    "reasonCode",
    "message",
    "subjectTransactionId",
    "originalDispatchDigest",
    "currentSemanticDispatchKey",
    "checkDigest",
}


def _digest(value: object) -> str:
    try:
        return f"sha256:{sha256_json(value)}"
    except (TypeError, ValueError) as exc:
        raise MathFlowError("work dispatch data must be canonical JSON") from exc


def _without(value: Mapping[str, object], *fields: str) -> dict[str, object]:
    return {
        key: copy.deepcopy(item)
        for key, item in value.items()
        if key not in fields
    }


def _require_digest(value: object, label: str) -> str:
    if not isinstance(value, str) or not DIGEST.fullmatch(value):
        raise MathFlowError(f"{label} must be a sha256 digest")
    return value


def _require_transaction(value: object, label: str) -> str:
    if not isinstance(value, str) or not GIT_SHA.fullmatch(value):
        raise MathFlowError(f"{label} must be an exact transaction ID")
    return value


def _require_identifier(value: object, label: str) -> str:
    if not isinstance(value, str) or not IDENTIFIER.fullmatch(value):
        raise MathFlowError(f"{label} must be a stable lowercase identifier")
    return value


def _positive_integer(value: object, label: str, maximum: int) -> int:
    if (
        not isinstance(value, int)
        or isinstance(value, bool)
        or not 1 <= value <= maximum
    ):
        raise MathFlowError(f"{label} must be between 1 and {maximum}")
    return value


def _nonnegative_integer(value: object, label: str) -> int:
    if not isinstance(value, int) or isinstance(value, bool) or value < 0:
        raise MathFlowError(f"{label} must be a non-negative integer")
    return value


def _repository_path(value: object, label: str) -> str:
    if not isinstance(value, str) or not value:
        raise MathFlowError(f"{label} must be a repository path")
    path = PurePosixPath(value)
    if (
        path.is_absolute()
        or path.as_posix() != value
        or any(part in {"", ".", ".."} for part in path.parts)
    ):
        raise MathFlowError(f"{label} is unsafe")
    return value


def _runtime_policy_core(config: Mapping[str, object]) -> dict[str, object]:
    return {
        key: copy.deepcopy(config[key])
        for key in (
            "schemaVersion",
            "id",
            "projectionId",
            "knowledgeProjectionId",
            "builderSpec",
            "workProviderSpec",
            "transport",
            "runner",
            "retryPolicy",
        )
    }


def load_work_accounting_hosted_config(
    root: Path, path: Path
) -> dict[str, object]:
    """Load one inactive config and verify every executable identity by content."""

    root = root.resolve()
    try:
        config = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise MathFlowError(f"could not read hosted work-accounting config: {exc}") from exc
    if not isinstance(config, dict) or set(config) != CONFIG_FIELDS:
        raise MathFlowError("hosted work-accounting config has an invalid envelope")
    if (
        config.get("schemaVersion") != 1
        or config.get("status") != "inactive"
        or config.get("id") != "inactive-work-accounting-hosted-v1"
    ):
        raise MathFlowError("hosted work-accounting config must remain inactive V1")
    _require_identifier(config.get("projectionId"), "hosted work projection ID")
    _require_identifier(
        config.get("knowledgeProjectionId"), "hosted knowledge projection ID"
    )

    expected_specs = (
        (
            "builderSpec",
            "openrouter-hierarchical-research-builder-v6",
        ),
        ("workProviderSpec", "openrouter-work-accounting-v1"),
    )
    for field, implementation in expected_specs:
        binding = config.get(field)
        if not isinstance(binding, dict) or set(binding) != SPEC_FIELDS:
            raise MathFlowError(f"hosted {field} binding is invalid")
        relative = _repository_path(binding.get("path"), f"hosted {field} path")
        spec = load_judge_spec(root / relative)
        if (
            spec.get("id") != binding.get("id")
            or spec.get("implementation") != implementation
            or binding.get("implementation") != implementation
            or binding.get("digest") != _digest(spec)
        ):
            raise MathFlowError(f"hosted {field} identity binding mismatch")

    transport = config.get("transport")
    if not isinstance(transport, dict) or set(transport) != TRANSPORT_FIELDS:
        raise MathFlowError("hosted transport identity is invalid")
    if (
        _without(transport, "digest") != TRANSPORT_IDENTITY
        or transport.get("digest") != _digest(TRANSPORT_IDENTITY)
    ):
        raise MathFlowError("hosted transport identity binding mismatch")

    runner = config.get("runner")
    if not isinstance(runner, dict) or set(runner) != RUNNER_FIELDS:
        raise MathFlowError("hosted runner identity is invalid")
    relative_runner = _repository_path(runner.get("path"), "hosted runner path")
    runner_path = root / relative_runner
    if (
        runner.get("implementation") != "work-accounting-pipeline-v1"
        or not runner_path.is_file()
        or runner.get("digest") != sha256_bytes(runner_path.read_bytes())
    ):
        raise MathFlowError("hosted runner identity binding mismatch")

    retry = config.get("retryPolicy")
    if (
        not isinstance(retry, dict)
        or set(retry) != RETRY_FIELDS
        or retry.get("mode") != "automatic"
        or retry.get("manualReview") is not False
    ):
        raise MathFlowError("hosted retries must be automatic with no manual review")
    _positive_integer(retry.get("maximumAttempts"), "hosted maximum attempts", 10)
    _positive_integer(
        retry.get("baseRetrySeconds"), "hosted retry base seconds", 86_400
    )
    _positive_integer(
        retry.get("staleClaimSeconds"), "hosted stale claim seconds", 604_800
    )
    batching = config.get("hostedBatching")
    if (
        not isinstance(batching, dict)
        or set(batching) != BATCH_FIELDS
        or batching.get("semanticEffect") != "none"
    ):
        raise MathFlowError("hosted batching must be explicitly non-semantic")
    _positive_integer(
        batching.get("maximumSubjectsPerRun"),
        "hosted maximum subjects per run",
        500,
    )
    if config.get("runtimePolicyDigest") != _digest(_runtime_policy_core(config)):
        raise MathFlowError("hosted runtime policy digest mismatch")
    if config.get("configDigest") != _digest(_without(config, "configDigest")):
        raise MathFlowError("hosted config digest mismatch")
    return config


def validate_work_disposition_snapshot(
    value: object,
    root: Path,
    *,
    config: Mapping[str, object],
) -> dict[str, object]:
    if not isinstance(value, dict) or set(value) != SNAPSHOT_FIELDS:
        raise MathFlowError("work disposition snapshot has an invalid envelope")
    if value.get("schemaVersion") != 1:
        raise MathFlowError("work disposition snapshot has an unsupported version")
    problem = _require_identifier(value.get("problemId"), "disposition problem")
    head = _require_transaction(value.get("canonicalHead"), "disposition head")
    if resolve_commit(root.resolve(), head) != head:
        raise MathFlowError("work disposition head is not exact")
    canonical = ledger(root.resolve(), problem, head)
    if value.get("problemLedgerDigest") != canonical.get("problemLedgerDigest"):
        raise MathFlowError("work disposition ledger binding mismatch")
    if (
        value.get("knowledgeProjectionId") != config.get("knowledgeProjectionId")
        or value.get("knowledgeBuilderSpecDigest")
        != config["builderSpec"]["digest"]  # type: ignore[index]
    ):
        raise MathFlowError("work disposition knowledge identity mismatch")
    subjects = value.get("subjects")
    transactions = canonical.get("transactions")
    if not isinstance(subjects, list) or not isinstance(transactions, list):
        raise MathFlowError("work disposition subjects are invalid")
    expected = [
        (str(item["transactionId"]), int(item["ordinal"])) for item in transactions
    ]
    observed: list[tuple[str, int]] = []
    for item in subjects:
        if not isinstance(item, dict) or set(item) != DISPOSITION_FIELDS:
            raise MathFlowError("work disposition subject has an invalid envelope")
        transaction_id = _require_transaction(
            item.get("transactionId"), "disposition subject"
        )
        ordinal = _positive_integer(
            item.get("ledgerOrdinal"), "disposition ordinal", 10**12
        )
        observed.append((transaction_id, ordinal))
        status = item.get("status")
        if status not in DISPOSITIONS:
            raise MathFlowError("work disposition status is invalid")
        judgment = item.get("judgmentId")
        submission = item.get("acceptedSubmissionInputDigest")
        if status == "pending":
            if judgment is not None or submission is not None:
                raise MathFlowError("pending disposition may not bind terminal artifacts")
        else:
            _require_digest(judgment, "terminal disposition judgment")
            if status == "accepted":
                _require_digest(submission, "accepted submission input")
            elif submission is not None:
                raise MathFlowError("excluded disposition may not carry accepted input")
    if observed != expected:
        raise MathFlowError("work dispositions must cover exact canonical ledger order")
    if value.get("snapshotDigest") != _digest(_without(value, "snapshotDigest")):
        raise MathFlowError("work disposition snapshot digest mismatch")
    return value


def validate_work_dispatch_history(value: object) -> dict[str, object]:
    if not isinstance(value, dict) or set(value) != HISTORY_FIELDS:
        raise MathFlowError("work dispatch history has an invalid envelope")
    if value.get("schemaVersion") != 1 or not isinstance(value.get("runs"), list):
        raise MathFlowError("work dispatch history has an invalid version or runs")
    previous: tuple[int, int] | None = None
    run_ids: set[int] = set()
    for run in value["runs"]:
        if not isinstance(run, dict) or set(run) != RUN_FIELDS:
            raise MathFlowError("work dispatch history run has an invalid envelope")
        run_id = _positive_integer(run.get("runId"), "work dispatch run ID", 10**18)
        if run_id in run_ids:
            raise MathFlowError("work dispatch history repeats a run ID")
        run_ids.add(run_id)
        _require_digest(run.get("semanticDispatchKey"), "history dispatch key")
        _require_transaction(run.get("subjectTransactionId"), "history subject")
        started = _nonnegative_integer(run.get("startedAt"), "history start time")
        ordering = (started, run_id)
        if previous is not None and ordering <= previous:
            raise MathFlowError("work dispatch history is not canonical")
        previous = ordering
        status = run.get("status")
        conclusion = run.get("conclusion")
        completed = run.get("completedAt")
        if status in ACTIVE_STATUSES:
            if conclusion is not None or completed is not None:
                raise MathFlowError("active work dispatch has terminal fields")
        elif status == "completed":
            if conclusion not in CONCLUSIONS:
                raise MathFlowError("completed work dispatch has invalid conclusion")
            completed_at = _nonnegative_integer(completed, "history completion time")
            if completed_at < started:
                raise MathFlowError("work dispatch completes before it starts")
        else:
            raise MathFlowError("work dispatch history status is invalid")
    if value.get("historyDigest") != _digest(_without(value, "historyDigest")):
        raise MathFlowError("work dispatch history digest mismatch")
    return value


def empty_work_dispatch_history() -> dict[str, object]:
    core: dict[str, object] = {"schemaVersion": 1, "runs": []}
    return {**core, "historyDigest": _digest(core)}


def _validate_lane(
    config: Mapping[str, object],
    pipeline_value: object,
    schedule_value: object,
) -> tuple[dict[str, object], dict[str, object]]:
    pipeline = validate_work_accounting_pipeline_state(pipeline_value)
    schedule = validate_work_accounting_schedule(schedule_value)
    if (
        pipeline["projectionId"] != config["projectionId"]
        or schedule["projectionId"] != config["projectionId"]
        or pipeline["projectionSpecDigest"] != config["runtimePolicyDigest"]
        or schedule["projectionSpecDigest"] != config["runtimePolicyDigest"]
        or pipeline["scheduleDigest"] != schedule["scheduleDigest"]
        or pipeline["problemId"] != schedule["problemId"]
        or pipeline["rootContractDigest"] != schedule["rootContractDigest"]
        or pipeline["accountingStateDigest"]
        != schedule["terminalAccountingStateDigest"]
    ):
        raise MathFlowError("hosted dispatch lane identity binding mismatch")
    return pipeline, schedule


def _frontier(
    pipeline: Mapping[str, object],
    schedule: Mapping[str, object],
    snapshot: Mapping[str, object],
) -> tuple[dict[str, object] | None, str, int | None, str]:
    dispositions = snapshot["subjects"]
    assert isinstance(dispositions, list)
    accepted = [item for item in dispositions if item["status"] == "accepted"]
    completed = [
        str(item["subjectTransactionId"])
        for item in pipeline["completedTransitions"]
    ]
    accepted_ids = [str(item["transactionId"]) for item in accepted]
    if completed != accepted_ids[: len(completed)]:
        raise MathFlowError("hosted accounting history is not an accepted canonical prefix")
    candidate = next(
        (item for item in accepted if item["transactionId"] not in set(completed)),
        None,
    )
    if candidate is None:
        return None, "no-accepted-submission", None, "new-subject"
    candidate_id = str(candidate["transactionId"])
    candidate_ordinal = int(candidate["ledgerOrdinal"])
    unresolved = next(
        (
            item
            for item in dispositions
            if int(item["ledgerOrdinal"]) < candidate_ordinal
            and item["status"] == "pending"
        ),
        None,
    )
    if unresolved is not None:
        return (
            None,
            "earlier-canonical-submission-unresolved",
            None,
            "new-subject",
        )
    pending = pipeline.get("pendingTransition")
    mode = "new-subject"
    if pipeline.get("phase") != "ready":
        if not isinstance(pending, dict) or pending.get("subjectTransactionId") != candidate_id:
            raise MathFlowError("pending hosted transition is not the canonical frontier")
        mode = "resume-pending"
        schedule_frontier = next(
            (item for item in schedule["subjects"] if item["completion"] is None),
            None,
        )
        if (
            not isinstance(schedule_frontier, dict)
            or schedule_frontier.get("transactionId") != candidate_id
        ):
            raise MathFlowError("hosted schedule frontier differs from pending transition")
        failures = schedule_frontier["failureHistory"]
        if failures:
            last = failures[-1]
            if last["exhausted"]:
                return None, "automatic-retries-exhausted", None, mode
            return candidate, "schedule-retry", last["retryNotBefore"], mode
    return candidate, "eligible", None, mode


def _semantic_key(
    *,
    config: Mapping[str, object],
    snapshot: Mapping[str, object],
    pipeline: Mapping[str, object],
    schedule: Mapping[str, object],
    candidate: Mapping[str, object],
    projection_head: str,
    projection_state_digest: str,
) -> str:
    pending = pipeline.get("pendingTransition")
    predecessor_knowledge = (
        pending["beforeKnowledgeStateDigest"]
        if isinstance(pending, dict)
        else pipeline["formedKnowledgeStateDigest"]
    )
    return _digest(
        {
            "runtimePolicyDigest": config["runtimePolicyDigest"],
            "canonicalHead": snapshot["canonicalHead"],
            "problemLedgerDigest": snapshot["problemLedgerDigest"],
            "projectionHead": projection_head,
            "projectionStateDigest": projection_state_digest,
            "rootContractDigest": pipeline["rootContractDigest"],
            "pipelineStateDigest": pipeline["pipelineStateDigest"],
            "scheduleDigest": schedule["scheduleDigest"],
            "dispositionSnapshotDigest": snapshot["snapshotDigest"],
            "subjectTransactionId": candidate["transactionId"],
            "acceptedSubmissionInputDigest": candidate[
                "acceptedSubmissionInputDigest"
            ],
            "judgmentId": candidate["judgmentId"],
            "predecessorAccountingStateDigest": pipeline["accountingStateDigest"],
            "predecessorKnowledgeStateDigest": predecessor_knowledge,
            "builderSpecDigest": config["builderSpec"]["digest"],  # type: ignore[index]
            "workProviderSpecDigest": config["workProviderSpec"]["digest"],  # type: ignore[index]
        }
    )


def _history_gate(
    history: Mapping[str, object],
    *,
    semantic_key: str,
    subject_transaction_id: str,
    as_of: int,
    retry_policy: Mapping[str, object],
) -> tuple[bool, str, int | None, int, str]:
    matching = [
        run for run in history["runs"] if run["semanticDispatchKey"] == semantic_key
    ]
    if any(
        run["subjectTransactionId"] != subject_transaction_id for run in matching
    ):
        raise MathFlowError("matching hosted dispatch history names another subject")
    stale_after = int(retry_policy["staleClaimSeconds"])
    active = [run for run in matching if run["status"] in ACTIVE_STATUSES]
    live_active = next(
        (run for run in active if as_of < int(run["startedAt"]) + stale_after),
        None,
    )
    if live_active is not None:
        return (
            False,
            "matching-dispatch-active",
            int(live_active["startedAt"]) + stale_after,
            0,
            "new-subject",
        )
    stale_claims = [run for run in active if run is not live_active]
    completed = [run for run in matching if run["status"] == "completed"]
    maximum = int(retry_policy["maximumAttempts"])
    base = int(retry_policy["baseRetrySeconds"])
    prior_attempts = len(completed) + len(stale_claims)
    if prior_attempts >= maximum:
        return False, "hosted-retries-exhausted", None, prior_attempts, "new-subject"
    latest_prior = (
        max(
            completed + stale_claims,
            key=lambda run: (int(run["startedAt"]), int(run["runId"])),
        )
        if prior_attempts
        else None
    )
    if latest_prior is not None and latest_prior["status"] == "completed":
        retry_at = int(latest_prior["completedAt"]) + base * (2 ** (prior_attempts - 1))
        recovery_mode = (
            "recover-stale-success"
            if latest_prior["conclusion"] == "success"
            else "new-subject"
        )
        if as_of < retry_at:
            reason = (
                "stale-success-recovery-backoff"
                if recovery_mode == "recover-stale-success"
                else "hosted-retry-backoff-active"
            )
            return False, reason, retry_at, prior_attempts, recovery_mode
        return True, "eligible", None, prior_attempts + 1, recovery_mode
    if latest_prior is not None:
        return True, "eligible", None, prior_attempts + 1, "recover-stale-claim"
    return True, "eligible", None, 1, "new-subject"


def _seal_plan(value: Mapping[str, object]) -> dict[str, object]:
    core = _without(value, "dispatchDigest")
    return validate_work_accounting_dispatch_plan(
        {**core, "dispatchDigest": _digest(core)}
    )


def validate_work_accounting_dispatch_plan(value: object) -> dict[str, object]:
    if not isinstance(value, dict) or set(value) != PLAN_FIELDS:
        raise MathFlowError("work-accounting dispatch plan has an invalid envelope")
    if value.get("schemaVersion") != 1 or not isinstance(value.get("eligible"), bool):
        raise MathFlowError("work-accounting dispatch plan has an invalid version")
    for field in ("reasonCode", "message"):
        if not isinstance(value.get(field), str) or not value[field]:
            raise MathFlowError("work-accounting dispatch plan has invalid text")
    for field in (
        "problemId",
        "projectionId",
    ):
        _require_identifier(value.get(field), f"dispatch plan {field}")
    for field in ("canonicalHead", "projectionHead"):
        _require_transaction(value.get(field), f"dispatch plan {field}")
    for field in (
        "problemLedgerDigest",
        "projectionStateDigest",
        "rootContractDigest",
        "pipelineStateDigest",
        "scheduleDigest",
        "dispositionSnapshotDigest",
    ):
        _require_digest(value.get(field), f"dispatch plan {field}")
    config = value.get("configuration")
    if not isinstance(config, dict) or set(config) != {
        "id",
        "configDigest",
        "runtimePolicyDigest",
        "builderSpecDigest",
        "workProviderSpecDigest",
        "transportDigest",
        "runnerDigest",
    }:
        raise MathFlowError("dispatch plan configuration binding is invalid")
    for field in set(config) - {"id"}:
        _require_digest(config.get(field), f"dispatch plan configuration {field}")
    if config.get("id") != "inactive-work-accounting-hosted-v1":
        raise MathFlowError("dispatch plan configuration ID is invalid")
    if value.get("manualReview") is not False:
        raise MathFlowError("work-accounting dispatch may not use manual review")
    _positive_integer(
        value.get("maximumSubjectsPerRun"), "dispatch batch limit", 500
    )
    next_at = value.get("nextEligibleAt")
    if next_at is not None:
        _nonnegative_integer(next_at, "dispatch next eligible time")
    optional_digests = (
        "acceptedSubmissionInputDigest",
        "judgmentId",
        "semanticDispatchKey",
    )
    if value["eligible"]:
        _require_transaction(value.get("subjectTransactionId"), "dispatch subject")
        _positive_integer(value.get("ledgerOrdinal"), "dispatch ordinal", 10**12)
        for field in optional_digests:
            _require_digest(value.get(field), f"dispatch {field}")
        _require_digest(
            value.get("predecessorAccountingStateDigest"),
            "dispatch predecessor accounting state",
        )
        _require_digest(
            value.get("predecessorKnowledgeStateDigest"),
            "dispatch predecessor knowledge state",
        )
        _positive_integer(
            value.get("automaticAttemptNumber"), "dispatch attempt", 10
        )
        if value.get("mode") not in {
            "new-subject",
            "resume-pending",
            "recover-stale-claim",
            "recover-stale-success",
        }:
            raise MathFlowError("dispatch mode is invalid")
    elif any(
        value.get(field) is not None
        for field in (
            "subjectTransactionId",
            "ledgerOrdinal",
            *optional_digests,
            "predecessorAccountingStateDigest",
            "predecessorKnowledgeStateDigest",
            "mode",
            "automaticAttemptNumber",
        )
    ):
        raise MathFlowError("ineligible work dispatch carries subject authorization")
    if value.get("dispatchDigest") != _digest(_without(value, "dispatchDigest")):
        raise MathFlowError("work-accounting dispatch digest mismatch")
    return value


def plan_work_accounting_dispatch(
    root: Path,
    *,
    config: Mapping[str, object],
    pipeline_state: object,
    schedule: object,
    disposition_snapshot: object,
    run_history: object,
    canonical_head: str,
    projection_head: str,
    projection_state_digest: str,
    as_of: int,
    target_subject_transaction_id: str | None = None,
) -> dict[str, object]:
    """Authorize at most one exact canonical frontier for automatic hosted work."""

    pipeline, current_schedule = _validate_lane(config, pipeline_state, schedule)
    snapshot = validate_work_disposition_snapshot(
        disposition_snapshot, root, config=config
    )
    history = validate_work_dispatch_history(run_history)
    exact_canonical_head = _require_transaction(
        canonical_head, "hosted canonical head"
    )
    if (
        resolve_commit(root.resolve(), exact_canonical_head) != exact_canonical_head
        or snapshot["canonicalHead"] != exact_canonical_head
    ):
        raise MathFlowError("hosted canonical head does not match the disposition snapshot")
    _require_transaction(projection_head, "hosted projection head")
    _require_digest(projection_state_digest, "hosted projection state")
    now = _nonnegative_integer(as_of, "hosted dispatch time")
    if pipeline["problemId"] != snapshot["problemId"]:
        raise MathFlowError("hosted disposition snapshot belongs to another lane")
    target = (
        _require_transaction(target_subject_transaction_id, "target subject")
        if target_subject_transaction_id is not None
        else None
    )
    candidate, reason, schedule_retry_at, mode = _frontier(
        pipeline, current_schedule, snapshot
    )
    eligible = candidate is not None
    next_at = None
    attempt: int | None = None
    semantic_key: str | None = None
    if candidate is not None and target is not None and candidate["transactionId"] != target:
        eligible = False
        reason = "target-is-not-canonical-frontier"
    if eligible and schedule_retry_at is not None:
        next_at = int(schedule_retry_at)
        if now < next_at:
            eligible = False
            reason = "schedule-retry-backoff-active"
    if eligible and candidate is not None:
        semantic_key = _semantic_key(
            config=config,
            snapshot=snapshot,
            pipeline=pipeline,
            schedule=current_schedule,
            candidate=candidate,
            projection_head=projection_head,
            projection_state_digest=projection_state_digest,
        )
        allowed, history_reason, history_next, attempt_value, history_mode = (
            _history_gate(
                history,
                semantic_key=semantic_key,
                subject_transaction_id=str(candidate["transactionId"]),
                as_of=now,
                retry_policy=config["retryPolicy"],  # type: ignore[arg-type]
            )
        )
        attempt = attempt_value
        if not allowed:
            eligible = False
            reason = history_reason
            next_at = history_next
        elif history_mode in {"recover-stale-claim", "recover-stale-success"}:
            mode = history_mode
    messages = {
        "eligible": "The exact canonical accounting frontier is eligible.",
        "no-accepted-submission": "No accepted unprocessed submission is ready.",
        "earlier-canonical-submission-unresolved": "An earlier canonical submission has no terminal validity disposition.",
        "automatic-retries-exhausted": "The accounting scheduler exhausted automatic retries.",
        "schedule-retry-backoff-active": "The accounting scheduler retry backoff has not elapsed.",
        "target-is-not-canonical-frontier": "The requested subject is not the exact canonical accounting frontier.",
        "matching-dispatch-active": "An exact matching hosted dispatch is already active.",
        "hosted-retries-exhausted": "Hosted automatic recovery exhausted its retry budget.",
        "hosted-retry-backoff-active": "Hosted automatic recovery backoff has not elapsed.",
        "stale-success-recovery-backoff": "A successful run did not advance state; recovery backoff has not elapsed.",
    }
    if not eligible:
        candidate_for_output = None
        semantic_for_output = None
        attempt_for_output = None
        mode_for_output = None
    else:
        candidate_for_output = candidate
        semantic_for_output = semantic_key
        attempt_for_output = attempt
        mode_for_output = mode
        reason = "eligible"
        next_at = None
    pending = pipeline.get("pendingTransition")
    predecessor_knowledge = (
        pending["beforeKnowledgeStateDigest"]
        if isinstance(pending, dict)
        else pipeline["formedKnowledgeStateDigest"]
    )
    return _seal_plan(
        {
            "schemaVersion": 1,
            "eligible": eligible,
            "reasonCode": reason,
            "message": messages[reason],
            "nextEligibleAt": next_at,
            "configuration": {
                "id": config["id"],
                "configDigest": config["configDigest"],
                "runtimePolicyDigest": config["runtimePolicyDigest"],
                "builderSpecDigest": config["builderSpec"]["digest"],  # type: ignore[index]
                "workProviderSpecDigest": config["workProviderSpec"]["digest"],  # type: ignore[index]
                "transportDigest": config["transport"]["digest"],  # type: ignore[index]
                "runnerDigest": config["runner"]["digest"],  # type: ignore[index]
            },
            "problemId": pipeline["problemId"],
            "projectionId": pipeline["projectionId"],
            "canonicalHead": snapshot["canonicalHead"],
            "problemLedgerDigest": snapshot["problemLedgerDigest"],
            "projectionHead": projection_head,
            "projectionStateDigest": projection_state_digest,
            "rootContractDigest": pipeline["rootContractDigest"],
            "pipelineStateDigest": pipeline["pipelineStateDigest"],
            "scheduleDigest": current_schedule["scheduleDigest"],
            "dispositionSnapshotDigest": snapshot["snapshotDigest"],
            "subjectTransactionId": candidate_for_output["transactionId"]
            if candidate_for_output
            else None,
            "ledgerOrdinal": candidate_for_output["ledgerOrdinal"]
            if candidate_for_output
            else None,
            "acceptedSubmissionInputDigest": candidate_for_output[
                "acceptedSubmissionInputDigest"
            ]
            if candidate_for_output
            else None,
            "judgmentId": candidate_for_output["judgmentId"]
            if candidate_for_output
            else None,
            "predecessorAccountingStateDigest": pipeline["accountingStateDigest"]
            if candidate_for_output
            else None,
            "predecessorKnowledgeStateDigest": predecessor_knowledge
            if candidate_for_output
            else None,
            "mode": mode_for_output,
            "semanticDispatchKey": semantic_for_output,
            "automaticAttemptNumber": attempt_for_output,
            "maximumSubjectsPerRun": config["hostedBatching"][  # type: ignore[index]
                "maximumSubjectsPerRun"
            ],
            "manualReview": False,
        }
    )


def _seal_check(value: Mapping[str, object]) -> dict[str, object]:
    core = _without(value, "checkDigest")
    return validate_work_accounting_prepublication_check(
        {**core, "checkDigest": _digest(core)}
    )


def validate_work_accounting_prepublication_check(
    value: object,
) -> dict[str, object]:
    if not isinstance(value, dict) or set(value) != CHECK_FIELDS:
        raise MathFlowError("work prepublication check has an invalid envelope")
    if value.get("schemaVersion") != 1 or not isinstance(
        value.get("publishable"), bool
    ):
        raise MathFlowError("work prepublication check has an invalid version")
    for field in ("reasonCode", "message"):
        if not isinstance(value.get(field), str) or not value[field]:
            raise MathFlowError("work prepublication check has invalid text")
    _require_transaction(value.get("subjectTransactionId"), "prepublication subject")
    _require_digest(value.get("originalDispatchDigest"), "original dispatch digest")
    current_key = value.get("currentSemanticDispatchKey")
    if current_key is not None:
        _require_digest(current_key, "current semantic dispatch key")
    if value.get("checkDigest") != _digest(_without(value, "checkDigest")):
        raise MathFlowError("work prepublication check digest mismatch")
    return value


def recheck_work_accounting_prepublication(
    root: Path,
    *,
    original_plan: object,
    config: Mapping[str, object],
    pipeline_state: object,
    schedule: object,
    disposition_snapshot: object,
    canonical_head: str,
    projection_head: str,
    projection_state_digest: str,
    as_of: int,
    target_subject_transaction_id: str | None = None,
) -> dict[str, object]:
    """Replan against current canonical/projection state before any publication."""

    original = validate_work_accounting_dispatch_plan(original_plan)
    if not original["eligible"]:
        raise MathFlowError("an ineligible dispatch cannot authorize publication")
    if target_subject_transaction_id is not None and (
        _require_transaction(target_subject_transaction_id, "prepublication subject")
        != original["subjectTransactionId"]
    ):
        raise MathFlowError("prepublication subject differs from the original dispatch")
    current = plan_work_accounting_dispatch(
        root,
        config=config,
        pipeline_state=pipeline_state,
        schedule=schedule,
        disposition_snapshot=disposition_snapshot,
        run_history=empty_work_dispatch_history(),
        canonical_head=canonical_head,
        projection_head=projection_head,
        projection_state_digest=projection_state_digest,
        as_of=as_of,
        target_subject_transaction_id=str(original["subjectTransactionId"]),
    )
    bindings = (
        "canonicalHead",
        "problemLedgerDigest",
        "projectionHead",
        "projectionStateDigest",
        "rootContractDigest",
        "pipelineStateDigest",
        "scheduleDigest",
        "dispositionSnapshotDigest",
        "subjectTransactionId",
        "acceptedSubmissionInputDigest",
        "judgmentId",
        "predecessorAccountingStateDigest",
        "predecessorKnowledgeStateDigest",
        "semanticDispatchKey",
    )
    publishable = bool(current["eligible"]) and all(
        current.get(field) == original.get(field) for field in bindings
    )
    reason = "publishable" if publishable else "dispatch-superseded"
    message = (
        "Canonical, projection, lane, subject, and predecessor bindings are unchanged."
        if publishable
        else "Discard the result because an exact dispatch binding changed."
    )
    return _seal_check(
        {
            "schemaVersion": 1,
            "publishable": publishable,
            "reasonCode": reason,
            "message": message,
            "subjectTransactionId": original["subjectTransactionId"],
            "originalDispatchDigest": original["dispatchDigest"],
            "currentSemanticDispatchKey": current.get("semanticDispatchKey"),
        }
    )
