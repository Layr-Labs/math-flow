from __future__ import annotations

import json
import subprocess
import tempfile
import unittest
from pathlib import Path

from math_flow.errors import MathFlowError
from math_flow.problem_registry import (
    active_problem_ids,
    load_problem_registry,
    problem_status,
    validate_problem_registry,
)
from math_flow.repository import affected_problems, validate_pr, validate_tree


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


class ProblemRegistryTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        git(self.root, "init", "-q")
        git(self.root, "config", "user.name", "Test Author")
        git(self.root, "config", "user.email", "test@example.com")
        write(self.root / "problems/active/problem.md", "# Active\n")
        write(self.root / "problems/archived/problem.md", "# Archived\n")
        git(self.root, "add", ".")
        git(self.root, "commit", "-qm", "Admit problems")
        self.unarchived_head = git(self.root, "rev-parse", "HEAD")

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def archive_problem(self) -> str:
        write(
            self.root / "protocol/problem-registry.json",
            json.dumps(
                {
                    "schemaVersion": 1,
                    "archivedProblems": ["archived"],
                },
                indent=2,
            )
            + "\n",
        )
        git(self.root, "add", ".")
        git(self.root, "commit", "-qm", "Archive one problem")
        return git(self.root, "rev-parse", "HEAD")

    def test_absent_registry_keeps_every_problem_active(self) -> None:
        self.assertEqual(
            load_problem_registry(self.root, self.unarchived_head),
            {"schemaVersion": 1, "archivedProblems": []},
        )
        self.assertEqual(
            active_problem_ids(self.root, self.unarchived_head),
            ["active", "archived"],
        )

    def test_archive_is_reversible_metadata_not_ledger_deletion(self) -> None:
        archived_head = self.archive_problem()
        self.assertEqual(problem_status(self.root, "archived", archived_head), "archived")
        self.assertEqual(problem_status(self.root, "active", archived_head), "active")
        self.assertEqual(active_problem_ids(self.root, archived_head), ["active"])
        self.assertEqual(validate_tree(self.root)["problems"], 2)

        write(
            self.root / "protocol/problem-registry.json",
            '{"schemaVersion": 1, "archivedProblems": []}\n',
        )
        git(self.root, "add", ".")
        git(self.root, "commit", "-qm", "Restore archived problem")
        restored_head = git(self.root, "rev-parse", "HEAD")
        self.assertEqual(problem_status(self.root, "archived", restored_head), "active")

    def test_registry_rejects_unknown_unsorted_and_duplicate_ids(self) -> None:
        with self.assertRaisesRegex(MathFlowError, "unknown problem"):
            validate_problem_registry(
                {"schemaVersion": 1, "archivedProblems": ["missing"]},
                ["active", "archived"],
            )
        for archived in (["archived", "active"], ["active", "active"]):
            with self.assertRaisesRegex(MathFlowError, "unique and sorted"):
                validate_problem_registry(
                    {"schemaVersion": 1, "archivedProblems": archived},
                    ["active", "archived"],
                )

    def test_archived_problem_rejects_new_participant_events(self) -> None:
        archived_head = self.archive_problem()
        write(
            self.root / "problems/archived/contributions/late/README.md",
            "# Late contribution\n",
        )
        git(self.root, "add", ".")
        git(self.root, "commit", "-qm", "Attempt archived contribution")
        contribution_head = git(self.root, "rev-parse", "HEAD")
        with self.assertRaisesRegex(MathFlowError, "archived"):
            validate_pr(self.root, archived_head, contribution_head)

    def test_affected_problem_planning_omits_archived_problems(self) -> None:
        archived_head = self.archive_problem()
        write(self.root / "math_flow/runtime.py", "# shared change\n")
        git(self.root, "add", ".")
        git(self.root, "commit", "-qm", "Change shared runtime")
        changed_head = git(self.root, "rev-parse", "HEAD")
        affected = affected_problems(
            self.root,
            archived_head,
            changed_head,
            ["math_flow/**"],
        )
        self.assertEqual(affected["problems"], ["active"])


if __name__ == "__main__":
    unittest.main()
