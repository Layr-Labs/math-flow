from __future__ import annotations

import copy
import json
import tempfile
import unittest
from fractions import Fraction
from pathlib import Path

from math_flow.counterfactual_context import build_submission_evidence_manifest
from math_flow.errors import MathFlowError
from math_flow.joint_portfolio_serial_credit import (
    run_joint_portfolio_serial_credit_v1,
    validate_joint_portfolio_serial_credit_candidate_v1,
)
from math_flow.repository import sha256_json
from tests import test_joint_portfolio_serial_transition as transition_fixtures


class SerialCounterfactualProvider:
    def __init__(
        self,
        *,
        subject: str,
        claim_key: str,
        affected_program_ids: list[str],
        updates: list[dict[str, object]],
    ) -> None:
        self.subject = subject
        self.claim_key = claim_key
        self.affected_program_ids = affected_program_ids
        self.updates = updates
        self.calls: list[tuple[str, dict[str, object], tuple[object, ...]]] = []

    def __call__(self, *, stage, request, evidence_files):
        evidence = tuple(evidence_files)
        self.calls.append((stage, copy.deepcopy(request), evidence))
        if stage == "safe-facts":
            if not evidence:
                raise AssertionError("safe facts require current submission evidence")
            return {
                "facts": [
                    {
                        "id": "realized-result-condition",
                        "condition": "The accepted result holds in the realized same world.",
                        "actorVisibility": "withheld-until-independent-discovery",
                        "affectedNodeRefs": [
                            {"kind": "program", "id": program_id}
                            for program_id in self.affected_program_ids
                        ],
                        "acceptedClaimKeys": [self.claim_key],
                    }
                ],
                "assumptions": [
                    "The no-access community follows the exact pre-submission information policy."
                ],
            }
        if stage != "no-access":
            raise AssertionError(f"serial credit may not invoke {stage}")
        if evidence:
            raise AssertionError("no-access estimation received submission evidence")
        return {"updates": copy.deepcopy(self.updates)}


