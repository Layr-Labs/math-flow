"""Provider-neutral, unpublished K1->K2->K3 joint-portfolio holdout.

The holdout is deliberately outside projection, publication, governance, CLI,
and viewer surfaces.  It serializes the first three accepted BSSC validity-v4
subjects through the joint topology/live-W+ reducer and the frozen-W+ credit
adapter.  A caller injects both the joint-author runner/transport and the
counterfactual provider, so capture and fixture transports require no network.

The resulting bundle is not just a bag of self-digested model output.  Its
loader verifies every byte, reloads each nested validity bundle, rebuilds the
accepted claims and submission evidence, re-reduces every joint response, and
replays every safe-fact, counterfactual, work-state, and credit edge.
"""

from __future__ import annotations

import copy
import json
import re
import tempfile
from collections.abc import Mapping, Sequence
from pathlib import Path, PurePosixPath

from math_flow.artifacts import (
    ArtifactBundle,
    file_digest,
    read_verified_artifact,
    sha256_bytes,
    verify_bundle,
)
from math_flow.bssc_research_v4_producer import (
    _accepted_frontier,
    _materialize_validity_bundle,
)
from math_flow.counterfactual_context import (
    accepted_claim_refs_from_validity,
    build_counterfactual_safe_facts,
    build_impact_subgraph_context,
    manifest_submission_at,
    reconstruct_submission_evidence,
    validate_submission_evidence_manifest,
)
from math_flow.errors import MathFlowError
from math_flow.joint_portfolio_boundaries import (
    build_joint_portfolio_no_access_policy_context_v1,
    make_joint_portfolio_boundary_state_v1,
)
from math_flow.joint_portfolio_serial_credit_v2 import (
    _build_joint_no_access_input,
    _frozen,
    _joint_impact_seeds,
    _make_joint_no_access_request,
    run_joint_portfolio_serial_credit_v2,
    validate_joint_portfolio_serial_credit_replay_v2,
    validate_joint_portfolio_serial_frozen_wplus_v2,
)
from math_flow.joint_portfolio_serial_provider_v2 import (
    JointPortfolioSerialAuthorProvider,
    run_joint_portfolio_serial_author_v2,
    validate_joint_portfolio_serial_author_replay_v2,
)
from math_flow.joint_portfolio_serial_transition_v2 import (
    make_joint_portfolio_semantic_packet_v2,
)
from math_flow.judges import load_source
from math_flow.judgments import load_judgment_bundle
from math_flow.research_builder_v10 import (
    build_research_builder_v10_authoring_packet,
    build_research_builder_v10_route_context,
)
from math_flow.research_builder_v7 import empty_research_program_state_v3
from math_flow.research_projection import _accepted_claims
from math_flow.repository import sha256_json
from math_flow.work_accounting import (
    make_zero_work_accounting_state,
    materialize_submission_work_value,
    validate_root_contract,
)
from math_flow.work_projection import (
    PROFILE_V2,
    SubmissionEvidenceFile,
    WorkProjectionProvider,
    _assert_no_access_evidence_structure,
    _bindings,
    _ensure_required_context_coverage,
    _patch_from_response,
    _required_primitive_updates,
    _safe_fact_stage_input,
    _validate_transition,
)
from math_flow.work_projection import _make_request as _make_work_request


PROFILE = "math-flow/joint-portfolio-serial-holdout-v1"
EXPERIMENT_PATH = PurePosixPath(
    "protocol/experiments/bssc-joint-portfolio-serial-k1-k3-v1/manifest.json"
)
PROBLEM_ID = "bssc-sum-capacity"
SUBJECTS = (
    "c70e1829a7c6a2a8cb8cfc2383f8abf825ac5ea6",
    "f236017c62c67ce4218c1f81ea34134f0954b556",
    "14889884ae6ac1f80cc56485e7acf1b0b2cb6ae9",
)
STEP_PLAN = (
    {
        "ordinal": 1,
        "ledgerOrdinal": 3,
        "subjectTransactionId": SUBJECTS[0],
        "validityJudgmentId": "sha256:6811dbc06c253fd81a1d9244887b661fff26b22c3cdcda708cd6bdf5642a7293",
        "validityRunDigest": "sha256:fd6e2748ffa7a88e1b992001d4a36cfed0194c2ee608acf68907286e7facd0fe",
    },
    {
        "ordinal": 2,
        "ledgerOrdinal": 4,
        "subjectTransactionId": SUBJECTS[1],
        "validityJudgmentId": "sha256:2c29fd881dec9aa923aa0713acc56df2c05d02f30ac544213f720af9158b7a41",
        "validityRunDigest": "sha256:5ad78e67ec6a1f83651aa590ff7f3c2fb809eac8201422a69cd2bc8783a475c9",
    },
    {
        "ordinal": 3,
        "ledgerOrdinal": 5,
        "subjectTransactionId": SUBJECTS[2],
        "validityJudgmentId": "sha256:34c5377dbd5c5d147acb250ac80640770b6176749e6c235d4a71ebc508b615c2",
        "validityRunDigest": "sha256:cd8752f9eade1a095dd49c5b3d80463c89786ecf9e6587d57fb6f08c31ce86ec",
    },
)
K1_PROGRAM = "program-bssc-code-induced-converse"
K2_PROGRAM = "program-bssc-uv-product-branchwise-additivity"
K1_RESULTS = (
    "result-bssc-coarse-entropy-copy-refinement-no-go",
    "result-bssc-code-induced-finite-block-dependence-balance",
)
K2_RESULTS = (
    "result-uv-average-product-additivity",
    "result-uv-branchwise-symmetry-specialization",
)
DIGEST = re.compile(r"^sha256:[0-9a-f]{64}$")
ARTIFACT_FIELDS = {"path", "role", "mediaType", "digest", "bytes"}
CREDIT_ARTIFACT_NAMES = (
    "safeRequest",
    "safeResponse",
    "safeFacts",
    "impactContext",
    "noAccessPolicyContext",
    "noAccessInput",
    "noAccessRequest",
    "noAccessResponse",
    "noAccessPatch",
    "noAccessState",
    "withAccessPatch",
    "withAccessState",
    "evaluation",
    "creditCandidate",
)


def _digest(value: object) -> str:
    return f"sha256:{sha256_json(copy.deepcopy(value))}"


def _json_bytes(value: object) -> bytes:
    return (json.dumps(value, indent=2, ensure_ascii=False) + "\n").encode("utf-8")


def _load_json(path: Path, label: str) -> object:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as error:
        raise MathFlowError(f"joint holdout {label} is unreadable") from error


def _normalized_accepted_claims(
    judgment: Mapping[str, object], packet: Mapping[str, object]
) -> list[dict[str, object]]:
    raw = _accepted_claims(copy.deepcopy(dict(judgment)), copy.deepcopy(dict(packet)))
    claims = [
        {
            "claimKey": str(item["claimKey"]),
            "declaredStatement": str(item["statement"]),
            "validitySummary": str(item["validitySummary"]),
            "scopeQualifications": sorted(
                {str(value) for value in item["scopeQualifications"]}
            ),
            "evidenceTransactionIds": sorted(
                {str(value) for value in item["evidenceTransactionIds"]}
            ),
            "dependencyTransactionIds": sorted(
                {str(value) for value in item["dependencyTransactionIds"]}
            ),
        }
        for item in raw
    ]
    if not claims or claims != sorted(claims, key=lambda item: str(item["claimKey"])):
        raise MathFlowError("joint holdout validity claims are empty or noncanonical")
    return claims


def _semantic_claim_refs(
    claims: Sequence[Mapping[str, object]],
    *,
    subject_transaction_id: str,
    judgment_id: str,
) -> list[dict[str, str]]:
    return sorted(
        [
            {
                "transactionId": subject_transaction_id,
                "claimKey": str(claim["claimKey"]),
                "judgmentId": judgment_id,
                "assessmentDigest": _digest(claim),
            }
            for claim in claims
        ],
        key=lambda item: (
            item["claimKey"], item["judgmentId"], item["assessmentDigest"]
        ),
    )


def _root_boundary() -> dict[str, str]:
    return {
        "programId": "root",
        "directResidualWorkScope": (
            "Integration and choice among independent BSSC research packages, "
            "excluding the direct work assigned inside a child package."
        ),
        "activationCondition": (
            "The canonical BSSC sum-capacity problem remains unresolved."
        ),
        "stoppingCondition": (
            "The canonical objective is solved or every represented route is pruned."
        ),
        "independentVariationRationale": (
            "Root integration can vary independently of direct work inside any one route."
        ),
    }


