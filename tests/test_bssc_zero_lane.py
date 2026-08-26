from __future__ import annotations

import copy
import json
import tempfile
import unittest
from pathlib import Path

from math_flow.bssc_zero_lane import (
    build_bssc_zero_lane_readiness_report,
    load_bssc_zero_lane_accepted_submissions,
    validate_bssc_zero_lane_readiness_report,
)
from math_flow.errors import MathFlowError
from math_flow.work_accounting_pipeline import (
    LocalCASObjectStore,
    advance_work_accounting_pipeline,
    initialize_work_accounting_pipeline,
)
from math_flow.research_topology import empty_research_program_state_v2
from math_flow.work_accounting import make_zero_work_accounting_state


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "tests/fixtures/bssc_work_replay_source_v1.json"
PROJECTION = ROOT / "protocol/runtime/inactive-openrouter-research-v4-projection.json"
CONTRACT = ROOT / "protocol/runtime/inactive-bssc-work-accounting-root-contract-v1.json"
ACCEPTED_ORDINALS = [3, 4, 5, 9, 10, 11, 12, 14, 15, 16, 17, 18, 19, 21, 24, 25]


class SixteenSubjectBuilder:
    def __init__(self) -> None:
        self.calls: list[str] = []

    def __call__(self, *, base_knowledge_state, submission):
        subject = str(submission["transactionId"])
        ordinal = int(submission["ordinal"])
        self.calls.append(subject)
        operations = []
        if "root/bssc" not in base_knowledge_state["programs"]:
            operations.extend(
                [
                    {
                        "entityKind": "thread",
                        "entityId": "root/bssc-entry",
                        "baseDigest": None,
                        "value": {
                            "id": "root/bssc-entry",
                            "programId": "root",
                            "title": "BSSC program entry",
                            "summary": "Enter the fixture BSSC research program.",
                            "kind": "research",
                            "status": "active",
                            "expectedExposure": "1",
                            "conditions": [],
                            "sourceTransactionIds": [subject],
                        },
                    },
                    {
                        "entityKind": "program",
                        "entityId": "root/bssc",
                        "baseDigest": None,
                        "value": {
                            "id": "root/bssc",
                            "parentId": "root",
                            "title": "BSSC fixture program",
                            "objective": "Resolve the BSSC fixture objective.",
                            "status": "active",
                            "parentThreadIds": ["root/bssc-entry"],
                            "sourceTransactionIds": [subject],
                            "lineage": [],
                        },
                    },
                    {
                        "entityKind": "thread",
                        "entityId": "root/bssc/unstructured-search",
                        "baseDigest": None,
                        "value": {
                            "id": "root/bssc/unstructured-search",
                            "programId": "root/bssc",
                            "title": "Unstructured search",
                            "summary": "Work not yet decomposed in the BSSC fixture.",
                            "kind": "unstructured",
                            "status": "active",
                            "expectedExposure": "1",
                            "conditions": [],
                            "sourceTransactionIds": [subject],
                        },
                    },
                ]
            )
            direct_thread = "root/bssc/unstructured-search"
        else:
            direct_thread = f"root/bssc/line-{ordinal}"
            operations.append(
                {
                    "entityKind": "thread",
                    "entityId": direct_thread,
                    "baseDigest": None,
                    "value": {
                        "id": direct_thread,
                        "programId": "root/bssc",
                        "title": f"Fixture line {ordinal}",
                        "summary": "Track one accepted BSSC fixture contribution.",
                        "kind": "research",
                        "status": "active",
                        "expectedExposure": "1",
                        "conditions": [],
                        "sourceTransactionIds": [subject],
                    },
                }
            )
        item_id = f"root/bssc/result-{ordinal}"
        operations.append(
            {
                "entityKind": "item",
                "entityId": item_id,
                "baseDigest": None,
                "value": {
                    "id": item_id,
                    "programId": "root/bssc",
                    "type": "result",
                    "title": f"Fixture result {ordinal}",
                    "summary": "Represent the exact accepted claim in this fixture.",
                    "claimRefs": [
                        {"transactionId": subject, "claimKey": item["claimKey"]}
                        for item in submission["acceptedClaims"]
                    ],
                    "sourceTransactionIds": [subject],
                    "dependencyItemIds": [],
                },
            }
        )
        return {
            "schemaVersion": 1,
            "subjectTransactionId": subject,
            "baseStateDigest": base_knowledge_state["stateDigest"],
            "contentOperations": operations,
            "topologyOperations": [],
            "contribution": {
                "claimKeys": [item["claimKey"] for item in submission["acceptedClaims"]],
                "directProgramId": "root/bssc",
                "directThreadIds": [direct_thread],
                "itemIds": [item_id],
            },
            "placementAudit": {
                "basis": "local-objective",
                "rationale": "The fixture contribution advances the BSSC local objective.",
                "relatedProgramIds": ["root/bssc"],
            },
            "topologyRationale": None,
        }


