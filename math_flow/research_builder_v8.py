from __future__ import annotations

from collections.abc import Mapping

from .errors import MathFlowError
from .research_builder_v7 import apply_research_builder_v7_transition


def _artifact_pairs(value: object) -> set[tuple[str, str]]:
    if not isinstance(value, list):
        return set()
    return {
        (str(item["path"]), str(item["digest"]))
        for item in value
        if isinstance(item, dict)
        and isinstance(item.get("path"), str)
        and isinstance(item.get("digest"), str)
    }


def _linked_program_ids(result: object) -> set[str]:
    if not isinstance(result, dict):
        return set()
    linked: set[str] = set()
    primary = result.get("primaryProgramId")
    if isinstance(primary, str):
        linked.add(primary)
    related = result.get("relatedProgramIds")
    if isinstance(related, list):
        linked.update(str(item) for item in related if isinstance(item, str))
    return linked


def _ancestors(state: Mapping[str, object], program_id: str) -> set[str]:
    programs = state.get("programs")
    if not isinstance(programs, dict) or program_id not in programs:
        return set()
    result: set[str] = set()
    cursor: str | None = program_id
    while cursor is not None:
        if cursor in result:
            raise MathFlowError("research builder v8 program ancestry contains a cycle")
        result.add(cursor)
        program = programs.get(cursor)
        if not isinstance(program, dict):
            break
        parent = program.get("parentId")
        cursor = str(parent) if isinstance(parent, str) else None
    return result


def _validate_evidence_and_program_refresh(
    base_state: Mapping[str, object],
    transition: Mapping[str, object],
    post_state: Mapping[str, object],
    *,
    evidence_file_refs: Mapping[str, str],
) -> None:
    subject = transition.get("subjectTransactionId")
    if not isinstance(subject, str):
        raise MathFlowError("research builder v8 transition has no subject")
    if not evidence_file_refs or any(
        not isinstance(path, str) or not isinstance(digest, str)
        for path, digest in evidence_file_refs.items()
    ):
        raise MathFlowError("research builder v8 needs exact submission evidence refs")
    exact_current_artifacts = set(evidence_file_refs.items())

    base_results = base_state.get("intermediateResults")
    post_results = post_state.get("intermediateResults")
    post_programs = post_state.get("programs")
    if not isinstance(base_results, dict) or not isinstance(post_results, dict):
        raise MathFlowError("research builder v8 requires two-entity research states")
    if not isinstance(post_programs, dict):
        raise MathFlowError("research builder v8 post-state has no programs")

    contribution = transition.get("contribution")
    if not isinstance(contribution, dict):
        raise MathFlowError("research builder v8 transition has no contribution")
    result_ids = contribution.get("intermediateResultIds")
    direct_program_ids = contribution.get("directProgramIds")
    if not isinstance(result_ids, list) or not isinstance(direct_program_ids, list):
        raise MathFlowError("research builder v8 contribution is incomplete")

    impacted_program_ids = {
        str(item) for item in direct_program_ids if isinstance(item, str)
    }
    for result_id in result_ids:
        result = post_results.get(result_id)
        if not isinstance(result, dict):
            raise MathFlowError("research builder v8 contribution result is missing")
        support = result.get("support")
        refs = _artifact_pairs(
            support.get("artifactRefs") if isinstance(support, dict) else None
        )
        if not refs & exact_current_artifacts:
            raise MathFlowError(
                "research builder v8 subject result must cite an exact current "
                f"submission artifact: {result_id}"
            )
        impacted_program_ids.update(_linked_program_ids(result))
        impacted_program_ids.update(
            _linked_program_ids(base_results.get(result_id))
        )

    operations: list[object] = []
    for field in ("contentOperations", "topologyOperations"):
        raw_operations = transition.get(field)
        if isinstance(raw_operations, list):
            operations.extend(raw_operations)
    operated_programs: set[str] = set()
    for operation in operations:
        if not isinstance(operation, dict):
            continue
        entity_id = operation.get("entityId")
        value = operation.get("value")
        if operation.get("entityKind") == "program" and isinstance(entity_id, str):
            operated_programs.add(entity_id)
            if isinstance(value, dict):
                parent = value.get("parentId")
                if isinstance(parent, str):
                    impacted_program_ids.add(parent)
            base_programs = base_state.get("programs")
            prior = (
                base_programs.get(entity_id)
                if isinstance(base_programs, dict)
                else None
            )
            if isinstance(prior, dict) and isinstance(prior.get("parentId"), str):
                impacted_program_ids.add(str(prior["parentId"]))
            impacted_program_ids.add(entity_id)
        elif operation.get("entityKind") == "intermediateResult":
            impacted_program_ids.update(_linked_program_ids(value))
            if isinstance(entity_id, str):
                prior = base_results.get(entity_id)
                impacted_program_ids.update(_linked_program_ids(prior))
                after = post_results.get(entity_id)
                if isinstance(after, dict):
                    support = after.get("support")
                    after_refs = _artifact_pairs(
                        support.get("artifactRefs")
                        if isinstance(support, dict)
                        else None
                    )
                    prior_support = prior.get("support") if isinstance(prior, dict) else None
                    prior_refs = _artifact_pairs(
                        prior_support.get("artifactRefs")
                        if isinstance(prior_support, dict)
                        else None
                    )
                    if not (after_refs - prior_refs) <= exact_current_artifacts:
                        raise MathFlowError(
                            "research builder v8 introduced an artifact that is not "
                            "bound by the current evidence manifest"
                        )

    refresh_required: set[str] = set()
    for program_id in impacted_program_ids:
        refresh_required.update(_ancestors(base_state, program_id))
        refresh_required.update(_ancestors(post_state, program_id))
    base_programs = base_state.get("programs")
    if not isinstance(base_programs, dict):
        raise MathFlowError("research builder v8 base-state has no programs")
    refresh_required &= set(base_programs)
    missing = sorted(refresh_required - operated_programs)
    if missing:
        raise MathFlowError(
            "research builder v8 must refresh every affected existing program and "
            f"ancestor: {missing[0]}"
        )
    for program_id in refresh_required:
        program = post_programs.get(program_id)
        sources = program.get("sourceTransactionIds") if isinstance(program, dict) else None
        if not isinstance(sources, list) or subject not in sources:
            raise MathFlowError(
                "research builder v8 affected program refresh must cite the current "
                f"submission: {program_id}"
            )


def apply_research_builder_v8_transition(
    base_state: dict[str, object],
    transition: dict[str, object],
    *,
    accepted_claims: object,
    judgment_id: str,
    evidence_file_refs: Mapping[str, str],
) -> dict[str, object]:
    """Apply the state-v3 reducer plus Builder V8 context-integrity checks."""

    reduced = apply_research_builder_v7_transition(
        base_state,
        transition,
        accepted_claims=accepted_claims,
        judgment_id=judgment_id,
    )
    _validate_evidence_and_program_refresh(
        base_state,
        transition,
        reduced["postState"],
        evidence_file_refs=evidence_file_refs,
    )
    return reduced


__all__ = ["apply_research_builder_v8_transition"]
