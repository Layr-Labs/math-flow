"""Inactive end-to-end orchestration and CAS persistence for work accounting V1."""

from __future__ import annotations

import copy
import fcntl
import json
import os
import re
import tempfile
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import Callable, Mapping, Protocol, Sequence

from .artifacts import sha256_bytes
from .counterfactual_context import (
    reconstruct_submission_evidence,
    validate_submission_evidence_manifest,
)
from .errors import MathFlowError
from .repository import canonical_json, ledger, sha256_json
from .research_builder_v6 import (
    apply_research_builder_v6_transition,
    validate_research_builder_v6_handoff,
)
from .research_topology import (
    validate_research_program_state_v2,
    validate_research_topology_alignment,
)
from .work_accounting import (
    validate_root_contract,
    validate_work_accounting_state,
)
from .work_accounting_schedule import (
    apply_work_accounting_publication,
    discover_work_accounting_subjects,
    initialize_work_accounting_schedule,
    materialize_work_accounting_publication_manifest,
    plan_next_work_accounting_transition,
    record_work_accounting_failure,
    validate_work_accounting_publication_manifest,
    validate_work_accounting_schedule,
    validate_work_accounting_transition_claim,
)
from .work_projection import (
    PROFILE as WORK_PROJECTION_PROFILE_V1,
    PROFILE_V2 as WORK_PROJECTION_PROFILE_V2,
    WorkProjectionProvider,
    load_work_projection_bundle,
    prepare_frozen_with_access_candidate_v2,
    run_work_projection_bundle,
)


DIGEST = re.compile(r"^sha256:[0-9a-f]{64}$")
GIT_SHA = re.compile(r"^[0-9a-f]{40}$")
IDENTIFIER = re.compile(r"^[a-z0-9][a-z0-9/_-]*$")
SAFE_KEY_PART = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")

PIPELINE_FIELDS = {
    "schemaVersion",
    "problemId",
    "projectionId",
    "projectionSpecDigest",
    "rootContractDigest",
    "phase",
    "formedKnowledgeStateDigest",
    "accountingStateDigest",
    "scheduleDigest",
    "completedTransitions",
    "pendingTransition",
    "pipelineStateDigest",
}
PENDING_FIELDS = {
    "stage",
    "subjectTransactionId",
    "ledgerOrdinal",
    "submissionInputDigest",
    "builderResultDigest",
    "builderHandoffDigest",
    "topologyAlignmentDigest",
    "beforeKnowledgeStateDigest",
    "afterKnowledgeStateDigest",
    "claimDigest",
    "workBundleDigest",
    "publicationManifestDigest",
    "nextAccountingStateDigest",
    "nextScheduleDigest",
}
COMPLETED_FIELDS = {
    "subjectTransactionId",
    "ledgerOrdinal",
    "submissionInputDigest",
    "builderResultDigest",
    "builderHandoffDigest",
    "topologyAlignmentDigest",
    "workBundleDigest",
    "publicationManifestDigest",
    "accountingStateDigest",
}
SUBMISSION_FIELDS = {
    "schemaVersion",
    "problemId",
    "transactionId",
    "ordinal",
    "acceptedClaims",
    "judgmentId",
    "acceptedClaimRefs",
    "evidenceManifest",
    "evidenceChunkDigests",
    "submissionInputDigest",
}
BUILDER_RESULT_FIELDS = {
    "schemaVersion",
    "problemId",
    "subjectTransactionId",
    "ledgerOrdinal",
    "submissionInputDigest",
    "builderRequestDigest",
    "builderProposalDigest",
    "beforeKnowledgeStateDigest",
    "afterKnowledgeStateDigest",
    "topologyAlignmentDigest",
    "builderHandoffDigest",
    "builderResultDigest",
}
WORK_INDEX_FIELDS = {
    "schemaVersion",
    "automaticRetryKey",
    "subjectTransactionId",
    "predecessorAccountingStateDigest",
    "beforeKnowledgeStateDigest",
    "afterKnowledgeStateDigest",
    "workBundleDigest",
    "evaluationDigest",
    "workResultIndexDigest",
}


class CASConflict(MathFlowError):
    """The mutable lane head changed from the caller's expected version."""


class ImmutableConflict(MathFlowError):
    """An immutable key already contains different bytes."""


class WorkProviderFailure(MathFlowError):
    """An injected work provider failed before producing valid stage output."""


@dataclass(frozen=True)
class StoredValue:
    value: bytes
    version: str


class CASObjectStore(Protocol):
    """Filesystem/object-store-neutral byte and compare-and-swap boundary."""

    def get(self, key: str) -> StoredValue | None: ...

    def put_immutable(self, key: str, value: bytes) -> str: ...

    def compare_and_swap(
        self, key: str, expected_version: str | None, value: bytes
    ) -> str: ...


class BuilderTransitionProvider(Protocol):
    """Provider-neutral source of one v6 builder transition proposal."""

    def __call__(
        self,
        *,
        base_knowledge_state: Mapping[str, object],
        submission: Mapping[str, object],
    ) -> object: ...


@dataclass(frozen=True)
class AcceptedWorkSubmission:
    transaction_id: str
    ordinal: int
    accepted_claims: Sequence[Mapping[str, object]]
    judgment_id: str
    accepted_claim_refs: Sequence[Mapping[str, object]]
    evidence_manifest: Mapping[str, object]
    evidence_chunks: Mapping[str, bytes]


CrashHook = Callable[[str], None]


class LocalCASObjectStore:
    """Safe local implementation of immutable puts and atomic CAS references."""

    def __init__(self, root: Path):
        if root.exists() and root.is_symlink():
            raise MathFlowError("local CAS root may not be a symlink")
        self.root = root.resolve()
        self.root.mkdir(parents=True, exist_ok=True)
        self.locks = self.root / ".locks"
        if self.locks.exists() and self.locks.is_symlink():
            raise MathFlowError("local CAS lock directory may not be a symlink")
        self.locks.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def _parts(key: str) -> tuple[str, ...]:
        if not isinstance(key, str):
            raise MathFlowError("object-store key is unsafe")
        path = PurePosixPath(key)
        if (
            path.is_absolute()
            or not path.parts
            or path.as_posix() != key
            or any(
                part in {"", ".", ".."} or not SAFE_KEY_PART.fullmatch(part)
                for part in path.parts
            )
        ):
            raise MathFlowError("object-store key is unsafe")
        return tuple(path.parts)

    def _path(self, key: str) -> Path:
        target = self.root.joinpath(*self._parts(key))
        cursor = self.root
        for part in self._parts(key)[:-1]:
            cursor = cursor / part
            if cursor.exists() and cursor.is_symlink():
                raise MathFlowError("object-store key traverses a symlink")
        resolved_parent = target.parent.resolve()
        try:
            resolved_parent.relative_to(self.root)
        except ValueError as exc:
            raise MathFlowError("object-store key escapes its root") from exc
        if target.exists() and target.is_symlink():
            raise MathFlowError("object-store object may not be a symlink")
        return target

    def _lock_path(self, key: str) -> Path:
        digest = sha256_bytes(key.encode("utf-8")).removeprefix("sha256:")
        return self.locks / f"{digest}.lock"

    def _locked(self, key: str):
        lock_path = self._lock_path(key)
        descriptor = os.open(lock_path, os.O_CREAT | os.O_RDWR, 0o600)

        class Lock:
            def __enter__(inner):
                fcntl.flock(descriptor, fcntl.LOCK_EX)
                return inner

            def __exit__(inner, exc_type, exc, traceback):
                fcntl.flock(descriptor, fcntl.LOCK_UN)
                os.close(descriptor)

        return Lock()

    @staticmethod
    def _write_replace(target: Path, value: bytes) -> None:
        target.parent.mkdir(parents=True, exist_ok=True)
        descriptor, temporary_name = tempfile.mkstemp(
            prefix=f".{target.name}.", suffix=".tmp", dir=target.parent
        )
        temporary = Path(temporary_name)
        try:
            with os.fdopen(descriptor, "wb") as handle:
                handle.write(value)
                handle.flush()
                os.fsync(handle.fileno())
            os.replace(temporary, target)
            directory = os.open(target.parent, os.O_RDONLY)
            try:
                os.fsync(directory)
            finally:
                os.close(directory)
        finally:
            if temporary.exists():
                temporary.unlink()

    def get(self, key: str) -> StoredValue | None:
        target = self._path(key)
        if not target.exists():
            return None
        if not target.is_file():
            raise MathFlowError("object-store value is not a regular file")
        value = target.read_bytes()
        return StoredValue(value=value, version=sha256_bytes(value))

    def put_immutable(self, key: str, value: bytes) -> str:
        if not isinstance(value, bytes):
            raise MathFlowError("immutable object value must be bytes")
        target = self._path(key)
        with self._locked(key):
            current = self.get(key)
            if current is not None:
                if current.value != value:
                    raise ImmutableConflict("immutable object already has different bytes")
                return current.version
            self._write_replace(target, value)
        return sha256_bytes(value)

    def compare_and_swap(
        self, key: str, expected_version: str | None, value: bytes
    ) -> str:
        if expected_version is not None and not DIGEST.fullmatch(expected_version):
            raise MathFlowError("CAS expected version must be a sha256 digest or null")
        if not isinstance(value, bytes):
            raise MathFlowError("CAS value must be bytes")
        target = self._path(key)
        with self._locked(key):
            current = self.get(key)
            current_version = current.version if current is not None else None
            if current_version != expected_version:
                raise CASConflict("CAS reference changed from its expected version")
            self._write_replace(target, value)
        return sha256_bytes(value)


