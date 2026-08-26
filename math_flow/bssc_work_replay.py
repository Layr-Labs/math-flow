"""Provider-free discovery and migration for the historical BSSC v5 chain.

This module is intentionally inactive.  It reads immutable Git objects, validates
the historical builder-v5 chain, and describes the exact bootstrap boundary for
work accounting.  It never calls a model, publishes a projection, or writes to
the canonical/projection histories.
"""

from __future__ import annotations

import copy
import json
import re
from pathlib import Path, PurePosixPath
from typing import Mapping

from .artifacts import sha256_bytes
from .errors import MathFlowError
from .repository import is_ancestor, ledger, read_bytes_at, resolve_commit, sha256_json
from .research_state import empty_research_program_state, validate_research_program_state
from .research_topology import (
    derive_research_topology_alignment,
    validate_research_program_state_v2,
)


DIGEST = re.compile(r"^sha256:[0-9a-f]{64}$")
GIT_SHA = re.compile(r"^[0-9a-f]{40}$")
PROFILE = "math-flow/hierarchical-research-v5"
SOURCE_FIELDS = {
    "schemaVersion",
    "problemId",
    "mainCommit",
    "problemLedgerDigest",
    "projectionCommit",
    "projectionIndexPath",
    "terminalRunDigest",
    "terminalStateDigest",
    "outputProfile",
}
REPORT_FIELDS = {
    "schemaVersion",
    "problemId",
    "status",
    "source",
    "canonicalSubmissionCount",
    "acceptedSubmissionCount",
    "excludedSubmissionCount",
    "coveredSubjectTransactionIds",
    "bootstrapCutoff",
    "subjects",
    "replayTransitions",
    "missingAccountingEvaluationSubjectTransactionIds",
    "providerRequirements",
    "invariants",
    "activationSeam",
    "reportDigest",
}


def _content_digest(value: Mapping[str, object], field: str) -> str:
    return f"sha256:{sha256_json({key: item for key, item in value.items() if key != field})}"


def _require_digest(value: object, label: str) -> str:
    if not isinstance(value, str) or not DIGEST.fullmatch(value):
        raise MathFlowError(f"{label} must be a sha256 digest")
    return value


def _require_commit(value: object, label: str) -> str:
    if not isinstance(value, str) or not GIT_SHA.fullmatch(value):
        raise MathFlowError(f"{label} must be a full Git commit")
    return value


def _safe_repository_path(value: object, label: str) -> str:
    if not isinstance(value, str):
        raise MathFlowError(f"{label} must be a repository path")
    path = PurePosixPath(value)
    if path.is_absolute() or not path.parts or ".." in path.parts:
        raise MathFlowError(f"{label} is unsafe")
    return path.as_posix()


def validate_bssc_replay_source(value: object) -> dict[str, object]:
    """Validate the immutable source pins used for historical discovery."""

    if not isinstance(value, dict) or set(value) != SOURCE_FIELDS:
        raise MathFlowError("BSSC replay source has an invalid envelope")
    if value.get("schemaVersion") != 1:
        raise MathFlowError("BSSC replay source has an unsupported version")
    if value.get("problemId") != "bssc-sum-capacity":
        raise MathFlowError("BSSC replay source must identify bssc-sum-capacity")
    _require_commit(value.get("mainCommit"), "BSSC replay main commit")
    _require_digest(value.get("problemLedgerDigest"), "BSSC problem ledger digest")
    _require_commit(value.get("projectionCommit"), "BSSC projection commit")
    _safe_repository_path(value.get("projectionIndexPath"), "BSSC projection index")
    _require_digest(value.get("terminalRunDigest"), "BSSC terminal run digest")
    _require_digest(value.get("terminalStateDigest"), "BSSC terminal state digest")
    if value.get("outputProfile") != PROFILE:
        raise MathFlowError("BSSC replay source must pin hierarchical research v5")
    return value


def load_bssc_replay_source(path: Path) -> dict[str, object]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise MathFlowError(f"could not read BSSC replay source {path}: {exc}") from exc
    return validate_bssc_replay_source(value)


