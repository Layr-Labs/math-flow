from __future__ import annotations

import copy
import json
import re
from pathlib import Path

from .artifacts import load_manifest, read_verified_artifact, sha256_bytes
from .errors import MathFlowError
from .judges import artifact_evidence
from .knowledge import (
    apply_deltas,
    apply_revision_deltas,
    empty_state,
    empty_state_v2,
    selected_nodes,
    selected_nodes_v2,
    state_index,
    state_index_v2,
    validate_state,
    validate_state_v2,
)
from .openrouter import OpenRouterTransport, format_error_message, send_chat_completion
from .repository import is_ancestor, read_at, sha256_json


def _request(
    spec: dict[str, object],
    stage_name: str,
    messages: list[dict[str, str]],
    schema: dict[str, object] | None = None,
) -> dict[str, object]:
    stages = spec.get("stages", {})
    stage = stages.get(stage_name, {}) if isinstance(stages, dict) else {}
    model = stage.get("model", spec["model"])
    parameters = {**spec["parameters"], **stage.get("parameters", {})}
    payload: dict[str, object] = {
        "model": model,
        "messages": messages,
        "provider": spec["provider"],
    }
    for key, value in parameters.items():
        if key not in {"temperature", "top_p", "max_tokens", "seed", "reasoning"}:
            raise MathFlowError(f"unsupported OpenRouter judge parameter: {key}")
        if key == "reasoning" and (
            not isinstance(value, dict)
            or set(value) != {"effort"}
            or value.get("effort")
            not in {"none", "minimal", "low", "medium", "high", "xhigh", "max"}
        ):
            raise MathFlowError("OpenRouter reasoning must specify one supported effort")
        payload[key] = value
    if schema is not None:
        payload["response_format"] = {
            "type": "json_schema",
            "json_schema": {
                "name": "math_flow_hierarchical_control",
                "strict": True,
                "schema": schema,
            },
        }
    return payload


def _assistant_content(response: dict[str, object]) -> str:
    if "error" in response:
        raise MathFlowError(f"OpenRouter returned an error: {format_error_message(response['error'])[:500]}")
    try:
        content = response["choices"][0]["message"]["content"]
    except (KeyError, IndexError, TypeError) as exc:
        raise MathFlowError("OpenRouter returned no assistant message") from exc
    if not isinstance(content, str) or not content.strip():
        raise MathFlowError("OpenRouter returned an empty assistant message")
    return content


def _structured_content(
    response: dict[str, object], stage: str | None = None
) -> dict[str, object]:
    content = _assistant_content(response)
    candidate = content.strip()
    fenced = re.fullmatch(
        r"```(?:json)?\s*\n?(.*?)\n?```", candidate, flags=re.DOTALL | re.IGNORECASE
    )
    if fenced is not None:
        candidate = fenced.group(1).strip()
    try:
        value = json.loads(candidate)
    except json.JSONDecodeError as exc:
        finish_reason: object = None
        try:
            finish_reason = response["choices"][0].get("finish_reason")
        except (KeyError, IndexError, TypeError, AttributeError):
            pass
        detail = (
            (f"stage={stage}, " if stage else "")
            + f"finish_reason={finish_reason or 'unknown'}, "
            f"content_chars={len(content)}, line={exc.lineno}, column={exc.colno}"
        )
        raise MathFlowError(
            f"OpenRouter control response was not valid JSON ({detail})"
        ) from exc
    if not isinstance(value, dict):
        raise MathFlowError("OpenRouter control response must be a JSON object")
    return value


def _provider_run(response: dict[str, object], requested_model: str, stage: str) -> dict[str, object]:
    return {
        "provider": "openrouter",
        "stage": stage,
        "requestedModel": requested_model,
        "resolvedModel": response.get("model") if isinstance(response.get("model"), str) else None,
        "responseId": response.get("id") if isinstance(response.get("id"), str) else None,
        "usage": response.get("usage") if isinstance(response.get("usage"), dict) else {},
    }


