from __future__ import annotations

import copy
import tempfile
import unittest
from pathlib import Path

from math_flow.counterfactual_context import (
    build_counterfactual_safe_facts,
    build_impact_subgraph_context,
    build_no_access_stage_input,
    build_submission_evidence_manifest,
    validate_impact_subgraph_context,
)
from math_flow.errors import MathFlowError
from math_flow.research_builder_v7 import (
    apply_research_builder_v7_transition,
    empty_research_program_state_v3,
)
from math_flow.research_topology import empty_research_program_state_v2
from math_flow.work_accounting import (
    bind_patch_to_state,
    make_root_contract,
    make_work_accounting_patch,
    make_zero_work_accounting_state,
    materialize_submission_work_value,
)
from math_flow.work_accounting_pipeline_v3 import (
    AcceptedWorkSubmission,
    LocalCASObjectStore,
    _materialize_builder_result,
    normalize_work_accounting_submission,
)
from math_flow.work_accounting_knowledge import (
    derive_work_accounting_topology_alignment,
)


PROBLEM = "two-entity-accounting"
TX = "a" * 40
JUDGMENT = "sha256:" + "b" * 64
ASSESSMENT = "sha256:" + "c" * 64
PROJECTION_SPEC = "sha256:" + "d" * 64


def _accepted_claims() -> list[dict[str, object]]:
    return [
        {
            "claimKey": "main",
            "statement": "The accepted local reduction holds.",
            "dependencyTransactionIds": [],
        }
    ]


def _claim_refs() -> list[dict[str, str]]:
    return [
        {
            "transactionId": TX,
            "claimKey": "main",
            "judgmentId": JUDGMENT,
            "assessmentDigest": ASSESSMENT,
        }
    ]


def _transition(base: dict[str, object]) -> dict[str, object]:
    program_id = "program/local-line"
    result_id = "result/local-reduction"
    return {
        "schemaVersion": 1,
        "subjectTransactionId": TX,
        "baseStateDigest": base["stateDigest"],
        "contentOperations": [
            {
                "entityKind": "program",
                "entityId": program_id,
                "baseDigest": None,
                "value": {
                    "id": program_id,
                    "parentId": "root",
                    "title": "Local line",
                    "objective": "Resolve the local reduction line.",
                    "currentStateSummary": "A local reduction is established.",
                    "localResidualSummary": "The terminal local bound remains open.",
                    "status": "active",
                    "intermediateResultIds": [result_id],
                    "sourceTransactionIds": [TX],
                    "lineage": [],
                },
            },
            {
                "entityKind": "intermediateResult",
                "entityId": result_id,
                "baseDigest": None,
                "value": {
                    "id": result_id,
                    "primaryProgramId": program_id,
                    "relatedProgramIds": [],
                    "title": "Local reduction",
                    "statement": "The local case reduces to a finite obstruction.",
                    "scopeQualifications": ["Under the accepted finite hypothesis."],
                    "support": {
                        "proofs": ["A direct proof establishes the reduction."],
                        "methods": ["Normalize before applying the obstruction."],
                        "computations": [],
                        "tools": [],
                        "artifactRefs": [],
                        "attestationRefs": [],
                    },
                    "dependencyResultIds": [],
                    "claimRefs": [{"transactionId": TX, "claimKey": "main"}],
                    "sourceTransactionIds": [TX],
                    "judgmentIds": [JUDGMENT],
                    "status": "active",
                    "supersededByResultIds": [],
                },
            },
        ],
        "topologyOperations": [],
        "contribution": {
            "claimKeys": ["main"],
            "directProgramIds": [program_id],
            "intermediateResultIds": [result_id],
        },
        "placementAudit": {
            "basis": "local-objective",
            "rationale": "The accepted result advances the narrow local line.",
            "relatedProgramIds": [program_id],
        },
        "topologyRationale": None,
    }


def _research_transition() -> tuple[dict[str, object], dict[str, object]]:
    before = empty_research_program_state_v3(PROBLEM)
    reduced = apply_research_builder_v7_transition(
        before,
        _transition(before),
        accepted_claims=_accepted_claims(),
        judgment_id=JUDGMENT,
    )
    return before, reduced


