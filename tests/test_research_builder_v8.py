from __future__ import annotations

import copy
import json
import unittest
from pathlib import Path

from math_flow.artifacts import sha256_bytes
from math_flow.errors import MathFlowError
from math_flow.governed_providers import (
    OpenRouterResearchBuilderV8Provider,
    _builder_transition_schema_v8,
)
from math_flow.research_builder_v7 import empty_research_program_state_v3
from math_flow.research_builder_v8 import apply_research_builder_v8_transition
from math_flow.work_projection import SubmissionEvidenceFile


ROOT = Path(__file__).resolve().parents[1]
SPEC = ROOT / "protocol/judges/openrouter-hierarchical-research-builder-v8.json"
TX_A = "a" * 40
TX_B = "b" * 40
TX_C = "c" * 40
JUDGMENT_A = "sha256:" + "1" * 64
JUDGMENT_B = "sha256:" + "2" * 64
PATH_A = "problems/two-entity-fixture/contributions/a/README.md"
PATH_B = "problems/two-entity-fixture/contributions/b/README.md"
CONTENT_A = b"# Exact accepted submission A\n"
CONTENT_B = b"# Exact accepted submission B\n"


def accepted(claim_key: str) -> list[dict[str, object]]:
    return [
        {
            "claimKey": claim_key,
            "declaredStatement": "The contributor declared a broader result.",
            "validitySummary": "Only the finite restricted case is established.",
            "scopeQualifications": ["Finite restricted case only."],
            "evidenceTransactionIds": [],
            "dependencyTransactionIds": [],
        }
    ]


def without_digest(value: dict[str, object]) -> dict[str, object]:
    return {key: copy.deepcopy(item) for key, item in value.items() if key != "digest"}


def raw_first_transition(base: dict[str, object]) -> dict[str, object]:
    root = without_digest(base["programs"]["root"])
    root.update(
        {
            "currentStateSummary": "The finite restricted case is established.",
            "localResidualSummary": "The unrestricted objective remains open.",
            "intermediateResultIds": ["result/restricted"],
            "sourceTransactionIds": [TX_A],
        }
    )
    result = {
        "id": "result/restricted",
        "primaryProgramId": "root",
        "relatedProgramIds": [],
        "title": "Restricted result",
        "statement": "The finite restricted case is established.",
        "scopeQualifications": ["Finite restricted case only."],
        "support": {
            "proofs": ["The submission gives the accepted proof."],
            "methods": [],
            "computations": [],
            "tools": [],
            "artifactPaths": [PATH_A],
            "attestationRefs": [],
        },
        "dependencyResultIds": [],
        "claimRefs": [{"transactionId": TX_A, "claimKey": "claim-a"}],
        "sourceTransactionIds": [TX_A],
        "judgmentIds": [],
        "status": "active",
        "supersededByResultIds": [],
    }
    return {
        "schemaVersion": 1,
        "subjectTransactionId": TX_A,
        "baseStateDigest": base["stateDigest"],
        "contentOperations": [
            {
                "entityKind": "program",
                "entityId": "root",
                "baseDigest": base["stateDigest"],
                "value": root,
            },
            {
                "entityKind": "intermediateResult",
                "entityId": "result/restricted",
                "baseDigest": None,
                "value": result,
            },
        ],
        "topologyOperations": [],
        "contribution": {
            "claimKeys": ["claim-a"],
            "directProgramIds": ["root"],
            "intermediateResultIds": ["result/restricted"],
        },
        "placementAudit": {
            "basis": "canonical-objective",
            "rationale": "The restricted result concerns the canonical objective.",
            "relatedProgramIds": [],
        },
        "topologyRationale": None,
    }


def raw_local_first_transition(base: dict[str, object]) -> dict[str, object]:
    transition = raw_first_transition(base)
    root = transition["contentOperations"][0]["value"]
    root["intermediateResultIds"] = []
    program = {
        "id": "program/local",
        "parentId": "root",
        "title": "Restricted program",
        "objective": "Resolve the restricted case.",
        "currentStateSummary": "The finite restricted case is established.",
        "localResidualSummary": "The unrestricted extension remains open.",
        "status": "active",
        "intermediateResultIds": ["result/restricted"],
        "sourceTransactionIds": [TX_A],
        "lineage": [],
    }
    result = transition["contentOperations"][1]["value"]
    result["primaryProgramId"] = "program/local"
    transition["contentOperations"] = [
        transition["contentOperations"][0],
        {
            "entityKind": "program",
            "entityId": "program/local",
            "baseDigest": None,
            "value": program,
        },
        transition["contentOperations"][1],
    ]
    transition["contribution"]["directProgramIds"] = ["program/local"]
    transition["placementAudit"] = {
        "basis": "local-objective",
        "rationale": "The result concerns a durable restricted direction.",
        "relatedProgramIds": ["program/local"],
    }
    return transition


