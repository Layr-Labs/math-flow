from __future__ import annotations

import copy
import json
import tempfile
import unittest
from pathlib import Path

from math_flow.artifacts import verify_bundle
from math_flow.bssc_research_v4_producer import plan_bssc_research_v4_frontier
from math_flow.cli import main
from math_flow.coordination import (
    claim_due_build,
    complete_build,
    publish_batch,
    record_completed_inputs,
)
from math_flow.errors import MathFlowError
from math_flow.judges import load_judge_spec
from math_flow.repository import sha256_json
from math_flow.research_projection import run_research_build_bundle


ROOT = Path(__file__).resolve().parents[1]
SOURCE_PATH = ROOT / "protocol/runtime/bssc-research-v4-validity-source-v1.json"
SOURCE = json.loads(SOURCE_PATH.read_text(encoding="utf-8"))
INACTIVE_PROJECTION = json.loads(
    (
        ROOT
        / "protocol/runtime/inactive-openrouter-research-v4-projection.json"
    ).read_text(encoding="utf-8")
)
FIRST_SUBJECT = "c70e1829a7c6a2a8cb8cfc2383f8abf825ac5ea6"
SECOND_SUBJECT = "f236017c62c67ce4218c1f81ea34134f0954b556"
FIRST_JUDGMENT_RUN = (
    "sha256:fd6e2748ffa7a88e1b992001d4a36cfed0194c2ee608acf68907286e7facd0fe"
)


def active_projection() -> dict[str, object]:
    projection = copy.deepcopy(INACTIVE_PROJECTION)
    projection["status"] = "active"
    projection["description"] = "Fixture serial BSSC research-v4 producer."
    projection["scheduling"]["knowledgeMinimumIntervalSeconds"] = 0
    projection["scheduling"]["maximumJudgmentsPerBuild"] = 1
    return projection


def response(content: str) -> dict[str, object]:
    return {
        "id": "fixture-response",
        "model": "openai/gpt-5.6-sol",
        "usage": {"prompt_tokens": 1, "completion_tokens": 1},
        "choices": [
            {"finish_reason": "stop", "message": {"content": content}}
        ],
    }


def v6_transport(request: dict[str, object]) -> dict[str, object]:
    content = str(request["messages"][-1]["content"])
    payload = json.loads(
        content.split("<math-flow-input>\n", 1)[1].split(
            "\n</math-flow-input>", 1
        )[0]
    )
    subject = str(payload["subjectTransactionId"])
    claims = payload["acceptedClaims"]
    suffix = subject[:8]
    thread_id = f"root/serial-{suffix}"
    item_id = f"root/result-{suffix}"
    return response(
        json.dumps(
            {
                "schemaVersion": 1,
                "subjectTransactionId": subject,
                "baseStateDigest": payload["baseState"]["stateDigest"],
                "contentOperations": [
                    {
                        "entityKind": "thread",
                        "entityId": thread_id,
                        "baseDigest": None,
                        "value": {
                            "id": thread_id,
                            "programId": "root",
                            "title": "Serial fixture line",
                            "summary": "Track one accepted fixture result.",
                            "kind": "research",
                            "status": "active",
                            "expectedExposure": "1",
                            "conditions": [],
                            "sourceTransactionIds": [subject],
                        },
                    },
                    {
                        "entityKind": "item",
                        "entityId": item_id,
                        "baseDigest": None,
                        "value": {
                            "id": item_id,
                            "programId": "root",
                            "type": "result",
                            "title": "Serial fixture result",
                            "summary": "Represent one exact accepted claim set.",
                            "claimRefs": [
                                {
                                    "transactionId": subject,
                                    "claimKey": item["claimKey"],
                                }
                                for item in claims
                            ],
                            "sourceTransactionIds": [subject],
                            "dependencyItemIds": [],
                        },
                    },
                ],
                "topologyOperations": [],
                "contribution": {
                    "claimKeys": sorted(str(item["claimKey"]) for item in claims),
                    "directProgramId": "root",
                    "directThreadIds": [thread_id],
                    "itemIds": [item_id],
                },
                "placementAudit": {
                    "basis": "canonical-objective",
                    "rationale": "The fixture result is problem-global.",
                    "relatedProgramIds": [],
                },
                "topologyRationale": None,
            }
        )
    )


