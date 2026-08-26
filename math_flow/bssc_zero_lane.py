"""Inactive, provider-free readiness model for a zero-origin BSSC v6 lane."""

from __future__ import annotations

import copy
import json
from pathlib import Path
from typing import Mapping

from .artifacts import sha256_bytes
from .bssc_work_replay import (
    _load_v5_chain,
    build_bssc_work_replay_readiness_report,
    validate_bssc_replay_source,
)
from .counterfactual_context import (
    accepted_claim_refs_from_validity,
    manifest_submission_at,
)
from .errors import MathFlowError
from .governance import validate_projection_spec
from .repository import ledger, read_bytes_at, sha256_json
from .research_topology import empty_research_program_state_v2
from .work_accounting import (
    make_zero_work_accounting_state,
    validate_root_contract,
)
from .work_accounting_pipeline import AcceptedWorkSubmission
from .validity import validate_evidence_packet_v4


DIGEST_FIELDS = {
    "rootContractDigest",
    "knowledgeProjectionSpecDigest",
    "knowledgeStateDigest",
    "accountingStateDigest",
    "reportDigest",
}
REPORT_FIELDS = {
    "schemaVersion",
    "problemId",
    "status",
    "source",
    "knowledgeProjection",
    "rootContractDigest",
    "zeroOrigin",
    "canonicalSubmissionCount",
    "acceptedSubmissionCount",
    "excludedSubmissionCount",
    "subjects",
    "acceptedTransitionOrder",
    "providerRequirements",
    "invariants",
    "activationSeam",
    "reportDigest",
}
STATUS = "inactive-contract-review-and-provider-inputs-required"


def _content_digest(value: Mapping[str, object], field: str) -> str:
    return f"sha256:{sha256_json({key: item for key, item in value.items() if key != field})}"


