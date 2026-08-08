from __future__ import annotations

import copy
import re

from .errors import MathFlowError
from .repository import sha256_json


NODE_ID = re.compile(r"^[a-z0-9][a-z0-9/_-]*$")
NODE_TYPES = {"root", "program", "claim", "lemma", "question", "dispute", "method", "result"}
ACTIONS = {"upsert", "retire"}
OPERATION_FIELDS = {
    "action",
    "nodeId",
    "parentId",
    "nodeType",
    "title",
    "summary",
    "reportSection",
    "baseDigest",
    "transactionIds",
}
NODE_FIELDS = {
    "id",
    "parentId",
    "type",
    "title",
    "summary",
    "status",
    "reportRef",
    "contentMarkdown",
    "transactionIds",
    "digest",
}


def _with_node_digest(node: dict[str, object]) -> dict[str, object]:
    value = {key: copy.deepcopy(item) for key, item in node.items() if key != "digest"}
    value["digest"] = f"sha256:{sha256_json(value)}"
    return value


def _with_state_digest(state: dict[str, object]) -> dict[str, object]:
    value = {key: copy.deepcopy(item) for key, item in state.items() if key != "stateDigest"}
    value["stateDigest"] = f"sha256:{sha256_json(value)}"
    return value


def empty_state(problem: str) -> dict[str, object]:
    root = _with_node_digest(
        {
            "id": "root",
            "parentId": None,
            "type": "root",
            "title": f"Research state for {problem}",
            "summary": "No judge-authored research programs have been established yet.",
            "status": "active",
            "reportRef": None,
            "contentMarkdown": "No judge-authored research programs have been established yet.",
            "transactionIds": [],
        }
    )
    return _with_state_digest(
        {"schemaVersion": 1, "problemId": problem, "rootId": "root", "nodes": {"root": root}}
    )


def validate_state(state: object, problem: str | None = None) -> dict[str, object]:
    if not isinstance(state, dict) or state.get("schemaVersion") != 1:
        raise MathFlowError("invalid hierarchical knowledge state")
    if problem is not None and state.get("problemId") != problem:
        raise MathFlowError("base knowledge state belongs to a different problem")
    nodes = state.get("nodes")
    if not isinstance(nodes, dict) or "root" not in nodes:
        raise MathFlowError("hierarchical knowledge state is missing its root node")
    expected_state_digest = _with_state_digest(state)["stateDigest"]
    if state.get("stateDigest") != expected_state_digest:
        raise MathFlowError("hierarchical knowledge state digest mismatch")
    for node_id, node in nodes.items():
        if not isinstance(node, dict) or set(node) != NODE_FIELDS or node.get("id") != node_id:
            raise MathFlowError(f"invalid knowledge node: {node_id}")
        if node.get("type") not in NODE_TYPES or node.get("status") not in {"active", "retired"}:
            raise MathFlowError(f"invalid knowledge node type or status: {node_id}")
        if not isinstance(node.get("contentMarkdown"), str):
            raise MathFlowError(f"knowledge node content must be Markdown text: {node_id}")
        if node.get("digest") != _with_node_digest(node)["digest"]:
            raise MathFlowError(f"knowledge node digest mismatch: {node_id}")
    return state


def state_index(state: dict[str, object]) -> list[dict[str, object]]:
    validate_state(state)
    return [
        {
            "id": node["id"],
            "parentId": node["parentId"],
            "type": node["type"],
            "title": node["title"],
            "summary": node["summary"],
            "status": node["status"],
            "digest": node["digest"],
        }
        for _, node in sorted(state["nodes"].items())
    ]


def selected_nodes(state: dict[str, object], node_ids: list[str]) -> list[dict[str, object]]:
    validate_state(state)
    nodes = state["nodes"]
    missing = [node_id for node_id in node_ids if node_id not in nodes]
    if missing:
        raise MathFlowError(f"judge selected an unknown knowledge node: {missing[0]}")
    return [copy.deepcopy(nodes[node_id]) for node_id in node_ids]


