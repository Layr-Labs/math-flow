"""Inactive provider-free experiment for bounded Work Accounting V2 slices.

The live V2 protocol sends a complete accounting state to every judgment
stage.  This module tests a narrower trust boundary without changing that
protocol: complete state remains in trusted code, while a prospective judge
would see only an exact writable cut, pure-ancestor aggregates, and collapsed
aggregates for excluded child subtrees.

The experiment never truncates.  A cut which omits a topology-required node or
crosses either configured bound fails closed and must be explicitly widened.
"""

from __future__ import annotations

import copy
import re
from collections.abc import Mapping, Sequence
from fractions import Fraction

from .counterfactual_context import (
    build_impact_subgraph_context,
    validate_impact_subgraph_context,
)
from .errors import MathFlowError
from .repository import sha256_json
from .work_accounting import (
    apply_work_accounting_patch,
    canonical_decimal,
    materialize_submission_work_value,
    validate_root_contract,
    validate_work_accounting_patch,
    validate_work_accounting_state,
)
from .work_accounting_knowledge import (
    validate_work_accounting_knowledge_state,
    validate_work_accounting_topology_alignment,
)


EXPERIMENT_ID = "inactive-provider-free-work-accounting-local-slice-v1"
ACTIVATION_STATUS = "inactive-provider-free-experiment"
DEFAULT_MAX_INCLUDED_NODES = 128
DEFAULT_MAX_BOUNDARY_NODES = 256

_DIGEST = re.compile(r"^sha256:[0-9a-f]{64}$")
_TRANSACTION = re.compile(r"^[0-9a-f]{40}$")
_IDENTIFIER = re.compile(r"^[a-z0-9][a-z0-9/_-]*$")
_MODES = {"no-access", "with-access"}
_CHANGES = {"directWorkHours", "conditionalIncidence"}

_SLICE_FIELDS = {
    "schemaVersion",
    "experimentId",
    "activationStatus",
    "problemId",
    "subjectTransactionId",
    "evaluationMode",
    "rootContractDigest",
    "baseAccountingStateDigest",
    "baseKnowledgeStateDigest",
    "targetKnowledgeStateDigest",
    "topologyAlignmentDigest",
    "impactContextDigest",
    "rootNodeRef",
    "limits",
    "writeScopeNodeRefs",
    "requiredPrimitiveUpdates",
    "exactNodes",
    "ancestorAggregates",
    "boundaryAggregates",
    "sliceDigest",
}
_NODE_FIELDS = {
    "nodeRef",
    "parentRef",
    "status",
    "roles",
    "targetKnowledgeNodeDigest",
    "baseAnnotationDigest",
    "directWorkHours",
    "conditionalIncidence",
    "includedChildRefs",
    "boundaryChildRefs",
    "collapsedBoundaryContributionWorkHours",
    "nodeDigest",
}
_BOUNDARY_FIELDS = {
    "nodeRef",
    "parentRef",
    "targetKnowledgeNodeDigest",
    "rootBaseAnnotationDigest",
    "conditionalIncidence",
    "conditionalSubtreeWorkHours",
    "conditionalContributionWorkHours",
    "programCount",
    "boundaryDigest",
}
_REQUIRED_FIELDS = {"nodeRef", "requiredChanges", "reasons"}


def _content_digest(value: Mapping[str, object], field: str) -> str:
    return "sha256:" + sha256_json(
        {key: copy.deepcopy(item) for key, item in value.items() if key != field}
    )


def _require_digest(value: object, label: str, *, nullable: bool = False) -> str | None:
    if value is None and nullable:
        return None
    if not isinstance(value, str) or not _DIGEST.fullmatch(value):
        raise MathFlowError(f"{label} must be a sha256 digest")
    return value


def _require_ref(value: object, label: str = "node reference") -> dict[str, str]:
    if (
        not isinstance(value, dict)
        or set(value) != {"kind", "id"}
        or value.get("kind") != "program"
        or not isinstance(value.get("id"), str)
        or not _IDENTIFIER.fullmatch(str(value["id"]))
    ):
        raise MathFlowError(f"{label} must be an exact program reference")
    return {"kind": "program", "id": str(value["id"])}


def _key(value: object, label: str = "node reference") -> tuple[str, str]:
    ref = _require_ref(value, label)
    return ref["kind"], ref["id"]


def _ref(key: tuple[str, str]) -> dict[str, str]:
    return {"kind": key[0], "id": key[1]}


def _require_canonical_number(
    value: object, label: str, *, probability: bool = False, nullable: bool = False
) -> Fraction | None:
    if value is None and nullable:
        return None
    normalized = canonical_decimal(value, label)
    if normalized != value:
        raise MathFlowError(f"{label} must be a canonical decimal string")
    result = Fraction(normalized)
    if probability and result > 1:
        raise MathFlowError(f"{label} must be between zero and one")
    return result


