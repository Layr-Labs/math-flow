from __future__ import annotations

import json
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from math_flow.cli import main
from math_flow.errors import MathFlowError
from math_flow.repository import sha256_json, validate_tree
from math_flow.solver_tools import credit_status, register_direction


def git(root: Path, *args: str) -> str:
    return subprocess.run(
        ["git", *args],
        cwd=root,
        check=True,
        stdout=subprocess.PIPE,
        text=True,
    ).stdout.strip()


def write(path: Path, value: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(value, encoding="utf-8")


class SolverToolTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.base = Path(self.temporary.name)
        self.root = self.base / "repository"
        self.root.mkdir()
        git(self.root, "init", "-q")
        git(self.root, "config", "user.name", "Test Author")
        git(self.root, "config", "user.email", "test@example.com")
        write(self.root / "problems/demo/problem.md", "# Demo\n\nFind progress.\n")
        self.v1 = {
            "schemaVersion": 1,
            "id": "credit-v1",
            "implementation": "openrouter-credit-assignment-v1",
            "description": "Ledger credit.",
            "inputBuilder": "locked-knowledge-ledger-v1",
            "invocationAdapter": "openrouter-chat-completions-v1",
            "outputProfile": "math-flow/credit-assignment-markdown-v1",
            "outputAdapter": "report-extract-credit-v1",
            "reducer": None,
            "rubric": {"priority": "Use canonical contribution order."},
        }
        self.v2 = {
            **self.v1,
            "id": "credit-v2",
            "implementation": "openrouter-credit-assignment-v2",
            "description": "Direction-aware credit.",
            "inputBuilder": "locked-knowledge-ledger-directions-v2",
            "outputProfile": "math-flow/credit-assignment-markdown-v2",
            "outputAdapter": "report-extract-credit-v2",
            "rubric": {"priority": "Use exact register-event references."},
        }
        self.research_v2 = {
            **self.v1,
            "id": "credit-research",
            "implementation": "openrouter-hierarchical-research-credit-v2",
            "description": "Hierarchical research credit.",
            "inputBuilder": "locked-research-history-v2",
            "outputProfile": "math-flow/hierarchical-research-credit-v2",
            "outputAdapter": "structured-hierarchical-credit-v2",
            "reducer": "hierarchical-credit-allocation-v2",
        }
        write(
            self.root / "protocol/judges/credit-v1.json",
            json.dumps(self.v1) + "\n",
        )
        write(
            self.root / "protocol/judges/credit-v2.json",
            json.dumps(self.v2) + "\n",
        )
        write(
            self.root / "protocol/judges/credit-research.json",
            json.dumps(self.research_v2) + "\n",
        )
        git(self.root, "add", ".")
        git(self.root, "commit", "-qm", "Create fixture")
        self.head = git(self.root, "rev-parse", "HEAD")
        self.plan = self.base / "plan.md"
        write(
            self.plan,
            "# Modular direction\n\n## Scope\n\nProve the bounded modular case.\n",
        )

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def _active(self, overlays: list[str]) -> dict[str, object]:
        projections = []
        for version in overlays:
            spec = {
                "v1": self.v1,
                "v2": self.v2,
                "research": self.research_v2,
            }[version]
            projections.append(
                {
                    "schemaVersion": 1,
                    "projectionId": str(spec["id"]),
                    "projectionSpecDigest": "sha256:" + version * 32,
                    "problemId": "demo",
                    "canonicalHead": self.head,
                    "engine": "overlay-repository-v1",
                    "dependencies": [
                        {
                            "name": "knowledge",
                            "projectionId": "research-v1",
                            "projectionSpecDigest": "sha256:" + "a" * 64,
                            "artifactRole": "knowledge-state",
                        }
                    ],
                    "scheduling": {"minimumIntervalSeconds": 3600},
                    "runner": {
                        "implementation": spec["implementation"],
                        "spec": f"protocol/judges/{spec['id']}.json",
                    },
                }
            )
        return {
            "schemaVersion": 1,
            "problemId": "demo",
            "canonicalHead": self.head,
            "projections": projections,
        }

    @patch("math_flow.solver_tools.list_active_projections")
    def test_credit_status_explains_direction_aware_policy(self, active_mock) -> None:
        active_mock.return_value = self._active(["v1", "v2"])
        result = credit_status(self.root, "demo", self.head)
        self.assertTrue(result["registrationAffectsActiveCreditPolicy"])
        self.assertEqual(result["registrationAwareOverlayIds"], ["credit-v2"])
        by_id = {
            item["projectionId"]: item for item in result["activeCreditOverlays"]
        }
        self.assertFalse(by_id["credit-v1"]["consumesResearchDirectionEvents"])
        self.assertTrue(by_id["credit-v2"]["consumesResearchDirectionEvents"])
        self.assertIn(
            "research-direction-events", by_id["credit-v2"]["inputCapabilities"]
        )
        self.assertEqual(
            by_id["credit-v2"]["runner"]["specDigest"],
            "sha256:" + sha256_json(self.v2),
        )

    @patch("math_flow.solver_tools.list_active_projections")
    def test_credit_status_reports_no_applicable_overlay(self, active_mock) -> None:
        active_mock.return_value = self._active([])
        result = credit_status(self.root, "demo", self.head)
        self.assertFalse(result["registrationAffectsActiveCreditPolicy"])
        self.assertEqual(result["activeCreditOverlays"], [])
        self.assertIn("No active credit overlay", result["message"])

    @patch("math_flow.solver_tools.list_active_projections")
    def test_credit_status_describes_hierarchical_research_inputs(
        self, active_mock
    ) -> None:
        active_mock.return_value = self._active(["research"])
        result = credit_status(self.root, "demo", self.head)
        overlay = result["activeCreditOverlays"][0]
        self.assertEqual(
            overlay["inputCapabilities"],
            [
                "research-program-state",
                "accepted-submission-content",
                "validity-records",
                "serialized-research-state-history",
            ],
        )
        self.assertFalse(overlay["consumesResearchDirectionEvents"])
        self.assertFalse(result["registrationAffectsActiveCreditPolicy"])

    def test_register_direction_scaffolds_only_the_atomic_event(self) -> None:
        result = register_direction(
            self.root,
            "demo",
            "modular-case",
            "initial-plan",
            "Modular case",
            "Prove a sharply bounded modular subcase.",
            self.plan,
            ["program", "program/modular-case"],
            self.head,
        )
        target = self.root / result["path"]
        self.assertEqual(
            sorted(path.name for path in target.iterdir()),
            ["README.md", "event.json"],
        )
        self.assertEqual((target / "README.md").read_text(), self.plan.read_text())
        event = json.loads((target / "event.json").read_text())
        self.assertEqual(event["eventType"], "register")
        self.assertEqual(
            event["relatedKnowledgeNodeIds"],
            ["program", "program/modular-case"],
        )
        self.assertFalse(result["creditPolicyInterpreted"])
        self.assertEqual(validate_tree(self.root)["researchDirections"], 1)
        with self.assertRaisesRegex(MathFlowError, "already exists"):
            register_direction(
                self.root,
                "demo",
                "modular-case",
                "initial-plan",
                "Modular case",
                "Prove a sharply bounded modular subcase.",
                self.plan,
                ["program", "program/modular-case"],
                self.head,
            )

    def test_register_direction_cli_and_sorted_node_guard(self) -> None:
        with self.assertRaisesRegex(MathFlowError, "unique and sorted"):
            register_direction(
                self.root,
                "demo",
                "bad-order",
                "initial-plan",
                "Bad order",
                "This should fail before writing.",
                self.plan,
                ["z", "a"],
                self.head,
            )
        self.assertEqual(
            main(
                [
                    "--root",
                    str(self.root),
                    "register-direction",
                    "--problem",
                    "demo",
                    "--direction",
                    "cli-direction",
                    "--title",
                    "CLI direction",
                    "--summary",
                    "A complete bounded CLI-generated direction.",
                    "--plan-file",
                    str(self.plan),
                    "--head",
                    self.head,
                ]
            ),
            0,
        )
        self.assertTrue(
            (
                self.root
                / "problems/demo/directions/cli-direction/events/initial-plan/event.json"
            ).is_file()
        )


if __name__ == "__main__":
    unittest.main()
