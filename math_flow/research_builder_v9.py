from __future__ import annotations

import copy
from collections.abc import Mapping

from .errors import MathFlowError
from .repository import sha256_json
from .research_builder_v7 import validate_research_program_state_v3
from .research_builder_v8 import apply_research_builder_v8_transition


CONTEXT_FIELDS = {
    "schemaVersion",
    "problemId",
    "baseStateDigest",
    "rootProgramId",
    "dependencyTransactionIds",
    "supportLoadedResultIds",
    "supportOmittedResultIds",
    "programs",
    "intermediateResults",
    "contextDigest",
}
PROGRAM_CONTEXT_FIELDS = {
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
}
RESULT_CONTEXT_FIELDS = {
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
}
SUPPORT_CONTEXT_FIELDS = {
    "proofs",
    "methods",
    "computations",
    "tools",
    "artifactPaths",
    "attestationRefs",
}


def _context_digest(value: Mapping[str, object]) -> str:
    core = {key: copy.deepcopy(item) for key, item in value.items() if key != "contextDigest"}
    return f"sha256:{sha256_json(core)}"


def _dependency_transaction_ids(accepted_claims: object) -> list[str]:
    if not isinstance(accepted_claims, list) or not accepted_claims:
        raise MathFlowError("research builder v9 context needs accepted claims")
    dependencies: set[str] = set()
    for claim in accepted_claims:
        raw = claim.get("dependencyTransactionIds") if isinstance(claim, dict) else None
        if not isinstance(raw, list) or any(not isinstance(item, str) for item in raw):
            raise MathFlowError("research builder v9 claim dependencies are invalid")
        dependencies.update(raw)
    return sorted(dependencies)


def _loaded_result_ids(
    base_state: Mapping[str, object], dependency_transaction_ids: list[str]
) -> set[str]:
    contributions = base_state.get("contributions")
    results = base_state.get("intermediateResults")
    if not isinstance(contributions, dict) or not isinstance(results, dict):
        raise MathFlowError("research builder v9 context requires a two-entity state")
    loaded: set[str] = set()
    pending: list[str] = []
    for transaction_id in dependency_transaction_ids:
        contribution = contributions.get(transaction_id)
        if not isinstance(contribution, dict):
            raise MathFlowError(
                "research builder v9 dependency is absent from the predecessor: "
                f"{transaction_id}"
            )
        result_ids = contribution.get("intermediateResultIds")
        if not isinstance(result_ids, list):
            raise MathFlowError("research builder v9 contribution mapping is invalid")
        pending.extend(str(item) for item in result_ids)
    while pending:
        result_id = pending.pop()
        if result_id in loaded:
            continue
        result = results.get(result_id)
        if not isinstance(result, dict):
            raise MathFlowError(
                "research builder v9 dependency result is absent: " + result_id
            )
        loaded.add(result_id)
        dependency_ids = result.get("dependencyResultIds")
        if not isinstance(dependency_ids, list):
            raise MathFlowError("research builder v9 result dependencies are invalid")
        pending.extend(str(item) for item in dependency_ids)
    return loaded


def _program_context(program: Mapping[str, object]) -> dict[str, object]:
    return {
        key: copy.deepcopy(program[key])
        for key in PROGRAM_CONTEXT_FIELDS
    }


def _support_context(support: Mapping[str, object]) -> dict[str, object]:
    artifact_refs = support.get("artifactRefs")
    if not isinstance(artifact_refs, list):
        raise MathFlowError("research builder v9 result artifacts are invalid")
    return {
        "proofs": copy.deepcopy(support["proofs"]),
        "methods": copy.deepcopy(support["methods"]),
        "computations": copy.deepcopy(support["computations"]),
        "tools": copy.deepcopy(support["tools"]),
        "artifactPaths": sorted(
            {
                str(item["path"])
                for item in artifact_refs
                if isinstance(item, dict) and isinstance(item.get("path"), str)
            }
        ),
        "attestationRefs": copy.deepcopy(support["attestationRefs"]),
    }


def _result_context(
    result: Mapping[str, object], *, include_support: bool
) -> dict[str, object]:
    value = {
        key: copy.deepcopy(result[key])
        for key in RESULT_CONTEXT_FIELDS
        if key != "support"
    }
    support = result.get("support")
    if not isinstance(support, dict):
        raise MathFlowError("research builder v9 result support is invalid")
    value["support"] = _support_context(support) if include_support else None
    return value


