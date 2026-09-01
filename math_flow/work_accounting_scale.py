"""Provider-free capacity and locality probes for Work Accounting V2.

The probe deliberately exercises the production request/context builders and
the governed OpenRouter adapter with a local capture transport.  It never calls
an external provider.  Token counts are labelled estimates derived from compact
UTF-8 byte lengths; they are not model-tokenizer measurements.
"""

from __future__ import annotations

import base64
import copy
import json
import math
from collections.abc import Mapping, Sequence
from dataclasses import asdict, dataclass
from decimal import Decimal
from pathlib import Path

from .builder_scale import SyntheticBuilderStateConfig, build_synthetic_builder_fixture
from .counterfactual_context import (
    assemble_with_access_evidence,
    build_counterfactual_safe_facts,
    build_impact_subgraph_context,
    build_no_access_stage_input_v2,
    build_submission_evidence_manifest,
    build_with_access_stage_input,
)
from .errors import MathFlowError
from .governed_providers import OpenRouterWorkProjectionProviderV2
from .repository import sha256_json
from .research_builder_v7 import apply_research_builder_v7_transition
from .work_accounting import (
    apply_work_accounting_patch,
    build_work_accounting_state,
    make_root_contract,
)
from .work_projection import (
    PROFILE_V2,
    SubmissionEvidenceFile,
    _bindings,
    _make_request,
    _patch_from_response,
    _required_primitive_updates,
    _safe_fact_stage_input,
)


SCENARIOS = (
    "dependency-closure",
    "topology-revision",
    "solving-zero-out",
    "broad-local-subtree",
)
DEFAULT_INPUT_BUDGET_TOKENS = 128_000
TOKEN_ESTIMATE_METHOD = "ceil(compact-json-utf8-bytes/4)"
TOKEN_UPPER_BOUND_METHOD = "compact-json-utf8-bytes (one token per byte)"
SUBJECT = "f" * 40
JUDGMENT = "sha256:" + "9" * 64
ASSESSMENT = "sha256:" + "8" * 64
PROJECTION = "sha256:" + "7" * 64


@dataclass(frozen=True)
class WorkAccountingScaleConfig:
    """Independent state-size and local-hot-branch dimensions."""

    program_count: int
    result_count: int
    maximum_depth: int
    hot_branch_width: int
    evidence_bytes: int = 4096
    descendant_depth: int = 2
    dependency_depth: int = 3
    dependency_width: int = 2

    def validate(self) -> WorkAccountingScaleConfig:
        values = asdict(self)
        if any(
            not isinstance(value, int) or isinstance(value, bool)
            for value in values.values()
        ):
            raise MathFlowError("work-accounting scale settings must be integers")
        if (
            self.program_count < 3
            or self.result_count < 1
            or self.maximum_depth < 1
            or self.hot_branch_width < 2
            or self.evidence_bytes < 64
            or not 0 <= self.descendant_depth <= 4
            or self.dependency_depth < 0
            or self.dependency_width < 1
        ):
            raise MathFlowError("work-accounting scale settings are out of range")
        required_results = self.dependency_depth * self.dependency_width + 1
        if self.result_count < required_results:
            raise MathFlowError(
                "work-accounting scale state has too few dependency results"
            )
        return self


def default_work_accounting_scale_configurations(
) -> tuple[WorkAccountingScaleConfig, ...]:
    """A widening matrix that crosses the probe's nominal 128k input budget."""

    return (
        WorkAccountingScaleConfig(16, 24, 3, 4),
        WorkAccountingScaleConfig(64, 64, 3, 8),
        WorkAccountingScaleConfig(256, 128, 3, 16),
        WorkAccountingScaleConfig(1024, 256, 3, 32),
    )


def _compact_json_bytes(value: object) -> bytes:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")


def measure_serialized_value(value: object) -> dict[str, object]:
    """Measure compact JSON with deliberately conservative token labels."""

    byte_count = len(_compact_json_bytes(value))
    return {
        "utf8Bytes": byte_count,
        "estimatedTokens": math.ceil(byte_count / 4),
        "estimatedTokenMethod": TOKEN_ESTIMATE_METHOD,
        "conservativeTokenUpperBound": byte_count,
        "conservativeUpperBoundMethod": TOKEN_UPPER_BOUND_METHOD,
    }


def _measure_exact_bytes(byte_count: int) -> dict[str, object]:
    return {
        "rawBytes": byte_count,
        "estimatedTokens": math.ceil(byte_count / 4),
        "estimatedTokenMethod": "ceil(raw-bytes/4); only a size proxy",
        "conservativeTokenUpperBound": byte_count,
        "conservativeUpperBoundMethod": "raw bytes (one token per byte)",
    }


