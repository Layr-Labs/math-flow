from __future__ import annotations

import json
import re
from pathlib import Path

from .artifacts import ArtifactBundle, read_verified_artifact, verify_bundle
from .credit_schedule import plan_credit_run, validate_credit_run_schedule
from .errors import MathFlowError
from .governance import resolve_projection
from .hierarchical import (
    _assistant_content,
    _provider_run,
    _request,
    _structured_content,
)
from .judges import artifact_evidence, load_judge_spec, load_source
from .knowledge import validate_state_v2, validate_state_v3
from .openrouter import OpenRouterTransport, send_chat_completion
from .projection_dependencies import resolve_projection_dependencies
from .repository import read_at, sha256_json
from .runs import run_envelope


SIGNIFICANCE = {
    "foundational",
    "major",
    "supporting",
    "minor",
    "none",
    "uncertain",
}
CREDIT_ROLES = {
    "direction-priority",
    "conjecture",
    "construction",
    "proof",
    "computation",
    "verification",
    "correction",
    "exposition",
    "other",
}
GIT_SHA = re.compile(r"^[0-9a-f]{40}$")


def _knowledge_bundle(
    projection_root: Path, dependency: dict[str, object]
) -> Path:
    run_digest = str(dependency["runDigest"])
    digest_hex = run_digest.removeprefix("sha256:")
    bundle = (
        projection_root.resolve()
        / "objects"
        / str(dependency["runKind"])
        / digest_hex[:2]
        / digest_hex
    )
    manifest, actual_digest = verify_bundle(bundle)
    if actual_digest != run_digest:
        raise MathFlowError("credit dependency bundle changed after lock resolution")
    artifact = dependency.get("artifact")
    if not isinstance(artifact, dict) or artifact.get("role") != "knowledge-state":
        raise MathFlowError("credit runner requires a locked knowledge-state artifact")
    if manifest.get("problemLedgerDigest") != dependency.get("problemLedgerDigest"):
        raise MathFlowError("credit dependency bundle does not match its locked ledger")
    return bundle


def _knowledge_state(
    projection_root: Path, dependency: dict[str, object], problem: str
) -> tuple[dict[str, object], list[dict[str, object]], str]:
    bundle = _knowledge_bundle(projection_root, dependency)
    manifest, _ = verify_bundle(bundle)
    try:
        state = json.loads(
            read_verified_artifact(bundle, manifest, "knowledge-state")
        )
    except json.JSONDecodeError as exc:
        raise MathFlowError("locked knowledge state is not valid JSON") from exc
    if (
        not isinstance(state, dict)
        or state.get("problemId") != problem
        or not isinstance(state.get("nodes"), dict)
    ):
        raise MathFlowError("locked knowledge state has an invalid problem or node index")
    output_profile = manifest.get("outputProfile")
    revision_role = (
        "knowledge-revisions"
        if output_profile == "math-flow/knowledge-build-markdown-v2"
        else "adjudication-revisions"
    )
    if output_profile not in {
        "math-flow/hierarchical-markdown-v2",
        "math-flow/knowledge-build-markdown-v1",
        "math-flow/knowledge-build-markdown-v2",
    }:
        raise MathFlowError("credit dependency uses an unsupported knowledge profile")
    try:
        revision_text = read_verified_artifact(
            bundle, manifest, revision_role
        ).decode("utf-8")
        revisions = [
            json.loads(line) for line in revision_text.splitlines() if line.strip()
        ]
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise MathFlowError("locked knowledge revisions are invalid JSON Lines") from exc
    if any(not isinstance(item, dict) for item in revisions):
        raise MathFlowError("locked knowledge revisions contain a non-object record")
    if output_profile == "math-flow/knowledge-build-markdown-v2":
        validate_state_v3(state, revisions, problem)
    else:
        validate_state_v2(state, revisions, problem)
    return state, revisions, str(output_profile)


