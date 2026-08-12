from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from math_flow.cli import main
from math_flow.errors import MathFlowError
from math_flow.scale_probe import run_provider_free_scale_probe


class ProviderFreeScaleProbeTests(unittest.TestCase):
    def test_exercises_congestion_without_provider_calls(self) -> None:
        result = run_provider_free_scale_probe(
            problems=2,
            projections=2,
            solvers=4,
            minimum_interval_seconds=30,
            maximum_judgments_per_build=3,
        )

        self.assertEqual(result["status"], "passed")
        self.assertEqual(result["providerCalls"], 0)
        self.assertEqual(result["judgmentAndFormation"]["knowledgeLanes"], 4)
        self.assertEqual(
            result["judgmentAndFormation"]["duplicateSameLaneClaimsRejected"],
            4,
        )
        self.assertGreaterEqual(
            result["judgmentAndFormation"]["dependencyAtomicClaims"], 4
        )
        self.assertEqual(result["publication"]["disjointLaneUpdatesMerged"], 4)
        self.assertGreater(result["publication"]["immutableCommits"], 0)
        self.assertEqual(result["discovery"]["catalogEntries"], 4)
        self.assertEqual(result["discovery"]["materializedContexts"], 4)
        self.assertTrue(all(result["verifiedInvariants"].values()))

    def test_cli_writes_a_machine_readable_report(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / "scale-report.json"
            status = main(
                [
                    "provider-free-scale-probe",
                    "--problems",
                    "1",
                    "--projections-per-problem",
                    "1",
                    "--solvers",
                    "2",
                    "--minimum-interval",
                    "1",
                    "--maximum-judgments",
                    "3",
                    "--output",
                    str(output),
                ]
            )
            self.assertEqual(status, 0)
            self.assertIn('"providerCalls": 0', output.read_text(encoding="utf-8"))

    def test_rejects_a_limit_that_would_split_one_conflict_component(self) -> None:
        with self.assertRaisesRegex(MathFlowError, "at least three"):
            run_provider_free_scale_probe(
                problems=1,
                projections=1,
                solvers=2,
                minimum_interval_seconds=1,
                maximum_judgments_per_build=2,
            )

    def test_hosted_workflows_group_by_verified_judgment_stream(self) -> None:
        root = Path(__file__).resolve().parents[1]
        projection = (root / ".github/workflows/project-openrouter.yml").read_text(
            encoding="utf-8"
        )
        auto_merge = (
            root / ".github/workflows/auto-merge-contribution.yml"
        ).read_text(encoding="utf-8")
        wakeup = (root / ".github/workflows/projection-wakeup.yml").read_text(
            encoding="utf-8"
        )

        self.assertIn("inputs.judgment_stream_id || inputs.problem", projection)
        self.assertIn(
            'judgment_stream_id does not match the governed primary judge.',
            projection,
        )
        self.assertIn('--repo "$GITHUB_REPOSITORY"', projection)
        for caller in (auto_merge, wakeup):
            self.assertIn("group_by(.judgmentStreamId)", caller)
            self.assertIn('-f judgment_stream_id="$judgment_stream_id"', caller)
            self.assertIn("failed_stream_dispatches", caller)


if __name__ == "__main__":
    unittest.main()