def _measure_model_input_proxy(payload: Mapping[str, object]) -> dict[str, object]:
    """Measure model-visible variable input without HTTP JSON escaping.

    Provider tokenizer framing is unknown.  This proxy sums exact message
    content bytes and the compact structured-output response-format bytes.
    """

    messages = payload.get("messages")
    response_format = payload.get("response_format")
    if not isinstance(messages, list) or not isinstance(response_format, dict):
        raise MathFlowError("provider-free capture has an invalid chat payload")
    message_bytes = 0
    for message in messages:
        if (
            not isinstance(message, dict)
            or not isinstance(message.get("content"), str)
        ):
            raise MathFlowError("provider-free capture has an invalid chat message")
        message_bytes += len(str(message["content"]).encode("utf-8"))
    schema_bytes = len(_compact_json_bytes(response_format))
    total = message_bytes + schema_bytes
    return {
        "utf8Bytes": total,
        "messageContentBytes": message_bytes,
        "structuredOutputSchemaBytes": schema_bytes,
        "estimatedTokens": math.ceil(total / 4),
        "estimatedTokenMethod": (
            "ceil((message-content-utf8-bytes + compact-response-format-bytes)/4)"
        ),
        "conservativeTokenUpperBound": total,
        "conservativeUpperBoundMethod": (
            "message content plus response-format bytes (one token per byte)"
        ),
        "omittedUnknownOverhead": "provider tokenizer chat framing/control tokens",
    }


def _without_digest(value: Mapping[str, object]) -> dict[str, object]:
    return {
        key: copy.deepcopy(item)
        for key, item in value.items()
        if key != "digest"
    }


def _program_children(state: Mapping[str, object]) -> dict[str, list[str]]:
    programs = state["programs"]
    assert isinstance(programs, dict)
    result = {str(program_id): [] for program_id in programs}
    for program_id, record in programs.items():
        assert isinstance(record, dict)
        parent = record.get("parentId")
        if isinstance(parent, str):
            result[parent].append(str(program_id))
    for children in result.values():
        children.sort()
    return result


def _active_leaf(state: Mapping[str, object]) -> str:
    programs = state["programs"]
    assert isinstance(programs, dict)
    children = _program_children(state)
    candidates = [
        str(program_id)
        for program_id, record in programs.items()
        if program_id != "root"
        and isinstance(record, dict)
        and record.get("status") == "active"
        and not children[str(program_id)]
    ]
    if not candidates:
        raise MathFlowError("work-accounting solving probe needs an active leaf")
    return sorted(candidates)[-1]


def _broad_seed(state: Mapping[str, object]) -> str:
    programs = state["programs"]
    assert isinstance(programs, dict)
    children = _program_children(state)
    candidates = [
        (len(child_ids), program_id)
        for program_id, child_ids in children.items()
        if program_id != "root"
        and isinstance(programs[program_id], dict)
        and programs[program_id].get("status") == "active"
    ]
    width, program_id = max(candidates, key=lambda item: (item[0], item[1]))
    if width < 1:
        raise MathFlowError("work-accounting broad probe needs a non-root subtree")
    return program_id


def _dependency_scope(
    fixture: Mapping[str, object],
) -> tuple[list[str], list[str], str, str]:
    state = fixture["state"]
    challenges = fixture["challenges"]
    assert isinstance(state, dict) and isinstance(challenges, dict)
    challenge = challenges["dependency-closure"]
    assert isinstance(challenge, dict)
    result_ids = sorted(map(str, challenge["requiredResultIds"]))
    program_ids = sorted(map(str, challenge["requiredProgramIds"]))
    dependency_result_id = result_ids[-1]
    results = state["intermediateResults"]
    assert isinstance(results, dict)
    dependency_result = results[dependency_result_id]
    assert isinstance(dependency_result, dict)
    dependency_transaction_id = str(dependency_result["sourceTransactionIds"][0])
    target_program_id = str(dependency_result["primaryProgramId"])
    return program_ids, result_ids, dependency_result_id, dependency_transaction_id


def _result_value(
    *,
    primary_program_id: str,
    dependency_result_ids: Sequence[str],
    scenario: str,
) -> dict[str, object]:
    return {
        "id": "result/work-accounting-probe",
        "primaryProgramId": primary_program_id,
        "relatedProgramIds": [],
        "title": "Work-accounting scale probe result",
        "statement": f"The provider-free {scenario} probe outcome is represented.",
        "scopeQualifications": ["Synthetic provider-free capacity probe only."],
        "support": {
            "proofs": ["The deterministic fixture constructor supplies this result."],
            "methods": [],
            "computations": [],
            "tools": [],
            "artifactRefs": [],
            "attestationRefs": [],
        },
        "dependencyResultIds": sorted(set(dependency_result_ids)),
        "claimRefs": [{"transactionId": SUBJECT, "claimKey": "claim/current"}],
        "sourceTransactionIds": [SUBJECT],
        "judgmentIds": [JUDGMENT],
        "status": "active",
        "supersededByResultIds": [],
    }


def _add_result_to_program(
    state: Mapping[str, object], program_id: str
) -> dict[str, object]:
    programs = state["programs"]
    assert isinstance(programs, dict)
    record = programs[program_id]
    assert isinstance(record, dict)
    value = _without_digest(record)
    value["intermediateResultIds"] = sorted(
        {*map(str, value["intermediateResultIds"]), "result/work-accounting-probe"}
    )
    value["sourceTransactionIds"] = sorted(
        {*map(str, value["sourceTransactionIds"]), SUBJECT}
    )
    return value


