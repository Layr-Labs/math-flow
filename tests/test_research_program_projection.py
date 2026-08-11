from __future__ import annotations

import json
import unittest
from pathlib import Path

from math_flow.judges import load_judge_spec


class ResearchProgramProjectionTests(unittest.TestCase):
    def setUp(self) -> None:
        self.root = Path(__file__).parents[1]

    def test_builder_uses_neutral_v2_profile_and_additive_program_policy(self) -> None:
        builder_path = (
            self.root
            / "protocol/judges/openrouter-research-program-builder-v2.json"
        )
        builder = load_judge_spec(builder_path)

        self.assertEqual(builder["implementation"], "openrouter-knowledge-builder-v2")
        self.assertEqual(
            builder["outputProfile"], "math-flow/knowledge-build-markdown-v2"
        )
        self.assertEqual(
            builder["outputAdapter"],
            "select-form-extract-knowledge-revisions-v2",
        )
        self.assertEqual(builder["reducer"], "hierarchical-knowledge-revisions-v3")
        self.assertIn("additive institutional memory", builder["systemPrompt"])
        self.assertIn("central exact-value question", builder["systemPrompt"])
        self.assertIn("never itself a knowledge node", builder["systemPrompt"])

    def test_projection_does_not_mutate_the_legacy_wildcard_projection(self) -> None:
        legacy = json.loads(
            (self.root / "protocol/projections/openrouter-research-v1.json").read_text(
                encoding="utf-8"
            )
        )
        self.assertEqual(legacy["allowedProblems"], ["*"])
        self.assertEqual(
            legacy["knowledgeBuilder"],
            "protocol/judges/openrouter-knowledge-builder-v1.json",
        )


if __name__ == "__main__":
    unittest.main()
