from __future__ import annotations

import json
import re
from pathlib import Path, PurePosixPath

from .errors import MathFlowError
from .repository import (
    _commit_author,
    _parse_name_status,
    _run_git,
    commit_timestamp,
    read_at,
    resolve_commit,
    sha256_json,
    validate_slug,
)


GIT_SHA = re.compile(r"^[0-9a-f]{40}$")
KNOWLEDGE_NODE_ID = re.compile(
    r"^[a-z0-9][a-z0-9_-]*(?:/[a-z0-9][a-z0-9_-]*)*$"
)
EVENT_TYPES = {"register", "update", "release", "complete"}


def direction_event_key(path: str) -> tuple[str, str, str] | None:
    """Return ``(problem, direction, event)`` for a direction-event path."""

    parts = PurePosixPath(path).parts
    if (
        len(parts) < 7
        or parts[0] != "problems"
        or parts[2] != "directions"
        or parts[4] != "events"
    ):
        return None
    return parts[1], parts[3], parts[5]


def _text(value: object, label: str, maximum: int) -> str:
    if (
        not isinstance(value, str)
        or not value
        or value != value.strip()
        or len(value) > maximum
    ):
        raise MathFlowError(
            f"research direction {label} must be non-empty, trimmed text of at most {maximum} characters"
        )
    if label == "title" and ("\n" in value or "\r" in value):
        raise MathFlowError("research direction title must be one line")
    return value


def _knowledge_node_ids(value: object) -> list[str]:
    if not isinstance(value, list) or any(not isinstance(item, str) for item in value):
        raise MathFlowError("research direction relatedKnowledgeNodeIds must be an array of node IDs")
    for node_id in value:
        if not KNOWLEDGE_NODE_ID.fullmatch(node_id):
            raise MathFlowError(f"invalid related knowledge node ID: {node_id!r}")
    if value != sorted(set(value)):
        raise MathFlowError(
            "research direction relatedKnowledgeNodeIds must be unique and sorted"
        )
    return value


def validate_direction_event(
    value: object,
    *,
    expected_direction_id: str | None = None,
    expected_event_id: str | None = None,
) -> dict[str, object]:
    """Validate one versioned, participant-authored direction event."""

    if not isinstance(value, dict):
        raise MathFlowError("research direction event must be a JSON object")
    event_type = value.get("eventType")
    expected_fields = {
        "register": {
            "schemaVersion",
            "eventType",
            "eventId",
            "directionId",
            "title",
            "summary",
            "relatedKnowledgeNodeIds",
        },
        "update": {
            "schemaVersion",
            "eventType",
            "eventId",
            "directionId",
            "previousEventId",
            "title",
            "summary",
            "relatedKnowledgeNodeIds",
        },
        "release": {
            "schemaVersion",
            "eventType",
            "eventId",
            "directionId",
            "previousEventId",
            "reason",
        },
        "complete": {
            "schemaVersion",
            "eventType",
            "eventId",
            "directionId",
            "previousEventId",
            "summary",
            "contributionTransactionIds",
        },
    }
    if event_type not in EVENT_TYPES or set(value) != expected_fields.get(event_type):
        raise MathFlowError(
            "research direction event has unsupported or missing fields"
        )
    if value.get("schemaVersion") != 1 or isinstance(
        value.get("schemaVersion"), bool
    ):
        raise MathFlowError("research direction event has an invalid schema version")
    direction_id = value.get("directionId")
    event_id = value.get("eventId")
    if not isinstance(direction_id, str):
        raise MathFlowError("research direction event directionId must be a slug")
    if not isinstance(event_id, str):
        raise MathFlowError("research direction event eventId must be a slug")
    validate_slug(direction_id, "research direction id")
    validate_slug(event_id, "research direction event id")
    if expected_direction_id is not None and direction_id != expected_direction_id:
        raise MathFlowError("research direction event directionId does not match its path")
    if expected_event_id is not None and event_id != expected_event_id:
        raise MathFlowError("research direction event eventId does not match its path")

    if event_type in {"update", "release", "complete"}:
        previous = value.get("previousEventId")
        if not isinstance(previous, str):
            raise MathFlowError("research direction previousEventId must be a slug")
        validate_slug(previous, "research direction previous event id")
        if previous == event_id:
            raise MathFlowError("research direction event cannot name itself as predecessor")
    if event_type in {"register", "update"}:
        _text(value.get("title"), "title", 160)
        _text(value.get("summary"), "summary", 2_000)
        _knowledge_node_ids(value.get("relatedKnowledgeNodeIds"))
    elif event_type == "release":
        _text(value.get("reason"), "release reason", 2_000)
    else:
        _text(value.get("summary"), "completion summary", 2_000)
        transaction_ids = value.get("contributionTransactionIds")
        if (
            not isinstance(transaction_ids, list)
            or not transaction_ids
            or any(
                not isinstance(item, str) or not GIT_SHA.fullmatch(item)
                for item in transaction_ids
            )
            or len(transaction_ids) != len(set(transaction_ids))
        ):
            raise MathFlowError(
                "research direction completion needs unique contribution transaction IDs"
            )
    return value


