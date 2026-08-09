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

REVISION_ACTIONS = {"issue", "revise", "retract", "reinstate"}
REVISION_RELATIONS = {"supports", "refutes", "qualifies", "context", "formalizes", "supersedes"}
REVISION_EVIDENCE_KINDS = {"transaction", "artifact", "verifier-attestation", "judge-run"}
V2_OPERATION_FIELDS = {
    "action",
    "adjudicationId",
    "nodeId",
    "parentId",
    "nodeType",
    "title",
    "summary",
    "reportSection",
    "baseDigest",
    "baseRevisionId",
    "subjects",
    "evidence",
}
V2_NODE_FIELDS = {
    "id",
    "parentId",
    "type",
    "title",
    "summary",
    "status",
    "reportRef",
    "contentMarkdown",
    "subjects",
    "evidence",
    "currentAdjudication",
    "digest",
}
REVISION_FIELDS = {
    "revisionId",
    "adjudicationId",
    "revisionNumber",
    "action",
    "baseRevisionId",
    "nodeId",
    "parentId",
    "nodeType",
    "title",
    "subjects",
    "evidence",
    "issuedAtLedgerHead",
    "reportRef",
    "summary",
    "status",
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


def empty_state_v2(problem: str) -> dict[str, object]:
    """Create the revision-aware example state without inventing an adjudication."""
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
            "subjects": [],
            "evidence": [],
            "currentAdjudication": None,
        }
    )
    return _with_state_digest(
        {"schemaVersion": 2, "problemId": problem, "rootId": "root", "nodes": {"root": root}}
    )


def _revision_id(revision: dict[str, object]) -> str:
    content = {key: copy.deepcopy(value) for key, value in revision.items() if key != "revisionId"}
    return f"sha256:{sha256_json(content)}"


