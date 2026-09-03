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
    OpenRouterJointPortfolioSerialCreditV2Provider,
    PROFILE,
    run_joint_portfolio_serial_credit_v2,
    validate_joint_portfolio_serial_credit_candidate_v2,
    validate_joint_portfolio_serial_credit_replay_v2,
)
from math_flow.repository import sha256_json
from tests import test_joint_portfolio_serial_transition_v2 as fixtures


ROOT = Path(__file__).resolve().parents[1]


def _quoted_input(request: dict[str, object]) -> dict[str, object]:
    prefix = "<math-flow-input>\n"
    suffix = "\n</math-flow-input>"
    for message in reversed(request["messages"]):
        content = message.get("content") if isinstance(message, dict) else None
        if not isinstance(content, str) or prefix not in content:
            continue
        raw = content.split(prefix, 1)[1]
        if not raw.endswith(suffix):
            raise AssertionError("malformed governed input")
        value = json.loads(raw[: -len(suffix)])
        if not isinstance(value, dict):
            raise AssertionError("governed input is not an object")
        return value
    raise AssertionError("governed input is missing")


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


class FixtureOpenRouterTransport:
    def __init__(self, provider: CounterfactualProviderV2) -> None:
        self.provider = provider
        self.requests: list[dict[str, object]] = []

    def __call__(self, request: dict[str, object]) -> dict[str, object]:
        self.requests.append(copy.deepcopy(request))
        user_data = _quoted_input(request)
        work_request = user_data["request"]
        stage = str(work_request["stage"])
        response = self.provider(
            stage=stage,
            request=work_request,
            evidence_files=(object(),) if stage == "safe-facts" else (),
        )
        return {
            "id": f"fixture-{len(self.requests)}",
            "model": "openai/gpt-5.6-sol",
            "choices": [
                {
                    "finish_reason": "stop",
                    "message": {"content": json.dumps(response)},
                }
            ],
        }


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
        accepted_refs = [{
            "transactionId": subject,
            "claimKey": claim,
            "judgmentId": inputs["judgment"],
            "assessmentDigest": f"sha256:{sha256_json(inputs['claims'][0])}",
        }]
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

    def reseal_candidate(self, candidate: dict[str, object]) -> dict[str, object]:
        value = copy.deepcopy(candidate)
        value["nodeEffectsDigest"] = f"sha256:{sha256_json({'evaluationDigest': value['evaluationDigest'], 'nodeEffects': value['nodeEffects']})}"
        core = {key: item for key, item in value.items() if key != "candidateDigest"}
        value["candidateDigest"] = f"sha256:{sha256_json(core)}"
        return value

    def replay_candidate(
        self,
        candidate: dict[str, object],
        *,
        result: dict[str, object],
        case: dict[str, object],
    ) -> dict[str, object]:
        return validate_joint_portfolio_serial_credit_replay_v2(
            candidate,
            accepted_claim_refs=case["acceptedRefs"],
            base_boundary_state=case["inputs"]["boundaries"],
            base_knowledge_state=case["inputs"]["state"],
            target_knowledge_state=result["jointArtifacts"]["postState"],
            impact_context=result["impactContext"],
            no_access_policy_context=result["noAccessPolicyContext"],
            no_access_request=result["noAccessRequest"],
            no_access_state=result["noAccessState"],
            with_access_state=result["withAccessState"],
            no_access_patch=result["noAccessPatch"],
            with_access_patch=result["withAccessPatch"],
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

    def test_claim_judgment_and_semantic_assessment_substitution_fail_before_calls(self) -> None:
        case = self.case(2)
        for field in ("judgmentId", "assessmentDigest"):
            with self.subTest(field=field):
                substituted = copy.deepcopy(case)
                substituted["acceptedRefs"][0][field] = "sha256:" + "f" * 64
                provider = self.provider(substituted)
                with self.assertRaisesRegex(
                    MathFlowError,
                    "accepted claim identities do not match the semantic assessments",
                ):
                    self.run_credit(substituted, provider)
                self.assertEqual(provider.calls, [])

    def test_no_access_request_carries_prior_and_sanitized_local_policy_only(self) -> None:
        case = self.case(2)
        result = self.run_credit(case, self.provider(case))
        request = result["noAccessRequest"]
        self.assertEqual(request["profile"], PROFILE)
        policy = request["stageInput"]["workPolicyContext"]
        self.assertEqual(policy, result["noAccessPolicyContext"])
        self.assertEqual(
            policy["baseBoundaryStateDigest"],
            case["inputs"]["boundaries"]["stateDigest"],
        )
        rows = {row["programId"]: row for row in policy["programPolicies"]}
        self.assertEqual(rows["root"]["source"], "pre-contribution-boundary")
        prior_root = {
            row["programId"]: row for row in case["inputs"]["boundaries"]["boundaries"]
        }["root"]
        self.assertEqual(rows["root"]["baseBoundaryDigest"], prior_root["boundaryDigest"])
        self.assertEqual(
            rows[fixtures.PROGRAM2]["source"], "sanitized-new-target-package"
        )
        self.assertIsNone(rows[fixtures.PROGRAM2]["baseBoundaryDigest"])
        for field in (
            "directResidualWorkScope",
            "activationCondition",
            "stoppingCondition",
            "independentVariationRationale",
        ):
            self.assertTrue(rows[fixtures.PROGRAM2][field])
        rendered = json.dumps(request, sort_keys=True)
        for key in (
            '"evidenceManifest":',
            '"verifiedChunkDigests":',
            '"withAccessPatch":',
            '"programBoundaries":',
            '"topologyRationale":',
        ):
            self.assertNotIn(key, rendered)
        self.assertNotIn(
            case["inputs"]["response"]["programBoundaries"][0][
                "independentVariationRationale"
            ],
            rendered,
        )
        for assessment in case["inputs"]["response"]["withAccessAssessments"]:
            self.assertNotIn(assessment["rationale"], rendered)

    def test_openrouter_adapter_accepts_joint_no_access_profile(self) -> None:
        case = self.case(2)
        fixture_provider = self.provider(case)
        transport = FixtureOpenRouterTransport(fixture_provider)
        spec = json.loads(
            (
                ROOT / "protocol/judges/openrouter-work-accounting-v2.json"
            ).read_text(encoding="utf-8")
        )
        provider = OpenRouterJointPortfolioSerialCreditV2Provider(
            spec, transport=transport
        )
        result = self.run_credit(case, provider)

        self.assertEqual(result["creditCandidate"]["allocatedWorkHours"], "300")
        self.assertEqual(
            [record["stage"] for record in provider.invocation_records],
            ["safe-facts", "no-access"],
        )
        self.assertEqual(len(transport.requests), 2)
        safe_input = _quoted_input(transport.requests[0])
        no_access_input = _quoted_input(transport.requests[1])
        self.assertIn("submissionEvidence", safe_input)
        self.assertNotIn("submissionEvidence", no_access_input)
        self.assertEqual(no_access_input["request"]["profile"], PROFILE)
        self.assertIn(
            "workPolicyContext",
            no_access_input["request"]["stageInput"],
        )

    def test_node_effect_schema_and_replay_reject_rehashed_tampering(self) -> None:
        case = self.case(1)
        result = self.run_credit(case, self.provider(case))
        candidate = result["creditCandidate"]
        self.replay_candidate(candidate, result=result, case=case)

        truncated = copy.deepcopy(candidate)
        truncated["nodeEffects"][0].pop("withAccess")
        truncated = self.reseal_candidate(truncated)
        with self.assertRaisesRegex(MathFlowError, "invalid fields"):
            validate_joint_portfolio_serial_credit_candidate_v2(truncated)

        rebound = copy.deepcopy(candidate)
        rebound["nodeEffects"][0]["nodeRef"]["id"] = "program-substituted-binding"
        rebound = self.reseal_candidate(rebound)
        validate_joint_portfolio_serial_credit_candidate_v2(rebound)
        with self.assertRaisesRegex(MathFlowError, "do not replay"):
            self.replay_candidate(rebound, result=result, case=case)

        reordered = copy.deepcopy(candidate)
        reordered["nodeEffects"] = list(reversed(reordered["nodeEffects"]))
        reordered = self.reseal_candidate(reordered)
        with self.assertRaisesRegex(MathFlowError, "uniquely ordered"):
            validate_joint_portfolio_serial_credit_candidate_v2(reordered)

        duplicated = copy.deepcopy(candidate)
        duplicated["nodeEffects"].insert(1, copy.deepcopy(duplicated["nodeEffects"][0]))
        duplicated = self.reseal_candidate(duplicated)
        with self.assertRaisesRegex(MathFlowError, "uniquely ordered"):
            validate_joint_portfolio_serial_credit_candidate_v2(duplicated)

        noncanonical = copy.deepcopy(candidate)
        noncanonical["nodeEffects"][0]["workReductionHours"] += ".0"
        noncanonical = self.reseal_candidate(noncanonical)
        with self.assertRaisesRegex(MathFlowError, "canonical signed"):
            validate_joint_portfolio_serial_credit_candidate_v2(noncanonical)

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
