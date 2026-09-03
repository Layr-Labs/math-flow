"""Complete a generalized joint serial transition with W- and submission credit.

This inactive adapter treats the reducer-authored joint knowledge/W+ transition
as immutable authority.  It invokes only counterfactual-safe fact extraction
and W- estimation, then derives positive D and its additive node explanation in
trusted code.  It has no publication, scheduling, or provider configuration.
"""

from __future__ import annotations

import copy
import re
from collections.abc import Mapping, Sequence
from fractions import Fraction
from pathlib import Path

from math_flow.counterfactual_context import (
    build_counterfactual_safe_facts,
    build_impact_subgraph_context,
    build_no_access_stage_input_v2,
    validate_submission_evidence_manifest,
)
from math_flow.errors import MathFlowError
from math_flow.joint_portfolio_credit_experiment import build_joint_credit_node_effects
from math_flow.joint_portfolio_serial_transition import (
    reduce_joint_portfolio_serial_transition_v1,
)
from math_flow.repository import sha256_json
from math_flow.work_accounting import (
    materialize_submission_work_value,
    validate_root_contract,
)
from math_flow.work_projection import (
    PROFILE_V2,
    WorkProjectionCheckpointStore,
    WorkProjectionProvider,
    _assert_no_access_evidence_structure,
    _bindings,
    _ensure_required_context_coverage,
    _evidence_files,
    _invoke,
    _make_request,
    _patch_from_response,
    _required_primitive_updates,
    _safe_fact_stage_input,
    _seed_refs_from_safe_facts,
    _validate_transition,
)


PROFILE = "math-flow/joint-portfolio-serial-credit-candidate-v1"
FROZEN_AUTHORITY = "joint-portfolio-serial-transition-v1"
DIGEST = re.compile(r"^sha256:[0-9a-f]{64}$")
TRANSACTION = re.compile(r"^[0-9a-f]{40}$")

FROZEN_FIELDS = {
    "schemaVersion",
    "authority",
    "problemId",
    "subjectTransactionId",
    "rootContractDigest",
    "baseKnowledgeStateDigest",
    "targetKnowledgeStateDigest",
    "baseAccountingStateDigest",
    "topologyAlignmentDigest",
    "responseDigest",
    "semanticPacketDigest",
    "authoringPacketDigest",
    "transitionDigest",
    "sameWorldHandoffDigest",
    "withAccessPatchDigest",
    "withAccessStateDigest",
    "candidateDigest",
}
CREDIT_FIELDS = {
    "schemaVersion",
    "profile",
    "problemId",
    "subjectTransactionId",
    "accountingUnit",
    "allocationTarget",
    "basis",
    "rootContractDigest",
    "baseKnowledgeStateDigest",
    "targetKnowledgeStateDigest",
    "baseAccountingStateDigest",
    "topologyAlignmentDigest",
    "jointWithAccessCandidateDigest",
    "jointResponseDigest",
    "semanticPacketDigest",
    "authoringPacketDigest",
    "sameWorldHandoffDigest",
    "safeFactsDigest",
    "impactContextDigest",
    "noAccessPatchDigest",
    "withAccessPatchDigest",
    "noAccessStateDigest",
    "withAccessStateDigest",
    "evaluationDigest",
    "noAccessWorkHours",
    "withAccessWorkHours",
    "allocatedWorkHours",
    "nodeEffectsDigest",
    "nodeEffects",
    "candidateDigest",
}
FROZEN_DIGEST_FIELDS = FROZEN_FIELDS - {
    "schemaVersion",
    "authority",
    "problemId",
    "subjectTransactionId",
}
CREDIT_DIGEST_FIELDS = {
    field for field in CREDIT_FIELDS if field.endswith("Digest")
}


def _digest(value: object) -> str:
    return f"sha256:{sha256_json(copy.deepcopy(value))}"


def _seal(value: Mapping[str, object], field: str) -> dict[str, object]:
    core = {key: copy.deepcopy(item) for key, item in value.items() if key != field}
    return {**core, field: _digest(core)}


def validate_joint_portfolio_serial_frozen_wplus_v1(value: object) -> dict[str, object]:
    if not isinstance(value, dict) or set(value) != FROZEN_FIELDS:
        raise MathFlowError("joint serial frozen W+ candidate has an invalid envelope")
    candidate = copy.deepcopy(value)
    if candidate.get("schemaVersion") != 1 or candidate.get("authority") != FROZEN_AUTHORITY:
        raise MathFlowError("joint serial frozen W+ candidate has an invalid authority")
    subject = candidate.get("subjectTransactionId")
    if not isinstance(subject, str) or not TRANSACTION.fullmatch(subject):
        raise MathFlowError("joint serial frozen W+ candidate has an invalid subject")
    for field in FROZEN_DIGEST_FIELDS:
        item = candidate.get(field)
        if not isinstance(item, str) or not DIGEST.fullmatch(item):
            raise MathFlowError(f"joint serial frozen W+ candidate has an invalid {field}")
    if candidate.get("candidateDigest") != _digest(
        {key: item for key, item in candidate.items() if key != "candidateDigest"}
    ):
        raise MathFlowError("joint serial frozen W+ candidate digest mismatch")
    return candidate


