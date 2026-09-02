from __future__ import annotations

import copy
import json
import unittest
from pathlib import Path

from experiments.bssc_accounting_topology_prompt import state_summary
from experiments.bssc_local_builder_v10 import _scenario_artifact
from math_flow.artifacts import sha256_bytes
from math_flow.errors import MathFlowError
from math_flow.joint_portfolio_wplus_experiment import (
    OpenRouterJointPortfolioWPlusExperimentProvider,
    reduce_joint_portfolio_wplus_response,
    validate_fixed_semantic_packet,
)
from math_flow.research_builder_v7 import validate_research_program_state_v3
from math_flow.teacher_student_scenarios import _score_json_relational
from math_flow.work_accounting import make_zero_work_accounting_state
from math_flow.work_projection import SubmissionEvidenceFile


ROOT = Path(__file__).resolve().parents[1]
EXPERIMENT = ROOT / "protocol/experiments/bssc-joint-portfolio-wplus-k1-v1"
SUBJECT = "c70e1829a7c6a2a8cb8cfc2383f8abf825ac5ea6"
CLAIM = "bssc-sum-capacity/code-induced-dependence-balance-and-entropy-no-go"
JUDGMENT = "sha256:" + "1" * 64


class JointPortfolioWPlusExperimentTests(unittest.TestCase):
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
                (EXPERIMENT / "fixed-semantic-packet-v1.json").read_text(
                    encoding="utf-8"
                )
            )
        )
        self.contract = json.loads(
            (EXPERIMENT / "root-contract-v1.json").read_text(encoding="utf-8")
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
        program_ids = [program["id"] for program in programs] + ["root"]
        return {
            "schemaVersion": 1,
            "subjectTransactionId": SUBJECT,
            "baseStateDigest": self.base["stateDigest"],
            "programs": programs,
            "resultPlacements": [
                {
                    "resultId": "result-bssc-coarse-entropy-copy-refinement-no-go",
                    "primaryProgramId": "leaf-channel-refinement",
                    "relatedProgramIds": [],
                },
                {
                    "resultId": "result-bssc-code-induced-finite-block-dependence-balance",
                    "primaryProgramId": "leaf-structure-preserving-reduction",
                    "relatedProgramIds": [],
                },
            ],
            "accountingBoundaries": [
                {
                    "programId": program_id,
                    "directResidualWorkScope": f"Direct residual scope for {program_id}.",
                    "activationCondition": f"Activation condition for {program_id}.",
                    "stoppingCondition": f"Stopping condition for {program_id}.",
                    "independentVariationRationale": f"Independent variation rationale for {program_id}.",
                }
                for program_id in sorted(program_ids)
            ],
            "withAccessAnnotations": [
                {
                    "programId": program_id,
                    "directWorkHours": {
                        "root": "10",
                        "portfolio-code-induced-converse": "20",
                        "leaf-channel-refinement": "30",
                        "leaf-structure-preserving-reduction": "40",
                    }[program_id],
                    "conditionalIncidence": (
                        None
                        if program_id == "root"
                        else {
                            "portfolio-code-induced-converse": "1",
                            "leaf-channel-refinement": "0.8",
                            "leaf-structure-preserving-reduction": "0.9",
                        }[program_id]
                    ),
                    "rationale": f"Primitive W+ rationale for {program_id}.",
                    "evidenceRefs": [CLAIM],
                }
                for program_id in sorted(program_ids)
            ],
            "topologyRationale": "The two leaves have independently variable residual-work and stopping decisions under one narrow shared objective.",
        }

    def reduce(self, response: object) -> dict[str, object]:
        return reduce_joint_portfolio_wplus_response(
            response,
            base_state=self.base,
            base_accounting_state=self.base_accounting,
            root_contract=self.contract,
            semantic_packet=self.packet,
            accepted_claims=self.claims,
            judgment_id=JUDGMENT,
            evidence_files=self.evidence,
        )

    def test_joint_response_reduces_to_three_programs_and_valid_wplus(self) -> None:
        reduced = self.reduce(self.response())
        post = reduced["postState"]
        self.assertEqual(
            set(post["programs"]),
            {
                "root",
                "portfolio-code-induced-converse",
                "leaf-channel-refinement",
                "leaf-structure-preserving-reduction",
            },
        )
        self.assertEqual(
            post["intermediateResults"][
                "result-bssc-coarse-entropy-copy-refinement-no-go"
            ]["primaryProgramId"],
            "leaf-channel-refinement",
        )
        self.assertEqual(reduced["withAccessState"]["totalWorkHours"], "90")
        self.assertEqual(
            reduced["withAccessState"]["processedSubmissionIds"], [SUBJECT]
        )
        self.assertEqual(
            reduced["withAccessPatch"]["evaluationMode"], "with-access"
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
                "k1.author.topology": _scenario_artifact(state_summary(post, SUBJECT)),
            },
            variant="joint-portfolio-wplus-v1",
            seed=1729,
            scorer_id="joint-portfolio-wplus-test",
        )
        self.assertEqual(score["status"], "passed")

    def test_missing_accounting_node_is_rejected_before_reduction(self) -> None:
        response = self.response()
        response["withAccessAnnotations"] = response["withAccessAnnotations"][:-1]
        with self.assertRaisesRegex(MathFlowError, "cover every target program"):
            self.reduce(response)

    def test_result_merging_or_replacement_is_outside_provider_authority(self) -> None:
        response = self.response()
        response["resultPlacements"][0]["resultId"] = "replacement-result"
        with self.assertRaisesRegex(MathFlowError, "place every fixed result"):
            self.reduce(response)

    def test_root_incidence_and_child_probability_use_existing_accounting_guards(self) -> None:
        root_bad = self.response()
        next(
            row
            for row in root_bad["withAccessAnnotations"]
            if row["programId"] == "root"
        )["conditionalIncidence"] = "1"
        with self.assertRaisesRegex(MathFlowError, "root incidence"):
            self.reduce(root_bad)

        probability_bad = self.response()
        next(
            row
            for row in probability_bad["withAccessAnnotations"]
            if row["programId"] == "leaf-channel-refinement"
        )["conditionalIncidence"] = "1.1"
        with self.assertRaisesRegex(MathFlowError, "between zero and one"):
            self.reduce(probability_bad)

    def test_packet_digest_and_semantics_are_immutable(self) -> None:
        bad = copy.deepcopy(self.packet)
        bad["intermediateResults"][0]["statement"] = "changed"
        with self.assertRaisesRegex(MathFlowError, "digest mismatch"):
            validate_fixed_semantic_packet(bad)

    def test_governed_provider_uses_one_joint_stage_and_reduces_response(self) -> None:
        requests: list[dict[str, object]] = []

        def transport(request: dict[str, object]) -> dict[str, object]:
            requests.append(copy.deepcopy(request))
            return {
                "id": "joint-response-1",
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
                / "protocol/judges/openrouter-joint-portfolio-wplus-experiment-v1.json"
            ).read_text(encoding="utf-8")
        )
        provider = OpenRouterJointPortfolioWPlusExperimentProvider(
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
        self.assertEqual(len(requests), 1)
        self.assertEqual(artifacts["withAccessState"]["totalWorkHours"], "90")
        self.assertEqual(provider.invocation_records[0]["stage"], "joint-portfolio-wplus")
        user_message = requests[0]["messages"][2]["content"]
        self.assertNotIn('"noAccessState"', user_message)
        self.assertNotIn('"workValueHours"', user_message)


if __name__ == "__main__":
    unittest.main()
