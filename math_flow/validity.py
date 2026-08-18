from __future__ import annotations

import json
import re
from pathlib import Path

from .artifacts import read_verified_artifact, verify_bundle
from .claims import CLAIM_KEY, validate_claim_manifest
from .coordination import load_scheduler
from .errors import MathFlowError
from .governance import resolve_projection
from .projection_queue import validate_scheduler_state
from .repository import is_ancestor, list_files_at, read_at, sha256_json
from .research_state import validate_research_program_state


TRANSACTION_ID = re.compile(r"\b[0-9a-f]{40}\b")
CLAIM_HEADINGS = {
    "claim",
    "claims",
    "claim and scope",
    "claims and exact scope",
}


def _legacy_claim_section(readme: str) -> str:
    lines = readme.splitlines()
    start: int | None = None
    for index, line in enumerate(lines):
        if not line.startswith("## "):
            continue
        heading = line[3:].strip().lower()
        if heading in CLAIM_HEADINGS:
            start = index + 1
            break
    if start is None:
        return readme.strip()
    end = len(lines)
    for index in range(start, len(lines)):
        if lines[index].startswith("## "):
            end = index
            break
    section = "\n".join(lines[start:end]).strip()
    return section or readme.strip()


def contribution_claims(
    root: Path,
    problem: str,
    source: dict[str, object],
    head: str,
    subject_transaction_id: str,
) -> list[dict[str, object]]:
    transactions = list(source["transactions"])
    by_id = {str(item["transactionId"]): item for item in transactions}
    subject = by_id.get(subject_transaction_id)
    if subject is None:
        raise MathFlowError("validity subject is outside the canonical problem ledger")
    subject_ordinal = int(subject["ordinal"])
    prior = {
        str(item["transactionId"]): item
        for item in transactions
        if int(item["ordinal"]) < subject_ordinal
    }
    content_head = "WORKTREE" if head == "WORKTREE" else subject_transaction_id
    contribution_path = str(subject["path"])
    files = set(list_files_at(root, content_head, contribution_path))
    manifest_path = f"{contribution_path}/claims.json"
    if manifest_path in files:
        try:
            value = json.loads(read_at(root, content_head, manifest_path))
        except json.JSONDecodeError as exc:
            raise MathFlowError("contribution claims manifest is not valid JSON") from exc
        return validate_claim_manifest(
            value,
            problem=problem,
            subject_transaction_id=subject_transaction_id,
            prior_transaction_ids=set(prior),
        )

    readme = read_at(root, content_head, f"{contribution_path}/README.md")
    statement = _legacy_claim_section(readme)
    contribution_id = str(subject["contributionId"])
    cited = [
        transaction_id
        for transaction_id in dict.fromkeys(TRANSACTION_ID.findall(statement))
        if transaction_id in prior
    ]
    return [
        {
            "claimKey": f"{problem}/{contribution_id}",
            "statement": statement,
            "dependencyTransactionIds": cited,
        }
    ]


def _run_bundle(projection_root: Path, run_digest: str) -> Path:
    if not re.fullmatch(r"sha256:[0-9a-f]{64}", run_digest):
        raise MathFlowError("knowledge context run digest is invalid")
    digest = run_digest.removeprefix("sha256:")
    return projection_root / "objects" / "knowledge-build" / digest[:2] / digest


