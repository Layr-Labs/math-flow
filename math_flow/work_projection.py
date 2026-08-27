from __future__ import annotations

import copy
import json
import re
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import Callable, Protocol

from .artifacts import ArtifactBundle, sha256_bytes, verify_bundle
from .counterfactual_context import (
    assemble_with_access_evidence,
    build_counterfactual_safe_facts,
    build_impact_subgraph_context,
    build_no_access_stage_input,
    build_with_access_stage_input,
    reconstruct_submission_evidence,
    validate_counterfactual_safe_facts,
    validate_impact_subgraph_context,
    validate_no_access_stage_input,
    validate_submission_evidence_manifest,
    validate_with_access_stage_input,
)
from .errors import MathFlowError
from .repository import sha256_json
from .research_topology import (
    derive_research_topology_alignment,
    validate_research_program_state_versioned,
    validate_research_topology_alignment,
)
from .work_accounting import (
    bind_patch_to_state,
    make_work_accounting_patch,
    materialize_submission_work_value,
    validate_root_contract,
    validate_submission_work_value,
    validate_work_accounting_patch,
    validate_work_accounting_state,
)


DIGEST = re.compile(r"^sha256:[0-9a-f]{64}$")
GIT_SHA = re.compile(r"^[0-9a-f]{40}$")
STAGES = ("safe-facts", "no-access", "with-access")
PROFILE = "math-flow/work-accounting-transition-v1"

REQUEST_FIELDS = {
    "schemaVersion",
    "profile",
    "stage",
    "problemId",
    "subjectTransactionId",
    "bindings",
    "rootContract",
    "baseAccountingState",
    "topologyAlignmentRef",
    "requiredPrimitiveUpdates",
    "stageInput",
    "requestDigest",
}
BINDING_FIELDS = {
    "rootContractDigest",
    "baseAccountingStateDigest",
    "baseKnowledgeStateDigest",
    "targetKnowledgeStateDigest",
    "topologyAlignmentDigest",
    "submissionEvidenceManifestDigest",
    "submissionDigest",
    "acceptedClaimRefsDigest",
}
REQUIRED_UPDATE_FIELDS = {"nodeRef", "requiredChanges", "reasons"}
PATCH_RESPONSE_FIELDS = {"updates"}
PATCH_UPDATE_INPUT_FIELDS = {"nodeRef", "changes", "rationale", "evidenceRefs"}

MANIFEST_FIELDS = {
    "protocolVersion",
    "runKind",
    "outputProfile",
    "problemId",
    "subjectTransactionId",
    "rootContractDigest",
    "baseAccountingStateDigest",
    "baseKnowledgeStateDigest",
    "targetKnowledgeStateDigest",
    "topologyAlignmentDigest",
    "submissionEvidenceManifestDigest",
    "submissionDigest",
    "acceptedClaimRefsDigest",
    "safeFactsDigest",
    "impactContextDigest",
    "requestDigests",
    "responseDigests",
    "noAccessPatchDigest",
    "withAccessPatchDigest",
    "noAccessStateDigest",
    "withAccessStateDigest",
    "evaluationDigest",
    "artifacts",
}
ARTIFACT_FIELDS = {"path", "role", "mediaType", "digest", "bytes"}

UNIQUE_ARTIFACT_ROLES = {
    "work-root-contract": "input/root-contract.json",
    "work-base-knowledge-state": "input/base-knowledge-state.json",
    "work-target-knowledge-state": "input/target-knowledge-state.json",
    "work-base-accounting-state": "input/base-accounting-state.json",
    "work-topology-alignment": "input/topology-alignment.json",
    "submission-evidence-manifest": "input/evidence/manifest.json",
    "safe-facts-request": "stages/safe-facts/request.json",
    "safe-facts-response": "stages/safe-facts/response.json",
    "counterfactual-safe-facts": "context/safe-facts.json",
    "work-impact-context": "context/impact-subgraph.json",
    "no-access-stage-input": "stages/no-access/input.json",
    "no-access-request": "stages/no-access/request.json",
    "no-access-response": "stages/no-access/response.json",
    "no-access-work-patch": "state/no-access-patch.json",
    "no-access-work-state": "state/no-access-state.json",
    "with-access-stage-input": "stages/with-access/input.json",
    "with-access-request": "stages/with-access/request.json",
    "with-access-response": "stages/with-access/response.json",
    "with-access-work-patch": "state/with-access-patch.json",
    "with-access-work-state": "state/with-access-state.json",
    "submission-work-evaluation": "evaluation.json",
}


@dataclass(frozen=True)
class SubmissionEvidenceFile:
    """One verified file made available outside the JSON provider request."""

    path: str
    digest: str
    content: bytes


class WorkProjectionProvider(Protocol):
    """Provider-neutral boundary for the three governed estimation stages."""

    def __call__(
        self,
        *,
        stage: str,
        request: Mapping[str, object],
        evidence_files: Sequence[SubmissionEvidenceFile],
    ) -> object: ...


def _object_digest(value: object) -> str:
    try:
        return f"sha256:{sha256_json(value)}"
    except (TypeError, ValueError) as exc:
        raise MathFlowError("work projection value must be canonical JSON data") from exc


def _without_digest(value: Mapping[str, object], field: str) -> dict[str, object]:
    return {key: copy.deepcopy(item) for key, item in value.items() if key != field}


def _require_digest(value: object, label: str) -> str:
    if not isinstance(value, str) or not DIGEST.fullmatch(value):
        raise MathFlowError(f"{label} must be a sha256 digest")
    return value


def _require_transaction(value: object, label: str) -> str:
    if not isinstance(value, str) or not GIT_SHA.fullmatch(value):
        raise MathFlowError(f"{label} must be a canonical transaction ID")
    return value


def _node_ref(value: object, label: str) -> dict[str, str]:
    if not isinstance(value, dict) or set(value) != {"kind", "id"}:
        raise MathFlowError(f"{label} has invalid fields")
    kind = value.get("kind")
    node_id = value.get("id")
    if kind not in {"program", "thread"} or not isinstance(node_id, str):
        raise MathFlowError(f"{label} must identify a program or thread")
    return {"kind": str(kind), "id": node_id}


def _node_key(value: object, label: str = "node reference") -> tuple[str, str]:
    ref = _node_ref(value, label)
    return ref["kind"], ref["id"]


def _json_bytes(value: object) -> bytes:
    try:
        return (json.dumps(value, indent=2, ensure_ascii=False) + "\n").encode("utf-8")
    except (TypeError, ValueError) as exc:
        raise MathFlowError("provider output must be finite canonical JSON data") from exc


def _json_artifact(raw: bytes, label: str) -> object:
    try:
        return json.loads(raw)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise MathFlowError(f"{label} is not valid UTF-8 JSON") from exc


