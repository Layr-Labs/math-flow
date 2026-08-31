from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from math_flow.artifacts import verify_bundle
from math_flow.bssc_research_v7_producer import plan_bssc_research_v7_frontier
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


ROOT = Path(__file__).resolve().parents[1]
SOURCE_PATH = ROOT / "protocol/runtime/bssc-research-v4-validity-source-v1.json"
SOURCE = json.loads(SOURCE_PATH.read_text(encoding="utf-8"))
PROJECTION_PATH = ROOT / "protocol/runtime/openrouter-research-v7-projection.json"
PROJECTION = json.loads(PROJECTION_PATH.read_text(encoding="utf-8"))
FIRST_SUBJECT = "c70e1829a7c6a2a8cb8cfc2383f8abf825ac5ea6"
SECOND_SUBJECT = "f236017c62c67ce4218c1f81ea34134f0954b556"
FIRST_JUDGMENT_RUN = (
    "sha256:fd6e2748ffa7a88e1b992001d4a36cfed0194c2ee608acf68907286e7facd0fe"
)


def response(content: str) -> dict[str, object]:
    return {
        "id": "fixture-response-v9",
        "model": "openai/gpt-5.6-sol",
        "usage": {"prompt_tokens": 1, "completion_tokens": 1},
        "choices": [{"finish_reason": "stop", "message": {"content": content}}],
    }


def v9_transport(request: dict[str, object]) -> dict[str, object]:
    content = str(request["messages"][-1]["content"])
    payload = json.loads(
        content.split("<math-flow-input>\n", 1)[1].split(
            "\n</math-flow-input>", 1
        )[0]
    )
    subject = str(payload["subjectTransactionId"])
    claims = payload["acceptedClaimAssessments"]
    judgment_id = str(payload["judgmentId"])
    base = payload["baseStateContext"]
    root = dict(base["programs"]["root"])
    result_id = f"result/serial-{subject[:8]}"
    root.update(
        {
            "currentStateSummary": "The accepted serial fixture result is established.",
            "localResidualSummary": "The remaining canonical problem is open.",
            "intermediateResultIds": [result_id],
            "sourceTransactionIds": [subject],
        }
    )
    result = {
        "id": result_id,
        "primaryProgramId": "root",
        "relatedProgramIds": [],
        "title": "Serial fixture result",
        "statement": "The exact accepted claims are packaged as one reusable result.",
        "scopeQualifications": [],
        "supportAdditions": {
            "proofs": ["The accepted submission supplies the supporting argument."],
            "methods": [],
            "computations": [],
            "tools": [],
            "artifactPaths": [payload["submissionEvidence"]["files"][0]["path"]],
            "attestationRefs": [],
        },
        "dependencyResultIds": [],
        "claimRefs": [
            {"transactionId": subject, "claimKey": item["claimKey"]}
            for item in claims
        ],
        "sourceTransactionIds": [subject],
        "judgmentIds": [judgment_id],
        "status": "active",
        "supersededByResultIds": [],
    }
    return response(
        json.dumps(
            {
                "schemaVersion": 1,
                "subjectTransactionId": subject,
                "baseStateDigest": base["baseStateDigest"],
                "contentOperations": [
                    {
                        "entityKind": "program",
                        "entityId": "root",
                        "baseDigest": None,
                        "value": root,
                    },
                    {
                        "entityKind": "intermediateResult",
                        "entityId": result_id,
                        "baseDigest": None,
                        "value": result,
                    },
                ],
                "topologyOperations": [],
                "contribution": {
                    "claimKeys": sorted(str(item["claimKey"]) for item in claims),
                    "directProgramIds": ["root"],
                    "intermediateResultIds": [result_id],
                },
                "placementAudit": {
                    "basis": "canonical-objective",
                    "rationale": "The fixture result directly concerns the canonical objective.",
                    "relatedProgramIds": [],
                },
                "topologyRationale": None,
            }
        )
    )