def raw_second_transition(base: dict[str, object]) -> dict[str, object]:
    root = without_digest(base["programs"]["root"])
    root.update(
        {
            "currentStateSummary": "The finite restricted case is strengthened.",
            "localResidualSummary": "The unrestricted objective remains open.",
            "sourceTransactionIds": [TX_B],
        }
    )
    program = without_digest(base["programs"]["program/local"])
    program.update(
        {
            "currentStateSummary": "The finite restricted case is strengthened.",
            "sourceTransactionIds": [TX_B],
        }
    )
    result = without_digest(base["intermediateResults"]["result/restricted"])
    support = copy.deepcopy(result["support"])
    support.pop("artifactRefs")
    support["artifactPaths"] = [PATH_B]
    support["methods"] = ["The second submission strengthens the reduction."]
    result.update(
        {
            "statement": "The finite restricted case is established more sharply.",
            "support": support,
            "dependencyResultIds": [],
            "claimRefs": [{"transactionId": TX_B, "claimKey": "claim-b"}],
            "sourceTransactionIds": [TX_B],
            "judgmentIds": [],
            "supersededByResultIds": [],
        }
    )
    return {
        "schemaVersion": 1,
        "subjectTransactionId": TX_B,
        "baseStateDigest": base["stateDigest"],
        "contentOperations": [
            {
                "entityKind": "program",
                "entityId": "root",
                "baseDigest": base["stateDigest"],
                "value": root,
            },
            {
                "entityKind": "program",
                "entityId": "program/local",
                "baseDigest": base["stateDigest"],
                "value": program,
            },
            {
                "entityKind": "intermediateResult",
                "entityId": "result/restricted",
                "baseDigest": base["stateDigest"],
                "value": result,
            },
        ],
        "topologyOperations": [],
        "contribution": {
            "claimKeys": ["claim-b"],
            "directProgramIds": ["program/local"],
            "intermediateResultIds": ["result/restricted"],
        },
        "placementAudit": {
            "basis": "local-objective",
            "rationale": "The strengthened result concerns the restricted direction.",
            "relatedProgramIds": ["program/local"],
        },
        "topologyRationale": None,
    }


class Transport:
    def __init__(self, values: list[object]):
        self.values = list(values)
        self.requests: list[dict[str, object]] = []

    def __call__(self, request: dict[str, object]) -> dict[str, object]:
        self.requests.append(copy.deepcopy(request))
        value = self.values.pop(0)
        return {
            "id": "response-v8",
            "model": "openai/gpt-5.6-sol",
            "choices": [
                {"finish_reason": "stop", "message": {"content": json.dumps(value)}}
            ],
        }