def _support(
    *,
    proofs: Sequence[str] = (),
    methods: Sequence[str] = (),
    computations: Sequence[str] = (),
    tools: Sequence[str] = (),
    artifact_paths: Sequence[str] = (),
    attestation_refs: Sequence[str] = (),
) -> dict[str, object]:
    return {
        "proofs": sorted(set(proofs)),
        "methods": sorted(set(methods)),
        "computations": sorted(set(computations)),
        "tools": sorted(set(tools)),
        "artifactPaths": sorted(set(artifact_paths)),
        "attestationRefs": sorted(set(attestation_refs)),
    }


def _create_result(
    *,
    result_id: str,
    title: str,
    statement: str,
    qualifications: Sequence[str],
    support: Mapping[str, object],
    dependencies: Sequence[str],
    claim_key: str,
) -> dict[str, object]:
    return {
        "action": "create",
        "id": result_id,
        "baseDigest": None,
        "title": title,
        "statement": statement,
        "scopeQualifications": sorted(set(qualifications)),
        "supportAdditions": copy.deepcopy(dict(support)),
        "dependencyResultIds": sorted(set(dependencies)),
        "claimKeys": [claim_key],
        "status": "active",
        "supersededByResultIds": [],
    }


def _result_artifact_paths(evidence_manifest: Mapping[str, object]) -> list[str]:
    files = evidence_manifest.get("files")
    if not isinstance(files, list):
        raise MathFlowError("joint holdout evidence manifest is invalid")
    return sorted(str(item["path"]) for item in files if isinstance(item, Mapping))


def _semantic_packet(
    *,
    ordinal: int,
    state: Mapping[str, object],
    claims: Sequence[Mapping[str, object]],
    evidence_manifest: Mapping[str, object],
    evidence_files: Sequence[SubmissionEvidenceFile],
    dependency_packet: Mapping[str, object],
) -> dict[str, object]:
    subject = SUBJECTS[ordinal - 1]
    claim_key = str(claims[0]["claimKey"])
    refs = {item.path: item.digest for item in evidence_files}
    paths = _result_artifact_paths(evidence_manifest)
    if ordinal == 1:
        changes = [
            _create_result(
                result_id=K1_RESULTS[0],
                title="Finite entropic witness obstructing the specified entropy/copy refinement",
                statement=(
                    "An actual finite entropic witness satisfies the stated coarse BSSC "
                    "relaxation and attains both direct sum branches at "
                    "2h_2(1/4)-5/4, so universal finite-variable inequalities and any "
                    "finite standard copy-lemma sequence cannot lower that relaxation."
                ),
                qualifications=(
                    "The witness is not an actual binary-input BSSC distribution.",
                    "The result obstructs only the specified relaxation and is not a capacity bound.",
                ),
                support=_support(
                    proofs=("Explicit finite witness and conditional-resampling copy argument.",),
                    computations=("Exact structural and objective audit.",),
                    tools=("Python exact-arithmetic witness checker.",),
                    artifact_paths=paths,
                ),
                dependencies=(K1_RESULTS[1],),
                claim_key=claim_key,
            ),
            _create_result(
                result_id=K1_RESULTS[1],
                title="Finite-block code-induced dependence balance and compatible rate rows",
                statement=(
                    "Every deterministic private-message code induces the finite-block "
                    "dependence-balance telescope, fixed-coordinate encoder-map factorization, "
                    "and four compatible Fano-adjusted rate rows."
                ),
                qualifications=(
                    "The auxiliaries may grow with blocklength, so this is not a fixed-cardinality single-letter outer region.",
                    "The result is a necessary condition, not itself a capacity bound.",
                ),
                support=_support(
                    proofs=("Endpoint telescope, Fano bounds, and four chain-rule rate derivations.",),
                    methods=("Uniform-time single-letterization retaining the encoder map.",),
                    artifact_paths=paths,
                ),
                dependencies=(),
                claim_key=claim_key,
            ),
        ]
        root_update = {
            "currentStateSummary": (
                "Accepted K1 work establishes a code-induced finite-block converse structure "
                "and a no-go result for one coarse entropy/copy refinement."
            ),
            "localResidualSummary": (
                "The BSSC sum-capacity remains open; structure-preserving reductions and "
                "independent converse and achievability routes remain."
            ),
        }
    elif ordinal == 2:
        changes = [
            _create_result(
                result_id=K2_RESULTS[0],
                title="Exact product additivity of the averaged relaxed-UV scalar",
                statement=(
                    "For arbitrary finite-alphabet DMBCs, the averaged scalar formed from "
                    "the two separately relaxed UV rows is exactly additive under products, "
                    "including correlated product inputs and joint envelope auxiliaries."
                ),
                qualifications=(
                    "The theorem concerns an averaged separately-relaxed scalar, not the complete UV region.",
                    "It does not require the declared BSSC dependency.",
                ),
                support=_support(
                    proofs=("Analytic chain-rule and concave-envelope product argument.",),
                    computations=("Finite-channel and hostile-case corroborative audits.",),
                    artifact_paths=paths,
                ),
                dependencies=(),
                claim_key=claim_key,
            ),
            _create_result(
                result_id=K2_RESULTS[1],
                title="Receiver-skew symmetry bridge and exact BSSC product value",
                statement=(
                    "Receiver-exchanging involutive symmetry makes the branchwise relaxed-UV "
                    "scalar equal the averaged scalar and preserves additivity on finite products; "
                    "for the half-skew BSSC the normalized value is 2h_2(1/4)-5/4."
                ),
                qualifications=(
                    "The equality claim is restricted to receiver-skew channels.",
                    "The non-frontier scalar result does not establish capacity or full UV tensorization.",
                ),
                support=_support(
                    proofs=("Involution symmetrization and finite-product closure.",),
                    computations=("Decimal and hostile-case corroborative audits.",),
                    artifact_paths=paths,
                ),
                dependencies=(K1_RESULTS[0], K2_RESULTS[0]),
                claim_key=claim_key,
            ),
        ]
        root_update = {
            "currentStateSummary": (
                "K2 adds exact product additivity and receiver-skew specialization for the "
                "two separately relaxed UV scalars alongside K1."
            ),
            "localResidualSummary": (
                "The full UV region, coupled auxiliary systems, other converses, achievability, "
                "and the canonical capacity objective remain unresolved."
            ),
        }
    else:
        attestations = dependency_packet.get("objectiveAttestations", [])
        attestation_refs = sorted(
            str(raw["attestation"]["attestationId"])
            for raw in attestations
            if isinstance(raw, Mapping)
            and isinstance(raw.get("attestation"), Mapping)
            and isinstance(raw["attestation"].get("attestationId"), str)
        )
        changes = []
        for result_id in K2_RESULTS:
            prior = state["intermediateResults"].get(result_id)
            if not isinstance(prior, Mapping):
                raise MathFlowError("joint holdout K3 cannot find the exact K2 result")
            changes.append(
                {
                    "action": "support",
                    "id": result_id,
                    "baseDigest": prior["digest"],
                    "title": prior["title"],
                    "statement": prior["statement"],
                    "scopeQualifications": list(prior["scopeQualifications"]),
                    "supportAdditions": _support(
                        proofs=("Independent analytic proof of the same relaxed-UV theorem chain.",),
                        computations=("Selected support-contact and receiver-skew checks.",),
                        artifact_paths=paths,
                        attestation_refs=attestation_refs,
                    ),
                    "dependencyResultIds": list(prior["dependencyResultIds"]),
                    "claimKeys": [claim_key],
                    "status": prior["status"],
                    "supersededByResultIds": list(prior["supersededByResultIds"]),
                }
            )
        root_update = {
            "currentStateSummary": (
                "K3 adds independently accepted analytic and attested support to the exact "
                "existing K2 relaxed-UV theorem chain."
            ),
            "localResidualSummary": (
                "No new accounting route is created; the same UV package and broader BSSC "
                "residual portfolio remain."
            ),
        }
    return make_joint_portfolio_semantic_packet_v2(
        problem_id=PROBLEM_ID,
        subject_transaction_id=subject,
        base_state_digest=str(state["stateDigest"]),
        accepted_claims=claims,
        evidence_file_refs=refs,
        root_update=root_update,
        result_changes=sorted(changes, key=lambda item: str(item["id"])),
    )