def _read_json_at(root: Path, commit: str, path: str, label: str) -> tuple[bytes, object]:
    try:
        raw = read_bytes_at(root, commit, path)
        value = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise MathFlowError(f"{label} is not valid JSON: {path}") from exc
    return raw, value


def _artifact(
    run: Mapping[str, object], role: str, *, expected_path: str
) -> dict[str, object]:
    artifacts = run.get("artifacts")
    if not isinstance(artifacts, list):
        raise MathFlowError("historical builder run has an invalid artifact index")
    matches = [item for item in artifacts if isinstance(item, dict) and item.get("role") == role]
    if len(matches) != 1 or matches[0].get("path") != expected_path:
        raise MathFlowError(f"historical builder run must contain one exact {role} artifact")
    result = matches[0]
    _require_digest(result.get("digest"), f"historical {role} artifact digest")
    return result


def _read_run_artifact(
    root: Path,
    projection_commit: str,
    run_path: str,
    run: Mapping[str, object],
    role: str,
    relative_path: str,
) -> object:
    entry = _artifact(run, role, expected_path=relative_path)
    path = f"{run_path}/{relative_path}"
    raw, value = _read_json_at(root, projection_commit, path, role)
    if sha256_bytes(raw) != entry["digest"]:
        raise MathFlowError(f"historical {role} artifact digest mismatch")
    return value


def migrate_research_program_state_v1_to_v2(
    state: object, *, base_state_digest: str | None
) -> dict[str, object]:
    """Losslessly wrap a validated v1 state as a lineage-neutral v2 state.

    The migration adds only the v2 lineage field and recomputes structural
    digests.  ``base_state_digest`` is supplied by the serialized migration
    harness because source-v1 and migrated-v2 digests intentionally differ.
    """

    legacy = validate_research_program_state(state)
    if base_state_digest is not None:
        _require_digest(base_state_digest, "migrated research base state digest")
    result = copy.deepcopy(legacy)
    result["schemaVersion"] = 2
    result["baseStateDigest"] = base_state_digest
    programs = result["programs"]
    assert isinstance(programs, dict)
    for program in programs.values():
        assert isinstance(program, dict)
        program["lineage"] = []
        program["digest"] = _content_digest(program, "digest")
    result["stateDigest"] = _content_digest(result, "stateDigest")
    return validate_research_program_state_v2(result, str(result["problemId"]))


def _run_path(run_digest: str) -> str:
    hexadecimal = run_digest.removeprefix("sha256:")
    return f"objects/knowledge-build/{hexadecimal[:2]}/{hexadecimal}"


