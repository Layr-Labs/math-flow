from __future__ import annotations

import base64
import json
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from math_flow.errors import MathFlowError
from math_flow.github_projection import publish_github_projection


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


class FakeResponse:
    def __init__(self, value: object) -> None:
        self.body = json.dumps(value).encode("utf-8")

    def __enter__(self) -> "FakeResponse":
        return self

    def __exit__(self, *arguments: object) -> None:
        return None

    def read(self) -> bytes:
        return self.body


class GitHubProjectionPublicationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        git(self.root, "init", "-q")
        git(self.root, "config", "user.name", "Projection Test")
        git(self.root, "config", "user.email", "projection@example.com")
        target = self.root / "coordination/scheduler.json"
        target.parent.mkdir(parents=True)
        target.write_text('{"schemaVersion": 1}\n', encoding="utf-8")
        git(self.root, "add", ".")
        git(self.root, "commit", "-qm", "Initialize projection")

    def tearDown(self) -> None:
        self.temporary.cleanup()

    @staticmethod
    def signed_commit(number: int) -> dict[str, object]:
        oid = f"{number:040x}"
        return {
            "oid": oid,
            "url": f"https://github.com/example/research/commit/{oid}",
            "signature": {
                "isValid": True,
                "wasSignedByGitHub": True,
                "signer": {"login": "web-flow"},
                "state": "VALID",
            },
        }

    @staticmethod
    def graphql_response(commit: dict[str, object]) -> FakeResponse:
        return FakeResponse({"data": {"createCommitOnBranch": {"commit": commit}}})

    def test_publishes_only_projection_files_and_requires_github_signature(self) -> None:
        scheduler = self.root / "coordination/scheduler.json"
        scheduler.write_text('{"schemaVersion": 1, "lanes": {}}\n', encoding="utf-8")
        scheduler.with_name("scheduler.json.lock").touch()
        report = self.root / "objects/judgment/ab/example/report.md"
        report.parent.mkdir(parents=True)
        report.write_text("# Judgment\n", encoding="utf-8")
        object_commit = self.signed_commit(1)
        metadata_commit = self.signed_commit(2)
        with patch(
            "math_flow.github_projection.urllib.request.urlopen",
            side_effect=[
                self.graphql_response(object_commit),
                self.graphql_response(metadata_commit),
            ],
        ) as urlopen:
            result = publish_github_projection(
                self.root,
                "example/research",
                "projections",
                "Publish demo",
                "secret-token",
            )

        self.assertEqual(urlopen.call_count, 2)
        object_request = urlopen.call_args_list[0].args[0]
        object_payload = json.loads(object_request.data)
        object_additions = object_payload["variables"]["additions"]
        self.assertEqual(
            [addition["path"] for addition in object_additions],
            ["objects/judgment/ab/example/report.md"],
        )
        self.assertEqual(
            base64.b64decode(object_additions[0]["contents"]).decode("utf-8"),
            "# Judgment\n",
        )
        metadata_payload = json.loads(urlopen.call_args_list[1].args[0].data)
        self.assertEqual(
            [addition["path"] for addition in metadata_payload["variables"]["additions"]],
            ["coordination/scheduler.json"],
        )
        self.assertEqual(
            metadata_payload["variables"]["expected"], object_commit["oid"]
        )
        self.assertEqual(
            object_request.get_header("Authorization"), "Bearer secret-token"
        )
        self.assertEqual(result["commit"], metadata_commit["oid"])
        self.assertEqual(result["commitCount"], 2)
        self.assertEqual(result["immutableCommitCount"], 1)
        self.assertEqual(result["metadataCommit"], metadata_commit["oid"])
        self.assertTrue(result["signature"]["wasSignedByGitHub"])

    def test_chunks_more_than_one_hundred_immutable_files_before_metadata(self) -> None:
        old_index = self.root / "indexes/problems/demo/obsolete.json"
        old_index.parent.mkdir(parents=True)
        old_index.write_text("{}\n", encoding="utf-8")
        git(self.root, "add", ".")
        git(self.root, "commit", "-qm", "Add old projection index")
        initial_head = git(self.root, "rev-parse", "HEAD")
        old_index.unlink()

        scheduler = self.root / "coordination/scheduler.json"
        scheduler.write_text('{"schemaVersion": 1, "lanes": {}}\n', encoding="utf-8")
        catalog = self.root / "viewer/catalog.json"
        catalog.parent.mkdir(parents=True)
        catalog.write_text('{"problems": []}\n', encoding="utf-8")
        for number in range(203):
            target = self.root / f"objects/judgment/{number:03d}/report.md"
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(f"# Judgment {number}\n", encoding="utf-8")
        for number in range(2):
            target = self.root / f"publication-batches/{number:03d}.json"
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text("{}\n", encoding="utf-8")

        returned_commits = [self.signed_commit(number) for number in range(1, 5)]
        with patch(
            "math_flow.github_projection.urllib.request.urlopen",
            side_effect=[self.graphql_response(commit) for commit in returned_commits],
        ) as urlopen:
            result = publish_github_projection(
                self.root,
                "example/research",
                "projections",
                "Publish large projection",
                "secret-token",
            )

        self.assertEqual(urlopen.call_count, 4)
        payloads = [json.loads(call.args[0].data)["variables"] for call in urlopen.call_args_list]
        self.assertEqual(
            [len(payload["additions"]) + len(payload["deletions"]) for payload in payloads],
            [100, 100, 5, 3],
        )
        self.assertTrue(
            all(
                addition["path"].startswith(("objects/", "publication-batches/"))
                for payload in payloads[:3]
                for addition in payload["additions"]
            )
        )
        self.assertTrue(all(not payload["deletions"] for payload in payloads[:3]))
        self.assertEqual(
            [addition["path"] for addition in payloads[3]["additions"]],
            ["coordination/scheduler.json", "viewer/catalog.json"],
        )
        self.assertEqual(payloads[3]["deletions"], [{"path": "indexes/problems/demo/obsolete.json"}])
        expected_heads = [initial_head] + [commit["oid"] for commit in returned_commits[:-1]]
        self.assertEqual(
            [payload["expected"] for payload in payloads],
            expected_heads,
        )
        self.assertEqual(result["previousHead"], initial_head)
        self.assertEqual(result["commit"], returned_commits[-1]["oid"])
        self.assertEqual(result["commitCount"], 4)
        self.assertEqual(result["immutableCommitCount"], 3)
        self.assertEqual(result["metadataCommit"], returned_commits[-1]["oid"])
        self.assertEqual(
            [commit["previousHead"] for commit in result["commits"]],
            expected_heads,
        )
        self.assertTrue(
            all(commit["signature"]["wasSignedByGitHub"] for commit in result["commits"])
        )
        self.assertNotIn("secret-token", json.dumps(result))

    def test_stops_before_metadata_when_an_immutable_chunk_is_not_signed(self) -> None:
        scheduler = self.root / "coordination/scheduler.json"
        scheduler.write_text('{"schemaVersion": 1, "lanes": {}}\n', encoding="utf-8")
        for number in range(101):
            target = self.root / f"objects/judgment/{number:03d}/report.md"
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(f"# Judgment {number}\n", encoding="utf-8")
        unsigned = self.signed_commit(2)
        unsigned["signature"] = {
            "isValid": False,
            "wasSignedByGitHub": False,
            "signer": None,
            "state": "UNSIGNED",
        }

        with patch(
            "math_flow.github_projection.urllib.request.urlopen",
            side_effect=[
                self.graphql_response(self.signed_commit(1)),
                self.graphql_response(unsigned),
            ],
        ) as urlopen:
            with self.assertRaisesRegex(MathFlowError, "valid GitHub-signed"):
                publish_github_projection(
                    self.root,
                    "example/research",
                    "projections",
                    "Publish large projection",
                    "secret-token",
                )

        self.assertEqual(urlopen.call_count, 2)
        payloads = [json.loads(call.args[0].data)["variables"] for call in urlopen.call_args_list]
        self.assertEqual([len(payload["additions"]) for payload in payloads], [100, 1])
        self.assertTrue(
            all(
                addition["path"].startswith("objects/")
                for payload in payloads
                for addition in payload["additions"]
            )
        )

    def test_rejects_oversized_mutable_metadata_before_publishing_objects(self) -> None:
        report = self.root / "objects/judgment/ab/example/report.md"
        report.parent.mkdir(parents=True)
        report.write_text("# Judgment\n", encoding="utf-8")
        for number in range(100):
            target = self.root / f"indexes/problems/demo/{number:03d}.json"
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text("{}\n", encoding="utf-8")
        # The scheduler modification makes 101 mutable metadata changes.
        scheduler = self.root / "coordination/scheduler.json"
        scheduler.write_text('{"schemaVersion": 1, "lanes": {}}\n', encoding="utf-8")

        with patch("math_flow.github_projection.urllib.request.urlopen") as urlopen:
            with self.assertRaisesRegex(MathFlowError, "mutable metadata exceeds"):
                publish_github_projection(
                    self.root,
                    "example/research",
                    "projections",
                    "Publish oversized metadata",
                    "secret-token",
                )

        urlopen.assert_not_called()

    def test_rejects_changes_outside_projection_publication_paths(self) -> None:
        (self.root / "README.md").write_text("unexpected\n", encoding="utf-8")
        with self.assertRaisesRegex(MathFlowError, "unexpected path"):
            publish_github_projection(
                self.root,
                "example/research",
                "projections",
                "Publish demo",
                "secret-token",
            )

    def test_rejects_an_unsigned_graphql_response(self) -> None:
        scheduler = self.root / "coordination/scheduler.json"
        scheduler.write_text('{"schemaVersion": 1, "lanes": {}}\n', encoding="utf-8")
        commit = {
            "oid": "f" * 40,
            "url": "https://github.com/example/research/commit/" + "f" * 40,
            "signature": {
                "isValid": False,
                "wasSignedByGitHub": False,
                "signer": None,
                "state": "UNSIGNED",
            },
        }
        with patch(
            "math_flow.github_projection.urllib.request.urlopen",
            return_value=FakeResponse({"data": {"createCommitOnBranch": {"commit": commit}}}),
        ):
            with self.assertRaisesRegex(MathFlowError, "valid GitHub-signed"):
                publish_github_projection(
                    self.root,
                    "example/research",
                    "projections",
                    "Publish demo",
                    "secret-token",
                )
