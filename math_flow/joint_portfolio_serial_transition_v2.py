"""Generalized bounded joint knowledge/topology/live-W+ transition V2.

V2 separates support-only result refresh from semantic replacement, carries a
cumulative work-policy boundary state, derives the complete accounting-affected
program set, and resolves typed W+ evidence references before reduction.
"""

from __future__ import annotations

import copy
import re
from collections.abc import Mapping, Sequence
from fractions import Fraction

from math_flow.errors import MathFlowError
from math_flow.joint_portfolio_boundaries import (
    BOUNDARY_TEXT_FIELDS,
    advance_joint_portfolio_boundary_state_v1,
    validate_joint_portfolio_boundary_state_v1,
)
from math_flow.joint_portfolio_serial_transition import evidence_manifest_digest
from math_flow.repository import sha256_json
from math_flow.research_builder_v7 import validate_research_program_state_v3
from math_flow.research_builder_joint_v11 import (
    apply_research_builder_joint_v11_transition,
)
from math_flow.research_builder_v10 import validate_research_builder_v10_authoring_packet
from math_flow.work_accounting import (
    apply_work_accounting_patch,
    bind_patch_to_state,
    canonical_decimal,
    make_work_accounting_patch,
    validate_root_contract,
    validate_work_accounting_state,
)


IMPLEMENTATION = "joint-portfolio-serial-transition-v2"
DIGEST = re.compile(r"^sha256:[0-9a-f]{64}$")
TRANSACTION = re.compile(r"^[0-9a-f]{40}$")
IDENTIFIER = re.compile(r"^[a-z0-9][a-z0-9/_-]*$")

SEMANTIC_PACKET_FIELDS = {
    "schemaVersion",
    "problemId",
    "subjectTransactionId",
    "baseStateDigest",
    "acceptedClaimsDigest",
    "evidenceManifestDigest",
    "rootUpdate",
    "resultChanges",
    "packetDigest",
}
ROOT_UPDATE_FIELDS = {"currentStateSummary", "localResidualSummary"}
SUPPORT_ADDITION_FIELDS = {
    "proofs",
    "methods",
    "computations",
    "tools",
    "artifactPaths",
    "attestationRefs",
}
RESULT_CHANGE_FIELDS = {
    "action",
    "id",
    "baseDigest",
    "title",
    "statement",
    "scopeQualifications",
    "supportAdditions",
    "dependencyResultIds",
    "claimKeys",
    "status",
    "supersededByResultIds",
}
RESPONSE_FIELDS = {
    "schemaVersion",
    "subjectTransactionId",
    "baseStateDigest",
    "baseAccountingStateDigest",
    "baseBoundaryStateDigest",
    "semanticPacketDigest",
    "authoringPacketDigest",
    "programChanges",
    "resultPlacements",
    "programBoundaries",
    "withAccessAssessments",
    "topologyRationale",
}
PROGRAM_CHANGE_FIELDS = {
    "action",
    "programId",
    "baseDigest",
    "parentId",
    "title",
    "objective",
    "currentStateSummary",
    "localResidualSummary",
    "status",
}
PLACEMENT_FIELDS = {"resultId", "primaryProgramId", "relatedProgramIds"}
BOUNDARY_FIELDS = {"programId", *BOUNDARY_TEXT_FIELDS}
EVIDENCE_REF_FIELDS = {"kind", "id", "digest"}
ASSESSMENT_FIELDS = {
    "programId",
    "directWorkHours",
    "conditionalIncidence",
    "rationale",
    "evidenceRefs",
}


def _digest(value: object) -> str:
    return f"sha256:{sha256_json(copy.deepcopy(value))}"


def _content_digest(value: Mapping[str, object], field: str) -> str:
    return _digest({key: item for key, item in value.items() if key != field})


