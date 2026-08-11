from __future__ import annotations

import contextlib
import io
import json
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

from math_flow.artifacts import ArtifactBundle, load_manifest, sha256_bytes
from math_flow.cli import main
from math_flow.coordination import lane_id, publish_batch, record_completed_inputs
from math_flow.errors import MathFlowError
from math_flow.governance import resolve_projection
from math_flow.projection_dependencies import resolve_projection_dependencies
from math_flow.repository import ledger, sha256_json


def write(path: Path, value: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(value, encoding="utf-8")


def write_json(path: Path, value: object) -> None:
    write(path, json.dumps(value, indent=2) + "\n")


def git(root: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", *args],
        cwd=root,
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    return result.stdout.strip()


def projection_spec(
    projection_id: str, dependencies: list[dict[str, str]] | None = None
) -> dict[str, object]:
    value: dict[str, object] = {
        "schemaVersion": 1,
        "id": projection_id,
        "description": f"Projection {projection_id}",
        "status": "active",
        "engine": "openrouter-repository-v1",
        "allowedProblems": ["demo"],
        "primaryJudge": "protocol/judges/primary.json",
        "reconciliationJudge": "protocol/judges/reconciliation.json",
        "knowledgeBuilder": "protocol/judges/builder.json",
        "scheduling": {
            "judgmentMaxParallel": 8,
            "knowledgeMinimumIntervalSeconds": 0,
            "maximumJudgmentsPerBuild": 100,
        },
    }
    if dependencies is not None:
        value["dependencies"] = dependencies
    return value


class ProjectionDependencyTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        self.projection_root = self.root / "published"
        git(self.root, "init", "-q")
        git(self.root, "config", "user.name", "Dependency Test")
        git(self.root, "config", "user.email", "dependency@example.com")
        write(self.root / "problems/demo/problem.md", "# Demo\n")
        for name, implementation in {
            "primary": "openrouter-markdown-judgment-v1",
            "reconciliation": "openrouter-markdown-reconciliation-v1",
            "builder": "openrouter-knowledge-builder-v1",
        }.items():
            write_json(
                self.root / f"protocol/judges/{name}.json",
                {"implementation": implementation},
            )
        write_json(
            self.root / "protocol/projections/knowledge-v1.json",
            projection_spec("knowledge-v1"),
        )
        write_json(
            self.root / "protocol/projections/credit-v1.json",
            projection_spec(
                "credit-v1",
                [
                    {
                        "name": "knowledge",
                        "projectionId": "knowledge-v1",
                        "artifactRole": "knowledge-state",
                    }
                ],
            ),
        )
        git(self.root, "add", ".")
        git(self.root, "commit", "-qm", "Initialize dependency fixture")
        self.head = git(self.root, "rev-parse", "HEAD")
        self._publish_knowledge_state()

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def _publish_knowledge_state(self) -> None:
        source = ledger(self.root, "demo", self.head)
        producer = resolve_projection(
            self.root, "knowledge-v1", "demo", self.head
        )
        builder = json.loads(
            (self.root / "protocol/judges/builder.json").read_text(
                encoding="utf-8"
            )
        )
        builder_digest = f"sha256:{sha256_json(builder)}"
        projection_digest = str(producer["projectionSpecDigest"])
        identifier = lane_id("demo", builder_digest, projection_digest)

        bundle = self.root / "knowledge-bundle"
        writer = ArtifactBundle(bundle)
        writer.add_json(
            "state/state.json",
            {"schemaVersion": 1, "problemId": "demo", "nodes": []},
            "knowledge-state",
        )
        writer.finalize(
            {
                "protocolVersion": 1,
                "runKind": "knowledge-build",
                "problemId": "demo",
                "ledgerHead": source["ledgerHead"],
                "problemLedgerHead": source["problemLedgerHead"],
                "problemLedgerDigest": source["problemLedgerDigest"],
                "judgeSpec": {"id": "builder", "digest": builder_digest},
                "inputs": {
                    "laneId": identifier,
                    "problemId": "demo",
                    "builderSpecDigest": builder_digest,
                    "projectionSpecDigest": projection_digest,
                },
            }
        )
        _, run_digest = load_manifest(bundle)
        digest_hex = run_digest.removeprefix("sha256:")
        target = (
            self.projection_root
            / "objects"
            / "knowledge-build"
            / digest_hex[:2]
            / digest_hex
        )
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copytree(bundle, target)

        scheduler = self.projection_root / "coordination/scheduler.json"
        lane = record_completed_inputs(
            scheduler,
            "demo",
            builder_digest,
            [],
            [],
            0,
            10,
            projection_digest,
        )
        lane["latestStateRun"] = run_digest
        lane["lastCompletedAt"] = 10
        lane["nextEligibleAt"] = None
        state = {
            "schemaVersion": 1,
            "lanes": {identifier: lane},
        }
        write_json(scheduler, state)

    def test_resolves_exact_verified_dependency_lock_and_cli(self) -> None:
        first = resolve_projection_dependencies(
            self.root,
            self.projection_root,
            "credit-v1",
            "demo",
            self.head,
        )
        second = resolve_projection_dependencies(
            self.root,
            self.projection_root,
            "credit-v1",
            "demo",
            self.head,
        )
        self.assertEqual(first, second)
        self.assertRegex(
            first["dependencyLockDigest"], r"^sha256:[0-9a-f]{64}$"
        )
        dependency = first["dependencies"][0]
        self.assertEqual(dependency["name"], "knowledge")
        self.assertEqual(dependency["artifact"]["role"], "knowledge-state")
        self.assertRegex(dependency["runDigest"], r"^sha256:[0-9a-f]{64}$")

        output = self.root / "dependency-lock.json"
        self.assertEqual(
            main(
                [
                    "--root",
                    str(self.root),
                    "resolve-projection-dependencies",
                    "--projection",
                    "credit-v1",
                    "--problem",
                    "demo",
                    "--head",
                    self.head,
                    "--projection-dir",
                    str(self.projection_root),
                    "--output",
                    str(output),
                ]
            ),
            0,
        )
        self.assertEqual(json.loads(output.read_text(encoding="utf-8")), first)

    def test_rejects_stale_or_unfinished_dependency(self) -> None:
        write(
            self.root / "problems/demo/contributions/new-result/README.md",
            "# New result\n",
        )
        git(self.root, "add", ".")
        git(self.root, "commit", "-qm", "Advance demo ledger")
        new_head = git(self.root, "rev-parse", "HEAD")
        with self.assertRaisesRegex(MathFlowError, "is stale"):
            resolve_projection_dependencies(
                self.root,
                self.projection_root,
                "credit-v1",
                "demo",
                new_head,
            )

        state_path = self.projection_root / "coordination/scheduler.json"
        state = json.loads(state_path.read_text(encoding="utf-8"))
        lane = next(iter(state["lanes"].values()))
        pending = "sha256:" + "1" * 64
        lane["observedJudgmentIds"] = [pending]
        lane["pendingJudgmentIds"] = [pending]
        lane["nextEligibleAt"] = 10
        write_json(state_path, state)
        with self.assertRaisesRegex(MathFlowError, "pending knowledge inputs"):
            resolve_projection_dependencies(
                self.root,
                self.projection_root,
                "credit-v1",
                "demo",
                self.head,
            )

    def test_rejects_unsupported_dependency_role_before_execution(self) -> None:
        consumer = projection_spec(
            "credit-v1",
            [
                {
                    "name": "judgments",
                    "projectionId": "knowledge-v1",
                    "artifactRole": "judgment-record",
                }
            ],
        )
        write_json(
            self.root / "protocol/projections/credit-v1.json", consumer
        )
        git(self.root, "add", ".")
        git(self.root, "commit", "-qm", "Request unsupported dependency role")
        head = git(self.root, "rev-parse", "HEAD")

        stderr = io.StringIO()
        with contextlib.redirect_stderr(stderr):
            status = main(
                [
                    "--root",
                    str(self.root),
                    "resolve-projection-dependencies",
                    "--projection",
                    "credit-v1",
                    "--problem",
                    "demo",
                    "--head",
                    head,
                    "--projection-dir",
                    str(self.projection_root),
                ]
            )
        self.assertEqual(status, 2)
        self.assertIn("role is not supported", stderr.getvalue())

    def test_rejects_dependency_run_with_the_wrong_builder_identity(self) -> None:
        scheduler_path = self.projection_root / "coordination/scheduler.json"
        scheduler = json.loads(scheduler_path.read_text(encoding="utf-8"))
        lane = next(iter(scheduler["lanes"].values()))
        prior_digest = str(lane["latestStateRun"])
        prior_hex = prior_digest.removeprefix("sha256:")
        prior = (
            self.projection_root
            / "objects"
            / "knowledge-build"
            / prior_hex[:2]
            / prior_hex
        )
        manifest = json.loads((prior / "run.json").read_text(encoding="utf-8"))
        manifest["judgeSpec"]["digest"] = "sha256:" + "f" * 64
        rendered = json.dumps(manifest, indent=2) + "\n"
        bad_digest = sha256_bytes(rendered.encode("utf-8"))
        bad_hex = bad_digest.removeprefix("sha256:")
        bad = (
            self.projection_root
            / "objects"
            / "knowledge-build"
            / bad_hex[:2]
            / bad_hex
        )
        bad.parent.mkdir(parents=True, exist_ok=True)
        shutil.copytree(prior, bad)
        write(bad / "run.json", rendered)
        lane["latestStateRun"] = bad_digest
        write_json(scheduler_path, scheduler)

        with self.assertRaisesRegex(MathFlowError, "does not match 'knowledge-v1'"):
            resolve_projection_dependencies(
                self.root,
                self.projection_root,
                "credit-v1",
                "demo",
                self.head,
            )

    def test_publisher_accepts_credit_assignment_as_an_independent_run_kind(self) -> None:
        dependency_lock = resolve_projection_dependencies(
            self.root,
            self.projection_root,
            "credit-v1",
            "demo",
            self.head,
        )
        bundle = self.root / "credit-bundle"
        writer = ArtifactBundle(bundle)
        writer.add_json(
            "control/dependencies.json", dependency_lock, "dependency-lock"
        )
        writer.add_text(
            "report.md",
            "# Credit assessment\n\nNo contributions yet.\n",
            "credit-report",
            "text/markdown",
        )
        writer.add_json(
            "credit/index.json",
            {
                "schemaVersion": 1,
                "problemId": "demo",
                "dependencyLockDigest": dependency_lock[
                    "dependencyLockDigest"
                ],
                "assignments": [],
            },
            "credit-index",
        )
        source = ledger(self.root, "demo", self.head)
        writer.finalize(
            {
                "protocolVersion": 1,
                "runKind": "credit-assignment",
                "problemId": "demo",
                "ledgerHead": source["ledgerHead"],
                "problemLedgerHead": source["problemLedgerHead"],
                "problemLedgerDigest": source["problemLedgerDigest"],
                "judgeSpec": {
                    "id": "credit-fixture",
                    "digest": "sha256:" + "2" * 64,
                },
                "runner": {
                    "implementation": "credit-fixture-v1",
                    "mathFlowVersion": "0.5.0",
                },
                "judgeBuilder": {
                    "inputBuilder": "credit-input-fixture-v1",
                    "invocationAdapter": "none",
                    "outputAdapter": "credit-index-fixture-v1",
                    "reducer": None,
                },
                "baseRun": None,
                "outputProfile": "math-flow/credit-assignment-markdown-v1",
                "requestDigests": [],
                "providerRuns": [],
                "inputs": {
                    "dependencyLockDigest": dependency_lock[
                        "dependencyLockDigest"
                    ]
                },
            }
        )

        publication = self.root / "credit-publication"
        batch = publish_batch(publication, [bundle])
        self.assertEqual(batch["objects"][0]["runKind"], "credit-assignment")
        self.assertIn(
            "/credit-assignment/",
            "/" + batch["objects"][0]["path"],
        )


if __name__ == "__main__":
    unittest.main()