def _json_bytes(value: object) -> bytes:
    try:
        return (canonical_json(value) + "\n").encode("utf-8")
    except (TypeError, ValueError) as exc:
        raise MathFlowError("pipeline artifact must be canonical JSON") from exc


def _json_value(value: bytes, label: str) -> dict[str, object]:
    try:
        result = json.loads(value)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise MathFlowError(f"{label} is not valid UTF-8 JSON") from exc
    if not isinstance(result, dict):
        raise MathFlowError(f"{label} must be a JSON object")
    return result


def _content_digest(value: Mapping[str, object], digest_field: str) -> str:
    core = {key: copy.deepcopy(item) for key, item in value.items() if key != digest_field}
    return f"sha256:{sha256_json(core)}"


def _require_digest(value: object, label: str, *, nullable: bool = False) -> str | None:
    if value is None and nullable:
        return None
    if not isinstance(value, str) or not DIGEST.fullmatch(value):
        raise MathFlowError(f"{label} must be a sha256 digest")
    return value


def _require_transaction(value: object, label: str) -> str:
    if not isinstance(value, str) or not GIT_SHA.fullmatch(value):
        raise MathFlowError(f"{label} must be a canonical transaction ID")
    return value


def _require_positive_integer(value: object, label: str) -> int:
    if not isinstance(value, int) or isinstance(value, bool) or value < 1:
        raise MathFlowError(f"{label} must be a positive integer")
    return value


def _object_key(kind: str, digest: str, suffix: str = "json") -> str:
    _require_digest(digest, f"{kind} object digest")
    return f"objects/{kind}/{digest.removeprefix('sha256:')}.{suffix}"


def _lane_key(projection_id: str, problem: str) -> str:
    if not IDENTIFIER.fullmatch(projection_id) or not IDENTIFIER.fullmatch(problem):
        raise MathFlowError("pipeline lane identity is invalid")
    return f"refs/work-accounting/{projection_id.replace('/', '__')}/{problem}.json"


def _call_hook(hook: CrashHook | None, boundary: str) -> None:
    if hook is not None:
        hook(boundary)


def _validate_completed_transition(value: object, label: str) -> dict[str, object]:
    if not isinstance(value, dict) or set(value) != COMPLETED_FIELDS:
        raise MathFlowError(f"{label} has invalid fields")
    _require_transaction(value.get("subjectTransactionId"), f"{label} subject")
    _require_positive_integer(value.get("ledgerOrdinal"), f"{label} ordinal")
    for field in COMPLETED_FIELDS - {"subjectTransactionId", "ledgerOrdinal"}:
        _require_digest(value.get(field), f"{label} {field}")
    return value


def _validate_pending_transition(value: object) -> dict[str, object] | None:
    if value is None:
        return None
    if not isinstance(value, dict) or set(value) != PENDING_FIELDS:
        raise MathFlowError("pipeline pending transition has invalid fields")
    if value.get("stage") not in {"awaiting-work", "publication-prepared"}:
        raise MathFlowError("pipeline pending transition has an invalid stage")
    _require_transaction(value.get("subjectTransactionId"), "pipeline pending subject")
    _require_positive_integer(value.get("ledgerOrdinal"), "pipeline pending ordinal")
    required = {
        "submissionInputDigest",
        "builderResultDigest",
        "builderHandoffDigest",
        "topologyAlignmentDigest",
        "beforeKnowledgeStateDigest",
        "afterKnowledgeStateDigest",
    }
    for field in required:
        _require_digest(value.get(field), f"pipeline pending {field}")
    optional = {
        "claimDigest",
        "workBundleDigest",
        "publicationManifestDigest",
        "nextAccountingStateDigest",
        "nextScheduleDigest",
    }
    for field in optional:
        _require_digest(value.get(field), f"pipeline pending {field}", nullable=True)
    if value["stage"] == "awaiting-work":
        if any(
            value[field] is not None
            for field in (
                "workBundleDigest",
                "publicationManifestDigest",
                "nextAccountingStateDigest",
                "nextScheduleDigest",
            )
        ):
            raise MathFlowError("awaiting-work transition contains publication outputs")
    elif any(value[field] is None for field in optional):
        raise MathFlowError("publication-prepared transition is incomplete")
    return value


def validate_work_accounting_pipeline_state(value: object) -> dict[str, object]:
    if not isinstance(value, dict) or set(value) != PIPELINE_FIELDS:
        raise MathFlowError("work-accounting pipeline state has an invalid envelope")
    if value.get("schemaVersion") != 1:
        raise MathFlowError("work-accounting pipeline state has an unsupported version")
    if (
        not isinstance(value.get("problemId"), str)
        or not IDENTIFIER.fullmatch(value["problemId"])
        or not isinstance(value.get("projectionId"), str)
        or not IDENTIFIER.fullmatch(value["projectionId"])
    ):
        raise MathFlowError("work-accounting pipeline identity is invalid")
    for field in (
        "projectionSpecDigest",
        "rootContractDigest",
        "formedKnowledgeStateDigest",
        "accountingStateDigest",
        "scheduleDigest",
    ):
        _require_digest(value.get(field), f"pipeline {field}")
    phase = value.get("phase")
    if phase not in {"ready", "awaiting-work", "publication-prepared"}:
        raise MathFlowError("work-accounting pipeline phase is invalid")
    completed = value.get("completedTransitions")
    if not isinstance(completed, list):
        raise MathFlowError("pipeline completed transitions must be an array")
    ids: list[str] = []
    ordinals: list[int] = []
    for index, item in enumerate(completed):
        record = _validate_completed_transition(
            item, f"pipeline completed transition {index + 1}"
        )
        ids.append(str(record["subjectTransactionId"]))
        ordinals.append(int(record["ledgerOrdinal"]))
    if len(ids) != len(set(ids)) or ordinals != sorted(set(ordinals)):
        raise MathFlowError("pipeline completed transitions are not canonical")
    pending = _validate_pending_transition(value.get("pendingTransition"))
    if (phase == "ready") != (pending is None):
        raise MathFlowError("pipeline phase and pending transition disagree")
    if pending is not None:
        if pending["stage"] != phase:
            raise MathFlowError("pipeline and pending phases disagree")
        if pending["subjectTransactionId"] in ids:
            raise MathFlowError("pipeline pending subject is already completed")
        if ordinals and int(pending["ledgerOrdinal"]) <= ordinals[-1]:
            raise MathFlowError("pipeline pending subject is outside canonical order")
        if value["formedKnowledgeStateDigest"] != pending["afterKnowledgeStateDigest"]:
            raise MathFlowError("pipeline formed state differs from pending builder output")
    if value.get("pipelineStateDigest") != _content_digest(
        value, "pipelineStateDigest"
    ):
        raise MathFlowError("work-accounting pipeline state digest mismatch")
    return value


def _seal_pipeline_state(value: Mapping[str, object]) -> dict[str, object]:
    result = {
        key: copy.deepcopy(item)
        for key, item in value.items()
        if key != "pipelineStateDigest"
    }
    result["pipelineStateDigest"] = _content_digest(result, "pipelineStateDigest")
    return validate_work_accounting_pipeline_state(result)


def _seal_submission(value: Mapping[str, object]) -> dict[str, object]:
    result = {
        key: copy.deepcopy(item)
        for key, item in value.items()
        if key != "submissionInputDigest"
    }
    result["submissionInputDigest"] = _content_digest(
        result, "submissionInputDigest"
    )
    return result


