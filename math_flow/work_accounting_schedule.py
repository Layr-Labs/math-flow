"""Pure canonical scheduling and publication reducers for work accounting V1."""

from __future__ import annotations

import copy
import re
from fractions import Fraction
from pathlib import Path
from typing import Iterable, Mapping

from .errors import MathFlowError
from .repository import ledger, sha256_json
from .research_topology import validate_research_program_state_versioned
from .work_accounting import (
    materialize_submission_work_value,
    validate_root_contract,
    validate_submission_work_value,
    validate_work_accounting_state,
)


DIGEST = re.compile(r"^sha256:[0-9a-f]{64}$")
GIT_SHA = re.compile(r"^[0-9a-f]{40}$")
IDENTIFIER = re.compile(r"^[a-z0-9][a-z0-9/_-]*$")
CANONICAL_DECIMAL = re.compile(r"^(?:0|[1-9][0-9]*)(?:\.[0-9]*[1-9])?$")

SUBJECT_STATUSES = {"pending", "blocked", "failed", "processed"}
BLOCK_REASONS = {
    "earlier-canonical-submission-unresolved",
    "predecessor-submission-unprocessed",
}
FAILURE_KINDS = {
    "provider-invalid",
    "nonpositive-work-value",
    "counterfactual-invalid",
    "publication-invalid",
}
REPAIR_REASONS = {
    "validity-reversal",
    "evidence-defect",
    "implementation-defect",
    "topology-lineage-defect",
}

SCHEDULE_FIELDS = {
    "schemaVersion",
    "problemId",
    "projectionId",
    "projectionSpecDigest",
    "rootContractDigest",
    "problemLedgerDigest",
    "canonicalTransactionIds",
    "resolvedSubmissionIds",
    "retryPolicy",
    "observedKnowledgeStateDigest",
    "observedKnowledgeLedgerHead",
    "initialAccountingStateDigest",
    "terminalAccountingStateDigest",
    "terminalKnowledgeStateDigest",
    "subjects",
    "repairEventDigests",
    "scheduleDigest",
}
RETRY_POLICY_FIELDS = {"maximumAttempts", "baseRetrySeconds"}
SUBJECT_FIELDS = {
    "transactionId",
    "ledgerOrdinal",
    "postKnowledgeStateDigest",
    "postKnowledgeLedgerHead",
    "status",
    "blockReason",
    "blockedByTransactionId",
    "attemptCount",
    "failureHistory",
    "completion",
    "affectedByRepairDigests",
    "recordDigest",
}
FAILURE_FIELDS = {
    "failureKind",
    "claimDigest",
    "attemptNumber",
    "evidenceDigest",
    "failedAt",
    "retryNotBefore",
    "exhausted",
    "failureDigest",
}
COMPLETION_FIELDS = {
    "kind",
    "attemptNumber",
    "evaluationDigest",
    "committedAccountingStateDigest",
    "publicationManifestDigest",
}
CLAIM_FIELDS = {
    "schemaVersion",
    "problemId",
    "projectionId",
    "projectionSpecDigest",
    "rootContractDigest",
    "subjectTransactionId",
    "ledgerOrdinal",
    "attemptNumber",
    "subjectRecordDigest",
    "predecessorAccountingStateDigest",
    "predecessorKnowledgeStateDigest",
    "postKnowledgeStateDigest",
    "postKnowledgeLedgerHead",
    "previousAttemptClaimDigest",
    "automaticRetryKey",
    "claimDigest",
}
PUBLICATION_FIELDS = {
    "schemaVersion",
    "problemId",
    "projectionId",
    "projectionSpecDigest",
    "rootContractDigest",
    "subjectTransactionId",
    "ledgerOrdinal",
    "attemptNumber",
    "claimDigest",
    "automaticRetryKey",
    "predecessorAccountingStateDigest",
    "predecessorKnowledgeStateDigest",
    "postKnowledgeStateDigest",
    "evaluationDigest",
    "noAccessPatchDigest",
    "withAccessPatchDigest",
    "noAccessStateDigest",
    "committedAccountingStateDigest",
    "workValueHours",
    "publicationManifestDigest",
}
REPAIR_FIELDS = {
    "schemaVersion",
    "problemId",
    "projectionId",
    "projectionSpecDigest",
    "rootContractDigest",
    "reasonKind",
    "baseAccountingStateDigest",
    "repairedAccountingStateDigest",
    "knowledgeStateDigest",
    "affectedHistory",
    "evidenceRefs",
    "suffixReplay",
    "repairEventDigest",
}
HISTORY_FLAG_FIELDS = {"subjectTransactionId", "evaluationDigest"}


def _content_digest(value: Mapping[str, object], digest_field: str) -> str:
    content = {
        key: copy.deepcopy(item)
        for key, item in value.items()
        if key != digest_field
    }
    return f"sha256:{sha256_json(content)}"


def _require_digest(
    value: object, label: str, *, nullable: bool = False
) -> str | None:
    if value is None and nullable:
        return None
    if not isinstance(value, str) or not DIGEST.fullmatch(value):
        raise MathFlowError(f"{label} must be a sha256 digest")
    return value


def _require_transaction(
    value: object, label: str, *, nullable: bool = False
) -> str | None:
    if value is None and nullable:
        return None
    if not isinstance(value, str) or not GIT_SHA.fullmatch(value):
        raise MathFlowError(f"{label} must be a canonical transaction ID")
    return value


def _require_identifier(value: object, label: str) -> str:
    if not isinstance(value, str) or not IDENTIFIER.fullmatch(value):
        raise MathFlowError(f"{label} must be a stable lowercase identifier")
    return value


def _require_nonnegative_integer(value: object, label: str) -> int:
    if not isinstance(value, int) or isinstance(value, bool) or value < 0:
        raise MathFlowError(f"{label} must be a non-negative integer")
    return value


def _require_sorted_unique_strings(value: object, label: str) -> list[str]:
    if (
        not isinstance(value, list)
        or any(not isinstance(item, str) or not item for item in value)
        or value != sorted(set(value))
    ):
        raise MathFlowError(f"{label} must contain sorted unique non-empty strings")
    return list(value)


def _require_digest_list(value: object, label: str) -> list[str]:
    result = _require_sorted_unique_strings(value, label)
    for index, item in enumerate(result):
        _require_digest(item, f"{label} item {index + 1}")
    return result


def _require_positive_decimal(value: object, label: str) -> str:
    if (
        not isinstance(value, str)
        or len(value) > 128
        or not CANONICAL_DECIMAL.fullmatch(value)
        or Fraction(value) <= 0
    ):
        raise MathFlowError(f"{label} must be a strictly positive canonical decimal")
    return value


def _canonical_transactions(
    root: Path, problem: str, head: str
) -> tuple[dict[str, object], list[str], dict[str, int]]:
    canonical = ledger(root, problem, head)
    transactions = canonical.get("transactions")
    if not isinstance(transactions, list):  # pragma: no cover - ledger guarantees this
        raise AssertionError("canonical ledger has no transactions")
    ids = [str(item["transactionId"]) for item in transactions]
    ordinals = {str(item["transactionId"]): int(item["ordinal"]) for item in transactions}
    if len(ids) != len(set(ids)):
        raise MathFlowError("canonical problem ledger repeats a submission transaction")
    return canonical, ids, ordinals