def _build_transition(
    fixture: Mapping[str, object], scenario: str
) -> tuple[dict[str, object], list[str], list[str], str | None]:
    state = fixture["state"]
    assert isinstance(state, dict)
    programs = state["programs"]
    assert isinstance(programs, dict)
    dependency_result_ids: list[str] = []
    expected_dependency_closure: list[str] = []
    solving_program_id: str | None = None
    topology_operations: list[dict[str, object]] = []
    content_operations: list[dict[str, object]] = []

    if scenario == "dependency-closure":
        seed_ids, expected_dependency_closure, dependency_result_id, _ = (
            _dependency_scope(fixture)
        )
        direct_program_id = str(
            state["intermediateResults"][dependency_result_id]["primaryProgramId"]
        )
        dependency_result_ids = [dependency_result_id]
        direct_value = _add_result_to_program(state, direct_program_id)
        content_operations.append(
            {
                "entityKind": "program",
                "entityId": direct_program_id,
                "baseDigest": programs[direct_program_id]["digest"],
                "value": direct_value,
            }
        )
        placement = {
            "basis": "local-objective",
            "rationale": "The dependency-bearing result advances this local package.",
            "relatedProgramIds": [direct_program_id],
        }
    elif scenario == "broad-local-subtree":
        direct_program_id = _broad_seed(state)
        seed_ids = [direct_program_id]
        direct_value = _add_result_to_program(state, direct_program_id)
        content_operations.append(
            {
                "entityKind": "program",
                "entityId": direct_program_id,
                "baseDigest": programs[direct_program_id]["digest"],
                "value": direct_value,
            }
        )
        placement = {
            "basis": "local-objective",
            "rationale": "The result advances the selected broad local subtree.",
            "relatedProgramIds": [direct_program_id],
        }
    elif scenario == "solving-zero-out":
        direct_program_id = "root"
        solving_program_id = _active_leaf(state)
        # Root is included deterministically as an ancestor.  Seeding it would
        # expand every root descendant to ``descendant_depth`` and turn this
        # intentionally local completion case into an accidental global read.
        seed_ids = [solving_program_id]
        solved = _without_digest(programs[solving_program_id])
        solved["status"] = "completed"
        solved["currentStateSummary"] = "The local package is complete in the realized world."
        solved["localResidualSummary"] = "No local residual work remains."
        solved["sourceTransactionIds"] = sorted(
            {*map(str, solved["sourceTransactionIds"]), SUBJECT}
        )
        content_operations.extend(
            [
                {
                    "entityKind": "program",
                    "entityId": solving_program_id,
                    "baseDigest": programs[solving_program_id]["digest"],
                    "value": solved,
                },
                {
                    "entityKind": "program",
                    "entityId": "root",
                    "baseDigest": programs["root"]["digest"],
                    "value": _add_result_to_program(state, "root"),
                },
            ]
        )
        placement = {
            "basis": "canonical-objective",
            "rationale": "The accepted result records the realized completion event.",
            "relatedProgramIds": [],
        }
    elif scenario == "topology-revision":
        direct_program_id = "root"
        children = _program_children(state)["root"]
        if len(children) < 2:
            raise MathFlowError("topology revision probe needs two root children")
        new_parent_id, moved_program_id = children[:2]
        moved = _without_digest(programs[moved_program_id])
        moved["parentId"] = new_parent_id
        topology_operations.append(
            {
                "action": "move",
                "entityKind": "program",
                "entityId": moved_program_id,
                "baseDigest": programs[moved_program_id]["digest"],
                "value": moved,
            }
        )
        # The revised node pulls in its ancestors (including root) and its new
        # decision-point siblings without expanding every root child.
        seed_ids = [moved_program_id]
        content_operations.append(
            {
                "entityKind": "program",
                "entityId": "root",
                "baseDigest": programs["root"]["digest"],
                "value": _add_result_to_program(state, "root"),
            }
        )
        placement = {
            "basis": "canonical-objective",
            "rationale": "The canonical contribution accompanies a topology revision.",
            "relatedProgramIds": [],
        }
    else:
        raise MathFlowError(f"unsupported work-accounting scale scenario: {scenario}")

    content_operations.append(
        {
            "entityKind": "intermediateResult",
            "entityId": "result/work-accounting-probe",
            "baseDigest": None,
            "value": _result_value(
                primary_program_id=direct_program_id,
                dependency_result_ids=dependency_result_ids,
                scenario=scenario,
            ),
        }
    )
    transition = {
        "schemaVersion": 1,
        "subjectTransactionId": SUBJECT,
        "baseStateDigest": state["stateDigest"],
        "contentOperations": content_operations,
        "topologyOperations": topology_operations,
        "contribution": {
            "claimKeys": ["claim/current"],
            "directProgramIds": [direct_program_id],
            "intermediateResultIds": ["result/work-accounting-probe"],
        },
        "placementAudit": placement,
        "topologyRationale": (
            "Move one active work package under its revised accounting parent."
            if topology_operations
            else None
        ),
    }
    return transition, seed_ids, expected_dependency_closure, solving_program_id


def _root_contract() -> dict[str, object]:
    return make_root_contract(
        problem_id="synthetic-builder-scale",
        knowledge_projection_id="provider-free-work-accounting-scale-v1",
        knowledge_projection_spec_digest=PROJECTION,
        objective="Resolve the synthetic benchmark objective.",
        terminal_condition="The synthetic canonical objective is complete.",
        tool_baseline="Ordinary references and standard research tools as of 2026-08-31.",
        reference_community_description="Qualified researchers organized by Math Flow.",
        researcher_qualification="A competent human researcher qualified for the local package.",
    )


