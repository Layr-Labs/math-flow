from __future__ import annotations

import json
import unittest
from pathlib import Path

from math_flow.judges import load_judge_spec


class ResearchProgramProjectionTests(unittest.TestCase):
    def setUp(self) -> None:
        self.root = Path(__file__).parents[1]

    def test_v3_builder_uses_revisable_taxonomy_policy(self) -> None:
        builder_path = (
            self.root
            / "protocol/judges/openrouter-research-program-builder-v3.json"
        )
        builder = load_judge_spec(builder_path)

        self.assertEqual(builder["implementation"], "openrouter-knowledge-builder-v3")
        self.assertEqual(
            builder["outputProfile"], "math-flow/knowledge-build-markdown-v2"
        )
        self.assertEqual(
            builder["outputAdapter"],
            "select-form-extract-knowledge-revisions-v2",
        )
        self.assertEqual(builder["reducer"], "hierarchical-knowledge-revisions-v3")
        self.assertIn("do not treat the current taxonomy as immutable", builder["systemPrompt"])
        self.assertIn("split a broad program into sibling successors", builder["systemPrompt"])
        self.assertIn("central exact-value question", builder["systemPrompt"])
        self.assertIn("never itself a knowledge node", builder["systemPrompt"])

    def test_v2_builder_remains_frozen_for_active_projection_replay(self) -> None:
        builder = load_judge_spec(
            self.root
            / "protocol/judges/openrouter-research-program-builder-v2.json"
        )
        self.assertEqual(builder["implementation"], "openrouter-knowledge-builder-v2")
        self.assertIn("additive institutional memory", builder["systemPrompt"])
        self.assertNotIn("split a broad program", builder["systemPrompt"])

    def test_specialized_projection_has_distinct_scope_and_shared_judges(self) -> None:
        default = json.loads(
            (self.root / "protocol/projections/openrouter-research-v1.json").read_text(
                encoding="utf-8"
            )
        )
        specialized = json.loads(
            (
                self.root
                / "protocol/projections/openrouter-no-three-in-line-research-programs-v2.json"
            ).read_text(encoding="utf-8")
        )

        self.assertEqual(default["allowedProblems"], ["*"])
        self.assertEqual(specialized["allowedProblems"], ["no-three-in-line-77"])
        self.assertNotEqual(default["id"], specialized["id"])
        if default["primaryJudge"] == (
            "protocol/judges/openrouter-validity-judgment-v2.json"
        ):
            self.assertIsNone(default["reconciliationJudge"])
            self.assertEqual(
                default["knowledgeBuilder"],
                "protocol/judges/openrouter-hierarchical-research-builder-v2.json",
            )
        else:
            self.assertEqual(
                default["primaryJudge"],
                "protocol/judges/openrouter-markdown-judgment-v1.json",
            )
            self.assertEqual(
                default["reconciliationJudge"],
                "protocol/judges/openrouter-markdown-reconciliation-v1.json",
            )
            self.assertEqual(
                default["knowledgeBuilder"],
                "protocol/judges/openrouter-research-program-builder-v2.json",
            )
        if default["primaryJudge"].endswith("validity-judgment-v2.json"):
            self.assertNotEqual(default["primaryJudge"], specialized["primaryJudge"])
        else:
            self.assertEqual(default["primaryJudge"], specialized["primaryJudge"])
        self.assertIsNotNone(specialized["reconciliationJudge"])
        self.assertEqual(
            specialized["knowledgeBuilder"],
            "protocol/judges/openrouter-research-program-builder-v2.json",
        )

    def test_hierarchical_research_builder_separates_state_from_credit(self) -> None:
        builder = load_judge_spec(
            self.root
            / "protocol/judges/openrouter-hierarchical-research-builder-v2.json"
        )
        self.assertEqual(
            builder["implementation"],
            "openrouter-hierarchical-research-builder-v2",
        )
        self.assertEqual(builder["outputProfile"], "math-flow/hierarchical-research-v2")
        self.assertEqual(builder["reducer"], "batched-research-state-v2")
        self.assertNotIn("credit", builder["stages"])
        self.assertIn("exclude invalid and indeterminate claims", builder["systemPrompt"])

    def test_hosted_primary_judgments_are_not_globally_serialized(self) -> None:
        workflow = (
            self.root / ".github/workflows/project-openrouter.yml"
        ).read_text(encoding="utf-8")
        self.assertNotIn("\nconcurrency:\n", workflow)
        self.assertIn("reconciliation_enabled", workflow)
        self.assertIn("This projection has no reconciliation stage.", workflow)


if __name__ == "__main__":
    unittest.main()
