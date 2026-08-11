from __future__ import annotations

import unittest
from pathlib import Path
from unittest.mock import patch

from math_flow.artifacts import sha256_bytes
from math_flow.errors import MathFlowError
from math_flow.knowledge import empty_state_v3
from math_flow.viewer import (
    _revision_artifact,
    _validate_new_revision_report_links,
    _validate_revision_state,
    export_viewer_data,
)


class ViewerNeutralRevisionTests(unittest.TestCase):
    def test_prefers_the_profile_specific_neutral_revision_artifact(self) -> None:
        manifest = {"artifacts": [{"role": "knowledge-revisions"}]}
        payload = b'{"revisionId":"sha256:example","facets":["content"]}\n'
        with patch("math_flow.viewer.read_verified_artifact", return_value=payload) as read:
            revisions = _revision_artifact(Path("run"), manifest)
        read.assert_called_once_with(Path("run"), manifest, "knowledge-revisions")
        self.assertEqual(revisions[0]["facets"], ["content"])

    def test_rejects_ambiguous_revision_artifacts(self) -> None:
        manifest = {
            "artifacts": [
                {"role": "knowledge-revisions"},
                {"role": "adjudication-revisions"},
            ]
        }
        with self.assertRaisesRegex(MathFlowError, "one revision-history artifact"):
            _revision_artifact(Path("run"), manifest)

    def test_validates_neutral_state_with_the_v3_validator(self) -> None:
        state = empty_state_v3("demo")
        _validate_revision_state(
            "math-flow/knowledge-build-markdown-v2", state, [], "demo"
        )
        with self.assertRaisesRegex(MathFlowError, "different problem"):
            _validate_revision_state(
                "math-flow/knowledge-build-markdown-v2", state, [], "another"
            )

    def test_binds_new_revision_to_exact_unique_report_section(self) -> None:
        report = "# Formation\n\n## Node: program/a\nCurrent account.\n\n## Change: program/a\nWhy.\n"
        section = "## Node: program/a\nCurrent account.\n"
        report_digest = sha256_bytes(report.encode("utf-8"))
        revision = {
            "nodeId": "program/a",
            "reportRef": {
                "artifact": "report.md",
                "digest": report_digest,
                "section": "## Node: program/a",
            },
            "contentDigest": sha256_bytes(section.encode("utf-8")),
            "changeRef": {
                "artifact": "report.md",
                "digest": report_digest,
                "section": "## Change: program/a",
            },
            "changeRationale": "Why.",
        }
        _validate_new_revision_report_links([revision], 0, report, report_digest)

        wrong_report = {
            **revision,
            "reportRef": {
                **revision["reportRef"],
                "digest": "sha256:" + "0" * 64,
            },
        }
        with self.assertRaisesRegex(MathFlowError, "does not reference its run report"):
            _validate_new_revision_report_links([wrong_report], 0, report, report_digest)

        duplicate = report + "\n## Node: program/a\nDifferent account.\n"
        with self.assertRaisesRegex(MathFlowError, "missing or ambiguous"):
            _validate_new_revision_report_links([revision], 0, duplicate, report_digest)

        wrong_content = {**revision, "contentDigest": "sha256:" + "1" * 64}
        with self.assertRaisesRegex(MathFlowError, "content does not match"):
            _validate_new_revision_report_links([wrong_content], 0, report, report_digest)

        wrong_rationale = {**revision, "changeRationale": "A different explanation."}
        with self.assertRaisesRegex(MathFlowError, "rationale does not match"):
            _validate_new_revision_report_links(
                [wrong_rationale], 0, report, report_digest
            )

        wrong_change_report = {
            **revision,
            "changeRef": {
                **revision["changeRef"],
                "digest": "sha256:" + "2" * 64,
            },
        }
        with self.assertRaisesRegex(MathFlowError, "change report"):
            _validate_new_revision_report_links(
                [wrong_change_report], 0, report, report_digest
            )

        duplicate_change = report + "\n## Change: program/a\nAnother reason.\n"
        with self.assertRaisesRegex(MathFlowError, "change section is missing or ambiguous"):
            _validate_new_revision_report_links(
                [revision], 0, duplicate_change, report_digest
            )

    @patch(
        "math_flow.viewer._report_artifact",
        return_value=("# Report\n", "sha256:" + "a" * 64),
    )
    @patch("math_flow.viewer._revision_artifact", return_value=[])
    @patch("math_flow.viewer._validate_revision_state")
    @patch("math_flow.viewer._json_artifact")
    @patch("math_flow.viewer.read_at", return_value="# Demo\n")
    @patch(
        "math_flow.viewer.ledger",
        return_value={"ledgerHead": "head", "transactions": []},
    )
    @patch("math_flow.viewer.load_manifest")
    def test_rejects_output_profile_change_within_chain(
        self,
        load_manifest,
        _ledger,
        _read_at,
        json_artifact,
        _validate,
        _revisions,
        _report,
    ) -> None:
        load_manifest.side_effect = [
            (
                {
                    "problemId": "demo",
                    "outputProfile": "math-flow/knowledge-build-markdown-v1",
                    "baseRun": None,
                    "ledgerHead": "head",
                    "judgeSpec": {},
                    "runner": {},
                    "providerRuns": [],
                },
                "sha256:" + "1" * 64,
            ),
            (
                {
                    "problemId": "demo",
                    "outputProfile": "math-flow/knowledge-build-markdown-v2",
                    "baseRun": "sha256:" + "1" * 64,
                },
                "sha256:" + "2" * 64,
            ),
        ]
        json_artifact.side_effect = lambda _bundle, _manifest, role: (
            {"nodes": {}} if role == "knowledge-state" else {"normalizations": []}
        )
        with self.assertRaisesRegex(MathFlowError, "changes output profile"):
            export_viewer_data(
                Path("."), "demo", "HEAD", [Path("run-1"), Path("run-2")]
            )


if __name__ == "__main__":
    unittest.main()
