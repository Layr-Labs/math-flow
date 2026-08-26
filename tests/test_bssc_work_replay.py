from __future__ import annotations

import copy
import json
import subprocess
import tempfile
import unittest
from decimal import Decimal
from pathlib import Path

from math_flow.bssc_work_replay import (
    build_bssc_work_replay_readiness_report,
    load_bssc_replay_source,
    validate_bssc_work_replay_readiness_report,
)
from math_flow.counterfactual_context import build_submission_evidence_manifest
from math_flow.errors import MathFlowError
from math_flow.research_topology import empty_research_program_state_v2
from math_flow.work_accounting import build_work_accounting_state, make_root_contract
from math_flow.work_accounting_pipeline import (
    AcceptedWorkSubmission,
    LocalCASObjectStore,
    advance_work_accounting_pipeline,
    initialize_work_accounting_pipeline,
    materialize_stored_work_projection_bundle,
)


ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "tests" / "fixtures"
READINESS = ROOT / "docs" / "BSSC_WORK_ACCOUNTING_REPLAY_READINESS_V1.json"
PROJECTION_SPEC = "sha256:" + "a" * 64
ASSESSMENT = "sha256:" + "b" * 64
JUDGMENTS = ("sha256:" + "c" * 64, "sha256:" + "d" * 64)


def _git(root: Path, *arguments: str) -> str:
    return subprocess.run(
        ["git", *arguments],
        cwd=root,
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    ).stdout.strip()


