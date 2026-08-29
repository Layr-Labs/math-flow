from __future__ import annotations

import copy
import json
import unittest
from pathlib import Path

from math_flow.artifacts import sha256_bytes
from math_flow.errors import MathFlowError
from math_flow.governed_providers import (
    OpenRouterResearchBuilderV7Provider,
    _builder_transition_schema_v7,
)
from math_flow.research_builder_v7 import (
    apply_research_builder_v7_sequence,
    apply_research_builder_v7_transition,
    empty_research_program_state_v3,
    validate_research_program_state_v3,
    validate_research_topology_alignment_v2,
)
from math_flow.research_topology import validate_research_program_state_versioned
from math_flow.work_projection import SubmissionEvidenceFile


ROOT = Path(__file__).resolve().parents[1]
BUILDER_SPEC = (
    ROOT / "protocol/judges/openrouter-hierarchical-research-builder-v7.json"
)
TX_A = "a" * 40
TX_B = "b" * 40
TX_C = "c" * 40
JUDGMENT_A = "sha256:" + "1" * 64
JUDGMENT_B = "sha256:" + "2" * 64
JUDGMENT_C = "sha256:" + "3" * 64


def _accepted_claim(
    claim_key: str, *, dependencies: list[str] | None = None
) -> list[dict[str, object]]:
    return [
        {
            "claimKey": claim_key,
            "statement": f"Accepted statement for {claim_key}.",
            "dependencyTransactionIds": list(dependencies or []),
        }
    ]


def _without_digest(record: dict[str, object]) -> dict[str, object]:
    return {key: copy.deepcopy(value) for key, value in record.items() if key != "digest"}


def _support(*, proof: str | None = None, tool: str | None = None) -> dict[str, object]:
    return {
        "proofs": [proof] if proof else [],
        "methods": [],
        "computations": [],
        "tools": [tool] if tool else [],
        "artifactRefs": [],
        "attestationRefs": [],
    }


def _first_transition(base: dict[str, object]) -> dict[str, object]:
    root = _without_digest(base["programs"]["root"])
    root.update(
        {
            "currentStateSummary": "The canonical lemma is established.",
            "localResidualSummary": "The remaining canonical problem is open.",
            "intermediateResultIds": ["result/canonical-lemma"],
            "sourceTransactionIds": [TX_A],
        }
    )
    result = {
        "id": "result/canonical-lemma",
        "primaryProgramId": "root",
        "relatedProgramIds": [],
        "title": "Canonical lemma",
        "statement": "The canonical lemma holds.",
        "scopeQualifications": ["Under the stated finite hypothesis."],
        "support": _support(proof="A direct proof establishes the lemma."),
        "dependencyResultIds": [],
        "claimRefs": [{"transactionId": TX_A, "claimKey": "claim-a"}],
        "sourceTransactionIds": [TX_A],
        "judgmentIds": [JUDGMENT_A],
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
                "baseDigest": base["programs"]["root"]["digest"],
                "value": root,
            },
            {
                "entityKind": "intermediateResult",
                "entityId": "result/canonical-lemma",
                "baseDigest": None,
                "value": result,
            },
        ],
        "topologyOperations": [],
        "contribution": {
            "claimKeys": ["claim-a"],
            "directProgramIds": ["root"],
            "intermediateResultIds": ["result/canonical-lemma"],
        },
        "placementAudit": {
            "basis": "canonical-objective",
            "rationale": "The lemma directly concerns the canonical objective.",
            "relatedProgramIds": [],
        },
        "topologyRationale": None,
    }


def _second_transition(base: dict[str, object]) -> dict[str, object]:
    program = {
        "id": "program/local-line",
        "parentId": "root",
        "title": "Local line",
        "objective": "Resolve the local structural direction.",
        "currentStateSummary": "A local reduction is established.",
        "localResidualSummary": "The terminal local bound remains open.",
        "status": "active",
        "intermediateResultIds": ["result/local-reduction"],
        "sourceTransactionIds": [TX_B],
        "lineage": [],
    }
    result = {
        "id": "result/local-reduction",
        "primaryProgramId": "program/local-line",
        "relatedProgramIds": [],
        "title": "Local reduction",
        "statement": "The local case reduces to the canonical lemma.",
        "scopeQualifications": [],
        "support": _support(tool="A symbolic checker verifies the reduction."),
        "dependencyResultIds": ["result/canonical-lemma"],
        "claimRefs": [{"transactionId": TX_B, "claimKey": "claim-b"}],
        "sourceTransactionIds": [TX_B],
        "judgmentIds": [JUDGMENT_B],
        "status": "active",
        "supersededByResultIds": [],
    }
    return {
        "schemaVersion": 1,
        "subjectTransactionId": TX_B,
        "baseStateDigest": base["stateDigest"],
        "contentOperations": [
            {
                "entityKind": "program",
                "entityId": "program/local-line",
                "baseDigest": None,
                "value": program,
            },
            {
                "entityKind": "intermediateResult",
                "entityId": "result/local-reduction",
                "baseDigest": None,
                "value": result,
            },
        ],
        "topologyOperations": [],
        "contribution": {
            "claimKeys": ["claim-b"],
            "directProgramIds": ["program/local-line"],
            "intermediateResultIds": ["result/local-reduction"],
        },
        "placementAudit": {
            "basis": "local-objective",
            "rationale": "The reduction belongs to the narrow local direction.",
            "relatedProgramIds": ["program/local-line"],
        },
        "topologyRationale": None,
    }


