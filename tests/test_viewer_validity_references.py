from __future__ import annotations

import unittest
from pathlib import Path
from unittest.mock import patch

from math_flow.errors import MathFlowError
from math_flow.viewer import (
    _viewer_declared_references_by_claim,
    _viewer_judgment,
)


PROBLEM = "fixture-problem"
PACKET_DIGEST = f"sha256:{'a' * 64}"
RUN_DIGEST = f"sha256:{'b' * 64}"
JUDGMENT_ID = f"sha256:{'c' * 64}"
REFERENCE_A = "1" * 40
REFERENCE_B = "2" * 40


def v3_record() -> dict[str, object]:
    return {
        "schemaVersion": 3,
        "judgmentId": JUDGMENT_ID,
        "judgmentKind": "primary",
        "dependencyPacketDigest": PACKET_DIGEST,
        "reportDigest": f"sha256:{'d' * 64}",
        "assessments": [
            {
                "claimKey": "fixture-problem/claim-a",
                "requiredDependencyTransactionIds": [REFERENCE_A],
            },
            {
                "claimKey": "fixture-problem/claim-b",
                "requiredDependencyTransactionIds": [],
            },
        ],
    }


def v3_packet() -> dict[str, object]:
    return {
        "schemaVersion": 2,
        "packetDigest": PACKET_DIGEST,
        "claims": [
            {
                "claimKey": "fixture-problem/claim-a",
                "declaredReferenceTransactionIds": [REFERENCE_A, REFERENCE_B],
            },
            {
                "claimKey": "fixture-problem/claim-b",
                "declaredReferenceTransactionIds": [],
            },
        ],
    }


class ViewerValidityReferenceTests(unittest.TestCase):
    def test_extracts_per_claim_declared_references_for_validity_v3(self) -> None:
        self.assertEqual(
            _viewer_declared_references_by_claim(v3_record(), v3_packet()),
            {
                "fixture-problem/claim-a": [REFERENCE_A, REFERENCE_B],
                "fixture-problem/claim-b": [],
            },
        )

    def test_rejects_required_reference_declared_only_for_another_claim(self) -> None:
        record = v3_record()
        record["assessments"][0]["requiredDependencyTransactionIds"] = [REFERENCE_B]
        packet = v3_packet()
        packet["claims"][0]["declaredReferenceTransactionIds"] = [REFERENCE_A]
        packet["claims"][1]["declaredReferenceTransactionIds"] = [REFERENCE_B]
        with self.assertRaisesRegex(MathFlowError, "assessment provenance"):
            _viewer_declared_references_by_claim(record, packet)

    def test_rejects_a_packet_not_bound_to_the_judgment(self) -> None:
        packet = v3_packet()
        packet["packetDigest"] = f"sha256:{'e' * 64}"
        with self.assertRaisesRegex(MathFlowError, "does not match"):
            _viewer_declared_references_by_claim(v3_record(), packet)

    def test_viewer_adds_v3_reference_index_but_keeps_v2_shape(self) -> None:
        manifest = {
            "runKind": "judgment",
            "problemId": PROBLEM,
            "ledgerHead": "f" * 40,
            "judgeSpec": {"id": "fixture", "digest": f"sha256:{'0' * 64}"},
            "providerRuns": [],
        }
        with (
            patch("math_flow.viewer.load_manifest", return_value=(manifest, RUN_DIGEST)),
            patch(
                "math_flow.viewer._json_artifact",
                side_effect=[v3_record(), v3_packet()],
            ),
            patch(
                "math_flow.viewer.read_verified_artifact",
                return_value=b"# Validity report\n",
            ),
        ):
            exported = _viewer_judgment(Path("fixture-v3"), PROBLEM)
        self.assertEqual(
            exported["declaredReferenceTransactionIdsByClaim"],
            {
                "fixture-problem/claim-a": [REFERENCE_A, REFERENCE_B],
                "fixture-problem/claim-b": [],
            },
        )

        v2 = {**v3_record(), "schemaVersion": 2}
        for assessment in v2["assessments"]:
            assessment.pop("requiredDependencyTransactionIds")
        with (
            patch("math_flow.viewer.load_manifest", return_value=(manifest, RUN_DIGEST)),
            patch("math_flow.viewer._json_artifact", return_value=v2),
            patch(
                "math_flow.viewer.read_verified_artifact",
                return_value=b"# Validity report\n",
            ),
        ):
            exported_v2 = _viewer_judgment(Path("fixture-v2"), PROBLEM)
        self.assertNotIn("declaredReferenceTransactionIdsByClaim", exported_v2)


if __name__ == "__main__":
    unittest.main()
