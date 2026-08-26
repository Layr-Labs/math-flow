"""Secure hosted execution for the serial BSSC work-accounting lane.

The module is deliberately separate from the general CLI.  Planning and
prepublication checks are provider-free.  Only ``execute`` constructs the
governed work provider, and only ``publish`` receives a GitHub token.
"""

from __future__ import annotations

import argparse
import copy
import datetime as dt
import json
import os
import re
import subprocess
import zipfile
from collections.abc import Mapping, Sequence
from pathlib import Path
from .bssc_work_replay import _load_v5_chain, load_bssc_replay_source
from .bssc_zero_lane import load_bssc_zero_lane_accepted_submissions
from .errors import MathFlowError
from .governance import validate_projection_spec
from .governed_providers import OpenRouterWorkProjectionProvider
from .repository import canonical_json, ledger, sha256_json
from .research_topology import empty_research_program_state_v2
from .research_topology import validate_research_program_state_v2
from .work_accounting import make_zero_work_accounting_state, validate_root_contract
from .work_accounting_dispatch import (
    load_work_accounting_hosted_config,
    plan_work_accounting_dispatch,
    recheck_work_accounting_prepublication,
    validate_work_accounting_dispatch_plan,
    validate_work_accounting_prepublication_check,
    validate_work_dispatch_history,
)
from .work_accounting_pipeline import (
    AcceptedWorkSubmission,
    advance_work_accounting_pipeline,
    initialize_work_accounting_pipeline,
    read_work_accounting_pipeline_state,
)
from .work_accounting_projection_store import (
    ProjectionBranchWorkAccountingStore,
    ProjectionPublisher,
    publish_work_accounting_projection,
)
from .work_accounting_schedule import validate_work_accounting_schedule


PROBLEM = "bssc-sum-capacity"
PRODUCTION_CONFIG = Path("protocol/runtime/bssc-work-accounting-hosted-v1.json")
ADMITTED_PROJECTION_DIRECTORY = Path("protocol/projections")
DIGEST = re.compile(r"^sha256:[0-9a-f]{64}$")
GIT_SHA = re.compile(r"^[0-9a-f]{40}$")
FROZEN_PLAN_FIELDS = {
    "schemaVersion",
    "runId",
    "plannedAt",
    "plan",
    "frozenPlanDigest",
}
RECEIPT_FIELDS = {
    "schemaVersion",
    "subjectTransactionId",
    "dispatchDigest",
    "predecessorPipelineStateDigest",
    "resultPipelineStateDigest",
    "status",
    "completedTransitionCount",
    "receiptDigest",
}


def _digest(value: object) -> str:
    return f"sha256:{sha256_json(value)}"


def _seal(value: Mapping[str, object], field: str) -> dict[str, object]:
    core = {
        key: copy.deepcopy(item) for key, item in value.items() if key != field
    }
    return {**core, field: _digest(core)}


def _read_json(path: Path, label: str) -> dict[str, object]:
    if path.is_symlink() or not path.is_file():
        raise MathFlowError(f"{label} must be a regular file")
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise MathFlowError(f"could not read {label}: {exc}") from exc
    if not isinstance(value, dict):
        raise MathFlowError(f"{label} must be a JSON object")
    return value


def _git_head(root: Path) -> str:
    try:
        value = subprocess.run(
            ["git", "-C", str(root), "rev-parse", "HEAD"],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        ).stdout.strip()
    except subprocess.CalledProcessError as exc:
        raise MathFlowError("could not resolve the projection worktree head") from exc
    if not GIT_SHA.fullmatch(value):
        raise MathFlowError("projection worktree head is not exact")
    return value


def _require_admitted_copy(
    repository_root: Path,
    *,
    candidate_path: str,
    projection_id: str,
) -> None:
    candidate = repository_root / candidate_path
    admitted = repository_root / ADMITTED_PROJECTION_DIRECTORY / f"{projection_id}.json"
    if not admitted.is_file() or admitted.is_symlink():
        raise MathFlowError(
            f"active projection {projection_id!r} has not been admitted"
        )
    if candidate.read_bytes() != admitted.read_bytes():
        raise MathFlowError(
            f"admitted projection {projection_id!r} is not byte-identical to its governed candidate"
        )