def normalize_work_accounting_submission(
    submission: AcceptedWorkSubmission, problem: str
) -> tuple[dict[str, object], dict[str, bytes]]:
    """Normalize one accepted submission into the pipeline's exact CAS input.

    Hosted callers use this provider-free boundary when constructing disposition
    snapshots.  Returning the normalized evidence chunks alongside the sealed
    record keeps the digest calculation identical to pipeline execution.
    """

    transaction_id = _require_transaction(
        submission.transaction_id, "accepted pipeline submission"
    )
    ordinal = _require_positive_integer(
        submission.ordinal, "accepted pipeline submission ordinal"
    )
    if not isinstance(submission.judgment_id, str) or not DIGEST.fullmatch(
        submission.judgment_id
    ):
        raise MathFlowError("accepted pipeline submission judgment is invalid")
    claims = [copy.deepcopy(dict(item)) for item in submission.accepted_claims]
    if not claims:
        raise MathFlowError("accepted pipeline submission has no accepted claims")
    claim_keys: list[str] = []
    for claim in claims:
        if set(claim) != {"claimKey", "statement", "dependencyTransactionIds"}:
            raise MathFlowError("accepted pipeline claim has invalid fields")
        claim_key = claim.get("claimKey")
        dependencies = claim.get("dependencyTransactionIds")
        if (
            not isinstance(claim_key, str)
            or not IDENTIFIER.fullmatch(claim_key)
            or not isinstance(claim.get("statement"), str)
            or not str(claim["statement"]).strip()
            or not isinstance(dependencies, list)
            or len(dependencies) != len(set(dependencies))
            or any(not isinstance(item, str) or not GIT_SHA.fullmatch(item) for item in dependencies)
        ):
            raise MathFlowError("accepted pipeline claim is invalid")
        claim_keys.append(claim_key)
    if claim_keys != sorted(set(claim_keys)):
        raise MathFlowError("accepted pipeline claims are not canonical")
    refs = [copy.deepcopy(dict(item)) for item in submission.accepted_claim_refs]
    ref_keys: list[str] = []
    for ref in refs:
        if (
            set(ref)
            != {"transactionId", "claimKey", "judgmentId", "assessmentDigest"}
            or ref.get("transactionId") != transaction_id
            or ref.get("judgmentId") != submission.judgment_id
            or not isinstance(ref.get("claimKey"), str)
        ):
            raise MathFlowError("accepted pipeline claim reference is invalid")
        _require_digest(ref.get("assessmentDigest"), "accepted assessment digest")
        ref_keys.append(str(ref["claimKey"]))
    if ref_keys != sorted(set(ref_keys)) or ref_keys != claim_keys:
        raise MathFlowError("accepted pipeline claim references do not match claims")
    manifest = validate_submission_evidence_manifest(
        copy.deepcopy(dict(submission.evidence_manifest))
    )
    if (
        manifest["problemId"] != problem
        or manifest["subjectTransactionId"] != transaction_id
    ):
        raise MathFlowError("accepted pipeline evidence belongs to another submission")
    chunks = {str(key): bytes(value) for key, value in submission.evidence_chunks.items()}
    reconstruct_submission_evidence(manifest, chunks)
    chunk_digests = sorted(chunks)
    if any(sha256_bytes(chunks[digest]) != digest for digest in chunk_digests):
        raise MathFlowError("accepted pipeline evidence chunk digest mismatch")
    record = _seal_submission(
        {
            "schemaVersion": 1,
            "problemId": problem,
            "transactionId": transaction_id,
            "ordinal": ordinal,
            "acceptedClaims": claims,
            "judgmentId": submission.judgment_id,
            "acceptedClaimRefs": refs,
            "evidenceManifest": manifest,
            "evidenceChunkDigests": chunk_digests,
        }
    )
    return record, chunks


def validate_work_accounting_submission_input(value: object) -> dict[str, object]:
    if not isinstance(value, dict) or set(value) != SUBMISSION_FIELDS:
        raise MathFlowError("pipeline submission input has an invalid envelope")
    if value.get("schemaVersion") != 1:
        raise MathFlowError("pipeline submission input has an unsupported version")
    _require_transaction(value.get("transactionId"), "pipeline submission subject")
    _require_positive_integer(value.get("ordinal"), "pipeline submission ordinal")
    if not isinstance(value.get("problemId"), str) or not IDENTIFIER.fullmatch(
        value["problemId"]
    ):
        raise MathFlowError("pipeline submission problem ID is invalid")
    _require_digest(value.get("judgmentId"), "pipeline submission judgment")
    claims = value.get("acceptedClaims")
    if not isinstance(claims, list) or not claims:
        raise MathFlowError("pipeline submission accepted claims are invalid")
    claim_keys: list[str] = []
    for claim in claims:
        dependencies = claim.get("dependencyTransactionIds") if isinstance(claim, dict) else None
        if (
            not isinstance(claim, dict)
            or set(claim) != {"claimKey", "statement", "dependencyTransactionIds"}
            or not isinstance(claim.get("claimKey"), str)
            or not IDENTIFIER.fullmatch(str(claim["claimKey"]))
            or not isinstance(claim.get("statement"), str)
            or not str(claim["statement"]).strip()
            or not isinstance(dependencies, list)
            or len(dependencies) != len(set(dependencies))
            or any(
                not isinstance(item, str) or not GIT_SHA.fullmatch(item)
                for item in dependencies
            )
        ):
            raise MathFlowError("pipeline submission accepted claim is invalid")
        claim_keys.append(str(claim["claimKey"]))
    if claim_keys != sorted(set(claim_keys)):
        raise MathFlowError("pipeline submission accepted claims are not canonical")
    refs = value.get("acceptedClaimRefs")
    if not isinstance(refs, list) or not refs:
        raise MathFlowError("pipeline submission accepted claim refs are invalid")
    ref_keys: list[str] = []
    for ref in refs:
        if (
            not isinstance(ref, dict)
            or set(ref)
            != {"transactionId", "claimKey", "judgmentId", "assessmentDigest"}
            or ref.get("transactionId") != value["transactionId"]
            or ref.get("judgmentId") != value["judgmentId"]
            or not isinstance(ref.get("claimKey"), str)
        ):
            raise MathFlowError("pipeline submission accepted claim ref is invalid")
        _require_digest(ref.get("assessmentDigest"), "pipeline assessment digest")
        ref_keys.append(str(ref["claimKey"]))
    if ref_keys != claim_keys:
        raise MathFlowError("pipeline submission claim references do not match claims")
    manifest = validate_submission_evidence_manifest(value.get("evidenceManifest"))
    if (
        manifest["problemId"] != value["problemId"]
        or manifest["subjectTransactionId"] != value["transactionId"]
    ):
        raise MathFlowError("pipeline submission evidence binding mismatch")
    chunks = value.get("evidenceChunkDigests")
    referenced_chunks = sorted(
        {
            str(chunk["digest"])
            for file_record in manifest["files"]
            for chunk in file_record["chunks"]
        }
    )
    if (
        not isinstance(chunks, list)
        or chunks != sorted(set(chunks))
        or any(not isinstance(item, str) or not DIGEST.fullmatch(item) for item in chunks)
        or chunks != referenced_chunks
    ):
        raise MathFlowError("pipeline submission evidence chunk index is invalid")
    if value.get("submissionInputDigest") != _content_digest(
        value, "submissionInputDigest"
    ):
        raise MathFlowError("pipeline submission input digest mismatch")
    return value


def _put_json_immutable(store: CASObjectStore, key: str, value: object) -> str:
    return store.put_immutable(key, _json_bytes(value))


def _load_json(store: CASObjectStore, key: str, label: str) -> dict[str, object]:
    stored = store.get(key)
    if stored is None:
        raise MathFlowError(f"{label} is missing from immutable storage")
    return _json_value(stored.value, label)


def _put_digest_object(
    store: CASObjectStore, kind: str, value: Mapping[str, object], digest_field: str
) -> None:
    digest = _require_digest(value.get(digest_field), f"{kind} {digest_field}")
    assert isinstance(digest, str)
    _put_json_immutable(store, _object_key(kind, digest), value)


def _load_digest_object(
    store: CASObjectStore, kind: str, digest: str
) -> dict[str, object]:
    return _load_json(store, _object_key(kind, digest), f"{kind} object")


def _put_pipeline_objects(
    store: CASObjectStore,
    *,
    root_contract: Mapping[str, object] | None = None,
    knowledge_state: Mapping[str, object] | None = None,
    accounting_state: Mapping[str, object] | None = None,
    schedule: Mapping[str, object] | None = None,
    pipeline_state: Mapping[str, object] | None = None,
) -> None:
    if root_contract is not None:
        _put_digest_object(store, "root-contracts", root_contract, "rootContractDigest")
    if knowledge_state is not None:
        _put_digest_object(store, "knowledge-states", knowledge_state, "stateDigest")
    if accounting_state is not None:
        _put_digest_object(store, "accounting-states", accounting_state, "stateDigest")
    if schedule is not None:
        _put_digest_object(store, "schedules", schedule, "scheduleDigest")
    if pipeline_state is not None:
        _put_digest_object(
            store, "pipeline-states", pipeline_state, "pipelineStateDigest"
        )


def read_work_accounting_pipeline_state(
    store: CASObjectStore, *, projection_id: str, problem: str
) -> tuple[dict[str, object], str] | None:
    stored = store.get(_lane_key(projection_id, problem))
    if stored is None:
        return None
    return validate_work_accounting_pipeline_state(
        _json_value(stored.value, "work-accounting pipeline lane")
    ), stored.version


def _load_live_objects(
    store: CASObjectStore, pipeline: Mapping[str, object]
) -> tuple[
    dict[str, object], dict[str, object], dict[str, object], dict[str, object]
]:
    contract = validate_root_contract(
        _load_digest_object(
            store, "root-contracts", str(pipeline["rootContractDigest"])
        ),
        str(pipeline["problemId"]),
    )
    knowledge = validate_research_program_state_v2(
        _load_digest_object(
            store, "knowledge-states", str(pipeline["formedKnowledgeStateDigest"])
        ),
        str(pipeline["problemId"]),
    )
    schedule = validate_work_accounting_schedule(
        _load_digest_object(store, "schedules", str(pipeline["scheduleDigest"]))
    )
    accounting_knowledge_digest = str(schedule["terminalKnowledgeStateDigest"])
    accounting_knowledge = validate_research_program_state_v2(
        _load_digest_object(store, "knowledge-states", accounting_knowledge_digest),
        str(pipeline["problemId"]),
    )
    accounting = validate_work_accounting_state(
        _load_digest_object(
            store, "accounting-states", str(pipeline["accountingStateDigest"])
        ),
        accounting_knowledge,
        contract,
    )
    if (
        contract["rootContractDigest"] != pipeline["rootContractDigest"]
        or schedule["scheduleDigest"] != pipeline["scheduleDigest"]
        or accounting["stateDigest"] != pipeline["accountingStateDigest"]
        or schedule["terminalAccountingStateDigest"] != accounting["stateDigest"]
    ):
        raise MathFlowError("pipeline lane references inconsistent live objects")
    if pipeline["phase"] == "ready" and (
        accounting["knowledgeStateDigest"] != knowledge["stateDigest"]
        or schedule["terminalKnowledgeStateDigest"] != knowledge["stateDigest"]
    ):
        raise MathFlowError("ready pipeline does not have one common terminal state")
    return contract, knowledge, accounting, schedule


