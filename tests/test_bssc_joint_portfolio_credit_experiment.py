from __future__ import annotations

import argparse
import json
import tempfile
import unittest
from pathlib import Path

from experiments.bssc_joint_portfolio_credit import run
from math_flow.artifacts import sha256_bytes
from math_flow.repository import sha256_json


ROOT = Path(__file__).resolve().parents[1]
EXPERIMENT = ROOT / "protocol/experiments/bssc-joint-portfolio-credit-k2-v1"


class BsscJointPortfolioCreditExperimentTests(unittest.TestCase):
    def test_manifest_binds_the_exact_successful_wplus_and_work_judge(self) -> None:
        manifest = json.loads((EXPERIMENT / "manifest.json").read_text(encoding="utf-8"))
        for path_field, digest_field in (
            ("sourceExperimentManifest", "sourceExperimentManifestFileDigest"),
            ("frozenJointResponse", "frozenJointResponseFileDigest"),
            ("workJudgeSpec", "workJudgeSpecFileDigest"),
        ):
            path = ROOT / manifest[path_field]
            self.assertEqual(sha256_bytes(path.read_bytes()), manifest[digest_field])
        response = json.loads((ROOT / manifest["frozenJointResponse"]).read_text())
        self.assertEqual(
            "sha256:" + sha256_json(response), manifest["frozenJointResponseDigest"]
        )
        self.assertTrue(manifest["publicationForbidden"])
        self.assertIn("continue=false", manifest["holdoutPolicy"])
        self.assertEqual(manifest["acceptedTransitionOrdinal"], 2)

    def test_dry_run_reproduces_the_frozen_joint_prerequisite_without_provider(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / "candidate"
            code = run(
                argparse.Namespace(
                    root=ROOT,
                    output=output,
                    manifest=EXPERIMENT / "manifest.json",
                    dry_run=True,
                )
            )
            self.assertEqual(code, 0)
            completion = json.loads(
                (output / "complete.json").read_text(encoding="utf-8")
            )
            self.assertEqual(completion["status"], "dry-run")
            self.assertEqual(completion["providerCalls"], 0)
            self.assertTrue(completion["jointPrerequisiteVerified"])
            self.assertEqual(
                completion["frozenWithAccessStateDigest"],
                "sha256:cb2eba47967e819afba6b7918566378017ef21e2f37623841a2324a6a4e1cab7",
            )
            score = json.loads(
                (output / "joint/relational-score.json").read_text(encoding="utf-8")
            )
            self.assertEqual(score["status"], "passed")


if __name__ == "__main__":
    unittest.main()