def validate_revisions(revisions: object, problem: str | None = None) -> list[dict[str, object]]:
    if not isinstance(revisions, list):
        raise MathFlowError("invalid adjudication revision history")
    latest: dict[str, dict[str, object]] = {}
    revision_ids: set[str] = set()
    for raw in revisions:
        if not isinstance(raw, dict) or set(raw) != REVISION_FIELDS:
            raise MathFlowError("invalid adjudication revision record")
        revision = raw
        revision_id = revision.get("revisionId")
        if revision_id != _revision_id(revision) or revision_id in revision_ids:
            raise MathFlowError("invalid or duplicate adjudication revision ID")
        revision_ids.add(str(revision_id))
        adjudication_id = revision.get("adjudicationId")
        node_id = revision.get("nodeId")
        if (
            not isinstance(adjudication_id, str)
            or adjudication_id != node_id
            or not NODE_ID.fullmatch(adjudication_id)
        ):
            raise MathFlowError("adjudication ID must equal its stable knowledge node ID")
        prior = latest.get(adjudication_id)
        expected_number = 1 if prior is None else int(prior["revisionNumber"]) + 1
        expected_base = None if prior is None else prior["revisionId"]
        if (
            not isinstance(revision.get("revisionNumber"), int)
            or isinstance(revision.get("revisionNumber"), bool)
            or revision.get("revisionNumber") != expected_number
            or revision.get("baseRevisionId") != expected_base
        ):
            raise MathFlowError(f"broken adjudication revision chain: {adjudication_id}")
        action = revision.get("action")
        if action not in REVISION_ACTIONS:
            raise MathFlowError(f"invalid adjudication revision action: {action}")
        if prior is None and action != "issue":
            raise MathFlowError(f"first adjudication revision must issue: {adjudication_id}")
        if prior is not None:
            prior_status = prior["status"]
            if action == "issue":
                raise MathFlowError(f"adjudication may only be issued once: {adjudication_id}")
            if action in {"revise", "retract"} and prior_status != "active":
                raise MathFlowError(f"cannot {action} inactive adjudication: {adjudication_id}")
            if action == "reinstate" and prior_status != "retired":
                raise MathFlowError(f"cannot reinstate active adjudication: {adjudication_id}")
        expected_status = "retired" if action == "retract" else "active"
        if revision.get("status") != expected_status:
            raise MathFlowError(f"adjudication revision has inconsistent status: {adjudication_id}")
        if not isinstance(revision.get("issuedAtLedgerHead"), str) or not revision["issuedAtLedgerHead"]:
            raise MathFlowError("adjudication revision is missing its issuance ledger head")
        subjects = revision.get("subjects")
        if not isinstance(subjects, list) or any(
            not isinstance(item, dict)
            or set(item) != {"kind", "id", "ledgerPosition"}
            or item.get("kind") != "transaction"
            or not isinstance(item.get("id"), str)
            or not isinstance(item.get("ledgerPosition"), int)
            or isinstance(item.get("ledgerPosition"), bool)
            or int(item["ledgerPosition"]) < 1
            for item in subjects
        ):
            raise MathFlowError("invalid adjudication revision subjects")
        if len({str(item["id"]) for item in subjects}) != len(subjects):
            raise MathFlowError("adjudication revision subjects must not contain duplicates")
        evidence = revision.get("evidence")
        if not isinstance(evidence, list):
            raise MathFlowError("invalid adjudication revision evidence")
        for item in evidence:
            if (
                not isinstance(item, dict)
                or set(item) != {"kind", "id", "digest", "relation"}
                or item.get("kind") not in REVISION_EVIDENCE_KINDS
                or item.get("relation") not in REVISION_RELATIONS
                or not isinstance(item.get("id"), str)
                or not item["id"]
            ):
                raise MathFlowError("invalid adjudication revision evidence")
            digest = item.get("digest")
            if item["kind"] == "transaction" and digest is not None:
                raise MathFlowError("transaction evidence must use its commit ID, not a second digest")
            if item["kind"] != "transaction" and not (
                isinstance(digest, str) and re.fullmatch(r"sha256:[0-9a-f]{64}", digest)
            ):
                raise MathFlowError("content-addressed evidence must have a SHA-256 digest")
        report_ref = revision.get("reportRef")
        if (
            not isinstance(report_ref, dict)
            or set(report_ref) != {"artifact", "digest", "section"}
            or report_ref.get("artifact") != "report.md"
            or not isinstance(report_ref.get("digest"), str)
            or not re.fullmatch(r"sha256:[0-9a-f]{64}", str(report_ref["digest"]))
            or not isinstance(report_ref.get("section"), str)
            or not report_ref["section"]
        ):
            raise MathFlowError("invalid adjudication revision report reference")
        if not isinstance(revision.get("summary"), str) or not revision["summary"].strip():
            raise MathFlowError("adjudication revision summary must be non-empty")
        parent_id = revision.get("parentId")
        if parent_id is not None and (
            not isinstance(parent_id, str) or not NODE_ID.fullmatch(parent_id)
        ):
            raise MathFlowError("invalid adjudication revision parent")
        if revision.get("nodeType") not in NODE_TYPES:
            raise MathFlowError("invalid adjudication revision node type")
        if not isinstance(revision.get("title"), str) or not revision["title"].strip():
            raise MathFlowError("adjudication revision title must be non-empty")
        latest[adjudication_id] = revision
    return revisions


