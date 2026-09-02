"""Inactive additive V11 adapter for terminal joint-portfolio lifecycle states.

The active V7 placement audit requires every directly credited non-root program
to remain active. A joint knowledge/W+ transition must also represent the
submission that completes or retires its own work package. V11 validates an
active shadow through the unchanged V10 reducer, then applies only the already
validated terminal lifecycle fields in trusted code and recomputes all digests,
alignment, and handoff.
"""

from __future__ import annotations

import copy
from collections.abc import Mapping

from math_flow.errors import MathFlowError
from math_flow.research_builder_v7 import (
    _normalize_program,
    _normalize_result,
    _same_world_handoff,
    _with_state_digest,
    derive_research_topology_alignment_v2,
    validate_research_builder_v7_handoff,
    validate_research_program_state_v3,
)
from math_flow.research_builder_v10 import apply_research_builder_v10_transition


def _terminalize(
    state: Mapping[str, object],
    *,
    program_statuses: Mapping[str, str],
    result_statuses: Mapping[str, str],
) -> dict[str, object]:
    result = copy.deepcopy(dict(state))
    result.pop("stateDigest", None)
    for program_id, status in sorted(program_statuses.items()):
        if status not in {"completed", "retired"}:
            raise MathFlowError("joint V11 terminal program status is invalid")
        existing = result["programs"].get(program_id)
        if not isinstance(existing, dict) or program_id == "root":
            raise MathFlowError("joint V11 terminal program is invalid")
        value = copy.deepcopy(existing)
        value.pop("digest")
        value["status"] = status
        result["programs"][program_id] = _normalize_program(program_id, value)
    for result_id, status in sorted(result_statuses.items()):
        if status != "retired":
            raise MathFlowError("joint V11 terminal result status is invalid")
        existing = result["intermediateResults"].get(result_id)
        if not isinstance(existing, dict):
            raise MathFlowError("joint V11 terminal result is invalid")
        value = copy.deepcopy(existing)
        value.pop("digest")
        value["status"] = status
        result["intermediateResults"][result_id] = _normalize_result(result_id, value)
    sealed = _with_state_digest(result)
    return validate_research_program_state_v3(sealed)


def _active_shadow(
    transition: Mapping[str, object],
    *,
    subject: str,
    program_statuses: Mapping[str, str],
    result_statuses: Mapping[str, str],
) -> dict[str, object]:
    shadow = copy.deepcopy(dict(transition))
    content = list(shadow["contentOperations"])
    topology: list[dict[str, object]] = []
    seen = {
        (str(raw["entityKind"]), str(raw["entityId"]))
        for raw in content
        if isinstance(raw, dict)
    }
    for raw in list(shadow["topologyOperations"]):
        if not isinstance(raw, dict):
            raise MathFlowError("joint V11 topology operation is invalid")
        key = (str(raw["entityKind"]), str(raw["entityId"]))
        terminal = (
            key[0] == "program" and key[1] in program_statuses
        ) or (
            key[0] == "intermediateResult" and key[1] in result_statuses
        )
        if not terminal:
            topology.append(raw)
            continue
        if raw.get("action") != "retire" or key in seen:
            raise MathFlowError("joint V11 terminal lifecycle operation is inconsistent")
        value = copy.deepcopy(raw["value"])
        value["status"] = "active"
        if key[0] == "program":
            value["sourceTransactionIds"] = sorted(
                {*map(str, value["sourceTransactionIds"]), subject}
            )
        content.append(
            {
                "entityKind": key[0],
                "entityId": key[1],
                "baseDigest": raw["baseDigest"],
                "value": value,
            }
        )
        seen.add(key)
    for raw in content:
        if not isinstance(raw, dict):
            raise MathFlowError("joint V11 content operation is invalid")
        if raw.get("entityKind") == "program" and raw.get("entityId") in program_statuses:
            raw["value"]["status"] = "active"
    shadow["contentOperations"] = content
    shadow["topologyOperations"] = topology
    shadow["topologyRationale"] = (
        transition.get("topologyRationale") if topology else None
    )
    return shadow


def apply_research_builder_joint_v11_transition(
    base_state: Mapping[str, object],
    transition: Mapping[str, object],
    *,
    authoring_packet: Mapping[str, object],
    accepted_claims: object,
    judgment_id: str,
    evidence_file_refs: Mapping[str, str],
    final_program_statuses: Mapping[str, str],
    final_result_statuses: Mapping[str, str],
) -> dict[str, object]:
    """Apply one V10-scoped transition with explicit terminal lifecycle state."""

    before = validate_research_program_state_v3(copy.deepcopy(dict(base_state)))
    subject = transition.get("subjectTransactionId")
    if not isinstance(subject, str):
        raise MathFlowError("joint V11 transition has an invalid subject")
    shadow = _active_shadow(
        transition,
        subject=subject,
        program_statuses=final_program_statuses,
        result_statuses=final_result_statuses,
    )
    reduced = apply_research_builder_v10_transition(
        before,
        shadow,
        authoring_packet=authoring_packet,
        accepted_claims=accepted_claims,
        judgment_id=judgment_id,
        evidence_file_refs=evidence_file_refs,
    )
    post = _terminalize(
        reduced["postState"],
        program_statuses=final_program_statuses,
        result_statuses=final_result_statuses,
    )
    contribution = post["contributions"][subject]
    mapped = {
        str(program_id)
        for result_id in contribution["intermediateResultIds"]
        for program_id in [
            post["intermediateResults"][result_id]["primaryProgramId"],
            *post["intermediateResults"][result_id]["relatedProgramIds"],
        ]
    }
    if mapped != set(contribution["directProgramIds"]):
        raise MathFlowError("joint V11 terminal contribution placement drifted")
    alignment = derive_research_topology_alignment_v2(before, post)
    handoff = _same_world_handoff(subject, before, post, alignment)
    validate_research_builder_v7_handoff(handoff, before, post, alignment, subject)
    return {
        "subjectTransactionId": subject,
        "postState": post,
        "topologyAlignment": alignment,
        "sameWorldHandoff": handoff,
        "authoringPacketDigest": reduced["authoringPacketDigest"],
        "validationShadowStateDigest": reduced["postState"]["stateDigest"],
    }


__all__ = ["apply_research_builder_joint_v11_transition"]
