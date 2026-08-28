from __future__ import annotations

import copy
import re
from collections.abc import Iterable

from .errors import MathFlowError
from .repository import sha256_json
from .research_state import (
    CONTRIBUTION_FIELDS,
    ITEM_FIELDS,
    PROGRAM_FIELDS,
    PROGRAM_STATUSES,
    STATE_FIELDS,
    THREAD_FIELDS,
    _validate_contribution,
    _validate_item,
    _validate_thread,
    validate_research_program_state,
)


IDENTIFIER = re.compile(r"^[a-z0-9][a-z0-9/_-]*$")
GIT_SHA = re.compile(r"^[0-9a-f]{40}$")
DIGEST = re.compile(r"^sha256:[0-9a-f]{64}$")

LINEAGE_RELATIONS = {
    "split-from",
    "split-into",
    "merged-from",
    "merged-into",
}
PROGRAM_V2_FIELDS = PROGRAM_FIELDS | {"lineage"}
STATE_V2_FIELDS = STATE_FIELDS
TRANSITION_ACTIONS = {"create", "move", "retire"}
ENTITY_COLLECTIONS = {
    "program": "programs",
    "thread": "threads",
    "item": "items",
}


def _digest_record(record: dict[str, object]) -> str:
    value = {key: item for key, item in record.items() if key != "digest"}
    return f"sha256:{sha256_json(value)}"


def _with_record_digest(record: dict[str, object]) -> dict[str, object]:
    value = {
        key: copy.deepcopy(item) for key, item in record.items() if key != "digest"
    }
    return {**value, "digest": _digest_record(value)}


def _with_state_digest(state: dict[str, object]) -> dict[str, object]:
    value = {
        key: copy.deepcopy(item)
        for key, item in state.items()
        if key != "stateDigest"
    }
    return {**value, "stateDigest": f"sha256:{sha256_json(value)}"}


def _require_identifier(value: object, label: str) -> str:
    if not isinstance(value, str) or not IDENTIFIER.fullmatch(value):
        raise MathFlowError(f"{label} must be a stable lowercase path")
    return value


def _require_string_array(value: object, label: str) -> list[str]:
    if (
        not isinstance(value, list)
        or any(not isinstance(item, str) or not item for item in value)
        or len(value) != len(set(value))
    ):
        raise MathFlowError(f"{label} must contain unique non-empty strings")
    return list(value)


def _validate_lineage(value: object, program_id: str) -> list[dict[str, str]]:
    if not isinstance(value, list):
        raise MathFlowError(
            f"research program lineage must be an array: {program_id}"
        )
    result: list[dict[str, str]] = []
    seen: set[tuple[str, str]] = set()
    seen_targets: dict[str, str] = {}
    for raw_item in value:
        if (
            not isinstance(raw_item, dict)
            or set(raw_item) != {"relation", "programId"}
            or raw_item.get("relation") not in LINEAGE_RELATIONS
            or not isinstance(raw_item.get("programId"), str)
            or not IDENTIFIER.fullmatch(str(raw_item["programId"]))
            or raw_item["programId"] == program_id
        ):
            raise MathFlowError(f"invalid research program lineage: {program_id}")
        relation = str(raw_item["relation"])
        target_id = str(raw_item["programId"])
        key = (relation, target_id)
        if key in seen:
            raise MathFlowError(f"duplicate research program lineage: {program_id}")
        if target_id in seen_targets and seen_targets[target_id] != relation:
            raise MathFlowError(
                f"research program lineage repeats one target with different relations: {program_id}"
            )
        seen.add(key)
        seen_targets[target_id] = relation
        result.append({"relation": relation, "programId": target_id})
    return result


def _canonical_lineage(value: object, program_id: str) -> list[dict[str, str]]:
    return sorted(
        _validate_lineage(value, program_id),
        key=lambda item: (item["relation"], item["programId"]),
    )