def _accepted_ids(
    knowledge_state: Mapping[str, object],
    canonical_ids: list[str],
) -> list[str]:
    contributions = knowledge_state.get("contributions")
    if not isinstance(contributions, dict):
        raise MathFlowError("knowledge state has no accepted contribution collection")
    unknown = set(contributions) - set(canonical_ids)
    if unknown:
        raise MathFlowError("knowledge state accepts a submission outside canonical ledger")
    return [transaction_id for transaction_id in canonical_ids if transaction_id in contributions]


def _normalized_resolved_ids(
    value: Iterable[str], canonical_ids: list[str], accepted_ids: list[str]
) -> list[str]:
    supplied = list(value)
    if len(supplied) != len(set(supplied)) or any(
        not isinstance(item, str) or not GIT_SHA.fullmatch(item) for item in supplied
    ):
        raise MathFlowError("resolved submission IDs must be unique canonical transactions")
    supplied_set = set(supplied)
    if not supplied_set <= set(canonical_ids):
        raise MathFlowError(
            "resolved submission IDs contain a transaction outside canonical ledger"
        )
    if not set(accepted_ids) <= supplied_set:
        raise MathFlowError("every accepted submission must have a terminal disposition")
    return [transaction_id for transaction_id in canonical_ids if transaction_id in supplied_set]


def _subject_digest(record: Mapping[str, object]) -> str:
    return _content_digest(record, "recordDigest")


def _with_subject_digest(record: Mapping[str, object]) -> dict[str, object]:
    result = {
        key: copy.deepcopy(item) for key, item in record.items() if key != "recordDigest"
    }
    result["recordDigest"] = _subject_digest(result)
    return result


def _failure_digest(failure: Mapping[str, object]) -> str:
    return _content_digest(failure, "failureDigest")


def _processed_ids(schedule: Mapping[str, object]) -> list[str]:
    subjects = schedule.get("subjects")
    assert isinstance(subjects, list)
    return [
        str(record["transactionId"])
        for record in subjects
        if isinstance(record, dict) and record.get("status") == "processed"
    ]


def _first_unresolved_before(
    canonical_ids: list[str], resolved_ids: set[str], transaction_id: str
) -> str | None:
    for candidate in canonical_ids:
        if candidate == transaction_id:
            return None
        if candidate not in resolved_ids:
            return candidate
    raise MathFlowError("accounting subject is outside the canonical ledger")


def _restated_subjects(
    records: list[dict[str, object]],
    *,
    canonical_ids: list[str],
    resolved_ids: list[str],
) -> list[dict[str, object]]:
    result = [copy.deepcopy(record) for record in records]
    frontier_index = next(
        (index for index, record in enumerate(result) if record.get("completion") is None),
        None,
    )
    resolved = set(resolved_ids)
    frontier_id = (
        str(result[frontier_index]["transactionId"])
        if frontier_index is not None
        else None
    )
    external_blocker = (
        _first_unresolved_before(canonical_ids, resolved, frontier_id)
        if frontier_id is not None
        else None
    )
    for index, record in enumerate(result):
        completion = record.get("completion")
        if completion is not None:
            if frontier_index is not None and index > frontier_index:
                raise MathFlowError(
                    "work-accounting processed subjects must form a canonical prefix"
                )
            record["status"] = "processed"
            record["blockReason"] = None
            record["blockedByTransactionId"] = None
        elif index == frontier_index:
            if external_blocker is not None:
                record["status"] = "blocked"
                record["blockReason"] = "earlier-canonical-submission-unresolved"
                record["blockedByTransactionId"] = external_blocker
            elif record.get("failureHistory"):
                record["status"] = "failed"
                record["blockReason"] = None
                record["blockedByTransactionId"] = None
            else:
                record["status"] = "pending"
                record["blockReason"] = None
                record["blockedByTransactionId"] = None
        else:
            record["status"] = "blocked"
            record["blockReason"] = "predecessor-submission-unprocessed"
            record["blockedByTransactionId"] = frontier_id
        record = _with_subject_digest(record)
        result[index] = record
    return result


def _seal_schedule(value: Mapping[str, object]) -> dict[str, object]:
    result = {
        key: copy.deepcopy(item) for key, item in value.items() if key != "scheduleDigest"
    }
    result["scheduleDigest"] = _content_digest(result, "scheduleDigest")
    return result


def _bootstrap_completion() -> dict[str, object]:
    return {
        "kind": "bootstrap",
        "attemptNumber": 0,
        "evaluationDigest": None,
        "committedAccountingStateDigest": None,
        "publicationManifestDigest": None,
    }


def initialize_work_accounting_schedule(
    root: Path,
    *,
    problem: str,
    projection_id: str,
    projection_spec_digest: str,
    root_contract: object,
    accounting_state: object,
    knowledge_state: object,
    resolved_submission_ids: Iterable[str],
    head: str = "HEAD",
    maximum_attempts: int = 3,
    base_retry_seconds: int = 60,
) -> dict[str, object]:
    contract = validate_root_contract(root_contract, problem)
    knowledge = validate_research_program_state_versioned(knowledge_state, problem)
    accounting = validate_work_accounting_state(accounting_state, knowledge, contract)
    if accounting.get("evaluationMode") == "no-access":
        raise MathFlowError("an ephemeral no-access state cannot initialize scheduling")
    _require_identifier(projection_id, "work-accounting projection ID")
    _require_digest(projection_spec_digest, "work-accounting projection spec digest")
    maximum = _require_nonnegative_integer(
        maximum_attempts, "work-accounting maximum attempts"
    )
    retry_base = _require_nonnegative_integer(
        base_retry_seconds, "work-accounting retry base"
    )
    if maximum < 1 or retry_base < 1:
        raise MathFlowError("work-accounting retry policy values must be positive")
    canonical, canonical_ids, ordinals = _canonical_transactions(root, problem, head)
    accepted = _accepted_ids(knowledge, canonical_ids)
    resolved = _normalized_resolved_ids(resolved_submission_ids, canonical_ids, accepted)
    processed = list(accounting["processedSubmissionIds"])
    if processed != accepted[: len(processed)]:
        raise MathFlowError(
            "initial accounting processed submissions must be a canonical accepted prefix"
        )
    records: list[dict[str, object]] = []
    for transaction_id in accepted:
        records.append(
            {
                "transactionId": transaction_id,
                "ledgerOrdinal": ordinals[transaction_id],
                "postKnowledgeStateDigest": knowledge["stateDigest"],
                "postKnowledgeLedgerHead": knowledge["ledgerHead"],
                "status": "pending",
                "blockReason": None,
                "blockedByTransactionId": None,
                "attemptCount": 0,
                "failureHistory": [],
                "completion": _bootstrap_completion()
                if transaction_id in processed
                else None,
                "affectedByRepairDigests": [],
            }
        )
    records = _restated_subjects(
        records, canonical_ids=canonical_ids, resolved_ids=resolved
    )
    schedule = _seal_schedule(
        {
            "schemaVersion": 1,
            "problemId": problem,
            "projectionId": projection_id,
            "projectionSpecDigest": projection_spec_digest,
            "rootContractDigest": contract["rootContractDigest"],
            "problemLedgerDigest": canonical["problemLedgerDigest"],
            "canonicalTransactionIds": canonical_ids,
            "resolvedSubmissionIds": resolved,
            "retryPolicy": {
                "maximumAttempts": maximum,
                "baseRetrySeconds": retry_base,
            },
            "observedKnowledgeStateDigest": knowledge["stateDigest"],
            "observedKnowledgeLedgerHead": knowledge["ledgerHead"],
            "initialAccountingStateDigest": accounting["stateDigest"],
            "terminalAccountingStateDigest": accounting["stateDigest"],
            "terminalKnowledgeStateDigest": accounting["knowledgeStateDigest"],
            "subjects": records,
            "repairEventDigests": [],
        }
    )
    return validate_work_accounting_schedule(schedule)


