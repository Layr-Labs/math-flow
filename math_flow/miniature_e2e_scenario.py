"""Provider-free miniature end-to-end protocol evaluation fixture.

This module deliberately contains no provider or publication adapter.  It
builds one synthetic, precommitted eight-submission history through the real
two-entity knowledge reducer and hierarchical work-accounting reducer, then
scores the resulting transcript by deterministic replay.
"""

from __future__ import annotations

import copy
from fractions import Fraction
from typing import Mapping

from .errors import MathFlowError
from .repository import sha256_json
from .research_builder_v7 import (
    apply_research_builder_v7_transition,
    empty_research_program_state_v3,
    validate_research_program_state_v3,
)
from .work_accounting import (
    apply_work_accounting_patch,
    bind_patch_to_state,
    canonical_decimal,
    make_root_contract,
    make_work_accounting_patch,
    make_zero_work_accounting_state,
    materialize_submission_work_value,
    validate_root_contract,
    validate_submission_work_value,
    validate_work_accounting_state,
)


PROBLEM_ID = "miniature-route-portfolio"
PROJECTION_SPEC_DIGEST = "sha256:" + "e" * 64
SUBJECTS = tuple(f"{index:040x}" for index in range(1, 9))
JUDGMENT_IDS = tuple("sha256:" + str(index) * 64 for index in range(1, 9))

ROUTE_A = "route-a"
ROUTE_B = "route-b"
DEAD_END = "route-b/dead-end"
FOUNDATION = "foundation"
RESULT_A = "result/route-a-opening"
RESULT_B = "result/route-b-opening"
RESULT_FOUNDATION = "result/foundation-lemma"
RESULT_NEGATIVE = "result/dead-end-impossibility"
RESULT_GLOBALITY = "result/foundation-generality"
RESULT_CROSS = "result/cross-route-bridge"
RESULT_SOLUTION = "result/decisive-solution"

REQUIRED_CASE_TAGS = {
    "independent-route",
    "dependency",
    "negative-pruning",
    "partial-positive",
    "decisive-completion",
    "duplicate-reproduction",
    "topology-correction",
    "cross-program",
}

KNOWLEDGE_BUILDER_ID = "openrouter-hierarchical-research-builder-v10-experiment"
WORK_ACCOUNTING_ID = "openrouter-work-accounting-v2"
WORK_ACCOUNTING_PROFILE = "math-flow/work-accounting-transition-v2"


def _without_digest(record: Mapping[str, object]) -> dict[str, object]:
    return {
        key: copy.deepcopy(value)
        for key, value in record.items()
        if key != "digest"
    }


def _support(note: str, *, category: str = "proofs") -> dict[str, object]:
    support: dict[str, object] = {
        "proofs": [],
        "methods": [],
        "computations": [],
        "tools": [],
        "artifactRefs": [],
        "attestationRefs": [],
    }
    support[category] = [note]
    return support


def _program(
    program_id: str,
    *,
    parent_id: str,
    title: str,
    objective: str,
    current: str,
    residual: str,
    sources: list[str],
    results: list[str] | None = None,
    status: str = "active",
) -> dict[str, object]:
    return {
        "id": program_id,
        "parentId": parent_id,
        "title": title,
        "objective": objective,
        "currentStateSummary": current,
        "localResidualSummary": residual,
        "status": status,
        "intermediateResultIds": sorted(results or []),
        "sourceTransactionIds": sorted(sources),
        "lineage": [],
    }


def _result(
    result_id: str,
    *,
    subject: str,
    judgment_id: str,
    claim_key: str,
    primary_program_id: str,
    title: str,
    statement: str,
    support: dict[str, object],
    related_program_ids: list[str] | None = None,
    dependency_result_ids: list[str] | None = None,
    qualifications: list[str] | None = None,
) -> dict[str, object]:
    return {
        "id": result_id,
        "primaryProgramId": primary_program_id,
        "relatedProgramIds": sorted(related_program_ids or []),
        "title": title,
        "statement": statement,
        "scopeQualifications": sorted(qualifications or []),
        "support": support,
        "dependencyResultIds": sorted(dependency_result_ids or []),
        "claimRefs": [{"transactionId": subject, "claimKey": claim_key}],
        "sourceTransactionIds": [subject],
        "judgmentIds": [judgment_id],
        "status": "active",
        "supersededByResultIds": [],
    }


def _content_operation(
    base: Mapping[str, object],
    kind: str,
    entity_id: str,
    value: Mapping[str, object],
) -> dict[str, object]:
    collection = "programs" if kind == "program" else "intermediateResults"
    existing = base[collection].get(entity_id)  # type: ignore[index]
    return {
        "entityKind": kind,
        "entityId": entity_id,
        "baseDigest": existing["digest"] if isinstance(existing, dict) else None,
        "value": copy.deepcopy(dict(value)),
    }


def _transition(
    base: Mapping[str, object],
    *,
    ordinal: int,
    claim_key: str,
    content_operations: list[dict[str, object]],
    direct_program_ids: list[str],
    result_ids: list[str],
    basis: str,
    rationale: str,
    related_program_ids: list[str],
    topology_operations: list[dict[str, object]] | None = None,
    topology_rationale: str | None = None,
) -> dict[str, object]:
    return {
        "schemaVersion": 1,
        "subjectTransactionId": SUBJECTS[ordinal - 1],
        "baseStateDigest": base["stateDigest"],
        "contentOperations": content_operations,
        "topologyOperations": topology_operations or [],
        "contribution": {
            "claimKeys": [claim_key],
            "directProgramIds": sorted(direct_program_ids),
            "intermediateResultIds": sorted(result_ids),
        },
        "placementAudit": {
            "basis": basis,
            "rationale": rationale,
            "relatedProgramIds": sorted(related_program_ids),
        },
        "topologyRationale": topology_rationale,
    }


def _accepted_claim(
    ordinal: int, claim_key: str, statement: str, dependencies: list[str] | None = None
) -> list[dict[str, object]]:
    return [
        {
            "claimKey": claim_key,
            "statement": statement,
            "dependencyTransactionIds": sorted(dependencies or []),
        }
    ]


def _transition_1(base: Mapping[str, object]) -> tuple[dict[str, object], list[dict[str, object]]]:
    subject = SUBJECTS[0]
    claim = "route-a-opening"
    program = _program(
        ROUTE_A,
        parent_id="root",
        title="Route A",
        objective="Resolve the problem through the structural route.",
        current="A partial structural reduction is established.",
        residual="The main route-A construction and verification remain.",
        sources=[subject],
        results=[RESULT_A],
    )
    result = _result(
        RESULT_A,
        subject=subject,
        judgment_id=JUDGMENT_IDS[0],
        claim_key=claim,
        primary_program_id=ROUTE_A,
        title="Route-A opening reduction",
        statement="The canonical objective reduces to the route-A structural case.",
        support=_support("A direct reduction establishes the structural case."),
    )
    transition = _transition(
        base,
        ordinal=1,
        claim_key=claim,
        content_operations=[
            _content_operation(base, "program", ROUTE_A, program),
            _content_operation(base, "intermediateResult", RESULT_A, result),
        ],
        direct_program_ids=[ROUTE_A],
        result_ids=[RESULT_A],
        basis="local-objective",
        rationale="The accepted reduction opens one coherent local route.",
        related_program_ids=[ROUTE_A],
    )
    return transition, _accepted_claim(
        1, claim, "The route-A structural reduction is valid."
    )


