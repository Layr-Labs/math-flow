from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from experiments.miniature_e2e_protocol import (
    RELATIVE_DIR,
    write_miniature_e2e_fixture,
)
from math_flow.artifacts import verify_bundle
from math_flow.miniature_e2e_scenario import (
    SUBJECTS,
    build_miniature_e2e_transcript,
    miniature_e2e_oracle,
    score_miniature_e2e_scenario,
)
from math_flow.teacher_student_scenarios import run_teacher_student_scenario


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = RELATIVE_DIR / "scenario-v1.json"


class MiniatureEndToEndScenarioTests(unittest.TestCase):
    def test_reference_history_passes_full_deterministic_score(self) -> None:
        transcript = build_miniature_e2e_transcript()
        score = score_miniature_e2e_scenario(
            transcript,
            miniature_e2e_oracle(),
        )
        self.assertEqual(score["status"], "passed")
        self.assertEqual(score["hardFailures"], [])
        self.assertEqual(score["passed"], 102)
        self.assertEqual(score["adversarialAudit"]["status"], "passed")
        self.assertEqual(
            [item["id"] for item in score["adversarialAudit"]["checks"]],
            [
                "duplicate-credit",
                "dependency-double-count",
                "nonpositive-d",
                "live-w-plus-chaining",
                "solving-zero-out",
                "cross-program-contribution",
                "topology-revelation",
                "prior-credit-correction-separation",
            ],
        )
        self.assertEqual(len(transcript["steps"]), 8)
        self.assertEqual(
            [step["evaluation"]["workValueHours"] for step in transcript["steps"]],
            ["20", "5", "10", "15", "2", "2", "12", "59"],
        )
        self.assertEqual(
            transcript["steps"][-1]["withAccessState"]["totalWorkHours"],
            "0",
        )
        self.assertEqual(
            [
                correction["correctedSubjectTransactionId"]
                for step in transcript["steps"]
                for correction in step["priorCreditCorrections"]
            ],
            [SUBJECTS[2]],
        )

    def test_scorer_detects_node_reduction_and_live_chain_tampering(self) -> None:
        transcript = build_miniature_e2e_transcript()
        transcript["steps"][6]["nodeReductions"][0]["deltaWorkHours"] = "999"
        transcript["steps"][4]["baseLiveAccountingStateDigest"] = "sha256:" + "0" * 64
        score = score_miniature_e2e_scenario(
            transcript,
            miniature_e2e_oracle(),
        )
        self.assertEqual(score["status"], "failed")
        self.assertIn("live-base-5", score["hardFailures"])
        self.assertIn("node-reduction-replay-7", score["hardFailures"])
        self.assertIn("transcript-digest", score["hardFailures"])

    def test_checked_in_fixture_is_exactly_regenerable(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            generated_root = Path(directory)
            result = write_miniature_e2e_fixture(generated_root)
            self.assertEqual(result["score"]["status"], "passed")
            generated_dir = generated_root / RELATIVE_DIR
            checked_dir = ROOT / RELATIVE_DIR
            generated_files = sorted(
                path.relative_to(generated_dir) for path in generated_dir.rglob("*") if path.is_file()
            )
            checked_files = sorted(
                path.relative_to(checked_dir) for path in checked_dir.rglob("*") if path.is_file()
            )
            self.assertEqual(generated_files, checked_files)
            for relative in generated_files:
                self.assertEqual(
                    (generated_dir / relative).read_bytes(),
                    (checked_dir / relative).read_bytes(),
                    relative.as_posix(),
                )

    def test_common_scenario_runner_replays_without_provider_or_publication(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "bundle"
            manifest = run_teacher_student_scenario(ROOT, MANIFEST, output)
            verified, _ = verify_bundle(output)
            self.assertEqual(manifest, verified)
            self.assertEqual(manifest["summary"]["status"], "passed")
            self.assertEqual(manifest["summary"]["hardFailures"], 0)
            self.assertEqual(manifest["execution"]["providerCallsExecuted"], 0)
            self.assertTrue(manifest["execution"]["publicationForbidden"])
            telemetry = json.loads((output / "telemetry.json").read_text())
            self.assertEqual(telemetry["providerCallsExecuted"], 0)
            self.assertEqual(telemetry["providerCallsRecorded"], 0)
            frozen_ids = {
                item["id"]
                for item in json.loads((output / "scenario/manifest.json").read_text())[
                    "frozenInputs"
                ]
            }
            self.assertEqual(
                frozen_ids,
                {
                    "miniature-oracle",
                    "knowledge-builder-spec",
                    "work-accounting-spec",
                    "work-accounting-policy",
                },
            )


if __name__ == "__main__":
    unittest.main()