def _consolidating_transition(base: dict[str, object]) -> dict[str, object]:
    existing = _without_digest(base["intermediateResults"]["result/canonical-lemma"])
    existing["claimRefs"] = [
        *existing["claimRefs"],
        {"transactionId": TX_C, "claimKey": "claim-c"},
    ]
    existing["sourceTransactionIds"] = [TX_A, TX_C]
    existing["judgmentIds"] = [JUDGMENT_A, JUDGMENT_C]
    existing["support"] = {
        **existing["support"],
        "tools": ["An independent checker certifies the same reusable lemma."],
    }
    return {
        "schemaVersion": 1,
        "subjectTransactionId": TX_C,
        "baseStateDigest": base["stateDigest"],
        "contentOperations": [
            {
                "entityKind": "intermediateResult",
                "entityId": "result/canonical-lemma",
                "baseDigest": base["intermediateResults"]["result/canonical-lemma"]["digest"],
                "value": existing,
            }
        ],
        "topologyOperations": [],
        "contribution": {
            "claimKeys": ["claim-c"],
            "directProgramIds": ["root"],
            "intermediateResultIds": ["result/canonical-lemma"],
        },
        "placementAudit": {
            "basis": "canonical-objective",
            "rationale": "The submission strengthens support for the same global lemma.",
            "relatedProgramIds": [],
        },
        "topologyRationale": None,
    }


class SequentialTransport:
    def __init__(self, values: list[object]):
        self.values = list(values)
        self.requests: list[dict[str, object]] = []

    def __call__(self, payload: dict[str, object]) -> dict[str, object]:
        self.requests.append(copy.deepcopy(payload))
        value = self.values.pop(0)
        return {
            "id": "response-v7",
            "model": "openai/gpt-5.6-sol",
            "choices": [
                {"finish_reason": "stop", "message": {"content": json.dumps(value)}}
            ],
        }