def _load_v5_chain(
    root: Path, source: Mapping[str, object]
) -> list[dict[str, object]]:
    projection_commit = str(source["projectionCommit"])
    index_path = str(source["projectionIndexPath"])
    raw_index, index = _read_json_at(
        root, projection_commit, index_path, "historical projection run index"
    )
    if not isinstance(index, list):
        raise MathFlowError("historical projection run index must be an array")
    indexed: dict[str, dict[str, object]] = {}
    for entry in index:
        if (
            isinstance(entry, dict)
            and isinstance(entry.get("runDigest"), str)
            and isinstance(entry.get("path"), str)
        ):
            indexed[str(entry["runDigest"])] = entry
    if not raw_index:
        raise MathFlowError("historical projection run index is empty")

    reverse_chain: list[dict[str, object]] = []
    observed: set[str] = set()
    current: str | None = str(source["terminalRunDigest"])
    while current is not None:
        if current in observed:
            raise MathFlowError("historical builder-v5 base-run chain contains a cycle")
        observed.add(current)
        expected_path = _run_path(current)
        indexed_run = indexed.get(current)
        if (
            not isinstance(indexed_run, dict)
            or indexed_run.get("runKind") != "knowledge-build"
            or indexed_run.get("path") != expected_path
        ):
            raise MathFlowError("historical builder-v5 run is absent or misaddressed")
        raw_run, run = _read_json_at(
            root, projection_commit, f"{expected_path}/run.json", "historical builder run"
        )
        if sha256_bytes(raw_run) != current:
            raise MathFlowError("historical builder run digest mismatch")
        if not isinstance(run, dict):
            raise MathFlowError("historical builder run must be an object")
        if (
            run.get("runKind") != "knowledge-build"
            or run.get("problemId") != source["problemId"]
            or run.get("outputProfile") != source["outputProfile"]
        ):
            raise MathFlowError("historical builder run has the wrong identity")
        batch = _read_run_artifact(
            root,
            projection_commit,
            expected_path,
            run,
            "research-batch-input",
            "input/research-batch.json",
        )
        state = _read_run_artifact(
            root,
            projection_commit,
            expected_path,
            run,
            "research-program-state",
            "state/state.json",
        )
        if not isinstance(batch, dict) or not isinstance(state, dict):
            raise MathFlowError("historical builder artifacts must be objects")
        validate_research_program_state(state, str(source["problemId"]))
        judgments = batch.get("judgments")
        if not isinstance(judgments, list) or not judgments:
            raise MathFlowError("historical research batch must contain judgments")
        accepted: list[str] = []
        excluded: list[str] = []
        for judgment in judgments:
            if not isinstance(judgment, dict):
                raise MathFlowError("historical research judgment must be an object")
            subject = _require_commit(
                judgment.get("subjectTransactionId"), "historical judgment subject"
            )
            judgment_digest = _require_digest(
                judgment.get("runDigest"), "historical validity run digest"
            )
            judgment_entry = indexed.get(judgment_digest)
            expected_judgment_path = (
                "objects/judgment/"
                f"{judgment_digest.removeprefix('sha256:')[:2]}/"
                f"{judgment_digest.removeprefix('sha256:')}"
            )
            if (
                not isinstance(judgment_entry, dict)
                or judgment_entry.get("runKind") != "judgment"
                or judgment_entry.get("path") != expected_judgment_path
            ):
                raise MathFlowError("historical validity run is absent or misaddressed")
            raw_judgment_run, judgment_run = _read_json_at(
                root,
                projection_commit,
                f"{expected_judgment_path}/run.json",
                "historical validity run",
            )
            if sha256_bytes(raw_judgment_run) != judgment_digest or not isinstance(
                judgment_run, dict
            ):
                raise MathFlowError("historical validity run digest mismatch")
            inputs = judgment_run.get("inputs")
            if (
                judgment_run.get("problemId") != source["problemId"]
                or judgment_run.get("runKind") != "judgment"
                or not isinstance(inputs, dict)
                or inputs.get("subjectTransactionIds") != [subject]
            ):
                raise MathFlowError("historical validity run has the wrong subject")
            judgment_record = _read_run_artifact(
                root,
                projection_commit,
                expected_judgment_path,
                judgment_run,
                "judgment-record",
                "judgment.json",
            )
            if not isinstance(judgment_record, dict):
                raise MathFlowError("historical validity judgment must be an object")
            record_subjects = judgment_record.get("subjects")
            if (
                judgment_record.get("judgmentId") != judgment.get("judgmentId")
                or not isinstance(record_subjects, list)
                or [
                    item.get("id") for item in record_subjects if isinstance(item, dict)
                ]
                != [subject]
            ):
                raise MathFlowError("historical formation judgment is not validity-bound")
            accepted_claims = judgment.get("acceptedClaimKeys")
            excluded_assessments = judgment.get("excludedAssessments")
            if not isinstance(accepted_claims, list) or not isinstance(
                excluded_assessments, list
            ):
                raise MathFlowError("historical judgment has invalid acceptance fields")
            if bool(accepted_claims) == bool(excluded_assessments):
                raise MathFlowError("historical judgment must be exactly accepted or excluded")
            (accepted if accepted_claims else excluded).append(subject)
        reverse_chain.append(
            {
                "runDigest": current,
                "baseRunDigest": run.get("baseRun"),
                "runPath": expected_path,
                "runLedgerHead": run.get("ledgerHead"),
                "batch": batch,
                "state": state,
                "acceptedSubjectTransactionIds": accepted,
                "excludedSubjectTransactionIds": excluded,
            }
        )
        base = run.get("baseRun")
        if base is not None:
            _require_digest(base, "historical builder base run")
        current = str(base) if isinstance(base, str) else None

    chain = list(reversed(reverse_chain))
    prior_state: dict[str, object] | None = None
    prior_run_digest: str | None = None
    latest_accepted_subject: str | None = None
    for ordinal, record in enumerate(chain, start=1):
        state = record["state"]
        batch = record["batch"]
        assert isinstance(state, dict)
        assert isinstance(batch, dict)
        if record["baseRunDigest"] != prior_run_digest:
            raise MathFlowError("historical builder-v5 run chain is not serialized")
        batch_subjects = [
            str(judgment["subjectTransactionId"]) for judgment in batch["judgments"]
        ]
        run_ledger_head = _require_commit(
            record["runLedgerHead"], "historical builder run ledger head"
        )
        if not is_ancestor(root, batch_subjects[-1], run_ledger_head):
            raise MathFlowError("historical builder run ledger head is before its batch frontier")
        expected_base = (
            prior_state["stateDigest"]
            if prior_state is not None
            else empty_research_program_state(str(source["problemId"]))["stateDigest"]
        )
        if batch.get("baseProgramStateDigest") != expected_base:
            raise MathFlowError("historical research batches are not state-serialized")
        prior_ids = set(prior_state["contributions"]) if prior_state is not None else set()
        current_ids = set(state["contributions"])
        if current_ids - prior_ids != set(record["acceptedSubjectTransactionIds"]):
            raise MathFlowError("historical builder state does not match accepted judgments")
        if not prior_ids <= current_ids:
            raise MathFlowError("historical builder state removes accepted contributions")
        if record["acceptedSubjectTransactionIds"]:
            if state.get("baseStateDigest") != expected_base:
                raise MathFlowError("historical accepted state has the wrong base digest")
            latest_accepted_subject = str(record["acceptedSubjectTransactionIds"][-1])
        elif prior_state is None or state != prior_state:
            raise MathFlowError("historical excluded-only run must preserve the exact state")
        if state.get("ledgerHead") != latest_accepted_subject:
            raise MathFlowError("historical state ledger head is not its accepted frontier")
        record["formationOrdinal"] = ordinal
        prior_state = state
        prior_run_digest = str(record["runDigest"])
    if chain[-1]["state"]["stateDigest"] != source["terminalStateDigest"]:
        raise MathFlowError("historical terminal knowledge-state digest mismatch")
    return chain


