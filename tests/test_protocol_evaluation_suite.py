from __future__ import annotations

import copy
import json
import tempfile
import unittest
from contextlib import redirect_stderr
from io import StringIO
from pathlib import Path
from unittest import mock

from math_flow.cli import build_parser
from math_flow.errors import MathFlowError
from math_flow.protocol_evaluation_suite import (
    COMPONENT_ORDER,
    COMPONENT_RUNNERS,
    DEFAULT_MANIFEST_PATH,
    load_protocol_evaluation_suite_manifest,
    run_provider_free_protocol_evaluation_suite,
)
from math_flow.repository import sha256_json


ROOT = Path(__file__).resolve().parents[1]


class ProtocolEvaluationSuiteTests(unittest.TestCase):
    def test_pr_suite_runs_every_component_with_zero_authority(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / "out"
            summary = run_provider_free_protocol_evaluation_suite(
                ROOT, output, mode="pr"
            )
            self.assertEqual(summary["status"], "passed")
            self.assertEqual(summary["componentCount"], len(COMPONENT_ORDER))
            self.assertEqual(summary["passedComponents"], len(COMPONENT_ORDER))
            self.assertEqual(summary["failedComponents"], [])
            self.assertEqual(
                [component["id"] for component in summary["components"]],
                list(COMPONENT_ORDER),
            )
            self.assertEqual(
                summary["authority"],
                {
                    "credentialInputsAccepted": [],
                    "executionFlagsAccepted": [],
                    "providerCalls": 0,
                    "networkUsed": False,
                    "publicationAttempted": False,
                },
            )
            for component in summary["components"]:
                self.assertEqual(component["status"], "passed")
                self.assertEqual(component["providerCalls"], 0)
                self.assertFalse(component["networkUsed"])
                self.assertFalse(component["publicationAttempted"])
                component_core = {
                    key: value
                    for key, value in component.items()
                    if key != "componentDigest"
                }
                self.assertEqual(
                    component["componentDigest"],
                    "sha256:" + sha256_json(component_core),
                )
            core = {
                key: value for key, value in summary.items() if key != "summaryDigest"
            }
            self.assertEqual(
                summary["summaryDigest"], "sha256:" + sha256_json(core)
            )
            self.assertEqual(
                json.loads((output / "summary.json").read_text(encoding="utf-8")),
                summary,
            )
            markdown = (output / "summary.md").read_text(encoding="utf-8")
            self.assertIn(
                f"{len(COMPONENT_ORDER)}/{len(COMPONENT_ORDER)} passed",
                markdown,
            )
            self.assertIn("0 provider calls", markdown)

    def test_full_mode_exactly_regenerates_checked_scale_reports(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            summary = run_provider_free_protocol_evaluation_suite(
                ROOT, Path(temporary) / "out", mode="full"
            )
        self.assertEqual(summary["status"], "passed")
        by_id = {component["id"]: component for component in summary["components"]}
        self.assertEqual(
            by_id["builder-context-scale"]["verification"],
            "exact-regeneration",
        )
        self.assertEqual(
            by_id["work-accounting-context-scale"]["verification"],
            "exact-regeneration",
        )
        self.assertEqual(
            by_id["work-accounting-local-slice"]["verification"],
            "exact-regeneration",
        )
        self.assertEqual(
            by_id["work-accounting-local-slice"]["details"],
            {
                "caseCount": 24,
                "boundedRootTotalMatchCaseCount": 20,
                "explicitWideningCaseCount": 4,
                "allAttemptedRootTotalChecksMatch": True,
            },
        )
        self.assertEqual(
            by_id["no-three-v10-v2-preflight"]["verification"],
            "exact-zero-call-preflight-regeneration",
        )

    def test_checked_artifact_drift_fails_closed(self) -> None:
        manifest = json.loads((ROOT / DEFAULT_MANIFEST_PATH).read_text(encoding="utf-8"))
        with tempfile.TemporaryDirectory(dir=ROOT) as temporary:
            temporary_path = Path(temporary)
            source = ROOT / manifest["components"][0]["checkedArtifact"]["path"]
            drifted = temporary_path / "drifted-builder-report.json"
            drifted.write_bytes(source.read_bytes() + b"\n")
            manifest["components"][0]["checkedArtifact"]["path"] = (
                drifted.relative_to(ROOT).as_posix()
            )
            candidate = temporary_path / "manifest.json"
            candidate.write_text(json.dumps(manifest), encoding="utf-8")

            def passed(context: object) -> dict[str, object]:
                return {
                    "verification": "test-noop",
                    "outputDigest": "sha256:" + "a" * 64,
                    "providerCalls": 0,
                    "networkUsed": False,
                    "publicationAttempted": False,
                    "details": {},
                }

            replacements = {identifier: passed for identifier in COMPONENT_ORDER}
            with mock.patch.dict(COMPONENT_RUNNERS, replacements, clear=True):
                summary = run_provider_free_protocol_evaluation_suite(
                    ROOT,
                    temporary_path / "out",
                    mode="pr",
                    manifest_path=candidate,
                )
        self.assertEqual(summary["status"], "failed")
        self.assertEqual(summary["failedComponents"], [COMPONENT_ORDER[0]])
        failure = summary["components"][0]["failure"]
        self.assertIn("digest drift", failure["summary"])
        self.assertEqual(summary["authority"]["providerCalls"], 0)

    def test_authority_fields_and_cli_execution_flags_are_rejected(self) -> None:
        manifest = json.loads((ROOT / DEFAULT_MANIFEST_PATH).read_text(encoding="utf-8"))
        manifest["providerExecutionAuthorized"] = True
        with tempfile.TemporaryDirectory(dir=ROOT) as temporary:
            candidate = Path(temporary) / "manifest.json"
            candidate.write_text(json.dumps(manifest), encoding="utf-8")
            with self.assertRaisesRegex(MathFlowError, "authority-free"):
                load_protocol_evaluation_suite_manifest(ROOT, candidate)

        parser = build_parser()
        with redirect_stderr(StringIO()), self.assertRaises(SystemExit):
            parser.parse_args(
                [
                    "protocol-evaluation-suite",
                    "--output-dir",
                    "out",
                    "--execute-provider",
                ]
            )
        with redirect_stderr(StringIO()), self.assertRaises(SystemExit):
            parser.parse_args(
                [
                    "protocol-evaluation-suite",
                    "--output-dir",
                    "out",
                    "--provider-api-key",
                    "secret",
                ]
            )

    def test_component_authority_violation_fails_closed_as_unknown(self) -> None:
        def passed(context: object) -> dict[str, object]:
            return {
                "verification": "test-noop",
                "outputDigest": "sha256:" + "a" * 64,
                "providerCalls": 0,
                "networkUsed": False,
                "publicationAttempted": False,
                "details": {},
            }

        def violated(context: object) -> dict[str, object]:
            return {**passed(context), "providerCalls": 1}

        replacements = {identifier: passed for identifier in COMPONENT_ORDER}
        replacements[COMPONENT_ORDER[0]] = violated
        with tempfile.TemporaryDirectory() as temporary:
            with mock.patch.dict(COMPONENT_RUNNERS, replacements, clear=True):
                summary = run_provider_free_protocol_evaluation_suite(
                    ROOT, Path(temporary) / "out", mode="pr"
                )
        self.assertEqual(summary["status"], "failed")
        self.assertEqual(
            summary["failedComponents"],
            [COMPONENT_ORDER[0], "suite-authority-boundary"],
        )
        first = summary["components"][0]
        self.assertEqual(first["status"], "failed")
        self.assertIn("forbidden external effect", first["failure"]["summary"])
        self.assertIsNone(first["providerCalls"])
        self.assertIsNone(first["networkUsed"])
        self.assertIsNone(first["publicationAttempted"])
        self.assertIsNone(summary["authority"]["providerCalls"])
        self.assertIsNone(summary["authority"]["networkUsed"])
        self.assertIsNone(summary["authority"]["publicationAttempted"])

    def test_unknown_component_requires_an_additive_registry_entry(self) -> None:
        manifest = json.loads((ROOT / DEFAULT_MANIFEST_PATH).read_text(encoding="utf-8"))
        candidate_component = copy.deepcopy(manifest["components"][-1])
        candidate_component["id"] = "future-local-accounting-slice"
        manifest["components"].append(candidate_component)
        with tempfile.TemporaryDirectory(dir=ROOT) as temporary:
            candidate = Path(temporary) / "manifest.json"
            candidate.write_text(json.dumps(manifest), encoding="utf-8")
            with self.assertRaisesRegex(MathFlowError, "not allowlisted"):
                load_protocol_evaluation_suite_manifest(ROOT, candidate)


if __name__ == "__main__":
    unittest.main()
