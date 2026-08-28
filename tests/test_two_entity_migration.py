from __future__ import annotations

import copy
import json
import tempfile
import unittest
from pathlib import Path

from math_flow.cli import main
from math_flow.errors import MathFlowError
from math_flow.repository import sha256_json
from math_flow.research_topology import validate_research_program_state_v2
from math_flow.two_entity_migration import (
    audit_two_entity_migration_v2,
    migrate_research_program_state_v2_to_v3,
)


TRANSACTION_A = "a" * 40
TRANSACTION_B = "b" * 40
JUDGMENT_A = "sha256:" + "1" * 64
JUDGMENT_B = "sha256:" + "2" * 64


def _record(value: dict[str, object]) -> dict[str, object]:
    result = copy.deepcopy(value)
    result["digest"] = f"sha256:{sha256_json(result)}"
    return result


def _item(
    item_id: str,
    item_type: str,
    transaction_id: str,
    *,
    dependencies: list[str] | None = None,
    claim_key: str = "claim",
    program_id: str = "root",
) -> dict[str, object]:
    return _record(
        {
            "id": item_id,
            "programId": program_id,
            "type": item_type,
            "title": f"Title for {item_id}",
            "summary": f"Summary for {item_id}.",
            "claimRefs": [
                {"transactionId": transaction_id, "claimKey": claim_key}
            ],
            "sourceTransactionIds": [transaction_id],
            "dependencyItemIds": dependencies or [],
        }
    )


def _source_state(
    contribution_items: list[tuple[str, str, list[dict[str, object]]]],
) -> dict[str, object]:
    transactions = [transaction_id for transaction_id, _, _ in contribution_items]
    root = _record(
        {
            "id": "root",
            "parentId": None,
            "title": "Root program",
            "objective": "Resolve the canonical problem.",
            "status": "active",
            "parentThreadIds": [],
            "sourceTransactionIds": [],
            "lineage": [],
        }
    )
    residual = _record(
        {
            "id": "root/unstructured-search",
            "programId": "root",
            "title": "Residual work",
            "summary": "Work not yet decomposed into a named direction.",
            "kind": "unstructured",
            "status": "active",
            "expectedExposure": "0",
            "conditions": [],
            "sourceTransactionIds": [],
        }
    )
    route = _record(
        {
            "id": "root/algebraic-route",
            "programId": "root",
            "title": "Algebraic route",
            "summary": "Develop an algebraic reduction.",
            "kind": "research",
            "status": "active",
            "expectedExposure": "12",
            "conditions": ["The reduction remains applicable."],
            "sourceTransactionIds": transactions,
        }
    )
    items: dict[str, dict[str, object]] = {}
    contributions: dict[str, dict[str, object]] = {}
    for index, (transaction_id, judgment_id, records) in enumerate(
        contribution_items
    ):
        for record in records:
            items[str(record["id"])] = record
        claim_keys = sorted(
            {
                str(reference["claimKey"])
                for record in records
                for reference in record["claimRefs"]
            }
        )
        contributions[transaction_id] = _record(
            {
                "id": transaction_id,
                "transactionId": transaction_id,
                "claimKeys": claim_keys,
                "directProgramId": "root",
                "directThreadIds": ["root/algebraic-route"],
                "itemIds": [str(record["id"]) for record in records],
                "dependencyTransactionIds": (
                    [] if index == 0 else [transactions[index - 1]]
                ),
                "judgmentId": judgment_id,
            }
        )
    state = {
        "schemaVersion": 2,
        "problemId": "test-problem",
        "ledgerHead": transactions[-1],
        "baseStateDigest": None,
        "rootProgramId": "root",
        "programs": {"root": root},
        "threads": {
            "root/unstructured-search": residual,
            "root/algebraic-route": route,
        },
        "items": items,
        "contributions": contributions,
    }
    state["stateDigest"] = f"sha256:{sha256_json(state)}"
    validate_research_program_state_v2(state)
    return state


