from __future__ import annotations

import copy
import random
import unittest
from fractions import Fraction

from math_flow.errors import MathFlowError
from math_flow.repository import sha256_json
from math_flow.research_state import (
    apply_research_program_delta,
    empty_research_program_state,
)
from math_flow.work_accounting import (
    bind_patch_to_state,
    build_work_accounting_state,
    canonical_decimal,
    make_root_contract,
    make_work_accounting_patch,
    materialize_submission_work_value,
    validate_root_contract,
    validate_submission_work_value,
    validate_work_accounting_patch,
    validate_work_accounting_state,
)


TX = "a" * 40
JUDGMENT = "sha256:" + "b" * 64
PROJECTION_SPEC = "sha256:" + "c" * 64


def accepted_knowledge_state() -> dict[str, object]:
    base = empty_research_program_state("demo")
    return apply_research_program_delta(
        base,
        {
            "schemaVersion": 1,
            "operations": [
                {
                    "entityKind": "thread",
                    "entityId": "root/approach-entry",
                    "baseDigest": None,
                    "value": {
                        "id": "root/approach-entry",
                        "programId": "root",
                        "title": "Approach entry",
                        "summary": "The parent-level entry point for the approach.",
                        "kind": "research",
                        "status": "active",
                        "expectedExposure": "1",
                        "conditions": [],
                        "sourceTransactionIds": [TX],
                    },
                },
                {
                    "entityKind": "program",
                    "entityId": "root/approach",
                    "baseDigest": None,
                    "value": {
                        "id": "root/approach",
                        "parentId": "root",
                        "title": "Approach",
                        "objective": "Resolve the approach-specific objective.",
                        "status": "active",
                        "parentThreadIds": ["root/approach-entry"],
                        "sourceTransactionIds": [TX],
                    },
                },
                {
                    "entityKind": "thread",
                    "entityId": "root/approach/unstructured-search",
                    "baseDigest": None,
                    "value": {
                        "id": "root/approach/unstructured-search",
                        "programId": "root/approach",
                        "title": "Unstructured search",
                        "summary": "Work not decomposed inside the approach.",
                        "kind": "unstructured",
                        "status": "active",
                        "expectedExposure": "1",
                        "conditions": [],
                        "sourceTransactionIds": [TX],
                    },
                },
                {
                    "entityKind": "thread",
                    "entityId": "root/approach/direct-line",
                    "baseDigest": None,
                    "value": {
                        "id": "root/approach/direct-line",
                        "programId": "root/approach",
                        "title": "Direct line",
                        "summary": "Complete the accepted contribution's line.",
                        "kind": "research",
                        "status": "active",
                        "expectedExposure": "1",
                        "conditions": [],
                        "sourceTransactionIds": [TX],
                    },
                },
                {
                    "entityKind": "item",
                    "entityId": "root/approach/result",
                    "baseDigest": None,
                    "value": {
                        "id": "root/approach/result",
                        "programId": "root/approach",
                        "type": "result",
                        "title": "Accepted result",
                        "summary": "The accepted mathematical result.",
                        "claimRefs": [{"transactionId": TX, "claimKey": "main"}],
                        "sourceTransactionIds": [TX],
                        "dependencyItemIds": [],
                    },
                },
            ],
            "contribution": {
                "claimKeys": ["main"],
                "directProgramId": "root/approach",
                "directThreadIds": ["root/approach/direct-line"],
                "itemIds": ["root/approach/result"],
            },
        },
        ledger_head=TX,
        subject_transaction_id=TX,
        accepted_claims=[
            {"claimKey": "main", "statement": "Accepted", "dependencyTransactionIds": []}
        ],
        judgment_id=JUDGMENT,
    )


def contract() -> dict[str, object]:
    return make_root_contract(
        problem_id="demo",
        knowledge_projection_id="openrouter-research-v3",
        knowledge_projection_spec_digest=PROJECTION_SPEC,
        objective="Resolve the demo problem.",
        terminal_condition="A valid proof of the canonical objective is accepted.",
        tool_baseline="Ordinary mathematical references, Python, and standard proof tools as of 2026-08-25.",
        reference_community_description="Researchers whose accepted submissions Math Flow organizes into its knowledge state.",
        researcher_qualification="A researcher qualified for the mathematical work package being estimated.",
    )


