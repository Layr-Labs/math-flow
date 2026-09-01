from __future__ import annotations

import copy
import json
import math
import re
from dataclasses import dataclass
from decimal import Decimal
from pathlib import Path, PurePosixPath
from typing import Mapping, Sequence

from . import __version__
from .artifacts import ArtifactBundle, sha256_bytes
from .errors import MathFlowError
from .repository import validate_slug


_DIGEST = re.compile(r"^sha256:[0-9a-f]{64}$")
_LEDGER_HEAD = re.compile(r"^[0-9a-f]{40}$")
_STAGE_ADAPTERS = {"fixture-replay-v1"}
_SCORERS = {"json-relational-v1"}
_ATTEMPT_STATUSES = {"retry", "accepted", "failed"}
_SEVERITIES = {"hard", "advisory"}
_BUDGET_FIELDS = (
    "maximumProviderCalls",
    "maximumStageAttempts",
    "maximumPromptTokens",
    "maximumCompletionTokens",
    "maximumTotalTokens",
    "maximumCostUsd",
)


@dataclass(frozen=True)
class ScenarioArtifact:
    value: object
    digest: str
    media_type: str


@dataclass(frozen=True)
class PreparedFixture:
    path: Path
    raw: bytes
    value: dict[str, object]
    attempts: tuple[dict[str, object], ...]
    telemetry: tuple[dict[str, object], ...]
    outputs: tuple[tuple[str, ScenarioArtifact, bytes | None], ...]


def _json_bytes(value: object) -> bytes:
    return (json.dumps(value, indent=2, ensure_ascii=False) + "\n").encode("utf-8")


def _require_mapping(value: object, label: str) -> dict[str, object]:
    if not isinstance(value, dict):
        raise MathFlowError(f"{label} must be an object")
    return value


def _require_list(value: object, label: str) -> list[object]:
    if not isinstance(value, list):
        raise MathFlowError(f"{label} must be an array")
    return value


def _require_string(value: object, label: str) -> str:
    if not isinstance(value, str) or not value:
        raise MathFlowError(f"{label} must be a nonempty string")
    return value


def _require_bool(value: object, label: str) -> bool:
    if not isinstance(value, bool):
        raise MathFlowError(f"{label} must be a boolean")
    return value


