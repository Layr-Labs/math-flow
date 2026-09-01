"""Deterministic zero-provider probe for the inactive accounting slice."""

from __future__ import annotations

import copy
import json
import math
from collections.abc import Mapping, Sequence
from dataclasses import asdict
from pathlib import Path

from .builder_scale import SyntheticBuilderStateConfig, build_synthetic_builder_fixture
from .counterfactual_context import build_impact_subgraph_context
from .errors import MathFlowError
from .research_builder_v7 import apply_research_builder_v7_transition
from .repository import sha256_json
from .work_accounting import (
    bind_patch_to_state,
    make_work_accounting_patch,
    materialize_submission_work_value,
)
from .work_accounting_local_slice import (
    DEFAULT_MAX_BOUNDARY_NODES,
    DEFAULT_MAX_INCLUDED_NODES,
    build_frozen_with_access_local_snapshot,
    build_local_accounting_slice,
    materialize_local_slice_submission_work_value,
)
from .work_accounting_scale import (
    ASSESSMENT,
    JUDGMENT,
    SUBJECT,
    WorkAccountingScaleConfig,
    _active_leaf,
    _add_result_to_program,
    _base_accounting_state,
    _build_transition,
    _program_children,
    _result_value,
    _root_contract,
    default_work_accounting_scale_configurations,
)


PROBE_ID = "provider-free-work-accounting-local-slice-v1"
SCENARIOS = (
    "direct",
    "dependency",
    "subtree",
    "topology-alignment",
    "completed-node",
    "broad-scope",
)
TOKEN_ESTIMATE_METHOD = "ceil(compact-json-utf8-bytes/4)"
_WIDE_LIMIT = 4096


def compact_json_bytes(value: object) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode("utf-8")


def measure(value: object) -> dict[str, object]:
    size = len(compact_json_bytes(value))
    return {
        "utf8Bytes": size,
        "estimatedTokens": math.ceil(size / 4),
        "estimatedTokenMethod": TOKEN_ESTIMATE_METHOD,
    }


def _fixture_scenario(scenario: str) -> str:
    return {
        "direct": "broad-local-subtree",
        "dependency": "dependency-closure",
        "subtree": "broad-local-subtree",
        "topology-alignment": "topology-revision",
        "completed-node": "solving-zero-out",
        "broad-scope": "broad-local-subtree",
    }[scenario]


def _local_transition(
    fixture: Mapping[str, object], *, program_id: str, scenario: str
) -> tuple[dict[str, object], list[str], list[str], None]:
    state = fixture["state"]
    assert isinstance(state, dict)
    programs = state["programs"]
    assert isinstance(programs, dict)
    transition = {
        "schemaVersion": 1,
        "subjectTransactionId": SUBJECT,
        "baseStateDigest": state["stateDigest"],
        "contentOperations": [
            {
                "entityKind": "program",
                "entityId": program_id,
                "baseDigest": programs[program_id]["digest"],
                "value": _add_result_to_program(state, program_id),
            },
            {
                "entityKind": "intermediateResult",
                "entityId": "result/work-accounting-probe",
                "baseDigest": None,
                "value": _result_value(
                    primary_program_id=program_id,
                    dependency_result_ids=[],
                    scenario=scenario,
                ),
            },
        ],
        "topologyOperations": [],
        "contribution": {
            "claimKeys": ["claim/current"],
            "directProgramIds": [program_id],
            "intermediateResultIds": ["result/work-accounting-probe"],
        },
        "placementAudit": {
            "basis": "local-objective",
            "rationale": "The deterministic contribution advances this bounded package.",
            "relatedProgramIds": [program_id],
        },
        "topologyRationale": None,
    }
    return transition, [program_id], [], None


