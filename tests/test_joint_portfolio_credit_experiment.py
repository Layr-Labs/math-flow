from __future__ import annotations

import copy
import json
import tempfile
import unittest
from pathlib import Path

from math_flow.counterfactual_context import build_submission_evidence_manifest
from math_flow.errors import MathFlowError
from math_flow.joint_portfolio_credit_experiment import (
    run_joint_portfolio_credit_candidate,
    validate_joint_portfolio_credit_candidate,
)


ROOT = Path(__file__).resolve().parents[1]
EXPERIMENT = ROOT / "protocol/experiments/bssc-joint-portfolio-wplus-k2-v3"
SUBJECT = "f236017c62c67ce4218c1f81ea34134f0954b556"
CLAIM = "bssc-sum-capacity/uv-product-branchwise-additivity"
JUDGMENT = "sha256:" + "2" * 64
ASSESSMENT = "sha256:" + "3" * 64
NEW_PROGRAM = "program-bssc-uv-product-branchwise-additivity"


class CounterfactualProvider:
    def __init__(self, *, nonpositive: bool = False) -> None:
        self.nonpositive = nonpositive
        self.calls: list[tuple[str, dict[str, object], tuple[object, ...]]] = []

    def __call__(self, *, stage, request, evidence_files):
        evidence = tuple(evidence_files)
        self.calls.append((stage, copy.deepcopy(request), evidence))
        if stage == "safe-facts":
            if not evidence:
                raise AssertionError("safe-fact extraction requires exact submission evidence")
            return {
                "facts": [
                    {
                        "id": "uv-package-is-resolved",
                        "condition": "The stated UV scalar package has a valid resolution in the realized world.",
                        "actorVisibility": "withheld-until-independent-discovery",
                        "affectedNodeRefs": [{"kind": "program", "id": "root"}],
                        "acceptedClaimKeys": [CLAIM],
                    }
                ],
                "assumptions": [
                    "The counterfactual community follows the fixed pre-submission policy."
                ],
            }
        if stage != "no-access":
            raise AssertionError(f"joint completion must not regenerate W+: {stage}")
        if evidence:
            raise AssertionError("no-access estimation received submission evidence")
        updates = [
            {
                "nodeRef": {"kind": "program", "id": NEW_PROGRAM},
                "changes": {
                    "directWorkHours": "0" if self.nonpositive else "400",
                    "conditionalIncidence": "1" if self.nonpositive else "0.5",
                },
                "rationale": "Estimate independent discovery work on the realized post-state topology.",
                "evidenceRefs": ["safe-fact:uv-package-is-resolved"],
            }
        ]
        if self.nonpositive:
            updates.append(
                {
                    "nodeRef": {"kind": "program", "id": "root"},
                    "changes": {"directWorkHours": "3400"},
                    "rationale": "A deliberately invalid low counterfactual for the rejection test.",
                    "evidenceRefs": ["safe-fact:uv-package-is-resolved"],
                }
            )
        return {"updates": updates}