def _base_accounting_state(
    state: Mapping[str, object], contract: Mapping[str, object]
) -> dict[str, object]:
    programs = state["programs"]
    contributions = state["contributions"]
    assert isinstance(programs, dict) and isinstance(contributions, dict)
    annotations: list[dict[str, object]] = []
    for index, (program_id, record) in enumerate(sorted(programs.items())):
        assert isinstance(record, dict)
        inactive = record.get("status") in {"completed", "retired"}
        annotations.append(
            {
                "nodeRef": {"kind": "program", "id": str(program_id)},
                "directWorkHours": (
                    "0"
                    if inactive
                    else "40"
                    if program_id == "root"
                    else str(8 + (index % 17))
                ),
                "conditionalIncidence": (
                    None
                    if program_id == "root"
                    else "0"
                    if inactive
                    else "0.5"
                ),
            }
        )
    return build_work_accounting_state(
        root_contract=contract,
        knowledge_state=state,
        annotations=annotations,
        # The fixture dict is populated in submission order; preserve that live
        # accounting sequence instead of imposing an unrelated lexical order.
        processed_submission_ids=list(map(str, contributions)),
    )


def _annotation_map(state: Mapping[str, object]) -> dict[str, dict[str, object]]:
    return {
        str(item["nodeRef"]["id"]): item
        for item in state["annotations"]
        if isinstance(item, dict) and isinstance(item.get("nodeRef"), dict)
    }


def _patch_updates(
    *,
    mode: str,
    scenario: str,
    seed_ids: Sequence[str],
    before: Mapping[str, object],
    after: Mapping[str, object],
    base: Mapping[str, object],
    required: Sequence[Mapping[str, object]],
    solving_program_id: str | None,
    evidence_ref: str,
) -> list[dict[str, object]]:
    del before
    base_annotations = _annotation_map(base)
    required_by_id = {
        str(item["nodeRef"]["id"]): set(map(str, item["requiredChanges"]))
        for item in required
    }
    update_ids = set(required_by_id)
    if scenario in {"dependency-closure", "broad-local-subtree"}:
        update_ids.add(str(seed_ids[0]))
    else:
        update_ids.add("root")
    if solving_program_id is not None and mode == "with-access":
        update_ids.add(solving_program_id)

    programs = after["programs"]
    assert isinstance(programs, dict)
    updates: list[dict[str, object]] = []
    for program_id in sorted(update_ids):
        changes: dict[str, object] = {}
        required_changes = required_by_id.get(program_id, set())
        base_annotation = base_annotations.get(program_id)
        status = programs[program_id]["status"]
        if status in {"completed", "retired"} and mode == "with-access":
            if program_id != "root":
                changes["conditionalIncidence"] = "0"
            changes["directWorkHours"] = "0"
        else:
            if "conditionalIncidence" in required_changes:
                changes["conditionalIncidence"] = "0.4" if mode == "with-access" else "0.6"
            if "directWorkHours" in required_changes:
                changes["directWorkHours"] = "6" if mode == "with-access" else "12"

        if not changes:
            if base_annotation is None:
                changes = {
                    "directWorkHours": "6" if mode == "with-access" else "12",
                    "conditionalIncidence": "0.4" if mode == "with-access" else "0.6",
                }
            else:
                old = int(str(base_annotation["directWorkHours"]))
                changes["directWorkHours"] = str(
                    max(1, old - 4) if mode == "with-access" else old + 4
                )
        updates.append(
            {
                "nodeRef": {"kind": "program", "id": program_id},
                "changes": changes,
                "rationale": f"Synthetic {mode} primitive estimate for {program_id}.",
                "evidenceRefs": [evidence_ref],
            }
        )
    return updates


class _CaptureTransport:
    """Local transport double; an invocation is not an external provider call."""

    def __init__(self, response: Mapping[str, object]) -> None:
        self.response = copy.deepcopy(dict(response))
        self.payloads: list[dict[str, object]] = []

    def __call__(self, payload: dict[str, object]) -> dict[str, object]:
        self.payloads.append(copy.deepcopy(payload))
        return {
            "id": "provider-free-capture",
            "model": "provider-free/capture",
            "choices": [
                {
                    "finish_reason": "stop",
                    "message": {
                        "content": json.dumps(
                            self.response,
                            sort_keys=True,
                            separators=(",", ":"),
                        )
                    },
                }
            ],
        }


def _capture_actual_transport_payload(
    *,
    spec: Mapping[str, object],
    stage: str,
    request: Mapping[str, object],
    evidence_files: Sequence[SubmissionEvidenceFile],
    response: Mapping[str, object],
) -> dict[str, object]:
    capture = _CaptureTransport(response)
    adapter = OpenRouterWorkProjectionProviderV2(spec, transport=capture)
    adapter(
        stage=stage,
        request=request,
        evidence_files=evidence_files,
    )
    if len(capture.payloads) != 1:
        raise MathFlowError("provider-free capture did not make exactly one local call")
    return capture.payloads[0]


