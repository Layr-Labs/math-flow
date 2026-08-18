from __future__ import annotations

import copy
import unittest

from math_flow.errors import MathFlowError
from math_flow.research_state import (
    apply_research_program_delta,
    empty_research_program_state,
    materialize_credit_evaluations,
    validate_hierarchical_credit_state,
    validate_research_program_state,
)


TX1 = "a" * 40
TX2 = "b" * 40
JUDGMENT = "sha256:" + "c" * 64


def claim(transaction_id: str, key: str, dependencies: list[str] | None = None):
    return {
        "claimKey": key,
        "statement": f"Statement for {key}",
        "dependencyTransactionIds": dependencies or [],
    }


def first_delta() -> dict[str, object]:
    return {
        "schemaVersion": 1,
        "operations": [
            {
                "entityKind": "thread",
                "entityId": "root/direct-line",
                "baseDigest": None,
                "value": {
                    "id": "root/direct-line",
                    "programId": "root",
                    "title": "Direct line",
                    "summary": "Develop the accepted bound.",
                    "kind": "research",
                    "status": "active",
                    "expectedExposure": "4",
                    "conditions": [],
                    "sourceTransactionIds": [TX1],
                },
            },
            {
                "entityKind": "item",
                "entityId": "root/result-one",
                "baseDigest": None,
                "value": {
                    "id": "root/result-one",
                    "programId": "root",
                    "type": "result",
                    "title": "First result",
                    "summary": "The accepted mathematical conclusion.",
                    "claimRefs": [{"transactionId": TX1, "claimKey": "main"}],
                    "sourceTransactionIds": [TX1],
                    "dependencyItemIds": [],
                },
            },
            {
                "entityKind": "item",
                "entityId": "root/proof-one",
                "baseDigest": None,
                "value": {
                    "id": "root/proof-one",
                    "programId": "root",
                    "type": "proof",
                    "title": "First proof",
                    "summary": "The reusable proof mechanism.",
                    "claimRefs": [],
                    "sourceTransactionIds": [TX1],
                    "dependencyItemIds": ["root/result-one"],
                },
            },
        ],
        "contribution": {
            "claimKeys": ["main"],
            "directProgramId": "root",
            "directThreadIds": ["root/direct-line"],
            "itemIds": ["root/result-one", "root/proof-one"],
        },
    }


def first_credit() -> dict[str, object]:
    return {
        "schemaVersion": 1,
        "evaluations": [
            {
                "programId": "root",
                "unattributedWork": "0.5",
                "rationale": "A small residual remains uncertain.",
                "children": [
                    {
                        "kind": "contribution",
                        "id": TX1,
                        "counterfactual": "Remove the result and its descendants.",
                        "directEffects": [
                            {
                                "threadId": "root/direct-line",
                                "withoutWork": "3",
                                "withWork": "0",
                                "rationale": "The contribution completes this line.",
                            }
                        ],
                        "obviatedEffects": [
                            {
                                "threadId": "root/unstructured-search",
                                "withoutWork": "1",
                                "withWork": "0.5",
                                "rationale": "Less undirected search is needed.",
                            }
                        ],
                        "confidence": "high",
                        "evidenceRefs": [TX1],
                    }
                ],
            }
        ],
    }


