from __future__ import annotations

import copy
import json
import os
import re
import tempfile
from pathlib import Path

from .artifacts import ArtifactBundle, load_manifest, read_verified_artifact, sha256_bytes
from .errors import MathFlowError
from .hierarchical import (
    _assistant_content,
    _canonicalize_revision_delta,
    _provider_run,
    _request,
    _revision_delta_schema,
    _selector_schema,
    _structured_content,
    load_base_revision_state,
)
from .judges import load_judge_spec, load_source
from .judgments import detect_conflicts, load_judgment_bundle
from .knowledge import (
    apply_knowledge_revision_deltas,
    apply_revision_deltas,
    empty_state_v3,
    selected_nodes_v2,
    selected_nodes_v3,
    state_index_v2,
    state_index_v3,
    validate_state_v3,
)
from .openrouter import OpenRouterTransport, send_chat_completion
from .repository import is_ancestor, read_at, sha256_json
from .runs import run_envelope


DIGEST = re.compile(r"^sha256:[0-9a-f]{64}$")
CLAIM_FIELDS = {
    "schemaVersion",
    "laneId",
    "problemId",
    "builderSpecDigest",
    "baseStateRun",
    "judgmentIds",
    "conflictIds",
    "judgmentSetDigest",
    "buildToken",
    "claimedAt",
}
OPTIONAL_CLAIM_FIELDS = {"projectionSpecDigest"}
RESOLVED_OUTCOMES = {
    "compatible",
    "prefer-support",
    "prefer-refutation",
    "synthesize",
}
CONFLICT_STANCES = {"supports", "refutes", "qualifies", "uncertain", "raises"}
NODE_ID = re.compile(r"^[a-z0-9][a-z0-9/_-]*$")
EMPTY_RESPONSE_ATTEMPTS = 3


def _digest(value: object, label: str, nullable: bool = False) -> str | None:
    if nullable and value is None:
        return None
    if not isinstance(value, str) or not DIGEST.fullmatch(value):
        raise MathFlowError(f"{label} must be a SHA-256 digest")
    return value


def validate_build_claim(
    claim: object, problem: str, builder_spec_digest: str
) -> dict[str, object]:
    claim_fields = set(claim) if isinstance(claim, dict) else set()
    if (
        not isinstance(claim, dict)
        or claim_fields not in (
            CLAIM_FIELDS,
            CLAIM_FIELDS | OPTIONAL_CLAIM_FIELDS,
        )
    ):
        raise MathFlowError("knowledge build claim has an invalid envelope")
    if claim.get("schemaVersion") != 1 or claim.get("problemId") != problem:
        raise MathFlowError("knowledge build claim belongs to another problem or version")
    if claim.get("builderSpecDigest") != builder_spec_digest:
        raise MathFlowError("knowledge build claim does not match the builder specification")
    _digest(claim.get("laneId"), "knowledge lane ID")
    _digest(claim.get("builderSpecDigest"), "builder spec digest")
    projection_spec_digest = claim.get("projectionSpecDigest")
    if projection_spec_digest is not None:
        _digest(projection_spec_digest, "projection spec digest")
    _digest(claim.get("baseStateRun"), "base state run", nullable=True)
    _digest(claim.get("judgmentSetDigest"), "judgment-set digest")
    _digest(claim.get("buildToken"), "knowledge build token")
    lane_identity = (
        {"problemId": problem, "projectionSpecDigest": projection_spec_digest}
        if projection_spec_digest is not None
        else {"problemId": problem, "builderSpecDigest": builder_spec_digest}
    )
    expected_lane = "sha256:" + sha256_json(lane_identity)
    if claim["laneId"] != expected_lane:
        raise MathFlowError("knowledge build claim has the wrong lane identity")
    if (
        not isinstance(claim.get("claimedAt"), int)
        or isinstance(claim.get("claimedAt"), bool)
        or int(claim["claimedAt"]) < 0
    ):
        raise MathFlowError("knowledge build claim time must be a non-negative integer")
    judgment_ids = claim.get("judgmentIds")
    conflict_ids = claim.get("conflictIds")
    if (
        not isinstance(judgment_ids, list)
        or not isinstance(conflict_ids, list)
        or any(_digest(item, "judgment ID") is None for item in judgment_ids)
        or any(_digest(item, "conflict ID") is None for item in conflict_ids)
    ):
        raise MathFlowError("knowledge build claim has invalid input IDs")
    if len(judgment_ids) != len(set(judgment_ids)) or len(conflict_ids) != len(
        set(conflict_ids)
    ):
        raise MathFlowError("knowledge build claim contains duplicate inputs")
    if not judgment_ids and not conflict_ids:
        raise MathFlowError("knowledge build claim contains no inputs")
    expected_set_digest = (
        f"sha256:{sha256_json({'judgmentIds': judgment_ids, 'conflictIds': conflict_ids})}"
    )
    if claim["judgmentSetDigest"] != expected_set_digest:
        raise MathFlowError("knowledge build claim judgment-set digest does not match")
    immutable_fields = set(claim) - {"claimedAt", "buildToken"}
    core = {key: claim[key] for key in immutable_fields}
    if claim["buildToken"] != f"sha256:{sha256_json(core)}":
        raise MathFlowError("knowledge build token does not match its claim")
    return {**core, "buildToken": claim["buildToken"]}


