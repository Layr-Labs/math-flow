from __future__ import annotations

import copy
import json
import unittest
from pathlib import Path

from math_flow.artifacts import sha256_bytes
from math_flow.errors import MathFlowError
from math_flow.governed_providers import (
    OpenRouterResearchBuilderV9Provider,
    _builder_transition_schema_v9,
)
from math_flow.research_builder_v7 import empty_research_program_state_v3
from math_flow.research_builder_v8 import apply_research_builder_v8_transition
from math_flow.research_builder_v9 import (
    build_research_builder_v9_context,
    validate_research_builder_v9_context,
)
from math_flow.repository import sha256_json
from math_flow.work_projection import SubmissionEvidenceFile


ROOT = Path(__file__).resolve().parents[1]
SPEC = ROOT / "protocol/judges/openrouter-hierarchical-research-builder-v9.json"
TX_A = "a" * 40
TX_B = "b" * 40
TX_C = "c" * 40
JUDGMENT_A = "sha256:" + "1" * 64
JUDGMENT_B = "sha256:" + "2" * 64
JUDGMENT_C = "sha256:" + "3" * 64
PATH_A = "problems/two-entity-fixture/contributions/a/README.md"
PATH_B = "problems/two-entity-fixture/contributions/b/README.md"
PATH_C = "problems/two-entity-fixture/contributions/c/README.md"
CONTENT_A = b"# A\n"
CONTENT_B = b"# B\n"
CONTENT_C = b"# C\n"


def accepted(
    claim_key: str, dependencies: list[str] | None = None
) -> list[dict[str, object]]:
    return [
        {
            "claimKey": claim_key,
            "declaredStatement": "The contributor's declared statement.",
            "validitySummary": "The exact restricted statement is established.",
            "scopeQualifications": ["Restricted scope."],
            "evidenceTransactionIds": [],
            "dependencyTransactionIds": sorted(dependencies or []),
        }
    ]


def without_digest(value: dict[str, object]) -> dict[str, object]:
    return {key: copy.deepcopy(item) for key, item in value.items() if key != "digest"}


def append_result_transition(
    base: dict[str, object],
    *,
    subject: str,
    claim_key: str,
    judgment_id: str,
    result_id: str,
    artifact_path: str,
    artifact_digest: str,
    dependency_transactions: list[str] | None = None,
    dependency_results: list[str] | None = None,
) -> dict[str, object]:
    root = without_digest(base["programs"]["root"])
    root["currentStateSummary"] = "Two exact restricted results are established."
    root["localResidualSummary"] = "The unrestricted objective remains open."
    root["sourceTransactionIds"] = sorted(
        [*root["sourceTransactionIds"], subject]
    )
    existing_program = base["programs"].get("program/local")
    if isinstance(existing_program, dict):
        program = without_digest(existing_program)
        program["currentStateSummary"] = "Two local restricted results are established."
        program["intermediateResultIds"] = sorted(
            [*program["intermediateResultIds"], result_id]
        )
        program["sourceTransactionIds"] = sorted(
            [*program["sourceTransactionIds"], subject]
        )
        program_base_digest = existing_program["digest"]
    else:
        program = {
            "id": "program/local",
            "parentId": "root",
            "title": "Restricted local program",
            "objective": "Resolve the restricted local objective.",
            "currentStateSummary": "One local restricted result is established.",
            "localResidualSummary": "The unrestricted extension remains open.",
            "status": "active",
            "intermediateResultIds": [result_id],
            "sourceTransactionIds": [subject],
            "lineage": [],
        }
        program_base_digest = None
    result = {
        "id": result_id,
        "primaryProgramId": "program/local",
        "relatedProgramIds": [],
        "title": f"Result {result_id}",
        "statement": f"The exact statement for {result_id} is established.",
        "scopeQualifications": ["Restricted scope."],
        "support": {
            "proofs": [f"Hidden proof for {result_id}."],
            "methods": [],
            "computations": [],
            "tools": [],
            "artifactRefs": [{"path": artifact_path, "digest": artifact_digest}],
            "attestationRefs": [],
        },
        "dependencyResultIds": sorted(dependency_results or []),
        "claimRefs": [{"transactionId": subject, "claimKey": claim_key}],
        "sourceTransactionIds": [subject],
        "judgmentIds": [judgment_id],
        "status": "active",
        "supersededByResultIds": [],
    }
    return {
        "schemaVersion": 1,
        "subjectTransactionId": subject,
        "baseStateDigest": base["stateDigest"],
        "contentOperations": [
            {
                "entityKind": "program",
                "entityId": "root",
                "baseDigest": base["programs"]["root"]["digest"],
                "value": root,
            },
            {
                "entityKind": "program",
                "entityId": "program/local",
                "baseDigest": program_base_digest,
                "value": program,
            },
            {
                "entityKind": "intermediateResult",
                "entityId": result_id,
                "baseDigest": None,
                "value": result,
            },
        ],
        "topologyOperations": [],
        "contribution": {
            "claimKeys": [claim_key],
            "directProgramIds": ["program/local"],
            "intermediateResultIds": [result_id],
        },
        "placementAudit": {
            "basis": "local-objective",
            "rationale": "The result concerns a durable local objective.",
            "relatedProgramIds": ["program/local"],
        },
        "topologyRationale": None,
    }


