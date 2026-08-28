"""Versioned knowledge-state boundary used by work accounting.

Research builders own their state, alignment, and handoff formats.  Work
accounting consumes those artifacts but must keep already-published builder-v6
and work-projection bundles replayable.  This module is the deliberately small
dispatch seam between the legacy program/thread/item state and the additive
program/intermediate-result state.
"""

from __future__ import annotations

from collections.abc import Mapping

from .errors import MathFlowError
from .research_builder_v6 import (
    apply_research_builder_v6_transition,
    validate_research_builder_v6_handoff,
)
from .research_builder_v7 import (
    apply_research_builder_v7_transition,
    derive_research_topology_alignment_v2,
    validate_research_builder_v7_handoff,
    validate_research_program_state_v3,
    validate_research_topology_alignment_v2,
)
from .research_topology import (
    derive_research_topology_alignment,
    validate_research_program_state_versioned,
    validate_research_topology_alignment,
)


def knowledge_schema_version(value: object) -> int:
    if not isinstance(value, Mapping):
        raise MathFlowError("work accounting knowledge state must be an object")
    version = value.get("schemaVersion")
    if isinstance(version, bool) or not isinstance(version, int):
        raise MathFlowError("work accounting knowledge state has an invalid version")
    return version


def validate_work_accounting_knowledge_state(
    value: object, problem: str | None = None
) -> dict[str, object]:
    if knowledge_schema_version(value) == 3:
        return validate_research_program_state_v3(value, problem)
    return validate_research_program_state_versioned(value, problem)


def _matching_versions(
    before_state: object, after_state: object
) -> tuple[dict[str, object], dict[str, object], int]:
    before = validate_work_accounting_knowledge_state(before_state)
    after = validate_work_accounting_knowledge_state(
        after_state, str(before["problemId"])
    )
    version = knowledge_schema_version(before)
    if knowledge_schema_version(after) != version:
        raise MathFlowError("work accounting may not cross knowledge-state versions")
    return before, after, version


def derive_work_accounting_topology_alignment(
    before_state: object, after_state: object
) -> dict[str, object]:
    before, after, version = _matching_versions(before_state, after_state)
    if version == 3:
        return derive_research_topology_alignment_v2(before, after)
    return derive_research_topology_alignment(before, after)


def validate_work_accounting_topology_alignment(
    alignment: object,
    before_state: object,
    after_state: object,
) -> dict[str, object]:
    before, after, version = _matching_versions(before_state, after_state)
    if version == 3:
        return validate_research_topology_alignment_v2(alignment, before, after)
    return validate_research_topology_alignment(alignment, before, after)


def apply_work_accounting_builder_transition(
    base_state: dict[str, object],
    transition: object,
    *,
    accepted_claims: object,
    judgment_id: str,
) -> dict[str, object]:
    base = validate_work_accounting_knowledge_state(base_state)
    if knowledge_schema_version(base) == 3:
        return apply_research_builder_v7_transition(
            base,
            transition,
            accepted_claims=accepted_claims,
            judgment_id=judgment_id,
        )
    return apply_research_builder_v6_transition(
        base,
        transition,
        accepted_claims=accepted_claims,
        judgment_id=judgment_id,
    )


def validate_work_accounting_builder_handoff(
    handoff: object,
    before_state: object,
    after_state: object,
    alignment: object,
    subject_transaction_id: str,
) -> dict[str, object]:
    before, after, version = _matching_versions(before_state, after_state)
    if version == 3:
        if not isinstance(alignment, dict):
            raise MathFlowError("work accounting topology alignment must be an object")
        return validate_research_builder_v7_handoff(
            handoff,
            before,
            after,
            alignment,
            subject_transaction_id,
        )
    if not isinstance(alignment, dict):
        raise MathFlowError("work accounting topology alignment must be an object")
    return validate_research_builder_v6_handoff(
        handoff,
        before,
        after,
        alignment,
        subject_transaction_id,
    )