def _program_topology(
    knowledge: Mapping[str, object],
) -> tuple[
    dict[tuple[str, str], Mapping[str, object]],
    dict[tuple[str, str], tuple[str, str] | None],
    tuple[str, str],
]:
    if knowledge.get("schemaVersion") != 3:
        raise MathFlowError(
            "local accounting slice experiment supports program-only knowledge state v3"
        )
    raw_programs = knowledge.get("programs")
    if not isinstance(raw_programs, dict):
        raise MathFlowError("local accounting slice requires knowledge programs")
    programs: dict[tuple[str, str], Mapping[str, object]] = {}
    parents: dict[tuple[str, str], tuple[str, str] | None] = {}
    for program_id, raw in raw_programs.items():
        if not isinstance(raw, dict):
            raise MathFlowError("local accounting slice encountered an invalid program")
        key = ("program", str(program_id))
        programs[key] = raw
        parent = raw.get("parentId")
        parents[key] = ("program", str(parent)) if isinstance(parent, str) else None
    root = ("program", str(knowledge["rootProgramId"]))
    if root not in programs or parents[root] is not None:
        raise MathFlowError("local accounting slice has an invalid root")
    return programs, parents, root


def _children(
    parents: Mapping[tuple[str, str], tuple[str, str] | None]
) -> dict[tuple[str, str], list[tuple[str, str]]]:
    result = {key: [] for key in parents}
    for key, parent in parents.items():
        if parent is not None:
            result[parent].append(key)
    for child_keys in result.values():
        child_keys.sort()
    return result


def _annotation_map(
    state: Mapping[str, object],
) -> dict[tuple[str, str], Mapping[str, object]]:
    annotations = state.get("annotations")
    if not isinstance(annotations, list):
        raise MathFlowError("local accounting slice requires accounting annotations")
    return {_key(item["nodeRef"]): item for item in annotations if isinstance(item, dict)}


def _derive_required_updates(
    before: Mapping[str, object],
    after: Mapping[str, object],
    base: Mapping[str, object],
    *,
    evaluation_mode: str,
) -> list[dict[str, object]]:
    """Mirror V2's topology/inactive primitive obligations in trusted code."""

    if evaluation_mode not in _MODES:
        raise MathFlowError("local accounting slice has an invalid evaluation mode")
    before_programs, before_parents, _ = _program_topology(before)
    after_programs, after_parents, root = _program_topology(after)
    base_annotations = _annotation_map(base)
    requirements: dict[tuple[str, str], tuple[set[str], set[str]]] = {}

    def add(key: tuple[str, str], changes: Sequence[str], reason: str) -> None:
        change_set, reasons = requirements.setdefault(key, (set(), set()))
        change_set.update(changes)
        reasons.add(reason)

    for key, record in after_programs.items():
        if key not in before_programs:
            add(key, ("directWorkHours", "conditionalIncidence"), "created")
        elif before_parents[key] != after_parents[key]:
            add(key, ("conditionalIncidence",), "reparented")
        if evaluation_mode == "with-access" and record.get("status") in {
            "completed",
            "retired",
        }:
            annotation = base_annotations.get(key)
            if annotation is not None:
                changes: list[str] = []
                if annotation.get("directWorkHours") != "0":
                    changes.append("directWorkHours")
                if key != root and annotation.get("conditionalIncidence") != "0":
                    changes.append("conditionalIncidence")
                if changes:
                    add(key, changes, "inactive-zeroing")
    if root in requirements:
        requirements[root][0].discard("conditionalIncidence")
    return [
        {
            "nodeRef": _ref(key),
            "requiredChanges": sorted(changes),
            "reasons": sorted(reasons),
        }
        for key, (changes, reasons) in sorted(requirements.items())
        if changes
    ]


def _target_topology_subtree(
    key: tuple[str, str],
    *,
    children: Mapping[tuple[str, str], Sequence[tuple[str, str]]],
    annotations: Mapping[tuple[str, str], Mapping[str, object]],
    forbidden: set[tuple[str, str]],
) -> tuple[Fraction, int]:
    totals: dict[tuple[str, str], Fraction] = {}
    counts: dict[tuple[str, str], int] = {}
    active: set[tuple[str, str]] = set()
    finished: set[tuple[str, str]] = set()
    stack: list[tuple[tuple[str, str], bool]] = [(key, False)]
    while stack:
        current, expanded = stack.pop()
        if expanded:
            annotation = annotations[current]
            direct = _require_canonical_number(
                annotation.get("directWorkHours"), "boundary direct work"
            )
            assert isinstance(direct, Fraction)
            total = direct
            count = 1
            for child in children[current]:
                incidence = _require_canonical_number(
                    annotations[child].get("conditionalIncidence"),
                    "boundary conditional incidence",
                    probability=True,
                )
                assert isinstance(incidence, Fraction)
                total += incidence * totals[child]
                count += counts[child]
            totals[current] = total
            counts[current] = count
            active.remove(current)
            finished.add(current)
            continue
        if current in finished:
            continue
        if current in active:
            raise MathFlowError("local accounting boundary contains a cycle")
        if current in forbidden:
            raise MathFlowError("local accounting boundary overlaps the writable slice")
        if current not in annotations:
            raise MathFlowError(
                "local accounting boundary contains a node without a trusted base primitive"
            )
        active.add(current)
        stack.append((current, True))
        for child in reversed(children[current]):
            stack.append((child, False))
    return totals[key], counts[key]