def discover_work_accounting_subjects(
    schedule: object,
    root: Path,
    *,
    knowledge_state: object,
    resolved_submission_ids: Iterable[str],
    head: str = "HEAD",
) -> dict[str, object]:
    current = validate_work_accounting_schedule(schedule)
    problem = str(current["problemId"])
    knowledge = validate_research_program_state_versioned(knowledge_state, problem)
    canonical, canonical_ids, ordinals = _canonical_transactions(root, problem, head)
    old_canonical = list(current["canonicalTransactionIds"])
    if canonical_ids[: len(old_canonical)] != old_canonical:
        raise MathFlowError("canonical problem ledger is not an append-only extension")
    accepted = _accepted_ids(knowledge, canonical_ids)
    resolved = _normalized_resolved_ids(resolved_submission_ids, canonical_ids, accepted)
    if not set(current["resolvedSubmissionIds"]) <= set(resolved):
        raise MathFlowError("terminal submission dispositions cannot disappear")
    existing_records = {
        str(record["transactionId"]): copy.deepcopy(record)
        for record in current["subjects"]
    }
    if not set(existing_records) <= set(accepted):
        raise MathFlowError(
            "accepted work-accounting subjects cannot disappear through ordinary discovery"
        )
    processed = [
        str(record["transactionId"])
        for record in current["subjects"]
        if record["completion"] is not None
    ]
    if processed != accepted[: len(processed)]:
        raise MathFlowError(
            "newly accepted history would insert behind a processed accounting subject"
        )
    records: list[dict[str, object]] = []
    for transaction_id in accepted:
        existing = existing_records.get(transaction_id)
        if existing is not None:
            records.append(existing)
            continue
        records.append(
            {
                "transactionId": transaction_id,
                "ledgerOrdinal": ordinals[transaction_id],
                "postKnowledgeStateDigest": knowledge["stateDigest"],
                "postKnowledgeLedgerHead": knowledge["ledgerHead"],
                "status": "pending",
                "blockReason": None,
                "blockedByTransactionId": None,
                "attemptCount": 0,
                "failureHistory": [],
                "completion": None,
                "affectedByRepairDigests": [],
            }
        )
    records = _restated_subjects(
        records, canonical_ids=canonical_ids, resolved_ids=resolved
    )
    result = _seal_schedule(
        {
            **{
                key: copy.deepcopy(value)
                for key, value in current.items()
                if key not in {"scheduleDigest", "subjects"}
            },
            "problemLedgerDigest": canonical["problemLedgerDigest"],
            "canonicalTransactionIds": canonical_ids,
            "resolvedSubmissionIds": resolved,
            "observedKnowledgeStateDigest": knowledge["stateDigest"],
            "observedKnowledgeLedgerHead": knowledge["ledgerHead"],
            "subjects": records,
        }
    )
    return validate_work_accounting_schedule(result)


def _validate_completion(value: object, label: str) -> dict[str, object] | None:
    if value is None:
        return None
    if not isinstance(value, dict) or set(value) != COMPLETION_FIELDS:
        raise MathFlowError(f"{label} has invalid fields")
    kind = value.get("kind")
    attempt = _require_nonnegative_integer(value.get("attemptNumber"), f"{label} attempt")
    if kind == "bootstrap":
        if attempt != 0 or any(
            value.get(field) is not None
            for field in (
                "evaluationDigest",
                "committedAccountingStateDigest",
                "publicationManifestDigest",
            )
        ):
            raise MathFlowError(f"{label} bootstrap completion is invalid")
    elif kind == "evaluated":
        if attempt < 1:
            raise MathFlowError(f"{label} evaluated completion has no attempt")
        for field in (
            "evaluationDigest",
            "committedAccountingStateDigest",
            "publicationManifestDigest",
        ):
            _require_digest(value.get(field), f"{label} {field}")
    else:
        raise MathFlowError(f"{label} has an invalid kind")
    return value


def _validate_failure(value: object, label: str) -> dict[str, object]:
    if not isinstance(value, dict) or set(value) != FAILURE_FIELDS:
        raise MathFlowError(f"{label} has invalid fields")
    if value.get("failureKind") not in FAILURE_KINDS:
        raise MathFlowError(f"{label} has an invalid kind")
    _require_digest(value.get("claimDigest"), f"{label} claim digest")
    _require_digest(value.get("evidenceDigest"), f"{label} evidence digest")
    attempt = _require_nonnegative_integer(value.get("attemptNumber"), f"{label} attempt")
    if attempt < 1:
        raise MathFlowError(f"{label} attempt must be positive")
    _require_nonnegative_integer(value.get("failedAt"), f"{label} failedAt")
    retry = value.get("retryNotBefore")
    if retry is not None:
        _require_nonnegative_integer(retry, f"{label} retryNotBefore")
    if not isinstance(value.get("exhausted"), bool):
        raise MathFlowError(f"{label} exhausted must be boolean")
    if value.get("exhausted") != (retry is None):
        raise MathFlowError(f"{label} retry and exhaustion disagree")
    if value.get("failureDigest") != _failure_digest(value):
        raise MathFlowError(f"{label} digest mismatch")
    return value


