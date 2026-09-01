"""Provider-free preflight for the No-Three-in-Line V10/V2 shadow.

This module intentionally has no provider or transport boundary.  It verifies
the frozen repository/projection inputs and produces a deterministic serial
execution and request-budget plan.  Semantic requests remain unmaterialized
until an explicitly authorized runner has trusted predecessor K/W states.
"""

from __future__ import annotations

import copy
import hashlib
import json
import subprocess
from collections.abc import Mapping, Sequence
from pathlib import Path, PurePosixPath

from .artifacts import sha256_bytes
from .counterfactual_context import (
    accepted_claim_refs_from_validity,
    build_submission_evidence_manifest,
    manifest_submission_at,
    reconstruct_submission_evidence,
)
from .errors import MathFlowError
from .repository import ledger, read_bytes_at, resolve_commit, sha256_json
from .research_builder_v7 import empty_research_program_state_v3
from .research_builder_v10 import build_research_builder_v10_route_context
from .validity import validate_evidence_packet_v4
from .work_accounting import make_zero_work_accounting_state, validate_root_contract


PROBLEM_ID = "no-three-in-line-77"
EXPERIMENT_ID = "no-three-v10-v2-shadow-v1"
ADAPTER_ID = "provider-free-serial-v10-v2-preflight-v1"
DEFAULT_MANIFEST_PATH = (
    "protocol/experiments/no-three-v10-v2-shadow-v1/manifest.json"
)
PROVIDER_STAGE_ORDER = (
    ("knowledge", "route"),
    ("knowledge", "route-refine"),
    ("knowledge", "organize"),
    ("accounting", "safe-facts"),
    ("accounting", "with-access"),
    ("accounting", "no-access"),
)
SERIAL_STAGE_ORDER = (
    ("knowledge", "route", "provider-request"),
    ("knowledge", "route-refine", "provider-request"),
    ("knowledge", "organize", "provider-request"),
    ("knowledge", "trusted-reduce", "trusted-local"),
    ("accounting", "safe-facts", "provider-request"),
    ("accounting", "with-access", "provider-request"),
    ("accounting", "freeze-with-access", "trusted-local"),
    ("accounting", "no-access", "provider-request"),
    ("accounting", "trusted-reduce", "trusted-local"),
)


def _digest_bytes(value: bytes) -> str:
    return f"sha256:{hashlib.sha256(value).hexdigest()}"


def _object_digest(value: object) -> str:
    return f"sha256:{sha256_json(value)}"


def _mapping(value: object, label: str) -> dict[str, object]:
    if not isinstance(value, dict):
        raise MathFlowError(f"{label} must be an object")
    return value


def _sequence(value: object, label: str) -> list[object]:
    if not isinstance(value, list):
        raise MathFlowError(f"{label} must be an array")
    return value