def _transition_2(base: Mapping[str, object]) -> tuple[dict[str, object], list[dict[str, object]]]:
    subject = SUBJECTS[1]
    claim = "route-b-opening"
    route_b = _program(
        ROUTE_B,
        parent_id="root",
        title="Route B",
        objective="Resolve the problem through the computational route.",
        current="A computational formulation makes route B actionable.",
        residual="The formulation, its main search, and one suspect branch remain.",
        sources=[subject],
        results=[RESULT_B],
    )
    dead_end = _program(
        DEAD_END,
        parent_id=ROUTE_B,
        title="Route-B suspect branch",
        objective="Test whether the restricted branch can meet the target.",
        current="The branch is a credible active fallback.",
        residual="Search or rule out the restricted branch.",
        sources=[subject],
    )
    result = _result(
        RESULT_B,
        subject=subject,
        judgment_id=JUDGMENT_IDS[1],
        claim_key=claim,
        primary_program_id=ROUTE_B,
        title="Route-B computational formulation",
        statement="The canonical objective has an independent finite-search formulation.",
        support=_support(
            "A deterministic encoding supplies the finite-search formulation.",
            category="computations",
        ),
    )
    transition = _transition(
        base,
        ordinal=2,
        claim_key=claim,
        content_operations=[
            _content_operation(base, "program", ROUTE_B, route_b),
            _content_operation(base, "program", DEAD_END, dead_end),
            _content_operation(base, "intermediateResult", RESULT_B, result),
        ],
        direct_program_ids=[ROUTE_B],
        result_ids=[RESULT_B],
        basis="local-objective",
        rationale="The computational formulation is independent of route A.",
        related_program_ids=[ROUTE_B],
    )
    return transition, _accepted_claim(
        2, claim, "The independent route-B formulation is valid."
    )


def _transition_3(base: Mapping[str, object]) -> tuple[dict[str, object], list[dict[str, object]]]:
    subject = SUBJECTS[2]
    claim = "foundation-lemma"
    program = _program(
        FOUNDATION,
        parent_id=ROUTE_A,
        title="Reusable foundation",
        objective="Establish the technical foundation needed by route A.",
        current="A dependency-backed partial lemma is established.",
        residual="Complete the foundation and integrate it into a terminal argument.",
        sources=[subject],
        results=[RESULT_FOUNDATION],
    )
    route_a = _without_digest(base["programs"][ROUTE_A])  # type: ignore[index]
    route_a.update(
        {
            "currentStateSummary": "Route A now has an explicit dependent foundation.",
            "localResidualSummary": "Integrate and complete the route above the foundation.",
            "sourceTransactionIds": sorted([*route_a["sourceTransactionIds"], subject]),
        }
    )
    result = _result(
        RESULT_FOUNDATION,
        subject=subject,
        judgment_id=JUDGMENT_IDS[2],
        claim_key=claim,
        primary_program_id=FOUNDATION,
        title="Dependency-backed foundation lemma",
        statement="The foundation lemma holds assuming the route-A opening reduction.",
        support=_support("The proof invokes the accepted route-A reduction."),
        dependency_result_ids=[RESULT_A],
    )
    transition = _transition(
        base,
        ordinal=3,
        claim_key=claim,
        content_operations=[
            _content_operation(base, "program", ROUTE_A, route_a),
            _content_operation(base, "program", FOUNDATION, program),
            _content_operation(base, "intermediateResult", RESULT_FOUNDATION, result),
        ],
        direct_program_ids=[FOUNDATION],
        result_ids=[RESULT_FOUNDATION],
        basis="local-objective",
        rationale="The lemma is a distinct dependent work package within route A.",
        related_program_ids=[FOUNDATION],
    )
    return transition, _accepted_claim(
        3,
        claim,
        "The foundation lemma follows from the route-A opening reduction.",
        [SUBJECTS[0]],
    )


def _transition_4(base: Mapping[str, object]) -> tuple[dict[str, object], list[dict[str, object]]]:
    subject = SUBJECTS[3]
    claim = "dead-end-impossibility"
    dead_end = _without_digest(base["programs"][DEAD_END])  # type: ignore[index]
    dead_end.update(
        {
            "currentStateSummary": "The restricted branch is proved impossible.",
            "localResidualSummary": "No further work remains on this branch.",
            "status": "completed",
            "sourceTransactionIds": sorted([*dead_end["sourceTransactionIds"], subject]),
        }
    )
    route_b = _without_digest(base["programs"][ROUTE_B])  # type: ignore[index]
    route_b.update(
        {
            "currentStateSummary": "The suspect branch is eliminated; the main route remains.",
            "localResidualSummary": "Complete the remaining route-B search.",
            "intermediateResultIds": sorted(
                [*route_b["intermediateResultIds"], RESULT_NEGATIVE]
            ),
            "sourceTransactionIds": sorted(
                [*route_b["sourceTransactionIds"], subject]
            ),
        }
    )
    result = _result(
        RESULT_NEGATIVE,
        subject=subject,
        judgment_id=JUDGMENT_IDS[3],
        claim_key=claim,
        primary_program_id=ROUTE_B,
        title="Restricted branch impossibility",
        statement="No object in the restricted route-B branch can meet the target.",
        support=_support("A separating invariant rules out the entire branch."),
        dependency_result_ids=[RESULT_B],
    )
    transition = _transition(
        base,
        ordinal=4,
        claim_key=claim,
        content_operations=[
            _content_operation(base, "program", DEAD_END, dead_end),
            _content_operation(base, "program", ROUTE_B, route_b),
            _content_operation(base, "intermediateResult", RESULT_NEGATIVE, result),
        ],
        direct_program_ids=[ROUTE_B],
        result_ids=[RESULT_NEGATIVE],
        basis="local-objective",
        rationale="The route-B negative result conclusively completes its suspect branch.",
        related_program_ids=[ROUTE_B],
    )
    return transition, _accepted_claim(
        4,
        claim,
        "The restricted route-B branch is impossible.",
        [SUBJECTS[1]],
    )


