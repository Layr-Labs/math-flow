from __future__ import annotations

import json
import tempfile
import unittest
import copy
from pathlib import Path
from unittest.mock import patch

from math_flow.artifacts import verify_bundle
from math_flow.bssc_research_v8_producer import plan_bssc_research_v8_frontier
from math_flow.cli import main
from math_flow.coordination import (
    claim_due_build,
    complete_build,
    publish_batch,
    record_completed_inputs,
)
from math_flow.judges import load_judge_spec
from math_flow.repository import sha256_json
from math_flow.research_projection import run_research_build_bundle
from math_flow.work_accounting_research_v10 import (
    load_published_research_v10_transition,
)


ROOT = Path(__file__).resolve().parents[1]
SOURCE_PATH = ROOT / "protocol/runtime/bssc-research-v4-validity-source-v1.json"
SOURCE = json.loads(SOURCE_PATH.read_text(encoding="utf-8"))
PROJECTION_PATH = ROOT / "protocol/runtime/openrouter-research-v8-projection.json"
PROJECTION = json.loads(PROJECTION_PATH.read_text(encoding="utf-8"))
FIRST_SUBJECT = "c70e1829a7c6a2a8cb8cfc2383f8abf825ac5ea6"
FIRST_JUDGMENT_RUN = (
    "sha256:fd6e2748ffa7a88e1b992001d4a36cfed0194c2ee608acf68907286e7facd0fe"
)


def _response(content: object) -> dict[str, object]:
    return {
        "id": "fixture-response-v10",
        "model": "openai/gpt-5.6-sol",
        "usage": {"prompt_tokens": 1, "completion_tokens": 1},
        "choices": [
            {"finish_reason": "stop", "message": {"content": json.dumps(content)}}
        ],
    }


def _v10_transport(request: dict[str, object]) -> dict[str, object]:
    content = str(request["messages"][-1]["content"])
    payload = json.loads(
        content.split("<math-flow-input>\n", 1)[1].split(
            "\n</math-flow-input>", 1
        )[0]
    )
    role = payload["role"]
    subject = str(payload["subjectTransactionId"])
    program_id = "program/code-induced-structure"
    result_id = "result/code-induced-structure"
    if role in {
        "builder-v10-local-portfolio-router",
        "builder-v10-local-portfolio-route-refiner",
    }:
        route_context = payload["routeContext"]
        return _response(
            {
                "schemaVersion": 1,
                "baseStateDigest": route_context["baseStateDigest"],
                "routeContextDigest": route_context["contextDigest"],
                "inspectProgramIds": ["root"],
                "inspectResultIds": [],
                "searchQueries": [],
                "writeProgramIds": ["root"],
                "writeResultIds": [],
                "createProgramIds": [program_id],
                "createResultIds": [result_id],
            }
        )

    packet = payload["authoringPacket"]
    root_view = packet["programs"]["root"]
    claims = payload["acceptedClaimAssessments"]
    judgment_id = str(payload["judgmentId"])
    evidence_path = str(payload["submissionEvidence"]["files"][0]["path"])
    root = {
        "id": "root",
        "parentId": None,
        "title": root_view["title"],
        "objective": root_view["objective"],
        "currentStateSummary": "The first accepted structural route is established.",
        "localResidualSummary": "The canonical objective remains open.",
        "status": "active",
        "intermediateResultIdAdditions": [],
        "intermediateResultIdRemovals": [],
        "sourceTransactionIds": [subject],
        "lineage": copy.deepcopy(root_view["lineage"]),
    }
    return _response(
        {
            "schemaVersion": 1,
            "subjectTransactionId": subject,
            "baseStateDigest": packet["baseStateDigest"],
            "contentOperations": [
                {
                    "entityKind": "program",
                    "entityId": "root",
                    "baseDigest": None,
                    "value": root,
                }
            ],
            "topologyOperations": [
                {
                    "action": "create",
                    "entityKind": "program",
                    "entityId": program_id,
                    "baseDigest": None,
                    "value": {
                        "id": program_id,
                        "parentId": "root",
                        "title": "Code-induced structural route",
                        "objective": "Develop the accepted structural route.",
                        "currentStateSummary": "The opening structural result is established.",
                        "localResidualSummary": "The route retains unresolved local work.",
                        "status": "active",
                        "intermediateResultIdAdditions": [result_id],
                        "intermediateResultIdRemovals": [],
                        "sourceTransactionIds": [subject],
                        "lineage": [],
                    },
                },
                {
                    "action": "create",
                    "entityKind": "intermediateResult",
                    "entityId": result_id,
                    "baseDigest": None,
                    "value": {
                        "id": result_id,
                        "primaryProgramId": program_id,
                        "relatedProgramIds": [],
                        "title": "Code-induced structural result",
                        "statement": str(claims[0]["validitySummary"]),
                        "scopeQualifications": copy.deepcopy(
                            claims[0]["scopeQualifications"]
                        ),
                        "supportAdditions": {
                            "proofs": ["The accepted submission supplies the proof."],
                            "methods": [],
                            "computations": [],
                            "tools": [],
                            "artifactPaths": [evidence_path],
                            "attestationRefs": [],
                        },
                        "dependencyResultIds": [],
                        "claimRefs": [
                            {
                                "transactionId": subject,
                                "claimKey": str(claim["claimKey"]),
                            }
                            for claim in claims
                        ],
                        "sourceTransactionIds": [subject],
                        "judgmentIds": [judgment_id],
                        "status": "active",
                        "supersededByResultIds": [],
                    },
                },
            ],
            "contribution": {
                "claimKeys": sorted(str(claim["claimKey"]) for claim in claims),
                "directProgramIds": [program_id],
                "intermediateResultIds": [result_id],
            },
            "placementAudit": {
                "rationale": "The accepted result opens one durable accounting route."
            },
            "topologyRationale": "Create one independently actionable work package.",
        }
    )