def _validate_limits(max_included_nodes: int, max_boundary_nodes: int) -> None:
    if (
        isinstance(max_included_nodes, bool)
        or not isinstance(max_included_nodes, int)
        or max_included_nodes < 1
        or isinstance(max_boundary_nodes, bool)
        or not isinstance(max_boundary_nodes, int)
        or max_boundary_nodes < 0
    ):
        raise MathFlowError("local accounting slice limits must be non-negative bounds")


def build_local_accounting_slice(
    *,
    base_state: object,
    root_contract: object,
    base_knowledge_state: object,
    target_knowledge_state: object,
    topology_alignment: object | None,
    impact_context: object,
    evaluation_mode: str,
    max_included_nodes: int = DEFAULT_MAX_INCLUDED_NODES,
    max_boundary_nodes: int = DEFAULT_MAX_BOUNDARY_NODES,
) -> dict[str, object]:
    """Build a bounded, deterministic accounting cut from trusted global state."""

    _validate_limits(max_included_nodes, max_boundary_nodes)
    contract = validate_root_contract(root_contract)
    before = validate_work_accounting_knowledge_state(
        base_knowledge_state, str(contract["problemId"])
    )
    after = validate_work_accounting_knowledge_state(
        target_knowledge_state, str(contract["problemId"])
    )
    base = validate_work_accounting_state(base_state, before, contract)
    if evaluation_mode not in _MODES:
        raise MathFlowError("local accounting slice has an invalid evaluation mode")
    context = validate_impact_subgraph_context(impact_context)
    if context.get("schemaVersion") != 2 or after.get("schemaVersion") != 3:
        raise MathFlowError("local accounting slice requires program-only V2 impact context")
    subject = context.get("subjectTransactionId")
    if (
        not isinstance(subject, str)
        or not _TRANSACTION.fullmatch(subject)
        or context.get("problemId") != contract.get("problemId")
        or context.get("knowledgeStateDigest") != after.get("stateDigest")
    ):
        raise MathFlowError("local accounting slice impact bindings are stale")
    expected_context = build_impact_subgraph_context(
        problem_id=str(contract["problemId"]),
        subject_transaction_id=subject,
        accepted_claim_refs=context["acceptedClaimRefs"],
        research_state=after,
        seed_node_refs=context["seedNodeRefs"],
        descendant_depth=int(context["descendantDepth"]),
    )
    if context != expected_context:
        raise MathFlowError("local accounting slice impact context is not deterministic")

    _, before_parents, _ = _program_topology(before)
    _, after_parents, _ = _program_topology(after)
    topology_changed = before_parents != after_parents
    if topology_changed and topology_alignment is None:
        raise MathFlowError(
            "topology-changing local accounting slice requires exact alignment"
        )
    alignment_digest: str | None = None
    if topology_alignment is not None:
        alignment = validate_work_accounting_topology_alignment(
            topology_alignment, before, after
        )
        alignment_digest = str(alignment["alignmentDigest"])

    programs, parents, root = _program_topology(after)
    child_map = _children(parents)
    base_annotations = _annotation_map(base)
    included_records = context["includedNodes"]
    boundary_records = context["boundarySummaries"]
    assert isinstance(included_records, list) and isinstance(boundary_records, list)
    if len(included_records) > max_included_nodes:
        raise MathFlowError(
            "local accounting slice exceeds included-node bound; widen explicitly"
        )
    if len(boundary_records) > max_boundary_nodes:
        raise MathFlowError(
            "local accounting slice exceeds boundary-node bound; widen explicitly"
        )
    included = {_key(item["ref"]): item for item in included_records}
    if len(included) != len(included_records):
        raise MathFlowError("local accounting slice repeats an included node")
    if root not in included:
        raise MathFlowError("local accounting slice omits the accounting root")

    required = _derive_required_updates(
        before, after, base, evaluation_mode=evaluation_mode
    )
    required_keys = {_key(item["nodeRef"]): item for item in required}
    missing_required = sorted(set(required_keys) - set(included))
    if missing_required:
        raise MathFlowError(
            "local accounting slice omits topology-required nodes: "
            + ", ".join(key[1] for key in missing_required)
        )

    boundary_by_parent: dict[tuple[str, str], list[dict[str, object]]] = {
        key: [] for key in included
    }
    boundary_aggregates: list[dict[str, object]] = []
    boundary_keys: set[tuple[str, str]] = set()
    for summary in boundary_records:
        key = _key(summary["nodeRef"], "boundary node reference")
        parent = _key(summary["parentRef"], "boundary parent reference")
        if key in boundary_keys or key in included or parent not in included:
            raise MathFlowError("local accounting slice has an invalid boundary cut")
        boundary_keys.add(key)
        if parents.get(key) != parent:
            raise MathFlowError("local accounting boundary parent is stale")
        subtree, count = _target_topology_subtree(
            key,
            children=child_map,
            annotations=base_annotations,
            forbidden=set(included),
        )
        root_annotation = base_annotations[key]
        incidence = _require_canonical_number(
            root_annotation.get("conditionalIncidence"),
            "boundary root incidence",
            probability=True,
        )
        assert isinstance(incidence, Fraction)
        if count != summary.get("programCount"):
            raise MathFlowError("local accounting boundary count is stale")
        core: dict[str, object] = {
            "nodeRef": _ref(key),
            "parentRef": _ref(parent),
            "targetKnowledgeNodeDigest": programs[key]["digest"],
            "rootBaseAnnotationDigest": root_annotation["annotationDigest"],
            "conditionalIncidence": canonical_decimal(incidence),
            "conditionalSubtreeWorkHours": canonical_decimal(subtree),
            "conditionalContributionWorkHours": canonical_decimal(incidence * subtree),
            "programCount": count,
        }
        aggregate = {**core, "boundaryDigest": _content_digest(core, "boundaryDigest")}
        boundary_aggregates.append(aggregate)
        boundary_by_parent[parent].append(aggregate)
    boundary_aggregates.sort(key=lambda item: _key(item["nodeRef"]))

    included_children = {
        key: sorted(child for child in child_map[key] if child in included)
        for key in included
    }
    exact_nodes: list[dict[str, object]] = []
    ancestor_aggregates: list[dict[str, object]] = []
    for key in sorted(included):
        context_record = included[key]
        record = programs.get(key)
        if record is None:
            raise MathFlowError("local accounting slice includes an unknown program")
        if (
            context_record.get("recordDigest") != record.get("digest")
            or context_record.get("status") != record.get("status")
            or (
                _key(context_record["parentRef"])
                if context_record.get("parentRef") is not None
                else None
            )
            != parents[key]
        ):
            raise MathFlowError("local accounting slice includes stale program metadata")
        annotation = base_annotations.get(key)
        boundaries = sorted(
            boundary_by_parent[key], key=lambda item: _key(item["nodeRef"])
        )
        core = {
            "nodeRef": _ref(key),
            "parentRef": _ref(parents[key]) if parents[key] is not None else None,
            "status": record["status"],
            "roles": copy.deepcopy(context_record["roles"]),
            "targetKnowledgeNodeDigest": record["digest"],
            "baseAnnotationDigest": (
                annotation["annotationDigest"] if annotation is not None else None
            ),
            "directWorkHours": (
                annotation["directWorkHours"] if annotation is not None else None
            ),
            "conditionalIncidence": (
                annotation["conditionalIncidence"] if annotation is not None else None
            ),
            "includedChildRefs": [_ref(child) for child in included_children[key]],
            "boundaryChildRefs": [item["nodeRef"] for item in boundaries],
            "collapsedBoundaryContributionWorkHours": canonical_decimal(
                sum(
                    (
                        Fraction(str(item["conditionalContributionWorkHours"]))
                        for item in boundaries
                    ),
                    Fraction(0),
                )
            ),
        }
        node = {**core, "nodeDigest": _content_digest(core, "nodeDigest")}
        if context_record.get("roles") == ["ancestor"]:
            ancestor_aggregates.append(node)
        else:
            exact_nodes.append(node)

    core_slice: dict[str, object] = {
        "schemaVersion": 1,
        "experimentId": EXPERIMENT_ID,
        "activationStatus": ACTIVATION_STATUS,
        "problemId": contract["problemId"],
        "subjectTransactionId": subject,
        "evaluationMode": evaluation_mode,
        "rootContractDigest": contract["rootContractDigest"],
        "baseAccountingStateDigest": base["stateDigest"],
        "baseKnowledgeStateDigest": before["stateDigest"],
        "targetKnowledgeStateDigest": after["stateDigest"],
        "topologyAlignmentDigest": alignment_digest,
        "impactContextDigest": context["contextDigest"],
        "rootNodeRef": _ref(root),
        "limits": {
            "maxIncludedNodes": max_included_nodes,
            "maxBoundaryNodes": max_boundary_nodes,
        },
        "writeScopeNodeRefs": [_ref(key) for key in sorted(included)],
        "requiredPrimitiveUpdates": required,
        "exactNodes": exact_nodes,
        "ancestorAggregates": ancestor_aggregates,
        "boundaryAggregates": boundary_aggregates,
    }
    result = {**core_slice, "sliceDigest": _content_digest(core_slice, "sliceDigest")}
    validate_local_accounting_slice(result)
    return result