def _transition_5(base: Mapping[str, object]) -> tuple[dict[str, object], list[dict[str, object]]]:
    subject = SUBJECTS[4]
    claim = "route-a-reproduction"
    result = _without_digest(base["intermediateResults"][RESULT_A])  # type: ignore[index]
    result["claimRefs"] = sorted(
        [
            *result["claimRefs"],
            {"transactionId": subject, "claimKey": claim},
        ],
        key=lambda item: (item["transactionId"], item["claimKey"]),
    )
    result["sourceTransactionIds"] = sorted([*result["sourceTransactionIds"], subject])
    result["judgmentIds"] = sorted([*result["judgmentIds"], JUDGMENT_IDS[4]])
    result["support"] = {
        **result["support"],
        "proofs": sorted(
            [
                *result["support"]["proofs"],
                "An independent proof reproduces the same opening reduction.",
            ]
        ),
    }
    transition = _transition(
        base,
        ordinal=5,
        claim_key=claim,
        content_operations=[
            _content_operation(base, "intermediateResult", RESULT_A, result)
        ],
        direct_program_ids=[ROUTE_A],
        result_ids=[RESULT_A],
        basis="local-objective",
        rationale="The submission is independent support for the existing route-A result.",
        related_program_ids=[ROUTE_A],
    )
    return transition, _accepted_claim(
        5, claim, "An independent derivation reproduces the route-A opening reduction."
    )


def _transition_6(base: Mapping[str, object]) -> tuple[dict[str, object], list[dict[str, object]]]:
    subject = SUBJECTS[5]
    claim = "foundation-generality"
    root = _without_digest(base["programs"]["root"])  # type: ignore[index]
    root.update(
        {
            "currentStateSummary": "The foundation is recognized as globally reusable.",
            "localResidualSummary": "The two routes remain open above their shared foundation.",
            "intermediateResultIds": sorted(
                [*root["intermediateResultIds"], RESULT_GLOBALITY]
            ),
            "sourceTransactionIds": sorted([*root["sourceTransactionIds"], subject]),
        }
    )
    moved = _without_digest(base["programs"][FOUNDATION])  # type: ignore[index]
    moved["parentId"] = "root"
    result = _result(
        RESULT_GLOBALITY,
        subject=subject,
        judgment_id=JUDGMENT_IDS[5],
        claim_key=claim,
        primary_program_id="root",
        title="Foundation generality",
        statement="The foundation is reusable outside route A and belongs at shared scope.",
        support=_support("A transport argument proves route-independent reuse."),
        dependency_result_ids=[RESULT_FOUNDATION],
    )
    topology_operation = {
        "action": "move",
        "entityKind": "program",
        "entityId": FOUNDATION,
        "baseDigest": base["programs"][FOUNDATION]["digest"],  # type: ignore[index]
        "value": moved,
    }
    transition = _transition(
        base,
        ordinal=6,
        claim_key=claim,
        content_operations=[
            _content_operation(base, "program", "root", root),
            _content_operation(base, "intermediateResult", RESULT_GLOBALITY, result),
        ],
        topology_operations=[topology_operation],
        topology_rationale=(
            "The accepted generality result reveals that the foundation is shared, "
            "so its stable program moves from route A to root without changing content."
        ),
        direct_program_ids=["root"],
        result_ids=[RESULT_GLOBALITY],
        basis="canonical-objective",
        rationale="The generality claim determines shared canonical placement.",
        related_program_ids=[],
    )
    return transition, _accepted_claim(
        6,
        claim,
        "The foundation is reusable independently of route A.",
        [SUBJECTS[2]],
    )


def _transition_7(base: Mapping[str, object]) -> tuple[dict[str, object], list[dict[str, object]]]:
    subject = SUBJECTS[6]
    claim = "cross-route-bridge"
    route_a = _without_digest(base["programs"][ROUTE_A])  # type: ignore[index]
    route_b = _without_digest(base["programs"][ROUTE_B])  # type: ignore[index]
    for program in (route_a, route_b):
        program["intermediateResultIds"] = sorted(
            [*program["intermediateResultIds"], RESULT_CROSS]
        )
        program["sourceTransactionIds"] = sorted(
            [*program["sourceTransactionIds"], subject]
        )
    route_a["currentStateSummary"] = "Route A is linked to route B by a shared bridge."
    route_a["localResidualSummary"] = "Complete the reduced route-A terminal step."
    route_b["currentStateSummary"] = "Route B is linked to route A by a shared bridge."
    route_b["localResidualSummary"] = "Complete the reduced route-B terminal search."
    result = _result(
        RESULT_CROSS,
        subject=subject,
        judgment_id=JUDGMENT_IDS[6],
        claim_key=claim,
        primary_program_id=ROUTE_A,
        related_program_ids=[ROUTE_B],
        title="Cross-route bridge",
        statement="One bridge lemma simultaneously simplifies routes A and B.",
        support=_support("A common invariant links the two otherwise independent routes."),
        dependency_result_ids=[RESULT_A, RESULT_B],
    )
    transition = _transition(
        base,
        ordinal=7,
        claim_key=claim,
        content_operations=[
            _content_operation(base, "program", ROUTE_A, route_a),
            _content_operation(base, "program", ROUTE_B, route_b),
            _content_operation(base, "intermediateResult", RESULT_CROSS, result),
        ],
        direct_program_ids=[ROUTE_A, ROUTE_B],
        result_ids=[RESULT_CROSS],
        basis="cross-program",
        rationale="The accepted bridge directly reduces two incomparable programs.",
        related_program_ids=[ROUTE_A, ROUTE_B],
    )
    return transition, _accepted_claim(
        7,
        claim,
        "The cross-route bridge simultaneously simplifies routes A and B.",
        [SUBJECTS[0], SUBJECTS[1]],
    )


def _transition_8(base: Mapping[str, object]) -> tuple[dict[str, object], list[dict[str, object]]]:
    subject = SUBJECTS[7]
    claim = "decisive-solution"
    root = _without_digest(base["programs"]["root"])  # type: ignore[index]
    root.update(
        {
            "currentStateSummary": "The canonical objective is decisively solved.",
            "localResidualSummary": "No research work remains under the root contract.",
            "intermediateResultIds": sorted(
                [*root["intermediateResultIds"], RESULT_SOLUTION]
            ),
            "sourceTransactionIds": sorted([*root["sourceTransactionIds"], subject]),
        }
    )
    programs: list[tuple[str, dict[str, object]]] = []
    for program_id in (ROUTE_A, ROUTE_B, FOUNDATION):
        program = _without_digest(base["programs"][program_id])  # type: ignore[index]
        program.update(
            {
                "status": "completed",
                "currentStateSummary": "The decisive solution completes this work package.",
                "localResidualSummary": "No further work remains under the root contract.",
                "sourceTransactionIds": sorted(
                    [*program["sourceTransactionIds"], subject]
                ),
            }
        )
        programs.append((program_id, program))
    result = _result(
        RESULT_SOLUTION,
        subject=subject,
        judgment_id=JUDGMENT_IDS[7],
        claim_key=claim,
        primary_program_id="root",
        title="Decisive solution",
        statement="The canonical objective is fully resolved.",
        support=_support("A complete argument closes the root objective."),
        dependency_result_ids=[RESULT_CROSS, RESULT_GLOBALITY],
    )
    transition = _transition(
        base,
        ordinal=8,
        claim_key=claim,
        content_operations=[
            _content_operation(base, "program", "root", root),
            *[
                _content_operation(base, "program", program_id, program)
                for program_id, program in programs
            ],
            _content_operation(base, "intermediateResult", RESULT_SOLUTION, result),
        ],
        direct_program_ids=["root"],
        result_ids=[RESULT_SOLUTION],
        basis="canonical-objective",
        rationale="The accepted result directly satisfies the canonical terminal condition.",
        related_program_ids=[],
    )
    return transition, _accepted_claim(
        8,
        claim,
        "The decisive argument resolves the canonical objective.",
        [SUBJECTS[5], SUBJECTS[6]],
    )


