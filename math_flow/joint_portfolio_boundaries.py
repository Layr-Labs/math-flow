"""Cumulative accounting work-policy boundaries for joint portfolio states."""

from __future__ import annotations

import copy
import re
from collections.abc import Mapping, Sequence

from math_flow.counterfactual_context import validate_impact_subgraph_context
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
NO_ACCESS_POLICY_FIELDS = {
    "programId",
    "parentProgramId",
    "source",
    "baseBoundaryDigest",
    "baseKnowledgeNodeDigest",
    "targetKnowledgeNodeDigest",
    *BOUNDARY_TEXT_FIELDS,
    "policyDigest",
}
NO_ACCESS_CONTEXT_FIELDS = {
    "schemaVersion",
    "problemId",
    "subjectTransactionId",
    "baseBoundaryStateDigest",
    "baseKnowledgeStateDigest",
    "targetKnowledgeStateDigest",
    "impactContextDigest",
    "programPolicies",
    "contextDigest",
}
SANITIZED_NEW_POLICY = {
    "directResidualWorkScope": (
        "Estimate only direct residual work local to this newly represented target package "
        "under the no-access counterfactual."
    ),
    "activationCondition": (
        "Activate this target package only if the reference portfolio would include it "
        "without access to the subject submission."
    ),
    "stoppingCondition": (
        "Stop when the independently included counterfactual package is completed, "
        "superseded, or pruned."
    ),
    "independentVariationRationale": (
        "No pre-contribution boundary exists for this target-only package; vary its "
        "inclusion and residual work independently using only the supplied topology and safe facts."
    ),
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


def _local_program_ids(impact_context: Mapping[str, object]) -> list[str]:
    ids: set[str] = set()
    for raw in impact_context["includedNodes"]:
        ref = raw["ref"]
        if ref["kind"] != "program":
            raise MathFlowError("joint no-access policy context supports program nodes only")
        ids.add(str(ref["id"]))
    for raw in impact_context["boundarySummaries"]:
        ref = raw["nodeRef"]
        if ref["kind"] != "program":
            raise MathFlowError("joint no-access policy boundary supports program nodes only")
        ids.add(str(ref["id"]))
    return sorted(ids)


def validate_joint_portfolio_no_access_policy_context_envelope_v1(
    value: object,
) -> dict[str, object]:
    if not isinstance(value, dict) or set(value) != NO_ACCESS_CONTEXT_FIELDS:
        raise MathFlowError("joint no-access work-policy context has an invalid envelope")
    if value.get("schemaVersion") != 1:
        raise MathFlowError("joint no-access work-policy context has an invalid version")
    if not isinstance(value.get("problemId"), str) or not value["problemId"]:
        raise MathFlowError("joint no-access work-policy context has an invalid problem")
    subject = value.get("subjectTransactionId")
    if not isinstance(subject, str) or not TRANSACTION.fullmatch(subject):
        raise MathFlowError("joint no-access work-policy context has an invalid subject")
    for field in (
        "baseBoundaryStateDigest",
        "baseKnowledgeStateDigest",
        "targetKnowledgeStateDigest",
        "impactContextDigest",
        "contextDigest",
    ):
        if not isinstance(value.get(field), str) or not DIGEST.fullmatch(str(value[field])):
            raise MathFlowError(f"joint no-access work-policy context has an invalid {field}")
    policies = value.get("programPolicies")
    if not isinstance(policies, list) or not policies:
        raise MathFlowError("joint no-access work-policy context needs local policies")
    ids: list[str] = []
    for raw in policies:
        if not isinstance(raw, dict) or set(raw) != NO_ACCESS_POLICY_FIELDS:
            raise MathFlowError("joint no-access work-policy row has invalid fields")
        program_id = raw.get("programId")
        if not isinstance(program_id, str) or not program_id:
            raise MathFlowError("joint no-access work-policy row has an invalid program")
        ids.append(program_id)
        parent = raw.get("parentProgramId")
        if parent is not None and (not isinstance(parent, str) or not parent):
            raise MathFlowError("joint no-access work-policy row has an invalid parent")
        source = raw.get("source")
        if source not in {"pre-contribution-boundary", "sanitized-new-target-package"}:
            raise MathFlowError("joint no-access work-policy row has an invalid source")
        base_boundary = raw.get("baseBoundaryDigest")
        base_node = raw.get("baseKnowledgeNodeDigest")
        if source == "pre-contribution-boundary":
            if not isinstance(base_boundary, str) or not DIGEST.fullmatch(base_boundary):
                raise MathFlowError("joint no-access prior policy lacks its boundary digest")
            if not isinstance(base_node, str) or not DIGEST.fullmatch(base_node):
                raise MathFlowError("joint no-access prior policy lacks its node digest")
        elif base_boundary is not None or base_node is not None:
            raise MathFlowError("joint no-access sanitized policy invents a prior boundary")
        target_node = raw.get("targetKnowledgeNodeDigest")
        if not isinstance(target_node, str) or not DIGEST.fullmatch(target_node):
            raise MathFlowError("joint no-access work-policy row lacks its target node digest")
        for field in BOUNDARY_TEXT_FIELDS:
            _require_text(raw.get(field), f"joint no-access work-policy {field}")
        core = {key: copy.deepcopy(item) for key, item in raw.items() if key != "policyDigest"}
        if raw.get("policyDigest") != _digest(core):
            raise MathFlowError("joint no-access work-policy row digest mismatch")
        if source == "sanitized-new-target-package" and any(
            raw[field] != SANITIZED_NEW_POLICY[field] for field in BOUNDARY_TEXT_FIELDS
        ):
            raise MathFlowError("joint no-access target-only policy is not sanitized")
    if ids != sorted(set(ids)):
        raise MathFlowError("joint no-access work-policy rows are not canonical")
    core = {key: copy.deepcopy(item) for key, item in value.items() if key != "contextDigest"}
    if value.get("contextDigest") != _digest(core):
        raise MathFlowError("joint no-access work-policy context digest mismatch")
    return copy.deepcopy(value)


def build_joint_portfolio_no_access_policy_context_v1(
    *,
    base_boundary_state: Mapping[str, object],
    base_knowledge_state: Mapping[str, object],
    target_knowledge_state: Mapping[str, object],
    impact_context: Mapping[str, object],
) -> dict[str, object]:
    """Expose only prior local policy plus generic policy for target-only packages."""

    before = validate_research_program_state_v3(copy.deepcopy(dict(base_knowledge_state)))
    after = validate_research_program_state_v3(copy.deepcopy(dict(target_knowledge_state)))
    base = validate_joint_portfolio_boundary_state_v1(base_boundary_state, before)
    impact = validate_impact_subgraph_context(copy.deepcopy(dict(impact_context)))
    if (
        before["problemId"] != after["problemId"]
        or impact["problemId"] != after["problemId"]
        or impact["knowledgeStateDigest"] != after["stateDigest"]
        or impact["subjectTransactionId"] != after["ledgerHead"]
    ):
        raise MathFlowError("joint no-access work-policy context has stale state bindings")
    prior = {str(row["programId"]): row for row in base["boundaries"]}
    policies: list[dict[str, object]] = []
    for program_id in _local_program_ids(impact):
        target = after["programs"].get(program_id)
        if not isinstance(target, dict):
            raise MathFlowError("joint no-access policy names a missing target program")
        old = prior.get(program_id)
        if old is None:
            source = "sanitized-new-target-package"
            text = SANITIZED_NEW_POLICY
            base_boundary_digest = None
            base_node_digest = None
        else:
            source = "pre-contribution-boundary"
            text = old
            base_boundary_digest = old["boundaryDigest"]
            base_node_digest = old["knowledgeNodeDigest"]
        row_core = {
            "programId": program_id,
            "parentProgramId": target["parentId"],
            "source": source,
            "baseBoundaryDigest": base_boundary_digest,
            "baseKnowledgeNodeDigest": base_node_digest,
            "targetKnowledgeNodeDigest": target["digest"],
            **{field: text[field] for field in sorted(BOUNDARY_TEXT_FIELDS)},
        }
        policies.append({**row_core, "policyDigest": _digest(row_core)})
    core = {
        "schemaVersion": 1,
        "problemId": before["problemId"],
        "subjectTransactionId": after["ledgerHead"],
        "baseBoundaryStateDigest": base["stateDigest"],
        "baseKnowledgeStateDigest": before["stateDigest"],
        "targetKnowledgeStateDigest": after["stateDigest"],
        "impactContextDigest": impact["contextDigest"],
        "programPolicies": policies,
    }
    return validate_joint_portfolio_no_access_policy_context_envelope_v1(
        {**core, "contextDigest": _digest(core)}
    )


def validate_joint_portfolio_no_access_policy_context_v1(
    value: object,
    *,
    base_boundary_state: Mapping[str, object],
    base_knowledge_state: Mapping[str, object],
    target_knowledge_state: Mapping[str, object],
    impact_context: Mapping[str, object],
) -> dict[str, object]:
    context = validate_joint_portfolio_no_access_policy_context_envelope_v1(value)
    expected = build_joint_portfolio_no_access_policy_context_v1(
        base_boundary_state=base_boundary_state,
        base_knowledge_state=base_knowledge_state,
        target_knowledge_state=target_knowledge_state,
        impact_context=impact_context,
    )
    if context != expected:
        raise MathFlowError("joint no-access work-policy context is not reproducible")
    return context


__all__ = [
    "BOUNDARY_TEXT_FIELDS",
    "SANITIZED_NEW_POLICY",
    "advance_joint_portfolio_boundary_state_v1",
    "build_joint_portfolio_no_access_policy_context_v1",
    "make_joint_portfolio_boundary_state_v1",
    "validate_joint_portfolio_no_access_policy_context_envelope_v1",
    "validate_joint_portfolio_no_access_policy_context_v1",
    "validate_joint_portfolio_boundary_state_v1",
]