class TwoEntityMigrationTests(unittest.TestCase):
    def test_unambiguous_state_folds_threads_and_support(self) -> None:
        proof = _item("item/proof", "proof", TRANSACTION_A)
        tool = _item("item/tool", "tool", TRANSACTION_A)
        result = _item(
            "item/result",
            "result",
            TRANSACTION_A,
            dependencies=["item/proof", "item/tool"],
        )
        source = _source_state(
            [(TRANSACTION_A, JUDGMENT_A, [result, proof, tool])]
        )
        original = copy.deepcopy(source)

        audit = audit_two_entity_migration_v2(source)
        migrated = migrate_research_program_state_v2_to_v3(source)

        self.assertEqual(source, original)
        self.assertEqual(audit["status"], "ready")
        self.assertEqual(audit["unresolvedMappings"], [])
        self.assertEqual(audit["proposedState"], migrated)
        self.assertEqual(migrated["schemaVersion"], 3)
        self.assertIsNone(migrated["baseStateDigest"])
        self.assertEqual(
            set(migrated["programs"]), {"root", "root/algebraic-route"}
        )
        self.assertIn(
            "Work not yet decomposed",
            migrated["programs"]["root"]["localResidualSummary"],
        )
        self.assertEqual(
            migrated["programs"]["root/algebraic-route"]["parentId"], "root"
        )
        intermediate_result = migrated["intermediateResults"]["item/result"]
        self.assertEqual(intermediate_result["primaryProgramId"], "root")
        self.assertEqual(
            intermediate_result["relatedProgramIds"], ["root/algebraic-route"]
        )
        self.assertEqual(
            intermediate_result["support"]["proofs"],
            ["Title for item/proof\n\nSummary for item/proof."],
        )
        self.assertEqual(
            intermediate_result["support"]["tools"],
            ["Title for item/tool\n\nSummary for item/tool."],
        )
        self.assertEqual(
            migrated["programs"]["root"]["intermediateResultIds"],
            ["item/result"],
        )
        self.assertEqual(
            migrated["programs"]["root/algebraic-route"][
                "intermediateResultIds"
            ],
            ["item/result"],
        )
        self.assertEqual(
            migrated["contributions"][TRANSACTION_A]["directProgramIds"],
            ["root", "root/algebraic-route"],
        )
        self.assertEqual(audit["summary"]["bundledSupportItemCount"], 2)
        self.assertEqual(audit_two_entity_migration_v2(source), audit)

    def test_dependency_edges_collapse_to_result_dependencies(self) -> None:
        first_proof = _item("item/first-proof", "proof", TRANSACTION_A)
        first_result = _item(
            "item/first-result",
            "result",
            TRANSACTION_A,
            dependencies=["item/first-proof"],
        )
        second_computation = _item(
            "item/second-computation",
            "computation",
            TRANSACTION_B,
            claim_key="second-claim",
            dependencies=["item/first-proof"],
        )
        second_result = _item(
            "item/second-result",
            "result",
            TRANSACTION_B,
            claim_key="second-claim",
            dependencies=["item/second-computation", "item/first-result"],
        )
        source = _source_state(
            [
                (TRANSACTION_A, JUDGMENT_A, [first_result, first_proof]),
                (
                    TRANSACTION_B,
                    JUDGMENT_B,
                    [second_result, second_computation],
                ),
            ]
        )

        migrated = migrate_research_program_state_v2_to_v3(source)

        self.assertEqual(
            migrated["intermediateResults"]["item/second-result"][
                "dependencyResultIds"
            ],
            ["item/first-result"],
        )

    def test_direct_dependency_disambiguates_multiple_results(self) -> None:
        proof = _item("item/proof", "proof", TRANSACTION_A)
        first = _item(
            "item/result-a",
            "result",
            TRANSACTION_A,
            dependencies=["item/proof"],
        )
        second = _item("item/result-b", "result", TRANSACTION_A)
        source = _source_state(
            [(TRANSACTION_A, JUDGMENT_A, [first, second, proof])]
        )

        audit = audit_two_entity_migration_v2(source)

        self.assertEqual(audit["status"], "ready")
        mapping = {
            value["sourceItemId"]: value["targetIntermediateResultId"]
            for value in audit["itemMappings"]
        }
        self.assertEqual(mapping["item/proof"], "item/result-a")

    def test_bundle_contraction_that_creates_dependency_cycle_is_unresolved(self) -> None:
        first_support = _item("item/first-proof", "proof", TRANSACTION_A)
        second_support = _item(
            "item/second-proof",
            "proof",
            TRANSACTION_B,
            claim_key="second-claim",
        )
        first_result = _item(
            "item/first-result",
            "result",
            TRANSACTION_A,
            dependencies=["item/second-proof"],
        )
        second_result = _item(
            "item/second-result",
            "result",
            TRANSACTION_B,
            claim_key="second-claim",
            dependencies=["item/first-proof"],
        )
        source = _source_state(
            [
                (TRANSACTION_A, JUDGMENT_A, [first_result, first_support]),
                (TRANSACTION_B, JUDGMENT_B, [second_result, second_support]),
            ]
        )

        audit = audit_two_entity_migration_v2(source)

        self.assertEqual(audit["status"], "unresolved")
        self.assertEqual(
            audit["unresolvedMappings"][0]["reasonCode"],
            "dependency-cycle-after-bundling",
        )

    def test_ambiguous_support_is_reported_and_strict_migration_fails(self) -> None:
        first = _item("item/result-a", "result", TRANSACTION_A)
        second = _item("item/result-b", "result", TRANSACTION_A)
        proof = _item("item/proof", "proof", TRANSACTION_A)
        source = _source_state(
            [(TRANSACTION_A, JUDGMENT_A, [first, second, proof])]
        )

        audit = audit_two_entity_migration_v2(source)

        self.assertEqual(audit["status"], "unresolved")
        self.assertIsNone(audit["proposedState"])
        self.assertEqual(
            audit["unresolvedMappings"][0]["reasonCode"],
            "ambiguous-support-result",
        )
        self.assertEqual(
            audit["unresolvedMappings"][0]["candidateIntermediateResultIds"],
            ["item/result-a", "item/result-b"],
        )
        with self.assertRaisesRegex(
            MathFlowError, "ambiguous-support-result:item/proof"
        ):
            migrate_research_program_state_v2_to_v3(source)

    def test_question_item_requires_explicit_program_or_result_choice(self) -> None:
        result = _item("item/result", "result", TRANSACTION_A)
        question = _item("item/question", "question", TRANSACTION_A)
        source = _source_state(
            [(TRANSACTION_A, JUDGMENT_A, [result, question])]
        )

        audit = audit_two_entity_migration_v2(source)

        self.assertEqual(audit["status"], "unresolved")
        self.assertEqual(
            audit["unresolvedMappings"][0]["reasonCode"],
            "question-item-requires-semantic-choice",
        )

    def test_invalid_source_state_is_rejected_before_planning(self) -> None:
        result = _item("item/result", "result", TRANSACTION_A)
        source = _source_state([(TRANSACTION_A, JUDGMENT_A, [result])])
        source["stateDigest"] = "sha256:" + "0" * 64

        with self.assertRaisesRegex(MathFlowError, "state v2 digest mismatch"):
            audit_two_entity_migration_v2(source)

    def test_cli_writes_the_provider_free_audit(self) -> None:
        result = _item("item/result", "result", TRANSACTION_A)
        source = _source_state([(TRANSACTION_A, JUDGMENT_A, [result])])
        with tempfile.TemporaryDirectory() as directory_value:
            directory = Path(directory_value)
            state_path = directory / "state.json"
            output_path = directory / "audit.json"
            state_path.write_text(json.dumps(source), encoding="utf-8")

            exit_code = main(
                [
                    "two-entity-migration-audit",
                    "--state",
                    str(state_path),
                    "--output",
                    str(output_path),
                ]
            )
            audit = json.loads(output_path.read_text(encoding="utf-8"))

        self.assertEqual(exit_code, 0)
        self.assertEqual(audit["status"], "ready")
        self.assertEqual(audit["sourceStateDigest"], source["stateDigest"])


if __name__ == "__main__":
    unittest.main()