def validate_joint_portfolio_serial_credit_candidate_v1(
    value: object,
) -> dict[str, object]:
    if not isinstance(value, dict) or set(value) != CREDIT_FIELDS:
        raise MathFlowError("joint serial credit candidate has an invalid envelope")
    candidate = copy.deepcopy(value)
    if candidate.get("schemaVersion") != 1 or candidate.get("profile") != PROFILE:
        raise MathFlowError("joint serial credit candidate has an invalid profile")
    subject = candidate.get("subjectTransactionId")
    if not isinstance(subject, str) or not TRANSACTION.fullmatch(subject):
        raise MathFlowError("joint serial credit candidate has an invalid subject")
    if not isinstance(candidate.get("problemId"), str) or not candidate["problemId"]:
        raise MathFlowError("joint serial credit candidate has an invalid problem")
    if not isinstance(candidate.get("accountingUnit"), str) or not candidate["accountingUnit"]:
        raise MathFlowError("joint serial credit candidate has an invalid accounting unit")
    for field in CREDIT_DIGEST_FIELDS:
        item = candidate.get(field)
        if not isinstance(item, str) or not DIGEST.fullmatch(item):
            raise MathFlowError(f"joint serial credit candidate has an invalid {field}")
    if candidate.get("allocationTarget") != {"kind": "submission", "id": subject}:
        raise MathFlowError("joint serial credit must allocate directly to its submission")
    if candidate.get("basis") != "same-world-work-reduction":
        raise MathFlowError("joint serial credit candidate has an invalid basis")
    no_work = Fraction(str(candidate.get("noAccessWorkHours")))
    with_work = Fraction(str(candidate.get("withAccessWorkHours")))
    allocated = Fraction(str(candidate.get("allocatedWorkHours")))
    if allocated <= 0 or no_work - with_work != allocated:
        raise MathFlowError("joint serial credit must equal a positive W-minus minus W-plus")
    effects = candidate.get("nodeEffects")
    if not isinstance(effects, list):
        raise MathFlowError("joint serial credit node effects must be an array")
    effect_total = Fraction(0)
    for effect in effects:
        if not isinstance(effect, dict) or not isinstance(effect.get("nodeRef"), dict):
            raise MathFlowError("joint serial credit node effect is invalid")
        effect_total += Fraction(str(effect.get("workReductionHours")))
    if effect_total != allocated:
        raise MathFlowError("joint serial credit node effects do not conserve allocation")
    expected_effect_digest = _digest(
        {
            "evaluationDigest": candidate["evaluationDigest"],
            "nodeEffects": effects,
        }
    )
    if candidate.get("nodeEffectsDigest") != expected_effect_digest:
        raise MathFlowError("joint serial credit node-effects digest mismatch")
    if candidate.get("candidateDigest") != _digest(
        {key: item for key, item in candidate.items() if key != "candidateDigest"}
    ):
        raise MathFlowError("joint serial credit candidate digest mismatch")
    return candidate


def _frozen_wplus_candidate(
    *,
    contract: Mapping[str, object],
    joint: Mapping[str, object],
) -> dict[str, object]:
    return _seal(
        {
            "schemaVersion": 1,
            "authority": FROZEN_AUTHORITY,
            "problemId": contract["problemId"],
            "subjectTransactionId": joint["postState"]["ledgerHead"],
            "rootContractDigest": contract["rootContractDigest"],
            "baseKnowledgeStateDigest": joint["transition"]["baseStateDigest"],
            "targetKnowledgeStateDigest": joint["postState"]["stateDigest"],
            "baseAccountingStateDigest": joint["withAccessPatch"][
                "baseAccountingStateDigest"
            ],
            "topologyAlignmentDigest": joint["topologyAlignment"]["alignmentDigest"],
            "responseDigest": _digest(joint["response"]),
            "semanticPacketDigest": joint["semanticPacket"]["packetDigest"],
            "authoringPacketDigest": joint["authoringPacketDigest"],
            "transitionDigest": _digest(joint["transition"]),
            "sameWorldHandoffDigest": joint["sameWorldHandoff"]["handoffDigest"],
            "withAccessPatchDigest": joint["withAccessPatch"]["patchDigest"],
            "withAccessStateDigest": joint["withAccessState"]["stateDigest"],
        },
        "candidateDigest",
    )


