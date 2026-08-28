from __future__ import annotations

import copy
import re
from collections.abc import Iterable, Mapping
from pathlib import Path, PurePosixPath

from .artifacts import sha256_bytes
from .errors import MathFlowError
from .repository import list_files_at, read_bytes_at, sha256_json
from .research_topology import validate_research_program_state_versioned


GIT_SHA = re.compile(r"^[0-9a-f]{40}$")
DIGEST = re.compile(r"^sha256:[0-9a-f]{64}$")
IDENTIFIER = re.compile(r"^[a-z0-9][a-z0-9/_-]*$")
SLUG = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")

DEFAULT_CHUNK_BYTES = 64 * 1024
MAX_CHUNK_BYTES = 1024 * 1024
MAX_SAFE_TEXT_BYTES = 8 * 1024
MAX_SAFE_FACTS = 128
MAX_SAFE_ASSUMPTIONS = 128
EVIDENCE_COPY_WINDOW = 32
MIN_SHORT_EVIDENCE_COPY = 16

# ``thread`` remains accepted for replay of state-v1/v2 accounting bundles.
# State v3 exposes only program accounting nodes.
NODE_KINDS = {"program", "thread"}
SAFE_FACT_FIELDS = {
    "id",
    "condition",
    "actorVisibility",
    "affectedNodeRefs",
    "acceptedClaimKeys",
}
SAFE_FACT_ENVELOPE_FIELDS = {"facts", "assumptions"}


def _object_digest(value: object) -> str:
    return f"sha256:{sha256_json(value)}"


def _without_digest(value: Mapping[str, object], field: str) -> dict[str, object]:
    return {key: copy.deepcopy(item) for key, item in value.items() if key != field}


def _require_exact_fields(
    value: object, fields: set[str], label: str
) -> dict[str, object]:
    if not isinstance(value, dict) or set(value) != fields:
        raise MathFlowError(f"{label} has missing or unexpected fields")
    return value


def _require_text(value: object, label: str, *, max_bytes: int | None = None) -> str:
    if not isinstance(value, str) or not value.strip():
        raise MathFlowError(f"{label} must be non-empty text")
    rendered = value.strip()
    if any(ord(character) < 32 and character not in "\n\t" for character in rendered):
        raise MathFlowError(f"{label} contains a prohibited control character")
    if max_bytes is not None and len(rendered.encode("utf-8")) > max_bytes:
        raise MathFlowError(f"{label} exceeds the safe text limit")
    return rendered


def _require_identifier(value: object, label: str) -> str:
    if not isinstance(value, str) or not IDENTIFIER.fullmatch(value):
        raise MathFlowError(f"{label} must be a stable lowercase path")
    return value


def _require_digest(value: object, label: str) -> str:
    if not isinstance(value, str) or not DIGEST.fullmatch(value):
        raise MathFlowError(f"{label} must be a sha256 digest")
    return value


def _require_transaction(value: object, label: str) -> str:
    if not isinstance(value, str) or not GIT_SHA.fullmatch(value):
        raise MathFlowError(f"{label} must be a canonical transaction ID")
    return value


def _require_problem(value: object) -> str:
    if not isinstance(value, str) or not SLUG.fullmatch(value):
        raise MathFlowError("problem ID must be a lowercase hyphenated slug")
    return value


def _relative_path(value: object, label: str) -> PurePosixPath:
    if not isinstance(value, str) or not value or "\\" in value or "\x00" in value:
        raise MathFlowError(f"{label} is not a safe repository path")
    path = PurePosixPath(value)
    if path.is_absolute() or not path.parts or any(part in {"", ".", ".."} for part in path.parts):
        raise MathFlowError(f"{label} is not a safe repository path")
    if path.as_posix() != value:
        raise MathFlowError(f"{label} is not canonical POSIX form")
    return path


def _contribution_path(value: object, problem_id: str) -> PurePosixPath:
    path = _relative_path(value, "contribution path")
    if (
        len(path.parts) != 4
        or path.parts[:3] != ("problems", problem_id, "contributions")
        or not SLUG.fullmatch(path.parts[3])
    ):
        raise MathFlowError("contribution path is outside the exact problem contribution namespace")
    return path


def _framed_submission_digest(files: Iterable[tuple[str, bytes]]) -> str:
    framed = bytearray()
    for path, content in files:
        path_bytes = path.encode("utf-8")
        framed.extend(len(path_bytes).to_bytes(8, "big"))
        framed.extend(path_bytes)
        framed.extend(len(content).to_bytes(8, "big"))
        framed.extend(content)
    return sha256_bytes(bytes(framed))


def build_submission_evidence_manifest(
    *,
    problem_id: str,
    subject_transaction_id: str,
    contribution_path: str,
    files: Mapping[str, bytes],
    chunk_bytes: int = DEFAULT_CHUNK_BYTES,
) -> tuple[dict[str, object], dict[str, bytes]]:
    """Build a complete metadata-only manifest and a separate chunk store.

    ``files`` uses exact repository-relative POSIX paths. The caller is
    responsible for retrieving the files from the canonical subject tree; use
    :func:`manifest_submission_at` for the repository-backed path.
    """

    problem = _require_problem(problem_id)
    subject = _require_transaction(subject_transaction_id, "subject transaction ID")
    prefix = _contribution_path(contribution_path, problem)
    if isinstance(chunk_bytes, bool) or not isinstance(chunk_bytes, int):
        raise MathFlowError("evidence chunk size must be an integer")
    if not 1 <= chunk_bytes <= MAX_CHUNK_BYTES:
        raise MathFlowError("evidence chunk size is outside the supported range")
    if not isinstance(files, Mapping) or not files:
        raise MathFlowError("submission evidence must contain at least one file")

    normalized: list[tuple[str, bytes]] = []
    for raw_path, raw_content in files.items():
        path = _relative_path(raw_path, "submission evidence path")
        try:
            relative = path.relative_to(prefix)
        except ValueError as exc:
            raise MathFlowError(
                f"submission evidence path escapes contribution: {path}"
            ) from exc
        if not relative.parts:
            raise MathFlowError("submission evidence path must identify a file")
        if not isinstance(raw_content, bytes):
            raise MathFlowError(f"submission evidence must preserve exact bytes: {path}")
        normalized.append((path.as_posix(), raw_content))
    normalized.sort(key=lambda item: item[0])
    paths = [path for path, _ in normalized]
    if len(paths) != len(set(paths)):
        raise MathFlowError("submission evidence contains duplicate file paths")
    readme = f"{prefix.as_posix()}/README.md"
    by_path = dict(normalized)
    if readme not in by_path or not by_path[readme].strip():
        raise MathFlowError("submission evidence is missing a non-empty README.md")

    chunks: dict[str, bytes] = {}
    file_records: list[dict[str, object]] = []
    for path, content in normalized:
        chunk_records: list[dict[str, object]] = []
        for ordinal, offset in enumerate(range(0, len(content), chunk_bytes)):
            chunk = content[offset : offset + chunk_bytes]
            digest = sha256_bytes(chunk)
            existing = chunks.setdefault(digest, chunk)
            if existing != chunk:  # Defensive even though a sha256 collision is infeasible.
                raise MathFlowError("submission evidence chunk digest collision")
            chunk_records.append(
                {
                    "ordinal": ordinal,
                    "offset": offset,
                    "bytes": len(chunk),
                    "digest": digest,
                }
            )
        file_records.append(
            {
                "path": path,
                "bytes": len(content),
                "digest": sha256_bytes(content),
                "chunks": chunk_records,
            }
        )

    core: dict[str, object] = {
        "schemaVersion": 1,
        "problemId": problem,
        "subjectTransactionId": subject,
        "sourceRevision": subject,
        "contributionPath": prefix.as_posix(),
        "chunkSizeBytes": chunk_bytes,
        "totalBytes": sum(len(content) for _, content in normalized),
        "submissionDigest": _framed_submission_digest(normalized),
        "files": file_records,
    }
    manifest = {**core, "manifestDigest": _object_digest(core)}
    validate_submission_evidence_manifest(manifest)
    reconstruct_submission_evidence(manifest, chunks)
    return manifest, chunks