def _contract() -> dict[str, object]:
    return make_root_contract(
        problem_id=PROBLEM,
        knowledge_projection_id="two-entity-knowledge",
        knowledge_projection_spec_digest=PROJECTION_SPEC,
        objective="Resolve the fixture objective.",
        terminal_condition="A complete proof or disproof is established.",
        tool_baseline="Conventional mathematical literature and local computation.",
        reference_community_description="Competent human mathematical researchers.",
        researcher_qualification="Researchers qualified for the local program.",
    )


class StaticBuilderV7:
    def __call__(self, *, base_knowledge_state, submission):
        self.base = copy.deepcopy(base_knowledge_state)
        self.submission = copy.deepcopy(submission)
        return _transition(dict(base_knowledge_state))


class TwoEntityWorkAccountingTests(unittest.TestCase):
    def setUp(self) -> None:
        self.before, self.reduced = _research_transition()
        self.after = self.reduced["postState"]
        contribution_path = f"problems/{PROBLEM}/contributions/local-reduction"
        self.manifest, self.chunks = build_submission_evidence_manifest(
            problem_id=PROBLEM,
            subject_transaction_id=TX,
            contribution_path=contribution_path,
            files={
                f"{contribution_path}/README.md": (
                    b"Accepted mathematical contribution with a complete local argument."
                )
            },
        )

    def _safe_facts(self) -> dict[str, object]:
        return build_counterfactual_safe_facts(
            problem_id=PROBLEM,
            subject_transaction_id=TX,
            accepted_claim_refs=_claim_refs(),
            research_state=self.after,
            evidence_manifest=self.manifest,
            evidence_chunks=self.chunks,
            extracted={
                "facts": [
                    {
                        "id": "finite-obstruction",
                        "condition": "A finite obstruction governs the local line.",
                        "actorVisibility": "withheld-until-independent-discovery",
                        "affectedNodeRefs": [
                            {"kind": "program", "id": "program/local-line"}
                        ],
                        "acceptedClaimKeys": ["main"],
                    }
                ],
                "assumptions": [],
            },
        )

    def test_state_v3_accounting_topology_contains_programs_only(self) -> None:
        zero = make_zero_work_accounting_state(
            root_contract=_contract(), knowledge_state=self.before
        )
        self.assertEqual(
            [annotation["nodeRef"] for annotation in zero["annotations"]],
            [{"kind": "program", "id": "root"}],
        )

        no_patch = bind_patch_to_state(
            make_work_accounting_patch(
                problem_id=PROBLEM,
                subject_transaction_id=TX,
                evaluation_mode="no-access",
                root_contract_digest=_contract()["rootContractDigest"],
                base_accounting_state_digest=zero["stateDigest"],
                base_knowledge_state_digest=self.before["stateDigest"],
                target_knowledge_state_digest=self.after["stateDigest"],
                topology_alignment_digest=self.reduced["topologyAlignment"][
                    "alignmentDigest"
                ],
                updates=[
                    {
                        "nodeRef": {"kind": "program", "id": "program/local-line"},
                        "changes": {
                            "directWorkHours": "5",
                            "conditionalIncidence": "1",
                        },
                        "rationale": "The line still requires five hours without access.",
                        "evidenceRefs": ["estimate:no-access"],
                    }
                ],
            ),
            zero,
        )
        with_patch = bind_patch_to_state(
            make_work_accounting_patch(
                problem_id=PROBLEM,
                subject_transaction_id=TX,
                evaluation_mode="with-access",
                root_contract_digest=_contract()["rootContractDigest"],
                base_accounting_state_digest=zero["stateDigest"],
                base_knowledge_state_digest=self.before["stateDigest"],
                target_knowledge_state_digest=self.after["stateDigest"],
                topology_alignment_digest=self.reduced["topologyAlignment"][
                    "alignmentDigest"
                ],
                updates=[
                    {
                        "nodeRef": {"kind": "program", "id": "program/local-line"},
                        "changes": {
                            "directWorkHours": "3",
                            "conditionalIncidence": "1",
                        },
                        "rationale": "The accepted reduction leaves three hours of work.",
                        "evidenceRefs": ["estimate:with-access"],
                    }
                ],
            ),
            zero,
        )
        no_state, with_state, evaluation = materialize_submission_work_value(
            base_state=zero,
            no_access_patch=no_patch,
            with_access_patch=with_patch,
            root_contract=_contract(),
            base_knowledge_state=self.before,
            target_knowledge_state=self.after,
            topology_alignment=self.reduced["topologyAlignment"],
        )
        self.assertEqual(no_state["totalWorkHours"], "5")
        self.assertEqual(with_state["totalWorkHours"], "3")
        self.assertEqual(evaluation["workValueHours"], "2")
        self.assertTrue(
            all(
                annotation["nodeRef"]["kind"] == "program"
                for annotation in with_state["annotations"]
            )
        )

    def test_impact_context_v2_exposes_only_structural_result_metadata(self) -> None:
        safe = self._safe_facts()
        context = build_impact_subgraph_context(
            problem_id=PROBLEM,
            subject_transaction_id=TX,
            accepted_claim_refs=_claim_refs(),
            research_state=self.after,
            seed_node_refs=[{"kind": "program", "id": "program/local-line"}],
        )
        self.assertEqual(context["schemaVersion"], 2)
        self.assertEqual(context["expansionPolicy"]["allowedKinds"], ["program"])
        self.assertNotIn("semanticItemRefs", context)
        semantic = context["semanticIntermediateResultRefs"]
        self.assertEqual(len(semantic), 1)
        self.assertEqual(
            set(semantic[0]),
            {
                "intermediateResultId",
                "primaryProgramRef",
                "relatedProgramRefs",
                "status",
                "claimRefs",
                "dependencyResultIds",
                "recordDigest",
            },
        )
        for prohibited in ("title", "statement", "scopeQualifications", "support"):
            self.assertNotIn(prohibited, semantic[0])
        validate_impact_subgraph_context(context)
        no_access = build_no_access_stage_input(
            safe_facts=safe,
            impact_context=context,
            research_state=self.after,
        )
        self.assertEqual(no_access["impactContext"], context)

        leaked = copy.deepcopy(context)
        leaked["semanticIntermediateResultRefs"][0]["statement"] = "Leaked result"
        with self.assertRaisesRegex(MathFlowError, "missing or unexpected fields"):
            validate_impact_subgraph_context(leaked)

    def test_pipeline_materializes_v7_state_alignment_and_handoff(self) -> None:
        submission = AcceptedWorkSubmission(
            transaction_id=TX,
            ordinal=1,
            accepted_claims=_accepted_claims(),
            judgment_id=JUDGMENT,
            accepted_claim_refs=_claim_refs(),
            evidence_manifest=self.manifest,
            evidence_chunks=self.chunks,
        )
        normalized, _ = normalize_work_accounting_submission(submission, PROBLEM)
        provider = StaticBuilderV7()
        with tempfile.TemporaryDirectory() as directory:
            result, post, alignment, handoff = _materialize_builder_result(
                LocalCASObjectStore(Path(directory) / "cas"),
                provider,
                base_knowledge=self.before,
                submission=normalized,
                crash_hook=None,
            )
        self.assertEqual(post, self.after)
        self.assertEqual(alignment["schemaVersion"], 2)
        self.assertEqual(handoff["schemaVersion"], 2)
        self.assertEqual(handoff["accountingNodeKinds"], ["program"])
        self.assertEqual(handoff["semanticLeafKinds"], ["intermediateResult"])
        self.assertEqual(result["afterKnowledgeStateDigest"], post["stateDigest"])

    def test_program_thread_alignment_replay_does_not_cross_into_v3(self) -> None:
        legacy = empty_research_program_state_v2(PROBLEM)
        with self.assertRaisesRegex(MathFlowError, "knowledge-state versions"):
            derive_work_accounting_topology_alignment(legacy, self.after)


if __name__ == "__main__":
    unittest.main()