class ResearchBuilderV8Tests(unittest.TestCase):
    def setUp(self) -> None:
        self.base = empty_research_program_state_v3("two-entity-fixture")

    def provider(self, transition: dict[str, object]) -> tuple[OpenRouterResearchBuilderV8Provider, Transport]:
        transport = Transport([copy.deepcopy(transition) for _ in range(3)])
        provider = OpenRouterResearchBuilderV8Provider(
            json.loads(SPEC.read_text(encoding="utf-8")), transport=transport
        )
        return provider, transport

    def test_provider_passes_full_validity_context_and_binds_exact_artifact(self) -> None:
        provider, transport = self.provider(raw_first_transition(self.base))
        output = provider.run(
            problem_id="two-entity-fixture",
            subject_transaction_id=TX_A,
            base_state=self.base,
            accepted_claims=accepted("claim-a"),
            judgment_id=JUDGMENT_A,
            evidence_files=(
                SubmissionEvidenceFile(
                    path=PATH_A,
                    digest=sha256_bytes(CONTENT_A),
                    content=CONTENT_A,
                ),
            ),
        )
        support = output["contentOperations"][1]["value"]["support"]
        self.assertNotIn("artifactPaths", support)
        self.assertEqual(
            support["artifactRefs"],
            [{"path": PATH_A, "digest": sha256_bytes(CONTENT_A)}],
        )
        self.assertEqual(
            output["contentOperations"][0]["baseDigest"],
            self.base["programs"]["root"]["digest"],
        )
        payload = json.loads(
            str(transport.requests[0]["messages"][-1]["content"])
            .split("<math-flow-input>\n", 1)[1]
            .split("\n</math-flow-input>", 1)[0]
        )
        self.assertEqual(payload["acceptedClaimAssessments"], accepted("claim-a"))
        self.assertNotIn("acceptedClaims", payload)

    def test_reducer_rejects_subject_result_without_current_artifact(self) -> None:
        raw = raw_first_transition(self.base)
        raw_support = raw["contentOperations"][1]["value"]["support"]
        raw_support.pop("artifactPaths")
        raw_support["artifactRefs"] = []
        raw["contentOperations"][0]["baseDigest"] = self.base["programs"]["root"]["digest"]
        raw["contentOperations"][1]["value"]["judgmentIds"] = [JUDGMENT_A]
        with self.assertRaisesRegex(MathFlowError, "exact current submission artifact"):
            apply_research_builder_v8_transition(
                self.base,
                raw,
                accepted_claims=accepted("claim-a"),
                judgment_id=JUDGMENT_A,
                evidence_file_refs={PATH_A: sha256_bytes(CONTENT_A)},
            )

    def test_provider_preserves_prior_additive_provenance(self) -> None:
        first_provider, _ = self.provider(raw_local_first_transition(self.base))
        first_transition = first_provider.run(
            problem_id="two-entity-fixture",
            subject_transaction_id=TX_A,
            base_state=self.base,
            accepted_claims=accepted("claim-a"),
            judgment_id=JUDGMENT_A,
            evidence_files=(
                SubmissionEvidenceFile(PATH_A, sha256_bytes(CONTENT_A), CONTENT_A),
            ),
        )
        first = apply_research_builder_v8_transition(
            self.base,
            first_transition,
            accepted_claims=accepted("claim-a"),
            judgment_id=JUDGMENT_A,
            evidence_file_refs={PATH_A: sha256_bytes(CONTENT_A)},
        )["postState"]

        second_provider, _ = self.provider(raw_second_transition(first))
        second_transition = second_provider.run(
            problem_id="two-entity-fixture",
            subject_transaction_id=TX_B,
            base_state=first,
            accepted_claims=accepted("claim-b"),
            judgment_id=JUDGMENT_B,
            evidence_files=(
                SubmissionEvidenceFile(PATH_B, sha256_bytes(CONTENT_B), CONTENT_B),
            ),
        )
        root = second_transition["contentOperations"][0]["value"]
        program = second_transition["contentOperations"][1]["value"]
        result = second_transition["contentOperations"][2]["value"]
        self.assertEqual(root["sourceTransactionIds"], [TX_A, TX_B])
        self.assertEqual(program["sourceTransactionIds"], [TX_A, TX_B])
        self.assertEqual(result["sourceTransactionIds"], [TX_A, TX_B])
        self.assertEqual(
            result["claimRefs"],
            [
                {"transactionId": TX_A, "claimKey": "claim-a"},
                {"transactionId": TX_B, "claimKey": "claim-b"},
            ],
        )
        self.assertEqual(result["judgmentIds"], [JUDGMENT_A, JUDGMENT_B])
        self.assertEqual(
            result["support"]["artifactRefs"],
            [
                {"path": PATH_A, "digest": sha256_bytes(CONTENT_A)},
                {"path": PATH_B, "digest": sha256_bytes(CONTENT_B)},
            ],
        )
        apply_research_builder_v8_transition(
            first,
            second_transition,
            accepted_claims=accepted("claim-b"),
            judgment_id=JUDGMENT_B,
            evidence_file_refs={PATH_B: sha256_bytes(CONTENT_B)},
        )

    def test_provider_still_rejects_invented_provenance(self) -> None:
        first_provider, _ = self.provider(raw_local_first_transition(self.base))
        first_transition = first_provider.run(
            problem_id="two-entity-fixture",
            subject_transaction_id=TX_A,
            base_state=self.base,
            accepted_claims=accepted("claim-a"),
            judgment_id=JUDGMENT_A,
            evidence_files=(
                SubmissionEvidenceFile(PATH_A, sha256_bytes(CONTENT_A), CONTENT_A),
            ),
        )
        first = apply_research_builder_v8_transition(
            self.base,
            first_transition,
            accepted_claims=accepted("claim-a"),
            judgment_id=JUDGMENT_A,
            evidence_file_refs={PATH_A: sha256_bytes(CONTENT_A)},
        )["postState"]
        raw = raw_second_transition(first)
        raw["contentOperations"][0]["value"]["sourceTransactionIds"] = [TX_B, TX_C]

        second_provider, _ = self.provider(raw)
        with self.assertRaisesRegex(MathFlowError, "only accepted sources"):
            second_provider.run(
                problem_id="two-entity-fixture",
                subject_transaction_id=TX_B,
                base_state=first,
                accepted_claims=accepted("claim-b"),
                judgment_id=JUDGMENT_B,
                evidence_files=(
                    SubmissionEvidenceFile(
                        PATH_B, sha256_bytes(CONTENT_B), CONTENT_B
                    ),
                ),
            )

    def test_reducer_rejects_stale_existing_ancestor_summary(self) -> None:
        provider, _ = self.provider(raw_first_transition(self.base))
        first_transition = provider.run(
            problem_id="two-entity-fixture",
            subject_transaction_id=TX_A,
            base_state=self.base,
            accepted_claims=accepted("claim-a"),
            judgment_id=JUDGMENT_A,
            evidence_files=(SubmissionEvidenceFile(PATH_A, sha256_bytes(CONTENT_A), CONTENT_A),),
        )
        first = apply_research_builder_v8_transition(
            self.base,
            first_transition,
            accepted_claims=accepted("claim-a"),
            judgment_id=JUDGMENT_A,
            evidence_file_refs={PATH_A: sha256_bytes(CONTENT_A)},
        )["postState"]
        local_program = {
            "id": "program/local",
            "parentId": "root",
            "title": "Local program",
            "objective": "Resolve the local case.",
            "currentStateSummary": "A local reduction is established.",
            "localResidualSummary": "The terminal local step remains open.",
            "status": "active",
            "intermediateResultIds": ["result/local"],
            "sourceTransactionIds": [TX_B],
            "lineage": [],
        }
        local_result = {
            "id": "result/local",
            "primaryProgramId": "program/local",
            "relatedProgramIds": [],
            "title": "Local reduction",
            "statement": "The local case reduces to a finite subcase.",
            "scopeQualifications": [],
            "support": {
                "proofs": [], "methods": ["Reduction"], "computations": [],
                "tools": [],
                "artifactRefs": [{"path": PATH_B, "digest": sha256_bytes(CONTENT_B)}],
                "attestationRefs": [],
            },
            "dependencyResultIds": [],
            "claimRefs": [{"transactionId": TX_B, "claimKey": "claim-b"}],
            "sourceTransactionIds": [TX_B],
            "judgmentIds": [JUDGMENT_B],
            "status": "active",
            "supersededByResultIds": [],
        }
        transition = {
            "schemaVersion": 1,
            "subjectTransactionId": TX_B,
            "baseStateDigest": first["stateDigest"],
            "contentOperations": [
                {"entityKind": "program", "entityId": "program/local", "baseDigest": None, "value": local_program},
                {"entityKind": "intermediateResult", "entityId": "result/local", "baseDigest": None, "value": local_result},
            ],
            "topologyOperations": [],
            "contribution": {"claimKeys": ["claim-b"], "directProgramIds": ["program/local"], "intermediateResultIds": ["result/local"]},
            "placementAudit": {"basis": "local-objective", "rationale": "This is a narrow local direction.", "relatedProgramIds": ["program/local"]},
            "topologyRationale": None,
        }
        with self.assertRaisesRegex(MathFlowError, "affected existing program and ancestor: root"):
            apply_research_builder_v8_transition(
                first,
                transition,
                accepted_claims=accepted("claim-b"),
                judgment_id=JUDGMENT_B,
                evidence_file_refs={PATH_B: sha256_bytes(CONTENT_B)},
            )

    def test_provider_schema_asks_for_paths_not_digests(self) -> None:
        rendered = json.dumps(_builder_transition_schema_v8(), sort_keys=True)
        self.assertIn("artifactPaths", rendered)
        self.assertNotIn("artifactRefs", rendered)
        profile = json.loads(
            (ROOT / "protocol/profiles/hierarchical-research-v8.json").read_text()
        )
        self.assertEqual(profile["id"], "math-flow/hierarchical-research-v8")
        self.assertIn(
            "protocol/schemas/research-builder-submission-input-v2.schema.json",
            profile["schemas"],
        )


if __name__ == "__main__":
    unittest.main()