def _assert_no_access_evidence_nonleakage(
    request: Mapping[str, object], evidence_files: Sequence[SubmissionEvidenceFile]
) -> None:
    """Enforce the byte-level half of the epistemic firewall.

    Safe-fact extraction owns the harder semantic judgment. This guard ensures
    that later composition cannot accidentally reintroduce a raw evidence span.
    """

    # Identity fields, the immutable root contract, claim keys, and builder node
    # IDs are independently governed bindings and may legitimately be printed
    # in the manifested submission. Scan only provider-authored prose. The same
    # prose was checked when safe facts were built; this second check protects
    # the later request-composition boundary.
    stage_input = request.get("stageInput")
    safe_facts = (
        stage_input.get("safeFacts") if isinstance(stage_input, dict) else None
    )
    facts = safe_facts.get("facts") if isinstance(safe_facts, dict) else None
    assumptions = (
        safe_facts.get("assumptions") if isinstance(safe_facts, dict) else None
    )
    rendered = _json_bytes(
        {
            "factConditions": [
                item.get("condition")
                for item in facts
                if isinstance(item, dict)
            ]
            if isinstance(facts, list)
            else [],
            "assumptions": assumptions if isinstance(assumptions, list) else [],
        }
    )
    window = 32
    rendered_windows = {
        rendered[offset : offset + window]
        for offset in range(max(0, len(rendered) - window + 1))
    }
    for evidence in evidence_files:
        content = evidence.content
        if len(content) >= window:
            if any(
                content[offset : offset + window] in rendered_windows
                for offset in range(len(content) - window + 1)
            ):
                raise MathFlowError("no-access request contains raw submission evidence")
        elif len(content) >= 16 and content in rendered:
            raise MathFlowError("no-access request contains a raw submission artifact")

    prohibited_keys = {
        "evidenceManifest",
        "verifiedChunkDigests",
        "verifiedFileCount",
        "verifiedTotalBytes",
    }

    def visit(value: object) -> None:
        if isinstance(value, dict):
            if prohibited_keys & set(value):
                raise MathFlowError("no-access request crosses the evidence firewall")
            for item in value.values():
                visit(item)
        elif isinstance(value, list):
            for item in value:
                visit(item)

    visit(request)


def _accepted_claim_refs_digest(refs: object) -> str:
    return _object_digest(refs)


def _validate_transition(
    *,
    subject_transaction_id: str,
    root_contract: object,
    base_knowledge_state: object,
    target_knowledge_state: object,
    base_accounting_state: object,
    topology_alignment: object | None,
    evidence_manifest: object,
    evidence_chunks: Mapping[str, bytes],
    accepted_claim_refs: object,
) -> tuple[
    str,
    dict[str, object],
    dict[str, object],
    dict[str, object],
    dict[str, object],
    dict[str, object],
    dict[str, bytes],
    list[dict[str, object]],
]:
    subject = _require_transaction(subject_transaction_id, "work projection subject")
    contract = validate_root_contract(root_contract)
    problem = str(contract["problemId"])
    before = validate_research_program_state_versioned(base_knowledge_state, problem)
    after = validate_research_program_state_versioned(target_knowledge_state, problem)
    base = validate_work_accounting_state(base_accounting_state, before, contract)
    expected_alignment = derive_research_topology_alignment(before, after)
    if topology_alignment is None:
        alignment = expected_alignment
    else:
        alignment = validate_research_topology_alignment(
            topology_alignment, before, after
        )
    if alignment != expected_alignment:
        raise MathFlowError("work projection topology alignment is not deterministic")

    before_contributions = set(before["contributions"])
    after_contributions = set(after["contributions"])
    if after_contributions - before_contributions != {subject}:
        raise MathFlowError(
            "work projection transition must add exactly its one subject submission"
        )
    if before_contributions - after_contributions:
        raise MathFlowError("work projection transition may not remove accepted submissions")
    if any(
        before["contributions"][transaction_id]
        != after["contributions"][transaction_id]
        for transaction_id in before_contributions
    ):
        raise MathFlowError(
            "work projection transition may not rewrite a prior accepted submission"
        )
    if set(base["processedSubmissionIds"]) != before_contributions:
        raise MathFlowError(
            "work projection base must have processed every prior accepted submission"
        )
    if subject in base["processedSubmissionIds"]:
        raise MathFlowError("work projection subject has already been processed")

    manifest = validate_submission_evidence_manifest(evidence_manifest)
    if manifest["problemId"] != problem or manifest["subjectTransactionId"] != subject:
        raise MathFlowError("work projection evidence belongs to another subject")
    chunks = dict(evidence_chunks)
    reconstruct_submission_evidence(manifest, chunks)

    if not isinstance(accepted_claim_refs, list) or not accepted_claim_refs:
        raise MathFlowError("work projection requires accepted claim identities")
    claims = copy.deepcopy(accepted_claim_refs)
    claim_keys: list[str] = []
    for claim in claims:
        if (
            not isinstance(claim, dict)
            or set(claim)
            != {"transactionId", "claimKey", "judgmentId", "assessmentDigest"}
            or claim.get("transactionId") != subject
        ):
            raise MathFlowError("work projection accepted claim identity is invalid")
        claim_key = claim.get("claimKey")
        if not isinstance(claim_key, str) or not claim_key:
            raise MathFlowError("work projection accepted claim key is invalid")
        _require_digest(claim.get("judgmentId"), "validity judgment ID")
        _require_digest(claim.get("assessmentDigest"), "validity assessment digest")
        claim_keys.append(claim_key)
    canonical_claims = sorted(
        claims,
        key=lambda item: (
            str(item["claimKey"]),
            str(item["judgmentId"]),
            str(item["assessmentDigest"]),
        ),
    )
    if claims != canonical_claims or len(claim_keys) != len(set(claim_keys)):
        raise MathFlowError("work projection accepted claim identities are not canonical")
    contribution = after["contributions"][subject]
    if set(claim_keys) != set(contribution["claimKeys"]):
        raise MathFlowError(
            "work projection claim identities do not match the accepted contribution"
        )
    return subject, contract, before, after, base, alignment, chunks, claims


def _required_primitive_updates(
    before: Mapping[str, object],
    after: Mapping[str, object],
    base_accounting_state: Mapping[str, object],
    *,
    evaluation_mode: str,
) -> list[dict[str, object]]:
    if evaluation_mode not in {"no-access", "with-access"}:
        raise MathFlowError("primitive updates require a counterfactual evaluation mode")
    base_annotations = {
        _node_key(item["nodeRef"]): item for item in base_accounting_state["annotations"]
    }
    requirements: dict[tuple[str, str], tuple[set[str], set[str]]] = {}

    def add(key: tuple[str, str], changes: Sequence[str], reason: str) -> None:
        existing = requirements.setdefault(key, (set(), set()))
        existing[0].update(changes)
        existing[1].add(reason)

    for kind, collection_name in (("program", "programs"), ("thread", "threads")):
        before_nodes = before[collection_name]
        after_nodes = after[collection_name]
        assert isinstance(before_nodes, dict) and isinstance(after_nodes, dict)
        for node_id, record in after_nodes.items():
            assert isinstance(record, dict)
            key = (kind, str(node_id))
            old = before_nodes.get(node_id)
            if old is None:
                add(key, ("directWorkHours", "conditionalIncidence"), "created")
            else:
                assert isinstance(old, dict)
                old_parent = old.get("parentId") if kind == "program" else old.get("programId")
                new_parent = (
                    record.get("parentId")
                    if kind == "program"
                    else record.get("programId")
                )
                if old_parent != new_parent:
                    add(key, ("conditionalIncidence",), "reparented")
            if (
                evaluation_mode == "with-access"
                and record.get("status") in {"completed", "retired"}
            ):
                annotation = base_annotations.get(key)
                if annotation is not None:
                    changes = []
                    if annotation.get("directWorkHours") != "0":
                        changes.append("directWorkHours")
                    if key != ("program", str(after["rootProgramId"])) and annotation.get(
                        "conditionalIncidence"
                    ) != "0":
                        changes.append("conditionalIncidence")
                    if changes:
                        add(key, changes, "inactive-zeroing")

    root_key = ("program", str(after["rootProgramId"]))
    if root_key in requirements:
        requirements[root_key][0].discard("conditionalIncidence")
    return [
        {
            "nodeRef": {"kind": key[0], "id": key[1]},
            "requiredChanges": sorted(changes),
            "reasons": sorted(reasons),
        }
        for key, (changes, reasons) in sorted(requirements.items())
        if changes
    ]


