from __future__ import annotations

import copy
import re
from fractions import Fraction
from typing import Mapping, Sequence

from math_flow.errors import MathFlowError
from math_flow.research_builder_v7 import validate_research_program_state_v3
from math_flow.research_builder_v10 import (
    apply_research_builder_v10_transition,
    validate_research_builder_v10_authoring_packet,
)
from math_flow.repository import sha256_json
from math_flow.work_accounting import (
    apply_work_accounting_patch,
    bind_patch_to_state,
    canonical_decimal,
    make_work_accounting_patch,
    validate_root_contract,
    validate_work_accounting_state,
)


IMPLEMENTATION = "joint-portfolio-serial-transition-v1"

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
SUPPORT_ADDITION_FIELDS = {
    "proofs",
    "methods",
    "computations",
    "tools",
    "artifactPaths",
    "attestationRefs",
}
RESPONSE_FIELDS = {
    "schemaVersion",
    "subjectTransactionId",
    "baseStateDigest",
    "baseAccountingStateDigest",
    "semanticPacketDigest",
    "authoringPacketDigest",
    "programChanges",
    "resultPlacements",
    "programBoundaries",
    "rootBoundary",
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
BOUNDARY_FIELDS = {
    "programId",
    "directResidualWorkScope",
    "activationCondition",
    "stoppingCondition",
    "independentVariationRationale",
}
ROOT_BOUNDARY_FIELDS = BOUNDARY_FIELDS - {"programId"}
ASSESSMENT_FIELDS = {
    "programId",
    "directWorkHours",
    "conditionalIncidence",
    "rationale",
    "evidenceRefs",
}


def _content_digest(value: Mapping[str, object], field: str) -> str:
    payload = {key: item for key, item in value.items() if key != field}
    return f"sha256:{sha256_json(payload)}"


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
        raise MathFlowError("joint serial transition needs accepted claims")
    keys: list[str] = []
    for claim in accepted_claims:
        if not isinstance(claim, dict):
            raise MathFlowError("joint serial accepted claim must be an object")
        keys.append(_require_identifier(claim.get("claimKey"), "accepted claim key"))
    if len(keys) != len(set(keys)):
        raise MathFlowError("joint serial accepted claim keys must be unique")
    return set(keys)


def evidence_manifest_digest(evidence_file_refs: Mapping[str, str]) -> str:
    rows: list[dict[str, str]] = []
    for path, digest in sorted(evidence_file_refs.items()):
        if not isinstance(path, str) or not path:
            raise MathFlowError("joint serial evidence path is invalid")
        if not isinstance(digest, str) or not DIGEST.fullmatch(digest):
            raise MathFlowError("joint serial evidence digest is invalid")
        rows.append({"path": path, "digest": digest})
    if not rows:
        raise MathFlowError("joint serial transition requires exact submission evidence")
    return f"sha256:{sha256_json(rows)}"


def make_joint_portfolio_semantic_packet_v1(
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
        "schemaVersion": 1,
        "problemId": problem_id,
        "subjectTransactionId": subject_transaction_id,
        "baseStateDigest": base_state_digest,
        "acceptedClaimsDigest": f"sha256:{sha256_json(accepted_claims)}",
        "evidenceManifestDigest": evidence_manifest_digest(evidence_file_refs),
        "rootUpdate": copy.deepcopy(dict(root_update)),
        "resultChanges": copy.deepcopy(list(result_changes)),
    }
    packet = {**core, "packetDigest": _content_digest(core, "packetDigest")}
    return packet


def validate_joint_portfolio_semantic_packet_v1(
    value: object,
    *,
    base_state: Mapping[str, object],
    accepted_claims: object,
    evidence_file_refs: Mapping[str, str],
) -> dict[str, object]:
    state = validate_research_program_state_v3(copy.deepcopy(dict(base_state)))
    if not isinstance(value, dict) or set(value) != SEMANTIC_PACKET_FIELDS:
        raise MathFlowError("joint serial semantic packet has an invalid envelope")
    if value.get("schemaVersion") != 1:
        raise MathFlowError("joint serial semantic packet has an unsupported version")
    if value.get("problemId") != state["problemId"]:
        raise MathFlowError("joint serial semantic packet belongs to another problem")
    subject = value.get("subjectTransactionId")
    if not isinstance(subject, str) or not TRANSACTION.fullmatch(subject):
        raise MathFlowError("joint serial semantic packet has an invalid subject")
    if value.get("baseStateDigest") != state["stateDigest"]:
        raise MathFlowError("joint serial semantic packet has a stale base state")
    if value.get("acceptedClaimsDigest") != f"sha256:{sha256_json(accepted_claims)}":
        raise MathFlowError("joint serial semantic packet accepted-claim binding is stale")
    if value.get("evidenceManifestDigest") != evidence_manifest_digest(evidence_file_refs):
        raise MathFlowError("joint serial semantic packet evidence binding is stale")
    if value.get("packetDigest") != _content_digest(value, "packetDigest"):
        raise MathFlowError("joint serial semantic packet digest mismatch")

    root_update = value.get("rootUpdate")
    if not isinstance(root_update, dict) or set(root_update) != ROOT_UPDATE_FIELDS:
        raise MathFlowError("joint serial semantic packet root update is invalid")
    for field in sorted(ROOT_UPDATE_FIELDS):
        _require_text(root_update.get(field), f"joint serial root update {field}")

    accepted_keys = _accepted_claim_keys(accepted_claims)
    base_results = state["intermediateResults"]
    assert isinstance(base_results, dict)
    changes = value.get("resultChanges")
    if not isinstance(changes, list) or not changes:
        raise MathFlowError("joint serial semantic packet needs result changes")
    observed_ids: list[str] = []
    prospective_ids = set(base_results)
    for raw in changes:
        if not isinstance(raw, dict) or set(raw) != RESULT_CHANGE_FIELDS:
            raise MathFlowError("joint serial semantic result change has invalid fields")
        result_id = _require_identifier(raw.get("id"), "joint serial result ID")
        observed_ids.append(result_id)
        action = raw.get("action")
        existing = base_results.get(result_id)
        if action == "create":
            if existing is not None or raw.get("baseDigest") is not None:
                raise MathFlowError("joint serial result creation requires a new ID")
            prospective_ids.add(result_id)
        elif action == "refresh":
            if not isinstance(existing, dict) or raw.get("baseDigest") != existing.get("digest"):
                raise MathFlowError("joint serial result refresh has a stale base guard")
        else:
            raise MathFlowError("joint serial semantic result action is invalid")
        for field in ("title", "statement"):
            _require_text(raw.get(field), f"joint serial result {field}")
        _sorted_strings(raw.get("scopeQualifications"), "result qualifications")
        dependencies = _sorted_strings(
            raw.get("dependencyResultIds"),
            "result dependencies",
            pattern=IDENTIFIER,
        )
        claim_keys = _sorted_strings(raw.get("claimKeys"), "result claim keys", pattern=IDENTIFIER)
        if not claim_keys or not set(claim_keys) <= accepted_keys:
            raise MathFlowError("joint serial semantic result references an unaccepted claim")
        if raw.get("status") != "active":
            raise MathFlowError("joint serial semantic results must remain active in V1")
        _sorted_strings(
            raw.get("supersededByResultIds"),
            "result supersession IDs",
            pattern=IDENTIFIER,
        )
        support = raw.get("supportAdditions")
        if not isinstance(support, dict) or set(support) != SUPPORT_ADDITION_FIELDS:
            raise MathFlowError("joint serial result support additions are invalid")
        for field in ("proofs", "methods", "computations", "tools", "artifactPaths"):
            _sorted_strings(support.get(field), f"result support {field}")
        _sorted_strings(support.get("attestationRefs"), "result attestation refs")
        if not set(support["artifactPaths"]) <= set(evidence_file_refs):
            raise MathFlowError("joint serial semantic result references unavailable evidence")
        if result_id in dependencies:
            raise MathFlowError("joint serial semantic result depends on itself")
    if observed_ids != sorted(set(observed_ids)):
        raise MathFlowError("joint serial semantic result changes must be canonically ordered")
    for raw in changes:
        if not set(raw["dependencyResultIds"]) <= prospective_ids:
            raise MathFlowError("joint serial semantic result has an unknown dependency")
        if not set(raw["supersededByResultIds"]) <= prospective_ids:
            raise MathFlowError("joint serial semantic result has an unknown successor")
    return copy.deepcopy(value)


def _merge_strings(before: Sequence[object], additions: Sequence[object]) -> list[str]:
    return sorted({str(item) for item in [*before, *additions]})


def _merge_artifact_refs(
    before: Sequence[object], additions: Sequence[str], evidence_file_refs: Mapping[str, str]
) -> list[dict[str, str]]:
    by_key: dict[tuple[str, str], dict[str, str]] = {}
    for raw in before:
        if isinstance(raw, dict):
            key = (str(raw.get("path")), str(raw.get("digest")))
            by_key[key] = {"path": key[0], "digest": key[1]}
    for path in additions:
        key = (path, evidence_file_refs[path])
        by_key[key] = {"path": key[0], "digest": key[1]}
    return [by_key[key] for key in sorted(by_key)]


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
    base_results = base_state["intermediateResults"]
    assert isinstance(base_results, dict)
    existing = base_results.get(str(raw["id"]))
    if isinstance(existing, dict):
        if primary_program_id != existing["primaryProgramId"] or list(related_program_ids) != list(existing["relatedProgramIds"]):
            raise MathFlowError(
                "joint serial V1 cannot combine a result refresh with a placement move"
            )
        prior_support = existing["support"]
        prior_claim_refs = list(existing["claimRefs"])
        prior_sources = list(existing["sourceTransactionIds"])
        prior_judgments = list(existing["judgmentIds"])
    else:
        prior_support = {
            "proofs": [],
            "methods": [],
            "computations": [],
            "tools": [],
            "artifactRefs": [],
            "attestationRefs": [],
        }
        prior_claim_refs = []
        prior_sources = []
        prior_judgments = []
    additions = raw["supportAdditions"]
    assert isinstance(additions, Mapping)
    claim_refs = {
        (str(item["transactionId"]), str(item["claimKey"]))
        for item in prior_claim_refs
        if isinstance(item, Mapping)
    }
    claim_refs.update((subject, str(key)) for key in raw["claimKeys"])
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
            "artifactRefs": _merge_artifact_refs(
                prior_support["artifactRefs"],
                list(additions["artifactPaths"]),
                evidence_file_refs,
            ),
            "attestationRefs": _merge_strings(
                prior_support["attestationRefs"], additions["attestationRefs"]
            ),
        },
        "dependencyResultIds": list(raw["dependencyResultIds"]),
        "claimRefs": [
            {"transactionId": transaction_id, "claimKey": claim_key}
            for transaction_id, claim_key in sorted(claim_refs)
        ],
        "sourceTransactionIds": sorted({*map(str, prior_sources), subject}),
        "judgmentIds": sorted({*map(str, prior_judgments), judgment_id}),
        "status": raw["status"],
        "supersededByResultIds": list(raw["supersededByResultIds"]),
    }


