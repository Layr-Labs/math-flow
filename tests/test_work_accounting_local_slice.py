from __future__ import annotations

import copy
import json
import unittest
from fractions import Fraction
from pathlib import Path

from math_flow.counterfactual_context import build_impact_subgraph_context
from math_flow.errors import MathFlowError
from math_flow.repository import sha256_json
from math_flow.work_accounting import (
    bind_patch_to_state,
    canonical_decimal,
    make_work_accounting_patch,
)
from math_flow.work_accounting_local_slice import (
    _target_topology_subtree,
    apply_local_accounting_slice_patch,
    build_local_accounting_slice,
    materialize_local_slice_submission_work_value,
    reduce_local_accounting_slice,
)
from math_flow.work_accounting_local_slice_probe import (
    SCENARIOS,
    _build_fixture,
    _make_patch,
    build_local_slice_probe_case,
    run_local_slice_probe,
)
from math_flow.work_accounting_scale import SUBJECT, WorkAccountingScaleConfig


SMALL = WorkAccountingScaleConfig(16, 24, 3, 4)
REPORT = (
    Path(__file__).resolve().parents[1]
    / "protocol/experiments/work-accounting-local-slice-v1/provider-free-report.json"
)


def _digest(value: dict[str, object], field: str) -> str:
    return "sha256:" + sha256_json(
        {key: item for key, item in value.items() if key != field}
    )


def _objects(scenario: str = "direct") -> dict[str, object]:
    fixture = _build_fixture(SMALL, scenario)
    common = {
        "base_state": fixture["base"],
        "root_contract": fixture["contract"],
        "base_knowledge_state": fixture["before"],
        "target_knowledge_state": fixture["after"],
        "topology_alignment": fixture["alignment"],
        "impact_context": fixture["impact"],
    }
    with_slice = build_local_accounting_slice(
        **common, evaluation_mode="with-access"
    )
    no_slice = build_local_accounting_slice(**common, evaluation_mode="no-access")
    return {
        "fixture": fixture,
        "common": common,
        "withSlice": with_slice,
        "noSlice": no_slice,
        "withPatch": _make_patch(fixture, with_slice, mode="with-access"),
        "noPatch": _make_patch(fixture, no_slice, mode="no-access"),
    }


def _raw_updates(patch: dict[str, object]) -> list[dict[str, object]]:
    return [
        {
            "nodeRef": copy.deepcopy(item["nodeRef"]),
            "changes": copy.deepcopy(item["changes"]),
            "rationale": item["rationale"],
            "evidenceRefs": copy.deepcopy(item["evidenceRefs"]),
        }
        for item in patch["updates"]
    ]


def _annotation_by_id(state: dict[str, object]) -> dict[str, dict[str, object]]:
    return {
        str(item["nodeRef"]["id"]): item
        for item in state["annotations"]
        if isinstance(item, dict) and isinstance(item.get("nodeRef"), dict)
    }


def _patch_with_extra(
    objects: dict[str, object], node_id: str
) -> dict[str, object]:
    fixture = objects["fixture"]
    original = objects["withPatch"]
    updates = _raw_updates(original)
    updates.append(
        {
            "nodeRef": {"kind": "program", "id": node_id},
            "changes": {"directWorkHours": "99"},
            "rationale": "Adversarial update outside the exact local cut.",
            "evidenceRefs": ["synthetic:adversarial"],
        }
    )
    patch = make_work_accounting_patch(
        problem_id=str(original["problemId"]),
        subject_transaction_id=str(original["subjectTransactionId"]),
        evaluation_mode=str(original["evaluationMode"]),
        root_contract_digest=str(original["rootContractDigest"]),
        base_accounting_state_digest=str(original["baseAccountingStateDigest"]),
        base_knowledge_state_digest=str(original["baseKnowledgeStateDigest"]),
        target_knowledge_state_digest=str(original["targetKnowledgeStateDigest"]),
        topology_alignment_digest=str(original["topologyAlignmentDigest"]),
        updates=updates,
    )
    return bind_patch_to_state(patch, fixture["base"])