def validate_work_accounting_schedule(value: object) -> dict[str, object]:
    if not isinstance(value, dict) or set(value) != SCHEDULE_FIELDS:
        raise MathFlowError("work-accounting schedule has an invalid envelope")
    if value.get("schemaVersion") != 1:
        raise MathFlowError("work-accounting schedule has an unsupported version")
    _require_identifier(value.get("problemId"), "schedule problem ID")
    _require_identifier(value.get("projectionId"), "schedule projection ID")
    for field in (
        "projectionSpecDigest",
        "rootContractDigest",
        "problemLedgerDigest",
        "observedKnowledgeStateDigest",
        "initialAccountingStateDigest",
        "terminalAccountingStateDigest",
        "terminalKnowledgeStateDigest",
    ):
        _require_digest(value.get(field), f"schedule {field}")
    _require_transaction(
        value.get("observedKnowledgeLedgerHead"),
        "schedule observed knowledge ledger head",
        nullable=True,
    )
    canonical_ids = value.get("canonicalTransactionIds")
    if not isinstance(canonical_ids, list) or any(
        not isinstance(item, str) or not GIT_SHA.fullmatch(item) for item in canonical_ids
    ) or len(canonical_ids) != len(set(canonical_ids)):
        raise MathFlowError("schedule canonical transactions are invalid")
    resolved_ids = value.get("resolvedSubmissionIds")
    if not isinstance(resolved_ids, list) or any(
        not isinstance(item, str) or not GIT_SHA.fullmatch(item) for item in resolved_ids
    ) or resolved_ids != [item for item in canonical_ids if item in set(resolved_ids)]:
        raise MathFlowError("schedule resolved submissions are not canonically ordered")
    retry_policy = value.get("retryPolicy")
    if not isinstance(retry_policy, dict) or set(retry_policy) != RETRY_POLICY_FIELDS:
        raise MathFlowError("schedule retry policy has invalid fields")
    maximum_attempts = _require_nonnegative_integer(
        retry_policy.get("maximumAttempts"), "schedule maximum attempts"
    )
    base_retry_seconds = _require_nonnegative_integer(
        retry_policy.get("baseRetrySeconds"), "schedule retry base"
    )
    if maximum_attempts < 1 or base_retry_seconds < 1:
        raise MathFlowError("schedule retry policy values must be positive")
    subjects = value.get("subjects")
    if not isinstance(subjects, list):
        raise MathFlowError("schedule subjects must be an array")
    subject_ids: list[str] = []
    ordinals: list[int] = []
    for index, record in enumerate(subjects):
        label = f"schedule subject {index + 1}"
        if not isinstance(record, dict) or set(record) != SUBJECT_FIELDS:
            raise MathFlowError(f"{label} has invalid fields")
        transaction_id = _require_transaction(record.get("transactionId"), f"{label} transaction")
        assert isinstance(transaction_id, str)
        subject_ids.append(transaction_id)
        ordinal = _require_nonnegative_integer(record.get("ledgerOrdinal"), f"{label} ordinal")
        if ordinal < 1:
            raise MathFlowError(f"{label} ordinal must be positive")
        ordinals.append(ordinal)
        _require_digest(record.get("postKnowledgeStateDigest"), f"{label} post-state digest")
        _require_transaction(
            record.get("postKnowledgeLedgerHead"),
            f"{label} post-state ledger head",
            nullable=True,
        )
        if record.get("status") not in SUBJECT_STATUSES:
            raise MathFlowError(f"{label} has an invalid status")
        block_reason = record.get("blockReason")
        blocker = record.get("blockedByTransactionId")
        if record.get("status") == "blocked":
            if block_reason not in BLOCK_REASONS:
                raise MathFlowError(f"{label} has an invalid block reason")
            _require_transaction(blocker, f"{label} blocker")
        elif block_reason is not None or blocker is not None:
            raise MathFlowError(f"{label} has blocker data while not blocked")
        attempt_count = _require_nonnegative_integer(
            record.get("attemptCount"), f"{label} attempts"
        )
        failures = record.get("failureHistory")
        if not isinstance(failures, list):
            raise MathFlowError(f"{label} failure history must be an array")
        if len(failures) > maximum_attempts:
            raise MathFlowError(f"{label} exceeds the fixed automatic retry policy")
        for failure_index, failure in enumerate(failures):
            validated = _validate_failure(failure, f"{label} failure {failure_index + 1}")
            if validated["attemptNumber"] != failure_index + 1:
                raise MathFlowError(f"{label} failure attempts must be consecutive")
            expected_exhausted = validated["attemptNumber"] >= maximum_attempts
            expected_retry = (
                None
                if expected_exhausted
                else validated["failedAt"]
                + base_retry_seconds * (2 ** (validated["attemptNumber"] - 1))
            )
            if (
                validated["exhausted"] != expected_exhausted
                or validated["retryNotBefore"] != expected_retry
            ):
                raise MathFlowError(f"{label} failure retry schedule is not deterministic")
        completion = _validate_completion(record.get("completion"), f"{label} completion")
        expected_attempts = len(failures)
        if completion is not None and completion["kind"] == "evaluated":
            expected_attempts += 1
            if completion["attemptNumber"] != expected_attempts:
                raise MathFlowError(f"{label} completion attempt is not consecutive")
        if attempt_count != expected_attempts:
            raise MathFlowError(f"{label} attempt count is inconsistent")
        repair_digests = record.get("affectedByRepairDigests")
        _require_digest_list(repair_digests, f"{label} repair flags")
        if record.get("recordDigest") != _subject_digest(record):
            raise MathFlowError(f"{label} digest mismatch")
    if len(subject_ids) != len(set(subject_ids)):
        raise MathFlowError("work-accounting schedule repeats a subject")
    canonical_subjects = [item for item in canonical_ids if item in set(subject_ids)]
    expected_ordinals = [canonical_ids.index(item) + 1 for item in subject_ids]
    if (
        subject_ids != canonical_subjects
        or ordinals != expected_ordinals
        or not set(subject_ids) <= set(resolved_ids)
    ):
        raise MathFlowError("work-accounting subjects are not in canonical ledger order")
    expected = _restated_subjects(
        [
            {key: copy.deepcopy(item) for key, item in record.items() if key != "recordDigest"}
            for record in subjects
        ],
        canonical_ids=list(canonical_ids),
        resolved_ids=list(resolved_ids),
    )
    if subjects != expected:
        raise MathFlowError("work-accounting subject statuses are not deterministic")
    repair_events = _require_digest_list(
        value.get("repairEventDigests"), "schedule repair event digests"
    )
    known_repair_digests = set(repair_events)
    if any(
        not set(record["affectedByRepairDigests"]) <= known_repair_digests
        for record in subjects
    ):
        raise MathFlowError("subject history flags reference an unknown repair event")
    if value.get("scheduleDigest") != _content_digest(value, "scheduleDigest"):
        raise MathFlowError("work-accounting schedule digest mismatch")
    return value


def _seal_claim(value: Mapping[str, object]) -> dict[str, object]:
    result = {key: copy.deepcopy(item) for key, item in value.items() if key != "claimDigest"}
    result["claimDigest"] = _content_digest(result, "claimDigest")
    return result


def _automatic_retry_key(
    schedule: Mapping[str, object],
    record: Mapping[str, object],
    *,
    predecessor_accounting_state_digest: str,
    predecessor_knowledge_state_digest: str,
) -> str:
    subject = {
        "problemId": schedule["problemId"],
        "projectionId": schedule["projectionId"],
        "projectionSpecDigest": schedule["projectionSpecDigest"],
        "rootContractDigest": schedule["rootContractDigest"],
        "subjectTransactionId": record["transactionId"],
        "predecessorAccountingStateDigest": predecessor_accounting_state_digest,
        "predecessorKnowledgeStateDigest": predecessor_knowledge_state_digest,
        "postKnowledgeStateDigest": record["postKnowledgeStateDigest"],
    }
    return f"sha256:{sha256_json(subject)}"


def _require_live_claim(
    schedule: Mapping[str, object],
    record: Mapping[str, object],
    transition: Mapping[str, object],
) -> None:
    failures = record["failureHistory"]
    assert isinstance(failures, list)
    previous = failures[-1]["claimDigest"] if failures else None
    exact_fields = {
        "subjectTransactionId": record["transactionId"],
        "ledgerOrdinal": record["ledgerOrdinal"],
        "attemptNumber": int(record["attemptCount"]) + 1,
        "subjectRecordDigest": record["recordDigest"],
        "predecessorAccountingStateDigest": schedule[
            "terminalAccountingStateDigest"
        ],
        "predecessorKnowledgeStateDigest": schedule["terminalKnowledgeStateDigest"],
        "postKnowledgeStateDigest": record["postKnowledgeStateDigest"],
        "postKnowledgeLedgerHead": record["postKnowledgeLedgerHead"],
        "previousAttemptClaimDigest": previous,
        "automaticRetryKey": _automatic_retry_key(
            schedule,
            record,
            predecessor_accounting_state_digest=str(
                schedule["terminalAccountingStateDigest"]
            ),
            predecessor_knowledge_state_digest=str(
                schedule["terminalKnowledgeStateDigest"]
            ),
        ),
    }
    if any(transition.get(field) != expected for field, expected in exact_fields.items()):
        raise MathFlowError("work-accounting transition claim is stale or noncanonical")


