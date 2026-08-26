from __future__ import annotations

import copy
import json
import unittest
from pathlib import Path

from math_flow.errors import MathFlowError
from math_flow.judges import load_judge_spec
from math_flow.research_builder_v6 import (
    apply_research_builder_v6_sequence,
    apply_research_builder_v6_transition,
    validate_research_builder_v6_handoff,
)
from math_flow.research_topology import (
    empty_research_program_state_v2,
    validate_research_program_state_v2,
    validate_research_topology_alignment,
)


ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "tests" / "fixtures"
TX_A = "a" * 40
TX_B = "b" * 40
TX_C = "c" * 40
JUDGMENT_A = "sha256:" + "1" * 64
JUDGMENT_B = "sha256:" + "2" * 64
JUDGMENT_C = "sha256:" + "3" * 64


def _program(
    program_id: str,
    parent_id: str,
    parent_thread_ids: list[str],
    source_ids: list[str],
    *,
    status: str = "active",
    lineage: list[dict[str, str]] | None = None,
) -> dict[str, object]:
    return {
        "id": program_id,
        "parentId": parent_id,
        "title": f"Program {program_id}",
        "objective": f"Resolve the local objective for {program_id}.",
        "status": status,
        "parentThreadIds": parent_thread_ids,
        "sourceTransactionIds": source_ids,
        "lineage": lineage or [],
    }


def _thread(
    thread_id: str,
    program_id: str,
    source_ids: list[str],
    *,
    kind: str = "unstructured",
    status: str = "active",
    exposure: str = "1",
) -> dict[str, object]:
    return {
        "id": thread_id,
        "programId": program_id,
        "title": f"Thread {thread_id}",
        "summary": f"Advance {thread_id}.",
        "kind": kind,
        "status": status,
        "expectedExposure": exposure,
        "conditions": [],
        "sourceTransactionIds": source_ids,
    }


def _item(
    item_id: str,
    program_id: str,
    transaction_id: str,
    claim_key: str,
) -> dict[str, object]:
    return {
        "id": item_id,
        "programId": program_id,
        "type": "result",
        "title": f"Result {item_id}",
        "summary": f"Accepted result for {claim_key}.",
        "claimRefs": [
            {"transactionId": transaction_id, "claimKey": claim_key}
        ],
        "sourceTransactionIds": [transaction_id],
        "dependencyItemIds": [],
    }


def _content_operation(
    kind: str,
    entity_id: str,
    value: dict[str, object],
    base_digest: str | None = None,
) -> dict[str, object]:
    return {
        "entityKind": kind,
        "entityId": entity_id,
        "baseDigest": base_digest,
        "value": value,
    }


def _transition(
    base_state: dict[str, object],
    transaction_id: str,
    claim_key: str,
    *,
    program_id: str,
    thread_id: str,
    item_id: str,
    content_operations: list[dict[str, object]],
    topology_operations: list[dict[str, object]] | None = None,
    placement_basis: str = "local-objective",
    related_program_ids: list[str] | None = None,
) -> dict[str, object]:
    topology_operations = topology_operations or []
    if related_program_ids is None:
        related_program_ids = [program_id] if program_id != "root" else []
    return {
        "schemaVersion": 1,
        "subjectTransactionId": transaction_id,
        "baseStateDigest": base_state["stateDigest"],
        "contentOperations": content_operations,
        "topologyOperations": topology_operations,
        "contribution": {
            "claimKeys": [claim_key],
            "directProgramId": program_id,
            "directThreadIds": [thread_id],
            "itemIds": [item_id],
        },
        "placementAudit": {
            "basis": placement_basis,
            "rationale": "This is the narrowest durable objective for the accepted result.",
            "relatedProgramIds": related_program_ids,
        },
        "topologyRationale": (
            "The prior boundary is broader than the stable successor objectives."
            if topology_operations
            else None
        ),
    }


def _first_transition(
    base_state: dict[str, object],
    *,
    transaction_id: str = TX_A,
    claim_key: str = "claim-a",
) -> dict[str, object]:
    return _transition(
        base_state,
        transaction_id,
        claim_key,
        program_id="program-a",
        thread_id="program-a/unstructured",
        item_id="program-a/result-a",
        content_operations=[
            _content_operation(
                "thread",
                "root/program-a-line",
                _thread(
                    "root/program-a-line",
                    "root",
                    [transaction_id],
                    kind="research",
                ),
            ),
            _content_operation(
                "program",
                "program-a",
                _program(
                    "program-a",
                    "root",
                    ["root/program-a-line"],
                    [transaction_id],
                ),
            ),
            _content_operation(
                "thread",
                "program-a/unstructured",
                _thread(
                    "program-a/unstructured", "program-a", [transaction_id]
                ),
            ),
            _content_operation(
                "item",
                "program-a/result-a",
                _item(
                    "program-a/result-a",
                    "program-a",
                    transaction_id,
                    claim_key,
                ),
            ),
        ],
    )