def initialize_work_accounting_pipeline(
    store: CASObjectStore,
    repository_root: Path,
    *,
    problem: str,
    projection_id: str,
    projection_spec_digest: str,
    root_contract: object,
    initial_knowledge_state: object,
    initial_accounting_state: object,
    resolved_submission_ids: Sequence[str],
    head: str = "HEAD",
    maximum_attempts: int = 3,
    base_retry_seconds: int = 60,
) -> dict[str, object]:
    contract = validate_root_contract(root_contract, problem)
    knowledge = validate_research_program_state_v2(initial_knowledge_state, problem)
    accounting = validate_work_accounting_state(
        initial_accounting_state, knowledge, contract
    )
    schedule = initialize_work_accounting_schedule(
        repository_root,
        problem=problem,
        projection_id=projection_id,
        projection_spec_digest=projection_spec_digest,
        root_contract=contract,
        accounting_state=accounting,
        knowledge_state=knowledge,
        resolved_submission_ids=resolved_submission_ids,
        head=head,
        maximum_attempts=maximum_attempts,
        base_retry_seconds=base_retry_seconds,
    )
    if schedule["subjects"] or accounting["processedSubmissionIds"]:
        raise MathFlowError(
            "pipeline initialization requires an unprocessed builder-v6 baseline"
        )
    pipeline = _seal_pipeline_state(
        {
            "schemaVersion": 1,
            "problemId": problem,
            "projectionId": projection_id,
            "projectionSpecDigest": projection_spec_digest,
            "rootContractDigest": contract["rootContractDigest"],
            "phase": "ready",
            "formedKnowledgeStateDigest": knowledge["stateDigest"],
            "accountingStateDigest": accounting["stateDigest"],
            "scheduleDigest": schedule["scheduleDigest"],
            "completedTransitions": [],
            "pendingTransition": None,
        }
    )
    _put_pipeline_objects(
        store,
        root_contract=contract,
        knowledge_state=knowledge,
        accounting_state=accounting,
        schedule=schedule,
        pipeline_state=pipeline,
    )
    lane_key = _lane_key(projection_id, problem)
    try:
        store.compare_and_swap(lane_key, None, _json_bytes(pipeline))
    except CASConflict:
        existing = read_work_accounting_pipeline_state(
            store, projection_id=projection_id, problem=problem
        )
        if existing is None or existing[0] != pipeline:
            raise
        return existing[0]
    return pipeline


def _canonicalize_submissions(
    repository_root: Path,
    *,
    problem: str,
    head: str,
    submissions: Sequence[AcceptedWorkSubmission],
) -> list[tuple[dict[str, object], dict[str, bytes]]]:
    canonical = ledger(repository_root, problem, head)
    ordinals = {
        str(item["transactionId"]): int(item["ordinal"])
        for item in canonical["transactions"]
    }
    records = [
        normalize_work_accounting_submission(item, problem) for item in submissions
    ]
    ids = [str(record[0]["transactionId"]) for record in records]
    if len(ids) != len(set(ids)):
        raise MathFlowError("pipeline accepted submissions repeat a transaction")
    if any(
        transaction_id not in ordinals
        or int(record["ordinal"]) != ordinals[transaction_id]
        for record, transaction_id in ((item[0], str(item[0]["transactionId"])) for item in records)
    ):
        raise MathFlowError("pipeline accepted submission ordinal is not canonical")
    expected = [item for item in ordinals if item in set(ids)]
    if ids != expected:
        raise MathFlowError("pipeline accepted submissions are not in first-parent order")
    return records


def _submission_key(digest: str) -> str:
    return _object_key("submission-inputs", digest)


def _store_submission(
    store: CASObjectStore,
    submission: Mapping[str, object],
    chunks: Mapping[str, bytes],
) -> None:
    validate_work_accounting_submission_input(dict(submission))
    for digest, content in sorted(chunks.items()):
        store.put_immutable(_object_key("evidence-chunks", digest, "bin"), content)
    _put_json_immutable(
        store, _submission_key(str(submission["submissionInputDigest"])), submission
    )


def _load_submission(
    store: CASObjectStore, digest: str
) -> tuple[dict[str, object], dict[str, bytes]]:
    submission = validate_work_accounting_submission_input(
        _load_json(store, _submission_key(digest), "pipeline submission input")
    )
    chunks = {
        str(chunk_digest): store.get(
            _object_key("evidence-chunks", str(chunk_digest), "bin")
        )
        for chunk_digest in submission["evidenceChunkDigests"]
    }
    if any(value is None for value in chunks.values()):
        raise MathFlowError("pipeline submission evidence chunk is missing")
    values = {
        digest_value: stored.value
        for digest_value, stored in chunks.items()
        if stored is not None
    }
    reconstruct_submission_evidence(submission["evidenceManifest"], values)
    return submission, values


def _builder_request(
    base_knowledge: Mapping[str, object], submission: Mapping[str, object]
) -> dict[str, object]:
    core = {
        "schemaVersion": 1,
        "problemId": submission["problemId"],
        "subjectTransactionId": submission["transactionId"],
        "ledgerOrdinal": submission["ordinal"],
        "baseKnowledgeStateDigest": base_knowledge["stateDigest"],
        "submissionInputDigest": submission["submissionInputDigest"],
        "judgmentId": submission["judgmentId"],
    }
    return {**core, "builderRequestDigest": _content_digest(core, "builderRequestDigest")}


def _proposal_index_key(builder_request_digest: str) -> str:
    _require_digest(builder_request_digest, "builder request digest")
    return (
        "indexes/builder-proposals/"
        f"{builder_request_digest.removeprefix('sha256:')}.json"
    )


def _load_or_call_builder(
    store: CASObjectStore,
    provider: BuilderTransitionProvider,
    *,
    base_knowledge: Mapping[str, object],
    submission: Mapping[str, object],
) -> tuple[dict[str, object], str, str]:
    request = _builder_request(base_knowledge, submission)
    request_digest = str(request["builderRequestDigest"])
    key = _proposal_index_key(request_digest)
    existing = store.get(key)
    if existing is not None:
        envelope = _json_value(existing.value, "builder proposal index")
    else:
        proposal = provider(
            base_knowledge_state=copy.deepcopy(dict(base_knowledge)),
            submission=copy.deepcopy(dict(submission)),
        )
        if not isinstance(proposal, dict):
            raise MathFlowError("builder transition provider returned a non-object")
        proposal_digest = f"sha256:{sha256_json(proposal)}"
        envelope = {
            "schemaVersion": 1,
            "builderRequestDigest": request_digest,
            "builderProposalDigest": proposal_digest,
            "transition": copy.deepcopy(proposal),
        }
        envelope["proposalIndexDigest"] = _content_digest(
            envelope, "proposalIndexDigest"
        )
        try:
            _put_json_immutable(store, key, envelope)
        except ImmutableConflict:
            envelope = _load_json(store, key, "builder proposal index")
    if (
        set(envelope)
        != {
            "schemaVersion",
            "builderRequestDigest",
            "builderProposalDigest",
            "transition",
            "proposalIndexDigest",
        }
        or envelope.get("schemaVersion") != 1
        or envelope.get("builderRequestDigest") != request_digest
        or not isinstance(envelope.get("transition"), dict)
        or envelope.get("builderProposalDigest")
        != f"sha256:{sha256_json(envelope['transition'])}"
        or envelope.get("proposalIndexDigest")
        != _content_digest(envelope, "proposalIndexDigest")
    ):
        raise MathFlowError("builder proposal index binding mismatch")
    return (
        copy.deepcopy(envelope["transition"]),
        request_digest,
        str(envelope["builderProposalDigest"]),
    )


def _seal_builder_result(value: Mapping[str, object]) -> dict[str, object]:
    result = {
        key: copy.deepcopy(item)
        for key, item in value.items()
        if key != "builderResultDigest"
    }
    result["builderResultDigest"] = _content_digest(result, "builderResultDigest")
    return validate_work_accounting_builder_result(result)


def validate_work_accounting_builder_result(value: object) -> dict[str, object]:
    if not isinstance(value, dict) or set(value) != BUILDER_RESULT_FIELDS:
        raise MathFlowError("pipeline builder result has an invalid envelope")
    if value.get("schemaVersion") != 1:
        raise MathFlowError("pipeline builder result has an unsupported version")
    if not isinstance(value.get("problemId"), str) or not IDENTIFIER.fullmatch(
        value["problemId"]
    ):
        raise MathFlowError("pipeline builder result problem is invalid")
    _require_transaction(value.get("subjectTransactionId"), "builder result subject")
    _require_positive_integer(value.get("ledgerOrdinal"), "builder result ordinal")
    for field in BUILDER_RESULT_FIELDS - {
        "schemaVersion",
        "problemId",
        "subjectTransactionId",
        "ledgerOrdinal",
    }:
        _require_digest(value.get(field), f"builder result {field}")
    if value.get("builderResultDigest") != _content_digest(
        value, "builderResultDigest"
    ):
        raise MathFlowError("pipeline builder result digest mismatch")
    return value