def _text(value: object, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise MathFlowError(f"{label} must be non-empty text")
    return value


def _integer(value: object, label: str, *, minimum: int = 0) -> int:
    if (
        not isinstance(value, int)
        or isinstance(value, bool)
        or value < minimum
    ):
        raise MathFlowError(f"{label} must be an integer of at least {minimum}")
    return value


def _repo_path(root: Path, value: object, label: str) -> tuple[str, Path]:
    rendered = _text(value, label)
    path = PurePosixPath(rendered)
    if (
        path.is_absolute()
        or not path.parts
        or any(part in {"", ".", ".."} for part in path.parts)
        or path.as_posix() != rendered
    ):
        raise MathFlowError(f"{label} must be a canonical repository-relative path")
    unresolved = root / rendered
    if unresolved.is_symlink():
        raise MathFlowError(f"{label} must not be a symlink")
    target = unresolved.resolve()
    try:
        target.relative_to(root)
    except ValueError as exc:
        raise MathFlowError(f"{label} escapes the repository root") from exc
    if not target.is_file() or target.is_symlink():
        raise MathFlowError(f"{label} must name a regular non-symlink file")
    return rendered, target


def _worktree_submission_manifest(
    root: Path, *, transaction_id: str, contribution_path: str
) -> tuple[dict[str, object], dict[str, bytes]]:
    directory = root / contribution_path
    if not directory.is_dir() or directory.is_symlink():
        raise MathFlowError("No-Three current contribution directory is invalid")
    files: dict[str, bytes] = {}
    for path in sorted(directory.rglob("*")):
        if path.is_symlink():
            raise MathFlowError("No-Three current contribution evidence contains a symlink")
        if path.is_file():
            files[path.relative_to(root).as_posix()] = path.read_bytes()
    return build_submission_evidence_manifest(
        problem_id=PROBLEM_ID,
        subject_transaction_id=transaction_id,
        contribution_path=contribution_path,
        files=files,
    )


def _json_file(root: Path, value: object, label: str) -> tuple[str, Path, dict[str, object]]:
    rendered, target = _repo_path(root, value, label)
    try:
        loaded = json.loads(target.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise MathFlowError(f"{label} is not readable JSON") from exc
    return rendered, target, _mapping(loaded, label)


def _git_text(root: Path, *arguments: str) -> str:
    try:
        result = subprocess.run(
            ["git", *arguments],
            cwd=root,
            check=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
    except FileNotFoundError as exc:
        raise MathFlowError("Git is required for the No-Three shadow preflight") from exc
    if result.returncode:
        detail = result.stderr.strip() or result.stdout.strip()
        raise MathFlowError(f"No-Three shadow Git binding failed: {detail}")
    return result.stdout


def _projection_bundle(
    root: Path, commit: str, bundle_path: str
) -> tuple[dict[str, object], dict[str, bytes], str]:
    path = PurePosixPath(bundle_path)
    if (
        path.is_absolute()
        or not path.parts
        or any(part in {"", ".", ".."} for part in path.parts)
        or path.as_posix() != bundle_path
    ):
        raise MathFlowError("projection bundle path is unsafe")
    run_bytes = read_bytes_at(root, commit, f"{bundle_path}/run.json")
    try:
        run = json.loads(run_bytes)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise MathFlowError("projection run manifest is not valid JSON") from exc
    manifest = _mapping(run, "projection run manifest")
    artifacts: dict[str, bytes] = {}
    for raw_entry in _sequence(manifest.get("artifacts"), "projection artifacts"):
        entry = _mapping(raw_entry, "projection artifact")
        role = _text(entry.get("role"), "projection artifact role")
        artifact_path = _text(entry.get("path"), "projection artifact path")
        if role in artifacts:
            raise MathFlowError(f"projection bundle repeats artifact role: {role}")
        raw = read_bytes_at(root, commit, f"{bundle_path}/{artifact_path}")
        if (
            _digest_bytes(raw) != entry.get("digest")
            or len(raw) != entry.get("bytes")
        ):
            raise MathFlowError(
                f"projection artifact does not match its run manifest: {role}"
            )
        artifacts[role] = raw
    return manifest, artifacts, _digest_bytes(run_bytes)


def _path_content_digest(
    files: Mapping[str, bytes], contribution_path: str
) -> str:
    prefix = PurePosixPath(contribution_path)
    digest = hashlib.sha256()
    for path, content in sorted(files.items()):
        try:
            relative = PurePosixPath(path).relative_to(prefix).as_posix()
        except ValueError as exc:
            raise MathFlowError("submission evidence escapes its contribution") from exc
        digest.update(relative.encode("utf-8"))
        digest.update(b"\0")
        digest.update(hashlib.sha256(content).hexdigest().encode("ascii"))
        digest.update(b"\n")
    return f"sha256:{digest.hexdigest()}"


def _accepted_claim_assessments(
    judgment: Mapping[str, object], packet: Mapping[str, object]
) -> list[dict[str, object]]:
    claim_by_key = {
        str(item.get("claimKey")): item
        for item in _sequence(packet.get("claims"), "validity packet claims")
        if isinstance(item, dict) and isinstance(item.get("claimKey"), str)
    }
    accepted: list[dict[str, object]] = []
    for raw_assessment in _sequence(
        judgment.get("assessments"), "validity assessments"
    ):
        assessment = _mapping(raw_assessment, "validity assessment")
        if assessment.get("status") != "valid":
            continue
        claim_key = _text(assessment.get("claimKey"), "accepted claim key")
        claim = claim_by_key.get(claim_key)
        if not isinstance(claim, dict):
            raise MathFlowError("validity assessment has no packet claim")
        accepted.append(
            {
                "claimKey": claim_key,
                "declaredStatement": _text(
                    claim.get("statement"), "accepted declared statement"
                ),
                "validitySummary": _text(
                    assessment.get("summary"), "accepted validity summary"
                ),
                "scopeQualifications": sorted(
                    {
                        _text(item, "accepted scope qualification")
                        for item in _sequence(
                            assessment.get("scopeQualifications"),
                            "accepted scope qualifications",
                        )
                    }
                ),
                "evidenceTransactionIds": sorted(
                    {
                        _text(item, "accepted evidence transaction")
                        for item in _sequence(
                            assessment.get("evidenceTransactionIds"),
                            "accepted evidence transactions",
                        )
                    }
                ),
                "dependencyTransactionIds": sorted(
                    {
                        _text(item, "accepted dependency transaction")
                        for item in _sequence(
                            assessment.get("requiredDependencyTransactionIds"),
                            "accepted dependency transactions",
                        )
                    }
                ),
            }
        )
    accepted.sort(key=lambda item: str(item["claimKey"]))
    if not accepted:
        raise MathFlowError("No-Three shadow subject has no accepted claim")
    if len({item["claimKey"] for item in accepted}) != len(accepted):
        raise MathFlowError("No-Three shadow accepted claim identities repeat")
    return accepted


def _frozen_inputs(
    root: Path, manifest: Mapping[str, object]
) -> tuple[dict[str, dict[str, object]], list[dict[str, object]]]:
    by_id: dict[str, dict[str, object]] = {}
    bindings: list[dict[str, object]] = []
    for raw_binding in _sequence(
        manifest.get("frozenLocalInputs"), "frozen local inputs"
    ):
        binding = _mapping(raw_binding, "frozen local input")
        input_id = _text(binding.get("id"), "frozen input ID")
        if input_id in by_id:
            raise MathFlowError(f"frozen local input ID repeats: {input_id}")
        path, target = _repo_path(root, binding.get("path"), "frozen input path")
        digest = _digest_bytes(target.read_bytes())
        if digest != binding.get("digest"):
            raise MathFlowError(f"frozen local input digest mismatch: {input_id}")
        normalized = copy.deepcopy(binding)
        by_id[input_id] = normalized
        bindings.append(
            {
                "id": input_id,
                "path": path,
                "digest": digest,
                "bytes": target.stat().st_size,
            }
        )
    return by_id, bindings


def _stage_limits(spec: Mapping[str, object], label: str) -> tuple[int, dict[str, int]]:
    retry = _mapping(spec.get("retryPolicy"), f"{label} retry policy")
    attempts = _integer(
        retry.get("maximumAttempts"), f"{label} maximum attempts", minimum=1
    )
    stages = _mapping(spec.get("stages"), f"{label} stages")
    limits: dict[str, int] = {}
    for stage, raw_stage in stages.items():
        record = _mapping(raw_stage, f"{label} {stage} stage")
        parameters = _mapping(record.get("parameters"), f"{label} {stage} parameters")
        limits[str(stage)] = _integer(
            parameters.get("max_tokens"),
            f"{label} {stage} completion limit",
            minimum=1,
        )
    return attempts, limits


def _verify_baselines(
    root: Path,
    commit: str,
    snapshot: Mapping[str, object],
    manifest: Mapping[str, object],
) -> list[dict[str, object]]:
    roles = {
        "legacyKnowledge": "research-program-state",
        "legacyHierarchicalCredit": "hierarchical-credit-state",
    }
    result: list[dict[str, object]] = []
    baselines = _mapping(manifest.get("observationalBaselines"), "observational baselines")
    for key, role in roles.items():
        baseline = _mapping(baselines.get(key), f"{key} baseline")
        run, artifacts, run_digest = _projection_bundle(
            root, commit, _text(baseline.get("path"), f"{key} path")
        )
        if run_digest != baseline.get("runDigest"):
            raise MathFlowError(f"{key} run digest mismatch")
        if (
            run.get("problemLedgerHead") != snapshot.get("problemLedgerHead")
            or run.get("problemLedgerDigest") != snapshot.get("problemLedgerDigest")
        ):
            raise MathFlowError(f"{key} uses another problem-ledger horizon")
        raw_state = artifacts.get(role)
        if raw_state is None or _digest_bytes(raw_state) != baseline.get(
            "stateArtifactDigest"
        ):
            raise MathFlowError(f"{key} state artifact digest mismatch")
        try:
            state = json.loads(raw_state)
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise MathFlowError(f"{key} state artifact is invalid JSON") from exc
        if not isinstance(state, dict) or state.get("stateDigest") != baseline.get(
            "stateDigest"
        ):
            raise MathFlowError(f"{key} state identity mismatch")
        result.append(
            {
                "id": key,
                "role": baseline.get("role"),
                "runDigest": run_digest,
                "stateArtifactDigest": _digest_bytes(raw_state),
                "stateDigest": state["stateDigest"],
            }
        )
    return result


def build_no_three_v10_v2_shadow_preflight(
    root: Path,
    manifest_path: Path | str = DEFAULT_MANIFEST_PATH,
) -> dict[str, object]:
    """Verify frozen inputs and return a zero-call serial execution plan.

    No provider object, transport, credential, or publication store can be
    supplied to this function.  The returned plan contains no semantic request
    digest because those requests depend on yet-unwritten trusted predecessors.
    """

    repository = root.resolve()
    if not repository.is_dir():
        raise MathFlowError("No-Three shadow repository root is missing")
    requested_manifest = Path(manifest_path)
    if requested_manifest.is_absolute():
        resolved_manifest = requested_manifest.resolve()
        try:
            manifest_relative = resolved_manifest.relative_to(repository).as_posix()
        except ValueError as exc:
            raise MathFlowError("No-Three shadow manifest escapes the repository") from exc
    else:
        manifest_relative = requested_manifest.as_posix()
    manifest_relative, manifest_file, manifest = _json_file(
        repository, manifest_relative, "No-Three shadow manifest"
    )
    manifest_digest = _digest_bytes(manifest_file.read_bytes())
    if (
        manifest.get("schemaVersion") != 1
        or manifest.get("id") != EXPERIMENT_ID
        or manifest.get("problemId") != PROBLEM_ID
        or manifest.get("status") != "planned-unpublished-experiment"
        or manifest.get("publicationForbidden") is not True
        or manifest.get("productionMutationForbidden") is not True
    ):
        raise MathFlowError("No-Three shadow manifest is not the frozen unpublished experiment")
    execution = _mapping(manifest.get("execution"), "No-Three execution")
    if (
        execution.get("adapter") != ADAPTER_ID
        or execution.get("providerExecutionAuthorized") is not False
        or execution.get("continue") is not False
        or execution.get("rootContractReviewStatus") != "review-required"
        or execution.get("semanticFixtures") != []
        or execution.get("semanticOutputDigests") != []
    ):
        raise MathFlowError("No-Three shadow execution is not fail-closed")
    zero_budgets = _mapping(manifest.get("budgets"), "No-Three execution budgets")
    if not zero_budgets or any(value != 0 for value in zero_budgets.values()):
        raise MathFlowError("No-Three provider-free preflight must have only zero budgets")

    frozen_by_id, frozen_bindings = _frozen_inputs(repository, manifest)
    required_frozen_ids = {
        "experimental-knowledge-projection",
        "root-contract-review-draft",
        "preflight-runner-implementation",
        "knowledge-builder-spec",
        "work-accounting-spec",
        "work-accounting-policy",
    }
    if set(frozen_by_id) != required_frozen_ids:
        raise MathFlowError("No-Three shadow frozen input set is incomplete")

    projection_binding = frozen_by_id["experimental-knowledge-projection"]
    _, _, projection_spec = _json_file(
        repository,
        projection_binding["path"],
        "No-Three experimental knowledge projection",
    )
    if (
        projection_spec.get("id") != "no-three-research-v10-shadow-v1"
        or projection_spec.get("status") != "review-draft-unpublished-experiment"
        or projection_spec.get("allowedProblems") != [PROBLEM_ID]
        or projection_spec.get("publicationForbidden") is not True
        or projection_spec.get("productionMutationForbidden") is not True
        or projection_spec.get("providerExecutionAuthorized") is not False
        or projection_spec.get("initialStateFactory")
        != execution.get("initialKnowledgeStateFactory")
    ):
        raise MathFlowError("No-Three experimental knowledge projection is unsafe")
    problem_binding = _mapping(
        projection_spec.get("canonicalProblem"), "projection canonical problem"
    )
    problem_path, problem_file = _repo_path(
        repository, problem_binding.get("path"), "projection canonical problem path"
    )
    if (
        problem_path != f"problems/{PROBLEM_ID}/problem.md"
        or _digest_bytes(problem_file.read_bytes()) != problem_binding.get("digest")
    ):
        raise MathFlowError("No-Three projection canonical objective digest mismatch")
    builder_binding = _mapping(
        projection_spec.get("knowledgeBuilder"), "projection knowledge builder"
    )
    if builder_binding.get("path") != frozen_by_id["knowledge-builder-spec"].get(
        "path"
    ) or builder_binding.get("digest") != frozen_by_id["knowledge-builder-spec"].get(
        "digest"
    ):
        raise MathFlowError("No-Three projection builder binding mismatch")

    contract_binding = frozen_by_id["root-contract-review-draft"]
    _, _, raw_contract = _json_file(
        repository, contract_binding["path"], "No-Three root-contract review draft"
    )
    contract = validate_root_contract(raw_contract, PROBLEM_ID)
    projection_spec_digest = _object_digest(projection_spec)
    if (
        contract.get("knowledgeProjectionId") != projection_spec.get("id")
        or contract.get("knowledgeProjectionSpecDigest") != projection_spec_digest
        or contract.get("rootContractDigest") != execution.get("rootContractDigest")
    ):
        raise MathFlowError("No-Three root contract is not bound to the shadow projection")

    _, _, builder_spec = _json_file(
        repository,
        frozen_by_id["knowledge-builder-spec"]["path"],
        "No-Three V10 builder spec",
    )
    _, _, accounting_spec = _json_file(
        repository,
        frozen_by_id["work-accounting-spec"]["path"],
        "No-Three V2 accounting spec",
    )
    if (
        builder_spec.get("id")
        != "openrouter-hierarchical-research-builder-v10-experiment"
        or builder_spec.get("implementation")
        != "openrouter-hierarchical-research-builder-v10"
        or builder_binding.get("id") != builder_spec.get("id")
        or accounting_spec.get("id") != "openrouter-work-accounting-v2"
        or accounting_spec.get("implementation") != "openrouter-work-accounting-v2"
        or builder_spec.get("model") != accounting_spec.get("model")
    ):
        raise MathFlowError("No-Three shadow judge identity mismatch")
    builder_attempts, builder_limits = _stage_limits(builder_spec, "V10 builder")
    accounting_attempts, accounting_limits = _stage_limits(
        accounting_spec, "V2 accounting"
    )
    if set(builder_limits) != {"route", "route-refine", "organize"} or set(
        accounting_limits
    ) != {"safe-facts", "with-access", "no-access"}:
        raise MathFlowError("No-Three shadow provider stage set drifted")

    snapshot = _mapping(manifest.get("projectionSnapshot"), "projection snapshot")
    commit = _text(snapshot.get("commit"), "projection snapshot commit")
    if resolve_commit(repository, commit) != commit:
        raise MathFlowError("No-Three projection snapshot is not an exact commit")
    for label in ("catalog", "problemRunIndex"):
        binding = _mapping(snapshot.get(label), f"projection {label}")
        raw = read_bytes_at(repository, commit, _text(binding.get("path"), label))
        if _digest_bytes(raw) != binding.get("digest"):
            raise MathFlowError(f"No-Three projection {label} digest mismatch")
    canonical = ledger(
        repository,
        PROBLEM_ID,
        _text(snapshot.get("problemLedgerHead"), "problem ledger head"),
    )
    if (
        canonical.get("problemLedgerHead") != snapshot.get("problemLedgerHead")
        or canonical.get("problemLedgerDigest") != snapshot.get("problemLedgerDigest")
    ):
        raise MathFlowError("No-Three canonical ledger binding mismatch")
    transactions = _sequence(canonical.get("transactions"), "canonical transactions")

    initial_knowledge = empty_research_program_state_v3(PROBLEM_ID)
    initial_accounting = make_zero_work_accounting_state(
        root_contract=contract, knowledge_state=initial_knowledge
    )
    subjects: list[dict[str, object]] = []
    for raw_subject in _sequence(manifest.get("subjects"), "No-Three subjects"):
        subject = _mapping(raw_subject, "No-Three subject")
        sequence = _integer(
            subject.get("acceptedSequenceIndex"), "accepted sequence", minimum=1
        )
        ledger_position = _integer(
            subject.get("ledgerPosition"), "subject ledger position", minimum=1
        )
        transaction_id = _text(subject.get("transactionId"), "subject transaction")
        if ledger_position > len(transactions):
            raise MathFlowError("No-Three subject ledger position is out of range")
        transaction = _mapping(
            transactions[ledger_position - 1], "canonical subject transaction"
        )
        if (
            transaction.get("ordinal") != ledger_position
            or transaction.get("transactionId") != transaction_id
            or transaction.get("contributionId") != subject.get("contributionId")
            or transaction.get("path") != subject.get("contributionPath")
        ):
            raise MathFlowError("No-Three subject does not match the canonical ledger")
        contribution_path = _text(
            subject.get("contributionPath"), "subject contribution path"
        )
        tree_id = _git_text(
            repository, "rev-parse", f"{transaction_id}:{contribution_path}"
        ).strip()
        if tree_id != subject.get("gitTreeObjectId"):
            raise MathFlowError("No-Three subject Git tree object mismatch")

        historical_manifest, historical_chunks = manifest_submission_at(
            repository,
            problem_id=PROBLEM_ID,
            subject_transaction_id=transaction_id,
            contribution_path=contribution_path,
        )
        historical_files = reconstruct_submission_evidence(
            historical_manifest, historical_chunks
        )
        current_manifest, current_chunks = _worktree_submission_manifest(
            repository,
            transaction_id=transaction_id,
            contribution_path=contribution_path,
        )
        current_files = reconstruct_submission_evidence(current_manifest, current_chunks)
        if current_files != historical_files:
            raise MathFlowError("No-Three current evidence differs from its subject tree")
        evidence = _mapping(subject.get("evidenceBundle"), "subject evidence bundle")
        if (
            evidence.get("algorithm") != "sha256-path-content-v1"
            or evidence.get("fileCount") != len(historical_files)
            or evidence.get("bytes") != sum(len(item) for item in historical_files.values())
            or evidence.get("digest")
            != _path_content_digest(historical_files, contribution_path)
        ):
            raise MathFlowError("No-Three subject evidence bundle mismatch")

        judgment_binding = _mapping(subject.get("judgment"), "subject judgment")
        run, artifacts, run_digest = _projection_bundle(
            repository,
            commit,
            _text(judgment_binding.get("path"), "subject judgment path"),
        )
        if (
            run_digest != judgment_binding.get("runDigest")
            or run.get("problemId") != PROBLEM_ID
            or run.get("problemLedgerHead") != snapshot.get("problemLedgerHead")
            or run.get("problemLedgerDigest") != snapshot.get("problemLedgerDigest")
            or _mapping(run.get("judgeSpec"), "validity judge identity").get("id")
            != _mapping(
                manifest.get("subjectSelection"), "subject selection"
            ).get("validityJudgeSpecId")
            or _mapping(run.get("judgeSpec"), "validity judge identity").get(
                "digest"
            )
            != _mapping(
                manifest.get("subjectSelection"), "subject selection"
            ).get("validityJudgeSpecDigest")
        ):
            raise MathFlowError("No-Three validity run identity mismatch")
        inputs = _mapping(run.get("inputs"), "validity run inputs")
        if (
            inputs.get("subjectTransactionIds") != [transaction_id]
            or inputs.get("dependencyPacketDigest")
            != judgment_binding.get("dependencyPacketDigest")
        ):
            raise MathFlowError("No-Three validity run subject binding mismatch")
        judgment_raw = artifacts.get("judgment-record")
        packet_raw = artifacts.get("judgment-dependency-packet")
        report_raw = artifacts.get("judgment-report")
        if judgment_raw is None or packet_raw is None or report_raw is None:
            raise MathFlowError("No-Three validity bundle is incomplete")
        if (
            _digest_bytes(judgment_raw)
            != judgment_binding.get("judgmentRecordArtifactDigest")
            or _digest_bytes(packet_raw)
            != judgment_binding.get("dependencyPacketArtifactDigest")
            or _digest_bytes(report_raw) != judgment_binding.get("reportArtifactDigest")
        ):
            raise MathFlowError("No-Three validity artifact binding mismatch")
        try:
            judgment = _mapping(
                json.loads(judgment_raw), "No-Three validity judgment"
            )
            packet = validate_evidence_packet_v4(json.loads(packet_raw))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise MathFlowError("No-Three validity artifacts are invalid JSON") from exc
        if (
            judgment.get("judgmentId") != judgment_binding.get("judgmentId")
            or packet.get("packetDigest") != judgment_binding.get("dependencyPacketDigest")
            or packet.get("subjectTransactionId") != transaction_id
        ):
            raise MathFlowError("No-Three accepted judgment binding mismatch")
        claims = _accepted_claim_assessments(judgment, packet)
        claim_refs = accepted_claim_refs_from_validity(
            judgment, subject_transaction_id=transaction_id
        )
        if (
            [item["claimKey"] for item in claims] != [subject.get("claimKey")]
            or sorted(
                {
                    dependency
                    for item in claims
                    for dependency in item["dependencyTransactionIds"]
                }
            )
            != subject.get("requiredDependencyTransactionIds")
        ):
            raise MathFlowError("No-Three accepted claim selection mismatch")
        for attestation_digest in _sequence(
            judgment_binding.get("objectiveAttestationRunDigests"),
            "objective attestation digests",
        ):
            digest = _text(attestation_digest, "objective attestation digest")
            digest_hex = digest.removeprefix("sha256:")
            raw_attestation = read_bytes_at(
                repository,
                commit,
                f"objects/verifier-attestation/{digest_hex[:2]}/{digest_hex}/run.json",
            )
            if _digest_bytes(raw_attestation) != digest:
                raise MathFlowError("No-Three objective attestation digest mismatch")

        # All current accepted subjects have empty required dependency sets, so
        # a from-zero route context is sufficient to validate the exact V10
        # accepted-claim shape without pretending it is the later live route.
        shape_context = build_research_builder_v10_route_context(
            initial_knowledge, claims
        )
        subjects.append(
            {
                "acceptedSequenceIndex": sequence,
                "ledgerPosition": ledger_position,
                "transactionId": transaction_id,
                "contributionId": subject.get("contributionId"),
                "gitTreeObjectId": tree_id,
                "judgmentRunDigest": run_digest,
                "judgmentId": judgment["judgmentId"],
                "acceptedClaimsDigest": _object_digest(claims),
                "acceptedClaimRefsDigest": _object_digest(claim_refs),
                "acceptedClaimKeys": [item["claimKey"] for item in claims],
                "requiredDependencyTransactionIds": subject.get(
                    "requiredDependencyTransactionIds"
                ),
                "evidenceManifestDigest": historical_manifest["manifestDigest"],
                "submissionDigest": historical_manifest["submissionDigest"],
                "evidenceFileCount": len(historical_files),
                "evidenceBytes": sum(len(item) for item in historical_files.values()),
                "fromZeroClaimShapeContextDigest": shape_context["contextDigest"],
            }
        )

    subjects.sort(key=lambda item: int(item["acceptedSequenceIndex"]))
    if (
        [item["acceptedSequenceIndex"] for item in subjects] != [1, 2, 3, 4]
        or [item["ledgerPosition"] for item in subjects] != [4, 5, 9, 10]
        or len({item["transactionId"] for item in subjects}) != 4
    ):
        raise MathFlowError("No-Three accepted subject ordering is not exact")
    selection = _mapping(manifest.get("subjectSelection"), "subject selection")
    if (
        selection.get("acceptedCount") != len(subjects)
        or selection.get("canonicalContributionCount") != len(transactions)
        or selection.get("selectionRule")
        != "Include exactly the canonical transactions whose pinned validity-v4 assessment status is valid; preserve canonical ledger position and consume each exactly once."
    ):
        raise MathFlowError("No-Three subject-selection contract mismatch")

    baselines = _verify_baselines(repository, commit, snapshot, manifest)
    envelope = _mapping(
        manifest.get("futureExecutionEnvelope"), "future execution envelope"
    )
    if envelope.get("advisoryNotAuthorization") is not True:
        raise MathFlowError("No-Three future envelope must not authorize execution")
    per_call_request_bytes = _integer(
        envelope.get("maximumRequestBytes"), "maximum request bytes", minimum=1
    )
    per_call_prompt_tokens = _integer(
        envelope.get("maximumEstimatedPromptTokensPerCall"),
        "maximum estimated prompt tokens per call",
        minimum=1,
    )
    per_call_cost = envelope.get("maximumSingleCallCostUsd")
    if not isinstance(per_call_cost, (int, float)) or isinstance(per_call_cost, bool) or per_call_cost <= 0:
        raise MathFlowError("maximum single-call cost must be positive")
    if builder_attempts != accounting_attempts or builder_attempts != envelope.get(
        "maximumAttemptsPerProviderStage"
    ):
        raise MathFlowError("No-Three retry envelope differs from judge specifications")

    stage_limits = {
        **{("knowledge", key): value for key, value in builder_limits.items()},
        **{("accounting", key): value for key, value in accounting_limits.items()},
    }
    stages: list[dict[str, object]] = []
    previous_stage_id: str | None = None
    for subject in subjects:
        subject_index = int(subject["acceptedSequenceIndex"])
        for subsystem, stage, stage_kind in SERIAL_STAGE_ORDER:
            stage_id = f"k{subject_index}-{subsystem}-{stage}"
            record: dict[str, object] = {
                "stageIndex": len(stages) + 1,
                "stageId": stage_id,
                "subjectSequenceIndex": subject_index,
                "subjectTransactionId": subject["transactionId"],
                "subsystem": subsystem,
                "stage": stage,
                "kind": stage_kind,
                "dependsOnStageId": previous_stage_id,
                "providerExecutionAuthorized": False,
                "publicationAuthorized": False,
            }
            if stage_kind == "provider-request":
                completion = stage_limits[(subsystem, stage)]
                record["requestMaterialization"] = (
                    "deferred-until-reviewed-contract-explicit-provider-authorization-"
                    "and-exact-trusted-predecessor"
                )
                record["requestBudget"] = {
                    "maximumRequestBytes": per_call_request_bytes,
                    "maximumEstimatedPromptTokens": per_call_prompt_tokens,
                    "maximumCompletionTokens": completion,
                    "maximumAttempts": builder_attempts,
                    "maximumReservedCompletionTokens": completion * builder_attempts,
                    "maximumSingleCallCostUsd": per_call_cost,
                }
            else:
                record["requestMaterialization"] = "trusted-local-step-after-predecessor"
                record["providerCallBudget"] = 0
            stages.append(record)
            previous_stage_id = stage_id

    nominal_calls = len(subjects) * len(PROVIDER_STAGE_ORDER)
    maximum_attempts = nominal_calls * builder_attempts
    completion_reservation = sum(
        int(stage["requestBudget"]["maximumReservedCompletionTokens"])
        for stage in stages
        if stage["kind"] == "provider-request"
    )
    if (
        envelope.get("nominalProviderCalls") != nominal_calls
        or envelope.get("maximumProviderCalls") != maximum_attempts
        or envelope.get("maximumReservedCompletionTokens")
        != completion_reservation
    ):
        raise MathFlowError("No-Three future execution envelope arithmetic mismatch")

    bindings = {
        "manifest": {
            "path": manifest_relative,
            "digest": manifest_digest,
        },
        "frozenLocalInputs": frozen_bindings,
        "projectionSnapshotCommit": commit,
        "problemLedgerHead": snapshot["problemLedgerHead"],
        "problemLedgerDigest": snapshot["problemLedgerDigest"],
        "rootContractDigest": contract["rootContractDigest"],
        "knowledgeProjectionId": projection_spec["id"],
        "knowledgeProjectionSpecDigest": projection_spec_digest,
        "initialKnowledgeStateDigest": initial_knowledge["stateDigest"],
        "initialAccountingStateDigest": initial_accounting["stateDigest"],
        "subjects": subjects,
        "observationalBaselines": baselines,
    }
    core: dict[str, object] = {
        "schemaVersion": 1,
        "runKind": "no-three-v10-v2-shadow-preflight",
        "experimentId": EXPERIMENT_ID,
        "status": "review-required-provider-free-plan-ready",
        "problemId": PROBLEM_ID,
        "publicationForbidden": True,
        "productionMutationForbidden": True,
        "providerExecutionAuthorized": False,
        "providerCallCount": 0,
        "semanticRequestDigests": [],
        "semanticRequestMaterializationReason": (
            "V10 and V2 requests after the first boundary depend on trusted K/W outputs "
            "that do not exist before semantic execution; preflight binds their inputs, "
            "order, and budgets without inventing predecessor state."
        ),
        "inputBindings": bindings,
        "inputBindingsDigest": _object_digest(bindings),
        "serialExecutionPlan": stages,
        "budgetPlan": {
            "providerStagesPerSubject": len(PROVIDER_STAGE_ORDER),
            "trustedLocalStagesPerSubject": len(SERIAL_STAGE_ORDER)
            - len(PROVIDER_STAGE_ORDER),
            "subjectCount": len(subjects),
            "nominalProviderCalls": nominal_calls,
            "maximumProviderAttempts": maximum_attempts,
            "maximumReservedCompletionTokens": completion_reservation,
            "maximumRequestBytesPerCall": per_call_request_bytes,
            "maximumEstimatedPromptTokensPerCall": per_call_prompt_tokens,
            "maximumTotalReportedTokens": envelope["maximumTotalReportedTokens"],
            "maximumSingleCallCostUsd": per_call_cost,
            "maximumTotalCostUsd": envelope["maximumTotalCostUsd"],
            "requestSideVerifiedPriceBoundRequired": envelope[
                "requestSideVerifiedPriceBoundRequired"
            ],
            "currentProviderCallsAuthorized": 0,
            "currentPromptTokensAuthorized": 0,
            "currentCompletionTokensAuthorized": 0,
            "currentCostUsdAuthorized": 0,
        },
        "remainingBlockers": [
            "explicit-root-contract-review",
            "semantic-runner-with-checkpoint-and-local-artifact-boundaries",
            "request-side-verified-price-bound",
            "explicit-provider-authorization",
        ],
    }
    return {**core, "planDigest": _object_digest(core)}


__all__ = [
    "ADAPTER_ID",
    "DEFAULT_MANIFEST_PATH",
    "EXPERIMENT_ID",
    "PROBLEM_ID",
    "build_no_three_v10_v2_shadow_preflight",
]