def load_bssc_work_accounting_deployment(
    repository_root: Path,
    config_path: Path = PRODUCTION_CONFIG,
    *,
    require_admitted: bool = True,
) -> dict[str, object]:
    """Load and cross-bind every production BSSC identity."""

    root = repository_root.resolve()
    resolved_config = config_path if config_path.is_absolute() else root / config_path
    config = load_work_accounting_hosted_config(root, resolved_config)
    if (
        config.get("status") != "active"
        or config.get("problemId") != PROBLEM
        or config.get("hostedBatching", {}).get("maximumSubjectsPerRun") != 1
    ):
        raise MathFlowError("production BSSC hosted config is not a one-subject active lane")

    source_binding = config["validitySource"]
    contract_binding = config["rootContract"]
    knowledge_binding = config["knowledgeProjectionSpec"]
    assert isinstance(source_binding, dict)
    assert isinstance(contract_binding, dict)
    assert isinstance(knowledge_binding, dict)
    source = load_bssc_replay_source(root / str(source_binding["path"]))
    canonical = ledger(root, PROBLEM, str(source["mainCommit"]))
    if canonical["problemLedgerDigest"] != source["problemLedgerDigest"]:
        raise MathFlowError("production BSSC source pin does not match its canonical ledger")
    contract = validate_root_contract(
        _read_json(root / str(contract_binding["path"]), "BSSC root contract"),
        PROBLEM,
    )
    knowledge = validate_projection_spec(
        _read_json(
            root / str(knowledge_binding["path"]), "BSSC knowledge projection candidate"
        ),
        str(knowledge_binding["id"]),
        lambda relative: (root / relative).read_text(encoding="utf-8"),
    )
    if (
        knowledge["status"] != "active"
        or contract["knowledgeProjectionId"] != knowledge["id"]
        or contract["knowledgeProjectionSpecDigest"] != knowledge_binding["digest"]
    ):
        raise MathFlowError("BSSC root contract does not bind the active knowledge projection")
    if require_admitted:
        projection_binding = config["projectionSpec"]
        assert isinstance(projection_binding, dict)
        _require_admitted_copy(
            root,
            candidate_path=str(projection_binding["path"]),
            projection_id=str(projection_binding["id"]),
        )
        _require_admitted_copy(
            root,
            candidate_path=str(knowledge_binding["path"]),
            projection_id=str(knowledge_binding["id"]),
        )
    return {
        "config": config,
        "source": source,
        "contract": contract,
        "knowledgeProjection": knowledge,
    }


def build_bssc_work_disposition_snapshot(
    repository_root: Path,
    *,
    deployment: Mapping[str, object],
    canonical_head: str | None = None,
) -> dict[str, object]:
    """Normalize the pinned validity-v4 history into 25 terminal dispositions."""

    # Imported here so the hosted surface and its provider-free snapshot builder
    # use the pipeline's single public submission canonicalizer.
    from .work_accounting_pipeline import normalize_work_accounting_submission

    root = repository_root.resolve()
    config = deployment["config"]
    source = deployment["source"]
    assert isinstance(config, Mapping)
    assert isinstance(source, Mapping)
    head = canonical_head or _git_head(root)
    canonical = ledger(root, PROBLEM, head)
    if canonical["problemLedgerDigest"] != source["problemLedgerDigest"]:
        raise MathFlowError("current BSSC ledger differs from the production source pin")
    entries: dict[str, Mapping[str, object]] = {}
    for formation in _load_v5_chain(root, source):
        batch = formation.get("batch")
        if not isinstance(batch, Mapping) or not isinstance(batch.get("judgments"), list):
            raise MathFlowError("historical BSSC validity batch is invalid")
        for entry in batch["judgments"]:
            if not isinstance(entry, Mapping):
                raise MathFlowError("historical BSSC validity entry is invalid")
            transaction_id = str(entry.get("subjectTransactionId"))
            if transaction_id in entries:
                raise MathFlowError("historical BSSC validity repeats a subject")
            entries[transaction_id] = entry
    submissions = {
        item.transaction_id: item
        for item in load_bssc_zero_lane_accepted_submissions(root, source)
    }
    subjects: list[dict[str, object]] = []
    for transaction in canonical["transactions"]:
        transaction_id = str(transaction["transactionId"])
        entry = entries.get(transaction_id)
        if entry is None:
            raise MathFlowError("pinned BSSC validity history is incomplete")
        accepted_keys = entry.get("acceptedClaimKeys")
        excluded = entry.get("excludedAssessments")
        if not isinstance(accepted_keys, list) or not isinstance(excluded, list):
            raise MathFlowError("pinned BSSC validity disposition is invalid")
        normalized_digest: str | None = None
        if accepted_keys:
            if excluded or transaction_id not in submissions:
                raise MathFlowError("accepted BSSC disposition is internally inconsistent")
            normalized, _ = normalize_work_accounting_submission(
                submissions[transaction_id], PROBLEM
            )
            status = "accepted"
            normalized_digest = str(normalized["submissionInputDigest"])
        else:
            statuses = {
                item.get("status") for item in excluded if isinstance(item, Mapping)
            }
            if not excluded or statuses not in ({"invalid"}, {"indeterminate"}):
                raise MathFlowError("excluded BSSC validity disposition is ambiguous")
            status = "rejected" if statuses == {"invalid"} else "indeterminate"
        subjects.append(
            {
                "transactionId": transaction_id,
                "ledgerOrdinal": transaction["ordinal"],
                "status": status,
                "judgmentId": entry["judgmentId"],
                "acceptedSubmissionInputDigest": normalized_digest,
            }
        )
    core: dict[str, object] = {
        "schemaVersion": 1,
        "problemId": PROBLEM,
        "canonicalHead": head,
        "problemLedgerDigest": source["problemLedgerDigest"],
        "knowledgeProjectionId": config["knowledgeProjectionId"],
        "knowledgeBuilderSpecDigest": config["builderSpec"]["digest"],
        "subjects": subjects,
    }
    from .work_accounting_dispatch import validate_work_disposition_snapshot

    return validate_work_disposition_snapshot(
        {**core, "snapshotDigest": _digest(core)}, root, config=config
    )


