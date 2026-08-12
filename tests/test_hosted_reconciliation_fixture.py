from __future__ import annotations

import json
import tempfile
import unittest
from copy import deepcopy
from pathlib import Path
from unittest.mock import patch

from math_flow.judgments import (
    plan_reconciliation_inputs,
    run_reconciliation_judgment_bundle,
)
from math_flow.judges import load_source
from math_flow.hosted_reconciliation_smoke import (
    CLAIM_KEY,
    PRIMARY_JUDGE,
    PROBLEM_ID,
    prepare_fixture,
)


class HostedReconciliationFixtureTests(unittest.TestCase):
    def test_fixture_pins_reviewed_prefix_when_later_contributions_exist(self) -> None:
        root = Path(__file__).parents[1]
        current = load_source(root, PROBLEM_ID, "HEAD")
        extended = deepcopy(current)
        extended["transactions"].append(
            {
                **extended["transactions"][-1],
                "ordinal": len(extended["transactions"]) + 1,
                "contributionId": "later-contribution",
            }
        )
        calls = 0

        def source_at(
            source_root: Path, problem: str, head: str
        ) -> dict[str, object]:
            nonlocal calls
            calls += 1
            return extended if calls == 1 else load_source(source_root, problem, head)

        with tempfile.TemporaryDirectory() as temporary, patch(
            "math_flow.hosted_reconciliation_smoke.load_source",
            side_effect=source_at,
        ):
            plan = prepare_fixture(root, Path(temporary) / "staging")

        self.assertEqual(len(plan["primaryBundlePaths"]), 4)
        self.assertEqual(
            plan["ledgerHead"], current["transactions"][-1]["transactionId"]
        )

    def test_fixture_covers_ledger_and_derives_one_current_conflict(self) -> None:
        root = Path(__file__).parents[1]
        with tempfile.TemporaryDirectory() as temporary:
            staging = Path(temporary) / "staging"
            plan = prepare_fixture(root, staging)
            projection = Path(temporary) / "projection"
            projection.mkdir()
            reconciliation_plan = plan_reconciliation_inputs(
                root,
                projection,
                PROBLEM_ID,
                root / PRIMARY_JUDGE,
                root
                / "protocol/judges/openrouter-markdown-reconciliation-v1.json",
                str(plan["ledgerHead"]),
                [Path(item) for item in plan["primaryBundlePaths"]],
            )
            conflict = json.loads(
                (staging / "conflicts.json").read_text(encoding="utf-8")
            )["conflicts"][0]
            conflict_judgment_ids = {
                str(item["judgmentId"]) for item in conflict["judgments"]
            }
            transaction_ids: list[str] = []
            for bundle in plan["primaryBundlePaths"]:
                judgment = json.loads(
                    (Path(bundle) / "judgment.json").read_text(encoding="utf-8")
                )
                if judgment["judgmentId"] in conflict_judgment_ids:
                    transaction_ids.extend(
                        str(subject["id"]) for subject in judgment["subjects"]
                    )
            responses = iter(
                [
                    {
                        "id": "fixture-reconciliation-report",
                        "model": "openai/gpt-5.6-sol",
                        "choices": [
                            {
                                "message": {
                                    "content": (
                                        "# Reconciliation\n\nThe later proof refutes the "
                                        "overbroad equivalence while preserving the "
                                        "narrower centered-half-turn conclusion."
                                    )
                                }
                            }
                        ],
                    },
                    {
                        "id": "fixture-reconciliation-extract",
                        "model": "openai/gpt-5.6-sol",
                        "choices": [
                            {
                                "message": {
                                    "content": json.dumps(
                                        {
                                            "outcome": "prefer-refutation",
                                            "summary": "The strict-subclass distinction is decisive.",
                                            "findings": [
                                                {
                                                    "claimKey": CLAIM_KEY,
                                                    "stance": "refutes",
                                                    "summary": "rct4 is a strict subclass.",
                                                    "subjectTransactionIds": transaction_ids,
                                                    "evidenceTransactionIds": transaction_ids,
                                                }
                                            ],
                                        }
                                    )
                                }
                            }
                        ],
                    },
                ]
            )
            reconciliation_bundle = staging / "reconciliation"
            run_reconciliation_judgment_bundle(
                root,
                PROBLEM_ID,
                root
                / "protocol/judges/openrouter-markdown-reconciliation-v1.json",
                str(plan["ledgerHead"]),
                conflict,
                [Path(item) for item in plan["primaryBundlePaths"]],
                reconciliation_bundle,
                transport=lambda _: next(responses),
            )
            verified_plan = plan_reconciliation_inputs(
                root,
                projection,
                PROBLEM_ID,
                root / PRIMARY_JUDGE,
                root
                / "protocol/judges/openrouter-markdown-reconciliation-v1.json",
                str(plan["ledgerHead"]),
                [Path(item) for item in plan["primaryBundlePaths"]],
                [reconciliation_bundle],
                [str(plan["conflictId"])],
            )

        self.assertTrue(plan["fixtureOnly"])
        self.assertEqual(len(reconciliation_plan["primaryJudgmentIds"]), 4)
        self.assertEqual(reconciliation_plan["publishedBundles"], [])
        self.assertEqual(reconciliation_plan["newBundles"], [])
        self.assertEqual(len(reconciliation_plan["missingConflicts"]), 1)
        self.assertEqual(reconciliation_plan["conflicts"][0]["claimKey"], CLAIM_KEY)
        self.assertEqual(
            reconciliation_plan["conflicts"][0]["conflictId"], plan["conflictId"]
        )
        self.assertEqual(verified_plan["missingConflicts"], [])
        self.assertEqual(len(verified_plan["newBundles"]), 1)
        self.assertEqual(
            verified_plan["newBundles"][0]["conflictId"], plan["conflictId"]
        )


if __name__ == "__main__":
    unittest.main()