def validate_work_accounting_transition_claim(value: object) -> dict[str, object]:
    if not isinstance(value, dict) or set(value) != CLAIM_FIELDS:
        raise MathFlowError("work-accounting transition claim has an invalid envelope")
    if value.get("schemaVersion") != 1:
        raise MathFlowError("work-accounting transition claim has an unsupported version")
    _require_identifier(value.get("problemId"), "claim problem ID")
    _require_identifier(value.get("projectionId"), "claim projection ID")
    for field in (
        "projectionSpecDigest",
        "rootContractDigest",
        "subjectRecordDigest",
        "predecessorAccountingStateDigest",
        "predecessorKnowledgeStateDigest",
        "postKnowledgeStateDigest",
        "automaticRetryKey",
    ):
        _require_digest(value.get(field), f"claim {field}")
    _require_transaction(value.get("subjectTransactionId"), "claim subject")
    _require_transaction(
        value.get("postKnowledgeLedgerHead"), "claim post knowledge ledger head", nullable=True
    )
    ordinal = _require_nonnegative_integer(value.get("ledgerOrdinal"), "claim ledger ordinal")
    attempt = _require_nonnegative_integer(value.get("attemptNumber"), "claim attempt")
    if ordinal < 1 or attempt < 1:
        raise MathFlowError("claim ordinal and attempt must be positive")
    previous = _require_digest(
        value.get("previousAttemptClaimDigest"), "previous attempt claim digest", nullable=True
    )
    if (attempt == 1) != (previous is None):
        raise MathFlowError("claim previous attempt binding is inconsistent")
    if value.get("claimDigest") != _content_digest(value, "claimDigest"):
        raise MathFlowError("work-accounting transition claim digest mismatch")
    return value


def plan_next_work_accounting_transition(
    schedule: object,
    *,
    accounting_state: object,
    predecessor_knowledge_state: object,
    target_knowledge_state: object,
    root_contract: object,
    as_of: int,
) -> dict[str, object]:
    current = validate_work_accounting_schedule(schedule)
    now = _require_nonnegative_integer(as_of, "work-accounting planning time")
    maximum_attempts = int(current["retryPolicy"]["maximumAttempts"])
    contract = validate_root_contract(root_contract, str(current["problemId"]))
    predecessor_knowledge = validate_research_program_state_versioned(
        predecessor_knowledge_state, str(current["problemId"])
    )
    accounting = validate_work_accounting_state(
        accounting_state, predecessor_knowledge, contract
    )
    if accounting.get("evaluationMode") == "no-access":
        raise MathFlowError("an ephemeral no-access state cannot be scheduled")
    if accounting.get("stateDigest") != current.get("terminalAccountingStateDigest"):
        raise MathFlowError("scheduler terminal accounting state has changed")
    if predecessor_knowledge.get("stateDigest") != current.get("terminalKnowledgeStateDigest"):
        raise MathFlowError("scheduler predecessor knowledge state has changed")
    if accounting.get("processedSubmissionIds") != _processed_ids(current):
        raise MathFlowError("scheduler and accounting state disagree on processed submissions")
    frontier = next(
        (record for record in current["subjects"] if record["completion"] is None),
        None,
    )
    if frontier is None:
        return {
            "schemaVersion": 1,
            "eligible": False,
            "reasonCode": "all-accepted-submissions-processed",
            "message": "Every discovered accepted submission has been processed.",
            "nextEligibleAt": None,
            "claim": None,
        }
    if frontier["status"] == "blocked":
        return {
            "schemaVersion": 1,
            "eligible": False,
            "reasonCode": str(frontier["blockReason"]),
            "message": "Canonical predecessor coverage is incomplete.",
            "nextEligibleAt": None,
            "claim": None,
        }
    failures = frontier["failureHistory"]
    if failures:
        last_failure = failures[-1]
        if last_failure["exhausted"] or len(failures) >= maximum_attempts:
            return {
                "schemaVersion": 1,
                "eligible": False,
                "reasonCode": "automatic-retries-exhausted",
                "message": "The subject exhausted deterministic automatic retries.",
                "nextEligibleAt": None,
                "claim": None,
            }
        retry_at = int(last_failure["retryNotBefore"])
        if now < retry_at:
            return {
                "schemaVersion": 1,
                "eligible": False,
                "reasonCode": "retry-backoff-active",
                "message": "The deterministic retry backoff has not elapsed.",
                "nextEligibleAt": retry_at,
                "claim": None,
            }
    target_knowledge = validate_research_program_state_versioned(
        target_knowledge_state, str(current["problemId"])
    )
    if target_knowledge.get("stateDigest") != frontier.get("postKnowledgeStateDigest"):
        raise MathFlowError("scheduler received the wrong post-builder knowledge state")
    subject = str(frontier["transactionId"])
    if subject not in target_knowledge["contributions"]:
        raise MathFlowError("scheduled subject is not accepted in its post-builder state")
    attempt = int(frontier["attemptCount"]) + 1
    claim = _seal_claim(
        {
            "schemaVersion": 1,
            "problemId": current["problemId"],
            "projectionId": current["projectionId"],
            "projectionSpecDigest": current["projectionSpecDigest"],
            "rootContractDigest": current["rootContractDigest"],
            "subjectTransactionId": subject,
            "ledgerOrdinal": frontier["ledgerOrdinal"],
            "attemptNumber": attempt,
            "subjectRecordDigest": frontier["recordDigest"],
            "predecessorAccountingStateDigest": accounting["stateDigest"],
            "predecessorKnowledgeStateDigest": predecessor_knowledge["stateDigest"],
            "postKnowledgeStateDigest": target_knowledge["stateDigest"],
            "postKnowledgeLedgerHead": target_knowledge["ledgerHead"],
            "previousAttemptClaimDigest": failures[-1]["claimDigest"]
            if failures
            else None,
            "automaticRetryKey": _automatic_retry_key(
                current,
                frontier,
                predecessor_accounting_state_digest=str(accounting["stateDigest"]),
                predecessor_knowledge_state_digest=str(
                    predecessor_knowledge["stateDigest"]
                ),
            ),
        }
    )
    validate_work_accounting_transition_claim(claim)
    return {
        "schemaVersion": 1,
        "eligible": True,
        "reasonCode": "eligible",
        "message": "The next canonical accepted submission is eligible.",
        "nextEligibleAt": None,
        "claim": claim,
    }