def _validate_operation(operation: object) -> dict[str, object]:
    if not isinstance(operation, dict) or set(operation) != OPERATION_FIELDS:
        raise MathFlowError("hierarchical judge returned an invalid delta operation")
    if operation["action"] not in ACTIONS:
        raise MathFlowError(f"invalid knowledge delta action: {operation['action']}")
    node_id = operation["nodeId"]
    if not isinstance(node_id, str) or not NODE_ID.fullmatch(node_id):
        raise MathFlowError(f"invalid knowledge node id: {node_id}")
    if operation["nodeType"] not in NODE_TYPES:
        raise MathFlowError(f"invalid knowledge node type: {operation['nodeType']}")
    for field in ("title", "summary", "reportSection"):
        if not isinstance(operation[field], str) or not operation[field].strip():
            raise MathFlowError(f"knowledge delta {field} must be non-empty")
    parent_id = operation["parentId"]
    if parent_id is not None and (not isinstance(parent_id, str) or not NODE_ID.fullmatch(parent_id)):
        raise MathFlowError(f"invalid parent knowledge node id: {parent_id}")
    base_digest = operation["baseDigest"]
    if base_digest is not None and not (
        isinstance(base_digest, str) and re.fullmatch(r"sha256:[0-9a-f]{64}", base_digest)
    ):
        raise MathFlowError("knowledge delta baseDigest must be null or a SHA-256 digest")
    transaction_ids = operation["transactionIds"]
    if not isinstance(transaction_ids, list) or any(not isinstance(value, str) for value in transaction_ids):
        raise MathFlowError("knowledge delta transactionIds must be a string array")
    if len(transaction_ids) != len(set(transaction_ids)):
        raise MathFlowError("knowledge delta transactionIds must not contain duplicates")
    return operation


def apply_deltas(
    state: dict[str, object],
    selected_node_ids: list[str],
    operations: list[object],
    report_digest: str,
    report_markdown: str,
) -> dict[str, object]:
    validate_state(state)
    if len(selected_node_ids) != len(set(selected_node_ids)):
        raise MathFlowError("hierarchical judge selected duplicate knowledge nodes")
    selected_nodes(state, selected_node_ids)
    result = copy.deepcopy(state)
    nodes = result["nodes"]

    def report_section(heading: str) -> str:
        lines = report_markdown.splitlines()
        try:
            start = next(index for index, line in enumerate(lines) if line.strip() == heading)
        except StopIteration as exc:
            raise MathFlowError(f"knowledge delta references a missing report heading: {heading}") from exc
        end = len(lines)
        for index in range(start + 1, len(lines)):
            if lines[index].strip().startswith("## "):
                end = index
                break
        return "\n".join(lines[start:end]).strip() + "\n"

    for raw_operation in operations:
        operation = _validate_operation(raw_operation)
        node_id = str(operation["nodeId"])
        existing = nodes.get(node_id)
        if existing is not None:
            if node_id not in selected_node_ids:
                raise MathFlowError(f"judge updated a knowledge node it did not select: {node_id}")
            if operation["baseDigest"] != existing["digest"]:
                raise MathFlowError(f"stale knowledge delta for node: {node_id}")
        elif operation["baseDigest"] is not None:
            raise MathFlowError(f"new knowledge node must have a null baseDigest: {node_id}")

        if operation["action"] == "retire":
            if existing is None:
                raise MathFlowError(f"cannot retire missing knowledge node: {node_id}")
            if node_id == "root":
                raise MathFlowError("cannot retire the root knowledge node")
            updated = {**existing, "status": "retired", "summary": operation["summary"]}
            updated["reportRef"] = {
                "artifact": "report.md",
                "digest": report_digest,
                "section": operation["reportSection"],
            }
            updated["contentMarkdown"] = report_section(str(operation["reportSection"]))
            updated["transactionIds"] = operation["transactionIds"]
            nodes[node_id] = _with_node_digest(updated)
            continue

        parent_id = operation["parentId"]
        if node_id == "root":
            if operation["nodeType"] != "root":
                raise MathFlowError("the root knowledge node must keep type root")
            parent_id = None
        elif parent_id not in nodes:
            raise MathFlowError(f"knowledge node parent must be created first: {parent_id}")
        updated = {
            "id": node_id,
            "parentId": parent_id,
            "type": operation["nodeType"],
            "title": operation["title"],
            "summary": operation["summary"],
            "status": "active",
            "reportRef": {
                "artifact": "report.md",
                "digest": report_digest,
                "section": operation["reportSection"],
            },
            "contentMarkdown": report_section(str(operation["reportSection"])),
            "transactionIds": operation["transactionIds"],
        }
        nodes[node_id] = _with_node_digest(updated)
    for node_id, node in nodes.items():
        parent_id = node["parentId"]
        visited = {node_id}
        while parent_id is not None:
            if parent_id not in nodes:
                raise MathFlowError(f"knowledge node has missing parent: {node_id}")
            if parent_id in visited:
                raise MathFlowError(f"knowledge hierarchy contains a cycle at: {node_id}")
            visited.add(parent_id)
            parent_id = nodes[parent_id]["parentId"]
    return _with_state_digest(result)