def _load_conflicts(
    path: Path | None, problem: str, expected_ids: list[str]
) -> dict[str, dict[str, object]]:
    if path is None:
        if expected_ids:
            raise MathFlowError("knowledge build is missing its claimed conflict records")
        return {}
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise MathFlowError(f"could not read knowledge-build conflicts: {exc}") from exc
    records = value.get("conflicts") if isinstance(value, dict) else None
    if not isinstance(records, list):
        raise MathFlowError("knowledge-build conflict input must contain a conflicts array")
    loaded: dict[str, dict[str, object]] = {}
    for record in records:
        if not isinstance(record, dict):
            raise MathFlowError("knowledge-build conflict record must be an object")
        conflict_id = record.get("conflictId")
        core = {key: item for key, item in record.items() if key != "conflictId"}
        conflict_judgments = record.get("judgments")
        if (
            set(record)
            != {
                "schemaVersion",
                "conflictId",
                "problemId",
                "claimKey",
                "status",
                "judgments",
            }
            or conflict_id != f"sha256:{sha256_json(core)}"
            or record.get("schemaVersion") != 1
            or record.get("problemId") != problem
            or record.get("status") != "open"
            or not isinstance(record.get("claimKey"), str)
            or not isinstance(conflict_judgments, list)
            or any(
                not isinstance(item, dict)
                or set(item) != {"judgmentId", "stance", "summary"}
                or _digest(item.get("judgmentId"), "conflict judgment ID") is None
                or item.get("stance") not in CONFLICT_STANCES
                or not isinstance(item.get("summary"), str)
                or not item["summary"].strip()
                for item in conflict_judgments
            )
            or not any(item["stance"] == "supports" for item in conflict_judgments)
            or not any(item["stance"] == "refutes" for item in conflict_judgments)
        ):
            raise MathFlowError("knowledge-build conflict record is invalid")
        if conflict_id in loaded:
            raise MathFlowError("knowledge-build conflict input contains duplicates")
        loaded[str(conflict_id)] = record
    if set(loaded) != set(expected_ids):
        missing = set(expected_ids) - set(loaded)
        extra = set(loaded) - set(expected_ids)
        detail = sorted(missing or extra)[0]
        raise MathFlowError(
            f"knowledge-build conflict inputs do not match the claim: {detail}"
        )
    return loaded


def _load_judgments(
    bundle_dirs: list[Path], problem: str, expected_ids: list[str]
) -> dict[str, dict[str, object]]:
    loaded: dict[str, dict[str, object]] = {}
    for bundle_dir in bundle_dirs:
        manifest, judgment, run_digest = load_judgment_bundle(bundle_dir)
        judgment_id = str(judgment["judgmentId"])
        if judgment.get("problemId") != problem:
            raise MathFlowError("knowledge-build judgment belongs to another problem")
        if judgment_id in loaded:
            raise MathFlowError("knowledge-build judgment input contains duplicates")
        try:
            report = read_verified_artifact(
                bundle_dir, manifest, "judgment-report"
            ).decode("utf-8")
        except UnicodeDecodeError as exc:
            raise MathFlowError("knowledge-build judgment report is not UTF-8") from exc
        loaded[judgment_id] = {
            "record": judgment,
            "report": report,
            "runDigest": run_digest,
        }
    if set(loaded) != set(expected_ids):
        missing = set(expected_ids) - set(loaded)
        extra = set(loaded) - set(expected_ids)
        detail = sorted(missing or extra)[0]
        raise MathFlowError(
            f"knowledge-build judgment inputs do not match the claim: {detail}"
        )
    return loaded


def _unresolved_conflict_ids(
    conflicts: dict[str, dict[str, object]],
    judgments: dict[str, dict[str, object]],
) -> set[str]:
    outcomes: dict[str, set[str]] = {conflict_id: set() for conflict_id in conflicts}
    for item in judgments.values():
        record = item["record"]
        reconciliation = record.get("reconciliation")
        if not isinstance(reconciliation, dict):
            continue
        conflict_id = reconciliation.get("conflictId")
        if conflict_id not in conflicts:
            raise MathFlowError(
                "knowledge formation received a reconciliation without its "
                f"current conflict record: {conflict_id}"
            )
        required_ids = {
            str(conflict_judgment["judgmentId"])
            for conflict_judgment in conflicts[str(conflict_id)]["judgments"]
        }
        if set(reconciliation.get("inputJudgmentIds", [])) != required_ids:
            raise MathFlowError(
                "knowledge formation reconciliation inputs do not match conflict: "
                f"{conflict_id}"
            )
        outcome = reconciliation.get("outcome")
        if isinstance(outcome, str):
            outcomes[str(conflict_id)].add(outcome)
    return {
        conflict_id
        for conflict_id, values in outcomes.items()
        if len(values) != 1 or not values <= RESOLVED_OUTCOMES
    }