def record_work_accounting_failure(
    schedule: object,
    claim: object,
    *,
    failure_kind: str,
    evidence_digest: str,
    failed_at: int,
) -> dict[str, object]:
    current = validate_work_accounting_schedule(schedule)
    transition = validate_work_accounting_transition_claim(claim)
    lane_fields = {
        "problemId",
        "projectionId",
        "projectionSpecDigest",
        "rootContractDigest",
    }
    if any(transition.get(field) != current.get(field) for field in lane_fields):
        raise MathFlowError("work-accounting failure belongs to another scheduling lane")
    if failure_kind not in FAILURE_KINDS:
        raise MathFlowError("work-accounting failure has an invalid kind")
    _require_digest(evidence_digest, "work-accounting failure evidence digest")
    failed_epoch = _require_nonnegative_integer(failed_at, "work-accounting failure time")
    delay = int(current["retryPolicy"]["baseRetrySeconds"])
    maximum_attempts = int(current["retryPolicy"]["maximumAttempts"])
    records = [copy.deepcopy(record) for record in current["subjects"]]
    frontier_index = next(
        (index for index, record in enumerate(records) if record["completion"] is None),
        None,
    )
    if frontier_index is None:
        raise MathFlowError("cannot fail a transition after all subjects are processed")
    record = records[frontier_index]
    if record["transactionId"] != transition["subjectTransactionId"]:
        raise MathFlowError("work-accounting failure does not target the canonical frontier")
    if record["recordDigest"] != transition["subjectRecordDigest"]:
        history = record["failureHistory"]
        if history and history[-1]["claimDigest"] == transition["claimDigest"]:
            expected = history[-1]
            if (
                expected["failureKind"] == failure_kind
                and expected["evidenceDigest"] == evidence_digest
                and expected["failedAt"] == failed_epoch
            ):
                return current
            raise MathFlowError("one transition claim cannot have two failure outcomes")
        raise MathFlowError("work-accounting failure uses a stale subject record")
    _require_live_claim(current, record, transition)
    attempt = int(transition["attemptNumber"])
    if attempt != int(record["attemptCount"]) + 1:
        raise MathFlowError("work-accounting failure attempt is not the next attempt")
    exhausted = attempt >= maximum_attempts
    retry_not_before = None if exhausted else failed_epoch + delay * (2 ** (attempt - 1))
    failure: dict[str, object] = {
        "failureKind": failure_kind,
        "claimDigest": transition["claimDigest"],
        "attemptNumber": attempt,
        "evidenceDigest": evidence_digest,
        "failedAt": failed_epoch,
        "retryNotBefore": retry_not_before,
        "exhausted": exhausted,
    }
    failure["failureDigest"] = _failure_digest(failure)
    record.pop("recordDigest", None)
    record["attemptCount"] = attempt
    record["failureHistory"].append(failure)
    records[frontier_index] = record
    records = _restated_subjects(
        records,
        canonical_ids=list(current["canonicalTransactionIds"]),
        resolved_ids=list(current["resolvedSubmissionIds"]),
    )
    result = _seal_schedule(
        {
            **{
                key: copy.deepcopy(value)
                for key, value in current.items()
                if key not in {"scheduleDigest", "subjects"}
            },
            "subjects": records,
        }
    )
    return validate_work_accounting_schedule(result)


def _seal_publication(value: Mapping[str, object]) -> dict[str, object]:
    result = {
        key: copy.deepcopy(item)
        for key, item in value.items()
        if key != "publicationManifestDigest"
    }
    result["publicationManifestDigest"] = _content_digest(
        result, "publicationManifestDigest"
    )
    return result


def validate_work_accounting_publication_manifest(value: object) -> dict[str, object]:
    if not isinstance(value, dict) or set(value) != PUBLICATION_FIELDS:
        raise MathFlowError("work-accounting publication manifest has an invalid envelope")
    if value.get("schemaVersion") != 1:
        raise MathFlowError("work-accounting publication manifest has an unsupported version")
    _require_identifier(value.get("problemId"), "publication problem ID")
    _require_identifier(value.get("projectionId"), "publication projection ID")
    _require_transaction(value.get("subjectTransactionId"), "publication subject")
    ordinal = _require_nonnegative_integer(value.get("ledgerOrdinal"), "publication ordinal")
    attempt = _require_nonnegative_integer(value.get("attemptNumber"), "publication attempt")
    if ordinal < 1 or attempt < 1:
        raise MathFlowError("publication ordinal and attempt must be positive")
    for field in (
        "projectionSpecDigest",
        "rootContractDigest",
        "claimDigest",
        "automaticRetryKey",
        "predecessorAccountingStateDigest",
        "predecessorKnowledgeStateDigest",
        "postKnowledgeStateDigest",
        "evaluationDigest",
        "noAccessPatchDigest",
        "withAccessPatchDigest",
        "noAccessStateDigest",
        "committedAccountingStateDigest",
    ):
        _require_digest(value.get(field), f"publication {field}")
    _require_positive_decimal(value.get("workValueHours"), "publication work value")
    if value.get("publicationManifestDigest") != _content_digest(
        value, "publicationManifestDigest"
    ):
        raise MathFlowError("work-accounting publication manifest digest mismatch")
    return value


def materialize_work_accounting_publication_manifest(
    claim: object,
    *,
    evaluation: object,
    no_access_patch: object,
    with_access_patch: object,
    predecessor_accounting_state: object,
    committed_accounting_state: object,
    predecessor_knowledge_state: object,
    target_knowledge_state: object,
    root_contract: object,
    topology_alignment: object | None = None,
) -> dict[str, object]:
    transition = validate_work_accounting_transition_claim(claim)
    result_value = validate_submission_work_value(evaluation)
    contract = validate_root_contract(root_contract, str(transition["problemId"]))
    predecessor_knowledge = validate_research_program_state_versioned(
        predecessor_knowledge_state, str(transition["problemId"])
    )
    target_knowledge = validate_research_program_state_versioned(
        target_knowledge_state, str(transition["problemId"])
    )
    predecessor = validate_work_accounting_state(
        predecessor_accounting_state, predecessor_knowledge, contract
    )
    committed = validate_work_accounting_state(
        committed_accounting_state, target_knowledge, contract
    )
    _, computed_committed, computed_evaluation = materialize_submission_work_value(
        base_state=predecessor,
        no_access_patch=no_access_patch,
        with_access_patch=with_access_patch,
        root_contract=contract,
        base_knowledge_state=predecessor_knowledge,
        target_knowledge_state=target_knowledge,
        topology_alignment=topology_alignment,
    )
    if result_value != computed_evaluation or committed != computed_committed:
        raise MathFlowError(
            "work-accounting publication does not reproduce from its primitive patches"
        )
    subject = transition["subjectTransactionId"]
    if (
        transition["rootContractDigest"] != contract["rootContractDigest"]
        or transition["predecessorAccountingStateDigest"] != predecessor["stateDigest"]
        or transition["predecessorKnowledgeStateDigest"] != predecessor_knowledge["stateDigest"]
        or transition["postKnowledgeStateDigest"] != target_knowledge["stateDigest"]
        or result_value["subjectTransactionId"] != subject
        or result_value["baseAccountingStateDigest"] != predecessor["stateDigest"]
        or result_value["baseKnowledgeStateDigest"] != predecessor_knowledge["stateDigest"]
        or result_value["targetKnowledgeStateDigest"] != target_knowledge["stateDigest"]
        or committed["stateDigest"] != result_value["withAccessStateDigest"]
        or committed["predecessorStateDigest"] != predecessor["stateDigest"]
        or committed["evaluationMode"] != "with-access"
        or committed["subjectTransactionId"] != subject
    ):
        raise MathFlowError("work-accounting publication inputs do not form one exact transition")
    manifest = _seal_publication(
        {
            "schemaVersion": 1,
            "problemId": transition["problemId"],
            "projectionId": transition["projectionId"],
            "projectionSpecDigest": transition["projectionSpecDigest"],
            "rootContractDigest": transition["rootContractDigest"],
            "subjectTransactionId": subject,
            "ledgerOrdinal": transition["ledgerOrdinal"],
            "attemptNumber": transition["attemptNumber"],
            "claimDigest": transition["claimDigest"],
            "automaticRetryKey": transition["automaticRetryKey"],
            "predecessorAccountingStateDigest": predecessor["stateDigest"],
            "predecessorKnowledgeStateDigest": predecessor_knowledge["stateDigest"],
            "postKnowledgeStateDigest": target_knowledge["stateDigest"],
            "evaluationDigest": result_value["evaluationDigest"],
            "noAccessPatchDigest": result_value["noAccessPatchDigest"],
            "withAccessPatchDigest": result_value["withAccessPatchDigest"],
            "noAccessStateDigest": result_value["noAccessStateDigest"],
            "committedAccountingStateDigest": committed["stateDigest"],
            "workValueHours": result_value["workValueHours"],
        }
    )
    return validate_work_accounting_publication_manifest(manifest)