def joint_portfolio_serial_response_schema_v1(
    *,
    subject_transaction_id: str,
    base_state_digest: str,
    base_accounting_state_digest: str,
    semantic_packet_digest: str,
    authoring_packet_digest: str,
) -> dict[str, object]:
    text = {"type": "string", "minLength": 1}
    string_array = {"type": "array", "items": {"type": "string"}}
    program_change = {
        "type": "object",
        "additionalProperties": False,
        "required": sorted(PROGRAM_CHANGE_FIELDS),
        "properties": {
            "action": {"type": "string", "enum": ["create", "refresh", "move"]},
            "programId": {"type": "string"},
            "baseDigest": {"anyOf": [{"type": "string"}, {"type": "null"}]},
            "parentId": {"type": "string"},
            "title": text,
            "objective": text,
            "currentStateSummary": text,
            "localResidualSummary": text,
            "status": {"type": "string", "const": "active"},
        },
    }
    placement = {
        "type": "object",
        "additionalProperties": False,
        "required": sorted(PLACEMENT_FIELDS),
        "properties": {
            "resultId": {"type": "string"},
            "primaryProgramId": {"type": "string"},
            "relatedProgramIds": string_array,
        },
    }
    boundary = {
        "type": "object",
        "additionalProperties": False,
        "required": sorted(BOUNDARY_FIELDS),
        "properties": {field: text for field in BOUNDARY_FIELDS},
    }
    assessment = {
        "type": "object",
        "additionalProperties": False,
        "required": sorted(ASSESSMENT_FIELDS),
        "properties": {
            "programId": {"type": "string"},
            "directWorkHours": {"type": "string"},
            "conditionalIncidence": {
                "anyOf": [{"type": "string"}, {"type": "null"}]
            },
            "rationale": text,
            "evidenceRefs": string_array,
        },
    }
    root_boundary = {
        "type": "object",
        "additionalProperties": False,
        "required": sorted(ROOT_BOUNDARY_FIELDS),
        "properties": {field: text for field in ROOT_BOUNDARY_FIELDS},
    }
    return {
        "type": "object",
        "additionalProperties": False,
        "required": sorted(RESPONSE_FIELDS),
        "properties": {
            "schemaVersion": {"type": "integer", "const": 1},
            "subjectTransactionId": {"type": "string", "const": subject_transaction_id},
            "baseStateDigest": {"type": "string", "const": base_state_digest},
            "baseAccountingStateDigest": {
                "type": "string",
                "const": base_accounting_state_digest,
            },
            "semanticPacketDigest": {"type": "string", "const": semantic_packet_digest},
            "authoringPacketDigest": {"type": "string", "const": authoring_packet_digest},
            "programChanges": {"type": "array", "items": program_change},
            "resultPlacements": {"type": "array", "items": placement},
            "programBoundaries": {"type": "array", "items": boundary},
            "rootBoundary": root_boundary,
            "withAccessAssessments": {"type": "array", "items": assessment},
            "topologyRationale": {
                "anyOf": [{"type": "string", "minLength": 1}, {"type": "null"}]
            },
        },
    }