def _bindings(
    *,
    contract: Mapping[str, object],
    base: Mapping[str, object],
    before: Mapping[str, object],
    after: Mapping[str, object],
    alignment: Mapping[str, object],
    manifest: Mapping[str, object],
    accepted_claim_refs: object,
) -> dict[str, object]:
    return {
        "rootContractDigest": contract["rootContractDigest"],
        "baseAccountingStateDigest": base["stateDigest"],
        "baseKnowledgeStateDigest": before["stateDigest"],
        "targetKnowledgeStateDigest": after["stateDigest"],
        "topologyAlignmentDigest": alignment["alignmentDigest"],
        "submissionEvidenceManifestDigest": manifest["manifestDigest"],
        "submissionDigest": manifest["submissionDigest"],
        "acceptedClaimRefsDigest": _accepted_claim_refs_digest(accepted_claim_refs),
    }


def _safe_fact_stage_input(
    *,
    accepted_claim_refs: object,
    target_knowledge_state: Mapping[str, object],
    evidence_manifest: Mapping[str, object],
) -> dict[str, object]:
    return {
        "acceptedClaimRefs": copy.deepcopy(accepted_claim_refs),
        "knowledgeStateDigest": target_knowledge_state["stateDigest"],
        "evidenceManifest": copy.deepcopy(evidence_manifest),
        "verifiedChunkDigests": sorted(
            {
                str(chunk["digest"])
                for record in evidence_manifest["files"]
                for chunk in record["chunks"]
            }
        ),
    }


def _make_request(
    *,
    stage: str,
    problem_id: str,
    subject_transaction_id: str,
    bindings: Mapping[str, object],
    root_contract: Mapping[str, object],
    base_accounting_state: Mapping[str, object],
    topology_alignment: Mapping[str, object],
    required_updates: Sequence[Mapping[str, object]],
    stage_input: object,
) -> dict[str, object]:
    core: dict[str, object] = {
        "schemaVersion": 1,
        "profile": PROFILE,
        "stage": stage,
        "problemId": problem_id,
        "subjectTransactionId": subject_transaction_id,
        "bindings": copy.deepcopy(bindings),
        "rootContract": copy.deepcopy(root_contract),
        "baseAccountingState": copy.deepcopy(base_accounting_state),
        "topologyAlignmentRef": {
            "alignmentDigest": topology_alignment["alignmentDigest"],
            "beforeKnowledgeStateDigest": topology_alignment[
                "beforeKnowledgeStateDigest"
            ],
            "afterKnowledgeStateDigest": topology_alignment[
                "afterKnowledgeStateDigest"
            ],
        },
        "requiredPrimitiveUpdates": copy.deepcopy(list(required_updates)),
        "stageInput": copy.deepcopy(stage_input),
    }
    result = {**core, "requestDigest": _object_digest(core)}
    return validate_work_projection_request(result)


def validate_work_projection_request(value: object) -> dict[str, object]:
    if not isinstance(value, dict) or set(value) != REQUEST_FIELDS:
        raise MathFlowError("work projection request has an invalid envelope")
    if value.get("schemaVersion") != 1 or value.get("profile") != PROFILE:
        raise MathFlowError("work projection request has an invalid version or profile")
    stage = value.get("stage")
    if stage not in STAGES:
        raise MathFlowError("work projection request has an invalid stage")
    _require_transaction(value.get("subjectTransactionId"), "work projection request subject")
    if not isinstance(value.get("problemId"), str) or not value["problemId"]:
        raise MathFlowError("work projection request problem ID is invalid")
    bindings = value.get("bindings")
    if not isinstance(bindings, dict) or set(bindings) != BINDING_FIELDS:
        raise MathFlowError("work projection request has invalid identity bindings")
    for field in BINDING_FIELDS:
        _require_digest(bindings.get(field), f"work projection {field}")
    contract = validate_root_contract(value.get("rootContract"), str(value["problemId"]))
    if contract["rootContractDigest"] != bindings["rootContractDigest"]:
        raise MathFlowError("work projection request root-contract binding mismatch")
    base = value.get("baseAccountingState")
    if (
        not isinstance(base, dict)
        or base.get("stateDigest") != bindings["baseAccountingStateDigest"]
    ):
        raise MathFlowError("work projection request base-accounting binding mismatch")
    if base.get("knowledgeStateDigest") != bindings["baseKnowledgeStateDigest"]:
        raise MathFlowError("work projection request base-knowledge binding mismatch")
    alignment = value.get("topologyAlignmentRef")
    if (
        not isinstance(alignment, dict)
        or set(alignment)
        != {
            "alignmentDigest",
            "beforeKnowledgeStateDigest",
            "afterKnowledgeStateDigest",
        }
        or alignment.get("alignmentDigest")
        != bindings["topologyAlignmentDigest"]
        or alignment.get("beforeKnowledgeStateDigest") != bindings["baseKnowledgeStateDigest"]
        or alignment.get("afterKnowledgeStateDigest") != bindings["targetKnowledgeStateDigest"]
    ):
        raise MathFlowError("work projection request topology binding mismatch")
    required = value.get("requiredPrimitiveUpdates")
    if not isinstance(required, list):
        raise MathFlowError("work projection required primitive updates must be an array")
    keys: list[tuple[str, str]] = []
    for item in required:
        if not isinstance(item, dict) or set(item) != REQUIRED_UPDATE_FIELDS:
            raise MathFlowError("work projection primitive requirement has invalid fields")
        keys.append(_node_key(item.get("nodeRef"), "required primitive node"))
        changes = item.get("requiredChanges")
        reasons = item.get("reasons")
        if (
            not isinstance(changes, list)
            or not changes
            or changes != sorted(set(changes))
            or not set(changes) <= {"directWorkHours", "conditionalIncidence"}
            or not isinstance(reasons, list)
            or not reasons
            or reasons != sorted(set(reasons))
            or not set(reasons) <= {"created", "reparented", "inactive-zeroing"}
        ):
            raise MathFlowError("work projection primitive requirement is not canonical")
    if keys != sorted(set(keys)):
        raise MathFlowError("work projection primitive requirements are not canonical")
    stage_input = value.get("stageInput")
    if stage == "safe-facts":
        if required:
            raise MathFlowError("safe-fact extraction may not request accounting patches")
        if not isinstance(stage_input, dict) or set(stage_input) != {
            "acceptedClaimRefs",
            "knowledgeStateDigest",
            "evidenceManifest",
            "verifiedChunkDigests",
        }:
            raise MathFlowError("safe-fact extraction input has invalid fields")
        manifest = validate_submission_evidence_manifest(stage_input["evidenceManifest"])
        if (
            manifest["manifestDigest"] != bindings["submissionEvidenceManifestDigest"]
            or manifest["submissionDigest"] != bindings["submissionDigest"]
            or stage_input["knowledgeStateDigest"] != bindings["targetKnowledgeStateDigest"]
            or _accepted_claim_refs_digest(stage_input["acceptedClaimRefs"])
            != bindings["acceptedClaimRefsDigest"]
        ):
            raise MathFlowError("safe-fact extraction input binding mismatch")
        expected_chunks = sorted(
            {
                str(chunk["digest"])
                for record in manifest["files"]
                for chunk in record["chunks"]
            }
        )
        if stage_input["verifiedChunkDigests"] != expected_chunks:
            raise MathFlowError("safe-fact extraction chunk binding is incomplete")
    elif stage == "no-access":
        validate_no_access_stage_input(stage_input)
    else:
        validate_with_access_stage_input(stage_input)
    if value.get("requestDigest") != _object_digest(_without_digest(value, "requestDigest")):
        raise MathFlowError("work projection request digest mismatch")
    return value