def _require_text(value: object, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise MathFlowError(f"{label} must be non-empty text")
    return value


def _require_identifier(value: object, label: str) -> str:
    if not isinstance(value, str) or not IDENTIFIER.fullmatch(value):
        raise MathFlowError(f"{label} is invalid")
    return value


def _sorted_strings(
    value: object,
    label: str,
    *,
    pattern: re.Pattern[str] | None = None,
) -> list[str]:
    if not isinstance(value, list) or any(not isinstance(item, str) for item in value):
        raise MathFlowError(f"{label} must be an array of strings")
    result = list(value)
    if result != sorted(set(result)):
        raise MathFlowError(f"{label} must be unique and canonically ordered")
    if pattern is not None and any(not pattern.fullmatch(item) for item in result):
        raise MathFlowError(f"{label} contains an invalid identifier")
    return result


def _accepted_claim_keys(accepted_claims: object) -> set[str]:
    if not isinstance(accepted_claims, list) or not accepted_claims:
        raise MathFlowError("joint serial V2 needs accepted claims")
    keys = [
        _require_identifier(
            claim.get("claimKey") if isinstance(claim, dict) else None,
            "accepted claim key",
        )
        for claim in accepted_claims
    ]
    if len(keys) != len(set(keys)):
        raise MathFlowError("joint serial V2 accepted claim keys must be unique")
    return set(keys)


def make_joint_portfolio_semantic_packet_v2(
    *,
    problem_id: str,
    subject_transaction_id: str,
    base_state_digest: str,
    accepted_claims: object,
    evidence_file_refs: Mapping[str, str],
    root_update: Mapping[str, object],
    result_changes: Sequence[Mapping[str, object]],
) -> dict[str, object]:
    core: dict[str, object] = {
        "schemaVersion": 2,
        "problemId": problem_id,
        "subjectTransactionId": subject_transaction_id,
        "baseStateDigest": base_state_digest,
        "acceptedClaimsDigest": _digest(accepted_claims),
        "evidenceManifestDigest": evidence_manifest_digest(evidence_file_refs),
        "rootUpdate": copy.deepcopy(dict(root_update)),
        "resultChanges": copy.deepcopy(list(result_changes)),
    }
    return {**core, "packetDigest": _content_digest(core, "packetDigest")}


def _semantic_fields_equal(raw: Mapping[str, object], existing: Mapping[str, object]) -> bool:
    return all(
        raw[field] == existing[field]
        for field in ("title", "statement", "scopeQualifications", "dependencyResultIds")
    )


def _support_is_empty(value: Mapping[str, object]) -> bool:
    return all(not value[field] for field in SUPPORT_ADDITION_FIELDS)


def validate_joint_portfolio_semantic_packet_v2(
    value: object,
    *,
    base_state: Mapping[str, object],
    accepted_claims: object,
    evidence_file_refs: Mapping[str, str],
) -> dict[str, object]:
    state = validate_research_program_state_v3(copy.deepcopy(dict(base_state)))
    if not isinstance(value, dict) or set(value) != SEMANTIC_PACKET_FIELDS:
        raise MathFlowError("joint serial V2 semantic packet has an invalid envelope")
    if value.get("schemaVersion") != 2 or value.get("problemId") != state["problemId"]:
        raise MathFlowError("joint serial V2 semantic packet belongs to another protocol")
    subject = value.get("subjectTransactionId")
    if not isinstance(subject, str) or not TRANSACTION.fullmatch(subject):
        raise MathFlowError("joint serial V2 semantic packet has an invalid subject")
    if value.get("baseStateDigest") != state["stateDigest"]:
        raise MathFlowError("joint serial V2 semantic packet has a stale base state")
    if value.get("acceptedClaimsDigest") != _digest(accepted_claims):
        raise MathFlowError("joint serial V2 semantic packet accepted-claim binding is stale")
    if value.get("evidenceManifestDigest") != evidence_manifest_digest(evidence_file_refs):
        raise MathFlowError("joint serial V2 semantic packet evidence binding is stale")
    if value.get("packetDigest") != _content_digest(value, "packetDigest"):
        raise MathFlowError("joint serial V2 semantic packet digest mismatch")
    root_update = value.get("rootUpdate")
    if not isinstance(root_update, dict) or set(root_update) != ROOT_UPDATE_FIELDS:
        raise MathFlowError("joint serial V2 root update is invalid")
    for field in ROOT_UPDATE_FIELDS:
        _require_text(root_update.get(field), f"joint serial V2 root {field}")

    changes = value.get("resultChanges")
    if not isinstance(changes, list) or not changes:
        raise MathFlowError("joint serial V2 needs result changes")
    accepted_keys = _accepted_claim_keys(accepted_claims)
    base_results = state["intermediateResults"]
    prospective = set(base_results)
    ids: list[str] = []
    for raw in changes:
        if not isinstance(raw, dict) or set(raw) != RESULT_CHANGE_FIELDS:
            raise MathFlowError("joint serial V2 result change has invalid fields")
        result_id = _require_identifier(raw.get("id"), "joint serial V2 result ID")
        ids.append(result_id)
        action = raw.get("action")
        existing = base_results.get(result_id)
        if action == "create":
            if existing is not None or raw.get("baseDigest") is not None:
                raise MathFlowError("joint serial V2 result creation requires a new ID")
            prospective.add(result_id)
        elif action in {"support", "supersede", "retire"}:
            if not isinstance(existing, dict) or raw.get("baseDigest") != existing.get("digest"):
                raise MathFlowError("joint serial V2 result change has a stale base guard")
        else:
            raise MathFlowError("joint serial V2 result action is invalid")
    if ids != sorted(set(ids)):
        raise MathFlowError("joint serial V2 result changes must be canonically ordered")

    observed_claims: set[str] = set()
    created_ids = {
        str(raw["id"]) for raw in changes if isinstance(raw, dict) and raw.get("action") == "create"
    }
    for raw in changes:
        result_id = str(raw["id"])
        action = str(raw["action"])
        existing = base_results.get(result_id)
        for field in ("title", "statement"):
            _require_text(raw.get(field), f"joint serial V2 result {field}")
        qualifications = _sorted_strings(raw.get("scopeQualifications"), "result qualifications")
        dependencies = _sorted_strings(raw.get("dependencyResultIds"), "result dependencies", pattern=IDENTIFIER)
        claim_keys = _sorted_strings(raw.get("claimKeys"), "result claim keys", pattern=IDENTIFIER)
        successors = _sorted_strings(raw.get("supersededByResultIds"), "result successors", pattern=IDENTIFIER)
        if not set(claim_keys) <= accepted_keys:
            raise MathFlowError("joint serial V2 result references an unaccepted claim")
        observed_claims.update(claim_keys)
        support = raw.get("supportAdditions")
        if not isinstance(support, dict) or set(support) != SUPPORT_ADDITION_FIELDS:
            raise MathFlowError("joint serial V2 result support additions are invalid")
        for field in ("proofs", "methods", "computations", "tools", "artifactPaths"):
            _sorted_strings(support.get(field), f"result support {field}")
        _sorted_strings(support.get("attestationRefs"), "result attestation refs", pattern=DIGEST)
        if not set(support["artifactPaths"]) <= set(evidence_file_refs):
            raise MathFlowError("joint serial V2 result references unavailable evidence")
        if result_id in set(dependencies) | set(successors):
            raise MathFlowError("joint serial V2 result references itself")
        if not set(dependencies) <= prospective or not set(successors) <= prospective:
            raise MathFlowError("joint serial V2 result references an unknown result")

        if action == "create":
            if raw.get("status") != "active" or successors:
                raise MathFlowError("joint serial V2 may create only active results")
            if not claim_keys:
                raise MathFlowError("joint serial V2 created results need accepted claim provenance")
        else:
            assert isinstance(existing, dict)
            if not _semantic_fields_equal(raw, existing):
                raise MathFlowError(
                    "joint serial V2 support/lifecycle change cannot replace result semantics"
                )
            if action == "support" and (
                raw.get("status") != existing["status"]
                or successors != existing["supersededByResultIds"]
            ):
                raise MathFlowError("joint serial V2 support refresh may change only support and provenance")
            if action == "support" and not claim_keys:
                raise MathFlowError("joint serial V2 support refresh needs accepted claim provenance")
            if action == "supersede" and (
                existing["status"] != "active"
                or raw.get("status") != "superseded"
                or not successors
                or not set(successors) <= created_ids
            ):
                raise MathFlowError("joint serial V2 supersession needs explicit new successor results")
            if action == "retire" and (
                existing["status"] == "retired"
                or raw.get("status") != "retired"
                or successors != existing["supersededByResultIds"]
            ):
                raise MathFlowError("joint serial V2 result retirement is invalid")
            if action in {"supersede", "retire"} and (
                claim_keys or not _support_is_empty(support)
            ):
                raise MathFlowError(
                    "joint serial V2 lifecycle changes cannot treat the new claim as support for old semantics"
                )
        if qualifications != raw["scopeQualifications"]:
            raise AssertionError("canonical qualification validation drift")
    if observed_claims != accepted_keys:
        raise MathFlowError("joint serial V2 result changes must cover every accepted claim")
    return copy.deepcopy(value)


def _merge_strings(before: Sequence[object], additions: Sequence[object]) -> list[str]:
    return sorted({str(item) for item in [*before, *additions]})


def _merge_artifacts(
    before: Sequence[object],
    paths: Sequence[str],
    evidence_file_refs: Mapping[str, str],
) -> list[dict[str, str]]:
    rows = {
        (str(raw["path"]), str(raw["digest"]))
        for raw in before
        if isinstance(raw, Mapping) and "path" in raw and "digest" in raw
    }
    rows.update((path, evidence_file_refs[path]) for path in paths)
    return [{"path": path, "digest": digest} for path, digest in sorted(rows)]


def _materialize_result(
    raw: Mapping[str, object],
    *,
    base_state: Mapping[str, object],
    subject: str,
    judgment_id: str,
    evidence_file_refs: Mapping[str, str],
    primary_program_id: str,
    related_program_ids: Sequence[str],
) -> dict[str, object]:
    existing = base_state["intermediateResults"].get(str(raw["id"]))
    if isinstance(existing, Mapping):
        if (
            primary_program_id != existing["primaryProgramId"]
            or list(related_program_ids) != existing["relatedProgramIds"]
        ):
            raise MathFlowError("joint serial V2 existing result placement must remain exact")
        prior_support = existing["support"]
        prior_claims = existing["claimRefs"]
        prior_sources = existing["sourceTransactionIds"]
        prior_judgments = existing["judgmentIds"]
    else:
        prior_support = {
            "proofs": [], "methods": [], "computations": [], "tools": [],
            "artifactRefs": [], "attestationRefs": [],
        }
        prior_claims = []
        prior_sources = []
        prior_judgments = []
    additions = raw["supportAdditions"]
    claims = {
        (str(item["transactionId"]), str(item["claimKey"]))
        for item in prior_claims
        if isinstance(item, Mapping)
    }
    claims.update((subject, str(key)) for key in raw["claimKeys"])
    return {
        "id": raw["id"],
        "primaryProgramId": primary_program_id,
        "relatedProgramIds": list(related_program_ids),
        "title": raw["title"],
        "statement": raw["statement"],
        "scopeQualifications": list(raw["scopeQualifications"]),
        "support": {
            "proofs": _merge_strings(prior_support["proofs"], additions["proofs"]),
            "methods": _merge_strings(prior_support["methods"], additions["methods"]),
            "computations": _merge_strings(prior_support["computations"], additions["computations"]),
            "tools": _merge_strings(prior_support["tools"], additions["tools"]),
            "artifactRefs": _merge_artifacts(prior_support["artifactRefs"], additions["artifactPaths"], evidence_file_refs),
            "attestationRefs": _merge_strings(prior_support["attestationRefs"], additions["attestationRefs"]),
        },
        "dependencyResultIds": list(raw["dependencyResultIds"]),
        "claimRefs": [
            {"transactionId": transaction_id, "claimKey": claim_key}
            for transaction_id, claim_key in sorted(claims)
        ],
        "sourceTransactionIds": sorted({*map(str, prior_sources), subject}),
        "judgmentIds": sorted({*map(str, prior_judgments), judgment_id}),
        "status": raw["status"],
        "supersededByResultIds": list(raw["supersededByResultIds"]),
    }


def _evidence_ref_schema() -> dict[str, object]:
    return {
        "type": "object",
        "additionalProperties": False,
        "required": sorted(EVIDENCE_REF_FIELDS),
        "properties": {
            "kind": {
                "type": "string",
                "enum": ["accepted-claim", "submission-evidence", "prior-program", "prior-result", "semantic-result"],
            },
            "id": {"type": "string"},
            "digest": {"type": "string"},
        },
    }


def joint_portfolio_serial_response_schema_v2(
    *,
    subject_transaction_id: str,
    base_state_digest: str,
    base_accounting_state_digest: str,
    base_boundary_state_digest: str,
    semantic_packet_digest: str,
    authoring_packet_digest: str,
) -> dict[str, object]:
    text = {"type": "string", "minLength": 1}
    array = {"type": "array", "items": {"type": "string"}}
    return {
        "type": "object",
        "additionalProperties": False,
        "required": sorted(RESPONSE_FIELDS),
        "properties": {
            "schemaVersion": {"type": "integer", "const": 2},
            "subjectTransactionId": {"type": "string", "const": subject_transaction_id},
            "baseStateDigest": {"type": "string", "const": base_state_digest},
            "baseAccountingStateDigest": {"type": "string", "const": base_accounting_state_digest},
            "baseBoundaryStateDigest": {"type": "string", "const": base_boundary_state_digest},
            "semanticPacketDigest": {"type": "string", "const": semantic_packet_digest},
            "authoringPacketDigest": {"type": "string", "const": authoring_packet_digest},
            "programChanges": {
                "type": "array",
                "items": {
                    "type": "object", "additionalProperties": False,
                    "required": sorted(PROGRAM_CHANGE_FIELDS),
                    "properties": {
                        "action": {"type": "string", "enum": ["create", "refresh", "move", "retire"]},
                        "programId": {"type": "string"},
                        "baseDigest": {"anyOf": [{"type": "string"}, {"type": "null"}]},
                        "parentId": {"anyOf": [{"type": "string"}, {"type": "null"}]},
                        "title": text, "objective": text, "currentStateSummary": text,
                        "localResidualSummary": text,
                        "status": {"type": "string", "enum": ["active", "completed", "retired"]},
                    },
                },
            },
            "resultPlacements": {
                "type": "array",
                "items": {
                    "type": "object", "additionalProperties": False,
                    "required": sorted(PLACEMENT_FIELDS),
                    "properties": {"resultId": {"type": "string"}, "primaryProgramId": {"type": "string"}, "relatedProgramIds": array},
                },
            },
            "programBoundaries": {
                "type": "array",
                "items": {
                    "type": "object", "additionalProperties": False,
                    "required": sorted(BOUNDARY_FIELDS),
                    "properties": {"programId": {"type": "string"}, **{field: text for field in BOUNDARY_TEXT_FIELDS}},
                },
            },
            "withAccessAssessments": {
                "type": "array",
                "items": {
                    "type": "object", "additionalProperties": False,
                    "required": sorted(ASSESSMENT_FIELDS),
                    "properties": {
                        "programId": {"type": "string"}, "directWorkHours": {"type": "string"},
                        "conditionalIncidence": {"anyOf": [{"type": "string"}, {"type": "null"}]},
                        "rationale": text,
                        "evidenceRefs": {"type": "array", "items": _evidence_ref_schema()},
                    },
                },
            },
            "topologyRationale": {"anyOf": [text, {"type": "null"}]},
        },
    }


def _validate_evidence_refs(
    value: object,
    *,
    semantic_packet: Mapping[str, object],
    base_state: Mapping[str, object],
    evidence_file_refs: Mapping[str, str],
    readable_program_ids: set[str],
    readable_result_ids: set[str],
) -> list[dict[str, str]]:
    if not isinstance(value, list) or not value:
        raise MathFlowError("joint serial V2 W+ assessment needs typed evidence")
    result_ids = {str(raw["id"]) for raw in semantic_packet["resultChanges"]}
    rows: list[dict[str, str]] = []
    for raw in value:
        if not isinstance(raw, dict) or set(raw) != EVIDENCE_REF_FIELDS:
            raise MathFlowError("joint serial V2 W+ evidence reference is invalid")
        kind, identifier, digest = raw.get("kind"), raw.get("id"), raw.get("digest")
        if not isinstance(identifier, str) or not isinstance(digest, str) or not DIGEST.fullmatch(digest):
            raise MathFlowError("joint serial V2 W+ evidence reference is malformed")
        expected: str | None = None
        if kind == "accepted-claim" and identifier in _accepted_claim_keys_from_packet(semantic_packet):
            expected = str(semantic_packet["acceptedClaimsDigest"])
        elif kind == "submission-evidence" and identifier in evidence_file_refs:
            expected = evidence_file_refs[identifier]
        elif (
            kind == "prior-program"
            and identifier in readable_program_ids
            and identifier in base_state["programs"]
        ):
            expected = str(base_state["programs"][identifier]["digest"])
        elif (
            kind == "prior-result"
            and identifier in readable_result_ids
            and identifier in base_state["intermediateResults"]
        ):
            expected = str(base_state["intermediateResults"][identifier]["digest"])
        elif kind == "semantic-result" and identifier in result_ids:
            expected = str(semantic_packet["packetDigest"])
        if digest != expected:
            raise MathFlowError("joint serial V2 W+ evidence reference does not resolve")
        rows.append({"kind": str(kind), "id": identifier, "digest": digest})
    if rows != sorted(rows, key=lambda row: (row["kind"], row["id"], row["digest"])) or len({(row["kind"], row["id"], row["digest"]) for row in rows}) != len(rows):
        raise MathFlowError("joint serial V2 W+ evidence references must be canonical")
    return rows


def _accepted_claim_keys_from_packet(packet: Mapping[str, object]) -> set[str]:
    return {
        str(key)
        for raw in packet["resultChanges"]
        for key in raw["claimKeys"]
    }


def _validate_response(
    value: object,
    *,
    base_state: Mapping[str, object],
    base_accounting_state: Mapping[str, object],
    base_boundary_state: Mapping[str, object],
    semantic_packet: Mapping[str, object],
    authoring_packet: Mapping[str, object],
    evidence_file_refs: Mapping[str, str],
) -> tuple[dict[str, object], list[str]]:
    if not isinstance(value, dict) or set(value) != RESPONSE_FIELDS or value.get("schemaVersion") != 2:
        raise MathFlowError("joint serial V2 response has an invalid envelope")
    expected = {
        "subjectTransactionId": semantic_packet["subjectTransactionId"],
        "baseStateDigest": base_state["stateDigest"],
        "baseAccountingStateDigest": base_accounting_state["stateDigest"],
        "baseBoundaryStateDigest": base_boundary_state["stateDigest"],
        "semanticPacketDigest": semantic_packet["packetDigest"],
        "authoringPacketDigest": authoring_packet["authoringPacketDigest"],
    }
    for field, expected_value in expected.items():
        if value.get(field) != expected_value:
            raise MathFlowError(f"joint serial V2 response has a stale {field} binding")
    write = authoring_packet["writeScope"]
    read = authoring_packet["readSet"]
    existing_programs = set(write["existingProgramIds"])
    created_programs = set(write["createProgramIds"])
    readable_programs = set(read["programIds"]) | created_programs | {"root"}
    readable_prior_programs = set(read["programIds"])
    readable_prior_results = set(read["resultIds"])
    existing_results = set(write["existingResultIds"])
    created_results = set(write["createResultIds"])

    raw_changes = value.get("programChanges")
    if not isinstance(raw_changes, list):
        raise MathFlowError("joint serial V2 program changes must be an array")
    program_changes: dict[str, dict[str, object]] = {}
    affected = {"root"}
    topology = False
    for raw in raw_changes:
        if not isinstance(raw, dict) or set(raw) != PROGRAM_CHANGE_FIELDS:
            raise MathFlowError("joint serial V2 program change has invalid fields")
        program_id = _require_identifier(raw.get("programId"), "joint serial V2 program ID")
        if program_id == "root" or program_id in program_changes:
            raise MathFlowError("joint serial V2 program changes must be unique and exclude root")
        action = raw.get("action")
        existing = base_state["programs"].get(program_id)
        parent = raw.get("parentId")
        if not isinstance(parent, str) or parent not in readable_programs or parent == program_id:
            raise MathFlowError("joint serial V2 program parent is outside local scope")
        for field in ("title", "objective", "currentStateSummary", "localResidualSummary"):
            _require_text(raw.get(field), f"joint serial V2 program {field}")
        if action == "create":
            if existing is not None or program_id not in created_programs or raw.get("baseDigest") is not None or raw.get("status") != "active":
                raise MathFlowError("joint serial V2 program creation escapes its scope")
            topology = True
        elif action in {"refresh", "move", "retire"}:
            if not isinstance(existing, dict) or program_id not in existing_programs or raw.get("baseDigest") != existing["digest"]:
                raise MathFlowError("joint serial V2 existing program change has a stale scope guard")
            affected.add(str(existing["parentId"]))
            if action == "refresh":
                if parent != existing["parentId"] or raw.get("status") == "retired":
                    raise MathFlowError("joint serial V2 refresh hides topology or retirement")
                if raw.get("status") not in {existing["status"], "completed"}:
                    raise MathFlowError("joint serial V2 refresh has an invalid lifecycle change")
                if existing["status"] == "completed" and raw.get("status") != "completed":
                    raise MathFlowError("joint serial V2 cannot silently reopen a completed program")
                if raw.get("status") != existing["status"]:
                    topology = True
            elif action == "move":
                topology = True
                if parent == existing["parentId"] or existing["status"] != "active":
                    raise MathFlowError("joint serial V2 program move is invalid")
                for field in ("title", "objective", "currentStateSummary", "localResidualSummary", "status"):
                    if raw.get(field) != existing[field]:
                        raise MathFlowError("joint serial V2 move+refresh is not supported atomically")
            else:
                topology = True
                if parent != existing["parentId"] or existing["status"] == "retired" or raw.get("status") != "retired":
                    raise MathFlowError("joint serial V2 program retirement is invalid")
                for field in ("title", "objective", "currentStateSummary", "localResidualSummary"):
                    if raw.get(field) != existing[field]:
                        raise MathFlowError("joint serial V2 retirement must preserve semantics")
        else:
            raise MathFlowError("joint serial V2 program action is invalid")
        affected.update({program_id, parent})
        program_changes[program_id] = copy.deepcopy(raw)
    if list(program_changes) != sorted(program_changes):
        raise MathFlowError("joint serial V2 program changes must be canonical")
    program_actions = {str(raw["action"]) for raw in program_changes.values()}
    if "retire" in program_actions and program_actions != {"retire"}:
        raise MathFlowError(
            "joint serial V2 program retirement cannot accompany create, refresh, or move "
            "until atomic program lineage is supported"
        )

    semantic_ids = [str(raw["id"]) for raw in semantic_packet["resultChanges"]]
    raw_placements = value.get("resultPlacements")
    if not isinstance(raw_placements, list):
        raise MathFlowError("joint serial V2 placements must be an array")
    placements: dict[str, dict[str, object]] = {}
    owner_ids: set[str] = set()
    action_by_result = {str(raw["id"]): str(raw["action"]) for raw in semantic_packet["resultChanges"]}
    for raw in raw_placements:
        if not isinstance(raw, dict) or set(raw) != PLACEMENT_FIELDS:
            raise MathFlowError("joint serial V2 result placement has invalid fields")
        result_id = _require_identifier(raw.get("resultId"), "joint serial V2 placement result")
        primary = _require_identifier(raw.get("primaryProgramId"), "joint serial V2 primary program")
        related = _sorted_strings(raw.get("relatedProgramIds"), "joint serial V2 related programs", pattern=IDENTIFIER)
        owners = {primary, *related}
        if result_id in placements or primary in related or not owners <= readable_programs:
            raise MathFlowError("joint serial V2 result placement escapes local scope")
        if result_id in base_state["intermediateResults"]:
            prior = base_state["intermediateResults"][result_id]
            if result_id not in existing_results or primary != prior["primaryProgramId"] or related != prior["relatedProgramIds"]:
                raise MathFlowError("joint serial V2 existing result placement must remain exact")
        elif result_id not in created_results:
            raise MathFlowError("joint serial V2 result creation escapes its scope")
        placements[result_id] = copy.deepcopy(raw)
        owner_ids.update(owners)
        affected.update(owners)
        if action_by_result.get(result_id) in {"create", "supersede", "retire"}:
            topology = True
    if list(placements) != semantic_ids:
        raise MathFlowError("joint serial V2 must place every semantic result exactly once")
    if not (owner_ids - {"root"}) <= set(program_changes):
        raise MathFlowError("joint serial V2 non-root result owners must be explicitly changed")
    affected.discard("None")
    if not affected <= readable_programs:
        raise MathFlowError("joint serial V2 accounting-affected set escapes the read scope")
    affected_ids = sorted(affected)
    required_existing_writes = (
        affected & set(base_state["programs"])
    ) - {"root"}
    if not required_existing_writes <= existing_programs:
        raise MathFlowError(
            "joint serial V2 accounting-affected existing programs must be in the exact write scope"
        )

    boundaries = value.get("programBoundaries")
    if not isinstance(boundaries, list):
        raise MathFlowError("joint serial V2 boundaries must be an array")
    boundary_ids: list[str] = []
    for raw in boundaries:
        if not isinstance(raw, dict) or set(raw) != BOUNDARY_FIELDS:
            raise MathFlowError("joint serial V2 boundary has invalid fields")
        boundary_ids.append(_require_identifier(raw.get("programId"), "joint serial V2 boundary program"))
        for field in BOUNDARY_TEXT_FIELDS:
            _require_text(raw.get(field), f"joint serial V2 boundary {field}")
    if boundary_ids != affected_ids:
        raise MathFlowError("joint serial V2 boundaries must cover every accounting-affected program")

    assessments = value.get("withAccessAssessments")
    if not isinstance(assessments, list):
        raise MathFlowError("joint serial V2 W+ assessments must be an array")
    assessment_ids: list[str] = []
    for raw in assessments:
        if not isinstance(raw, dict) or set(raw) != ASSESSMENT_FIELDS:
            raise MathFlowError("joint serial V2 W+ assessment has invalid fields")
        program_id = _require_identifier(raw.get("programId"), "joint serial V2 W+ program")
        assessment_ids.append(program_id)
        canonical_decimal(raw.get("directWorkHours"), "joint serial V2 direct work")
        incidence = raw.get("conditionalIncidence")
        if program_id == "root":
            if incidence is not None:
                raise MathFlowError("joint serial V2 root cannot author incidence")
        elif Fraction(canonical_decimal(incidence, "joint serial V2 incidence")) > 1:
            raise MathFlowError("joint serial V2 incidence exceeds one")
        _require_text(raw.get("rationale"), "joint serial V2 W+ rationale")
        _validate_evidence_refs(
            raw.get("evidenceRefs"),
            semantic_packet=semantic_packet,
            base_state=base_state,
            evidence_file_refs=evidence_file_refs,
            readable_program_ids=readable_prior_programs,
            readable_result_ids=readable_prior_results,
        )
    if assessment_ids != affected_ids:
        raise MathFlowError("joint serial V2 W+ assessments must cover every accounting-affected program")
    rationale = value.get("topologyRationale")
    if topology:
        _require_text(rationale, "joint serial V2 topology rationale")
    elif rationale is not None:
        raise MathFlowError("joint serial V2 topology rationale requires a topology/lifecycle operation")
    return copy.deepcopy(value), affected_ids


def reduce_joint_portfolio_serial_transition_v2(
    response: object,
    *,
    base_state: Mapping[str, object],
    base_accounting_state: Mapping[str, object],
    base_boundary_state: Mapping[str, object],
    root_contract: Mapping[str, object],
    semantic_packet: Mapping[str, object],
    authoring_packet: Mapping[str, object],
    accepted_claims: object,
    judgment_id: str,
    evidence_file_refs: Mapping[str, str],
) -> dict[str, object]:
    state = validate_research_program_state_v3(copy.deepcopy(dict(base_state)))
    contract = validate_root_contract(copy.deepcopy(dict(root_contract)), str(state["problemId"]))
    accounting = validate_work_accounting_state(copy.deepcopy(dict(base_accounting_state)), state, contract)
    boundaries = validate_joint_portfolio_boundary_state_v1(base_boundary_state, state)
    packet = validate_joint_portfolio_semantic_packet_v2(semantic_packet, base_state=state, accepted_claims=accepted_claims, evidence_file_refs=evidence_file_refs)
    scope = validate_research_builder_v10_authoring_packet(copy.deepcopy(dict(authoring_packet)), base_state=state, accepted_claims=accepted_claims)
    if "root" not in scope["writeScope"]["existingProgramIds"]:
        raise MathFlowError("joint serial V2 local scope must authorize root synthesis")
    candidate, affected_ids = _validate_response(
        response, base_state=state, base_accounting_state=accounting,
        base_boundary_state=boundaries, semantic_packet=packet,
        authoring_packet=scope, evidence_file_refs=evidence_file_refs,
    )
    if not isinstance(judgment_id, str) or not DIGEST.fullmatch(judgment_id):
        raise MathFlowError("joint serial V2 needs an exact judgment digest")
    subject = str(packet["subjectTransactionId"])
    result_changes = {str(raw["id"]): raw for raw in packet["resultChanges"]}
    placements = {str(raw["resultId"]): raw for raw in candidate["resultPlacements"]}
    program_changes = {str(raw["programId"]): raw for raw in candidate["programChanges"]}
    memberships = {
        str(program_id): set(program["intermediateResultIds"])
        for program_id, program in state["programs"].items()
    }
    for program_id in program_changes:
        memberships.setdefault(program_id, set())
    materialized: dict[str, dict[str, object]] = {}
    for result_id in sorted(result_changes):
        placement = placements[result_id]
        result = _materialize_result(
            result_changes[result_id], base_state=state, subject=subject,
            judgment_id=judgment_id, evidence_file_refs=evidence_file_refs,
            primary_program_id=str(placement["primaryProgramId"]),
            related_program_ids=list(placement["relatedProgramIds"]),
        )
        materialized[result_id] = result
        for owner in [result["primaryProgramId"], *result["relatedProgramIds"]]:
            memberships.setdefault(str(owner), set()).add(result_id)

    content_operations: list[dict[str, object]] = []
    topology_operations: list[dict[str, object]] = []
    root = copy.deepcopy(state["programs"]["root"])
    root.pop("digest")
    root.update(copy.deepcopy(packet["rootUpdate"]))
    root["intermediateResultIds"] = sorted(memberships["root"])
    root["sourceTransactionIds"] = sorted({*root["sourceTransactionIds"], subject})
    content_operations.append({"entityKind": "program", "entityId": "root", "baseDigest": state["programs"]["root"]["digest"], "value": root})

    # V8/V10 require every affected existing ancestor to carry the subject.
    # For parents that need accounting reassessment but no semantic rewrite,
    # derive an exact semantic carry plus additive provenance in trusted code.
    for program_id in sorted(set(affected_ids) - {"root", *program_changes}):
        existing_parent = copy.deepcopy(state["programs"][program_id])
        existing_parent.pop("digest")
        existing_parent["sourceTransactionIds"] = sorted(
            {*existing_parent["sourceTransactionIds"], subject}
        )
        content_operations.append(
            {
                "entityKind": "program",
                "entityId": program_id,
                "baseDigest": state["programs"][program_id]["digest"],
                "value": existing_parent,
            }
        )

    for program_id in sorted(program_changes):
        raw = program_changes[program_id]
        action = str(raw["action"])
        existing = state["programs"].get(program_id)
        if action in {"move", "retire"}:
            assert isinstance(existing, Mapping)
            value = copy.deepcopy(existing)
            value.pop("digest")
            if action == "move":
                value["parentId"] = raw["parentId"]
            else:
                value["status"] = "retired"
            topology_operations.append({"action": action, "entityKind": "program", "entityId": program_id, "baseDigest": existing["digest"], "value": value})
            continue
        value = {
            "id": program_id, "parentId": raw["parentId"], "title": raw["title"],
            "objective": raw["objective"], "currentStateSummary": raw["currentStateSummary"],
            "localResidualSummary": raw["localResidualSummary"], "status": raw["status"],
            "intermediateResultIds": sorted(memberships[program_id]),
            "sourceTransactionIds": sorted({*(existing["sourceTransactionIds"] if isinstance(existing, Mapping) else []), subject}),
            "lineage": copy.deepcopy(existing["lineage"] if isinstance(existing, Mapping) else []),
        }
        operation = {"entityKind": "program", "entityId": program_id, "baseDigest": existing["digest"] if isinstance(existing, Mapping) else None, "value": value}
        if action == "create":
            topology_operations.append({"action": "create", **operation})
        else:
            content_operations.append(operation)

    for result_id in sorted(materialized):
        action = str(result_changes[result_id]["action"])
        existing = state["intermediateResults"].get(result_id)
        operation = {"entityKind": "intermediateResult", "entityId": result_id, "baseDigest": existing["digest"] if isinstance(existing, Mapping) else None, "value": materialized[result_id]}
        if action == "create":
            topology_operations.append({"action": "create", **operation})
        elif action == "retire":
            topology_operations.append({"action": "retire", **operation})
        else:
            content_operations.append(operation)

    contribution_result_ids = sorted(
        result_id
        for result_id, raw in result_changes.items()
        if raw["claimKeys"]
    )
    direct_program_ids = sorted({
        str(owner)
        for result_id in contribution_result_ids
        for owner in [
            materialized[result_id]["primaryProgramId"],
            *materialized[result_id]["relatedProgramIds"],
        ]
    })
    if direct_program_ids == ["root"]:
        placement_basis = "canonical-objective"
        placement_related: list[str] = []
    else:
        placement_basis = "local-objective" if len(direct_program_ids) == 1 else "cross-program"
        placement_related = direct_program_ids
    transition = {
        "schemaVersion": 1, "subjectTransactionId": subject, "baseStateDigest": state["stateDigest"],
        "contentOperations": content_operations, "topologyOperations": topology_operations,
        "contribution": {
            "claimKeys": sorted({str(key) for raw in result_changes.values() for key in raw["claimKeys"]}),
            "directProgramIds": direct_program_ids,
            "intermediateResultIds": contribution_result_ids,
        },
        "placementAudit": {
            "basis": placement_basis,
            "rationale": candidate["topologyRationale"] or "Stable accounting work packages and result identities are reused.",
            "relatedProgramIds": placement_related,
        },
        "topologyRationale": candidate["topologyRationale"],
    }
    final_program_statuses = {
        program_id: str(raw["status"])
        for program_id, raw in program_changes.items()
        if raw["status"] in {"completed", "retired"}
    }
    final_result_statuses = {
        result_id: "retired"
        for result_id, raw in result_changes.items()
        if raw["status"] == "retired"
    }
    reduced = apply_research_builder_joint_v11_transition(
        copy.deepcopy(state), transition, authoring_packet=scope,
        accepted_claims=accepted_claims, judgment_id=judgment_id,
        evidence_file_refs=evidence_file_refs,
        final_program_statuses=final_program_statuses,
        final_result_statuses=final_result_statuses,
    )
    post_state = reduced["postState"]
    target_boundaries = advance_joint_portfolio_boundary_state_v1(
        base_boundary_state=boundaries, base_knowledge_state=state,
        target_knowledge_state=post_state,
        updated_boundaries=candidate["programBoundaries"],
        required_program_ids=affected_ids,
    )

    base_annotations = {
        str(raw["nodeRef"]["id"]): raw
        for raw in accounting["annotations"]
        if raw["nodeRef"]["kind"] == "program"
    }
    updates: list[dict[str, object]] = []
    for assessment in candidate["withAccessAssessments"]:
        program_id = str(assessment["programId"])
        prior = base_annotations.get(program_id)
        direct = canonical_decimal(assessment["directWorkHours"], "joint serial V2 direct work")
        incidence = assessment["conditionalIncidence"]
        normalized_incidence = canonical_decimal(incidence, "joint serial V2 incidence") if incidence is not None else None
        changes: dict[str, object] = {}
        if prior is None or direct != prior["directWorkHours"]:
            changes["directWorkHours"] = direct
        if program_id != "root" and (prior is None or normalized_incidence != prior["conditionalIncidence"] or program_changes.get(program_id, {}).get("action") == "move"):
            changes["conditionalIncidence"] = normalized_incidence
        if changes:
            updates.append({
                "nodeRef": {"kind": "program", "id": program_id},
                "changes": changes, "rationale": assessment["rationale"],
                "evidenceRefs": [f"{raw['kind']}:{raw['id']}:{raw['digest']}" for raw in assessment["evidenceRefs"]],
            })
    patch = make_work_accounting_patch(
        problem_id=str(state["problemId"]), subject_transaction_id=subject,
        evaluation_mode="with-access", root_contract_digest=str(contract["rootContractDigest"]),
        base_accounting_state_digest=str(accounting["stateDigest"]),
        base_knowledge_state_digest=str(state["stateDigest"]),
        target_knowledge_state_digest=str(post_state["stateDigest"]),
        topology_alignment_digest=str(reduced["topologyAlignment"]["alignmentDigest"]),
        updates=updates,
    )
    patch = bind_patch_to_state(patch, accounting)
    with_access_state = apply_work_accounting_patch(
        accounting, patch, root_contract=contract, base_knowledge_state=state,
        target_knowledge_state=post_state, topology_alignment=reduced["topologyAlignment"],
    )
    after_annotations = {str(raw["nodeRef"]["id"]): raw for raw in with_access_state["annotations"]}
    for program_id, prior in base_annotations.items():
        if program_id not in affected_ids:
            after = after_annotations[program_id]
            if prior["directWorkHours"] != after["directWorkHours"] or prior["conditionalIncidence"] != after["conditionalIncidence"]:
                raise MathFlowError("joint serial V2 changed an unaffected W+ primitive")
    return {
        "schemaVersion": 2, "implementation": IMPLEMENTATION,
        "response": candidate, "semanticPacket": packet,
        "authoringPacketDigest": scope["authoringPacketDigest"],
        "accountingAffectedProgramIds": affected_ids,
        "transition": transition, "postState": post_state,
        "topologyAlignment": reduced["topologyAlignment"],
        "sameWorldHandoff": reduced["sameWorldHandoff"],
        "boundaryState": target_boundaries,
        "withAccessPatch": patch, "withAccessState": with_access_state,
    }


__all__ = [
    "IMPLEMENTATION",
    "joint_portfolio_serial_response_schema_v2",
    "make_joint_portfolio_semantic_packet_v2",
    "reduce_joint_portfolio_serial_transition_v2",
    "validate_joint_portfolio_semantic_packet_v2",
]
