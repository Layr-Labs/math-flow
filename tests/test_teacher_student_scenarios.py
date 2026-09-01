from __future__ import annotations

import json
import tempfile
import unittest
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path

from math_flow.artifacts import sha256_bytes, verify_bundle
from math_flow.cli import main
from math_flow.errors import MathFlowError
from math_flow.teacher_student_scenarios import (
    run_teacher_student_scenario,
    validate_teacher_student_scenario_manifest,
)


def _write_json(path: Path, value: object) -> str:
    path.parent.mkdir(parents=True, exist_ok=True)
    raw = (json.dumps(value, indent=2, ensure_ascii=False) + "\n").encode("utf-8")
    path.write_bytes(raw)
    return sha256_bytes(raw)


def _attempt(label: str) -> dict[str, object]:
    return {
        "status": "accepted",
        "providerCall": False,
        "rawRequest": {"stage": label},
        "rawResponse": {"content": "ok"},
        "telemetry": {
            "model": "fake/provider-free",
            "configuredContextTokens": 100,
            "configuredCompletionTokens": 10,
            "requestComponents": [
                {"id": "system", "content": label},
                {"id": "local-context", "characters": 4},
            ],
            "promptTokens": 2,
            "cachedPromptTokens": 0,
            "reasoningTokens": 0,
            "completionTokens": 1,
            "totalTokens": 3,
            "costUsd": 0,
            "elapsedMs": 1,
            "finishReason": "stop",
            "outputCharacters": 2,
            "trailingWhitespaceCharacters": 0,
            "validationClass": "accepted",
            "retryCause": None,
            "entityCounts": {"programs": 1},
        },
    }


def _scenario(root: Path, *, failing_gold: bool = False) -> Path:
    initial_path = root / "fixtures/initial.json"
    initial_digest = _write_json(initial_path, {"programs": {}})
    gold_path = root / "fixtures/gold.json"
    gold_digest = _write_json(
        gold_path,
        {
            "schemaVersion": 1,
            "assertions": [
                {
                    "id": "route-selects-one-program",
                    "severity": "hard",
                    "actual": {
                        "operation": "length",
                        "value": {
                            "artifact": "k1.route.plan",
                            "pointer": "/programIds",
                        },
                    },
                    "operator": "equals",
                    "expected": 2 if failing_gold else 1,
                },
                {
                    "id": "author-uses-route-id",
                    "severity": "hard",
                    "actual": {
                        "operation": "keys",
                        "value": {
                            "artifact": "k1.author.state",
                            "pointer": "/programs",
                        },
                    },
                    "operator": "set-equals",
                    "expectedExpression": {
                        "artifact": "k1.route.plan",
                        "pointer": "/programIds",
                    },
                },
                {
                    "id": "root-pointer-addresses-the-whole-artifact",
                    "severity": "hard",
                    "actual": {
                        "artifact": "k1.route.plan",
                        "pointer": "",
                    },
                    "operator": "equals",
                    "expected": {"programIds": ["program-one"]},
                },
            ],
        },
    )
    route_path = root / "fixtures/route.json"
    route_digest = _write_json(
        route_path,
        {
            "schemaVersion": 1,
            "stageId": "route",
            "outcome": "accepted",
            "attempts": [_attempt("route")],
            "outputs": [
                {
                    "id": "plan",
                    "mediaType": "application/json",
                    "value": {"programIds": ["program-one"]},
                }
            ],
        },
    )
    author_path = root / "fixtures/author.json"
    author_digest = _write_json(
        author_path,
        {
            "schemaVersion": 1,
            "stageId": "author",
            "outcome": "accepted",
            "attempts": [_attempt("author")],
            "outputs": [
                {
                    "id": "state",
                    "mediaType": "application/json",
                    "value": {
                        "programs": {"program-one": {"status": "active"}}
                    },
                }
            ],
        },
    )
    manifest_path = root / "scenario.json"
    _write_json(
        manifest_path,
        {
            "schemaVersion": 1,
            "id": "route-author-smoke",
            "description": "A provider-free two-stage teacher-student smoke case.",
            "problemId": "synthetic-problem",
            "ledgerHead": "a" * 40,
            "publicationForbidden": True,
            "execution": {"adapter": "fixture-replay-v1"},
            "variants": [{"id": "candidate"}],
            "seeds": [7],
            "budgets": {
                "maximumProviderCalls": 0,
                "maximumStageAttempts": 2,
                "maximumPromptTokens": 4,
                "maximumCompletionTokens": 2,
                "maximumTotalTokens": 6,
                "maximumCostUsd": 0,
            },
            "frozenInputs": [
                {
                    "id": "initial-state",
                    "path": "fixtures/initial.json",
                    "digest": initial_digest,
                    "mediaType": "application/json",
                },
                {
                    "id": "relational-gold",
                    "path": "fixtures/gold.json",
                    "digest": gold_digest,
                    "mediaType": "application/json",
                },
            ],
            "steps": [
                {
                    "id": "k1",
                    "subjectTransactionId": "b" * 40,
                    "stages": [
                        {
                            "id": "route",
                            "adapter": "fixture-replay-v1",
                            "reads": ["initial-state"],
                            "outputs": ["plan"],
                            "fixtures": [
                                {
                                    "variant": "candidate",
                                    "seed": 7,
                                    "path": "fixtures/route.json",
                                    "digest": route_digest,
                                }
                            ],
                        },
                        {
                            "id": "author",
                            "adapter": "fixture-replay-v1",
                            "reads": ["initial-state", "k1.route.plan"],
                            "outputs": ["state"],
                            "fixtures": [
                                {
                                    "variant": "candidate",
                                    "seed": 7,
                                    "path": "fixtures/author.json",
                                    "digest": author_digest,
                                }
                            ],
                        },
                    ],
                }
            ],
            "scorers": [
                {
                    "id": "topology",
                    "implementation": "json-relational-v1",
                    "goldInputId": "relational-gold",
                }
            ],
        },
    )
    return manifest_path