def _require_nonnegative_int(value: object, label: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise MathFlowError(f"{label} must be a nonnegative integer")
    return value


def _require_nonnegative_decimal(value: object, label: str) -> Decimal:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise MathFlowError(f"{label} must be a nonnegative number")
    if isinstance(value, float) and not math.isfinite(value):
        raise MathFlowError(f"{label} must be finite")
    result = Decimal(str(value))
    if result < 0:
        raise MathFlowError(f"{label} must be nonnegative")
    return result


def _check_digest(value: object, label: str) -> str:
    digest = _require_string(value, label)
    if not _DIGEST.fullmatch(digest):
        raise MathFlowError(f"{label} must be a sha256 digest")
    return digest


def _check_identifier(value: object, label: str) -> str:
    identifier = _require_string(value, label)
    validate_slug(identifier, label)
    return identifier


def _safe_repo_file(root: Path, raw_path: object, label: str) -> Path:
    relative = PurePosixPath(_require_string(raw_path, label))
    if relative.is_absolute() or ".." in relative.parts or not relative.parts:
        raise MathFlowError(f"{label} must be a repository-relative path")
    root = root.resolve()
    target = root.joinpath(*relative.parts)
    cursor = root
    for part in relative.parts:
        cursor = cursor / part
        if cursor.is_symlink():
            raise MathFlowError(f"{label} may not traverse a symlink: {relative}")
    resolved = target.resolve()
    try:
        resolved.relative_to(root)
    except ValueError as exc:
        raise MathFlowError(f"{label} escapes the repository: {relative}") from exc
    if not resolved.is_file():
        raise MathFlowError(f"{label} does not exist: {relative}")
    return resolved


def _load_json_bytes(raw: bytes, label: str) -> object:
    try:
        return json.loads(raw)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise MathFlowError(f"{label} is not valid UTF-8 JSON: {exc}") from exc


def _load_bound_file(
    root: Path,
    path_value: object,
    digest_value: object,
    label: str,
) -> tuple[Path, bytes]:
    path = _safe_repo_file(root, path_value, f"{label} path")
    raw = path.read_bytes()
    expected = _check_digest(digest_value, f"{label} digest")
    actual = sha256_bytes(raw)
    if actual != expected:
        raise MathFlowError(
            f"{label} digest mismatch: expected {expected}, observed {actual}"
        )
    return path, raw


def _validate_budgets(value: object) -> dict[str, object]:
    budgets = _require_mapping(value, "scenario budgets")
    missing = [key for key in _BUDGET_FIELDS if key not in budgets]
    extras = sorted(set(budgets) - set(_BUDGET_FIELDS))
    if missing or extras:
        detail = []
        if missing:
            detail.append(f"missing {', '.join(missing)}")
        if extras:
            detail.append(f"unknown {', '.join(extras)}")
        raise MathFlowError("scenario budgets are invalid: " + "; ".join(detail))
    normalized = {
        key: _require_nonnegative_int(budgets[key], f"scenario budget {key}")
        for key in _BUDGET_FIELDS[:-1]
    }
    normalized["maximumCostUsd"] = float(
        _require_nonnegative_decimal(
            budgets["maximumCostUsd"], "scenario budget maximumCostUsd"
        )
    )
    return normalized


def validate_teacher_student_scenario_manifest(
    root: Path, manifest_path: Path
) -> tuple[dict[str, object], bytes, str]:
    root = root.resolve()
    path = manifest_path if manifest_path.is_absolute() else root / manifest_path
    path = path.resolve()
    try:
        path.relative_to(root)
    except ValueError as exc:
        raise MathFlowError("scenario manifest must be inside the repository") from exc
    relative_manifest = path.relative_to(root)
    cursor = root
    for part in relative_manifest.parts:
        cursor = cursor / part
        if cursor.is_symlink():
            raise MathFlowError("scenario manifest may not traverse a symlink")
    if not path.is_file():
        raise MathFlowError(f"scenario manifest is not a regular file: {path}")
    raw = path.read_bytes()
    manifest = _require_mapping(_load_json_bytes(raw, "scenario manifest"), "scenario manifest")
    allowed = {
        "schemaVersion",
        "id",
        "description",
        "problemId",
        "ledgerHead",
        "publicationForbidden",
        "execution",
        "variants",
        "seeds",
        "budgets",
        "frozenInputs",
        "steps",
        "scorers",
    }
    extras = sorted(set(manifest) - allowed)
    if extras:
        raise MathFlowError(f"scenario manifest contains unknown field: {extras[0]}")
    if manifest.get("schemaVersion") != 1:
        raise MathFlowError("scenario manifest schemaVersion must be 1")
    _check_identifier(manifest.get("id"), "scenario id")
    _require_string(manifest.get("description"), "scenario description")
    _check_identifier(manifest.get("problemId"), "scenario problem id")
    ledger_head = _require_string(manifest.get("ledgerHead"), "scenario ledger head")
    if not _LEDGER_HEAD.fullmatch(ledger_head):
        raise MathFlowError("scenario ledgerHead must be a full 40-character commit")
    if _require_bool(
        manifest.get("publicationForbidden"), "scenario publicationForbidden"
    ) is not True:
        raise MathFlowError("teacher-student scenarios must forbid publication")
    execution = _require_mapping(manifest.get("execution"), "scenario execution")
    if execution != {"adapter": "fixture-replay-v1"}:
        raise MathFlowError(
            "provider-free scenario execution must use only fixture-replay-v1"
        )
    manifest["budgets"] = _validate_budgets(manifest.get("budgets"))

    variants = _require_list(manifest.get("variants"), "scenario variants")
    if not variants:
        raise MathFlowError("scenario variants may not be empty")
    variant_ids: list[str] = []
    normalized_variants: list[dict[str, object]] = []
    for index, raw_variant in enumerate(variants):
        variant = _require_mapping(raw_variant, f"scenario variant {index + 1}")
        if set(variant) - {"id", "description"}:
            raise MathFlowError(f"scenario variant {index + 1} has unknown fields")
        identifier = _check_identifier(
            variant.get("id"), f"scenario variant {index + 1} id"
        )
        if identifier in variant_ids:
            raise MathFlowError(f"duplicate scenario variant: {identifier}")
        variant_ids.append(identifier)
        if "description" in variant:
            _require_string(
                variant["description"], f"scenario variant {identifier} description"
            )
        normalized_variants.append(copy.deepcopy(variant))
    manifest["variants"] = normalized_variants

    seeds = _require_list(manifest.get("seeds"), "scenario seeds")
    if not seeds:
        raise MathFlowError("scenario seeds may not be empty")
    normalized_seeds: list[int] = []
    for index, seed in enumerate(seeds):
        value = _require_nonnegative_int(seed, f"scenario seed {index + 1}")
        if value in normalized_seeds:
            raise MathFlowError(f"duplicate scenario seed: {value}")
        normalized_seeds.append(value)
    manifest["seeds"] = normalized_seeds

    frozen_inputs = _require_list(
        manifest.get("frozenInputs"), "scenario frozenInputs"
    )
    if not frozen_inputs:
        raise MathFlowError("scenario frozenInputs may not be empty")
    input_ids: list[str] = []
    normalized_inputs: list[dict[str, object]] = []
    for index, raw_input in enumerate(frozen_inputs):
        item = _require_mapping(raw_input, f"frozen input {index + 1}")
        if set(item) != {"id", "path", "digest", "mediaType"}:
            raise MathFlowError(
                f"frozen input {index + 1} must contain exactly id, path, digest, and mediaType"
            )
        identifier = _check_identifier(item["id"], f"frozen input {index + 1} id")
        if identifier in input_ids:
            raise MathFlowError(f"duplicate frozen input: {identifier}")
        input_ids.append(identifier)
        _require_string(item["path"], f"frozen input {identifier} path")
        _check_digest(item["digest"], f"frozen input {identifier} digest")
        _require_string(item["mediaType"], f"frozen input {identifier} mediaType")
        normalized_inputs.append(copy.deepcopy(item))
    manifest["frozenInputs"] = normalized_inputs

    available = set(input_ids)
    steps = _require_list(manifest.get("steps"), "scenario steps")
    if not steps:
        raise MathFlowError("scenario steps may not be empty")
    step_ids: list[str] = []
    normalized_steps: list[dict[str, object]] = []
    expected_fixture_keys = {
        (variant_id, seed) for variant_id in variant_ids for seed in normalized_seeds
    }
    for step_index, raw_step in enumerate(steps):
        step = _require_mapping(raw_step, f"scenario step {step_index + 1}")
        if set(step) - {"id", "subjectTransactionId", "stages"}:
            raise MathFlowError(f"scenario step {step_index + 1} has unknown fields")
        step_id = _check_identifier(step.get("id"), f"scenario step {step_index + 1} id")
        if step_id in step_ids:
            raise MathFlowError(f"duplicate scenario step: {step_id}")
        step_ids.append(step_id)
        if "subjectTransactionId" in step:
            subject = _require_string(
                step["subjectTransactionId"], f"scenario step {step_id} subject"
            )
            if not _LEDGER_HEAD.fullmatch(subject):
                raise MathFlowError(
                    f"scenario step {step_id} subjectTransactionId must be a full commit"
                )
        stages = _require_list(step.get("stages"), f"scenario step {step_id} stages")
        if not stages:
            raise MathFlowError(f"scenario step {step_id} stages may not be empty")
        stage_ids: list[str] = []
        normalized_stages: list[dict[str, object]] = []
        for stage_index, raw_stage in enumerate(stages):
            stage = _require_mapping(
                raw_stage, f"scenario step {step_id} stage {stage_index + 1}"
            )
            if set(stage) != {"id", "adapter", "reads", "outputs", "fixtures"}:
                raise MathFlowError(
                    f"scenario step {step_id} stage {stage_index + 1} has an invalid contract"
                )
            stage_id = _check_identifier(
                stage["id"], f"scenario step {step_id} stage {stage_index + 1} id"
            )
            if stage_id in stage_ids:
                raise MathFlowError(
                    f"duplicate stage {stage_id} in scenario step {step_id}"
                )
            stage_ids.append(stage_id)
            adapter = _require_string(
                stage["adapter"], f"scenario stage {step_id}.{stage_id} adapter"
            )
            if adapter not in _STAGE_ADAPTERS:
                raise MathFlowError(f"unknown scenario stage adapter: {adapter}")
            reads = _require_list(
                stage["reads"], f"scenario stage {step_id}.{stage_id} reads"
            )
            normalized_reads: list[str] = []
            for read in reads:
                reference = _require_string(
                    read, f"scenario stage {step_id}.{stage_id} read"
                )
                if reference not in available:
                    raise MathFlowError(
                        f"scenario stage {step_id}.{stage_id} reads unavailable artifact {reference}"
                    )
                if reference in normalized_reads:
                    raise MathFlowError(
                        f"scenario stage {step_id}.{stage_id} repeats read {reference}"
                    )
                normalized_reads.append(reference)
            outputs = _require_list(
                stage["outputs"], f"scenario stage {step_id}.{stage_id} outputs"
            )
            if not outputs:
                raise MathFlowError(
                    f"scenario stage {step_id}.{stage_id} outputs may not be empty"
                )
            normalized_outputs: list[str] = []
            for output in outputs:
                output_id = _check_identifier(
                    output, f"scenario stage {step_id}.{stage_id} output"
                )
                if output_id in normalized_outputs:
                    raise MathFlowError(
                        f"scenario stage {step_id}.{stage_id} repeats output {output_id}"
                    )
                qualified = f"{step_id}.{stage_id}.{output_id}"
                if qualified in available:
                    raise MathFlowError(f"duplicate scenario artifact: {qualified}")
                normalized_outputs.append(output_id)
                available.add(qualified)
            fixtures = _require_list(
                stage["fixtures"], f"scenario stage {step_id}.{stage_id} fixtures"
            )
            fixture_keys: set[tuple[str, int]] = set()
            normalized_fixtures: list[dict[str, object]] = []
            for fixture_index, raw_fixture in enumerate(fixtures):
                fixture = _require_mapping(
                    raw_fixture,
                    f"scenario stage {step_id}.{stage_id} fixture {fixture_index + 1}",
                )
                if set(fixture) != {"variant", "seed", "path", "digest"}:
                    raise MathFlowError(
                        f"scenario stage {step_id}.{stage_id} fixture contract is invalid"
                    )
                variant = _require_string(
                    fixture["variant"],
                    f"scenario stage {step_id}.{stage_id} fixture variant",
                )
                seed = _require_nonnegative_int(
                    fixture["seed"],
                    f"scenario stage {step_id}.{stage_id} fixture seed",
                )
                key = (variant, seed)
                if key not in expected_fixture_keys:
                    raise MathFlowError(
                        f"scenario stage {step_id}.{stage_id} fixture has unknown matrix key {key}"
                    )
                if key in fixture_keys:
                    raise MathFlowError(
                        f"scenario stage {step_id}.{stage_id} repeats fixture matrix key {key}"
                    )
                fixture_keys.add(key)
                _require_string(
                    fixture["path"], f"scenario stage {step_id}.{stage_id} fixture path"
                )
                _check_digest(
                    fixture["digest"],
                    f"scenario stage {step_id}.{stage_id} fixture digest",
                )
                normalized_fixtures.append(copy.deepcopy(fixture))
            if fixture_keys != expected_fixture_keys:
                missing = sorted(expected_fixture_keys - fixture_keys)
                raise MathFlowError(
                    f"scenario stage {step_id}.{stage_id} is missing fixture {missing[0]}"
                )
            normalized_stages.append(
                {
                    **copy.deepcopy(stage),
                    "reads": normalized_reads,
                    "outputs": normalized_outputs,
                    "fixtures": normalized_fixtures,
                }
            )
        normalized_steps.append({**copy.deepcopy(step), "stages": normalized_stages})
    manifest["steps"] = normalized_steps

    scorers = _require_list(manifest.get("scorers"), "scenario scorers")
    if not scorers:
        raise MathFlowError("scenario scorers may not be empty")
    scorer_ids: list[str] = []
    normalized_scorers: list[dict[str, object]] = []
    for index, raw_scorer in enumerate(scorers):
        scorer = _require_mapping(raw_scorer, f"scenario scorer {index + 1}")
        if set(scorer) != {"id", "implementation", "goldInputId"}:
            raise MathFlowError(f"scenario scorer {index + 1} contract is invalid")
        scorer_id = _check_identifier(scorer["id"], f"scenario scorer {index + 1} id")
        if scorer_id in scorer_ids:
            raise MathFlowError(f"duplicate scenario scorer: {scorer_id}")
        scorer_ids.append(scorer_id)
        implementation = _require_string(
            scorer["implementation"], f"scenario scorer {scorer_id} implementation"
        )
        if implementation not in _SCORERS:
            raise MathFlowError(f"unknown scenario scorer implementation: {implementation}")
        gold_id = _require_string(
            scorer["goldInputId"], f"scenario scorer {scorer_id} goldInputId"
        )
        if gold_id not in input_ids:
            raise MathFlowError(
                f"scenario scorer {scorer_id} references unknown frozen input {gold_id}"
            )
        normalized_scorers.append(copy.deepcopy(scorer))
    manifest["scorers"] = normalized_scorers
    return manifest, raw, sha256_bytes(raw)


def _normalize_component(value: object, label: str) -> dict[str, object]:
    component = _require_mapping(value, label)
    allowed = {"id", "characters", "bytes", "tokens", "content"}
    if set(component) - allowed:
        raise MathFlowError(f"{label} contains unknown fields")
    identifier = _check_identifier(component.get("id"), f"{label} id")
    content = component.get("content")
    if content is not None and not isinstance(content, str):
        raise MathFlowError(f"{label} content must be a string")
    characters = component.get("characters")
    byte_count = component.get("bytes")
    tokens = component.get("tokens")
    if content is not None:
        actual_characters = len(content)
        actual_bytes = len(content.encode("utf-8"))
        if characters is not None and characters != actual_characters:
            raise MathFlowError(f"{label} character count does not match content")
        if byte_count is not None and byte_count != actual_bytes:
            raise MathFlowError(f"{label} byte count does not match content")
        characters = actual_characters
        byte_count = actual_bytes
    if characters is None:
        raise MathFlowError(f"{label} must provide content or characters")
    result: dict[str, object] = {
        "id": identifier,
        "characters": _require_nonnegative_int(characters, f"{label} characters"),
        "bytes": (
            _require_nonnegative_int(byte_count, f"{label} bytes")
            if byte_count is not None
            else None
        ),
        "tokens": (
            _require_nonnegative_int(tokens, f"{label} tokens")
            if tokens is not None
            else None
        ),
    }
    return result


def _normalize_attempt_telemetry(
    attempt: Mapping[str, object],
    *,
    variant: str,
    seed: int,
    step_id: str,
    stage_id: str,
    attempt_number: int,
) -> dict[str, object]:
    telemetry = _require_mapping(
        attempt.get("telemetry"),
        f"scenario attempt {step_id}.{stage_id}.{attempt_number} telemetry",
    )
    allowed = {
        "model",
        "configuredContextTokens",
        "configuredCompletionTokens",
        "requestComponents",
        "promptTokens",
        "cachedPromptTokens",
        "reasoningTokens",
        "completionTokens",
        "totalTokens",
        "costUsd",
        "elapsedMs",
        "finishReason",
        "outputCharacters",
        "trailingWhitespaceCharacters",
        "validationClass",
        "retryCause",
        "entityCounts",
    }
    extras = sorted(set(telemetry) - allowed)
    if extras:
        raise MathFlowError(
            f"scenario attempt {step_id}.{stage_id}.{attempt_number} telemetry contains unknown field {extras[0]}"
        )
    label = f"scenario attempt {step_id}.{stage_id}.{attempt_number}"
    components = [
        _normalize_component(component, f"{label} request component {index + 1}")
        for index, component in enumerate(
            _require_list(telemetry.get("requestComponents"), f"{label} requestComponents")
        )
    ]
    component_ids = [str(item["id"]) for item in components]
    if len(set(component_ids)) != len(component_ids):
        raise MathFlowError(f"{label} request component ids must be unique")
    provider_call = _require_bool(attempt.get("providerCall"), f"{label} providerCall")
    prompt_tokens = _require_nonnegative_int(
        telemetry.get("promptTokens"), f"{label} promptTokens"
    )
    completion_tokens = _require_nonnegative_int(
        telemetry.get("completionTokens"), f"{label} completionTokens"
    )
    total_tokens = _require_nonnegative_int(
        telemetry.get("totalTokens"), f"{label} totalTokens"
    )
    if total_tokens != prompt_tokens + completion_tokens:
        raise MathFlowError(f"{label} totalTokens must equal prompt plus completion")
    output_characters = telemetry.get("outputCharacters")
    trailing_characters = telemetry.get("trailingWhitespaceCharacters")
    raw_response = attempt.get("rawResponse")
    _require_mapping(attempt.get("rawRequest"), f"{label} rawRequest")
    _require_mapping(raw_response, f"{label} rawResponse")
    if isinstance(raw_response, dict) and isinstance(raw_response.get("content"), str):
        content = str(raw_response["content"])
        observed_output = len(content)
        observed_trailing = len(content) - len(content.rstrip())
        if output_characters is not None and output_characters != observed_output:
            raise MathFlowError(f"{label} outputCharacters does not match raw response")
        if trailing_characters is not None and trailing_characters != observed_trailing:
            raise MathFlowError(
                f"{label} trailingWhitespaceCharacters does not match raw response"
            )
        output_characters = observed_output
        trailing_characters = observed_trailing
    output_characters = _require_nonnegative_int(
        output_characters, f"{label} outputCharacters"
    )
    trailing_characters = _require_nonnegative_int(
        trailing_characters, f"{label} trailingWhitespaceCharacters"
    )
    if trailing_characters > output_characters:
        raise MathFlowError(f"{label} trailing whitespace exceeds output length")
    entity_counts = telemetry.get("entityCounts", {})
    entity_counts = _require_mapping(entity_counts, f"{label} entityCounts")
    normalized_counts: dict[str, int] = {}
    for key, count in sorted(entity_counts.items()):
        identifier = _check_identifier(key, f"{label} entity count id")
        normalized_counts[identifier] = _require_nonnegative_int(
            count, f"{label} entity count {identifier}"
        )
    status = _require_string(attempt.get("status"), f"{label} status")
    if status not in _ATTEMPT_STATUSES:
        raise MathFlowError(f"{label} has unknown status {status}")
    retry_cause = telemetry.get("retryCause")
    if retry_cause is not None:
        _require_string(retry_cause, f"{label} retryCause")
    if status == "retry" and retry_cause is None:
        raise MathFlowError(f"{label} retry must declare retryCause")
    model = telemetry.get("model")
    if model is not None:
        _require_string(model, f"{label} model")
    context_limit = telemetry.get("configuredContextTokens")
    if context_limit is not None:
        context_limit = _require_nonnegative_int(
            context_limit, f"{label} configuredContextTokens"
        )
    completion_limit = telemetry.get("configuredCompletionTokens")
    if completion_limit is not None:
        completion_limit = _require_nonnegative_int(
            completion_limit, f"{label} configuredCompletionTokens"
        )
    finish_reason = telemetry.get("finishReason")
    if finish_reason is not None:
        _require_string(finish_reason, f"{label} finishReason")
    return {
        "schemaVersion": 1,
        "variant": variant,
        "seed": seed,
        "step": step_id,
        "stage": stage_id,
        "attempt": attempt_number,
        "status": status,
        "providerCallRecorded": provider_call,
        "model": model,
        "configuredContextTokens": context_limit,
        "configuredCompletionTokens": completion_limit,
        "requestComponents": components,
        "requestCharacters": sum(int(item["characters"]) for item in components),
        "requestBytes": (
            sum(int(item["bytes"]) for item in components)
            if all(item["bytes"] is not None for item in components)
            else None
        ),
        "promptTokens": prompt_tokens,
        "cachedPromptTokens": _require_nonnegative_int(
            telemetry.get("cachedPromptTokens", 0), f"{label} cachedPromptTokens"
        ),
        "reasoningTokens": _require_nonnegative_int(
            telemetry.get("reasoningTokens", 0), f"{label} reasoningTokens"
        ),
        "completionTokens": completion_tokens,
        "totalTokens": total_tokens,
        "costUsd": float(
            _require_nonnegative_decimal(telemetry.get("costUsd", 0), f"{label} costUsd")
        ),
        "elapsedMs": (
            _require_nonnegative_int(telemetry["elapsedMs"], f"{label} elapsedMs")
            if telemetry.get("elapsedMs") is not None
            else None
        ),
        "finishReason": finish_reason,
        "outputCharacters": output_characters,
        "trailingWhitespaceCharacters": trailing_characters,
        "validationClass": _require_string(
            telemetry.get("validationClass"), f"{label} validationClass"
        ),
        "retryCause": retry_cause,
        "entityCounts": normalized_counts,
    }


def _prepare_fixture(
    root: Path,
    stage: Mapping[str, object],
    fixture_ref: Mapping[str, object],
    *,
    variant: str,
    seed: int,
    step_id: str,
    stage_id: str,
) -> PreparedFixture:
    path, raw = _load_bound_file(
        root,
        fixture_ref.get("path"),
        fixture_ref.get("digest"),
        f"scenario fixture {variant}/{seed}/{step_id}/{stage_id}",
    )
    value = _require_mapping(
        _load_json_bytes(raw, f"scenario fixture {path}"), f"scenario fixture {path}"
    )
    if set(value) != {"schemaVersion", "stageId", "outcome", "attempts", "outputs"}:
        raise MathFlowError(f"scenario fixture {path} has an invalid contract")
    if value.get("schemaVersion") != 1:
        raise MathFlowError(f"scenario fixture {path} schemaVersion must be 1")
    if value.get("stageId") != stage_id:
        raise MathFlowError(f"scenario fixture {path} stageId does not match manifest")
    outcome = _require_string(value.get("outcome"), f"scenario fixture {path} outcome")
    if outcome not in {"accepted", "failed"}:
        raise MathFlowError(f"scenario fixture {path} has unknown outcome {outcome}")
    raw_attempts = _require_list(value.get("attempts"), f"scenario fixture {path} attempts")
    if not raw_attempts:
        raise MathFlowError(f"scenario fixture {path} attempts may not be empty")
    attempts: list[dict[str, object]] = []
    telemetry: list[dict[str, object]] = []
    for index, raw_attempt in enumerate(raw_attempts):
        attempt = _require_mapping(
            raw_attempt, f"scenario fixture {path} attempt {index + 1}"
        )
        if set(attempt) != {"status", "providerCall", "rawRequest", "rawResponse", "telemetry"}:
            raise MathFlowError(
                f"scenario fixture {path} attempt {index + 1} has an invalid contract"
            )
        attempts.append(copy.deepcopy(attempt))
        telemetry.append(
            _normalize_attempt_telemetry(
                attempt,
                variant=variant,
                seed=seed,
                step_id=step_id,
                stage_id=stage_id,
                attempt_number=index + 1,
            )
        )
    if any(attempt["status"] != "retry" for attempt in attempts[:-1]):
        raise MathFlowError(f"scenario fixture {path} has a nonterminal non-retry attempt")
    if attempts[-1]["status"] != outcome:
        raise MathFlowError(f"scenario fixture {path} terminal attempt disagrees with outcome")

    declared_outputs = set(str(item) for item in stage["outputs"])
    raw_outputs = _require_list(value.get("outputs"), f"scenario fixture {path} outputs")
    output_ids: set[str] = set()
    outputs: list[tuple[str, ScenarioArtifact, bytes | None]] = []
    for index, raw_output in enumerate(raw_outputs):
        output = _require_mapping(
            raw_output, f"scenario fixture {path} output {index + 1}"
        )
        allowed = {"id", "mediaType", "value", "path", "digest"}
        if set(output) - allowed:
            raise MathFlowError(f"scenario fixture {path} output {index + 1} has unknown fields")
        output_id = _check_identifier(
            output.get("id"), f"scenario fixture {path} output {index + 1} id"
        )
        if output_id in output_ids:
            raise MathFlowError(f"scenario fixture {path} repeats output {output_id}")
        output_ids.add(output_id)
        media_type = _require_string(
            output.get("mediaType"), f"scenario fixture {path} output {output_id} mediaType"
        )
        has_value = "value" in output
        has_path = "path" in output or "digest" in output
        if has_value == has_path:
            raise MathFlowError(
                f"scenario fixture {path} output {output_id} must contain either value or path/digest"
            )
        if has_value:
            output_value = copy.deepcopy(output["value"])
            rendered = _json_bytes(output_value)
            artifact = ScenarioArtifact(
                value=output_value,
                digest=sha256_bytes(rendered),
                media_type=media_type,
            )
            outputs.append((output_id, artifact, None))
        else:
            output_path, output_raw = _load_bound_file(
                root,
                output.get("path"),
                output.get("digest"),
                f"scenario fixture {path} output {output_id}",
            )
            output_value: object
            if media_type == "application/json":
                output_value = _load_json_bytes(
                    output_raw, f"scenario fixture output {output_path}"
                )
            elif media_type.startswith("text/"):
                try:
                    output_value = output_raw.decode("utf-8")
                except UnicodeDecodeError as exc:
                    raise MathFlowError(
                        f"scenario fixture output {output_path} is not UTF-8"
                    ) from exc
            else:
                output_value = output_raw
            artifact = ScenarioArtifact(
                value=output_value,
                digest=sha256_bytes(output_raw),
                media_type=media_type,
            )
            outputs.append((output_id, artifact, output_raw))
    expected_outputs = declared_outputs if outcome == "accepted" else set()
    if output_ids != expected_outputs:
        raise MathFlowError(
            f"scenario fixture {path} outputs do not match the stage contract"
        )
    return PreparedFixture(
        path=path,
        raw=raw,
        value=value,
        attempts=tuple(attempts),
        telemetry=tuple(telemetry),
        outputs=tuple(outputs),
    )


def _aggregate_telemetry(records: Sequence[Mapping[str, object]]) -> dict[str, object]:
    cost = sum((Decimal(str(item["costUsd"])) for item in records), Decimal("0"))
    validation_counts: dict[str, int] = {}
    retry_counts: dict[str, int] = {}
    component_totals: dict[str, dict[str, int | None]] = {}
    stage_totals: dict[str, dict[str, object]] = {}
    for record in records:
        validation = str(record["validationClass"])
        validation_counts[validation] = validation_counts.get(validation, 0) + 1
        retry = record.get("retryCause")
        if isinstance(retry, str):
            retry_counts[retry] = retry_counts.get(retry, 0) + 1
        for component in record["requestComponents"]:
            component = _require_mapping(component, "normalized request component")
            key = str(component["id"])
            current = component_totals.setdefault(
                key, {"characters": 0, "bytes": 0, "tokens": 0}
            )
            current["characters"] = int(current["characters"] or 0) + int(
                component["characters"]
            )
            for field in ("bytes", "tokens"):
                if current[field] is None or component[field] is None:
                    current[field] = None
                else:
                    current[field] = int(current[field]) + int(component[field])
        stage_key = f"{record['step']}.{record['stage']}"
        stage = stage_totals.setdefault(
            stage_key,
            {
                "attempts": 0,
                "providerCallsRecorded": 0,
                "promptTokens": 0,
                "completionTokens": 0,
                "totalTokens": 0,
                "costUsd": 0.0,
            },
        )
        stage["attempts"] = int(stage["attempts"]) + 1
        stage["providerCallsRecorded"] = int(stage["providerCallsRecorded"]) + int(
            bool(record["providerCallRecorded"])
        )
        for field in ("promptTokens", "completionTokens", "totalTokens"):
            stage[field] = int(stage[field]) + int(record[field])
        stage["costUsd"] = float(
            Decimal(str(stage["costUsd"])) + Decimal(str(record["costUsd"]))
        )
    return {
        "schemaVersion": 1,
        "providerCallsExecuted": 0,
        "providerCallsRecorded": sum(
            int(bool(item["providerCallRecorded"])) for item in records
        ),
        "stageAttempts": len(records),
        "promptTokens": sum(int(item["promptTokens"]) for item in records),
        "cachedPromptTokens": sum(int(item["cachedPromptTokens"]) for item in records),
        "reasoningTokens": sum(int(item["reasoningTokens"]) for item in records),
        "completionTokens": sum(int(item["completionTokens"]) for item in records),
        "totalTokens": sum(int(item["totalTokens"]) for item in records),
        "costUsdRecorded": float(cost),
        "requestCharacters": sum(int(item["requestCharacters"]) for item in records),
        "outputCharacters": sum(int(item["outputCharacters"]) for item in records),
        "trailingWhitespaceCharacters": sum(
            int(item["trailingWhitespaceCharacters"]) for item in records
        ),
        "validationClasses": dict(sorted(validation_counts.items())),
        "retryCauses": dict(sorted(retry_counts.items())),
        "requestComponents": dict(sorted(component_totals.items())),
        "stages": dict(sorted(stage_totals.items())),
    }


def _enforce_budgets(
    budgets: Mapping[str, object], telemetry: Mapping[str, object]
) -> dict[str, object]:
    observed = {
        "maximumProviderCalls": int(telemetry["providerCallsRecorded"]),
        "maximumStageAttempts": int(telemetry["stageAttempts"]),
        "maximumPromptTokens": int(telemetry["promptTokens"]),
        "maximumCompletionTokens": int(telemetry["completionTokens"]),
        "maximumTotalTokens": int(telemetry["totalTokens"]),
        "maximumCostUsd": float(telemetry["costUsdRecorded"]),
    }
    checks: list[dict[str, object]] = []
    for field in _BUDGET_FIELDS:
        limit = Decimal(str(budgets[field]))
        actual = Decimal(str(observed[field]))
        passed = actual <= limit
        checks.append(
            {
                "metric": field,
                "limit": float(limit) if field == "maximumCostUsd" else int(limit),
                "observed": float(actual) if field == "maximumCostUsd" else int(actual),
                "passed": passed,
            }
        )
        if not passed:
            raise MathFlowError(
                f"scenario hard budget exceeded for {field}: observed {actual}, limit {limit}"
            )
    return {"schemaVersion": 1, "status": "passed", "checks": checks}


def _pointer(value: object, pointer: object) -> object:
    raw = _require_string(pointer, "relational JSON pointer")
    if raw == "":
        return value
    if not raw.startswith("/"):
        raise MathFlowError(f"invalid relational JSON pointer: {raw}")
    current = value
    for part in raw[1:].split("/"):
        token = part.replace("~1", "/").replace("~0", "~")
        if isinstance(current, dict):
            if token not in current:
                raise MathFlowError(f"relational JSON pointer is missing key {token!r}")
            current = current[token]
        elif isinstance(current, list):
            try:
                index = int(token)
            except ValueError as exc:
                raise MathFlowError(
                    f"relational JSON pointer list index is invalid: {token}"
                ) from exc
            if index < 0 or index >= len(current):
                raise MathFlowError(
                    f"relational JSON pointer list index is out of range: {index}"
                )
            current = current[index]
        else:
            raise MathFlowError("relational JSON pointer traverses a scalar")
    return current


def _compare(actual: object, operator: str, expected: object) -> bool:
    if operator == "equals":
        return actual == expected
    if operator == "not-equals":
        return actual != expected
    if operator == "contains":
        return expected in actual if isinstance(actual, (list, str, dict)) else False
    if operator == "set-equals":
        return isinstance(actual, list) and isinstance(expected, list) and {
            json.dumps(item, sort_keys=True, ensure_ascii=False) for item in actual
        } == {json.dumps(item, sort_keys=True, ensure_ascii=False) for item in expected}
    if operator == "subset-of":
        return isinstance(actual, list) and isinstance(expected, list) and {
            json.dumps(item, sort_keys=True, ensure_ascii=False) for item in actual
        } <= {json.dumps(item, sort_keys=True, ensure_ascii=False) for item in expected}
    if operator == "greater-than":
        return isinstance(actual, (int, float)) and isinstance(expected, (int, float)) and actual > expected
    if operator == "less-than":
        return isinstance(actual, (int, float)) and isinstance(expected, (int, float)) and actual < expected
    if operator == "truthy":
        return bool(actual)
    if operator == "falsy":
        return not bool(actual)
    raise MathFlowError(f"unknown relational assertion operator: {operator}")


def _evaluate_expression(
    expression: object, registry: Mapping[str, ScenarioArtifact]
) -> object:
    expr = _require_mapping(expression, "relational expression")
    if "artifact" in expr:
        if set(expr) - {"artifact", "pointer"}:
            raise MathFlowError("artifact relational expression has unknown fields")
        artifact_id = _require_string(expr["artifact"], "relational artifact id")
        if artifact_id not in registry:
            raise MathFlowError(f"relational expression references missing artifact {artifact_id}")
        value = registry[artifact_id].value
        return _pointer(value, expr.get("pointer", ""))
    operation = _require_string(expr.get("operation"), "relational expression operation")
    if operation in {"keys", "values", "length", "unique", "sort", "flatten"}:
        value = _evaluate_expression(expr.get("value"), registry)
        if operation == "keys":
            if not isinstance(value, dict):
                raise MathFlowError("relational keys operation requires an object")
            return sorted(value)
        if operation == "values":
            if not isinstance(value, dict):
                raise MathFlowError("relational values operation requires an object")
            return list(value.values())
        if operation == "length":
            if not isinstance(value, (dict, list, str)):
                raise MathFlowError("relational length operation requires a collection")
            return len(value)
        if not isinstance(value, list):
            raise MathFlowError(f"relational {operation} operation requires an array")
        if operation == "flatten":
            if any(not isinstance(item, list) for item in value):
                raise MathFlowError("relational flatten operation requires an array of arrays")
            return [nested for item in value for nested in item]
        if operation == "unique":
            seen: set[str] = set()
            result: list[object] = []
            for item in value:
                key = json.dumps(item, sort_keys=True, ensure_ascii=False)
                if key not in seen:
                    seen.add(key)
                    result.append(item)
            return result
        return sorted(value, key=lambda item: json.dumps(item, sort_keys=True, ensure_ascii=False))
    if operation == "map":
        value = _evaluate_expression(expr.get("value"), registry)
        if not isinstance(value, list):
            raise MathFlowError("relational map operation requires an array")
        pointer = expr.get("pointer", "")
        return [_pointer(item, pointer) for item in value]
    if operation == "filter":
        value = _evaluate_expression(expr.get("value"), registry)
        if not isinstance(value, list):
            raise MathFlowError("relational filter operation requires an array")
        raw_conditions = _require_list(expr.get("where"), "relational filter conditions")
        conditions = [_require_mapping(item, "relational filter condition") for item in raw_conditions]
        result = []
        for item in value:
            if all(
                _compare(
                    _pointer(item, condition.get("pointer", "")),
                    _require_string(condition.get("operator"), "relational filter operator"),
                    condition.get("expected"),
                )
                for condition in conditions
            ):
                result.append(item)
        return result
    if operation in {"difference", "intersection", "concat"}:
        left = _evaluate_expression(expr.get("left"), registry)
        right = _evaluate_expression(expr.get("right"), registry)
        if not isinstance(left, list) or not isinstance(right, list):
            raise MathFlowError(f"relational {operation} requires arrays")
        if operation == "concat":
            return left + right
        right_keys = {
            json.dumps(item, sort_keys=True, ensure_ascii=False) for item in right
        }
        if operation == "difference":
            return [
                item
                for item in left
                if json.dumps(item, sort_keys=True, ensure_ascii=False) not in right_keys
            ]
        return [
            item
            for item in left
            if json.dumps(item, sort_keys=True, ensure_ascii=False) in right_keys
        ]
    raise MathFlowError(f"unknown relational expression operation: {operation}")


def _score_json_relational(
    gold: object,
    registry: Mapping[str, ScenarioArtifact],
    *,
    variant: str,
    seed: int,
    scorer_id: str,
) -> dict[str, object]:
    document = _require_mapping(gold, f"relational gold {scorer_id}")
    if document.get("schemaVersion") != 1:
        raise MathFlowError(f"relational gold {scorer_id} schemaVersion must be 1")
    assertions = _require_list(
        document.get("assertions"), f"relational gold {scorer_id} assertions"
    )
    results: list[dict[str, object]] = []
    for index, raw_assertion in enumerate(assertions):
        assertion = _require_mapping(
            raw_assertion, f"relational gold {scorer_id} assertion {index + 1}"
        )
        assertion_id = _check_identifier(
            assertion.get("id"), f"relational gold {scorer_id} assertion id"
        )
        allowed = {
            "id",
            "severity",
            "actual",
            "operator",
            "expected",
            "expectedExpression",
            "message",
            "variants",
            "seeds",
        }
        extras = sorted(set(assertion) - allowed)
        if extras:
            raise MathFlowError(
                f"relational assertion {assertion_id} contains unknown field {extras[0]}"
            )
        if "expected" in assertion and "expectedExpression" in assertion:
            raise MathFlowError(
                f"relational assertion {assertion_id} cannot declare two expected values"
            )
        variants = assertion.get("variants")
        if variants is not None:
            variants = _require_list(variants, f"relational assertion {assertion_id} variants")
            if variant not in variants:
                continue
        seeds = assertion.get("seeds")
        if seeds is not None:
            seeds = _require_list(seeds, f"relational assertion {assertion_id} seeds")
            if seed not in seeds:
                continue
        severity = _require_string(
            assertion.get("severity", "hard"),
            f"relational assertion {assertion_id} severity",
        )
        if severity not in _SEVERITIES:
            raise MathFlowError(f"relational assertion {assertion_id} has unknown severity")
        operator = _require_string(
            assertion.get("operator"), f"relational assertion {assertion_id} operator"
        )
        try:
            actual = _evaluate_expression(assertion.get("actual"), registry)
            expected = (
                _evaluate_expression(assertion["expectedExpression"], registry)
                if "expectedExpression" in assertion
                else assertion.get("expected")
            )
            passed = _compare(actual, operator, expected)
            result = {
                "id": assertion_id,
                "severity": severity,
                "passed": passed,
                "operator": operator,
                "actual": actual,
                "expected": expected,
                "message": assertion.get("message"),
            }
        except MathFlowError as exc:
            result = {
                "id": assertion_id,
                "severity": severity,
                "passed": False,
                "operator": operator,
                "error": str(exc),
                "message": assertion.get("message"),
            }
        results.append(result)
    hard_failures = [
        item["id"] for item in results if not item["passed"] and item["severity"] == "hard"
    ]
    advisory_failures = [
        item["id"]
        for item in results
        if not item["passed"] and item["severity"] == "advisory"
    ]
    return {
        "schemaVersion": 1,
        "scorerId": scorer_id,
        "implementation": "json-relational-v1",
        "status": "passed" if not hard_failures else "failed",
        "assertions": results,
        "passed": sum(int(bool(item["passed"])) for item in results),
        "failed": sum(int(not bool(item["passed"])) for item in results),
        "hardFailures": hard_failures,
        "advisoryFailures": advisory_failures,
    }


def _render_report(
    manifest: Mapping[str, object],
    telemetry: Mapping[str, object],
    budget: Mapping[str, object],
    chain_results: Sequence[Mapping[str, object]],
) -> str:
    hard_failures = sum(int(item["hardFailures"]) for item in chain_results)
    return "\n".join(
        [
            f"# Teacher-student scenario: {manifest['id']}",
            "",
            str(manifest["description"]),
            "",
            "## Execution",
            "",
            "- Adapter: `fixture-replay-v1` (provider-free)",
            "- Provider calls executed: 0",
            f"- Historical/fake provider calls represented: {telemetry['providerCallsRecorded']}",
            f"- Stage attempts represented: {telemetry['stageAttempts']}",
            f"- Recorded tokens: {telemetry['totalTokens']}",
            f"- Recorded cost: ${float(telemetry['costUsdRecorded']):.6f}",
            f"- Hard budgets: {budget['status']}",
            f"- Publication forbidden: {str(manifest['publicationForbidden']).lower()}",
            "",
            "## Score",
            "",
            f"- Chains: {len(chain_results)}",
            f"- Hard assertion failures: {hard_failures}",
            f"- Overall status: {'passed' if hard_failures == 0 else 'failed'}",
            "",
            "Every fixture, raw attempt, normalized telemetry record, stage output,",
            "read binding, and scorecard is digest-indexed by `run.json`.",
            "",
        ]
    )


def run_teacher_student_scenario(
    root: Path, manifest_path: Path, output_dir: Path
) -> dict[str, object]:
    root = root.resolve()
    manifest, manifest_raw, manifest_digest = validate_teacher_student_scenario_manifest(
        root, manifest_path
    )
    frozen: dict[str, tuple[dict[str, object], ScenarioArtifact, bytes]] = {}
    for item in manifest["frozenInputs"]:
        item = _require_mapping(item, "validated frozen input")
        path, raw = _load_bound_file(
            root,
            item["path"],
            item["digest"],
            f"frozen input {item['id']}",
        )
        media_type = str(item["mediaType"])
        if media_type == "application/json":
            value = _load_json_bytes(raw, f"frozen input {path}")
        elif media_type.startswith("text/"):
            try:
                value = raw.decode("utf-8")
            except UnicodeDecodeError as exc:
                raise MathFlowError(f"frozen input {path} is not UTF-8") from exc
        else:
            value = raw
        frozen[str(item["id"])] = (
            item,
            ScenarioArtifact(value=value, digest=sha256_bytes(raw), media_type=media_type),
            raw,
        )

    prepared: dict[tuple[str, int, str, str], PreparedFixture] = {}
    telemetry_records: list[dict[str, object]] = []
    for variant_entry in manifest["variants"]:
        variant = str(variant_entry["id"])
        for seed in manifest["seeds"]:
            reachable = True
            for step in manifest["steps"]:
                step_id = str(step["id"])
                for stage in step["stages"]:
                    stage_id = str(stage["id"])
                    fixture_ref = next(
                        item
                        for item in stage["fixtures"]
                        if item["variant"] == variant and item["seed"] == seed
                    )
                    fixture = _prepare_fixture(
                        root,
                        stage,
                        fixture_ref,
                        variant=variant,
                        seed=int(seed),
                        step_id=step_id,
                        stage_id=stage_id,
                    )
                    prepared[(variant, int(seed), step_id, stage_id)] = fixture
                    if reachable:
                        telemetry_records.extend(copy.deepcopy(list(fixture.telemetry)))
                        if fixture.value["outcome"] != "accepted":
                            reachable = False
    aggregate_telemetry = _aggregate_telemetry(telemetry_records)
    budget_report = _enforce_budgets(manifest["budgets"], aggregate_telemetry)

    bundle = ArtifactBundle(output_dir)
    bundle.add_bytes(
        "scenario/manifest.json",
        manifest_raw,
        "teacher-student-scenario-manifest",
        "application/json",
    )
    for input_id, (item, artifact, raw) in sorted(frozen.items()):
        suffix = PurePosixPath(str(item["path"])).suffix or ".bin"
        bundle.add_bytes(
            f"scenario/inputs/{input_id}{suffix}",
            raw,
            f"teacher-student-scenario-input/{input_id}",
            artifact.media_type,
        )

    chain_results: list[dict[str, object]] = []
    for variant_entry in manifest["variants"]:
        variant = str(variant_entry["id"])
        for seed_value in manifest["seeds"]:
            seed = int(seed_value)
            chain_registry = {
                key: artifact for key, (_, artifact, _) in frozen.items()
            }
            chain_status = "completed"
            stage_results: list[dict[str, object]] = []
            chain_telemetry: list[dict[str, object]] = []
            prefix = f"chains/{variant}/seed-{seed}"
            for step in manifest["steps"]:
                step_id = str(step["id"])
                for stage in step["stages"]:
                    stage_id = str(stage["id"])
                    fixture = prepared[(variant, seed, step_id, stage_id)]
                    stage_prefix = f"{prefix}/steps/{step_id}/stages/{stage_id}"
                    bundle.add_bytes(
                        f"{stage_prefix}/fixture.json",
                        fixture.raw,
                        f"teacher-student-stage-fixture/{variant}/{seed}/{step_id}/{stage_id}",
                        "application/json",
                    )
                    reads = []
                    for reference in stage["reads"]:
                        if reference not in chain_registry:
                            raise MathFlowError(
                                f"scenario stage {step_id}.{stage_id} is missing read {reference} at execution"
                            )
                        reads.append(
                            {
                                "artifactId": reference,
                                "digest": chain_registry[reference].digest,
                            }
                        )
                    for index, (attempt, telemetry) in enumerate(
                        zip(fixture.attempts, fixture.telemetry, strict=True), start=1
                    ):
                        bundle.add_json(
                            f"{stage_prefix}/attempts/attempt-{index}.json",
                            attempt,
                            f"teacher-student-raw-attempt/{variant}/{seed}/{step_id}/{stage_id}/{index}",
                        )
                        bundle.add_json(
                            f"{stage_prefix}/attempts/attempt-{index}-telemetry.json",
                            telemetry,
                            f"teacher-student-attempt-telemetry/{variant}/{seed}/{step_id}/{stage_id}/{index}",
                        )
                        chain_telemetry.append(copy.deepcopy(telemetry))
                    output_bindings = []
                    for output_id, artifact, raw in fixture.outputs:
                        qualified = f"{step_id}.{stage_id}.{output_id}"
                        if raw is None:
                            bundle.add_json(
                                f"{stage_prefix}/outputs/{output_id}.json",
                                artifact.value,
                                f"teacher-student-stage-output/{variant}/{seed}/{qualified}",
                            )
                        else:
                            extension = (
                                ".json"
                                if artifact.media_type == "application/json"
                                else ".txt"
                                if artifact.media_type.startswith("text/")
                                else ".bin"
                            )
                            bundle.add_bytes(
                                f"{stage_prefix}/outputs/{output_id}{extension}",
                                raw,
                                f"teacher-student-stage-output/{variant}/{seed}/{qualified}",
                                artifact.media_type,
                            )
                        chain_registry[qualified] = artifact
                        output_bindings.append(
                            {"artifactId": qualified, "digest": artifact.digest}
                        )
                    result = {
                        "schemaVersion": 1,
                        "step": step_id,
                        "stage": stage_id,
                        "adapter": stage["adapter"],
                        "outcome": fixture.value["outcome"],
                        "reads": reads,
                        "outputs": output_bindings,
                        "attempts": len(fixture.attempts),
                    }
                    bundle.add_json(
                        f"{stage_prefix}/result.json",
                        result,
                        f"teacher-student-stage-result/{variant}/{seed}/{step_id}/{stage_id}",
                    )
                    stage_results.append(result)
                    if result["outcome"] != "accepted":
                        chain_status = "failed-stage"
                        break
                if chain_status != "completed":
                    break
            scorecards: list[dict[str, object]] = []
            if chain_status == "completed":
                for scorer in manifest["scorers"]:
                    scorer_id = str(scorer["id"])
                    gold = chain_registry[str(scorer["goldInputId"])].value
                    scorecard = _score_json_relational(
                        gold,
                        chain_registry,
                        variant=variant,
                        seed=seed,
                        scorer_id=scorer_id,
                    )
                    scorecards.append(scorecard)
                    bundle.add_json(
                        f"{prefix}/scores/{scorer_id}.json",
                        scorecard,
                        f"teacher-student-scorecard/{variant}/{seed}/{scorer_id}",
                    )
            hard_failures = sum(len(item["hardFailures"]) for item in scorecards)
            chain_summary = {
                "schemaVersion": 1,
                "variant": variant,
                "seed": seed,
                "status": chain_status,
                "scoreStatus": (
                    "not-scored"
                    if not scorecards
                    else "failed"
                    if hard_failures
                    else "passed"
                ),
                "hardFailures": hard_failures,
                "stages": stage_results,
                "telemetry": _aggregate_telemetry(chain_telemetry),
            }
            bundle.add_json(
                f"{prefix}/summary.json",
                chain_summary,
                f"teacher-student-chain-summary/{variant}/{seed}",
            )
            chain_results.append(chain_summary)

    bundle.add_json(
        "telemetry.json", aggregate_telemetry, "teacher-student-aggregate-telemetry"
    )
    bundle.add_json("budgets.json", budget_report, "teacher-student-budget-report")
    summary = {
        "schemaVersion": 1,
        "scenarioId": manifest["id"],
        "chains": len(chain_results),
        "completedChains": sum(item["status"] == "completed" for item in chain_results),
        "hardFailures": sum(int(item["hardFailures"]) for item in chain_results),
    }
    summary["status"] = (
        "passed"
        if summary["completedChains"] == summary["chains"]
        and summary["hardFailures"] == 0
        else "failed"
    )
    bundle.add_json("summary.json", summary, "teacher-student-scenario-summary")
    bundle.add_text(
        "report.md",
        _render_report(manifest, aggregate_telemetry, budget_report, chain_results),
        "teacher-student-scenario-report",
        "text/markdown",
    )
    return bundle.finalize(
        {
            "protocolVersion": 1,
            "runKind": "teacher-student-scenario",
            "problemId": manifest["problemId"],
            "ledgerHead": manifest["ledgerHead"],
            "scenario": {
                "id": manifest["id"],
                "schemaVersion": manifest["schemaVersion"],
                "digest": manifest_digest,
            },
            "runner": {
                "implementation": "teacher-student-scenario-v1",
                "mathFlowVersion": __version__,
            },
            "execution": {
                "adapter": "fixture-replay-v1",
                "providerCallsExecuted": 0,
                "publicationForbidden": True,
            },
            "budgets": manifest["budgets"],
            "summary": summary,
        }
    )
