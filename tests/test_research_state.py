from __future__ import annotations

import copy
import unittest

from math_flow.errors import MathFlowError
from math_flow.research_state import (
    apply_research_program_delta,
    apply_research_program_batch_delta,
    apply_research_program_batch_delta_v5,
    empty_research_program_state,
    materialize_credit_evaluations,
    validate_hierarchical_credit_state,
    validate_research_program_state,
    validate_research_program_v5_batch_binding,
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
    def test_dependency_connected_submissions_apply_in_one_batch(self) -> None:
        base = empty_research_program_state("demo")
        operations = list(first_delta()["operations"])
        operations.extend(
            [
                {
                    "entityKind": "thread",
                    "entityId": "root/follow-up-line",
                    "baseDigest": None,
                    "value": {
                        "id": "root/follow-up-line",
                        "programId": "root",
                        "title": "Follow-up line",
                        "summary": "Use the first accepted result.",
                        "kind": "research",
                        "status": "active",
                        "expectedExposure": "2",
                        "conditions": [],
                        "sourceTransactionIds": [TX2],
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
                        "title": "Second result",
                        "summary": "A dependent accepted conclusion.",
                        "claimRefs": [
                            {"transactionId": TX2, "claimKey": "follow-up"}
                        ],
                        "sourceTransactionIds": [TX2],
                        "dependencyItemIds": ["root/result-one"],
                    },
                },
            ]
        )
        post = apply_research_program_batch_delta(
            base,
            {
                "schemaVersion": 1,
                "operations": operations,
                "contributions": [
                    {"transactionId": TX1, **first_delta()["contribution"]},
                    {
                        "transactionId": TX2,
                        "claimKeys": ["follow-up"],
                        "directProgramId": "root",
                        "directThreadIds": ["root/follow-up-line"],
                        "itemIds": ["root/result-two"],
                    },
                ],
            },
            ledger_head=TX2,
            accepted_claims_by_transaction={
                TX1: [claim(TX1, "main")],
                TX2: [claim(TX2, "follow-up", [TX1])],
            },
            judgment_ids={TX1: JUDGMENT, TX2: "sha256:" + "d" * 64},
        )
        self.assertEqual(set(post["contributions"]), {TX1, TX2})
        self.assertEqual(
            post["contributions"][TX2]["dependencyTransactionIds"], [TX1]
        )

    def test_batch_rejects_dependency_absent_from_state_and_batch(self) -> None:
        base = empty_research_program_state("demo")
        delta = first_delta()
        with self.assertRaisesRegex(MathFlowError, "absent from research state"):
            apply_research_program_batch_delta(
                base,
                {
                    "schemaVersion": 1,
                    "operations": [
                        {
                            **operation,
                            "value": {
                                **operation["value"],
                                "sourceTransactionIds": [TX2],
                                **(
                                    {
                                        "claimRefs": [
                                            {
                                                "transactionId": TX2,
                                                "claimKey": "follow-up",
                                            }
                                        ]
                                    }
                                    if operation["entityKind"] == "item"
                                    and operation["value"]["type"] == "result"
                                    else {}
                                ),
                            },
                        }
                        for operation in delta["operations"]
                    ],
                    "contributions": [
                        {
                            "transactionId": TX2,
                            **delta["contribution"],
                            "claimKeys": ["follow-up"],
                        }
                    ],
                },
                ledger_head=TX2,
                accepted_claims_by_transaction={
                    TX2: [claim(TX2, "follow-up", [TX1])]
                },
                judgment_ids={TX2: JUDGMENT},
            )

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

    def test_retrospective_reference_rejects_obviation_invented_after_child(self) -> None:
        base = empty_research_program_state("demo")
        delta = first_delta()
        delta["operations"].append(
            {
                "entityKind": "thread",
                "entityId": "root/new-alternative",
                "baseDigest": None,
                "value": {
                    "id": "root/new-alternative",
                    "programId": "root",
                    "title": "New alternative",
                    "summary": "A route first recorded with the contribution.",
                    "kind": "research",
                    "status": "active",
                    "expectedExposure": "2",
                    "conditions": [],
                    "sourceTransactionIds": [TX1],
                },
            }
        )
        post = apply_research_program_delta(
            base,
            delta,
            ledger_head=TX1,
            subject_transaction_id=TX1,
            accepted_claims=[claim(TX1, "main")],
            judgment_id=JUDGMENT,
        )
        raw = first_credit()
        raw["evaluations"][0]["children"][0]["obviatedEffects"] = [
            {
                "threadId": "root/new-alternative",
                "withoutWork": "2",
                "withWork": "0",
                "rationale": "This route did not exist in the historical base.",
            }
        ]
        with self.assertRaisesRegex(MathFlowError, "outside the local program"):
            materialize_credit_evaluations(
                prior_credit_state=None,
                base_program_state=post,
                post_program_state=post,
                horizon_program_state=post,
                subject_transaction_id=None,
                raw_delta=raw,
                target_children_by_program={
                    "root": [{"kind": "contribution", "id": TX1}]
                },
                reference_states_by_child={
                    ("root", "contribution", TX1): (base, post)
                },
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

    def test_v5_root_singleton_is_valid_but_second_root_singleton_is_rejected(
        self,
    ) -> None:
        base = empty_research_program_state("demo")
        first = apply_research_program_batch_delta_v5(
            base,
            {
                "schemaVersion": 2,
                "operations": first_delta()["operations"],
                "contributions": [
                    {"transactionId": TX1, **first_delta()["contribution"]}
                ],
                "placementAudits": [
                    {
                        "transactionId": TX1,
                        "basis": "canonical-objective",
                        "rationale": "This fixture result addresses the canonical objective directly.",
                        "relatedProgramIds": [],
                    }
                ],
            },
            ledger_head=TX1,
            accepted_claims_by_transaction={TX1: [claim(TX1, "main")]},
            judgment_ids={TX1: JUDGMENT},
        )
        self.assertEqual(first["contributions"][TX1]["directProgramId"], "root")

        second_delta = {
            "schemaVersion": 2,
            "operations": [
                {
                    "entityKind": "thread",
                    "entityId": "root/second-global-line",
                    "baseDigest": None,
                    "value": {
                        "id": "root/second-global-line",
                        "programId": "root",
                        "title": "Second global line",
                        "summary": "Track a second accepted global result.",
                        "kind": "research",
                        "status": "active",
                        "expectedExposure": "2",
                        "conditions": [],
                        "sourceTransactionIds": [TX2],
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
                        "title": "Second result",
                        "summary": "The second accepted mathematical conclusion.",
                        "claimRefs": [
                            {"transactionId": TX2, "claimKey": "second"}
                        ],
                        "sourceTransactionIds": [TX2],
                        "dependencyItemIds": [],
                    },
                },
            ],
            "contributions": [
                {
                    "transactionId": TX2,
                    "claimKeys": ["second"],
                    "directProgramId": "root",
                    "directThreadIds": ["root/second-global-line"],
                    "itemIds": ["root/result-two"],
                }
            ],
            "placementAudits": [
                {
                    "transactionId": TX2,
                    "basis": "canonical-objective",
                    "rationale": "This fixture also claims direct canonical scope.",
                    "relatedProgramIds": [],
                }
            ],
        }
        with self.assertRaisesRegex(MathFlowError, "may not remain root-only"):
            apply_research_program_batch_delta_v5(
                first,
                second_delta,
                ledger_head=TX2,
                accepted_claims_by_transaction={TX2: [claim(TX2, "second")]},
                judgment_ids={TX2: "sha256:" + "d" * 64},
            )

    def test_v5_local_placement_rejects_a_retired_direct_program(self) -> None:
        base = empty_research_program_state("demo")
        delta = {
            "schemaVersion": 2,
            "operations": [
                {
                    "entityKind": "thread",
                    "entityId": "root/retired-agenda",
                    "baseDigest": None,
                    "value": {
                        "id": "root/retired-agenda",
                        "programId": "root",
                        "title": "Retired agenda",
                        "summary": "A parent line for the retired program fixture.",
                        "kind": "research",
                        "status": "active",
                        "expectedExposure": "1",
                        "conditions": [],
                        "sourceTransactionIds": [TX1],
                    },
                },
                {
                    "entityKind": "program",
                    "entityId": "program/retired",
                    "baseDigest": None,
                    "value": {
                        "id": "program/retired",
                        "parentId": "root",
                        "title": "Retired program",
                        "objective": "Exercise local placement lifecycle validation.",
                        "status": "retired",
                        "parentThreadIds": ["root/retired-agenda"],
                        "sourceTransactionIds": [TX1],
                    },
                },
                {
                    "entityKind": "thread",
                    "entityId": "program/retired/direct",
                    "baseDigest": None,
                    "value": {
                        "id": "program/retired/direct",
                        "programId": "program/retired",
                        "title": "Retired direct line",
                        "summary": "A direct line under a retired program.",
                        "kind": "research",
                        "status": "active",
                        "expectedExposure": "1",
                        "conditions": [],
                        "sourceTransactionIds": [TX1],
                    },
                },
                {
                    "entityKind": "item",
                    "entityId": "program/retired/result",
                    "baseDigest": None,
                    "value": {
                        "id": "program/retired/result",
                        "programId": "program/retired",
                        "type": "result",
                        "title": "Retired-program result",
                        "summary": "An accepted fixture result.",
                        "claimRefs": [
                            {"transactionId": TX1, "claimKey": "main"}
                        ],
                        "sourceTransactionIds": [TX1],
                        "dependencyItemIds": [],
                    },
                },
            ],
            "contributions": [
                {
                    "transactionId": TX1,
                    "claimKeys": ["main"],
                    "directProgramId": "program/retired",
                    "directThreadIds": ["program/retired/direct"],
                    "itemIds": ["program/retired/result"],
                }
            ],
            "placementAudits": [
                {
                    "transactionId": TX1,
                    "basis": "local-objective",
                    "rationale": "Deliberately name a retired local program.",
                    "relatedProgramIds": ["program/retired"],
                }
            ],
        }
        with self.assertRaisesRegex(MathFlowError, "active non-root program"):
            apply_research_program_batch_delta_v5(
                base,
                delta,
                ledger_head=TX1,
                accepted_claims_by_transaction={TX1: [claim(TX1, "main")]},
                judgment_ids={TX1: JUDGMENT},
            )

    def test_v5_batch_binding_treats_claim_keys_as_an_unordered_set(self) -> None:
        base = empty_research_program_state("demo")
        operations = copy.deepcopy(first_delta()["operations"])
        operations.append(
            {
                "entityKind": "item",
                "entityId": "root/result-auxiliary",
                "baseDigest": None,
                "value": {
                    "id": "root/result-auxiliary",
                    "programId": "root",
                    "type": "result",
                    "title": "Auxiliary result",
                    "summary": "Represent the second accepted fixture claim.",
                    "claimRefs": [
                        {"transactionId": TX1, "claimKey": "auxiliary"}
                    ],
                    "sourceTransactionIds": [TX1],
                    "dependencyItemIds": [],
                },
            }
        )
        delta = {
            "schemaVersion": 2,
            "operations": operations,
            "contributions": [
                {
                    "transactionId": TX1,
                    "claimKeys": ["auxiliary", "main"],
                    "directProgramId": "root",
                    "directThreadIds": ["root/direct-line"],
                    "itemIds": [
                        "root/result-one",
                        "root/proof-one",
                        "root/result-auxiliary",
                    ],
                }
            ],
            "placementAudits": [
                {
                    "transactionId": TX1,
                    "basis": "canonical-objective",
                    "rationale": "The two-claim fixture addresses the canonical objective.",
                    "relatedProgramIds": [],
                }
            ],
        }
        post = apply_research_program_batch_delta_v5(
            base,
            delta,
            ledger_head=TX1,
            accepted_claims_by_transaction={
                TX1: [claim(TX1, "main"), claim(TX1, "auxiliary")]
            },
            judgment_ids={TX1: JUDGMENT},
        )
        validate_research_program_v5_batch_binding(
            {
                "schemaVersion": 3,
                "problemId": "demo",
                "baseProgramStateDigest": base["stateDigest"],
                "judgments": [
                    {
                        "judgmentId": JUDGMENT,
                        "runDigest": "sha256:" + "e" * 64,
                        "subjectTransactionId": TX1,
                        "acceptedClaimKeys": ["main", "auxiliary"],
                        "excludedAssessments": [],
                    }
                ],
            },
            delta,
            post,
            "demo",
        )

    def test_v5_excluded_only_batch_binding_requires_the_exact_empty_delta(
        self,
    ) -> None:
        state = empty_research_program_state("demo")
        root_program = state["programs"]["root"]
        with self.assertRaisesRegex(MathFlowError, "empty delta"):
            validate_research_program_v5_batch_binding(
                {
                    "schemaVersion": 3,
                    "problemId": "demo",
                    "baseProgramStateDigest": state["stateDigest"],
                    "judgments": [
                        {
                            "judgmentId": JUDGMENT,
                            "runDigest": "sha256:" + "e" * 64,
                            "subjectTransactionId": TX1,
                            "acceptedClaimKeys": [],
                            "excludedAssessments": [],
                        }
                    ],
                },
                {
                    "schemaVersion": 2,
                    "operations": [
                        {
                            "entityKind": "program",
                            "entityId": "root",
                            "baseDigest": root_program["digest"],
                            "value": {
                                key: value
                                for key, value in root_program.items()
                                if key != "digest"
                            },
                        }
                    ],
                    "contributions": [],
                    "placementAudits": [],
                },
                state,
                "demo",
            )


if __name__ == "__main__":
    unittest.main()