def _validate_program_v2(record: object, program_id: str) -> dict[str, object]:
    if not isinstance(record, dict) or set(record) != PROGRAM_V2_FIELDS:
        raise MathFlowError(f"research program v2 has invalid fields: {program_id}")
    if record.get("id") != program_id:
        raise MathFlowError(f"research program v2 ID mismatch: {program_id}")
    _require_identifier(program_id, "research program v2 ID")
    parent_id = record.get("parentId")
    if parent_id is not None:
        _require_identifier(parent_id, "research program v2 parent ID")
    if not isinstance(record.get("title"), str) or not str(record["title"]).strip():
        raise MathFlowError("research program v2 title must be non-empty text")
    if not isinstance(record.get("objective"), str) or not str(
        record["objective"]
    ).strip():
        raise MathFlowError("research program v2 objective must be non-empty text")
    if record.get("status") not in PROGRAM_STATUSES:
        raise MathFlowError(f"research program v2 has invalid status: {program_id}")
    _require_string_array(record.get("parentThreadIds"), "program parentThreadIds")
    sources = _require_string_array(
        record.get("sourceTransactionIds"), "program sourceTransactionIds"
    )
    if any(not GIT_SHA.fullmatch(item) for item in sources):
        raise MathFlowError(
            f"research program v2 has invalid transaction provenance: {program_id}"
        )
    if record.get("lineage") != _canonical_lineage(
        record.get("lineage"), program_id
    ):
        raise MathFlowError(
            f"research program lineage must be canonically sorted: {program_id}"
        )
    if record.get("digest") != _digest_record(record):
        raise MathFlowError(f"research program v2 digest mismatch: {program_id}")
    return record


def _validate_lineage_graph(programs: dict[str, object]) -> None:
    inverse = {
        "split-from": "split-into",
        "split-into": "split-from",
        "merged-from": "merged-into",
        "merged-into": "merged-from",
    }
    directed_successors: dict[str, set[str]] = {program_id: set() for program_id in programs}

    for program_id, raw_program in programs.items():
        assert isinstance(raw_program, dict)
        lineage = _validate_lineage(raw_program.get("lineage"), program_id)
        counts = {
            relation: sum(item["relation"] == relation for item in lineage)
            for relation in LINEAGE_RELATIONS
        }
        if counts["split-from"] > 1:
            raise MathFlowError(
                f"research program split successor has multiple predecessors: {program_id}"
            )
        if counts["split-into"] == 1:
            raise MathFlowError(
                f"research program split must have at least two successors: {program_id}"
            )
        if counts["merged-from"] == 1:
            raise MathFlowError(
                f"research program merge must have at least two predecessors: {program_id}"
            )
        if counts["merged-into"] > 1:
            raise MathFlowError(
                f"research program merge predecessor has multiple successors: {program_id}"
            )
        if counts["split-into"] and counts["merged-into"]:
            raise MathFlowError(
                f"research program cannot be split and merged in one lineage state: {program_id}"
            )
        if counts["split-from"] and counts["merged-from"]:
            raise MathFlowError(
                f"research program cannot be both split and merge successor: {program_id}"
            )
        has_successors = bool(counts["split-into"] or counts["merged-into"])
        if has_successors and raw_program.get("status") != "retired":
            raise MathFlowError(
                f"research program lineage predecessor must be retired: {program_id}"
            )
        for item in lineage:
            relation = item["relation"]
            target_id = item["programId"]
            target = programs.get(target_id)
            if not isinstance(target, dict):
                raise MathFlowError(
                    f"research program lineage references a missing program: {program_id}"
                )
            reciprocal = {"relation": inverse[relation], "programId": program_id}
            if reciprocal not in target.get("lineage", []):
                raise MathFlowError(
                    f"research program lineage is not reciprocal: {program_id}"
                )
            if relation in {"split-into", "merged-into"}:
                directed_successors[program_id].add(target_id)

    visiting: set[str] = set()
    visited: set[str] = set()

    def visit(program_id: str) -> None:
        if program_id in visited:
            return
        if program_id in visiting:
            raise MathFlowError(
                f"research program lineage contains a cycle: {program_id}"
            )
        visiting.add(program_id)
        for successor_id in sorted(directed_successors[program_id]):
            visit(successor_id)
        visiting.remove(program_id)
        visited.add(program_id)

    for program_id in sorted(programs):
        visit(program_id)


