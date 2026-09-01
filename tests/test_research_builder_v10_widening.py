from __future__ import annotations

import copy
import json
import math
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from math_flow.errors import MathFlowError
from math_flow.research_builder_v10_widening import (
    WideningBudgets,
    load_bound_widening_spec,
    load_widening_manifest,
    materialize_widening_case,
    plan_widening_experiment,
    run_widening_experiment,
)


ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = (
    ROOT / "protocol/experiments/local-builder-v10-widening-v1/manifest.json"
)


def quoted_input(request: dict[str, object]) -> dict[str, object]:
    messages = request["messages"]
    assert isinstance(messages, list)
    for message in reversed(messages):
        content = message["content"]
        assert isinstance(content, str)
        if "<math-flow-input>\n" in content:
            return json.loads(
                content.split("<math-flow-input>\n", 1)[1].split(
                    "\n</math-flow-input>", 1
                )[0]
            )
    raise AssertionError("request has no quoted input")


class SemanticTeacherTransport:
    """A deterministic fake teacher that uses only model-visible route inputs."""

    def __init__(self, *, reject_first: bool = False) -> None:
        self.requests: list[dict[str, object]] = []
        self.reject_first = reject_first

    @staticmethod
    def _plan(user: dict[str, object]) -> dict[str, object]:
        context = user["routeContext"]
        assert isinstance(context, dict)
        claims = user["acceptedClaimAssessments"]
        assert isinstance(claims, list) and isinstance(claims[0], dict)
        summary = str(claims[0]["validitySummary"])
        clue = ""
        marker = "Accepted routing-relevant semantic description: "
        if marker in summary:
            clue = summary.split(marker, 1)[1].rstrip(".")
        search_query = clue
        if "revise both successors" in clue:
            search_query = "revision successor retired predecessor"

        inspect_programs = {"root"}
        inspect_results: set[str] = set()
        write_programs: set[str] = set()
        create_programs: list[str] = []
        search_queries = (
            [
                {
                    "query": search_query,
                    "entityKinds": ["intermediateResult", "program"],
                    "limit": 16,
                }
            ]
            if search_query
            else []
        )
        discovery = user.get("discoveryPacket")
        if isinstance(discovery, dict):
            search_results = discovery.get("searchResults")
            if isinstance(search_results, list):
                for result_set in search_results:
                    matches = (
                        result_set.get("matches")
                        if isinstance(result_set, dict)
                        else None
                    )
                    if not isinstance(matches, list):
                        continue
                    for match in matches:
                        if not isinstance(match, dict):
                            continue
                        entity_id = match.get("entityId")
                        if not isinstance(entity_id, str):
                            continue
                        if match.get("entityKind") == "program":
                            inspect_programs.add(entity_id)
                        else:
                            inspect_results.add(entity_id)
            capsules = discovery.get("programCapsules")
            if isinstance(capsules, dict):
                for program_id, capsule in capsules.items():
                    if not str(program_id).startswith("program/revision-"):
                        continue
                    linked = (
                        capsule.get("linkedResults")
                        if isinstance(capsule, dict)
                        else None
                    )
                    if isinstance(linked, list):
                        inspect_results.update(
                            str(item["entityId"])
                            for item in linked
                            if isinstance(item, dict)
                            and isinstance(item.get("entityId"), str)
                        )
        if "independent route" in clue:
            create_programs = ["program/proposed-independent-route"]
        if "revise both successors" in clue:
            revision_ids = {
                "program/revision-old",
                "program/revision-left",
                "program/revision-right",
            }
            inspect_programs.update(revision_ids)
            write_programs.update(revision_ids)
        return {
            "schemaVersion": 1,
            "baseStateDigest": context["baseStateDigest"],
            "routeContextDigest": context["contextDigest"],
            "inspectProgramIds": sorted(inspect_programs),
            "inspectResultIds": sorted(inspect_results),
            "searchQueries": search_queries,
            "writeProgramIds": sorted(write_programs),
            "writeResultIds": [],
            "createProgramIds": create_programs,
            "createResultIds": [],
        }

    def __call__(self, request: dict[str, object]) -> dict[str, object]:
        self.requests.append(copy.deepcopy(request))
        user = quoted_input(request)
        if self.reject_first and len(self.requests) == 1:
            value: dict[str, object] = {}
        else:
            value = self._plan(user)
        content = json.dumps(value, sort_keys=True)
        prompt_tokens = math.ceil(
            len(
                json.dumps(
                    request,
                    sort_keys=True,
                    separators=(",", ":"),
                    ensure_ascii=False,
                ).encode("utf-8")
            )
            / 4
        )
        completion_tokens = max(1, math.ceil(len(content.encode("utf-8")) / 4))
        return {
            "id": f"fake-widening-{len(self.requests)}",
            "model": "openai/gpt-5.6-sol",
            "choices": [
                {"finish_reason": "stop", "message": {"content": content}}
            ],
            "usage": {
                "prompt_tokens": prompt_tokens,
                "completion_tokens": completion_tokens,
                "total_tokens": prompt_tokens + completion_tokens,
                "completion_tokens_details": {"reasoning_tokens": 7},
                "cost": 0.01,
            },
        }


