from __future__ import annotations

import json
from pathlib import Path

from .artifacts import load_manifest, read_verified_artifact, sha256_bytes, verify_bundle
from .attestations import verification_requests, verifier_attestation_details
from .coordination import load_scheduler
from .credit import load_credit_assignment_bundle
from .credit_schedule import ordered_credit_runs
from .directions import research_direction_ledger
from .errors import MathFlowError
from .governance import projection_registry_index
from .knowledge import validate_state_v2, validate_state_v3
from .repository import ledger, read_at
from .research_state import validate_research_program_state


def _projection_catalog_sort_key(item: dict[str, object]) -> tuple[object, ...]:
    return (
        str(item["problemId"]),
        item.get("projectionSpec") is None,
        str(item["label"]),
        str(item["id"]),
    )


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
    artifacts = manifest.get("artifacts")
    roles = {
        str(item.get("role"))
        for item in artifacts
        if isinstance(item, dict) and isinstance(item.get("role"), str)
    } if isinstance(artifacts, list) else set()
    revision_roles = roles & {"knowledge-revisions", "adjudication-revisions"}
    if len(revision_roles) != 1:
        raise MathFlowError("viewer source run must have one revision-history artifact")
    role = next(iter(revision_roles))
    try:
        text = read_verified_artifact(bundle, manifest, role).decode("utf-8")
        values = [json.loads(line) for line in text.splitlines() if line.strip()]
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise MathFlowError("viewer revision history is not valid JSON Lines") from exc
    if any(not isinstance(item, dict) for item in values):
        raise MathFlowError("viewer revision history contains a non-object record")
    return values


def _validate_revision_state(
    output_profile: object,
    state: dict[str, object],
    revisions: list[dict[str, object]],
    problem: str,
) -> None:
    if output_profile == "math-flow/knowledge-build-markdown-v2":
        validate_state_v3(state, revisions, problem)
    else:
        validate_state_v2(state, revisions, problem)


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


def _validate_new_revision_report_links(
    revisions: list[dict[str, object]],
    start: int,
    report: str,
    report_digest: str,
) -> None:
    """Bind newly appended neutral revisions to this run's exact report bytes."""

    lines = report.splitlines()

    def exact_section(heading: object, label: str) -> str:
        matches = [
            index
            for index, line in enumerate(lines)
            if isinstance(heading, str) and line.strip() == heading
        ]
        if len(matches) != 1:
            raise MathFlowError(
                f"viewer knowledge revision {label} section is missing or ambiguous"
            )
        start_line = matches[0]
        end_line = len(lines)
        for index in range(start_line + 1, len(lines)):
            if lines[index].strip().startswith("## "):
                end_line = index
                break
        return "\n".join(lines[start_line:end_line]).strip() + "\n"

    for revision_index, revision in enumerate(revisions[start:], start=start):
        report_ref = revision.get("reportRef")
        node_id = revision.get("nodeId")
        if not isinstance(node_id, str) or not isinstance(report_ref, dict):
            raise MathFlowError("viewer knowledge revision has an invalid report reference")
        if revision.get("action") == "move":
            base_revision_id = revision.get("baseRevisionId")
            prior = next(
                (
                    item
                    for item in revisions[:revision_index]
                    if item.get("revisionId") == base_revision_id
                ),
                None,
            )
            if (
                not isinstance(prior, dict)
                or report_ref != prior.get("reportRef")
                or revision.get("contentDigest") != prior.get("contentDigest")
            ):
                raise MathFlowError(
                    "viewer topology move does not reuse its prior node report"
                )
        else:
            if report_ref.get("digest") != report_digest:
                raise MathFlowError(
                    "viewer knowledge revision does not reference its run report"
                )
            heading = report_ref.get("section")
            if heading != f"## Node: {node_id}":
                raise MathFlowError(
                    "viewer knowledge revision report section does not match its node"
                )
            section = exact_section(heading, "report")
            if revision.get("contentDigest") != sha256_bytes(section.encode("utf-8")):
                raise MathFlowError(
                    "viewer knowledge revision content does not match its report section"
                )
        change_ref = revision.get("changeRef")
        if (
            not isinstance(change_ref, dict)
            or change_ref.get("artifact") != "report.md"
            or change_ref.get("digest") != report_digest
        ):
            raise MathFlowError(
                "viewer knowledge revision does not reference its change report"
            )
        change_heading = change_ref.get("section")
        if change_heading != f"## Change: {node_id}":
            raise MathFlowError(
                "viewer knowledge revision change section does not match its node"
            )
        change_section = exact_section(change_heading, "change")
        change_rationale = "\n".join(change_section.splitlines()[1:]).strip()
        if revision.get("changeRationale") != change_rationale:
            raise MathFlowError(
                "viewer knowledge revision rationale does not match its change section"
            )