def _selector_schema(node_ids: list[str]) -> dict[str, object]:
    item_schema: dict[str, object] = {"type": "string"}
    if node_ids:
        item_schema["enum"] = node_ids
    return {
        "type": "object",
        "properties": {
            "selectedNodeIds": {"type": "array", "items": item_schema},
            "rationale": {"type": "string"},
        },
        "required": ["selectedNodeIds", "rationale"],
        "additionalProperties": False,
    }


def _delta_schema(transaction_ids: list[str]) -> dict[str, object]:
    transaction_schema: dict[str, object] = {"type": "string"}
    if transaction_ids:
        transaction_schema["enum"] = transaction_ids
    operation = {
        "type": "object",
        "properties": {
            "action": {"type": "string", "enum": ["upsert", "retire"]},
            "nodeId": {"type": "string"},
            "parentId": {"type": ["string", "null"]},
            "nodeType": {
                "type": "string",
                "enum": ["root", "program", "claim", "lemma", "question", "dispute", "method", "result"],
            },
            "title": {"type": "string"},
            "summary": {"type": "string"},
            "reportSection": {"type": "string"},
            "baseDigest": {"type": ["string", "null"]},
            "transactionIds": {"type": "array", "items": transaction_schema},
        },
        "required": [
            "action",
            "nodeId",
            "parentId",
            "nodeType",
            "title",
            "summary",
            "reportSection",
            "baseDigest",
            "transactionIds",
        ],
        "additionalProperties": False,
    }
    return {
        "type": "object",
        "properties": {"operations": {"type": "array", "items": operation}},
        "required": ["operations"],
        "additionalProperties": False,
    }


def _revision_delta_schema(
    transaction_ids: list[str],
    evidence_kinds: list[str] | None = None,
    evidence_ids: list[str] | None = None,
    evidence_digests: list[str | None] | None = None,
) -> dict[str, object]:
    transaction_schema: dict[str, object] = {"type": "string"}
    if transaction_ids:
        transaction_schema["enum"] = transaction_ids
    subject = {
        "type": "object",
        "properties": {
            "kind": {"type": "string", "enum": ["transaction"]},
            "id": transaction_schema,
        },
        "required": ["kind", "id"],
        "additionalProperties": False,
    }
    evidence_id_schema: dict[str, object] = {"type": "string"}
    if evidence_ids:
        evidence_id_schema["enum"] = evidence_ids
    evidence_digest_schema: dict[str, object] = {"type": ["string", "null"]}
    if evidence_digests:
        evidence_digest_schema["enum"] = evidence_digests
    evidence = {
        "type": "object",
        "properties": {
            "kind": {
                "type": "string",
                "enum": evidence_kinds
                or [
                    "transaction",
                    "artifact",
                    "verifier-attestation",
                    "judge-run",
                    "judgment",
                    "conflict",
                ],
            },
            "id": evidence_id_schema,
            "digest": evidence_digest_schema,
            "relation": {
                "type": "string",
                "enum": ["supports", "refutes", "qualifies", "context", "formalizes", "supersedes"],
            },
        },
        "required": ["kind", "id", "digest", "relation"],
        "additionalProperties": False,
    }
    operation = {
        "type": "object",
        "properties": {
            "action": {"type": "string", "enum": ["issue", "revise", "retract", "reinstate"]},
            "adjudicationId": {"type": "string"},
            "nodeId": {"type": "string"},
            "parentId": {"type": ["string", "null"]},
            "nodeType": {
                "type": "string",
                "enum": ["root", "program", "claim", "lemma", "question", "dispute", "method", "result"],
            },
            "title": {"type": "string"},
            "summary": {"type": "string"},
            "reportSection": {"type": "string"},
            "baseDigest": {"type": ["string", "null"]},
            "baseRevisionId": {"type": ["string", "null"]},
            "subjects": {"type": "array", "items": subject},
            "evidence": {"type": "array", "items": evidence},
        },
        "required": [
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
        ],
        "additionalProperties": False,
    }
    return {
        "type": "object",
        "properties": {"operations": {"type": "array", "items": operation}},
        "required": ["operations"],
        "additionalProperties": False,
    }