def empty_research_program_state_v2(problem: str) -> dict[str, object]:
    _require_identifier(problem, "research program v2 problem ID")
    root = _with_record_digest(
        {
            "id": "root",
            "parentId": None,
            "title": "Canonical problem",
            "objective": "Resolve the canonical problem.",
            "status": "active",
            "parentThreadIds": [],
            "sourceTransactionIds": [],
            "lineage": [],
        }
    )
    unstructured = _with_record_digest(
        {
            "id": "root/unstructured-search",
            "programId": "root",
            "title": "Unstructured search and overhead",
            "summary": "Future work not yet assigned to a more specific research thread.",
            "kind": "unstructured",
            "status": "active",
            "expectedExposure": "1",
            "conditions": [],
            "sourceTransactionIds": [],
        }
    )
    return _with_state_digest(
        {
            "schemaVersion": 2,
            "problemId": problem,
            "ledgerHead": None,
            "baseStateDigest": None,
            "rootProgramId": "root",
            "programs": {"root": root},
            "threads": {"root/unstructured-search": unstructured},
            "items": {},
            "contributions": {},
        }
    )


def validate_research_program_state_v2(
    value: object, problem: str | None = None
) -> dict[str, object]:
    if not isinstance(value, dict) or set(value) != STATE_V2_FIELDS:
        raise MathFlowError("research program state v2 has an invalid envelope")
    if value.get("schemaVersion") != 2:
        raise MathFlowError("research program state v2 has an unsupported version")
    if problem is not None and value.get("problemId") != problem:
        raise MathFlowError("research program state v2 belongs to another problem")
    _require_identifier(value.get("problemId"), "research program v2 problem ID")
    ledger_head = value.get("ledgerHead")
    if ledger_head is not None and (
        not isinstance(ledger_head, str) or not GIT_SHA.fullmatch(ledger_head)
    ):
        raise MathFlowError("research program state v2 has an invalid ledger head")
    base_digest = value.get("baseStateDigest")
    if base_digest is not None and (
        not isinstance(base_digest, str) or not DIGEST.fullmatch(base_digest)
    ):
        raise MathFlowError("research program state v2 has an invalid base digest")
    if value.get("rootProgramId") != "root":
        raise MathFlowError("research program state v2 must use root program 'root'")

    programs = value.get("programs")
    threads = value.get("threads")
    items = value.get("items")
    contributions = value.get("contributions")
    if any(
        not isinstance(collection, dict)
        for collection in (programs, threads, items, contributions)
    ):
        raise MathFlowError("research program state v2 collections must be objects")
    assert isinstance(programs, dict)
    assert isinstance(threads, dict)
    assert isinstance(items, dict)
    assert isinstance(contributions, dict)
    if "root" not in programs:
        raise MathFlowError("research program state v2 is missing its root program")
    for record_id, record in programs.items():
        _validate_program_v2(record, str(record_id))
    for record_id, record in threads.items():
        _validate_thread(record, str(record_id))
    for record_id, record in items.items():
        _validate_item(record, str(record_id))
    for record_id, record in contributions.items():
        _validate_contribution(record, str(record_id))

    root = programs["root"]
    if (
        root.get("parentId") is not None
        or root.get("parentThreadIds") != []
        or root.get("status") != "active"
        or root.get("lineage") != []
    ):
        raise MathFlowError(
            "research program state v2 root must be active and lineage-free"
        )

    for program_id, record in programs.items():
        parent_id = record.get("parentId")
        if program_id != "root":
            if parent_id not in programs:
                raise MathFlowError(
                    f"research program v2 has missing parent: {program_id}"
                )
            if not record.get("parentThreadIds"):
                raise MathFlowError(
                    f"non-root research program v2 must occupy a parent thread: {program_id}"
                )
        if isinstance(parent_id, str):
            for thread_id in record.get("parentThreadIds", []):
                thread = threads.get(thread_id)
                if not isinstance(thread, dict) or thread.get("programId") != parent_id:
                    raise MathFlowError(
                        f"program v2 parent thread is outside its parent program: {program_id}"
                    )

    for program_id in programs:
        observed: set[str] = set()
        cursor: str | None = str(program_id)
        while cursor is not None:
            if cursor in observed:
                raise MathFlowError(
                    f"research program v2 hierarchy contains a cycle: {program_id}"
                )
            observed.add(cursor)
            parent = programs[cursor].get("parentId")
            cursor = str(parent) if isinstance(parent, str) else None

    for program_id, record in programs.items():
        if record.get("status") != "active":
            continue
        cursor = record.get("parentId")
        while isinstance(cursor, str):
            ancestor = programs[cursor]
            if ancestor.get("status") == "retired":
                raise MathFlowError(
                    f"active research program has a retired ancestor: {program_id}"
                )
            cursor = ancestor.get("parentId")

    occupied_parent_threads: dict[str, str] = {}
    for program_id, record in programs.items():
        if record.get("status") != "active":
            continue
        for thread_id in record.get("parentThreadIds", []):
            prior = occupied_parent_threads.setdefault(str(thread_id), str(program_id))
            if prior != program_id:
                raise MathFlowError(
                    f"parent thread belongs to more than one active child program: {thread_id}"
                )

    for thread_id, record in threads.items():
        owner_id = record.get("programId")
        owner = programs.get(owner_id)
        if not isinstance(owner, dict):
            raise MathFlowError(
                f"research thread v2 {thread_id} has missing program: {owner_id}"
            )
        if owner.get("status") == "retired" and record.get("status") not in {
            "completed",
            "retired",
        }:
            raise MathFlowError(
                f"live research thread remains in a retired program: {thread_id}"
            )

    for program_id, program_record in programs.items():
        if program_record.get("status") != "active":
            continue
        catch_all = [
            thread
            for thread in threads.values()
            if thread.get("programId") == program_id
            and thread.get("kind") == "unstructured"
            and thread.get("status") not in {"completed", "retired"}
        ]
        if len(catch_all) != 1:
            raise MathFlowError(
                f"active research program v2 must have exactly one active unstructured thread: {program_id}"
            )

    for item_id, record in items.items():
        owner_id = record.get("programId")
        owner = programs.get(owner_id)
        if not isinstance(owner, dict):
            raise MathFlowError(
                f"research item v2 {item_id} has missing program: {owner_id}"
            )
        if owner.get("status") == "retired":
            raise MathFlowError(
                f"research item remains in a retired program: {item_id}"
            )
        for dependency_id in record.get("dependencyItemIds", []):
            if dependency_id not in items:
                raise MathFlowError(
                    f"research item v2 has missing dependency: {item_id}"
                )
        for reference in record.get("claimRefs", []):
            contribution = contributions.get(reference.get("transactionId"))
            if (
                not isinstance(contribution, dict)
                or reference.get("claimKey") not in contribution.get("claimKeys", [])
            ):
                raise MathFlowError(
                    f"research item v2 references a claim outside accepted state: {item_id}"
                )

    visiting_items: set[str] = set()
    visited_items: set[str] = set()

    def visit_item(item_id: str) -> None:
        if item_id in visited_items:
            return
        if item_id in visiting_items:
            raise MathFlowError(
                f"research item v2 dependency graph contains a cycle: {item_id}"
            )
        visiting_items.add(item_id)
        for dependency_id in items[item_id]["dependencyItemIds"]:
            visit_item(str(dependency_id))
        visiting_items.remove(item_id)
        visited_items.add(item_id)

    for item_id in items:
        visit_item(str(item_id))

    for contribution_id, record in contributions.items():
        if record.get("directProgramId") not in programs:
            raise MathFlowError(
                f"research contribution v2 has missing historical program: {contribution_id}"
            )
        if any(thread_id not in threads for thread_id in record.get("directThreadIds", [])):
            raise MathFlowError(
                f"research contribution v2 references a missing historical thread: {contribution_id}"
            )
        if any(item_id not in items for item_id in record.get("itemIds", [])):
            raise MathFlowError(
                f"research contribution v2 references a missing item: {contribution_id}"
            )
        if not record.get("directThreadIds") or not record.get("itemIds"):
            raise MathFlowError(
                f"research contribution v2 must name a historical line and durable item: {contribution_id}"
            )

    accepted_ids = set(contributions)
    for collection_name, collection in (
        ("program", programs),
        ("thread", threads),
        ("item", items),
    ):
        for record_id, record in collection.items():
            if not set(record.get("sourceTransactionIds", [])) <= accepted_ids:
                raise MathFlowError(
                    f"research {collection_name} v2 cites an unaccepted source: {record_id}"
                )

    _validate_lineage_graph(programs)
    if value.get("stateDigest") != _with_state_digest(value)["stateDigest"]:
        raise MathFlowError("research program state v2 digest mismatch")
    return value