class ResearchStateTests(unittest.TestCase):
    def test_atomic_program_update_and_hierarchical_credit(self) -> None:
        base = empty_research_program_state("demo")
        post = apply_research_program_delta(
            base,
            first_delta(),
            ledger_head=TX1,
            subject_transaction_id=TX1,
            accepted_claims=[claim(TX1, "main")],
            judgment_id=JUDGMENT,
        )
        validate_research_program_state(post, "demo")
        self.assertEqual(post["contributions"][TX1]["claimKeys"], ["main"])
        self.assertEqual(
            post["contributions"][TX1]["itemIds"],
            ["root/result-one", "root/proof-one"],
        )

        credit = materialize_credit_evaluations(
            prior_credit_state=None,
            base_program_state=base,
            post_program_state=post,
            horizon_program_state=post,
            subject_transaction_id=TX1,
            raw_delta=first_credit(),
        )
        validate_hierarchical_credit_state(credit, "demo")
        child = credit["evaluations"]["root"]["children"][0]
        self.assertEqual(child["directWork"], "3")
        self.assertEqual(child["obviatedWork"], "0.5")
        self.assertEqual(child["totalWork"], "3.5")
        self.assertEqual(
            credit["allocations"][TX1],
            {"numerator": "3.5", "denominator": "4"},
        )

    def test_bad_news_does_not_turn_matched_credit_negative(self) -> None:
        base = empty_research_program_state("demo")
        first = apply_research_program_delta(
            base,
            first_delta(),
            ledger_head=TX1,
            subject_transaction_id=TX1,
            accepted_claims=[claim(TX1, "main")],
            judgment_id=JUDGMENT,
        )
        first_score = materialize_credit_evaluations(
            prior_credit_state=None,
            base_program_state=base,
            post_program_state=first,
            horizon_program_state=first,
            subject_transaction_id=TX1,
            raw_delta=first_credit(),
        )
        direct = first["threads"]["root/direct-line"]
        second_delta = {
            "schemaVersion": 1,
            "operations": [
                {
                    "entityKind": "thread",
                    "entityId": "root/direct-line",
                    "baseDigest": direct["digest"],
                    "value": {
                        **{key: value for key, value in direct.items() if key != "digest"},
                        "summary": "Bad news reveals a harder remaining direct line.",
                        "expectedExposure": "8",
                        "sourceTransactionIds": [TX1, TX2],
                    },
                },
                {
                    "entityKind": "item",
                    "entityId": "root/result-two",
                    "baseDigest": None,
                    "value": {
                        "id": "root/result-two",
                        "programId": "root",
                        "type": "result",
                        "title": "Useful negative result",
                        "summary": "The result rules out one costly version of the line.",
                        "claimRefs": [
                            {"transactionId": TX2, "claimKey": "negative-result"}
                        ],
                        "sourceTransactionIds": [TX2],
                        "dependencyItemIds": ["root/result-one"],
                    },
                },
            ],
            "contribution": {
                "claimKeys": ["negative-result"],
                "directProgramId": "root",
                "directThreadIds": ["root/direct-line"],
                "itemIds": ["root/result-two"],
            },
        }
        second = apply_research_program_delta(
            first,
            second_delta,
            ledger_head=TX2,
            subject_transaction_id=TX2,
            accepted_claims=[claim(TX2, "negative-result", [TX1])],
            judgment_id=JUDGMENT,
        )
        self.assertGreater(
            float(second["threads"]["root/direct-line"]["expectedExposure"]),
            float(first["threads"]["root/direct-line"]["expectedExposure"]),
        )
        second_score = materialize_credit_evaluations(
            prior_credit_state=first_score,
            base_program_state=first,
            post_program_state=second,
            horizon_program_state=second,
            subject_transaction_id=TX2,
            raw_delta={
                "schemaVersion": 1,
                "evaluations": [
                    {
                        "programId": "root",
                        "unattributedWork": "0.5",
                        "rationale": "Retain the same residual estimate.",
                        "children": [
                            {
                                "kind": "contribution",
                                "id": TX2,
                                "counterfactual": "Without the negative result, repeat the ruled-out work.",
                                "directEffects": [
                                    {
                                        "threadId": "root/direct-line",
                                        "withoutWork": "10",
                                        "withWork": "8",
                                        "rationale": "Two units are saved despite harder news.",
                                    }
                                ],
                                "obviatedEffects": [],
                                "confidence": "high",
                                "evidenceRefs": [TX2],
                            }
                        ],
                    }
                ],
            },
        )
        children = second_score["evaluations"]["root"]["children"]
        by_id = {child["id"]: child for child in children}
        self.assertEqual(by_id[TX2]["totalWork"], "2")
        self.assertEqual(by_id[TX1]["horizonLedgerHead"], TX1)

    def test_negative_total_counterfactual_is_rejected(self) -> None:
        base = empty_research_program_state("demo")
        post = apply_research_program_delta(
            base,
            first_delta(),
            ledger_head=TX1,
            subject_transaction_id=TX1,
            accepted_claims=[claim(TX1, "main")],
            judgment_id=JUDGMENT,
        )
        raw = first_credit()
        raw["evaluations"][0]["children"][0]["directEffects"][0]["withoutWork"] = "0"
        raw["evaluations"][0]["children"][0]["directEffects"][0]["withWork"] = "2"
        raw["evaluations"][0]["children"][0]["obviatedEffects"] = []
        with self.assertRaisesRegex(MathFlowError, "negative total work reduction"):
            materialize_credit_evaluations(
                prior_credit_state=None,
                base_program_state=base,
                post_program_state=post,
                horizon_program_state=post,
                subject_transaction_id=TX1,
                raw_delta=raw,
            )

    def test_existing_program_topology_is_immutable(self) -> None:
        base = empty_research_program_state("demo")
        delta = first_delta()
        root = base["programs"]["root"]
        delta["operations"].append(
            {
                "entityKind": "program",
                "entityId": "root",
                "baseDigest": root["digest"],
                "value": {
                    **{key: value for key, value in root.items() if key != "digest"},
                    "parentThreadIds": ["root/direct-line"],
                    "sourceTransactionIds": [TX1],
                },
            }
        )
        with self.assertRaisesRegex(MathFlowError, "topology or type"):
            apply_research_program_delta(
                base,
                delta,
                ledger_head=TX1,
                subject_transaction_id=TX1,
                accepted_claims=[claim(TX1, "main")],
                judgment_id=JUDGMENT,
            )


if __name__ == "__main__":
    unittest.main()
