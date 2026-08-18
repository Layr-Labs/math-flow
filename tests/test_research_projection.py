from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from math_flow.judgments import run_primary_judgment_bundle
from math_flow.errors import MathFlowError
from math_flow.judges import load_source
from math_flow.research_projection import (
    load_research_credit_refresh_bundle,
    load_research_update_bundle,
    run_research_credit_refresh_bundle,
    run_research_update_bundle,
)
from math_flow.validity import research_state_dependency_context


ROOT = Path(__file__).resolve().parents[1]
PROBLEM = "bssc-sum-capacity"
TX = "d638c346212db3e75f6a53dcebcfd09f55125852"


def response(content: str, index: int) -> dict[str, object]:
    return {
        "id": f"response-{index}",
        "model": "openai/gpt-5.6-sol",
        "usage": {"prompt_tokens": 1, "completion_tokens": 1},
        "choices": [
            {"finish_reason": "stop", "message": {"content": content}}
        ],
    }


class ResearchProjectionTests(unittest.TestCase):
    def test_validity_to_program_state_and_credit_bundle(self) -> None:
        calls: list[dict[str, object]] = []

        def fake_transport(request: dict[str, object]) -> dict[str, object]:
            calls.append(request)
            schema = (
                request.get("response_format", {})
                .get("json_schema", {})
                .get("schema")
            )
            if schema is None:
                return response(
                    "# Rigorous audit\n\nEvery stated obligation was checked in this fixture.",
                    len(calls),
                )
            properties = schema["properties"]
            if "assessments" in properties:
                claim_keys = properties["assessments"]["items"]["properties"][
                    "claimKey"
                ]["enum"]
                value = {
                    "assessments": [
                        {
                            "claimKey": claim_key,
                            "status": "valid",
                            "premiseStatus": "not-required",
                            "summary": "The fixture accepts the exact declared claim.",
                            "scopeQualifications": [],
                            "evidenceIssues": [],
                            "evidenceTransactionIds": [],
                        }
                        for claim_key in claim_keys
                    ]
                }
                return response(json.dumps(value), len(calls))
            if "contribution" in properties:
                claim_keys = properties["contribution"]["properties"][
                    "claimKeys"
                ]["items"]["enum"]
                value = {
                    "schemaVersion": 1,
                    "operations": [
                        {
                            "entityKind": "thread",
                            "entityId": "root/gk-reduction",
                            "baseDigest": None,
                            "value": {
                                "id": "root/gk-reduction",
                                "programId": "root",
                                "title": "Auxiliary receiver reduction",
                                "summary": "Develop the structural converse reduction.",
                                "kind": "research",
                                "status": "active",
                                "expectedExposure": "4",
                                "conditions": [],
                                "sourceTransactionIds": [TX],
                            },
                        },
                        {
                            "entityKind": "item",
                            "entityId": "root/gk-foundations-result",
                            "baseDigest": None,
                            "value": {
                                "id": "root/gk-foundations-result",
                                "programId": "root",
                                "type": "result",
                                "title": "Gohari–Kramer foundations",
                                "summary": "The exact accepted structural and finite-grid result.",
                                "claimRefs": [
                                    {"transactionId": TX, "claimKey": claim_keys[0]}
                                ],
                                "sourceTransactionIds": [TX],
                                "dependencyItemIds": [],
                            },
                        },
                        {
                            "entityKind": "item",
                            "entityId": "root/gk-foundations-method",
                            "baseDigest": None,
                            "value": {
                                "id": "root/gk-foundations-method",
                                "programId": "root",
                                "type": "method",
                                "title": "Posterior-grid reduction method",
                                "summary": "The reusable method separated from the result.",
                                "claimRefs": [],
                                "sourceTransactionIds": [TX],
                                "dependencyItemIds": ["root/gk-foundations-result"],
                            },
                        },
                    ],
                    "contribution": {
                        "claimKeys": claim_keys,
                        "directProgramId": "root",
                        "directThreadIds": ["root/gk-reduction"],
                        "itemIds": [
                            "root/gk-foundations-result",
                            "root/gk-foundations-method",
                        ],
                    },
                }
                return response(json.dumps(value), len(calls))
            value = {
                "schemaVersion": 1,
                "evaluations": [
                    {
                        "programId": "root",
                        "unattributedWork": "1",
                        "rationale": "Some local causal value remains unassigned.",
                        "children": [
                            {
                                "kind": "contribution",
                                "id": TX,
                                "counterfactual": "Remove the accepted reduction and adapt from the same problem.",
                                "directEffects": [
                                    {
                                        "threadId": "root/gk-reduction",
                                        "withoutWork": "5",
                                        "withWork": "2",
                                        "rationale": "The accepted reduction saves three units locally.",
                                    }
                                ],
                                "obviatedEffects": [
                                    {
                                        "threadId": "root/unstructured-search",
                                        "withoutWork": "1",
                                        "withWork": "0.5",
                                        "rationale": "It narrows otherwise unstructured search.",
                                    }
                                ],
                                "confidence": "medium",
                                "evidenceRefs": [TX],
                            }
                        ],
                    }
                ],
            }
            return response(json.dumps(value), len(calls))

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            validity_dir = root / "validity"
            research_dir = root / "research"
            refresh_dir = root / "refresh"
            run_primary_judgment_bundle(
                ROOT,
                PROBLEM,
                ROOT / "protocol/judges/openrouter-validity-judgment-v2.json",
                TX,
                [TX],
                validity_dir,
                projection_root=None,
                transport=fake_transport,
            )
            run_research_update_bundle(
                ROOT,
                PROBLEM,
                ROOT / "protocol/judges/openrouter-hierarchical-research-v1.json",
                TX,
                validity_dir,
                research_dir,
                transport=fake_transport,
            )
            manifest, state, credit, _ = load_research_update_bundle(research_dir)
            run_research_credit_refresh_bundle(
                ROOT,
                PROBLEM,
                ROOT / "protocol/judges/openrouter-hierarchical-research-v1.json",
                research_dir,
                [research_dir],
                refresh_dir,
                transport=fake_transport,
            )
            refresh_manifest, refresh_state, refresh_credit, _ = (
                load_research_credit_refresh_bundle(refresh_dir)
            )
            context = research_state_dependency_context(
                research_dir,
                PROBLEM,
                load_source(
                    ROOT,
                    PROBLEM,
                    "f236017c62c67ce4218c1f81ea34134f0954b556",
                ),
                4,
                [TX],
            )

        self.assertEqual(len(calls), 5)
        self.assertEqual(manifest["runKind"], "research-update")
        self.assertEqual(state["ledgerHead"], TX)
        self.assertEqual(state["contributions"][TX]["directProgramId"], "root")
        self.assertEqual(len(state["contributions"][TX]["claimKeys"]), 1)
        self.assertEqual(
            credit["evaluations"]["root"]["children"][0]["totalWork"],
            "3.5",
        )
        self.assertEqual(refresh_manifest["runKind"], "research-credit-refresh")
        self.assertEqual(refresh_state["stateDigest"], state["stateDigest"])
        self.assertEqual(
            refresh_credit["evaluations"]["root"]["children"][0][
                "horizonStateDigest"
            ],
            state["stateDigest"],
        )
        self.assertEqual(context["sourceKind"], "research-program-state")
        self.assertEqual(context["unresolvedDependencyTransactionIds"], [])
        self.assertIn("root/gk-foundations-result", context["selectedItems"])

    def test_invalid_submission_has_no_research_state_transition(self) -> None:
        calls = 0

        def fake_transport(request: dict[str, object]) -> dict[str, object]:
            nonlocal calls
            calls += 1
            schema = (
                request.get("response_format", {})
                .get("json_schema", {})
                .get("schema")
            )
            if schema is None:
                return response("# Audit\n\nA decisive fixture defect is present.", calls)
            claim_keys = schema["properties"]["assessments"]["items"][
                "properties"
            ]["claimKey"]["enum"]
            return response(
                json.dumps(
                    {
                        "assessments": [
                            {
                                "claimKey": key,
                                "status": "invalid",
                                "premiseStatus": "not-required",
                                "summary": "A decisive fixture defect defeats the claim.",
                                "scopeQualifications": [],
                                "evidenceIssues": ["Fixture defect."],
                                "evidenceTransactionIds": [],
                            }
                            for key in claim_keys
                        ]
                    }
                ),
                calls,
            )

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            validity_dir = root / "validity"
            run_primary_judgment_bundle(
                ROOT,
                PROBLEM,
                ROOT / "protocol/judges/openrouter-validity-judgment-v2.json",
                TX,
                [TX],
                validity_dir,
                projection_root=None,
                transport=fake_transport,
            )
            with self.assertRaisesRegex(MathFlowError, "no valid claims remain"):
                run_research_update_bundle(
                    ROOT,
                    PROBLEM,
                    ROOT
                    / "protocol/judges/openrouter-hierarchical-research-v1.json",
                    TX,
                    validity_dir,
                    root / "research",
                    transport=fake_transport,
                )
        self.assertEqual(calls, 2)


if __name__ == "__main__":
    unittest.main()
