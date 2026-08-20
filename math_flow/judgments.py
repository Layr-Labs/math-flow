from __future__ import annotations

import copy
import json
import re
from pathlib import Path

from .artifacts import ArtifactBundle, load_manifest, read_verified_artifact, sha256_bytes
from .attestations import objective_attestation_status
from .errors import MathFlowError
from .hierarchical import _assistant_content, _provider_run, _request, _structured_content
from .judges import artifact_evidence, load_judge_spec, load_source
from .openrouter import OpenRouterTransport, send_chat_completion
from .repository import is_ancestor, read_at, sha256_json
from .runs import run_envelope
from .validity import (
    build_dependency_packet,
    build_evidence_packet_v3,
    build_evidence_packet_v4,
    contribution_claims,
    validate_dependency_packet,
    validate_evidence_packet_v3,
    validate_evidence_packet_v4,
)


CLAIM_KEY = re.compile(r"^[a-z0-9][a-z0-9/_-]*$")
STANCES = {"supports", "refutes", "qualifies", "uncertain", "raises"}
RECONCILIATION_OUTCOMES = {
    "compatible",
    "prefer-support",
    "prefer-refutation",
    "synthesize",
    "unresolved",
    "needs-evidence",
}
PRIMARY_JUDGMENT_IMPLEMENTATIONS = {
    "openrouter-markdown-judgment-v1",
    "openrouter-validity-judgment-v2",
    "openrouter-validity-judgment-v3",
    "openrouter-validity-judgment-v4",
}
VALIDITY_STATUSES = {"valid", "invalid", "indeterminate"}
PREMISE_STATUSES = {"satisfied", "missing", "disputed", "not-required"}


def _reject_truncated_response(response: dict[str, object], stage: str) -> None:
    try:
        finish_reason = response["choices"][0].get("finish_reason")
    except (KeyError, IndexError, TypeError, AttributeError):
        finish_reason = None
    if finish_reason == "length":
        raise MathFlowError(f"OpenRouter {stage} response was truncated")


def _finding_schema(transaction_ids: list[str]) -> dict[str, object]:
    transaction: dict[str, object] = {"type": "string"}
    if transaction_ids:
        transaction["enum"] = transaction_ids
    finding = {
        "type": "object",
        "properties": {
            "claimKey": {"type": "string"},
            "stance": {"type": "string", "enum": sorted(STANCES)},
            "summary": {"type": "string"},
            "subjectTransactionIds": {"type": "array", "items": transaction},
            "evidenceTransactionIds": {"type": "array", "items": transaction},
        },
        "required": [
            "claimKey",
            "stance",
            "summary",
            "subjectTransactionIds",
            "evidenceTransactionIds",
        ],
        "additionalProperties": False,
    }
    return {
        "type": "object",
        "properties": {"findings": {"type": "array", "items": finding}},
        "required": ["findings"],
        "additionalProperties": False,
    }


def _validate_findings(
    value: object, subject_ids: set[str], ledger_ids: set[str]
) -> list[dict[str, object]]:
    if not isinstance(value, dict) or set(value) != {"findings"}:
        raise MathFlowError("judgment extractor returned an invalid findings envelope")
    findings = value["findings"]
    if not isinstance(findings, list):
        raise MathFlowError("judgment findings must be an array")
    validated: list[dict[str, object]] = []
    seen: set[tuple[str, str]] = set()
    for finding in findings:
        expected = {
            "claimKey",
            "stance",
            "summary",
            "subjectTransactionIds",
            "evidenceTransactionIds",
        }
        if not isinstance(finding, dict) or set(finding) != expected:
            raise MathFlowError("judgment extractor returned an invalid finding")
        claim_key = finding["claimKey"]
        stance = finding["stance"]
        summary = finding["summary"]
        subjects = finding["subjectTransactionIds"]
        evidence = finding["evidenceTransactionIds"]
        if not isinstance(claim_key, str) or not CLAIM_KEY.fullmatch(claim_key):
            raise MathFlowError("judgment claimKey must be a stable lowercase path")
        if stance not in STANCES:
            raise MathFlowError(f"unsupported judgment stance: {stance}")
        if not isinstance(summary, str) or not summary.strip():
            raise MathFlowError("judgment finding summary must be non-empty")
        if not isinstance(subjects, list) or any(not isinstance(item, str) for item in subjects):
            raise MathFlowError("judgment finding subjects must be transaction IDs")
        if not subjects or not set(subjects) <= subject_ids:
            raise MathFlowError("judgment finding references a subject outside this judgment")
        if not isinstance(evidence, list) or any(not isinstance(item, str) for item in evidence):
            raise MathFlowError("judgment finding evidence must be transaction IDs")
        if not set(evidence) <= ledger_ids:
            raise MathFlowError("judgment finding references evidence outside the ledger")
        key = (claim_key, str(stance))
        if key in seen:
            raise MathFlowError("judgment contains a duplicate claim stance")
        seen.add(key)
        validated.append(
            {
                "claimKey": claim_key,
                "stance": stance,
                "summary": summary.strip(),
                "subjectTransactionIds": list(dict.fromkeys(subjects)),
                "evidenceTransactionIds": list(dict.fromkeys(evidence)),
            }
        )
    return validated


def _reconciliation_schema(transaction_ids: list[str]) -> dict[str, object]:
    schema = _finding_schema(transaction_ids)
    properties = schema["properties"]
    properties["outcome"] = {
        "type": "string",
        "enum": sorted(RECONCILIATION_OUTCOMES),
    }
    properties["summary"] = {"type": "string"}
    schema["required"] = ["outcome", "summary", "findings"]
    return schema


