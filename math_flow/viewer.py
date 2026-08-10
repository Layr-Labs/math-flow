from __future__ import annotations

import json
from pathlib import Path

from .artifacts import load_manifest, read_verified_artifact, verify_bundle
from .coordination import load_scheduler
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
        if manifest.get("outputProfile") not in {
            "math-flow/hierarchical-markdown-v2",
            "math-flow/knowledge-build-markdown-v1",
        }:
            raise MathFlowError(f"viewer run is not revision-aware hierarchical Markdown: {bundle}")
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
            and provider_run.get("cacheHit") is not True
            and isinstance(provider_run.get("usage"), dict)
            and isinstance(provider_run["usage"].get("cost", 0), (int, float))
        )
        run_id = bundle.name
        runs.append(
            {
                "id": run_id,
                "ordinal": ordinal,
                "ledgerHead": manifest["ledgerHead"],
                "problemLedgerHead": manifest.get(
                    "problemLedgerHead", manifest["ledgerHead"]
                ),
                "runDigest": manifest_digest,
                "baseRun": manifest.get("baseRun"),
                "runKind": manifest.get("runKind", "legacy-projection"),
                "inputs": manifest.get("inputs"),
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


def _projection_run_index(projection_root: Path) -> dict[str, dict[str, object]]:
    runs: dict[str, dict[str, object]] = {}
    index_root = projection_root / "indexes" / "problems"
    if not index_root.exists():
        return runs
    for index_path in sorted(index_root.glob("*/runs.json")):
        try:
            values = json.loads(index_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise MathFlowError(f"could not read projection index {index_path}: {exc}") from exc
        if not isinstance(values, list) or any(not isinstance(item, dict) for item in values):
            raise MathFlowError(f"invalid projection index: {index_path}")
        for item in values:
            digest = item.get("runDigest")
            relative = item.get("path")
            if not isinstance(digest, str) or not isinstance(relative, str):
                raise MathFlowError(f"projection index entry is incomplete: {index_path}")
            target = (projection_root / relative).resolve()
            try:
                target.relative_to(projection_root.resolve())
            except ValueError as exc:
                raise MathFlowError(f"projection index path escapes its root: {relative}") from exc
            manifest, verified_digest = verify_bundle(target)
            if verified_digest != digest:
                raise MathFlowError(f"projection index digest does not match object: {relative}")
            if manifest.get("runKind", "legacy-projection") not in {
                "knowledge-build",
                "legacy-projection",
            }:
                continue
            if manifest.get("outputProfile") not in {
                "math-flow/hierarchical-markdown-v2",
                "math-flow/knowledge-build-markdown-v1",
            }:
                continue
            if digest in runs and runs[digest]["path"] != target:
                raise MathFlowError(f"projection digest appears at multiple paths: {digest}")
            runs[digest] = {"manifest": manifest, "path": target}
    return runs


def _projection_lane(manifest: dict[str, object]) -> str:
    inputs = manifest.get("inputs")
    if isinstance(inputs, dict) and isinstance(inputs.get("laneId"), str):
        return str(inputs["laneId"])
    judge_spec = manifest.get("judgeSpec")
    if isinstance(judge_spec, dict) and isinstance(judge_spec.get("digest"), str):
        return str(judge_spec["digest"])
    raise MathFlowError("viewer projection run has no stable lane identity")


def _projection_chain(
    runs: dict[str, dict[str, object]], terminal_digest: str
) -> list[Path]:
    chain: list[Path] = []
    seen: set[str] = set()
    cursor: str | None = terminal_digest
    while cursor is not None:
        if cursor in seen:
            raise MathFlowError(f"viewer projection chain contains a cycle: {cursor}")
        seen.add(cursor)
        item = runs.get(cursor)
        if item is None:
            raise MathFlowError(f"viewer projection chain is missing base run: {cursor}")
        chain.append(item["path"])
        manifest = item["manifest"]
        base = manifest.get("baseRun")
        if base is not None and not isinstance(base, str):
            raise MathFlowError(f"viewer projection run has an invalid base run: {cursor}")
        cursor = base
    chain.reverse()
    return chain


def export_viewer_catalog(
    root: Path,
    projection_root: Path,
    repository: str,
    canonical_ref: str = "main",
    projection_ref: str = "projections",
) -> dict[str, object]:
    """Build a deterministic, repository-backed catalog of published projections."""

    root = root.resolve()
    projection_root = projection_root.resolve()
    published_runs = _projection_run_index(projection_root)
    by_lane: dict[tuple[str, str], dict[str, dict[str, object]]] = {}
    for digest, item in published_runs.items():
        manifest = item["manifest"]
        problem = manifest.get("problemId")
        if not isinstance(problem, str):
            raise MathFlowError(f"viewer projection run has no problem ID: {digest}")
        by_lane.setdefault((problem, _projection_lane(manifest)), {})[digest] = item

    scheduler_path = projection_root / "coordination" / "scheduler.json"
    scheduler = load_scheduler(scheduler_path) if scheduler_path.exists() else None
    scheduled_terminals: dict[tuple[str, str], str] = {}
    if scheduler is not None:
        for lane_id, lane in scheduler["lanes"].items():
            latest = lane.get("latestStateRun")
            problem = lane.get("problemId")
            if latest is None:
                continue
            if not isinstance(problem, str) or not isinstance(latest, str):
                raise MathFlowError(f"knowledge scheduler lane has invalid viewer state: {lane_id}")
            scheduled_terminals[(problem, str(lane_id))] = latest

    projections: list[dict[str, object]] = []
    for (problem, lane), lane_runs in sorted(by_lane.items()):
        bases = {
            str(item["manifest"].get("baseRun"))
            for item in lane_runs.values()
            if item["manifest"].get("baseRun") is not None
        }
        scheduled = scheduled_terminals.get((problem, lane))
        terminals = [scheduled] if scheduled is not None else sorted(set(lane_runs) - bases)
        if scheduled is not None and scheduled not in lane_runs:
            raise MathFlowError(
                f"knowledge scheduler latest state is not published for {problem}: {scheduled}"
            )
        if not terminals:
            raise MathFlowError(f"viewer projection lane has no terminal run: {lane}")
        for terminal in terminals:
            chain = _projection_chain(lane_runs, terminal)
            terminal_manifest = lane_runs[terminal]["manifest"]
            head = terminal_manifest.get("ledgerHead")
            if not isinstance(head, str):
                raise MathFlowError(f"viewer projection run has no ledger head: {terminal}")
            data = export_viewer_data(root, problem, head, chain)
            judge_spec = terminal_manifest.get("judgeSpec")
            if not isinstance(judge_spec, dict):
                raise MathFlowError(f"viewer projection run has no judge identity: {terminal}")
            projection_id = lane if len(terminals) == 1 else f"{lane}@{terminal}"
            projections.append(
                {
                    "id": projection_id,
                    "problemId": problem,
                    "label": str(judge_spec.get("id", "unnamed projection")),
                    "builder": judge_spec,
                    "latestRunDigest": terminal,
                    "runCount": len(chain),
                    "data": data,
                }
            )

    projections.sort(key=lambda item: (str(item["problemId"]), str(item["label"]), str(item["id"])))
    return {
        "schemaVersion": 1,
        "repository": {
            "slug": repository,
            "canonicalRef": canonical_ref,
            "projectionRef": projection_ref,
        },
        "projections": projections,
        "defaultProjectionId": projections[0]["id"] if projections else None,
    }