def small_manifest() -> tuple[dict[str, object], dict[str, object]]:
    manifest = load_widening_manifest(MANIFEST_PATH, repository_root=ROOT)
    chosen = [
        copy.deepcopy(manifest["cases"][0]),
        copy.deepcopy(manifest["cases"][1]),
        copy.deepcopy(manifest["cases"][-1]),
    ]
    for case in chosen:
        case["configuration"] = {
            "programCount": 12,
            "resultCount": 20,
            "maximumDepth": 3,
            "maximumWidth": 3,
            "provenancePerResult": 1,
            "dependencyDepth": 2,
            "dependencyWidth": 2,
            "supportBytes": 64,
            "summaryBytes": 64,
            "evidenceBytes": 256,
        }
    result = copy.deepcopy(manifest)
    result["cases"] = chosen
    result["budgets"]["maximumProviderCalls"] = 12
    result["budgets"]["maximumTotalReservedTokens"] = 6084288
    result["budgets"]["maximumTotalCostUsd"] = 3.0
    spec = load_bound_widening_spec(manifest, repository_root=ROOT)
    return result, spec


class ResearchBuilderV10WideningTests(unittest.TestCase):
    def test_repository_manifest_is_fail_closed_and_spec_bound(self) -> None:
        manifest = load_widening_manifest(MANIFEST_PATH, repository_root=ROOT)
        self.assertTrue(manifest["publicationForbidden"])
        self.assertEqual(manifest["providerExecutionDefault"], "disabled")
        self.assertEqual(
            manifest["judgeSpecDigest"],
            "sha256:47528dfd15010796f3d6aaa2500ad8ec07e499cfeb5b5fd6bcd0c8522dbebffd",
        )
        self.assertEqual(
            manifest["candidateJudgeSpecDigest"],
            "sha256:62e036b564b90e3739770897bdec60c92d860cf673b48b67dea05d9d656d54de",
        )
        self.assertEqual(
            [
                case["configuration"]["programCount"]
                for case in manifest["cases"]
                if case["phase"] == "widening"
            ],
            [16, 64, 256, 1024],
        )
        altered = copy.deepcopy(manifest)
        altered["publicationForbidden"] = False
        with self.assertRaisesRegex(MathFlowError, "must remain unpublished"):
            from math_flow.research_builder_v10_widening import (
                validate_widening_manifest,
            )

            validate_widening_manifest(altered, repository_root=ROOT)

        for unsafe_path in (
            "../openrouter-hierarchical-research-builder-v10-experiment.json",
            str(ROOT / "protocol/judges/openrouter-hierarchical-research-builder-v10-experiment.json"),
        ):
            with self.subTest(unsafe_path=unsafe_path):
                altered = copy.deepcopy(manifest)
                altered["judgeSpec"] = unsafe_path
                with self.assertRaisesRegex(MathFlowError, "repository-relative"):
                    validate_widening_manifest(altered, repository_root=ROOT)

    def test_plan_is_provider_free_and_records_widening_context(self) -> None:
        manifest, spec = small_manifest()
        report = plan_widening_experiment(manifest, spec=spec)
        self.assertEqual(report["providerCalls"], 0)
        self.assertTrue(report["publicationForbidden"])
        self.assertEqual(len(report["cases"]), 3)
        self.assertTrue(
            all(
                case["routeContextMeasurement"]["utf8Bytes"] > 0
                for case in report["cases"]
            )
        )

    def test_runtime_rejects_a_mutated_candidate_prompt(self) -> None:
        manifest, spec = small_manifest()
        altered = copy.deepcopy(spec)
        altered["systemPrompt"] = str(altered["systemPrompt"]) + " mutated"
        with self.assertRaisesRegex(MathFlowError, "candidate judge changed"):
            plan_widening_experiment(manifest, spec=altered)

    def test_fake_route_refine_suite_records_boundary_usage_and_retry(self) -> None:
        manifest, spec = small_manifest()
        teacher = SemanticTeacherTransport(reject_first=True)
        report = run_widening_experiment(
            manifest, spec=spec, transport=teacher
        )
        self.assertEqual(report["status"], "passed")
        self.assertEqual(report["casesCompleted"], 3)
        self.assertEqual(report["authorStageInvocations"], 0)
        self.assertFalse(report["publicationAttempted"])
        telemetry = report["telemetry"]
        self.assertEqual(telemetry["providerCalls"], 7)
        self.assertEqual(len(telemetry["requestRecords"]), 7)
        self.assertTrue(
            all(record["stage"] in {"route", "route-refine"} for record in telemetry["requestRecords"])
        )
        self.assertTrue(
            all(record["usage"]["costUsd"] == 0.01 for record in telemetry["requestRecords"])
        )
        self.assertGreater(len(report["attemptJournals"]), 6)
        limitation = report["caseReports"][-1]["score"]
        self.assertTrue(limitation["hardPassed"])
        self.assertFalse(
            limitation["advisory"]["routingRecoveredDespiteWithheldClue"]
        )
        self.assertTrue(
            limitation["hardChecks"]["clueAbsentFromEveryRouteRequest"]
        )

    def test_call_ceiling_blocks_before_an_extra_transport_call(self) -> None:
        manifest, spec = small_manifest()
        manifest["cases"] = manifest["cases"][:1]
        manifest["budgets"]["maximumProviderCalls"] = 1
        manifest["budgets"]["maximumTotalReservedTokens"] = 507024
        manifest["budgets"]["maximumTotalCostUsd"] = 0.25
        teacher = SemanticTeacherTransport()
        report = run_widening_experiment(
            manifest, spec=spec, transport=teacher
        )
        self.assertEqual(report["status"], "failed")
        self.assertEqual(len(teacher.requests), 1)
        self.assertEqual(report["telemetry"]["providerCalls"], 1)
        self.assertGreaterEqual(report["telemetry"]["blockedAttempts"], 1)
        self.assertIn("provider-call budget", report["failure"]["summary"])

    def test_request_ceiling_blocks_before_any_transport_call(self) -> None:
        manifest, spec = small_manifest()
        manifest["cases"] = manifest["cases"][:1]
        manifest["budgets"].update(
            {
                "maximumProviderCalls": 1,
                "maximumRequestBytes": 10,
                "maximumEstimatedPromptTokens": 3,
                "maximumConservativePromptTokens": 1034,
                "maximumTotalReservedTokens": 7034,
                "maximumTotalCostUsd": 0.25,
            }
        )
        teacher = SemanticTeacherTransport()
        report = run_widening_experiment(
            manifest, spec=spec, transport=teacher
        )
        self.assertEqual(report["status"], "failed")
        self.assertEqual(teacher.requests, [])
        self.assertEqual(report["telemetry"]["providerCalls"], 0)
        self.assertGreaterEqual(report["telemetry"]["blockedAttempts"], 1)

    def test_missing_cost_telemetry_blocks_all_later_calls(self) -> None:
        manifest, spec = small_manifest()
        manifest["cases"] = manifest["cases"][:1]
        manifest["budgets"]["maximumProviderCalls"] = 4
        manifest["budgets"]["maximumTotalReservedTokens"] = 2028096
        manifest["budgets"]["maximumTotalCostUsd"] = 1.0
        teacher = SemanticTeacherTransport()

        def missing_cost(request: dict[str, object]) -> dict[str, object]:
            response = teacher(request)
            del response["usage"]["cost"]
            return response

        report = run_widening_experiment(
            manifest, spec=spec, transport=missing_cost
        )
        self.assertEqual(report["status"], "failed")
        self.assertEqual(len(teacher.requests), 1)
        self.assertIn("cost telemetry", report["failure"]["summary"])
        self.assertIsNotNone(report["telemetry"]["blockedReason"])

    def test_cli_provider_mode_requires_authorization_before_output_creation(self) -> None:
        from experiments.research_builder_v10_widening import main

        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / "not-created"
            with patch.dict(
                "os.environ",
                {"MATH_FLOW_V10_WIDENING_AUTHORIZATION": "wrong"},
                clear=False,
            ):
                with self.assertRaisesRegex(MathFlowError, "requires exact"):
                    main(["--execute-provider", "--output-dir", str(output)])
            self.assertFalse(output.exists())

    def test_evidence_only_case_places_clue_only_in_evidence(self) -> None:
        manifest, _ = small_manifest()
        case = manifest["cases"][-1]
        fixture = materialize_widening_case(case)
        clue = fixture["semanticClue"]
        self.assertIn(clue, json.dumps(fixture["submissionEvidence"]))
        self.assertNotIn(clue, json.dumps(fixture["acceptedClaims"]))

    def test_hot_branch_case_has_64_step_history_without_topology_growth(self) -> None:
        manifest = load_widening_manifest(MANIFEST_PATH, repository_root=ROOT)
        case = next(
            item
            for item in manifest["cases"]
            if item["phase"] == "sequential-growth"
        )
        fixture = materialize_widening_case(case)
        growth = fixture["sequentialGrowth"]
        self.assertEqual(growth["historySteps"], 64)
        self.assertFalse(growth["topologyChanged"])
        target = fixture["state"]["intermediateResults"][growth["hotResultId"]]
        self.assertEqual(len(target["sourceTransactionIds"]), 64)
        self.assertEqual(len(target["claimRefs"]), 64)
        self.assertEqual(len(target["judgmentIds"]), 64)

    def test_packet_reports_semantic_table_capsule_duplication(self) -> None:
        manifest, spec = small_manifest()
        manifest["cases"] = manifest["cases"][:1]
        manifest["budgets"]["maximumProviderCalls"] = 4
        manifest["budgets"]["maximumTotalReservedTokens"] = 2028096
        manifest["budgets"]["maximumTotalCostUsd"] = 1.0
        report = run_widening_experiment(
            manifest, spec=spec, transport=SemanticTeacherTransport()
        )
        self.assertEqual(report["status"], "passed")
        case_report = report["caseReports"][0]
        for field in (
            "discoveryPacketEntityDuplication",
            "authoringPacketEntityDuplication",
        ):
            duplication = case_report[field]
            self.assertGreater(duplication["entityOccurrences"], 0)
            self.assertGreater(duplication["duplicateEntityOccurrences"], 0)
            self.assertGreater(duplication["repeatedEntityBytesAfterFirst"], 0)

    def test_budget_contract_requires_full_reservations(self) -> None:
        manifest, _ = small_manifest()
        budgets = copy.deepcopy(manifest["budgets"])
        budgets["maximumTotalCostUsd"] = 0.01
        with self.assertRaisesRegex(MathFlowError, "cannot cover every"):
            WideningBudgets.from_mapping(budgets)


if __name__ == "__main__":
    unittest.main()