def _evidence_files(
    manifest: Mapping[str, object], chunks: Mapping[str, bytes]
) -> tuple[SubmissionEvidenceFile, ...]:
    files = reconstruct_submission_evidence(manifest, chunks)
    records = {str(item["path"]): item for item in manifest["files"]}
    return tuple(
        SubmissionEvidenceFile(
            path=path,
            digest=str(records[path]["digest"]),
            content=content,
        )
        for path, content in sorted(files.items())
    )


class WorkProjectionCheckpointStore:
    """Content-bound provider response cache for deterministic resume."""

    def __init__(self, checkpoint_dir: Path):
        self.checkpoint_dir = checkpoint_dir.resolve()
        self.checkpoint_dir.mkdir(parents=True, exist_ok=True)
        self.performed_calls = 0
        self.reused_calls = 0

    def call(
        self,
        provider: WorkProjectionProvider,
        *,
        stage: str,
        request: Mapping[str, object],
        evidence_files: Sequence[SubmissionEvidenceFile],
    ) -> object:
        validated_request = validate_work_projection_request(dict(request))
        request_digest = str(validated_request["requestDigest"])
        checkpoint = self.checkpoint_dir / f"{request_digest.removeprefix('sha256:')}.json"
        if checkpoint.is_symlink():
            raise MathFlowError("work projection provider checkpoint may not be a symlink")
        if checkpoint.is_file():
            try:
                envelope = json.loads(checkpoint.read_text(encoding="utf-8"))
            except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
                raise MathFlowError("work projection provider checkpoint is unreadable") from exc
            if (
                not isinstance(envelope, dict)
                or set(envelope)
                != {"schemaVersion", "stage", "requestDigest", "responseDigest", "response"}
                or envelope.get("schemaVersion") != 1
                or envelope.get("stage") != stage
                or envelope.get("requestDigest") != request_digest
                or envelope.get("responseDigest") != _object_digest(envelope.get("response"))
            ):
                raise MathFlowError("work projection provider checkpoint binding mismatch")
            self.reused_calls += 1
            return copy.deepcopy(envelope["response"])

        response = provider(
            stage=stage,
            request=copy.deepcopy(validated_request),
            evidence_files=tuple(evidence_files),
        )
        # A round trip both rejects non-JSON provider objects and isolates later mutation.
        response = _json_artifact(_json_bytes(response), "work projection provider response")
        envelope = {
            "schemaVersion": 1,
            "stage": stage,
            "requestDigest": request_digest,
            "responseDigest": _object_digest(response),
            "response": response,
        }
        temporary = checkpoint.with_suffix(".tmp")
        if temporary.is_symlink():
            raise MathFlowError("work projection temporary checkpoint may not be a symlink")
        temporary.write_bytes(_json_bytes(envelope))
        temporary.replace(checkpoint)
        self.performed_calls += 1
        return copy.deepcopy(response)

    def invalidate(
        self,
        *,
        stage: str,
        request: Mapping[str, object],
    ) -> None:
        """Remove a checkpoint rejected by downstream deterministic validation."""

        validated_request = validate_work_projection_request(dict(request))
        request_digest = str(validated_request["requestDigest"])
        checkpoint = self.checkpoint_dir / f"{request_digest.removeprefix('sha256:')}.json"
        if checkpoint.is_symlink():
            raise MathFlowError("work projection provider checkpoint may not be a symlink")
        if checkpoint.is_file():
            checkpoint.unlink()


def _invoke(
    provider: WorkProjectionProvider,
    checkpoint_store: WorkProjectionCheckpointStore | None,
    *,
    stage: str,
    request: Mapping[str, object],
    evidence_files: Sequence[SubmissionEvidenceFile],
    semantic_validate: Callable[[object], object] | None = None,
) -> object:
    validated_call = getattr(provider, "call_with_semantic_validation", None)

    def call_provider(
        *,
        stage: str,
        request: Mapping[str, object],
        evidence_files: Sequence[SubmissionEvidenceFile],
    ) -> object:
        if semantic_validate is not None and callable(validated_call):
            return validated_call(
                stage=stage,
                request=request,
                evidence_files=evidence_files,
                validate=semantic_validate,
            )
        response = provider(
            stage=stage,
            request=copy.deepcopy(request),
            evidence_files=tuple(evidence_files),
        )
        response = _json_artifact(
            _json_bytes(response), "work projection provider response"
        )
        if semantic_validate is not None:
            semantic_validate(response)
        return response

    try:
        response = (
            checkpoint_store.call(
                call_provider,
                stage=stage,
                request=request,
                evidence_files=evidence_files,
            )
            if checkpoint_store is not None
            else call_provider(
                stage=stage,
                request=request,
                evidence_files=evidence_files,
            )
        )
        if semantic_validate is not None:
            semantic_validate(response)
        return response
    except (MathFlowError, TypeError, ValueError):
        if checkpoint_store is not None:
            checkpoint_store.invalidate(stage=stage, request=request)
        raise


def _validate_patch_response(
    response: object,
    *,
    required_updates: Sequence[Mapping[str, object]],
    allowed_node_refs: set[tuple[str, str]],
) -> list[dict[str, object]]:
    if not isinstance(response, dict) or set(response) != PATCH_RESPONSE_FIELDS:
        raise MathFlowError("work projection patch response has an invalid envelope")
    updates = response.get("updates")
    if not isinstance(updates, list) or len(updates) > 512:
        raise MathFlowError("work projection patch response has invalid updates")
    update_map: dict[tuple[str, str], dict[str, object]] = {}
    for update in updates:
        if not isinstance(update, dict) or set(update) != PATCH_UPDATE_INPUT_FIELDS:
            raise MathFlowError("work projection patch response update has invalid fields")
        key = _node_key(update.get("nodeRef"), "work projection patch response node")
        if key in update_map or key not in allowed_node_refs:
            raise MathFlowError("work projection patch response escapes its impact context")
        rationale = update.get("rationale")
        evidence_refs = update.get("evidenceRefs")
        if (
            not isinstance(rationale, str)
            or not rationale.strip()
            or len(rationale.encode("utf-8")) > 16 * 1024
            or not isinstance(evidence_refs, list)
            or not evidence_refs
            or len(evidence_refs) > 128
            or any(
                not isinstance(item, str)
                or not item
                or len(item.encode("utf-8")) > 512
                for item in evidence_refs
            )
        ):
            raise MathFlowError("work projection patch response contains invalid audit text")
        update_map[key] = update
    for requirement in required_updates:
        key = _node_key(requirement["nodeRef"])
        update = update_map.get(key)
        changes = update.get("changes") if update is not None else None
        if not isinstance(changes, dict) or not set(requirement["requiredChanges"]) <= set(
            changes
        ):
            raise MathFlowError(
                "work projection patch omits a topology-required primitive estimate"
            )
    return copy.deepcopy(updates)