def _materialize_builder_result(
    store: CASObjectStore,
    provider: BuilderTransitionProvider,
    *,
    base_knowledge: Mapping[str, object],
    submission: Mapping[str, object],
    crash_hook: CrashHook | None,
) -> tuple[
    dict[str, object],
    dict[str, object],
    dict[str, object],
    dict[str, object],
]:
    proposal, request_digest, proposal_digest = _load_or_call_builder(
        store,
        provider,
        base_knowledge=base_knowledge,
        submission=submission,
    )
    _call_hook(crash_hook, "builder-proposal-stored")
    reduced = apply_research_builder_v6_transition(
        dict(base_knowledge),
        proposal,
        accepted_claims=submission["acceptedClaims"],
        judgment_id=str(submission["judgmentId"]),
    )
    post = validate_research_program_state_v2(
        reduced["postState"], str(submission["problemId"])
    )
    alignment = validate_research_topology_alignment(
        reduced["topologyAlignment"], dict(base_knowledge), post
    )
    handoff = validate_research_builder_v6_handoff(
        reduced["sameWorldHandoff"],
        dict(base_knowledge),
        post,
        alignment,
        str(submission["transactionId"]),
    )
    result = _seal_builder_result(
        {
            "schemaVersion": 1,
            "problemId": submission["problemId"],
            "subjectTransactionId": submission["transactionId"],
            "ledgerOrdinal": submission["ordinal"],
            "submissionInputDigest": submission["submissionInputDigest"],
            "builderRequestDigest": request_digest,
            "builderProposalDigest": proposal_digest,
            "beforeKnowledgeStateDigest": base_knowledge["stateDigest"],
            "afterKnowledgeStateDigest": post["stateDigest"],
            "topologyAlignmentDigest": alignment["alignmentDigest"],
            "builderHandoffDigest": handoff["handoffDigest"],
        }
    )
    _put_pipeline_objects(store, knowledge_state=post)
    _put_digest_object(store, "topology-alignments", alignment, "alignmentDigest")
    _put_digest_object(store, "builder-handoffs", handoff, "handoffDigest")
    _put_digest_object(store, "builder-results", result, "builderResultDigest")
    return result, post, alignment, handoff


def _bundle_prefix(bundle_digest: str) -> str:
    _require_digest(bundle_digest, "work bundle digest")
    return f"objects/work-bundles/{bundle_digest.removeprefix('sha256:')}"


def _bundle_key(bundle_digest: str, relative: str) -> str:
    path = PurePosixPath(relative)
    if path.is_absolute() or not path.parts or ".." in path.parts:
        raise MathFlowError("work bundle artifact path is unsafe")
    for part in path.parts:
        if not SAFE_KEY_PART.fullmatch(part):
            raise MathFlowError("work bundle artifact path is unsafe")
    return f"{_bundle_prefix(bundle_digest)}/{'/'.join(path.parts)}"


def _store_work_bundle(
    store: CASObjectStore, bundle_dir: Path
) -> dict[str, object]:
    loaded = load_work_projection_bundle(bundle_dir)
    manifest = loaded["manifest"]
    bundle_digest = str(loaded["bundleDigest"])
    for artifact in manifest["artifacts"]:
        relative = str(artifact["path"])
        content = bundle_dir.joinpath(*PurePosixPath(relative).parts).read_bytes()
        if sha256_bytes(content) != artifact["digest"]:
            raise MathFlowError("work bundle changed after verification")
        store.put_immutable(_bundle_key(bundle_digest, relative), content)
    run_bytes = (bundle_dir / "run.json").read_bytes()
    if sha256_bytes(run_bytes) != bundle_digest:
        raise MathFlowError("work bundle manifest content address changed")
    store.put_immutable(_bundle_key(bundle_digest, "run.json"), run_bytes)
    return loaded


def _restore_work_bundle(
    store: CASObjectStore,
    bundle_digest: str,
    output_dir: Path,
) -> dict[str, object]:
    run = store.get(_bundle_key(bundle_digest, "run.json"))
    if run is None or run.version != bundle_digest:
        raise MathFlowError("immutable work bundle manifest is missing or misaddressed")
    manifest = _json_value(run.value, "immutable work bundle manifest")
    output_dir.mkdir(parents=True, exist_ok=False)
    for artifact in manifest.get("artifacts", []):
        if not isinstance(artifact, dict):
            raise MathFlowError("immutable work bundle artifact index is invalid")
        relative = str(artifact.get("path", ""))
        stored = store.get(_bundle_key(bundle_digest, relative))
        if stored is None or stored.version != artifact.get("digest"):
            raise MathFlowError("immutable work bundle artifact is missing or misaddressed")
        target = output_dir.joinpath(*PurePosixPath(relative).parts)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(stored.value)
    (output_dir / "run.json").write_bytes(run.value)
    return load_work_projection_bundle(
        output_dir, expected_bundle_digest=bundle_digest
    )


def materialize_stored_work_projection_bundle(
    store: CASObjectStore,
    *,
    bundle_digest: str,
    output_dir: Path,
) -> dict[str, object]:
    """Reconstruct and fully validate an immutable work bundle from a CAS store."""

    return _restore_work_bundle(store, bundle_digest, output_dir)


def _work_index_key(automatic_retry_key: str) -> str:
    _require_digest(automatic_retry_key, "automatic retry key")
    return (
        "indexes/work-results/"
        f"{automatic_retry_key.removeprefix('sha256:')}.json"
    )


def _frozen_with_access_candidate_key(automatic_retry_key: str) -> str:
    """Address one V2 ``W+`` candidate by retry-stable transition identity."""

    _require_digest(automatic_retry_key, "automatic retry key")
    return (
        "indexes/frozen-with-access-candidates/"
        f"{automatic_retry_key.removeprefix('sha256:')}.json"
    )


def _seal_work_index(value: Mapping[str, object]) -> dict[str, object]:
    result = {
        key: copy.deepcopy(item)
        for key, item in value.items()
        if key != "workResultIndexDigest"
    }
    result["workResultIndexDigest"] = _content_digest(
        result, "workResultIndexDigest"
    )
    return validate_work_accounting_work_result_index(result)


def validate_work_accounting_work_result_index(value: object) -> dict[str, object]:
    if not isinstance(value, dict) or set(value) != WORK_INDEX_FIELDS:
        raise MathFlowError("work result index has an invalid envelope")
    if value.get("schemaVersion") != 1:
        raise MathFlowError("work result index has an unsupported version")
    _require_transaction(value.get("subjectTransactionId"), "work result subject")
    for field in WORK_INDEX_FIELDS - {"schemaVersion", "subjectTransactionId"}:
        _require_digest(value.get(field), f"work result {field}")
    if value.get("workResultIndexDigest") != _content_digest(
        value, "workResultIndexDigest"
    ):
        raise MathFlowError("work result index digest mismatch")
    return value


def _validate_loaded_work(
    loaded: Mapping[str, object],
    *,
    claim: Mapping[str, object],
    submission: Mapping[str, object],
    builder_result: Mapping[str, object],
) -> None:
    manifest = loaded["manifest"]
    evaluation = loaded["evaluation"]
    if (
        manifest["subjectTransactionId"] != claim["subjectTransactionId"]
        or manifest["baseAccountingStateDigest"]
        != claim["predecessorAccountingStateDigest"]
        or manifest["baseKnowledgeStateDigest"]
        != builder_result["beforeKnowledgeStateDigest"]
        or manifest["targetKnowledgeStateDigest"]
        != builder_result["afterKnowledgeStateDigest"]
        or manifest["topologyAlignmentDigest"]
        != builder_result["topologyAlignmentDigest"]
        or manifest["submissionEvidenceManifestDigest"]
        != submission["evidenceManifest"]["manifestDigest"]
        or evaluation["subjectTransactionId"] != claim["subjectTransactionId"]
    ):
        raise MathFlowError("work bundle does not match the pending exact transition")