def _authoring_packet(
    *, ordinal: int, state: Mapping[str, object], claims: object
) -> dict[str, object]:
    route_context = build_research_builder_v10_route_context(state, claims)
    if ordinal == 1:
        write_programs, write_results = ["root"], []
        create_programs, create_results = [K1_PROGRAM], list(K1_RESULTS)
        inspect_programs, inspect_results = [], []
    elif ordinal == 2:
        write_programs, write_results = ["root"], []
        create_programs, create_results = [K2_PROGRAM], list(K2_RESULTS)
        inspect_programs, inspect_results = [K1_PROGRAM], [K1_RESULTS[0]]
    else:
        write_programs, write_results = ["root", K2_PROGRAM], list(K2_RESULTS)
        create_programs, create_results = [], []
        inspect_programs, inspect_results = [], []
    route = {
        "schemaVersion": 1,
        "baseStateDigest": state["stateDigest"],
        "routeContextDigest": route_context["contextDigest"],
        "inspectProgramIds": sorted(inspect_programs),
        "inspectResultIds": sorted(inspect_results),
        "searchQueries": [],
        "writeProgramIds": sorted(write_programs),
        "writeResultIds": sorted(write_results),
        "createProgramIds": sorted(create_programs),
        "createResultIds": sorted(create_results),
    }
    return build_research_builder_v10_authoring_packet(
        state,
        claims,
        route,
        route_context=route_context,
        max_programs=24,
        max_results=24,
    )


def _validate_experiment(root: Path) -> dict[str, object]:
    path = root.joinpath(*EXPERIMENT_PATH.parts)
    value = _load_json(path, "experiment manifest")
    if not isinstance(value, dict):
        raise MathFlowError("joint holdout experiment manifest must be an object")
    required = {
        "schemaVersion", "id", "description", "problemId", "status",
        "publicationForbidden", "continue", "protocolBaseCommit", "validitySource",
        "validitySourceFileDigest", "rootContract", "rootContractFileDigest",
        "workJudgeSpec", "workJudgeSpecFileDigest", "workJudgeSpecDigest",
        "jointAuthorJudgeSpec", "jointAuthorJudgeSpecFileDigest",
        "jointAuthorJudgeSpecDigest", "subjects", "steps", "primaryGate",
        "holdoutPolicy",
    }
    if (
        set(value) != required
        or value.get("schemaVersion") != 1
        or value.get("problemId") != PROBLEM_ID
        or value.get("status") != "unpublished-experiment"
        or value.get("publicationForbidden") is not True
        or value.get("continue") is not False
        or value.get("subjects") != list(SUBJECTS)
        or value.get("steps") != list(STEP_PLAN)
        or not isinstance(value.get("protocolBaseCommit"), str)
        or not re.fullmatch(r"[0-9a-f]{40}", str(value["protocolBaseCommit"]))
        or not DIGEST.fullmatch(str(value.get("workJudgeSpecDigest", "")))
        or not DIGEST.fullmatch(str(value.get("jointAuthorJudgeSpecDigest", "")))
    ):
        raise MathFlowError("joint holdout experiment contract is invalid")
    for path_field, digest_field in (
        ("validitySource", "validitySourceFileDigest"),
        ("rootContract", "rootContractFileDigest"),
        ("workJudgeSpec", "workJudgeSpecFileDigest"),
        ("jointAuthorJudgeSpec", "jointAuthorJudgeSpecFileDigest"),
    ):
        relative = PurePosixPath(str(value[path_field]))
        if relative.is_absolute() or ".." in relative.parts:
            raise MathFlowError("joint holdout experiment path is unsafe")
        target = root.joinpath(*relative.parts)
        if file_digest(target) != value[digest_field]:
            raise MathFlowError(f"joint holdout {path_field} file binding mismatch")
    work_spec = _load_json(
        root.joinpath(*PurePosixPath(str(value["workJudgeSpec"])).parts),
        "work judge spec",
    )
    if _digest(work_spec) != value["workJudgeSpecDigest"]:
        raise MathFlowError("joint holdout work judge semantic digest mismatch")
    joint_spec = _load_json(
        root.joinpath(*PurePosixPath(str(value["jointAuthorJudgeSpec"])).parts),
        "joint author judge spec",
    )
    if _digest(joint_spec) != value["jointAuthorJudgeSpecDigest"]:
        raise MathFlowError("joint holdout author judge semantic digest mismatch")
    return copy.deepcopy(value)


def _materialize_cases(
    root: Path, *, experiment: Mapping[str, object], directory: Path
) -> tuple[dict[str, object], list[dict[str, object]]]:
    source_path = root.joinpath(
        *PurePosixPath(str(experiment["validitySource"])).parts
    )
    source = _load_json(source_path, "validity source")
    if not isinstance(source, dict):
        raise MathFlowError("joint holdout validity source is invalid")
    pins, accepted = _accepted_frontier(root, source)
    selected = accepted[:3]
    observed_plan = [
        {
            "ordinal": item["acceptedTransitionOrdinal"],
            "ledgerOrdinal": item["ledgerOrdinal"],
            "subjectTransactionId": item["subjectTransactionId"],
            "validityJudgmentId": item["judgmentId"],
            "validityRunDigest": item["judgmentRunDigest"],
        }
        for item in selected
    ]
    if observed_plan != list(STEP_PLAN):
        raise MathFlowError("joint holdout accepted frontier is stale or skipped")
    cases: list[dict[str, object]] = []
    for ordinal, entry in enumerate(selected, start=1):
        validity_dir = directory / f"k{ordinal}" / "validity"
        _materialize_validity_bundle(
            root,
            projection_commit=str(pins["projectionCommit"]),
            entry=entry,
            destination=validity_dir,
        )
        validity_manifest, judgment, run_digest = load_judgment_bundle(validity_dir)
        packet = json.loads(
            read_verified_artifact(
                validity_dir, validity_manifest, "judgment-dependency-packet"
            )
        )
        subject = SUBJECTS[ordinal - 1]
        if (
            run_digest != entry["judgmentRunDigest"]
            or judgment.get("judgmentId") != entry["judgmentId"]
            or judgment["subjects"] != [
                {"kind": "transaction", "id": subject, "ledgerPosition": ordinal + 2}
            ]
        ):
            raise MathFlowError("joint holdout validity identity binding mismatch")
        claims = _normalized_accepted_claims(judgment, packet)
        validity_claim_refs = accepted_claim_refs_from_validity(
            judgment, subject_transaction_id=subject
        )
        claim_refs = _semantic_claim_refs(
            claims,
            subject_transaction_id=subject,
            judgment_id=str(judgment["judgmentId"]),
        )
        transaction = next(
            item
            for item in load_source(root, PROBLEM_ID, subject)["transactions"]
            if item["transactionId"] == subject
        )
        evidence_manifest, evidence_chunks = manifest_submission_at(
            root,
            problem_id=PROBLEM_ID,
            subject_transaction_id=subject,
            contribution_path=str(transaction["path"]),
        )
        reconstructed = reconstruct_submission_evidence(
            evidence_manifest, evidence_chunks
        )
        evidence_files = tuple(
            SubmissionEvidenceFile(
                path=path, digest=sha256_bytes(content), content=content
            )
            for path, content in sorted(reconstructed.items())
        )
        cases.append(
            {
                "ordinal": ordinal,
                "subject": subject,
                "frontier": copy.deepcopy(entry),
                "validityDir": validity_dir,
                "validityManifest": validity_manifest,
                "validityRunDigest": run_digest,
                "judgment": judgment,
                "dependencyPacket": packet,
                "claims": claims,
                "claimRefs": claim_refs,
                "validityClaimRefs": validity_claim_refs,
                "evidenceManifest": evidence_manifest,
                "evidenceChunks": evidence_chunks,
                "evidenceFiles": evidence_files,
            }
        )
    return pins, cases