def _epoch(value: object, label: str) -> int:
    if not isinstance(value, str) or not value:
        raise MathFlowError(f"{label} must be an ISO-8601 timestamp")
    try:
        parsed = dt.datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise MathFlowError(f"{label} must be an ISO-8601 timestamp") from exc
    if parsed.tzinfo is None:
        raise MathFlowError(f"{label} must include a timezone")
    timestamp = int(parsed.timestamp())
    if timestamp < 0:
        raise MathFlowError(f"{label} predates the Unix epoch")
    return timestamp


def validate_frozen_work_accounting_plan(value: object) -> dict[str, object]:
    if not isinstance(value, dict) or set(value) != FROZEN_PLAN_FIELDS:
        raise MathFlowError("frozen work-accounting plan has an invalid envelope")
    run_id = value.get("runId")
    planned_at = value.get("plannedAt")
    if (
        not isinstance(run_id, int)
        or isinstance(run_id, bool)
        or run_id < 1
        or not isinstance(planned_at, int)
        or isinstance(planned_at, bool)
        or planned_at < 0
    ):
        raise MathFlowError("frozen work-accounting plan has invalid run metadata")
    validate_work_accounting_dispatch_plan(value.get("plan"))
    if value.get("frozenPlanDigest") != _digest(
        {key: item for key, item in value.items() if key != "frozenPlanDigest"}
    ):
        raise MathFlowError("frozen work-accounting plan digest mismatch")
    return copy.deepcopy(value)


def freeze_work_accounting_plan(
    *, run_id: int, planned_at: int, plan: object
) -> dict[str, object]:
    validated = validate_work_accounting_dispatch_plan(plan)
    return validate_frozen_work_accounting_plan(
        _seal(
            {
                "schemaVersion": 1,
                "runId": run_id,
                "plannedAt": planned_at,
                "plan": validated,
            },
            "frozenPlanDigest",
        )
    )


def build_work_dispatch_history(
    raw_runs: object,
    frozen_plans: Mapping[int, object],
    *,
    config: Mapping[str, object],
    current_run_id: int | None = None,
) -> dict[str, object]:
    """Derive retry history only from GitHub runs with validated frozen plans."""

    if not isinstance(raw_runs, list):
        raise MathFlowError("hosted GitHub run history must be an array")
    validated_plans: dict[int, dict[str, object]] = {}
    for run_id, value in frozen_plans.items():
        if not isinstance(run_id, int) or isinstance(run_id, bool) or run_id < 1:
            raise MathFlowError("frozen plan map has an invalid run ID")
        frozen = validate_frozen_work_accounting_plan(value)
        if frozen["runId"] != run_id:
            raise MathFlowError("frozen plan map key differs from its run ID")
        validated_plans[run_id] = frozen
    normalized: list[dict[str, object]] = []
    observed: set[int] = set()
    for raw in raw_runs:
        if not isinstance(raw, dict):
            raise MathFlowError("hosted GitHub run record must be an object")
        run_id = raw.get("databaseId")
        if not isinstance(run_id, int) or isinstance(run_id, bool) or run_id < 1:
            raise MathFlowError("hosted GitHub run has an invalid database ID")
        if run_id in observed:
            raise MathFlowError("hosted GitHub run history repeats a database ID")
        observed.add(run_id)
        if run_id == current_run_id or run_id not in validated_plans:
            continue
        frozen = validated_plans[run_id]
        plan = frozen["plan"]
        assert isinstance(plan, dict)
        if (
            not plan["eligible"]
            or plan["configuration"]["configDigest"] != config["configDigest"]
            or plan["problemId"] != config["problemId"]
            or plan["projectionId"] != config["projectionId"]
        ):
            continue
        raw_status = raw.get("status")
        if raw_status == "completed":
            status = "completed"
            raw_conclusion = raw.get("conclusion")
            conclusion = (
                raw_conclusion
                if raw_conclusion in {"success", "cancelled", "timed_out"}
                else "failure"
            )
            completed_at = _epoch(raw.get("updatedAt"), "hosted run completion")
        elif raw_status in {"in_progress"}:
            status = "in_progress"
            conclusion = None
            completed_at = None
        elif raw_status in {"queued", "requested", "pending", "waiting"}:
            status = "queued"
            conclusion = None
            completed_at = None
        else:
            raise MathFlowError("hosted GitHub run status is unsupported")
        started_raw = raw.get("startedAt") or raw.get("createdAt")
        normalized.append(
            {
                "runId": run_id,
                "semanticDispatchKey": plan["semanticDispatchKey"],
                "subjectTransactionId": plan["subjectTransactionId"],
                "status": status,
                "conclusion": conclusion,
                "startedAt": _epoch(started_raw, "hosted run start"),
                "completedAt": completed_at,
            }
        )
    normalized.sort(key=lambda item: (int(item["startedAt"]), int(item["runId"])))
    core: dict[str, object] = {"schemaVersion": 1, "runs": normalized}
    return validate_work_dispatch_history(
        {**core, "historyDigest": _digest(core)}
    )


