from __future__ import annotations

import copy
import json
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

from math_flow.artifacts import ArtifactBundle, load_manifest
from math_flow.coordination import record_completed_inputs
from math_flow.counterfactual_context import build_submission_evidence_manifest
from math_flow.errors import MathFlowError
from math_flow.projection_dependencies import resolve_projection_dependencies
from math_flow.repository import ledger, sha256_json
from math_flow.research_builder_v6 import apply_research_builder_v6_transition
from math_flow.research_topology import empty_research_program_state_v2
from math_flow.viewer import export_viewer_catalog, export_viewer_data
from math_flow.work_accounting import build_work_accounting_state, make_root_contract
from math_flow.work_accounting_pipeline import (
    AcceptedWorkSubmission,
    advance_work_accounting_pipeline,
    initialize_work_accounting_pipeline,
    normalize_work_accounting_submission,
)
from math_flow.work_accounting_projection_store import (
    ProjectionBranchWorkAccountingStore,
)
from math_flow.work_accounting_research_v6 import (
    PublishedResearchV6TransitionProvider,
    load_published_research_v6_chain,
    load_published_research_v6_transition,
)


JUDGMENT = "sha256:" + "a" * 64
JUDGMENT_RUN = "sha256:" + "b" * 64
ASSESSMENT = "sha256:" + "c" * 64


