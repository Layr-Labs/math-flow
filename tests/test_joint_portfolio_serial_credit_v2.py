from __future__ import annotations

import copy
import json
import tempfile
import unittest
from fractions import Fraction
from pathlib import Path

from math_flow.counterfactual_context import build_submission_evidence_manifest
from math_flow.errors import MathFlowError
from math_flow.joint_portfolio_serial_credit_v2 import (
    run_joint_portfolio_serial_credit_v2,
    validate_joint_portfolio_serial_credit_candidate_v2,
)
from math_flow.repository import sha256_json
from tests import test_joint_portfolio_serial_transition_v2 as fixtures


class CounterfactualProviderV2:
    def __init__(self, *, subject: str, claim: str, affected: list[str], updates: list[dict[str, object]]) -> None:
        self.subject, self.claim, self.affected, self.updates = subject, claim, affected, updates
        self.calls: list[tuple[str, dict[str, object], tuple[object, ...]]] = []

    def __call__(self, *, stage, request, evidence_files):
        evidence = tuple(evidence_files)
        self.calls.append((stage, copy.deepcopy(request), evidence))
        if stage == "safe-facts":
            if not evidence:
                raise AssertionError("safe facts need exact evidence")
            return {
                "facts": [{
                    "id": "realized-result-condition",
                    "condition": "The accepted result holds in the realized same world.",
                    "actorVisibility": "withheld-until-independent-discovery",
                    "affectedNodeRefs": [{"kind": "program", "id": program} for program in self.affected],
                    "acceptedClaimKeys": [self.claim],
                }],
                "assumptions": ["The no-access community follows the pre-submission policy."],
            }
        if stage != "no-access" or evidence:
            raise AssertionError("invalid counterfactual stage boundary")
        return {"updates": copy.deepcopy(self.updates)}


