from __future__ import annotations

import json
import unittest
from pathlib import Path

from math_flow.governance import validate_projection_spec
from math_flow.repository import sha256_json
from math_flow.research_topology import empty_research_program_state_v2
from math_flow.work_accounting import (
    make_zero_work_accounting_state,
    validate_root_contract,
)


ROOT = Path(__file__).resolve().parents[1]
CONTRACT_PATH = (
    ROOT / "protocol/runtime/inactive-bssc-work-accounting-root-contract-v1.json"
)
PROJECTION_PATH = (
    ROOT / "protocol/runtime/inactive-openrouter-research-v4-projection.json"
)
OVERLAY_PATH = (
    ROOT / "protocol/runtime/inactive-openrouter-work-accounting-v1-projection.json"
)


class BSSCRootContractTests(unittest.TestCase):
    def test_inactive_root_contract_binds_exact_candidate_projection(self) -> None:
        projection = json.loads(PROJECTION_PATH.read_text(encoding="utf-8"))
        reader = lambda relative: (ROOT / relative).read_text(encoding="utf-8")
        validate_projection_spec(projection, "openrouter-research-v4", reader)

        contract = validate_root_contract(
            json.loads(CONTRACT_PATH.read_text(encoding="utf-8")),
            "bssc-sum-capacity",
        )
        self.assertEqual(contract["knowledgeProjectionId"], projection["id"])
        self.assertEqual(
            contract["knowledgeProjectionSpecDigest"],
            f"sha256:{sha256_json(projection)}",
        )
        self.assertEqual(projection["status"], "disabled")
        self.assertEqual(projection["allowedProblems"], ["bssc-sum-capacity"])
        self.assertFalse(
            (ROOT / "protocol/projections/openrouter-research-v4.json").exists()
        )

        overlay = json.loads(OVERLAY_PATH.read_text(encoding="utf-8"))
        validate_projection_spec(overlay, "openrouter-work-accounting-v1", reader)
        self.assertEqual(
            overlay["dependencies"],
            [
                {
                    "name": "knowledge",
                    "projectionId": projection["id"],
                    "artifactRole": "research-builder-handoff",
                }
            ],
        )
        self.assertFalse(
            (ROOT / "protocol/projections/openrouter-work-accounting-v1.json").exists()
        )

    def test_contract_has_a_deterministic_zero_origin(self) -> None:
        contract = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))
        knowledge = empty_research_program_state_v2("bssc-sum-capacity")
        accounting = make_zero_work_accounting_state(
            root_contract=contract,
            knowledge_state=knowledge,
        )
        self.assertIsNone(knowledge["ledgerHead"])
        self.assertEqual(knowledge["contributions"], {})
        self.assertEqual(accounting["processedSubmissionIds"], [])
        self.assertEqual(accounting["totalWorkHours"], "0")


if __name__ == "__main__":
    unittest.main()
