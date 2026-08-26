"""Provider-free frontier planning for the serial BSSC builder-v6 producer.

The hosted producer must not rediscover or regenerate historical validity
judgments.  This module reads the immutable validity-v4 runs pinned by the
BSSC bootstrap source, copies their exact bytes into a staging directory, and
checks the published builder-v6 predecessor chain before exposing one next
accepted subject.
"""

from __future__ import annotations

import json
import re
from pathlib import Path, PurePosixPath
from typing import Mapping

from .artifacts import read_verified_artifact, verify_bundle
from .bssc_work_replay import _load_v5_chain, validate_bssc_replay_source
from .coordination import lane_id, load_scheduler
from .errors import MathFlowError
from .governance import validate_projection_spec
from .judges import load_judge_spec
from .judgments import load_judgment_bundle
from .repository import (
    ledger,
    list_files_at,
    read_bytes_at,
    resolve_commit,
    sha256_json,
)
from .research_projection import load_research_build_bundle


PROBLEM_ID = "bssc-sum-capacity"
PROJECTION_ID = "openrouter-research-v4"
BUILDER_PATH = "protocol/judges/openrouter-hierarchical-research-builder-v6.json"
BUILDER_PROFILE = "math-flow/hierarchical-research-v6"
VALIDITY_PROFILE = "math-flow/validity-judgment-v4"
DIGEST = re.compile(r"^sha256:[0-9a-f]{64}$")


def _content_digest(value: Mapping[str, object], field: str) -> str:
    return f"sha256:{sha256_json({key: item for key, item in value.items() if key != field})}"


def _bundle_path(kind: str, run_digest: str) -> str:
    hexadecimal = run_digest.removeprefix("sha256:")
    return f"objects/{kind}/{hexadecimal[:2]}/{hexadecimal}"


def _load_active_projection(
    repository_root: Path, projection: object
) -> tuple[dict[str, object], str, str]:
    spec = validate_projection_spec(
        projection,
        PROJECTION_ID,
        lambda relative: (repository_root / relative).read_text(encoding="utf-8"),
    )
    if (
        spec.get("status") != "active"
        or spec.get("allowedProblems") != [PROBLEM_ID]
        or spec.get("knowledgeBuilder") != BUILDER_PATH
        or spec.get("reconciliationJudge") is not None
        or spec.get("scheduling", {}).get("maximumJudgmentsPerBuild") != 1
    ):
        raise MathFlowError(
            "serial BSSC producer requires the active BSSC-only builder-v6 projection"
        )
    projection_digest = f"sha256:{sha256_json(spec)}"
    builder = load_judge_spec(repository_root / BUILDER_PATH)
    if builder.get("implementation") != "openrouter-hierarchical-research-builder-v6":
        raise MathFlowError("serial BSSC producer has the wrong builder implementation")
    return spec, projection_digest, f"sha256:{sha256_json(builder)}"