def _current_revisions(state: dict[str, object]) -> dict[str, str | None]:
    revisions: dict[str, str | None] = {}
    for node_id, node in state["nodes"].items():
        if not isinstance(node_id, str) or not isinstance(node, dict):
            raise MathFlowError("locked knowledge state contains an invalid node")
        current = node.get("currentRevision", node.get("currentAdjudication"))
        if current is None:
            revision_id = None
        elif isinstance(current, dict) and isinstance(
            current.get("revisionId"), str
        ):
            revision_id = str(current["revisionId"])
        else:
            raise MathFlowError(
                f"locked knowledge node has an invalid current revision: {node_id}"
            )
        revisions[node_id] = revision_id
    return revisions


def _credit_schema(
    transaction_ids: list[str],
    node_revisions: dict[str, str | None],
    reservation_transaction_ids: list[str] | None = None,
) -> dict[str, object]:
    transaction: dict[str, object] = {
        "type": "string",
        "enum": transaction_ids,
    }
    reservation_transaction: dict[str, object] = {
        "type": "string",
        "enum": reservation_transaction_ids or transaction_ids,
    }
    node_ids = sorted(node_revisions)
    revision_ids = sorted(
        {value for value in node_revisions.values() if value is not None}
    )
    revision: dict[str, object] = {"type": ["string", "null"]}
    if revision_ids:
        revision["enum"] = [None, *revision_ids]
    knowledge_ref = {
        "type": "object",
        "properties": {
            "nodeId": {"type": "string", "enum": node_ids},
            "revisionId": revision,
        },
        "required": ["nodeId", "revisionId"],
        "additionalProperties": False,
    }
    assignment = {
        "type": "object",
        "properties": {
            "transactionId": transaction,
            "significance": {
                "type": "string",
                "enum": sorted(SIGNIFICANCE),
            },
            "roles": {
                "type": "array",
                "items": {"type": "string", "enum": sorted(CREDIT_ROLES)},
            },
            "knowledgeRefs": {"type": "array", "items": knowledge_ref},
            "reservationTransactionIds": {
                "type": "array",
                "items": reservation_transaction,
            },
        },
        "required": [
            "transactionId",
            "significance",
            "roles",
            "knowledgeRefs",
            "reservationTransactionIds",
        ],
        "additionalProperties": False,
    }
    return {
        "type": "object",
        "properties": {
            "assignments": {
                "type": "array",
                "minItems": len(transaction_ids),
                "maxItems": len(transaction_ids),
                "items": assignment,
            }
        },
        "required": ["assignments"],
        "additionalProperties": False,
    }


def _report_section(report: str, heading: str) -> str:
    lines = report.splitlines()
    matches = [index for index, line in enumerate(lines) if line.strip() == heading]
    if len(matches) != 1:
        raise MathFlowError(
            f"credit report section is missing or ambiguous: {heading}"
        )
    start = matches[0]
    end = len(lines)
    for index in range(start + 1, len(lines)):
        if lines[index].strip().startswith("## "):
            end = index
            break
    section = "\n".join(lines[start:end]).strip()
    if not "\n".join(section.splitlines()[1:]).strip():
        raise MathFlowError(f"credit report section is empty: {heading}")
    return section + "\n"


def _reject_truncated_response(
    response: dict[str, object], stage: str
) -> None:
    try:
        finish_reason = response["choices"][0].get("finish_reason")
    except (KeyError, IndexError, TypeError, AttributeError):
        return
    if finish_reason == "length":
        raise MathFlowError(f"OpenRouter credit {stage} response was truncated")