def validate_research_program_state_versioned(
    value: object, problem: str | None = None
) -> dict[str, object]:
    """Validate any replayable hierarchical research-state contract."""

    if not isinstance(value, dict):
        raise MathFlowError("research program state must be an object")
    if value.get("schemaVersion") == 1:
        return validate_research_program_state(value, problem)
    if value.get("schemaVersion") == 2:
        return validate_research_program_state_v2(value, problem)
    if value.get("schemaVersion") == 3:
        # Local import avoids making the independent v7 reducer part of the
        # state-v1/v2 topology module's import graph.
        from .research_builder_v7 import validate_research_program_state_v3

        return validate_research_program_state_v3(value, problem)
    raise MathFlowError("research program state has an unsupported version")


def _normalize_entity_value(
    kind: str, entity_id: str, value: object
) -> dict[str, object]:
    if not isinstance(value, dict):
        raise MathFlowError("research topology operation value must be an object")
    expected = {
        "program": PROGRAM_V2_FIELDS - {"digest"},
        "thread": THREAD_FIELDS - {"digest"},
        "item": ITEM_FIELDS - {"digest"},
    }.get(kind)
    if expected is None or set(value) != expected:
        raise MathFlowError(f"research topology operation has invalid {kind} fields")
    if value.get("id") != entity_id:
        raise MathFlowError("research topology operation entity ID mismatch")
    normalized = copy.deepcopy(value)
    if kind == "program":
        normalized["lineage"] = _canonical_lineage(
            normalized.get("lineage"), entity_id
        )
    return _with_record_digest(normalized)


