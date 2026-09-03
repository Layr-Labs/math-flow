"""Fail-closed hosted runner for the unpublished BSSC K1->K3 holdout.

The runner adds execution authority and transport budgets around the existing
provider-neutral holdout.  It cannot publish, continue, select another subject,
or alter the fixed route.  A request-side OpenRouter ``max_price`` filter is
injected immediately before network dispatch and recorded separately from the
semantic judge request digest.
"""

from __future__ import annotations

import copy
import json
import math
from collections.abc import Mapping
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from pathlib import Path, PurePosixPath

from .artifacts import file_digest
from .errors import MathFlowError
from .governed_providers import GovernedProviderTerminalError
from .joint_portfolio_serial_credit_v2 import (
    OpenRouterJointPortfolioSerialCreditV2Provider,
)
from .joint_portfolio_serial_holdout import (
    SUBJECTS,
    run_bssc_joint_portfolio_serial_holdout_v1,
)
from .joint_portfolio_serial_provider_v2 import (
    OpenRouterJointPortfolioSerialAuthorV2Provider,
)
from .openrouter import OpenRouterTransport, send_chat_completion
from .repository import sha256_json


DEFAULT_MANIFEST = PurePosixPath(
    "protocol/experiments/bssc-joint-portfolio-serial-k1-k3-v1/hosted-runner-v1.json"
)
STAGE_ORDER = ("joint-author", "safe-facts", "no-access")
MANIFEST_FIELDS = {
    "schemaVersion",
    "id",
    "description",
    "status",
    "publicationForbidden",
    "continue",
    "providerExecutionDefault",
    "stopOnFirstHardFailure",
    "holdoutManifest",
    "holdoutManifestFileDigest",
    "jointAuthorJudgeSpec",
    "jointAuthorJudgeSpecFileDigest",
    "jointAuthorJudgeSpecDigest",
    "workJudgeSpec",
    "workJudgeSpecFileDigest",
    "workJudgeSpecDigest",
    "model",
    "subjects",
    "stageOrder",
    "nominalProviderCalls",
    "maximumAttemptsPerStage",
    "authorizationEnvironmentVariable",
    "authorizationValue",
    "budgets",
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
    "requestPriceCeilingUsdPerMillionTokens",
}
PRICE_FIELDS = {"prompt", "completion"}


def _digest(value: object) -> str:
    try:
        return f"sha256:{sha256_json(copy.deepcopy(value))}"
    except (TypeError, ValueError) as exc:
        raise MathFlowError("joint hosted-runner data must be canonical JSON") from exc


