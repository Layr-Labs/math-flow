from __future__ import annotations

import json
import re
from pathlib import Path

from .artifacts import ArtifactBundle, load_manifest, read_verified_artifact, sha256_bytes
from .errors import MathFlowError
from .hierarchical import _assistant_content, _provider_run, _request, _structured_content
from .judges import artifact_evidence, load_judge_spec, load_source
from .openrouter import OpenRouterTransport, send_chat_completion
from .repository import is_ancestor, read_at, sha256_json
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
    if spec["implementation"] != "openrouter-markdown-judgment-v1":
        raise MathFlowError("judgment planning requires a primary Markdown judge spec")
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


def plan_primary_judgment_coverage(
    root: Path,
    projection_root: Path,
    problem: str,
    judge_path: Path,
    head: str,
) -> dict[str, object]:
    """Find ledger transactions without a published primary judgment from this judge."""

    root = root.resolve()
    projection_root = projection_root.resolve()
    source, spec, published_bundles = _published_primary_judgment_bundles(
        root, projection_root, problem, judge_path, head
    )
    judge_digest = f"sha256:{sha256_json(spec)}"
    transactions = list(source["transactions"])
    covered = {
        subject_id
        for bundle in published_bundles
        for subject_id in bundle["subjectTransactionIds"]
    }

    missing = [
        {
            "transactionId": str(transaction["transactionId"]),
            "ordinal": int(transaction["ordinal"]),
            "contributionId": str(transaction["contributionId"]),
        }
        for transaction in transactions
        if transaction["transactionId"] not in covered
    ]
    return {
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


def plan_primary_judgment_inputs(
    root: Path,
    projection_root: Path,
    problem: str,
    judge_path: Path,
    head: str,
    additional_roots: list[Path] | None = None,
    expected_new_subject_ids: list[str] | None = None,
) -> dict[str, object]:
    """Plan the complete verified primary-judgment input set for formation.

    Published judgments are reusable across knowledge lanes.  Additional roots
    hold newly produced workflow artifacts and must cover exactly the subjects
    from the preceding coverage plan when that expectation is supplied.
    """

    root = root.resolve()
    projection_root = projection_root.resolve()
    source, spec, published = _published_primary_judgment_bundles(
        root, projection_root, problem, judge_path, head
    )
    expected = None if expected_new_subject_ids is None else list(expected_new_subject_ids)
    if expected is not None and len(expected) != len(set(expected)):
        raise MathFlowError("expected new judgment subjects contain duplicates")

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
        raise MathFlowError(
            f"new judgment duplicates a published subject: {sorted(overlap)[0]}"
        )
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
    ledger_ids = {str(item["transactionId"]) for item in source["transactions"]}
    combined_subjects = published_subjects | additional_subjects
    missing = ledger_ids - combined_subjects
    if missing:
        raise MathFlowError(
            f"formation judgment inputs do not cover the current ledger: {sorted(missing)[0]}"
        )
    return {
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


def verify_primary_judgment_artifacts(
    root: Path,
    search_root: Path,
    problem: str,
    judge_path: Path,
    head: str,
    expected_subject_ids: list[str] | None = None,
) -> dict[str, object]:
    """Discover and verify a complete primary-judgment artifact batch.

    download-artifact may extract one matching artifact directly into its target
    directory while extracting multiple matches into per-artifact directories.
    Discovering manifests recursively supports both layouts without weakening
    bundle, judge, ledger, or expected-subject validation.
    """

    root = root.resolve()
    search_root = search_root.resolve()
    if not search_root.is_dir():
        raise MathFlowError(f"judgment artifact directory does not exist: {search_root}")
    spec = load_judge_spec(judge_path)
    if spec.get("implementation") != "openrouter-markdown-judgment-v1":
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

    if expected and observed_subjects != set(expected):
        missing = set(expected) - observed_subjects
        extra = observed_subjects - set(expected)
        detail = sorted(missing or extra)[0]
        raise MathFlowError(
            f"downloaded judgment subjects do not match the current plan: {detail}"
        )
    return {
        "schemaVersion": 1,
        "problemId": problem,
        "ledgerHead": source["ledgerHead"],
        "problemLedgerDigest": source["problemLedgerDigest"],
        "judgeSpec": {"id": spec["id"], "digest": judge_digest},
        "expectedSubjectTransactionIds": expected,
        "bundles": bundles,
    }


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
) -> dict[str, object]:
    """Derive current conflicts and bind their published/new reconciliations."""

    root = root.resolve()
    projection_root = projection_root.resolve()
    source = load_source(root, problem, head)
    primary_spec = load_judge_spec(primary_judge_path)
    if primary_spec.get("implementation") != "openrouter-markdown-judgment-v1":
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
        unknown = set(expected) - conflicts.keys()
        if unknown:
            raise MathFlowError(
                f"expected reconciliation targets a non-current conflict: {sorted(unknown)[0]}"
            )
        observed = {str(item["conflictId"]) for item in additional}
        if observed != set(expected):
            difference = set(expected) - observed or observed - set(expected)
            raise MathFlowError(
                f"additional reconciliation conflicts do not match the current plan: {sorted(difference)[0]}"
            )

    published_conflicts = {str(item["conflictId"]) for item in published}
    additional_conflicts = {str(item["conflictId"]) for item in additional}
    overlap = published_conflicts & additional_conflicts
    if overlap:
        raise MathFlowError(
            f"new reconciliation duplicates a published conflict: {sorted(overlap)[0]}"
        )
    combined_by_id = {str(item["judgmentId"]): item for item in published}
    for item in additional:
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
    if expected is not None and missing:
        raise MathFlowError(
            f"reconciliation inputs do not cover current conflict: {missing[0]['conflictId']}"
        )
    return {
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
                    "conflictId": item["conflictId"],
                    "claimKey": item["claimKey"],
                }
                for item in missing
            ]
        },
    }