def _research_viewer_nodes(
    state: dict[str, object], transaction_positions: dict[str, int]
) -> dict[str, dict[str, object]]:
    def references(transaction_ids: list[object], relation: str) -> list[dict[str, object]]:
        return [
            {
                "kind": "transaction",
                "id": str(transaction_id),
                "ledgerPosition": transaction_positions.get(str(transaction_id)),
                "relation": relation,
            }
            for transaction_id in transaction_ids
        ]

    nodes: dict[str, dict[str, object]] = {}
    for program_id, program in state["programs"].items():
        source_ids = list(program.get("sourceTransactionIds", []))
        nodes[str(program_id)] = {
            "id": str(program_id),
            "parentId": program.get("parentId"),
            "type": "program",
            "title": program["title"],
            "summary": program["objective"],
            "status": program["status"],
            "contentMarkdown": "\n\n".join(
                [
                    f"## Objective\n\n{program['objective']}",
                    "## Local credit context\n\n"
                    + (
                        "Root program."
                        if program_id == "root"
                        else "Occupies parent threads: "
                        + ", ".join(program["parentThreadIds"])
                    ),
                ]
            ),
            "subjects": references(source_ids, "source"),
            "evidence": [],
            "reportRef": None,
            "digest": program["digest"],
        }
    for thread_id, thread in state["threads"].items():
        node_id = f"thread:{thread_id}"
        source_ids = list(thread.get("sourceTransactionIds", []))
        nodes[node_id] = {
            "id": node_id,
            "parentId": thread["programId"],
            "type": "question",
            "title": thread["title"],
            "summary": thread["summary"],
            "status": thread["status"],
            "contentMarkdown": "\n\n".join(
                [
                    thread["summary"],
                    f"**Thread kind:** {thread['kind']}",
                    f"**Expected local exposure:** {thread['expectedExposure']}",
                    (
                        "**Conditions:** " + "; ".join(thread["conditions"])
                        if thread["conditions"]
                        else "**Conditions:** none"
                    ),
                ]
            ),
            "subjects": references(source_ids, "source"),
            "evidence": [],
            "reportRef": None,
            "digest": thread["digest"],
        }
    for item_id, item in state["items"].items():
        node_id = f"item:{item_id}"
        subject_ids = list(
            dict.fromkeys(str(reference["transactionId"]) for reference in item["claimRefs"])
        )
        source_ids = [
            str(transaction_id)
            for transaction_id in item.get("sourceTransactionIds", [])
            if str(transaction_id) not in subject_ids
        ]
        evidence = references(source_ids, "source")
        evidence.extend(
            {
                "kind": "knowledge-node",
                "id": f"item:{dependency_id}",
                "relation": "depends-on",
            }
            for dependency_id in item.get("dependencyItemIds", [])
        )
        claim_lines = [
            f"- `{reference['claimKey']}` from `{reference['transactionId']}`"
            for reference in item["claimRefs"]
        ]
        nodes[node_id] = {
            "id": node_id,
            "parentId": item["programId"],
            "type": item["type"],
            "title": item["title"],
            "summary": item["summary"],
            "status": "active",
            "contentMarkdown": item["summary"]
            + (
                "\n\n## Accepted claims\n\n" + "\n".join(claim_lines)
                if claim_lines
                else ""
            ),
            "subjects": references(subject_ids, "accepted-claim"),
            "evidence": evidence,
            "reportRef": None,
            "digest": item["digest"],
        }
    return nodes