def build_bssc_zero_lane_readiness_report(
    repository_root: Path,
    *,
    replay_source: object,
    knowledge_projection: object,
    root_contract: object,
) -> dict[str, object]:
    """Describe the exact K0/A0 -> x1 ... x16 execution still required.

    Historical v5 artifacts are consulted only to verify the canonical
    validity disposition of all 25 submissions.  Their knowledge states,
    batches, and topology are deliberately not reused by the new lane.
    """

    projection = validate_projection_spec(
        knowledge_projection,
        "openrouter-research-v4",
        lambda relative: (repository_root / relative).read_text(encoding="utf-8"),
    )
    if (
        projection.get("status") != "disabled"
        or projection.get("allowedProblems") != ["bssc-sum-capacity"]
        or projection.get("knowledgeBuilder")
        != "protocol/judges/openrouter-hierarchical-research-builder-v6.json"
    ):
        raise MathFlowError("BSSC zero lane requires the inactive BSSC builder-v6 projection")
    projection_digest = f"sha256:{sha256_json(projection)}"
    contract = validate_root_contract(root_contract, "bssc-sum-capacity")
    if (
        contract.get("knowledgeProjectionId") != projection["id"]
        or contract.get("knowledgeProjectionSpecDigest") != projection_digest
    ):
        raise MathFlowError("BSSC root contract does not bind the candidate knowledge projection")

    historical = build_bssc_work_replay_readiness_report(
        repository_root, replay_source
    )
    knowledge = empty_research_program_state_v2("bssc-sum-capacity")
    accounting = make_zero_work_accounting_state(
        root_contract=contract,
        knowledge_state=knowledge,
    )

    subjects: list[dict[str, object]] = []
    accepted_ids: list[str] = []
    accepted_ordinal = 0
    for old_subject in historical["subjects"]:
        accepted = old_subject["validityStatus"] == "accepted"
        if accepted:
            accepted_ordinal += 1
            accepted_ids.append(str(old_subject["transactionId"]))
        subjects.append(
            {
                "ledgerOrdinal": old_subject["ledgerOrdinal"],
                "transactionId": old_subject["transactionId"],
                "contributionId": old_subject["contributionId"],
                "validityStatus": old_subject["validityStatus"],
                "acceptedTransitionOrdinal": accepted_ordinal if accepted else None,
                "laneAction": (
                    "builder-v6-transition-and-work-evaluation"
                    if accepted
                    else "no-knowledge-or-accounting-transition"
                ),
            }
        )

    result: dict[str, object] = {
        "schemaVersion": 1,
        "problemId": "bssc-sum-capacity",
        "status": STATUS,
        "source": {
            "canonicalMainCommit": historical["source"]["mainCommit"],
            "problemLedgerDigest": historical["source"]["problemLedgerDigest"],
            "validityEvidenceProjectionCommit": historical["source"][
                "projectionCommit"
            ],
            "validityEvidenceTerminalRunDigest": historical["source"][
                "terminalRunDigest"
            ],
            "validityEvidenceOutputProfile": historical["source"]["outputProfile"],
            "historicalKnowledgeStatesReused": False,
        },
        "knowledgeProjection": {
            "id": projection["id"],
            "specDigest": projection_digest,
            "status": projection["status"],
            "knowledgeBuilder": projection["knowledgeBuilder"],
        },
        "rootContractDigest": contract["rootContractDigest"],
        "zeroOrigin": {
            "knowledgeStateDigest": knowledge["stateDigest"],
            "knowledgeLedgerHead": knowledge["ledgerHead"],
            "accountingStateDigest": accounting["stateDigest"],
            "processedSubmissionIds": accounting["processedSubmissionIds"],
            "totalWorkHours": accounting["totalWorkHours"],
            "meaning": (
                "Structural origin only; zero is not a provider estimate of remaining work."
            ),
        },
        "canonicalSubmissionCount": len(subjects),
        "acceptedSubmissionCount": len(accepted_ids),
        "excludedSubmissionCount": len(subjects) - len(accepted_ids),
        "subjects": subjects,
        "acceptedTransitionOrder": accepted_ids,
        "providerRequirements": [
            {
                "kind": "builder-v6-transition",
                "subjectTransactionIds": accepted_ids,
                "requiredCount": len(accepted_ids),
                "description": (
                    "Author and deterministically reduce one sequential builder-v6 "
                    "transition from the exact predecessor for every accepted submission."
                ),
            },
            {
                "kind": "same-world-work-evaluation",
                "subjectTransactionIds": accepted_ids,
                "requiredCount": len(accepted_ids),
                "stagesPerSubject": ["safe-facts", "no-access", "with-access"],
                "description": (
                    "Estimate one strictly positive same-world work reduction for every "
                    "accepted submission after its builder-v6 topology transition."
                ),
            },
        ],
        "invariants": {
            "zeroOriginVerified": True,
            "canonicalFirstParentOrderVerified": True,
            "oneKnowledgeTransitionPerAcceptedSubmission": True,
            "oneWorkEvaluationPerAcceptedSubmission": True,
            "excludedSubmissionsProduceNoTransition": True,
            "historicalV5KnowledgeStatesReused": False,
            "accountingNodeKinds": ["program", "thread"],
            "semanticLeafKinds": ["item"],
            "itemsExcludedFromNumericAccounting": True,
            "strictPositiveReductionVerified": False,
        },
        "activationSeam": (
            "After root-contract approval and separate governed projection admission, "
            "initialize K0 and A0, then process all 25 canonical submissions in order: "
            "each of the 16 accepted submissions gets one builder-v6 transition and one "
            "same-world work evaluation; each of the nine excluded submissions gets neither."
        ),
    }
    result["reportDigest"] = _content_digest(result, "reportDigest")
    return validate_bssc_zero_lane_readiness_report(result)


def _historical_judgment_artifact(
    root: Path,
    *,
    projection_commit: str,
    run_digest: str,
    role: str,
) -> object:
    hexadecimal = run_digest.removeprefix("sha256:")
    prefix = f"objects/judgment/{hexadecimal[:2]}/{hexadecimal}"
    raw_run = read_bytes_at(root, projection_commit, f"{prefix}/run.json")
    if sha256_bytes(raw_run) != run_digest:
        raise MathFlowError("historical validity run digest mismatch")
    try:
        run = json.loads(raw_run)
    except json.JSONDecodeError as exc:
        raise MathFlowError("historical validity run is invalid JSON") from exc
    artifacts = run.get("artifacts") if isinstance(run, dict) else None
    matches = (
        [item for item in artifacts if isinstance(item, dict) and item.get("role") == role]
        if isinstance(artifacts, list)
        else []
    )
    if (
        len(matches) != 1
        or run.get("outputProfile") != "math-flow/validity-judgment-v4"
        or run.get("problemId") != "bssc-sum-capacity"
    ):
        raise MathFlowError("historical validity artifact binding mismatch")
    relative = matches[0].get("path")
    if not isinstance(relative, str) or "/" in relative or relative in {"", ".", ".."}:
        raise MathFlowError("historical validity artifact path is unsafe")
    raw = read_bytes_at(root, projection_commit, f"{prefix}/{relative}")
    if sha256_bytes(raw) != matches[0].get("digest"):
        raise MathFlowError("historical validity artifact digest mismatch")
    try:
        return json.loads(raw)
    except json.JSONDecodeError as exc:
        raise MathFlowError("historical validity artifact is invalid JSON") from exc


