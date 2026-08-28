from __future__ import annotations

import json
import re
from pathlib import Path

from .artifacts import read_verified_artifact, verify_bundle
from .attestations import objective_attestation_status
from .claims import CLAIM_KEY, validate_claim_manifest
from .coordination import load_scheduler
from .errors import MathFlowError
from .governance import resolve_projection
from .projection_queue import validate_scheduler_state
from .repository import is_ancestor, list_files_at, read_at, sha256_json
from .research_state import (
    validate_research_program_v5_batch_binding,
)
from .research_topology import validate_research_program_state_versioned


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
            state_artifacts = [
                item
                for item in manifest["artifacts"]
                if isinstance(item, dict)
                and item.get("role")
                in {"knowledge-state", "research-program-state"}
            ]
            if len(state_artifacts) != 1:
                raise MathFlowError("knowledge context bundle has no unique state artifact")
            state_artifact = state_artifacts[0]
            role = state_artifact["role"]
            try:
                state = json.loads(read_verified_artifact(bundle, manifest, str(role)))
            except json.JSONDecodeError as exc:
                raise MathFlowError("knowledge context state is not valid JSON") from exc
            if role == "research-program-state":
                validate_research_program_state_versioned(state, problem)
                source_kind = "research-program-state"
            else:
                if not isinstance(state, dict) or not isinstance(
                    state.get("nodes"), dict
                ):
                    raise MathFlowError("knowledge context state has an invalid node map")
                source_kind = "knowledge-state"
            return {
                "projectionId": projection_id,
                "projectionSpecDigest": projection_digest,
                "runDigest": run_digest,
                "stateDigest": state.get("stateDigest"),
                "stateArtifactDigest": state_artifact["digest"],
                "problemLedgerHead": problem_ledger_head,
                "sourceKind": source_kind,
                "state": state,
            }
        base_run = manifest.get("baseRun")
        run_digest = str(base_run) if isinstance(base_run, str) else None
    return None


def _selected_research_state_context(
    state: dict[str, object],
    dependencies: list[str],
    *,
    run_digest: str,
    state_artifact_digest: str,
    problem_ledger_head: str,
) -> dict[str, object]:
    if state.get("schemaVersion") == 3:
        selected_contributions = {
            transaction_id: state["contributions"][transaction_id]
            for transaction_id in dependencies
            if transaction_id in state["contributions"]
        }
        selected_result_ids = {
            str(result_id)
            for contribution in selected_contributions.values()
            for result_id in contribution.get("intermediateResultIds", [])
        }
        frontier = list(selected_result_ids)
        while frontier:
            result_id = frontier.pop()
            result = state["intermediateResults"].get(result_id)
            if not isinstance(result, dict):
                continue
            for dependency_result_id in result.get("dependencyResultIds", []):
                dependency_result_id = str(dependency_result_id)
                if dependency_result_id not in selected_result_ids:
                    selected_result_ids.add(dependency_result_id)
                    frontier.append(dependency_result_id)
        selected_results = {
            result_id: state["intermediateResults"][result_id]
            for result_id in sorted(selected_result_ids)
            if result_id in state["intermediateResults"]
        }
        selected_program_ids = {
            str(program_id)
            for contribution in selected_contributions.values()
            for program_id in contribution.get("directProgramIds", [])
        }
        for result in selected_results.values():
            selected_program_ids.add(str(result["primaryProgramId"]))
            selected_program_ids.update(
                str(program_id) for program_id in result.get("relatedProgramIds", [])
            )
        for program_id in list(selected_program_ids):
            cursor = state["programs"].get(program_id)
            while isinstance(cursor, dict) and isinstance(cursor.get("parentId"), str):
                parent_id = str(cursor["parentId"])
                selected_program_ids.add(parent_id)
                cursor = state["programs"].get(parent_id)
        return {
            "sourceKind": "research-program-state",
            "runDigest": run_digest,
            "stateDigest": state["stateDigest"],
            "stateArtifactDigest": state_artifact_digest,
            "problemLedgerHead": problem_ledger_head,
            "selectedPrograms": {
                program_id: state["programs"][program_id]
                for program_id in sorted(selected_program_ids)
                if program_id in state["programs"]
            },
            "selectedIntermediateResults": selected_results,
            "unresolvedDependencyTransactionIds": sorted(
                set(dependencies) - set(selected_contributions)
            ),
        }

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
        "stateArtifactDigest": state_artifact_digest,
        "problemLedgerHead": problem_ledger_head,
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