def _export_research_viewer_data(
    root: Path,
    problem: str,
    head: str,
    run_dirs: list[Path],
    judgment_dirs: list[Path] | None,
) -> dict[str, object]:
    source = ledger(root, problem, head)
    resolved_head = str(source["ledgerHead"])
    problem_markdown = read_at(root, resolved_head, f"problems/{problem}/problem.md")
    transactions = []
    transaction_positions: dict[str, int] = {}
    for transaction in source["transactions"]:
        transaction_id = str(transaction["transactionId"])
        transaction_positions[transaction_id] = int(transaction["ordinal"])
        path = str(transaction["path"])
        transactions.append(
            {
                **transaction,
                "contentMarkdown": read_at(
                    root, transaction_id, f"{path}/README.md"
                ),
            }
        )

    runs: list[dict[str, object]] = []
    previous_digest: str | None = None
    previous_nodes: dict[str, dict[str, object]] = {}
    for ordinal, raw_bundle in enumerate(run_dirs, start=1):
        bundle = raw_bundle.resolve()
        manifest, manifest_digest = load_manifest(bundle)
        if (
            manifest.get("problemId") != problem
            or manifest.get("outputProfile") != "math-flow/hierarchical-research-v2"
        ):
            raise MathFlowError(
                f"viewer run is not a hierarchical research v2 build: {bundle}"
            )
        if previous_digest is not None and manifest.get("baseRun") != previous_digest:
            raise MathFlowError(f"viewer research runs do not form a base-run chain: {bundle}")
        state = _json_artifact(bundle, manifest, "research-program-state")
        validate_research_program_state(state, problem)
        delta = _json_artifact(bundle, manifest, "research-program-delta")
        nodes = _research_viewer_nodes(state, transaction_positions)
        changed_node_ids = [
            node_id
            for node_id, node in nodes.items()
            if previous_nodes.get(node_id, {}).get("digest") != node.get("digest")
        ]
        cost = sum(
            float(provider_run.get("usage", {}).get("cost", 0))
            for provider_run in manifest.get("providerRuns", [])
            if isinstance(provider_run, dict)
            and isinstance(provider_run.get("usage"), dict)
            and isinstance(provider_run["usage"].get("cost", 0), (int, float))
        )
        runs.append(
            {
                "id": bundle.name,
                "ordinal": ordinal,
                "ledgerHead": manifest["ledgerHead"],
                "problemLedgerHead": manifest.get(
                    "problemLedgerHead", manifest["ledgerHead"]
                ),
                "runDigest": manifest_digest,
                "baseRun": manifest.get("baseRun"),
                "runKind": manifest.get("runKind"),
                "inputs": manifest.get("inputs"),
                "judgeSpec": manifest["judgeSpec"],
                "runner": manifest["runner"],
                "cost": cost,
                "selection": {
                    "selectedNodeIds": sorted(changed_node_ids),
                    "rationale": "Nodes changed by the accepted validity batch.",
                },
                "normalizations": [],
                "delta": delta,
                "state": {"nodes": nodes, "stateDigest": state["stateDigest"]},
                "revisionIds": [],
                "addedRevisionIds": [],
                "changedNodeIds": sorted(changed_node_ids),
                "reportDigest": state["stateDigest"],
                "revisionSemantics": "neutral-knowledge",
            }
        )
        previous_digest = manifest_digest
        previous_nodes = nodes

    judgments_by_id: dict[str, dict[str, object]] = {}
    for judgment_dir in judgment_dirs or []:
        judgment = _viewer_judgment(judgment_dir.resolve(), problem)
        judgment_id = str(judgment["judgmentId"])
        prior = judgments_by_id.get(judgment_id)
        if prior is not None and prior["runDigest"] != judgment["runDigest"]:
            raise MathFlowError(f"viewer judgment ID has multiple run bundles: {judgment_id}")
        judgments_by_id[judgment_id] = judgment
    judgments = sorted(
        judgments_by_id.values(),
        key=lambda item: (
            min(
                (
                    int(subject.get("ledgerPosition", 0))
                    for subject in item["record"].get("subjects", [])
                    if isinstance(subject, dict)
                ),
                default=0,
            ),
            str(item["judgmentId"]),
        ),
    )
    return {
        "schemaVersion": 1,
        "problem": {
            "id": problem,
            "title": _title(problem_markdown, problem),
            "statementMarkdown": problem_markdown,
        },
        "ledgerHead": source["ledgerHead"],
        "transactions": transactions,
        "judgments": judgments,
        "runs": runs,
        "revisions": [],
        "reports": [],
        "latestRunId": runs[-1]["id"],
    }
def _viewer_judgment(bundle: Path, problem: str) -> dict[str, object]:
    manifest, run_digest = load_manifest(bundle)
    if manifest.get("runKind") != "judgment" or manifest.get("problemId") != problem:
        raise MathFlowError(f"viewer judgment belongs to another problem or run kind: {bundle}")
    record = _json_artifact(bundle, manifest, "judgment-record")
    judgment_id = record.get("judgmentId")
    if not isinstance(judgment_id, str):
        raise MathFlowError(f"viewer judgment has no content address: {bundle}")
    try:
        report = read_verified_artifact(bundle, manifest, "judgment-report").decode("utf-8")
    except UnicodeDecodeError as exc:
        raise MathFlowError("viewer judgment report is not UTF-8") from exc
    cost = sum(
        float(provider_run.get("usage", {}).get("cost", 0))
        for provider_run in manifest.get("providerRuns", [])
        if isinstance(provider_run, dict)
        and isinstance(provider_run.get("usage"), dict)
        and isinstance(provider_run["usage"].get("cost", 0), (int, float))
    )
    models = sorted(
        {
            str(provider_run.get("resolvedModel") or provider_run.get("requestedModel"))
            for provider_run in manifest.get("providerRuns", [])
            if isinstance(provider_run, dict)
            and isinstance(
                provider_run.get("resolvedModel") or provider_run.get("requestedModel"),
                str,
            )
        }
    )
    return {
        "judgmentId": judgment_id,
        "runDigest": run_digest,
        "judgmentKind": record.get("judgmentKind"),
        "ledgerHead": manifest.get("ledgerHead"),
        "problemLedgerHead": manifest.get("problemLedgerHead", manifest.get("ledgerHead")),
        "judgeSpec": manifest.get("judgeSpec"),
        "models": models,
        "cost": cost,
        "reportDigest": record.get("reportDigest"),
        "reportMarkdown": report,
        "record": record,
    }