def validate_state_v2(
    state: object,
    revisions: object,
    problem: str | None = None,
) -> tuple[dict[str, object], list[dict[str, object]]]:
    history = validate_revisions(revisions, problem)
    if not isinstance(state, dict) or state.get("schemaVersion") != 2:
        raise MathFlowError("invalid revision-aware hierarchical knowledge state")
    if problem is not None and state.get("problemId") != problem:
        raise MathFlowError("base knowledge state belongs to a different problem")
    nodes = state.get("nodes")
    if not isinstance(nodes, dict) or "root" not in nodes:
        raise MathFlowError("hierarchical knowledge state is missing its root node")
    if state.get("stateDigest") != _with_state_digest(state)["stateDigest"]:
        raise MathFlowError("hierarchical knowledge state digest mismatch")
    latest = {str(item["adjudicationId"]): item for item in history}
    seen_adjudications: set[str] = set()
    for node_id, node in nodes.items():
        if not isinstance(node, dict) or set(node) != V2_NODE_FIELDS or node.get("id") != node_id:
            raise MathFlowError(f"invalid revision-aware knowledge node: {node_id}")
        if node.get("type") not in NODE_TYPES or node.get("status") not in {"active", "retired"}:
            raise MathFlowError(f"invalid knowledge node type or status: {node_id}")
        if not isinstance(node.get("contentMarkdown"), str):
            raise MathFlowError(f"knowledge node content must be Markdown text: {node_id}")
        if node.get("digest") != _with_node_digest(node)["digest"]:
            raise MathFlowError(f"knowledge node digest mismatch: {node_id}")
        current = node.get("currentAdjudication")
        if current is None:
            if node_id != "root":
                raise MathFlowError(f"knowledge node has no adjudication: {node_id}")
            continue
        if not isinstance(current, dict) or set(current) != {
            "adjudicationId", "revisionId", "revisionNumber"
        }:
            raise MathFlowError(f"invalid current adjudication pointer: {node_id}")
        adjudication_id = current.get("adjudicationId")
        if adjudication_id != node_id or adjudication_id in seen_adjudications:
            raise MathFlowError(f"invalid or duplicate adjudication identity: {node_id}")
        seen_adjudications.add(str(adjudication_id))
        revision = latest.get(str(adjudication_id))
        if revision is None or current.get("revisionId") != revision["revisionId"] or current.get(
            "revisionNumber"
        ) != revision["revisionNumber"]:
            raise MathFlowError(f"knowledge node does not point to its latest revision: {node_id}")
        if node.get("status") != revision["status"]:
            raise MathFlowError(f"knowledge node status disagrees with its revision: {node_id}")
        for field in ("subjects", "evidence", "reportRef", "summary"):
            if node.get(field) != revision[field]:
                raise MathFlowError(
                    f"knowledge node {field} disagrees with its current revision: {node_id}"
                )
        if (
            node.get("parentId") != revision["parentId"]
            or node.get("type") != revision["nodeType"]
            or node.get("title") != revision["title"]
        ):
            raise MathFlowError(
                f"knowledge node structure disagrees with its current revision: {node_id}"
            )
    if set(latest) != seen_adjudications:
        raise MathFlowError("revision history contains an adjudication without a knowledge node")
    return state, history


def state_index_v2(state: dict[str, object], revisions: list[dict[str, object]]) -> list[dict[str, object]]:
    validate_state_v2(state, revisions)
    return [
        {
            "id": node["id"],
            "parentId": node["parentId"],
            "type": node["type"],
            "title": node["title"],
            "summary": node["summary"],
            "status": node["status"],
            "currentAdjudication": node["currentAdjudication"],
            "digest": node["digest"],
        }
        for _, node in sorted(state["nodes"].items())
    ]


def selected_nodes_v2(
    state: dict[str, object], revisions: list[dict[str, object]], node_ids: list[str]
) -> list[dict[str, object]]:
    validate_state_v2(state, revisions)
    nodes = state["nodes"]
    missing = [node_id for node_id in node_ids if node_id not in nodes]
    if missing:
        raise MathFlowError(f"judge selected an unknown knowledge node: {missing[0]}")
    return [copy.deepcopy(nodes[node_id]) for node_id in node_ids]


