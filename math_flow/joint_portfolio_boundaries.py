"""Cumulative accounting work-policy boundaries for joint portfolio states."""

from __future__ import annotations

import copy
import re
from collections.abc import Mapping, Sequence

from math_flow.errors import MathFlowError
from math_flow.repository import sha256_json
from math_flow.research_builder_v7 import validate_research_program_state_v3


DIGEST = re.compile(r"^sha256:[0-9a-f]{64}$")
TRANSACTION = re.compile(r"^[0-9a-f]{40}$")
BOUNDARY_TEXT_FIELDS = {
    "directResidualWorkScope",
    "activationCondition",
    "stoppingCondition",
    "independentVariationRationale",
}
BOUNDARY_FIELDS = {
    "programId",
    "knowledgeNodeDigest",
    *BOUNDARY_TEXT_FIELDS,
    "boundaryDigest",
}
STATE_FIELDS = {
    "schemaVersion",
    "problemId",
    "knowledgeStateDigest",
    "knowledgeLedgerHead",
    "boundaries",
    "stateDigest",
}


def _digest(value: object) -> str:
    return f"sha256:{sha256_json(copy.deepcopy(value))}"


def _require_text(value: object, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise MathFlowError(f"{label} must be non-empty text")
    return value


def _seal_boundary(
    program_id: str,
    node_digest: str,
    raw: Mapping[str, object],
) -> dict[str, object]:
    if set(raw) not in (BOUNDARY_TEXT_FIELDS, BOUNDARY_TEXT_FIELDS | {"programId"}):
        raise MathFlowError("joint portfolio boundary has invalid fields")
    if "programId" in raw and raw.get("programId") != program_id:
        raise MathFlowError("joint portfolio boundary names another program")
    core = {
        "programId": program_id,
        "knowledgeNodeDigest": node_digest,
        **{
            field: _require_text(raw.get(field), f"joint portfolio boundary {field}")
            for field in sorted(BOUNDARY_TEXT_FIELDS)
        },
    }
    return {**core, "boundaryDigest": _digest(core)}


def make_joint_portfolio_boundary_state_v1(
    *,
    knowledge_state: Mapping[str, object],
    boundaries: Sequence[Mapping[str, object]],
) -> dict[str, object]:
    """Seal exactly one boundary for every program in a knowledge state."""

    state = validate_research_program_state_v3(copy.deepcopy(dict(knowledge_state)))
    by_id: dict[str, Mapping[str, object]] = {}
    for raw in boundaries:
        if not isinstance(raw, Mapping):
            raise MathFlowError("joint portfolio boundaries must be objects")
        program_id = raw.get("programId")
        if not isinstance(program_id, str) or program_id in by_id:
            raise MathFlowError("joint portfolio boundary IDs must be unique")
        by_id[program_id] = raw
    if set(by_id) != set(state["programs"]):
        raise MathFlowError("joint portfolio boundaries must cover every program exactly")
    rows = [
        _seal_boundary(
            program_id,
            str(state["programs"][program_id]["digest"]),
            by_id[program_id],
        )
        for program_id in sorted(by_id)
    ]
    core = {
        "schemaVersion": 1,
        "problemId": state["problemId"],
        "knowledgeStateDigest": state["stateDigest"],
        "knowledgeLedgerHead": state["ledgerHead"],
        "boundaries": rows,
    }
    return {**core, "stateDigest": _digest(core)}


def validate_joint_portfolio_boundary_state_v1(
    value: object,
    knowledge_state: Mapping[str, object],
) -> dict[str, object]:
    state = validate_research_program_state_v3(copy.deepcopy(dict(knowledge_state)))
    if not isinstance(value, dict) or set(value) != STATE_FIELDS:
        raise MathFlowError("joint portfolio boundary state has an invalid envelope")
    if value.get("schemaVersion") != 1 or value.get("problemId") != state["problemId"]:
        raise MathFlowError("joint portfolio boundary state belongs to another protocol")
    if value.get("knowledgeStateDigest") != state["stateDigest"]:
        raise MathFlowError("joint portfolio boundary state has a stale knowledge binding")
    if value.get("knowledgeLedgerHead") != state["ledgerHead"]:
        raise MathFlowError("joint portfolio boundary state has a stale ledger binding")
    rows = value.get("boundaries")
    if not isinstance(rows, list):
        raise MathFlowError("joint portfolio boundary state boundaries must be an array")
    raw_text: list[dict[str, object]] = []
    ids: list[str] = []
    for raw in rows:
        if not isinstance(raw, dict) or set(raw) != BOUNDARY_FIELDS:
            raise MathFlowError("joint portfolio boundary state row is invalid")
        program_id = raw.get("programId")
        if not isinstance(program_id, str) or program_id not in state["programs"]:
            raise MathFlowError("joint portfolio boundary state names an unknown program")
        ids.append(program_id)
        if raw.get("knowledgeNodeDigest") != state["programs"][program_id]["digest"]:
            raise MathFlowError("joint portfolio boundary node binding is stale")
        expected = _seal_boundary(
            program_id,
            str(raw["knowledgeNodeDigest"]),
            {field: raw[field] for field in BOUNDARY_TEXT_FIELDS},
        )
        if raw != expected:
            raise MathFlowError("joint portfolio boundary digest mismatch")
        raw_text.append({"programId": program_id, **{field: raw[field] for field in BOUNDARY_TEXT_FIELDS}})
    if ids != sorted(set(ids)) or set(ids) != set(state["programs"]):
        raise MathFlowError("joint portfolio boundary state coverage is invalid")
    expected_state = make_joint_portfolio_boundary_state_v1(
        knowledge_state=state,
        boundaries=raw_text,
    )
    if value != expected_state:
        raise MathFlowError("joint portfolio boundary state digest mismatch")
    return copy.deepcopy(value)


def advance_joint_portfolio_boundary_state_v1(
    *,
    base_boundary_state: Mapping[str, object],
    base_knowledge_state: Mapping[str, object],
    target_knowledge_state: Mapping[str, object],
    updated_boundaries: Sequence[Mapping[str, object]],
    required_program_ids: Sequence[str],
) -> dict[str, object]:
    """Carry unaffected boundary text and replace every required local boundary."""

    before = validate_research_program_state_v3(copy.deepcopy(dict(base_knowledge_state)))
    after = validate_research_program_state_v3(copy.deepcopy(dict(target_knowledge_state)))
    base = validate_joint_portfolio_boundary_state_v1(base_boundary_state, before)
    if before["problemId"] != after["problemId"]:
        raise MathFlowError("joint portfolio boundary transition crosses problems")
    required = list(required_program_ids)
    if required != sorted(set(required)) or not set(required) <= set(after["programs"]):
        raise MathFlowError("joint portfolio required boundary set is invalid")
    updates: dict[str, Mapping[str, object]] = {}
    for raw in updated_boundaries:
        if not isinstance(raw, Mapping):
            raise MathFlowError("joint portfolio boundary update is invalid")
        program_id = raw.get("programId")
        if not isinstance(program_id, str) or program_id in updates:
            raise MathFlowError("joint portfolio boundary updates must be unique")
        updates[program_id] = raw
    if list(updates) != required:
        raise MathFlowError("joint portfolio boundary updates must cover the affected set")
    prior = {str(row["programId"]): row for row in base["boundaries"]}
    materialized: list[dict[str, object]] = []
    for program_id in sorted(after["programs"]):
        source = updates.get(program_id) or prior.get(program_id)
        if source is None:
            raise MathFlowError("new joint portfolio program lacks a boundary")
        materialized.append(
            {"programId": program_id, **{field: source[field] for field in BOUNDARY_TEXT_FIELDS}}
        )
    return make_joint_portfolio_boundary_state_v1(
        knowledge_state=after,
        boundaries=materialized,
    )


__all__ = [
    "BOUNDARY_TEXT_FIELDS",
    "advance_joint_portfolio_boundary_state_v1",
    "make_joint_portfolio_boundary_state_v1",
    "validate_joint_portfolio_boundary_state_v1",
]