def _subject_record(
    ledger_record: Mapping[str, object],
    formation: Mapping[str, object],
    *,
    status: str,
    cutoff_formation_ordinal: int,
) -> dict[str, object]:
    formation_ordinal = int(formation["formationOrdinal"])
    accepted = status == "accepted"
    if not accepted:
        disposition = "excluded-not-accounting-subject"
    elif formation_ordinal <= cutoff_formation_ordinal:
        disposition = "bootstrap-baseline-only"
    else:
        disposition = "exact-post-state-awaiting-provider"
    state = formation["state"]
    assert isinstance(state, dict)
    return {
        "ledgerOrdinal": ledger_record["ordinal"],
        "transactionId": ledger_record["transactionId"],
        "contributionId": ledger_record["contributionId"],
        "validityStatus": status,
        "formationOrdinal": formation_ordinal,
        "formationRunDigest": formation["runDigest"],
        "formationAcceptedSubjectCount": len(
            formation["acceptedSubjectTransactionIds"]
        ),
        "accountingDisposition": disposition,
        "sourcePostKnowledgeStateDigest": (
            state["stateDigest"] if disposition == "exact-post-state-awaiting-provider" else None
        ),
    }


def build_bssc_work_replay_readiness_report(
    repository_root: Path, source: object
) -> dict[str, object]:
    """Discover the exact historical chain and emit a deterministic readiness report."""

    pins = validate_bssc_replay_source(source)
    root = repository_root.resolve()
    main_commit = resolve_commit(root, str(pins["mainCommit"]))
    projection_commit = resolve_commit(root, str(pins["projectionCommit"]))
    if main_commit != pins["mainCommit"] or projection_commit != pins["projectionCommit"]:
        raise MathFlowError("BSSC replay source commit pin did not resolve exactly")
    canonical = ledger(root, str(pins["problemId"]), head=main_commit)
    if canonical["problemLedgerDigest"] != pins["problemLedgerDigest"]:
        raise MathFlowError("BSSC canonical problem ledger digest changed")
    transactions = canonical["transactions"]
    assert isinstance(transactions, list)
    chain = _load_v5_chain(root, pins)

    flattened: list[str] = []
    formation_by_subject: dict[str, dict[str, object]] = {}
    status_by_subject: dict[str, str] = {}
    for formation in chain:
        batch = formation["batch"]
        assert isinstance(batch, dict)
        for judgment in batch["judgments"]:
            subject = str(judgment["subjectTransactionId"])
            if subject in formation_by_subject:
                raise MathFlowError("historical formation repeats a canonical subject")
            flattened.append(subject)
            formation_by_subject[subject] = formation
            status_by_subject[subject] = (
                "accepted" if judgment["acceptedClaimKeys"] else "excluded"
            )
    canonical_ids = [str(item["transactionId"]) for item in transactions]
    if flattened != canonical_ids:
        raise MathFlowError(
            "historical validity/formation subjects do not match first-parent ledger order"
        )

    ambiguous = [
        formation
        for formation in chain
        if len(formation["acceptedSubjectTransactionIds"]) > 1
    ]
    if not ambiguous:
        raise MathFlowError("BSSC historical chain unexpectedly has no batched accepted run")
    cutoff = ambiguous[-1]
    cutoff_ordinal = int(cutoff["formationOrdinal"])
    cutoff_state = cutoff["state"]
    assert isinstance(cutoff_state, dict)

    subjects = [
        _subject_record(
            item,
            formation_by_subject[str(item["transactionId"])],
            status=status_by_subject[str(item["transactionId"])],
            cutoff_formation_ordinal=cutoff_ordinal,
        )
        for item in transactions
    ]
    bootstrap_ids = [
        str(item["transactionId"])
        for item in subjects
        if item["accountingDisposition"] == "bootstrap-baseline-only"
    ]
    replay_subjects = [
        item
        for item in subjects
        if item["accountingDisposition"] == "exact-post-state-awaiting-provider"
    ]
    replay_ids = [str(item["transactionId"]) for item in replay_subjects]
    for item in replay_subjects:
        if item["formationAcceptedSubjectCount"] != 1:
            raise MathFlowError("post-cutoff historical replay is not one subject per state")

    migrated_before = migrate_research_program_state_v1_to_v2(
        cutoff_state, base_state_digest=None
    )
    replay_transitions: list[dict[str, object]] = []
    source_before_digest = str(cutoff_state["stateDigest"])
    for item in replay_subjects:
        formation = formation_by_subject[str(item["transactionId"])]
        source_after = formation["state"]
        assert isinstance(source_after, dict)
        migrated_after = migrate_research_program_state_v1_to_v2(
            source_after, base_state_digest=str(migrated_before["stateDigest"])
        )
        alignment = derive_research_topology_alignment(migrated_before, migrated_after)
        replay_transitions.append(
            {
                "subjectTransactionId": item["transactionId"],
                "ledgerOrdinal": item["ledgerOrdinal"],
                "sourceBeforeKnowledgeStateDigest": source_before_digest,
                "sourceAfterKnowledgeStateDigest": source_after["stateDigest"],
                "migratedBeforeKnowledgeStateDigest": migrated_before["stateDigest"],
                "migratedAfterKnowledgeStateDigest": migrated_after["stateDigest"],
                "topologyAlignmentDigest": alignment["alignmentDigest"],
                "createdAccountingNodeCount": sum(
                    entry["entityKind"] in {"program", "thread"}
                    for entry in alignment["created"]
                ),
                "createdSemanticItemCount": sum(
                    entry["entityKind"] == "item" for entry in alignment["created"]
                ),
            }
        )
        migrated_before = migrated_after
        source_before_digest = str(source_after["stateDigest"])

    accepted_ids = [
        str(item["transactionId"])
        for item in subjects
        if item["validityStatus"] == "accepted"
    ]
    excluded_ids = [
        str(item["transactionId"])
        for item in subjects
        if item["validityStatus"] == "excluded"
    ]
    report: dict[str, object] = {
        "schemaVersion": 1,
        "problemId": pins["problemId"],
        "status": "activation-blocked-on-provider-inputs",
        "source": {
            "mainCommit": main_commit,
            "problemLedgerDigest": canonical["problemLedgerDigest"],
            "projectionCommit": projection_commit,
            "terminalRunDigest": pins["terminalRunDigest"],
            "terminalStateDigest": pins["terminalStateDigest"],
            "outputProfile": pins["outputProfile"],
            "formationRunCount": len(chain),
        },
        "canonicalSubmissionCount": len(subjects),
        "acceptedSubmissionCount": len(accepted_ids),
        "excludedSubmissionCount": len(excluded_ids),
        "coveredSubjectTransactionIds": canonical_ids,
        "bootstrapCutoff": {
            "reasonCode": "last-historical-multi-accepted-builder-v5-batch",
            "formationOrdinal": cutoff_ordinal,
            "runDigest": cutoff["runDigest"],
            "ledgerOrdinal": max(
                int(item["ledgerOrdinal"])
                for item in subjects
                if item["formationOrdinal"] <= cutoff_ordinal
            ),
            "sourceKnowledgeStateDigest": cutoff_state["stateDigest"],
            "migratedKnowledgeStateDigest": replay_transitions[0][
                "migratedBeforeKnowledgeStateDigest"
            ]
            if replay_transitions
            else migrated_before["stateDigest"],
            "bootstrapSubjectTransactionIds": bootstrap_ids,
        },
        "subjects": subjects,
        "replayTransitions": replay_transitions,
        "missingAccountingEvaluationSubjectTransactionIds": accepted_ids,
        "providerRequirements": [
            {
                "kind": "bootstrap-root-contract-and-primitives",
                "subjectTransactionIds": bootstrap_ids,
                "description": (
                    "A real provider must supply the root contract and complete baseline "
                    "program/thread human-researcher-hour primitives at the cutoff state."
                ),
            },
            {
                "kind": "per-submission-counterfactual-responses",
                "subjectTransactionIds": replay_ids,
                "description": (
                    "A real provider must supply safe-facts, no-access, and with-access "
                    "responses for each exact post-cutoff submission transition."
                ),
            },
        ],
        "invariants": {
            "canonicalFirstParentOrderVerified": True,
            "validityAndFormationCoverageVerified": True,
            "oneExactPostStatePerReplaySubmission": len(replay_transitions)
            == len(replay_ids),
            "predecessorChainVerified": all(
                current["migratedBeforeKnowledgeStateDigest"]
                == previous["migratedAfterKnowledgeStateDigest"]
                for previous, current in zip(
                    replay_transitions, replay_transitions[1:], strict=False
                )
            ),
            "accountingNodeKinds": ["program", "thread"],
            "semanticLeafKinds": ["item"],
            "itemsExcludedFromNumericAccounting": True,
            "strictPositiveReductionHistoricallyVerified": False,
        },
        "activationSeam": (
            "Production activation must atomically seed the CAS lane with the migrated "
            "cutoff knowledge state and a provider-authored baseline accounting state, "
            "then execute the four exact replay transitions. The current production CAS "
            "initializer intentionally rejects pre-populated historical baselines."
        ),
    }
    report["reportDigest"] = _content_digest(report, "reportDigest")
    return validate_bssc_work_replay_readiness_report(report)