class JointPortfolioSerialCreditTests(unittest.TestCase):
    def setUp(self) -> None:
        fixture = transition_fixtures.JointPortfolioSerialTransitionTests(
            methodName="runTest"
        )
        fixture.setUp()
        self.fixture = fixture
        self.k1, self.k1_inputs = fixture.k1()
        self.k2, self.k2_inputs = fixture.k2(self.k1)
        self.k3, self.k3_inputs = fixture.k3(self.k2)

    def case(self, ordinal: int):
        if ordinal == 1:
            return {
                "subject": self.fixture.tx1,
                "baseState": self.fixture.origin,
                "baseAccounting": self.fixture.accounting_origin,
                "joint": self.k1,
                "inputs": self.k1_inputs,
                "judgment": "sha256:" + "1" * 64,
                "affected": [self.fixture.program1, "root"],
                "updates": [
                    {
                        "nodeRef": {"kind": "program", "id": self.fixture.program1},
                        "changes": {
                            "directWorkHours": "400",
                            "conditionalIncidence": "0.5",
                        },
                        "rationale": "Without access, the community performs the structural route before independent discovery.",
                        "evidenceRefs": ["safe-fact:realized-result-condition"],
                    },
                    {
                        "nodeRef": {"kind": "program", "id": "root"},
                        "changes": {"directWorkHours": "1100"},
                        "rationale": "The no-access root retains additional discovery and integration work.",
                        "evidenceRefs": ["safe-fact:realized-result-condition"],
                    },
                ],
                "expectedD": "200",
            }
        if ordinal == 2:
            return {
                "subject": self.fixture.tx2,
                "baseState": self.k1["postState"],
                "baseAccounting": self.k1["withAccessState"],
                "joint": self.k2,
                "inputs": self.k2_inputs,
                "judgment": "sha256:" + "2" * 64,
                "affected": [self.fixture.program2, "root"],
                "updates": [
                    {
                        "nodeRef": {"kind": "program", "id": self.fixture.program2},
                        "changes": {
                            "directWorkHours": "200",
                            "conditionalIncidence": "1",
                        },
                        "rationale": "Without access, the community performs the UV blocking package before rediscovery.",
                        "evidenceRefs": ["safe-fact:realized-result-condition"],
                    }
                ],
                "expectedD": "300",
            }
        return {
            "subject": self.fixture.tx3,
            "baseState": self.k2["postState"],
            "baseAccounting": self.k2["withAccessState"],
            "joint": self.k3,
            "inputs": self.k3_inputs,
            "judgment": "sha256:" + "3" * 64,
            "affected": ["root"],
            "updates": [],
            "expectedD": "50",
        }

    def manifest(self, case: dict[str, object]):
        evidence = case["inputs"]["evidence"]
        subject = str(case["subject"])
        files = {path: f"evidence:{subject}".encode() for path in evidence}
        return build_submission_evidence_manifest(
            problem_id=self.fixture.problem,
            subject_transaction_id=subject,
            contribution_path=f"problems/{self.fixture.problem}/contributions/{subject}",
            files=files,
            chunk_bytes=11,
        )

    def provider(
        self,
        case: dict[str, object],
        *,
        updates: list[dict[str, object]] | None = None,
    ) -> SerialCounterfactualProvider:
        claim_key = str(case["inputs"]["claims"][0]["claimKey"])
        return SerialCounterfactualProvider(
            subject=str(case["subject"]),
            claim_key=claim_key,
            affected_program_ids=list(case["affected"]),
            updates=copy.deepcopy(case["updates"] if updates is None else updates),
        )

    def run_credit(
        self,
        case: dict[str, object],
        provider: SerialCounterfactualProvider,
        *,
        checkpoint: Path | None = None,
        expected_frozen_candidate: object | None = None,
        joint_response: object | None = None,
    ) -> dict[str, object]:
        manifest, chunks = self.manifest(case)
        claim_key = str(case["inputs"]["claims"][0]["claimKey"])
        return run_joint_portfolio_serial_credit_v1(
            provider=provider,
            subject_transaction_id=str(case["subject"]),
            root_contract=self.fixture.contract,
            base_knowledge_state=case["baseState"],
            base_accounting_state=case["baseAccounting"],
            joint_response=(
                case["inputs"]["response"]
                if joint_response is None
                else joint_response
            ),
            semantic_packet=case["inputs"]["semantic"],
            authoring_packet=case["inputs"]["scope"],
            accepted_claims=case["inputs"]["claims"],
            accepted_claim_refs=[
                {
                    "transactionId": case["subject"],
                    "claimKey": claim_key,
                    "judgmentId": case["judgment"],
                    "assessmentDigest": "sha256:" + str(case["subject"])[0] * 64,
                }
            ],
            judgment_id=str(case["judgment"]),
            evidence_manifest=manifest,
            evidence_chunks=chunks,
            expected_frozen_candidate=expected_frozen_candidate,
            checkpoint_dir=checkpoint,
            descendant_depth=1,
        )

    def test_k1_k2_k3_each_freezes_wplus_and_allocates_positive_d_to_submission(self) -> None:
        observed = []
        for ordinal in (1, 2, 3):
            case = self.case(ordinal)
            provider = self.provider(case)
            result = self.run_credit(case, provider)
            self.assertEqual(
                [stage for stage, _, _ in provider.calls],
                ["safe-facts", "no-access"],
            )
            self.assertEqual(
                result["withAccessState"], case["joint"]["withAccessState"]
            )
            self.assertEqual(
                result["evaluation"]["workValueHours"], case["expectedD"]
            )
            candidate = validate_joint_portfolio_serial_credit_candidate_v1(
                result["creditCandidate"]
            )
            self.assertEqual(
                candidate["allocationTarget"],
                {"kind": "submission", "id": case["subject"]},
            )
            effect_total = sum(
                Fraction(str(effect["workReductionHours"]))
                for effect in candidate["nodeEffects"]
            )
            self.assertEqual(effect_total, Fraction(str(case["expectedD"])))
            observed.append(candidate["allocatedWorkHours"])
        self.assertEqual(observed, ["200", "300", "50"])

    def test_no_access_request_excludes_evidence_and_wplus_rationales(self) -> None:
        case = self.case(2)
        result = self.run_credit(case, self.provider(case))
        rendered = json.dumps(result["noAccessRequest"], sort_keys=True)
        # Exact evidence digests remain authoritative bindings; the raw
        # manifest, evidence body, and with-access patch must not cross the
        # no-access boundary.
        self.assertNotIn('"evidenceManifest":', rendered)
        self.assertNotIn('"submissionEvidence":', rendered)
        self.assertNotIn('"contentBase64":', rendered)
        self.assertNotIn('"withAccessPatch":', rendered)
        self.assertNotIn(
            str(case["inputs"]["response"]["topologyRationale"]), rendered
        )
        self.assertEqual(
            result["noAccessRequest"]["stageInput"]["frozenWithAccessState"],
            case["joint"]["withAccessState"],
        )

    def test_nonpositive_wminus_is_rejected_without_clamping(self) -> None:
        case = self.case(2)
        invalid_updates = [
            {
                "nodeRef": {"kind": "program", "id": self.fixture.program2},
                "changes": {
                    "directWorkHours": "0",
                    "conditionalIncidence": "1",
                },
                "rationale": "Deliberately invalid nonpositive counterfactual.",
                "evidenceRefs": ["safe-fact:realized-result-condition"],
            },
            {
                "nodeRef": {"kind": "program", "id": "root"},
                "changes": {"directWorkHours": "800"},
                "rationale": "Deliberately invalid nonpositive counterfactual.",
                "evidenceRefs": ["safe-fact:realized-result-condition"],
            },
        ]
        with self.assertRaisesRegex(MathFlowError, "strictly positive"):
            self.run_credit(case, self.provider(case, updates=invalid_updates))

    def test_tampered_frozen_candidate_fails_before_any_provider_call(self) -> None:
        case = self.case(2)
        first = self.run_credit(case, self.provider(case))
        tampered = copy.deepcopy(first["jointWithAccessCandidate"])
        tampered["withAccessStateDigest"] = "sha256:" + "f" * 64
        core = {key: value for key, value in tampered.items() if key != "candidateDigest"}
        tampered["candidateDigest"] = f"sha256:{sha256_json(core)}"
        provider = self.provider(case)
        with self.assertRaisesRegex(MathFlowError, "replay differs"):
            self.run_credit(
                case,
                provider,
                expected_frozen_candidate=tampered,
            )
        self.assertEqual(provider.calls, [])

    def test_stale_joint_response_fails_before_any_provider_call(self) -> None:
        case = self.case(2)
        stale = copy.deepcopy(case["inputs"]["response"])
        stale["baseStateDigest"] = "sha256:" + "0" * 64
        provider = self.provider(case)
        with self.assertRaises(MathFlowError):
            self.run_credit(case, provider, joint_response=stale)
        self.assertEqual(provider.calls, [])

    def test_checkpoint_reuses_safe_facts_and_invalidates_only_rejected_wminus(self) -> None:
        case = self.case(2)
        invalid_updates = [
            {
                "nodeRef": {"kind": "program", "id": self.fixture.program2},
                "changes": {
                    "directWorkHours": "0",
                    "conditionalIncidence": "1",
                },
                "rationale": "Deliberately invalid nonpositive counterfactual.",
                "evidenceRefs": ["safe-fact:realized-result-condition"],
            },
            {
                "nodeRef": {"kind": "program", "id": "root"},
                "changes": {"directWorkHours": "800"},
                "rationale": "Deliberately invalid nonpositive counterfactual.",
                "evidenceRefs": ["safe-fact:realized-result-condition"],
            },
        ]
        with tempfile.TemporaryDirectory() as temporary:
            checkpoint = Path(temporary) / "joint-serial-credit"
            with self.assertRaisesRegex(MathFlowError, "strictly positive"):
                self.run_credit(
                    case,
                    self.provider(case, updates=invalid_updates),
                    checkpoint=checkpoint,
                )
            retry = self.provider(case)
            result = self.run_credit(case, retry, checkpoint=checkpoint)
            self.assertEqual([stage for stage, _, _ in retry.calls], ["no-access"])
            self.assertEqual(result["creditCandidate"]["allocatedWorkHours"], "300")
            replay = self.provider(case)
            self.run_credit(
                case,
                replay,
                checkpoint=checkpoint,
                expected_frozen_candidate=result["jointWithAccessCandidate"],
            )
            self.assertEqual(replay.calls, [])


if __name__ == "__main__":
    unittest.main()