def manifest_submission_at(
    root: Path,
    *,
    problem_id: str,
    subject_transaction_id: str,
    contribution_path: str,
    chunk_bytes: int = DEFAULT_CHUNK_BYTES,
) -> tuple[dict[str, object], dict[str, bytes]]:
    """Manifest an exact canonical submission from its own transaction tree."""

    problem = _require_problem(problem_id)
    subject = _require_transaction(subject_transaction_id, "subject transaction ID")
    prefix = _contribution_path(contribution_path, problem).as_posix()
    paths = list_files_at(root.resolve(), subject, prefix)
    files = {path: read_bytes_at(root.resolve(), subject, path) for path in paths}
    return build_submission_evidence_manifest(
        problem_id=problem,
        subject_transaction_id=subject,
        contribution_path=prefix,
        files=files,
        chunk_bytes=chunk_bytes,
    )


def validate_submission_evidence_manifest(value: object) -> dict[str, object]:
    fields = {
        "schemaVersion",
        "problemId",
        "subjectTransactionId",
        "sourceRevision",
        "contributionPath",
        "chunkSizeBytes",
        "totalBytes",
        "submissionDigest",
        "files",
        "manifestDigest",
    }
    manifest = _require_exact_fields(value, fields, "submission evidence manifest")
    if manifest.get("schemaVersion") != 1:
        raise MathFlowError("submission evidence manifest has an unsupported version")
    problem = _require_problem(manifest.get("problemId"))
    subject = _require_transaction(
        manifest.get("subjectTransactionId"), "manifest subject transaction ID"
    )
    if manifest.get("sourceRevision") != subject:
        raise MathFlowError("submission evidence must come from the exact subject revision")
    prefix = _contribution_path(manifest.get("contributionPath"), problem)
    chunk_size = manifest.get("chunkSizeBytes")
    if isinstance(chunk_size, bool) or not isinstance(chunk_size, int) or not 1 <= chunk_size <= MAX_CHUNK_BYTES:
        raise MathFlowError("submission evidence manifest has an invalid chunk size")
    total_bytes = manifest.get("totalBytes")
    if isinstance(total_bytes, bool) or not isinstance(total_bytes, int) or total_bytes < 1:
        raise MathFlowError("submission evidence manifest has an invalid total byte count")
    _require_digest(manifest.get("submissionDigest"), "submission digest")
    files = manifest.get("files")
    if not isinstance(files, list) or not files:
        raise MathFlowError("submission evidence manifest must list files")

    previous_path: str | None = None
    observed_total = 0
    saw_readme = False
    for file_record in files:
        file_fields = {"path", "bytes", "digest", "chunks"}
        record = _require_exact_fields(file_record, file_fields, "submission evidence file")
        path = _relative_path(record.get("path"), "submission evidence file path")
        try:
            path.relative_to(prefix)
        except ValueError as exc:
            raise MathFlowError(f"submission evidence file escapes contribution: {path}") from exc
        if previous_path is not None and path.as_posix() <= previous_path:
            raise MathFlowError("submission evidence files must be uniquely sorted")
        previous_path = path.as_posix()
        if path.as_posix() == f"{prefix.as_posix()}/README.md":
            saw_readme = True
        size = record.get("bytes")
        if isinstance(size, bool) or not isinstance(size, int) or size < 0:
            raise MathFlowError(f"submission evidence file has an invalid byte count: {path}")
        _require_digest(record.get("digest"), "submission evidence file digest")
        chunk_records = record.get("chunks")
        if not isinstance(chunk_records, list):
            raise MathFlowError(f"submission evidence file has invalid chunks: {path}")
        expected_offset = 0
        for expected_ordinal, chunk_record in enumerate(chunk_records):
            chunk = _require_exact_fields(
                chunk_record, {"ordinal", "offset", "bytes", "digest"}, "evidence chunk"
            )
            chunk_bytes_value = chunk.get("bytes")
            if (
                chunk.get("ordinal") != expected_ordinal
                or chunk.get("offset") != expected_offset
                or isinstance(chunk_bytes_value, bool)
                or not isinstance(chunk_bytes_value, int)
                or not 1 <= chunk_bytes_value <= chunk_size
            ):
                raise MathFlowError(f"submission evidence chunk coverage is invalid: {path}")
            if expected_ordinal < len(chunk_records) - 1 and chunk_bytes_value != chunk_size:
                raise MathFlowError(f"submission evidence contains a truncated interior chunk: {path}")
            _require_digest(chunk.get("digest"), "submission evidence chunk digest")
            expected_offset += chunk_bytes_value
        if expected_offset != size or (size == 0 and chunk_records) or (size > 0 and not chunk_records):
            raise MathFlowError(f"submission evidence chunk coverage is incomplete: {path}")
        observed_total += size
    if not saw_readme:
        raise MathFlowError("submission evidence manifest is missing README.md")
    if observed_total != total_bytes:
        raise MathFlowError("submission evidence manifest total byte count mismatch")
    expected_digest = _object_digest(_without_digest(manifest, "manifestDigest"))
    if manifest.get("manifestDigest") != expected_digest:
        raise MathFlowError("submission evidence manifest digest mismatch")
    return manifest


def reconstruct_submission_evidence(
    manifest_value: object, chunks: Mapping[str, bytes]
) -> dict[str, bytes]:
    manifest = validate_submission_evidence_manifest(manifest_value)
    if not isinstance(chunks, Mapping):
        raise MathFlowError("submission evidence chunk store must be a mapping")
    expected_digests = {
        str(chunk["digest"])
        for file_record in manifest["files"]
        for chunk in file_record["chunks"]
    }
    if set(chunks) != expected_digests:
        missing = expected_digests - set(chunks)
        extra = set(chunks) - expected_digests
        detail = sorted(missing or extra)[0]
        reason = "missing" if missing else "undeclared"
        raise MathFlowError(f"submission evidence chunk store has {reason} chunk: {detail}")

    verified_chunks: dict[str, bytes] = {}
    for digest in sorted(expected_digests):
        _require_digest(digest, "submission evidence chunk key")
        value = chunks[digest]
        if not isinstance(value, bytes):
            raise MathFlowError(f"submission evidence chunk is not exact bytes: {digest}")
        if sha256_bytes(value) != digest:
            raise MathFlowError(f"submission evidence chunk digest mismatch: {digest}")
        verified_chunks[digest] = value

    reconstructed: dict[str, bytes] = {}
    for file_record in manifest["files"]:
        content = b"".join(
            verified_chunks[str(chunk["digest"])] for chunk in file_record["chunks"]
        )
        path = str(file_record["path"])
        if len(content) != file_record["bytes"]:
            raise MathFlowError(f"submission evidence file byte count mismatch: {path}")
        if sha256_bytes(content) != file_record["digest"]:
            raise MathFlowError(f"submission evidence file digest mismatch: {path}")
        reconstructed[path] = content
    if sum(len(content) for content in reconstructed.values()) != manifest["totalBytes"]:
        raise MathFlowError("reconstructed submission evidence total byte count mismatch")
    if _framed_submission_digest(reconstructed.items()) != manifest["submissionDigest"]:
        raise MathFlowError("reconstructed submission evidence digest mismatch")
    readme = f"{manifest['contributionPath']}/README.md"
    if not reconstructed.get(readme, b"").strip():
        raise MathFlowError("reconstructed submission evidence has an empty README.md")
    return reconstructed