def load_bssc_zero_lane_accepted_submissions(
    repository_root: Path,
    replay_source: object,
) -> list[AcceptedWorkSubmission]:
    """Materialize the exact 16 accepted BSSC inputs without reusing v5 state."""

    root = repository_root.resolve()
    pins = validate_bssc_replay_source(replay_source)
    canonical = ledger(root, "bssc-sum-capacity", str(pins["mainCommit"]))
    transaction_by_id = {
        str(item["transactionId"]): item for item in canonical["transactions"]
    }
    accepted_entries: dict[str, dict[str, object]] = {}
    for formation in _load_v5_chain(root, pins):
        for entry in formation["batch"]["judgments"]:
            if entry["acceptedClaimKeys"]:
                accepted_entries[str(entry["subjectTransactionId"])] = entry

    result: list[AcceptedWorkSubmission] = []
    projection_commit = str(pins["projectionCommit"])
    for transaction_id, transaction in transaction_by_id.items():
        entry = accepted_entries.get(transaction_id)
        if entry is None:
            continue
        run_digest = str(entry["runDigest"])
        judgment = _historical_judgment_artifact(
            root,
            projection_commit=projection_commit,
            run_digest=run_digest,
            role="judgment-record",
        )
        packet = _historical_judgment_artifact(
            root,
            projection_commit=projection_commit,
            run_digest=run_digest,
            role="judgment-dependency-packet",
        )
        validate_evidence_packet_v4(packet)
        if (
            not isinstance(judgment, dict)
            or judgment.get("schemaVersion") != 4
            or judgment.get("judgmentId") != entry["judgmentId"]
            or packet.get("subjectTransactionId") != transaction_id
        ):
            raise MathFlowError("historical accepted validity identity mismatch")
        claims_by_key = {
            str(item["claimKey"]): item
            for item in packet["claims"]
            if isinstance(item, dict) and isinstance(item.get("claimKey"), str)
        }
        valid_assessments = {
            str(item["claimKey"]): item
            for item in judgment.get("assessments", [])
            if isinstance(item, dict) and item.get("status") == "valid"
        }
        expected_keys = sorted(str(item) for item in entry["acceptedClaimKeys"])
        if sorted(valid_assessments) != expected_keys or not set(expected_keys) <= set(
            claims_by_key
        ):
            raise MathFlowError("historical accepted claim set mismatch")
        accepted_claims = [
            {
                "claimKey": claim_key,
                "statement": claims_by_key[claim_key]["statement"],
                "dependencyTransactionIds": sorted(
                    str(item)
                    for item in valid_assessments[claim_key][
                        "requiredDependencyTransactionIds"
                    ]
                ),
            }
            for claim_key in expected_keys
        ]
        evidence_manifest, evidence_chunks = manifest_submission_at(
            root,
            problem_id="bssc-sum-capacity",
            subject_transaction_id=transaction_id,
            contribution_path=str(transaction["path"]),
        )
        result.append(
            AcceptedWorkSubmission(
                transaction_id=transaction_id,
                ordinal=int(transaction["ordinal"]),
                accepted_claims=accepted_claims,
                judgment_id=str(entry["judgmentId"]),
                accepted_claim_refs=accepted_claim_refs_from_validity(
                    judgment, subject_transaction_id=transaction_id
                ),
                evidence_manifest=evidence_manifest,
                evidence_chunks=evidence_chunks,
            )
        )
    if len(result) != 16:
        raise MathFlowError("BSSC zero lane must materialize exactly 16 accepted inputs")
    accepted_ids = [item.transaction_id for item in result]
    for item in result:
        unavailable = {
            str(dependency)
            for claim in item.accepted_claims
            for dependency in claim["dependencyTransactionIds"]
            if dependency not in accepted_ids[: accepted_ids.index(item.transaction_id)]
        }
        if unavailable:
            raise MathFlowError(
                "BSSC accepted claim dependency is absent from its zero-lane predecessor"
            )
    return result


