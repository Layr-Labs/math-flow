from __future__ import annotations

import copy
import re
from collections.abc import Iterable

from .errors import MathFlowError
from .repository import sha256_json


IDENTIFIER = re.compile(r"^[a-z0-9][a-z0-9/_-]*$")
GIT_SHA = re.compile(r"^[0-9a-f]{40}$")
DIGEST = re.compile(r"^sha256:[0-9a-f]{64}$")

PROGRAM_STATUSES = {"active", "completed", "retired"}
RESULT_STATUSES = {"active", "superseded", "retired"}
LINEAGE_RELATIONS = {
    "split-from",
    "split-into",
    "merged-from",
    "merged-into",
}
STATE_FIELDS = {
    "schemaVersion",
    "problemId",
    "ledgerHead",
    "baseStateDigest",
    "rootProgramId",
    "programs",
    "intermediateResults",
    "contributions",
    "stateDigest",
}
PROGRAM_FIELDS = {
    "id",
    "parentId",
    "title",
    "objective",
    "currentStateSummary",
    "localResidualSummary",
    "status",
    "intermediateResultIds",
    "sourceTransactionIds",
    "lineage",
    "digest",
}
RESULT_FIELDS = {
    "id",
    "primaryProgramId",
    "relatedProgramIds",
    "title",
    "statement",
    "scopeQualifications",
    "support",
    "dependencyResultIds",
    "claimRefs",
    "sourceTransactionIds",
    "judgmentIds",
    "status",
    "supersededByResultIds",
    "digest",
}
SUPPORT_FIELDS = {
    "proofs",
    "methods",
    "computations",
    "tools",
    "artifactRefs",
    "attestationRefs",
}
CONTRIBUTION_FIELDS = {
    "id",
    "transactionId",
    "claimKeys",
    "directProgramIds",
    "intermediateResultIds",
    "dependencyTransactionIds",
    "judgmentId",
    "digest",
}
TRANSITION_FIELDS = {
    "schemaVersion",
    "subjectTransactionId",
    "baseStateDigest",
    "contentOperations",
    "topologyOperations",
    "contribution",
    "placementAudit",
    "topologyRationale",
}
CONTENT_OPERATION_FIELDS = {"entityKind", "entityId", "baseDigest", "value"}
TOPOLOGY_OPERATION_FIELDS = {
    "action",
    "entityKind",
    "entityId",
    "baseDigest",
    "value",
}
TRANSITION_CONTRIBUTION_FIELDS = {
    "claimKeys",
    "directProgramIds",
    "intermediateResultIds",
}
PLACEMENT_AUDIT_FIELDS = {"basis", "rationale", "relatedProgramIds"}
ALIGNMENT_FIELDS = {
    "schemaVersion",
    "problemId",
    "beforeKnowledgeStateDigest",
    "afterKnowledgeStateDigest",
    "preserved",
    "moved",
    "splits",
    "merges",
    "created",
    "retired",
    "alignmentDigest",
}
HANDOFF_FIELDS = {
    "schemaVersion",
    "problemId",
    "subjectTransactionId",
    "beforeKnowledgeStateDigest",
    "afterKnowledgeStateDigest",
    "topologyAlignmentDigest",
    "sameWorldReferenceStateDigest",
    "accountingNodeKinds",
    "semanticLeafKinds",
    "handoffDigest",
}
ENTITY_COLLECTIONS = {
    "program": "programs",
    "intermediateResult": "intermediateResults",
}


def _record_digest(record: dict[str, object]) -> str:
    value = {key: item for key, item in record.items() if key != "digest"}
    return f"sha256:{sha256_json(value)}"


def _with_record_digest(record: dict[str, object]) -> dict[str, object]:
    value = {
        key: copy.deepcopy(item) for key, item in record.items() if key != "digest"
    }
    return {**value, "digest": _record_digest(value)}


def _with_state_digest(state: dict[str, object]) -> dict[str, object]:
    value = {
        key: copy.deepcopy(item)
        for key, item in state.items()
        if key != "stateDigest"
    }
    return {**value, "stateDigest": f"sha256:{sha256_json(value)}"}


def _with_alignment_digest(alignment: dict[str, object]) -> dict[str, object]:
    value = {
        key: copy.deepcopy(item)
        for key, item in alignment.items()
        if key != "alignmentDigest"
    }
    return {**value, "alignmentDigest": f"sha256:{sha256_json(value)}"}


def _with_handoff_digest(handoff: dict[str, object]) -> dict[str, object]:
    value = {
        key: copy.deepcopy(item)
        for key, item in handoff.items()
        if key != "handoffDigest"
    }
    return {**value, "handoffDigest": f"sha256:{sha256_json(value)}"}


def _require_identifier(value: object, label: str) -> str:
    if not isinstance(value, str) or not IDENTIFIER.fullmatch(value):
        raise MathFlowError(f"{label} must be a stable lowercase path")
    return value