def _accepted_claim_refs(
    value: object, subject_transaction_id: str
) -> list[dict[str, str]]:
    if not isinstance(value, list) or not value:
        raise MathFlowError("accepted claim references must be a non-empty array")
    result: list[dict[str, str]] = []
    for item in value:
        ref = _require_exact_fields(
            item,
            {"transactionId", "claimKey", "judgmentId", "assessmentDigest"},
            "accepted claim reference",
        )
        if ref.get("transactionId") != subject_transaction_id:
            raise MathFlowError("accepted claim reference belongs to another submission")
        claim_key = _require_identifier(ref.get("claimKey"), "accepted claim key")
        result.append(
            {
                "transactionId": subject_transaction_id,
                "claimKey": claim_key,
                "judgmentId": _require_digest(ref.get("judgmentId"), "validity judgment ID"),
                "assessmentDigest": _require_digest(
                    ref.get("assessmentDigest"), "validity assessment digest"
                ),
            }
        )
    result.sort(key=lambda item: (item["claimKey"], item["judgmentId"], item["assessmentDigest"]))
    identities = [
        (item["transactionId"], item["claimKey"], item["judgmentId"], item["assessmentDigest"])
        for item in result
    ]
    if len(identities) != len(set(identities)):
        raise MathFlowError("accepted claim references contain duplicates")
    if len({item["claimKey"] for item in result}) != len(result):
        raise MathFlowError("accepted claim references repeat a claim identity")
    return result


def accepted_claim_refs_from_validity(
    judgment: object, *, subject_transaction_id: str
) -> list[dict[str, str]]:
    """Derive immutable identities for valid v4 claim assessments.

    Statements and assessment summaries are deliberately excluded. The digest
    binds the complete assessment in the already-published validity object.
    """

    subject = _require_transaction(subject_transaction_id, "subject transaction ID")
    if not isinstance(judgment, dict) or judgment.get("schemaVersion") != 4:
        raise MathFlowError("accepted claim identities require a validity-v4 judgment")
    judgment_id = _require_digest(judgment.get("judgmentId"), "validity judgment ID")
    subjects = judgment.get("subjects")
    if (
        not isinstance(subjects, list)
        or len(subjects) != 1
        or not isinstance(subjects[0], dict)
        or subjects[0].get("kind") != "transaction"
        or subjects[0].get("id") != subject
    ):
        raise MathFlowError("validity judgment belongs to another subject")
    assessments = judgment.get("assessments")
    if not isinstance(assessments, list):
        raise MathFlowError("validity judgment has invalid assessments")
    refs = []
    expected_assessment_fields = {
        "claimKey",
        "status",
        "premiseStatus",
        "summary",
        "scopeQualifications",
        "evidenceIssues",
        "evidenceTransactionIds",
        "requiredDependencyTransactionIds",
    }
    for assessment in assessments:
        if not isinstance(assessment, dict) or set(assessment) != expected_assessment_fields:
            raise MathFlowError("validity judgment contains an invalid assessment")
        if assessment.get("status") != "valid":
            continue
        premise_status = assessment.get("premiseStatus")
        required = assessment.get("requiredDependencyTransactionIds")
        evidence = assessment.get("evidenceTransactionIds")
        if (
            not isinstance(required, list)
            or not isinstance(evidence, list)
            or any(
                not isinstance(item, str) or not GIT_SHA.fullmatch(item)
                for item in [*required, *evidence]
            )
            or len(required) != len(set(required))
            or len(evidence) != len(set(evidence))
            or not set(required) <= set(evidence)
        ):
            raise MathFlowError("valid assessment has invalid dependency evidence")
        if premise_status not in {"satisfied", "not-required"} or (
            required and premise_status != "satisfied"
        ):
            raise MathFlowError("valid assessment has inconsistent premise status")
        refs.append(
            {
                "transactionId": subject,
                "claimKey": assessment.get("claimKey"),
                "judgmentId": judgment_id,
                "assessmentDigest": _object_digest(assessment),
            }
        )
    if not refs:
        raise MathFlowError("submission has no accepted claim identities")
    return _accepted_claim_refs(refs, subject)


def _node_ref(value: object, label: str) -> dict[str, str]:
    ref = _require_exact_fields(value, {"kind", "id"}, label)
    kind = ref.get("kind")
    if kind not in NODE_KINDS:
        raise MathFlowError(f"{label} kind must be program or thread")
    return {"kind": str(kind), "id": _require_identifier(ref.get("id"), f"{label} ID")}


def _node_ref_key(value: Mapping[str, str]) -> tuple[str, str]:
    return value["kind"], value["id"]


def _state_bindings(
    research_state: object, problem_id: str | None = None
) -> tuple[dict[str, object], set[tuple[str, str]]]:
    state = validate_research_program_state_versioned(
        research_state, problem=problem_id
    )
    refs = {("program", str(node_id)) for node_id in state["programs"]}
    refs.update(
        ("thread", str(node_id)) for node_id in state.get("threads", {})
    )
    return state, refs


def _assert_no_raw_evidence_copy(
    value: object, reconstructed_evidence: Mapping[str, bytes]
) -> None:
    """Reject verbatim evidence spans; semantic safety remains a judge boundary."""

    strings: list[str] = []

    def visit(item: object) -> None:
        if isinstance(item, str):
            strings.append(item)
        elif isinstance(item, list):
            for child in item:
                visit(child)
        elif isinstance(item, dict):
            for child in item.values():
                visit(child)

    visit(value)
    candidate_values = [text.encode("utf-8") for text in strings if text]
    candidate_windows: dict[int, set[bytes]] = {}
    mask = (1 << 64) - 1
    base = 257
    factor = pow(base, EVIDENCE_COPY_WINDOW - 1, 1 << 64)

    def window_hash(window: bytes) -> int:
        result = 0
        for byte in window:
            result = ((result * base) + byte) & mask
        return result

    for candidate in candidate_values:
        for offset in range(0, max(0, len(candidate) - EVIDENCE_COPY_WINDOW + 1)):
            window = candidate[offset : offset + EVIDENCE_COPY_WINDOW]
            candidate_windows.setdefault(window_hash(window), set()).add(window)

    for evidence in reconstructed_evidence.values():
        if len(evidence) >= EVIDENCE_COPY_WINDOW and candidate_windows:
            rolling = window_hash(evidence[:EVIDENCE_COPY_WINDOW])
            for offset in range(0, len(evidence) - EVIDENCE_COPY_WINDOW + 1):
                if offset:
                    outgoing = evidence[offset - 1]
                    incoming = evidence[offset + EVIDENCE_COPY_WINDOW - 1]
                    rolling = (
                        ((rolling - (outgoing * factor)) * base) + incoming
                    ) & mask
                possible = candidate_windows.get(rolling)
                if possible and evidence[offset : offset + EVIDENCE_COPY_WINDOW] in possible:
                    raise MathFlowError(
                        "counterfactual-safe facts copy a raw submission evidence span"
                    )
        elif len(evidence) >= MIN_SHORT_EVIDENCE_COPY and any(
            evidence in candidate for candidate in candidate_values
        ):
            raise MathFlowError(
                "counterfactual-safe facts copy a raw submission evidence artifact"
            )


