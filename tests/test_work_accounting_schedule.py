from __future__ import annotations

import copy
import subprocess
import tempfile
import unittest
from fractions import Fraction
from pathlib import Path

from math_flow.errors import MathFlowError
from math_flow.repository import sha256_json
from math_flow.research_state import (
    apply_research_program_batch_delta,
    empty_research_program_state,
)
from math_flow.work_accounting import (
    bind_patch_to_state,
    build_work_accounting_state,
    canonical_decimal,
    make_root_contract,
    make_work_accounting_patch,
    materialize_submission_work_value,
)
from math_flow.work_accounting_schedule import (
    apply_work_accounting_publication,
    apply_work_accounting_state_repair,
    discover_work_accounting_subjects,
    initialize_work_accounting_schedule,
    materialize_work_accounting_publication_manifest,
    materialize_work_accounting_state_repair,
    plan_next_work_accounting_transition,
    record_work_accounting_failure,
    validate_work_accounting_publication_manifest,
    validate_work_accounting_schedule,
)


PROJECTION_SPEC = "sha256:" + "c" * 64
JUDGMENT = "sha256:" + "d" * 64
FAILURE_EVIDENCE = "sha256:" + "e" * 64


def git(root: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", *args],
        cwd=root,
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    return result.stdout.strip()


def write(path: Path, value: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(value, encoding="utf-8")


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
            "conditionalIncidence": "1",
        },
        {
            "nodeRef": {"kind": "thread", "id": "root/approach-entry"},
            "directWorkHours": "0",
            "conditionalIncidence": "1",
        },
        {
            "nodeRef": {
                "kind": "thread",
                "id": "root/approach/direct-line",
            },
            "directWorkHours": "20",
            "conditionalIncidence": "1",
        },
        {
            "nodeRef": {
                "kind": "thread",
                "id": "root/approach/unstructured-search",
            },
            "directWorkHours": "3",
            "conditionalIncidence": "1",
        },
        {
            "nodeRef": {"kind": "thread", "id": "root/unstructured-search"},
            "directWorkHours": "5",
            "conditionalIncidence": "1",
        },
    ]


class WorkAccountingScheduleTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        git(self.root, "init", "-q")
        git(self.root, "config", "user.name", "Accounting Schedule Test")
        git(self.root, "config", "user.email", "accounting@example.com")
        write(self.root / "problems/demo/problem.md", "# Demo\n")
        git(self.root, "add", ".")
        git(self.root, "commit", "-qm", "add problem")
        self.transactions: list[str] = []
        for index in range(1, 4):
            write(
                self.root
                / f"problems/demo/contributions/submission-{index}/submission.md",
                f"# Submission {index}\n",
            )
            git(self.root, "add", ".")
            git(self.root, "commit", "-qm", f"add submission {index}")
            self.transactions.append(git(self.root, "rev-parse", "HEAD"))
        self.accepted = [self.transactions[0], self.transactions[2]]
        self.knowledge = self._knowledge_state(self.accepted)
        self.contract = make_root_contract(
            problem_id="demo",
            knowledge_projection_id="openrouter-research-v3",
            knowledge_projection_spec_digest=PROJECTION_SPEC,
            objective="Resolve the demo problem.",
            terminal_condition="A valid proof of the canonical objective is accepted.",
            tool_baseline=(
                "Ordinary mathematical references, Python, and standard proof tools "
                "as of 2026-08-25."
            ),
            reference_community_description="Researchers whose submissions Math Flow organizes.",
            researcher_qualification="A competent human researcher qualified for the work package.",
        )
        self.baseline = build_work_accounting_state(
            root_contract=self.contract,
            knowledge_state=self.knowledge,
            annotations=annotations(),
        )

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def _knowledge_state(self, accepted: list[str]) -> dict[str, object]:
        base = empty_research_program_state("demo")
        source_ids = sorted(accepted)
        claim_refs = [
            {"transactionId": transaction_id, "claimKey": f"claim/{index}"}
            for index, transaction_id in enumerate(accepted, 1)
        ]
        operations = [
            {
                "entityKind": "thread",
                "entityId": "root/approach-entry",
                "baseDigest": None,
                "value": {
                    "id": "root/approach-entry",
                    "programId": "root",
                    "title": "Approach entry",
                    "summary": "Entry point for the accepted approach.",
                    "kind": "research",
                    "status": "active",
                    "expectedExposure": "1",
                    "conditions": [],
                    "sourceTransactionIds": source_ids,
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
                    "sourceTransactionIds": source_ids,
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
                    "summary": "The concrete accepted research line.",
                    "kind": "research",
                    "status": "active",
                    "expectedExposure": "1",
                    "conditions": [],
                    "sourceTransactionIds": source_ids,
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
                    "summary": "Residual work inside the approach.",
                    "kind": "unstructured",
                    "status": "active",
                    "expectedExposure": "1",
                    "conditions": [],
                    "sourceTransactionIds": source_ids,
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
                    "claimRefs": claim_refs,
                    "sourceTransactionIds": source_ids,
                    "dependencyItemIds": [],
                },
            },
        ]
        contributions = [
            {
                "transactionId": transaction_id,
                "claimKeys": [f"claim/{index}"],
                "directProgramId": "root/approach",
                "directThreadIds": ["root/approach/direct-line"],
                "itemIds": ["root/approach/result"],
            }
            for index, transaction_id in enumerate(accepted, 1)
        ]
        claims = {
            transaction_id: [
                {
                    "claimKey": f"claim/{index}",
                    "statement": f"Accepted claim {index}.",
                    "dependencyTransactionIds": [],
                }
            ]
            for index, transaction_id in enumerate(accepted, 1)
        }
        return apply_research_program_batch_delta(
            base,
            {
                "schemaVersion": 1,
                "operations": operations,
                "contributions": contributions,
            },
            ledger_head=self.transactions[-1],
            accepted_claims_by_transaction=claims,
            judgment_ids={transaction_id: JUDGMENT for transaction_id in accepted},
        )

    def _schedule(self, *, resolve_excluded: bool = True) -> dict[str, object]:
        resolved = list(self.accepted)
        if resolve_excluded:
            resolved.insert(1, self.transactions[1])
        return initialize_work_accounting_schedule(
            self.root,
            problem="demo",
            projection_id="hierarchical-work-accounting-v1",
            projection_spec_digest=PROJECTION_SPEC,
            root_contract=self.contract,
            accounting_state=self.baseline,
            knowledge_state=self.knowledge,
            resolved_submission_ids=resolved,
            maximum_attempts=3,
            base_retry_seconds=60,
        )

    def _transition_artifacts(
        self,
        schedule: dict[str, object],
        state: dict[str, object],
        *,
        as_of: int = 0,
    ) -> tuple[
        dict[str, object],
        dict[str, object],
        dict[str, object],
        dict[str, object],
        dict[str, object],
        dict[str, object],
    ]:
        plan = plan_next_work_accounting_transition(
            schedule,
            accounting_state=state,
            predecessor_knowledge_state=self.knowledge,
            target_knowledge_state=self.knowledge,
            root_contract=self.contract,
            as_of=as_of,
        )
        self.assertTrue(plan["eligible"])
        claim = plan["claim"]
        assert isinstance(claim, dict)
        subject = str(claim["subjectTransactionId"])
        current_direct = next(
            item["directWorkHours"]
            for item in state["annotations"]
            if item["nodeRef"]
            == {"kind": "thread", "id": "root/approach/direct-line"}
        )
        no_direct = canonical_decimal(Fraction(str(current_direct)) - 1)
        with_direct = canonical_decimal(Fraction(str(current_direct)) - 2)
        patches = []
        for mode, direct in (("no-access", no_direct), ("with-access", with_direct)):
            unbound = make_work_accounting_patch(
                problem_id="demo",
                subject_transaction_id=subject,
                evaluation_mode=mode,
                root_contract_digest=str(self.contract["rootContractDigest"]),
                base_accounting_state_digest=str(state["stateDigest"]),
                base_knowledge_state_digest=str(self.knowledge["stateDigest"]),
                target_knowledge_state_digest=str(self.knowledge["stateDigest"]),
                topology_alignment_digest=None,
                updates=[
                    {
                        "nodeRef": {
                            "kind": "thread",
                            "id": "root/approach/direct-line",
                        },
                        "changes": {"directWorkHours": direct},
                        "rationale": f"The {mode} continuation re-estimates residual work.",
                        "evidenceRefs": [subject],
                    }
                ],
            )
            patches.append(bind_patch_to_state(unbound, state))
        _, committed, evaluation = materialize_submission_work_value(
            base_state=state,
            no_access_patch=patches[0],
            with_access_patch=patches[1],
            root_contract=self.contract,
            base_knowledge_state=self.knowledge,
            target_knowledge_state=self.knowledge,
        )
        publication = materialize_work_accounting_publication_manifest(
            claim,
            evaluation=evaluation,
            no_access_patch=patches[0],
            with_access_patch=patches[1],
            predecessor_accounting_state=state,
            committed_accounting_state=committed,
            predecessor_knowledge_state=self.knowledge,
            target_knowledge_state=self.knowledge,
            root_contract=self.contract,
        )
        return claim, evaluation, committed, publication, patches[0], patches[1]

    def _apply_transition(
        self,
        schedule: dict[str, object],
        state: dict[str, object],
        *,
        as_of: int = 0,
    ) -> tuple[dict[str, object], dict[str, object], tuple[str, str, str, str]]:
        (
            claim,
            evaluation,
            committed,
            publication,
            no_access_patch,
            with_access_patch,
        ) = self._transition_artifacts(schedule, state, as_of=as_of)
        updated = apply_work_accounting_publication(
            schedule,
            claim,
            publication,
            evaluation=evaluation,
            no_access_patch=no_access_patch,
            with_access_patch=with_access_patch,
            predecessor_accounting_state=state,
            committed_accounting_state=committed,
            predecessor_knowledge_state=self.knowledge,
            target_knowledge_state=self.knowledge,
            root_contract=self.contract,
        )
        identity = (
            str(claim["claimDigest"]),
            str(evaluation["evaluationDigest"]),
            str(publication["publicationManifestDigest"]),
            str(committed["stateDigest"]),
        )
        return updated, committed, identity

    def test_canonical_discovery_blocks_behind_unresolved_ledger_transaction(self) -> None:
        schedule = self._schedule(resolve_excluded=False)
        self.assertEqual(
            [(item["ledgerOrdinal"], item["status"]) for item in schedule["subjects"]],
            [(1, "pending"), (3, "blocked")],
        )
        schedule, state, _ = self._apply_transition(schedule, self.baseline)
        plan = plan_next_work_accounting_transition(
            schedule,
            accounting_state=state,
            predecessor_knowledge_state=self.knowledge,
            target_knowledge_state=self.knowledge,
            root_contract=self.contract,
            as_of=0,
        )
        self.assertFalse(plan["eligible"])
        self.assertEqual(plan["reasonCode"], "earlier-canonical-submission-unresolved")
        self.assertEqual(schedule["subjects"][1]["blockedByTransactionId"], self.transactions[1])

        discovered = discover_work_accounting_subjects(
            schedule,
            self.root,
            knowledge_state=self.knowledge,
            resolved_submission_ids=self.transactions,
        )
        self.assertEqual(discovered["subjects"][1]["status"], "pending")

    def test_hosted_batch_grouping_is_semantically_invisible(self) -> None:
        def run(group_size: int) -> tuple[list[tuple[str, str, str, str]], str, str]:
            schedule = self._schedule()
            state = copy.deepcopy(self.baseline)
            identities: list[tuple[str, str, str, str]] = []
            remaining = len(self.accepted)
            while remaining:
                for _ in range(min(group_size, remaining)):
                    schedule, state, identity = self._apply_transition(schedule, state)
                    identities.append(identity)
                    remaining -= 1
            return identities, str(schedule["scheduleDigest"]), str(state["stateDigest"])

        self.assertEqual(run(1), run(2))

    def test_publication_resume_is_idempotent_and_never_replays_subject(self) -> None:
        schedule = self._schedule()
        first = self._transition_artifacts(schedule, self.baseline)
        second = self._transition_artifacts(schedule, self.baseline)
        self.assertEqual(first, second)
        (
            claim,
            evaluation,
            committed,
            publication,
            no_access_patch,
            with_access_patch,
        ) = first
        applied = apply_work_accounting_publication(
            schedule,
            claim,
            publication,
            evaluation=evaluation,
            no_access_patch=no_access_patch,
            with_access_patch=with_access_patch,
            predecessor_accounting_state=self.baseline,
            committed_accounting_state=committed,
            predecessor_knowledge_state=self.knowledge,
            target_knowledge_state=self.knowledge,
            root_contract=self.contract,
        )
        resumed = apply_work_accounting_publication(
            applied,
            claim,
            publication,
            evaluation=evaluation,
            no_access_patch=no_access_patch,
            with_access_patch=with_access_patch,
            predecessor_accounting_state=self.baseline,
            committed_accounting_state=committed,
            predecessor_knowledge_state=self.knowledge,
            target_knowledge_state=self.knowledge,
            root_contract=self.contract,
        )
        self.assertEqual(applied, resumed)
        with self.assertRaisesRegex(MathFlowError, "terminal accounting state has changed"):
            plan_next_work_accounting_transition(
                applied,
                accounting_state=self.baseline,
                predecessor_knowledge_state=self.knowledge,
                target_knowledge_state=self.knowledge,
                root_contract=self.contract,
                as_of=0,
            )

    def test_failures_retry_deterministically_then_block_without_clamping(self) -> None:
        schedule = self._schedule()
        plan = plan_next_work_accounting_transition(
            schedule,
            accounting_state=self.baseline,
            predecessor_knowledge_state=self.knowledge,
            target_knowledge_state=self.knowledge,
            root_contract=self.contract,
            as_of=100,
        )
        claim1 = plan["claim"]
        schedule = record_work_accounting_failure(
            schedule,
            claim1,
            failure_kind="nonpositive-work-value",
            evidence_digest=FAILURE_EVIDENCE,
            failed_at=100,
        )
        self.assertEqual(
            record_work_accounting_failure(
                schedule,
                claim1,
                failure_kind="nonpositive-work-value",
                evidence_digest=FAILURE_EVIDENCE,
                failed_at=100,
            ),
            schedule,
        )
        self.assertEqual(schedule["subjects"][0]["status"], "failed")
        self.assertEqual(schedule["subjects"][0]["failureHistory"][0]["retryNotBefore"], 160)
        waiting = plan_next_work_accounting_transition(
            schedule,
            accounting_state=self.baseline,
            predecessor_knowledge_state=self.knowledge,
            target_knowledge_state=self.knowledge,
            root_contract=self.contract,
            as_of=159,
        )
        self.assertEqual(waiting["reasonCode"], "retry-backoff-active")
        claim2 = plan_next_work_accounting_transition(
            schedule,
            accounting_state=self.baseline,
            predecessor_knowledge_state=self.knowledge,
            target_knowledge_state=self.knowledge,
            root_contract=self.contract,
            as_of=160,
        )["claim"]
        self.assertEqual(claim1["automaticRetryKey"], claim2["automaticRetryKey"])
        self.assertEqual(claim2["previousAttemptClaimDigest"], claim1["claimDigest"])
        schedule = record_work_accounting_failure(
            schedule,
            claim2,
            failure_kind="provider-invalid",
            evidence_digest=FAILURE_EVIDENCE,
            failed_at=200,
        )
        claim3 = plan_next_work_accounting_transition(
            schedule,
            accounting_state=self.baseline,
            predecessor_knowledge_state=self.knowledge,
            target_knowledge_state=self.knowledge,
            root_contract=self.contract,
            as_of=320,
        )["claim"]
        schedule = record_work_accounting_failure(
            schedule,
            claim3,
            failure_kind="counterfactual-invalid",
            evidence_digest=FAILURE_EVIDENCE,
            failed_at=320,
        )
        exhausted = plan_next_work_accounting_transition(
            schedule,
            accounting_state=self.baseline,
            predecessor_knowledge_state=self.knowledge,
            target_knowledge_state=self.knowledge,
            root_contract=self.contract,
            as_of=1000,
        )
        self.assertEqual(exhausted["reasonCode"], "automatic-retries-exhausted")
        self.assertIsNone(schedule["subjects"][0]["failureHistory"][-1]["retryNotBefore"])
        self.assertEqual(schedule["subjects"][1]["status"], "blocked")

    def test_publication_rejects_derived_or_identity_tampering(self) -> None:
        schedule = self._schedule()
        (
            claim,
            evaluation,
            committed,
            publication,
            no_access_patch,
            with_access_patch,
        ) = self._transition_artifacts(schedule, self.baseline)
        tampered = copy.deepcopy(publication)
        tampered["workValueHours"] = "999"
        tampered["publicationManifestDigest"] = "sha256:" + sha256_json(
            {
                key: value
                for key, value in tampered.items()
                if key != "publicationManifestDigest"
            }
        )
        validate_work_accounting_publication_manifest(tampered)
        with self.assertRaisesRegex(MathFlowError, "canonical exact transition"):
            apply_work_accounting_publication(
                schedule,
                claim,
                tampered,
                evaluation=evaluation,
                no_access_patch=no_access_patch,
                with_access_patch=with_access_patch,
                predecessor_accounting_state=self.baseline,
                committed_accounting_state=committed,
                predecessor_knowledge_state=self.knowledge,
                target_knowledge_state=self.knowledge,
                root_contract=self.contract,
            )

    def test_corrections_are_prospective_and_flag_history_without_replay(self) -> None:
        schedule = self._schedule()
        state = self.baseline
        for _ in self.accepted:
            schedule, state, _ = self._apply_transition(schedule, state)
        completions = copy.deepcopy([item["completion"] for item in schedule["subjects"]])
        repaired_annotations = [
            {
                "nodeRef": copy.deepcopy(item["nodeRef"]),
                "directWorkHours": "19"
                if item["nodeRef"]
                == {"kind": "thread", "id": "root/approach/direct-line"}
                else item["directWorkHours"],
                "conditionalIncidence": item["conditionalIncidence"],
            }
            for item in state["annotations"]
        ]
        repaired = build_work_accounting_state(
            root_contract=self.contract,
            knowledge_state=self.knowledge,
            annotations=repaired_annotations,
            predecessor_state_digest=str(state["stateDigest"]),
            evaluation_mode="baseline",
            processed_submission_ids=self.accepted,
        )
        event = materialize_work_accounting_state_repair(
            schedule,
            reason_kind="implementation-defect",
            base_accounting_state=state,
            repaired_accounting_state=repaired,
            knowledge_state=self.knowledge,
            root_contract=self.contract,
            affected_submission_ids=[self.accepted[0]],
            evidence_refs=["projection-run/repair-evidence.json"],
        )
        self.assertFalse(event["suffixReplay"])
        updated = apply_work_accounting_state_repair(
            schedule,
            event,
            repaired_accounting_state=repaired,
            knowledge_state=self.knowledge,
            root_contract=self.contract,
        )
        self.assertEqual(
            [item["completion"] for item in updated["subjects"]], completions
        )
        self.assertEqual(
            updated["subjects"][0]["affectedByRepairDigests"],
            [event["repairEventDigest"]],
        )
        self.assertEqual(updated["subjects"][1]["affectedByRepairDigests"], [])
        self.assertEqual(
            apply_work_accounting_state_repair(
                updated,
                event,
                repaired_accounting_state=repaired,
                knowledge_state=self.knowledge,
                root_contract=self.contract,
            ),
            updated,
        )

    def test_schedule_validator_rejects_retry_and_order_forgery(self) -> None:
        schedule = self._schedule()
        forged = copy.deepcopy(schedule)
        forged["subjects"][0]["ledgerOrdinal"] = 2
        forged["subjects"][0]["recordDigest"] = "sha256:" + sha256_json(
            {
                key: value
                for key, value in forged["subjects"][0].items()
                if key != "recordDigest"
            }
        )
        forged["scheduleDigest"] = "sha256:" + sha256_json(
            {key: value for key, value in forged.items() if key != "scheduleDigest"}
        )
        with self.assertRaisesRegex(MathFlowError, "canonical ledger order"):
            validate_work_accounting_schedule(forged)

        plan = plan_next_work_accounting_transition(
            schedule,
            accounting_state=self.baseline,
            predecessor_knowledge_state=self.knowledge,
            target_knowledge_state=self.knowledge,
            root_contract=self.contract,
            as_of=0,
        )
        failed = record_work_accounting_failure(
            schedule,
            plan["claim"],
            failure_kind="provider-invalid",
            evidence_digest=FAILURE_EVIDENCE,
            failed_at=10,
        )
        retry_forgery = copy.deepcopy(failed)
        failure = retry_forgery["subjects"][0]["failureHistory"][0]
        failure["retryNotBefore"] = 71
        failure["failureDigest"] = "sha256:" + sha256_json(
            {key: value for key, value in failure.items() if key != "failureDigest"}
        )
        record = retry_forgery["subjects"][0]
        record["recordDigest"] = "sha256:" + sha256_json(
            {key: value for key, value in record.items() if key != "recordDigest"}
        )
        retry_forgery["scheduleDigest"] = "sha256:" + sha256_json(
            {
                key: value
                for key, value in retry_forgery.items()
                if key != "scheduleDigest"
            }
        )
        with self.assertRaisesRegex(MathFlowError, "retry schedule is not deterministic"):
            validate_work_accounting_schedule(retry_forgery)


if __name__ == "__main__":
    unittest.main()
