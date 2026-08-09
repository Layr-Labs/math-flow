from __future__ import annotations

import json
from pathlib import Path

from .artifacts import load_manifest, read_verified_artifact
from .errors import MathFlowError
from .knowledge import validate_state_v2
from .repository import ledger, read_at


def _json_artifact(
    bundle: Path, manifest: dict[str, object], role: str
) -> dict[str, object]:
    try:
        value = json.loads(read_verified_artifact(bundle, manifest, role))
    except json.JSONDecodeError as exc:
        raise MathFlowError(f"viewer source artifact {role!r} is not valid JSON") from exc
    if not isinstance(value, dict):
        raise MathFlowError(f"viewer source artifact {role!r} must be a JSON object")
    return value


def _revision_artifact(
    bundle: Path, manifest: dict[str, object]
) -> list[dict[str, object]]:
    try:
        text = read_verified_artifact(bundle, manifest, "adjudication-revisions").decode(
            "utf-8"
        )
        values = [json.loads(line) for line in text.splitlines() if line.strip()]
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise MathFlowError("viewer revision history is not valid JSON Lines") from exc
    if any(not isinstance(item, dict) for item in values):
        raise MathFlowError("viewer revision history contains a non-object record")
    return values


def _report_artifact(
    bundle: Path, manifest: dict[str, object]
) -> tuple[str, str]:
    try:
        report = read_verified_artifact(bundle, manifest, "report").decode("utf-8")
    except UnicodeDecodeError as exc:
        raise MathFlowError("viewer report artifact is not UTF-8") from exc
    artifacts = manifest.get("artifacts")
    if not isinstance(artifacts, list):
        raise MathFlowError("viewer source run has no artifact index")
    matches = [
        item
        for item in artifacts
        if isinstance(item, dict) and item.get("role") == "report"
    ]
    if len(matches) != 1 or not isinstance(matches[0].get("digest"), str):
        raise MathFlowError("viewer source run has no unique report digest")
    return report, str(matches[0]["digest"])


def _title(markdown: str, fallback: str) -> str:
    for line in markdown.splitlines():
        if line.startswith("# "):
            return line[2:].strip()
    return fallback


def export_viewer_data(
    root: Path,
    problem: str,
    head: str,
    run_dirs: list[Path],
) -> dict[str, object]:
    if not run_dirs:
        raise MathFlowError("viewer export requires at least one judge run")
    root = root.resolve()
    source = ledger(root, problem, head)
    resolved_head = str(source["ledgerHead"])
    problem_markdown = read_at(root, resolved_head, f"problems/{problem}/problem.md")
    transactions = []
    for transaction in source["transactions"]:
        transaction_id = str(transaction["transactionId"])
        path = str(transaction["path"])
        transactions.append(
            {
                **transaction,
                "contentMarkdown": read_at(root, transaction_id, f"{path}/README.md"),
            }
        )

    runs: list[dict[str, object]] = []
    reports: list[dict[str, object]] = []
    previous_manifest_digest: str | None = None
    previous_revision_ids: list[str] = []
    previous_nodes: dict[str, object] = {}
    latest_revisions: list[dict[str, object]] = []
    for ordinal, raw_bundle in enumerate(run_dirs, start=1):
        bundle = raw_bundle.resolve()
        manifest, manifest_digest = load_manifest(bundle)
        if manifest.get("problemId") != problem:
            raise MathFlowError(f"viewer run belongs to a different problem: {bundle}")
        if manifest.get("outputProfile") != "math-flow/hierarchical-markdown-v2":
            raise MathFlowError(f"viewer run is not hierarchical Markdown v2: {bundle}")
        if previous_manifest_digest is not None and manifest.get("baseRun") != previous_manifest_digest:
            raise MathFlowError(f"viewer judge runs do not form a base-run chain: {bundle}")

        state = _json_artifact(bundle, manifest, "knowledge-state")
        revisions = _revision_artifact(bundle, manifest)
        validate_state_v2(state, revisions, problem)
        revision_ids = [str(item["revisionId"]) for item in revisions]
        if revision_ids[: len(previous_revision_ids)] != previous_revision_ids:
            raise MathFlowError(f"viewer judge run rewrites prior revision history: {bundle}")
        added_revision_ids = revision_ids[len(previous_revision_ids) :]
        report, report_digest = _report_artifact(bundle, manifest)
        selection = _json_artifact(bundle, manifest, "node-selection")
        normalizations = _json_artifact(bundle, manifest, "adapter-normalizations")
        delta = _json_artifact(bundle, manifest, "knowledge-delta")
        nodes = state.get("nodes")
        if not isinstance(nodes, dict):
            raise MathFlowError(f"viewer knowledge state has no node map: {bundle}")
        changed_node_ids = [
            node_id
            for node_id, node in nodes.items()
            if not isinstance(previous_nodes.get(node_id), dict)
            or not isinstance(node, dict)
            or previous_nodes[node_id].get("digest") != node.get("digest")
        ]
        cost = sum(
            float(provider_run.get("usage", {}).get("cost", 0))
            for provider_run in manifest.get("providerRuns", [])
            if isinstance(provider_run, dict)
            and isinstance(provider_run.get("usage"), dict)
            and isinstance(provider_run["usage"].get("cost", 0), (int, float))
        )
        run_id = bundle.name
        runs.append(
            {
                "id": run_id,
                "ordinal": ordinal,
                "ledgerHead": manifest["ledgerHead"],
                "runDigest": manifest_digest,
                "baseRun": manifest.get("baseRun"),
                "judgeSpec": manifest["judgeSpec"],
                "runner": manifest["runner"],
                "cost": cost,
                "selection": selection,
                "normalizations": normalizations.get("normalizations", []),
                "delta": delta,
                "state": state,
                "revisionIds": revision_ids,
                "addedRevisionIds": added_revision_ids,
                "changedNodeIds": changed_node_ids,
                "reportDigest": report_digest,
            }
        )
        reports.append({"runId": run_id, "digest": report_digest, "markdown": report})
        previous_manifest_digest = manifest_digest
        previous_revision_ids = revision_ids
        previous_nodes = nodes
        latest_revisions = revisions

    return {
        "schemaVersion": 1,
        "problem": {
            "id": problem,
            "title": _title(problem_markdown, problem),
            "statementMarkdown": problem_markdown,
        },
        "ledgerHead": source["ledgerHead"],
        "transactions": transactions,
        "runs": runs,
        "revisions": latest_revisions,
        "reports": reports,
        "latestRunId": runs[-1]["id"],
    }