def _decisive_completion_transition(
    fixture: Mapping[str, object], *, program_id: str
) -> tuple[dict[str, object], list[str], list[str], str]:
    state = fixture["state"]
    assert isinstance(state, dict)
    programs = state["programs"]
    assert isinstance(programs, dict)
    children = _program_children(state)
    subtree: list[str] = []
    queue = [program_id]
    while queue:
        current = queue.pop(0)
        subtree.append(current)
        queue.extend(children[current])
    operations: list[dict[str, object]] = []
    for current in sorted(subtree):
        raw = programs[current]
        assert isinstance(raw, dict)
        value = {
            key: copy.deepcopy(item) for key, item in raw.items() if key != "digest"
        }
        value["status"] = "completed"
        value["currentStateSummary"] = (
            "The deterministic decisive result completes this work package."
        )
        value["localResidualSummary"] = "No local residual work remains."
        value["sourceTransactionIds"] = sorted(
            {*map(str, value["sourceTransactionIds"]), SUBJECT}
        )
        operations.append(
            {
                "entityKind": "program",
                "entityId": current,
                "baseDigest": raw["digest"],
                "value": value,
            }
        )
    operations.append(
        {
            "entityKind": "program",
            "entityId": "root",
            "baseDigest": programs["root"]["digest"],
            "value": _add_result_to_program(state, "root"),
        }
    )
    operations.append(
        {
            "entityKind": "intermediateResult",
            "entityId": "result/work-accounting-probe",
            "baseDigest": None,
            "value": _result_value(
                primary_program_id="root",
                dependency_result_ids=[],
                scenario="completed-node",
            ),
        }
    )
    transition = {
        "schemaVersion": 1,
        "subjectTransactionId": SUBJECT,
        "baseStateDigest": state["stateDigest"],
        "contentOperations": operations,
        "topologyOperations": [],
        "contribution": {
            "claimKeys": ["claim/current"],
            "directProgramIds": ["root"],
            "intermediateResultIds": ["result/work-accounting-probe"],
        },
        "placementAudit": {
            "basis": "canonical-objective",
            "rationale": "The decisive result completes the selected subtree.",
            "relatedProgramIds": [],
        },
        "topologyRationale": None,
    }
    return transition, [program_id], [], program_id


def _descendant_depth(config: WorkAccountingScaleConfig, scenario: str) -> int:
    if scenario == "direct":
        return 0
    if scenario == "subtree":
        return min(1, config.descendant_depth)
    return config.descendant_depth


def _build_fixture(
    configuration: WorkAccountingScaleConfig, scenario: str
) -> dict[str, object]:
    config = configuration.validate()
    fixture = build_synthetic_builder_fixture(
        SyntheticBuilderStateConfig(
            program_count=config.program_count,
            result_count=config.result_count,
            maximum_depth=config.maximum_depth,
            maximum_width=config.hot_branch_width,
            provenance_per_result=1,
            dependency_depth=config.dependency_depth,
            dependency_width=config.dependency_width,
            support_bytes=96,
            summary_bytes=96,
            evidence_bytes=config.evidence_bytes,
            challenges=("dependency-closure",),
        )
    )
    before = fixture["state"]
    assert isinstance(before, dict)
    if scenario == "direct":
        transition, seed_ids, _, solving_program_id = _local_transition(
            fixture,
            program_id=_active_leaf(before),
            scenario=scenario,
        )
    elif scenario == "subtree":
        leaf_id = _active_leaf(before)
        transition, seed_ids, _, solving_program_id = _local_transition(
            fixture,
            program_id=leaf_id,
            scenario=scenario,
        )
    elif scenario == "completed-node":
        leaf_id = _active_leaf(before)
        parent_id = before["programs"][leaf_id].get("parentId")
        if not isinstance(parent_id, str) or parent_id == "root":
            raise MathFlowError("decisive completion probe needs an internal package")
        transition, seed_ids, _, solving_program_id = (
            _decisive_completion_transition(fixture, program_id=parent_id)
        )
    else:
        transition, seed_ids, _, solving_program_id = _build_transition(
            fixture, _fixture_scenario(scenario)
        )
    dependency_transactions: list[str] = []
    if scenario == "dependency":
        results = before["intermediateResults"]
        assert isinstance(results, dict)
        result_id = transition["contentOperations"][-1]["value"][
            "dependencyResultIds"
        ][0]
        dependency_transactions = [
            str(results[result_id]["sourceTransactionIds"][0])
        ]
    reduced = apply_research_builder_v7_transition(
        before,
        transition,
        accepted_claims=[
            {
                "claimKey": "claim/current",
                "statement": "The deterministic local-slice probe claim is accepted.",
                "dependencyTransactionIds": dependency_transactions,
            }
        ],
        judgment_id=JUDGMENT,
    )
    after = reduced["postState"]
    alignment = reduced["topologyAlignment"]
    assert isinstance(after, dict) and isinstance(alignment, dict)
    contract = _root_contract()
    base = _base_accounting_state(before, contract)
    claims = [
        {
            "transactionId": SUBJECT,
            "claimKey": "claim/current",
            "judgmentId": JUDGMENT,
            "assessmentDigest": ASSESSMENT,
        }
    ]
    impact = build_impact_subgraph_context(
        problem_id="synthetic-builder-scale",
        subject_transaction_id=SUBJECT,
        accepted_claim_refs=claims,
        research_state=after,
        seed_node_refs=[
            {"kind": "program", "id": str(program_id)}
            for program_id in sorted(set(seed_ids))
        ],
        descendant_depth=_descendant_depth(config, scenario),
    )
    return {
        "configuration": config,
        "scenario": scenario,
        "before": before,
        "after": after,
        "alignment": alignment,
        "contract": contract,
        "base": base,
        "impact": impact,
        "seedIds": sorted(set(map(str, seed_ids))),
        "solvingProgramId": solving_program_id,
    }