def _persist_validated_author_checkpoint(
    path: Path,
    *,
    author_result: Mapping[str, object],
    frozen: Mapping[str, object],
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.is_symlink():
        raise MathFlowError("joint holdout author checkpoint may not be a symlink")
    envelope = {
        "schemaVersion": 1,
        "authorResultDigest": author_result["resultDigest"],
        "frozenCandidateDigest": frozen["candidateDigest"],
        "authorResult": copy.deepcopy(dict(author_result)),
    }
    if path.is_file():
        observed = _load_json(path, "author checkpoint")
        if observed != envelope:
            raise MathFlowError("joint holdout author checkpoint binding mismatch")
        return
    temporary = path.with_suffix(".tmp")
    temporary.write_bytes(_json_bytes(envelope))
    temporary.replace(path)


def _load_author_checkpoint(path: Path) -> dict[str, object] | None:
    if not path.exists():
        return None
    if path.is_symlink() or not path.is_file():
        raise MathFlowError("joint holdout author checkpoint is unsafe")
    value = _load_json(path, "author checkpoint")
    if not isinstance(value, dict) or set(value) != {
        "schemaVersion", "authorResultDigest", "frozenCandidateDigest",
        "authorResult",
    }:
        raise MathFlowError("joint holdout author checkpoint envelope is invalid")
    author_result = value.get("authorResult")
    if (
        value.get("schemaVersion") != 1
        or not isinstance(author_result, dict)
        or value.get("authorResultDigest") != author_result.get("resultDigest")
    ):
        raise MathFlowError("joint holdout author checkpoint digest mismatch")
    return copy.deepcopy(value)


def _assert_k3_reuse_and_refresh(
    *,
    before_state: Mapping[str, object],
    joint: Mapping[str, object],
    evidence_manifest: Mapping[str, object],
) -> None:
    after = joint["postState"]
    if (
        joint["transition"]["topologyOperations"]
        or set(after["programs"]) != set(before_state["programs"])
        or set(after["intermediateResults"])
        != set(before_state["intermediateResults"])
        or joint["accountingAffectedProgramIds"] != [K2_PROGRAM, "root"]
    ):
        raise MathFlowError("joint holdout K3 in-place reuse gate failed")
    evidence_paths = {
        str(item["path"])
        for item in evidence_manifest["files"]
        if isinstance(item, Mapping)
    }
    for result_id in K2_RESULTS:
        before_result = before_state["intermediateResults"].get(result_id)
        after_result = after["intermediateResults"].get(result_id)
        if not isinstance(before_result, Mapping) or not isinstance(after_result, Mapping):
            raise MathFlowError("joint holdout K3 lost an exact K2 result")
        expected_sources = sorted(
            {*before_result["sourceTransactionIds"], SUBJECTS[2]}
        )
        artifact_paths = {
            str(item["path"])
            for item in after_result["support"]["artifactRefs"]
            if isinstance(item, Mapping)
        }
        if (
            after_result["sourceTransactionIds"] != expected_sources
            or not evidence_paths <= artifact_paths
        ):
            raise MathFlowError(
                "joint holdout K3 did not append canonical support to both K2 results"
            )
    # Generic author validation already requires a complete, evidence-backed
    # current-subject assessment for every affected program. Reassessment may
    # retain exactly the prior numbers, including zero on a completed package.


def run_bssc_joint_portfolio_serial_holdout_v1(
    *,
    root: Path,
    output_dir: Path,
    checkpoint_dir: Path,
    joint_author_provider: JointPortfolioSerialAuthorProvider,
    credit_provider: WorkProjectionProvider,
    continue_run: bool = False,
    publish: bool = False,
) -> dict[str, object]:
    """Run the exact unpublished three-subject chain and write one bundle."""

    if continue_run or publish:
        raise MathFlowError("joint holdout requires continue=false and forbids publication")
    root = root.resolve()
    experiment = _validate_experiment(root)
    joint_author_judge_spec_digest = str(experiment["jointAuthorJudgeSpecDigest"])
    contract_path = root.joinpath(
        *PurePosixPath(str(experiment["rootContract"])).parts
    )
    contract = validate_root_contract(_load_json(contract_path, "root contract"), PROBLEM_ID)
    validity_source_path = root.joinpath(
        *PurePosixPath(str(experiment["validitySource"])).parts
    )
    work_judge_spec_path = root.joinpath(
        *PurePosixPath(str(experiment["workJudgeSpec"])).parts
    )
    joint_author_judge_spec_path = root.joinpath(
        *PurePosixPath(str(experiment["jointAuthorJudgeSpec"])).parts
    )
    origin = empty_research_program_state_v3(PROBLEM_ID)
    accounting = make_zero_work_accounting_state(
        root_contract=contract, knowledge_state=origin
    )
    boundaries = make_joint_portfolio_boundary_state_v1(
        knowledge_state=origin, boundaries=[_root_boundary()]
    )
    checkpoint_dir = checkpoint_dir.resolve()
    checkpoint_dir.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="math-flow-joint-holdout-") as temporary:
        pins, cases = _materialize_cases(
            root, experiment=experiment, directory=Path(temporary)
        )
        state = origin
        step_results: list[dict[str, object]] = []
        for case in cases:
            ordinal = int(case["ordinal"])
            subject = str(case["subject"])
            claims = case["claims"]
            semantic = _semantic_packet(
                ordinal=ordinal,
                state=state,
                claims=claims,
                evidence_manifest=case["evidenceManifest"],
                evidence_files=case["evidenceFiles"],
                dependency_packet=case["dependencyPacket"],
            )
            authoring = _authoring_packet(
                ordinal=ordinal, state=state, claims=claims
            )
            author_checkpoint_path = checkpoint_dir / f"k{ordinal}" / "validated-author.json"
            checkpoint = _load_author_checkpoint(author_checkpoint_path)
            if checkpoint is None:
                authored = run_joint_portfolio_serial_author_v2(
                    provider=joint_author_provider,
                    problem_id=PROBLEM_ID,
                    subject_transaction_id=subject,
                    base_state=state,
                    base_accounting_state=accounting,
                    base_boundary_state=boundaries,
                    root_contract=contract,
                    semantic_packet=semantic,
                    authoring_packet=authoring,
                    accepted_claims=claims,
                    judgment_id=str(case["judgment"]["judgmentId"]),
                    judge_spec_digest=joint_author_judge_spec_digest,
                    evidence_files=case["evidenceFiles"],
                )
            else:
                authored = checkpoint["authorResult"]
            authored = validate_joint_portfolio_serial_author_replay_v2(
                authored,
                problem_id=PROBLEM_ID,
                subject_transaction_id=subject,
                base_state=state,
                base_accounting_state=accounting,
                base_boundary_state=boundaries,
                root_contract=contract,
                semantic_packet=semantic,
                authoring_packet=authoring,
                accepted_claims=claims,
                judgment_id=str(case["judgment"]["judgmentId"]),
                judge_spec_digest=joint_author_judge_spec_digest,
                evidence_files=case["evidenceFiles"],
            )
            request, response, joint = (
                authored["request"], authored["response"], authored["reduced"]
            )
            frozen = validate_joint_portfolio_serial_frozen_wplus_v2(
                _frozen(contract, joint)
            )
            if checkpoint is not None and checkpoint["frozenCandidateDigest"] != frozen["candidateDigest"]:
                raise MathFlowError("joint holdout frozen W+ checkpoint binding mismatch")
            if ordinal == 3:
                _assert_k3_reuse_and_refresh(
                    before_state=state,
                    joint=joint,
                    evidence_manifest=case["evidenceManifest"],
                )
            _persist_validated_author_checkpoint(
                author_checkpoint_path,
                author_result=authored,
                frozen=frozen,
            )
            credit = run_joint_portfolio_serial_credit_v2(
                provider=credit_provider,
                subject_transaction_id=subject,
                root_contract=contract,
                base_knowledge_state=state,
                base_accounting_state=accounting,
                base_boundary_state=boundaries,
                joint_response=response,
                semantic_packet=semantic,
                authoring_packet=authoring,
                accepted_claims=claims,
                accepted_claim_refs=case["claimRefs"],
                judgment_id=str(case["judgment"]["judgmentId"]),
                evidence_manifest=case["evidenceManifest"],
                evidence_chunks=case["evidenceChunks"],
                expected_frozen_candidate=frozen,
                checkpoint_dir=checkpoint_dir / f"k{ordinal}" / "credit",
                descendant_depth=1,
            )
            if credit["jointArtifacts"] != joint:
                raise MathFlowError("joint holdout credit changed the frozen joint reduction")
            step_results.append(
                {
                    "case": case,
                    "semanticPacket": semantic,
                    "authoringPacket": authoring,
                    "authorRequest": request,
                    "authorResponse": response,
                    "authorResult": authored,
                    "joint": joint,
                    "credit": credit,
                }
            )
            state = joint["postState"]
            accounting = joint["withAccessState"]
            boundaries = joint["boundaryState"]

        output_dir = output_dir.resolve()
        bundle = ArtifactBundle(output_dir)
        bundle.add_json("input/experiment.json", experiment, "joint-holdout-experiment")
        bundle.add_bytes(
            "input/root-contract.json",
            contract_path.read_bytes(),
            "joint-holdout-root-contract",
            "application/json",
        )
        bundle.add_bytes(
            "input/validity-source.json",
            validity_source_path.read_bytes(),
            "joint-holdout-validity-source",
            "application/json",
        )
        bundle.add_bytes(
            "input/work-judge-spec.json",
            work_judge_spec_path.read_bytes(),
            "joint-holdout-work-judge-spec",
            "application/json",
        )
        bundle.add_bytes(
            "input/joint-author-judge-spec.json",
            joint_author_judge_spec_path.read_bytes(),
            "joint-holdout-joint-author-judge-spec",
            "application/json",
        )
        bundle.add_json("state/k0/knowledge.json", origin, "joint-holdout-k0-knowledge")
        bundle.add_json("state/k0/accounting.json", make_zero_work_accounting_state(root_contract=contract, knowledge_state=origin), "joint-holdout-k0-accounting")
        bundle.add_json("state/k0/boundaries.json", make_joint_portfolio_boundary_state_v1(knowledge_state=origin, boundaries=[_root_boundary()]), "joint-holdout-k0-boundaries")
        step_bindings: list[dict[str, object]] = []
        for step in step_results:
            case = step["case"]
            ordinal = int(case["ordinal"])
            prefix = f"steps/k{ordinal}"
            validity_dir = Path(case["validityDir"])
            for filename, role in (
                ("run.json", "run"),
                ("judgment.json", "judgment"),
                ("dependency-packet.json", "dependency-packet"),
                ("report.md", "report"),
            ):
                source = validity_dir / filename
                media = "application/json" if filename.endswith(".json") else "text/markdown"
                bundle.add_bytes(
                    f"{prefix}/validity/{filename}",
                    source.read_bytes(),
                    f"joint-holdout-k{ordinal}-validity-{role}",
                    media,
                )
            for path, value, role in (
                ("input/accepted-claims.json", case["claims"], "accepted-claims"),
                ("input/accepted-claim-refs.json", case["claimRefs"], "accepted-claim-refs"),
                ("input/validity-claim-refs.json", case["validityClaimRefs"], "validity-claim-refs"),
                ("input/evidence-manifest.json", case["evidenceManifest"], "evidence-manifest"),
                ("input/semantic-packet.json", step["semanticPacket"], "semantic-packet"),
                ("input/authoring-packet.json", step["authoringPacket"], "authoring-packet"),
                ("author/request.json", step["authorRequest"], "author-request"),
                ("author/response.json", step["authorResponse"], "author-response"),
                ("author/replay.json", step["authorResult"], "author-replay"),
                ("author/reduction.json", step["joint"], "joint-reduction"),
                ("credit/frozen-wplus.json", step["credit"]["jointWithAccessCandidate"], "frozen-wplus"),
            ):
                bundle.add_json(f"{prefix}/{path}", value, f"joint-holdout-k{ordinal}-{role}")
            for digest, content in sorted(case["evidenceChunks"].items()):
                bundle.add_bytes(
                    f"{prefix}/input/evidence/chunks/{str(digest).removeprefix('sha256:')}.bin",
                    content,
                    f"joint-holdout-k{ordinal}-evidence-chunk",
                    "application/octet-stream",
                )
            credit = step["credit"]
            for name in CREDIT_ARTIFACT_NAMES:
                bundle.add_json(
                    f"{prefix}/credit/{name}.json",
                    credit[name],
                    f"joint-holdout-k{ordinal}-{name}",
                )
            joint = step["joint"]
            credit_candidate = credit["creditCandidate"]
            step_bindings.append(
                {
                    "ordinal": ordinal,
                    "subjectTransactionId": case["subject"],
                    "validityRunDigest": case["validityRunDigest"],
                    "validityJudgmentId": case["judgment"]["judgmentId"],
                    "validityJudgeSpecDigest": case["judgment"]["judgeSpec"]["digest"],
                    "acceptedClaimsDigest": _digest(case["claims"]),
                    "acceptedClaimRefsDigest": _digest(case["claimRefs"]),
                    "validityClaimRefsDigest": _digest(case["validityClaimRefs"]),
                    "evidenceManifestDigest": case["evidenceManifest"]["manifestDigest"],
                    "baseKnowledgeStateDigest": joint["transition"]["baseStateDigest"],
                    "baseAccountingStateDigest": joint["withAccessPatch"]["baseAccountingStateDigest"],
                    "baseBoundaryStateDigest": joint["response"]["baseBoundaryStateDigest"],
                    "semanticPacketDigest": step["semanticPacket"]["packetDigest"],
                    "authoringPacketDigest": step["authoringPacket"]["authoringPacketDigest"],
                    "authorRequestDigest": _digest(step["authorRequest"]),
                    "sealedAuthorRequestDigest": step["authorRequest"]["requestDigest"],
                    "authorResponseDigest": _digest(step["authorResponse"]),
                    "authorResultDigest": step["authorResult"]["resultDigest"],
                    "jointReductionDigest": _digest(joint),
                    "postKnowledgeStateDigest": joint["postState"]["stateDigest"],
                    "targetBoundaryStateDigest": joint["boundaryState"]["stateDigest"],
                    "frozenWithAccessCandidateDigest": credit["jointWithAccessCandidate"]["candidateDigest"],
                    "withAccessStateDigest": credit["withAccessState"]["stateDigest"],
                    "safeRequestDigest": credit["safeRequest"]["requestDigest"],
                    "safeResponseDigest": _digest(credit["safeResponse"]),
                    "safeFactsDigest": credit["safeFacts"]["safeFactsDigest"],
                    "noAccessRequestDigest": credit["noAccessRequest"]["requestDigest"],
                    "noAccessResponseDigest": _digest(credit["noAccessResponse"]),
                    "noAccessPatchDigest": credit["noAccessPatch"]["patchDigest"],
                    "noAccessStateDigest": credit["noAccessState"]["stateDigest"],
                    "evaluationDigest": credit["evaluation"]["evaluationDigest"],
                    "creditCandidateDigest": credit_candidate["candidateDigest"],
                }
            )
        graph_core = {
            "experimentDigest": _digest(experiment),
            "rootContractDigest": contract["rootContractDigest"],
            "initialKnowledgeStateDigest": origin["stateDigest"],
            "jointAuthorJudgeSpecDigest": joint_author_judge_spec_digest,
            "workJudgeSpecDigest": experiment["workJudgeSpecDigest"],
            "stepBindings": step_bindings,
        }
        envelope = {
            "protocolVersion": 1,
            "runKind": "joint-portfolio-serial-holdout",
            "outputProfile": PROFILE,
            "problemId": PROBLEM_ID,
            "publicationForbidden": True,
            "continue": False,
            "protocolBaseCommit": experiment["protocolBaseCommit"],
            "validitySourceMainCommit": pins["mainCommit"],
            "validityProjectionCommit": pins["projectionCommit"],
            **graph_core,
            "graphDigest": _digest(graph_core),
            "terminalKnowledgeStateDigest": state["stateDigest"],
            "terminalAccountingStateDigest": accounting["stateDigest"],
            "terminalBoundaryStateDigest": boundaries["stateDigest"],
        }
        bundle.finalize(envelope)
    return load_bssc_joint_portfolio_serial_holdout_bundle_v1(output_dir)


