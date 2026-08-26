from __future__ import annotations

import base64
import json
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

from math_flow.errors import MathFlowError
from math_flow.repository import canonical_json, sha256_json
from math_flow.research_topology import empty_research_program_state_v2
from math_flow.work_accounting import build_work_accounting_state, make_root_contract
from math_flow.work_accounting_pipeline import (
    CASConflict,
    ImmutableConflict,
    initialize_work_accounting_pipeline,
)
from math_flow.work_accounting_projection_store import (
    ProjectionBranchWorkAccountingStore,
    publish_work_accounting_projection,
    validate_work_accounting_projection_marker,
    validate_work_accounting_projection_publication,
)


SPEC = "sha256:" + "a" * 64
ROOT_CONTRACT = "sha256:" + "b" * 64
KNOWLEDGE = "sha256:" + "c" * 64
ACCOUNTING = "sha256:" + "d" * 64
SCHEDULE = "sha256:" + "e" * 64


def git(root: Path, *arguments: str) -> str:
    result = subprocess.run(
        ["git", *arguments],
        cwd=root,
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    return result.stdout.strip()


def pipeline_bytes(*, formed_digest: str = KNOWLEDGE, problem: str = "demo") -> bytes:
    core = {
        "schemaVersion": 1,
        "problemId": problem,
        "projectionId": "work-accounting-v1",
        "projectionSpecDigest": SPEC,
        "rootContractDigest": ROOT_CONTRACT,
        "phase": "ready",
        "formedKnowledgeStateDigest": formed_digest,
        "accountingStateDigest": ACCOUNTING,
        "scheduleDigest": SCHEDULE,
        "completedTransitions": [],
        "pendingTransition": None,
    }
    value = {
        **core,
        "pipelineStateDigest": f"sha256:{sha256_json(core)}",
    }
    return (canonical_json(value) + "\n").encode("utf-8")


class FakeResponse:
    def __init__(self, value: object) -> None:
        self.content = json.dumps(value).encode("utf-8")

    def __enter__(self):
        return self

    def __exit__(self, *arguments):
        return None

    def read(self) -> bytes:
        return self.content


def signed_commit(number: int) -> dict[str, object]:
    oid = f"{number:040x}"
    return {
        "oid": oid,
        "url": f"https://github.com/example/math-flow/commit/{oid}",
        "signature": {
            "isValid": True,
            "wasSignedByGitHub": True,
            "signer": {"login": "web-flow"},
            "state": "VALID",
        },
    }


class WorkAccountingProjectionStoreTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        git(self.root, "init", "-q")
        git(self.root, "config", "user.name", "Projection Adapter Test")
        git(self.root, "config", "user.email", "projection-adapter@example.com")
        problem = self.root / "problems/demo/problem.md"
        problem.parent.mkdir(parents=True)
        problem.write_text("# Demo\n", encoding="utf-8")
        git(self.root, "add", ".")
        git(self.root, "commit", "-qm", "initialize projections")
        self.store = ProjectionBranchWorkAccountingStore(
            self.root,
            problem="demo",
            projection_id="work-accounting-v1",
            projection_spec_digest=SPEC,
        )

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def initialize_lane(self) -> str:
        object_key = f"objects/root-contracts/{ROOT_CONTRACT.removeprefix('sha256:')}.json"
        self.store.put_immutable(object_key, b'{"root":"contract"}\n')
        return self.store.compare_and_swap(
            self.store.pipeline_lane_key, None, pipeline_bytes()
        )

    def test_exact_lane_scoping_immutable_put_and_stale_cas(self) -> None:
        object_key = f"objects/root-contracts/{ROOT_CONTRACT.removeprefix('sha256:')}.json"
        version = self.store.put_immutable(object_key, b"contract")
        self.assertEqual(self.store.put_immutable(object_key, b"contract"), version)
        with self.assertRaises(ImmutableConflict):
            self.store.put_immutable(object_key, b"different")
        physical = self.store.data_root / object_key
        self.assertTrue(physical.is_file())
        self.assertIn("demo", physical.as_posix())
        self.assertIn(self.store.scope_hex, physical.as_posix())

        head_version = self.store.compare_and_swap(
            self.store.pipeline_lane_key, None, pipeline_bytes()
        )
        with self.assertRaises(CASConflict):
            self.store.compare_and_swap(
                self.store.pipeline_lane_key,
                "sha256:" + "0" * 64,
                pipeline_bytes(formed_digest="sha256:" + "f" * 64),
            )
        self.assertEqual(
            self.store.get(self.store.pipeline_lane_key).version, head_version
        )
        with self.assertRaisesRegex(MathFlowError, "another scope"):
            self.store.get("refs/work-accounting/other/demo.json")

    def test_provider_neutral_pipeline_initializes_directly_on_adapter(self) -> None:
        contract = make_root_contract(
            problem_id="demo",
            knowledge_projection_id="openrouter-hierarchical-research-builder-v6",
            knowledge_projection_spec_digest=SPEC,
            objective="Resolve the demo objective.",
            terminal_condition="An accepted proof resolves the objective.",
            tool_baseline="Ordinary mathematical tools as of 2026-08-25.",
            reference_community_description="Qualified researchers organized by Math Flow.",
            researcher_qualification="A competent human researcher for the work package.",
        )
        knowledge = empty_research_program_state_v2("demo")
        accounting = build_work_accounting_state(
            root_contract=contract,
            knowledge_state=knowledge,
            annotations=[
                {
                    "nodeRef": {"kind": "program", "id": "root"},
                    "directWorkHours": "1",
                    "conditionalIncidence": None,
                },
                {
                    "nodeRef": {"kind": "thread", "id": "root/unstructured-search"},
                    "directWorkHours": "10",
                    "conditionalIncidence": "1",
                },
            ],
        )
        state = initialize_work_accounting_pipeline(
            self.store,
            self.root,
            problem="demo",
            projection_id="work-accounting-v1",
            projection_spec_digest=SPEC,
            root_contract=contract,
            initial_knowledge_state=knowledge,
            initial_accounting_state=accounting,
            resolved_submission_ids=[],
        )
        self.assertEqual(state["phase"], "ready")
        self.assertEqual(
            self.store.get(self.store.pipeline_lane_key).value,
            (canonical_json(state) + "\n").encode("utf-8"),
        )
        prepared = self.store.prepare_publication()
        self.assertEqual(
            prepared["manifest"]["pipelineStateDigest"], state["pipelineStateDigest"]
        )

    def test_prepare_marker_and_deletion_free_retention_are_reproducible(self) -> None:
        self.initialize_lane()
        prepared = self.store.prepare_publication()
        self.assertTrue(prepared["prepared"])
        manifest = validate_work_accounting_projection_publication(
            prepared["manifest"]
        )
        marker = validate_work_accounting_projection_marker(prepared["marker"])
        self.assertEqual(
            marker["publicationManifestDigest"], manifest["publicationManifestDigest"]
        )
        self.assertTrue(
            all(
                record["path"].startswith(
                    f"objects/work-accounting-cas-v1/demo/{self.store.scope_hex}/"
                )
                for record in [manifest["identityObject"], *manifest["retainedObjects"]]
            )
        )
        repeated = self.store.prepare_publication()
        self.assertTrue(repeated["prepared"])
        self.assertEqual(repeated["manifest"], manifest)

        plan = self.store.plan_retention()
        self.assertEqual(plan["deletionPaths"], [])
        self.assertEqual(plan["unpublishedPaths"], [])
        self.assertIn(manifest["publicationManifestDigest"], plan["publicationManifestDigests"])
        self.assertIn(self.store._relative(self.store.head_path), plan["retainedPaths"])

    def test_signed_github_publisher_keeps_metadata_final(self) -> None:
        self.initialize_lane()
        object_commit = signed_commit(1)
        metadata_commit = signed_commit(2)
        responses = [
            FakeResponse({"data": {"createCommitOnBranch": {"commit": object_commit}}}),
            FakeResponse({"data": {"createCommitOnBranch": {"commit": metadata_commit}}}),
        ]
        with patch(
            "math_flow.github_projection.urllib.request.urlopen", side_effect=responses
        ) as urlopen:
            result = publish_work_accounting_projection(
                self.store,
                repository="example/math-flow",
                branch="projections",
                message="Publish work accounting",
                token="test-token",
            )

        self.assertEqual(result["status"], "published")
        self.assertEqual(urlopen.call_count, 2)
        payloads = [json.loads(call.args[0].data)["variables"] for call in urlopen.call_args_list]
        self.assertTrue(
            all(
                addition["path"].startswith("objects/")
                for addition in payloads[0]["additions"]
            )
        )
        self.assertEqual(payloads[0]["deletions"], [])
        self.assertTrue(
            all(
                addition["path"].startswith("indexes/problems/demo/")
                for addition in payloads[1]["additions"]
            )
        )
        self.assertEqual(payloads[1]["expected"], object_commit["oid"])
        self.assertEqual(
            base64.b64decode(
                next(
                    addition["contents"]
                    for addition in payloads[1]["additions"]
                    if addition["path"].endswith("publication.json")
                )
            ),
            self.store.marker_path.read_bytes(),
        )
        self.assertNotIn("test-token", json.dumps(result))

    def test_unsigned_or_malformed_publication_report_fails_closed(self) -> None:
        self.initialize_lane()
        previous = git(self.root, "rev-parse", "HEAD")

        def malformed(*arguments, **kwargs):
            signature = {
                "isValid": False,
                "wasSignedByGitHub": False,
                "signer": None,
                "state": "UNSIGNED",
            }
            return {
                "repository": "example/math-flow",
                "branch": "projections",
                "previousHead": previous,
                "commit": "1" * 40,
                "url": "https://github.com/example/math-flow/commit/" + "1" * 40,
                "filesAddedOrUpdated": 5,
                "filesDeleted": 0,
                "signature": signature,
                "commitCount": 1,
                "immutableCommitCount": 0,
                "metadataCommit": "1" * 40,
                "commits": [
                    {
                        "phase": "metadata",
                        "previousHead": previous,
                        "commit": "1" * 40,
                        "url": "https://github.com/example/math-flow/commit/" + "1" * 40,
                        "filesAddedOrUpdated": 2,
                        "filesDeleted": 0,
                        "signature": signature,
                    }
                ],
            }

        with self.assertRaisesRegex(MathFlowError, "signed commit chain"):
            publish_work_accounting_projection(
                self.store,
                repository="example/math-flow",
                branch="projections",
                message="Publish work accounting",
                token="test-token",
                publisher=malformed,
            )

    def test_publication_preflight_rejects_unrelated_worktree_changes(self) -> None:
        self.initialize_lane()
        self.store.prepare_publication()
        unrelated = self.root / "objects/another-projection/object.json"
        unrelated.parent.mkdir(parents=True)
        unrelated.write_text("{}\n", encoding="utf-8")
        publisher = Mock()

        with self.assertRaisesRegex(MathFlowError, "cross-lane path"):
            publish_work_accounting_projection(
                self.store,
                repository="example/math-flow",
                branch="projections",
                message="Publish work accounting",
                token="test-token",
                publisher=publisher,
            )
        publisher.assert_not_called()

    def test_publication_preflight_rejects_deletion_and_immutable_rewrite(self) -> None:
        self.initialize_lane()
        self.store.prepare_publication()
        git(self.root, "add", "objects", "indexes")
        git(self.root, "commit", "-qm", "publish complete lane")

        original = self.store.identity_path.read_bytes()
        self.store.identity_path.unlink()
        with self.assertRaisesRegex(MathFlowError, "may not delete"):
            self.store.validate_publication_changes()

        self.store.identity_path.write_bytes(original + b" ")
        with self.assertRaisesRegex(MathFlowError, "may not rewrite"):
            self.store.validate_publication_changes()

    def test_remote_expected_head_race_rejects_then_retries_same_bytes(self) -> None:
        self.initialize_lane()
        stale = FakeResponse(
            {
                "errors": [
                    {"message": "Expected branch head no longer matches expectedHeadOid"}
                ]
            }
        )
        with patch(
            "math_flow.github_projection.urllib.request.urlopen", return_value=stale
        ):
            with self.assertRaisesRegex(MathFlowError, "expectedHeadOid"):
                publish_work_accounting_projection(
                    self.store,
                    repository="example/math-flow",
                    branch="projections",
                    message="Publish work accounting",
                    token="test-token",
                )
        prepared = self.store.prepare_publication()
        self.assertTrue(prepared["prepared"])

        responses = [
            FakeResponse(
                {"data": {"createCommitOnBranch": {"commit": signed_commit(1)}}}
            ),
            FakeResponse(
                {"data": {"createCommitOnBranch": {"commit": signed_commit(2)}}}
            ),
        ]
        with patch(
            "math_flow.github_projection.urllib.request.urlopen", side_effect=responses
        ):
            retried = publish_work_accounting_projection(
                self.store,
                repository="example/math-flow",
                branch="projections",
                message="Publish work accounting",
                token="test-token",
            )
        self.assertEqual(retried["status"], "published")
        self.assertEqual(
            retried["publicationManifestDigest"],
            prepared["manifest"]["publicationManifestDigest"],
        )

    def test_immutable_phase_crash_and_fresh_retry_are_idempotent(self) -> None:
        self.initialize_lane()
        first = self.store.prepare_publication()
        git(self.root, "add", "objects")
        git(self.root, "commit", "-qm", "publish immutable phase")
        # The local head and marker are still pending, exactly as after a crash
        # between the immutable and final metadata commits.
        resumed = ProjectionBranchWorkAccountingStore(
            self.root,
            problem="demo",
            projection_id="work-accounting-v1",
            projection_spec_digest=SPEC,
        )
        prepared = resumed.prepare_publication()
        self.assertTrue(prepared["prepared"])
        self.assertEqual(prepared["manifest"], first["manifest"])
        git(self.root, "add", "indexes")
        git(self.root, "commit", "-qm", "publish metadata phase")

        fresh = ProjectionBranchWorkAccountingStore(
            self.root,
            problem="demo",
            projection_id="work-accounting-v1",
            projection_spec_digest=SPEC,
        )
        final = fresh.prepare_publication()
        self.assertFalse(final["prepared"])
        self.assertEqual(final["manifest"], first["manifest"])

    def test_stale_writer_objects_cannot_publish_under_an_unchanged_head(self) -> None:
        self.initialize_lane()
        self.store.prepare_publication()
        git(self.root, "add", "objects", "indexes")
        git(self.root, "commit", "-qm", "publish complete lane")
        self.store.put_immutable("objects/loser/unreachable.json", b"{}\n")
        with self.assertRaisesRegex(MathFlowError, "unchanged pipeline head"):
            self.store.prepare_publication()

    def test_size_count_and_symlink_limits_fail_before_publication(self) -> None:
        transport_limited = ProjectionBranchWorkAccountingStore(
            self.root,
            problem="demo",
            projection_id="work-accounting-v1",
            projection_spec_digest=SPEC,
            maximum_transport_chunk_bytes=1,
        )
        transport_limited.put_immutable(
            f"objects/root-contracts/{ROOT_CONTRACT.removeprefix('sha256:')}.json",
            b"{}\n",
        )
        transport_limited.compare_and_swap(
            transport_limited.pipeline_lane_key, None, pipeline_bytes()
        )
        transport_limited.prepare_publication()
        with self.assertRaisesRegex(MathFlowError, "chunk exceeds its byte limit"):
            transport_limited.validate_publication_changes()
        git(self.root, "add", "objects", "indexes")
        git(self.root, "commit", "-qm", "publish transport-limit fixture")

        limited = ProjectionBranchWorkAccountingStore(
            self.root,
            problem="other-demo",
            projection_id="work-accounting-v1",
            projection_spec_digest=SPEC,
            maximum_object_bytes=4,
            maximum_lane_objects=1,
        )
        with self.assertRaisesRegex(MathFlowError, "byte limit"):
            limited.put_immutable("objects/example/large.bin", b"12345")
        limited.put_immutable("objects/example/one.bin", b"1")
        with self.assertRaisesRegex(MathFlowError, "maximum object count"):
            limited.put_immutable("objects/example/two.bin", b"2")
        with self.assertRaisesRegex(MathFlowError, "safe relative path"):
            limited.put_immutable("objects/../escape.bin", b"1")

        symlinked = ProjectionBranchWorkAccountingStore(
            self.root,
            problem="symlink-demo",
            projection_id="work-accounting-v1",
            projection_spec_digest=SPEC,
        )
        outside = self.root / "outside-store"
        outside.mkdir()
        symlinked.data_root.symlink_to(outside, target_is_directory=True)
        with self.assertRaisesRegex(MathFlowError, "symlink"):
            symlinked.put_immutable("objects/example/escape.bin", b"1")

    def test_inactive_publication_schema_is_present(self) -> None:
        schema = json.loads(
            (
                Path(__file__).resolve().parents[1]
                / "protocol/schemas/work-accounting-projection-publication-v1.schema.json"
            ).read_text()
        )
        self.assertEqual(schema["$schema"], "https://json-schema.org/draft/2020-12/schema")
        self.assertEqual(schema["properties"]["schemaVersion"], {"const": 1})


if __name__ == "__main__":
    unittest.main()