def _load_or_run_work_bundle(
    store: CASObjectStore,
    work_provider: WorkProjectionProvider,
    *,
    scratch_root: Path,
    claim: Mapping[str, object],
    submission: Mapping[str, object],
    evidence_chunks: Mapping[str, bytes],
    builder_result: Mapping[str, object],
    root_contract: Mapping[str, object],
    base_knowledge: Mapping[str, object],
    target_knowledge: Mapping[str, object],
    base_accounting: Mapping[str, object],
    alignment: Mapping[str, object],
) -> dict[str, object]:
    retry_key = str(claim["automaticRetryKey"])
    output_profile = getattr(
        work_provider, "output_profile", WORK_PROJECTION_PROFILE_V1
    )
    if output_profile not in {
        WORK_PROJECTION_PROFILE_V1,
        WORK_PROJECTION_PROFILE_V2,
    }:
        raise MathFlowError("work provider uses an unsupported output profile")
    existing = store.get(_work_index_key(retry_key))
    scratch_root.mkdir(parents=True, exist_ok=True)
    if existing is not None:
        index = validate_work_accounting_work_result_index(
            _json_value(existing.value, "work result index")
        )
        with tempfile.TemporaryDirectory(dir=scratch_root) as temporary:
            loaded = _restore_work_bundle(
                store, str(index["workBundleDigest"]), Path(temporary) / "bundle"
            )
        _validate_loaded_work(
            loaded,
            claim=claim,
            submission=submission,
            builder_result=builder_result,
        )
        return loaded

    frozen_candidate: object | None = None
    if output_profile == WORK_PROJECTION_PROFILE_V2:
        # The scheduler issues a new claim digest after a failed attempt, while
        # automaticRetryKey remains bound to the same semantic transition.  W+
        # must therefore be durable under the latter identity.  The local
        # checkpoint is also retry-stable, but the immutable CAS candidate is
        # authoritative when a later hosted attempt has a fresh scratch root.
        checkpoint_dir = (
            scratch_root
            / "checkpoints"
            / "work-accounting-v2"
            / retry_key.removeprefix("sha256:")
        )
        candidate_key = _frozen_with_access_candidate_key(retry_key)
        stored_candidate = store.get(candidate_key)
        if stored_candidate is None:
            proposed_candidate = prepare_frozen_with_access_candidate_v2(
                provider=work_provider,
                subject_transaction_id=str(claim["subjectTransactionId"]),
                root_contract=root_contract,
                base_knowledge_state=base_knowledge,
                target_knowledge_state=target_knowledge,
                base_accounting_state=base_accounting,
                topology_alignment=alignment,
                evidence_manifest=submission["evidenceManifest"],
                evidence_chunks=evidence_chunks,
                accepted_claim_refs=submission["acceptedClaimRefs"],
                checkpoint_dir=checkpoint_dir,
            )
            try:
                store.put_immutable(candidate_key, _json_bytes(proposed_candidate))
                frozen_candidate = proposed_candidate
            except ImmutableConflict:
                winner = store.get(candidate_key)
                if winner is None:  # pragma: no cover - immutable CAS contract
                    raise MathFlowError("frozen W+ candidate winner disappeared")
                frozen_candidate = _json_value(
                    winner.value, "frozen with-access candidate"
                )
        else:
            frozen_candidate = _json_value(
                stored_candidate.value, "frozen with-access candidate"
            )
    else:
        # Preserve the historical V1 claim-scoped checkpoint behavior exactly.
        checkpoint_dir = (
            scratch_root
            / "checkpoints"
            / str(claim["claimDigest"]).removeprefix("sha256:")
        )
    with tempfile.TemporaryDirectory(dir=scratch_root) as temporary:
        bundle_dir = Path(temporary) / "bundle"
        run_work_projection_bundle(
            output_dir=bundle_dir,
            provider=work_provider,
            subject_transaction_id=str(claim["subjectTransactionId"]),
            root_contract=root_contract,
            base_knowledge_state=base_knowledge,
            target_knowledge_state=target_knowledge,
            base_accounting_state=base_accounting,
            topology_alignment=alignment,
            evidence_manifest=submission["evidenceManifest"],
            evidence_chunks=evidence_chunks,
            accepted_claim_refs=submission["acceptedClaimRefs"],
            checkpoint_dir=checkpoint_dir,
            output_profile=output_profile,
            frozen_with_access_candidate=frozen_candidate,
        )
        loaded = _store_work_bundle(store, bundle_dir)
    _validate_loaded_work(
        loaded,
        claim=claim,
        submission=submission,
        builder_result=builder_result,
    )
    index = _seal_work_index(
        {
            "schemaVersion": 1,
            "automaticRetryKey": retry_key,
            "subjectTransactionId": claim["subjectTransactionId"],
            "predecessorAccountingStateDigest": claim[
                "predecessorAccountingStateDigest"
            ],
            "beforeKnowledgeStateDigest": builder_result[
                "beforeKnowledgeStateDigest"
            ],
            "afterKnowledgeStateDigest": builder_result[
                "afterKnowledgeStateDigest"
            ],
            "workBundleDigest": loaded["bundleDigest"],
            "evaluationDigest": loaded["evaluation"]["evaluationDigest"],
        }
    )
    try:
        _put_json_immutable(store, _work_index_key(retry_key), index)
    except ImmutableConflict:
        winner = validate_work_accounting_work_result_index(
            _load_json(store, _work_index_key(retry_key), "work result index")
        )
        with tempfile.TemporaryDirectory(dir=scratch_root) as temporary:
            loaded = _restore_work_bundle(
                store, str(winner["workBundleDigest"]), Path(temporary) / "bundle"
            )
        _validate_loaded_work(
            loaded,
            claim=claim,
            submission=submission,
            builder_result=builder_result,
        )
    return loaded


def _cas_pipeline_state(
    store: CASObjectStore,
    *,
    projection_id: str,
    problem: str,
    expected_version: str,
    next_state: Mapping[str, object],
) -> tuple[dict[str, object], str, bool]:
    state = validate_work_accounting_pipeline_state(dict(next_state))
    _put_pipeline_objects(store, pipeline_state=state)
    try:
        version = store.compare_and_swap(
            _lane_key(projection_id, problem), expected_version, _json_bytes(state)
        )
        return state, version, True
    except CASConflict:
        winner = read_work_accounting_pipeline_state(
            store, projection_id=projection_id, problem=problem
        )
        if winner is None:
            raise MathFlowError("pipeline CAS winner disappeared")
        return winner[0], winner[1], False


def _load_builder_objects(
    store: CASObjectStore, pending: Mapping[str, object]
) -> tuple[dict[str, object], dict[str, object], dict[str, object], dict[str, object]]:
    result = validate_work_accounting_builder_result(
        _load_digest_object(
            store, "builder-results", str(pending["builderResultDigest"])
        )
    )
    before = validate_research_program_state_v2(
        _load_digest_object(
            store, "knowledge-states", str(pending["beforeKnowledgeStateDigest"])
        )
    )
    after = validate_research_program_state_v2(
        _load_digest_object(
            store, "knowledge-states", str(pending["afterKnowledgeStateDigest"])
        )
    )
    alignment = validate_research_topology_alignment(
        _load_digest_object(
            store, "topology-alignments", str(pending["topologyAlignmentDigest"])
        ),
        before,
        after,
    )
    handoff = validate_research_builder_v6_handoff(
        _load_digest_object(
            store, "builder-handoffs", str(pending["builderHandoffDigest"])
        ),
        before,
        after,
        alignment,
        str(pending["subjectTransactionId"]),
    )
    if (
        result["subjectTransactionId"] != pending["subjectTransactionId"]
        or result["beforeKnowledgeStateDigest"] != before["stateDigest"]
        or result["afterKnowledgeStateDigest"] != after["stateDigest"]
        or result["topologyAlignmentDigest"] != alignment["alignmentDigest"]
        or result["builderHandoffDigest"] != handoff["handoffDigest"]
    ):
        raise MathFlowError("pending builder object bindings disagree")
    return result, before, after, alignment


def _begin_builder_transition(
    store: CASObjectStore,
    repository_root: Path,
    builder_provider: BuilderTransitionProvider,
    *,
    pipeline: Mapping[str, object],
    pipeline_version: str,
    submission: Mapping[str, object],
    chunks: Mapping[str, bytes],
    contract: Mapping[str, object],
    base_knowledge: Mapping[str, object],
    base_accounting: Mapping[str, object],
    schedule: Mapping[str, object],
    head: str,
    as_of: int,
    crash_hook: CrashHook | None,
) -> tuple[dict[str, object], str, bool]:
    _store_submission(store, submission, chunks)
    _call_hook(crash_hook, "submission-stored")
    result, post, alignment, handoff = _materialize_builder_result(
        store,
        builder_provider,
        base_knowledge=base_knowledge,
        submission=submission,
        crash_hook=crash_hook,
    )
    _call_hook(crash_hook, "builder-artifacts-stored")
    discovered = discover_work_accounting_subjects(
        schedule,
        repository_root,
        knowledge_state=post,
        resolved_submission_ids=schedule["resolvedSubmissionIds"],
        head=head,
    )
    plan = plan_next_work_accounting_transition(
        discovered,
        accounting_state=base_accounting,
        predecessor_knowledge_state=base_knowledge,
        target_knowledge_state=post,
        root_contract=contract,
        as_of=as_of,
    )
    if not plan["eligible"] or not isinstance(plan["claim"], dict):
        raise MathFlowError("new accepted builder subject is not accounting-eligible")
    claim = validate_work_accounting_transition_claim(plan["claim"])
    _put_digest_object(store, "transition-claims", claim, "claimDigest")
    _put_pipeline_objects(store, knowledge_state=post, schedule=discovered)
    pending = {
        "stage": "awaiting-work",
        "subjectTransactionId": submission["transactionId"],
        "ledgerOrdinal": submission["ordinal"],
        "submissionInputDigest": submission["submissionInputDigest"],
        "builderResultDigest": result["builderResultDigest"],
        "builderHandoffDigest": handoff["handoffDigest"],
        "topologyAlignmentDigest": alignment["alignmentDigest"],
        "beforeKnowledgeStateDigest": base_knowledge["stateDigest"],
        "afterKnowledgeStateDigest": post["stateDigest"],
        "claimDigest": claim["claimDigest"],
        "workBundleDigest": None,
        "publicationManifestDigest": None,
        "nextAccountingStateDigest": None,
        "nextScheduleDigest": None,
    }
    next_pipeline = _seal_pipeline_state(
        {
            **{
                key: copy.deepcopy(value)
                for key, value in pipeline.items()
                if key
                not in {
                    "pipelineStateDigest",
                    "phase",
                    "formedKnowledgeStateDigest",
                    "scheduleDigest",
                    "pendingTransition",
                }
            },
            "phase": "awaiting-work",
            "formedKnowledgeStateDigest": post["stateDigest"],
            "scheduleDigest": discovered["scheduleDigest"],
            "pendingTransition": pending,
        }
    )
    committed = _cas_pipeline_state(
        store,
        projection_id=str(pipeline["projectionId"]),
        problem=str(pipeline["problemId"]),
        expected_version=pipeline_version,
        next_state=next_pipeline,
    )
    if committed[2]:
        _call_hook(crash_hook, "builder-head-committed")
    return committed