def _artifact_entry(manifest: Mapping[str, object], role: str) -> Mapping[str, object]:
    matches = [item for item in manifest["artifacts"] if item.get("role") == role]
    if len(matches) != 1:
        raise MathFlowError(f"joint holdout bundle must contain one {role} artifact")
    return matches[0]


def _expected_static_artifacts() -> dict[str, str]:
    expected = {
        "joint-holdout-experiment": "input/experiment.json",
        "joint-holdout-root-contract": "input/root-contract.json",
        "joint-holdout-validity-source": "input/validity-source.json",
        "joint-holdout-work-judge-spec": "input/work-judge-spec.json",
        "joint-holdout-joint-author-judge-spec": (
            "input/joint-author-judge-spec.json"
        ),
        "joint-holdout-k0-knowledge": "state/k0/knowledge.json",
        "joint-holdout-k0-accounting": "state/k0/accounting.json",
        "joint-holdout-k0-boundaries": "state/k0/boundaries.json",
    }
    for ordinal in range(1, 4):
        prefix = f"steps/k{ordinal}"
        for filename, suffix in (
            ("run.json", "run"),
            ("judgment.json", "judgment"),
            ("dependency-packet.json", "dependency-packet"),
            ("report.md", "report"),
        ):
            expected[f"joint-holdout-k{ordinal}-validity-{suffix}"] = (
                f"{prefix}/validity/{filename}"
            )
        for path, suffix in (
            ("input/accepted-claims.json", "accepted-claims"),
            ("input/accepted-claim-refs.json", "accepted-claim-refs"),
            ("input/validity-claim-refs.json", "validity-claim-refs"),
            ("input/evidence-manifest.json", "evidence-manifest"),
            ("input/semantic-packet.json", "semantic-packet"),
            ("input/authoring-packet.json", "authoring-packet"),
            ("author/request.json", "author-request"),
            ("author/response.json", "author-response"),
            ("author/replay.json", "author-replay"),
            ("author/reduction.json", "joint-reduction"),
            ("credit/frozen-wplus.json", "frozen-wplus"),
        ):
            expected[f"joint-holdout-k{ordinal}-{suffix}"] = f"{prefix}/{path}"
        for name in CREDIT_ARTIFACT_NAMES:
            expected[f"joint-holdout-k{ordinal}-{name}"] = (
                f"{prefix}/credit/{name}.json"
            )
    return expected