def _viewer_credit_assignment(
    bundle: Path,
    expected_digest: str,
    published_objects: dict[str, dict[str, object]],
) -> dict[str, object]:
    """Load a credit overlay through its canonical verifier and bind its dependency."""

    manifest, credit_index, run_digest = load_credit_assignment_bundle(bundle)
    if run_digest != expected_digest:
        raise MathFlowError(
            f"viewer credit assignment digest does not match its index: {bundle}"
        )
    credit_input = _json_artifact(bundle, manifest, "credit-input")
    dependency_lock = _json_artifact(bundle, manifest, "dependency-lock")
    try:
        report = read_verified_artifact(
            bundle, manifest, "credit-report"
        ).decode("utf-8")
    except UnicodeDecodeError as exc:
        raise MathFlowError("viewer credit report is not UTF-8") from exc

    dependencies = dependency_lock.get("dependencies")
    knowledge_dependencies = [
        item
        for item in dependencies
        if isinstance(item, dict) and item.get("artifactRole") == "knowledge-state"
    ] if isinstance(dependencies, list) else []
    if len(knowledge_dependencies) != 1:
        raise MathFlowError(
            "viewer credit assignment must lock exactly one knowledge state"
        )
    dependency = knowledge_dependencies[0]
    dependency_digest = dependency.get("runDigest")
    dependency_object = (
        published_objects.get(dependency_digest)
        if isinstance(dependency_digest, str)
        else None
    )
    if dependency_object is None:
        raise MathFlowError(
            "viewer credit assignment references an unpublished knowledge run"
        )
    dependency_manifest = dependency_object["manifest"]
    dependency_inputs = dependency_manifest.get("inputs")
    dependency_artifact = dependency.get("artifact")
    artifacts = dependency_manifest.get("artifacts")
    matching_artifacts = [
        item
        for item in artifacts
        if isinstance(item, dict) and item.get("role") == "knowledge-state"
    ] if isinstance(artifacts, list) else []
    if (
        dependency_manifest.get("runKind") != "knowledge-build"
        or dependency_manifest.get("problemId") != manifest.get("problemId")
        or not isinstance(dependency_inputs, dict)
        or dependency_inputs.get("projectionSpecDigest")
        != dependency.get("projectionSpecDigest")
        or dependency_manifest.get("problemLedgerDigest")
        != dependency.get("problemLedgerDigest")
        or len(matching_artifacts) != 1
        or matching_artifacts[0] != dependency_artifact
    ):
        raise MathFlowError(
            "viewer credit assignment knowledge dependency is inconsistent"
        )

    cost = sum(
        float(provider_run.get("usage", {}).get("cost", 0))
        for provider_run in manifest.get("providerRuns", [])
        if isinstance(provider_run, dict)
        and provider_run.get("cacheHit") is not True
        and isinstance(provider_run.get("usage"), dict)
        and isinstance(provider_run["usage"].get("cost", 0), (int, float))
    )
    models = sorted(
        {
            str(provider_run.get("resolvedModel") or provider_run.get("requestedModel"))
            for provider_run in manifest.get("providerRuns", [])
            if isinstance(provider_run, dict)
            and isinstance(
                provider_run.get("resolvedModel") or provider_run.get("requestedModel"),
                str,
            )
        }
    )
    inputs = manifest.get("inputs")
    consumer = dependency_lock.get("consumer")
    if not isinstance(inputs, dict) or not isinstance(consumer, dict):
        raise MathFlowError("viewer credit assignment has no projection identity")
    return {
        "id": run_digest,
        "runDigest": run_digest,
        "ledgerHead": manifest["ledgerHead"],
        "problemLedgerHead": manifest["problemLedgerHead"],
        "problemLedgerDigest": manifest["problemLedgerDigest"],
        "projectionId": consumer["projectionId"],
        "projectionSpecDigest": consumer["projectionSpecDigest"],
        "dependencyLockDigest": dependency_lock["dependencyLockDigest"],
        "dependency": dependency,
        "assignments": credit_index["assignments"],
        "reportMarkdown": report,
        "creditInput": credit_input,
        "dependencyLock": dependency_lock,
        "models": models,
        "cost": cost,
        "schedule": inputs.get("schedule"),
    }


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
    judgment_dirs: list[Path] | None = None,
) -> dict[str, object]:
    if not run_dirs:
        raise MathFlowError("viewer export requires at least one judge run")
    root = root.resolve()
    first_manifest, first_manifest_digest = load_manifest(run_dirs[0].resolve())
    if first_manifest.get("outputProfile") == "math-flow/hierarchical-research-v2":
        return _export_research_viewer_data(
            root, problem, head, run_dirs, judgment_dirs
        )
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
    previous_output_profile: object = None
    previous_revision_ids: list[str] = []
    previous_nodes: dict[str, object] = {}
    latest_revisions: list[dict[str, object]] = []
    for ordinal, raw_bundle in enumerate(run_dirs, start=1):
        bundle = raw_bundle.resolve()
        manifest, manifest_digest = (
            (first_manifest, first_manifest_digest)
            if ordinal == 1
            else load_manifest(bundle)
        )
        if manifest.get("problemId") != problem:
            raise MathFlowError(f"viewer run belongs to a different problem: {bundle}")
        if manifest.get("outputProfile") not in {
            "math-flow/hierarchical-markdown-v2",
            "math-flow/knowledge-build-markdown-v1",
            "math-flow/knowledge-build-markdown-v2",
        }:
            raise MathFlowError(f"viewer run is not revision-aware hierarchical Markdown: {bundle}")
        if (
            previous_output_profile is not None
            and manifest.get("outputProfile") != previous_output_profile
        ):
            raise MathFlowError(
                f"viewer projection chain changes output profile: {bundle}"
            )
        if previous_manifest_digest is not None and manifest.get("baseRun") != previous_manifest_digest:
            raise MathFlowError(f"viewer judge runs do not form a base-run chain: {bundle}")

        state = _json_artifact(bundle, manifest, "knowledge-state")
        revisions = _revision_artifact(bundle, manifest)
        neutral_revisions = (
            manifest.get("outputProfile") == "math-flow/knowledge-build-markdown-v2"
        )
        _validate_revision_state(
            manifest.get("outputProfile"), state, revisions, problem
        )
        revision_ids = [str(item["revisionId"]) for item in revisions]
        if revision_ids[: len(previous_revision_ids)] != previous_revision_ids:
            raise MathFlowError(f"viewer judge run rewrites prior revision history: {bundle}")
        added_revision_ids = revision_ids[len(previous_revision_ids) :]
        report, report_digest = _report_artifact(bundle, manifest)
        if neutral_revisions:
            _validate_new_revision_report_links(
                revisions, len(previous_revision_ids), report, report_digest
            )
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
                "revisionSemantics": (
                    "neutral-knowledge" if neutral_revisions else "legacy-adjudication"
                ),
            }
        )
        reports.append({"runId": run_id, "digest": report_digest, "markdown": report})
        previous_manifest_digest = manifest_digest
        previous_output_profile = manifest.get("outputProfile")
        previous_revision_ids = revision_ids
        previous_nodes = nodes
        latest_revisions = revisions

    judgments_by_id: dict[str, dict[str, object]] = {}
    for judgment_dir in judgment_dirs or []:
        judgment = _viewer_judgment(judgment_dir.resolve(), problem)
        judgment_id = str(judgment["judgmentId"])
        prior = judgments_by_id.get(judgment_id)
        if prior is not None and prior["runDigest"] != judgment["runDigest"]:
            raise MathFlowError(f"viewer judgment ID has multiple run bundles: {judgment_id}")
        judgments_by_id[judgment_id] = judgment
    judgments = sorted(
        judgments_by_id.values(),
        key=lambda item: (
            min(
                (
                    int(subject.get("ledgerPosition", 0))
                    for subject in item["record"].get("subjects", [])
                    if isinstance(subject, dict)
                ),
                default=0,
            ),
            str(item["judgmentId"]),
        ),
    )

    return {
        "schemaVersion": 1,
        "problem": {
            "id": problem,
            "title": _title(problem_markdown, problem),
            "statementMarkdown": problem_markdown,
        },
        "ledgerHead": source["ledgerHead"],
        "transactions": transactions,
        "judgments": judgments,
        "runs": runs,
        "revisions": latest_revisions,
        "reports": reports,
        "latestRunId": runs[-1]["id"],
    }