def _validate_credit_index(
    value: object,
    problem: str,
    dependency_lock_digest: str,
    transactions: list[dict[str, object]],
    node_revisions: dict[str, str | None],
    report: str,
    *,
    materialized: bool = False,
    assignment_transaction_ids: list[str] | None = None,
) -> dict[str, object]:
    if not isinstance(value, dict) or set(value) != {"assignments"}:
        raise MathFlowError("credit extractor returned an invalid assignments envelope")
    assignments = value["assignments"]
    canonical_transaction_ids = [str(item["transactionId"]) for item in transactions]
    transaction_ids = assignment_transaction_ids or canonical_transaction_ids
    if (
        len(transaction_ids) != len(set(transaction_ids))
        or any(item not in canonical_transaction_ids for item in transaction_ids)
    ):
        raise MathFlowError("credit assignment scope is not a canonical transaction subset")
    ordinals = {
        str(item["transactionId"]): int(item["ordinal"])
        for item in transactions
    }
    if not isinstance(assignments, list) or len(assignments) != len(transaction_ids):
        raise MathFlowError("credit extractor must return one assignment per transaction")
    by_transaction: dict[str, dict[str, object]] = {}
    expected_fields = {
        "transactionId",
        "significance",
        "roles",
        "knowledgeRefs",
        "reservationTransactionIds",
    }
    if materialized:
        expected_fields.add("reportSection")
    for assignment in assignments:
        if not isinstance(assignment, dict) or set(assignment) != expected_fields:
            raise MathFlowError("credit extractor returned an invalid assignment")
        transaction_id = assignment.get("transactionId")
        if (
            not isinstance(transaction_id, str)
            or transaction_id not in ordinals
            or transaction_id in by_transaction
        ):
            raise MathFlowError("credit extractor returned an invalid transaction ID")
        significance = assignment.get("significance")
        if not isinstance(significance, str) or significance not in SIGNIFICANCE:
            raise MathFlowError("credit extractor returned invalid significance")
        roles = assignment.get("roles")
        if (
            not isinstance(roles, list)
            or any(
                not isinstance(role, str) or role not in CREDIT_ROLES
                for role in roles
            )
            or roles != sorted(set(roles))
        ):
            raise MathFlowError("credit roles must be unique and sorted")
        refs = assignment.get("knowledgeRefs")
        if not isinstance(refs, list):
            raise MathFlowError("credit knowledge references must be an array")
        normalized_refs: list[tuple[str, str | None]] = []
        for reference in refs:
            if not isinstance(reference, dict) or set(reference) != {
                "nodeId",
                "revisionId",
            }:
                raise MathFlowError("credit assignment has an invalid knowledge reference")
            node_id = reference.get("nodeId")
            revision_id = reference.get("revisionId")
            if (
                not isinstance(node_id, str)
                or node_id not in node_revisions
                or revision_id != node_revisions[node_id]
            ):
                raise MathFlowError(
                    "credit assignment does not reference the locked current revision"
                )
            normalized_refs.append((node_id, revision_id))
        if normalized_refs != sorted(set(normalized_refs)):
            raise MathFlowError("credit knowledge references must be unique and sorted")
        reservations = assignment.get("reservationTransactionIds")
        if (
            not isinstance(reservations, list)
            or any(
                not isinstance(item, str) or item not in ordinals
                for item in reservations
            )
            or reservations != sorted(set(reservations), key=ordinals.get)
            or any(ordinals[item] > ordinals[transaction_id] for item in reservations)
        ):
            raise MathFlowError(
                "credit reservation references must be unique prior ledger transactions"
            )
        heading = f"## Contribution: {transaction_id}"
        if materialized and assignment.get("reportSection") != heading:
            raise MathFlowError(
                "credit assignment report section does not match its transaction"
            )
        _report_section(report, heading)
        by_transaction[transaction_id] = {
            **assignment,
            "reportSection": heading,
        }

    if set(by_transaction) != set(transaction_ids):
        raise MathFlowError("credit extractor omitted a canonical transaction")
    ordered = [by_transaction[transaction_id] for transaction_id in transaction_ids]
    return {
        "schemaVersion": 1,
        "problemId": problem,
        "dependencyLockDigest": dependency_lock_digest,
        "assignments": ordered,
    }


