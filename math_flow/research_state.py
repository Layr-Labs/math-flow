from __future__ import annotations

import copy
import re
from decimal import Decimal, InvalidOperation
from fractions import Fraction

from .errors import MathFlowError
from .repository import sha256_json


IDENTIFIER = re.compile(r"^[a-z0-9][a-z0-9/_-]*$")
GIT_SHA = re.compile(r"^[0-9a-f]{40}$")
DIGEST = re.compile(r"^sha256:[0-9a-f]{64}$")

PROGRAM_STATUSES = {"active", "completed", "retired"}
THREAD_KINDS = {"research", "verification", "exploration", "unstructured"}
THREAD_STATUSES = {
    "active",
    "queued",
    "conditional",
    "blocked",
    "exploratory",
    "completed",
    "retired",
}
ITEM_TYPES = {"result", "proof", "method", "computation", "tool", "question"}
CONFIDENCE_LEVELS = {"low", "medium", "high"}

PROGRAM_FIELDS = {
    "id",
    "parentId",
    "title",
    "objective",
    "status",
    "parentThreadIds",
    "sourceTransactionIds",
    "digest",
}
THREAD_FIELDS = {
    "id",
    "programId",
    "title",
    "summary",
    "kind",
    "status",
    "expectedExposure",
    "conditions",
    "sourceTransactionIds",
    "digest",
}
ITEM_FIELDS = {
    "id",
    "programId",
    "type",
    "title",
    "summary",
    "claimRefs",
    "sourceTransactionIds",
    "dependencyItemIds",
    "digest",
}
CONTRIBUTION_FIELDS = {
    "id",
    "transactionId",
    "claimKeys",
    "directProgramId",
    "directThreadIds",
    "itemIds",
    "dependencyTransactionIds",
    "judgmentId",
    "digest",
}
STATE_FIELDS = {
    "schemaVersion",
    "problemId",
    "ledgerHead",
    "baseStateDigest",
    "rootProgramId",
    "programs",
    "threads",
    "items",
    "contributions",
    "stateDigest",
}


def _record_digest(record: dict[str, object]) -> str:
    return f"sha256:{sha256_json({key: value for key, value in record.items() if key != 'digest'})}"


def _with_record_digest(record: dict[str, object]) -> dict[str, object]:
    value = {key: copy.deepcopy(item) for key, item in record.items() if key != "digest"}
    return {**value, "digest": _record_digest(value)}


def _with_state_digest(state: dict[str, object]) -> dict[str, object]:
    value = {key: copy.deepcopy(item) for key, item in state.items() if key != "stateDigest"}
    return {**value, "stateDigest": f"sha256:{sha256_json(value)}"}


