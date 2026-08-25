from __future__ import annotations

import copy
import re

from .errors import MathFlowError
from .repository import sha256_json
from .research_topology import (
    ENTITY_COLLECTIONS,
    _normalize_entity_value,
    apply_research_topology_transition,
    derive_research_topology_alignment,
    validate_research_program_state_v2,
    validate_research_topology_alignment,
)


IDENTIFIER = re.compile(r"^[a-z0-9][a-z0-9/_-]*$")
GIT_SHA = re.compile(r"^[0-9a-f]{40}$")
DIGEST = re.compile(r"^sha256:[0-9a-f]{64}$")

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
CONTRIBUTION_FIELDS = {
    "claimKeys",
    "directProgramId",
    "directThreadIds",
    "itemIds",
}
PLACEMENT_AUDIT_FIELDS = {"basis", "rationale", "relatedProgramIds"}
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


def _with_record_digest(record: dict[str, object]) -> dict[str, object]:
    value = {
        key: copy.deepcopy(item) for key, item in record.items() if key != "digest"
    }
    return {**value, "digest": f"sha256:{sha256_json(value)}"}


def _with_state_digest(state: dict[str, object]) -> dict[str, object]:
    value = {
        key: copy.deepcopy(item)
        for key, item in state.items()
        if key != "stateDigest"
    }
    return {**value, "stateDigest": f"sha256:{sha256_json(value)}"}


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


def _require_unique_strings(value: object, label: str) -> list[str]:
    if (
        not isinstance(value, list)
        or any(not isinstance(item, str) or not item for item in value)
        or len(value) != len(set(value))
    ):
        raise MathFlowError(f"{label} must contain unique non-empty strings")
    return list(value)


def _accepted_claims(
    value: object, subject_transaction_id: str
) -> dict[str, dict[str, object]]:
    if not isinstance(value, list) or not value:
        raise MathFlowError("research builder v6 needs at least one accepted claim")
    result: dict[str, dict[str, object]] = {}
    for claim in value:
        if not isinstance(claim, dict):
            raise MathFlowError("research builder v6 accepted claim must be an object")
        claim_key = _require_identifier(
            claim.get("claimKey"), "research builder v6 accepted claim key"
        )
        if claim_key in result:
            raise MathFlowError("research builder v6 repeats an accepted claim key")
        dependencies = _require_unique_strings(
            claim.get("dependencyTransactionIds"),
            "research builder v6 accepted claim dependencies",
        )
        if any(not GIT_SHA.fullmatch(item) for item in dependencies):
            raise MathFlowError(
                "research builder v6 accepted claim has an invalid dependency"
            )
        if subject_transaction_id in dependencies:
            raise MathFlowError(
                "research builder v6 accepted claim may not depend on its own submission"
            )
        result[claim_key] = claim
    return result


def _changed_fields(
    before: dict[str, object], after: dict[str, object]
) -> set[str]:
    return {
        field
        for field in set(before) | set(after)
        if field != "digest" and before.get(field) != after.get(field)
    }