def load_credit_assignment_bundle(
    bundle_dir: Path,
) -> tuple[dict[str, object], dict[str, object], str]:
    """Verify a published/local credit bundle and its internal bindings."""

    manifest, run_digest = verify_bundle(bundle_dir)
    if (
        manifest.get("runKind") != "credit-assignment"
        or manifest.get("outputProfile")
        != "math-flow/credit-assignment-markdown-v1"
        or not isinstance(manifest.get("problemId"), str)
        or not isinstance(manifest.get("ledgerHead"), str)
        or not isinstance(manifest.get("problemLedgerHead"), str)
        or not isinstance(manifest.get("problemLedgerDigest"), str)
    ):
        raise MathFlowError("bundle is not a qualitative credit assignment")
    try:
        dependency_lock = json.loads(
            read_verified_artifact(bundle_dir, manifest, "dependency-lock")
        )
        credit_input = json.loads(
            read_verified_artifact(bundle_dir, manifest, "credit-input")
        )
        credit_index = json.loads(
            read_verified_artifact(bundle_dir, manifest, "credit-index")
        )
        report = read_verified_artifact(
            bundle_dir, manifest, "credit-report"
        ).decode("utf-8")
    except json.JSONDecodeError as exc:
        raise MathFlowError("credit bundle contains invalid JSON") from exc
    except UnicodeDecodeError as exc:
        raise MathFlowError("credit bundle report is not UTF-8") from exc
    if not isinstance(dependency_lock, dict):
        raise MathFlowError("credit bundle dependency lock must be an object")
    if set(dependency_lock) != {
        "schemaVersion",
        "consumer",
        "problemLedger",
        "dependencies",
        "dependencyLockDigest",
    } or dependency_lock.get("schemaVersion") != 1:
        raise MathFlowError("credit bundle dependency lock has an invalid envelope")
    lock_digest = dependency_lock.get("dependencyLockDigest")
    lock_core = {
        key: value
        for key, value in dependency_lock.items()
        if key != "dependencyLockDigest"
    }
    if lock_digest != f"sha256:{sha256_json(lock_core)}":
        raise MathFlowError("credit bundle dependency lock digest is invalid")
    consumer = dependency_lock.get("consumer")
    locked_ledger = dependency_lock.get("problemLedger")
    dependencies = dependency_lock.get("dependencies")
    if (
        not isinstance(consumer, dict)
        or set(consumer)
        != {
            "projectionId",
            "projectionSpecDigest",
            "problemId",
            "canonicalHead",
        }
        or not isinstance(locked_ledger, dict)
        or set(locked_ledger) != {"problemLedgerHead", "problemLedgerDigest"}
        or not isinstance(dependencies, list)
        or any(not isinstance(item, dict) for item in dependencies)
    ):
        raise MathFlowError("credit bundle dependency lock is malformed")
    if not isinstance(credit_input, dict):
        raise MathFlowError("credit bundle input must be an object")
    input_fields = {
        "schemaVersion",
        "problemId",
        "ledgerHead",
        "problemLedgerHead",
        "problemLedgerDigest",
        "creditProjection",
        "dependencyLockDigest",
        "transactions",
        "problemStatement",
        "contributionEvidence",
        "knowledgeState",
        "knowledgeRevisions",
        "knowledgeOutputProfile",
    }
    optional_input_fields = {"schedule"}
    transactions = credit_input.get("transactions")
    state = credit_input.get("knowledgeState")
    revisions = credit_input.get("knowledgeRevisions")
    knowledge_profile = credit_input.get("knowledgeOutputProfile")
    if (
        not input_fields <= set(credit_input)
        or not set(credit_input) <= input_fields | optional_input_fields
        or credit_input.get("schemaVersion") != 1
        or credit_input.get("problemId") != manifest.get("problemId")
        or credit_input.get("ledgerHead") != manifest.get("ledgerHead")
        or credit_input.get("problemLedgerHead")
        != manifest.get("problemLedgerHead")
        or credit_input.get("problemLedgerDigest")
        != manifest.get("problemLedgerDigest")
        or credit_input.get("dependencyLockDigest") != lock_digest
        or not isinstance(transactions, list)
        or any(not isinstance(item, dict) for item in transactions)
        or not isinstance(state, dict)
        or not isinstance(revisions, list)
        or any(not isinstance(item, dict) for item in revisions)
        or state.get("problemId") != manifest.get("problemId")
        or not isinstance(credit_input.get("problemStatement"), str)
        or not isinstance(credit_input.get("contributionEvidence"), str)
    ):
        raise MathFlowError("credit bundle input does not match its run manifest")
    if knowledge_profile == "math-flow/knowledge-build-markdown-v2":
        validate_state_v3(state, revisions, str(manifest["problemId"]))
    elif knowledge_profile in {
        "math-flow/hierarchical-markdown-v2",
        "math-flow/knowledge-build-markdown-v1",
    }:
        validate_state_v2(state, revisions, str(manifest["problemId"]))
    else:
        raise MathFlowError("credit bundle input has an unsupported knowledge profile")
    transaction_ids = [item.get("transactionId") for item in transactions]
    ordinals = [item.get("ordinal") for item in transactions]
    if (
        any(
            not isinstance(item, str) or not GIT_SHA.fullmatch(item)
            for item in transaction_ids
        )
        or len(transaction_ids) != len(set(transaction_ids))
        or any(
            not isinstance(item, int) or isinstance(item, bool)
            for item in ordinals
        )
        or ordinals != list(range(1, len(transactions) + 1))
    ):
        raise MathFlowError("credit bundle input has an invalid transaction ledger")
    for item in transactions:
        contribution_id = item.get("contributionId")
        author = item.get("author")
        if (
            set(item)
            != {"ordinal", "transactionId", "contributionId", "path", "author"}
            or not isinstance(contribution_id, str)
            or item.get("path")
            != f"problems/{manifest['problemId']}/contributions/{contribution_id}"
            or not isinstance(author, dict)
            or set(author) != {"displayName", "email"}
            or not isinstance(author.get("displayName"), str)
            or not isinstance(author.get("email"), str)
        ):
            raise MathFlowError("credit bundle input has invalid transaction metadata")
    projection = credit_input.get("creditProjection")
    manifest_inputs = manifest.get("inputs")
    raw_schedule = credit_input.get("schedule")
    schedule = (
        validate_credit_run_schedule(raw_schedule)
        if raw_schedule is not None
        else None
    )
    if (
        not isinstance(projection, dict)
        or set(projection) != {"projectionId", "projectionSpecDigest"}
        or consumer.get("projectionId") != projection.get("projectionId")
        or consumer.get("projectionSpecDigest")
        != projection.get("projectionSpecDigest")
        or consumer.get("problemId") != manifest.get("problemId")
        or consumer.get("canonicalHead") != manifest.get("ledgerHead")
        or locked_ledger.get("problemLedgerHead")
        != manifest.get("problemLedgerHead")
        or locked_ledger.get("problemLedgerDigest")
        != manifest.get("problemLedgerDigest")
        or not isinstance(manifest_inputs, dict)
        or manifest_inputs.get("projectionId") != projection.get("projectionId")
        or manifest_inputs.get("projectionSpecDigest")
        != projection.get("projectionSpecDigest")
        or manifest_inputs.get("dependencyLockDigest") != lock_digest
        or manifest_inputs.get("dependencyRunDigests")
        != [item.get("runDigest") for item in dependencies]
        or manifest_inputs.get("schedule") != schedule
    ):
        raise MathFlowError("credit bundle projection inputs are inconsistent")
    if not isinstance(credit_index, dict) or set(credit_index) != {
        "schemaVersion",
        "problemId",
        "dependencyLockDigest",
        "assignments",
    }:
        raise MathFlowError("credit bundle index has an invalid envelope")
    assignment_transaction_ids = None
    if schedule is not None and schedule["mode"] == "utc-calendar":
        assignment_transaction_ids = list(
            schedule["allocationWindow"]["transactionIds"]
        )
    validated_index = _validate_credit_index(
        {"assignments": credit_index["assignments"]},
        str(manifest["problemId"]),
        str(lock_digest),
        transactions,
        _current_revisions(state),
        report,
        materialized=True,
        assignment_transaction_ids=assignment_transaction_ids,
    )
    if validated_index != credit_index:
        raise MathFlowError("credit bundle index is not canonical")
    return manifest, credit_index, run_digest