def _annotation_map(state: Mapping[str, object]) -> dict[str, Mapping[str, object]]:
    return {
        str(item["nodeRef"]["id"]): item
        for item in state["annotations"]
        if isinstance(item, dict) and isinstance(item.get("nodeRef"), dict)
    }


def _selected_update_ids(
    fixture: Mapping[str, object], wide_slice: Mapping[str, object]
) -> set[str]:
    scenario = str(fixture["scenario"])
    required = {
        str(item["nodeRef"]["id"])
        for item in wide_slice["requiredPrimitiveUpdates"]
    }
    seed_ids = list(map(str, fixture["seedIds"]))
    selected = set(required)
    records = [*wide_slice["exactNodes"], *wide_slice["ancestorAggregates"]]
    active = [
        str(item["nodeRef"]["id"])
        for item in records
        if item["status"] == "active" and item["directWorkHours"] is not None
    ]
    if scenario in {"topology-alignment", "completed-node"}:
        selected.add("root")
    elif scenario in {"direct", "dependency"}:
        selected.add(seed_ids[0])
    elif scenario == "subtree":
        # The synthetic widening fixture is shallow and wide.  The seed's
        # sibling-decision set is therefore the exact local work-package
        # subtree available at this cut; update several independent children
        # rather than silently expanding across the root boundary.
        selected.update(active[: min(8, len(active))])
    elif scenario == "broad-scope":
        selected.update(active[: min(32, len(active))])
    else:
        raise MathFlowError(f"unsupported local-slice scenario: {scenario}")
    return selected