def build_counterfactual_safe_facts(
    *,
    problem_id: str,
    subject_transaction_id: str,
    accepted_claim_refs: object,
    research_state: object,
    evidence_manifest: object,
    evidence_chunks: Mapping[str, bytes],
    extracted: object,
) -> dict[str, object]:
    """Validate model-extracted safe facts and wrap trusted identity bindings.

    This is the governed epistemic judgment boundary. Structural validation can
    exclude raw bytes, arbitrary fields, actor-visible facts, and references
    outside builder state; it cannot prove that a paraphrase is non-actionable.
    """

    problem = _require_problem(problem_id)
    subject = _require_transaction(subject_transaction_id, "subject transaction ID")
    state, allowed_refs = _state_bindings(research_state, problem)
    manifest = validate_submission_evidence_manifest(evidence_manifest)
    if manifest.get("problemId") != problem or manifest.get("subjectTransactionId") != subject:
        raise MathFlowError("safe-fact evidence belongs to another problem or subject")
    evidence = reconstruct_submission_evidence(manifest, evidence_chunks)
    claims = _accepted_claim_refs(accepted_claim_refs, subject)
    payload = _require_exact_fields(
        extracted, SAFE_FACT_ENVELOPE_FIELDS, "counterfactual-safe fact extraction"
    )
    raw_facts = payload.get("facts")
    if not isinstance(raw_facts, list) or not 1 <= len(raw_facts) <= MAX_SAFE_FACTS:
        raise MathFlowError("counterfactual-safe fact extraction must contain facts")
    claim_keys = {item["claimKey"] for item in claims}
    facts: list[dict[str, object]] = []
    seen_ids: set[str] = set()
    for raw_fact in raw_facts:
        fact = _require_exact_fields(raw_fact, SAFE_FACT_FIELDS, "counterfactual-safe fact")
        fact_id = _require_identifier(fact.get("id"), "counterfactual-safe fact ID")
        if fact_id in seen_ids:
            raise MathFlowError("counterfactual-safe fact IDs must be unique")
        seen_ids.add(fact_id)
        if fact.get("actorVisibility") != "withheld-until-independent-discovery":
            raise MathFlowError("counterfactual-safe fact must remain hidden from no-access actors")
        raw_refs = fact.get("affectedNodeRefs")
        if not isinstance(raw_refs, list) or not raw_refs:
            raise MathFlowError("counterfactual-safe fact must identify affected builder nodes")
        refs = [_node_ref(item, "counterfactual-safe affected node") for item in raw_refs]
        if any(_node_ref_key(ref) not in allowed_refs for ref in refs):
            raise MathFlowError("counterfactual-safe fact references a node outside builder state")
        refs.sort(key=_node_ref_key)
        if len({_node_ref_key(ref) for ref in refs}) != len(refs):
            raise MathFlowError("counterfactual-safe fact repeats an affected node")
        raw_keys = fact.get("acceptedClaimKeys")
        if (
            not isinstance(raw_keys, list)
            or not raw_keys
            or any(not isinstance(item, str) or item not in claim_keys for item in raw_keys)
            or len(raw_keys) != len(set(raw_keys))
        ):
            raise MathFlowError("counterfactual-safe fact has invalid accepted claim identities")
        facts.append(
            {
                "id": fact_id,
                "condition": _require_text(
                    fact.get("condition"), "counterfactual-safe condition", max_bytes=MAX_SAFE_TEXT_BYTES
                ),
                "actorVisibility": "withheld-until-independent-discovery",
                "affectedNodeRefs": refs,
                "acceptedClaimKeys": sorted(raw_keys),
            }
        )
    facts.sort(key=lambda item: str(item["id"]))

    raw_assumptions = payload.get("assumptions")
    if (
        not isinstance(raw_assumptions, list)
        or len(raw_assumptions) > MAX_SAFE_ASSUMPTIONS
        or any(not isinstance(item, str) for item in raw_assumptions)
    ):
        raise MathFlowError("counterfactual-safe assumptions must be text")
    assumptions = sorted(
        {
            _require_text(item, "counterfactual-safe assumption", max_bytes=MAX_SAFE_TEXT_BYTES)
            for item in raw_assumptions
        }
    )
    semantic_payload = {"facts": facts, "assumptions": assumptions}
    # Claim keys and builder node IDs are mandatory identity bindings and may
    # legitimately be printed in the manifested submission.  The epistemic
    # boundary applies to provider-authored prose, so scan only fact conditions
    # and assumptions for copied evidence spans.
    _assert_no_raw_evidence_copy(
        {
            "factConditions": [fact["condition"] for fact in facts],
            "assumptions": assumptions,
        },
        evidence,
    )
    core: dict[str, object] = {
        "schemaVersion": 1,
        "problemId": problem,
        "subjectTransactionId": subject,
        "acceptedClaimRefs": claims,
        "knowledgeStateDigest": state["stateDigest"],
        "subjectEvidenceManifestDigest": manifest["manifestDigest"],
        **semantic_payload,
    }
    safe_facts = {**core, "safeFactsDigest": _object_digest(core)}
    validate_counterfactual_safe_facts(safe_facts)
    return safe_facts


def validate_counterfactual_safe_facts(value: object) -> dict[str, object]:
    fields = {
        "schemaVersion",
        "problemId",
        "subjectTransactionId",
        "acceptedClaimRefs",
        "knowledgeStateDigest",
        "subjectEvidenceManifestDigest",
        "facts",
        "assumptions",
        "safeFactsDigest",
    }
    safe = _require_exact_fields(value, fields, "counterfactual-safe facts")
    if safe.get("schemaVersion") != 1:
        raise MathFlowError("counterfactual-safe facts have an unsupported version")
    _require_problem(safe.get("problemId"))
    subject = _require_transaction(safe.get("subjectTransactionId"), "safe-fact subject ID")
    claims = _accepted_claim_refs(safe.get("acceptedClaimRefs"), subject)
    if safe.get("acceptedClaimRefs") != claims:
        raise MathFlowError("counterfactual-safe accepted claim identities are not canonical")
    _require_digest(safe.get("knowledgeStateDigest"), "safe-fact knowledge-state digest")
    _require_digest(safe.get("subjectEvidenceManifestDigest"), "safe-fact evidence manifest digest")
    facts = safe.get("facts")
    if not isinstance(facts, list) or not 1 <= len(facts) <= MAX_SAFE_FACTS:
        raise MathFlowError("counterfactual-safe facts must contain facts")
    seen: set[str] = set()
    claim_keys = {item["claimKey"] for item in claims}
    previous: str | None = None
    for raw_fact in facts:
        fact = _require_exact_fields(raw_fact, SAFE_FACT_FIELDS, "counterfactual-safe fact")
        fact_id = _require_identifier(fact.get("id"), "counterfactual-safe fact ID")
        if fact_id in seen or (previous is not None and fact_id <= previous):
            raise MathFlowError("counterfactual-safe facts must be uniquely sorted")
        seen.add(fact_id)
        previous = fact_id
        _require_text(fact.get("condition"), "counterfactual-safe condition", max_bytes=MAX_SAFE_TEXT_BYTES)
        if fact.get("actorVisibility") != "withheld-until-independent-discovery":
            raise MathFlowError("counterfactual-safe fact violates actor visibility")
        refs = fact.get("affectedNodeRefs")
        if not isinstance(refs, list) or not refs:
            raise MathFlowError("counterfactual-safe fact must reference builder nodes")
        parsed_refs = [_node_ref(ref, "counterfactual-safe affected node") for ref in refs]
        if parsed_refs != sorted(parsed_refs, key=_node_ref_key) or len(
            {_node_ref_key(ref) for ref in parsed_refs}
        ) != len(parsed_refs):
            raise MathFlowError("counterfactual-safe affected nodes are not canonical")
        keys = fact.get("acceptedClaimKeys")
        if (
            not isinstance(keys, list)
            or not keys
            or keys != sorted(keys)
            or len(keys) != len(set(keys))
            or any(key not in claim_keys for key in keys)
        ):
            raise MathFlowError("counterfactual-safe claim keys are not canonical")
    assumptions = safe.get("assumptions")
    if (
        not isinstance(assumptions, list)
        or len(assumptions) > MAX_SAFE_ASSUMPTIONS
        or assumptions != sorted(set(assumptions))
        or any(not isinstance(item, str) for item in assumptions)
    ):
        raise MathFlowError("counterfactual-safe assumptions are not canonical")
    for item in assumptions:
        _require_text(item, "counterfactual-safe assumption", max_bytes=MAX_SAFE_TEXT_BYTES)
    if safe.get("safeFactsDigest") != _object_digest(_without_digest(safe, "safeFactsDigest")):
        raise MathFlowError("counterfactual-safe facts digest mismatch")
    return safe