def _validate_v2_operation(operation: object) -> dict[str, object]:
    if not isinstance(operation, dict) or set(operation) != V2_OPERATION_FIELDS:
        raise MathFlowError("hierarchical judge returned an invalid revision operation")
    if operation["action"] not in REVISION_ACTIONS:
        raise MathFlowError(f"invalid adjudication revision action: {operation['action']}")
    node_id = operation["nodeId"]
    if not isinstance(node_id, str) or not NODE_ID.fullmatch(node_id):
        raise MathFlowError(f"invalid knowledge node id: {node_id}")
    if operation["adjudicationId"] != node_id:
        raise MathFlowError("adjudication ID must equal its stable knowledge node ID")
    if operation["nodeType"] not in NODE_TYPES:
        raise MathFlowError(f"invalid knowledge node type: {operation['nodeType']}")
    for field in ("title", "summary", "reportSection"):
        if not isinstance(operation[field], str) or not operation[field].strip():
            raise MathFlowError(f"knowledge delta {field} must be non-empty")
    parent_id = operation["parentId"]
    if parent_id is not None and (not isinstance(parent_id, str) or not NODE_ID.fullmatch(parent_id)):
        raise MathFlowError(f"invalid parent knowledge node id: {parent_id}")
    for field in ("baseDigest", "baseRevisionId"):
        value = operation[field]
        if value is not None and not (
            isinstance(value, str) and re.fullmatch(r"sha256:[0-9a-f]{64}", value)
        ):
            raise MathFlowError(f"knowledge delta {field} must be null or a SHA-256 digest")
    subjects = operation["subjects"]
    if not isinstance(subjects, list) or any(
        not isinstance(item, dict) or set(item) != {"kind", "id"} or item.get("kind") != "transaction"
        or not isinstance(item.get("id"), str)
        for item in subjects
    ):
        raise MathFlowError("adjudication subjects must be transaction references")
    if len({str(item["id"]) for item in subjects}) != len(subjects):
        raise MathFlowError("adjudication subjects must not contain duplicates")
    evidence = operation["evidence"]
    if not isinstance(evidence, list):
        raise MathFlowError("adjudication evidence must be an array")
    for item in evidence:
        if not isinstance(item, dict) or set(item) != {"kind", "id", "digest", "relation"}:
            raise MathFlowError("invalid adjudication evidence reference")
        if item.get("kind") not in REVISION_EVIDENCE_KINDS or item.get("relation") not in REVISION_RELATIONS:
            raise MathFlowError("invalid adjudication evidence kind or relation")
        if not isinstance(item.get("id"), str) or not item["id"]:
            raise MathFlowError("adjudication evidence ID must be non-empty")
        digest = item.get("digest")
        if digest is not None and not (
            isinstance(digest, str) and re.fullmatch(r"sha256:[0-9a-f]{64}", digest)
        ):
            raise MathFlowError("adjudication evidence digest must be null or a SHA-256 digest")
        if item["kind"] != "transaction" and digest is None:
            raise MathFlowError("non-transaction evidence must have a content digest")
        if item["kind"] == "transaction" and digest is not None:
            raise MathFlowError("transaction evidence must use its commit ID, not a second digest")
    return operation


