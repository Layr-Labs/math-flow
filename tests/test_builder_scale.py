from __future__ import annotations

import unittest

from math_flow.builder_scale import (
    SyntheticBuilderStateConfig,
    build_bounded_local_packet_model,
    build_positioned_semantic_probe,
    build_synthetic_builder_fixture,
    classify_capacity_outcome,
    make_v10_context_strategy,
    measure_provenance_growth,
    run_provider_free_builder_context_scale_probe,
    score_adversarial_route_plan,
    score_positioned_semantic_probe,
)
from math_flow.errors import MathFlowError
from math_flow.research_builder_v7 import validate_research_program_state_v3
from math_flow.research_builder_v10 import (
    build_research_builder_v10_authoring_packet,
    build_research_builder_v10_route_context,
)


class BuilderScaleTests(unittest.TestCase):
    def configuration(
        self,
        *,
        programs: int = 16,
        results: int = 24,
        provenance: int = 2,
    ) -> SyntheticBuilderStateConfig:
        return SyntheticBuilderStateConfig(
            program_count=programs,
            result_count=results,
            maximum_depth=4,
            maximum_width=3,
            provenance_per_result=provenance,
            dependency_depth=2,
            dependency_width=2,
        )

    def test_generates_a_valid_state_with_independent_dimensions(self) -> None:
        fixture = build_synthetic_builder_fixture(self.configuration())
        state = validate_research_program_state_v3(fixture["state"])
        self.assertEqual(len(state["programs"]), 16)
        self.assertEqual(len(state["intermediateResults"]), 24)
        self.assertEqual(len(state["contributions"]), 48)
        self.assertEqual(
            set(fixture["challenges"]),
            {
                "dependency-closure",
                "distant-duplicate",
                "cross-program-placement",
                "root-sibling",
                "misleading-capsule",
                "topology-revision",
            },
        )

    def test_dependency_challenge_precommits_the_transitive_closure(self) -> None:
        fixture = build_synthetic_builder_fixture(self.configuration())
        challenge = fixture["challenges"]["dependency-closure"]
        self.assertEqual(len(challenge["requiredResultIds"]), 5)
        packet = build_bounded_local_packet_model(fixture)
        results = packet["author"]["authoringPacket"]["intermediateResults"]
        self.assertEqual(set(results), set(challenge["requiredResultIds"]))

    def test_topology_revision_is_reciprocal_and_has_atomic_gold(self) -> None:
        fixture = build_synthetic_builder_fixture(self.configuration())
        state = fixture["state"]
        old = state["programs"]["program/revision-old"]
        self.assertEqual(old["status"], "retired")
        self.assertEqual(
            {item["programId"] for item in old["lineage"]},
            {"program/revision-left", "program/revision-right"},
        )
        challenge = fixture["challenges"]["topology-revision"]
        complete = score_adversarial_route_plan(
            fixture,
            "topology-revision",
            {
                "selectedProgramIds": challenge["requiredProgramIds"],
                "selectedResultIds": challenge["requiredResultIds"],
                "requestedWriteIds": challenge["requiredWriteEntityIds"],
            },
        )
        incomplete = score_adversarial_route_plan(
            fixture,
            "topology-revision",
            {
                "selectedProgramIds": challenge["successorProgramIds"][:1],
                "selectedResultIds": challenge["requiredResultIds"],
                "requestedWriteIds": [],
            },
        )
        self.assertTrue(complete["passed"])
        self.assertFalse(incomplete["passed"])
        self.assertTrue(incomplete["missingWriteIds"])

    def test_provenance_telemetry_covers_root_ancestors_and_results(self) -> None:
        fixture = build_synthetic_builder_fixture(self.configuration(provenance=4))
        report = measure_provenance_growth(fixture["state"])
        occurrences = report["occurrences"]
        self.assertEqual(occurrences["rootSourceTransactions"], 96)
        self.assertEqual(occurrences["resultSourceTransactions"], 96)
        self.assertEqual(occurrences["resultClaimReferences"], 96)
        self.assertEqual(occurrences["resultJudgments"], 96)
        self.assertGreater(occurrences["nonRootProgramSourceTransactions"], 96)
        self.assertGreater(report["allProvenance"]["utf8Bytes"], 0)

    def test_bounded_semantic_packet_avoids_cumulative_provenance(self) -> None:
        fixture = build_synthetic_builder_fixture(self.configuration(provenance=8))
        semantic = build_bounded_local_packet_model(
            fixture, include_exact_provenance=False
        )
        exact = build_bounded_local_packet_model(
            fixture, include_exact_provenance=True
        )
        semantic_text = str(semantic["author"])
        exact_text = str(exact["author"])
        source_transaction = fixture["state"]["programs"]["root"][
            "sourceTransactionIds"
        ][0]
        self.assertIn("provenanceCounts", semantic_text)
        self.assertIn("supportDigest", semantic_text)
        self.assertNotIn("Proof support for", semantic_text)
        self.assertNotIn(source_transaction, semantic_text)
        self.assertIn(source_transaction, exact_text)
        self.assertNotIn("submissionEvidence", str(semantic["route"]))
        self.assertNotIn("submissionEvidence", str(semantic["route-refine"]))

    def test_probe_compares_all_core_and_bounded_views_without_calls(self) -> None:
        report = run_provider_free_builder_context_scale_probe(
            [
                self.configuration(programs=16, results=24, provenance=1),
                self.configuration(programs=64, results=96, provenance=4),
            ],
            input_budget_tokens=128_000,
        )
        self.assertEqual(report["status"], "passed")
        self.assertEqual(report["providerCalls"], 0)
        self.assertTrue(all(report["verifiedInvariants"].values()))
        first, second = report["cases"]
        for case in (first, second):
            comparison = case["comparisons"]["bounded-semantic"]
            self.assertLess(comparison["maximumStageRatioToV9"], 1)
        self.assertGreater(
            second["comparisons"]["v9ProvenanceOverhead"][
                "estimatedProvenanceOverheadPercent"
            ],
            first["comparisons"]["v9ProvenanceOverhead"][
                "estimatedProvenanceOverheadPercent"
            ],
        )

    def test_custom_context_strategy_uses_the_adapter_boundary(self) -> None:
        def custom(fixture: object, challenge: str) -> dict[str, dict[str, object]]:
            self.assertEqual(challenge, "dependency-closure")
            return {"route": {"constantPacket": {"schemaVersion": 1}}}

        report = run_provider_free_builder_context_scale_probe(
            [self.configuration()],
            strategies={"custom": custom},
        )
        self.assertIn("custom", report["cases"][0]["strategies"])
        self.assertFalse(
            report["verifiedInvariants"]["fullV9AndBoundedPacketsCompared"]
        )

    def test_v10_adapter_builds_the_exact_raw_route_plan_contract(self) -> None:
        observed = {}

        def route_builder(state: object, claims: object) -> dict[str, object]:
            return {
                "baseStateDigest": state["stateDigest"],
                "contextDigest": "sha256:" + "a" * 64,
            }

        def author_builder(
            state: object,
            claims: object,
            route_plan: dict[str, object],
            *,
            route_context: dict[str, object],
        ) -> dict[str, object]:
            observed.update(route_plan)
            self.assertEqual(
                route_plan["routeContextDigest"], route_context["contextDigest"]
            )
            return {"routePlan": route_plan, "packetDigest": "sha256:" + "b" * 64}

        fixture = build_synthetic_builder_fixture(self.configuration())
        strategy = make_v10_context_strategy(route_builder, author_builder)
        view = strategy(fixture, "topology-revision")
        self.assertEqual(set(view), {"route", "route-refine", "author"})
        self.assertNotIn("submissionEvidence", view["route"])
        self.assertNotIn("submissionEvidence", view["route-refine"])
        self.assertIn("submissionEvidence", view["author"])
        self.assertEqual(
            set(observed),
            {
                "schemaVersion",
                "baseStateDigest",
                "routeContextDigest",
                "inspectProgramIds",
                "inspectResultIds",
                "searchQueries",
                "writeProgramIds",
                "writeResultIds",
                "createProgramIds",
                "createResultIds",
            },
        )
        self.assertEqual(
            set(observed["writeProgramIds"]),
            {
                "program/revision-old",
                "program/revision-left",
                "program/revision-right",
            },
        )

    def test_actual_v10_strategy_remains_bounded_without_route_evidence(self) -> None:
        strategy = make_v10_context_strategy(
            build_research_builder_v10_route_context,
            build_research_builder_v10_authoring_packet,
        )
        report = run_provider_free_builder_context_scale_probe(
            [self.configuration(programs=64, results=96, provenance=4)],
            strategies={"v10-actual": strategy},
        )
        measured = report["cases"][0]["strategies"]["v10-actual"]
        self.assertLess(measured["maximumStageEstimatedTokens"], 128_000)
        self.assertEqual(
            measured["stages"]["route"]["components"][
                "acceptedClaimAssessments"
            ]["utf8Bytes"],
            measured["stages"]["route-refine"]["components"][
                "acceptedClaimAssessments"
            ]["utf8Bytes"],
        )
    def test_positioned_soft_semantic_probes_keep_the_same_gold(self) -> None:
        fixture = build_synthetic_builder_fixture(self.configuration())
        expected = None
        for position in ("beginning", "middle", "end"):
            probe = build_positioned_semantic_probe(
                fixture, "distant-duplicate", position
            )
            if expected is None:
                expected = probe["expectedEntityIds"]
            self.assertEqual(probe["expectedEntityIds"], expected)
            self.assertTrue(
                score_positioned_semantic_probe(
                    probe, probe["expectedEntityIds"]
                )["passed"]
            )
            self.assertFalse(score_positioned_semantic_probe(probe, [])["passed"])

    def test_capacity_classifier_keeps_three_failure_classes_distinct(self) -> None:
        input_failure = classify_capacity_outcome(
            prompt="x" * 8_000,
            input_budget_tokens=1_000,
            completion_limit_tokens=4_000,
        )
        output_failure = classify_capacity_outcome(
            prompt="small",
            input_budget_tokens=1_000,
            completion_limit_tokens=100,
            output_text="{}" + " " * 2_000,
            finish_reason="length",
            provider_completion_tokens=100,
        )
        soft_failure = classify_capacity_outcome(
            prompt="small",
            input_budget_tokens=1_000,
            completion_limit_tokens=100,
            output_text="{}",
            semantic_checks={"distantDuplicateFound": False},
        )
        self.assertEqual(input_failure["classification"], "hard-input-exhaustion")
        self.assertEqual(output_failure["classification"], "hard-output-exhaustion")
        self.assertTrue(output_failure["outputPathologyObserved"])
        self.assertEqual(
            soft_failure["classification"], "soft-semantic-degradation"
        )

    def test_local_packet_fails_instead_of_truncating_dependency_closure(self) -> None:
        fixture = build_synthetic_builder_fixture(self.configuration())
        with self.assertRaisesRegex(MathFlowError, "dependency closure exceeds"):
            build_bounded_local_packet_model(
                fixture,
                maximum_exact_results=4,
            )


if __name__ == "__main__":
    unittest.main()