def _apply_content_operations(
    base_state: dict[str, object],
    transition: dict[str, object],
    *,
    accepted_claims: object,
    judgment_id: str,
) -> dict[str, object]:
    subject_transaction_id = str(transition["subjectTransactionId"])
    claims_by_key = _accepted_claims(accepted_claims, subject_transaction_id)
    if not isinstance(judgment_id, str) or not DIGEST.fullmatch(judgment_id):
        raise MathFlowError("research builder v6 needs an exact judgment digest")

    operations = transition["contentOperations"]
    contribution_value = transition["contribution"]
    if not isinstance(operations, list) or not isinstance(contribution_value, dict):
        raise MathFlowError("research builder v6 content transition is invalid")
    if set(contribution_value) != CONTRIBUTION_FIELDS:
        raise MathFlowError("research builder v6 contribution has invalid fields")

    result = copy.deepcopy(base_state)
    result.pop("stateDigest", None)
    collections = {
        kind: result[collection_name]
        for kind, collection_name in ENTITY_COLLECTIONS.items()
    }
    contributions = result["contributions"]
    assert isinstance(contributions, dict)
    if subject_transaction_id in contributions:
        raise MathFlowError(
            "research builder v6 state already contains the accepted submission"
        )
    allowed_sources = set(contributions) | {subject_transaction_id}
    seen_operations: set[tuple[str, str]] = set()

    for operation in operations:
        if not isinstance(operation, dict) or set(operation) != CONTENT_OPERATION_FIELDS:
            raise MathFlowError(
                "research builder v6 content operation has invalid fields"
            )
        kind = operation.get("entityKind")
        if kind not in collections:
            raise MathFlowError(
                "research builder v6 content operation has an invalid entity kind"
            )
        entity_id = _require_identifier(
            operation.get("entityId"), "research builder v6 content entity ID"
        )
        key = (str(kind), entity_id)
        if key in seen_operations:
            raise MathFlowError(
                "research builder v6 content operations repeat an entity"
            )
        seen_operations.add(key)
        collection = collections[str(kind)]
        assert isinstance(collection, dict)
        existing = collection.get(entity_id)
        base_digest = operation.get("baseDigest")
        if existing is None:
            if base_digest is not None:
                raise MathFlowError(
                    "new research builder v6 content entity must use null baseDigest"
                )
        elif not isinstance(existing, dict) or base_digest != existing.get("digest"):
            raise MathFlowError(
                "research builder v6 content operation baseDigest mismatch"
            )

        normalized = _normalize_entity_value(
            str(kind), entity_id, operation.get("value")
        )
        sources = set(normalized.get("sourceTransactionIds", []))
        if subject_transaction_id not in sources:
            raise MathFlowError(
                "every research builder v6 content operation must cite its submission"
            )
        if not sources <= allowed_sources:
            raise MathFlowError(
                "research builder v6 content operation cites an unaccepted submission"
            )

        if isinstance(existing, dict):
            immutable_fields = {
                "program": {"parentId", "parentThreadIds", "lineage"},
                "thread": {"programId", "kind"},
                "item": {"programId", "type"},
            }[str(kind)]
            if _changed_fields(existing, normalized) & immutable_fields:
                raise MathFlowError(
                    "research builder v6 content operation hides a topology or type change"
                )
            if existing.get("status") != "retired" and normalized.get(
                "status"
            ) == "retired":
                raise MathFlowError(
                    "research builder v6 retirement needs an explicit topology operation"
                )
            if existing.get("status") == "retired" and normalized.get(
                "status"
            ) != "retired":
                raise MathFlowError(
                    "research builder v6 content operation may not revive a retired entity"
                )
            if not set(existing.get("sourceTransactionIds", [])) <= sources:
                raise MathFlowError(
                    "research builder v6 content provenance is additive"
                )
            if kind == "item":
                prior_claims = {
                    (str(ref["transactionId"]), str(ref["claimKey"]))
                    for ref in existing.get("claimRefs", [])
                }
                next_claims = {
                    (str(ref["transactionId"]), str(ref["claimKey"]))
                    for ref in normalized.get("claimRefs", [])
                }
                if not prior_claims <= next_claims or not set(
                    existing.get("dependencyItemIds", [])
                ) <= set(normalized.get("dependencyItemIds", [])):
                    raise MathFlowError(
                        "research builder v6 item evidence and dependencies are additive"
                    )
        elif (
            (kind == "program" and normalized.get("lineage") != [])
            or normalized.get("status") == "retired"
        ):
            raise MathFlowError(
                "research builder v6 content creation may not invent lineage or retired entities"
            )
        collection[entity_id] = normalized

    claim_keys = _require_unique_strings(
        contribution_value.get("claimKeys"),
        "research builder v6 contribution claim keys",
    )
    if set(claim_keys) != set(claims_by_key):
        raise MathFlowError(
            "research builder v6 contribution must cover every accepted claim exactly once"
        )
    direct_program_id = _require_identifier(
        contribution_value.get("directProgramId"),
        "research builder v6 contribution direct program ID",
    )
    direct_thread_ids = _require_unique_strings(
        contribution_value.get("directThreadIds"),
        "research builder v6 contribution direct thread IDs",
    )
    item_ids = _require_unique_strings(
        contribution_value.get("itemIds"),
        "research builder v6 contribution item IDs",
    )
    if not direct_thread_ids or not item_ids:
        raise MathFlowError(
            "research builder v6 contribution needs a direct thread and durable item"
        )
    dependency_ids = list(
        dict.fromkeys(
            dependency
            for claim_key in claim_keys
            for dependency in claims_by_key[claim_key]["dependencyTransactionIds"]
        )
    )
    if not set(dependency_ids) <= set(contributions):
        missing = sorted(set(dependency_ids) - set(contributions))[0]
        raise MathFlowError(
            "research builder v6 accepted dependency is absent from prior state: "
            f"{missing}"
        )
    contributions[subject_transaction_id] = _with_record_digest(
        {
            "id": subject_transaction_id,
            "transactionId": subject_transaction_id,
            "claimKeys": claim_keys,
            "directProgramId": direct_program_id,
            "directThreadIds": direct_thread_ids,
            "itemIds": item_ids,
            "dependencyTransactionIds": dependency_ids,
            "judgmentId": judgment_id,
        }
    )
    result["ledgerHead"] = subject_transaction_id
    result["baseStateDigest"] = base_state["stateDigest"]
    content_state = _with_state_digest(result)
    validate_research_program_state_v2(
        content_state, str(base_state["problemId"])
    )

    direct_program = content_state["programs"].get(direct_program_id)
    if not isinstance(direct_program, dict) or direct_program.get("status") != "active":
        raise MathFlowError(
            "research builder v6 contribution needs an active initial program"
        )
    if any(
        content_state["threads"][thread_id].get("programId") != direct_program_id
        or content_state["threads"][thread_id].get("status") == "retired"
        for thread_id in direct_thread_ids
    ):
        raise MathFlowError(
            "research builder v6 contribution thread is outside its initial program"
        )
    if any(
        content_state["items"][item_id].get("programId") != direct_program_id
        for item_id in item_ids
    ):
        raise MathFlowError(
            "research builder v6 contribution item is outside its initial program"
        )

    represented = {
        (str(ref["transactionId"]), str(ref["claimKey"]))
        for item_id in item_ids
        for ref in content_state["items"][item_id]["claimRefs"]
    }
    expected = {(subject_transaction_id, claim_key) for claim_key in claim_keys}
    if not expected <= represented:
        raise MathFlowError(
            "research builder v6 accepted claim is not represented by a durable item"
        )
    _validate_placement_audit(content_state, transition)
    return content_state