class JointPortfolioCreditExperimentTests(unittest.TestCase):
    def setUp(self) -> None:
        self.base = json.loads(
            (EXPERIMENT / "fixtures/k1-post-state.json").read_text(encoding="utf-8")
        )
        self.base_accounting = json.loads(
            (EXPERIMENT / "fixtures/k1-with-access-state.json").read_text(
                encoding="utf-8"
            )
        )
        self.contract = json.loads(
            (
                ROOT
                / "protocol/experiments/bssc-joint-portfolio-wplus-k1-v2/root-contract-v2.json"
            ).read_text(encoding="utf-8")
        )
        self.packet = json.loads(
            (EXPERIMENT / "fixed-semantic-packet-v3.json").read_text(encoding="utf-8")
        )
        self.response = json.loads(
            (
                EXPERIMENT
                / "fixtures/successful-response-run-33564954137.json"
            ).read_text(encoding="utf-8")
        )
        self.claims = [
            {
                "claimKey": CLAIM,
                "declaredStatement": "accepted",
                "validitySummary": "accepted",
                "scopeQualifications": [],
                "evidenceTransactionIds": [
                    "c70e1829a7c6a2a8cb8cfc2383f8abf825ac5ea6"
                ],
                "dependencyTransactionIds": [
                    "c70e1829a7c6a2a8cb8cfc2383f8abf825ac5ea6"
                ],
            }
        ]
        self.claim_refs = [
            {
                "transactionId": SUBJECT,
                "claimKey": CLAIM,
                "judgmentId": JUDGMENT,
                "assessmentDigest": ASSESSMENT,
            }
        ]
        paths = sorted(
            {
                path
                for result in self.packet["intermediateResults"]
                for path in result["support"]["artifactPaths"]
            }
        )
        files = {
            path: f"fixture evidence for {path}\n".encode() for path in paths
        }
        self.manifest, self.chunks = build_submission_evidence_manifest(
            problem_id="bssc-sum-capacity",
            subject_transaction_id=SUBJECT,
            contribution_path=(
                "problems/bssc-sum-capacity/contributions/"
                "uv-product-branchwise-additivity"
            ),
            files=files,
            chunk_bytes=37,
        )

    def _run_candidate(
        self, provider: CounterfactualProvider, checkpoint: Path | None = None
    ):
        return run_joint_portfolio_credit_candidate(
            provider=provider,
            subject_transaction_id=SUBJECT,
            root_contract=self.contract,
            base_knowledge_state=self.base,
            base_accounting_state=self.base_accounting,
            joint_response=self.response,
            semantic_packet=self.packet,
            accepted_claims=self.claims,
            accepted_claim_refs=self.claim_refs,
            judgment_id=JUDGMENT,
            evidence_manifest=self.manifest,
            evidence_chunks=self.chunks,
            checkpoint_dir=checkpoint,
            descendant_depth=1,
        )

    def test_joint_wplus_is_frozen_and_credit_is_allocated_to_submission(self) -> None:
        provider = CounterfactualProvider()
        result = self._run_candidate(provider)
        self.assertEqual([stage for stage, _, _ in provider.calls], ["safe-facts", "no-access"])
        self.assertEqual(result["withAccessState"]["totalWorkHours"], "4351.7375")
        self.assertEqual(result["noAccessState"]["totalWorkHours"], "4651.7375")
        self.assertEqual(result["evaluation"]["workValueHours"], "300")
        credit = validate_joint_portfolio_credit_candidate(result["creditCandidate"])
        self.assertEqual(
            credit["allocationTarget"], {"kind": "submission", "id": SUBJECT}
        )
        self.assertEqual(credit["allocatedWorkHours"], "300")
        effects = {
            item["nodeRef"]["id"]: item["workReductionHours"]
            for item in credit["nodeEffects"]
        }
        self.assertEqual(effects["root"], "100")
        self.assertEqual(effects[NEW_PROGRAM], "200")
        rendered = json.dumps(credit, sort_keys=True)
        self.assertNotIn("percentage", rendered.lower())
        self.assertNotIn("share", rendered.lower())

    def test_no_access_request_excludes_evidence_and_joint_rationales(self) -> None:
        provider = CounterfactualProvider()
        result = self._run_candidate(provider)
        request = result["noAccessRequest"]
        rendered = json.dumps(request, sort_keys=True)
        self.assertNotIn("evidenceManifest", rendered)
        self.assertNotIn("withAccessPatch", rendered)
        self.assertNotIn(self.response["topologyRationale"], rendered)
        prohibited = {"evidenceManifest", "submissionEvidence", "contentBase64"}

        def assert_no_prohibited_keys(value):
            if isinstance(value, dict):
                self.assertFalse(prohibited & set(value))
                for child in value.values():
                    assert_no_prohibited_keys(child)
            elif isinstance(value, list):
                for child in value:
                    assert_no_prohibited_keys(child)

        assert_no_prohibited_keys(request)
        self.assertEqual(
            request["stageInput"]["frozenWithAccessState"],
            result["withAccessState"],
        )

    def test_nonpositive_counterfactual_is_rejected_without_changing_wplus(self) -> None:
        with self.assertRaisesRegex(MathFlowError, "strictly positive"):
            self._run_candidate(CounterfactualProvider(nonpositive=True))

    def test_tampered_joint_response_fails_before_counterfactual_calls(self) -> None:
        response = copy.deepcopy(self.response)
        response["baseStateDigest"] = "sha256:" + "0" * 64
        provider = CounterfactualProvider()
        with self.assertRaises(MathFlowError):
            run_joint_portfolio_credit_candidate(
                provider=provider,
                subject_transaction_id=SUBJECT,
                root_contract=self.contract,
                base_knowledge_state=self.base,
                base_accounting_state=self.base_accounting,
                joint_response=response,
                semantic_packet=self.packet,
                accepted_claims=self.claims,
                accepted_claim_refs=self.claim_refs,
                judgment_id=JUDGMENT,
                evidence_manifest=self.manifest,
                evidence_chunks=self.chunks,
            )
        self.assertEqual(provider.calls, [])

    def test_checkpoint_reuses_safe_facts_but_not_rejected_no_access(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            checkpoint = Path(temporary) / "checkpoints"
            with self.assertRaisesRegex(MathFlowError, "strictly positive"):
                self._run_candidate(CounterfactualProvider(nonpositive=True), checkpoint)
            retry = CounterfactualProvider()
            result = self._run_candidate(retry, checkpoint)
            self.assertEqual([stage for stage, _, _ in retry.calls], ["no-access"])
            self.assertEqual(result["creditCandidate"]["allocatedWorkHours"], "300")


if __name__ == "__main__":
    unittest.main()
