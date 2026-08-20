from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from math_flow.artifacts import read_verified_artifact, sha256_bytes, verify_bundle
from math_flow.attestations import (
    ExecutionResult,
    _run_bounded_process,
    docker_oci_executor,
    objective_attestation_status,
    plan_verifier_attestation,
    run_verifier_attestation_bundle,
    verifier_spec_digest,
    verify_verifier_attestation_bundle,
)
from math_flow.coordination import publish_batch
from math_flow.errors import MathFlowError
from math_flow.judgments import (
    load_judgment_bundle,
    plan_primary_judgment_inputs,
    plan_primary_judgment_coverage,
    run_primary_judgment_bundle,
)
from math_flow.judges import load_source
from math_flow.repository import validate_pr, validate_tree
from math_flow.validity import build_evidence_packet_v4
from math_flow.viewer import _viewer_objective_attestations


def git(root: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", *args],
        cwd=root,
        check=True,
        stdout=subprocess.PIPE,
        text=True,
    )
    return result.stdout.strip()


def write(path: Path, value: str | bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if isinstance(value, bytes):
        path.write_bytes(value)
    else:
        path.write_text(value, encoding="utf-8")


class ObjectiveAttestationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        git(self.root, "init", "-q")
        git(self.root, "config", "user.name", "Attestation Test")
        git(self.root, "config", "user.email", "attestation@example.com")
        write(self.root / "problems/demo/problem.md", "# Demo\n")
        source_spec = (
            Path(__file__).parents[1]
            / "protocol/verifiers/python-stdlib-3-13-v1.json"
        )
        self.spec = json.loads(source_spec.read_text(encoding="utf-8"))
        write(
            self.root / "protocol/verifiers/python-stdlib-3-13-v1.json",
            json.dumps(self.spec, indent=2) + "\n",
        )
        git(self.root, "add", ".")
        git(self.root, "commit", "-qm", "Add problem and trusted verifier")
        self.base = git(self.root, "rev-parse", "HEAD")

    def add_contribution(self, *, spec_digest: str | None = None) -> str:
        prefix = self.root / "problems/demo/contributions/certificate"
        write(prefix / "README.md", "# Exact certificate\n")
        write(
            prefix / "verify.py",
            "from pathlib import Path\n"
            "assert Path('certificate.bin').read_bytes() == b'\\x00proof\\xff'\n"
            "print('certificate: valid')\n",
        )
        write(prefix / "certificate.bin", b"\x00proof\xff")
        request = {
            "schemaVersion": 1,
            "verifier": {
                "id": "python-stdlib-3-13-v1",
                "specDigest": spec_digest or verifier_spec_digest(self.spec),
            },
            "entrypoint": "verify.py",
            "arguments": [],
        }
        write(prefix / "verification.json", json.dumps(request, indent=2) + "\n")
        git(self.root, "add", ".")
        git(self.root, "commit", "-qm", "Add exact certificate")
        return git(self.root, "rev-parse", "HEAD")

    def add_claim_contribution(
        self,
        name: str,
        *,
        dependencies: list[str] | None = None,
        verification: bool = False,
        statement: str | None = None,
    ) -> str:
        prefix = self.root / f"problems/demo/contributions/{name}"
        write(
            prefix / "README.md",
            f"# {name}\n\n## Claims\n\n{statement or f'Claim for {name}.'}\n",
        )
        write(
            prefix / "claims.json",
            json.dumps(
                {
                    "schemaVersion": 1,
                    "claims": [
                        {
                            "claimKey": f"demo/{name}",
                            "statement": statement or f"Claim for {name}.",
                            "dependencyTransactionIds": dependencies or [],
                        }
                    ],
                },
                indent=2,
            )
            + "\n",
        )
        if verification:
            write(
                prefix / "verify.py",
                "from pathlib import Path\n"
                "assert Path('certificate.bin').read_bytes() == b'\\x00proof\\xff'\n"
                "print('certificate: valid')\n",
            )
            write(prefix / "certificate.bin", b"\x00proof\xff")
            write(
                prefix / "verification.json",
                json.dumps(
                    {
                        "schemaVersion": 1,
                        "verifier": {
                            "id": "python-stdlib-3-13-v1",
                            "specDigest": verifier_spec_digest(self.spec),
                        },
                        "entrypoint": "verify.py",
                        "arguments": [],
                    },
                    indent=2,
                )
                + "\n",
            )
        git(self.root, "add", ".")
        git(self.root, "commit", "-qm", f"Add {name}")
        return git(self.root, "rev-parse", "HEAD")

    def validity_v4_judge(self) -> Path:
        judge_value = json.loads(
            (
                Path(__file__).parents[1]
                / "protocol/judges/openrouter-validity-judgment-v4.json"
            ).read_text(encoding="utf-8")
        )
        judge_value.pop("contextProjection")
        judge = self.root / "validity-v4.json"
        write(judge, json.dumps(judge_value, indent=2) + "\n")
        return judge

    @staticmethod
    def passing_executor(
        materialized: Path,
        spec: dict[str, object],
        request: dict[str, object],
    ) -> ExecutionResult:
        assert request["entrypoint"] == "verify.py"
        assert (materialized / "certificate.bin").read_bytes() == b"\x00proof\xff"
        assert (materialized / "verification.json").is_file()
        assert spec["environment"]["network"] == "none"
        return ExecutionResult(0, b"certificate: valid\n", b"")

    def test_valid_request_is_canonical_intent_not_a_result(self) -> None:
        head = self.add_contribution()
        validated = validate_pr(self.root, self.base, head)
        self.assertEqual(validated["transactionKind"], "contribution")
        self.assertEqual(validate_tree(self.root)["contributions"], 1)
        request = json.loads(
            (
                self.root
                / "problems/demo/contributions/certificate/verification.json"
            ).read_text(encoding="utf-8")
        )
        self.assertNotIn("status", request)
        self.assertNotIn("accepted", request)

    def test_stale_verifier_digest_is_rejected_on_admission(self) -> None:
        head = self.add_contribution(spec_digest="sha256:" + "f" * 64)
        with self.assertRaisesRegex(MathFlowError, "spec digest is stale"):
            validate_pr(self.root, self.base, head)

    def test_mutable_image_tag_is_rejected(self) -> None:
        self.spec["environment"]["image"] = "python:3.13.7-slim"
        write(
            self.root / "protocol/verifiers/python-stdlib-3-13-v1.json",
            json.dumps(self.spec, indent=2) + "\n",
        )
        with self.assertRaisesRegex(MathFlowError, "exact sha256 OCI digest"):
            validate_tree(self.root)

    def test_attestation_is_deterministic_verified_and_replayable(self) -> None:
        transaction = self.add_contribution()
        first_parent = tempfile.TemporaryDirectory()
        second_parent = tempfile.TemporaryDirectory()
        self.addCleanup(first_parent.cleanup)
        self.addCleanup(second_parent.cleanup)
        first = Path(first_parent.name) / "run"
        second = Path(second_parent.name) / "run"
        first_manifest = run_verifier_attestation_bundle(
            self.root,
            "demo",
            transaction,
            "HEAD",
            first,
            executor=self.passing_executor,
        )
        second_manifest = run_verifier_attestation_bundle(
            self.root,
            "demo",
            transaction,
            "HEAD",
            second,
            executor=self.passing_executor,
        )
        self.assertEqual(first_manifest, second_manifest)
        self.assertEqual(first_manifest["runKind"], "verifier-attestation")
        self.assertEqual(first_manifest["inputs"]["transactionId"], transaction)
        self.assertEqual(verify_bundle(first)[1], verify_bundle(second)[1])

        verified = verify_verifier_attestation_bundle(
            self.root,
            first,
            "HEAD",
            replay=True,
            executor=self.passing_executor,
        )
        self.assertEqual(verified["transactionId"], transaction)
        self.assertEqual(verified["status"], "passed")
        self.assertTrue(verified["replayed"])

        pending_catalog = _viewer_objective_attestations(
            self.root, {}, ["demo"], "HEAD"
        )
        self.assertEqual(pending_catalog[0]["selectionStatus"], "pending")
        manifest, run_digest = verify_bundle(first)
        published_catalog = _viewer_objective_attestations(
            self.root,
            {run_digest: {"manifest": manifest, "path": first}},
            ["demo"],
            "HEAD",
        )
        self.assertEqual(published_catalog[0]["selectionStatus"], "passed")
        self.assertEqual(
            published_catalog[0]["run"]["stdout"]["text"],
            "certificate: valid\n",
        )

        projections = Path(first_parent.name) / "projections"
        pending = plan_verifier_attestation(
            self.root, projections, "demo", transaction, "HEAD"
        )
        self.assertTrue(pending["eligible"])
        pending_status = objective_attestation_status(
            self.root, projections, "demo", transaction, "HEAD"
        )
        self.assertTrue(pending_status["requested"])
        self.assertFalse(pending_status["terminal"])
        self.assertIsNone(pending_status["evidence"])
        batch = publish_batch(projections, [first])
        self.assertEqual(batch["objects"][0]["runKind"], "verifier-attestation")
        self.assertTrue(
            (
                projections
                / Path(batch["objects"][0]["path"])
                / "attestation.json"
            ).is_file()
        )
        published = plan_verifier_attestation(
            self.root, projections, "demo", transaction, "HEAD"
        )
        self.assertFalse(published["eligible"])
        self.assertEqual(
            published["publishedRunDigest"], batch["objects"][0]["runDigest"]
        )
        terminal_status = objective_attestation_status(
            self.root, projections, "demo", transaction, "HEAD"
        )
        self.assertTrue(terminal_status["terminal"])
        self.assertEqual(
            terminal_status["evidence"]["runDigest"],
            batch["objects"][0]["runDigest"],
        )
        self.assertEqual(terminal_status["evidence"]["status"], "passed")
        self.assertEqual(
            terminal_status["evidence"]["stdout"]["text"],
            "certificate: valid\n",
        )

        conflicting = Path(second_parent.name) / "conflicting"

        def failing_executor(
            _materialized: Path,
            _spec: dict[str, object],
            _request: dict[str, object],
        ) -> ExecutionResult:
            return ExecutionResult(1, b"invalid\n", b"")

        run_verifier_attestation_bundle(
            self.root,
            "demo",
            transaction,
            "HEAD",
            conflicting,
            executor=failing_executor,
        )
        with self.assertRaisesRegex(MathFlowError, "different published attestation"):
            publish_batch(projections, [conflicting])

        empty_projection = Path(second_parent.name) / "empty-projections"
        with self.assertRaisesRegex(MathFlowError, "different outcomes"):
            publish_batch(empty_projection, [first, conflicting])
        self.assertFalse(empty_projection.exists())

    def test_later_unrelated_commit_does_not_make_attestation_stale(self) -> None:
        transaction = self.add_contribution()
        output_parent = tempfile.TemporaryDirectory()
        self.addCleanup(output_parent.cleanup)
        output = Path(output_parent.name) / "run"
        run_verifier_attestation_bundle(
            self.root,
            "demo",
            transaction,
            "HEAD",
            output,
            executor=self.passing_executor,
        )
        write(self.root / "docs/maintenance.md", "Unrelated maintenance.\n")
        git(self.root, "add", ".")
        git(self.root, "commit", "-qm", "Unrelated maintenance")
        verified = verify_verifier_attestation_bundle(self.root, output, "HEAD")
        self.assertEqual(verified["transactionId"], transaction)
        with self.assertRaisesRegex(MathFlowError, "not an ancestor"):
            verify_verifier_attestation_bundle(self.root, output, self.base)

    def test_validity_v3_defers_only_until_terminal_attestation_and_binds_it(self) -> None:
        transaction = self.add_contribution()
        judge_value = json.loads(
            (
                Path(__file__).parents[1]
                / "protocol/judges/openrouter-validity-judgment-v3.json"
            ).read_text(encoding="utf-8")
        )
        judge_value.pop("contextProjection")
        judge = self.root / "validity-v3.json"
        write(judge, json.dumps(judge_value, indent=2) + "\n")
        projections = self.root / "projection-state"

        pending = plan_primary_judgment_coverage(
            self.root, projections, "demo", judge, "HEAD"
        )
        self.assertEqual(pending["missingTransactions"], [])
        self.assertEqual(
            [item["transactionId"] for item in pending["deferredTransactions"]],
            [transaction],
        )
        partial_inputs = plan_primary_judgment_inputs(
            self.root, projections, "demo", judge, "HEAD"
        )
        self.assertEqual(partial_inputs["bundles"], [])
        self.assertEqual(
            [
                item["transactionId"]
                for item in partial_inputs["deferredTransactions"]
            ],
            [transaction],
        )
        with self.assertRaisesRegex(MathFlowError, "deferred until objective attestation"):
            run_primary_judgment_bundle(
                self.root,
                "demo",
                judge,
                "HEAD",
                [transaction],
                self.root / "premature-judgment",
                projection_root=projections,
                transport=lambda _: {},
            )

        attestation = self.root / "attestation-run"
        run_verifier_attestation_bundle(
            self.root,
            "demo",
            transaction,
            "HEAD",
            attestation,
            executor=self.passing_executor,
        )
        published_attestation = publish_batch(projections, [attestation])["objects"][0]
        ready = plan_primary_judgment_coverage(
            self.root, projections, "demo", judge, "HEAD"
        )
        self.assertEqual(ready["deferredTransactions"], [])
        self.assertEqual(
            [item["transactionId"] for item in ready["missingTransactions"]],
            [transaction],
        )

        responses = iter(
            [
                {
                    "id": "report",
                    "model": "openai/gpt-5.6-sol",
                    "choices": [
                        {
                            "finish_reason": "stop",
                            "message": {
                                "content": "The pinned execution passes and its exact predicate matches the bounded certificate claim."
                            },
                        }
                    ],
                },
                {
                    "id": "extract",
                    "model": "openai/gpt-5.6-sol",
                    "choices": [
                        {
                            "finish_reason": "stop",
                            "message": {
                                "content": json.dumps(
                                    {
                                        "assessments": [
                                            {
                                                "claimKey": "demo/certificate",
                                                "status": "valid",
                                                "premiseStatus": "not-required",
                                                "summary": "The exact pinned check establishes the bounded claim.",
                                                "scopeQualifications": [],
                                                "evidenceIssues": [],
                                                "evidenceTransactionIds": [],
                                                "requiredDependencyTransactionIds": [],
                                            }
                                        ]
                                    }
                                )
                            },
                        }
                    ],
                },
            ]
        )
        judgment_dir = self.root / "validity-v3-run"
        manifest = run_primary_judgment_bundle(
            self.root,
            "demo",
            judge,
            "HEAD",
            [transaction],
            judgment_dir,
            projection_root=projections,
            transport=lambda _: next(responses),
        )
        packet = json.loads(
            read_verified_artifact(
                judgment_dir, manifest, "judgment-dependency-packet"
            )
        )
        self.assertEqual(packet["schemaVersion"], 2)
        self.assertEqual(
            packet["objectiveAttestation"]["runDigest"],
            published_attestation["runDigest"],
        )
        self.assertEqual(
            manifest["inputs"]["objectiveAttestationRunDigest"],
            published_attestation["runDigest"],
        )
        _, judgment, _ = load_judgment_bundle(judgment_dir)
        self.assertEqual(judgment["schemaVersion"], 3)
        publish_batch(projections, [judgment_dir])
        replanned = plan_primary_judgment_coverage(
            self.root,
            projections,
            "demo",
            judge,
            "HEAD",
            subject_transaction_id=transaction,
        )
        self.assertEqual(replanned["targetSubjectTransactionId"], transaction)
        self.assertEqual(replanned["missingTransactions"], [])

    def test_validity_v3_coverage_keeps_independent_subject_ready(self) -> None:
        attestation_subject = self.add_contribution()
        plain = self.root / "problems/demo/contributions/plain-proof"
        write(plain / "README.md", "# Plain proof\n\n## Claim\n\nA separate claim.\n")
        git(self.root, "add", ".")
        git(self.root, "commit", "-qm", "Add independent proof")
        plain_subject = git(self.root, "rev-parse", "HEAD")
        judge_value = json.loads(
            (
                Path(__file__).parents[1]
                / "protocol/judges/openrouter-validity-judgment-v3.json"
            ).read_text(encoding="utf-8")
        )
        judge_value.pop("contextProjection")
        judge = self.root / "validity-v3.json"
        write(judge, json.dumps(judge_value, indent=2) + "\n")
        coverage = plan_primary_judgment_coverage(
            self.root, self.root / "projection-state", "demo", judge, "HEAD"
        )
        self.assertEqual(
            [item["transactionId"] for item in coverage["missingTransactions"]],
            [plain_subject],
        )
        self.assertEqual(
            [item["transactionId"] for item in coverage["deferredTransactions"]],
            [attestation_subject],
        )

    def test_validity_v4_binds_subject_and_declared_reference_attestations_only(
        self,
    ) -> None:
        reference = self.add_claim_contribution(
            "verified-reference",
            verification=True,
            statement="The declared computational premise is certified.",
        )
        unrelated = self.add_claim_contribution(
            "unrelated-verified-work",
            verification=True,
            statement="UNRELATED_ATTESTED_ASSERTION must stay outside the packet.",
        )
        subject = self.add_claim_contribution(
            "dependent-attested",
            dependencies=[reference],
            verification=True,
            statement="The subject follows from the declared computational premise.",
        )
        projections = self.root / "projection-state-v4"
        attestation_dirs = []
        published_by_transaction: dict[str, str] = {}
        for transaction in (reference, unrelated, subject):
            output = self.root / f"attestation-{transaction[:8]}"
            run_verifier_attestation_bundle(
                self.root,
                "demo",
                transaction,
                "HEAD",
                output,
                executor=self.passing_executor,
            )
            attestation_dirs.append(output)
        published = publish_batch(projections, attestation_dirs)["objects"]
        for item in published:
            manifest = json.loads(
                (projections / item["path"] / "run.json").read_text(
                    encoding="utf-8"
                )
            )
            published_by_transaction[manifest["inputs"]["transactionId"]] = item[
                "runDigest"
            ]

        responses = iter(
            [
                {
                    "id": "report-v4",
                    "model": "openai/gpt-5.6-sol",
                    "choices": [
                        {
                            "finish_reason": "stop",
                            "message": {
                                "content": "The bounded subject and reference evidence establish the claim."
                            },
                        }
                    ],
                },
                {
                    "id": "extract-v4",
                    "model": "openai/gpt-5.6-sol",
                    "choices": [
                        {
                            "finish_reason": "stop",
                            "message": {
                                "content": json.dumps(
                                    {
                                        "assessments": [
                                            {
                                                "claimKey": "demo/dependent-attested",
                                                "status": "valid",
                                                "premiseStatus": "satisfied",
                                                "summary": "The exact bounded evidence establishes the claim.",
                                                "scopeQualifications": [],
                                                "evidenceIssues": [],
                                                "evidenceTransactionIds": [reference],
                                                "requiredDependencyTransactionIds": [
                                                    reference
                                                ],
                                            }
                                        ]
                                    }
                                )
                            },
                        }
                    ],
                },
            ]
        )
        requests: list[dict[str, object]] = []

        def transport(request: dict[str, object]) -> dict[str, object]:
            requests.append(request)
            return next(responses)

        output = self.root / "validity-v4-run"
        manifest = run_primary_judgment_bundle(
            self.root,
            "demo",
            self.validity_v4_judge(),
            "HEAD",
            [subject],
            output,
            projection_root=projections,
            transport=transport,
        )
        packet = json.loads(
            read_verified_artifact(output, manifest, "judgment-dependency-packet")
        )
        self.assertEqual(packet["schemaVersion"], 3)
        self.assertIsNone(packet["knowledgeContext"])
        self.assertEqual(packet["declaredReferenceTransactionIds"], [reference])
        self.assertEqual(
            [
                (entry["transactionId"], entry["relation"])
                for entry in packet["objectiveAttestations"]
            ],
            [(subject, "subject"), (reference, "declared-reference")],
        )
        expected_runs = {
            subject: published_by_transaction[subject],
            reference: published_by_transaction[reference],
        }
        self.assertEqual(
            manifest["inputs"][
                "objectiveAttestationRunDigestsByTransactionId"
            ],
            expected_runs,
        )
        self.assertNotIn(unrelated, expected_runs)
        report_prompt = requests[0]["messages"][1]["content"]
        self.assertIn("declared computational premise", report_prompt)
        self.assertNotIn("UNRELATED_ATTESTED_ASSERTION", report_prompt)
        self.assertNotIn("unrelated-verified-work", report_prompt)
        loaded_manifest, judgment, _ = load_judgment_bundle(output)
        self.assertEqual(loaded_manifest["outputProfile"], "math-flow/validity-judgment-v4")
        self.assertEqual(judgment["schemaVersion"], 4)
        self.assertEqual(judgment["dependencyPacketDigest"], packet["packetDigest"])
        manifest_path = output / "run.json"
        forged_manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        forged_manifest["inputs"][
            "objectiveAttestationRunDigestsByTransactionId"
        ][unrelated] = published_by_transaction[unrelated]
        manifest_path.write_text(
            json.dumps(forged_manifest, indent=2) + "\n", encoding="utf-8"
        )
        with self.assertRaisesRegex(MathFlowError, "does not bind"):
            load_judgment_bundle(output)

    def test_validity_v4_pending_reference_defers_only_dependent_subject(self) -> None:
        reference = self.add_claim_contribution(
            "pending-reference", verification=True
        )
        dependent = self.add_claim_contribution(
            "dependent-proof", dependencies=[reference]
        )
        independent = self.add_claim_contribution("independent-proof")
        projections = self.root / "projection-state-v4"
        judge = self.validity_v4_judge()

        coverage = plan_primary_judgment_coverage(
            self.root, projections, "demo", judge, "HEAD"
        )
        self.assertEqual(
            [item["transactionId"] for item in coverage["missingTransactions"]],
            [independent],
        )
        self.assertEqual(
            [item["transactionId"] for item in coverage["deferredTransactions"]],
            [reference, dependent],
        )
        dependent_gate = next(
            item
            for item in coverage["deferredTransactions"]
            if item["transactionId"] == dependent
        )
        self.assertEqual(
            dependent_gate["pendingObjectiveAttestations"],
            [
                {
                    "transactionId": reference,
                    "relation": "declared-reference",
                    "requestDigest": dependent_gate[
                        "pendingObjectiveAttestations"
                    ][0]["requestDigest"],
                }
            ],
        )
        dependent_only = plan_primary_judgment_coverage(
            self.root,
            projections,
            "demo",
            judge,
            "HEAD",
            subject_transaction_id=dependent,
        )
        self.assertEqual(dependent_only["missingTransactions"], [])
        self.assertEqual(
            [
                item["transactionId"]
                for item in dependent_only["deferredTransactions"]
            ],
            [dependent],
        )
        independent_only = plan_primary_judgment_coverage(
            self.root,
            projections,
            "demo",
            judge,
            "HEAD",
            subject_transaction_id=independent,
        )
        self.assertEqual(
            [
                item["transactionId"]
                for item in independent_only["missingTransactions"]
            ],
            [independent],
        )
        self.assertEqual(independent_only["deferredTransactions"], [])
        with self.assertRaisesRegex(
            MathFlowError, f"declared-reference {reference}"
        ):
            run_primary_judgment_bundle(
                self.root,
                "demo",
                judge,
                "HEAD",
                [dependent],
                self.root / "premature-v4-judgment",
                projection_root=projections,
                transport=lambda _: {},
            )

        attestation = self.root / "pending-reference-attestation"
        run_verifier_attestation_bundle(
            self.root,
            "demo",
            reference,
            "HEAD",
            attestation,
            executor=self.passing_executor,
        )
        publish_batch(projections, [attestation])
        ready = plan_primary_judgment_coverage(
            self.root, projections, "demo", judge, "HEAD"
        )
        self.assertEqual(ready["deferredTransactions"], [])
        self.assertEqual(
            [item["transactionId"] for item in ready["missingTransactions"]],
            [reference, dependent, independent],
        )
        before_ready = {
            item["transactionId"] for item in coverage["missingTransactions"]
        }
        self.assertEqual(
            [
                item["transactionId"]
                for item in ready["missingTransactions"]
                if item["transactionId"] not in before_ready
            ],
            [reference, dependent],
        )
        dependent_ready = plan_primary_judgment_coverage(
            self.root,
            projections,
            "demo",
            judge,
            "HEAD",
            subject_transaction_id=dependent,
        )
        self.assertEqual(dependent_ready["deferredTransactions"], [])
        self.assertEqual(
            [
                item["transactionId"]
                for item in dependent_ready["missingTransactions"]
            ],
            [dependent],
        )

    def test_validity_v4_reference_without_request_neither_blocks_nor_expands(
        self,
    ) -> None:
        reference = self.add_claim_contribution("ordinary-reference")
        subject = self.add_claim_contribution(
            "ordinary-dependent", dependencies=[reference]
        )
        projections = self.root / "projection-state-v4"
        coverage = plan_primary_judgment_coverage(
            self.root,
            projections,
            "demo",
            self.validity_v4_judge(),
            "HEAD",
        )
        self.assertEqual(coverage["deferredTransactions"], [])
        self.assertEqual(
            [item["transactionId"] for item in coverage["missingTransactions"]],
            [reference, subject],
        )
        source = load_source(self.root, "demo", "HEAD")
        packet = build_evidence_packet_v4(
            self.root,
            projections,
            "demo",
            source,
            "HEAD",
            subject,
            None,
        )
        self.assertEqual(packet["objectiveAttestations"], [])

    def test_validity_v4_failed_and_error_reference_attestations_are_terminal(
        self,
    ) -> None:
        failed_reference = self.add_claim_contribution(
            "failed-reference", verification=True
        )
        error_reference = self.add_claim_contribution(
            "error-reference", verification=True
        )
        subject = self.add_claim_contribution(
            "terminal-outcome-dependent",
            dependencies=[failed_reference, error_reference],
        )

        def failed_executor(
            _materialized: Path,
            _spec: dict[str, object],
            _request: dict[str, object],
        ) -> ExecutionResult:
            return ExecutionResult(1, b"predicate failed\n", b"")

        def error_executor(
            _materialized: Path,
            _spec: dict[str, object],
            _request: dict[str, object],
        ) -> ExecutionResult:
            return ExecutionResult(125, b"", b"executor error\n")

        failed = self.root / "failed-attestation"
        error = self.root / "error-attestation"
        run_verifier_attestation_bundle(
            self.root,
            "demo",
            failed_reference,
            "HEAD",
            failed,
            executor=failed_executor,
        )
        run_verifier_attestation_bundle(
            self.root,
            "demo",
            error_reference,
            "HEAD",
            error,
            executor=error_executor,
        )
        projections = self.root / "projection-state-v4"
        publish_batch(projections, [failed, error])
        source = load_source(self.root, "demo", "HEAD")
        packet = build_evidence_packet_v4(
            self.root,
            projections,
            "demo",
            source,
            "HEAD",
            subject,
            None,
        )
        self.assertEqual(
            [entry["attestation"]["status"] for entry in packet["objectiveAttestations"]],
            ["failed", "error"],
        )
        coverage = plan_primary_judgment_coverage(
            self.root,
            projections,
            "demo",
            self.validity_v4_judge(),
            "HEAD",
        )
        self.assertEqual(coverage["deferredTransactions"], [])
        self.assertIn(
            subject,
            [item["transactionId"] for item in coverage["missingTransactions"]],
        )

    def test_forged_environment_is_rejected_even_when_digests_are_rewritten(self) -> None:
        transaction = self.add_contribution()
        output_parent = tempfile.TemporaryDirectory()
        self.addCleanup(output_parent.cleanup)
        output = Path(output_parent.name) / "run"
        run_verifier_attestation_bundle(
            self.root,
            "demo",
            transaction,
            "HEAD",
            output,
            executor=self.passing_executor,
        )
        attestation_path = output / "attestation.json"
        attestation = json.loads(attestation_path.read_text(encoding="utf-8"))
        attestation["environment"]["image"] = "python@sha256:" + "f" * 64
        core = {key: value for key, value in attestation.items() if key != "attestationId"}
        attestation["attestationId"] = "sha256:" + __import__("hashlib").sha256(
            json.dumps(core, sort_keys=True, separators=(",", ":")).encode()
        ).hexdigest()
        rendered = json.dumps(attestation, indent=2) + "\n"
        attestation_path.write_text(rendered, encoding="utf-8")
        manifest_path = output / "run.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        record = next(
            item for item in manifest["artifacts"] if item["role"] == "verifier-attestation"
        )
        record["digest"] = sha256_bytes(rendered.encode())
        record["bytes"] = len(rendered.encode())
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        with self.assertRaisesRegex(MathFlowError, "environment is unpinned or forged"):
            verify_verifier_attestation_bundle(self.root, output, "HEAD")

    def test_replay_detects_nondeterministic_output(self) -> None:
        transaction = self.add_contribution()
        output_parent = tempfile.TemporaryDirectory()
        self.addCleanup(output_parent.cleanup)
        output = Path(output_parent.name) / "run"
        run_verifier_attestation_bundle(
            self.root,
            "demo",
            transaction,
            "HEAD",
            output,
            executor=self.passing_executor,
        )

        def changed_output(
            _materialized: Path,
            _spec: dict[str, object],
            _request: dict[str, object],
        ) -> ExecutionResult:
            return ExecutionResult(0, b"different\n", b"")

        with self.assertRaisesRegex(MathFlowError, "replay output does not match"):
            verify_verifier_attestation_bundle(
                self.root,
                output,
                "HEAD",
                replay=True,
                executor=changed_output,
            )

    @patch("math_flow.attestations._run_bounded_process")
    def test_oci_executor_enforces_pinned_non_shell_isolation(self, run) -> None:
        run.return_value = ExecutionResult(0, b"ok\n", b"")
        request = {
            "schemaVersion": 1,
            "verifier": {
                "id": self.spec["id"],
                "specDigest": verifier_spec_digest(self.spec),
            },
            "entrypoint": "verify.py",
            "arguments": ["certificate.bin"],
        }
        result = docker_oci_executor(self.root, self.spec, request)
        self.assertEqual(result.exit_code, 0)
        invocation = run.call_args.args[0]
        self.assertIsInstance(invocation, list)
        self.assertEqual(invocation[:3], ["docker", "run", "--rm"])
        self.assertIn("--cidfile", invocation)
        self.assertIn("--network", invocation)
        self.assertEqual(invocation[invocation.index("--network") + 1], "none")
        self.assertIn("--read-only", invocation)
        self.assertEqual(invocation[invocation.index("--user") + 1], "65534:65534")
        self.assertIn("--cap-drop", invocation)
        self.assertEqual(invocation[invocation.index("--cap-drop") + 1], "ALL")
        self.assertIn(str(self.spec["environment"]["image"]), invocation)
        self.assertEqual(invocation[-3:], ["-B", "verify.py", "certificate.bin"])
        self.assertEqual(run.call_args.kwargs["timeout_seconds"], 300)
        self.assertEqual(run.call_args.kwargs["maximum_output_bytes"], 262144)

    def test_process_output_is_bounded_before_it_can_fill_memory(self) -> None:
        invocation = [
            sys.executable,
            "-c",
            "import sys; sys.stdout.buffer.write(b'x' * 200000)",
        ]
        with self.assertRaisesRegex(MathFlowError, "maximumOutputBytes"):
            _run_bounded_process(
                invocation,
                timeout_seconds=10,
                maximum_output_bytes=4096,
            )


if __name__ == "__main__":
    unittest.main()