_TRANSITION_BUILDERS = (
    _transition_1,
    _transition_2,
    _transition_3,
    _transition_4,
    _transition_5,
    _transition_6,
    _transition_7,
    _transition_8,
)

_CASE_TAGS = (
    ["independent-route", "partial-positive"],
    ["independent-route", "partial-positive"],
    ["dependency", "partial-positive"],
    ["negative-pruning"],
    ["duplicate-reproduction"],
    ["topology-correction"],
    ["cross-program"],
    ["decisive-completion"],
)


def miniature_root_contract() -> dict[str, object]:
    return make_root_contract(
        problem_id=PROBLEM_ID,
        knowledge_projection_id="miniature-e2e-knowledge-v1",
        knowledge_projection_spec_digest=PROJECTION_SPEC_DIGEST,
        objective="Resolve the synthetic two-route objective.",
        terminal_condition=(
            "A complete accepted argument resolving the synthetic objective is available."
        ),
        tool_baseline=(
            "Ordinary mathematical references, Python, and standard proof tools as of 2026-08-31."
        ),
        reference_community_description=(
            "Qualified researchers pursuing the builder-organized two-route portfolio."
        ),
        researcher_qualification=(
            "A competent researcher qualified for the relevant mathematical work package."
        ),
    )


def _work_update(
    node_id: str,
    *,
    subject: str,
    direct: str | None = None,
    incidence: str | None = None,
) -> dict[str, object]:
    changes: dict[str, object] = {}
    if direct is not None:
        changes["directWorkHours"] = direct
    if incidence is not None:
        changes["conditionalIncidence"] = incidence
    return {
        "nodeRef": {"kind": "program", "id": node_id},
        "changes": changes,
        "rationale": f"Synthetic oracle estimate for submission {subject} at {node_id}.",
        "evidenceRefs": [subject],
    }


def _work_plan(ordinal: int) -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    subject = SUBJECTS[ordinal - 1]
    if ordinal == 1:
        return (
            [
                _work_update("root", subject=subject, direct="10"),
                _work_update(ROUTE_A, subject=subject, direct="70", incidence="1"),
            ],
            [
                _work_update("root", subject=subject, direct="10"),
                _work_update(ROUTE_A, subject=subject, direct="50", incidence="1"),
            ],
        )
    if ordinal == 2:
        return (
            [
                _work_update(ROUTE_B, subject=subject, direct="30", incidence="1"),
                _work_update(DEAD_END, subject=subject, direct="15", incidence="1"),
            ],
            [
                _work_update(ROUTE_B, subject=subject, direct="25", incidence="1"),
                _work_update(DEAD_END, subject=subject, direct="15", incidence="1"),
            ],
        )
    if ordinal == 3:
        return (
            [
                _work_update(ROUTE_A, subject=subject, direct="20"),
                _work_update(FOUNDATION, subject=subject, direct="30", incidence="1"),
            ],
            [
                _work_update(ROUTE_A, subject=subject, direct="20"),
                _work_update(FOUNDATION, subject=subject, direct="20", incidence="1"),
            ],
        )
    if ordinal == 4:
        return (
            [],
            [_work_update(DEAD_END, subject=subject, direct="0", incidence="0")],
        )
    if ordinal == 5:
        return ([], [_work_update(ROUTE_A, subject=subject, direct="18")])
    if ordinal == 6:
        return (
            [_work_update(FOUNDATION, subject=subject, incidence="1")],
            [_work_update(FOUNDATION, subject=subject, direct="18", incidence="1")],
        )
    if ordinal == 7:
        return (
            [],
            [
                _work_update(ROUTE_A, subject=subject, direct="13"),
                _work_update(ROUTE_B, subject=subject, direct="18"),
            ],
        )
    if ordinal == 8:
        return (
            [],
            [
                _work_update("root", subject=subject, direct="0"),
                _work_update(ROUTE_A, subject=subject, direct="0", incidence="0"),
                _work_update(ROUTE_B, subject=subject, direct="0", incidence="0"),
                _work_update(FOUNDATION, subject=subject, direct="0", incidence="0"),
            ],
        )
    raise MathFlowError("miniature scenario ordinal is out of range")


def _patch(
    *,
    mode: str,
    subject: str,
    root_contract: Mapping[str, object],
    base_accounting_state: Mapping[str, object],
    base_knowledge_state: Mapping[str, object],
    target_knowledge_state: Mapping[str, object],
    topology_alignment: Mapping[str, object],
    updates: list[dict[str, object]],
) -> dict[str, object]:
    unbound = make_work_accounting_patch(
        problem_id=PROBLEM_ID,
        subject_transaction_id=subject,
        evaluation_mode=mode,
        root_contract_digest=str(root_contract["rootContractDigest"]),
        base_accounting_state_digest=str(base_accounting_state["stateDigest"]),
        base_knowledge_state_digest=str(base_knowledge_state["stateDigest"]),
        target_knowledge_state_digest=str(target_knowledge_state["stateDigest"]),
        topology_alignment_digest=str(topology_alignment["alignmentDigest"]),
        updates=updates,
    )
    return bind_patch_to_state(unbound, base_accounting_state)


def _expected_direct(state: Mapping[str, object]) -> dict[str, Fraction]:
    return {
        str(item["nodeRef"]["id"]): Fraction(str(item["expectedDirectWork"]))
        for item in state["derived"]  # type: ignore[index]
    }


def _node_reductions(
    no_access_state: Mapping[str, object], with_access_state: Mapping[str, object]
) -> list[dict[str, object]]:
    no_values = _expected_direct(no_access_state)
    with_values = _expected_direct(with_access_state)
    result = []
    for node_id in sorted(no_values):
        delta = no_values[node_id] - with_values[node_id]
        if delta:
            result.append(
                {
                    "nodeRef": {"kind": "program", "id": node_id},
                    "noAccessExpectedDirectWork": canonical_decimal(no_values[node_id]),
                    "withAccessExpectedDirectWork": canonical_decimal(with_values[node_id]),
                    "deltaWorkHours": canonical_decimal(delta),
                }
            )
    return result