def _component_metrics(
    *,
    request: Mapping[str, object],
    payload: Mapping[str, object],
    raw_evidence_bytes: int,
) -> dict[str, object]:
    stage_input = request["stageInput"]
    assert isinstance(stage_input, dict)
    result: dict[str, object] = {
        "governedRequest": measure_serialized_value(request),
        "baseAccountingState": measure_serialized_value(
            request["baseAccountingState"]
        ),
        "stageInput": measure_serialized_value(stage_input),
        "rootContract": measure_serialized_value(request["rootContract"]),
        "requiredPrimitiveUpdates": measure_serialized_value(
            request["requiredPrimitiveUpdates"]
        ),
        "modelInputProxy": _measure_model_input_proxy(payload),
        "actualTransportEnvelope": measure_serialized_value(payload),
        "rawSubmissionEvidence": _measure_exact_bytes(raw_evidence_bytes),
    }
    impact = stage_input.get("impactContext")
    if isinstance(impact, dict):
        result["impactContext"] = measure_serialized_value(impact)
    frozen = stage_input.get("frozenWithAccessState")
    if isinstance(frozen, dict):
        result["frozenWithAccessState"] = measure_serialized_value(frozen)
    manifest = stage_input.get("evidenceManifest")
    if isinstance(manifest, dict):
        result["evidenceManifest"] = measure_serialized_value(manifest)
    return result


def _budget_classification(
    stage_reports: Mapping[str, Mapping[str, object]], input_budget_tokens: int
) -> dict[str, object]:
    model_proxy_crossings: list[str] = []
    transport_crossings: list[str] = []
    upper_bound_crossings: list[str] = []
    maximum_stage = ""
    maximum_estimate = -1
    maximum_transport_estimate = -1
    for stage, report in stage_reports.items():
        model_proxy = report["components"]["modelInputProxy"]
        transport = report["components"]["actualTransportEnvelope"]
        estimate = int(model_proxy["estimatedTokens"])
        transport_estimate = int(transport["estimatedTokens"])
        upper = int(model_proxy["conservativeTokenUpperBound"])
        if estimate > input_budget_tokens:
            model_proxy_crossings.append(stage)
        if transport_estimate > input_budget_tokens:
            transport_crossings.append(stage)
        if upper > input_budget_tokens:
            upper_bound_crossings.append(stage)
        if estimate > maximum_estimate:
            maximum_estimate = estimate
            maximum_stage = stage
        maximum_transport_estimate = max(
            maximum_transport_estimate, transport_estimate
        )
    return {
        "inputBudgetTokens": input_budget_tokens,
        "inputBudgetMeaning": (
            "probe threshold applied to the model-input proxy; not an observed "
            "provider tokenizer count or configured model context window"
        ),
        "capacityClass": (
            "hard-input-exhaustion-estimated"
            if model_proxy_crossings
            else "within-estimated-input-budget"
        ),
        "estimatedInputBudgetCrossedUnderModelInputProxy": bool(
            model_proxy_crossings
        ),
        "stagesCrossingModelInputProxyBudget": model_proxy_crossings,
        "stagesCrossingSerializedTransportBudget": transport_crossings,
        "stagesWhoseModelInputProxyUpperBoundCrossesBudget": (
            upper_bound_crossings
        ),
        "maximumStage": maximum_stage,
        "maximumStageEstimatedModelInputTokens": maximum_estimate,
        "maximumStageSerializedTransportEstimatedTokens": (
            maximum_transport_estimate
        ),
        "hardOutputCapacity": "not-observable-in-provider-free-input-probe",
    }


def _annotation(state: Mapping[str, object], program_id: str) -> Mapping[str, object]:
    for item in state["annotations"]:
        if item["nodeRef"] == {"kind": "program", "id": program_id}:
            return item
    raise MathFlowError(f"missing work-accounting annotation: {program_id}")