class ResearchBuilderV7Tests(unittest.TestCase):
    def setUp(self) -> None:
        self.base = empty_research_program_state_v3("two-entity-fixture")

    def _first(self) -> dict[str, object]:
        return apply_research_builder_v7_transition(
            self.base,
            _first_transition(self.base),
            accepted_claims=_accepted_claim("claim-a"),
            judgment_id=JUDGMENT_A,
        )

    def test_empty_state_has_only_program_and_intermediate_result_entities(self) -> None:
        validated = validate_research_program_state_v3(self.base)
        self.assertEqual(validated["schemaVersion"], 3)
        self.assertEqual(set(validated), {
            "schemaVersion", "problemId", "ledgerHead", "baseStateDigest",
            "rootProgramId", "programs", "intermediateResults", "contributions",
            "stateDigest",
        })
        self.assertNotIn("threads", validated)
        self.assertNotIn("items", validated)
        self.assertEqual(
            validate_research_program_state_versioned(validated), validated
        )

    def test_transition_packages_support_and_derives_program_only_handoff(self) -> None:
        reduced = self._first()
        state = reduced["postState"]
        result = state["intermediateResults"]["result/canonical-lemma"]
        self.assertEqual(result["support"]["proofs"], ["A direct proof establishes the lemma."])
        self.assertEqual(state["programs"]["root"]["intermediateResultIds"], ["result/canonical-lemma"])
        self.assertEqual(reduced["sameWorldHandoff"]["accountingNodeKinds"], ["program"])
        self.assertEqual(reduced["sameWorldHandoff"]["semanticLeafKinds"], ["intermediateResult"])
        validate_research_topology_alignment_v2(
            reduced["topologyAlignment"], self.base, state
        )

    def test_existing_result_can_receive_new_support_without_new_semantic_node(self) -> None:
        first = self._first()["postState"]
        second = apply_research_builder_v7_transition(
            first,
            _second_transition(first),
            accepted_claims=_accepted_claim("claim-b", dependencies=[TX_A]),
            judgment_id=JUDGMENT_B,
        )["postState"]
        reduced = apply_research_builder_v7_transition(
            second,
            _consolidating_transition(second),
            accepted_claims=_accepted_claim("claim-c"),
            judgment_id=JUDGMENT_C,
        )
        self.assertEqual(len(reduced["postState"]["intermediateResults"]), 2)
        result = reduced["postState"]["intermediateResults"]["result/canonical-lemma"]
        self.assertEqual(result["sourceTransactionIds"], [TX_A, TX_C])
        self.assertEqual(result["support"]["tools"], ["An independent checker certifies the same reusable lemma."])

    def test_empty_support_is_valid_when_claim_and_judgment_provenance_are_exact(self) -> None:
        transition = _first_transition(self.base)
        transition["contentOperations"][1]["value"]["support"] = _support()
        reduced = apply_research_builder_v7_transition(
            self.base,
            transition,
            accepted_claims=_accepted_claim("claim-a"),
            judgment_id=JUDGMENT_A,
        )
        result = reduced["postState"]["intermediateResults"]["result/canonical-lemma"]
        self.assertTrue(all(not value for value in result["support"].values()))
        self.assertEqual(result["judgmentIds"], [JUDGMENT_A])

    def test_sequence_is_one_transition_per_canonical_submission(self) -> None:
        first_transition = _first_transition(self.base)
        first_state = self._first()["postState"]
        second_transition = _second_transition(first_state)
        results = apply_research_builder_v7_sequence(
            self.base,
            [first_transition, second_transition],
            accepted_submissions=[
                {
                    "transactionId": TX_A,
                    "ordinal": 1,
                    "acceptedClaims": _accepted_claim("claim-a"),
                    "judgmentId": JUDGMENT_A,
                },
                {
                    "transactionId": TX_B,
                    "ordinal": 2,
                    "acceptedClaims": _accepted_claim("claim-b", dependencies=[TX_A]),
                    "judgmentId": JUDGMENT_B,
                },
            ],
        )
        self.assertEqual([item["subjectTransactionId"] for item in results], [TX_A, TX_B])
        self.assertEqual(results[-1]["postState"]["ledgerHead"], TX_B)

    def test_state_rejects_nonreciprocal_program_result_links(self) -> None:
        state = copy.deepcopy(self._first()["postState"])
        state["programs"]["root"]["intermediateResultIds"] = []
        from math_flow.repository import sha256_json

        root = state["programs"]["root"]
        root["digest"] = "sha256:" + sha256_json(
            {key: value for key, value in root.items() if key != "digest"}
        )
        state["stateDigest"] = "sha256:" + sha256_json(
            {key: value for key, value in state.items() if key != "stateDigest"}
        )
        with self.assertRaisesRegex(MathFlowError, "links are not reciprocal"):
            validate_research_program_state_v3(state)

    def test_transition_rejects_stale_base_and_unrepresented_claim(self) -> None:
        stale = _first_transition(self.base)
        stale["baseStateDigest"] = "sha256:" + "0" * 64
        with self.assertRaisesRegex(MathFlowError, "stale base"):
            apply_research_builder_v7_transition(
                self.base,
                stale,
                accepted_claims=_accepted_claim("claim-a"),
                judgment_id=JUDGMENT_A,
            )

    def test_transition_rejects_false_direct_program_provenance(self) -> None:
        transition = _first_transition(self.base)
        transition["contribution"]["directProgramIds"] = ["missing-program"]
        with self.assertRaisesRegex(MathFlowError, "exactly match"):
            apply_research_builder_v7_transition(
                self.base,
                transition,
                accepted_claims=_accepted_claim("claim-a"),
                judgment_id=JUDGMENT_A,
            )
        missing = _first_transition(self.base)
        missing["contentOperations"][1]["value"]["claimRefs"][0]["claimKey"] = "other"
        with self.assertRaisesRegex(MathFlowError, "unaccepted claim"):
            apply_research_builder_v7_transition(
                self.base,
                missing,
                accepted_claims=_accepted_claim("claim-a"),
                judgment_id=JUDGMENT_A,
            )

    def test_transition_rejects_thread_entity_and_result_dependency_cycle(self) -> None:
        thread = _first_transition(self.base)
        thread["contentOperations"][0]["entityKind"] = "thread"
        with self.assertRaisesRegex(MathFlowError, "invalid entity kind"):
            apply_research_builder_v7_transition(
                self.base,
                thread,
                accepted_claims=_accepted_claim("claim-a"),
                judgment_id=JUDGMENT_A,
            )
        cycle = _first_transition(self.base)
        cycle["contentOperations"][1]["value"]["dependencyResultIds"] = ["result/canonical-lemma"]
        with self.assertRaisesRegex(MathFlowError, "may not reference itself"):
            apply_research_builder_v7_transition(
                self.base,
                cycle,
                accepted_claims=_accepted_claim("claim-a"),
                judgment_id=JUDGMENT_A,
            )

    def test_provider_returns_only_reducer_validated_transition(self) -> None:
        transition = _first_transition(self.base)
        transport = SequentialTransport([transition])
        provider = OpenRouterResearchBuilderV7Provider(
            json.loads(BUILDER_SPEC.read_text()), transport=transport
        )
        content = b"# Exact accepted submission\n"
        evidence = (
            SubmissionEvidenceFile(
                path="problems/two-entity-fixture/contributions/accepted/README.md",
                digest=sha256_bytes(content),
                content=content,
            ),
        )
        output = provider.run(
            problem_id="two-entity-fixture",
            subject_transaction_id=TX_A,
            base_state=self.base,
            accepted_claims=_accepted_claim("claim-a"),
            judgment_id=JUDGMENT_A,
            evidence_files=evidence,
        )
        self.assertEqual(output, transition)
        schema = transport.requests[0]["response_format"]["json_schema"]["schema"]
        self.assertEqual(schema["properties"]["subjectTransactionId"]["enum"], [TX_A])
        rendered = json.dumps(schema, sort_keys=True)
        self.assertNotIn('"thread"', rendered)
        self.assertNotIn('"item"', rendered)
        self.assertNotIn("uniqueItems", rendered)

    def test_provider_retries_after_deterministic_validation_failure(self) -> None:
        rejected = _first_transition(self.base)
        rejected["contentOperations"][1]["value"]["primaryProgramId"] = "missing"
        corrected = _first_transition(self.base)
        transport = SequentialTransport([rejected, corrected])
        invalidations = 0

        def invalidate() -> None:
            nonlocal invalidations
            invalidations += 1

        provider = OpenRouterResearchBuilderV7Provider(
            json.loads(BUILDER_SPEC.read_text()),
            transport=transport,
            invalidate_last_response=invalidate,
        )
        content = b"# Exact accepted submission\n"
        output = provider.run(
            problem_id="two-entity-fixture",
            subject_transaction_id=TX_A,
            base_state=self.base,
            accepted_claims=_accepted_claim("claim-a"),
            judgment_id=JUDGMENT_A,
            evidence_files=(
                SubmissionEvidenceFile(
                    path="problems/two-entity-fixture/contributions/accepted/README.md",
                    digest=sha256_bytes(content),
                    content=content,
                ),
            ),
        )
        self.assertEqual(output, corrected)
        self.assertEqual(invalidations, 1)
        self.assertEqual(len(transport.requests), 2)

    def test_provider_injects_existing_content_entity_base_digest(self) -> None:
        transition = _first_transition(self.base)
        transition["contentOperations"][0]["baseDigest"] = self.base["stateDigest"]
        transport = SequentialTransport([transition])
        provider = OpenRouterResearchBuilderV7Provider(
            json.loads(BUILDER_SPEC.read_text()), transport=transport
        )
        content = b"# Exact accepted submission\n"
        output = provider.run(
            problem_id="two-entity-fixture",
            subject_transaction_id=TX_A,
            base_state=self.base,
            accepted_claims=_accepted_claim("claim-a"),
            judgment_id=JUDGMENT_A,
            evidence_files=(
                SubmissionEvidenceFile(
                    path="problems/two-entity-fixture/contributions/accepted/README.md",
                    digest=sha256_bytes(content),
                    content=content,
                ),
            ),
        )
        self.assertEqual(
            output["contentOperations"][0]["baseDigest"],
            self.base["programs"]["root"]["digest"],
        )
        self.assertEqual(len(transport.requests), 1)

    def test_provider_schema_is_strict_and_profile_is_additive(self) -> None:
        schema = _builder_transition_schema_v7()
        stack: list[object] = [schema]
        while stack:
            node = stack.pop()
            if isinstance(node, dict):
                self.assertNotIn("oneOf", node)
                self.assertNotIn("uniqueItems", node)
                if node.get("type") == "object":
                    properties = node.get("properties")
                    self.assertIsInstance(properties, dict)
                    self.assertEqual(set(node.get("required", [])), set(properties))
                    self.assertIs(node.get("additionalProperties"), False)
                stack.extend(node.values())
            elif isinstance(node, list):
                stack.extend(node)
        profile = json.loads(
            (ROOT / "protocol/profiles/hierarchical-research-v7.json").read_text()
        )
        self.assertEqual(profile["id"], "math-flow/hierarchical-research-v7")
        self.assertIn("protocol/schemas/research-program-state-v3.schema.json", profile["schemas"])


if __name__ == "__main__":
    unittest.main()