def _historical_context(
    root: Path,
    projection_root: Path,
    problem: str,
    projection_id: str,
    head: str,
    source: dict[str, object],
    subject_ordinal: int,
) -> dict[str, object] | None:
    projection = resolve_projection(root, projection_id, problem, head)
    projection_digest = str(projection["projectionSpecDigest"])
    scheduler_path = projection_root / "coordination" / "scheduler.json"
    if not scheduler_path.is_file():
        return None
    scheduler = validate_scheduler_state(load_scheduler(scheduler_path))
    lanes = [
        lane
        for lane in scheduler["lanes"].values()
        if lane.get("problemId") == problem
        and lane.get("projectionSpecDigest") == projection_digest
    ]
    if len(lanes) > 1:
        raise MathFlowError("knowledge context projection resolves to multiple lanes")
    if not lanes or not isinstance(lanes[0].get("latestStateRun"), str):
        return None
    transaction_ordinals = {
        str(item["transactionId"]): int(item["ordinal"])
        for item in source["transactions"]
    }
    run_digest: str | None = str(lanes[0]["latestStateRun"])
    visited: set[str] = set()
    while run_digest is not None:
        if run_digest in visited:
            raise MathFlowError("knowledge context base-run chain contains a cycle")
        visited.add(run_digest)
        bundle = _run_bundle(projection_root, run_digest)
        manifest, actual_digest = verify_bundle(bundle)
        if actual_digest != run_digest:
            raise MathFlowError("knowledge context bundle does not match its content address")
        inputs = manifest.get("inputs")
        if (
            manifest.get("runKind") != "knowledge-build"
            or manifest.get("problemId") != problem
            or not isinstance(inputs, dict)
            or inputs.get("projectionSpecDigest") != projection_digest
        ):
            raise MathFlowError("knowledge context bundle does not match its projection")
        problem_ledger_head = manifest.get("problemLedgerHead")
        if not isinstance(problem_ledger_head, str):
            raise MathFlowError("knowledge context bundle has no problem-ledger head")
        ordinal = transaction_ordinals.get(problem_ledger_head)
        if ordinal is not None and ordinal < subject_ordinal:
            if head != "WORKTREE" and not is_ancestor(
                root, str(manifest["ledgerHead"]), str(source["ledgerHead"])
            ):
                raise MathFlowError("knowledge context is outside canonical history")
            try:
                state = json.loads(
                    read_verified_artifact(bundle, manifest, "knowledge-state")
                )
            except json.JSONDecodeError as exc:
                raise MathFlowError("knowledge context state is not valid JSON") from exc
            if not isinstance(state, dict) or not isinstance(state.get("nodes"), dict):
                raise MathFlowError("knowledge context state has an invalid node map")
            state_artifacts = [
                item
                for item in manifest["artifacts"]
                if isinstance(item, dict) and item.get("role") == "knowledge-state"
            ]
            if len(state_artifacts) != 1:
                raise MathFlowError("knowledge context bundle has no unique state artifact")
            state_artifact = state_artifacts[0]
            return {
                "projectionId": projection_id,
                "projectionSpecDigest": projection_digest,
                "runDigest": run_digest,
                "stateDigest": state.get("stateDigest"),
                "stateArtifactDigest": state_artifact["digest"],
                "problemLedgerHead": problem_ledger_head,
                "state": state,
            }
        base_run = manifest.get("baseRun")
        run_digest = str(base_run) if isinstance(base_run, str) else None
    return None


