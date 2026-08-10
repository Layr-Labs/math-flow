from __future__ import annotations

import json
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from math_flow.context import _select_projection, materialize_agent_context
from math_flow.errors import MathFlowError


def git(root: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", *args], cwd=root, check=True, stdout=subprocess.PIPE, text=True
    )
    return result.stdout.strip()


def write(path: Path, value: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(value, encoding="utf-8")


class AgentContextTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        git(self.root, "init", "-q")
        git(self.root, "config", "user.name", "Test Author")
        git(self.root, "config", "user.email", "test@example.com")
        write(self.root / "problems/demo/problem.md", "# Demo problem\n\nFind a proof.\n")
        git(self.root, "add", ".")
        git(self.root, "commit", "-qm", "Create problem")
        self.first = self._commit_contribution("first", "# First\n\nInitial evidence.\n")
        self.second = self._commit_contribution("second", "# Second\n\nNew evidence.\n")
        self.projection_root = self.root / "projection-worktree"
        write(
            self.projection_root / "coordination/scheduler.json",
            json.dumps(
                {
                    "schemaVersion": 1,
                    "lanes": {
                        "lane-one": {
                            "pendingJudgmentIds": ["sha256:" + "b" * 64],
                            "pendingConflictIds": [],
                            "activeBuild": None,
                            "nextEligibleAt": 123,
                        }
                    },
                }
            ),
        )

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def _commit_contribution(self, name: str, body: str) -> str:
        write(self.root / f"problems/demo/contributions/{name}/README.md", body)
        git(self.root, "add", ".")
        git(self.root, "commit", "-qm", f"Add {name}")
        return git(self.root, "rev-parse", "HEAD")

    def _catalog(self) -> dict[str, object]:
        state = {
            "schemaVersion": 2,
            "problemId": "demo",
            "rootId": "root",
            "nodes": {
                "root": {
                    "id": "root",
                    "parentId": None,
                    "type": "root",
                    "title": "Demo knowledge",
                    "summary": "Root summary",
                    "status": "active",
                    "contentMarkdown": "Current root assessment.",
                    "subjects": [],
                    "evidence": [],
                    "digest": "sha256:" + "1" * 64,
                },
                "program": {
                    "id": "program",
                    "parentId": "root",
                    "type": "program",
                    "title": "Program",
                    "summary": "Program summary",
                    "status": "active",
                    "contentMarkdown": "Program assessment.",
                    "subjects": [{"kind": "transaction", "id": self.first}],
                    "evidence": [],
                    "digest": "sha256:" + "2" * 64,
                },
                "program/claim": {
                    "id": "program/claim",
                    "parentId": "program",
                    "type": "claim",
                    "title": "Claim",
                    "summary": "Claim summary",
                    "status": "active",
                    "contentMarkdown": "Detailed claim assessment.",
                    "subjects": [],
                    "evidence": [],
                    "digest": "sha256:" + "3" * 64,
                },
                "other": {
                    "id": "other",
                    "parentId": "root",
                    "type": "question",
                    "title": "Other",
                    "summary": "Other summary",
                    "status": "active",
                    "contentMarkdown": "Unrelated assessment.",
                    "subjects": [],
                    "evidence": [],
                    "digest": "sha256:" + "4" * 64,
                },
            },
            "stateDigest": "sha256:" + "a" * 64,
        }
        return {
            "schemaVersion": 1,
            "projections": [
                {
                    "id": "projection-one",
                    "problemId": "demo",
                    "label": "Builder one",
                    "builder": {"id": "builder-one"},
                    "latestRunDigest": "sha256:" + "c" * 64,
                    "runCount": 1,
                    "data": {
                        "problem": {
                            "id": "demo",
                            "title": "Demo problem",
                            "statementMarkdown": "# Demo problem\n\nFind a proof.\n",
                        },
                        "judgments": [
                            {
                                "record": {
                                    "judgmentKind": "primary",
                                    "subjects": [
                                        {"kind": "transaction", "id": self.first}
                                    ],
                                }
                            }
                        ],
                        "runs": [
                            {
                                "ledgerHead": self.first,
                                "problemLedgerHead": self.first,
                                "inputs": {"laneId": "lane-one"},
                                "state": state,
                            }
                        ],
                    },
                }
            ],
        }

    def test_materializes_exact_state_and_scoped_markdown_with_staleness(self) -> None:
        output = self.root / "agent-context"
        catalog = self._catalog()
        with patch("math_flow.context.export_viewer_catalog", return_value=catalog):
            summary = materialize_agent_context(
                self.root,
                self.projection_root,
                "demo",
                output,
                head="HEAD",
                node_ids=["program"],
            )

        expected_state = catalog["projections"][0]["data"]["runs"][0]["state"]
        self.assertEqual(json.loads((output / "state.json").read_text()), expected_state)
        context = json.loads((output / "context.json").read_text())
        self.assertEqual(summary["freshness"], "stale")
        self.assertEqual(context["verification"]["baseRunChain"], "verified")
        self.assertEqual(context["freshness"]["repositoryHistoryRelation"], "projection-is-ancestor")
        self.assertEqual(
            context["freshness"]["canonicalTransactionsMissingFromProjection"],
            [self.second],
        )
        self.assertEqual(
            context["scope"]["includedNodeIds"], ["program", "program/claim"]
        )
        self.assertEqual(len(context["coverage"]["canonicalTransactionsWithoutBuiltPrimaryJudgment"]), 1)
        self.assertEqual(context["coordination"]["pendingJudgmentIds"], ["sha256:" + "b" * 64])
        markdown = (output / "context.md").read_text()
        self.assertIn("Program assessment.", markdown)
        self.assertIn("Detailed claim assessment.", markdown)
        self.assertNotIn("Unrelated assessment.", markdown)
        self.assertIn("untrusted research content", markdown)

    def test_requires_explicit_projection_when_multiple_exist(self) -> None:
        catalog = self._catalog()
        second = dict(catalog["projections"][0])
        second["id"] = "projection-two"
        catalog["projections"].append(second)
        with self.assertRaisesRegex(MathFlowError, "select one with --projection"):
            _select_projection(catalog, "demo", None)
        self.assertEqual(
            _select_projection(catalog, "demo", "projection-two")["id"],
            "projection-two",
        )

    def test_rejects_unknown_scoped_node_without_writing(self) -> None:
        output = self.root / "agent-context"
        with patch("math_flow.context.export_viewer_catalog", return_value=self._catalog()):
            with self.assertRaisesRegex(MathFlowError, "unknown knowledge node"):
                materialize_agent_context(
                    self.root,
                    self.projection_root,
                    "demo",
                    output,
                    node_ids=["missing"],
                )
        self.assertFalse(output.exists())


if __name__ == "__main__":
    unittest.main()