def _positive_integer(value: object, label: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 1:
        raise MathFlowError(f"joint hosted-runner {label} must be a positive integer")
    return value


def _decimal(value: object, label: str, *, positive: bool = True) -> Decimal:
    if isinstance(value, bool) or not isinstance(value, (int, float, str)):
        raise MathFlowError(f"joint hosted-runner {label} must be a decimal")
    try:
        result = Decimal(str(value))
    except InvalidOperation as exc:
        raise MathFlowError(f"joint hosted-runner {label} must be a decimal") from exc
    if not result.is_finite() or (result <= 0 if positive else result < 0):
        qualifier = "positive" if positive else "nonnegative"
        raise MathFlowError(f"joint hosted-runner {label} must be {qualifier}")
    return result


def _safe_file(root: Path, value: object, label: str) -> Path:
    if not isinstance(value, str) or not value:
        raise MathFlowError(f"joint hosted-runner {label} is invalid")
    relative = PurePosixPath(value)
    if relative.is_absolute() or ".." in relative.parts:
        raise MathFlowError(f"joint hosted-runner {label} path is unsafe")
    repository = root.resolve()
    target = repository.joinpath(*relative.parts)
    cursor = repository
    for part in relative.parts:
        cursor = cursor / part
        if cursor.is_symlink():
            raise MathFlowError(f"joint hosted-runner {label} may not traverse a symlink")
    resolved = target.resolve()
    try:
        resolved.relative_to(repository)
    except ValueError as exc:
        raise MathFlowError(f"joint hosted-runner {label} escapes the repository") from exc
    if not resolved.is_file():
        raise MathFlowError(f"joint hosted-runner {label} is missing")
    return resolved


def _load_json(path: Path, label: str) -> dict[str, object]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise MathFlowError(f"joint hosted-runner {label} is unreadable") from exc
    if not isinstance(value, dict):
        raise MathFlowError(f"joint hosted-runner {label} must be an object")
    return value


@dataclass(frozen=True)
class JointHostedBudgets:
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
    prompt_price_usd_per_million_tokens: Decimal
    completion_price_usd_per_million_tokens: Decimal

    @classmethod
    def from_mapping(cls, value: object) -> "JointHostedBudgets":
        if not isinstance(value, dict) or set(value) != BUDGET_FIELDS:
            raise MathFlowError("joint hosted-runner budgets have invalid fields")
        prices = value.get("requestPriceCeilingUsdPerMillionTokens")
        if not isinstance(prices, dict) or set(prices) != PRICE_FIELDS:
            raise MathFlowError("joint hosted-runner request price ceiling is invalid")
        result = cls(
            maximum_provider_calls=_positive_integer(
                value["maximumProviderCalls"], "maximumProviderCalls"
            ),
            maximum_request_bytes=_positive_integer(
                value["maximumRequestBytes"], "maximumRequestBytes"
            ),
            maximum_estimated_prompt_tokens=_positive_integer(
                value["maximumEstimatedPromptTokens"],
                "maximumEstimatedPromptTokens",
            ),
            maximum_conservative_prompt_tokens=_positive_integer(
                value["maximumConservativePromptTokens"],
                "maximumConservativePromptTokens",
            ),
            prompt_token_overhead_reservation=_positive_integer(
                value["promptTokenOverheadReservation"],
                "promptTokenOverheadReservation",
            ),
            maximum_completion_tokens_per_call=_positive_integer(
                value["maximumCompletionTokensPerCall"],
                "maximumCompletionTokensPerCall",
            ),
            maximum_total_reserved_tokens=_positive_integer(
                value["maximumTotalReservedTokens"],
                "maximumTotalReservedTokens",
            ),
            maximum_total_reported_tokens=_positive_integer(
                value["maximumTotalReportedTokens"],
                "maximumTotalReportedTokens",
            ),
            maximum_single_call_cost_usd=_decimal(
                value["maximumSingleCallCostUsd"], "maximumSingleCallCostUsd"
            ),
            maximum_total_cost_usd=_decimal(
                value["maximumTotalCostUsd"], "maximumTotalCostUsd"
            ),
            prompt_price_usd_per_million_tokens=_decimal(
                prices["prompt"], "prompt price ceiling"
            ),
            completion_price_usd_per_million_tokens=_decimal(
                prices["completion"], "completion price ceiling"
            ),
        )
        minimum_conservative = (
            result.maximum_request_bytes + result.prompt_token_overhead_reservation
        )
        if result.maximum_conservative_prompt_tokens < minimum_conservative:
            raise MathFlowError(
                "joint hosted-runner conservative prompt ceiling cannot cover "
                "the request-byte reservation"
            )
        if (
            math.ceil(result.maximum_request_bytes / 4)
            > result.maximum_estimated_prompt_tokens
        ):
            raise MathFlowError(
                "joint hosted-runner estimated prompt ceiling cannot cover "
                "the request-byte ceiling"
            )
        maximum_call_cost = (
            Decimal(result.maximum_conservative_prompt_tokens)
            * result.prompt_price_usd_per_million_tokens
            + Decimal(result.maximum_completion_tokens_per_call)
            * result.completion_price_usd_per_million_tokens
        ) / Decimal(1_000_000)
        if result.maximum_single_call_cost_usd < maximum_call_cost:
            raise MathFlowError(
                "joint hosted-runner single-call cost ceiling cannot cover "
                "the request-side price reservation"
            )
        if (
            result.maximum_total_reserved_tokens
            < result.maximum_conservative_prompt_tokens
            + result.maximum_completion_tokens_per_call
            or result.maximum_total_reported_tokens
            > result.maximum_total_reserved_tokens
            or result.maximum_total_cost_usd < result.maximum_single_call_cost_usd
        ):
            raise MathFlowError("joint hosted-runner cumulative budgets are inconsistent")
        return result

    @property
    def price_filter(self) -> dict[str, float]:
        return {
            "prompt": float(self.prompt_price_usd_per_million_tokens),
            "completion": float(self.completion_price_usd_per_million_tokens),
        }


def load_joint_hosted_manifest(
    path: Path | None = None, *, repository_root: Path
) -> dict[str, object]:
    root = repository_root.resolve()
    manifest_path = (
        root.joinpath(*DEFAULT_MANIFEST.parts)
        if path is None
        else (path if path.is_absolute() else root / path)
    )
    manifest_path = manifest_path.resolve()
    try:
        manifest_path.relative_to(root)
    except ValueError as exc:
        raise MathFlowError("joint hosted-runner manifest escapes the repository") from exc
    manifest = _load_json(manifest_path, "manifest")
    if set(manifest) != MANIFEST_FIELDS:
        raise MathFlowError("joint hosted-runner manifest has invalid fields")
    if (
        manifest.get("schemaVersion") != 1
        or manifest.get("status") != "unpublished-experiment"
        or manifest.get("publicationForbidden") is not True
        or manifest.get("continue") is not False
        or manifest.get("providerExecutionDefault") != "disabled"
        or manifest.get("stopOnFirstHardFailure") is not True
        or manifest.get("subjects") != list(SUBJECTS)
        or manifest.get("stageOrder") != list(STAGE_ORDER)
        or manifest.get("nominalProviderCalls") != len(SUBJECTS) * len(STAGE_ORDER)
    ):
        raise MathFlowError(
            "joint hosted-runner must remain fixed, unpublished, disabled, and fail-fast"
        )
    for field in (
        "id",
        "description",
        "model",
        "authorizationEnvironmentVariable",
        "authorizationValue",
    ):
        if not isinstance(manifest.get(field), str) or not str(manifest[field]).strip():
            raise MathFlowError(f"joint hosted-runner manifest {field} is invalid")
    attempts = _positive_integer(
        manifest.get("maximumAttemptsPerStage"), "maximumAttemptsPerStage"
    )
    budgets = JointHostedBudgets.from_mapping(manifest.get("budgets"))
    if budgets.maximum_provider_calls != int(manifest["nominalProviderCalls"]) * attempts:
        raise MathFlowError(
            "joint hosted-runner call budget must reserve every governed stage attempt"
        )

    loaded: dict[str, dict[str, object]] = {}
    for prefix in ("holdoutManifest", "jointAuthorJudgeSpec", "workJudgeSpec"):
        target = _safe_file(root, manifest[prefix], prefix)
        if file_digest(target) != manifest[f"{prefix}FileDigest"]:
            raise MathFlowError(f"joint hosted-runner {prefix} file binding mismatch")
        loaded[prefix] = _load_json(target, prefix)
    holdout = loaded["holdoutManifest"]
    if (
        holdout.get("publicationForbidden") is not True
        or holdout.get("continue") is not False
        or holdout.get("subjects") != list(SUBJECTS)
        or holdout.get("jointAuthorJudgeSpecDigest")
        != manifest.get("jointAuthorJudgeSpecDigest")
        or holdout.get("workJudgeSpecDigest") != manifest.get("workJudgeSpecDigest")
    ):
        raise MathFlowError("joint hosted-runner holdout binding is incompatible")
    for prefix in ("jointAuthorJudgeSpec", "workJudgeSpec"):
        spec = loaded[prefix]
        if (
            _digest(spec) != manifest[f"{prefix}Digest"]
            or spec.get("model") != manifest.get("model")
        ):
            raise MathFlowError(f"joint hosted-runner {prefix} semantic binding mismatch")
        retry = spec.get("retryPolicy")
        if not isinstance(retry, dict) or retry.get("maximumAttempts") != attempts:
            raise MathFlowError(f"joint hosted-runner {prefix} retry binding mismatch")
    author_stages = loaded["jointAuthorJudgeSpec"].get("stages")
    work_stages = loaded["workJudgeSpec"].get("stages")
    expected_stage_specs = {
        "joint-author": author_stages.get("joint-author")
        if isinstance(author_stages, dict)
        else None,
        "safe-facts": work_stages.get("safe-facts")
        if isinstance(work_stages, dict)
        else None,
        "no-access": work_stages.get("no-access")
        if isinstance(work_stages, dict)
        else None,
    }
    for stage, raw in expected_stage_specs.items():
        parameters = raw.get("parameters") if isinstance(raw, dict) else None
        maximum = parameters.get("max_tokens") if isinstance(parameters, dict) else None
        if (
            isinstance(maximum, bool)
            or not isinstance(maximum, int)
            or maximum < 1
            or maximum > budgets.maximum_completion_tokens_per_call
        ):
            raise MathFlowError(f"joint hosted-runner {stage} token binding is invalid")
    return copy.deepcopy(manifest)


def build_joint_hosted_plan(manifest: Mapping[str, object]) -> dict[str, object]:
    sequence = [
        {
            "ordinal": index + 1,
            "subjectTransactionId": subject,
            "stage": stage,
            "maximumAttempts": manifest["maximumAttemptsPerStage"],
        }
        for index, (subject, stage) in enumerate(
            (subject, stage) for subject in SUBJECTS for stage in STAGE_ORDER
        )
    ]
    core = {
        "schemaVersion": 1,
        "experimentId": manifest["id"],
        "status": "provider-free-plan",
        "publicationForbidden": True,
        "continue": False,
        "providerExecutionDefault": "disabled",
        "providerCallsAuthorized": 0,
        "nominalProviderCalls": manifest["nominalProviderCalls"],
        "maximumProviderCalls": manifest["budgets"]["maximumProviderCalls"],
        "requestSidePriceFilter": copy.deepcopy(
            manifest["budgets"]["requestPriceCeilingUsdPerMillionTokens"]
        ),
        "subjects": list(SUBJECTS),
        "serialStagePlan": sequence,
        "budgets": copy.deepcopy(manifest["budgets"]),
    }
    return {**core, "planDigest": _digest(core)}


class JointHoldoutBudgetedTransport:
    """Apply exact serial, request, token, price, and cost stops before dispatch."""

    def __init__(
        self,
        *,
        manifest: Mapping[str, object],
        author_spec: Mapping[str, object],
        work_spec: Mapping[str, object],
        transport: OpenRouterTransport,
    ) -> None:
        self.manifest = copy.deepcopy(dict(manifest))
        self.budgets = JointHostedBudgets.from_mapping(manifest.get("budgets"))
        self.transport = transport
        self.expected = [
            (subject, stage) for subject in SUBJECTS for stage in STAGE_ORDER
        ]
        self.maximum_attempts = int(manifest["maximumAttemptsPerStage"])
        self.stage_prompts = {
            "joint-author": author_spec["stagePrompts"]["joint-author"],
            "safe-facts": work_spec["stagePrompts"]["safe-facts"],
            "no-access": work_spec["stagePrompts"]["no-access"],
        }
        self.model = str(manifest["model"])
        self.records: list[dict[str, object]] = []
        self.blocked_records: list[dict[str, object]] = []
        self.blocked_reason: str | None = None
        self.sequence_index = -1
        self.stage_attempt = 0
        self.reserved_tokens = 0
        self.reported_tokens = 0
        self.reserved_cost_usd = Decimal("0")
        self.reported_cost_usd = Decimal("0")
        self.latest_identity: tuple[str, str] | None = None

    def _block(self, reason: str, record: dict[str, object] | None = None) -> None:
        self.blocked_reason = reason
        if record is not None:
            blocked = copy.deepcopy(record)
            blocked["outcome"] = "blocked-before-provider"
            blocked["blockedReason"] = reason
            self.blocked_records.append(blocked)
        raise GovernedProviderTerminalError(reason)

    def _identity(self, request: Mapping[str, object]) -> tuple[str, str]:
        if request.get("model") != self.model:
            raise MathFlowError("joint hosted-runner request changed the pinned model")
        messages = request.get("messages")
        if not isinstance(messages, list):
            raise MathFlowError("joint hosted-runner request has no messages")
        prompt_matches = [
            stage
            for stage, prompt in self.stage_prompts.items()
            if any(
                isinstance(message, dict)
                and message.get("role") == "system"
                and message.get("content") == prompt
                for message in messages
            )
        ]
        if len(prompt_matches) != 1:
            raise MathFlowError("joint hosted-runner stage prompt is not exact")
        prefix = "<math-flow-input>\n"
        suffix = "\n</math-flow-input>"
        quoted: dict[str, object] | None = None
        for message in messages:
            content = message.get("content") if isinstance(message, dict) else None
            if not isinstance(content, str) or prefix not in content:
                continue
            raw = content.split(prefix, 1)[1]
            if not raw.endswith(suffix):
                raise MathFlowError("joint hosted-runner quoted input is malformed")
            value = json.loads(raw[: -len(suffix)])
            if not isinstance(value, dict):
                raise MathFlowError("joint hosted-runner quoted input is invalid")
            quoted = value
            break
        if quoted is None:
            raise MathFlowError("joint hosted-runner request lacks quoted input")
        stage = prompt_matches[0]
        if stage == "joint-author":
            subject = quoted.get("subjectTransactionId")
            declared_stage = quoted.get("stage")
        else:
            nested = quoted.get("request")
            if not isinstance(nested, dict):
                raise MathFlowError("joint hosted-runner work input is invalid")
            subject = nested.get("subjectTransactionId")
            declared_stage = nested.get("stage")
        if declared_stage != stage or subject not in SUBJECTS:
            raise MathFlowError("joint hosted-runner request identity is outside the holdout")
        return str(subject), stage

    def _advance(self, identity: tuple[str, str], record: dict[str, object]) -> None:
        if self.sequence_index >= 0 and identity == self.expected[self.sequence_index]:
            self.stage_attempt += 1
        elif (
            self.sequence_index + 1 < len(self.expected)
            and identity == self.expected[self.sequence_index + 1]
        ):
            self.sequence_index += 1
            self.stage_attempt = 1
        else:
            self._block("joint hosted-runner provider stage is reordered or skipped", record)
        if self.stage_attempt > self.maximum_attempts:
            self._block("joint hosted-runner per-stage attempt budget exhausted", record)

    def __call__(self, request: dict[str, object]) -> dict[str, object]:
        try:
            identity = self._identity(request)
        except (MathFlowError, TypeError, ValueError, json.JSONDecodeError) as exc:
            self._block(str(exc))
        self.latest_identity = identity
        compact = json.dumps(
            request, sort_keys=True, separators=(",", ":"), ensure_ascii=False
        ).encode("utf-8")
        request_bytes = len(compact)
        estimated_prompt = math.ceil(request_bytes / 4)
        conservative_prompt = (
            request_bytes + self.budgets.prompt_token_overhead_reservation
        )
        maximum_completion = request.get("max_tokens")
        record: dict[str, object] = {
            "schemaVersion": 1,
            "subjectTransactionId": identity[0],
            "stage": identity[1],
            "requestDigest": _digest(request),
            "requestBytes": request_bytes,
            "estimatedPromptTokens": estimated_prompt,
            "conservativePromptTokenReservation": conservative_prompt,
            "maximumCompletionTokenReservation": maximum_completion,
        }
        if self.blocked_reason is not None:
            self._block(self.blocked_reason, record)
        self._advance(identity, record)
        record["stageAttempt"] = self.stage_attempt
        if len(self.records) >= self.budgets.maximum_provider_calls:
            self._block("joint hosted-runner provider-call budget exhausted", record)
        if request_bytes > self.budgets.maximum_request_bytes:
            self._block("joint hosted-runner request-byte budget exhausted", record)
        if estimated_prompt > self.budgets.maximum_estimated_prompt_tokens:
            self._block("joint hosted-runner estimated prompt-token budget exhausted", record)
        if conservative_prompt > self.budgets.maximum_conservative_prompt_tokens:
            self._block("joint hosted-runner conservative prompt-token budget exhausted", record)
        if (
            isinstance(maximum_completion, bool)
            or not isinstance(maximum_completion, int)
            or maximum_completion < 1
            or maximum_completion > self.budgets.maximum_completion_tokens_per_call
        ):
            self._block("joint hosted-runner completion-token reservation is invalid", record)
        token_reservation = conservative_prompt + maximum_completion
        cost_reservation = (
            Decimal(conservative_prompt)
            * self.budgets.prompt_price_usd_per_million_tokens
            + Decimal(maximum_completion)
            * self.budgets.completion_price_usd_per_million_tokens
        ) / Decimal(1_000_000)
        if token_reservation + self.reserved_tokens > self.budgets.maximum_total_reserved_tokens:
            self._block("joint hosted-runner total token reservation exhausted", record)
        if cost_reservation > self.budgets.maximum_single_call_cost_usd:
            self._block("joint hosted-runner single-call cost reservation exhausted", record)
        if cost_reservation + self.reserved_cost_usd > self.budgets.maximum_total_cost_usd:
            self._block("joint hosted-runner total cost reservation exhausted", record)

        effective = copy.deepcopy(request)
        provider = effective.get("provider")
        if not isinstance(provider, dict) or "max_price" in provider:
            self._block("joint hosted-runner provider routing contract is invalid", record)
        effective["provider"] = {
            **provider,
            "max_price": self.budgets.price_filter,
        }
        record["effectiveRequestDigest"] = _digest(effective)
        record["requestPriceCeilingUsdPerMillionTokens"] = self.budgets.price_filter
        self.reserved_tokens += token_reservation
        self.reserved_cost_usd += cost_reservation
        record["providerCallIndex"] = len(self.records) + 1
        record["callReservedTokens"] = token_reservation
        record["callReservedCostUsd"] = float(cost_reservation)
        record["cumulativeReservedTokens"] = self.reserved_tokens
        record["cumulativeReservedCostUsd"] = float(self.reserved_cost_usd)
        try:
            response = self.transport(copy.deepcopy(effective))
        except Exception as exc:
            record["outcome"] = "transport-uncertain"
            self.records.append(record)
            self.blocked_reason = (
                "joint hosted-runner transport outcome is uncertain; later calls are blocked"
            )
            raise GovernedProviderTerminalError(self.blocked_reason) from exc
        if not isinstance(response, dict):
            record["outcome"] = "invalid-provider-response"
            self.records.append(record)
            self.blocked_reason = "joint hosted-runner provider returned a non-object"
            raise GovernedProviderTerminalError(self.blocked_reason)
        record["rawResponse"] = copy.deepcopy(response)
        record["responseDigest"] = _digest(response)
        usage = response.get("usage")
        if not isinstance(usage, dict):
            record["outcome"] = "invalid-provider-telemetry"
            self.records.append(record)
            self.blocked_reason = "joint hosted-runner response omitted usage telemetry"
            raise GovernedProviderTerminalError(self.blocked_reason)
        tokens: dict[str, int] = {}
        for field in ("prompt_tokens", "completion_tokens", "total_tokens"):
            value = usage.get(field)
            if isinstance(value, bool) or not isinstance(value, int) or value < 0:
                record["outcome"] = "invalid-provider-telemetry"
                self.records.append(record)
                self.blocked_reason = "joint hosted-runner response token telemetry is invalid"
                raise GovernedProviderTerminalError(self.blocked_reason)
            tokens[field] = value
        if tokens["total_tokens"] != tokens["prompt_tokens"] + tokens["completion_tokens"]:
            record["outcome"] = "invalid-provider-telemetry"
            self.records.append(record)
            self.blocked_reason = "joint hosted-runner token telemetry is inconsistent"
            raise GovernedProviderTerminalError(self.blocked_reason)
        cost = _decimal(usage.get("cost"), "reported provider cost", positive=False)
        self.reported_tokens += tokens["total_tokens"]
        self.reported_cost_usd += cost
        record["usage"] = {
            "promptTokens": tokens["prompt_tokens"],
            "completionTokens": tokens["completion_tokens"],
            "totalTokens": tokens["total_tokens"],
            "costUsd": float(cost),
        }
        record["resolvedModel"] = response.get("model")
        record["cumulativeReportedTokens"] = self.reported_tokens
        record["cumulativeReportedCostUsd"] = float(self.reported_cost_usd)
        violations: list[str] = []
        if tokens["prompt_tokens"] > conservative_prompt:
            violations.append("reported prompt tokens exceed reservation")
        if tokens["completion_tokens"] > maximum_completion:
            violations.append("reported completion tokens exceed reservation")
        if tokens["total_tokens"] > token_reservation:
            violations.append("reported total tokens exceed reservation")
        if self.reported_tokens > self.budgets.maximum_total_reported_tokens:
            violations.append("reported total-token budget exhausted")
        if cost > cost_reservation:
            violations.append("reported cost exceeds request-side reservation")
        if self.reported_cost_usd > self.budgets.maximum_total_cost_usd:
            violations.append("reported total-cost budget exhausted")
        if violations:
            record["outcome"] = "hard-budget-violation"
            record["blockedReason"] = "; ".join(violations)
            self.records.append(record)
            self.blocked_reason = "joint hosted-runner hard budget violation: " + "; ".join(violations)
            raise GovernedProviderTerminalError(self.blocked_reason)
        record["outcome"] = "provider-response-recorded"
        self.records.append(record)
        return copy.deepcopy(response)

    def finalize_success(self) -> None:
        if self.sequence_index != len(self.expected) - 1:
            raise MathFlowError("joint hosted-runner did not execute the complete fixed stage chain")
        observed = {
            (str(record["subjectTransactionId"]), str(record["stage"]))
            for record in self.records
        }
        if observed != set(self.expected) or self.blocked_reason is not None:
            raise MathFlowError("joint hosted-runner fixed stage coverage is invalid")

    def summary(self) -> dict[str, object]:
        return {
            "schemaVersion": 1,
            "providerCalls": len(self.records),
            "blockedAttempts": len(self.blocked_records),
            "reservedTokens": self.reserved_tokens,
            "reportedTokens": self.reported_tokens,
            "reservedCostUsd": float(self.reserved_cost_usd),
            "reportedCostUsd": float(self.reported_cost_usd),
            "blockedReason": self.blocked_reason,
            "requestRecords": copy.deepcopy(self.records),
            "blockedRequestRecords": copy.deepcopy(self.blocked_records),
        }


class _AttemptJournalWriter:
    def __init__(
        self, directory: Path, *, role: str, budgeted: JointHoldoutBudgetedTransport
    ) -> None:
        self.directory = directory.resolve()
        self.directory.mkdir(parents=True, exist_ok=True)
        self.role = role
        self.budgeted = budgeted
        self.count = 0

    def __call__(self, journal: dict[str, object]) -> None:
        self.count += 1
        identity = self.budgeted.latest_identity
        core = {
            "schemaVersion": 1,
            "role": self.role,
            "subjectTransactionId": identity[0] if identity else None,
            "stage": identity[1] if identity else journal.get("stage"),
            "journal": copy.deepcopy(journal),
        }
        path = self.directory / f"{self.role}-{self.count:04d}.json"
        temporary = path.with_suffix(".tmp")
        temporary.write_text(
            json.dumps(core, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
        temporary.replace(path)


def run_joint_hosted_holdout(
    *,
    repository_root: Path,
    manifest: Mapping[str, object],
    bundle_dir: Path,
    checkpoint_dir: Path,
    authorization: str,
    transport: OpenRouterTransport = send_chat_completion,
) -> dict[str, object]:
    """Execute exactly one fresh, publication-forbidden K1->K3 semantic sample."""

    root = repository_root.resolve()
    canonical_manifest = load_joint_hosted_manifest(repository_root=root)
    if copy.deepcopy(dict(manifest)) != canonical_manifest:
        raise MathFlowError(
            "joint hosted-runner execution manifest is not the canonical bound file"
        )
    if authorization != manifest.get("authorizationValue"):
        raise MathFlowError("joint hosted-runner provider authorization is not exact")
    bundle = bundle_dir.resolve()
    checkpoints = checkpoint_dir.resolve()
    if bundle.exists() or checkpoints.exists():
        raise MathFlowError(
            "joint hosted-runner requires new bundle and checkpoint directories"
        )
    author_path = _safe_file(root, manifest["jointAuthorJudgeSpec"], "author judge")
    work_path = _safe_file(root, manifest["workJudgeSpec"], "work judge")
    author_spec = _load_json(author_path, "author judge")
    work_spec = _load_json(work_path, "work judge")
    budgeted = JointHoldoutBudgetedTransport(
        manifest=manifest,
        author_spec=author_spec,
        work_spec=work_spec,
        transport=transport,
    )
    journal_root = checkpoints / "attempt-journals"
    author_writer = _AttemptJournalWriter(
        journal_root, role="joint-author", budgeted=budgeted
    )
    credit_writer = _AttemptJournalWriter(
        journal_root, role="joint-credit", budgeted=budgeted
    )
    author = OpenRouterJointPortfolioSerialAuthorV2Provider(
        author_spec,
        transport=budgeted,
        attempt_journal_writer=author_writer,
    )
    credit = OpenRouterJointPortfolioSerialCreditV2Provider(
        work_spec,
        transport=budgeted,
        attempt_journal_writer=credit_writer,
    )
    status = "completed"
    failure: dict[str, object] | None = None
    loaded: dict[str, object] | None = None
    try:
        loaded = run_bssc_joint_portfolio_serial_holdout_v1(
            root=root,
            output_dir=bundle,
            checkpoint_dir=checkpoints / "holdout",
            joint_author_provider=author,
            credit_provider=credit,
            continue_run=False,
            publish=False,
        )
        budgeted.finalize_success()
    except Exception as exc:  # noqa: BLE001 - retained semantic experiment failure
        status = "failed"
        failure_core = {
            "class": type(exc).__name__,
            "summary": str(exc)[:2000],
        }
        failure = {**failure_core, "failureDigest": _digest(failure_core)}
    telemetry = budgeted.summary()
    core: dict[str, object] = {
        "schemaVersion": 1,
        "experimentId": manifest["id"],
        "status": status,
        "publicationForbidden": True,
        "publicationAttempted": False,
        "continue": False,
        "subjects": list(SUBJECTS),
        "nominalProviderCalls": manifest["nominalProviderCalls"],
        "bundleDigest": loaded["bundleDigest"] if loaded is not None else None,
        "terminalKnowledgeStateDigest": (
            loaded["terminalKnowledgeState"]["stateDigest"]
            if loaded is not None
            else None
        ),
        "terminalAccountingStateDigest": (
            loaded["terminalAccountingState"]["stateDigest"]
            if loaded is not None
            else None
        ),
        "terminalBoundaryStateDigest": (
            loaded["terminalBoundaryState"]["stateDigest"]
            if loaded is not None
            else None
        ),
        "authorInvocations": copy.deepcopy(author.invocation_records),
        "creditInvocations": copy.deepcopy(credit.invocation_records),
        "attemptJournalFiles": author_writer.count + credit_writer.count,
        "telemetry": telemetry,
        "failure": failure,
    }
    return {**core, "reportDigest": _digest(core)}


__all__ = [
    "DEFAULT_MANIFEST",
    "JointHoldoutBudgetedTransport",
    "JointHostedBudgets",
    "build_joint_hosted_plan",
    "load_joint_hosted_manifest",
    "run_joint_hosted_holdout",
]
