from __future__ import annotations

import argparse
import json
from pathlib import Path

from math_flow.artifacts import sha256_bytes
from math_flow.miniature_e2e_scenario import (
    PROBLEM_ID,
    SUBJECTS,
    build_miniature_e2e_transcript,
    miniature_e2e_oracle,
    score_miniature_e2e_scenario,
)


RELATIVE_DIR = Path("protocol/experiments/miniature-e2e-v1")
SOURCE_ROOT = Path(__file__).resolve().parents[1]
CANDIDATE_INPUTS = (
    (
        "knowledge-builder-spec",
        "protocol/judges/openrouter-hierarchical-research-builder-v10-experiment.json",
        "application/json",
    ),
    (
        "work-accounting-spec",
        "protocol/judges/openrouter-work-accounting-v2.json",
        "application/json",
    ),
    (
        "work-accounting-policy",
        "protocol/policies/hierarchical-work-remaining-accounting-v2.md",
        "text/markdown",
    ),
)


def _json_bytes(value: object) -> bytes:
    return (json.dumps(value, indent=2, ensure_ascii=False) + "\n").encode("utf-8")


def _write(path: Path, value: object) -> str:
    raw = _json_bytes(value)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(raw)
    return sha256_bytes(raw)


def write_miniature_e2e_fixture(destination_root: Path) -> dict[str, object]:
    """Regenerate the checked-in provider-free scenario from executable reducers."""

    destination_root = destination_root.resolve()
    target = destination_root / RELATIVE_DIR
    transcript = build_miniature_e2e_transcript()
    oracle = miniature_e2e_oracle()
    score = score_miniature_e2e_scenario(transcript, oracle)
    if score["status"] != "passed":
        raise RuntimeError(f"generated miniature E2E fixture failed: {score['hardFailures']}")

    transcript_digest = _write(target / "transcript.json", transcript)
    oracle_digest = _write(target / "oracle.json", oracle)
    candidate_inputs = [
        {
            "id": input_id,
            "path": path,
            "digest": sha256_bytes((SOURCE_ROOT / path).read_bytes()),
            "mediaType": media_type,
        }
        for input_id, path, media_type in CANDIDATE_INPUTS
    ]
    accepted_text = "accepted deterministic V10/V2 captured replay"
    request_component = json.dumps(
        {
            "kind": "deterministic-v10-v2-captured-replay",
            "transcriptDigest": transcript_digest,
            "localCaptureTransportInvocations": len(SUBJECTS) * 3,
            "externalProviderCalls": 0,
            "networkUsed": False,
            "candidateBindings": {
                item["id"]: item["digest"] for item in candidate_inputs
            },
        },
        sort_keys=True,
        separators=(",", ":"),
    )
    fixture = {
        "schemaVersion": 1,
        "stageId": "replay",
        "outcome": "accepted",
        "inputBindings": [
            {"artifactId": "miniature-oracle", "digest": oracle_digest},
            *[
                {"artifactId": item["id"], "digest": item["digest"]}
                for item in candidate_inputs
            ],
        ],
        "attempts": [
            {
                "status": "accepted",
                "providerCall": False,
                "rawRequest": {
                    "kind": "deterministic-v10-v2-captured-replay",
                    "transcriptDigest": transcript_digest,
                    "localCaptureTransportInvocations": len(SUBJECTS) * 3,
                    "externalProviderCalls": 0,
                    "networkUsed": False,
                    "candidateBindings": {
                        item["id"]: item["digest"] for item in candidate_inputs
                    },
                },
                "rawResponse": {"content": accepted_text},
                "telemetry": {
                    "model": "provider-free/reducer-replay-v1",
                    "configuredContextTokens": 0,
                    "configuredCompletionTokens": 0,
                    "requestComponents": [
                        {
                            "id": "deterministic-v10-v2-captured-replay",
                            "content": request_component,
                        }
                    ],
                    "promptTokens": 0,
                    "cachedPromptTokens": 0,
                    "reasoningTokens": 0,
                    "completionTokens": 0,
                    "totalTokens": 0,
                    "costUsd": 0,
                    "elapsedMs": 0,
                    "finishReason": "stop",
                    "outputCharacters": len(accepted_text),
                    "trailingWhitespaceCharacters": 0,
                    "validationClass": "accepted",
                    "retryCause": None,
                    "entityCounts": {
                        "contributions": len(SUBJECTS),
                        "programs": len(
                            transcript["steps"][-1]["knowledgeAfter"]["programs"]
                        ),
                        "intermediate-results": len(
                            transcript["steps"][-1]["knowledgeAfter"][
                                "intermediateResults"
                            ]
                        ),
                    },
                },
            }
        ],
        "outputs": [
            {
                "id": "transcript",
                "mediaType": "application/json",
                "path": f"{RELATIVE_DIR.as_posix()}/transcript.json",
                "digest": transcript_digest,
            }
        ],
    }
    fixture_digest = _write(target / "replay" / "fixture.json", fixture)
    manifest = {
        "schemaVersion": 1,
        "id": "miniature-e2e-protocol-v1",
        "description": (
            "Provider-free replay of an eight-submission synthetic history through "
            "scoped V10 knowledge formation and the actual captured V2 request, "
            "A-first bundle, loader, and hierarchical work-accounting path."
        ),
        "problemId": PROBLEM_ID,
        "ledgerHead": SUBJECTS[-1],
        "publicationForbidden": True,
        "execution": {"adapter": "fixture-replay-v1"},
        "variants": [
            {
                "id": "reference-reducer-history",
                "description": (
                    "The precommitted deterministic miniature reference history with "
                    "fixture-local V2 request captures and zero external calls."
                ),
            }
        ],
        "seeds": [0],
        "budgets": {
            "maximumProviderCalls": 0,
            "maximumStageAttempts": 1,
            "maximumPromptTokens": 0,
            "maximumCompletionTokens": 0,
            "maximumTotalTokens": 0,
            "maximumCostUsd": 0,
        },
        "frozenInputs": [
            {
                "id": "miniature-oracle",
                "path": f"{RELATIVE_DIR.as_posix()}/oracle.json",
                "digest": oracle_digest,
                "mediaType": "application/json",
            },
            *candidate_inputs,
        ],
        "steps": [
            {
                "id": "history",
                "stages": [
                    {
                        "id": "replay",
                        "adapter": "fixture-replay-v1",
                        "reads": [
                            "miniature-oracle",
                            "knowledge-builder-spec",
                            "work-accounting-spec",
                            "work-accounting-policy",
                        ],
                        "outputs": ["transcript"],
                        "fixtures": [
                            {
                                "variant": "reference-reducer-history",
                                "seed": 0,
                                "path": f"{RELATIVE_DIR.as_posix()}/replay/fixture.json",
                                "digest": fixture_digest,
                            }
                        ],
                    }
                ],
            }
        ],
        "scorers": [
            {
                "id": "knowledge-work-e2e",
                "implementation": "miniature-e2e-v1",
                "goldInputId": "miniature-oracle",
            }
        ],
    }
    manifest_digest = _write(target / "scenario-v1.json", manifest)
    return {
        "transcriptDigest": transcript_digest,
        "oracleDigest": oracle_digest,
        "fixtureDigest": fixture_digest,
        "manifestDigest": manifest_digest,
        "score": score,
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Regenerate the provider-free miniature E2E scenario fixture."
    )
    parser.add_argument(
        "--destination-root",
        type=Path,
        default=Path(__file__).resolve().parents[1],
    )
    args = parser.parse_args()
    result = write_miniature_e2e_fixture(args.destination_root)
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