def _derive_directions(
    events: list[dict[str, object]],
) -> list[dict[str, object]]:
    grouped: dict[str, list[dict[str, object]]] = {}
    for event in events:
        data = event.get("data")
        if not isinstance(data, dict):
            raise MathFlowError("research direction event has no validated data")
        grouped.setdefault(str(data["directionId"]), []).append(event)

    directions: list[dict[str, object]] = []
    for direction_id, direction_events in sorted(grouped.items()):
        by_id = {str(item["data"]["eventId"]): item for item in direction_events}
        if len(by_id) != len(direction_events):
            raise MathFlowError(
                f"research direction {direction_id!r} repeats an event ID"
            )
        registrations = [
            item for item in direction_events if item["data"]["eventType"] == "register"
        ]
        if len(registrations) != 1:
            raise MathFlowError(
                f"research direction {direction_id!r} must have exactly one register event"
            )
        successors: dict[str, list[dict[str, object]]] = {}
        for item in direction_events:
            data = item["data"]
            if data["eventType"] == "register":
                continue
            previous = str(data["previousEventId"])
            if previous not in by_id:
                raise MathFlowError(
                    f"research direction {direction_id!r} references unknown predecessor {previous!r}"
                )
            successors.setdefault(previous, []).append(item)
        branched = [event_id for event_id, items in successors.items() if len(items) != 1]
        if branched:
            raise MathFlowError(
                f"research direction {direction_id!r} branches after event {branched[0]!r}"
            )

        chain: list[dict[str, object]] = []
        cursor = registrations[0]
        while True:
            chain.append(cursor)
            children = successors.get(str(cursor["data"]["eventId"]), [])
            if not children:
                break
            cursor = children[0]
        if len(chain) != len(direction_events):
            raise MathFlowError(
                f"research direction {direction_id!r} has disconnected or cyclic events"
            )
        status = "active"
        snapshot = chain[0]["data"]
        for item in chain[1:]:
            data = item["data"]
            if status != "active":
                raise MathFlowError(
                    f"research direction {direction_id!r} changes after it is {status}"
                )
            if data["eventType"] == "update":
                snapshot = data
            elif data["eventType"] == "release":
                status = "released"
            elif data["eventType"] == "complete":
                status = "completed"

        registration = chain[0]
        current = chain[-1]
        completion_ids = (
            list(current["data"]["contributionTransactionIds"])
            if current["data"]["eventType"] == "complete"
            else []
        )
        directions.append(
            {
                "directionId": direction_id,
                "title": snapshot["title"],
                "summary": snapshot["summary"],
                "relatedKnowledgeNodeIds": list(
                    snapshot["relatedKnowledgeNodeIds"]
                ),
                "status": status,
                "registeredEventId": registration["data"]["eventId"],
                "registeredTransactionId": registration.get("transactionId"),
                "registeredAt": registration.get("committedAt"),
                "registeredBy": registration.get("author"),
                "currentEventId": current["data"]["eventId"],
                "currentTransactionId": current.get("transactionId"),
                "currentAt": current.get("committedAt"),
                "completionTransactionIds": completion_ids,
                "eventIds": [str(item["data"]["eventId"]) for item in chain],
            }
        )
    return directions