def validate_bssc_work_replay_readiness_report(value: object) -> dict[str, object]:
    """Validate the generated report without consulting Git or a provider."""

    if not isinstance(value, dict) or set(value) != REPORT_FIELDS:
        raise MathFlowError("BSSC replay readiness report has an invalid envelope")
    if value.get("schemaVersion") != 1 or value.get("problemId") != "bssc-sum-capacity":
        raise MathFlowError("BSSC replay readiness report has an invalid identity")
    if value.get("status") != "activation-blocked-on-provider-inputs":
        raise MathFlowError("BSSC replay readiness report must fail closed")
    subjects = value.get("subjects")
    transitions = value.get("replayTransitions")
    cutoff = value.get("bootstrapCutoff")
    invariants = value.get("invariants")
    if not all(
        isinstance(item, expected)
        for item, expected in (
            (subjects, list),
            (transitions, list),
            (cutoff, dict),
            (invariants, dict),
        )
    ):
        raise MathFlowError("BSSC replay readiness report has invalid collections")
    assert isinstance(subjects, list)
    assert isinstance(transitions, list)
    assert isinstance(cutoff, dict)
    assert isinstance(invariants, dict)
    subject_ids = [item.get("transactionId") for item in subjects if isinstance(item, dict)]
    if (
        len(subject_ids) != len(subjects)
        or subject_ids != value.get("coveredSubjectTransactionIds")
        or len(subject_ids) != len(set(subject_ids))
        or [item.get("ledgerOrdinal") for item in subjects if isinstance(item, dict)]
        != list(range(1, len(subjects) + 1))
    ):
        raise MathFlowError("BSSC replay readiness subjects are not canonical")
    accepted = [
        item
        for item in subjects
        if isinstance(item, dict) and item.get("validityStatus") == "accepted"
    ]
    excluded = [
        item
        for item in subjects
        if isinstance(item, dict) and item.get("validityStatus") == "excluded"
    ]
    if len(accepted) != value.get("acceptedSubmissionCount") or len(excluded) != value.get(
        "excludedSubmissionCount"
    ):
        raise MathFlowError("BSSC replay readiness subject counts are inconsistent")
    replay_ids = [
        item.get("subjectTransactionId")
        for item in transitions
        if isinstance(item, dict)
    ]
    expected_replay_ids = [
        item.get("transactionId")
        for item in accepted
        if item.get("accountingDisposition") == "exact-post-state-awaiting-provider"
    ]
    if replay_ids != expected_replay_ids or len(replay_ids) != len(set(replay_ids)):
        raise MathFlowError("BSSC replay transitions are not one per exact subject")
    for previous, current in zip(transitions, transitions[1:], strict=False):
        if (
            not isinstance(previous, dict)
            or not isinstance(current, dict)
            or previous.get("migratedAfterKnowledgeStateDigest")
            != current.get("migratedBeforeKnowledgeStateDigest")
        ):
            raise MathFlowError("BSSC replay migrated predecessor chain is broken")
    if (
        invariants.get("accountingNodeKinds") != ["program", "thread"]
        or invariants.get("semanticLeafKinds") != ["item"]
        or invariants.get("itemsExcludedFromNumericAccounting") is not True
        or invariants.get("strictPositiveReductionHistoricallyVerified") is not False
    ):
        raise MathFlowError("BSSC replay readiness accounting boundaries are unsafe")
    missing = value.get("missingAccountingEvaluationSubjectTransactionIds")
    if missing != [item.get("transactionId") for item in accepted]:
        raise MathFlowError("BSSC replay report must expose every missing evaluation")
    for field in (
        "sourceKnowledgeStateDigest",
        "migratedKnowledgeStateDigest",
        "runDigest",
    ):
        _require_digest(cutoff.get(field), f"BSSC replay cutoff {field}")
    if value.get("reportDigest") != _content_digest(value, "reportDigest"):
        raise MathFlowError("BSSC replay readiness report digest mismatch")
    return value