def _patch_from_response(
    response: object,
    *,
    mode: str,
    problem_id: str,
    subject_transaction_id: str,
    bindings: Mapping[str, object],
    base_accounting_state: Mapping[str, object],
    required_updates: Sequence[Mapping[str, object]],
    impact_context: Mapping[str, object],
) -> dict[str, object]:
    allowed = {
        _node_key(item["ref"])
        for item in impact_context["includedNodes"]
    }
    updates = _validate_patch_response(
        response,
        required_updates=required_updates,
        allowed_node_refs=allowed,
    )
    patch = make_work_accounting_patch(
        problem_id=problem_id,
        subject_transaction_id=subject_transaction_id,
        evaluation_mode=mode,
        root_contract_digest=str(bindings["rootContractDigest"]),
        base_accounting_state_digest=str(bindings["baseAccountingStateDigest"]),
        base_knowledge_state_digest=str(bindings["baseKnowledgeStateDigest"]),
        target_knowledge_state_digest=str(bindings["targetKnowledgeStateDigest"]),
        topology_alignment_digest=str(bindings["topologyAlignmentDigest"]),
        updates=updates,
    )
    return bind_patch_to_state(patch, base_accounting_state)


def _seed_refs_from_safe_facts(safe_facts: Mapping[str, object]) -> list[dict[str, str]]:
    by_key: dict[tuple[str, str], dict[str, str]] = {}
    for fact in safe_facts["facts"]:
        for ref in fact["affectedNodeRefs"]:
            by_key[_node_key(ref)] = copy.deepcopy(ref)
    return [by_key[key] for key in sorted(by_key)]


def _ensure_required_context_coverage(
    required_updates: Sequence[Mapping[str, object]],
    context: Mapping[str, object],
) -> None:
    included = {_node_key(item["ref"]) for item in context["includedNodes"]}
    missing = [
        _node_key(item["nodeRef"])
        for item in required_updates
        if _node_key(item["nodeRef"]) not in included
    ]
    if missing:
        raise MathFlowError(
            "counterfactual-safe facts do not cover a topology-required accounting node: "
            f"{missing[0][0]}/{missing[0][1]}"
        )


def _response_digest(stage: str, response: object) -> dict[str, str]:
    return {"stage": stage, "digest": _object_digest(response)}


def validate_work_projection_manifest(value: object) -> dict[str, object]:
    if not isinstance(value, dict) or set(value) != MANIFEST_FIELDS:
        raise MathFlowError("work projection bundle manifest has an invalid envelope")
    if (
        value.get("protocolVersion") != 1
        or value.get("runKind") != "work-accounting-evaluation"
        or value.get("outputProfile") != PROFILE
    ):
        raise MathFlowError("work projection bundle has an invalid protocol identity")
    _require_transaction(value.get("subjectTransactionId"), "work projection bundle subject")
    if not isinstance(value.get("problemId"), str) or not value["problemId"]:
        raise MathFlowError("work projection bundle problem ID is invalid")
    for field in MANIFEST_FIELDS - {
        "protocolVersion",
        "runKind",
        "outputProfile",
        "problemId",
        "subjectTransactionId",
        "requestDigests",
        "responseDigests",
        "artifacts",
    }:
        _require_digest(value.get(field), f"work projection bundle {field}")
    requests = value.get("requestDigests")
    if not isinstance(requests, list) or len(requests) != 3 or any(
        not isinstance(item, str) or not DIGEST.fullmatch(item) for item in requests
    ):
        raise MathFlowError("work projection bundle must bind three request digests")
    responses = value.get("responseDigests")
    if (
        not isinstance(responses, list)
        or [item.get("stage") if isinstance(item, dict) else None for item in responses]
        != list(STAGES)
    ):
        raise MathFlowError("work projection bundle response index is invalid")
    for item in responses:
        if not isinstance(item, dict) or set(item) != {"stage", "digest"}:
            raise MathFlowError("work projection bundle response binding is invalid")
        _require_digest(item.get("digest"), "work projection response digest")
    artifacts = value.get("artifacts")
    if not isinstance(artifacts, list) or any(not isinstance(item, dict) for item in artifacts):
        raise MathFlowError("work projection bundle artifact index is invalid")
    paths: list[str] = []
    for artifact in artifacts:
        if set(artifact) != ARTIFACT_FIELDS:
            raise MathFlowError("work projection artifact entry has invalid fields")
        path = artifact.get("path")
        if not isinstance(path, str) or not path:
            raise MathFlowError("work projection artifact path is invalid")
        paths.append(path)
        _require_digest(artifact.get("digest"), "work projection artifact digest")
        if (
            not isinstance(artifact.get("role"), str)
            or not artifact["role"]
            or not isinstance(artifact.get("mediaType"), str)
            or not artifact["mediaType"]
            or isinstance(artifact.get("bytes"), bool)
            or not isinstance(artifact["bytes"], int)
            or artifact["bytes"] < 0
        ):
            raise MathFlowError("work projection artifact entry is invalid")
    if paths != sorted(set(paths)):
        raise MathFlowError("work projection artifact paths are not canonical")
    roles = [str(item.get("role")) for item in artifacts]
    for role in UNIQUE_ARTIFACT_ROLES:
        if roles.count(role) != 1:
            raise MathFlowError(f"work projection bundle must contain one {role} artifact")
    allowed_roles = set(UNIQUE_ARTIFACT_ROLES) | {"submission-evidence-chunk"}
    if any(role not in allowed_roles for role in roles):
        raise MathFlowError("work projection bundle contains an unexpected artifact role")
    return value