def run_credit_assignment_bundle(
    root: Path,
    projection_root: Path,
    projection: str,
    problem: str,
    head: str,
    output_dir: Path,
    transport: OpenRouterTransport | None = None,
    *,
    as_of: int | None = None,
) -> dict[str, object]:
    root = root.resolve()
    resolved = resolve_projection(root, projection, problem, head)
    if resolved.get("engine") != "overlay-repository-v1":
        raise MathFlowError("credit command requires an overlay projection")
    runner = resolved.get("runner")
    if (
        not isinstance(runner, dict)
        or runner.get("implementation") != "openrouter-credit-assignment-v1"
        or not isinstance(runner.get("spec"), str)
    ):
        raise MathFlowError("credit projection does not select the supported credit runner")
    spec_path = root / str(runner["spec"])
    spec = load_judge_spec(spec_path)
    if spec.get("implementation") != runner["implementation"]:
        raise MathFlowError("credit projection runner does not match its judge spec")
    canonical_spec = json.loads(
        read_at(root, str(resolved["canonicalHead"]), str(runner["spec"]))
    )
    if canonical_spec != spec:
        raise MathFlowError("credit judge spec differs from the canonical projection head")

    plan = plan_credit_run(
        root, projection_root, projection, problem, head, as_of
    )
    if plan.get("eligible") is not True:
        raise MathFlowError(
            "credit run is not eligible: "
            f"{plan.get('reasonCode')}: {plan.get('message')}"
        )
    schedule = validate_credit_run_schedule(plan.get("schedule"))

    dependency_lock = resolve_projection_dependencies(
        root,
        projection_root,
        projection,
        problem,
        head,
    )
    if dependency_lock["dependencyLockDigest"] != plan.get("dependencyLockDigest"):
        raise MathFlowError("credit dependency state changed after eligibility planning")
    knowledge_dependencies = [
        item
        for item in dependency_lock["dependencies"]
        if item.get("artifactRole") == "knowledge-state"
    ]
    if len(knowledge_dependencies) != 1:
        raise MathFlowError("credit runner requires exactly one knowledge-state dependency")
    knowledge_dependency = knowledge_dependencies[0]
    state, knowledge_revisions, knowledge_profile = _knowledge_state(
        projection_root, knowledge_dependency, problem
    )
    node_revisions = _current_revisions(state)
    source = load_source(root, problem, head)
    if source["problemLedgerDigest"] != dependency_lock["problemLedger"][
        "problemLedgerDigest"
    ]:
        raise MathFlowError("credit source ledger does not match its dependency lock")
    transactions = source["transactions"]
    if not transactions:
        raise MathFlowError("credit assignment requires at least one canonical transaction")
    transaction_ids = [str(item["transactionId"]) for item in transactions]
    assignment_transaction_ids = transaction_ids
    if schedule["mode"] == "utc-calendar":
        assignment_transaction_ids = list(
            schedule["allocationWindow"]["transactionIds"]
        )
    problem_statement = read_at(
        root, str(source["ledgerHead"]), f"problems/{problem}/problem.md"
    )
    evidence = artifact_evidence(root, source, head)
    credit_input = {
        "schemaVersion": 1,
        "problemId": problem,
        "ledgerHead": source["ledgerHead"],
        "problemLedgerHead": source["problemLedgerHead"],
        "problemLedgerDigest": source["problemLedgerDigest"],
        "creditProjection": {
            "projectionId": projection,
            "projectionSpecDigest": resolved["projectionSpecDigest"],
        },
        "dependencyLockDigest": dependency_lock["dependencyLockDigest"],
        "transactions": transactions,
        "problemStatement": problem_statement,
        "contributionEvidence": evidence,
        "knowledgeState": state,
        "knowledgeRevisions": knowledge_revisions,
        "knowledgeOutputProfile": knowledge_profile,
        "schedule": schedule,
    }

    headings = "\n".join(
        f"## Contribution: {transaction_id}"
        for transaction_id in assignment_transaction_ids
    )
    report_prompt = "\n\n".join(
        [
            (
                "Write a detailed Markdown credit assessment of every contribution in the governed UTC allocation window. Do not output JSON and do not alter or re-adjudicate the mathematics."
                if schedule["mode"] == "utc-calendar"
                else "Write a detailed Markdown credit assessment of every canonical contribution. Do not output JSON and do not alter or re-adjudicate the mathematics."
            ),
            "Credit is qualitative and non-zero-sum: assess each transaction's causal contribution, significance, and roles on its own merits. Explain uncertainty rather than forcing a ranking.",
            (
                "This run has a governed UTC allocation window. Assess and emit headings only for the window's transaction IDs; older contributions are context and may be cited as reservation evidence. "
                + json.dumps(schedule["allocationWindow"], ensure_ascii=False)
                if schedule["mode"] == "utc-calendar"
                else "This rolling run assesses the complete canonical ledger."
            ),
            "Use each required level-two heading exactly once, with substantive reasoning beneath it. Discuss reservations only when a canonical contribution actually provides specific evidence of one.",
            f"Required headings in ledger order:\n{headings}",
            f"Rubric:\n{json.dumps(spec['rubric'], indent=2, ensure_ascii=False)}",
            f"Problem statement:\n<problem>\n{problem_statement}\n</problem>",
            "Locked holistic knowledge state:\n<knowledge-state>\n"
            + json.dumps(state, indent=2, ensure_ascii=False)
            + "\n</knowledge-state>",
            f"Canonical contributions in ledger order:\n{evidence}",
        ]
    )
    report_request = _request(
        spec,
        "report",
        [
            {"role": "system", "content": str(spec["systemPrompt"])},
            {"role": "user", "content": report_prompt},
        ],
    )
    send = transport or send_chat_completion
    report_response = send(report_request)
    _reject_truncated_response(report_response, "report")
    report = _assistant_content(report_response).rstrip() + "\n"

    node_index = [
        {"nodeId": node_id, "revisionId": node_revisions[node_id]}
        for node_id in sorted(node_revisions)
    ]
    extract_prompt = "\n\n".join(
        [
            "Extract a faithful qualitative credit index from the report. Do not redo, summarize, or extend its assessment.",
            "Return exactly one assignment per transaction in ledger order. Sort roles alphabetically, knowledgeRefs by nodeId then revisionId, and reservationTransactionIds by ledger order.",
            "Do not return report-section headings; trusted runner code derives each exact heading from its transaction ID.",
            "A knowledge reference must use the exact current revision shown below. A reservation reference must be a canonical transaction no later than the transaction being assessed.",
            "Transactions in assignment scope and ledger order:\n"
            + json.dumps(assignment_transaction_ids, indent=2),
            f"Current knowledge references:\n{json.dumps(node_index, indent=2)}",
            f"Report:\n<credit-report>\n{report}</credit-report>",
        ]
    )
    extract_request = _request(
        spec,
        "extract",
        [
            {
                "role": "system",
                "content": "You are a faithful credit-index extractor. Emit only the requested control index and preserve the report's meaning.",
            },
            {"role": "user", "content": extract_prompt},
        ],
        _credit_schema(
            assignment_transaction_ids,
            node_revisions,
            reservation_transaction_ids=transaction_ids,
        ),
    )
    extract_response = send(extract_request)
    _reject_truncated_response(extract_response, "extract")
    credit_index = _validate_credit_index(
        _structured_content(extract_response, "extract"),
        problem,
        str(dependency_lock["dependencyLockDigest"]),
        transactions,
        node_revisions,
        report,
        assignment_transaction_ids=assignment_transaction_ids,
    )

    bundle = ArtifactBundle(output_dir)
    bundle.add_json(
        "control/dependencies.json", dependency_lock, "dependency-lock"
    )
    bundle.add_json("control/input.json", credit_input, "credit-input")
    bundle.add_text(
        "report.md", report, "credit-report", "text/markdown"
    )
    bundle.add_json("credit/index.json", credit_index, "credit-index")
    requests = [report_request, extract_request]
    responses = [report_response, extract_response]
    envelope = run_envelope(
        problem,
        source,
        spec,
        None,
        [f"sha256:{sha256_json(request)}" for request in requests],
        [
            _provider_run(response, str(request["model"]), stage)
            for response, request, stage in zip(
                responses, requests, ["report", "extract"], strict=True
            )
        ],
        run_kind="credit-assignment",
        inputs={
            "projectionId": projection,
            "projectionSpecDigest": resolved["projectionSpecDigest"],
            "dependencyLockDigest": dependency_lock["dependencyLockDigest"],
            "dependencyRunDigests": [
                item["runDigest"] for item in dependency_lock["dependencies"]
            ],
            "schedule": schedule,
        },
    )
    return bundle.finalize(envelope)