def _validate_node_records(
    records: object, label: str
) -> list[tuple[str, str]]:
    if not isinstance(records, list):
        raise MathFlowError(f"{label} must be an array")
    keys: list[tuple[str, str]] = []
    for raw in records:
        if not isinstance(raw, dict) or set(raw) != _NODE_FIELDS:
            raise MathFlowError(f"{label} has an invalid node envelope")
        key = _key(raw.get("nodeRef"), f"{label} node reference")
        keys.append(key)
        parent = raw.get("parentRef")
        if parent is not None:
            _require_ref(parent, f"{label} parent reference")
        roles = raw.get("roles")
        if (
            not isinstance(roles, list)
            or roles != sorted(set(roles))
            or any(not isinstance(role, str) or not role for role in roles)
        ):
            raise MathFlowError(f"{label} roles are not canonical")
        _require_digest(raw.get("targetKnowledgeNodeDigest"), f"{label} knowledge digest")
        _require_digest(
            raw.get("baseAnnotationDigest"), f"{label} annotation digest", nullable=True
        )
        has_base = raw.get("baseAnnotationDigest") is not None
        _require_canonical_number(
            raw.get("directWorkHours"), f"{label} direct work", nullable=not has_base
        )
        _require_canonical_number(
            raw.get("conditionalIncidence"),
            f"{label} incidence",
            probability=True,
            nullable=(not has_base or parent is None),
        )
        for field in ("includedChildRefs", "boundaryChildRefs"):
            refs = raw.get(field)
            if not isinstance(refs, list):
                raise MathFlowError(f"{label} child references must be arrays")
            parsed = [_key(ref, f"{label} child reference") for ref in refs]
            if parsed != sorted(set(parsed)):
                raise MathFlowError(f"{label} child references are not canonical")
        _require_canonical_number(
            raw.get("collapsedBoundaryContributionWorkHours"),
            f"{label} collapsed boundary contribution",
        )
        if raw.get("nodeDigest") != _content_digest(raw, "nodeDigest"):
            raise MathFlowError(f"{label} node digest mismatch")
    if keys != sorted(set(keys)):
        raise MathFlowError(f"{label} nodes are not uniquely sorted")
    return keys


