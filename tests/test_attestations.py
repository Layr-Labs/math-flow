from __future__ import annotations

import json
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from math_flow.artifacts import sha256_bytes, verify_bundle
from math_flow.attestations import (
    ExecutionResult,
    docker_oci_executor,
    run_verifier_attestation_bundle,
    verifier_spec_digest,
    verify_verifier_attestation_bundle,
)
from math_flow.coordination import publish_batch
from math_flow.errors import MathFlowError
from math_flow.repository import validate_pr, validate_tree


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

        projections = Path(first_parent.name) / "projections"
        batch = publish_batch(projections, [first])
        self.assertEqual(batch["objects"][0]["runKind"], "verifier-attestation")
        self.assertTrue(
            (
                projections
                / Path(batch["objects"][0]["path"])
                / "attestation.json"
            ).is_file()
        )

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

    @patch("math_flow.attestations.subprocess.run")
    def test_oci_executor_enforces_pinned_non_shell_isolation(self, run) -> None:
        run.return_value = subprocess.CompletedProcess(
            args=[], returncode=0, stdout=b"ok\n", stderr=b""
        )
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
        self.assertIn("--network", invocation)
        self.assertEqual(invocation[invocation.index("--network") + 1], "none")
        self.assertIn("--read-only", invocation)
        self.assertEqual(invocation[invocation.index("--user") + 1], "65534:65534")
        self.assertIn("--cap-drop", invocation)
        self.assertEqual(invocation[invocation.index("--cap-drop") + 1], "ALL")
        self.assertIn(str(self.spec["environment"]["image"]), invocation)
        self.assertEqual(invocation[-3:], ["-B", "verify.py", "certificate.bin"])
        self.assertEqual(run.call_args.kwargs["timeout"], 300)
        self.assertNotIn("shell", run.call_args.kwargs)


if __name__ == "__main__":
    unittest.main()
