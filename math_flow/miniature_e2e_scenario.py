"""Provider-free miniature end-to-end protocol evaluation fixture.

This module never dispatches an external provider or publication adapter.  It
builds one synthetic, precommitted eight-submission history through the real
local knowledge-builder and Work Accounting V2 request/bundle paths.  A local
capture transport returns the precommitted semantic responses while preserving
the governed adapter, epistemic firewall, and deterministic reducers exactly.
"""

from __future__ import annotations

import base64
import copy
import json
import tempfile
from fractions import Fraction
from pathlib import Path
from typing import Mapping

from .artifacts import sha256_bytes
from .counterfactual_context import (
    accepted_claim_refs_from_validity,
    build_submission_evidence_manifest,
)
from .errors import MathFlowError
from .governed_providers import OpenRouterWorkProjectionProviderV2
from .judges import load_judge_spec
from .repository import sha256_json
from .research_builder_v7 import (
    empty_research_program_state_v3,
    validate_research_program_state_v3,
)
from .research_builder_v10 import (
    apply_research_builder_v10_transition,
    build_research_builder_v10_authoring_packet,
    build_research_builder_v10_route_context,
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
from .work_projection import (
    PROFILE_V2,
    load_work_projection_bundle,
    run_work_projection_bundle,
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
WORK_ACCOUNTING_PROFILE = PROFILE_V2
WORK_ACCOUNTING_SPEC_PATH = (
    Path(__file__).resolve().parents[1]
    / "protocol/judges/openrouter-work-accounting-v2.json"
)
WORK_ACCOUNTING_STAGE_ORDER = ("safe-facts", "with-access", "no-access")
WORK_ACCOUNTING_DESCENDANT_DEPTH = 1


def _evidence_files(subject: str) -> dict[str, bytes]:
    path = f"problems/{PROBLEM_ID}/contributions/{subject}/README.md"
    content = (
        "# Synthetic accepted submission\n\n"
        f"Provider-free evidence for transaction `{subject}`.\n"
    ).encode("utf-8")
    return {path: content}


def _evidence_file_refs(subject: str) -> dict[str, str]:
    return {
        path: sha256_bytes(content)
        for path, content in _evidence_files(subject).items()
    }


def _evidence_artifact_ref(subject: str) -> dict[str, str]:
    (path, digest), = _evidence_file_refs(subject).items()
    return {"path": path, "digest": digest}


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
    bound_support = copy.deepcopy(support)
    artifact_refs = bound_support.get("artifactRefs")
    if not isinstance(artifact_refs, list):
        raise MathFlowError("miniature result support has invalid artifact refs")
    artifact_refs.append(_evidence_artifact_ref(subject))
    bound_support["artifactRefs"] = sorted(
        artifact_refs,
        key=lambda item: (str(item["path"]), str(item["digest"])),
    )
    return {
        "id": result_id,
        "primaryProgramId": primary_program_id,
        "relatedProgramIds": sorted(related_program_ids or []),
        "title": title,
        "statement": statement,
        "scopeQualifications": sorted(qualifications or []),
        "support": bound_support,
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
        "artifactRefs": sorted(
            [
                *result["support"]["artifactRefs"],
                _evidence_artifact_ref(subject),
            ],
            key=lambda item: (str(item["path"]), str(item["digest"])),
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


def _linked_program_ids(result: object) -> set[str]:
    if not isinstance(result, dict):
        return set()
    linked: set[str] = set()
    primary = result.get("primaryProgramId")
    if isinstance(primary, str):
        linked.add(primary)
    related = result.get("relatedProgramIds")
    if isinstance(related, list):
        linked.update(str(item) for item in related if isinstance(item, str))
    return linked


def _complete_v8_program_refreshes(
    base: Mapping[str, object], transition: Mapping[str, object]
) -> dict[str, object]:
    """Complete the deterministic affected-ancestor refresh required by V8."""

    completed = copy.deepcopy(dict(transition))
    subject = completed.get("subjectTransactionId")
    base_programs = base.get("programs")
    base_results = base.get("intermediateResults")
    if (
        not isinstance(subject, str)
        or not isinstance(base_programs, dict)
        or not isinstance(base_results, dict)
    ):
        raise MathFlowError("miniature V8 refresh input is invalid")

    raw_content = completed.get("contentOperations")
    raw_topology = completed.get("topologyOperations")
    if not isinstance(raw_content, list) or not isinstance(raw_topology, list):
        raise MathFlowError("miniature transition operations are invalid")

    operations = [*raw_content, *raw_topology]
    planned_programs = {
        str(program_id): program
        for program_id, program in base_programs.items()
        if isinstance(program, dict)
    }
    planned_results = {
        str(result_id): result
        for result_id, result in base_results.items()
        if isinstance(result, dict)
    }
    operated_program_ids: set[str] = set()
    topology_only_program_ids: set[str] = set()
    for operation in operations:
        if not isinstance(operation, dict):
            raise MathFlowError("miniature transition operation is invalid")
        kind = operation.get("entityKind")
        entity_id = operation.get("entityId")
        value = operation.get("value")
        if not isinstance(entity_id, str) or not isinstance(value, dict):
            raise MathFlowError("miniature transition operation value is invalid")
        if kind == "program":
            planned_programs[entity_id] = value
            operated_program_ids.add(entity_id)
            if operation in raw_topology and entity_id in base_programs:
                topology_only_program_ids.add(entity_id)
        elif kind == "intermediateResult":
            planned_results[entity_id] = value

    impacted: set[str] = set()
    contribution = completed.get("contribution")
    if not isinstance(contribution, dict):
        raise MathFlowError("miniature transition contribution is invalid")
    direct_program_ids = contribution.get("directProgramIds")
    contribution_result_ids = contribution.get("intermediateResultIds")
    if not isinstance(direct_program_ids, list) or not isinstance(
        contribution_result_ids, list
    ):
        raise MathFlowError("miniature transition contribution is incomplete")
    impacted.update(str(item) for item in direct_program_ids if isinstance(item, str))
    for result_id in contribution_result_ids:
        if isinstance(result_id, str):
            impacted.update(_linked_program_ids(base_results.get(result_id)))
            impacted.update(_linked_program_ids(planned_results.get(result_id)))
    for operation in operations:
        assert isinstance(operation, dict)
        entity_id = str(operation["entityId"])
        if operation.get("entityKind") == "program":
            impacted.add(entity_id)
            prior = base_programs.get(entity_id)
            after = planned_programs.get(entity_id)
            for program in (prior, after):
                parent = program.get("parentId") if isinstance(program, dict) else None
                if isinstance(parent, str):
                    impacted.add(parent)
        else:
            impacted.update(_linked_program_ids(base_results.get(entity_id)))
            impacted.update(_linked_program_ids(planned_results.get(entity_id)))

    def add_existing_ancestors(
        program_id: str, programs: Mapping[str, object], target: set[str]
    ) -> None:
        seen: set[str] = set()
        cursor: str | None = program_id
        while cursor is not None:
            if cursor in seen:
                raise MathFlowError("miniature planned program ancestry has a cycle")
            seen.add(cursor)
            if cursor in base_programs:
                target.add(cursor)
            program = programs.get(cursor)
            parent = program.get("parentId") if isinstance(program, dict) else None
            cursor = str(parent) if isinstance(parent, str) else None

    refresh_required: set[str] = set()
    for program_id in impacted:
        add_existing_ancestors(program_id, base_programs, refresh_required)
        add_existing_ancestors(program_id, planned_programs, refresh_required)

    for operation in raw_content:
        if not isinstance(operation, dict) or operation.get("entityKind") != "program":
            continue
        entity_id = operation.get("entityId")
        value = operation.get("value")
        if entity_id not in base_programs or not isinstance(value, dict):
            continue
        sources = value.get("sourceTransactionIds")
        if not isinstance(sources, list) or any(
            not isinstance(item, str) for item in sources
        ):
            raise MathFlowError("miniature program source provenance is invalid")
        value["sourceTransactionIds"] = sorted({*sources, subject})

    for program_id in sorted(refresh_required - operated_program_ids):
        prior = base_programs.get(program_id)
        if not isinstance(prior, dict):
            raise MathFlowError("miniature affected program is absent")
        refreshed = _without_digest(prior)
        sources = refreshed.get("sourceTransactionIds")
        if not isinstance(sources, list):
            raise MathFlowError("miniature affected program provenance is invalid")
        refreshed["sourceTransactionIds"] = sorted({*sources, subject})
        raw_content.append(
            _content_operation(base, "program", program_id, refreshed)
        )

    if topology_only_program_ids & {
        str(operation.get("entityId"))
        for operation in raw_content
        if isinstance(operation, dict)
        and operation.get("entityKind") == "program"
    }:
        raise MathFlowError("miniature topology-only program was also content-refreshed")
    return completed


def _raw_v10_route_plan(
    base: Mapping[str, object],
    transition: Mapping[str, object],
    route_context: Mapping[str, object],
) -> dict[str, object]:
    existing_program_ids: set[str] = set()
    existing_result_ids: set[str] = set()
    create_program_ids: set[str] = set()
    create_result_ids: set[str] = set()
    base_programs = base.get("programs")
    base_results = base.get("intermediateResults")
    if not isinstance(base_programs, dict) or not isinstance(base_results, dict):
        raise MathFlowError("miniature route base state is invalid")
    for field in ("contentOperations", "topologyOperations"):
        operations = transition.get(field)
        if not isinstance(operations, list):
            raise MathFlowError("miniature route transition operations are invalid")
        for operation in operations:
            if not isinstance(operation, dict):
                raise MathFlowError("miniature route transition operation is invalid")
            entity_id = operation.get("entityId")
            if not isinstance(entity_id, str):
                raise MathFlowError("miniature route entity ID is invalid")
            if operation.get("entityKind") == "program":
                (existing_program_ids if entity_id in base_programs else create_program_ids).add(
                    entity_id
                )
            elif operation.get("entityKind") == "intermediateResult":
                (existing_result_ids if entity_id in base_results else create_result_ids).add(
                    entity_id
                )
            else:
                raise MathFlowError("miniature route entity kind is invalid")
    return {
        "schemaVersion": 1,
        "baseStateDigest": base["stateDigest"],
        "routeContextDigest": route_context["contextDigest"],
        "inspectProgramIds": [],
        "inspectResultIds": [],
        "searchQueries": [],
        "writeProgramIds": sorted(existing_program_ids),
        "writeResultIds": sorted(existing_result_ids),
        "createProgramIds": sorted(create_program_ids),
        "createResultIds": sorted(create_result_ids),
    }


def _knowledge_builder_replay_record(
    *,
    route_context: Mapping[str, object],
    authoring_packet: Mapping[str, object],
    transition: Mapping[str, object],
    evidence_file_refs: Mapping[str, str],
) -> dict[str, object]:
    return {
        "schemaVersion": 1,
        "providerCallsExecuted": 0,
        "evidenceFileRefs": copy.deepcopy(dict(evidence_file_refs)),
        "routeContextDigest": route_context["contextDigest"],
        "routePlan": copy.deepcopy(authoring_packet["routePlan"]),
        "authoringPacketDigest": authoring_packet["authoringPacketDigest"],
        "readSet": copy.deepcopy(authoring_packet["readSet"]),
        "writeScope": copy.deepcopy(authoring_packet["writeScope"]),
        "expandedTransitionDigest": "sha256:" + sha256_json(transition),
    }


def _build_v10_knowledge_artifacts(
    base: Mapping[str, object],
    accepted_claims: object,
    transition: Mapping[str, object],
    *,
    route_plan: object | None = None,
) -> tuple[dict[str, object], dict[str, object], dict[str, object]]:
    route_context = build_research_builder_v10_route_context(
        base, accepted_claims
    )
    raw_plan = (
        _raw_v10_route_plan(base, transition, route_context)
        if route_plan is None
        else route_plan
    )
    authoring_packet = build_research_builder_v10_authoring_packet(
        base,
        accepted_claims,
        raw_plan,
        route_context=route_context,
    )
    evidence_file_refs = _evidence_file_refs(
        str(transition["subjectTransactionId"])
    )
    replay = _knowledge_builder_replay_record(
        route_context=route_context,
        authoring_packet=authoring_packet,
        transition=transition,
        evidence_file_refs=evidence_file_refs,
    )
    return route_context, authoring_packet, replay


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


# These scopes are an independent semantic part of the miniature oracle.  In
# particular, they are not inferred from the sparse work patches below.  That
# lets the fixture exercise the real safe-fact/context coverage boundary
# without making successful routing tautological in the implementation.
_SAFE_FACT_PLANS = (
    (
        "structural-route-available",
        "A structural line of attack is available in the reference world.",
        (ROUTE_A,),
    ),
    (
        "computational-route-available",
        "A computational line of attack is available in the reference world.",
        (ROUTE_B,),
    ),
    (
        "technical-dependency-available",
        "A reusable technical dependency is available in the reference world.",
        (FOUNDATION,),
    ),
    (
        "search-branch-impossible",
        "One previously live search branch cannot succeed in the reference world.",
        (DEAD_END,),
    ),
    (
        "independent-support-available",
        "Independent support exists for a previously represented conclusion.",
        (ROUTE_A,),
    ),
    (
        "shared-technical-scope",
        "A technical dependency applies at shared scope in the reference world.",
        (FOUNDATION,),
    ),
    (
        "cross-route-bridge-available",
        "A bridge can reduce residual work in two active lines of attack.",
        (ROUTE_A, ROUTE_B),
    ),
    (
        "terminal-resolution-available",
        "A terminal resolution is available in the reference world.",
        ("root",),
    ),
)


def _safe_fact_response(
    ordinal: int, accepted_claims: object
) -> dict[str, object]:
    if (
        not isinstance(accepted_claims, list)
        or not accepted_claims
        or any(not isinstance(claim, dict) for claim in accepted_claims)
    ):
        raise MathFlowError("miniature safe-fact plan requires accepted claims")
    fact_id, condition, program_ids = _SAFE_FACT_PLANS[ordinal - 1]
    claim_keys = sorted(str(claim["claimKey"]) for claim in accepted_claims)
    return {
        "facts": [
            {
                "id": fact_id,
                "condition": condition,
                "actorVisibility": "withheld-until-independent-discovery",
                "affectedNodeRefs": [
                    {"kind": "program", "id": program_id}
                    for program_id in sorted(program_ids)
                ],
                "acceptedClaimKeys": claim_keys,
            }
        ],
        "assumptions": [
            "The fixed root contract governs both same-world accounting branches."
        ],
    }


def _synthetic_validity_judgment(
    *,
    subject: str,
    judgment_id: str,
    accepted_claims: object,
) -> dict[str, object]:
    if not isinstance(accepted_claims, list) or not accepted_claims:
        raise MathFlowError("miniature validity preimage requires accepted claims")
    assessments: list[dict[str, object]] = []
    for claim in accepted_claims:
        if not isinstance(claim, dict):
            raise MathFlowError("miniature accepted claim is invalid")
        dependencies = claim.get("dependencyTransactionIds")
        if not isinstance(dependencies, list):
            raise MathFlowError("miniature accepted claim dependencies are invalid")
        assessments.append(
            {
                "claimKey": claim["claimKey"],
                "status": "valid",
                "premiseStatus": "satisfied" if dependencies else "not-required",
                "summary": f"Synthetic accepted assessment for {claim['claimKey']}.",
                "scopeQualifications": [],
                "evidenceIssues": [],
                "evidenceTransactionIds": sorted({subject, *dependencies}),
                "requiredDependencyTransactionIds": sorted(dependencies),
            }
        )
    return {
        "schemaVersion": 4,
        "judgmentId": judgment_id,
        "subjects": [{"kind": "transaction", "id": subject}],
        "assessments": sorted(
            assessments, key=lambda assessment: str(assessment["claimKey"])
        ),
    }


def _transport_user_data(payload: object) -> dict[str, object]:
    if not isinstance(payload, dict):
        raise MathFlowError("fixture-local transport payload is not an object")
    messages = payload.get("messages")
    if not isinstance(messages, list):
        raise MathFlowError("fixture-local transport payload has no messages")
    user_messages = [
        message
        for message in messages
        if isinstance(message, dict) and message.get("role") == "user"
    ]
    if not user_messages or not isinstance(user_messages[-1].get("content"), str):
        raise MathFlowError("fixture-local transport payload has no user input")
    content = str(user_messages[-1]["content"])
    prefix = "<math-flow-input>\n"
    suffix = "\n</math-flow-input>"
    start = content.find(prefix)
    end = content.rfind(suffix)
    if start < 0 or end <= start:
        raise MathFlowError("fixture-local transport input framing is invalid")
    try:
        value = json.loads(content[start + len(prefix) : end])
    except json.JSONDecodeError as exc:
        raise MathFlowError("fixture-local transport input is not JSON") from exc
    if not isinstance(value, dict):
        raise MathFlowError("fixture-local transport user data is not an object")
    return value


class _StageAwareLocalCaptureTransport:
    """Return precommitted responses without network or provider dispatch."""

    def __init__(
        self,
        *,
        subject: str,
        responses: Mapping[str, Mapping[str, object]],
    ) -> None:
        self.subject = subject
        self.responses = {
            stage: copy.deepcopy(dict(response))
            for stage, response in responses.items()
        }
        self.expected_stages = list(WORK_ACCOUNTING_STAGE_ORDER)
        self.payloads: list[tuple[str, dict[str, object]]] = []

    def __call__(self, payload: dict[str, object]) -> dict[str, object]:
        user_data = _transport_user_data(payload)
        request = user_data.get("request")
        stage = request.get("stage") if isinstance(request, dict) else None
        expected = self.expected_stages.pop(0) if self.expected_stages else None
        if stage != expected or stage not in self.responses:
            raise MathFlowError(
                "fixture-local transport observed an unexpected V2 stage"
            )
        self.payloads.append((str(stage), copy.deepcopy(payload)))
        return {
            "id": f"provider-free-{self.subject}-{stage}",
            "model": "provider-free/local-capture-v1",
            "choices": [
                {
                    "finish_reason": "stop",
                    "message": {
                        "content": json.dumps(
                            self.responses[str(stage)],
                            sort_keys=True,
                            separators=(",", ":"),
                            ensure_ascii=False,
                        )
                    },
                }
            ],
        }

    def captured_records(self) -> list[dict[str, object]]:
        if self.expected_stages:
            raise MathFlowError("fixture-local transport did not capture every V2 stage")
        records = []
        for stage, payload in self.payloads:
            records.append(
                {
                    "schemaVersion": 1,
                    "kind": "fixture-local-openrouter-request-capture",
                    "stage": stage,
                    "networkDispatched": False,
                    "payloadDigest": "sha256:" + sha256_json(payload),
                    "payload": copy.deepcopy(payload),
                }
            )
        return records


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


def _contains_exact_key(value: object, prohibited: set[str]) -> bool:
    if isinstance(value, dict):
        return bool(prohibited & set(value)) or any(
            _contains_exact_key(item, prohibited) for item in value.values()
        )
    if isinstance(value, list):
        return any(_contains_exact_key(item, prohibited) for item in value)
    return False


def _capture_audit(
    *,
    records: list[dict[str, object]],
    evidence_files: Mapping[str, bytes],
    candidate: Mapping[str, object],
    no_access_input: Mapping[str, object],
    no_access_request: Mapping[str, object],
) -> dict[str, object]:
    stages = [record.get("stage") for record in records]
    if stages != list(WORK_ACCOUNTING_STAGE_ORDER):
        raise MathFlowError("fixture-local V2 captures have the wrong stage order")
    expected_files = [
        {
            "path": path,
            "digest": sha256_bytes(content),
            "bytes": len(content),
            "contentBase64": base64.b64encode(content).decode("ascii"),
        }
        for path, content in sorted(evidence_files.items())
    ]
    user_data = [
        _transport_user_data(record.get("payload")) for record in records
    ]
    for index in (0, 1):
        evidence = user_data[index].get("submissionEvidence")
        if not isinstance(evidence, dict) or evidence.get("files") != expected_files:
            raise MathFlowError(
                "fixture-local evidence-bearing capture is not exact"
            )
    no_access_data = user_data[2]
    if "submissionEvidence" in no_access_data:
        raise MathFlowError("fixture-local W- capture contains submission evidence")
    captured_no_request = no_access_data.get("request")
    if captured_no_request != no_access_request:
        raise MathFlowError("fixture-local W- capture changed its governed request")
    if no_access_request.get("stageInput") != no_access_input:
        raise MathFlowError("fixture-local W- request changed its stage input")
    if (
        no_access_input.get("frozenWithAccessCandidateDigest")
        != candidate.get("candidateDigest")
        or no_access_input.get("frozenWithAccessState")
        != candidate.get("withAccessState")
    ):
        raise MathFlowError("fixture-local W- capture is not bound to frozen W+")
    prohibited = {
        "evidenceManifest",
        "verifiedChunkDigests",
        "verifiedFileCount",
        "verifiedTotalBytes",
        "submissionEvidence",
        "contentBase64",
    }
    if _contains_exact_key(no_access_data, prohibited):
        raise MathFlowError("fixture-local W- capture crosses the evidence firewall")
    rendered_no_access = json.dumps(
        no_access_data, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    )
    if any(
        base64.b64encode(content).decode("ascii") in rendered_no_access
        for content in evidence_files.values()
    ):
        raise MathFlowError("fixture-local W- capture leaks raw evidence bytes")
    return {
        "schemaVersion": 1,
        "stageOrder": list(WORK_ACCOUNTING_STAGE_ORDER),
        "evidenceBearingStages": ["safe-facts", "with-access"],
        "evidenceFreeStages": ["no-access"],
        "frozenWithAccessCandidateDigest": candidate["candidateDigest"],
        "frozenWithAccessStateDigest": candidate["withAccessState"]["stateDigest"],  # type: ignore[index]
        "noAccessInputDigest": no_access_input["inputDigest"],
        "noAccessRequestDigest": no_access_request["requestDigest"],
    }


def _read_json(path: Path) -> dict[str, object]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise MathFlowError(f"miniature V2 replay artifact is unreadable: {path}") from exc
    if not isinstance(value, dict):
        raise MathFlowError("miniature V2 replay artifact is not an object")
    return value


def _build_work_accounting_replay(
    *,
    ordinal: int,
    subject: str,
    judgment_id: str,
    accepted_claims: object,
    root_contract: Mapping[str, object],
    base_accounting_state: Mapping[str, object],
    base_knowledge_state: Mapping[str, object],
    target_knowledge_state: Mapping[str, object],
    topology_alignment: Mapping[str, object],
    judge_spec: Mapping[str, object],
) -> dict[str, object]:
    no_updates, with_updates = _work_plan(ordinal)
    evidence_files = _evidence_files(subject)
    contribution_path = f"problems/{PROBLEM_ID}/contributions/{subject}"
    evidence_manifest, evidence_chunks = build_submission_evidence_manifest(
        problem_id=PROBLEM_ID,
        subject_transaction_id=subject,
        contribution_path=contribution_path,
        files=evidence_files,
        chunk_bytes=64,
    )
    validity_judgment = _synthetic_validity_judgment(
        subject=subject,
        judgment_id=judgment_id,
        accepted_claims=accepted_claims,
    )
    accepted_claim_refs = accepted_claim_refs_from_validity(
        validity_judgment,
        subject_transaction_id=subject,
    )

    expected_with_patch = _patch(
        mode="with-access",
        subject=subject,
        root_contract=root_contract,
        base_accounting_state=base_accounting_state,
        base_knowledge_state=base_knowledge_state,
        target_knowledge_state=target_knowledge_state,
        topology_alignment=topology_alignment,
        updates=with_updates,
    )
    expected_no_patch = _patch(
        mode="no-access",
        subject=subject,
        root_contract=root_contract,
        base_accounting_state=base_accounting_state,
        base_knowledge_state=base_knowledge_state,
        target_knowledge_state=target_knowledge_state,
        topology_alignment=topology_alignment,
        updates=no_updates,
    )
    expected_no_state, expected_with_state, expected_evaluation = (
        materialize_submission_work_value(
            base_state=base_accounting_state,
            no_access_patch=expected_no_patch,
            with_access_patch=expected_with_patch,
            root_contract=root_contract,
            base_knowledge_state=base_knowledge_state,
            target_knowledge_state=target_knowledge_state,
            topology_alignment=topology_alignment,
        )
    )

    transport = _StageAwareLocalCaptureTransport(
        subject=subject,
        responses={
            "safe-facts": _safe_fact_response(ordinal, accepted_claims),
            "with-access": {"updates": with_updates},
            "no-access": {"updates": no_updates},
        },
    )
    provider = OpenRouterWorkProjectionProviderV2(
        judge_spec,
        transport=transport,
    )
    with tempfile.TemporaryDirectory(prefix="math-flow-miniature-v2-") as temporary:
        bundle_dir = Path(temporary) / "bundle"
        manifest = run_work_projection_bundle(
            output_dir=bundle_dir,
            provider=provider,
            subject_transaction_id=subject,
            root_contract=root_contract,
            base_knowledge_state=base_knowledge_state,
            target_knowledge_state=target_knowledge_state,
            base_accounting_state=base_accounting_state,
            topology_alignment=topology_alignment,
            evidence_manifest=evidence_manifest,
            evidence_chunks=evidence_chunks,
            accepted_claim_refs=accepted_claim_refs,
            descendant_depth=WORK_ACCOUNTING_DESCENDANT_DEPTH,
            output_profile=PROFILE_V2,
        )
        loaded = load_work_projection_bundle(bundle_dir)
        no_access_input = _read_json(bundle_dir / "stages/no-access/input.json")
        no_access_request = _read_json(bundle_dir / "stages/no-access/request.json")
        no_access_response = _read_json(bundle_dir / "stages/no-access/response.json")

    observed_invocations = [
        (record.get("stage"), record.get("attempts"))
        for record in provider.invocation_records
    ]
    if observed_invocations != [
        (stage, 1) for stage in WORK_ACCOUNTING_STAGE_ORDER
    ]:
        raise MathFlowError(
            "fixture-local V2 adapter did not accept one response per stage"
        )
    if (
        manifest != loaded["manifest"]
        or loaded["withAccessPatch"] != expected_with_patch
        or loaded["noAccessPatch"] != expected_no_patch
        or loaded["withAccessState"] != expected_with_state
        or loaded["noAccessState"] != expected_no_state
        or loaded["evaluation"] != expected_evaluation
    ):
        raise MathFlowError(
            "actual V2 bundle diverges from the precommitted work oracle"
        )
    candidate = loaded["frozenWithAccessCandidate"]
    if not isinstance(candidate, dict):
        raise MathFlowError("actual V2 bundle has no frozen W+ candidate")
    captured_records = transport.captured_records()
    capture_audit = _capture_audit(
        records=captured_records,
        evidence_files=evidence_files,
        candidate=candidate,
        no_access_input=no_access_input,
        no_access_request=no_access_request,
    )
    replay_core: dict[str, object] = {
        "schemaVersion": 1,
        "profile": PROFILE_V2,
        "providerSubstitution": (
            "Precommitted structured responses are returned by an explicitly "
            "fixture-local capture transport; no external provider is contacted."
        ),
        "judgeSpec": {
            "id": judge_spec["id"],
            # This binds the parsed canonical object.  The candidate contract
            # separately binds the raw judge-spec file bytes.
            "canonicalDigest": "sha256:" + sha256_json(judge_spec),
        },
        "descendantDepth": WORK_ACCOUNTING_DESCENDANT_DEPTH,
        "acceptedValidityJudgmentPreimage": validity_judgment,
        "acceptedClaimRefs": accepted_claim_refs,
        "evidenceManifest": evidence_manifest,
        "bundleManifest": manifest,
        "bundleDigest": loaded["bundleDigest"],
        "frozenWithAccessCandidateDigest": candidate["candidateDigest"],
        "noAccessStageInput": no_access_input,
        "noAccessRequest": no_access_request,
        "noAccessResponse": no_access_response,
        "capturedPayloads": captured_records,
        "captureAudit": capture_audit,
        "execution": {
            "localCaptureTransportInvocations": len(captured_records),
            "externalProviderCalls": 0,
            "networkUsed": False,
            "publicationAttempted": False,
        },
        "precommittedBindings": {
            "noAccessPatchDigest": expected_no_patch["patchDigest"],
            "withAccessPatchDigest": expected_with_patch["patchDigest"],
            "noAccessStateDigest": expected_no_state["stateDigest"],
            "withAccessStateDigest": expected_with_state["stateDigest"],
            "evaluationDigest": expected_evaluation["evaluationDigest"],
        },
    }
    replay = {
        **replay_core,
        "replayDigest": "sha256:" + sha256_json(replay_core),
    }
    return {
        "workAccountingReplay": replay,
        "withAccessPatch": loaded["withAccessPatch"],
        "frozenWithAccessCandidate": candidate,
        "noAccessPatch": loaded["noAccessPatch"],
        "noAccessState": loaded["noAccessState"],
        "withAccessState": loaded["withAccessState"],
        "evaluation": loaded["evaluation"],
    }


def build_miniature_e2e_transcript() -> dict[str, object]:
    """Build the complete synthetic transcript through executable reducers."""

    root_contract = miniature_root_contract()
    work_accounting_spec = load_judge_spec(WORK_ACCOUNTING_SPEC_PATH)
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
        raw_transition, accepted_claims = transition_builder(knowledge)
        transition = _complete_v8_program_refreshes(knowledge, raw_transition)
        subject = SUBJECTS[ordinal - 1]
        judgment_id = JUDGMENT_IDS[ordinal - 1]
        _, authoring_packet, builder_replay = _build_v10_knowledge_artifacts(
            knowledge,
            accepted_claims,
            transition,
        )
        reduced = apply_research_builder_v10_transition(
            knowledge,
            transition,
            authoring_packet=authoring_packet,
            accepted_claims=accepted_claims,
            judgment_id=judgment_id,
            evidence_file_refs=_evidence_file_refs(subject),
        )
        target = reduced["postState"]
        alignment = reduced["topologyAlignment"]
        accounting = _build_work_accounting_replay(
            ordinal=ordinal,
            subject=subject,
            judgment_id=judgment_id,
            accepted_claims=accepted_claims,
            root_contract=root_contract,
            base_accounting_state=live_accounting,
            base_knowledge_state=knowledge,
            target_knowledge_state=target,
            topology_alignment=alignment,
            judge_spec=work_accounting_spec,
        )
        with_patch = accounting["withAccessPatch"]
        frozen_candidate = accounting["frozenWithAccessCandidate"]
        no_patch = accounting["noAccessPatch"]
        no_state = accounting["noAccessState"]
        with_state = accounting["withAccessState"]
        evaluation = accounting["evaluation"]
        step: dict[str, object] = {
            "schemaVersion": 1,
            "ordinal": ordinal,
            "subjectTransactionId": subject,
            "caseTags": list(_CASE_TAGS[ordinal - 1]),
            "acceptedClaims": accepted_claims,
            "judgmentId": judgment_id,
            "knowledgeBuilderReplay": builder_replay,
            "builderTransition": transition,
            "knowledgeAfter": target,
            "topologyAlignment": alignment,
            "sameWorldHandoff": reduced["sameWorldHandoff"],
            "baseLiveAccountingStateDigest": live_accounting["stateDigest"],
            "workAccountingReplay": accounting["workAccountingReplay"],
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
                "Precommitted synthetic route and author choices substitute for "
                "V10 provider calls; trusted route binding, local authoring-packet "
                "construction, scoped application, and V8/V7 reduction remain exact."
            ),
            "workAccountingId": WORK_ACCOUNTING_ID,
            "workAccountingProfile": WORK_ACCOUNTING_PROFILE,
            "estimationOrder": "with-access-then-no-access",
            "workRequestConstruction": "actual-v2-adapter-bundle-replay",
            "localCaptureTransportInvocations": 24,
            "externalProviderCalls": 0,
            "workJudgeSubstitution": (
                "Precommitted safe-fact and sparse primitive responses are returned "
                "by an explicitly fixture-local transport; the actual V2 governed "
                "request, A-first freeze, firewall, bundle, loader, and reducers remain exact."
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
    work_accounting_spec = load_judge_spec(WORK_ACCOUNTING_SPEC_PATH)
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
        and candidate_contract.get("workRequestConstruction")
        == "actual-v2-adapter-bundle-replay"
        and candidate_contract.get("localCaptureTransportInvocations") == 24
        and candidate_contract.get("externalProviderCalls") == 0
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
    local_capture_invocations = 0
    external_provider_calls = 0
    network_or_publication_attempted = False
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
        transition = raw_step.get("builderTransition")
        builder_replay = raw_step.get("knowledgeBuilderReplay")
        if not isinstance(transition, dict) or not isinstance(builder_replay, dict):
            raise MathFlowError("miniature E2E V10 replay inputs are invalid")
        _, authoring_packet, expected_builder_replay = (
            _build_v10_knowledge_artifacts(
                knowledge,
                raw_step.get("acceptedClaims"),
                transition,
                route_plan=builder_replay.get("routePlan"),
            )
        )
        _, canonical_authoring_packet, _ = _build_v10_knowledge_artifacts(
            knowledge,
            raw_step.get("acceptedClaims"),
            transition,
        )
        exact_builder_binding = (
            builder_replay == expected_builder_replay
            and authoring_packet["routePlan"]
            == canonical_authoring_packet["routePlan"]
        )
        reduced = apply_research_builder_v10_transition(
            knowledge,
            transition,
            authoring_packet=authoring_packet,
            accepted_claims=raw_step.get("acceptedClaims"),
            judgment_id=str(raw_step.get("judgmentId")),
            evidence_file_refs=_evidence_file_refs(subject),
        )
        target = reduced["postState"]
        alignment = reduced["topologyAlignment"]
        check(
            f"knowledge-replay-{ordinal}",
            exact_builder_binding and target == raw_step.get("knowledgeAfter"),
            "The bound V10 route/packet and scoped knowledge post-state replay exactly.",
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
        expected_accounting = _build_work_accounting_replay(
            ordinal=ordinal,
            subject=subject,
            judgment_id=str(raw_step.get("judgmentId")),
            accepted_claims=raw_step.get("acceptedClaims"),
            root_contract=root_contract,
            base_accounting_state=live,
            base_knowledge_state=knowledge,
            target_knowledge_state=target,
            topology_alignment=alignment,
            judge_spec=work_accounting_spec,
        )
        raw_replay = raw_step.get("workAccountingReplay")
        exact_v2_replay = (
            raw_replay == expected_accounting["workAccountingReplay"]
            and raw_step.get("withAccessPatch")
            == expected_accounting["withAccessPatch"]
            and raw_step.get("frozenWithAccessCandidate")
            == expected_accounting["frozenWithAccessCandidate"]
            and raw_step.get("noAccessPatch") == expected_accounting["noAccessPatch"]
            and raw_step.get("noAccessState") == expected_accounting["noAccessState"]
            and raw_step.get("withAccessState")
            == expected_accounting["withAccessState"]
            and raw_step.get("evaluation") == expected_accounting["evaluation"]
        )
        check(
            f"work-v2-bundle-replay-{ordinal}",
            exact_v2_replay,
            (
                "The actual V2 adapter, requests, frozen W+ candidate, bundle, "
                "and loaded semantic outputs replay exactly."
            ),
        )
        execution = raw_replay.get("execution") if isinstance(raw_replay, dict) else None
        captured = (
            raw_replay.get("capturedPayloads")
            if isinstance(raw_replay, dict)
            else None
        )
        provider_free_capture = (
            isinstance(execution, dict)
            and execution
            == {
                "localCaptureTransportInvocations": 3,
                "externalProviderCalls": 0,
                "networkUsed": False,
                "publicationAttempted": False,
            }
            and isinstance(captured, list)
            and [
                item.get("stage") if isinstance(item, dict) else None
                for item in captured
            ]
            == list(WORK_ACCOUNTING_STAGE_ORDER)
            and all(
                isinstance(item, dict)
                and item.get("kind")
                == "fixture-local-openrouter-request-capture"
                and item.get("networkDispatched") is False
                for item in captured
            )
        )
        check(
            f"provider-free-v2-capture-{ordinal}",
            provider_free_capture,
            (
                "Each V2 stage is captured once by the explicitly local transport "
                "with no external call, network use, or publication."
            ),
        )
        if isinstance(execution, dict):
            local = execution.get("localCaptureTransportInvocations")
            external = execution.get("externalProviderCalls")
            if isinstance(local, int) and not isinstance(local, bool):
                local_capture_invocations += local
            if isinstance(external, int) and not isinstance(external, bool):
                external_provider_calls += external
            network_or_publication_attempted = network_or_publication_attempted or bool(
                execution.get("networkUsed")
                or execution.get("publicationAttempted")
            )
        frozen_with_state = apply_work_accounting_patch(
            live,
            raw_step.get("withAccessPatch"),
            root_contract=root_contract,
            base_knowledge_state=knowledge,
            target_knowledge_state=target,
            topology_alignment=alignment,
        )
        expected_candidate = expected_accounting["frozenWithAccessCandidate"]
        check(
            f"a-first-freeze-{ordinal}",
            raw_step.get("frozenWithAccessCandidate") == expected_candidate
            and isinstance(expected_candidate, dict)
            and expected_candidate.get("withAccessState") == frozen_with_state,
            "The complete W+ candidate is materialized and frozen before W- evaluation.",
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

    check(
        "provider-free-v2-execution",
        local_capture_invocations == len(raw_steps) * len(WORK_ACCOUNTING_STAGE_ORDER)
        and external_provider_calls == 0
        and not network_or_publication_attempted,
        "The eight-step V2 replay uses 24 local captures and no external effects.",
        actual={
            "localCaptureTransportInvocations": local_capture_invocations,
            "externalProviderCalls": external_provider_calls,
            "networkOrPublicationAttempted": network_or_publication_attempted,
        },
        expected={
            "localCaptureTransportInvocations": len(raw_steps)
            * len(WORK_ACCOUNTING_STAGE_ORDER),
            "externalProviderCalls": 0,
            "networkOrPublicationAttempted": False,
        },
    )

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