def research_state_dependency_context(
    bundle_dir: Path,
    problem: str,
    source: dict[str, object],
    subject_ordinal: int,
    dependencies: list[str],
) -> dict[str, object]:
    manifest, run_digest = verify_bundle(bundle_dir)
    if (
        manifest.get("runKind") != "research-update"
        or manifest.get("problemId") != problem
    ):
        raise MathFlowError("validity research-state context is not a research update")
    try:
        state = json.loads(
            read_verified_artifact(bundle_dir, manifest, "research-program-state")
        )
    except json.JSONDecodeError as exc:
        raise MathFlowError("validity research-state context is invalid JSON") from exc
    validate_research_program_state(state, problem)
    transaction_ordinals = {
        str(item["transactionId"]): int(item["ordinal"])
        for item in source["transactions"]
    }
    state_head = state.get("ledgerHead")
    if (
        not isinstance(state_head, str)
        or transaction_ordinals.get(state_head, subject_ordinal) >= subject_ordinal
    ):
        raise MathFlowError("validity research-state context is not pre-subject")
    state_artifacts = [
        item
        for item in manifest.get("artifacts", [])
        if isinstance(item, dict) and item.get("role") == "research-program-state"
    ]
    if len(state_artifacts) != 1:
        raise MathFlowError("validity research-state context has no unique state artifact")

    selected_contributions = {
        transaction_id: state["contributions"][transaction_id]
        for transaction_id in dependencies
        if transaction_id in state["contributions"]
    }
    selected_item_ids = {
        str(item_id)
        for contribution in selected_contributions.values()
        for item_id in contribution.get("itemIds", [])
    }
    frontier = list(selected_item_ids)
    while frontier:
        item_id = frontier.pop()
        item = state["items"].get(item_id)
        if not isinstance(item, dict):
            continue
        for dependency_item_id in item.get("dependencyItemIds", []):
            dependency_item_id = str(dependency_item_id)
            if dependency_item_id not in selected_item_ids:
                selected_item_ids.add(dependency_item_id)
                frontier.append(dependency_item_id)
    selected_items = {
        item_id: state["items"][item_id]
        for item_id in sorted(selected_item_ids)
        if item_id in state["items"]
    }
    selected_program_ids = {
        str(contribution["directProgramId"])
        for contribution in selected_contributions.values()
    } | {str(item["programId"]) for item in selected_items.values()}
    for program_id in list(selected_program_ids):
        cursor = state["programs"].get(program_id)
        while isinstance(cursor, dict) and isinstance(cursor.get("parentId"), str):
            parent_id = str(cursor["parentId"])
            selected_program_ids.add(parent_id)
            cursor = state["programs"].get(parent_id)
    selected_threads = {
        thread_id: state["threads"][thread_id]
        for contribution in selected_contributions.values()
        for thread_id in contribution.get("directThreadIds", [])
        if thread_id in state["threads"]
    }
    return {
        "sourceKind": "research-program-state",
        "runDigest": run_digest,
        "stateDigest": state["stateDigest"],
        "stateArtifactDigest": state_artifacts[0]["digest"],
        "problemLedgerHead": state_head,
        "selectedPrograms": {
            program_id: state["programs"][program_id]
            for program_id in sorted(selected_program_ids)
            if program_id in state["programs"]
        },
        "selectedThreads": selected_threads,
        "selectedItems": selected_items,
        "unresolvedDependencyTransactionIds": sorted(
            set(dependencies) - set(selected_contributions)
        ),
    }


def build_dependency_packet(
    root: Path,
    projection_root: Path | None,
    problem: str,
    source: dict[str, object],
    head: str,
    subject_transaction_id: str,
    context_projection: str | None,
    research_state_run: Path | None = None,
) -> dict[str, object]:
    transactions = list(source["transactions"])
    by_id = {str(item["transactionId"]): item for item in transactions}
    subject = by_id.get(subject_transaction_id)
    if subject is None:
        raise MathFlowError("validity subject is outside the canonical problem ledger")
    claims = contribution_claims(
        root, problem, source, head, subject_transaction_id
    )
    dependencies = list(
        dict.fromkeys(
            transaction_id
            for claim in claims
            for transaction_id in claim["dependencyTransactionIds"]
        )
    )
    context = None
    if research_state_run is not None and dependencies:
        context = research_state_dependency_context(
            research_state_run,
            problem,
            source,
            int(subject["ordinal"]),
            dependencies,
        )
    elif context_projection is not None and dependencies and projection_root is not None:
        historical = _historical_context(
            root,
            projection_root.resolve(),
            problem,
            context_projection,
            head,
            source,
            int(subject["ordinal"]),
        )
        if historical is not None:
            nodes = historical.pop("state")["nodes"]
            selected: dict[str, object] = {}
            for node_id, node in nodes.items():
                if node_id == "root" or not isinstance(node, dict):
                    continue
                references = [
                    reference
                    for field in ("subjects", "evidence")
                    for reference in (
                        node.get(field) if isinstance(node.get(field), list) else []
                    )
                    if isinstance(reference, dict)
                ]
                if any(reference.get("id") in dependencies for reference in references):
                    selected[str(node_id)] = node
            represented = {
                str(reference["id"])
                for node in selected.values()
                if isinstance(node, dict)
                for field in ("subjects", "evidence")
                for reference in (
                    node.get(field) if isinstance(node.get(field), list) else []
                )
                if isinstance(reference, dict)
                and reference.get("id") in dependencies
            }
            context = {
                **historical,
                "selectedNodes": selected,
                "unresolvedDependencyTransactionIds": sorted(
                    set(dependencies) - represented
                ),
            }
    core = {
        "schemaVersion": 1,
        "problemId": problem,
        "subjectTransactionId": subject_transaction_id,
        "subjectLedgerPosition": int(subject["ordinal"]),
        "claims": claims,
        "dependencyTransactionIds": dependencies,
        "knowledgeContext": context,
    }
    return {**core, "packetDigest": f"sha256:{sha256_json(core)}"}


