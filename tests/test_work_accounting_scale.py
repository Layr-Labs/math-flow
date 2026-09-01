from __future__ import annotations

import hashlib
import json
import unittest
from pathlib import Path

from math_flow.errors import MathFlowError
from math_flow.repository import sha256_json
from math_flow.work_accounting_scale import (
    SCENARIOS,
    WorkAccountingScaleConfig,
    build_work_accounting_scale_case,
    measure_serialized_value,
    run_provider_free_work_accounting_scale_probe,
)


SMALL = WorkAccountingScaleConfig(16, 24, 3, 4, evidence_bytes=512)


class WorkAccountingScaleTests(unittest.TestCase):
    def test_serialized_measurement_labels_estimates(self) -> None:
        measured = measure_serialized_value({"alpha": "beta"})
        self.assertEqual(measured["utf8Bytes"], 16)
        self.assertEqual(measured["estimatedTokens"], 4)
        self.assertIn("compact-json", measured["estimatedTokenMethod"])
        self.assertEqual(
            measured["conservativeTokenUpperBound"], measured["utf8Bytes"]
        )

    def test_all_adversarial_scenarios_use_real_v2_builders_without_provider(self) -> None:
        for scenario in SCENARIOS:
            with self.subTest(scenario=scenario):
                case = build_work_accounting_scale_case(SMALL, scenario)
                self.assertTrue(case["semanticAdversarialClassification"]["passed"])
                self.assertEqual(case["providerActivity"]["externalProviderCalls"], 0)
                self.assertFalse(case["providerActivity"]["networkUsed"])
                self.assertEqual(
                    set(case["stages"]), {"safe-facts", "with-access", "no-access"}
                )
                self.assertEqual(
                    case["capacityClassification"]["maximumStage"], "no-access"
                )
                no_components = case["stages"]["no-access"]["components"]
                self.assertIn("frozenWithAccessState", no_components)
                self.assertEqual(
                    no_components["rawSubmissionEvidence"]["rawBytes"], 0
                )
                self.assertGreater(
                    case["stages"]["with-access"]["components"][
                        "rawSubmissionEvidence"
                    ]["rawBytes"],
                    0,
                )
                self.assertEqual(
                    no_components["baseAccountingState"],
                    case["stages"]["with-access"]["components"][
                        "baseAccountingState"
                    ],
                )

    def test_capacity_crossing_is_independent_of_semantic_classification(self) -> None:
        case = build_work_accounting_scale_case(
            SMALL,
            "solving-zero-out",
            input_budget_tokens=100,
        )
        self.assertTrue(
            case["capacityClassification"][
                "estimatedInputBudgetCrossedUnderModelInputProxy"
            ]
        )
        self.assertTrue(case["semanticAdversarialClassification"]["passed"])
        self.assertTrue(
            case["semanticAdversarialClassification"]["checks"][
                "withAccessCompletedNodeZeroed"
            ]
        )
        self.assertTrue(
            case["semanticAdversarialClassification"]["checks"][
                "noAccessCompletedNodeMayRetainWork"
            ]
        )

    def test_dependency_and_topology_cases_exercise_relational_structure(self) -> None:
        dependency = build_work_accounting_scale_case(SMALL, "dependency-closure")
        topology = build_work_accounting_scale_case(SMALL, "topology-revision")
        self.assertTrue(
            dependency["semanticAdversarialClassification"]["checks"][
                "preexpandedDependencyScopeRetained"
            ]
        )
        self.assertEqual(
            dependency["stateShape"]["dependencySeedPolicy"],
            "preexpanded-result-owner-programs",
        )
        self.assertTrue(
            topology["semanticAdversarialClassification"]["checks"][
                "topologyMoveAlignedAndReanchored"
            ]
        )
        self.assertGreater(topology["stateShape"]["withAccessRequiredUpdateCount"], 0)
        self.assertGreater(topology["stateShape"]["noAccessRequiredUpdateCount"], 0)

    def test_probe_report_is_digest_bound_and_provider_free(self) -> None:
        report = run_provider_free_work_accounting_scale_probe(
            [SMALL],
            scenarios=("dependency-closure", "broad-local-subtree"),
        )
        self.assertEqual(report["caseCount"], 2)
        self.assertEqual(report["providerCalls"], 0)
        self.assertFalse(report["networkUsed"])
        self.assertTrue(report["summary"]["allSemanticAdversarialChecksPass"])
        self.assertRegex(report["reportDigest"], r"^sha256:[0-9a-f]{64}$")
        core = {key: value for key, value in report.items() if key != "reportDigest"}
        self.assertEqual(report["reportDigest"], "sha256:" + sha256_json(core))

    def test_invalid_configuration_and_scenario_fail_closed(self) -> None:
        with self.assertRaisesRegex(MathFlowError, "out of range"):
            WorkAccountingScaleConfig(2, 24, 3, 4).validate()
        with self.assertRaisesRegex(MathFlowError, "unsupported"):
            build_work_accounting_scale_case(SMALL, "unknown")
        with self.assertRaisesRegex(MathFlowError, "needs cases"):
            run_provider_free_work_accounting_scale_probe([])

    def test_checked_in_full_scale_report_regenerates_exactly(self) -> None:
        report = run_provider_free_work_accounting_scale_probe(
            input_budget_tokens=128_000
        )
        regenerated = (json.dumps(report, indent=2, sort_keys=True) + "\n").encode()
        checked_in = (
            Path(__file__).resolve().parents[1]
            / "protocol/experiments/work-accounting-context-scale-v1/provider-free-report.json"
        ).read_bytes()
        self.assertEqual(hashlib.sha256(regenerated).digest(), hashlib.sha256(checked_in).digest())
        self.assertEqual(len(regenerated), len(checked_in))


if __name__ == "__main__":
    unittest.main()
