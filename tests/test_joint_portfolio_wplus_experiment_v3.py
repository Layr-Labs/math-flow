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
    OpenRouterJointPortfolioWPlusExperimentProviderV3,
    reduce_joint_portfolio_wplus_response_v3,
    validate_fixed_semantic_packet,
)
from math_flow.research_builder_v7 import validate_research_program_state_v3
from math_flow.teacher_student_scenarios import _score_json_relational
from math_flow.work_accounting import (
    validate_root_contract,
    validate_work_accounting_state,
)
from math_flow.work_projection import SubmissionEvidenceFile


ROOT = Path(__file__).resolve().parents[1]
EXPERIMENT = ROOT / "protocol/experiments/bssc-joint-portfolio-wplus-k2-v3"
SUBJECT = "f236017c62c67ce4218c1f81ea34134f0954b556"
CLAIM = "bssc-sum-capacity/uv-product-branchwise-additivity"
JUDGMENT = "sha256:" + "2" * 64
NEW_PROGRAM = "program-uv-relaxed-sum-rate-tensorization"


class JointPortfolioWPlusExperimentV3Tests(unittest.TestCase):
    def setUp(self) -> None:
        self.base = validate_research_program_state_v3(
            json.loads(
                (EXPERIMENT / "fixtures/k1-post-state.json").read_text(
                    encoding="utf-8"
                )
            )
        )
        self.contract = validate_root_contract(
            json.loads(
                (
                    ROOT
                    / "protocol/experiments/bssc-joint-portfolio-wplus-k1-v2/root-contract-v2.json"
                ).read_text(encoding="utf-8")
            )
        )
        self.base_accounting = validate_work_accounting_state(
            json.loads(
                (EXPERIMENT / "fixtures/k1-with-access-state.json").read_text(
                    encoding="utf-8"
                )
            ),
            self.base,
            self.contract,
        )
        self.packet = validate_fixed_semantic_packet(
            json.loads(
                (EXPERIMENT / "fixed-semantic-packet-v3.json").read_text(
                    encoding="utf-8"
                )
            ),
            external_dependency_result_ids=set(self.base["intermediateResults"]),
        )
        self.claims = [
            {
                "claimKey": CLAIM,
                "declaredStatement": "accepted",
                "validitySummary": "accepted",
                "scopeQualifications": [],
                "evidenceTransactionIds": [
                    "c70e1829a7c6a2a8cb8cfc2383f8abf825ac5ea6"
                ],
                "dependencyTransactionIds": [
                    "c70e1829a7c6a2a8cb8cfc2383f8abf825ac5ea6"
                ],
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

    def response(self) -> dict[str, object]:
        return {
            "schemaVersion": 3,
            "subjectTransactionId": SUBJECT,
            "baseStateDigest": self.base["stateDigest"],
            "createdPrograms": [
                {
                    "id": NEW_PROGRAM,
                    "parentId": "root",
                    "title": "Tensorization of separately relaxed UV scalars",
                    "objective": "Determine whether blocking strengthens the separately relaxed UV scalars.",
                    "currentStateSummary": "The fixed theorem chain resolves the stated product and symmetry questions.",
                    "localResidualSummary": "No residual remains for the stated route; richer coupled UV systems are separate work.",
                    "status": "active",
                }
            ],
            "resultPlacements": [
                {
                    "resultId": "result-uv-average-product-additivity",
                    "primaryProgramId": NEW_PROGRAM,
                },
                {
                    "resultId": "result-uv-branchwise-symmetry-specialization",
                    "primaryProgramId": NEW_PROGRAM,
                },
            ],
            "createdProgramBoundaries": [
                {
                    "programId": NEW_PROGRAM,
                    "directResidualWorkScope": "Work on blocking of the two separately relaxed UV scalar rows.",
                    "activationCondition": "The reference program tests whether this UV relaxation improves under blocking.",
                    "stoppingCondition": "The product and symmetry behavior is resolved or the route is pruned.",
                    "independentVariationRationale": "This route can stop independently of the code-induced converse route.",
                }
            ],
            "rootBoundary": {
                "directResidualWorkScope": "Unrepresented terminal work and root integration.",
                "activationCondition": "The canonical exact-capacity problem remains open.",
                "stoppingCondition": "The root contract terminal condition is met.",
                "independentVariationRationale": "Root residual excludes represented child work.",
            },
            "createdProgramWithAccessAnnotations": [
                {
                    "programId": NEW_PROGRAM,
                    "directWorkHours": "500",
                    "conditionalIncidence": "0.4",
                    "rationale": "The accepted chain closes this route in the actual state, while the active package is retained for same-world accounting.",
                    "evidenceRefs": [CLAIM],
                }
            ],
            "rootWithAccessAnnotation": {
                "directWorkHours": "3600",
                "rationale": "The broad root residual is unchanged and excludes represented child work.",
                "evidenceRefs": [CLAIM],
            },
            "topologyRationale": "The UV blocking route has one continue-or-prune decision independent of the K1 portfolio; its two reusable results stay in one root-child program.",
        }

    def reduce(self, response: object) -> dict[str, object]:
        return reduce_joint_portfolio_wplus_response_v3(
            response,
            base_state=self.base,
            base_accounting_state=self.base_accounting,
            root_contract=self.contract,
            semantic_packet=self.packet,
            accepted_claims=self.claims,
            judgment_id=JUDGMENT,
            evidence_files=self.evidence,
        )

    def score(self, reduced: dict[str, object]) -> dict[str, object]:
        gold = json.loads(
            (EXPERIMENT / "relational-gold-v3.json").read_text(encoding="utf-8")
        )
        return _score_json_relational(
            gold,
            {
                "fixed-base-state": _scenario_artifact(self.base),
                "k2.author.transition": _scenario_artifact(reduced["transition"]),
                "k2.author.topology": _scenario_artifact(
                    state_summary(reduced["postState"], SUBJECT)
                ),
            },
            variant="joint-portfolio-wplus-v3",
            seed=1729,
            scorer_id="joint-portfolio-wplus-v3-test",
        )

    def test_v3_carries_k1_primitives_and_passes_k2_gold(self) -> None:
        reduced = self.reduce(self.response())
        self.assertEqual(reduced["withAccessState"]["totalWorkHours"], "4651.7375")
        self.assertEqual(self.score(reduced)["status"], "passed")
        before = {
            row["nodeRef"]["id"]: (
                row["directWorkHours"],
                row["conditionalIncidence"],
            )
            for row in self.base_accounting["annotations"]
        }
        after = {
            row["nodeRef"]["id"]: (
                row["directWorkHours"],
                row["conditionalIncidence"],
            )
            for row in reduced["withAccessState"]["annotations"]
        }
        for program_id in self.base["programs"]:
            self.assertEqual(after[program_id], before[program_id])

    def test_v3_requires_active_created_programs(self) -> None:
        response = self.response()
        response["createdPrograms"][0]["status"] = "completed"
        with self.assertRaisesRegex(MathFlowError, "program status is invalid"):
            self.reduce(response)

    def test_v3_does_not_mechanically_bake_the_k2_parent_answer(self) -> None:
        response = self.response()
        response["createdPrograms"][0][
            "parentId"
        ] = "program-bssc-code-induced-converse"
        reduced = self.reduce(response)
        self.assertEqual(self.score(reduced)["status"], "failed")

    def test_v3_provider_schema_is_active_only_and_uses_live_base(self) -> None:
        requests: list[dict[str, object]] = []

        def transport(request: dict[str, object]) -> dict[str, object]:
            requests.append(copy.deepcopy(request))
            return {
                "id": "joint-v3-response-1",
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
                / "protocol/judges/openrouter-joint-portfolio-wplus-experiment-v3.json"
            ).read_text(encoding="utf-8")
        )
        provider = OpenRouterJointPortfolioWPlusExperimentProviderV3(
            spec, transport=transport
        )
        artifacts = provider.run(
            problem_id="bssc-sum-capacity",
            subject_transaction_id=SUBJECT,
            base_state=self.base,
            base_accounting_state=self.base_accounting,
            root_contract=self.contract,
            semantic_packet=self.packet,
            accepted_claims=self.claims,
            judgment_id=JUDGMENT,
            evidence_files=self.evidence,
        )
        self.assertEqual(artifacts["withAccessState"]["totalWorkHours"], "4651.7375")
        schema = requests[0]["response_format"]["json_schema"]["schema"]
        status = schema["properties"]["createdPrograms"]["items"]["properties"][
            "status"
        ]
        self.assertEqual(status, {"type": "string", "const": "active"})
        user_message = requests[0]["messages"][-1]["content"]
        self.assertIn(
            str(self.base_accounting["stateDigest"]),
            user_message,
        )


if __name__ == "__main__":
    unittest.main()