def _make_patch(
    fixture: Mapping[str, object],
    wide_slice: Mapping[str, object],
    *,
    mode: str,
) -> dict[str, object]:
    base = fixture["base"]
    after = fixture["after"]
    alignment = fixture["alignment"]
    contract = fixture["contract"]
    assert all(isinstance(item, dict) for item in (base, after, alignment, contract))
    base_annotations = _annotation_map(base)
    programs = after["programs"]
    required = {
        str(item["nodeRef"]["id"]): set(map(str, item["requiredChanges"]))
        for item in wide_slice["requiredPrimitiveUpdates"]
    }
    updates: list[dict[str, object]] = []
    for program_id in sorted(_selected_update_ids(fixture, wide_slice)):
        annotation = base_annotations.get(program_id)
        changes: dict[str, object] = {}
        target_status = programs[program_id]["status"]
        required_changes = required.get(program_id, set())
        if mode == "with-access" and target_status in {"completed", "retired"}:
            changes["directWorkHours"] = "0"
            if program_id != "root":
                changes["conditionalIncidence"] = "0"
        else:
            if annotation is None:
                changes["directWorkHours"] = "6" if mode == "with-access" else "12"
                if program_id != "root":
                    changes["conditionalIncidence"] = (
                        "0.4" if mode == "with-access" else "0.6"
                    )
            else:
                old_direct = int(str(annotation["directWorkHours"]))
                changes["directWorkHours"] = str(
                    max(1, old_direct - 2)
                    if mode == "with-access"
                    else old_direct + 2
                )
                if "conditionalIncidence" in required_changes:
                    changes["conditionalIncidence"] = (
                        "0.4" if mode == "with-access" else "0.6"
                    )
        for field in required_changes:
            if field == "directWorkHours" and field not in changes:
                changes[field] = "6" if mode == "with-access" else "12"
            if field == "conditionalIncidence" and field not in changes:
                changes[field] = "0.4" if mode == "with-access" else "0.6"
        updates.append(
            {
                "nodeRef": {"kind": "program", "id": program_id},
                "changes": changes,
                "rationale": f"Deterministic {mode} local-slice probe estimate.",
                "evidenceRefs": [f"synthetic:{fixture['scenario']}:{mode}"],
            }
        )
    patch = make_work_accounting_patch(
        problem_id="synthetic-builder-scale",
        subject_transaction_id=SUBJECT,
        evaluation_mode=mode,
        root_contract_digest=str(contract["rootContractDigest"]),
        base_accounting_state_digest=str(base["stateDigest"]),
        base_knowledge_state_digest=str(fixture["before"]["stateDigest"]),
        target_knowledge_state_digest=str(after["stateDigest"]),
        topology_alignment_digest=str(alignment["alignmentDigest"]),
        updates=updates,
    )
    return bind_patch_to_state(patch, base)