def annotations() -> list[dict[str, object]]:
    return [
        {
            "nodeRef": {"kind": "program", "id": "root"},
            "directWorkHours": "1",
            "conditionalIncidence": None,
        },
        {
            "nodeRef": {"kind": "program", "id": "root/approach"},
            "directWorkHours": "2",
            "conditionalIncidence": "0.5",
        },
        {
            "nodeRef": {"kind": "thread", "id": "root/approach-entry"},
            "directWorkHours": "0",
            "conditionalIncidence": "0.5",
        },
        {
            "nodeRef": {"kind": "thread", "id": "root/approach/direct-line"},
            "directWorkHours": "10",
            "conditionalIncidence": "0.8",
        },
        {
            "nodeRef": {"kind": "thread", "id": "root/approach/unstructured-search"},
            "directWorkHours": "3",
            "conditionalIncidence": "1",
        },
        {
            "nodeRef": {"kind": "thread", "id": "root/unstructured-search"},
            "directWorkHours": "5",
            "conditionalIncidence": "1",
        },
    ]


def baseline_state() -> tuple[dict[str, object], dict[str, object], dict[str, object]]:
    knowledge = accepted_knowledge_state()
    root_contract = contract()
    state = build_work_accounting_state(
        root_contract=root_contract,
        knowledge_state=knowledge,
        annotations=annotations(),
    )
    return knowledge, root_contract, state


def patch(
    state: dict[str, object],
    knowledge: dict[str, object],
    root_contract: dict[str, object],
    *,
    mode: str,
    direct_work: str,
) -> dict[str, object]:
    unbound = make_work_accounting_patch(
        problem_id="demo",
        subject_transaction_id=TX,
        evaluation_mode=mode,
        root_contract_digest=str(root_contract["rootContractDigest"]),
        base_accounting_state_digest=str(state["stateDigest"]),
        base_knowledge_state_digest=str(knowledge["stateDigest"]),
        target_knowledge_state_digest=str(knowledge["stateDigest"]),
        topology_alignment_digest=None,
        updates=[
            {
                "nodeRef": {"kind": "thread", "id": "root/approach/direct-line"},
                "changes": {"directWorkHours": direct_work},
                "rationale": f"The {mode} continuation changes residual work.",
                "evidenceRefs": [TX],
            }
        ],
    )
    return bind_patch_to_state(unbound, state)