def _run_markdown_primary_judgment_bundle(
    root: Path,
    problem: str,
    judge_path: Path,
    head: str,
    subject_transaction_ids: list[str],
    output_dir: Path,
    context_transaction_ids: list[str] | None = None,
    transport: OpenRouterTransport | None = None,
) -> dict[str, object]:
    root = root.resolve()
    spec = load_judge_spec(judge_path)
    if spec["implementation"] != "openrouter-markdown-judgment-v1":
        raise MathFlowError("judgment command requires a v1 Markdown judgment spec")
    source = load_source(root, problem, head)
    transactions = source["transactions"]
    by_id = {str(item["transactionId"]): item for item in transactions}
    requested = list(dict.fromkeys(subject_transaction_ids))
    if not requested:
        raise MathFlowError("a primary judgment requires at least one subject transaction")
    missing = [transaction_id for transaction_id in requested if transaction_id not in by_id]
    if missing:
        raise MathFlowError(f"judgment subject is outside the problem ledger: {missing[0]}")
    context_ids = list(dict.fromkeys(context_transaction_ids or []))
    missing_context = [transaction_id for transaction_id in context_ids if transaction_id not in by_id]
    if missing_context:
        raise MathFlowError(f"judgment context is outside the problem ledger: {missing_context[0]}")
    supplied_ids = list(dict.fromkeys([*requested, *context_ids]))
    subject_transactions = sorted(
        (by_id[transaction_id] for transaction_id in requested),
        key=lambda item: int(item["ordinal"]),
    )
    selected_transactions = sorted(
        (by_id[transaction_id] for transaction_id in supplied_ids),
        key=lambda item: int(item["ordinal"]),
    )
    selected_source = {**source, "transactions": selected_transactions}
    resolved_head = "WORKTREE" if head == "WORKTREE" else str(source["ledgerHead"])
    problem_statement = read_at(root, resolved_head, f"problems/{problem}/problem.md")
    evidence = artifact_evidence(root, selected_source, head)
    subject_ids = [str(item["transactionId"]) for item in subject_transactions]
    ledger_ids = [str(item["transactionId"]) for item in selected_transactions]
    send = transport or send_chat_completion

    report_prompt = "\n\n".join(
        [
            "Write a detailed Markdown judgment of the supplied subject transactions. Do not output JSON and do not construct or mutate a cumulative knowledge state.",
            "Separate distinct mathematical findings, explain decisive reasoning, and identify contradictions or missing evidence. Do not optimize for brevity.",
            f"Rubric:\n{json.dumps(spec['rubric'], indent=2, ensure_ascii=False)}",
            f"Problem:\n{problem_statement}",
            f"Subject transaction IDs:\n{json.dumps(subject_ids, indent=2)}",
            f"Subject evidence:\n{evidence}",
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
    report_response = send(report_request)
    _reject_truncated_response(report_response, "report")
    report = _assistant_content(report_response).rstrip() + "\n"

    extract_prompt = "\n\n".join(
        [
            "Index the mathematical findings in the report without redoing or shortening the judgment.",
            "Use a stable lowercase claimKey such as `triangle-midpoints/equal-areas`; independent judgments about the same mathematical claim should use the same key.",
            "supports means the subject supplies support, refutes means it supplies contrary evidence, qualifies narrows a claim, uncertain means the assessment cannot decide, and raises introduces a question.",
            "Every finding must name at least one supplied subject transaction. Evidence transaction IDs must come from the supplied ledger IDs.",
            f"Subject transaction IDs:\n{json.dumps(subject_ids, indent=2)}",
            f"Ledger transaction IDs:\n{json.dumps(ledger_ids, indent=2)}",
            f"Report:\n<report>\n{report}</report>",
        ]
    )
    extract_request = _request(
        spec,
        "extract",
        [
            {
                "role": "system",
                "content": "You are a faithful routing-index extractor. Preserve the Markdown judgment's meaning and emit only its finding index.",
            },
            {"role": "user", "content": extract_prompt},
        ],
        _finding_schema(ledger_ids),
    )
    extract_response = send(extract_request)
    _reject_truncated_response(extract_response, "extract")
    findings = _validate_findings(
        _structured_content(extract_response, "extract"), set(subject_ids), set(ledger_ids)
    )
    report_digest = sha256_bytes(report.encode("utf-8"))
    judgment_core: dict[str, object] = {
        "schemaVersion": 1,
        "judgmentKind": "primary",
        "problemId": problem,
        "ledgerHead": source["ledgerHead"],
        "problemLedgerDigest": source["problemLedgerDigest"],
        "judgeSpec": {
            "id": spec["id"],
            "digest": f"sha256:{sha256_json(spec)}",
        },
        "subjects": [
            {
                "kind": "transaction",
                "id": item["transactionId"],
                "ledgerPosition": item["ordinal"],
            }
            for item in subject_transactions
        ],
        "findings": findings,
        "reportDigest": report_digest,
    }
    judgment = {
        **judgment_core,
        "judgmentId": f"sha256:{sha256_json(judgment_core)}",
    }
    bundle = ArtifactBundle(output_dir)
    bundle.add_text("report.md", report, "judgment-report", "text/markdown")
    bundle.add_json("judgment.json", judgment, "judgment-record")
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
        run_kind="judgment",
        inputs={
            "subjectTransactionIds": subject_ids,
            "contextTransactionIds": [
                transaction_id for transaction_id in ledger_ids if transaction_id not in subject_ids
            ],
        },
    )
    return bundle.finalize(envelope)


def _validity_schema(
    claim_keys: list[str], dependency_ids: list[str]
) -> dict[str, object]:
    evidence_item: dict[str, object] = {"type": "string"}
    if dependency_ids:
        evidence_item["enum"] = dependency_ids
    assessment = {
        "type": "object",
        "properties": {
            "claimKey": {"type": "string", "enum": claim_keys},
            "status": {"type": "string", "enum": sorted(VALIDITY_STATUSES)},
            "premiseStatus": {"type": "string", "enum": sorted(PREMISE_STATUSES)},
            "summary": {"type": "string"},
            "scopeQualifications": {"type": "array", "items": {"type": "string"}},
            "evidenceIssues": {"type": "array", "items": {"type": "string"}},
            "evidenceTransactionIds": {
                "type": "array",
                "items": evidence_item,
            },
        },
        "required": [
            "claimKey",
            "status",
            "premiseStatus",
            "summary",
            "scopeQualifications",
            "evidenceIssues",
            "evidenceTransactionIds",
        ],
        "additionalProperties": False,
    }
    return {
        "type": "object",
        "properties": {
            "assessments": {
                "type": "array",
                "items": assessment,
                "minItems": len(claim_keys),
                "maxItems": len(claim_keys),
            }
        },
        "required": ["assessments"],
        "additionalProperties": False,
    }


def _validate_assessments(
    value: object,
    claims: list[dict[str, object]],
    dependency_ids: set[str],
) -> list[dict[str, object]]:
    if not isinstance(value, dict) or set(value) != {"assessments"}:
        raise MathFlowError("validity extractor returned an invalid assessments envelope")
    assessments = value["assessments"]
    if not isinstance(assessments, list):
        raise MathFlowError("validity assessments must be an array")
    claim_keys = [str(claim["claimKey"]) for claim in claims]
    expected_fields = {
        "claimKey",
        "status",
        "premiseStatus",
        "summary",
        "scopeQualifications",
        "evidenceIssues",
        "evidenceTransactionIds",
    }
    validated: list[dict[str, object]] = []
    observed: list[str] = []
    for assessment in assessments:
        if not isinstance(assessment, dict) or set(assessment) != expected_fields:
            raise MathFlowError("validity extractor returned an invalid assessment")
        claim_key = assessment["claimKey"]
        status = assessment["status"]
        premise_status = assessment["premiseStatus"]
        summary = assessment["summary"]
        qualifications = assessment["scopeQualifications"]
        issues = assessment["evidenceIssues"]
        evidence = assessment["evidenceTransactionIds"]
        if not isinstance(claim_key, str) or claim_key not in claim_keys:
            raise MathFlowError("validity assessment references an undeclared claim")
        if status not in VALIDITY_STATUSES or premise_status not in PREMISE_STATUSES:
            raise MathFlowError("validity assessment has an unsupported status")
        if not isinstance(summary, str) or not summary.strip():
            raise MathFlowError("validity assessment summary must be non-empty")
        if not isinstance(qualifications, list) or any(
            not isinstance(item, str) or not item.strip() for item in qualifications
        ):
            raise MathFlowError("validity scope qualifications must be non-empty strings")
        if not isinstance(issues, list) or any(
            not isinstance(item, str) or not item.strip() for item in issues
        ):
            raise MathFlowError("validity evidence issues must be non-empty strings")
        if (
            not isinstance(evidence, list)
            or any(not isinstance(item, str) for item in evidence)
            or len(evidence) != len(set(evidence))
            or not set(evidence) <= dependency_ids
        ):
            raise MathFlowError("validity assessment cites undeclared dependency evidence")
        observed.append(claim_key)
        validated.append(
            {
                "claimKey": claim_key,
                "status": status,
                "premiseStatus": premise_status,
                "summary": summary.strip(),
                "scopeQualifications": [item.strip() for item in qualifications],
                "evidenceIssues": [item.strip() for item in issues],
                "evidenceTransactionIds": evidence,
            }
        )
    if len(observed) != len(set(observed)) or set(observed) != set(claim_keys):
        raise MathFlowError("validity judgment must assess every declared claim exactly once")
    by_key = {str(item["claimKey"]): item for item in validated}
    return [by_key[key] for key in claim_keys]


def _validity_v3_schema(
    claims: list[dict[str, object]], reference_ids: list[str]
) -> dict[str, object]:
    claim_keys = [str(claim["claimKey"]) for claim in claims]
    schema = _validity_schema(claim_keys, reference_ids)
    assessments = schema["properties"]["assessments"]
    template = assessments["items"]
    variants: list[dict[str, object]] = []
    for claim in claims:
        assessment = copy.deepcopy(template)
        claim_key = str(claim["claimKey"])
        claim_references = list(claim["declaredReferenceTransactionIds"])
        assessment["properties"]["claimKey"]["enum"] = [claim_key]
        evidence = assessment["properties"]["evidenceTransactionIds"]
        evidence["items"] = {
            "type": "string",
            **({"enum": claim_references} if claim_references else {}),
        }
        if not claim_references:
            evidence["maxItems"] = 0
        assessment["properties"]["requiredDependencyTransactionIds"] = {
            "type": "array",
            "items": {
                "type": "string",
                **({"enum": claim_references} if claim_references else {}),
            },
            **({"maxItems": 0} if not claim_references else {}),
        }
        assessment["required"].append("requiredDependencyTransactionIds")
        variants.append(assessment)
    assessments["items"] = {"anyOf": variants}
    return schema


def _validate_assessments_v3(
    value: object,
    claims: list[dict[str, object]],
    reference_ids: set[str],
) -> list[dict[str, object]]:
    if not isinstance(value, dict) or not isinstance(value.get("assessments"), list):
        raise MathFlowError("validity-v3 extractor returned an invalid assessments envelope")
    references_by_claim = {
        str(claim["claimKey"]): set(claim["declaredReferenceTransactionIds"])
        for claim in claims
    }
    stripped: list[dict[str, object]] = []
    required_by_key: dict[str, list[str]] = {}
    for assessment in value["assessments"]:
        if not isinstance(assessment, dict):
            raise MathFlowError("validity-v3 extractor returned an invalid assessment")
        required = assessment.get("requiredDependencyTransactionIds")
        claim_key = assessment.get("claimKey")
        if (
            not isinstance(required, list)
            or any(not isinstance(item, str) for item in required)
            or len(required) != len(set(required))
            or not isinstance(claim_key, str)
            or claim_key not in references_by_claim
            or not set(required) <= references_by_claim[claim_key]
        ):
            raise MathFlowError(
                "validity-v3 assessment has invalid per-claim required dependencies"
            )
        evidence = assessment.get("evidenceTransactionIds")
        if (
            not isinstance(evidence, list)
            or not set(evidence) <= references_by_claim[claim_key]
            or not set(required) <= set(evidence)
        ):
            raise MathFlowError(
                "validity-v3 evidence and required dependencies must belong to the same claim"
            )
        status = assessment.get("status")
        premise_status = assessment.get("premiseStatus")
        if status == "valid" and (
            premise_status not in {"satisfied", "not-required"}
            or (required and premise_status != "satisfied")
        ):
            raise MathFlowError(
                "validity-v3 valid assessment has inconsistent premise status"
            )
        required_by_key[claim_key] = list(required)
        stripped.append(
            {
                key: item
                for key, item in assessment.items()
                if key != "requiredDependencyTransactionIds"
            }
        )
    v2_claims = [
        {
            "claimKey": claim["claimKey"],
            "statement": claim["statement"],
            "dependencyTransactionIds": claim[
                "declaredReferenceTransactionIds"
            ],
        }
        for claim in claims
    ]
    validated = _validate_assessments(
        {"assessments": stripped}, v2_claims, reference_ids
    )
    return [
        {
            **assessment,
            "requiredDependencyTransactionIds": required_by_key[
                str(assessment["claimKey"])
            ],
        }
        for assessment in validated
    ]


def _run_validity_primary_judgment_bundle(
    root: Path,
    problem: str,
    judge_path: Path,
    head: str,
    subject_transaction_ids: list[str],
    output_dir: Path,
    projection_root: Path | None,
    context_transaction_ids: list[str] | None,
    research_state_run: Path | None,
    transport: OpenRouterTransport | None,
) -> dict[str, object]:
    root = root.resolve()
    spec = load_judge_spec(judge_path)
    implementation = str(spec["implementation"])
    if implementation not in {
        "openrouter-validity-judgment-v2",
        "openrouter-validity-judgment-v3",
        "openrouter-validity-judgment-v4",
    }:
        raise MathFlowError("judgment command requires a validity judgment spec")
    is_v3 = implementation == "openrouter-validity-judgment-v3"
    is_v4 = implementation == "openrouter-validity-judgment-v4"
    is_reference_aware = is_v3 or is_v4
    requested = list(dict.fromkeys(subject_transaction_ids))
    if len(requested) != 1:
        raise MathFlowError("a validity judgment assesses exactly one subject transaction")
    if context_transaction_ids:
        raise MathFlowError(
            "validity judgments derive references from the contribution; --evidence is not allowed"
        )
    source = load_source(root, problem, head)
    by_id = {
        str(item["transactionId"]): item for item in source["transactions"]
    }
    subject_id = requested[0]
    subject = by_id.get(subject_id)
    if subject is None:
        raise MathFlowError(f"judgment subject is outside the problem ledger: {subject_id}")
    context_projection = spec.get("contextProjection")
    if context_projection is not None and not isinstance(context_projection, str):
        raise MathFlowError("validity judge contextProjection must be a projection ID")
    if is_v4:
        packet = build_evidence_packet_v4(
            root,
            projection_root,
            problem,
            source,
            head,
            subject_id,
            context_projection,
            research_state_run,
        )
    elif is_v3:
        packet = build_evidence_packet_v3(
            root,
            projection_root,
            problem,
            source,
            head,
            subject_id,
            context_projection,
            research_state_run,
        )
    else:
        packet = build_dependency_packet(
            root,
            projection_root,
            problem,
            source,
            head,
            subject_id,
            context_projection,
            research_state_run,
        )
    (
        validate_evidence_packet_v4
        if is_v4
        else validate_evidence_packet_v3
        if is_v3
        else validate_dependency_packet
    )(packet)
    claims = list(packet["claims"])
    reference_ids = list(
        packet[
            "declaredReferenceTransactionIds"
            if is_reference_aware
            else "dependencyTransactionIds"
        ]
    )
    dependency_transactions = [by_id[item] for item in reference_ids]
    subject_source = {**source, "transactions": [subject]}
    dependency_source = {**source, "transactions": dependency_transactions}
    resolved_head = "WORKTREE" if head == "WORKTREE" else str(source["ledgerHead"])
    problem_statement = read_at(root, resolved_head, f"problems/{problem}/problem.md")
    subject_evidence = artifact_evidence(root, subject_source, head)
    dependency_evidence = (
        artifact_evidence(root, dependency_source, head)
        if dependency_transactions
        else "(none declared)"
    )
    send = transport or send_chat_completion
    report_prompt = "\n\n".join(
        [
            (
                "Perform a rigorous, adversarial mathematical correctness audit of each declared claim using the supplied subject and declared reference evidence."
                if is_reference_aware
                else "Perform a rigorous, adversarial mathematical correctness audit of each declared claim using the supplied subject and its explicitly declared premises."
            )
            + " The dominant objective is to prevent false acceptance: mark a claim valid only after affirmatively verifying its exact statement and every material proof obligation.",
            "Check all logical inferences, lemma applications, assumptions, quantifiers, domains, edge and degenerate cases, calculations, and dependency hypotheses. Actively look for counterexamples and hidden gaps. Never repair an omitted step or give the submission the benefit of the doubt. Use invalid for a decisive defect and indeterminate whenever any material obligation remains unresolved.",
            *(
                [
                    "Treat cited transactions as declared references, not automatically as logical premises. For each claim, identify as required dependencies only references whose mathematical content is actually necessary to establish the claim from the supplied record. A historical/provenance citation, a target being corrected, or a result whose complete needed argument is independently restated is not a required dependency. Preserve such citations as references, but do not make accepted-state formation depend on them.",
                    (
                        "If the packet contains terminal objective attestations for the subject or declared references, audit exactly what each pinned command and bytes establish and whether that encoded predicate supports the mathematical claim. Every attestation is trusted execution evidence, not an automatic validity verdict. If a scoped verification request exists, the scheduler will not invoke you until its terminal attestation is present."
                        if is_v4
                        else "If the packet contains a terminal objective attestation, audit exactly what its pinned command and bytes establish and whether that encoded predicate matches the mathematical claim. The attestation is trusted execution evidence, not an automatic validity verdict. If a verification request exists, the scheduler will not invoke you until its terminal attestation is present."
                    ),
                ]
                if is_reference_aware
                else []
            ),
            "The declared claim keys organize the final verdicts; they do not constrain the analysis. Within each claim's Markdown section, decompose the proof into as many intermediate obligations and discuss as many defects as rigorous verification requires. Keep those obligations, missing premises, evidence defects, and scope qualifications attached to the corresponding declared claim rather than promoting them to new top-level claim identities.",
            "Do not build global knowledge state, assess novelty or priority, organize research programs, or assign credit.",
            f"Rubric:\n{json.dumps(spec['rubric'], indent=2, ensure_ascii=False)}",
            f"Problem:\n{problem_statement}",
            f"Dependency packet:\n{json.dumps(packet, indent=2, ensure_ascii=False)}",
            f"Subject evidence:\n{subject_evidence}",
            f"Declared reference evidence:\n{dependency_evidence}",
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
    report_response = send(report_request)
    _reject_truncated_response(report_response, "report")
    report = _assistant_content(report_response).rstrip() + "\n"
    claim_keys = [str(claim["claimKey"]) for claim in claims]
    extract_prompt = "\n\n".join(
        [
            "Create one structured validity record for each declared claim key. This is an indexing rule for the already-completed rigorous audit, not a limit on the report's mathematical decomposition. Do not create, split, merge, or rename the declared claim identities. Preserve every material proof defect, unresolved obligation, and qualification within its claim record.",
            "valid means the supplied argument establishes the claim under satisfied premises; invalid means a decisive error or counterexample defeats it; indeterminate means the bounded record does not decide it.",
            *(
                [
                    "For requiredDependencyTransactionIds, include exactly this claim's declared references whose mathematical content is logically necessary to establish this claim. evidenceTransactionIds is also claim-local: do not borrow a reference declared only by another claim. Every required dependency must appear in evidenceTransactionIds. A valid claim with required dependencies must report premiseStatus satisfied; a valid claim without them may report satisfied or not-required. Do not include provenance-only citations, corrected or criticized submissions, or a reference whose needed argument is fully established within the subject itself.",
                ]
                if is_reference_aware
                else []
            ),
            f"Declared claims:\n{json.dumps(claims, indent=2, ensure_ascii=False)}",
            f"Allowed reference evidence IDs:\n{json.dumps(reference_ids, indent=2)}",
            f"Report:\n<report>\n{report}</report>",
        ]
    )
    extract_request = _request(
        spec,
        "extract",
        [
            {
                "role": "system",
                "content": "You are a faithful validity-record extractor. Emit only assessments for the declared claims.",
            },
            {"role": "user", "content": extract_prompt},
        ],
        (
            _validity_v3_schema(claims, reference_ids)
            if is_reference_aware
            else _validity_schema(claim_keys, reference_ids)
        ),
    )
    extract_response = send(extract_request)
    _reject_truncated_response(extract_response, "extract")
    structured = _structured_content(extract_response, "extract")
    assessments = (
        _validate_assessments_v3(structured, claims, set(reference_ids))
        if is_reference_aware
        else _validate_assessments(structured, claims, set(reference_ids))
    )
    stance = {"valid": "supports", "invalid": "refutes", "indeterminate": "uncertain"}
    findings = [
        {
            "claimKey": assessment["claimKey"],
            "stance": stance[str(assessment["status"])],
            "summary": assessment["summary"],
            "subjectTransactionIds": [subject_id],
            "evidenceTransactionIds": assessment["evidenceTransactionIds"],
        }
        for assessment in assessments
    ]
    report_digest = sha256_bytes(report.encode("utf-8"))
    judgment_core: dict[str, object] = {
        "schemaVersion": 4 if is_v4 else 3 if is_v3 else 2,
        "judgmentKind": "primary",
        "problemId": problem,
        "ledgerHead": source["ledgerHead"],
        "problemLedgerDigest": source["problemLedgerDigest"],
        "judgeSpec": {"id": spec["id"], "digest": f"sha256:{sha256_json(spec)}"},
        "subjects": [
            {
                "kind": "transaction",
                "id": subject_id,
                "ledgerPosition": subject["ordinal"],
            }
        ],
        "assessments": assessments,
        "findings": findings,
        "dependencyPacketDigest": packet["packetDigest"],
        "reportDigest": report_digest,
    }
    judgment = {**judgment_core, "judgmentId": f"sha256:{sha256_json(judgment_core)}"}
    bundle = ArtifactBundle(output_dir)
    bundle.add_text("report.md", report, "judgment-report", "text/markdown")
    bundle.add_json(
        "dependency-packet.json", packet, "judgment-dependency-packet"
    )
    bundle.add_json("judgment.json", judgment, "judgment-record")
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
        run_kind="judgment",
        inputs={
            "subjectTransactionIds": [subject_id],
            (
                "declaredReferenceTransactionIds"
                if is_reference_aware
                else "dependencyTransactionIds"
            ): reference_ids,
            "dependencyPacketDigest": packet["packetDigest"],
            **(
                {
                    "objectiveAttestationRunDigest": (
                        packet["objectiveAttestation"]["runDigest"]
                        if isinstance(packet.get("objectiveAttestation"), dict)
                        else None
                    )
                }
                if is_v3
                else {}
            ),
            **(
                {
                    "objectiveAttestationRunDigestsByTransactionId": {
                        str(entry["transactionId"]): str(
                            entry["attestation"]["runDigest"]
                        )
                        for entry in packet["objectiveAttestations"]
                    }
                }
                if is_v4
                else {}
            ),
            "knowledgeContext": (
                None
                if packet["knowledgeContext"] is None
                else {
                    key: value
                    for key, value in packet["knowledgeContext"].items()
                    if key
                    not in {
                        "selectedNodes",
                        "selectedPrograms",
                        "selectedThreads",
                        "selectedItems",
                    }
                }
            ),
        },
    )
    return bundle.finalize(envelope)


def run_primary_judgment_bundle(
    root: Path,
    problem: str,
    judge_path: Path,
    head: str,
    subject_transaction_ids: list[str],
    output_dir: Path,
    context_transaction_ids: list[str] | None = None,
    transport: OpenRouterTransport | None = None,
    projection_root: Path | None = None,
    research_state_run: Path | None = None,
) -> dict[str, object]:
    spec = load_judge_spec(judge_path)
    if spec["implementation"] in {
        "openrouter-validity-judgment-v2",
        "openrouter-validity-judgment-v3",
        "openrouter-validity-judgment-v4",
    }:
        return _run_validity_primary_judgment_bundle(
            root,
            problem,
            judge_path,
            head,
            subject_transaction_ids,
            output_dir,
            projection_root,
            context_transaction_ids,
            research_state_run,
            transport,
        )
    if spec["implementation"] == "openrouter-markdown-judgment-v1":
        return _run_markdown_primary_judgment_bundle(
            root,
            problem,
            judge_path,
            head,
            subject_transaction_ids,
            output_dir,
            context_transaction_ids,
            transport,
        )
    raise MathFlowError("judgment command requires a supported primary judgment spec")


def run_reconciliation_judgment_bundle(
    root: Path,
    problem: str,
    judge_path: Path,
    head: str,
    conflict: dict[str, object],
    judgment_bundle_dirs: list[Path],
    output_dir: Path,
    transport: OpenRouterTransport | None = None,
) -> dict[str, object]:
    root = root.resolve()
    spec = load_judge_spec(judge_path)
    if spec["implementation"] != "openrouter-markdown-reconciliation-v1":
        raise MathFlowError("reconcile command requires a reconciliation judgment spec")
    conflict_id = conflict.get("conflictId")
    conflict_core = {key: value for key, value in conflict.items() if key != "conflictId"}
    if conflict_id != f"sha256:{sha256_json(conflict_core)}":
        raise MathFlowError("conflict ID does not match its content")
    if conflict.get("problemId") != problem or conflict.get("status") != "open":
        raise MathFlowError("reconciliation conflict is not open for this problem")
    claim_key = conflict.get("claimKey")
    conflict_judgments = conflict.get("judgments")
    if not isinstance(claim_key, str) or not isinstance(conflict_judgments, list):
        raise MathFlowError("reconciliation conflict is missing routing fields")
    required_ids = {
        item.get("judgmentId")
        for item in conflict_judgments
        if isinstance(item, dict) and isinstance(item.get("judgmentId"), str)
    }
    if not required_ids or any(
        not isinstance(item, dict)
        or not isinstance(item.get("judgmentId"), str)
        or item.get("stance") not in STANCES
        or not isinstance(item.get("summary"), str)
        for item in conflict_judgments
    ):
        raise MathFlowError("reconciliation conflict contains invalid judgment references")

    loaded: dict[str, tuple[dict[str, object], str]] = {}
    for bundle_dir in judgment_bundle_dirs:
        manifest, judgment, _ = load_judgment_bundle(bundle_dir)
        judgment_id = str(judgment["judgmentId"])
        if judgment_id in loaded:
            raise MathFlowError(
                f"reconciliation input judgments contain a duplicate: {judgment_id}"
            )
        if judgment.get("judgmentKind") != "primary":
            raise MathFlowError("reconciliation input judgment is not primary")
        if judgment.get("problemId") != problem:
            raise MathFlowError("reconciliation input judgment belongs to another problem")
        report = read_verified_artifact(bundle_dir, manifest, "judgment-report").decode("utf-8")
        loaded[judgment_id] = (judgment, report)
    missing = required_ids - loaded.keys()
    if missing:
        raise MathFlowError(f"missing reconciliation input judgment: {sorted(missing)[0]}")
    derived_conflicts = {
        str(item["conflictId"]): item for item in detect_conflicts(judgment_bundle_dirs)
    }
    if derived_conflicts.get(str(conflict_id)) != conflict:
        raise MathFlowError(
            "reconciliation conflict does not match the supplied primary judgments"
        )

    source = load_source(root, problem, head)
    ledger_by_id = {str(item["transactionId"]): item for item in source["transactions"]}
    subject_transactions: dict[str, dict[str, object]] = {}
    report_blocks = []
    for judgment_id in sorted(required_ids):
        judgment, report = loaded[judgment_id]
        for subject in judgment.get("subjects", []):
            if isinstance(subject, dict) and subject.get("kind") == "transaction":
                transaction_id = str(subject.get("id"))
                transaction = ledger_by_id.get(transaction_id)
                if transaction is None:
                    raise MathFlowError("reconciliation subject is outside the current ledger")
                subject_transactions[transaction_id] = transaction
        report_blocks.append(
            "\n".join(
                [
                    f"<judgment id={json.dumps(judgment_id)}>",
                    f"finding_index: {json.dumps(judgment.get('findings'), indent=2, ensure_ascii=False)}",
                    report,
                    "</judgment>",
                ]
            )
        )
    ordered_transactions = sorted(
        subject_transactions.values(), key=lambda item: int(item["ordinal"])
    )
    selected_source = {**source, "transactions": ordered_transactions}
    resolved_head = "WORKTREE" if head == "WORKTREE" else str(source["ledgerHead"])
    problem_statement = read_at(root, resolved_head, f"problems/{problem}/problem.md")
    canonical_evidence = artifact_evidence(root, selected_source, head)
    transaction_ids = [str(item["transactionId"]) for item in ordered_transactions]
    send = transport or send_chat_completion

    report_prompt = "\n\n".join(
        [
            "Write a detailed Markdown reconciliation judgment. Do not output JSON and do not construct or mutate cumulative knowledge state.",
            "Recheck the mathematical conflict rather than counting votes. Explain whether the inputs are compatible, whether one side is better supported, whether a synthesis is possible, or why the dispute remains unresolved.",
            f"Rubric:\n{json.dumps(spec['rubric'], indent=2, ensure_ascii=False)}",
            f"Problem:\n{problem_statement}",
            f"Conflict record:\n{json.dumps(conflict, indent=2, ensure_ascii=False)}",
            f"Input judgment reports:\n{''.join(report_blocks)}",
            f"Canonical subject evidence:\n{canonical_evidence}",
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
    report_response = send(report_request)
    _reject_truncated_response(report_response, "reconciliation report")
    report = _assistant_content(report_response).rstrip() + "\n"
    extract_prompt = "\n\n".join(
        [
            "Extract the reconciliation outcome and one finding index without redoing or shortening the judgment.",
            f"The finding claimKey must be exactly {json.dumps(claim_key)}.",
            "Use qualifies for a compatible or synthesized resolution, supports when the supporting side prevails, refutes when the refuting side prevails, and uncertain for an unresolved or needs-evidence outcome.",
            f"Allowed transaction IDs:\n{json.dumps(transaction_ids, indent=2)}",
            f"Report:\n<report>\n{report}</report>",
        ]
    )
    extract_request = _request(
        spec,
        "extract",
        [
            {
                "role": "system",
                "content": "You are a faithful reconciliation-index extractor. Emit only the requested routing fields.",
            },
            {"role": "user", "content": extract_prompt},
        ],
        _reconciliation_schema(transaction_ids),
    )
    extract_response = send(extract_request)
    _reject_truncated_response(extract_response, "reconciliation extract")
    extracted = _structured_content(extract_response, "extract")
    if not isinstance(extracted, dict) or set(extracted) != {"outcome", "summary", "findings"}:
        raise MathFlowError("reconciliation extractor returned an invalid envelope")
    outcome = extracted["outcome"]
    summary = extracted["summary"]
    if outcome not in RECONCILIATION_OUTCOMES:
        raise MathFlowError("reconciliation extractor returned an invalid outcome")
    if not isinstance(summary, str) or not summary.strip():
        raise MathFlowError("reconciliation summary must be non-empty")
    findings = _validate_findings(
        {"findings": extracted["findings"]}, set(transaction_ids), set(ledger_by_id)
    )
    if len(findings) != 1 or findings[0]["claimKey"] != claim_key:
        raise MathFlowError("reconciliation must index exactly its conflict claim")

    report_digest = sha256_bytes(report.encode("utf-8"))
    judgment_core: dict[str, object] = {
        "schemaVersion": 1,
        "judgmentKind": "reconciliation",
        "problemId": problem,
        "ledgerHead": source["ledgerHead"],
        "problemLedgerDigest": source["problemLedgerDigest"],
        "judgeSpec": {
            "id": spec["id"],
            "digest": f"sha256:{sha256_json(spec)}",
        },
        "subjects": [
            {
                "kind": "transaction",
                "id": item["transactionId"],
                "ledgerPosition": item["ordinal"],
            }
            for item in ordered_transactions
        ],
        "findings": findings,
        "reportDigest": report_digest,
        "reconciliation": {
            "conflictId": conflict_id,
            "inputJudgmentIds": sorted(required_ids),
            "outcome": outcome,
            "summary": summary.strip(),
        },
    }
    judgment = {
        **judgment_core,
        "judgmentId": f"sha256:{sha256_json(judgment_core)}",
    }
    bundle = ArtifactBundle(output_dir)
    bundle.add_text("report.md", report, "judgment-report", "text/markdown")
    bundle.add_json("judgment.json", judgment, "judgment-record")
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
        run_kind="judgment",
        inputs={
            "conflictId": conflict_id,
            "inputJudgmentIds": sorted(required_ids),
        },
    )
    return bundle.finalize(envelope)


def load_judgment_bundle(bundle_dir: Path) -> tuple[dict[str, object], dict[str, object], str]:
    manifest, manifest_digest = load_manifest(bundle_dir)
    output_profile = manifest.get("outputProfile")
    if (
        manifest.get("runKind") != "judgment"
        or output_profile
        not in {
            "math-flow/judgment-markdown-v1",
            "math-flow/validity-judgment-v2",
            "math-flow/validity-judgment-v3",
            "math-flow/validity-judgment-v4",
        }
    ):
        raise MathFlowError(f"bundle is not an immutable judgment: {bundle_dir}")
    try:
        judgment = json.loads(read_verified_artifact(bundle_dir, manifest, "judgment-record"))
    except json.JSONDecodeError as exc:
        raise MathFlowError("judgment record is not valid JSON") from exc
    if not isinstance(judgment, dict):
        raise MathFlowError("judgment record must be an object")
    required: set[str] = {
        "schemaVersion",
        "judgmentId",
        "judgmentKind",
        "problemId",
        "ledgerHead",
        "problemLedgerDigest",
        "judgeSpec",
        "subjects",
        "findings",
        "reportDigest",
    }
    kind = judgment.get("judgmentKind")
    validity_version = {
        "math-flow/validity-judgment-v2": 2,
        "math-flow/validity-judgment-v3": 3,
        "math-flow/validity-judgment-v4": 4,
    }.get(str(output_profile))
    is_validity = validity_version is not None
    allowed = required | (
        {"assessments", "dependencyPacketDigest"}
        if is_validity
        else ({"reconciliation"} if kind == "reconciliation" else set())
    )
    if (
        judgment.get("schemaVersion") != (validity_version if is_validity else 1)
        or kind not in ({"primary"} if is_validity else {"primary", "reconciliation"})
        or set(judgment) != allowed
        or judgment.get("problemId") != manifest.get("problemId")
        or judgment.get("ledgerHead") != manifest.get("ledgerHead")
        or judgment.get("problemLedgerDigest") != manifest.get("problemLedgerDigest")
        or judgment.get("judgeSpec") != manifest.get("judgeSpec")
    ):
        raise MathFlowError("judgment record does not match its run manifest")
    subjects = judgment.get("subjects")
    findings = judgment.get("findings")
    if (
        not isinstance(subjects, list)
        or not subjects
        or any(
            not isinstance(subject, dict)
            or set(subject) != {"kind", "id", "ledgerPosition"}
            or subject.get("kind") != "transaction"
            or not isinstance(subject.get("id"), str)
            or not isinstance(subject.get("ledgerPosition"), int)
            for subject in subjects
        )
        or not isinstance(findings, list)
    ):
        raise MathFlowError("judgment record has invalid subjects or findings")
    subject_ids = {str(subject["id"]) for subject in subjects}
    finding_evidence = {
        str(item)
        for finding in findings
        if isinstance(finding, dict)
        for item in finding.get("evidenceTransactionIds", [])
        if isinstance(item, str)
    }
    _validate_findings(
        {"findings": findings}, subject_ids, subject_ids | finding_evidence
    )
    if is_validity:
        try:
            packet = json.loads(
                read_verified_artifact(
                    bundle_dir, manifest, "judgment-dependency-packet"
                )
            )
        except json.JSONDecodeError as exc:
            raise MathFlowError("judgment dependency packet is not valid JSON") from exc
        packet = (
            validate_evidence_packet_v4(packet)
            if validity_version == 4
            else validate_evidence_packet_v3(packet)
            if validity_version == 3
            else validate_dependency_packet(packet)
        )
        if (
            packet.get("problemId") != judgment.get("problemId")
            or packet.get("subjectTransactionId") not in subject_ids
            or packet.get("packetDigest") != judgment.get("dependencyPacketDigest")
        ):
            raise MathFlowError("validity judgment does not match its dependency packet")
        if validity_version == 4:
            manifest_inputs = manifest.get("inputs")
            expected_attestations = {
                str(entry["transactionId"]): str(
                    entry["attestation"]["runDigest"]
                )
                for entry in packet["objectiveAttestations"]
            }
            if (
                not isinstance(manifest_inputs, dict)
                or manifest_inputs.get(
                    "objectiveAttestationRunDigestsByTransactionId"
                )
                != expected_attestations
            ):
                raise MathFlowError(
                    "validity-v4 manifest does not bind its objective attestations"
                )
        claims = packet.get("claims")
        dependency_ids = packet.get(
            "declaredReferenceTransactionIds"
            if validity_version in {3, 4}
            else "dependencyTransactionIds"
        )
        if not isinstance(claims, list) or not isinstance(dependency_ids, list):
            raise MathFlowError("validity dependency packet has invalid claim data")
        assessments = (
            _validate_assessments_v3(
                {"assessments": judgment.get("assessments")},
                claims,
                {str(item) for item in dependency_ids},
            )
            if validity_version in {3, 4}
            else _validate_assessments(
                {"assessments": judgment.get("assessments")},
                claims,
                {str(item) for item in dependency_ids},
            )
        )
        stance = {
            "valid": "supports",
            "invalid": "refutes",
            "indeterminate": "uncertain",
        }
        expected_findings = [
            {
                "claimKey": assessment["claimKey"],
                "stance": stance[str(assessment["status"])],
                "summary": assessment["summary"],
                "subjectTransactionIds": [str(packet["subjectTransactionId"])],
                "evidenceTransactionIds": assessment["evidenceTransactionIds"],
            }
            for assessment in assessments
        ]
        if findings != expected_findings:
            raise MathFlowError("validity finding index does not match its assessments")
    if kind == "reconciliation":
        reconciliation = judgment.get("reconciliation")
        if (
            not isinstance(reconciliation, dict)
            or set(reconciliation)
            != {"conflictId", "inputJudgmentIds", "outcome", "summary"}
            or reconciliation.get("outcome") not in RECONCILIATION_OUTCOMES
        ):
            raise MathFlowError("reconciliation judgment has invalid provenance")
    judgment_id = judgment.get("judgmentId")
    core = {key: value for key, value in judgment.items() if key != "judgmentId"}
    expected = f"sha256:{sha256_json(core)}"
    if judgment_id != expected:
        raise MathFlowError("judgment ID does not match its content")
    report = read_verified_artifact(bundle_dir, manifest, "judgment-report")
    if judgment.get("reportDigest") != sha256_bytes(report):
        raise MathFlowError("judgment report digest does not match its record")
    return manifest, judgment, manifest_digest


def _reusable_judgment_history(
    root: Path,
    problem: str,
    head: str,
    source: dict[str, object],
    judgment: dict[str, object],
) -> bool:
    """Verify that a historical judgment remains an input to this ledger.

    A judgment's problem-ledger digest intentionally describes the ledger at the
    time of judgment.  Requiring it to equal the current digest would prevent an
    append-only ledger from reusing any earlier judgment.  Instead, reconstruct
    and verify that historical ledger, require it to be an ancestor of the
    current ledger, and confirm that its problem statement, subjects, and cited
    transaction evidence still have the same meaning in the current ledger.
    """

    if judgment.get("problemId") != problem:
        return False
    judgment_head = judgment.get("ledgerHead")
    if not isinstance(judgment_head, str):  # load_judgment_bundle is stricter; defensive here.
        raise MathFlowError("published judgment has no ledger head")
    if head == "WORKTREE":
        return judgment_head == source["ledgerHead"]
    if not is_ancestor(root, judgment_head, str(source["ledgerHead"])):
        return False

    historical = load_source(root, problem, judgment_head)
    if historical["problemLedgerDigest"] != judgment.get("problemLedgerDigest"):
        raise MathFlowError("published judgment does not match its historical problem ledger")
    current_statement = read_at(
        root, str(source["ledgerHead"]), f"problems/{problem}/problem.md"
    )
    historical_statement = read_at(
        root, judgment_head, f"problems/{problem}/problem.md"
    )
    if current_statement != historical_statement:
        return False

    historical_positions = {
        str(item["transactionId"]): int(item["ordinal"])
        for item in historical["transactions"]
    }
    current_positions = {
        str(item["transactionId"]): int(item["ordinal"])
        for item in source["transactions"]
    }
    for subject in judgment["subjects"]:
        subject_id = str(subject["id"])
        position = subject["ledgerPosition"]
        if historical_positions.get(subject_id) != position:
            raise MathFlowError(
                f"published judgment subject is outside its historical ledger: {subject_id}"
            )
        if current_positions.get(subject_id) != position:
            return False
    evidence_ids = {
        str(transaction_id)
        for finding in judgment["findings"]
        for transaction_id in finding["evidenceTransactionIds"]
    }
    if not evidence_ids <= historical_positions.keys():
        raise MathFlowError("published judgment cites evidence outside its historical ledger")
    return evidence_ids <= current_positions.keys()


def _published_primary_judgment_bundles(
    root: Path,
    projection_root: Path,
    problem: str,
    judge_path: Path,
    head: str,
) -> tuple[dict[str, object], dict[str, object], list[dict[str, object]]]:
    """Load verified reusable primary judgments from the published object index."""

    root = root.resolve()
    projection_root = projection_root.resolve()
    spec = load_judge_spec(judge_path)
    if spec["implementation"] not in PRIMARY_JUDGMENT_IMPLEMENTATIONS:
        raise MathFlowError("judgment planning requires a primary judge spec")
    judge_identity = {"id": spec["id"], "digest": f"sha256:{sha256_json(spec)}"}
    source = load_source(root, problem, head)
    index_path = projection_root / "indexes" / "problems" / problem / "runs.json"
    if not index_path.exists():
        return source, spec, []
    try:
        entries = json.loads(index_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise MathFlowError(f"could not read projection judgment index: {exc}") from exc
    if not isinstance(entries, list) or any(not isinstance(item, dict) for item in entries):
        raise MathFlowError("projection judgment index must be an object array")

    by_judgment_id: dict[str, dict[str, object]] = {}
    judgment_id_by_subject: dict[str, str] = {}
    for entry in sorted(
        entries,
        key=lambda item: (str(item.get("runDigest", "")), str(item.get("path", ""))),
    ):
        if entry.get("runKind") != "judgment":
            continue
        relative = entry.get("path")
        expected_digest = entry.get("runDigest")
        if not isinstance(relative, str) or not isinstance(expected_digest, str):
            raise MathFlowError("projection judgment index entry is incomplete")
        target = (projection_root / relative).resolve()
        try:
            target.relative_to(projection_root)
        except ValueError as exc:
            raise MathFlowError(
                f"projection judgment path escapes its root: {relative}"
            ) from exc
        _, judgment, run_digest = load_judgment_bundle(target)
        if run_digest != expected_digest:
            raise MathFlowError(
                f"projection judgment digest does not match its index: {relative}"
            )
        if (
            judgment.get("judgmentKind") != "primary"
            or judgment.get("judgeSpec") != judge_identity
            or not _reusable_judgment_history(root, problem, head, source, judgment)
        ):
            continue
        judgment_id = str(judgment["judgmentId"])
        candidate = {
            "source": "published",
            "path": str(target),
            "publishedPath": relative,
            "runDigest": run_digest,
            "judgmentId": judgment_id,
            "ledgerHead": judgment["ledgerHead"],
            "problemLedgerDigest": judgment["problemLedgerDigest"],
            "subjectTransactionIds": [
                str(subject["id"]) for subject in judgment["subjects"]
            ],
        }
        for subject_id in candidate["subjectTransactionIds"]:
            existing_judgment_id = judgment_id_by_subject.get(subject_id)
            if (
                existing_judgment_id is not None
                and existing_judgment_id != judgment_id
            ):
                raise MathFlowError(
                    "published index contains multiple distinct reusable primary "
                    "judgments for judge "
                    f"{judge_identity['digest']} and subject {subject_id}"
                )
            judgment_id_by_subject[subject_id] = judgment_id
        existing = by_judgment_id.get(judgment_id)
        if existing is None or (str(candidate["runDigest"]), str(candidate["path"])) < (
            str(existing["runDigest"]),
            str(existing["path"]),
        ):
            by_judgment_id[judgment_id] = candidate
    bundles = sorted(
        by_judgment_id.values(),
        key=lambda item: (str(item["judgmentId"]), str(item["runDigest"])),
    )
    return source, spec, bundles


def _partition_attestation_ready_transactions(
    root: Path,
    projection_root: Path,
    problem: str,
    head: str,
    transactions: list[dict[str, object]],
) -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    ready: list[dict[str, object]] = []
    deferred: list[dict[str, object]] = []
    for transaction in transactions:
        transaction_id = str(transaction["transactionId"])
        status = objective_attestation_status(
            root, projection_root, problem, transaction_id, head
        )
        item = {
            "transactionId": transaction_id,
            "ordinal": int(transaction["ordinal"]),
            "contributionId": str(transaction["contributionId"]),
        }
        if status["requested"] and not status["terminal"]:
            deferred.append(
                {
                    **item,
                    "reasonCode": "objective-attestation-pending",
                    "requestDigest": status["requestDigest"],
                }
            )
        else:
            ready.append(item)
    return ready, deferred


def _partition_reference_attestation_ready_transactions(
    root: Path,
    projection_root: Path,
    problem: str,
    head: str,
    source: dict[str, object],
    transactions: list[dict[str, object]],
) -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    """Gate one v4 subject on only its own and its declared references' requests."""

    ready: list[dict[str, object]] = []
    deferred: list[dict[str, object]] = []
    status_by_transaction: dict[str, dict[str, object]] = {}
    for transaction in transactions:
        transaction_id = str(transaction["transactionId"])
        claims = contribution_claims(
            root,
            problem,
            source,
            head,
            transaction_id,
        )
        reference_ids = list(
            dict.fromkeys(
                str(reference)
                for claim in claims
                for reference in claim["dependencyTransactionIds"]
            )
        )
        scoped = [
            (transaction_id, "subject"),
            *((reference, "declared-reference") for reference in reference_ids),
        ]
        pending: list[dict[str, object]] = []
        for evidence_transaction_id, relation in scoped:
            status = status_by_transaction.get(evidence_transaction_id)
            if status is None:
                status = objective_attestation_status(
                    root,
                    projection_root,
                    problem,
                    evidence_transaction_id,
                    head,
                )
                status_by_transaction[evidence_transaction_id] = status
            if status["requested"] and not status["terminal"]:
                pending.append(
                    {
                        "transactionId": evidence_transaction_id,
                        "relation": relation,
                        "requestDigest": status["requestDigest"],
                    }
                )
        item = {
            "transactionId": transaction_id,
            "ordinal": int(transaction["ordinal"]),
            "contributionId": str(transaction["contributionId"]),
        }
        if pending:
            deferred.append(
                {
                    **item,
                    "reasonCode": "objective-attestation-pending",
                    "pendingObjectiveAttestations": pending,
                }
            )
        else:
            ready.append(item)
    return ready, deferred


def plan_primary_judgment_coverage(
    root: Path,
    projection_root: Path,
    problem: str,
    judge_path: Path,
    head: str,
    subject_transaction_id: str | None = None,
) -> dict[str, object]:
    """Find uncovered transactions, optionally for exactly one targeted subject."""

    root = root.resolve()
    projection_root = projection_root.resolve()
    source, spec, published_bundles = _published_primary_judgment_bundles(
        root, projection_root, problem, judge_path, head
    )
    judge_digest = f"sha256:{sha256_json(spec)}"
    transactions = list(source["transactions"])
    if subject_transaction_id is not None:
        transactions_by_id = {
            str(transaction["transactionId"]): transaction
            for transaction in transactions
        }
        target = transactions_by_id.get(subject_transaction_id)
        if target is None:
            raise MathFlowError(
                "target judgment subject is outside the current problem ledger: "
                f"{subject_transaction_id}"
            )
        transactions = [target]
    covered = {
        subject_id
        for bundle in published_bundles
        for subject_id in bundle["subjectTransactionIds"]
    }

    missing_candidates = [
        {
            "transactionId": str(transaction["transactionId"]),
            "ordinal": int(transaction["ordinal"]),
            "contributionId": str(transaction["contributionId"]),
        }
        for transaction in transactions
        if transaction["transactionId"] not in covered
    ]
    deferred: list[dict[str, object]] = []
    if spec["implementation"] == "openrouter-validity-judgment-v4":
        missing, deferred = _partition_reference_attestation_ready_transactions(
            root,
            projection_root,
            problem,
            head,
            source,
            missing_candidates,
        )
    elif spec["implementation"] == "openrouter-validity-judgment-v3":
        missing, deferred = _partition_attestation_ready_transactions(
            root, projection_root, problem, head, missing_candidates
        )
    else:
        missing = missing_candidates
    result = {
        "schemaVersion": 1,
        "problemId": problem,
        "ledgerHead": source["ledgerHead"],
        "judgeSpec": {"id": spec["id"], "digest": judge_digest},
        "coveredTransactionIds": sorted(covered),
        "publishedBundles": published_bundles,
        "missingTransactions": missing,
        "matrix": {
            "include": [
                {
                    "transactionId": item["transactionId"],
                    "ordinal": item["ordinal"],
                }
                for item in missing
            ]
        },
    }
    if spec["implementation"] in {
        "openrouter-validity-judgment-v3",
        "openrouter-validity-judgment-v4",
    }:
        result["deferredTransactions"] = deferred
    if subject_transaction_id is not None:
        result["targetSubjectTransactionId"] = subject_transaction_id
    return result


def plan_primary_judgment_inputs(
    root: Path,
    projection_root: Path,
    problem: str,
    judge_path: Path,
    head: str,
    additional_roots: list[Path] | None = None,
    expected_new_subject_ids: list[str] | None = None,
    target_subject_transaction_id: str | None = None,
) -> dict[str, object]:
    """Plan verified primary inputs for complete or targeted formation.

    Published judgments are reusable across knowledge lanes.  Additional roots
    hold newly produced workflow artifacts and must cover exactly the subjects
    from the preceding coverage plan when that expectation is supplied.
    Untargeted mode requires every attestation-ready ledger subject. Targeted
    mode requires its exact ready subject and reports other ready omissions in
    ``pendingTransactions`` so callers can apply their governed formation
    barrier without discarding published work.
    """

    root = root.resolve()
    projection_root = projection_root.resolve()
    source, spec, published = _published_primary_judgment_bundles(
        root, projection_root, problem, judge_path, head
    )
    ledger_by_id = {
        str(item["transactionId"]): item for item in source["transactions"]
    }
    if (
        target_subject_transaction_id is not None
        and target_subject_transaction_id not in ledger_by_id
    ):
        raise MathFlowError(
            "target judgment subject is outside the current problem ledger: "
            f"{target_subject_transaction_id}"
        )
    expected = None if expected_new_subject_ids is None else list(expected_new_subject_ids)
    if expected is not None and len(expected) != len(set(expected)):
        raise MathFlowError("expected new judgment subjects contain duplicates")
    if target_subject_transaction_id is not None and any(
        subject_id != target_subject_transaction_id for subject_id in expected or []
    ):
        raise MathFlowError(
            "targeted judgment inputs may expect only the targeted subject"
        )

    additional: list[dict[str, object]] = []
    for search_root in additional_roots or []:
        verified = verify_primary_judgment_artifacts(
            root, search_root, problem, judge_path, head
        )
        for bundle in verified["bundles"]:
            bundle_dir = Path(str(bundle["path"]))
            _, judgment, _ = load_judgment_bundle(bundle_dir)
            additional.append(
                {
                    "source": "additional",
                    "path": str(bundle_dir.resolve()),
                    "runDigest": bundle["runDigest"],
                    "judgmentId": bundle["judgmentId"],
                    "ledgerHead": judgment["ledgerHead"],
                    "problemLedgerDigest": judgment["problemLedgerDigest"],
                    "subjectTransactionIds": list(bundle["subjectTransactionIds"]),
                }
            )

    additional_ids = [str(item["judgmentId"]) for item in additional]
    if len(additional_ids) != len(set(additional_ids)):
        raise MathFlowError("additional judgment inputs contain a duplicate judgment")
    additional_subjects = {
        str(subject_id)
        for bundle in additional
        for subject_id in bundle["subjectTransactionIds"]
    }
    if expected is not None and additional_subjects != set(expected):
        difference = set(expected) - additional_subjects or additional_subjects - set(expected)
        raise MathFlowError(
            f"additional judgment subjects do not match the current plan: {sorted(difference)[0]}"
        )

    published_subjects = {
        str(subject_id)
        for bundle in published
        for subject_id in bundle["subjectTransactionIds"]
    }
    overlap = published_subjects & additional_subjects
    if overlap:
        if target_subject_transaction_id is None:
            raise MathFlowError(
                f"new judgment duplicates a published subject: {sorted(overlap)[0]}"
            )
        published_ids_by_subject: dict[str, set[str]] = {}
        for bundle in published:
            for subject_id in bundle["subjectTransactionIds"]:
                published_ids_by_subject.setdefault(str(subject_id), set()).add(
                    str(bundle["judgmentId"])
                )
        retained_additional: list[dict[str, object]] = []
        for bundle in additional:
            judgment_id = str(bundle["judgmentId"])
            overlapping_subjects = set(bundle["subjectTransactionIds"]) & overlap
            if overlapping_subjects:
                if any(
                    published_ids_by_subject.get(str(subject_id)) != {judgment_id}
                    for subject_id in overlapping_subjects
                ):
                    raise MathFlowError(
                        "new targeted judgment conflicts with a published subject: "
                        f"{sorted(str(item) for item in overlapping_subjects)[0]}"
                    )
                continue
            retained_additional.append(bundle)
        additional = retained_additional
        additional_subjects = {
            str(subject_id)
            for bundle in additional
            for subject_id in bundle["subjectTransactionIds"]
        }
    combined_by_id = {str(item["judgmentId"]): item for item in published}
    for item in additional:
        judgment_id = str(item["judgmentId"])
        if judgment_id in combined_by_id:
            raise MathFlowError(f"new judgment is already published: {judgment_id}")
        combined_by_id[judgment_id] = item
    combined = sorted(
        combined_by_id.values(),
        key=lambda item: (str(item["judgmentId"]), str(item["runDigest"])),
    )
    ledger_ids = set(ledger_by_id)
    combined_subjects = published_subjects | additional_subjects
    missing = ledger_ids - combined_subjects
    deferred: list[dict[str, object]] = []
    ready: list[dict[str, object]] = []
    if missing and spec["implementation"] in {
        "openrouter-validity-judgment-v3",
        "openrouter-validity-judgment-v4",
    }:
        missing_transactions = [
            transaction
            for transaction in source["transactions"]
            if transaction["transactionId"] in missing
        ]
        if spec["implementation"] == "openrouter-validity-judgment-v4":
            ready, deferred = _partition_reference_attestation_ready_transactions(
                root,
                projection_root,
                problem,
                head,
                source,
                missing_transactions,
            )
        else:
            ready, deferred = _partition_attestation_ready_transactions(
                root, projection_root, problem, head, missing_transactions
            )
    elif missing:
        ready = [
            {
                "transactionId": str(transaction["transactionId"]),
                "ordinal": int(transaction["ordinal"]),
                "contributionId": str(transaction["contributionId"]),
            }
            for transaction in source["transactions"]
            if transaction["transactionId"] in missing
        ]

    pending: list[dict[str, object]] = []
    if target_subject_transaction_id is None:
        if ready:
            raise MathFlowError(
                "formation judgment inputs omit an attestation-ready subject: "
                f"{ready[0]['transactionId']}"
            )
    else:
        ready_ids = {str(item["transactionId"]) for item in ready}
        if target_subject_transaction_id in ready_ids:
            raise MathFlowError(
                "targeted formation inputs omit their ready subject: "
                f"{target_subject_transaction_id}"
            )
        pending = ready

    if missing and not ready and not deferred:
        raise MathFlowError(
            f"formation judgment inputs do not cover the current ledger: {sorted(missing)[0]}"
        )
    result = {
        "schemaVersion": 1,
        "problemId": problem,
        "ledgerHead": source["ledgerHead"],
        "problemLedgerDigest": source["problemLedgerDigest"],
        "judgeSpec": {
            "id": spec["id"],
            "digest": f"sha256:{sha256_json(spec)}",
        },
        "expectedNewSubjectTransactionIds": expected or [],
        "coveredSubjectTransactionIds": sorted(combined_subjects),
        "publishedBundles": published,
        "newBundles": sorted(
            additional,
            key=lambda item: (str(item["judgmentId"]), str(item["runDigest"])),
        ),
        "bundles": combined,
    }
    if spec["implementation"] in {
        "openrouter-validity-judgment-v3",
        "openrouter-validity-judgment-v4",
    }:
        result["deferredTransactions"] = deferred
    if target_subject_transaction_id is not None:
        result["targetSubjectTransactionId"] = target_subject_transaction_id
        result["pendingTransactions"] = pending
    return result


def verify_primary_judgment_artifacts(
    root: Path,
    search_root: Path,
    problem: str,
    judge_path: Path,
    head: str,
    expected_subject_ids: list[str] | None = None,
    allow_expected_subset: bool = False,
    retain_expected_subset: bool = False,
) -> dict[str, object]:
    """Discover and verify a primary-judgment artifact batch.

    download-artifact may extract one matching artifact directly into its target
    directory while extracting multiple matches into per-artifact directories.
    Discovering manifests recursively supports both layouts without weakening
    bundle, judge, ledger, or expected-subject validation.  Partial publication
    mode accepts a nonempty subset of an explicit frozen plan, but never an
    artifact for a subject outside that plan. Resume filtering first verifies
    every candidate, then retains only whole bundles contained in the frozen
    plan; it never splits a mixed-subject bundle.
    """

    root = root.resolve()
    search_root = search_root.resolve()
    if not search_root.is_dir():
        raise MathFlowError(f"judgment artifact directory does not exist: {search_root}")
    spec = load_judge_spec(judge_path)
    if spec.get("implementation") not in PRIMARY_JUDGMENT_IMPLEMENTATIONS:
        raise MathFlowError("judgment artifact verification requires a primary judge spec")
    judge_digest = f"sha256:{sha256_json(spec)}"
    source = load_source(root, problem, head)
    transactions = {
        str(item["transactionId"]): int(item["ordinal"])
        for item in source["transactions"]
    }
    expected = list(expected_subject_ids or [])
    if len(expected) != len(set(expected)):
        raise MathFlowError("expected judgment subjects contain duplicates")
    if allow_expected_subset and not expected:
        raise MathFlowError(
            "partial judgment artifact verification requires expected subjects"
        )
    if retain_expected_subset and not expected:
        raise MathFlowError(
            "resume judgment artifact filtering requires expected subjects"
        )
    if allow_expected_subset and retain_expected_subset:
        raise MathFlowError(
            "judgment artifact subset modes are mutually exclusive"
        )
    unknown_expected = set(expected) - transactions.keys()
    if unknown_expected:
        raise MathFlowError(
            f"expected judgment subject is outside the current ledger: {sorted(unknown_expected)[0]}"
        )

    candidates = sorted(
        {
            manifest.parent.resolve()
            for manifest in search_root.rglob("run.json")
            if manifest.is_file() and not manifest.is_symlink()
        },
        key=str,
    )
    if not candidates:
        raise MathFlowError("no judgment bundles were found in the downloaded artifacts")

    bundles: list[dict[str, object]] = []
    observed_judgments: set[str] = set()
    observed_subjects: set[str] = set()
    for bundle_dir in candidates:
        try:
            bundle_dir.relative_to(search_root)
        except ValueError as exc:  # pragma: no cover - resolve/rglob defensive check
            raise MathFlowError("judgment bundle escapes the artifact directory") from exc
        manifest, judgment, run_digest = load_judgment_bundle(bundle_dir)
        judgment_id = str(judgment["judgmentId"])
        if judgment_id in observed_judgments:
            raise MathFlowError(f"downloaded judgment artifacts contain a duplicate: {judgment_id}")
        if judgment.get("judgmentKind") != "primary":
            raise MathFlowError(f"downloaded artifact is not a primary judgment: {bundle_dir}")
        if judgment.get("problemId") != problem:
            raise MathFlowError("downloaded judgment belongs to another problem")
        if judgment.get("judgeSpec") != {"id": spec["id"], "digest": judge_digest}:
            raise MathFlowError("downloaded judgment does not match the approved primary judge")
        if judgment.get("problemLedgerDigest") != source["problemLedgerDigest"]:
            raise MathFlowError("downloaded judgment is stale for the current problem ledger")
        judgment_head = str(judgment["ledgerHead"])
        if head != "WORKTREE" and not is_ancestor(
            root, judgment_head, str(source["ledgerHead"])
        ):
            raise MathFlowError("downloaded judgment ledger is not an ancestor of the current head")

        subject_ids: list[str] = []
        for subject in judgment["subjects"]:
            subject_id = str(subject["id"])
            if transactions.get(subject_id) != subject["ledgerPosition"]:
                raise MathFlowError(
                    f"downloaded judgment subject is outside the current ledger: {subject_id}"
                )
            if subject_id in observed_subjects:
                raise MathFlowError(
                    f"downloaded judgments assess the same subject more than once: {subject_id}"
                )
            observed_subjects.add(subject_id)
            subject_ids.append(subject_id)
        observed_judgments.add(judgment_id)
        bundles.append(
            {
                "path": str(bundle_dir),
                "runDigest": run_digest,
                "judgmentId": judgment_id,
                "subjectTransactionIds": subject_ids,
            }
        )

    expected_set = set(expected)
    rejected_bundles: list[dict[str, object]] = []
    if retain_expected_subset:
        retained: list[dict[str, object]] = []
        retained_subjects: set[str] = set()
        for bundle in bundles:
            bundle_subjects = {
                str(item) for item in bundle["subjectTransactionIds"]
            }
            unexpected = bundle_subjects - expected_set
            if unexpected:
                rejected_bundles.append(
                    {
                        "judgmentId": str(bundle["judgmentId"]),
                        "runDigest": str(bundle["runDigest"]),
                        "subjectTransactionIds": sorted(bundle_subjects),
                        "unexpectedSubjectTransactionIds": sorted(unexpected),
                    }
                )
                continue
            retained.append(bundle)
            retained_subjects.update(bundle_subjects)
        if not retained_subjects:
            raise MathFlowError(
                "resume judgment artifacts do not contain a retained planned subject"
            )
        bundles = retained
        observed_subjects = retained_subjects
    elif allow_expected_subset:
        if not observed_subjects:
            raise MathFlowError(
                "partial judgment artifacts do not contain a planned subject"
            )
        extra = observed_subjects - expected_set
        if extra:
            raise MathFlowError(
                "downloaded judgment subject is outside the current plan: "
                f"{sorted(extra)[0]}"
            )
    elif expected and observed_subjects != expected_set:
        missing = expected_set - observed_subjects
        extra = observed_subjects - expected_set
        detail = sorted(missing or extra)[0]
        raise MathFlowError(
            f"downloaded judgment subjects do not match the current plan: {detail}"
        )
    result: dict[str, object] = {
        "schemaVersion": 1,
        "problemId": problem,
        "ledgerHead": source["ledgerHead"],
        "problemLedgerDigest": source["problemLedgerDigest"],
        "judgeSpec": {"id": spec["id"], "digest": judge_digest},
        "expectedSubjectTransactionIds": expected,
        "bundles": bundles,
    }
    if allow_expected_subset or retain_expected_subset:
        result["missingExpectedSubjectTransactionIds"] = sorted(
            expected_set - observed_subjects
        )
    if retain_expected_subset:
        result["rejectedBundles"] = rejected_bundles
        result["rejectedSubjectTransactionIds"] = sorted(
            {
                str(subject_id)
                for bundle in rejected_bundles
                for subject_id in bundle["unexpectedSubjectTransactionIds"]
            }
        )
    return result


def detect_conflicts(bundle_dirs: list[Path]) -> list[dict[str, object]]:
    grouped: dict[tuple[str, str], list[dict[str, str]]] = {}
    for bundle_dir in bundle_dirs:
        _, judgment, _ = load_judgment_bundle(bundle_dir)
        if judgment.get("judgmentKind") != "primary":
            continue
        problem = judgment.get("problemId")
        judgment_id = judgment.get("judgmentId")
        findings = judgment.get("findings")
        if not isinstance(problem, str) or not isinstance(judgment_id, str) or not isinstance(findings, list):
            raise MathFlowError("judgment record is missing conflict-routing fields")
        for finding in findings:
            if not isinstance(finding, dict):
                raise MathFlowError("judgment contains an invalid finding")
            claim_key = finding.get("claimKey")
            stance = finding.get("stance")
            summary = finding.get("summary")
            if not all(isinstance(item, str) for item in (claim_key, stance, summary)):
                raise MathFlowError("judgment finding is missing conflict-routing fields")
            grouped.setdefault((problem, claim_key), []).append(
                {"judgmentId": judgment_id, "stance": stance, "summary": summary}
            )

    conflicts: list[dict[str, object]] = []
    for (problem, claim_key), findings in sorted(grouped.items()):
        supporting_ids = {
            item["judgmentId"] for item in findings if item["stance"] == "supports"
        }
        refuting_ids = {
            item["judgmentId"] for item in findings if item["stance"] == "refutes"
        }
        if not supporting_ids or not refuting_ids or not any(
            support != refutation
            for support in supporting_ids
            for refutation in refuting_ids
        ):
            continue
        unique = {
            (item["judgmentId"], item["stance"], item["summary"]): item
            for item in findings
        }
        ordered = [unique[key] for key in sorted(unique)]
        core: dict[str, object] = {
            "schemaVersion": 1,
            "problemId": problem,
            "claimKey": claim_key,
            "status": "open",
            "judgments": ordered,
        }
        conflicts.append({**core, "conflictId": f"sha256:{sha256_json(core)}"})
    return conflicts


def _published_reconciliation_bundles(
    root: Path,
    projection_root: Path,
    problem: str,
    head: str,
    source: dict[str, object],
    judge_identity: dict[str, str],
    conflicts: dict[str, dict[str, object]],
) -> list[dict[str, object]]:
    index_path = projection_root / "indexes" / "problems" / problem / "runs.json"
    if not index_path.exists():
        return []
    try:
        entries = json.loads(index_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise MathFlowError(f"could not read projection reconciliation index: {exc}") from exc
    if not isinstance(entries, list) or any(not isinstance(item, dict) for item in entries):
        raise MathFlowError("projection reconciliation index must be an object array")

    by_judgment_id: dict[str, dict[str, object]] = {}
    judgment_id_by_conflict: dict[str, str] = {}
    for entry in sorted(
        entries,
        key=lambda item: (str(item.get("runDigest", "")), str(item.get("path", ""))),
    ):
        if entry.get("runKind") != "judgment":
            continue
        relative = entry.get("path")
        expected_digest = entry.get("runDigest")
        if not isinstance(relative, str) or not isinstance(expected_digest, str):
            raise MathFlowError("projection reconciliation index entry is incomplete")
        target = (projection_root / relative).resolve()
        try:
            target.relative_to(projection_root)
        except ValueError as exc:
            raise MathFlowError(
                f"projection reconciliation path escapes its root: {relative}"
            ) from exc
        _, judgment, run_digest = load_judgment_bundle(target)
        if run_digest != expected_digest:
            raise MathFlowError(
                f"projection reconciliation digest does not match its index: {relative}"
            )
        reconciliation = judgment.get("reconciliation")
        if (
            judgment.get("judgmentKind") != "reconciliation"
            or judgment.get("judgeSpec") != judge_identity
            or not isinstance(reconciliation, dict)
            or not _reusable_judgment_history(root, problem, head, source, judgment)
        ):
            continue
        conflict_id = str(reconciliation["conflictId"])
        conflict = conflicts.get(conflict_id)
        if conflict is None:
            continue
        required_ids = {
            str(item["judgmentId"]) for item in conflict["judgments"]
        }
        if set(reconciliation["inputJudgmentIds"]) != required_ids:
            raise MathFlowError(
                f"published reconciliation inputs do not match its conflict: {conflict_id}"
            )
        if any(
            finding.get("claimKey") != conflict["claimKey"]
            for finding in judgment["findings"]
        ):
            raise MathFlowError(
                f"published reconciliation finding does not match its conflict: {conflict_id}"
            )
        judgment_id = str(judgment["judgmentId"])
        candidate = {
            "source": "published",
            "path": str(target),
            "publishedPath": relative,
            "runDigest": run_digest,
            "judgmentId": judgment_id,
            "conflictId": conflict_id,
            "ledgerHead": judgment["ledgerHead"],
            "problemLedgerDigest": judgment["problemLedgerDigest"],
            "subjectTransactionIds": [
                str(subject["id"]) for subject in judgment["subjects"]
            ],
        }
        existing_judgment_id = judgment_id_by_conflict.get(conflict_id)
        if (
            existing_judgment_id is not None
            and existing_judgment_id != judgment_id
        ):
            raise MathFlowError(
                "published index contains multiple distinct reusable reconciliation "
                "judgments for judge "
                f"{judge_identity['digest']} and conflict {conflict_id}"
            )
        judgment_id_by_conflict[conflict_id] = judgment_id
        existing = by_judgment_id.get(judgment_id)
        if existing is None or (str(candidate["runDigest"]), str(candidate["path"])) < (
            str(existing["runDigest"]),
            str(existing["path"]),
        ):
            by_judgment_id[judgment_id] = candidate
    return sorted(
        by_judgment_id.values(),
        key=lambda item: (
            str(item["conflictId"]),
            str(item["judgmentId"]),
            str(item["runDigest"]),
        ),
    )


def _additional_reconciliation_bundles(
    root: Path,
    search_roots: list[Path],
    problem: str,
    head: str,
    source: dict[str, object],
    judge_identity: dict[str, str],
    conflicts: dict[str, dict[str, object]],
) -> list[dict[str, object]]:
    candidates: set[Path] = set()
    for raw_root in search_roots:
        search_root = raw_root.resolve()
        if not search_root.is_dir():
            raise MathFlowError(
                f"reconciliation artifact directory does not exist: {search_root}"
            )
        candidates.update(
            manifest.parent.resolve()
            for manifest in search_root.rglob("run.json")
            if manifest.is_file() and not manifest.is_symlink()
        )
    if search_roots and not candidates:
        raise MathFlowError("no reconciliation bundles were found in the artifacts")

    bundles: list[dict[str, object]] = []
    observed_judgments: set[str] = set()
    observed_conflicts: set[str] = set()
    for bundle_dir in sorted(candidates, key=str):
        _, judgment, run_digest = load_judgment_bundle(bundle_dir)
        reconciliation = judgment.get("reconciliation")
        if judgment.get("judgmentKind") != "reconciliation" or not isinstance(
            reconciliation, dict
        ):
            raise MathFlowError(
                f"additional artifact is not a reconciliation judgment: {bundle_dir}"
            )
        if judgment.get("problemId") != problem:
            raise MathFlowError("additional reconciliation belongs to another problem")
        if judgment.get("judgeSpec") != judge_identity:
            raise MathFlowError(
                "additional reconciliation does not match the approved judge"
            )
        if judgment.get("problemLedgerDigest") != source["problemLedgerDigest"]:
            raise MathFlowError(
                "additional reconciliation is stale for the current problem ledger"
            )
        judgment_head = str(judgment["ledgerHead"])
        if head != "WORKTREE" and not is_ancestor(
            root, judgment_head, str(source["ledgerHead"])
        ):
            raise MathFlowError(
                "additional reconciliation ledger is not an ancestor of the current head"
            )
        conflict_id = str(reconciliation["conflictId"])
        conflict = conflicts.get(conflict_id)
        if conflict is None:
            raise MathFlowError(
                f"additional reconciliation targets a non-current conflict: {conflict_id}"
            )
        required_ids = {
            str(item["judgmentId"]) for item in conflict["judgments"]
        }
        if set(reconciliation["inputJudgmentIds"]) != required_ids:
            raise MathFlowError(
                f"additional reconciliation inputs do not match its conflict: {conflict_id}"
            )
        if any(
            finding.get("claimKey") != conflict["claimKey"]
            for finding in judgment["findings"]
        ):
            raise MathFlowError(
                f"additional reconciliation finding does not match its conflict: {conflict_id}"
            )
        judgment_id = str(judgment["judgmentId"])
        if judgment_id in observed_judgments:
            raise MathFlowError(
                f"additional reconciliations contain a duplicate judgment: {judgment_id}"
            )
        if conflict_id in observed_conflicts:
            raise MathFlowError(
                f"additional reconciliations assess the same conflict twice: {conflict_id}"
            )
        observed_judgments.add(judgment_id)
        observed_conflicts.add(conflict_id)
        bundles.append(
            {
                "source": "additional",
                "path": str(bundle_dir),
                "runDigest": run_digest,
                "judgmentId": judgment_id,
                "conflictId": conflict_id,
                "ledgerHead": judgment["ledgerHead"],
                "problemLedgerDigest": judgment["problemLedgerDigest"],
                "subjectTransactionIds": [
                    str(subject["id"]) for subject in judgment["subjects"]
                ],
            }
        )
    return sorted(
        bundles,
        key=lambda item: (
            str(item["conflictId"]),
            str(item["judgmentId"]),
            str(item["runDigest"]),
        ),
    )


def plan_reconciliation_inputs(
    root: Path,
    projection_root: Path,
    problem: str,
    primary_judge_path: Path,
    reconciliation_judge_path: Path,
    head: str,
    primary_bundle_dirs: list[Path],
    additional_roots: list[Path] | None = None,
    expected_new_conflict_ids: list[str] | None = None,
    allow_expected_subset: bool = False,
) -> dict[str, object]:
    """Derive conflicts and bind published or planned new reconciliations.

    Partial publication mode verifies a nonempty subset of the exact expected
    conflict plan.  It is only a durability path for already-produced artifacts;
    missing expected conflicts remain explicit and cannot enter formation.
    """

    root = root.resolve()
    projection_root = projection_root.resolve()
    source = load_source(root, problem, head)
    primary_spec = load_judge_spec(primary_judge_path)
    if primary_spec.get("implementation") not in PRIMARY_JUDGMENT_IMPLEMENTATIONS:
        raise MathFlowError("reconciliation planning requires a primary judge spec")
    primary_identity = {
        "id": str(primary_spec["id"]),
        "digest": f"sha256:{sha256_json(primary_spec)}",
    }
    primary_ids: set[str] = set()
    covered_subjects: set[str] = set()
    for bundle_dir in primary_bundle_dirs:
        _, judgment, _ = load_judgment_bundle(bundle_dir)
        judgment_id = str(judgment["judgmentId"])
        if (
            judgment.get("judgmentKind") != "primary"
            or judgment.get("judgeSpec") != primary_identity
            or not _reusable_judgment_history(root, problem, head, source, judgment)
        ):
            raise MathFlowError(
                f"reconciliation planner received an invalid primary judgment: {bundle_dir}"
            )
        if judgment_id in primary_ids:
            raise MathFlowError(
                f"reconciliation planner received a duplicate primary judgment: {judgment_id}"
            )
        primary_ids.add(judgment_id)
        covered_subjects.update(str(subject["id"]) for subject in judgment["subjects"])
    ledger_ids = {str(item["transactionId"]) for item in source["transactions"]}
    if covered_subjects != ledger_ids:
        difference = ledger_ids - covered_subjects or covered_subjects - ledger_ids
        raise MathFlowError(
            f"reconciliation primary inputs do not cover the current ledger: {sorted(difference)[0]}"
        )

    conflicts_list = detect_conflicts(primary_bundle_dirs)
    conflicts = {str(item["conflictId"]): item for item in conflicts_list}
    reconciliation_spec = load_judge_spec(reconciliation_judge_path)
    if reconciliation_spec.get("implementation") != "openrouter-markdown-reconciliation-v1":
        raise MathFlowError("reconciliation planning requires a reconciliation judge spec")
    reconciliation_identity = {
        "id": str(reconciliation_spec["id"]),
        "digest": f"sha256:{sha256_json(reconciliation_spec)}",
    }
    published = _published_reconciliation_bundles(
        root,
        projection_root,
        problem,
        head,
        source,
        reconciliation_identity,
        conflicts,
    )
    additional = _additional_reconciliation_bundles(
        root,
        additional_roots or [],
        problem,
        head,
        source,
        reconciliation_identity,
        conflicts,
    )
    expected = (
        None
        if expected_new_conflict_ids is None
        else list(expected_new_conflict_ids)
    )
    if expected is not None:
        if len(expected) != len(set(expected)):
            raise MathFlowError("expected reconciliation conflicts contain duplicates")
        if allow_expected_subset and not expected:
            raise MathFlowError(
                "partial reconciliation verification requires expected conflicts"
            )
        unknown = set(expected) - conflicts.keys()
        if unknown:
            raise MathFlowError(
                f"expected reconciliation targets a non-current conflict: {sorted(unknown)[0]}"
            )
        observed = {str(item["conflictId"]) for item in additional}
        if allow_expected_subset:
            if not observed:
                raise MathFlowError(
                    "partial reconciliation artifacts do not contain a planned conflict"
                )
            extra = observed - set(expected)
            if extra:
                raise MathFlowError(
                    "additional reconciliation conflict is outside the current plan: "
                    f"{sorted(extra)[0]}"
                )
        elif observed != set(expected):
            difference = set(expected) - observed or observed - set(expected)
            raise MathFlowError(
                f"additional reconciliation conflicts do not match the current plan: {sorted(difference)[0]}"
            )
    elif allow_expected_subset:
        raise MathFlowError(
            "partial reconciliation verification requires expected conflicts"
        )

    published_conflicts = {str(item["conflictId"]) for item in published}
    additional_conflicts = {str(item["conflictId"]) for item in additional}
    overlap = published_conflicts & additional_conflicts
    if overlap and not allow_expected_subset:
        raise MathFlowError(
            f"new reconciliation duplicates a published conflict: {sorted(overlap)[0]}"
        )
    combined_by_id = {str(item["judgmentId"]): item for item in published}
    for item in additional:
        if (
            allow_expected_subset
            and str(item["conflictId"]) in published_conflicts
        ):
            # Keep canonical inputs unambiguous. The additional bundle remains
            # in newBundles so independent publication can reject or identify
            # an exact already-published object without stranding its siblings.
            continue
        judgment_id = str(item["judgmentId"])
        if judgment_id in combined_by_id:
            raise MathFlowError(
                f"new reconciliation is already published: {judgment_id}"
            )
        combined_by_id[judgment_id] = item
    combined = sorted(
        combined_by_id.values(),
        key=lambda item: (
            str(item["conflictId"]),
            str(item["judgmentId"]),
            str(item["runDigest"]),
        ),
    )
    covered_conflicts = published_conflicts | additional_conflicts
    missing = [
        conflicts[conflict_id]
        for conflict_id in sorted(set(conflicts) - covered_conflicts)
    ]
    if expected is not None and missing and not allow_expected_subset:
        raise MathFlowError(
            f"reconciliation inputs do not cover current conflict: {missing[0]['conflictId']}"
        )
    result: dict[str, object] = {
        "schemaVersion": 1,
        "problemId": problem,
        "ledgerHead": source["ledgerHead"],
        "problemLedgerDigest": source["problemLedgerDigest"],
        "primaryJudgeSpec": primary_identity,
        "reconciliationJudgeSpec": reconciliation_identity,
        "primaryJudgmentIds": sorted(primary_ids),
        "conflicts": conflicts_list,
        "publishedBundles": published,
        "newBundles": additional,
        "bundles": combined,
        "missingConflicts": missing,
        "matrix": {
            "include": [
                {
                    "ordinal": ordinal,
                    "conflictId": item["conflictId"],
                    "claimKey": item["claimKey"],
                }
                for ordinal, item in enumerate(missing, start=1)
            ]
        },
    }
    if allow_expected_subset:
        expected_set = set(expected or [])
        result["missingExpectedConflictIds"] = sorted(
            expected_set - (published_conflicts | additional_conflicts)
        )
    return result