def validate_direction_tree(root: Path, problem_dir: Path) -> tuple[int, int]:
    """Validate current worktree direction files without requiring Git history."""

    directions_root = problem_dir / "directions"
    if not directions_root.exists():
        return 0, 0
    if not directions_root.is_dir() or directions_root.is_symlink():
        raise MathFlowError(f"directions must be a real directory: {directions_root}")
    records: list[dict[str, object]] = []
    for direction_dir in sorted(directions_root.iterdir()):
        if not direction_dir.is_dir() or direction_dir.is_symlink():
            raise MathFlowError(
                f"directions may only contain real direction directories: {direction_dir}"
            )
        validate_slug(direction_dir.name, "research direction id")
        entries = sorted(path.name for path in direction_dir.iterdir())
        if entries != ["events"] or not (direction_dir / "events").is_dir():
            raise MathFlowError(
                f"research direction must contain exactly an events directory: {direction_dir}"
            )
        events_dir = direction_dir / "events"
        if events_dir.is_symlink():
            raise MathFlowError(f"research direction events may not be symlinks: {events_dir}")
        event_dirs = sorted(events_dir.iterdir())
        if not event_dirs:
            raise MathFlowError(f"research direction has no events: {direction_dir}")
        for event_dir in event_dirs:
            if not event_dir.is_dir() or event_dir.is_symlink():
                raise MathFlowError(
                    f"research direction events may only contain real event directories: {event_dir}"
                )
            validate_slug(event_dir.name, "research direction event id")
            files = sorted(path.name for path in event_dir.iterdir())
            if files != ["README.md", "event.json"]:
                raise MathFlowError(
                    f"research direction event must contain exactly README.md and event.json: {event_dir}"
                )
            for path in event_dir.iterdir():
                if path.is_symlink() or not path.is_file():
                    raise MathFlowError(
                        f"research direction event files must be regular files: {path}"
                    )
            readme = (event_dir / "README.md").read_text(encoding="utf-8")
            if not readme.strip():
                raise MathFlowError(
                    f"research direction event README must contain text: {event_dir / 'README.md'}"
                )
            try:
                value = json.loads((event_dir / "event.json").read_text(encoding="utf-8"))
            except json.JSONDecodeError as exc:
                raise MathFlowError(
                    f"research direction event is not valid JSON: {event_dir / 'event.json'}: {exc}"
                ) from exc
            data = validate_direction_event(
                value,
                expected_direction_id=direction_dir.name,
                expected_event_id=event_dir.name,
            )
            records.append({"data": data})
    _derive_directions(records)
    return len(records), len({str(item["data"]["directionId"]) for item in records})