def apply_work_accounting_publication(
    schedule: object,
    claim: object,
    manifest: object,
    *,
    evaluation: object,
    no_access_patch: object,
    with_access_patch: object,
    predecessor_accounting_state: object,
    committed_accounting_state: object,
    predecessor_knowledge_state: object,
    target_knowledge_state: object,
    root_contract: object,
    topology_alignment: object | None = None,
) -> dict[str, object]:
    current = validate_work_accounting_schedule(schedule)
    transition = validate_work_accounting_transition_claim(claim)
    publication = validate_work_accounting_publication_manifest(manifest)
    lane_fields = {
        "problemId",
        "projectionId",
        "projectionSpecDigest",
        "rootContractDigest",
    }
    if any(transition.get(field) != current.get(field) for field in lane_fields):
        raise MathFlowError("publication belongs to another scheduling lane")
    identity_fields = {
        "problemId",
        "projectionId",
        "projectionSpecDigest",
        "rootContractDigest",
        "subjectTransactionId",
        "ledgerOrdinal",
        "attemptNumber",
        "claimDigest",
        "automaticRetryKey",
        "predecessorAccountingStateDigest",
        "predecessorKnowledgeStateDigest",
        "postKnowledgeStateDigest",
    }
    if any(publication.get(field) != transition.get(field) for field in identity_fields):
        raise MathFlowError("publication manifest does not match its transition claim")
    expected_publication = materialize_work_accounting_publication_manifest(
        transition,
        evaluation=evaluation,
        no_access_patch=no_access_patch,
        with_access_patch=with_access_patch,
        predecessor_accounting_state=predecessor_accounting_state,
        committed_accounting_state=committed_accounting_state,
        predecessor_knowledge_state=predecessor_knowledge_state,
        target_knowledge_state=target_knowledge_state,
        root_contract=root_contract,
        topology_alignment=topology_alignment,
    )
    if publication != expected_publication:
        raise MathFlowError("publication manifest is not the canonical exact transition")
    records = [copy.deepcopy(record) for record in current["subjects"]]
    matching = next(
        (
            record
            for record in records
            if record["transactionId"] == transition["subjectTransactionId"]
        ),
        None,
    )
    if matching is None:
        raise MathFlowError("publication subject is absent from work-accounting schedule")
    completion = matching.get("completion")
    if completion is not None:
        if (
            completion.get("kind") == "evaluated"
            and completion.get("publicationManifestDigest")
            == publication["publicationManifestDigest"]
        ):
            return current
        raise MathFlowError("processed work-accounting subject has another publication")
    frontier = next(record for record in records if record["completion"] is None)
    if frontier["transactionId"] != transition["subjectTransactionId"]:
        raise MathFlowError("publication does not target the canonical accounting frontier")
    _require_live_claim(current, frontier, transition)
    if (
        current["terminalAccountingStateDigest"]
        != transition["predecessorAccountingStateDigest"]
    ):
        raise MathFlowError("publication transition claim is stale")
    contract = validate_root_contract(root_contract, str(current["problemId"]))
    target_knowledge = validate_research_program_state_versioned(
        target_knowledge_state, str(current["problemId"])
    )
    committed = validate_work_accounting_state(
        committed_accounting_state, target_knowledge, contract
    )
    if (
        target_knowledge["stateDigest"] != transition["postKnowledgeStateDigest"]
        or committed["stateDigest"] != publication["committedAccountingStateDigest"]
        or committed["predecessorStateDigest"]
        != transition["predecessorAccountingStateDigest"]
        or committed["processedSubmissionIds"]
        != [*_processed_ids(current), transition["subjectTransactionId"]]
    ):
        raise MathFlowError("publication committed state does not advance the exact predecessor")
    index = next(
        index
        for index, record in enumerate(records)
        if record["transactionId"] == transition["subjectTransactionId"]
    )
    updated = records[index]
    updated.pop("recordDigest", None)
    updated["attemptCount"] = transition["attemptNumber"]
    updated["completion"] = {
        "kind": "evaluated",
        "attemptNumber": transition["attemptNumber"],
        "evaluationDigest": publication["evaluationDigest"],
        "committedAccountingStateDigest": publication["committedAccountingStateDigest"],
        "publicationManifestDigest": publication["publicationManifestDigest"],
    }
    records[index] = updated
    records = _restated_subjects(
        records,
        canonical_ids=list(current["canonicalTransactionIds"]),
        resolved_ids=list(current["resolvedSubmissionIds"]),
    )
    result = _seal_schedule(
        {
            **{
                key: copy.deepcopy(value)
                for key, value in current.items()
                if key not in {
                    "scheduleDigest",
                    "subjects",
                    "terminalAccountingStateDigest",
                    "terminalKnowledgeStateDigest",
                }
            },
            "terminalAccountingStateDigest": committed["stateDigest"],
            "terminalKnowledgeStateDigest": target_knowledge["stateDigest"],
            "subjects": records,
        }
    )
    return validate_work_accounting_schedule(result)