def _is_descendant(
    state: dict[str, object], candidate_id: str, ancestor_id: str
) -> bool:
    programs = state["programs"]
    assert isinstance(programs, dict)
    cursor: str | None = candidate_id
    while cursor is not None:
        if cursor == ancestor_id:
            return True
        parent_id = programs[cursor].get("parentId")
        cursor = str(parent_id) if isinstance(parent_id, str) else None
    return False


def _validate_placement_audit(
    content_state: dict[str, object], transition: dict[str, object]
) -> None:
    audit = transition["placementAudit"]
    if not isinstance(audit, dict) or set(audit) != PLACEMENT_AUDIT_FIELDS:
        raise MathFlowError("research builder v6 placement audit has invalid fields")
    basis = audit.get("basis")
    if basis not in {"local-objective", "cross-program", "canonical-objective"}:
        raise MathFlowError("research builder v6 placement basis is invalid")
    if not isinstance(audit.get("rationale"), str) or not str(
        audit["rationale"]
    ).strip():
        raise MathFlowError("research builder v6 placement rationale is empty")
    related_program_ids = _require_unique_strings(
        audit.get("relatedProgramIds"),
        "research builder v6 related program IDs",
    )
    subject_transaction_id = str(transition["subjectTransactionId"])
    contribution = content_state["contributions"][subject_transaction_id]
    direct_program_id = str(contribution["directProgramId"])
    programs = content_state["programs"]
    assert isinstance(programs, dict)
    contributions = content_state["contributions"]
    assert isinstance(contributions, dict)
    if len(contributions) >= 2 and all(
        record.get("directProgramId") == "root"
        for record in contributions.values()
    ):
        raise MathFlowError(
            "hierarchical research v6 multi-submission state may not remain root-only"
        )
    if basis == "local-objective":
        direct_program = programs.get(direct_program_id)
        if (
            direct_program_id == "root"
            or not isinstance(direct_program, dict)
            or direct_program.get("status") != "active"
            or related_program_ids != [direct_program_id]
        ):
            raise MathFlowError(
                "research builder v6 local placement must name its active non-root program"
            )
        return
    if direct_program_id != "root":
        raise MathFlowError(
            "research builder v6 exceptional placement applies only at root"
        )
    if basis == "canonical-objective":
        if related_program_ids:
            raise MathFlowError(
                "research builder v6 canonical placement may not name local programs"
            )
        return
    if len(related_program_ids) < 2:
        raise MathFlowError(
            "research builder v6 cross-program placement needs two local programs"
        )
    for program_id in related_program_ids:
        program = programs.get(program_id)
        if (
            program_id == "root"
            or not isinstance(program, dict)
            or program.get("status") != "active"
        ):
            raise MathFlowError(
                "research builder v6 cross-program placement names an invalid program"
            )
    for index, left_id in enumerate(related_program_ids):
        for right_id in related_program_ids[index + 1 :]:
            if _is_descendant(
                content_state, left_id, right_id
            ) or _is_descendant(content_state, right_id, left_id):
                raise MathFlowError(
                    "research builder v6 cross-program placement requires incomparable programs"
                )


