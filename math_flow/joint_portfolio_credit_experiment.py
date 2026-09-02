"""Complete a joint topology/W+ judgment with same-world W- and credit.

This unpublished bridge keeps the successful joint portfolio/W+ judgment as
the live-state authority.  It does not ask the legacy work estimator to
recreate W+.  Instead it validates and freezes the joint response, extracts
counterfactual-safe facts, estimates only W-, and lets the trusted accounting
reducer assign the resulting work reduction directly to the submission.
"""

from __future__ import annotations

import copy
from collections.abc import Mapping, Sequence
from fractions import Fraction
from pathlib import Path

from .counterfactual_context import (
    build_counterfactual_safe_facts,
    build_impact_subgraph_context,
    build_no_access_stage_input_v2,
    validate_submission_evidence_manifest,
)
from .errors import MathFlowError
from .joint_portfolio_wplus_experiment import (
    reduce_joint_portfolio_wplus_response_v3,
)
from .repository import sha256_json
from .work_accounting import (
    apply_work_accounting_patch,
    canonical_decimal,
    materialize_submission_work_value,
    validate_root_contract,
)
from .work_projection import (
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


PROFILE = "math-flow/joint-portfolio-credit-candidate-v1"
CREDIT_CANDIDATE_FIELDS = {
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


def _digest(value: object) -> str:
    return f"sha256:{sha256_json(copy.deepcopy(value))}"


def _seal(value: Mapping[str, object], field: str) -> dict[str, object]:
    core = {key: copy.deepcopy(item) for key, item in value.items() if key != field}
    return {**core, field: _digest(core)}


def _node_key(value: object) -> tuple[str, str]:
    if not isinstance(value, dict):
        raise MathFlowError("joint credit node reference must be an object")
    kind = value.get("kind")
    node_id = value.get("id")
    if kind not in {"program", "thread"} or not isinstance(node_id, str):
        raise MathFlowError("joint credit node reference is invalid")
    return str(kind), node_id


def _signed_decimal(value: Fraction) -> str:
    return f"-{canonical_decimal(-value)}" if value < 0 else canonical_decimal(value)


def _state_views(state: Mapping[str, object]) -> dict[tuple[str, str], dict[str, object]]:
    annotations = {
        _node_key(item["nodeRef"]): item
        for item in state["annotations"]
        if isinstance(item, dict)
    }
    derived = {
        _node_key(item["nodeRef"]): item
        for item in state["derived"]
        if isinstance(item, dict)
    }
    if set(annotations) != set(derived):
        raise MathFlowError("joint credit accounting state has mismatched node views")
    return {
        key: {
            "nodeRef": copy.deepcopy(annotations[key]["nodeRef"]),
            "knowledgeNodeDigest": annotations[key]["knowledgeNodeDigest"],
            "directWorkHours": annotations[key]["directWorkHours"],
            "conditionalIncidence": annotations[key]["conditionalIncidence"],
            "globalReach": derived[key]["globalReach"],
            "conditionalSubtreeWorkHours": derived[key]["conditionalSubtreeWork"],
            "expectedDirectWorkHours": derived[key]["expectedDirectWork"],
        }
        for key in sorted(annotations)
    }


def _patch_keys(patch: Mapping[str, object]) -> set[tuple[str, str]]:
    return {
        _node_key(update["nodeRef"])
        for update in patch["updates"]
        if isinstance(update, dict)
    }


def build_joint_credit_node_effects(
    *,
    no_access_state: Mapping[str, object],
    with_access_state: Mapping[str, object],
    no_access_patch: Mapping[str, object],
    with_access_patch: Mapping[str, object],
    expected_work_value: str,
) -> list[dict[str, object]]:
    """Derive an additive node explanation without assigning credit to nodes."""

    no_views = _state_views(no_access_state)
    with_views = _state_views(with_access_state)
    if set(no_views) != set(with_views):
        raise MathFlowError("joint credit counterfactual node sets differ")
    no_direct = _patch_keys(no_access_patch)
    with_direct = _patch_keys(with_access_patch)
    primitive_fields = ("directWorkHours", "conditionalIncidence")
    derived_fields = (
        "globalReach",
        "conditionalSubtreeWorkHours",
        "expectedDirectWorkHours",
    )
    effects: list[dict[str, object]] = []
    additive_total = Fraction(0)
    for key in sorted(no_views):
        no_view = no_views[key]
        with_view = with_views[key]
        if no_view["knowledgeNodeDigest"] != with_view["knowledgeNodeDigest"]:
            raise MathFlowError("joint credit branches use different knowledge nodes")
        primitive_differences = [
            field for field in primitive_fields if no_view[field] != with_view[field]
        ]
        derived_differences = [
            field for field in derived_fields if no_view[field] != with_view[field]
        ]
        direct = key in no_direct or key in with_direct
        if not direct and not derived_differences:
            continue
        reduction = Fraction(str(no_view["expectedDirectWorkHours"])) - Fraction(
            str(with_view["expectedDirectWorkHours"])
        )
        additive_total += reduction
        effects.append(
            {
                "nodeRef": copy.deepcopy(no_view["nodeRef"]),
                "knowledgeNodeDigest": no_view["knowledgeNodeDigest"],
                "effectKind": "direct" if direct else "propagated",
                "directUpdateBranches": [
                    branch
                    for branch, keys in (
                        ("no-access", no_direct),
                        ("with-access", with_direct),
                    )
                    if key in keys
                ],
                "primitiveDifferenceFields": primitive_differences,
                "derivedDifferenceFields": derived_differences,
                "noAccess": {
                    field: copy.deepcopy(no_view[field])
                    for field in (*primitive_fields, *derived_fields)
                },
                "withAccess": {
                    field: copy.deepcopy(with_view[field])
                    for field in (*primitive_fields, *derived_fields)
                },
                "workReductionHours": _signed_decimal(reduction),
            }
        )
    if additive_total != Fraction(expected_work_value):
        raise MathFlowError("joint credit node effects do not conserve work value")
    return effects


def validate_joint_portfolio_credit_candidate(value: object) -> dict[str, object]:
    if not isinstance(value, dict) or set(value) != CREDIT_CANDIDATE_FIELDS:
        raise MathFlowError("joint portfolio credit candidate has an invalid envelope")
    candidate = copy.deepcopy(value)
    if candidate.get("schemaVersion") != 1 or candidate.get("profile") != PROFILE:
        raise MathFlowError("joint portfolio credit candidate has an invalid profile")
    subject = candidate.get("subjectTransactionId")
    if candidate.get("allocationTarget") != {"kind": "submission", "id": subject}:
        raise MathFlowError("joint portfolio credit must allocate directly to its submission")
    if candidate.get("basis") != "same-world-work-reduction":
        raise MathFlowError("joint portfolio credit candidate has an invalid basis")
    no_work = Fraction(str(candidate.get("noAccessWorkHours")))
    with_work = Fraction(str(candidate.get("withAccessWorkHours")))
    allocated = Fraction(str(candidate.get("allocatedWorkHours")))
    if allocated <= 0 or no_work - with_work != allocated:
        raise MathFlowError("joint portfolio credit must equal a positive W-minus minus W-plus")
    effects = candidate.get("nodeEffects")
    if not isinstance(effects, list):
        raise MathFlowError("joint portfolio credit node effects must be an array")
    effect_total = Fraction(0)
    for effect in effects:
        if not isinstance(effect, dict):
            raise MathFlowError("joint portfolio credit node effect is invalid")
        _node_key(effect.get("nodeRef"))
        effect_total += Fraction(str(effect.get("workReductionHours")))
    if effect_total != allocated:
        raise MathFlowError("joint portfolio credit node effects do not conserve allocation")
    expected_effect_digest = _digest(
        {
            "evaluationDigest": candidate["evaluationDigest"],
            "nodeEffects": effects,
        }
    )
    if candidate.get("nodeEffectsDigest") != expected_effect_digest:
        raise MathFlowError("joint portfolio credit node-effects digest mismatch")
    if candidate.get("candidateDigest") != _digest(
        {key: item for key, item in candidate.items() if key != "candidateDigest"}
    ):
        raise MathFlowError("joint portfolio credit candidate digest mismatch")
    return candidate


def run_joint_portfolio_credit_candidate(
    *,
    provider: WorkProjectionProvider,
    subject_transaction_id: str,
    root_contract: object,
    base_knowledge_state: Mapping[str, object],
    base_accounting_state: Mapping[str, object],
    joint_response: object,
    semantic_packet: Mapping[str, object],
    accepted_claims: Sequence[Mapping[str, object]],
    accepted_claim_refs: object,
    judgment_id: str,
    evidence_manifest: object,
    evidence_chunks: Mapping[str, bytes],
    checkpoint_dir: Path | None = None,
    descendant_depth: int = 1,
) -> dict[str, object]:
    """Run safe-facts and W- after freezing the joint topology/W+ response."""

    manifest = validate_submission_evidence_manifest(evidence_manifest)
    verified_files = _evidence_files(manifest, evidence_chunks)
    contract = validate_root_contract(root_contract)
    joint = reduce_joint_portfolio_wplus_response_v3(
        joint_response,
        base_state=base_knowledge_state,
        base_accounting_state=base_accounting_state,
        root_contract=contract,
        semantic_packet=semantic_packet,
        accepted_claims=accepted_claims,
        judgment_id=judgment_id,
        evidence_files=verified_files,
    )
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
        raise MathFlowError("joint portfolio credit semantic packet names another subject")
    if chunks != dict(evidence_chunks):
        raise MathFlowError("joint portfolio credit evidence changed during validation")
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
    joint_with_access_candidate = _seal(
        {
            "schemaVersion": 1,
            "authority": "joint-portfolio-wplus-v3",
            "problemId": contract["problemId"],
            "subjectTransactionId": subject,
            "baseKnowledgeStateDigest": before["stateDigest"],
            "targetKnowledgeStateDigest": after["stateDigest"],
            "baseAccountingStateDigest": base["stateDigest"],
            "topologyAlignmentDigest": alignment["alignmentDigest"],
            "responseDigest": _digest(joint["response"]),
            "transitionDigest": _digest(joint["transition"]),
            "sameWorldHandoffDigest": joint["sameWorldHandoff"]["handoffDigest"],
            "withAccessPatchDigest": joint["withAccessPatch"]["patchDigest"],
            "withAccessStateDigest": joint["withAccessState"]["stateDigest"],
        },
        "candidateDigest",
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
        frozen_with_access_candidate_digest=str(
            joint_with_access_candidate["candidateDigest"]
        ),
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
        patch = _patch_from_response(
            response,
            mode="no-access",
            problem_id=str(contract["problemId"]),
            subject_transaction_id=subject,
            bindings=bindings,
            base_accounting_state=base,
            required_updates=no_required,
            impact_context=context,
        )
        # Keep provider-local retries branch-local.  The no-access role never
        # receives a target-D or positivity diagnostic; an outer retry can
        # reuse the exact frozen joint W+ candidate.
        apply_work_accounting_patch(
            base,
            patch,
            root_contract=contract,
            base_knowledge_state=before,
            target_knowledge_state=after,
            topology_alignment=alignment,
        )
        return patch

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
        raise MathFlowError("joint portfolio credit changed the frozen W+ state")
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
            "jointWithAccessCandidateDigest": joint_with_access_candidate[
                "candidateDigest"
            ],
            "jointResponseDigest": _digest(joint["response"]),
            "sameWorldHandoffDigest": joint["sameWorldHandoff"]["handoffDigest"],
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
    validate_joint_portfolio_credit_candidate(credit)
    return {
        "jointArtifacts": joint,
        "jointWithAccessCandidate": joint_with_access_candidate,
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