class BSSCResearchV8ProducerTests(unittest.TestCase):
    def test_initial_frontier_starts_from_zero_and_materializes_one_subject(self) -> None:
        with tempfile.TemporaryDirectory() as directory_value:
            directory = Path(directory_value)
            plan = plan_bssc_research_v8_frontier(
                ROOT,
                projection_root=directory / "published",
                scheduler_file=directory / "scheduler.json",
                materialization_root=directory / "inputs",
                replay_source=SOURCE,
                projection=PROJECTION,
            )
            self.assertEqual(plan["projection"]["id"], "openrouter-research-v8")
            self.assertEqual(plan["status"], "ready")
            self.assertEqual(plan["completedAcceptedCount"], 0)
            self.assertEqual(plan["remainingAcceptedCount"], 16)
            self.assertEqual(
                plan["nextTransition"]["subjectTransactionId"], FIRST_SUBJECT
            )
            self.assertIsNone(plan["nextTransition"]["baseRunDigest"])
            self.assertEqual(len(plan["judgmentBundles"]), 1)
            _, digest = verify_bundle(directory / "inputs/accepted-01")
            self.assertEqual(digest, FIRST_JUDGMENT_RUN)

    def test_v10_bundle_advances_and_replays_one_exact_frontier(self) -> None:
        with tempfile.TemporaryDirectory() as directory_value:
            directory = Path(directory_value)
            projection_root = directory / "published"
            scheduler = projection_root / "coordination/scheduler.json"
            materialized = directory / "inputs"
            initial = plan_bssc_research_v8_frontier(
                ROOT,
                projection_root=projection_root,
                scheduler_file=scheduler,
                materialization_root=materialized,
                replay_source=SOURCE,
                projection=PROJECTION,
            )
            builder_path = (
                ROOT / "protocol/judges/openrouter-hierarchical-research-builder-v10.json"
            )
            builder_digest = f"sha256:{sha256_json(load_judge_spec(builder_path))}"
            projection_digest = f"sha256:{sha256_json(PROJECTION)}"
            first_judgment = initial["judgmentBundles"][0]
            lane = record_completed_inputs(
                scheduler,
                "bssc-sum-capacity",
                builder_digest,
                [str(first_judgment["judgmentId"])],
                [],
                0,
                1,
                projection_spec_digest=projection_digest,
                problem_ledger_digest=str(
                    initial["nextTransition"]["problemLedgerDigest"]
                ),
            )
            claim = claim_due_build(scheduler, str(lane["laneId"]), 1, 1)
            self.assertIsNotNone(claim)
            assert claim is not None
            output = directory / "knowledge-build"
            run_research_build_bundle(
                ROOT,
                "bssc-sum-capacity",
                builder_path,
                FIRST_SUBJECT,
                claim,
                [materialized / str(first_judgment["relativePath"])],
                None,
                output,
                transport=_v10_transport,
            )
            manifest, run_digest = verify_bundle(output)
            self.assertEqual(
                manifest["outputProfile"], "math-flow/hierarchical-research-v10"
            )
            loaded = load_published_research_v10_transition(
                output,
                expected_bundle_digest=run_digest,
                expected_problem="bssc-sum-capacity",
                expected_projection_spec_digest=projection_digest,
                expected_builder_spec_digest=builder_digest,
            )
            self.assertEqual(
                loaded.submission["subjectTransactionId"], FIRST_SUBJECT
            )
            self.assertIn(
                "program/code-induced-structure",
                loaded.target_knowledge_state["programs"],
            )
            complete_build(
                scheduler,
                str(lane["laneId"]),
                str(claim["buildToken"]),
                run_digest,
                2,
            )
            publish_batch(projection_root, [output])
            following = plan_bssc_research_v8_frontier(
                ROOT,
                projection_root=projection_root,
                scheduler_file=scheduler,
                materialization_root=directory / "following-inputs",
                replay_source=SOURCE,
                projection=PROJECTION,
            )
            self.assertEqual(following["completedAcceptedCount"], 1)
            self.assertEqual(following["remainingAcceptedCount"], 15)
            self.assertEqual(following["nextTransition"]["baseRunDigest"], run_digest)

    def test_cli_and_workflow_use_the_serial_v10_route(self) -> None:
        with tempfile.TemporaryDirectory() as directory_value:
            directory = Path(directory_value)
            output = directory / "frontier.json"
            self.assertEqual(
                main(
                    [
                        "--root",
                        str(ROOT),
                        "bssc-research-v8-frontier",
                        "--source",
                        str(SOURCE_PATH),
                        "--projection",
                        str(PROJECTION_PATH),
                        "--projection-dir",
                        str(directory / "published"),
                        "--scheduler-file",
                        str(directory / "scheduler.json"),
                        "--materialization-dir",
                        str(directory / "inputs"),
                        "--output",
                        str(output),
                    ]
                ),
                0,
            )
            self.assertEqual(
                json.loads(output.read_text(encoding="utf-8"))[
                    "completedAcceptedCount"
                ],
                0,
            )

        workflow = (
            ROOT / ".github/workflows/project-research-v8-serial.yml"
        ).read_text(encoding="utf-8")
        generic = (ROOT / ".github/workflows/project-openrouter.yml").read_text(
            encoding="utf-8"
        )
        self.assertIn("bssc-research-v8-frontier", workflow)
        self.assertIn("--maximum-judgments 1", workflow)
        self.assertIn('--head "$subject"', workflow)
        self.assertIn("inputs.continue == true", workflow)
        self.assertIn("builder-v10-diagnostics", workflow)
        self.assertNotIn("work-accounting", workflow)
        self.assertNotIn("export-viewer-catalog", workflow)
        self.assertNotIn("project-openrouter.yml", workflow)
        self.assertIn(
            "openrouter-research-v8 must run through project-research-v8-serial.yml",
            generic,
        )

    def test_knowledge_build_cli_routes_builder_v10_to_research_formation(self) -> None:
        with tempfile.TemporaryDirectory() as directory_value:
            directory = Path(directory_value)
            claim = directory / "claim.json"
            claim.write_text("{}\n", encoding="utf-8")
            with (
                patch(
                    "math_flow.cli.run_research_build_bundle",
                    return_value={"routed": "builder-v10"},
                ) as research_build,
                patch(
                    "math_flow.cli.run_knowledge_build_bundle",
                    side_effect=AssertionError("builder-v10 entered the legacy route"),
                ) as legacy_build,
            ):
                self.assertEqual(
                    main(
                        [
                            "--root",
                            str(ROOT),
                            "knowledge-build",
                            "--problem",
                            "bssc-sum-capacity",
                            "--builder",
                            str(
                                ROOT
                                / "protocol/judges/openrouter-hierarchical-research-builder-v10.json"
                            ),
                            "--claim",
                            str(claim),
                            "--output-dir",
                            str(directory / "knowledge-build"),
                        ]
                    ),
                    0,
                )
            research_build.assert_called_once()
            legacy_build.assert_not_called()

    def test_runtime_candidate_requires_a_byte_identical_separate_admission(self) -> None:
        self.assertEqual(PROJECTION["status"], "active")
        self.assertEqual(
            PROJECTION["knowledgeBuilder"],
            "protocol/judges/openrouter-hierarchical-research-builder-v10.json",
        )
        admitted = ROOT / "protocol/projections/openrouter-research-v8.json"
        if admitted.exists():
            self.assertEqual(PROJECTION_PATH.read_bytes(), admitted.read_bytes())

        builder = json.loads(
            (
                ROOT
                / "protocol/judges/openrouter-hierarchical-research-builder-v10.json"
            ).read_text(encoding="utf-8")
        )
        self.assertIn("Create the smallest accounting tree", builder["systemPrompt"])
        self.assertIn("same-world no-access work package", builder["systemPrompt"])
        self.assertIn("minimize program cardinality", builder["stagePrompts"]["route-refine"])
        self.assertIn("route grants a maximum scope", builder["stagePrompts"]["organize"])


if __name__ == "__main__":
    unittest.main()
