from __future__ import annotations

import copy
import json
import tempfile
import unittest
import zipfile
from pathlib import Path
from types import SimpleNamespace

from math_flow.bssc_work_accounting_hosted import (
    _load_plan_archives,
    _research_transition_base_knowledge_state,
    _require_admitted_copy,
    build_work_dispatch_history,
    build_bssc_work_disposition_snapshot,
    freeze_work_accounting_plan,
    load_bssc_work_accounting_deployment,
    validate_frozen_work_accounting_plan,
)
from math_flow.errors import MathFlowError
from math_flow.bssc_work_replay import load_bssc_replay_source
from math_flow.repository import sha256_json
from math_flow.research_topology import empty_research_program_state_v2
from math_flow.work_accounting_dispatch import (
    load_work_accounting_hosted_config,
    validate_work_accounting_dispatch_plan,
    validate_work_dispatch_history,
)


DIGEST = "sha256:" + "a" * 64
TRANSACTION = "1" * 40


def seal(value: dict[str, object], field: str) -> dict[str, object]:
    core = {key: copy.deepcopy(item) for key, item in value.items() if key != field}
    return {**core, field: "sha256:" + sha256_json(core)}


def eligible_plan() -> dict[str, object]:
    return validate_work_accounting_dispatch_plan(
        seal(
            {
                "schemaVersion": 1,
                "eligible": True,
                "reasonCode": "eligible",
                "message": "The exact canonical accounting frontier is eligible.",
                "nextEligibleAt": None,
                "configuration": {
                    "id": "bssc-work-accounting-hosted-v1",
                    "configDigest": DIGEST,
                    "runtimePolicyDigest": DIGEST,
                    "builderSpecDigest": DIGEST,
                    "workProviderSpecDigest": DIGEST,
                    "transportDigest": DIGEST,
                    "runnerDigest": DIGEST,
                    "projectionSpecDigest": DIGEST,
                },
                "problemId": "bssc-sum-capacity",
                "projectionId": "openrouter-work-accounting-v1",
                "canonicalHead": "2" * 40,
                "problemLedgerDigest": DIGEST,
                "projectionHead": "3" * 40,
                "projectionStateDigest": DIGEST,
                "rootContractDigest": DIGEST,
                "pipelineStateDigest": DIGEST,
                "scheduleDigest": DIGEST,
                "dispositionSnapshotDigest": DIGEST,
                "subjectTransactionId": TRANSACTION,
                "ledgerOrdinal": 3,
                "acceptedSubmissionInputDigest": DIGEST,
                "judgmentId": DIGEST,
                "predecessorAccountingStateDigest": DIGEST,
                "predecessorKnowledgeStateDigest": DIGEST,
                "mode": "new-subject",
                "semanticDispatchKey": DIGEST,
                "automaticAttemptNumber": 1,
                "maximumSubjectsPerRun": 1,
                "manualReview": False,
            },
            "dispatchDigest",
        )
    )


