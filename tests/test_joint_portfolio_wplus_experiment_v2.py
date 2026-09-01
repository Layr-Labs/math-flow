from __future__ import annotations

import copy
import json
import unittest
from pathlib import Path

from experiments.bssc_accounting_topology_prompt import state_summary
from experiments.bssc_local_builder_v10 import (
    BudgetedCapturingTransport,
    _scenario_artifact,
)
from math_flow.artifacts import sha256_bytes
from math_flow.errors import MathFlowError
from math_flow.joint_portfolio_wplus_experiment import (
    OpenRouterJointPortfolioWPlusExperimentProviderV2,
    reduce_joint_portfolio_wplus_response_v2,
    validate_fixed_semantic_packet,
)
from math_flow.research_builder_v7 import validate_research_program_state_v3
from math_flow.teacher_student_scenarios import _score_json_relational
from math_flow.work_accounting import make_zero_work_accounting_state
from math_flow.work_projection import SubmissionEvidenceFile


ROOT = Path(__file__).resolve().parents[1]
EXPERIMENT_V1 = ROOT / "protocol/experiments/bssc-joint-portfolio-wplus-k1-v1"
EXPERIMENT_V2 = ROOT / "protocol/experiments/bssc-joint-portfolio-wplus-k1-v2"
SUBJECT = "c70e1829a7c6a2a8cb8cfc2383f8abf825ac5ea6"
CLAIM = "bssc-sum-capacity/code-induced-dependence-balance-and-entropy-no-go"
JUDGMENT = "sha256:" + "2" * 64