def build_impact_subgraph_context(
    *,
    problem_id: str,
    subject_transaction_id: str,
    accepted_claim_refs: object,
    research_state: object,
    seed_node_refs: object,
    descendant_depth: int = 1,
) -> dict[str, object]:
    """Construct a deterministic local topology packet with collapsed boundaries."""

    problem = _require_problem(problem_id)
    subject = _require_transaction(subject_transaction_id, "subject transaction ID")
    state, allowed_refs = _state_bindings(research_state, problem)
    claims = _accepted_claim_refs(accepted_claim_refs, subject)
    if isinstance(descendant_depth, bool) or not isinstance(descendant_depth, int) or not 0 <= descendant_depth <= 4:
        raise MathFlowError("impact context descendant depth must be between zero and four")
    if not isinstance(seed_node_refs, list) or not seed_node_refs:
        raise MathFlowError("impact context requires seed builder nodes")
    seeds = [_node_ref(item, "impact context seed") for item in seed_node_refs]
    if any(_node_ref_key(seed) not in allowed_refs for seed in seeds):
        raise MathFlowError("impact context seed escapes the exact builder topology")
    seeds.sort(key=_node_ref_key)
    if len({_node_ref_key(seed) for seed in seeds}) != len(seeds):
        raise MathFlowError("impact context repeats a seed builder node")

    programs: dict[str, dict[str, object]] = state["programs"]
    threads: dict[str, dict[str, object]] = state["threads"]
    items: dict[str, dict[str, object]] = state["items"]
    program_children: dict[str, list[str]] = {str(node_id): [] for node_id in programs}
    for program_id, program in programs.items():
        parent = program.get("parentId")
        if isinstance(parent, str):
            program_children[parent].append(str(program_id))
    threads_by_program: dict[str, list[str]] = {str(node_id): [] for node_id in programs}
    for thread_id, thread in threads.items():
        threads_by_program[str(thread["programId"])].append(str(thread_id))
    for values in (program_children, threads_by_program):
        for node_ids in values.values():
            node_ids.sort()

    included_programs: set[str] = set()
    included_threads: set[str] = set()
    roles: dict[tuple[str, str], set[str]] = {}

    def add(kind: str, node_id: str, role: str) -> None:
        (included_programs if kind == "program" else included_threads).add(node_id)
        roles.setdefault((kind, node_id), set()).add(role)

    seed_programs: set[str] = set()
    for seed in seeds:
        add(seed["kind"], seed["id"], "seed")
        program_id = seed["id"] if seed["kind"] == "program" else str(threads[seed["id"]]["programId"])
        seed_programs.add(program_id)
        add("program", program_id, "seed-owner" if seed["kind"] == "thread" else "seed")

    for program_id in sorted(seed_programs):
        cursor: str | None = program_id
        while cursor is not None:
            add("program", cursor, "ancestor" if cursor != program_id else "seed")
            parent = programs[cursor].get("parentId")
            cursor = str(parent) if isinstance(parent, str) else None
        parent = programs[program_id].get("parentId")
        if isinstance(parent, str):
            for sibling in program_children[parent]:
                add("program", sibling, "sibling-decision-point")

        frontier = [(program_id, 0)]
        while frontier:
            current, depth = frontier.pop(0)
            if depth >= descendant_depth:
                continue
            for child in program_children[current]:
                add("program", child, "descendant")
                frontier.append((child, depth + 1))

    for program_id in sorted(included_programs):
        for thread_id in threads_by_program[program_id]:
            add("thread", thread_id, "local-thread")

    included_nodes: list[dict[str, object]] = []
    for program_id in sorted(included_programs):
        program = programs[program_id]
        parent = program.get("parentId")
        included_nodes.append(
            {
                "ref": {"kind": "program", "id": program_id},
                "parentRef": {"kind": "program", "id": parent} if isinstance(parent, str) else None,
                "status": program["status"],
                "roles": sorted(roles.get(("program", program_id), set())),
                "recordDigest": program["digest"],
            }
        )
    for thread_id in sorted(included_threads):
        thread = threads[thread_id]
        included_nodes.append(
            {
                "ref": {"kind": "thread", "id": thread_id},
                "parentRef": {"kind": "program", "id": thread["programId"]},
                "status": thread["status"],
                "roles": sorted(roles.get(("thread", thread_id), set())),
                "recordDigest": thread["digest"],
            }
        )
    included_nodes.sort(key=lambda item: _node_ref_key(item["ref"]))

    boundary_summaries: list[dict[str, object]] = []
    for parent_id in sorted(included_programs):
        for child_id in program_children[parent_id]:
            if child_id in included_programs:
                continue
            descendant_programs: set[str] = set()
            queue = [child_id]
            while queue:
                current = queue.pop(0)
                if current in descendant_programs:
                    continue
                descendant_programs.add(current)
                queue.extend(program_children[current])
            boundary_summaries.append(
                {
                    "nodeRef": {"kind": "program", "id": child_id},
                    "parentRef": {"kind": "program", "id": parent_id},
                    "relationship": "collapsed-descendant-subtree",
                    "programCount": len(descendant_programs),
                    "threadCount": sum(len(threads_by_program[node]) for node in descendant_programs),
                    "itemCount": sum(
                        1 for item in items.values() if item.get("programId") in descendant_programs
                    ),
                    "recordDigest": programs[child_id]["digest"],
                }
            )
    boundary_summaries.sort(key=lambda item: _node_ref_key(item["nodeRef"]))

    semantic_item_refs: list[dict[str, object]] = []
    for item_id, item in sorted(items.items()):
        if item.get("programId") not in included_programs:
            continue
        semantic_item_refs.append(
            {
                "itemId": item_id,
                "programRef": {"kind": "program", "id": item["programId"]},
                "itemType": item["type"],
                "claimRefs": copy.deepcopy(item["claimRefs"]),
                "dependencyItemIds": sorted(item["dependencyItemIds"]),
                "recordDigest": item["digest"],
            }
        )

    core: dict[str, object] = {
        "schemaVersion": 1,
        "problemId": problem,
        "subjectTransactionId": subject,
        "acceptedClaimRefs": claims,
        "knowledgeStateDigest": state["stateDigest"],
        "seedNodeRefs": seeds,
        "descendantDepth": descendant_depth,
        "includedNodes": included_nodes,
        "boundarySummaries": boundary_summaries,
        "semanticItemRefs": semantic_item_refs,
        "expansionPolicy": {
            "allowedKinds": ["program", "thread"],
            "maximumDescendantDepth": 4,
            "requiresExactBuilderNode": True,
        },
    }
    context = {**core, "contextDigest": _object_digest(core)}
    validate_impact_subgraph_context(context)
    return context


