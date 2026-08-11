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
_TRANSIENT_PATHS = {"coordination/scheduler.json.lock"}
_IMMUTABLE_PATH_PREFIXES = ("objects/", "publication-batches/")
_MAX_FILES_PER_COMMIT = 100
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
        # Coordination keeps this file open while atomically updating the
        # scheduler.  The lock is local process state, not projection state.
        if path in _TRANSIENT_PATHS:
            continue
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
    return additions, deletions


def _is_immutable_addition(path: str) -> bool:
    return path.startswith(_IMMUTABLE_PATH_PREFIXES)


def _publication_plan(
    additions: list[dict[str, str]],
    deletions: list[dict[str, str]],
) -> list[tuple[str, list[dict[str, str]], list[dict[str, str]]]]:
    immutable = [item for item in additions if _is_immutable_addition(item["path"])]
    mutable = [item for item in additions if not _is_immutable_addition(item["path"])]
    if len(mutable) + len(deletions) > _MAX_FILES_PER_COMMIT:
        raise MathFlowError(
            "projection mutable metadata exceeds GitHub's 100-file commit limit"
        )

    plan: list[tuple[str, list[dict[str, str]], list[dict[str, str]]]] = []
    for start in range(0, len(immutable), _MAX_FILES_PER_COMMIT):
        plan.append(
            ("immutable", immutable[start : start + _MAX_FILES_PER_COMMIT], [])
        )
    if mutable or deletions:
        plan.append(("metadata", mutable, deletions))
    return plan


def _publish_commit(
    endpoint: str,
    repository: str,
    branch: str,
    expected_head: str,
    message: str,
    token: str,
    additions: list[dict[str, str]],
    deletions: list[dict[str, str]],
) -> tuple[dict[str, object], dict[str, object]]:
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
        detail = exc.read().decode("utf-8", errors="replace").replace(token, "[REDACTED]")
        raise MathFlowError(
            f"GitHub projection publication failed: HTTP {exc.code}: {detail}"
        ) from exc
    except urllib.error.URLError as exc:
        reason = str(exc.reason).replace(token, "[REDACTED]")
        raise MathFlowError(f"GitHub projection publication failed: {reason}") from exc

    try:
        response_value = json.loads(response_body)
    except json.JSONDecodeError as exc:
        raise MathFlowError("GitHub projection publication returned invalid JSON") from exc
    errors = response_value.get("errors") if isinstance(response_value, dict) else None
    if errors:
        messages = [
            str(error.get("message", "unknown GraphQL error")).replace(token, "[REDACTED]")
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
    if (
        not isinstance(signature, dict)
        or signature.get("isValid") is not True
        or signature.get("wasSignedByGitHub") is not True
    ):
        raise MathFlowError("GitHub did not return a valid GitHub-signed projection commit")
    signer = signature.get("signer")
    verified_signature: dict[str, object] = {
        "isValid": True,
        "wasSignedByGitHub": True,
        "signer": signer.get("login") if isinstance(signer, dict) else None,
        "state": signature.get("state"),
    }
    return commit, verified_signature


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

    initial_head = _git(projection_dir, "rev-parse", "HEAD")
    additions, deletions = _changed_files(projection_dir)
    plan = _publication_plan(additions, deletions)
    expected_head = initial_head
    commits: list[dict[str, object]] = []
    for phase, commit_additions, commit_deletions in plan:
        commit, signature = _publish_commit(
            endpoint,
            repository,
            branch,
            expected_head,
            message,
            token,
            commit_additions,
            commit_deletions,
        )
        commits.append(
            {
                "phase": phase,
                "previousHead": expected_head,
                "commit": commit["oid"],
                "url": commit["url"],
                "filesAddedOrUpdated": len(commit_additions),
                "filesDeleted": len(commit_deletions),
                "signature": signature,
            }
        )
        expected_head = commit["oid"]

    final_commit = commits[-1]
    return {
        "repository": repository,
        "branch": branch,
        "previousHead": initial_head,
        "commit": final_commit["commit"],
        "url": final_commit["url"],
        "filesAddedOrUpdated": len(additions),
        "filesDeleted": len(deletions),
        "signature": final_commit["signature"],
        "commitCount": len(commits),
        "immutableCommitCount": sum(item["phase"] == "immutable" for item in commits),
        "metadataCommit": next(
            (item["commit"] for item in commits if item["phase"] == "metadata"), None
        ),
        "commits": commits,
    }