class JointPortfolioSerialCreditV2Tests(unittest.TestCase):
    def setUp(self) -> None:
        fixture = fixtures.JointPortfolioSerialTransitionV2Tests(methodName="runTest")
        fixture.setUp()
        self.fixture = fixture
        self.k1, self.k1_inputs = fixture.k1()
        self.k2, self.k2_inputs = fixture.k2(self.k1)
        self.k3, self.k3_inputs = fixture.k3(self.k2)

    def case(self, ordinal: int) -> dict[str, object]:
        if ordinal == 1:
            joint, inputs, subject, claim, expected = self.k1, self.k1_inputs, fixtures.TX1, f"{fixtures.PROBLEM}/k1-code-induced", "200"
            affected = [fixtures.PROGRAM1, "root"]
            updates = [
                {"nodeRef": {"kind": "program", "id": fixtures.PROGRAM1}, "changes": {"directWorkHours": "200", "conditionalIncidence": "0.5"}, "rationale": "No-access route still needs the K1 work.", "evidenceRefs": ["safe-fact:realized-result-condition"]},
                {"nodeRef": {"kind": "program", "id": "root"}, "changes": {"directWorkHours": "1200"}, "rationale": "No-access root retains discovery work.", "evidenceRefs": ["safe-fact:realized-result-condition"]},
            ]
        elif ordinal == 2:
            joint, inputs, subject, claim, expected = self.k2, self.k2_inputs, fixtures.TX2, f"{fixtures.PROBLEM}/k2-uv-chain", "300"
            affected = [fixtures.PROGRAM2, "root"]
            updates = [
                {"nodeRef": {"kind": "program", "id": fixtures.PROGRAM2}, "changes": {"directWorkHours": "200", "conditionalIncidence": "1"}, "rationale": "Without K2 the UV package remains.", "evidenceRefs": ["safe-fact:realized-result-condition"]},
            ]
        else:
            joint, inputs, subject, claim, expected = self.k3, self.k3_inputs, fixtures.TX3, f"{fixtures.PROBLEM}/k3-uv-verification", "50"
            affected = [fixtures.PROGRAM2, "root"]
            updates = []
        evidence_chunks = {path: f"evidence:{subject}".encode() for path in inputs["evidence"]}
        manifest, chunks = build_submission_evidence_manifest(
            problem_id=fixtures.PROBLEM, subject_transaction_id=subject,
            contribution_path=f"problems/{fixtures.PROBLEM}/contributions/{subject}",
            files=evidence_chunks, chunk_bytes=11,
        )
        accepted_refs = [{"transactionId": subject, "claimKey": claim, "judgmentId": inputs["judgment"], "assessmentDigest": "sha256:" + subject[0] * 64}]
        return {"joint": joint, "inputs": inputs, "subject": subject, "claim": claim, "expected": expected, "affected": affected, "updates": updates, "chunks": chunks, "manifest": manifest, "acceptedRefs": accepted_refs}

    def provider(self, case: dict[str, object], updates: list[dict[str, object]] | None = None) -> CounterfactualProviderV2:
        return CounterfactualProviderV2(subject=case["subject"], claim=case["claim"], affected=case["affected"], updates=updates if updates is not None else case["updates"])

    def run_credit(self, case: dict[str, object], provider: CounterfactualProviderV2, **extra):
        inputs = case["inputs"]
        joint_response = extra.pop("joint_response", inputs["response"])
        return run_joint_portfolio_serial_credit_v2(
            provider=provider, subject_transaction_id=case["subject"], root_contract=self.fixture.contract,
            base_knowledge_state=inputs["state"], base_accounting_state=inputs["accounting"],
            base_boundary_state=inputs["boundaries"], joint_response=joint_response,
            semantic_packet=inputs["packet"], authoring_packet=inputs["scope"],
            accepted_claims=inputs["claims"], accepted_claim_refs=case["acceptedRefs"],
            judgment_id=inputs["judgment"], evidence_manifest=case["manifest"],
            evidence_chunks=case["chunks"], **extra,
        )

    def test_k1_k2_k3_freeze_boundary_aware_wplus_and_allocate_to_submission(self) -> None:
        for ordinal in (1, 2, 3):
            case = self.case(ordinal)
            result = self.run_credit(case, self.provider(case))
            candidate = validate_joint_portfolio_serial_credit_candidate_v2(result["creditCandidate"])
            self.assertEqual(candidate["allocatedWorkHours"], case["expected"])
            self.assertEqual(candidate["allocationTarget"], {"kind": "submission", "id": case["subject"]})
            self.assertEqual(candidate["targetBoundaryStateDigest"], case["joint"]["boundaryState"]["stateDigest"])
            self.assertEqual(sum((Fraction(effect["workReductionHours"]) for effect in candidate["nodeEffects"]), Fraction(0)), Fraction(case["expected"]))

    def test_nonpositive_wminus_is_rejected_without_clamp(self) -> None:
        case = self.case(2)
        updates = [
            {"nodeRef": {"kind": "program", "id": fixtures.PROGRAM2}, "changes": {"directWorkHours": "0", "conditionalIncidence": "1"}, "rationale": "Invalid no reduction.", "evidenceRefs": ["safe-fact:realized-result-condition"]},
            {"nodeRef": {"kind": "program", "id": "root"}, "changes": {"directWorkHours": "800"}, "rationale": "Invalid no reduction.", "evidenceRefs": ["safe-fact:realized-result-condition"]},
        ]
        with self.assertRaisesRegex(MathFlowError, "strictly positive"):
            self.run_credit(case, self.provider(case, updates))

    def test_tampered_frozen_boundary_binding_fails_before_calls(self) -> None:
        case = self.case(1)
        first = self.run_credit(case, self.provider(case))
        frozen = copy.deepcopy(first["jointWithAccessCandidate"])
        frozen["targetBoundaryStateDigest"] = "sha256:" + "f" * 64
        core = {key: value for key, value in frozen.items() if key != "candidateDigest"}
        frozen["candidateDigest"] = f"sha256:{sha256_json(core)}"
        provider = self.provider(case)
        with self.assertRaisesRegex(MathFlowError, "differs from expected"):
            self.run_credit(case, provider, expected_frozen_candidate=frozen)
        self.assertEqual(provider.calls, [])

    def test_stale_joint_response_fails_before_calls(self) -> None:
        case = self.case(2)
        stale = copy.deepcopy(case["inputs"]["response"])
        stale["baseAccountingStateDigest"] = "sha256:" + "0" * 64
        provider = self.provider(case)
        with self.assertRaisesRegex(MathFlowError, "stale baseAccountingStateDigest"):
            self.run_credit(case, provider, joint_response=stale)
        self.assertEqual(provider.calls, [])

    def test_rejected_wminus_reuses_safe_facts_and_invalidates_only_no_access(self) -> None:
        case = self.case(2)
        invalid_updates = [
            {
                "nodeRef": {"kind": "program", "id": fixtures.PROGRAM2},
                "changes": {"directWorkHours": "0", "conditionalIncidence": "1"},
                "rationale": "Invalid no reduction.",
                "evidenceRefs": ["safe-fact:realized-result-condition"],
            },
            {
                "nodeRef": {"kind": "program", "id": "root"},
                "changes": {"directWorkHours": "800"},
                "rationale": "Invalid no reduction.",
                "evidenceRefs": ["safe-fact:realized-result-condition"],
            },
        ]
        with tempfile.TemporaryDirectory() as directory:
            checkpoint = Path(directory) / "joint-credit-v2"
            rejected = self.provider(case, invalid_updates)
            with self.assertRaisesRegex(MathFlowError, "strictly positive"):
                self.run_credit(case, rejected, checkpoint_dir=checkpoint)
            self.assertEqual(
                [stage for stage, _, _ in rejected.calls],
                ["safe-facts", "no-access"],
            )
            retry = self.provider(case)
            accepted = self.run_credit(case, retry, checkpoint_dir=checkpoint)
            self.assertEqual([stage for stage, _, _ in retry.calls], ["no-access"])
            self.assertEqual(accepted["creditCandidate"]["allocatedWorkHours"], "300")

    def test_checkpoint_replays_both_counterfactual_stages(self) -> None:
        case = self.case(3)
        with tempfile.TemporaryDirectory() as directory:
            first_provider = self.provider(case)
            first = self.run_credit(case, first_provider, checkpoint_dir=Path(directory))
            self.assertEqual([stage for stage, _, _ in first_provider.calls], ["safe-facts", "no-access"])
            replay_provider = self.provider(case)
            replay = self.run_credit(case, replay_provider, checkpoint_dir=Path(directory), expected_frozen_candidate=first["jointWithAccessCandidate"])
            self.assertEqual(replay_provider.calls, [])
            self.assertEqual(replay["creditCandidate"], first["creditCandidate"])

    def test_no_access_request_has_no_raw_evidence_or_joint_rationales(self) -> None:
        case = self.case(2)
        result = self.run_credit(case, self.provider(case))
        rendered = json.dumps(result["noAccessRequest"], sort_keys=True)
        for key in ('"evidenceManifest":', '"contentBase64":', '"withAccessPatch":'):
            self.assertNotIn(key, rendered)
        self.assertNotIn(str(case["inputs"]["response"]["topologyRationale"]), rendered)


if __name__ == "__main__":
    unittest.main()