def validate_impact_subgraph_context(value: object) -> dict[str, object]:
    fields = {
        "schemaVersion",
        "problemId",
        "subjectTransactionId",
        "acceptedClaimRefs",
        "knowledgeStateDigest",
        "seedNodeRefs",
        "descendantDepth",
        "includedNodes",
        "boundarySummaries",
        "semanticItemRefs",
        "expansionPolicy",
        "contextDigest",
    }
    context = _require_exact_fields(value, fields, "impact-subgraph context")
    if context.get("schemaVersion") != 1:
        raise MathFlowError("impact-subgraph context has an unsupported version")
    _require_problem(context.get("problemId"))
    subject = _require_transaction(context.get("subjectTransactionId"), "impact context subject ID")
    claims = _accepted_claim_refs(context.get("acceptedClaimRefs"), subject)
    if context.get("acceptedClaimRefs") != claims:
        raise MathFlowError("impact context accepted claim identities are not canonical")
    _require_digest(context.get("knowledgeStateDigest"), "impact context knowledge-state digest")
    depth = context.get("descendantDepth")
    if isinstance(depth, bool) or not isinstance(depth, int) or not 0 <= depth <= 4:
        raise MathFlowError("impact context has an invalid descendant depth")
    seeds = context.get("seedNodeRefs")
    if not isinstance(seeds, list) or not seeds:
        raise MathFlowError("impact context must contain seed nodes")
    parsed_seeds = [_node_ref(item, "impact context seed") for item in seeds]
    if parsed_seeds != sorted(parsed_seeds, key=_node_ref_key) or len(
        {_node_ref_key(item) for item in parsed_seeds}
    ) != len(parsed_seeds):
        raise MathFlowError("impact context seeds are not canonical")
    included = context.get("includedNodes")
    if not isinstance(included, list) or not included:
        raise MathFlowError("impact context must contain builder nodes")
    included_keys: set[tuple[str, str]] = set()
    previous_key: tuple[str, str] | None = None
    for raw_node in included:
        node = _require_exact_fields(
            raw_node, {"ref", "parentRef", "status", "roles", "recordDigest"}, "impact context node"
        )
        ref = _node_ref(node.get("ref"), "impact context node reference")
        key = _node_ref_key(ref)
        if key in included_keys or (previous_key is not None and key <= previous_key):
            raise MathFlowError("impact context nodes are not uniquely sorted")
        included_keys.add(key)
        previous_key = key
        parent = node.get("parentRef")
        if parent is not None and _node_ref(parent, "impact context parent")["kind"] != "program":
            raise MathFlowError("impact context parent must be a program")
        _require_text(node.get("status"), "impact context node status")
        roles = node.get("roles")
        if not isinstance(roles, list) or roles != sorted(set(roles)) or any(
            not isinstance(role, str) or not role for role in roles
        ):
            raise MathFlowError("impact context node roles are not canonical")
        _require_digest(node.get("recordDigest"), "impact context node record digest")
    if any(_node_ref_key(seed) not in included_keys for seed in parsed_seeds):
        raise MathFlowError("impact context omits a seed node")
    boundaries = context.get("boundarySummaries")
    if not isinstance(boundaries, list):
        raise MathFlowError("impact context boundaries must be an array")
    boundary_keys: list[tuple[str, str]] = []
    for raw_boundary in boundaries:
        boundary = _require_exact_fields(
            raw_boundary,
            {"nodeRef", "parentRef", "relationship", "programCount", "threadCount", "itemCount", "recordDigest"},
            "impact context boundary",
        )
        ref = _node_ref(boundary.get("nodeRef"), "impact context boundary node")
        if ref["kind"] != "program" or _node_ref_key(ref) in included_keys:
            raise MathFlowError("impact context boundary must be an excluded program")
        parent = _node_ref(boundary.get("parentRef"), "impact context boundary parent")
        if parent["kind"] != "program" or _node_ref_key(parent) not in included_keys:
            raise MathFlowError("impact context boundary parent is outside included context")
        if boundary.get("relationship") != "collapsed-descendant-subtree":
            raise MathFlowError("impact context boundary has an invalid relationship")
        for field in ("programCount", "threadCount", "itemCount"):
            number = boundary.get(field)
            if isinstance(number, bool) or not isinstance(number, int) or number < (1 if field == "programCount" else 0):
                raise MathFlowError("impact context boundary has an invalid count")
        _require_digest(boundary.get("recordDigest"), "impact context boundary record digest")
        boundary_keys.append(_node_ref_key(ref))
    if boundary_keys != sorted(set(boundary_keys)):
        raise MathFlowError("impact context boundaries are not uniquely sorted")
    semantic = context.get("semanticItemRefs")
    if not isinstance(semantic, list):
        raise MathFlowError("impact context semantic item refs must be an array")
    previous_item: str | None = None
    for raw_item in semantic:
        item = _require_exact_fields(
            raw_item,
            {"itemId", "programRef", "itemType", "claimRefs", "dependencyItemIds", "recordDigest"},
            "impact context semantic item",
        )
        item_id = _require_identifier(item.get("itemId"), "impact context semantic item ID")
        if previous_item is not None and item_id <= previous_item:
            raise MathFlowError("impact context semantic items are not uniquely sorted")
        previous_item = item_id
        program_ref = _node_ref(item.get("programRef"), "semantic item program")
        if program_ref["kind"] != "program" or _node_ref_key(program_ref) not in included_keys:
            raise MathFlowError("semantic item program is outside included context")
        if item.get("itemType") not in {
            "result",
            "proof",
            "method",
            "computation",
            "tool",
            "question",
        }:
            raise MathFlowError("semantic item has an invalid item type")
        if not isinstance(item.get("claimRefs"), list) or not isinstance(item.get("dependencyItemIds"), list):
            raise MathFlowError("semantic item evidence references are invalid")
        seen_claims: set[tuple[str, str]] = set()
        for claim_ref in item["claimRefs"]:
            ref = _require_exact_fields(
                claim_ref, {"transactionId", "claimKey"}, "semantic item claim reference"
            )
            identity = (
                _require_transaction(ref.get("transactionId"), "semantic item claim transaction"),
                _require_identifier(ref.get("claimKey"), "semantic item claim key"),
            )
            if identity in seen_claims:
                raise MathFlowError("semantic item repeats a claim reference")
            seen_claims.add(identity)
        dependencies = item["dependencyItemIds"]
        if dependencies != sorted(set(dependencies)):
            raise MathFlowError("semantic item dependencies are not canonical")
        for dependency in item["dependencyItemIds"]:
            _require_identifier(dependency, "semantic item dependency ID")
        _require_digest(item.get("recordDigest"), "semantic item record digest")
    if context.get("expansionPolicy") != {
        "allowedKinds": ["program", "thread"],
        "maximumDescendantDepth": 4,
        "requiresExactBuilderNode": True,
    }:
        raise MathFlowError("impact context expansion policy is not the V1 firewall policy")
    if context.get("contextDigest") != _object_digest(_without_digest(context, "contextDigest")):
        raise MathFlowError("impact context digest mismatch")
    return context