def _failure_kind(exc: Exception) -> str:
    if isinstance(exc, WorkProviderFailure):
        return "provider-invalid"
    message = str(exc)
    if isinstance(exc, MathFlowError) and "strictly positive" in message:
        return "nonpositive-work-value"
    if isinstance(exc, MathFlowError) and any(
        marker in message
        for marker in (
            "provider output",
            "provider checkpoint",
            "work projection patch response",
            "counterfactual-safe fact",
            "counterfactual-safe assumptions",
            "topology-required accounting node",
        )
    ):
        return "provider-invalid"
    if isinstance(exc, MathFlowError):
        return "counterfactual-invalid"
    return "provider-invalid"


def _record_attempt_failure(
    store: CASObjectStore,
    *,
    pipeline: Mapping[str, object],
    pipeline_version: str,
    schedule: Mapping[str, object],
    claim: Mapping[str, object],
    exc: Exception,
    failed_at: int,
    crash_hook: CrashHook | None,
    failure_kind: str | None = None,
) -> tuple[dict[str, object], str, bool]:
    kind = failure_kind or _failure_kind(exc)
    evidence: dict[str, object] = {
        "schemaVersion": 1,
        "failureKind": kind,
        "claimDigest": claim["claimDigest"],
        "exceptionType": type(exc).__name__,
        "messageDigest": sha256_bytes(str(exc).encode("utf-8")),
    }
    evidence["failureEvidenceDigest"] = _content_digest(
        evidence, "failureEvidenceDigest"
    )
    _put_digest_object(
        store, "failure-evidence", evidence, "failureEvidenceDigest"
    )
    failed_schedule = record_work_accounting_failure(
        schedule,
        claim,
        failure_kind=kind,
        evidence_digest=str(evidence["failureEvidenceDigest"]),
        failed_at=failed_at,
    )
    _put_pipeline_objects(store, schedule=failed_schedule)
    _call_hook(crash_hook, "failure-artifacts-stored")
    pending = copy.deepcopy(pipeline["pendingTransition"])
    assert isinstance(pending, dict)
    pending["claimDigest"] = None
    next_pipeline = _seal_pipeline_state(
        {
            **{
                key: copy.deepcopy(value)
                for key, value in pipeline.items()
                if key not in {"pipelineStateDigest", "scheduleDigest", "pendingTransition"}
            },
            "scheduleDigest": failed_schedule["scheduleDigest"],
            "pendingTransition": pending,
        }
    )
    committed = _cas_pipeline_state(
        store,
        projection_id=str(pipeline["projectionId"]),
        problem=str(pipeline["problemId"]),
        expected_version=pipeline_version,
        next_state=next_pipeline,
    )
    if committed[2]:
        _call_hook(crash_hook, "failure-head-committed")
    return committed


def _ensure_pending_claim(
    store: CASObjectStore,
    *,
    pipeline: Mapping[str, object],
    pipeline_version: str,
    contract: Mapping[str, object],
    base_knowledge: Mapping[str, object],
    target_knowledge: Mapping[str, object],
    base_accounting: Mapping[str, object],
    schedule: Mapping[str, object],
    as_of: int,
    crash_hook: CrashHook | None,
) -> tuple[dict[str, object] | None, dict[str, object], str, bool]:
    pending = pipeline["pendingTransition"]
    assert isinstance(pending, dict)
    existing_digest = pending["claimDigest"]
    plan = plan_next_work_accounting_transition(
        schedule,
        accounting_state=base_accounting,
        predecessor_knowledge_state=base_knowledge,
        target_knowledge_state=target_knowledge,
        root_contract=contract,
        as_of=as_of,
    )
    if not plan["eligible"]:
        if existing_digest is not None:
            raise MathFlowError("pipeline stores a claim that is no longer eligible")
        return None, dict(pipeline), pipeline_version, False
    claim = validate_work_accounting_transition_claim(plan["claim"])
    if existing_digest is not None:
        stored_claim = validate_work_accounting_transition_claim(
            _load_digest_object(store, "transition-claims", str(existing_digest))
        )
        if claim != stored_claim:
            raise MathFlowError("stored pipeline claim is not reproducible")
        return claim, dict(pipeline), pipeline_version, False

    _put_digest_object(store, "transition-claims", claim, "claimDigest")
    next_pending = copy.deepcopy(pending)
    next_pending["claimDigest"] = claim["claimDigest"]
    next_pipeline = _seal_pipeline_state(
        {
            **{
                key: copy.deepcopy(value)
                for key, value in pipeline.items()
                if key not in {"pipelineStateDigest", "pendingTransition"}
            },
            "pendingTransition": next_pending,
        }
    )
    state, version, won = _cas_pipeline_state(
        store,
        projection_id=str(pipeline["projectionId"]),
        problem=str(pipeline["problemId"]),
        expected_version=pipeline_version,
        next_state=next_pipeline,
    )
    if won:
        _call_hook(crash_hook, "retry-claim-committed")
    return None, state, version, True


def _prepare_publication(
    store: CASObjectStore,
    work_provider: WorkProjectionProvider,
    *,
    scratch_root: Path,
    pipeline: Mapping[str, object],
    pipeline_version: str,
    contract: Mapping[str, object],
    base_accounting: Mapping[str, object],
    schedule: Mapping[str, object],
    claim: Mapping[str, object],
    submission: Mapping[str, object],
    evidence_chunks: Mapping[str, bytes],
    builder_result: Mapping[str, object],
    base_knowledge: Mapping[str, object],
    target_knowledge: Mapping[str, object],
    alignment: Mapping[str, object],
    failed_at: int,
    crash_hook: CrashHook | None,
) -> tuple[dict[str, object], str, bool]:
    try:
        loaded = _load_or_run_work_bundle(
            store,
            work_provider,
            scratch_root=scratch_root,
            claim=claim,
            submission=submission,
            evidence_chunks=evidence_chunks,
            builder_result=builder_result,
            root_contract=contract,
            base_knowledge=base_knowledge,
            target_knowledge=target_knowledge,
            base_accounting=base_accounting,
            alignment=alignment,
        )
    except Exception as exc:
        return _record_attempt_failure(
            store,
            pipeline=pipeline,
            pipeline_version=pipeline_version,
            schedule=schedule,
            claim=claim,
            exc=exc,
            failed_at=failed_at,
            crash_hook=crash_hook,
        )
    _call_hook(crash_hook, "work-bundle-stored")
    try:
        publication = materialize_work_accounting_publication_manifest(
            claim,
            evaluation=loaded["evaluation"],
            no_access_patch=loaded["noAccessPatch"],
            with_access_patch=loaded["withAccessPatch"],
            predecessor_accounting_state=base_accounting,
            committed_accounting_state=loaded["withAccessState"],
            predecessor_knowledge_state=base_knowledge,
            target_knowledge_state=target_knowledge,
            root_contract=contract,
            topology_alignment=alignment,
        )
        next_schedule = apply_work_accounting_publication(
            schedule,
            claim,
            publication,
            evaluation=loaded["evaluation"],
            no_access_patch=loaded["noAccessPatch"],
            with_access_patch=loaded["withAccessPatch"],
            predecessor_accounting_state=base_accounting,
            committed_accounting_state=loaded["withAccessState"],
            predecessor_knowledge_state=base_knowledge,
            target_knowledge_state=target_knowledge,
            root_contract=contract,
            topology_alignment=alignment,
        )
    except Exception as exc:
        return _record_attempt_failure(
            store,
            pipeline=pipeline,
            pipeline_version=pipeline_version,
            schedule=schedule,
            claim=claim,
            exc=exc,
            failed_at=failed_at,
            crash_hook=crash_hook,
            failure_kind="publication-invalid",
        )

    committed_accounting = loaded["withAccessState"]
    validate_work_accounting_publication_manifest(publication)
    _put_digest_object(
        store,
        "publication-manifests",
        publication,
        "publicationManifestDigest",
    )
    _put_pipeline_objects(
        store,
        knowledge_state=target_knowledge,
        accounting_state=committed_accounting,
        schedule=next_schedule,
    )
    _call_hook(crash_hook, "publication-artifacts-stored")
    pending = copy.deepcopy(pipeline["pendingTransition"])
    assert isinstance(pending, dict)
    pending.update(
        {
            "stage": "publication-prepared",
            "workBundleDigest": loaded["bundleDigest"],
            "publicationManifestDigest": publication["publicationManifestDigest"],
            "nextAccountingStateDigest": committed_accounting["stateDigest"],
            "nextScheduleDigest": next_schedule["scheduleDigest"],
        }
    )
    prepared = _seal_pipeline_state(
        {
            **{
                key: copy.deepcopy(value)
                for key, value in pipeline.items()
                if key not in {"pipelineStateDigest", "phase", "pendingTransition"}
            },
            "phase": "publication-prepared",
            "pendingTransition": pending,
        }
    )
    committed = _cas_pipeline_state(
        store,
        projection_id=str(pipeline["projectionId"]),
        problem=str(pipeline["problemId"]),
        expected_version=pipeline_version,
        next_state=prepared,
    )
    if committed[2]:
        _call_hook(crash_hook, "publication-prepared-committed")
    return committed


