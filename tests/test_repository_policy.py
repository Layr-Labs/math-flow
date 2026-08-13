from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class RepositoryPolicyTests(unittest.TestCase):
    def test_every_workflow_is_covered_by_codeowners_wildcard(self) -> None:
        codeowners = (ROOT / ".github" / "CODEOWNERS").read_text(encoding="utf-8")
        rules = {
            line.split()[0]
            for line in codeowners.splitlines()
            if line.strip() and not line.lstrip().startswith("#")
        }
        self.assertIn("/.github/workflows/**", rules)
        self.assertTrue(list((ROOT / ".github" / "workflows").glob("*.yml")))

    def test_participant_event_paths_are_not_codeowned(self) -> None:
        codeowners = (ROOT / ".github" / "CODEOWNERS").read_text(encoding="utf-8")
        self.assertNotIn("/problems/**", codeowners)
        self.assertNotIn("/problems/*/contributions/", codeowners)
        self.assertNotIn("/problems/*/directions/", codeowners)


if __name__ == "__main__":
    unittest.main()