def _changed_fields(
    before: dict[str, object], after: dict[str, object]
) -> set[str]:
    return {
        key
        for key in set(before) | set(after)
        if key != "digest" and before.get(key) != after.get(key)
    }


def _lineage_keys(program: dict[str, object], relation: str) -> set[str]:
    return {
        str(item["programId"])
        for item in program.get("lineage", [])
        if item.get("relation") == relation
    }


def _validate_new_lineage_transition(
    base_state: dict[str, object], post_state: dict[str, object]
) -> None:
    base_programs = base_state["programs"]
    post_programs = post_state["programs"]
    assert isinstance(base_programs, dict)
    assert isinstance(post_programs, dict)

    for program_id, post_program in post_programs.items():
        assert isinstance(post_program, dict)
        base_program = base_programs.get(program_id)
        if base_program is not None:
            assert isinstance(base_program, dict)
        for relation in LINEAGE_RELATIONS:
            prior_ids = (
                _lineage_keys(base_program, relation)
                if isinstance(base_program, dict)
                else set()
            )
            current_ids = _lineage_keys(post_program, relation)
            if not prior_ids <= current_ids:
                raise MathFlowError(
                    f"research program lineage is append-only: {program_id}"
                )
            added_ids = current_ids - prior_ids
            if added_ids and prior_ids:
                raise MathFlowError(
                    f"research program lineage event must be atomic: {program_id}"
                )

        new_split_successors = _lineage_keys(
            post_program, "split-into"
        ) - (
            _lineage_keys(base_program, "split-into")
            if isinstance(base_program, dict)
            else set()
        )
        if new_split_successors:
            former_parent = (
                base_program.get("parentId")
                if isinstance(base_program, dict)
                else post_program.get("parentId")
            )
            if post_program.get("status") != "retired" or any(
                not isinstance(post_programs.get(successor_id), dict)
                or post_programs[successor_id].get("status") != "active"
                or post_programs[successor_id].get("parentId") != former_parent
                for successor_id in new_split_successors
            ):
                raise MathFlowError(
                    f"new research program split needs active sibling successors: {program_id}"
                )

        new_merge_predecessors = _lineage_keys(
            post_program, "merged-from"
        ) - (
            _lineage_keys(base_program, "merged-from")
            if isinstance(base_program, dict)
            else set()
        )
        if new_merge_predecessors and (
            post_program.get("status") != "active"
            or any(
                not isinstance(post_programs.get(predecessor_id), dict)
                or post_programs[predecessor_id].get("status") != "retired"
                for predecessor_id in new_merge_predecessors
            )
        ):
            raise MathFlowError(
                f"new research program merge needs retired predecessors and an active successor: {program_id}"
            )