def _canonicalize_revision_delta(
    state: dict[str, object], selected_node_ids: list[str], delta: dict[str, object]
) -> tuple[dict[str, object], list[dict[str, object]]]:
    """Canonicalize state-derived control fields without changing mathematical meaning."""
    canonical = copy.deepcopy(delta)
    normalizations: list[dict[str, object]] = []
    operations = canonical.get("operations")
    nodes = state.get("nodes")
    if not isinstance(operations, list) or not isinstance(nodes, dict):
        return canonical, normalizations

    def record(kind: str, node_id: object, reason: str, **fields: object) -> None:
        normalizations.append(
            {"kind": kind, "nodeId": node_id, "reason": reason, **fields}
        )

    for operation in operations:
        if not isinstance(operation, dict):
            continue
        node_id = operation.get("nodeId")
        existing = nodes.get(node_id) if isinstance(node_id, str) else None
        current = (
            existing.get("currentAdjudication") if isinstance(existing, dict) else None
        )
        action = operation.get("action")
        if existing is None:
            if action == "revise":
                operation["action"] = "issue"
                record(
                    "new-node-first-adjudication",
                    node_id,
                    "A node absent from the base state has no adjudication to revise.",
                    fromAction="revise",
                    toAction="issue",
                )
            if operation.get("baseDigest") is not None or operation.get(
                "baseRevisionId"
            ) is not None:
                operation["baseDigest"] = None
                operation["baseRevisionId"] = None
                record(
                    "new-node-null-base",
                    node_id,
                    "A new node has no prior node or adjudication revision.",
                )
            if (
                node_id != "root"
                and operation.get("parentId") in {None, "", "None", "null"}
                and "root" in selected_node_ids
            ):
                operation["parentId"] = "root"
                record(
                    "top-level-node-parent",
                    node_id,
                    "A top-level node is a child of the selected structural root.",
                    toParentId="root",
                )
            continue

        expected_digest = existing.get("digest")
        expected_revision_id = (
            current.get("revisionId") if isinstance(current, dict) else None
        )
        if (
            operation.get("baseDigest") != expected_digest
            or operation.get("baseRevisionId") != expected_revision_id
        ):
            operation["baseDigest"] = expected_digest
            operation["baseRevisionId"] = expected_revision_id
            record(
                "attach-current-base",
                node_id,
                "Concurrency guards come from the authoritative selected state.",
            )
        if action == "revise" and current is None:
            operation["action"] = "issue"
            record(
                "structural-root-first-adjudication",
                node_id,
                "The seed root exists structurally but has no prior adjudication to revise.",
                fromAction="revise",
                toAction="issue",
            )
        elif (
            action == "issue"
            and isinstance(current, dict)
            and existing.get("status") == "active"
        ):
            operation["action"] = "revise"
            record(
                "existing-node-subsequent-adjudication",
                node_id,
                "An active adjudication can be revised but cannot be issued twice.",
                fromAction="issue",
                toAction="revise",
            )

    available = set(nodes)
    pending = list(operations)
    ordered: list[object] = []
    while pending:
        next_pending: list[object] = []
        progressed = False
        for operation in pending:
            if not isinstance(operation, dict):
                next_pending.append(operation)
                continue
            node_id = operation.get("nodeId")
            parent_id = operation.get("parentId")
            if node_id == "root" or parent_id in available:
                ordered.append(operation)
                if isinstance(node_id, str):
                    available.add(node_id)
                progressed = True
            else:
                next_pending.append(operation)
        if not progressed:
            ordered.extend(next_pending)
            break
        pending = next_pending
    if ordered != operations:
        canonical["operations"] = ordered
        record(
            "parent-before-child-order",
            None,
            "Parent node creations must precede their children.",
        )
    return canonical, normalizations