def apply_revision_deltas(
    state: dict[str, object],
    revisions: list[dict[str, object]],
    selected_node_ids: list[str],
    operations: list[object],
    report_digest: str,
    report_markdown: str,
    issued_at_ledger_head: str,
    transaction_positions: dict[str, int],
) -> tuple[dict[str, object], list[dict[str, object]]]:
    validate_state_v2(state, revisions)
    if len(selected_node_ids) != len(set(selected_node_ids)):
        raise MathFlowError("hierarchical judge selected duplicate knowledge nodes")
    selected_nodes_v2(state, revisions, selected_node_ids)
    result = copy.deepcopy(state)
    history = copy.deepcopy(revisions)
    nodes = result["nodes"]
    initial_node_ids = set(nodes)

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
        operation = _validate_v2_operation(raw_operation)
        node_id = str(operation["nodeId"])
        existing = nodes.get(node_id)
        current = existing.get("currentAdjudication") if existing is not None else None
        action = str(operation["action"])
        if existing is not None:
            if node_id not in selected_node_ids:
                raise MathFlowError(f"judge updated a knowledge node it did not select: {node_id}")
            if action == "issue" and current is not None:
                raise MathFlowError(f"adjudication may only be issued once: {node_id}")
            if action != "issue" and current is None:
                raise MathFlowError(f"knowledge node has no adjudication to {action}: {node_id}")
            if operation["baseDigest"] != existing["digest"]:
                raise MathFlowError(f"stale knowledge delta for node: {node_id}")
            expected_revision = None if current is None else current["revisionId"]
            if operation["baseRevisionId"] != expected_revision:
                raise MathFlowError(f"stale adjudication revision for node: {node_id}")
            if action in {"revise", "retract"} and existing["status"] != "active":
                raise MathFlowError(f"cannot {action} inactive adjudication: {node_id}")
            if action == "reinstate" and existing["status"] != "retired":
                raise MathFlowError(f"cannot reinstate active adjudication: {node_id}")
        else:
            if action != "issue":
                raise MathFlowError(f"new knowledge node must issue its adjudication: {node_id}")
            if operation["baseDigest"] is not None or operation["baseRevisionId"] is not None:
                raise MathFlowError(f"new knowledge node must have null base references: {node_id}")

        subject_ids = [str(item["id"]) for item in operation["subjects"]]
        unknown_subjects = [value for value in subject_ids if value not in transaction_positions]
        if unknown_subjects:
            raise MathFlowError(f"adjudication subject is outside the ledger: {unknown_subjects[0]}")
        subjects = [
            {"kind": "transaction", "id": value, "ledgerPosition": transaction_positions[value]}
            for value in subject_ids
        ]
        evidence = copy.deepcopy(operation["evidence"])
        for item in evidence:
            if item["kind"] == "transaction" and item["id"] not in transaction_positions:
                raise MathFlowError(f"adjudication evidence is outside the ledger: {item['id']}")

        parent_id = operation["parentId"]
        if node_id == "root":
            if operation["nodeType"] != "root":
                raise MathFlowError("the root knowledge node must keep type root")
            parent_id = None
            if action == "retract":
                raise MathFlowError("cannot retract the root knowledge node")
        elif parent_id not in nodes:
            raise MathFlowError(
                f"knowledge node parent must be created first: {parent_id!r} for {node_id}"
            )
        elif (
            existing is None
            and parent_id in initial_node_ids
            and parent_id not in selected_node_ids
        ):
            raise MathFlowError(
                f"new knowledge node parent was not selected: {parent_id!r} for {node_id}"
            )
        status = "retired" if action == "retract" else "active"
        section_ref = {
            "artifact": "report.md",
            "digest": report_digest,
            "section": operation["reportSection"],
        }
        revision_number = 1 if current is None else int(current["revisionNumber"]) + 1
        revision = {
            "adjudicationId": operation["adjudicationId"],
            "revisionNumber": revision_number,
            "action": action,
            "baseRevisionId": None if current is None else current["revisionId"],
            "nodeId": node_id,
            "parentId": parent_id,
            "nodeType": operation["nodeType"],
            "title": operation["title"],
            "subjects": subjects,
            "evidence": evidence,
            "issuedAtLedgerHead": issued_at_ledger_head,
            "reportRef": section_ref,
            "summary": operation["summary"],
            "status": status,
        }
        revision["revisionId"] = _revision_id(revision)
        history.append(revision)
        updated = {
            "id": node_id,
            "parentId": parent_id,
            "type": operation["nodeType"],
            "title": operation["title"],
            "summary": operation["summary"],
            "status": status,
            "reportRef": section_ref,
            "contentMarkdown": report_section(str(operation["reportSection"])),
            "subjects": subjects,
            "evidence": evidence,
            "currentAdjudication": {
                "adjudicationId": operation["adjudicationId"],
                "revisionId": revision["revisionId"],
                "revisionNumber": revision_number,
            },
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
    next_state = _with_state_digest(result)
    validate_state_v2(next_state, history)
    return next_state, history