def validate_bssc_execution_receipt(value: object) -> dict[str, object]:
    if not isinstance(value, dict) or set(value) != RECEIPT_FIELDS:
        raise MathFlowError("BSSC work execution receipt has an invalid envelope")
    if value.get("schemaVersion") != 1 or value.get("status") not in {
        "completed",
        "retry-scheduled",
    }:
        raise MathFlowError("BSSC work execution receipt has an invalid status")
    if not isinstance(value.get("subjectTransactionId"), str) or not GIT_SHA.fullmatch(
        value["subjectTransactionId"]
    ):
        raise MathFlowError("BSSC work execution receipt has an invalid subject")
    for field in (
        "dispatchDigest",
        "predecessorPipelineStateDigest",
        "resultPipelineStateDigest",
    ):
        if not isinstance(value.get(field), str) or not DIGEST.fullmatch(value[field]):
            raise MathFlowError(f"BSSC work execution receipt {field} is invalid")
    count = value.get("completedTransitionCount")
    if not isinstance(count, int) or isinstance(count, bool) or count < 0:
        raise MathFlowError("BSSC work execution receipt count is invalid")
    if value.get("receiptDigest") != _digest(
        {key: item for key, item in value.items() if key != "receiptDigest"}
    ):
        raise MathFlowError("BSSC work execution receipt digest mismatch")
    return copy.deepcopy(value)


def _schedule(
    store: ProjectionBranchWorkAccountingStore,
    pipeline: Mapping[str, object],
) -> dict[str, object]:
    hexadecimal = str(pipeline["scheduleDigest"]).removeprefix("sha256:")
    stored = store.get(f"objects/schedules/{hexadecimal}.json")
    if stored is None:
        raise MathFlowError("BSSC accounting schedule object is missing")
    try:
        value = json.loads(stored.value)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise MathFlowError("BSSC accounting schedule object is invalid JSON") from exc
    return validate_work_accounting_schedule(value)


def _formed_knowledge_state(
    store: ProjectionBranchWorkAccountingStore,
    pipeline: Mapping[str, object],
) -> dict[str, object]:
    hexadecimal = str(pipeline["formedKnowledgeStateDigest"]).removeprefix("sha256:")
    stored = store.get(f"objects/knowledge-states/{hexadecimal}.json")
    if stored is None:
        raise MathFlowError("BSSC formed knowledge-state object is missing")
    try:
        value = json.loads(stored.value)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise MathFlowError("BSSC formed knowledge-state object is invalid JSON") from exc
    state = validate_research_program_state_v2(value, PROBLEM)
    if state["stateDigest"] != pipeline["formedKnowledgeStateDigest"]:
        raise MathFlowError("BSSC formed knowledge-state digest binding mismatch")
    return state


def discover_published_research_v6_transition_bundle(
    projection_root: Path,
    *,
    base_knowledge_state: Mapping[str, object],
    submission: AcceptedWorkSubmission,
    knowledge_projection_spec_digest: str,
    builder_spec_digest: str,
) -> Path:
    """Find the unique published v6 bundle for an exact base and submission."""

    from .work_accounting_pipeline import normalize_work_accounting_submission
    from .work_accounting_research_v6 import (
        PublishedResearchV6TransitionProvider,
        load_published_research_v6_transition,
    )

    normalized, _ = normalize_work_accounting_submission(submission, PROBLEM)
    object_root = projection_root / "objects" / "knowledge-build"
    if not object_root.is_dir() or object_root.is_symlink():
        raise MathFlowError("published research-v6 object root is missing")
    matches: list[Path] = []
    for prefix in sorted(object_root.iterdir(), key=lambda item: item.name):
        if prefix.is_symlink() or not prefix.is_dir() or not re.fullmatch(
            r"[0-9a-f]{2}", prefix.name
        ):
            continue
        for bundle_dir in sorted(prefix.iterdir(), key=lambda item: item.name):
            if bundle_dir.is_symlink() or not bundle_dir.is_dir() or not re.fullmatch(
                r"[0-9a-f]{64}", bundle_dir.name
            ):
                continue
            try:
                transition = load_published_research_v6_transition(
                    bundle_dir,
                    expected_bundle_digest=f"sha256:{bundle_dir.name}",
                    expected_problem=PROBLEM,
                    expected_projection_spec_digest=knowledge_projection_spec_digest,
                    expected_builder_spec_digest=builder_spec_digest,
                )
                provider = PublishedResearchV6TransitionProvider([transition])
                provider(
                    base_knowledge_state=base_knowledge_state,
                    submission=normalized,
                )
            except MathFlowError:
                continue
            matches.append(bundle_dir)
    if len(matches) != 1:
        raise MathFlowError(
            "expected exactly one published research-v6 transition for the frozen subject"
        )
    return matches[0]