def load_base_state(
    base_run: Path | None, problem: str
) -> tuple[dict[str, object], str | None, str | None]:
    if base_run is None:
        return empty_state(problem), None, None
    manifest, manifest_digest = load_manifest(base_run)
    if manifest.get("problemId") != problem:
        raise MathFlowError("base judge run belongs to a different problem")
    if manifest.get("outputProfile") != "math-flow/hierarchical-markdown-v1":
        raise MathFlowError("base judge run does not contain hierarchical Markdown state")
    try:
        state = json.loads(read_verified_artifact(base_run, manifest, "knowledge-state"))
    except json.JSONDecodeError as exc:
        raise MathFlowError("base knowledge state artifact is not valid JSON") from exc
    ledger_head = manifest.get("ledgerHead")
    if not isinstance(ledger_head, str):
        raise MathFlowError("base judge run has no ledger head")
    return validate_state(state, problem), manifest_digest, ledger_head


def load_base_revision_state(
    base_run: Path | None, problem: str
) -> tuple[dict[str, object], list[dict[str, object]], str | None, str | None]:
    if base_run is None:
        return empty_state_v2(problem), [], None, None
    manifest, manifest_digest = load_manifest(base_run)
    if manifest.get("problemId") != problem:
        raise MathFlowError("base judge run belongs to a different problem")
    if manifest.get("outputProfile") not in {
        "math-flow/hierarchical-markdown-v2",
        "math-flow/knowledge-build-markdown-v1",
    }:
        raise MathFlowError("base judge run does not contain revision-aware hierarchical state")
    try:
        state = json.loads(read_verified_artifact(base_run, manifest, "knowledge-state"))
        revision_text = read_verified_artifact(
            base_run, manifest, "adjudication-revisions"
        ).decode("utf-8")
        revisions = [json.loads(line) for line in revision_text.splitlines() if line.strip()]
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise MathFlowError("base revision-aware state artifacts are not valid JSON") from exc
    ledger_head = manifest.get("ledgerHead")
    if not isinstance(ledger_head, str):
        raise MathFlowError("base judge run has no ledger head")
    valid_state, valid_revisions = validate_state_v2(state, revisions, problem)
    return valid_state, valid_revisions, manifest_digest, ledger_head