class BSSCResearchV7ProducerTests(unittest.TestCase):
    def test_initial_frontier_starts_from_zero_and_materializes_one_subject(self) -> None:
        with tempfile.TemporaryDirectory() as directory_value:
            directory = Path(directory_value)
            plan = plan_bssc_research_v7_frontier(
                ROOT,
                projection_root=directory / "published",
                scheduler_file=directory / "scheduler.json",
                materialization_root=directory / "inputs",
                replay_source=SOURCE,
                projection=PROJECTION,
            )
            self.assertEqual(plan["projection"]["id"], "openrouter-research-v7")
            self.assertEqual(plan["status"], "ready")
            self.assertEqual(plan["completedAcceptedCount"], 0)
            self.assertEqual(plan["remainingAcceptedCount"], 16)
            self.assertEqual(plan["nextTransition"]["subjectTransactionId"], FIRST_SUBJECT)
            self.assertIsNone(plan["nextTransition"]["baseRunDigest"])
            self.assertEqual(len(plan["judgmentBundles"]), 1)
            _, digest = verify_bundle(directory / "inputs/accepted-01")
            self.assertEqual(digest, FIRST_JUDGMENT_RUN)

    def test_state_v3_bundle_advances_exactly_one_frontier(self) -> None:
        with tempfile.TemporaryDirectory() as directory_value:
            directory = Path(directory_value)
            projection_root = directory / "published"
            scheduler = projection_root / "coordination/scheduler.json"
            materialized = directory / "inputs"
            initial = plan_bssc_research_v7_frontier(
                ROOT,
                projection_root=projection_root,
                scheduler_file=scheduler,
                materialization_root=materialized,
                replay_source=SOURCE,
                projection=PROJECTION,
            )
            builder_path = (
                ROOT / "protocol/judges/openrouter-hierarchical-research-builder-v9.json"
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
                problem_ledger_digest=str(initial["nextTransition"]["problemLedgerDigest"]),
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
                transport=v9_transport,
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

            following = plan_bssc_research_v7_frontier(
                ROOT,
                projection_root=projection_root,
                scheduler_file=scheduler,
                materialization_root=directory / "following-inputs",
                replay_source=SOURCE,
                projection=PROJECTION,
            )
            self.assertEqual(following["completedAcceptedCount"], 1)
            self.assertEqual(following["remainingAcceptedCount"], 15)
            self.assertEqual(
                following["nextTransition"]["subjectTransactionId"], SECOND_SUBJECT
            )
            self.assertEqual(following["nextTransition"]["baseRunDigest"], run_digest)
            self.assertEqual(len(following["judgmentBundles"]), 2)

    def test_cli_and_workflow_use_the_serial_v9_route(self) -> None:
        with tempfile.TemporaryDirectory() as directory_value:
            directory = Path(directory_value)
            output = directory / "frontier.json"
            self.assertEqual(
                main(
                    [
                        "--root",
                        str(ROOT),
                        "bssc-research-v7-frontier",
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
                json.loads(output.read_text(encoding="utf-8"))["completedAcceptedCount"],
                0,
            )

        workflow = (
            ROOT / ".github/workflows/project-research-v7-serial.yml"
        ).read_text(encoding="utf-8")
        generic = (ROOT / ".github/workflows/project-openrouter.yml").read_text(
            encoding="utf-8"
        )
        self.assertIn("bssc-research-v7-frontier", workflow)
        self.assertIn("--maximum-judgments 1", workflow)
        self.assertIn('--head "$subject"', workflow)
        self.assertIn("inputs.continue == true", workflow)
        self.assertIn("builder-v9-diagnostics", workflow)
        self.assertNotIn("work-accounting", workflow)
        self.assertNotIn("export-viewer-catalog", workflow)
        self.assertNotIn("project-openrouter.yml", workflow)
        self.assertIn(
            "openrouter-research-v7 must run through project-research-v7-serial.yml",
            generic,
        )

    def test_runtime_candidate_accepts_optional_separate_admission(self) -> None:
        self.assertEqual(PROJECTION["status"], "active")
        self.assertEqual(
            PROJECTION["knowledgeBuilder"],
            "protocol/judges/openrouter-hierarchical-research-builder-v9.json",
        )
        admitted = ROOT / "protocol/projections/openrouter-research-v7.json"
        if admitted.exists():
            self.assertEqual(PROJECTION_PATH.read_bytes(), admitted.read_bytes())


if __name__ == "__main__":
    unittest.main()