def _validate_response(
    value: object,
    *,
    base_state: Mapping[str, object],
    base_accounting_state: Mapping[str, object],
    semantic_packet: Mapping[str, object],
    authoring_packet: Mapping[str, object],
) -> dict[str, object]:
    if not isinstance(value, dict) or set(value) != RESPONSE_FIELDS:
        raise MathFlowError("joint serial response has an invalid envelope")
    if value.get("schemaVersion") != 1:
        raise MathFlowError("joint serial response has an unsupported version")
    expected_bindings = {
        "subjectTransactionId": semantic_packet["subjectTransactionId"],
        "baseStateDigest": base_state["stateDigest"],
        "baseAccountingStateDigest": base_accounting_state["stateDigest"],
        "semanticPacketDigest": semantic_packet["packetDigest"],
        "authoringPacketDigest": authoring_packet["authoringPacketDigest"],
    }
    for field, expected in expected_bindings.items():
        if value.get(field) != expected:
            raise MathFlowError(f"joint serial response has a stale {field} binding")

    write_scope = authoring_packet["writeScope"]
    read_set = authoring_packet["readSet"]
    assert isinstance(write_scope, Mapping) and isinstance(read_set, Mapping)
    existing_programs = set(write_scope["existingProgramIds"])
    created_programs = set(write_scope["createProgramIds"])
    readable_programs = set(read_set["programIds"]) | created_programs
    existing_results = set(write_scope["existingResultIds"])
    created_results = set(write_scope["createResultIds"])

    raw_program_changes = value.get("programChanges")
    if not isinstance(raw_program_changes, list):
        raise MathFlowError("joint serial program changes must be an array")
    program_changes: dict[str, dict[str, object]] = {}
    for raw in raw_program_changes:
        if not isinstance(raw, dict) or set(raw) != PROGRAM_CHANGE_FIELDS:
            raise MathFlowError("joint serial program change has invalid fields")
        program_id = _require_identifier(raw.get("programId"), "joint serial program ID")
        if program_id == "root" or program_id in program_changes:
            raise MathFlowError("joint serial program changes must be unique and exclude root")
        action = raw.get("action")
        existing = base_state["programs"].get(program_id)
        if action == "create":
            if existing is not None or program_id not in created_programs or raw.get("baseDigest") is not None:
                raise MathFlowError("joint serial program creation escapes its create scope")
        elif action in {"refresh", "move"}:
            if (
                not isinstance(existing, dict)
                or program_id not in existing_programs
                or raw.get("baseDigest") != existing.get("digest")
            ):
                raise MathFlowError("joint serial existing program change has a stale scope guard")
            if action == "refresh" and raw.get("parentId") != existing.get("parentId"):
                raise MathFlowError("joint serial program refresh hides a topology move")
            if action == "move":
                for field in (
                    "title",
                    "objective",
                    "currentStateSummary",
                    "localResidualSummary",
                    "status",
                ):
                    if raw.get(field) != existing.get(field):
                        raise MathFlowError("joint serial program move changes semantic content")
                if raw.get("parentId") == existing.get("parentId"):
                    raise MathFlowError("joint serial program move is a no-op")
        else:
            raise MathFlowError("joint serial program action is invalid")
        parent_id = _require_identifier(raw.get("parentId"), "joint serial program parent")
        if parent_id not in readable_programs or parent_id == program_id:
            raise MathFlowError("joint serial program parent is outside the read scope")
        for field in ("title", "objective", "currentStateSummary", "localResidualSummary"):
            _require_text(raw.get(field), f"joint serial program {field}")
        if raw.get("status") != "active":
            raise MathFlowError("joint serial V1 program changes must remain active")
        program_changes[program_id] = copy.deepcopy(raw)
    if list(program_changes) != sorted(program_changes):
        raise MathFlowError("joint serial program changes must be canonically ordered")

    semantic_ids = [str(row["id"]) for row in semantic_packet["resultChanges"]]
    raw_placements = value.get("resultPlacements")
    if not isinstance(raw_placements, list):
        raise MathFlowError("joint serial result placements must be an array")
    placements: dict[str, dict[str, object]] = {}
    owner_ids: set[str] = set()
    for raw in raw_placements:
        if not isinstance(raw, dict) or set(raw) != PLACEMENT_FIELDS:
            raise MathFlowError("joint serial result placement has invalid fields")
        result_id = _require_identifier(raw.get("resultId"), "joint serial placement result")
        if result_id in placements:
            raise MathFlowError("joint serial places one result more than once")
        primary = _require_identifier(raw.get("primaryProgramId"), "joint serial primary program")
        related = _sorted_strings(raw.get("relatedProgramIds"), "joint serial related programs", pattern=IDENTIFIER)
        linked = {primary, *related}
        if "root" in linked or not linked <= readable_programs:
            raise MathFlowError("joint serial result placement escapes the local program scope")
        placements[result_id] = copy.deepcopy(raw)
        owner_ids.update(linked)
    if list(placements) != semantic_ids:
        raise MathFlowError("joint serial must place every semantic result exactly once")
    if not owner_ids <= set(program_changes):
        raise MathFlowError("joint serial result owners must be explicitly refreshed or created")
    for result_id, raw in placements.items():
        if result_id in base_state["intermediateResults"]:
            existing = base_state["intermediateResults"][result_id]
            if result_id not in existing_results:
                raise MathFlowError("joint serial result refresh escapes its write scope")
            if (
                raw["primaryProgramId"] != existing["primaryProgramId"]
                or raw["relatedProgramIds"] != existing["relatedProgramIds"]
            ):
                raise MathFlowError("joint serial V1 cannot move a refreshed result")
        elif result_id not in created_results:
            raise MathFlowError("joint serial result creation escapes its create scope")

    boundaries = value.get("programBoundaries")
    if not isinstance(boundaries, list):
        raise MathFlowError("joint serial program boundaries must be an array")
    boundary_ids: list[str] = []
    for raw in boundaries:
        if not isinstance(raw, dict) or set(raw) != BOUNDARY_FIELDS:
            raise MathFlowError("joint serial program boundary has invalid fields")
        boundary_ids.append(_require_identifier(raw.get("programId"), "joint serial boundary program"))
        for field in sorted(ROOT_BOUNDARY_FIELDS):
            _require_text(raw.get(field), f"joint serial boundary {field}")
    if boundary_ids != sorted(program_changes):
        raise MathFlowError("joint serial boundaries must cover every changed program")
    root_boundary = value.get("rootBoundary")
    if not isinstance(root_boundary, dict) or set(root_boundary) != ROOT_BOUNDARY_FIELDS:
        raise MathFlowError("joint serial root boundary is invalid")
    for field in sorted(ROOT_BOUNDARY_FIELDS):
        _require_text(root_boundary.get(field), f"joint serial root boundary {field}")

    assessments = value.get("withAccessAssessments")
    if not isinstance(assessments, list):
        raise MathFlowError("joint serial W+ assessments must be an array")
    assessment_ids: list[str] = []
    for raw in assessments:
        if not isinstance(raw, dict) or set(raw) != ASSESSMENT_FIELDS:
            raise MathFlowError("joint serial W+ assessment has invalid fields")
        program_id = _require_identifier(raw.get("programId"), "joint serial W+ program")
        assessment_ids.append(program_id)
        canonical_decimal(raw.get("directWorkHours"), "joint serial direct work")
        incidence = raw.get("conditionalIncidence")
        if program_id == "root":
            if incidence is not None:
                raise MathFlowError("joint serial root W+ assessment cannot author incidence")
        else:
            probability = canonical_decimal(incidence, "joint serial conditional incidence")
            if Fraction(probability) > 1:
                raise MathFlowError("joint serial conditional incidence exceeds one")
        _require_text(raw.get("rationale"), "joint serial W+ rationale")
        evidence_refs = _sorted_strings(raw.get("evidenceRefs"), "joint serial W+ evidence refs")
        if not evidence_refs:
            raise MathFlowError("joint serial W+ assessments require evidence")
    required_assessments = sorted({"root", *program_changes})
    if assessment_ids != required_assessments:
        raise MathFlowError("joint serial W+ assessments must cover root and every changed program")

    topology_actions = {
        str(raw["action"]) for raw in program_changes.values()
    } & {"create", "move"}
    topology_actions.update(
        str(raw["action"])
        for raw in semantic_packet["resultChanges"]
        if raw["action"] == "create"
    )
    rationale = value.get("topologyRationale")
    if topology_actions:
        _require_text(rationale, "joint serial topology rationale")
    elif rationale is not None:
        raise MathFlowError("joint serial topology rationale requires a topology operation")
    return copy.deepcopy(value)