def validate_local_accounting_slice(value: object) -> dict[str, object]:
    """Validate the self-contained envelope; trusted application rederives it."""

    if not isinstance(value, dict) or set(value) != _SLICE_FIELDS:
        raise MathFlowError("local accounting slice has an invalid envelope")
    if (
        value.get("schemaVersion") != 1
        or value.get("experimentId") != EXPERIMENT_ID
        or value.get("activationStatus") != ACTIVATION_STATUS
    ):
        raise MathFlowError("local accounting slice is not the inactive V1 experiment")
    if (
        not isinstance(value.get("problemId"), str)
        or not _IDENTIFIER.fullmatch(str(value["problemId"]))
        or not isinstance(value.get("subjectTransactionId"), str)
        or not _TRANSACTION.fullmatch(str(value["subjectTransactionId"]))
        or value.get("evaluationMode") not in _MODES
    ):
        raise MathFlowError("local accounting slice has invalid identity fields")
    for field in (
        "rootContractDigest",
        "baseAccountingStateDigest",
        "baseKnowledgeStateDigest",
        "targetKnowledgeStateDigest",
        "impactContextDigest",
    ):
        _require_digest(value.get(field), field)
    _require_digest(value.get("topologyAlignmentDigest"), "topology alignment digest", nullable=True)
    root = _key(value.get("rootNodeRef"), "local accounting root")
    limits = value.get("limits")
    if not isinstance(limits, dict) or set(limits) != {
        "maxIncludedNodes",
        "maxBoundaryNodes",
    }:
        raise MathFlowError("local accounting slice limits have an invalid envelope")
    _validate_limits(limits["maxIncludedNodes"], limits["maxBoundaryNodes"])

    scope = value.get("writeScopeNodeRefs")
    if not isinstance(scope, list):
        raise MathFlowError("local accounting slice write scope must be an array")
    scope_keys = [_key(ref, "write-scope node reference") for ref in scope]
    if scope_keys != sorted(set(scope_keys)) or root not in scope_keys:
        raise MathFlowError("local accounting slice write scope is not canonical")
    if len(scope_keys) > limits["maxIncludedNodes"]:
        raise MathFlowError("local accounting slice exceeds its included-node bound")

    exact_keys = _validate_node_records(value.get("exactNodes"), "exact local slice")
    ancestor_keys = _validate_node_records(
        value.get("ancestorAggregates"), "ancestor aggregate"
    )
    if sorted([*exact_keys, *ancestor_keys]) != scope_keys:
        raise MathFlowError("local accounting slice node records do not match write scope")

    raw_boundaries = value.get("boundaryAggregates")
    if not isinstance(raw_boundaries, list):
        raise MathFlowError("local accounting boundaries must be an array")
    boundary_keys: list[tuple[str, str]] = []
    boundary_parents: dict[tuple[str, str], list[tuple[str, str]]] = {}
    for raw in raw_boundaries:
        if not isinstance(raw, dict) or set(raw) != _BOUNDARY_FIELDS:
            raise MathFlowError("local accounting boundary has an invalid envelope")
        key = _key(raw.get("nodeRef"), "boundary node reference")
        parent = _key(raw.get("parentRef"), "boundary parent reference")
        if key in scope_keys or parent not in scope_keys:
            raise MathFlowError("local accounting boundary escapes the exact cut")
        boundary_keys.append(key)
        boundary_parents.setdefault(parent, []).append(key)
        _require_digest(raw.get("targetKnowledgeNodeDigest"), "boundary knowledge digest")
        _require_digest(raw.get("rootBaseAnnotationDigest"), "boundary annotation digest")
        _require_canonical_number(
            raw.get("conditionalIncidence"), "boundary incidence", probability=True
        )
        _require_canonical_number(
            raw.get("conditionalSubtreeWorkHours"), "boundary subtree work"
        )
        _require_canonical_number(
            raw.get("conditionalContributionWorkHours"), "boundary contribution"
        )
        if (
            isinstance(raw.get("programCount"), bool)
            or not isinstance(raw.get("programCount"), int)
            or raw["programCount"] < 1
        ):
            raise MathFlowError("local accounting boundary program count is invalid")
        if raw.get("boundaryDigest") != _content_digest(raw, "boundaryDigest"):
            raise MathFlowError("local accounting boundary digest mismatch")
    if boundary_keys != sorted(set(boundary_keys)):
        raise MathFlowError("local accounting boundaries are not uniquely sorted")
    if len(boundary_keys) > limits["maxBoundaryNodes"]:
        raise MathFlowError("local accounting slice exceeds its boundary-node bound")

    records = {
        _key(item["nodeRef"]): item
        for item in [*value["exactNodes"], *value["ancestorAggregates"]]
    }
    if any(item["roles"] == ["ancestor"] for item in value["exactNodes"]) or any(
        item["roles"] != ["ancestor"] for item in value["ancestorAggregates"]
    ):
        raise MathFlowError("local accounting ancestor classification is inconsistent")
    observed_parent: dict[tuple[str, str], tuple[str, str] | None] = {}
    observed_as_child: dict[tuple[str, str], tuple[str, str]] = {}
    for key, record in records.items():
        included_children = [_key(ref) for ref in record["includedChildRefs"]]
        boundary_children = [_key(ref) for ref in record["boundaryChildRefs"]]
        if boundary_children != sorted(boundary_parents.get(key, [])):
            raise MathFlowError("local accounting node boundary references disagree")
        if any(child not in records for child in included_children):
            raise MathFlowError("local accounting node names an unknown included child")
        parent = (
            _key(record["parentRef"])
            if record.get("parentRef") is not None
            else None
        )
        observed_parent[key] = parent
        for child in included_children:
            if child in observed_as_child:
                raise MathFlowError("local accounting node has multiple included parents")
            observed_as_child[child] = key
        expected_collapsed = sum(
            (
                Fraction(str(item["conditionalContributionWorkHours"]))
                for item in raw_boundaries
                if _key(item["parentRef"]) == key
            ),
            Fraction(0),
        )
        if record["collapsedBoundaryContributionWorkHours"] != canonical_decimal(
            expected_collapsed
        ):
            raise MathFlowError("local accounting ancestor/boundary aggregate mismatch")
    if observed_parent[root] is not None:
        raise MathFlowError("local accounting root must have no parent")
    for key, parent in observed_parent.items():
        if key == root:
            continue
        if parent not in records or observed_as_child.get(key) != parent:
            raise MathFlowError("local accounting parent/child edges are not reciprocal")
    for raw in raw_boundaries:
        incidence = Fraction(str(raw["conditionalIncidence"]))
        subtree = Fraction(str(raw["conditionalSubtreeWorkHours"]))
        if raw["conditionalContributionWorkHours"] != canonical_decimal(
            incidence * subtree
        ):
            raise MathFlowError("local accounting boundary contribution is inconsistent")

    raw_required = value.get("requiredPrimitiveUpdates")
    if not isinstance(raw_required, list):
        raise MathFlowError("local accounting required updates must be an array")
    required_keys: list[tuple[str, str]] = []
    for raw in raw_required:
        if not isinstance(raw, dict) or set(raw) != _REQUIRED_FIELDS:
            raise MathFlowError("local accounting required update has an invalid envelope")
        key = _key(raw.get("nodeRef"), "required update node reference")
        required_keys.append(key)
        changes = raw.get("requiredChanges")
        reasons = raw.get("reasons")
        if (
            not isinstance(changes, list)
            or not changes
            or changes != sorted(set(changes))
            or not set(changes) <= _CHANGES
            or not isinstance(reasons, list)
            or not reasons
            or reasons != sorted(set(reasons))
            or any(not isinstance(reason, str) or not reason for reason in reasons)
            or key not in scope_keys
        ):
            raise MathFlowError("local accounting required update is invalid")
    if required_keys != sorted(set(required_keys)):
        raise MathFlowError("local accounting required updates are not uniquely sorted")
    if value.get("sliceDigest") != _content_digest(value, "sliceDigest"):
        raise MathFlowError("local accounting slice digest mismatch")
    return value