def research_state_dependency_context(
    bundle_dir: Path,
    problem: str,
    source: dict[str, object],
    subject_ordinal: int,
    dependencies: list[str],
) -> dict[str, object]:
    manifest, run_digest = verify_bundle(bundle_dir)
    if (
        manifest.get("runKind") not in {"research-update", "knowledge-build"}
        or manifest.get("problemId") != problem
    ):
        raise MathFlowError("validity research-state context is not a research state run")
    try:
        state = json.loads(
            read_verified_artifact(bundle_dir, manifest, "research-program-state")
        )
        if manifest.get("outputProfile") == "math-flow/hierarchical-research-v5":
            delta = json.loads(
                read_verified_artifact(
                    bundle_dir, manifest, "research-program-delta"
                )
            )
            batch_input = json.loads(
                read_verified_artifact(bundle_dir, manifest, "research-batch-input")
            )
        else:
            delta = None
            batch_input = None
    except json.JSONDecodeError as exc:
        raise MathFlowError("validity research-state context is invalid JSON") from exc
    validate_research_program_state_versioned(state, problem)
    transaction_ordinals = {
        str(item["transactionId"]): int(item["ordinal"])
        for item in source["transactions"]
    }
    context_head = manifest.get("problemLedgerHead")
    if (
        not isinstance(context_head, str)
        or transaction_ordinals.get(context_head, subject_ordinal) >= subject_ordinal
    ):
        raise MathFlowError("validity research-state context is not pre-subject")
    if delta is not None:
        validate_research_program_v5_batch_binding(
            batch_input,
            delta,
            state,
            problem,
            problem_ledger_head=context_head,
        )
    state_artifacts = [
        item
        for item in manifest.get("artifacts", [])
        if isinstance(item, dict) and item.get("role") == "research-program-state"
    ]
    if len(state_artifacts) != 1:
        raise MathFlowError("validity research-state context has no unique state artifact")
    return _selected_research_state_context(
        state,
        dependencies,
        run_digest=run_digest,
        state_artifact_digest=str(state_artifacts[0]["digest"]),
        problem_ledger_head=context_head,
    )


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
            historical_state = historical.pop("state")
            source_kind = historical.pop("sourceKind")
            if source_kind == "research-program-state":
                context = _selected_research_state_context(
                    historical_state,
                    dependencies,
                    run_digest=str(historical["runDigest"]),
                    state_artifact_digest=str(historical["stateArtifactDigest"]),
                    problem_ledger_head=str(historical["problemLedgerHead"]),
                )
            else:
                nodes = historical_state["nodes"]
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


def build_evidence_packet_v3(
    root: Path,
    projection_root: Path | None,
    problem: str,
    source: dict[str, object],
    head: str,
    subject_transaction_id: str,
    context_projection: str | None,
    research_state_run: Path | None = None,
) -> dict[str, object]:
    """Build the v3 validity packet with references and terminal attestations.

    V2 treated every transaction mentioned by the legacy claim extractor as a
    formation dependency.  V3 deliberately calls these *declared references*;
    the validity assessment separately records which of them are actually
    required premises.  This preserves citation provenance without importing a
    rejected referenced submission into accepted research state.
    """

    v2_packet = build_dependency_packet(
        root,
        projection_root,
        problem,
        source,
        head,
        subject_transaction_id,
        context_projection,
        research_state_run,
    )
    references = list(v2_packet["dependencyTransactionIds"])
    claims = [
        {
            "claimKey": claim["claimKey"],
            "statement": claim["statement"],
            "declaredReferenceTransactionIds": list(
                claim["dependencyTransactionIds"]
            ),
        }
        for claim in v2_packet["claims"]
    ]
    if projection_root is None:
        transactions = {
            str(item["transactionId"]): item for item in source["transactions"]
        }
        subject = transactions[subject_transaction_id]
        prefix = str(subject["path"])
        files = set(list_files_at(root, subject_transaction_id, prefix))
        if f"{prefix}/verification.json" in files:
            raise MathFlowError(
                "validity-v3 judgment requires projection state for objective attestation evidence"
            )
        attestation = None
    else:
        status = objective_attestation_status(
            root,
            projection_root,
            problem,
            subject_transaction_id,
            head,
        )
        if status["requested"] and not status["terminal"]:
            raise MathFlowError(
                "validity-v3 judgment is deferred until objective attestation is terminal"
            )
        attestation = status["evidence"]
    core = {
        "schemaVersion": 2,
        "problemId": problem,
        "subjectTransactionId": subject_transaction_id,
        "subjectLedgerPosition": v2_packet["subjectLedgerPosition"],
        "claims": claims,
        "declaredReferenceTransactionIds": references,
        "knowledgeContext": v2_packet["knowledgeContext"],
        "objectiveAttestation": attestation,
    }
    return {**core, "packetDigest": f"sha256:{sha256_json(core)}"}