def _finalize_publication(
    store: CASObjectStore,
    *,
    pipeline: Mapping[str, object],
    pipeline_version: str,
    crash_hook: CrashHook | None,
) -> tuple[dict[str, object], str, bool]:
    pending = pipeline["pendingTransition"]
    assert isinstance(pending, dict)
    publication = validate_work_accounting_publication_manifest(
        _load_digest_object(
            store,
            "publication-manifests",
            str(pending["publicationManifestDigest"]),
        )
    )
    next_schedule = validate_work_accounting_schedule(
        _load_digest_object(store, "schedules", str(pending["nextScheduleDigest"]))
    )
    target_knowledge = validate_research_program_state_v2(
        _load_digest_object(
            store, "knowledge-states", str(pending["afterKnowledgeStateDigest"])
        )
    )
    contract = validate_root_contract(
        _load_digest_object(
            store, "root-contracts", str(pipeline["rootContractDigest"])
        ),
        str(pipeline["problemId"]),
    )
    next_accounting = validate_work_accounting_state(
        _load_digest_object(
            store, "accounting-states", str(pending["nextAccountingStateDigest"])
        ),
        target_knowledge,
        contract,
    )
    matching = next(
        (
            item
            for item in next_schedule["subjects"]
            if item["transactionId"] == pending["subjectTransactionId"]
        ),
        None,
    )
    if (
        matching is None
        or matching["completion"] is None
        or matching["completion"]["publicationManifestDigest"]
        != publication["publicationManifestDigest"]
        or next_schedule["terminalAccountingStateDigest"]
        != next_accounting["stateDigest"]
        or next_schedule["terminalKnowledgeStateDigest"]
        != target_knowledge["stateDigest"]
        or next_accounting["processedSubmissionIds"][-1]
        != pending["subjectTransactionId"]
    ):
        raise MathFlowError("prepared publication does not advance the exact lane")
    completed = [*copy.deepcopy(pipeline["completedTransitions"])]
    completed.append(
        {
            "subjectTransactionId": pending["subjectTransactionId"],
            "ledgerOrdinal": pending["ledgerOrdinal"],
            "submissionInputDigest": pending["submissionInputDigest"],
            "builderResultDigest": pending["builderResultDigest"],
            "builderHandoffDigest": pending["builderHandoffDigest"],
            "topologyAlignmentDigest": pending["topologyAlignmentDigest"],
            "workBundleDigest": pending["workBundleDigest"],
            "publicationManifestDigest": pending["publicationManifestDigest"],
            "accountingStateDigest": pending["nextAccountingStateDigest"],
        }
    )
    ready = _seal_pipeline_state(
        {
            **{
                key: copy.deepcopy(value)
                for key, value in pipeline.items()
                if key
                not in {
                    "pipelineStateDigest",
                    "phase",
                    "accountingStateDigest",
                    "scheduleDigest",
                    "completedTransitions",
                    "pendingTransition",
                }
            },
            "phase": "ready",
            "accountingStateDigest": next_accounting["stateDigest"],
            "scheduleDigest": next_schedule["scheduleDigest"],
            "completedTransitions": completed,
            "pendingTransition": None,
        }
    )
    committed = _cas_pipeline_state(
        store,
        projection_id=str(pipeline["projectionId"]),
        problem=str(pipeline["problemId"]),
        expected_version=pipeline_version,
        next_state=ready,
    )
    if committed[2]:
        _call_hook(crash_hook, "publication-head-committed")
    return committed


def advance_work_accounting_pipeline(
    store: CASObjectStore,
    repository_root: Path,
    *,
    projection_id: str,
    problem: str,
    builder_provider: BuilderTransitionProvider,
    work_provider: WorkProjectionProvider,
    accepted_submissions: Sequence[AcceptedWorkSubmission],
    scratch_root: Path,
    as_of: int,
    head: str = "HEAD",
    maximum_subjects: int | None = None,
    crash_hook: CrashHook | None = None,
) -> dict[str, object]:
    """Advance one inactive lane without making hosted batch size semantic."""

    if not isinstance(as_of, int) or isinstance(as_of, bool) or as_of < 0:
        raise MathFlowError("pipeline as-of time must be a non-negative integer")
    if maximum_subjects is not None:
        _require_positive_integer(maximum_subjects, "pipeline maximum subjects")
    normalized = _canonicalize_submissions(
        repository_root,
        problem=problem,
        head=head,
        submissions=accepted_submissions,
    )
    supplied = {str(record["transactionId"]): (record, chunks) for record, chunks in normalized}
    initial = read_work_accounting_pipeline_state(
        store, projection_id=projection_id, problem=problem
    )
    if initial is None:
        raise MathFlowError("work-accounting pipeline lane is not initialized")
    initial_completed = len(initial[0]["completedTransitions"])

    while True:
        current = read_work_accounting_pipeline_state(
            store, projection_id=projection_id, problem=problem
        )
        if current is None:  # pragma: no cover - immutable initialized lane
            raise MathFlowError("work-accounting pipeline lane disappeared")
        pipeline, pipeline_version = current
        if (
            pipeline["projectionId"] != projection_id
            or pipeline["problemId"] != problem
        ):
            raise MathFlowError("work-accounting pipeline lane identity changed")
        if (
            maximum_subjects is not None
            and len(pipeline["completedTransitions"]) - initial_completed
            >= maximum_subjects
            and pipeline["phase"] == "ready"
        ):
            return pipeline
        contract, formed_knowledge, accounting, schedule = _load_live_objects(
            store, pipeline
        )

        if pipeline["phase"] == "ready":
            completed_by_id = {
                str(item["subjectTransactionId"]): item
                for item in pipeline["completedTransitions"]
            }
            for transaction_id, (record, _) in supplied.items():
                completed = completed_by_id.get(transaction_id)
                if completed is not None and (
                    completed["submissionInputDigest"]
                    != record["submissionInputDigest"]
                ):
                    raise MathFlowError(
                        "supplied accepted submission differs from completed history"
                    )
            next_input = next(
                (
                    item
                    for item in normalized
                    if str(item[0]["transactionId"]) not in completed_by_id
                ),
                None,
            )
            if next_input is None:
                return pipeline
            record, chunks = next_input
            formed_ids = list(formed_knowledge["contributions"])
            completed_ids = [
                str(item["subjectTransactionId"])
                for item in pipeline["completedTransitions"]
            ]
            if set(formed_ids) != set(completed_ids):
                raise MathFlowError(
                    "ready pipeline builder and accounting histories disagree"
                )
            result = _begin_builder_transition(
                store,
                repository_root,
                builder_provider,
                pipeline=pipeline,
                pipeline_version=pipeline_version,
                submission=record,
                chunks=chunks,
                contract=contract,
                base_knowledge=formed_knowledge,
                base_accounting=accounting,
                schedule=schedule,
                head=head,
                as_of=as_of,
                crash_hook=crash_hook,
            )
            if not result[2]:
                continue
            continue

        pending = pipeline["pendingTransition"]
        assert isinstance(pending, dict)
        if pipeline["phase"] == "publication-prepared":
            result = _finalize_publication(
                store,
                pipeline=pipeline,
                pipeline_version=pipeline_version,
                crash_hook=crash_hook,
            )
            if not result[2]:
                continue
            continue

        submission, chunks = _load_submission(
            store, str(pending["submissionInputDigest"])
        )
        builder_result, base_knowledge, target_knowledge, alignment = (
            _load_builder_objects(store, pending)
        )
        claim, claim_pipeline, claim_version, changed = _ensure_pending_claim(
            store,
            pipeline=pipeline,
            pipeline_version=pipeline_version,
            contract=contract,
            base_knowledge=base_knowledge,
            target_knowledge=target_knowledge,
            base_accounting=accounting,
            schedule=schedule,
            as_of=as_of,
            crash_hook=crash_hook,
        )
        if changed:
            continue
        if claim is None:
            return pipeline
        result = _prepare_publication(
            store,
            work_provider,
            scratch_root=scratch_root,
            pipeline=claim_pipeline,
            pipeline_version=claim_version,
            contract=contract,
            base_accounting=accounting,
            schedule=schedule,
            claim=claim,
            submission=submission,
            evidence_chunks=chunks,
            builder_result=builder_result,
            base_knowledge=base_knowledge,
            target_knowledge=target_knowledge,
            alignment=alignment,
            failed_at=as_of,
            crash_hook=crash_hook,
        )
        if not result[2]:
            continue
        next_pending = result[0].get("pendingTransition")
        if (
            result[0]["phase"] == "awaiting-work"
            and isinstance(next_pending, dict)
            and next_pending["claimDigest"] is None
        ):
            return result[0]