def _assert_patch_bound_to_slice(
    slice_value: Mapping[str, object], patch: Mapping[str, object]
) -> None:
    fields = {
        "problemId": "problemId",
        "subjectTransactionId": "subjectTransactionId",
        "evaluationMode": "evaluationMode",
        "rootContractDigest": "rootContractDigest",
        "baseAccountingStateDigest": "baseAccountingStateDigest",
        "baseKnowledgeStateDigest": "baseKnowledgeStateDigest",
        "targetKnowledgeStateDigest": "targetKnowledgeStateDigest",
        "topologyAlignmentDigest": "topologyAlignmentDigest",
    }
    if any(
        patch.get(patch_field) != slice_value.get(slice_field)
        for patch_field, slice_field in fields.items()
    ):
        raise MathFlowError("local accounting patch identity does not match its slice")
    scope = {_key(ref) for ref in slice_value["writeScopeNodeRefs"]}
    updates = {_key(item["nodeRef"]): item for item in patch["updates"]}
    escaped = sorted(set(updates) - scope)
    if escaped:
        raise MathFlowError(
            "local accounting patch updates outside its exact write scope: "
            + ", ".join(key[1] for key in escaped)
        )
    required = {
        _key(item["nodeRef"]): set(item["requiredChanges"])
        for item in slice_value["requiredPrimitiveUpdates"]
    }
    for key, changes in required.items():
        update = updates.get(key)
        if update is None or not changes <= set(update["changes"]):
            raise MathFlowError(
                "local accounting patch omits a topology-required primitive estimate"
            )