def _open_lane(
    repository_root: Path,
    projection_root: Path,
    deployment: Mapping[str, object],
) -> tuple[
    ProjectionBranchWorkAccountingStore,
    dict[str, object],
    dict[str, object],
    list[AcceptedWorkSubmission],
]:
    config = deployment["config"]
    source = deployment["source"]
    contract = deployment["contract"]
    assert isinstance(config, Mapping)
    assert isinstance(source, Mapping)
    store = ProjectionBranchWorkAccountingStore(
        projection_root,
        problem=PROBLEM,
        projection_id=str(config["projectionId"]),
        projection_spec_digest=str(config["projectionSpec"]["digest"]),
    )
    submissions = load_bssc_zero_lane_accepted_submissions(repository_root, source)
    current = read_work_accounting_pipeline_state(
        store, projection_id=str(config["projectionId"]), problem=PROBLEM
    )
    if current is None:
        knowledge = empty_research_program_state_v2(PROBLEM)
        accounting = make_zero_work_accounting_state(
            root_contract=contract,
            knowledge_state=knowledge,
        )
        resolved = [
            str(item["transactionId"])
            for item in ledger(repository_root, PROBLEM, str(source["mainCommit"]))[
                "transactions"
            ]
        ]
        pipeline = initialize_work_accounting_pipeline(
            store,
            repository_root,
            problem=PROBLEM,
            projection_id=str(config["projectionId"]),
            projection_spec_digest=str(config["projectionSpec"]["digest"]),
            root_contract=contract,
            initial_knowledge_state=knowledge,
            initial_accounting_state=accounting,
            resolved_submission_ids=resolved,
            head=_git_head(repository_root),
            maximum_attempts=int(config["retryPolicy"]["maximumAttempts"]),
            base_retry_seconds=int(config["retryPolicy"]["baseRetrySeconds"]),
        )
    else:
        pipeline = current[0]
    return store, pipeline, _schedule(store, pipeline), submissions


def plan_bssc_work_accounting(
    repository_root: Path,
    projection_root: Path,
    *,
    deployment: Mapping[str, object],
    run_history: object,
    as_of: int,
    target_subject_transaction_id: str | None = None,
) -> dict[str, object]:
    store, pipeline, schedule, _ = _open_lane(
        repository_root, projection_root, deployment
    )
    del store
    config = deployment["config"]
    assert isinstance(config, Mapping)
    canonical_head = _git_head(repository_root)
    snapshot = build_bssc_work_disposition_snapshot(
        repository_root, deployment=deployment, canonical_head=canonical_head
    )
    return plan_work_accounting_dispatch(
        repository_root,
        config=config,
        pipeline_state=pipeline,
        schedule=schedule,
        disposition_snapshot=snapshot,
        run_history=run_history,
        canonical_head=canonical_head,
        projection_head=_git_head(projection_root),
        projection_state_digest=str(pipeline["formedKnowledgeStateDigest"]),
        as_of=as_of,
        target_subject_transaction_id=target_subject_transaction_id,
    )