def _validate_bound_pair(
    safe_facts_value: object, context_value: object
) -> tuple[dict[str, object], dict[str, object]]:
    safe = validate_counterfactual_safe_facts(safe_facts_value)
    context = validate_impact_subgraph_context(context_value)
    fields = ("problemId", "subjectTransactionId", "acceptedClaimRefs", "knowledgeStateDigest")
    if any(safe[field] != context[field] for field in fields):
        raise MathFlowError("safe facts and impact context have different identity bindings")
    allowed = {_node_ref_key(node["ref"]) for node in context["includedNodes"]}
    allowed.update(_node_ref_key(boundary["nodeRef"]) for boundary in context["boundarySummaries"])
    for fact in safe["facts"]:
        for ref in fact["affectedNodeRefs"]:
            if _node_ref_key(ref) not in allowed:
                raise MathFlowError("safe fact affected node escapes the supplied impact context")
    return safe, context


def _validate_context_against_builder_state(
    context: dict[str, object], research_state: object
) -> None:
    state, _ = _state_bindings(research_state, str(context["problemId"]))
    if state["stateDigest"] != context["knowledgeStateDigest"]:
        raise MathFlowError("impact context is bound to another builder state")
    rebuilt = build_impact_subgraph_context(
        problem_id=str(context["problemId"]),
        subject_transaction_id=str(context["subjectTransactionId"]),
        accepted_claim_refs=context["acceptedClaimRefs"],
        research_state=state,
        seed_node_refs=context["seedNodeRefs"],
        descendant_depth=int(context["descendantDepth"]),
    )
    if rebuilt != context:
        raise MathFlowError("impact context escapes the exact builder topology")


def build_no_access_stage_input(
    *, safe_facts: object, impact_context: object, research_state: object
) -> dict[str, object]:
    safe, context = _validate_bound_pair(safe_facts, impact_context)
    _validate_context_against_builder_state(context, research_state)
    core: dict[str, object] = {
        "schemaVersion": 1,
        "evaluationMode": "no-access",
        "problemId": safe["problemId"],
        "subjectTransactionId": safe["subjectTransactionId"],
        "acceptedClaimRefs": copy.deepcopy(safe["acceptedClaimRefs"]),
        "knowledgeStateDigest": safe["knowledgeStateDigest"],
        "safeFacts": copy.deepcopy(safe),
        "impactContext": copy.deepcopy(context),
        "visibilityPolicy": {
            "contributionAvailableToEvaluator": False,
            "contributionAvailableToActors": False,
            "actorsMayUseOnlyPreexistingPolicyUntilIndependentDiscovery": True,
        },
    }
    result = {**core, "inputDigest": _object_digest(core)}
    validate_no_access_stage_input(result)
    return result


def validate_no_access_stage_input(value: object) -> dict[str, object]:
    fields = {
        "schemaVersion",
        "evaluationMode",
        "problemId",
        "subjectTransactionId",
        "acceptedClaimRefs",
        "knowledgeStateDigest",
        "safeFacts",
        "impactContext",
        "visibilityPolicy",
        "inputDigest",
    }
    stage = _require_exact_fields(value, fields, "no-access stage input")
    if stage.get("schemaVersion") != 1 or stage.get("evaluationMode") != "no-access":
        raise MathFlowError("no-access stage input has an invalid version or mode")
    safe, context = _validate_bound_pair(stage.get("safeFacts"), stage.get("impactContext"))
    for field in ("problemId", "subjectTransactionId", "acceptedClaimRefs", "knowledgeStateDigest"):
        if stage.get(field) != safe[field] or stage.get(field) != context[field]:
            raise MathFlowError("no-access stage identity binding mismatch")
    if stage.get("visibilityPolicy") != {
        "contributionAvailableToEvaluator": False,
        "contributionAvailableToActors": False,
        "actorsMayUseOnlyPreexistingPolicyUntilIndependentDiscovery": True,
    }:
        raise MathFlowError("no-access stage has an invalid epistemic firewall policy")
    if stage.get("inputDigest") != _object_digest(_without_digest(stage, "inputDigest")):
        raise MathFlowError("no-access stage input digest mismatch")
    return stage


def build_no_access_stage_input_v2(
    *,
    safe_facts: object,
    impact_context: object,
    research_state: object,
    frozen_with_access_state: object,
    frozen_with_access_candidate_digest: str,
) -> dict[str, object]:
    """Bind the immutable live ``W+`` candidate into the no-access estimate.

    V2 deliberately exposes the reducer-authored numeric consequences of the
    submission to the evaluator while continuing to withhold the submission
    itself from both the request and the simulated actors.
    """

    safe, context = _validate_bound_pair(safe_facts, impact_context)
    _validate_context_against_builder_state(context, research_state)
    if not isinstance(frozen_with_access_state, dict):
        raise MathFlowError("no-access V2 input requires a frozen with-access state")
    state = copy.deepcopy(frozen_with_access_state)
    state_digest = _require_digest(
        state.get("stateDigest"), "frozen with-access state digest"
    )
    candidate_digest = _require_digest(
        frozen_with_access_candidate_digest,
        "frozen with-access candidate digest",
    )
    if (
        state.get("problemId") != safe["problemId"]
        or state.get("knowledgeStateDigest") != safe["knowledgeStateDigest"]
        or state.get("evaluationMode") != "with-access"
        or state.get("subjectTransactionId") != safe["subjectTransactionId"]
    ):
        raise MathFlowError("frozen with-access state has different identity bindings")
    processed = state.get("processedSubmissionIds")
    if not isinstance(processed, list) or not processed or processed[-1] != safe[
        "subjectTransactionId"
    ]:
        raise MathFlowError("frozen with-access state does not commit its subject")
    core: dict[str, object] = {
        "schemaVersion": 2,
        "evaluationMode": "no-access",
        "problemId": safe["problemId"],
        "subjectTransactionId": safe["subjectTransactionId"],
        "acceptedClaimRefs": copy.deepcopy(safe["acceptedClaimRefs"]),
        "knowledgeStateDigest": safe["knowledgeStateDigest"],
        "safeFacts": copy.deepcopy(safe),
        "impactContext": copy.deepcopy(context),
        "frozenWithAccessCandidateDigest": candidate_digest,
        "frozenWithAccessStateDigest": state_digest,
        "frozenWithAccessState": state,
        "visibilityPolicy": {
            "rawContributionAvailableToEvaluator": False,
            "frozenWithAccessStateAvailableToEvaluator": True,
            "contributionAvailableToActors": False,
            "actorsMayUseOnlyPreexistingPolicyUntilIndependentDiscovery": True,
        },
    }
    result = {**core, "inputDigest": _object_digest(core)}
    validate_no_access_stage_input_v2(result)
    return result