def _write(path: Path, value: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(value, encoding="utf-8")


def _without_digest(record: dict[str, object]) -> dict[str, object]:
    return {key: copy.deepcopy(value) for key, value in record.items() if key != "digest"}


def _program(
    program_id: str,
    parent_id: str,
    parent_threads: list[str],
    sources: list[str],
    *,
    status: str = "active",
    lineage: list[dict[str, str]] | None = None,
) -> dict[str, object]:
    return {
        "id": program_id,
        "parentId": parent_id,
        "title": f"Program {program_id}",
        "objective": f"Resolve the objective for {program_id}.",
        "status": status,
        "parentThreadIds": parent_threads,
        "sourceTransactionIds": sources,
        "lineage": lineage or [],
    }


def _thread(
    thread_id: str,
    program_id: str,
    sources: list[str],
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
        "sourceTransactionIds": sources,
    }


def _item(
    item_id: str, program_id: str, transaction_id: str, claim_key: str
) -> dict[str, object]:
    return {
        "id": item_id,
        "programId": program_id,
        "type": "result",
        "title": f"Result {item_id}",
        "summary": f"Accepted result for {claim_key}.",
        "claimRefs": [{"transactionId": transaction_id, "claimKey": claim_key}],
        "sourceTransactionIds": [transaction_id],
        "dependencyItemIds": [],
    }


def _content(
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


def _topology(
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


class DeterministicFixtureBuilder:
    """Two fixed transition shapes; the second splits the first program."""

    def __init__(self) -> None:
        self.calls: list[str] = []

    def __call__(self, *, base_knowledge_state, submission):
        subject = str(submission["transactionId"])
        claim_key = str(submission["acceptedClaims"][0]["claimKey"])
        self.calls.append(subject)
        if not base_knowledge_state["contributions"]:
            return {
                "schemaVersion": 1,
                "subjectTransactionId": subject,
                "baseStateDigest": base_knowledge_state["stateDigest"],
                "contentOperations": [
                    _content(
                        "thread",
                        "root/program-a-line",
                        _thread("root/program-a-line", "root", [subject], kind="research"),
                    ),
                    _content(
                        "program",
                        "program-a",
                        _program("program-a", "root", ["root/program-a-line"], [subject]),
                    ),
                    _content(
                        "thread",
                        "program-a/unstructured",
                        _thread("program-a/unstructured", "program-a", [subject]),
                    ),
                    _content(
                        "item",
                        "program-a/result-a",
                        _item("program-a/result-a", "program-a", subject, claim_key),
                    ),
                ],
                "topologyOperations": [],
                "contribution": {
                    "claimKeys": [claim_key],
                    "directProgramId": "program-a",
                    "directThreadIds": ["program-a/unstructured"],
                    "itemIds": ["program-a/result-a"],
                },
                "placementAudit": {
                    "basis": "local-objective",
                    "rationale": "The result establishes a durable local program.",
                    "relatedProgramIds": ["program-a"],
                },
                "topologyRationale": None,
            }

        predecessor = base_knowledge_state["programs"]["program-a"]
        predecessor_thread = base_knowledge_state["threads"]["program-a/unstructured"]
        moved_item = base_knowledge_state["items"]["program-a/result-a"]
        left = "program-a/left"
        right = "program-a/right"
        topology = [
            _topology(
                "create",
                "thread",
                "root/program-a-left-line",
                _thread("root/program-a-left-line", "root", [subject], kind="research"),
                None,
            ),
            _topology(
                "create",
                "thread",
                "root/program-a-right-line",
                _thread("root/program-a-right-line", "root", [subject], kind="research"),
                None,
            ),
            _topology(
                "create",
                "program",
                left,
                _program(
                    left,
                    "root",
                    ["root/program-a-left-line"],
                    [subject],
                    lineage=[{"relation": "split-from", "programId": "program-a"}],
                ),
                None,
            ),
            _topology(
                "create",
                "program",
                right,
                _program(
                    right,
                    "root",
                    ["root/program-a-right-line"],
                    [subject],
                    lineage=[{"relation": "split-from", "programId": "program-a"}],
                ),
                None,
            ),
            _topology(
                "create",
                "thread",
                f"{left}/unstructured",
                _thread(f"{left}/unstructured", left, [subject]),
                None,
            ),
            _topology(
                "create",
                "thread",
                f"{right}/unstructured",
                _thread(f"{right}/unstructured", right, [subject]),
                None,
            ),
            _topology(
                "move",
                "item",
                "program-a/result-a",
                {**_without_digest(moved_item), "programId": left},
                moved_item["digest"],
            ),
            _topology(
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
            _topology(
                "retire",
                "program",
                "program-a",
                {
                    **_without_digest(predecessor),
                    "status": "retired",
                    "lineage": [
                        {"relation": "split-into", "programId": left},
                        {"relation": "split-into", "programId": right},
                    ],
                },
                predecessor["digest"],
            ),
        ]
        return {
            "schemaVersion": 1,
            "subjectTransactionId": subject,
            "baseStateDigest": base_knowledge_state["stateDigest"],
            "contentOperations": [
                _content(
                    "item",
                    "root/result-b",
                    _item("root/result-b", "root", subject, claim_key),
                )
            ],
            "topologyOperations": topology,
            "contribution": {
                "claimKeys": [claim_key],
                "directProgramId": "root",
                "directThreadIds": ["root/unstructured-search"],
                "itemIds": ["root/result-b"],
            },
            "placementAudit": {
                "basis": "canonical-objective",
                "rationale": "The result also revises the cross-cutting topology.",
                "relatedProgramIds": [],
            },
            "topologyRationale": "The prior program has split into stable successors.",
        }


class DeterministicFixtureWorkProvider:
    """Deterministic positive same-world estimates, never a model call."""

    def __init__(self, subjects: list[str]) -> None:
        self.subjects = subjects
        self.calls: list[tuple[str, str]] = []

    def __call__(self, *, stage, request, evidence_files):
        del evidence_files
        subject = str(request["subjectTransactionId"])
        self.calls.append((subject, stage))
        if stage == "safe-facts":
            ids = (
                (
                    ("program", "root"),
                    ("program", "program-a"),
                    ("thread", "root/unstructured-search"),
                    ("thread", "root/program-a-line"),
                    ("thread", "program-a/unstructured"),
                )
                if subject == self.subjects[0]
                else (
                    ("program", "root"),
                    ("program", "program-a"),
                    ("program", "program-a/left"),
                    ("program", "program-a/right"),
                    ("thread", "root/unstructured-search"),
                    ("thread", "root/program-a-line"),
                    ("thread", "program-a/unstructured"),
                    ("thread", "root/program-a-left-line"),
                    ("thread", "root/program-a-right-line"),
                    ("thread", "program-a/left/unstructured"),
                    ("thread", "program-a/right/unstructured"),
                )
            )
            return {
                "facts": [
                    {
                        "id": "fixture-realized-world",
                        "condition": "The accepted submission and reduced topology exist.",
                        "actorVisibility": "withheld-until-independent-discovery",
                        "affectedNodeRefs": [
                            {"kind": kind, "id": entity_id} for kind, entity_id in ids
                        ],
                        "acceptedClaimKeys": [
                            request["stageInput"]["acceptedClaimRefs"][0]["claimKey"]
                        ],
                    }
                ],
                "assumptions": ["Use competent human researcher hours."],
            }
        updates = []
        for required in request["requiredPrimitiveUpdates"]:
            inactive = "inactive-zeroing" in required["reasons"]
            changes = {}
            for field in required["requiredChanges"]:
                if inactive:
                    changes[field] = "0"
                elif field == "directWorkHours":
                    changes[field] = "4" if stage == "no-access" else "1"
                else:
                    changes[field] = "1"
            updates.append(
                {
                    "nodeRef": copy.deepcopy(required["nodeRef"]),
                    "changes": changes,
                    "rationale": "Estimate every required primitive in the fixture world.",
                    "evidenceRefs": [f"fixture:{stage}"],
                }
            )
        updates.append(
            {
                "nodeRef": {"kind": "thread", "id": "root/unstructured-search"},
                "changes": {
                    "directWorkHours": (
                        "12"
                        if stage == "no-access" and subject == self.subjects[0]
                        else "2"
                        if stage == "with-access" and subject == self.subjects[0]
                        else "15"
                        if stage == "no-access"
                        else "3"
                    )
                },
                "rationale": "The fixture submission reduces residual canonical search.",
                "evidenceRefs": [f"fixture:{stage}"],
            }
        )
        by_ref = {
            (item["nodeRef"]["kind"], item["nodeRef"]["id"]): item
            for item in updates
        }
        return {"updates": [by_ref[key] for key in sorted(by_ref)]}


class BsscHistoricalDiscoveryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.source = load_bssc_replay_source(
            FIXTURES / "bssc_work_replay_source_v1.json"
        )
        cls.report = build_bssc_work_replay_readiness_report(ROOT, cls.source)

    def test_checked_readiness_report_is_exact_and_fail_closed(self) -> None:
        checked = json.loads(READINESS.read_text(encoding="utf-8"))
        self.assertEqual(self.report, checked)
        validate_bssc_work_replay_readiness_report(checked)
        self.assertEqual(self.report["canonicalSubmissionCount"], 25)
        self.assertEqual(self.report["acceptedSubmissionCount"], 16)
        self.assertEqual(self.report["excludedSubmissionCount"], 9)
        self.assertEqual(self.report["bootstrapCutoff"]["ledgerOrdinal"], 18)
        self.assertEqual(
            [item["ledgerOrdinal"] for item in self.report["replayTransitions"]],
            [19, 21, 24, 25],
        )
        self.assertFalse(
            self.report["invariants"]["strictPositiveReductionHistoricallyVerified"]
        )

    def test_source_and_report_tampering_fail_closed(self) -> None:
        source = copy.deepcopy(self.source)
        source["terminalStateDigest"] = "sha256:" + "0" * 64
        with self.assertRaisesRegex(MathFlowError, "terminal knowledge-state"):
            build_bssc_work_replay_readiness_report(ROOT, source)
        report = copy.deepcopy(self.report)
        report["invariants"]["accountingNodeKinds"].append("item")
        with self.assertRaisesRegex(MathFlowError, "accounting boundaries"):
            validate_bssc_work_replay_readiness_report(report)


class ProviderFreeReplayHarnessTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        _git(self.root, "init", "-q")
        _git(self.root, "config", "user.name", "Replay Fixture")
        _git(self.root, "config", "user.email", "fixture@example.com")
        _write(self.root / "problems/demo/problem.md", "# Demo\n")
        _git(self.root, "add", ".")
        _git(self.root, "commit", "-qm", "add demo")
        self.transaction_ids: list[str] = []
        for ordinal in (1, 2):
            _write(
                self.root / f"problems/demo/contributions/submission-{ordinal}/README.md",
                f"# Submission {ordinal}\n\nExact fixture evidence {ordinal}.\n",
            )
            _git(self.root, "add", ".")
            _git(self.root, "commit", "-qm", f"submission {ordinal}")
            self.transaction_ids.append(_git(self.root, "rev-parse", "HEAD"))
        self.contract = make_root_contract(
            problem_id="demo",
            knowledge_projection_id="fixture-research-builder-v6",
            knowledge_projection_spec_digest=PROJECTION_SPEC,
            objective="Resolve the fixture objective.",
            terminal_condition="The objective has an accepted proof.",
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
                    "nodeRef": {"kind": "thread", "id": "root/unstructured-search"},
                    "directWorkHours": "20",
                    "conditionalIncidence": "1",
                },
            ],
        )
        self.submissions = [self._submission(index) for index in range(2)]

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def _submission(self, index: int) -> AcceptedWorkSubmission:
        subject = self.transaction_ids[index]
        claim_key = f"claim-{index + 1}"
        contribution = f"problems/demo/contributions/submission-{index + 1}"
        files = {
            f"{contribution}/README.md": (
                f"# Submission {index + 1}\n\nExact fixture evidence {index + 1}.\n"
            ).encode()
        }
        manifest, chunks = build_submission_evidence_manifest(
            problem_id="demo",
            subject_transaction_id=subject,
            contribution_path=contribution,
            files=files,
            chunk_bytes=17,
        )
        return AcceptedWorkSubmission(
            transaction_id=subject,
            ordinal=index + 1,
            accepted_claims=[
                {
                    "claimKey": claim_key,
                    "statement": f"Accepted fixture statement {index + 1}.",
                    "dependencyTransactionIds": [],
                }
            ],
            judgment_id=JUDGMENTS[index],
            accepted_claim_refs=[
                {
                    "transactionId": subject,
                    "claimKey": claim_key,
                    "judgmentId": JUDGMENTS[index],
                    "assessmentDigest": ASSESSMENT,
                }
            ],
            evidence_manifest=manifest,
            evidence_chunks=chunks,
        )

    def _run(self, name: str, *, maximum_subjects: int | None = None):
        store = LocalCASObjectStore(self.root / f"store-{name}")
        initialize_work_accounting_pipeline(
            store,
            self.root,
            problem="demo",
            projection_id="fixture-work-accounting-v1",
            projection_spec_digest=PROJECTION_SPEC,
            root_contract=self.contract,
            initial_knowledge_state=self.knowledge,
            initial_accounting_state=self.accounting,
            resolved_submission_ids=self.transaction_ids,
            base_retry_seconds=10,
        )
        builder = DeterministicFixtureBuilder()
        work = DeterministicFixtureWorkProvider(self.transaction_ids)
        state = advance_work_accounting_pipeline(
            store,
            self.root,
            projection_id="fixture-work-accounting-v1",
            problem="demo",
            builder_provider=builder,
            work_provider=work,
            accepted_submissions=self.submissions,
            scratch_root=self.root / f"scratch-{name}",
            as_of=100,
            maximum_subjects=maximum_subjects,
        )
        return store, builder, work, state

    def test_fixture_pipeline_proves_serial_positive_batch_invariant_replay(self) -> None:
        all_store, all_builder, _, all_state = self._run("all")
        split_store, _, _, first = self._run("split", maximum_subjects=1)
        self.assertEqual(len(first["completedTransitions"]), 1)
        split_builder = DeterministicFixtureBuilder()
        split_work = DeterministicFixtureWorkProvider(self.transaction_ids)
        split_state = advance_work_accounting_pipeline(
            split_store,
            self.root,
            projection_id="fixture-work-accounting-v1",
            problem="demo",
            builder_provider=split_builder,
            work_provider=split_work,
            accepted_submissions=self.submissions,
            scratch_root=self.root / "scratch-split-second",
            as_of=100,
            maximum_subjects=1,
        )
        self.assertEqual(split_state, all_state)
        self.assertEqual(all_builder.calls, self.transaction_ids)
        completed = all_state["completedTransitions"]
        self.assertEqual(
            [item["subjectTransactionId"] for item in completed], self.transaction_ids
        )

        evaluations = []
        for index, record in enumerate(completed):
            loaded = materialize_stored_work_projection_bundle(
                all_store,
                bundle_digest=record["workBundleDigest"],
                output_dir=self.root / f"restored-{index}",
            )
            evaluations.append(loaded["evaluation"])
        self.assertTrue(
            all(Decimal(item["workValueHours"]) > 0 for item in evaluations)
        )
        self.assertEqual(
            [item["subjectTransactionId"] for item in evaluations], self.transaction_ids
        )
        self.assertEqual(
            evaluations[1]["baseAccountingStateDigest"],
            completed[0]["accountingStateDigest"],
        )

        final_digest = str(all_state["accountingStateDigest"])
        stored = all_store.get(
            f"objects/accounting-states/{final_digest.removeprefix('sha256:')}.json"
        )
        assert stored is not None
        accounting = json.loads(stored.value)
        self.assertEqual(
            {item["nodeRef"]["kind"] for item in accounting["annotations"]},
            {"program", "thread"},
        )

        replayed = advance_work_accounting_pipeline(
            all_store,
            self.root,
            projection_id="fixture-work-accounting-v1",
            problem="demo",
            builder_provider=lambda **_: self.fail("completed builder replayed"),
            work_provider=lambda **_: self.fail("completed work provider replayed"),
            accepted_submissions=self.submissions,
            scratch_root=self.root / "scratch-idempotent",
            as_of=100,
        )
        self.assertEqual(replayed, all_state)


if __name__ == "__main__":
    unittest.main()
