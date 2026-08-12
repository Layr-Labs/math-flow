from __future__ import annotations

import json
from pathlib import Path, PurePosixPath

from .artifacts import read_verified_artifact, verify_bundle
from .credit import load_credit_assignment_bundle
from .credit_schedule import ordered_credit_runs
from .errors import MathFlowError
from .governance import list_active_projections
from .projection_dependencies import (
    resolve_projection_dependencies,
    same_projection_dependency_state,
)


CREDIT_RUNNERS = {
    "openrouter-credit-assignment-v1",
    "openrouter-credit-assignment-v2",
}


def _credit_projections(
    root: Path, problem: str, head: str
) -> list[dict[str, object]]:
    listing = list_active_projections(
        root, problem, head, engine="overlay-repository-v1"
    )
    return [
        item
        for item in listing["projections"]
        if isinstance(item.get("runner"), dict)
        and item["runner"].get("implementation") in CREDIT_RUNNERS
    ]


def _select_credit_projection(
    projections: list[dict[str, object]], requested: str | None
) -> tuple[dict[str, object] | None, dict[str, object] | None]:
    choices = [str(item["projectionId"]) for item in projections]
    if requested is not None:
        matches = [item for item in projections if item["projectionId"] == requested]
        if len(matches) != 1:
            suffix = ": " + ", ".join(choices) if choices else ""
            raise MathFlowError(
                f"unknown credit projection {requested!r}; choices{suffix}"
            )
        return matches[0], None
    if not projections:
        return None, {
            "status": "unavailable",
            "reasonCode": "no-governed-credit-projection",
            "message": "No active governed credit projection applies to this problem.",
            "availableProjectionIds": [],
        }
    if len(projections) > 1:
        return None, {
            "status": "selection-required",
            "reasonCode": "multiple-governed-credit-projections",
            "message": "Select one governed credit projection with --credit-projection.",
            "availableProjectionIds": choices,
        }
    return projections[0], None


def _dependency_failure_status(message: str) -> tuple[str, str]:
    if "stale" in message:
        return "stale", "knowledge-dependency-stale"
    if any(
        marker in message
        for marker in (
            "active build",
            "pending knowledge inputs",
            "no published state",
        )
    ):
        return "pending", "knowledge-dependency-pending"
    return "unavailable", "knowledge-dependency-unavailable"