def validate_bssc_zero_lane_readiness_report(value: object) -> dict[str, object]:
    if not isinstance(value, dict) or set(value) != REPORT_FIELDS:
        raise MathFlowError("BSSC zero-lane readiness report has an invalid envelope")
    if (
        value.get("schemaVersion") != 1
        or value.get("problemId") != "bssc-sum-capacity"
        or value.get("status") != STATUS
    ):
        raise MathFlowError("BSSC zero-lane readiness report has an invalid identity")
    subjects = value.get("subjects")
    accepted_order = value.get("acceptedTransitionOrder")
    zero = value.get("zeroOrigin")
    source = value.get("source")
    projection = value.get("knowledgeProjection")
    invariants = value.get("invariants")
    requirements = value.get("providerRequirements")
    if not all(
        isinstance(item, expected)
        for item, expected in (
            (subjects, list),
            (accepted_order, list),
            (zero, dict),
            (source, dict),
            (projection, dict),
            (invariants, dict),
            (requirements, list),
        )
    ):
        raise MathFlowError("BSSC zero-lane readiness report has invalid collections")
    assert isinstance(subjects, list)
    assert isinstance(accepted_order, list)
    accepted = [
        item for item in subjects
        if isinstance(item, dict) and item.get("validityStatus") == "accepted"
    ]
    excluded = [
        item for item in subjects
        if isinstance(item, dict) and item.get("validityStatus") == "excluded"
    ]
    if (
        [item.get("ledgerOrdinal") for item in subjects if isinstance(item, dict)]
        != list(range(1, len(subjects) + 1))
        or [item.get("transactionId") for item in accepted] != accepted_order
        or [item.get("acceptedTransitionOrdinal") for item in accepted]
        != list(range(1, len(accepted) + 1))
        or any(item.get("acceptedTransitionOrdinal") is not None for item in excluded)
    ):
        raise MathFlowError("BSSC zero-lane subjects are not in canonical transition order")
    if (
        len(subjects) != value.get("canonicalSubmissionCount")
        or len(accepted) != value.get("acceptedSubmissionCount")
        or len(excluded) != value.get("excludedSubmissionCount")
        or len(accepted) != 16
        or len(excluded) != 9
    ):
        raise MathFlowError("BSSC zero-lane subject counts are inconsistent")
    if any(
        item.get("laneAction")
        != (
            "builder-v6-transition-and-work-evaluation"
            if item.get("validityStatus") == "accepted"
            else "no-knowledge-or-accounting-transition"
        )
        for item in subjects
        if isinstance(item, dict)
    ):
        raise MathFlowError("BSSC zero-lane subject action is inconsistent")
    assert isinstance(zero, dict)
    if (
        zero.get("knowledgeLedgerHead") is not None
        or zero.get("processedSubmissionIds") != []
        or zero.get("totalWorkHours") != "0"
    ):
        raise MathFlowError("BSSC zero-lane origin is not empty")
    assert isinstance(source, dict)
    assert isinstance(projection, dict)
    assert isinstance(invariants, dict)
    if (
        source.get("historicalKnowledgeStatesReused") is not False
        or projection.get("id") != "openrouter-research-v4"
        or projection.get("status") != "disabled"
        or invariants.get("historicalV5KnowledgeStatesReused") is not False
        or invariants.get("itemsExcludedFromNumericAccounting") is not True
        or invariants.get("strictPositiveReductionVerified") is not False
    ):
        raise MathFlowError("BSSC zero-lane invariants are unsafe")
    assert isinstance(requirements, list)
    if (
        len(requirements) != 2
        or any(item.get("subjectTransactionIds") != accepted_order for item in requirements)
        or any(item.get("requiredCount") != len(accepted_order) for item in requirements)
    ):
        raise MathFlowError("BSSC zero-lane provider requirements are incomplete")
    for digest in (
        value.get("rootContractDigest"),
        projection.get("specDigest"),
        zero.get("knowledgeStateDigest"),
        zero.get("accountingStateDigest"),
        value.get("reportDigest"),
    ):
        if (
            not isinstance(digest, str)
            or not digest.startswith("sha256:")
            or len(digest) != 71
        ):
            raise MathFlowError("BSSC zero-lane report contains an invalid digest")
    if value.get("reportDigest") != _content_digest(value, "reportDigest"):
        raise MathFlowError("BSSC zero-lane readiness report digest mismatch")
    return copy.deepcopy(value)