def _prior_credit_correction(
    *,
    triggering_step: Mapping[str, object],
    corrected_step: Mapping[str, object],
) -> dict[str, object]:
    correction: dict[str, object] = {
        "schemaVersion": 1,
        "correctionId": "foundation-shared-scope",
        "triggeringSubjectTransactionId": triggering_step["subjectTransactionId"],
        "correctedSubjectTransactionId": corrected_step["subjectTransactionId"],
        "priorEvaluationDigest": corrected_step["evaluation"]["evaluationDigest"],  # type: ignore[index]
        "causeKnowledgeStateDigest": triggering_step["knowledgeAfter"]["stateDigest"],  # type: ignore[index]
        "causeTopologyAlignmentDigest": triggering_step["topologyAlignment"]["alignmentDigest"],  # type: ignore[index]
        "changeKind": "allocation-only",
        "changesLiveWorkEstimate": False,
        "beforeAllocation": [
            {"programId": ROUTE_A, "share": "1"},
            {"programId": ROUTE_B, "share": "0"},
        ],
        "afterAllocation": [
            {"programId": ROUTE_A, "share": "0.6"},
            {"programId": ROUTE_B, "share": "0.4"},
        ],
        "rationale": (
            "The later topology correction reveals that the foundation is shared; "
            "the earlier work evaluation stays immutable while its presentation is reallocated."
        ),
    }
    correction["correctionDigest"] = "sha256:" + sha256_json(correction)
    return correction


def _frozen_with_access_candidate(
    *,
    subject: str,
    base_accounting_state: Mapping[str, object],
    with_access_patch: Mapping[str, object],
    with_access_state: Mapping[str, object],
) -> dict[str, object]:
    candidate: dict[str, object] = {
        "schemaVersion": 1,
        "profile": WORK_ACCOUNTING_PROFILE,
        "subjectTransactionId": subject,
        "baseAccountingStateDigest": base_accounting_state["stateDigest"],
        "withAccessPatchDigest": with_access_patch["patchDigest"],
        "withAccessStateDigest": with_access_state["stateDigest"],
        "providerFreeSubstitution": (
            "The synthetic oracle supplies the sparse W+ patch; trusted code "
            "materializes and freezes W+ before the W- patch is evaluated."
        ),
    }
    candidate["candidateDigest"] = "sha256:" + sha256_json(candidate)
    return candidate


def build_miniature_e2e_transcript() -> dict[str, object]:
    """Build the complete synthetic transcript through executable reducers."""

    root_contract = miniature_root_contract()
    knowledge = empty_research_program_state_v3(PROBLEM_ID)
    live_accounting = make_zero_work_accounting_state(
        root_contract=root_contract,
        knowledge_state=knowledge,
    )
    transcript: dict[str, object] = {
        "schemaVersion": 1,
        "problemId": PROBLEM_ID,
        "description": (
            "Eight synthetic accepted submissions exercise the first miniature "
            "knowledge-plus-work evaluation portfolio."
        ),
        "rootContract": root_contract,
        "initialKnowledgeState": knowledge,
        "initialAccountingState": live_accounting,
        "steps": [],
    }
    steps: list[dict[str, object]] = transcript["steps"]  # type: ignore[assignment]
    for ordinal, transition_builder in enumerate(_TRANSITION_BUILDERS, start=1):
        transition, accepted_claims = transition_builder(knowledge)
        subject = SUBJECTS[ordinal - 1]
        judgment_id = JUDGMENT_IDS[ordinal - 1]
        reduced = apply_research_builder_v7_transition(
            knowledge,
            transition,
            accepted_claims=accepted_claims,
            judgment_id=judgment_id,
        )
        target = reduced["postState"]
        alignment = reduced["topologyAlignment"]
        no_updates, with_updates = _work_plan(ordinal)
        # Preserve the V2 A-first boundary even though semantic estimates are
        # supplied by a synthetic oracle rather than a provider.  W+ is
        # materialized and content-bound before W- is constructed.
        with_patch = _patch(
            mode="with-access",
            subject=subject,
            root_contract=root_contract,
            base_accounting_state=live_accounting,
            base_knowledge_state=knowledge,
            target_knowledge_state=target,
            topology_alignment=alignment,
            updates=with_updates,
        )
        frozen_with_state = apply_work_accounting_patch(
            live_accounting,
            with_patch,
            root_contract=root_contract,
            base_knowledge_state=knowledge,
            target_knowledge_state=target,
            topology_alignment=alignment,
        )
        frozen_candidate = _frozen_with_access_candidate(
            subject=subject,
            base_accounting_state=live_accounting,
            with_access_patch=with_patch,
            with_access_state=frozen_with_state,
        )
        no_patch = _patch(
            mode="no-access",
            subject=subject,
            root_contract=root_contract,
            base_accounting_state=live_accounting,
            base_knowledge_state=knowledge,
            target_knowledge_state=target,
            topology_alignment=alignment,
            updates=no_updates,
        )
        no_state, with_state, evaluation = materialize_submission_work_value(
            base_state=live_accounting,
            no_access_patch=no_patch,
            with_access_patch=with_patch,
            root_contract=root_contract,
            base_knowledge_state=knowledge,
            target_knowledge_state=target,
            topology_alignment=alignment,
        )
        step: dict[str, object] = {
            "schemaVersion": 1,
            "ordinal": ordinal,
            "subjectTransactionId": subject,
            "caseTags": list(_CASE_TAGS[ordinal - 1]),
            "acceptedClaims": accepted_claims,
            "judgmentId": judgment_id,
            "builderTransition": transition,
            "knowledgeAfter": target,
            "topologyAlignment": alignment,
            "sameWorldHandoff": reduced["sameWorldHandoff"],
            "baseLiveAccountingStateDigest": live_accounting["stateDigest"],
            "withAccessPatch": with_patch,
            "frozenWithAccessCandidate": frozen_candidate,
            "noAccessPatch": no_patch,
            "noAccessState": no_state,
            "withAccessState": with_state,
            "evaluation": evaluation,
            "nodeReductions": _node_reductions(no_state, with_state),
            "priorCreditCorrections": [],
        }
        steps.append(step)
        if ordinal == 6:
            step["priorCreditCorrections"] = [
                _prior_credit_correction(
                    triggering_step=step,
                    corrected_step=steps[2],
                )
            ]
        knowledge = target
        live_accounting = with_state
    transcript["finalKnowledgeStateDigest"] = knowledge["stateDigest"]
    transcript["finalLiveAccountingStateDigest"] = live_accounting["stateDigest"]
    transcript["transcriptDigest"] = "sha256:" + sha256_json(transcript)
    return transcript