def materialize_work_accounting_state_repair(
    schedule: object,
    *,
    reason_kind: str,
    base_accounting_state: object,
    repaired_accounting_state: object,
    knowledge_state: object,
    root_contract: object,
    affected_submission_ids: Iterable[str],
    evidence_refs: Iterable[str],
) -> dict[str, object]:
    current = validate_work_accounting_schedule(schedule)
    if reason_kind not in REPAIR_REASONS:
        raise MathFlowError("work-accounting state repair has an invalid reason")
    if any(record["completion"] is None for record in current["subjects"]):
        raise MathFlowError("prospective state repair requires an empty subject backlog")
    contract = validate_root_contract(root_contract, str(current["problemId"]))
    knowledge = validate_research_program_state_versioned(
        knowledge_state, str(current["problemId"])
    )
    base = validate_work_accounting_state(base_accounting_state, knowledge, contract)
    repaired = validate_work_accounting_state(
        repaired_accounting_state, knowledge, contract
    )
    affected = list(affected_submission_ids)
    processed = _processed_ids(current)
    if (
        len(affected) != len(set(affected))
        or affected != [item for item in processed if item in set(affected)]
        or not affected
    ):
        raise MathFlowError(
            "state repair affected history must be a nonempty canonical processed subset"
        )
    if (
        base["stateDigest"] != current["terminalAccountingStateDigest"]
        or base["knowledgeStateDigest"] != current["terminalKnowledgeStateDigest"]
        or repaired["predecessorStateDigest"] != base["stateDigest"]
        or repaired["knowledgeStateDigest"] != knowledge["stateDigest"]
        or repaired["evaluationMode"] != "baseline"
        or repaired["subjectTransactionId"] is not None
        or repaired["processedSubmissionIds"] != base["processedSubmissionIds"]
    ):
        raise MathFlowError("state repair does not prospectively advance the live accounting state")
    evidence = sorted(set(evidence_refs))
    _require_sorted_unique_strings(evidence, "state repair evidence references")
    if not evidence:
        raise MathFlowError("state repair requires evidence")
    completion_by_subject = {
        str(record["transactionId"]): record["completion"]
        for record in current["subjects"]
    }
    history = [
        {
            "subjectTransactionId": transaction_id,
            "evaluationDigest": completion_by_subject[transaction_id]["evaluationDigest"]
            if completion_by_subject[transaction_id]["kind"] == "evaluated"
            else None,
        }
        for transaction_id in affected
    ]
    event: dict[str, object] = {
        "schemaVersion": 1,
        "problemId": current["problemId"],
        "projectionId": current["projectionId"],
        "projectionSpecDigest": current["projectionSpecDigest"],
        "rootContractDigest": current["rootContractDigest"],
        "reasonKind": reason_kind,
        "baseAccountingStateDigest": base["stateDigest"],
        "repairedAccountingStateDigest": repaired["stateDigest"],
        "knowledgeStateDigest": knowledge["stateDigest"],
        "affectedHistory": history,
        "evidenceRefs": evidence,
        "suffixReplay": False,
    }
    event["repairEventDigest"] = _content_digest(event, "repairEventDigest")
    return validate_work_accounting_state_repair(event)


def validate_work_accounting_state_repair(value: object) -> dict[str, object]:
    if not isinstance(value, dict) or set(value) != REPAIR_FIELDS:
        raise MathFlowError("work-accounting state repair has an invalid envelope")
    if value.get("schemaVersion") != 1:
        raise MathFlowError("work-accounting state repair has an unsupported version")
    _require_identifier(value.get("problemId"), "state repair problem ID")
    _require_identifier(value.get("projectionId"), "state repair projection ID")
    if value.get("reasonKind") not in REPAIR_REASONS:
        raise MathFlowError("work-accounting state repair has an invalid reason")
    for field in (
        "projectionSpecDigest",
        "rootContractDigest",
        "baseAccountingStateDigest",
        "repairedAccountingStateDigest",
        "knowledgeStateDigest",
    ):
        _require_digest(value.get(field), f"state repair {field}")
    history = value.get("affectedHistory")
    if not isinstance(history, list) or not history:
        raise MathFlowError("state repair affected history must be nonempty")
    ids: list[str] = []
    for flag in history:
        if not isinstance(flag, dict) or set(flag) != HISTORY_FLAG_FIELDS:
            raise MathFlowError("state repair history flag has invalid fields")
        transaction_id = _require_transaction(
            flag.get("subjectTransactionId"), "state repair affected subject"
        )
        assert isinstance(transaction_id, str)
        ids.append(transaction_id)
        _require_digest(
            flag.get("evaluationDigest"), "state repair affected evaluation", nullable=True
        )
    if len(ids) != len(set(ids)):
        raise MathFlowError("state repair repeats an affected subject")
    evidence = _require_sorted_unique_strings(value.get("evidenceRefs"), "state repair evidence")
    if not evidence:
        raise MathFlowError("state repair requires evidence")
    if value.get("suffixReplay") is not False:
        raise MathFlowError("work-accounting v1 state repair cannot replay historical suffixes")
    if value.get("repairEventDigest") != _content_digest(value, "repairEventDigest"):
        raise MathFlowError("work-accounting state repair digest mismatch")
    return value


def apply_work_accounting_state_repair(
    schedule: object,
    event: object,
    *,
    repaired_accounting_state: object,
    knowledge_state: object,
    root_contract: object,
) -> dict[str, object]:
    current = validate_work_accounting_schedule(schedule)
    repair = validate_work_accounting_state_repair(event)
    if repair["repairEventDigest"] in current["repairEventDigests"]:
        return current
    identity_fields = {"problemId", "projectionId", "projectionSpecDigest", "rootContractDigest"}
    if any(repair.get(field) != current.get(field) for field in identity_fields):
        raise MathFlowError("state repair belongs to another accounting lane")
    if any(record["completion"] is None for record in current["subjects"]):
        raise MathFlowError("prospective state repair requires an empty subject backlog")
    contract = validate_root_contract(root_contract, str(current["problemId"]))
    knowledge = validate_research_program_state_versioned(
        knowledge_state, str(current["problemId"])
    )
    repaired = validate_work_accounting_state(
        repaired_accounting_state, knowledge, contract
    )
    if (
        repair["baseAccountingStateDigest"] != current["terminalAccountingStateDigest"]
        or repair["repairedAccountingStateDigest"] != repaired["stateDigest"]
        or repair["knowledgeStateDigest"] != knowledge["stateDigest"]
        or repaired["predecessorStateDigest"] != current["terminalAccountingStateDigest"]
        or repaired["processedSubmissionIds"] != _processed_ids(current)
        or repaired["evaluationMode"] != "baseline"
        or repaired["subjectTransactionId"] is not None
    ):
        raise MathFlowError("state repair is stale or does not preserve processed history")
    affected_ids = {
        str(flag["subjectTransactionId"]) for flag in repair["affectedHistory"]
    }
    completion_by_subject = {
        str(record["transactionId"]): record["completion"]
        for record in current["subjects"]
    }
    expected_history = [
        {
            "subjectTransactionId": str(record["transactionId"]),
            "evaluationDigest": completion_by_subject[str(record["transactionId"])][
                "evaluationDigest"
            ]
            if completion_by_subject[str(record["transactionId"])]["kind"]
            == "evaluated"
            else None,
        }
        for record in current["subjects"]
        if record["transactionId"] in affected_ids
    ]
    if repair["affectedHistory"] != expected_history:
        raise MathFlowError("state repair affected-history flags do not match live history")
    records = []
    for raw_record in current["subjects"]:
        record = copy.deepcopy(raw_record)
        if record["transactionId"] in affected_ids:
            record.pop("recordDigest", None)
            record["affectedByRepairDigests"] = sorted(
                {*record["affectedByRepairDigests"], repair["repairEventDigest"]}
            )
        records.append(record)
    records = _restated_subjects(
        records,
        canonical_ids=list(current["canonicalTransactionIds"]),
        resolved_ids=list(current["resolvedSubmissionIds"]),
    )
    result = _seal_schedule(
        {
            **{
                key: copy.deepcopy(value)
                for key, value in current.items()
                if key not in {
                    "scheduleDigest",
                    "subjects",
                    "terminalAccountingStateDigest",
                    "terminalKnowledgeStateDigest",
                    "repairEventDigests",
                }
            },
            "terminalAccountingStateDigest": repaired["stateDigest"],
            "terminalKnowledgeStateDigest": knowledge["stateDigest"],
            "subjects": records,
            "repairEventDigests": sorted(
                {*current["repairEventDigests"], repair["repairEventDigest"]}
            ),
        }
    )
    return validate_work_accounting_schedule(result)