def run_work_projection_bundle(
    *,
    output_dir: Path,
    provider: WorkProjectionProvider,
    subject_transaction_id: str,
    root_contract: object,
    base_knowledge_state: object,
    target_knowledge_state: object,
    base_accounting_state: object,
    topology_alignment: object | None,
    evidence_manifest: object,
    evidence_chunks: Mapping[str, bytes],
    accepted_claim_refs: object,
    checkpoint_dir: Path | None = None,
    descendant_depth: int = 1,
) -> dict[str, object]:
    """Run one inactive V1 work transition and materialize its immutable bundle."""

    (
        subject,
        contract,
        before,
        after,
        base,
        alignment,
        chunks,
        claims,
    ) = _validate_transition(
        subject_transaction_id=subject_transaction_id,
        root_contract=root_contract,
        base_knowledge_state=base_knowledge_state,
        target_knowledge_state=target_knowledge_state,
        base_accounting_state=base_accounting_state,
        topology_alignment=topology_alignment,
        evidence_manifest=evidence_manifest,
        evidence_chunks=evidence_chunks,
        accepted_claim_refs=accepted_claim_refs,
    )
    manifest = validate_submission_evidence_manifest(evidence_manifest)
    bindings = _bindings(
        contract=contract,
        base=base,
        before=before,
        after=after,
        alignment=alignment,
        manifest=manifest,
        accepted_claim_refs=claims,
    )
    no_access_required_updates = _required_primitive_updates(
        before,
        after,
        base,
        evaluation_mode="no-access",
    )
    with_access_required_updates = _required_primitive_updates(
        before,
        after,
        base,
        evaluation_mode="with-access",
    )
    verified_files = _evidence_files(manifest, chunks)
    checkpoint = (
        WorkProjectionCheckpointStore(checkpoint_dir)
        if checkpoint_dir is not None
        else None
    )

    safe_request = _make_request(
        stage="safe-facts",
        problem_id=str(contract["problemId"]),
        subject_transaction_id=subject,
        bindings=bindings,
        root_contract=contract,
        base_accounting_state=base,
        topology_alignment=alignment,
        required_updates=[],
        stage_input=_safe_fact_stage_input(
            accepted_claim_refs=claims,
            target_knowledge_state=after,
            evidence_manifest=manifest,
        ),
    )
    def validate_safe_response(response: object) -> dict[str, object]:
        safe = build_counterfactual_safe_facts(
            problem_id=str(contract["problemId"]),
            subject_transaction_id=subject,
            accepted_claim_refs=claims,
            research_state=after,
            evidence_manifest=manifest,
            evidence_chunks=chunks,
            extracted=response,
        )
        safe_context = build_impact_subgraph_context(
            problem_id=str(contract["problemId"]),
            subject_transaction_id=subject,
            accepted_claim_refs=claims,
            research_state=after,
            seed_node_refs=_seed_refs_from_safe_facts(safe),
            descendant_depth=descendant_depth,
        )
        _ensure_required_context_coverage(no_access_required_updates, safe_context)
        _ensure_required_context_coverage(with_access_required_updates, safe_context)
        return safe

    safe_response = _invoke(
        provider,
        checkpoint,
        stage="safe-facts",
        request=safe_request,
        evidence_files=verified_files,
        semantic_validate=validate_safe_response,
    )
    safe_facts = validate_safe_response(safe_response)
    context = build_impact_subgraph_context(
        problem_id=str(contract["problemId"]),
        subject_transaction_id=subject,
        accepted_claim_refs=claims,
        research_state=after,
        seed_node_refs=_seed_refs_from_safe_facts(safe_facts),
        descendant_depth=descendant_depth,
    )
    _ensure_required_context_coverage(no_access_required_updates, context)
    _ensure_required_context_coverage(with_access_required_updates, context)

    no_input = build_no_access_stage_input(
        safe_facts=safe_facts,
        impact_context=context,
        research_state=after,
    )
    no_request = _make_request(
        stage="no-access",
        problem_id=str(contract["problemId"]),
        subject_transaction_id=subject,
        bindings=bindings,
        root_contract=contract,
        base_accounting_state=base,
        topology_alignment=alignment,
        required_updates=no_access_required_updates,
        stage_input=no_input,
    )
    _assert_no_access_evidence_nonleakage(no_request, verified_files)
    def validate_no_access_response(response: object) -> dict[str, object]:
        return _patch_from_response(
            response,
            mode="no-access",
            problem_id=str(contract["problemId"]),
            subject_transaction_id=subject,
            bindings=bindings,
            base_accounting_state=base,
            required_updates=no_access_required_updates,
            impact_context=context,
        )

    no_response = _invoke(
        provider,
        checkpoint,
        stage="no-access",
        request=no_request,
        evidence_files=(),
        semantic_validate=validate_no_access_response,
    )
    no_patch = validate_no_access_response(no_response)

    with_input = build_with_access_stage_input(
        safe_facts=safe_facts,
        impact_context=context,
        research_state=after,
        evidence_manifest=manifest,
        evidence_chunks=chunks,
    )
    # This is also a fail-closed completeness check on the exact stage binding.
    assembled = assemble_with_access_evidence(with_input, chunks)
    with_files = tuple(
        SubmissionEvidenceFile(
            path=str(item["path"]),
            digest=str(item["digest"]),
            content=bytes(item["content"]),
        )
        for item in assembled
    )
    with_request = _make_request(
        stage="with-access",
        problem_id=str(contract["problemId"]),
        subject_transaction_id=subject,
        bindings=bindings,
        root_contract=contract,
        base_accounting_state=base,
        topology_alignment=alignment,
        required_updates=with_access_required_updates,
        stage_input=with_input,
    )
    def validate_with_access_response(response: object) -> dict[str, object]:
        candidate = _patch_from_response(
            response,
            mode="with-access",
            problem_id=str(contract["problemId"]),
            subject_transaction_id=subject,
            bindings=bindings,
            base_accounting_state=base,
            required_updates=with_access_required_updates,
            impact_context=context,
        )
        materialize_submission_work_value(
            base_state=base,
            no_access_patch=no_patch,
            with_access_patch=candidate,
            root_contract=contract,
            base_knowledge_state=before,
            target_knowledge_state=after,
            topology_alignment=alignment,
        )
        return candidate

    with_response = _invoke(
        provider,
        checkpoint,
        stage="with-access",
        request=with_request,
        evidence_files=with_files,
        semantic_validate=validate_with_access_response,
    )
    with_patch = validate_with_access_response(with_response)
    no_state, with_state, evaluation = materialize_submission_work_value(
        base_state=base,
        no_access_patch=no_patch,
        with_access_patch=with_patch,
        root_contract=contract,
        base_knowledge_state=before,
        target_knowledge_state=after,
        topology_alignment=alignment,
    )

    bundle = ArtifactBundle(output_dir)
    bundle.add_json(UNIQUE_ARTIFACT_ROLES["work-root-contract"], contract, "work-root-contract")
    bundle.add_json(
        UNIQUE_ARTIFACT_ROLES["work-base-knowledge-state"],
        before,
        "work-base-knowledge-state",
    )
    bundle.add_json(
        UNIQUE_ARTIFACT_ROLES["work-target-knowledge-state"],
        after,
        "work-target-knowledge-state",
    )
    bundle.add_json(
        UNIQUE_ARTIFACT_ROLES["work-base-accounting-state"],
        base,
        "work-base-accounting-state",
    )
    bundle.add_json(
        UNIQUE_ARTIFACT_ROLES["work-topology-alignment"],
        alignment,
        "work-topology-alignment",
    )
    bundle.add_json(
        UNIQUE_ARTIFACT_ROLES["submission-evidence-manifest"],
        manifest,
        "submission-evidence-manifest",
    )
    for digest, content in sorted(chunks.items()):
        bundle.add_bytes(
            f"input/evidence/chunks/{digest.removeprefix('sha256:')}.bin",
            content,
            "submission-evidence-chunk",
            "application/octet-stream",
        )
    for path, value, role in (
        (UNIQUE_ARTIFACT_ROLES["safe-facts-request"], safe_request, "safe-facts-request"),
        (UNIQUE_ARTIFACT_ROLES["safe-facts-response"], safe_response, "safe-facts-response"),
        (
            UNIQUE_ARTIFACT_ROLES["counterfactual-safe-facts"],
            safe_facts,
            "counterfactual-safe-facts",
        ),
        (UNIQUE_ARTIFACT_ROLES["work-impact-context"], context, "work-impact-context"),
        (UNIQUE_ARTIFACT_ROLES["no-access-stage-input"], no_input, "no-access-stage-input"),
        (UNIQUE_ARTIFACT_ROLES["no-access-request"], no_request, "no-access-request"),
        (UNIQUE_ARTIFACT_ROLES["no-access-response"], no_response, "no-access-response"),
        (UNIQUE_ARTIFACT_ROLES["no-access-work-patch"], no_patch, "no-access-work-patch"),
        (UNIQUE_ARTIFACT_ROLES["no-access-work-state"], no_state, "no-access-work-state"),
        (UNIQUE_ARTIFACT_ROLES["with-access-stage-input"], with_input, "with-access-stage-input"),
        (UNIQUE_ARTIFACT_ROLES["with-access-request"], with_request, "with-access-request"),
        (UNIQUE_ARTIFACT_ROLES["with-access-response"], with_response, "with-access-response"),
        (UNIQUE_ARTIFACT_ROLES["with-access-work-patch"], with_patch, "with-access-work-patch"),
        (UNIQUE_ARTIFACT_ROLES["with-access-work-state"], with_state, "with-access-work-state"),
        (
            UNIQUE_ARTIFACT_ROLES["submission-work-evaluation"],
            evaluation,
            "submission-work-evaluation",
        ),
    ):
        bundle.add_json(path, value, role)
    envelope: dict[str, object] = {
        "protocolVersion": 1,
        "runKind": "work-accounting-evaluation",
        "outputProfile": PROFILE,
        "problemId": contract["problemId"],
        "subjectTransactionId": subject,
        **bindings,
        "safeFactsDigest": safe_facts["safeFactsDigest"],
        "impactContextDigest": context["contextDigest"],
        "requestDigests": [
            safe_request["requestDigest"],
            no_request["requestDigest"],
            with_request["requestDigest"],
        ],
        "responseDigests": [
            _response_digest("safe-facts", safe_response),
            _response_digest("no-access", no_response),
            _response_digest("with-access", with_response),
        ],
        "noAccessPatchDigest": no_patch["patchDigest"],
        "withAccessPatchDigest": with_patch["patchDigest"],
        "noAccessStateDigest": no_state["stateDigest"],
        "withAccessStateDigest": with_state["stateDigest"],
        "evaluationDigest": evaluation["evaluationDigest"],
    }
    result = bundle.finalize(envelope)
    validate_work_projection_manifest(result)
    return result


