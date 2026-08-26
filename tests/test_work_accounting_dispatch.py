from __future__ import annotations

import copy
import json
import subprocess
import tempfile
import unittest
from pathlib import Path

from math_flow.cli import main
from math_flow.counterfactual_context import build_submission_evidence_manifest
from math_flow.errors import MathFlowError
from math_flow.repository import ledger, sha256_json
from math_flow.research_topology import empty_research_program_state_v2
from math_flow.work_accounting import build_work_accounting_state, make_root_contract
from math_flow.work_accounting_dispatch import (
    empty_work_dispatch_history,
    load_work_accounting_hosted_config,
    plan_work_accounting_dispatch,
    recheck_work_accounting_prepublication,
    validate_work_accounting_dispatch_plan,
    validate_work_accounting_prepublication_check,
)
from math_flow.work_accounting_pipeline import (
    AcceptedWorkSubmission,
    LocalCASObjectStore,
    advance_work_accounting_pipeline,
    initialize_work_accounting_pipeline,
    read_work_accounting_pipeline_state,
)
from tests.test_work_accounting_pipeline import (
    ASSESSMENT,
    CrashOnce,
    FakeWorkProvider,
    JUDGMENTS,
    RecordingBuilder,
)


ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = ROOT / "protocol/runtime/inactive-work-accounting-hosted-v1.json"
DIGEST_A = "sha256:" + "a" * 64
DIGEST_B = "sha256:" + "b" * 64


def git(root: Path, *arguments: str) -> str:
    return subprocess.run(
        ["git", *arguments],
        cwd=root,
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    ).stdout.strip()


