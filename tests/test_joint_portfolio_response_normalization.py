from __future__ import annotations

import copy
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from math_flow.errors import MathFlowError
from math_flow import joint_portfolio_serial_holdout as holdout
from math_flow.joint_portfolio_serial_provider_v2 import (
    OpenRouterJointPortfolioSerialAuthorV2Provider,
    run_joint_portfolio_serial_author_v2,
    validate_joint_portfolio_serial_author_replay_v2,
)
from math_flow.repository import sha256_json
from tests import test_joint_portfolio_serial_transition_v2 as scenario_module
from tests.test_joint_portfolio_serial_provider_v2 import (
    SequentialOpenRouterTransport,
    _provider_inputs,
    _spec,
    _spec_digest,
)


ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "tests/fixtures/joint_portfolio_k1_hosted_ordering.json"
ROW_KEYS = {
    "programChanges": "programId",
    "resultPlacements": "resultId",
    "programBoundaries": "programId",
    "withAccessAssessments": "programId",
}


def reverse_sets(response):
    for field in ROW_KEYS:
        response[field].reverse()
    for row in response["resultPlacements"]:
        row["relatedProgramIds"].reverse()
    for row in response["withAccessAssessments"]:
        row["evidenceRefs"].reverse()


def canonical_copy(response):
    response = copy.deepcopy(response)
    for field, key in ROW_KEYS.items():
        response[field].sort(key=lambda row: row[key])
    for row in response["resultPlacements"]:
        row["relatedProgramIds"].sort()
    for row in response["withAccessAssessments"]:
        row["evidenceRefs"].sort(key=lambda ref: (ref["kind"], ref["id"], ref["digest"]))
    return response


class JointResponseNormalizationTests(unittest.TestCase):
    def setUp(self):
        self.scenario = scenario_module.JointPortfolioSerialTransitionV2Tests()
        self.scenario.setUp()
        _, inputs = self.scenario.k1()
        # Three incomparable work packages exercise multiple program rows and
        # multiple related owners without changing the accepted semantic packet.
        response = inputs["response"]
        for program_id in ("program-a", "program-z"):
            program = copy.deepcopy(response["programChanges"][0])
            program["programId"] = program_id
            response["programChanges"].append(program)
            response["programBoundaries"].append(scenario_module.boundary(program_id))
            assessment = copy.deepcopy(response["withAccessAssessments"][0])
            assessment["programId"] = program_id
            response["withAccessAssessments"].append(assessment)
        response["resultPlacements"][0]["relatedProgramIds"] = ["program-a", "program-z"]
        inputs["scope"] = self.scenario.scope(
            inputs["state"], inputs["claims"], write_programs=["root"],
            write_results=[], create_programs=["program-a", scenario_module.PROGRAM1, "program-z"],
            create_results=[scenario_module.RESULT1],
        )
        response["authoringPacketDigest"] = inputs["scope"]["authoringPacketDigest"]
        for row in response["withAccessAssessments"]:
            row["evidenceRefs"].extend([
                {"kind": "prior-program", "id": "root", "digest": inputs["state"]["programs"]["root"]["digest"]},
                {"kind": "semantic-result", "id": scenario_module.RESULT1, "digest": inputs["packet"]["packetDigest"]},
            ])
        inputs["response"] = canonical_copy(response)
        self.inputs = inputs
        self.expected = self.scenario.reduce(inputs)

    def test_every_unordered_field_and_combination_reduce_identically(self):
        for field in (*ROW_KEYS, "relatedProgramIds", "evidenceRefs", "all"):
            with self.subTest(field=field):
                inputs = copy.deepcopy(self.inputs)
                response = inputs["response"]
                if field in ROW_KEYS:
                    response[field].reverse()
                elif field == "relatedProgramIds":
                    response["resultPlacements"][0][field].reverse()
                elif field == "evidenceRefs":
                    for row in response["withAccessAssessments"]:
                        row[field].reverse()
                else:
                    reverse_sets(response)
                untouched = copy.deepcopy(response)
                self.assertEqual(self.scenario.reduce(inputs), self.expected)
                self.assertEqual(response, untouched)

    def test_result_permutation_with_two_results_reduces_identically(self):
        k1, _ = self.scenario.k1()
        expected, inputs = self.scenario.k2(k1)
        inputs["response"]["resultPlacements"].reverse()
        self.assertEqual(self.scenario.reduce(inputs), expected)

    def test_duplicates_remain_errors_not_silent_deduplication(self):
        for field in (*ROW_KEYS, "relatedProgramIds", "evidenceRefs"):
            with self.subTest(field=field):
                inputs = copy.deepcopy(self.inputs)
                response = inputs["response"]
                reverse_sets(response)
                rows = (
                    response["resultPlacements"][0][field] if field == "relatedProgramIds"
                    else response["withAccessAssessments"][0][field] if field == "evidenceRefs"
                    else response[field]
                )
                rows.append(copy.deepcopy(rows[0]))
                with self.assertRaises(MathFlowError):
                    self.scenario.reduce(inputs)

    def test_missing_rows_stale_bindings_scope_and_evidence_still_fail(self):
        for field in ("resultPlacements", "programBoundaries", "withAccessAssessments", "binding", "scope", "evidence"):
            with self.subTest(field=field):
                inputs = copy.deepcopy(self.inputs)
                response = inputs["response"]
                reverse_sets(response)
                if field in ROW_KEYS:
                    response[field].pop()
                elif field == "binding":
                    response["baseStateDigest"] = "sha256:" + "f" * 64
                elif field == "scope":
                    response["programChanges"][0]["programId"] = "program-not-authorized"
                else:
                    response["withAccessAssessments"][0]["evidenceRefs"][0]["digest"] = "sha256:" + "f" * 64
                with self.assertRaises(MathFlowError):
                    self.scenario.reduce(inputs)

    def test_malformed_sort_keys_and_extra_fields_are_not_repaired(self):
        for field, key in ROW_KEYS.items():
            for invalid in (None, 1, [], {}):
                with self.subTest(field=field, invalid=invalid):
                    inputs = copy.deepcopy(self.inputs)
                    inputs["response"][field][0][key] = invalid
                    with self.assertRaises(MathFlowError):
                        self.scenario.reduce(inputs)
        for field in ROW_KEYS:
            with self.subTest(extra_field=field):
                inputs = copy.deepcopy(self.inputs)
                inputs["response"][field][0]["unapproved"] = True
                with self.assertRaises(MathFlowError):
                    self.scenario.reduce(inputs)

    def test_raw_response_digest_and_replay_are_preserved_with_one_transport_call(self):
        raw = copy.deepcopy(self.inputs["response"])
        reverse_sets(raw)
        transport = SequentialOpenRouterTransport([raw])
        provider = OpenRouterJointPortfolioSerialAuthorV2Provider(_spec(), transport=transport)
        kwargs = _provider_inputs(self.inputs)
        result = run_joint_portfolio_serial_author_v2(provider=provider, **kwargs)
        self.assertEqual(len(transport.requests), 1)
        self.assertEqual(provider.invocation_records[0]["attempts"], 1)
        self.assertEqual(result["response"], raw)
        self.assertEqual(result["responseDigest"], "sha256:" + sha256_json(raw))
        self.assertEqual(result["reduced"], self.expected)
        self.assertNotEqual(result["response"], result["reduced"]["response"])
        self.assertEqual(validate_joint_portfolio_serial_author_replay_v2(result, **kwargs), result)
        tampered = copy.deepcopy(result)
        tampered["response"]["programChanges"].reverse()
        with self.assertRaisesRegex(MathFlowError, "not exact"):
            validate_joint_portfolio_serial_author_replay_v2(tampered, **kwargs)


class HostedOrderingResponseRegressionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.fixture = json.loads(FIXTURE.read_text())
        captured = {}

        class InputsCaptured(Exception):
            pass

        def capture(**kwargs):
            captured.update(kwargs)
            raise InputsCaptured()

        def forbidden(**kwargs):
            raise AssertionError("No live provider or credit call is allowed")

        # Use the actual holdout input assembly, stopping before its first author
        # call. This reconstructs the original K1 evidence, scope and bindings.
        with tempfile.TemporaryDirectory() as directory:
            with patch.object(holdout, "run_joint_portfolio_serial_author_v2", side_effect=capture):
                try:
                    holdout.run_bssc_joint_portfolio_serial_holdout_v1(
                        root=ROOT, output_dir=Path(directory) / "unused",
                        checkpoint_dir=Path(directory) / "checkpoints",
                        joint_author_provider=forbidden, credit_provider=forbidden,
                    )
                except InputsCaptured:
                    pass
        captured.pop("provider")
        cls.kwargs = captured

    def test_exact_recorded_responses_need_no_retries_for_ordering(self):
        for attempt in self.fixture["attempts"][1:]:
            with self.subTest(attempt=attempt["attempt"]):
                raw = copy.deepcopy(attempt["response"])
                self.assertEqual("sha256:" + sha256_json(raw), attempt["responseDigest"])
                transport = SequentialOpenRouterTransport([raw])
                provider = OpenRouterJointPortfolioSerialAuthorV2Provider(_spec(), transport=transport)
                result = run_joint_portfolio_serial_author_v2(provider=provider, **self.kwargs)
                self.assertEqual(len(transport.requests), 1)
                self.assertEqual(provider.invocation_records[0]["attempts"], 1)
                self.assertEqual(result["response"], raw)
                self.assertEqual(result["responseDigest"], attempt["responseDigest"])
                self.assertEqual(result["reduced"]["response"], canonical_copy(raw))
                self.assertEqual(validate_joint_portfolio_serial_author_replay_v2(result, **self.kwargs), result)
                self.assertEqual(self.kwargs["judge_spec_digest"], _spec_digest())

    def test_original_root_update_is_not_silently_dropped(self):
        attempt = self.fixture["attempts"][0]
        raw = copy.deepcopy(attempt["response"])
        self.assertEqual("sha256:" + sha256_json(raw), attempt["responseDigest"])
        with self.assertRaisesRegex(MathFlowError, "exclude root.*semanticPacket.rootUpdate"):
            run_joint_portfolio_serial_author_v2(provider=lambda **kwargs: copy.deepcopy(raw), **self.kwargs)
        self.assertEqual(raw, attempt["response"])
        # Explicit diagnostic correction, not an automatic acceptance path.
        corrected = copy.deepcopy(raw)
        corrected["programChanges"] = [row for row in corrected["programChanges"] if row["programId"] != "root"]
        result = run_joint_portfolio_serial_author_v2(provider=lambda **kwargs: copy.deepcopy(corrected), **self.kwargs)
        self.assertEqual(result["reduced"]["response"], canonical_copy(corrected))


if __name__ == "__main__":
    unittest.main()