class Transport:
    def __init__(self, value: object):
        self.value = value
        self.requests: list[dict[str, object]] = []

    def __call__(self, request: dict[str, object]) -> dict[str, object]:
        self.requests.append(copy.deepcopy(request))
        return {
            "id": "response-v9",
            "model": "openai/gpt-5.6-sol",
            "choices": [
                {
                    "finish_reason": "stop",
                    "message": {"content": json.dumps(self.value)},
                }
            ],
        }


class ResearchBuilderV9Tests(unittest.TestCase):
    def setUp(self) -> None:
        empty = empty_research_program_state_v3("two-entity-fixture")
        first_transition = append_result_transition(
            empty,
            subject=TX_A,
            claim_key="claim-a",
            judgment_id=JUDGMENT_A,
            result_id="result/a",
            artifact_path=PATH_A,
            artifact_digest=sha256_bytes(CONTENT_A),
        )
        self.first = apply_research_builder_v8_transition(
            empty,
            first_transition,
            accepted_claims=accepted("claim-a"),
            judgment_id=JUDGMENT_A,
            evidence_file_refs={PATH_A: sha256_bytes(CONTENT_A)},
        )["postState"]
        second_transition = append_result_transition(
            self.first,
            subject=TX_B,
            claim_key="claim-b",
            judgment_id=JUDGMENT_B,
            result_id="result/b",
            artifact_path=PATH_B,
            artifact_digest=sha256_bytes(CONTENT_B),
        )
        self.base = apply_research_builder_v8_transition(
            self.first,
            second_transition,
            accepted_claims=accepted("claim-b"),
            judgment_id=JUDGMENT_B,
            evidence_file_refs={PATH_B: sha256_bytes(CONTENT_B)},
        )["postState"]

    def test_context_keeps_all_result_cores_and_loads_dependency_support(self) -> None:
        context = build_research_builder_v9_context(
            self.base, accepted("claim-c", [TX_A])
        )
        validate_research_builder_v9_context(
            context,
            base_state=self.base,
            accepted_claims=accepted("claim-c", [TX_A]),
        )
        self.assertEqual(context["supportLoadedResultIds"], ["result/a"])
        self.assertEqual(context["supportOmittedResultIds"], ["result/b"])
        self.assertIn("statement", context["intermediateResults"]["result/b"])
        self.assertIsNone(context["intermediateResults"]["result/b"]["support"])
        loaded_support = context["intermediateResults"]["result/a"]["support"]
        self.assertEqual(loaded_support["artifactPaths"], [PATH_A])
        self.assertNotIn(sha256_bytes(CONTENT_A), json.dumps(context))
        self.assertNotIn("digest", context["programs"]["root"])

    def test_context_loads_transitive_result_dependency_closure(self) -> None:
        empty = empty_research_program_state_v3("two-entity-fixture")
        first_transition = append_result_transition(
            empty,
            subject=TX_A,
            claim_key="claim-a",
            judgment_id=JUDGMENT_A,
            result_id="result/a",
            artifact_path=PATH_A,
            artifact_digest=sha256_bytes(CONTENT_A),
        )
        first = apply_research_builder_v8_transition(
            empty,
            first_transition,
            accepted_claims=accepted("claim-a"),
            judgment_id=JUDGMENT_A,
            evidence_file_refs={PATH_A: sha256_bytes(CONTENT_A)},
        )["postState"]
        second_transition = append_result_transition(
            first,
            subject=TX_B,
            claim_key="claim-b",
            judgment_id=JUDGMENT_B,
            result_id="result/b",
            artifact_path=PATH_B,
            artifact_digest=sha256_bytes(CONTENT_B),
            dependency_transactions=[TX_A],
            dependency_results=["result/a"],
        )
        second = apply_research_builder_v8_transition(
            first,
            second_transition,
            accepted_claims=accepted("claim-b", [TX_A]),
            judgment_id=JUDGMENT_B,
            evidence_file_refs={PATH_B: sha256_bytes(CONTENT_B)},
        )["postState"]
        context = build_research_builder_v9_context(
            second, accepted("claim-c", [TX_B])
        )
        self.assertEqual(
            context["supportLoadedResultIds"], ["result/a", "result/b"]
        )

    def test_provider_preserves_hidden_support_and_sends_no_full_state(self) -> None:
        root = without_digest(self.base["programs"]["root"])
        root["currentStateSummary"] = "Result B is strengthened."
        root["sourceTransactionIds"] = [TX_C]
        program = without_digest(self.base["programs"]["program/local"])
        program["currentStateSummary"] = "Local result B is strengthened."
        program["sourceTransactionIds"] = [TX_C]
        result = without_digest(self.base["intermediateResults"]["result/b"])
        result.pop("support")
        result.update(
            {
                "statement": "The exact statement for result B is strengthened.",
                "claimRefs": [{"transactionId": TX_C, "claimKey": "claim-c"}],
                "sourceTransactionIds": [TX_C],
                "judgmentIds": [],
                "supportAdditions": {
                    "proofs": [],
                    "methods": ["A new strengthening method."],
                    "computations": [],
                    "tools": [],
                    "artifactPaths": [PATH_C],
                    "attestationRefs": [],
                },
            }
        )
        response = {
            "schemaVersion": 1,
            "subjectTransactionId": TX_C,
            "baseStateDigest": self.base["stateDigest"],
            "contentOperations": [
                {"entityKind": "program", "entityId": "root", "baseDigest": None, "value": root},
                {"entityKind": "program", "entityId": "program/local", "baseDigest": None, "value": program},
                {"entityKind": "intermediateResult", "entityId": "result/b", "baseDigest": None, "value": result},
            ],
            "topologyOperations": [],
            "contribution": {"claimKeys": ["claim-c"], "directProgramIds": ["program/local"], "intermediateResultIds": ["result/b"]},
            "placementAudit": {"rationale": "The strengthening concerns the local objective."},
            "topologyRationale": "No topology change.",
        }
        transport = Transport(response)
        provider = OpenRouterResearchBuilderV9Provider(
            json.loads(SPEC.read_text(encoding="utf-8")), transport=transport
        )
        output = provider.run(
            problem_id="two-entity-fixture",
            subject_transaction_id=TX_C,
            base_state=self.base,
            accepted_claims=accepted("claim-c"),
            judgment_id=JUDGMENT_C,
            evidence_files=(
                SubmissionEvidenceFile(PATH_C, sha256_bytes(CONTENT_C), CONTENT_C),
            ),
        )
        support = output["contentOperations"][2]["value"]["support"]
        self.assertIn("Hidden proof for result/b.", support["proofs"])
        self.assertIn("A new strengthening method.", support["methods"])
        self.assertEqual(
            support["artifactRefs"],
            [
                {"path": PATH_B, "digest": sha256_bytes(CONTENT_B)},
                {"path": PATH_C, "digest": sha256_bytes(CONTENT_C)},
            ],
        )
        payload_text = str(transport.requests[0]["messages"][-1]["content"])
        payload = json.loads(
            payload_text.split("<math-flow-input>\n", 1)[1].split(
                "\n</math-flow-input>", 1
            )[0]
        )
        self.assertNotIn("baseState", payload)
        self.assertIn("baseStateContext", payload)
        self.assertNotIn("Hidden proof for result/b.", payload_text)
        self.assertIsNone(
            payload["baseStateContext"]["intermediateResults"]["result/b"]["support"]
        )

    def test_context_tampering_fails_closed(self) -> None:
        context = build_research_builder_v9_context(
            self.base, accepted("claim-c", [TX_A])
        )
        context["intermediateResults"]["result/b"]["support"] = {
            "proofs": ["Injected"],
            "methods": [],
            "computations": [],
            "tools": [],
            "artifactPaths": [],
            "attestationRefs": [],
        }
        with self.assertRaisesRegex(MathFlowError, "digest mismatch"):
            validate_research_builder_v9_context(context)

        malformed_selection = build_research_builder_v9_context(
            self.base, accepted("claim-c", [TX_A])
        )
        malformed_selection["supportLoadedResultIds"] = [{}]
        core = {
            key: value
            for key, value in malformed_selection.items()
            if key != "contextDigest"
        }
        malformed_selection["contextDigest"] = "sha256:" + sha256_json(core)
        with self.assertRaisesRegex(MathFlowError, "selection is invalid"):
            validate_research_builder_v9_context(malformed_selection)

    def test_v9_schema_uses_support_additions_and_profile_binds_context(self) -> None:
        rendered = json.dumps(_builder_transition_schema_v9(), sort_keys=True)
        self.assertIn("supportAdditions", rendered)
        self.assertNotIn('"support":', rendered)
        profile = json.loads(
            (ROOT / "protocol/profiles/hierarchical-research-v9.json").read_text()
        )
        self.assertIn("research-builder-context", profile["requiredArtifactRoles"])
        self.assertIn(
            "protocol/schemas/research-builder-context-v1.schema.json",
            profile["schemas"],
        )


if __name__ == "__main__":
    unittest.main()