def _same_world_handoff(
    subject_transaction_id: str,
    before_state: dict[str, object],
    after_state: dict[str, object],
    alignment: dict[str, object],
) -> dict[str, object]:
    return _with_handoff_digest(
        {
            "schemaVersion": 1,
            "problemId": before_state["problemId"],
            "subjectTransactionId": subject_transaction_id,
            "beforeKnowledgeStateDigest": before_state["stateDigest"],
            "afterKnowledgeStateDigest": after_state["stateDigest"],
            "topologyAlignmentDigest": alignment["alignmentDigest"],
            "sameWorldReferenceStateDigest": after_state["stateDigest"],
            "accountingNodeKinds": ["program", "thread"],
            "semanticLeafKinds": ["item"],
        }
    )


def validate_research_builder_v6_handoff(
    handoff: object,
    before_state: dict[str, object],
    after_state: dict[str, object],
    alignment: dict[str, object],
    subject_transaction_id: str,
) -> dict[str, object]:
    if not isinstance(subject_transaction_id, str) or not GIT_SHA.fullmatch(
        subject_transaction_id
    ):
        raise MathFlowError("research builder v6 handoff has an invalid subject")
    validate_research_program_state_v2(before_state)
    validate_research_program_state_v2(after_state)
    validate_research_topology_alignment(alignment, before_state, after_state)
    if not isinstance(handoff, dict) or set(handoff) != HANDOFF_FIELDS:
        raise MathFlowError("research builder v6 handoff has an invalid envelope")
    expected = _same_world_handoff(
        subject_transaction_id, before_state, after_state, alignment
    )
    if handoff != expected:
        raise MathFlowError(
            "research builder v6 handoff differs from the deterministic same-world handoff"
        )
    return handoff