def reduce_local_accounting_slice(
    slice_value: object, patch_value: object
) -> str:
    """Reduce only the bounded cut and return its exact root total."""

    slice_data = validate_local_accounting_slice(slice_value)
    patch = validate_work_accounting_patch(patch_value)
    _assert_patch_bound_to_slice(slice_data, patch)
    records = {
        _key(item["nodeRef"]): item
        for item in [*slice_data["exactNodes"], *slice_data["ancestorAggregates"]]
    }
    updates = {_key(item["nodeRef"]): item for item in patch["updates"]}
    children = {
        key: [_key(ref) for ref in record["includedChildRefs"]]
        for key, record in records.items()
    }
    values: dict[tuple[str, str], tuple[Fraction, Fraction | None]] = {}
    for key, record in records.items():
        update = updates.get(key)
        changes = update["changes"] if update is not None else {}
        direct_value = changes.get("directWorkHours", record["directWorkHours"])
        incidence_value = changes.get(
            "conditionalIncidence", record["conditionalIncidence"]
        )
        if direct_value is None:
            raise MathFlowError("local accounting patch leaves a new node without direct work")
        direct = _require_canonical_number(direct_value, "local direct work")
        incidence = _require_canonical_number(
            incidence_value,
            "local conditional incidence",
            probability=True,
            nullable=record["parentRef"] is None,
        )
        assert isinstance(direct, Fraction)
        values[key] = (direct, incidence)

    root = _key(slice_data["rootNodeRef"])
    totals: dict[tuple[str, str], Fraction] = {}
    active: set[tuple[str, str]] = set()
    visited: set[tuple[str, str]] = set()
    stack: list[tuple[tuple[str, str], bool]] = [(root, False)]
    while stack:
        key, expanded = stack.pop()
        if expanded:
            direct, _ = values[key]
            total = direct + Fraction(
                str(records[key]["collapsedBoundaryContributionWorkHours"])
            )
            for child in children[key]:
                _, incidence = values[child]
                if incidence is None:
                    raise MathFlowError(
                        "non-root local accounting node has null incidence"
                    )
                total += incidence * totals[child]
            totals[key] = total
            active.remove(key)
            visited.add(key)
            continue
        if key in visited:
            continue
        if key in active:
            raise MathFlowError("local accounting slice contains a cycle")
        active.add(key)
        stack.append((key, True))
        for child in reversed(children[key]):
            stack.append((child, False))
    if visited != set(records):
        raise MathFlowError("local accounting slice contains unreachable nodes")
    return canonical_decimal(totals[root])