def _problem_index_entries(
    projection_root: Path, problem: str
) -> list[dict[str, object]]:
    index = projection_root / "indexes" / "problems" / problem / "runs.json"
    if not index.exists():
        return []
    try:
        value = json.loads(index.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise MathFlowError(f"could not read projection credit index: {exc}") from exc
    if not isinstance(value, list) or any(not isinstance(item, dict) for item in value):
        raise MathFlowError("projection credit index must be an object array")
    return value


def _indexed_bundle(
    projection_root: Path, entry: dict[str, object]
) -> tuple[Path, str]:
    expected_digest = entry.get("runDigest")
    relative = entry.get("path")
    if not isinstance(expected_digest, str) or not isinstance(relative, str):
        raise MathFlowError("projection credit index entry is incomplete")
    relative_path = PurePosixPath(relative)
    if relative_path.is_absolute() or ".." in relative_path.parts:
        raise MathFlowError(f"projection credit path escapes its root: {relative}")
    root = projection_root.resolve()
    target = root.joinpath(*relative_path.parts).resolve()
    try:
        target.relative_to(root)
    except ValueError as exc:
        raise MathFlowError(
            f"projection credit path escapes its root: {relative}"
        ) from exc
    return target, expected_digest


def _load_credit_candidate(
    target: Path, expected_digest: str
) -> dict[str, object]:
    manifest, credit_index, run_digest = load_credit_assignment_bundle(target)
    if run_digest != expected_digest:
        raise MathFlowError(
            "projection credit digest does not match its problem index"
        )
    dependency_lock = json.loads(
        read_verified_artifact(target, manifest, "dependency-lock")
    )
    credit_input = json.loads(read_verified_artifact(target, manifest, "credit-input"))
    report = read_verified_artifact(target, manifest, "credit-report").decode("utf-8")
    return {
        "manifest": manifest,
        "creditIndex": credit_index,
        "dependencyLock": dependency_lock,
        "creditInput": credit_input,
        "report": report,
        "runDigest": run_digest,
    }


def _candidate_identity(
    projection_root: Path, entry: dict[str, object]
) -> tuple[str | None, str | None]:
    """Return a verified bundle's declared projection identity when readable.

    Full credit verification happens after this inexpensive attribution step. A
    malformed bundle with no trustworthy manifest identity remains unattributed
    rather than being silently assigned to every governed overlay.
    """

    target, expected_digest = _indexed_bundle(projection_root, entry)
    manifest, run_digest = verify_bundle(target)
    if run_digest != expected_digest:
        raise MathFlowError(
            "projection credit digest does not match its problem index"
        )
    inputs = manifest.get("inputs")
    if not isinstance(inputs, dict):
        return None, None
    projection_id = inputs.get("projectionId")
    projection_digest = inputs.get("projectionSpecDigest")
    return (
        str(projection_id) if isinstance(projection_id, str) else None,
        str(projection_digest) if isinstance(projection_digest, str) else None,
    )


def _candidate_summary(candidate: dict[str, object]) -> dict[str, object]:
    manifest = candidate["manifest"]
    dependency_lock = candidate["dependencyLock"]
    inputs = manifest["inputs"]
    return {
        "runDigest": candidate["runDigest"],
        "ledgerHead": manifest["ledgerHead"],
        "problemLedgerHead": manifest["problemLedgerHead"],
        "problemLedgerDigest": manifest["problemLedgerDigest"],
        "projectionSpecDigest": inputs["projectionSpecDigest"],
        "dependencyLockDigest": inputs["dependencyLockDigest"],
        "dependencyConsumer": dependency_lock["consumer"],
        "dependencyRunDigests": list(inputs["dependencyRunDigests"]),
        "dependencies": list(dependency_lock["dependencies"]),
        "schedule": inputs.get("schedule"),
    }


def _assignment_context(candidate: dict[str, object]) -> list[dict[str, object]]:
    credit_input = candidate["creditInput"]
    metadata = {
        str(item["transactionId"]): item for item in credit_input["transactions"]
    }
    assignments: list[dict[str, object]] = []
    for raw_assignment in candidate["creditIndex"]["assignments"]:
        transaction_id = str(raw_assignment["transactionId"])
        transaction = metadata[transaction_id]
        direction_registration_ids = raw_assignment.get(
            "directionRegistrationTransactionIds"
        )
        reservation_ids = raw_assignment.get("reservationTransactionIds")
        assignments.append(
            {
                "ordinal": transaction["ordinal"],
                "transactionId": transaction_id,
                "contributionId": transaction["contributionId"],
                "path": transaction["path"],
                "author": transaction["author"],
                "significance": raw_assignment["significance"],
                "roles": list(raw_assignment["roles"]),
                "knowledgeRefs": list(raw_assignment["knowledgeRefs"]),
                **(
                    {
                        "directionRegistrationTransactionIds": list(
                            direction_registration_ids
                        )
                    }
                    if isinstance(direction_registration_ids, list)
                    else {
                        "reservationTransactionIds": list(reservation_ids)
                        if isinstance(reservation_ids, list)
                        else []
                    }
                ),
                "reportSection": raw_assignment["reportSection"],
            }
        )
    return assignments


def _validate_candidate_history(
    candidate: dict[str, object], canonical_transactions: list[dict[str, object]]
) -> None:
    transactions = candidate["creditInput"].get("transactions")
    normalized = (
        [
            {key: value for key, value in item.items() if key != "canonicalOrdinal"}
            for item in transactions
        ]
        if isinstance(transactions, list)
        and all(isinstance(item, dict) for item in transactions)
        else transactions
    )
    if (
        not isinstance(transactions, list)
        or len(transactions) > len(canonical_transactions)
        or normalized != canonical_transactions[: len(transactions)]
    ):
        raise MathFlowError(
            "published credit input does not match canonical transaction history"
        )


def _select_stale_candidate(
    candidates: list[dict[str, object]], canonical_transaction_ids: list[str]
) -> tuple[dict[str, object] | None, bool]:
    positions = {
        transaction_id: ordinal
        for ordinal, transaction_id in enumerate(canonical_transaction_ids, start=1)
    }

    def progress(candidate: dict[str, object]) -> int:
        transaction_ids = [
            str(item["transactionId"])
            for item in candidate["creditInput"]["transactions"]
        ]
        if not transaction_ids:
            return 0
        if any(value not in positions for value in transaction_ids):
            return -1
        return max(positions[value] for value in transaction_ids)

    usable = [item for item in candidates if progress(item) >= 0]
    if not usable:
        return None, False
    latest_progress = max(progress(item) for item in usable)
    latest = [item for item in usable if progress(item) == latest_progress]
    if len(latest) == 1:
        return latest[0], False
    projection_digests = {
        str(item["manifest"]["inputs"].get("projectionSpecDigest"))
        for item in latest
    }
    if len(projection_digests) == 1:
        digest = next(iter(projection_digests))
        chain_candidates = [
            {
                **item,
                "schedule": item["manifest"]["inputs"].get("schedule"),
            }
            for item in usable
            if item["manifest"]["inputs"].get("projectionSpecDigest") == digest
        ]
        try:
            chain = ordered_credit_runs(chain_candidates)
        except MathFlowError:
            chain = []
        if chain and progress(chain[-1]) == latest_progress:
            return chain[-1], False
    return None, True


def build_credit_context(
    root: Path,
    projection_root: Path,
    problem: str,
    head: str,
    canonical_transactions: list[dict[str, object]],
    *,
    credit_projection_id: str | None = None,
) -> tuple[dict[str, object], str | None]:
    """Resolve verified qualitative credit for an agent context snapshot.

    The result is descriptive only. It never calls a model and never changes
    mathematical validity or the selected knowledge projection.
    """

    projections = _credit_projections(root, problem, head)
    selected, selection_status = _select_credit_projection(
        projections, credit_projection_id
    )
    semantics = {
        "kind": "qualitative-non-zero-sum",
        "affectsMathematicalValidity": False,
    }
    if selection_status is not None:
        return {"schemaVersion": 1, "semantics": semantics, **selection_status}, None
    if selected is None:  # pragma: no cover - guarded by _select_credit_projection
        raise AssertionError("credit projection selection has no result")

    projection_id = str(selected["projectionId"])
    projection_digest = str(selected["projectionSpecDigest"])
    result: dict[str, object] = {
        "schemaVersion": 1,
        "semantics": semantics,
        "availableProjectionIds": [
            str(item["projectionId"]) for item in projections
        ],
        "projection": {
            "id": projection_id,
            "digest": projection_digest,
            "runner": selected["runner"],
            "dependencies": selected["dependencies"],
        },
    }

    expected_lock: dict[str, object] | None = None
    dependency_error: str | None = None
    try:
        expected_lock = resolve_projection_dependencies(
            root, projection_root, projection_id, problem, head
        )
        result["dependency"] = {
            "status": "current",
            "lockDigest": expected_lock["dependencyLockDigest"],
            "consumer": expected_lock["consumer"],
            "problemLedger": expected_lock["problemLedger"],
            "runs": expected_lock["dependencies"],
        }
    except MathFlowError as exc:
        dependency_error = str(exc)
        status, reason_code = _dependency_failure_status(dependency_error)
        result["dependency"] = {
            "status": status,
            "reasonCode": reason_code,
            "message": dependency_error,
        }

    candidates: list[dict[str, object]] = []
    invalid: list[dict[str, str]] = []
    for entry in _problem_index_entries(projection_root, problem):
        if entry.get("runKind") != "credit-assignment":
            continue
        try:
            declared_id, _ = _candidate_identity(projection_root, entry)
            if declared_id != projection_id:
                continue
            target, expected_digest = _indexed_bundle(projection_root, entry)
            candidate = _load_credit_candidate(target, expected_digest)
            if candidate["manifest"].get("problemId") != problem:
                raise MathFlowError("published credit run belongs to another problem")
            _validate_candidate_history(candidate, canonical_transactions)
            candidates.append(candidate)
        except (MathFlowError, OSError, UnicodeError, json.JSONDecodeError) as exc:
            invalid.append(
                {
                    "runDigest": str(entry.get("runDigest", "unknown")),
                    "message": str(exc),
                }
            )

    result["verification"] = {
        "validPublishedRuns": len(candidates),
        "invalidPublishedRuns": invalid,
        "bundleValidation": "math_flow.credit.load_credit_assignment_bundle",
        "terminalSemantics": "verified-scheduled-predecessor-chain-or-unique-legacy-run",
    }
    applicable: list[dict[str, object]] = []
    if expected_lock is not None:
        applicable = [
            candidate
            for candidate in candidates
            if candidate["manifest"]["inputs"].get("projectionSpecDigest")
            == projection_digest
            and same_projection_dependency_state(
                candidate["dependencyLock"], expected_lock
            )
            and candidate["manifest"].get("problemLedgerDigest")
            == expected_lock["problemLedger"]["problemLedgerDigest"]
        ]

    chosen: dict[str, object] | None = None
    if applicable:
        governed_candidates = [
            {
                **candidate,
                "schedule": candidate["manifest"]["inputs"].get("schedule"),
            }
            for candidate in candidates
            if candidate["manifest"]["inputs"].get("projectionSpecDigest")
            == projection_digest
        ]
        try:
            ordered_governed = ordered_credit_runs(governed_candidates)
        except MathFlowError:
            ordered_governed = []
        terminal = ordered_governed[-1] if ordered_governed else None
        applicable_digests = {
            str(candidate["runDigest"]) for candidate in applicable
        }
        if terminal is not None and str(terminal["runDigest"]) in applicable_digests:
            chosen = terminal
            legacy_single = (
                len(ordered_governed) == 1
                and ordered_governed[0]["schedule"] is None
            )
            result.update(
                {
                    "status": "current",
                    "reasonCode": (
                        "unique-current-dependency-state-run"
                        if legacy_single
                        else "scheduled-chain-terminal-current"
                    ),
                    "message": (
                        "One verified run matches the governed projection and current dependency state."
                        if legacy_single
                        else "The latest run in one verified overlay predecessor chain matches the current governed dependency state."
                    ),
                }
            )
        else:
            result.update(
                {
                    "status": "ambiguous",
                    "reasonCode": "multiple-current-dependency-state-runs",
                    "message": "Current verified runs do not form one scheduled predecessor chain; no overlay terminal is selected.",
                    "applicableRunDigests": sorted(
                        str(item["runDigest"]) for item in applicable
                    ),
                }
            )
    else:
        canonical_ids = [
            str(item["transactionId"]) for item in canonical_transactions
        ]
        stale, stale_ambiguous = _select_stale_candidate(candidates, canonical_ids)
        if stale_ambiguous:
            result.update(
                {
                    "status": "ambiguous",
                    "reasonCode": "multiple-latest-stale-runs",
                    "message": "Multiple verified historical credit runs are equally recent; no overlay terminal selects one.",
                }
            )
        elif stale is not None:
            result.update(
                {
                    "status": "stale",
                    "reasonCode": "latest-verified-run-is-not-current",
                    "message": "The latest uniquely identifiable verified credit run does not match the current governed projection and dependency state.",
                }
            )
            chosen = stale
        elif invalid:
            result.update(
                {
                    "status": "invalid",
                    "reasonCode": "published-credit-run-invalid",
                    "message": "Published credit objects exist but none can be verified for this projection.",
                }
            )
        elif dependency_error is not None:
            dependency = result["dependency"]
            result.update(
                {
                    "status": dependency["status"],
                    "reasonCode": dependency["reasonCode"],
                    "message": "Credit cannot be formed until its knowledge dependency is available and current.",
                }
            )
        else:
            result.update(
                {
                    "status": "pending",
                    "reasonCode": "no-published-credit-run",
                    "message": "The governed credit projection has no published run for its current dependency state.",
                }
            )

    if chosen is None:
        return result, None
    result["run"] = {
        **_candidate_summary(chosen),
        "authoritative": result["status"] == "current",
        "selectionBasis": (
            "verified scheduled predecessor-chain terminal"
            if result.get("reasonCode") == "scheduled-chain-terminal-current"
            else "unique same governed projection and dependency state"
            if result["status"] == "current"
            else "unique latest verified historical ledger coverage"
        ),
        "reportFile": "credit-report.md",
    }
    result["assignments"] = _assignment_context(chosen)
    result["files"] = {
        "credit": "credit.json",
        "report": "credit-report.md",
    }
    return result, str(chosen["report"])