def _accepted_claim(
    claim_key: str, dependencies: list[str] | None = None
) -> list[dict[str, object]]:
    return [
        {
            "claimKey": claim_key,
            "dependencyTransactionIds": dependencies or [],
        }
    ]


def _without_digest(record: dict[str, object]) -> dict[str, object]:
    return {key: copy.deepcopy(value) for key, value in record.items() if key != "digest"}


class ResearchBuilderV6Tests(unittest.TestCase):
    def setUp(self) -> None:
        self.base = empty_research_program_state_v2("handoff-fixture")

    def _first_result(self) -> dict[str, object]:
        return apply_research_builder_v6_transition(
            self.base,
            _first_transition(self.base),
            accepted_claims=_accepted_claim("claim-a"),
            judgment_id=JUDGMENT_A,
        )

    def test_inactive_spec_loads_without_projection_admission(self) -> None:
        spec = load_judge_spec(
            ROOT
            / "protocol"
            / "judges"
            / "openrouter-hierarchical-research-builder-v6.json"
        )
        self.assertEqual(
            spec["implementation"], "openrouter-hierarchical-research-builder-v6"
        )
        projection_text = "\n".join(
            path.read_text(encoding="utf-8")
            for path in (ROOT / "protocol" / "projections").glob("*.json")
        )
        self.assertNotIn("openrouter-hierarchical-research-builder-v6", projection_text)

    def test_one_submission_produces_exact_state_alignment_and_handoff(self) -> None:
        result = self._first_result()
        post_state = result["postState"]
        alignment = result["topologyAlignment"]
        handoff = result["sameWorldHandoff"]
        validate_research_program_state_v2(post_state, "handoff-fixture")
        validate_research_topology_alignment(alignment, self.base, post_state)
        validate_research_builder_v6_handoff(
            handoff, self.base, post_state, alignment, TX_A
        )
        self.assertEqual(post_state["ledgerHead"], TX_A)
        self.assertEqual(handoff["sameWorldReferenceStateDigest"], post_state["stateDigest"])
        self.assertEqual(handoff["accountingNodeKinds"], ["program", "thread"])
        self.assertEqual(handoff["semanticLeafKinds"], ["item"])
        self.assertIn(
            ("item", "program-a/result-a"),
            {
                (entry["entityKind"], entry["entityId"])
                for entry in alignment["created"]
            },
        )

    def test_canonical_sequence_has_one_adjacent_handoff_per_submission(self) -> None:
        fixture = json.loads(
            (FIXTURES / "research_builder_v6_same_world_handoff.json").read_text(
                encoding="utf-8"
            )
        )
        first_transition = _first_transition(self.base)
        first_result = self._first_result()
        first_state = first_result["postState"]
        second_transition = _transition(
            first_state,
            TX_B,
            "claim-b",
            program_id="program-a",
            thread_id="program-a/unstructured",
            item_id="program-a/result-b",
            content_operations=[
                _content_operation(
                    "item",
                    "program-a/result-b",
                    _item("program-a/result-b", "program-a", TX_B, "claim-b"),
                )
            ],
        )
        submissions = [
            {
                "transactionId": item["transactionId"],
                "ordinal": item["ordinal"],
                "acceptedClaims": _accepted_claim(item["claimKey"]),
                "judgmentId": JUDGMENT_A if index == 0 else JUDGMENT_B,
            }
            for index, item in enumerate(fixture["acceptedSubmissions"])
        ]
        results = apply_research_builder_v6_sequence(
            self.base,
            [first_transition, second_transition],
            accepted_submissions=submissions,
        )
        self.assertEqual(len(results), 2)
        self.assertEqual(
            results[0]["postState"]["stateDigest"],
            results[1]["topologyAlignment"]["beforeKnowledgeStateDigest"],
        )
        self.assertEqual(
            results[1]["sameWorldHandoff"]["sameWorldReferenceStateDigest"],
            results[1]["postState"]["stateDigest"],
        )

    def test_sequence_rejects_reordered_or_missing_submission_transition(self) -> None:
        first_transition = _first_transition(self.base)
        metadata = {
            "transactionId": TX_A,
            "ordinal": 1,
            "acceptedClaims": _accepted_claim("claim-a"),
            "judgmentId": JUDGMENT_A,
        }
        with self.assertRaisesRegex(MathFlowError, "one transition per accepted"):
            apply_research_builder_v6_sequence(
                self.base, [], accepted_submissions=[metadata]
            )
        reversed_metadata = [
            metadata,
            {
                "transactionId": TX_B,
                "ordinal": 0,
                "acceptedClaims": _accepted_claim("claim-b"),
                "judgmentId": JUDGMENT_B,
            },
        ]
        with self.assertRaisesRegex(MathFlowError, "canonical order"):
            apply_research_builder_v6_sequence(
                self.base,
                [first_transition, {**first_transition, "subjectTransactionId": TX_B}],
                accepted_submissions=reversed_metadata,
            )

    def test_topology_revision_fixture_splits_and_moves_stable_item(self) -> None:
        fixture = json.loads(
            (FIXTURES / "research_builder_v6_topology_revision.json").read_text(
                encoding="utf-8"
            )
        )
        first = self._first_result()
        base = first["postState"]
        predecessor_id = fixture["predecessorProgramId"]
        left_id, right_id = fixture["successorProgramIds"]
        trigger = fixture["triggerTransactionId"]
        predecessor = base["programs"][predecessor_id]
        predecessor_thread = base["threads"]["program-a/unstructured"]
        moved_item = base["items"][fixture["movedItemId"]]

        def topology_operation(
            action: str,
            kind: str,
            entity_id: str,
            value: dict[str, object],
            base_digest: str | None,
        ) -> dict[str, object]:
            return {
                "action": action,
                "entityKind": kind,
                "entityId": entity_id,
                "baseDigest": base_digest,
                "value": value,
            }

        topology_operations = [
            topology_operation(
                "create",
                "thread",
                "root/program-a-left-line",
                _thread(
                    "root/program-a-left-line", "root", [trigger], kind="research"
                ),
                None,
            ),
            topology_operation(
                "create",
                "thread",
                "root/program-a-right-line",
                _thread(
                    "root/program-a-right-line", "root", [trigger], kind="research"
                ),
                None,
            ),
            topology_operation(
                "create",
                "program",
                left_id,
                _program(
                    left_id,
                    "root",
                    ["root/program-a-left-line"],
                    [trigger],
                    lineage=[{"relation": "split-from", "programId": predecessor_id}],
                ),
                None,
            ),
            topology_operation(
                "create",
                "program",
                right_id,
                _program(
                    right_id,
                    "root",
                    ["root/program-a-right-line"],
                    [trigger],
                    lineage=[{"relation": "split-from", "programId": predecessor_id}],
                ),
                None,
            ),
            topology_operation(
                "create",
                "thread",
                f"{left_id}/unstructured",
                _thread(f"{left_id}/unstructured", left_id, [trigger]),
                None,
            ),
            topology_operation(
                "create",
                "thread",
                f"{right_id}/unstructured",
                _thread(f"{right_id}/unstructured", right_id, [trigger]),
                None,
            ),
            topology_operation(
                "move",
                "item",
                fixture["movedItemId"],
                {
                    **_without_digest(moved_item),
                    "programId": left_id,
                },
                moved_item["digest"],
            ),
            topology_operation(
                "retire",
                "thread",
                "program-a/unstructured",
                {
                    **_without_digest(predecessor_thread),
                    "status": "retired",
                    "expectedExposure": "0",
                },
                predecessor_thread["digest"],
            ),
            topology_operation(
                "retire",
                "program",
                predecessor_id,
                {
                    **_without_digest(predecessor),
                    "status": "retired",
                    "lineage": [
                        {"relation": "split-into", "programId": left_id},
                        {"relation": "split-into", "programId": right_id},
                    ],
                },
                predecessor["digest"],
            ),
        ]
        transition = _transition(
            base,
            trigger,
            "claim-c",
            program_id="root",
            thread_id="root/unstructured-search",
            item_id="root/result-c",
            content_operations=[
                _content_operation(
                    "item",
                    "root/result-c",
                    _item("root/result-c", "root", trigger, "claim-c"),
                )
            ],
            topology_operations=topology_operations,
            placement_basis="canonical-objective",
            related_program_ids=[],
        )
        result = apply_research_builder_v6_transition(
            base,
            transition,
            accepted_claims=_accepted_claim("claim-c"),
            judgment_id=JUDGMENT_C,
        )
        post = result["postState"]
        alignment = result["topologyAlignment"]
        self.assertEqual(post["items"][fixture["movedItemId"]]["programId"], left_id)
        self.assertEqual(post["programs"][predecessor_id]["status"], "retired")
        self.assertEqual(
            alignment["splits"],
            [
                {
                    "predecessorProgramId": predecessor_id,
                    "successorProgramIds": [left_id, right_id],
                }
            ],
        )
        self.assertIn(
            fixture["movedItemId"],
            [entry["entityId"] for entry in alignment["moved"]],
        )
        self.assertEqual(
            result["sameWorldHandoff"]["accountingNodeKinds"],
            fixture["expectedAccountingNodeKinds"],
        )
        self.assertEqual(
            result["sameWorldHandoff"]["semanticLeafKinds"],
            fixture["expectedSemanticLeafKinds"],
        )

    def test_transition_rejects_model_supplied_alignment_and_stale_base(self) -> None:
        transition = _first_transition(self.base)
        with self.assertRaisesRegex(MathFlowError, "invalid envelope"):
            apply_research_builder_v6_transition(
                self.base,
                {**transition, "topologyAlignment": {}},
                accepted_claims=_accepted_claim("claim-a"),
                judgment_id=JUDGMENT_A,
            )
        stale = {**transition, "baseStateDigest": "sha256:" + "0" * 64}
        with self.assertRaisesRegex(MathFlowError, "stale base"):
            apply_research_builder_v6_transition(
                self.base,
                stale,
                accepted_claims=_accepted_claim("claim-a"),
                judgment_id=JUDGMENT_A,
            )

    def test_content_operation_cannot_hide_a_move(self) -> None:
        first = self._first_result()
        base = first["postState"]
        moved_item = base["items"]["program-a/result-a"]
        transition = _transition(
            base,
            TX_B,
            "claim-b",
            program_id="program-a",
            thread_id="program-a/unstructured",
            item_id="program-a/result-b",
            content_operations=[
                _content_operation(
                    "item",
                    "program-a/result-a",
                    {
                        **_without_digest(moved_item),
                        "programId": "root",
                        "sourceTransactionIds": [TX_A, TX_B],
                    },
                    moved_item["digest"],
                ),
                _content_operation(
                    "item",
                    "program-a/result-b",
                    _item("program-a/result-b", "program-a", TX_B, "claim-b"),
                ),
            ],
        )
        with self.assertRaisesRegex(MathFlowError, "hides a topology"):
            apply_research_builder_v6_transition(
                base,
                transition,
                accepted_claims=_accepted_claim("claim-b"),
                judgment_id=JUDGMENT_B,
            )

    def test_new_contribution_must_be_coherently_placed_before_topology(self) -> None:
        transition = _first_transition(self.base)
        transition["contentOperations"][-1]["value"]["programId"] = "root"
        with self.assertRaisesRegex(MathFlowError, "outside its initial program"):
            apply_research_builder_v6_transition(
                self.base,
                transition,
                accepted_claims=_accepted_claim("claim-a"),
                judgment_id=JUDGMENT_A,
            )

    def test_topology_operations_cannot_create_unjudged_semantic_items(self) -> None:
        transition = _first_transition(self.base)
        transition["topologyOperations"] = [
            {
                "action": "create",
                "entityKind": "item",
                "entityId": "root/extra-item",
                "baseDigest": None,
                "value": _item("root/extra-item", "root", TX_A, "claim-a"),
            }
        ]
        transition["topologyRationale"] = "Create an extra semantic node."
        with self.assertRaisesRegex(MathFlowError, "accepted content, not topology"):
            apply_research_builder_v6_transition(
                self.base,
                transition,
                accepted_claims=_accepted_claim("claim-a"),
                judgment_id=JUDGMENT_A,
            )

    def test_same_world_handoff_rejects_tampering(self) -> None:
        result = self._first_result()
        tampered = {
            **result["sameWorldHandoff"],
            "sameWorldReferenceStateDigest": self.base["stateDigest"],
        }
        with self.assertRaisesRegex(MathFlowError, "deterministic same-world"):
            validate_research_builder_v6_handoff(
                tampered,
                self.base,
                result["postState"],
                result["topologyAlignment"],
                TX_A,
            )

    def test_missing_dependency_is_rejected_before_formation(self) -> None:
        transition = _first_transition(self.base)
        with self.assertRaisesRegex(MathFlowError, "dependency is absent"):
            apply_research_builder_v6_transition(
                self.base,
                transition,
                accepted_claims=_accepted_claim("claim-a", [TX_B]),
                judgment_id=JUDGMENT_A,
            )


if __name__ == "__main__":
    unittest.main()