def build_work_accounting_scale_case(
    configuration: WorkAccountingScaleConfig,
    scenario: str,
    *,
    input_budget_tokens: int = DEFAULT_INPUT_BUDGET_TOKENS,
    spec: Mapping[str, object] | None = None,
) -> dict[str, object]:
    """Build and measure one zero-network, reducer-valid V2 scale case."""

    config = configuration.validate()
    if scenario not in SCENARIOS:
        raise MathFlowError(f"unsupported work-accounting scale scenario: {scenario}")
    if (
        not isinstance(input_budget_tokens, int)
        or isinstance(input_budget_tokens, bool)
        or input_budget_tokens < 1
    ):
        raise MathFlowError("work-accounting scale input budget must be positive")
    if spec is None:
        spec_path = (
            Path(__file__).resolve().parents[1]
            / "protocol/judges/openrouter-work-accounting-v2.json"
        )
        spec = json.loads(spec_path.read_text(encoding="utf-8"))

    builder_fixture = build_synthetic_builder_fixture(
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
    before = builder_fixture["state"]
    assert isinstance(before, dict)
    transition, seed_ids, expected_dependencies, solving_program_id = _build_transition(
        builder_fixture, scenario
    )
    dependency_txs = (
        [
            _dependency_scope(builder_fixture)[3]
        ]
        if scenario == "dependency-closure"
        else []
    )
    reduced = apply_research_builder_v7_transition(
        before,
        transition,
        accepted_claims=[
            {
                "claimKey": "claim/current",
                "statement": "The synthetic provider-free probe claim is accepted.",
                "dependencyTransactionIds": dependency_txs,
            }
        ],
        judgment_id=JUDGMENT,
    )
    after = reduced["postState"]
    alignment = reduced["topologyAlignment"]
    assert isinstance(after, dict) and isinstance(alignment, dict)
    contract = _root_contract()
    base = _base_accounting_state(before, contract)

    contribution_path = "problems/synthetic-builder-scale/contributions/provider-free-probe"
    evidence_prefix = (
        "Synthetic untrusted benchmark evidence for request capacity measurement.\n"
    ).encode("utf-8")
    padding = b"e" * max(0, config.evidence_bytes - len(evidence_prefix))
    evidence = evidence_prefix + padding
    manifest, chunks = build_submission_evidence_manifest(
        problem_id="synthetic-builder-scale",
        subject_transaction_id=SUBJECT,
        contribution_path=contribution_path,
        files={f"{contribution_path}/README.md": evidence},
    )
    accepted_claim_refs = [
        {
            "transactionId": SUBJECT,
            "claimKey": "claim/current",
            "judgmentId": JUDGMENT,
            "assessmentDigest": ASSESSMENT,
        }
    ]
    safe_response = {
        "facts": [
            {
                "id": f"probe/{scenario}",
                "condition": (
                    "A scenario-relevant mathematical outcome exists in the realized world."
                ),
                "actorVisibility": "withheld-until-independent-discovery",
                "affectedNodeRefs": [
                    {"kind": "program", "id": program_id}
                    for program_id in sorted(set(seed_ids))
                ],
                "acceptedClaimKeys": ["claim/current"],
            }
        ],
        "assumptions": [
            "The fixed reference community follows the frozen root contract."
        ],
    }
    safe_facts = build_counterfactual_safe_facts(
        problem_id="synthetic-builder-scale",
        subject_transaction_id=SUBJECT,
        accepted_claim_refs=accepted_claim_refs,
        research_state=after,
        evidence_manifest=manifest,
        evidence_chunks=chunks,
        extracted=safe_response,
    )
    impact = build_impact_subgraph_context(
        problem_id="synthetic-builder-scale",
        subject_transaction_id=SUBJECT,
        accepted_claim_refs=accepted_claim_refs,
        research_state=after,
        seed_node_refs=safe_response["facts"][0]["affectedNodeRefs"],
        descendant_depth=config.descendant_depth,
    )
    bindings = _bindings(
        contract=contract,
        base=base,
        before=before,
        after=after,
        alignment=alignment,
        manifest=manifest,
        accepted_claim_refs=accepted_claim_refs,
    )
    with_required = _required_primitive_updates(
        before, after, base, evaluation_mode="with-access"
    )
    no_required = _required_primitive_updates(
        before, after, base, evaluation_mode="no-access"
    )
    with_updates = _patch_updates(
        mode="with-access",
        scenario=scenario,
        seed_ids=seed_ids,
        before=before,
        after=after,
        base=base,
        required=with_required,
        solving_program_id=solving_program_id,
        evidence_ref=str(manifest["manifestDigest"]),
    )
    with_patch = _patch_from_response(
        {"updates": with_updates},
        mode="with-access",
        problem_id="synthetic-builder-scale",
        subject_transaction_id=SUBJECT,
        bindings=bindings,
        base_accounting_state=base,
        required_updates=with_required,
        impact_context=impact,
    )
    with_state = apply_work_accounting_patch(
        base,
        with_patch,
        root_contract=contract,
        base_knowledge_state=before,
        target_knowledge_state=after,
        topology_alignment=alignment,
    )
    no_updates = _patch_updates(
        mode="no-access",
        scenario=scenario,
        seed_ids=seed_ids,
        before=before,
        after=after,
        base=base,
        required=no_required,
        solving_program_id=solving_program_id,
        evidence_ref=f"safe-fact:probe/{scenario}",
    )
    no_patch = _patch_from_response(
        {"updates": no_updates},
        mode="no-access",
        problem_id="synthetic-builder-scale",
        subject_transaction_id=SUBJECT,
        bindings=bindings,
        base_accounting_state=base,
        required_updates=no_required,
        impact_context=impact,
    )
    no_state = apply_work_accounting_patch(
        base,
        no_patch,
        root_contract=contract,
        base_knowledge_state=before,
        target_knowledge_state=after,
        topology_alignment=alignment,
    )

    safe_input = _safe_fact_stage_input(
        accepted_claim_refs=accepted_claim_refs,
        target_knowledge_state=after,
        evidence_manifest=manifest,
    )
    with_input = build_with_access_stage_input(
        safe_facts=safe_facts,
        impact_context=impact,
        research_state=after,
        evidence_manifest=manifest,
        evidence_chunks=chunks,
    )
    candidate_core = {
        "safeFactsDigest": safe_facts["safeFactsDigest"],
        "withAccessStateDigest": with_state["stateDigest"],
    }
    candidate_digest = "sha256:" + sha256_json(candidate_core)
    no_input = build_no_access_stage_input_v2(
        safe_facts=safe_facts,
        impact_context=impact,
        research_state=after,
        frozen_with_access_state=with_state,
        frozen_with_access_candidate_digest=candidate_digest,
    )
    stage_inputs = {
        "safe-facts": (safe_input, [], safe_response),
        "with-access": (with_input, with_required, {"updates": with_updates}),
        "no-access": (no_input, no_required, {"updates": no_updates}),
    }
    assembled = assemble_with_access_evidence(with_input, chunks)
    evidence_files = tuple(
        SubmissionEvidenceFile(
            path=str(item["path"]),
            digest=str(item["digest"]),
            content=bytes(item["content"]),
        )
        for item in assembled
    )
    stage_reports: dict[str, dict[str, object]] = {}
    captured_payloads: dict[str, dict[str, object]] = {}
    for stage, (stage_input, required, response) in stage_inputs.items():
        request = _make_request(
            stage=stage,
            problem_id="synthetic-builder-scale",
            subject_transaction_id=SUBJECT,
            bindings=bindings,
            root_contract=contract,
            base_accounting_state=base,
            topology_alignment=alignment,
            required_updates=required,
            stage_input=stage_input,
            profile=PROFILE_V2,
        )
        supplied_evidence = evidence_files if stage != "no-access" else ()
        payload = _capture_actual_transport_payload(
            spec=spec,
            stage=stage,
            request=request,
            evidence_files=supplied_evidence,
            response=response,
        )
        captured_payloads[stage] = payload
        stage_parameters = spec["stages"][stage]["parameters"]
        max_output_tokens = int(stage_parameters["max_tokens"])
        components = _component_metrics(
            request=request,
            payload=payload,
            raw_evidence_bytes=(len(evidence) if supplied_evidence else 0),
        )
        estimated_input = int(components["modelInputProxy"]["estimatedTokens"])
        stage_reports[stage] = {
            "requestDigest": request["requestDigest"],
            "configuredMaxOutputTokens": max_output_tokens,
            "estimatedInputPlusConfiguredMaxOutputTokens": (
                estimated_input + max_output_tokens
            ),
            "components": components,
        }

    rendered_no_payload = _compact_json_bytes(captured_payloads["no-access"])
    semantic_result_ids = {
        str(item["intermediateResultId"])
        for item in impact["semanticIntermediateResultRefs"]
    }
    included_program_ids = {
        str(item["ref"]["id"]) for item in impact["includedNodes"]
    }
    required_context_ids = {
        str(item["nodeRef"]["id"])
        for item in [*with_required, *no_required]
    }
    semantic_checks: dict[str, bool] = {
        "requiredPrimitiveUpdatesCoveredByImpactContext": (
            required_context_ids <= included_program_ids
        ),
        "strictlyPositiveSyntheticReduction": (
            Decimal(str(no_state["totalWorkHours"]))
            > Decimal(str(with_state["totalWorkHours"]))
        ),
        "noAccessOmitsRawEvidenceAndManifest": (
            b"contentBase64" not in rendered_no_payload
            and b"evidenceManifest" not in rendered_no_payload
            and base64.b64encode(evidence) not in rendered_no_payload
        ),
        "safeFactsAndWithAccessReceiveExactEvidence": (
            base64.b64encode(evidence)
            in _compact_json_bytes(captured_payloads["safe-facts"])
            and base64.b64encode(evidence)
            in _compact_json_bytes(captured_payloads["with-access"])
        ),
        "localCaptureOnlyNoExternalProviderCalls": True,
    }
    if scenario == "dependency-closure":
        # Production impact-context construction does not traverse result
        # dependencies.  This case deliberately pre-expands dependency-owner
        # programs before safe-fact seeding and verifies that the actual V2
        # context retains every required identity without truncation.
        semantic_checks["preexpandedDependencyScopeRetained"] = set(
            expected_dependencies
        ) <= semantic_result_ids
    if scenario == "topology-revision":
        semantic_checks["topologyMoveAlignedAndReanchored"] = (
            bool(alignment["moved"])
            and any("conditionalIncidence" in item["requiredChanges"] for item in with_required)
            and any("conditionalIncidence" in item["requiredChanges"] for item in no_required)
        )
    if scenario == "solving-zero-out":
        assert solving_program_id is not None
        with_annotation = _annotation(with_state, solving_program_id)
        no_annotation = _annotation(no_state, solving_program_id)
        semantic_checks["withAccessCompletedNodeZeroed"] = (
            with_annotation["directWorkHours"] == "0"
            and with_annotation["conditionalIncidence"] == "0"
        )
        semantic_checks["noAccessCompletedNodeMayRetainWork"] = (
            no_annotation["directWorkHours"] != "0"
            and no_annotation["conditionalIncidence"] != "0"
        )
    if scenario == "broad-local-subtree":
        children = _program_children(after)[seed_ids[0]]
        semantic_checks["hotBranchIncludedAtConfiguredDepth"] = (
            set(children) <= included_program_ids
        )

    failed_checks = sorted(
        name for name, passed in semantic_checks.items() if not passed
    )
    result = {
        "schemaVersion": 1,
        "scenario": scenario,
        "configuration": asdict(config),
        "fixtureBindings": {
            "beforeKnowledgeStateDigest": before["stateDigest"],
            "afterKnowledgeStateDigest": after["stateDigest"],
            "topologyAlignmentDigest": alignment["alignmentDigest"],
            "baseAccountingStateDigest": base["stateDigest"],
            "withAccessStateDigest": with_state["stateDigest"],
            "noAccessStateDigest": no_state["stateDigest"],
        },
        "stateShape": {
            "programCount": len(before["programs"]),
            "resultCount": len(before["intermediateResults"]),
            "processedSubmissionCount": len(base["processedSubmissionIds"]),
            "seedProgramCount": len(set(seed_ids)),
            "impactIncludedProgramCount": len(impact["includedNodes"]),
            "impactBoundarySummaryCount": len(impact["boundarySummaries"]),
            "impactSemanticResultRefCount": len(
                impact["semanticIntermediateResultRefs"]
            ),
            "withAccessRequiredUpdateCount": len(with_required),
            "noAccessRequiredUpdateCount": len(no_required),
            "dependencySeedPolicy": (
                "preexpanded-result-owner-programs"
                if scenario == "dependency-closure"
                else None
            ),
        },
        "serializedStates": {
            "knowledgeStateBefore": measure_serialized_value(before),
            "knowledgeStateAfter": measure_serialized_value(after),
            "baseAccountingState": measure_serialized_value(base),
            "withAccessState": measure_serialized_value(with_state),
            "noAccessState": measure_serialized_value(no_state),
            "topologyAlignment": measure_serialized_value(alignment),
        },
        "stages": stage_reports,
        "capacityClassification": _budget_classification(
            stage_reports, input_budget_tokens
        ),
        "semanticAdversarialClassification": {
            "passed": not failed_checks,
            "checks": semantic_checks,
            "failedChecks": failed_checks,
            "classificationNote": (
                "Reducer/adversarial invariant results are reported independently "
                "from serialized input-budget crossings."
            ),
        },
        "providerActivity": {
            "externalProviderCalls": 0,
            "localCaptureTransportInvocations": 3,
            "networkUsed": False,
        },
    }
    return result


def run_provider_free_work_accounting_scale_probe(
    configurations: Sequence[WorkAccountingScaleConfig] | None = None,
    *,
    scenarios: Sequence[str] = SCENARIOS,
    input_budget_tokens: int = DEFAULT_INPUT_BUDGET_TOKENS,
    spec: Mapping[str, object] | None = None,
) -> dict[str, object]:
    """Run the complete widening matrix without any external model invocation."""

    selected = tuple(
        default_work_accounting_scale_configurations()
        if configurations is None
        else configurations
    )
    selected_scenarios = tuple(scenarios)
    if not selected or not selected_scenarios:
        raise MathFlowError("work-accounting scale probe needs cases and scenarios")
    if len(selected_scenarios) != len(set(selected_scenarios)) or any(
        scenario not in SCENARIOS for scenario in selected_scenarios
    ):
        raise MathFlowError("work-accounting scale scenarios must be unique and supported")
    selected_spec: Mapping[str, object]
    if spec is None:
        spec_path = (
            Path(__file__).resolve().parents[1]
            / "protocol/judges/openrouter-work-accounting-v2.json"
        )
        selected_spec = json.loads(spec_path.read_text(encoding="utf-8"))
    else:
        selected_spec = spec
    cases = [
        build_work_accounting_scale_case(
            configuration,
            scenario,
            input_budget_tokens=input_budget_tokens,
            spec=selected_spec,
        )
        for configuration in selected
        for scenario in selected_scenarios
    ]
    semantic_failures = [
        {
            "configuration": case["configuration"],
            "scenario": case["scenario"],
            "failedChecks": case["semanticAdversarialClassification"]["failedChecks"],
        }
        for case in cases
        if not case["semanticAdversarialClassification"]["passed"]
    ]
    budget_crossings = [
        {
            "configuration": case["configuration"],
            "scenario": case["scenario"],
            "stages": case["capacityClassification"][
                "stagesCrossingModelInputProxyBudget"
            ],
        }
        for case in cases
        if case["capacityClassification"][
            "estimatedInputBudgetCrossedUnderModelInputProxy"
        ]
    ]
    core: dict[str, object] = {
        "schemaVersion": 1,
        "probeId": "provider-free-work-accounting-context-scale-v1",
        "providerCalls": 0,
        "networkUsed": False,
        "judgeSpec": {
            "id": selected_spec.get("id"),
            "digest": "sha256:" + sha256_json(selected_spec),
        },
        "inputBudgetTokens": input_budget_tokens,
        "tokenEstimate": {
            "primary": (
                "ceil((message-content-utf8-bytes + "
                "compact-response-format-bytes)/4)"
            ),
            "serializedComponents": TOKEN_ESTIMATE_METHOD,
            "conservativeUpperBound": TOKEN_UPPER_BOUND_METHOD,
            "warning": (
                "These are model-input and serialized-size proxies, not tokenizer "
                "counts or observed provider usage."
            ),
        },
        "configuredOutputLimits": {
            stage: int(selected_spec["stages"][stage]["parameters"]["max_tokens"])
            for stage in ("safe-facts", "with-access", "no-access")
        },
        "caseCount": len(cases),
        "cases": cases,
        "summary": {
            "allSemanticAdversarialChecksPass": not semantic_failures,
            "semanticFailureCount": len(semantic_failures),
            "semanticFailures": semantic_failures,
            "estimatedInputCrossingCaseCount": len(budget_crossings),
            "estimatedInputCrossings": budget_crossings,
        },
    }
    return {**core, "reportDigest": "sha256:" + sha256_json(core)}


__all__ = [
    "DEFAULT_INPUT_BUDGET_TOKENS",
    "SCENARIOS",
    "WorkAccountingScaleConfig",
    "build_work_accounting_scale_case",
    "default_work_accounting_scale_configurations",
    "measure_serialized_value",
    "run_provider_free_work_accounting_scale_probe",
]
