"""Publication-forbidden route/refine widening experiment for local Builder V10.

This module deliberately stops before Builder V10 authoring.  It can build a
provider-free plan or exercise the governed route and route-refine adapter with
an explicitly supplied transport.  It has no projection, reducer, publication,
or workflow integration surface.
"""

from __future__ import annotations

import copy
import hashlib
import json
import math
from collections.abc import Callable, Mapping, Sequence
from dataclasses import asdict, dataclass
from decimal import Decimal, InvalidOperation
from pathlib import Path

from .artifacts import sha256_bytes
from .builder_scale import (
    ADVERSARIAL_CHALLENGES,
    SyntheticBuilderStateConfig,
    build_synthetic_builder_fixture,
    measure_serialized_value,
)
from .errors import MathFlowError
from .research_builder_v10 import (
    bind_research_builder_v10_route_plan,
    build_research_builder_v10_authoring_packet,
    build_research_builder_v10_catalog,
    build_research_builder_v10_route_context,
)
from .research_builder_v10_provider import (
    OpenRouterResearchBuilderV10Provider,
    _route_plan_schema_v10,
)
from .research_builder_v7 import (
    _normalize_contribution,
    _normalize_program,
    _normalize_result,
    _with_state_digest,
    validate_research_program_state_v3,
)


MANIFEST_FIELDS = {
    "schemaVersion",
    "id",
    "description",
    "status",
    "publicationForbidden",
    "providerExecutionDefault",
    "judgeSpec",
    "judgeSpecDigest",
    "model",
    "reasoningEffort",
    "seed",
    "maximumAttemptsPerStage",
    "maximumProgramsInAuthorPacket",
    "maximumResultsInAuthorPacket",
    "stopOnFirstHardFailure",
    "authorizationEnvironmentVariable",
    "authorizationValue",
    "budgets",
    "cases",
}
BUDGET_FIELDS = {
    "maximumProviderCalls",
    "maximumRequestBytes",
    "maximumEstimatedPromptTokens",
    "maximumConservativePromptTokens",
    "promptTokenOverheadReservation",
    "maximumCompletionTokensPerCall",
    "maximumTotalReservedTokens",
    "maximumTotalReportedTokens",
    "maximumSingleCallCostUsd",
    "maximumTotalCostUsd",
}
CASE_FIELDS = {
    "id",
    "phase",
    "challenge",
    "clueMode",
    "historySteps",
    "configuration",
}
CONFIGURATION_FIELDS = {
    "programCount",
    "resultCount",
    "maximumDepth",
    "maximumWidth",
    "provenancePerResult",
    "dependencyDepth",
    "dependencyWidth",
    "supportBytes",
    "summaryBytes",
    "evidenceBytes",
}
PHASES = {"widening", "adversarial", "sequential-growth", "limitation"}
CLUE_MODES = {"validity-summary", "evidence-only"}


def _compact_bytes(value: object) -> bytes:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")


def _digest(value: object) -> str:
    return sha256_bytes(_compact_bytes(value))


def _require_exact_fields(
    value: object, expected: set[str], label: str
) -> dict[str, object]:
    if not isinstance(value, dict) or set(value) != expected:
        raise MathFlowError(f"{label} has invalid fields")
    return value