def run_hierarchical_judge(
    root: Path,
    problem: str,
    spec: dict[str, object],
    source: dict[str, object],
    head: str,
    base_run: Path | None,
    transport: OpenRouterTransport | None = None,
) -> dict[str, object]:
    revisioned = spec["implementation"] == "openrouter-hierarchical-markdown-v2"
    if revisioned:
        state, revisions, base_run_digest, base_ledger_head = load_base_revision_state(
            base_run, problem
        )
    else:
        state, base_run_digest, base_ledger_head = load_base_state(base_run, problem)
        revisions = []
    if base_ledger_head is not None and head != "WORKTREE":
        if base_ledger_head.startswith("WORKTREE:") or not is_ancestor(
            root, base_ledger_head, str(source["ledgerHead"])
        ):
            raise MathFlowError("base judge run ledger head is not an ancestor of this run")
    send = transport or send_chat_completion
    resolved_head = "WORKTREE" if head == "WORKTREE" else str(source["ledgerHead"])
    problem_statement = read_at(root, resolved_head, f"problems/{problem}/problem.md")
    evidence = artifact_evidence(root, source, head)
    index = state_index_v2(state, revisions) if revisioned else state_index(state)
    node_ids = [str(node["id"]) for node in index]

    selector_prompt = "\n\n".join(
        [
            "Select the smallest set of existing knowledge nodes that must be inspected to assess the supplied ledger.",
            "Select root when a new top-level research program may need to be created. An empty selection means no state update is needed.",
            f"Problem:\n{problem_statement}",
            f"Current knowledge-state index:\n{json.dumps(index, indent=2, ensure_ascii=False)}",
            f"Ledger evidence:\n{evidence or '[no contributions]'}",
        ]
    )
    selector_request = _request(
        spec,
        "select",
        [
            {"role": "system", "content": str(spec["systemPrompt"])},
            {"role": "user", "content": selector_prompt},
        ],
        _selector_schema(node_ids),
    )
    selector_response = send(selector_request)
    selection = _structured_content(selector_response, "select")
    if set(selection) != {"selectedNodeIds", "rationale"}:
        raise MathFlowError("hierarchical selector returned unexpected fields")
    selected_ids = selection["selectedNodeIds"]
    if not isinstance(selected_ids, list) or any(not isinstance(value, str) for value in selected_ids):
        raise MathFlowError("hierarchical selector selectedNodeIds must be a string array")
    if len(selected_ids) != len(set(selected_ids)):
        raise MathFlowError("hierarchical selector returned duplicate node IDs")
    if not isinstance(selection["rationale"], str) or not selection["rationale"].strip():
        raise MathFlowError("hierarchical selector rationale must be non-empty")
    selected = (
        selected_nodes_v2(state, revisions, selected_ids)
        if revisioned
        else selected_nodes(state, selected_ids)
    )

    writer_prompt = "\n\n".join(
        [
            "Write a detailed Markdown research assessment. Do not output JSON and do not optimize for brevity.",
            "Explain correctness, gaps, competing approaches, cumulative knowledge, and credit with enough detail for a mathematician to audit.",
            "Treat the materialized knowledge state as a holistic current account, not a collection of submissions, corrections, judgments, or other update events.",
            "When later evidence changes an existing mathematical concept, update that selected stable node. Propose a new node only for a distinct durable concept that remains meaningful without transaction names or chronology.",
            "Use explicit headings of the form `## Node: <stable-id>` for every existing or proposed knowledge node that should change.",
            "Each `## Node:` section must state the complete current knowledge after the update, without framing it as a correction or change log. Put historical explanation under a separate `## Change: <stable-id>` heading so it is audited in the report but not copied into current node content.",
            "You may propose new stable IDs using lowercase letters, numbers, slashes, underscores, and hyphens.",
            *(
                [
                    "Treat prior adjudications as immutable history. When new evidence changes a past judgment, explain the revision or retraction and distinguish the older subject from the newer evidence.",
                    "Discuss whether each changed node issues, revises, retracts, or reinstates its adjudication.",
                ]
                if revisioned
                else []
            ),
            f"Judge rubric:\n{json.dumps(spec['rubric'], indent=2, ensure_ascii=False)}",
            f"Problem:\n{problem_statement}",
            f"Selected knowledge nodes:\n{json.dumps(selected, indent=2, ensure_ascii=False)}",
            f"Selection rationale:\n{selection['rationale']}",
            f"Ledger evidence:\n{evidence or '[no contributions]'}",
        ]
    )
    writer_request = _request(
        spec,
        "report",
        [
            {"role": "system", "content": str(spec["systemPrompt"])},
            {"role": "user", "content": writer_prompt},
        ],
    )
    writer_response = send(writer_request)
    report = _assistant_content(writer_response).rstrip() + "\n"

    transaction_ids = [str(item["transactionId"]) for item in source["transactions"]]
    transaction_positions = {
        str(item["transactionId"]): int(item["ordinal"]) for item in source["transactions"]
    }
    unadjudicated_selected_ids = [
        str(node["id"])
        for node in selected
        if revisioned and node.get("currentAdjudication") is None
    ]
    extractor_prompt = "\n\n".join(
        [
            "Extract only the knowledge-state delta implied by the report. Do not redo the mathematical judgment.",
            "Existing nodes may be updated only if they were selected. New nodes must be parented under a selected or newly created node.",
            "Do not issue a node merely to record a submission, judgment, correction, or revision event. A correction to an existing concept normally produces only a revise, retract, or reinstate operation on that stable node.",
            "For existing nodes, copy the exact current digest into baseDigest. For new nodes use null.",
            *(
                [
                    "Use issue for a first adjudication, revise for an active adjudication changed without withdrawal, retract to withdraw an active adjudication, and reinstate only for a retracted adjudication.",
                    "adjudicationId must equal nodeId. Copy the selected node's current revisionId into baseRevisionId; use null for a first adjudication.",
                    f"These selected structural nodes have no prior adjudication and must use issue, never revise: {json.dumps(unadjudicated_selected_ids)}",
                    "Every non-root node must have a non-null parentId. Use parentId root for a new top-level research program when root was selected.",
                    "subjects identify older or current ledger transactions being adjudicated. evidence identifies why the adjudication is warranted or changed; later transactions may refute earlier subjects.",
                    "For transaction evidence, use the transaction ID as id and null digest. Non-transaction evidence requires a SHA-256 digest and must only reference an artifact explicitly present in the supplied evidence.",
                ]
                if revisioned
                else []
            ),
            "Create parent nodes before their children in the operations array.",
            "reportSection must exactly equal the full `## Node: ...` heading line from the report, including the two hash characters. Return no operation when the report proposes no state change.",
            f"Selected nodes:\n{json.dumps(selected, indent=2, ensure_ascii=False)}",
            f"Allowed transaction IDs:\n{json.dumps(transaction_ids, indent=2)}",
            f"Report:\n<report>\n{report}\n</report>",
        ]
    )
    extractor_request = _request(
        spec,
        "extract",
        [
            {
                "role": "system",
                "content": "You are a faithful data extractor. Preserve the report's meaning and emit only requested state operations.",
            },
            {"role": "user", "content": extractor_prompt},
        ],
        (
            _revision_delta_schema(transaction_ids)
            if revisioned
            else _delta_schema(transaction_ids)
        ),
    )
    extractor_response = send(extractor_request)
    delta = _structured_content(extractor_response, "extract")
    if set(delta) != {"operations"} or not isinstance(delta["operations"], list):
        raise MathFlowError("hierarchical extractor returned an invalid delta envelope")
    if revisioned:
        delta, normalizations = _canonicalize_revision_delta(state, selected_ids, delta)
    else:
        normalizations = []
    report_headings = {line.strip() for line in report.splitlines() if line.strip().startswith("## ")}
    allowed_transaction_ids = set(transaction_ids)
    for operation in delta["operations"]:
        if not isinstance(operation, dict):
            raise MathFlowError("hierarchical extractor returned a non-object delta operation")
        if operation.get("reportSection") not in report_headings:
            raise MathFlowError("knowledge delta references a missing Markdown report heading")
        if revisioned:
            operation_subjects = operation.get("subjects")
            operation_evidence = operation.get("evidence")
            if not isinstance(operation_subjects, list) or not isinstance(operation_evidence, list):
                raise MathFlowError("revision operation must distinguish subjects and evidence")
            subject_ids = {
                item.get("id") for item in operation_subjects if isinstance(item, dict)
            }
            evidence_transaction_ids = {
                item.get("id")
                for item in operation_evidence
                if isinstance(item, dict) and item.get("kind") == "transaction"
            }
            if not subject_ids <= allowed_transaction_ids or not evidence_transaction_ids <= allowed_transaction_ids:
                raise MathFlowError("adjudication revision references a transaction outside the ledger")
        else:
            operation_transaction_ids = operation.get("transactionIds")
            if not isinstance(operation_transaction_ids, list) or not set(operation_transaction_ids) <= allowed_transaction_ids:
                raise MathFlowError("knowledge delta references a transaction outside the ledger")
    report_digest = sha256_bytes(report.encode("utf-8"))
    if revisioned:
        next_state, next_revisions = apply_revision_deltas(
            state,
            revisions,
            selected_ids,
            delta["operations"],
            report_digest,
            report,
            str(source["ledgerHead"]),
            transaction_positions,
        )
    else:
        next_state = apply_deltas(
            state, selected_ids, delta["operations"], report_digest, report
        )
        next_revisions = []

    responses = [selector_response, writer_response, extractor_response]
    requests = [selector_request, writer_request, extractor_request]
    stages = ["select", "report", "extract"]
    return {
        "baseRunDigest": base_run_digest,
        "selection": selection,
        "report": report,
        "delta": delta,
        "state": next_state,
        "revisions": next_revisions,
        "normalizations": normalizations,
        "requestDigests": [f"sha256:{sha256_json(request)}" for request in requests],
        "providerRuns": [
            _provider_run(response, str(request["model"]), stage)
            for response, request, stage in zip(responses, requests, stages, strict=True)
        ],
    }