def apply_research_topology_transition(
    base_state: dict[str, object], transition: object
) -> tuple[dict[str, object], dict[str, object]]:
    """Apply a topology-only state-v2 transition and derive its alignment."""

    validate_research_program_state_v2(base_state)
    if not isinstance(transition, dict) or set(transition) != {
        "schemaVersion",
        "baseStateDigest",
        "operations",
    }:
        raise MathFlowError("research topology transition has an invalid envelope")
    if transition.get("schemaVersion") != 1:
        raise MathFlowError("research topology transition has an unsupported version")
    if transition.get("baseStateDigest") != base_state.get("stateDigest"):
        raise MathFlowError("research topology transition has a stale base state")
    operations = transition.get("operations")
    if not isinstance(operations, list) or not operations:
        raise MathFlowError("research topology transition operations must be non-empty")

    result = copy.deepcopy(base_state)
    result.pop("stateDigest", None)
    collections = {
        kind: result[collection_name]
        for kind, collection_name in ENTITY_COLLECTIONS.items()
    }
    seen: set[tuple[str, str]] = set()
    for operation in operations:
        if not isinstance(operation, dict) or set(operation) != {
            "action",
            "entityKind",
            "entityId",
            "baseDigest",
            "value",
        }:
            raise MathFlowError("research topology operation has invalid fields")
        action = operation.get("action")
        kind = operation.get("entityKind")
        if action not in TRANSITION_ACTIONS:
            raise MathFlowError("research topology operation has an invalid action")
        if kind not in collections:
            raise MathFlowError("research topology operation has an invalid entity kind")
        entity_id = _require_identifier(
            operation.get("entityId"), "research topology entity ID"
        )
        key = (str(kind), entity_id)
        if key in seen:
            raise MathFlowError("research topology transition repeats an entity")
        seen.add(key)
        collection = collections[str(kind)]
        assert isinstance(collection, dict)
        existing = collection.get(entity_id)
        base_digest = operation.get("baseDigest")
        if action == "create":
            if existing is not None:
                raise MathFlowError(
                    "research topology create requires a new ID, but the entity "
                    f"already exists: {kind} {entity_id}"
                )
            if base_digest is not None:
                raise MathFlowError(
                    "research topology create requires null baseDigest: "
                    f"{kind} {entity_id}"
                )
        else:
            if not isinstance(existing, dict):
                raise MathFlowError(
                    "research topology operation requires an existing entity: "
                    f"{action} {kind} {entity_id}"
                )
            if base_digest != existing.get("digest"):
                raise MathFlowError(
                    "research topology operation baseDigest mismatch: "
                    f"{action} {kind} {entity_id} expected {existing.get('digest')}"
                )

        normalized = _normalize_entity_value(
            str(kind), entity_id, operation.get("value")
        )
        if action == "move":
            assert isinstance(existing, dict)
            if entity_id == "root":
                raise MathFlowError("research topology may not move the root program")
            allowed = {
                "program": {"parentId", "parentThreadIds", "lineage"},
                "thread": {"programId"},
                "item": {"programId"},
            }[str(kind)]
            changed = _changed_fields(existing, normalized)
            if not changed or not changed <= allowed:
                raise MathFlowError(
                    "research topology move must preserve identity, content, lifecycle, and provenance"
                )
            if kind == "program" and existing.get("status") != "active":
                raise MathFlowError("research topology may move only an active program")
        elif action == "retire":
            assert isinstance(existing, dict)
            if kind not in {"program", "thread"} or entity_id == "root":
                raise MathFlowError(
                    "research topology retirement applies only to non-root programs and threads"
                )
            if (
                existing.get("status") == "retired"
                or normalized.get("status") != "retired"
            ):
                raise MathFlowError(
                    "research topology retirement must newly retire its entity"
                )
            allowed = (
                {"status", "lineage"}
                if kind == "program"
                else {"status", "expectedExposure"}
            )
            if not _changed_fields(existing, normalized) <= allowed:
                raise MathFlowError(
                    "research topology retirement must preserve identity, content, placement, and provenance"
                )
            if kind == "thread" and normalized.get("expectedExposure") != "0":
                raise MathFlowError(
                    "retired research topology thread must have zero expected exposure"
                )
        collection[entity_id] = normalized

    result["baseStateDigest"] = base_state["stateDigest"]
    post_state = _with_state_digest(result)
    validate_research_program_state_v2(post_state, str(base_state["problemId"]))
    _validate_new_lineage_transition(base_state, post_state)
    alignment = derive_research_topology_alignment(base_state, post_state)
    return post_state, alignment