def _positive_integer(value: object, label: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 1:
        raise MathFlowError(f"{label} must be a positive integer")
    return value


def _nonnegative_decimal(value: object, label: str) -> Decimal:
    if isinstance(value, bool):
        raise MathFlowError(f"{label} must be a nonnegative decimal")
    try:
        result = Decimal(str(value))
    except (InvalidOperation, ValueError) as exc:
        raise MathFlowError(f"{label} must be a nonnegative decimal") from exc
    if not result.is_finite() or result < 0:
        raise MathFlowError(f"{label} must be a nonnegative decimal")
    return result


@dataclass(frozen=True)
class WideningBudgets:
    maximum_provider_calls: int
    maximum_request_bytes: int
    maximum_estimated_prompt_tokens: int
    maximum_conservative_prompt_tokens: int
    prompt_token_overhead_reservation: int
    maximum_completion_tokens_per_call: int
    maximum_total_reserved_tokens: int
    maximum_total_reported_tokens: int
    maximum_single_call_cost_usd: Decimal
    maximum_total_cost_usd: Decimal

    @classmethod
    def from_mapping(cls, value: object) -> "WideningBudgets":
        raw = _require_exact_fields(value, BUDGET_FIELDS, "widening budgets")
        budgets = cls(
            maximum_provider_calls=_positive_integer(
                raw["maximumProviderCalls"], "maximumProviderCalls"
            ),
            maximum_request_bytes=_positive_integer(
                raw["maximumRequestBytes"], "maximumRequestBytes"
            ),
            maximum_estimated_prompt_tokens=_positive_integer(
                raw["maximumEstimatedPromptTokens"],
                "maximumEstimatedPromptTokens",
            ),
            maximum_conservative_prompt_tokens=_positive_integer(
                raw["maximumConservativePromptTokens"],
                "maximumConservativePromptTokens",
            ),
            prompt_token_overhead_reservation=_positive_integer(
                raw["promptTokenOverheadReservation"],
                "promptTokenOverheadReservation",
            ),
            maximum_completion_tokens_per_call=_positive_integer(
                raw["maximumCompletionTokensPerCall"],
                "maximumCompletionTokensPerCall",
            ),
            maximum_total_reserved_tokens=_positive_integer(
                raw["maximumTotalReservedTokens"],
                "maximumTotalReservedTokens",
            ),
            maximum_total_reported_tokens=_positive_integer(
                raw["maximumTotalReportedTokens"],
                "maximumTotalReportedTokens",
            ),
            maximum_single_call_cost_usd=_nonnegative_decimal(
                raw["maximumSingleCallCostUsd"], "maximumSingleCallCostUsd"
            ),
            maximum_total_cost_usd=_nonnegative_decimal(
                raw["maximumTotalCostUsd"], "maximumTotalCostUsd"
            ),
        )
        if (
            budgets.maximum_conservative_prompt_tokens
            < budgets.maximum_request_bytes
            + budgets.prompt_token_overhead_reservation
        ):
            raise MathFlowError(
                "maximumConservativePromptTokens cannot cover the request reservation"
            )
        worst_call = (
            budgets.maximum_conservative_prompt_tokens
            + budgets.maximum_completion_tokens_per_call
        )
        if (
            budgets.maximum_total_reserved_tokens
            < budgets.maximum_provider_calls * worst_call
        ):
            raise MathFlowError(
                "maximumTotalReservedTokens cannot cover every permitted call"
            )
        if (
            budgets.maximum_total_cost_usd
            < budgets.maximum_provider_calls
            * budgets.maximum_single_call_cost_usd
        ):
            raise MathFlowError(
                "maximumTotalCostUsd cannot cover every permitted cost reservation"
            )
        return budgets

    def as_json(self) -> dict[str, object]:
        result = asdict(self)
        return {
            key: (float(value) if isinstance(value, Decimal) else value)
            for key, value in result.items()
        }


def _configuration(value: object) -> SyntheticBuilderStateConfig:
    raw = _require_exact_fields(
        value, CONFIGURATION_FIELDS, "widening case configuration"
    )
    return SyntheticBuilderStateConfig(
        program_count=_positive_integer(raw["programCount"], "programCount"),
        result_count=_positive_integer(raw["resultCount"], "resultCount"),
        maximum_depth=_positive_integer(raw["maximumDepth"], "maximumDepth"),
        maximum_width=_positive_integer(raw["maximumWidth"], "maximumWidth"),
        provenance_per_result=_positive_integer(
            raw["provenancePerResult"], "provenancePerResult"
        ),
        dependency_depth=_positive_integer(
            raw["dependencyDepth"], "dependencyDepth"
        ),
        dependency_width=_positive_integer(
            raw["dependencyWidth"], "dependencyWidth"
        ),
        support_bytes=_positive_integer(raw["supportBytes"], "supportBytes"),
        summary_bytes=_positive_integer(raw["summaryBytes"], "summaryBytes"),
        evidence_bytes=_positive_integer(raw["evidenceBytes"], "evidenceBytes"),
        challenges=ADVERSARIAL_CHALLENGES,
    ).validate()


def load_widening_manifest(
    path: Path, *, repository_root: Path
) -> dict[str, object]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise MathFlowError("could not load the V10 widening manifest") from exc
    return validate_widening_manifest(value, repository_root=repository_root)


def validate_widening_manifest(
    value: object, *, repository_root: Path
) -> dict[str, object]:
    manifest = _require_exact_fields(
        value, MANIFEST_FIELDS, "V10 widening manifest"
    )
    if (
        manifest.get("schemaVersion") != 1
        or manifest.get("status") != "unpublished-experiment"
        or manifest.get("publicationForbidden") is not True
        or manifest.get("providerExecutionDefault") != "disabled"
        or manifest.get("stopOnFirstHardFailure") is not True
    ):
        raise MathFlowError(
            "V10 widening experiment must remain unpublished, disabled, and fail-fast"
        )
    for field in (
        "id",
        "description",
        "judgeSpec",
        "judgeSpecDigest",
        "model",
        "reasoningEffort",
        "authorizationEnvironmentVariable",
        "authorizationValue",
    ):
        if not isinstance(manifest.get(field), str) or not str(manifest[field]).strip():
            raise MathFlowError(f"V10 widening manifest {field} is invalid")
    _positive_integer(manifest.get("seed"), "seed")
    attempts = _positive_integer(
        manifest.get("maximumAttemptsPerStage"), "maximumAttemptsPerStage"
    )
    _positive_integer(
        manifest.get("maximumProgramsInAuthorPacket"),
        "maximumProgramsInAuthorPacket",
    )
    _positive_integer(
        manifest.get("maximumResultsInAuthorPacket"),
        "maximumResultsInAuthorPacket",
    )
    budgets = WideningBudgets.from_mapping(manifest.get("budgets"))

    spec_path = repository_root / str(manifest["judgeSpec"])
    try:
        raw_spec = spec_path.read_bytes()
        spec = json.loads(raw_spec.decode("utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise MathFlowError("V10 widening judge spec is unavailable") from exc
    if sha256_bytes(raw_spec) != manifest["judgeSpecDigest"]:
        raise MathFlowError("V10 widening judge spec digest mismatch")
    if not isinstance(spec, dict) or spec.get("model") != manifest["model"]:
        raise MathFlowError("V10 widening manifest model does not match its judge")
    stages = spec.get("stages")
    if not isinstance(stages, dict):
        raise MathFlowError("V10 widening judge has no stages")
    for stage in ("route", "route-refine"):
        stage_value = stages.get(stage)
        parameters = (
            stage_value.get("parameters") if isinstance(stage_value, dict) else None
        )
        reasoning = (
            parameters.get("reasoning") if isinstance(parameters, dict) else None
        )
        if (
            not isinstance(parameters, dict)
            or _positive_integer(parameters.get("max_tokens"), f"{stage} max_tokens")
            > budgets.maximum_completion_tokens_per_call
            or not isinstance(reasoning, dict)
            or reasoning.get("effort") != manifest["reasoningEffort"]
        ):
            raise MathFlowError(
                f"V10 widening manifest does not bind the {stage} parameters"
            )

    cases = manifest.get("cases")
    if not isinstance(cases, list) or not cases:
        raise MathFlowError("V10 widening manifest needs cases")
    case_ids: list[str] = []
    widening_sizes: list[int] = []
    evidence_only_ids: list[str] = []
    for raw_case in cases:
        case = _require_exact_fields(raw_case, CASE_FIELDS, "V10 widening case")
        case_id = case.get("id")
        phase = case.get("phase")
        challenge = case.get("challenge")
        clue_mode = case.get("clueMode")
        history_steps = case.get("historySteps")
        if (
            not isinstance(case_id, str)
            or not case_id
            or phase not in PHASES
            or challenge not in ADVERSARIAL_CHALLENGES
            or clue_mode not in CLUE_MODES
        ):
            raise MathFlowError("V10 widening case is invalid")
        config = _configuration(case.get("configuration"))
        if phase == "sequential-growth":
            if (
                isinstance(history_steps, bool)
                or not isinstance(history_steps, int)
                or not 50 <= history_steps <= 100
            ):
                raise MathFlowError(
                    "sequential-growth case must declare 50-100 history steps"
                )
        elif history_steps is not None:
            raise MathFlowError(
                "only sequential-growth cases may declare history steps"
            )
        case_ids.append(case_id)
        if phase == "widening":
            widening_sizes.append(config.program_count)
        if clue_mode == "evidence-only":
            evidence_only_ids.append(case_id)
            if phase != "limitation":
                raise MathFlowError(
                    "evidence-only routing clue must be an explicit limitation case"
                )
        elif phase == "limitation":
            raise MathFlowError("limitation case must use the evidence-only clue")
    if len(case_ids) != len(set(case_ids)):
        raise MathFlowError("V10 widening case IDs must be unique")
    if widening_sizes != sorted(set(widening_sizes)):
        raise MathFlowError("V10 widening sizes must be strictly increasing")
    if len(evidence_only_ids) != 1:
        raise MathFlowError("V10 widening suite needs exactly one evidence-only case")
    if budgets.maximum_provider_calls != len(cases) * 2 * attempts:
        raise MathFlowError(
            "maximumProviderCalls must reserve route and refine retries for every case"
        )
    return copy.deepcopy(manifest)


def load_bound_widening_spec(
    manifest: Mapping[str, object], *, repository_root: Path
) -> dict[str, object]:
    path = repository_root / str(manifest["judgeSpec"])
    raw = path.read_bytes()
    if sha256_bytes(raw) != manifest.get("judgeSpecDigest"):
        raise MathFlowError("V10 widening judge spec changed after validation")
    value = json.loads(raw.decode("utf-8"))
    if not isinstance(value, dict):
        raise MathFlowError("V10 widening judge spec must be an object")
    spec = copy.deepcopy(value)
    spec["id"] = f"{value['id']}-widening-v1"
    parameters = copy.deepcopy(spec.get("parameters", {}))
    parameters["seed"] = manifest["seed"]
    spec["parameters"] = parameters
    retry = copy.deepcopy(spec.get("retryPolicy", {}))
    retry["maximumAttempts"] = manifest["maximumAttemptsPerStage"]
    spec["retryPolicy"] = retry
    return spec


def _validate_runtime_contract(
    manifest: Mapping[str, object], spec: Mapping[str, object]
) -> None:
    if (
        manifest.get("publicationForbidden") is not True
        or manifest.get("providerExecutionDefault") != "disabled"
        or manifest.get("stopOnFirstHardFailure") is not True
    ):
        raise MathFlowError("V10 widening runtime contract is not fail-closed")
    if (
        spec.get("implementation")
        != "openrouter-hierarchical-research-builder-v10"
        or spec.get("model") != manifest.get("model")
    ):
        raise MathFlowError("V10 widening runtime judge identity changed")
    parameters = spec.get("parameters")
    retry = spec.get("retryPolicy")
    if (
        not isinstance(parameters, dict)
        or parameters.get("seed") != manifest.get("seed")
        or not isinstance(retry, dict)
        or retry.get("maximumAttempts")
        != manifest.get("maximumAttemptsPerStage")
    ):
        raise MathFlowError("V10 widening runtime seed/retry contract changed")
    budgets = WideningBudgets.from_mapping(manifest.get("budgets"))
    stages = spec.get("stages")
    if not isinstance(stages, dict):
        raise MathFlowError("V10 widening runtime judge has no stages")
    for stage in ("route", "route-refine"):
        stage_value = stages.get(stage)
        stage_parameters = (
            stage_value.get("parameters")
            if isinstance(stage_value, dict)
            else None
        )
        reasoning = (
            stage_parameters.get("reasoning")
            if isinstance(stage_parameters, dict)
            else None
        )
        if (
            not isinstance(stage_parameters, dict)
            or _positive_integer(
                stage_parameters.get("max_tokens"), f"runtime {stage} max_tokens"
            )
            > budgets.maximum_completion_tokens_per_call
            or not isinstance(reasoning, dict)
            or reasoning.get("effort") != manifest.get("reasoningEffort")
        ):
            raise MathFlowError(f"V10 widening runtime {stage} contract changed")


def _extend_hot_branch_history(
    fixture: dict[str, object], *, history_steps: int
) -> None:
    """Add accepted provenance to one dependency result without widening topology."""

    state = fixture.get("state")
    claims = fixture.get("acceptedClaims")
    if not isinstance(state, dict) or not isinstance(claims, list) or not claims:
        raise MathFlowError("hot-branch growth fixture is invalid")
    dependency_ids = claims[0].get("dependencyTransactionIds") if isinstance(claims[0], dict) else None
    contributions = copy.deepcopy(state.get("contributions"))
    programs = copy.deepcopy(state.get("programs"))
    results = copy.deepcopy(state.get("intermediateResults"))
    if (
        not isinstance(dependency_ids, list)
        or len(dependency_ids) != 1
        or not isinstance(contributions, dict)
        or not isinstance(programs, dict)
        or not isinstance(results, dict)
    ):
        raise MathFlowError("hot-branch growth dependency is invalid")
    original_transaction = str(dependency_ids[0])
    original = contributions.get(original_transaction)
    if not isinstance(original, dict):
        raise MathFlowError("hot-branch source contribution is absent")
    target_ids = original.get("intermediateResultIds")
    if not isinstance(target_ids, list) or len(target_ids) != 1:
        raise MathFlowError("hot-branch source must map to one result")
    target_id = str(target_ids[0])
    target = results.get(target_id)
    if not isinstance(target, dict):
        raise MathFlowError("hot-branch target result is absent")
    source_ids = list(target["sourceTransactionIds"])
    claim_refs = copy.deepcopy(target["claimRefs"])
    judgment_ids = list(target["judgmentIds"])
    new_transactions: list[str] = []
    for step in range(2, history_steps + 1):
        transaction_id = hashlib.sha1(
            f"builder-v10-hot-branch:{target_id}:{step}".encode("utf-8")
        ).hexdigest()
        judgment_id = "sha256:" + hashlib.sha256(
            f"builder-v10-hot-branch-judgment:{target_id}:{step}".encode("utf-8")
        ).hexdigest()
        claim_key = f"claim/hot-branch/step-{step:04d}"
        contributions[transaction_id] = _normalize_contribution(
            transaction_id,
            {
                "id": transaction_id,
                "transactionId": transaction_id,
                "claimKeys": [claim_key],
                "directProgramIds": copy.deepcopy(original["directProgramIds"]),
                "intermediateResultIds": [target_id],
                "dependencyTransactionIds": copy.deepcopy(
                    original["dependencyTransactionIds"]
                ),
                "judgmentId": judgment_id,
            },
        )
        source_ids.append(transaction_id)
        judgment_ids.append(judgment_id)
        claim_refs.append(
            {"transactionId": transaction_id, "claimKey": claim_key}
        )
        new_transactions.append(transaction_id)
    target_raw = {key: copy.deepcopy(value) for key, value in target.items() if key != "digest"}
    target_raw["sourceTransactionIds"] = source_ids
    target_raw["claimRefs"] = claim_refs
    target_raw["judgmentIds"] = judgment_ids
    results[target_id] = _normalize_result(target_id, target_raw)
    for program_id, program in list(programs.items()):
        if not isinstance(program, dict):
            continue
        prior_sources = program.get("sourceTransactionIds")
        if not isinstance(prior_sources, list) or original_transaction not in prior_sources:
            continue
        raw_program = {
            key: copy.deepcopy(value)
            for key, value in program.items()
            if key != "digest"
        }
        raw_program["sourceTransactionIds"] = [*prior_sources, *new_transactions]
        programs[str(program_id)] = _normalize_program(str(program_id), raw_program)
    state_raw = {
        key: copy.deepcopy(value)
        for key, value in state.items()
        if key not in {"stateDigest", "programs", "intermediateResults", "contributions", "ledgerHead"}
    }
    state_raw.update(
        {
            "ledgerHead": new_transactions[-1],
            "programs": programs,
            "intermediateResults": results,
            "contributions": contributions,
        }
    )
    extended = _with_state_digest(state_raw)
    validate_research_program_state_v3(extended)
    fixture["state"] = extended
    fixture["sequentialGrowth"] = {
        "historySteps": history_steps,
        "hotResultId": target_id,
        "initialTransactionId": original_transaction,
        "finalTransactionId": new_transactions[-1],
        "topologyChanged": False,
    }


def materialize_widening_case(case: Mapping[str, object]) -> dict[str, object]:
    validated = _require_exact_fields(
        copy.deepcopy(dict(case)), CASE_FIELDS, "V10 widening case"
    )
    config = _configuration(validated["configuration"])
    fixture = build_synthetic_builder_fixture(config)
    history_steps = validated.get("historySteps")
    if isinstance(history_steps, int) and not isinstance(history_steps, bool):
        _extend_hot_branch_history(fixture, history_steps=history_steps)
    challenges = fixture.get("challenges")
    if not isinstance(challenges, dict) or not isinstance(
        challenges.get(validated["challenge"]), dict
    ):
        raise MathFlowError("V10 widening case challenge was not materialized")
    challenge = challenges[str(validated["challenge"])]
    query = challenge.get("query")
    if not isinstance(query, str) or not query:
        raise MathFlowError("V10 widening case has no semantic routing clue")
    claims = copy.deepcopy(fixture["acceptedClaims"])
    evidence = copy.deepcopy(fixture["submissionEvidence"])
    assert isinstance(claims, list) and isinstance(claims[0], dict)
    files = evidence.get("files") if isinstance(evidence, dict) else None
    if not isinstance(files, list) or not files or not isinstance(files[0], dict):
        raise MathFlowError("V10 widening fixture has no submission evidence")
    if validated["clueMode"] == "validity-summary":
        claims[0]["validitySummary"] = (
            "Accepted routing-relevant semantic description: " + query + "."
        )
    else:
        claims[0]["validitySummary"] = (
            "The benchmark's restricted current statement is accepted; no topical "
            "routing clue is included in this validity surface."
        )
        files[0]["content"] = str(files[0].get("content", "")) + "\n" + query
    fixture["acceptedClaims"] = claims
    fixture["submissionEvidence"] = evidence
    fixture["activeChallenge"] = copy.deepcopy(challenge)
    fixture["caseId"] = validated["id"]
    fixture["phase"] = validated["phase"]
    fixture["clueMode"] = validated["clueMode"]
    fixture["semanticClue"] = query
    fixture["fixtureDigest"] = _digest(
        {
            "configuration": fixture["configuration"],
            "stateDigest": fixture["state"]["stateDigest"],
            "acceptedClaims": claims,
            "submissionEvidence": evidence,
            "activeChallenge": challenge,
            "caseId": validated["id"],
            "sequentialGrowth": fixture.get("sequentialGrowth"),
        }
    )
    return fixture


def _route_input_from_request(request: Mapping[str, object]) -> dict[str, object]:
    messages = request.get("messages")
    if not isinstance(messages, list):
        raise MathFlowError("V10 widening request has no messages")
    prefix = "<math-flow-input>\n"
    suffix = "\n</math-flow-input>"
    for message in reversed(messages):
        content = message.get("content") if isinstance(message, dict) else None
        if not isinstance(content, str) or prefix not in content:
            continue
        quoted = content.split(prefix, 1)[1]
        if not quoted.endswith(suffix):
            raise MathFlowError("V10 widening request has a malformed quoted input")
        try:
            parsed = json.loads(quoted[: -len(suffix)])
        except json.JSONDecodeError as exc:
            raise MathFlowError("V10 widening request quoted input is invalid") from exc
        if not isinstance(parsed, dict):
            raise MathFlowError("V10 widening request quoted input is not an object")
        return parsed
    raise MathFlowError("V10 widening request has no quoted route input")


def _request_components(request: Mapping[str, object]) -> dict[str, object]:
    messages = request.get("messages")
    if not isinstance(messages, list) or len(messages) < 3:
        raise MathFlowError("V10 widening request messages are incomplete")
    schema = request.get("response_format")
    return {
        "systemPrompt": messages[0],
        "stagePrompt": messages[1],
        "userEnvelope": messages[2:],
        "routeInput": _route_input_from_request(request),
        "responseFormat": schema,
    }


def _finish_reason(response: Mapping[str, object]) -> str | None:
    choices = response.get("choices")
    if not isinstance(choices, list) or not choices or not isinstance(choices[0], dict):
        return None
    value = choices[0].get("finish_reason")
    return value if isinstance(value, str) else None


def _output_text(response: Mapping[str, object]) -> str:
    choices = response.get("choices")
    if not isinstance(choices, list) or not choices or not isinstance(choices[0], dict):
        return ""
    message = choices[0].get("message")
    if not isinstance(message, dict):
        return ""
    content = message.get("content")
    if isinstance(content, str):
        return content
    parsed = message.get("parsed")
    return (
        json.dumps(parsed, sort_keys=True, ensure_ascii=False)
        if parsed is not None
        else ""
    )


class WideningBudgetedTransport:
    """Reserve every call before transport and retain exact provider telemetry.

    Cost is bounded by a per-call reservation supplied by the manifest.  No
    client can stop an already accepted provider request whose actual charge
    violates that asserted bound, so such a violation permanently blocks all
    later calls and is reported as a hard protocol failure.
    """

    def __init__(
        self,
        budgets: WideningBudgets,
        *,
        transport: Callable[[dict[str, object]], dict[str, object]],
    ) -> None:
        self.budgets = budgets
        self.transport = transport
        self.case_id: str | None = None
        self.stage: str | None = None
        self.records: list[dict[str, object]] = []
        self.blocked_records: list[dict[str, object]] = []
        self.blocked_reason: str | None = None
        self.reserved_tokens = 0
        self.reserved_cost_usd = Decimal("0")
        self.reported_tokens = 0
        self.reported_cost_usd = Decimal("0")
        self._attempts: dict[tuple[str, str], int] = {}

    def begin(self, *, case_id: str, stage: str) -> None:
        if stage not in {"route", "route-refine"}:
            raise MathFlowError("V10 widening transport only permits route/refine")
        self.case_id = case_id
        self.stage = stage

    def _block(self, reason: str, record: dict[str, object] | None = None) -> None:
        self.blocked_reason = reason
        if record is not None:
            blocked = copy.deepcopy(record)
            blocked["outcome"] = "blocked-before-provider"
            blocked["blockedReason"] = reason
            self.blocked_records.append(blocked)
        raise MathFlowError(reason)

    def __call__(self, request: dict[str, object]) -> dict[str, object]:
        if self.case_id is None or self.stage is None:
            raise MathFlowError("V10 widening transport stage was not declared")
        key = (self.case_id, self.stage)
        attempt = self._attempts.get(key, 0) + 1
        self._attempts[key] = attempt
        measurement = measure_serialized_value(request)
        components = _request_components(request)
        component_measurements = {
            name: {
                **measure_serialized_value(value),
                "digest": _digest(value),
            }
            for name, value in sorted(components.items())
        }
        request_bytes = int(measurement["utf8Bytes"])
        estimated_prompt = int(measurement["estimatedTokens"])
        conservative_prompt = (
            request_bytes + self.budgets.prompt_token_overhead_reservation
        )
        maximum_completion = request.get("max_tokens")
        record: dict[str, object] = {
            "schemaVersion": 1,
            "caseId": self.case_id,
            "stage": self.stage,
            "attempt": attempt,
            "requestDigest": _digest(request),
            "rawRequest": copy.deepcopy(request),
            "requestMeasurement": measurement,
            "contextMeasurement": measure_serialized_value(
                components["routeInput"]
            ),
            "requestComponents": component_measurements,
            "estimatedPromptTokens": estimated_prompt,
            "conservativePromptTokenReservation": conservative_prompt,
            "maximumCompletionTokenReservation": maximum_completion,
        }
        if self.blocked_reason is not None:
            self._block(self.blocked_reason, record)
        if len(self.records) >= self.budgets.maximum_provider_calls:
            self._block("V10 widening provider-call budget exhausted", record)
        if request_bytes > self.budgets.maximum_request_bytes:
            self._block(
                "V10 widening request-byte budget exhausted: "
                f"{request_bytes} > {self.budgets.maximum_request_bytes}",
                record,
            )
        if estimated_prompt > self.budgets.maximum_estimated_prompt_tokens:
            self._block(
                "V10 widening estimated prompt-token budget exhausted", record
            )
        if (
            conservative_prompt
            > self.budgets.maximum_conservative_prompt_tokens
        ):
            self._block(
                "V10 widening conservative prompt-token budget exhausted", record
            )
        if (
            isinstance(maximum_completion, bool)
            or not isinstance(maximum_completion, int)
            or maximum_completion < 1
            or maximum_completion
            > self.budgets.maximum_completion_tokens_per_call
        ):
            self._block(
                "V10 widening completion-token reservation is invalid", record
            )
        call_reservation = conservative_prompt + maximum_completion
        if (
            self.reserved_tokens + call_reservation
            > self.budgets.maximum_total_reserved_tokens
        ):
            self._block("V10 widening total token reservation exhausted", record)
        if (
            self.reserved_cost_usd
            + self.budgets.maximum_single_call_cost_usd
            > self.budgets.maximum_total_cost_usd
        ):
            self._block("V10 widening total cost reservation exhausted", record)

        self.reserved_tokens += call_reservation
        self.reserved_cost_usd += self.budgets.maximum_single_call_cost_usd
        record["providerCallIndex"] = len(self.records) + 1
        record["cumulativeReservedTokens"] = self.reserved_tokens
        record["cumulativeReservedCostUsd"] = float(self.reserved_cost_usd)
        try:
            response = self.transport(copy.deepcopy(request))
        except Exception:
            self.blocked_reason = (
                "V10 widening transport outcome is uncertain; later calls are blocked"
            )
            record["outcome"] = "transport-uncertain"
            record["blockedReason"] = self.blocked_reason
            self.records.append(record)
            raise
        if not isinstance(response, dict):
            self.blocked_reason = (
                "V10 widening transport returned a non-object; later calls are blocked"
            )
            record["outcome"] = "invalid-provider-telemetry"
            self.records.append(record)
            raise MathFlowError(self.blocked_reason)

        record["rawResponse"] = copy.deepcopy(response)
        record["responseDigest"] = _digest(response)
        record["responseMeasurement"] = measure_serialized_value(response)
        usage = response.get("usage")
        if not isinstance(usage, dict):
            self.blocked_reason = (
                "V10 widening response omitted usage telemetry; later calls are blocked"
            )
            record["outcome"] = "invalid-provider-telemetry"
            self.records.append(record)
            raise MathFlowError(self.blocked_reason)
        token_values: dict[str, int] = {}
        for field in ("prompt_tokens", "completion_tokens", "total_tokens"):
            value = usage.get(field)
            if isinstance(value, bool) or not isinstance(value, int) or value < 0:
                self.blocked_reason = (
                    "V10 widening response omitted exact token telemetry; later calls are blocked"
                )
                record["outcome"] = "invalid-provider-telemetry"
                self.records.append(record)
                raise MathFlowError(self.blocked_reason)
            token_values[field] = value
        if token_values["total_tokens"] != (
            token_values["prompt_tokens"] + token_values["completion_tokens"]
        ):
            self.blocked_reason = (
                "V10 widening response token telemetry is inconsistent; later calls are blocked"
            )
            record["outcome"] = "invalid-provider-telemetry"
            self.records.append(record)
            raise MathFlowError(self.blocked_reason)
        try:
            cost = _nonnegative_decimal(usage.get("cost"), "provider usage cost")
        except MathFlowError:
            self.blocked_reason = (
                "V10 widening response omitted exact cost telemetry; later calls are blocked"
            )
            record["outcome"] = "invalid-provider-telemetry"
            record["blockedReason"] = self.blocked_reason
            self.records.append(record)
            raise MathFlowError(self.blocked_reason)
        details = usage.get("completion_tokens_details")
        reasoning_tokens = 0
        if isinstance(details, dict):
            raw_reasoning = details.get("reasoning_tokens", 0)
            if (
                isinstance(raw_reasoning, bool)
                or not isinstance(raw_reasoning, int)
                or raw_reasoning < 0
            ):
                self.blocked_reason = (
                    "V10 widening reasoning telemetry is invalid; later calls are blocked"
                )
                record["outcome"] = "invalid-provider-telemetry"
                self.records.append(record)
                raise MathFlowError(self.blocked_reason)
            reasoning_tokens = raw_reasoning
        self.reported_tokens += token_values["total_tokens"]
        self.reported_cost_usd += cost
        output = _output_text(response)
        record["usage"] = {
            "promptTokens": token_values["prompt_tokens"],
            "completionTokens": token_values["completion_tokens"],
            "reasoningTokens": reasoning_tokens,
            "totalTokens": token_values["total_tokens"],
            "costUsd": float(cost),
        }
        record["model"] = response.get("model")
        record["finishReason"] = _finish_reason(response)
        record["outputMeasurement"] = {
            "characters": len(output),
            "utf8Bytes": len(output.encode("utf-8")),
            "trailingWhitespaceCharacters": len(output) - len(output.rstrip()),
        }
        record["cumulativeReportedTokens"] = self.reported_tokens
        record["cumulativeReportedCostUsd"] = float(self.reported_cost_usd)
        record["outcome"] = "provider-response-recorded"
        self.records.append(record)
        violations: list[str] = []
        if token_values["prompt_tokens"] > conservative_prompt:
            violations.append("reported prompt tokens exceed reservation")
        if token_values["completion_tokens"] > maximum_completion:
            violations.append("reported completion tokens exceed reservation")
        if self.reported_tokens > self.budgets.maximum_total_reported_tokens:
            violations.append("reported total token budget exhausted")
        if cost > self.budgets.maximum_single_call_cost_usd:
            violations.append("reported single-call cost exceeds reservation")
        if self.reported_cost_usd > self.budgets.maximum_total_cost_usd:
            violations.append("reported total cost budget exhausted")
        if violations:
            self.blocked_reason = (
                "V10 widening provider telemetry violated a hard stop: "
                + "; ".join(violations)
            )
            record["outcome"] = "hard-budget-violation"
            record["blockedReason"] = self.blocked_reason
            raise MathFlowError(self.blocked_reason)
        return copy.deepcopy(response)

    def summary(self) -> dict[str, object]:
        return {
            "schemaVersion": 1,
            "providerCalls": len(self.records),
            "blockedAttempts": len(self.blocked_records),
            "reservedTokens": self.reserved_tokens,
            "reservedCostUsd": float(self.reserved_cost_usd),
            "reportedTokens": self.reported_tokens,
            "reportedCostUsd": float(self.reported_cost_usd),
            "blockedReason": self.blocked_reason,
            "requestRecords": copy.deepcopy(self.records),
            "blockedRequestRecords": copy.deepcopy(self.blocked_records),
        }


def _case_identity(case_id: str) -> tuple[str, str]:
    transaction_id = hashlib.sha1(
        f"local-builder-v10-widening:{case_id}".encode("utf-8")
    ).hexdigest()
    judgment_id = "sha256:" + hashlib.sha256(
        f"local-builder-v10-widening-judgment:{case_id}".encode("utf-8")
    ).hexdigest()
    return transaction_id, judgment_id


def _validate_route_factory(
    *,
    state: Mapping[str, object],
    accepted_claims: object,
    route_context: Mapping[str, object],
    catalog: Mapping[str, object],
    max_programs: int,
    max_results: int,
) -> Callable[[object], dict[str, object]]:
    def validate(value: object) -> dict[str, object]:
        bound = bind_research_builder_v10_route_plan(
            route_context, catalog, value
        )
        build_research_builder_v10_authoring_packet(
            state,
            accepted_claims,
            bound,
            route_context=route_context,
            max_programs=max_programs,
            max_results=max_results,
        )
        return bound

    return validate


def measure_packet_entity_duplication(packet: Mapping[str, object]) -> dict[str, object]:
    """Measure repeated entity semantics inside one serialized local packet."""

    occurrences: list[tuple[str, str, int, str]] = []

    def add(kind: str, entity_id: str, value: object, path: str) -> None:
        occurrences.append(
            (kind, entity_id, int(measure_serialized_value(value)["utf8Bytes"]), path)
        )

    def visit(value: object, path: str) -> None:
        if isinstance(value, dict):
            entity_kind = value.get("entityKind")
            entity_id = value.get("entityId")
            if (
                entity_kind in {"program", "intermediateResult"}
                and isinstance(entity_id, str)
            ):
                add(str(entity_kind), entity_id, value, path)
            for collection_name, kind in (
                ("programs", "program"),
                ("intermediateResults", "intermediateResult"),
            ):
                collection = value.get(collection_name)
                if isinstance(collection, dict):
                    for item_id, item in collection.items():
                        if isinstance(item_id, str) and isinstance(item, dict):
                            add(
                                kind,
                                item_id,
                                item,
                                f"{path}/{collection_name}/{item_id}",
                            )
            for key, item in value.items():
                visit(item, f"{path}/{key}")
        elif isinstance(value, list):
            for index, item in enumerate(value):
                visit(item, f"{path}/{index}")

    visit(packet, "$")
    grouped: dict[tuple[str, str], list[tuple[int, str]]] = {}
    for kind, entity_id, size, path in occurrences:
        grouped.setdefault((kind, entity_id), []).append((size, path))
    repeated = {
        key: values for key, values in grouped.items() if len(values) > 1
    }
    duplicate_occurrences = sum(len(values) - 1 for values in grouped.values())
    repeated_bytes = sum(
        sum(size for size, _ in values[1:]) for values in grouped.values()
    )
    top = sorted(
        (
            {
                "entityKind": kind,
                "entityId": entity_id,
                "occurrences": len(values),
                "occurrenceBytes": sum(size for size, _ in values),
                "repeatedBytesAfterFirst": sum(size for size, _ in values[1:]),
                "paths": [path for _, path in values],
            }
            for (kind, entity_id), values in repeated.items()
        ),
        key=lambda item: (
            -int(item["repeatedBytesAfterFirst"]),
            str(item["entityKind"]),
            str(item["entityId"]),
        ),
    )[:20]
    total = len(occurrences)
    return {
        "schemaVersion": 1,
        "packetBytes": int(measure_serialized_value(packet)["utf8Bytes"]),
        "entityOccurrences": total,
        "uniqueEntities": len(grouped),
        "duplicateEntityOccurrences": duplicate_occurrences,
        "duplicateOccurrenceFraction": (
            duplicate_occurrences / total if total else 0.0
        ),
        "repeatedEntityBytesAfterFirst": repeated_bytes,
        "repeatedEntityBytesFractionOfPacket": (
            repeated_bytes / int(measure_serialized_value(packet)["utf8Bytes"])
            if packet
            else 0.0
        ),
        "topRepeatedEntities": top,
    }


def _score_route_refine_case(
    fixture: Mapping[str, object],
    final_plan: Mapping[str, object],
    authoring_packet: Mapping[str, object],
    request_records: Sequence[Mapping[str, object]],
) -> dict[str, object]:
    challenge = fixture.get("activeChallenge")
    if not isinstance(challenge, dict):
        raise MathFlowError("V10 widening fixture has no active challenge")
    read_set = authoring_packet.get("readSet")
    write_scope = authoring_packet.get("writeScope")
    if not isinstance(read_set, dict) or not isinstance(write_scope, dict):
        raise MathFlowError("V10 widening authoring packet has no scopes")
    programs = {str(item) for item in read_set.get("programIds", [])}
    results = {str(item) for item in read_set.get("resultIds", [])}
    writes = {
        *(f"program:{item}" for item in write_scope.get("existingProgramIds", [])),
        *(f"intermediateResult:{item}" for item in write_scope.get("existingResultIds", [])),
    }
    checks: dict[str, bool] = {
        "requiredProgramsLoaded": set(challenge.get("requiredProgramIds", []))
        <= programs,
        "requiredResultsLoaded": set(challenge.get("requiredResultIds", []))
        <= results,
        "requiredWriteScopeLoaded": set(
            challenge.get("requiredWriteEntityIds", [])
        )
        <= writes,
    }
    if challenge.get("requiredParentProgramId") == "root":
        checks["rootContextLoaded"] = "root" in programs
        checks["newProgramReserved"] = bool(final_plan.get("createProgramIds"))
        forbidden = challenge.get("forbiddenParentProgramId")
        if isinstance(forbidden, str):
            checks["forbiddenLocalParentNotSelectedAsSoleWrite"] = (
                set(final_plan.get("writeProgramIds", [])) != {forbidden}
            )
    clue = fixture.get("semanticClue")
    if not isinstance(clue, str):
        raise MathFlowError("V10 widening fixture has no semantic clue")
    request_texts = [
        json.dumps(
            record.get("rawRequest"),
            sort_keys=True,
            ensure_ascii=False,
        )
        for record in request_records
    ]
    evidence = fixture.get("submissionEvidence")
    evidence_text = json.dumps(evidence, sort_keys=True, ensure_ascii=False)
    clue_mode = fixture.get("clueMode")
    if clue_mode == "evidence-only":
        boundary_checks = {
            "cluePresentInEvidence": clue in evidence_text,
            "clueAbsentFromEveryRouteRequest": all(
                clue not in request_text for request_text in request_texts
            ),
        }
        hard_checks = boundary_checks
        routing_checks = checks
        hard_passed = all(boundary_checks.values())
        passed = hard_passed
        advisory = {
            "expectedLimitation": (
                "Route/refine is intentionally author-blind and cannot use a clue "
                "that exists only in raw submission evidence."
            ),
            "routingRecoveredDespiteWithheldClue": all(routing_checks.values()),
        }
    else:
        visibility = {
            "cluePresentInEveryRouteStage": all(
                clue in request_text for request_text in request_texts
            )
        }
        hard_checks = {**checks, **visibility}
        routing_checks = checks
        hard_passed = all(hard_checks.values())
        passed = hard_passed
        advisory = None
    return {
        "schemaVersion": 1,
        "challenge": fixture.get("activeChallenge"),
        "clueMode": clue_mode,
        "hardPassed": hard_passed,
        "passed": passed,
        "hardChecks": hard_checks,
        "routingChecks": routing_checks,
        "advisory": advisory,
        "missingProgramIds": sorted(
            set(challenge.get("requiredProgramIds", [])) - programs
        ),
        "missingResultIds": sorted(
            set(challenge.get("requiredResultIds", [])) - results
        ),
        "missingWriteIds": sorted(
            set(challenge.get("requiredWriteEntityIds", [])) - writes
        ),
    }


def run_v10_route_refine_case(
    *,
    provider: OpenRouterResearchBuilderV10Provider,
    budgeted_transport: WideningBudgetedTransport,
    fixture: Mapping[str, object],
    max_programs: int,
    max_results: int,
) -> dict[str, object]:
    """Run only the two discovery stages; authoring is structurally unreachable."""

    case_id = fixture.get("caseId")
    state = fixture.get("state")
    accepted_claims = fixture.get("acceptedClaims")
    if (
        not isinstance(case_id, str)
        or not isinstance(state, dict)
        or not isinstance(accepted_claims, list)
    ):
        raise MathFlowError("V10 widening case fixture is invalid")
    problem_id = state.get("problemId")
    base_digest = state.get("stateDigest")
    if not isinstance(problem_id, str) or not isinstance(base_digest, str):
        raise MathFlowError("V10 widening state identity is invalid")
    transaction_id, judgment_id = _case_identity(case_id)
    catalog = build_research_builder_v10_catalog(state)
    route_context = build_research_builder_v10_route_context(
        state, accepted_claims
    )
    route_schema = _route_plan_schema_v10(
        base_state_digest=base_digest,
        route_context_digest=str(route_context["contextDigest"]),
    )
    validate_route = _validate_route_factory(
        state=state,
        accepted_claims=accepted_claims,
        route_context=route_context,
        catalog=catalog,
        max_programs=max_programs,
        max_results=max_results,
    )
    record_start = len(budgeted_transport.records)
    blocked_start = len(budgeted_transport.blocked_records)
    budgeted_transport.begin(case_id=case_id, stage="route")
    discovery_plan = provider._invoke(
        stage="route",
        user_data={
            "schemaVersion": 1,
            "role": "builder-v10-local-portfolio-router",
            "problemId": problem_id,
            "subjectTransactionId": transaction_id,
            "routeContext": route_context,
            "acceptedClaimAssessments": copy.deepcopy(accepted_claims),
            "judgmentId": judgment_id,
        },
        schema=route_schema,
        validate=validate_route,
        retry_feedback=lambda exc, attempt: (
            f"Trusted route validation rejected attempt {attempt}: "
            + json.dumps(str(exc)[:1000], ensure_ascii=False)
            + ". Return a complete route plan bound to the original digests."
        ),
    )
    discovery_packet = build_research_builder_v10_authoring_packet(
        state,
        accepted_claims,
        discovery_plan,
        route_context=route_context,
        max_programs=max_programs,
        max_results=max_results,
    )
    budgeted_transport.begin(case_id=case_id, stage="route-refine")
    final_plan = provider._invoke(
        stage="route-refine",
        user_data={
            "schemaVersion": 1,
            "role": "builder-v10-local-portfolio-route-refiner",
            "problemId": problem_id,
            "subjectTransactionId": transaction_id,
            "routeContext": route_context,
            "acceptedClaimAssessments": copy.deepcopy(accepted_claims),
            "discoveryPlan": discovery_plan,
            "discoveryPacket": discovery_packet,
        },
        schema=route_schema,
        validate=validate_route,
        retry_feedback=lambda exc, attempt: (
            f"Trusted route refinement rejected attempt {attempt}: "
            + json.dumps(str(exc)[:1000], ensure_ascii=False)
            + ". Return the final complete route plan inside the original budget."
        ),
    )
    authoring_packet = build_research_builder_v10_authoring_packet(
        state,
        accepted_claims,
        final_plan,
        route_context=route_context,
        max_programs=max_programs,
        max_results=max_results,
    )
    records = budgeted_transport.records[record_start:]
    score = _score_route_refine_case(
        fixture, final_plan, authoring_packet, records
    )
    return {
        "schemaVersion": 1,
        "caseId": case_id,
        "phase": fixture.get("phase"),
        "sequentialGrowth": copy.deepcopy(fixture.get("sequentialGrowth")),
        "fixtureDigest": fixture.get("fixtureDigest"),
        "stateDigest": base_digest,
        "stateCounts": {
            "programs": len(state["programs"]),
            "results": len(state["intermediateResults"]),
            "contributions": len(state["contributions"]),
        },
        "routeContextDigest": route_context["contextDigest"],
        "routeContextMeasurement": measure_serialized_value(route_context),
        "discoveryPlan": discovery_plan,
        "discoveryPacketDigest": discovery_packet["authoringPacketDigest"],
        "discoveryPacketMeasurement": measure_serialized_value(discovery_packet),
        "discoveryPacketEntityDuplication": measure_packet_entity_duplication(
            discovery_packet
        ),
        "routePlan": final_plan,
        "authoringPacketDigest": authoring_packet["authoringPacketDigest"],
        "authoringPacketMeasurement": measure_serialized_value(authoring_packet),
        "authoringPacketEntityDuplication": measure_packet_entity_duplication(
            authoring_packet
        ),
        "readSet": copy.deepcopy(authoring_packet["readSet"]),
        "writeScope": copy.deepcopy(authoring_packet["writeScope"]),
        "score": score,
        "requestRecordRange": [record_start, len(budgeted_transport.records)],
        "blockedRequestRecordRange": [
            blocked_start,
            len(budgeted_transport.blocked_records),
        ],
        "authorStageInvoked": False,
        "publicationAttempted": False,
    }


def _case_plan(case: Mapping[str, object]) -> dict[str, object]:
    fixture = materialize_widening_case(case)
    state = fixture["state"]
    claims = fixture["acceptedClaims"]
    assert isinstance(state, dict)
    route_context = build_research_builder_v10_route_context(state, claims)
    challenge = fixture["activeChallenge"]
    assert isinstance(challenge, dict)
    return {
        "caseId": fixture["caseId"],
        "phase": fixture["phase"],
        "challenge": case["challenge"],
        "clueMode": fixture["clueMode"],
        "fixtureDigest": fixture["fixtureDigest"],
        "stateDigest": state["stateDigest"],
        "stateCounts": {
            "programs": len(state["programs"]),
            "results": len(state["intermediateResults"]),
            "contributions": len(state["contributions"]),
        },
        "routeContextDigest": route_context["contextDigest"],
        "routeContextMeasurement": measure_serialized_value(route_context),
        "semanticClueDigest": _digest(fixture["semanticClue"]),
        "semanticClueSurface": fixture["clueMode"],
        "sequentialGrowth": copy.deepcopy(fixture.get("sequentialGrowth")),
        "requiredProgramCount": len(challenge.get("requiredProgramIds", [])),
        "requiredResultCount": len(challenge.get("requiredResultIds", [])),
        "requiredWriteCount": len(challenge.get("requiredWriteEntityIds", [])),
    }


def plan_widening_experiment(
    manifest: Mapping[str, object], *, spec: Mapping[str, object]
) -> dict[str, object]:
    _validate_runtime_contract(manifest, spec)
    cases = manifest.get("cases")
    if not isinstance(cases, list):
        raise MathFlowError("V10 widening manifest has no cases")
    plans = [_case_plan(case) for case in cases]
    core: dict[str, object] = {
        "schemaVersion": 1,
        "experimentId": manifest.get("id"),
        "mode": "provider-free-plan",
        "publicationForbidden": True,
        "providerExecutionDefault": "disabled",
        "providerCalls": 0,
        "judgeSpecDigest": manifest.get("judgeSpecDigest"),
        "candidateJudgeSpecDigest": _digest(spec),
        "budgets": copy.deepcopy(manifest.get("budgets")),
        "cases": plans,
    }
    return {**core, "planDigest": _digest(core)}


def run_widening_experiment(
    manifest: Mapping[str, object],
    *,
    spec: Mapping[str, object],
    transport: Callable[[dict[str, object]], dict[str, object]],
) -> dict[str, object]:
    """Execute a bounded local suite.  A transport must be supplied explicitly."""

    _validate_runtime_contract(manifest, spec)
    cases = manifest.get("cases")
    if not isinstance(cases, list):
        raise MathFlowError("V10 widening manifest has no cases")
    budgets = WideningBudgets.from_mapping(manifest.get("budgets"))
    budgeted = WideningBudgetedTransport(budgets, transport=transport)
    journals: list[dict[str, object]] = []
    provider = OpenRouterResearchBuilderV10Provider(
        spec,
        transport=budgeted,
        attempt_journal_writer=lambda value: journals.append(copy.deepcopy(value)),
    )
    reports: list[dict[str, object]] = []
    status = "passed"
    failure: dict[str, object] | None = None
    for raw_case in cases:
        assert isinstance(raw_case, dict)
        case_id = str(raw_case.get("id"))
        try:
            fixture = materialize_widening_case(raw_case)
            report = run_v10_route_refine_case(
                provider=provider,
                budgeted_transport=budgeted,
                fixture=fixture,
                max_programs=int(manifest["maximumProgramsInAuthorPacket"]),
                max_results=int(manifest["maximumResultsInAuthorPacket"]),
            )
            reports.append(report)
            score = report.get("score")
            if not isinstance(score, dict) or score.get("hardPassed") is not True:
                raise MathFlowError(
                    "V10 widening case failed its hard semantic checks"
                )
        except (MathFlowError, TypeError, ValueError) as exc:
            status = "failed"
            failure = {
                "caseId": case_id,
                "class": type(exc).__name__,
                "summary": str(exc)[:1000],
                "digest": _digest(
                    {"caseId": case_id, "class": type(exc).__name__, "message": str(exc)}
                ),
            }
            break
    telemetry = budgeted.summary()
    core: dict[str, object] = {
        "schemaVersion": 1,
        "experimentId": manifest.get("id"),
        "mode": "provider-route-refine",
        "status": status,
        "publicationForbidden": True,
        "publicationAttempted": False,
        "authorStageInvocations": 0,
        "judgeSpecDigest": manifest.get("judgeSpecDigest"),
        "candidateJudgeSpecDigest": provider.spec_digest,
        "casesPlanned": len(cases),
        "casesCompleted": len(reports),
        "caseReports": reports,
        "failure": failure,
        "providerInvocations": copy.deepcopy(provider.invocation_records),
        "attemptJournals": journals,
        "telemetry": telemetry,
    }
    return {**core, "reportDigest": _digest(core)}


__all__ = [
    "WideningBudgetedTransport",
    "WideningBudgets",
    "load_bound_widening_spec",
    "load_widening_manifest",
    "materialize_widening_case",
    "measure_packet_entity_duplication",
    "plan_widening_experiment",
    "run_v10_route_refine_case",
    "run_widening_experiment",
    "validate_widening_manifest",
]