class SixteenSubjectWorkProvider:
    def __init__(self, subjects: list[str]) -> None:
        self.positions = {subject: index for index, subject in enumerate(subjects, 1)}
        self.calls: list[tuple[str, str]] = []

    def __call__(self, *, stage, request, evidence_files):
        subject = str(request["subjectTransactionId"])
        self.calls.append((subject, stage))
        if stage == "safe-facts":
            position = self.positions[subject]
            affected = [
                {"kind": "thread", "id": "root/unstructured-search"},
                (
                    {"kind": "program", "id": "root/bssc"}
                    if position == 1
                    else {
                        "kind": "thread",
                        "id": f"root/bssc/line-{ACCEPTED_ORDINALS[position - 1]}",
                    }
                ),
            ]
            if position == 1:
                affected.extend(
                    [
                        {"kind": "thread", "id": "root/bssc-entry"},
                        {
                            "kind": "thread",
                            "id": "root/bssc/unstructured-search",
                        },
                    ]
                )
            return {
                "facts": [
                    {
                        "id": "fixture-realized-world",
                        "condition": "A hidden fixture condition holds in the realized world.",
                        "actorVisibility": "withheld-until-independent-discovery",
                        "affectedNodeRefs": affected,
                        "acceptedClaimKeys": [
                            item["claimKey"]
                            for item in request["stageInput"]["acceptedClaimRefs"]
                        ],
                    }
                ],
                "assumptions": ["Use competent human researcher hours."],
            }
        updates = []
        for required in request["requiredPrimitiveUpdates"]:
            changes = {}
            inactive = "inactive-zeroing" in required["reasons"]
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
                    "rationale": "Estimate every topology-required fixture primitive.",
                    "evidenceRefs": [f"fixture:{stage}"],
                }
            )
        position = self.positions[subject]
        updates.append(
            {
                "nodeRef": {"kind": "thread", "id": "root/unstructured-search"},
                "changes": {
                    "directWorkHours": str(
                        100 + position if stage == "no-access" else 90 + position
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


class BSSCZeroLaneTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.source = json.loads(SOURCE.read_text(encoding="utf-8"))
        cls.projection = json.loads(PROJECTION.read_text(encoding="utf-8"))
        cls.contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
        cls.report = build_bssc_zero_lane_readiness_report(
            ROOT,
            replay_source=cls.source,
            knowledge_projection=cls.projection,
            root_contract=cls.contract,
        )

    def test_all_accepted_submissions_run_from_zero(self) -> None:
        report = validate_bssc_zero_lane_readiness_report(self.report)
        self.assertEqual(report["canonicalSubmissionCount"], 25)
        self.assertEqual(report["acceptedSubmissionCount"], 16)
        self.assertEqual(report["excludedSubmissionCount"], 9)
        self.assertEqual(
            [
                item["ledgerOrdinal"]
                for item in report["subjects"]
                if item["validityStatus"] == "accepted"
            ],
            ACCEPTED_ORDINALS,
        )
        self.assertEqual(
            [item["requiredCount"] for item in report["providerRequirements"]],
            [16, 16],
        )
        self.assertFalse(
            report["invariants"]["historicalV5KnowledgeStatesReused"]
        )

    def test_zero_origin_can_initialize_against_all_resolved_submissions(self) -> None:
        report = self.report
        knowledge = empty_research_program_state_v2("bssc-sum-capacity")
        accounting = make_zero_work_accounting_state(
            root_contract=self.contract,
            knowledge_state=knowledge,
        )
        resolved = [item["transactionId"] for item in report["subjects"]]
        with tempfile.TemporaryDirectory() as temporary:
            pipeline = initialize_work_accounting_pipeline(
                LocalCASObjectStore(Path(temporary)),
                ROOT,
                problem="bssc-sum-capacity",
                projection_id="openrouter-work-accounting-v1",
                projection_spec_digest="sha256:" + "a" * 64,
                root_contract=self.contract,
                initial_knowledge_state=knowledge,
                initial_accounting_state=accounting,
                resolved_submission_ids=resolved,
                head=self.source["mainCommit"],
            )
        self.assertEqual(pipeline["completedTransitions"], [])
        self.assertEqual(pipeline["formedKnowledgeStateDigest"], knowledge["stateDigest"])

    def test_exact_accepted_inputs_drive_sixteen_first_pass_evaluations(self) -> None:
        submissions = load_bssc_zero_lane_accepted_submissions(ROOT, self.source)
        self.assertEqual(
            [item.ordinal for item in submissions],
            ACCEPTED_ORDINALS,
        )
        knowledge = empty_research_program_state_v2("bssc-sum-capacity")
        accounting = make_zero_work_accounting_state(
            root_contract=self.contract,
            knowledge_state=knowledge,
        )
        resolved = [item["transactionId"] for item in self.report["subjects"]]
        with tempfile.TemporaryDirectory() as temporary:
            temporary_root = Path(temporary)
            store = LocalCASObjectStore(temporary_root / "store")
            initialize_work_accounting_pipeline(
                store,
                ROOT,
                problem="bssc-sum-capacity",
                projection_id="openrouter-work-accounting-v1",
                projection_spec_digest="sha256:" + "a" * 64,
                root_contract=self.contract,
                initial_knowledge_state=knowledge,
                initial_accounting_state=accounting,
                resolved_submission_ids=resolved,
                head=self.source["mainCommit"],
            )
            builder = SixteenSubjectBuilder()
            work = SixteenSubjectWorkProvider(
                [item.transaction_id for item in submissions]
            )
            final = advance_work_accounting_pipeline(
                store,
                ROOT,
                projection_id="openrouter-work-accounting-v1",
                problem="bssc-sum-capacity",
                builder_provider=builder,
                work_provider=work,
                accepted_submissions=submissions,
                scratch_root=temporary_root / "scratch",
                head=self.source["mainCommit"],
                as_of=100,
            )
        expected = [item.transaction_id for item in submissions]
        self.assertEqual(builder.calls, expected)
        self.assertEqual(
            [item["subjectTransactionId"] for item in final["completedTransitions"]],
            expected,
        )
        self.assertEqual(len(work.calls), 48)
        self.assertEqual(final["phase"], "ready")

    def test_contract_or_report_tampering_fails_closed(self) -> None:
        projection = copy.deepcopy(self.projection)
        projection["description"] = "A different inactive candidate."
        with self.assertRaisesRegex(MathFlowError, "does not bind"):
            build_bssc_zero_lane_readiness_report(
                ROOT,
                replay_source=self.source,
                knowledge_projection=projection,
                root_contract=self.contract,
            )
        report = copy.deepcopy(self.report)
        report["source"]["historicalKnowledgeStatesReused"] = True
        with self.assertRaisesRegex(MathFlowError, "invariants are unsafe"):
            validate_bssc_zero_lane_readiness_report(report)


if __name__ == "__main__":
    unittest.main()