def _accepted_frontier(
    repository_root: Path, source: object
) -> tuple[dict[str, object], list[dict[str, object]]]:
    pins = validate_bssc_replay_source(source)
    root = repository_root.resolve()
    if (
        resolve_commit(root, str(pins["mainCommit"])) != pins["mainCommit"]
        or resolve_commit(root, str(pins["projectionCommit"]))
        != pins["projectionCommit"]
    ):
        raise MathFlowError("BSSC producer source pins do not resolve exactly")
    canonical = ledger(root, PROBLEM_ID, str(pins["mainCommit"]))
    if canonical.get("problemLedgerDigest") != pins["problemLedgerDigest"]:
        raise MathFlowError("BSSC producer canonical ledger digest changed")
    transactions = canonical.get("transactions")
    if not isinstance(transactions, list) or len(transactions) != 25:
        raise MathFlowError("BSSC producer requires the exact 25-submission ledger")
    canonical_by_id = {
        str(item["transactionId"]): item
        for item in transactions
        if isinstance(item, dict)
    }

    formation_subjects: list[str] = []
    accepted: list[dict[str, object]] = []
    for formation in _load_v5_chain(root, pins):
        batch = formation.get("batch")
        if not isinstance(batch, dict) or not isinstance(batch.get("judgments"), list):
            raise MathFlowError("BSSC historical validity batch is invalid")
        for judgment in batch["judgments"]:
            if not isinstance(judgment, dict):
                raise MathFlowError("BSSC historical validity entry is invalid")
            subject = str(judgment["subjectTransactionId"])
            formation_subjects.append(subject)
            if not judgment["acceptedClaimKeys"]:
                continue
            transaction = canonical_by_id.get(subject)
            if not isinstance(transaction, dict):
                raise MathFlowError("accepted BSSC subject is outside the canonical ledger")
            accepted.append(
                {
                    "acceptedTransitionOrdinal": len(accepted) + 1,
                    "ledgerOrdinal": int(transaction["ordinal"]),
                    "subjectTransactionId": subject,
                    "judgmentId": str(judgment["judgmentId"]),
                    "judgmentRunDigest": str(judgment["runDigest"]),
                }
            )
    canonical_subjects = [str(item["transactionId"]) for item in transactions]
    if formation_subjects != canonical_subjects:
        raise MathFlowError(
            "BSSC producer validity subjects do not match canonical first-parent order"
        )
    if len(accepted) != 16:
        raise MathFlowError("BSSC producer requires exactly 16 accepted subjects")
    if [item["ledgerOrdinal"] for item in accepted] != [
        3,
        4,
        5,
        9,
        10,
        11,
        12,
        14,
        15,
        16,
        17,
        18,
        19,
        21,
        24,
        25,
    ]:
        raise MathFlowError("BSSC producer accepted ordinal frontier changed")
    return pins, accepted


def _materialize_validity_bundle(
    repository_root: Path,
    *,
    projection_commit: str,
    entry: Mapping[str, object],
    destination: Path,
) -> None:
    run_digest = str(entry["judgmentRunDigest"])
    source_prefix = _bundle_path("judgment", run_digest)
    files = list_files_at(repository_root, projection_commit, source_prefix)
    if not files or f"{source_prefix}/run.json" not in files:
        raise MathFlowError("pinned BSSC validity bundle is missing")
    expected_relative = []
    for source_path in files:
        relative = PurePosixPath(source_path).relative_to(source_prefix)
        if relative.is_absolute() or ".." in relative.parts or not relative.parts:
            raise MathFlowError("pinned BSSC validity bundle has an unsafe path")
        target = destination.joinpath(*relative.parts)
        value = read_bytes_at(repository_root, projection_commit, source_path)
        if target.exists():
            if not target.is_file() or target.read_bytes() != value:
                raise MathFlowError(
                    "materialized BSSC validity bundle differs from its immutable source"
                )
        else:
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(value)
        expected_relative.append(relative.as_posix())
    actual_relative = sorted(
        path.relative_to(destination).as_posix()
        for path in destination.rglob("*")
        if path.is_file() and not path.is_symlink()
    )
    if actual_relative != sorted(expected_relative):
        raise MathFlowError("materialized BSSC validity bundle contains extra files")
    manifest, verified_digest = verify_bundle(destination)
    loaded_manifest, judgment, loaded_digest = load_judgment_bundle(destination)
    subjects = judgment.get("subjects")
    if (
        verified_digest != run_digest
        or loaded_digest != run_digest
        or manifest != loaded_manifest
        or manifest.get("outputProfile") != VALIDITY_PROFILE
        or manifest.get("problemId") != PROBLEM_ID
        or not isinstance(subjects, list)
        or len(subjects) != 1
        or subjects[0].get("id") != entry["subjectTransactionId"]
        or judgment.get("judgmentId") != entry["judgmentId"]
    ):
        raise MathFlowError("materialized BSSC validity bundle identity mismatch")