class WorkAccountingTests(unittest.TestCase):
    def test_exact_propagation_and_accounting_equality(self) -> None:
        knowledge, root_contract, state = baseline_state()
        validate_work_accounting_state(state, knowledge, root_contract)
        self.assertEqual(state["totalWorkHours"], "12.5")
        root = next(
            item
            for item in state["derived"]
            if item["nodeRef"] == {"kind": "program", "id": "root"}
        )
        self.assertEqual(root["globalReach"], "1")
        self.assertEqual(root["conditionalSubtreeWork"], "12.5")
        expected_direct = sum(
            (Fraction(item["expectedDirectWork"]) for item in state["derived"]),
            Fraction(0),
        )
        self.assertEqual(expected_direct, Fraction(state["totalWorkHours"]))

    def test_submission_value_is_one_global_positive_difference(self) -> None:
        knowledge, root_contract, state = baseline_state()
        no_access = patch(
            state, knowledge, root_contract, mode="no-access", direct_work="8"
        )
        with_access = patch(
            state, knowledge, root_contract, mode="with-access", direct_work="3"
        )
        no_state, with_state, evaluation = materialize_submission_work_value(
            base_state=state,
            no_access_patch=no_access,
            with_access_patch=with_access,
            root_contract=root_contract,
            base_knowledge_state=knowledge,
            target_knowledge_state=knowledge,
        )
        self.assertEqual(no_state["totalWorkHours"], "11.7")
        self.assertEqual(with_state["totalWorkHours"], "9.7")
        self.assertEqual(evaluation["workValueHours"], "2")
        self.assertEqual(no_state["processedSubmissionIds"], [])
        self.assertEqual(with_state["processedSubmissionIds"], [TX])
        self.assertEqual(with_state["predecessorStateDigest"], state["stateDigest"])
        self.assertEqual(
            evaluation["affectedNodeRefs"],
            [{"kind": "thread", "id": "root/approach/direct-line"}],
        )
        validate_submission_work_value(evaluation)

    def test_nonpositive_counterfactual_is_rejected_without_clamping(self) -> None:
        knowledge, root_contract, state = baseline_state()
        no_access = patch(
            state, knowledge, root_contract, mode="no-access", direct_work="4"
        )
        with_access = patch(
            state, knowledge, root_contract, mode="with-access", direct_work="6"
        )
        with self.assertRaisesRegex(MathFlowError, "strictly positive"):
            materialize_submission_work_value(
                base_state=state,
                no_access_patch=no_access,
                with_access_patch=with_access,
                root_contract=root_contract,
                base_knowledge_state=knowledge,
                target_knowledge_state=knowledge,
            )

    def test_derived_fields_are_recomputed_and_cannot_be_trusted(self) -> None:
        knowledge, root_contract, state = baseline_state()
        tampered = copy.deepcopy(state)
        tampered["derived"][0]["globalReach"] = "0"
        content = {key: value for key, value in tampered.items() if key != "stateDigest"}
        tampered["stateDigest"] = "sha256:" + sha256_json(content)
        with self.assertRaisesRegex(MathFlowError, "derived fields are inconsistent"):
            validate_work_accounting_state(tampered, knowledge, root_contract)

        invalid_patch = patch(
            state, knowledge, root_contract, mode="no-access", direct_work="8"
        )
        invalid_patch = copy.deepcopy(invalid_patch)
        invalid_patch["updates"][0]["changes"]["globalReach"] = "1"
        content = {
            key: value for key, value in invalid_patch.items() if key != "patchDigest"
        }
        invalid_patch["patchDigest"] = "sha256:" + sha256_json(content)
        with self.assertRaisesRegex(MathFlowError, "primitive fields only"):
            validate_work_accounting_patch(invalid_patch)

    def test_stale_annotation_guard_is_rejected(self) -> None:
        knowledge, root_contract, state = baseline_state()
        delta = patch(
            state, knowledge, root_contract, mode="no-access", direct_work="8"
        )
        delta = copy.deepcopy(delta)
        delta["updates"][0]["baseAnnotationDigest"] = "sha256:" + "d" * 64
        content = {key: value for key, value in delta.items() if key != "patchDigest"}
        delta["patchDigest"] = "sha256:" + sha256_json(content)
        with self.assertRaisesRegex(MathFlowError, "base guard mismatch"):
            from math_flow.work_accounting import apply_work_accounting_patch

            apply_work_accounting_patch(
                state,
                delta,
                root_contract=root_contract,
                base_knowledge_state=knowledge,
                target_knowledge_state=knowledge,
            )

    def test_exact_knowledge_digest_and_node_set_are_mandatory(self) -> None:
        knowledge, root_contract, state = baseline_state()
        another = copy.deepcopy(knowledge)
        another["ledgerHead"] = "f" * 40
        content = {key: value for key, value in another.items() if key != "stateDigest"}
        another["stateDigest"] = "sha256:" + sha256_json(content)
        with self.assertRaisesRegex(MathFlowError, "another knowledge state"):
            validate_work_accounting_state(state, another, root_contract)

        missing = annotations()[:-1]
        with self.assertRaisesRegex(MathFlowError, "every program and thread"):
            build_work_accounting_state(
                root_contract=root_contract,
                knowledge_state=knowledge,
                annotations=missing,
            )

    def test_root_contract_pins_human_hours_and_builder_authority(self) -> None:
        root_contract = contract()
        invalid = copy.deepcopy(root_contract)
        invalid["workUnit"]["id"] = "frontier-llm-hour"
        content = {
            key: value for key, value in invalid.items() if key != "rootContractDigest"
        }
        invalid["rootContractDigest"] = "sha256:" + sha256_json(content)
        with self.assertRaisesRegex(MathFlowError, "competent human researcher hours"):
            validate_root_contract(invalid)

        invalid = copy.deepcopy(root_contract)
        invalid["referenceCommunity"]["portfolioAuthority"] = "credit-model"
        content = {
            key: value for key, value in invalid.items() if key != "rootContractDigest"
        }
        invalid["rootContractDigest"] = "sha256:" + sha256_json(content)
        with self.assertRaisesRegex(MathFlowError, "knowledge builder"):
            validate_root_contract(invalid)

    def test_decimal_normalization_is_exact_and_canonical(self) -> None:
        self.assertEqual(canonical_decimal("1.2300"), "1.23")
        self.assertEqual(canonical_decimal(Fraction(1, 8)), "0.125")
        with self.assertRaises(MathFlowError):
            canonical_decimal("01")
        with self.assertRaisesRegex(MathFlowError, "finite decimal representation"):
            canonical_decimal(Fraction(1, 3))

    def test_property_style_exact_equality_over_many_primitive_assignments(self) -> None:
        knowledge = accepted_knowledge_state()
        root_contract = contract()
        generator = random.Random(20260825)
        refs = [item["nodeRef"] for item in annotations()]
        for _ in range(50):
            values: list[dict[str, object]] = []
            for ref in refs:
                is_root = ref == {"kind": "program", "id": "root"}
                values.append(
                    {
                        "nodeRef": ref,
                        "directWorkHours": canonical_decimal(
                            Fraction(generator.randrange(0, 500), 100)
                        ),
                        "conditionalIncidence": None
                        if is_root
                        else canonical_decimal(
                            Fraction(generator.randrange(0, 101), 100)
                        ),
                    }
                )
            state = build_work_accounting_state(
                root_contract=root_contract,
                knowledge_state=knowledge,
                annotations=values,
            )
            expected = sum(
                (Fraction(item["expectedDirectWork"]) for item in state["derived"]),
                Fraction(0),
            )
            self.assertEqual(expected, Fraction(state["totalWorkHours"]))

    def test_topology_change_requires_exact_builder_alignment(self) -> None:
        base_knowledge = empty_research_program_state("demo")
        target_knowledge = accepted_knowledge_state()
        root_contract = contract()
        base_state = build_work_accounting_state(
            root_contract=root_contract,
            knowledge_state=base_knowledge,
            annotations=[
                {
                    "nodeRef": {"kind": "program", "id": "root"},
                    "directWorkHours": "1",
                    "conditionalIncidence": None,
                },
                {
                    "nodeRef": {"kind": "thread", "id": "root/unstructured-search"},
                    "directWorkHours": "20",
                    "conditionalIncidence": "1",
                },
            ],
        )
        new_refs = [
            ("program", "root/approach", "2", "0.5"),
            ("thread", "root/approach-entry", "0", "0.5"),
            ("thread", "root/approach/direct-line", "8", "0.8"),
            ("thread", "root/approach/unstructured-search", "3", "1"),
        ]
        alignment: dict[str, object] = {
            "schemaVersion": 1,
            "problemId": "demo",
            "beforeKnowledgeStateDigest": base_knowledge["stateDigest"],
            "afterKnowledgeStateDigest": target_knowledge["stateDigest"],
            "preserved": [],
            "moved": [],
            "splits": [],
            "merges": [],
            "created": [],
            "retired": [],
        }
        alignment["alignmentDigest"] = "sha256:" + sha256_json(alignment)
        unbound = make_work_accounting_patch(
            problem_id="demo",
            subject_transaction_id=TX,
            evaluation_mode="no-access",
            root_contract_digest=str(root_contract["rootContractDigest"]),
            base_accounting_state_digest=str(base_state["stateDigest"]),
            base_knowledge_state_digest=str(base_knowledge["stateDigest"]),
            target_knowledge_state_digest=str(target_knowledge["stateDigest"]),
            topology_alignment_digest=str(alignment["alignmentDigest"]),
            updates=[
                {
                    "nodeRef": {"kind": kind, "id": node_id},
                    "changes": {
                        "directWorkHours": direct,
                        "conditionalIncidence": incidence,
                    },
                    "rationale": "Estimate newly explicit work in the no-access world.",
                    "evidenceRefs": [TX],
                }
                for kind, node_id, direct, incidence in new_refs
            ],
        )
        delta = bind_patch_to_state(unbound, base_state)
        from math_flow.work_accounting import apply_work_accounting_patch

        with self.assertRaisesRegex(MathFlowError, "require builder-derived alignment"):
            missing_alignment = copy.deepcopy(delta)
            missing_alignment["topologyAlignmentDigest"] = None
            content = {
                key: value
                for key, value in missing_alignment.items()
                if key != "patchDigest"
            }
            missing_alignment["patchDigest"] = "sha256:" + sha256_json(content)
            apply_work_accounting_patch(
                base_state,
                missing_alignment,
                root_contract=root_contract,
                base_knowledge_state=base_knowledge,
                target_knowledge_state=target_knowledge,
            )
        result = apply_work_accounting_patch(
            base_state,
            delta,
            root_contract=root_contract,
            base_knowledge_state=base_knowledge,
            target_knowledge_state=target_knowledge,
            topology_alignment=alignment,
        )
        self.assertEqual(result["knowledgeStateDigest"], target_knowledge["stateDigest"])
        self.assertEqual(len(result["annotations"]), 6)


if __name__ == "__main__":
    unittest.main()