class JointPortfolioWPlusExperimentV2Tests(unittest.TestCase):
    def setUp(self) -> None:
        self.base = validate_research_program_state_v3(
            json.loads(
                (
                    ROOT
                    / "protocol/experiments/bssc-local-builder-v10-k1-v1/fixtures/empty-state.json"
                ).read_text(encoding="utf-8")
            )
        )
        self.packet = validate_fixed_semantic_packet(
            json.loads(
                (EXPERIMENT_V1 / "fixed-semantic-packet-v1.json").read_text(
                    encoding="utf-8"
                )
            )
        )
        self.contract = json.loads(
            (EXPERIMENT_V2 / "root-contract-v2.json").read_text(encoding="utf-8")
        )
        self.claims = [
            {
                "claimKey": CLAIM,
                "declaredStatement": "accepted",
                "validitySummary": "accepted",
                "scopeQualifications": [],
                "evidenceTransactionIds": [SUBJECT],
                "dependencyTransactionIds": [],
            }
        ]
        paths = sorted(
            {
                path
                for result in self.packet["intermediateResults"]
                for path in result["support"]["artifactPaths"]
            }
        )
        self.evidence = tuple(
            SubmissionEvidenceFile(
                path=path,
                content=f"fixture:{path}".encode(),
                digest=sha256_bytes(f"fixture:{path}".encode()),
            )
            for path in paths
        )
        self.base_accounting = make_zero_work_accounting_state(
            root_contract=self.contract,
            knowledge_state=self.base,
        )

    def response(self) -> dict[str, object]:
        programs = [
            {
                "id": "leaf-channel-refinement",
                "parentId": "portfolio-code-induced-converse",
                "title": "Channel-specific refinements",
                "objective": "Find channel-specific constraints beyond the closed coarse route.",
                "currentStateSummary": "The specified coarse entropy/copy route is obstructed.",
                "localResidualSummary": "Develop exact binary-posterior or other channel-specific constraints.",
                "status": "active",
            },
            {
                "id": "leaf-structure-preserving-reduction",
                "parentId": "portfolio-code-induced-converse",
                "title": "Structure-preserving reduction",
                "objective": "Turn finite-block code-induced constraints into a usable converse reduction.",
                "currentStateSummary": "An exact finite-block necessary condition is available.",
                "localResidualSummary": "Establish a fixed-cardinality or compact representation preserving encoder structure.",
                "status": "active",
            },
            {
                "id": "portfolio-code-induced-converse",
                "parentId": "root",
                "title": "Code-induced converse portfolio",
                "objective": "Develop a BSSC converse from structure inherited from actual codes.",
                "currentStateSummary": "The structural theorem and one refinement no-go are known.",
                "localResidualSummary": "Coordinate structural reduction and viable channel-specific refinements.",
                "status": "active",
            },
        ]
        hours = {
            "leaf-channel-refinement": "30",
            "leaf-structure-preserving-reduction": "40",
            "portfolio-code-induced-converse": "20",
        }
        incidence = {
            "leaf-channel-refinement": "0.8",
            "leaf-structure-preserving-reduction": "0.9",
            "portfolio-code-induced-converse": "1",
        }
        return {
            "schemaVersion": 2,
            "subjectTransactionId": SUBJECT,
            "baseStateDigest": self.base["stateDigest"],
            "createdPrograms": programs,
            "resultPlacements": [
                {
                    "resultId": "result-bssc-coarse-entropy-copy-refinement-no-go",
                    "primaryProgramId": "leaf-channel-refinement",
                },
                {
                    "resultId": "result-bssc-code-induced-finite-block-dependence-balance",
                    "primaryProgramId": "leaf-structure-preserving-reduction",
                },
            ],
            "createdProgramBoundaries": [
                {
                    "programId": program["id"],
                    "directResidualWorkScope": f"Direct residual scope for {program['id']}.",
                    "activationCondition": f"Activation condition for {program['id']}.",
                    "stoppingCondition": f"Stopping condition for {program['id']}.",
                    "independentVariationRationale": f"Independent variation rationale for {program['id']}.",
                }
                for program in programs
            ],
            "rootBoundary": {
                "directResidualWorkScope": "Unrepresented terminal work and root integration.",
                "activationCondition": "The admitted root problem is active.",
                "stoppingCondition": "The root contract terminal condition is met.",
                "independentVariationRationale": "Root residual varies separately from the created local subtree.",
            },
            "createdProgramWithAccessAnnotations": [
                {
                    "programId": program["id"],
                    "directWorkHours": hours[program["id"]],
                    "conditionalIncidence": incidence[program["id"]],
                    "rationale": f"Primitive W+ rationale for {program['id']}.",
                    "evidenceRefs": [CLAIM],
                }
                for program in programs
            ],
            "rootWithAccessAnnotation": {
                "directWorkHours": "10",
                "rationale": "Root residual excludes work assigned to the created subtree.",
                "evidenceRefs": [CLAIM],
            },
            "topologyRationale": "The two leaves have independently variable residual-work and stopping decisions under one narrow shared objective.",
        }

    def reduce(self, response: object) -> dict[str, object]:
        return reduce_joint_portfolio_wplus_response_v2(
            response,
            base_state=self.base,
            base_accounting_state=self.base_accounting,
            root_contract=self.contract,
            semantic_packet=self.packet,
            accepted_claims=self.claims,
            judgment_id=JUDGMENT,
            evidence_files=self.evidence,
        )

    def test_v2_reduces_to_the_precommitted_topology_and_wplus(self) -> None:
        reduced = self.reduce(self.response())
        self.assertEqual(len(reduced["response"]["createdPrograms"]), 3)
        self.assertEqual(reduced["withAccessState"]["totalWorkHours"], "90")
        self.assertNotIn(
            "root",
            {
                program["id"]
                for program in reduced["response"]["createdPrograms"]
            },
        )
        gold = json.loads(
            (
                ROOT
                / "protocol/experiments/bssc-local-builder-v10-k1-v1/relational-gold-v1.json"
            ).read_text(encoding="utf-8")
        )
        score = _score_json_relational(
            gold,
            {
                "fixed-base-state": _scenario_artifact(self.base),
                "k1.author.transition": _scenario_artifact(reduced["transition"]),
                "k1.author.topology": _scenario_artifact(
                    state_summary(reduced["postState"], SUBJECT)
                ),
            },
            variant="joint-portfolio-wplus-v2",
            seed=1729,
            scorer_id="joint-portfolio-wplus-v2-test",
        )
        self.assertEqual(score["status"], "passed")

    def test_v2_root_cannot_be_returned_as_a_created_program(self) -> None:
        response = self.response()
        response["createdPrograms"][0]["id"] = "root"
        with self.assertRaisesRegex(MathFlowError, "dedicated root fields"):
            self.reduce(response)

    def test_v2_rejects_speculative_created_leaf(self) -> None:
        response = self.response()
        response["createdPrograms"].append(
            {
                "id": "unaffected-achievability",
                "parentId": "root",
                "title": "Unaffected achievability",
                "objective": "Invent an achievability program unrelated to the fixed results.",
                "currentStateSummary": "No fixed result changes this package.",
                "localResidualSummary": "All work remains hypothetical here.",
                "status": "active",
            }
        )
        with self.assertRaisesRegex(MathFlowError, "speculative outside"):
            self.reduce(response)

    def test_v2_rejects_unary_created_wrapper(self) -> None:
        response = self.response()
        response["createdPrograms"][2]["parentId"] = "wrapper"
        response["createdPrograms"].append(
            {
                "id": "wrapper",
                "parentId": "root",
                "title": "Unary wrapper",
                "objective": "Restate the only child objective.",
                "currentStateSummary": "No independent work boundary.",
                "localResidualSummary": "No separate residual work.",
                "status": "active",
            }
        )
        with self.assertRaisesRegex(MathFlowError, "unary wrapper"):
            self.reduce(response)

    def test_v2_result_placement_cannot_add_ancestor_membership(self) -> None:
        response = self.response()
        response["resultPlacements"][0]["relatedProgramIds"] = [
            "portfolio-code-induced-converse"
        ]
        with self.assertRaisesRegex(MathFlowError, "narrowest primary program"):
            self.reduce(response)

    def test_v2_provider_preserves_pre_dispatch_budget_classification(self) -> None:
        inner_calls: list[dict[str, object]] = []
        transport = BudgetedCapturingTransport(
            maximum_calls=3,
            maximum_cost_usd=1.5,
            maximum_single_call_cost_usd=0.75,
            maximum_request_bytes=768000,
            maximum_total_tokens=1,
            transport=lambda request: inner_calls.append(request) or {},
        )
        spec = json.loads(
            (
                ROOT
                / "protocol/judges/openrouter-joint-portfolio-wplus-experiment-v2.json"
            ).read_text(encoding="utf-8")
        )
        provider = OpenRouterJointPortfolioWPlusExperimentProviderV2(
            spec, transport=transport
        )
        with self.assertRaises(MathFlowError) as raised:
            provider.run(
                problem_id="bssc-sum-capacity",
                subject_transaction_id=SUBJECT,
                base_state=self.base,
                root_contract=self.contract,
                semantic_packet=self.packet,
                accepted_claims=self.claims,
                judgment_id=JUDGMENT,
                evidence_files=self.evidence,
            )
        self.assertIn("total-token budget exhausted", str(raised.exception))
        self.assertNotIn("outcome is uncertain", str(raised.exception))
        self.assertEqual(inner_calls, [])
        self.assertEqual(transport.requests, [])

    def test_v2_provider_uses_separate_root_fields(self) -> None:
        requests: list[dict[str, object]] = []

        def transport(request: dict[str, object]) -> dict[str, object]:
            requests.append(copy.deepcopy(request))
            return {
                "id": "joint-v2-response-1",
                "model": "openai/gpt-5.6-sol",
                "choices": [
                    {
                        "finish_reason": "stop",
                        "message": {"content": json.dumps(self.response())},
                    }
                ],
            }

        spec = json.loads(
            (
                ROOT
                / "protocol/judges/openrouter-joint-portfolio-wplus-experiment-v2.json"
            ).read_text(encoding="utf-8")
        )
        provider = OpenRouterJointPortfolioWPlusExperimentProviderV2(
            spec, transport=transport
        )
        artifacts = provider.run(
            problem_id="bssc-sum-capacity",
            subject_transaction_id=SUBJECT,
            base_state=self.base,
            root_contract=self.contract,
            semantic_packet=self.packet,
            accepted_claims=self.claims,
            judgment_id=JUDGMENT,
            evidence_files=self.evidence,
        )
        self.assertEqual(artifacts["withAccessState"]["totalWorkHours"], "90")
        schema = requests[0]["response_format"]["json_schema"]["schema"]
        self.assertIn("createdPrograms", schema["properties"])
        self.assertIn("rootWithAccessAnnotation", schema["properties"])
        self.assertNotIn("programs", schema["properties"])


if __name__ == "__main__":
    unittest.main()