def build_local_slice_probe_case(
    configuration: WorkAccountingScaleConfig,
    scenario: str,
    *,
    max_included_nodes: int = DEFAULT_MAX_INCLUDED_NODES,
    max_boundary_nodes: int = DEFAULT_MAX_BOUNDARY_NODES,
) -> dict[str, object]:
    """Run one full-reducer oracle and one bounded local-slice replay."""

    if scenario not in SCENARIOS:
        raise MathFlowError(f"unsupported local-slice scenario: {scenario}")
    fixture = _build_fixture(configuration, scenario)
    kwargs = {
        "base_state": fixture["base"],
        "root_contract": fixture["contract"],
        "base_knowledge_state": fixture["before"],
        "target_knowledge_state": fixture["after"],
        "topology_alignment": fixture["alignment"],
        "impact_context": fixture["impact"],
    }
    wide_with = build_local_accounting_slice(
        **kwargs,
        evaluation_mode="with-access",
        max_included_nodes=_WIDE_LIMIT,
        max_boundary_nodes=_WIDE_LIMIT,
    )
    wide_no = build_local_accounting_slice(
        **kwargs,
        evaluation_mode="no-access",
        max_included_nodes=_WIDE_LIMIT,
        max_boundary_nodes=_WIDE_LIMIT,
    )
    with_patch = _make_patch(fixture, wide_with, mode="with-access")
    no_patch = _make_patch(fixture, wide_no, mode="no-access")
    full_no, full_with, full_evaluation = materialize_submission_work_value(
        base_state=fixture["base"],
        no_access_patch=no_patch,
        with_access_patch=with_patch,
        root_contract=fixture["contract"],
        base_knowledge_state=fixture["before"],
        target_knowledge_state=fixture["after"],
        topology_alignment=fixture["alignment"],
    )
    shape = {
        "programCount": len(fixture["before"]["programs"]),
        "impactIncludedNodeCount": len(fixture["impact"]["includedNodes"]),
        "impactBoundaryNodeCount": len(fixture["impact"]["boundarySummaries"]),
        "withAccessRequiredUpdateCount": len(
            wide_with["requiredPrimitiveUpdates"]
        ),
        "noAccessRequiredUpdateCount": len(wide_no["requiredPrimitiveUpdates"]),
        "withAccessPatchUpdateCount": len(with_patch["updates"]),
        "noAccessPatchUpdateCount": len(no_patch["updates"]),
    }
    base_result: dict[str, object] = {
        "schemaVersion": 1,
        "scenario": scenario,
        "configuration": asdict(configuration),
        "bounds": {
            "maxIncludedNodes": max_included_nodes,
            "maxBoundaryNodes": max_boundary_nodes,
            "policy": "fail-closed-never-truncate",
        },
        "stateShape": shape,
        "fullStateOracle": {
            "baseAccountingState": measure(fixture["base"]),
            "noAccessState": measure(full_no),
            "withAccessState": measure(full_with),
            "noAccessStateDigest": full_no["stateDigest"],
            "withAccessStateDigest": full_with["stateDigest"],
            "evaluationDigest": full_evaluation["evaluationDigest"],
            "noAccessWorkHours": full_evaluation["noAccessWorkHours"],
            "withAccessWorkHours": full_evaluation["withAccessWorkHours"],
            "workValueHours": full_evaluation["workValueHours"],
        },
        "providerActivity": {
            "externalProviderCalls": 0,
            "networkUsed": False,
        },
    }
    try:
        bounded_with = build_local_accounting_slice(
            **kwargs,
            evaluation_mode="with-access",
            max_included_nodes=max_included_nodes,
            max_boundary_nodes=max_boundary_nodes,
        )
        bounded_no = build_local_accounting_slice(
            **kwargs,
            evaluation_mode="no-access",
            max_included_nodes=max_included_nodes,
            max_boundary_nodes=max_boundary_nodes,
        )
    except MathFlowError as exc:
        return {
            **base_result,
            "classification": "requires-explicit-widening",
            "failureReason": str(exc),
            "truncated": False,
            "explicitWideSliceMeasurement": {
                "withAccessSlice": measure(wide_with),
                "noAccessSlice": measure(wide_no),
            },
            "equivalence": {
                "attempted": False,
                "reason": "bounded cut rejected before any local reduction",
            },
        }

    local_no, local_with, local_evaluation = (
        materialize_local_slice_submission_work_value(
            **kwargs,
            no_access_patch=no_patch,
            with_access_patch=with_patch,
            no_access_slice=bounded_no,
            with_access_slice=bounded_with,
        )
    )
    frozen_snapshot = build_frozen_with_access_local_snapshot(
        frozen_with_access_state=local_with,
        root_contract=fixture["contract"],
        target_knowledge_state=fixture["after"],
        impact_context=fixture["impact"],
        max_included_nodes=max_included_nodes,
        max_boundary_nodes=max_boundary_nodes,
    )
    exact = (
        local_no == full_no
        and local_with == full_with
        and local_evaluation == full_evaluation
    )
    if not exact:
        raise MathFlowError("local-slice probe diverged from the full-state oracle")
    return {
        **base_result,
        "classification": "bounded-exact-equivalence",
        "failureReason": None,
        "truncated": False,
        "localArtifacts": {
            "withAccessSlice": measure(bounded_with),
            "noAccessSlice": measure(bounded_no),
            "frozenWithAccessSnapshot": measure(frozen_snapshot),
            "withAccessSliceDigest": bounded_with["sliceDigest"],
            "noAccessSliceDigest": bounded_no["sliceDigest"],
            "frozenWithAccessSnapshotDigest": frozen_snapshot["snapshotDigest"],
        },
        "equivalence": {
            "attempted": True,
            "globalNoAccessStateExact": local_no == full_no,
            "globalWithAccessStateExact": local_with == full_with,
            "evaluationExact": local_evaluation == full_evaluation,
        },
    }