def validate_no_access_stage_input_v2(value: object) -> dict[str, object]:
    fields = {
        "schemaVersion",
        "evaluationMode",
        "problemId",
        "subjectTransactionId",
        "acceptedClaimRefs",
        "knowledgeStateDigest",
        "safeFacts",
        "impactContext",
        "frozenWithAccessCandidateDigest",
        "frozenWithAccessStateDigest",
        "frozenWithAccessState",
        "visibilityPolicy",
        "inputDigest",
    }
    stage = _require_exact_fields(value, fields, "no-access V2 stage input")
    if stage.get("schemaVersion") != 2 or stage.get("evaluationMode") != "no-access":
        raise MathFlowError("no-access V2 stage input has an invalid version or mode")
    safe, context = _validate_bound_pair(stage.get("safeFacts"), stage.get("impactContext"))
    for field in ("problemId", "subjectTransactionId", "acceptedClaimRefs", "knowledgeStateDigest"):
        if stage.get(field) != safe[field] or stage.get(field) != context[field]:
            raise MathFlowError("no-access V2 stage identity binding mismatch")
    frozen = stage.get("frozenWithAccessState")
    if not isinstance(frozen, dict):
        raise MathFlowError("no-access V2 stage is missing its frozen with-access state")
    frozen_digest = _require_digest(
        stage.get("frozenWithAccessStateDigest"),
        "no-access V2 frozen with-access state digest",
    )
    _require_digest(
        stage.get("frozenWithAccessCandidateDigest"),
        "no-access V2 frozen with-access candidate digest",
    )
    if (
        frozen.get("stateDigest") != frozen_digest
        or frozen.get("problemId") != stage["problemId"]
        or frozen.get("knowledgeStateDigest") != stage["knowledgeStateDigest"]
        or frozen.get("evaluationMode") != "with-access"
        or frozen.get("subjectTransactionId") != stage["subjectTransactionId"]
    ):
        raise MathFlowError("no-access V2 frozen with-access binding mismatch")
    processed = frozen.get("processedSubmissionIds")
    if not isinstance(processed, list) or not processed or processed[-1] != stage[
        "subjectTransactionId"
    ]:
        raise MathFlowError("no-access V2 frozen state does not commit its subject")
    if stage.get("visibilityPolicy") != {
        "rawContributionAvailableToEvaluator": False,
        "frozenWithAccessStateAvailableToEvaluator": True,
        "contributionAvailableToActors": False,
        "actorsMayUseOnlyPreexistingPolicyUntilIndependentDiscovery": True,
    }:
        raise MathFlowError("no-access V2 stage has an invalid epistemic policy")
    if stage.get("inputDigest") != _object_digest(_without_digest(stage, "inputDigest")):
        raise MathFlowError("no-access V2 stage input digest mismatch")
    return stage


def build_with_access_stage_input(
    *,
    safe_facts: object,
    impact_context: object,
    research_state: object,
    evidence_manifest: object,
    evidence_chunks: Mapping[str, bytes],
) -> dict[str, object]:
    safe, context = _validate_bound_pair(safe_facts, impact_context)
    _validate_context_against_builder_state(context, research_state)
    manifest = validate_submission_evidence_manifest(evidence_manifest)
    reconstructed = reconstruct_submission_evidence(manifest, evidence_chunks)
    if (
        manifest["problemId"] != safe["problemId"]
        or manifest["subjectTransactionId"] != safe["subjectTransactionId"]
        or manifest["manifestDigest"] != safe["subjectEvidenceManifestDigest"]
    ):
        raise MathFlowError("with-access evidence has different identity bindings")
    verified_chunk_digests = sorted(evidence_chunks)
    core: dict[str, object] = {
        "schemaVersion": 1,
        "evaluationMode": "with-access",
        "problemId": safe["problemId"],
        "subjectTransactionId": safe["subjectTransactionId"],
        "acceptedClaimRefs": copy.deepcopy(safe["acceptedClaimRefs"]),
        "knowledgeStateDigest": safe["knowledgeStateDigest"],
        "safeFactsDigest": safe["safeFactsDigest"],
        "safeFactsEvidenceManifestDigest": safe["subjectEvidenceManifestDigest"],
        "impactContext": copy.deepcopy(context),
        "evidenceManifest": copy.deepcopy(manifest),
        "verifiedChunkDigests": verified_chunk_digests,
        "verifiedFileCount": len(reconstructed),
        "verifiedTotalBytes": sum(len(content) for content in reconstructed.values()),
        "visibilityPolicy": {
            "contributionAvailableToEvaluator": True,
            "contributionAvailableToActors": True,
        },
    }
    result = {**core, "inputDigest": _object_digest(core)}
    validate_with_access_stage_input(result)
    return result


def validate_with_access_stage_input(value: object) -> dict[str, object]:
    fields = {
        "schemaVersion",
        "evaluationMode",
        "problemId",
        "subjectTransactionId",
        "acceptedClaimRefs",
        "knowledgeStateDigest",
        "safeFactsDigest",
        "safeFactsEvidenceManifestDigest",
        "impactContext",
        "evidenceManifest",
        "verifiedChunkDigests",
        "verifiedFileCount",
        "verifiedTotalBytes",
        "visibilityPolicy",
        "inputDigest",
    }
    stage = _require_exact_fields(value, fields, "with-access stage input")
    if stage.get("schemaVersion") != 1 or stage.get("evaluationMode") != "with-access":
        raise MathFlowError("with-access stage input has an invalid version or mode")
    context = validate_impact_subgraph_context(stage.get("impactContext"))
    manifest = validate_submission_evidence_manifest(stage.get("evidenceManifest"))
    for field in ("problemId", "subjectTransactionId", "acceptedClaimRefs", "knowledgeStateDigest"):
        if stage.get(field) != context[field]:
            raise MathFlowError("with-access stage identity binding mismatch")
    if stage.get("problemId") != manifest["problemId"] or stage.get("subjectTransactionId") != manifest["subjectTransactionId"]:
        raise MathFlowError("with-access stage evidence identity mismatch")
    _require_digest(stage.get("safeFactsDigest"), "with-access safe-facts digest")
    if stage.get("safeFactsEvidenceManifestDigest") != manifest["manifestDigest"]:
        raise MathFlowError("with-access safe-fact and evidence manifest bindings differ")
    expected_chunks = sorted(
        {
            str(chunk["digest"])
            for file_record in manifest["files"]
            for chunk in file_record["chunks"]
        }
    )
    if stage.get("verifiedChunkDigests") != expected_chunks:
        raise MathFlowError("with-access stage chunk binding is incomplete")
    if stage.get("verifiedFileCount") != len(manifest["files"]) or stage.get("verifiedTotalBytes") != manifest["totalBytes"]:
        raise MathFlowError("with-access stage evidence counts are inconsistent")
    if stage.get("visibilityPolicy") != {
        "contributionAvailableToEvaluator": True,
        "contributionAvailableToActors": True,
    }:
        raise MathFlowError("with-access stage has an invalid visibility policy")
    if stage.get("inputDigest") != _object_digest(_without_digest(stage, "inputDigest")):
        raise MathFlowError("with-access stage input digest mismatch")
    return stage


def assemble_with_access_evidence(
    stage_input: object, chunks: Mapping[str, bytes]
) -> list[dict[str, object]]:
    """Verify a with-access binding and reconstruct all exact submission files."""

    stage = validate_with_access_stage_input(stage_input)
    files = reconstruct_submission_evidence(stage["evidenceManifest"], chunks)
    if sorted(chunks) != stage["verifiedChunkDigests"]:
        raise MathFlowError("with-access chunk store does not match the bound stage input")
    return [
        {
            "path": path,
            "bytes": len(content),
            "digest": sha256_bytes(content),
            "content": content,
        }
        for path, content in sorted(files.items())
    ]