def _published_v6_chain(
    projection_root: Path,
    latest_run_digest: str | None,
    *,
    projection_digest: str,
    builder_digest: str,
    accepted: list[dict[str, object]],
) -> list[dict[str, object]]:
    reverse: list[dict[str, object]] = []
    observed: set[str] = set()
    current = latest_run_digest
    while current is not None:
        if not DIGEST.fullmatch(current) or current in observed:
            raise MathFlowError("published BSSC builder-v6 chain has an invalid base link")
        observed.add(current)
        relative = _bundle_path("knowledge-build", current)
        bundle = projection_root / relative
        manifest, state, loaded_digest = load_research_build_bundle(bundle)
        if loaded_digest != current:
            raise MathFlowError("published BSSC builder-v6 run is misaddressed")
        try:
            submission = json.loads(
                read_verified_artifact(
                    bundle, manifest, "research-builder-submission-input"
                )
            )
        except json.JSONDecodeError as exc:
            raise MathFlowError(
                "published BSSC builder-v6 submission input is invalid JSON"
            ) from exc
        judge = manifest.get("judgeSpec")
        inputs = manifest.get("inputs")
        if (
            manifest.get("problemId") != PROBLEM_ID
            or manifest.get("outputProfile") != BUILDER_PROFILE
            or not isinstance(judge, dict)
            or judge.get("digest") != builder_digest
            or not isinstance(inputs, dict)
            or inputs.get("projectionSpecDigest") != projection_digest
            or not isinstance(submission, dict)
        ):
            raise MathFlowError("published BSSC builder-v6 run belongs to another lane")
        reverse.append(
            {
                "runDigest": current,
                "baseRunDigest": manifest.get("baseRun"),
                "subjectTransactionId": submission.get("subjectTransactionId"),
                "judgmentId": submission.get("judgmentId"),
                "judgmentRunDigest": inputs.get("judgmentRunDigest"),
                "knowledgeStateDigest": state.get("stateDigest"),
            }
        )
        base = manifest.get("baseRun")
        if base is not None and (not isinstance(base, str) or not DIGEST.fullmatch(base)):
            raise MathFlowError("published BSSC builder-v6 run has an invalid base digest")
        current = base if isinstance(base, str) else None

    chain = list(reversed(reverse))
    if len(chain) > len(accepted):
        raise MathFlowError("published BSSC builder-v6 chain exceeds the accepted frontier")
    prior: str | None = None
    for index, record in enumerate(chain):
        expected = accepted[index]
        if (
            record["baseRunDigest"] != prior
            or record["subjectTransactionId"] != expected["subjectTransactionId"]
            or record["judgmentId"] != expected["judgmentId"]
            or record["judgmentRunDigest"] != expected["judgmentRunDigest"]
        ):
            raise MathFlowError(
                "published BSSC builder-v6 chain is not the canonical accepted prefix"
            )
        prior = str(record["runDigest"])
    return chain