def run_local_slice_probe(
    configurations: Sequence[WorkAccountingScaleConfig] | None = None,
    *,
    scenarios: Sequence[str] = SCENARIOS,
    max_included_nodes: int = DEFAULT_MAX_INCLUDED_NODES,
    max_boundary_nodes: int = DEFAULT_MAX_BOUNDARY_NODES,
) -> dict[str, object]:
    selected = tuple(
        default_work_accounting_scale_configurations()
        if configurations is None
        else configurations
    )
    selected_scenarios = tuple(scenarios)
    if (
        not selected
        or not selected_scenarios
        or len(selected_scenarios) != len(set(selected_scenarios))
        or any(scenario not in SCENARIOS for scenario in selected_scenarios)
    ):
        raise MathFlowError("local-slice probe requires unique supported cases")
    cases = [
        build_local_slice_probe_case(
            configuration,
            scenario,
            max_included_nodes=max_included_nodes,
            max_boundary_nodes=max_boundary_nodes,
        )
        for configuration in selected
        for scenario in selected_scenarios
    ]
    successful = [
        case for case in cases if case["classification"] == "bounded-exact-equivalence"
    ]
    widened = [
        case for case in cases if case["classification"] == "requires-explicit-widening"
    ]
    byte_ratios: list[float] = []
    frozen_ratios: list[float] = []
    for case in successful:
        local = case["localArtifacts"]
        full = case["fullStateOracle"]
        byte_ratios.append(
            local["withAccessSlice"]["utf8Bytes"]
            / full["baseAccountingState"]["utf8Bytes"]
        )
        frozen_ratios.append(
            local["frozenWithAccessSnapshot"]["utf8Bytes"]
            / full["withAccessState"]["utf8Bytes"]
        )
    core: dict[str, object] = {
        "schemaVersion": 1,
        "probeId": PROBE_ID,
        "activationStatus": "inactive-provider-free-experiment",
        "providerCalls": 0,
        "networkUsed": False,
        "bounds": {
            "maxIncludedNodes": max_included_nodes,
            "maxBoundaryNodes": max_boundary_nodes,
            "policy": "fail-closed-never-truncate",
        },
        "tokenEstimate": {
            "method": TOKEN_ESTIMATE_METHOD,
            "classification": "size-proxy-not-model-tokenizer-measurement",
        },
        "summary": {
            "caseCount": len(cases),
            "boundedExactCaseCount": len(successful),
            "explicitWideningCaseCount": len(widened),
            "allAttemptedEquivalenceChecksExact": all(
                all(
                    value is True
                    for key, value in case["equivalence"].items()
                    if key != "attempted"
                )
                for case in successful
            ),
            "minimumWithAccessSliceToFullBaseByteRatio": (
                min(byte_ratios) if byte_ratios else None
            ),
            "maximumWithAccessSliceToFullBaseByteRatio": (
                max(byte_ratios) if byte_ratios else None
            ),
            "minimumFrozenSnapshotToFullWithAccessByteRatio": (
                min(frozen_ratios) if frozen_ratios else None
            ),
            "maximumFrozenSnapshotToFullWithAccessByteRatio": (
                max(frozen_ratios) if frozen_ratios else None
            ),
        },
        "limitations": [
            "This proves deterministic reducer equivalence, not model judgment quality.",
            "Token counts are compact-JSON byte proxies, not provider tokenizer counts.",
            "Dependency, root-wide, or topology-required cuts may exceed a bound and fail; they are never truncated.",
            "The experiment supports program-only knowledge state v3 and is not wired to a provider or active lane.",
        ],
        "cases": cases,
    }
    return {**core, "reportDigest": "sha256:" + sha256_json(core)}


def write_local_slice_probe_report(path: Path) -> dict[str, object]:
    report = run_local_slice_probe()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    return report