def _cached_stage_response(
    checkpoint_dir: Path,
    stage: str,
    request: dict[str, object],
    send: OpenRouterTransport,
) -> tuple[dict[str, object], bool]:
    request_digest = f"sha256:{sha256_json(request)}"
    target = checkpoint_dir / f"{stage}-{request_digest.removeprefix('sha256:')}.json"
    if target.exists():
        try:
            cached = json.loads(target.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise MathFlowError(f"could not read knowledge-build checkpoint: {target}") from exc
        if (
            not isinstance(cached, dict)
            or set(cached) != {"schemaVersion", "stage", "requestDigest", "response"}
            or cached.get("schemaVersion") != 1
            or cached.get("stage") != stage
            or cached.get("requestDigest") != request_digest
            or not isinstance(cached.get("response"), dict)
        ):
            raise MathFlowError(f"invalid knowledge-build checkpoint: {target}")
        cached_response = cached["response"]
        if _stage_response_disposition(cached_response) == "usable":
            return cached_response, True
        target.unlink(missing_ok=True)

    response: dict[str, object] = {}
    for attempt in range(EMPTY_RESPONSE_ATTEMPTS):
        response = send(request)
        disposition = _stage_response_disposition(response)
        if disposition != "empty" or attempt == EMPTY_RESPONSE_ATTEMPTS - 1:
            break
    if disposition != "usable":
        return response, False
    checkpoint = {
        "schemaVersion": 1,
        "stage": stage,
        "requestDigest": request_digest,
        "response": response,
    }
    checkpoint_dir.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix=f".{target.name}.", dir=checkpoint_dir)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
            json.dump(checkpoint, handle, ensure_ascii=False)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, target)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)
    return response, False


def _stage_response_disposition(response: dict[str, object]) -> str:
    """Classify responses for formation retry and checkpoint decisions."""
    if "error" in response:
        return "error"
    try:
        choice = response["choices"][0]
        if choice.get("finish_reason") == "length":
            return "truncated"
        content = choice["message"]["content"]
    except (KeyError, IndexError, TypeError, AttributeError):
        return "empty"
    return "usable" if isinstance(content, str) and content.strip() else "empty"


def _normalize_new_node_ids_from_report_headings(
    state: dict[str, object],
    delta: dict[str, object],
    report_headings: set[str],
) -> tuple[dict[str, object], list[dict[str, object]]]:
    """Make a new node's identity match the report heading it references."""
    canonical = copy.deepcopy(delta)
    operations = canonical.get("operations")
    nodes = state.get("nodes")
    if not isinstance(operations, list) or not isinstance(nodes, dict):
        return canonical, []
    mapping: dict[str, str] = {}
    normalizations: list[dict[str, object]] = []
    operation_ids = {
        str(item.get("nodeId")) for item in operations if isinstance(item, dict)
    }
    for operation in operations:
        if not isinstance(operation, dict):
            continue
        old_id = operation.get("nodeId")
        section = operation.get("reportSection")
        if not isinstance(old_id, str) or not isinstance(section, str):
            continue
        prefix = "## Node: "
        if not section.startswith(prefix):
            continue
        if section not in report_headings:
            def heading_key(value: str) -> str:
                identifier = value.removeprefix(prefix).strip().strip("`*_ ").lower()
                return re.sub(r"[/_-]+", "-", identifier)

            aliases = {heading_key(section), heading_key(old_id)}
            matches = [
                heading
                for heading in report_headings
                if heading.startswith(prefix)
                and heading_key(heading) in aliases
            ]
            if len(matches) == 1 and operation.get("action") in {"issue", "create"}:
                prior_section = section
                operation["reportSection"] = matches[0]
                section = matches[0]
                normalizations.append(
                    {
                        "kind": "new-node-report-section-alias",
                        "nodeId": old_id,
                        "reason": "A new node's report reference used an equivalent stable-ID separator or quoting form.",
                        "fromReportSection": prior_section,
                        "toReportSection": matches[0],
                    }
                )
        heading_id = section.removeprefix(prefix).strip()
        if heading_id == old_id:
            continue
        if (
            operation.get("action") not in {"issue", "create"}
            or operation.get("baseDigest") is not None
            or operation.get("baseRevisionId") is not None
            or old_id in nodes
            or heading_id in nodes
            or not NODE_ID.fullmatch(heading_id)
            or heading_id in operation_ids
            or old_id in mapping
        ):
            raise MathFlowError(
                "knowledge operation report heading does not match its stable node ID"
            )
        mapping[old_id] = heading_id
        operation["nodeId"] = heading_id
        if "adjudicationId" in operation:
            operation["adjudicationId"] = heading_id
        expected_change_heading = f"## Change: {heading_id}"
        if (
            "changeSection" in operation
            and expected_change_heading in report_headings
        ):
            operation["changeSection"] = expected_change_heading
        normalizations.append(
            {
                "kind": "new-node-id-from-report-heading",
                "nodeId": heading_id,
                "reason": "A new node's stable identity is defined by its referenced report heading.",
                "fromNodeId": old_id,
                "toNodeId": heading_id,
            }
        )
    for operation in operations:
        if isinstance(operation, dict) and operation.get("parentId") in mapping:
            operation["parentId"] = mapping[str(operation["parentId"])]
    return canonical, normalizations


def _knowledge_revision_delta_schema(
    transaction_ids: list[str],
    evidence_kinds: list[str],
    evidence_ids: list[str],
    evidence_digests: list[str | None],
) -> dict[str, object]:
    """Return the v3 control schema without model-declared revision facets."""

    schema = _revision_delta_schema(
        transaction_ids,
        evidence_kinds=evidence_kinds,
        evidence_ids=evidence_ids,
        evidence_digests=evidence_digests,
    )
    operation = schema["properties"]["operations"]["items"]
    operation["properties"].pop("adjudicationId")
    operation["required"].remove("adjudicationId")
    operation["properties"]["changeSection"] = {
        "type": "string",
        "minLength": 1,
    }
    operation["required"].append("changeSection")
    operation["properties"]["action"]["enum"] = [
        "create",
        "update",
        "retire",
        "restore",
    ]
    return schema


