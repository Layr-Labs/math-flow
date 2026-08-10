from __future__ import annotations

import base64
import json
import re
import subprocess
import urllib.error
import urllib.request
from pathlib import Path

from .errors import MathFlowError


_REPOSITORY_RE = re.compile(r"^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$")
_PUBLISHED_PATHS = (
    "coordination/scheduler.json",
    "indexes/",
    "objects/",
    "publication-batches/",
    "viewer/catalog.json",
)
_GRAPHQL = """
mutation PublishProjection(
  $repository: String!
  $branch: String!
  $expected: GitObjectID!
  $headline: String!
  $additions: [FileAddition!]!
  $deletions: [FileDeletion!]!
) {
  createCommitOnBranch(input: {
    branch: {
      repositoryNameWithOwner: $repository
      branchName: $branch
    }
    expectedHeadOid: $expected
    message: {headline: $headline}
    fileChanges: {additions: $additions, deletions: $deletions}
  }) {
    commit {
      oid
      url
      signature {
        isValid
        wasSignedByGitHub
        signer { login }
        state
      }
    }
  }
}
""".strip()


def _git(worktree: Path, *arguments: str) -> str:
    result = subprocess.run(
        ["git", "-C", str(worktree), *arguments],
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    return result.stdout.rstrip("\n")


def _is_published_path(path: str) -> bool:
    return any(
        path == allowed or (allowed.endswith("/") and path.startswith(allowed))
        for allowed in _PUBLISHED_PATHS
    )


def _changed_files(worktree: Path) -> tuple[list[dict[str, str]], list[dict[str, str]]]:
    raw = _git(worktree, "status", "--porcelain=v1", "--untracked-files=all", "-z")
    entries = raw.split("\0") if raw else []
    additions: list[dict[str, str]] = []
    deletions: list[dict[str, str]] = []
    seen: set[str] = set()
    index = 0
    while index < len(entries):
        entry = entries[index]
        index += 1
        if not entry:
            continue
        if len(entry) < 4 or entry[2] != " ":
            raise MathFlowError("could not parse projection worktree status")
        status = entry[:2]
        path = entry[3:]
        if "R" in status or "C" in status:
            raise MathFlowError("projection publication does not support renamed files")
        if not _is_published_path(path):
            raise MathFlowError(f"projection publication touched an unexpected path: {path}")
        if path in seen:
            raise MathFlowError(f"projection publication contains a duplicate path: {path}")
        seen.add(path)
        if "D" in status:
            deletions.append({"path": path})
            continue
        target = worktree / path
        if not target.is_file() or target.is_symlink():
            raise MathFlowError(f"projection publication path is not a regular file: {path}")
        additions.append(
            {
                "path": path,
                "contents": base64.b64encode(target.read_bytes()).decode("ascii"),
            }
        )
    additions.sort(key=lambda item: item["path"])
    deletions.sort(key=lambda item: item["path"])
    if not additions and not deletions:
        raise MathFlowError("projection publication has no file changes")
    if len(additions) + len(deletions) > 100:
        raise MathFlowError("projection publication exceeds GitHub's 100-file commit limit")
    return additions, deletions


def publish_github_projection(
    projection_dir: Path,
    repository: str,
    branch: str,
    message: str,
    token: str,
    *,
    endpoint: str = "https://api.github.com/graphql",
) -> dict[str, object]:
    if not projection_dir.is_dir():
        raise MathFlowError(f"projection worktree does not exist: {projection_dir}")
    if not _REPOSITORY_RE.fullmatch(repository):
        raise MathFlowError("repository must be an owner/name GitHub slug")
    if not branch or branch.startswith("-") or ".." in branch:
        raise MathFlowError("projection branch name is invalid")
    if not message.strip():
        raise MathFlowError("projection commit message must not be empty")
    if not token.strip():
        raise MathFlowError("GITHUB_TOKEN is required for projection publication")

    expected_head = _git(projection_dir, "rev-parse", "HEAD")
    additions, deletions = _changed_files(projection_dir)
    payload = {
        "query": _GRAPHQL,
        "variables": {
            "repository": repository,
            "branch": branch,
            "expected": expected_head,
            "headline": message,
            "additions": additions,
            "deletions": deletions,
        },
    }
    request = urllib.request.Request(
        endpoint,
        data=json.dumps(payload, separators=(",", ":")).encode("utf-8"),
        headers={
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "User-Agent": "math-flow-projection-publisher",
            "X-GitHub-Api-Version": "2022-11-28",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=60) as response:
            response_body = response.read().decode("utf-8")
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise MathFlowError(f"GitHub projection publication failed: HTTP {exc.code}: {detail}") from exc
    except urllib.error.URLError as exc:
        raise MathFlowError(f"GitHub projection publication failed: {exc.reason}") from exc

    try:
        response_value = json.loads(response_body)
    except json.JSONDecodeError as exc:
        raise MathFlowError("GitHub projection publication returned invalid JSON") from exc
    errors = response_value.get("errors") if isinstance(response_value, dict) else None
    if errors:
        messages = [
            str(error.get("message", "unknown GraphQL error"))
            for error in errors
            if isinstance(error, dict)
        ]
        raise MathFlowError(
            "GitHub projection publication failed: " + "; ".join(messages or ["unknown error"])
        )
    try:
        commit = response_value["data"]["createCommitOnBranch"]["commit"]
        signature = commit["signature"]
    except (KeyError, TypeError) as exc:
        raise MathFlowError("GitHub projection publication response omitted commit metadata") from exc
    if not isinstance(commit.get("oid"), str) or not isinstance(commit.get("url"), str):
        raise MathFlowError("GitHub projection publication response contained an invalid commit")
    if not isinstance(signature, dict) or not signature.get("isValid") or not signature.get(
        "wasSignedByGitHub"
    ):
        raise MathFlowError("GitHub did not return a valid GitHub-signed projection commit")
    return {
        "repository": repository,
        "branch": branch,
        "previousHead": expected_head,
        "commit": commit["oid"],
        "url": commit["url"],
        "filesAddedOrUpdated": len(additions),
        "filesDeleted": len(deletions),
        "signature": {
            "isValid": True,
            "wasSignedByGitHub": True,
            "signer": (signature.get("signer") or {}).get("login"),
            "state": signature.get("state"),
        },
    }