def _validate_artifact_index(manifest: Mapping[str, object]) -> None:
    artifacts = manifest.get("artifacts")
    if not isinstance(artifacts, list):
        raise MathFlowError("joint holdout bundle has no artifact index")
    expected = _expected_static_artifacts()
    observed: dict[str, str] = {}
    for raw in artifacts:
        if (
            not isinstance(raw, dict)
            or set(raw) != ARTIFACT_FIELDS
            or not DIGEST.fullmatch(str(raw.get("digest", "")))
            or isinstance(raw.get("bytes"), bool)
            or not isinstance(raw.get("bytes"), int)
            or raw["bytes"] < 0
        ):
            raise MathFlowError("joint holdout artifact index entry is invalid")
        role, path = str(raw.get("role", "")), str(raw.get("path", ""))
        if role.endswith("-evidence-chunk"):
            if role not in {
                f"joint-holdout-k{ordinal}-evidence-chunk"
                for ordinal in range(1, 4)
            }:
                raise MathFlowError("joint holdout evidence chunk role is invalid")
            continue
        if role in observed:
            raise MathFlowError("joint holdout static artifact role is duplicated")
        observed[role] = path
    if observed != expected:
        raise MathFlowError("joint holdout static artifact graph is incomplete or substituted")


def _artifact_bytes(bundle: Path, entry: Mapping[str, object]) -> bytes:
    relative = PurePosixPath(str(entry.get("path", "")))
    if relative.is_absolute() or not relative.parts or ".." in relative.parts:
        raise MathFlowError("joint holdout artifact path is unsafe")
    target = bundle.joinpath(*relative.parts).resolve()
    try:
        target.relative_to(bundle)
    except ValueError as error:
        raise MathFlowError("joint holdout artifact escapes its bundle") from error
    return target.read_bytes()


def _json_role(bundle: Path, manifest: Mapping[str, object], role: str) -> object:
    raw = _artifact_bytes(bundle, _artifact_entry(manifest, role))
    try:
        value = json.loads(raw)
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise MathFlowError(f"joint holdout {role} artifact is invalid JSON") from error
    if raw != _json_bytes(value):
        raise MathFlowError(f"joint holdout {role} artifact is not canonical JSON")
    return value


def _pinned_json_role(
    bundle: Path, manifest: Mapping[str, object], role: str
) -> object:
    raw = _artifact_bytes(bundle, _artifact_entry(manifest, role))
    try:
        return json.loads(raw)
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise MathFlowError(f"joint holdout {role} artifact is invalid JSON") from error


def _evidence_chunks(
    bundle: Path, manifest: Mapping[str, object], ordinal: int
) -> dict[str, bytes]:
    role = f"joint-holdout-k{ordinal}-evidence-chunk"
    chunks: dict[str, bytes] = {}
    for entry in manifest["artifacts"]:
        if entry.get("role") != role:
            continue
        digest = str(entry.get("digest"))
        expected = f"steps/k{ordinal}/input/evidence/chunks/{digest.removeprefix('sha256:')}.bin"
        if entry.get("path") != expected or digest in chunks:
            raise MathFlowError("joint holdout evidence chunk index is not canonical")
        chunks[digest] = _artifact_bytes(bundle, entry)
    return chunks


def _load_nested_validity(
    bundle: Path, manifest: Mapping[str, object], ordinal: int
) -> tuple[dict[str, object], dict[str, object], dict[str, object], str]:
    validity_dir = bundle / f"steps/k{ordinal}/validity"
    expected_roles = {
        f"joint-holdout-k{ordinal}-validity-{suffix}"
        for suffix in ("run", "judgment", "dependency-packet", "report")
    }
    for role in expected_roles:
        _artifact_entry(manifest, role)
    verify_bundle(validity_dir)
    inner_manifest, judgment, run_digest = load_judgment_bundle(validity_dir)
    packet = json.loads(
        read_verified_artifact(
            validity_dir, inner_manifest, "judgment-dependency-packet"
        )
    )
    return inner_manifest, judgment, packet, run_digest