def run_joint_portfolio_serial_credit_v1(
    *,
    provider: WorkProjectionProvider,
    subject_transaction_id: str,
    root_contract: object,
    base_knowledge_state: Mapping[str, object],
    base_accounting_state: Mapping[str, object],
    joint_response: object,
    semantic_packet: Mapping[str, object],
    authoring_packet: Mapping[str, object],
    accepted_claims: object,
    accepted_claim_refs: object,
    judgment_id: str,
    evidence_manifest: object,
    evidence_chunks: Mapping[str, bytes],
    expected_frozen_candidate: object | None = None,
    checkpoint_dir: Path | None = None,
    descendant_depth: int = 1,
) -> dict[str, object]:
    """Freeze one adjacent joint W+ transition, estimate W-, and derive D."""

    manifest = validate_submission_evidence_manifest(evidence_manifest)
    verified_files = _evidence_files(manifest, evidence_chunks)
    evidence_file_refs = {item.path: item.digest for item in verified_files}
    contract = validate_root_contract(root_contract)
    joint = reduce_joint_portfolio_serial_transition_v1(
        joint_response,
        base_state=base_knowledge_state,
        base_accounting_state=base_accounting_state,
        root_contract=contract,
        semantic_packet=semantic_packet,
        authoring_packet=authoring_packet,
        accepted_claims=accepted_claims,
        judgment_id=judgment_id,
        evidence_file_refs=evidence_file_refs,
    )
    frozen = validate_joint_portfolio_serial_frozen_wplus_v1(
        _frozen_wplus_candidate(contract=contract, joint=joint)
    )
    if expected_frozen_candidate is not None:
        expected = validate_joint_portfolio_serial_frozen_wplus_v1(
            expected_frozen_candidate
        )
        if expected != frozen:
            raise MathFlowError("joint serial frozen W+ replay differs from the expected candidate")

    (
        subject,
        contract,
        before,
        after,
        base,
        alignment,
        chunks,
        claim_refs,
    ) = _validate_transition(
        subject_transaction_id=subject_transaction_id,
        root_contract=contract,
        base_knowledge_state=base_knowledge_state,
        target_knowledge_state=joint["postState"],
        base_accounting_state=base_accounting_state,
        topology_alignment=joint["topologyAlignment"],
        evidence_manifest=manifest,
        evidence_chunks=evidence_chunks,
        accepted_claim_refs=accepted_claim_refs,
    )
    if subject != semantic_packet.get("subjectTransactionId"):
        raise MathFlowError("joint serial credit semantic packet names another subject")
    if chunks != dict(evidence_chunks):
        raise MathFlowError("joint serial credit evidence changed during validation")
    bindings = _bindings(
        contract=contract,
        base=base,
        before=before,
        after=after,
        alignment=alignment,
        manifest=manifest,
        accepted_claim_refs=claim_refs,
    )
    no_required = _required_primitive_updates(
        before, after, base, evaluation_mode="no-access"
    )
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
            accepted_claim_refs=claim_refs,
            target_knowledge_state=after,
            evidence_manifest=manifest,
        ),
        profile=PROFILE_V2,
    )

    def validate_safe_response(response: object) -> dict[str, object]:
        safe = build_counterfactual_safe_facts(
            problem_id=str(contract["problemId"]),
            subject_transaction_id=subject,
            accepted_claim_refs=claim_refs,
            research_state=after,
            evidence_manifest=manifest,
            evidence_chunks=chunks,
            extracted=response,
        )
        context = build_impact_subgraph_context(
            problem_id=str(contract["problemId"]),
            subject_transaction_id=subject,
            accepted_claim_refs=claim_refs,
            research_state=after,
            seed_node_refs=_seed_refs_from_safe_facts(safe),
            descendant_depth=descendant_depth,
        )
        _ensure_required_context_coverage(no_required, context)
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
        accepted_claim_refs=claim_refs,
        research_state=after,
        seed_node_refs=_seed_refs_from_safe_facts(safe_facts),
        descendant_depth=descendant_depth,
    )
    _ensure_required_context_coverage(no_required, context)
    frozen_with_state = joint["withAccessState"]
    no_input = build_no_access_stage_input_v2(
        safe_facts=safe_facts,
        impact_context=context,
        research_state=after,
        frozen_with_access_state=frozen_with_state,
        frozen_with_access_candidate_digest=str(frozen["candidateDigest"]),
    )
    no_request = _make_request(
        stage="no-access",
        problem_id=str(contract["problemId"]),
        subject_transaction_id=subject,
        bindings=bindings,
        root_contract=contract,
        base_accounting_state=base,
        topology_alignment=alignment,
        required_updates=no_required,
        stage_input=no_input,
        profile=PROFILE_V2,
    )
    _assert_no_access_evidence_structure(no_request)

    def validate_no_response(response: object) -> dict[str, object]:
        return _patch_from_response(
            response,
            mode="no-access",
            problem_id=str(contract["problemId"]),
            subject_transaction_id=subject,
            bindings=bindings,
            base_accounting_state=base,
            required_updates=no_required,
            impact_context=context,
        )

    no_response = _invoke(
        provider,
        checkpoint,
        stage="no-access",
        request=no_request,
        evidence_files=(),
        semantic_validate=validate_no_response,
    )
    try:
        no_patch = validate_no_response(no_response)
        no_state, reproduced_with_state, evaluation = materialize_submission_work_value(
            base_state=base,
            no_access_patch=no_patch,
            with_access_patch=joint["withAccessPatch"],
            root_contract=contract,
            base_knowledge_state=before,
            target_knowledge_state=after,
            topology_alignment=alignment,
        )
    except Exception:
        if checkpoint is not None:
            checkpoint.invalidate(stage="no-access", request=no_request)
        raise
    if reproduced_with_state != frozen_with_state:
        raise MathFlowError("joint serial credit changed the frozen W+ state")
    node_effects = build_joint_credit_node_effects(
        no_access_state=no_state,
        with_access_state=frozen_with_state,
        no_access_patch=no_patch,
        with_access_patch=joint["withAccessPatch"],
        expected_work_value=str(evaluation["workValueHours"]),
    )
    node_effects_digest = _digest(
        {
            "evaluationDigest": evaluation["evaluationDigest"],
            "nodeEffects": node_effects,
        }
    )
    credit = _seal(
        {
            "schemaVersion": 1,
            "profile": PROFILE,
            "problemId": contract["problemId"],
            "subjectTransactionId": subject,
            "accountingUnit": contract["workUnit"]["id"],
            "allocationTarget": {"kind": "submission", "id": subject},
            "basis": "same-world-work-reduction",
            "rootContractDigest": contract["rootContractDigest"],
            "baseKnowledgeStateDigest": before["stateDigest"],
            "targetKnowledgeStateDigest": after["stateDigest"],
            "baseAccountingStateDigest": base["stateDigest"],
            "topologyAlignmentDigest": alignment["alignmentDigest"],
            "jointWithAccessCandidateDigest": frozen["candidateDigest"],
            "jointResponseDigest": frozen["responseDigest"],
            "semanticPacketDigest": frozen["semanticPacketDigest"],
            "authoringPacketDigest": frozen["authoringPacketDigest"],
            "sameWorldHandoffDigest": frozen["sameWorldHandoffDigest"],
            "safeFactsDigest": safe_facts["safeFactsDigest"],
            "impactContextDigest": context["contextDigest"],
            "noAccessPatchDigest": no_patch["patchDigest"],
            "withAccessPatchDigest": joint["withAccessPatch"]["patchDigest"],
            "noAccessStateDigest": no_state["stateDigest"],
            "withAccessStateDigest": frozen_with_state["stateDigest"],
            "evaluationDigest": evaluation["evaluationDigest"],
            "noAccessWorkHours": evaluation["noAccessWorkHours"],
            "withAccessWorkHours": evaluation["withAccessWorkHours"],
            "allocatedWorkHours": evaluation["workValueHours"],
            "nodeEffectsDigest": node_effects_digest,
            "nodeEffects": node_effects,
        },
        "candidateDigest",
    )
    validate_joint_portfolio_serial_credit_candidate_v1(credit)
    return {
        "jointArtifacts": joint,
        "jointWithAccessCandidate": frozen,
        "safeRequest": safe_request,
        "safeResponse": safe_response,
        "safeFacts": safe_facts,
        "impactContext": context,
        "noAccessInput": no_input,
        "noAccessRequest": no_request,
        "noAccessResponse": no_response,
        "noAccessPatch": no_patch,
        "noAccessState": no_state,
        "withAccessPatch": joint["withAccessPatch"],
        "withAccessState": frozen_with_state,
        "evaluation": evaluation,
        "creditCandidate": credit,
    }


__all__ = [
    "PROFILE",
    "run_joint_portfolio_serial_credit_v1",
    "validate_joint_portfolio_serial_credit_candidate_v1",
    "validate_joint_portfolio_serial_frozen_wplus_v1",
]