class BsscHostedAccountingTests(unittest.TestCase):
    def test_resume_reuses_pending_pretransition_knowledge_base(self) -> None:
        base = empty_research_program_state_v2("bssc-sum-capacity")
        stored = SimpleNamespace(
            value=(json.dumps(base, sort_keys=True) + "\n").encode("utf-8")
        )

        class Store:
            def get(self, key: str):
                expected = (
                    "objects/knowledge-states/"
                    f"{str(base['stateDigest']).removeprefix('sha256:')}.json"
                )
                return stored if key == expected else None

        for stage in ("awaiting-work", "publication-prepared"):
            with self.subTest(stage=stage):
                selected = _research_transition_base_knowledge_state(
                    Store(),  # type: ignore[arg-type]
                    {
                        "formedKnowledgeStateDigest": DIGEST,
                        "pendingTransition": {
                            "stage": stage,
                            "subjectTransactionId": TRANSACTION,
                            "beforeKnowledgeStateDigest": base["stateDigest"],
                        },
                    },
                    TRANSACTION,
                    str(base["stateDigest"]),
                )
                self.assertEqual(selected, base)
        with self.assertRaisesRegex(MathFlowError, "does not authorize"):
            _research_transition_base_knowledge_state(
                Store(),  # type: ignore[arg-type]
                {
                    "formedKnowledgeStateDigest": DIGEST,
                    "pendingTransition": {
                        "stage": "awaiting-work",
                        "subjectTransactionId": TRANSACTION,
                        "beforeKnowledgeStateDigest": base["stateDigest"],
                    },
                },
                "2" * 40,
                str(base["stateDigest"]),
            )
        with self.assertRaisesRegex(MathFlowError, "differs from"):
            _research_transition_base_knowledge_state(
                Store(),  # type: ignore[arg-type]
                {
                    "formedKnowledgeStateDigest": DIGEST,
                    "pendingTransition": {
                        "stage": "awaiting-work",
                        "subjectTransactionId": TRANSACTION,
                        "beforeKnowledgeStateDigest": base["stateDigest"],
                    },
                },
                TRANSACTION,
                DIGEST,
            )

    def test_active_deployment_is_sealed_before_separate_admission(self) -> None:
        root = Path(__file__).resolve().parents[1]
        deployment = load_bssc_work_accounting_deployment(
            root, require_admitted=False
        )
        self.assertEqual(
            deployment["config"]["configDigest"],
            "sha256:fae8e7d3aba92ba64c9595ebf53f9d18cc53d10fb9ba0eadbc3f5e4b329d3e71",
        )
        self.assertEqual(
            deployment["contract"]["rootContractDigest"],
            "sha256:01d52a695e88694768973f3590c0c13eb5acd8070fbed32de8ad01e460c41135",
        )

    def test_pinned_validity_history_normalizes_to_16_accepted_9_indeterminate(self) -> None:
        root = Path(__file__).resolve().parents[1]
        deployment = {
            "config": load_work_accounting_hosted_config(
                root,
                root / "protocol/runtime/inactive-work-accounting-hosted-v1.json",
            ),
            "source": load_bssc_replay_source(
                root / "protocol/runtime/bssc-work-accounting-source-v1.json"
            ),
        }
        first = build_bssc_work_disposition_snapshot(
            root, deployment=deployment
        )
        second = build_bssc_work_disposition_snapshot(
            root, deployment=deployment
        )
        self.assertEqual(first, second)
        statuses = [item["status"] for item in first["subjects"]]
        self.assertEqual(statuses.count("accepted"), 16)
        self.assertEqual(statuses.count("indeterminate"), 9)
        self.assertNotIn("pending", statuses)
        self.assertTrue(
            all(
                item["acceptedSubmissionInputDigest"] is not None
                for item in first["subjects"]
                if item["status"] == "accepted"
            )
        )

    def test_active_hosted_workflow_has_narrow_secret_steps(self) -> None:
        root = Path(__file__).resolve().parents[1]
        path = root / ".github/workflows/project-bssc-work-accounting-v1.yml"
        self.assertTrue(path.is_file())
        self.assertFalse(
            (
                root
                / ".github/workflows/project-bssc-work-accounting-v1.yml.inactive"
            ).exists()
        )
        workflow = path.read_text(encoding="utf-8")
        self.assertIn('cron: "*/5 * * * *"', workflow)
        self.assertIn("cancel-in-progress: false", workflow)
        self.assertEqual(workflow.count("OPENROUTER_API_KEY:"), 1)
        self.assertIn("--root prepublish-main prepublish", workflow)
        self.assertIn("persist-credentials: false", workflow)
        self.assertIn("refresh-viewer-catalog.yml", workflow)
        self.assertNotIn("${{ inputs.", workflow)

    def test_history_uses_only_digest_validated_frozen_plan_artifacts(self) -> None:
        plan = freeze_work_accounting_plan(
            run_id=41, planned_at=100, plan=eligible_plan()
        )
        history = build_work_dispatch_history(
            [
                {
                    "databaseId": 42,
                    "status": "in_progress",
                    "conclusion": None,
                    "createdAt": "2026-08-25T00:02:00Z",
                    "startedAt": "2026-08-25T00:02:01Z",
                    "updatedAt": "2026-08-25T00:02:02Z",
                },
                {
                    "databaseId": 41,
                    "status": "completed",
                    "conclusion": "startup_failure",
                    "createdAt": "2026-08-25T00:00:00Z",
                    "startedAt": "2026-08-25T00:00:01Z",
                    "updatedAt": "2026-08-25T00:01:00Z",
                },
            ],
            {41: plan},
            config={
                "configDigest": DIGEST,
                "problemId": "bssc-sum-capacity",
                "projectionId": "openrouter-work-accounting-v1",
            },
            current_run_id=42,
        )
        validate_work_dispatch_history(history)
        self.assertEqual(len(history["runs"]), 1)
        self.assertEqual(history["runs"][0]["conclusion"], "failure")
        self.assertEqual(history["runs"][0]["subjectTransactionId"], TRANSACTION)

        tampered = copy.deepcopy(plan)
        tampered["plan"]["subjectTransactionId"] = "4" * 40
        with self.assertRaisesRegex(MathFlowError, "dispatch digest mismatch"):
            build_work_dispatch_history(
                [],
                {41: tampered},
                config={
                    "configDigest": DIGEST,
                    "problemId": "bssc-sum-capacity",
                    "projectionId": "openrouter-work-accounting-v1",
                },
            )

    def test_frozen_plan_archives_fail_closed_on_path_escape(self) -> None:
        frozen = freeze_work_accounting_plan(
            run_id=41, planned_at=100, plan=eligible_plan()
        )
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            with zipfile.ZipFile(root / "41.zip", "w") as archive:
                archive.writestr("frozen-plan.json", json.dumps(frozen))
            loaded = _load_plan_archives(root)
            self.assertEqual(loaded[41], frozen)

            with zipfile.ZipFile(root / "42.zip", "w") as archive:
                archive.writestr("../frozen-plan.json", json.dumps(frozen))
            with self.assertRaisesRegex(MathFlowError, "unsafe envelope"):
                _load_plan_archives(root)

    def test_active_projection_admission_must_be_byte_identical(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            candidate = root / "protocol/runtime/candidate.json"
            admitted = root / "protocol/projections/demo.json"
            candidate.parent.mkdir(parents=True)
            admitted.parent.mkdir(parents=True)
            candidate.write_bytes(b'{"status":"active"}\n')
            admitted.write_bytes(candidate.read_bytes())
            _require_admitted_copy(
                root,
                candidate_path="protocol/runtime/candidate.json",
                projection_id="demo",
            )
            admitted.write_bytes(b'{"status":"disabled"}\n')
            with self.assertRaisesRegex(MathFlowError, "byte-identical"):
                _require_admitted_copy(
                    root,
                    candidate_path="protocol/runtime/candidate.json",
                    projection_id="demo",
                )

    def test_frozen_plan_digest_binds_run_and_authorization(self) -> None:
        frozen = freeze_work_accounting_plan(
            run_id=41, planned_at=100, plan=eligible_plan()
        )
        validate_frozen_work_accounting_plan(frozen)
        frozen["runId"] = 42
        with self.assertRaisesRegex(MathFlowError, "digest mismatch"):
            validate_frozen_work_accounting_plan(frozen)


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