def reduce_joint_portfolio_serial_transition_v1(
    response: object,
    *,
    base_state: Mapping[str, object],
    base_accounting_state: Mapping[str, object],
    root_contract: Mapping[str, object],
    semantic_packet: Mapping[str, object],
    authoring_packet: Mapping[str, object],
    accepted_claims: object,
    judgment_id: str,
    evidence_file_refs: Mapping[str, str],
) -> dict[str, object]:
    state = validate_research_program_state_v3(copy.deepcopy(dict(base_state)))
    contract = validate_root_contract(copy.deepcopy(dict(root_contract)), str(state["problemId"]))
    base_accounting = validate_work_accounting_state(
        copy.deepcopy(dict(base_accounting_state)), state, contract
    )
    packet = validate_joint_portfolio_semantic_packet_v1(
        semantic_packet,
        base_state=state,
        accepted_claims=accepted_claims,
        evidence_file_refs=evidence_file_refs,
    )
    scope = validate_research_builder_v10_authoring_packet(
        copy.deepcopy(dict(authoring_packet)),
        base_state=state,
        accepted_claims=accepted_claims,
    )
    if "root" not in scope["writeScope"]["existingProgramIds"]:
        raise MathFlowError("joint serial local scope must authorize root synthesis")
    candidate = _validate_response(
        response,
        base_state=state,
        base_accounting_state=base_accounting,
        semantic_packet=packet,
        authoring_packet=scope,
    )
    subject = str(packet["subjectTransactionId"])
    if not isinstance(judgment_id, str) or not DIGEST.fullmatch(judgment_id):
        raise MathFlowError("joint serial transition needs an exact judgment digest")
    result_changes = {str(raw["id"]): raw for raw in packet["resultChanges"]}
    placements = {str(raw["resultId"]): raw for raw in candidate["resultPlacements"]}
    program_changes = {str(raw["programId"]): raw for raw in candidate["programChanges"]}

    memberships: dict[str, set[str]] = {
        str(program_id): set(program["intermediateResultIds"])
        for program_id, program in state["programs"].items()
    }
    for program_id in program_changes:
        memberships.setdefault(program_id, set())
    materialized_results: dict[str, dict[str, object]] = {}
    for result_id in sorted(result_changes):
        placement = placements[result_id]
        result = _materialize_result(
            result_changes[result_id],
            base_state=state,
            subject=subject,
            judgment_id=judgment_id,
            evidence_file_refs=evidence_file_refs,
            primary_program_id=str(placement["primaryProgramId"]),
            related_program_ids=list(placement["relatedProgramIds"]),
        )
        materialized_results[result_id] = result
        for program_id in [result["primaryProgramId"], *result["relatedProgramIds"]]:
            memberships[str(program_id)].add(result_id)

    content_operations: list[dict[str, object]] = []
    topology_operations: list[dict[str, object]] = []
    root = copy.deepcopy(state["programs"]["root"])
    root.pop("digest")
    root.update(copy.deepcopy(packet["rootUpdate"]))
    root["intermediateResultIds"] = sorted(memberships["root"])
    root["sourceTransactionIds"] = sorted({*root["sourceTransactionIds"], subject})
    content_operations.append(
        {
            "entityKind": "program",
            "entityId": "root",
            "baseDigest": state["programs"]["root"]["digest"],
            "value": root,
        }
    )

    for program_id in sorted(program_changes):
        raw = program_changes[program_id]
        action = str(raw["action"])
        if action == "move":
            existing = copy.deepcopy(state["programs"][program_id])
            existing.pop("digest")
            existing["parentId"] = raw["parentId"]
            topology_operations.append(
                {
                    "action": "move",
                    "entityKind": "program",
                    "entityId": program_id,
                    "baseDigest": state["programs"][program_id]["digest"],
                    "value": existing,
                }
            )
            continue
        existing = state["programs"].get(program_id)
        value = {
            "id": program_id,
            "parentId": raw["parentId"],
            "title": raw["title"],
            "objective": raw["objective"],
            "currentStateSummary": raw["currentStateSummary"],
            "localResidualSummary": raw["localResidualSummary"],
            "status": raw["status"],
            "intermediateResultIds": sorted(memberships[program_id]),
            "sourceTransactionIds": sorted(
                {
                    *(
                        existing["sourceTransactionIds"]
                        if isinstance(existing, Mapping)
                        else []
                    ),
                    subject,
                }
            ),
            "lineage": copy.deepcopy(existing["lineage"] if isinstance(existing, Mapping) else []),
        }
        operation = {
            "entityKind": "program",
            "entityId": program_id,
            "baseDigest": existing["digest"] if isinstance(existing, Mapping) else None,
            "value": value,
        }
        if action == "create":
            topology_operations.append({"action": "create", **operation})
        else:
            content_operations.append(operation)

    for result_id in sorted(materialized_results):
        raw = result_changes[result_id]
        existing = state["intermediateResults"].get(result_id)
        operation = {
            "entityKind": "intermediateResult",
            "entityId": result_id,
            "baseDigest": existing["digest"] if isinstance(existing, Mapping) else None,
            "value": materialized_results[result_id],
        }
        if raw["action"] == "create":
            topology_operations.append({"action": "create", **operation})
        else:
            content_operations.append(operation)

    direct_program_ids = sorted(
        {
            str(program_id)
            for result in materialized_results.values()
            for program_id in [result["primaryProgramId"], *result["relatedProgramIds"]]
        }
    )
    claim_keys = sorted(
        {str(key) for raw in result_changes.values() for key in raw["claimKeys"]}
    )
    basis = "local-objective" if len(direct_program_ids) == 1 else "cross-program"
    transition = {
        "schemaVersion": 1,
        "subjectTransactionId": subject,
        "baseStateDigest": state["stateDigest"],
        "contentOperations": content_operations,
        "topologyOperations": topology_operations,
        "contribution": {
            "claimKeys": claim_keys,
            "directProgramIds": direct_program_ids,
            "intermediateResultIds": sorted(materialized_results),
        },
        "placementAudit": {
            "basis": basis,
            "rationale": candidate["topologyRationale"]
            or "Existing accounting work packages and result identities are reused.",
            "relatedProgramIds": direct_program_ids,
        },
        "topologyRationale": candidate["topologyRationale"],
    }
    reduced = apply_research_builder_v10_transition(
        copy.deepcopy(state),
        transition,
        authoring_packet=scope,
        accepted_claims=accepted_claims,
        judgment_id=judgment_id,
        evidence_file_refs=evidence_file_refs,
    )
    post_state = reduced["postState"]
    for result_id, expected in materialized_results.items():
        if post_state["intermediateResults"].get(result_id) != {
            **expected,
            "digest": post_state["intermediateResults"][result_id]["digest"],
        }:
            raise MathFlowError("joint serial reducer changed fixed result semantics")
    if post_state["programs"]["root"]["currentStateSummary"] != packet["rootUpdate"]["currentStateSummary"]:
        raise MathFlowError("joint serial reducer changed fixed root synthesis")
    if post_state["programs"]["root"]["localResidualSummary"] != packet["rootUpdate"]["localResidualSummary"]:
        raise MathFlowError("joint serial reducer changed fixed root residual synthesis")

    base_annotations = {
        str(raw["nodeRef"]["id"]): raw
        for raw in base_accounting["annotations"]
        if raw["nodeRef"]["kind"] == "program"
    }
    moved_ids = {
        str(raw["programId"])
        for raw in candidate["programChanges"]
        if raw["action"] == "move"
    }
    updates: list[dict[str, object]] = []
    assessed_ids: set[str] = set()
    for assessment in candidate["withAccessAssessments"]:
        program_id = str(assessment["programId"])
        assessed_ids.add(program_id)
        base_annotation = base_annotations.get(program_id)
        direct = canonical_decimal(assessment["directWorkHours"], "joint serial direct work")
        incidence = assessment["conditionalIncidence"]
        normalized_incidence = (
            canonical_decimal(incidence, "joint serial conditional incidence")
            if incidence is not None
            else None
        )
        changes: dict[str, object] = {}
        if base_annotation is None or direct != base_annotation["directWorkHours"]:
            changes["directWorkHours"] = direct
        if program_id != "root" and (
            base_annotation is None
            or normalized_incidence != base_annotation["conditionalIncidence"]
            or program_id in moved_ids
        ):
            changes["conditionalIncidence"] = normalized_incidence
        if changes:
            updates.append(
                {
                    "nodeRef": {"kind": "program", "id": program_id},
                    "changes": changes,
                    "rationale": assessment["rationale"],
                    "evidenceRefs": list(assessment["evidenceRefs"]),
                }
            )
    patch = make_work_accounting_patch(
        problem_id=str(state["problemId"]),
        subject_transaction_id=subject,
        evaluation_mode="with-access",
        root_contract_digest=str(contract["rootContractDigest"]),
        base_accounting_state_digest=str(base_accounting["stateDigest"]),
        base_knowledge_state_digest=str(state["stateDigest"]),
        target_knowledge_state_digest=str(post_state["stateDigest"]),
        topology_alignment_digest=str(reduced["topologyAlignment"]["alignmentDigest"]),
        updates=updates,
    )
    patch = bind_patch_to_state(patch, base_accounting)
    with_access_state = apply_work_accounting_patch(
        base_accounting,
        patch,
        root_contract=contract,
        base_knowledge_state=state,
        target_knowledge_state=post_state,
        topology_alignment=reduced["topologyAlignment"],
    )
    after_annotations = {
        str(raw["nodeRef"]["id"]): raw for raw in with_access_state["annotations"]
    }
    for program_id, before in base_annotations.items():
        if program_id not in assessed_ids:
            after = after_annotations[program_id]
            if (
                before["directWorkHours"] != after["directWorkHours"]
                or before["conditionalIncidence"] != after["conditionalIncidence"]
            ):
                raise MathFlowError("joint serial transition changed an unassessed W+ primitive")
    return {
        "schemaVersion": 1,
        "implementation": IMPLEMENTATION,
        "response": candidate,
        "semanticPacket": packet,
        "authoringPacketDigest": scope["authoringPacketDigest"],
        "transition": transition,
        "postState": post_state,
        "topologyAlignment": reduced["topologyAlignment"],
        "sameWorldHandoff": reduced["sameWorldHandoff"],
        "withAccessPatch": patch,
        "withAccessState": with_access_state,
    }


__all__ = [
    "IMPLEMENTATION",
    "evidence_manifest_digest",
    "joint_portfolio_serial_response_schema_v1",
    "make_joint_portfolio_semantic_packet_v1",
    "reduce_joint_portfolio_serial_transition_v1",
    "validate_joint_portfolio_semantic_packet_v1",
]