def validate_dependency_packet(value: object) -> dict[str, object]:
    required = {
        "schemaVersion",
        "problemId",
        "subjectTransactionId",
        "subjectLedgerPosition",
        "claims",
        "dependencyTransactionIds",
        "knowledgeContext",
        "packetDigest",
    }
    if not isinstance(value, dict) or set(value) != required:
        raise MathFlowError("validity dependency packet has an invalid envelope")
    core = {key: value[key] for key in required if key != "packetDigest"}
    if (
        value.get("schemaVersion") != 1
        or not isinstance(value.get("problemId"), str)
        or not isinstance(value.get("subjectTransactionId"), str)
        or not isinstance(value.get("subjectLedgerPosition"), int)
        or not isinstance(value.get("claims"), list)
        or not value.get("claims")
        or not isinstance(value.get("dependencyTransactionIds"), list)
        or any(
            not isinstance(item, str)
            for item in value.get("dependencyTransactionIds", [])
        )
        or len(value.get("dependencyTransactionIds", []))
        != len(set(value.get("dependencyTransactionIds", [])))
        or value.get("packetDigest") != f"sha256:{sha256_json(core)}"
    ):
        raise MathFlowError("validity dependency packet digest is invalid")
    dependencies = set(value["dependencyTransactionIds"])
    claim_keys: set[str] = set()
    claimed_dependencies: set[str] = set()
    for claim in value["claims"]:
        if (
            not isinstance(claim, dict)
            or set(claim)
            != {"claimKey", "statement", "dependencyTransactionIds"}
            or not isinstance(claim.get("claimKey"), str)
            or not CLAIM_KEY.fullmatch(str(claim.get("claimKey")))
            or not isinstance(claim.get("statement"), str)
            or not str(claim.get("statement")).strip()
            or not isinstance(claim.get("dependencyTransactionIds"), list)
            or any(
                not isinstance(item, str)
                for item in claim.get("dependencyTransactionIds", [])
            )
            or not set(claim.get("dependencyTransactionIds", [])) <= dependencies
        ):
            raise MathFlowError("validity dependency packet contains an invalid claim")
        claim_key = str(claim["claimKey"])
        if claim_key in claim_keys:
            raise MathFlowError("validity dependency packet repeats a claim key")
        claim_keys.add(claim_key)
        claimed_dependencies.update(claim["dependencyTransactionIds"])
    if dependencies != claimed_dependencies:
        raise MathFlowError(
            "validity dependency packet contains dependencies not declared by a claim"
        )
    context = value.get("knowledgeContext")
    if context is not None:
        legacy_context_fields = {
            "projectionId",
            "projectionSpecDigest",
            "runDigest",
            "stateDigest",
            "stateArtifactDigest",
            "problemLedgerHead",
            "selectedNodes",
            "unresolvedDependencyTransactionIds",
        }
        research_context_fields = {
            "sourceKind",
            "runDigest",
            "stateDigest",
            "stateArtifactDigest",
            "problemLedgerHead",
            "selectedPrograms",
            "selectedThreads",
            "selectedItems",
            "unresolvedDependencyTransactionIds",
        }
        if (
            not isinstance(context, dict)
            or (
                set(context) != legacy_context_fields
                and set(context) != research_context_fields
            )
        ):
            raise MathFlowError("validity dependency packet has invalid knowledge context")
    return value
