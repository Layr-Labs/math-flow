from __future__ import annotations

import copy
import base64
import json
import unittest
from pathlib import Path

from math_flow.artifacts import sha256_bytes
from math_flow.errors import MathFlowError
from math_flow.governed_providers import GovernedProviderTerminalError
from math_flow.research_builder_v7 import empty_research_program_state_v3
from math_flow.research_builder_v10_provider import (
    OpenRouterResearchBuilderV10Provider,
    _builder_transition_schema_v10,
    _normalize_v10_transition,
    _route_plan_schema_v10,
)
from math_flow.work_projection import SubmissionEvidenceFile


ROOT = Path(__file__).resolve().parents[1]
SPEC = (
    ROOT
    / "protocol/judges/openrouter-hierarchical-research-builder-v10-experiment.json"
)
SUBJECT = "a" * 40
JUDGMENT = "sha256:" + "1" * 64
EVIDENCE_PATH = "problems/two-entity-fixture/contributions/a/README.md"
EVIDENCE = b"# Accepted local result\n"


def assert_openai_strict_schema(test: unittest.TestCase, schema: object) -> None:
    pending = [schema]
    while pending:
        node = pending.pop()
        if isinstance(node, dict):
            for unsupported in ("oneOf", "uniqueItems", "minProperties"):
                test.assertNotIn(unsupported, node)
            if node.get("type") == "object":
                properties = node.get("properties")
                test.assertIsInstance(properties, dict)
                test.assertIs(node.get("additionalProperties"), False)
                test.assertEqual(set(node.get("required", [])), set(properties))
            pending.extend(node.values())
        elif isinstance(node, list):
            pending.extend(node)


def accepted_claims() -> list[dict[str, object]]:
    return [
        {
            "claimKey": "accepted-local-result",
            "declaredStatement": "A restricted local result is established.",
            "validitySummary": "The restricted local result is established.",
            "scopeQualifications": ["Only the restricted setting is covered."],
            "evidenceTransactionIds": [],
            "dependencyTransactionIds": [],
        }
    ]


class SequentialTransport:
    def __init__(self, values: list[dict[str, object]]) -> None:
        self.values = list(values)
        self.requests: list[dict[str, object]] = []

    def __call__(self, request: dict[str, object]) -> dict[str, object]:
        self.requests.append(copy.deepcopy(request))
        value = self.values.pop(0)
        return {
            "id": f"response-{len(self.requests)}",
            "model": "openai/gpt-5.6-sol",
            "choices": [
                {
                    "finish_reason": "stop",
                    "message": {"content": json.dumps(value)},
                }
            ],
        }