def _canonicalize_knowledge_revision_delta(
    state: dict[str, object],
    selected_node_ids: list[str],
    delta: dict[str, object],
) -> tuple[dict[str, object], list[dict[str, object]]]:
    """Canonicalize only state-derived controls for the neutral v3 reducer."""

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
            existing.get("currentRevision") if isinstance(existing, dict) else None
        )
        action = operation.get("action")
        if existing is None:
            if action == "update":
                operation["action"] = "create"
                record(
                    "new-node-first-revision",
                    node_id,
                    "A node absent from the base state must be created before it can be updated.",
                    fromAction="update",
                    toAction="create",
                )
            if operation.get("baseDigest") is not None or operation.get(
                "baseRevisionId"
            ) is not None:
                operation["baseDigest"] = None
                operation["baseRevisionId"] = None
                record(
                    "new-node-null-base",
                    node_id,
                    "A new node has no prior node or knowledge revision.",
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
        if action == "update" and current is None:
            operation["action"] = "create"
            record(
                "structural-root-first-revision",
                node_id,
                "The seed root exists structurally but has no prior knowledge revision.",
                fromAction="update",
                toAction="create",
            )
        elif (
            action == "create"
            and isinstance(current, dict)
            and existing.get("status") == "active"
        ):
            operation["action"] = "update"
            record(
                "existing-node-subsequent-revision",
                node_id,
                "An active knowledge node can be updated but cannot be created twice.",
                fromAction="create",
                toAction="update",
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


def _load_base_knowledge_revision_state(
    base_run: Path | None,
    problem: str,
) -> tuple[dict[str, object], list[dict[str, object]], str | None, str | None]:
    if base_run is None:
        return empty_state_v3(problem), [], None, None
    manifest, manifest_digest = load_manifest(base_run)
    if manifest.get("problemId") != problem:
        raise MathFlowError("base knowledge run belongs to a different problem")
    if manifest.get("outputProfile") != "math-flow/knowledge-build-markdown-v2":
        raise MathFlowError(
            "base knowledge run does not contain neutral facet-aware state"
        )
    try:
        state = json.loads(
            read_verified_artifact(base_run, manifest, "knowledge-state")
        )
        revision_text = read_verified_artifact(
            base_run, manifest, "knowledge-revisions"
        ).decode("utf-8")
        revisions = [
            json.loads(line) for line in revision_text.splitlines() if line.strip()
        ]
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise MathFlowError(
            "base neutral knowledge-state artifacts are not valid JSON"
        ) from exc
    ledger_head = manifest.get("ledgerHead")
    if not isinstance(ledger_head, str):
        raise MathFlowError("base knowledge run has no ledger head")
    valid_state, valid_revisions = validate_state_v3(state, revisions, problem)
    return valid_state, valid_revisions, manifest_digest, ledger_head


def run_knowledge_build_bundle(
    root: Path,
    problem: str,
    builder_path: Path,
    head: str,
    claim: object,
    judgment_bundle_dirs: list[Path],
    conflicts_path: Path | None,
    output_dir: Path,
    base_run: Path | None = None,
    transport: OpenRouterTransport | None = None,
    checkpoint_dir: Path | None = None,
) -> dict[str, object]:
    root = root.resolve()
    spec = load_judge_spec(builder_path)
    implementation = spec["implementation"]
    if implementation not in {
        "openrouter-knowledge-builder-v1",
        "openrouter-knowledge-builder-v2",
    }:
        raise MathFlowError("knowledge-build command requires a knowledge builder spec")
    neutral_revisions = implementation == "openrouter-knowledge-builder-v2"
    builder_digest = f"sha256:{sha256_json(spec)}"
    build_input = validate_build_claim(claim, problem, builder_digest)
    judgments = _load_judgments(
        judgment_bundle_dirs, problem, list(build_input["judgmentIds"])
    )
    conflicts = _load_conflicts(
        conflicts_path, problem, list(build_input["conflictIds"])
    )
    derived_conflicts = {
        str(item["conflictId"]): item
        for item in detect_conflicts(judgment_bundle_dirs)
    }
    missing_conflicts = set(derived_conflicts) - set(conflicts)
    if missing_conflicts:
        raise MathFlowError(
            "knowledge formation received opposed primary judgments without their "
            f"conflict record: {sorted(missing_conflicts)[0]}"
        )
    extra_conflicts = set(conflicts) - set(derived_conflicts)
    if extra_conflicts:
        raise MathFlowError(
            "knowledge formation received a conflict record without its opposed "
            f"primary judgments: {sorted(extra_conflicts)[0]}"
        )
    unresolved_conflicts = _unresolved_conflict_ids(conflicts, judgments)
    source = load_source(root, problem, head)
    transaction_positions = {
        str(item["transactionId"]): int(item["ordinal"])
        for item in source["transactions"]
    }
    claimed_subject_ids = {
        str(subject["id"])
        for item in judgments.values()
        for subject in item["record"]["subjects"]
    }
    claimed_transaction_evidence_ids = claimed_subject_ids | {
        str(transaction_id)
        for item in judgments.values()
        for finding in item["record"]["findings"]
        for transaction_id in finding["evidenceTransactionIds"]
    }
    for item in judgments.values():
        for subject in item["record"]["subjects"]:
            if subject["id"] not in transaction_positions:
                raise MathFlowError(
                    f"knowledge-build judgment subject is outside the current ledger: {subject['id']}"
                )

    if neutral_revisions:
        state, revisions, base_digest, base_ledger_head = (
            _load_base_knowledge_revision_state(base_run, problem)
        )
    else:
        state, revisions, base_digest, base_ledger_head = load_base_revision_state(
            base_run, problem
        )
    if build_input["baseStateRun"] != base_digest:
        raise MathFlowError("knowledge build base run does not match its claim")
    if base_ledger_head is not None and head != "WORKTREE":
        if base_ledger_head.startswith("WORKTREE:") or not is_ancestor(
            root, base_ledger_head, str(source["ledgerHead"])
        ):
            raise MathFlowError("knowledge build base ledger is not an ancestor of this run")

    resolved_head = "WORKTREE" if head == "WORKTREE" else str(source["ledgerHead"])
    problem_statement = read_at(root, resolved_head, f"problems/{problem}/problem.md")
    index = (
        state_index_v3(state, revisions)
        if neutral_revisions
        else state_index_v2(state, revisions)
    )
    node_ids = [str(node["id"]) for node in index]
    judgment_index = [
        {
            "judgmentId": judgment_id,
            "judgmentKind": item["record"]["judgmentKind"],
            "subjects": item["record"]["subjects"],
            "findings": item["record"]["findings"],
            **(
                {"reconciliation": item["record"]["reconciliation"]}
                if "reconciliation" in item["record"]
                else {}
            ),
        }
        for judgment_id, item in sorted(judgments.items())
    ]
    conflict_index = [conflicts[key] for key in sorted(conflicts)]
    send = transport or send_chat_completion
    checkpoints = (
        checkpoint_dir.resolve()
        if checkpoint_dir is not None
        else output_dir.resolve().with_name(f".{output_dir.name}.checkpoints")
    )

    stage_attempts: dict[str, list[tuple[dict[str, object], bool]]] = {}

    def send_stage(stage: str, request: dict[str, object]) -> dict[str, object]:
        response, cache_hit = _cached_stage_response(checkpoints, stage, request, send)
        stage_attempts.setdefault(stage, []).append((response, cache_hit))
        return response

    def invalidate_stage(stage: str, request: dict[str, object]) -> None:
        request_digest = sha256_json(request)
        (checkpoints / f"{stage}-{request_digest}.json").unlink(missing_ok=True)

    selector_prompt = "\n\n".join(
        [
            "Select the smallest set of existing knowledge nodes that may need organizational updates for this exact judgment batch.",
            "Select root when a new top-level program, claim, or dispute may be needed.",
            "This is knowledge formation, not mathematical adjudication. The supplied judgments and reconciliation outcomes are immutable inputs.",
            f"Problem:\n{problem_statement}",
            f"Current knowledge-state index:\n{json.dumps(index, indent=2, ensure_ascii=False)}",
            f"Judgment routing index:\n{json.dumps(judgment_index, indent=2, ensure_ascii=False)}",
            f"Open conflict records:\n{json.dumps(conflict_index, indent=2, ensure_ascii=False)}",
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
    selector_response = send_stage("select", selector_request)
    selection = _structured_content(selector_response, "select")
    if set(selection) != {"selectedNodeIds", "rationale"}:
        raise MathFlowError("knowledge builder selector returned unexpected fields")
    selected_ids = selection["selectedNodeIds"]
    if (
        not isinstance(selected_ids, list)
        or any(not isinstance(value, str) for value in selected_ids)
        or len(selected_ids) != len(set(selected_ids))
        or not isinstance(selection["rationale"], str)
        or not selection["rationale"].strip()
    ):
        raise MathFlowError("knowledge builder selector returned an invalid selection")
    selected = (
        selected_nodes_v3(state, revisions, selected_ids)
        if neutral_revisions
        else selected_nodes_v2(state, revisions, selected_ids)
    )

    judgment_reports = "\n\n".join(
        "\n".join(
            [
                f"<judgment id={json.dumps(judgment_id)}>",
                item["report"],
                "</judgment>",
            ]
        )
        for judgment_id, item in sorted(judgments.items())
    )
    change_report_guidance = (
        "For every changed node, follow its holistic `## Node: <stable-id>` section "
        "with one unique `## Change: <stable-id>` section. Its body must be a concise, "
        "self-contained audit rationale explaining why this build changes the node; "
        "do not repeat the holistic node assessment there."
        if neutral_revisions
        else "Put historical explanation under a separate `## Change: <stable-id>` heading so it remains in the report but outside materialized node content."
    )
    writer_prompt = "\n\n".join(
        [
            "Write a detailed Markdown knowledge-formation report. Do not output JSON and do not redo, extend, or overturn any mathematical judgment.",
            "Organize the immutable judgment results into durable knowledge nodes. Attribute conclusions to their source judgments rather than presenting your own new mathematical conclusion.",
            "Treat the knowledge state as a holistic current account, not a collection of deltas. A submission, judgment, correction, or revision event belongs in provenance and is not itself a knowledge node.",
            "When a judgment changes an existing mathematical concept, update that concept's selected stable node. Propose a new node only for a distinct durable concept that would remain meaningful if transaction names and chronology were removed.",
            "A reconciliation outcome may resolve its named conflict. If a conflict has no reconciliation, has an unresolved or needs-evidence outcome, or has incompatible reconciliation outcomes, preserve it as an active dispute node and do not choose a side.",
            "Use explicit headings of the form `## Node: <stable-id>` for every existing or proposed node that should change.",
            "Each `## Node:` section must be a self-contained statement of the complete current knowledge after the proposed update. Do not title or frame it as a submission, correction, revision, or change log.",
            change_report_guidance,
            "Explain organizational changes and provenance in enough detail for an auditor. Stable IDs use lowercase letters, numbers, slashes, underscores, and hyphens.",
            f"Formation rubric:\n{json.dumps(spec['rubric'], indent=2, ensure_ascii=False)}",
            f"Problem:\n{problem_statement}",
            f"Selected knowledge nodes:\n{json.dumps(selected, indent=2, ensure_ascii=False)}",
            f"Selection rationale:\n{selection['rationale']}",
            f"Judgment routing index:\n{json.dumps(judgment_index, indent=2, ensure_ascii=False)}",
            f"Conflict records:\n{json.dumps(conflict_index, indent=2, ensure_ascii=False)}",
            f"Conflicts that must remain active disputes:\n{json.dumps(sorted(unresolved_conflicts), indent=2)}",
            f"Immutable judgment reports:\n{judgment_reports or '[no judgment reports]'}",
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
    writer_response = send_stage("report", writer_request)
    report = _assistant_content(writer_response).rstrip() + "\n"

    unrevised_selected_ids = [
        str(node["id"])
        for node in selected
        if node.get(
            "currentRevision" if neutral_revisions else "currentAdjudication"
        )
        is None
    ]
    selected_subject_ids = {
        str(subject["id"])
        for node in selected
        for subject in node.get("subjects", [])
        if isinstance(subject, dict) and isinstance(subject.get("id"), str)
    }
    selected_evidence = [
        evidence
        for node in selected
        for evidence in node.get("evidence", [])
        if isinstance(evidence, dict)
        and isinstance(evidence.get("kind"), str)
        and isinstance(evidence.get("id"), str)
    ]
    allowed_subject_ids = claimed_subject_ids | selected_subject_ids
    allowed_transaction_evidence_ids = claimed_transaction_evidence_ids | {
        str(evidence["id"])
        for evidence in selected_evidence
        if evidence["kind"] == "transaction"
    }
    allowed_judgment_evidence_ids = set(judgments) | {
        str(evidence["id"])
        for evidence in selected_evidence
        if evidence["kind"] == "judgment"
    }
    allowed_conflict_evidence_ids = set(conflicts) | {
        str(evidence["id"])
        for evidence in selected_evidence
        if evidence["kind"] == "conflict"
    }
    if neutral_revisions:
        action_guidance = (
            "Use create for a first node revision, update for a material change to an "
            "active node, retire to make an active node inactive, and restore only for "
            "a retired node. Do not classify revision facets; the reducer derives them "
            "from actual topology, content, lifecycle, and provenance changes."
        )
        base_guidance = (
            "For an existing node copy its exact digest and current revisionId into "
            "the base fields; use null base fields for a first revision."
        )
        first_revision_guidance = (
            "Selected structural nodes without a prior revision must use create: "
            f"{json.dumps(unrevised_selected_ids)}"
        )
    else:
        action_guidance = (
            "Use issue for a first node adjudication, revise for an active node update, "
            "retract to retire an active node, and reinstate only for a retired node."
        )
        base_guidance = (
            "adjudicationId must equal nodeId. For an existing node copy its exact "
            "digest and current revisionId into the base fields; use null base fields "
            "for a first adjudication."
        )
        first_revision_guidance = (
            "Selected structural nodes without a prior adjudication must use issue: "
            f"{json.dumps(unrevised_selected_ids)}"
        )
    event_node_guidance = (
        "The state is a holistic current view. Do not create an event-shaped node "
        "merely to record a submission, judgment, correction, or revision. When the "
        "report corrects an existing concept, emit only the operation on that stable "
        "node unless the report also states a genuinely distinct durable concept."
        if neutral_revisions
        else "The state is a holistic current view. Do not issue an event-shaped node merely to record a submission, judgment, correction, or revision. When the report corrects an existing concept, emit only the operation on that stable node unless the report also states a genuinely distinct durable concept."
    )
    conflict_action_guidance = (
        "Every conflict listed as requiring an active dispute must be cited by a "
        "non-retire dispute operation. Do not create an active dispute node merely "
        "to say that no conflict exists. Every active dispute operation must cite at "
        "least one conflict from the required unresolved dispute list. A resolved "
        "existing dispute may instead be retired."
        if neutral_revisions
        else "Every conflict listed as requiring an active dispute must be cited by a non-retract dispute operation. Do not create an active dispute node merely to say that no conflict exists. Every active dispute operation must cite at least one conflict from the required unresolved dispute list. A resolved existing dispute may instead be retracted."
    )
    report_reference_guidance = (
        "reportSection must exactly equal `## Node: <nodeId>` and changeSection "
        "must exactly equal `## Change: <nodeId>`, both using the operation's exact "
        "nodeId. The reducer copies the exact Change-section body into immutable "
        "revision provenance; do not place a change rationale in summary."
        if neutral_revisions
        else "reportSection must exactly equal `## Node: <nodeId>` using the operation's exact nodeId."
    )
    extractor_prompt = "\n\n".join(
        [
            "Extract only the sparse knowledge-state delta stated by the formation report. Do not perform mathematical reasoning or change any judgment outcome.",
            "Existing nodes may change only when selected. New nodes must be parented under a selected or newly created node. Create parents before children.",
            event_node_guidance,
            action_guidance,
            base_guidance,
            first_revision_guidance,
            "Every non-root node needs a parentId. A new top-level node uses parentId root when root was selected.",
            "Subjects are ledger transactions represented by the durable mathematical node. On an existing node, preserve its prior subjects unless a supplied judgment changes what that node represents. A corrective transaction normally belongs in evidence rather than becoming a new subject. Evidence may reference an allowed transaction, judgment, or conflict. For transaction evidence use null digest. For judgment or conflict evidence set digest equal to its content-addressed ID.",
            "A new node may name as a subject only a transaction that was a subject of a claimed judgment; context-only evidence must remain evidence and must not be promoted to a subject.",
            conflict_action_guidance,
            f"{report_reference_guidance} Return no operation only when the report specifies no state change.",
            f"Selected nodes:\n{json.dumps(selected, indent=2, ensure_ascii=False)}",
            f"Allowed subject transaction IDs (claimed subjects plus subjects already represented by selected nodes):\n{json.dumps(sorted(allowed_subject_ids), indent=2)}",
            f"Allowed transaction evidence IDs:\n{json.dumps(sorted(allowed_transaction_evidence_ids), indent=2)}",
            f"Allowed judgment IDs:\n{json.dumps(sorted(allowed_judgment_evidence_ids), indent=2)}",
            f"Allowed conflict IDs:\n{json.dumps(sorted(allowed_conflict_evidence_ids), indent=2)}",
            f"Existing selected-node evidence that may be preserved exactly:\n{json.dumps(selected_evidence, indent=2, ensure_ascii=False)}",
            f"Required unresolved dispute IDs:\n{json.dumps(sorted(unresolved_conflicts), indent=2)}",
            f"Report:\n<report>\n{report}\n</report>",
        ]
    )
    selected_evidence_kinds = {str(item["kind"]) for item in selected_evidence}
    selected_evidence_ids = {str(item["id"]) for item in selected_evidence}
    selected_evidence_digests = {item.get("digest") for item in selected_evidence}
    core_evidence_kinds = ["transaction", "judgment", "conflict"]
    delta_schema_args = {
        "evidence_kinds": [
            *core_evidence_kinds,
            *sorted(selected_evidence_kinds - set(core_evidence_kinds)),
        ],
        "evidence_ids": sorted(
            allowed_transaction_evidence_ids
            | allowed_judgment_evidence_ids
            | allowed_conflict_evidence_ids
            | selected_evidence_ids
        ),
        "evidence_digests": [
            None,
            *sorted(
                {
                    *allowed_judgment_evidence_ids,
                    *allowed_conflict_evidence_ids,
                    *(
                        value
                        for value in selected_evidence_digests
                        if isinstance(value, str)
                    ),
                }
            ),
        ],
    }
    delta_schema = (
        _knowledge_revision_delta_schema(
            sorted(allowed_subject_ids), **delta_schema_args
        )
        if neutral_revisions
        else _revision_delta_schema(
            sorted(allowed_subject_ids), **delta_schema_args
        )
    )
    extractor_request = _request(
        spec,
        "extract",
        [
            {
                "role": "system",
                "content": "You are a faithful data extractor for a non-adjudicative knowledge-formation adapter. Emit only report-backed state operations.",
            },
            {"role": "user", "content": extractor_prompt},
        ],
        delta_schema,
    )
    report_headings = {
        line.strip() for line in report.splitlines() if line.strip().startswith("## ")
    }

    def normalized_delta(response: dict[str, object]) -> tuple[dict[str, object], list[dict[str, object]]]:
        extracted = _structured_content(response, "extract")
        if set(extracted) != {"operations"} or not isinstance(extracted["operations"], list):
            raise MathFlowError("knowledge builder extractor returned an invalid delta envelope")
        extracted, heading_normalizations = _normalize_new_node_ids_from_report_headings(
            state, extracted, report_headings
        )
        if neutral_revisions:
            extracted, state_normalizations = _canonicalize_knowledge_revision_delta(
                state, selected_ids, extracted
            )
        else:
            extracted, state_normalizations = _canonicalize_revision_delta(
                state, selected_ids, extracted
            )
        return extracted, [*heading_normalizations, *state_normalizations]

    extractor_response = send_stage("extract", extractor_request)
    delta, normalizations = normalized_delta(extractor_response)
    if any(
        not isinstance(operation, dict)
        or operation.get("reportSection") not in report_headings
        or (
            neutral_revisions
            and operation.get("changeSection") not in report_headings
        )
        for operation in delta["operations"]
    ):
        invalidate_stage("extract", extractor_request)
        extractor_response = send_stage("extract", extractor_request)
        delta, normalizations = normalized_delta(extractor_response)
    observed_unresolved: set[str] = set()
    inactive_action = "retire" if neutral_revisions else "retract"
    for operation in delta["operations"]:
        if not isinstance(operation, dict):
            raise MathFlowError("knowledge builder extractor returned a non-object operation")
        if operation.get("reportSection") not in report_headings:
            raise MathFlowError("knowledge delta references a missing Markdown report heading")
        if operation.get("reportSection") != f"## Node: {operation.get('nodeId')}":
            raise MathFlowError(
                "knowledge operation report heading does not match its stable node ID"
            )
        if neutral_revisions:
            if operation.get("changeSection") not in report_headings:
                raise MathFlowError(
                    "knowledge delta references a missing Markdown change heading"
                )
            if operation.get("changeSection") != f"## Change: {operation.get('nodeId')}":
                raise MathFlowError(
                    "knowledge operation change heading does not match its stable node ID"
                )
        subjects = operation.get("subjects")
        evidence = operation.get("evidence")
        if not isinstance(subjects, list) or not isinstance(evidence, list):
            raise MathFlowError("knowledge operation must distinguish subjects and evidence")
        existing_node = state["nodes"].get(operation.get("nodeId"))
        existing_evidence = {
            (
                item.get("kind"),
                item.get("id"),
                item.get("digest"),
                item.get("relation"),
            )
            for item in (
                existing_node.get("evidence", [])
                if isinstance(existing_node, dict)
                else []
            )
            if isinstance(item, dict)
        }
        permitted_subject_ids = (
            allowed_subject_ids if isinstance(existing_node, dict) else claimed_subject_ids
        )
        if any(
            not isinstance(item, dict) or item.get("id") not in permitted_subject_ids
            for item in subjects
        ):
            raise MathFlowError(
                "knowledge operation promotes a transaction outside its allowed subjects"
            )
        for item in evidence:
            if not isinstance(item, dict):
                raise MathFlowError("knowledge operation has an invalid evidence reference")
            kind = item.get("kind")
            identifier = item.get("id")
            digest = item.get("digest")
            relation = item.get("relation")
            if kind == "transaction":
                valid = identifier in claimed_transaction_evidence_ids and digest is None
            elif kind == "judgment":
                valid = identifier in judgments and digest == identifier
            elif kind == "conflict":
                valid = identifier in conflicts and digest == identifier
            else:
                valid = False
            valid = valid or (kind, identifier, digest, relation) in existing_evidence
            if not valid:
                raise MathFlowError(
                    "knowledge operation references evidence outside its claimed inputs: "
                    f"kind={kind!r}, id={identifier!r}"
                )
            if (
                kind == "conflict"
                and identifier in unresolved_conflicts
                and operation.get("nodeType") == "dispute"
                and operation.get("action") != inactive_action
            ):
                observed_unresolved.add(str(identifier))
        if (
            operation.get("nodeType") == "dispute"
            and operation.get("action") != inactive_action
        ):
            cited_conflicts = {
                str(item.get("id"))
                for item in evidence
                if isinstance(item, dict) and item.get("kind") == "conflict"
            }
            if not cited_conflicts or not cited_conflicts <= unresolved_conflicts:
                raise MathFlowError(
                    "active knowledge dispute does not cite a required unresolved conflict"
                )
    missing_disputes = unresolved_conflicts - observed_unresolved
    if missing_disputes:
        raise MathFlowError(
            "knowledge formation did not preserve unresolved conflict as a dispute: "
            f"{sorted(missing_disputes)[0]}"
        )

    report_digest = sha256_bytes(report.encode("utf-8"))
    apply_delta = (
        apply_knowledge_revision_deltas
        if neutral_revisions
        else apply_revision_deltas
    )
    next_state, next_revisions = apply_delta(
        state,
        revisions,
        selected_ids,
        delta["operations"],
        report_digest,
        report,
        str(source["ledgerHead"]),
        transaction_positions,
    )
    requests = [selector_request, writer_request, extractor_request]
    stages = ["select", "report", "extract"]
    provider_runs: list[dict[str, object]] = []
    for request, stage in zip(requests, stages, strict=True):
        attempts = stage_attempts[stage]
        for attempt, (response, cache_hit) in enumerate(attempts, start=1):
            provider_run = {
                **_provider_run(response, str(request["model"]), stage),
                "cacheHit": cache_hit,
            }
            if len(attempts) > 1:
                provider_run["attempt"] = attempt
                provider_run["validationRejected"] = attempt < len(attempts)
            provider_runs.append(provider_run)

    bundle = ArtifactBundle(output_dir)
    bundle.add_json("control/build-input.json", build_input, "knowledge-build-input")
    bundle.add_json("control/selection.json", selection, "node-selection")
    bundle.add_json(
        "control/normalizations.json",
        {"normalizations": normalizations},
        "adapter-normalizations",
    )
    bundle.add_text("report.md", report, "report", "text/markdown")
    bundle.add_json("state/delta.json", delta, "knowledge-delta")
    bundle.add_json("state/state.json", next_state, "knowledge-state")
    revision_lines = "".join(
        json.dumps(item, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        + "\n"
        for item in next_revisions
    )
    bundle.add_text(
        "state/revisions.jsonl",
        revision_lines,
        "knowledge-revisions" if neutral_revisions else "adjudication-revisions",
        "application/x-ndjson",
    )
    envelope = run_envelope(
        problem,
        source,
        spec,
        base_digest,
        [f"sha256:{sha256_json(request)}" for request in requests],
        provider_runs,
        run_kind="knowledge-build",
        inputs=build_input,
    )
    return bundle.finalize(envelope)