def git(root: Path, *arguments: str) -> str:
    result = subprocess.run(
        ["git", *arguments],
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


def write_json(path: Path, value: object) -> None:
    write(path, json.dumps(value, indent=2) + "\n")


def _digest(value: object) -> str:
    return f"sha256:{sha256_json(value)}"


def _transition(
    base: dict[str, object], subject: str, claim_key: str, *, second: bool = False
) -> dict[str, object]:
    if second:
        thread_id = "program-a/second-line"
        item_id = "program-a/result-2"
        operations = [
            {
                "entityKind": "thread",
                "entityId": thread_id,
                "baseDigest": None,
                "value": {
                    "id": thread_id,
                    "programId": "program-a",
                    "title": "Second line",
                    "summary": "Track the second accepted result.",
                    "kind": "research",
                    "status": "active",
                    "expectedExposure": "1",
                    "conditions": [],
                    "sourceTransactionIds": [subject],
                },
            },
            {
                "entityKind": "item",
                "entityId": item_id,
                "baseDigest": None,
                "value": {
                    "id": item_id,
                    "programId": "program-a",
                    "type": "result",
                    "title": "Second result",
                    "summary": "Represent the second accepted claim.",
                    "claimRefs": [
                        {"transactionId": subject, "claimKey": claim_key}
                    ],
                    "sourceTransactionIds": [subject],
                    "dependencyItemIds": [],
                },
            },
        ]
        direct_threads = [thread_id]
        item_ids = [item_id]
    else:
        operations = [
            {
                "entityKind": "thread",
                "entityId": "root/program-a-line",
                "baseDigest": None,
                "value": {
                    "id": "root/program-a-line",
                    "programId": "root",
                    "title": "Program A entry",
                    "summary": "Enter the first local research program.",
                    "kind": "research",
                    "status": "active",
                    "expectedExposure": "1",
                    "conditions": [],
                    "sourceTransactionIds": [subject],
                },
            },
            {
                "entityKind": "program",
                "entityId": "program-a",
                "baseDigest": None,
                "value": {
                    "id": "program-a",
                    "parentId": "root",
                    "title": "Program A",
                    "objective": "Resolve the first local objective.",
                    "status": "active",
                    "parentThreadIds": ["root/program-a-line"],
                    "sourceTransactionIds": [subject],
                    "lineage": [],
                },
            },
            {
                "entityKind": "thread",
                "entityId": "program-a/unstructured",
                "baseDigest": None,
                "value": {
                    "id": "program-a/unstructured",
                    "programId": "program-a",
                    "title": "Program A residual",
                    "summary": "Retain residual work inside the local program.",
                    "kind": "unstructured",
                    "status": "active",
                    "expectedExposure": "1",
                    "conditions": [],
                    "sourceTransactionIds": [subject],
                },
            },
            {
                "entityKind": "item",
                "entityId": "program-a/result-1",
                "baseDigest": None,
                "value": {
                    "id": "program-a/result-1",
                    "programId": "program-a",
                    "type": "result",
                    "title": "First result",
                    "summary": "Represent the first accepted claim.",
                    "claimRefs": [
                        {"transactionId": subject, "claimKey": claim_key}
                    ],
                    "sourceTransactionIds": [subject],
                    "dependencyItemIds": [],
                },
            },
        ]
        direct_threads = ["program-a/unstructured"]
        item_ids = ["program-a/result-1"]
    return {
        "schemaVersion": 1,
        "subjectTransactionId": subject,
        "baseStateDigest": base["stateDigest"],
        "contentOperations": operations,
        "topologyOperations": [],
        "contribution": {
            "claimKeys": [claim_key],
            "directProgramId": "program-a",
            "directThreadIds": direct_threads,
            "itemIds": item_ids,
        },
        "placementAudit": {
            "basis": "local-objective",
            "rationale": "The accepted result advances the exact local objective.",
            "relatedProgramIds": ["program-a"],
        },
        "topologyRationale": None,
    }


class DeterministicWorkProvider:
    def __call__(self, *, stage, request, evidence_files):
        if stage == "safe-facts":
            return {
                "facts": [
                    {
                        "id": "accepted-submission-changes-world",
                        "condition": "The accepted result and realized topology exist.",
                        "actorVisibility": "withheld-until-independent-discovery",
                        "affectedNodeRefs": [
                            {"kind": "program", "id": "root"},
                            {"kind": "program", "id": "program-a"},
                            {"kind": "thread", "id": "root/unstructured-search"},
                            {"kind": "thread", "id": "root/program-a-line"},
                            {"kind": "thread", "id": "program-a/unstructured"},
                        ],
                        "acceptedClaimKeys": [
                            request["stageInput"]["acceptedClaimRefs"][0]["claimKey"]
                        ],
                    }
                ],
                "assumptions": ["Use the fixed competent-human reference world."],
            }
        updates = []
        for requirement in request["requiredPrimitiveUpdates"]:
            inactive = "inactive-zeroing" in requirement["reasons"]
            changes = {
                field: (
                    "0"
                    if inactive
                    else "4"
                    if stage == "no-access" and field == "directWorkHours"
                    else "1"
                )
                for field in requirement["requiredChanges"]
            }
            updates.append(
                {
                    "nodeRef": copy.deepcopy(requirement["nodeRef"]),
                    "changes": changes,
                    "rationale": "Estimate each topology-required primitive.",
                    "evidenceRefs": [f"stage:{stage}"],
                }
            )
        updates.append(
            {
                "nodeRef": {"kind": "thread", "id": "root/unstructured-search"},
                "changes": {"directWorkHours": "12" if stage == "no-access" else "2"},
                "rationale": "The accepted result reduces residual search.",
                "evidenceRefs": [f"stage:{stage}"],
            }
        )
        by_ref = {
            (item["nodeRef"]["kind"], item["nodeRef"]["id"]): item
            for item in updates
        }
        return {"updates": [by_ref[key] for key in sorted(by_ref)]}


class PublishedResearchV6ConsumptionTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name) / "canonical"
        self.projection_root = Path(self.temporary.name) / "projections"
        self.root.mkdir()
        self.projection_root.mkdir()
        for repository in (self.root, self.projection_root):
            git(repository, "init", "-q")
            git(repository, "config", "user.name", "Published V6 Test")
            git(repository, "config", "user.email", "published-v6@example.com")
        write(self.root / "problems/demo/problem.md", "# Demo\n")
        git(self.root, "add", ".")
        git(self.root, "commit", "-qm", "add problem")
        contribution = "problems/demo/contributions/first"
        self.submission_bytes = b"# First\n\nAn exact accepted result.\n"
        write(self.root / contribution / "README.md", self.submission_bytes.decode())
        git(self.root, "add", ".")
        git(self.root, "commit", "-qm", "add first result")
        self.subject = git(self.root, "rev-parse", "HEAD")

        self.builder_spec = {
            "id": "builder-v6",
            "implementation": "openrouter-hierarchical-research-builder-v6",
        }
        self.builder_digest = _digest(self.builder_spec)
        write_json(self.root / "protocol/judges/validity-v4.json", {
            "implementation": "openrouter-validity-judgment-v4"
        })
        write_json(self.root / "protocol/judges/builder-v6.json", self.builder_spec)
        write_json(self.root / "protocol/judges/work-v1.json", {
            "implementation": "openrouter-work-accounting-v1"
        })
        self.research_spec = {
            "schemaVersion": 1,
            "id": "research-v6",
            "description": "Research v6 fixture",
            "status": "active",
            "engine": "openrouter-repository-v1",
            "allowedProblems": ["demo"],
            "primaryJudge": "protocol/judges/validity-v4.json",
            "reconciliationJudge": None,
            "knowledgeBuilder": "protocol/judges/builder-v6.json",
            "scheduling": {
                "judgmentMaxParallel": 1,
                "knowledgeMinimumIntervalSeconds": 0,
                "maximumJudgmentsPerBuild": 1,
            },
        }
        write_json(
            self.root / "protocol/projections/research-v6.json", self.research_spec
        )
        self.research_digest = _digest(self.research_spec)
        self.work_spec = {
            "schemaVersion": 2,
            "id": "work-v1",
            "description": "Work accounting fixture",
            "status": "active",
            "engine": "overlay-repository-v1",
            "allowedProblems": ["demo"],
            "runner": {
                "implementation": "openrouter-work-accounting-v1",
                "spec": "protocol/judges/work-v1.json",
            },
            "dependencies": [
                {
                    "name": "knowledge",
                    "projectionId": "research-v6",
                    "artifactRole": "research-builder-handoff",
                }
            ],
            "scheduling": {"minimumIntervalSeconds": 0},
        }
        write_json(self.root / "protocol/projections/work-v1.json", self.work_spec)
        git(self.root, "add", ".")
        git(self.root, "commit", "-qm", "add governed projections")
        self.head = git(self.root, "rev-parse", "HEAD")
        self.work_digest = _digest(self.work_spec)

        self.claims = [
            {
                "claimKey": "claim-1",
                "statement": "The first exact claim.",
                "dependencyTransactionIds": [],
            }
        ]
        self.evidence_manifest, self.evidence_chunks = (
            build_submission_evidence_manifest(
                problem_id="demo",
                subject_transaction_id=self.subject,
                contribution_path=contribution,
                files={f"{contribution}/README.md": self.submission_bytes},
                chunk_bytes=16,
            )
        )
        self.accepted = AcceptedWorkSubmission(
            transaction_id=self.subject,
            ordinal=1,
            accepted_claims=self.claims,
            judgment_id=JUDGMENT,
            accepted_claim_refs=[
                {
                    "transactionId": self.subject,
                    "claimKey": "claim-1",
                    "judgmentId": JUDGMENT,
                    "assessmentDigest": ASSESSMENT,
                }
            ],
            evidence_manifest=self.evidence_manifest,
            evidence_chunks=self.evidence_chunks,
        )
        base = empty_research_program_state_v2("demo")
        transition = _transition(base, self.subject, "claim-1")
        self.bundle = Path(self.temporary.name) / "research-bundle"
        self.bundle_digest, self.target = self._make_bundle(
            self.bundle,
            base=base,
            transition=transition,
            subject=self.subject,
            ordinal=1,
            claim_key="claim-1",
            evidence_manifest=self.evidence_manifest,
            base_run=None,
        )
        self._publish_research_bundle(self.bundle, self.bundle_digest)
        self._publish_judgment_bundle()
        self._write_run_index()
        self._write_scheduler()
        write(self.projection_root / ".gitkeep", "")
        git(self.projection_root, "add", ".")
        git(self.projection_root, "commit", "-qm", "publish research fixture")

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def _make_bundle(
        self,
        target: Path,
        *,
        base: dict[str, object],
        transition: dict[str, object],
        subject: str,
        ordinal: int,
        claim_key: str,
        evidence_manifest: dict[str, object],
        base_run: str | None,
    ) -> tuple[str, dict[str, object]]:
        claims = [
            {
                "claimKey": claim_key,
                "statement": f"Exact statement {ordinal}.",
                "dependencyTransactionIds": [],
            }
        ]
        # Preserve the exact first accepted claim bytes used by the work lane.
        if ordinal == 1:
            claims = copy.deepcopy(self.claims)
        reduced = apply_research_builder_v6_transition(
            base, transition, accepted_claims=claims, judgment_id=JUDGMENT
        )
        submission_core = {
            "schemaVersion": 1,
            "problemId": "demo",
            "subjectTransactionId": subject,
            "ledgerOrdinal": ordinal,
            "judgmentId": JUDGMENT,
            "acceptedClaims": claims,
            "evidenceManifestDigest": evidence_manifest["manifestDigest"],
        }
        submission = {
            **submission_core,
            "submissionInputDigest": _digest(submission_core),
        }
        set_core = {"judgmentIds": [JUDGMENT], "conflictIds": []}
        claim_core = {
            "schemaVersion": 1,
            "laneId": _digest(
                {
                    "problemId": "demo",
                    "projectionSpecDigest": self.research_digest,
                }
            ),
            "problemId": "demo",
            "builderSpecDigest": self.builder_digest,
            "baseStateRun": base_run,
            "judgmentIds": [JUDGMENT],
            "conflictIds": [],
            "judgmentSetDigest": _digest(set_core),
            "projectionSpecDigest": self.research_digest,
        }
        build_input = {**claim_core, "buildToken": _digest(claim_core)}
        source = ledger(self.root, "demo", self.head)
        writer = ArtifactBundle(target)
        writer.add_json("control/build-input.json", build_input, "knowledge-build-input")
        writer.add_json(
            "input/submission.json", submission, "research-builder-submission-input"
        )
        writer.add_json(
            "input/evidence-manifest.json",
            evidence_manifest,
            "submission-evidence-manifest",
        )
        writer.add_json("state/base-state.json", base, "research-program-base-state")
        writer.add_json(
            "state/transition.json", transition, "research-program-transition"
        )
        writer.add_json(
            "state/state.json", reduced["postState"], "research-program-state"
        )
        writer.add_json(
            "state/topology-alignment.json",
            reduced["topologyAlignment"],
            "research-topology-alignment",
        )
        writer.add_json(
            "state/same-world-handoff.json",
            reduced["sameWorldHandoff"],
            "research-builder-handoff",
        )
        writer.finalize(
            {
                "protocolVersion": 1,
                "runKind": "knowledge-build",
                "problemId": "demo",
                "ledgerHead": subject,
                "problemLedgerHead": source["problemLedgerHead"],
                "problemLedgerDigest": source["problemLedgerDigest"],
                "outputProfile": "math-flow/hierarchical-research-v6",
                "judgeSpec": {"id": "builder-v6", "digest": self.builder_digest},
                "runner": {"implementation": "fixture", "mathFlowVersion": "test"},
                "baseRun": base_run,
                "requestDigests": [],
                "providerRuns": [],
                "inputs": {
                    **build_input,
                    "judgmentRunDigest": JUDGMENT_RUN,
                    "submissionInputDigest": submission["submissionInputDigest"],
                },
            }
        )
        _, bundle_digest = load_manifest(target)
        return bundle_digest, reduced["postState"]

    def _publish_research_bundle(self, bundle: Path, digest: str) -> Path:
        digest_hex = digest.removeprefix("sha256:")
        published = (
            self.projection_root
            / "objects"
            / "knowledge-build"
            / digest_hex[:2]
            / digest_hex
        )
        published.parent.mkdir(parents=True, exist_ok=True)
        shutil.copytree(bundle, published)
        return published

    def _publish_judgment_bundle(self) -> None:
        bundle = Path(self.temporary.name) / "judgment-bundle"
        writer = ArtifactBundle(bundle)
        writer.add_json(
            "judgment.json",
            {
                "schemaVersion": 1,
                "judgmentId": JUDGMENT,
                "judgmentKind": "primary",
                "subjects": [{"id": self.subject}],
            },
            "judgment-record",
        )
        writer.add_text("report.md", "# Validity\n", "judgment-report", "text/markdown")
        writer.finalize(
            {
                "protocolVersion": 1,
                "runKind": "judgment",
                "problemId": "demo",
                "ledgerHead": self.subject,
                "problemLedgerHead": self.subject,
                "problemLedgerDigest": ledger(self.root, "demo", self.head)[
                    "problemLedgerDigest"
                ],
                "outputProfile": "fixture-validity",
                "judgeSpec": {"id": "validity-v4", "digest": _digest({})},
                "runner": {"implementation": "fixture", "mathFlowVersion": "test"},
                "baseRun": None,
                "requestDigests": [],
                "providerRuns": [],
            }
        )
        _, digest = load_manifest(bundle)
        # The v6 fixture binds a synthetic judgment-run digest; make the actual
        # manifest address match that binding only in the publication index is
        # unnecessary because the viewer indexes the judgment ID, not this input.
        digest_hex = digest.removeprefix("sha256:")
        target = (
            self.projection_root
            / "objects"
            / "judgment"
            / digest_hex[:2]
            / digest_hex
        )
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copytree(bundle, target)
        self.judgment_bundle_digest = digest
        self.judgment_bundle_path = target

    def _write_run_index(self) -> None:
        research_hex = self.bundle_digest.removeprefix("sha256:")
        judgment_hex = self.judgment_bundle_digest.removeprefix("sha256:")
        write_json(
            self.projection_root / "indexes/problems/demo/runs.json",
            [
                {
                    "runDigest": self.judgment_bundle_digest,
                    "runKind": "judgment",
                    "problemId": "demo",
                    "path": f"objects/judgment/{judgment_hex[:2]}/{judgment_hex}",
                },
                {
                    "runDigest": self.bundle_digest,
                    "runKind": "knowledge-build",
                    "problemId": "demo",
                    "path": f"objects/knowledge-build/{research_hex[:2]}/{research_hex}",
                },
            ],
        )

    def _write_scheduler(self) -> None:
        scheduler_path = self.projection_root / "coordination/scheduler.json"
        lane = record_completed_inputs(
            scheduler_path,
            "demo",
            self.builder_digest,
            [JUDGMENT],
            [],
            0,
            1,
            projection_spec_digest=self.research_digest,
        )
        lane["latestStateRun"] = self.bundle_digest
        lane["lastCompletedAt"] = 1
        lane["pendingJudgmentIds"] = []
        lane["nextEligibleAt"] = None
        write_json(scheduler_path, {"schemaVersion": 1, "lanes": {lane["laneId"]: lane}})

    def test_loads_chain_and_replays_exact_transition_without_provider(self) -> None:
        loaded = load_published_research_v6_transition(
            self.bundle,
            expected_bundle_digest=self.bundle_digest,
            expected_problem="demo",
            expected_projection_spec_digest=self.research_digest,
            expected_builder_spec_digest=self.builder_digest,
        )
        record, _ = normalize_work_accounting_submission(self.accepted, "demo")
        provider = PublishedResearchV6TransitionProvider([loaded])
        self.assertEqual(
            provider(
                base_knowledge_state=empty_research_program_state_v2("demo"),
                submission=record,
            ),
            loaded.transition,
        )
        changed = copy.deepcopy(self.accepted)
        changed = AcceptedWorkSubmission(
            **{
                **changed.__dict__,
                "accepted_claims": [
                    {
                        **self.claims[0],
                        "statement": "A different accepted statement.",
                    }
                ],
            }
        )
        changed_record, _ = normalize_work_accounting_submission(changed, "demo")
        with self.assertRaisesRegex(MathFlowError, "does not match"):
            provider(
                base_knowledge_state=empty_research_program_state_v2("demo"),
                submission=changed_record,
            )

    def test_loads_complete_published_predecessor_chain(self) -> None:
        second_subject = "d" * 40
        second_manifest, _ = build_submission_evidence_manifest(
            problem_id="demo",
            subject_transaction_id=second_subject,
            contribution_path="problems/demo/contributions/second",
            files={"problems/demo/contributions/second/README.md": b"# Second\n"},
            chunk_bytes=16,
        )
        transition = _transition(
            self.target, second_subject, "claim-2", second=True
        )
        second_bundle = Path(self.temporary.name) / "research-bundle-2"
        second_digest, _ = self._make_bundle(
            second_bundle,
            base=self.target,
            transition=transition,
            subject=second_subject,
            ordinal=2,
            claim_key="claim-2",
            evidence_manifest=second_manifest,
            base_run=self.bundle_digest,
        )
        self._publish_research_bundle(second_bundle, second_digest)
        chain = load_published_research_v6_chain(
            self.projection_root,
            second_digest,
            expected_problem="demo",
            expected_projection_spec_digest=self.research_digest,
            expected_builder_spec_digest=self.builder_digest,
        )
        self.assertEqual([item.bundle_digest for item in chain], [self.bundle_digest, second_digest])

    def test_resolves_typed_handoff_and_exports_research_v6(self) -> None:
        lock = resolve_projection_dependencies(
            self.root, self.projection_root, "work-v1", "demo", self.head
        )
        dependency = lock["dependencies"][0]
        self.assertEqual(dependency["artifact"]["role"], "research-builder-handoff")
        data = export_viewer_data(
            self.root,
            "demo",
            self.subject,
            [self.bundle],
            judgment_dirs=[self.judgment_bundle_path],
        )
        run = data["runs"][0]
        self.assertEqual(run["state"]["stateDigest"], self.target["stateDigest"])
        self.assertEqual(
            run["sameWorldHandoff"]["handoffDigest"],
            load_published_research_v6_transition(self.bundle).same_world_handoff[
                "handoffDigest"
            ],
        )

    def test_catalog_automatically_discovers_verified_published_work_lane(self) -> None:
        contract = make_root_contract(
            problem_id="demo",
            knowledge_projection_id="research-v6",
            knowledge_projection_spec_digest=self.research_digest,
            objective="Resolve the demo objective.",
            terminal_condition="The exact accepted result resolves the objective.",
            tool_baseline="Ordinary mathematical research tools as of 2026-08-25.",
            reference_community_description="Qualified researchers organized by Math Flow.",
            researcher_qualification="A competent human researcher for the work package.",
        )
        initial_knowledge = empty_research_program_state_v2("demo")
        initial_accounting = build_work_accounting_state(
            root_contract=contract,
            knowledge_state=initial_knowledge,
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
        store = ProjectionBranchWorkAccountingStore(
            self.projection_root,
            problem="demo",
            projection_id="work-v1",
            projection_spec_digest=self.work_digest,
        )
        initialize_work_accounting_pipeline(
            store,
            self.root,
            problem="demo",
            projection_id="work-v1",
            projection_spec_digest=self.work_digest,
            root_contract=contract,
            initial_knowledge_state=initial_knowledge,
            initial_accounting_state=initial_accounting,
            resolved_submission_ids=[self.subject],
            head=self.head,
        )
        loaded = load_published_research_v6_transition(self.bundle)
        pipeline = advance_work_accounting_pipeline(
            store,
            self.root,
            projection_id="work-v1",
            problem="demo",
            builder_provider=PublishedResearchV6TransitionProvider([loaded]),
            work_provider=DeterministicWorkProvider(),
            accepted_submissions=[self.accepted],
            scratch_root=Path(self.temporary.name) / "scratch",
            as_of=100,
            head=self.head,
        )
        self.assertEqual(len(pipeline["completedTransitions"]), 1)
        store.prepare_publication()
        # An object-first publisher may crash before advancing the marker.  The
        # catalog must continue to present the last complete publication and
        # ignore an immutable object that is not reachable from that marker.
        store.put_immutable("objects/future-checkpoint/orphan.bin", b"future")

        catalog = export_viewer_catalog(
            self.root,
            self.projection_root,
            "example/math-flow",
            canonical_ref="HEAD",
        )
        work = catalog["workAccountingProjections"]
        self.assertEqual(len(work), 1)
        self.assertEqual(work[0]["id"], "work-v1")
        self.assertEqual(work[0]["researchProjectionIds"], ["research-v6"])
        self.assertEqual(
            work[0]["runs"][0]["terminalKnowledgeStateDigest"],
            self.target["stateDigest"],
        )


if __name__ == "__main__":
    unittest.main()