class ResearchBuilderV10ProviderTests(unittest.TestCase):
    def test_experiment_prompt_preserves_accounting_boundary_controls(self) -> None:
        spec = json.loads(SPEC.read_text(encoding="utf-8"))
        system_prompt = spec["systemPrompt"]
        route_prompt = spec["stagePrompts"]["route"]
        refine_prompt = spec["stagePrompts"]["route-refine"]

        self.assertIn("author-blind intervention test", system_prompt)
        self.assertIn("independent activation or stopping condition", system_prompt)
        self.assertIn("does not by itself establish accounting ancestry", system_prompt)
        self.assertIn("Root is the correct parent", system_prompt)
        self.assertIn("same-world no-access work package", system_prompt)
        self.assertIn("with-access remaining work becomes zero", system_prompt)
        self.assertIn("author-blind work-policy intervention test", route_prompt)
        self.assertIn("conditionally part of that parent's work policy", route_prompt)
        self.assertIn("same-world no-access work package", route_prompt)
        self.assertIn("broad topical umbrella", refine_prompt)
        self.assertIn("mathematical or evidentiary dependency never establishes", refine_prompt)
        self.assertEqual(spec["stages"]["route"]["parameters"]["max_tokens"], 6000)
        self.assertEqual(
            spec["stages"]["route-refine"]["parameters"]["max_tokens"], 4000
        )

    def test_route_refine_author_keeps_raw_evidence_out_of_routing(self) -> None:
        base = empty_research_program_state_v3("two-entity-fixture")
        route_context_digest = None

        def route_plan() -> dict[str, object]:
            assert route_context_digest is not None
            return {
                "schemaVersion": 1,
                "baseStateDigest": base["stateDigest"],
                "routeContextDigest": route_context_digest,
                "inspectProgramIds": ["root"],
                "inspectResultIds": [],
                "searchQueries": [],
                "writeProgramIds": ["root"],
                "writeResultIds": [],
                "createProgramIds": ["program/local"],
                "createResultIds": ["result/local"],
            }

        root = {
            key: copy.deepcopy(value)
            for key, value in base["programs"]["root"].items()
            if key != "digest"
        }
        root["currentStateSummary"] = "One restricted local result is established."
        root["localResidualSummary"] = "The canonical objective remains open."
        root["sourceTransactionIds"] = [SUBJECT]
        root.pop("intermediateResultIds")
        root["intermediateResultIdAdditions"] = []
        root["intermediateResultIdRemovals"] = []
        author = {
            "schemaVersion": 1,
            "subjectTransactionId": SUBJECT,
            "baseStateDigest": base["stateDigest"],
            "contentOperations": [
                {
                    "entityKind": "program",
                    "entityId": "root",
                    "baseDigest": None,
                    "value": root,
                }
            ],
            "topologyOperations": [
                {
                    "action": "create",
                    "entityKind": "program",
                    "entityId": "program/local",
                    "baseDigest": None,
                    "value": {
                        "id": "program/local",
                        "parentId": "root",
                        "title": "Restricted local program",
                        "objective": "Resolve the restricted local objective.",
                        "currentStateSummary": "One restricted result is established.",
                        "localResidualSummary": "The unrestricted extension remains open.",
                        "status": "active",
                        "intermediateResultIdAdditions": ["result/local"],
                        "intermediateResultIdRemovals": [],
                        "sourceTransactionIds": [SUBJECT],
                        "lineage": [],
                    },
                },
                {
                    "action": "create",
                    "entityKind": "intermediateResult",
                    "entityId": "result/local",
                    "baseDigest": None,
                    "value": {
                        "id": "result/local",
                        "primaryProgramId": "program/local",
                        "relatedProgramIds": [],
                        "title": "Restricted local result",
                        "statement": "The restricted local result is established.",
                        "scopeQualifications": [
                            "Only the restricted setting is covered."
                        ],
                        "supportAdditions": {
                            "proofs": ["The submitted proof establishes the result."],
                            "methods": [],
                            "computations": [],
                            "tools": [],
                            "artifactPaths": [EVIDENCE_PATH],
                            "attestationRefs": [],
                        },
                        "dependencyResultIds": [],
                        "claimRefs": [
                            {
                                "transactionId": SUBJECT,
                                "claimKey": "accepted-local-result",
                            }
                        ],
                        "sourceTransactionIds": [SUBJECT],
                        "judgmentIds": [],
                        "status": "active",
                        "supersededByResultIds": [],
                    },
                },
            ],
            "contribution": {
                "claimKeys": ["accepted-local-result"],
                "directProgramIds": ["program/local"],
                "intermediateResultIds": ["result/local"],
            },
            "placementAudit": {
                "rationale": "The claim establishes a durable local objective."
            },
            "topologyRationale": "Create one independently accountable local program.",
        }

        # The route digest is reducer-derived, so build one provider solely to
        # materialize it before installing the deterministic transport.
        from math_flow.research_builder_v10 import (
            build_research_builder_v10_route_context,
        )

        route_context_digest = build_research_builder_v10_route_context(
            base, accepted_claims()
        )["contextDigest"]
        transport = SequentialTransport([route_plan(), route_plan(), author])
        provider = OpenRouterResearchBuilderV10Provider(
            json.loads(SPEC.read_text(encoding="utf-8")), transport=transport
        )
        transition = provider.run(
            problem_id="two-entity-fixture",
            subject_transaction_id=SUBJECT,
            base_state=base,
            accepted_claims=accepted_claims(),
            judgment_id=JUDGMENT,
            evidence_files=(
                SubmissionEvidenceFile(
                    EVIDENCE_PATH, sha256_bytes(EVIDENCE), EVIDENCE
                ),
            ),
        )
        self.assertEqual(len(transport.requests), 3)
        self.assertEqual(
            [record["stage"] for record in provider.invocation_records],
            ["route", "route-refine", "organize"],
        )
        route_payloads = json.dumps(transport.requests[:2], sort_keys=True)
        self.assertNotIn("contentBase64", route_payloads)
        self.assertNotIn(EVIDENCE.decode().strip(), route_payloads)
        author_payload = json.dumps(transport.requests[2], sort_keys=True)
        self.assertIn("contentBase64", author_payload)
        self.assertIn(base64.b64encode(EVIDENCE).decode(), author_payload)
        result = transition["topologyOperations"][1]["value"]
        self.assertEqual(result["judgmentIds"], [JUDGMENT])
        self.assertEqual(
            result["support"]["artifactRefs"],
            [{"path": EVIDENCE_PATH, "digest": sha256_bytes(EVIDENCE)}],
        )
        self.assertIsNotNone(provider.latest_artifacts)

    def test_terminal_transport_outcome_suppresses_duplicate_provider_calls(self) -> None:
        base = empty_research_program_state_v3("two-entity-fixture")
        calls: list[dict[str, object]] = []
        journals: list[dict[str, object]] = []

        def transport(request: dict[str, object]) -> dict[str, object]:
            calls.append(copy.deepcopy(request))
            raise GovernedProviderTerminalError(
                "provider cost telemetry is unknown; further spending is blocked"
            )

        provider = OpenRouterResearchBuilderV10Provider(
            json.loads(SPEC.read_text(encoding="utf-8")),
            transport=transport,
            attempt_journal_writer=journals.append,
        )
        with self.assertRaisesRegex(
            MathFlowError,
            r"stopped after 1 automatic attempt; further retries were suppressed",
        ):
            provider.run(
                problem_id="two-entity-fixture",
                subject_transaction_id=SUBJECT,
                base_state=base,
                accepted_claims=accepted_claims(),
                judgment_id=JUDGMENT,
                evidence_files=(
                    SubmissionEvidenceFile(
                        EVIDENCE_PATH, sha256_bytes(EVIDENCE), EVIDENCE
                    ),
                ),
            )

        self.assertEqual(len(calls), 1)
        self.assertEqual(len(journals), 1)
        self.assertEqual(len(journals[0]["attemptRecords"]), 1)
        self.assertEqual(
            journals[0]["attemptRecords"][0]["outcome"], "transport-rejected"
        )

    def test_program_link_patch_restores_hidden_links_and_supports_removal(self) -> None:
        prior_ids = [f"result/prior-{index}" for index in range(12)]
        base = {
            "programs": {
                "program/local": {
                    "digest": "sha256:" + "a" * 64,
                    "intermediateResultIds": prior_ids,
                    "sourceTransactionIds": ["b" * 40],
                }
            },
            "intermediateResults": {},
            "contributions": {},
        }
        transition = {
            "topologyOperations": [],
            "contentOperations": [
                {
                    "entityKind": "program",
                    "entityId": "program/local",
                    "baseDigest": None,
                    "value": {
                        "sourceTransactionIds": [SUBJECT],
                        "intermediateResultIdAdditions": ["result/current"],
                        "intermediateResultIdRemovals": ["result/prior-3"],
                    },
                }
            ],
        }
        normalized = _normalize_v10_transition(
            transition,
            base_state=base,
            subject_transaction_id=SUBJECT,
            judgment_id=JUDGMENT,
            evidence_by_path={},
        )
        value = normalized["contentOperations"][0]["value"]
        self.assertEqual(len(value["intermediateResultIds"]), 12)
        self.assertIn("result/current", value["intermediateResultIds"])
        self.assertNotIn("result/prior-3", value["intermediateResultIds"])
        self.assertEqual(value["sourceTransactionIds"], [SUBJECT, "b" * 40])

        schema = _builder_transition_schema_v10()
        rendered = json.dumps(schema, sort_keys=True)
        self.assertIn("intermediateResultIdAdditions", rendered)
        self.assertIn("intermediateResultIdRemovals", rendered)

        route_schema_value = _route_plan_schema_v10(
            base_state_digest="sha256:" + "a" * 64,
            route_context_digest="sha256:" + "b" * 64,
        )
        assert_openai_strict_schema(self, route_schema_value)
        assert_openai_strict_schema(self, schema)
        route_schema = json.dumps(route_schema_value, sort_keys=True)
        self.assertNotIn("uniqueItems", route_schema)


if __name__ == "__main__":
    unittest.main()