def _projection_object_index(projection_root: Path) -> dict[str, dict[str, object]]:
    objects: dict[str, dict[str, object]] = {}
    index_root = projection_root / "indexes" / "problems"
    if not index_root.exists():
        return objects
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
            if digest in objects and objects[digest]["path"] != target:
                raise MathFlowError(f"projection digest appears at multiple paths: {digest}")
            objects[digest] = {"manifest": manifest, "path": target}
    return objects


def _projection_judgment_index(
    published_objects: dict[str, dict[str, object]],
) -> dict[str, dict[str, object]]:
    judgments: dict[str, dict[str, object]] = {}
    for digest, item in published_objects.items():
        manifest = item["manifest"]
        target = item["path"]
        if manifest.get("runKind") != "judgment":
            continue
        record = _json_artifact(target, manifest, "judgment-record")
        judgment_id = record.get("judgmentId")
        if not isinstance(judgment_id, str):
            raise MathFlowError(f"published judgment has no content address: {target}")
        prior = judgments.get(judgment_id)
        if prior is not None and prior["path"] != target:
            raise MathFlowError(
                f"projection judgment appears at multiple paths: {judgment_id}"
            )
        judgments[judgment_id] = {
            "manifest": manifest,
            "path": target,
            "runDigest": digest,
        }
    return judgments


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


