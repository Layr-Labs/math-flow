from __future__ import annotations

import copy
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from math_flow import joint_portfolio_serial_holdout as holdout
from math_flow.errors import MathFlowError
from math_flow.joint_portfolio_serial_provider_v2 import (
    OpenRouterJointPortfolioSerialAuthorV2Provider,
    run_joint_portfolio_serial_author_v2,
    validate_joint_portfolio_serial_author_replay_v2,
)
from math_flow.repository import sha256_json
from tests import test_joint_portfolio_serial_transition_v2 as scenario_module
from tests.test_joint_portfolio_serial_holdout import (
    FixtureCreditProvider, FixtureJointAuthorProvider,
)
from tests.test_joint_portfolio_serial_provider_v2 import SequentialOpenRouterTransport, _spec


ROOT = Path(__file__).resolve().parents[1]


class CompletionAndExplanationTests(unittest.TestCase):
    def setUp(self):
        self.scenario = scenario_module.JointPortfolioSerialTransitionV2Tests()
        self.scenario.setUp()
        self.k1, _ = self.scenario.k1()
        self.k2, self.inputs = self.scenario.k2(self.k1)

    def completed_inputs(self):
        inputs = copy.deepcopy(self.inputs)
        inputs["response"]["programChanges"][0]["status"] = "completed"
        row = next(row for row in inputs["response"]["withAccessAssessments"]
                   if row["programId"] == scenario_module.PROGRAM2)
        row["directWorkHours"] = "0"
        row["conditionalIncidence"] = "0"
        return inputs

    def test_completed_creation_requires_zero_live_work_and_keeps_terminal_identity(self):
        inputs = self.completed_inputs()
        untouched = copy.deepcopy(inputs["response"])
        result = self.scenario.reduce(inputs)
        self.assertEqual(inputs["response"], untouched)
        self.assertEqual(result["postState"]["programs"][scenario_module.PROGRAM2]["status"], "completed")
        self.assertEqual(result["response"]["programChanges"][0]["status"], "completed")
        for field, value in (("directWorkHours", "1"), ("conditionalIncidence", "0.1")):
            with self.subTest(field=field):
                invalid = copy.deepcopy(inputs)
                invalid["response"]["withAccessAssessments"][0][field] = value
                with self.assertRaisesRegex(MathFlowError, "zero"):
                    self.scenario.reduce(invalid)

    def test_completed_creation_does_not_allow_retired_creation_or_scope_escape(self):
        for mutation in ("retired", "unknown", "scope", "base"):
            with self.subTest(mutation=mutation):
                inputs = self.completed_inputs()
                program = inputs["response"]["programChanges"][0]
                if mutation == "scope":
                    program["programId"] = "unreserved-program"
                elif mutation == "base":
                    program["baseDigest"] = "sha256:" + "a" * 64
                else:
                    program["status"] = mutation
                with self.assertRaisesRegex(MathFlowError, "creation escapes"):
                    self.scenario.reduce(inputs)

    def test_no_change_explanation_is_retained_without_creating_topology(self):
        _, inputs = self.scenario.k3(self.k2)
        text = "The existing package is reused; no topology change is needed."
        inputs["response"]["topologyRationale"] = text
        result = self.scenario.reduce(inputs)
        self.assertEqual(result["response"]["topologyRationale"], text)
        self.assertEqual(result["transition"]["placementAudit"]["rationale"], text)
        self.assertEqual(result["transition"]["topologyOperations"], [])
        for invalid in ("", " ", 1, {}, []):
            with self.subTest(invalid=invalid):
                inputs["response"]["topologyRationale"] = invalid
                with self.assertRaisesRegex(MathFlowError, "non-empty text"):
                    self.scenario.reduce(inputs)
        self.inputs["response"]["topologyRationale"] = None
        with self.assertRaisesRegex(MathFlowError, "topology rationale"):
            self.scenario.reduce(self.inputs)


class CompletedAndUnchangedHoldoutTests(unittest.TestCase):
    def test_completed_or_active_package_can_be_reassessed_without_numerical_change(self):
        for completed in (False, True):
            with self.subTest(completed=completed), tempfile.TemporaryDirectory() as directory:
                author_fixture = FixtureJointAuthorProvider()
                credit_fixture = FixtureCreditProvider()

                def author(**kwargs):
                    response = author_fixture(**kwargs)
                    if response["subjectTransactionId"] == holdout.SUBJECTS[0]:
                        return response
                    if completed:
                        response["programChanges"][0]["status"] = "completed"
                    for row in response["withAccessAssessments"]:
                        if row["programId"] == holdout.K2_PROGRAM:
                            row["directWorkHours"] = "0"
                            row["conditionalIncidence"] = "0" if completed else "1"
                        else:
                            row["directWorkHours"] = "900"
                    if response["subjectTransactionId"] == holdout.SUBJECTS[2]:
                        response["topologyRationale"] = "Support is added without changing topology or live estimates."
                    return response

                def credit(**kwargs):
                    response = credit_fixture(**kwargs)
                    if kwargs["stage"] == "no-access" and kwargs["request"]["subjectTransactionId"] == holdout.SUBJECTS[2]:
                        # A synthetic positive counterfactual for this mechanics
                        # test, not a hosted numerical result or K3 credit oracle.
                        response = {"updates": [{"nodeRef": {"kind": "program", "id": "root"},
                            "changes": {"directWorkHours": "910"},
                            "rationale": "Ten hours of root work remain without this evidence.",
                            "evidenceRefs": ["safe-fact:realized-result-condition"]}]}
                    return response

                output = Path(directory) / "bundle"
                result = holdout.run_bssc_joint_portfolio_serial_holdout_v1(
                    root=ROOT, output_dir=output, checkpoint_dir=Path(directory) / "checkpoints",
                    joint_author_provider=author, credit_provider=credit,
                )
                replay = holdout.load_bssc_joint_portfolio_serial_holdout_bundle_v1(
                    output, expected_bundle_digest=result["bundleDigest"])
                k2, k3 = replay["steps"][1:]
                self.assertEqual(k2["joint"]["withAccessState"]["totalWorkHours"], k3["joint"]["withAccessState"]["totalWorkHours"])
                self.assertEqual(k3["joint"]["withAccessPatch"]["updates"], [])
                self.assertEqual(k3["creditCandidate"]["allocatedWorkHours"], "10")
                self.assertEqual(k3["joint"]["transition"]["topologyOperations"], [])
                status = "completed" if completed else "active"
                self.assertEqual(k3["joint"]["postState"]["programs"][holdout.K2_PROGRAM]["status"], status)
                effect = next(row for row in k2["creditCandidate"]["nodeEffects"] if row["nodeRef"]["id"] == holdout.K2_PROGRAM)
                self.assertEqual(effect["withAccess"]["directWorkHours"], "0")
                self.assertEqual(effect["noAccess"]["directWorkHours"], "200")
                self.assertEqual(effect["noAccess"]["conditionalIncidence"], "1")
                self.assertEqual(len(author_fixture.calls), 3)
                self.assertEqual(len(credit_fixture.calls), 6)


class RecordedCompletionAndRefreshTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        fixture = json.loads((ROOT / "tests/fixtures/joint_portfolio_hosted_completion_refresh.json").read_text())
        cls.records = {row["call"]: row for row in fixture["responses"]}
        cls.inputs = {}
        cls.manifests = {}
        original_author = holdout.run_joint_portfolio_serial_author_v2
        original_cases = holdout._materialize_cases

        class Captured(Exception):
            pass

        def capture_cases(*args, **kwargs):
            result = original_cases(*args, **kwargs)
            cls.manifests = {case["subject"]: case["evidenceManifest"] for case in result[1]}
            return result

        def capture_author(**kwargs):
            subject = kwargs["subject_transaction_id"]
            cls.inputs[subject] = {key: value for key, value in kwargs.items() if key != "provider"}
            if subject == holdout.SUBJECTS[2]:
                raise Captured()
            call = 1 if subject == holdout.SUBJECTS[0] else 5
            kwargs["provider"] = lambda **unused: copy.deepcopy(cls.records[call]["response"])
            return original_author(**kwargs)

        def forbidden(**kwargs):
            raise AssertionError("No real provider call is permitted")

        with tempfile.TemporaryDirectory() as directory:
            with patch.object(holdout, "run_joint_portfolio_serial_author_v2", side_effect=capture_author), patch.object(holdout, "_materialize_cases", side_effect=capture_cases):
                try:
                    holdout.run_bssc_joint_portfolio_serial_holdout_v1(
                        root=ROOT, output_dir=Path(directory) / "unused",
                        checkpoint_dir=Path(directory) / "checkpoints",
                        joint_author_provider=forbidden, credit_provider=FixtureCreditProvider(),
                    )
                except Captured:
                    pass

    def test_exact_completed_k2_and_unchanged_k3_responses_pass_once(self):
        for call in (4, 9, 10):
            with self.subTest(call=call):
                record = self.records[call]
                raw = copy.deepcopy(record["response"])
                self.assertEqual("sha256:" + sha256_json(raw), record["responseDigest"])
                transport = SequentialOpenRouterTransport([raw])
                provider = OpenRouterJointPortfolioSerialAuthorV2Provider(_spec(), transport=transport)
                kwargs = self.inputs[record["subjectTransactionId"]]
                result = run_joint_portfolio_serial_author_v2(provider=provider, **kwargs)
                self.assertEqual(len(transport.requests), 1)
                self.assertEqual(result["response"], raw)
                self.assertEqual(result["responseDigest"], record["responseDigest"])
                self.assertEqual(validate_joint_portfolio_serial_author_replay_v2(result, **kwargs), result)
                if call == 4:
                    self.assertEqual(result["reduced"]["postState"]["programs"][holdout.K2_PROGRAM]["status"], "completed")
                else:
                    holdout._assert_k3_reuse_and_refresh(before_state=kwargs["base_state"], joint=result["reduced"], evidence_manifest=self.manifests[record["subjectTransactionId"]])
                    self.assertEqual(result["reduced"]["withAccessState"]["totalWorkHours"], kwargs["base_accounting_state"]["totalWorkHours"])

    def test_explicit_owner_refresh_and_complete_current_assessments_still_required(self):
        raw = copy.deepcopy(self.records[8]["response"])
        kwargs = self.inputs[holdout.SUBJECTS[2]]
        with self.assertRaisesRegex(MathFlowError, "owners must be explicitly changed"):
            run_joint_portfolio_serial_author_v2(provider=lambda **unused: raw, **kwargs)
        for field in ("withAccessAssessments", "programBoundaries"):
            with self.subTest(field=field):
                raw = copy.deepcopy(self.records[9]["response"])
                raw[field].pop()
                with self.assertRaisesRegex(MathFlowError, "cover every accounting-affected"):
                    run_joint_portfolio_serial_author_v2(provider=lambda **unused: raw, **kwargs)


if __name__ == "__main__":
    unittest.main()
