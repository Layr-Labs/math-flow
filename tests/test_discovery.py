from __future__ import annotations

import json
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from math_flow.cli import main
from math_flow.discovery import discover_problems


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


class ProblemDiscoveryTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        git(self.root, "init", "-q")
        git(self.root, "config", "user.name", "Test Author")
        git(self.root, "config", "user.email", "test@example.com")
        write(self.root / "problems/fresh/problem.md", "# Fresh problem\n\nStart here.\n")
        write(self.root / "problems/started/problem.md", "# Started problem\n\nContinue.\n")
        git(self.root, "add", ".")
        git(self.root, "commit", "-qm", "Admit problems")
        write(
            self.root / "problems/started/contributions/first/README.md",
            "# First contribution\n",
        )
        git(self.root, "add", ".")
        git(self.root, "commit", "-qm", "Start one problem")
        self.head = git(self.root, "rev-parse", "HEAD")
        self.transaction = self.head

    def tearDown(self) -> None:
        self.temporary.cleanup()

    @staticmethod
    def _active(_root: Path, problem: str, head: str) -> dict[str, object]:
        return {
            "schemaVersion": 1,
            "problemId": problem,
            "canonicalHead": head,
            "projections": [
                {
                    "projectionId": "research-v1",
                    "engine": "openrouter-repository-v1",
                    "knowledgeBuilder": "builder.json",
                },
                {
                    "projectionId": "credit-v1",
                    "engine": "overlay-repository-v1",
                    "runner": {"implementation": "credit"},
                },
            ],
        }

    def _catalog(self, projected_ids: list[str]) -> dict[str, object]:
        return {
            "schemaVersion": 1,
            "projections": [
                {
                    "id": "research-v1",
                    "problemId": "started",
                    "latestRunDigest": "sha256:" + "a" * 64,
                    "runCount": 1,
                    "data": {
                        "problem": {
                            "statementMarkdown": "# Started problem\n\nContinue.\n"
                        },
                        "transactions": [
                            {"transactionId": value} for value in projected_ids
                        ],
                    },
                }
            ],
        }

    @patch("math_flow.discovery.list_active_projections", side_effect=_active)
    def test_lists_unstarted_problem_without_projection_checkout(self, _active_mock) -> None:
        result = discover_problems(self.root, self.head)
        by_id = {item["problemId"]: item for item in result["problems"]}
        self.assertEqual(result["projectionInspection"], "not-requested")
        self.assertEqual(by_id["fresh"]["stage"], "ready-for-first-contribution")
        self.assertEqual(by_id["fresh"]["contributionCount"], 0)
        self.assertEqual(by_id["started"]["stage"], "projection-unchecked")
        self.assertEqual(
            by_id["fresh"]["activeKnowledgeProjectionIds"], ["research-v1"]
        )
        self.assertEqual(by_id["fresh"]["activeOverlayProjectionIds"], ["credit-v1"])

    @patch("math_flow.discovery.export_viewer_catalog")
    @patch("math_flow.discovery.list_active_projections", side_effect=_active)
    def test_joins_verified_projection_without_hiding_unstarted_problem(
        self, _active_mock, catalog_mock
    ) -> None:
        catalog_mock.return_value = self._catalog([self.transaction])
        projection_root = self.root / "projection"
        projection_root.mkdir()
        result = discover_problems(self.root, self.head, projection_root)
        by_id = {item["problemId"]: item for item in result["problems"]}
        self.assertEqual(result["projectionInspection"], "verified")
        self.assertEqual(by_id["fresh"]["stage"], "ready-for-first-contribution")
        self.assertEqual(by_id["started"]["stage"], "knowledge-current")
        self.assertTrue(
            by_id["started"]["publishedKnowledgeProjections"][0]["current"]
        )

    @patch("math_flow.discovery.list_active_projections", side_effect=_active)
    def test_cli_filters_ready_problems(self, _active_mock) -> None:
        output = self.root / "problems.json"
        self.assertEqual(
            main(
                [
                    "--root",
                    str(self.root),
                    "list-problems",
                    "--head",
                    self.head,
                    "--stage",
                    "ready-for-first-contribution",
                    "--output",
                    str(output),
                ]
            ),
            0,
        )
        value = json.loads(output.read_text(encoding="utf-8"))
        self.assertEqual([item["problemId"] for item in value["problems"]], ["fresh"])

    @patch("math_flow.discovery.list_active_projections", side_effect=_active)
    def test_archived_problems_are_hidden_by_default_and_explicitly_discoverable(
        self, _active_mock
    ) -> None:
        write(
            self.root / "protocol/problem-registry.json",
            json.dumps(
                {
                    "schemaVersion": 1,
                    "archivedProblems": ["fresh"],
                }
            ),
        )
        git(self.root, "add", ".")
        git(self.root, "commit", "-qm", "Archive fresh problem")
        head = git(self.root, "rev-parse", "HEAD")

        active = discover_problems(self.root, head)
        self.assertEqual(
            [item["problemId"] for item in active["problems"]], ["started"]
        )
        self.assertEqual(active["archivedProblemCount"], 1)

        complete = discover_problems(self.root, head, include_archived=True)
        by_id = {item["problemId"]: item for item in complete["problems"]}
        self.assertEqual(by_id["fresh"]["status"], "archived")
        self.assertEqual(by_id["fresh"]["stage"], "archived")
        self.assertEqual(by_id["fresh"]["activeKnowledgeProjectionIds"], [])


if __name__ == "__main__":
    unittest.main()