def miniature_e2e_oracle() -> dict[str, object]:
    """Return the small precommitted relational/semantic oracle."""

    return {
        "schemaVersion": 1,
        "transcriptArtifactId": "history.replay.transcript",
        "candidateContract": {
            "knowledgeBuilderId": KNOWLEDGE_BUILDER_ID,
            "knowledgeBuilderSubstitution": (
                "Precommitted synthetic transitions substitute for V10 route, "
                "route-refine, and organize judge calls; the state-v3 reducer remains exact."
            ),
            "workAccountingId": WORK_ACCOUNTING_ID,
            "workAccountingProfile": WORK_ACCOUNTING_PROFILE,
            "estimationOrder": "with-access-then-no-access",
            "workJudgeSubstitution": (
                "Precommitted sparse primitive patches substitute for the V2 "
                "with-access and no-access judges; trusted A-first freezing and reduction remain exact."
            ),
        },
        "orderedSubjectTransactionIds": list(SUBJECTS),
        "requiredCaseTags": sorted(REQUIRED_CASE_TAGS),
        "expectedWorkValueHours": ["20", "5", "10", "15", "2", "2", "12", "59"],
        "independentRouteProgramIds": [ROUTE_A, ROUTE_B],
        "dependencySubjectTransactionId": SUBJECTS[2],
        "negativeSubjectTransactionId": SUBJECTS[3],
        "duplicateSubjectTransactionId": SUBJECTS[4],
        "topologyCorrectionSubjectTransactionId": SUBJECTS[5],
        "crossProgramSubjectTransactionId": SUBJECTS[6],
        "decisiveSubjectTransactionId": SUBJECTS[7],
        "correctedSubjectTransactionId": SUBJECTS[2],
    }


def _correction_digest(value: Mapping[str, object]) -> str:
    content = {key: copy.deepcopy(item) for key, item in value.items() if key != "correctionDigest"}
    return "sha256:" + sha256_json(content)


def _normalized_allocation_total(
    value: object,
    *,
    valid_program_ids: frozenset[str],
) -> Fraction | None:
    """Return one only for a well-formed, exactly normalized allocation."""

    if not isinstance(value, list) or not value:
        return None
    seen_program_ids: set[str] = set()
    total = Fraction(0)
    for raw_item in value:
        if not isinstance(raw_item, dict):
            return None
        program_id = raw_item.get("programId")
        if (
            not isinstance(program_id, str)
            or program_id not in valid_program_ids
            or program_id in seen_program_ids
        ):
            return None
        raw_share = raw_item.get("share")
        if isinstance(raw_share, bool) or not isinstance(
            raw_share, (str, int, float)
        ):
            return None
        try:
            share = Fraction(str(raw_share))
        except (TypeError, ValueError, ZeroDivisionError, OverflowError):
            return None
        if share < 0 or share > 1:
            return None
        seen_program_ids.add(program_id)
        total += share
    return total if total == 1 else None