def load_bssc_joint_portfolio_serial_holdout_bundle_v1(
    bundle_dir: Path, *, expected_bundle_digest: str | None = None
) -> dict[str, object]:
    """Byte-verify and re-reduce the complete serial holdout graph."""

    bundle = bundle_dir.resolve()
    manifest, bundle_digest = verify_bundle(bundle)
    if expected_bundle_digest is not None and bundle_digest != expected_bundle_digest:
        raise MathFlowError("joint holdout bundle does not match its content address")
    if (
        manifest.get("runKind") != "joint-portfolio-serial-holdout"
        or manifest.get("outputProfile") != PROFILE
        or manifest.get("problemId") != PROBLEM_ID
        or manifest.get("publicationForbidden") is not True
        or manifest.get("continue") is not False
        or not isinstance(manifest.get("artifacts"), list)
        or manifest["artifacts"] != sorted(manifest["artifacts"], key=lambda item: str(item["path"]))
    ):
        raise MathFlowError("joint holdout bundle manifest is invalid")
    _validate_artifact_index(manifest)
    experiment = _json_role(bundle, manifest, "joint-holdout-experiment")
    if (
        not isinstance(experiment, dict)
        or experiment.get("subjects") != list(SUBJECTS)
        or experiment.get("steps") != list(STEP_PLAN)
        or experiment.get("publicationForbidden") is not True
        or experiment.get("continue") is not False
        or manifest.get("protocolBaseCommit") != experiment.get("protocolBaseCommit")
        or manifest.get("workJudgeSpecDigest") != experiment.get("workJudgeSpecDigest")
        or manifest.get("jointAuthorJudgeSpecDigest")
        != experiment.get("jointAuthorJudgeSpecDigest")
        or not re.fullmatch(
            r"[0-9a-f]{40}", str(manifest.get("validitySourceMainCommit", ""))
        )
        or not re.fullmatch(
            r"[0-9a-f]{40}", str(manifest.get("validityProjectionCommit", ""))
        )
    ):
        raise MathFlowError("joint holdout experiment artifact is invalid")
    validity_source = _pinned_json_role(
        bundle, manifest, "joint-holdout-validity-source"
    )
    work_judge_spec = _pinned_json_role(
        bundle, manifest, "joint-holdout-work-judge-spec"
    )
    joint_author_judge_spec = _pinned_json_role(
        bundle, manifest, "joint-holdout-joint-author-judge-spec"
    )
    if (
        _artifact_entry(manifest, "joint-holdout-validity-source").get("digest")
        != experiment.get("validitySourceFileDigest")
        or not isinstance(validity_source, dict)
        or validity_source.get("problemId") != PROBLEM_ID
        or validity_source.get("mainCommit")
        != manifest.get("validitySourceMainCommit")
        or validity_source.get("projectionCommit")
        != manifest.get("validityProjectionCommit")
        or _artifact_entry(manifest, "joint-holdout-work-judge-spec").get(
            "digest"
        )
        != experiment.get("workJudgeSpecFileDigest")
        or _digest(work_judge_spec) != experiment.get("workJudgeSpecDigest")
        or _artifact_entry(
            manifest, "joint-holdout-joint-author-judge-spec"
        ).get("digest")
        != experiment.get("jointAuthorJudgeSpecFileDigest")
        or _digest(joint_author_judge_spec)
        != experiment.get("jointAuthorJudgeSpecDigest")
        or _artifact_entry(manifest, "joint-holdout-root-contract").get("digest")
        != experiment.get("rootContractFileDigest")
    ):
        raise MathFlowError("joint holdout bound protocol input does not replay")
    contract = validate_root_contract(
        _pinned_json_role(bundle, manifest, "joint-holdout-root-contract"),
        PROBLEM_ID,
    )
    state = _json_role(bundle, manifest, "joint-holdout-k0-knowledge")
    accounting = _json_role(bundle, manifest, "joint-holdout-k0-accounting")
    boundaries = _json_role(bundle, manifest, "joint-holdout-k0-boundaries")
    expected_origin = empty_research_program_state_v3(PROBLEM_ID)
    if state != expected_origin:
        raise MathFlowError("joint holdout K0 knowledge state is not reproducible")
    if accounting != make_zero_work_accounting_state(root_contract=contract, knowledge_state=state):
        raise MathFlowError("joint holdout K0 accounting state is not reproducible")
    if boundaries != make_joint_portfolio_boundary_state_v1(knowledge_state=state, boundaries=[_root_boundary()]):
        raise MathFlowError("joint holdout K0 boundary state is not reproducible")
    raw_bindings = manifest.get("stepBindings")
    if not isinstance(raw_bindings, list) or [raw.get("subjectTransactionId") if isinstance(raw, dict) else None for raw in raw_bindings] != list(SUBJECTS):
        raise MathFlowError("joint holdout serial frontier is truncated, reordered, or skipped")
    replayed_steps: list[dict[str, object]] = []
    for ordinal, binding in enumerate(raw_bindings, start=1):
        if not isinstance(binding, dict) or binding.get("ordinal") != ordinal:
            raise MathFlowError("joint holdout step order is invalid")
        _, judgment, packet, validity_run_digest = _load_nested_validity(
            bundle, manifest, ordinal
        )
        subject = SUBJECTS[ordinal - 1]
        if (
            validity_run_digest != binding.get("validityRunDigest")
            or judgment.get("judgmentId") != binding.get("validityJudgmentId")
            or judgment.get("judgeSpec", {}).get("digest") != binding.get("validityJudgeSpecDigest")
            or judgment.get("subjects") != [{"kind": "transaction", "id": subject, "ledgerPosition": ordinal + 2}]
        ):
            raise MathFlowError("joint holdout validity binding mismatch")
        claims = _normalized_accepted_claims(judgment, packet)
        validity_claim_refs = accepted_claim_refs_from_validity(
            judgment, subject_transaction_id=subject
        )
        claim_refs = _semantic_claim_refs(
            claims,
            subject_transaction_id=subject,
            judgment_id=str(judgment["judgmentId"]),
        )
        if (
            claims != _json_role(bundle, manifest, f"joint-holdout-k{ordinal}-accepted-claims")
            or claim_refs != _json_role(bundle, manifest, f"joint-holdout-k{ordinal}-accepted-claim-refs")
            or validity_claim_refs != _json_role(bundle, manifest, f"joint-holdout-k{ordinal}-validity-claim-refs")
            or _digest(claims) != binding.get("acceptedClaimsDigest")
            or _digest(claim_refs) != binding.get("acceptedClaimRefsDigest")
            or _digest(validity_claim_refs) != binding.get("validityClaimRefsDigest")
        ):
            raise MathFlowError("joint holdout accepted validity data does not replay")
        evidence_manifest = validate_submission_evidence_manifest(
            _json_role(bundle, manifest, f"joint-holdout-k{ordinal}-evidence-manifest")
        )
        chunks = _evidence_chunks(bundle, manifest, ordinal)
        reconstructed = reconstruct_submission_evidence(evidence_manifest, chunks)
        evidence_files = tuple(
            SubmissionEvidenceFile(path=path, digest=sha256_bytes(content), content=content)
            for path, content in sorted(reconstructed.items())
        )
        if evidence_manifest["manifestDigest"] != binding.get("evidenceManifestDigest"):
            raise MathFlowError("joint holdout evidence manifest binding mismatch")
        semantic = _json_role(bundle, manifest, f"joint-holdout-k{ordinal}-semantic-packet")
        authoring = _json_role(bundle, manifest, f"joint-holdout-k{ordinal}-authoring-packet")
        request = _json_role(bundle, manifest, f"joint-holdout-k{ordinal}-author-request")
        response = _json_role(bundle, manifest, f"joint-holdout-k{ordinal}-author-response")
        author_result = _json_role(
            bundle, manifest, f"joint-holdout-k{ordinal}-author-replay"
        )
        author_result = validate_joint_portfolio_serial_author_replay_v2(
            author_result,
            problem_id=PROBLEM_ID,
            subject_transaction_id=subject,
            base_state=state,
            base_accounting_state=accounting,
            base_boundary_state=boundaries,
            root_contract=contract,
            semantic_packet=semantic,
            authoring_packet=authoring,
            accepted_claims=claims,
            judgment_id=str(judgment["judgmentId"]),
            judge_spec_digest=str(experiment["jointAuthorJudgeSpecDigest"]),
            evidence_files=evidence_files,
        )
        joint = author_result["reduced"]
        stored_joint = _json_role(bundle, manifest, f"joint-holdout-k{ordinal}-joint-reduction")
        if (
            request != author_result["request"]
            or response != author_result["response"]
            or joint != stored_joint
        ):
            raise MathFlowError("joint holdout author graph does not replay exactly")
        frozen = validate_joint_portfolio_serial_frozen_wplus_v2(
            _frozen(contract, joint)
        )
        stored_frozen = _json_role(bundle, manifest, f"joint-holdout-k{ordinal}-frozen-wplus")
        if frozen != stored_frozen:
            raise MathFlowError("joint holdout frozen W+ does not replay")
        safe_request = _json_role(bundle, manifest, f"joint-holdout-k{ordinal}-safeRequest")
        safe_response = _json_role(bundle, manifest, f"joint-holdout-k{ordinal}-safeResponse")
        safe_facts = build_counterfactual_safe_facts(
            problem_id=PROBLEM_ID,
            subject_transaction_id=subject,
            accepted_claim_refs=claim_refs,
            research_state=joint["postState"],
            evidence_manifest=evidence_manifest,
            evidence_chunks=chunks,
            extracted=safe_response,
        )
        stored_safe = _json_role(bundle, manifest, f"joint-holdout-k{ordinal}-safeFacts")
        if safe_facts != stored_safe:
            raise MathFlowError("joint holdout safe facts do not replay")
        transition = _validate_transition(
            subject_transaction_id=subject,
            root_contract=contract,
            base_knowledge_state=state,
            target_knowledge_state=joint["postState"],
            base_accounting_state=accounting,
            topology_alignment=joint["topologyAlignment"],
            evidence_manifest=evidence_manifest,
            evidence_chunks=chunks,
            accepted_claim_refs=claim_refs,
        )
        _, _, before, after, base, alignment, _, bound_refs = transition
        bindings = _bindings(
            contract=contract, base=base, before=before, after=after,
            alignment=alignment, manifest=evidence_manifest,
            accepted_claim_refs=bound_refs,
        )
        expected_safe_request = _make_work_request(
            stage="safe-facts", problem_id=PROBLEM_ID,
            subject_transaction_id=subject, bindings=bindings,
            root_contract=contract, base_accounting_state=base,
            topology_alignment=alignment, required_updates=[],
            stage_input=_safe_fact_stage_input(
                accepted_claim_refs=bound_refs,
                target_knowledge_state=after,
                evidence_manifest=evidence_manifest,
            ),
            profile=PROFILE_V2,
        )
        if safe_request != expected_safe_request:
            raise MathFlowError("joint holdout safe-fact request does not replay")
        required = _required_primitive_updates(before, after, base, evaluation_mode="no-access")
        context = build_impact_subgraph_context(
            problem_id=PROBLEM_ID,
            subject_transaction_id=subject,
            accepted_claim_refs=bound_refs,
            research_state=after,
            seed_node_refs=_joint_impact_seeds(
                safe_facts, joint["accountingAffectedProgramIds"]
            ),
            descendant_depth=1,
        )
        if context != _json_role(bundle, manifest, f"joint-holdout-k{ordinal}-impactContext"):
            raise MathFlowError("joint holdout impact context does not replay")
        _ensure_required_context_coverage(required, context)
        policy = build_joint_portfolio_no_access_policy_context_v1(
            base_boundary_state=boundaries,
            base_knowledge_state=before,
            target_knowledge_state=after,
            impact_context=context,
        )
        if policy != _json_role(bundle, manifest, f"joint-holdout-k{ordinal}-noAccessPolicyContext"):
            raise MathFlowError("joint holdout no-access policy does not replay")
        no_input = _build_joint_no_access_input(
            safe_facts=safe_facts,
            impact_context=context,
            research_state=after,
            frozen_with_access_state=joint["withAccessState"],
            frozen_with_access_candidate_digest=str(frozen["candidateDigest"]),
            policy_context=policy,
        )
        if no_input != _json_role(bundle, manifest, f"joint-holdout-k{ordinal}-noAccessInput"):
            raise MathFlowError("joint holdout no-access input does not replay")
        no_request = _make_joint_no_access_request(
            problem_id=PROBLEM_ID,
            subject_transaction_id=subject,
            bindings=bindings,
            root_contract=contract,
            base_accounting_state=base,
            topology_alignment=alignment,
            required_updates=required,
            stage_input=no_input,
        )
        if no_request != _json_role(bundle, manifest, f"joint-holdout-k{ordinal}-noAccessRequest"):
            raise MathFlowError("joint holdout no-access request does not replay")
        _assert_no_access_evidence_structure(no_request)
        no_response = _json_role(bundle, manifest, f"joint-holdout-k{ordinal}-noAccessResponse")
        no_patch = _patch_from_response(
            no_response,
            mode="no-access",
            problem_id=PROBLEM_ID,
            subject_transaction_id=subject,
            bindings=bindings,
            base_accounting_state=base,
            required_updates=required,
            impact_context=context,
        )
        if no_patch != _json_role(bundle, manifest, f"joint-holdout-k{ordinal}-noAccessPatch"):
            raise MathFlowError("joint holdout no-access patch does not replay")
        no_state, with_state, evaluation = materialize_submission_work_value(
            base_state=base,
            no_access_patch=no_patch,
            with_access_patch=joint["withAccessPatch"],
            root_contract=contract,
            base_knowledge_state=before,
            target_knowledge_state=after,
            topology_alignment=alignment,
        )
        if (
            no_state != _json_role(bundle, manifest, f"joint-holdout-k{ordinal}-noAccessState")
            or with_state != _json_role(bundle, manifest, f"joint-holdout-k{ordinal}-withAccessState")
            or joint["withAccessPatch"] != _json_role(bundle, manifest, f"joint-holdout-k{ordinal}-withAccessPatch")
            or evaluation != _json_role(bundle, manifest, f"joint-holdout-k{ordinal}-evaluation")
        ):
            raise MathFlowError("joint holdout materialized work graph does not replay")
        credit = _json_role(bundle, manifest, f"joint-holdout-k{ordinal}-creditCandidate")
        validate_joint_portfolio_serial_credit_replay_v2(
            credit,
            accepted_claim_refs=bound_refs,
            base_boundary_state=boundaries,
            base_knowledge_state=before,
            target_knowledge_state=after,
            impact_context=context,
            no_access_policy_context=policy,
            no_access_request=no_request,
            no_access_state=no_state,
            with_access_state=with_state,
            no_access_patch=no_patch,
            with_access_patch=joint["withAccessPatch"],
        )
        expected_binding = {
            "ordinal": ordinal,
            "subjectTransactionId": subject,
            "validityRunDigest": validity_run_digest,
            "validityJudgmentId": judgment["judgmentId"],
            "validityJudgeSpecDigest": judgment["judgeSpec"]["digest"],
            "acceptedClaimsDigest": _digest(claims),
            "acceptedClaimRefsDigest": _digest(claim_refs),
            "validityClaimRefsDigest": _digest(validity_claim_refs),
            "evidenceManifestDigest": evidence_manifest["manifestDigest"],
            "baseKnowledgeStateDigest": joint["transition"]["baseStateDigest"],
            "baseAccountingStateDigest": joint["withAccessPatch"]["baseAccountingStateDigest"],
            "baseBoundaryStateDigest": joint["response"]["baseBoundaryStateDigest"],
            "semanticPacketDigest": semantic["packetDigest"],
            "authoringPacketDigest": authoring["authoringPacketDigest"],
            "authorRequestDigest": _digest(request),
            "sealedAuthorRequestDigest": request["requestDigest"],
            "authorResponseDigest": _digest(response),
            "authorResultDigest": author_result["resultDigest"],
            "jointReductionDigest": _digest(joint),
            "postKnowledgeStateDigest": joint["postState"]["stateDigest"],
            "targetBoundaryStateDigest": joint["boundaryState"]["stateDigest"],
            "frozenWithAccessCandidateDigest": frozen["candidateDigest"],
            "withAccessStateDigest": with_state["stateDigest"],
            "safeRequestDigest": safe_request["requestDigest"],
            "safeResponseDigest": _digest(safe_response),
            "safeFactsDigest": safe_facts["safeFactsDigest"],
            "noAccessRequestDigest": no_request["requestDigest"],
            "noAccessResponseDigest": _digest(no_response),
            "noAccessPatchDigest": no_patch["patchDigest"],
            "noAccessStateDigest": no_state["stateDigest"],
            "evaluationDigest": evaluation["evaluationDigest"],
            "creditCandidateDigest": credit["candidateDigest"],
        }
        if binding != expected_binding:
            raise MathFlowError("joint holdout step binding does not match replay")
        if ordinal == 3:
            _assert_k3_reuse_and_refresh(
                before_state=before,
                joint=joint,
                evidence_manifest=evidence_manifest,
            )
        replayed_steps.append(
            {
                "binding": expected_binding,
                "authorResult": author_result,
                "joint": joint,
                "creditCandidate": credit,
            }
        )
        state, accounting, boundaries = after, with_state, joint["boundaryState"]
    graph_core = {
        "experimentDigest": _digest(experiment),
        "rootContractDigest": contract["rootContractDigest"],
        "initialKnowledgeStateDigest": expected_origin["stateDigest"],
        "jointAuthorJudgeSpecDigest": manifest.get("jointAuthorJudgeSpecDigest"),
        "workJudgeSpecDigest": experiment["workJudgeSpecDigest"],
        "stepBindings": [item["binding"] for item in replayed_steps],
    }
    if (
        manifest.get("graphDigest") != _digest(graph_core)
        or manifest.get("experimentDigest") != graph_core["experimentDigest"]
        or manifest.get("rootContractDigest") != graph_core["rootContractDigest"]
        or manifest.get("initialKnowledgeStateDigest") != graph_core["initialKnowledgeStateDigest"]
        or manifest.get("workJudgeSpecDigest") != graph_core["workJudgeSpecDigest"]
        or manifest.get("terminalKnowledgeStateDigest") != state["stateDigest"]
        or manifest.get("terminalAccountingStateDigest") != accounting["stateDigest"]
        or manifest.get("terminalBoundaryStateDigest") != boundaries["stateDigest"]
    ):
        raise MathFlowError("joint holdout terminal graph binding mismatch")
    return {
        "manifest": manifest,
        "bundleDigest": bundle_digest,
        "rootContract": contract,
        "steps": replayed_steps,
        "terminalKnowledgeState": state,
        "terminalAccountingState": accounting,
        "terminalBoundaryState": boundaries,
    }


__all__ = [
    "PROFILE",
    "SUBJECTS",
    "load_bssc_joint_portfolio_serial_holdout_bundle_v1",
    "run_bssc_joint_portfolio_serial_holdout_v1",
]