def _entity_parent(kind: str, record: dict[str, object]) -> str | None:
    if kind == "program":
        parent_id = record.get("parentId")
    else:
        parent_id = record.get("programId")
    return str(parent_id) if isinstance(parent_id, str) else None


def _identity_entry(
    kind: str,
    entity_id: str,
    before: dict[str, object] | None,
    after: dict[str, object] | None,
) -> dict[str, object]:
    entry: dict[str, object] = {"entityKind": kind, "entityId": entity_id}
    if before is not None:
        entry["beforeDigest"] = before["digest"]
    if after is not None:
        entry["afterDigest"] = after["digest"]
    return entry


def _new_lineage_edges(
    before_program: dict[str, object] | None,
    after_program: dict[str, object],
    relation: str,
) -> list[str]:
    before_edges = {
        str(item["programId"])
        for item in (before_program or {}).get("lineage", [])
        if item.get("relation") == relation
    }
    return sorted(
        str(item["programId"])
        for item in after_program.get("lineage", [])
        if item.get("relation") == relation
        and str(item["programId"]) not in before_edges
    )


def _sorted_identity_entries(entries: Iterable[dict[str, object]]) -> list[dict[str, object]]:
    return sorted(entries, key=lambda item: (str(item["entityKind"]), str(item["entityId"])))


