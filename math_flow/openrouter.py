from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from collections.abc import Callable
from typing import Any

from .errors import MathFlowError


OPENROUTER_CHAT_COMPLETIONS_URL = "https://openrouter.ai/api/v1/chat/completions"
OpenRouterTransport = Callable[[dict[str, object]], dict[str, object]]


def format_error_message(error: object, fallback: str = "request failed") -> str:
    if not isinstance(error, dict):
        return fallback
    message = str(error.get("message", fallback))
    metadata = error.get("metadata")
    if not isinstance(metadata, dict):
        return message
    details = []
    for field in ("error_type", "provider_name", "provider_code"):
        value = metadata.get(field)
        if isinstance(value, (str, int)):
            details.append(f"{field}={value}")
    return f"{message} ({', '.join(details)})" if details else message


def judge_output_schema(transaction_ids: list[str]) -> dict[str, object]:
    transaction_id_schema: dict[str, object] = {"type": "string"}
    if transaction_ids:
        transaction_id_schema["enum"] = transaction_ids
    return {
        "type": "object",
        "properties": {
            "contributionVerdicts": {
                "type": "array",
                "minItems": len(transaction_ids),
                "maxItems": len(transaction_ids),
                "items": {
                    "type": "object",
                    "properties": {
                        "transactionId": transaction_id_schema,
                        "status": {
                            "type": "string",
                            "enum": ["accepted", "rejected", "uncertain"],
                        },
                        "confidence": {"type": "number", "minimum": 0, "maximum": 1},
                        "rationale": {"type": "string"},
                    },
                    "required": ["transactionId", "status", "confidence", "rationale"],
                    "additionalProperties": False,
                },
            },
            "knowledgeState": {
                "type": "object",
                "properties": {
                    "summary": {"type": "string"},
                    "establishedClaims": {"type": "array", "items": {"type": "string"}},
                    "openQuestions": {"type": "array", "items": {"type": "string"}},
                    "disputes": {"type": "array", "items": {"type": "string"}},
                },
                "required": ["summary", "establishedClaims", "openQuestions", "disputes"],
                "additionalProperties": False,
            },
            "creditAssignments": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "participant": {"type": "string"},
                        "transactionIds": {
                            "type": "array",
                            "items": transaction_id_schema,
                        },
                        "score": {"type": "number", "minimum": 0, "maximum": 1},
                        "rationale": {"type": "string"},
                    },
                    "required": ["participant", "transactionIds", "score", "rationale"],
                    "additionalProperties": False,
                },
            },
        },
        "required": ["contributionVerdicts", "knowledgeState", "creditAssignments"],
        "additionalProperties": False,
    }


def send_chat_completion(payload: dict[str, object]) -> dict[str, object]:
    api_key = os.environ.get("OPENROUTER_API_KEY")
    if not api_key:
        raise MathFlowError("OPENROUTER_API_KEY is required for an OpenRouter judge run")

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "X-Title": "Math Flow",
    }
    site_url = os.environ.get("MATH_FLOW_SITE_URL")
    if site_url:
        headers["HTTP-Referer"] = site_url
    request = urllib.request.Request(
        OPENROUTER_CHAT_COMPLETIONS_URL,
        data=json.dumps(payload).encode("utf-8"),
        headers=headers,
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=180) as response:
            body = response.read().decode("utf-8")
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        message = "request failed"
        try:
            error = json.loads(body).get("error", {})
            message = format_error_message(error, message)
        except (json.JSONDecodeError, AttributeError):
            pass
        raise MathFlowError(f"OpenRouter returned HTTP {exc.code}: {message[:500]}") from exc
    except urllib.error.URLError as exc:
        raise MathFlowError(f"could not reach OpenRouter: {exc.reason}") from exc

    try:
        parsed: Any = json.loads(body)
    except json.JSONDecodeError as exc:
        raise MathFlowError("OpenRouter returned a non-JSON response") from exc
    if not isinstance(parsed, dict):
        raise MathFlowError("OpenRouter returned an unexpected response shape")
    return parsed