def execute_bssc_work_accounting(
    repository_root: Path,
    projection_root: Path,
    *,
    deployment: Mapping[str, object],
    frozen_plan: object,
    research_bundle_dir: Path | None,
    scratch_root: Path,
    as_of: int,
    work_provider: object | None = None,
) -> dict[str, object]:
    """Execute exactly the frozen subject and persist only its local CAS result."""

    from .work_accounting_research_v6 import (
        PublishedResearchV6TransitionProvider,
        load_published_research_v6_transition,
    )

    frozen = validate_frozen_work_accounting_plan(frozen_plan)
    plan = frozen["plan"]
    assert isinstance(plan, dict)
    if not plan["eligible"]:
        raise MathFlowError("an ineligible frozen plan cannot execute providers")
    config = deployment["config"]
    assert isinstance(config, Mapping)
    if plan["configuration"]["configDigest"] != config["configDigest"]:
        raise MathFlowError("frozen plan does not bind the production config")
    store, before, schedule, submissions = _open_lane(
        repository_root, projection_root, deployment
    )
    canonical_head = _git_head(repository_root)
    snapshot = build_bssc_work_disposition_snapshot(
        repository_root, deployment=deployment, canonical_head=canonical_head
    )
    check = recheck_work_accounting_prepublication(
        repository_root,
        original_plan=plan,
        config=config,
        pipeline_state=before,
        schedule=schedule,
        disposition_snapshot=snapshot,
        canonical_head=canonical_head,
        projection_head=_git_head(projection_root),
        projection_state_digest=str(before["formedKnowledgeStateDigest"]),
        as_of=as_of,
        target_subject_transaction_id=str(plan["subjectTransactionId"]),
    )
    if not check["publishable"]:
        raise MathFlowError("frozen plan was superseded before provider execution")
    if research_bundle_dir is None:
        subject = next(
            (
                item
                for item in submissions
                if item.transaction_id == plan["subjectTransactionId"]
            ),
            None,
        )
        if subject is None:
            raise MathFlowError("frozen subject is absent from accepted BSSC inputs")
        research_bundle_dir = discover_published_research_v6_transition_bundle(
            projection_root,
            base_knowledge_state=_formed_knowledge_state(store, before),
            submission=subject,
            knowledge_projection_spec_digest=str(
                config["knowledgeProjectionSpec"]["digest"]
            ),
            builder_spec_digest=str(config["builderSpec"]["digest"]),
        )
    transition = load_published_research_v6_transition(
        research_bundle_dir,
        expected_problem=PROBLEM,
        expected_projection_spec_digest=str(
            config["knowledgeProjectionSpec"]["digest"]
        ),
        expected_builder_spec_digest=str(config["builderSpec"]["digest"]),
    )
    builder_provider = PublishedResearchV6TransitionProvider([transition])
    governed_work = work_provider or OpenRouterWorkProjectionProvider.load(
        repository_root / str(config["workProviderSpec"]["path"])
    )
    result = advance_work_accounting_pipeline(
        store,
        repository_root,
        projection_id=str(config["projectionId"]),
        problem=PROBLEM,
        builder_provider=builder_provider,
        work_provider=governed_work,  # type: ignore[arg-type]
        accepted_submissions=submissions,
        scratch_root=scratch_root,
        as_of=as_of,
        head=canonical_head,
        maximum_subjects=1,
    )
    completed_before = len(before["completedTransitions"])
    completed_after = len(result["completedTransitions"])
    if completed_after == completed_before + 1:
        latest = result["completedTransitions"][-1]
        if latest["subjectTransactionId"] != plan["subjectTransactionId"]:
            raise MathFlowError("provider execution advanced another subject")
        status = "completed"
    elif completed_after == completed_before:
        pending = result.get("pendingTransition")
        if (
            not isinstance(pending, Mapping)
            or pending.get("subjectTransactionId") != plan["subjectTransactionId"]
        ):
            raise MathFlowError("provider execution neither completed nor scheduled retry")
        status = "retry-scheduled"
    else:
        raise MathFlowError("one hosted execution advanced more than one subject")
    return validate_bssc_execution_receipt(
        _seal(
            {
                "schemaVersion": 1,
                "subjectTransactionId": plan["subjectTransactionId"],
                "dispatchDigest": plan["dispatchDigest"],
                "predecessorPipelineStateDigest": before["pipelineStateDigest"],
                "resultPipelineStateDigest": result["pipelineStateDigest"],
                "status": status,
                "completedTransitionCount": completed_after,
            },
            "receiptDigest",
        )
    )


def recheck_bssc_work_accounting_publication(
    repository_root: Path,
    fresh_projection_root: Path,
    *,
    deployment: Mapping[str, object],
    frozen_plan: object,
    as_of: int,
) -> dict[str, object]:
    frozen = validate_frozen_work_accounting_plan(frozen_plan)
    plan = frozen["plan"]
    assert isinstance(plan, dict)
    store, pipeline, schedule, _ = _open_lane(
        repository_root, fresh_projection_root, deployment
    )
    del store
    config = deployment["config"]
    assert isinstance(config, Mapping)
    canonical_head = _git_head(repository_root)
    return recheck_work_accounting_prepublication(
        repository_root,
        original_plan=plan,
        config=config,
        pipeline_state=pipeline,
        schedule=schedule,
        disposition_snapshot=build_bssc_work_disposition_snapshot(
            repository_root,
            deployment=deployment,
            canonical_head=canonical_head,
        ),
        canonical_head=canonical_head,
        projection_head=_git_head(fresh_projection_root),
        projection_state_digest=str(pipeline["formedKnowledgeStateDigest"]),
        as_of=as_of,
        target_subject_transaction_id=str(plan["subjectTransactionId"]),
    )


