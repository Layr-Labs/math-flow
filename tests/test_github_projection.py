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

    def test_publishes_only_projection_files_and_requires_github_signature(self) -> None:
        scheduler = self.root / "coordination/scheduler.json"
        scheduler.write_text('{"schemaVersion": 1, "lanes": {}}\n', encoding="utf-8")
        scheduler.with_name("scheduler.json.lock").touch()
        report = self.root / "objects/judgment/ab/example/report.md"
        report.parent.mkdir(parents=True)
        report.write_text("# Judgment\n", encoding="utf-8")
        commit = {
            "oid": "f" * 40,
            "url": "https://github.com/example/research/commit/" + "f" * 40,
            "signature": {
                "isValid": True,
                "wasSignedByGitHub": True,
                "signer": {"login": "web-flow"},
                "state": "VALID",
            },
        }
        with patch(
            "math_flow.github_projection.urllib.request.urlopen",
            return_value=FakeResponse({"data": {"createCommitOnBranch": {"commit": commit}}}),
        ) as urlopen:
            result = publish_github_projection(
                self.root,
                "example/research",
                "projections",
                "Publish demo",
                "secret-token",
            )

        request = urlopen.call_args.args[0]
        payload = json.loads(request.data)
        additions = payload["variables"]["additions"]
        self.assertEqual(
            [addition["path"] for addition in additions],
            ["coordination/scheduler.json", "objects/judgment/ab/example/report.md"],
        )
        self.assertEqual(
            base64.b64decode(additions[1]["contents"]).decode("utf-8"),
            "# Judgment\n",
        )
        self.assertEqual(request.get_header("Authorization"), "Bearer secret-token")
        self.assertEqual(result["commit"], "f" * 40)
        self.assertTrue(result["signature"]["wasSignedByGitHub"])

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