def score_miniature_e2e_scenario(
    transcript: object,
    oracle: object,
    *,
    scorer_id: str = "miniature-e2e",
) -> dict[str, object]:
    """Replay and score knowledge topology plus hierarchical work accounting."""

    assertions: list[dict[str, object]] = []

    def check(
        assertion_id: str,
        passed: bool,
        message: str,
        *,
        actual: object | None = None,
        expected: object | None = None,
    ) -> None:
        assertions.append(
            {
                "id": assertion_id,
                "severity": "hard",
                "passed": bool(passed),
                "actual": actual,
                "expected": expected,
                "message": message,
            }
        )

    if not isinstance(transcript, dict) or not isinstance(oracle, dict):
        raise MathFlowError("miniature E2E transcript and oracle must be objects")
    if transcript.get("schemaVersion") != 1 or oracle.get("schemaVersion") != 1:
        raise MathFlowError("miniature E2E transcript or oracle version is unsupported")
    root_contract = validate_root_contract(transcript.get("rootContract"), PROBLEM_ID)
    knowledge = validate_research_program_state_v3(
        transcript.get("initialKnowledgeState"), PROBLEM_ID
    )
    live = validate_work_accounting_state(
        transcript.get("initialAccountingState"), knowledge, root_contract
    )
    expected_origin = make_zero_work_accounting_state(
        root_contract=root_contract, knowledge_state=knowledge
    )
    check(
        "zero-origin",
        live == expected_origin,
        "The scenario starts from the deterministic zero-work origin.",
    )
    candidate_contract = oracle.get("candidateContract")
    check(
        "candidate-contract",
        isinstance(candidate_contract, dict)
        and candidate_contract.get("knowledgeBuilderId") == KNOWLEDGE_BUILDER_ID
        and candidate_contract.get("workAccountingId") == WORK_ACCOUNTING_ID
        and candidate_contract.get("workAccountingProfile") == WORK_ACCOUNTING_PROFILE
        and candidate_contract.get("estimationOrder") == "with-access-then-no-access"
        and "Precommitted" in str(candidate_contract.get("knowledgeBuilderSubstitution"))
        and "Precommitted" in str(candidate_contract.get("workJudgeSubstitution")),
        "The fixture explicitly binds the V10/V2 candidate and records its provider-free judge substitutions.",
    )
    raw_steps = transcript.get("steps")
    if not isinstance(raw_steps, list):
        raise MathFlowError("miniature E2E transcript steps must be an array")
    check(
        "miniature-size",
        3 <= len(raw_steps) <= 8,
        "The benchmark remains a three-to-eight submission miniature.",
        actual=len(raw_steps),
        expected="3..8",
    )
    expected_subjects = oracle.get("orderedSubjectTransactionIds")
    observed_subjects = [
        step.get("subjectTransactionId") if isinstance(step, dict) else None
        for step in raw_steps
    ]
    check(
        "ordered-subjects",
        observed_subjects == expected_subjects,
        "Accepted submissions are processed once in the precommitted order.",
        actual=observed_subjects,
        expected=expected_subjects,
    )

    evaluations: dict[str, dict[str, object]] = {}
    step_by_subject: dict[str, dict[str, object]] = {}
    all_tags: set[str] = set()
    all_corrections: list[tuple[dict[str, object], frozenset[str]]] = []
    for ordinal, raw_step in enumerate(raw_steps, start=1):
        if not isinstance(raw_step, dict):
            raise MathFlowError("miniature E2E step must be an object")
        subject = str(raw_step.get("subjectTransactionId"))
        step_by_subject[subject] = raw_step
        tags = raw_step.get("caseTags")
        if isinstance(tags, list):
            all_tags.update(str(tag) for tag in tags)
        check(
            f"ordinal-{ordinal}",
            raw_step.get("ordinal") == ordinal,
            "Step ordinals are contiguous and canonical.",
        )
        reduced = apply_research_builder_v7_transition(
            knowledge,
            raw_step.get("builderTransition"),
            accepted_claims=raw_step.get("acceptedClaims"),
            judgment_id=str(raw_step.get("judgmentId")),
        )
        target = reduced["postState"]
        alignment = reduced["topologyAlignment"]
        check(
            f"knowledge-replay-{ordinal}",
            target == raw_step.get("knowledgeAfter"),
            "The knowledge post-state is the exact reducer output.",
        )
        check(
            f"topology-replay-{ordinal}",
            alignment == raw_step.get("topologyAlignment")
            and reduced["sameWorldHandoff"] == raw_step.get("sameWorldHandoff"),
            "Topology alignment and same-world handoff replay exactly.",
        )
        check(
            f"live-base-{ordinal}",
            raw_step.get("baseLiveAccountingStateDigest") == live.get("stateDigest"),
            "Only the prior W+ state is used as the next live accounting base.",
        )
        frozen_with_state = apply_work_accounting_patch(
            live,
            raw_step.get("withAccessPatch"),
            root_contract=root_contract,
            base_knowledge_state=knowledge,
            target_knowledge_state=target,
            topology_alignment=alignment,
        )
        expected_candidate = _frozen_with_access_candidate(
            subject=subject,
            base_accounting_state=live,
            with_access_patch=raw_step.get("withAccessPatch"),
            with_access_state=frozen_with_state,
        )
        check(
            f"a-first-freeze-{ordinal}",
            raw_step.get("frozenWithAccessCandidate") == expected_candidate,
            "W+ is materialized and content-bound before W- evaluation.",
        )
        no_state, with_state, evaluation = materialize_submission_work_value(
            base_state=live,
            no_access_patch=raw_step.get("noAccessPatch"),
            with_access_patch=raw_step.get("withAccessPatch"),
            root_contract=root_contract,
            base_knowledge_state=knowledge,
            target_knowledge_state=target,
            topology_alignment=alignment,
        )
        check(
            f"work-replay-{ordinal}",
            no_state == raw_step.get("noAccessState")
            and with_state == raw_step.get("withAccessState")
            and with_state == frozen_with_state
            and evaluation == raw_step.get("evaluation"),
            "W-, W+, and D are exact deterministic reducer outputs.",
        )
        validate_submission_work_value(evaluation)
        check(
            f"positive-delta-{ordinal}",
            Fraction(str(evaluation["workValueHours"])) > 0,
            "Every accepted submission has strictly positive D.",
            actual=evaluation["workValueHours"],
            expected="> 0",
        )
        check(
            f"counterfactual-not-live-{ordinal}",
            subject not in no_state["processedSubmissionIds"]
            and with_state["processedSubmissionIds"][-1] == subject,
            "W- stays audit-only while W+ appends the current subject.",
        )
        reductions = _node_reductions(no_state, with_state)
        reduction_total = sum(
            (Fraction(str(item["deltaWorkHours"])) for item in reductions),
            Fraction(0),
        )
        check(
            f"node-reduction-replay-{ordinal}",
            reductions == raw_step.get("nodeReductions"),
            "Node-level reductions are derived from expected direct work.",
        )
        check(
            f"node-reduction-sum-{ordinal}",
            reduction_total == Fraction(str(evaluation["workValueHours"])),
            "Node-level reductions sum exactly to displayed submission D.",
            actual=canonical_decimal(reduction_total),
            expected=evaluation["workValueHours"],
        )
        corrections = raw_step.get("priorCreditCorrections")
        if not isinstance(corrections, list):
            raise MathFlowError("miniature prior-credit corrections must be an array")
        target_programs = target.get("programs")
        valid_program_ids = (
            frozenset(str(program_id) for program_id in target_programs)
            if isinstance(target_programs, dict)
            else frozenset()
        )
        all_corrections.extend(
            (item, valid_program_ids)
            for item in corrections
            if isinstance(item, dict)
        )
        evaluations[subject] = evaluation
        knowledge = target
        live = with_state

    required_tags = set(str(item) for item in oracle.get("requiredCaseTags", []))
    check(
        "case-coverage",
        required_tags == all_tags == REQUIRED_CASE_TAGS,
        "The miniature jointly covers every roadmap case class.",
        actual=sorted(all_tags),
        expected=sorted(REQUIRED_CASE_TAGS),
    )
    observed_values = [
        evaluations[str(subject)]["workValueHours"]
        for subject in expected_subjects
        if str(subject) in evaluations
    ] if isinstance(expected_subjects, list) else []
    check(
        "precommitted-work-values",
        observed_values == oracle.get("expectedWorkValueHours"),
        "The exact synthetic hour scale is precommitted rather than inferred by the scorer.",
        actual=observed_values,
        expected=oracle.get("expectedWorkValueHours"),
    )
    route_ids = oracle.get("independentRouteProgramIds")
    programs = knowledge["programs"]
    check(
        "independent-routes",
        isinstance(route_ids, list)
        and all(
            isinstance(programs.get(program_id), dict)
            and programs[program_id]["parentId"] == "root"
            for program_id in route_ids
        ),
        "Routes A and B remain incomparable sibling programs.",
    )

    dependency_subject = str(oracle.get("dependencySubjectTransactionId"))
    dependency_step = step_by_subject.get(dependency_subject, {})
    dependency_state = dependency_step.get("knowledgeAfter", {})
    dependency_result = (
        dependency_state.get("intermediateResults", {}).get(RESULT_FOUNDATION, {})
        if isinstance(dependency_state, dict)
        else {}
    )
    dependency_contribution = (
        dependency_state.get("contributions", {}).get(dependency_subject, {})
        if isinstance(dependency_state, dict)
        else {}
    )
    check(
        "dependency-chain",
        dependency_contribution.get("dependencyTransactionIds") == [SUBJECTS[0]]
        and dependency_result.get("dependencyResultIds") == [RESULT_A],
        "The dependent submission binds both transaction and result dependencies.",
    )
    check(
        "dependency-not-double-counted",
        [item["nodeRef"]["id"] for item in dependency_step.get("nodeReductions", [])]
        == [FOUNDATION],
        "The dependency's avoided work is counted at its canonical package, not again at its ancestor.",
    )

    negative_step = step_by_subject[str(oracle.get("negativeSubjectTransactionId"))]
    no_dead = next(
        item
        for item in negative_step["noAccessState"]["annotations"]
        if item["nodeRef"]["id"] == DEAD_END
    )
    with_dead = next(
        item
        for item in negative_step["withAccessState"]["annotations"]
        if item["nodeRef"]["id"] == DEAD_END
    )
    check(
        "negative-pruning",
        no_dead["directWorkHours"] == "15"
        and no_dead["conditionalIncidence"] == "1"
        and with_dead["directWorkHours"] == "0"
        and with_dead["conditionalIncidence"] == "0",
        "A completed negative branch retains same-world W- but is zeroed in live W+.",
    )

    duplicate_step = step_by_subject[str(oracle.get("duplicateSubjectTransactionId"))]
    duplicate_result = duplicate_step["knowledgeAfter"]["intermediateResults"][RESULT_A]
    check(
        "duplicate-reuses-result",
        {ref["transactionId"] for ref in duplicate_result["claimRefs"]}
        == {SUBJECTS[0], SUBJECTS[4]}
        and duplicate_step["builderTransition"]["contribution"]["intermediateResultIds"]
        == [RESULT_A],
        "Independent reproduction enriches the existing result instead of duplicating it.",
    )
    check(
        "duplicate-discounted",
        Fraction(str(duplicate_step["evaluation"]["workValueHours"]))
        < Fraction(str(step_by_subject[SUBJECTS[0]]["evaluation"]["workValueHours"])),
        "The reproduction receives less work value than the original result.",
    )

    topology_step = step_by_subject[
        str(oracle.get("topologyCorrectionSubjectTransactionId"))
    ]
    moved = topology_step["topologyAlignment"]["moved"]
    check(
        "topology-correction",
        any(
            item.get("entityKind") == "program"
            and item.get("entityId") == FOUNDATION
            and item.get("fromProgramIds") == [ROUTE_A]
            and item.get("toProgramIds") == ["root"]
            for item in moved
        ),
        "The later generality result moves the stable foundation to shared root scope.",
    )
    check(
        "topology-no-invented-work",
        topology_step["noAccessState"]["totalWorkHours"]
        == step_by_subject[SUBJECTS[4]]["withAccessState"]["totalWorkHours"],
        "Re-anchoring the revealed package creates no same-world W- work by itself.",
    )

    cross_step = step_by_subject[str(oracle.get("crossProgramSubjectTransactionId"))]
    cross_result = cross_step["knowledgeAfter"]["intermediateResults"][RESULT_CROSS]
    check(
        "cross-program",
        cross_step["builderTransition"]["contribution"]["directProgramIds"]
        == [ROUTE_A, ROUTE_B]
        and cross_result["primaryProgramId"] == ROUTE_A
        and cross_result["relatedProgramIds"] == [ROUTE_B]
        and {item["nodeRef"]["id"] for item in cross_step["nodeReductions"]}
        == {ROUTE_A, ROUTE_B},
        "One canonical result spans and reduces two incomparable programs.",
    )

    decisive_step = step_by_subject[str(oracle.get("decisiveSubjectTransactionId"))]
    check(
        "decisive-completion",
        decisive_step["withAccessState"]["totalWorkHours"] == "0"
        and Fraction(str(decisive_step["noAccessState"]["totalWorkHours"])) > 0,
        "The decisive contribution zeros live work while same-world W- remains positive.",
    )

    corrected_subject = str(oracle.get("correctedSubjectTransactionId"))
    check(
        "prior-correction-count",
        len(all_corrections) == 1,
        "Exactly one explicit prior-credit correction is recorded separately.",
        actual=len(all_corrections),
        expected=1,
    )
    if all_corrections:
        correction, valid_program_ids = all_corrections[0]
        before_total = _normalized_allocation_total(
            correction.get("beforeAllocation"),
            valid_program_ids=valid_program_ids,
        )
        after_total = _normalized_allocation_total(
            correction.get("afterAllocation"),
            valid_program_ids=valid_program_ids,
        )
        check(
            "prior-correction-separate",
            correction.get("triggeringSubjectTransactionId") == SUBJECTS[5]
            and correction.get("correctedSubjectTransactionId") == corrected_subject
            and correction.get("priorEvaluationDigest")
            == evaluations[corrected_subject]["evaluationDigest"]
            and correction.get("changesLiveWorkEstimate") is False
            and correction.get("changeKind") == "allocation-only"
            and "workValueHours" not in correction,
            "The correction points to immutable prior D and never enters current-submission work value.",
        )
        check(
            "prior-correction-balanced",
            before_total == after_total == Fraction(1)
            and correction.get("beforeAllocation") != correction.get("afterAllocation")
            and correction.get("correctionDigest") == _correction_digest(correction),
            (
                "Prior allocations cite distinct existing programs, use finite shares "
                "in [0, 1], normalize exactly, change, and remain digest-bound."
            ),
        )

    check(
        "final-knowledge-binding",
        transcript.get("finalKnowledgeStateDigest") == knowledge.get("stateDigest"),
        "The transcript binds the exact terminal knowledge state.",
    )
    check(
        "final-live-binding",
        transcript.get("finalLiveAccountingStateDigest") == live.get("stateDigest"),
        "The transcript binds the exact terminal live W+ state.",
    )
    expected_transcript_digest = "sha256:" + sha256_json(
        {key: value for key, value in transcript.items() if key != "transcriptDigest"}
    )
    check(
        "transcript-digest",
        transcript.get("transcriptDigest") == expected_transcript_digest,
        "The complete provider-free transcript is content-bound.",
    )

    hard_failures = [
        str(item["id"])
        for item in assertions
        if not item["passed"] and item["severity"] == "hard"
    ]
    assertion_status = {
        str(item["id"]): bool(item["passed"]) for item in assertions
    }
    adversarial_groups = [
        (
            "duplicate-credit",
            ["duplicate-reuses-result", "duplicate-discounted"],
        ),
        ("dependency-double-count", ["dependency-not-double-counted"]),
        (
            "nonpositive-d",
            [f"positive-delta-{ordinal}" for ordinal in range(1, len(raw_steps) + 1)],
        ),
        (
            "live-w-plus-chaining",
            [
                *[f"live-base-{ordinal}" for ordinal in range(1, len(raw_steps) + 1)],
                *[
                    f"counterfactual-not-live-{ordinal}"
                    for ordinal in range(1, len(raw_steps) + 1)
                ],
                *[
                    f"a-first-freeze-{ordinal}"
                    for ordinal in range(1, len(raw_steps) + 1)
                ],
            ],
        ),
        ("solving-zero-out", ["decisive-completion"]),
        ("cross-program-contribution", ["cross-program"]),
        (
            "topology-revelation",
            ["topology-correction", "topology-no-invented-work"],
        ),
        (
            "prior-credit-correction-separation",
            [
                "prior-correction-count",
                "prior-correction-separate",
                "prior-correction-balanced",
            ],
        ),
    ]
    adversarial_checks = [
        {
            "id": group_id,
            "assertionIds": assertion_ids,
            "passed": all(assertion_status.get(assertion_id, False) for assertion_id in assertion_ids),
        }
        for group_id, assertion_ids in adversarial_groups
    ]
    adversarial_audit = {
        "schemaVersion": 1,
        "status": (
            "passed"
            if all(item["passed"] for item in adversarial_checks)
            else "failed"
        ),
        "checks": adversarial_checks,
    }
    return {
        "schemaVersion": 1,
        "scorerId": scorer_id,
        "implementation": "miniature-e2e-v1",
        "status": "passed" if not hard_failures else "failed",
        "assertions": assertions,
        "passed": sum(int(bool(item["passed"])) for item in assertions),
        "failed": sum(int(not bool(item["passed"])) for item in assertions),
        "hardFailures": hard_failures,
        "advisoryFailures": [],
        "adversarialAudit": adversarial_audit,
    }