def build_research_builder_v9_context(
    base_state: Mapping[str, object], accepted_claims: object
) -> dict[str, object]:
    """Build the progressive, digest-bound view supplied to Builder V9."""

    state = validate_research_program_state_v3(copy.deepcopy(dict(base_state)))
    dependencies = _dependency_transaction_ids(accepted_claims)
    loaded = _loaded_result_ids(state, dependencies)
    programs = state["programs"]
    results = state["intermediateResults"]
    assert isinstance(programs, dict)
    assert isinstance(results, dict)
    core: dict[str, object] = {
        "schemaVersion": 1,
        "problemId": state["problemId"],
        "baseStateDigest": state["stateDigest"],
        "rootProgramId": state["rootProgramId"],
        "dependencyTransactionIds": dependencies,
        "supportLoadedResultIds": sorted(loaded),
        "supportOmittedResultIds": sorted(set(results) - loaded),
        "programs": {
            str(program_id): _program_context(program)
            for program_id, program in sorted(programs.items())
            if isinstance(program, dict)
        },
        "intermediateResults": {
            str(result_id): _result_context(
                result, include_support=str(result_id) in loaded
            )
            for result_id, result in sorted(results.items())
            if isinstance(result, dict)
        },
    }
    return {**core, "contextDigest": _context_digest(core)}


def validate_research_builder_v9_context(
    value: object,
    *,
    base_state: Mapping[str, object] | None = None,
    accepted_claims: object | None = None,
) -> dict[str, object]:
    if not isinstance(value, dict) or set(value) != CONTEXT_FIELDS:
        raise MathFlowError("research builder v9 context has an invalid envelope")
    if value.get("schemaVersion") != 1:
        raise MathFlowError("research builder v9 context has an unsupported version")
    if value.get("contextDigest") != _context_digest(value):
        raise MathFlowError("research builder v9 context digest mismatch")
    programs = value.get("programs")
    results = value.get("intermediateResults")
    loaded = value.get("supportLoadedResultIds")
    omitted = value.get("supportOmittedResultIds")
    if (
        not isinstance(programs, dict)
        or not isinstance(results, dict)
        or not isinstance(loaded, list)
        or not isinstance(omitted, list)
        or any(not isinstance(item, str) for item in [*loaded, *omitted])
        or loaded != sorted(set(loaded))
        or omitted != sorted(set(omitted))
        or set(loaded) | set(omitted) != set(results)
        or set(loaded) & set(omitted)
    ):
        raise MathFlowError("research builder v9 context selection is invalid")
    for program_id, program in programs.items():
        if (
            not isinstance(program_id, str)
            or not isinstance(program, dict)
            or set(program) != PROGRAM_CONTEXT_FIELDS
            or program.get("id") != program_id
        ):
            raise MathFlowError("research builder v9 program context is invalid")
    for result_id, result in results.items():
        if (
            not isinstance(result_id, str)
            or not isinstance(result, dict)
            or set(result) != RESULT_CONTEXT_FIELDS
            or result.get("id") != result_id
        ):
            raise MathFlowError("research builder v9 result context is invalid")
        support = result.get("support")
        if result_id in loaded:
            if not isinstance(support, dict) or set(support) != SUPPORT_CONTEXT_FIELDS:
                raise MathFlowError("research builder v9 loaded support is invalid")
        elif support is not None:
            raise MathFlowError("research builder v9 omitted support must be null")
    if base_state is not None:
        if accepted_claims is None:
            raise MathFlowError("research builder v9 context validation needs claims")
        expected = build_research_builder_v9_context(base_state, accepted_claims)
        if value != expected:
            raise MathFlowError("research builder v9 context is not reducer-derived")
    return value


def apply_research_builder_v9_transition(
    base_state: dict[str, object],
    transition: dict[str, object],
    *,
    accepted_claims: object,
    judgment_id: str,
    evidence_file_refs: Mapping[str, str],
) -> dict[str, object]:
    """Apply V8's complete-state reducer after V9 trusted patch expansion."""

    return apply_research_builder_v8_transition(
        base_state,
        transition,
        accepted_claims=accepted_claims,
        judgment_id=judgment_id,
        evidence_file_refs=evidence_file_refs,
    )


__all__ = [
    "apply_research_builder_v9_transition",
    "build_research_builder_v9_context",
    "validate_research_builder_v9_context",
]