def derive_research_topology_alignment(
    before_state: dict[str, object], after_state: dict[str, object]
) -> dict[str, object]:
    """Derive the canonical identity alignment between adjacent research states."""

    validate_research_program_state_versioned(before_state)
    validate_research_program_state_versioned(after_state)
    if before_state.get("problemId") != after_state.get("problemId"):
        raise MathFlowError("research topology alignment crosses problems")
    if after_state.get("baseStateDigest") != before_state.get("stateDigest"):
        raise MathFlowError("research topology alignment states are not adjacent")

    preserved: list[dict[str, object]] = []
    moved: list[dict[str, object]] = []
    created: list[dict[str, object]] = []
    retired: list[dict[str, object]] = []
    for kind, collection_name in ENTITY_COLLECTIONS.items():
        before_collection = before_state[collection_name]
        after_collection = after_state[collection_name]
        assert isinstance(before_collection, dict)
        assert isinstance(after_collection, dict)
        missing = set(before_collection) - set(after_collection)
        if missing:
            raise MathFlowError(
                f"research topology alignment removes an entity: {sorted(missing)[0]}"
            )
        for entity_id in sorted(after_collection):
            before = before_collection.get(entity_id)
            after = after_collection[entity_id]
            assert isinstance(after, dict)
            if not isinstance(before, dict):
                created.append(_identity_entry(kind, str(entity_id), None, after))
                continue
            if (
                kind in {"program", "thread"}
                and before.get("status") != "retired"
                and after.get("status") == "retired"
            ):
                retired.append(_identity_entry(kind, str(entity_id), before, after))
                continue
            before_parent = _entity_parent(kind, before)
            after_parent = _entity_parent(kind, after)
            parent_threads_changed = kind == "program" and before.get(
                "parentThreadIds"
            ) != after.get("parentThreadIds")
            if before_parent != after_parent or parent_threads_changed:
                entry = _identity_entry(kind, str(entity_id), before, after)
                entry.update(
                    {
                        "fromParentId": before_parent,
                        "toParentId": after_parent,
                        "fromParentThreadIds": (
                            list(before.get("parentThreadIds", []))
                            if kind == "program"
                            else []
                        ),
                        "toParentThreadIds": (
                            list(after.get("parentThreadIds", []))
                            if kind == "program"
                            else []
                        ),
                    }
                )
                moved.append(entry)
            else:
                preserved.append(_identity_entry(kind, str(entity_id), before, after))

    before_programs = before_state["programs"]
    after_programs = after_state["programs"]
    assert isinstance(before_programs, dict)
    assert isinstance(after_programs, dict)
    splits: list[dict[str, object]] = []
    merges: list[dict[str, object]] = []
    for program_id in sorted(after_programs):
        after_program = after_programs[program_id]
        before_program = before_programs.get(program_id)
        assert isinstance(after_program, dict)
        if before_program is not None:
            assert isinstance(before_program, dict)
        successor_ids = _new_lineage_edges(
            before_program, after_program, "split-into"
        )
        if successor_ids:
            splits.append(
                {
                    "predecessorProgramId": str(program_id),
                    "successorProgramIds": successor_ids,
                }
            )
        predecessor_ids = _new_lineage_edges(
            before_program, after_program, "merged-from"
        )
        if predecessor_ids:
            merges.append(
                {
                    "predecessorProgramIds": predecessor_ids,
                    "successorProgramId": str(program_id),
                }
            )

    value: dict[str, object] = {
        "schemaVersion": 1,
        "problemId": before_state["problemId"],
        "beforeKnowledgeStateDigest": before_state["stateDigest"],
        "afterKnowledgeStateDigest": after_state["stateDigest"],
        "preserved": _sorted_identity_entries(preserved),
        "moved": _sorted_identity_entries(moved),
        "splits": sorted(
            splits, key=lambda item: str(item["predecessorProgramId"])
        ),
        "merges": sorted(
            merges, key=lambda item: str(item["successorProgramId"])
        ),
        "created": _sorted_identity_entries(created),
        "retired": _sorted_identity_entries(retired),
    }
    return {**value, "alignmentDigest": f"sha256:{sha256_json(value)}"}


def validate_research_topology_alignment(
    alignment: object,
    before_state: dict[str, object],
    after_state: dict[str, object],
) -> dict[str, object]:
    if not isinstance(alignment, dict):
        raise MathFlowError("research topology alignment must be an object")
    expected = derive_research_topology_alignment(before_state, after_state)
    if alignment != expected:
        raise MathFlowError(
            "research topology alignment differs from the deterministic state alignment"
        )
    return alignment
