from __future__ import annotations

import copy
import re
from fractions import Fraction
from typing import Iterable, Mapping

from .errors import MathFlowError
from .repository import sha256_json
from .research_state import validate_research_program_state


DIGEST = re.compile(r"^sha256:[0-9a-f]{64}$")
GIT_SHA = re.compile(r"^[0-9a-f]{40}$")
IDENTIFIER = re.compile(r"^[a-z0-9][a-z0-9/_-]*$")
CANONICAL_DECIMAL = re.compile(r"^(?:0|[1-9][0-9]*)(?:\.[0-9]*[1-9])?$")

NODE_KINDS = {"program", "thread"}
EVALUATION_MODES = {"baseline", "no-access", "with-access"}
PATCH_MODES = {"no-access", "with-access"}

ROOT_CONTRACT_FIELDS = {
    "schemaVersion",
    "problemId",
    "knowledgeProjectionId",
    "knowledgeProjectionSpecDigest",
    "objective",
    "terminalCondition",
    "workUnit",
    "referenceCommunity",
    "rootContractDigest",
}
WORK_UNIT_FIELDS = {"id", "definition", "toolBaseline"}
REFERENCE_COMMUNITY_FIELDS = {
    "portfolioAuthority",
    "description",
    "researcherQualification",
}
NODE_REF_FIELDS = {"kind", "id"}
ANNOTATION_FIELDS = {
    "nodeRef",
    "knowledgeNodeDigest",
    "directWorkHours",
    "conditionalIncidence",
    "annotationDigest",
}
DERIVED_FIELDS = {
    "nodeRef",
    "globalReach",
    "conditionalSubtreeWork",
    "expectedDirectWork",
}
STATE_FIELDS = {
    "schemaVersion",
    "problemId",
    "rootContractDigest",
    "knowledgeStateDigest",
    "knowledgeLedgerHead",
    "predecessorStateDigest",
    "evaluationMode",
    "subjectTransactionId",
    "processedSubmissionIds",
    "rootNodeRef",
    "annotations",
    "derived",
    "totalWorkHours",
    "stateDigest",
}
PATCH_FIELDS = {
    "schemaVersion",
    "problemId",
    "subjectTransactionId",
    "evaluationMode",
    "rootContractDigest",
    "baseAccountingStateDigest",
    "baseKnowledgeStateDigest",
    "targetKnowledgeStateDigest",
    "topologyAlignmentDigest",
    "updates",
    "patchDigest",
}
UPDATE_FIELDS = {
    "nodeRef",
    "baseAnnotationDigest",
    "changes",
    "rationale",
    "evidenceRefs",
}
CHANGE_FIELDS = {"directWorkHours", "conditionalIncidence"}
EVALUATION_FIELDS = {
    "schemaVersion",
    "problemId",
    "subjectTransactionId",
    "rootContractDigest",
    "baseAccountingStateDigest",
    "baseKnowledgeStateDigest",
    "targetKnowledgeStateDigest",
    "topologyAlignmentDigest",
    "noAccessPatchDigest",
    "withAccessPatchDigest",
    "noAccessStateDigest",
    "withAccessStateDigest",
    "noAccessWorkHours",
    "withAccessWorkHours",
    "workValueHours",
    "affectedNodeRefs",
    "evaluationDigest",
}

WORK_UNIT_ID = "competent-human-researcher-hour"
WORK_UNIT_DEFINITION = (
    "One focused person-hour of research by a researcher qualified for the "
    "relevant work package, using the fixed conventional tool baseline named "
    "by this contract."
)
PORTFOLIO_AUTHORITY = "math-flow-knowledge-state-builder"


def _validate_knowledge_state(
    value: object, problem: str | None = None
) -> dict[str, object]:
    """Validate active v1 state and use the additive v1/v2 dispatcher when present."""

    try:
        from .research_topology import validate_research_program_state_versioned
    except ModuleNotFoundError as exc:
        if exc.name != f"{__package__}.research_topology":
            raise
        return validate_research_program_state(value, problem)
    return validate_research_program_state_versioned(value, problem)


def _content_digest(value: Mapping[str, object], digest_field: str) -> str:
    content = {key: copy.deepcopy(item) for key, item in value.items() if key != digest_field}
    return f"sha256:{sha256_json(content)}"


def _require_digest(value: object, label: str, *, nullable: bool = False) -> str | None:
    if value is None and nullable:
        return None
    if not isinstance(value, str) or not DIGEST.fullmatch(value):
        raise MathFlowError(f"{label} must be a sha256 digest")
    return value


def _require_transaction(
    value: object, label: str, *, nullable: bool = False
) -> str | None:
    if value is None and nullable:
        return None
    if not isinstance(value, str) or not GIT_SHA.fullmatch(value):
        raise MathFlowError(f"{label} must be a canonical transaction ID")
    return value


def _require_identifier(value: object, label: str) -> str:
    if not isinstance(value, str) or not IDENTIFIER.fullmatch(value):
        raise MathFlowError(f"{label} must be a stable lowercase path")
    return value