class TeacherStudentScenarioTests(unittest.TestCase):
    def test_replays_route_author_and_writes_verified_bundle(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            manifest = _scenario(root)
            output = root / "output"
            result = run_teacher_student_scenario(root, manifest, output)

            self.assertEqual(result["runKind"], "teacher-student-scenario")
            self.assertEqual(result["execution"]["providerCallsExecuted"], 0)
            self.assertEqual(result["summary"]["status"], "passed")
            verified, _ = verify_bundle(output)
            self.assertEqual(verified, result)
            telemetry = json.loads((output / "telemetry.json").read_text())
            self.assertEqual(telemetry["stageAttempts"], 2)
            self.assertEqual(telemetry["providerCallsRecorded"], 0)
            self.assertEqual(telemetry["requestComponents"]["system"]["characters"], 11)
            score = json.loads(
                (
                    output
                    / "chains/candidate/seed-7/scores/topology.json"
                ).read_text()
            )
            self.assertEqual(score["status"], "passed")
            stage = json.loads(
                (
                    output
                    / "chains/candidate/seed-7/steps/k1/stages/author/result.json"
                ).read_text()
            )
            self.assertEqual(
                [item["artifactId"] for item in stage["reads"]],
                ["initial-state", "k1.route.plan"],
            )

    def test_cli_can_require_a_passing_score(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            manifest = _scenario(root, failing_gold=True)
            output = root / "output"
            with redirect_stdout(StringIO()):
                status = main(
                    [
                        "--root",
                        str(root),
                        "teacher-student-scenario",
                        "--manifest",
                        str(manifest),
                        "--output-dir",
                        str(output),
                        "--require-pass",
                    ]
                )
            self.assertEqual(status, 2)
            self.assertEqual(
                json.loads((output / "summary.json").read_text())["status"],
                "failed",
            )

    def test_hard_budget_is_checked_before_bundle_creation(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            manifest = _scenario(root)
            value = json.loads(manifest.read_text())
            value["budgets"]["maximumTotalTokens"] = 5
            _write_json(manifest, value)
            output = root / "output"
            with self.assertRaisesRegex(MathFlowError, "hard budget exceeded"):
                run_teacher_student_scenario(root, manifest, output)
            self.assertFalse(output.exists())

    def test_fixture_digest_is_fail_closed(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            manifest = _scenario(root)
            route = root / "fixtures/route.json"
            route.write_text(route.read_text() + " ", encoding="utf-8")
            with self.assertRaisesRegex(MathFlowError, "digest mismatch"):
                run_teacher_student_scenario(root, manifest, root / "output")

    def test_publication_must_be_forbidden(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            manifest = _scenario(root)
            value = json.loads(manifest.read_text())
            value["publicationForbidden"] = False
            _write_json(manifest, value)
            with self.assertRaisesRegex(MathFlowError, "must forbid publication"):
                validate_teacher_student_scenario_manifest(root, manifest)

    def test_failed_stage_stops_chain_and_excludes_unreached_telemetry(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            manifest = _scenario(root)
            value = json.loads(manifest.read_text())
            fixture_path = root / "fixtures/route.json"
            fixture = json.loads(fixture_path.read_text())
            fixture["outcome"] = "failed"
            fixture["attempts"][0]["status"] = "failed"
            fixture["attempts"][0]["telemetry"]["validationClass"] = "semantic-failure"
            fixture["outputs"] = []
            digest = _write_json(fixture_path, fixture)
            value["steps"][0]["stages"][0]["fixtures"][0]["digest"] = digest
            _write_json(manifest, value)
            output = root / "output"
            result = run_teacher_student_scenario(root, manifest, output)
            self.assertEqual(result["summary"]["status"], "failed")
            telemetry = json.loads((output / "telemetry.json").read_text())
            self.assertEqual(telemetry["stageAttempts"], 1)
            self.assertFalse(
                (
                    output
                    / "chains/candidate/seed-7/steps/k1/stages/author/result.json"
                ).exists()
            )

    def test_forward_stage_read_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            manifest = _scenario(root)
            value = json.loads(manifest.read_text())
            value["steps"][0]["stages"][0]["reads"] = ["k1.author.state"]
            _write_json(manifest, value)
            with self.assertRaisesRegex(MathFlowError, "unavailable artifact"):
                validate_teacher_student_scenario_manifest(root, manifest)

    def test_replays_migrated_bssc_holdout_without_provider(self) -> None:
        root = Path(__file__).resolve().parents[1]
        manifest = root / "protocol/experiments/bssc-credit-topology-v3/scenario-v1.json"
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / "replay"
            result = run_teacher_student_scenario(root, manifest, output)
            self.assertEqual(result["execution"]["providerCallsExecuted"], 0)
            self.assertEqual(result["summary"]["chains"], 2)
            self.assertEqual(result["summary"]["hardFailures"], 8)
            telemetry = json.loads((output / "telemetry.json").read_text())
            self.assertEqual(telemetry["providerCallsRecorded"], 5)
            self.assertEqual(telemetry["totalTokens"], 179804)
            self.assertEqual(telemetry["costUsdRecorded"], 0.590397)
            self.assertEqual(telemetry["retryCauses"], {"length-truncated": 1})


if __name__ == "__main__":
    unittest.main()