def plan_bssc_research_v4_frontier(
    repository_root: Path,
    *,
    projection_root: Path,
    scheduler_file: Path,
    materialization_root: Path,
    replay_source: object,
    projection: object,
    expected_projection_digest: str | None = None,
) -> dict[str, object]:
    """Validate the published prefix and materialize inputs through one frontier.

    This function never claims a scheduler lease and never calls a provider.  A
    caller may feed ``judgmentBundles`` to ``knowledge-trigger`` and then claim
    with ``maximumJudgmentsPerBuild=1``.
    """

    root = repository_root.resolve()
    projection_root = projection_root.resolve()
    materialization_root = materialization_root.resolve()
    spec, projection_digest, builder_digest = _load_active_projection(root, projection)
    if (
        expected_projection_digest is not None
        and expected_projection_digest != projection_digest
    ):
        raise MathFlowError(
            "admitted BSSC projection digest differs from the active runtime contract"
        )
    pins, accepted = _accepted_frontier(root, replay_source)
    identifier = lane_id(PROBLEM_ID, builder_digest, projection_digest)
    scheduler = load_scheduler(scheduler_file)
    lane = scheduler["lanes"].get(identifier)
    if lane is None:
        latest_run = None
        observed_ids: list[str] = []
        pending_ids: list[str] = []
    else:
        if (
            not isinstance(lane, dict)
            or lane.get("problemId") != PROBLEM_ID
            or lane.get("builderSpecDigest") != builder_digest
            or lane.get("projectionSpecDigest") != projection_digest
            or lane.get("minimumIntervalSeconds")
            != spec["scheduling"]["knowledgeMinimumIntervalSeconds"]
            or lane.get("activeBuild") is not None
            or lane.get("observedConflictIds") != []
            or lane.get("pendingConflictIds") != []
        ):
            raise MathFlowError("published BSSC builder-v6 scheduler lane is inconsistent")
        latest_run = lane.get("latestStateRun")
        if latest_run is not None and (
            not isinstance(latest_run, str) or not DIGEST.fullmatch(latest_run)
        ):
            raise MathFlowError("published BSSC scheduler has an invalid latest run")
        observed_ids = lane.get("observedJudgmentIds")
        pending_ids = lane.get("pendingJudgmentIds")
        if not isinstance(observed_ids, list) or not isinstance(pending_ids, list):
            raise MathFlowError("published BSSC scheduler has invalid judgment indexes")

    chain = _published_v6_chain(
        projection_root,
        latest_run,
        projection_digest=projection_digest,
        builder_digest=builder_digest,
        accepted=accepted,
    )
    completed_count = len(chain)
    expected_completed_ids = sorted(
        str(item["judgmentId"]) for item in accepted[:completed_count]
    )
    next_id = (
        str(accepted[completed_count]["judgmentId"])
        if completed_count < len(accepted)
        else None
    )
    allowed_observed = [expected_completed_ids]
    if next_id is not None:
        allowed_observed.append(sorted(expected_completed_ids + [next_id]))
    if (
        observed_ids not in allowed_observed
        or pending_ids not in ([], [next_id] if next_id is not None else [])
        or (pending_ids and observed_ids != sorted(expected_completed_ids + [next_id]))
    ):
        raise MathFlowError(
            "published BSSC scheduler does not match the canonical accepted frontier"
        )

    materialized: list[dict[str, object]] = []
    next_transition: dict[str, object] | None = None
    if completed_count < len(accepted):
        next_transition = dict(accepted[completed_count])
        for entry in accepted[: completed_count + 1]:
            relative = f"accepted-{int(entry['acceptedTransitionOrdinal']):02d}"
            _materialize_validity_bundle(
                root,
                projection_commit=str(pins["projectionCommit"]),
                entry=entry,
                destination=materialization_root / relative,
            )
            materialized.append(
                {
                    "acceptedTransitionOrdinal": entry["acceptedTransitionOrdinal"],
                    "subjectTransactionId": entry["subjectTransactionId"],
                    "judgmentId": entry["judgmentId"],
                    "judgmentRunDigest": entry["judgmentRunDigest"],
                    "relativePath": relative,
                }
            )
        next_transition["problemLedgerDigest"] = ledger(
            root, PROBLEM_ID, str(next_transition["subjectTransactionId"])
        )["problemLedgerDigest"]
        next_transition["baseRunDigest"] = latest_run
        next_transition["baseRunRelativePath"] = (
            _bundle_path("knowledge-build", str(latest_run))
            if isinstance(latest_run, str)
            else None
        )
        next_transition["judgmentBundleRelativePath"] = materialized[-1][
            "relativePath"
        ]

    result: dict[str, object] = {
        "schemaVersion": 1,
        "problemId": PROBLEM_ID,
        "status": "complete" if next_transition is None else "ready",
        "source": {
            "canonicalMainCommit": pins["mainCommit"],
            "problemLedgerDigest": pins["problemLedgerDigest"],
            "validityProjectionCommit": pins["projectionCommit"],
        },
        "projection": {
            "id": PROJECTION_ID,
            "projectionSpecDigest": projection_digest,
            "builderSpecDigest": builder_digest,
            "maximumJudgmentsPerBuild": 1,
        },
        "laneId": identifier,
        "acceptedSubmissionCount": len(accepted),
        "acceptedLedgerOrdinals": [item["ledgerOrdinal"] for item in accepted],
        "acceptedTransitionOrder": [
            item["subjectTransactionId"] for item in accepted
        ],
        "completedAcceptedCount": completed_count,
        "remainingAcceptedCount": len(accepted) - completed_count,
        "completedTransitions": chain,
        "nextTransition": next_transition,
        "judgmentBundles": materialized,
    }
    result["planDigest"] = _content_digest(result, "planDigest")
    return result


def load_json_file(path: Path, label: str) -> object:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise MathFlowError(f"could not read {label} {path}: {exc}") from exc