def build_evidence_packet_v4(
    root: Path,
    projection_root: Path | None,
    problem: str,
    source: dict[str, object],
    head: str,
    subject_transaction_id: str,
    context_projection: str | None,
    research_state_run: Path | None = None,
) -> dict[str, object]:
    """Build bounded validity evidence with terminal attestations for references.

    V4 preserves v3's declared-reference versus required-premise boundary.  It
    additionally resolves objective evidence for the subject and for exactly
    the transactions declared by its claims.  It never scans unrelated ledger
    entries for judgment evidence.
    """

    v2_packet = build_dependency_packet(
        root,
        projection_root,
        problem,
        source,
        head,
        subject_transaction_id,
        context_projection,
        research_state_run,
    )
    references = list(v2_packet["dependencyTransactionIds"])
    claims = [
        {
            "claimKey": claim["claimKey"],
            "statement": claim["statement"],
            "declaredReferenceTransactionIds": list(
                claim["dependencyTransactionIds"]
            ),
        }
        for claim in v2_packet["claims"]
    ]
    scoped_transactions = [
        (subject_transaction_id, "subject"),
        *((transaction_id, "declared-reference") for transaction_id in references),
    ]
    attestations: list[dict[str, object]] = []
    if projection_root is None:
        transactions = {
            str(item["transactionId"]): item for item in source["transactions"]
        }
        for transaction_id, relation in scoped_transactions:
            transaction = transactions[transaction_id]
            prefix = str(transaction["path"])
            content_head = (
                "WORKTREE"
                if head == "WORKTREE" and transaction_id == subject_transaction_id
                else transaction_id
            )
            files = set(list_files_at(root, content_head, prefix))
            if f"{prefix}/verification.json" in files:
                raise MathFlowError(
                    "validity-v4 judgment requires projection state for objective "
                    f"attestation evidence: {relation} {transaction_id}"
                )
    else:
        for transaction_id, relation in scoped_transactions:
            status = objective_attestation_status(
                root,
                projection_root,
                problem,
                transaction_id,
                head,
            )
            if status["requested"] and not status["terminal"]:
                raise MathFlowError(
                    "validity-v4 judgment is deferred until objective attestation "
                    f"is terminal: {relation} {transaction_id}"
                )
            evidence = status["evidence"]
            if evidence is not None:
                attestations.append(
                    {
                        "transactionId": transaction_id,
                        "relation": relation,
                        "attestation": evidence,
                    }
                )
    core = {
        "schemaVersion": 3,
        "problemId": problem,
        "subjectTransactionId": subject_transaction_id,
        "subjectLedgerPosition": v2_packet["subjectLedgerPosition"],
        "claims": claims,
        "declaredReferenceTransactionIds": references,
        "knowledgeContext": v2_packet["knowledgeContext"],
        "objectiveAttestations": attestations,
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


def validate_evidence_packet_v3(value: object) -> dict[str, object]:
    required = {
        "schemaVersion",
        "problemId",
        "subjectTransactionId",
        "subjectLedgerPosition",
        "claims",
        "declaredReferenceTransactionIds",
        "knowledgeContext",
        "objectiveAttestation",
        "packetDigest",
    }
    if not isinstance(value, dict) or set(value) != required:
        raise MathFlowError("validity-v3 evidence packet has an invalid envelope")
    core = {key: value[key] for key in required if key != "packetDigest"}
    references = value.get("declaredReferenceTransactionIds")
    if (
        value.get("schemaVersion") != 2
        or not isinstance(value.get("problemId"), str)
        or not isinstance(value.get("subjectTransactionId"), str)
        or not re.fullmatch(r"[0-9a-f]{40}", str(value.get("subjectTransactionId")))
        or not isinstance(value.get("subjectLedgerPosition"), int)
        or not isinstance(references, list)
        or any(
            not isinstance(item, str) or not re.fullmatch(r"[0-9a-f]{40}", item)
            for item in references
        )
        or len(references) != len(set(references))
        or value.get("packetDigest") != f"sha256:{sha256_json(core)}"
    ):
        raise MathFlowError("validity-v3 evidence packet digest is invalid")
    claims = value.get("claims")
    if not isinstance(claims, list) or not claims:
        raise MathFlowError("validity-v3 evidence packet has no claims")
    declared: set[str] = set()
    claim_keys: set[str] = set()
    for claim in claims:
        if (
            not isinstance(claim, dict)
            or set(claim)
            != {
                "claimKey",
                "statement",
                "declaredReferenceTransactionIds",
            }
            or not isinstance(claim.get("claimKey"), str)
            or not CLAIM_KEY.fullmatch(str(claim.get("claimKey")))
            or not isinstance(claim.get("statement"), str)
            or not str(claim.get("statement")).strip()
            or not isinstance(claim.get("declaredReferenceTransactionIds"), list)
            or any(
                not isinstance(item, str) or item not in references
                for item in claim.get("declaredReferenceTransactionIds", [])
            )
            or len(claim.get("declaredReferenceTransactionIds", []))
            != len(set(claim.get("declaredReferenceTransactionIds", [])))
        ):
            raise MathFlowError("validity-v3 evidence packet contains an invalid claim")
        claim_key = str(claim["claimKey"])
        if claim_key in claim_keys:
            raise MathFlowError("validity-v3 evidence packet repeats a claim key")
        claim_keys.add(claim_key)
        declared.update(claim["declaredReferenceTransactionIds"])
    if declared != set(references):
        raise MathFlowError(
            "validity-v3 evidence packet contains undeclared references"
        )
    # Reuse the v2 context shape validator without changing its published
    # packet semantics.
    context = value.get("knowledgeContext")
    if context is not None:
        synthetic = {
            "schemaVersion": 1,
            "problemId": value["problemId"],
            "subjectTransactionId": value["subjectTransactionId"],
            "subjectLedgerPosition": value["subjectLedgerPosition"],
            "claims": [
                {
                    "claimKey": claim["claimKey"],
                    "statement": claim["statement"],
                    "dependencyTransactionIds": claim[
                        "declaredReferenceTransactionIds"
                    ],
                }
                for claim in claims
            ],
            "dependencyTransactionIds": references,
            "knowledgeContext": context,
        }
        synthetic["packetDigest"] = f"sha256:{sha256_json(synthetic)}"
        validate_dependency_packet(synthetic)
    attestation = value.get("objectiveAttestation")
    if attestation is not None:
        expected_fields = {
            "schemaVersion",
            "requestDigest",
            "runDigest",
            "attestationId",
            "status",
            "verifier",
            "environmentDigest",
            "result",
            "artifacts",
            "stdout",
            "stderr",
        }
        if (
            not isinstance(attestation, dict)
            or set(attestation) != expected_fields
            or attestation.get("schemaVersion") != 1
            or attestation.get("status") not in {"passed", "failed", "error"}
            or any(
                not isinstance(attestation.get(field), str)
                or not re.fullmatch(r"sha256:[0-9a-f]{64}", str(attestation[field]))
                for field in (
                    "requestDigest",
                    "runDigest",
                    "attestationId",
                    "environmentDigest",
                )
            )
            or not isinstance(attestation.get("verifier"), dict)
            or not isinstance(attestation.get("result"), dict)
            or not isinstance(attestation.get("artifacts"), dict)
            or not isinstance(attestation.get("stdout"), dict)
            or not isinstance(attestation.get("stderr"), dict)
        ):
            raise MathFlowError(
                "validity-v3 evidence packet has an invalid objective attestation"
            )
    return value


def validate_evidence_packet_v4(value: object) -> dict[str, object]:
    required = {
        "schemaVersion",
        "problemId",
        "subjectTransactionId",
        "subjectLedgerPosition",
        "claims",
        "declaredReferenceTransactionIds",
        "knowledgeContext",
        "objectiveAttestations",
        "packetDigest",
    }
    if not isinstance(value, dict) or set(value) != required:
        raise MathFlowError("validity-v4 evidence packet has an invalid envelope")
    core = {key: value[key] for key in required if key != "packetDigest"}
    if (
        value.get("schemaVersion") != 3
        or value.get("packetDigest") != f"sha256:{sha256_json(core)}"
    ):
        raise MathFlowError("validity-v4 evidence packet digest is invalid")

    # Reuse the frozen v3 validation for the unchanged claim, reference, and
    # bounded historical-context contract.
    v3_core = {
        "schemaVersion": 2,
        "problemId": value["problemId"],
        "subjectTransactionId": value["subjectTransactionId"],
        "subjectLedgerPosition": value["subjectLedgerPosition"],
        "claims": value["claims"],
        "declaredReferenceTransactionIds": value[
            "declaredReferenceTransactionIds"
        ],
        "knowledgeContext": value["knowledgeContext"],
        "objectiveAttestation": None,
    }
    validate_evidence_packet_v3(
        {**v3_core, "packetDigest": f"sha256:{sha256_json(v3_core)}"}
    )

    attestations = value.get("objectiveAttestations")
    if not isinstance(attestations, list):
        raise MathFlowError("validity-v4 evidence packet has invalid attestations")
    subject_id = str(value["subjectTransactionId"])
    references = list(value["declaredReferenceTransactionIds"])
    scoped_order = [subject_id, *references]
    seen: set[str] = set()
    actual_order: list[str] = []
    for entry in attestations:
        if (
            not isinstance(entry, dict)
            or set(entry) != {"transactionId", "relation", "attestation"}
            or not isinstance(entry.get("transactionId"), str)
        ):
            raise MathFlowError("validity-v4 evidence packet has invalid attestations")
        transaction_id = str(entry["transactionId"])
        expected_relation = (
            "subject"
            if transaction_id == subject_id
            else "declared-reference"
            if transaction_id in references
            else None
        )
        if (
            expected_relation is None
            or entry.get("relation") != expected_relation
            or transaction_id in seen
        ):
            raise MathFlowError("validity-v4 evidence packet has invalid attestations")
        attestation = entry.get("attestation")
        expected_fields = {
            "schemaVersion",
            "requestDigest",
            "runDigest",
            "attestationId",
            "status",
            "verifier",
            "environmentDigest",
            "result",
            "artifacts",
            "stdout",
            "stderr",
        }
        if (
            not isinstance(attestation, dict)
            or set(attestation) != expected_fields
            or attestation.get("schemaVersion") != 1
            or attestation.get("status") not in {"passed", "failed", "error"}
            or any(
                not isinstance(attestation.get(field), str)
                or not re.fullmatch(
                    r"sha256:[0-9a-f]{64}", str(attestation[field])
                )
                for field in (
                    "requestDigest",
                    "runDigest",
                    "attestationId",
                    "environmentDigest",
                )
            )
            or not isinstance(attestation.get("verifier"), dict)
            or not isinstance(attestation.get("result"), dict)
            or not isinstance(attestation.get("artifacts"), dict)
            or not isinstance(attestation.get("stdout"), dict)
            or not isinstance(attestation.get("stderr"), dict)
        ):
            raise MathFlowError("validity-v4 evidence packet has invalid attestations")
        seen.add(transaction_id)
        actual_order.append(transaction_id)
    if actual_order != [item for item in scoped_order if item in seen]:
        raise MathFlowError("validity-v4 evidence packet attestations are out of order")
    return value


def formation_dependency_transaction_ids(
    judgment: dict[str, object], packet: dict[str, object]
) -> list[str]:
    """Return only transaction prerequisites for accepted-state formation."""

    if packet.get("schemaVersion") == 1:
        dependencies = packet.get("dependencyTransactionIds")
        if not isinstance(dependencies, list) or any(
            not isinstance(item, str) for item in dependencies
        ):
            raise MathFlowError("validity dependency packet is invalid")
        return list(dict.fromkeys(dependencies))
    packet_version = packet.get("schemaVersion")
    if packet_version == 2:
        validate_evidence_packet_v3(packet)
    elif packet_version == 3:
        validate_evidence_packet_v4(packet)
    else:
        raise MathFlowError("validity evidence packet version is unsupported")
    assessments = judgment.get("assessments")
    if not isinstance(assessments, list):
        raise MathFlowError("validity-v3 judgment has invalid assessments")
    dependencies: list[str] = []
    for assessment in assessments:
        if not isinstance(assessment, dict) or assessment.get("status") != "valid":
            continue
        required = assessment.get("requiredDependencyTransactionIds")
        if not isinstance(required, list) or any(
            not isinstance(item, str) for item in required
        ):
            raise MathFlowError("validity-v3 assessment dependencies are invalid")
        dependencies.extend(required)
    return list(dict.fromkeys(dependencies))