def _artifact_entry(
    manifest: Mapping[str, object], role: str
) -> Mapping[str, object]:
    matches = [item for item in manifest["artifacts"] if item.get("role") == role]
    if len(matches) != 1:
        raise MathFlowError(f"work projection bundle must contain one {role} artifact")
    return matches[0]


def _read_entry(bundle_dir: Path, entry: Mapping[str, object]) -> bytes:
    relative = PurePosixPath(str(entry.get("path", "")))
    if relative.is_absolute() or not relative.parts or ".." in relative.parts:
        raise MathFlowError("work projection bundle contains an unsafe artifact path")
    target = bundle_dir.resolve().joinpath(*relative.parts).resolve()
    try:
        target.relative_to(bundle_dir.resolve())
    except ValueError as exc:
        raise MathFlowError("work projection artifact escapes its bundle") from exc
    return target.read_bytes()


def _load_json_role(
    bundle_dir: Path, manifest: Mapping[str, object], role: str
) -> object:
    return _json_artifact(_read_entry(bundle_dir, _artifact_entry(manifest, role)), role)


def load_work_projection_bundle(
    bundle_dir: Path, *, expected_bundle_digest: str | None = None
) -> dict[str, object]:
    """Verify and deterministically replay all semantic bindings in a bundle."""

    manifest, bundle_digest = verify_bundle(bundle_dir)
    validate_work_projection_manifest(manifest)
    if expected_bundle_digest is not None:
        _require_digest(expected_bundle_digest, "expected work projection bundle digest")
        if bundle_digest != expected_bundle_digest:
            raise MathFlowError("work projection bundle does not match its content address")
    for role, expected_path in UNIQUE_ARTIFACT_ROLES.items():
        entry = _artifact_entry(manifest, role)
        if entry.get("path") != expected_path:
            raise MathFlowError(f"work projection {role} artifact has a noncanonical path")

    contract = _load_json_role(bundle_dir, manifest, "work-root-contract")
    before = _load_json_role(bundle_dir, manifest, "work-base-knowledge-state")
    after = _load_json_role(bundle_dir, manifest, "work-target-knowledge-state")
    base = _load_json_role(bundle_dir, manifest, "work-base-accounting-state")
    alignment = _load_json_role(bundle_dir, manifest, "work-topology-alignment")
    evidence_manifest = _load_json_role(bundle_dir, manifest, "submission-evidence-manifest")

    chunks: dict[str, bytes] = {}
    for entry in manifest["artifacts"]:
        if entry.get("role") != "submission-evidence-chunk":
            continue
        digest = str(entry.get("digest"))
        expected_path = f"input/evidence/chunks/{digest.removeprefix('sha256:')}.bin"
        if entry.get("path") != expected_path or digest in chunks:
            raise MathFlowError("work projection evidence chunk artifact is not canonical")
        chunks[digest] = _read_entry(bundle_dir, entry)

    safe_request = _load_json_role(bundle_dir, manifest, "safe-facts-request")
    validated_safe_request = validate_work_projection_request(safe_request)
    safe_stage_input = validated_safe_request["stageInput"]
    assert isinstance(safe_stage_input, dict)
    subject, contract, before, after, base, alignment, chunks, claims = _validate_transition(
        subject_transaction_id=str(manifest["subjectTransactionId"]),
        root_contract=contract,
        base_knowledge_state=before,
        target_knowledge_state=after,
        base_accounting_state=base,
        topology_alignment=alignment,
        evidence_manifest=evidence_manifest,
        evidence_chunks=chunks,
        accepted_claim_refs=safe_stage_input["acceptedClaimRefs"],
    )
    bindings = _bindings(
        contract=contract,
        base=base,
        before=before,
        after=after,
        alignment=alignment,
        manifest=evidence_manifest,
        accepted_claim_refs=claims,
    )
    for field, expected in bindings.items():
        if manifest.get(field) != expected:
            raise MathFlowError(f"work projection bundle {field} binding mismatch")
    no_access_required_updates = _required_primitive_updates(
        before,
        after,
        base,
        evaluation_mode="no-access",
    )
    with_access_required_updates = _required_primitive_updates(
        before,
        after,
        base,
        evaluation_mode="with-access",
    )

    safe_response = _load_json_role(bundle_dir, manifest, "safe-facts-response")
    safe_facts = _load_json_role(bundle_dir, manifest, "counterfactual-safe-facts")
    expected_safe_request = _make_request(
        stage="safe-facts",
        problem_id=str(contract["problemId"]),
        subject_transaction_id=subject,
        bindings=bindings,
        root_contract=contract,
        base_accounting_state=base,
        topology_alignment=alignment,
        required_updates=[],
        stage_input=_safe_fact_stage_input(
            accepted_claim_refs=claims,
            target_knowledge_state=after,
            evidence_manifest=evidence_manifest,
        ),
    )
    if safe_request != expected_safe_request:
        raise MathFlowError("work projection safe-fact request is not reproducible")
    rebuilt_safe = build_counterfactual_safe_facts(
        problem_id=str(contract["problemId"]),
        subject_transaction_id=subject,
        accepted_claim_refs=claims,
        research_state=after,
        evidence_manifest=evidence_manifest,
        evidence_chunks=chunks,
        extracted=safe_response,
    )
    if safe_facts != rebuilt_safe:
        raise MathFlowError("work projection safe-fact artifact does not match its response")
    context = _load_json_role(bundle_dir, manifest, "work-impact-context")
    rebuilt_context = build_impact_subgraph_context(
        problem_id=str(contract["problemId"]),
        subject_transaction_id=subject,
        accepted_claim_refs=claims,
        research_state=after,
        seed_node_refs=_seed_refs_from_safe_facts(safe_facts),
        descendant_depth=int(context["descendantDepth"]),
    )
    if context != rebuilt_context:
        raise MathFlowError("work projection impact context is not reproducible")
    _ensure_required_context_coverage(no_access_required_updates, context)
    _ensure_required_context_coverage(with_access_required_updates, context)

    no_input = _load_json_role(bundle_dir, manifest, "no-access-stage-input")
    expected_no_input = build_no_access_stage_input(
        safe_facts=safe_facts, impact_context=context, research_state=after
    )
    if no_input != expected_no_input:
        raise MathFlowError("work projection no-access input is not reproducible")
    no_request = _load_json_role(bundle_dir, manifest, "no-access-request")
    expected_no_request = _make_request(
        stage="no-access",
        problem_id=str(contract["problemId"]),
        subject_transaction_id=subject,
        bindings=bindings,
        root_contract=contract,
        base_accounting_state=base,
        topology_alignment=alignment,
        required_updates=no_access_required_updates,
        stage_input=no_input,
    )
    if no_request != expected_no_request:
        # Bundles produced before inactive-node counterfactuals were repaired
        # required completed/retired zeroing in both branches.  Keep those
        # immutable bundles replayable while new runs use mode-aware rules.
        legacy_no_request = _make_request(
            stage="no-access",
            problem_id=str(contract["problemId"]),
            subject_transaction_id=subject,
            bindings=bindings,
            root_contract=contract,
            base_accounting_state=base,
            topology_alignment=alignment,
            required_updates=with_access_required_updates,
            stage_input=no_input,
        )
        if no_request != legacy_no_request:
            raise MathFlowError("work projection no-access request is not reproducible")
        effective_no_access_required_updates = with_access_required_updates
    else:
        effective_no_access_required_updates = no_access_required_updates
    _assert_no_access_evidence_nonleakage(
        no_request, _evidence_files(evidence_manifest, chunks)
    )
    no_response = _load_json_role(bundle_dir, manifest, "no-access-response")
    no_patch = _load_json_role(bundle_dir, manifest, "no-access-work-patch")
    rebuilt_no_patch = _patch_from_response(
        no_response,
        mode="no-access",
        problem_id=str(contract["problemId"]),
        subject_transaction_id=subject,
        bindings=bindings,
        base_accounting_state=base,
        required_updates=effective_no_access_required_updates,
        impact_context=context,
    )
    if no_patch != rebuilt_no_patch:
        raise MathFlowError("work projection no-access patch does not match its response")

    with_input = _load_json_role(bundle_dir, manifest, "with-access-stage-input")
    expected_with_input = build_with_access_stage_input(
        safe_facts=safe_facts,
        impact_context=context,
        research_state=after,
        evidence_manifest=evidence_manifest,
        evidence_chunks=chunks,
    )
    if with_input != expected_with_input:
        raise MathFlowError("work projection with-access input is not reproducible")
    assemble_with_access_evidence(with_input, chunks)
    with_request = _load_json_role(bundle_dir, manifest, "with-access-request")
    expected_with_request = _make_request(
        stage="with-access",
        problem_id=str(contract["problemId"]),
        subject_transaction_id=subject,
        bindings=bindings,
        root_contract=contract,
        base_accounting_state=base,
        topology_alignment=alignment,
        required_updates=with_access_required_updates,
        stage_input=with_input,
    )
    if with_request != expected_with_request:
        raise MathFlowError("work projection with-access request is not reproducible")
    with_response = _load_json_role(bundle_dir, manifest, "with-access-response")
    with_patch = _load_json_role(bundle_dir, manifest, "with-access-work-patch")
    rebuilt_with_patch = _patch_from_response(
        with_response,
        mode="with-access",
        problem_id=str(contract["problemId"]),
        subject_transaction_id=subject,
        bindings=bindings,
        base_accounting_state=base,
        required_updates=with_access_required_updates,
        impact_context=context,
    )
    if with_patch != rebuilt_with_patch:
        raise MathFlowError("work projection with-access patch does not match its response")

    no_state, with_state, evaluation = materialize_submission_work_value(
        base_state=base,
        no_access_patch=no_patch,
        with_access_patch=with_patch,
        root_contract=contract,
        base_knowledge_state=before,
        target_knowledge_state=after,
        topology_alignment=alignment,
    )
    if no_state != _load_json_role(bundle_dir, manifest, "no-access-work-state"):
        raise MathFlowError("work projection no-access state is not reproducible")
    if with_state != _load_json_role(bundle_dir, manifest, "with-access-work-state"):
        raise MathFlowError("work projection with-access state is not reproducible")
    if evaluation != _load_json_role(bundle_dir, manifest, "submission-work-evaluation"):
        raise MathFlowError("work projection evaluation is not reproducible")
    validate_counterfactual_safe_facts(safe_facts)
    validate_impact_subgraph_context(context)
    validate_work_accounting_patch(no_patch)
    validate_work_accounting_patch(with_patch)
    validate_submission_work_value(evaluation)

    requests = (safe_request, no_request, with_request)
    responses = (safe_response, no_response, with_response)
    if manifest["requestDigests"] != [item["requestDigest"] for item in requests]:
        raise MathFlowError("work projection bundle request digest index mismatch")
    if manifest["responseDigests"] != [
        _response_digest(stage, response)
        for stage, response in zip(STAGES, responses, strict=True)
    ]:
        raise MathFlowError("work projection bundle response digest index mismatch")
    final_bindings = {
        "safeFactsDigest": safe_facts["safeFactsDigest"],
        "impactContextDigest": context["contextDigest"],
        "noAccessPatchDigest": no_patch["patchDigest"],
        "withAccessPatchDigest": with_patch["patchDigest"],
        "noAccessStateDigest": no_state["stateDigest"],
        "withAccessStateDigest": with_state["stateDigest"],
        "evaluationDigest": evaluation["evaluationDigest"],
    }
    for field, expected in final_bindings.items():
        if manifest.get(field) != expected:
            raise MathFlowError(f"work projection bundle {field} binding mismatch")
    return {
        "manifest": manifest,
        "bundleDigest": bundle_digest,
        "rootContract": contract,
        "baseKnowledgeState": before,
        "targetKnowledgeState": after,
        "baseAccountingState": base,
        "topologyAlignment": alignment,
        "evidenceManifest": evidence_manifest,
        "evidenceChunks": chunks,
        "safeFacts": safe_facts,
        "impactContext": context,
        "noAccessPatch": no_patch,
        "withAccessPatch": with_patch,
        "noAccessState": no_state,
        "withAccessState": with_state,
        "evaluation": evaluation,
    }