def _require_text(value: object, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise MathFlowError(f"{label} must be non-empty text")
    return value


def _require_unique_strings(
    value: object,
    label: str,
    *,
    pattern: re.Pattern[str] | None = None,
    nonempty: bool = True,
) -> list[str]:
    if not isinstance(value, list) or any(not isinstance(item, str) for item in value):
        raise MathFlowError(f"{label} must contain unique strings")
    result = [str(item) for item in value]
    if (nonempty and any(not item.strip() for item in result)) or len(result) != len(
        set(result)
    ):
        raise MathFlowError(f"{label} must contain unique non-empty strings")
    if pattern is not None and any(not pattern.fullmatch(item) for item in result):
        raise MathFlowError(f"{label} contains an invalid value")
    return result


def _canonical_strings(
    value: object,
    label: str,
    *,
    pattern: re.Pattern[str] | None = None,
    nonempty: bool = True,
) -> list[str]:
    return sorted(
        _require_unique_strings(
            value, label, pattern=pattern, nonempty=nonempty
        )
    )


def _canonical_lineage(value: object, program_id: str) -> list[dict[str, str]]:
    if not isinstance(value, list):
        raise MathFlowError(f"research program lineage must be an array: {program_id}")
    result: list[dict[str, str]] = []
    seen_targets: dict[str, str] = {}
    for raw_item in value:
        if (
            not isinstance(raw_item, dict)
            or set(raw_item) != {"relation", "programId"}
            or raw_item.get("relation") not in LINEAGE_RELATIONS
        ):
            raise MathFlowError(f"invalid research program lineage: {program_id}")
        target_id = _require_identifier(
            raw_item.get("programId"), "research program lineage target"
        )
        relation = str(raw_item["relation"])
        if target_id == program_id or target_id in seen_targets:
            raise MathFlowError(f"duplicate research program lineage: {program_id}")
        seen_targets[target_id] = relation
        result.append({"relation": relation, "programId": target_id})
    return sorted(result, key=lambda item: (item["relation"], item["programId"]))


def _canonical_claim_refs(value: object) -> list[dict[str, str]]:
    if not isinstance(value, list) or not value:
        raise MathFlowError("intermediate result claimRefs must be non-empty")
    result: list[dict[str, str]] = []
    seen: set[tuple[str, str]] = set()
    for raw_ref in value:
        if not isinstance(raw_ref, dict) or set(raw_ref) != {
            "transactionId",
            "claimKey",
        }:
            raise MathFlowError("intermediate result claim reference is invalid")
        transaction_id = raw_ref.get("transactionId")
        if not isinstance(transaction_id, str) or not GIT_SHA.fullmatch(transaction_id):
            raise MathFlowError("intermediate result claim reference transaction is invalid")
        claim_key = _require_identifier(
            raw_ref.get("claimKey"), "intermediate result claim key"
        )
        key = (transaction_id, claim_key)
        if key in seen:
            raise MathFlowError("intermediate result repeats a claim reference")
        seen.add(key)
        result.append({"transactionId": transaction_id, "claimKey": claim_key})
    return sorted(result, key=lambda item: (item["transactionId"], item["claimKey"]))


def _canonical_support(value: object) -> dict[str, object]:
    if not isinstance(value, dict) or set(value) != SUPPORT_FIELDS:
        raise MathFlowError("intermediate result support has invalid fields")
    artifact_refs = value.get("artifactRefs")
    if not isinstance(artifact_refs, list):
        raise MathFlowError("intermediate result artifactRefs must be an array")
    normalized_artifacts: list[dict[str, str]] = []
    seen_artifacts: set[tuple[str, str]] = set()
    for raw_ref in artifact_refs:
        if not isinstance(raw_ref, dict) or set(raw_ref) != {"path", "digest"}:
            raise MathFlowError("intermediate result artifact reference is invalid")
        path = raw_ref.get("path")
        digest = raw_ref.get("digest")
        if (
            not isinstance(path, str)
            or not path
            or path.startswith("/")
            or ".." in path.split("/")
            or not isinstance(digest, str)
            or not DIGEST.fullmatch(digest)
        ):
            raise MathFlowError("intermediate result artifact reference is unsafe")
        key = (path, digest)
        if key in seen_artifacts:
            raise MathFlowError("intermediate result repeats an artifact reference")
        seen_artifacts.add(key)
        normalized_artifacts.append({"path": path, "digest": digest})
    return {
        "proofs": _canonical_strings(value.get("proofs"), "support proofs"),
        "methods": _canonical_strings(value.get("methods"), "support methods"),
        "computations": _canonical_strings(
            value.get("computations"), "support computations"
        ),
        "tools": _canonical_strings(value.get("tools"), "support tools"),
        "artifactRefs": sorted(
            normalized_artifacts, key=lambda item: (item["path"], item["digest"])
        ),
        "attestationRefs": _canonical_strings(
            value.get("attestationRefs"),
            "support attestationRefs",
            pattern=DIGEST,
        ),
    }


def _normalize_program(entity_id: str, value: object) -> dict[str, object]:
    if not isinstance(value, dict) or set(value) != PROGRAM_FIELDS - {"digest"}:
        raise MathFlowError(f"research program v3 has invalid fields: {entity_id}")
    if value.get("id") != entity_id:
        raise MathFlowError(f"research program v3 ID mismatch: {entity_id}")
    _require_identifier(entity_id, "research program v3 ID")
    parent_id = value.get("parentId")
    if parent_id is not None:
        _require_identifier(parent_id, "research program v3 parent ID")
    status = value.get("status")
    if status not in PROGRAM_STATUSES:
        raise MathFlowError(f"research program v3 has invalid status: {entity_id}")
    normalized = {
        "id": entity_id,
        "parentId": parent_id,
        "title": _require_text(value.get("title"), "research program title"),
        "objective": _require_text(
            value.get("objective"), "research program objective"
        ),
        "currentStateSummary": _require_text(
            value.get("currentStateSummary"), "research program current state summary"
        ),
        "localResidualSummary": _require_text(
            value.get("localResidualSummary"),
            "research program local residual summary",
        ),
        "status": status,
        "intermediateResultIds": _canonical_strings(
            value.get("intermediateResultIds"),
            "program intermediateResultIds",
            pattern=IDENTIFIER,
        ),
        "sourceTransactionIds": _canonical_strings(
            value.get("sourceTransactionIds"),
            "program sourceTransactionIds",
            pattern=GIT_SHA,
        ),
        "lineage": _canonical_lineage(value.get("lineage"), entity_id),
    }
    return _with_record_digest(normalized)


def _normalize_result(entity_id: str, value: object) -> dict[str, object]:
    if not isinstance(value, dict) or set(value) != RESULT_FIELDS - {"digest"}:
        raise MathFlowError(f"intermediate result has invalid fields: {entity_id}")
    if value.get("id") != entity_id:
        raise MathFlowError(f"intermediate result ID mismatch: {entity_id}")
    _require_identifier(entity_id, "intermediate result ID")
    primary_program_id = _require_identifier(
        value.get("primaryProgramId"), "intermediate result primary program"
    )
    related_program_ids = _canonical_strings(
        value.get("relatedProgramIds"),
        "intermediate result relatedProgramIds",
        pattern=IDENTIFIER,
    )
    if primary_program_id in related_program_ids:
        raise MathFlowError(
            f"intermediate result repeats its primary program as related: {entity_id}"
        )
    dependency_ids = _canonical_strings(
        value.get("dependencyResultIds"),
        "intermediate result dependencyResultIds",
        pattern=IDENTIFIER,
    )
    superseded_by = _canonical_strings(
        value.get("supersededByResultIds"),
        "intermediate result supersededByResultIds",
        pattern=IDENTIFIER,
    )
    if entity_id in set(dependency_ids) | set(superseded_by):
        raise MathFlowError(f"intermediate result may not reference itself: {entity_id}")
    status = value.get("status")
    if status not in RESULT_STATUSES:
        raise MathFlowError(f"intermediate result has invalid status: {entity_id}")
    if (status == "active" and superseded_by) or (
        status == "superseded" and not superseded_by
    ):
        raise MathFlowError(
            f"intermediate result supersession status and successors disagree: {entity_id}"
        )
    normalized = {
        "id": entity_id,
        "primaryProgramId": primary_program_id,
        "relatedProgramIds": related_program_ids,
        "title": _require_text(value.get("title"), "intermediate result title"),
        "statement": _require_text(
            value.get("statement"), "intermediate result statement"
        ),
        "scopeQualifications": _canonical_strings(
            value.get("scopeQualifications"),
            "intermediate result scopeQualifications",
        ),
        "support": _canonical_support(value.get("support")),
        "dependencyResultIds": dependency_ids,
        "claimRefs": _canonical_claim_refs(value.get("claimRefs")),
        "sourceTransactionIds": _canonical_strings(
            value.get("sourceTransactionIds"),
            "intermediate result sourceTransactionIds",
            pattern=GIT_SHA,
        ),
        "judgmentIds": _canonical_strings(
            value.get("judgmentIds"),
            "intermediate result judgmentIds",
            pattern=DIGEST,
        ),
        "status": status,
        "supersededByResultIds": superseded_by,
    }
    if not normalized["sourceTransactionIds"] or not normalized["judgmentIds"]:
        raise MathFlowError(
            f"intermediate result needs source and judgment provenance: {entity_id}"
        )
    return _with_record_digest(normalized)


def _normalize_contribution(entity_id: str, value: object) -> dict[str, object]:
    if not isinstance(value, dict) or set(value) != CONTRIBUTION_FIELDS - {"digest"}:
        raise MathFlowError(f"research contribution v3 has invalid fields: {entity_id}")
    if (
        value.get("id") != entity_id
        or value.get("transactionId") != entity_id
        or not GIT_SHA.fullmatch(entity_id)
    ):
        raise MathFlowError(f"research contribution v3 ID mismatch: {entity_id}")
    judgment_id = value.get("judgmentId")
    if not isinstance(judgment_id, str) or not DIGEST.fullmatch(judgment_id):
        raise MathFlowError(f"research contribution v3 judgment is invalid: {entity_id}")
    normalized = {
        "id": entity_id,
        "transactionId": entity_id,
        "claimKeys": _canonical_strings(
            value.get("claimKeys"), "contribution claimKeys", pattern=IDENTIFIER
        ),
        "directProgramIds": _canonical_strings(
            value.get("directProgramIds"),
            "contribution directProgramIds",
            pattern=IDENTIFIER,
        ),
        "intermediateResultIds": _canonical_strings(
            value.get("intermediateResultIds"),
            "contribution intermediateResultIds",
            pattern=IDENTIFIER,
        ),
        "dependencyTransactionIds": _canonical_strings(
            value.get("dependencyTransactionIds"),
            "contribution dependencyTransactionIds",
            pattern=GIT_SHA,
        ),
        "judgmentId": judgment_id,
    }
    if any(not normalized[field] for field in ("claimKeys", "directProgramIds", "intermediateResultIds")):
        raise MathFlowError(f"research contribution v3 has an empty required mapping: {entity_id}")
    if entity_id in normalized["dependencyTransactionIds"]:
        raise MathFlowError("research contribution may not depend on itself")
    return _with_record_digest(normalized)


def empty_research_program_state_v3(problem: str) -> dict[str, object]:
    _require_identifier(problem, "research program v3 problem ID")
    root = _normalize_program(
        "root",
        {
            "id": "root",
            "parentId": None,
            "title": "Canonical problem",
            "objective": "Resolve the canonical problem.",
            "currentStateSummary": "No accepted intermediate results yet.",
            "localResidualSummary": (
                "All unresolved work remains local until it is organized into child programs."
            ),
            "status": "active",
            "intermediateResultIds": [],
            "sourceTransactionIds": [],
            "lineage": [],
        },
    )
    return _with_state_digest(
        {
            "schemaVersion": 3,
            "problemId": problem,
            "ledgerHead": None,
            "baseStateDigest": None,
            "rootProgramId": "root",
            "programs": {"root": root},
            "intermediateResults": {},
            "contributions": {},
        }
    )


def _lineage_ids(program: dict[str, object], relation: str) -> set[str]:
    return {
        str(item["programId"])
        for item in program.get("lineage", [])
        if isinstance(item, dict) and item.get("relation") == relation
    }


def _validate_lineage_graph(programs: dict[str, object]) -> None:
    inverse = {
        "split-from": "split-into",
        "split-into": "split-from",
        "merged-from": "merged-into",
        "merged-into": "merged-from",
    }
    successors: dict[str, set[str]] = {str(program_id): set() for program_id in programs}
    for program_id, raw_program in programs.items():
        assert isinstance(raw_program, dict)
        counts = {
            relation: sum(
                item.get("relation") == relation
                for item in raw_program.get("lineage", [])
            )
            for relation in LINEAGE_RELATIONS
        }
        if counts["split-from"] > 1 or counts["merged-into"] > 1:
            raise MathFlowError(f"research program lineage cardinality is invalid: {program_id}")
        if counts["split-into"] == 1 or counts["merged-from"] == 1:
            raise MathFlowError(f"research program lineage event is incomplete: {program_id}")
        if counts["split-into"] and counts["merged-into"]:
            raise MathFlowError(f"research program has conflicting successor lineage: {program_id}")
        if counts["split-from"] and counts["merged-from"]:
            raise MathFlowError(f"research program has conflicting predecessor lineage: {program_id}")
        if (counts["split-into"] or counts["merged-into"]) and raw_program.get("status") != "retired":
            raise MathFlowError(f"research program lineage predecessor must be retired: {program_id}")
        for item in raw_program.get("lineage", []):
            target_id = str(item["programId"])
            target = programs.get(target_id)
            reciprocal = {"relation": inverse[str(item["relation"])], "programId": str(program_id)}
            if not isinstance(target, dict) or reciprocal not in target.get("lineage", []):
                raise MathFlowError(f"research program lineage is not reciprocal: {program_id}")
            if item["relation"] in {"split-into", "merged-into"}:
                successors[str(program_id)].add(target_id)

    visiting: set[str] = set()
    visited: set[str] = set()

    def visit(program_id: str) -> None:
        if program_id in visited:
            return
        if program_id in visiting:
            raise MathFlowError(f"research program lineage contains a cycle: {program_id}")
        visiting.add(program_id)
        for successor_id in sorted(successors[program_id]):
            visit(successor_id)
        visiting.remove(program_id)
        visited.add(program_id)

    for program_id in sorted(programs):
        visit(str(program_id))


def validate_research_program_state_v3(
    value: object, problem: str | None = None
) -> dict[str, object]:
    if not isinstance(value, dict) or set(value) != STATE_FIELDS:
        raise MathFlowError("research program state v3 has an invalid envelope")
    if value.get("schemaVersion") != 3:
        raise MathFlowError("research program state v3 has an unsupported version")
    problem_id = _require_identifier(value.get("problemId"), "research program v3 problem ID")
    if problem is not None and problem_id != problem:
        raise MathFlowError("research program state v3 belongs to another problem")
    ledger_head = value.get("ledgerHead")
    if ledger_head is not None and (
        not isinstance(ledger_head, str) or not GIT_SHA.fullmatch(ledger_head)
    ):
        raise MathFlowError("research program state v3 has an invalid ledger head")
    base_digest = value.get("baseStateDigest")
    if base_digest is not None and (
        not isinstance(base_digest, str) or not DIGEST.fullmatch(base_digest)
    ):
        raise MathFlowError("research program state v3 has an invalid base digest")
    if value.get("rootProgramId") != "root":
        raise MathFlowError("research program state v3 must use root program 'root'")
    programs = value.get("programs")
    results = value.get("intermediateResults")
    contributions = value.get("contributions")
    if any(not isinstance(collection, dict) for collection in (programs, results, contributions)):
        raise MathFlowError("research program state v3 collections must be objects")
    assert isinstance(programs, dict)
    assert isinstance(results, dict)
    assert isinstance(contributions, dict)
    if "root" not in programs:
        raise MathFlowError("research program state v3 is missing its root program")
    for program_id, record in programs.items():
        if not isinstance(record, dict) or record != _normalize_program(str(program_id), {k: copy.deepcopy(v) for k, v in record.items() if k != "digest"}):
            raise MathFlowError(f"research program v3 is not canonical: {program_id}")
    for result_id, record in results.items():
        if not isinstance(record, dict) or record != _normalize_result(str(result_id), {k: copy.deepcopy(v) for k, v in record.items() if k != "digest"}):
            raise MathFlowError(f"intermediate result is not canonical: {result_id}")
    for contribution_id, record in contributions.items():
        if not isinstance(record, dict) or record != _normalize_contribution(str(contribution_id), {k: copy.deepcopy(v) for k, v in record.items() if k != "digest"}):
            raise MathFlowError(f"research contribution v3 is not canonical: {contribution_id}")

    root = programs["root"]
    if root.get("parentId") is not None or root.get("status") != "active" or root.get("lineage") != []:
        raise MathFlowError("research program state v3 root must be active and lineage-free")
    for program_id, record in programs.items():
        parent_id = record.get("parentId")
        if program_id != "root" and parent_id not in programs:
            raise MathFlowError(f"research program v3 has missing parent: {program_id}")
        observed: set[str] = set()
        cursor: str | None = str(program_id)
        while cursor is not None:
            if cursor in observed:
                raise MathFlowError(f"research program v3 hierarchy contains a cycle: {program_id}")
            observed.add(cursor)
            parent = programs[cursor].get("parentId")
            cursor = str(parent) if isinstance(parent, str) else None
        if record.get("status") != "retired":
            cursor_value = parent_id
            while isinstance(cursor_value, str):
                ancestor = programs[cursor_value]
                if ancestor.get("status") == "retired":
                    raise MathFlowError(f"live research program has a retired ancestor: {program_id}")
                cursor_value = ancestor.get("parentId")

    expected_program_results: dict[str, set[str]] = {
        str(program_id): set() for program_id in programs
    }
    for result_id, record in results.items():
        linked_program_ids = [str(record["primaryProgramId"]), *map(str, record["relatedProgramIds"])]
        for program_id in linked_program_ids:
            program_record = programs.get(program_id)
            if not isinstance(program_record, dict):
                raise MathFlowError(f"intermediate result has missing program: {result_id}")
            if record.get("status") != "retired" and program_record.get("status") == "retired":
                raise MathFlowError(f"live intermediate result remains in a retired program: {result_id}")
            expected_program_results[program_id].add(str(result_id))
        for dependency_id in record.get("dependencyResultIds", []):
            if dependency_id not in results:
                raise MathFlowError(f"intermediate result has missing dependency: {result_id}")
        for successor_id in record.get("supersededByResultIds", []):
            successor = results.get(successor_id)
            if not isinstance(successor, dict) or successor.get("status") != "active":
                raise MathFlowError(f"intermediate result has invalid supersession target: {result_id}")
        expected_judgments: set[str] = set()
        for reference in record.get("claimRefs", []):
            contribution = contributions.get(reference.get("transactionId"))
            if not isinstance(contribution, dict) or reference.get("claimKey") not in contribution.get("claimKeys", []):
                raise MathFlowError(f"intermediate result references an unaccepted claim: {result_id}")
            expected_judgments.add(str(contribution["judgmentId"]))
        for transaction_id in record.get("sourceTransactionIds", []):
            contribution = contributions.get(transaction_id)
            if not isinstance(contribution, dict):
                raise MathFlowError(f"intermediate result cites an unaccepted source: {result_id}")
            expected_judgments.add(str(contribution["judgmentId"]))
        if set(record.get("judgmentIds", [])) != expected_judgments:
            raise MathFlowError(f"intermediate result judgment provenance is incomplete: {result_id}")

    for program_id, record in programs.items():
        if set(record.get("intermediateResultIds", [])) != expected_program_results[str(program_id)]:
            raise MathFlowError(f"research program result links are not reciprocal: {program_id}")
        if not set(record.get("sourceTransactionIds", [])) <= set(contributions):
            raise MathFlowError(f"research program cites an unaccepted source: {program_id}")

    visiting_results: set[str] = set()
    visited_results: set[str] = set()

    def visit_result(result_id: str) -> None:
        if result_id in visited_results:
            return
        if result_id in visiting_results:
            raise MathFlowError(f"intermediate result dependency graph contains a cycle: {result_id}")
        visiting_results.add(result_id)
        for dependency_id in results[result_id]["dependencyResultIds"]:
            visit_result(str(dependency_id))
        visiting_results.remove(result_id)
        visited_results.add(result_id)

    for result_id in results:
        visit_result(str(result_id))

    for contribution_id, record in contributions.items():
        if any(program_id not in programs for program_id in record.get("directProgramIds", [])):
            raise MathFlowError(f"research contribution has missing historical program: {contribution_id}")
        if any(result_id not in results for result_id in record.get("intermediateResultIds", [])):
            raise MathFlowError(f"research contribution has missing intermediate result: {contribution_id}")
        if any(dependency_id not in contributions for dependency_id in record.get("dependencyTransactionIds", [])):
            raise MathFlowError(f"research contribution has missing dependency: {contribution_id}")
        represented = {
            str(reference["claimKey"])
            for result_id in record["intermediateResultIds"]
            for reference in results[result_id]["claimRefs"]
            if reference["transactionId"] == contribution_id
        }
        if represented != set(record.get("claimKeys", [])):
            raise MathFlowError(f"research contribution claim coverage is incomplete: {contribution_id}")
        for result_id in record["intermediateResultIds"]:
            result = results[result_id]
            if contribution_id not in result.get("sourceTransactionIds", []) or record.get("judgmentId") not in result.get("judgmentIds", []):
                raise MathFlowError(f"research contribution result provenance is incomplete: {contribution_id}")

    _validate_lineage_graph(programs)
    if value.get("stateDigest") != _with_state_digest(value)["stateDigest"]:
        raise MathFlowError("research program state v3 digest mismatch")
    return value


def _accepted_claims(value: object, subject_transaction_id: str) -> dict[str, dict[str, object]]:
    if not isinstance(value, list) or not value:
        raise MathFlowError("research builder v7 needs at least one accepted claim")
    result: dict[str, dict[str, object]] = {}
    for claim in value:
        if not isinstance(claim, dict):
            raise MathFlowError("research builder v7 accepted claim must be an object")
        claim_key = _require_identifier(claim.get("claimKey"), "research builder v7 accepted claim key")
        if claim_key in result:
            raise MathFlowError("research builder v7 repeats an accepted claim key")
        dependencies = _require_unique_strings(
            claim.get("dependencyTransactionIds"),
            "research builder v7 accepted claim dependencies",
            pattern=GIT_SHA,
        )
        if subject_transaction_id in dependencies:
            raise MathFlowError("research builder v7 accepted claim may not depend on itself")
        result[claim_key] = claim
    return result


def _changed_fields(before: dict[str, object], after: dict[str, object]) -> set[str]:
    return {
        field
        for field in set(before) | set(after)
        if field != "digest" and before.get(field) != after.get(field)
    }


def _normalize_entity_value(kind: str, entity_id: str, value: object) -> dict[str, object]:
    if kind == "program":
        return _normalize_program(entity_id, value)
    if kind == "intermediateResult":
        return _normalize_result(entity_id, value)
    raise MathFlowError("research builder v7 operation has an invalid entity kind")


def _is_descendant(state: dict[str, object], candidate_id: str, ancestor_id: str) -> bool:
    programs = state["programs"]
    assert isinstance(programs, dict)
    cursor: str | None = candidate_id
    while cursor is not None:
        if cursor == ancestor_id:
            return True
        parent_id = programs[cursor].get("parentId")
        cursor = str(parent_id) if isinstance(parent_id, str) else None
    return False


def _validate_placement_audit(state: dict[str, object], transition: dict[str, object]) -> None:
    audit = transition.get("placementAudit")
    if not isinstance(audit, dict) or set(audit) != PLACEMENT_AUDIT_FIELDS:
        raise MathFlowError("research builder v7 placement audit has invalid fields")
    basis = audit.get("basis")
    if basis not in {"local-objective", "cross-program", "canonical-objective"}:
        raise MathFlowError("research builder v7 placement basis is invalid")
    _require_text(audit.get("rationale"), "research builder v7 placement rationale")
    related = _canonical_strings(
        audit.get("relatedProgramIds"), "research builder v7 related program IDs", pattern=IDENTIFIER
    )
    subject = str(transition["subjectTransactionId"])
    contribution = state["contributions"][subject]
    direct = list(contribution["directProgramIds"])
    programs = state["programs"]
    assert isinstance(programs, dict)
    if len(state["contributions"]) >= 2 and all(
        record.get("directProgramIds") == ["root"]
        for record in state["contributions"].values()
    ):
        raise MathFlowError("hierarchical research v7 multi-submission state may not remain root-only")
    if basis == "canonical-objective":
        if direct != ["root"] or related:
            raise MathFlowError("research builder v7 canonical placement must be root-only")
        return
    if basis == "local-objective":
        if len(direct) != 1 or direct[0] == "root" or related != direct:
            raise MathFlowError("research builder v7 local placement must name one non-root program")
        program = programs.get(direct[0])
        if not isinstance(program, dict) or program.get("status") != "active":
            raise MathFlowError("research builder v7 local placement program is not active")
        return
    if related != direct or len(direct) < 2 or "root" in direct:
        raise MathFlowError("research builder v7 cross-program placement needs two local programs")
    for program_id in direct:
        program = programs.get(program_id)
        if not isinstance(program, dict) or program.get("status") != "active":
            raise MathFlowError("research builder v7 cross-program placement names an invalid program")
    for index, left_id in enumerate(direct):
        for right_id in direct[index + 1 :]:
            if _is_descendant(state, left_id, right_id) or _is_descendant(state, right_id, left_id):
                raise MathFlowError("research builder v7 cross-program placement requires incomparable programs")


def _validate_new_lineage_transition(
    base_state: dict[str, object], post_state: dict[str, object]
) -> None:
    base_programs = base_state["programs"]
    post_programs = post_state["programs"]
    assert isinstance(base_programs, dict)
    assert isinstance(post_programs, dict)
    for program_id, post_program in post_programs.items():
        assert isinstance(post_program, dict)
        base_program = base_programs.get(program_id)
        if base_program is not None:
            assert isinstance(base_program, dict)
        for relation in LINEAGE_RELATIONS:
            prior = _lineage_ids(base_program, relation) if isinstance(base_program, dict) else set()
            current = _lineage_ids(post_program, relation)
            if not prior <= current:
                raise MathFlowError(f"research program lineage is append-only: {program_id}")
            if current - prior and prior:
                raise MathFlowError(f"research program lineage event must be atomic: {program_id}")
        new_split_successors = _lineage_ids(post_program, "split-into") - (
            _lineage_ids(base_program, "split-into") if isinstance(base_program, dict) else set()
        )
        if new_split_successors:
            former_parent = base_program.get("parentId") if isinstance(base_program, dict) else post_program.get("parentId")
            if post_program.get("status") != "retired" or any(
                not isinstance(post_programs.get(successor_id), dict)
                or post_programs[successor_id].get("status") != "active"
                or post_programs[successor_id].get("parentId") != former_parent
                for successor_id in new_split_successors
            ):
                raise MathFlowError(f"new research program split needs active sibling successors: {program_id}")
        new_merge_predecessors = _lineage_ids(post_program, "merged-from") - (
            _lineage_ids(base_program, "merged-from") if isinstance(base_program, dict) else set()
        )
        if new_merge_predecessors and (
            post_program.get("status") != "active"
            or any(
                not isinstance(post_programs.get(predecessor_id), dict)
                or post_programs[predecessor_id].get("status") != "retired"
                for predecessor_id in new_merge_predecessors
            )
        ):
            raise MathFlowError(f"new research program merge needs retired predecessors and an active successor: {program_id}")


def _apply_transition_operations(
    base_state: dict[str, object],
    transition: dict[str, object],
    *,
    accepted_claims: object,
    judgment_id: str,
) -> dict[str, object]:
    subject = str(transition["subjectTransactionId"])
    claims = _accepted_claims(accepted_claims, subject)
    if not DIGEST.fullmatch(judgment_id):
        raise MathFlowError("research builder v7 needs an exact judgment digest")
    content_operations = transition.get("contentOperations")
    topology_operations = transition.get("topologyOperations")
    contribution_value = transition.get("contribution")
    if not isinstance(content_operations, list) or not isinstance(topology_operations, list):
        raise MathFlowError("research builder v7 operations must be arrays")
    if not isinstance(contribution_value, dict) or set(contribution_value) != TRANSITION_CONTRIBUTION_FIELDS:
        raise MathFlowError("research builder v7 contribution has invalid fields")

    result = copy.deepcopy(base_state)
    result.pop("stateDigest", None)
    collections = {
        kind: result[collection_name]
        for kind, collection_name in ENTITY_COLLECTIONS.items()
    }
    contributions = result["contributions"]
    assert isinstance(contributions, dict)
    if subject in contributions:
        raise MathFlowError("research builder v7 state already contains the accepted submission")
    allowed_sources = set(contributions) | {subject}
    seen: set[tuple[str, str]] = set()

    def apply_operation(operation: object, *, topology: bool) -> None:
        expected_fields = TOPOLOGY_OPERATION_FIELDS if topology else CONTENT_OPERATION_FIELDS
        if not isinstance(operation, dict) or set(operation) != expected_fields:
            raise MathFlowError("research builder v7 operation has invalid fields")
        action = operation.get("action") if topology else "content"
        if topology and action not in {"create", "move", "retire"}:
            raise MathFlowError("research builder v7 topology action is invalid")
        kind = operation.get("entityKind")
        if kind not in collections:
            raise MathFlowError("research builder v7 operation has an invalid entity kind")
        entity_id = _require_identifier(operation.get("entityId"), "research builder v7 entity ID")
        key = (str(kind), entity_id)
        if key in seen:
            raise MathFlowError("research builder v7 transition repeats an entity")
        seen.add(key)
        collection = collections[str(kind)]
        assert isinstance(collection, dict)
        existing = collection.get(entity_id)
        base_digest = operation.get("baseDigest")
        creating = existing is None
        if action == "create" and not creating:
            raise MathFlowError("research builder v7 topology create requires a new ID")
        if creating:
            if action not in {"content", "create"} or base_digest is not None:
                raise MathFlowError("new research builder v7 entity must use null baseDigest")
        elif action == "create" or not isinstance(existing, dict) or base_digest != existing.get("digest"):
            expected = existing.get("digest") if isinstance(existing, dict) else None
            raise MathFlowError(f"research builder v7 operation baseDigest mismatch: {kind} {entity_id} expected {expected}")
        normalized = _normalize_entity_value(str(kind), entity_id, operation.get("value"))
        sources = set(normalized.get("sourceTransactionIds", []))
        if not sources <= allowed_sources or (
            (not topology or creating) and subject not in sources
        ):
            raise MathFlowError(
                "research builder v7 content and created entities must cite only "
                "accepted sources including their submission"
            )

        if creating:
            if normalized.get("status") != "active":
                raise MathFlowError("research builder v7 may create only active entities")
            if not topology and kind == "program" and normalized.get("lineage"):
                raise MathFlowError("research builder v7 content creation may not invent lineage")
        else:
            assert isinstance(existing, dict)
            if not set(existing.get("sourceTransactionIds", [])) <= sources:
                raise MathFlowError("research builder v7 provenance is additive")
            if action == "content":
                immutable = {
                    "program": {"parentId", "lineage"},
                    "intermediateResult": {"primaryProgramId", "relatedProgramIds"},
                }[str(kind)]
                if _changed_fields(existing, normalized) & immutable:
                    raise MathFlowError("research builder v7 content operation hides a topology change")
                if kind == "program" and existing.get("status") != "retired" and normalized.get("status") == "retired":
                    raise MathFlowError("research builder v7 program retirement needs a topology operation")
                if existing.get("status") == "retired" and normalized.get("status") != "retired":
                    raise MathFlowError("research builder v7 may not revive a retired entity")
                if kind == "intermediateResult":
                    for field in (
                        "dependencyResultIds",
                        "claimRefs",
                        "judgmentIds",
                        "supersededByResultIds",
                    ):
                        prior = {
                            tuple(sorted(item.items())) if isinstance(item, dict) else str(item)
                            for item in existing.get(field, [])
                        }
                        current = {
                            tuple(sorted(item.items())) if isinstance(item, dict) else str(item)
                            for item in normalized.get(field, [])
                        }
                        if not prior <= current:
                            raise MathFlowError("research builder v7 result evidence and dependencies are additive")
            elif action == "move":
                if entity_id == "root":
                    raise MathFlowError("research builder v7 may not move the root program")
                allowed = {
                    "program": {"parentId", "lineage"},
                    "intermediateResult": {"primaryProgramId", "relatedProgramIds"},
                }[str(kind)]
                changed = _changed_fields(existing, normalized)
                if not changed or not changed <= allowed:
                    raise MathFlowError("research builder v7 move must preserve content, lifecycle, and provenance")
                if existing.get("status") != "active":
                    raise MathFlowError("research builder v7 may move only an active entity")
            elif action == "retire":
                if entity_id == "root" or existing.get("status") == "retired" or normalized.get("status") != "retired":
                    raise MathFlowError("research builder v7 retirement is invalid")
                allowed = {"status", "lineage"} if kind == "program" else {"status"}
                if not _changed_fields(existing, normalized) <= allowed:
                    raise MathFlowError("research builder v7 retirement must preserve content, placement, and provenance")
        collection[entity_id] = normalized

    for operation in content_operations:
        apply_operation(operation, topology=False)
    for operation in topology_operations:
        apply_operation(operation, topology=True)

    claim_keys = _canonical_strings(
        contribution_value.get("claimKeys"), "research builder v7 contribution claim keys", pattern=IDENTIFIER
    )
    if set(claim_keys) != set(claims):
        raise MathFlowError("research builder v7 contribution must cover every accepted claim exactly once")
    direct_program_ids = _canonical_strings(
        contribution_value.get("directProgramIds"), "research builder v7 direct program IDs", pattern=IDENTIFIER
    )
    result_ids = _canonical_strings(
        contribution_value.get("intermediateResultIds"), "research builder v7 result IDs", pattern=IDENTIFIER
    )
    if not direct_program_ids or not result_ids:
        raise MathFlowError("research builder v7 contribution needs a program and intermediate result")
    dependency_ids = sorted(
        {
            str(dependency)
            for claim_key in claim_keys
            for dependency in claims[claim_key]["dependencyTransactionIds"]
        }
    )
    if not set(dependency_ids) <= set(contributions):
        missing = sorted(set(dependency_ids) - set(contributions))[0]
        raise MathFlowError(f"research builder v7 accepted dependency is absent from prior state: {missing}")
    contributions[subject] = _normalize_contribution(
        subject,
        {
            "id": subject,
            "transactionId": subject,
            "claimKeys": claim_keys,
            "directProgramIds": direct_program_ids,
            "intermediateResultIds": result_ids,
            "dependencyTransactionIds": dependency_ids,
            "judgmentId": judgment_id,
        },
    )
    if any(result_id not in collections["intermediateResult"] for result_id in result_ids):
        raise MathFlowError(
            "research builder v7 contribution names a missing intermediate result"
        )
    mapped_program_ids = {
        str(program_id)
        for result_id in result_ids
        for program_id in [
            collections["intermediateResult"][result_id]["primaryProgramId"],
            *collections["intermediateResult"][result_id]["relatedProgramIds"],
        ]
    }
    if set(direct_program_ids) != mapped_program_ids:
        raise MathFlowError(
            "research builder v7 contribution direct programs must exactly match "
            "its intermediate-result program links"
        )
    result["ledgerHead"] = subject
    result["baseStateDigest"] = base_state["stateDigest"]
    post_state = _with_state_digest(result)
    validate_research_program_state_v3(post_state, str(base_state["problemId"]))
    _validate_placement_audit(post_state, transition)
    _validate_new_lineage_transition(base_state, post_state)
    return post_state


def _identity_entry(
    kind: str,
    entity_id: str,
    before: dict[str, object] | None,
    after: dict[str, object] | None,
) -> dict[str, object]:
    entry: dict[str, object] = {"entityKind": kind, "entityId": entity_id}
    if before is not None:
        entry["beforeDigest"] = before["digest"]
    if after is not None:
        entry["afterDigest"] = after["digest"]
    return entry


def _entity_program_ids(kind: str, record: dict[str, object]) -> list[str]:
    if kind == "program":
        parent_id = record.get("parentId")
        return [str(parent_id)] if isinstance(parent_id, str) else []
    return sorted(
        [str(record["primaryProgramId"]), *map(str, record.get("relatedProgramIds", []))]
    )


def _sorted_identity_entries(entries: Iterable[dict[str, object]]) -> list[dict[str, object]]:
    return sorted(entries, key=lambda item: (str(item["entityKind"]), str(item["entityId"])))


def derive_research_topology_alignment_v2(
    before_state: dict[str, object], after_state: dict[str, object]
) -> dict[str, object]:
    validate_research_program_state_v3(before_state)
    validate_research_program_state_v3(after_state)
    if before_state.get("problemId") != after_state.get("problemId"):
        raise MathFlowError("research topology alignment crosses problems")
    if after_state.get("baseStateDigest") != before_state.get("stateDigest"):
        raise MathFlowError("research topology alignment states are not adjacent")
    preserved: list[dict[str, object]] = []
    moved: list[dict[str, object]] = []
    created: list[dict[str, object]] = []
    retired: list[dict[str, object]] = []
    for kind, collection_name in ENTITY_COLLECTIONS.items():
        before_collection = before_state[collection_name]
        after_collection = after_state[collection_name]
        assert isinstance(before_collection, dict)
        assert isinstance(after_collection, dict)
        missing = set(before_collection) - set(after_collection)
        if missing:
            raise MathFlowError(f"research topology alignment removes an entity: {sorted(missing)[0]}")
        for entity_id in sorted(after_collection):
            before = before_collection.get(entity_id)
            after = after_collection[entity_id]
            assert isinstance(after, dict)
            if not isinstance(before, dict):
                created.append(_identity_entry(kind, str(entity_id), None, after))
            elif before.get("status") != "retired" and after.get("status") == "retired":
                retired.append(_identity_entry(kind, str(entity_id), before, after))
            elif _entity_program_ids(kind, before) != _entity_program_ids(kind, after):
                entry = _identity_entry(kind, str(entity_id), before, after)
                entry.update(
                    {
                        "fromProgramIds": _entity_program_ids(kind, before),
                        "toProgramIds": _entity_program_ids(kind, after),
                    }
                )
                moved.append(entry)
            else:
                preserved.append(_identity_entry(kind, str(entity_id), before, after))
    before_programs = before_state["programs"]
    after_programs = after_state["programs"]
    assert isinstance(before_programs, dict)
    assert isinstance(after_programs, dict)
    splits: list[dict[str, object]] = []
    merges: list[dict[str, object]] = []
    for program_id in sorted(after_programs):
        after_program = after_programs[program_id]
        before_program = before_programs.get(program_id)
        assert isinstance(after_program, dict)
        prior = before_program if isinstance(before_program, dict) else {}
        split_successors = sorted(_lineage_ids(after_program, "split-into") - _lineage_ids(prior, "split-into"))
        if split_successors:
            splits.append({"predecessorProgramId": str(program_id), "successorProgramIds": split_successors})
        merge_predecessors = sorted(_lineage_ids(after_program, "merged-from") - _lineage_ids(prior, "merged-from"))
        if merge_predecessors:
            merges.append({"predecessorProgramIds": merge_predecessors, "successorProgramId": str(program_id)})
    return _with_alignment_digest(
        {
            "schemaVersion": 2,
            "problemId": before_state["problemId"],
            "beforeKnowledgeStateDigest": before_state["stateDigest"],
            "afterKnowledgeStateDigest": after_state["stateDigest"],
            "preserved": _sorted_identity_entries(preserved),
            "moved": _sorted_identity_entries(moved),
            "splits": sorted(splits, key=lambda item: str(item["predecessorProgramId"])),
            "merges": sorted(merges, key=lambda item: str(item["successorProgramId"])),
            "created": _sorted_identity_entries(created),
            "retired": _sorted_identity_entries(retired),
        }
    )


def validate_research_topology_alignment_v2(
    alignment: object,
    before_state: dict[str, object],
    after_state: dict[str, object],
) -> dict[str, object]:
    if not isinstance(alignment, dict) or set(alignment) != ALIGNMENT_FIELDS:
        raise MathFlowError("research topology alignment v2 has an invalid envelope")
    expected = derive_research_topology_alignment_v2(before_state, after_state)
    if alignment != expected:
        raise MathFlowError("research topology alignment v2 differs from deterministic state alignment")
    return alignment


def _same_world_handoff(
    subject_transaction_id: str,
    before_state: dict[str, object],
    after_state: dict[str, object],
    alignment: dict[str, object],
) -> dict[str, object]:
    return _with_handoff_digest(
        {
            "schemaVersion": 2,
            "problemId": before_state["problemId"],
            "subjectTransactionId": subject_transaction_id,
            "beforeKnowledgeStateDigest": before_state["stateDigest"],
            "afterKnowledgeStateDigest": after_state["stateDigest"],
            "topologyAlignmentDigest": alignment["alignmentDigest"],
            "sameWorldReferenceStateDigest": after_state["stateDigest"],
            "accountingNodeKinds": ["program"],
            "semanticLeafKinds": ["intermediateResult"],
        }
    )


def validate_research_builder_v7_handoff(
    handoff: object,
    before_state: dict[str, object],
    after_state: dict[str, object],
    alignment: dict[str, object],
    subject_transaction_id: str,
) -> dict[str, object]:
    if not GIT_SHA.fullmatch(subject_transaction_id):
        raise MathFlowError("research builder v7 handoff has an invalid subject")
    validate_research_program_state_v3(before_state)
    validate_research_program_state_v3(after_state)
    validate_research_topology_alignment_v2(alignment, before_state, after_state)
    if not isinstance(handoff, dict) or set(handoff) != HANDOFF_FIELDS:
        raise MathFlowError("research builder v7 handoff has an invalid envelope")
    expected = _same_world_handoff(subject_transaction_id, before_state, after_state, alignment)
    if handoff != expected:
        raise MathFlowError("research builder v7 handoff differs from deterministic same-world handoff")
    return handoff


def apply_research_builder_v7_transition(
    base_state: dict[str, object],
    transition: object,
    *,
    accepted_claims: object,
    judgment_id: str,
) -> dict[str, object]:
    """Apply one accepted submission to the two-entity knowledge state."""

    validate_research_program_state_v3(base_state)
    if not isinstance(transition, dict) or set(transition) != TRANSITION_FIELDS:
        raise MathFlowError("research builder v7 transition has an invalid envelope")
    if transition.get("schemaVersion") != 1:
        raise MathFlowError("research builder v7 transition has an unsupported version")
    subject = transition.get("subjectTransactionId")
    if not isinstance(subject, str) or not GIT_SHA.fullmatch(subject):
        raise MathFlowError("research builder v7 transition has an invalid subject")
    if transition.get("baseStateDigest") != base_state.get("stateDigest"):
        raise MathFlowError("research builder v7 transition has a stale base state")
    topology_operations = transition.get("topologyOperations")
    if not isinstance(topology_operations, list):
        raise MathFlowError("research builder v7 topologyOperations must be an array")
    topology_rationale = transition.get("topologyRationale")
    if topology_operations:
        _require_text(topology_rationale, "research builder v7 topology rationale")
    elif topology_rationale is not None:
        raise MathFlowError("research builder v7 topology rationale requires topology operations")
    post_state = _apply_transition_operations(
        base_state,
        transition,
        accepted_claims=accepted_claims,
        judgment_id=judgment_id,
    )
    alignment = derive_research_topology_alignment_v2(base_state, post_state)
    handoff = _same_world_handoff(subject, base_state, post_state, alignment)
    validate_research_builder_v7_handoff(handoff, base_state, post_state, alignment, subject)
    return {
        "subjectTransactionId": subject,
        "postState": post_state,
        "topologyAlignment": alignment,
        "sameWorldHandoff": handoff,
    }


def apply_research_builder_v7_sequence(
    base_state: dict[str, object],
    transitions: object,
    *,
    accepted_submissions: object,
) -> list[dict[str, object]]:
    """Apply one v7 transition per accepted submission in canonical order."""

    validate_research_program_state_v3(base_state)
    if not isinstance(transitions, list) or not isinstance(accepted_submissions, list):
        raise MathFlowError("research builder v7 sequence inputs must be arrays")
    if len(transitions) != len(accepted_submissions):
        raise MathFlowError("research builder v7 sequence must have one transition per accepted submission")
    expected_subjects: list[str] = []
    prior_ordinal = -1
    normalized_submissions: list[dict[str, object]] = []
    for submission in accepted_submissions:
        if not isinstance(submission, dict) or set(submission) != {
            "transactionId",
            "ordinal",
            "acceptedClaims",
            "judgmentId",
        }:
            raise MathFlowError("research builder v7 accepted submission metadata is invalid")
        transaction_id = submission.get("transactionId")
        ordinal = submission.get("ordinal")
        if (
            not isinstance(transaction_id, str)
            or not GIT_SHA.fullmatch(transaction_id)
            or transaction_id in expected_subjects
            or not isinstance(ordinal, int)
            or isinstance(ordinal, bool)
            or ordinal <= prior_ordinal
        ):
            raise MathFlowError("research builder v7 accepted submissions are not in canonical order")
        expected_subjects.append(transaction_id)
        prior_ordinal = ordinal
        normalized_submissions.append(submission)
    observed_subjects = [
        transition.get("subjectTransactionId") if isinstance(transition, dict) else None
        for transition in transitions
    ]
    if observed_subjects != expected_subjects:
        raise MathFlowError("research builder v7 transitions do not match accepted-submission order")
    results: list[dict[str, object]] = []
    state = base_state
    for transition, submission in zip(transitions, normalized_submissions, strict=True):
        reduced = apply_research_builder_v7_transition(
            state,
            transition,
            accepted_claims=submission["acceptedClaims"],
            judgment_id=str(submission["judgmentId"]),
        )
        results.append(reduced)
        state = reduced["postState"]
        assert isinstance(state, dict)
    return results