class BSSCResearchV4ProducerTests(unittest.TestCase):
    def test_initial_frontier_materializes_exact_first_validity_bundle(self) -> None:
        with tempfile.TemporaryDirectory() as directory_value:
            directory = Path(directory_value)
            projection = active_projection()
            first = plan_bssc_research_v4_frontier(
                ROOT,
                projection_root=directory / "published",
                scheduler_file=directory / "published/coordination/scheduler.json",
                materialization_root=directory / "inputs-a",
                replay_source=SOURCE,
                projection=projection,
            )
            second = plan_bssc_research_v4_frontier(
                ROOT,
                projection_root=directory / "published",
                scheduler_file=directory / "published/coordination/scheduler.json",
                materialization_root=directory / "inputs-b",
                replay_source=SOURCE,
                projection=projection,
            )
            self.assertEqual(first, second)
            self.assertEqual(first["status"], "ready")
            self.assertEqual(first["completedAcceptedCount"], 0)
            self.assertEqual(first["remainingAcceptedCount"], 16)
            self.assertEqual(
                first["acceptedLedgerOrdinals"],
                [3, 4, 5, 9, 10, 11, 12, 14, 15, 16, 17, 18, 19, 21, 24, 25],
            )
            self.assertEqual(len(first["acceptedTransitionOrder"]), 16)
            self.assertEqual(
                first["nextTransition"]["subjectTransactionId"], FIRST_SUBJECT
            )
            self.assertEqual(first["nextTransition"]["ledgerOrdinal"], 3)
            self.assertIsNone(first["nextTransition"]["baseRunDigest"])
            self.assertEqual(len(first["judgmentBundles"]), 1)
            _, digest = verify_bundle(directory / "inputs-a/accepted-01")
            self.assertEqual(digest, FIRST_JUDGMENT_RUN)

    def test_completed_bundle_advances_exactly_one_frontier(self) -> None:
        with tempfile.TemporaryDirectory() as directory_value:
            directory = Path(directory_value)
            projection_root = directory / "published"
            scheduler = projection_root / "coordination/scheduler.json"
            materialized = directory / "inputs"
            projection = active_projection()
            initial = plan_bssc_research_v4_frontier(
                ROOT,
                projection_root=projection_root,
                scheduler_file=scheduler,
                materialization_root=materialized,
                replay_source=SOURCE,
                projection=projection,
            )
            builder_path = (
                ROOT
                / "protocol/judges/openrouter-hierarchical-research-builder-v6.json"
            )
            builder_digest = f"sha256:{sha256_json(load_judge_spec(builder_path))}"
            projection_digest = f"sha256:{sha256_json(projection)}"
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
                transport=v6_transport,
            )
            _, run_digest = verify_bundle(output)
            complete_build(
                scheduler,
                str(lane["laneId"]),
                str(claim["buildToken"]),
                run_digest,
                2,
            )
            publish_batch(projection_root, [output])

            following = plan_bssc_research_v4_frontier(
                ROOT,
                projection_root=projection_root,
                scheduler_file=scheduler,
                materialization_root=directory / "following-inputs",
                replay_source=SOURCE,
                projection=projection,
            )
            self.assertEqual(following["completedAcceptedCount"], 1)
            self.assertEqual(following["remainingAcceptedCount"], 15)
            self.assertEqual(
                following["nextTransition"]["subjectTransactionId"], SECOND_SUBJECT
            )
            self.assertEqual(following["nextTransition"]["baseRunDigest"], run_digest)
            self.assertEqual(len(following["judgmentBundles"]), 2)

    def test_rejects_nonserial_projection_and_stale_scheduler_base(self) -> None:
        with tempfile.TemporaryDirectory() as directory_value:
            directory = Path(directory_value)
            projection = active_projection()
            nonserial = copy.deepcopy(projection)
            nonserial["scheduling"]["maximumJudgmentsPerBuild"] = 500
            with self.assertRaisesRegex(MathFlowError, "serial BSSC producer"):
                plan_bssc_research_v4_frontier(
                    ROOT,
                    projection_root=directory / "published",
                    scheduler_file=directory / "scheduler.json",
                    materialization_root=directory / "inputs",
                    replay_source=SOURCE,
                    projection=nonserial,
                )

            first = plan_bssc_research_v4_frontier(
                ROOT,
                projection_root=directory / "published",
                scheduler_file=directory / "scheduler.json",
                materialization_root=directory / "inputs",
                replay_source=SOURCE,
                projection=projection,
            )
            lane = {
                "laneId": first["laneId"],
                "problemId": "bssc-sum-capacity",
                "builderSpecDigest": first["projection"]["builderSpecDigest"],
                "projectionSpecDigest": first["projection"]["projectionSpecDigest"],
                "minimumIntervalSeconds": 0,
                "latestStateRun": "sha256:" + "f" * 64,
                "lastCompletedAt": 1,
                "nextEligibleAt": None,
                "observedJudgmentIds": [],
                "observedConflictIds": [],
                "pendingJudgmentIds": [],
                "pendingConflictIds": [],
                "activeBuild": None,
            }
            scheduler = directory / "stale-scheduler.json"
            scheduler.write_text(
                json.dumps(
                    {"schemaVersion": 1, "lanes": {str(first["laneId"]): lane}}
                )
                + "\n",
                encoding="utf-8",
            )
            with self.assertRaises(MathFlowError):
                plan_bssc_research_v4_frontier(
                    ROOT,
                    projection_root=directory / "published",
                    scheduler_file=scheduler,
                    materialization_root=directory / "stale-inputs",
                    replay_source=SOURCE,
                    projection=projection,
                )

    def test_materialization_is_idempotent_and_rejects_tampering(self) -> None:
        with tempfile.TemporaryDirectory() as directory_value:
            directory = Path(directory_value)
            arguments = {
                "projection_root": directory / "published",
                "scheduler_file": directory / "scheduler.json",
                "materialization_root": directory / "inputs",
                "replay_source": SOURCE,
                "projection": active_projection(),
            }
            plan_bssc_research_v4_frontier(ROOT, **arguments)
            plan_bssc_research_v4_frontier(ROOT, **arguments)
            report = directory / "inputs/accepted-01/report.md"
            report.write_text("tampered\n", encoding="utf-8")
            with self.assertRaisesRegex(MathFlowError, "differs from its immutable source"):
                plan_bssc_research_v4_frontier(ROOT, **arguments)

    def test_cli_materializes_the_same_provider_free_frontier(self) -> None:
        with tempfile.TemporaryDirectory() as directory_value:
            directory = Path(directory_value)
            projection_path = directory / "projection.json"
            projection_path.write_text(
                json.dumps(active_projection()) + "\n", encoding="utf-8"
            )
            output = directory / "frontier.json"
            self.assertEqual(
                main(
                    [
                        "--root",
                        str(ROOT),
                        "bssc-research-v4-frontier",
                        "--source",
                        str(SOURCE_PATH),
                        "--projection",
                        str(projection_path),
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
            plan = json.loads(output.read_text(encoding="utf-8"))
            self.assertEqual(plan["nextTransition"]["subjectTransactionId"], FIRST_SUBJECT)

    def test_inactive_workflow_template_is_serial_and_has_no_accounting_lane(self) -> None:
        workflow = (
            ROOT
            / ".github/workflows/project-research-v4-serial.yml.inactive"
        ).read_text(encoding="utf-8")
        self.assertIn("--maximum-judgments 1", workflow)
        self.assertIn('--head "$subject"', workflow)
        self.assertIn("bssc-research-v4-frontier", workflow)
        self.assertIn("research-builder-submission-input", (
            ROOT / "math_flow/research_projection.py"
        ).read_text(encoding="utf-8"))
        self.assertNotIn("work-accounting", workflow)
        self.assertNotIn("export-viewer-catalog", workflow)
        self.assertNotIn("project-openrouter.yml", workflow)
        self.assertFalse(
            (ROOT / ".github/workflows/project-research-v4-serial.yml").exists()
        )


if __name__ == "__main__":
    unittest.main()