def publish_bssc_work_accounting(
    repository_root: Path,
    projection_root: Path,
    *,
    deployment: Mapping[str, object],
    frozen_plan: object,
    execution_receipt: object,
    prepublication_check: object,
    repository: str,
    branch: str,
    token: str,
    publisher: ProjectionPublisher | None = None,
) -> dict[str, object]:
    """Publish only a locally materialized result with a fresh successful check."""

    del repository_root
    frozen = validate_frozen_work_accounting_plan(frozen_plan)
    receipt = validate_bssc_execution_receipt(execution_receipt)
    check = validate_work_accounting_prepublication_check(prepublication_check)
    plan = frozen["plan"]
    assert isinstance(plan, dict)
    if (
        not check["publishable"]
        or check["originalDispatchDigest"] != plan["dispatchDigest"]
        or receipt["dispatchDigest"] != plan["dispatchDigest"]
        or receipt["subjectTransactionId"] != plan["subjectTransactionId"]
        or check["subjectTransactionId"] != plan["subjectTransactionId"]
    ):
        raise MathFlowError("publication artifacts do not authorize one exact result")
    config = deployment["config"]
    assert isinstance(config, Mapping)
    store = ProjectionBranchWorkAccountingStore(
        projection_root,
        problem=PROBLEM,
        projection_id=str(config["projectionId"]),
        projection_spec_digest=str(config["projectionSpec"]["digest"]),
    )
    current = read_work_accounting_pipeline_state(
        store, projection_id=str(config["projectionId"]), problem=PROBLEM
    )
    if current is None or current[0]["pipelineStateDigest"] != receipt[
        "resultPipelineStateDigest"
    ]:
        raise MathFlowError("local publication lane differs from the execution receipt")
    if not token:
        raise MathFlowError("signed projection publication requires a token")
    kwargs: dict[str, object] = {}
    if publisher is not None:
        kwargs["publisher"] = publisher
    return publish_work_accounting_projection(
        store,
        repository=repository,
        branch=branch,
        message=(
            "Publish BSSC work accounting for "
            f"{str(plan['subjectTransactionId'])[:12]}"
        ),
        token=token,
        **kwargs,  # type: ignore[arg-type]
    )


def _write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(canonical_json(value) + "\n", encoding="utf-8")


def _load_plan_directory(path: Path) -> dict[int, dict[str, object]]:
    if not path.is_dir() or path.is_symlink():
        raise MathFlowError("frozen plan directory must be a regular directory")
    result: dict[int, dict[str, object]] = {}
    for candidate in sorted(path.iterdir(), key=lambda item: item.name):
        if candidate.is_symlink() or not candidate.is_file():
            raise MathFlowError("frozen plan directory contains a non-regular entry")
        match = re.fullmatch(r"([1-9][0-9]*)\.json", candidate.name)
        if match is None:
            raise MathFlowError("frozen plan filename must be <run-id>.json")
        run_id = int(match.group(1))
        if run_id in result:
            raise MathFlowError("frozen plan directory repeats a run ID")
        result[run_id] = validate_frozen_work_accounting_plan(
            _read_json(candidate, "frozen work-accounting plan")
        )
    return result


def _load_plan_archives(path: Path) -> dict[int, dict[str, object]]:
    """Load prior plan artifacts without trusting archive paths or metadata."""

    if not path.is_dir() or path.is_symlink():
        raise MathFlowError("frozen plan archive directory must be a regular directory")
    result: dict[int, dict[str, object]] = {}
    for candidate in sorted(path.iterdir(), key=lambda item: item.name):
        if candidate.is_symlink() or not candidate.is_file():
            raise MathFlowError("frozen plan archive directory contains a non-file")
        match = re.fullmatch(r"([1-9][0-9]*)\.zip", candidate.name)
        if match is None:
            raise MathFlowError("frozen plan archive filename must be <run-id>.zip")
        run_id = int(match.group(1))
        try:
            with zipfile.ZipFile(candidate) as archive:
                members = archive.infolist()
                if (
                    len(members) != 1
                    or members[0].filename != "frozen-plan.json"
                    or members[0].is_dir()
                    or members[0].file_size > 1_000_000
                    or members[0].flag_bits & 0x1
                ):
                    raise MathFlowError("frozen plan artifact has an unsafe envelope")
                raw = archive.read(members[0])
        except (OSError, zipfile.BadZipFile) as exc:
            raise MathFlowError("frozen plan artifact is not a valid zip") from exc
        try:
            value = json.loads(raw)
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise MathFlowError("frozen plan artifact is not valid JSON") from exc
        frozen = validate_frozen_work_accounting_plan(value)
        if frozen["runId"] != run_id:
            raise MathFlowError("frozen plan artifact filename binds another run")
        result[run_id] = frozen
    return result