def write(path: Path, value: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(value, encoding="utf-8")


def seal(value: dict[str, object], field: str) -> dict[str, object]:
    core = {key: copy.deepcopy(item) for key, item in value.items() if key != field}
    return {**core, field: "sha256:" + sha256_json(core)}


class WorkAccountingDispatchTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        git(self.root, "init", "-q")
        git(self.root, "config", "user.name", "Dispatch Test")
        git(self.root, "config", "user.email", "dispatch@example.com")
        write(self.root / "problems/demo/problem.md", "# Demo\n")
        git(self.root, "add", ".")
        git(self.root, "commit", "-qm", "add demo")
        self.transactions: list[str] = []
        for index in range(1, 4):
            write(
                self.root
                / f"problems/demo/contributions/submission-{index}/README.md",
                f"# Submission {index}\n\nExact accepted evidence {index}.\n",
            )
            git(self.root, "add", ".")
            git(self.root, "commit", "-qm", f"submission {index}")
            self.transactions.append(git(self.root, "rev-parse", "HEAD"))
        self.head = git(self.root, "rev-parse", "HEAD")
        for relative in (
            "protocol/judges/openrouter-hierarchical-research-builder-v6.json",
            "protocol/judges/openrouter-work-accounting-v1.json",
            "protocol/runtime/inactive-openrouter-work-accounting-v1-projection.json",
            "math_flow/work_accounting_pipeline.py",
        ):
            target = self.root / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes((ROOT / relative).read_bytes())
        self.config = load_work_accounting_hosted_config(ROOT, CONFIG_PATH)
        self.contract = make_root_contract(
            problem_id="demo",
            knowledge_projection_id=str(self.config["knowledgeProjectionId"]),
            knowledge_projection_spec_digest=str(
                self.config["builderSpec"]["digest"]
            ),
            objective="Resolve the demo objective.",
            terminal_condition="The canonical objective has an accepted proof.",
            tool_baseline="Ordinary mathematical tools and references as of 2026-08-25.",
            reference_community_description="Qualified researchers organized by Math Flow.",
            researcher_qualification="A competent human researcher qualified for this work.",
        )
        self.knowledge = empty_research_program_state_v2("demo")
        self.accounting = build_work_accounting_state(
            root_contract=self.contract,
            knowledge_state=self.knowledge,
            annotations=[
                {
                    "nodeRef": {"kind": "program", "id": "root"},
                    "directWorkHours": "1",
                    "conditionalIncidence": None,
                },
                {
                    "nodeRef": {
                        "kind": "thread",
                        "id": "root/unstructured-search",
                    },
                    "directWorkHours": "10",
                    "conditionalIncidence": "1",
                },
            ],
        )
        self.store = LocalCASObjectStore(self.root / "store")
        self.pipeline = initialize_work_accounting_pipeline(
            self.store,
            self.root,
            problem="demo",
            projection_id=str(self.config["projectionId"]),
            projection_spec_digest=str(self.config["projectionSpec"]["digest"]),
            root_contract=self.contract,
            initial_knowledge_state=self.knowledge,
            initial_accounting_state=self.accounting,
            resolved_submission_ids=self.transactions,
            head=self.head,
            maximum_attempts=int(self.config["retryPolicy"]["maximumAttempts"]),
            base_retry_seconds=int(self.config["retryPolicy"]["baseRetrySeconds"]),
        )
        self.schedule = self._schedule(self.pipeline)

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def _schedule(self, pipeline: dict[str, object]) -> dict[str, object]:
        digest = str(pipeline["scheduleDigest"]).removeprefix("sha256:")
        stored = self.store.get(f"objects/schedules/{digest}.json")
        self.assertIsNotNone(stored)
        return json.loads(stored.value)

    def _snapshot(
        self,
        statuses: list[str],
        *,
        accepted_digests: dict[int, str] | None = None,
        canonical_head: str | None = None,
    ) -> dict[str, object]:
        head = canonical_head or self.head
        canonical = ledger(self.root, "demo", head)
        accepted_digests = accepted_digests or {}
        subjects = []
        for index, (transaction, status) in enumerate(
            zip(canonical["transactions"], statuses, strict=True)
        ):
            terminal = status != "pending"
            subjects.append(
                {
                    "transactionId": transaction["transactionId"],
                    "ledgerOrdinal": transaction["ordinal"],
                    "status": status,
                    "judgmentId": ("sha256:" + f"{index + 1:064x}")
                    if terminal
                    else None,
                    "acceptedSubmissionInputDigest": accepted_digests.get(
                        index, "sha256:" + f"{index + 101:064x}"
                    )
                    if status == "accepted"
                    else None,
                }
            )
        return seal(
            {
                "schemaVersion": 1,
                "problemId": "demo",
                "canonicalHead": head,
                "problemLedgerDigest": canonical["problemLedgerDigest"],
                "knowledgeProjectionId": self.config["knowledgeProjectionId"],
                "knowledgeBuilderSpecDigest": self.config["builderSpec"]["digest"],
                "subjects": subjects,
            },
            "snapshotDigest",
        )

    def _history(self, runs: list[dict[str, object]]) -> dict[str, object]:
        return seal({"schemaVersion": 1, "runs": runs}, "historyDigest")

    def _plan(
        self,
        snapshot: dict[str, object],
        *,
        pipeline: dict[str, object] | None = None,
        schedule: dict[str, object] | None = None,
        history: dict[str, object] | None = None,
        as_of: int = 1000,
        target: str | None = None,
        config: dict[str, object] | None = None,
        projection_state_digest: str | None = None,
    ) -> dict[str, object]:
        return plan_work_accounting_dispatch(
            self.root,
            config=config or self.config,
            pipeline_state=pipeline or self.pipeline,
            schedule=schedule or self.schedule,
            disposition_snapshot=snapshot,
            run_history=history or empty_work_dispatch_history(),
            canonical_head=self.head,
            projection_head=self.head,
            projection_state_digest=projection_state_digest
            or str(self.knowledge["stateDigest"]),
            as_of=as_of,
            target_subject_transaction_id=target,
        )

    def _accepted_submission(self, index: int) -> AcceptedWorkSubmission:
        transaction_id = self.transactions[index]
        claim_key = f"claim-{index + 1}"
        contribution = f"problems/demo/contributions/submission-{index + 1}"
        manifest, chunks = build_submission_evidence_manifest(
            problem_id="demo",
            subject_transaction_id=transaction_id,
            contribution_path=contribution,
            files={
                f"{contribution}/README.md": (
                    f"# Submission {index + 1}\n\nExact accepted evidence {index + 1}.\n"
                ).encode()
            },
            chunk_bytes=17,
        )
        return AcceptedWorkSubmission(
            transaction_id=transaction_id,
            ordinal=index + 1,
            accepted_claims=[
                {
                    "claimKey": claim_key,
                    "statement": f"Accepted statement {index + 1}.",
                    "dependencyTransactionIds": [],
                }
            ],
            judgment_id=JUDGMENTS[index],
            accepted_claim_refs=[
                {
                    "transactionId": transaction_id,
                    "claimKey": claim_key,
                    "judgmentId": JUDGMENTS[index],
                    "assessmentDigest": ASSESSMENT,
                }
            ],
            evidence_manifest=manifest,
            evidence_chunks=chunks,
        )

    def test_parallel_validity_completion_cannot_reorder_accounting(self) -> None:
        blocked = self._plan(self._snapshot(["pending", "accepted", "accepted"]))
        self.assertFalse(blocked["eligible"])
        self.assertEqual(
            blocked["reasonCode"], "earlier-canonical-submission-unresolved"
        )

        exact = self._plan(
            self._snapshot(["rejected", "accepted", "accepted"]),
            target=self.transactions[1],
        )
        self.assertTrue(exact["eligible"])
        self.assertEqual(exact["subjectTransactionId"], self.transactions[1])
        self.assertEqual(exact["ledgerOrdinal"], 2)

        skipped = self._plan(
            self._snapshot(["rejected", "accepted", "accepted"]),
            target=self.transactions[2],
        )
        self.assertFalse(skipped["eligible"])
        self.assertEqual(skipped["reasonCode"], "target-is-not-canonical-frontier")
        self.assertIsNone(skipped["subjectTransactionId"])

    def test_hosted_retry_backoff_active_suppression_and_stale_success_recovery(self) -> None:
        snapshot = self._snapshot(["rejected", "accepted", "rejected"])
        initial = self._plan(snapshot, target=self.transactions[1])
        key = initial["semanticDispatchKey"]
        active = self._history(
            [
                {
                    "runId": 1,
                    "semanticDispatchKey": key,
                    "subjectTransactionId": self.transactions[1],
                    "status": "in_progress",
                    "conclusion": None,
                    "startedAt": 100,
                    "completedAt": None,
                }
            ]
        )
        self.assertEqual(
            self._plan(snapshot, history=active)["reasonCode"],
            "matching-dispatch-active",
        )
        stale_claim = self._plan(snapshot, history=active, as_of=3700)
        self.assertTrue(stale_claim["eligible"])
        self.assertEqual(stale_claim["mode"], "recover-stale-claim")
        self.assertEqual(stale_claim["automaticAttemptNumber"], 2)

        failed = self._history(
            [
                {
                    "runId": 2,
                    "semanticDispatchKey": key,
                    "subjectTransactionId": self.transactions[1],
                    "status": "completed",
                    "conclusion": "timed_out",
                    "startedAt": 100,
                    "completedAt": 110,
                }
            ]
        )
        waiting = self._plan(snapshot, history=failed, as_of=169)
        self.assertEqual(waiting["reasonCode"], "hosted-retry-backoff-active")
        self.assertEqual(waiting["nextEligibleAt"], 170)
        retry = self._plan(snapshot, history=failed, as_of=170)
        self.assertTrue(retry["eligible"])
        self.assertEqual(retry["automaticAttemptNumber"], 2)

        success = self._history(
            [
                {
                    "runId": 3,
                    "semanticDispatchKey": key,
                    "subjectTransactionId": self.transactions[1],
                    "status": "completed",
                    "conclusion": "success",
                    "startedAt": 100,
                    "completedAt": 110,
                }
            ]
        )
        stale = self._plan(snapshot, history=success, as_of=170)
        self.assertTrue(stale["eligible"])
        self.assertEqual(stale["mode"], "recover-stale-success")
        self.assertEqual(stale["automaticAttemptNumber"], 2)

        exhausted_runs = [
            {
                "runId": run_id,
                "semanticDispatchKey": key,
                "subjectTransactionId": self.transactions[1],
                "status": "completed",
                "conclusion": "failure",
                "startedAt": run_id * 100,
                "completedAt": run_id * 100 + 10,
            }
            for run_id in range(1, 6)
        ]
        exhausted = self._plan(
            snapshot, history=self._history(exhausted_runs), as_of=100_000
        )
        self.assertFalse(exhausted["eligible"])
        self.assertEqual(exhausted["reasonCode"], "hosted-retries-exhausted")

        malicious = copy.deepcopy(active)
        malicious["runs"][0]["subjectTransactionId"] = self.transactions[2]
        malicious = seal(malicious, "historyDigest")
        with self.assertRaisesRegex(MathFlowError, "another subject"):
            self._plan(snapshot, history=malicious)

    def test_crash_pending_transition_resumes_the_exact_subject(self) -> None:
        accepted = self._accepted_submission(0)
        crash = CrashOnce("builder-head-committed")
        with self.assertRaisesRegex(RuntimeError, "simulated crash"):
            advance_work_accounting_pipeline(
                self.store,
                self.root,
                projection_id=str(self.config["projectionId"]),
                problem="demo",
                builder_provider=RecordingBuilder(),
                work_provider=FakeWorkProvider(self.transactions),
                accepted_submissions=[accepted],
                scratch_root=self.root / "scratch",
                as_of=100,
                head=self.head,
                maximum_subjects=1,
                crash_hook=crash,
            )
        pending, _ = read_work_accounting_pipeline_state(
            self.store, projection_id=str(self.config["projectionId"]), problem="demo"
        )
        self.assertEqual(pending["phase"], "awaiting-work")
        pending_schedule = self._schedule(pending)
        snapshot = self._snapshot(
            ["accepted", "rejected", "rejected"],
            accepted_digests={0: pending["pendingTransition"]["submissionInputDigest"]},
        )
        resumed = self._plan(
            snapshot,
            pipeline=pending,
            schedule=pending_schedule,
            target=self.transactions[0],
            projection_state_digest=str(pending["formedKnowledgeStateDigest"]),
        )
        self.assertTrue(resumed["eligible"])
        self.assertEqual(resumed["mode"], "resume-pending")
        self.assertEqual(resumed["subjectTransactionId"], self.transactions[0])

    def test_prepublication_recheck_discards_any_state_drift(self) -> None:
        snapshot = self._snapshot(["rejected", "accepted", "rejected"])
        plan = self._plan(snapshot, target=self.transactions[1])
        current = recheck_work_accounting_prepublication(
            self.root,
            original_plan=plan,
            config=self.config,
            pipeline_state=self.pipeline,
            schedule=self.schedule,
            disposition_snapshot=snapshot,
            canonical_head=self.head,
            projection_head=self.head,
            projection_state_digest=str(self.knowledge["stateDigest"]),
            as_of=1001,
        )
        self.assertTrue(current["publishable"])
        validate_work_accounting_prepublication_check(current)

        drifted = recheck_work_accounting_prepublication(
            self.root,
            original_plan=plan,
            config=self.config,
            pipeline_state=self.pipeline,
            schedule=self.schedule,
            disposition_snapshot=snapshot,
            canonical_head=self.head,
            projection_head=self.head,
            projection_state_digest=DIGEST_B,
            as_of=1001,
        )
        self.assertFalse(drifted["publishable"])
        self.assertEqual(drifted["reasonCode"], "dispatch-superseded")

        write(self.root / "problems/demo/contributions/submission-4/README.md", "# Four\n")
        git(self.root, "add", ".")
        git(self.root, "commit", "-qm", "submission four")
        moved_head = git(self.root, "rev-parse", "HEAD")
        with self.assertRaisesRegex(MathFlowError, "canonical head"):
            recheck_work_accounting_prepublication(
                self.root,
                original_plan=plan,
                config=self.config,
                pipeline_state=self.pipeline,
                schedule=self.schedule,
                disposition_snapshot=snapshot,
                canonical_head=moved_head,
                projection_head=self.head,
                projection_state_digest=str(self.knowledge["stateDigest"]),
                as_of=1001,
            )

    def test_batch_size_is_operational_and_not_part_of_semantic_key(self) -> None:
        alternate = copy.deepcopy(self.config)
        alternate["hostedBatching"]["maximumSubjectsPerRun"] = 1
        alternate = seal(alternate, "configDigest")
        path = self.root / "alternate-config.json"
        path.write_text(json.dumps(alternate), encoding="utf-8")
        loaded = load_work_accounting_hosted_config(ROOT, path)
        snapshot = self._snapshot(["rejected", "accepted", "rejected"])
        standard = self._plan(snapshot, target=self.transactions[1])
        limited = self._plan(
            snapshot, target=self.transactions[1], config=loaded
        )
        self.assertEqual(standard["semanticDispatchKey"], limited["semanticDispatchKey"])
        self.assertNotEqual(standard["dispatchDigest"], limited["dispatchDigest"])
        self.assertEqual(limited["maximumSubjectsPerRun"], 1)

    def test_governed_config_rejects_identity_and_path_tampering(self) -> None:
        for name, mutation in (
            (
                "builder",
                lambda value: value["builderSpec"].update(
                    {"digest": "sha256:" + "0" * 64}
                ),
            ),
            (
                "traversal",
                lambda value: value["runner"].update({"path": "../runner.py"}),
            ),
            (
                "manual",
                lambda value: value["retryPolicy"].update({"manualReview": True}),
            ),
        ):
            with self.subTest(name=name):
                invalid = copy.deepcopy(self.config)
                mutation(invalid)
                path = self.root / f"{name}.json"
                path.write_text(json.dumps(invalid), encoding="utf-8")
                with self.assertRaises(MathFlowError):
                    load_work_accounting_hosted_config(ROOT, path)

    def test_cli_and_fake_hosted_path_publish_only_after_fresh_recheck(self) -> None:
        snapshot = self._snapshot(["rejected", "accepted", "rejected"])
        inputs = {
            "pipeline.json": self.pipeline,
            "schedule.json": self.schedule,
            "snapshot.json": snapshot,
            "history.json": empty_work_dispatch_history(),
        }
        for name, value in inputs.items():
            (self.root / name).write_text(json.dumps(value), encoding="utf-8")
        output = self.root / "plan.json"
        self.assertEqual(
            main(
                [
                    "--root",
                    str(self.root),
                    "work-accounting-dispatch-plan",
                    "--config",
                    str(CONFIG_PATH),
                    "--pipeline-state",
                    str(self.root / "pipeline.json"),
                    "--schedule",
                    str(self.root / "schedule.json"),
                    "--dispositions",
                    str(self.root / "snapshot.json"),
                    "--run-history",
                    str(self.root / "history.json"),
                    "--canonical-head",
                    self.head,
                    "--projection-head",
                    self.head,
                    "--projection-state-digest",
                    str(self.knowledge["stateDigest"]),
                    "--as-of",
                    "1000",
                    "--subject",
                    self.transactions[1],
                    "--output",
                    str(output),
                ]
            ),
            0,
        )
        plan = validate_work_accounting_dispatch_plan(json.loads(output.read_text()))
        transport_calls: list[str] = []
        publications: list[str] = []

        def fake_transport() -> dict[str, object]:
            transport_calls.append(str(plan["subjectTransactionId"]))
            return {
                "subjectTransactionId": plan["subjectTransactionId"],
                "semanticDispatchKey": plan["semanticDispatchKey"],
                "resultDigest": DIGEST_A,
            }

        result = fake_transport()
        check = recheck_work_accounting_prepublication(
            self.root,
            original_plan=plan,
            config=self.config,
            pipeline_state=self.pipeline,
            schedule=self.schedule,
            disposition_snapshot=snapshot,
            canonical_head=self.head,
            projection_head=self.head,
            projection_state_digest=str(self.knowledge["stateDigest"]),
            as_of=1001,
        )
        if check["publishable"]:
            publications.append(str(result["resultDigest"]))
        self.assertEqual(transport_calls, [self.transactions[1]])
        self.assertEqual(publications, [DIGEST_A])

        changed = recheck_work_accounting_prepublication(
            self.root,
            original_plan=plan,
            config=self.config,
            pipeline_state=self.pipeline,
            schedule=self.schedule,
            disposition_snapshot=snapshot,
            canonical_head=self.head,
            projection_head=self.head,
            projection_state_digest=DIGEST_B,
            as_of=1001,
        )
        if changed["publishable"]:  # pragma: no cover - fail-closed assertion
            publications.append("should-not-publish")
        self.assertEqual(publications, [DIGEST_A])

    def test_reusable_workflow_is_inactive_secret_free_and_shell_safe(self) -> None:
        workflow = (
            ROOT / ".github/workflows/work-accounting-dispatch-contract-v1.yml"
        ).read_text(encoding="utf-8")
        trigger = workflow.split("permissions:", 1)[0]
        self.assertIn("on:\n  workflow_call:", trigger)
        self.assertNotIn("\n  schedule:", trigger)
        self.assertNotIn("\n  workflow_dispatch:", trigger)
        self.assertNotIn("\n  push:", trigger)
        self.assertNotIn("secrets.", workflow)
        self.assertNotIn("OPENROUTER", workflow)
        self.assertIn("contents: read", workflow)
        self.assertNotIn("contents: write", workflow)
        self.assertIn("ref: main", workflow)
        self.assertIn("work-accounting-prepublish-check", workflow)
        for block in workflow.split("run: |")[1:]:
            shell = block.split("\n      -", 1)[0]
            self.assertNotIn("${{", shell)


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