def _require_text(value: object, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise MathFlowError(f"{label} must be non-empty text")
    if value != value.strip():
        raise MathFlowError(f"{label} must not have surrounding whitespace")
    return value


def _require_sorted_unique_strings(value: object, label: str) -> list[str]:
    if (
        not isinstance(value, list)
        or any(not isinstance(item, str) or not item for item in value)
        or value != sorted(set(value))
    ):
        raise MathFlowError(f"{label} must contain sorted unique non-empty strings")
    return list(value)


def _fraction_to_decimal(value: Fraction) -> str:
    if value < 0:
        raise MathFlowError("accounting values must be non-negative")
    denominator = value.denominator
    twos = 0
    fives = 0
    while denominator % 2 == 0:
        denominator //= 2
        twos += 1
    while denominator % 5 == 0:
        denominator //= 5
        fives += 1
    if denominator != 1:
        raise MathFlowError("accounting values must have a finite decimal representation")
    scale = max(twos, fives)
    scaled = value.numerator * (2 ** (scale - twos)) * (5 ** (scale - fives))
    if scale == 0:
        return str(scaled)
    digits = str(scaled).rjust(scale + 1, "0")
    integer = digits[:-scale]
    fractional = digits[-scale:].rstrip("0")
    return integer if not fractional else f"{integer}.{fractional}"


def canonical_decimal(value: object, label: str = "value") -> str:
    """Return the unique non-negative finite-decimal representation of value."""

    if isinstance(value, bool):
        raise MathFlowError(f"{label} must be a non-negative finite decimal")
    if isinstance(value, Fraction):
        return _fraction_to_decimal(value)
    if isinstance(value, int):
        if value < 0:
            raise MathFlowError(f"{label} must be a non-negative finite decimal")
        return str(value)
    if not isinstance(value, str) or len(value) > 128:
        raise MathFlowError(f"{label} must be a non-negative finite decimal")
    if not re.fullmatch(r"(?:0|[1-9][0-9]*)(?:\.[0-9]+)?", value):
        raise MathFlowError(f"{label} must be a non-negative finite decimal")
    integer, dot, fractional = value.partition(".")
    fractional = fractional.rstrip("0")
    return integer if not fractional else f"{integer}.{fractional}"


def _require_canonical_decimal(value: object, label: str) -> Fraction:
    if not isinstance(value, str) or not CANONICAL_DECIMAL.fullmatch(value):
        raise MathFlowError(f"{label} must be a canonical non-negative decimal string")
    if len(value) > 128:
        raise MathFlowError(f"{label} is too precise")
    return Fraction(value)


def _require_probability(value: object, label: str) -> Fraction:
    result = _require_canonical_decimal(value, label)
    if result > 1:
        raise MathFlowError(f"{label} must be between zero and one")
    return result


def _node_ref(value: object, label: str = "node reference") -> dict[str, str]:
    if not isinstance(value, dict) or set(value) != NODE_REF_FIELDS:
        raise MathFlowError(f"{label} has invalid fields")
    kind = value.get("kind")
    if kind not in NODE_KINDS:
        raise MathFlowError(f"{label} has an invalid kind")
    return {"kind": str(kind), "id": _require_identifier(value.get("id"), f"{label} ID")}


def _node_key(value: object, label: str = "node reference") -> tuple[str, str]:
    normalized = _node_ref(value, label)
    return normalized["kind"], normalized["id"]


def _node_ref_for(key: tuple[str, str]) -> dict[str, str]:
    return {"kind": key[0], "id": key[1]}


def _node_ref_sort_key(value: Mapping[str, object]) -> tuple[str, str]:
    return str(value.get("kind")), str(value.get("id"))


def _knowledge_topology(
    knowledge_state: object,
) -> tuple[
    dict[tuple[str, str], dict[str, object]],
    dict[tuple[str, str], tuple[str, str] | None],
    tuple[str, str],
]:
    state = _validate_knowledge_state(knowledge_state)
    programs = state["programs"]
    threads = state["threads"]
    assert isinstance(programs, dict) and isinstance(threads, dict)
    nodes: dict[tuple[str, str], dict[str, object]] = {}
    parents: dict[tuple[str, str], tuple[str, str] | None] = {}
    for program_id, program in programs.items():
        key = ("program", str(program_id))
        assert isinstance(program, dict)
        nodes[key] = program
        parent_id = program.get("parentId")
        parents[key] = (
            ("program", str(parent_id)) if isinstance(parent_id, str) else None
        )
    for thread_id, thread in threads.items():
        key = ("thread", str(thread_id))
        assert isinstance(thread, dict)
        nodes[key] = thread
        parents[key] = ("program", str(thread["programId"]))
    root = ("program", str(state["rootProgramId"]))
    if parents.get(root) is not None:
        raise MathFlowError("work-accounting root must be the knowledge-state root program")
    return nodes, parents, root


def _topology_signature(knowledge_state: object) -> dict[tuple[str, str], tuple[str, str] | None]:
    _, parents, _ = _knowledge_topology(knowledge_state)
    return parents


def make_root_contract(
    *,
    problem_id: str,
    knowledge_projection_id: str,
    knowledge_projection_spec_digest: str,
    objective: str,
    terminal_condition: str,
    tool_baseline: str,
    reference_community_description: str,
    researcher_qualification: str,
) -> dict[str, object]:
    result: dict[str, object] = {
        "schemaVersion": 1,
        "problemId": problem_id,
        "knowledgeProjectionId": knowledge_projection_id,
        "knowledgeProjectionSpecDigest": knowledge_projection_spec_digest,
        "objective": objective,
        "terminalCondition": terminal_condition,
        "workUnit": {
            "id": WORK_UNIT_ID,
            "definition": WORK_UNIT_DEFINITION,
            "toolBaseline": tool_baseline,
        },
        "referenceCommunity": {
            "portfolioAuthority": PORTFOLIO_AUTHORITY,
            "description": reference_community_description,
            "researcherQualification": researcher_qualification,
        },
    }
    result["rootContractDigest"] = _content_digest(result, "rootContractDigest")
    return validate_root_contract(result)


def validate_root_contract(value: object, problem: str | None = None) -> dict[str, object]:
    if not isinstance(value, dict) or set(value) != ROOT_CONTRACT_FIELDS:
        raise MathFlowError("work-accounting root contract has an invalid envelope")
    if value.get("schemaVersion") != 1:
        raise MathFlowError("work-accounting root contract has an unsupported version")
    problem_id = _require_identifier(value.get("problemId"), "root-contract problem ID")
    if problem is not None and problem_id != problem:
        raise MathFlowError("work-accounting root contract belongs to another problem")
    _require_identifier(value.get("knowledgeProjectionId"), "knowledge projection ID")
    _require_digest(value.get("knowledgeProjectionSpecDigest"), "knowledge projection spec digest")
    _require_text(value.get("objective"), "root objective")
    _require_text(value.get("terminalCondition"), "root terminal condition")
    work_unit = value.get("workUnit")
    if not isinstance(work_unit, dict) or set(work_unit) != WORK_UNIT_FIELDS:
        raise MathFlowError("work-accounting unit contract has invalid fields")
    if work_unit.get("id") != WORK_UNIT_ID or work_unit.get("definition") != WORK_UNIT_DEFINITION:
        raise MathFlowError("work-accounting v1 must use competent human researcher hours")
    _require_text(work_unit.get("toolBaseline"), "work-accounting tool baseline")
    community = value.get("referenceCommunity")
    if not isinstance(community, dict) or set(community) != REFERENCE_COMMUNITY_FIELDS:
        raise MathFlowError("work-accounting reference community has invalid fields")
    if community.get("portfolioAuthority") != PORTFOLIO_AUTHORITY:
        raise MathFlowError("the Math Flow knowledge builder must own the reference portfolio")
    _require_text(community.get("description"), "reference community description")
    _require_text(community.get("researcherQualification"), "researcher qualification")
    if value.get("rootContractDigest") != _content_digest(value, "rootContractDigest"):
        raise MathFlowError("work-accounting root contract digest mismatch")
    return value


def _annotation_digest(value: Mapping[str, object]) -> str:
    return _content_digest(value, "annotationDigest")


def _normalize_annotation(
    value: object,
    *,
    knowledge_node_digest: str,
    is_root: bool,
) -> dict[str, object]:
    if not isinstance(value, dict):
        raise MathFlowError("work-accounting annotation must be an object")
    allowed = {"nodeRef", "directWorkHours", "conditionalIncidence"}
    if set(value) != allowed:
        raise MathFlowError("work-accounting annotation input has invalid fields")
    node_ref = _node_ref(value.get("nodeRef"), "annotation node reference")
    direct = canonical_decimal(value.get("directWorkHours"), "direct work")
    incidence_value = value.get("conditionalIncidence")
    if is_root:
        if incidence_value is not None:
            raise MathFlowError("root program conditional incidence must be null")
        incidence: str | None = None
    else:
        incidence = canonical_decimal(incidence_value, "conditional incidence")
        if Fraction(incidence) > 1:
            raise MathFlowError("conditional incidence must be between zero and one")
    result: dict[str, object] = {
        "nodeRef": node_ref,
        "knowledgeNodeDigest": knowledge_node_digest,
        "directWorkHours": direct,
        "conditionalIncidence": incidence,
    }
    result["annotationDigest"] = _annotation_digest(result)
    return result


def _derive(
    annotations: Mapping[tuple[str, str], Mapping[str, object]],
    parents: Mapping[tuple[str, str], tuple[str, str] | None],
    root: tuple[str, str],
) -> tuple[list[dict[str, object]], str]:
    children: dict[tuple[str, str], list[tuple[str, str]]] = {
        key: [] for key in parents
    }
    for key, parent in parents.items():
        if parent is not None:
            children[parent].append(key)
    for values in children.values():
        values.sort()

    reach: dict[tuple[str, str], Fraction] = {root: Fraction(1)}

    def propagate(key: tuple[str, str]) -> None:
        for child in children[key]:
            incidence = _require_probability(
                annotations[child]["conditionalIncidence"],
                "conditional incidence",
            )
            reach[child] = reach[key] * incidence
            propagate(child)

    propagate(root)
    subtree: dict[tuple[str, str], Fraction] = {}

    def aggregate(key: tuple[str, str]) -> Fraction:
        result = _require_canonical_decimal(
            annotations[key]["directWorkHours"], "direct work"
        )
        for child in children[key]:
            incidence = _require_probability(
                annotations[child]["conditionalIncidence"],
                "conditional incidence",
            )
            result += incidence * aggregate(child)
        subtree[key] = result
        return result

    total = aggregate(root)
    derived: list[dict[str, object]] = []
    direct_sum = Fraction(0)
    for key in sorted(annotations):
        direct = _require_canonical_decimal(
            annotations[key]["directWorkHours"], "direct work"
        )
        expected_direct = reach[key] * direct
        direct_sum += expected_direct
        derived.append(
            {
                "nodeRef": _node_ref_for(key),
                "globalReach": canonical_decimal(reach[key]),
                "conditionalSubtreeWork": canonical_decimal(subtree[key]),
                "expectedDirectWork": canonical_decimal(expected_direct),
            }
        )
    if total != direct_sum:
        raise MathFlowError(
            "work-accounting equality failed: root subtree work differs from summed expected direct work"
        )
    return derived, canonical_decimal(total)


def build_work_accounting_state(
    *,
    root_contract: object,
    knowledge_state: object,
    annotations: Iterable[object],
    predecessor_state_digest: str | None = None,
    evaluation_mode: str = "baseline",
    subject_transaction_id: str | None = None,
    processed_submission_ids: Iterable[str] = (),
) -> dict[str, object]:
    contract = validate_root_contract(root_contract)
    knowledge = _validate_knowledge_state(knowledge_state, str(contract["problemId"]))
    if evaluation_mode not in EVALUATION_MODES:
        raise MathFlowError("work-accounting state has an invalid evaluation mode")
    nodes, parents, root = _knowledge_topology(knowledge)
    normalized_by_key: dict[tuple[str, str], dict[str, object]] = {}
    for raw in annotations:
        if not isinstance(raw, dict):
            raise MathFlowError("work-accounting annotation input must be an object")
        key = _node_key(raw.get("nodeRef"), "annotation node reference")
        if key in normalized_by_key:
            raise MathFlowError("work-accounting state annotates one node more than once")
        record = nodes.get(key)
        if record is None:
            raise MathFlowError("work-accounting state annotates a node outside knowledge state")
        normalized_by_key[key] = _normalize_annotation(
            raw,
            knowledge_node_digest=str(record["digest"]),
            is_root=key == root,
        )
    if set(normalized_by_key) != set(nodes):
        raise MathFlowError("work-accounting state must annotate every program and thread exactly once")
    if evaluation_mode != "no-access":
        for key, annotation in normalized_by_key.items():
            status = nodes[key].get("status")
            if status in {"completed", "retired"}:
                if annotation["directWorkHours"] != "0":
                    raise MathFlowError(
                        "completed or retired knowledge nodes must have zero direct work"
                    )
                if key != root and annotation["conditionalIncidence"] != "0":
                    raise MathFlowError(
                        "completed or retired knowledge nodes must have zero incidence"
                    )
    processed = list(processed_submission_ids)
    if processed != list(dict.fromkeys(processed)) or any(
        not GIT_SHA.fullmatch(item) for item in processed
    ):
        raise MathFlowError("processed submission IDs must be unique canonical transactions")
    if evaluation_mode == "baseline":
        if subject_transaction_id is not None:
            raise MathFlowError("baseline accounting state may not name a subject")
    else:
        _require_transaction(subject_transaction_id, "work-accounting subject")
        if evaluation_mode == "no-access" and subject_transaction_id in processed:
            raise MathFlowError("no-access branch may not mark its withheld subject processed")
        if evaluation_mode == "with-access" and (
            not processed or processed[-1] != subject_transaction_id
        ):
            raise MathFlowError("with-access state must append its subject to processed submissions")
    _require_digest(predecessor_state_digest, "predecessor accounting state digest", nullable=True)
    derived, total = _derive(normalized_by_key, parents, root)
    result: dict[str, object] = {
        "schemaVersion": 1,
        "problemId": contract["problemId"],
        "rootContractDigest": contract["rootContractDigest"],
        "knowledgeStateDigest": knowledge["stateDigest"],
        "knowledgeLedgerHead": knowledge["ledgerHead"],
        "predecessorStateDigest": predecessor_state_digest,
        "evaluationMode": evaluation_mode,
        "subjectTransactionId": subject_transaction_id,
        "processedSubmissionIds": processed,
        "rootNodeRef": _node_ref_for(root),
        "annotations": [normalized_by_key[key] for key in sorted(normalized_by_key)],
        "derived": derived,
        "totalWorkHours": total,
    }
    result["stateDigest"] = _content_digest(result, "stateDigest")
    return validate_work_accounting_state(result, knowledge, contract)


def make_zero_work_accounting_state(
    *,
    root_contract: object,
    knowledge_state: object,
) -> dict[str, object]:
    """Create the deterministic structural accounting origin for a new lane.

    This is not a provider-authored estimate.  It is valid only for an empty
    builder-owned knowledge state before the first accepted submission.  Every
    direct-work primitive is zero; active non-root nodes receive incidence one
    so the seed topology remains reachable, while inactive nodes receive zero.
    The first per-submission same-world evaluation replaces the relevant
    primitives with actual no-access and with-access estimates.
    """

    contract = validate_root_contract(root_contract)
    knowledge = _validate_knowledge_state(
        knowledge_state, str(contract["problemId"])
    )
    if (
        knowledge.get("ledgerHead") is not None
        or knowledge.get("baseStateDigest") is not None
        or knowledge.get("contributions") != {}
    ):
        raise MathFlowError(
            "zero work-accounting state requires an unprocessed knowledge origin"
        )
    nodes, _, root = _knowledge_topology(knowledge)
    annotations = []
    for key in sorted(nodes):
        record = nodes[key]
        annotations.append(
            {
                "nodeRef": _node_ref_for(key),
                "directWorkHours": "0",
                "conditionalIncidence": (
                    None
                    if key == root
                    else "0"
                    if record.get("status") in {"completed", "retired"}
                    else "1"
                ),
            }
        )
    return build_work_accounting_state(
        root_contract=contract,
        knowledge_state=knowledge,
        annotations=annotations,
    )


def validate_work_accounting_state(
    value: object,
    knowledge_state: object,
    root_contract: object | None = None,
) -> dict[str, object]:
    if not isinstance(value, dict) or set(value) != STATE_FIELDS:
        raise MathFlowError("work-accounting state has an invalid envelope")
    if value.get("schemaVersion") != 1:
        raise MathFlowError("work-accounting state has an unsupported version")
    knowledge = _validate_knowledge_state(knowledge_state)
    problem_id = _require_identifier(value.get("problemId"), "work-accounting problem ID")
    if problem_id != knowledge.get("problemId"):
        raise MathFlowError("work-accounting state belongs to another problem")
    if value.get("knowledgeStateDigest") != knowledge.get("stateDigest"):
        raise MathFlowError("work-accounting state is bound to another knowledge state")
    if value.get("knowledgeLedgerHead") != knowledge.get("ledgerHead"):
        raise MathFlowError("work-accounting knowledge ledger head mismatch")
    _require_digest(value.get("rootContractDigest"), "root contract digest")
    if root_contract is not None:
        contract = validate_root_contract(root_contract, problem_id)
        if value.get("rootContractDigest") != contract.get("rootContractDigest"):
            raise MathFlowError("work-accounting state uses another root contract")
    _require_digest(value.get("predecessorStateDigest"), "predecessor state digest", nullable=True)
    mode = value.get("evaluationMode")
    if mode not in EVALUATION_MODES:
        raise MathFlowError("work-accounting state has an invalid evaluation mode")
    subject = _require_transaction(
        value.get("subjectTransactionId"), "work-accounting subject", nullable=mode == "baseline"
    )
    processed = _require_sorted_submission_sequence(value.get("processedSubmissionIds"))
    contributions = knowledge.get("contributions")
    assert isinstance(contributions, dict)
    if not set(processed) <= set(contributions):
        raise MathFlowError(
            "processed submissions must be accepted in the bound knowledge state"
        )
    if mode == "baseline" and subject is not None:
        raise MathFlowError("baseline accounting state may not name a subject")
    if mode != "baseline" and subject not in contributions:
        raise MathFlowError(
            "work-accounting subject must be accepted in the bound knowledge state"
        )
    if mode == "no-access" and subject in processed:
        raise MathFlowError("no-access branch may not mark its withheld subject processed")
    if mode == "with-access" and (not processed or processed[-1] != subject):
        raise MathFlowError("with-access state must append its subject to processed submissions")

    nodes, parents, root = _knowledge_topology(knowledge)
    if _node_key(value.get("rootNodeRef"), "root node reference") != root:
        raise MathFlowError("work-accounting root does not match knowledge state")
    raw_annotations = value.get("annotations")
    if not isinstance(raw_annotations, list):
        raise MathFlowError("work-accounting annotations must be an array")
    annotations: dict[tuple[str, str], dict[str, object]] = {}
    observed_order: list[tuple[str, str]] = []
    for raw in raw_annotations:
        if not isinstance(raw, dict) or set(raw) != ANNOTATION_FIELDS:
            raise MathFlowError("work-accounting annotation has invalid fields")
        key = _node_key(raw.get("nodeRef"), "annotation node reference")
        if key in annotations:
            raise MathFlowError("work-accounting state annotates one node more than once")
        observed_order.append(key)
        record = nodes.get(key)
        if record is None:
            raise MathFlowError("work-accounting state annotates a node outside knowledge state")
        if raw.get("knowledgeNodeDigest") != record.get("digest"):
            raise MathFlowError("work-accounting annotation knowledge-node digest mismatch")
        _require_digest(raw.get("knowledgeNodeDigest"), "knowledge-node digest")
        direct = _require_canonical_decimal(raw.get("directWorkHours"), "direct work")
        if key == root:
            if raw.get("conditionalIncidence") is not None:
                raise MathFlowError("root program conditional incidence must be null")
        else:
            incidence = _require_probability(raw.get("conditionalIncidence"), "conditional incidence")
            if (
                mode != "no-access"
                and record.get("status") in {"completed", "retired"}
                and incidence != 0
            ):
                raise MathFlowError("completed or retired knowledge nodes must have zero incidence")
        if (
            mode != "no-access"
            and record.get("status") in {"completed", "retired"}
            and direct != 0
        ):
            raise MathFlowError("completed or retired knowledge nodes must have zero direct work")
        if raw.get("annotationDigest") != _annotation_digest(raw):
            raise MathFlowError("work-accounting annotation digest mismatch")
        annotations[key] = raw
    if observed_order != sorted(observed_order):
        raise MathFlowError("work-accounting annotations must be in canonical order")
    if set(annotations) != set(nodes):
        raise MathFlowError("work-accounting state must annotate every program and thread exactly once")

    expected_derived, expected_total = _derive(annotations, parents, root)
    if value.get("derived") != expected_derived:
        raise MathFlowError("work-accounting derived fields are inconsistent with primitives")
    if value.get("totalWorkHours") != expected_total:
        raise MathFlowError("work-accounting total is inconsistent with primitives")
    if value.get("stateDigest") != _content_digest(value, "stateDigest"):
        raise MathFlowError("work-accounting state digest mismatch")
    return value


def _require_sorted_submission_sequence(value: object) -> list[str]:
    if not isinstance(value, list) or any(
        not isinstance(item, str) or not GIT_SHA.fullmatch(item) for item in value
    ):
        raise MathFlowError("processed submission IDs must be canonical transactions")
    if len(value) != len(set(value)):
        raise MathFlowError("processed submission IDs must be unique")
    return list(value)


def make_work_accounting_patch(
    *,
    problem_id: str,
    subject_transaction_id: str,
    evaluation_mode: str,
    root_contract_digest: str,
    base_accounting_state_digest: str,
    base_knowledge_state_digest: str,
    target_knowledge_state_digest: str,
    topology_alignment_digest: str | None,
    updates: Iterable[object],
) -> dict[str, object]:
    normalized_updates: list[dict[str, object]] = []
    for raw in updates:
        if not isinstance(raw, dict) or set(raw) != UPDATE_FIELDS - {"baseAnnotationDigest"}:
            raise MathFlowError("work-accounting patch update input has invalid fields")
        changes = raw.get("changes")
        if not isinstance(changes, dict) or not changes or not set(changes) <= CHANGE_FIELDS:
            raise MathFlowError("work-accounting patch changes must contain primitive fields only")
        normalized_changes: dict[str, object] = {}
        if "directWorkHours" in changes:
            normalized_changes["directWorkHours"] = canonical_decimal(
                changes["directWorkHours"], "direct work"
            )
        if "conditionalIncidence" in changes:
            normalized_changes["conditionalIncidence"] = canonical_decimal(
                changes["conditionalIncidence"], "conditional incidence"
            )
        normalized_updates.append(
            {
                "nodeRef": _node_ref(raw.get("nodeRef"), "patch node reference"),
                "baseAnnotationDigest": None,
                "changes": normalized_changes,
                "rationale": raw.get("rationale"),
                "evidenceRefs": sorted(set(raw.get("evidenceRefs", [])))
                if isinstance(raw.get("evidenceRefs"), list)
                else raw.get("evidenceRefs"),
            }
        )
    normalized_updates.sort(key=lambda item: _node_ref_sort_key(item["nodeRef"]))
    result: dict[str, object] = {
        "schemaVersion": 1,
        "problemId": problem_id,
        "subjectTransactionId": subject_transaction_id,
        "evaluationMode": evaluation_mode,
        "rootContractDigest": root_contract_digest,
        "baseAccountingStateDigest": base_accounting_state_digest,
        "baseKnowledgeStateDigest": base_knowledge_state_digest,
        "targetKnowledgeStateDigest": target_knowledge_state_digest,
        "topologyAlignmentDigest": topology_alignment_digest,
        "updates": normalized_updates,
    }
    # Base annotation guards are filled by bind_patch_to_state before publication.
    result["patchDigest"] = _content_digest(result, "patchDigest")
    return validate_work_accounting_patch(result)


def bind_patch_to_state(patch: object, base_state: object) -> dict[str, object]:
    validated = validate_work_accounting_patch(patch)
    if not isinstance(base_state, dict) or base_state.get("stateDigest") != validated.get(
        "baseAccountingStateDigest"
    ):
        raise MathFlowError("work-accounting patch base state digest mismatch")
    annotations = {
        _node_key(item["nodeRef"]): item
        for item in base_state.get("annotations", [])
        if isinstance(item, dict) and "nodeRef" in item
    }
    result = copy.deepcopy(validated)
    result.pop("patchDigest", None)
    for update in result["updates"]:
        key = _node_key(update["nodeRef"])
        base = annotations.get(key)
        update["baseAnnotationDigest"] = base.get("annotationDigest") if base else None
    result["patchDigest"] = _content_digest(result, "patchDigest")
    return validate_work_accounting_patch(result)


def validate_work_accounting_patch(value: object) -> dict[str, object]:
    if not isinstance(value, dict) or set(value) != PATCH_FIELDS:
        raise MathFlowError("work-accounting patch has an invalid envelope")
    if value.get("schemaVersion") != 1:
        raise MathFlowError("work-accounting patch has an unsupported version")
    _require_identifier(value.get("problemId"), "patch problem ID")
    _require_transaction(value.get("subjectTransactionId"), "patch subject")
    if value.get("evaluationMode") not in PATCH_MODES:
        raise MathFlowError("work-accounting patch has an invalid evaluation mode")
    for field in (
        "rootContractDigest",
        "baseAccountingStateDigest",
        "baseKnowledgeStateDigest",
        "targetKnowledgeStateDigest",
    ):
        _require_digest(value.get(field), field)
    _require_digest(value.get("topologyAlignmentDigest"), "topology alignment digest", nullable=True)
    updates = value.get("updates")
    if not isinstance(updates, list):
        raise MathFlowError("work-accounting patch updates must be an array")
    keys: list[tuple[str, str]] = []
    for update in updates:
        if not isinstance(update, dict) or set(update) != UPDATE_FIELDS:
            raise MathFlowError("work-accounting patch update has invalid fields")
        key = _node_key(update.get("nodeRef"), "patch node reference")
        keys.append(key)
        _require_digest(update.get("baseAnnotationDigest"), "base annotation digest", nullable=True)
        changes = update.get("changes")
        if not isinstance(changes, dict) or not changes or not set(changes) <= CHANGE_FIELDS:
            raise MathFlowError("work-accounting patch changes must contain primitive fields only")
        if "directWorkHours" in changes:
            _require_canonical_decimal(changes["directWorkHours"], "direct work")
        if "conditionalIncidence" in changes:
            _require_probability(changes["conditionalIncidence"], "conditional incidence")
        _require_text(update.get("rationale"), "patch rationale")
        evidence = _require_sorted_unique_strings(update.get("evidenceRefs"), "patch evidence references")
        if not evidence:
            raise MathFlowError("every primitive accounting update requires evidence")
    if keys != sorted(set(keys)):
        raise MathFlowError("work-accounting patch updates must be unique and canonically ordered")
    if value.get("patchDigest") != _content_digest(value, "patchDigest"):
        raise MathFlowError("work-accounting patch digest mismatch")
    return value


def _validate_alignment_binding(
    alignment: object,
    *,
    problem_id: str,
    before_state: Mapping[str, object],
    after_state: Mapping[str, object],
    expected_digest: str,
) -> None:
    if not isinstance(alignment, dict):
        raise MathFlowError("topology alignment must be an object")
    if alignment.get("schemaVersion") != 1 or alignment.get("problemId") != problem_id:
        raise MathFlowError("topology alignment has an invalid identity")
    if alignment.get("beforeKnowledgeStateDigest") != before_state.get("stateDigest"):
        raise MathFlowError("topology alignment has the wrong before state")
    if alignment.get("afterKnowledgeStateDigest") != after_state.get("stateDigest"):
        raise MathFlowError("topology alignment has the wrong after state")
    if alignment.get("alignmentDigest") != expected_digest:
        raise MathFlowError("topology alignment digest does not match the patch")
    if expected_digest != _content_digest(alignment, "alignmentDigest"):
        raise MathFlowError("topology alignment digest mismatch")
    from .research_topology import validate_research_topology_alignment

    validate_research_topology_alignment(alignment, before_state, after_state)


def apply_work_accounting_patch(
    base_state: object,
    patch: object,
    *,
    root_contract: object,
    base_knowledge_state: object,
    target_knowledge_state: object,
    topology_alignment: object | None = None,
) -> dict[str, object]:
    contract = validate_root_contract(root_contract)
    base_knowledge = _validate_knowledge_state(
        base_knowledge_state, str(contract["problemId"])
    )
    target_knowledge = _validate_knowledge_state(
        target_knowledge_state, str(contract["problemId"])
    )
    base = validate_work_accounting_state(base_state, base_knowledge, contract)
    delta = validate_work_accounting_patch(patch)
    if base.get("evaluationMode") == "no-access":
        raise MathFlowError("an ephemeral no-access state cannot be a live predecessor")
    if delta.get("problemId") != contract.get("problemId"):
        raise MathFlowError("work-accounting patch belongs to another problem")
    if delta.get("rootContractDigest") != contract.get("rootContractDigest"):
        raise MathFlowError("work-accounting patch uses another root contract")
    if delta.get("baseAccountingStateDigest") != base.get("stateDigest"):
        raise MathFlowError("work-accounting patch base state digest mismatch")
    if delta.get("baseKnowledgeStateDigest") != base_knowledge.get("stateDigest"):
        raise MathFlowError("work-accounting patch base knowledge-state digest mismatch")
    if base.get("knowledgeStateDigest") != base_knowledge.get("stateDigest"):
        raise MathFlowError("live accounting state and supplied base knowledge state disagree")
    if delta.get("targetKnowledgeStateDigest") != target_knowledge.get("stateDigest"):
        raise MathFlowError("work-accounting patch target knowledge-state digest mismatch")
    subject = str(delta["subjectTransactionId"])
    if subject in base["processedSubmissionIds"]:
        raise MathFlowError("work-accounting submission has already been processed")
    if subject not in target_knowledge["contributions"]:
        raise MathFlowError("work-accounting subject is not accepted in target knowledge state")

    topology_changed = _topology_signature(base_knowledge) != _topology_signature(target_knowledge)
    alignment_digest = delta.get("topologyAlignmentDigest")
    if topology_changed and alignment_digest is None:
        raise MathFlowError("topology-changing accounting patches require builder-derived alignment")
    if alignment_digest is not None:
        _validate_alignment_binding(
            topology_alignment,
            problem_id=str(contract["problemId"]),
            before_state=base_knowledge,
            after_state=target_knowledge,
            expected_digest=str(alignment_digest),
        )
    elif topology_alignment is not None:
        raise MathFlowError("unbound topology alignment may not affect accounting")

    base_annotations = {
        _node_key(item["nodeRef"]): item for item in base["annotations"]
    }
    target_nodes, target_parents, target_root = _knowledge_topology(target_knowledge)
    base_parents = _topology_signature(base_knowledge)
    update_map: dict[tuple[str, str], dict[str, object]] = {}
    for update in delta["updates"]:
        key = _node_key(update["nodeRef"])
        if key in update_map:
            raise MathFlowError("work-accounting patch updates one node more than once")
        if key not in target_nodes:
            raise MathFlowError("work-accounting patch updates a node outside target knowledge state")
        base_annotation = base_annotations.get(key)
        expected_base_digest = (
            base_annotation.get("annotationDigest") if base_annotation else None
        )
        if update.get("baseAnnotationDigest") != expected_base_digest:
            raise MathFlowError("work-accounting patch annotation base guard mismatch")
        if key == target_root and "conditionalIncidence" in update["changes"]:
            raise MathFlowError("root incidence is derived from the root contract and cannot be patched")
        update_map[key] = update

    annotation_inputs: list[dict[str, object]] = []
    for key in sorted(target_nodes):
        base_annotation = base_annotations.get(key)
        update = update_map.get(key)
        if base_annotation is None:
            if update is None or set(update["changes"]) != CHANGE_FIELDS:
                raise MathFlowError("new accounting nodes require complete primitive estimates")
            direct = update["changes"]["directWorkHours"]
            incidence: object = update["changes"]["conditionalIncidence"]
        else:
            direct = base_annotation["directWorkHours"]
            incidence = base_annotation["conditionalIncidence"]
            if update is not None:
                direct = update["changes"].get("directWorkHours", direct)
                incidence = update["changes"].get("conditionalIncidence", incidence)
                changed_value = (
                    direct != base_annotation["directWorkHours"]
                    or incidence != base_annotation["conditionalIncidence"]
                )
                moved = base_parents.get(key) != target_parents.get(key)
                if not changed_value and not moved:
                    raise MathFlowError("work-accounting patch contains a no-op primitive update")
        if key != target_root and base_parents.get(key) != target_parents.get(key):
            if update is None or "conditionalIncidence" not in update["changes"]:
                raise MathFlowError("moved accounting nodes require a re-anchored incidence estimate")
        if key == target_root:
            incidence = None
        annotation_inputs.append(
            {
                "nodeRef": _node_ref_for(key),
                "directWorkHours": direct,
                "conditionalIncidence": incidence,
            }
        )
    processed = list(base["processedSubmissionIds"])
    if delta["evaluationMode"] == "with-access":
        processed.append(subject)
    return build_work_accounting_state(
        root_contract=contract,
        knowledge_state=target_knowledge,
        annotations=annotation_inputs,
        predecessor_state_digest=str(base["stateDigest"]),
        evaluation_mode=str(delta["evaluationMode"]),
        subject_transaction_id=subject,
        processed_submission_ids=processed,
    )


def materialize_submission_work_value(
    *,
    base_state: object,
    no_access_patch: object,
    with_access_patch: object,
    root_contract: object,
    base_knowledge_state: object,
    target_knowledge_state: object,
    topology_alignment: object | None = None,
) -> tuple[dict[str, object], dict[str, object], dict[str, object]]:
    no_patch = validate_work_accounting_patch(no_access_patch)
    with_patch = validate_work_accounting_patch(with_access_patch)
    if no_patch.get("evaluationMode") != "no-access":
        raise MathFlowError("submission work value requires a no-access patch")
    if with_patch.get("evaluationMode") != "with-access":
        raise MathFlowError("submission work value requires a with-access patch")
    identity_fields = {
        "problemId",
        "subjectTransactionId",
        "rootContractDigest",
        "baseAccountingStateDigest",
        "baseKnowledgeStateDigest",
        "targetKnowledgeStateDigest",
        "topologyAlignmentDigest",
    }
    if any(no_patch.get(field) != with_patch.get(field) for field in identity_fields):
        raise MathFlowError("counterfactual patches do not describe the same submission transition")
    no_state = apply_work_accounting_patch(
        base_state,
        no_patch,
        root_contract=root_contract,
        base_knowledge_state=base_knowledge_state,
        target_knowledge_state=target_knowledge_state,
        topology_alignment=topology_alignment,
    )
    with_state = apply_work_accounting_patch(
        base_state,
        with_patch,
        root_contract=root_contract,
        base_knowledge_state=base_knowledge_state,
        target_knowledge_state=target_knowledge_state,
        topology_alignment=topology_alignment,
    )
    no_work = _require_canonical_decimal(no_state["totalWorkHours"], "no-access work")
    with_work = _require_canonical_decimal(with_state["totalWorkHours"], "with-access work")
    work_value = no_work - with_work
    if work_value <= 0:
        raise MathFlowError(
            "submission work value must be strictly positive; counterfactual patches must be re-estimated"
        )
    affected_keys = sorted(
        {
            _node_key(update["nodeRef"])
            for patch_value in (no_patch, with_patch)
            for update in patch_value["updates"]
        }
    )
    result: dict[str, object] = {
        "schemaVersion": 1,
        "problemId": no_patch["problemId"],
        "subjectTransactionId": no_patch["subjectTransactionId"],
        "rootContractDigest": no_patch["rootContractDigest"],
        "baseAccountingStateDigest": no_patch["baseAccountingStateDigest"],
        "baseKnowledgeStateDigest": no_patch["baseKnowledgeStateDigest"],
        "targetKnowledgeStateDigest": no_patch["targetKnowledgeStateDigest"],
        "topologyAlignmentDigest": no_patch["topologyAlignmentDigest"],
        "noAccessPatchDigest": no_patch["patchDigest"],
        "withAccessPatchDigest": with_patch["patchDigest"],
        "noAccessStateDigest": no_state["stateDigest"],
        "withAccessStateDigest": with_state["stateDigest"],
        "noAccessWorkHours": no_state["totalWorkHours"],
        "withAccessWorkHours": with_state["totalWorkHours"],
        "workValueHours": canonical_decimal(work_value),
        "affectedNodeRefs": [_node_ref_for(key) for key in affected_keys],
    }
    result["evaluationDigest"] = _content_digest(result, "evaluationDigest")
    validate_submission_work_value(result)
    return no_state, with_state, result


def validate_submission_work_value(value: object) -> dict[str, object]:
    if not isinstance(value, dict) or set(value) != EVALUATION_FIELDS:
        raise MathFlowError("submission work-value evaluation has an invalid envelope")
    if value.get("schemaVersion") != 1:
        raise MathFlowError("submission work-value evaluation has an unsupported version")
    _require_identifier(value.get("problemId"), "work-value problem ID")
    _require_transaction(value.get("subjectTransactionId"), "work-value subject")
    for field in (
        "rootContractDigest",
        "baseAccountingStateDigest",
        "baseKnowledgeStateDigest",
        "targetKnowledgeStateDigest",
        "noAccessPatchDigest",
        "withAccessPatchDigest",
        "noAccessStateDigest",
        "withAccessStateDigest",
    ):
        _require_digest(value.get(field), field)
    _require_digest(value.get("topologyAlignmentDigest"), "topology alignment digest", nullable=True)
    no_work = _require_canonical_decimal(value.get("noAccessWorkHours"), "no-access work")
    with_work = _require_canonical_decimal(value.get("withAccessWorkHours"), "with-access work")
    work_value = _require_canonical_decimal(value.get("workValueHours"), "submission work value")
    if work_value <= 0 or no_work - with_work != work_value:
        raise MathFlowError("submission work value must equal a strictly positive W-minus minus W-plus")
    refs = value.get("affectedNodeRefs")
    if not isinstance(refs, list):
        raise MathFlowError("affected node references must be an array")
    keys = [_node_key(ref, "affected node reference") for ref in refs]
    if keys != sorted(set(keys)):
        raise MathFlowError("affected node references must be unique and canonically ordered")
    if value.get("evaluationDigest") != _content_digest(value, "evaluationDigest"):
        raise MathFlowError("submission work-value evaluation digest mismatch")
    return value
