from __future__ import annotations

import json
import re
from pathlib import Path

from .artifacts import ArtifactBundle, read_verified_artifact, sha256_bytes
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
from .judgments import load_judgment_bundle
from .knowledge import apply_revision_deltas, selected_nodes_v2, state_index_v2
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
IMMUTABLE_CLAIM_FIELDS = CLAIM_FIELDS - {"claimedAt", "buildToken"}
RESOLVED_OUTCOMES = {
    "compatible",
    "prefer-support",
    "prefer-refutation",
    "synthesize",
}
CONFLICT_STANCES = {"supports", "refutes", "qualifies", "uncertain", "raises"}


def _digest(value: object, label: str, nullable: bool = False) -> str | None:
    if nullable and value is None:
        return None
    if not isinstance(value, str) or not DIGEST.fullmatch(value):
        raise MathFlowError(f"{label} must be a SHA-256 digest")
    return value


def validate_build_claim(
    claim: object, problem: str, builder_spec_digest: str
) -> dict[str, object]:
    if not isinstance(claim, dict) or set(claim) != CLAIM_FIELDS:
        raise MathFlowError("knowledge build claim has an invalid envelope")
    if claim.get("schemaVersion") != 1 or claim.get("problemId") != problem:
        raise MathFlowError("knowledge build claim belongs to another problem or version")
    if claim.get("builderSpecDigest") != builder_spec_digest:
        raise MathFlowError("knowledge build claim does not match the builder specification")
    _digest(claim.get("laneId"), "knowledge lane ID")
    _digest(claim.get("builderSpecDigest"), "builder spec digest")
    _digest(claim.get("baseStateRun"), "base state run", nullable=True)
    _digest(claim.get("judgmentSetDigest"), "judgment-set digest")
    _digest(claim.get("buildToken"), "knowledge build token")
    expected_lane = (
        "sha256:"
        + sha256_json(
            {"problemId": problem, "builderSpecDigest": builder_spec_digest}
        )
    )
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
    core = {key: claim[key] for key in IMMUTABLE_CLAIM_FIELDS}
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
        outcome = reconciliation.get("outcome")
        if conflict_id in outcomes and isinstance(outcome, str):
            outcomes[str(conflict_id)].add(outcome)
    return {
        conflict_id
        for conflict_id, values in outcomes.items()
        if len(values) != 1 or not values <= RESOLVED_OUTCOMES
    }


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
) -> dict[str, object]:
    root = root.resolve()
    spec = load_judge_spec(builder_path)
    if spec["implementation"] != "openrouter-knowledge-builder-v1":
        raise MathFlowError("knowledge-build command requires a knowledge builder spec")
    builder_digest = f"sha256:{sha256_json(spec)}"
    build_input = validate_build_claim(claim, problem, builder_digest)
    judgments = _load_judgments(
        judgment_bundle_dirs, problem, list(build_input["judgmentIds"])
    )
    conflicts = _load_conflicts(
        conflicts_path, problem, list(build_input["conflictIds"])
    )
    unresolved_conflicts = _unresolved_conflict_ids(conflicts, judgments)
    source = load_source(root, problem, head)
    transaction_positions = {
        str(item["transactionId"]): int(item["ordinal"])
        for item in source["transactions"]
    }
    for item in judgments.values():
        for subject in item["record"]["subjects"]:
            if subject["id"] not in transaction_positions:
                raise MathFlowError(
                    f"knowledge-build judgment subject is outside the current ledger: {subject['id']}"
                )

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
    index = state_index_v2(state, revisions)
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
    selector_response = send(selector_request)
    selection = _structured_content(selector_response)
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
    selected = selected_nodes_v2(state, revisions, selected_ids)

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
    writer_prompt = "\n\n".join(
        [
            "Write a detailed Markdown knowledge-formation report. Do not output JSON and do not redo, extend, or overturn any mathematical judgment.",
            "Organize the immutable judgment results into durable knowledge nodes. Attribute conclusions to their source judgments rather than presenting your own new mathematical conclusion.",
            "A reconciliation outcome may resolve its named conflict. If a conflict has no reconciliation, has an unresolved or needs-evidence outcome, or has incompatible reconciliation outcomes, preserve it as an active dispute node and do not choose a side.",
            "Use explicit headings of the form `## Node: <stable-id>` for every existing or proposed node that should change.",
            "Explain the organizational change and provenance in enough detail for an auditor. Stable IDs use lowercase letters, numbers, slashes, underscores, and hyphens.",
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
    writer_response = send(writer_request)
    report = _assistant_content(writer_response).rstrip() + "\n"

    transaction_ids = list(transaction_positions)
    unadjudicated_selected_ids = [
        str(node["id"])
        for node in selected
        if node.get("currentAdjudication") is None
    ]
    extractor_prompt = "\n\n".join(
        [
            "Extract only the sparse knowledge-state delta stated by the formation report. Do not perform mathematical reasoning or change any judgment outcome.",
            "Existing nodes may change only when selected. New nodes must be parented under a selected or newly created node. Create parents before children.",
            "Use issue for a first node adjudication, revise for an active node update, retract to retire an active node, and reinstate only for a retired node.",
            "adjudicationId must equal nodeId. For an existing node copy its exact digest and current revisionId into the base fields; use null base fields for a first adjudication.",
            f"Selected structural nodes without a prior adjudication must use issue: {json.dumps(unadjudicated_selected_ids)}",
            "Every non-root node needs a parentId. A new top-level node uses parentId root when root was selected.",
            "Subjects are ledger transactions represented by the node. Evidence may reference an allowed transaction, judgment, or conflict. For transaction evidence use null digest. For judgment or conflict evidence set digest equal to its content-addressed ID.",
            "Every conflict listed as requiring an active dispute must be cited by a non-retract dispute operation.",
            "reportSection must exactly equal the full `## Node: ...` heading line from the report. Return no operation only when the report specifies no state change.",
            f"Selected nodes:\n{json.dumps(selected, indent=2, ensure_ascii=False)}",
            f"Allowed transaction IDs:\n{json.dumps(transaction_ids, indent=2)}",
            f"Allowed judgment IDs:\n{json.dumps(sorted(judgments), indent=2)}",
            f"Allowed conflict IDs:\n{json.dumps(sorted(conflicts), indent=2)}",
            f"Required unresolved dispute IDs:\n{json.dumps(sorted(unresolved_conflicts), indent=2)}",
            f"Report:\n<report>\n{report}\n</report>",
        ]
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
        _revision_delta_schema(transaction_ids),
    )
    extractor_response = send(extractor_request)
    delta = _structured_content(extractor_response)
    if set(delta) != {"operations"} or not isinstance(delta["operations"], list):
        raise MathFlowError("knowledge builder extractor returned an invalid delta envelope")
    delta, normalizations = _canonicalize_revision_delta(state, selected_ids, delta)
    report_headings = {
        line.strip() for line in report.splitlines() if line.strip().startswith("## ")
    }
    observed_unresolved: set[str] = set()
    for operation in delta["operations"]:
        if not isinstance(operation, dict):
            raise MathFlowError("knowledge builder extractor returned a non-object operation")
        if operation.get("reportSection") not in report_headings:
            raise MathFlowError("knowledge delta references a missing Markdown report heading")
        subjects = operation.get("subjects")
        evidence = operation.get("evidence")
        if not isinstance(subjects, list) or not isinstance(evidence, list):
            raise MathFlowError("knowledge operation must distinguish subjects and evidence")
        if any(
            not isinstance(item, dict) or item.get("id") not in transaction_positions
            for item in subjects
        ):
            raise MathFlowError("knowledge operation has a subject outside the current ledger")
        for item in evidence:
            if not isinstance(item, dict):
                raise MathFlowError("knowledge operation has an invalid evidence reference")
            kind = item.get("kind")
            identifier = item.get("id")
            digest = item.get("digest")
            if kind == "transaction":
                valid = identifier in transaction_positions and digest is None
            elif kind == "judgment":
                valid = identifier in judgments and digest == identifier
            elif kind == "conflict":
                valid = identifier in conflicts and digest == identifier
            else:
                valid = False
            if not valid:
                raise MathFlowError(
                    "knowledge operation references evidence outside its claimed inputs"
                )
            if (
                kind == "conflict"
                and identifier in unresolved_conflicts
                and operation.get("nodeType") == "dispute"
                and operation.get("action") != "retract"
            ):
                observed_unresolved.add(str(identifier))
    missing_disputes = unresolved_conflicts - observed_unresolved
    if missing_disputes:
        raise MathFlowError(
            "knowledge formation did not preserve unresolved conflict as a dispute: "
            f"{sorted(missing_disputes)[0]}"
        )

    report_digest = sha256_bytes(report.encode("utf-8"))
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
    requests = [selector_request, writer_request, extractor_request]
    responses = [selector_response, writer_response, extractor_response]
    stages = ["select", "report", "extract"]

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
        "adjudication-revisions",
        "application/x-ndjson",
    )
    envelope = run_envelope(
        problem,
        source,
        spec,
        base_digest,
        [f"sha256:{sha256_json(request)}" for request in requests],
        [
            _provider_run(response, str(request["model"]), stage)
            for response, request, stage in zip(responses, requests, stages, strict=True)
        ],
        run_kind="knowledge-build",
        inputs=build_input,
    )
    return bundle.finalize(envelope)