def _append_github_output(path: Path, **values: object) -> None:
    if path.exists() and (path.is_symlink() or not path.is_file()):
        raise MathFlowError("GitHub output path must be a regular file")
    rendered: list[str] = []
    for key, value in values.items():
        if not re.fullmatch(r"[a-z][a-z0-9_]*", key):
            raise MathFlowError("GitHub output key is invalid")
        text = str(value).lower() if isinstance(value, bool) else str(value)
        if "\n" in text or "\r" in text:
            raise MathFlowError("GitHub output value may not contain a newline")
        rendered.append(f"{key}={text}\n")
    with path.open("a", encoding="utf-8") as output:
        output.writelines(rendered)


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="python -m math_flow.bssc_work_accounting_hosted")
    parser.add_argument("--root", type=Path, default=Path("."))
    parser.add_argument("--config", type=Path, default=PRODUCTION_CONFIG)
    subparsers = parser.add_subparsers(dest="command", required=True)

    plan = subparsers.add_parser("plan")
    plan.add_argument("--projection-dir", type=Path, required=True)
    plan.add_argument("--github-runs", type=Path, required=True)
    plan.add_argument("--frozen-plan-dir", type=Path, required=True)
    plan.add_argument("--frozen-plan-zip-dir", type=Path)
    plan.add_argument("--run-id", type=int, required=True)
    plan.add_argument("--as-of", type=int, required=True)
    plan.add_argument("--subject")
    plan.add_argument("--output", type=Path, required=True)
    plan.add_argument("--github-output", type=Path)

    execute = subparsers.add_parser("execute")
    execute.add_argument("--projection-dir", type=Path, required=True)
    execute.add_argument("--frozen-plan", type=Path, required=True)
    execute.add_argument("--research-bundle-dir", type=Path)
    execute.add_argument("--scratch-root", type=Path, required=True)
    execute.add_argument("--as-of", type=int, required=True)
    execute.add_argument("--output", type=Path, required=True)

    prepublish = subparsers.add_parser("prepublish")
    prepublish.add_argument("--projection-dir", type=Path, required=True)
    prepublish.add_argument("--frozen-plan", type=Path, required=True)
    prepublish.add_argument("--as-of", type=int, required=True)
    prepublish.add_argument("--output", type=Path, required=True)
    prepublish.add_argument("--github-output", type=Path)

    publish = subparsers.add_parser("publish")
    publish.add_argument("--projection-dir", type=Path, required=True)
    publish.add_argument("--frozen-plan", type=Path, required=True)
    publish.add_argument("--execution-receipt", type=Path, required=True)
    publish.add_argument("--prepublication-check", type=Path, required=True)
    publish.add_argument("--repository", required=True)
    publish.add_argument("--branch", default="projections")
    publish.add_argument("--output", type=Path, required=True)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    arguments = _parser().parse_args(argv)
    root = arguments.root.resolve()
    deployment = load_bssc_work_accounting_deployment(root, arguments.config)
    if arguments.command == "plan":
        runs = json.loads(arguments.github_runs.read_text(encoding="utf-8"))
        frozen_plans = _load_plan_directory(arguments.frozen_plan_dir)
        if arguments.frozen_plan_zip_dir is not None:
            archived = _load_plan_archives(arguments.frozen_plan_zip_dir)
            overlap = set(frozen_plans) & set(archived)
            if overlap:
                raise MathFlowError("frozen plan inputs repeat a run ID")
            frozen_plans.update(archived)
        history = build_work_dispatch_history(
            runs,
            frozen_plans,
            config=deployment["config"],  # type: ignore[arg-type]
            current_run_id=arguments.run_id,
        )
        planned = plan_bssc_work_accounting(
            root,
            arguments.projection_dir,
            deployment=deployment,
            run_history=history,
            as_of=arguments.as_of,
            target_subject_transaction_id=arguments.subject,
        )
        result = freeze_work_accounting_plan(
            run_id=arguments.run_id, planned_at=arguments.as_of, plan=planned
        )
        if arguments.github_output is not None:
            _append_github_output(
                arguments.github_output,
                eligible=planned["eligible"],
                reason_code=planned["reasonCode"],
            )
    elif arguments.command == "execute":
        result = execute_bssc_work_accounting(
            root,
            arguments.projection_dir,
            deployment=deployment,
            frozen_plan=_read_json(arguments.frozen_plan, "frozen plan"),
            research_bundle_dir=arguments.research_bundle_dir,
            scratch_root=arguments.scratch_root,
            as_of=arguments.as_of,
        )
    elif arguments.command == "prepublish":
        result = recheck_bssc_work_accounting_publication(
            root,
            arguments.projection_dir,
            deployment=deployment,
            frozen_plan=_read_json(arguments.frozen_plan, "frozen plan"),
            as_of=arguments.as_of,
        )
        if arguments.github_output is not None:
            _append_github_output(
                arguments.github_output,
                publishable=result["publishable"],
                reason_code=result["reasonCode"],
            )
    else:
        token = os.environ.get("GITHUB_TOKEN", "")
        result = publish_bssc_work_accounting(
            root,
            arguments.projection_dir,
            deployment=deployment,
            frozen_plan=_read_json(arguments.frozen_plan, "frozen plan"),
            execution_receipt=_read_json(
                arguments.execution_receipt, "BSSC execution receipt"
            ),
            prepublication_check=_read_json(
                arguments.prepublication_check, "BSSC prepublication check"
            ),
            repository=arguments.repository,
            branch=arguments.branch,
            token=token,
        )
    _write_json(arguments.output, result)
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