def research_direction_ledger(
    root: Path, problem: str, head: str = "HEAD"
) -> dict[str, object]:
    """Derive immutable research-direction history from first-parent Git history."""

    root = root.resolve()
    validate_slug(problem, "problem id")
    head_sha = resolve_commit(root, head)
    if _run_git(
        root,
        "cat-file",
        "-e",
        f"{head_sha}:problems/{problem}/problem.md",
        check=False,
    ).returncode:
        raise MathFlowError(f"problem does not exist at {head_sha}: {problem}")
    prefix = f"problems/{problem}/directions"
    commits = _run_git(
        root, "rev-list", "--first-parent", "--reverse", head_sha, "--", prefix
    ).stdout.splitlines()
    all_commits = _run_git(
        root, "rev-list", "--first-parent", "--reverse", head_sha
    ).stdout.splitlines()
    canonical_ordinals = {commit: index for index, commit in enumerate(all_commits, 1)}
    events: list[dict[str, object]] = []
    seen: set[tuple[str, str, str]] = set()
    for commit in commits:
        parents = _run_git(root, "rev-list", "--parents", "-n", "1", commit).stdout.split()
        if len(parents) == 1:
            raw_diff = _run_git(
                root,
                "diff-tree",
                "--root",
                "--no-commit-id",
                "--name-status",
                "-r",
                "-z",
                commit,
                "--",
                prefix,
            )
        else:
            raw_diff = _run_git(
                root,
                "diff-tree",
                "--no-commit-id",
                "--name-status",
                "-r",
                "-z",
                parents[1],
                commit,
                "--",
                prefix,
            )
        changes = _parse_name_status(raw_diff.stdout)
        keys = {direction_event_key(change.path) for change in changes}
        if None in keys or len(keys) != 1:
            raise MathFlowError(
                f"canonical direction commit must change exactly one event directory: {commit}"
            )
        key = next(iter(keys))
        if key in seen:
            raise MathFlowError(f"canonical research direction event was modified: {commit}")
        if any(change.status != "A" for change in changes):
            raise MathFlowError(f"canonical research direction events are append-only: {commit}")
        changed_names = sorted(PurePosixPath(change.path).name for change in changes)
        if changed_names != ["README.md", "event.json"]:
            raise MathFlowError(
                f"canonical direction event must add exactly README.md and event.json: {commit}"
            )
        _, direction_id, event_id = key
        event_prefix = f"{prefix}/{direction_id}/events/{event_id}"
        try:
            value = json.loads(read_at(root, commit, f"{event_prefix}/event.json"))
        except json.JSONDecodeError as exc:
            raise MathFlowError(
                f"canonical research direction event is not valid JSON: {commit}: {exc}"
            ) from exc
        data = validate_direction_event(
            value,
            expected_direction_id=direction_id,
            expected_event_id=event_id,
        )
        readme = read_at(root, commit, f"{event_prefix}/README.md")
        if not readme.strip():
            raise MathFlowError(
                f"canonical research direction event README is empty: {commit}"
            )
        events.append(
            {
                "ordinal": len(events) + 1,
                "canonicalOrdinal": canonical_ordinals[commit],
                "transactionId": commit,
                "committedAt": commit_timestamp(root, commit),
                "eventId": event_id,
                "directionId": direction_id,
                "eventType": data["eventType"],
                "path": event_prefix,
                "author": _commit_author(root, commit),
                "contentDigest": f"sha256:{sha256_json({'event': data, 'markdown': readme})}",
                "contentMarkdown": readme,
                "data": data,
            }
        )
        seen.add(key)

    directions = _derive_directions(events)
    core = {
        "schemaVersion": 1,
        "problemId": problem,
        "events": [
            {
                "transactionId": item["transactionId"],
                "eventId": item["eventId"],
                "directionId": item["directionId"],
                "eventType": item["eventType"],
                "contentDigest": item["contentDigest"],
            }
            for item in events
        ],
    }
    return {
        "schemaVersion": 1,
        "problemId": problem,
        "ledgerHead": head_sha,
        "directionLedgerHead": events[-1]["transactionId"] if events else None,
        "directionLedgerDigest": f"sha256:{sha256_json(core)}",
        "events": events,
        "directions": directions,
    }