def apply_research_builder_v6_transition(
    base_state: dict[str, object],
    transition: object,
    *,
    accepted_claims: object,
    judgment_id: str,
) -> dict[str, object]:
    """Apply one accepted submission and return its exact same-world artifacts."""

    validate_research_program_state_v2(base_state)
    if not isinstance(transition, dict) or set(transition) != TRANSITION_FIELDS:
        raise MathFlowError("research builder v6 transition has an invalid envelope")
    if transition.get("schemaVersion") != 1:
        raise MathFlowError("research builder v6 transition has an unsupported version")
    subject_transaction_id = transition.get("subjectTransactionId")
    if not isinstance(subject_transaction_id, str) or not GIT_SHA.fullmatch(
        subject_transaction_id
    ):
        raise MathFlowError("research builder v6 transition has an invalid subject")
    if transition.get("baseStateDigest") != base_state.get("stateDigest"):
        raise MathFlowError("research builder v6 transition has a stale base state")
    topology_operations = transition.get("topologyOperations")
    if not isinstance(topology_operations, list):
        raise MathFlowError("research builder v6 topologyOperations must be an array")
    if any(
        isinstance(operation, dict)
        and operation.get("action") == "create"
        and operation.get("entityKind") == "item"
        for operation in topology_operations
    ):
        raise MathFlowError(
            "research builder v6 items must be authored as accepted content, not topology"
        )
    topology_rationale = transition.get("topologyRationale")
    if topology_operations:
        if not isinstance(topology_rationale, str) or not topology_rationale.strip():
            raise MathFlowError(
                "research builder v6 topology revision needs a rationale"
            )
    elif topology_rationale is not None:
        raise MathFlowError(
            "research builder v6 topology rationale requires topology operations"
        )

    content_state = _apply_content_operations(
        base_state,
        transition,
        accepted_claims=accepted_claims,
        judgment_id=judgment_id,
    )
    if topology_operations:
        topology_state, _ = apply_research_topology_transition(
            content_state,
            {
                "schemaVersion": 1,
                "baseStateDigest": content_state["stateDigest"],
                "operations": topology_operations,
            },
        )
        topology_state["baseStateDigest"] = base_state["stateDigest"]
        post_state = _with_state_digest(topology_state)
        validate_research_program_state_v2(
            post_state, str(base_state["problemId"])
        )
    else:
        post_state = content_state

    alignment = derive_research_topology_alignment(base_state, post_state)
    validate_research_topology_alignment(alignment, base_state, post_state)
    handoff = _same_world_handoff(
        subject_transaction_id, base_state, post_state, alignment
    )
    validate_research_builder_v6_handoff(
        handoff,
        base_state,
        post_state,
        alignment,
        subject_transaction_id,
    )
    return {
        "subjectTransactionId": subject_transaction_id,
        "postState": post_state,
        "topologyAlignment": alignment,
        "sameWorldHandoff": handoff,
    }


def apply_research_builder_v6_sequence(
    base_state: dict[str, object],
    transitions: object,
    *,
    accepted_submissions: object,
) -> list[dict[str, object]]:
    """Apply exact accepted submissions in caller-supplied canonical ledger order."""

    validate_research_program_state_v2(base_state)
    if not isinstance(transitions, list) or not isinstance(
        accepted_submissions, list
    ):
        raise MathFlowError("research builder v6 sequence inputs must be arrays")
    if len(transitions) != len(accepted_submissions):
        raise MathFlowError(
            "research builder v6 sequence must have one transition per accepted submission"
        )

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
            raise MathFlowError(
                "research builder v6 accepted submission metadata is invalid"
            )
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
            raise MathFlowError(
                "research builder v6 accepted submissions are not in unique canonical order"
            )
        expected_subjects.append(transaction_id)
        prior_ordinal = ordinal
        normalized_submissions.append(submission)
    observed_subjects = [
        transition.get("subjectTransactionId")
        if isinstance(transition, dict)
        else None
        for transition in transitions
    ]
    if observed_subjects != expected_subjects:
        raise MathFlowError(
            "research builder v6 transitions do not match canonical accepted-submission order"
        )

    results: list[dict[str, object]] = []
    state = base_state
    for transition, submission in zip(
        transitions, normalized_submissions, strict=True
    ):
        result = apply_research_builder_v6_transition(
            state,
            transition,
            accepted_claims=submission["acceptedClaims"],
            judgment_id=str(submission["judgmentId"]),
        )
        results.append(result)
        state = result["postState"]
        assert isinstance(state, dict)
    return results
