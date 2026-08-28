from __future__ import annotations

import copy
import json
import tempfile
import unittest
from fractions import Fraction
from pathlib import Path
from unittest.mock import patch

from math_flow.errors import MathFlowError
from math_flow.work_accounting import (
    apply_work_accounting_patch,
    bind_patch_to_state,
    build_work_accounting_state,
    make_work_accounting_patch,
    materialize_submission_work_value,
)
from math_flow.work_accounting_projection_store import (
    work_accounting_lane_scope_digest,
)
from math_flow.work_accounting_schedule import (
    apply_work_accounting_publication,
    apply_work_accounting_state_repair,
    materialize_work_accounting_state_repair,
)
from math_flow.work_accounting_viewer import (
    _attach_verified_requests,
    _node_effect_view,
    _patch_view,
    _require_bundle_output_profile,
    build_work_accounting_viewer_projection,
    discover_published_work_accounting_viewer_projections,
)
from math_flow.viewer import export_viewer_catalog
from tests import test_work_accounting_schedule as schedule_tests


class WorkAccountingViewerTests(unittest.TestCase):
    def setUp(self) -> None:
        # Reuse the scheduler's realistic repository fixture without inheriting
        # its test class (which would duplicate the scheduler suite here).
        self.fixture = schedule_tests.WorkAccountingScheduleTests(
            methodName="test_hosted_batch_grouping_is_semantically_invisible"
        )
        self.fixture.setUp()
        self.schedule = self.fixture._schedule()
        (
            self.claim,
            self.evaluation,
            self.committed,
            self.publication,
            self.no_access_patch,
            self.with_access_patch,
        ) = self.fixture._transition_artifacts(self.schedule, self.fixture.baseline)
        self.schedule = apply_work_accounting_publication(
            self.schedule,
            self.claim,
            self.publication,
            evaluation=self.evaluation,
            no_access_patch=self.no_access_patch,
            with_access_patch=self.with_access_patch,
            predecessor_accounting_state=self.fixture.baseline,
            committed_accounting_state=self.committed,
            predecessor_knowledge_state=self.fixture.knowledge,
            target_knowledge_state=self.fixture.knowledge,
            root_contract=self.fixture.contract,
        )
        first_no_access = apply_work_accounting_patch(
            self.fixture.baseline,
            self.no_access_patch,
            root_contract=self.fixture.contract,
            base_knowledge_state=self.fixture.knowledge,
            target_knowledge_state=self.fixture.knowledge,
        )
        first_loaded = {
            "manifest": {
                "problemId": "demo",
                "subjectTransactionId": self.evaluation["subjectTransactionId"],
            },
            "rootContract": self.fixture.contract,
            "baseKnowledgeState": self.fixture.knowledge,
            "targetKnowledgeState": self.fixture.knowledge,
            "baseAccountingState": self.fixture.baseline,
            "noAccessPatch": self.no_access_patch,
            "withAccessPatch": self.with_access_patch,
            "noAccessRequest": {"requiredPrimitiveUpdates": []},
            "withAccessRequest": {"requiredPrimitiveUpdates": []},
            "noAccessState": first_no_access,
            "withAccessState": self.committed,
            "evaluation": self.evaluation,
        }
        (
            second_claim,
            second_evaluation,
            second_committed,
            second_publication,
            second_no_access_patch,
            second_with_access_patch,
        ) = self.fixture._transition_artifacts(self.schedule, self.committed)
        self.schedule = apply_work_accounting_publication(
            self.schedule,
            second_claim,
            second_publication,
            evaluation=second_evaluation,
            no_access_patch=second_no_access_patch,
            with_access_patch=second_with_access_patch,
            predecessor_accounting_state=self.committed,
            committed_accounting_state=second_committed,
            predecessor_knowledge_state=self.fixture.knowledge,
            target_knowledge_state=self.fixture.knowledge,
            root_contract=self.fixture.contract,
        )
        second_no_access = apply_work_accounting_patch(
            self.committed,
            second_no_access_patch,
            root_contract=self.fixture.contract,
            base_knowledge_state=self.fixture.knowledge,
            target_knowledge_state=self.fixture.knowledge,
        )
        second_loaded = {
            "manifest": {
                "problemId": "demo",
                "subjectTransactionId": second_evaluation["subjectTransactionId"],
            },
            "rootContract": self.fixture.contract,
            "baseKnowledgeState": self.fixture.knowledge,
            "targetKnowledgeState": self.fixture.knowledge,
            "baseAccountingState": self.committed,
            "noAccessPatch": second_no_access_patch,
            "withAccessPatch": second_with_access_patch,
            "noAccessRequest": {"requiredPrimitiveUpdates": []},
            "withAccessRequest": {"requiredPrimitiveUpdates": []},
            "noAccessState": second_no_access,
            "withAccessState": second_committed,
            "evaluation": second_evaluation,
        }
        self.loaded = [first_loaded, second_loaded]
        self.publications = [self.publication, second_publication]
        self.committed = second_committed

    def tearDown(self) -> None:
        self.fixture.tearDown()

    def _build(self, **changes: object) -> dict[str, object]:
        values: dict[str, object] = {
            "projection_id": "hierarchical-work-accounting-v1",
            "label": "Hierarchical work accounting V1",
            "research_projection_ids": ["openrouter-research-v3"],
            "schedule": self.schedule,
            "loaded_evaluation_bundles": self.loaded,
            "publication_manifests": self.publications,
            "terminal_accounting_state": self.committed,
            "terminal_knowledge_state": self.fixture.knowledge,
            "root_contract": self.fixture.contract,
        }
        values.update(changes)
        return build_work_accounting_viewer_projection(**values)

    def test_exports_exact_submission_credit_and_program_thread_annotations(self) -> None:
        projection = self._build()
        self.assertEqual(projection["schemaVersion"], 2)
        self.assertEqual(projection["workAccounting"]["label"], "competent human researcher hours")
        run = projection["runs"][0]
        self.assertEqual(run["terminalAccountingState"], self.committed)
        self.assertEqual(run["runDigest"], self.schedule["scheduleDigest"])
        evaluation = run["evaluations"][0]
        self.assertEqual(evaluation["canonicalOrdinal"], 1)
        self.assertEqual(evaluation["evaluation"], self.evaluation)
        self.assertEqual(evaluation["exAnteWorkHours"], self.evaluation["noAccessWorkHours"])
        self.assertEqual(evaluation["exPostWorkHours"], self.evaluation["withAccessWorkHours"])
        self.assertEqual(evaluation["noAccessWorkHours"], self.evaluation["noAccessWorkHours"])
        self.assertEqual(evaluation["newLiveWorkHours"], self.evaluation["withAccessWorkHours"])
        self.assertEqual(evaluation["workReductionHours"], self.evaluation["workValueHours"])
        self.assertTrue(evaluation["nodeAnnotations"])
        self.assertEqual(evaluation["directUpdateCount"], 1)
        self.assertEqual(evaluation["propagatedEffectCount"], 2)
        self.assertEqual(len(evaluation["nodeEffects"]), 3)
        effect = next(
            item for item in evaluation["nodeEffects"] if item["effectKind"] == "direct"
        )
        self.assertEqual(effect["effectKind"], "direct")
        self.assertEqual(effect["directUpdateBranches"], ["no-access", "new-live"])
        self.assertEqual(effect["primitiveDifferenceFields"], ["directWorkHours"])
        self.assertEqual(effect["workReductionHours"], evaluation["workReductionHours"])
        self.assertTrue(run["terminalNodeAnnotations"])
        self.assertTrue(all("knowledgeStatus" in item for item in run["terminalNodeAnnotations"]))
        self.assertLessEqual(
            {item["nodeRef"]["kind"] for item in evaluation["nodeAnnotations"]},
            {"program", "thread"},
        )
        self.assertNotIn("share", evaluation)
        self.assertNotIn("percentage", evaluation)

    def test_ordinary_catalog_export_omits_the_inactive_overlay(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            catalog = export_viewer_catalog(
                self.fixture.root,
                Path(temporary),
                "example/math-flow",
                canonical_ref="HEAD",
            )
        self.assertNotIn("workAccountingProjections", catalog)

    def test_discovers_governed_v1_and_v2_but_not_unrelated_overlays(self) -> None:
        digests = {
            "openrouter-work-accounting-v1": f"sha256:{'1' * 64}",
            "openrouter-work-accounting-v2": f"sha256:{'2' * 64}",
            "unrelated-credit-overlay": f"sha256:{'3' * 64}",
        }

        def spec(projection_id: str, implementation: str) -> dict[str, object]:
            return {
                "id": projection_id,
                "engine": "overlay-repository-v1",
                "allowedProblems": ["demo"],
                "runner": {
                    "implementation": implementation,
                    "spec": f"protocol/judges/{implementation}.json",
                },
                "dependencies": [
                    {
                        "name": "knowledge",
                        "projectionId": "openrouter-research-v3",
                        "artifactRole": "research-builder-handoff",
                    }
                ],
            }

        specs = {
            digests["openrouter-work-accounting-v1"]: spec(
                "openrouter-work-accounting-v1", "openrouter-work-accounting-v1"
            ),
            digests["openrouter-work-accounting-v2"]: spec(
                "openrouter-work-accounting-v2", "openrouter-work-accounting-v2"
            ),
            digests["unrelated-credit-overlay"]: spec(
                "unrelated-credit-overlay", "openrouter-credit-assignment-v2"
            ),
        }
        stores: list[object] = []
        loaded_profiles: dict[str, str] = {}

        class FakeStore:
            def __init__(
                self,
                root: Path,
                *,
                problem: str,
                projection_id: str,
                projection_spec_digest: str,
                create: bool,
            ) -> None:
                self.root = root
                self.problem = problem
                self.projection_id = projection_id
                self.projection_spec_digest = projection_spec_digest
                self.create = create
                stores.append(self)

            def load_published_snapshot(self) -> dict[str, object]:
                return {"pipeline": {"completedTransitions": [{}]}}

        def load_projection(
            store: FakeStore,
            *,
            label: str,
            research_projection_ids: list[str],
            expected_output_profile: str,
        ) -> dict[str, object]:
            loaded_profiles[store.projection_id] = expected_output_profile
            return self._build(
                projection_id=store.projection_id,
                label=label,
                research_projection_ids=research_projection_ids,
            )

        with tempfile.TemporaryDirectory() as temporary:
            projection_root = Path(temporary)
            for projection_id, projection_digest in digests.items():
                scope = work_accounting_lane_scope_digest(
                    problem="demo",
                    projection_id=projection_id,
                    projection_spec_digest=projection_digest,
                ).removeprefix("sha256:")
                marker = (
                    projection_root
                    / "indexes/problems/demo/work-accounting-v1"
                    / scope
                    / "publication.json"
                )
                marker.parent.mkdir(parents=True)
                marker.write_text("{}\n", encoding="utf-8")
            with (
                patch(
                    "math_flow.work_accounting_viewer.ProjectionBranchWorkAccountingStore",
                    FakeStore,
                ),
                patch(
                    "math_flow.work_accounting_viewer.load_published_work_accounting_viewer_projection",
                    side_effect=load_projection,
                ),
            ):
                projections = discover_published_work_accounting_viewer_projections(
                    projection_root,
                    projection_specs=specs,
                    problem_ids=["demo"],
                )

        self.assertEqual(
            [item["id"] for item in projections],
            ["openrouter-work-accounting-v1", "openrouter-work-accounting-v2"],
        )
        self.assertEqual(
            loaded_profiles,
            {
                "openrouter-work-accounting-v1": "math-flow/work-accounting-transition-v1",
                "openrouter-work-accounting-v2": "math-flow/work-accounting-transition-v2",
            },
        )
        self.assertEqual(
            {store.projection_id for store in stores},
            {"openrouter-work-accounting-v1", "openrouter-work-accounting-v2"},
        )
        v2_evaluation = projections[1]["runs"][0]["evaluations"][0]
        self.assertTrue(v2_evaluation["nodeEffects"])
        self.assertEqual(
            sum(
                Fraction(str(item["workReductionHours"]))
                for item in v2_evaluation["nodeEffects"]
            ),
            Fraction(str(v2_evaluation["workReductionHours"])),
        )
        self.assertTrue(v2_evaluation["nodeEffectsDigest"].startswith("sha256:"))

    def test_published_bundle_profile_must_match_the_governed_lane(self) -> None:
        _require_bundle_output_profile(
            {
                "manifest": {
                    "outputProfile": "math-flow/work-accounting-transition-v1"
                }
            },
            "math-flow/work-accounting-transition-v1",
        )
        _require_bundle_output_profile(
            {
                "manifest": {
                    "outputProfile": "math-flow/work-accounting-transition-v2"
                }
            },
            "math-flow/work-accounting-transition-v2",
        )
        with self.assertRaisesRegex(MathFlowError, "profile disagrees"):
            _require_bundle_output_profile(
                {
                    "manifest": {
                        "outputProfile": "math-flow/work-accounting-transition-v1"
                    }
                },
                "math-flow/work-accounting-transition-v2",
            )

    def test_node_effects_separate_direct_updates_from_propagation(self) -> None:
        subject = self.evaluation["subjectTransactionId"]

        def patch(mode: str, updates: list[dict[str, object]]) -> dict[str, object]:
            return bind_patch_to_state(
                make_work_accounting_patch(
                    problem_id="demo",
                    subject_transaction_id=subject,
                    evaluation_mode=mode,
                    root_contract_digest=self.fixture.contract["rootContractDigest"],
                    base_accounting_state_digest=self.fixture.baseline["stateDigest"],
                    base_knowledge_state_digest=self.fixture.knowledge["stateDigest"],
                    target_knowledge_state_digest=self.fixture.knowledge["stateDigest"],
                    topology_alignment_digest=None,
                    updates=updates,
                ),
                self.fixture.baseline,
            )

        no_patch = patch("no-access", [])
        live_patch = patch(
            "with-access",
            [
                {
                    "nodeRef": {"kind": "program", "id": "root/approach"},
                    "changes": {"conditionalIncidence": "0.5"},
                    "rationale": "The contribution halves the chance that this program is needed.",
                    "evidenceRefs": [subject],
                }
            ],
        )
        no_state, live_state, evaluation = materialize_submission_work_value(
            base_state=self.fixture.baseline,
            no_access_patch=no_patch,
            with_access_patch=live_patch,
            root_contract=self.fixture.contract,
            base_knowledge_state=self.fixture.knowledge,
            target_knowledge_state=self.fixture.knowledge,
        )
        effects, _ = _node_effect_view(
            evaluation_digest=evaluation["evaluationDigest"],
            no_access_state=no_state,
            new_live_state=live_state,
            no_access_patch=no_patch,
            new_live_patch=live_patch,
            no_access_request={"requiredPrimitiveUpdates": []},
            new_live_request={"requiredPrimitiveUpdates": []},
            after_knowledge=self.fixture.knowledge,
            expected_work_reduction=evaluation["workValueHours"],
        )
        direct = [item for item in effects if item["effectKind"] == "direct"]
        propagated = [item for item in effects if item["effectKind"] == "propagated"]
        self.assertEqual(
            [item["nodeRef"] for item in direct],
            [{"kind": "program", "id": "root/approach"}],
        )
        self.assertEqual(len(propagated), 3)
        self.assertTrue(
            any("conditionalSubtreeWorkHours" in item["derivedDifferenceFields"] for item in propagated)
        )
        self.assertTrue(
            any("globalReach" in item["derivedDifferenceFields"] for item in propagated)
        )

    def test_node_effects_preserve_signed_rerouting_contributions(self) -> None:
        subject = self.evaluation["subjectTransactionId"]
        updates = {
            "no-access": [
                {
                    "nodeRef": {"kind": "thread", "id": "root/approach/unstructured-search"},
                    "changes": {"conditionalIncidence": "0"},
                    "rationale": "The fallback is not reached in the no-access route.",
                    "evidenceRefs": [subject],
                },
            ],
            "with-access": [
                {
                    "nodeRef": {"kind": "thread", "id": "root/approach/direct-line"},
                    "changes": {"directWorkHours": "1"},
                    "rationale": "The contribution nearly completes the direct line.",
                    "evidenceRefs": [subject],
                },
            ],
        }
        patches = []
        for mode in ("no-access", "with-access"):
            patches.append(
                bind_patch_to_state(
                    make_work_accounting_patch(
                        problem_id="demo",
                        subject_transaction_id=subject,
                        evaluation_mode=mode,
                        root_contract_digest=self.fixture.contract["rootContractDigest"],
                        base_accounting_state_digest=self.fixture.baseline["stateDigest"],
                        base_knowledge_state_digest=self.fixture.knowledge["stateDigest"],
                        target_knowledge_state_digest=self.fixture.knowledge["stateDigest"],
                        topology_alignment_digest=None,
                        updates=updates[mode],
                    ),
                    self.fixture.baseline,
                )
            )
        no_state, live_state, evaluation = materialize_submission_work_value(
            base_state=self.fixture.baseline,
            no_access_patch=patches[0],
            with_access_patch=patches[1],
            root_contract=self.fixture.contract,
            base_knowledge_state=self.fixture.knowledge,
            target_knowledge_state=self.fixture.knowledge,
        )
        effects, _ = _node_effect_view(
            evaluation_digest=evaluation["evaluationDigest"],
            no_access_state=no_state,
            new_live_state=live_state,
            no_access_patch=patches[0],
            new_live_patch=patches[1],
            no_access_request={"requiredPrimitiveUpdates": []},
            new_live_request={"requiredPrimitiveUpdates": []},
            after_knowledge=self.fixture.knowledge,
            expected_work_reduction=evaluation["workValueHours"],
        )
        fallback = next(
            item
            for item in effects
            if item["nodeRef"]
            == {"kind": "thread", "id": "root/approach/unstructured-search"}
        )
        self.assertEqual(fallback["workReductionHours"], "-3")

    def test_uses_stored_legacy_no_access_topology_requirement(self) -> None:
        loaded = copy.deepcopy(self.loaded)
        no_update = loaded[0]["noAccessPatch"]["updates"][0]
        loaded[0]["noAccessRequest"] = {
            "requiredPrimitiveUpdates": [
                {
                    "nodeRef": copy.deepcopy(no_update["nodeRef"]),
                    "requiredChanges": sorted(no_update["changes"]),
                    "reasons": ["inactive-zeroing"],
                }
            ]
        }
        projection = self._build(loaded_evaluation_bundles=loaded)
        effect = next(
            item
            for item in projection["runs"][0]["evaluations"][0]["nodeEffects"]
            if item["nodeRef"] == no_update["nodeRef"]
        )
        self.assertEqual(effect["topologyRequiredBranches"], ["no-access"])
        self.assertEqual(
            effect["topologyRequirements"],
            [
                {
                    "branch": "no-access",
                    "requiredChanges": sorted(no_update["changes"]),
                    "reasons": ["inactive-zeroing"],
                }
            ],
        )
        self.assertEqual(effect["topologyClassification"], "topology-associated")
        self.assertFalse(effect["topologyOnly"])

    def test_topology_only_covers_every_patched_field_even_when_credit_changes(self) -> None:
        loaded = copy.deepcopy(self.loaded)
        node_ref = loaded[0]["noAccessPatch"]["updates"][0]["nodeRef"]
        for request_key, patch_key in (
            ("noAccessRequest", "noAccessPatch"),
            ("withAccessRequest", "withAccessPatch"),
        ):
            update = loaded[0][patch_key]["updates"][0]
            self.assertEqual(update["nodeRef"], node_ref)
            loaded[0][request_key] = {
                "requiredPrimitiveUpdates": [
                    {
                        "nodeRef": copy.deepcopy(node_ref),
                        "requiredChanges": sorted(update["changes"]),
                        "reasons": ["created"],
                    }
                ]
            }
        projection = self._build(loaded_evaluation_bundles=loaded)
        effect = next(
            item
            for item in projection["runs"][0]["evaluations"][0]["nodeEffects"]
            if item["nodeRef"] == node_ref
        )
        self.assertNotEqual(effect["workReductionHours"], "0")
        self.assertEqual(effect["topologyClassification"], "topology-only")
        self.assertTrue(effect["topologyOnly"])

    def test_patch_prose_is_exported_only_as_bounded_previews(self) -> None:
        preview = _patch_view(
            {
                "changes": {"directWorkHours": "1"},
                "rationale": "r" * 500,
                "evidenceRefs": [
                    "a" * 300,
                    "b" * 300,
                    "c" * 300,
                    "d" * 300,
                ],
            }
        )
        assert preview is not None
        self.assertEqual(len(preview["rationalePreview"]), 240)
        self.assertTrue(preview["rationaleTruncated"])
        self.assertEqual(len(preview["evidenceRefPreviews"]), 3)
        self.assertTrue(
            all(len(value) == 160 for value in preview["evidenceRefPreviews"])
        )
        self.assertEqual(preview["evidenceRefCount"], 4)
        self.assertTrue(preview["evidenceRefsTruncated"])
        self.assertNotIn("rationale", preview)
        self.assertNotIn("evidenceRefs", preview)

    def test_attaches_branch_requests_without_assuming_manifest_stage_order(self) -> None:
        safe_digest = f"sha256:{'1' * 64}"
        live_digest = f"sha256:{'2' * 64}"
        no_digest = f"sha256:{'3' * 64}"
        with tempfile.TemporaryDirectory() as temporary:
            bundle = Path(temporary)
            no_path = bundle / "stages/no-access/request.json"
            live_path = bundle / "stages/with-access/request.json"
            no_path.parent.mkdir(parents=True)
            live_path.parent.mkdir(parents=True)
            no_request = {"stage": "no-access", "requestDigest": no_digest}
            live_request = {"stage": "with-access", "requestDigest": live_digest}
            no_path.write_text(json.dumps(no_request), encoding="utf-8")
            live_path.write_text(json.dumps(live_request), encoding="utf-8")
            loaded = {
                "manifest": {
                    "artifacts": [
                        {
                            "role": "no-access-request",
                            "path": "stages/no-access/request.json",
                        },
                        {
                            "role": "with-access-request",
                            "path": "stages/with-access/request.json",
                        },
                    ],
                    # Work-projection V2 indexes with-access before no-access.
                    "requestDigests": [safe_digest, live_digest, no_digest],
                }
            }
            with patch(
                "math_flow.work_accounting_viewer.validate_work_projection_request",
                side_effect=lambda value: value,
            ):
                attached = _attach_verified_requests(loaded, bundle)
        self.assertEqual(attached["noAccessRequest"], no_request)
        self.assertEqual(attached["withAccessRequest"], live_request)

    def test_rejects_publication_or_terminal_state_not_bound_by_schedule(self) -> None:
        publication = copy.deepcopy(self.publication)
        publication["workValueHours"] = "999"
        with self.assertRaisesRegex(MathFlowError, "digest mismatch"):
            self._build(publication_manifests=[publication, self.publications[1]])

        with self.assertRaisesRegex(MathFlowError, "terminal artifacts"):
            self._build(terminal_accounting_state=self.fixture.baseline)

    def test_exports_prospective_correction_without_rewriting_work_value(self) -> None:
        raw_annotations = []
        for annotation in self.committed["annotations"]:
            raw = {
                "nodeRef": copy.deepcopy(annotation["nodeRef"]),
                "directWorkHours": annotation["directWorkHours"],
                "conditionalIncidence": annotation["conditionalIncidence"],
            }
            if raw["nodeRef"] == {"kind": "thread", "id": "root/approach/direct-line"}:
                raw["directWorkHours"] = "7"
            raw_annotations.append(raw)
        repaired = build_work_accounting_state(
            root_contract=self.fixture.contract,
            knowledge_state=self.fixture.knowledge,
            annotations=raw_annotations,
            predecessor_state_digest=self.committed["stateDigest"],
            processed_submission_ids=self.committed["processedSubmissionIds"],
        )
        event = materialize_work_accounting_state_repair(
            self.schedule,
            reason_kind="evidence-defect",
            base_accounting_state=self.committed,
            repaired_accounting_state=repaired,
            knowledge_state=self.fixture.knowledge,
            root_contract=self.fixture.contract,
            affected_submission_ids=[self.evaluation["subjectTransactionId"]],
            evidence_refs=["audit-ticket-1"],
        )
        repaired_schedule = apply_work_accounting_state_repair(
            self.schedule,
            event,
            repaired_accounting_state=repaired,
            knowledge_state=self.fixture.knowledge,
            root_contract=self.fixture.contract,
        )
        projection = self._build(
            schedule=repaired_schedule,
            terminal_accounting_state=repaired,
            repair_events=[event],
            repair_accounting_states=[repaired],
        )
        evaluation = projection["runs"][0]["evaluations"][0]
        self.assertTrue(evaluation["prospectiveCorrection"])
        self.assertTrue(evaluation["affectedHistory"])
        self.assertEqual(
            evaluation["affectedByRepairDigests"], [event["repairEventDigest"]]
        )
        self.assertEqual(evaluation["workReductionHours"], self.evaluation["workValueHours"])

    def test_rejects_missing_or_ambiguous_repair_lineage(self) -> None:
        # A repaired schedule cannot be represented without its exact repair
        # event and state artifacts.
        raw_annotations = [
            {
                "nodeRef": copy.deepcopy(item["nodeRef"]),
                "directWorkHours": item["directWorkHours"],
                "conditionalIncidence": item["conditionalIncidence"],
            }
            for item in self.committed["annotations"]
        ]
        raw_annotations[0]["directWorkHours"] = "2"
        repaired = build_work_accounting_state(
            root_contract=self.fixture.contract,
            knowledge_state=self.fixture.knowledge,
            annotations=raw_annotations,
            predecessor_state_digest=self.committed["stateDigest"],
            processed_submission_ids=self.committed["processedSubmissionIds"],
        )
        event = materialize_work_accounting_state_repair(
            self.schedule,
            reason_kind="implementation-defect",
            base_accounting_state=self.committed,
            repaired_accounting_state=repaired,
            knowledge_state=self.fixture.knowledge,
            root_contract=self.fixture.contract,
            affected_submission_ids=[self.evaluation["subjectTransactionId"]],
            evidence_refs=["audit-ticket-2"],
        )
        repaired_schedule = apply_work_accounting_state_repair(
            self.schedule,
            event,
            repaired_accounting_state=repaired,
            knowledge_state=self.fixture.knowledge,
            root_contract=self.fixture.contract,
        )
        with self.assertRaisesRegex(MathFlowError, "repair events do not exactly match"):
            self._build(
                schedule=repaired_schedule,
                terminal_accounting_state=repaired,
            )


if __name__ == "__main__":
    unittest.main()
