from __future__ import annotations

import copy
import json
import subprocess
import tempfile
import unittest
from pathlib import Path

from math_flow.counterfactual_context import build_submission_evidence_manifest
from math_flow.errors import MathFlowError
from math_flow.research_topology import empty_research_program_state_v2
from math_flow.work_accounting import build_work_accounting_state, make_root_contract
from math_flow.work_accounting_pipeline import (
    AcceptedWorkSubmission,
    CASConflict,
    LocalCASObjectStore,
    WorkProviderFailure,
    advance_work_accounting_pipeline,
    initialize_work_accounting_pipeline,
    materialize_stored_work_projection_bundle,
    read_work_accounting_pipeline_state,
)
from math_flow.work_projection import PROFILE_V2


PROJECTION_SPEC = "sha256:" + "a" * 64
ASSESSMENT = "sha256:" + "b" * 64
JUDGMENTS = ("sha256:" + "c" * 64, "sha256:" + "d" * 64)


def git(root: Path, *arguments: str) -> str:
    completed = subprocess.run(
        ["git", *arguments],
        cwd=root,
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    return completed.stdout.strip()


def write(path: Path, value: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(value, encoding="utf-8")


def without_digest(record: dict[str, object]) -> dict[str, object]:
    return {key: copy.deepcopy(value) for key, value in record.items() if key != "digest"}


def program(
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


def thread(
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


def item(
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


def content_operation(
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


def topology_operation(
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


class FakeBuilderProvider:
    """Deterministic builder fake whose second subject revises the topology."""

    def __init__(self) -> None:
        self.calls: list[str] = []
        self.target_by_subject: dict[str, dict[str, object]] = {}

    def __call__(self, *, base_knowledge_state, submission):
        transaction_id = str(submission["transactionId"])
        claim_key = str(submission["acceptedClaims"][0]["claimKey"])
        self.calls.append(transaction_id)
        if not base_knowledge_state["contributions"]:
            transition = {
                "schemaVersion": 1,
                "subjectTransactionId": transaction_id,
                "baseStateDigest": base_knowledge_state["stateDigest"],
                "contentOperations": [
                    content_operation(
                        "thread",
                        "root/program-a-line",
                        thread(
                            "root/program-a-line", "root", [transaction_id], kind="research"
                        ),
                    ),
                    content_operation(
                        "program",
                        "program-a",
                        program(
                            "program-a", "root", ["root/program-a-line"], [transaction_id]
                        ),
                    ),
                    content_operation(
                        "thread",
                        "program-a/unstructured",
                        thread("program-a/unstructured", "program-a", [transaction_id]),
                    ),
                    content_operation(
                        "item",
                        "program-a/result-a",
                        item("program-a/result-a", "program-a", transaction_id, claim_key),
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
                    "rationale": "The first result establishes a durable local program.",
                    "relatedProgramIds": ["program-a"],
                },
                "topologyRationale": None,
            }
            return transition

        predecessor = base_knowledge_state["programs"]["program-a"]
        predecessor_thread = base_knowledge_state["threads"]["program-a/unstructured"]
        moved_item = base_knowledge_state["items"]["program-a/result-a"]
        left_id = "program-a/left"
        right_id = "program-a/right"
        topology = [
            topology_operation(
                "create",
                "thread",
                "root/program-a-left-line",
                thread("root/program-a-left-line", "root", [transaction_id], kind="research"),
                None,
            ),
            topology_operation(
                "create",
                "thread",
                "root/program-a-right-line",
                thread("root/program-a-right-line", "root", [transaction_id], kind="research"),
                None,
            ),
            topology_operation(
                "create",
                "program",
                left_id,
                program(
                    left_id,
                    "root",
                    ["root/program-a-left-line"],
                    [transaction_id],
                    lineage=[{"relation": "split-from", "programId": "program-a"}],
                ),
                None,
            ),
            topology_operation(
                "create",
                "program",
                right_id,
                program(
                    right_id,
                    "root",
                    ["root/program-a-right-line"],
                    [transaction_id],
                    lineage=[{"relation": "split-from", "programId": "program-a"}],
                ),
                None,
            ),
            topology_operation(
                "create",
                "thread",
                f"{left_id}/unstructured",
                thread(f"{left_id}/unstructured", left_id, [transaction_id]),
                None,
            ),
            topology_operation(
                "create",
                "thread",
                f"{right_id}/unstructured",
                thread(f"{right_id}/unstructured", right_id, [transaction_id]),
                None,
            ),
            topology_operation(
                "move",
                "item",
                "program-a/result-a",
                {**without_digest(moved_item), "programId": left_id},
                moved_item["digest"],
            ),
            topology_operation(
                "retire",
                "thread",
                "program-a/unstructured",
                {
                    **without_digest(predecessor_thread),
                    "status": "retired",
                    "expectedExposure": "0",
                },
                predecessor_thread["digest"],
            ),
            topology_operation(
                "retire",
                "program",
                "program-a",
                {
                    **without_digest(predecessor),
                    "status": "retired",
                    "lineage": [
                        {"relation": "split-into", "programId": left_id},
                        {"relation": "split-into", "programId": right_id},
                    ],
                },
                predecessor["digest"],
            ),
        ]
        return {
            "schemaVersion": 1,
            "subjectTransactionId": transaction_id,
            "baseStateDigest": base_knowledge_state["stateDigest"],
            "contentOperations": [
                content_operation(
                    "item",
                    "root/result-b",
                    item("root/result-b", "root", transaction_id, claim_key),
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
                "rationale": "The second result also revises the cross-cutting topology.",
                "relatedProgramIds": [],
            },
            "topologyRationale": "The prior program has resolved into two stable successors.",
        }


class FakeWorkProvider:
    def __init__(
        self,
        subjects: list[str],
        *,
        failures: int = 0,
        malformed_responses: int = 0,
        reverse_work: bool = False,
    ) -> None:
        self.subjects = subjects
        self.failures = failures
        self.malformed_responses = malformed_responses
        self.reverse_work = reverse_work
        self.calls: list[tuple[str, str]] = []

    def __call__(self, *, stage, request, evidence_files):
        subject = str(request["subjectTransactionId"])
        self.calls.append((subject, stage))
        if stage == "safe-facts" and self.failures:
            self.failures -= 1
            raise WorkProviderFailure("injected provider failure")
        if stage == "safe-facts" and self.malformed_responses:
            self.malformed_responses -= 1
            return {"facts": [], "assumptions": []}
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
            refs = [{"kind": kind, "id": entity_id} for kind, entity_id in ids]
            claim_key = request["stageInput"]["acceptedClaimRefs"][0]["claimKey"]
            return {
                "facts": [
                    {
                        "id": "accepted-submission-changes-world",
                        "condition": "The accepted submission and realized builder topology exist.",
                        "actorVisibility": "withheld-until-independent-discovery",
                        "affectedNodeRefs": refs,
                        "acceptedClaimKeys": [claim_key],
                    }
                ],
                "assumptions": ["The competent reference community uses the fixed contract."],
            }
        updates = []
        for requirement in request["requiredPrimitiveUpdates"]:
            node_ref = requirement["nodeRef"]
            inactive = "inactive-zeroing" in requirement["reasons"]
            changes: dict[str, str] = {}
            for field in requirement["requiredChanges"]:
                if field == "directWorkHours":
                    changes[field] = (
                        "0"
                        if inactive
                        else "1"
                        if self.reverse_work and stage == "no-access"
                        else "4"
                        if self.reverse_work
                        else "4"
                        if stage == "no-access"
                        else "1"
                    )
                else:
                    changes[field] = "0" if inactive else "1"
            updates.append(
                {
                    "nodeRef": copy.deepcopy(node_ref),
                    "changes": changes,
                    "rationale": "Estimate every topology-required primitive in the realized world.",
                    "evidenceRefs": [f"stage:{stage}"],
                }
            )
        # This stable existing leaf guarantees a strictly positive same-world reduction.
        updates.append(
            {
                "nodeRef": {"kind": "thread", "id": "root/unstructured-search"},
                "changes": {
                    "directWorkHours": (
                        "2"
                        if self.reverse_work and stage == "no-access"
                        else "12"
                        if self.reverse_work
                        else "12"
                        if stage == "no-access" and subject == self.subjects[0]
                        else "2"
                        if stage == "with-access" and subject == self.subjects[0]
                        else "15"
                        if stage == "no-access"
                        else "3"
                    )
                },
                "rationale": "The accepted submission reduces residual canonical search.",
                "evidenceRefs": [f"stage:{stage}"],
            }
        )
        by_ref = {(item["nodeRef"]["kind"], item["nodeRef"]["id"]): item for item in updates}
        return {"updates": [by_ref[key] for key in sorted(by_ref)]}


class FailingV2WorkProvider(FakeWorkProvider):
    """Produces a valid frozen W+ followed by a nonpositive first W-."""

    output_profile = PROFILE_V2

    def __init__(self, subjects: list[str]) -> None:
        super().__init__(subjects, reverse_work=True)


class RecoveringNoAccessOnlyV2Provider:
    """A fresh retry process that must consume the CAS-frozen W+ directly."""

    output_profile = PROFILE_V2

    def __init__(self) -> None:
        self.calls: list[str] = []

    def __call__(self, *, stage, request, evidence_files):
        self.calls.append(stage)
        if stage != "no-access" or evidence_files:
            raise AssertionError("V2 retry regenerated or exposed the frozen W+ arm")
        updates = []
        for requirement in request["requiredPrimitiveUpdates"]:
            changes = {
                field: (
                    "0"
                    if "inactive-zeroing" in requirement["reasons"]
                    else "20"
                    if field == "directWorkHours"
                    else "1"
                )
                for field in requirement["requiredChanges"]
            }
            updates.append(
                {
                    "nodeRef": copy.deepcopy(requirement["nodeRef"]),
                    "changes": changes,
                    "rationale": "Retry only the direct no-access W- estimate.",
                    "evidenceRefs": ["stage:no-access"],
                }
            )
        root_search = ("thread", "root/unstructured-search")
        by_ref = {
            (item["nodeRef"]["kind"], item["nodeRef"]["id"]): item
            for item in updates
        }
        by_ref[root_search] = {
            "nodeRef": {"kind": root_search[0], "id": root_search[1]},
            "changes": {"directWorkHours": "30"},
            "rationale": "The no-access world retains substantial search work.",
            "evidenceRefs": ["stage:no-access"],
        }
        return {"updates": [by_ref[key] for key in sorted(by_ref)]}


class RecordingBuilder(FakeBuilderProvider):
    def __call__(self, *, base_knowledge_state, submission):
        transition = super().__call__(
            base_knowledge_state=base_knowledge_state, submission=submission
        )
        # The pipeline performs the authoritative reduction. Repeating it here only gives
        # the work-provider fake the exact expected target for deterministic test output.
        from math_flow.research_builder_v6 import apply_research_builder_v6_transition

        reduced = apply_research_builder_v6_transition(
            base_knowledge_state,
            transition,
            accepted_claims=submission["acceptedClaims"],
            judgment_id=submission["judgmentId"],
        )
        self.target_by_subject[str(submission["transactionId"])] = reduced["postState"]
        return transition


class CrashOnce:
    def __init__(self, boundary: str) -> None:
        self.boundary = boundary
        self.triggered = False

    def __call__(self, boundary: str) -> None:
        if boundary == self.boundary and not self.triggered:
            self.triggered = True
            raise RuntimeError(f"simulated crash at {boundary}")


class WorkAccountingPipelineTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        git(self.root, "init", "-q")
        git(self.root, "config", "user.name", "Pipeline Test")
        git(self.root, "config", "user.email", "pipeline@example.com")
        write(self.root / "problems/demo/problem.md", "# Demo\n")
        git(self.root, "add", ".")
        git(self.root, "commit", "-qm", "add demo")
        self.transaction_ids: list[str] = []
        for index in (1, 2):
            write(
                self.root / f"problems/demo/contributions/submission-{index}/README.md",
                f"# Submission {index}\n\nExact accepted evidence {index}.\n",
            )
            git(self.root, "add", ".")
            git(self.root, "commit", "-qm", f"submission {index}")
            self.transaction_ids.append(git(self.root, "rev-parse", "HEAD"))
        self.contract = make_root_contract(
            problem_id="demo",
            knowledge_projection_id="openrouter-hierarchical-research-builder-v6",
            knowledge_projection_spec_digest=PROJECTION_SPEC,
            objective="Resolve the demo objective.",
            terminal_condition="The canonical objective has an accepted proof.",
            tool_baseline="Ordinary mathematical tools and references as of 2026-08-25.",
            reference_community_description="Qualified researchers organized by Math Flow.",
            researcher_qualification="A competent human researcher qualified for this work.",
        )
        self.initial_knowledge = empty_research_program_state_v2("demo")
        self.initial_accounting = build_work_accounting_state(
            root_contract=self.contract,
            knowledge_state=self.initial_knowledge,
            annotations=[
                {
                    "nodeRef": {"kind": "program", "id": "root"},
                    "directWorkHours": "1",
                    "conditionalIncidence": None,
                },
                {
                    "nodeRef": {"kind": "thread", "id": "root/unstructured-search"},
                    "directWorkHours": "10",
                    "conditionalIncidence": "1",
                },
            ],
        )
        self.submissions = [self._submission(index) for index in range(2)]

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def _submission(self, index: int) -> AcceptedWorkSubmission:
        transaction_id = self.transaction_ids[index]
        claim_key = f"claim-{index + 1}"
        contribution = f"problems/demo/contributions/submission-{index + 1}"
        files = {
            f"{contribution}/README.md": (
                f"# Submission {index + 1}\n\nExact accepted evidence {index + 1}.\n"
            ).encode()
        }
        manifest, chunks = build_submission_evidence_manifest(
            problem_id="demo",
            subject_transaction_id=transaction_id,
            contribution_path=contribution,
            files=files,
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

    def _initialize(self, store: LocalCASObjectStore) -> dict[str, object]:
        return initialize_work_accounting_pipeline(
            store,
            self.root,
            problem="demo",
            projection_id="work-accounting-v1",
            projection_spec_digest=PROJECTION_SPEC,
            root_contract=self.contract,
            initial_knowledge_state=self.initial_knowledge,
            initial_accounting_state=self.initial_accounting,
            resolved_submission_ids=self.transaction_ids,
            base_retry_seconds=10,
        )

    def _run(
        self,
        store_root: Path,
        scratch: Path,
        *,
        maximum_subjects: int | None = None,
        as_of: int = 100,
        crash_hook=None,
        failures: int = 0,
        submissions: list[AcceptedWorkSubmission] | None = None,
    ):
        store = LocalCASObjectStore(store_root)
        if read_work_accounting_pipeline_state(
            store, projection_id="work-accounting-v1", problem="demo"
        ) is None:
            self._initialize(store)
        builder = RecordingBuilder()
        work = FakeWorkProvider(self.transaction_ids, failures=failures)
        state = advance_work_accounting_pipeline(
            store,
            self.root,
            projection_id="work-accounting-v1",
            problem="demo",
            builder_provider=builder,
            work_provider=work,
            accepted_submissions=self.submissions if submissions is None else submissions,
            scratch_root=scratch,
            as_of=as_of,
            maximum_subjects=maximum_subjects,
            crash_hook=crash_hook,
        )
        return store, builder, work, state

    def test_two_submission_end_to_end_includes_topology_revision(self) -> None:
        store, builder, _, state = self._run(
            self.root / "store", self.root / "scratch"
        )
        self.assertEqual(
            [item["subjectTransactionId"] for item in state["completedTransitions"]],
            self.transaction_ids,
        )
        self.assertEqual(builder.calls, self.transaction_ids)
        second = state["completedTransitions"][1]
        alignment_path = (
            self.root
            / "store/objects/topology-alignments"
            / f"{str(second['topologyAlignmentDigest']).removeprefix('sha256:')}.json"
        )
        alignment = json.loads(alignment_path.read_text())
        self.assertEqual(
            alignment["splits"],
            [
                {
                    "predecessorProgramId": "program-a",
                    "successorProgramIds": ["program-a/left", "program-a/right"],
                }
            ],
        )
        self.assertEqual(state["phase"], "ready")
        self.assertIsNone(state["pendingTransition"])
        self.assertEqual(len(set(item["workBundleDigest"] for item in state["completedTransitions"])), 2)
        restored = materialize_stored_work_projection_bundle(
            store,
            bundle_digest=state["completedTransitions"][0]["workBundleDigest"],
            output_dir=self.root / "restored-work-bundle",
        )
        self.assertEqual(
            restored["bundleDigest"], state["completedTransitions"][0]["workBundleDigest"]
        )
        replayed = advance_work_accounting_pipeline(
            store,
            self.root,
            projection_id="work-accounting-v1",
            problem="demo",
            builder_provider=lambda **_: self.fail("completed builder subject replayed"),
            work_provider=lambda **_: self.fail("completed work subject replayed"),
            accepted_submissions=self.submissions,
            scratch_root=self.root / "scratch-replay",
            as_of=100,
        )
        self.assertEqual(replayed, state)

    def test_hosted_batch_size_is_semantically_invisible(self) -> None:
        _, _, _, all_at_once = self._run(
            self.root / "store-all", self.root / "scratch-all"
        )
        store, _, _, first = self._run(
            self.root / "store-one", self.root / "scratch-one", maximum_subjects=1
        )
        self.assertEqual(len(first["completedTransitions"]), 1)
        builder = RecordingBuilder()
        work = FakeWorkProvider(self.transaction_ids)
        split = advance_work_accounting_pipeline(
            store,
            self.root,
            projection_id="work-accounting-v1",
            problem="demo",
            builder_provider=builder,
            work_provider=work,
            accepted_submissions=self.submissions,
            scratch_root=self.root / "scratch-one-second",
            as_of=100,
            maximum_subjects=1,
        )
        self.assertEqual(split, all_at_once)

    def test_stale_compare_and_swap_is_rejected_without_overwrite(self) -> None:
        store = LocalCASObjectStore(self.root / "cas")
        first = store.compare_and_swap("refs/lane.json", None, b"first")
        with self.assertRaises(CASConflict):
            store.compare_and_swap("refs/lane.json", "sha256:" + "0" * 64, b"stale")
        self.assertEqual(store.get("refs/lane.json").value, b"first")
        self.assertEqual(store.compare_and_swap("refs/lane.json", first, b"second"), store.get("refs/lane.json").version)

    def test_resume_after_every_success_boundary(self) -> None:
        boundaries = (
            "submission-stored",
            "builder-proposal-stored",
            "builder-artifacts-stored",
            "builder-head-committed",
            "work-bundle-stored",
            "publication-artifacts-stored",
            "publication-prepared-committed",
            "publication-head-committed",
        )
        _, _, _, expected = self._run(
            self.root / "store-baseline",
            self.root / "scratch-baseline",
            maximum_subjects=1,
            submissions=self.submissions[:1],
        )
        for boundary in boundaries:
            with self.subTest(boundary=boundary):
                hook = CrashOnce(boundary)
                store_root = self.root / f"store-crash-{boundary}"
                scratch = self.root / f"scratch-crash-{boundary}"
                with self.assertRaisesRegex(RuntimeError, "simulated crash"):
                    self._run(
                        store_root,
                        scratch,
                        maximum_subjects=1,
                        crash_hook=hook,
                        submissions=self.submissions[:1],
                    )
                self.assertTrue(hook.triggered)
                _, _, _, resumed = self._run(
                    store_root,
                    scratch,
                    maximum_subjects=1,
                    submissions=self.submissions[:1],
                )
                self.assertEqual(resumed, expected)

    def test_provider_failure_uses_scheduler_retry_without_clamp(self) -> None:
        store, _, _, failed = self._run(
            self.root / "store-retry",
            self.root / "scratch-retry",
            maximum_subjects=1,
            failures=1,
            as_of=100,
        )
        self.assertEqual(failed["phase"], "awaiting-work")
        self.assertIsNone(failed["pendingTransition"]["claimDigest"])
        schedule_digest = str(failed["scheduleDigest"]).removeprefix("sha256:")
        schedule = json.loads(
            (self.root / f"store-retry/objects/schedules/{schedule_digest}.json").read_text()
        )
        self.assertEqual(schedule["subjects"][0]["status"], "failed")
        self.assertEqual(schedule["subjects"][0]["failureHistory"][0]["failureKind"], "provider-invalid")
        builder = RecordingBuilder()
        work = FakeWorkProvider(self.transaction_ids)
        before_backoff = advance_work_accounting_pipeline(
            store,
            self.root,
            projection_id="work-accounting-v1",
            problem="demo",
            builder_provider=builder,
            work_provider=work,
            accepted_submissions=self.submissions,
            scratch_root=self.root / "scratch-retry-early",
            as_of=109,
            maximum_subjects=1,
        )
        self.assertEqual(before_backoff, failed)
        self.assertEqual(work.calls, [])
        recovered = advance_work_accounting_pipeline(
            store,
            self.root,
            projection_id="work-accounting-v1",
            problem="demo",
            builder_provider=builder,
            work_provider=work,
            accepted_submissions=self.submissions,
            scratch_root=self.root / "scratch-retry-late",
            as_of=110,
            maximum_subjects=1,
        )
        self.assertEqual(len(recovered["completedTransitions"]), 1)
        self.assertEqual(recovered["phase"], "ready")
        self.assertEqual(builder.calls, [])

    def test_failure_and_retry_commits_are_crash_recoverable(self) -> None:
        for boundary in ("failure-artifacts-stored", "failure-head-committed"):
            with self.subTest(boundary=boundary):
                hook = CrashOnce(boundary)
                store_root = self.root / f"store-{boundary}"
                scratch = self.root / f"scratch-{boundary}"
                with self.assertRaisesRegex(RuntimeError, "simulated crash"):
                    self._run(
                        store_root,
                        scratch,
                        maximum_subjects=1,
                        failures=1,
                        crash_hook=hook,
                        submissions=self.submissions[:1],
                    )
                self.assertTrue(hook.triggered)
                _, _, _, resumed = self._run(
                    store_root,
                    scratch,
                    maximum_subjects=1,
                    as_of=110,
                    submissions=self.submissions[:1],
                )
                self.assertEqual(len(resumed["completedTransitions"]), 1)

        store_root = self.root / "store-retry-claim-crash"
        scratch = self.root / "scratch-retry-claim-crash"
        self._run(
            store_root,
            scratch,
            maximum_subjects=1,
            failures=1,
            submissions=self.submissions[:1],
        )
        hook = CrashOnce("retry-claim-committed")
        with self.assertRaisesRegex(RuntimeError, "simulated crash"):
            self._run(
                store_root,
                scratch,
                maximum_subjects=1,
                as_of=110,
                crash_hook=hook,
                submissions=self.submissions[:1],
            )
        self.assertTrue(hook.triggered)
        _, _, _, resumed = self._run(
            store_root,
            scratch,
            maximum_subjects=1,
            as_of=110,
            submissions=self.submissions[:1],
        )
        self.assertEqual(len(resumed["completedTransitions"]), 1)

    def test_malformed_provider_result_is_explicitly_provider_invalid(self) -> None:
        store = LocalCASObjectStore(self.root / "store-malformed")
        self._initialize(store)
        builder = RecordingBuilder()
        state = advance_work_accounting_pipeline(
            store,
            self.root,
            projection_id="work-accounting-v1",
            problem="demo",
            builder_provider=builder,
            work_provider=FakeWorkProvider(
                self.transaction_ids, malformed_responses=1
            ),
            accepted_submissions=self.submissions[:1],
            scratch_root=self.root / "scratch-malformed",
            as_of=100,
        )
        schedule_digest = str(state["scheduleDigest"]).removeprefix("sha256:")
        schedule = json.loads(
            (
                self.root
                / f"store-malformed/objects/schedules/{schedule_digest}.json"
            ).read_text()
        )
        self.assertEqual(
            schedule["subjects"][0]["failureHistory"][0]["failureKind"],
            "provider-invalid",
        )

    def test_nonpositive_work_value_is_failed_without_clamping(self) -> None:
        store = LocalCASObjectStore(self.root / "store-nonpositive")
        self._initialize(store)
        builder = RecordingBuilder()
        state = advance_work_accounting_pipeline(
            store,
            self.root,
            projection_id="work-accounting-v1",
            problem="demo",
            builder_provider=builder,
            work_provider=FakeWorkProvider(self.transaction_ids, reverse_work=True),
            accepted_submissions=self.submissions[:1],
            scratch_root=self.root / "scratch-nonpositive",
            as_of=100,
        )
        self.assertEqual(state["completedTransitions"], [])
        schedule_digest = str(state["scheduleDigest"]).removeprefix("sha256:")
        schedule = json.loads(
            (
                self.root
                / f"store-nonpositive/objects/schedules/{schedule_digest}.json"
            ).read_text()
        )
        failure = schedule["subjects"][0]["failureHistory"][0]
        self.assertEqual(failure["failureKind"], "nonpositive-work-value")
        self.assertNotIn("workValueHours", failure)

    def test_v2_outer_retry_reuses_cas_frozen_with_access_candidate(self) -> None:
        store = LocalCASObjectStore(self.root / "store-v2-retry")
        self._initialize(store)
        first_provider = FailingV2WorkProvider(self.transaction_ids)
        failed = advance_work_accounting_pipeline(
            store,
            self.root,
            projection_id="work-accounting-v1",
            problem="demo",
            builder_provider=RecordingBuilder(),
            work_provider=first_provider,
            accepted_submissions=self.submissions[:1],
            scratch_root=self.root / "scratch-v2-first-process",
            as_of=100,
            maximum_subjects=1,
        )
        self.assertEqual(failed["phase"], "awaiting-work")
        self.assertIsNone(failed["pendingTransition"]["claimDigest"])
        self.assertEqual(
            [stage for _, stage in first_provider.calls],
            ["safe-facts", "with-access", "no-access"],
        )
        frozen = list(
            (self.root / "store-v2-retry/indexes/frozen-with-access-candidates").glob(
                "*.json"
            )
        )
        self.assertEqual(len(frozen), 1)
        frozen_bytes = frozen[0].read_bytes()

        retry_provider = RecoveringNoAccessOnlyV2Provider()
        recovered = advance_work_accounting_pipeline(
            store,
            self.root,
            projection_id="work-accounting-v1",
            problem="demo",
            builder_provider=RecordingBuilder(),
            work_provider=retry_provider,
            accepted_submissions=self.submissions[:1],
            # A distinct scratch root models a fresh hosted process.  Only the
            # immutable CAS candidate can carry W+ across this boundary.
            scratch_root=self.root / "scratch-v2-second-process",
            as_of=110,
            maximum_subjects=1,
        )
        self.assertEqual(retry_provider.calls, ["no-access"])
        self.assertEqual(len(recovered["completedTransitions"]), 1)
        self.assertEqual(frozen[0].read_bytes(), frozen_bytes)

    def test_local_store_rejects_path_escape(self) -> None:
        store = LocalCASObjectStore(self.root / "safe-store")
        for key in ("../escape", "/absolute", "a//b"):
            with self.subTest(key=key), self.assertRaises(MathFlowError):
                store.put_immutable(key, b"unsafe")
        target = self.root / "actual-store"
        target.mkdir()
        link = self.root / "linked-store"
        link.symlink_to(target, target_is_directory=True)
        with self.assertRaisesRegex(MathFlowError, "root may not be a symlink"):
            LocalCASObjectStore(link)

    def test_inactive_pipeline_schema_is_present(self) -> None:
        schema = json.loads(
            (
                Path(__file__).resolve().parents[1]
                / "protocol/schemas/work-accounting-pipeline-state-v1.schema.json"
            ).read_text()
        )
        self.assertEqual(schema["$schema"], "https://json-schema.org/draft/2020-12/schema")
        self.assertEqual(schema["properties"]["schemaVersion"], {"const": 1})


if __name__ == "__main__":
    unittest.main()
