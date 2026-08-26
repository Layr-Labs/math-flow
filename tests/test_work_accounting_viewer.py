from __future__ import annotations

import copy
import tempfile
import unittest
from pathlib import Path

from math_flow.errors import MathFlowError
from math_flow.work_accounting import build_work_accounting_state
from math_flow.work_accounting_schedule import (
    apply_work_accounting_publication,
    apply_work_accounting_state_repair,
    materialize_work_accounting_state_repair,
)
from math_flow.work_accounting_viewer import build_work_accounting_viewer_projection
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
        first_loaded = {
            "manifest": {
                "problemId": "demo",
                "subjectTransactionId": self.evaluation["subjectTransactionId"],
            },
            "rootContract": self.fixture.contract,
            "baseKnowledgeState": self.fixture.knowledge,
            "targetKnowledgeState": self.fixture.knowledge,
            "baseAccountingState": self.fixture.baseline,
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
        second_loaded = {
            "manifest": {
                "problemId": "demo",
                "subjectTransactionId": second_evaluation["subjectTransactionId"],
            },
            "rootContract": self.fixture.contract,
            "baseKnowledgeState": self.fixture.knowledge,
            "targetKnowledgeState": self.fixture.knowledge,
            "baseAccountingState": self.committed,
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
        self.assertEqual(projection["workAccounting"]["label"], "competent human researcher hours")
        run = projection["runs"][0]
        self.assertEqual(run["terminalAccountingState"], self.committed)
        self.assertEqual(run["runDigest"], self.schedule["scheduleDigest"])
        evaluation = run["evaluations"][0]
        self.assertEqual(evaluation["canonicalOrdinal"], 1)
        self.assertEqual(evaluation["evaluation"], self.evaluation)
        self.assertEqual(evaluation["exAnteWorkHours"], self.evaluation["noAccessWorkHours"])
        self.assertEqual(evaluation["exPostWorkHours"], self.evaluation["withAccessWorkHours"])
        self.assertEqual(evaluation["workReductionHours"], self.evaluation["workValueHours"])
        self.assertTrue(evaluation["nodeAnnotations"])
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
