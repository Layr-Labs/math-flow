from __future__ import annotations

import json
import re
from pathlib import Path

from .artifacts import ArtifactBundle, load_manifest, read_verified_artifact, sha256_bytes
from .errors import MathFlowError
from .hierarchical import _assistant_content, _provider_run, _request, _structured_content
from .judges import artifact_evidence, load_judge_spec, load_source
from .openrouter import OpenRouterTransport, send_chat_completion
from .repository import read_at, sha256_json
from .runs import run_envelope


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


def run_primary_judgment_bundle(
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
        raise MathFlowError("judgment command requires a parallel Markdown judgment spec")
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
        if judgment.get("problemId") != problem:
            raise MathFlowError("reconciliation input judgment belongs to another problem")
        report = read_verified_artifact(bundle_dir, manifest, "judgment-report").decode("utf-8")
        loaded[judgment_id] = (judgment, report)
    missing = required_ids - loaded.keys()
    if missing:
        raise MathFlowError(f"missing reconciliation input judgment: {sorted(missing)[0]}")

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
    if (
        manifest.get("runKind") != "judgment"
        or manifest.get("outputProfile") != "math-flow/judgment-markdown-v1"
    ):
        raise MathFlowError(f"bundle is not an immutable judgment: {bundle_dir}")
    try:
        judgment = json.loads(read_verified_artifact(bundle_dir, manifest, "judgment-record"))
    except json.JSONDecodeError as exc:
        raise MathFlowError("judgment record is not valid JSON") from exc
    if not isinstance(judgment, dict):
        raise MathFlowError("judgment record must be an object")
    required = {
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
    allowed = required | ({"reconciliation"} if kind == "reconciliation" else set())
    if (
        judgment.get("schemaVersion") != 1
        or kind not in {"primary", "reconciliation"}
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