def _viewer_objective_attestations(
    root: Path,
    published_objects: dict[str, dict[str, object]],
    problems: list[str],
    canonical_ref: str,
) -> list[dict[str, object]]:
    objective_attestations: list[dict[str, object]] = []
    for problem in sorted(problems):
        requests = verification_requests(root, problem, canonical_ref)
        request_index = {
            (str(item["transactionId"]), str(item["requestDigest"])): item
            for item in requests
        }
        published: dict[tuple[str, str], dict[str, object]] = {}
        for digest, item in sorted(published_objects.items()):
            manifest = item["manifest"]
            if (
                manifest.get("runKind") != "verifier-attestation"
                or manifest.get("problemId") != problem
            ):
                continue
            details = verifier_attestation_details(root, item["path"], canonical_ref)
            key = (
                str(details["transactionId"]),
                str(details["requestDigest"]),
            )
            if key not in request_index:
                raise MathFlowError(
                    "published objective attestation has no canonical request"
                )
            if key in published and published[key]["runDigest"] != digest:
                raise MathFlowError(
                    "canonical objective-verification request has multiple outcomes"
                )
            published[key] = details
        for request in requests:
            key = (
                str(request["transactionId"]),
                str(request["requestDigest"]),
            )
            run = published.get(key)
            objective_attestations.append(
                {
                    "problemId": problem,
                    "transactionId": request["transactionId"],
                    "contributionId": request["contributionId"],
                    "requestDigest": request["requestDigest"],
                    "verifier": request["verifier"],
                    "environmentDigest": request["environmentDigest"],
                    "selectionStatus": str(run["status"]) if run else "pending",
                    "run": run,
                }
            )
    objective_attestations.sort(
        key=lambda item: (str(item["problemId"]), str(item["transactionId"]))
    )
    return objective_attestations


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
    projection_specs = projection_registry_index(root)
    published_objects = _projection_object_index(projection_root)
    published_runs = {
        digest: item
        for digest, item in published_objects.items()
        if item["manifest"].get("runKind", "legacy-projection")
        in {"knowledge-build", "legacy-projection"}
        and item["manifest"].get("outputProfile")
        in {
            "math-flow/hierarchical-markdown-v2",
            "math-flow/knowledge-build-markdown-v1",
            "math-flow/knowledge-build-markdown-v2",
            "math-flow/hierarchical-research-v2",
        }
    }
    published_judgments = _projection_judgment_index(published_objects)
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
            referenced_judgment_ids: set[str] = set()
            for bundle in chain:
                manifest, _ = load_manifest(bundle)
                inputs = manifest.get("inputs")
                if isinstance(inputs, dict) and isinstance(inputs.get("judgmentIds"), list):
                    referenced_judgment_ids.update(
                        str(value)
                        for value in inputs["judgmentIds"]
                        if isinstance(value, str)
                    )
            missing_judgments = referenced_judgment_ids - set(published_judgments)
            if missing_judgments:
                raise MathFlowError(
                    "viewer projection is missing a referenced judgment: "
                    f"{sorted(missing_judgments)[0]}"
                )
            judgment_dirs = [
                published_judgments[judgment_id]["path"]
                for judgment_id in sorted(referenced_judgment_ids)
            ]
            data = export_viewer_data(
                root,
                problem,
                head,
                chain,
                judgment_dirs=judgment_dirs,
            )
            judge_spec = terminal_manifest.get("judgeSpec")
            if not isinstance(judge_spec, dict):
                raise MathFlowError(f"viewer projection run has no judge identity: {terminal}")
            terminal_inputs = terminal_manifest.get("inputs")
            projection_digest = (
                terminal_inputs.get("projectionSpecDigest")
                if isinstance(terminal_inputs, dict)
                else None
            )
            registered = (
                projection_specs.get(projection_digest)
                if isinstance(projection_digest, str)
                else None
            )
            registered_id = str(registered["id"]) if registered else None
            base_projection_id = registered_id or lane
            projection_id = (
                base_projection_id
                if len(terminals) == 1
                else f"{base_projection_id}@{terminal}"
            )
            projections.append(
                {
                    "id": projection_id,
                    "problemId": problem,
                    "label": registered_id
                    or str(judge_spec.get("id", "unnamed projection")),
                    "projectionSpec": registered,
                    "builder": judge_spec,
                    "latestRunDigest": terminal,
                    "runCount": len(chain),
                    "data": data,
                }
            )

    # A governed projection edit creates a new digest and lane while its old
    # content-addressed runs remain valid history. Prefer lanes whose digest is
    # still registered so a retired implementation cannot become the default
    # merely because its builder label sorts first.
    projections.sort(key=_projection_catalog_sort_key)

    projection_specs_by_id = {
        str(spec["id"]): spec for spec in projection_specs.values()
    }
    credit_runs: list[dict[str, object]] = []
    for digest, item in sorted(published_objects.items()):
        if item["manifest"].get("runKind") != "credit-assignment":
            continue
        credit_run = _viewer_credit_assignment(
            item["path"], digest, published_objects
        )
        problem = str(item["manifest"]["problemId"])
        current_ledger = ledger(root, problem, canonical_ref)
        associated = [
            projection
            for projection in projections
            if projection["problemId"] == problem
            and any(
                run.get("runDigest") == credit_run["dependency"]["runDigest"]
                for run in projection["data"]["runs"]
            )
        ]
        if not associated:
            raise MathFlowError(
                "viewer credit assignment dependency is absent from every knowledge projection"
            )
        consumer_spec = projection_specs.get(
            str(credit_run["projectionSpecDigest"])
        )
        locked_dependency = credit_run["dependency"]
        declared_dependencies = (
            consumer_spec.get("dependencies", [])
            if isinstance(consumer_spec, dict)
            else []
        )
        declared_dependency = next(
            (
                dependency
                for dependency in declared_dependencies
                if isinstance(dependency, dict)
                and dependency.get("name") == locked_dependency.get("name")
            ),
            None,
        )
        producer_spec = projection_specs_by_id.get(
            str(locked_dependency.get("projectionId"))
        )
        current_consumer = (
            isinstance(consumer_spec, dict)
            and consumer_spec.get("id") == credit_run["projectionId"]
            and consumer_spec.get("engine") == "overlay-repository-v1"
        )
        current_dependency_declaration = (
            isinstance(declared_dependency, dict)
            and declared_dependency.get("projectionId")
            == locked_dependency.get("projectionId")
            and declared_dependency.get("artifactRole")
            == locked_dependency.get("artifactRole")
            and isinstance(producer_spec, dict)
            and producer_spec.get("digest")
            == locked_dependency.get("projectionSpecDigest")
        )
        current_knowledge = current_dependency_declaration and any(
            projection["latestRunDigest"] == locked_dependency["runDigest"]
            and isinstance(projection.get("projectionSpec"), dict)
            and projection["projectionSpec"].get("digest")
            == locked_dependency.get("projectionSpecDigest")
            for projection in associated
        )
        current_problem_ledger = (
            credit_run["problemLedgerHead"] == current_ledger["problemLedgerHead"]
            and credit_run["problemLedgerDigest"]
            == current_ledger["problemLedgerDigest"]
        )
        stale_reasons = []
        # canonicalHead is intentionally excluded: unrelated repository commits
        # do not change the semantic applicability of an exact credit lock.
        if not current_consumer:
            stale_reasons.append("credit-projection-changed")
        if not current_problem_ledger:
            stale_reasons.append("canonical-ledger-advanced")
        if not current_dependency_declaration:
            stale_reasons.append("knowledge-dependency-changed")
        elif not current_knowledge:
            stale_reasons.append("knowledge-projection-advanced")
        credit_runs.append(
            {
                **credit_run,
                "knowledgeProjectionIds": [
                    str(projection["id"]) for projection in associated
                ],
                "currentProblemLedger": current_problem_ledger,
                "currentKnowledgeDependency": current_knowledge,
                "stale": bool(stale_reasons),
                "staleReasons": stale_reasons,
            }
        )

    grouped_credit: dict[tuple[str, str, str], list[dict[str, object]]] = {}
    for credit_run in credit_runs:
        key = (
            str(credit_run["creditInput"]["problemId"]),
            str(credit_run["projectionId"]),
            str(credit_run["projectionSpecDigest"]),
        )
        grouped_credit.setdefault(key, []).append(credit_run)

    for projection_digest, spec in projection_specs.items():
        if spec.get("engine") != "overlay-repository-v1":
            continue
        dependencies = spec.get("dependencies")
        knowledge_dependencies = [
            dependency
            for dependency in dependencies
            if isinstance(dependency, dict)
            and dependency.get("artifactRole") == "knowledge-state"
        ] if isinstance(dependencies, list) else []
        if len(knowledge_dependencies) != 1:
            continue
        producer_id = knowledge_dependencies[0].get("projectionId")
        allowed = spec.get("allowedProblems")
        for knowledge_projection in projections:
            registered_knowledge = knowledge_projection.get("projectionSpec")
            if (
                not isinstance(registered_knowledge, dict)
                or registered_knowledge.get("id") != producer_id
                or not isinstance(allowed, list)
                or (
                    "*" not in allowed
                    and knowledge_projection["problemId"] not in allowed
                )
            ):
                continue
            grouped_credit.setdefault(
                (
                    str(knowledge_projection["problemId"]),
                    str(spec["id"]),
                    projection_digest,
                ),
                [],
            )

    credit_projections: list[dict[str, object]] = []
    projection_id_counts: dict[str, int] = {}
    for _, projection_id, _ in grouped_credit:
        projection_id_counts[projection_id] = projection_id_counts.get(projection_id, 0) + 1
    for (problem, projection_id, projection_digest), group_runs in sorted(
        grouped_credit.items()
    ):
        group_runs.sort(
            key=lambda item: (
                int(item["schedule"]["evaluatedAt"])
                if isinstance(item.get("schedule"), dict)
                else -1,
                len(item["creditInput"]["transactions"]),
                str(item["problemLedgerHead"]),
                str(item["runDigest"]),
            )
        )
        try:
            ordered_group = ordered_credit_runs(group_runs)
        except MathFlowError:
            ordered_group = []
        if ordered_group:
            latest = ordered_group[-1]
            selection_status = "current" if latest["stale"] is False else "historical"
        elif group_runs:
            latest = None
            selection_status = "ambiguous"
        else:
            latest = None
            selection_status = "pending"
        registered = projection_specs.get(projection_digest)
        if registered is not None and registered.get("engine") != "overlay-repository-v1":
            raise MathFlowError(
                f"viewer credit assignment uses a non-overlay projection: {projection_id}"
            )
        catalog_id = (
            projection_id
            if projection_id_counts[projection_id] == 1
            else f"{projection_id}@{projection_digest}"
        )
        declared_dependency_ids = {
            str(knowledge_projection["id"])
            for knowledge_projection in projections
            if knowledge_projection["problemId"] == problem
            and isinstance(knowledge_projection.get("projectionSpec"), dict)
            and registered is not None
            and any(
                isinstance(dependency, dict)
                and dependency.get("artifactRole") == "knowledge-state"
                and dependency.get("projectionId")
                == knowledge_projection["projectionSpec"].get("id")
                for dependency in registered.get("dependencies", [])
            )
        }
        credit_projections.append(
            {
                "id": catalog_id,
                "problemId": problem,
                "label": projection_id,
                "projectionSpec": registered,
                "knowledgeProjectionIds": sorted(
                    {
                        knowledge_projection_id
                        for item in group_runs
                        for knowledge_projection_id in item["knowledgeProjectionIds"]
                    }
                    | declared_dependency_ids
                ),
                "latestRunDigest": latest["runDigest"] if latest else None,
                "selectionStatus": selection_status,
                "runCount": len(group_runs),
                "runs": group_runs,
            }
        )

    credit_projections.sort(
        key=lambda item: (str(item["problemId"]), str(item["label"]), str(item["id"]))
    )
    direction_ledgers = [
        research_direction_ledger(root, problem, canonical_ref)
        for problem in sorted(
            {str(projection["problemId"]) for projection in projections}
        )
    ]
    objective_attestations = _viewer_objective_attestations(
        root,
        published_objects,
        sorted({str(projection["problemId"]) for projection in projections}),
        canonical_ref,
    )
    return {
        "schemaVersion": 1,
        "repository": {
            "slug": repository,
            "canonicalRef": canonical_ref,
            "projectionRef": projection_ref,
        },
        "projections": projections,
        "creditProjections": credit_projections,
        "researchDirections": direction_ledgers,
        "objectiveAttestations": objective_attestations,
        "defaultProjectionId": projections[0]["id"] if projections else None,
    }