def apply_local_accounting_slice_patch(
    *,
    base_state: object,
    patch: object,
    local_slice: object,
    root_contract: object,
    base_knowledge_state: object,
    target_knowledge_state: object,
    topology_alignment: object | None,
    impact_context: object,
) -> dict[str, object]:
    """Rebind a local patch to trusted global state, then apply unchanged V2."""

    slice_data = validate_local_accounting_slice(local_slice)
    limits = slice_data["limits"]
    assert isinstance(limits, dict)
    expected = build_local_accounting_slice(
        base_state=base_state,
        root_contract=root_contract,
        base_knowledge_state=base_knowledge_state,
        target_knowledge_state=target_knowledge_state,
        topology_alignment=topology_alignment,
        impact_context=impact_context,
        evaluation_mode=str(slice_data["evaluationMode"]),
        max_included_nodes=int(limits["maxIncludedNodes"]),
        max_boundary_nodes=int(limits["maxBoundaryNodes"]),
    )
    if slice_data != expected:
        raise MathFlowError("local accounting slice is stale or boundary-tampered")
    validated_patch = validate_work_accounting_patch(patch)
    _assert_patch_bound_to_slice(slice_data, validated_patch)
    predicted_total = reduce_local_accounting_slice(slice_data, validated_patch)
    global_state = apply_work_accounting_patch(
        base_state,
        validated_patch,
        root_contract=root_contract,
        base_knowledge_state=base_knowledge_state,
        target_knowledge_state=target_knowledge_state,
        topology_alignment=topology_alignment,
    )
    if global_state.get("totalWorkHours") != predicted_total:
        raise MathFlowError(
            "local accounting aggregate does not reproduce the trusted global reducer"
        )
    return global_state


def materialize_local_slice_submission_work_value(
    *,
    base_state: object,
    no_access_patch: object,
    with_access_patch: object,
    no_access_slice: object,
    with_access_slice: object,
    root_contract: object,
    base_knowledge_state: object,
    target_knowledge_state: object,
    topology_alignment: object | None,
    impact_context: object,
) -> tuple[dict[str, object], dict[str, object], dict[str, object]]:
    """Materialize W-/W+/D and assert byte-exact full-reducer equivalence."""

    local_no = apply_local_accounting_slice_patch(
        base_state=base_state,
        patch=no_access_patch,
        local_slice=no_access_slice,
        root_contract=root_contract,
        base_knowledge_state=base_knowledge_state,
        target_knowledge_state=target_knowledge_state,
        topology_alignment=topology_alignment,
        impact_context=impact_context,
    )
    local_with = apply_local_accounting_slice_patch(
        base_state=base_state,
        patch=with_access_patch,
        local_slice=with_access_slice,
        root_contract=root_contract,
        base_knowledge_state=base_knowledge_state,
        target_knowledge_state=target_knowledge_state,
        topology_alignment=topology_alignment,
        impact_context=impact_context,
    )
    full_no, full_with, evaluation = materialize_submission_work_value(
        base_state=base_state,
        no_access_patch=no_access_patch,
        with_access_patch=with_access_patch,
        root_contract=root_contract,
        base_knowledge_state=base_knowledge_state,
        target_knowledge_state=target_knowledge_state,
        topology_alignment=topology_alignment,
    )
    if local_no != full_no or local_with != full_with:
        raise MathFlowError("local accounting materialization diverges from full V2")
    return local_no, local_with, evaluation


def build_frozen_with_access_local_snapshot(
    *,
    frozen_with_access_state: object,
    root_contract: object,
    target_knowledge_state: object,
    impact_context: object,
    max_included_nodes: int = DEFAULT_MAX_INCLUDED_NODES,
    max_boundary_nodes: int = DEFAULT_MAX_BOUNDARY_NODES,
) -> dict[str, object]:
    """Collapse a frozen W+ state for provider-free W- size experiments.

    This is deliberately a snapshot, not an accounting predecessor and not an
    activation API.  It reuses the exact slice constructor with identical base
    and target topology, then removes patch-stage identity fields which would
    falsely suggest that the frozen W+ state may be advanced as a live state.
    """

    structural = build_local_accounting_slice(
        base_state=frozen_with_access_state,
        root_contract=root_contract,
        base_knowledge_state=target_knowledge_state,
        target_knowledge_state=target_knowledge_state,
        topology_alignment=None,
        impact_context=impact_context,
        evaluation_mode="no-access",
        max_included_nodes=max_included_nodes,
        max_boundary_nodes=max_boundary_nodes,
    )
    state = frozen_with_access_state
    if not isinstance(state, dict) or state.get("evaluationMode") != "with-access":
        raise MathFlowError("frozen local snapshot requires a with-access state")
    core: dict[str, object] = {
        "schemaVersion": 1,
        "experimentId": EXPERIMENT_ID,
        "activationStatus": ACTIVATION_STATUS,
        "problemId": structural["problemId"],
        "subjectTransactionId": structural["subjectTransactionId"],
        "frozenWithAccessStateDigest": state["stateDigest"],
        "knowledgeStateDigest": structural["targetKnowledgeStateDigest"],
        "impactContextDigest": structural["impactContextDigest"],
        "rootNodeRef": structural["rootNodeRef"],
        "limits": structural["limits"],
        "exactNodes": structural["exactNodes"],
        "ancestorAggregates": structural["ancestorAggregates"],
        "boundaryAggregates": structural["boundaryAggregates"],
    }
    return {
        **core,
        "snapshotDigest": _content_digest(core, "snapshotDigest"),
    }
