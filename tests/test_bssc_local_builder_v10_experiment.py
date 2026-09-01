from __future__ import annotations

import copy
import json
import unittest
from pathlib import Path

from experiments.bssc_local_builder_v10 import (
    BudgetedCapturingTransport,
    _scenario_artifact,
)
from math_flow.errors import MathFlowError
from math_flow.teacher_student_scenarios import _score_json_relational


ROOT = Path(__file__).resolve().parents[1]


class BudgetedCapturingTransportTests(unittest.TestCase):
    def response(self, cost: object) -> dict[str, object]:
        return {
            "choices": [{"finish_reason": "stop", "message": {"content": "{}"}}],
            "usage": {
                "cost": cost,
                "prompt_tokens": 10,
                "completion_tokens": 10,
                "total_tokens": 20,
            },
        }

    def test_reserves_single_call_ceiling_before_spending(self) -> None:
        calls = []

        def inner(request: dict[str, object]) -> dict[str, object]:
            calls.append(request)
            return self.response(0.75)

        transport = BudgetedCapturingTransport(
            maximum_calls=5,
            maximum_cost_usd=1.0,
            maximum_single_call_cost_usd=0.75,
            maximum_request_bytes=1000,
            maximum_total_tokens=10000,
            transport=inner,
        )
        transport({"attempt": 1, "max_tokens": 100})
        with self.assertRaisesRegex(MathFlowError, "cost budget exhausted"):
            transport({"attempt": 2, "max_tokens": 100})
        self.assertEqual(len(calls), 1)
        self.assertEqual(transport.reported_cost_usd, 0.75)

    def test_missing_or_excessive_cost_blocks_all_followups(self) -> None:
        responses = iter([self.response(None), self.response(0.01)])
        transport = BudgetedCapturingTransport(
            maximum_calls=5,
            maximum_cost_usd=3.0,
            maximum_single_call_cost_usd=0.75,
            maximum_request_bytes=1000,
            maximum_total_tokens=10000,
            transport=lambda request: next(responses),
        )
        with self.assertRaisesRegex(MathFlowError, "omitted valid cost telemetry"):
            transport({"attempt": 1, "max_tokens": 100})
        with self.assertRaisesRegex(MathFlowError, "omitted valid cost telemetry"):
            transport({"attempt": 2, "max_tokens": 100})
        self.assertEqual(len(transport.requests), 1)

        expensive = BudgetedCapturingTransport(
            maximum_calls=5,
            maximum_cost_usd=3.0,
            maximum_single_call_cost_usd=0.75,
            maximum_request_bytes=1000,
            maximum_total_tokens=10000,
            transport=lambda request: self.response(0.80),
        )
        with self.assertRaisesRegex(MathFlowError, "single-call cost ceiling"):
            expensive({"attempt": 1, "max_tokens": 100})
        with self.assertRaisesRegex(MathFlowError, "single-call cost ceiling"):
            expensive({"attempt": 2, "max_tokens": 100})
        self.assertEqual(len(expensive.requests), 1)

    def test_oversized_request_fails_before_transport(self) -> None:
        calls = []
        transport = BudgetedCapturingTransport(
            maximum_calls=5,
            maximum_cost_usd=3.0,
            maximum_single_call_cost_usd=0.75,
            maximum_request_bytes=32,
            maximum_total_tokens=10000,
            transport=lambda request: calls.append(request) or self.response(0.01),
        )
        with self.assertRaisesRegex(MathFlowError, "request budget exhausted"):
            transport({"payload": "x" * 100})
        self.assertEqual(calls, [])
        self.assertEqual(transport.requests, [])


class RevisedAccountingGoldTests(unittest.TestCase):
    def test_non_main_workflow_targets_the_final_k2_only_v3_manifest(self) -> None:
        workflow = (
            ROOT / ".github/workflows/project-research-v7-serial.yml"
        ).read_text(encoding="utf-8")
        self.assertIn(
            "--manifest protocol/experiments/bssc-local-builder-v10-v3/manifest.json",
            workflow,
        )
        self.assertIn(
            '--output "${RUNNER_TEMP}/bssc-local-builder-v10-v3"',
            workflow,
        )
        self.assertNotIn(
            '--output "${RUNNER_TEMP}/bssc-local-builder-v10-v2"',
            workflow,
        )
        self.assertNotIn(
            '--output "${RUNNER_TEMP}/bssc-local-builder-v10-v1"',
            workflow,
        )

    def test_accepts_root_owned_replay_and_rejects_k1_nesting(self) -> None:
        gold = json.loads(
            (
                ROOT
                / "protocol/experiments/bssc-local-builder-v10-v2/relational-gold-v2.json"
            ).read_text(encoding="utf-8")
        )
        fixed = json.loads(
            (
                ROOT
                / "protocol/experiments/bssc-credit-topology-v3/fixtures/k1-refined-seed-2718-state.json"
            ).read_text(encoding="utf-8")
        )
        transition = json.loads(
            (
                ROOT
                / "protocol/experiments/bssc-credit-topology-v3/replay/seed-1729/k2/transition.json"
            ).read_text(encoding="utf-8")
        )
        topology = json.loads(
            (
                ROOT
                / "protocol/experiments/bssc-credit-topology-v3/replay/seed-1729/k2/topology-summary.json"
            ).read_text(encoding="utf-8")
        )

        def score(candidate_transition: object, candidate_topology: object) -> dict:
            return _score_json_relational(
                gold,
                {
                    "fixed-base-state": _scenario_artifact(fixed),
                    "k2.author.transition": _scenario_artifact(candidate_transition),
                    "k2.author.topology": _scenario_artifact(candidate_topology),
                },
                variant="local-builder-v10",
                seed=1729,
                scorer_id="bssc-accounting-topology-v10-v2",
            )

        accepted = score(transition, topology)
        self.assertEqual(accepted["status"], "passed")
        self.assertEqual(accepted["hardFailures"], [])

        nested_transition = copy.deepcopy(transition)
        nested_topology = copy.deepcopy(topology)
        created_program_ids = {
            operation["entityId"]
            for operation in nested_transition["topologyOperations"]
            if operation["entityKind"] == "program"
        }
        nested_transition["topologyOperations"] = [
            operation
            for operation in nested_transition["topologyOperations"]
            if operation["entityKind"] != "program"
        ]
        nested_transition["contribution"]["directProgramIds"] = [
            "program-channel-specific-converse-refinement"
        ]
        nested_topology["programs"] = [
            program
            for program in nested_topology["programs"]
            if program["id"] not in created_program_ids
        ]
        for result in nested_topology["subjectResults"]:
            result["primaryProgramId"] = (
                "program-channel-specific-converse-refinement"
            )

        rejected = score(nested_transition, nested_topology)
        self.assertEqual(rejected["status"], "failed")
        self.assertIn("k2-adds-one-root-child-program", rejected["hardFailures"])
        self.assertIn("k2-direct-program-is-new-root-child", rejected["hardFailures"])


if __name__ == "__main__":
    unittest.main()