def _require_text(value: object, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise MathFlowError(f"{label} must be non-empty text")
    return value.strip()


def _require_identifier(value: object, label: str) -> str:
    if not isinstance(value, str) or not IDENTIFIER.fullmatch(value):
        raise MathFlowError(f"{label} must be a stable lowercase path")
    return value


def _require_strings(value: object, label: str) -> list[str]:
    if (
        not isinstance(value, list)
        or any(not isinstance(item, str) or not item for item in value)
        or len(value) != len(set(value))
    ):
        raise MathFlowError(f"{label} must contain unique non-empty strings")
    return list(value)


def _claim_ref(value: object, label: str) -> dict[str, str]:
    if not isinstance(value, dict) or set(value) != {"transactionId", "claimKey"}:
        raise MathFlowError(f"{label} must be a claim reference")
    transaction_id = value.get("transactionId")
    claim_key = value.get("claimKey")
    if not isinstance(transaction_id, str) or not GIT_SHA.fullmatch(transaction_id):
        raise MathFlowError(f"{label} has an invalid transaction ID")
    return {
        "transactionId": transaction_id,
        "claimKey": _require_identifier(claim_key, f"{label} claimKey"),
    }


def _claim_refs(value: object, label: str) -> list[dict[str, str]]:
    if not isinstance(value, list):
        raise MathFlowError(f"{label} must be an array")
    result = [_claim_ref(item, label) for item in value]
    keys = [(item["transactionId"], item["claimKey"]) for item in result]
    if len(keys) != len(set(keys)):
        raise MathFlowError(f"{label} contains duplicate claim references")
    return result


def empty_research_program_state(problem: str) -> dict[str, object]:
    root = _with_record_digest(
        {
            "id": "root",
            "parentId": None,
            "title": "Canonical problem",
            "objective": "Resolve the canonical problem.",
            "status": "active",
            "parentThreadIds": [],
            "sourceTransactionIds": [],
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
            "schemaVersion": 1,
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


def _validate_program(record: object, record_id: str) -> dict[str, object]:
    if not isinstance(record, dict) or set(record) != PROGRAM_FIELDS:
        raise MathFlowError(f"research program has invalid fields: {record_id}")
    if record.get("id") != record_id:
        raise MathFlowError(f"research program ID mismatch: {record_id}")
    _require_identifier(record_id, "research program ID")
    parent_id = record.get("parentId")
    if parent_id is not None:
        _require_identifier(parent_id, "research program parent ID")
    _require_text(record.get("title"), "research program title")
    _require_text(record.get("objective"), "research program objective")
    if record.get("status") not in PROGRAM_STATUSES:
        raise MathFlowError(f"research program has invalid status: {record_id}")
    _require_strings(record.get("parentThreadIds"), "program parentThreadIds")
    sources = _require_strings(
        record.get("sourceTransactionIds"), "program sourceTransactionIds"
    )
    if any(not GIT_SHA.fullmatch(item) for item in sources):
        raise MathFlowError(f"research program has invalid transaction provenance: {record_id}")
    if record.get("digest") != _record_digest(record):
        raise MathFlowError(f"research program digest mismatch: {record_id}")
    return record


def _validate_thread(record: object, record_id: str) -> dict[str, object]:
    if not isinstance(record, dict) or set(record) != THREAD_FIELDS:
        raise MathFlowError(f"research thread has invalid fields: {record_id}")
    if record.get("id") != record_id:
        raise MathFlowError(f"research thread ID mismatch: {record_id}")
    _require_identifier(record_id, "research thread ID")
    _require_identifier(record.get("programId"), "research thread program ID")
    _require_text(record.get("title"), "research thread title")
    _require_text(record.get("summary"), "research thread summary")
    if record.get("kind") not in THREAD_KINDS:
        raise MathFlowError(f"research thread has invalid kind: {record_id}")
    if record.get("status") not in THREAD_STATUSES:
        raise MathFlowError(f"research thread has invalid status: {record_id}")
    exposure = _decimal(
        record.get("expectedExposure"), "research thread expectedExposure"
    )
    if record.get("status") in {"completed", "retired"} and exposure != 0:
        raise MathFlowError(
            f"completed or retired research thread must have zero exposure: {record_id}"
        )
    _require_strings(record.get("conditions"), "research thread conditions")
    sources = _require_strings(
        record.get("sourceTransactionIds"), "thread sourceTransactionIds"
    )
    if any(not GIT_SHA.fullmatch(item) for item in sources):
        raise MathFlowError(f"research thread has invalid transaction provenance: {record_id}")
    if record.get("digest") != _record_digest(record):
        raise MathFlowError(f"research thread digest mismatch: {record_id}")
    return record


def _validate_item(record: object, record_id: str) -> dict[str, object]:
    if not isinstance(record, dict) or set(record) != ITEM_FIELDS:
        raise MathFlowError(f"research item has invalid fields: {record_id}")
    if record.get("id") != record_id:
        raise MathFlowError(f"research item ID mismatch: {record_id}")
    _require_identifier(record_id, "research item ID")
    _require_identifier(record.get("programId"), "research item program ID")
    if record.get("type") not in ITEM_TYPES:
        raise MathFlowError(f"research item has invalid type: {record_id}")
    _require_text(record.get("title"), "research item title")
    _require_text(record.get("summary"), "research item summary")
    _claim_refs(record.get("claimRefs"), "research item claimRefs")
    sources = _require_strings(
        record.get("sourceTransactionIds"), "item sourceTransactionIds"
    )
    if any(not GIT_SHA.fullmatch(item) for item in sources):
        raise MathFlowError(f"research item has invalid transaction provenance: {record_id}")
    _require_strings(record.get("dependencyItemIds"), "item dependencyItemIds")
    if record.get("digest") != _record_digest(record):
        raise MathFlowError(f"research item digest mismatch: {record_id}")
    return record


def _validate_contribution(record: object, record_id: str) -> dict[str, object]:
    if not isinstance(record, dict) or set(record) != CONTRIBUTION_FIELDS:
        raise MathFlowError(f"research contribution has invalid fields: {record_id}")
    if record.get("id") != record_id:
        raise MathFlowError(f"research contribution ID mismatch: {record_id}")
    transaction_id = record.get("transactionId")
    if not isinstance(transaction_id, str) or not GIT_SHA.fullmatch(transaction_id):
        raise MathFlowError(f"research contribution has invalid transaction ID: {record_id}")
    claim_keys = _require_strings(
        record.get("claimKeys"), "research contribution claimKeys"
    )
    if not claim_keys or any(not IDENTIFIER.fullmatch(item) for item in claim_keys):
        raise MathFlowError(
            f"research contribution has invalid claim keys: {record_id}"
        )
    _require_identifier(record.get("directProgramId"), "contribution directProgramId")
    _require_strings(record.get("directThreadIds"), "contribution directThreadIds")
    _require_strings(record.get("itemIds"), "contribution itemIds")
    dependencies = _require_strings(
        record.get("dependencyTransactionIds"),
        "contribution dependencyTransactionIds",
    )
    if any(not GIT_SHA.fullmatch(item) for item in dependencies):
        raise MathFlowError(
            f"research contribution has invalid dependency transaction: {record_id}"
        )
    judgment_id = record.get("judgmentId")
    if not isinstance(judgment_id, str) or not DIGEST.fullmatch(judgment_id):
        raise MathFlowError(f"research contribution has invalid judgment ID: {record_id}")
    if record.get("digest") != _record_digest(record):
        raise MathFlowError(f"research contribution digest mismatch: {record_id}")
    return record


def validate_research_program_state(
    value: object, problem: str | None = None
) -> dict[str, object]:
    if not isinstance(value, dict) or set(value) != STATE_FIELDS:
        raise MathFlowError("research program state has an invalid envelope")
    if value.get("schemaVersion") != 1:
        raise MathFlowError("research program state has an unsupported version")
    if problem is not None and value.get("problemId") != problem:
        raise MathFlowError("research program state belongs to another problem")
    _require_identifier(value.get("problemId"), "research program problem ID")
    ledger_head = value.get("ledgerHead")
    if ledger_head is not None and (
        not isinstance(ledger_head, str) or not GIT_SHA.fullmatch(ledger_head)
    ):
        raise MathFlowError("research program state has an invalid ledger head")
    base_digest = value.get("baseStateDigest")
    if base_digest is not None and (
        not isinstance(base_digest, str) or not DIGEST.fullmatch(base_digest)
    ):
        raise MathFlowError("research program state has an invalid base digest")
    if value.get("rootProgramId") != "root":
        raise MathFlowError("research program state must use root program 'root'")
    programs = value.get("programs")
    threads = value.get("threads")
    items = value.get("items")
    contributions = value.get("contributions")
    if any(not isinstance(item, dict) for item in (programs, threads, items, contributions)):
        raise MathFlowError("research program state collections must be objects")
    assert isinstance(programs, dict)
    assert isinstance(threads, dict)
    assert isinstance(items, dict)
    assert isinstance(contributions, dict)
    if "root" not in programs:
        raise MathFlowError("research program state is missing its root program")
    for record_id, record in programs.items():
        _validate_program(record, str(record_id))
    for record_id, record in threads.items():
        _validate_thread(record, str(record_id))
    for record_id, record in items.items():
        _validate_item(record, str(record_id))
    for record_id, record in contributions.items():
        _validate_contribution(record, str(record_id))

    root = programs["root"]
    if root.get("parentId") is not None or root.get("parentThreadIds") != []:
        raise MathFlowError("root program may not have a parent or parent threads")
    for program_id, record in programs.items():
        parent_id = record.get("parentId")
        if program_id != "root":
            if parent_id not in programs:
                raise MathFlowError(f"research program has missing parent: {program_id}")
            if not record.get("parentThreadIds"):
                raise MathFlowError(
                    f"non-root research program must occupy a parent thread: {program_id}"
                )
        if isinstance(parent_id, str):
            for thread_id in record.get("parentThreadIds", []):
                thread = threads.get(thread_id)
                if not isinstance(thread, dict) or thread.get("programId") != parent_id:
                    raise MathFlowError(
                        f"program parent thread is outside its parent program: {program_id}"
                    )
    for program_id in programs:
        observed: set[str] = set()
        cursor: str | None = str(program_id)
        while cursor is not None:
            if cursor in observed:
                raise MathFlowError(f"research program hierarchy contains a cycle: {program_id}")
            observed.add(cursor)
            parent = programs[cursor].get("parentId")
            cursor = str(parent) if isinstance(parent, str) else None

    for thread_id, record in threads.items():
        if record.get("programId") not in programs:
            raise MathFlowError(f"research thread has missing program: {thread_id}")
    parent_thread_owner: dict[str, str] = {}
    for program_id, record in programs.items():
        for thread_id in record.get("parentThreadIds", []):
            owner = parent_thread_owner.setdefault(str(thread_id), str(program_id))
            if owner != program_id:
                raise MathFlowError(
                    f"parent thread belongs to more than one child program: {thread_id}"
                )
    for program_id, program in programs.items():
        if program.get("status") != "active":
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
                f"active program must have exactly one active unstructured thread: {program_id}"
            )

    for item_id, record in items.items():
        if record.get("programId") not in programs:
            raise MathFlowError(f"research item has missing program: {item_id}")
        for dependency_id in record.get("dependencyItemIds", []):
            if dependency_id not in items:
                raise MathFlowError(f"research item has missing dependency: {item_id}")
        for reference in record.get("claimRefs", []):
            contribution = contributions.get(reference.get("transactionId"))
            if (
                not isinstance(contribution, dict)
                or reference.get("claimKey") not in contribution.get("claimKeys", [])
            ):
                raise MathFlowError(
                    f"research item references a claim outside accepted state: {item_id}"
                )
    visiting_items: set[str] = set()
    visited_items: set[str] = set()

    def visit_item(item_id: str) -> None:
        if item_id in visited_items:
            return
        if item_id in visiting_items:
            raise MathFlowError(
                f"research item dependency graph contains a cycle: {item_id}"
            )
        visiting_items.add(item_id)
        for dependency_item_id in items[item_id]["dependencyItemIds"]:
            visit_item(str(dependency_item_id))
        visiting_items.remove(item_id)
        visited_items.add(item_id)

    for item_id in items:
        visit_item(str(item_id))
    for contribution_id, record in contributions.items():
        direct_program = record.get("directProgramId")
        if direct_program not in programs:
            raise MathFlowError(
                f"research contribution has missing direct program: {contribution_id}"
            )
        for thread_id in record.get("directThreadIds", []):
            thread = threads.get(thread_id)
            if not isinstance(thread, dict) or thread.get("programId") != direct_program:
                raise MathFlowError(
                    f"contribution direct thread is outside its direct program: {contribution_id}"
                )
        for item_id in record.get("itemIds", []):
            item = items.get(item_id)
            if not isinstance(item, dict):
                raise MathFlowError(
                    f"research contribution references a missing item: {contribution_id}"
                )
            if item.get("programId") != direct_program:
                raise MathFlowError(
                    f"research contribution item is outside its direct program: {contribution_id}"
                )
        if not record.get("directThreadIds") or not record.get("itemIds"):
            raise MathFlowError(
                f"research contribution must name a direct line and durable item: {contribution_id}"
            )
    accepted_transaction_ids = set(contributions)
    for collection_name, collection in (
        ("program", programs),
        ("thread", threads),
        ("item", items),
    ):
        for record_id, record in collection.items():
            if not set(record.get("sourceTransactionIds", [])) <= accepted_transaction_ids:
                raise MathFlowError(
                    f"research {collection_name} cites an unaccepted source: {record_id}"
                )
    if value.get("stateDigest") != _with_state_digest(value)["stateDigest"]:
        raise MathFlowError("research program state digest mismatch")
    return value


def _normalize_entity_value(
    kind: str, entity_id: str, value: object
) -> dict[str, object]:
    if not isinstance(value, dict):
        raise MathFlowError("research program delta entity value must be an object")
    expected = {
        "program": PROGRAM_FIELDS - {"digest"},
        "thread": THREAD_FIELDS - {"digest"},
        "item": ITEM_FIELDS - {"digest"},
    }.get(kind)
    if expected is None or set(value) != expected:
        raise MathFlowError(f"research program delta has invalid {kind} fields")
    if value.get("id") != entity_id:
        raise MathFlowError("research program delta entity ID mismatch")
    return _with_record_digest(value)


def apply_research_program_delta(
    base_state: dict[str, object],
    delta: object,
    *,
    ledger_head: str,
    subject_transaction_id: str,
    accepted_claims: list[dict[str, object]],
    judgment_id: str,
) -> dict[str, object]:
    validate_research_program_state(base_state)
    if ledger_head != subject_transaction_id or not GIT_SHA.fullmatch(ledger_head):
        raise MathFlowError("research program transition must be bound to its subject transaction")
    if not isinstance(delta, dict) or set(delta) != {
        "schemaVersion",
        "operations",
        "contribution",
    }:
        raise MathFlowError("research program delta has an invalid envelope")
    if delta.get("schemaVersion") != 1:
        raise MathFlowError("research program delta has an unsupported version")
    operations = delta.get("operations")
    contribution_value = delta.get("contribution")
    if not isinstance(operations, list) or not isinstance(contribution_value, dict):
        raise MathFlowError("research program delta content is invalid")

    result = copy.deepcopy(base_state)
    result.pop("stateDigest", None)
    collections = {
        "program": result["programs"],
        "thread": result["threads"],
        "item": result["items"],
    }
    existing_contributions = result["contributions"]
    assert isinstance(existing_contributions, dict)
    assert all(isinstance(collection, dict) for collection in collections.values())
    seen_operations: set[tuple[str, str]] = set()
    for operation in operations:
        if not isinstance(operation, dict) or set(operation) != {
            "entityKind",
            "entityId",
            "baseDigest",
            "value",
        }:
            raise MathFlowError("research program delta operation has invalid fields")
        kind = operation.get("entityKind")
        entity_id = operation.get("entityId")
        if kind not in collections:
            raise MathFlowError("research program delta has an invalid entity kind")
        entity_id = _require_identifier(entity_id, "research program delta entity ID")
        key = (str(kind), entity_id)
        if key in seen_operations:
            raise MathFlowError("research program delta updates one entity more than once")
        seen_operations.add(key)
        collection = collections[str(kind)]
        assert isinstance(collection, dict)
        existing = collection.get(entity_id)
        base_digest = operation.get("baseDigest")
        if existing is None:
            if base_digest is not None:
                raise MathFlowError("new research program entity must use null baseDigest")
        elif base_digest != existing.get("digest"):
            raise MathFlowError("research program delta baseDigest mismatch")
        normalized = _normalize_entity_value(
            str(kind), entity_id, operation.get("value")
        )
        allowed_sources = set(existing_contributions) | {subject_transaction_id}
        if subject_transaction_id not in normalized.get("sourceTransactionIds", []):
            raise MathFlowError(
                "every research program update must cite its subject transaction"
            )
        if not set(normalized.get("sourceTransactionIds", [])) <= allowed_sources:
            raise MathFlowError(
                "research program update cites a transaction outside accepted state"
            )
        if isinstance(existing, dict):
            immutable_fields = {
                "program": ("parentId", "parentThreadIds"),
                "thread": ("programId", "kind"),
                "item": ("programId", "type"),
            }[str(kind)]
            if any(normalized.get(field) != existing.get(field) for field in immutable_fields):
                raise MathFlowError(
                    f"research program v1 does not permit changing {kind} topology or type"
                )
            if not set(existing.get("sourceTransactionIds", [])) <= set(
                normalized.get("sourceTransactionIds", [])
            ):
                raise MathFlowError(
                    "research program v1 provenance is additive and may not be removed"
                )
            if kind == "item":
                old_claim_refs = {
                    (str(ref["transactionId"]), str(ref["claimKey"]))
                    for ref in existing.get("claimRefs", [])
                }
                new_claim_refs = {
                    (str(ref["transactionId"]), str(ref["claimKey"]))
                    for ref in normalized.get("claimRefs", [])
                }
                if not old_claim_refs <= new_claim_refs or not set(
                    existing.get("dependencyItemIds", [])
                ) <= set(normalized.get("dependencyItemIds", [])):
                    raise MathFlowError(
                        "research item claim and dependency provenance is additive"
                    )
        collection[entity_id] = normalized

    claim_by_key = {str(claim["claimKey"]): claim for claim in accepted_claims}
    if len(claim_by_key) != len(accepted_claims):
        raise MathFlowError("accepted claims contain duplicate claim keys")
    contributions = result["contributions"]
    assert isinstance(contributions, dict)
    if set(contribution_value) != {
        "claimKeys",
        "directProgramId",
        "directThreadIds",
        "itemIds",
    }:
        raise MathFlowError("research program contribution mapping has invalid fields")
    claim_keys = _require_strings(
        contribution_value.get("claimKeys"), "research program contribution claimKeys"
    )
    if set(claim_keys) != set(claim_by_key):
        raise MathFlowError(
            "research program contribution must include every accepted claim exactly once"
        )
    direct_program_id = _require_identifier(
        contribution_value.get("directProgramId"), "contribution direct program ID"
    )
    direct_thread_ids = _require_strings(
        contribution_value.get("directThreadIds"), "contribution directThreadIds"
    )
    item_ids = _require_strings(
        contribution_value.get("itemIds"), "contribution itemIds"
    )
    contribution_id = subject_transaction_id
    if contribution_id in contributions:
        raise MathFlowError("research program state already contains this contribution")
    dependency_ids: list[str] = []
    for claim_key in claim_keys:
        raw_dependencies = claim_by_key[claim_key].get("dependencyTransactionIds")
        if not isinstance(raw_dependencies, list):
            raise MathFlowError("accepted claim dependencies are invalid")
        dependency_ids.extend(str(item) for item in raw_dependencies)
    contribution = _with_record_digest(
        {
            "id": contribution_id,
            "transactionId": subject_transaction_id,
            "claimKeys": claim_keys,
            "directProgramId": direct_program_id,
            "directThreadIds": direct_thread_ids,
            "itemIds": item_ids,
            "dependencyTransactionIds": list(dict.fromkeys(dependency_ids)),
            "judgmentId": judgment_id,
        }
    )
    contributions[contribution_id] = contribution

    result["ledgerHead"] = ledger_head
    result["baseStateDigest"] = base_state["stateDigest"]
    next_state = _with_state_digest(result)
    validate_research_program_state(next_state, str(base_state["problemId"]))

    new_claim_refs = {
        (subject_transaction_id, str(claim["claimKey"])) for claim in accepted_claims
    }
    contribution_items = {
        item_id: next_state["items"][item_id]
        for item_id in item_ids
    }
    represented = {
        (str(ref["transactionId"]), str(ref["claimKey"]))
        for item in contribution_items.values()
        for ref in item.get("claimRefs", [])
    }
    missing = new_claim_refs - represented
    if missing:
        raise MathFlowError(
            f"accepted claim is not represented by a research item: {sorted(missing)[0][1]}"
        )
    return next_state


def research_program_index(state: dict[str, object]) -> dict[str, object]:
    validate_research_program_state(state)
    return {
        "programs": [
            {
                "id": record["id"],
                "parentId": record["parentId"],
                "title": record["title"],
                "objective": record["objective"],
                "status": record["status"],
                "digest": record["digest"],
            }
            for _, record in sorted(state["programs"].items())
        ],
        "threads": [
            {
                "id": record["id"],
                "programId": record["programId"],
                "title": record["title"],
                "kind": record["kind"],
                "status": record["status"],
                "expectedExposure": record["expectedExposure"],
                "digest": record["digest"],
            }
            for _, record in sorted(state["threads"].items())
        ],
        "items": [
            {
                "id": record["id"],
                "programId": record["programId"],
                "type": record["type"],
                "title": record["title"],
                "digest": record["digest"],
            }
            for _, record in sorted(state["items"].items())
        ],
    }


def _decimal(value: object, label: str, *, nonnegative: bool = True) -> Decimal:
    if isinstance(value, bool) or not isinstance(value, (int, float, str)):
        raise MathFlowError(f"{label} must be a decimal work estimate")
    try:
        result = Decimal(str(value))
    except InvalidOperation as exc:
        raise MathFlowError(f"{label} must be a decimal work estimate") from exc
    if not result.is_finite() or (nonnegative and result < 0):
        raise MathFlowError(f"{label} must be a finite non-negative work estimate")
    return result


def _decimal_text(value: Decimal) -> str:
    normalized = value.normalize()
    if normalized == normalized.to_integral():
        return str(normalized.quantize(Decimal(1)))
    return format(normalized, "f")


def credit_children(state: dict[str, object], program_id: str) -> list[dict[str, str]]:
    validate_research_program_state(state)
    children = [
        {"kind": "program", "id": child_id}
        for child_id, program in state["programs"].items()
        if program.get("parentId") == program_id
    ]
    children.extend(
        {"kind": "contribution", "id": contribution_id}
        for contribution_id, contribution in state["contributions"].items()
        if contribution.get("directProgramId") == program_id
    )
    return sorted(children, key=lambda item: (item["kind"], item["id"]))


def affected_credit_targets(
    state: dict[str, object], transaction_id: str
) -> dict[str, list[dict[str, str]]]:
    validate_research_program_state(state)
    contribution = state["contributions"].get(transaction_id)
    if not isinstance(contribution, dict):
        raise MathFlowError("credit update subject is not an accepted contribution")
    direct_program_id = str(contribution["directProgramId"])
    targets: dict[str, list[dict[str, str]]] = {
        direct_program_id: [{"kind": "contribution", "id": transaction_id}]
    }
    child_program_id = direct_program_id
    parent = state["programs"][child_program_id].get("parentId")
    while isinstance(parent, str):
        targets.setdefault(parent, []).append(
            {"kind": "program", "id": child_program_id}
        )
        child_program_id = parent
        parent = state["programs"][child_program_id].get("parentId")
    return {
        program_id: sorted(children, key=lambda item: (item["kind"], item["id"]))
        for program_id, children in targets.items()
    }


def credit_child_thread_ids(
    state: dict[str, object], program_id: str, kind: str, child_id: str
) -> list[str]:
    validate_research_program_state(state)
    if kind == "program":
        child = state["programs"].get(child_id)
        if not isinstance(child, dict) or child.get("parentId") != program_id:
            raise MathFlowError("credit child program is outside the local program")
        thread_ids = child.get("parentThreadIds")
    elif kind == "contribution":
        child = state["contributions"].get(child_id)
        if not isinstance(child, dict) or child.get("directProgramId") != program_id:
            raise MathFlowError("credit child contribution is outside the local program")
        thread_ids = child.get("directThreadIds")
    else:
        raise MathFlowError("credit child kind is invalid")
    return _require_strings(thread_ids, "credit child direct thread IDs")


def _local_thread_snapshot(
    state: dict[str, object], program_id: str
) -> list[dict[str, object]]:
    return [
        {
            "id": thread["id"],
            "title": thread["title"],
            "summary": thread["summary"],
            "kind": thread["kind"],
            "status": thread["status"],
            "expectedExposure": thread["expectedExposure"],
            "conditions": copy.deepcopy(thread["conditions"]),
            "digest": thread["digest"],
        }
        for _, thread in sorted(state["threads"].items())
        if thread.get("programId") == program_id
    ]


def _effect(
    value: object,
    *,
    label: str,
    allowed_thread_ids: set[str],
    require_reduction: bool,
) -> tuple[dict[str, object], Decimal]:
    if not isinstance(value, dict) or set(value) != {
        "threadId",
        "withoutWork",
        "withWork",
        "rationale",
    }:
        raise MathFlowError(f"{label} has invalid fields")
    thread_id = value.get("threadId")
    if not isinstance(thread_id, str) or thread_id not in allowed_thread_ids:
        raise MathFlowError(f"{label} references a thread outside the local program")
    without_work = _decimal(value.get("withoutWork"), f"{label} withoutWork")
    with_work = _decimal(value.get("withWork"), f"{label} withWork")
    if require_reduction and with_work > without_work:
        raise MathFlowError(f"{label} obviated work must weakly reduce exposure")
    rationale = _require_text(value.get("rationale"), f"{label} rationale")
    return (
        {
            "threadId": thread_id,
            "withoutWork": _decimal_text(without_work),
            "withWork": _decimal_text(with_work),
            "rationale": rationale,
        },
        without_work - with_work,
    )


def _fraction(numerator: Decimal, denominator: Decimal) -> dict[str, str]:
    return {
        "numerator": _decimal_text(numerator),
        "denominator": _decimal_text(denominator),
    }


def _multiply_fractions(
    left: dict[str, str], right: dict[str, str]
) -> dict[str, str]:
    return _fraction(
        Decimal(left["numerator"]) * Decimal(right["numerator"]),
        Decimal(left["denominator"]) * Decimal(right["denominator"]),
    )


def materialize_credit_evaluations(
    *,
    prior_credit_state: dict[str, object] | None,
    base_program_state: dict[str, object],
    post_program_state: dict[str, object],
    horizon_program_state: dict[str, object],
    subject_transaction_id: str | None,
    raw_delta: object,
    target_children_by_program: dict[str, list[dict[str, str]]] | None = None,
) -> dict[str, object]:
    validate_research_program_state(base_program_state)
    validate_research_program_state(post_program_state)
    validate_research_program_state(horizon_program_state)
    stationary_refresh = (
        post_program_state.get("stateDigest") == base_program_state.get("stateDigest")
        and target_children_by_program is not None
    )
    if (
        post_program_state.get("baseStateDigest")
        != base_program_state.get("stateDigest")
        and not stationary_refresh
    ):
        raise MathFlowError("credit evaluation post state does not extend its base state")
    if subject_transaction_id is not None:
        if subject_transaction_id not in post_program_state["contributions"]:
            raise MathFlowError("credit evaluation subject is absent from the post state")
        if subject_transaction_id not in horizon_program_state["contributions"]:
            raise MathFlowError("credit evaluation subject is absent from the horizon state")
    if not isinstance(raw_delta, dict) or set(raw_delta) != {
        "schemaVersion",
        "evaluations",
    }:
        raise MathFlowError("hierarchical credit delta has an invalid envelope")
    if raw_delta.get("schemaVersion") != 1 or not isinstance(
        raw_delta.get("evaluations"), list
    ):
        raise MathFlowError("hierarchical credit delta has an invalid version or evaluations")

    required_targets = (
        target_children_by_program
        if target_children_by_program is not None
        else affected_credit_targets(post_program_state, str(subject_transaction_id))
    )
    existing_evaluations: dict[str, object] = {}
    base_credit_digest = None
    if prior_credit_state is not None:
        validated_prior = validate_hierarchical_credit_state(
            prior_credit_state, str(post_program_state["problemId"])
        )
        if validated_prior.get("programStateDigest") != base_program_state.get(
            "stateDigest"
        ):
            raise MathFlowError(
                "prior hierarchical credit state does not describe the base program state"
            )
        existing_evaluations = copy.deepcopy(validated_prior["evaluations"])
        base_credit_digest = validated_prior["stateDigest"]

    supplied: dict[str, dict[str, object]] = {}
    for raw_evaluation in raw_delta["evaluations"]:
        if not isinstance(raw_evaluation, dict) or set(raw_evaluation) != {
            "programId",
            "unattributedWork",
            "rationale",
            "children",
        }:
            raise MathFlowError("hierarchical credit program evaluation has invalid fields")
        program_id = raw_evaluation.get("programId")
        if not isinstance(program_id, str) or program_id in supplied:
            raise MathFlowError("hierarchical credit program IDs must be unique")
        supplied[program_id] = raw_evaluation
    if set(supplied) != set(required_targets):
        raise MathFlowError("hierarchical credit delta must evaluate the affected program path")

    for program_id, target_children in required_targets.items():
        raw_evaluation = supplied[program_id]
        raw_children = raw_evaluation["children"]
        if not isinstance(raw_children, list):
            raise MathFlowError("hierarchical credit children must be an array")
        prior_evaluation = existing_evaluations.get(program_id)
        prior_children = {
            (str(child["kind"]), str(child["id"])): copy.deepcopy(child)
            for child in (
                prior_evaluation.get("children", [])
                if isinstance(prior_evaluation, dict)
                else []
            )
            if isinstance(child, dict)
            and child.get("kind") in {"program", "contribution"}
            and isinstance(child.get("id"), str)
        }
        observed_targets: list[dict[str, str]] = []
        for raw_child in raw_children:
            if not isinstance(raw_child, dict) or set(raw_child) != {
                "kind",
                "id",
                "counterfactual",
                "directEffects",
                "obviatedEffects",
                "confidence",
                "evidenceRefs",
            }:
                raise MathFlowError("hierarchical credit child assessment has invalid fields")
            kind = raw_child.get("kind")
            child_id = raw_child.get("id")
            if kind not in {"program", "contribution"} or not isinstance(child_id, str):
                raise MathFlowError("hierarchical credit child reference is invalid")
            child_key = (str(kind), child_id)
            observed_targets.append({"kind": str(kind), "id": child_id})
            counterfactual = _require_text(
                raw_child.get("counterfactual"), "credit counterfactual"
            )
            if raw_child.get("confidence") not in CONFIDENCE_LEVELS:
                raise MathFlowError("hierarchical credit confidence is invalid")
            evidence_refs = _require_strings(
                raw_child.get("evidenceRefs"), "credit evidenceRefs"
            )
            direct_raw = raw_child.get("directEffects")
            obviated_raw = raw_child.get("obviatedEffects")
            if not isinstance(direct_raw, list) or not isinstance(obviated_raw, list):
                raise MathFlowError("hierarchical credit effects must be arrays")

            prior_child = prior_children.get(child_key)
            if isinstance(prior_child, dict):
                reference_base_digest = prior_child.get("referenceBaseStateDigest")
                reference_post_digest = prior_child.get("referencePostStateDigest")
                reference_base_threads = copy.deepcopy(
                    prior_child.get("referenceBaseThreads")
                )
                reference_post_threads = copy.deepcopy(
                    prior_child.get("referencePostThreads")
                )
                if not isinstance(reference_base_threads, list) or not isinstance(
                    reference_post_threads, list
                ):
                    raise MathFlowError("prior credit child lacks reference snapshots")
            else:
                if stationary_refresh:
                    raise MathFlowError(
                        "retrospective credit refresh requires a stored historical reference for every child"
                    )
                reference_base_digest = base_program_state["stateDigest"]
                reference_post_digest = post_program_state["stateDigest"]
                reference_base_threads = _local_thread_snapshot(
                    base_program_state, program_id
                )
                reference_post_threads = _local_thread_snapshot(
                    post_program_state, program_id
                )

            direct_thread_ids = credit_child_thread_ids(
                post_program_state, program_id, str(kind), child_id
            )
            reference_base_thread_ids = {
                str(thread["id"])
                for thread in reference_base_threads
                if isinstance(thread, dict) and isinstance(thread.get("id"), str)
            }
            direct_effects: list[dict[str, object]] = []
            obviated_effects: list[dict[str, object]] = []
            direct_work = Decimal(0)
            obviated_work = Decimal(0)
            seen_threads: set[str] = set()
            for effect_value in direct_raw:
                effect, work = _effect(
                    effect_value,
                    label="direct credit effect",
                    allowed_thread_ids=set(direct_thread_ids),
                    require_reduction=False,
                )
                thread_id = str(effect["threadId"])
                if thread_id in seen_threads:
                    raise MathFlowError("credit assessment counts one thread more than once")
                seen_threads.add(thread_id)
                direct_effects.append(effect)
                direct_work += work
            if {str(effect["threadId"]) for effect in direct_effects} != set(
                direct_thread_ids
            ):
                raise MathFlowError(
                    "credit assessment must evaluate every thread on the child's direct line"
                )
            for effect_value in obviated_raw:
                effect, work = _effect(
                    effect_value,
                    label="obviated credit effect",
                    allowed_thread_ids=reference_base_thread_ids
                    - set(direct_thread_ids),
                    require_reduction=True,
                )
                thread_id = str(effect["threadId"])
                if thread_id in seen_threads:
                    raise MathFlowError("credit assessment counts one thread more than once")
                seen_threads.add(thread_id)
                obviated_effects.append(effect)
                obviated_work += work
            total_work = direct_work + obviated_work
            if total_work < 0:
                raise MathFlowError(
                    "hindsight counterfactual must not assign negative total work reduction"
                )
            prior_children[child_key] = {
                "kind": str(kind),
                "id": child_id,
                "referenceBaseStateDigest": reference_base_digest,
                "referencePostStateDigest": reference_post_digest,
                "referenceBaseThreads": reference_base_threads,
                "referencePostThreads": reference_post_threads,
                "horizonStateDigest": horizon_program_state["stateDigest"],
                "horizonLedgerHead": horizon_program_state["ledgerHead"],
                "counterfactual": counterfactual,
                "directEffects": direct_effects,
                "obviatedEffects": obviated_effects,
                "directWork": _decimal_text(direct_work),
                "obviatedWork": _decimal_text(obviated_work),
                "totalWork": _decimal_text(total_work),
                "confidence": raw_child["confidence"],
                "evidenceRefs": evidence_refs,
            }

        if sorted(observed_targets, key=lambda item: (item["kind"], item["id"])) != target_children:
            raise MathFlowError(
                f"hierarchical credit evaluation must assess the changed local child: {program_id}"
            )
        expected_children = credit_children(post_program_state, program_id)
        if sorted(
            ({"kind": kind, "id": child_id} for kind, child_id in prior_children),
            key=lambda item: (item["kind"], item["id"]),
        ) != expected_children:
            raise MathFlowError(
                f"hierarchical credit state lacks a score for a local child: {program_id}"
            )
        normalized_children = [
            prior_children[(child["kind"], child["id"])]
            for child in expected_children
        ]
        scores = [
            _decimal(child["totalWork"], "hierarchical credit child totalWork")
            for child in normalized_children
        ]
        unattributed = _decimal(
            raw_evaluation.get("unattributedWork"), "unattributed work"
        )
        denominator = sum(scores, Decimal(0)) + unattributed
        if denominator <= 0:
            raise MathFlowError("hierarchical credit allocation denominator must be positive")
        for child, score in zip(normalized_children, scores, strict=True):
            child["allocationShare"] = _fraction(score, denominator)
        evaluation = {
            "programId": program_id,
            "unattributedWork": _decimal_text(unattributed),
            "unattributedShare": _fraction(unattributed, denominator),
            "unattributedHorizonStateDigest": horizon_program_state["stateDigest"],
            "rationale": _require_text(
                raw_evaluation.get("rationale"), "credit program rationale"
            ),
            "children": normalized_children,
        }
        existing_evaluations[program_id] = {
            **evaluation,
            "digest": f"sha256:{sha256_json(evaluation)}",
        }

    state_core = {
        "schemaVersion": 1,
        "problemId": post_program_state["problemId"],
        "programStateDigest": post_program_state["stateDigest"],
        "horizonStateDigest": horizon_program_state["stateDigest"],
        "baseCreditStateDigest": base_credit_digest,
        "evaluations": existing_evaluations,
    }
    allocations, residuals = derive_hierarchical_allocations(
        post_program_state, existing_evaluations
    )
    return validate_hierarchical_credit_state(
        _with_state_digest(
            {
                **state_core,
                "allocations": allocations,
                "residualAllocations": residuals,
            }
        ),
        str(post_program_state["problemId"]),
    )


def derive_hierarchical_allocations(
    program_state: dict[str, object], evaluations: dict[str, object]
) -> tuple[dict[str, dict[str, str]], dict[str, dict[str, str]]]:
    validate_research_program_state(program_state)
    allocations: dict[str, dict[str, str]] = {}
    residuals: dict[str, dict[str, str]] = {}

    def visit(program_id: str, pot: dict[str, str]) -> None:
        evaluation = evaluations.get(program_id)
        if not isinstance(evaluation, dict):
            residuals[program_id] = pot
            return
        residuals[program_id] = _multiply_fractions(
            pot, evaluation["unattributedShare"]
        )
        for child in evaluation["children"]:
            child_pot = _multiply_fractions(pot, child["allocationShare"])
            if child["kind"] == "program":
                visit(str(child["id"]), child_pot)
            else:
                allocations[str(child["id"])] = child_pot

    visit("root", {"numerator": "1", "denominator": "1"})
    return allocations, residuals


CREDIT_STATE_FIELDS = {
    "schemaVersion",
    "problemId",
    "programStateDigest",
    "horizonStateDigest",
    "baseCreditStateDigest",
    "evaluations",
    "allocations",
    "residualAllocations",
    "stateDigest",
}

CREDIT_EVALUATION_FIELDS = {
    "programId",
    "unattributedWork",
    "unattributedShare",
    "unattributedHorizonStateDigest",
    "rationale",
    "children",
    "digest",
}
CREDIT_CHILD_FIELDS = {
    "kind",
    "id",
    "referenceBaseStateDigest",
    "referencePostStateDigest",
    "referenceBaseThreads",
    "referencePostThreads",
    "horizonStateDigest",
    "horizonLedgerHead",
    "counterfactual",
    "directEffects",
    "obviatedEffects",
    "directWork",
    "obviatedWork",
    "totalWork",
    "confidence",
    "evidenceRefs",
    "allocationShare",
}


def _validated_fraction(value: object, label: str) -> tuple[Decimal, Decimal]:
    if not isinstance(value, dict) or set(value) != {"numerator", "denominator"}:
        raise MathFlowError(f"hierarchical credit {label} fraction is invalid")
    numerator = _decimal(value["numerator"], f"{label} numerator")
    denominator = _decimal(value["denominator"], f"{label} denominator")
    if denominator <= 0 or numerator > denominator:
        raise MathFlowError(f"hierarchical credit {label} fraction is invalid")
    return numerator, denominator


def validate_hierarchical_credit_state(
    value: object, problem: str | None = None
) -> dict[str, object]:
    if not isinstance(value, dict) or set(value) != CREDIT_STATE_FIELDS:
        raise MathFlowError("hierarchical credit state has an invalid envelope")
    if value.get("schemaVersion") != 1:
        raise MathFlowError("hierarchical credit state has an unsupported version")
    if problem is not None and value.get("problemId") != problem:
        raise MathFlowError("hierarchical credit state belongs to another problem")
    _require_identifier(value.get("problemId"), "hierarchical credit problem ID")
    for field in ("programStateDigest", "horizonStateDigest"):
        raw = value.get(field)
        if not isinstance(raw, str) or not DIGEST.fullmatch(raw):
            raise MathFlowError(f"hierarchical credit state has invalid {field}")
    base = value.get("baseCreditStateDigest")
    if base is not None and (not isinstance(base, str) or not DIGEST.fullmatch(base)):
        raise MathFlowError("hierarchical credit state has invalid base digest")
    evaluations = value.get("evaluations")
    allocations = value.get("allocations")
    residuals = value.get("residualAllocations")
    if any(not isinstance(item, dict) for item in (evaluations, allocations, residuals)):
        raise MathFlowError("hierarchical credit state collections must be objects")
    assert isinstance(evaluations, dict)
    for program_id, evaluation in evaluations.items():
        _require_identifier(program_id, "credit evaluation program ID")
        if (
            not isinstance(evaluation, dict)
            or set(evaluation) != CREDIT_EVALUATION_FIELDS
            or evaluation.get("programId") != program_id
        ):
            raise MathFlowError("hierarchical credit evaluation is invalid")
        unattributed = _decimal(
            evaluation.get("unattributedWork"), "credit unattributedWork"
        )
        horizon_digest = evaluation.get("unattributedHorizonStateDigest")
        if not isinstance(horizon_digest, str) or not DIGEST.fullmatch(horizon_digest):
            raise MathFlowError("hierarchical credit evaluation has invalid horizon")
        _require_text(evaluation.get("rationale"), "credit evaluation rationale")
        children = evaluation.get("children")
        if not isinstance(children, list):
            raise MathFlowError("hierarchical credit evaluation children are invalid")
        child_scores: list[Decimal] = []
        observed_children: set[tuple[str, str]] = set()
        for child in children:
            if not isinstance(child, dict) or set(child) != CREDIT_CHILD_FIELDS:
                raise MathFlowError("hierarchical credit child is invalid")
            kind = child.get("kind")
            child_id = child.get("id")
            if kind not in {"program", "contribution"} or not isinstance(
                child_id, str
            ):
                raise MathFlowError("hierarchical credit child reference is invalid")
            child_key = (str(kind), child_id)
            if child_key in observed_children:
                raise MathFlowError("hierarchical credit evaluation repeats a child")
            observed_children.add(child_key)
            for field in (
                "referenceBaseStateDigest",
                "referencePostStateDigest",
                "horizonStateDigest",
            ):
                raw_digest = child.get(field)
                if not isinstance(raw_digest, str) or not DIGEST.fullmatch(raw_digest):
                    raise MathFlowError("hierarchical credit child has invalid state binding")
            ledger_head = child.get("horizonLedgerHead")
            if not isinstance(ledger_head, str) or not GIT_SHA.fullmatch(ledger_head):
                raise MathFlowError("hierarchical credit child has invalid horizon head")
            _require_text(child.get("counterfactual"), "credit child counterfactual")
            if child.get("confidence") not in CONFIDENCE_LEVELS:
                raise MathFlowError("hierarchical credit child confidence is invalid")
            _require_strings(child.get("evidenceRefs"), "credit child evidenceRefs")
            for snapshot_field in ("referenceBaseThreads", "referencePostThreads"):
                snapshots = child.get(snapshot_field)
                if not isinstance(snapshots, list):
                    raise MathFlowError("hierarchical credit reference snapshot is invalid")
                snapshot_ids: set[str] = set()
                for snapshot in snapshots:
                    expected_snapshot_fields = {
                        "id",
                        "title",
                        "summary",
                        "kind",
                        "status",
                        "expectedExposure",
                        "conditions",
                        "digest",
                    }
                    if not isinstance(snapshot, dict) or set(snapshot) != expected_snapshot_fields:
                        raise MathFlowError("hierarchical credit thread snapshot is invalid")
                    snapshot_id = _require_identifier(
                        snapshot.get("id"), "credit thread snapshot ID"
                    )
                    if snapshot_id in snapshot_ids:
                        raise MathFlowError("hierarchical credit thread snapshot repeats an ID")
                    snapshot_ids.add(snapshot_id)
                    _require_text(snapshot.get("title"), "credit thread snapshot title")
                    _require_text(snapshot.get("summary"), "credit thread snapshot summary")
                    _decimal(
                        snapshot.get("expectedExposure"),
                        "credit thread snapshot expectedExposure",
                    )
                    _require_strings(
                        snapshot.get("conditions"), "credit thread snapshot conditions"
                    )
                    snapshot_digest = snapshot.get("digest")
                    if not isinstance(snapshot_digest, str) or not DIGEST.fullmatch(
                        snapshot_digest
                    ):
                        raise MathFlowError("hierarchical credit thread snapshot digest is invalid")
            direct_effects = child.get("directEffects")
            obviated_effects = child.get("obviatedEffects")
            if not isinstance(direct_effects, list) or not isinstance(
                obviated_effects, list
            ):
                raise MathFlowError("hierarchical credit child effects are invalid")
            seen_effect_threads: set[str] = set()
            computed_direct = Decimal(0)
            computed_obviated = Decimal(0)
            for effect_group, label, require_reduction in (
                (direct_effects, "direct", False),
                (obviated_effects, "obviated", True),
            ):
                for effect in effect_group:
                    if not isinstance(effect, dict) or set(effect) != {
                        "threadId",
                        "withoutWork",
                        "withWork",
                        "rationale",
                    }:
                        raise MathFlowError("hierarchical credit effect is invalid")
                    thread_id = _require_identifier(
                        effect.get("threadId"), "credit effect thread ID"
                    )
                    if thread_id in seen_effect_threads:
                        raise MathFlowError("hierarchical credit counts one thread twice")
                    seen_effect_threads.add(thread_id)
                    without_work = _decimal(
                        effect.get("withoutWork"), "credit effect withoutWork"
                    )
                    with_work = _decimal(
                        effect.get("withWork"), "credit effect withWork"
                    )
                    if require_reduction and with_work > without_work:
                        raise MathFlowError("hierarchical obviated work increases exposure")
                    _require_text(effect.get("rationale"), "credit effect rationale")
                    if label == "direct":
                        computed_direct += without_work - with_work
                    else:
                        computed_obviated += without_work - with_work
            direct_work = _decimal(
                child.get("directWork"), "credit child directWork", nonnegative=False
            )
            obviated_work = _decimal(
                child.get("obviatedWork"), "credit child obviatedWork"
            )
            total_work = _decimal(child.get("totalWork"), "credit child totalWork")
            if (
                direct_work != computed_direct
                or obviated_work != computed_obviated
                or total_work != direct_work + obviated_work
            ):
                raise MathFlowError("hierarchical credit child work does not conserve")
            child_scores.append(total_work)
        denominator = sum(child_scores, Decimal(0)) + unattributed
        if denominator <= 0:
            raise MathFlowError("hierarchical credit allocation denominator must be positive")
        unattributed_numerator, unattributed_denominator = _validated_fraction(
            evaluation.get("unattributedShare"), "unattributed"
        )
        unattributed_ratio = Fraction(unattributed_numerator) / Fraction(
            unattributed_denominator
        )
        if unattributed_ratio != Fraction(unattributed) / Fraction(denominator):
            raise MathFlowError("hierarchical credit unattributed share is inconsistent")
        allocated_share = unattributed_ratio
        for child, score in zip(children, child_scores, strict=True):
            numerator, share_denominator = _validated_fraction(
                child.get("allocationShare"), "child allocation"
            )
            child_ratio = Fraction(numerator) / Fraction(share_denominator)
            if child_ratio != Fraction(score) / Fraction(denominator):
                raise MathFlowError("hierarchical credit child share is inconsistent")
            allocated_share += child_ratio
        if allocated_share != 1:
            raise MathFlowError("hierarchical credit local shares do not conserve")
        digest = evaluation.get("digest")
        core = {key: item for key, item in evaluation.items() if key != "digest"}
        if not isinstance(digest, str) or digest != f"sha256:{sha256_json(core)}":
            raise MathFlowError("hierarchical credit evaluation digest mismatch")
    for collection, label in ((allocations, "allocation"), (residuals, "residual")):
        assert isinstance(collection, dict)
        for key, fraction in collection.items():
            if not isinstance(key, str):
                raise MathFlowError(f"hierarchical credit {label} is invalid")
            _validated_fraction(fraction, label)
    if value.get("stateDigest") != _with_state_digest(value)["stateDigest"]:
        raise MathFlowError("hierarchical credit state digest mismatch")
    return value


def validate_credit_against_program_state(
    program_state: dict[str, object], credit_state: dict[str, object]
) -> dict[str, object]:
    validate_research_program_state(program_state)
    validate_hierarchical_credit_state(
        credit_state, str(program_state["problemId"])
    )
    if credit_state.get("programStateDigest") != program_state.get("stateDigest"):
        raise MathFlowError("hierarchical credit does not describe the program state")
    expected_programs = {
        program_id
        for program_id in program_state["programs"]
        if credit_children(program_state, str(program_id))
    }
    evaluations = credit_state["evaluations"]
    if set(evaluations) != expected_programs:
        raise MathFlowError("hierarchical credit does not cover every credit-bearing program")
    for program_id, evaluation in evaluations.items():
        expected_children = credit_children(program_state, str(program_id))
        observed_children = [
            {"kind": str(child["kind"]), "id": str(child["id"])}
            for child in evaluation["children"]
        ]
        if observed_children != expected_children:
            raise MathFlowError("hierarchical credit children do not match program state")
        for child in evaluation["children"]:
            direct_thread_ids = set(
                credit_child_thread_ids(
                    program_state,
                    str(program_id),
                    str(child["kind"]),
                    str(child["id"]),
                )
            )
            observed_direct = {
                str(effect["threadId"]) for effect in child["directEffects"]
            }
            if observed_direct != direct_thread_ids:
                raise MathFlowError("hierarchical credit direct line does not match state")
            reference_threads = {
                str(thread["id"]) for thread in child["referenceBaseThreads"]
            }
            observed_obviated = {
                str(effect["threadId"]) for effect in child["obviatedEffects"]
            }
            if not observed_obviated <= reference_threads - direct_thread_ids:
                raise MathFlowError(
                    "hierarchical credit obviation is outside the historical local ledger"
                )
    allocations, residuals = derive_hierarchical_allocations(
        program_state, evaluations
    )
    if (
        allocations != credit_state.get("allocations")
        or residuals != credit_state.get("residualAllocations")
    ):
        raise MathFlowError("hierarchical credit global allocation is inconsistent")
    return credit_state