class WorkAccountingLocalSliceTests(unittest.TestCase):
    def test_representative_cases_are_exact_full_state_replays(self) -> None:
        for scenario in SCENARIOS:
            with self.subTest(scenario=scenario):
                result = build_local_slice_probe_case(SMALL, scenario)
                self.assertEqual(result["classification"], "bounded-exact-equivalence")
                self.assertEqual(
                    result["equivalence"],
                    {
                        "attempted": True,
                        "globalNoAccessStateExact": True,
                        "globalWithAccessStateExact": True,
                        "evaluationExact": True,
                    },
                )
                self.assertGreater(Fraction(result["fullStateOracle"]["workValueHours"]), 0)

    def test_local_materializer_returns_exact_w_minus_w_plus_and_evaluation(self) -> None:
        objects = _objects("subtree")
        no_state, with_state, evaluation = materialize_local_slice_submission_work_value(
            **objects["common"],
            no_access_patch=objects["noPatch"],
            with_access_patch=objects["withPatch"],
            no_access_slice=objects["noSlice"],
            with_access_slice=objects["withSlice"],
        )
        self.assertEqual(
            Fraction(no_state["totalWorkHours"])
            - Fraction(with_state["totalWorkHours"]),
            Fraction(evaluation["workValueHours"]),
        )

    def test_rehashed_stale_slice_is_rejected_against_trusted_global_state(self) -> None:
        objects = _objects()
        stale = copy.deepcopy(objects["withSlice"])
        stale["baseAccountingStateDigest"] = "sha256:" + "0" * 64
        stale["sliceDigest"] = _digest(stale, "sliceDigest")
        with self.assertRaisesRegex(MathFlowError, "stale|tampered"):
            apply_local_accounting_slice_patch(
                **objects["common"], patch=objects["withPatch"], local_slice=stale
            )

    def test_topology_required_node_missing_from_context_fails_before_reduction(self) -> None:
        objects = _objects("topology-alignment")
        fixture = objects["fixture"]
        original = fixture["impact"]
        root_only = build_impact_subgraph_context(
            problem_id="synthetic-builder-scale",
            subject_transaction_id=SUBJECT,
            accepted_claim_refs=original["acceptedClaimRefs"],
            research_state=fixture["after"],
            seed_node_refs=[{"kind": "program", "id": "root"}],
            descendant_depth=0,
        )
        with self.assertRaisesRegex(MathFlowError, "omits topology-required nodes"):
            build_local_accounting_slice(
                base_state=fixture["base"],
                root_contract=fixture["contract"],
                base_knowledge_state=fixture["before"],
                target_knowledge_state=fixture["after"],
                topology_alignment=fixture["alignment"],
                impact_context=root_only,
                evaluation_mode="with-access",
            )

    def test_topology_change_without_alignment_fails_closed(self) -> None:
        objects = _objects("topology-alignment")
        fixture = objects["fixture"]
        with self.assertRaisesRegex(MathFlowError, "requires exact alignment"):
            build_local_accounting_slice(
                base_state=fixture["base"],
                root_contract=fixture["contract"],
                base_knowledge_state=fixture["before"],
                target_knowledge_state=fixture["after"],
                topology_alignment=None,
                impact_context=fixture["impact"],
                evaluation_mode="with-access",
            )

    def test_decisive_internal_completion_cannot_hide_required_descendants(self) -> None:
        objects = _objects("completed-node")
        fixture = objects["fixture"]
        original = fixture["impact"]
        internal_id = fixture["seedIds"][0]
        collapsed = build_impact_subgraph_context(
            problem_id="synthetic-builder-scale",
            subject_transaction_id=SUBJECT,
            accepted_claim_refs=original["acceptedClaimRefs"],
            research_state=fixture["after"],
            seed_node_refs=[{"kind": "program", "id": internal_id}],
            descendant_depth=0,
        )
        self.assertTrue(collapsed["boundarySummaries"])
        with self.assertRaisesRegex(MathFlowError, "omits topology-required nodes"):
            build_local_accounting_slice(
                base_state=fixture["base"],
                root_contract=fixture["contract"],
                base_knowledge_state=fixture["before"],
                target_knowledge_state=fixture["after"],
                topology_alignment=fixture["alignment"],
                impact_context=collapsed,
                evaluation_mode="with-access",
            )

    def test_two_independent_seed_branches_reduce_exactly(self) -> None:
        configuration = WorkAccountingScaleConfig(64, 64, 4, 4)
        fixture = _build_fixture(configuration, "direct")
        programs = fixture["after"]["programs"]
        children = {program_id: [] for program_id in programs}
        for program_id, record in programs.items():
            parent = record.get("parentId")
            if isinstance(parent, str):
                children[parent].append(program_id)

        def root_branch(program_id: str) -> str:
            cursor = program_id
            while programs[cursor].get("parentId") != "root":
                cursor = programs[cursor]["parentId"]
            return cursor

        leaves_by_branch: dict[str, str] = {}
        for program_id, record in sorted(programs.items()):
            if (
                program_id != "root"
                and record["status"] == "active"
                and not children[program_id]
            ):
                leaves_by_branch.setdefault(root_branch(program_id), program_id)
        self.assertGreaterEqual(len(leaves_by_branch), 2)
        seeds = sorted(leaves_by_branch.values())[:2]
        impact = build_impact_subgraph_context(
            problem_id="synthetic-builder-scale",
            subject_transaction_id=SUBJECT,
            accepted_claim_refs=fixture["impact"]["acceptedClaimRefs"],
            research_state=fixture["after"],
            seed_node_refs=[{"kind": "program", "id": node_id} for node_id in seeds],
            descendant_depth=0,
        )
        common = {
            "base_state": fixture["base"],
            "root_contract": fixture["contract"],
            "base_knowledge_state": fixture["before"],
            "target_knowledge_state": fixture["after"],
            "topology_alignment": fixture["alignment"],
            "impact_context": impact,
        }
        with_slice = build_local_accounting_slice(
            **common, evaluation_mode="with-access"
        )
        no_slice = build_local_accounting_slice(**common, evaluation_mode="no-access")
        annotations = _annotation_by_id(fixture["base"])

        def make(mode: str) -> dict[str, object]:
            updates = []
            for node_id in seeds:
                old = int(str(annotations[node_id]["directWorkHours"]))
                updates.append(
                    {
                        "nodeRef": {"kind": "program", "id": node_id},
                        "changes": {
                            "directWorkHours": str(
                                old - 2 if mode == "with-access" else old + 2
                            )
                        },
                        "rationale": "Two-branch deterministic accounting update.",
                        "evidenceRefs": [f"synthetic:two-branch:{mode}"],
                    }
                )
            unbound = make_work_accounting_patch(
                problem_id="synthetic-builder-scale",
                subject_transaction_id=SUBJECT,
                evaluation_mode=mode,
                root_contract_digest=fixture["contract"]["rootContractDigest"],
                base_accounting_state_digest=fixture["base"]["stateDigest"],
                base_knowledge_state_digest=fixture["before"]["stateDigest"],
                target_knowledge_state_digest=fixture["after"]["stateDigest"],
                topology_alignment_digest=fixture["alignment"]["alignmentDigest"],
                updates=updates,
            )
            return bind_patch_to_state(unbound, fixture["base"])

        no_state, with_state, evaluation = materialize_local_slice_submission_work_value(
            **common,
            no_access_patch=make("no-access"),
            with_access_patch=make("with-access"),
            no_access_slice=no_slice,
            with_access_slice=with_slice,
        )
        self.assertGreater(
            Fraction(no_state["totalWorkHours"]),
            Fraction(with_state["totalWorkHours"]),
        )
        self.assertGreater(Fraction(evaluation["workValueHours"]), 0)

    def test_moved_subtree_may_keep_unchanged_descendants_collapsed(self) -> None:
        fixture = _build_fixture(
            WorkAccountingScaleConfig(64, 64, 3, 8), "topology-alignment"
        )
        moved_id = fixture["alignment"]["moved"][0]["entityId"]
        impact = build_impact_subgraph_context(
            problem_id="synthetic-builder-scale",
            subject_transaction_id=SUBJECT,
            accepted_claim_refs=fixture["impact"]["acceptedClaimRefs"],
            research_state=fixture["after"],
            seed_node_refs=[{"kind": "program", "id": moved_id}],
            descendant_depth=0,
        )
        common = {
            "base_state": fixture["base"],
            "root_contract": fixture["contract"],
            "base_knowledge_state": fixture["before"],
            "target_knowledge_state": fixture["after"],
            "topology_alignment": fixture["alignment"],
            "impact_context": impact,
        }
        with_slice = build_local_accounting_slice(
            **common, evaluation_mode="with-access"
        )
        no_slice = build_local_accounting_slice(**common, evaluation_mode="no-access")
        self.assertTrue(
            any(
                item["parentRef"]["id"] == moved_id
                for item in with_slice["boundaryAggregates"]
            )
        )
        no_state, with_state, evaluation = materialize_local_slice_submission_work_value(
            **common,
            no_access_patch=_make_patch(fixture, no_slice, mode="no-access"),
            with_access_patch=_make_patch(
                fixture, with_slice, mode="with-access"
            ),
            no_access_slice=no_slice,
            with_access_slice=with_slice,
        )
        self.assertGreater(
            Fraction(no_state["totalWorkHours"]),
            Fraction(with_state["totalWorkHours"]),
        )
        self.assertGreater(Fraction(evaluation["workValueHours"]), 0)

    def test_patch_missing_required_primitive_fails_closed(self) -> None:
        objects = _objects("topology-alignment")
        patch = copy.deepcopy(objects["withPatch"])
        required_id = objects["withSlice"]["requiredPrimitiveUpdates"][0][
            "nodeRef"
        ]["id"]
        update = next(
            item for item in patch["updates"] if item["nodeRef"]["id"] == required_id
        )
        update["changes"].pop("conditionalIncidence")
        patch["patchDigest"] = _digest(patch, "patchDigest")
        with self.assertRaisesRegex(MathFlowError, "omits a topology-required"):
            apply_local_accounting_slice_patch(
                **objects["common"], patch=patch, local_slice=objects["withSlice"]
            )

    def test_known_boundary_and_unknown_program_updates_are_out_of_scope(self) -> None:
        objects = _objects()
        boundary_id = objects["withSlice"]["boundaryAggregates"][0]["nodeRef"]["id"]
        for node_id in (boundary_id, "unknown/program"):
            with self.subTest(node_id=node_id):
                patch = _patch_with_extra(objects, node_id)
                with self.assertRaisesRegex(MathFlowError, "outside its exact write scope"):
                    apply_local_accounting_slice_patch(
                        **objects["common"],
                        patch=patch,
                        local_slice=objects["withSlice"],
                    )

    def test_duplicate_patch_id_is_rejected_even_with_recomputed_digest(self) -> None:
        objects = _objects()
        patch = copy.deepcopy(objects["withPatch"])
        patch["updates"].append(copy.deepcopy(patch["updates"][0]))
        patch["updates"].sort(key=lambda item: item["nodeRef"]["id"])
        patch["patchDigest"] = _digest(patch, "patchDigest")
        with self.assertRaisesRegex(MathFlowError, "unique and canonically ordered"):
            apply_local_accounting_slice_patch(
                **objects["common"], patch=patch, local_slice=objects["withSlice"]
            )

    def test_boundary_tampering_fails_even_when_all_local_digests_are_recomputed(self) -> None:
        objects = _objects()
        tampered = copy.deepcopy(objects["withSlice"])
        boundary = tampered["boundaryAggregates"][0]
        boundary["conditionalSubtreeWorkHours"] = canonical_decimal(
            Fraction(boundary["conditionalSubtreeWorkHours"]) + 1
        )
        boundary["conditionalContributionWorkHours"] = canonical_decimal(
            Fraction(boundary["conditionalIncidence"])
            * Fraction(boundary["conditionalSubtreeWorkHours"])
        )
        boundary["boundaryDigest"] = _digest(boundary, "boundaryDigest")
        parent_id = boundary["parentRef"]["id"]
        records = [*tampered["exactNodes"], *tampered["ancestorAggregates"]]
        parent = next(item for item in records if item["nodeRef"]["id"] == parent_id)
        parent_boundaries = [
            item
            for item in tampered["boundaryAggregates"]
            if item["parentRef"]["id"] == parent_id
        ]
        parent["collapsedBoundaryContributionWorkHours"] = canonical_decimal(
            sum(
                (
                    Fraction(item["conditionalContributionWorkHours"])
                    for item in parent_boundaries
                ),
                Fraction(0),
            )
        )
        parent["nodeDigest"] = _digest(parent, "nodeDigest")
        tampered["sliceDigest"] = _digest(tampered, "sliceDigest")
        with self.assertRaisesRegex(MathFlowError, "stale|tampered"):
            apply_local_accounting_slice_patch(
                **objects["common"],
                patch=objects["withPatch"],
                local_slice=tampered,
            )

    def test_deep_boundary_and_local_reduction_are_iterative(self) -> None:
        count = 1500
        keys = [("program", f"deep/n{index:04d}") for index in range(count)]
        children = {key: [] for key in keys}
        annotations = {}
        for index, key in enumerate(keys):
            if index + 1 < count:
                children[key].append(keys[index + 1])
            annotations[key] = {
                "directWorkHours": "1",
                "conditionalIncidence": None if index == 0 else "1",
            }
        total, observed_count = _target_topology_subtree(
            keys[0], children=children, annotations=annotations, forbidden=set()
        )
        self.assertEqual(total, count)
        self.assertEqual(observed_count, count)

        records = []
        for index, key in enumerate(keys):
            core = {
                "nodeRef": {"kind": key[0], "id": key[1]},
                "parentRef": (
                    None
                    if index == 0
                    else {"kind": keys[index - 1][0], "id": keys[index - 1][1]}
                ),
                "status": "active",
                "roles": ["seed"] if index == 0 else ["descendant"],
                "targetKnowledgeNodeDigest": "sha256:" + "1" * 64,
                "baseAnnotationDigest": "sha256:" + "2" * 64,
                "directWorkHours": "1",
                "conditionalIncidence": None if index == 0 else "1",
                "includedChildRefs": (
                    []
                    if index + 1 == count
                    else [{"kind": keys[index + 1][0], "id": keys[index + 1][1]}]
                ),
                "boundaryChildRefs": [],
                "collapsedBoundaryContributionWorkHours": "0",
            }
            records.append({**core, "nodeDigest": _digest(core, "nodeDigest")})
        slice_core = {
            "schemaVersion": 1,
            "experimentId": "inactive-provider-free-work-accounting-local-slice-v1",
            "activationStatus": "inactive-provider-free-experiment",
            "problemId": "deep-probe",
            "subjectTransactionId": "a" * 40,
            "evaluationMode": "with-access",
            "rootContractDigest": "sha256:" + "3" * 64,
            "baseAccountingStateDigest": "sha256:" + "4" * 64,
            "baseKnowledgeStateDigest": "sha256:" + "5" * 64,
            "targetKnowledgeStateDigest": "sha256:" + "6" * 64,
            "topologyAlignmentDigest": None,
            "impactContextDigest": "sha256:" + "7" * 64,
            "rootNodeRef": {"kind": keys[0][0], "id": keys[0][1]},
            "limits": {"maxIncludedNodes": count, "maxBoundaryNodes": 0},
            "writeScopeNodeRefs": [
                {"kind": kind, "id": node_id} for kind, node_id in keys
            ],
            "requiredPrimitiveUpdates": [],
            "exactNodes": records,
            "ancestorAggregates": [],
            "boundaryAggregates": [],
        }
        local_slice = {
            **slice_core,
            "sliceDigest": _digest(slice_core, "sliceDigest"),
        }
        patch = make_work_accounting_patch(
            problem_id="deep-probe",
            subject_transaction_id="a" * 40,
            evaluation_mode="with-access",
            root_contract_digest="sha256:" + "3" * 64,
            base_accounting_state_digest="sha256:" + "4" * 64,
            base_knowledge_state_digest="sha256:" + "5" * 64,
            target_knowledge_state_digest="sha256:" + "6" * 64,
            topology_alignment_digest=None,
            updates=[],
        )
        self.assertEqual(reduce_local_accounting_slice(local_slice, patch), str(count))


class WorkAccountingLocalSliceScaleTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.report = run_local_slice_probe()

    def test_scale_probe_reaches_1024_and_never_truncates(self) -> None:
        self.assertEqual(self.report["providerCalls"], 0)
        self.assertFalse(self.report["networkUsed"])
        self.assertTrue(self.report["summary"]["allAttemptedEquivalenceChecksExact"])
        largest = [
            case
            for case in self.report["cases"]
            if case["configuration"]["program_count"] == 1024
        ]
        self.assertEqual({case["scenario"] for case in largest}, set(SCENARIOS))
        by_scenario = {case["scenario"]: case for case in largest}
        for scenario in ("direct", "subtree", "topology-alignment"):
            self.assertEqual(
                by_scenario[scenario]["classification"],
                "bounded-exact-equivalence",
            )
        for scenario in ("dependency", "completed-node", "broad-scope"):
            self.assertEqual(
                by_scenario[scenario]["classification"],
                "requires-explicit-widening",
            )
            self.assertFalse(by_scenario[scenario]["truncated"])
        topology = by_scenario["topology-alignment"]
        self.assertLess(
            topology["localArtifacts"]["withAccessSlice"]["utf8Bytes"],
            topology["fullStateOracle"]["baseAccountingState"]["utf8Bytes"],
        )
        self.assertLess(
            topology["localArtifacts"]["frozenWithAccessSnapshot"]["utf8Bytes"],
            topology["fullStateOracle"]["withAccessState"]["utf8Bytes"],
        )

    def test_checked_in_report_regenerates_exactly(self) -> None:
        checked_in = json.loads(REPORT.read_text(encoding="utf-8"))
        self.assertEqual(self.report, checked_in)


if __name__ == "__main__":
    unittest.main()
