from __future__ import annotations

from pathlib import Path

from .governance import list_active_projections
from .problem_registry import canonical_problem_ids, load_problem_registry
from .repository import (
    ledger,
    read_at,
    resolve_commit,
)
from .viewer import export_viewer_catalog


def _title(markdown: str, fallback: str) -> str:
    for raw in markdown.splitlines():
        line = raw.strip()
        if line.startswith("# ") and line[2:].strip():
            return line[2:].strip()
    return fallback.replace("-", " ")


def discover_problems(
    root: Path,
    head: str = "HEAD",
    projection_root: Path | None = None,
    include_archived: bool = False,
) -> dict[str, object]:
    """List active problems, optionally including archived canonical history."""

    root = root.resolve()
    canonical_head = resolve_commit(root, head)
    catalog = (
        export_viewer_catalog(
            root,
            projection_root.resolve(),
            repository="local",
            canonical_ref=canonical_head,
            projection_ref="projections",
        )
        if projection_root is not None
        else None
    )
    published_by_problem: dict[str, list[dict[str, object]]] = {}
    if catalog is not None:
        for projection in catalog["projections"]:
            published_by_problem.setdefault(str(projection["problemId"]), []).append(
                projection
            )

    registry = load_problem_registry(root, canonical_head)
    archived = set(registry["archivedProblems"])
    problems: list[dict[str, object]] = []
    for problem_id in canonical_problem_ids(root, canonical_head):
        status = "archived" if problem_id in archived else "active"
        if status == "archived" and not include_archived:
            continue
        statement = read_at(
            root, canonical_head, f"problems/{problem_id}/problem.md"
        )
        source = ledger(root, problem_id, canonical_head)
        transactions = list(source["transactions"])
        transaction_ids = [str(item["transactionId"]) for item in transactions]
        active = (
            []
            if status == "archived"
            else list_active_projections(root, problem_id, canonical_head)[
                "projections"
            ]
        )
        knowledge_ids = sorted(
            str(item["projectionId"])
            for item in active
            if "knowledgeBuilder" in item
        )
        overlay_ids = sorted(
            str(item["projectionId"])
            for item in active
            if "knowledgeBuilder" not in item
        )

        published: list[dict[str, object]] = []
        for item in published_by_problem.get(problem_id, []):
            projection_id = str(item["id"])
            matching_id = next(
                (
                    active_id
                    for active_id in knowledge_ids
                    if projection_id == active_id
                    or projection_id.startswith(f"{active_id}@")
                ),
                None,
            )
            if matching_id is None:
                continue
            data = item["data"]
            projected_ids = [
                str(transaction["transactionId"])
                for transaction in data["transactions"]
            ]
            current = (
                projected_ids == transaction_ids
                and data["problem"]["statementMarkdown"] == statement
            )
            published.append(
                {
                    "projectionId": matching_id,
                    "latestRunDigest": item["latestRunDigest"],
                    "runCount": item["runCount"],
                    "projectedContributionCount": len(projected_ids),
                    "current": current,
                }
            )
        published.sort(
            key=lambda item: (str(item["projectionId"]), str(item["latestRunDigest"]))
        )

        if status == "archived":
            stage = "archived"
            next_action = "unarchive-before-new-work"
        elif not transactions:
            stage = "ready-for-first-contribution"
            next_action = "inspect-problem-and-submit-first-contribution"
        elif catalog is None:
            stage = "projection-unchecked"
            next_action = "inspect-verified-projection-status"
        elif any(bool(item["current"]) for item in published):
            stage = "knowledge-current"
            next_action = "materialize-context-and-select-research-objective"
        elif published:
            stage = "knowledge-stale"
            next_action = "wait-for-or-investigate-projection-publication"
        else:
            stage = "knowledge-pending"
            next_action = "wait-for-or-investigate-first-projection-publication"

        problems.append(
            {
                "problemId": problem_id,
                "status": status,
                "title": _title(statement, problem_id),
                "statementPath": f"problems/{problem_id}/problem.md",
                "contributionCount": len(transactions),
                "latestContributionTransactionId": (
                    transaction_ids[-1] if transaction_ids else None
                ),
                "stage": stage,
                "nextAction": next_action,
                "activeKnowledgeProjectionIds": knowledge_ids,
                "activeOverlayProjectionIds": overlay_ids,
                "publishedKnowledgeProjections": published,
            }
        )

    return {
        "schemaVersion": 1,
        "canonicalHead": canonical_head,
        "projectionInspection": "verified" if catalog is not None else "not-requested",
        "archivedProblemCount": len(archived),
        "problems": problems,
    }