def validate_direction_ledger(value: object) -> dict[str, object]:
    """Validate a self-contained direction ledger embedded in another artifact."""

    fields = {
        "schemaVersion",
        "problemId",
        "ledgerHead",
        "directionLedgerHead",
        "directionLedgerDigest",
        "events",
        "directions",
    }
    if not isinstance(value, dict) or set(value) != fields:
        raise MathFlowError("research direction ledger has unsupported or missing fields")
    problem = value.get("problemId")
    ledger_head = value.get("ledgerHead")
    direction_head = value.get("directionLedgerHead")
    if value.get("schemaVersion") != 1 or not isinstance(problem, str):
        raise MathFlowError("research direction ledger has an invalid identity")
    validate_slug(problem, "research direction ledger problem id")
    if not isinstance(ledger_head, str) or not GIT_SHA.fullmatch(ledger_head):
        raise MathFlowError("research direction ledger has an invalid canonical head")
    if direction_head is not None and (
        not isinstance(direction_head, str) or not GIT_SHA.fullmatch(direction_head)
    ):
        raise MathFlowError("research direction ledger has an invalid event head")
    raw_events = value.get("events")
    if not isinstance(raw_events, list):
        raise MathFlowError("research direction ledger events must be an array")
    event_fields = {
        "ordinal",
        "canonicalOrdinal",
        "transactionId",
        "committedAt",
        "eventId",
        "directionId",
        "eventType",
        "path",
        "author",
        "contentDigest",
        "contentMarkdown",
        "data",
    }
    events: list[dict[str, object]] = []
    previous_canonical = 0
    for index, raw_event in enumerate(raw_events, start=1):
        if not isinstance(raw_event, dict) or set(raw_event) != event_fields:
            raise MathFlowError("research direction ledger contains an invalid event")
        transaction_id = raw_event.get("transactionId")
        committed_at = raw_event.get("committedAt")
        canonical_ordinal = raw_event.get("canonicalOrdinal")
        direction_id = raw_event.get("directionId")
        event_id = raw_event.get("eventId")
        author = raw_event.get("author")
        markdown = raw_event.get("contentMarkdown")
        if (
            raw_event.get("ordinal") != index
            or not isinstance(canonical_ordinal, int)
            or isinstance(canonical_ordinal, bool)
            or canonical_ordinal <= previous_canonical
            or not isinstance(transaction_id, str)
            or not GIT_SHA.fullmatch(transaction_id)
            or not isinstance(committed_at, int)
            or isinstance(committed_at, bool)
            or committed_at < 0
            or not isinstance(direction_id, str)
            or not isinstance(event_id, str)
            or raw_event.get("eventType") not in EVENT_TYPES
            or raw_event.get("path")
            != f"problems/{problem}/directions/{direction_id}/events/{event_id}"
            or not isinstance(author, dict)
            or set(author) != {"displayName", "email"}
            or any(not isinstance(author.get(field), str) for field in author)
            or not isinstance(markdown, str)
            or not markdown.strip()
        ):
            raise MathFlowError("research direction ledger contains invalid event metadata")
        data = validate_direction_event(
            raw_event.get("data"),
            expected_direction_id=direction_id,
            expected_event_id=event_id,
        )
        if raw_event.get("eventType") != data["eventType"]:
            raise MathFlowError("research direction ledger event type is inconsistent")
        expected_content = f"sha256:{sha256_json({'event': data, 'markdown': markdown})}"
        if raw_event.get("contentDigest") != expected_content:
            raise MathFlowError("research direction ledger event content digest is invalid")
        previous_canonical = canonical_ordinal
        events.append(raw_event)
    if direction_head != (events[-1]["transactionId"] if events else None):
        raise MathFlowError("research direction ledger head does not match its events")
    derived = _derive_directions(events)
    if value.get("directions") != derived:
        raise MathFlowError("research direction ledger current state is not derived from its events")
    core = {
        "schemaVersion": 1,
        "problemId": problem,
        "events": [
            {
                "transactionId": item["transactionId"],
                "eventId": item["eventId"],
                "directionId": item["directionId"],
                "eventType": item["eventType"],
                "contentDigest": item["contentDigest"],
            }
            for item in events
        ],
    }
    if value.get("directionLedgerDigest") != f"sha256:{sha256_json(core)}":
        raise MathFlowError("research direction ledger digest is invalid")
    return value


def potential_direction_overlaps(
    directions: list[dict[str, object]],
) -> list[dict[str, object]]:
    """Report only mechanically evident overlap through shared knowledge refs."""

    active = [item for item in directions if item.get("status") == "active"]
    overlaps: list[dict[str, object]] = []
    for index, left in enumerate(active):
        left_nodes = set(left.get("relatedKnowledgeNodeIds", []))
        for right in active[index + 1 :]:
            shared = sorted(left_nodes & set(right.get("relatedKnowledgeNodeIds", [])))
            if shared:
                overlaps.append(
                    {
                        "directionIds": sorted(
                            [str(left["directionId"]), str(right["directionId"])]
                        ),
                        "sharedKnowledgeNodeIds": shared,
                    }
                )
    overlaps.sort(key=lambda item: item["directionIds"])
    return overlaps
